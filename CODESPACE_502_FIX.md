# 🚨 GitHub Codespace HTTP 502 Fix

## Problem: 
Port 5000 ist PRIVAT (benötigt GitHub Login) → HTTP 502 Error

## SOFORTIGE LÖSUNG:

### Option 1: Port öffentlich machen (TERMINAL im Codespace)
```bash
gh codespace ports visibility 5000:public
```

### Option 2: GitHub Web UI
1. Im Codespace → "PORTS" Tab (unten)
2. Port 5000 → Rechtsklick → "Change Port Visibility" → PUBLIC

### Option 3: Flask neu starten mit Public URL
```bash
pkill -f flask
source .venv/bin/activate
export FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5000
```

### Dann testen:
```bash
curl -I http://localhost:5000
# Sollte HTTP 200 zeigen
```

## Nach dem Fix:
✅ https://cautious-halibut-xrrpx6rx7x4c6q44-5000.app.github.dev/ sollte funktionieren

## Falls immer noch 502:
```bash
# Debug Commands im Codespace:
ps aux | grep flask           # Prüfe ob Flask läuft
ss -tlnp | grep 5000         # Prüfe Port
gh codespace ports           # Zeige Port Status
```