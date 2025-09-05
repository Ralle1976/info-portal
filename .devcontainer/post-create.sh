#!/bin/bash
set -e

echo "🚀 Starting QR-Info-Portal Development Environment Setup..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Change to workspace directory
cd /workspaces/qr-info-portal

echo -e "${BLUE}📦 Setting up Python virtual environment...${NC}"
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

echo -e "${BLUE}📋 Installing Python dependencies...${NC}"
# Install requirements
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo -e "${BLUE}🔧 Setting up development tools...${NC}"
# Install additional development tools
pip install flask-shell-ipython ipython

echo -e "${BLUE}🗄️ Setting up database...${NC}"
# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h postgres -p 5432 -U postgres; do
  sleep 1
done

# Initialize database
echo -e "${GREEN}Creating database schema...${NC}"
python -c "
from app import create_app
from app.database import init_db
app = create_app()
with app.app_context():
    init_db()
print('✅ Database initialized successfully!')
"

echo -e "${BLUE}🔐 Setting up environment files...${NC}"
# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env 2>/dev/null || cat > .env << EOF
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Security
SECRET_KEY=dev-secret-key-change-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/qr_portal_dev
SQLITE_DATABASE_URL=sqlite:///data/portal.db

# Redis
REDIS_URL=redis://redis:6379/0

# Site Configuration
SITE_URL=http://localhost:5000
SITE_NAME=Labor Pattaya

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Features
FEATURE_KIOSK_SPLIT=true
FEATURE_ANALYTICS=true
FEATURE_BOOKING=false
EOF
    echo -e "${GREEN}✅ Created .env file${NC}"
fi

echo -e "${BLUE}🛡️ Setting up security tools...${NC}"
# Initialize pre-commit hooks
pre-commit install

# Create pre-commit config if it doesn't exist
if [ ! -f .pre-commit-config.yaml ]; then
    cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ["-r", "app/", "-ll"]
        exclude: ^tests/

  - repo: https://github.com/Lucas-C/pre-commit-hooks-safety
    rev: v1.3.2
    hooks:
      - id: python-safety-dependencies-check
EOF
fi

echo -e "${BLUE}📁 Setting up directories...${NC}"
# Create necessary directories
mkdir -p logs data screenshots visual_tests browser_screenshots
mkdir -p app/static/qr
touch logs/.gitkeep data/.gitkeep screenshots/.gitkeep

echo -e "${BLUE}🧪 Running initial tests...${NC}"
# Run basic tests to verify setup
python -m pytest tests/ -v --tb=short || echo "⚠️ Some tests failed - this is normal for initial setup"

echo -e "${BLUE}📊 Setting up monitoring...${NC}"
# Create simple health check
python -c "
import requests
import time
import sys
# Basic connectivity tests
try:
    # Test Redis
    import redis
    r = redis.from_url('redis://redis:6379/0')
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'⚠️ Redis connection failed: {e}')

try:
    # Test PostgreSQL
    import psycopg2
    conn = psycopg2.connect('postgresql://postgres:postgres@postgres:5432/qr_portal_dev')
    conn.close()
    print('✅ PostgreSQL connection successful')
except Exception as e:
    print(f'⚠️ PostgreSQL connection failed: {e}')
"

echo -e "${BLUE}🎨 Setting up CSS/JS tools...${NC}"
# Install basic frontend tools if needed
npm install -g live-server

echo -e "${GREEN}✅ Development environment setup complete!${NC}"
echo ""
echo -e "${YELLOW}🚀 Quick Start Commands:${NC}"
echo "  • Start Flask:     source .venv/bin/activate && python run.py"
echo "  • Run Tests:       source .venv/bin/activate && pytest"
echo "  • Security Check:  source .venv/bin/activate && bandit -r app/"
echo "  • Code Format:     source .venv/bin/activate && black app/ && isort app/"
echo ""
echo -e "${YELLOW}📡 Available Services:${NC}"
echo "  • Flask App:       http://localhost:5000"
echo "  • PostgreSQL:      localhost:5432 (postgres/postgres)"
echo "  • Redis:           localhost:6379"
echo "  • Live Server:     http://localhost:3000"
echo ""
echo -e "${YELLOW}🔧 Multi-Agent Sessions:${NC}"
echo "  Terminal 1: Flask Development (flask-dev profile)"
echo "  Terminal 2: Testing (testing profile)"
echo "  Terminal 3: General development (zsh)"
echo ""
echo -e "${GREEN}Happy coding! 🎉${NC}"