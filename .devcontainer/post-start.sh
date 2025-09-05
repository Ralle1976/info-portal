#!/bin/bash
set -e

echo "🔄 Starting QR-Info-Portal services..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Change to workspace directory
cd /workspaces/qr-info-portal

# Activate virtual environment
source .venv/bin/activate

echo -e "${BLUE}🏥 Health check: Services...${NC}"
# Wait for services to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h postgres -p 5432 -U postgres -q; do
  sleep 1
done
echo "✅ PostgreSQL ready"

echo "Waiting for Redis..."
until redis-cli -h redis ping &>/dev/null; do
  sleep 1
done
echo "✅ Redis ready"

echo -e "${BLUE}🗄️ Database migration check...${NC}"
# Run any pending migrations
python -c "
from app import create_app
from app.database import init_db
app = create_app()
with app.app_context():
    try:
        init_db()
        print('✅ Database schema up to date')
    except Exception as e:
        print(f'⚠️ Database migration issue: {e}')
"

echo -e "${BLUE}🔑 Checking configuration...${NC}"
# Validate configuration
python -c "
try:
    from app.services.config_service import ConfigService
    config = ConfigService()
    print('✅ Configuration loaded successfully')
    print(f'   Site: {config.get_site_config().get(\"name\", \"QR-Info-Portal\")}')
    print(f'   Languages: {config.get_site_config().get(\"languages\", [\"de\"])}')
except Exception as e:
    print(f'⚠️ Configuration issue: {e}')
"

echo -e "${BLUE}📊 System status...${NC}"
# Show system info
echo "Python version: $(python --version)"
echo "Flask environment: $FLASK_ENV"
echo "Working directory: $(pwd)"
echo "Available disk space:"
df -h /workspace | tail -1

echo -e "${YELLOW}🌐 Network Information:${NC}"
# Show network info for LAN access
LOCAL_IP=$(hostname -I | awk '{print $1}' | head -n1)
echo "Container IP: $LOCAL_IP"
echo "Access URLs:"
echo "  • Local:     http://localhost:5000"
echo "  • LAN:       http://$LOCAL_IP:5000 (if port forwarded)"

echo -e "${BLUE}🧹 Cleanup temporary files...${NC}"
# Clean up any temporary files
find /workspace -name "*.pyc" -delete 2>/dev/null || true
find /workspace -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo -e "${GREEN}✅ All services ready for development!${NC}"
echo ""
echo -e "${YELLOW}Quick Commands:${NC}"
echo "  • flask run --host 0.0.0.0 --port 5000 --debug"
echo "  • pytest -v"
echo "  • black app/ && isort app/"
echo "  • bandit -r app/"
echo ""
echo -e "${YELLOW}Multi-Agent Development:${NC}"
echo "  Open multiple VS Code terminals for parallel development"
echo "  Terminal profiles available: flask-dev, testing, zsh"