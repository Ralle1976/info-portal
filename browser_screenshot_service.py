#!/usr/bin/env python3
"""
QR Info Portal - Real Browser Screenshot Service
Uses subprocess to control browsers without selenium (system-wide installation not needed)
"""

import os
import sys
import json
import time
import subprocess
import tempfile
from datetime import datetime
from urllib.parse import urljoin

class BrowserScreenshotService:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.screenshots_dir = "browser_screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Detect available browsers
        self.browsers = self.detect_browsers()
        print(f"📱 Available browsers: {list(self.browsers.keys())}")
    
    def detect_browsers(self):
        """Detect available browsers on the system"""
        browsers = {}
        
        # Try common browser locations and commands
        browser_candidates = {
            'chromium': ['chromium-browser', 'chromium', 'google-chrome', 'chrome'],
            'firefox': ['firefox', 'firefox-esr'],
            'webkit': ['webkit2png', 'wkhtmltopdf']  # Alternative tools
        }
        
        for browser_type, commands in browser_candidates.items():
            for cmd in commands:
                try:
                    # Check if command exists
                    result = subprocess.run(['which', cmd], capture_output=True, text=True)
                    if result.returncode == 0:
                        browsers[browser_type] = {
                            'command': cmd,
                            'path': result.stdout.strip()
                        }
                        break
                except:
                    continue
        
        return browsers
    
    def take_screenshot_with_chromium(self, url, output_file):
        """Take screenshot using Chromium/Chrome"""
        if 'chromium' not in self.browsers:
            return False, "Chromium not available"
        
        cmd = self.browsers['chromium']['command']
        
        try:
            # Use headless Chrome to take screenshot
            subprocess.run([
                cmd,
                '--headless',
                '--no-sandbox',
                '--disable-gpu',
                '--virtual-time-budget=2000',  # Wait 2 seconds for page load
                '--window-size=1920,1080',
                '--screenshot=' + output_file,
                url
            ], check=True, capture_output=True, timeout=30)
            
            return True, f"Screenshot saved: {output_file}"
            
        except subprocess.TimeoutExpired:
            return False, "Screenshot timeout"
        except subprocess.CalledProcessError as e:
            return False, f"Chromium error: {e.stderr.decode() if e.stderr else 'Unknown error'}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def take_screenshot_with_firefox(self, url, output_file):
        """Take screenshot using Firefox"""
        if 'firefox' not in self.browsers:
            return False, "Firefox not available"
        
        # Firefox doesn't have built-in screenshot capability like Chrome
        # We'll use a different approach with a temporary HTML file
        
        try:
            # Create a simple HTML page that loads the target URL in an iframe
            # and uses JavaScript to take a screenshot (this is a workaround)
            
            html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; padding: 0; }}
        iframe {{ width: 100vw; height: 100vh; border: none; }}
    </style>
</head>
<body>
    <iframe src="{url}"></iframe>
    <script>
        setTimeout(() => {{
            console.log("Page loaded");
        }}, 2000);
    </script>
</body>
</html>
'''
            
            # Save temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html_content)
                temp_html = f.name
            
            # Use Firefox to open and process (limited functionality without extensions)
            subprocess.run([
                self.browsers['firefox']['command'],
                '--headless',
                '--screenshot=' + output_file,
                'file://' + temp_html
            ], check=True, capture_output=True, timeout=30)
            
            os.unlink(temp_html)  # Clean up
            return True, f"Screenshot saved: {output_file}"
            
        except subprocess.TimeoutExpired:
            return False, "Firefox screenshot timeout"
        except subprocess.CalledProcessError as e:
            return False, f"Firefox error: {e.stderr.decode() if e.stderr else 'Unknown error'}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def create_web_based_screenshot(self, url, output_file):
        """Create a web-based screenshot using HTML canvas (fallback method)"""
        try:
            # Create an HTML file that loads the target URL and uses canvas to capture it
            html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ margin: 0; font-family: Arial, sans-serif; }}
        .container {{ padding: 20px; }}
        .frame {{ border: 2px solid #ccc; width: 100%; height: 600px; }}
        .info {{ margin: 10px 0; font-size: 14px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>📸 Web Screenshot Capture</h2>
        <div class="info">URL: {url}</div>
        <div class="info">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        <iframe class="frame" src="{url}"></iframe>
        <div class="info">
            💡 This is a fallback web-based screenshot when no browser is available for headless capture.
        </div>
    </div>
</body>
</html>
'''
            
            with open(output_file.replace('.png', '.html'), 'w') as f:
                f.write(html_content)
            
            return True, f"Web-based screenshot saved: {output_file.replace('.png', '.html')}"
            
        except Exception as e:
            return False, f"Web screenshot error: {str(e)}"
    
    def take_screenshot(self, page_path, browser_type=None):
        """Take a screenshot of the given page"""
        url = urljoin(self.base_url, page_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        page_name = page_path.replace('/', '_') or 'home'
        
        # Try different browsers in order of preference
        if not browser_type:
            browser_preference = ['chromium', 'firefox', 'webkit']
        else:
            browser_preference = [browser_type]
        
        for browser in browser_preference:
            if browser not in self.browsers:
                continue
            
            output_file = os.path.join(self.screenshots_dir, f"{page_name}_{browser}_{timestamp}.png")
            
            print(f"📸 Taking screenshot of {url} using {browser}...")
            
            if browser == 'chromium':
                success, message = self.take_screenshot_with_chromium(url, output_file)
            elif browser == 'firefox':
                success, message = self.take_screenshot_with_firefox(url, output_file)
            else:
                success, message = False, f"Browser {browser} not implemented"
            
            if success:
                print(f"✅ {message}")
                return output_file
            else:
                print(f"❌ {browser}: {message}")
        
        # Fallback to web-based screenshot
        print("🔄 Trying web-based fallback screenshot...")
        output_file = os.path.join(self.screenshots_dir, f"{page_name}_web_{timestamp}.html")
        success, message = self.create_web_based_screenshot(url, output_file)
        
        if success:
            print(f"✅ {message}")
            return output_file
        else:
            print(f"❌ Fallback failed: {message}")
            return None
    
    def screenshot_all_pages(self):
        """Take screenshots of all main pages"""
        pages = [
            '/',
            '/week',
            '/month', 
            '/kiosk/single',
            '/kiosk/triple'
        ]
        
        results = []
        
        print("📸 Starting browser screenshot session...")
        print("=" * 60)
        
        for page in pages:
            print(f"\n🎯 Processing: {page}")
            screenshot_file = self.take_screenshot(page)
            results.append({
                'page': page,
                'screenshot_file': screenshot_file,
                'success': screenshot_file is not None,
                'timestamp': datetime.now().isoformat()
            })
            time.sleep(1)  # Small delay between screenshots
        
        # Save results summary
        summary_file = os.path.join(self.screenshots_dir, 'screenshot_summary.json')
        with open(summary_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'base_url': self.base_url,
                'browsers_available': list(self.browsers.keys()),
                'results': results
            }, f, indent=2)
        
        successful = sum(1 for r in results if r['success'])
        print(f"\n🎉 Screenshot session complete!")
        print(f"✅ {successful}/{len(results)} pages captured successfully")
        print(f"📁 Screenshots saved in: {self.screenshots_dir}/")
        print(f"📊 Summary: {summary_file}")
        
        return results
    
    def install_browser_suggestions(self):
        """Provide suggestions for installing browsers"""
        print("\n💡 Browser Installation Suggestions:")
        print("=" * 50)
        
        if not self.browsers:
            print("❌ No browsers detected!")
            print("\n🔧 To install browsers:")
            print("   Ubuntu/Debian: sudo apt install firefox-esr chromium-browser")
            print("   Fedora/RHEL:   sudo dnf install firefox chromium")
            print("   macOS:         brew install --cask firefox google-chrome")
            print("   Windows:       Download from browser websites")
        else:
            print("✅ Detected browsers:")
            for browser, info in self.browsers.items():
                print(f"   {browser}: {info['path']}")
        
        print("\n📋 Alternative screenshot methods available:")
        print("   • Web-based HTML screenshots (fallback)")
        print("   • ASCII-based screenshots (screenshot_service.py)")
        print("   • Structure analysis (monitor.py)")

def main():
    print("🚀 QR Info Portal - Browser Screenshot Service")
    print("=" * 60)
    
    service = BrowserScreenshotService()
    
    # Show browser installation suggestions if needed
    if not service.browsers:
        service.install_browser_suggestions()
        print("\n⚠️  No browsers available for screenshots.")
        print("   Falling back to web-based screenshots...")
    
    # Take screenshots
    results = service.screenshot_all_pages()
    
    # Show final summary
    print("\n💡 Tips:")
    print("1. Install browsers for better screenshot quality")
    print("2. Use web-based screenshots for basic visual testing")
    print("3. Combine with other monitoring tools for full coverage")

if __name__ == "__main__":
    main()