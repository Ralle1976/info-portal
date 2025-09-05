# 🚀 Deployment Guide - QR Info Portal

Umfassende Anleitung für das Deployment des QR Info Portals in verschiedenen Umgebungen - von lokaler Entwicklung bis zur produktiven Cloud-Infrastruktur.

## 📋 Inhaltsverzeichnis

1. [Deployment-Optionen](#deployment-optionen)
2. [Docker Deployment](#docker-deployment)
3. [Cloud-Deployment](#cloud-deployment)
4. [Reverse Proxy Setup](#reverse-proxy-setup)
5. [SSL/HTTPS Konfiguration](#ssl-https-konfiguration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)
8. [Performance Optimierung](#performance-optimierung)

---

## 🎯 Deployment-Optionen

### Übersicht der Optionen

| Option | Komplexität | Kosten | Skalierbarkeit | Wartung |
|--------|-------------|---------|---------------|---------|
| **Lokales LAN** | 🟢 Niedrig | 🟢 Kostenlos | 🟡 Begrenzt | 🟢 Einfach |
| **Docker Local** | 🟡 Mittel | 🟢 Kostenlos | 🟡 Mittel | 🟡 Mittel |
| **VPS/Cloud** | 🟡 Mittel | 🟡 Niedrig | 🟢 Hoch | 🟡 Mittel |
| **Container-Platform** | 🔴 Hoch | 🟡 Mittel | 🟢 Sehr hoch | 🟢 Automatisch |

### Empfehlungen nach Anwendungsfall

#### 🏠 **Lokaler Betrieb (Klinik/Praxis)**
- **Setup**: Flask Development Server
- **Zugriff**: LAN-IP + Port 5000
- **Ideal für**: Einzelstandort, wenige Benutzer
- **Vorteile**: Einfach, schnell, kostenlos

#### 🏢 **Kleine Unternehmen**
- **Setup**: Docker + Nginx
- **Zugriff**: eigene Domain
- **Ideal für**: Mehrere Standorte, externe Zugriffe
- **Vorteile**: Professionell, skalierbar

#### 🌐 **Große Organisationen**
- **Setup**: Kubernetes/Cloud
- **Zugriff**: Load Balancer + CDN
- **Ideal für**: Viele Standorte, hohe Verfügbarkeit
- **Vorteile**: Enterprise-ready, hoch verfügbar

---

## 🐳 Docker Deployment

### Grundlegendes Docker Setup

#### 1. Dockerfile (bereits vorhanden)
```dockerfile
FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/healthz || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

#### 2. Docker Build & Run
```bash
# Image erstellen
docker build -t qr-info-portal:latest .

# Container starten
docker run -d \
    --name qr-portal \
    -p 5000:5000 \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/config.yml:/app/config.yml \
    --env-file .env \
    qr-info-portal:latest

# Logs anzeigen
docker logs -f qr-portal

# Container stoppen
docker stop qr-portal
docker rm qr-portal
```

### Docker Compose (Empfohlen)

#### docker-compose.yml
```yaml
version: '3.8'

services:
  # Hauptanwendung
  qr-portal:
    build: .
    container_name: qr-info-portal
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=sqlite:///data/portal.db
    volumes:
      - ./data:/app/data
      - ./config.yml:/app/config.yml
      - ./logs:/app/logs
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - qr-portal-network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: qr-portal-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./ssl:/etc/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - qr-portal
    networks:
      - qr-portal-network

  # PostgreSQL (optional, für größere Installationen)
  postgres:
    image: postgres:15-alpine
    container_name: qr-portal-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=qr_portal
      - POSTGRES_USER=portal_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - qr-portal-network

  # Redis (für Session-Speicherung)
  redis:
    image: redis:7-alpine
    container_name: qr-portal-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - qr-portal-network

networks:
  qr-portal-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

#### Docker Compose Befehle
```bash
# Alle Services starten
docker-compose up -d

# Logs aller Services
docker-compose logs -f

# Nur App-Logs
docker-compose logs -f qr-portal

# Services neustarten
docker-compose restart

# Alles stoppen und entfernen
docker-compose down

# Mit Volume-Entfernung (⚠️ Datenverlust!)
docker-compose down -v

# Services aktualisieren
docker-compose pull
docker-compose up -d
```

### Production Docker Setup

#### Multi-Stage Dockerfile (Optimiert)
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels and install
COPY --from=builder /app/wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy application
COPY . .

# Create data directory and set permissions
RUN mkdir -p data logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/healthz || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "30", "app:app"]
```

---

## ☁️ Cloud-Deployment

### DigitalOcean App Platform

#### app.yaml
```yaml
name: qr-info-portal
services:
- name: web
  source_dir: /
  github:
    repo: your-username/qr-info-portal
    branch: main
  run_command: gunicorn --bind 0.0.0.0:8080 --workers 2 app:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
  health_check:
    http_path: /healthz
  envs:
  - key: FLASK_ENV
    value: production
  - key: SECRET_KEY
    value: your-secret-key
  - key: SITE_URL
    value: https://your-app.ondigitalocean.app

databases:
- name: qr-portal-db
  engine: PG
  num_nodes: 1
  size: db-s-dev-database
```

### Heroku Deployment

#### Procfile
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app
release: python -c "from app.database import init_database; init_database()"
```

#### heroku.yml
```yaml
build:
  docker:
    web: Dockerfile
run:
  web: gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app
```

#### Heroku CLI Befehle
```bash
# App erstellen
heroku create qr-info-portal

# Environment Variables setzen
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key

# PostgreSQL hinzufügen
heroku addons:create heroku-postgresql:hobby-dev

# Deployment
git push heroku main

# Logs anzeigen
heroku logs --tail

# App skalieren
heroku ps:scale web=2
```

### AWS Elastic Beanstalk

#### .ebextensions/01-packages.config
```yaml
packages:
  yum:
    git: []
    postgresql-devel: []
```

#### .ebextensions/02-python.config
```yaml
container_commands:
  01_migrate:
    command: "python -c 'from app.database import init_database; init_database()'"
    leader_only: true
```

#### Dockerrun.aws.json
```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "your-account.dkr.ecr.region.amazonaws.com/qr-info-portal:latest"
  },
  "Ports": [
    {
      "ContainerPort": "5000"
    }
  ]
}
```

### Google Cloud Run

#### cloudbuild.yaml
```yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/qr-info-portal', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/qr-info-portal']
- name: 'gcr.io/cloud-builders/gcloud'
  args: 
  - 'run'
  - 'deploy'
  - 'qr-info-portal'
  - '--image'
  - 'gcr.io/$PROJECT_ID/qr-info-portal'
  - '--region'
  - 'us-central1'
  - '--platform'
  - 'managed'
```

---

## 🔄 Reverse Proxy Setup

### Nginx Konfiguration

#### nginx/nginx.conf
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=admin:10m rate=5r/s;

    # Upstream
    upstream qr_portal {
        server qr-portal:5000;
        keepalive 32;
    }

    include /etc/nginx/conf.d/*.conf;
}
```

#### nginx/conf.d/default.conf
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/your-domain.com.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Main location
    location / {
        proxy_pass http://qr_portal;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Static files caching
    location /static/ {
        proxy_pass http://qr_portal;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # QR codes caching
    location /qr {
        proxy_pass http://qr_portal;
        expires 1d;
        add_header Cache-Control "public";
    }

    # Admin with rate limiting
    location /admin/ {
        limit_req zone=admin burst=10 nodelay;
        proxy_pass http://qr_portal;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API with rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://qr_portal;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /healthz {
        proxy_pass http://qr_portal;
        access_log off;
    }
}
```

### Apache Setup (Alternative)

#### apache/sites-available/qr-portal.conf
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    ServerAlias www.your-domain.com
    Redirect permanent / https://your-domain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName your-domain.com
    ServerAlias www.your-domain.com

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/your-domain.com.crt
    SSLCertificateKeyFile /etc/ssl/private/your-domain.com.key
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384

    # Proxy Configuration
    ProxyPreserveHost On
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/

    # Headers
    ProxyPassReverse / http://localhost:5000/
    ProxySetHeader Host $host
    ProxySetHeader X-Real-IP $remote_addr
    ProxySetHeader X-Forwarded-For $proxy_add_x_forwarded_for
    ProxySetHeader X-Forwarded-Proto $scheme

    # Logging
    ErrorLog ${APACHE_LOG_DIR}/qr-portal_error.log
    CustomLog ${APACHE_LOG_DIR}/qr-portal_access.log combined
</VirtualHost>
```

---

## 🔒 SSL/HTTPS Konfiguration

### Let's Encrypt mit Certbot

#### Automatische SSL-Einrichtung
```bash
# Certbot installieren (Ubuntu/Debian)
sudo apt update
sudo apt install certbot python3-certbot-nginx

# SSL-Zertifikat für Nginx erstellen
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Automatische Erneuerung testen
sudo certbot renew --dry-run

# Cronjob für automatische Erneuerung
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

#### Docker mit Let's Encrypt
```yaml
# In docker-compose.yml hinzufügen
services:
  certbot:
    image: certbot/certbot
    container_name: qr-portal-certbot
    volumes:
      - ./ssl:/etc/letsencrypt
      - ./ssl-webroot:/var/www/certbot
    command: certonly --webroot --webroot-path=/var/www/certbot --email your-email@domain.com --agree-tos --no-eff-email -d your-domain.com
```

### Cloudflare SSL

#### Cloudflare-Konfiguration
```nginx
# Nginx für Cloudflare optimiert
server {
    listen 80;
    server_name your-domain.com;

    # Cloudflare Real IP
    set_real_ip_from 103.21.244.0/22;
    set_real_ip_from 103.22.200.0/22;
    set_real_ip_from 103.31.4.0/22;
    real_ip_header CF-Connecting-IP;

    location / {
        proxy_pass http://qr_portal;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📊 Monitoring & Logging

### Logging-Konfiguration

#### app/logging_config.py
```python
import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/portal.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Add handlers
    app_logger = logging.getLogger('qr_portal')
    app_logger.addHandler(file_handler)
    app_logger.setLevel(logging.INFO)
    
    return app_logger
```

### Prometheus Metrics

#### requirements-monitoring.txt
```
prometheus-client==0.18.0
flask-prometheus-metrics==1.0.0
```

#### app/monitoring.py
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Response
import time

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_USERS = Gauge('active_users_total', 'Number of active users')

def setup_metrics(app):
    @app.before_request
    def before_request():
        request.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown'
        ).inc()
        
        if hasattr(request, 'start_time'):
            REQUEST_DURATION.observe(time.time() - request.start_time)
        
        return response
    
    @app.route('/metrics')
    def metrics():
        return Response(generate_latest(), mimetype='text/plain')
```

### Health Monitoring

#### docker-compose.override.yml (Monitoring)
```yaml
version: '3.8'

services:
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: qr-portal-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - qr-portal-network

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: qr-portal-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - qr-portal-network

volumes:
  prometheus_data:
  grafana_data:
```

---

## 💾 Backup & Recovery

### Automatisches Backup

#### scripts/backup.sh
```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/backups/qr-portal"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Starting backup at $(date)"

# Database backup
if [ -f "data/portal.db" ]; then
    cp data/portal.db "$BACKUP_DIR/database_$DATE.db"
    echo "Database backed up"
fi

# Configuration backup
if [ -f "config.yml" ]; then
    cp config.yml "$BACKUP_DIR/config_$DATE.yml"
    echo "Configuration backed up"
fi

# Environment backup (without secrets)
if [ -f ".env" ]; then
    grep -v "PASSWORD\|SECRET\|KEY" .env > "$BACKUP_DIR/env_$DATE.txt"
    echo "Environment backed up"
fi

# Static files backup
if [ -d "app/static/qr" ]; then
    tar -czf "$BACKUP_DIR/qr_codes_$DATE.tar.gz" app/static/qr/
    echo "QR codes backed up"
fi

# Cleanup old backups
find "$BACKUP_DIR" -name "*.db" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.yml" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.txt" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed at $(date)"
echo "Backup files:"
ls -la "$BACKUP_DIR" | grep "$DATE"
```

#### Docker Backup Script
```bash
#!/bin/bash

# Docker container backup
CONTAINER_NAME="qr-info-portal"
BACKUP_DIR="/backups/docker"
DATE=$(date +%Y%m%d_%H%M%S)

# Create container backup
docker exec $CONTAINER_NAME tar -czf - /app/data | gzip > "$BACKUP_DIR/container_data_$DATE.tar.gz"

# Database dump (if using PostgreSQL)
docker exec qr-portal-db pg_dump -U portal_user qr_portal > "$BACKUP_DIR/postgres_$DATE.sql"

echo "Docker backup completed"
```

### Restore Procedures

#### scripts/restore.sh
```bash
#!/bin/bash

BACKUP_FILE=$1
RESTORE_TYPE=$2

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file> [database|config|full]"
    exit 1
fi

case $RESTORE_TYPE in
    "database")
        echo "Restoring database from $BACKUP_FILE"
        cp "$BACKUP_FILE" data/portal.db
        ;;
    "config")
        echo "Restoring configuration from $BACKUP_FILE"
        cp "$BACKUP_FILE" config.yml
        ;;
    "full")
        echo "Full restore not implemented yet"
        ;;
    *)
        echo "Unknown restore type: $RESTORE_TYPE"
        exit 1
        ;;
esac

echo "Restore completed"
```

---

## ⚡ Performance Optimierung

### Gunicorn-Konfiguration

#### gunicorn.conf.py
```python
# Gunicorn configuration file

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 5

# Restart workers
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "qr-info-portal"

# Server mechanics
preload_app = True
daemon = False
pidfile = "logs/gunicorn.pid"
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None
```

### Caching-Strategien

#### app/cache.py
```python
from functools import wraps
from flask import request, make_response
import hashlib
import time

# Simple in-memory cache
_cache = {}
_cache_timestamps = {}

def cache_response(timeout=300):
    """Cache decorator for views"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create cache key
            cache_key = hashlib.md5(
                f"{request.url}:{request.method}".encode()
            ).hexdigest()
            
            # Check cache
            if cache_key in _cache:
                if time.time() - _cache_timestamps[cache_key] < timeout:
                    response = make_response(_cache[cache_key])
                    response.headers['X-Cache'] = 'HIT'
                    return response
            
            # Generate response
            result = f(*args, **kwargs)
            
            # Store in cache
            _cache[cache_key] = result
            _cache_timestamps[cache_key] = time.time()
            
            if hasattr(result, 'headers'):
                result.headers['X-Cache'] = 'MISS'
            
            return result
        return decorated_function
    return decorator

# Usage in routes
@cache_response(timeout=600)  # 10 minutes
@public_bp.route('/api/status')
def get_status():
    return jsonify(StatusService.get_current_status())
```

### Database Optimierung

#### SQLite Optimierungen
```python
# In app/database.py
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        # Performance optimizations
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
        cursor.close()
```

---

## 🚨 Troubleshooting

### Häufige Deployment-Probleme

#### 1. Port-Konflikte
```bash
# Port prüfen
sudo netstat -tlnp | grep :5000
sudo lsof -i :5000

# Docker port mapping prüfen
docker ps
docker port qr-portal
```

#### 2. Permission Issues
```bash
# Docker permissions
sudo chown -R $USER:$USER data/
chmod 755 data/

# SELinux (CentOS/RHEL)
sudo setsebool -P httpd_can_network_connect 1
sudo semanage port -a -t http_port_t -p tcp 5000
```

#### 3. SSL-Probleme
```bash
# SSL-Zertifikat prüfen
openssl x509 -in /etc/ssl/certs/your-domain.com.crt -text -noout

# SSL-Test
curl -I https://your-domain.com
ssl-cert-check -c /etc/ssl/certs/your-domain.com.crt
```

### Monitoring-Commands

#### System-Monitoring
```bash
# Docker stats
docker stats qr-portal

# Nginx status
docker exec qr-portal-nginx nginx -t
docker logs qr-portal-nginx

# Application logs
docker logs -f qr-portal --tail 100

# Database size
du -sh data/portal.db
```

#### Performance-Tests
```bash
# Load testing mit Apache Bench
ab -n 1000 -c 10 http://your-domain.com/

# Curl response time
curl -w "@curl-format.txt" -o /dev/null -s http://your-domain.com/

# Where curl-format.txt contains:
# time_namelookup:  %{time_namelookup}\n
# time_connect:     %{time_connect}\n
# time_appconnect:  %{time_appconnect}\n
# time_pretransfer: %{time_pretransfer}\n
# time_redirect:    %{time_redirect}\n
# time_starttransfer: %{time_starttransfer}\n
# time_total:       %{time_total}\n
```

---

**🎉 Deployment erfolgreich! Das QR Info Portal ist jetzt produktionsbereit.**

Für weitere Hilfe siehe:
- **[SETUP.md](SETUP.md)** - Grundlegende Installation
- **[README.md](README.md)** - Projekt-Übersicht
- **[API.md](API.md)** - API-Dokumentation