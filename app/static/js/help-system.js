/**
 * QR Info Portal - Interactive Help System
 * Provides contextual help, tooltips, search, and getting started wizard
 */

class HelpSystem {
    constructor() {
        this.currentLanguage = document.documentElement.lang || 'de';
        this.helpData = null;
        this.currentPage = this.detectCurrentPage();
        this.activeTooltip = null;
        this.wizardStep = 0;
        this.isFirstTime = this.checkFirstTimeUser();
        
        this.init();
    }

    async init() {
        try {
            await this.loadHelpData();
            this.createHelpElements();
            this.attachEventListeners();
            this.initializeTooltips();
            
            // Show getting started wizard for first-time users
            if (this.isFirstTime && this.currentPage.includes('admin')) {
                setTimeout(() => this.showGettingStartedWizard(), 1000);
            }
            
            // Show contextual help based on URL parameters
            this.checkContextualHelp();
            
        } catch (error) {
            console.error('Help System initialization failed:', error);
        }
    }

    async loadHelpData() {
        try {
            // Try to load from help API endpoint first, then fallback to static files
            const response = await fetch(`/help/data/${this.currentLanguage}`);
            if (response.ok) {
                this.helpData = await response.json();
                return;
            }
            
            // Fallback to static files
            const staticResponse = await fetch(`/static/help/help_${this.currentLanguage}.json`);
            if (!staticResponse.ok) {
                throw new Error(`Failed to load help data: ${staticResponse.status}`);
            }
            this.helpData = await staticResponse.json();
        } catch (error) {
            console.warn(`Fallback to default help data for ${this.currentLanguage}:`, error);
            this.helpData = this.getDefaultHelpData();
        }
    }

    detectCurrentPage() {
        const path = window.location.pathname;
        const search = window.location.search;
        
        if (path.includes('/admin')) {
            if (path.includes('/status')) return 'admin_status';
            if (path.includes('/hours')) return 'admin_hours';
            if (path.includes('/announcements')) return 'admin_announcements';
            if (path.includes('/settings')) return 'admin_settings';
            return 'admin_dashboard';
        } else if (path.includes('/kiosk')) {
            return 'kiosk';
        } else if (path.includes('/week')) {
            return 'week';
        } else if (path.includes('/month')) {
            return 'month';
        } else {
            return 'home';
        }
    }

    createHelpElements() {
        // Help button
        const helpButton = document.createElement('button');
        helpButton.className = 'help-button';
        helpButton.innerHTML = '<i class="fas fa-question"></i>';
        helpButton.title = this.getText('help_button_title', 'Hilfe öffnen');
        helpButton.addEventListener('click', () => this.toggleHelpPanel());
        document.body.appendChild(helpButton);

        // Help panel
        const helpPanel = document.createElement('div');
        helpPanel.className = 'help-panel';
        helpPanel.id = 'helpPanel';
        helpPanel.innerHTML = this.createHelpPanelContent();
        document.body.appendChild(helpPanel);

        // Tooltip container
        const tooltipContainer = document.createElement('div');
        tooltipContainer.className = 'help-tooltip';
        tooltipContainer.id = 'helpTooltip';
        document.body.appendChild(tooltipContainer);

        // Getting started wizard
        const wizard = document.createElement('div');
        wizard.className = 'help-wizard';
        wizard.id = 'helpWizard';
        wizard.innerHTML = this.createWizardContent();
        document.body.appendChild(wizard);

        // Contextual help container
        const contextualHelp = document.createElement('div');
        contextualHelp.className = 'help-contextual';
        contextualHelp.id = 'helpContextual';
        document.body.appendChild(contextualHelp);
    }

    createHelpPanelContent() {
        const pageHelp = this.helpData?.pages?.[this.currentPage] || {};
        const sections = pageHelp.sections || [];
        const quickActions = pageHelp.quick_actions || [];
        
        return `
            <div class="help-panel-header">
                <h3><i class="fas fa-question-circle mr-2"></i>${pageHelp.title || 'Hilfe'}</h3>
                <button class="help-close-btn" onclick="helpSystem.toggleHelpPanel()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="help-panel-content">
                <!-- Search -->
                <div class="help-search">
                    <i class="fas fa-search help-search-icon"></i>
                    <input type="text" class="help-search-input" placeholder="${this.getText('search_help', 'Hilfe durchsuchen...')}" 
                           onkeyup="helpSystem.searchHelp(this.value)">
                    <div class="help-search-results" id="helpSearchResults"></div>
                </div>

                <!-- Page Description -->
                ${pageHelp.description ? `<div class="mb-4 text-gray-600 text-sm">${pageHelp.description}</div>` : ''}

                <!-- Quick Actions -->
                ${quickActions.length > 0 ? `
                    <div class="help-quick-actions">
                        <h4 class="text-sm font-semibold text-gray-700 mb-2">${this.getText('quick_actions', 'Schnellzugriffe')}</h4>
                        ${quickActions.map(action => `
                            <div class="help-quick-action" onclick="helpSystem.executeQuickAction('${action.title}')">
                                <div class="help-quick-action-icon">⚡</div>
                                <div class="help-quick-action-text">
                                    <div class="font-medium">${action.title}</div>
                                    <div class="text-xs text-gray-500">${action.description}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}

                <!-- Help Sections -->
                <div class="help-sections">
                    ${sections.map((section, index) => `
                        <div class="help-section ${index === 0 ? 'active' : ''}" data-section="${index}">
                            <div class="help-section-header" onclick="helpSystem.toggleSection(${index})">
                                <span>${section.title}</span>
                                <i class="fas fa-chevron-down help-section-toggle"></i>
                            </div>
                            <div class="help-section-content">
                                <div class="prose prose-sm text-gray-700">
                                    ${this.formatHelpContent(section.content)}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <!-- Getting Started Button -->
                <div class="mt-6 pt-4 border-t border-gray-200">
                    <button class="w-full btn-enhanced bg-thai-turquoise text-white" onclick="helpSystem.showGettingStartedWizard()">
                        <i class="fas fa-play mr-2"></i>${this.getText('getting_started', 'Erste Schritte')}
                    </button>
                </div>

                <!-- FAQ Link -->
                <div class="mt-4 text-center">
                    <a href="/help/faq" class="text-sm text-thai-turquoise hover:underline">
                        <i class="fas fa-question-circle mr-1"></i>${this.getText('view_faq', 'Häufige Fragen anzeigen')}
                    </a>
                </div>
            </div>
        `;
    }

    createWizardContent() {
        const userType = this.currentPage.includes('admin') ? 'admin' : 'visitor';
        const guide = this.helpData?.quick_start?.[userType] || {};
        const steps = guide.steps || [];

        return `
            <div class="help-wizard-content">
                <div class="help-wizard-header">
                    <div class="help-wizard-title">${guide.title || 'Schnellstart'}</div>
                    <div class="help-wizard-subtitle">${this.getText('wizard_subtitle', 'Lassen Sie sich durch die wichtigsten Funktionen führen')}</div>
                </div>
                
                <div class="help-wizard-steps">
                    ${steps.map((step, index) => `
                        <div class="help-wizard-step ${index === 0 ? 'active' : ''}" data-step="${index}">
                            <div class="help-wizard-step-content">
                                <div class="help-wizard-step-title">
                                    <div class="help-wizard-step-number">${index + 1}</div>
                                    ${step.title}
                                </div>
                                <div class="help-wizard-step-description">${step.description}</div>
                                ${step.items ? `
                                    <ul class="help-wizard-step-items">
                                        ${step.items.map(item => `<li>${item}</li>`).join('')}
                                    </ul>
                                ` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <div class="help-wizard-actions">
                    <button class="help-wizard-button help-wizard-button-secondary" onclick="helpSystem.closeWizard()">
                        ${this.getText('skip', 'Überspringen')}
                    </button>
                    
                    <div class="help-wizard-progress">
                        <span id="wizardProgressText">1 / ${steps.length}</span>
                        <div class="help-wizard-progress-dots">
                            ${steps.map((_, index) => `
                                <div class="help-wizard-progress-dot ${index === 0 ? 'active' : ''}"></div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <button class="help-wizard-button help-wizard-button-primary" onclick="helpSystem.nextWizardStep()">
                        ${this.getText('next', 'Weiter')}
                    </button>
                </div>
            </div>
        `;
    }

    formatHelpContent(content) {
        if (!content) return '';
        
        // Convert markdown-like formatting to HTML
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n•/g, '<br>•')
            .replace(/\n([0-9]+\.)/g, '<br>$1')
            .replace(/\n/g, '<br>');
    }

    attachEventListeners() {
        // Enhanced keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Escape key to close panels
            if (e.key === 'Escape') {
                this.closeAllPanels();
                return;
            }
            
            // F1 to show getting started wizard
            if (e.key === 'F1') {
                e.preventDefault();
                this.showGettingStartedWizard();
                return;
            }
            
            // Alt+H to toggle help panel
            if (e.altKey && e.key.toLowerCase() === 'h') {
                e.preventDefault();
                this.toggleHelpPanel();
                return;
            }
            
            // Ctrl+? or ? (when input not focused) for keyboard shortcuts help
            if ((e.ctrlKey && e.key === '?') || 
                (e.key === '?' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName))) {
                e.preventDefault();
                this.showKeyboardShortcuts();
                return;
            }
            
            // Ctrl+/ to focus search (when help panel is open)
            if (e.ctrlKey && e.key === '/') {
                const helpPanel = document.getElementById('helpPanel');
                if (helpPanel && helpPanel.classList.contains('active')) {
                    e.preventDefault();
                    const searchInput = document.querySelector('.help-search-input');
                    if (searchInput) {
                        searchInput.focus();
                        searchInput.select();
                    }
                }
                return;
            }
        });

        // Click outside to close panels
        document.addEventListener('click', (e) => {
            const helpPanel = document.getElementById('helpPanel');
            const helpButton = document.querySelector('.help-button');
            
            if (helpPanel && helpButton && 
                !helpPanel.contains(e.target) && 
                !helpButton.contains(e.target) &&
                !e.target.closest('.help-wizard') &&
                !e.target.closest('.help-contextual')) {
                this.closeHelpPanel();
            }
        });

        // Handle dynamic content changes
        const observer = new MutationObserver(() => {
            this.initializeTooltips();
        });
        observer.observe(document.body, { childList: true, subtree: true });
        
        // Show keyboard shortcut hints on first visit
        if (!localStorage.getItem('help_shortcuts_seen')) {
            setTimeout(() => {
                this.showKeyboardShortcutHint();
                localStorage.setItem('help_shortcuts_seen', 'true');
            }, 3000);
        }
    }

    initializeTooltips() {
        // Find all elements with data-help-tooltip
        const elements = document.querySelectorAll('[data-help-tooltip]');
        
        elements.forEach(element => {
            element.addEventListener('mouseenter', (e) => this.showTooltip(e));
            element.addEventListener('mouseleave', () => this.hideTooltip());
            element.addEventListener('focus', (e) => this.showTooltip(e));
            element.addEventListener('blur', () => this.hideTooltip());
        });

        // Auto-add tooltips based on help data
        this.addAutomaticTooltips();
    }

    addAutomaticTooltips() {
        const pageHelp = this.helpData?.pages?.[this.currentPage];
        const tooltips = pageHelp?.tooltips || {};

        Object.entries(tooltips).forEach(([elementId, tooltipText]) => {
            const element = document.getElementById(elementId) || document.querySelector(`[data-help-id="${elementId}"]`);
            if (element && !element.getAttribute('data-help-tooltip')) {
                element.setAttribute('data-help-tooltip', tooltipText);
                element.addEventListener('mouseenter', (e) => this.showTooltip(e));
                element.addEventListener('mouseleave', () => this.hideTooltip());
            }
        });
    }

    showTooltip(event) {
        const element = event.target;
        const tooltipText = element.getAttribute('data-help-tooltip');
        
        if (!tooltipText) return;

        const tooltip = document.getElementById('helpTooltip');
        tooltip.textContent = tooltipText;
        tooltip.className = 'help-tooltip show';

        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let top, left, position = 'top';

        // Try to position tooltip above element
        if (rect.top > tooltipRect.height + 10) {
            top = rect.top - tooltipRect.height - 10;
            position = 'top';
        } else if (window.innerHeight - rect.bottom > tooltipRect.height + 10) {
            top = rect.bottom + 10;
            position = 'bottom';
        } else if (rect.left > tooltipRect.width + 10) {
            top = rect.top + (rect.height - tooltipRect.height) / 2;
            left = rect.left - tooltipRect.width - 10;
            position = 'left';
        } else {
            top = rect.top + (rect.height - tooltipRect.height) / 2;
            left = rect.right + 10;
            position = 'right';
        }

        if (position === 'top' || position === 'bottom') {
            left = rect.left + (rect.width - tooltipRect.width) / 2;
            left = Math.max(10, Math.min(left, window.innerWidth - tooltipRect.width - 10));
        }

        tooltip.style.top = `${top + window.scrollY}px`;
        tooltip.style.left = `${left + window.scrollX}px`;
        tooltip.className = `help-tooltip show ${position}`;

        this.activeTooltip = tooltip;
    }

    hideTooltip() {
        if (this.activeTooltip) {
            this.activeTooltip.classList.remove('show');
            this.activeTooltip = null;
        }
    }

    toggleHelpPanel() {
        const panel = document.getElementById('helpPanel');
        panel.classList.toggle('active');
    }

    closeHelpPanel() {
        const panel = document.getElementById('helpPanel');
        panel.classList.remove('active');
    }

    toggleSection(sectionIndex) {
        const section = document.querySelector(`.help-section[data-section="${sectionIndex}"]`);
        section.classList.toggle('active');
    }

    async searchHelp(query) {
        if (!query.trim()) {
            document.getElementById('helpSearchResults').innerHTML = '';
            return;
        }

        try {
            // Use server-side search API for better results
            const response = await fetch(`/help/search?q=${encodeURIComponent(query)}`);
            if (response.ok) {
                const data = await response.json();
                this.displaySearchResults(data.results || []);
            } else {
                // Fallback to client-side search
                const results = this.performSearch(query);
                this.displaySearchResults(results);
            }
        } catch (error) {
            console.warn('Search API failed, using local search:', error);
            const results = this.performSearch(query);
            this.displaySearchResults(results);
        }
    }

    performSearch(query) {
        const results = [];
        const queryLower = query.toLowerCase();

        // Search through current page content
        const pageHelp = this.helpData?.pages?.[this.currentPage];
        if (pageHelp) {
            if (pageHelp.title?.toLowerCase().includes(queryLower)) {
                results.push({
                    type: 'page',
                    title: pageHelp.title,
                    excerpt: pageHelp.description,
                    relevance: 'high'
                });
            }

            pageHelp.sections?.forEach(section => {
                if (section.title?.toLowerCase().includes(queryLower) || 
                    section.content?.toLowerCase().includes(queryLower)) {
                    results.push({
                        type: 'section',
                        title: section.title,
                        excerpt: section.content?.substring(0, 100) + '...',
                        relevance: 'medium'
                    });
                }
            });
        }

        // Search through FAQs
        this.helpData?.faqs?.forEach(faq => {
            if (faq.question?.toLowerCase().includes(queryLower) || 
                faq.answer?.toLowerCase().includes(queryLower)) {
                results.push({
                    type: 'faq',
                    title: faq.question,
                    excerpt: faq.answer?.substring(0, 100) + '...',
                    relevance: 'high'
                });
            }
        });

        return results.slice(0, 5); // Limit results
    }

    displaySearchResults(results) {
        const container = document.getElementById('helpSearchResults');
        
        if (results.length === 0) {
            container.innerHTML = `<div class="p-4 text-center text-gray-500 text-sm">${this.getText('no_results', 'Keine Ergebnisse gefunden')}</div>`;
            return;
        }

        container.innerHTML = results.map(result => `
            <div class="help-search-result" onclick="helpSystem.selectSearchResult('${result.type}', '${result.title}')">
                <div class="help-search-result-title">${result.title}</div>
                <div class="help-search-result-excerpt">${result.excerpt}</div>
            </div>
        `).join('');
    }

    executeQuickAction(actionTitle) {
        // Handle different quick actions based on current page
        switch (actionTitle) {
            case 'Notfall-Schließung':
            case 'Emergency Closure':
            case 'ปิดฉุกเฉิน':
                this.showContextualHelp('emergency_closure');
                break;
            case 'Termin vereinbaren':
            case 'Make Appointment':
            case 'นัดหมายล่วงหน้า':
                window.open('tel:+66381234567');
                break;
            case 'Portal anzeigen':
            case 'View Portal':
            case 'ดูหน้าเว็บ':
                window.open('/', '_blank');
                break;
            default:
                console.log('Quick action:', actionTitle);
        }
    }

    showGettingStartedWizard() {
        const wizard = document.getElementById('helpWizard');
        wizard.classList.add('active');
        this.wizardStep = 0;
        this.updateWizardProgress();

        // Mark as not first time anymore
        localStorage.setItem('qr_portal_visited', 'true');
    }

    nextWizardStep() {
        const steps = document.querySelectorAll('.help-wizard-step');
        const totalSteps = steps.length;

        if (this.wizardStep < totalSteps - 1) {
            steps[this.wizardStep].classList.remove('active');
            this.wizardStep++;
            steps[this.wizardStep].classList.add('active');
            this.updateWizardProgress();
        } else {
            this.closeWizard();
        }
    }

    previousWizardStep() {
        const steps = document.querySelectorAll('.help-wizard-step');

        if (this.wizardStep > 0) {
            steps[this.wizardStep].classList.remove('active');
            this.wizardStep--;
            steps[this.wizardStep].classList.add('active');
            this.updateWizardProgress();
        }
    }

    updateWizardProgress() {
        const totalSteps = document.querySelectorAll('.help-wizard-step').length;
        const progressText = document.getElementById('wizardProgressText');
        const progressDots = document.querySelectorAll('.help-wizard-progress-dot');
        
        if (progressText) {
            progressText.textContent = `${this.wizardStep + 1} / ${totalSteps}`;
        }

        progressDots.forEach((dot, index) => {
            dot.classList.remove('active', 'completed');
            if (index < this.wizardStep) {
                dot.classList.add('completed');
            } else if (index === this.wizardStep) {
                dot.classList.add('active');
            }
        });

        // Update button text for last step
        const nextButton = document.querySelector('.help-wizard-button-primary');
        if (this.wizardStep === totalSteps - 1) {
            nextButton.textContent = this.getText('finish', 'Fertig');
        } else {
            nextButton.textContent = this.getText('next', 'Weiter');
        }
    }

    closeWizard() {
        const wizard = document.getElementById('helpWizard');
        wizard.classList.remove('active');
    }

    showContextualHelp(context) {
        const contextualHelp = this.helpData?.contextual?.[context];
        if (!contextualHelp) return;

        const container = document.getElementById('helpContextual');
        container.innerHTML = `
            <div class="flex items-start">
                <i class="fas fa-lightbulb help-contextual-icon"></i>
                <div class="flex-1">
                    <div class="font-medium">${contextualHelp.message}</div>
                    ${contextualHelp.description ? `<div class="mt-1 text-sm">${contextualHelp.description}</div>` : ''}
                    ${contextualHelp.tips ? `
                        <ul class="mt-2 text-sm space-y-1">
                            ${contextualHelp.tips.map(tip => `<li>${tip}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
                <button onclick="this.parentElement.parentElement.classList.remove('show')" class="ml-2">
                    <i class="fas fa-times text-gray-400 hover:text-gray-600"></i>
                </button>
            </div>
        `;
        container.classList.add('show');

        // Auto-hide after 10 seconds
        setTimeout(() => {
            container.classList.remove('show');
        }, 10000);
    }

    checkContextualHelp() {
        const urlParams = new URLSearchParams(window.location.search);
        const helpContext = urlParams.get('help');
        
        if (helpContext) {
            setTimeout(() => this.showContextualHelp(helpContext), 1000);
        }
    }

    checkFirstTimeUser() {
        return !localStorage.getItem('qr_portal_visited');
    }

    closeAllPanels() {
        this.closeHelpPanel();
        this.closeWizard();
        this.hideTooltip();
        
        const contextualHelp = document.getElementById('helpContextual');
        if (contextualHelp) {
            contextualHelp.classList.remove('show');
        }
    }

    getText(key, fallback) {
        // Simple text lookup - in production, this would use the same i18n system
        const texts = {
            'help_button_title': {
                'de': 'Hilfe öffnen',
                'th': 'เปิดความช่วยเหลือ',
                'en': 'Open Help'
            },
            'search_help': {
                'de': 'Hilfe durchsuchen...',
                'th': 'ค้นหาความช่วยเหลือ...',
                'en': 'Search help...'
            },
            'no_results': {
                'de': 'Keine Ergebnisse gefunden',
                'th': 'ไม่พบผลลัพธ์',
                'en': 'No results found'
            }
        };
        
        return texts[key]?.[this.currentLanguage] || fallback;
    }

    showKeyboardShortcuts() {
        const shortcuts = {
            'F1': 'Schnellstart-Assistent öffnen',
            'Alt + H': 'Hilfe-Panel umschalten', 
            'Escape': 'Alle Hilfe-Fenster schließen',
            '?': 'Tastaturkürzel anzeigen',
            'Strg + /': 'Suche fokussieren (wenn Hilfe offen)'
        };
        
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md mx-4 animate-bounce">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold">⌨️ Tastaturkürzel</h3>
                    <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="space-y-2">
                    ${Object.entries(shortcuts).map(([key, desc]) => `
                        <div class="flex justify-between">
                            <span class="bg-gray-100 px-2 py-1 rounded text-sm font-mono">${key}</span>
                            <span class="text-sm text-gray-600">${desc}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="mt-4 text-center">
                    <button onclick="this.closest('.fixed').remove()" class="btn-enhanced bg-thai-turquoise text-white">
                        Verstanden
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (modal.parentNode) modal.remove();
        }, 10000);
    }
    
    showKeyboardShortcutHint() {
        const hint = document.createElement('div');
        hint.className = 'fixed bottom-20 right-6 bg-thai-turquoise text-white px-4 py-2 rounded-lg shadow-lg z-40 animate-bounce';
        hint.innerHTML = `
            <div class="text-sm">
                💡 Drücken Sie <kbd class="bg-white text-thai-turquoise px-1 rounded">F1</kbd> für Hilfe!
                <button onclick="this.closest('.fixed').remove()" class="ml-2 text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(hint);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (hint.parentNode) {
                hint.style.transform = 'translateX(100%)';
                setTimeout(() => hint.remove(), 300);
            }
        }, 5000);
    }

    getDefaultHelpData() {
        return {
            pages: {
                home: {
                    title: "Hilfe",
                    description: "Willkommen beim QR Info Portal",
                    sections: [
                        {
                            title: "Grundlagen",
                            content: "Das Portal zeigt aktuelle Informationen über das Labor."
                        }
                    ]
                }
            },
            faqs: []
        };
    }
}

// Initialize help system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.helpSystem = new HelpSystem();
});

// Utility function to highlight elements (for guided tours)
function highlightElement(selector, duration = 3000) {
    const element = document.querySelector(selector);
    if (element) {
        element.classList.add('help-highlight');
        setTimeout(() => {
            element.classList.remove('help-highlight');
        }, duration);
    }
}