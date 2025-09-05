#!/usr/bin/env python3
"""
CONTINUOUS SECURITY VALIDATION TESTS
====================================
Unit tests that validate security fixes and prevent regression
Run with: pytest tests/test_security_validation.py -v
"""

import pytest
import re
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path

# Add app to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models import AdminUser, Announcement
from app.database import get_session
from sqlmodel import Session, select

class TestSQLInjectionProtection:
    """Test SQL injection protection measures"""
    
    def test_orm_usage_prevents_sql_injection(self):
        """Verify ORM usage instead of raw SQL"""
        # Read routes_admin.py and check for dangerous patterns
        routes_file = Path(__file__).parent.parent / "app" / "routes_admin.py"
        with open(routes_file, 'r') as f:
            content = f.read()
        
        # Check that no raw SQL DELETE/INSERT/UPDATE statements exist
        dangerous_sql_patterns = [
            r'session\.exec\s*\(\s*["\']DELETE',
            r'session\.exec\s*\(\s*["\']INSERT', 
            r'session\.exec\s*\(\s*["\']UPDATE',
            r'session\.execute\s*\(\s*["\'](?:DELETE|INSERT|UPDATE)'
        ]
        
        for pattern in dangerous_sql_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            assert len(matches) == 0, f"Found dangerous raw SQL: {matches}"
    
    def test_parameterized_queries_only(self):
        """Ensure all queries use parameterized statements"""
        # Check that string formatting is not used with SQL
        routes_file = Path(__file__).parent.parent / "app" / "routes_admin.py"
        with open(routes_file, 'r') as f:
            content = f.read()
        
        # Look for dangerous string formatting patterns
        format_patterns = [
            r'f["\'].*?SELECT.*?\{.*?\}',
            r'["\'].*?SELECT.*?["\'].*?%',
            r'\.format\(.*?\).*?(?:SELECT|INSERT|UPDATE|DELETE)'
        ]
        
        for pattern in format_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            assert len(matches) == 0, f"Found SQL with string formatting: {matches}"

class TestXSSProtection:
    """Test XSS protection measures"""
    
    def test_template_safe_filter_usage(self):
        """Verify no unsafe |safe filters on user content"""
        templates_dir = Path(__file__).parent.parent / "app" / "templates"
        
        unsafe_files = []
        
        for template_file in templates_dir.rglob("*.html"):
            with open(template_file, 'r') as f:
                content = f.read()
            
            # Find |safe usage that might be dangerous
            safe_patterns = re.findall(r'(\w+\.\w+\s*\|\s*safe)', content)
            if safe_patterns:
                # Check if it's user-controllable content
                dangerous_vars = ['content', 'body', 'title', 'description', 'note']
                for pattern in safe_patterns:
                    for var in dangerous_vars:
                        if var in pattern.lower():
                            unsafe_files.append(f"{template_file}: {pattern}")
        
        assert len(unsafe_files) == 0, f"Found unsafe |safe usage: {unsafe_files}"
    
    def test_input_sanitization_function_security(self):
        """Test that sanitize_input function properly protects against XSS"""
        from app.routes_admin import sanitize_input
        
        # Test XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "'-alert('XSS')-'"
        ]
        
        for payload in xss_payloads:
            sanitized = sanitize_input(payload, allow_html=False)
            
            # Verify dangerous elements are removed/escaped
            assert "<script>" not in sanitized, f"Script tag not removed from: {payload}"
            assert "javascript:" not in sanitized.lower(), f"JavaScript protocol not removed: {payload}"
            assert "onerror=" not in sanitized.lower(), f"Event handler not removed: {payload}"

class TestAuthenticationSecurity:
    """Test authentication security implementation"""
    
    def test_no_default_credentials(self):
        """Verify no hardcoded default credentials exist"""
        routes_file = Path(__file__).parent.parent / "app" / "routes_admin.py"
        with open(routes_file, 'r') as f:
            content = f.read()
        
        # Check for dangerous default credentials
        assert "'admin123'" not in content, "Default password 'admin123' found in code"
        assert '"admin123"' not in content, "Default password 'admin123' found in code"
    
    def test_password_hashing_implementation(self):
        """Test password hashing is properly implemented"""
        admin_user = AdminUser(username="test")
        
        # Test password setting
        admin_user.set_password("testpassword123")
        assert admin_user.password_hash != "testpassword123", "Password not hashed"
        assert len(admin_user.password_hash) > 50, "Hash appears too short"
        
        # Test password verification
        assert admin_user.verify_password("testpassword123"), "Password verification failed"
        assert not admin_user.verify_password("wrongpassword"), "Wrong password accepted"
    
    def test_account_lockout_mechanism(self):
        """Test account lockout after failed attempts"""
        admin_user = AdminUser(username="test_lockout")
        
        # Simulate multiple failed login attempts
        for i in range(6):  # Should lock after 5 attempts
            admin_user.record_login_attempt(False)
        
        assert admin_user.is_locked(), "Account not locked after multiple failed attempts"
        assert admin_user.login_attempts >= 5, "Failed attempt counter not working"

class TestCSRFProtection:
    """Test CSRF protection implementation"""
    
    def test_csrf_token_generation(self):
        """Test CSRF token generation security"""
        from app.routes_admin import generate_csrf_token
        
        # Generate multiple tokens
        tokens = [generate_csrf_token() for _ in range(10)]
        
        # Verify uniqueness
        assert len(set(tokens)) == len(tokens), "CSRF tokens not unique"
        
        # Verify length (should be 32 hex chars)
        for token in tokens:
            assert len(token) == 32, f"CSRF token wrong length: {len(token)}"
            assert re.match(r'^[a-f0-9]+$', token), f"CSRF token not hex: {token}"
    
    def test_csrf_validation_function(self):
        """Test CSRF validation logic"""
        from app.routes_admin import validate_csrf_token, generate_csrf_token
        from flask import Flask
        
        app = Flask(__name__)
        with app.test_request_context():
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    # Generate token
                    token = generate_csrf_token()
                    sess['csrf_token'] = token
                    
                    # Valid token should pass
                    assert validate_csrf_token(token), "Valid CSRF token rejected"
                    
                    # Invalid token should fail
                    assert not validate_csrf_token("invalid"), "Invalid CSRF token accepted"
                    assert not validate_csrf_token(""), "Empty CSRF token accepted"

class TestRateLimiting:
    """Test rate limiting implementation"""
    
    def test_rate_limit_implementation(self):
        """Test rate limiting logic"""
        from app.routes_admin import check_rate_limit, rate_limit_store
        
        # Clear rate limit store
        rate_limit_store.clear()
        
        test_ip = "192.168.1.100"
        
        # Should allow initial requests
        for i in range(20):
            result = check_rate_limit(test_ip)
            if i < 30:  # Should allow up to 30 requests
                assert result, f"Rate limit triggered too early at request {i}"
        
        # Should block after limit
        for i in range(5):
            result = check_rate_limit(test_ip)
            assert not result, f"Rate limit not triggered after exceeding limit"

class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_sanitize_input_xss_protection(self):
        """Test XSS protection in input sanitization"""
        from app.routes_admin import sanitize_input
        
        test_cases = [
            ("<script>alert('XSS')</script>", "Script tags should be escaped/removed"),
            ("<img src=x onerror=alert(1)>", "Image with onerror should be sanitized"),
            ("javascript:alert(1)", "JavaScript protocol should be removed"),
            ("data:text/html,<script>alert(1)</script>", "Data URI should be sanitized"),
            ("'><script>alert(1)</script>", "Quote breaking should be handled")
        ]
        
        for payload, description in test_cases:
            result = sanitize_input(payload, allow_html=False)
            
            # Check that dangerous patterns are removed
            assert "<script>" not in result.lower(), f"{description} - script not removed"
            assert "javascript:" not in result.lower(), f"{description} - javascript protocol found"
            assert "onerror=" not in result.lower(), f"{description} - event handler found"
    
    def test_maximum_input_lengths(self):
        """Test input length limitations"""
        from app.routes_admin import sanitize_input
        
        # Test length limiting
        long_input = "A" * 10000
        result = sanitize_input(long_input, max_length=500)
        
        assert len(result) <= 500, f"Input not properly truncated: {len(result)}"

class TestSessionSecurity:
    """Test session security configuration"""
    
    def test_session_configuration(self):
        """Test session security settings"""
        app = create_app()
        
        # Check security configurations
        assert app.config.get('SESSION_COOKIE_HTTPONLY'), "HttpOnly not set on session cookies"
        assert app.config.get('SESSION_COOKIE_SAMESITE') == 'Lax', "SameSite not properly configured"
        
        # Check session lifetime is reasonable
        lifetime = app.config.get('PERMANENT_SESSION_LIFETIME')
        if lifetime:
            assert lifetime.total_seconds() <= 7200, "Session lifetime too long (>2 hours)"

class TestSecurityHeaders:
    """Test security headers implementation"""
    
    def test_security_headers_present(self):
        """Test that required security headers are present"""
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/')
            
            required_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY', 
                'X-XSS-Protection': '1; mode=block',
                'Content-Security-Policy': True  # Just check presence
            }
            
            for header, expected in required_headers.items():
                assert header in response.headers, f"Missing security header: {header}"
                
                if expected is not True:
                    assert response.headers[header] == expected, f"Wrong value for {header}"

class TestFileUploadSecurity:
    """Test file upload security (if implemented)"""
    
    def test_file_upload_restrictions(self):
        """Test file upload security measures"""
        # This test will pass if no file upload is implemented
        # or if proper security measures are in place
        
        routes_file = Path(__file__).parent.parent / "app" / "routes_admin.py"
        with open(routes_file, 'r') as f:
            content = f.read()
        
        if "request.files" in content:
            # File upload exists - check for security measures
            security_measures = [
                "secure_filename",  # Filename sanitization
                "allowed_extensions",  # File type validation
                "MAX_CONTENT_LENGTH",  # File size limits
            ]
            
            missing_measures = []
            for measure in security_measures:
                if measure not in content:
                    missing_measures.append(measure)
            
            assert len(missing_measures) == 0, f"Missing file upload security: {missing_measures}"

class TestConfigurationSecurity:
    """Test security-related configuration"""
    
    def test_secret_key_configuration(self):
        """Test secret key is properly configured"""
        app = create_app()
        
        secret_key = app.config.get('SECRET_KEY')
        assert secret_key, "SECRET_KEY not configured"
        assert secret_key != 'dev-secret-key', "Development secret key used"
        assert len(secret_key) >= 32, "Secret key too short"
    
    def test_debug_mode_disabled(self):
        """Test debug mode is disabled in production"""
        app = create_app()
        
        # Debug should be disabled by default
        assert not app.debug, "Debug mode enabled - security risk"

class TestDataExposureProtection:
    """Test protection against sensitive data exposure"""
    
    def test_no_password_logging(self):
        """Verify passwords are not logged"""
        from app.routes_admin import log_admin_action
        
        # Mock logger to capture log calls
        with patch('app.routes_admin.logger') as mock_logger:
            # Simulate admin action that might log sensitive data
            test_details = {"password": "secret123", "normal_field": "value"}
            log_admin_action("test_action", test_details)
            
            # Verify password is not in any log calls
            for call in mock_logger.info.call_args_list:
                log_message = str(call[0][0])
                assert "secret123" not in log_message, "Password found in log message"
    
    def test_error_messages_no_sensitive_info(self):
        """Test error messages don't expose sensitive information"""
        app = create_app()
        
        with app.test_client() as client:
            # Test various error conditions
            error_urls = [
                '/admin/nonexistent',
                '/qr?target=invalid_url', 
                '/month?year=invalid'
            ]
            
            for url in error_urls:
                response = client.get(url)
                
                # Check that error messages don't contain sensitive info
                sensitive_patterns = [
                    r'/[a-zA-Z0-9_/\-\.]+\.py',  # File paths
                    r'password',                  # Password references
                    r'secret',                   # Secret references
                    r'Traceback'                 # Python tracebacks
                ]
                
                for pattern in sensitive_patterns:
                    matches = re.findall(pattern, response.get_data(as_text=True), re.IGNORECASE)
                    assert len(matches) == 0, f"Sensitive info in error: {pattern} in {url}"

@pytest.fixture
def test_app():
    """Create test app instance"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable for testing
    return app

@pytest.fixture  
def test_client(test_app):
    """Create test client"""
    return test_app.test_client()

class TestAdminPanelSecurity:
    """Test admin panel specific security measures"""
    
    def test_admin_requires_authentication(self, test_client):
        """Test admin panel requires valid authentication"""
        response = test_client.get('/admin')
        assert response.status_code == 401, "Admin panel accessible without auth"
    
    def test_admin_csrf_protection(self, test_client):
        """Test CSRF protection on admin operations"""
        # This requires proper authentication setup
        import base64
        
        # Try with valid auth but no CSRF
        auth_header = base64.b64encode(b"admin:admin123").decode()
        headers = {"Authorization": f"Basic {auth_header}"}
        
        # POST operation without CSRF should fail
        response = test_client.post('/admin/status', 
                                   data={'status_type': 'URLAUB'}, 
                                   headers=headers)
        
        # Should be redirected or show error due to missing CSRF
        assert response.status_code in [403, 302], "CSRF protection not working"

class TestSecurityRegression:
    """Tests to prevent security regression"""
    
    def test_security_headers_regression(self, test_client):
        """Verify security headers don't get removed"""
        response = test_client.get('/')
        
        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
            'Content-Security-Policy'
        ]
        
        for header in required_headers:
            assert header in response.headers, f"Security header missing: {header}"
    
    def test_admin_rate_limiting_active(self):
        """Verify admin rate limiting is active"""
        from app.routes_admin import check_rate_limit, rate_limit_store
        
        # Clear previous state
        test_ip = "127.0.0.1"
        rate_limit_store.pop(test_ip, None)
        
        # Should allow reasonable number of requests
        for i in range(25):  # Under the limit
            result = check_rate_limit(test_ip)
            assert result, f"Rate limit triggered too early at request {i+1}"
        
        # Should start blocking after limit
        blocked_count = 0
        for i in range(10):  # Try more requests
            result = check_rate_limit(test_ip)
            if not result:
                blocked_count += 1
        
        assert blocked_count > 0, "Rate limiting not working - no blocks after limit"

# Integration Test for End-to-End Security
class TestE2ESecurityFlow:
    """End-to-end security validation"""
    
    def test_complete_admin_workflow_security(self, test_client):
        """Test complete admin workflow with security measures"""
        import base64
        
        # 1. Authenticate (should work with proper credentials)
        auth_header = base64.b64encode(b"admin:admin123").decode()
        headers = {"Authorization": f"Basic {auth_header}"}
        
        # 2. Access admin dashboard
        response = test_client.get('/admin', headers=headers)
        # Note: This might fail if default credentials are properly removed
        
        # 3. Check CSRF token is present
        if response.status_code == 200:
            assert 'csrf_token' in response.get_data(as_text=True), "CSRF token not found in admin page"

def pytest_html_report_title(report):
    """Customize pytest HTML report title"""
    report.title = "QR-Info-Portal Security Validation Report"

# Run tests with security-focused configuration
if __name__ == "__main__":
    pytest.main([
        __file__, 
        "-v", 
        "--tb=short",
        "--capture=no",
        f"--html=security_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
        "--self-contained-html"
    ])