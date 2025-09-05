#!/bin/bash
# 🚀 ONE-LINER CODESPACE FIX 
pkill -f "python.*flask" 2>/dev/null || true && sleep 2 && cp .env.codespace .env && source .env && export FLASK_APP=run.py FLASK_ENV=development FLASK_DEBUG=1 PYTHONPATH=$(pwd) && mkdir -p data logs && python3 run.py