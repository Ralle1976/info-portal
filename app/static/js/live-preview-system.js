/**
 * LIVE PREVIEW SYSTEM - SUB-AGENT 4
 * Parallel execution: Real-time preview of design changes
 */

class LivePreviewSystemAgent {
    constructor() {
        this.previewFrames = new Map();
        this.previewConfig = {
            updateDelay: 500,
            maxFrames: 3,
            themes: {
                medical: { primary: '#00A86B', secondary: '#40E0D0', accent: '#FF7F50' },
                thai: { primary: '#FFD700', secondary: '#FF7F50', accent: '#40E0D0' },
                modern: { primary: '#667EEA', secondary: '#764BA2', accent: '#F093FB' },
                nature: { primary: '#56AB2F', secondary: '#A8E6CF', accent: '#7F8C8D' }
            }
        };
        
        this.init();
    }

    init() {
        console.log('👁️ SUB-AGENT 4: Live Preview System started');
        this.createPreviewPanels();
        this.setupPreviewUpdates();
        this.initializePreviewFrames();
    }

    createPreviewPanels() {
        // Create design preview panel for step 4
        const designPreviewHTML = `
            <div class="live-preview-panel" id="design-preview-panel">
                <h3>Live-Vorschau</h3>
                
                <div class="preview-tabs">
                    <button type="button" class="preview-tab active" data-preview="desktop">
                        <i class="fas fa-desktop"></i> Desktop
                    </button>
                    <button type="button" class="preview-tab" data-preview="tablet">
                        <i class="fas fa-tablet-alt"></i> Tablet
                    </button>
                    <button type="button" class="preview-tab" data-preview="mobile">
                        <i class="fas fa-mobile-alt"></i> Mobile
                    </button>
                </div>
                
                <div class="preview-container">
                    <div class="preview-frame-container">
                        <iframe id="preview-frame-desktop" class="preview-frame active" 
                                src="about:blank" 
                                style="width: 1200px; height: 800px; transform: scale(0.4); transform-origin: top left;">
                        </iframe>
                        <iframe id="preview-frame-tablet" class="preview-frame" 
                                src="about:blank" 
                                style="width: 768px; height: 1024px; transform: scale(0.5); transform-origin: top left;">
                        </iframe>
                        <iframe id="preview-frame-mobile" class="preview-frame" 
                                src="about:blank" 
                                style="width: 375px; height: 667px; transform: scale(0.7); transform-origin: top left;">
                        </iframe>
                    </div>
                    
                    <div class="preview-loading" id="preview-loading">
                        <div class="loading-spinner"></div>
                        <p>Vorschau wird aktualisiert...</p>
                    </div>
                </div>
                
                <div class="preview-controls">
                    <button type="button" class="btn btn-outline btn-sm" onclick="livePreview.refreshPreviews()">
                        <i class="fas fa-sync mr-2"></i>Aktualisieren
                    </button>
                    <button type="button" class="btn btn-outline btn-sm" onclick="livePreview.openFullPreview()">
                        <i class="fas fa-external-link-alt mr-2"></i>Vollbild
                    </button>
                    <button type="button" class="btn btn-outline btn-sm" onclick="livePreview.exportPreview()">
                        <i class="fas fa-download mr-2"></i>Screenshot
                    </button>
                </div>
            </div>
        `;

        const designStep = document.querySelector('.wizard-step[data-step="4"] .design-preview');
        if (designStep) {
            designStep.innerHTML = designPreviewHTML;
        }

        // Create kiosk preview panel for step 5
        const kioskPreviewHTML = `
            <div class="kiosk-preview-panel" id="kiosk-preview-panel">
                <h3>Kiosk-Modi Vorschau</h3>
                
                <div class="kiosk-preview-modes">
                    <div class="kiosk-preview-item" data-mode="single">
                        <h4>Single Mode</h4>
                        <div class="kiosk-preview-mockup single-mockup">
                            <div class="mock-header">Labor Pattaya</div>
                            <div class="mock-status-large">GEÖFFNET</div>
                            <div class="mock-time-large">14:30:45</div>
                            <div class="mock-hours-today">08:30-12:00, 13:00-16:00</div>
                        </div>
                        <button type="button" class="btn btn-outline btn-sm" onclick="livePreview.testKioskMode('single')">
                            <i class="fas fa-play mr-1"></i>Testen
                        </button>
                    </div>
                    
                    <div class="kiosk-preview-item" data-mode="triple">
                        <h4>Triple Mode</h4>
                        <div class="kiosk-preview-mockup triple-mockup">
                            <div class="mock-header-small">Labor Pattaya</div>
                            <div class="mock-triple-grid">
                                <div class="mock-column">
                                    <div class="mock-title">Heute</div>
                                    <div class="mock-content-small"></div>
                                </div>
                                <div class="mock-column">
                                    <div class="mock-title">Woche</div>
                                    <div class="mock-content-small"></div>
                                </div>
                                <div class="mock-column">
                                    <div class="mock-title">Vorschau</div>
                                    <div class="mock-content-small"></div>
                                </div>
                            </div>
                        </div>
                        <button type="button" class="btn btn-outline btn-sm" onclick="livePreview.testKioskMode('triple')">
                            <i class="fas fa-play mr-1"></i>Testen
                        </button>
                    </div>
                    
                    <div class="kiosk-preview-item" data-mode="rotation">
                        <h4>Rotation Mode</h4>
                        <div class="kiosk-preview-mockup rotation-mockup">
                            <div class="mock-header-small">Labor Pattaya</div>
                            <div class="mock-rotation-indicator">
                                <div class="rotation-dot active"></div>
                                <div class="rotation-dot"></div>
                                <div class="rotation-dot"></div>
                            </div>
                            <div class="mock-rotating-content">
                                <div class="mock-slide active">Heute</div>
                                <div class="mock-slide">Woche</div>
                                <div class="mock-slide">Ankündigungen</div>
                            </div>
                        </div>
                        <button type="button" class="btn btn-outline btn-sm" onclick="livePreview.testKioskMode('rotation')">
                            <i class="fas fa-play mr-1"></i>Testen
                        </button>
                    </div>
                </div>
                
                <div class="kiosk-preview-settings">
                    <h4>Vorschau-Einstellungen</h4>
                    <div class="preview-options">
                        <label class="setting-item">
                            <span>Simulierte Bildschirmgröße</span>
                            <select id="preview-screen-size" onchange="livePreview.changeScreenSize(this.value)">
                                <option value="1920x1080">1920x1080 (Full HD)</option>
                                <option value="1366x768">1366x768 (Laptop)</option>
                                <option value="1024x768" selected>1024x768 (Tablet)</option>
                                <option value="768x1024">768x1024 (Tablet Portrait)</option>
                                <option value="375x667">375x667 (Mobile)</option>
                            </select>
                        </label>
                        
                        <label class="setting-item">
                            <span>Zoom-Level</span>
                            <select id="preview-zoom" onchange="livePreview.changeZoom(this.value)">
                                <option value="0.5">50%</option>
                                <option value="0.75">75%</option>
                                <option value="1.0" selected>100%</option>
                                <option value="1.25">125%</option>
                                <option value="1.5">150%</option>
                            </select>
                        </label>
                    </div>
                </div>
            </div>
        `;

        const kioskStep = document.querySelector('.wizard-step[data-step="5"] .step-content');
        if (kioskStep) {
            kioskStep.insertAdjacentHTML('beforeend', kioskPreviewHTML);
        }
    }

    setupPreviewUpdates() {
        // Listen for form changes that affect preview
        const previewFields = [
            'theme', 'header_style', 'card_style', 'show_animations',
            'site_name', 'site_subtitle', 'kiosk_font_scale'
        ];

        previewFields.forEach(fieldName => {
            const elements = document.querySelectorAll(`[name="${fieldName}"]`);
            elements.forEach(element => {
                element.addEventListener('change', () => {
                    this.debounce(() => this.updateAllPreviews(), this.previewConfig.updateDelay)();
                });
            });
        });

        // Preview tab switching
        document.querySelectorAll('.preview-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const previewType = e.target.dataset.preview;
                this.switchPreview(previewType);
            });
        });
    }

    initializePreviewFrames() {
        // Initialize preview frames with base content
        ['desktop', 'tablet', 'mobile'].forEach(type => {
            const frame = document.getElementById(`preview-frame-${type}`);
            if (frame) {
                this.previewFrames.set(type, frame);
                this.loadPreviewContent(type);
            }
        });
    }

    async loadPreviewContent(previewType) {
        const frame = this.previewFrames.get(previewType);
        if (!frame) return;

        try {
            const config = this.gatherPreviewConfig();
            const params = new URLSearchParams({
                preview: 'true',
                type: previewType,
                theme: config.theme,
                font_scale: config.font_scale
            });

            const previewUrl = `${window.location.origin}/?${params.toString()}`;
            frame.src = previewUrl;
            
        } catch (error) {
            console.error(`Failed to load ${previewType} preview:`, error);
        }
    }

    gatherPreviewConfig() {
        return {
            theme: document.querySelector('input[name="theme"]:checked')?.value || 'medical',
            header_style: document.getElementById('header_style')?.value || 'gradient',
            card_style: document.getElementById('card_style')?.value || 'rounded',
            font_scale: document.getElementById('kiosk_font_scale')?.value || '1.0',
            site_name: document.getElementById('site_name')?.value || 'Labor Pattaya',
            show_animations: document.querySelector('input[name="show_animations"]')?.checked || false
        };
    }

    updateAllPreviews() {
        console.log('🔄 Updating all previews...');
        document.getElementById('preview-loading').style.display = 'flex';
        
        setTimeout(() => {
            ['desktop', 'tablet', 'mobile'].forEach(type => {
                this.loadPreviewContent(type);
            });
            
            setTimeout(() => {
                document.getElementById('preview-loading').style.display = 'none';
            }, 2000);
        }, 100);
    }

    switchPreview(previewType) {
        // Update tab states
        document.querySelectorAll('.preview-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-preview="${previewType}"]`).classList.add('active');

        // Update frame visibility
        document.querySelectorAll('.preview-frame').forEach(frame => {
            frame.classList.remove('active');
        });
        document.getElementById(`preview-frame-${previewType}`).classList.add('active');
    }

    changeScreenSize(size) {
        const [width, height] = size.split('x').map(Number);
        const activeFrame = document.querySelector('.preview-frame.active');
        
        if (activeFrame) {
            activeFrame.style.width = `${width}px`;
            activeFrame.style.height = `${height}px`;
            
            // Adjust scale to fit container
            const containerWidth = activeFrame.parentElement.offsetWidth - 40;
            const scale = Math.min(containerWidth / width, 0.8);
            activeFrame.style.transform = `scale(${scale})`;
        }
    }

    changeZoom(zoom) {
        const activeFrame = document.querySelector('.preview-frame.active');
        if (activeFrame) {
            const currentTransform = activeFrame.style.transform;
            const scaleMatch = currentTransform.match(/scale\(([\d.]+)\)/);
            const currentScale = scaleMatch ? parseFloat(scaleMatch[1]) : 1;
            
            activeFrame.style.transform = currentTransform.replace(
                /scale\([\d.]+\)/,
                `scale(${currentScale * parseFloat(zoom)})`
            );
        }
    }

    testKioskMode(mode) {
        const testUrl = `${window.location.origin}/kiosk/${mode}?test=true`;
        const testWindow = window.open(testUrl, '_blank', 
            'width=1200,height=800,scrollbars=yes,resizable=yes');
        
        // Auto-close test window after 30 seconds
        setTimeout(() => {
            if (testWindow && !testWindow.closed) {
                testWindow.close();
            }
        }, 30000);
        
        window.wizardController.showNotification(`${mode} Modus wird in neuem Fenster getestet`, 'info');
    }

    openFullPreview() {
        const config = this.gatherPreviewConfig();
        const params = new URLSearchParams({
            preview: 'true',
            ...config
        });
        
        const previewUrl = `${window.location.origin}/?${params.toString()}`;
        window.open(previewUrl, '_blank', 'width=1400,height=900,scrollbars=yes,resizable=yes');
    }

    async exportPreview() {
        try {
            // Use html2canvas or similar to capture preview
            const activeFrame = document.querySelector('.preview-frame.active');
            if (!activeFrame) return;

            // For now, open preview in new window for manual screenshot
            this.openFullPreview();
            
            window.wizardController.showNotification(
                'Vorschau in neuem Fenster geöffnet - Screenshot kann manuell erstellt werden',
                'info'
            );
            
        } catch (error) {
            console.error('Preview export failed:', error);
            window.wizardController.showNotification('Export fehlgeschlagen', 'error');
        }
    }

    refreshPreviews() {
        this.updateAllPreviews();
        window.wizardController.showNotification('Vorschau aktualisiert', 'success');
    }

    // Real-time CSS injection for preview
    injectPreviewStyles(frameDocument, config) {
        if (!frameDocument) return;

        const theme = this.previewConfig.themes[config.theme] || this.previewConfig.themes.medical;
        
        const previewStyles = `
            <style>
                :root {
                    --preview-primary: ${theme.primary};
                    --preview-secondary: ${theme.secondary};
                    --preview-accent: ${theme.accent};
                }
                
                body {
                    font-size: ${parseFloat(config.font_scale) * 16}px !important;
                }
                
                .header-gradient {
                    background: ${config.header_style === 'gradient' 
                        ? `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})` 
                        : theme.primary} !important;
                }
                
                .enhanced-card,
                .kiosk-card {
                    border-radius: ${config.card_style === 'rounded' ? '1rem' : 
                                   config.card_style === 'sharp' ? '0' : '0.5rem'} !important;
                }
                
                .thai-primary {
                    color: ${theme.primary} !important;
                }
                
                ${config.show_animations ? '' : `
                    *, *::before, *::after {
                        animation: none !important;
                        transition: none !important;
                    }
                `}
            </style>
        `;
        
        const existingStyle = frameDocument.getElementById('preview-injected-styles');
        if (existingStyle) {
            existingStyle.remove();
        }
        
        frameDocument.head.insertAdjacentHTML('beforeend', previewStyles);
    }

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

// Global instance for template access
window.livePreview = new LivePreviewSystemAgent();