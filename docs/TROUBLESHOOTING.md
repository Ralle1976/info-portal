# 🔧 QR Info Portal - Troubleshooting Guide & FAQ

**Version:** 1.0.0 | **Last Updated:** 2025-08-23

---

## 📋 Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common User Issues](#common-user-issues)
3. [Admin Panel Problems](#admin-panel-problems)
4. [Technical Issues](#technical-issues)
5. [Performance Problems](#performance-problems)
6. [Mobile & QR Code Issues](#mobile--qr-code-issues)
7. [Language & Localization](#language--localization)
8. [Network & Connectivity](#network--connectivity)
9. [Database Issues](#database-issues)
10. [Security & Access](#security--access)
11. [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
12. [Error Codes Reference](#error-codes-reference)
13. [Getting Support](#getting-support)

---

## Quick Diagnostics

### 🚨 Emergency Checklist

**Before deep troubleshooting, check these basics:**

- [ ] **Internet Connection** - Can you reach other websites?
- [ ] **URL Correct** - Are you using the right address?
- [ ] **Browser Update** - Is your browser current (Chrome, Firefox, Safari, Edge)?
- [ ] **Cache Clear** - Try hard refresh (Ctrl+F5 / Cmd+Shift+R)
- [ ] **Mobile/Desktop** - Does it work on a different device?
- [ ] **Different Network** - Try mobile data vs WiFi

### 🔍 Quick Status Check

```bash
# Check if server is running
curl -I http://your-domain.com

# Check database connection
curl http://your-domain.com/healthz

# Check admin access
curl -I http://your-domain.com/admin
```

### 📱 Mobile Quick Test

1. **QR Code Test:** Use built-in camera app to scan
2. **Direct URL:** Type the URL manually in mobile browser
3. **Different Apps:** Try Chrome, Safari, Firefox mobile
4. **Network Switch:** WiFi → Mobile data or vice versa

---

## Common User Issues

### 🏠 Homepage Not Loading

**Problem:** Blank page, error message, or infinite loading

**Solutions:**

1. **Basic Troubleshooting:**
   ```bash
   # Clear browser cache
   Ctrl+Shift+Del (Chrome/Firefox)
   Cmd+Shift+Del (Safari)
   
   # Hard refresh
   Ctrl+F5 (Windows)
   Cmd+Shift+R (Mac)
   ```

2. **Check URL:**
   - Correct: `http://your-ip:5000` or `https://your-domain.com`
   - Incorrect: `http://your-ip:5000/home` (no `/home` needed)

3. **Network Issues:**
   - Try `ping your-domain.com`
   - Check firewall settings
   - Verify port 5000 is open

4. **Browser Compatibility:**
   - **Supported:** Chrome 70+, Firefox 65+, Safari 12+, Edge 79+
   - **Not Supported:** Internet Explorer
   - Try incognito/private browsing mode

### 🌍 Language Not Changing

**Problem:** Language switcher doesn't work or reverts

**Solutions:**

1. **Enable Cookies:**
   ```
   Chrome: Settings → Privacy and security → Cookies
   Firefox: Settings → Privacy & Security → Cookies
   Safari: Preferences → Privacy → Cookies
   ```

2. **Clear Language Cookies:**
   ```javascript
   // In browser console (F12)
   document.cookie = "language=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
   location.reload();
   ```

3. **URL Parameters:**
   ```
   Force German: https://your-domain.com/?lang=de
   Force Thai: https://your-domain.com/?lang=th
   Force English: https://your-domain.com/?lang=en
   ```

4. **Browser Language Override:**
   - Check browser language settings
   - Portal may auto-detect browser language

### 📅 Opening Hours Not Showing

**Problem:** Opening hours appear as "N/A" or are incorrect

**Solutions:**

1. **Check Admin Panel:**
   - Login to `/admin`
   - Go to "Öffnungszeiten" / "Hours"
   - Verify weekly schedule is set

2. **Time Format Issues:**
   ```
   Correct: 08:30-12:00, 13:00-16:00
   Incorrect: 8:30AM-12PM, 1-4PM
   Incorrect: 08.30-12.00
   ```

3. **Timezone Problems:**
   - Check `config.yml`: `timezone: "Asia/Bangkok"`
   - Server timezone should match local time
   ```bash
   timedatectl set-timezone Asia/Bangkok
   ```

4. **Database Issues:**
   ```bash
   # Check database for hours data
   sqlite3 data/portal.db "SELECT * FROM hours;"
   ```

### 🔴 Status Banner Not Updating

**Problem:** Status shows outdated information

**Solutions:**

1. **Admin Panel Check:**
   - Verify current status in admin dashboard
   - Check if status has end date that passed

2. **Cache Issues:**
   ```bash
   # Force browser cache clear
   Ctrl+Shift+Del → Clear all
   
   # Or add cache-busting parameter
   https://your-domain.com/?v=12345
   ```

3. **Database Consistency:**
   ```sql
   -- Check current status
   SELECT * FROM status ORDER BY created_at DESC LIMIT 1;
   
   -- Reset if needed
   UPDATE status SET type='ANWESEND' WHERE id = (SELECT MAX(id) FROM status);
   ```

---

## Admin Panel Problems

### 🔑 Cannot Login to Admin Panel

**Problem:** Login fails with correct credentials

**Solutions:**

1. **Check Password in .env:**
   ```bash
   # View current password (safely)
   grep ADMIN_PASSWORD .env
   
   # Generate new password
   echo "ADMIN_PASSWORD=$(openssl rand -base64 32)" >> .env
   ```

2. **Username Verification:**
   ```yaml
   # In config.yml
   admin:
     username: "admin"  # Default username
   ```

3. **Session Issues:**
   ```bash
   # Clear browser data completely
   # Or try incognito/private browsing
   ```

4. **Server Restart:**
   ```bash
   # Development server
   Ctrl+C and restart flask run
   
   # Docker
   docker-compose restart
   
   # Systemd
   sudo systemctl restart qr-portal
   ```

### 💾 Changes Not Saving

**Problem:** Admin changes don't appear on public site

**Solutions:**

1. **Check Save Confirmation:**
   - Look for green "Saved" message
   - No browser errors in console (F12)

2. **Database Permissions:**
   ```bash
   # Check database file permissions
   ls -la data/portal.db
   
   # Fix permissions if needed
   chmod 664 data/portal.db
   chown www-data:www-data data/portal.db  # or your user
   ```

3. **Database Locks:**
   ```bash
   # Check if database is locked
   sqlite3 data/portal.db ".timeout 1000"
   
   # Force unlock (dangerous!)
   rm -f data/portal.db-wal data/portal.db-shm
   ```

4. **Form Validation:**
   - Check all required fields are filled
   - Verify date formats are correct
   - Look for JavaScript errors in browser console

### 📊 Dashboard Cards Empty

**Problem:** Admin dashboard shows no data

**Solutions:**

1. **Database Initialization:**
   ```bash
   # Re-initialize database
   python -c "from app.database import init_database; init_database()"
   ```

2. **Check Database Content:**
   ```sql
   sqlite3 data/portal.db
   .tables
   SELECT COUNT(*) FROM status;
   SELECT COUNT(*) FROM hours;
   .exit
   ```

3. **Configuration Loading:**
   ```python
   # Test config loading
   python -c "
   from app import create_app
   app = create_app()
   with app.app_context():
       from app.models import Status
       print('Status records:', Status.select().count())
   "
   ```

### 🔄 Auto-refresh Not Working

**Problem:** Dashboard time not updating automatically

**Solutions:**

1. **JavaScript Enabled:**
   - Check browser settings allow JavaScript
   - Disable ad blockers temporarily

2. **Network Connection:**
   - Stable internet required for auto-updates
   - Check browser network tab for failed requests

3. **Server Response:**
   ```bash
   # Test time API endpoint
   curl http://localhost:5000/admin/api/current-time
   ```

---

## Technical Issues

### 🖥️ Server Won't Start

**Problem:** Flask server fails to start

**Solutions:**

1. **Port Already in Use:**
   ```bash
   # Find process using port 5000
   lsof -i :5000          # macOS/Linux
   netstat -ano | findstr :5000  # Windows
   
   # Kill process
   kill -9 [PID]          # macOS/Linux
   taskkill /PID [PID] /F # Windows
   
   # Use different port
   flask run --port 5001
   ```

2. **Python/Dependencies Issues:**
   ```bash
   # Check Python version
   python --version  # Must be 3.11+
   
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   
   # Check virtual environment
   which python  # Should point to .venv/bin/python
   ```

3. **Configuration Errors:**
   ```bash
   # Test configuration
   python -c "from app import create_app; create_app()"
   
   # Check .env file exists
   ls -la .env
   
   # Validate config.yml
   python -c "import yaml; yaml.safe_load(open('config.yml'))"
   ```

4. **File Permissions:**
   ```bash
   # Fix permissions
   chmod +x run.py
   chmod 755 app/
   chmod 644 config.yml
   chmod 600 .env
   ```

### 🗄️ Database Connection Failed

**Problem:** Cannot connect to SQLite database

**Solutions:**

1. **Database File Issues:**
   ```bash
   # Check if database exists
   ls -la data/portal.db
   
   # Check permissions
   chmod 664 data/portal.db
   
   # Create directory if missing
   mkdir -p data/
   ```

2. **Database Corruption:**
   ```bash
   # Check database integrity
   sqlite3 data/portal.db "PRAGMA integrity_check;"
   
   # Backup and recreate if corrupted
   cp data/portal.db data/portal.db.backup
   rm data/portal.db
   python -c "from app.database import init_database; init_database()"
   ```

3. **Lock Files:**
   ```bash
   # Remove lock files
   rm -f data/portal.db-wal
   rm -f data/portal.db-shm
   ```

### 🔧 Module Import Errors

**Problem:** Python ImportError or ModuleNotFoundError

**Solutions:**

1. **Virtual Environment:**
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   
   # Verify correct Python
   which python
   which pip
   ```

2. **Missing Dependencies:**
   ```bash
   # Install missing packages
   pip install -r requirements.txt
   
   # Check specific package
   pip show flask sqlmodel qrcode
   
   # Reinstall if needed
   pip uninstall -y flask && pip install flask
   ```

3. **PYTHONPATH Issues:**
   ```bash
   # Add current directory to path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   
   # Or use relative imports
   python -m app.main
   ```

---

## Performance Problems

### 🐌 Slow Page Loading

**Problem:** Pages take more than 3-5 seconds to load

**Solutions:**

1. **Server Resources:**
   ```bash
   # Check system resources
   top
   free -m      # Memory usage
   df -h        # Disk space
   
   # Check server logs
   tail -f server.log
   ```

2. **Database Optimization:**
   ```sql
   -- Optimize database
   sqlite3 data/portal.db "VACUUM;"
   
   -- Check database size
   ls -lh data/portal.db
   ```

3. **Network Issues:**
   ```bash
   # Test local vs remote
   curl -w "%{time_total}" http://localhost:5000
   curl -w "%{time_total}" http://your-domain.com
   
   # Check DNS resolution
   nslookup your-domain.com
   ```

4. **Browser Performance:**
   - Disable browser extensions
   - Clear cache and cookies
   - Check browser developer tools for slow requests

### 📱 Mobile Performance Issues

**Problem:** Slow or unresponsive on mobile devices

**Solutions:**

1. **Mobile Network:**
   - Switch between WiFi and mobile data
   - Check signal strength
   - Test on different mobile networks

2. **Browser Cache:**
   ```
   Chrome Mobile: Menu → Settings → Privacy → Clear browsing data
   Safari Mobile: Settings → Safari → Clear History and Website Data
   ```

3. **Image Optimization:**
   - Check if images are too large
   - Verify Tailwind CSS is loading properly
   - Test without images loaded

4. **JavaScript Performance:**
   - Check browser console for errors
   - Disable JavaScript temporarily to test base functionality

### 🔄 Auto-refresh Problems

**Problem:** Kiosk mode not auto-refreshing

**Solutions:**

1. **JavaScript Errors:**
   ```javascript
   // Open browser console (F12) and check for errors
   console.log('Checking auto-refresh...');
   ```

2. **Network Connectivity:**
   - Ensure stable internet connection
   - Check if firewall blocks periodic requests

3. **Browser Sleep Mode:**
   - Prevent browser/screen from sleeping
   - Use full-screen kiosk mode
   - Add keep-awake meta tag

4. **Server-Side Issues:**
   ```bash
   # Check if time API is responding
   curl http://localhost:5000/admin/api/current-time
   ```

---

## Mobile & QR Code Issues

### 📱 QR Code Won't Scan

**Problem:** QR code scanner can't read the code

**Solutions:**

1. **QR Code Quality:**
   ```bash
   # Generate high-quality QR code
   curl "http://localhost:5000/qr?size=large" -o test-qr.png
   
   # Check if QR contains correct URL
   # Use online QR decoder to verify content
   ```

2. **Camera Issues:**
   - Clean phone camera lens
   - Ensure good lighting
   - Hold phone steady 6-12 inches from QR code
   - Try different QR scanner apps

3. **QR Code Size:**
   - Too small: Minimum 2x2 cm for print
   - Too large: Maximum filling 80% of page
   - Proper contrast: Black on white background

4. **URL Problems:**
   ```bash
   # Verify URL in QR code works
   curl -I http://your-domain.com
   
   # Check SITE_URL in .env
   grep SITE_URL .env
   ```

### 📲 Mobile Layout Issues

**Problem:** Website doesn't display properly on phones

**Solutions:**

1. **Viewport Meta Tag:**
   ```html
   <!-- Should be in all templates -->
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   ```

2. **Responsive Design:**
   - Check Tailwind CSS is loading
   - Test with browser developer tools device simulation
   - Verify responsive classes are applied

3. **Font Issues:**
   ```css
   /* Thai font loading */
   @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
   ```

4. **Touch Targets:**
   - Ensure buttons are at least 44px high
   - Add proper touch event handling
   - Test on actual mobile devices

### 🔄 Mobile Browser Caching

**Problem:** Mobile browser shows outdated content

**Solutions:**

1. **Force Refresh:**
   ```
   iOS Safari: Hold refresh button → "Request Desktop Site" → Switch back
   Android Chrome: Menu → Settings → Site settings → All sites → Clear & reset
   ```

2. **Browser Data:**
   ```
   Clear all browser data including:
   - Cached images and files
   - Cookies and site data
   - Hosted app data
   ```

3. **PWA Cache:**
   ```javascript
   // If using PWA features, clear service worker cache
   navigator.serviceWorker.getRegistrations().then(function(registrations) {
     for(let registration of registrations) {
       registration.unregister();
     }
   });
   ```

---

## Language & Localization

### 🌐 Missing Translations

**Problem:** Text appears in wrong language or as translation keys

**Solutions:**

1. **Translation Files:**
   ```bash
   # Check translation files exist
   ls app/translations/
   
   # Should contain: de.json, th.json, en.json
   ```

2. **JSON Syntax:**
   ```bash
   # Validate JSON syntax
   python -m json.tool app/translations/de.json
   python -m json.tool app/translations/th.json
   python -m json.tool app/translations/en.json
   ```

3. **Missing Keys:**
   ```python
   # Check for missing translation keys
   import json
   
   with open('app/translations/de.json') as f:
       de_keys = set(json.load(f).keys())
   with open('app/translations/th.json') as f:
       th_keys = set(json.load(f).keys())
   with open('app/translations/en.json') as f:
       en_keys = set(json.load(f).keys())
       
   print("Missing in Thai:", de_keys - th_keys)
   print("Missing in English:", de_keys - en_keys)
   ```

4. **Template Usage:**
   ```jinja2
   <!-- Correct usage -->
   {{ t('site_title') }}
   
   <!-- Check for typos -->
   {{ t('site_titel') }}  <!-- Wrong! -->
   ```

### 🇹🇭 Thai Language Issues

**Problem:** Thai text not displaying correctly

**Solutions:**

1. **Font Loading:**
   ```css
   /* Ensure Sarabun font is loaded */
   @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
   
   body {
       font-family: 'Sarabun', sans-serif;
   }
   ```

2. **Character Encoding:**
   ```html
   <!-- Must be UTF-8 -->
   <meta charset="UTF-8">
   ```

3. **Database Encoding:**
   ```sql
   -- Check database collation
   sqlite3 data/portal.db "PRAGMA encoding;"
   
   -- Should return "UTF-8"
   ```

4. **Server Encoding:**
   ```bash
   # Check system locale
   locale
   
   # Set UTF-8 if needed
   export LC_ALL=en_US.UTF-8
   export LANG=en_US.UTF-8
   ```

### 🔄 Language Switching Not Persistent

**Problem:** Language resets on page reload

**Solutions:**

1. **Cookie Settings:**
   ```python
   # Check if cookies are being set
   from flask import request
   print(request.cookies.get('language'))
   ```

2. **Browser Cookie Settings:**
   - Enable cookies for the site
   - Check if in private/incognito mode
   - Disable cookie blockers

3. **Domain Issues:**
   ```python
   # Check cookie domain setting
   response.set_cookie('language', lang, domain='your-domain.com')
   ```

---

## Network & Connectivity

### 🌐 Cannot Access from Other Devices

**Problem:** Portal works locally but not from other devices

**Solutions:**

1. **Server Binding:**
   ```bash
   # Correct: Bind to all interfaces
   flask run --host 0.0.0.0 --port 5000
   
   # Wrong: Only localhost
   flask run --host 127.0.0.1 --port 5000
   ```

2. **Firewall Configuration:**
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 5000/tcp
   
   # CentOS/RHEL
   sudo firewall-cmd --add-port=5000/tcp --permanent
   sudo firewall-cmd --reload
   
   # Windows
   # Windows Firewall → Advanced → Inbound Rules → New Rule → Port 5000
   ```

3. **Find Your IP Address:**
   ```bash
   # Linux/macOS
   ip addr show | grep "inet " | grep -v 127.0.0.1
   hostname -I
   
   # macOS specific
   ipconfig getifaddr en0
   
   # Windows
   ipconfig | findstr "IPv4"
   ```

4. **Test Network Access:**
   ```bash
   # From another device on same network
   curl -I http://192.168.1.100:5000
   ping 192.168.1.100
   
   # Check port accessibility
   telnet 192.168.1.100 5000
   ```

### 🔒 HTTPS/SSL Issues

**Problem:** SSL certificate errors or mixed content

**Solutions:**

1. **Development vs Production:**
   ```bash
   # Development: HTTP is fine
   SITE_URL=http://your-ip:5000
   
   # Production: HTTPS required
   SITE_URL=https://your-domain.com
   ```

2. **Mixed Content:**
   ```html
   <!-- Avoid mixing HTTP/HTTPS -->
   <!-- Wrong: -->
   <script src="http://cdn.example.com/script.js"></script>
   
   <!-- Right: -->
   <script src="https://cdn.example.com/script.js"></script>
   ```

3. **Self-signed Certificates:**
   ```bash
   # Create self-signed certificate for testing
   openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
   ```

4. **Let's Encrypt:**
   ```bash
   # Get free SSL certificate
   sudo certbot --nginx -d your-domain.com
   ```

### 📡 Proxy/Reverse Proxy Issues

**Problem:** Portal doesn't work behind nginx/Apache

**Solutions:**

1. **Nginx Configuration:**
   ```nginx
   location / {
       proxy_pass http://127.0.0.1:5000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
   }
   ```

2. **Apache Configuration:**
   ```apache
   ProxyPass / http://127.0.0.1:5000/
   ProxyPassReverse / http://127.0.0.1:5000/
   ProxyPreserveHost On
   ```

3. **Flask Trust Proxy:**
   ```python
   # In app configuration
   from werkzeug.middleware.proxy_fix import ProxyFix
   app.wsgi_app = ProxyFix(app.wsgi_app)
   ```

---

## Database Issues

### 🗄️ Database Corruption

**Problem:** SQLite database corrupted or unusable

**Solutions:**

1. **Check Corruption:**
   ```bash
   sqlite3 data/portal.db "PRAGMA integrity_check;"
   ```

2. **Repair Database:**
   ```bash
   # Backup first
   cp data/portal.db data/portal.db.backup
   
   # Try to repair
   sqlite3 data/portal.db ".recover" | sqlite3 data/portal_recovered.db
   mv data/portal_recovered.db data/portal.db
   ```

3. **Recreate Database:**
   ```bash
   # Last resort: recreate from scratch
   mv data/portal.db data/portal.db.broken
   python -c "from app.database import init_database; init_database()"
   ```

4. **Prevent Future Corruption:**
   ```bash
   # Set proper WAL mode
   sqlite3 data/portal.db "PRAGMA journal_mode=WAL;"
   
   # Enable synchronous mode
   sqlite3 data/portal.db "PRAGMA synchronous=NORMAL;"
   ```

### 💾 Database Locked

**Problem:** "Database is locked" error

**Solutions:**

1. **Find Locking Process:**
   ```bash
   # Check what's using the database
   lsof data/portal.db
   
   # Kill processes if safe
   kill [PID]
   ```

2. **Remove Lock Files:**
   ```bash
   # Stop application first!
   rm -f data/portal.db-wal
   rm -f data/portal.db-shm
   ```

3. **Connection Pooling:**
   ```python
   # In database configuration
   SQLALCHEMY_ENGINE_OPTIONS = {
       'pool_timeout': 20,
       'pool_recycle': 3600
   }
   ```

### 📈 Database Growing Too Large

**Problem:** Database file size increasing rapidly

**Solutions:**

1. **Vacuum Database:**
   ```bash
   sqlite3 data/portal.db "VACUUM;"
   ```

2. **Clean Old Data:**
   ```sql
   -- Remove old log entries (older than 30 days)
   DELETE FROM logs WHERE created_at < date('now', '-30 days');
   
   -- Remove old status history (keep last 100)
   DELETE FROM status WHERE id NOT IN (
     SELECT id FROM status ORDER BY created_at DESC LIMIT 100
   );
   ```

3. **Optimize Configuration:**
   ```sql
   -- Set auto-vacuum
   sqlite3 data/portal.db "PRAGMA auto_vacuum=INCREMENTAL;"
   ```

---

## Security & Access

### 🔐 Admin Access Denied

**Problem:** Cannot access admin panel even with correct credentials

**Solutions:**

1. **Check Basic Auth:**
   ```bash
   # Test with curl
   curl -u admin:your-password http://localhost:5000/admin
   ```

2. **Password Reset:**
   ```bash
   # Generate new password
   NEW_PASS=$(openssl rand -base64 32)
   echo "ADMIN_PASSWORD=$NEW_PASS" >> .env
   echo "New password: $NEW_PASS"
   
   # Restart server
   ```

3. **Session Issues:**
   ```python
   # Check session configuration
   from flask import session
   print(session.get('admin_logged_in'))
   ```

4. **IP Restrictions:**
   ```python
   # Check if IP-based restrictions are enabled
   # Look in routes for IP filtering
   ```

### 🛡️ Security Headers Missing

**Problem:** Security scan shows missing headers

**Solutions:**

1. **Add Security Headers:**
   ```python
   @app.after_request
   def add_security_headers(response):
       response.headers['X-Content-Type-Options'] = 'nosniff'
       response.headers['X-Frame-Options'] = 'DENY'
       response.headers['X-XSS-Protection'] = '1; mode=block'
       return response
   ```

2. **HTTPS Enforcement:**
   ```python
   @app.before_request
   def force_https():
       if not request.is_secure and app.env != 'development':
           return redirect(request.url.replace('http://', 'https://'))
   ```

3. **Content Security Policy:**
   ```python
   response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com"
   ```

---

## Frequently Asked Questions (FAQ)

### General Usage

**Q: Do I need to install an app to use the QR Portal?**
A: No! The portal works directly in any modern web browser. Simply scan the QR code with your phone's camera app.

**Q: Which browsers are supported?**
A: All modern browsers: Chrome 70+, Firefox 65+, Safari 12+, Edge 79+. Internet Explorer is not supported.

**Q: Can I use the portal offline?**
A: Partially. Once loaded, basic information remains available, but updates require an internet connection.

**Q: How often is the information updated?**
A: Information is updated in real-time by the practice staff. There's no delay between admin changes and public visibility.

**Q: Is the portal available 24/7?**
A: Yes, the portal is accessible 24/7, showing current status even when the practice is closed.

### QR Codes

**Q: The QR code won't scan. What should I do?**
A: Try these steps:
1. Clean your camera lens
2. Ensure good lighting
3. Hold steady 6-12 inches from the code
4. Try a different QR scanner app
5. Manually type the URL if scanning fails

**Q: Can I print the QR code?**
A: Yes! Use the high-resolution PNG version from `/qr?size=large` for printing. Minimum print size should be 2x2 cm.

**Q: How do I create QR codes for social media?**
A: Admin panel → Social Media → Generate QR codes for LINE, Facebook, WhatsApp, etc.

### Languages & Localization

**Q: How do I change the language?**
A: Click the flag icons in the top-right corner. Your choice is automatically saved.

**Q: Why doesn't Thai text display correctly?**
A: Ensure your device supports the Sarabun font and has proper UTF-8 encoding. Most modern devices handle this automatically.

**Q: Can I add more languages?**
A: The system is designed for German, Thai, and English. Additional languages require custom development.

### Mobile Usage

**Q: Why is the mobile site slow?**
A: Try these solutions:
1. Switch between WiFi and mobile data
2. Clear your mobile browser cache
3. Restart your browser app
4. Check your internet connection speed

**Q: The mobile layout looks broken.**
A: This usually indicates:
1. Old browser version (update your browser)
2. JavaScript disabled (enable in settings)
3. Poor internet connection (affects CSS loading)

### Admin Panel

**Q: I forgot the admin password. How do I reset it?**
A: 
1. Access your server
2. Edit the `.env` file
3. Change `ADMIN_PASSWORD=new-password-here`
4. Restart the application

**Q: Changes in admin panel don't appear on the public site.**
A: Check these common causes:
1. Browser cache (try hard refresh: Ctrl+F5)
2. Form validation errors (check for red error messages)
3. JavaScript errors (check browser console: F12)
4. Database permissions (contact support)

**Q: Can multiple admins use the system simultaneously?**
A: The current version supports one admin login. Multiple simultaneous logins may cause conflicts.

### Technical Issues

**Q: What happens if the server goes down?**
A: Users will see an error page. Have a backup contact method (phone number on physical signage) for emergencies.

**Q: How do I backup my data?**
A: 
1. Copy the `data/portal.db` file
2. Copy the `config.yml` file  
3. Copy the `.env` file (store securely)
4. Set up automatic daily backups in production

**Q: Can I customize the appearance?**
A: Yes, through:
1. Admin panel settings (logo, colors, basic customization)
2. Custom CSS (advanced users)
3. Theme modifications (requires technical knowledge)

**Q: How do I update to a newer version?**
A: Follow the update procedure in INSTALLATION.md. Always backup first!

### Performance & Scaling

**Q: How many simultaneous users can the system handle?**
A: The basic setup handles 50-100 simultaneous users. For higher traffic, contact support for scaling options.

**Q: Why is the kiosk mode slow?**
A: Kiosk mode auto-refreshes every 60 seconds. Ensure:
1. Stable internet connection
2. Modern display hardware
3. Proper browser settings (no sleep mode)

**Q: Can I run multiple practices on one server?**
A: Each practice needs its own installation. Multi-tenant support requires custom development.

---

## Error Codes Reference

### HTTP Error Codes

**200 OK** - Request successful
**304 Not Modified** - Content not changed (browser cache working)
**400 Bad Request** - Invalid request format
**401 Unauthorized** - Admin login required
**403 Forbidden** - Access denied
**404 Not Found** - Page or resource doesn't exist
**500 Internal Server Error** - Server-side problem
**502 Bad Gateway** - Proxy/reverse proxy issue
**503 Service Unavailable** - Server temporarily down

### Application Error Codes

**APP_001** - Configuration file missing or invalid
**APP_002** - Database connection failed
**APP_003** - Translation file not found
**APP_004** - QR code generation failed
**APP_005** - Image processing error
**APP_006** - Session expired
**APP_007** - Invalid date format
**APP_008** - Missing required field
**APP_009** - Database query failed
**APP_010** - File permission denied

### Database Error Codes

**DB_001** - Database locked
**DB_002** - Database corrupted
**DB_003** - Table not found
**DB_004** - Constraint violation
**DB_005** - Foreign key constraint failed
**DB_006** - Disk space full
**DB_007** - Connection timeout
**DB_008** - Transaction rollback
**DB_009** - Schema version mismatch
**DB_010** - Backup/restore failed

### Network Error Codes

**NET_001** - DNS resolution failed
**NET_002** - Connection timeout
**NET_003** - SSL certificate invalid
**NET_004** - Port blocked by firewall
**NET_005** - Proxy authentication required
**NET_006** - Rate limit exceeded
**NET_007** - IP address blocked
**NET_008** - CDN unavailable
**NET_009** - Network unreachable
**NET_010** - Connection reset

---

## Getting Support

### 📞 Support Channels

**Emergency Support (24/7):**
- Phone: +66 38 123 999
- WhatsApp: +66 38 123 456
- Email: emergency@pattaya-medical.com

**Technical Support (Business Hours):**
- Email: tech@pattaya-medical.com
- Phone: +66 38 123 456 (Mon-Fri 9 AM - 5 PM)
- Support Portal: https://support.pattaya-medical.com

**Community Support:**
- GitHub Issues: https://github.com/Ralle1976/qr-info-portal/issues
- Documentation: https://docs.qr-info-portal.com
- FAQ Database: https://help.qr-info-portal.com

### 📋 Information to Provide

When contacting support, please provide:

**System Information:**
```bash
# Run these commands and include output
python --version
pip list | grep -E "(flask|sqlmodel)"
uname -a                    # Linux/macOS
systeminfo                  # Windows
```

**Application Information:**
- Portal URL
- Current version (check admin panel footer)
- Browser and version
- Device type (mobile, desktop, tablet)
- Error messages (exact text or screenshots)

**Problem Details:**
- What were you trying to do?
- What actually happened?
- When did the problem start?
- Does it happen consistently?
- Have you made any recent changes?

**Log Files:**
```bash
# Include recent log entries
tail -50 server.log
tail -50 /var/log/nginx/error.log  # if using nginx
```

### 🔧 Self-Help Resources

**Before Contacting Support:**

1. **Check This Troubleshooting Guide** - Many common issues are covered here
2. **Search the FAQ** - Look for your specific question
3. **Try Basic Solutions** - Restart browser, clear cache, try different device
4. **Check Status Page** - https://status.qr-info-portal.com (if available)
5. **Review Recent Changes** - Did you change anything recently?

**Documentation Library:**
- User Manual: `docs/USER_MANUAL.md`
- Admin Guide: `docs/ADMIN_GUIDE.md` 
- Installation Guide: `docs/INSTALLATION.md`
- API Documentation: `docs/API.md`

**Video Tutorials:**
- Getting Started: https://videos.qr-info-portal.com/getting-started
- Admin Training: https://videos.qr-info-portal.com/admin-training
- Troubleshooting: https://videos.qr-info-portal.com/troubleshooting

### 🎯 Escalation Process

1. **Level 1** - Self-help using documentation
2. **Level 2** - Community support (GitHub, forums)
3. **Level 3** - Technical support (email/phone)
4. **Level 4** - Emergency support (24/7 hotline)

**SLA (Service Level Agreement):**
- Emergency issues: Response within 2 hours
- Technical issues: Response within 24 hours (business days)
- General questions: Response within 48 hours

---

**📞 Need immediate help?** Call +66 38 123 999  
**📧 Technical questions?** Email tech@pattaya-medical.com  
**📋 Documentation Version:** 1.0.0 | Updated: 2025-08-23

**🔍 Still having issues?** Don't hesitate to reach out - we're here to help!