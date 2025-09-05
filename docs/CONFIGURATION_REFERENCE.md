# ⚙️ QR Info Portal - Configuration Reference Guide

**Version:** 1.0.0 | **Last Updated:** 2025-08-23

---

## 📋 Table of Contents

1. [Configuration Overview](#configuration-overview)
2. [Environment Variables (.env)](#environment-variables-env)
3. [Main Configuration (config.yml)](#main-configuration-configyml)
4. [Database Configuration](#database-configuration)
5. [Feature Flags](#feature-flags)
6. [Localization Settings](#localization-settings)
7. [Social Media Configuration](#social-media-configuration)
8. [Appointment System Configuration](#appointment-system-configuration)
9. [Legal Compliance Settings](#legal-compliance-settings)
10. [Performance & Caching](#performance--caching)
11. [Security Configuration](#security-configuration)
12. [Logging Configuration](#logging-configuration)
13. [Deployment Configurations](#deployment-configurations)
14. [Validation & Testing](#validation--testing)
15. [Configuration Examples](#configuration-examples)
16. [Migration & Updates](#migration--updates)

---

## Configuration Overview

The QR Info Portal uses a layered configuration system:

1. **Environment Variables (.env)** - System settings, secrets, deployment-specific values
2. **Main Configuration (config.yml)** - Business logic, content, user-configurable settings
3. **Runtime Configuration** - Dynamic settings stored in database
4. **Default Values** - Fallback values embedded in code

### Configuration Priority

```
Runtime DB Settings > Environment Variables > config.yml > Default Values
```

### Configuration Files Location

```
qr-info-portal/
├── .env                    # Environment variables (DO NOT commit)
├── .env.example           # Template for environment variables
├── config.yml             # Main configuration (safe to commit)
└── app/
    ├── config.py          # Configuration loading logic
    └── default_config.py  # Default values
```

---

## Environment Variables (.env)

### Flask Configuration

```bash
# Flask Application Settings
FLASK_APP=app
FLASK_ENV=production                    # development|testing|production
FLASK_DEBUG=false                       # true|false
SECRET_KEY=your-super-secret-key-here   # Required: Generate with openssl rand -base64 32

# Server Settings
HOST=0.0.0.0                           # Listen on all interfaces
PORT=5000                              # Port number
WORKERS=2                              # Number of worker processes (production)
```

**Secret Key Generation:**
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
# OR
openssl rand -base64 32
```

### Site Configuration

```bash
# Site Information
SITE_URL=https://your-domain.com        # Full URL (used for QR codes, emails)
SITE_NAME="Labor Pattaya"               # Site display name
SITE_DESCRIPTION="Medical Laboratory"   # SEO description

# Contact Information
ADMIN_EMAIL=admin@your-domain.com       # Administrative contact
SUPPORT_EMAIL=support@your-domain.com   # User support contact
EMERGENCY_PHONE=+66123456789            # Emergency contact number
```

### Authentication & Security

```bash
# Admin Authentication
ADMIN_USERNAME=admin                    # Default: admin
ADMIN_PASSWORD=secure-password-here     # Required: Strong password

# Security Settings  
SESSION_TIMEOUT=3600                    # Session timeout in seconds
MAX_LOGIN_ATTEMPTS=5                    # Max failed login attempts
LOGIN_LOCKOUT_DURATION=900              # Lockout duration in seconds (15 min)

# Password Requirements
MIN_PASSWORD_LENGTH=12                  # Minimum password length
REQUIRE_PASSWORD_COMPLEXITY=true        # Require special chars, numbers, etc.

# SSL/HTTPS
FORCE_HTTPS=false                       # Redirect HTTP to HTTPS (production: true)
HSTS_MAX_AGE=31536000                   # HTTP Strict Transport Security
```

### Database Configuration

```bash
# Database Settings
DATABASE_URL=sqlite:///data/portal.db   # Database connection string
DATABASE_POOL_SIZE=10                   # Connection pool size
DATABASE_POOL_TIMEOUT=30                # Pool timeout in seconds
DATABASE_POOL_RECYCLE=3600              # Recycle connections after seconds

# Backup Settings
AUTO_BACKUP=true                        # Enable automatic backups
BACKUP_INTERVAL=86400                   # Backup interval in seconds (24 hours)
BACKUP_RETENTION_DAYS=30                # Keep backups for days
BACKUP_LOCATION=backups/                # Backup directory
```

### Feature Flags

```bash
# Core Features
FEATURE_KIOSK_MODE=true                 # Enable kiosk display modes
FEATURE_SOCIAL_MEDIA=true               # Enable social media integration
FEATURE_QR_GENERATION=true              # Enable QR code generation
FEATURE_MULTI_LANGUAGE=true             # Enable multi-language support

# Advanced Features
FEATURE_BOOKING=false                   # Enable appointment booking system
FEATURE_ANALYTICS=false                 # Enable visitor analytics
FEATURE_API_ACCESS=true                 # Enable API endpoints
FEATURE_WEBHOOKS=false                  # Enable webhook system
FEATURE_PUSH_NOTIFICATIONS=false        # Enable push notifications

# Legal Compliance
FEATURE_LEGAL_EXTENDED=true             # Enable PDPA/GDPR compliance
FEATURE_COOKIE_CONSENT=true             # Enable cookie consent management
FEATURE_DATA_REQUESTS=true              # Enable data access/deletion requests
```

### External Services

```bash
# Email Settings (for notifications)
SMTP_SERVER=smtp.gmail.com              # SMTP server
SMTP_PORT=587                           # SMTP port
SMTP_USERNAME=your-email@gmail.com      # SMTP username
SMTP_PASSWORD=your-app-password         # SMTP password
SMTP_USE_TLS=true                       # Use TLS encryption
SMTP_FROM_ADDRESS=noreply@your-domain.com # From address

# SMS Settings (for appointment reminders)
SMS_PROVIDER=twilio                     # twilio|nexmo|aws_sns
SMS_API_KEY=your-api-key               # Provider API key
SMS_API_SECRET=your-api-secret         # Provider API secret
SMS_FROM_NUMBER=+66123456789           # Sender number

# Cloud Storage (for backups)
AWS_ACCESS_KEY_ID=your-access-key      # AWS credentials
AWS_SECRET_ACCESS_KEY=your-secret-key  # AWS secret
AWS_REGION=ap-southeast-1              # AWS region
S3_BUCKET=qr-portal-backups            # S3 bucket for backups

# CDN Settings
CDN_URL=https://cdn.your-domain.com    # CDN URL for static assets
CDN_ENABLED=false                      # Enable CDN usage
```

### Logging & Monitoring

```bash
# Logging Configuration
LOG_LEVEL=INFO                         # DEBUG|INFO|WARNING|ERROR|CRITICAL
LOG_FILE=logs/app.log                  # Log file path
LOG_MAX_SIZE=10485760                  # Max log file size (10MB)
LOG_BACKUP_COUNT=5                     # Number of log files to keep
LOG_FORMAT=detailed                    # simple|detailed|json

# Monitoring
SENTRY_DSN=                            # Sentry DSN for error tracking (optional)
HEALTH_CHECK_TOKEN=                    # Token for health check endpoint
METRICS_ENABLED=false                  # Enable metrics collection
```

### Performance Settings

```bash
# Caching
CACHE_TYPE=simple                      # simple|redis|memcached
CACHE_DEFAULT_TIMEOUT=300              # Cache timeout in seconds
REDIS_URL=redis://localhost:6379/0     # Redis connection (if using Redis cache)

# Rate Limiting
RATE_LIMIT_ENABLED=true                # Enable rate limiting
RATE_LIMIT_STORAGE_URL=redis://localhost:6379/1 # Storage for rate limits

# Performance
ENABLE_GZIP=true                       # Enable gzip compression
OPTIMIZE_IMAGES=true                   # Optimize images on upload
PRELOAD_TEMPLATES=true                 # Preload Jinja templates
```

---

## Main Configuration (config.yml)

### Site Information

```yaml
site:
  # Basic site information
  name: "ห้องปฏิบัติการพัทยา – เจาะเลือด"  # Site name in default language
  tagline: "Professional Medical Laboratory"   # Optional tagline
  description: "Medical laboratory services in Pattaya, Thailand"
  
  # Language configuration
  languages: ["th", "de", "en"]              # Supported languages
  default_language: "th"                     # Default language
  fallback_language: "en"                    # Fallback if translation missing
  
  # Regional settings
  timezone: "Asia/Bangkok"                   # Timezone for all dates/times
  currency: "THB"                            # Currency code
  country_code: "TH"                         # ISO country code
  locale: "th_TH"                           # System locale
  
  # Display settings
  theme: "thai"                             # UI theme: thai|medical|modern
  color_scheme: "light"                     # light|dark|auto
  font_family: "Sarabun"                    # Primary font family
  
  # Branding
  logo_url: "/static/img/logo.png"          # Path to logo file
  favicon_url: "/static/img/favicon.ico"    # Path to favicon
  apple_touch_icon_url: "/static/img/apple-touch-icon.png"
```

### Location & Contact

```yaml
location:
  # Physical address
  name: "Labor Pattaya"                     # Business name
  address: "Soi Buakhao, Pattaya"          # Street address
  city: "Pattaya"                           # City
  state: "Chonburi"                         # State/Province
  postal_code: "20150"                      # Postal code
  country: "Thailand"                       # Country name
  
  # GPS coordinates
  latitude: 12.923556                       # Latitude (decimal degrees)
  longitude: 100.882507                     # Longitude (decimal degrees)
  maps_link: "https://maps.google.com/?q=12.923556,100.882507"
  
  # Alternative maps
  apple_maps_link: "maps://maps.apple.com/?q=12.923556,100.882507"
  waze_link: "https://waze.com/ul?ll=12.923556,100.882507"
  
  # Directions & transport
  public_transport:
    - type: "songthaew"
      route: "Route 1 to Buakhao"
      fare_thb: 10
    - type: "motorcycle_taxi"
      note: "Available at main roads"
      fare_thb: 20-40
  
  parking:
    available: true
    type: "street"                          # street|private|paid
    note:
      th: "จอดรถข้างถนนได้"
      de: "Straßenparkplätze verfügbar"
      en: "Street parking available"

contact:
  # Primary contact methods
  phone: "+66 38 123 456"                   # Main phone number
  phone_display: "038-123-456"              # Display format
  whatsapp: "+66 38 123 456"                # WhatsApp number
  line: "@laborpattaya"                     # LINE official account
  
  # Email addresses
  email: "labor@pattaya-medical.com"        # General email
  appointments_email: "termine@pattaya-medical.com" # Appointments
  info_email: "info@pattaya-medical.com"    # Information requests
  
  # Emergency contact
  emergency_phone: "+66 38 123 999"         # Emergency number
  after_hours_phone: "+66 81 234 5678"      # After hours contact
  
  # Website & social
  website: "https://pattaya-medical.com"    # Main website
  booking_url: "https://booking.pattaya-medical.com" # Online booking (if available)
  
  # Business hours for phone
  phone_hours:
    mon: "08:00-17:00"
    tue: "08:00-17:00"
    wed: "08:00-12:00"
    thu: "08:00-17:00"
    fri: "08:00-16:00"
    sat: []
    sun: []
```

### Services Configuration

```yaml
services:
  # Standard services offered
  standard:
    - service_id: "BLOOD_TEST"
      name:
        th: "เจาะเลือด"
        de: "Blutabnahme"
        en: "Blood Test"
      description:
        th: "การเจาะเลือดเพื่อตรวจวิเคราะห์ทางการแพทย์"
        de: "Blutentnahme für medizinische Laboruntersuchungen"
        en: "Blood sampling for medical laboratory analysis"
      duration_minutes: 30                  # Typical duration
      preparation_required: true            # Requires preparation
      preparation_instructions:
        th: "งดอาหาร 8-12 ชั่วโมงก่อนตรวจ"
        de: "8-12 Stunden vor der Untersuchung nüchtern"
        en: "Fasting 8-12 hours before examination"
      price_thb: 500                        # Price in Thai Baht
      price_display: "500 บาท"              # Display format
      available: true                       # Currently available
      booking_required: true                # Requires appointment
      
    - service_id: "CONSULTATION"
      name:
        th: "ปรึกษาแพทย์"
        de: "Ärztliche Beratung"
        en: "Medical Consultation"
      description:
        th: "การปรึกษาและให้คำแนะนำทางการแพทย์"
        de: "Medizinische Beratung und Aufklärung"
        en: "Medical consultation and advice"
      duration_minutes: 45
      preparation_required: false
      price_thb: 800
      price_display: "800 บาท"
      available: true
      booking_required: true
      
  # Service categories
  categories:
    - id: "laboratory"
      name:
        th: "บริการห้องปฏิบัติการ"
        de: "Labordienstleistungen"
        en: "Laboratory Services"
      services: ["BLOOD_TEST", "URINE_TEST", "STOOL_TEST"]
      
    - id: "consultation"
      name:
        th: "บริการให้คำปรึกษา"
        de: "Beratungsleistungen"  
        en: "Consultation Services"
      services: ["CONSULTATION", "FOLLOW_UP"]
  
  # Special notes
  notes:
    th: "บริการอื่นๆ สอบถามได้ที่เคาน์เตอร์"
    de: "Weitere Leistungen auf Anfrage verfügbar"
    en: "Additional services available upon request"
```

### Operating Hours

```yaml
hours:
  # Standard weekly schedule
  weekly:
    monday:
      - "08:30-12:00"                       # Morning session
      - "13:00-16:00"                       # Afternoon session
    tuesday:
      - "08:30-12:00"
      - "13:00-16:00"
    wednesday:
      - "08:30-12:00"                       # Half day
    thursday:
      - "08:30-12:00"
      - "13:00-16:00"
    friday:
      - "08:30-13:00"                       # Extended morning
    saturday: []                            # Closed
    sunday: []                              # Closed
  
  # Special schedule variations
  variations:
    # First week of month - extended hours
    first_week:
      enabled: true
      friday:
        - "08:30-12:00"
        - "13:00-17:00"                     # Extended Friday
    
    # Last week of month - shortened hours
    last_week:
      enabled: true
      friday:
        - "08:30-12:00"                     # Morning only
  
  # Lunch break settings
  lunch_break:
    enabled: true
    start: "12:00"
    end: "13:00"
    note:
      th: "ช่วงพักกลางวัน"
      de: "Mittagspause"
      en: "Lunch break"
  
  # Appointment slots
  appointment_slots:
    duration_minutes: 30                    # Default slot duration
    buffer_minutes: 10                      # Buffer between appointments
    advance_booking_days: 14                # How far in advance to book
    same_day_booking: false                 # Allow same-day booking
  
  # Holiday handling
  holidays:
    # Automatic holiday recognition
    recognize_thai_holidays: true           # Auto-detect Thai public holidays
    recognize_christian_holidays: false     # Christmas, Easter, etc.
    recognize_chinese_holidays: true        # Chinese New Year, etc.
    
    # Custom holidays
    custom_holidays:
      - date: "2025-12-24"
        name:
          th: "วันคริสต์มาสอีฟ"
          de: "Heiligabend"
          en: "Christmas Eve"
        closed: true
        
      - date: "2025-12-31"
        name:
          th: "วันสิ้นปี"
          de: "Silvester"
          en: "New Year's Eve"
        hours: ["08:30-12:00"]              # Special hours
        
  # Exceptions (overrides weekly schedule)
  exceptions:
    # Vacation periods
    - date_range:
        start: "2025-09-15"
        end: "2025-09-22"
      closed: true
      reason:
        th: "ลาพักร้อน"
        de: "Urlaub"
        en: "Vacation"
      
    # Training days
    - date: "2025-10-15"
      closed: true
      reason:
        th: "อบรมเชิงปฏิบัติการ"
        de: "Fortbildungsveranstaltung"
        en: "Training workshop"
      
    # Extended hours for special events
    - date: "2025-11-01"
      hours: ["08:00-18:00"]
      reason:
        th: "วันตรวจสุขภาพพิเศษ"
        de: "Sonderuntersuchungstag"
        en: "Special health screening day"
```

### Status Configuration

```yaml
status:
  # Current status
  current:
    type: "ANWESEND"                        # Current status type
    valid_from: null                        # When this status started
    valid_until: null                       # When this status ends
    note: null                              # Optional note
    auto_update: true                       # Auto-update based on schedule
  
  # Status types configuration
  types:
    ANWESEND:
      color: "#10B981"                      # Green
      icon: "fas fa-check-circle"
      priority: 1                           # Display priority (1 = highest)
      auto_message: true                    # Generate automatic message
      
    GESCHLOSSEN:
      color: "#EF4444"                      # Red
      icon: "fas fa-times-circle"
      priority: 2
      auto_message: true
      
    URLAUB:
      color: "#F59E0B"                      # Amber
      icon: "fas fa-umbrella-beach"
      priority: 3
      requires_dates: true                  # Requires start/end dates
      show_return_date: true                # Show "back on" date
      
    BILDUNGSURLAUB:
      color: "#3B82F6"                      # Blue
      icon: "fas fa-graduation-cap"
      priority: 4
      requires_dates: true
      show_return_date: true
      
    KONGRESS:
      color: "#8B5CF6"                      # Purple
      icon: "fas fa-users"
      priority: 5
      requires_dates: true
      show_return_date: true
      
    SONSTIGES:
      color: "#6B7280"                      # Gray
      icon: "fas fa-info-circle"
      priority: 6
      requires_note: true                   # Must have explanation
  
  # Automatic status updates
  automation:
    enabled: true
    rules:
      # Automatically close during non-business hours
      - trigger: "time_based"
        condition: "outside_hours"
        action: "set_status"
        status: "GESCHLOSSEN"
        message:
          th: "นอกเวลาทำการ"
          de: "Außerhalb der Öffnungszeiten"
          en: "Outside business hours"
      
      # Automatically open during business hours (if not on vacation)
      - trigger: "time_based"
        condition: "business_hours"
        action: "set_status"
        status: "ANWESEND"
        exclude_statuses: ["URLAUB", "BILDUNGSURLAUB", "KONGRESS"]
```

### Announcement System

```yaml
announcements:
  # System settings
  max_active: 5                             # Maximum active announcements
  default_priority: "medium"                # Default priority level
  auto_expire: true                         # Auto-expire old announcements
  expire_after_days: 30                     # Days until auto-expiry
  
  # Priority levels
  priorities:
    high:
      color: "#EF4444"                      # Red
      icon: "fas fa-exclamation-circle"
      show_badge: true
      auto_highlight: true
      
    medium:
      color: "#F59E0B"                      # Amber
      icon: "fas fa-info-circle"
      show_badge: false
      auto_highlight: false
      
    low:
      color: "#10B981"                      # Green
      icon: "fas fa-lightbulb"
      show_badge: false
      auto_highlight: false
  
  # Display settings
  display:
    max_homepage: 3                         # Max announcements on homepage
    max_kiosk: 2                            # Max announcements in kiosk mode
    show_dates: true                        # Show publication dates
    enable_markdown: true                   # Allow Markdown formatting
    auto_translate: false                   # Auto-translate missing languages
  
  # Categories
  categories:
    - id: "general"
      name:
        th: "ประกาศทั่วไป"
        de: "Allgemeine Mitteilungen"
        en: "General Announcements"
      color: "#6B7280"
      
    - id: "hours"
      name:
        th: "เวลาทำการ"
        de: "Öffnungszeiten"
        en: "Opening Hours"
      color: "#3B82F6"
      
    - id: "services"
      name:
        th: "บริการ"
        de: "Dienstleistungen"
        en: "Services"
      color: "#10B981"
      
    - id: "emergency"
      name:
        th: "เร่งด่วน"
        de: "Eilmeldungen"
        en: "Emergency"
      color: "#EF4444"
      priority: "high"
  
  # Templates for common announcements
  templates:
    vacation:
      title:
        th: "ประกาศลาพักร้อน"
        de: "Urlaubsankündigung"
        en: "Vacation Notice"
      content:
        th: "เราจะปิดทำการช่วงลาพักร้อนตั้งแต่วันที่ {start_date} ถึง {end_date} กลับมาทำการตามปกติวันที่ {return_date}"
        de: "Wir sind im Urlaub vom {start_date} bis {end_date}. Wir kehren am {return_date} zurück."
        en: "We will be closed for vacation from {start_date} to {end_date}. Returning {return_date}."
      category: "general"
      priority: "high"
    
    hours_change:
      title:
        th: "เปลี่ยนแปลงเวลาทำการ"
        de: "Änderung der Öffnungszeiten"
        en: "Opening Hours Change"
      content:
        th: "เวลาทำการใหม่มีผลตั้งแต่วันที่ {effective_date}"
        de: "Neue Öffnungszeiten ab {effective_date}"
        en: "New opening hours effective {effective_date}"
      category: "hours"
      priority: "medium"
```

---

## Database Configuration

### SQLite Configuration

```yaml
database:
  # Basic settings
  type: "sqlite"
  path: "data/portal.db"                    # Database file path
  
  # Connection settings
  timeout: 30                               # Connection timeout (seconds)
  check_same_thread: false                  # Allow multi-threading
  
  # Performance settings
  journal_mode: "WAL"                       # Write-Ahead Logging
  synchronous: "NORMAL"                     # Synchronization level
  temp_store: "MEMORY"                      # Temporary storage location
  cache_size: 10000                         # Cache size (pages)
  
  # Backup settings
  auto_backup: true
  backup_interval: 86400                    # 24 hours in seconds
  backup_count: 30                          # Keep 30 backups
  backup_path: "backups/"
  
  # Maintenance
  auto_vacuum: "INCREMENTAL"                # Automatic space reclamation
  vacuum_interval: 604800                   # Weekly vacuum (seconds)
  analyze_interval: 86400                   # Daily statistics update
```

### PostgreSQL Configuration (Alternative)

```yaml
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  name: "qr_portal"
  user: "portal_user"
  password_env: "DATABASE_PASSWORD"         # From environment variable
  
  # Connection pool
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30
  pool_recycle: 3600
  
  # SSL settings
  sslmode: "require"                        # require|prefer|disable
  sslcert: "client-cert.pem"
  sslkey: "client-key.pem"
  sslrootcert: "server-ca.pem"
```

---

## Feature Flags

### Core Features

```yaml
features:
  # User Interface
  kiosk_mode: true                          # Enable kiosk display modes
  multi_language: true                      # Multi-language support
  dark_mode: false                          # Dark mode theme
  responsive_design: true                   # Mobile-responsive layouts
  
  # Content Features
  qr_generation: true                       # QR code generation
  social_media: true                        # Social media integration
  announcements: true                       # Announcement system
  status_management: true                   # Status management
  hours_management: true                    # Opening hours management
  
  # Advanced Features
  appointment_booking: false                # Online appointment booking
  patient_portal: false                     # Patient information portal
  inventory_management: false               # Lab inventory tracking
  reporting: false                          # Analytics and reporting
  
  # API Features
  public_api: true                          # Public API access
  admin_api: true                           # Administrative API
  webhooks: false                           # Webhook system
  api_keys: false                           # API key authentication
  
  # Integration Features
  email_notifications: false                # Email notifications
  sms_notifications: false                  # SMS notifications
  push_notifications: false                 # Push notifications
  calendar_sync: false                      # Calendar integration
  
  # Security Features
  two_factor_auth: false                    # 2FA for admin
  audit_logging: true                       # Detailed audit logs
  rate_limiting: true                       # API rate limiting
  csrf_protection: true                     # CSRF protection
  
  # Performance Features
  caching: true                             # Response caching
  image_optimization: true                  # Automatic image optimization
  minification: false                       # CSS/JS minification
  cdn_integration: false                    # CDN for static assets
  
  # Monitoring Features
  health_checks: true                       # System health monitoring
  error_tracking: false                     # External error tracking
  analytics: false                          # Usage analytics
  performance_monitoring: false             # Performance metrics
```

### Feature Dependencies

```yaml
feature_dependencies:
  # Appointment booking requires multiple features
  appointment_booking:
    requires: ["email_notifications", "sms_notifications"]
    recommends: ["calendar_sync", "patient_portal"]
  
  # Patient portal needs authentication
  patient_portal:
    requires: ["two_factor_auth", "audit_logging"]
    conflicts: ["single_user_mode"]
  
  # Advanced reporting needs data collection
  reporting:
    requires: ["analytics", "audit_logging"]
    recommends: ["performance_monitoring"]
  
  # API features
  webhooks:
    requires: ["api_keys", "audit_logging"]
    recommends: ["rate_limiting"]
```

---

## Localization Settings

### Language Configuration

```yaml
localization:
  # Supported languages
  languages:
    th:
      name: "ไทย"
      english_name: "Thai"
      locale: "th_TH"
      direction: "ltr"                      # Text direction: ltr|rtl
      flag_emoji: "🇹🇭"
      flag_code: "th"
      primary: true                         # Primary language for this installation
      
    de:
      name: "Deutsch"
      english_name: "German"
      locale: "de_DE"
      direction: "ltr"
      flag_emoji: "🇩🇪"
      flag_code: "de"
      primary: false
      
    en:
      name: "English"
      english_name: "English"
      locale: "en_US"
      direction: "ltr"
      flag_emoji: "🇺🇸"
      flag_code: "en"
      primary: false
  
  # Translation settings
  translation:
    fallback_language: "en"                 # Fallback when translation missing
    auto_detect_browser: true               # Detect browser language preference
    remember_choice: true                   # Remember user's language choice
    cookie_name: "user_language"            # Cookie name for language preference
    cookie_duration: 365                    # Cookie duration in days
    
    # Translation sources
    sources:
      - type: "json"                        # JSON translation files
        path: "app/translations/"
      - type: "database"                    # Database translations (admin-editable)
        table: "translations"
      - type: "external"                    # External translation service (future)
        provider: "google_translate"
    
    # Missing translation handling
    missing_key_action: "show_key"          # show_key|fallback|empty
    log_missing_keys: true                  # Log missing translation keys
    
  # Regional settings
  regional:
    timezone: "Asia/Bangkok"                # Default timezone
    currency: "THB"                         # Default currency
    number_format: "thai"                   # Number formatting style
    date_format:
      th: "วันที่ d เดือน F Y"              # Thai date format
      de: "d.m.Y"                          # German date format
      en: "F d, Y"                         # English date format
    time_format:
      th: "เวลา H:i น."                     # Thai time format
      de: "H:i Uhr"                        # German time format
      en: "h:i A"                          # English time format (12-hour)
    
  # Content localization
  content:
    # Automatic content translation
    auto_translate_missing: false           # Auto-translate missing content
    translation_service: "google"          # google|azure|aws|deepl
    preserve_html: true                     # Preserve HTML in translations
    
    # Content types that support localization
    localizable_fields:
      - "site_name"
      - "site_description"
      - "announcements"
      - "status_messages"
      - "service_descriptions"
      - "contact_notes"
    
    # Image localization
    localized_images: true                  # Support language-specific images
    image_naming: "{basename}_{lang}.{ext}" # Naming pattern for localized images
```

---

## Social Media Configuration

### Platform Settings

```yaml
social_media:
  enabled: true
  
  platforms:
    # LINE (Primary for Thailand)
    line:
      enabled: true
      type: "messaging"
      priority: 1                           # Display order
      
      # Account information
      official_account: "@laborpattaya"
      display_name: "Labor Pattaya Official"
      url: "https://line.me/R/ti/p/@laborpattaya"
      
      # Features
      qr_enabled: true
      share_enabled: true
      contact_method: true                  # Use as contact method
      
      # Display settings
      icon: "fab fa-line"
      color: "#00C300"
      button_text:
        th: "เพิ่มเพื่อน LINE"
        de: "LINE hinzufügen"
        en: "Add on LINE"
      
      # QR code settings
      qr_style: "square"                    # square|rounded|circle
      qr_size: "medium"                     # small|medium|large
      qr_logo: true                         # Include LINE logo in QR
      
    # Facebook
    facebook:
      enabled: true
      type: "social_network"
      priority: 2
      
      page_url: "https://facebook.com/laborpattaya"
      page_id: "laborpattaya"
      page_name: "Labor Pattaya"
      
      qr_enabled: true
      share_enabled: true
      contact_method: false
      
      icon: "fab fa-facebook-f"
      color: "#1877F2"
      button_text:
        th: "ติดตาม Facebook"
        de: "Facebook folgen"
        en: "Follow on Facebook"
      
      # Facebook-specific settings
      show_like_button: true
      show_share_button: true
      show_follow_button: true
      
    # WhatsApp Business
    whatsapp:
      enabled: true
      type: "messaging"
      priority: 3
      
      business_number: "+66381234567"
      display_number: "038-123-4567"
      url: "https://wa.me/66381234567"
      
      qr_enabled: true
      share_enabled: false
      contact_method: true
      
      icon: "fab fa-whatsapp"
      color: "#25D366"
      button_text:
        th: "แชท WhatsApp"
        de: "WhatsApp Chat"
        en: "WhatsApp Chat"
      
      # WhatsApp-specific settings
      welcome_message:
        th: "สวัสดีครับ! มีอะไรให้ช่วยเหลือไหมครับ?"
        de: "Hallo! Wie können wir Ihnen helfen?"
        en: "Hello! How can we help you?"
      
      business_hours_message:
        th: "เราจะตอบกลับในเวลาทำการ: จ-ศ 08:30-16:00 น."
        de: "Wir antworten während der Geschäftszeiten: Mo-Fr 08:30-16:00"
        en: "We reply during business hours: Mon-Fri 08:30-16:00"
      
    # Instagram
    instagram:
      enabled: true
      type: "social_network"
      priority: 4
      
      username: "laborpattaya"
      profile_url: "https://instagram.com/laborpattaya"
      
      qr_enabled: true
      share_enabled: true
      contact_method: false
      
      icon: "fab fa-instagram"
      color: "#E4405F"
      button_text:
        th: "ติดตาม Instagram"
        de: "Instagram folgen"
        en: "Follow on Instagram"
      
    # TikTok (Popular in Thailand)
    tiktok:
      enabled: true
      type: "social_network"
      priority: 5
      
      username: "@laborpattaya"
      profile_url: "https://tiktok.com/@laborpattaya"
      
      qr_enabled: true
      share_enabled: true
      contact_method: false
      
      icon: "fab fa-tiktok"
      color: "#000000"
      button_text:
        th: "ติดตาม TikTok"
        de: "TikTok folgen"
        en: "Follow on TikTok"
      
    # YouTube
    youtube:
      enabled: false                        # Disabled by default
      type: "video"
      priority: 6
      
      channel_id: "UCxxxxxxxxxxxxxx"
      channel_url: "https://youtube.com/@laborpattaya"
      channel_name: "Labor Pattaya"
      
      qr_enabled: false
      share_enabled: true
      contact_method: false
      
      icon: "fab fa-youtube"
      color: "#FF0000"
      button_text:
        th: "ติดตาม YouTube"
        de: "YouTube abonnieren"
        en: "Subscribe on YouTube"
      
    # Google Business Profile
    google_business:
      enabled: true
      type: "business_listing"
      priority: 7
      
      place_id: "ChIJxxxxxxxxxxxxx"
      business_url: "https://g.page/laborpattaya"
      business_name: "Labor Pattaya"
      
      qr_enabled: true
      share_enabled: false
      contact_method: false
      
      icon: "fab fa-google"
      color: "#4285F4"
      button_text:
        th: "รีวิว Google"
        de: "Google Bewertung"
        en: "Review on Google"
      
      # Google-specific settings
      show_reviews: true
      show_rating: true
      show_photos: false
  
  # Display settings
  display:
    show_follow_section: true               # Show "Follow Us" section
    show_share_buttons: true                # Show share buttons
    show_contact_methods: true              # Show social contact methods
    
    # Layout options
    layout: "grid"                          # grid|list|horizontal
    max_visible: 6                          # Maximum platforms to show
    show_all_toggle: true                   # "Show all" toggle for overflow
    
    # QR code display
    qr_section: true                        # Dedicated QR code section
    qr_size: "medium"                       # Default QR size
    qr_grid_columns: 3                      # QR codes per row
    qr_download_enabled: true               # Allow QR download
    
    # Button styling
    button_style: "thai"                    # thai|modern|minimal|custom
    button_size: "medium"                   # small|medium|large
    show_icons: true                        # Show platform icons
    show_text: true                         # Show button text
    
    # Colors and theming
    follow_brand_colors: true               # Use platform brand colors
    custom_color_scheme: null               # Custom color override
    hover_effects: true                     # Interactive hover effects
    
  # Integration settings
  integration:
    # Automatic posting (future feature)
    auto_post_announcements: false          # Post announcements to social media
    auto_post_platforms: ["facebook", "line"] # Platforms for auto-posting
    
    # Social login (future feature)
    social_login_enabled: false             # Enable social media login
    social_login_platforms: ["facebook", "google"]
    
    # Analytics integration
    track_social_clicks: true               # Track social media clicks
    utm_parameters: true                    # Add UTM parameters to links
    
  # Content settings
  content:
    # Hashtags for posts
    default_hashtags:
      th: ["#ห้องปฏิบัติการ", "#พัทยา", "#เจาะเลือด", "#ตรวจสุขภาพ"]
      de: ["#Labor", "#Pattaya", "#Bluttest", "#Gesundheit"]
      en: ["#Laboratory", "#Pattaya", "#BloodTest", "#Health"]
    
    # Content templates
    announcement_template:
      th: "📢 ประกาศจาก Lab Pattaya\n\n{content}\n\n📞 โทร: {phone}\n🌐 {website}\n\n{hashtags}"
      de: "📢 Ankündigung von Lab Pattaya\n\n{content}\n\n📞 Tel: {phone}\n🌐 {website}\n\n{hashtags}"
      en: "📢 Announcement from Lab Pattaya\n\n{content}\n\n📞 Phone: {phone}\n🌐 {website}\n\n{hashtags}"
    
    status_update_template:
      th: "🏥 สถานะปัจจุบัน: {status}\n\n{message}\n\nอัพเดทล่าสุด: {timestamp}"
      de: "🏥 Aktueller Status: {status}\n\n{message}\n\nLetzte Aktualisierung: {timestamp}"
      en: "🏥 Current Status: {status}\n\n{message}\n\nLast Updated: {timestamp}"
```

---

## Appointment System Configuration

*Note: This section applies when `FEATURE_BOOKING=true`*

### Service Configuration

```yaml
appointments:
  enabled: false                            # Feature flag control
  
  # Business rules
  business_rules:
    # Booking windows
    max_advance_days: 30                    # Maximum days in advance to book
    min_advance_hours: 24                   # Minimum hours in advance
    same_day_booking: false                 # Allow same-day appointments
    
    # Patient limits
    max_bookings_per_patient_monthly: 10    # Monthly booking limit per patient
    max_bookings_per_patient_daily: 2       # Daily booking limit per patient
    max_consecutive_bookings: 1             # Consecutive time slots per booking
    
    # Capacity management
    overbooking_percentage: 10              # Allow 10% overbooking
    last_minute_slots: 2                    # Reserve slots for emergencies
    
    # Confirmation and timing
    auto_confirm_after_minutes: 30          # Auto-confirm bookings after 30 min
    booking_timeout_minutes: 15             # Booking session timeout
    
    # No-show handling
    no_show_penalty_days: 7                 # Booking restriction after no-show
    max_no_shows_monthly: 2                 # Maximum no-shows before restriction
    
    # Cancellation policy
    min_cancellation_hours: 24              # Minimum cancellation notice
    cancellation_fee_percentage: 0          # Cancellation fee (0 = free)
    
  # Default services
  services:
    BLOOD_TEST:
      name:
        th: "เจาะเลือด"
        de: "Blutabnahme"
        en: "Blood Test"
      description:
        th: "การเจาะเลือดเพื่อตรวจวิเคราะห์ทางการแพทย์"
        de: "Blutentnahme zur Laboruntersuchung"
        en: "Blood sampling for laboratory analysis"
      duration_minutes: 30
      buffer_minutes: 10                    # Cleanup/preparation time
      max_bookings_per_slot: 2              # How many patients per time slot
      
      # Requirements
      requires_fasting: true
      preparation_instructions:
        th: "งดอาหาร 8-12 ชั่วโมงก่อนตรวจ, ดื่มน้ำได้"
        de: "8-12 Stunden vor der Untersuchung nüchtern, Wasser trinken erlaubt"
        en: "Fasting 8-12 hours before examination, water allowed"
      
      # Pricing
      price_thb: 500
      price_display:
        th: "500 บาท"
        de: "500 Baht"
        en: "500 THB"
      deposit_required: false
      deposit_percentage: 0
      
      # Availability
      available_days: [1, 2, 3, 4, 5]       # Monday-Friday (1=Monday)
      available_times:
        start: "08:30"
        end: "15:30"                        # Last slot at 15:30 for 30min service
      blackout_dates: []                    # Dates when service unavailable
      
      # Special requirements
      age_restrictions:
        min_age: 0
        max_age: null
        parental_consent_under: 18
      
      health_conditions:
        pregnancy_safe: true
        requires_medical_clearance: false
        contraindications: []
      
    CONSULTATION:
      name:
        th: "ปรึกษาแพทย์"
        de: "Ärztliche Beratung"
        en: "Medical Consultation"
      description:
        th: "การปรึกษาและให้คำแนะนำทางการแพทย์"
        de: "Medizinische Beratung und Aufklärung"
        en: "Medical consultation and advice"
      duration_minutes: 45
      buffer_minutes: 15
      max_bookings_per_slot: 1              # One-on-one consultations
      
      requires_fasting: false
      preparation_instructions:
        th: "เตรียมคำถามและเอกสารทางการแพทย์ที่เกี่ยวข้อง"
        de: "Bereiten Sie Fragen und relevante medizinische Unterlagen vor"
        en: "Prepare questions and relevant medical documents"
      
      price_thb: 800
      price_display:
        th: "800 บาท"
        de: "800 Baht"
        en: "800 THB"
      deposit_required: true
      deposit_percentage: 50                # 50% deposit required
      
      available_days: [1, 2, 3, 4, 5]
      available_times:
        start: "09:00"
        end: "15:00"                        # Last consultation at 15:00
      
      age_restrictions:
        min_age: 18                         # Adult consultations only
        max_age: null
        parental_consent_under: null
      
    RESULT_PICKUP:
      name:
        th: "รับผลตรวจ"
        de: "Ergebnisse abholen"
        en: "Result Pickup"
      description:
        th: "รับผลการตรวจวิเคราะห์และคำอธิบาย"
        de: "Abholen der Laborergebnisse mit Erläuterung"
        en: "Pick up laboratory results with explanation"
      duration_minutes: 15
      buffer_minutes: 5
      max_bookings_per_slot: 4              # Quick pickup service
      
      requires_fasting: false
      preparation_instructions:
        th: "นำบัตรประจำตัวและใบนัดหมาย"
        de: "Ausweis und Terminbestätigung mitbringen"
        en: "Bring ID and appointment confirmation"
      
      price_thb: null                       # Free service
      deposit_required: false
      
      available_days: [1, 2, 3, 4, 5]
      available_times:
        start: "08:30"
        end: "16:00"
      
  # Slot templates
  slot_templates:
    morning_standard:
      name: "Morgentermine Standard"
      day_of_week: null                     # Apply to all days
      start_time: "08:30"
      end_time: "12:00"
      slot_duration_minutes: 30
      max_bookings_per_slot: 2
      service_types: ["BLOOD_TEST", "CONSULTATION"]
      
    afternoon_standard:
      name: "Nachmittagstermine Standard"
      day_of_week: null
      start_time: "13:00"
      end_time: "16:00"
      slot_duration_minutes: 30
      max_bookings_per_slot: 1              # Fewer afternoon slots
      service_types: ["BLOOD_TEST", "CONSULTATION"]
      
    pickup_continuous:
      name: "Durchgehende Abholzeiten"
      day_of_week: null
      start_time: "08:30"
      end_time: "16:00"
      slot_duration_minutes: 15
      max_bookings_per_slot: 4
      service_types: ["RESULT_PICKUP"]
      
    friday_short:
      name: "Freitag verkürzt"
      day_of_week: 5                        # Friday only
      start_time: "08:30"
      end_time: "13:00"                     # Shorter Friday
      slot_duration_minutes: 30
      max_bookings_per_slot: 2
      service_types: ["BLOOD_TEST", "CONSULTATION"]
  
  # Patient information requirements
  patient_info:
    required_fields:
      - "full_name"
      - "phone"
      - "date_of_birth"
      - "gender"
    optional_fields:
      - "email"
      - "address"
      - "emergency_contact"
      - "medical_history"
      - "current_medications"
      - "allergies"
    
    # Validation rules
    validation:
      phone_format: "thai"                  # Thai phone number format
      email_required: false
      age_verification: true                # Verify age matches DOB
      
    # Privacy settings
    data_retention_days: 730               # Keep patient data for 2 years
    anonymize_after_days: 365              # Anonymize after 1 year
    
  # Notification system
  notifications:
    channels:
      line: true                            # LINE notifications (primary)
      sms: true                             # SMS notifications (backup)
      email: false                          # Email not commonly used in Thailand
      push: false                           # Push notifications (future)
      
    # Message templates
    templates:
      booking_confirmation:
        th: |
          ✅ ยืนยันการนัดหมาย #{reference}
          
          📋 บริการ: {service_name}
          📅 วันที่: {appointment_date}
          ⏰ เวลา: {appointment_time}
          
          {preparation_instructions}
          
          📞 ติดต่อ: {clinic_phone}
          🏥 {clinic_name}
        de: |
          ✅ Terminbestätigung #{reference}
          
          📋 Service: {service_name}
          📅 Datum: {appointment_date}
          ⏰ Zeit: {appointment_time}
          
          {preparation_instructions}
          
          📞 Kontakt: {clinic_phone}
          🏥 {clinic_name}
        en: |
          ✅ Appointment Confirmation #{reference}
          
          📋 Service: {service_name}
          📅 Date: {appointment_date}
          ⏰ Time: {appointment_time}
          
          {preparation_instructions}
          
          📞 Contact: {clinic_phone}
          🏥 {clinic_name}
      
      reminder_24h:
        th: |
          ⏰ เตือนนัดหมาย
          
          พรุ่งนี้คุณมีนัดหมาย {service_name}
          เวลา {appointment_time}
          
          {preparation_reminder}
          
          ยกเลิก/เปลี่ยนแปลง: {clinic_phone}
        de: |
          ⏰ Terminerinnerung
          
          Morgen haben Sie einen Termin: {service_name}
          Zeit: {appointment_time}
          
          {preparation_reminder}
          
          Änderungen: {clinic_phone}
        en: |
          ⏰ Appointment Reminder
          
          Tomorrow you have: {service_name}
          Time: {appointment_time}
          
          {preparation_reminder}
          
          Changes: {clinic_phone}
      
      reminder_2h:
        th: "🔔 อีก 2 ชั่วโมงจะถึงเวลานัดหมาย {service_name} ของคุณ กรุณามาถึงก่อนเวลา 15 นาที"
        de: "🔔 In 2 Stunden ist Ihr Termin: {service_name}. Bitte kommen Sie 15 Minuten früher."
        en: "🔔 Your {service_name} appointment is in 2 hours. Please arrive 15 minutes early."
      
      cancellation:
        th: "❌ การนัดหมาย #{reference} ถูกยกเลิกแล้ว สามารถนัดใหม่ได้ที่ {clinic_phone}"
        de: "❌ Termin #{reference} wurde storniert. Neuer Termin: {clinic_phone}"
        en: "❌ Appointment #{reference} has been cancelled. Rebook: {clinic_phone}"
    
    # Timing settings
    timing:
      confirmation_immediate: true          # Send confirmation immediately
      reminder_hours_before: [24, 2]       # Send reminders 24h and 2h before
      no_show_follow_up_hours: 2           # Follow up 2 hours after missed appointment
      
    # Delivery settings
    delivery:
      max_retries: 3                        # Retry failed notifications
      retry_delay_minutes: 5                # Wait 5 min between retries
      fallback_to_sms: true                 # Use SMS if LINE fails
      
  # Payment integration (future feature)
  payments:
    enabled: false
    providers: ["promptpay", "truemoney", "credit_card"]
    deposit_handling: "hold"               # hold|charge|none
    refund_policy: "automatic"             # automatic|manual|none
    
  # Reporting and analytics
  reporting:
    track_booking_funnel: true              # Track conversion rates
    track_no_shows: true                    # Monitor no-show rates
    track_cancellations: true               # Monitor cancellation patterns
    track_popular_times: true               # Identify busy periods
    
    # Reports generated
    daily_schedule: true                    # Daily appointment schedule
    weekly_summary: true                    # Weekly booking summary
    monthly_analytics: true                 # Monthly performance metrics
    no_show_analysis: true                  # No-show pattern analysis
```

---

## Legal Compliance Settings

### PDPA (Thailand) Configuration

```yaml
legal_compliance:
  # PDPA (Personal Data Protection Act) Thailand
  pdpa:
    enabled: true
    
    # Data controller information
    controller:
      name:
        th: "ห้องปฏิบัติการพัทยา"
        de: "Labor Pattaya"
        en: "Laboratory Pattaya"
      address: "Soi Buakhao, Pattaya, Chonburi 20150, Thailand"
      phone: "+66 38 123 456"
      email: "privacy@pattaya-medical.com"
      
      # Data Protection Officer (DPO)
      dpo_name: "Data Protection Officer"
      dpo_email: "dpo@pattaya-medical.com"
      dpo_phone: "+66 38 123 456"
    
    # Data collection settings
    data_collection:
      # What personal data is collected
      data_types:
        - type: "contact_info"
          fields: ["name", "phone", "email"]
          purpose: "appointment_scheduling"
          legal_basis: "consent"
          retention_period: "2_years"
          
        - type: "health_info"
          fields: ["medical_history", "allergies", "medications"]
          purpose: "medical_care"
          legal_basis: "legitimate_interest"
          retention_period: "5_years"
          
        - type: "technical_info"
          fields: ["ip_address", "browser_type", "visit_time"]
          purpose: "system_functionality"
          legal_basis: "legitimate_interest"
          retention_period: "1_year"
      
      # Consent management
      consent:
        granular_consent: true              # Allow specific consent choices
        consent_expiry_months: 12           # Consent expires after 12 months
        re_consent_reminder: true           # Remind users to renew consent
        
        # Consent categories
        categories:
          - id: "essential"
            name:
              th: "จำเป็นสำหรับการให้บริการ"
              de: "Wesentlich für den Service"
              en: "Essential for service"
            required: true
            description:
              th: "ข้อมูลที่จำเป็นสำหรับการให้บริการทางการแพทย์"
              de: "Für die medizinische Dienstleistung erforderliche Daten"
              en: "Data necessary for medical service provision"
            
          - id: "communication"
            name:
              th: "การสื่อสารและแจ้งเตือน"
              de: "Kommunikation und Benachrichtigungen"
              en: "Communication and notifications"
            required: false
            description:
              th: "การส่งข้อความแจ้งเตือนนัดหมายและข้อมูลสำคัญ"
              de: "Terminbenachrichtigungen und wichtige Informationen"
              en: "Appointment reminders and important notifications"
            
          - id: "analytics"
            name:
              th: "การวิเคราะห์การใช้งาน"
              de: "Nutzungsanalyse"
              en: "Usage analytics"
            required: false
            description:
              th: "การวิเคราะห์เพื่อปรับปรุงคุณภาพการให้บริการ"
              de: "Analyse zur Verbesserung der Servicequalität"
              en: "Analysis to improve service quality"
    
    # Data subject rights
    data_subject_rights:
      # Available rights
      rights:
        - "access"                          # Right to access personal data
        - "rectification"                   # Right to correct data
        - "erasure"                         # Right to delete data
        - "restrict_processing"             # Right to restrict processing
        - "data_portability"                # Right to data portability
        - "object"                          # Right to object to processing
        
      # Request handling
      request_handling:
        response_time_days: 30              # PDPA requires 30 days response
        verification_required: true         # Verify identity before processing
        fee_for_excessive_requests: true    # Charge fee for excessive requests
        
        # Request forms
        access_form_url: "/legal/data-access-request"
        deletion_form_url: "/legal/data-deletion-request"
        contact_email: "privacy@pattaya-medical.com"
    
    # Privacy policy
    privacy_policy:
      version: "1.0"
      last_updated: "2025-08-23"
      languages: ["th", "de", "en"]
      
      # Policy sections
      sections:
        - id: "data_collection"
          title:
            th: "การเก็บรวบรวมข้อมูลส่วนบุคคล"
            de: "Erhebung personenbezogener Daten"
            en: "Personal Data Collection"
        - id: "data_usage"
          title:
            th: "การใช้ข้อมูลส่วนบุคคล"
            de: "Verwendung personenbezogener Daten"
            en: "Personal Data Usage"
        - id: "data_sharing"
          title:
            th: "การเปิดเผยข้อมูลส่วนบุคคล"
            de: "Weitergabe personenbezogener Daten"
            en: "Personal Data Sharing"
        - id: "data_security"
          title:
            th: "ความปลอดภัยของข้อมูล"
            de: "Datensicherheit"
            en: "Data Security"
        - id: "your_rights"
          title:
            th: "สิทธิของคุณ"
            de: "Ihre Rechte"
            en: "Your Rights"
      
      # Auto-generation settings
      auto_generate: true                   # Generate policy from configuration
      include_contact_info: true            # Include contact information
      include_dpo_info: true                # Include DPO information
      include_complaint_procedure: true     # Include complaint procedure
  
  # GDPR (European Union) compliance
  gdpr:
    enabled: false                          # Enable if serving EU customers
    
    # Additional GDPR requirements
    lawful_basis_documentation: true        # Document legal basis for processing
    privacy_by_design: true                 # Implement privacy by design
    data_protection_impact_assessment: false # DPIA for high-risk processing
    
    # Additional rights under GDPR
    additional_rights:
      - "automated_decision_making"         # Right not to be subject to automated decisions
      - "profiling"                        # Right not to be subject to profiling
      
    # Breach notification
    breach_notification:
      enabled: true
      notification_hours: 72               # Notify authorities within 72 hours
      affected_individuals_notification: true # Notify affected individuals
  
  # Cookie policy
  cookies:
    enabled: true
    
    # Cookie categories
    categories:
      - id: "essential"
        name:
          th: "คุกกี้ที่จำเป็น"
          de: "Notwendige Cookies"
          en: "Essential Cookies"
        required: true
        description:
          th: "คุกกี้ที่จำเป็นสำหรับการทำงานของเว็บไซต์"
          de: "Cookies, die für die Funktionalität der Website erforderlich sind"
          en: "Cookies necessary for website functionality"
        cookies:
          - name: "session"
            purpose: "User session management"
            expiry: "Session"
          - name: "language"
            purpose: "Language preference"
            expiry: "1 year"
            
      - id: "analytics"
        name:
          th: "คุกกี้สำหรับการวิเคราะห์"
          de: "Analyse-Cookies"
          en: "Analytics Cookies"
        required: false
        description:
          th: "คุกกี้เพื่อวิเคราะห์การใช้งานเว็บไซต์"
          de: "Cookies zur Analyse der Website-Nutzung"
          en: "Cookies for analyzing website usage"
        cookies:
          - name: "_ga"
            purpose: "Google Analytics"
            expiry: "2 years"
          - name: "_gid"
            purpose: "Google Analytics"
            expiry: "24 hours"
    
    # Consent banner
    consent_banner:
      enabled: true
      position: "bottom"                    # bottom|top|center
      blocking: false                       # Block site until consent given
      
      # Banner text
      message:
        th: "เราใช้คุกกี้เพื่อปรับปรุงประสบการณ์การใช้งานของคุณ"
        de: "Wir verwenden Cookies, um Ihre Benutzererfahrung zu verbessern"
        en: "We use cookies to improve your user experience"
      
      # Buttons
      accept_all_text:
        th: "ยอมรับทั้งหมด"
        de: "Alle akzeptieren"
        en: "Accept All"
      
      customize_text:
        th: "ตั้งค่าคุกกี้"
        de: "Cookie-Einstellungen"
        en: "Cookie Settings"
      
      reject_text:
        th: "ปฏิเสธ"
        de: "Ablehnen"
        en: "Reject"
    
    # Cookie settings page
    settings_page:
      url: "/legal/cookie-settings"
      detailed_descriptions: true
      toggle_by_category: true
      save_preferences: true
  
  # Terms of service
  terms_of_service:
    enabled: true
    version: "1.0"
    last_updated: "2025-08-23"
    languages: ["th", "de", "en"]
    
    # Sections
    sections:
      - "service_description"
      - "user_obligations"
      - "limitation_of_liability"
      - "governing_law"
      - "dispute_resolution"
      - "contact_information"
    
    # Acceptance tracking
    track_acceptance: true
    require_acceptance: false               # Don't require acceptance for basic portal use
    acceptance_checkbox_text:
      th: "ฉันได้อ่านและยอมรับข้อกำหนดการให้บริการ"
      de: "Ich habe die Nutzungsbedingungen gelesen und akzeptiert"
      en: "I have read and accept the terms of service"
  
  # Compliance monitoring
  monitoring:
    # Audit logging
    audit_log: true
    log_data_access: true                   # Log all personal data access
    log_data_modifications: true            # Log all data changes
    log_consent_changes: true               # Log consent modifications
    
    # Regular reviews
    privacy_policy_review_months: 12        # Review policy annually
    consent_audit_months: 6                 # Audit consent every 6 months
    data_retention_review_months: 6         # Review retained data every 6 months
    
    # Compliance checks
    automated_compliance_checks: true       # Run automated compliance checks
    compliance_dashboard: true              # Show compliance dashboard to admins
    compliance_notifications: true          # Notify of compliance issues
    
  # Data retention and deletion
  data_retention:
    # Automatic deletion policies
    auto_deletion: true
    
    # Retention periods by data type
    retention_periods:
      appointment_data: "2_years"
      contact_information: "2_years" 
      medical_history: "5_years"           # Legal requirement for medical data
      system_logs: "1_year"
      analytics_data: "6_months"
      
    # Deletion procedures
    deletion:
      soft_delete: true                     # Mark as deleted but don't remove immediately
      hard_delete_after_days: 90           # Permanently delete after 90 days
      backup_exclusion: true                # Exclude deleted data from backups
      
    # Data archiving
    archiving:
      enabled: true
      archive_after_years: 2                # Archive old data after 2 years
      archive_location: "secure_storage"    # Secure archive location
```

---

## Performance & Caching

### Caching Configuration

```yaml
performance:
  # Caching strategy
  caching:
    enabled: true
    default_timeout: 300                    # 5 minutes default cache
    
    # Cache backends
    backends:
      default: "simple"                     # simple|redis|memcached
      session: "filesystem"                # Where to store sessions
      
    # Redis configuration (if using Redis)
    redis:
      host: "localhost"
      port: 6379
      db: 0
      password: null
      ssl: false
      connection_pool_size: 50
      
    # Cache keys and timeouts
    cache_keys:
      status_info: 60                       # Cache status for 1 minute
      opening_hours: 3600                   # Cache hours for 1 hour
      announcements: 300                    # Cache announcements for 5 minutes
      contact_info: 86400                   # Cache contact info for 24 hours
      qr_codes: 3600                        # Cache QR codes for 1 hour
      translations: 86400                   # Cache translations for 24 hours
      
    # Cache invalidation
    auto_invalidate: true                   # Auto-invalidate when data changes
    manual_invalidate_endpoints: true       # Provide manual cache clear endpoints
    
  # Static file optimization
  static_files:
    # Compression
    gzip_enabled: true
    gzip_level: 6                           # Compression level (1-9)
    gzip_min_size: 1000                     # Minimum file size to compress (bytes)
    
    # Browser caching
    cache_control_max_age: 31536000         # 1 year for static assets
    etag_enabled: true                      # Enable ETags
    last_modified_enabled: true             # Enable Last-Modified headers
    
    # Asset optimization
    css_minification: false                 # Minify CSS (requires build step)
    js_minification: false                  # Minify JavaScript
    image_optimization: true                # Optimize uploaded images
    
  # Database optimization
  database:
    # Connection pooling
    pool_size: 10                           # Connection pool size
    max_overflow: 20                        # Additional connections if needed
    pool_timeout: 30                        # Timeout waiting for connection
    pool_recycle: 3600                      # Recycle connections after 1 hour
    
    # Query optimization
    query_timeout: 30                       # Query timeout (seconds)
    slow_query_log: true                    # Log slow queries
    slow_query_threshold: 1.0               # Queries slower than 1 second
    
    # Database maintenance
    auto_vacuum: "incremental"              # SQLite auto-vacuum mode
    vacuum_schedule: "daily"                # When to run vacuum
    analyze_schedule: "weekly"              # When to update statistics
    
  # Response optimization
  response:
    # HTTP response settings
    keep_alive: true                        # Enable HTTP keep-alive
    keep_alive_timeout: 60                  # Keep-alive timeout
    
    # Content compression
    compress_response: true                 # Compress HTTP responses
    compress_min_size: 1000                 # Minimum response size to compress
    
    # Response headers
    security_headers: true                  # Add security headers
    cors_headers: true                      # Add CORS headers if needed
    
  # Monitoring and metrics
  monitoring:
    response_time_tracking: true            # Track response times
    memory_usage_tracking: true             # Track memory usage
    database_performance_tracking: true     # Track database performance
    
    # Performance thresholds
    slow_response_threshold: 2.0            # Responses slower than 2 seconds
    high_memory_threshold: 512              # Memory usage over 512MB
    
    # Alerting
    performance_alerts: true                # Send alerts for performance issues
    alert_email: "admin@pattaya-medical.com"
```

---

## Security Configuration

### Authentication & Authorization

```yaml
security:
  # Authentication settings
  authentication:
    # Session management
    session_timeout: 3600                   # 1 hour session timeout
    session_regenerate: true                # Regenerate session ID on login
    session_cookie_secure: true             # Secure cookies (HTTPS only)
    session_cookie_httponly: true           # HTTP-only cookies
    session_cookie_samesite: "strict"       # SameSite cookie attribute
    
    # Password requirements
    password_policy:
      min_length: 12                        # Minimum password length
      require_uppercase: true               # Require uppercase letters
      require_lowercase: true               # Require lowercase letters
      require_numbers: true                 # Require numbers
      require_special: true                 # Require special characters
      forbidden_passwords:                  # Common passwords to forbid
        - "password"
        - "123456"
        - "admin"
        - "laborpattaya"
      
    # Account lockout
    lockout_policy:
      max_attempts: 5                       # Maximum failed login attempts
      lockout_duration: 900                 # 15 minutes lockout
      progressive_lockout: true             # Increase lockout time with more attempts
      notify_on_lockout: true               # Send notification on account lockout
      
    # Two-factor authentication (future feature)
    two_factor:
      enabled: false
      methods: ["sms", "email", "totp"]
      backup_codes: true
      remember_device_days: 30
  
  # Authorization settings
  authorization:
    # Role-based access control
    rbac_enabled: true
    
    roles:
      super_admin:
        permissions:
          - "system:manage"
          - "users:manage"
          - "content:manage"
          - "settings:manage"
          - "security:manage"
          
      admin:
        permissions:
          - "content:manage"
          - "announcements:manage"
          - "hours:manage"
          - "status:manage"
          
      editor:
        permissions:
          - "content:edit"
          - "announcements:edit"
          - "status:view"
          
    # Permission inheritance
    permission_inheritance: true
    default_role: "admin"                   # Default role for new users
    
  # HTTPS and SSL/TLS
  https:
    force_https: true                       # Redirect HTTP to HTTPS in production
    hsts_enabled: true                      # HTTP Strict Transport Security
    hsts_max_age: 31536000                  # HSTS max age (1 year)
    hsts_include_subdomains: true           # Apply HSTS to subdomains
    
    # SSL/TLS settings
    tls_min_version: "1.2"                  # Minimum TLS version
    cipher_suites: "secure"                 # secure|modern|compatible
    
  # Security headers
  headers:
    # Content Security Policy
    csp_enabled: true
    csp_policy: |
      default-src 'self';
      script-src 'self' 'unsafe-inline' cdn.tailwindcss.com unpkg.com;
      style-src 'self' 'unsafe-inline' fonts.googleapis.com cdn.tailwindcss.com;
      font-src 'self' fonts.gstatic.com;
      img-src 'self' data: https:;
      connect-src 'self';
    
    # Other security headers
    x_frame_options: "DENY"                 # Prevent clickjacking
    x_content_type_options: "nosniff"       # Prevent MIME sniffing
    x_xss_protection: "1; mode=block"       # XSS protection
    referrer_policy: "strict-origin-when-cross-origin"
    
  # Rate limiting
  rate_limiting:
    enabled: true
    storage: "memory"                       # memory|redis|database
    
    # Rate limits by endpoint type
    limits:
      public_api:
        requests: 100
        window: 60                          # 100 requests per minute
        per: "ip"                           # Per IP address
        
      admin_api:
        requests: 300
        window: 60                          # 300 requests per minute
        per: "session"                      # Per authenticated session
        
      login_attempts:
        requests: 5
        window: 300                         # 5 attempts per 5 minutes
        per: "ip"
        
      qr_generation:
        requests: 50
        window: 60                          # 50 QR codes per minute
        per: "ip"
    
    # Rate limit responses
    rate_limit_headers: true                # Include rate limit headers in response
    rate_limit_message:
      th: "คำขอเกินขีดจำกัด กรุณาลองใหม่ภายหลัง"
      de: "Anfragenlimit überschritten. Bitte versuchen Sie es später erneut."
      en: "Rate limit exceeded. Please try again later."
      
  # Input validation and sanitization
  input_validation:
    # SQL injection protection
    sql_injection_protection: true
    parameterized_queries: true
    
    # XSS protection
    xss_protection: true
    html_sanitization: true
    allowed_html_tags: ["b", "i", "u", "br", "p", "strong", "em"]
    
    # CSRF protection
    csrf_protection: true
    csrf_token_timeout: 3600                # CSRF token valid for 1 hour
    
    # File upload security
    file_upload_security: true
    allowed_file_types: ["png", "jpg", "jpeg", "gif", "pdf"]
    max_file_size: 5242880                  # 5MB max file size
    virus_scanning: false                   # Virus scanning (requires external service)
    
  # Logging and monitoring
  security_logging:
    # Security event logging
    log_failed_logins: true
    log_successful_logins: true
    log_admin_actions: true
    log_data_access: true
    log_configuration_changes: true
    
    # Log retention
    log_retention_days: 90
    log_compression: true
    log_encryption: false
    
    # Alerting
    security_alerts: true
    alert_on_multiple_failures: true
    alert_threshold: 10                     # Alert after 10 failed logins from same IP
    alert_email: "security@pattaya-medical.com"
    
    # Integration with external systems
    siem_integration: false                 # Security Information Event Management
    syslog_enabled: false                   # Send logs to syslog server
    
  # Data protection
  data_protection:
    # Encryption
    encrypt_sensitive_data: true            # Encrypt sensitive data at rest
    encryption_algorithm: "AES-256"
    key_rotation_days: 90                   # Rotate encryption keys every 90 days
    
    # Data anonymization
    anonymize_logs: true                    # Remove PII from logs
    anonymize_ip_addresses: true            # Anonymize IP addresses
    
    # Backup security
    encrypt_backups: true                   # Encrypt database backups
    secure_backup_storage: true             # Use secure backup storage
    backup_access_control: true             # Control access to backups
    
  # Compliance and auditing
  compliance:
    # Audit requirements
    audit_trail: true                       # Maintain audit trail
    audit_retention_years: 7                # Keep audit logs for 7 years
    
    # Compliance frameworks
    frameworks:
      - "PDPA_Thailand"                     # Thai Personal Data Protection Act
      - "ISO27001"                          # Information Security Management
      - "HIPAA"                             # Health Insurance Portability (if applicable)
    
    # Regular security assessments
    security_assessments:
      penetration_testing_frequency: "annual"
      vulnerability_scanning_frequency: "quarterly"
      security_policy_review_frequency: "annual"
```

---

## Logging Configuration

### Application Logging

```yaml
logging:
  # General logging settings
  level: "INFO"                             # DEBUG|INFO|WARNING|ERROR|CRITICAL
  format: "detailed"                        # simple|detailed|json
  
  # Log destinations
  handlers:
    console:
      enabled: true
      level: "INFO"
      format: "simple"
      
    file:
      enabled: true
      level: "INFO"
      format: "detailed"
      filename: "logs/app.log"
      max_size: 10485760                    # 10MB per file
      backup_count: 5                       # Keep 5 backup files
      
    error_file:
      enabled: true
      level: "ERROR"
      format: "detailed"
      filename: "logs/error.log"
      max_size: 10485760
      backup_count: 10
      
    syslog:
      enabled: false
      level: "WARNING"
      address: ["localhost", 514]
      facility: "LOG_USER"
  
  # Log formats
  formats:
    simple: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    detailed: |
      %(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - 
      %(funcName)s() - %(message)s
    json: |
      {
        "timestamp": "%(asctime)s",
        "logger": "%(name)s", 
        "level": "%(levelname)s",
        "file": "%(pathname)s",
        "line": %(lineno)d,
        "function": "%(funcName)s",
        "message": "%(message)s"
      }
  
  # Logger-specific settings
  loggers:
    app:
      level: "INFO"
      propagate: true
      
    app.database:
      level: "WARNING"                      # Database operations
      propagate: true
      
    app.auth:
      level: "INFO"                         # Authentication events
      propagate: true
      
    app.api:
      level: "INFO"                         # API requests
      propagate: true
      
    sqlalchemy:
      level: "WARNING"                      # SQLAlchemy ORM
      propagate: false
      
    werkzeug:
      level: "WARNING"                      # Flask/Werkzeug
      propagate: false
  
  # What to log
  log_requests: true                        # HTTP requests
  log_responses: false                      # HTTP responses (verbose)
  log_sql_queries: false                    # SQL queries (debug only)
  log_template_rendering: false             # Template rendering (debug only)
  log_cache_operations: false               # Cache hit/miss (debug only)
  
  # Security logging
  security_logging:
    log_login_attempts: true                # All login attempts
    log_admin_actions: true                 # Administrative actions
    log_data_access: true                   # Personal data access
    log_config_changes: true                # Configuration changes
    log_failed_requests: true               # 4xx/5xx responses
    
  # Performance logging
  performance_logging:
    log_slow_requests: true                 # Requests slower than threshold
    slow_request_threshold: 2.0             # 2 seconds threshold
    log_memory_usage: false                 # Memory usage (debug only)
    log_database_queries: false             # Database query performance
    
  # Business event logging
  business_logging:
    log_status_changes: true                # Practice status changes
    log_appointment_bookings: true          # New appointments (if enabled)
    log_announcement_publications: true     # New announcements
    log_qr_generations: false               # QR code generations (verbose)
    
  # Log rotation and archiving
  rotation:
    rotate_when: "midnight"                 # When to rotate logs
    rotate_interval: 1                      # Rotate daily
    compress_old_logs: true                 # Compress rotated logs
    delete_old_logs_after_days: 30          # Delete logs after 30 days
    
  # Log monitoring and alerting
  monitoring:
    monitor_error_rate: true                # Monitor error rates
    error_rate_threshold: 0.05              # Alert if >5% of requests fail
    monitor_log_volume: true                # Monitor log volume
    log_volume_threshold: 1000              # Alert if >1000 log entries/minute
    
    # Alerting
    alert_on_errors: true                   # Send alerts for ERROR level logs
    alert_email: "alerts@pattaya-medical.com"
    alert_aggregation_minutes: 5            # Group alerts in 5-minute windows
    
  # External log services
  external_services:
    # Sentry for error tracking
    sentry:
      enabled: false
      dsn: ""                               # Sentry DSN
      environment: "production"
      sample_rate: 1.0                      # Sample rate for performance
      
    # ELK Stack integration
    elasticsearch:
      enabled: false
      hosts: ["localhost:9200"]
      index_pattern: "qr-portal-logs-%Y.%m.%d"
      
    # Cloud logging services
    cloudwatch:
      enabled: false
      region: "ap-southeast-1"
      log_group: "qr-portal"
      
    splunk:
      enabled: false
      host: "localhost"
      port: 8088
      token: ""
```

---

## Deployment Configurations

### Development Environment

```yaml
development:
  # Flask settings
  flask:
    debug: true
    testing: false
    host: "0.0.0.0"
    port: 5000
    threaded: true
    
  # Database
  database:
    url: "sqlite:///data/portal_dev.db"
    echo: true                              # Log SQL queries
    
  # Security (relaxed for development)
  security:
    force_https: false
    csrf_protection: false
    rate_limiting: false
    
  # Caching (minimal for development)
  cache:
    type: "simple"
    default_timeout: 60
    
  # Logging (verbose for development)
  logging:
    level: "DEBUG"
    console: true
    file: false
    
  # Features (enable all for testing)
  features:
    booking: true
    social_media: true
    analytics: true
    webhooks: true
    
  # External services (mock or disabled)
  external_services:
    email: "mock"
    sms: "mock"
    analytics: "disabled"
```

### Testing Environment

```yaml
testing:
  # Flask settings
  flask:
    testing: true
    debug: false
    host: "127.0.0.1"
    port: 5001
    
  # Database (in-memory for speed)
  database:
    url: "sqlite:///:memory:"
    echo: false
    
  # Security (disabled for testing)
  security:
    force_https: false
    csrf_protection: false
    rate_limiting: false
    session_timeout: 86400                  # Long timeout for testing
    
  # Caching (disabled for consistent testing)
  cache:
    type: "null"
    
  # Logging (minimal for testing)
  logging:
    level: "WARNING"
    console: false
    file: false
    
  # Test data
  test_data:
    load_fixtures: true                     # Load test data
    create_test_users: true                 # Create test admin users
    mock_external_services: true            # Mock external APIs
```

### Production Environment

```yaml
production:
  # Flask settings (optimized for production)
  flask:
    debug: false
    testing: false
    host: "127.0.0.1"                      # Bind to localhost (behind reverse proxy)
    port: 5000
    threaded: false                         # Use process-based workers instead
    
  # WSGI server configuration
  wsgi:
    server: "gunicorn"                      # gunicorn|uwsgi|waitress
    workers: 2                              # Number of worker processes
    worker_class: "sync"                    # Worker class
    max_requests: 1000                      # Requests before worker restart
    timeout: 30                             # Request timeout
    
  # Database (optimized for production)
  database:
    url: "sqlite:///data/portal.db"
    pool_size: 10
    max_overflow: 20
    pool_timeout: 30
    echo: false                             # Don't log SQL queries
    
  # Security (strict for production)
  security:
    force_https: true
    hsts_enabled: true
    csrf_protection: true
    rate_limiting: true
    session_timeout: 3600
    
    # Additional production security
    secure_cookies: true
    session_regenerate: true
    security_headers: true
    
  # Caching (Redis for production)
  cache:
    type: "redis"
    redis_url: "redis://localhost:6379/0"
    default_timeout: 3600
    
  # Performance optimizations
  performance:
    gzip_compression: true
    static_file_caching: true
    template_caching: true
    query_caching: true
    
  # Monitoring and logging
  monitoring:
    health_checks: true
    performance_monitoring: true
    error_tracking: true
    
  logging:
    level: "INFO"
    console: false
    file: true
    syslog: true
    
    # Structured logging for production
    format: "json"
    include_request_id: true
    
  # Backup configuration
  backups:
    enabled: true
    frequency: "daily"
    retention_days: 30
    remote_storage: true
    encryption: true
    
  # External services (production endpoints)
  external_services:
    email:
      provider: "smtp"
      server: "smtp.gmail.com"
      
    sms:
      provider: "twilio"
      
    analytics:
      provider: "google_analytics"
      tracking_id: "GA_TRACKING_ID"
      
    error_tracking:
      provider: "sentry"
      environment: "production"
```

### Docker Configuration

```yaml
docker:
  # Base image
  base_image: "python:3.11-slim"
  
  # Application settings
  app:
    working_directory: "/app"
    user: "app"
    uid: 1000
    gid: 1000
    
  # Environment variables
  environment:
    FLASK_ENV: "production"
    PYTHONPATH: "/app"
    
  # Volume mounts
  volumes:
    - "data:/app/data"                      # Database and uploads
    - "logs:/app/logs"                      # Log files
    - "backups:/app/backups"                # Backup files
    
  # Network configuration
  network:
    internal: false                         # Expose to external networks
    ports:
      - "5000:5000"
      
  # Health check
  health_check:
    test: "curl -f http://localhost:5000/healthz || exit 1"
    interval: "30s"
    timeout: "10s"
    retries: 3
    start_period: "10s"
    
  # Resource limits
  resources:
    cpu_limit: "1.0"
    memory_limit: "512M"
    
  # Restart policy
  restart_policy: "unless-stopped"
```

---

## Validation & Testing

### Configuration Validation

```yaml
validation:
  # Schema validation
  schema_validation: true                   # Validate config.yml against schema
  strict_mode: false                        # Allow unknown configuration keys
  
  # Required fields validation
  required_fields:
    - "site.name"
    - "site.languages"
    - "site.default_language"
    - "contact.phone"
    - "contact.email"
    - "location.address"
    
  # Data type validation
  field_types:
    "site.languages": "array"
    "location.latitude": "float"
    "location.longitude": "float"
    "hours.weekly.monday": "array"
    
  # Value constraints
  constraints:
    "site.languages":
      min_items: 1
      max_items: 5
      allowed_values: ["de", "th", "en", "fr", "es", "zh"]
      
    "location.latitude":
      min: -90.0
      max: 90.0
      
    "location.longitude":
      min: -180.0
      max: 180.0
      
    "contact.phone":
      pattern: "^\\+[1-9]\\d{1,14}$"       # International phone number format
      
  # Cross-field validation
  cross_validation:
    - field: "site.default_language"
      must_be_in: "site.languages"
      
    - field: "hours.exceptions[*].date"
      format: "YYYY-MM-DD"
      
  # Environment-specific validation
  environment_validation:
    production:
      required_env_vars:
        - "SECRET_KEY"
        - "ADMIN_PASSWORD"
        - "SITE_URL"
        
    development:
      required_env_vars:
        - "SECRET_KEY"
```

### Testing Configuration

```yaml
testing:
  # Test configuration validation
  config_tests:
    validate_schema: true                   # Test configuration schema
    validate_required_fields: true         # Test required field presence
    validate_data_types: true              # Test data type correctness
    validate_constraints: true             # Test value constraints
    
  # Integration tests
  integration_tests:
    test_database_connection: true          # Test database connectivity
    test_external_services: false          # Test external service connections
    test_email_sending: false              # Test email functionality
    test_qr_generation: true               # Test QR code generation
    
  # Load testing
  load_testing:
    enabled: false                          # Enable load testing
    concurrent_users: 50                    # Simulate concurrent users
    test_duration: 300                      # Test duration in seconds
    
  # Security testing
  security_testing:
    test_sql_injection: true               # Test for SQL injection vulnerabilities
    test_xss: true                          # Test for XSS vulnerabilities
    test_csrf: true                         # Test CSRF protection
    test_authentication: true              # Test authentication mechanisms
    
  # Performance testing
  performance_testing:
    test_response_times: true              # Test response time performance
    response_time_threshold: 2.0           # Maximum acceptable response time
    test_memory_usage: true                # Test memory usage
    memory_threshold: 512                  # Maximum memory usage in MB
```

---

## Configuration Examples

### Small Practice Setup

```yaml
# config.yml for small medical practice
site:
  name: "Dr. Smith Clinic"
  languages: ["th", "en"]
  default_language: "th"
  timezone: "Asia/Bangkok"

location:
  address: "123 Main Street, Pattaya"
  latitude: 12.923556
  longitude: 100.882507

contact:
  phone: "+66 38 123 456"
  email: "info@drsmith.com"

hours:
  weekly:
    monday: ["09:00-17:00"]
    tuesday: ["09:00-17:00"]
    wednesday: ["09:00-12:00"]
    thursday: ["09:00-17:00"]
    friday: ["09:00-16:00"]
    saturday: []
    sunday: []

services:
  standard:
    - "General Consultation"
    - "Health Check-up"
    - "Vaccination"

social_media:
  enabled: true
  platforms:
    line:
      enabled: true
      official_account: "@drsmith"
    facebook:
      enabled: true
      page_url: "https://facebook.com/drsmith"

features:
  booking: false
  social_media: true
  analytics: false
```

### Large Laboratory Setup

```yaml
# config.yml for large laboratory with multiple locations
site:
  name: "Bangkok Medical Laboratory"
  languages: ["th", "en", "de"]
  default_language: "th"
  timezone: "Asia/Bangkok"
  theme: "medical"

location:
  name: "BML Central Lab"
  address: "456 Hospital Road, Bangkok"
  latitude: 13.756331
  longitude: 100.501765
  
  # Multiple locations
  branches:
    - name: "BML Pattaya"
      address: "789 Beach Road, Pattaya"
      latitude: 12.923556
      longitude: 100.882507
      phone: "+66 38 555 0123"
    - name: "BML Phuket"
      address: "321 Tourist Street, Phuket"
      latitude: 7.878978
      longitude: 98.398080
      phone: "+66 76 555 0456"

services:
  categories:
    - id: "blood_tests"
      name:
        th: "การตรวจเลือด"
        en: "Blood Tests"
        de: "Blutuntersuchungen"
      services:
        - "Complete Blood Count"
        - "Lipid Profile"
        - "Liver Function"
        - "Kidney Function"
        
    - id: "specialized_tests"
      name:
        th: "การตรวจพิเศษ"
        en: "Specialized Tests"
        de: "Spezialuntersuchungen"
      services:
        - "Hormone Analysis"
        - "Tumor Markers"
        - "Genetic Testing"

appointments:
  enabled: true
  business_rules:
    max_advance_days: 60
    min_advance_hours: 48
    max_bookings_per_patient_monthly: 20
    
  notifications:
    channels:
      line: true
      sms: true
      email: true

features:
  booking: true
  social_media: true
  analytics: true
  webhooks: true
  api_access: true
```

### International Clinic Setup

```yaml
# config.yml for international clinic serving tourists
site:
  name: "Pattaya International Medical Center"
  languages: ["en", "th", "de", "fr", "ru"]
  default_language: "en"
  timezone: "Asia/Bangkok"
  theme: "international"

location:
  address: "88 International Drive, Pattaya"
  latitude: 12.923556
  longitude: 100.882507
  
  public_transport:
    - type: "airport_shuttle"
      route: "Suvarnabhumi Airport - Pattaya"
      fare_thb: 150
    - type: "hotel_pickup"
      note: "Free pickup from major hotels"

contact:
  phone: "+66 38 123 456"
  emergency_phone: "+66 38 911 911"
  whatsapp: "+66 81 234 5678"
  email: "info@pattayamedical.com"
  
  # Multi-language support staff
  languages_supported:
    - language: "english"
      available: "24/7"
    - language: "thai"
      available: "24/7"  
    - language: "german"
      available: "08:00-20:00"
    - language: "russian"
      available: "10:00-18:00"

services:
  medical_tourism:
    - "Health Check Packages"
    - "Dental Tourism"
    - "Cosmetic Surgery"
    - "Rehabilitation Services"
    
  insurance_accepted:
    - "International Health Insurance"
    - "Travel Insurance"
    - "European Health Cards"
    - "Government Health Schemes"

legal_compliance:
  pdpa:
    enabled: true
  gdpr:
    enabled: true                          # Serving European patients
    
payments:
  accepted_methods:
    - "Cash (THB, USD, EUR)"
    - "Credit Cards"
    - "Insurance Direct Billing"
    - "Bank Transfer"

features:
  booking: true
  multi_language: true
  patient_portal: true
  telemedicine: true
  medical_records: true
```

---

## Migration & Updates

### Configuration Migration

```yaml
migration:
  # Version tracking
  version_tracking: true
  current_version: "1.0.0"
  migration_history: true
  
  # Migration procedures
  procedures:
    # Backup before migration
    backup_before_migration: true
    backup_location: "backups/pre-migration/"
    
    # Validation during migration
    validate_after_migration: true
    rollback_on_failure: true
    
    # Migration steps
    steps:
      - name: "backup_current_config"
        action: "backup"
        target: ["config.yml", ".env", "data/portal.db"]
        
      - name: "validate_new_config"
        action: "validate"
        schema: "config_schema_v1.1.json"
        
      - name: "update_database_schema"
        action: "database_migration"
        script: "migrations/v1.0_to_v1.1.sql"
        
      - name: "update_config_format"
        action: "config_transform"
        transformer: "migrations/config_v1.0_to_v1.1.py"
        
      - name: "verify_functionality"
        action: "test"
        tests: ["health_check", "basic_functionality"]
  
  # Rollback procedures
  rollback:
    enabled: true
    automatic_rollback: true
    rollback_triggers:
      - "validation_failure"
      - "database_error"
      - "application_crash"
      
    rollback_steps:
      - name: "stop_application"
        action: "service_stop"
        
      - name: "restore_config"
        action: "restore"
        source: "backups/pre-migration/"
        
      - name: "restore_database"
        action: "database_restore"
        source: "backups/pre-migration/portal.db"
        
      - name: "restart_application"
        action: "service_start"
        
      - name: "verify_rollback"
        action: "health_check"
  
  # Configuration versioning
  versioning:
    track_changes: true
    change_log: "config/CHANGELOG.md"
    
    # Version compatibility
    backward_compatibility:
      supported_versions: ["0.9.x", "1.0.x"]
      deprecation_warnings: true
      migration_assistance: true
      
    forward_compatibility:
      unknown_fields: "ignore"              # ignore|warn|error
      future_features: "disable"            # disable|warn|enable
  
  # Migration validation
  validation:
    pre_migration:
      - "config_syntax"
      - "required_fields"
      - "data_integrity"
      
    post_migration:
      - "application_startup"
      - "database_connectivity"
      - "external_services"
      - "functional_tests"
      
    rollback_validation:
      - "data_consistency"
      - "feature_availability"
      - "performance_baseline"
```

### Update Procedures

```yaml
updates:
  # Update channels
  channels:
    stable: "https://releases.qr-portal.com/stable/"
    beta: "https://releases.qr-portal.com/beta/"
    development: "https://releases.qr-portal.com/dev/"
    
  # Update checking
  check_for_updates: true
  check_frequency: "weekly"                 # daily|weekly|monthly|never
  notify_admins: true
  
  # Automatic updates
  automatic_updates:
    enabled: false                          # Manual approval required
    security_updates_only: true             # Only auto-install security fixes
    maintenance_window: "02:00-04:00"       # When to perform updates
    
  # Pre-update requirements
  requirements:
    - name: "disk_space"
      check: "available_space_mb >= 1000"
      
    - name: "memory"
      check: "available_memory_mb >= 512"
      
    - name: "python_version"
      check: "python_version >= 3.11"
      
    - name: "dependencies"
      check: "all_dependencies_satisfied"
      
  # Update process
  process:
    steps:
      - "check_requirements"
      - "create_backup"
      - "download_update"
      - "verify_signature"
      - "stop_services"
      - "install_update"
      - "migrate_config"
      - "update_database"
      - "start_services"
      - "verify_update"
      - "cleanup"
      
    # Rollback on failure
    rollback_on_failure: true
    max_rollback_attempts: 3
    
  # Post-update actions
  post_update:
    - "clear_cache"
    - "rebuild_search_index"
    - "notify_admins"
    - "log_update_completion"
```

---

**📖 Configuration Reference Version:** 1.0.0 | **Last Updated:** 2025-08-23  
**🔧 For technical support:** config-help@pattaya-medical.com  
**📚 Full documentation:** https://docs.qr-info-portal.com