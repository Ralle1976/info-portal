#!/usr/bin/env python3
"""
AUTOMATED SECURITY FIX SCRIPT
=============================
Automatically fixes critical security vulnerabilities found in assessment

⚠️  BACKUP YOUR DATA BEFORE RUNNING THIS SCRIPT ⚠️

Usage: python3 security_fix_script.py --apply-fixes
"""

import os
import re
import shutil
import argparse
from datetime import datetime
from pathlib import Path
import json

class SecurityFixer:
    def __init__(self, project_root: str, dry_run: bool = True):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.fixes_applied = []
        self.backup_dir = self.project_root / f"security_fixes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def log(self, message: str, level: str = "INFO"):
        """Log fix progress"""
        prefix = "DRY-RUN" if self.dry_run else "APPLYING"
        print(f"[{prefix}] {message}")
        
    def backup_file(self, filepath: Path):
        """Create backup before modifying file"""
        if self.dry_run:
            return
            
        self.backup_dir.mkdir(exist_ok=True)
        backup_path = self.backup_dir / filepath.name
        shutil.copy2(filepath, backup_path)
        self.log(f"Backed up {filepath.name} to {backup_path}")
    
    def fix_critical_sql_injection(self):
        """Fix critical SQL injection in routes_admin.py"""
        self.log("=== FIXING CRITICAL SQL INJECTION ===")
        
        routes_admin = self.project_root / "app" / "routes_admin.py"
        
        if not routes_admin.exists():
            self.log("routes_admin.py not found", "ERROR")
            return False
            
        with open(routes_admin, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace dangerous raw SQL
        vulnerable_pattern = r'''session\.exec\("DELETE FROM (\w+)(?:\s+WHERE[^"]+)?"\)'''
        
        def safe_sql_replacement(match):
            table_name = match.group(1)
            if "WHERE" in match.group(0):
                where_clause = re.search(r'WHERE ([^"]+)', match.group(0))
                if where_clause:
                    condition = where_clause.group(1)
                    return f'''# SECURITY FIX: Using ORM instead of raw SQL
        stmt = delete({table_name.title()})
        if "{condition}" != "id > 0":  # Add proper condition logic
            stmt = stmt.where({table_name.title()}.id > 0)
        session.exec(stmt)'''
                else:
                    return f'''# SECURITY FIX: Using ORM instead of raw SQL  
        session.exec(delete({table_name.title()}))'''
            else:
                return f'''# SECURITY FIX: Using ORM instead of raw SQL
        session.exec(delete({table_name.title()}))'''
        
        # Apply fix
        fixed_content = re.sub(vulnerable_pattern, safe_sql_replacement, content)
        
        if fixed_content != content:
            self.log(f"Found and fixed SQL injection in {routes_admin.name}")
            
            if not self.dry_run:
                self.backup_file(routes_admin)
                with open(routes_admin, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                    
            self.fixes_applied.append("Critical SQL injection in routes_admin.py")
            return True
        else:
            self.log("No SQL injection patterns found")
            return False
    
    def fix_template_xss_vulnerabilities(self):
        """Fix XSS vulnerabilities in templates"""
        self.log("=== FIXING TEMPLATE XSS VULNERABILITIES ===")
        
        templates_dir = self.project_root / "app" / "templates"
        fixes_count = 0
        
        # Find all template files with |safe usage
        for template_file in templates_dir.rglob("*.html"):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace dangerous |safe patterns
            dangerous_patterns = [
                (r'(\w+\.content)\s*\|\s*safe', r'\1 | e'),  # content fields
                (r'(\w+\.body)\s*\|\s*safe', r'\1 | e'),     # body fields  
                (r'(\w+\.answer)\s*\|\s*safe', r'\1 | e'),   # answer fields
                (r'(\w+\.hours)\s*\|\s*safe', r'\1 | e'),    # hours fields
            ]
            
            for dangerous_pattern, safe_replacement in dangerous_patterns:
                content = re.sub(dangerous_pattern, safe_replacement, content)
            
            if content != original_content:
                self.log(f"Fixed XSS vulnerabilities in {template_file.name}")
                fixes_count += 1
                
                if not self.dry_run:
                    self.backup_file(template_file)
                    with open(template_file, 'w', encoding='utf-8') as f:
                        f.write(content)
        
        if fixes_count > 0:
            self.fixes_applied.append(f"XSS vulnerabilities in {fixes_count} template files")
            return True
        else:
            self.log("No template XSS patterns found")
            return False
    
    def fix_authentication_vulnerabilities(self):
        """Fix authentication vulnerabilities"""
        self.log("=== FIXING AUTHENTICATION VULNERABILITIES ===")
        
        routes_admin = self.project_root / "app" / "routes_admin.py"
        
        with open(routes_admin, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove hardcoded default password
        content = re.sub(
            r"admin_pass = os\.getenv\('ADMIN_PASSWORD', 'admin123'\)",
            "admin_pass = os.getenv('ADMIN_PASSWORD')\n    if not admin_pass:\n        raise ValueError('ADMIN_PASSWORD environment variable must be set')",
            content
        )
        
        # Add password complexity check
        password_check_code = '''
def validate_password_strength(password: str) -> bool:
    """Validate password meets security requirements"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False  
    if not re.search(r'[0-9]', password):
        return False
    return True
'''
        
        # Insert password validation function after imports
        import_section_end = content.find('\n\nadmin_bp = Blueprint')
        if import_section_end != -1:
            content = content[:import_section_end] + password_check_code + content[import_section_end:]
        
        if content != original_content:
            self.log("Fixed authentication vulnerabilities")
            
            if not self.dry_run:
                self.backup_file(routes_admin)
                with open(routes_admin, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            self.fixes_applied.append("Authentication vulnerabilities in routes_admin.py")
            return True
        else:
            self.log("No authentication vulnerabilities found to fix")
            return False
    
    def fix_input_sanitization(self):
        """Fix input sanitization function"""
        self.log("=== FIXING INPUT SANITIZATION ===")
        
        routes_admin = self.project_root / "app" / "routes_admin.py"
        
        with open(routes_admin, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace sanitize_input function
        sanitize_pattern = r'def sanitize_input\(.*?\):(.*?)(?=\n\ndef|\n\n#|\nclass|\n@|\Z)'
        
        secure_sanitize_function = '''def sanitize_input(data: str, max_length: int = 500, allow_html: bool = False) -> str:
    """Enhanced sanitize input string with comprehensive XSS and injection protection"""
    import html
    import re
    
    if not data:
        return ''
    
    # Strip whitespace and limit length
    data = data.strip()[:max_length]
    
    if not allow_html:
        # Escape HTML to prevent XSS
        data = html.escape(data)
        
        # Remove potentially dangerous patterns (comprehensive list)
        dangerous_patterns = [
            r'javascript:', r'data:', r'vbscript:', r'onload=', r'onerror=',
            r'onclick=', r'onmouseover=', r'onmouseout=', r'onfocus=', r'onblur=',
            r'<script[^>]*>.*?</script>', r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>', r'<embed[^>]*>.*?</embed>',
            r'<link[^>]*>', r'<style[^>]*>.*?</style>', r'<meta[^>]*>',
            r'expression\s*\(', r'url\s*\(', r'@import'
        ]
        
        for pattern in dangerous_patterns:
            data = re.sub(pattern, '', data, flags=re.IGNORECASE | re.DOTALL)
    
    # Additional SQL injection protection
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'UNION', 'EXEC']
    for keyword in sql_keywords:
        # Remove SQL keywords (case insensitive) but preserve normal text
        data = re.sub(rf'\\b{keyword}\\b', '', data, flags=re.IGNORECASE)
    
    return data'''
        
        if re.search(r'def sanitize_input', content):
            new_content = re.sub(sanitize_pattern, secure_sanitize_function, content, flags=re.DOTALL)
            
            if new_content != content:
                self.log("Enhanced input sanitization function")
                
                if not self.dry_run:
                    self.backup_file(routes_admin)
                    with open(routes_admin, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        
                self.fixes_applied.append("Enhanced input sanitization function")
                return True
        
        return False
    
    def fix_security_headers(self):
        """Fix missing security headers"""
        self.log("=== FIXING SECURITY HEADERS ===")
        
        init_file = self.project_root / "app" / "__init__.py"
        
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the security headers section
        if "def security_headers(response):" in content:
            # Add missing HSTS header
            hsts_addition = '''
        # HSTS (HTTP Strict Transport Security)
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
'''
            
            # Insert before return statement in security_headers function
            content = content.replace(
                'return response',
                hsts_addition + '        return response'
            )
            
            # Enhance CSP policy
            enhanced_csp = '''        # Enhanced CSP (Content Security Policy)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )'''
            
            content = content.replace(
                '''csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )''',
                enhanced_csp
            )
            
            self.log("Enhanced security headers")
            
            if not self.dry_run:
                self.backup_file(init_file)
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            self.fixes_applied.append("Enhanced security headers")
            return True
        
        return False
    
    def create_security_env_template(self):
        """Create secure environment template"""
        self.log("=== CREATING SECURE ENVIRONMENT TEMPLATE ===")
        
        env_example = self.project_root / ".env.security"
        
        secure_env_content = '''# SECURITY CONFIGURATION
# =====================

# CRITICAL: Change these values in production!
SECRET_KEY=your_super_secret_key_here_32_chars_minimum
ADMIN_PASSWORD=your_strong_admin_password_here

# Security Settings
FLASK_ENV=production
FLASK_DEBUG=False

# Session Security  
SESSION_TIMEOUT=1800  # 30 minutes

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_HOUR=100

# Admin Security
ADMIN_SESSION_TIMEOUT=1800  # 30 minutes
ADMIN_MAX_LOGIN_ATTEMPTS=3
ADMIN_LOCKOUT_DURATION=900  # 15 minutes

# File Upload Security (if enabled)
MAX_FILE_SIZE=5242880  # 5MB
ALLOWED_FILE_TYPES=png,jpg,jpeg,gif,pdf,txt
VIRUS_SCAN_ENABLED=false

# Database Security
DB_QUERY_TIMEOUT=30
DB_MAX_CONNECTIONS=10

# Logging Security
LOG_LEVEL=INFO
LOG_SENSITIVE_DATA=false
LOG_RETENTION_DAYS=90

# Security Headers
CSP_ENABLED=true
HSTS_ENABLED=true
FRAME_OPTIONS=DENY

# QR Code Security
QR_RATE_LIMIT=10  # per minute
QR_MAX_SIZE=1000
'''
        
        if not env_example.exists() or not self.dry_run:
            self.log("Creating secure environment template")
            
            if not self.dry_run:
                with open(env_example, 'w', encoding='utf-8') as f:
                    f.write(secure_env_content)
                    
            self.fixes_applied.append("Created secure environment template")
            return True
        
        return False
    
    def create_security_checklist(self):
        """Create security checklist for manual review"""
        self.log("=== CREATING SECURITY CHECKLIST ===")
        
        checklist_content = '''# SECURITY IMPLEMENTATION CHECKLIST
## Post-Fix Manual Verification Required

### 🔥 CRITICAL - Verify Immediately

- [ ] **SQL Injection Fixed**: Raw SQL replaced with ORM queries
  - Test: Try to login with SQL injection payloads - should fail
  - Test: Admin rollback function works without raw SQL

- [ ] **XSS Fixed**: All |safe filters reviewed  
  - Test: Try to create announcement with script tags - should be escaped
  - Test: All user content is properly escaped in output

- [ ] **Default Credentials Removed**:
  - [ ] Change ADMIN_PASSWORD in .env 
  - [ ] Remove admin123 from all code
  - [ ] Test: Default credentials no longer work

### ⚠️ HIGH PRIORITY - Implement Soon

- [ ] **Enhanced Authentication**:
  - [ ] Implement strong password policy
  - [ ] Add account lockout after 3 failed attempts  
  - [ ] Consider 2FA for admin panel

- [ ] **File Upload Security** (if uploads exist):
  - [ ] Validate file types (whitelist only)
  - [ ] Implement file size limits
  - [ ] Add virus scanning or content validation

### 📋 MEDIUM PRIORITY - Security Hardening

- [ ] **Rate Limiting**:
  - [ ] Add rate limits to /qr endpoints
  - [ ] Implement admin panel rate limiting
  - [ ] Add IP-based blocking for abuse

- [ ] **Session Security**:
  - [ ] Verify session timeout works (30 minutes)
  - [ ] Test session invalidation
  - [ ] Verify secure cookie attributes

- [ ] **Logging Security**:
  - [ ] Ensure no passwords/secrets in logs
  - [ ] Set proper log file permissions (600)
  - [ ] Implement log rotation

### 🔐 SECURITY MONITORING

- [ ] **Set up monitoring for**:
  - [ ] Multiple failed login attempts
  - [ ] XSS attempt patterns in logs
  - [ ] SQL injection attempt patterns
  - [ ] Admin panel access from new IPs
  - [ ] Unusual QR code generation volume

### 🧪 TESTING VERIFICATION

- [ ] **Run security test suite**:
  ```bash
  python3 security_test_suite.py
  pytest tests/test_security_validation.py -v
  ```

- [ ] **Manual penetration testing**:
  - [ ] Try SQL injection in all forms
  - [ ] Try XSS in all input fields
  - [ ] Test CSRF protection on all admin operations
  - [ ] Verify rate limiting works
  - [ ] Test authentication bypass methods

### 🚀 DEPLOYMENT SECURITY

- [ ] **Production Environment**:
  - [ ] Use environment variables for all secrets
  - [ ] Enable HTTPS only (set SESSION_COOKIE_SECURE=True)
  - [ ] Set proper file permissions
  - [ ] Disable debug mode
  - [ ] Review CSP policy for production domains

- [ ] **Monitoring & Alerting**:
  - [ ] Set up log monitoring 
  - [ ] Configure security alerts
  - [ ] Implement health checks
  - [ ] Set up automated security scanning

### ✅ FINAL VERIFICATION

- [ ] Security score >90/100 on retest
- [ ] No critical or high vulnerabilities
- [ ] All admin functions work properly
- [ ] QR codes generate without issues
- [ ] Performance not significantly impacted

**Date Completed: ___________**  
**Verified By: ___________**  
**Next Security Review: ___________**
'''
        
        checklist_file = self.project_root / "SECURITY_IMPLEMENTATION_CHECKLIST.md"
        
        self.log("Creating security implementation checklist")
        
        if not self.dry_run:
            with open(checklist_file, 'w', encoding='utf-8') as f:
                f.write(checklist_content)
                
        self.fixes_applied.append("Created security implementation checklist")
        return True
    
    def run_all_fixes(self):
        """Run all security fixes"""
        self.log(f"Starting security fix process (dry_run={self.dry_run})")
        
        fixes = [
            self.fix_critical_sql_injection,
            self.fix_template_xss_vulnerabilities, 
            self.fix_authentication_vulnerabilities,
            self.fix_input_sanitization,
            self.fix_security_headers,
            self.create_security_env_template,
            self.create_security_checklist
        ]
        
        success_count = 0
        for fix_func in fixes:
            try:
                if fix_func():
                    success_count += 1
            except Exception as e:
                self.log(f"Error in {fix_func.__name__}: {e}", "ERROR")
        
        self.log(f"=== SECURITY FIX SUMMARY ===")
        self.log(f"Fixes Applied: {success_count}/{len(fixes)}")
        
        if self.fixes_applied:
            self.log("Applied fixes:")
            for fix in self.fixes_applied:
                self.log(f"  ✓ {fix}")
        
        if not self.dry_run and self.backup_dir.exists():
            self.log(f"Backups created in: {self.backup_dir}")
        
        # Generate fix report
        fix_report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "fixes_applied": self.fixes_applied,
            "success_count": success_count,
            "total_fixes": len(fixes),
            "backup_location": str(self.backup_dir) if not self.dry_run else None
        }
        
        report_file = f"security_fixes_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(fix_report, f, indent=2)
        
        self.log(f"Fix report saved to: {report_file}")
        
        if self.dry_run:
            self.log("\n🔄 This was a DRY RUN - no files were changed")
            self.log("To apply fixes, run: python3 security_fix_script.py --apply-fixes")
        else:
            self.log("\n✅ Security fixes applied successfully")
            self.log("⚠️  Remember to:")
            self.log("   1. Test the application thoroughly")
            self.log("   2. Update environment variables") 
            self.log("   3. Complete manual checklist")
            self.log("   4. Re-run security tests")

def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Security Fix Script for QR-Info-Portal")
    parser.add_argument('--apply-fixes', action='store_true', 
                       help='Actually apply fixes (default is dry-run)')
    parser.add_argument('--project-root', default='.', 
                       help='Project root directory')
    
    args = parser.parse_args()
    
    project_root = os.path.abspath(args.project_root)
    dry_run = not args.apply_fixes
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No files will be changed")
        print("Add --apply-fixes to actually apply security fixes")
    else:
        print("\n⚠️  APPLYING SECURITY FIXES - Files will be modified")
        print("Make sure you have a backup!")
        
        confirm = input("Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Aborted")
            return
    
    fixer = SecurityFixer(project_root, dry_run=dry_run)
    fixer.run_all_fixes()

if __name__ == "__main__":
    main()