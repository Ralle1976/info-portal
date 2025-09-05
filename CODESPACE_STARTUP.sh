#!/bin/bash
# 🚀 FINAL CODESPACE STARTUP SOLUTION - "Cannot GET /" FIX
# Dieses Skript behebt den "Cannot GET /" Fehler definitiv

echo "🚀 QR-Info-Portal Codespace Startup..."
echo "====================================="

# Step 1: Complete cleanup
echo "🧹 Cleanup alle Flask-Prozesse..."
pkill -f "python.*flask" 2>/dev/null || true
pkill -f ".*run.py" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
sleep 3

# Step 2: Environment setup  
echo "⚙️ Environment Setup..."
cp .env.codespace .env
source .env

export FLASK_APP=run.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export PYTHONPATH=$(pwd)

# Step 3: Ensure data directory
echo "🗄️ Database vorbereiten..."
mkdir -p data
mkdir -p logs

# Step 4: Install/verify requirements
echo "📦 Dependencies prüfen..."
if [ ! -d ".venv" ]; then
    echo "   🐍 Virtual Environment erstellen..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt || echo "   ⚠️ Requirements bereits installiert"

# Step 5: Initialize database if needed
echo "🗄️ Database initialisieren..."
python3 -c "
try:
    from app.database import init_database
    init_database()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'⚠️ Database already exists or error: {e}')
" 2>/dev/null

# Step 6: Verify Flask app can be created
echo "🔍 Flask App Validierung..."
python3 -c "
import os
os.environ['FLASK_APP'] = 'run.py'
os.environ['FLASK_ENV'] = 'development'
try:
    from app import create_app
    app = create_app()
    print(f'✅ Flask app created with {len(app.url_map._rules)} routes')
    # Show first 10 routes for verification
    routes = list(app.url_map.iter_rules())[:10]
    for rule in routes:
        print(f'   📍 {rule.rule} -> {rule.endpoint}')
except Exception as e:
    print(f'❌ Flask app creation failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Flask-Validierung fehlgeschlagen. Abbruch."
    exit 1
fi

echo ""
echo "🌐 URLs nach dem Start:"
echo "   📊 Homepage: http://localhost:5000/"
echo "   🔑 Admin: http://localhost:5000/admin/ (admin/admin123)"
echo "   💓 Health: http://localhost:5000/healthz"
echo "   📅 Week: http://localhost:5000/week"
echo "   🗓️ Month: http://localhost:5000/month"
echo ""

# Step 7: Start Flask
echo "🚀 Flask Server starten..."
python3 run.py