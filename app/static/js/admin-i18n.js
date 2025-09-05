/**
 * Admin Interface Client-Side Internationalization System
 * 
 * This module provides client-side translation capabilities for the admin interface,
 * allowing JavaScript code to access translation keys dynamically.
 */

class AdminI18n {
    constructor() {
        this.translations = {};
        this.currentLanguage = 'de'; // Default language
        this.isReady = false;
        this.readyCallbacks = [];
        
        // Debug mode - set to false in production
        this.debug = false;
        
        this.log('AdminI18n initialized');
    }
    
    /**
     * Debug logging
     */
    log(...args) {
        if (this.debug) {
            console.log('[AdminI18n]', ...args);
        }
    }
    
    /**
     * Initialize the i18n system with language and load translations
     */
    async init(language = 'de') {
        this.currentLanguage = language;
        this.log(`Initializing with language: ${language}`);
        
        try {
            await this.loadTranslations(language);
            this.isReady = true;
            this.log('Ready!');
            
            // Execute any pending callbacks
            this.readyCallbacks.forEach(callback => {
                try {
                    callback();
                } catch (error) {
                    console.error('Error in ready callback:', error);
                }
            });
            this.readyCallbacks = [];
            
        } catch (error) {
            console.error('Failed to initialize AdminI18n:', error);
            // Fall back to showing keys as-is
            this.isReady = true;
        }
    }
    
    /**
     * Load translations for the specified language
     */
    async loadTranslations(language) {
        try {
            const response = await fetch(`/admin_translations_${language}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load translations for ${language}: ${response.status}`);
            }
            
            const data = await response.json();
            this.translations = data;
            this.log(`Loaded translations for ${language}`, Object.keys(this.translations));
            
        } catch (error) {
            console.error(`Failed to load translations for ${language}:`, error);
            
            // Try to fall back to German if not already trying German
            if (language !== 'de') {
                console.warn('Falling back to German translations');
                return this.loadTranslations('de');
            }
            
            // If German also fails, create empty translations object
            this.translations = {
                admin: {
                    errors: {},
                    validation: {},
                    common: {},
                    forms: {}
                }
            };
        }
    }
    
    /**
     * Get a translation by key path
     * @param {string} keyPath - Dot-separated path to translation (e.g., 'admin.common.save')
     * @param {object} params - Parameters to substitute in the translation (e.g., {name: 'John'})
     * @returns {string} - Translated string or the key if not found
     */
    t(keyPath, params = {}) {
        if (!this.isReady) {
            this.log(`Translation requested before ready: ${keyPath}`);
            return keyPath; // Return key as fallback
        }
        
        try {
            // Split the key path and navigate through the translation object
            const keys = keyPath.split('.');
            let value = this.translations;
            
            for (const key of keys) {
                if (value && typeof value === 'object' && key in value) {
                    value = value[key];
                } else {
                    this.log(`Translation not found for key: ${keyPath}`);
                    return keyPath; // Return key as fallback
                }
            }
            
            // If we found a string, process parameters
            if (typeof value === 'string') {
                return this.interpolate(value, params);
            } else {
                this.log(`Translation key does not resolve to string: ${keyPath}`, value);
                return keyPath;
            }
            
        } catch (error) {
            console.error(`Error getting translation for ${keyPath}:`, error);
            return keyPath;
        }
    }
    
    /**
     * Interpolate parameters into a translation string
     * Supports both {name} and X placeholder formats
     */
    interpolate(text, params) {
        let result = text;
        
        // Handle {key} style parameters
        Object.entries(params).forEach(([key, value]) => {
            const placeholder = `{${key}}`;
            result = result.replace(new RegExp(placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), value);
        });
        
        // Handle X placeholder (common in existing translations)
        if (params.X !== undefined) {
            result = result.replace(/X/g, params.X);
        }
        
        return result;
    }
    
    /**
     * Change language dynamically
     */
    async changeLanguage(language) {
        if (language === this.currentLanguage) {
            return; // Already using this language
        }
        
        this.log(`Changing language from ${this.currentLanguage} to ${language}`);
        this.isReady = false;
        await this.init(language);
    }
    
    /**
     * Get current language
     */
    getCurrentLanguage() {
        return this.currentLanguage;
    }
    
    /**
     * Check if system is ready
     */
    isReady() {
        return this.isReady;
    }
    
    /**
     * Execute callback when system is ready
     */
    onReady(callback) {
        if (this.isReady) {
            callback();
        } else {
            this.readyCallbacks.push(callback);
        }
    }
    
    /**
     * Get all available translation keys (for debugging)
     */
    getAvailableKeys(prefix = '', obj = null) {
        if (obj === null) obj = this.translations;
        let keys = [];
        
        for (const [key, value] of Object.entries(obj)) {
            const fullKey = prefix ? `${prefix}.${key}` : key;
            if (typeof value === 'object' && value !== null) {
                keys = keys.concat(this.getAvailableKeys(fullKey, value));
            } else if (typeof value === 'string') {
                keys.push(fullKey);
            }
        }
        
        return keys;
    }
    
    /**
     * Debug helper - print all available keys
     */
    debugKeys() {
        console.log('Available translation keys:', this.getAvailableKeys());
    }
}

// Create global instance
window.adminI18n = new AdminI18n();

// Create convenient global function
window.t = function(keyPath, params = {}) {
    return window.adminI18n.t(keyPath, params);
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // The actual initialization with current language will happen in the template
        console.log('AdminI18n ready for initialization');
    });
} else {
    console.log('AdminI18n ready for initialization');
}

// Export for module environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdminI18n;
}