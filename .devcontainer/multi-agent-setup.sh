#!/bin/bash
# Multi-Agent Development Environment Setup
# This script configures multiple development sessions for collaborative work

set -e

echo "🤖 Setting up Multi-Agent Development Environment..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Create session management directory
mkdir -p /workspace/.sessions

echo -e "${BLUE}🔧 Configuring tmux for multi-agent sessions...${NC}"
# Create tmux configuration
cat > /workspace/.tmux.conf << 'EOF'
# Multi-Agent Development tmux configuration
set -g default-terminal "screen-256color"
set -g mouse on
set -g history-limit 10000

# Key bindings
bind r source-file ~/.tmux.conf \; display "Config reloaded!"
bind | split-window -h
bind - split-window -v

# Status bar
set -g status-bg colour235
set -g status-fg white
set -g status-left '#[fg=green][#S] '
set -g status-right '#[fg=yellow]%Y-%m-%d %H:%M'

# Window list colors
setw -g window-status-current-style fg=black,bg=green
EOF

echo -e "${PURPLE}🚀 Creating agent session scripts...${NC}"

# Flask Development Agent Session
cat > /workspace/.sessions/flask-agent.sh << 'EOF'
#!/bin/bash
echo "🌶️ Starting Flask Development Agent Session..."
cd /workspaces/qr-info-portal
source .venv/bin/activate
export FLASK_ENV=development
export FLASK_DEBUG=1
export AGENT_ROLE=FLASK_DEVELOPER

echo "Flask Development Agent Ready!"
echo "Commands:"
echo "  • run          - Start Flask server"
echo "  • test         - Run tests"  
echo "  • format       - Format code"
echo "  • debug        - Start with debugger"

# Custom commands
alias run='python run.py'
alias test='pytest tests/ -v'
alias format='black app/ tests/ && isort app/ tests/'
alias debug='python -m pdb run.py'

exec bash
EOF

# Testing Agent Session  
cat > /workspace/.sessions/testing-agent.sh << 'EOF'
#!/bin/bash
echo "🧪 Starting Testing Agent Session..."
cd /workspaces/qr-info-portal
source .venv/bin/activate
export AGENT_ROLE=QA_TESTER

echo "Testing Agent Ready!"
echo "Commands:"
echo "  • test-all     - Run full test suite"
echo "  • test-quick   - Run quick tests"
echo "  • coverage     - Generate coverage report" 
echo "  • security     - Run security scans"

# Custom commands
alias test-all='pytest tests/ -v --cov=app --cov-report=html --cov-report=term'
alias test-quick='pytest tests/ -v -x --tb=line'
alias coverage='pytest tests/ --cov=app --cov-report=html && open htmlcov/index.html'
alias security='bandit -r app/ -ll && safety check'

exec bash
EOF

# Security Agent Session
cat > /workspace/.sessions/security-agent.sh << 'EOF'
#!/bin/bash
echo "🛡️ Starting Security Agent Session..."
cd /workspaces/qr-info-portal
source .venv/bin/activate
export AGENT_ROLE=SECURITY_ANALYST

echo "Security Agent Ready!"
echo "Commands:"
echo "  • scan         - Run security scan"
echo "  • deps         - Check dependencies"
echo "  • secrets      - Scan for secrets"
echo "  • audit        - Full security audit"

# Custom commands  
alias scan='bandit -r app/ -f json -o security_report.json && bandit -r app/ -ll'
alias deps='safety check --json --output safety_report.json && safety check'
alias secrets='detect-secrets scan --baseline .secrets.baseline'
alias audit='scan && deps && secrets'

exec bash
EOF

# Database Agent Session
cat > /workspace/.sessions/database-agent.sh << 'EOF' 
#!/bin/bash
echo "🗄️ Starting Database Agent Session..."
cd /workspaces/qr-info-portal
source .venv/bin/activate
export AGENT_ROLE=DATABASE_DEVELOPER

echo "Database Agent Ready!"
echo "Commands:"
echo "  • migrate      - Run migrations"
echo "  • reset        - Reset database"
echo "  • backup       - Backup database"
echo "  • psql         - Connect to PostgreSQL"

# Custom commands
alias migrate='python -c "from app.database import init_db; init_db()"'
alias reset='python -c "from app.database import reset_db, init_db; reset_db(); init_db()"'
alias backup='pg_dump -h postgres -U postgres qr_portal_dev > backup_$(date +%Y%m%d_%H%M%S).sql'
alias psql='psql -h postgres -U postgres -d qr_portal_dev'

exec bash
EOF

# Frontend Agent Session  
cat > /workspace/.sessions/frontend-agent.sh << 'EOF'
#!/bin/bash
echo "🎨 Starting Frontend Agent Session..."
cd /workspaces/qr-info-portal
source .venv/bin/activate
export AGENT_ROLE=FRONTEND_DEVELOPER

echo "Frontend Agent Ready!"
echo "Commands:"
echo "  • serve        - Start live server"
echo "  • validate     - Validate HTML"
echo "  • optimize     - Optimize assets"
echo "  • screenshots  - Generate screenshots"

# Custom commands
alias serve='live-server --port=3000 --host=0.0.0.0'
alias validate='python -c "from app.services.i18n import validate_templates; validate_templates()"'
alias optimize='echo "TODO: Implement asset optimization"'
alias screenshots='python browser_screenshot_service.py'

exec bash
EOF

# Make scripts executable
chmod +x /workspace/.sessions/*.sh

echo -e "${YELLOW}📋 Creating agent coordination script...${NC}"

# Agent coordination script
cat > /workspace/.sessions/start-agents.sh << 'EOF'
#!/bin/bash
echo "🤖 Starting Multi-Agent Development Environment..."

# Check if tmux is available
if ! command -v tmux &> /dev/null; then
    echo "Installing tmux..."
    sudo apt-get update && sudo apt-get install -y tmux
fi

# Kill existing session if it exists
tmux kill-session -t qr-portal-dev 2>/dev/null || true

# Create new session
tmux new-session -d -s qr-portal-dev -n main

# Create windows for each agent
tmux new-window -t qr-portal-dev -n flask 'bash /workspace/.sessions/flask-agent.sh'
tmux new-window -t qr-portal-dev -n testing 'bash /workspace/.sessions/testing-agent.sh' 
tmux new-window -t qr-portal-dev -n security 'bash /workspace/.sessions/security-agent.sh'
tmux new-window -t qr-portal-dev -n database 'bash /workspace/.sessions/database-agent.sh'
tmux new-window -t qr-portal-dev -n frontend 'bash /workspace/.sessions/frontend-agent.sh'

# Select flask window as default
tmux select-window -t qr-portal-dev:flask

echo "🎉 Multi-Agent Environment Ready!"
echo ""
echo "Available agent sessions:"
echo "  • Flask Development  (window: flask)"
echo "  • Testing & QA       (window: testing)"
echo "  • Security Analysis  (window: security)"  
echo "  • Database Dev       (window: database)"
echo "  • Frontend Dev       (window: frontend)"
echo ""
echo "To attach: tmux attach-session -t qr-portal-dev"
echo "To switch windows: Ctrl+B then 1-5"
echo "To detach: Ctrl+B then d"
EOF

chmod +x /workspace/.sessions/start-agents.sh

echo -e "${GREEN}✅ Multi-Agent Environment configured!${NC}"
echo ""
echo -e "${YELLOW}🚀 Quick Start:${NC}"
echo "  bash .sessions/start-agents.sh"
echo ""
echo -e "${YELLOW}📖 Agent Roles:${NC}"
echo "  🌶️ Flask Agent:     Main development, routing, services"
echo "  🧪 Testing Agent:   Unit tests, integration tests, QA" 
echo "  🛡️ Security Agent:  Security scans, vulnerability checks"
echo "  🗄️ Database Agent:  Schema changes, migrations, data"
echo "  🎨 Frontend Agent:  Templates, styling, UX/UI"