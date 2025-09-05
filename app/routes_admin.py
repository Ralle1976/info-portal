from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, session as flask_session, make_response
from functools import wraps
from flask_httpauth import HTTPBasicAuth
import os
import json
import logging
import zipfile
import tempfile
from datetime import datetime, date, timedelta
from collections import defaultdict
import time
from app.services import StatusService, ScheduleService, I18nService
from app.services.i18n import format_date, format_time, format_datetime, format_weekday, format_month_year, format_time_range
from app.services.social_media import SocialMediaService
from app.services.i18n import I18nService, t
from app.services.translation_validator import TranslationValidator
from app.services.analytics import analytics_service
from app.services.geocoding import geocoding_service
from app.models import StatusType, HourException, Announcement, Settings, Availability, SocialMediaConfig, SocialMediaPost, ChangeLog, AdminUser
from app.database import engine
from sqlmodel import Session, select
import yaml
from typing import Dict, Any, List
from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.utils import secure_filename
import secrets
import hashlib

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
auth = HTTPBasicAuth()

# Admin i18n context processor
def get_admin_i18n_context():
    """Get i18n context for admin templates"""
    # Handle admin language separately from public if needed
    admin_lang = request.args.get('lang')
    if admin_lang and admin_lang in I18nService.SUPPORTED_LANGUAGES:
        I18nService.set_language(admin_lang)
        flask_session['language'] = admin_lang  # Force set session language
    
    # For admin, default to German if no language set
    current_language = I18nService.get_current_language()
    if not flask_session.get('language') and not request.args.get('lang'):
        current_language = 'de'  # Admin default German
        I18nService.set_language('de')
        flask_session['language'] = 'de'
    
    # Create admin-specific translate function with explicit language
    def admin_translate(key, **kwargs):
        return I18nService.translate(key, language=flask_session.get('language', 'de'), **kwargs)
    
    return {
        'current_language': current_language,
        't': admin_translate,  # Use admin-specific translate function
        'i18n': I18nService
    }

def render_admin_template(template_name, **context):
    """Render admin template with i18n context"""
    i18n_context = get_admin_i18n_context()
    context.update(i18n_context)
    return render_template(template_name, **context)

# Setup Wizard State Management
wizard_sessions = {}  # In production, use Redis or database

# Configure logging
logger = logging.getLogger(__name__)

# RATE LIMITING FOR SECURITY
rate_limit_store = defaultdict(lambda: {'count': 0, 'last_reset': time.time()})
RATE_LIMIT_WINDOW = 300  # 5 minutes
RATE_LIMIT_MAX_REQUESTS = 30  # Max 30 requests per window

def check_rate_limit(ip_address: str) -> bool:
    """Check if IP is within rate limit"""
    now = time.time()
    user_data = rate_limit_store[ip_address]
    
    # Reset counter if window has passed
    if now - user_data['last_reset'] > RATE_LIMIT_WINDOW:
        user_data['count'] = 0
        user_data['last_reset'] = now
    
    # Check if limit exceeded
    if user_data['count'] >= RATE_LIMIT_MAX_REQUESTS:
        return False
    
    # Increment counter
    user_data['count'] += 1
    return True

def rate_limit(f):
    """Decorator for rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr or 'unknown'
        
        if not check_rate_limit(ip):
            logger.warning(f"Rate limit exceeded for IP {ip} on {request.endpoint}")
            return jsonify({
                'success': False, 
                'error': 'Rate limit exceeded. Please try again later.'
            }), 429
        
        return f(*args, **kwargs)
    return decorated_function

# CSRF Protection
def generate_csrf_token():
    """Generate CSRF token for form protection"""
    if 'csrf_token' not in flask_session:
        flask_session['csrf_token'] = secrets.token_hex(16)
    return flask_session['csrf_token']

def validate_csrf_token(token: str) -> bool:
    """Validate CSRF token"""
    if not token:
        return False
    session_token = flask_session.get('csrf_token')
    if not session_token:
        return False
    return token == session_token

def require_csrf(f):
    """Decorator to require CSRF token for POST/PUT/DELETE requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Check for CSRF token in multiple locations
            token = None
            
            # 1. Form data
            if request.form:
                token = request.form.get('csrf_token')
            
            # 2. JSON body
            if not token and request.is_json and request.json:
                token = request.json.get('csrf_token')
            
            # 3. Custom header (X-CSRFToken)
            if not token:
                token = request.headers.get('X-CSRFToken')
            
            # 4. Standard header (X-CSRF-Token)
            if not token:
                token = request.headers.get('X-CSRF-Token')
            
            if not token or not validate_csrf_token(token):
                logger.error(f"CSRF validation failed for {request.endpoint} - IP: {request.remote_addr} - Token: {'Present' if token else 'Missing'} - Expected: {flask_session.get('csrf_token', 'None')}")
                if request.is_json:
                    return jsonify({'success': False, 'error': 'CSRF token validation failed', 'redirect': '/admin'}), 403
                flash('Security token validation failed. Please try again.', 'error')
                return redirect(url_for('admin.dashboard')), 403
        return f(*args, **kwargs)
    return decorated_function

# Input validation helpers
def validate_required_fields(data: dict, required_fields: list) -> list:
    """Validate required fields in input data"""
    missing = [field for field in required_fields if not data.get(field)]
    return missing

def sanitize_input(data: str, max_length: int = 500, allow_html: bool = False) -> str:
    """Sanitize input string with XSS protection"""
    import html
    import re
    
    if not data:
        return ''
    
    # Strip whitespace and limit length
    data = data.strip()[:max_length]
    
    if not allow_html:
        # Escape HTML to prevent XSS
        data = html.escape(data)
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'javascript:', r'data:', r'vbscript:', r'onload=', r'onerror=',
            r'onclick=', r'onmouseover=', r'<script.*?>', r'</script>',
            r'<iframe.*?>', r'</iframe>', r'<object.*?>', r'</object>',
            r'<embed.*?>', r'</embed>', r'<link.*?>', r'<style.*?>', r'</style>'
        ]
        
        for pattern in dangerous_patterns:
            data = re.sub(pattern, '', data, flags=re.IGNORECASE)
    
    return data

# Logging helpers
def log_admin_action(action: str, details: dict = None):
    """Log admin actions for audit trail"""
    username = auth.current_user() if auth.current_user() else 'anonymous'
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user': username,
        'action': action,
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'details': details or {}
    }
    logger.info(f"Admin action: {json.dumps(log_entry)}")

@auth.verify_password
def verify_password(username, password):
    """Verify admin credentials - supports both env vars and database"""
    try:
        # First check database for hashed password
        with Session(engine) as session:
            admin_user_db = session.exec(select(AdminUser).where(AdminUser.username == username)).first()
            
            if admin_user_db:
                # Check if account is locked
                if admin_user_db.is_locked():
                    logger.warning(f"Login attempt for locked account: {username}")
                    return False
                
                # Verify password
                is_valid = admin_user_db.verify_password(password)
                
                # Record login attempt
                admin_user_db.record_login_attempt(is_valid)
                session.add(admin_user_db)
                session.commit()
                
                if is_valid:
                    logger.info(f"Successful database login for user: {username}")
                
                return is_valid
    
    except Exception as e:
        logger.error(f"Database authentication error: {e}")
    
    # Fallback to environment variables (backward compatibility)
    admin_user = os.getenv('ADMIN_USERNAME', 'admin')
    admin_pass = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    is_valid = username == admin_user and password == admin_pass
    
    if is_valid:
        logger.info(f"Successful environment login for user: {username}")
        
        # Migrate to database on successful env login
        try:
            with Session(engine) as session:
                existing_user = session.exec(select(AdminUser).where(AdminUser.username == username)).first()
                if not existing_user:
                    # Create database user with current password
                    new_admin = AdminUser(username=username)
                    new_admin.set_password(password)
                    session.add(new_admin)
                    session.commit()
                    logger.info(f"Migrated admin user {username} to database")
        except Exception as e:
            logger.error(f"Error migrating admin user to database: {e}")
    
    return is_valid

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@auth.login_required
def dashboard():
    """Admin dashboard"""
    # Get current status
    status = StatusService.get_current_status()
    
    # Get today's hours
    today = datetime.now(ScheduleService.TIMEZONE).date()
    today_hours = ScheduleService.get_hours_for_date(today)
    
    # Get recent announcements
    with Session(engine) as session:
        announcements = session.query(Announcement).order_by(Announcement.created_at.desc()).limit(5).all()
    
    return render_admin_template('admin/dashboard.html',
                         csrf_token=generate_csrf_token(),
        status=status,
        today_hours=today_hours,
        announcements=announcements,
        today=today
    )

@admin_bp.route('/status', methods=['GET', 'POST'])
@auth.login_required
@rate_limit
@require_csrf
def manage_status():
    """Manage laboratory status with enhanced validation"""
    if request.method == 'POST':
        try:
            status_type = StatusType(request.form.get('status_type'))
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')
            description = request.form.get('description')
            next_return = request.form.get('next_return')
            
            # Convert dates
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None
            next_return = datetime.strptime(next_return, '%Y-%m-%d').date() if next_return else None
            
            # Update status with validation
            status, validation_errors = StatusService.update_status(
                status_type, date_from, date_to, description, next_return,
                admin_user=auth.current_user(),
                admin_ip=request.remote_addr,
                validate=True
            )
            
            if status:
                # Show warnings if any
                warnings = [e for e in validation_errors if e.severity == "warning"]
                for warning in warnings:
                    flash(f'Warnung: {warning.message}', 'warning')
                
                flash('Status erfolgreich aktualisiert!', 'success')
                log_admin_action('update_status', {
                    'type': status.type,
                    'date_from': status.date_from.isoformat() if status.date_from else None,
                    'date_to': status.date_to.isoformat() if status.date_to else None
                })
            else:
                # Show validation errors
                for error in validation_errors:
                    if error.severity == "error":
                        flash(f'Fehler: {error.message}', 'error')
                        if error.suggestions:
                            flash(f'Vorschlag: {", ".join(error.suggestions)}', 'info')
            
            return redirect(url_for('admin.manage_status'))
            
        except ValueError as e:
            flash(f'Ungültiges Datumsformat: {str(e)}', 'error')
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            flash('Fehler beim Aktualisieren des Status', 'error')
    
    current_status = StatusService.get_current_status()
    
    # Ensure CSRF token is generated and stored in session
    csrf_token = generate_csrf_token()
    
    # Get status history for context
    status_history = StatusService.get_status_history(limit=5)
    
    return render_admin_template('admin/status.html',
                         csrf_token=csrf_token, 
                         status=current_status, 
                         status_history=status_history,
                         today=date.today().isoformat())

@admin_bp.route('/hours', methods=['GET', 'POST'])
@auth.login_required
@require_csrf
def manage_hours():
    """Manage opening hours"""
    if request.method == 'POST':
        try:
            # Handle weekly hours update
            weekly_hours = {}
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                is_closed = request.form.get(f'{day}-closed') == 'on'
                if is_closed:
                    weekly_hours[day] = []
                else:
                    hours = []
                    # Get all time slots for this day
                    i = 1
                    while True:
                        start_key = f'{day}-start-{i}'
                        end_key = f'{day}-end-{i}'
                        start_time = request.form.get(start_key)
                        end_time = request.form.get(end_key)
                        
                        if not start_time or not end_time:
                            break
                            
                        hours.append(f"{start_time}-{end_time}")
                        i += 1
                    
                    weekly_hours[day] = hours
            
            # Update weekly hours using ScheduleService
            success = ScheduleService.update_weekly_hours(weekly_hours)
            
            if success:
                log_admin_action('update_weekly_hours', {'hours': weekly_hours})
                flash('Öffnungszeiten erfolgreich aktualisiert!', 'success')
            else:
                flash('Fehler beim Aktualisieren der Öffnungszeiten', 'error')
                
        except Exception as e:
            logger.error(f"Error updating hours: {e}")
            flash(f'Fehler beim Speichern der Öffnungszeiten: {str(e)}', 'error')
        
        return redirect(url_for('admin.manage_hours'))
    
    # GET request
    current_hours = ScheduleService.get_weekly_hours()
    return render_admin_template('admin/hours.html',
                         csrf_token=generate_csrf_token(), 
                         current_hours=current_hours)

@admin_bp.route('/availability', methods=['GET', 'POST'])
@auth.login_required
@require_csrf
def manage_availability():
    """Manage availability slots"""
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            
            if action == 'add':
                # Add new availability slot
                date_str = request.form.get('date')
                start_time_str = request.form.get('start_time')
                end_time_str = request.form.get('end_time')
                slot_type = request.form.get('slot_type', 'general')
                capacity = int(request.form.get('capacity', 1))
                notes = sanitize_input(request.form.get('notes', ''), 500)
                
                # Validation
                if not date_str or not start_time_str or not end_time_str:
                    flash('Datum, Start- und Endzeit sind erforderlich', 'error')
                    return redirect(url_for('admin.manage_availability'))
                
                slot_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
                
                with Session(engine) as session:
                    availability = Availability(
                        availability_date=slot_date,
                        start_time=start_time,
                        end_time=end_time,
                        slot_type=slot_type,
                        capacity=capacity,
                        note=notes
                    )
                    session.add(availability)
                    session.commit()
                
                log_admin_action('add_availability', {'date': date_str, 'time': f'{start_time_str}-{end_time_str}'})
                flash('Verfügbarkeit erfolgreich hinzugefügt!', 'success')
                
            elif action == 'delete':
                # Delete specific availability slot
                availability_id = int(request.form.get('availability_id'))
                
                with Session(engine) as session:
                    slot = session.get(Availability, availability_id)
                    if slot:
                        session.delete(slot)
                        session.commit()
                        
                        log_admin_action('delete_availability', {'id': availability_id})
                        flash('Verfügbarkeit erfolgreich gelöscht!', 'success')
                    else:
                        flash('Verfügbarkeit nicht gefunden', 'error')
                        
        except Exception as e:
            logger.error(f"Error managing availability: {e}")
            flash(f'Fehler beim Verwalten der Verfügbarkeit: {str(e)}', 'error')
        
        return redirect(url_for('admin.manage_availability'))
    
    # GET request - load current availability
    with Session(engine) as session:
        # Get upcoming availability (next 4 weeks)
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=28)
        
        availability_slots = session.exec(
            select(Availability)
            .where(Availability.availability_date >= start_date)
            .where(Availability.availability_date <= end_date)
            .order_by(Availability.availability_date)
        ).all()
    
    return render_admin_template('admin/availability.html',
                         csrf_token=generate_csrf_token(), 
                         availability_slots=availability_slots)

@admin_bp.route('/announcements', methods=['GET', 'POST'])
@auth.login_required
@rate_limit
@require_csrf
def manage_announcements():
    """Manage announcements"""
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            
            if action == 'add':
                # Add new announcement
                title_de = sanitize_input(request.form.get('title_de', ''), 200)
                title_th = sanitize_input(request.form.get('title_th', ''), 200)
                title_en = sanitize_input(request.form.get('title_en', ''), 200)
                body_de = sanitize_input(request.form.get('body_de', ''), 1000)
                body_th = sanitize_input(request.form.get('body_th', ''), 1000)
                body_en = sanitize_input(request.form.get('body_en', ''), 1000)
                is_active = request.form.get('is_active') == 'on'
                
                # Validation
                if not title_de or not body_de:
                    flash('Titel und Text auf Deutsch sind erforderlich', 'error')
                    return redirect(url_for('admin.manage_announcements'))
                
                with Session(engine) as session:
                    announcement = Announcement(
                        title_de=title_de,
                        title_th=title_th,
                        title_en=title_en,
                        body_de=body_de,
                        body_th=body_th,
                        body_en=body_en,
                        is_active=is_active
                    )
                    session.add(announcement)
                    session.commit()
                
                log_admin_action('add_announcement', {'title': title_de})
                flash('Ankündigung erfolgreich hinzugefügt!', 'success')
                
            elif action == 'edit':
                # Edit existing announcement
                announcement_id = int(request.form.get('announcement_id'))
                title_de = sanitize_input(request.form.get('title_de', ''), 200)
                title_th = sanitize_input(request.form.get('title_th', ''), 200)
                title_en = sanitize_input(request.form.get('title_en', ''), 200)
                body_de = sanitize_input(request.form.get('body_de', ''), 1000)
                body_th = sanitize_input(request.form.get('body_th', ''), 1000)
                body_en = sanitize_input(request.form.get('body_en', ''), 1000)
                is_active = request.form.get('is_active') == 'on'
                
                with Session(engine) as session:
                    announcement = session.get(Announcement, announcement_id)
                    if announcement:
                        announcement.title_de = title_de
                        announcement.title_th = title_th
                        announcement.title_en = title_en
                        announcement.body_de = body_de
                        announcement.body_th = body_th
                        announcement.body_en = body_en
                        announcement.is_active = is_active
                        announcement.updated_at = datetime.now()
                        session.commit()
                        
                        log_admin_action('edit_announcement', {'id': announcement_id, 'title': title_de})
                        flash('Ankündigung erfolgreich aktualisiert!', 'success')
                    else:
                        flash('Ankündigung nicht gefunden', 'error')
                        
            elif action == 'delete':
                # Delete announcement
                announcement_id = int(request.form.get('announcement_id'))
                
                with Session(engine) as session:
                    announcement = session.get(Announcement, announcement_id)
                    if announcement:
                        session.delete(announcement)
                        session.commit()
                        
                        log_admin_action('delete_announcement', {'id': announcement_id})
                        flash('Ankündigung erfolgreich gelöscht!', 'success')
                    else:
                        flash('Ankündigung nicht gefunden', 'error')
                        
        except Exception as e:
            logger.error(f"Error managing announcements: {e}")
            flash(f'Fehler beim Verwalten der Ankündigungen: {str(e)}', 'error')
        
        return redirect(url_for('admin.manage_announcements'))
    
    # GET request
    with Session(engine) as session:
        announcements = session.exec(select(Announcement).order_by(Announcement.created_at.desc())).all()
    
    return render_admin_template('admin/announcements.html', 
                         announcements=announcements, 
                         csrf_token=generate_csrf_token())

@admin_bp.route('/settings', methods=['GET', 'POST'])
@auth.login_required
@rate_limit
@require_csrf
def manage_settings():
    """Manage general settings"""
    if request.method == 'POST':
        try:
            # Get form data
            site_name = sanitize_input(request.form.get('site_name', ''), 100)
            site_description = sanitize_input(request.form.get('site_description', ''), 500)
            contact_phone = sanitize_input(request.form.get('contact_phone', ''), 50)
            contact_email = sanitize_input(request.form.get('contact_email', ''), 100)
            contact_address = sanitize_input(request.form.get('contact_address', ''), 200)
            
            # Update or create settings
            with Session(engine) as session:
                # Try to get existing settings
                settings = session.exec(select(Settings).where(Settings.key == 'site_config')).first()
                
                config_data = {
                    'site_name': site_name,
                    'site_description': site_description,
                    'contact_phone': contact_phone,
                    'contact_email': contact_email,
                    'contact_address': contact_address
                }
                
                if settings:
                    # Update existing
                    settings.value = json.dumps(config_data)
                    settings.updated_at = datetime.now()
                else:
                    # Create new
                    settings = Settings(
                        key='site_config',
                        value=json.dumps(config_data),
                        description='General site configuration'
                    )
                    session.add(settings)
                
                session.commit()
                
            log_admin_action('update_settings', {'keys': list(config_data.keys())})
            flash('Einstellungen erfolgreich gespeichert!', 'success')
            
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            flash(f'Fehler beim Speichern der Einstellungen: {str(e)}', 'error')
        
        return redirect(url_for('admin.manage_settings'))
    
    # GET request - load current settings
    flask_session['csrf_token'] = generate_csrf_token()
    
    current_settings = {}
    try:
        with Session(engine) as session:
            settings = session.exec(select(Settings).where(Settings.key == 'site_config')).first()
            if settings and settings.value:
                if isinstance(settings.value, dict):
                    current_settings = settings.value
                else:
                    current_settings = json.loads(settings.value)
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
    
    return render_admin_template('admin/settings.html', 
                         csrf_token=generate_csrf_token(),
                         current_settings=current_settings)

@admin_bp.route('/rollback')
@auth.login_required
def manage_rollback():
    """Manage rollback operations"""
    # Temporarily disabled - ChangeLog import issue
    changes = []
    
    return render_admin_template('admin/rollback.html',
                         csrf_token=generate_csrf_token(), 
                         changes=changes)

@admin_bp.route('/api/rollback/<int:change_id>', methods=['POST'])
@auth.login_required
@require_csrf
def api_rollback_change(change_id: int):
    """Rollback a specific change"""
    try:
        success = StatusService.rollback_status(
            change_id,
            admin_user=auth.current_user(),
            admin_ip=request.remote_addr
        )
        
        if success:
            log_admin_action('rollback', {'change_id': change_id})
            return jsonify({'success': True, 'message': 'Änderung erfolgreich rückgängig gemacht'})
        else:
            return jsonify({
                'success': False, 
                'error': 'Änderung konnte nicht rückgängig gemacht werden'
            }), 400
            
    except Exception as e:
        logger.error(f"Error rolling back change {change_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/logout')
def logout():
    """Logout admin user"""
    flask_session.clear()
    response = make_response(redirect(url_for('public.home')))
    response.headers['WWW-Authenticate'] = 'Basic realm="Admin"'
    return response, 401

# API Endpoints
@admin_bp.route('/api/current-time')
@auth.login_required
def current_time():
    """API endpoint for current time in Bangkok timezone"""
    now = datetime.now(ScheduleService.TIMEZONE)
    return jsonify({
        'datetime': now.isoformat(),
        'time': now.strftime('%H:%M:%S'),
        'date': now.strftime('%Y-%m-%d'),
        'is_open': ScheduleService.is_open_now()
    })

@admin_bp.route('/api/validate-status', methods=['POST'])
@auth.login_required
def api_validate_status():
    """Real-time validation for status updates"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Parse input data
        status_type = StatusType(data.get('status_type', 'ANWESEND'))
        date_from = datetime.strptime(data['date_from'], '%Y-%m-%d').date() if data.get('date_from') else None
        date_to = datetime.strptime(data['date_to'], '%Y-%m-%d').date() if data.get('date_to') else None
        description = data.get('description')
        next_return = datetime.strptime(data['next_return'], '%Y-%m-%d').date() if data.get('next_return') else None
        current_id = data.get('current_id')  # For edit mode
        
        # Validate
        validation_errors = StatusService.validate_status_update(
            status_type, date_from, date_to, description, next_return, current_id
        )
        
        # Convert errors to JSON-serializable format
        errors_data = []
        for error in validation_errors:
            errors_data.append({
                'type': error.type,
                'field': error.field,
                'message': error.message,
                'severity': error.severity,
                'suggestions': error.suggestions or []
            })
        
        # Categorize results
        error_count = len([e for e in validation_errors if e.severity == 'error'])
        warning_count = len([e for e in validation_errors if e.severity == 'warning'])
        
        return jsonify({
            'success': True,
            'valid': error_count == 0,
            'errors': errors_data,
            'summary': {
                'total': len(validation_errors),
                'errors': error_count,
                'warnings': warning_count,
                'can_save': error_count == 0
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False, 
            'error': f'Invalid date format: {str(e)}',
            'valid': False
        }), 400
    except Exception as e:
        logger.error(f"Error validating status: {e}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'valid': False
        }), 500

@admin_bp.route('/api/suggest-dates', methods=['POST'])
@auth.login_required
def api_suggest_dates():
    """Suggest optimal dates for absence periods"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        status_type = StatusType(data.get('status_type', 'URLAUB'))
        start_date_str = data.get('preferred_start')
        duration_days = data.get('duration_days', 7)
        
        suggestions = []
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            
            # Get existing absences for conflict checking
            existing_absences = StatusService._get_existing_absences()
            
            # Generate suggestions around preferred start date
            for offset in [0, 1, -1, 2, -2, 7, -7]:
                suggested_start = start_date + timedelta(days=offset)
                suggested_end = suggested_start + timedelta(days=duration_days - 1)
                
                # Validate this suggestion
                validation_errors = StatusService.validate_status_update(
                    status_type, suggested_start, suggested_end
                )
                
                error_count = len([e for e in validation_errors if e.severity == 'error'])
                warning_count = len([e for e in validation_errors if e.severity == 'warning'])
                
                confidence = 100 - (error_count * 50) - (warning_count * 10)
                if confidence > 0:
                    suggestions.append({
                        'start_date': suggested_start.isoformat(),
                        'end_date': suggested_end.isoformat(),
                        'confidence': max(0, confidence),
                        'issues': [
                            {'message': e.message, 'severity': e.severity}
                            for e in validation_errors
                        ]
                    })
            
            # Sort by confidence
            suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions[:5]  # Top 5 suggestions
        })
        
    except Exception as e:
        logger.error(f"Error generating date suggestions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Hours Management API
@admin_bp.route('/api/weekly-hours', methods=['GET', 'POST'])
@auth.login_required
@require_csrf
def api_weekly_hours():
    """Get or update weekly opening hours"""
    if request.method == 'GET':
        try:
            hours = ScheduleService.get_weekly_hours()
            return jsonify({'success': True, 'hours': hours})
        except Exception as e:
            logger.error(f"Error loading weekly hours: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            if not data or 'hours' not in data:
                return jsonify({'success': False, 'error': 'Invalid data'}), 400
            
            # Validate hours format
            hours = data['hours']
            if not isinstance(hours, dict):
                return jsonify({'success': False, 'error': 'Hours must be an object'}), 400
            
            valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in hours:
                if day not in valid_days:
                    return jsonify({'success': False, 'error': f'Invalid day: {day}'}), 400
                
                if not isinstance(hours[day], list):
                    return jsonify({'success': False, 'error': f'Hours for {day} must be a list'}), 400
            
            ScheduleService.update_weekly_hours(hours)
            log_admin_action('update_weekly_hours', {'hours': hours})
            
            return jsonify({'success': True})
            
        except Exception as e:
            logger.error(f"Error updating weekly hours: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/hour-exceptions', methods=['GET', 'POST'])
@auth.login_required
@require_csrf
def api_hour_exceptions():
    """Get or create hour exceptions"""
    if request.method == 'GET':
        try:
            with Session(engine) as session:
                exceptions = session.exec(
                    select(HourException).order_by(HourException.exception_date)
                ).all()
                
                exception_list = []
                for exc in exceptions:
                    exception_list.append({
                        'id': exc.id,
                        'date': exc.exception_date.isoformat(),
                        'closed': exc.closed,
                        'hours': exc.time_ranges if exc.time_ranges else [],
                        'note': exc.note
                    })
                
                return jsonify({'success': True, 'exceptions': exception_list})
                
        except Exception as e:
            logger.error(f"Error loading hour exceptions: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            # Validate required fields
            missing = validate_required_fields(data, ['date'])
            if missing:
                return jsonify({'success': False, 'error': f'Missing fields: {missing}'}), 400
            
            # Parse date
            try:
                exception_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format'}), 400
            
            with Session(engine) as session:
                # Check if exception already exists for this date
                existing = session.exec(
                    select(HourException).where(HourException.exception_date == exception_date)
                ).first()
                
                if existing:
                    return jsonify({'success': False, 'error': 'Exception for this date already exists'}), 400
                
                # Create new exception
                exception = HourException(
                    exception_date=exception_date,
                    closed=data.get('closed', False),
                    time_ranges=data.get('hours', []),
                    note=sanitize_input(data.get('note', ''))
                )
                
                session.add(exception)
                session.commit()
                
                log_admin_action('create_hour_exception', {
                    'date': data['date'],
                    'closed': data.get('closed', False),
                    'note': data.get('note', '')
                })
                
                return jsonify({'success': True, 'id': exception.id})
                
        except Exception as e:
            logger.error(f"Error creating hour exception: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/hour-exceptions/<int:exception_id>', methods=['DELETE'])
@auth.login_required
@require_csrf
def api_delete_hour_exception(exception_id: int):
    """Delete hour exception"""
    try:
        with Session(engine) as session:
            exception = session.get(HourException, exception_id)
            if not exception:
                return jsonify({'success': False, 'error': 'Exception not found'}), 404
            
            date_str = exception.exception_date.isoformat()
            session.delete(exception)
            session.commit()
            
            log_admin_action('delete_hour_exception', {'date': date_str})
            return jsonify({'success': True})
            
    except Exception as e:
        logger.error(f"Error deleting hour exception: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/current-week-hours')
@auth.login_required
def api_current_week_hours():
    """Get current week hours with exceptions"""
    try:
        week_data = []
        today = datetime.now(ScheduleService.TIMEZONE).date()
        start_of_week = today - timedelta(days=today.weekday())
        
        for i in range(7):
            day_date = start_of_week + timedelta(days=i)
            day_hours = ScheduleService.get_hours_for_date(day_date)
            
            # Handle both dict and object responses safely
            if isinstance(day_hours, dict):
                is_closed = day_hours.get('closed', True)
                time_ranges = day_hours.get('time_ranges', [])
                note = day_hours.get('note')
            else:
                # Handle object response
                is_closed = getattr(day_hours, 'closed', True)
                time_ranges = getattr(day_hours, 'time_ranges', [])
                note = getattr(day_hours, 'note', None)
            
            week_data.append({
                'date': day_date.strftime('%d.%m'),
                'is_today': day_date == today,
                'closed': is_closed,
                'regular_hours': ', '.join(time_ranges) if not is_closed else 'Geschlossen',
                'exception': note is not None,
                'exception_hours': note or '',
                'note': note
            })
        
        return jsonify({'success': True, 'week': week_data})
        
    except Exception as e:
        logger.error(f"Error loading current week hours: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Announcements API
@admin_bp.route('/api/announcements', methods=['GET', 'POST'])
@auth.login_required
@require_csrf
def api_announcements():
    """Get or create announcements"""
    if request.method == 'GET':
        try:
            with Session(engine) as session:
                announcements = session.exec(
                    select(Announcement).order_by(Announcement.created_at.desc())
                ).all()
                
                announcement_list = []
                for ann in announcements:
                    announcement_list.append({
                        'id': ann.id,
                        'lang': ann.lang,
                        'title': ann.title,
                        'body': ann.body,
                        'priority': ann.priority or 'normal',
                        'category': ann.category or 'general',
                        'active': ann.active,
                        'start_date': ann.start_date.isoformat() if ann.start_date else None,
                        'end_date': ann.end_date.isoformat() if ann.end_date else None,
                        'created_at': ann.created_at.isoformat()
                    })
                
                return jsonify({'success': True, 'announcements': announcement_list})
                
        except Exception as e:
            logger.error(f"Error loading announcements: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            # Validate required fields
            missing = validate_required_fields(data, ['lang', 'title', 'body'])
            if missing:
                return jsonify({'success': False, 'error': f'Missing fields: {missing}'}), 400
            
            # Validate language
            if data['lang'] not in ['de', 'th', 'en']:
                return jsonify({'success': False, 'error': 'Invalid language'}), 400
            
            with Session(engine) as session:
                announcement = Announcement(
                    lang=data['lang'],
                    title=sanitize_input(data['title'], 200),
                    body=sanitize_input(data['body'], 1000),
                    priority=data.get('priority', 'normal'),
                    category=data.get('category', 'general'),
                    active=data.get('active', True),
                    start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
                    end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
                    created_at=datetime.now(ScheduleService.TIMEZONE)
                )
                
                session.add(announcement)
                session.commit()
                
                log_admin_action('create_announcement', {
                    'lang': data['lang'],
                    'title': data['title'],
                    'priority': data.get('priority', 'normal')
                })
                
                return jsonify({'success': True, 'id': announcement.id})
                
        except ValueError as e:
            return jsonify({'success': False, 'error': 'Invalid date format'}), 400
        except Exception as e:
            logger.error(f"Error creating announcement: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/announcements/<int:announcement_id>', methods=['PUT', 'DELETE'])
@auth.login_required
@require_csrf
def api_announcement_detail(announcement_id: int):
    """Update or delete announcement"""
    if request.method == 'PUT':
        try:
            data = request.json
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            with Session(engine) as session:
                announcement = session.get(Announcement, announcement_id)
                if not announcement:
                    return jsonify({'success': False, 'error': 'Announcement not found'}), 404
                
                # Update fields
                if 'title' in data:
                    announcement.title = sanitize_input(data['title'], 200)
                if 'body' in data:
                    announcement.body = sanitize_input(data['body'], 1000)
                if 'priority' in data:
                    announcement.priority = data['priority']
                if 'category' in data:
                    announcement.category = data['category']
                if 'active' in data:
                    announcement.active = data['active']
                if 'start_date' in data and data['start_date']:
                    announcement.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                if 'end_date' in data and data['end_date']:
                    announcement.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                
                session.commit()
                
                log_admin_action('update_announcement', {
                    'id': announcement_id,
                    'title': announcement.title
                })
                
                return jsonify({'success': True})
                
        except ValueError as e:
            return jsonify({'success': False, 'error': 'Invalid date format'}), 400
        except Exception as e:
            logger.error(f"Error updating announcement: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            with Session(engine) as session:
                announcement = session.get(Announcement, announcement_id)
                if not announcement:
                    return jsonify({'success': False, 'error': 'Announcement not found'}), 404
                
                title = announcement.title
                session.delete(announcement)
                session.commit()
                
                log_admin_action('delete_announcement', {
                    'id': announcement_id,
                    'title': title
                })
                
                return jsonify({'success': True})
                
        except Exception as e:
            logger.error(f"Error deleting announcement: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/announcements/<int:announcement_id>/toggle', methods=['PATCH'])
@auth.login_required
@require_csrf
def api_toggle_announcement(announcement_id: int):
    """Toggle announcement active status"""
    try:
        with Session(engine) as session:
            announcement = session.get(Announcement, announcement_id)
            if not announcement:
                return jsonify({'success': False, 'error': 'Announcement not found'}), 404
            
            announcement.active = not announcement.active
            session.commit()
            
            log_admin_action('toggle_announcement', {
                'id': announcement_id,
                'active': announcement.active
            })
            
            return jsonify({'success': True, 'active': announcement.active})
            
    except Exception as e:
        logger.error(f"Error toggling announcement: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Availability API
@admin_bp.route('/api/availability', methods=['GET', 'POST'])
@auth.login_required
@require_csrf
def api_availability():
    """Get or create availability slots"""
    if request.method == 'GET':
        try:
            year = request.args.get('year', type=int)
            month = request.args.get('month', type=int)
            
            if not year or not month:
                now = datetime.now(ScheduleService.TIMEZONE)
                year = now.year
                month = now.month
            
            with Session(engine) as session:
                # Get availability for the specified month
                start_date = date(year, month, 1)
                if month == 12:
                    end_date = date(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = date(year, month + 1, 1) - timedelta(days=1)
                
                slots = session.exec(
                    select(Availability).where(
                        Availability.availability_date >= start_date,
                        Availability.availability_date <= end_date
                    ).order_by(Availability.availability_date, Availability.start_time)
                ).all()
                
                slot_list = []
                for slot in slots:
                    slot_list.append({
                        'id': slot.id,
                        'date': slot.availability_date.isoformat(),
                        'start_time': slot.start_time.strftime('%H:%M'),
                        'end_time': slot.end_time.strftime('%H:%M'),
                        'type': slot.slot_type,
                        'capacity': slot.capacity,
                        'note': slot.note,
                        'active': slot.active,
                        'created_at': slot.created_at.isoformat()
                    })
                
                return jsonify({'success': True, 'slots': slot_list})
                
        except Exception as e:
            logger.error(f"Error loading availability: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            # Validate required fields
            missing = validate_required_fields(data, ['date', 'start_time', 'end_time'])
            if missing:
                return jsonify({'success': False, 'error': f'Missing fields: {missing}'}), 400
            
            # Parse and validate data
            try:
                slot_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                start_time = datetime.strptime(data['start_time'], '%H:%M').time()
                end_time = datetime.strptime(data['end_time'], '%H:%M').time()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date or time format'}), 400
            
            if start_time >= end_time:
                return jsonify({'success': False, 'error': 'End time must be after start time'}), 400
            
            with Session(engine) as session:
                # Check for overlapping slots
                existing = session.exec(
                    select(Availability).where(
                        Availability.availability_date == slot_date,
                        Availability.start_time < end_time,
                        Availability.end_time > start_time
                    )
                ).first()
                
                if existing:
                    return jsonify({'success': False, 'error': 'Overlapping time slot exists'}), 400
                
                # Handle recurring slots
                slots_created = []
                if data.get('recurring', False):
                    recurring_type = data.get('recurring_type', 'weekly')
                    until_date = datetime.strptime(data['recurring_until'], '%Y-%m-%d').date() if data.get('recurring_until') else None
                    
                    if not until_date:
                        until_date = slot_date + timedelta(days=90)  # Default 3 months
                    
                    current_date = slot_date
                    delta = timedelta(days=7 if recurring_type == 'weekly' else 14 if recurring_type == 'biweekly' else 30)
                    
                    while current_date <= until_date:
                        # Check if slot already exists
                        existing_recurring = session.exec(
                            select(Availability).where(
                                Availability.availability_date == current_date,
                                Availability.start_time < end_time,
                                Availability.end_time > start_time
                            )
                        ).first()
                        
                        if not existing_recurring:
                            slot = Availability(
                                availability_date=current_date,
                                start_time=start_time,
                                end_time=end_time,
                                slot_type=data.get('type', 'general'),
                                capacity=data.get('capacity', 1),
                                note=sanitize_input(data.get('note', '')),
                                active=data.get('active', True),
                                created_at=datetime.now(ScheduleService.TIMEZONE)
                            )
                            session.add(slot)
                            slots_created.append(current_date.isoformat())
                        
                        current_date += delta
                else:
                    # Single slot
                    slot = Availability(
                        availability_date=slot_date,
                        start_time=start_time,
                        end_time=end_time,
                        slot_type=data.get('type', 'general'),
                        capacity=data.get('capacity', 1),
                        note=sanitize_input(data.get('note', '')),
                        active=data.get('active', True),
                        created_at=datetime.now(ScheduleService.TIMEZONE)
                    )
                    session.add(slot)
                    slots_created.append(slot_date.isoformat())
                
                session.commit()
                
                log_admin_action('create_availability', {
                    'dates': slots_created,
                    'time': f"{data['start_time']}-{data['end_time']}",
                    'type': data.get('type', 'general')
                })
                
                return jsonify({'success': True, 'created_count': len(slots_created)})
                
        except Exception as e:
            logger.error(f"Error creating availability: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/availability/<int:slot_id>', methods=['PUT', 'DELETE'])
@auth.login_required
@require_csrf
def api_availability_detail(slot_id: int):
    """Update or delete availability slot"""
    if request.method == 'PUT':
        try:
            data = request.json
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            with Session(engine) as session:
                slot = session.get(Availability, slot_id)
                if not slot:
                    return jsonify({'success': False, 'error': 'Slot not found'}), 404
                
                # Store original values for rollback
                original_data = {
                    'date': slot.availability_date,
                    'start_time': slot.start_time,
                    'end_time': slot.end_time,
                    'type': slot.slot_type,
                    'capacity': slot.capacity,
                    'note': slot.note,
                    'active': slot.active
                }
                
                # Update fields
                if 'start_time' in data:
                    slot.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
                if 'end_time' in data:
                    slot.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
                if 'type' in data:
                    slot.slot_type = data['type']
                if 'capacity' in data:
                    slot.capacity = data['capacity']
                if 'note' in data:
                    slot.note = sanitize_input(data['note'])
                if 'active' in data:
                    slot.active = data['active']
                
                session.commit()
                
                log_admin_action('update_availability', {
                    'slot_id': slot_id,
                    'original': original_data,
                    'updated': data
                })
                
                return jsonify({'success': True})
                
        except ValueError as e:
            return jsonify({'success': False, 'error': 'Invalid time format'}), 400
        except Exception as e:
            logger.error(f"Error updating availability: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            with Session(engine) as session:
                slot = session.get(Availability, slot_id)
                if not slot:
                    return jsonify({'success': False, 'error': 'Slot not found'}), 404
                
                # Store for rollback capability
                slot_data = {
                    'date': slot.availability_date.isoformat(),
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M'),
                    'type': slot.slot_type,
                    'capacity': slot.capacity,
                    'note': slot.note,
                    'active': slot.active
                }
                
                session.delete(slot)
                session.commit()
                
                log_admin_action('delete_availability', {
                    'slot_id': slot_id,
                    'slot_data': slot_data
                })
                
                return jsonify({'success': True})
                
        except Exception as e:
            logger.error(f"Error deleting availability: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

# Bulk Operations for Availability
@admin_bp.route('/api/availability/apply-template', methods=['POST'])
@auth.login_required
@require_csrf
def api_apply_template():
    """Apply weekly template to month"""
    try:
        data = request.json
        if not data or 'template' not in data:
            return jsonify({'success': False, 'error': 'No template specified'}), 400
        
        template = data['template']
        year = data.get('year', datetime.now().year)
        month = data.get('month', datetime.now().month)
        
        # Define templates
        templates = {
            'standard': {
                'monday': [('14:00', '16:00')],
                'tuesday': [('14:00', '16:00')],
                'wednesday': [('14:00', '16:00')],
                'thursday': [('14:00', '16:00')],
                'friday': [('14:00', '16:00')],
                'saturday': [],
                'sunday': []
            },
            'compact': {
                'monday': [('15:00', '17:00')],
                'tuesday': [],
                'wednesday': [('15:00', '17:00')],
                'thursday': [],
                'friday': [('15:00', '17:00')],
                'saturday': [],
                'sunday': []
            },
            'extended': {
                'monday': [('10:00', '12:00'), ('14:00', '17:00')],
                'tuesday': [('10:00', '12:00'), ('14:00', '17:00')],
                'wednesday': [('10:00', '12:00'), ('14:00', '17:00')],
                'thursday': [('10:00', '12:00'), ('14:00', '17:00')],
                'friday': [('10:00', '12:00'), ('14:00', '17:00')],
                'saturday': [],
                'sunday': []
            }
        }
        
        if template not in templates:
            return jsonify({'success': False, 'error': 'Invalid template'}), 400
        
        template_data = templates[template]
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        created_count = 0
        with Session(engine) as session:
            # Get all days in the month
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            current_date = start_date
            while current_date <= end_date:
                weekday = weekdays[current_date.weekday()]
                time_slots = template_data.get(weekday, [])
                
                for start_time_str, end_time_str in time_slots:
                    start_time = datetime.strptime(start_time_str, '%H:%M').time()
                    end_time = datetime.strptime(end_time_str, '%H:%M').time()
                    
                    # Check if slot already exists
                    existing = session.exec(
                        select(Availability).where(
                            Availability.availability_date == current_date,
                            Availability.start_time == start_time,
                            Availability.end_time == end_time
                        )
                    ).first()
                    
                    if not existing:
                        slot = Availability(
                            availability_date=current_date,
                            start_time=start_time,
                            end_time=end_time,
                            slot_type='general',
                            capacity=1,
                            active=True,
                            created_at=datetime.now(ScheduleService.TIMEZONE)
                        )
                        session.add(slot)
                        created_count += 1
                
                current_date += timedelta(days=1)
            
            session.commit()
            
            log_admin_action('apply_template', {
                'template': template,
                'year': year,
                'month': month,
                'created_count': created_count
            })
            
            return jsonify({'success': True, 'created_count': created_count})
            
    except Exception as e:
        logger.error(f"Error applying template: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Settings Management API
@admin_bp.route('/api/contact-settings', methods=['GET', 'POST'])
@auth.login_required
@require_csrf
def api_contact_settings():
    """Get or update contact settings"""
    if request.method == 'GET':
        try:
            # Load from config.yml
            config_path = 'config.yml'
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                settings = {
                    'site_name': config.get('site', {}).get('name', ''),
                    'phone': config.get('contact', {}).get('phone', ''),
                    'email': config.get('contact', {}).get('email', ''),
                    'website': config.get('contact', {}).get('website', ''),
                    'address': config.get('location', {}).get('address', ''),
                    'latitude': config.get('location', {}).get('latitude'),
                    'longitude': config.get('location', {}).get('longitude'),
                    'directions': config.get('location', {}).get('directions', ''),
                    'services': config.get('services', {}).get('standard', [])
                }
            else:
                settings = {}
            
            return jsonify({'success': True, 'settings': settings})
            
        except Exception as e:
            logger.error(f"Error loading contact settings: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            # Load existing config
            config_path = 'config.yml'
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            
            # Create backup
            backup_path = f'config.yml.bak.{int(datetime.now().timestamp())}'
            if os.path.exists(config_path):
                os.rename(config_path, backup_path)
            
            # Update config
            config.setdefault('site', {})['name'] = sanitize_input(data.get('site_name', ''), 100)
            config.setdefault('contact', {}).update({
                'phone': sanitize_input(data.get('phone', ''), 20),
                'email': sanitize_input(data.get('email', ''), 100),
                'website': sanitize_input(data.get('website', ''), 200)
            })
            config.setdefault('location', {}).update({
                'address': sanitize_input(data.get('address', ''), 300),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'directions': sanitize_input(data.get('directions', ''), 500)
            })
            config.setdefault('services', {})['standard'] = data.get('services', [])
            
            # Save config
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            log_admin_action('update_contact_settings', {
                'fields_updated': list(data.keys()),
                'backup_created': backup_path
            })
            
            return jsonify({'success': True, 'backup_created': backup_path})
            
        except Exception as e:
            logger.error(f"Error updating contact settings: {e}")
            # Restore backup if exists
            if 'backup_path' in locals() and os.path.exists(backup_path):
                os.rename(backup_path, config_path)
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/appearance-settings', methods=['GET', 'POST'])
@auth.login_required
@require_csrf
def api_appearance_settings():
    """Get or update appearance settings"""
    if request.method == 'GET':
        try:
            # Return basic appearance settings
            settings = {
                'theme': 'default',
                'primary_color': '#0891b2',
                'secondary_color': '#f97316',
                'font_family': 'Sarabun',
                'logo_url': '',
                'favicon_url': '',
                'custom_css': ''
            }
            return jsonify({'success': True, 'settings': settings})
            
        except Exception as e:
            logger.error(f"Error loading appearance settings: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            # For now, just acknowledge the update
            log_admin_action('update_appearance_settings', {
                'settings_updated': list(data.keys())
            })
            
            return jsonify({'success': True, 'message': 'Appearance settings updated'})
            
        except Exception as e:
            logger.error(f"Error updating appearance settings: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

# Legal/Cookie compliance endpoints (basic stubs)
@admin_bp.route('/api/legal/cookie-banner-info')
def api_legal_cookie_banner_info():
    """Get cookie banner information"""
    lang = request.args.get('lang', 'th')
    return jsonify({
        'success': True,
        'banner_text': 'This website uses cookies for functionality.',
        'accept_text': 'Accept',
        'decline_text': 'Decline',
        'language': lang
    })

@admin_bp.route('/api/legal/consent-status')
def api_legal_consent_status():
    """Get consent status"""
    return jsonify({
        'success': True,
        'consent_given': False,
        'timestamp': None
    })

@admin_bp.route('/api/legal/consent', methods=['POST'])
def api_legal_consent():
    """Handle consent submission"""
    data = request.json or {}
    consent = data.get('consent', False)
    return jsonify({
        'success': True,
        'consent_recorded': consent,
        'timestamp': datetime.now().isoformat()
    })

# System Management API
@admin_bp.route('/api/system-info')
@auth.login_required
def api_system_info():
    """Get system information"""
    try:
        import psutil
        import sys
        
        # Calculate uptime (simplified)
        boot_time = psutil.boot_time()
        uptime = datetime.now().timestamp() - boot_time
        uptime_str = str(timedelta(seconds=int(uptime)))
        
        info = {
            'version': '1.0.0',
            'uptime': uptime_str,
            'python_version': sys.version.split()[0],
            'db_status': 'SQLite Connected',
            'memory_usage': f"{psutil.virtual_memory().percent}%",
            'disk_usage': f"{psutil.disk_usage('/').percent}%"
        }
        
        return jsonify({'success': True, **info})
        
    except ImportError:
        # Fallback without psutil
        return jsonify({
            'success': True,
            'version': '1.0.0',
            'uptime': 'Unknown',
            'db_status': 'SQLite Connected'
        })
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Bulk Operations API
@admin_bp.route('/api/bulk-availability', methods=['POST'])
@auth.login_required
@require_csrf
def api_bulk_availability():
    """Bulk create availability slots"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        operation = data.get('operation', 'create')
        
        if operation == 'create_template':
            return _create_availability_template(data)
        elif operation == 'import_csv':
            return _import_availability_csv(data)
        elif operation == 'bulk_delete':
            return _bulk_delete_availability(data)
        else:
            return jsonify({'success': False, 'error': 'Invalid operation'}), 400
            
    except Exception as e:
        logger.error(f"Error in bulk availability operation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def _create_availability_template(data):
    """Create availability slots based on template"""
    template_name = data.get('template_name', 'standard')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    
    if not start_date_str or not end_date_str:
        return jsonify({'success': False, 'error': 'Start and end dates required'}), 400
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    
    # Define templates
    templates = {
        'standard': {
            'monday': [('09:00', '12:00'), ('14:00', '17:00')],
            'tuesday': [('09:00', '12:00'), ('14:00', '17:00')],
            'wednesday': [('09:00', '12:00')],
            'thursday': [('09:00', '12:00'), ('14:00', '17:00')],
            'friday': [('09:00', '13:00')],
            'saturday': [],
            'sunday': []
        },
        'extended': {
            'monday': [('08:00', '12:00'), ('13:00', '18:00')],
            'tuesday': [('08:00', '12:00'), ('13:00', '18:00')],
            'wednesday': [('08:00', '12:00'), ('13:00', '18:00')],
            'thursday': [('08:00', '12:00'), ('13:00', '18:00')],
            'friday': [('08:00', '12:00'), ('13:00', '18:00')],
            'saturday': [('09:00', '13:00')],
            'sunday': []
        },
        'minimal': {
            'monday': [('10:00', '12:00')],
            'tuesday': [('10:00', '12:00')],
            'wednesday': [('10:00', '12:00')],
            'thursday': [('10:00', '12:00')],
            'friday': [('10:00', '12:00')],
            'saturday': [],
            'sunday': []
        }
    }
    
    template = templates.get(template_name)
    if not template:
        return jsonify({'success': False, 'error': 'Invalid template'}), 400
    
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    created_count = 0
    skipped_count = 0
    
    with Session(engine) as session:
        current_date = start_date
        while current_date <= end_date:
            weekday = weekdays[current_date.weekday()]
            time_slots = template.get(weekday, [])
            
            for start_time_str, end_time_str in time_slots:
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
                
                # Check if slot already exists
                existing = session.exec(
                    select(Availability).where(
                        Availability.availability_date == current_date,
                        Availability.start_time == start_time,
                        Availability.end_time == end_time
                    )
                ).first()
                
                if not existing:
                    slot = Availability(
                        availability_date=current_date,
                        start_time=start_time,
                        end_time=end_time,
                        slot_type='general',
                        capacity=1,
                        active=True,
                        created_at=datetime.now(ScheduleService.TIMEZONE)
                    )
                    session.add(slot)
                    created_count += 1
                else:
                    skipped_count += 1
            
            current_date += timedelta(days=1)
        
        session.commit()
        
        log_admin_action('bulk_create_availability', {
            'template': template_name,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'created_count': created_count,
            'skipped_count': skipped_count
        })
        
        return jsonify({
            'success': True,
            'created_count': created_count,
            'skipped_count': skipped_count,
            'message': f'{created_count} Slots erstellt, {skipped_count} übersprungen (bereits vorhanden)'
        })

def _import_availability_csv(data):
    """Import availability slots from CSV data"""
    csv_content = data.get('csv_content')
    if not csv_content:
        return jsonify({'success': False, 'error': 'No CSV content provided'}), 400
    
    # Parse CSV content (expecting: date,start_time,end_time,type,capacity,note)
    import csv
    import io
    
    reader = csv.DictReader(io.StringIO(csv_content))
    created_count = 0
    error_count = 0
    errors = []
    
    with Session(engine) as session:
        for row_num, row in enumerate(reader, start=2):  # Start at 2 because of header
            try:
                slot_date = datetime.strptime(row.get('date', ''), '%Y-%m-%d').date()
                start_time = datetime.strptime(row.get('start_time', ''), '%H:%M').time()
                end_time = datetime.strptime(row.get('end_time', ''), '%H:%M').time()
                slot_type = row.get('type', 'general')
                capacity = int(row.get('capacity', 1))
                note = row.get('note', '')
                
                # Validate
                if start_time >= end_time:
                    raise ValueError("End time must be after start time")
                
                # Check for existing slot
                existing = session.exec(
                    select(Availability).where(
                        Availability.availability_date == slot_date,
                        Availability.start_time == start_time,
                        Availability.end_time == end_time
                    )
                ).first()
                
                if not existing:
                    slot = Availability(
                        availability_date=slot_date,
                        start_time=start_time,
                        end_time=end_time,
                        slot_type=slot_type,
                        capacity=capacity,
                        note=note.strip() if note else None,
                        active=True,
                        created_at=datetime.now(ScheduleService.TIMEZONE)
                    )
                    session.add(slot)
                    created_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f'Zeile {row_num}: {str(e)}')
                if error_count > 10:  # Limit error messages
                    errors.append('... und weitere Fehler')
                    break
        
        if error_count == 0:
            session.commit()
            log_admin_action('bulk_import_availability', {
                'created_count': created_count,
                'source': 'csv'
            })
        else:
            session.rollback()  # Don't commit if there were errors
    
    return jsonify({
        'success': error_count == 0,
        'created_count': created_count,
        'error_count': error_count,
        'errors': errors[:10] if errors else [],
        'message': f'{created_count} Slots erstellt' if error_count == 0 else f'{error_count} Fehler gefunden'
    })

def _bulk_delete_availability(data):
    """Bulk delete availability slots"""
    criteria = data.get('criteria', {})
    
    with Session(engine) as session:
        query = select(Availability)
        
        # Apply filters
        if criteria.get('date_from'):
            date_from = datetime.strptime(criteria['date_from'], '%Y-%m-%d').date()
            query = query.where(Availability.availability_date >= date_from)
        
        if criteria.get('date_to'):
            date_to = datetime.strptime(criteria['date_to'], '%Y-%m-%d').date()
            query = query.where(Availability.availability_date <= date_to)
        
        if criteria.get('slot_type'):
            query = query.where(Availability.slot_type == criteria['slot_type'])
        
        if criteria.get('inactive_only'):
            query = query.where(Availability.active == False)
        
        slots_to_delete = session.exec(query).all()
        deleted_count = len(slots_to_delete)
        
        for slot in slots_to_delete:
            session.delete(slot)
        
        session.commit()
        
        log_admin_action('bulk_delete_availability', {
            'deleted_count': deleted_count,
            'criteria': criteria
        })
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'{deleted_count} Slots gelöscht'
        })

@admin_bp.route('/api/export-availability', methods=['GET'])
@auth.login_required  
def api_export_availability():
    """Export availability slots as CSV"""
    try:
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        if not year or not month:
            now = datetime.now(ScheduleService.TIMEZONE)
            year = now.year
            month = now.month
        
        with Session(engine) as session:
            # Get availability for the specified month
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            slots = session.exec(
                select(Availability).where(
                    Availability.availability_date >= start_date,
                    Availability.availability_date <= end_date
                ).order_by(Availability.availability_date, Availability.start_time)
            ).all()
            
            # Generate CSV content
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(['date', 'start_time', 'end_time', 'type', 'capacity', 'note', 'active'])
            
            # Data rows
            for slot in slots:
                writer.writerow([
                    slot.availability_date.strftime('%Y-%m-%d'),
                    slot.start_time.strftime('%H:%M'),
                    slot.end_time.strftime('%H:%M'),
                    slot.slot_type,
                    slot.capacity,
                    slot.note or '',
                    'yes' if slot.active else 'no'
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            # Return as downloadable file
            response = make_response(csv_content)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=availability-{year}-{month:02d}.csv'
            
            log_admin_action('export_availability', {
                'year': year,
                'month': month,
                'count': len(slots)
            })
            
            return response
            
    except Exception as e:
        logger.error(f"Error exporting availability: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Logging and Audit Trail API
@admin_bp.route('/api/logs')
@auth.login_required
def api_logs():
    """Get system logs with filtering"""
    try:
        level = request.args.get('level', '')
        source = request.args.get('source', '')
        date_filter = request.args.get('date', '')
        format_type = request.args.get('format', 'json')
        
        # Read log file (simplified - in production use proper log management)
        log_file = 'app.log'
        logs = []
        stats = {'error': 0, 'warning': 0, 'info': 0, 'debug': 0, 'total': 0}
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f.readlines()[-1000:]:  # Last 1000 lines
                    try:
                        # Parse log line (adjust based on your log format)
                        parts = line.strip().split(' - ', 3)
                        if len(parts) >= 4:
                            timestamp_str = parts[0]
                            log_level = parts[1]
                            log_source = parts[2]
                            message = parts[3]
                            
                            # Apply filters
                            if level and log_level != level:
                                continue
                            if source and source not in log_source:
                                continue
                            if date_filter and not timestamp_str.startswith(date_filter):
                                continue
                            
                            log_entry = {
                                'timestamp': timestamp_str,
                                'level': log_level,
                                'source': log_source,
                                'message': message
                            }
                            
                            logs.append(log_entry)
                            stats[log_level.lower()] = stats.get(log_level.lower(), 0) + 1
                            stats['total'] += 1
                    
                    except Exception:
                        continue
        
        if format_type == 'download':
            # Return as downloadable text file
            log_text = '\n'.join([f"[{log['timestamp']}] [{log['level']}] [{log['source']}] {log['message']}" for log in logs])
            response = make_response(log_text)
            response.headers['Content-Type'] = 'text/plain'
            response.headers['Content-Disposition'] = f'attachment; filename=logs-{datetime.now().strftime("%Y%m%d")}.txt'
            return response
        
        return jsonify({
            'success': True,
            'logs': logs[-100:],  # Return last 100 entries
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/logs', methods=['DELETE'])
@auth.login_required
@require_csrf
def api_clear_logs():
    """Clear system logs"""
    try:
        log_file = 'app.log'
        backup_file = f'app.log.bak.{int(datetime.now().timestamp())}'
        
        if os.path.exists(log_file):
            # Create backup before clearing
            os.rename(log_file, backup_file)
            # Create new empty log file
            open(log_file, 'w').close()
            
            log_admin_action('clear_logs', {'backup_created': backup_file})
            return jsonify({'success': True, 'backup_created': backup_file})
        else:
            return jsonify({'success': True, 'message': 'No log file found'})
            
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Social Media Management API
@admin_bp.route('/social-media', methods=['GET', 'POST'])
@auth.login_required
@require_csrf
def manage_social_media():
    """Manage social media settings and platforms"""
    social_service = SocialMediaService()
    
    if request.method == 'POST':
        try:
            # Update social media configuration
            data = request.form.to_dict()
            
            # Load current config
            config_path = 'config.yml'
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Update social media settings
            if 'social_enabled' in data:
                config.setdefault('social_media', {})['enabled'] = data['social_enabled'] == 'true'
            
            if 'show_follow_section' in data:
                config.setdefault('social_media', {}).setdefault('settings', {})['show_follow_section'] = data['show_follow_section'] == 'true'
            
            if 'show_share_buttons' in data:
                config.setdefault('social_media', {}).setdefault('settings', {})['show_share_buttons'] = data['show_share_buttons'] == 'true'
            
            # Update platform settings
            platforms = config.setdefault('social_media', {}).setdefault('platforms', {})
            
            for platform_name in ['line', 'facebook', 'instagram', 'whatsapp', 'tiktok', 'youtube', 'google_business']:
                platform_data = platforms.setdefault(platform_name, {})
                
                # Enable/disable platform
                platform_data['enabled'] = f'{platform_name}_enabled' in data
                platform_data['qr_enabled'] = f'{platform_name}_qr_enabled' in data
                
                # Update URLs and usernames
                if f'{platform_name}_url' in data:
                    platform_data['url'] = sanitize_input(data[f'{platform_name}_url'], 500)
                
                if f'{platform_name}_username' in data:
                    if platform_name == 'line':
                        platform_data['official_account'] = sanitize_input(data[f'{platform_name}_username'], 100)
                    else:
                        platform_data['username'] = sanitize_input(data[f'{platform_name}_username'], 100)
            
            # Save updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            log_admin_action('update_social_media', {
                'platforms_updated': [p for p in platforms.keys() if platforms[p].get('enabled')]
            })
            
            flash('Social Media Einstellungen erfolgreich aktualisiert!', 'success')
            return redirect(url_for('admin.manage_social_media'))
            
        except Exception as e:
            logger.error(f"Error updating social media settings: {e}")
            flash(f'Fehler beim Aktualisieren: {str(e)}', 'error')
    
    # Get current settings
    platforms = social_service.get_platforms_for_display()
    stats = social_service.get_social_media_stats()
    
    return render_admin_template('admin/social_media.html',
        platforms=platforms,
        stats=stats,
        config=social_service.config
    )

@admin_bp.route('/api/social-media/platforms', methods=['GET'])
@auth.login_required
def api_social_platforms():
    """Get social media platforms configuration"""
    try:
        social_service = SocialMediaService()
        platforms = social_service.get_platforms_for_display()
        stats = social_service.get_social_media_stats()
        
        return jsonify({
            'success': True,
            'platforms': platforms,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting social platforms: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/social-media/qr-generate', methods=['POST'])
@auth.login_required
@require_csrf
def api_generate_social_qr():
    """Generate QR codes for social media platforms"""
    try:
        data = request.json
        platforms = data.get('platforms', [])
        size = data.get('size', 'medium')
        
        social_service = SocialMediaService()
        results = {}
        
        if platforms == ['all']:
            # Generate for all enabled platforms
            platforms = social_service.get_enabled_platforms()
        
        for platform in platforms:
            filename = social_service.generate_platform_qr(platform, size)
            if filename:
                results[platform] = {
                    'filename': filename,
                    'url': f'/static/qr/{filename}',
                    'download_url': f'/static/qr/{filename}'
                }
        
        log_admin_action('generate_social_qr', {
            'platforms': platforms,
            'size': size,
            'generated_count': len(results)
        })
        
        return jsonify({
            'success': True,
            'generated': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error generating social QR codes: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/social-media/posts', methods=['GET', 'POST'])
@auth.login_required
@require_csrf
def api_social_posts():
    """Manage social media posts"""
    if request.method == 'GET':
        try:
            with Session(engine) as session:
                posts = session.exec(
                    select(SocialMediaPost).order_by(SocialMediaPost.created_at.desc())
                ).all()
                
                post_list = []
                for post in posts:
                    post_list.append({
                        'id': post.id,
                        'platform': post.platform,
                        'post_type': post.post_type,
                        'title': post.title,
                        'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                        'lang': post.lang,
                        'scheduled_for': post.scheduled_for.isoformat() if post.scheduled_for else None,
                        'posted_at': post.posted_at.isoformat() if post.posted_at else None,
                        'active': post.active,
                        'created_at': post.created_at.isoformat()
                    })
                
                return jsonify({'success': True, 'posts': post_list})
                
        except Exception as e:
            logger.error(f"Error getting social posts: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            
            # Validate required fields
            missing = validate_required_fields(data, ['platform', 'content', 'lang'])
            if missing:
                return jsonify({'success': False, 'error': f'Missing fields: {missing}'}), 400
            
            with Session(engine) as session:
                # Format content for platform
                social_service = SocialMediaService()
                formatted_content = social_service.format_content_for_platform(
                    data['platform'], 
                    data['content'], 
                    data['lang']
                )
                
                post = SocialMediaPost(
                    platform=data['platform'],
                    post_type=data.get('post_type', 'announcement'),
                    title=sanitize_input(data.get('title', ''), 200),
                    content=formatted_content,
                    image_url=sanitize_input(data.get('image_url', ''), 500),
                    lang=data['lang'],
                    scheduled_for=datetime.strptime(data['scheduled_for'], '%Y-%m-%d %H:%M') if data.get('scheduled_for') else None,
                    active=data.get('active', True),
                    created_at=datetime.now(ScheduleService.TIMEZONE)
                )
                
                session.add(post)
                session.commit()
                
                log_admin_action('create_social_post', {
                    'platform': data['platform'],
                    'lang': data['lang'],
                    'post_type': data.get('post_type', 'announcement')
                })
                
                return jsonify({'success': True, 'id': post.id})
                
        except Exception as e:
            logger.error(f"Error creating social post: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/social-media/posts/<int:post_id>', methods=['PUT', 'DELETE'])
@auth.login_required
@require_csrf
def api_social_post_detail(post_id: int):
    """Update or delete social media post"""
    if request.method == 'PUT':
        try:
            data = request.json
            
            with Session(engine) as session:
                post = session.get(SocialMediaPost, post_id)
                if not post:
                    return jsonify({'success': False, 'error': 'Post not found'}), 404
                
                # Update fields
                if 'title' in data:
                    post.title = sanitize_input(data['title'], 200)
                if 'content' in data:
                    social_service = SocialMediaService()
                    post.content = social_service.format_content_for_platform(
                        post.platform, 
                        data['content'], 
                        post.lang
                    )
                if 'scheduled_for' in data and data['scheduled_for']:
                    post.scheduled_for = datetime.strptime(data['scheduled_for'], '%Y-%m-%d %H:%M')
                if 'active' in data:
                    post.active = data['active']
                
                session.commit()
                
                log_admin_action('update_social_post', {'post_id': post_id})
                
                return jsonify({'success': True})
                
        except Exception as e:
            logger.error(f"Error updating social post: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            with Session(engine) as session:
                post = session.get(SocialMediaPost, post_id)
                if not post:
                    return jsonify({'success': False, 'error': 'Post not found'}), 404
                
                platform = post.platform
                session.delete(post)
                session.commit()
                
                log_admin_action('delete_social_post', {
                    'post_id': post_id,
                    'platform': platform
                })
                
                return jsonify({'success': True})
                
        except Exception as e:
            logger.error(f"Error deleting social post: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/social-media/analytics', methods=['GET'])
@auth.login_required
def api_social_analytics():
    """Get social media analytics and insights"""
    try:
        social_service = SocialMediaService()
        
        # Basic analytics from database
        with Session(engine) as session:
            # Posts by platform
            posts_by_platform = {}
            platforms = social_service.get_enabled_platforms()
            
            for platform in platforms:
                count = len(session.exec(
                    select(SocialMediaPost).where(
                        SocialMediaPost.platform == platform,
                        SocialMediaPost.active == True
                    )
                ).all())
                posts_by_platform[platform] = count
            
            # Recent activity
            recent_posts = session.exec(
                select(SocialMediaPost).where(
                    SocialMediaPost.created_at >= datetime.now() - timedelta(days=30)
                ).order_by(SocialMediaPost.created_at.desc())
            ).all()
            
            # Calculate trends
            engagement_by_platform = {}
            for post in recent_posts:
                platform = post.platform
                if platform not in engagement_by_platform:
                    engagement_by_platform[platform] = {
                        'posts': 0,
                        'total_engagement': 0
                    }
                engagement_by_platform[platform]['posts'] += 1
                
                # Get engagement stats if available
                stats = post.engagement_stats
                if stats:
                    engagement_by_platform[platform]['total_engagement'] += stats.get('likes', 0) + stats.get('shares', 0)
        
        analytics = {
            'enabled_platforms': len(platforms),
            'total_posts': sum(posts_by_platform.values()),
            'posts_by_platform': posts_by_platform,
            'engagement_by_platform': engagement_by_platform,
            'recent_activity': len(recent_posts),
            'qr_downloads': 0,  # Would need to track in real implementation
            'top_platform': max(posts_by_platform.items(), key=lambda x: x[1])[0] if posts_by_platform else None
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        logger.error(f"Error getting social analytics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==============================================
# SETUP WIZARD API ENDPOINTS - SUB-AGENT 2
# ==============================================

@admin_bp.route('/api/setup-wizard', methods=['POST'])
@require_csrf
@rate_limit
def handle_setup_wizard():
    """Handle complete setup wizard submission"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        session_id = data.get('session_id', secrets.token_hex(16))
        step = data.get('step', 1)
        step_data = data.get('data', {})
        
        # Store step data in wizard sessions
        if session_id not in wizard_sessions:
            wizard_sessions[session_id] = {
                'created_at': datetime.now(),
                'steps': {},
                'completed': False
            }
        
        wizard_sessions[session_id]['steps'][step] = step_data
        wizard_sessions[session_id]['last_updated'] = datetime.now()
        
        # If this is the final step, process complete configuration
        if step == 7:
            success = apply_wizard_configuration(session_id)
            if success:
                wizard_sessions[session_id]['completed'] = True
                # Log successful setup
                logger.info(f"Setup wizard completed successfully for session {session_id}")
                
                return jsonify({
                    'success': True,
                    'message': 'Setup erfolgreich abgeschlossen!',
                    'redirect': '/admin'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Konfiguration konnte nicht angewendet werden'
                }), 500
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'next_step': step + 1
        })
        
    except Exception as e:
        logger.error(f"Setup wizard error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/validate-field', methods=['POST'])
@require_csrf  
@rate_limit
def validate_wizard_field():
    """Real-time field validation for setup wizard"""
    try:
        data = request.get_json()
        field_name = data.get('field')
        value = data.get('value')
        
        if not field_name:
            return jsonify({'valid': False, 'message': 'Feldname fehlt'})
        
        validation_result = perform_field_validation(field_name, value)
        return jsonify(validation_result)
        
    except Exception as e:
        logger.error(f"Field validation error: {e}")
        return jsonify({'valid': False, 'message': 'Validierungsfehler'}), 500

@admin_bp.route('/api/create-backup', methods=['POST'])
@require_csrf
@rate_limit
def create_system_backup():
    """Create complete system backup"""
    try:
        # Create temporary backup file
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'database': {},
            'config': {},
            'settings': {}
        }
        
        # Backup database content
        with Session(engine) as session:
            # Export all settings
            settings = session.exec(select(Settings)).all()
            backup_data['settings'] = [setting.dict() for setting in settings]
            
            # Export announcements
            announcements = session.exec(select(Announcement)).all()
            backup_data['database']['announcements'] = [ann.dict() for ann in announcements]
            
            # Export availability
            availability = session.exec(select(Availability)).all()
            backup_data['database']['availability'] = [slot.dict() for slot in availability]
            
            # Export hour exceptions
            exceptions = session.exec(select(HourException)).all()
            backup_data['database']['exceptions'] = [exc.dict() for exc in exceptions]
        
        # Load config.yml if exists
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                backup_data['config'] = yaml.safe_load(f)
        
        # Create ZIP file with backup
        temp_dir = tempfile.mkdtemp()
        backup_filename = f"qr-portal-backup-{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        backup_path = os.path.join(temp_dir, backup_filename)
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add backup data as JSON
            zf.writestr('backup.json', json.dumps(backup_data, indent=2, ensure_ascii=False))
            
            # Add config.yml if exists
            if os.path.exists(config_path):
                zf.write(config_path, 'config.yml')
        
        logger.info(f"Backup created successfully: {backup_filename}")
        return send_file(backup_path, as_attachment=True, download_name=backup_filename)
        
    except Exception as e:
        logger.error(f"Backup creation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/restore-backup', methods=['POST'])
@require_csrf
@rate_limit  
def restore_system_backup():
    """Restore system from backup file"""
    try:
        if 'backup_file' not in request.files:
            return jsonify({'success': False, 'error': 'Keine Backup-Datei gefunden'})
        
        backup_file = request.files['backup_file']
        if backup_file.filename == '':
            return jsonify({'success': False, 'error': 'Keine Datei ausgewählt'})
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        backup_path = os.path.join(temp_dir, secure_filename(backup_file.filename))
        backup_file.save(backup_path)
        
        # Extract and process backup
        backup_data = None
        with zipfile.ZipFile(backup_path, 'r') as zf:
            # Read backup.json
            with zf.open('backup.json') as f:
                backup_data = json.load(f)
            
            # Restore config.yml if present
            try:
                with zf.open('config.yml') as f:
                    config_content = f.read()
                    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
                    with open(config_path, 'wb') as conf_file:
                        conf_file.write(config_content)
            except KeyError:
                pass  # config.yml not in backup
        
        if not backup_data:
            return jsonify({'success': False, 'error': 'Ungültiges Backup-Format'})
        
        # Restore database content
        with Session(engine) as session:
            # Clear existing data (be careful!)
            session.exec("DELETE FROM settings")
            session.exec("DELETE FROM announcements WHERE id > 0")
            session.exec("DELETE FROM availability WHERE id > 0")
            session.exec("DELETE FROM hour_exceptions WHERE id > 0")
            
            # Restore settings
            for setting_data in backup_data.get('settings', []):
                setting = Settings(**setting_data)
                session.add(setting)
            
            # Restore announcements
            for ann_data in backup_data.get('database', {}).get('announcements', []):
                announcement = Announcement(**ann_data)
                session.add(announcement)
            
            # Restore availability
            for avail_data in backup_data.get('database', {}).get('availability', []):
                availability = Availability(**avail_data)
                session.add(availability)
            
            # Restore hour exceptions
            for exc_data in backup_data.get('database', {}).get('exceptions', []):
                exception = HourException(**exc_data)
                session.add(exception)
            
            session.commit()
        
        # Clean up temporary files
        os.unlink(backup_path)
        os.rmdir(temp_dir)
        
        logger.info("Backup restored successfully")
        return jsonify({
            'success': True,
            'message': 'Backup erfolgreich wiederhergestellt'
        })
        
    except Exception as e:
        logger.error(f"Backup restoration error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/security-event', methods=['POST'])
@require_csrf
@rate_limit
def log_security_event():
    """Log security events from frontend"""
    try:
        data = request.get_json()
        event_type = data.get('type')
        details = data.get('details', {})
        
        # Log security event
        logger.warning(f"Security event: {event_type} from {request.remote_addr} - {details}")
        
        # Store in database if needed (implement security events table)
        # For now, just log it
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Security event logging error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def apply_wizard_configuration(session_id: str) -> bool:
    """Apply complete wizard configuration to system"""
    try:
        session_data = wizard_sessions.get(session_id)
        if not session_data or not session_data.get('steps'):
            return False
        
        steps = session_data['steps']
        
        # Step 1: Welcome/Basic Info
        site_name = steps.get('1', {}).get('site_name', 'Labor Pattaya')
        site_subtitle = steps.get('1', {}).get('site_subtitle', 'Blutabnahme & Labordiagnostik')
        
        # Step 2: Location
        location_data = steps.get('2', {})
        
        # Step 3: Opening Hours  
        hours_data = steps.get('3', {})
        
        # Step 4: Design
        design_data = steps.get('4', {})
        
        # Step 5: Kiosk Settings
        kiosk_data = steps.get('5', {})
        
        # Step 6: System Settings
        system_data = steps.get('6', {})
        
        # Step 7: Completion/Admin
        admin_data = steps.get('7', {})
        
        # Apply settings to database
        with Session(engine) as session:
            # Update or create settings
            settings_updates = {
                'site_name': site_name,
                'site_subtitle': site_subtitle,
                'contact_phone': location_data.get('phone', ''),
                'contact_email': location_data.get('email', ''),
                'location_address': location_data.get('address', ''),
                'location_latitude': location_data.get('latitude', ''),
                'location_longitude': location_data.get('longitude', ''),
                'theme': design_data.get('theme', 'medical'),
                'kiosk_font_scale': kiosk_data.get('font_scale', '1.0'),
                'kiosk_rotation_interval': kiosk_data.get('rotation_interval', '30'),
                'admin_password_hash': hashlib.sha256(admin_data.get('admin_password', 'admin').encode()).hexdigest()
            }
            
            for key, value in settings_updates.items():
                setting = session.exec(select(Settings).where(Settings.key == key)).first()
                if setting:
                    setting.value = str(value)
                else:
                    setting = Settings(key=key, value=str(value))
                    session.add(setting)
            
            session.commit()
        
        # Update config.yml
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Update configuration
            config['site']['name'] = site_name
            config['contact']['phone'] = location_data.get('phone', '')
            config['contact']['email'] = location_data.get('email', '')
            config['location']['address'] = location_data.get('address', '')
            config['location']['latitude'] = location_data.get('latitude', 12.923556)
            config['location']['longitude'] = location_data.get('longitude', 100.882507)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        logger.error(f"Error applying wizard configuration: {e}")
        return False

def perform_field_validation(field_name: str, value: str) -> dict:
    """Perform validation for specific fields"""
    try:
        if field_name == 'site_name':
            if not value or len(value.strip()) < 3:
                return {'valid': False, 'message': 'Name muss mindestens 3 Zeichen lang sein'}
            if len(value) > 100:
                return {'valid': False, 'message': 'Name darf maximal 100 Zeichen lang sein'}
                
        elif field_name == 'contact_email':
            import re
            if not value:
                return {'valid': False, 'message': 'E-Mail ist erforderlich'}
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', value):
                return {'valid': False, 'message': 'Ungültige E-Mail-Adresse'}
                
        elif field_name == 'contact_phone':
            if not value:
                return {'valid': False, 'message': 'Telefonnummer ist erforderlich'}
            if not value.startswith('+'):
                return {'valid': False, 'message': 'Telefonnummer muss mit + beginnen'}
                
        elif field_name == 'admin_password':
            if not value or len(value) < 8:
                return {'valid': False, 'message': 'Passwort muss mindestens 8 Zeichen lang sein'}
            
            # Check password strength
            import re
            score = 0
            if re.search(r'[A-Z]', value): score += 1
            if re.search(r'[a-z]', value): score += 1  
            if re.search(r'\d', value): score += 1
            if re.search(r'[!@#$%^&*(),.?":{}|<>]', value): score += 1
            
            if score < 3:
                return {'valid': False, 'message': 'Passwort zu schwach - benötigt Groß-/Kleinbuchstaben, Zahlen, Sonderzeichen'}
                
        elif field_name in ['latitude', 'longitude']:
            try:
                coord = float(value)
                if field_name == 'latitude' and (coord < -90 or coord > 90):
                    return {'valid': False, 'message': 'Breitengrad muss zwischen -90 und 90 liegen'}
                elif field_name == 'longitude' and (coord < -180 or coord > 180):
                    return {'valid': False, 'message': 'Längengrad muss zwischen -180 und 180 liegen'}
            except ValueError:
                return {'valid': False, 'message': 'Muss eine gültige Zahl sein'}
        
        return {'valid': True}
        
    except Exception as e:
        logger.error(f"Field validation error for {field_name}: {e}")
        return {'valid': False, 'message': 'Validierungsfehler'}

@admin_bp.route('/appointments')
@auth.login_required
def manage_appointments():
    """Manage appointment bookings (if feature is enabled)"""
    # Check if booking feature is enabled
    booking_enabled = os.getenv('FEATURE_BOOKING', 'false').lower() == 'true'
    
    if not booking_enabled:
        return render_admin_template('admin/appointments.html',
                             booking_enabled=False,
                             services=[],
                             today_stats={},
                             today=datetime.now().date())
    
    try:
        # Import booking models only if feature is enabled
        from app.models_booking import BookingService, BookingStatistics
        from app.services.booking import BookingManager
        from app.database import get_session
        
        session = get_session()
        booking_manager = BookingManager(session)
        
        # Get all services
        services = session.query(BookingService).order_by(BookingService.sort_order).all()
        
        # Get today's statistics
        today = datetime.now().date()
        today_stats = booking_manager.get_daily_statistics(today)
        
        return render_admin_template('admin/appointments.html',
                             booking_enabled=True,
                             services=services,
                             today_stats=today_stats,
                             today=today)
                                 
    except ImportError as e:
        logger.error(f"Booking feature dependencies not found: {e}")
        return render_admin_template('admin/appointments.html',
                             booking_enabled=False,
                             services=[],
                             today_stats={},
                             today=datetime.now().date())


@admin_bp.route('/change-password', methods=['GET', 'POST'])
@auth.login_required
@rate_limit
@require_csrf
def change_password():
    """Change admin password"""
    if request.method == 'POST':
        try:
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validate current password
            admin_user = os.getenv('ADMIN_USERNAME', 'admin')
            admin_pass = os.getenv('ADMIN_PASSWORD', 'admin123')
            
            if not current_password == admin_pass:
                flash(I18nService.translate('admin.password_change.invalid_current'), 'error')
                return redirect(url_for('admin.change_password'))
            
            # Validate new password
            if len(new_password) < 8:
                flash(I18nService.translate('admin.forms.required_field'), 'error')
                return redirect(url_for('admin.change_password'))
            
            if new_password != confirm_password:
                flash(I18nService.translate('admin.password_change.password_mismatch'), 'error')
                return redirect(url_for('admin.change_password'))
            
            # Check password strength
            if not validate_password_strength(new_password):
                flash(I18nService.translate('admin.forms.invalid_input'), 'error')
                return redirect(url_for('admin.change_password'))
            
            # Get or create admin user in database
            with Session(engine) as session:
                admin_user_db = session.exec(select(AdminUser).where(AdminUser.username == admin_user)).first()
                
                if not admin_user_db:
                    # Create new admin user
                    admin_user_db = AdminUser(username=admin_user)
                    session.add(admin_user_db)
                
                # Set new password
                admin_user_db.set_password(new_password)
                session.commit()
                
                # Log the password change
                log_admin_action('password_change', 
                               details={'changed_at': datetime.utcnow().isoformat()})
            
            # Update environment variable for immediate effect
            update_env_password(new_password)
            
            flash(I18nService.translate('admin.password_change.password_changed'), 'success')
            
            # Force logout by clearing auth
            from flask import g
            if hasattr(g, '_login'):
                delattr(g, '_login')
            
            return redirect(url_for('admin.dashboard'))
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            flash(I18nService.translate('admin.forms.save_error') + ': ' + str(e), 'error')
            return redirect(url_for('admin.change_password'))
    
    # GET request - show form
    flask_session['csrf_token'] = generate_csrf_token()
    
    return render_admin_template('admin/change_password.html',
                         csrf_token=generate_csrf_token())


def validate_password_strength(password: str) -> bool:
    """Validate password strength requirements"""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    # Require at least 3 of 4 categories
    categories = sum([has_upper, has_lower, has_digit, has_special])
    return categories >= 3


def update_env_password(new_password: str):
    """Update .env file with new password"""
    try:
        env_path = '/mnt/c/Users/tango/Desktop/Homepage/qr-info-portal/.env'
        
        # Read current .env content
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update ADMIN_PASSWORD line
        for i, line in enumerate(lines):
            if line.startswith('ADMIN_PASSWORD='):
                lines[i] = f'ADMIN_PASSWORD={new_password}\n'
                break
        else:
            # Add ADMIN_PASSWORD if not found
            lines.append(f'ADMIN_PASSWORD={new_password}\n')
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(lines)
            
        # Update current environment
        os.environ['ADMIN_PASSWORD'] = new_password
        
    except Exception as e:
        logger.error(f"Error updating .env file: {e}")
        raise


@admin_bp.route('/validate-translations')
@auth.login_required
def validate_translations():
    """Validate translation files for completeness and issues."""
    validator = TranslationValidator()
    results = validator.validate_all()
    suggestions = validator.get_fix_suggestions()
    
    return render_admin_template('admin/validate_translations.html',
                         results=results,
                         suggestions=suggestions)


@admin_bp.route('/api/validate-translations')
@auth.login_required
def api_validate_translations():
    """API endpoint for translation validation."""
    validator = TranslationValidator()
    results = validator.validate_all()
    
    return jsonify({
        'status': 'success',
        'data': results,
        'timestamp': datetime.now().isoformat()
    })


# Analytics Routes
@admin_bp.route('/analytics')
@auth.login_required
def analytics_dashboard():
    """Analytics dashboard showing visitor statistics"""
    return render_admin_template('admin/analytics.html')


@admin_bp.route('/api/analytics/summary')
@auth.login_required 
def api_analytics_summary():
    """Get analytics summary statistics"""
    try:
        days = int(request.args.get('days', 30))
        summary = analytics_service.get_summary_stats(days)
        
        # Get additional breakdowns
        with Session(engine) as db:
            from app.models import VisitorAnalytics
            from sqlmodel import func
            
            start_date = date.today() - timedelta(days=days)
            
            # Device stats
            device_stats = db.exec(
                select(
                    VisitorAnalytics.device_type,
                    func.count(VisitorAnalytics.id).label('count')
                )
                .where(VisitorAnalytics.visit_date >= start_date)
                .where(VisitorAnalytics.analytics_consent == True)
                .group_by(VisitorAnalytics.device_type)
            ).all()
            
            # Language stats  
            language_stats = db.exec(
                select(
                    VisitorAnalytics.preferred_language,
                    func.count(VisitorAnalytics.id).label('count')
                )
                .where(VisitorAnalytics.visit_date >= start_date)
                .where(VisitorAnalytics.analytics_consent == True)
                .group_by(VisitorAnalytics.preferred_language)
            ).all()
        
        device_breakdown = {row.device_type or 'unknown': row.count for row in device_stats}
        language_breakdown = {row.preferred_language: row.count for row in language_stats}
        
        return jsonify({
            'success': True,
            'stats': summary,
            'device_stats': device_breakdown,
            'language_stats': language_breakdown
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/api/geocode', methods=['POST'])
@auth.login_required
def api_geocode():
    """Geocode address to coordinates"""
    try:
        data = request.get_json()
        if not data or 'address' not in data:
            return jsonify({
                'success': False,
                'error': 'Address is required'
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({
                'success': False,
                'error': 'Address cannot be empty'
            }), 400
        
        # Get coordinates from geocoding service
        coordinates = geocoding_service.get_coordinates_from_address(address, "Thailand")
        
        if coordinates:
            lat, lng = coordinates
            return jsonify({
                'success': True,
                'coordinates': {
                    'latitude': lat,
                    'longitude': lng
                },
                'maps_link': geocoding_service.generate_maps_link(lat, lng, "Labor Pattaya"),
                'geocoding_source': 'OpenStreetMap'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Address could not be geocoded. Please check the address or try a different format.'
            }), 404
            
    except Exception as e:
        logger.error(f"Geocoding API error: {e}")
        return jsonify({
            'success': False,
            'error': f'Geocoding service error: {str(e)}'
        }), 500


@admin_bp.route('/api/analytics/daily')
@auth.login_required
def api_analytics_daily():
    """Get daily analytics statistics"""
    try:
        days = int(request.args.get('days', 14))
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        daily_stats = analytics_service.get_daily_stats(start_date, end_date)
        
        return jsonify({
            'success': True,
            'stats': daily_stats,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/api/analytics/popular-times')
@auth.login_required
def api_analytics_popular_times():
    """Get popular visit times analytics"""
    try:
        days = int(request.args.get('days', 7))
        popular_times = analytics_service.get_popular_times(days)
        
        return jsonify({
            'success': True,
            'stats': popular_times
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/api/analytics/recent-activity')
@auth.login_required
def api_analytics_recent_activity():
    """Get recent visitor activity"""
    try:
        limit = int(request.args.get('limit', 20))
        
        with Session(engine) as db:
            from app.models import VisitorAnalytics
            
            recent_activity = db.exec(
                select(VisitorAnalytics)
                .where(VisitorAnalytics.analytics_consent == True)
                .order_by(VisitorAnalytics.visit_time.desc())
                .limit(limit)
            ).all()
            
            activity_data = [
                {
                    'visit_time': activity.visit_time.isoformat(),
                    'page_path': activity.page_path,
                    'device_type': activity.device_type,
                    'preferred_language': activity.preferred_language,
                    'qr_code_scan': activity.qr_code_scan,
                    'qr_campaign': activity.qr_campaign,
                    'is_returning_visitor': activity.is_returning_visitor,
                    'referrer_type': activity.referrer_type
                }
                for activity in recent_activity
            ]
        
        return jsonify({
            'success': True,
            'activity': activity_data,
            'count': len(activity_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Server Management
@admin_bp.route('/api/server/restart', methods=['POST'])
@auth.login_required
@require_csrf
def api_server_restart():
    """Restart the Flask server"""
    try:
        import subprocess
        import sys
        
        # Log the restart action
        log_admin_action('server_restart', {
            'requested_by': auth.current_user(),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Schedule restart after response
        def restart_server():
            time.sleep(2)  # Give time for response to be sent
            # Kill current Flask process
            subprocess.run(['pkill', '-f', 'flask'], capture_output=True)
            subprocess.run(['pkill', '-f', 'python.*run.py'], capture_output=True)
            
            # Start new Flask process
            env = os.environ.copy()
            env['FLASK_APP'] = 'run.py'
            env['FLASK_ENV'] = 'development'
            subprocess.Popen([sys.executable, 'run.py'], env=env)
        
        # Start restart in background
        import threading
        threading.Thread(target=restart_server, daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': 'Server restart initiated. The page will reload in 5 seconds.'
        })
        
    except Exception as e:
        logger.error(f"Server restart error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


