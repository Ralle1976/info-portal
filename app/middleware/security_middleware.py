"""
Security Middleware for QR-Info-Portal
Implements security headers, CSP, rate limiting, and input sanitization
"""

from flask import request, g, jsonify, abort
from functools import wraps
import re
from app.services.security_service import security_service
from app.logging_config import get_logger

logger = get_logger(__name__)

def apply_security_headers(response):
    """Apply security headers to all responses"""
    try:
        # Determine if this is a kiosk request
        is_kiosk = (
            request.endpoint and 
            ('kiosk' in request.endpoint or request.path.startswith('/kiosk/'))
        )
        
        # Get security headers
        headers = security_service.get_security_headers()
        for header, value in headers.items():
            response.headers[header] = value
        
        # Content Security Policy
        csp = security_service.get_csp_header(is_kiosk=is_kiosk)
        if csp:
            response.headers['Content-Security-Policy'] = csp
        
        # Additional headers for specific content types
        if response.content_type and 'application/json' in response.content_type:
            response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Cache control for sensitive pages
        if request.endpoint and any(sensitive in request.endpoint for sensitive in ['admin', 'login']):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        logger.error(f"Error applying security headers: {e}")
        return response

def rate_limit_middleware():
    """Rate limiting middleware"""
    try:
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        
        # Extract endpoint pattern for rate limiting
        endpoint = request.endpoint or request.path
        
        # Check for rate limiting
        if security_service.is_rate_limited(endpoint, client_ip):
            security_service.log_security_event('rate_limit_exceeded', {
                'endpoint': endpoint,
                'client_ip': client_ip,
                'user_agent': request.user_agent.string
            })
            
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.'
            }), 429
            
    except Exception as e:
        logger.error(f"Error in rate limiting: {e}")
        # Don't block request on rate limiting errors
        pass

def csrf_protection_middleware():
    """CSRF protection for POST requests"""
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        # Skip CSRF for certain endpoints (like API endpoints with other auth)
        skip_csrf_endpoints = ['/healthz', '/api/']
        
        if not any(request.path.startswith(skip) for skip in skip_csrf_endpoints):
            # Check for CSRF token
            csrf_token = (
                request.form.get('csrf_token') or 
                request.headers.get('X-CSRF-Token') or
                request.json.get('csrf_token') if request.is_json else None
            )
            
            if not csrf_token or not security_service.validate_csrf_token(csrf_token):
                security_service.log_security_event('csrf_violation', {
                    'endpoint': request.endpoint,
                    'path': request.path,
                    'method': request.method,
                    'has_token': bool(csrf_token)
                })
                
                if request.is_json:
                    return jsonify({'error': 'CSRF token missing or invalid'}), 403
                else:
                    abort(403)

def sanitize_inputs_middleware():
    """Sanitize all user inputs"""
    try:
        # Sanitize form data
        if request.form:
            sanitized_form = {}
            for key, value in request.form.items():
                if isinstance(value, str):
                    sanitized_form[key] = security_service.sanitize_input(value)
                else:
                    sanitized_form[key] = value
            # Replace request.form with sanitized version
            request.form = sanitized_form
        
        # Sanitize URL parameters
        if request.args:
            sanitized_args = {}
            for key, value in request.args.items():
                if isinstance(value, str):
                    sanitized_args[key] = security_service.sanitize_input(value)
                else:
                    sanitized_args[key] = value
            # Store sanitized args in g for later use
            g.sanitized_args = sanitized_args
        
        # Sanitize JSON data (be careful not to break valid JSON structure)
        if request.is_json and request.json:
            g.sanitized_json = _sanitize_json_recursive(request.json)
            
    except Exception as e:
        logger.error(f"Error sanitizing inputs: {e}")
        # Don't block request on sanitization errors

def _sanitize_json_recursive(data):
    """Recursively sanitize JSON data"""
    if isinstance(data, dict):
        return {key: _sanitize_json_recursive(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_sanitize_json_recursive(item) for item in data]
    elif isinstance(data, str):
        return security_service.sanitize_input(data)
    else:
        return data

def kiosk_security_middleware():
    """Additional security for kiosk endpoints"""
    if request.path.startswith('/kiosk/'):
        # Kiosk-specific security checks
        
        # Check if request is from allowed networks (if configured)
        kiosk_config = security_service.config.get('kiosk_security', {})
        network_restrictions = kiosk_config.get('network_restrictions', {})
        
        if network_restrictions.get('allowed_networks'):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
            if not _is_ip_in_allowed_networks(client_ip, network_restrictions['allowed_networks']):
                security_service.log_security_event('kiosk_unauthorized_network', {
                    'client_ip': client_ip,
                    'path': request.path
                })
                abort(403)
        
        # Add kiosk-specific headers
        g.kiosk_headers = {
            'X-Frame-Options': 'DENY',
            'X-Content-Type-Options': 'nosniff',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        }

def _is_ip_in_allowed_networks(ip, allowed_networks):
    """Check if IP is in allowed networks (simplified implementation)"""
    # This is a simplified check - in production, use proper CIDR matching
    if not ip or not allowed_networks:
        return True
    
    for network in allowed_networks:
        if network.endswith('/16'):
            network_base = network.split('/')[0].rsplit('.', 2)[0]
            if ip.startswith(network_base):
                return True
        elif network.endswith('/8'):
            network_base = network.split('/')[0].split('.')[0]
            if ip.startswith(network_base):
                return True
        elif ip == network:
            return True
    
    return False

# Decorator for admin-only endpoints
def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check admin authentication
        if not _is_admin_authenticated():
            security_service.log_security_event('unauthorized_admin_access', {
                'endpoint': request.endpoint,
                'path': request.path,
                'client_ip': request.environ.get('REMOTE_ADDR', 'unknown')
            })
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

def _is_admin_authenticated():
    """Check if user is authenticated as admin"""
    # Implement your admin authentication logic here
    # For basic auth:
    from flask import request
    import base64
    import os
    
    auth = request.authorization
    if not auth:
        return False
    
    # Check against environment variables
    admin_user = os.getenv('ADMIN_USERNAME', 'admin')
    admin_pass = os.getenv('ADMIN_PASSWORD', '')
    
    return auth.username == admin_user and auth.password == admin_pass

# Decorator for file upload validation
def validate_file_upload(f):
    """Decorator to validate file uploads"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.files:
            for field_name, file in request.files.items():
                if file.filename:
                    # Read file content for validation
                    content = file.read()
                    file.seek(0)  # Reset file pointer
                    
                    # Validate file
                    validation_result = security_service.validate_file_upload(file.filename, content)
                    
                    if not validation_result['valid']:
                        security_service.log_security_event('malicious_file_upload', {
                            'filename': file.filename,
                            'errors': validation_result['errors'],
                            'client_ip': request.environ.get('REMOTE_ADDR', 'unknown')
                        })
                        
                        return jsonify({
                            'error': 'File upload validation failed',
                            'details': validation_result['errors']
                        }), 400
        
        return f(*args, **kwargs)
    return decorated_function

# Security middleware registration function
def register_security_middleware(app):
    """Register all security middleware with the Flask app"""
    
    # Before request middleware
    @app.before_request
    def before_request_security():
        # Rate limiting
        rate_limit_response = rate_limit_middleware()
        if rate_limit_response:
            return rate_limit_response
        
        # Input sanitization
        sanitize_inputs_middleware()
        
        # CSRF protection
        csrf_response = csrf_protection_middleware()
        if csrf_response:
            return csrf_response
        
        # Kiosk security
        kiosk_security_middleware()
    
    # After request middleware
    @app.after_request
    def after_request_security(response):
        # Apply security headers
        response = apply_security_headers(response)
        
        # Apply kiosk-specific headers if needed
        if hasattr(g, 'kiosk_headers'):
            for header, value in g.kiosk_headers.items():
                response.headers[header] = value
        
        return response
    
    # Error handlers for security
    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access denied'
        }), 403
    
    @app.errorhandler(429)
    def rate_limit_error(error):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    # Configure secure session
    security_service.configure_secure_session(app)
    
    logger.info("Security middleware registered successfully")