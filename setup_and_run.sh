#!/bin/bash

echo "🚀 QR-Info-Portal Setup und Test"
echo "================================="

# Check if we're in the right directory
if [ ! -f "run.py" ]; then
    echo "❌ Nicht im richtigen Verzeichnis! Navigiere zu qr-info-portal/"
    exit 1
fi

echo "📁 Arbeitsverzeichnis: $(pwd)"

# Create .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env Datei erstellt"
else
    echo "✅ .env Datei existiert bereits"
fi

# Try Docker first (recommended)
echo ""
echo "🐳 Versuche Docker Setup..."
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "✅ Docker gefunden - starte mit docker-compose"
    docker-compose up -d
    
    # Wait for container to start
    echo "⏳ Warte auf Container-Start..."
    sleep 10
    
    # Get container IP
    CONTAINER_IP=$(docker-compose exec web hostname -i 2>/dev/null | tr -d '\r')
    echo ""
    echo "🌐 Portal läuft in Docker!"
    echo "   - Lokal: http://localhost:5000"
    echo "   - Container: http://${CONTAINER_IP}:5000"
    
    # Test health endpoint
    if curl -s http://localhost:5000/healthz > /dev/null; then
        echo "✅ Health Check erfolgreich"
        echo ""
        echo "🎉 Portal ist bereit!"
        echo "   📱 QR-Code: http://localhost:5000/qr"
        echo "   🔧 Admin: http://localhost:5000/admin (admin/admin123)"
    else
        echo "❌ Health Check fehlgeschlagen"
        docker-compose logs
    fi
else
    echo "❌ Docker nicht verfügbar"
    echo ""
    echo "📦 Alternative: Python direkt verwenden"
    echo "   Installiere manuell:"
    echo "   pip3 install --break-system-packages Flask SQLModel python-dotenv PyYAML pytz 'qrcode[pil]' gunicorn"
    echo ""
    echo "   Dann starten mit:"
    echo "   python3 run.py"
    echo ""
    echo "📋 Oder nutze die requirements.txt:"
    echo "   pip3 install --break-system-packages -r requirements.txt"
    echo "   python3 run.py"
fi

# Get LAN IP
echo ""
echo "🌐 LAN IP-Adressen für externen Zugriff:"
if command -v hostname &> /dev/null; then
    hostname -I 2>/dev/null | awk '{print "   http://" $1 ":5000"}' || echo "   IP-Ermittlung fehlgeschlagen"
fi

if command -v ip &> /dev/null; then
    ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print "   http://" $2}' | cut -d/ -f1 | head -3
fi