from flask import Blueprint, jsonify, render_template, request, redirect, url_for, Response, send_file
from datetime import datetime, date, timedelta
from app.services import StatusService, ScheduleService, I18nService
from app.services.i18n import format_date, format_time, format_datetime, format_weekday, format_month_year, format_time_range
from app.services.qr import QRService
from app.services.social_media import SocialMediaService
from app.services.config_service import ConfigService
from app.services.kiosk_rotation import KioskRotationService
from app.services.analytics import analytics_service
from app.models import Announcement
from app.database import engine
from sqlmodel import Session, select
import yaml
import os
import io
from pathlib import Path

public_bp = Blueprint('public', __name__)


def _get_services_for_language(language: str) -> list:
    """Get services list for the specified language"""
    try:
        return ConfigService.get_services(language)
    except Exception as e:
        from app.logging_config import get_logger
        logger = get_logger('routes_public')
        logger.warning(f"Could not load services from config: {e}")
        # Fallback to hardcoded services
        return ['Blutabnahme', 'Vorgespräch', 'Nachgespräch', 'Befundausgabe']


def get_template_context():
    """Get common template context with i18n and date formatting functions"""
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return {
        'lang': I18nService.get_current_language(),
        'contact': config['contact'],
        'location': config['location'],
        'get_translation': I18nService.translate,
        't': I18nService.translate,
        'i18n': I18nService,
        # Date formatting functions
        'format_date': format_date,
        'format_time': format_time,
        'format_datetime': format_datetime,
        'format_weekday': format_weekday,
        'format_month_year': format_month_year,
        'format_time_range': format_time_range
    }

@public_bp.route('/healthz')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'qr-info-portal'
    }), 200

@public_bp.route('/')
def home():
    """Home page with today's status and hours"""
    
    # Analytics tracking (with consent check)
    analytics_consent = request.cookies.get('analytics_consent', 'false') == 'true'
    qr_campaign = request.args.get('qr', None)  # QR campaign tracking
    
    if analytics_consent:
        analytics_service.track_visit(
            request=request,
            page_path="/",
            qr_campaign=qr_campaign,
            analytics_consent=True
        )
    
    # Get current status
    status = StatusService.get_current_status()
    
    # Get today's hours
    today = datetime.now(ScheduleService.TIMEZONE).date()
    today_hours = ScheduleService.get_hours_for_date(today)
    
    # Get current language
    lang = I18nService.get_current_language()
    
    # Get announcements for current language with date filtering
    with Session(engine) as session:
        # Get active announcements that are currently valid (within date range)
        announcements = session.exec(
            select(Announcement).where(
                Announcement.active == True,
                (Announcement.start_date.is_(None)) | (Announcement.start_date <= today),
                (Announcement.end_date.is_(None)) | (Announcement.end_date >= today)
            ).order_by(Announcement.created_at.desc())
        ).all()
    
    # Get detailed opening status
    opening_status = ScheduleService.get_opening_status()
    
    # Load config for contact info and social media
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Get social media platforms
    social_service = SocialMediaService()
    social_platforms = social_service.get_platforms_for_display()
    
    # Get week schedule for quick view
    week_start = today - timedelta(days=today.weekday())
    week_hours = {}
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        day_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][i]
        hours = ScheduleService.get_hours_for_date(day_date)
        if not hours['closed']:
            week_hours[day_name] = hours['time_ranges']
        else:
            week_hours[day_name] = []
    
    # Get available time slots for today (if any)
    availability_today = []
    # This is indicative only - would be fetched from availability service
    
    # Determine which template to use based on language preference
    # Thai-first approach: always show Thai as primary with EN subtitles
    template_name = 'home_thai_first.html' if lang == 'th' else 'home.html'
    
    # Get base template context and extend it
    context = get_template_context()
    context.update({
        'status': status,
        'today': today,
        'today_hours': today_hours,
        'opening_status': opening_status,
        'week_hours': week_hours,
        'availability_today': availability_today,
        'services': _get_services_for_language(I18nService.get_current_language()),
        'announcements': announcements,
        'social_platforms': social_platforms
    })
    
    return render_template(template_name, **context)

@public_bp.route('/week')
def week_view():
    """Week view of opening hours"""
    # Get week parameter
    week_offset = request.args.get('offset', 0, type=int)
    start_date = datetime.now(ScheduleService.TIMEZONE).date()
    
    # Apply offset (weeks)
    from datetime import timedelta
    if week_offset != 0:
        start_date += timedelta(weeks=week_offset)
    
    # Get week schedule
    week_schedule = ScheduleService.get_week_schedule(start_date)
    
    # Get status
    status = StatusService.get_current_status()
    
    # Get current language
    lang = I18nService.get_current_language()
    
    # Use Thai-first template for Thai language
    template_name = 'week_thai_first.html' if lang == 'th' else 'week.html'
    
    # Get config for contact/location info needed by base template
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return render_template(template_name,
        week_schedule=week_schedule,
        week_offset=week_offset,
        status=status,
        today=datetime.now(ScheduleService.TIMEZONE).date(),
        lang=lang,
        contact=config['contact'],
        location=config['location'],
        get_translation=I18nService.translate,
        t=I18nService.translate,
        i18n=I18nService
    )

@public_bp.route('/month')
def month_view():
    """Month view of opening hours"""
    # Get month/year parameters
    now = datetime.now(ScheduleService.TIMEZONE)
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)
    
    # Get month schedule
    month_schedule = ScheduleService.get_month_schedule(year, month)
    
    # Get status
    status = StatusService.get_current_status()
    
    # Calculate prev/next month
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    # Get current language and config for template
    lang = I18nService.get_current_language()
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return render_template('month.html',
        month_schedule=month_schedule,
        year=year,
        month=month,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        status=status,
        today=datetime.now(ScheduleService.TIMEZONE).date(),
        lang=lang,
        contact=config['contact'],
        location=config['location'],
        get_translation=I18nService.translate,
        t=I18nService.translate,
        i18n=I18nService
    )

@public_bp.route('/set-language/<language>')
def set_language(language):
    """Set user language preference"""
    I18nService.set_language(language)
    # Redirect to referrer or home
    return redirect(request.referrer or url_for('public.home'))

@public_bp.route('/qr')
def qr_png():
    """Generate QR code as PNG"""
    # Get target URL from params or use site URL
    target = request.args.get('target', os.getenv('SITE_URL', request.url_root))
    size = request.args.get('size', 300, type=int)
    
    # Generate PNG file
    filename = QRService.generate_qr_png(target, size=size)
    # Fix: Remove duplicate 'app' in path
    file_path = os.path.join('static/qr', filename)
    
    # Use absolute path from app directory
    abs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', file_path)
    return send_file(abs_path, mimetype='image/png')

@public_bp.route('/qr.svg')
def qr_svg():
    """Generate QR code as SVG"""
    # Get target URL from params or use site URL
    target = request.args.get('target', os.getenv('SITE_URL', request.url_root))
    
    # Generate SVG
    svg_data = QRService.generate_qr_svg(target)
    
    return Response(svg_data, mimetype='image/svg+xml')

@public_bp.route('/social')
def social_media():
    """Social media overview page"""
    social_service = SocialMediaService()
    platforms = social_service.get_platforms_for_display()
    
    # Load config
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return render_template('social_media.html',
        platforms=platforms,
        config=config
    )

@public_bp.route('/social/qr/<platform>')
def social_qr(platform):
    """Generate QR code for specific social media platform"""
    social_service = SocialMediaService()
    size = request.args.get('size', 'medium')
    
    # Check if platform is enabled
    platform_config = social_service.get_platform_config(platform)
    if not platform_config.get('enabled', False) or not platform_config.get('qr_enabled', False):
        return jsonify({'error': 'Platform not available'}), 404
    
    # Generate QR code
    filename = social_service.generate_platform_qr(platform, size)
    if not filename:
        return jsonify({'error': 'Could not generate QR code'}), 500
    
    # Fix: Use correct path
    file_path = os.path.join('static/qr', filename)
    abs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', file_path)
    return send_file(abs_path, mimetype='image/png')

@public_bp.route('/social/share')
def social_share():
    """Generate share URLs for content"""
    content = request.args.get('content', 'Check out our laboratory!')
    url = request.args.get('url', request.url_root)
    platform = request.args.get('platform', '')
    
    social_service = SocialMediaService()
    
    if platform:
        share_url = social_service.get_share_url(platform, content, url)
        return redirect(share_url)
    
    # Return share options
    platforms = social_service.get_enabled_platforms()
    share_urls = {}
    
    for p in platforms:
        share_urls[p] = social_service.get_share_url(p, content, url)
    
    return jsonify(share_urls)

@public_bp.route('/social/qr-batch')
def social_qr_batch():
    """Generate all social media QR codes"""
    social_service = SocialMediaService()
    size = request.args.get('size', 'medium')
    
    # Get all platforms configuration
    config = social_service.config
    platforms_data = config.get('platforms', {})
    
    # Generate QR codes
    qr_results = QRService.generate_social_media_qr_batch(platforms_data, size)
    
    return jsonify({
        'success': True,
        'generated': len(qr_results),
        'files': qr_results
    })

@public_bp.route('/kiosk/single')
def kiosk_single():
    """Single kiosk view - full screen with today's info"""
    # Get current status and hours
    status = StatusService.get_current_status()
    today = datetime.now(ScheduleService.TIMEZONE).date()
    today_hours_data = ScheduleService.get_hours_for_date(today)
    
    # Extract time_ranges from the dict for template compatibility
    today_hours = today_hours_data.get('time_ranges', []) if today_hours_data else []
    
    opening_status = ScheduleService.get_opening_status()
    
    # Load config
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Get current language for kiosk
    lang = I18nService.get_current_language()
    
    return render_template('kiosk/single_redesigned.html',
        status=status,
        today_hours=today_hours,
        opening_status=opening_status,
        config=config,
        today=today,
        now=datetime.now(ScheduleService.TIMEZONE),
        lang=lang,
        get_translation=I18nService.translate,
        t=I18nService.translate,
        i18n=I18nService
    )

@public_bp.route('/kiosk/triple')
def kiosk_triple():
    """Triple kiosk view - 3 column layout with AJAX support"""
    # Get current status
    status = StatusService.get_current_status()
    today = datetime.now(ScheduleService.TIMEZONE).date()
    
    # Get today's hours
    today_hours = ScheduleService.get_hours_for_date(today)
    opening_status = ScheduleService.get_opening_status()
    
    # Get week schedule
    week_schedule = ScheduleService.get_week_schedule(today)
    
    # Get preview (next 3-4 weeks)
    preview_weeks = []
    for i in range(1, 4):
        week_start = today + timedelta(weeks=i)
        preview_weeks.append({
            'week_num': i,
            'schedule': ScheduleService.get_week_schedule(week_start)
        })
    
    # Load config
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Get current language for kiosk
    lang = I18nService.get_current_language()
    
    context = {
        'status': status,
        'today_hours': today_hours,
        'opening_status': opening_status,
        'week_schedule': week_schedule,
        'preview_weeks': preview_weeks,
        'config': config,
        'today': today,
        'now': datetime.now(ScheduleService.TIMEZONE),
        'lang': lang,
        'get_translation': I18nService.translate,
        't': I18nService.translate,
        'i18n': I18nService,
        'weekly_hours': week_schedule,
        'announcements': []
    }
    
    return render_template('kiosk/triple_modern.html', **context)

@public_bp.route('/kiosk/ultimate')
def kiosk_ultimate():
    """Ultimate kiosk view - optimized for large displays with enhanced features"""
    # Get current status
    status = StatusService.get_current_status()
    today = datetime.now(ScheduleService.TIMEZONE).date()
    today_hours = ScheduleService.get_hours_for_date(today)
    
    # Get detailed opening status
    opening_status = ScheduleService.get_opening_status()
    
    # Get announcements for current language
    lang = I18nService.get_current_language()
    with Session(engine) as session:
        announcements = session.exec(
            select(Announcement).where(
                Announcement.lang == lang,
                Announcement.active == True
            ).order_by(Announcement.created_at.desc()).limit(3)
        ).all()
    
    # Load config
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return render_template('kiosk/ultimate.html',
        status=status,
        today_hours=today_hours,
        opening_status=opening_status,
        announcements=announcements,
        config=config,
        today=today,
        now=datetime.now(ScheduleService.TIMEZONE),
        lang=I18nService.get_current_language(),
        get_translation=I18nService.translate,
        t=I18nService.translate,
        i18n=I18nService
    )

@public_bp.route('/kiosk/rotation')
def kiosk_rotation():
    """Advanced Kiosk Rotation System - Thailand Edition"""
    try:
        # Get current status and schedule info for template
        status = StatusService.get_current_status()
        today = datetime.now(ScheduleService.TIMEZONE).date()
        today_hours = ScheduleService.get_hours_for_date(today)
        
        # Get week schedule for the rotation
        week_schedule = {}
        week_start = today - timedelta(days=today.weekday())
        for i in range(7):
            day_date = week_start + timedelta(days=i)
            day_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][i]
            hours = ScheduleService.get_hours_for_date(day_date)
            if not hours.get('closed', True):
                week_schedule[day_name] = hours.get('time_ranges', [])
            else:
                week_schedule[day_name] = []
        
        # Calculate next opening if currently closed
        next_opening_thai = "สัปดาห์หน้า"  # Placeholder 
        next_opening_en = "Next week"     # Placeholder
        
        # Load config for contact info
        with open('config.yml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Get current language
        lang = I18nService.get_current_language()
        
        return render_template('kiosk/rotation_system.html',
            status=status,
            today_hours=today_hours,
            week_schedule=week_schedule,
            next_opening_thai=next_opening_thai,
            next_opening_en=next_opening_en,
            config=config,
            today=today,
            now=datetime.now(ScheduleService.TIMEZONE),
            lang=lang,
            get_translation=I18nService.translate,
            t=I18nService.translate,
            i18n=I18nService
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

@public_bp.route('/kiosk/triple_modern')
def kiosk_triple_modern():
    """Modern triple kiosk view with fixed banner layout"""
    # Get current status
    status = StatusService.get_current_status()
    today = datetime.now(ScheduleService.TIMEZONE).date()
    
    # Get today's hours
    today_hours = ScheduleService.get_hours_for_date(today)
    opening_status = ScheduleService.get_opening_status()
    
    # Get week schedule
    week_schedule = ScheduleService.get_week_schedule(today)
    
    # Get preview (next 3-4 weeks)
    preview_weeks = []
    for i in range(1, 4):
        week_start = today + timedelta(weeks=i)
        preview_weeks.append({
            'week_num': i,
            'schedule': ScheduleService.get_week_schedule(week_start)
        })
    
    # Load config
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Get current language for kiosk
    lang = I18nService.get_current_language()
    
    return render_template('kiosk/triple_modern.html',
        status=status,
        today_hours=today_hours,
        opening_status=opening_status,
        week_schedule=week_schedule,
        preview_weeks=preview_weeks,
        config=config,
        today=today,
        now=datetime.now(ScheduleService.TIMEZONE),
        lang=lang,
        get_translation=I18nService.translate,
        t=I18nService.translate,
        i18n=I18nService
    )

@public_bp.route('/home_modern')
def home_modern():
    """Modern home page with updated design"""
    # Get current status
    status = StatusService.get_current_status()
    
    # Get today's hours
    today = datetime.now(ScheduleService.TIMEZONE).date()
    today_hours = ScheduleService.get_hours_for_date(today)
    
    # Get current language
    lang = I18nService.get_current_language()
    
    # Get announcements for current language with date filtering
    with Session(engine) as session:
        # Get active announcements that are currently valid (within date range)
        announcements = session.exec(
            select(Announcement).where(
                Announcement.active == True,
                (Announcement.start_date.is_(None)) | (Announcement.start_date <= today),
                (Announcement.end_date.is_(None)) | (Announcement.end_date >= today)
            ).order_by(Announcement.created_at.desc())
        ).all()
    
    # Get detailed opening status
    opening_status = ScheduleService.get_opening_status()
    
    # Load config for contact info and social media
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Get social media platforms
    social_service = SocialMediaService()
    social_platforms = social_service.get_platforms_for_display()
    
    # Get week schedule for quick view
    week_start = today - timedelta(days=today.weekday())
    week_hours = {}
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        day_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][i]
        hours = ScheduleService.get_hours_for_date(day_date)
        if not hours['closed']:
            week_hours[day_name] = hours['time_ranges']
        else:
            week_hours[day_name] = []
    
    return render_template('home_modern.html',
        status=status,
        today=today,
        today_hours=today_hours,
        opening_status=opening_status,
        week_hours=week_hours,
        availability_today=[],
        services=['Blutabnahme', 'Vorgespräch', 'Nachgespräch', 'Befundausgabe'],
        announcements=announcements,
        lang=lang,
        contact=config['contact'],
        location=config['location'],
        social_platforms=social_platforms,
        get_translation=I18nService.translate,
        t=I18nService.translate,
        i18n=I18nService
    )


# Route to serve admin translation files for JavaScript i18n
@public_bp.route('/admin_translations_<language>.json')
def serve_admin_translations(language):
    """Serve admin translation files for JavaScript i18n system"""
    import logging
    logger = logging.getLogger(__name__)
    
    if language not in ['de', 'en', 'th']:
        return jsonify({'error': 'Unsupported language'}), 404
    
    try:
        # Load from app/translations directory and extract admin section
        from app.services.i18n import I18nService
        
        # Make sure translations are loaded
        if not I18nService.translations:
            I18nService.load_translations()
        
        # Get full translations and extract admin section only
        full_translations = I18nService.translations.get(language, {})
        admin_translations = full_translations.get('admin', {})
        
        if not admin_translations:
            logger.warning(f"No admin translations found for language: {language}")
            admin_translations = {}
        
        # Return as JSON directly instead of serving file
        response = jsonify(admin_translations)
        response.headers['Cache-Control'] = 'public, max-age=3600'
        response.headers['Access-Control-Allow-Origin'] = '*'
        
        return response
        
    except Exception as e:
        logger.error(f"Error serving admin translation file for {language}: {e}")
        return jsonify({'error': 'Internal server error'}), 500