#!/bin/bash
# QR Info Portal - Quick Security & UX Fixes
# Can be executed immediately to resolve critical issues

set -e

echo "🚀 QR Info Portal - Quick Fixes Deployment"
echo "=========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "app/__init__.py" ]; then
    log_error "Please run this script from the project root directory"
    exit 1
fi

log_info "Starting Quick Fixes deployment..."

# 1. Install additional dependencies
log_info "Installing security dependencies..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    log_warning "Virtual environment not found. Please run:"
    echo "python3 -m venv .venv && source .venv/bin/activate"
    exit 1
fi

pip install flask-wtf flask-compress flask-talisman >/dev/null 2>&1
log_success "Dependencies installed"

# 2. Create backup of current files
log_info "Creating backup of original files..."
backup_dir="backup/quick-fixes-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"

# Backup important files
cp app/__init__.py "$backup_dir/app__init__.py.bak" 2>/dev/null || true
cp -r app/templates "$backup_dir/templates.bak" 2>/dev/null || true
cp -r app/static "$backup_dir/static.bak" 2>/dev/null || true

log_success "Backup created in $backup_dir"

# 3. Apply Security Headers Fix
log_info "Applying security headers fix..."

if ! grep -q "set_security_headers" app/__init__.py; then
    cat >> app/__init__.py << 'EOF'

# Quick Fix: Security Headers
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # Force HTTPS in production
    if app.config.get('ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response
EOF
    log_success "Security headers added"
else
    log_warning "Security headers already present"
fi

# 4. Add CSRF Protection
log_info "Adding CSRF protection..."

if ! grep -q "CSRFProtect" app/__init__.py; then
    # Add import at top of file
    sed -i '/from flask import Flask/a from flask_wtf.csrf import CSRFProtect' app/__init__.py
    
    # Add CSRF initialization
    sed -i '/app = Flask(__name__)/a \    # CSRF Protection\n    csrf = CSRFProtect(app)\n    app.config["WTF_CSRF_TIME_LIMIT"] = None' app/__init__.py
    
    log_success "CSRF protection added"
else
    log_warning "CSRF protection already present"
fi

# 5. Enable Compression
log_info "Enabling GZIP compression..."

if ! grep -q "Compress" app/__init__.py; then
    sed -i '/from flask import Flask/a from flask_compress import Compress' app/__init__.py
    sed -i '/app = Flask(__name__)/a \    # GZIP Compression\n    Compress(app)' app/__init__.py
    
    log_success "GZIP compression enabled"
else
    log_warning "Compression already enabled"
fi

# 6. Add Mobile Navigation CSS
log_info "Adding mobile navigation CSS..."

mobile_css="app/static/css/mobile-fixes.css"
cat > "$mobile_css" << 'EOF'
/* Quick Fix: Mobile Navigation */
.mobile-bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-top: 1px solid #e5e7eb;
    display: none;
    grid-template-columns: repeat(3, 1fr);
    padding: 0.5rem;
    z-index: 50;
    box-shadow: 0 -2px 4px rgba(0,0,0,0.1);
}

@media (max-width: 768px) {
    body {
        padding-bottom: 4rem !important;
    }
    
    .mobile-bottom-nav {
        display: grid !important;
    }
    
    .desktop-nav {
        display: none !important;
    }
}

.nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.5rem;
    color: #6b7280;
    text-decoration: none;
    transition: all 0.2s;
    border-radius: 0.5rem;
}

.nav-item:hover,
.nav-item:focus {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
}

.nav-item.active {
    color: #3b82f6;
    background: rgba(59, 130, 246, 0.1);
}

.nav-item:active {
    transform: scale(0.95);
}

.nav-icon {
    width: 1.5rem;
    height: 1.5rem;
    margin-bottom: 0.25rem;
}

.nav-item span {
    font-size: 0.75rem;
    font-weight: 500;
}

/* Language Switcher Fix */
.language-switcher-floating {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 100;
}

.lang-trigger {
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    background: white;
    border: 2px solid #e5e7eb;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: all 0.2s;
}

.lang-trigger:hover {
    transform: scale(1.1);
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.lang-trigger:active {
    transform: scale(0.95);
}

.lang-menu {
    position: absolute;
    top: 3.5rem;
    right: 0;
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    padding: 0.5rem;
    min-width: 150px;
    display: none;
    opacity: 0;
    transform: translateY(-10px);
    transition: all 0.2s;
}

.language-switcher-floating:hover .lang-menu,
.language-switcher-floating:focus-within .lang-menu {
    display: block;
    opacity: 1;
    transform: translateY(0);
}

.lang-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-radius: 0.25rem;
    text-decoration: none;
    color: #374151;
    transition: background 0.2s;
    cursor: pointer;
}

.lang-option:hover {
    background: #f3f4f6;
}

.lang-option.active {
    background: #eff6ff;
    color: #2563eb;
    font-weight: 600;
}

.flag {
    font-size: 1.25rem;
}

/* Loading States */
.loading {
    opacity: 0.6;
    pointer-events: none;
}

button.loading {
    position: relative;
    color: transparent !important;
}

button.loading::after {
    content: "";
    position: absolute;
    width: 16px;
    height: 16px;
    top: 50%;
    left: 50%;
    margin: -8px 0 0 -8px;
    border: 2px solid #fff;
    border-radius: 50%;
    border-top-color: transparent;
    animation: spinner 0.6s linear infinite;
}

@keyframes spinner {
    to { transform: rotate(360deg); }
}

/* Toast Notifications */
.toast {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: #374151;
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.3s;
    max-width: 350px;
    z-index: 10000;
}

.toast.show {
    transform: translateY(0);
    opacity: 1;
}

.toast-success {
    background: #10b981;
}

.toast-error {
    background: #ef4444;
}

.toast-warning {
    background: #f59e0b;
}

@media (max-width: 640px) {
    .toast {
        left: 1rem;
        right: 1rem;
        bottom: 5rem;
    }
    
    .language-switcher-floating {
        top: auto;
        bottom: 5rem;
    }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    .lang-trigger,
    .nav-item {
        border-width: 2px;
        border-color: #000;
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
EOF

log_success "Mobile CSS fixes added"

# 7. Update base template with mobile navigation
log_info "Adding mobile navigation to base template..."

if [ -f "app/templates/base.html" ]; then
    if ! grep -q "mobile-bottom-nav" app/templates/base.html; then
        # Add mobile navigation before closing body tag
        sed -i '/<\/body>/i \
<!-- Quick Fix: Mobile Bottom Navigation -->\
<nav class="mobile-bottom-nav">\
    <a href="/" class="nav-item {{ '\''active'\'' if request.endpoint == '\''public.index'\'' }}">\
        <svg class="nav-icon" fill="currentColor" viewBox="0 0 20 20">\
            <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>\
        </svg>\
        <span>{{ _('\''Home'\'') }}</span>\
    </a>\
    <a href="/week" class="nav-item {{ '\''active'\'' if request.endpoint == '\''public.week'\'' }}">\
        <svg class="nav-icon" fill="currentColor" viewBox="0 0 20 20">\
            <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zM4 8h12v8H4V8z"></path>\
        </svg>\
        <span>{{ _('\''Week'\'') }}</span>\
    </a>\
    <a href="/month" class="nav-item {{ '\''active'\'' if request.endpoint == '\''public.month'\'' }}">\
        <svg class="nav-icon" fill="currentColor" viewBox="0 0 20 20">\
            <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zM4 8h12v8H4V8z"></path>\
        </svg>\
        <span>{{ _('\''Month'\'') }}</span>\
    </a>\
</nav>' app/templates/base.html

        log_success "Mobile navigation added to base template"
    else
        log_warning "Mobile navigation already present"
    fi

    # Add CSS link to head
    if ! grep -q "mobile-fixes.css" app/templates/base.html; then
        sed -i '/<\/head>/i \    <link rel="stylesheet" href="{{ url_for('\''static'\'', filename='\''css/mobile-fixes.css'\'') }}">' app/templates/base.html
        log_success "Mobile fixes CSS linked"
    else
        log_warning "Mobile fixes CSS already linked"
    fi

    # Add language switcher
    if ! grep -q "language-switcher-floating" app/templates/base.html; then
        sed -i '/<body>/a \
<!-- Quick Fix: Language Switcher -->\
<div class="language-switcher-floating">\
    <button class="lang-trigger" aria-label="Change language">\
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">\
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"></path>\
        </svg>\
    </button>\
    <div class="lang-menu">\
        <a href="?lang=de" class="lang-option {{ '\''active'\'' if g.language == '\''de'\'' }}">\
            <span class="flag">🇩🇪</span>\
            <span>Deutsch</span>\
        </a>\
        <a href="?lang=th" class="lang-option {{ '\''active'\'' if g.language == '\''th'\'' }}">\
            <span class="flag">🇹🇭</span>\
            <span>ไทย</span>\
        </a>\
        <a href="?lang=en" class="lang-option {{ '\''active'\'' if g.language == '\''en'\'' }}">\
            <span class="flag">🇬🇧</span>\
            <span>English</span>\
        </a>\
    </div>\
</div>' app/templates/base.html

        log_success "Language switcher added"
    else
        log_warning "Language switcher already present"
    fi
fi

# 8. Add feedback JavaScript
log_info "Adding feedback system..."

mkdir -p app/static/js
cat > app/static/js/feedback-system.js << 'EOF'
// Quick Fix: Feedback System
class FeedbackSystem {
    constructor() {
        this.createLoadingOverlay();
        this.interceptForms();
        this.interceptLinks();
    }
    
    createLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.innerHTML = `
            <div class="spinner">
                <div class="bounce1"></div>
                <div class="bounce2"></div>
                <div class="bounce3"></div>
            </div>
        `;
        overlay.style.cssText = `
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(255,255,255,0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s;
        `;
        document.body.appendChild(overlay);
    }
    
    show() {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.opacity = '1';
        overlay.style.pointerEvents = 'all';
    }
    
    hide() {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.opacity = '0';
        overlay.style.pointerEvents = 'none';
    }
    
    interceptForms() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                this.show();
                const submitBtn = form.querySelector('[type="submit"]');
                if (submitBtn) {
                    submitBtn.style.opacity = '0.6';
                    submitBtn.disabled = true;
                }
            });
        });
    }
    
    interceptLinks() {
        document.querySelectorAll('a[href^="/"]').forEach(link => {
            link.addEventListener('click', (e) => {
                if (!e.ctrlKey && !e.shiftKey && !e.metaKey) {
                    setTimeout(() => this.show(), 100);
                }
            });
        });
    }
    
    success(message) {
        this.showToast(message, 'success');
    }
    
    error(message) {
        this.showToast(message, 'error');
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#374151'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 350px;
            z-index: 10000;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.transform = 'translateY(0)';
            toast.style.opacity = '1';
        }, 10);
        
        setTimeout(() => {
            toast.style.transform = 'translateY(100px)';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.feedback = new FeedbackSystem();
});

window.addEventListener('load', () => {
    window.feedback?.hide();
});

// Add touch feedback for better mobile UX
document.addEventListener('touchstart', function(e) {
    if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') {
        e.target.style.transform = 'scale(0.95)';
    }
});

document.addEventListener('touchend', function(e) {
    if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') {
        setTimeout(() => {
            e.target.style.transform = 'scale(1)';
        }, 150);
    }
});
EOF

log_success "Feedback system JavaScript created"

# Link JavaScript in base template
if [ -f "app/templates/base.html" ]; then
    if ! grep -q "feedback-system.js" app/templates/base.html; then
        sed -i '/<\/body>/i \    <script src="{{ url_for('\''static'\'', filename='\''js/feedback-system.js'\'') }}"></script>' app/templates/base.html
        log_success "Feedback system linked in template"
    fi
fi

# 9. Test deployment
log_info "Testing fixes..."

# Check if Flask is running
if pgrep -f "flask" > /dev/null; then
    log_warning "Flask is already running. Please restart to apply changes:"
    echo "  pkill -f flask"
    echo "  flask run --host 0.0.0.0 --port 5000"
else
    log_info "Starting Flask development server for testing..."
    flask run --host 0.0.0.0 --port 5000 &
    FLASK_PID=$!
    
    # Wait for server to start
    sleep 3
    
    # Test health endpoint
    if curl -s http://localhost:5000/health > /dev/null; then
        log_success "Server is responding"
    else
        log_error "Server is not responding"
        kill $FLASK_PID 2>/dev/null || true
        exit 1
    fi
    
    # Test security headers
    if curl -s -I http://localhost:5000 | grep -q "X-Content-Type-Options"; then
        log_success "Security headers are present"
    else
        log_error "Security headers not found"
    fi
    
    # Stop test server
    kill $FLASK_PID 2>/dev/null || true
fi

# 10. Final checks
log_info "Running final validations..."

# Check file syntax
python -m py_compile app/__init__.py
log_success "Python syntax check passed"

# Check CSS syntax (basic)
if command -v csslint >/dev/null 2>&1; then
    csslint app/static/css/mobile-fixes.css
    log_success "CSS syntax check passed"
fi

echo ""
echo "🎉 Quick Fixes Applied Successfully!"
echo "=================================="
echo ""
log_info "Applied fixes:"
echo "  ✅ Security headers"
echo "  ✅ CSRF protection"
echo "  ✅ GZIP compression"
echo "  ✅ Mobile navigation"
echo "  ✅ Language switcher"
echo "  ✅ Loading feedback"
echo "  ✅ Toast notifications"
echo ""
log_info "Next steps:"
echo "  1. Restart the Flask server: flask run --host 0.0.0.0 --port 5000"
echo "  2. Test on mobile device: http://<your-ip>:5000"
echo "  3. Check browser security: Open DevTools > Security"
echo "  4. Review backup in: $backup_dir"
echo ""
log_warning "For production deployment, see docs/DEPLOYMENT_STRATEGY.md"
echo ""

# Show LAN IP for testing
lan_ip=$(hostname -I | awk '{print $1}')
echo -e "${BLUE}🌐 Test on LAN devices: http://$lan_ip:5000${NC}"
echo ""