"""
Security Service for QR-Info-Portal
Addresses GitHub Security Scan Issues
"""

import yaml
import os
import re
import html
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import request, session, current_app, g
from werkzeug.security import safe_str_cmp
import logging

class SecurityService:
    """Comprehensive security service for the application"""
    
    def __init__(self):
        self.config = self._load_security_config()
        self.logger = logging.getLogger(__name__)
        
    def _load_security_config(self) -> Dict[str, Any]:
        """Load security configuration"""
        config_path = os.path.join('config', 'security.yml')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Security config not found at {config_path}, using defaults")
            return self._get_default_security_config()
    
    def _get_default_security_config(self) -> Dict[str, Any]:
        """Fallback security configuration"""
        return {
            'security': {
                'csp': {'enabled': True},
                'headers': {'x_content_type_options': 'nosniff'},
                'input_validation': {'sanitize_html': True},
                'rate_limiting': {'enabled': True, 'global_rate_limit': 100}
            }
        }
    
    def get_csp_header(self, is_kiosk: bool = False) -> str:
        """Generate Content Security Policy header"""
        csp_config = self.config.get('security', {}).get('csp', {})
        
        if not csp_config.get('enabled', True):
            return ""
        
        # Base CSP
        csp_parts = []
        
        # Default source
        default_src = csp_config.get('default_src', ["'self'"])
        csp_parts.append(f"default-src {' '.join(default_src)}")
        
        # Script sources (stricter for production)
        script_src = csp_config.get('script_src', ["'self'"])
        if is_kiosk:
            # More restrictive for kiosk mode
            script_src = [src for src in script_src if not src == "'unsafe-inline'"]
        csp_parts.append(f"script-src {' '.join(script_src)}")
        
        # Style sources
        style_src = csp_config.get('style_src', ["'self'"])
        csp_parts.append(f"style-src {' '.join(style_src)}")
        
        # Font sources
        font_src = csp_config.get('font_src', ["'self'"])
        csp_parts.append(f"font-src {' '.join(font_src)}")
        
        # Image sources
        img_src = csp_config.get('img_src', ["'self'", "data:"])
        csp_parts.append(f"img-src {' '.join(img_src)}")
        
        # Connect sources
        connect_src = csp_config.get('connect_src', ["'self'"])
        csp_parts.append(f"connect-src {' '.join(connect_src)}")
        
        # Frame ancestors (prevent clickjacking)
        frame_ancestors = csp_config.get('frame_ancestors', ["'none'"])
        csp_parts.append(f"frame-ancestors {' '.join(frame_ancestors)}")
        
        # Base URI
        base_uri = csp_config.get('base_uri', ["'self'"])
        csp_parts.append(f"base-uri {' '.join(base_uri)}")
        
        # Form action
        form_action = csp_config.get('form_action', ["'self'"])
        csp_parts.append(f"form-action {' '.join(form_action)}")
        
        return '; '.join(csp_parts)
    
    def get_security_headers(self) -> Dict[str, str]:
        """Generate all security headers"""
        headers = {}
        
        headers_config = self.config.get('security', {}).get('headers', {})
        
        # Strict Transport Security
        if headers_config.get('strict_transport_security', {}).get('enabled', True):
            sts_config = headers_config.get('strict_transport_security', {})
            max_age = sts_config.get('max_age', 31536000)
            sts_value = f"max-age={max_age}"
            if sts_config.get('include_subdomains', True):
                sts_value += "; includeSubDomains"
            if sts_config.get('preload', True):
                sts_value += "; preload"
            headers['Strict-Transport-Security'] = sts_value
        
        # Content Type Options
        if headers_config.get('x_content_type_options'):
            headers['X-Content-Type-Options'] = headers_config['x_content_type_options']
        
        # Frame Options
        if headers_config.get('x_frame_options'):
            headers['X-Frame-Options'] = headers_config['x_frame_options']
        
        # XSS Protection
        if headers_config.get('x_xss_protection'):
            headers['X-XSS-Protection'] = headers_config['x_xss_protection']
        
        # Referrer Policy
        if headers_config.get('referrer_policy'):
            headers['Referrer-Policy'] = headers_config['referrer_policy']
        
        # Permissions Policy
        permissions = headers_config.get('permissions_policy', {})
        if permissions:
            policy_parts = []
            for feature, origins in permissions.items():
                if origins == ["none"]:
                    policy_parts.append(f"{feature}=()")
                else:
                    origins_str = ' '.join([f'"{origin}"' if origin != 'self' else origin for origin in origins])
                    policy_parts.append(f"{feature}=({origins_str})")
            if policy_parts:
                headers['Permissions-Policy'] = ', '.join(policy_parts)
        
        return headers
    
    def sanitize_input(self, input_value: str, max_length: Optional[int] = None) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        if not isinstance(input_value, str):
            return str(input_value)
        
        # Get max length from config
        if max_length is None:
            max_length = self.config.get('security', {}).get('input_validation', {}).get('max_input_length', 1000)
        
        # Truncate if too long
        if len(input_value) > max_length:
            input_value = input_value[:max_length]
        
        # HTML escape
        if self.config.get('security', {}).get('input_validation', {}).get('sanitize_html', True):
            input_value = html.escape(input_value)
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'<script.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',  # onclick, onload, etc.
            r'<iframe',
            r'<object',
            r'<embed'
        ]
        
        for pattern in dangerous_patterns:
            input_value = re.sub(pattern, '', input_value, flags=re.IGNORECASE)
        
        return input_value.strip()
    
    def validate_file_upload(self, filename: str, content: bytes) -> Dict[str, Any]:
        """Validate file uploads for security"""
        result = {
            'valid': True,
            'errors': [],
            'sanitized_filename': filename
        }
        
        upload_config = self.config.get('security', {}).get('file_uploads', {})
        
        # Check file extension
        allowed_extensions = upload_config.get('allowed_extensions', ['.yml', '.yaml', '.json', '.png', '.jpg', '.svg'])
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            result['valid'] = False
            result['errors'].append(f"File type {file_ext} not allowed")
        
        # Check file size
        max_size_mb = upload_config.get('max_file_size_mb', 2)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if len(content) > max_size_bytes:
            result['valid'] = False
            result['errors'].append(f"File size exceeds {max_size_mb}MB limit")
        
        # Sanitize filename
        result['sanitized_filename'] = self._sanitize_filename(filename)
        
        # Basic malware scanning (check for suspicious patterns)
        if upload_config.get('scan_for_malware', True):
            if self._contains_suspicious_patterns(content):
                result['valid'] = False
                result['errors'].append("File contains suspicious content")
        
        return result
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent directory traversal"""
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove potentially dangerous characters
        filename = re.sub(r'[^\w\-_\.]', '', filename)
        
        # Ensure it doesn't start with a dot (hidden file)
        if filename.startswith('.'):
            filename = 'file_' + filename
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext
        
        return filename
    
    def _contains_suspicious_patterns(self, content: bytes) -> bool:
        """Basic malware detection by pattern matching"""
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'eval(',
            b'exec(',
            b'system(',
            b'shell_exec',
            b'passthru',
            b'<?php'
        ]
        
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in suspicious_patterns)
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return session['csrf_token']
    
    def validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token"""
        session_token = session.get('csrf_token')
        if not session_token:
            return False
        
        return safe_str_cmp(session_token, token)
    
    def is_rate_limited(self, endpoint: str, client_ip: str) -> bool:
        """Check if request should be rate limited"""
        rate_config = self.config.get('security', {}).get('rate_limiting', {})
        
        if not rate_config.get('enabled', True):
            return False
        
        # Get rate limit for specific endpoint
        endpoint_limits = rate_config.get('endpoints', {})
        rate_limit = endpoint_limits.get(endpoint, rate_config.get('global_rate_limit', 100))
        
        # Simple in-memory rate limiting (for production, use Redis)
        if not hasattr(g, 'rate_limit_storage'):
            g.rate_limit_storage = {}
        
        now = datetime.now()
        minute_window = now.replace(second=0, microsecond=0)
        
        key = f"{client_ip}:{endpoint}:{minute_window}"
        current_count = g.rate_limit_storage.get(key, 0)
        
        if current_count >= rate_limit:
            self.logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint}")
            return True
        
        g.rate_limit_storage[key] = current_count + 1
        return False
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events"""
        if not self.config.get('security', {}).get('error_handling', {}).get('log_security_events', True):
            return
        
        self.logger.warning(f"Security event: {event_type}", extra={
            'event_type': event_type,
            'details': details,
            'client_ip': request.remote_addr if request else None,
            'user_agent': request.user_agent.string if request else None,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def get_safe_redirect_url(self, url: str, allowed_hosts: List[str] = None) -> Optional[str]:
        """Validate and return safe redirect URL"""
        if not url:
            return None
        
        # Only allow relative URLs or URLs to allowed hosts
        if url.startswith('/'):
            return url
        
        if allowed_hosts:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if parsed.hostname in allowed_hosts:
                return url
        
        return None
    
    def configure_secure_session(self, app):
        """Configure secure session settings"""
        session_config = self.config.get('security', {}).get('session', {})
        
        # Secure cookies
        app.config['SESSION_COOKIE_SECURE'] = session_config.get('secure_cookies', True)
        app.config['SESSION_COOKIE_HTTPONLY'] = session_config.get('httponly_cookies', True)
        app.config['SESSION_COOKIE_SAMESITE'] = session_config.get('samesite_cookies', 'Strict')
        
        # Session timeout
        timeout_minutes = session_config.get('session_timeout_minutes', 30)
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=timeout_minutes)

# Global instance
security_service = SecurityService()