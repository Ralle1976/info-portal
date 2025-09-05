#!/usr/bin/env python3
"""
QR Info Portal - Frontend Testing Suite
Spezieller Fokus auf Checkbox-State-Persistence und Admin Interface Testing
"""

import os
import sys
import json
import time
import base64
import requests
import subprocess
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
import logging

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium nicht verfügbar. Installiere mit: pip install selenium")

class FrontendTestSuite:
    def __init__(self, base_url="http://127.0.0.1:5000", admin_user="admin", admin_password="admin123"):
        self.base_url = base_url
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.test_results = []
        self.screenshots_dir = "frontend_test_screenshots"
        self.reports_dir = "frontend_reports"
        
        # Create directories
        for directory in [self.screenshots_dir, self.reports_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - Frontend Test - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.reports_dir, 'frontend_tests.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.driver = None
        if SELENIUM_AVAILABLE:
            self.setup_selenium()
    
    def setup_selenium(self):
        """Setup Selenium WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            self.logger.info("Selenium WebDriver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Selenium: {e}")
            return False
    
    def take_screenshot(self, name, description=""):
        """Take screenshot with timestamp and description"""
        if not self.driver:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        try:
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Screenshot saved: {filepath} - {description}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to take screenshot {name}: {e}")
            return None
    
    def test_checkbox_state_persistence(self):
        """
        HAUPTTEST: Checkbox-State-Persistence Problem
        Testet speziell das gemeldete Problem:
        "Öffnungszeiten werden gespeichert, aber Checkboxen nicht als aktiv angezeigt"
        """
        self.logger.info("🔍 Testing Checkbox State Persistence Problem...")
        test_result = {
            "test_name": "Checkbox State Persistence",
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "status": "unknown",
            "issues_found": [],
            "screenshots": []
        }
        
        if not self.driver:
            test_result["status"] = "skipped"
            test_result["issues_found"].append("Selenium not available")
            return test_result
        
        try:
            # Step 1: Navigate to admin hours page
            self.driver.get(f"{self.base_url}/admin/")
            test_result["steps"].append("Navigated to admin page")
            
            # Login if required
            if "login" in self.driver.current_url.lower() or self.driver.find_elements(By.NAME, "username"):
                username_field = self.driver.find_element(By.NAME, "username")
                password_field = self.driver.find_element(By.NAME, "password")
                
                username_field.send_keys(self.admin_user)
                password_field.send_keys(self.admin_password)
                
                submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_btn.click()
                
                time.sleep(2)
                test_result["steps"].append("Admin login completed")
            
            # Navigate to hours management
            hours_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/admin/hours')]"))
            )
            hours_link.click()
            test_result["steps"].append("Navigated to hours management")
            
            # Take initial screenshot
            screenshot = self.take_screenshot("hours_initial", "Initial hours management page")
            if screenshot:
                test_result["screenshots"].append(screenshot)
            
            # Wait for page to load completely
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "weekly-hours-form"))
            )
            
            # Step 2: Test current checkbox states
            checkbox_states = {}
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            
            for day in days:
                closed_checkbox = self.driver.find_element(By.ID, f"{day}-closed")
                single_checkbox = self.driver.find_element(By.ID, f"{day}-single")
                
                checkbox_states[day] = {
                    "closed_checked": closed_checkbox.is_selected(),
                    "single_checked": single_checkbox.is_selected(),
                    "closed_enabled": closed_checkbox.is_enabled(),
                    "single_enabled": single_checkbox.is_enabled()
                }
            
            test_result["initial_checkbox_states"] = checkbox_states
            test_result["steps"].append("Captured initial checkbox states")
            
            # Step 3: Test bulk hours functionality
            bulk_start = self.driver.find_element(By.ID, "bulk-start-time")
            bulk_end = self.driver.find_element(By.ID, "bulk-end-time")
            
            bulk_start.clear()
            bulk_start.send_keys("09:00")
            bulk_end.clear()
            bulk_end.send_keys("18:00")
            
            # Select specific days for bulk operation
            test_days = ["monday", "wednesday", "friday"]
            for day in test_days:
                checkbox = self.driver.find_element(By.ID, f"bulk-{day}")
                if not checkbox.is_selected():
                    checkbox.click()
            
            test_result["steps"].append(f"Set bulk hours 09:00-18:00 for {test_days}")
            
            # Take screenshot before applying
            screenshot = self.take_screenshot("hours_before_bulk", "Before applying bulk hours")
            if screenshot:
                test_result["screenshots"].append(screenshot)
            
            # Apply bulk hours
            apply_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Zeiten auf ausgewählte Tage anwenden')]")
            apply_btn.click()
            
            # Wait for JavaScript to complete
            time.sleep(2)
            test_result["steps"].append("Applied bulk hours")
            
            # Step 4: Check checkbox states after bulk operation
            checkbox_states_after = {}
            for day in days:
                closed_checkbox = self.driver.find_element(By.ID, f"{day}-closed")
                single_checkbox = self.driver.find_element(By.ID, f"{day}-single")
                
                checkbox_states_after[day] = {
                    "closed_checked": closed_checkbox.is_selected(),
                    "single_checked": single_checkbox.is_selected(),
                    "closed_enabled": closed_checkbox.is_enabled(),
                    "single_enabled": single_checkbox.is_enabled()
                }
            
            test_result["checkbox_states_after_bulk"] = checkbox_states_after
            test_result["steps"].append("Captured checkbox states after bulk operation")
            
            # Take screenshot after bulk operation
            screenshot = self.take_screenshot("hours_after_bulk", "After applying bulk hours")
            if screenshot:
                test_result["screenshots"].append(screenshot)
            
            # Step 5: Verify that single checkboxes are correctly checked for days with bulk hours
            issues_found = []
            for day in test_days:
                if not checkbox_states_after[day]["single_checked"]:
                    issues_found.append(f"Day {day}: Single checkbox not checked after bulk operation")
                if checkbox_states_after[day]["closed_checked"]:
                    issues_found.append(f"Day {day}: Closed checkbox still checked after bulk operation")
            
            # Step 6: Save the form and test persistence
            save_btn = self.driver.find_element(By.XPATH, "//button[@type='submit' and contains(text(), 'Speichern')]")
            save_btn.click()
            
            # Wait for save operation
            time.sleep(3)
            test_result["steps"].append("Saved weekly hours form")
            
            # Step 7: Reload page and check if states persist
            self.driver.refresh()
            time.sleep(3)
            
            # Wait for page reload
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "weekly-hours-form"))
            )
            
            # Check states after reload
            checkbox_states_after_reload = {}
            for day in days:
                closed_checkbox = self.driver.find_element(By.ID, f"{day}-closed")
                single_checkbox = self.driver.find_element(By.ID, f"{day}-single")
                
                checkbox_states_after_reload[day] = {
                    "closed_checked": closed_checkbox.is_selected(),
                    "single_checked": single_checkbox.is_selected(),
                    "closed_enabled": closed_checkbox.is_enabled(),
                    "single_enabled": single_checkbox.is_enabled()
                }
            
            test_result["checkbox_states_after_reload"] = checkbox_states_after_reload
            test_result["steps"].append("Captured checkbox states after page reload")
            
            # Take final screenshot
            screenshot = self.take_screenshot("hours_after_reload", "After page reload")
            if screenshot:
                test_result["screenshots"].append(screenshot)
            
            # Step 8: Analyze persistence issues
            for day in test_days:
                before_save = checkbox_states_after[day]
                after_reload = checkbox_states_after_reload[day]
                
                if before_save["single_checked"] != after_reload["single_checked"]:
                    issues_found.append(f"Day {day}: Single checkbox state lost after reload (was {before_save['single_checked']}, now {after_reload['single_checked']})")
                
                if before_save["closed_checked"] != after_reload["closed_checked"]:
                    issues_found.append(f"Day {day}: Closed checkbox state lost after reload (was {before_save['closed_checked']}, now {after_reload['closed_checked']})")
            
            test_result["issues_found"] = issues_found
            test_result["status"] = "fail" if issues_found else "pass"
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["error"] = str(e)
            self.logger.error(f"Checkbox persistence test failed: {e}")
            
            # Take error screenshot
            if self.driver:
                screenshot = self.take_screenshot("hours_error", f"Error occurred: {str(e)[:50]}")
                if screenshot:
                    test_result["screenshots"].append(screenshot)
        
        return test_result
    
    def test_admin_navigation(self):
        """Test admin interface navigation and functionality"""
        self.logger.info("🧭 Testing Admin Navigation...")
        test_result = {
            "test_name": "Admin Navigation",
            "timestamp": datetime.now().isoformat(),
            "navigation_tests": [],
            "status": "unknown",
            "screenshots": []
        }
        
        if not self.driver:
            test_result["status"] = "skipped"
            return test_result
        
        admin_pages = [
            ("/admin/", "Dashboard"),
            ("/admin/status", "Status Management"),
            ("/admin/hours", "Hours Management"),
            ("/admin/announcements", "Announcements"),
            ("/admin/settings", "Settings")
        ]
        
        try:
            # Login first
            self.driver.get(f"{self.base_url}/admin/")
            
            # Handle login if required
            if "login" in self.driver.current_url.lower() or self.driver.find_elements(By.NAME, "username"):
                username_field = self.driver.find_element(By.NAME, "username")
                password_field = self.driver.find_element(By.NAME, "password")
                
                username_field.send_keys(self.admin_user)
                password_field.send_keys(self.admin_password)
                
                submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_btn.click()
                time.sleep(2)
            
            # Test each admin page
            for path, name in admin_pages:
                try:
                    self.driver.get(f"{self.base_url}{path}")
                    time.sleep(1)
                    
                    # Check if page loaded successfully
                    page_loaded = "admin" in self.driver.current_url and "error" not in self.driver.page_source.lower()
                    
                    nav_test = {
                        "page": name,
                        "path": path,
                        "status": "pass" if page_loaded else "fail",
                        "current_url": self.driver.current_url,
                        "page_title": self.driver.title
                    }
                    
                    # Check for specific elements that should be present
                    if path == "/admin/hours":
                        has_form = bool(self.driver.find_elements(By.ID, "weekly-hours-form"))
                        has_checkboxes = bool(self.driver.find_elements(By.CLASS_NAME, "day-closed-toggle"))
                        nav_test["elements_check"] = {
                            "weekly_hours_form": has_form,
                            "day_toggle_checkboxes": has_checkboxes
                        }
                    
                    test_result["navigation_tests"].append(nav_test)
                    
                    # Take screenshot
                    screenshot = self.take_screenshot(f"nav_{name.lower().replace(' ', '_')}", f"Navigation to {name}")
                    if screenshot:
                        test_result["screenshots"].append(screenshot)
                    
                except Exception as e:
                    test_result["navigation_tests"].append({
                        "page": name,
                        "path": path,
                        "status": "error",
                        "error": str(e)
                    })
            
            # Overall status
            failed_tests = [t for t in test_result["navigation_tests"] if t["status"] != "pass"]
            test_result["status"] = "fail" if failed_tests else "pass"
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["error"] = str(e)
        
        return test_result
    
    def test_csrf_token_handling(self):
        """Test CSRF token handling in forms"""
        self.logger.info("🔒 Testing CSRF Token Handling...")
        test_result = {
            "test_name": "CSRF Token Handling",
            "timestamp": datetime.now().isoformat(),
            "csrf_tests": [],
            "status": "unknown"
        }
        
        if not self.driver:
            test_result["status"] = "skipped"
            return test_result
        
        try:
            # Navigate to hours management
            self.driver.get(f"{self.base_url}/admin/hours")
            
            # Login if needed
            if "login" in self.driver.current_url.lower():
                username_field = self.driver.find_element(By.NAME, "username")
                password_field = self.driver.find_element(By.NAME, "password")
                
                username_field.send_keys(self.admin_user)
                password_field.send_keys(self.admin_password)
                
                submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_btn.click()
                time.sleep(2)
                
                # Navigate to hours again
                self.driver.get(f"{self.base_url}/admin/hours")
            
            # Check for CSRF token in form
            csrf_tokens = self.driver.find_elements(By.NAME, "csrf_token")
            
            csrf_test = {
                "page": "/admin/hours",
                "csrf_tokens_found": len(csrf_tokens),
                "status": "pass" if len(csrf_tokens) > 0 else "fail"
            }
            
            if csrf_tokens:
                csrf_test["csrf_token_value"] = csrf_tokens[0].get_attribute("value")[:20] + "..."  # Masked for security
            
            test_result["csrf_tests"].append(csrf_test)
            
            # Test form submission with CSRF
            if csrf_tokens:
                # Modify a simple setting and save
                monday_single = self.driver.find_element(By.ID, "monday-single")
                initial_state = monday_single.is_selected()
                
                # Toggle the checkbox
                monday_single.click()
                time.sleep(1)
                
                # Save form
                save_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                save_btn.click()
                time.sleep(3)
                
                # Check for success/error messages
                page_source = self.driver.page_source
                
                csrf_submit_test = {
                    "action": "Form submission with CSRF",
                    "initial_checkbox_state": initial_state,
                    "form_submitted": True,
                    "page_contains_error": "error" in page_source.lower(),
                    "status": "pass" if "error" not in page_source.lower() else "fail"
                }
                
                test_result["csrf_tests"].append(csrf_submit_test)
                
                # Revert change
                monday_single = self.driver.find_element(By.ID, "monday-single")
                if monday_single.is_selected() != initial_state:
                    monday_single.click()
                    save_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                    save_btn.click()
                    time.sleep(2)
            
            failed_tests = [t for t in test_result["csrf_tests"] if t["status"] != "pass"]
            test_result["status"] = "fail" if failed_tests else "pass"
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["error"] = str(e)
        
        return test_result
    
    def test_mobile_responsiveness(self):
        """Test mobile responsiveness with different viewport sizes"""
        self.logger.info("📱 Testing Mobile Responsiveness...")
        test_result = {
            "test_name": "Mobile Responsiveness",
            "timestamp": datetime.now().isoformat(),
            "viewport_tests": [],
            "status": "unknown"
        }
        
        if not self.driver:
            test_result["status"] = "skipped"
            return test_result
        
        viewports = [
            ("desktop", 1920, 1080),
            ("tablet", 768, 1024),
            ("mobile", 375, 667),
            ("mobile_small", 320, 568)
        ]
        
        pages = ["/", "/week", "/month", "/kiosk/single"]
        
        try:
            for viewport_name, width, height in viewports:
                self.driver.set_window_size(width, height)
                time.sleep(1)
                
                for page in pages:
                    try:
                        self.driver.get(f"{self.base_url}{page}")
                        time.sleep(2)
                        
                        # Check for responsive elements
                        body = self.driver.find_element(By.TAG_NAME, "body")
                        body_width = body.size['width']
                        
                        # Check for overflow
                        has_horizontal_scroll = self.driver.execute_script(
                            "return document.body.scrollWidth > document.body.clientWidth;"
                        )
                        
                        # Check for mobile-friendly navigation
                        nav_elements = self.driver.find_elements(By.TAG_NAME, "nav")
                        mobile_nav_present = any("mobile" in nav.get_attribute("class") or "" for nav in nav_elements)
                        
                        viewport_test = {
                            "viewport": f"{viewport_name} ({width}x{height})",
                            "page": page,
                            "body_width": body_width,
                            "has_horizontal_scroll": has_horizontal_scroll,
                            "mobile_nav_present": mobile_nav_present,
                            "status": "fail" if has_horizontal_scroll else "pass"
                        }
                        
                        test_result["viewport_tests"].append(viewport_test)
                        
                        # Take screenshot
                        screenshot = self.take_screenshot(f"responsive_{viewport_name}_{page.replace('/', '_')}", 
                                                        f"{viewport_name} view of {page}")
                        
                    except Exception as e:
                        test_result["viewport_tests"].append({
                            "viewport": f"{viewport_name} ({width}x{height})",
                            "page": page,
                            "status": "error",
                            "error": str(e)
                        })
            
            # Reset to desktop size
            self.driver.set_window_size(1920, 1080)
            
            failed_tests = [t for t in test_result["viewport_tests"] if t["status"] != "pass"]
            test_result["status"] = "fail" if failed_tests else "pass"
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["error"] = str(e)
        
        return test_result
    
    def test_qr_code_generation(self):
        """Test QR code generation functionality"""
        self.logger.info("📋 Testing QR Code Generation...")
        test_result = {
            "test_name": "QR Code Generation",
            "timestamp": datetime.now().isoformat(),
            "qr_tests": [],
            "status": "unknown"
        }
        
        qr_endpoints = [
            ("/qr", "PNG QR Code"),
            ("/qr.svg", "SVG QR Code"),
            ("/qr?target=week", "Week QR Code"),
            ("/qr?target=month", "Month QR Code")
        ]
        
        try:
            for endpoint, description in qr_endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                    
                    qr_test = {
                        "endpoint": endpoint,
                        "description": description,
                        "status_code": response.status_code,
                        "content_type": response.headers.get('Content-Type', ''),
                        "content_length": len(response.content),
                        "status": "pass" if response.status_code == 200 else "fail"
                    }
                    
                    # Verify content type
                    if endpoint.endswith('.svg'):
                        expected_type = 'image/svg+xml'
                    else:
                        expected_type = 'image/png'
                    
                    if expected_type not in qr_test["content_type"]:
                        qr_test["status"] = "fail"
                        qr_test["content_type_error"] = f"Expected {expected_type}, got {qr_test['content_type']}"
                    
                    test_result["qr_tests"].append(qr_test)
                    
                except Exception as e:
                    test_result["qr_tests"].append({
                        "endpoint": endpoint,
                        "description": description,
                        "status": "error",
                        "error": str(e)
                    })
            
            failed_tests = [t for t in test_result["qr_tests"] if t["status"] != "pass"]
            test_result["status"] = "fail" if failed_tests else "pass"
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["error"] = str(e)
        
        return test_result
    
    def analyze_frontend_javascript(self):
        """Analyze frontend JavaScript for potential issues"""
        self.logger.info("🔍 Analyzing Frontend JavaScript...")
        
        js_analysis = {
            "analysis_name": "Frontend JavaScript Analysis",
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": [],
            "potential_issues": [],
            "recommendations": []
        }
        
        # Check for JavaScript files
        js_files = []
        static_dir = "app/static/js"
        
        if os.path.exists(static_dir):
            for file in os.listdir(static_dir):
                if file.endswith('.js'):
                    js_files.append(os.path.join(static_dir, file))
        
        # Also check inline JavaScript in templates
        template_files = []
        templates_dir = "app/templates"
        
        if os.path.exists(templates_dir):
            for root, dirs, files in os.walk(templates_dir):
                for file in files:
                    if file.endswith('.html'):
                        template_files.append(os.path.join(root, file))
        
        # Analyze JavaScript files
        for js_file in js_files:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_analysis = {
                    "file": js_file,
                    "size": len(content),
                    "functions": [],
                    "potential_issues": []
                }
                
                # Simple function detection
                import re
                functions = re.findall(r'function\s+(\w+)\s*\(', content)
                file_analysis["functions"] = functions
                
                # Check for common issues
                if 'console.log' in content:
                    file_analysis["potential_issues"].append("Contains console.log statements")
                
                if 'alert(' in content:
                    file_analysis["potential_issues"].append("Uses alert() - consider modern notifications")
                
                if 'setTimeout(' in content and 'clearTimeout' not in content:
                    file_analysis["potential_issues"].append("setTimeout without clearTimeout - potential memory leaks")
                
                js_analysis["files_analyzed"].append(file_analysis)
                
            except Exception as e:
                js_analysis["files_analyzed"].append({
                    "file": js_file,
                    "error": str(e)
                })
        
        # Analyze hours.html specifically for checkbox issues
        hours_template = "app/templates/admin/hours.html"
        if os.path.exists(hours_template):
            try:
                with open(hours_template, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for checkbox-related JavaScript
                checkbox_functions = []
                if 'renderWeeklyHours' in content:
                    checkbox_functions.append("renderWeeklyHours")
                if 'applyBulkHours' in content:
                    checkbox_functions.append("applyBulkHours")
                if 'day-closed-toggle' in content:
                    checkbox_functions.append("day-closed-toggle event listeners")
                if 'day-single-toggle' in content:
                    checkbox_functions.append("day-single-toggle event listeners")
                
                hours_analysis = {
                    "file": hours_template,
                    "checkbox_functions": checkbox_functions,
                    "potential_checkbox_issues": []
                }
                
                # Check for potential checkbox state issues
                if 'singleToggle.checked = true' in content:
                    if 'data-user-set' not in content:
                        hours_analysis["potential_checkbox_issues"].append(
                            "Single toggle set to true without user-set flag - may cause state conflicts"
                        )
                
                if 'renderWeeklyHours()' in content:
                    if content.count('renderWeeklyHours()') > 2:
                        hours_analysis["potential_checkbox_issues"].append(
                            "renderWeeklyHours() called multiple times - may cause race conditions"
                        )
                
                # Look for checkbox state management
                if 'weeklyHours[day].length === 1' in content:
                    if 'singleToggle.checked = true' in content:
                        hours_analysis["checkbox_state_management"] = "Present - sets single toggle for single time slots"
                    else:
                        hours_analysis["potential_checkbox_issues"].append(
                            "Single time slot detection present but checkbox state not properly managed"
                        )
                
                js_analysis["hours_template_analysis"] = hours_analysis
                
            except Exception as e:
                js_analysis["hours_template_analysis"] = {"error": str(e)}
        
        return js_analysis
    
    def run_full_frontend_test_suite(self):
        """Run complete frontend test suite"""
        self.logger.info("🚀 Starting Full Frontend Test Suite...")
        
        full_results = {
            "suite_name": "QR Portal Frontend Test Suite",
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "base_url": self.base_url,
                "admin_user": self.admin_user,
                "selenium_available": SELENIUM_AVAILABLE
            },
            "tests": {}
        }
        
        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available - some tests will be skipped")
        
        # Run all test categories
        test_methods = [
            ("checkbox_persistence", self.test_checkbox_state_persistence),
            ("admin_navigation", self.test_admin_navigation),
            ("csrf_handling", self.test_csrf_token_handling),
            ("mobile_responsive", self.test_mobile_responsiveness),
            ("qr_generation", self.test_qr_code_generation),
            ("javascript_analysis", self.analyze_frontend_javascript)
        ]
        
        for test_name, test_method in test_methods:
            try:
                self.logger.info(f"Running {test_name} tests...")
                result = test_method()
                full_results["tests"][test_name] = result
                
                # Log result
                status = result.get("status", "unknown")
                self.logger.info(f"{test_name}: {status}")
                
            except Exception as e:
                self.logger.error(f"Test {test_name} failed with exception: {e}")
                full_results["tests"][test_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Generate comprehensive report
        self.generate_frontend_report(full_results)
        
        # Cleanup
        if self.driver:
            self.driver.quit()
        
        return full_results
    
    def generate_frontend_report(self, results):
        """Generate detailed HTML report for frontend tests"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.reports_dir, f"frontend_test_report_{timestamp}.html")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Portal Frontend Test Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .section {{ padding: 25px; border-bottom: 1px solid #e9ecef; }}
        .section:last-child {{ border-bottom: none; }}
        .test-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
        .test-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #dee2e6; }}
        .test-card.pass {{ border-left-color: #28a745; background: #f8fff9; }}
        .test-card.fail {{ border-left-color: #dc3545; background: #fff8f8; }}
        .test-card.error {{ border-left-color: #fd7e14; background: #fffbf8; }}
        .test-card.warning {{ border-left-color: #ffc107; background: #fffef8; }}
        .status {{ font-weight: bold; text-transform: uppercase; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }}
        .status.pass {{ background: #d4edda; color: #155724; }}
        .status.fail {{ background: #f8d7da; color: #721c24; }}
        .status.error {{ background: #ffeaa7; color: #856404; }}
        .status.warning {{ background: #fff3cd; color: #856404; }}
        .issue {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 6px; }}
        .screenshot {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; margin: 10px 0; }}
        .code {{ background: #f1f3f4; padding: 10px; border-radius: 4px; font-family: 'Courier New', monospace; white-space: pre-wrap; }}
        .summary {{ display: flex; justify-content: space-around; background: #e9ecef; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .summary-item {{ text-align: center; }}
        .summary-number {{ font-size: 2em; font-weight: bold; color: #495057; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #dee2e6; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; font-weight: 600; }}
        .highlight {{ background: #fff3cd; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 QR Info Portal - Frontend Test Report</h1>
            <p>Generated: {results['timestamp']}</p>
            <p>Base URL: {results['server_info']['base_url']}</p>
            <p>Selenium Available: {'✅ Yes' if results['server_info']['selenium_available'] else '❌ No'}</p>
        </div>
"""
        
        # Test Summary
        html_content += """
        <div class="section">
            <h2>📊 Test Summary</h2>
            <div class="summary">
"""
        
        total_tests = len(results['tests'])
        passed_tests = sum(1 for test in results['tests'].values() if test.get('status') == 'pass')
        failed_tests = sum(1 for test in results['tests'].values() if test.get('status') == 'fail')
        error_tests = sum(1 for test in results['tests'].values() if test.get('status') == 'error')
        
        html_content += f"""
                <div class="summary-item">
                    <div class="summary-number" style="color: #28a745;">{passed_tests}</div>
                    <div>Passed</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number" style="color: #dc3545;">{failed_tests}</div>
                    <div>Failed</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number" style="color: #fd7e14;">{error_tests}</div>
                    <div>Errors</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number">{total_tests}</div>
                    <div>Total</div>
                </div>
            </div>
        </div>
"""
        
        # Checkbox Persistence Test (Hauptfokus)
        if 'checkbox_persistence' in results['tests']:
            checkbox_test = results['tests']['checkbox_persistence']
            html_content += f"""
        <div class="section">
            <h2>🎯 HAUPTTEST: Checkbox State Persistence</h2>
            <div class="test-card {checkbox_test.get('status', 'unknown')}">
                <h3>Status: <span class="status {checkbox_test.get('status', 'unknown')}">{checkbox_test.get('status', 'unknown')}</span></h3>
                <p><strong>Test Steps:</strong></p>
                <ol>
"""
            
            for step in checkbox_test.get('steps', []):
                html_content += f"<li>{step}</li>"
            
            html_content += "</ol>"
            
            if checkbox_test.get('issues_found'):
                html_content += "<h4>🐛 Issues Found:</h4><ul>"
                for issue in checkbox_test['issues_found']:
                    html_content += f'<li class="issue">{issue}</li>'
                html_content += "</ul>"
            
            if checkbox_test.get('screenshots'):
                html_content += "<h4>📸 Screenshots:</h4>"
                for screenshot in checkbox_test['screenshots']:
                    if os.path.exists(screenshot):
                        rel_path = os.path.relpath(screenshot)
                        html_content += f'<img src="{rel_path}" class="screenshot" alt="Test screenshot" />'
            
            html_content += "</div></div>"
        
        # Other test sections...
        for test_name, test_data in results['tests'].items():
            if test_name == 'checkbox_persistence':
                continue  # Already handled above
                
            html_content += f"""
        <div class="section">
            <h2>{test_name.replace('_', ' ').title()}</h2>
            <div class="test-card {test_data.get('status', 'unknown')}">
                <h3>Status: <span class="status {test_data.get('status', 'unknown')}">{test_data.get('status', 'unknown')}</span></h3>
                <pre class="code">{json.dumps(test_data, indent=2, default=str)}</pre>
            </div>
        </div>
"""
        
        html_content += """
        <div class="section">
            <h2>🔧 Recommendations for Checkbox Issue</h2>
            <div class="test-card warning">
                <h3>Problem Analysis</h3>
                <p>Das Checkbox-State-Persistence Problem tritt auf, wenn:</p>
                <ul>
                    <li>Bulk Hours angewendet werden, aber die entsprechenden Checkboxen nicht korrekt aktualisiert werden</li>
                    <li>Die renderWeeklyHours() Funktion die Checkbox-States nicht synchron zu den weeklyHours Daten setzt</li>
                    <li>Event Listener oder DOM-Updates nicht ordnungsgemäß ausgeführt werden</li>
                </ul>
                
                <h3>Lösungsansätze</h3>
                <ol>
                    <li><strong>Verbesserte State Synchronisation:</strong> Sicherstellen dass checkbox.checked immer mit weeklyHours[day] synchron ist</li>
                    <li><strong>Explicit Checkbox Updates:</strong> Nach jeder weeklyHours Änderung explizit alle Checkboxen aktualisieren</li>
                    <li><strong>Event Listener Debugging:</strong> Console.log Statements für Checkbox Events hinzufügen</li>
                    <li><strong>Force Re-render:</strong> Komplette DOM-Neurendierung nach Bulk Operations</li>
                </ol>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; color: #666;">
            <p>🤖 Generated by QR Portal Frontend Testing Suite</p>
            <p>For detailed analysis, check the log files in frontend_reports/</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Frontend test report generated: {report_file}")
        return report_file

def install_selenium():
    """Install Selenium if not available"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
        print("✅ Selenium installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Selenium: {e}")
        return False

def main():
    print("🎯 QR Portal Frontend Testing Suite")
    print("=" * 50)
    
    # Check if Selenium is available, offer to install
    if not SELENIUM_AVAILABLE:
        response = input("Selenium not found. Install now? (y/n): ")
        if response.lower() == 'y':
            if install_selenium():
                print("Please restart the script to use Selenium tests")
                return
        else:
            print("Continuing without Selenium (limited functionality)")
    
    # Check if server is running
    base_url = "http://127.0.0.1:5000"
    try:
        response = requests.get(f"{base_url}/healthz", timeout=5)
        if response.status_code != 200:
            print(f"⚠️ Server health check failed: {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Server not reachable. Please start the Flask server first:")
        print("   export FLASK_APP=app && flask run --host 0.0.0.0 --port 5000")
        return
    
    # Run tests
    suite = FrontendTestSuite(base_url)
    results = suite.run_full_frontend_test_suite()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 FRONTEND TEST RESULTS")
    print("=" * 60)
    
    for test_name, test_result in results['tests'].items():
        status = test_result.get('status', 'unknown')
        status_icon = {
            'pass': '✅',
            'fail': '❌', 
            'error': '⚠️',
            'skipped': '⏭️',
            'unknown': '❓'
        }.get(status, '❓')
        
        print(f"{status_icon} {test_name.replace('_', ' ').title()}: {status.upper()}")
        
        if status == 'fail' and test_result.get('issues_found'):
            for issue in test_result['issues_found'][:3]:  # Show first 3 issues
                print(f"   🐛 {issue}")
    
    print(f"\n📁 Detailed report saved in: frontend_reports/")
    print(f"📸 Screenshots available in: {suite.screenshots_dir}/")
    
    # Specific checkbox issue analysis
    if 'checkbox_persistence' in results['tests']:
        checkbox_result = results['tests']['checkbox_persistence']
        print(f"\n🎯 CHECKBOX PERSISTENCE ANALYSIS:")
        print(f"Status: {checkbox_result.get('status', 'unknown')}")
        
        if checkbox_result.get('issues_found'):
            print("Issues found:")
            for issue in checkbox_result['issues_found']:
                print(f"  • {issue}")
        else:
            print("✅ No checkbox persistence issues detected")

if __name__ == "__main__":
    main()