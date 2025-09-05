#!/usr/bin/env python3
"""
SECURITY TEST SUITE FOR QR-INFO-PORTAL
=====================================
Comprehensive penetration testing and vulnerability assessment

SECURITY AREAS TESTED:
1. SQL Injection (SQLi) - All database queries
2. Cross-Site Scripting (XSS) - Input/Output handling
3. Cross-Site Request Forgery (CSRF) - State-changing operations
4. Authentication Bypass - Admin panel access
5. Session Security - Cookie handling
6. Input Validation - All user inputs
7. Authorization - Role-based access control
8. Rate Limiting - Brute force protection
"""

import requests
import json
import time
import hashlib
import re
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import urllib.parse
import base64
import secrets
from dataclasses import dataclass
from enum import Enum

class VulnerabilityLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"  
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class SecurityVulnerability:
    category: str
    level: VulnerabilityLevel
    title: str
    description: str
    evidence: str
    impact: str
    recommendation: str
    cve_reference: Optional[str] = None
    exploit_scenario: Optional[str] = None

class QRPortalSecurityTester:
    def __init__(self, base_url: str = "http://localhost:5000", admin_user: str = "admin", admin_pass: str = "admin123"):
        self.base_url = base_url.rstrip('/')
        self.admin_user = admin_user
        self.admin_pass = admin_pass
        self.session = requests.Session()
        self.vulnerabilities: List[SecurityVulnerability] = []
        self.test_results: Dict[str, Any] = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log test progress"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def add_vulnerability(self, vuln: SecurityVulnerability):
        """Add discovered vulnerability"""
        self.vulnerabilities.append(vuln)
        self.log(f"VULNERABILITY FOUND: {vuln.level.value} - {vuln.title}", "CRITICAL" if vuln.level == VulnerabilityLevel.CRITICAL else "WARNING")

    # ==================== SQL INJECTION TESTS ====================
    
    def test_sql_injection_authentication(self):
        """Test SQL injection in admin authentication"""
        self.log("Testing SQL Injection in Authentication...")
        
        sql_payloads = [
            "admin' OR '1'='1",
            "admin' OR 1=1--",
            "admin' OR 1=1#",
            "' UNION SELECT 1,1,1,1--",
            "admin'; DROP TABLE adminuser;--",
            "admin' AND (SELECT SUBSTRING(password,1,1) FROM adminuser WHERE username='admin')='a'--",
            "admin' OR (SELECT COUNT(*) FROM adminuser)>0--",
        ]
        
        for payload in sql_payloads:
            try:
                auth = base64.b64encode(f"{payload}:anypassword".encode()).decode()
                headers = {"Authorization": f"Basic {auth}"}
                
                response = self.session.get(f"{self.base_url}/admin", headers=headers)
                
                if response.status_code == 200 and "dashboard" in response.text.lower():
                    self.add_vulnerability(SecurityVulnerability(
                        category="SQL_INJECTION",
                        level=VulnerabilityLevel.CRITICAL,
                        title="SQL Injection in Authentication",
                        description=f"Authentication bypass possible using SQL injection payload: {payload}",
                        evidence=f"Payload '{payload}' bypassed authentication. Status: {response.status_code}",
                        impact="Complete admin panel access without valid credentials",
                        recommendation="Use parameterized queries and prepared statements. Implement proper input validation.",
                        exploit_scenario="Attacker gains full admin access to modify lab status, hours, and announcements"
                    ))
                    
            except Exception as e:
                self.log(f"Error testing SQL injection payload {payload}: {e}", "ERROR")
    
    def test_sql_injection_parameters(self):
        """Test SQL injection in URL parameters and form fields"""
        self.log("Testing SQL Injection in Parameters...")
        
        # Test parameters that might be used in queries
        test_endpoints = [
            ("/week?offset='OR'1'='1", "week view offset parameter"),
            ("/month?year=2024'UNION SELECT * FROM settings--", "month view year parameter"),
            ("/month?month=1'OR 1=1--", "month view month parameter"),
        ]
        
        sql_payloads = [
            "' OR '1'='1",
            "1' OR 1=1--", 
            "1'; DROP TABLE announcements;--",
            "1' UNION SELECT password FROM adminuser--"
        ]
        
        for endpoint, description in test_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                # Check for SQL error messages that might indicate injection vulnerability
                sql_error_patterns = [
                    "sqlite3.OperationalError",
                    "SQL syntax error",
                    "mysql_fetch_array",
                    "postgres",
                    "ORA-01756",
                    "SQLServer JDBC Driver"
                ]
                
                for pattern in sql_error_patterns:
                    if pattern.lower() in response.text.lower():
                        self.add_vulnerability(SecurityVulnerability(
                            category="SQL_INJECTION",
                            level=VulnerabilityLevel.HIGH,
                            title="SQL Injection via URL Parameters",
                            description=f"SQL error message exposed in {description}",
                            evidence=f"Endpoint: {endpoint}, Pattern found: {pattern}",
                            impact="Database structure disclosure, potential data extraction",
                            recommendation="Implement proper parameter validation and hide database error messages"
                        ))
                        
            except Exception as e:
                self.log(f"Error testing endpoint {endpoint}: {e}", "ERROR")

    # ==================== XSS TESTS ====================
    
    def test_xss_stored(self):
        """Test Stored XSS in admin forms"""
        self.log("Testing Stored XSS vulnerabilities...")
        
        # Get admin session first
        admin_auth = self._get_admin_auth()
        if not admin_auth:
            self.log("Cannot test stored XSS - admin authentication failed", "ERROR")
            return
            
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'-alert('XSS')-'",
            "\"><script>alert('XSS')</script>",
            "<iframe src=javascript:alert('XSS')></iframe>"
        ]
        
        # Test announcement creation (most likely stored XSS vector)
        for payload in xss_payloads:
            try:
                # Get CSRF token first
                csrf_token = self._get_csrf_token(admin_auth)
                
                form_data = {
                    'csrf_token': csrf_token,
                    'lang': 'de',
                    'title': f"Test {payload}",
                    'body': f"Content with XSS: {payload}",
                    'priority': 'normal',
                    'category': 'general',
                    'active': 'on'
                }
                
                response = self.session.post(
                    f"{self.base_url}/admin/announcements",
                    data=form_data,
                    headers=admin_auth
                )
                
                # Check if the payload was stored without escaping
                home_response = self.session.get(f"{self.base_url}/")
                
                if payload in home_response.text and "<script>" in home_response.text:
                    self.add_vulnerability(SecurityVulnerability(
                        category="XSS_STORED",
                        level=VulnerabilityLevel.HIGH,
                        title="Stored XSS in Announcements",
                        description=f"XSS payload stored and executed: {payload}",
                        evidence=f"Payload found in homepage without escaping",
                        impact="Script execution in user browsers, session hijacking possible",
                        recommendation="Implement proper HTML escaping in templates and input sanitization"
                    ))
                    
            except Exception as e:
                self.log(f"Error testing stored XSS with payload {payload}: {e}", "ERROR")
    
    def test_xss_reflected(self):
        """Test Reflected XSS in URL parameters"""
        self.log("Testing Reflected XSS vulnerabilities...")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>", 
            "javascript:alert('XSS')",
            "\"><script>alert('XSS')</script>"
        ]
        
        # Test various endpoints that might reflect user input
        test_params = [
            ("week", "offset", "Week view offset parameter"),
            ("month", "year", "Month view year parameter"), 
            ("month", "month", "Month view month parameter"),
            ("set-language", None, "Language setting"),  # Test URL path injection
        ]
        
        for endpoint, param, description in test_params:
            for payload in xss_payloads:
                try:
                    if param:
                        url = f"{self.base_url}/{endpoint}?{param}={urllib.parse.quote(payload)}"
                    else:
                        url = f"{self.base_url}/{endpoint}/{urllib.parse.quote(payload)}"
                        
                    response = self.session.get(url)
                    
                    # Check if payload is reflected without escaping
                    if payload in response.text:
                        self.add_vulnerability(SecurityVulnerability(
                            category="XSS_REFLECTED", 
                            level=VulnerabilityLevel.MEDIUM,
                            title="Reflected XSS",
                            description=f"XSS payload reflected in {description}: {payload}",
                            evidence=f"URL: {url}, Payload reflected in response",
                            impact="Script execution via malicious links",
                            recommendation="Implement proper output encoding and input validation"
                        ))
                        
                except Exception as e:
                    self.log(f"Error testing reflected XSS on {endpoint}: {e}", "ERROR")

    # ==================== CSRF TESTS ====================
    
    def test_csrf_protection(self):
        """Test CSRF protection on state-changing operations"""
        self.log("Testing CSRF protection...")
        
        admin_auth = self._get_admin_auth()
        if not admin_auth:
            self.log("Cannot test CSRF - admin authentication failed", "ERROR")
            return
        
        # Test critical admin operations without CSRF token
        csrf_test_operations = [
            {
                "endpoint": "/admin/status",
                "method": "POST",
                "data": {"status_type": "URLAUB", "date_from": "2024-12-01", "date_to": "2024-12-31"},
                "description": "Status update"
            },
            {
                "endpoint": "/admin/hours", 
                "method": "POST",
                "data": {"monday-closed": "on", "tuesday-start-1": "09:00", "tuesday-end-1": "17:00"},
                "description": "Hours update"
            },
            {
                "endpoint": "/admin/announcements",
                "method": "POST", 
                "data": {"lang": "de", "title": "Test", "body": "Test announcement", "active": "on"},
                "description": "Announcement creation"
            }
        ]
        
        for operation in csrf_test_operations:
            try:
                # Test without CSRF token
                if operation["method"] == "POST":
                    response = self.session.post(
                        f"{self.base_url}{operation['endpoint']}", 
                        data=operation["data"],
                        headers=admin_auth
                    )
                else:
                    response = self.session.request(
                        operation["method"],
                        f"{self.base_url}{operation['endpoint']}",
                        data=operation["data"], 
                        headers=admin_auth
                    )
                
                # If operation succeeded without CSRF token, it's a vulnerability
                if response.status_code == 200 or "success" in response.text.lower():
                    self.add_vulnerability(SecurityVulnerability(
                        category="CSRF",
                        level=VulnerabilityLevel.HIGH,
                        title="Missing CSRF Protection",
                        description=f"CSRF protection missing or bypassable for {operation['description']}",
                        evidence=f"Operation succeeded without CSRF token. Status: {response.status_code}",
                        impact="Attackers can perform unauthorized actions on behalf of authenticated users",
                        recommendation="Implement proper CSRF token validation for all state-changing operations"
                    ))
                    
            except Exception as e:
                self.log(f"Error testing CSRF for {operation['endpoint']}: {e}", "ERROR")

    # ==================== AUTHENTICATION TESTS ====================
    
    def test_authentication_bypass(self):
        """Test authentication bypass techniques"""
        self.log("Testing Authentication Bypass...")
        
        # Test various bypass techniques
        bypass_attempts = [
            # Direct admin panel access
            {"url": "/admin", "method": "GET", "description": "Direct admin access"},
            {"url": "/admin/dashboard", "method": "GET", "description": "Direct dashboard access"},
            
            # Header manipulation
            {"url": "/admin", "method": "GET", "headers": {"X-Forwarded-For": "127.0.0.1"}, "description": "IP spoofing"},
            {"url": "/admin", "method": "GET", "headers": {"X-Real-IP": "localhost"}, "description": "Real IP header manipulation"},
            
            # Session manipulation
            {"url": "/admin", "method": "GET", "cookies": {"session": "admin"}, "description": "Session cookie manipulation"},
        ]
        
        for attempt in bypass_attempts:
            try:
                response = self.session.request(
                    attempt["method"],
                    f"{self.base_url}{attempt['url']}",
                    headers=attempt.get("headers", {}),
                    cookies=attempt.get("cookies", {})
                )
                
                # Check if unauthorized access was granted
                if response.status_code == 200 and ("dashboard" in response.text.lower() or "admin" in response.text.lower()):
                    self.add_vulnerability(SecurityVulnerability(
                        category="AUTHENTICATION_BYPASS",
                        level=VulnerabilityLevel.CRITICAL,
                        title="Authentication Bypass",
                        description=f"Admin panel accessible without authentication via {attempt['description']}",
                        evidence=f"Status: {response.status_code}, Content contains admin interface",
                        impact="Complete unauthorized access to admin functionality",
                        recommendation="Implement proper authentication middleware and session validation"
                    ))
                    
            except Exception as e:
                self.log(f"Error testing auth bypass {attempt['description']}: {e}", "ERROR")

    def test_brute_force_protection(self):
        """Test brute force protection on admin login"""
        self.log("Testing Brute Force Protection...")
        
        failed_attempts = 0
        locked_after = None
        
        # Try multiple failed login attempts
        for i in range(10):
            try:
                auth = base64.b64encode(f"{self.admin_user}:wrongpassword{i}".encode()).decode()
                headers = {"Authorization": f"Basic {auth}"}
                
                start_time = time.time()
                response = self.session.get(f"{self.base_url}/admin", headers=headers)
                response_time = time.time() - start_time
                
                if response.status_code == 401:
                    failed_attempts += 1
                    
                    # Check if response time significantly increased (could indicate rate limiting)
                    if response_time > 2.0 and not locked_after:
                        locked_after = i + 1
                        
                # Small delay between attempts
                time.sleep(0.5)
                
            except Exception as e:
                self.log(f"Error in brute force test attempt {i}: {e}", "ERROR")
        
        # Evaluate brute force protection
        if failed_attempts >= 10:
            if not locked_after or locked_after > 5:
                self.add_vulnerability(SecurityVulnerability(
                    category="BRUTE_FORCE",
                    level=VulnerabilityLevel.MEDIUM,
                    title="Insufficient Brute Force Protection",
                    description="No account lockout or insufficient rate limiting after multiple failed login attempts",
                    evidence=f"Completed {failed_attempts} attempts without lockout",
                    impact="Attackers can perform credential brute force attacks",
                    recommendation="Implement account lockout after 3-5 failed attempts and progressive delays"
                ))

    # ==================== SESSION SECURITY TESTS ====================
    
    def test_session_security(self):
        """Test session cookie security"""
        self.log("Testing Session Security...")
        
        # Get a valid session first
        admin_auth = self._get_admin_auth()
        if admin_auth:
            response = self.session.get(f"{self.base_url}/admin", headers=admin_auth)
            
            # Check session cookie attributes
            for cookie in self.session.cookies:
                if cookie.name.lower() in ['session', 'sessionid', 'auth']:
                    issues = []
                    
                    if not cookie.secure:
                        issues.append("Missing Secure flag")
                    if not cookie.has_nonstandard_attr('HttpOnly'):
                        issues.append("Missing HttpOnly flag")
                    if not cookie.has_nonstandard_attr('SameSite'):
                        issues.append("Missing SameSite attribute")
                        
                    if issues:
                        self.add_vulnerability(SecurityVulnerability(
                            category="SESSION_SECURITY",
                            level=VulnerabilityLevel.MEDIUM,
                            title="Insecure Session Cookie",
                            description=f"Session cookie missing security attributes: {', '.join(issues)}",
                            evidence=f"Cookie: {cookie.name}, Issues: {issues}",
                            impact="Session hijacking via XSS or man-in-the-middle attacks",
                            recommendation="Set Secure, HttpOnly, and SameSite=Lax attributes on session cookies"
                        ))

    # ==================== INPUT VALIDATION TESTS ====================
    
    def test_input_validation(self):
        """Test input validation across all forms"""
        self.log("Testing Input Validation...")
        
        admin_auth = self._get_admin_auth()
        if not admin_auth:
            return
            
        # Test extremely long inputs
        long_string = "A" * 10000
        oversized_payloads = [
            {"field": "description", "value": long_string, "endpoint": "/admin/status"},
            {"field": "title", "value": long_string, "endpoint": "/admin/announcements"},
            {"field": "body", "value": long_string, "endpoint": "/admin/announcements"},
        ]
        
        for payload in oversized_payloads:
            try:
                csrf_token = self._get_csrf_token(admin_auth)
                form_data = {
                    'csrf_token': csrf_token,
                    payload["field"]: payload["value"]
                }
                
                response = self.session.post(
                    f"{self.base_url}{payload['endpoint']}",
                    data=form_data,
                    headers=admin_auth
                )
                
                # If no error occurred, input validation might be missing
                if response.status_code == 200 and "error" not in response.text.lower():
                    self.add_vulnerability(SecurityVulnerability(
                        category="INPUT_VALIDATION",
                        level=VulnerabilityLevel.LOW,
                        title="Insufficient Input Length Validation",
                        description=f"No length validation for {payload['field']} field",
                        evidence=f"Accepted {len(payload['value'])} character input",
                        impact="Potential DoS through large data storage or processing",
                        recommendation="Implement proper input length validation"
                    ))
                    
            except Exception as e:
                self.log(f"Error testing input validation for {payload['field']}: {e}", "ERROR")

    # ==================== AUTHORIZATION TESTS ====================
    
    def test_authorization(self):
        """Test authorization and access control"""
        self.log("Testing Authorization...")
        
        # Test admin endpoints without authentication
        admin_endpoints = [
            "/admin/status",
            "/admin/hours", 
            "/admin/announcements",
            "/admin/availability",
            "/admin/settings"
        ]
        
        for endpoint in admin_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    self.add_vulnerability(SecurityVulnerability(
                        category="AUTHORIZATION",
                        level=VulnerabilityLevel.CRITICAL,
                        title="Missing Authorization",
                        description=f"Admin endpoint accessible without authentication: {endpoint}",
                        evidence=f"Status: {response.status_code}",
                        impact="Unauthorized access to admin functionality",
                        recommendation="Implement proper authentication middleware for all admin routes"
                    ))
                    
            except Exception as e:
                self.log(f"Error testing authorization for {endpoint}: {e}", "ERROR")

    # ==================== DIRECTORY TRAVERSAL TESTS ====================
    
    def test_directory_traversal(self):
        """Test directory traversal vulnerabilities"""
        self.log("Testing Directory Traversal...")
        
        traversal_payloads = [
            "../../etc/passwd",
            "../../../windows/system32/drivers/etc/hosts", 
            "....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2fboot.ini",
            "..\\..\\..\\windows\\win.ini"
        ]
        
        # Test file serving endpoints
        test_endpoints = [
            "/static/",
            "/qr/",
        ]
        
        for endpoint in test_endpoints:
            for payload in traversal_payloads:
                try:
                    url = f"{self.base_url}{endpoint}{payload}"
                    response = self.session.get(url)
                    
                    # Check for successful file access
                    sensitive_patterns = [
                        "root:x:0:0",  # /etc/passwd
                        "[fonts]",      # win.ini
                        "localhost",    # hosts file
                    ]
                    
                    for pattern in sensitive_patterns:
                        if pattern.lower() in response.text.lower():
                            self.add_vulnerability(SecurityVulnerability(
                                category="DIRECTORY_TRAVERSAL",
                                level=VulnerabilityLevel.HIGH,
                                title="Directory Traversal",
                                description=f"Directory traversal successful via {endpoint}",
                                evidence=f"Accessed: {payload}, Pattern found: {pattern}",
                                impact="Unauthorized file system access",
                                recommendation="Implement proper path validation and sanitization"
                            ))
                            
                except Exception as e:
                    self.log(f"Error testing directory traversal {endpoint}{payload}: {e}", "ERROR")

    # ==================== INFORMATION DISCLOSURE TESTS ====================
    
    def test_information_disclosure(self):
        """Test for information disclosure vulnerabilities"""
        self.log("Testing Information Disclosure...")
        
        # Test error handling
        error_inducing_urls = [
            "/nonexistent",
            "/admin/nonexistent", 
            "/qr?target=invalid_url",
            "/month?year=invalid",
            "/week?offset=invalid"
        ]
        
        for url in error_inducing_urls:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                
                # Check for sensitive information in error messages
                sensitive_patterns = [
                    r"/[a-zA-Z0-9_/\-\.]+\.py",  # Python file paths
                    r"Traceback",                # Python tracebacks
                    r"sqlite3\.",               # Database errors
                    r"File \".*?\"",            # File references
                    r"line \d+",                # Line numbers
                    r"SECRET_KEY",              # Configuration keys
                    r"password",                # Password references
                ]
                
                for pattern in sensitive_patterns:
                    matches = re.findall(pattern, response.text, re.IGNORECASE)
                    if matches:
                        self.add_vulnerability(SecurityVulnerability(
                            category="INFORMATION_DISCLOSURE",
                            level=VulnerabilityLevel.MEDIUM,
                            title="Sensitive Information Disclosure",
                            description=f"Error page reveals sensitive information: {pattern}",
                            evidence=f"URL: {url}, Matches: {matches[:3]}",
                            impact="Information useful for further attacks",
                            recommendation="Implement custom error pages without sensitive details"
                        ))
                        
            except Exception as e:
                self.log(f"Error testing information disclosure for {url}: {e}", "ERROR")

    # ==================== SECURITY HEADERS TESTS ====================
    
    def test_security_headers(self):
        """Test security headers"""
        self.log("Testing Security Headers...")
        
        response = self.session.get(f"{self.base_url}/")
        
        # Required security headers
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": None,  # Just check presence
            "Strict-Transport-Security": None,  # For HTTPS
        }
        
        for header, expected_values in required_headers.items():
            header_value = response.headers.get(header)
            
            if not header_value:
                severity = VulnerabilityLevel.MEDIUM if header != "Strict-Transport-Security" else VulnerabilityLevel.LOW
                self.add_vulnerability(SecurityVulnerability(
                    category="SECURITY_HEADERS",
                    level=severity,
                    title=f"Missing Security Header: {header}",
                    description=f"Security header {header} is missing",
                    evidence=f"Header not present in response",
                    impact="Reduced protection against various attacks",
                    recommendation=f"Add {header} header with appropriate value"
                ))
            elif expected_values and isinstance(expected_values, list):
                if header_value not in expected_values:
                    self.add_vulnerability(SecurityVulnerability(
                        category="SECURITY_HEADERS",
                        level=VulnerabilityLevel.LOW,
                        title=f"Suboptimal Security Header: {header}",
                        description=f"Security header {header} has suboptimal value: {header_value}",
                        evidence=f"Expected: {expected_values}, Got: {header_value}",
                        impact="Reduced security protection",
                        recommendation=f"Set {header} to one of: {expected_values}"
                    ))

    # ==================== RATE LIMITING TESTS ====================
    
    def test_rate_limiting(self):
        """Test rate limiting on critical endpoints"""
        self.log("Testing Rate Limiting...")
        
        # Test endpoints that should have rate limiting
        rate_limit_endpoints = [
            "/qr",
            "/qr.svg",
            "/admin/status",
            "/set-language/de"
        ]
        
        admin_auth = self._get_admin_auth()
        
        for endpoint in rate_limit_endpoints:
            try:
                # Make rapid requests to trigger rate limiting
                requests_made = 0
                rate_limited = False
                
                for i in range(50):  # Try 50 rapid requests
                    headers = admin_auth if endpoint.startswith('/admin') else {}
                    response = self.session.get(f"{self.base_url}{endpoint}", headers=headers)
                    requests_made += 1
                    
                    if response.status_code == 429:  # Too Many Requests
                        rate_limited = True
                        break
                        
                    time.sleep(0.1)  # Small delay
                
                if not rate_limited:
                    self.add_vulnerability(SecurityVulnerability(
                        category="RATE_LIMITING",
                        level=VulnerabilityLevel.MEDIUM,
                        title="Missing Rate Limiting",
                        description=f"No rate limiting on {endpoint}",
                        evidence=f"Completed {requests_made} requests without rate limiting",
                        impact="Potential DoS attacks and resource abuse",
                        recommendation="Implement rate limiting for resource-intensive endpoints"
                    ))
                    
            except Exception as e:
                self.log(f"Error testing rate limiting for {endpoint}: {e}", "ERROR")

    # ==================== HELPER METHODS ====================
    
    def _get_admin_auth(self) -> Optional[Dict[str, str]]:
        """Get admin authentication headers"""
        try:
            auth = base64.b64encode(f"{self.admin_user}:{self.admin_pass}".encode()).decode()
            headers = {"Authorization": f"Basic {auth}"}
            
            # Test if auth works
            response = self.session.get(f"{self.base_url}/admin", headers=headers)
            if response.status_code == 200:
                return headers
            else:
                self.log("Admin authentication failed", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Error getting admin auth: {e}", "ERROR")
            return None
    
    def _get_csrf_token(self, auth_headers: Dict[str, str]) -> Optional[str]:
        """Extract CSRF token from admin page"""
        try:
            response = self.session.get(f"{self.base_url}/admin", headers=auth_headers)
            
            # Look for CSRF token in HTML
            csrf_patterns = [
                r'name="csrf_token" value="([^"]*)"',
                r'"csrf_token": "([^"]*)"',
                r'csrf_token: "([^"]*)"'
            ]
            
            for pattern in csrf_patterns:
                match = re.search(pattern, response.text)
                if match:
                    return match.group(1)
                    
            return None
            
        except Exception as e:
            self.log(f"Error getting CSRF token: {e}", "ERROR")
            return None

    # ==================== MAIN TEST EXECUTION ====================
    
    def run_security_tests(self):
        """Run complete security test suite"""
        self.log("=== STARTING COMPREHENSIVE SECURITY AUDIT ===")
        
        start_time = datetime.now()
        
        try:
            # Test if application is running
            response = self.session.get(f"{self.base_url}/healthz")
            if response.status_code != 200:
                self.log("Application not running or health check failed", "ERROR")
                return
                
        except Exception as e:
            self.log(f"Cannot connect to application: {e}", "ERROR")
            return
        
        # Execute all security tests
        test_methods = [
            self.test_sql_injection_authentication,
            self.test_sql_injection_parameters, 
            self.test_xss_stored,
            self.test_xss_reflected,
            self.test_csrf_protection,
            self.test_authentication_bypass,
            self.test_brute_force_protection,
            self.test_session_security,
            self.test_input_validation,
            self.test_authorization,
            self.test_directory_traversal,
            self.test_information_disclosure,
            self.test_security_headers,
            self.test_rate_limiting
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log(f"Error in test {test_method.__name__}: {e}", "ERROR")
        
        end_time = datetime.now()
        
        # Generate summary
        self.generate_security_report(start_time, end_time)
    
    def generate_security_report(self, start_time: datetime, end_time: datetime):
        """Generate comprehensive security assessment report"""
        duration = (end_time - start_time).total_seconds()
        
        # Count vulnerabilities by severity
        severity_counts = {level: 0 for level in VulnerabilityLevel}
        for vuln in self.vulnerabilities:
            severity_counts[vuln.level] += 1
        
        # Calculate security score
        total_tests = 14  # Number of test categories
        critical_weight = 10
        high_weight = 5
        medium_weight = 2
        low_weight = 1
        
        penalty_score = (
            severity_counts[VulnerabilityLevel.CRITICAL] * critical_weight +
            severity_counts[VulnerabilityLevel.HIGH] * high_weight +
            severity_counts[VulnerabilityLevel.MEDIUM] * medium_weight +
            severity_counts[VulnerabilityLevel.LOW] * low_weight
        )
        
        max_score = 100
        security_score = max(0, max_score - penalty_score)
        
        # Generate report
        report = {
            "security_assessment": {
                "timestamp": datetime.now().isoformat(),
                "test_duration_seconds": duration,
                "target": self.base_url,
                "security_score": security_score,
                "risk_level": self._calculate_risk_level(security_score),
            },
            "vulnerability_summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "critical": severity_counts[VulnerabilityLevel.CRITICAL],
                "high": severity_counts[VulnerabilityLevel.HIGH], 
                "medium": severity_counts[VulnerabilityLevel.MEDIUM],
                "low": severity_counts[VulnerabilityLevel.LOW],
                "info": severity_counts[VulnerabilityLevel.INFO]
            },
            "vulnerabilities": [
                {
                    "category": v.category,
                    "level": v.level.value,
                    "title": v.title,
                    "description": v.description,
                    "evidence": v.evidence,
                    "impact": v.impact,
                    "recommendation": v.recommendation,
                    "cve_reference": v.cve_reference,
                    "exploit_scenario": v.exploit_scenario
                }
                for v in self.vulnerabilities
            ],
            "security_recommendations": self._generate_recommendations()
        }
        
        # Save report
        report_file = f"security_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"Security assessment completed. Score: {security_score}/100")
        self.log(f"Found {len(self.vulnerabilities)} vulnerabilities")
        self.log(f"Report saved to: {report_file}")
        
        return report
    
    def _calculate_risk_level(self, score: int) -> str:
        """Calculate overall risk level based on score"""
        if score >= 90:
            return "LOW"
        elif score >= 70:
            return "MEDIUM"
        elif score >= 50:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate prioritized security recommendations"""
        recommendations = []
        
        # Check for critical vulnerabilities
        if any(v.level == VulnerabilityLevel.CRITICAL for v in self.vulnerabilities):
            recommendations.append("IMMEDIATE ACTION REQUIRED: Critical vulnerabilities found")
        
        # Category-specific recommendations
        categories = set(v.category for v in self.vulnerabilities)
        
        if "SQL_INJECTION" in categories:
            recommendations.append("Implement parameterized queries and input validation")
        if "XSS_STORED" in categories or "XSS_REFLECTED" in categories:
            recommendations.append("Implement proper output encoding and CSP headers")
        if "CSRF" in categories:
            recommendations.append("Strengthen CSRF protection mechanisms")
        if "AUTHENTICATION_BYPASS" in categories:
            recommendations.append("Review and strengthen authentication implementation")
        if "AUTHORIZATION" in categories:
            recommendations.append("Implement proper access controls for admin functions")
            
        return recommendations


def main():
    """Run security tests"""
    tester = QRPortalSecurityTester()
    report = tester.run_security_tests()
    
    # Print summary
    print("\n" + "="*60)
    print("SECURITY ASSESSMENT SUMMARY")
    print("="*60)
    print(f"Security Score: {report['security_assessment']['security_score']}/100")
    print(f"Risk Level: {report['security_assessment']['risk_level']}")
    print(f"Total Vulnerabilities: {report['vulnerability_summary']['total_vulnerabilities']}")
    print(f"Critical: {report['vulnerability_summary']['critical']}")
    print(f"High: {report['vulnerability_summary']['high']}")
    print(f"Medium: {report['vulnerability_summary']['medium']}")
    print(f"Low: {report['vulnerability_summary']['low']}")
    print("="*60)

if __name__ == "__main__":
    main()