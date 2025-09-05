# QR-Info-Portal für Laborstandorte

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.1+-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

Ein modernes Webangebot für medizinische Laborstandorte in Thailand, das Besuchern sofortige Informationen über Verfügbarkeit, Öffnungszeiten und Servicestatus über QR-Code-Zugang bereitstellt.

## 🌟 Features

### 🎯 Kernfunktionen
- **QR-Code Integration** - Sofortiger Zugang via Türbeschilderung
- **Multi-Language Support** - Deutsch, Thai (ไทย), English
- **Responsive Design** - Optimiert für Mobile, Tablet & Desktop
- **Kiosk-Modi** - Spezielle Vollbild-Ansichten für Monitore
- **Real-Time Status** - Live-Updates zu Öffnungszeiten und Verfügbarkeit

### 🏥 Speziell für medizinische Einrichtungen
- **Status-Management** - Anwesend, Urlaub, Fortbildung, Kongress
- **Öffnungszeiten** - Wochenplan mit Ausnahmen
- **Terminverfügbarkeit** - Indikative Zeitfenster-Anzeige
- **Kontakt & Anfahrt** - Integration mit Google Maps
- **PDPA/GDPR Compliance** - Thai- und EU-Datenschutz

### 🖥️ Admin-Funktionen
- **Web-basiertes Admin-Panel** - Einfache Verwaltung
- **Multi-Agent System** - Erweiterte Funktionen durch Module
- **Social Media Integration** - QR-Codes für soziale Medien
- **Terminbuchungs-System** - Erweiterbar für Online-Buchungen
- **Rechtliche Compliance** - Automatische Dokumentation

## 🚀 Quick Start

### Voraussetzungen
- Python 3.11+
- Git
- Webbrowser

### Installation (5 Minuten)

```bash
# 1. Repository klonen
git clone https://github.com/Ralle1976/qr-info-portal.git
cd qr-info-portal

# 2. Virtual Environment erstellen
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Konfiguration erstellen
cp .env.example .env
# Bearbeiten Sie .env mit Ihren Einstellungen

# 5. Datenbank initialisieren
python -c "from app.database import init_database; init_database()"

# 6. Server starten
flask run --host 0.0.0.0 --port 5000
```

**Das Portal ist jetzt verfügbar unter:**
- Lokal: http://127.0.0.1:5000
- LAN: http://[Ihre-IP]:5000

## 🔧 Konfiguration

### Grundkonfiguration (`config.yml`)
```yaml
site:
  name: "Labor Pattaya – Blutabnahme"
  languages: ["de", "th", "en"]
  default_language: "de"
  timezone: "Asia/Bangkok"

location:
  address: "Ihre Adresse, Pattaya"
  latitude: 12.923556
  longitude: 100.882507

contact:
  phone: "+66 XXX XXX XXX"
  email: "info@labor-pattaya.com"

hours:
  weekly:
    mon: ["08:30-12:00", "13:00-16:00"]
    tue: ["08:30-12:00", "13:00-16:00"]
    wed: ["08:30-12:00"]
    thu: ["08:30-12:00", "13:00-16:00"]
    fri: ["08:30-13:00"]
    sat: []
    sun: []
```

### Umgebungsvariablen (`.env`)
```bash
# Flask
FLASK_APP=app
FLASK_ENV=production
SECRET_KEY=your-super-secret-key

# Admin
ADMIN_PASSWORD=secure-admin-password

# Features
FEATURE_BOOKING=false
FEATURE_SOCIAL_MEDIA=true

# Site
SITE_URL=https://your-domain.com
```

## 📱 Verwendung

### Für Besucher
1. **QR-Code scannen** an der Eingangstür
2. **Sofortige Information** über aktuellen Status
3. **Öffnungszeiten** für heute, diese Woche, diesen Monat
4. **Kontakt & Anfahrt** mit Google Maps Integration

### Für Administratoren
1. **Admin-Panel** unter `/admin` (Login erforderlich)
2. **Status ändern** - Anwesend/Urlaub/Fortbildung
3. **Öffnungszeiten** und Ausnahmen verwalten
4. **QR-Codes** für Druck generieren
5. **Mehrsprachige Inhalte** bearbeiten

### Kiosk-Modi
- **Single View**: `/kiosk/single` - Große Uhr mit aktuellem Status
- **Triple View**: `/kiosk/triple` - 3-Spalten-Layout (Heute|Woche|Vorschau)

## 🖼️ QR-Codes

### Automatische Generierung
- **PNG**: `/qr` - Für Digitalanzeigen (300-600 DPI)
- **SVG**: `/qr.svg` - Für Druckmaterialien (skalierbar)

### Empfohlene Verwendung
- **A4 Türschild** - QR-Code + Grundinformationen
- **Plakate** - QR-Code + Werbematerial
- **Visitenkarten** - Kompakte QR-Codes
- **Digital Signage** - Einbindung in Monitore

## 🗂️ Projektstruktur

```
qr-info-portal/
├── app/
│   ├── __init__.py              # Flask App Factory
│   ├── models.py                # Datenbank Modelle
│   ├── routes_public.py         # Öffentliche Routen
│   ├── routes_admin.py          # Admin Panel
│   ├── services/                # Business Logic
│   │   ├── schedule.py          # Öffnungszeiten
│   │   ├── status.py           # Status Management
│   │   ├── qr.py               # QR-Code Generation
│   │   └── i18n.py             # Internationalisierung
│   ├── templates/              # Jinja2 Templates
│   └── static/                 # CSS, JS, Assets
├── data/                       # SQLite Datenbank
├── config.yml                  # Hauptkonfiguration
├── requirements.txt            # Python Abhängigkeiten
├── Dockerfile                  # Docker Container
└── docker-compose.yml         # Docker Orchestrierung
```

## 🚢 Deployment

### Lokales Netzwerk (Empfohlen für Start)
```bash
# Starten Sie den Server im LAN
flask run --host 0.0.0.0 --port 5000

# Finden Sie Ihre IP-Adresse
ip addr show  # Linux
ipconfig      # Windows
```

### Docker (Produktion)
```bash
# Container erstellen und starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f

# Stoppen
docker-compose down
```

### Cloud-Deployment
- **Heroku**: `git push heroku main`
- **Railway**: Direkte GitHub-Integration
- **DigitalOcean**: App Platform
- **AWS**: Elastic Beanstalk

## 🔒 Sicherheit

### Datenschutz
- **PDPA Thailand** - Vollständige Compliance
- **EU GDPR** - Internationale Standards
- **Keine Patientendaten** - Nur Öffnungszeiten und Kontakt
- **Basic Auth** für Admin-Bereich

### Empfehlungen
- Starke Passwörter verwenden
- HTTPS in Produktion aktivieren
- Regelmäßige Backups
- Firewall-Konfiguration

## 🛠️ Erweiterungen

### Verfügbare Module
- **Terminbuchungs-System** - Online-Termine
- **Social Media Integration** - Automatische Posts
- **Legal Compliance** - Automatische Dokumentation
- **Multi-Monitor Support** - Verschiedene Kiosk-Modi

### Feature-Flags
```bash
# In .env aktivieren/deaktivieren
FEATURE_BOOKING=true          # Terminbuchungen
FEATURE_SOCIAL_MEDIA=true     # Social Media
FEATURE_LEGAL_EXTENDED=true   # Erweiterte Compliance
```

## 📞 Support

### Dokumentation
- **Setup**: [SETUP.md](SETUP.md) - Detaillierte Installation
- **API**: [API.md](API.md) - Alle verfügbaren Endpunkte
- **Features**: [FEATURES.md](FEATURES.md) - Vollständige Feature-Liste
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md) - Produktions-Setup

### Community
- **GitHub Issues**: Fehlerberichte und Feature-Requests
- **Discussions**: Community-Support und Ideen
- **Wiki**: Erweiterte Dokumentation und Tutorials

## 👨‍💻 Entwicklung

### Lokale Entwicklung
```bash
# Development Server mit Auto-Reload
FLASK_ENV=development flask run --debug

# Tests ausführen
python -m pytest tests/

# Code-Qualität
black . --check
flake8 .
```

### Beitragen
1. Fork des Repositories
2. Feature-Branch erstellen
3. Tests hinzufügen
4. Pull Request stellen

## 📄 Lizenz

MIT License - Siehe [LICENSE](LICENSE) für Details.

## 🙏 Danksagungen

- **Thai Community** - Für kulturelle Beratung
- **Medical Professionals** - Für Anforderungs-Feedback
- **Open Source Community** - Für verwendete Bibliotheken

---

**🏥 Perfekt für medizinische Einrichtungen in Thailand und international!**

[![Made in Thailand](https://img.shields.io/badge/Made%20in-Thailand-red.svg)]()
[![Built with Flask](https://img.shields.io/badge/Built%20with-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Responsive](https://img.shields.io/badge/Responsive-Yes-brightgreen.svg)]()