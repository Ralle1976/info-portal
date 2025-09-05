# 🔌 QR Info Portal - API Documentation

**Version:** 1.0.0 | **Last Updated:** 2025-08-23

---

## 📋 Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Base URLs & Endpoints](#base-urls--endpoints)
4. [Public API](#public-api)
5. [Admin API](#admin-api)
6. [QR Code API](#qr-code-api)
7. [Social Media API](#social-media-api)
8. [Legal Compliance API](#legal-compliance-api)
9. [Appointments API](#appointments-api)
10. [Response Formats](#response-formats)
11. [Error Handling](#error-handling)
12. [Rate Limiting](#rate-limiting)
13. [SDKs & Code Examples](#sdks--code-examples)
14. [Webhooks](#webhooks)
15. [Testing & Development](#testing--development)

---

## API Overview

The QR Info Portal provides both public and administrative APIs for integrating with medical practice management systems, mobile applications, and third-party services.

### Key Features

- **RESTful Design** - Standard HTTP methods and status codes
- **JSON Responses** - All data in JSON format with UTF-8 encoding
- **Multi-language Support** - Content in German, Thai, and English
- **Real-time Updates** - Live status and schedule information
- **Authentication** - Secure admin access with session management
- **Rate Limiting** - Fair usage policies to prevent abuse
- **CORS Support** - Cross-origin requests for web applications

### API Principles

- **Stateless** - Each request contains all necessary information
- **Idempotent** - Safe to retry GET, PUT, DELETE requests
- **Consistent** - Uniform response formats across all endpoints
- **Secure** - HTTPS in production, authentication for sensitive operations
- **Documented** - Complete documentation with examples

---

## Authentication

### Public API

Most public endpoints require **no authentication**:

```bash
curl -H "Accept: application/json" https://your-domain.com/api/status
```

### Admin API

Admin endpoints require **session-based authentication**:

```bash
# 1. Login to establish session
curl -X POST https://your-domain.com/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}' \
  -c cookies.txt

# 2. Use session for subsequent requests
curl -H "Accept: application/json" \
  -b cookies.txt \
  https://your-domain.com/api/admin/status
```

### API Keys (Future Enhancement)

For programmatic access without sessions:

```bash
curl -H "Authorization: Bearer your-api-key" \
  https://your-domain.com/api/admin/status
```

---

## Base URLs & Endpoints

### Production
```
Base URL: https://your-domain.com
API Base: https://your-domain.com/api
Admin API: https://your-domain.com/api/admin
```

### Development
```
Base URL: http://localhost:5000
API Base: http://localhost:5000/api
Admin API: http://localhost:5000/api/admin
```

### Versioning

Currently v1 (implicit). Future versions will use URL versioning:
```
https://your-domain.com/api/v2/status
```

---

## Public API

### Status Information

#### Get Current Status
```http
GET /api/status
```

**Response:**
```json
{
  "status": "ANWESEND",
  "status_display": {
    "de": "Geöffnet - Normal verfügbar",
    "th": "เปิดทำการ - บริการปกติ", 
    "en": "Open - Normal operation"
  },
  "is_open": true,
  "current_time": "2025-08-23T14:30:00+07:00",
  "timezone": "Asia/Bangkok",
  "valid_from": null,
  "valid_until": null,
  "note": {
    "de": null,
    "th": null,
    "en": null
  },
  "next_change": null,
  "emergency_contact": "+66 38 123 456"
}
```

**Status Types:**
- `ANWESEND` - Open/Present
- `GESCHLOSSEN` - Closed
- `URLAUB` - Vacation
- `BILDUNGSURLAUB` - Educational leave
- `KONGRESS` - Conference
- `SONSTIGES` - Other

#### Get Status History
```http
GET /api/status/history?limit=10&offset=0
```

**Response:**
```json
{
  "status_history": [
    {
      "id": 123,
      "status": "URLAUB",
      "valid_from": "2025-08-15T00:00:00+07:00",
      "valid_until": "2025-08-22T23:59:59+07:00",
      "created_at": "2025-08-14T10:00:00+07:00",
      "note": {
        "de": "Sommerurlaub in Deutschland",
        "th": "ลาพักร้อนที่เยอรมนี",
        "en": "Summer vacation in Germany"
      }
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 45,
    "items_per_page": 10
  }
}
```

### Opening Hours

#### Get Current Hours
```http
GET /api/hours
```

**Response:**
```json
{
  "today": {
    "date": "2025-08-23",
    "day_name": {
      "de": "Freitag",
      "th": "วันศุกร์",
      "en": "Friday"
    },
    "is_open": true,
    "hours": ["08:30-13:00"],
    "is_exception": false,
    "note": null
  },
  "week": [
    {
      "date": "2025-08-24",
      "day_name": {"de": "Samstag", "th": "วันเสาร์", "en": "Saturday"},
      "is_open": false,
      "hours": [],
      "is_exception": false
    }
  ],
  "exceptions": [
    {
      "date": "2025-08-26",
      "is_open": false,
      "hours": [],
      "reason": {"de": "Feiertag", "th": "วันหยุด", "en": "Public Holiday"}
    }
  ],
  "timezone": "Asia/Bangkok"
}
```

#### Get Weekly Schedule
```http
GET /api/hours/week?date=2025-08-23
```

#### Get Monthly Schedule
```http
GET /api/hours/month?year=2025&month=8
```

### Announcements

#### Get Active Announcements
```http
GET /api/announcements
```

**Response:**
```json
{
  "announcements": [
    {
      "id": 45,
      "title": {
        "de": "Neue Laboröffnungszeiten",
        "th": "เวลาทำการใหม่ของห้องปฏิบัติการ",
        "en": "New Laboratory Hours"
      },
      "content": {
        "de": "Ab dem 1. September erweiterte Öffnungszeiten...",
        "th": "ตั้งแต่วันที่ 1 กันยายน เวลาทำการใหม่...",
        "en": "Starting September 1st, extended hours..."
      },
      "priority": "medium",
      "valid_from": "2025-08-20T00:00:00+07:00",
      "valid_until": "2025-09-01T23:59:59+07:00",
      "show_on_homepage": true,
      "show_in_kiosk": true,
      "created_at": "2025-08-20T09:00:00+07:00",
      "updated_at": "2025-08-20T09:00:00+07:00"
    }
  ],
  "total_count": 3
}
```

### Contact Information

#### Get Contact Details
```http
GET /api/contact
```

**Response:**
```json
{
  "practice_name": {
    "de": "Labor Pattaya - Blutabnahme",
    "th": "ห้องปฏิบัติการพัทยา - เจาะเลือด",
    "en": "Laboratory Pattaya - Blood Tests"
  },
  "phone": "+66 38 123 456",
  "emergency_phone": "+66 38 123 999",
  "email": "labor@pattaya-medical.com",
  "address": {
    "street": "Soi Buakhao",
    "city": "Pattaya",
    "country": "Thailand",
    "full_address": "Soi Buakhao, Pattaya, Thailand"
  },
  "location": {
    "latitude": 12.923556,
    "longitude": 100.882507,
    "maps_url": "https://maps.google.com/?q=12.923556,100.882507"
  },
  "website": "https://pattaya-medical.com",
  "social_media": {
    "line": "@laborpattaya",
    "facebook": "laborpattaya",
    "instagram": "laborpattaya"
  }
}
```

### Services Information

#### Get Available Services
```http
GET /api/services
```

**Response:**
```json
{
  "services": [
    {
      "id": "BLOOD_TEST",
      "name": {
        "de": "Blutabnahme",
        "th": "เจาะเลือด",
        "en": "Blood Test"
      },
      "description": {
        "de": "Professionelle Blutentnahme für Laboruntersuchungen",
        "th": "การเจาะเลือดเพื่อตรวจวิเคราะห์ทางการแพทย์",
        "en": "Professional blood sampling for laboratory analysis"
      },
      "duration_minutes": 30,
      "requires_fasting": true,
      "preparation_instructions": {
        "de": "8-12 Stunden vor der Untersuchung nüchtern",
        "th": "งดอาหาร 8-12 ชั่วโมงก่อนตรวจ",
        "en": "Fasting 8-12 hours before examination"
      },
      "price_thb": 500,
      "available": true
    }
  ]
}
```

### Availability

#### Get Available Time Slots
```http
GET /api/availability?date=2025-08-24&service=BLOOD_TEST
```

**Response:**
```json
{
  "date": "2025-08-24",
  "available_slots": [
    {
      "time": "08:30",
      "available": true,
      "capacity": 2,
      "booked": 0,
      "service_types": ["BLOOD_TEST", "CONSULTATION"]
    },
    {
      "time": "09:00", 
      "available": true,
      "capacity": 2,
      "booked": 1,
      "service_types": ["BLOOD_TEST", "CONSULTATION"]
    }
  ],
  "note": {
    "de": "Indikative Zeiten - bitte telefonisch bestätigen",
    "th": "เวลาโดยประมาณ - กรุณาโทรยืนยัน",
    "en": "Indicative times - please confirm by phone"
  }
}
```

---

## Admin API

**🔒 All admin endpoints require authentication**

### Status Management

#### Update Current Status
```http
PUT /api/admin/status
```

**Request:**
```json
{
  "status": "URLAUB",
  "valid_from": "2025-08-25T00:00:00+07:00",
  "valid_until": "2025-08-30T23:59:59+07:00",
  "note": {
    "de": "Sommerurlaub - zurück am 31.08.",
    "th": "ลาพักร้อน - กลับวันที่ 31.08.",
    "en": "Summer vacation - back on 31.08."
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Status updated successfully",
  "status": {
    "id": 124,
    "status": "URLAUB",
    "valid_from": "2025-08-25T00:00:00+07:00",
    "valid_until": "2025-08-30T23:59:59+07:00",
    "created_at": "2025-08-23T14:30:00+07:00",
    "note": {
      "de": "Sommerurlaub - zurück am 31.08.",
      "th": "ลาพักร้อน - กลับวันที่ 31.08.", 
      "en": "Summer vacation - back on 31.08."
    }
  }
}
```

### Hours Management

#### Update Weekly Hours
```http
PUT /api/admin/hours/weekly
```

**Request:**
```json
{
  "monday": ["08:30-12:00", "13:00-16:00"],
  "tuesday": ["08:30-12:00", "13:00-16:00"],
  "wednesday": ["08:30-12:00"],
  "thursday": ["08:30-12:00", "13:00-16:00"],
  "friday": ["08:30-13:00"],
  "saturday": [],
  "sunday": []
}
```

#### Add Exception
```http
POST /api/admin/hours/exceptions
```

**Request:**
```json
{
  "date": "2025-08-26",
  "is_open": false,
  "hours": [],
  "reason": {
    "de": "Feiertag",
    "th": "วันหยุด",
    "en": "Public Holiday"
  }
}
```

### Announcements Management

#### Create Announcement
```http
POST /api/admin/announcements
```

**Request:**
```json
{
  "title": {
    "de": "Neue Laboröffnungszeiten",
    "th": "เวลาทำการใหม่",
    "en": "New Laboratory Hours"
  },
  "content": {
    "de": "Ab dem 1. September haben wir erweiterte Öffnungszeiten...",
    "th": "ตั้งแต่วันที่ 1 กันยายน เราจะมีเวลาทำการใหม่...",
    "en": "Starting September 1st, we have extended hours..."
  },
  "priority": "high",
  "valid_from": "2025-08-23T00:00:00+07:00",
  "valid_until": "2025-09-01T23:59:59+07:00",
  "show_on_homepage": true,
  "show_in_kiosk": true
}
```

#### Update Announcement
```http
PUT /api/admin/announcements/{id}
```

#### Delete Announcement
```http
DELETE /api/admin/announcements/{id}
```

### System Information

#### Get System Status
```http
GET /api/admin/system/status
```

**Response:**
```json
{
  "system": {
    "version": "1.0.0",
    "uptime_seconds": 86400,
    "database_status": "connected",
    "last_backup": "2025-08-23T02:00:00+07:00"
  },
  "statistics": {
    "total_visits_today": 145,
    "total_visits_month": 3200,
    "qr_scans_today": 89,
    "admin_sessions_active": 1
  },
  "health_checks": {
    "database": "ok",
    "qr_generation": "ok", 
    "external_apis": "ok",
    "disk_space": "ok"
  }
}
```

#### Get Activity Log
```http
GET /api/admin/activity?limit=50&offset=0
```

**Response:**
```json
{
  "activities": [
    {
      "id": 245,
      "action": "status_updated",
      "user": "admin",
      "details": {
        "old_status": "ANWESEND",
        "new_status": "URLAUB",
        "reason": "Summer vacation"
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2025-08-23T14:30:00+07:00"
    }
  ]
}
```

---

## QR Code API

### Generate QR Codes

#### Basic QR Code
```http
GET /api/qr?target={url}&size={size}&format={format}
```

**Parameters:**
- `target` - URL to encode (default: homepage)
- `size` - `small|medium|large` (default: medium)
- `format` - `png|svg` (default: png)

**Examples:**
```bash
# Homepage QR code
curl https://your-domain.com/api/qr > homepage.png

# Large SVG for printing
curl https://your-domain.com/api/qr?size=large&format=svg > print.svg

# Custom URL
curl "https://your-domain.com/api/qr?target=https://custom-url.com" > custom.png
```

#### QR Code with Logo
```http
GET /api/qr/branded?target={url}&logo=practice
```

#### Social Media QR Codes
```http
GET /api/qr/social/{platform}
```

**Platforms:** `line`, `facebook`, `instagram`, `whatsapp`

**Response:**
```json
{
  "qr_url": "/api/qr/social/line.png",
  "download_url": "/api/qr/social/line?download=true",
  "platform": "line",
  "target_url": "https://line.me/R/ti/p/@laborpattaya"
}
```

### QR Code Information

#### Get QR Code Stats
```http
GET /api/admin/qr/stats
```

**Response:**
```json
{
  "total_generated": 1250,
  "generated_today": 45,
  "popular_targets": [
    {"url": "/", "count": 800},
    {"url": "/week", "count": 200},
    {"url": "line://", "count": 150}
  ],
  "formats": {
    "png": 890,
    "svg": 360
  }
}
```

---

## Social Media API

### Get Social Media Configuration
```http
GET /api/social-media
```

**Response:**
```json
{
  "enabled": true,
  "platforms": {
    "line": {
      "enabled": true,
      "official_account": "@laborpattaya",
      "url": "https://line.me/R/ti/p/@laborpattaya",
      "qr_available": true
    },
    "facebook": {
      "enabled": true,
      "page_url": "https://facebook.com/laborpattaya",
      "qr_available": true
    },
    "whatsapp": {
      "enabled": true,
      "business_number": "+66381234567",
      "url": "https://wa.me/66381234567",
      "qr_available": true
    }
  },
  "settings": {
    "show_follow_section": true,
    "show_share_buttons": true,
    "qr_size": "medium",
    "button_style": "thai"
  }
}
```

### Update Social Media Settings (Admin)
```http
PUT /api/admin/social-media
```

---

## Legal Compliance API

### Privacy & PDPA

#### Get Privacy Policy
```http
GET /api/legal/privacy-policy?lang={language}
```

#### Get Cookie Policy
```http
GET /api/legal/cookie-policy?lang={language}
```

#### Data Request
```http
POST /api/legal/data-request
```

**Request:**
```json
{
  "type": "access|deletion|portability",
  "email": "patient@example.com",
  "phone": "+66381234567",
  "verification_code": "ABC123",
  "reason": "GDPR data access request"
}
```

#### Consent Management
```http
POST /api/legal/consent
```

**Request:**
```json
{
  "consent_types": ["cookies", "analytics", "marketing"],
  "granted": true,
  "user_identifier": "session_id_or_ip",
  "timestamp": "2025-08-23T14:30:00+07:00"
}
```

---

## Appointments API

**🔧 Feature flag: `FEATURE_BOOKING=true` required**

### Available Appointments

#### Get Available Slots
```http
GET /api/appointments/available?date=2025-08-24&service=BLOOD_TEST
```

**Response:**
```json
{
  "date": "2025-08-24",
  "service": "BLOOD_TEST",
  "available_slots": [
    {
      "time": "08:30",
      "duration_minutes": 30,
      "available_capacity": 2,
      "price_thb": 500,
      "requirements": {
        "fasting": true,
        "preparation_time": "8-12 hours"
      }
    }
  ]
}
```

### Book Appointment

#### Create Booking
```http
POST /api/appointments/book
```

**Request:**
```json
{
  "service": "BLOOD_TEST",
  "date": "2025-08-24",
  "time": "08:30",
  "patient": {
    "name": "John Doe",
    "phone": "+66381234567",
    "email": "john@example.com",
    "language_preference": "en"
  },
  "notes": "First time patient",
  "consent_given": true
}
```

**Response:**
```json
{
  "success": true,
  "booking": {
    "id": "BK-2025082401",
    "reference": "ABCD1234",
    "status": "confirmed",
    "service": "BLOOD_TEST",
    "date": "2025-08-24",
    "time": "08:30",
    "duration_minutes": 30,
    "confirmation_sent": true,
    "reminder_scheduled": true
  },
  "next_steps": {
    "preparation": "งดอาหาร 8-12 ชั่วโมงก่อนตรวจ",
    "arrival_time": "08:25",
    "contact_changes": "+66 38 123 456"
  }
}
```

### Booking Management (Admin)

#### Get Bookings
```http
GET /api/admin/appointments?date=2025-08-24&status=confirmed
```

#### Update Booking
```http
PUT /api/admin/appointments/{booking_id}
```

#### Cancel Booking
```http
DELETE /api/admin/appointments/{booking_id}
```

---

## Response Formats

### Success Responses

**Standard Success:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

**Collection Success:**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_items": 25,
    "items_per_page": 10
  }
}
```

### Error Responses

**Standard Error:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "field": "date",
      "issue": "Date must be in future"
    }
  }
}
```

**Validation Error:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR", 
    "message": "Validation failed",
    "validation_errors": [
      {
        "field": "phone",
        "message": "Invalid phone number format"
      },
      {
        "field": "email",
        "message": "Email address is required"
      }
    ]
  }
}
```

### Multi-language Content

All user-facing text supports multiple languages:

```json
{
  "title": {
    "de": "Deutscher Titel",
    "th": "ชื่อภาษาไทย",
    "en": "English Title"
  }
}
```

### Date/Time Formats

All timestamps use ISO 8601 format with timezone:

```json
{
  "created_at": "2025-08-23T14:30:00+07:00",
  "timezone": "Asia/Bangkok"
}
```

---

## Error Handling

### HTTP Status Codes

- `200` - Success
- `201` - Created successfully
- `204` - Success, no content
- `400` - Bad Request (client error)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (access denied)
- `404` - Not Found
- `409` - Conflict (resource conflict)
- `422` - Unprocessable Entity (validation error)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error
- `503` - Service Unavailable

### Error Codes

**Authentication:**
- `AUTH_001` - Invalid credentials
- `AUTH_002` - Session expired
- `AUTH_003` - Account locked

**Validation:**
- `VAL_001` - Required field missing
- `VAL_002` - Invalid format
- `VAL_003` - Value out of range

**Business Logic:**
- `BIZ_001` - Appointment slot unavailable
- `BIZ_002` - Service not available
- `BIZ_003` - Booking window closed

**System:**
- `SYS_001` - Database connection failed
- `SYS_002` - External service unavailable
- `SYS_003` - Configuration error

### Error Response Examples

**Bad Request:**
```json
{
  "success": false,
  "error": {
    "code": "VAL_002",
    "message": "Invalid date format",
    "details": "Date must be in YYYY-MM-DD format"
  }
}
```

**Authentication Required:**
```json
{
  "success": false,
  "error": {
    "code": "AUTH_001",
    "message": "Authentication required",
    "details": "Please login to access admin endpoints"
  }
}
```

**Rate Limited:**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT",
    "message": "Too many requests",
    "details": "Rate limit exceeded. Try again in 60 seconds.",
    "retry_after": 60
  }
}
```

---

## Rate Limiting

### Default Limits

**Public API:**
- 100 requests per minute per IP
- 1000 requests per hour per IP

**Admin API:**
- 300 requests per minute per session
- 5000 requests per hour per session

**QR Generation:**
- 50 QR codes per minute per IP
- 500 QR codes per hour per IP

### Headers

Rate limit information in response headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1692787200
X-RateLimit-Retry-After: 3600
```

### Rate Limit Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "retry_after": 3600
  }
}
```

---

## SDKs & Code Examples

### JavaScript/Node.js

```javascript
// QR Portal API Client
class QRPortalAPI {
  constructor(baseUrl, apiKey = null) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async getStatus() {
    const response = await fetch(`${this.baseUrl}/api/status`);
    return await response.json();
  }

  async getHours(date = null) {
    const url = date ? 
      `${this.baseUrl}/api/hours?date=${date}` : 
      `${this.baseUrl}/api/hours`;
    const response = await fetch(url);
    return await response.json();
  }

  async generateQR(target, size = 'medium') {
    const response = await fetch(
      `${this.baseUrl}/api/qr?target=${encodeURIComponent(target)}&size=${size}`
    );
    return await response.blob();
  }
}

// Usage
const api = new QRPortalAPI('https://your-domain.com');
const status = await api.getStatus();
console.log('Current status:', status.status);
```

### Python

```python
import requests
import json
from datetime import datetime

class QRPortalAPI:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.session = requests.Session()
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
    
    def get_status(self):
        response = self.session.get(f'{self.base_url}/api/status')
        response.raise_for_status()
        return response.json()
    
    def get_hours(self, date=None):
        url = f'{self.base_url}/api/hours'
        if date:
            url += f'?date={date}'
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def admin_login(self, username, password):
        data = {'username': username, 'password': password}
        response = self.session.post(
            f'{self.base_url}/admin/login', 
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_status(self, status, valid_from=None, valid_until=None, note=None):
        data = {'status': status}
        if valid_from:
            data['valid_from'] = valid_from
        if valid_until:
            data['valid_until'] = valid_until
        if note:
            data['note'] = note
        
        response = self.session.put(
            f'{self.base_url}/api/admin/status',
            json=data
        )
        response.raise_for_status()
        return response.json()

# Usage
api = QRPortalAPI('https://your-domain.com')
status = api.get_status()
print(f"Current status: {status['status']}")

# Admin operations
api.admin_login('admin', 'password')
result = api.update_status('URLAUB', 
    valid_from='2025-09-01T00:00:00+07:00',
    valid_until='2025-09-07T23:59:59+07:00',
    note={'de': 'Herbstferien', 'en': 'Autumn break'}
)
```

### PHP

```php
<?php
class QRPortalAPI {
    private $baseUrl;
    private $apiKey;
    
    public function __construct($baseUrl, $apiKey = null) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->apiKey = $apiKey;
    }
    
    public function getStatus() {
        return $this->makeRequest('/api/status');
    }
    
    public function getHours($date = null) {
        $endpoint = '/api/hours';
        if ($date) {
            $endpoint .= '?date=' . urlencode($date);
        }
        return $this->makeRequest($endpoint);
    }
    
    public function generateQR($target, $size = 'medium', $format = 'png') {
        $params = http_build_query([
            'target' => $target,
            'size' => $size,
            'format' => $format
        ]);
        
        $url = $this->baseUrl . '/api/qr?' . $params;
        return file_get_contents($url);
    }
    
    private function makeRequest($endpoint, $method = 'GET', $data = null) {
        $url = $this->baseUrl . $endpoint;
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'Accept: application/json'
        ]);
        
        if ($this->apiKey) {
            curl_setopt($ch, CURLOPT_HTTPHEADER, array_merge(
                curl_getopt($ch, CURLOPT_HTTPHEADER),
                ['Authorization: Bearer ' . $this->apiKey]
            ));
        }
        
        if ($method === 'POST' && $data) {
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode >= 400) {
            throw new Exception("API request failed with status $httpCode");
        }
        
        return json_decode($response, true);
    }
}

// Usage
$api = new QRPortalAPI('https://your-domain.com');
$status = $api->getStatus();
echo "Current status: " . $status['status'] . "\n";
?>
```

### cURL Examples

```bash
# Get current status
curl -H "Accept: application/json" \
  https://your-domain.com/api/status

# Get today's hours
curl -H "Accept: application/json" \
  https://your-domain.com/api/hours

# Generate QR code
curl -o homepage-qr.png \
  "https://your-domain.com/api/qr?size=large"

# Admin login
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}' \
  -c cookies.txt \
  https://your-domain.com/admin/login

# Update status (admin)
curl -X PUT \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"status":"URLAUB","note":{"de":"Ferienzeit"}}' \
  https://your-domain.com/api/admin/status

# Create announcement (admin)
curl -X POST \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": {"de": "Wichtiger Hinweis"},
    "content": {"de": "Neue Öffnungszeiten ab morgen"},
    "priority": "high",
    "show_on_homepage": true
  }' \
  https://your-domain.com/api/admin/announcements
```

---

## Webhooks

### Webhook Events

The system can send webhooks for important events:

**Available Events:**
- `status.updated` - Practice status changed
- `hours.updated` - Opening hours modified
- `announcement.created` - New announcement published
- `appointment.booked` - New appointment booked (if enabled)
- `system.error` - System error occurred

### Webhook Configuration (Admin)

```http
POST /api/admin/webhooks
```

**Request:**
```json
{
  "url": "https://your-service.com/webhook",
  "events": ["status.updated", "announcement.created"],
  "secret": "your-webhook-secret",
  "active": true
}
```

### Webhook Payload

```json
{
  "event": "status.updated",
  "timestamp": "2025-08-23T14:30:00+07:00",
  "data": {
    "old_status": "ANWESEND",
    "new_status": "URLAUB",
    "valid_from": "2025-08-25T00:00:00+07:00",
    "valid_until": "2025-08-30T23:59:59+07:00"
  },
  "portal_url": "https://your-domain.com"
}
```

### Webhook Security

Webhooks are signed with HMAC-SHA256:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(
        f"sha256={expected_signature}",
        signature
    )
```

---

## Testing & Development

### Test Environment

```bash
# Development server
FLASK_ENV=development flask run --debug

# Test with sample data
curl http://localhost:5000/api/status
```

### API Testing Tools

**Postman Collection:**
```json
{
  "info": {
    "name": "QR Info Portal API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Status",
      "request": {
        "method": "GET",
        "header": [
          {"key": "Accept", "value": "application/json"}
        ],
        "url": {
          "raw": "{{base_url}}/api/status",
          "host": ["{{base_url}}"],
          "path": ["api", "status"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "https://your-domain.com"
    }
  ]
}
```

### Mock Data

For testing, the API provides mock endpoints:

```bash
# Enable test mode
export FLASK_ENV=testing

# Mock endpoints
curl http://localhost:5000/api/test/status
curl http://localhost:5000/api/test/hours
curl http://localhost:5000/api/test/announcements
```

### Integration Tests

```python
import pytest
import requests

class TestQRPortalAPI:
    def setup_class(self):
        self.base_url = 'http://localhost:5000'
    
    def test_get_status(self):
        response = requests.get(f'{self.base_url}/api/status')
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert data['status'] in ['ANWESEND', 'GESCHLOSSEN', 'URLAUB', 'BILDUNGSURLAUB', 'KONGRESS', 'SONSTIGES']
    
    def test_get_hours(self):
        response = requests.get(f'{self.base_url}/api/hours')
        assert response.status_code == 200
        data = response.json()
        assert 'today' in data
        assert 'week' in data
    
    def test_qr_generation(self):
        response = requests.get(f'{self.base_url}/api/qr')
        assert response.status_code == 200
        assert response.headers['content-type'].startswith('image/')
```

### OpenAPI Specification

The API provides an OpenAPI/Swagger specification:

```http
GET /api/openapi.json
```

**Swagger UI:**
```http
GET /api/docs
```

---

## Changelog & Versioning

### Version 1.0.0 (Current)
- Initial API release
- Public endpoints for status, hours, announcements
- Admin endpoints for content management  
- QR code generation
- Multi-language support

### Planned Features (v1.1.0)
- API key authentication
- Webhook system
- Enhanced appointment booking API
- Real-time WebSocket updates
- API analytics dashboard

### Breaking Changes Policy

- **Major versions** (2.0.0) - May contain breaking changes
- **Minor versions** (1.1.0) - New features, backward compatible
- **Patch versions** (1.0.1) - Bug fixes, backward compatible

All breaking changes will be announced 3 months in advance with migration guides.

---

**📚 API Documentation Version:** 1.0.0 | **Last Updated:** 2025-08-23  
**🔗 Base URL:** https://your-domain.com/api  
**📧 API Support:** api-support@pattaya-medical.com