# GitHub Configuration & Workflows

Dieses Verzeichnis enthält alle GitHub-spezifischen Konfigurationsdateien, Workflows und Automatisierungen für das QR Info Portal Projekt.

## 📁 Verzeichnisstruktur

```
.github/
├── workflows/              # GitHub Actions Workflows
│   ├── ci.yml             # Continuous Integration Pipeline
│   ├── security-scan.yml  # Erweiterte Sicherheitsscans
│   ├── codeql-analysis.yml # GitHub CodeQL Analyse
│   ├── security-monitoring.yml # Tägliche Sicherheitsüberwachung
│   ├── pr-quality-gates.yml # PR Quality Gates & Checks
│   ├── dependency-updates.yml # Automatisierte Dependency Updates
│   ├── deployment.yml     # Deployment zu Staging/Production
│   ├── release.yml        # Release Management
│   └── update-actions.yml # GitHub Actions Updates
├── ISSUE_TEMPLATE/         # Issue Templates
│   ├── bug_report.yml     # Bug Report Template
│   ├── feature_request.yml # Feature Request Template
│   └── security_report.yml # Security Vulnerability Report
├── SECURITY.md            # Security Policy & Guidelines
├── dependabot.yml         # Dependabot Konfiguration
├── codeql-config.yml      # CodeQL Analyse Konfiguration
├── setup-repository-security.py # Repository Security Setup
└── setup-complete-repository.sh # Komplette Repository Einrichtung
```

## 🔄 GitHub Actions Workflows

### Core CI/CD Pipeline

#### `ci.yml` - Continuous Integration
- **Trigger**: Push zu main/develop, Pull Requests
- **Jobs**:
  - Code Quality (Black, isort, Flake8, MyPy)
  - Tests (Python 3.11, 3.12)
  - Security Scan (Bandit, Safety)
  - Docker Build & Test
  - Documentation Build

#### `security-scan.yml` - Erweiterte Sicherheitsscans
- **Trigger**: Push, PR, täglich um 02:00 UTC
- **Jobs**:
  - SAST (Static Application Security Testing)
  - Dependency Vulnerability Scan
  - Docker Security Scan (Trivy)
  - Secrets Detection (GitLeaks, TruffleHog)  
  - DAST (Dynamic Application Security Testing)
  - Compliance Check

#### `codeql-analysis.yml` - GitHub Advanced Security
- **Trigger**: Push, PR, wöchentlich
- **Jobs**:
  - CodeQL Analysis (Python, JavaScript)
  - Custom Security Rules
  - SARIF Upload für Security Tab

#### `security-monitoring.yml` - Kontinuierliche Überwachung
- **Trigger**: Täglich um 06:00 UTC
- **Jobs**:
  - Vulnerability Monitoring
  - SBOM Generation
  - License Compliance Check
  - Infrastructure Security Audit
  - Monatliche Secret Rotation Erinnerungen

### Quality Assurance

#### `pr-quality-gates.yml` - Pull Request Quality Gates
- **Trigger**: PR Events
- **Jobs**:
  - PR Information & Validation
  - Code Quality Checks
  - Security Review
  - Test Coverage Analysis
  - Docker Validation
  - Performance Regression Tests
  - Configuration Validation
  - Automated PR Comments

### Automation & Maintenance

#### `dependency-updates.yml` - Dependency Management
- **Trigger**: Wöchentlich, manuell
- **Jobs**:
  - Python Dependencies Update
  - GitHub Actions Update
  - Security Audit
  - Automated PR Creation

#### `update-actions.yml` - GitHub Actions Updates
- **Trigger**: Monatlich, manuell
- **Jobs**:
  - Action Version Updates
  - Security Review of Actions
  - Workflow Validation

### Deployment

#### `deployment.yml` - Staging & Production Deployment
- **Trigger**: Push zu main, Tags, manuell
- **Jobs**:
  - Staging Deployment
  - Production Deployment (nur für Tags)
  - Blue-Green Deployment
  - Automated Backups
  - Health Checks
  - Rollback bei Fehlern

#### `release.yml` - Release Management
- **Trigger**: Tags (v*), manuell
- **Jobs**:
  - Release Preparation
  - Full Test Suite
  - Build Release Assets
  - GitHub Release Creation
  - Container Registry Publishing
  - Documentation Updates

## 🛡️ Sicherheitsfeatures

### Automatisierte Sicherheitschecks
- ✅ **SAST**: Bandit, CodeQL, Semgrep, Custom Rules
- ✅ **DAST**: ZAP Baseline & Full Scans
- ✅ **Dependencies**: Safety, pip-audit, OSV Scanner
- ✅ **Container**: Trivy Image Scanning, Hadolint
- ✅ **Secrets**: GitLeaks, TruffleHog Detection
- ✅ **Supply Chain**: SBOM Generation, License Audit

### Compliance & Monitoring
- ✅ **Daily Monitoring**: Vulnerability Scans
- ✅ **Weekly Reports**: Compliance Status
- ✅ **Monthly Reminders**: Secret Rotation
- ✅ **Automated Issues**: Critical Vulnerability Alerts
- ✅ **Security Metrics**: Dashboard & Tracking

### Branch Protection
- ✅ **Required Reviews**: Min. 1 Reviewer
- ✅ **Status Checks**: Alle Tests müssen bestehen
- ✅ **No Force Push**: Verhindert Force Pushes
- ✅ **Up-to-date**: Branches müssen aktuell sein
- ✅ **Conversation Resolution**: Alle Kommentare müssen aufgelöst sein

## 🚀 Setup & Verwendung

### Automatisierte Einrichtung

```bash
# Führe das komplette Setup aus
./.github/setup-complete-repository.sh

# Oder nur die Python-basierte Security-Konfiguration
python .github/setup-repository-security.py
```

### Manuelle Einrichtung

1. **GitHub CLI installieren**:
   ```bash
   # macOS
   brew install gh
   
   # Ubuntu/Debian
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
   sudo apt update && sudo apt install gh
   ```

2. **GitHub CLI authentifizieren**:
   ```bash
   gh auth login
   ```

3. **Repository Secrets konfigurieren**:
   ```bash
   gh secret set ADMIN_PASSWORD
   gh secret set SECRET_KEY
   gh secret set SLACK_WEBHOOK  # Optional
   gh secret set SNYK_TOKEN     # Optional
   ```

4. **Pre-commit Hooks installieren**:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Workflow Testing

```bash
# Teste alle Workflows lokal
act -l  # Liste alle verfügbaren Jobs

# Teste spezifische Jobs
act -j lint
act -j security
act -j test
```

## 📊 Monitoring & Alerts

### Slack Integration
Konfiguriere Slack Webhooks für:
- 🚨 **Critical Security Alerts**
- 📦 **Deployment Notifications** 
- 🔄 **Dependency Updates**
- 📊 **Weekly Security Reports**

### GitHub Security Tab
Überwache:
- 🔍 **Code Scanning Alerts**
- 🚨 **Vulnerability Alerts**
- 🛡️ **Secret Scanning Results**
- 📋 **Security Advisories**

## 🛠️ Wartung

### Wöchentlich
- [ ] Review Dependabot PRs
- [ ] Check Security Alerts
- [ ] Monitor Workflow Status

### Monatlich  
- [ ] Review Access Permissions
- [ ] Update GitHub Actions
- [ ] Security Metrics Review
- [ ] Rotate Secrets (quarterly)

### Bei Kritischen Issues
- [ ] Immediate Security Patch
- [ ] Emergency Deployment
- [ ] Incident Documentation
- [ ] Process Improvement

## 🔧 Konfiguration

### Erforderliche Secrets

| Secret | Beschreibung | Required |
|--------|-------------|----------|
| `ADMIN_PASSWORD` | Admin Interface Passwort | ✅ Yes |
| `SECRET_KEY` | Flask Secret Key | ✅ Yes |
| `SLACK_WEBHOOK` | Slack Benachrichtigungen | ❌ Optional |
| `SNYK_TOKEN` | Snyk Security Scanning | ❌ Optional |
| `STAGING_HOST` | Staging Server Host | ❌ Optional |
| `STAGING_USER` | Staging Server User | ❌ Optional |
| `STAGING_SSH_KEY` | Staging SSH Key | ❌ Optional |
| `PROD_HOST` | Production Server Host | ❌ Optional |
| `PROD_USER` | Production Server User | ❌ Optional |
| `PROD_SSH_KEY` | Production SSH Key | ❌ Optional |

### Environment Variables (für Workflows)

```yaml
env:
  PYTHON_VERSION: '3.11'
  FORCE_COLOR: '1'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
```

## 📚 Dokumentation

### Workflow Dokumentation
- Jeder Workflow ist vollständig kommentiert
- Beschreibungen für alle Jobs und Steps
- Fehlerbehandlung und Fallback-Strategien

### Security Guidelines
- Siehe `SECURITY.md` für detaillierte Sicherheitsrichtlinien
- Best Practices für sichere Entwicklung
- Incident Response Prozeduren

## 🆘 Troubleshooting

### Häufige Probleme

1. **Workflow Failures**:
   ```bash
   # Workflow Logs anzeigen
   gh run list --limit 5
   gh run view [RUN_ID] --log
   ```

2. **Permission Errors**:
   - Überprüfe Repository Permissions
   - Stelle sicher, dass GITHUB_TOKEN korrekte Permissions hat
   - Aktiviere "Read and write permissions" für Actions

3. **Security Scan Failures**:
   - Überprüfe Bandit/Safety Reports
   - Update vulnerable Dependencies
   - Review Security Findings

4. **Deployment Issues**:
   - Check Docker Image Build
   - Verify Environment Variables
   - Review Server Connectivity

### Debug Commands

```bash
# Workflow Status
gh workflow list
gh run list --workflow=ci.yml --limit 10

# Security Status  
gh api repos/OWNER/REPO/vulnerability-alerts
gh api repos/OWNER/REPO/dependabot/alerts

# Repository Settings
gh repo view --json vulnerabilityAlertsEnabled,hasAutomatedSecurityFixesEnabled
```

## 🔄 Updates

Dieses Setup wird automatisch aktualisiert durch:
- **Monthly**: GitHub Actions Updates
- **Weekly**: Dependency Updates  
- **Daily**: Security Monitoring
- **On-Demand**: Manual Workflow Triggers

Für manuelle Updates:
```bash
# Update all workflows and configurations
git pull origin main
./.github/setup-complete-repository.sh
```

---

**Letzte Aktualisierung**: 2025-08-27  
**Version**: 1.0  
**Maintainer**: [@Ralle1976](https://github.com/Ralle1976)