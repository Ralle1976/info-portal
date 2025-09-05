# QR-Info-Portal Development Container

Diese .devcontainer Konfiguration stellt eine vollständige, sofort einsatzbereite Entwicklungsumgebung für das QR-Info-Portal bereit.

## 🚀 Schnellstart

1. **VS Code öffnen** mit der Remote-Containers Extension
2. **Command Palette** (`Ctrl+Shift+P`) → "Dev Containers: Reopen in Container"  
3. **Warten** bis alle Services gestartet sind (ca. 2-3 Minuten)
4. **Flask starten**: Terminal öffnen → `python run.py`

## 🛠️ Enthaltene Services

- **Python 3.11** mit allen Dependencies
- **PostgreSQL 15** (Development Database)
- **Redis 7** (Caching & Sessions)
- **Nginx** (optional, für Production-Testing)
- **Mailhog** (optional, für E-Mail Testing)

## 🔧 Konfigurierte Tools

### Code Quality & Security
- **Black** (Code Formatting)
- **isort** (Import Sorting)  
- **Flake8** (Linting)
- **MyPy** (Type Checking)
- **Bandit** (Security Scanner)
- **Safety** (Dependency Security)
- **Pre-commit Hooks** (automatische Checks)

### Development & Debugging
- **Flask Debugger** konfiguriert
- **Pytest** für Testing
- **SQLTools** für Database Management
- **Thunder Client** für API Testing

### Multi-Agent Development
- **4 vorkonfigurierte Terminal Profile**:
  - `flask-dev`: Flask Development
  - `testing`: Testing & QA
  - `security`: Security Analysis
  - `zsh`: General Development

## 📋 Verfügbare Tasks (VS Code Command Palette)

- **🚀 Start Flask Development Server**
- **🧪 Run All Tests**
- **🛡️ Security Scan (Bandit)**
- **🔍 Dependency Security Check**
- **🎨 Format Code (Black + isort)**
- **🐳 Build Docker Image**
- **🔄 Full CI Pipeline**

## 🤖 Multi-Agent Environment

Für parallele Entwicklung mit mehreren Agents:

```bash
# Start multi-agent tmux session
bash .devcontainer/multi-agent-setup.sh

# Oder manuelle Terminal Sessions:
# Terminal 1: Flask Development
source .venv/bin/activate && python run.py

# Terminal 2: Testing  
source .venv/bin/activate && pytest --watch

# Terminal 3: Security Analysis
source .venv/bin/activate && bandit -r app/

# Terminal 4: Database
psql -h postgres -U postgres -d qr_portal_dev
```

## 🌐 Zugriff & URLs

- **Flask App**: http://localhost:5000
- **PostgreSQL**: localhost:5432 (postgres/postgres)
- **Redis**: localhost:6379
- **Mailhog UI**: http://localhost:8025
- **Nginx**: http://localhost:80

## 🔑 Standard Login

- **Admin**: `admin` / `admin123` (change in production!)

## 📁 Wichtige Verzeichnisse

- `/workspace/.venv` - Python Virtual Environment
- `/workspace/logs` - Application Logs
- `/workspace/data` - SQLite Database (fallback)  
- `/workspace/screenshots` - Test Screenshots
- `/workspace/.sessions` - Multi-Agent Session Scripts

## 🚨 Wichtige Hinweise

1. **Automatisches Setup**: Alle Dependencies werden beim ersten Start automatisch installiert
2. **Database Migration**: Läuft automatisch beim Container Start
3. **Pre-commit Hooks**: Sind automatisch konfiguriert
4. **Security Scans**: Laufen bei jedem Commit
5. **Hot Reload**: Flask läuft mit Debug-Modus und Auto-Reload

## 🔧 Fehlerbehebung

### Container startet nicht
```bash
# Container neu bauen
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Dependencies fehlen
```bash
# Innerhalb des Containers
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Database Probleme
```bash
# Database Reset
python -c "from app.database import reset_db, init_db; reset_db(); init_db()"
```

### Port Konflikte
Ports in `.devcontainer/docker-compose.yml` ändern:
- Flask: 5000 → 5001
- PostgreSQL: 5432 → 5433  
- Redis: 6379 → 6380

## 📊 Performance

Der Container ist optimiert für:
- **Schnelle Starts** (Layer Caching)
- **Hot Reload** (Volume Mounts)
- **Parallele Entwicklung** (Multi-Agent Support)
- **Security First** (alle Scans konfiguriert)

Erwartete Startzeit: 2-3 Minuten beim ersten Start, 30-60 Sekunden bei Restarts.