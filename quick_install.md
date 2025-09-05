# 🚀 QR-Info-Portal - Schnellstart

## Option 1: Docker (Empfohlen)

```bash
# Repository klonen
git clone https://github.com/Ralle1976/qr-info-portal.git
cd qr-info-portal

# Mit Docker starten
docker-compose up -d

# Prüfen ob es läuft
curl http://localhost:5000/healthz
```

**Fertig!** Portal läuft unter: http://localhost:5000

## Option 2: Python direkt

```bash
# Repository klonen
git clone https://github.com/Ralle1976/qr-info-portal.git
cd qr-info-portal

# Dependencies installieren
pip3 install --break-system-packages -r requirements.txt

# .env Datei erstellen
cp .env.example .env

# Starten
python3 run.py
```

## Option 3: Setup-Script verwenden

```bash
git clone https://github.com/Ralle1976/qr-info-portal.git
cd qr-info-portal
./setup_and_run.sh
```

## 🌐 Zugriff

- **Lokal**: http://localhost:5000
- **LAN**: http://[DEINE-IP]:5000
- **QR-Code**: http://localhost:5000/qr
- **Admin**: http://localhost:5000/admin (admin/admin123)

## 📱 QR-Code generieren

```bash
# PNG für Druck
curl http://localhost:5000/qr > portal.png

# SVG für Skalierung  
curl http://localhost:5000/qr.svg > portal.svg

# Custom URL
curl "http://localhost:5000/qr?target=https://meine-domain.com" > custom.png
```

## ✅ Test

```bash
# Health Check
curl http://localhost:5000/healthz

# Sollte zurückgeben:
# {"status":"healthy","service":"qr-info-portal"}
```

## 🔧 Konfiguration

Bearbeite `config.yml` für:
- Standortdaten (Koordinaten, Adresse)
- Kontaktinformationen  
- Öffnungszeiten
- Mehrsprachige Inhalte

## 🛠️ Troubleshooting

**Python-Fehler "externally-managed-environment":**
```bash
pip3 install --break-system-packages -r requirements.txt
```

**Docker nicht verfügbar:**
- Windows: Docker Desktop installieren
- Linux: `sudo apt install docker.io docker-compose`
- macOS: Docker Desktop installieren

**Port bereits belegt:**
```bash
# Anderen Port verwenden
export FLASK_PORT=5001
python3 run.py
```

## 📋 Features

✅ Multi-Sprach-Support (Thai, Deutsch, Englisch)  
✅ QR-Code Generation (PNG/SVG)  
✅ Status-Management (Urlaub, Kongress, etc.)  
✅ Öffnungszeiten-Verwaltung  
✅ Responsive Thai-inspiriertes Design  
✅ Docker-Support  
✅ LAN-Zugriff für mobile Geräte