#!/bin/bash
# 🚀 Flask Startup Script für GitHub Codespace

echo "🔧 Starting Flask Server für QR-Info-Portal..."

# 1. Cleanup alte Prozesse
echo "🧹 Cleanup alte Flask-Prozesse..."
pkill -f "python.*flask" 2>/dev/null || true
pkill -f "run.py" 2>/dev/null || true
sleep 2

# 2. Environment Variables setzen
echo "⚙️ Environment Variables setzen..."
export FLASK_APP=run.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export PYTHONPATH=$(pwd)
export SITE_URL="https://$(echo $CODESPACE_NAME)-5000.app.github.dev"

# 3. Virtual Environment aktivieren
if [ -d ".venv" ]; then
    echo "🐍 Virtual Environment aktivieren..."
    source .venv/bin/activate
fi

# 4. Dependencies prüfen
echo "📦 Dependencies prüfen..."
pip install -q -r requirements.txt 2>/dev/null || echo "⚠️ Requirements installation skipped"

# 5. Database initialisieren
echo "🗄️ Database prüfen..."
python3 -c "from app.database import init_database; init_database()" 2>/dev/null || echo "⚠️ Database already initialized"

# 6. Flask starten
echo "🚀 Flask Server starten auf Port 5000..."
echo "🌐 URL: http://localhost:5000"
echo "🌐 External: https://$(echo $CODESPACE_NAME)-5000.app.github.dev (falls Codespace)"
echo ""

# Start Flask
python3 run.py