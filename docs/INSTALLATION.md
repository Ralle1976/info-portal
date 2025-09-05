# 🚀 QR Info Portal - Installation & Setup Guide

**Version:** 1.0.0 | **Last Updated:** 2025-08-23

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Installation](#quick-installation)
3. [Detailed Setup Process](#detailed-setup-process)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [First Run](#first-run)
7. [Network Configuration](#network-configuration)
8. [Production Deployment](#production-deployment)
9. [Docker Installation](#docker-installation)
10. [Troubleshooting Installation](#troubleshooting-installation)
11. [Post-Installation Setup](#post-installation-setup)
12. [Update Procedures](#update-procedures)

---

## System Requirements

### Minimum Requirements

**Hardware:**
- **CPU:** 1 core, 1 GHz
- **RAM:** 512 MB
- **Storage:** 2 GB free space
- **Network:** Broadband internet connection

**Operating System:**
- **Linux:** Ubuntu 20.04+ / CentOS 8+ / Debian 10+
- **Windows:** Windows 10/11, Windows Server 2019+
- **macOS:** macOS 11 Big Sur+

**Software Dependencies:**
- **Python:** 3.11 or higher
- **Git:** Latest version
- **Web Browser:** Modern browser (Chrome, Firefox, Safari, Edge)

### Recommended Requirements

**Hardware:**
- **CPU:** 2+ cores, 2 GHz
- **RAM:** 2 GB
- **Storage:** 10 GB free space (for backups and logs)
- **Network:** Stable broadband with static IP (for LAN access)

**For Production:**
- **CPU:** 4+ cores
- **RAM:** 4+ GB
- **Storage:** 50+ GB (SSD recommended)
- **SSL Certificate:** For HTTPS
- **Backup Storage:** External or cloud backup solution

### Network Requirements

**Ports:**
- **5000:** Default Flask development server
- **80:** HTTP (production with reverse proxy)
- **443:** HTTPS (production)

**External Services:**
- **Google Fonts:** For Sarabun font loading
- **Tailwind CDN:** For CSS framework
- **Font Awesome:** For icons
- **Line/Facebook/WhatsApp APIs:** For social media integration (optional)

---

## Quick Installation

### 🚀 Express Setup (5 Minutes)

For users who want to get running immediately:

```bash
# 1. Clone the repository
git clone https://github.com/Ralle1976/qr-info-portal.git
cd qr-info-portal

# 2. Run the quick setup script
chmod +x setup_and_run.sh
./setup_and_run.sh

# 3. Open your browser
# The script will show you the URL to access the portal
```

The setup script will:
- ✅ Check Python version
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Set up database
- ✅ Create default configuration
- ✅ Start the development server
- ✅ Display access URLs

### Windows Quick Setup

```powershell
# 1. Clone the repository
git clone https://github.com/Ralle1976/qr-info-portal.git
cd qr-info-portal

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
python -c "from app.database import init_database; init_database()"

# 5. Start server
set FLASK_APP=app
flask run --host 0.0.0.0 --port 5000
```

---

## Detailed Setup Process

### Step 1: System Preparation

#### Linux/macOS Preparation

```bash
# Update package manager
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# OR
sudo yum update -y                       # CentOS/RHEL
# OR  
brew update && brew upgrade              # macOS

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3.11-pip -y  # Ubuntu
# OR
brew install python@3.11                # macOS

# Install Git
sudo apt install git -y                 # Ubuntu
# OR
brew install git                         # macOS

# Verify installations
python3.11 --version
git --version
```

#### Windows Preparation

1. **Install Python 3.11+**
   - Download from [python.org](https://python.org/downloads/)
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install for all users"

2. **Install Git**
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Use default settings

3. **Install Visual C++ Redistributable** (if needed)
   - Some Python packages require compilation
   - Download from Microsoft website

#### Verify Prerequisites

```bash
# Check Python version (must be 3.11+)
python3 --version
# or on Windows
python --version

# Check pip
pip --version

# Check Git
git --version

# Check network connectivity
curl -I https://google.com
```

### Step 2: Download and Extract

#### Option A: Git Clone (Recommended)

```bash
# Clone repository
git clone https://github.com/Ralle1976/qr-info-portal.git
cd qr-info-portal

# Check download
ls -la
```

#### Option B: Download ZIP

1. Visit: https://github.com/Ralle1976/qr-info-portal
2. Click "Code" → "Download ZIP"
3. Extract to desired location
4. Open terminal/command prompt in extracted folder

### Step 3: Virtual Environment Setup

#### Why Virtual Environment?

Virtual environments:
- ✅ Isolate project dependencies
- ✅ Prevent conflicts with system Python
- ✅ Allow easy cleanup
- ✅ Enable reproducible deployments

#### Create Virtual Environment

```bash
# Linux/macOS
python3 -m venv .venv

# Windows
python -m venv .venv
```

#### Activate Virtual Environment

```bash
# Linux/macOS
source .venv/bin/activate

# Windows Command Prompt
.venv\Scripts\activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

**Verification:**
- Prompt should show `(.venv)` prefix
- `which python` should point to `.venv/bin/python`

### Step 4: Install Dependencies

```bash
# Ensure virtual environment is activated
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

**Key Dependencies Installed:**
- **Flask:** Web framework
- **SQLModel:** Database ORM
- **qrcode[pil]:** QR code generation
- **python-dotenv:** Environment variable management
- **Jinja2:** Template engine
- **Pillow:** Image processing

### Step 5: Directory Structure Verification

Verify your installation has the correct structure:

```
qr-info-portal/
├── app/                     # Main application code
│   ├── __init__.py
│   ├── models.py           # Database models
│   ├── routes_*.py         # Route handlers
│   ├── services/           # Business logic
│   ├── templates/          # HTML templates
│   └── static/            # CSS, JS, images
├── data/                   # Database storage
├── docs/                   # Documentation
├── config.yml              # Main configuration
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── Dockerfile             # Docker configuration
└── docker-compose.yml     # Docker orchestration
```

---

## Environment Configuration

### Step 1: Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit with your preferred editor
nano .env
# or
vim .env
# or on Windows
notepad .env
```

### Step 2: Configure Environment Variables

#### Basic Configuration

```bash
# Flask Configuration
FLASK_APP=app
FLASK_ENV=development          # Change to 'production' for live deployment
SECRET_KEY=your-super-secret-key-change-this-immediately

# Admin Credentials
ADMIN_PASSWORD=secure-admin-password-here

# Site Configuration  
SITE_URL=http://localhost:5000  # Change to your actual domain
PORT=5000

# Feature Flags
FEATURE_BOOKING=false          # Enable online appointments
FEATURE_SOCIAL_MEDIA=true     # Enable social media integration
FEATURE_LEGAL_EXTENDED=true   # Enable advanced PDPA compliance
FEATURE_KIOSK_SPLIT=true      # Enable multi-screen kiosk support

# Database Configuration
DATABASE_URL=sqlite:///data/portal.db

# Logging
LOG_LEVEL=INFO
```

#### Security Configuration

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output and use as SECRET_KEY

# Create strong admin password
# Use a password manager or generate with:
openssl rand -base64 32
```

#### Production Environment Variables

```bash
# Production settings
FLASK_ENV=production
DEBUG=False
SITE_URL=https://your-domain.com

# Security headers
FORCE_HTTPS=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True

# Performance
CACHE_TIMEOUT=3600
ENABLE_COMPRESSION=True

# External services (optional)
LINE_CHANNEL_SECRET=your-line-channel-secret
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

### Step 3: Validate Configuration

```bash
# Test configuration loading
python -c "from app import create_app; app = create_app(); print('Config loaded successfully')"

# Check environment variables
python -c "import os; print('SECRET_KEY set:', bool(os.getenv('SECRET_KEY')))"
```

---

## Database Setup

### Automatic Database Initialization

```bash
# Initialize database with default data
python -c "from app.database import init_database; init_database()"
```

This creates:
- ✅ Database file at `data/portal.db`
- ✅ Required tables (status, hours, announcements, etc.)
- ✅ Default configuration data
- ✅ Sample data for testing

### Manual Database Setup

If automatic setup fails:

```bash
# Create data directory
mkdir -p data

# Initialize database manually
python -c "
from app import create_app
from app.database import db, init_db
app = create_app()
with app.app_context():
    init_db()
    print('Database initialized successfully')
"
```

### Database Verification

```bash
# Check database file exists
ls -la data/portal.db

# Test database connection
python -c "
import sqlite3
conn = sqlite3.connect('data/portal.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
tables = cursor.fetchall()
print('Tables created:', [table[0] for table in tables])
conn.close()
"
```

### Initial Data Setup

```bash
# Load sample configuration
python -c "
from app import create_app
from app.services.status import StatusService
app = create_app()
with app.app_context():
    StatusService.set_status('ANWESEND', None, None, 'Initial setup complete')
    print('Default status set')
"
```

---

## First Run

### Start Development Server

```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Start the development server
FLASK_APP=app flask run --host 0.0.0.0 --port 5000

# Alternative using Python directly
python run.py
```

**Expected Output:**
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[your-local-ip]:5000
```

### Test Local Access

1. **Open browser and navigate to:**
   ```
   http://127.0.0.1:5000
   ```

2. **Verify functionality:**
   - ✅ Homepage loads with status banner
   - ✅ Language switcher works (DE/TH/EN)
   - ✅ Week/Month views accessible
   - ✅ Kiosk modes work (`/kiosk/single`, `/kiosk/triple`)

3. **Test admin access:**
   ```
   http://127.0.0.1:5000/admin
   ```
   - Username: `admin`
   - Password: (from your `.env` file)

### First-Run Checklist

- [ ] Homepage loads without errors
- [ ] All three languages display correctly
- [ ] Admin panel accessible with credentials
- [ ] QR codes generate properly (`/qr`, `/qr.svg`)
- [ ] Kiosk modes display correctly
- [ ] Mobile view responsive
- [ ] No JavaScript console errors

---

## Network Configuration

### Local Network Access

To access the portal from other devices on your network:

#### Find Your IP Address

```bash
# Linux
hostname -I | awk '{print $1}'

# macOS
ipconfig getifaddr en0

# Windows Command Prompt
ipconfig | findstr "IPv4"

# Windows PowerShell
(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi").IPAddress
```

#### Configure Firewall

**Linux (UFW):**
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

**Windows:**
1. Windows Security → Firewall & network protection
2. Advanced settings → Inbound Rules → New Rule
3. Port → TCP → Specific local ports: 5000
4. Allow the connection

**macOS:**
1. System Preferences → Security & Privacy → Firewall
2. Firewall Options → Add application
3. Select Python or allow incoming connections

#### Test Network Access

```bash
# Replace [YOUR-IP] with your actual IP address
curl -I http://[YOUR-IP]:5000

# Test from another device on same network
# Open browser to: http://[YOUR-IP]:5000
```

### Router Configuration (Optional)

For external internet access:

1. **Port Forwarding:**
   - Forward external port 80 → internal port 5000
   - Forward external port 443 → internal port 5000 (for HTTPS)

2. **Dynamic DNS:** 
   - Use service like DynDNS, No-IP, or DuckDNS
   - Update `.env` with `SITE_URL=https://your-ddns-domain.com`

3. **SSL Certificate:**
   - Use Let's Encrypt for free certificates
   - Configure reverse proxy (nginx/Apache)

---

## Production Deployment

### Preparation for Production

#### Security Hardening

```bash
# 1. Change environment to production
echo "FLASK_ENV=production" >> .env
echo "DEBUG=False" >> .env

# 2. Generate new secret key
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
echo "SECRET_KEY=$SECRET_KEY" >> .env

# 3. Set strong admin password
echo "ADMIN_PASSWORD=$(openssl rand -base64 32)" >> .env

# 4. Configure HTTPS
echo "FORCE_HTTPS=True" >> .env
```

#### Performance Optimization

```bash
# Install production WSGI server
pip install gunicorn

# Create gunicorn configuration
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:5000"
workers = 2
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
EOF
```

### Production Server Options

#### Option 1: Gunicorn (Recommended)

```bash
# Start with gunicorn
gunicorn -c gunicorn.conf.py app:create_app()

# Or with custom settings
gunicorn --bind 0.0.0.0:5000 --workers 2 'app:create_app()'
```

#### Option 2: uWSGI

```bash
# Install uWSGI
pip install uwsgi

# Create uwsgi.ini
cat > uwsgi.ini << EOF
[uwsgi]
module = app:create_app()
callable = app
master = true
processes = 2
socket = /tmp/qr-portal.sock
chmod-socket = 664
vacuum = true
die-on-term = true
EOF

# Run with uWSGI
uwsgi --ini uwsgi.ini
```

### Reverse Proxy Setup

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Proxy to Flask app
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files (optional optimization)
    location /static {
        alias /path/to/qr-info-portal/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### SSL Certificate Setup

#### Let's Encrypt (Free SSL)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### Process Management

#### Systemd Service

```ini
# /etc/systemd/system/qr-portal.service
[Unit]
Description=QR Info Portal
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/qr-info-portal
Environment=PATH=/path/to/qr-info-portal/.venv/bin
ExecStart=/path/to/qr-info-portal/.venv/bin/gunicorn -c gunicorn.conf.py 'app:create_app()'
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable qr-portal
sudo systemctl start qr-portal
sudo systemctl status qr-portal
```

---

## Docker Installation

### Benefits of Docker Deployment

- ✅ Consistent environment across systems
- ✅ Easy scaling and updates
- ✅ Isolated dependencies
- ✅ Simple backup and restore
- ✅ Production-ready configuration

### Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Single Container Deployment

```bash
# Build the image
docker build -t qr-info-portal .

# Run container
docker run -d \
  --name qr-portal \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.yml:/app/config.yml \
  --env-file .env \
  qr-info-portal

# Check container status
docker ps
docker logs qr-portal
```

### Docker Compose Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update and restart
docker-compose pull
docker-compose up -d --build
```

#### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build: .
    restart: always
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./config.yml:/app/config.yml
      - ./backups:/app/backups
    env_file:
      - .env
    environment:
      - FLASK_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app

  backup:
    image: alpine
    restart: "no"
    volumes:
      - ./data:/data:ro
      - ./backups:/backups
    command: |
      sh -c '
        while true; do
          cp /data/portal.db "/backups/portal-$(date +%Y%m%d_%H%M%S).db"
          find /backups -name "portal-*.db" -mtime +30 -delete
          sleep 86400
        done
      '
```

### Docker Management Commands

```bash
# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs app nginx

# Execute commands in container
docker-compose exec app python -c "from app.database import init_database; init_database()"

# Backup data
docker-compose exec app cp data/portal.db backups/manual-backup-$(date +%Y%m%d).db

# Update application
git pull
docker-compose build --no-cache
docker-compose up -d
```

---

## Troubleshooting Installation

### Common Installation Issues

#### Python Version Issues

**Problem:** "Python 3.11 or higher required"
```bash
# Solution: Install correct Python version
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv

# Verify
python3.11 --version
```

#### Permission Errors

**Problem:** Permission denied errors
```bash
# Linux/macOS - Fix permissions
sudo chown -R $USER:$USER qr-info-portal/
chmod +x setup_and_run.sh

# Windows - Run as administrator
# Right-click Command Prompt → "Run as administrator"
```

#### Virtual Environment Issues

**Problem:** Virtual environment activation fails
```bash
# Delete and recreate
rm -rf .venv
python3 -m venv .venv

# Windows PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Package Installation Failures

**Problem:** pip install fails
```bash
# Update pip
pip install --upgrade pip

# Install with specific index
pip install -r requirements.txt --index-url https://pypi.org/simple/

# Install individually if needed
pip install flask sqlmodel qrcode[pil] python-dotenv jinja2
```

#### Database Creation Errors

**Problem:** Database initialization fails
```bash
# Check permissions
ls -la data/
chmod 755 data/

# Manual database creation
python -c "
import sqlite3
conn = sqlite3.connect('data/portal.db')
conn.close()
print('Database file created')
"
```

### Network and Access Issues

#### Port Already in Use

**Problem:** "Address already in use" error
```bash
# Find process using port 5000
sudo lsof -i :5000          # Linux/macOS
netstat -ano | findstr :5000 # Windows

# Kill process
sudo kill -9 [PID]          # Linux/macOS
taskkill /PID [PID] /F      # Windows

# Use different port
flask run --port 5001
```

#### Firewall Blocking Access

**Problem:** Cannot access from other devices
```bash
# Check if service is running
curl http://localhost:5000

# Test with IP address
curl http://[YOUR-IP]:5000

# Temporarily disable firewall for testing
sudo ufw disable           # Linux
# Windows: Disable Windows Defender Firewall
```

#### DNS Resolution Issues

**Problem:** External access not working
```bash
# Check external IP
curl ifconfig.me

# Test port forwarding
telnet your-external-ip 5000

# Verify router port forwarding configuration
```

### Configuration Issues

#### Environment Variables Not Loading

**Problem:** Config values not applied
```bash
# Check .env file exists
ls -la .env

# Test loading
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('SECRET_KEY:', bool(os.getenv('SECRET_KEY')))
print('ADMIN_PASSWORD:', bool(os.getenv('ADMIN_PASSWORD')))
"
```

#### Configuration File Errors

**Problem:** config.yml parsing errors
```bash
# Validate YAML syntax
python -c "
import yaml
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
    print('Config loaded successfully')
    print('Site name:', config['site']['name'])
"
```

### Performance Issues

#### Slow Startup

**Problem:** Application takes long to start
```bash
# Check system resources
free -m              # Memory usage
df -h                # Disk space
top                  # CPU usage

# Reduce debug logging
echo "LOG_LEVEL=WARNING" >> .env
```

#### High Memory Usage

**Problem:** Excessive memory consumption
```bash
# Monitor memory usage
ps aux | grep python
htop                 # Interactive process monitor

# Restart with memory limits
docker run --memory=512m qr-info-portal
```

### Getting Help

#### Diagnostic Information Collection

```bash
# System info
uname -a                    # System information
python3 --version          # Python version
pip --version              # Pip version
free -m                    # Memory info
df -h                      # Disk space

# Application info
ls -la                     # Directory contents
cat .env                   # Environment variables (hide secrets)
tail -n 50 server.log      # Recent log entries
```

#### Log Collection

```bash
# Application logs
tail -f server.log

# System logs
sudo journalctl -u qr-portal -f    # If using systemd

# Docker logs
docker logs qr-portal
docker-compose logs -f
```

#### Support Channels

**Technical Support:**
- Email: tech@pattaya-medical.com
- GitHub Issues: Report bugs with logs
- Documentation: Check all docs/ files first

**Emergency Support:**
- Phone: +66 38 123 999 (24/7)
- WhatsApp: +66 38 123 456

---

## Post-Installation Setup

### Essential First Steps

#### 1. Admin Panel Configuration

```bash
# Access admin panel
open http://localhost:5000/admin
# Login: admin / [your-password]
```

**Required Settings:**
- [ ] Change admin password
- [ ] Set practice name and contact info
- [ ] Configure opening hours
- [ ] Set initial status
- [ ] Test QR code generation

#### 2. Content Localization

**Multi-language Setup:**
- [ ] Review German translations
- [ ] Add/edit Thai translations  
- [ ] Customize English content
- [ ] Test language switching

#### 3. QR Code Setup

```bash
# Test QR generation
curl http://localhost:5000/qr -o test-qr.png
curl http://localhost:5000/qr.svg -o test-qr.svg

# Print test QR codes
# Open files and print for physical testing
```

#### 4. Mobile Testing

Test on actual mobile devices:
- [ ] QR code scanning
- [ ] Mobile responsive layout
- [ ] Touch interface
- [ ] Font readability (especially Thai)

### Network Deployment

#### 1. LAN Access Setup

```bash
# Find your IP
ip addr show | grep "inet " | grep -v 127.0.0.1

# Start server for LAN access
flask run --host 0.0.0.0 --port 5000

# Test from other devices
# http://[YOUR-IP]:5000
```

#### 2. Print QR Codes

Create printable QR codes for door signage:

```bash
# High-resolution QR for printing
curl "http://localhost:5000/qr?size=large" -o door-qr-large.png

# Test scan with various apps
# - iOS Camera
# - Android Camera/Google Lens
# - LINE QR scanner
# - WhatsApp QR scanner
```

### Monitoring and Maintenance

#### 1. Setup Monitoring

```bash
# Create monitoring script
cat > check_portal.sh << 'EOF'
#!/bin/bash
URL="http://localhost:5000/healthz"
if curl -f -s $URL > /dev/null; then
    echo "$(date): Portal is running"
else
    echo "$(date): Portal is DOWN!" >> errors.log
    # Optionally restart service
    # systemctl restart qr-portal
fi
EOF

chmod +x check_portal.sh

# Add to crontab for every 5 minutes
echo "*/5 * * * * /path/to/qr-info-portal/check_portal.sh" | crontab -
```

#### 2. Backup Strategy

```bash
# Create backup script
cat > backup_portal.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup database
cp data/portal.db "$BACKUP_DIR/portal.db"

# Backup configuration
cp config.yml "$BACKUP_DIR/config.yml"
cp .env "$BACKUP_DIR/env.txt"

# Create archive
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR/"
rm -rf "$BACKUP_DIR/"

echo "Backup created: $BACKUP_DIR.tar.gz"

# Keep only last 30 days of backups
find backups/ -name "*.tar.gz" -mtime +30 -delete
EOF

chmod +x backup_portal.sh

# Daily backups
echo "0 2 * * * /path/to/qr-info-portal/backup_portal.sh" | crontab -
```

### Production Optimization

#### 1. Performance Tuning

```bash
# Add to .env for production
echo "CACHE_TIMEOUT=3600" >> .env
echo "ENABLE_GZIP=True" >> .env
echo "OPTIMIZE_IMAGES=True" >> .env
```

#### 2. Security Hardening

```bash
# Restrict file permissions
chmod 600 .env
chmod 700 data/
chmod 644 config.yml

# Setup log rotation
sudo logrotate -f /etc/logrotate.d/qr-portal
```

### Final Verification

#### Complete System Test

- [ ] **Public Access:** Homepage loads from external device
- [ ] **Admin Access:** Login and configuration changes work
- [ ] **QR Codes:** Generate and scan successfully  
- [ ] **Languages:** All three languages display correctly
- [ ] **Mobile:** Responsive design works on phones/tablets
- [ ] **Kiosk:** Full-screen modes work on larger displays
- [ ] **Social Media:** QR codes for platforms generate correctly
- [ ] **Performance:** Page loads under 3 seconds on mobile
- [ ] **Backup:** Automatic backups working
- [ ] **Monitoring:** Health checks functioning

#### Documentation Check

- [ ] Read USER_MANUAL.md
- [ ] Review ADMIN_GUIDE.md  
- [ ] Understand troubleshooting procedures
- [ ] Know how to update the system
- [ ] Have emergency contact information

---

## Update Procedures

### Application Updates

#### Standard Update Process

```bash
# 1. Backup current installation
./backup_portal.sh

# 2. Pull latest changes
git pull origin main

# 3. Update dependencies
source .venv/bin/activate
pip install -r requirements.txt --upgrade

# 4. Run database migrations (if any)
python -c "from app.database import migrate_database; migrate_database()"

# 5. Restart application
# For systemd:
sudo systemctl restart qr-portal

# For Docker:
docker-compose down && docker-compose up -d --build

# For development:
# Stop server (Ctrl+C) and restart
flask run --host 0.0.0.0 --port 5000
```

#### Emergency Rollback

```bash
# If update fails, restore from backup
cp backups/latest/portal.db data/portal.db
cp backups/latest/config.yml config.yml

# Revert to previous version
git log --oneline -5                    # Find previous commit
git reset --hard [previous-commit-hash]

# Restart service
sudo systemctl restart qr-portal
```

### System Updates

#### Operating System Updates

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL  
sudo yum update -y

# After OS updates, verify application
curl http://localhost:5000/healthz
```

#### Python Updates

```bash
# Check current Python version
python3 --version

# After Python updates, recreate virtual environment
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

**📞 Installation Support:** tech@pattaya-medical.com  
**📞 Emergency Support:** +66 38 123 999  
**📋 Documentation Version:** 1.0.0 | Updated: 2025-08-23