#!/usr/bin/env python3
"""
QR Info Portal - Screenshot Service
Creates visual screenshots using HTML to ASCII conversion and detailed page analysis
"""

import requests
import time
import os
from datetime import datetime
from urllib.parse import urljoin
import re

class ScreenshotService:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.output_dir = "visual_tests"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_visual_screenshot(self, html_content, page_name):
        """Create a detailed visual representation of the page"""
        
        # Extract page structure
        structure = self.analyze_page_structure(html_content)
        
        # Create visual ASCII art
        screenshot = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        QR INFO PORTAL - VISUAL SCREENSHOT                   ║
║                             {page_name.upper().center(40)}                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
"""
        
        # Header section
        if structure['title']:
            screenshot += f"║ 📄 TITLE: {structure['title'][:60]:<60} ║\n"
        
        # Navigation
        if structure['nav_links']:
            screenshot += "║                                                                              ║\n"
            screenshot += "║ 🧭 NAVIGATION:                                                               ║\n"
            for link in structure['nav_links'][:5]:
                screenshot += f"║    • {link[:68]:<68} ║\n"
        
        # Main content sections
        screenshot += "║                                                                              ║\n"
        screenshot += "║ 📋 MAIN CONTENT:                                                             ║\n"
        
        if structure['headings']:
            for i, heading in enumerate(structure['headings'][:8]):
                level = "H1" if "<h1" in heading.lower() else "H2" if "<h2" in heading.lower() else "H3"
                clean_heading = re.sub(r'<[^>]+>', '', heading).strip()[:65]
                screenshot += f"║    {level}: {clean_heading:<65} ║\n"
        
        # Forms and inputs
        if structure['forms']:
            screenshot += "║                                                                              ║\n"
            screenshot += "║ 📝 FORMS & INPUTS:                                                           ║\n"
            for form in structure['forms'][:3]:
                screenshot += f"║    • {form[:68]:<68} ║\n"
        
        # Status and important info
        if structure['status_info']:
            screenshot += "║                                                                              ║\n"
            screenshot += "║ ℹ️  STATUS & INFO:                                                           ║\n"
            for status in structure['status_info'][:3]:
                screenshot += f"║    • {status[:68]:<68} ║\n"
        
        # Links and buttons
        if structure['buttons']:
            screenshot += "║                                                                              ║\n"
            screenshot += "║ 🔘 BUTTONS & ACTIONS:                                                        ║\n"
            for button in structure['buttons'][:5]:
                screenshot += f"║    • {button[:68]:<68} ║\n"
        
        # Layout info
        screenshot += "║                                                                              ║\n"
        screenshot += "║ 📊 PAGE STATISTICS:                                                          ║\n"
        screenshot += f"║    • Total Size: {len(html_content):,} bytes{'':<35} ║\n"
        screenshot += f"║    • HTML Lines: {len(html_content.split(chr(10))):,}{'':<45} ║\n"
        screenshot += f"║    • External Links: {structure['external_links']} found{'':<35} ║\n"
        screenshot += f"║    • CSS Files: {structure['css_files']} referenced{'':<38} ║\n"
        screenshot += f"║    • JS Files: {structure['js_files']} referenced{'':<39} ║\n"
        
        # Footer
        screenshot += "║                                                                              ║\n"
        screenshot += "╚══════════════════════════════════════════════════════════════════════════════╝\n"
        
        return screenshot
    
    def analyze_page_structure(self, html_content):
        """Analyze HTML structure and extract key elements"""
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "No Title"
        
        # Extract navigation links
        nav_pattern = r'<nav[^>]*>.*?</nav>|<a[^>]*href=["\'][^"\']*["\'][^>]*>[^<]*</a>'
        nav_matches = re.findall(nav_pattern, html_content, re.IGNORECASE | re.DOTALL)
        nav_links = []
        for match in nav_matches[:10]:
            clean_match = re.sub(r'<[^>]+>', '', match).strip()
            if clean_match and len(clean_match) > 2:
                nav_links.append(clean_match)
        
        # Extract headings
        heading_pattern = r'<h[1-6][^>]*>.*?</h[1-6]>'
        headings = re.findall(heading_pattern, html_content, re.IGNORECASE | re.DOTALL)
        
        # Extract forms and inputs
        form_pattern = r'<(?:form|input|button|select|textarea)[^>]*[^>]*>'
        forms = re.findall(form_pattern, html_content, re.IGNORECASE)
        clean_forms = []
        for form in forms[:10]:
            if 'type=' in form or 'name=' in form:
                clean_forms.append(re.sub(r'<|>', '', form)[:50])
        
        # Extract status information (look for specific classes/content)
        status_pattern = r'(?:status|info|alert|banner|notice)[^>]*>([^<]+)'
        status_matches = re.findall(status_pattern, html_content, re.IGNORECASE)
        status_info = [status.strip() for status in status_matches if len(status.strip()) > 3][:5]
        
        # Extract buttons
        button_pattern = r'<button[^>]*>([^<]+)</button>|<input[^>]*type=["\'](?:submit|button)["\'][^>]*>'
        button_matches = re.findall(button_pattern, html_content, re.IGNORECASE)
        buttons = [btn.strip() for btn in button_matches if btn.strip()][:8]
        
        # Count external resources
        external_links = len(re.findall(r'https?://(?!127\.0\.0\.1|localhost)', html_content))
        css_files = len(re.findall(r'\.css', html_content))
        js_files = len(re.findall(r'\.js', html_content))
        
        return {
            'title': title,
            'nav_links': nav_links,
            'headings': headings,
            'forms': clean_forms,
            'status_info': status_info,
            'buttons': buttons,
            'external_links': external_links,
            'css_files': css_files,
            'js_files': js_files
        }
    
    def screenshot_page(self, path, save_html=False):
        """Take a visual screenshot of a page"""
        url = urljoin(self.base_url, path)
        page_name = path.replace('/', '_') or 'home'
        
        try:
            print(f"📸 Taking screenshot of: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return f"❌ Error: HTTP {response.status_code} for {url}"
            
            # Create visual screenshot
            screenshot = self.create_visual_screenshot(response.text, page_name)
            
            # Save screenshot
            screenshot_file = os.path.join(self.output_dir, f"{page_name}_screenshot.txt")
            with open(screenshot_file, 'w', encoding='utf-8') as f:
                f.write(screenshot)
            
            # Optionally save full HTML
            if save_html:
                html_file = os.path.join(self.output_dir, f"{page_name}_source.html")
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
            
            print(f"✅ Screenshot saved: {screenshot_file}")
            return screenshot_file
            
        except Exception as e:
            error_msg = f"❌ Error taking screenshot of {url}: {str(e)}"
            print(error_msg)
            return error_msg
    
    def screenshot_all_pages(self, save_html_sources=False):
        """Take screenshots of all main pages"""
        pages = [
            ('/', 'Homepage'),
            ('/week', 'Week View'),
            ('/month', 'Month View'),
            ('/kiosk/single', 'Kiosk Single'),
            ('/kiosk/triple', 'Kiosk Triple'),
            ('/qr', 'QR Code Generator')
        ]
        
        print("📸 Starting visual screenshot session...")
        print("=" * 60)
        
        results = []
        for path, description in pages:
            print(f"\n🎯 Processing: {description}")
            result = self.screenshot_page(path, save_html_sources)
            results.append((path, description, result))
            time.sleep(1)  # Small delay between requests
        
        # Create summary report
        self.create_screenshot_report(results)
        
        print(f"\n🎉 Screenshot session complete!")
        print(f"📁 Results saved in: {self.output_dir}/")
        
        return results
    
    def create_screenshot_report(self, results):
        """Create an HTML report with all screenshots"""
        report_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>QR Info Portal - Visual Screenshots Report</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background-color: #1a1a1a;
            color: #00ff00;
            margin: 20px;
            line-height: 1.4;
        }}
        .header {{
            text-align: center;
            border: 2px solid #00ff00;
            padding: 20px;
            margin-bottom: 30px;
            background-color: #002200;
        }}
        .screenshot {{
            background-color: #000;
            border: 1px solid #00ff00;
            padding: 15px;
            margin-bottom: 20px;
            overflow-x: auto;
            white-space: pre;
            font-size: 12px;
        }}
        .page-title {{
            color: #ffff00;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .success {{ color: #00ff00; }}
        .error {{ color: #ff0000; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📸 QR INFO PORTAL - VISUAL SCREENSHOTS</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total Pages Captured: {len(results)}</p>
    </div>
"""
        
        for path, description, result in results:
            is_error = result.startswith('❌')
            status_class = 'error' if is_error else 'success'
            
            report_html += f"""
    <div class="page-title {status_class}">
        🎯 {description} ({path})
    </div>
"""
            
            if not is_error and os.path.exists(result):
                # Read and include the screenshot
                with open(result, 'r', encoding='utf-8') as f:
                    screenshot_content = f.read()
                
                report_html += f"""
    <div class="screenshot">
{screenshot_content}
    </div>
"""
            else:
                report_html += f"""
    <div class="screenshot error">
        {result}
    </div>
"""
        
        report_html += """
</body>
</html>
"""
        
        # Save report
        report_file = os.path.join(self.output_dir, 'screenshot_report.html')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        print(f"📊 Visual report saved: {report_file}")
        return report_file

def main():
    print("🚀 QR Info Portal - Visual Screenshot Service")
    print("=" * 50)
    
    service = ScreenshotService()
    
    # Take screenshots of all pages
    results = service.screenshot_all_pages(save_html_sources=True)
    
    print(f"\n📋 Summary:")
    successful = len([r for r in results if not r[2].startswith('❌')])
    print(f"✅ Successful screenshots: {successful}/{len(results)}")
    
    print(f"\n💡 Tips:")
    print(f"1. Open {service.output_dir}/screenshot_report.html to view all screenshots")
    print(f"2. Individual screenshots are in {service.output_dir}/")
    print(f"3. HTML source files are also saved for detailed analysis")

if __name__ == "__main__":
    main()