#!/usr/bin/env python3
"""
🚀 CODESPACE-OPTIMIZED FLASK STARTUP
Spezielle Version für GitHub Codespace Environment
"""

import os
import sys
import signal
import logging
from pathlib import Path

def setup_codespace_environment():
    """Setup environment variables specifically for Codespace"""
    # Force environment variables
    os.environ['FLASK_APP'] = 'run.py'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    os.environ['FLASK_HOST'] = '0.0.0.0'
    os.environ['FLASK_PORT'] = '5000'
    
    # Set SECRET_KEY if not present
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'codespace-dev-secret-key-emergency'
    
    # Ensure database directory
    Path('data').mkdir(exist_ok=True)
    Path('logs').mkdir(exist_ok=True)
    
    # Add current directory to Python path
    current_dir = str(Path.cwd())
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

def signal_handler(sig, frame):
    print('\n🛑 Graceful shutdown requested...')
    sys.exit(0)

def main():
    """Main Flask startup function"""
    print("🚀 QR-Info-Portal Codespace Startup")
    print("====================================")
    
    # Setup environment
    setup_codespace_environment()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configure basic logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Import after environment setup
        from app import create_app
        
        print("📦 Creating Flask application...")
        app = create_app()
        
        # Get configuration
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_ENV') == 'development'
        
        # Route count validation
        route_count = len(app.url_map._rules)
        print(f"🔍 Registered routes: {route_count}")
        
        if route_count < 50:
            print("⚠️  WARNING: Low route count detected!")
        else:
            print("✅ Route registration successful")
        
        # Show some example routes
        print("📍 Available endpoints:")
        routes = list(app.url_map.iter_rules())[:8]
        for rule in routes:
            print(f"   {rule.rule} -> {rule.endpoint}")
        
        print(f"\n🌐 Starting server on http://{host}:{port}")
        print(f"🌐 Codespace URL: https://<CODESPACE-NAME>-{port}.app.github.dev/")
        print("🔧 Press CTRL+C to quit")
        print("")
        
        # Start Flask
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False,  # Disable reloader in Codespace
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ CRITICAL: Import error - {e}")
        print("🔧 Trying fallback import method...")
        
        # Fallback: try direct module import
        sys.path.append(os.getcwd())
        try:
            import app
            flask_app = app.create_app()
            flask_app.run(host='0.0.0.0', port=5000, debug=True)
        except Exception as fallback_error:
            print(f"❌ FALLBACK FAILED: {fallback_error}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ STARTUP ERROR: {e}")
        print("🔧 Environment debug info:")
        print(f"   Python version: {sys.version}")
        print(f"   Working directory: {os.getcwd()}")
        print(f"   Python path: {sys.path[:3]}...")  # First 3 entries
        print(f"   FLASK_APP: {os.environ.get('FLASK_APP', 'NOT SET')}")
        print(f"   SECRET_KEY: {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}")
        sys.exit(1)

if __name__ == '__main__':
    main()