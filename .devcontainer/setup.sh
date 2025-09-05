#!/bin/bash

# QR Info Portal - GitHub Codespace Setup Script
echo "🚀 Setting up QR Info Portal Development Environment..."

# Update system packages
sudo apt-get update -y

# Install system dependencies
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-venv \
    python3-pip \
    sqlite3 \
    libsqlite3-dev \
    git \
    curl \
    wget \
    unzip

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📚 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found, installing basic dependencies..."
    pip install flask flask-httpauth python-dotenv pyyaml qrcode[pil] pillow
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs data static/qr temp

# Set up environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        cat > .env << 'EOF'
# QR Info Portal Configuration
FLASK_APP=app
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
SITE_URL=https://${CODESPACE_NAME}-5000.app.github.dev
DATABASE_PATH=data/qr_portal.db
LOG_LEVEL=INFO

# GitHub Codespace specific
CODESPACE_NAME=${CODESPACE_NAME}
GITHUB_CODESPACES=true
EOF
    fi
fi

# Initialize database
echo "🗄️  Initializing database..."
python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app.database import init_database
    init_database()
    print('Database initialized successfully!')
"

# Create default configuration
echo "📝 Creating default configuration..."
if [ ! -f "config.yml" ]; then
    cat > config.yml << 'EOF'
site:
  name: "QR Info Portal - Lab Pattaya"
  languages: ["th", "en", "de"]
  default_language: "th"
  timezone: "Asia/Bangkok"

location:
  address: "Pattaya, Thailand"
  latitude: 12.927608
  longitude: 100.877081
  maps_link: "https://maps.google.com/?q=12.927608,100.877081"

contact:
  phone: "+66 XX XXX XXXX"
  email: "lab@example.com"

services:
  standard:
    - name:
        th: "เจาะเลือด"
        en: "Blood Test"
        de: "Blutabnahme"
    - name:
        th: "ปรึกษาแพทย์"
        en: "Medical Consultation"
        de: "Ärztliche Beratung"

status:
  current:
    type: "ANWESEND"
    from: null
    to: null
    note: null

hours:
  weekly:
    monday: ["08:30-12:00", "13:00-16:00"]
    tuesday: ["08:30-12:00", "13:00-16:00"]
    wednesday: ["08:30-12:00"]
    thursday: ["08:30-12:00", "13:00-16:00"]
    friday: ["08:30-13:00"]
    saturday: []
    sunday: []
  exceptions: []

availability:
  indicative_slots: []

announcements: []

admin:
  username: "admin"
  password_env: "ADMIN_PASSWORD"
EOF
fi

# Make script executable
chmod +x setup.sh

# Create run script for easy development
cat > run_dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting QR Info Portal Development Server..."
source .venv/bin/activate
export FLASK_APP=app
export FLASK_ENV=development
export FLASK_DEBUG=true

if [ -n "$CODESPACE_NAME" ]; then
    export SITE_URL="https://${CODESPACE_NAME}-5000.app.github.dev"
    echo "📡 Codespace URL: $SITE_URL"
fi

python -m flask run --host 0.0.0.0 --port 5000
EOF
chmod +x run_dev.sh

# Create quick commands
cat > Makefile << 'EOF'
.PHONY: dev setup test clean logs

dev:
	@echo "🚀 Starting development server..."
	@./run_dev.sh

setup:
	@echo "🔧 Setting up development environment..."
	@./.devcontainer/setup.sh

test:
	@echo "🧪 Running tests..."
	@source .venv/bin/activate && python -m pytest tests/ -v

clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@rm -rf .pytest_cache/

logs:
	@echo "📋 Showing recent logs..."
	@tail -f logs/*.log

install:
	@echo "📦 Installing dependencies..."
	@source .venv/bin/activate && pip install -r requirements.txt

update-deps:
	@echo "🔄 Updating dependencies..."
	@source .venv/bin/activate && pip install --upgrade -r requirements.txt

migrate:
	@echo "🗄️  Running database migrations..."
	@source .venv/bin/activate && python -c "from app.database import init_database; init_database()"

qr:
	@echo "📱 Generating QR codes..."
	@source .venv/bin/activate && python -c "from app.services.qr import QRService; import os; QRService.save_qr_files(os.getenv('SITE_URL', 'http://localhost:5000'))"
EOF

echo ""
echo "✅ GitHub Codespace setup completed!"
echo ""
echo "🎯 Available Commands:"
echo "   make dev        - Start development server"
echo "   make test       - Run tests"
echo "   make logs       - View application logs"
echo "   make qr         - Generate QR codes"
echo ""
echo "🌐 The application will be available at:"
if [ -n "$CODESPACE_NAME" ]; then
    echo "   https://${CODESPACE_NAME}-5000.app.github.dev"
else
    echo "   http://localhost:5000"
fi
echo ""
echo "👤 Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""