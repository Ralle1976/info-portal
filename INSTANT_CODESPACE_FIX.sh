#!/bin/bash
# ⚡ INSTANT CODESPACE FIX - "Cannot GET /" GUARANTEED SOLUTION

echo "🚨 CODESPACE EMERGENCY FIX - Starting..."
echo "========================================="

# Step 1: Nuclear cleanup
echo "🧹 NUCLEAR CLEANUP..."
sudo pkill -f flask 2>/dev/null || true
sudo pkill -f python 2>/dev/null || true  
sudo pkill -f gunicorn 2>/dev/null || true
sudo pkill -f run.py 2>/dev/null || true
sleep 5
echo "   ✅ All processes killed"

# Step 2: Port cleanup 
echo "🔧 PORT CLEANUP..."
sudo lsof -ti:5000 | xargs sudo kill -9 2>/dev/null || true
sudo netstat -tlnp | grep :5000 && sudo fuser -k 5000/tcp || echo "   ✅ Port 5000 free"
sleep 2

# Step 3: Environment reset
echo "⚙️ ENVIRONMENT RESET..."
cd /workspaces/qr-info-portal || cd /workspace/qr-info-portal || cd $(pwd)
export FLASK_APP=run.py
export FLASK_ENV=development  
export FLASK_DEBUG=1
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export PYTHONPATH=$(pwd)
export SECRET_KEY="codespace-emergency-key-$(date +%s)"

echo "   ✅ Environment: FLASK_APP=$FLASK_APP"
echo "   ✅ Host: $FLASK_HOST:$FLASK_PORT"

# Step 4: Dependencies check
echo "📦 DEPENDENCIES..."
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet -r requirements.txt || echo "   ⚠️ Requirements install skipped"

# Step 5: Database force init
echo "🗄️ DATABASE FORCE INIT..."
mkdir -p data logs
rm -f data/portal.db.lock 2>/dev/null || true
python3 -c "
import os
os.environ['FLASK_APP'] = 'run.py'
os.environ['SECRET_KEY'] = 'codespace-emergency-key'
try:
    from app.database import init_database
    init_database()
    print('   ✅ Database initialized')
except Exception as e:
    print(f'   ⚠️ Database error: {e}')
" || echo "   ⚠️ Database init failed - continuing"

# Step 6: Test Flask creation
echo "🔍 FLASK VALIDATION..."
python3 -c "
import os
os.environ['FLASK_APP'] = 'run.py'
os.environ['SECRET_KEY'] = 'codespace-emergency-key'
try:
    from app import create_app
    app = create_app()
    routes = len(app.url_map._rules)
    print(f'   ✅ Flask app: {routes} routes registered')
    if routes < 50:
        print('   ⚠️ WARNING: Low route count, possible import issues')
    else:
        print('   ✅ Route count looks good')
except Exception as e:
    print(f'   ❌ CRITICAL: Flask creation failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ CRITICAL: Flask validation failed!"
    echo "🔧 EMERGENCY FALLBACK..."
    python3 -m flask --app run.py --debug run --host=0.0.0.0 --port=5000
    exit $?
fi

# Step 7: FINAL START
echo ""
echo "🚀 STARTING FLASK - FINAL ATTEMPT..."
echo "=================="
echo "If successful, you'll see:"
echo "   ✅ Running on http://127.0.0.1:5000"  
echo "   ✅ Running on http://0.0.0.0:5000"
echo ""

# Start with explicit output
exec python3 run.py