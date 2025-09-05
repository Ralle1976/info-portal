/**
 * SETUP WIZARD CONTROLLER
 * Multi-Agent Architecture: Advanced wizard management system
 * Features: Step navigation, validation, live preview, auto-save
 */

class SetupWizardController {
    constructor() {
        this.config = {
            totalSteps: 7,
            currentStep: 1,
            autoSaveInterval: 30000, // 30 seconds
            validationTimeout: 500, // Debounce validation
            previewUpdateDelay: 1000
        };

        this.state = {
            formData: new Map(),
            validationErrors: new Map(),
            isDirty: false,
            isSubmitting: false,
            previewMode: false
        };

        this.validators = new ValidationEngine();
        this.previewSystem = new LivePreviewSystem();
        this.locationHelper = new LocationHelper();
        
        this.init();
    }

    /**
     * Initialize the wizard controller
     */
    init() {
        console.log('🧙‍♂️ Initializing Setup Wizard Controller...');
        
        this.bindElements();
        this.setupEventListeners();
        this.initializeSubSystems();
        this.loadSavedProgress();
        this.updateUI();
        
        console.log('✅ Setup Wizard Controller initialized');
    }

    /**
     * Bind DOM elements
     */
    bindElements() {
        this.elements = {
            form: document.getElementById('wizard-form'),
            steps: document.querySelectorAll('.wizard-step'),
            progressSteps: document.querySelectorAll('.progress-steps .step'),
            progressFill: document.getElementById('progress-fill'),
            btnPrevious: document.getElementById('btn-previous'),
            btnNext: document.getElementById('btn-next'),
            stepCounter: document.getElementById('step-counter'),
            configSummary: document.getElementById('config-summary'),
            designPreview: document.getElementById('design-preview'),
            currentTimePreview: document.getElementById('current-time-preview')
        };
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Navigation buttons
        this.elements.btnNext.addEventListener('click', () => this.nextStep());
        this.elements.btnPrevious.addEventListener('click', () => this.previousStep());

        // Step clicking navigation
        this.elements.progressSteps.forEach((step, index) => {
            step.addEventListener('click', () => this.goToStep(index + 1));
        });

        // Form change detection
        this.elements.form.addEventListener('input', this.debounce((e) => {
            this.handleFormChange(e);
        }, this.config.validationTimeout));

        // Setup type change
        document.querySelectorAll('input[name="setup_type"]').forEach(radio => {
            radio.addEventListener('change', (e) => this.handleSetupTypeChange(e.target.value));
        });

        // Theme selection
        document.querySelectorAll('input[name="theme"]').forEach(radio => {
            radio.addEventListener('change', (e) => this.handleThemeChange(e.target.value));
        });

        // Timezone preview update
        const timezoneSelect = document.getElementById('timezone');
        if (timezoneSelect) {
            timezoneSelect.addEventListener('change', () => this.updateTimezonePreview());
        }

        // Auto-save
        setInterval(() => this.autoSave(), this.config.autoSaveInterval);

        // Form submission
        this.elements.form.addEventListener('submit', (e) => this.handleSubmit(e));

        // Password strength
        const passwordInput = document.getElementById('admin_password');
        if (passwordInput) {
            passwordInput.addEventListener('input', () => this.updatePasswordStrength());
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    }

    /**
     * Initialize sub-systems
     */
    initializeSubSystems() {
        this.validators.init();
        this.previewSystem.init();
        this.locationHelper.init();
        this.updateTimezonePreview();
    }

    /**
     * Navigate to next step
     */
    async nextStep() {
        if (this.state.isSubmitting) return;

        // Validate current step
        const isValid = await this.validateCurrentStep();
        if (!isValid) {
            this.showValidationErrors();
            return;
        }

        if (this.config.currentStep < this.config.totalSteps) {
            this.config.currentStep++;
            this.updateUI();
            this.saveProgress();
        }
    }

    /**
     * Navigate to previous step
     */
    previousStep() {
        if (this.config.currentStep > 1) {
            this.config.currentStep--;
            this.updateUI();
        }
    }

    /**
     * Go to specific step
     */
    goToStep(stepNumber) {
        if (stepNumber >= 1 && stepNumber <= this.config.totalSteps) {
            this.config.currentStep = stepNumber;
            this.updateUI();
        }
    }

    /**
     * Update UI to reflect current step
     */
    updateUI() {
        // Update progress bar
        const progressPercent = (this.config.currentStep / this.config.totalSteps) * 100;
        this.elements.progressFill.style.width = `${progressPercent}%`;

        // Update progress steps
        this.elements.progressSteps.forEach((step, index) => {
            const stepNumber = index + 1;
            step.classList.remove('active', 'completed');
            
            if (stepNumber === this.config.currentStep) {
                step.classList.add('active');
            } else if (stepNumber < this.config.currentStep) {
                step.classList.add('completed');
            }
        });

        // Show/hide wizard steps
        this.elements.steps.forEach((step, index) => {
            step.classList.remove('active');
            if (index + 1 === this.config.currentStep) {
                step.classList.add('active');
            }
        });

        // Update navigation buttons
        this.elements.btnPrevious.disabled = this.config.currentStep === 1;
        
        if (this.config.currentStep === this.config.totalSteps) {
            this.elements.btnNext.textContent = 'Setup abschließen';
            this.elements.btnNext.innerHTML = '<i class="fas fa-check mr-2"></i>Setup abschließen';
        } else {
            this.elements.btnNext.innerHTML = 'Weiter<i class="fas fa-arrow-right ml-2"></i>';
        }

        // Update step counter
        this.elements.stepCounter.textContent = `Schritt ${this.config.currentStep} von ${this.config.totalSteps}`;

        // Update specific step content
        this.updateStepSpecificContent();
    }

    /**
     * Update step-specific content
     */
    updateStepSpecificContent() {
        switch (this.config.currentStep) {
            case 4: // Design step
                this.previewSystem.updateDesignPreview();
                break;
            case 7: // Final step
                this.updateConfigSummary();
                break;
        }
    }

    /**
     * Handle form changes
     */
    handleFormChange(event) {
        this.state.isDirty = true;
        const { name, value, type, checked } = event.target;
        
        if (type === 'checkbox') {
            this.state.formData.set(name, checked);
        } else if (type === 'radio') {
            if (checked) {
                this.state.formData.set(name, value);
            }
        } else {
            this.state.formData.set(name, value);
        }

        // Trigger validation for current field
        this.validateField(event.target);

        // Update live preview if relevant
        if (this.isDesignRelated(name)) {
            this.debounce(() => {
                this.previewSystem.updateDesignPreview();
            }, this.config.previewUpdateDelay)();
        }
    }

    /**
     * Check if field is design-related
     */
    isDesignRelated(fieldName) {
        const designFields = ['theme', 'header_style', 'card_style', 'show_animations', 'kiosk_font_scale'];
        return designFields.includes(fieldName);
    }

    /**
     * Handle setup type change
     */
    handleSetupTypeChange(setupType) {
        console.log(`🎯 Setup type changed to: ${setupType}`);
        
        // Adjust wizard based on setup type
        switch (setupType) {
            case 'quick':
                this.enableQuickMode();
                break;
            case 'detailed':
                this.enableDetailedMode();
                break;
            case 'advanced':
                this.enableAdvancedMode();
                break;
        }
    }

    /**
     * Enable quick setup mode
     */
    enableQuickMode() {
        // Hide advanced options
        document.querySelectorAll('.advanced-option').forEach(el => {
            el.style.display = 'none';
        });
        
        // Set sensible defaults
        this.setQuickDefaults();
    }

    /**
     * Enable detailed setup mode
     */
    enableDetailedMode() {
        // Show most options, hide only expert features
        document.querySelectorAll('.advanced-option').forEach(el => {
            el.style.display = 'block';
        });
        document.querySelectorAll('.expert-option').forEach(el => {
            el.style.display = 'none';
        });
    }

    /**
     * Enable advanced setup mode
     */
    enableAdvancedMode() {
        // Show all options
        document.querySelectorAll('.advanced-option, .expert-option').forEach(el => {
            el.style.display = 'block';
        });
    }

    /**
     * Set quick setup defaults
     */
    setQuickDefaults() {
        const defaults = {
            languages: ['de', 'th'],
            default_language: 'de',
            theme: 'medical',
            kiosk_modes: ['single', 'triple'],
            kiosk_refresh_interval: 120,
            enable_caching: true,
            auto_backup: 'daily'
        };

        Object.entries(defaults).forEach(([key, value]) => {
            const element = document.querySelector(`[name="${key}"]`);
            if (element) {
                if (element.type === 'checkbox' && Array.isArray(value)) {
                    // Handle multiple checkboxes
                    document.querySelectorAll(`[name="${key}"]`).forEach(cb => {
                        cb.checked = value.includes(cb.value);
                    });
                } else if (element.type === 'checkbox') {
                    element.checked = value;
                } else {
                    element.value = value;
                }
            }
        });
    }

    /**
     * Handle theme change
     */
    handleThemeChange(theme) {
        console.log(`🎨 Theme changed to: ${theme}`);
        this.previewSystem.updateThemePreview(theme);
        
        // Apply theme to wizard interface
        document.documentElement.setAttribute('data-wizard-theme', theme);
    }

    /**
     * Validate current step
     */
    async validateCurrentStep() {
        const currentStepElement = document.querySelector(`.wizard-step[data-step="${this.config.currentStep}"]`);
        const inputs = currentStepElement.querySelectorAll('input, select, textarea');
        
        let isValid = true;
        const validationPromises = [];

        inputs.forEach(input => {
            if (input.hasAttribute('required') || input.value.trim()) {
                validationPromises.push(this.validateField(input));
            }
        });

        const results = await Promise.all(validationPromises);
        results.forEach(result => {
            if (!result.valid) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * Validate individual field
     */
    async validateField(field) {
        const { name, value, type } = field;
        
        try {
            let result;
            
            switch (name) {
                case 'site_name':
                    result = this.validators.validateSiteName(value);
                    break;
                case 'contact_phone':
                    result = this.validators.validatePhone(value);
                    break;
                case 'contact_email':
                    result = this.validators.validateEmail(value);
                    break;
                case 'admin_password':
                    result = this.validators.validatePassword(value);
                    break;
                case 'latitude':
                case 'longitude':
                    result = this.validators.validateCoordinates(value);
                    break;
                default:
                    result = this.validators.validateGeneric(field);
            }

            this.updateFieldValidation(field, result);
            return result;

        } catch (error) {
            console.error('Validation error:', error);
            return { valid: false, message: 'Validierungsfehler' };
        }
    }

    /**
     * Update field validation UI
     */
    updateFieldValidation(field, result) {
        const formGroup = field.closest('.form-group');
        const existingError = formGroup.querySelector('.field-error');
        
        // Remove existing error
        if (existingError) {
            existingError.remove();
        }

        // Update field styling
        field.classList.remove('field-valid', 'field-invalid');
        
        if (result.valid) {
            field.classList.add('field-valid');
        } else {
            field.classList.add('field-invalid');
            
            // Add error message
            const errorElement = document.createElement('div');
            errorElement.className = 'field-error';
            errorElement.textContent = result.message;
            formGroup.appendChild(errorElement);
        }

        // Store validation result
        this.state.validationErrors.set(field.name, result);
    }

    /**
     * Show validation errors for current step
     */
    showValidationErrors() {
        const errors = Array.from(this.state.validationErrors.entries())
            .filter(([key, result]) => !result.valid)
            .map(([key, result]) => result.message);

        if (errors.length > 0) {
            this.showNotification(
                `Bitte korrigieren Sie folgende Fehler: ${errors.join(', ')}`,
                'error'
            );
        }
    }

    /**
     * Update timezone preview
     */
    updateTimezonePreview() {
        const timezoneSelect = document.getElementById('timezone');
        const previewElement = this.elements.currentTimePreview;
        
        if (!timezoneSelect || !previewElement) return;

        const timezone = timezoneSelect.value;
        
        const updateTime = () => {
            try {
                const now = new Date();
                const timeString = now.toLocaleTimeString('de-DE', {
                    timeZone: timezone,
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
                previewElement.textContent = timeString;
            } catch (error) {
                previewElement.textContent = 'Ungültige Zeitzone';
            }
        };

        updateTime();
        setInterval(updateTime, 1000);
    }

    /**
     * Update password strength indicator
     */
    updatePasswordStrength() {
        const passwordInput = document.getElementById('admin_password');
        const strengthIndicator = document.getElementById('password-strength');
        
        if (!passwordInput || !strengthIndicator) return;

        const password = passwordInput.value;
        const strength = this.validators.calculatePasswordStrength(password);
        
        strengthIndicator.className = `password-strength ${strength.level}`;
        strengthIndicator.querySelector('.strength-text').textContent = strength.text;
    }

    /**
     * Update configuration summary
     */
    updateConfigSummary() {
        if (!this.elements.configSummary) return;

        const config = this.gatherFormData();
        const summaryHTML = this.generateConfigSummaryHTML(config);
        this.elements.configSummary.innerHTML = summaryHTML;
    }

    /**
     * Generate configuration summary HTML
     */
    generateConfigSummaryHTML(config) {
        return `
            <div class="config-summary-grid">
                <div class="summary-card">
                    <h4><i class="fas fa-building text-thai-turquoise"></i> Standort</h4>
                    <p><strong>Name:</strong> ${config.site_name || 'Nicht festgelegt'}</p>
                    <p><strong>Telefon:</strong> ${config.contact_phone || 'Nicht festgelegt'}</p>
                    <p><strong>E-Mail:</strong> ${config.contact_email || 'Nicht festgelegt'}</p>
                </div>
                
                <div class="summary-card">
                    <h4><i class="fas fa-clock text-thai-turquoise"></i> Öffnungszeiten</h4>
                    <p><strong>Zeitzone:</strong> ${config.timezone || 'Asia/Bangkok'}</p>
                    <p><strong>Montag:</strong> ${this.formatDayHours('monday', config)}</p>
                    <p><strong>Freitag:</strong> ${this.formatDayHours('friday', config)}</p>
                </div>
                
                <div class="summary-card">
                    <h4><i class="fas fa-palette text-thai-turquoise"></i> Design</h4>
                    <p><strong>Theme:</strong> ${config.theme || 'medical'}</p>
                    <p><strong>Sprachen:</strong> ${this.getSelectedLanguages(config).join(', ')}</p>
                    <p><strong>Standard:</strong> ${config.default_language || 'de'}</p>
                </div>
                
                <div class="summary-card">
                    <h4><i class="fas fa-desktop text-thai-turquoise"></i> Kiosk</h4>
                    <p><strong>Modi:</strong> ${this.getSelectedKioskModes(config).join(', ')}</p>
                    <p><strong>Refresh:</strong> ${config.kiosk_refresh_interval || 120}s</p>
                    <p><strong>Vollbild:</strong> ${config.kiosk_fullscreen ? 'Ja' : 'Nein'}</p>
                </div>
            </div>
        `;
    }

    /**
     * Gather all form data
     */
    gatherFormData() {
        const formData = new FormData(this.elements.form);
        const config = {};
        
        for (const [key, value] of formData.entries()) {
            if (config[key]) {
                // Handle multiple values (checkboxes)
                if (!Array.isArray(config[key])) {
                    config[key] = [config[key]];
                }
                config[key].push(value);
            } else {
                config[key] = value;
            }
        }

        return config;
    }

    /**
     * Handle form submission
     */
    async handleSubmit(event) {
        event.preventDefault();
        
        if (this.state.isSubmitting) return;
        this.state.isSubmitting = true;

        try {
            // Final validation
            const isValid = await this.validateAllSteps();
            if (!isValid) {
                throw new Error('Validierung fehlgeschlagen');
            }

            // Show loading
            this.showLoading('Konfiguration wird gespeichert...');

            // Gather and prepare data
            const config = this.gatherFormData();
            const payload = this.preparePayload(config);

            // Submit to backend
            const response = await fetch('/admin/api/setup-wizard', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccess();
                // Clear saved progress
                localStorage.removeItem('wizard_progress');
                // Redirect to dashboard after success
                setTimeout(() => {
                    window.location.href = '/admin';
                }, 3000);
            } else {
                throw new Error(result.error || 'Setup fehlgeschlagen');
            }

        } catch (error) {
            console.error('Setup submission error:', error);
            this.showNotification(error.message, 'error');
        } finally {
            this.hideLoading();
            this.state.isSubmitting = false;
        }
    }

    /**
     * Validate all steps
     */
    async validateAllSteps() {
        for (let step = 1; step <= this.config.totalSteps; step++) {
            const stepElement = document.querySelector(`.wizard-step[data-step="${step}"]`);
            const inputs = stepElement.querySelectorAll('input[required], select[required], textarea[required]');
            
            for (const input of inputs) {
                const result = await this.validateField(input);
                if (!result.valid) {
                    this.goToStep(step);
                    this.showNotification(`Fehler in Schritt ${step}: ${result.message}`, 'error');
                    return false;
                }
            }
        }
        return true;
    }

    /**
     * Prepare payload for backend
     */
    preparePayload(config) {
        return {
            site: {
                name: config.site_name,
                subtitle: config.site_subtitle,
                languages: this.getSelectedLanguages(config),
                default_language: config.default_language,
                timezone: config.timezone
            },
            contact: {
                phone: config.contact_phone,
                email: config.contact_email
            },
            location: {
                address: config.address,
                latitude: parseFloat(config.latitude) || null,
                longitude: parseFloat(config.longitude) || null
            },
            theme: {
                name: config.theme,
                header_style: config.header_style,
                card_style: config.card_style,
                show_animations: config.show_animations === 'on',
                dark_mode_support: config.dark_mode_support === 'on',
                high_contrast: config.high_contrast === 'on'
            },
            kiosk: {
                modes: this.getSelectedKioskModes(config),
                refresh_interval: parseInt(config.kiosk_refresh_interval) || 120,
                font_scale: parseFloat(config.kiosk_font_scale) || 1.0,
                fullscreen: config.kiosk_fullscreen === 'on',
                disable_zoom: config.kiosk_disable_zoom === 'on',
                show_qr: config.kiosk_show_qr === 'on',
                hide_cursor: config.kiosk_hide_cursor === 'on'
            },
            system: {
                enable_caching: config.enable_caching === 'on',
                compress_responses: config.compress_responses === 'on',
                preload_resources: config.preload_resources === 'on',
                cache_duration: parseInt(config.cache_duration) || 60,
                enable_rate_limiting: config.enable_rate_limiting === 'on',
                enable_csrf_protection: config.enable_csrf_protection === 'on',
                log_admin_actions: config.log_admin_actions === 'on',
                auto_backup: config.auto_backup,
                auto_cleanup: config.auto_cleanup === 'on',
                health_monitoring: config.health_monitoring === 'on'
            },
            qr: {
                size: parseInt(config.qr_size) || 150,
                error_correction: config.qr_error_correction || 'M',
                include_logo: config.qr_include_logo === 'on'
            },
            hours: this.gatherHoursData(config),
            security: {
                admin_password: config.admin_password
            }
        };
    }

    /**
     * Auto-save progress
     */
    autoSave() {
        if (!this.state.isDirty) return;

        try {
            const progress = {
                currentStep: this.config.currentStep,
                formData: Object.fromEntries(this.state.formData),
                timestamp: Date.now()
            };

            localStorage.setItem('wizard_progress', JSON.stringify(progress));
            console.log('💾 Progress auto-saved');
            this.state.isDirty = false;
        } catch (error) {
            console.warn('Auto-save failed:', error);
        }
    }

    /**
     * Load saved progress
     */
    loadSavedProgress() {
        try {
            const saved = localStorage.getItem('wizard_progress');
            if (!saved) return;

            const progress = JSON.parse(saved);
            
            // Check if saved data is recent (within 24 hours)
            if (Date.now() - progress.timestamp > 24 * 60 * 60 * 1000) {
                localStorage.removeItem('wizard_progress');
                return;
            }

            // Restore form data
            Object.entries(progress.formData).forEach(([key, value]) => {
                const element = document.querySelector(`[name="${key}"]`);
                if (element) {
                    if (element.type === 'checkbox') {
                        element.checked = value === 'on' || value === true;
                    } else if (element.type === 'radio') {
                        if (element.value === value) {
                            element.checked = true;
                        }
                    } else {
                        element.value = value;
                    }
                }
            });

            // Restore step
            this.config.currentStep = progress.currentStep;
            
            console.log('📄 Progress restored from auto-save');
            this.showNotification('Fortschritt wiederhergestellt', 'info');

        } catch (error) {
            console.warn('Failed to load saved progress:', error);
            localStorage.removeItem('wizard_progress');
        }
    }

    /**
     * Save current progress
     */
    saveProgress() {
        this.state.isDirty = true;
        this.autoSave();
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 'Enter':
                    event.preventDefault();
                    this.nextStep();
                    break;
                case 'ArrowLeft':
                    event.preventDefault();
                    this.previousStep();
                    break;
                case 'ArrowRight':
                    event.preventDefault();
                    this.nextStep();
                    break;
                case 's':
                    event.preventDefault();
                    this.autoSave();
                    this.showNotification('Fortschritt gespeichert', 'success');
                    break;
            }
        }

        // Escape key
        if (event.key === 'Escape') {
            this.closeAllModals();
        }
    }

    /**
     * Utility methods
     */
    getSelectedLanguages(config) {
        const languages = [];
        if (config.languages) {
            if (Array.isArray(config.languages)) {
                return config.languages;
            } else {
                return [config.languages];
            }
        }
        
        // Fallback: check individual checkboxes
        document.querySelectorAll('input[name="languages"]:checked').forEach(cb => {
            languages.push(cb.value);
        });
        
        return languages.length > 0 ? languages : ['de', 'th', 'en'];
    }

    getSelectedKioskModes(config) {
        const modes = [];
        if (config.kiosk_modes) {
            if (Array.isArray(config.kiosk_modes)) {
                return config.kiosk_modes;
            } else {
                return [config.kiosk_modes];
            }
        }
        
        // Fallback: check individual checkboxes
        document.querySelectorAll('input[name="kiosk_modes"]:checked').forEach(cb => {
            modes.push(cb.value);
        });
        
        return modes.length > 0 ? modes : ['single', 'triple'];
    }

    formatDayHours(day, config) {
        const ranges = [];
        let rangeNum = 1;
        
        while (config[`${day}_start_${rangeNum}`] && config[`${day}_end_${rangeNum}`]) {
            ranges.push(`${config[`${day}_start_${rangeNum}`]}-${config[`${day}_end_${rangeNum}`]}`);
            rangeNum++;
        }
        
        return ranges.length > 0 ? ranges.join(', ') : 'Geschlossen';
    }

    gatherHoursData(config) {
        const hours = {};
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        
        days.forEach(day => {
            const ranges = [];
            let rangeNum = 1;
            
            while (config[`${day}_start_${rangeNum}`] && config[`${day}_end_${rangeNum}`]) {
                ranges.push(`${config[`${day}_start_${rangeNum}`]}-${config[`${day}_end_${rangeNum}`]}`);
                rangeNum++;
            }
            
            hours[day] = ranges;
        });
        
        return hours;
    }

    /**
     * Show success message
     */
    showSuccess() {
        const successHTML = `
            <div class="success-overlay">
                <div class="success-content">
                    <i class="fas fa-check-circle text-6xl text-green-500 mb-4"></i>
                    <h2 class="text-3xl font-bold text-gray-800 mb-4">Setup erfolgreich!</h2>
                    <p class="text-xl text-gray-600 mb-6">Ihr QR-Info-Portal ist jetzt einsatzbereit.</p>
                    <div class="success-actions">
                        <a href="/admin" class="btn btn-primary btn-lg">
                            <i class="fas fa-tachometer-alt mr-2"></i>Zum Dashboard
                        </a>
                        <a href="/" target="_blank" class="btn btn-outline btn-lg">
                            <i class="fas fa-external-link-alt mr-2"></i>Portal anzeigen
                        </a>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', successHTML);
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `wizard-notification notification-${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        notification.innerHTML = `
            <div class="notification-content">
                <i class="${icons[type]}"></i>
                <span>${message}</span>
                <button onclick="this.closest('.wizard-notification').remove()">×</button>
            </div>
        `;

        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    /**
     * Show loading overlay
     */
    showLoading(message = 'Wird geladen...') {
        const loadingHTML = `
            <div class="wizard-loading-overlay" id="wizard-loading">
                <div class="loading-content">
                    <div class="loading-spinner"></div>
                    <p>${message}</p>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', loadingHTML);
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        const loading = document.getElementById('wizard-loading');
        if (loading) {
            loading.remove();
        }
    }

    /**
     * Close all modals
     */
    closeAllModals() {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    /**
     * Debounce utility
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

/**
 * VALIDATION ENGINE
 * Handles all form validation logic
 */
class ValidationEngine {
    init() {
        console.log('🔍 Validation Engine initialized');
    }

    validateSiteName(value) {
        if (!value || value.trim().length < 3) {
            return { valid: false, message: 'Name muss mindestens 3 Zeichen haben' };
        }
        if (value.length > 100) {
            return { valid: false, message: 'Name darf maximal 100 Zeichen haben' };
        }
        return { valid: true };
    }

    validatePhone(value) {
        if (!value || value.trim().length === 0) {
            return { valid: false, message: 'Telefonnummer ist erforderlich' };
        }
        
        // Basic phone validation (international format)
        const phoneRegex = /^\+\d{1,3}[\s\d\-\(\)]{8,20}$/;
        if (!phoneRegex.test(value)) {
            return { valid: false, message: 'Ungültiges Telefonnummer-Format (z.B. +66 123 456 789)' };
        }
        
        return { valid: true };
    }

    validateEmail(value) {
        if (!value || value.trim().length === 0) {
            return { valid: false, message: 'E-Mail-Adresse ist erforderlich' };
        }
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            return { valid: false, message: 'Ungültige E-Mail-Adresse' };
        }
        
        return { valid: true };
    }

    validatePassword(value) {
        if (!value || value.length < 8) {
            return { valid: false, message: 'Passwort muss mindestens 8 Zeichen haben' };
        }
        
        const hasUpper = /[A-Z]/.test(value);
        const hasLower = /[a-z]/.test(value);
        const hasNumber = /\d/.test(value);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(value);
        
        const criteria = [hasUpper, hasLower, hasNumber, hasSpecial];
        const strength = criteria.filter(Boolean).length;
        
        if (strength < 3) {
            return { valid: false, message: 'Passwort muss Groß-/Kleinbuchstaben, Zahlen und Sonderzeichen enthalten' };
        }
        
        return { valid: true };
    }

    calculatePasswordStrength(password) {
        if (!password) {
            return { level: 'none', text: 'Passwort eingeben' };
        }

        const checks = {
            length: password.length >= 8,
            upper: /[A-Z]/.test(password),
            lower: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        const score = Object.values(checks).filter(Boolean).length;

        if (score < 2) return { level: 'weak', text: 'Schwach' };
        if (score < 3) return { level: 'fair', text: 'Ausreichend' };
        if (score < 4) return { level: 'good', text: 'Gut' };
        return { level: 'strong', text: 'Stark' };
    }

    validateCoordinates(value) {
        if (!value) return { valid: true }; // Optional field
        
        const coord = parseFloat(value);
        if (isNaN(coord)) {
            return { valid: false, message: 'Koordinate muss eine Zahl sein' };
        }
        
        return { valid: true };
    }

    validateGeneric(field) {
        if (field.hasAttribute('required') && !field.value.trim()) {
            return { valid: false, message: 'Dieses Feld ist erforderlich' };
        }
        
        if (field.type === 'email' && field.value) {
            return this.validateEmail(field.value);
        }
        
        if (field.type === 'tel' && field.value) {
            return this.validatePhone(field.value);
        }
        
        return { valid: true };
    }
}

/**
 * LIVE PREVIEW SYSTEM
 * Handles real-time preview of design changes
 */
class LivePreviewSystem {
    init() {
        console.log('👁️ Live Preview System initialized');
        this.previewFrame = null;
    }

    updateDesignPreview() {
        const previewContainer = document.getElementById('design-preview');
        if (!previewContainer) return;

        const theme = document.querySelector('input[name="theme"]:checked')?.value || 'medical';
        const headerStyle = document.getElementById('header_style')?.value || 'gradient';
        const cardStyle = document.getElementById('card_style')?.value || 'rounded';

        previewContainer.innerHTML = this.generatePreviewHTML(theme, headerStyle, cardStyle);
    }

    generatePreviewHTML(theme, headerStyle, cardStyle) {
        const themeColors = {
            medical: { primary: '#00A86B', secondary: '#40E0D0', accent: '#FF7F50' },
            thai: { primary: '#FFD700', secondary: '#FF7F50', accent: '#40E0D0' },
            modern: { primary: '#667EEA', secondary: '#764BA2', accent: '#F093FB' },
            nature: { primary: '#56AB2F', secondary: '#A8E6CF', accent: '#7F8C8D' }
        };

        const colors = themeColors[theme];

        return `
            <div class="preview-mockup">
                <div class="preview-header" style="background: linear-gradient(135deg, ${colors.primary}, ${colors.secondary});">
                    <div class="preview-logo"></div>
                    <div class="preview-title">Labor Pattaya</div>
                </div>
                <div class="preview-content">
                    <div class="preview-card ${cardStyle}" style="border-left: 4px solid ${colors.primary};">
                        <div class="preview-status" style="background: ${colors.primary};"></div>
                        <div class="preview-text"></div>
                    </div>
                    <div class="preview-card ${cardStyle}">
                        <div class="preview-hours"></div>
                    </div>
                </div>
            </div>
        `;
    }

    updateThemePreview(theme) {
        // Apply theme classes to wizard for immediate feedback
        document.body.className = `${document.body.className.replace(/theme-\w+/g, '')} theme-${theme}`;
    }
}

/**
 * LOCATION HELPER
 * Handles geolocation and map integration
 */
class LocationHelper {
    init() {
        console.log('📍 Location Helper initialized');
    }

    getCurrentLocation() {
        if (!navigator.geolocation) {
            alert('Geolocation wird von diesem Browser nicht unterstützt');
            return;
        }

        const options = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        };

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude.toFixed(6);
                const lng = position.coords.longitude.toFixed(6);
                
                document.getElementById('latitude').value = lat;
                document.getElementById('longitude').value = lng;
                
                window.wizardController.showNotification(
                    `Position erfasst: ${lat}, ${lng}`,
                    'success'
                );
            },
            (error) => {
                let message = 'Fehler beim Abrufen der Position';
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        message = 'Standortzugriff verweigert';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message = 'Position nicht verfügbar';
                        break;
                    case error.TIMEOUT:
                        message = 'Zeitüberschreitung bei Positionsabfrage';
                        break;
                }
                window.wizardController.showNotification(message, 'error');
            },
            options
        );
    }
}

// Global functions for template integration
window.getCurrentLocation = () => {
    window.wizardController.locationHelper.getCurrentLocation();
};

window.openMapSelector = () => {
    const modal = document.getElementById('map-modal');
    modal.classList.add('active');
    // Initialize map here (Google Maps or OpenStreetMap)
};

window.closeMapModal = () => {
    const modal = document.getElementById('map-modal');
    modal.classList.remove('active');
};

window.confirmMapSelection = () => {
    // Get selected coordinates from map
    window.closeMapModal();
};

window.addTimeRange = (day) => {
    const container = document.getElementById(`${day}_times`);
    const timeRanges = container.querySelectorAll('.time-range').length;
    
    const newRange = document.createElement('div');
    newRange.className = 'time-range';
    newRange.innerHTML = `
        <input type="time" name="${day}_start_${timeRanges + 1}">
        <span class="time-separator">bis</span>
        <input type="time" name="${day}_end_${timeRanges + 1}">
        <button type="button" class="btn-remove-time" onclick="removeTimeRange(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(newRange);
};

window.removeTimeRange = (button) => {
    button.closest('.time-range').remove();
};

window.addException = () => {
    const container = document.getElementById('exceptions-container');
    const exceptionCount = container.children.length;
    
    const newException = document.createElement('div');
    newException.className = 'exception-item';
    newException.innerHTML = `
        <div class="exception-form">
            <div class="form-grid">
                <div class="form-group">
                    <label>Datum</label>
                    <input type="date" name="exception_date_${exceptionCount}">
                </div>
                <div class="form-group">
                    <label>Grund</label>
                    <input type="text" name="exception_note_${exceptionCount}" placeholder="z.B. Feiertag, Fortbildung">
                </div>
            </div>
            <div class="toggle-option">
                <input type="checkbox" name="exception_closed_${exceptionCount}">
                <span class="toggle-label">Geschlossen</span>
            </div>
            <button type="button" class="btn btn-outline btn-sm" onclick="this.closest('.exception-item').remove()">
                <i class="fas fa-trash mr-2"></i>Entfernen
            </button>
        </div>
    `;
    
    container.appendChild(newException);
};

window.applyDisplayPreset = (preset) => {
    const presets = {
        'monitor-24': { font_scale: '1.0', refresh_interval: 120 },
        'tv-32': { font_scale: '1.2', refresh_interval: 180 },
        'tv-43-4k': { font_scale: '1.5', refresh_interval: 300 },
        'tablet': { font_scale: '0.9', refresh_interval: 60 }
    };

    const settings = presets[preset];
    if (settings) {
        Object.entries(settings).forEach(([key, value]) => {
            const element = document.querySelector(`[name="kiosk_${key}"]`);
            if (element) {
                element.value = value;
            }
        });
        
        window.wizardController.showNotification(`${preset} Einstellungen angewendet`, 'success');
    }
};

window.openPreview = () => {
    const previewUrl = `${window.location.origin}/?preview=true`;
    window.open(previewUrl, '_blank', 'width=1200,height=800');
};

window.downloadConfig = async () => {
    try {
        const config = window.wizardController.gatherFormData();
        const payload = window.wizardController.preparePayload(config);
        
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `qr-portal-config-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        window.wizardController.showNotification('Konfiguration heruntergeladen', 'success');
    } catch (error) {
        console.error('Download error:', error);
        window.wizardController.showNotification('Fehler beim Download', 'error');
    }
};

window.resetLogo = () => {
    document.getElementById('logo_upload').value = '';
    document.querySelector('.logo-preview .logo-placeholder').innerHTML = `
        <i class="fas fa-stethoscope text-4xl text-gray-400"></i>
        <p>Standard-Icon</p>
    `;
};

// Initialize wizard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.wizardController = new SetupWizardController();
});

// Add CSS for wizard-specific components
const wizardStyles = document.createElement('style');
wizardStyles.textContent = `
    .field-valid {
        border-color: #10B981 !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
    }
    
    .field-invalid {
        border-color: #EF4444 !important;
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
    }
    
    .field-error {
        color: #EF4444;
        font-size: 0.875rem;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .field-error::before {
        content: '⚠️';
    }
    
    .wizard-notification {
        position: fixed;
        top: 1rem;
        right: 1rem;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        color: white;
        font-weight: 600;
        z-index: 1000;
        transform: translateX(100%);
        transition: transform 0.3s ease-out;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        max-width: 400px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    }
    
    .wizard-notification.show {
        transform: translateX(0);
    }
    
    .notification-success { background: #10B981; }
    .notification-error { background: #EF4444; }
    .notification-warning { background: #F59E0B; }
    .notification-info { background: #3B82F6; }
    
    .wizard-loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(4px);
    }
    
    .loading-content {
        text-align: center;
        color: #374151;
    }
    
    .loading-spinner {
        width: 3rem;
        height: 3rem;
        border: 4px solid #E5E7EB;
        border-top: 4px solid #40E0D0;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .success-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.95);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(8px);
    }
    
    .success-content {
        text-align: center;
        max-width: 500px;
        padding: 3rem;
        background: white;
        border-radius: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }
    
    .success-actions {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .config-summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
    }
    
    .summary-card {
        background: white;
        border: 2px solid #E5E7EB;
        border-radius: 1rem;
        padding: 1.5rem;
        text-align: left;
    }
    
    .summary-card h4 {
        font-size: 1.125rem;
        font-weight: 700;
        color: #374151;
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .summary-card p {
        margin: 0.5rem 0;
        color: #6B7280;
    }
    
    .preview-mockup {
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
        border: 2px solid #E5E7EB;
        border-radius: 1rem;
        overflow: hidden;
        background: white;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    
    .preview-header {
        height: 60px;
        display: flex;
        align-items: center;
        padding: 0 1rem;
        gap: 1rem;
        color: white;
    }
    
    .preview-logo {
        width: 30px;
        height: 30px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 0.5rem;
    }
    
    .preview-title {
        font-weight: bold;
        font-size: 1.125rem;
    }
    
    .preview-content {
        padding: 1rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .preview-card {
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 1rem;
        background: #F9FAFB;
    }
    
    .preview-card.rounded { border-radius: 1rem; }
    .preview-card.sharp { border-radius: 0; }
    .preview-card.minimal { border: none; background: transparent; }
    .preview-card.elevated { box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); }
    
    .preview-status {
        height: 20px;
        border-radius: 0.25rem;
        margin-bottom: 0.5rem;
    }
    
    .preview-text {
        height: 40px;
        background: #E5E7EB;
        border-radius: 0.25rem;
    }
    
    .preview-hours {
        height: 60px;
        background: #E5E7EB;
        border-radius: 0.25rem;
    }
`;
document.head.appendChild(wizardStyles);