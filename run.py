#!/usr/bin/env python3
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"Starting QR-Info-Portal on http://{host}:{port}")
    print("Access from LAN: http://<YOUR-LAN-IP>:5000")
    
    app.run(host=host, port=port, debug=debug)