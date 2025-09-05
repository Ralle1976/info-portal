# 🚨 CRITICAL: "Cannot GET /" Fix für Codespace

## Problem: Flask Server läuft nicht richtig im Codespace

## ⚡ SOFORT-LÖSUNG (Copy & Paste):

```bash
# 1. Alle alten Flask-Prozesse killen
pkill -f "python.*flask" 2>/dev/null || true
pkill -f "run.py" 2>/dev/null || true
sleep 2

# 2. Environment richtig setzen
export FLASK_APP=run.py
export FLASK_ENV=development  
export FLASK_DEBUG=1
export PYTHONPATH=$(pwd)

# 3. Virtual Environment aktivieren (falls vorhanden)
if [ -d ".venv" ]; then source .venv/bin/activate; fi

# 4. Flask korrekt starten
python3 run.py
```

## 🧪 TESTEN:
```bash
# In neuem Terminal:
curl -I http://localhost:5000/
# Sollte: HTTP/1.1 200 OK zeigen

curl http://localhost:5000/healthz
# Sollte: {"status": "healthy"} zeigen
```

## 📋 DEBUG FALLS PROBLEME:
```bash
# 1. Prüfe ob run.py existiert
ls -la run.py

# 2. Prüfe Python Module
python3 -c "from app import create_app; print('OK')"

# 3. Prüfe Prozesse
ps aux | grep -E "(flask|python)" | grep -v grep

# 4. Prüfe Ports
ss -tlnp | grep 5000
```

## 🔧 ALTERNATIVE STARTUP:
```bash
# Falls run.py nicht funktioniert:
export FLASK_APP=app
python3 -m flask run --host=0.0.0.0 --port=5000
```

## ✅ NACH DEM FIX:
- ✅ http://localhost:5000/ → QR Portal Homepage
- ✅ http://localhost:5000/admin/ → Admin Interface  
- ✅ http://localhost:5000/qr → QR Code Generation
- ✅ External URL funktioniert über Port Forwarding