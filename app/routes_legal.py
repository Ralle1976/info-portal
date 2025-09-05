"""
Legal Compliance Routes - Public and Admin
Handles privacy policy, terms, consent management, and data subject requests
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime, date, timedelta
import json
import os
from typing import Dict, Any

from .services.legal_compliance import legal_service
from .services.legal_labels import legal_labels
from .services.i18n import I18nService
from .models import LegalDocument, DataSubjectRequest, CookieConsent, DataProcessingPurpose
from .database import get_session, db_session_context
from sqlmodel import select

# Create blueprints
legal_bp = Blueprint('legal', __name__, url_prefix='/legal')
legal_admin_bp = Blueprint('legal_admin', __name__, url_prefix='/admin/legal')


def admin_required(f):
    """Decorator to require admin authentication for legal admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Basic auth check - in production, use proper authentication
        auth = request.authorization
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if not auth or auth.username != admin_username or auth.password != admin_password:
            return jsonify({'error': 'Authentication required'}), 401, {
                'WWW-Authenticate': 'Basic realm="Legal Admin Area"'
            }
        return f(*args, **kwargs)
    return decorated_function


# === PUBLIC LEGAL ROUTES ===

@legal_bp.route('/privacy')
def privacy_policy():
    """Display privacy policy"""
    lang = request.args.get('lang', 'th')
    version = request.args.get('version')  # Optional specific version
    
    document = legal_service.get_legal_document('privacy_policy', lang, version)
    
    if not document:
        # Fallback to default language
        document = legal_service.get_legal_document('privacy_policy', 'th', version)
    
    if not document:
        flash(I18nService.translate('legal.privacy_not_available', lang), 'error')
        return redirect(url_for('public.home'))
    
    # Log access for compliance
    legal_service.log_compliance_event(
        log_type="legal_document",
        action="privacy_policy_accessed",
        details={"language": lang, "version": document.version},
        session_id_hash=legal_service._hash_identifier(session.get('legal_session_id', '')),
        compliance_frameworks=["PDPA", "GDPR"]
    )
    
    return render_template('legal/privacy_policy.html', 
                         document=document, 
                         language=lang)


@legal_bp.route('/terms')
def terms_of_service():
    """Display terms of service"""
    lang = request.args.get('lang', 'th')
    version = request.args.get('version')
    
    document = legal_service.get_legal_document('terms', lang, version)
    
    if not document:
        document = legal_service.get_legal_document('terms', 'th', version)
    
    if not document:
        flash(I18nService.translate('legal.terms_not_available', lang), 'error')
        return redirect(url_for('public.home'))
    
    legal_service.log_compliance_event(
        log_type="legal_document",
        action="terms_accessed",
        details={"language": lang, "version": document.version},
        session_id_hash=legal_service._hash_identifier(session.get('legal_session_id', '')),
        compliance_frameworks=["PDPA", "GDPR"]
    )
    
    return render_template('legal/terms.html', 
                         document=document, 
                         language=lang)


@legal_bp.route('/impressum')
def impressum():
    """Display impressum/legal notice"""
    lang = request.args.get('lang', 'th')
    
    document = legal_service.get_legal_document('impressum', lang)
    
    if not document:
        document = legal_service.get_legal_document('impressum', 'th')
    
    if not document:
        flash(I18nService.translate('legal.impressum_not_available', lang), 'error')
        return redirect(url_for('public.home'))
    
    return render_template('legal/impressum.html', 
                         document=document, 
                         language=lang)


@legal_bp.route('/medical-disclaimer')
def medical_disclaimer():
    """Display medical disclaimer for laboratory services"""
    lang = request.args.get('lang', 'th')
    
    document = legal_service.get_legal_document('medical_disclaimer', lang)
    
    if not document:
        document = legal_service.get_legal_document('medical_disclaimer', 'th')
    
    if not document:
        flash(I18nService.translate('legal.medical_disclaimer_not_available', lang), 'error')
        return redirect(url_for('public.home'))
    
    return render_template('legal/medical_disclaimer.html', 
                         document=document, 
                         language=lang)


# === CONSENT MANAGEMENT ===

@legal_bp.route('/consent', methods=['GET'])
def consent_settings():
    """Display consent management page"""
    lang = request.args.get('lang', 'th')
    
    # Get current consent status
    current_consent = legal_service.get_user_consent(request)
    
    # Get data processing purposes for display
    session = get_session()
    try:
        db_session = session
        purposes = db_session.exec(
            select(DataProcessingPurpose).where(DataProcessingPurpose.is_active == True)
        ).all()
    except Exception as e:
        print(f"Error loading purposes: {e}")
        purposes = []
    
    return render_template('legal/consent_settings.html',
                         current_consent=current_consent,
                         purposes=purposes,
                         language=lang)


@legal_bp.route('/consent', methods=['POST'])
def update_consent():
    """Update user consent preferences"""
    try:
        data = request.get_json() or request.form.to_dict()
        
        consent_data = {
            'functional': data.get('functional') == 'true' or data.get('functional') is True,
            'analytics': data.get('analytics') == 'true' or data.get('analytics') is True,
            'marketing': data.get('marketing') == 'true' or data.get('marketing') is True,
            'medical_disclaimer': data.get('medical_disclaimer') == 'true' or data.get('medical_disclaimer') is True,
            'language': data.get('language', 'th'),
            'source': 'settings',
            'version': '1.0'
        }
        
        success = legal_service.record_consent(request, consent_data)
        
        if success:
            if request.is_json:
                return jsonify({'success': True, 'message': 'Consent updated successfully'})
            else:
                flash(I18nService.translate('legal.consent_updated', consent_data['language']), 'success')
                return redirect(url_for('legal.consent_settings'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Failed to update consent'}), 500
            else:
                flash(I18nService.translate('legal.consent_update_failed', consent_data['language']), 'error')
                return redirect(url_for('legal.consent_settings'))
                
    except Exception as e:
        legal_service.log_compliance_event(
            log_type="consent",
            action="consent_update_error",
            details={"error": str(e)},
            severity="critical"
        )
        
        if request.is_json:
            return jsonify({'success': False, 'error': 'Internal error'}), 500
        else:
            flash(I18nService.translate('legal.consent_update_failed', 'th'), 'error')
            return redirect(url_for('legal.consent_settings'))


@legal_bp.route('/consent/withdraw', methods=['POST'])
def withdraw_consent():
    """Withdraw consent (GDPR Art. 7(3), PDPA rights)"""
    try:
        data = request.get_json() or request.form.to_dict()
        consent_types = data.get('types', [])
        
        if isinstance(consent_types, str):
            consent_types = [consent_types]
        
        success = legal_service.withdraw_consent(request, consent_types)
        
        if success:
            if request.is_json:
                return jsonify({'success': True, 'message': 'Consent withdrawn successfully'})
            else:
                flash(I18nService.translate('legal.consent_withdrawn', 'th'), 'success')
                return redirect(url_for('legal.consent_settings'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Failed to withdraw consent'}), 500
            else:
                flash(I18nService.translate('legal.consent_withdrawal_failed', 'th'), 'error')
                return redirect(url_for('legal.consent_settings'))
                
    except Exception as e:
        legal_service.log_compliance_event(
            log_type="consent",
            action="consent_withdrawal_error",
            details={"error": str(e)},
            severity="critical"
        )
        
        if request.is_json:
            return jsonify({'success': False, 'error': 'Internal error'}), 500
        else:
            flash(I18nService.translate('legal.consent_withdrawal_failed', 'th'), 'error')
            return redirect(url_for('legal.consent_settings'))


# === DATA SUBJECT REQUESTS ===

@legal_bp.route('/data-request', methods=['GET'])
def data_request_form():
    """Display data subject request form"""
    lang = request.args.get('lang', 'th')
    
    return render_template('legal/data_request.html', language=lang)


@legal_bp.route('/data-request', methods=['POST'])
def submit_data_request():
    """Submit data subject request (GDPR Art. 15-20, PDPA rights)"""
    try:
        data = request.form.to_dict()
        
        request_type = data.get('request_type')  # access, rectification, erasure, portability, objection
        email = data.get('email', '').strip()
        details = data.get('details', '').strip()
        language = data.get('language', 'th')
        
        # Validation
        if not request_type or not email or not details:
            flash(I18nService.translate('legal.data_request_incomplete', language), 'error')
            return redirect(url_for('legal.data_request_form'))
        
        # Create request
        verification_code = legal_service.create_data_subject_request(
            request_type=request_type,
            email=email,
            details=details,
            language=language
        )
        
        if verification_code:
            flash(I18nService.translate('legal.data_request_submitted', language), 'success')
            return render_template('legal/data_request_confirmation.html', 
                                 email=email, 
                                 language=language)
        else:
            flash(I18nService.translate('legal.data_request_failed', language), 'error')
            return redirect(url_for('legal.data_request_form'))
            
    except Exception as e:
        legal_service.log_compliance_event(
            log_type="data_request",
            action="submission_error",
            details={"error": str(e)},
            severity="critical"
        )
        
        flash(I18nService.translate('legal.data_request_failed', 'th'), 'error')
        return redirect(url_for('legal.data_request_form'))


@legal_bp.route('/data-request/verify/<verification_code>')
def verify_data_request(verification_code):
    """Verify data subject request via email link"""
    success = legal_service.verify_data_subject_request(verification_code)
    
    lang = request.args.get('lang', 'th')
    
    if success:
        message = I18nService.translate('legal.data_request_verified', lang)
        return render_template('legal/verification_result.html', 
                             success=True, 
                             message=message, 
                             language=lang)
    else:
        message = I18nService.translate('legal.data_request_verification_failed', lang)
        return render_template('legal/verification_result.html', 
                             success=False, 
                             message=message, 
                             language=lang)


# === COOKIE BANNER API ===

@legal_bp.route('/cookie-banner-info')
def cookie_banner_info():
    """API endpoint for cookie banner information"""
    lang = request.args.get('lang', 'th')
    
    # Check if user already has valid consent
    current_consent = legal_service.get_user_consent(request)
    
    if current_consent:
        return jsonify({
            'show_banner': False,
            'current_consent': current_consent
        })
    
    # Get data processing purposes for banner display
    session = get_session()
    try:
        db_session = session
        purposes = db_session.exec(
            select(DataProcessingPurpose).where(
                DataProcessingPurpose.is_active == True,
                DataProcessingPurpose.requires_explicit_consent == True
            )
        ).all()
    except Exception as e:
        print(f"Error loading purposes for banner: {e}")
        purposes = []
    
    purpose_info = []
    for purpose in purposes:
        purpose_info.append({
            'code': purpose.purpose_code,
            'name': purpose.purpose_name.get(lang, purpose.purpose_name.get('th', '')),
            'description': purpose.description.get(lang, purpose.description.get('th', '')),
            'required': not purpose.requires_explicit_consent
        })
    
    return jsonify({
        'show_banner': True,
        'purposes': purpose_info,
        'privacy_policy_url': url_for('legal.privacy_policy', lang=lang),
        'language': lang
    })


# === LEGAL ADMIN ROUTES ===

@legal_admin_bp.route('/')
@admin_required
def legal_dashboard():
    """Legal compliance admin dashboard"""
    # Get compliance status
    compliance_status = legal_service.check_compliance_status()
    
    # Get recent compliance logs
    session = get_session()
    try:
        db_session = session
        recent_logs = db_session.exec(
            select(legal_service.ComplianceLog)
            .order_by(legal_service.ComplianceLog.created_at.desc())
            .limit(20)
        ).all()
        
        # Get pending data requests
        pending_requests = db_session.exec(
            select(DataSubjectRequest)
            .where(DataSubjectRequest.status.in_(['pending', 'verified', 'processing']))
            .order_by(DataSubjectRequest.created_at.desc())
        ).all()
    except Exception as e:
        print(f"Error loading legal dashboard data: {e}")
        recent_logs = []
        pending_requests = []
    
    return render_template('admin/legal/dashboard.html',
                         compliance_status=compliance_status,
                         recent_logs=recent_logs,
                         pending_requests=pending_requests)


@legal_admin_bp.route('/documents')
@admin_required
def manage_documents():
    """Manage legal documents"""
    with db_session_context() as db_session:
        documents = db_session.exec(
            select(LegalDocument).order_by(
                LegalDocument.document_type,
                LegalDocument.language,
                LegalDocument.version.desc()
            )
        ).all()
    
    return render_template('admin/legal/documents.html', documents=documents)


@legal_admin_bp.route('/documents/create', methods=['GET', 'POST'])
@admin_required
def create_document():
    """Create new legal document"""
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            
            document = LegalDocument(
                document_type=data['document_type'],
                language=data['language'],
                version=data['version'],
                title=data['title'],
                content=data['content'],
                effective_date=datetime.strptime(data['effective_date'], '%Y-%m-%d').date(),
                requires_consent=data.get('requires_consent') == 'on',
                created_by=request.authorization.username if request.authorization else 'admin'
            )
            
            session = get_session()
            try:
                db_session = session
                db_session.add(document)
                db_session.commit()
                
                legal_service.log_compliance_event(
                    log_type="legal_document",
                    action="document_created",
                    details={
                        "document_type": data['document_type'],
                        "language": data['language'],
                        "version": data['version']
                    },
                    compliance_frameworks=["PDPA", "GDPR"]
                )
                
                flash('Legal document created successfully', 'success')
                return redirect(url_for('legal_admin.manage_documents'))
            except Exception as db_error:
                flash(f'Database error: {str(db_error)}', 'error')
            
        except Exception as e:
            legal_service.log_compliance_event(
                log_type="legal_document",
                action="document_creation_error",
                details={"error": str(e)},
                severity="critical"
            )
            flash(f'Error creating document: {str(e)}', 'error')
    
    return render_template('admin/legal/create_document.html')


@legal_admin_bp.route('/data-requests')
@admin_required
def manage_data_requests():
    """Manage data subject requests"""
    session = get_session()
    try:
        db_session = session
        requests = db_session.exec(
            select(DataSubjectRequest).order_by(DataSubjectRequest.created_at.desc())
        ).all()
        
        return render_template('admin/legal/data_requests.html', requests=requests)
    except Exception as e:
        print(f"Error loading data requests: {e}")
        return render_template('admin/legal/data_requests.html', requests=[])


@legal_admin_bp.route('/data-requests/<int:request_id>/process', methods=['POST'])
@admin_required
def process_data_request(request_id):
    """Process data subject request"""
    try:
        session = get_session()
        try:
            db_session = session
            data_request = db_session.get(DataSubjectRequest, request_id)
            
            if not data_request:
                return jsonify({'error': 'Request not found'}), 404
            
            action = request.form.get('action')  # approve, reject
            response_text = request.form.get('response_text', '')
            
            if action == 'approve':
                data_request.status = 'completed'
                # For data export requests, generate export
                if data_request.request_type == 'portability':
                    export_data = legal_service.export_user_data(data_request.session_id_hash)
                    data_request.data_export = export_data
            else:
                data_request.status = 'rejected'
            
            data_request.response_text = response_text
            data_request.response_sent_at = datetime.utcnow()
            data_request.processed_by = request.authorization.username if request.authorization else 'admin'
            
            db_session.commit()
            
            legal_service.log_compliance_event(
                log_type="data_request",
                action=f"request_{action}",
                details={
                    "request_id": request_id,
                    "request_type": data_request.request_type,
                    "processed_by": data_request.processed_by
                },
                compliance_frameworks=["PDPA", "GDPR"]
            )
            
            flash(f'Data request {action} successfully', 'success')
            return redirect(url_for('legal_admin.manage_data_requests'))
        except Exception as db_error:
            flash(f'Database error: {str(db_error)}', 'error')
            return redirect(url_for('legal_admin.manage_data_requests'))
            
    except Exception as e:
        legal_service.log_compliance_event(
            log_type="data_request",
            action="processing_error",
            details={"error": str(e), "request_id": request_id},
            severity="critical"
        )
        flash(f'Error processing request: {str(e)}', 'error')
        return redirect(url_for('legal_admin.manage_data_requests'))


@legal_admin_bp.route('/compliance-logs')
@admin_required
def view_compliance_logs():
    """View compliance audit logs"""
    page = request.args.get('page', 1, type=int)
    log_type = request.args.get('type', '')
    
    session = get_session()
    try:
        db_session = session
        query = select(legal_service.ComplianceLog).order_by(
            legal_service.ComplianceLog.created_at.desc()
        )
        
        if log_type:
            query = query.where(legal_service.ComplianceLog.log_type == log_type)
        
        # Simple pagination (in production, use proper pagination)
        logs = db_session.exec(query.limit(100).offset((page - 1) * 100)).all()
        
        return render_template('admin/legal/compliance_logs.html', 
                             logs=logs, 
                             current_page=page,
                             log_type=log_type)
    except Exception as e:
        print(f"Error loading compliance logs: {e}")
        return render_template('admin/legal/compliance_logs.html', 
                             logs=[], 
                             current_page=page,
                             log_type=log_type)


@legal_admin_bp.route('/cleanup-data', methods=['POST'])
@admin_required
def cleanup_expired_data():
    """Manually trigger data cleanup"""
    try:
        cleanup_stats = legal_service.cleanup_expired_data()
        
        flash(f'Data cleanup completed: {cleanup_stats}', 'success')
        
    except Exception as e:
        legal_service.log_compliance_event(
            log_type="cleanup",
            action="manual_cleanup_error",
            details={"error": str(e)},
            severity="critical"
        )
        flash(f'Error during cleanup: {str(e)}', 'error')
    
    return redirect(url_for('legal_admin.legal_dashboard'))


# === LEGAL LABELS MANAGEMENT ===

@legal_admin_bp.route('/settings')
@admin_required
def legal_settings():
    """Legal compliance settings page with configurable labels"""
    return render_template('admin/legal/settings.html')


@legal_admin_bp.route('/get-configs')
@admin_required
def get_legal_configs():
    """Get all legal configurations for all languages"""
    try:
        configs = {}
        for language in legal_labels.get_all_languages():
            configs[language] = legal_labels.get_legal_config(language)
        
        return jsonify(configs)
        
    except Exception as e:
        legal_service.log_compliance_event(
            log_type="settings",
            action="config_retrieval_error",
            details={"error": str(e)},
            severity="warning"
        )
        return jsonify({"error": "Failed to load configurations"}), 500


@legal_admin_bp.route('/save-config', methods=['POST'])
@admin_required
def save_legal_config():
    """Save legal configuration for a specific language"""
    try:
        data = request.get_json()
        language = data.get('language')
        config = data.get('config')
        
        if not language or not config:
            return jsonify({"error": "Language and config required"}), 400
        
        # Validate configuration
        validation_errors = legal_labels.validate_config(config)
        if validation_errors:
            return jsonify({
                "error": "Configuration validation failed",
                "details": validation_errors
            }), 400
        
        success = legal_labels.update_legal_config(language, config)
        
        if success:
            legal_service.log_compliance_event(
                log_type="settings",
                action="config_updated",
                details={
                    "language": language,
                    "sections_updated": list(config.keys())
                },
                compliance_frameworks=["PDPA", "GDPR"]
            )
            
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Failed to save configuration"}), 500
            
    except Exception as e:
        legal_service.log_compliance_event(
            log_type="settings",
            action="config_save_error",
            details={"error": str(e)},
            severity="critical"
        )
        return jsonify({"error": "Internal server error"}), 500


@legal_admin_bp.route('/export-configs')
@admin_required
def export_legal_configs():
    """Export all legal configurations as JSON"""
    try:
        configs = {}
        for language in legal_labels.get_all_languages():
            configs[language] = legal_labels.export_config(language)
        
        # Add metadata
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "version": "1.0",
            "site_name": "Laboratory Pattaya Legal Configs",
            "configs": configs
        }
        
        legal_service.log_compliance_event(
            log_type="settings",
            action="config_exported",
            details={"languages": list(configs.keys())},
            compliance_frameworks=["PDPA", "GDPR"]
        )
        
        response = jsonify(export_data)
        response.headers['Content-Disposition'] = f'attachment; filename=legal-configs-{datetime.utcnow().strftime("%Y%m%d")}.json'
        return response
        
    except Exception as e:
        legal_service.log_compliance_event(
            log_type="settings",
            action="config_export_error",
            details={"error": str(e)},
            severity="warning"
        )
        return jsonify({"error": "Failed to export configurations"}), 500


@legal_admin_bp.route('/import-configs', methods=['POST'])
@admin_required
def import_legal_configs():
    """Import legal configurations from JSON"""
    try:
        data = request.get_json()
        
        if 'configs' not in data:
            return jsonify({"error": "Invalid import format"}), 400
        
        configs = data['configs']
        imported_languages = []
        errors = []
        
        for language, config in configs.items():
            if language not in legal_labels.get_all_languages():
                errors.append(f"Unsupported language: {language}")
                continue
            
            # Validate configuration
            validation_errors = legal_labels.validate_config(config)
            if validation_errors:
                errors.append(f"Validation errors for {language}: {validation_errors}")
                continue
            
            success = legal_labels.import_config(language, config)
            if success:
                imported_languages.append(language)
            else:
                errors.append(f"Failed to import {language} configuration")
        
        legal_service.log_compliance_event(
            log_type="settings",
            action="config_imported",
            details={
                "imported_languages": imported_languages,
                "errors": errors
            },
            compliance_frameworks=["PDPA", "GDPR"]
        )
        
        if imported_languages:
            return jsonify({
                "success": True,
                "imported_languages": imported_languages,
                "errors": errors
            })
        else:
            return jsonify({
                "success": False,
                "error": "No configurations could be imported",
                "errors": errors
            }), 400
            
    except Exception as e:
        legal_service.log_compliance_event(
            log_type="settings",
            action="config_import_error",
            details={"error": str(e)},
            severity="critical"
        )
        return jsonify({"error": "Internal server error"}), 500


@legal_admin_bp.route('/reset-defaults', methods=['POST'])
@admin_required
def reset_to_defaults():
    """Reset all legal configurations to defaults"""
    try:
        reset_languages = []
        
        for language in legal_labels.get_all_languages():
            # Get default config and save it
            default_config = legal_labels._get_default_config(language)
            success = legal_labels.update_legal_config(language, default_config)
            
            if success:
                reset_languages.append(language)
        
        # Clear cache to ensure fresh defaults are loaded
        legal_labels.clear_cache()
        
        legal_service.log_compliance_event(
            log_type="settings",
            action="config_reset_to_defaults",
            details={"reset_languages": reset_languages},
            compliance_frameworks=["PDPA", "GDPR"]
        )
        
        return jsonify({
            "success": True,
            "reset_languages": reset_languages
        })
        
    except Exception as e:
        legal_service.log_compliance_event(
            log_type="settings",
            action="config_reset_error",
            details={"error": str(e)},
            severity="critical"
        )
        return jsonify({"error": "Failed to reset configurations"}), 500


@legal_admin_bp.route('/preview-labels/<language>')
@admin_required
def preview_labels(language):
    """Preview how labels will look in the frontend"""
    try:
        if language not in legal_labels.get_all_languages():
            return jsonify({"error": "Unsupported language"}), 400
        
        config = legal_labels.get_legal_config(language)
        
        # Generate preview data
        preview_data = {
            "site_title": legal_labels.get_label("site_title", language),
            "dashboard_title": legal_labels.get_label("compliance.dashboard.title", language),
            "date_format_example": legal_labels.format_date(datetime.now().date(), language),
            "datetime_format_example": legal_labels.format_datetime(datetime.now(), language),
            "legal_contact": legal_labels.get_legal_contact(language),
            "data_protection_authority": legal_labels.get_data_protection_authority(language),
            "document_labels": {
                "privacy_policy": legal_labels.get_label("compliance.documents.privacy_policy", language),
                "terms": legal_labels.get_label("compliance.documents.terms_of_service", language),
                "impressum": legal_labels.get_label("compliance.documents.impressum", language),
                "medical_disclaimer": legal_labels.get_label("compliance.documents.medical_disclaimer", language)
            }
        }
        
        return jsonify(preview_data)
        
    except Exception as e:
        return jsonify({"error": "Failed to generate preview"}), 500


# === ENHANCED LEGAL DOCUMENT MANAGEMENT WITH CONFIGURABLE LABELS ===

@legal_admin_bp.route('/documents/create-with-labels', methods=['GET', 'POST'])
@admin_required
def create_document_with_labels():
    """Create legal document with configurable labels"""
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            language = data.get('language', 'th')
            
            # Use configurable labels for document creation
            document_title = legal_labels.get_label(
                f"compliance.documents.{data['document_type']}", 
                language, 
                data.get('title', '')
            )
            
            document = LegalDocument(
                document_type=data['document_type'],
                language=language,
                version=data['version'],
                title=document_title if not data.get('custom_title') else data['title'],
                content=data['content'],
                effective_date=datetime.strptime(data['effective_date'], '%Y-%m-%d').date(),
                requires_consent=data.get('requires_consent') == 'on',
                created_by=request.authorization.username if request.authorization else 'admin'
            )
            
            session = get_session()
            try:
                db_session = session
                db_session.add(document)
                db_session.commit()
                
                legal_service.log_compliance_event(
                    log_type="legal_document",
                    action="document_created_with_labels",
                    details={
                        "document_type": data['document_type'],
                        "language": language,
                        "version": data['version'],
                        "uses_configurable_title": not data.get('custom_title')
                    },
                    compliance_frameworks=["PDPA", "GDPR"]
                )
                
                flash('Legal document created successfully with configurable labels', 'success')
                return redirect(url_for('legal_admin.manage_documents'))
            except Exception as db_error:
                flash(f'Database error: {str(db_error)}', 'error')
            
        except Exception as e:
            legal_service.log_compliance_event(
                log_type="legal_document",
                action="document_creation_error",
                details={"error": str(e)},
                severity="critical"
            )
            flash(f'Error creating document: {str(e)}', 'error')
    
    return render_template('admin/legal/create_document_with_labels.html',
                         languages=legal_labels.get_all_languages())


# Register blueprints in __init__.py or main app file
def register_legal_routes(app):
    """Register legal compliance routes"""
    app.register_blueprint(legal_bp)
    app.register_blueprint(legal_admin_bp)