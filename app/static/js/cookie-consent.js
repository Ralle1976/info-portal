/**
 * Cookie Consent Banner with Configurable Labels
 * Thailand PDPA and EU GDPR Compliant
 * Supports multi-language labels from backend configuration
 */

class CookieConsentBanner {
    constructor() {
        this.currentLanguage = document.documentElement.lang || 'th';
        this.consentData = null;
        this.bannerVisible = false;
        this.labels = {};
        
        this.init();
    }

    async init() {
        try {
            // Load labels and consent status
            await this.loadLabels();
            await this.checkConsentStatus();
            
            // Show banner if needed
            if (this.shouldShowBanner()) {
                this.createBanner();
                this.showBanner();
            }
            
            // Initialize consent-dependent features
            this.initializeFeatures();
            
        } catch (error) {
            console.error('Cookie consent initialization failed:', error);
        }
    }

    async loadLabels() {
        try {
            const response = await fetch(`/legal/cookie-banner-info?lang=${this.currentLanguage}`);
            const data = await response.json();
            
            this.labels = data.labels || {};
            this.consentData = data.current_consent;
            this.bannerVisible = data.show_banner;
            
        } catch (error) {
            console.error('Failed to load consent labels:', error);
            this.labels = this.getDefaultLabels();
        }
    }

    async checkConsentStatus() {
        try {
            const response = await fetch('/legal/consent-status');
            const data = await response.json();
            
            if (data.success && data.consent) {
                this.consentData = data.consent;
                return true;
            }
            
            return false;
            
        } catch (error) {
            console.error('Failed to check consent status:', error);
            return false;
        }
    }

    shouldShowBanner() {
        // Don't show if user already has valid consent
        if (this.consentData && this.consentData.expires_at) {
            const expiryDate = new Date(this.consentData.expires_at);
            if (expiryDate > new Date()) {
                return false;
            }
        }
        
        // Don't show on admin pages
        if (window.location.pathname.startsWith('/admin/')) {
            return false;
        }
        
        return true;
    }

    createBanner() {
        const banner = document.createElement('div');
        banner.id = 'cookie-consent-banner';
        banner.className = 'cookie-consent-banner';
        
        banner.innerHTML = `
            <div class="cookie-consent-content">
                <div class="cookie-consent-header">
                    <h3>${this.getLabel('banner.title', 'Cookie-Einstellungen')}</h3>
                    <button id="cookie-consent-close" class="cookie-consent-close" aria-label="${this.getLabel('banner.close', 'Schließen')}">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                        </svg>
                    </button>
                </div>
                
                <div class="cookie-consent-body">
                    <p class="cookie-consent-description">
                        ${this.getLabel('banner.description', 'Diese Website verwendet Cookies und verarbeitet personenbezogene Daten gemäß Thailand PDPA und EU DSGVO.')}
                    </p>
                    
                    <div class="cookie-consent-tabs">
                        <button class="cookie-tab active" data-tab="essential">${this.getLabel('consent.necessary', 'Notwendig')}</button>
                        <button class="cookie-tab" data-tab="functional">${this.getLabel('consent.functional', 'Funktional')}</button>
                        <button class="cookie-tab" data-tab="analytics">${this.getLabel('consent.analytics', 'Analytik')}</button>
                        <button class="cookie-tab" data-tab="marketing">${this.getLabel('consent.marketing', 'Marketing')}</button>
                    </div>
                    
                    <div class="cookie-consent-panels">
                        <!-- Essential Cookies Panel -->
                        <div class="cookie-panel active" data-panel="essential">
                            <div class="cookie-toggle">
                                <input type="checkbox" id="essential-cookies" checked disabled>
                                <label for="essential-cookies" class="cookie-toggle-label">
                                    <span class="cookie-toggle-title">${this.getLabel('consent.necessary', 'Notwendig')}</span>
                                    <span class="cookie-toggle-always">${this.getLabel('banner.always_active', 'Immer aktiv')}</span>
                                </label>
                            </div>
                            <p class="cookie-description">${this.getLabel('banner.necessary_description', 'Diese Cookies sind für das Funktionieren der Website unerlässlich.')}</p>
                            <div class="cookie-details">
                                <strong>${this.getLabel('banner.data_processed', 'Verarbeitete Daten')}:</strong>
                                <span>${this.getLabel('banner.necessary_data', 'Session-ID, Spracheinstellung, Consent-Status')}</span>
                            </div>
                            <div class="cookie-details">
                                <strong>${this.getLabel('banner.legal_basis', 'Rechtsgrundlage')}:</strong>
                                <span>${this.getLabel('banner.necessary_legal_basis', 'Berechtigte Interessen (Art. 6 Abs. 1 lit. f DSGVO)')}</span>
                            </div>
                        </div>
                        
                        <!-- Functional Cookies Panel -->
                        <div class="cookie-panel" data-panel="functional">
                            <div class="cookie-toggle">
                                <input type="checkbox" id="functional-cookies" ${this.consentData?.functional ? 'checked' : ''}>
                                <label for="functional-cookies" class="cookie-toggle-label">
                                    <span class="cookie-toggle-title">${this.getLabel('consent.functional', 'Funktional')}</span>
                                </label>
                            </div>
                            <p class="cookie-description">${this.getLabel('banner.functional_description', 'Diese Cookies verbessern die Nutzererfahrung.')}</p>
                            <div class="cookie-details">
                                <strong>${this.getLabel('banner.data_processed', 'Verarbeitete Daten')}:</strong>
                                <span>${this.getLabel('banner.functional_data', 'Benutzerpräferenzen, UI-Einstellungen')}</span>
                            </div>
                            <div class="cookie-details">
                                <strong>${this.getLabel('banner.retention', 'Speicherdauer')}:</strong>
                                <span>${this.getLabel('banner.functional_retention', '12 Monate')}</span>
                            </div>
                        </div>
                        
                        <!-- Analytics Cookies Panel -->
                        <div class="cookie-panel" data-panel="analytics">
                            <div class="cookie-toggle">
                                <input type="checkbox" id="analytics-cookies" ${this.consentData?.analytics ? 'checked' : ''}>
                                <label for="analytics-cookies" class="cookie-toggle-label">
                                    <span class="cookie-toggle-title">${this.getLabel('consent.analytics', 'Analytik')}</span>
                                </label>
                            </div>
                            <p class="cookie-description">${this.getLabel('banner.analytics_description', 'Diese Cookies helfen uns, die Website zu verbessern.')}</p>
                            <div class="cookie-details">
                                <strong>${this.getLabel('banner.data_processed', 'Verarbeitete Daten')}:</strong>
                                <span>${this.getLabel('banner.analytics_data', 'Anonymisierte Nutzungsstatistiken')}</span>
                            </div>
                            <div class="cookie-details">
                                <strong>${this.getLabel('banner.third_parties', 'Drittanbieter')}:</strong>
                                <span>${this.getLabel('banner.analytics_third_parties', 'Keine')}</span>
                            </div>
                        </div>
                        
                        <!-- Marketing Cookies Panel -->
                        <div class="cookie-panel" data-panel="marketing">
                            <div class="cookie-toggle">
                                <input type="checkbox" id="marketing-cookies" ${this.consentData?.marketing ? 'checked' : ''}>
                                <label for="marketing-cookies" class="cookie-toggle-label">
                                    <span class="cookie-toggle-title">${this.getLabel('consent.marketing', 'Marketing')}</span>
                                </label>
                            </div>
                            <p class="cookie-description">${this.getLabel('banner.marketing_description', 'Diese Cookies ermöglichen personalisierte Werbung.')}</p>
                            <div class="cookie-details">
                                <strong>${this.getLabel('banner.data_processed', 'Verarbeitete Daten')}:</strong>
                                <span>${this.getLabel('banner.marketing_data', 'Nutzungsprofil, Interessen')}</span>
                            </div>
                            <div class="cookie-details">
                                <strong>${this.getLabel('banner.third_parties', 'Drittanbieter')}:</strong>
                                <span>${this.getLabel('banner.marketing_third_parties', 'Social Media Partner')}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Medical Disclaimer for Laboratory -->
                    <div class="medical-disclaimer-section">
                        <div class="cookie-toggle">
                            <input type="checkbox" id="medical-disclaimer" ${this.consentData?.medical_disclaimer ? 'checked' : ''}>
                            <label for="medical-disclaimer" class="cookie-toggle-label">
                                <span class="cookie-toggle-title">${this.getLabel('consent.medical_disclaimer', 'Medizinischer Haftungsausschluss')}</span>
                            </label>
                        </div>
                        <p class="cookie-description medical-disclaimer-text">
                            ${this.getLabel('banner.medical_disclaimer_text', 'Ich verstehe, dass diese Website nur allgemeine Informationen über Laborleistungen bereitstellt und keinen Ersatz für eine medizinische Beratung darstellt.')}
                        </p>
                    </div>
                </div>
                
                <div class="cookie-consent-footer">
                    <div class="cookie-consent-links">
                        <a href="/legal/privacy?lang=${this.currentLanguage}" target="_blank">
                            ${this.getLabel('banner.privacy_policy', 'Datenschutzerklärung')}
                        </a>
                        <a href="/legal/terms?lang=${this.currentLanguage}" target="_blank">
                            ${this.getLabel('banner.terms', 'Nutzungsbedingungen')}
                        </a>
                        <a href="/legal/impressum?lang=${this.currentLanguage}" target="_blank">
                            ${this.getLabel('banner.impressum', 'Impressum')}
                        </a>
                    </div>
                    
                    <div class="cookie-consent-buttons">
                        <button id="cookie-consent-reject" class="cookie-btn cookie-btn-secondary">
                            ${this.getLabel('banner.reject_optional', 'Nur notwendige')}
                        </button>
                        <button id="cookie-consent-accept-all" class="cookie-btn cookie-btn-success">
                            ${this.getLabel('banner.accept_all', 'Alle akzeptieren')}
                        </button>
                        <button id="cookie-consent-save" class="cookie-btn cookie-btn-primary">
                            ${this.getLabel('banner.save_preferences', 'Auswahl speichern')}
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Thailand PDPA & EU GDPR Notice -->
            <div class="compliance-notice">
                <div class="compliance-flags">
                    <span class="flag-thai">🇹🇭</span>
                    <span class="flag-eu">🇪🇺</span>
                </div>
                <div class="compliance-text">
                    <small>${this.getLabel('banner.compliance_notice', 'Diese Website entspricht der Thailand PDPA und EU DSGVO')}</small>
                </div>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(banner);
        
        // Bind events
        this.bindEvents();
    }

    bindEvents() {
        // Tab switching
        document.querySelectorAll('.cookie-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });
        
        // Button actions
        document.getElementById('cookie-consent-close').addEventListener('click', () => {
            this.hideBanner();
        });
        
        document.getElementById('cookie-consent-reject').addEventListener('click', () => {
            this.rejectOptional();
        });
        
        document.getElementById('cookie-consent-accept-all').addEventListener('click', () => {
            this.acceptAll();
        });
        
        document.getElementById('cookie-consent-save').addEventListener('click', () => {
            this.savePreferences();
        });
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.bannerVisible) {
                this.hideBanner();
            }
        });
    }

    switchTab(tabName) {
        // Update active tab
        document.querySelectorAll('.cookie-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update active panel
        document.querySelectorAll('.cookie-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.querySelector(`[data-panel="${tabName}"]`).classList.add('active');
    }

    async rejectOptional() {
        const consentData = {
            functional: false,
            analytics: false,
            marketing: false,
            medical_disclaimer: false,
            language: this.currentLanguage,
            source: 'banner_reject'
        };
        
        await this.saveConsent(consentData);
        this.hideBanner();
    }

    async acceptAll() {
        const consentData = {
            functional: true,
            analytics: true,
            marketing: true,
            medical_disclaimer: true,
            language: this.currentLanguage,
            source: 'banner_accept_all'
        };
        
        await this.saveConsent(consentData);
        this.hideBanner();
    }

    async savePreferences() {
        const consentData = {
            functional: document.getElementById('functional-cookies').checked,
            analytics: document.getElementById('analytics-cookies').checked,
            marketing: document.getElementById('marketing-cookies').checked,
            medical_disclaimer: document.getElementById('medical-disclaimer').checked,
            language: this.currentLanguage,
            source: 'banner_custom'
        };
        
        await this.saveConsent(consentData);
        this.hideBanner();
    }

    async saveConsent(consentData) {
        try {
            const response = await fetch('/legal/consent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(consentData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.consentData = consentData;
                this.initializeFeatures();
                
                // Show success message
                this.showNotification(
                    this.getLabel('banner.consent_saved', 'Einstellungen gespeichert'),
                    'success'
                );
            } else {
                throw new Error(result.error || 'Failed to save consent');
            }
            
        } catch (error) {
            console.error('Failed to save consent:', error);
            this.showNotification(
                this.getLabel('banner.consent_error', 'Fehler beim Speichern'),
                'error'
            );
        }
    }

    showBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.classList.add('show');
            this.bannerVisible = true;
            
            // Add body class to prevent scrolling
            document.body.classList.add('cookie-banner-open');
        }
    }

    hideBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.classList.remove('show');
            this.bannerVisible = false;
            
            setTimeout(() => {
                banner.remove();
                document.body.classList.remove('cookie-banner-open');
            }, 300);
        }
    }

    initializeFeatures() {
        if (!this.consentData) return;
        
        // Initialize analytics if consented
        if (this.consentData.analytics) {
            this.initializeAnalytics();
        }
        
        // Initialize marketing features if consented
        if (this.consentData.marketing) {
            this.initializeMarketing();
        }
        
        // Initialize functional features if consented
        if (this.consentData.functional) {
            this.initializeFunctional();
        }
    }

    initializeAnalytics() {
        // Initialize analytics tracking (placeholder)
        console.log('Analytics initialized with consent');
    }

    initializeMarketing() {
        // Initialize marketing features (placeholder)
        console.log('Marketing features initialized with consent');
    }

    initializeFunctional() {
        // Initialize functional features (placeholder)
        console.log('Functional features initialized with consent');
    }

    getLabel(key, defaultValue = '') {
        const keys = key.split('.');
        let value = this.labels;
        
        for (const k of keys) {
            value = value && value[k];
        }
        
        return value || defaultValue;
    }

    getDefaultLabels() {
        // Fallback labels if backend is unavailable
        return {
            banner: {
                title: 'Cookie-Einstellungen',
                description: 'Diese Website verwendet Cookies gemäß Thailand PDPA und EU DSGVO.',
                accept_all: 'Alle akzeptieren',
                reject_optional: 'Nur notwendige',
                save_preferences: 'Auswahl speichern',
                privacy_policy: 'Datenschutzerklärung',
                always_active: 'Immer aktiv'
            },
            consent: {
                necessary: 'Notwendig',
                functional: 'Funktional',
                analytics: 'Analytik',
                marketing: 'Marketing'
            }
        };
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `cookie-notification cookie-notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new CookieConsentBanner();
    });
} else {
    new CookieConsentBanner();
}