#!/bin/bash
# QR-Info-Portal Codespace Startup Script
# Fixes "Cannot GET /" error in GitHub Codespaces

set -e  # Exit on any error

echo "🚀 QR-Info-Portal Codespace Startup"
echo "=================================="

# 1. Kill existing Flask processes
echo "📛 Stopping existing Flask processes..."
pkill -f "python.*flask" 2>/dev/null || true
pkill -f ".*run.py" 2>/dev/null || true
sleep 2

# 2. Check dependencies
echo "📦 Checking Python dependencies..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install requirements if needed
if [ ! -f ".venv/requirements_installed" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    touch .venv/requirements_installed
fi

# 3. Load environment variables
echo "⚙️  Loading environment variables..."
if [ ! -f ".env" ]; then
    echo "❌ .env file not found! Copying from .env.example..."
    cp .env.example .env
fi

source .env

# 4. Set Flask environment
echo "🔧 Setting Flask environment..."
export FLASK_APP=run.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export PYTHONPATH=/workspace

# 5. Check database
echo "🗄️  Checking database..."
mkdir -p data
if [ ! -f "data/portal.db" ]; then
    echo "Database not found, will be created on first run"
fi

# 6. Start Flask server
echo "🌐 Starting Flask server..."
echo "   Local: http://localhost:5000"
echo "   Admin: http://localhost:5000/admin (admin/admin123)"

# Start in background for Codespace
nohup python3 run.py > flask_startup.log 2>&1 &
FLASK_PID=$!

echo "   Process ID: $FLASK_PID"

# 7. Wait for startup and test
echo "⏳ Waiting for Flask to start..."
for i in {1..10}; do
    if curl -s http://localhost:5000/healthz | grep -q "healthy"; then
        echo "✅ Flask server is healthy!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Flask server not responding after 10 attempts"
        echo "   Check logs: tail -f flask_startup.log"
        exit 1
    fi
    echo "   Attempt $i/10 - waiting..."
    sleep 2
done

# 8. Test critical routes
echo "🧪 Testing routes..."
routes=(
    "/"
    "/healthz" 
    "/week"
    "/month"
    "/qr"
)

for route in "${routes[@]}"; do
    if curl -s -I "http://localhost:5000$route" | head -1 | grep -q "200 OK"; then
        echo "   ✅ $route: OK"
    else
        echo "   ❌ $route: FAILED"
    fi
done

# 9. Show status
echo ""
echo "📊 Final Status:"
echo "   Flask PID: $(ps aux | grep flask | grep -v grep | awk '{print $2}' | head -1)"
echo "   Port 5000: $(lsof -i :5000 | wc -l) connections"
echo "   Database: $(ls -lah data/portal.db 2>/dev/null | awk '{print $5}' || echo 'Not found')"

# 10. Codespace-specific info
if [ -n "$CODESPACE_NAME" ]; then
    echo ""
    echo "🌍 GitHub Codespace Access:"
    echo "   External URL: https://${CODESPACE_NAME}-5000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}/"
    echo "   📝 Note: Use the Ports tab in VS Code to access the forwarded port"
fi

echo ""
echo "🎉 Startup complete! Flask should now be accessible."
echo "   To monitor: tail -f flask_startup.log"
echo "   To stop: pkill -f 'python.*flask'"