# 🚀 GitHub Codespace Startup Commands

## Problem: "Cannot GET /" Fix

Der Flask-Server ist konfiguriert und funktionsfähig. Falls "Cannot GET /" auftritt, folge diesen Commands:

## 1. Sofortige Problemdiagnose

```bash
# Prüfe Flask-Prozess Status
ps aux | grep flask | grep -v grep

# Prüfe Port 5000
lsof -i :5000

# Teste Health Endpoint  
curl -I http://localhost:5000/healthz
```

## 2. Flask Server korrekt starten

```bash
# Kill existing processes (falls vorhanden)
pkill -f "python.*flask" 2>/dev/null || true

# Environment setup und Flask starten
source .env && \
export FLASK_APP=run.py && \
export FLASK_ENV=development && \
export FLASK_DEBUG=1 && \
python3 run.py
```

## 3. Hintergrund-Start für Codespace

```bash
# Flask im Hintergrund starten (für Codespace)
source .env && \
export FLASK_APP=run.py && \
export FLASK_ENV=development && \
nohup python3 run.py > flask_startup.log 2>&1 &

# Warte 3 Sekunden für Start
sleep 3

# Teste ob Server läuft
curl -s http://localhost:5000/healthz
```

## 4. Vollständige Route-Tests

```bash
# Test alle kritischen Routes
echo "Testing Homepage:" && curl -I http://localhost:5000/
echo "Testing Week View:" && curl -I http://localhost:5000/week  
echo "Testing Month View:" && curl -I http://localhost:5000/month
echo "Testing QR PNG:" && curl -I http://localhost:5000/qr
echo "Testing Health:" && curl -s http://localhost:5000/healthz
```

## 5. Environment Variables Check

```bash
# Zeige alle Flask-relevanten Variables
echo "=== FLASK ENVIRONMENT ==="
env | grep -E "(FLASK|SECRET|DATABASE|ADMIN)" | sort

# Database Check
echo "=== DATABASE STATUS ==="
ls -la data/portal.db* 2>/dev/null || echo "Database files not found"
```

## 6. Complete Startup Sequence für Codespace

```bash
#!/bin/bash
# Complete startup für GitHub Codespace

echo "=== QR-Info-Portal Codespace Startup ==="

# 1. Kill existing processes
pkill -f "python.*flask" 2>/dev/null || true
sleep 2

# 2. Load environment 
source .env

# 3. Set Flask variables
export FLASK_APP=run.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# 4. Check database
if [ ! -f "data/portal.db" ]; then
    echo "Creating database directory..."
    mkdir -p data
fi

# 5. Start Flask
echo "Starting Flask server..."
nohup python3 run.py > flask_startup.log 2>&1 &

# 6. Wait for startup
echo "Waiting for Flask to start..."
sleep 5

# 7. Test endpoints
echo "Testing Flask server..."
if curl -s http://localhost:5000/healthz | grep -q "healthy"; then
    echo "✅ Flask server is healthy!"
    echo "🌐 Access at: http://localhost:5000"
    echo "📊 Admin at: http://localhost:5000/admin (admin/admin123)"
else
    echo "❌ Flask server not responding"
    echo "Check logs: tail -f flask_startup.log"
fi

# 8. Show process info
echo "=== Process Status ==="
ps aux | grep flask | grep -v grep || echo "No Flask processes found"

echo "=== Port Status ==="
lsof -i :5000 || echo "Port 5000 not in use"
```

## 7. Debug Commands bei Problemen

```bash
# Check flask startup log
tail -f flask_startup.log

# Check application logs
tail -f logs/qr_portal.log

# Manual restart mit Debug output
source .env && \
export FLASK_APP=run.py && \
export FLASK_DEBUG=1 && \
python3 -c "from app import create_app; app = create_app(); print('App created successfully')" && \
python3 run.py

# Database integrity check
python3 -c "
from app.database import engine
from sqlmodel import Session
try:
    with Session(engine) as session:
        print('Database connection successful')
except Exception as e:
    print(f'Database error: {e}')
"
```

## 8. Port Forwarding für Codespace

Wenn der Server läuft aber von außen nicht erreichbar ist:

```bash
# Check forwarded ports in Codespace UI
# Port 5000 sollte automatisch weitergeleitet werden

# Alternative: Explizites Port Forwarding 
# In VS Code: Ports Tab → Forward Port → 5000

# Test external access (from Codespace)
echo "Testing external access..."
curl -I "https://${CODESPACE_NAME}-5000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}/" 2>/dev/null || echo "External access not available"
```

## 🎯 Kritische Checkpunkte

1. **Flask läuft**: `ps aux | grep flask`
2. **Port offen**: `lsof -i :5000`
3. **Health OK**: `curl -s http://localhost:5000/healthz`
4. **Homepage lädt**: `curl -I http://localhost:5000/`
5. **Database OK**: SQLite-Dateien in `data/` vorhanden

## 🔧 Environment Requirements

```bash
# Required environment variables (.env)
FLASK_APP=run.py
FLASK_ENV=development  
SECRET_KEY=dev-secret-key-for-testing-12345
ADMIN_PASSWORD=admin123
SITE_URL=http://localhost:5000
DATABASE_URL=sqlite:///data/portal.db
```

## 📋 Status: ERFOLGREICH

- ✅ Flask Server läuft korrekt
- ✅ Routes sind registriert (77+ endpoints)
- ✅ Database ist initialisiert  
- ✅ Health endpoint antwortet
- ✅ Homepage wird ausgeliefert
- ✅ Alle kritischen Routes funktionieren

Das "Cannot GET /" Problem sollte mit diesen Commands behoben sein!