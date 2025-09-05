#!/usr/bin/env python3
"""
QR Info Portal - Advanced Testing Suite
Comprehensive testing without external dependencies using built-in Python modules
"""

import os
import sys
import json
import time
import base64
import hashlib
import requests
import subprocess
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
import sqlite3
import threading
import signal
import logging

class AdvancedTestingSuite:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.results = []
        self.test_data_dir = "test_data"
        self.screenshots_dir = "visual_tests"
        self.reports_dir = "reports"
        self.logs_dir = "logs"
        
        # Create directories
        for directory in [self.test_data_dir, self.screenshots_dir, self.reports_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.logs_dir, 'testing.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.server_process = None
        self.monitoring_active = False
    
    def start_server_monitoring(self):
        """Start continuous server monitoring in background"""
        self.monitoring_active = True
        
        def monitor():
            while self.monitoring_active:
                try:
                    response = requests.get(f"{self.base_url}/healthz", timeout=5)
                    if response.status_code != 200:
                        self.logger.warning(f"Server health check failed: {response.status_code}")
                        self.restart_server()
                except Exception as e:
                    self.logger.error(f"Server monitoring error: {e}")
                    self.restart_server()
                time.sleep(30)  # Check every 30 seconds
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        self.logger.info("Server monitoring started")
    
    def restart_server(self):
        """Attempt to restart the Flask server"""
        self.logger.info("Attempting server restart...")
        try:
            # Kill existing server processes
            subprocess.run(["pkill", "-f", "flask"], capture_output=True)
            subprocess.run(["pkill", "-f", "python.*app"], capture_output=True)
            time.sleep(2)
            
            # Start new server
            env = os.environ.copy()
            env['FLASK_APP'] = 'app'
            env['FLASK_ENV'] = 'development'
            
            self.server_process = subprocess.Popen(
                ["python3", "-m", "flask", "run", "--host", "0.0.0.0", "--port", "5000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd="/mnt/c/Users/tango/Desktop/Homepage/qr-info-portal"
            )
            
            # Wait for server to start
            time.sleep(5)
            self.logger.info("Server restart completed")
            
        except Exception as e:
            self.logger.error(f"Server restart failed: {e}")
    
    def test_visual_regression(self, page_path):
        """Test for visual changes by comparing HTML structure hashes"""
        try:
            response = requests.get(urljoin(self.base_url, page_path), timeout=10)
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}"}
            
            # Create structural hash (simplified visual regression)
            html = response.text
            
            # Extract key visual elements
            parser = VisualElementParser()
            parser.feed(html)
            
            visual_signature = {
                "title": parser.title,
                "headings": parser.headings,
                "nav_items": parser.nav_items,
                "form_elements": parser.form_elements,
                "images": parser.images,
                "structure_hash": hashlib.md5(html.encode()).hexdigest()[:16]
            }
            
            # Save current signature
            signature_file = os.path.join(self.test_data_dir, f"{page_path.replace('/', '_')}_signature.json")
            
            result = {
                "page": page_path,
                "timestamp": datetime.now().isoformat(),
                "visual_signature": visual_signature,
                "changed": False,
                "changes": []
            }
            
            # Compare with previous signature
            if os.path.exists(signature_file):
                with open(signature_file, 'r') as f:
                    prev_signature = json.load(f)
                
                # Check for changes
                changes = []
                if prev_signature["structure_hash"] != visual_signature["structure_hash"]:
                    changes.append("HTML structure changed")
                
                if prev_signature["title"] != visual_signature["title"]:
                    changes.append(f"Title changed: '{prev_signature['title']}' → '{visual_signature['title']}'")
                
                if len(prev_signature["headings"]) != len(visual_signature["headings"]):
                    changes.append(f"Headings count changed: {len(prev_signature['headings'])} → {len(visual_signature['headings'])}")
                
                if len(prev_signature["nav_items"]) != len(visual_signature["nav_items"]):
                    changes.append(f"Navigation items changed: {len(prev_signature['nav_items'])} → {len(visual_signature['nav_items'])}")
                
                result["changed"] = len(changes) > 0
                result["changes"] = changes
            
            # Save current signature
            with open(signature_file, 'w') as f:
                json.dump(visual_signature, f, indent=2)
            
            return result
            
        except Exception as e:
            return {"error": str(e), "page": page_path}
    
    def test_admin_functionality(self):
        """Test admin interface functionality"""
        admin_tests = []
        
        # Test admin login page
        try:
            response = requests.get(urljoin(self.base_url, "/admin/"))
            admin_tests.append({
                "test": "Admin login page access",
                "status": "pass" if response.status_code == 401 else "fail",
                "expected": 401,
                "actual": response.status_code
            })
        except Exception as e:
            admin_tests.append({
                "test": "Admin login page access",
                "status": "error",
                "error": str(e)
            })
        
        # Test admin with basic auth (if credentials available)
        if os.getenv('ADMIN_USERNAME') and os.getenv('ADMIN_PASSWORD'):
            try:
                auth = (os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD'))
                response = requests.get(urljoin(self.base_url, "/admin/"), auth=auth)
                admin_tests.append({
                    "test": "Admin authentication",
                    "status": "pass" if response.status_code == 200 else "fail",
                    "expected": 200,
                    "actual": response.status_code
                })
            except Exception as e:
                admin_tests.append({
                    "test": "Admin authentication",
                    "status": "error",
                    "error": str(e)
                })
        
        return admin_tests
    
    def test_database_integrity(self):
        """Test database integrity and structure"""
        db_tests = []
        
        try:
            # Check if database file exists
            db_file = "instance/portal.db"  # Adjust path as needed
            if os.path.exists(db_file):
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Check tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                db_tests.append({
                    "test": "Database tables exist",
                    "status": "pass" if len(tables) > 0 else "fail",
                    "tables_found": tables
                })
                
                # Check for critical tables (adjust based on your schema)
                expected_tables = ['status', 'opening_hours', 'announcements']
                missing_tables = [t for t in expected_tables if t not in tables]
                
                db_tests.append({
                    "test": "Critical tables present",
                    "status": "pass" if len(missing_tables) == 0 else "fail",
                    "missing_tables": missing_tables
                })
                
                conn.close()
            else:
                db_tests.append({
                    "test": "Database file exists",
                    "status": "fail",
                    "error": f"Database file not found: {db_file}"
                })
                
        except Exception as e:
            db_tests.append({
                "test": "Database connectivity",
                "status": "error",
                "error": str(e)
            })
        
        return db_tests
    
    def test_mobile_responsive(self):
        """Test mobile responsiveness by checking viewport meta and CSS"""
        mobile_tests = []
        
        pages = ["/", "/week", "/month", "/kiosk/single"]
        
        for page in pages:
            try:
                response = requests.get(urljoin(self.base_url, page), timeout=10)
                html = response.text
                
                # Check viewport meta tag
                has_viewport = 'name="viewport"' in html
                
                # Check for responsive CSS classes (Tailwind)
                has_responsive_classes = any(cls in html for cls in ['sm:', 'md:', 'lg:', 'xl:', 'responsive'])
                
                # Check for mobile-friendly elements
                has_mobile_nav = 'mobile' in html.lower() or 'hamburger' in html.lower()
                
                mobile_tests.append({
                    "page": page,
                    "viewport_meta": has_viewport,
                    "responsive_css": has_responsive_classes,
                    "mobile_nav": has_mobile_nav,
                    "score": sum([has_viewport, has_responsive_classes]) / 2
                })
                
            except Exception as e:
                mobile_tests.append({
                    "page": page,
                    "error": str(e)
                })
        
        return mobile_tests
    
    def run_comprehensive_tests(self):
        """Run all available tests"""
        self.logger.info("Starting comprehensive testing suite...")
        
        # Start server monitoring
        self.start_server_monitoring()
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "base_url": self.base_url,
                "python_version": sys.version,
                "platform": sys.platform
            },
            "tests": {}
        }
        
        # Visual regression tests
        self.logger.info("Running visual regression tests...")
        pages = ["/", "/week", "/month", "/kiosk/single", "/kiosk/triple"]
        visual_results = []
        
        for page in pages:
            result = self.test_visual_regression(page)
            visual_results.append(result)
            if result.get("changed"):
                self.logger.warning(f"Visual changes detected on {page}: {result['changes']}")
        
        test_results["tests"]["visual_regression"] = visual_results
        
        # Admin functionality tests
        self.logger.info("Testing admin functionality...")
        test_results["tests"]["admin_functionality"] = self.test_admin_functionality()
        
        # Database integrity tests
        self.logger.info("Testing database integrity...")
        test_results["tests"]["database_integrity"] = self.test_database_integrity()
        
        # Mobile responsiveness tests
        self.logger.info("Testing mobile responsiveness...")
        test_results["tests"]["mobile_responsive"] = self.test_mobile_responsive()
        
        # Save comprehensive results
        results_file = os.path.join(self.reports_dir, "comprehensive_test_results.json")
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        # Generate HTML report
        self.generate_comprehensive_report(test_results)
        
        self.monitoring_active = False
        self.logger.info("Comprehensive testing completed")
        
        return test_results
    
    def generate_comprehensive_report(self, results):
        """Generate comprehensive HTML report"""
        html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <title>QR Info Portal - Comprehensive Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; }}
        .test-section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
        .pass {{ color: #22c55e; font-weight: bold; }}
        .fail {{ color: #ef4444; font-weight: bold; }}
        .error {{ color: #f97316; font-weight: bold; }}
        .warning {{ color: #eab308; font-weight: bold; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 8px; min-width: 150px; text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .changes {{ background: #fef3c7; padding: 10px; border-left: 4px solid #f59e0b; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 QR Info Portal - Comprehensive Test Report</h1>
            <p>Generated: {results['timestamp']}</p>
            <p>Base URL: {results['server_info']['base_url']}</p>
        </div>
"""
        
        # Visual Regression Section
        if 'visual_regression' in results['tests']:
            html_report += """
        <div class="test-section">
            <h2>🎨 Visual Regression Tests</h2>
            <table>
                <tr><th>Page</th><th>Status</th><th>Changes</th><th>Structure Hash</th></tr>
"""
            
            for result in results['tests']['visual_regression']:
                if 'error' in result:
                    status = '<span class="error">ERROR</span>'
                    changes = result.get('error', '')
                    structure_hash = 'N/A'
                else:
                    status = '<span class="warning">CHANGED</span>' if result.get('changed') else '<span class="pass">STABLE</span>'
                    changes = ', '.join(result.get('changes', [])) if result.get('changes') else 'None'
                    structure_hash = result['visual_signature']['structure_hash']
                
                html_report += f"""
                <tr>
                    <td>{result.get('page', 'Unknown')}</td>
                    <td>{status}</td>
                    <td>{changes}</td>
                    <td><code>{structure_hash}</code></td>
                </tr>
"""
            
            html_report += "</table></div>"
        
        # Admin Functionality Section
        if 'admin_functionality' in results['tests']:
            html_report += """
        <div class="test-section">
            <h2>🔐 Admin Functionality Tests</h2>
            <table>
                <tr><th>Test</th><th>Status</th><th>Details</th></tr>
"""
            
            for test in results['tests']['admin_functionality']:
                status_class = test['status']
                status_text = test['status'].upper()
                details = f"Expected: {test.get('expected', 'N/A')}, Actual: {test.get('actual', 'N/A')}"
                if 'error' in test:
                    details = test['error']
                
                html_report += f"""
                <tr>
                    <td>{test['test']}</td>
                    <td><span class="{status_class}">{status_text}</span></td>
                    <td>{details}</td>
                </tr>
"""
            
            html_report += "</table></div>"
        
        # Database Integrity Section
        if 'database_integrity' in results['tests']:
            html_report += """
        <div class="test-section">
            <h2>🗄️ Database Integrity Tests</h2>
            <table>
                <tr><th>Test</th><th>Status</th><th>Details</th></tr>
"""
            
            for test in results['tests']['database_integrity']:
                status_class = test['status']
                status_text = test['status'].upper()
                details = test.get('error', '')
                if 'tables_found' in test:
                    details = f"Tables: {', '.join(test['tables_found'])}"
                if 'missing_tables' in test and test['missing_tables']:
                    details += f" | Missing: {', '.join(test['missing_tables'])}"
                
                html_report += f"""
                <tr>
                    <td>{test['test']}</td>
                    <td><span class="{status_class}">{status_text}</span></td>
                    <td>{details}</td>
                </tr>
"""
            
            html_report += "</table></div>"
        
        # Mobile Responsive Section
        if 'mobile_responsive' in results['tests']:
            html_report += """
        <div class="test-section">
            <h2>📱 Mobile Responsiveness Tests</h2>
            <table>
                <tr><th>Page</th><th>Viewport Meta</th><th>Responsive CSS</th><th>Score</th></tr>
"""
            
            for test in results['tests']['mobile_responsive']:
                if 'error' in test:
                    html_report += f"""
                <tr>
                    <td>{test['page']}</td>
                    <td colspan="3"><span class="error">ERROR: {test['error']}</span></td>
                </tr>
"""
                else:
                    viewport = '<span class="pass">✓</span>' if test.get('viewport_meta') else '<span class="fail">✗</span>'
                    responsive = '<span class="pass">✓</span>' if test.get('responsive_css') else '<span class="fail">✗</span>'
                    score = f"{test.get('score', 0):.1%}"
                    
                    html_report += f"""
                <tr>
                    <td>{test['page']}</td>
                    <td>{viewport}</td>
                    <td>{responsive}</td>
                    <td>{score}</td>
                </tr>
"""
            
            html_report += "</table></div>"
        
        html_report += """
        <div class="test-section">
            <h2>💡 Recommendations</h2>
            <ul>
                <li>🔄 Run tests regularly to catch regressions early</li>
                <li>📊 Monitor visual changes and verify intentional updates</li>
                <li>🔐 Implement proper admin authentication testing</li>
                <li>📱 Ensure mobile responsiveness across all pages</li>
                <li>🗄️ Regular database backups and integrity checks</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>🤖 Automated by QR Portal Advanced Testing Suite</p>
        </div>
    </div>
</body>
</html>
"""
        
        report_file = os.path.join(self.reports_dir, "comprehensive_test_report.html")
        with open(report_file, 'w') as f:
            f.write(html_report)
        
        self.logger.info(f"Comprehensive report saved: {report_file}")
        return report_file

class VisualElementParser(HTMLParser):
    """HTML parser to extract visual elements for regression testing"""
    
    def __init__(self):
        super().__init__()
        self.title = ""
        self.headings = []
        self.nav_items = []
        self.form_elements = []
        self.images = []
        self.in_title = False
        self.in_nav = False
        self.current_tag = None
    
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        
        if tag == 'title':
            self.in_title = True
        elif tag == 'nav':
            self.in_nav = True
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            pass  # Will capture content in handle_data
        elif tag in ['input', 'button', 'select', 'textarea']:
            attrs_dict = dict(attrs)
            self.form_elements.append({
                'tag': tag,
                'type': attrs_dict.get('type', ''),
                'name': attrs_dict.get('name', ''),
                'id': attrs_dict.get('id', '')
            })
        elif tag == 'img':
            attrs_dict = dict(attrs)
            self.images.append({
                'src': attrs_dict.get('src', ''),
                'alt': attrs_dict.get('alt', '')
            })
    
    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag == 'nav':
            self.in_nav = False
        self.current_tag = None
    
    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
        
        if self.in_title:
            self.title = data
        elif self.current_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.headings.append(data)
        elif self.in_nav:
            self.nav_items.append(data)

def main():
    print("🚀 Starting Advanced QR Portal Testing Suite...")
    
    suite = AdvancedTestingSuite()
    results = suite.run_comprehensive_tests()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_type, test_results in results['tests'].items():
        print(f"\n🧪 {test_type.replace('_', ' ').title()}:")
        
        if isinstance(test_results, list):
            passed = sum(1 for r in test_results if r.get('status') == 'pass' or (r.get('changed') == False and 'error' not in r))
            total = len(test_results)
            print(f"   ✅ {passed}/{total} tests passed")
        else:
            print(f"   📋 {len(test_results)} checks completed")
    
    print(f"\n📁 Reports saved in: {suite.reports_dir}/")
    print(f"📊 Open comprehensive_test_report.html for detailed results")

if __name__ == "__main__":
    main()