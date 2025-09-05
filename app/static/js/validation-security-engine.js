/**
 * VALIDATION & SECURITY ENGINE - SUB-AGENT 5
 * Parallel execution: Comprehensive validation and security
 */

class ValidationSecurityAgent {
    constructor() {
        this.validators = new ValidationRuleEngine();
        this.security = new SecurityManager();
        this.realtime = new RealtimeValidation();
        
        this.init();
    }

    init() {
        console.log('🛡️ SUB-AGENT 5: Validation & Security Engine started');
        this.validators.init();
        this.security.init();
        this.realtime.init();
    }
}

class ValidationRuleEngine {
    constructor() {
        this.rules = {
            site_name: [
                { type: 'required', message: 'Name ist erforderlich' },
                { type: 'minLength', value: 3, message: 'Mindestens 3 Zeichen' },
                { type: 'maxLength', value: 100, message: 'Maximal 100 Zeichen' },
                { type: 'pattern', value: /^[a-zA-ZäöüÄÖÜß\s\-&.]+$/, message: 'Nur Buchstaben, Leerzeichen und - & . erlaubt' }
            ],
            contact_phone: [
                { type: 'required', message: 'Telefonnummer ist erforderlich' },
                { type: 'pattern', value: /^\+\d{1,3}[\s\d\-\(\)]{8,20}$/, message: 'Format: +66 123 456 789' }
            ],
            contact_email: [
                { type: 'required', message: 'E-Mail ist erforderlich' },
                { type: 'email', message: 'Ungültige E-Mail-Adresse' }
            ],
            admin_password: [
                { type: 'required', message: 'Passwort ist erforderlich' },
                { type: 'minLength', value: 8, message: 'Mindestens 8 Zeichen' },
                { type: 'custom', validator: this.validatePasswordStrength, message: 'Zu schwaches Passwort' }
            ],
            latitude: [
                { type: 'number', message: 'Muss eine Zahl sein' },
                { type: 'range', min: -90, max: 90, message: 'Zwischen -90 und 90' }
            ],
            longitude: [
                { type: 'number', message: 'Muss eine Zahl sein' },
                { type: 'range', min: -180, max: 180, message: 'Zwischen -180 und 180' }
            ]
        };
    }

    init() {
        console.log('✅ Validation Rules Engine initialized');
    }

    validateField(field, value) {
        const fieldName = field.name || field.id;
        const rules = this.rules[fieldName] || [];
        
        for (const rule of rules) {
            const result = this.applyRule(rule, value, field);
            if (!result.valid) {
                return result;
            }
        }
        
        return { valid: true };
    }

    applyRule(rule, value, field) {
        switch (rule.type) {
            case 'required':
                return {
                    valid: value && value.trim().length > 0,
                    message: rule.message
                };
                
            case 'minLength':
                return {
                    valid: !value || value.length >= rule.value,
                    message: rule.message
                };
                
            case 'maxLength':
                return {
                    valid: !value || value.length <= rule.value,
                    message: rule.message
                };
                
            case 'pattern':
                return {
                    valid: !value || rule.value.test(value),
                    message: rule.message
                };
                
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return {
                    valid: !value || emailRegex.test(value),
                    message: rule.message
                };
                
            case 'number':
                return {
                    valid: !value || !isNaN(parseFloat(value)),
                    message: rule.message
                };
                
            case 'range':
                const num = parseFloat(value);
                return {
                    valid: !value || (num >= rule.min && num <= rule.max),
                    message: rule.message
                };
                
            case 'custom':
                return rule.validator(value, field);
                
            default:
                return { valid: true };
        }
    }

    validatePasswordStrength(password) {
        if (!password) return { valid: false, message: 'Passwort eingeben' };

        const checks = {
            length: password.length >= 8,
            upper: /[A-Z]/.test(password),
            lower: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        const score = Object.values(checks).filter(Boolean).length;
        
        if (score < 3) {
            return { 
                valid: false, 
                message: 'Benötigt: Groß-/Kleinbuchstaben, Zahlen, Sonderzeichen'
            };
        }
        
        return { valid: true };
    }

    // Advanced validation for business logic
    validateOpeningHours(hoursData) {
        const errors = [];
        
        Object.entries(hoursData).forEach(([day, ranges]) => {
            ranges.forEach((range, index) => {
                if (!this.isValidTimeRange(range)) {
                    errors.push(`${day}: Ungültiger Zeitraum ${index + 1}`);
                }
            });
            
            // Check for overlapping ranges
            if (this.hasOverlappingRanges(ranges)) {
                errors.push(`${day}: Überschneidende Zeiträume`);
            }
        });
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }

    isValidTimeRange(range) {
        const [start, end] = range.split('-');
        if (!start || !end) return false;
        
        const startMinutes = this.timeToMinutes(start);
        const endMinutes = this.timeToMinutes(end);
        
        return startMinutes < endMinutes && startMinutes >= 0 && endMinutes <= 1440;
    }

    hasOverlappingRanges(ranges) {
        for (let i = 0; i < ranges.length; i++) {
            for (let j = i + 1; j < ranges.length; j++) {
                if (this.rangesOverlap(ranges[i], ranges[j])) {
                    return true;
                }
            }
        }
        return false;
    }

    rangesOverlap(range1, range2) {
        const [start1, end1] = range1.split('-').map(this.timeToMinutes);
        const [start2, end2] = range2.split('-').map(this.timeToMinutes);
        
        return start1 < end2 && start2 < end1;
    }

    timeToMinutes(timeString) {
        const [hours, minutes] = timeString.split(':').map(Number);
        return hours * 60 + minutes;
    }
}

class SecurityManager {
    constructor() {
        this.csrfToken = null;
        this.securityHeaders = new Map();
        this.encryptionKey = null;
    }

    init() {
        console.log('🔐 Security Manager initialized');
        this.initializeCSRF();
        this.setupSecurityHeaders();
        this.initializeEncryption();
        this.setupSecurityMonitoring();
    }

    initializeCSRF() {
        // Get CSRF token from form
        this.csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
        
        if (!this.csrfToken) {
            console.warn('⚠️ CSRF token not found');
            return;
        }

        // Add CSRF token to all AJAX requests
        const originalFetch = window.fetch;
        window.fetch = async (url, options = {}) => {
            if (options.method && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method.toUpperCase())) {
                options.headers = {
                    ...options.headers,
                    'X-CSRFToken': this.csrfToken
                };
            }
            return originalFetch(url, options);
        };
    }

    setupSecurityHeaders() {
        this.securityHeaders.set('X-Content-Type-Options', 'nosniff');
        this.securityHeaders.set('X-Frame-Options', 'DENY');
        this.securityHeaders.set('X-XSS-Protection', '1; mode=block');
        this.securityHeaders.set('Referrer-Policy', 'strict-origin-when-cross-origin');
    }

    initializeEncryption() {
        // Generate session-specific encryption key for sensitive data
        if (window.crypto && window.crypto.getRandomValues) {
            this.encryptionKey = this.generateEncryptionKey();
        }
    }

    generateEncryptionKey() {
        const array = new Uint8Array(32);
        window.crypto.getRandomValues(array);
        return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }

    setupSecurityMonitoring() {
        // Monitor for suspicious activity
        let rapidRequests = 0;
        const requestWindow = 60000; // 1 minute
        
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            rapidRequests++;
            
            setTimeout(() => rapidRequests--, requestWindow);
            
            if (rapidRequests > 50) {
                console.warn('🚨 Suspicious activity detected: Too many requests');
                this.logSecurityEvent('rapid_requests', { count: rapidRequests });
            }
            
            return originalFetch(...args);
        };
        
        // Monitor for XSS attempts
        document.addEventListener('input', (e) => {
            if (this.containsSuspiciousContent(e.target.value)) {
                console.warn('🚨 Suspicious input detected');
                this.logSecurityEvent('suspicious_input', { 
                    field: e.target.name,
                    value: e.target.value.substring(0, 50) 
                });
                
                // Sanitize input
                e.target.value = this.sanitizeInput(e.target.value);
            }
        });
    }

    containsSuspiciousContent(value) {
        if (!value) return false;
        
        const suspiciousPatterns = [
            /<script[^>]*>/i,
            /javascript:/i,
            /on\w+\s*=/i,
            /<iframe[^>]*>/i,
            /eval\s*\(/i,
            /document\.cookie/i
        ];
        
        return suspiciousPatterns.some(pattern => pattern.test(value));
    }

    sanitizeInput(value) {
        return value
            .replace(/<script[^>]*>.*?<\/script>/gi, '')
            .replace(/javascript:/gi, '')
            .replace(/on\w+\s*=/gi, '')
            .replace(/<iframe[^>]*>.*?<\/iframe>/gi, '')
            .replace(/eval\s*\(/gi, '')
            .replace(/document\.cookie/gi, '');
    }

    logSecurityEvent(type, details) {
        const event = {
            type,
            details,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href
        };
        
        try {
            const logs = JSON.parse(localStorage.getItem('security_events') || '[]');
            logs.push(event);
            
            // Keep only last 100 events
            if (logs.length > 100) {
                logs.splice(0, logs.length - 100);
            }
            
            localStorage.setItem('security_events', JSON.stringify(logs));
            
            // Send to backend if available
            fetch('/admin/api/security-event', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify(event)
            }).catch(console.warn);
            
        } catch (error) {
            console.warn('Failed to log security event:', error);
        }
    }

    // Password security analysis
    analyzePasswordSecurity(password) {
        const analysis = {
            length: password.length,
            hasUppercase: /[A-Z]/.test(password),
            hasLowercase: /[a-z]/.test(password),
            hasNumbers: /\d/.test(password),
            hasSpecialChars: /[!@#$%^&*(),.?":{}|<>]/.test(password),
            commonPatterns: this.checkCommonPatterns(password),
            entropy: this.calculateEntropy(password)
        };

        analysis.score = this.calculatePasswordScore(analysis);
        analysis.recommendations = this.getPasswordRecommendations(analysis);
        
        return analysis;
    }

    checkCommonPatterns(password) {
        const commonPatterns = [
            /123456/,
            /password/i,
            /qwerty/i,
            /admin/i,
            /test/i,
            /(\w)\1{2,}/, // Repeated characters
            /(\d)\1{2,}/, // Repeated numbers
        ];
        
        return commonPatterns.filter(pattern => pattern.test(password)).length;
    }

    calculateEntropy(password) {
        const charset = new Set(password);
        const charsetSize = charset.size;
        const length = password.length;
        
        return Math.log2(Math.pow(charsetSize, length));
    }

    calculatePasswordScore(analysis) {
        let score = 0;
        
        // Length bonus
        score += Math.min(analysis.length * 2, 20);
        
        // Character type bonuses
        if (analysis.hasUppercase) score += 5;
        if (analysis.hasLowercase) score += 5;
        if (analysis.hasNumbers) score += 5;
        if (analysis.hasSpecialChars) score += 10;
        
        // Entropy bonus
        score += Math.min(analysis.entropy / 10, 20);
        
        // Penalties
        score -= analysis.commonPatterns * 10;
        
        return Math.max(0, Math.min(100, score));
    }

    getPasswordRecommendations(analysis) {
        const recommendations = [];
        
        if (!analysis.hasUppercase) recommendations.push('Großbuchstaben hinzufügen');
        if (!analysis.hasLowercase) recommendations.push('Kleinbuchstaben hinzufügen');
        if (!analysis.hasNumbers) recommendations.push('Zahlen hinzufügen');
        if (!analysis.hasSpecialChars) recommendations.push('Sonderzeichen hinzufügen');
        if (analysis.length < 12) recommendations.push('Länger als 12 Zeichen');
        if (analysis.commonPatterns > 0) recommendations.push('Häufige Muster vermeiden');
        if (analysis.entropy < 50) recommendations.push('Mehr Variationen verwenden');
        
        return recommendations;
    }
}

class RealtimeValidation {
    constructor() {
        this.validationCache = new Map();
        this.debounceTimers = new Map();
    }

    init() {
        console.log('⚡ Realtime Validation initialized');
        this.setupRealtimeListeners();
        this.createValidationUI();
    }

    setupRealtimeListeners() {
        // Add real-time validation to all form fields
        document.addEventListener('input', (e) => {
            if (e.target.matches('input, select, textarea')) {
                this.debounceValidation(e.target);
            }
        });

        document.addEventListener('blur', (e) => {
            if (e.target.matches('input, select, textarea')) {
                this.validateFieldImmediate(e.target);
            }
        });
    }

    debounceValidation(field) {
        const fieldId = field.name || field.id;
        
        // Clear existing timer
        if (this.debounceTimers.has(fieldId)) {
            clearTimeout(this.debounceTimers.get(fieldId));
        }
        
        // Set new timer
        const timer = setTimeout(() => {
            this.validateFieldImmediate(field);
        }, 300);
        
        this.debounceTimers.set(fieldId, timer);
    }

    async validateFieldImmediate(field) {
        const fieldId = field.name || field.id;
        const value = field.value;
        
        try {
            // Check cache first
            const cacheKey = `${fieldId}:${value}`;
            if (this.validationCache.has(cacheKey)) {
                const cachedResult = this.validationCache.get(cacheKey);
                this.updateFieldUI(field, cachedResult);
                return cachedResult;
            }

            // Perform validation
            const validationEngine = window.validationSecurityAgent?.validators || window.wizardController?.validators;
            let result;
            
            if (validationEngine) {
                result = validationEngine.validateField(field, value);
            } else {
                result = this.basicValidation(field, value);
            }

            // Backend validation for critical fields
            if (this.isCriticalField(fieldId) && result.valid) {
                result = await this.validateWithBackend(fieldId, value);
            }

            // Cache result
            this.validationCache.set(cacheKey, result);
            
            // Update UI
            this.updateFieldUI(field, result);
            
            return result;
            
        } catch (error) {
            console.error('Validation error:', error);
            const errorResult = { valid: false, message: 'Validierungsfehler' };
            this.updateFieldUI(field, errorResult);
            return errorResult;
        }
    }

    async validateWithBackend(fieldName, value) {
        try {
            const response = await fetch('/admin/api/validate-field', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                },
                body: JSON.stringify({ field: fieldName, value })
            });

            const result = await response.json();
            return result;
            
        } catch (error) {
            console.warn('Backend validation failed:', error);
            return { valid: true }; // Fallback to client-side validation
        }
    }

    isCriticalField(fieldName) {
        const criticalFields = ['contact_email', 'admin_password', 'site_name'];
        return criticalFields.includes(fieldName);
    }

    basicValidation(field, value) {
        if (field.hasAttribute('required') && !value.trim()) {
            return { valid: false, message: 'Pflichtfeld' };
        }
        
        if (field.type === 'email' && value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            return { valid: false, message: 'Ungültige E-Mail' };
        }
        
        return { valid: true };
    }

    updateFieldUI(field, result) {
        const formGroup = field.closest('.form-group');
        if (!formGroup) return;

        // Remove existing validation classes and messages
        field.classList.remove('field-valid', 'field-invalid');
        const existingError = formGroup.querySelector('.field-error');
        const existingSuccess = formGroup.querySelector('.field-success');
        
        if (existingError) existingError.remove();
        if (existingSuccess) existingSuccess.remove();

        if (result.valid) {
            field.classList.add('field-valid');
            
            // Add success indicator for critical fields
            if (this.isCriticalField(field.name)) {
                const successEl = document.createElement('div');
                successEl.className = 'field-success';
                successEl.innerHTML = '<i class="fas fa-check-circle"></i> Gültig';
                formGroup.appendChild(successEl);
            }
        } else {
            field.classList.add('field-invalid');
            
            // Add error message
            const errorEl = document.createElement('div');
            errorEl.className = 'field-error';
            errorEl.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${result.message}`;
            formGroup.appendChild(errorEl);
        }
    }

    createValidationUI() {
        // Add validation status indicator
        const validationHTML = `
            <div class="validation-status-panel" id="validation-status">
                <div class="validation-summary">
                    <div class="validation-item">
                        <span class="validation-label">Validierung:</span>
                        <span class="validation-count" id="validation-count">0/0</span>
                    </div>
                    <div class="validation-progress">
                        <div class="validation-bar" id="validation-bar"></div>
                    </div>
                </div>
            </div>
        `;
        
        // Add to each wizard step
        document.querySelectorAll('.wizard-step').forEach(step => {
            step.insertAdjacentHTML('afterbegin', validationHTML);
        });
    }

    updateValidationStatus() {
        const allFields = document.querySelectorAll('input, select, textarea');
        const validFields = document.querySelectorAll('.field-valid').length;
        const totalFields = Array.from(allFields).filter(field => 
            field.type !== 'hidden' && !field.disabled
        ).length;
        
        const percentage = totalFields > 0 ? (validFields / totalFields) * 100 : 0;
        
        const countElement = document.getElementById('validation-count');
        const barElement = document.getElementById('validation-bar');
        
        if (countElement) countElement.textContent = `${validFields}/${totalFields}`;
        if (barElement) barElement.style.width = `${percentage}%`;
    }
}

// Enhanced security monitoring
class SecurityMonitor {
    constructor() {
        this.events = [];
        this.suspiciousActivity = 0;
        this.maxSuspiciousEvents = 10;
    }

    init() {
        this.setupEventMonitoring();
        this.setupNetworkMonitoring();
    }

    setupEventMonitoring() {
        // Monitor for unusual user behavior
        let clickCount = 0;
        let lastClickTime = 0;
        
        document.addEventListener('click', (e) => {
            const now = Date.now();
            if (now - lastClickTime < 100) {
                clickCount++;
                if (clickCount > 10) {
                    this.logSuspiciousActivity('rapid_clicking', { count: clickCount });
                }
            } else {
                clickCount = 0;
            }
            lastClickTime = now;
        });

        // Monitor for console access
        let devtools = false;
        setInterval(() => {
            const widthThreshold = window.outerWidth - window.innerWidth > 160;
            const heightThreshold = window.outerHeight - window.innerHeight > 160;
            
            if ((heightThreshold || widthThreshold) && !devtools) {
                devtools = true;
                this.logSuspiciousActivity('devtools_opened');
            } else if (!(heightThreshold || widthThreshold) && devtools) {
                devtools = false;
            }
        }, 500);
    }

    setupNetworkMonitoring() {
        // Monitor network requests
        const originalOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url, ...args) {
            // Log external requests
            if (url.startsWith('http') && !url.includes(window.location.origin)) {
                console.warn('🌐 External request detected:', url);
            }
            
            return originalOpen.call(this, method, url, ...args);
        };
    }

    logSuspiciousActivity(type, details = {}) {
        this.suspiciousActivity++;
        
        const event = {
            type,
            details,
            timestamp: new Date().toISOString(),
            suspiciousCount: this.suspiciousActivity
        };
        
        this.events.push(event);
        console.warn('🚨 Suspicious activity logged:', event);
        
        if (this.suspiciousActivity > this.maxSuspiciousEvents) {
            this.handleSecurityBreach();
        }
    }

    handleSecurityBreach() {
        console.error('🚨 SECURITY BREACH DETECTED - Too many suspicious events');
        
        // Lock wizard temporarily
        document.querySelectorAll('input, select, textarea, button').forEach(el => {
            el.disabled = true;
        });
        
        // Show security warning
        const warningHTML = `
            <div class="security-warning-overlay">
                <div class="security-warning-content">
                    <i class="fas fa-shield-alt text-6xl text-red-500 mb-4"></i>
                    <h2>Sicherheitswarnung</h2>
                    <p>Verdächtige Aktivitäten erkannt. Das Setup wurde vorübergehend gesperrt.</p>
                    <button onclick="this.closest('.security-warning-overlay').remove(); location.reload();" 
                            class="btn btn-primary">
                        Seite neu laden
                    </button>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', warningHTML);
    }
}

// Global instances
window.validationSecurityAgent = new ValidationSecurityAgent();
window.securityMonitor = new SecurityMonitor();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.wizard-container')) {
        window.securityMonitor.init();
    }
});