/**
 * ADVANCED SETTINGS ENGINE - SUB-AGENT 3
 * Parallel execution: Advanced configuration management
 */

class AdvancedSettingsEngine {
    constructor() {
        this.settings = {
            performance: new PerformanceSettings(),
            kiosk: new KioskModeSettings(),
            themes: new ThemeSettings(),
            backup: new BackupSettings(),
            security: new SecuritySettings()
        };
        
        this.init();
    }

    init() {
        console.log('⚙️ SUB-AGENT 3: Advanced Settings Engine started');
        Object.values(this.settings).forEach(setting => setting.init());
    }
}

class PerformanceSettings {
    constructor() {
        this.config = {
            cacheStrategies: ['memory', 'disk', 'redis'],
            compressionLevels: ['none', 'low', 'medium', 'high'],
            optimizationModes: ['speed', 'memory', 'balanced']
        };
    }

    init() {
        this.setupPerformanceMonitoring();
        this.createPerformanceUI();
    }

    setupPerformanceMonitoring() {
        // Performance metrics collection
        setInterval(() => {
            const metrics = {
                memory: performance.memory ? Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) : 0,
                fps: this.calculateFPS(),
                loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
                timestamp: Date.now()
            };
            
            this.storeMetrics(metrics);
        }, 10000);
    }

    calculateFPS() {
        let fps = 0;
        let lastTime = performance.now();
        
        const frame = (currentTime) => {
            fps = Math.round(1000 / (currentTime - lastTime));
            lastTime = currentTime;
            requestAnimationFrame(frame);
        };
        
        requestAnimationFrame(frame);
        return fps;
    }

    storeMetrics(metrics) {
        try {
            const stored = JSON.parse(localStorage.getItem('performance_metrics') || '[]');
            stored.push(metrics);
            
            // Keep only last 100 entries
            if (stored.length > 100) {
                stored.splice(0, stored.length - 100);
            }
            
            localStorage.setItem('performance_metrics', JSON.stringify(stored));
        } catch (error) {
            console.warn('Failed to store performance metrics:', error);
        }
    }

    createPerformanceUI() {
        // Inject performance settings UI
        const performanceHTML = `
            <div class="performance-settings-panel" id="performance-panel">
                <h3>Performance-Optimierung</h3>
                
                <div class="performance-metrics">
                    <div class="metric">
                        <label>Speicherverbrauch</label>
                        <div class="metric-value" id="memory-usage">-- MB</div>
                    </div>
                    <div class="metric">
                        <label>FPS</label>
                        <div class="metric-value" id="fps-counter">-- fps</div>
                    </div>
                    <div class="metric">
                        <label>Ladezeit</label>
                        <div class="metric-value" id="load-time">-- ms</div>
                    </div>
                </div>
                
                <div class="performance-controls">
                    <label class="setting-item">
                        <span>Cache-Strategie</span>
                        <select name="cache_strategy">
                            <option value="memory">Memory (schnell)</option>
                            <option value="disk" selected>Disk (ausgewogen)</option>
                            <option value="redis">Redis (professionell)</option>
                        </select>
                    </label>
                    
                    <label class="setting-item">
                        <span>Komprimierung</span>
                        <select name="compression_level">
                            <option value="none">Keine</option>
                            <option value="low">Niedrig</option>
                            <option value="medium" selected>Mittel</option>
                            <option value="high">Hoch</option>
                        </select>
                    </label>
                    
                    <label class="setting-item">
                        <span>Optimierung für</span>
                        <select name="optimization_mode">
                            <option value="speed">Geschwindigkeit</option>
                            <option value="memory">Speicher</option>
                            <option value="balanced" selected>Ausgewogen</option>
                        </select>
                    </label>
                </div>
            </div>
        `;
        
        // Insert into step 6 content
        const systemStep = document.querySelector('.wizard-step[data-step="6"] .step-content');
        if (systemStep) {
            systemStep.insertAdjacentHTML('beforeend', performanceHTML);
        }
    }
}

class KioskModeSettings {
    constructor() {
        this.kioskConfigs = {
            displays: {
                'small-tablet': { minWidth: 768, maxWidth: 1023, columns: 2, fontSize: 1.0 },
                'large-tablet': { minWidth: 1024, maxWidth: 1365, columns: 3, fontSize: 1.1 },
                'monitor-1080p': { minWidth: 1366, maxWidth: 1919, columns: 3, fontSize: 1.2 },
                'monitor-1440p': { minWidth: 1920, maxWidth: 2559, columns: 3, fontSize: 1.3 },
                'monitor-4k': { minWidth: 2560, maxWidth: 9999, columns: 3, fontSize: 1.5 }
            }
        };
    }

    init() {
        console.log('🖥️ SUB-AGENT 3: Kiosk Mode Settings initialized');
        this.createKioskUI();
        this.setupDisplayDetection();
    }

    setupDisplayDetection() {
        // Auto-detect optimal kiosk settings
        const width = window.innerWidth;
        const height = window.innerHeight;
        const dpr = window.devicePixelRatio;
        
        console.log(`📺 Display detected: ${width}x${height} @${dpr}x`);
        
        // Find matching display config
        const matchingConfig = Object.entries(this.kioskConfigs.displays).find(([key, config]) => {
            return width >= config.minWidth && width <= config.maxWidth;
        });
        
        if (matchingConfig) {
            const [displayType, config] = matchingConfig;
            this.applyDisplayConfig(displayType, config);
        }
    }

    applyDisplayConfig(displayType, config) {
        console.log(`🎯 Applying ${displayType} configuration:`, config);
        
        // Update form fields with detected values
        const fontScaleSelect = document.querySelector('[name="kiosk_font_scale"]');
        if (fontScaleSelect) {
            fontScaleSelect.value = config.fontSize;
        }
        
        // Show recommendation to user
        if (window.wizardController) {
            window.wizardController.showNotification(
                `${displayType} Display erkannt - Einstellungen angepasst`,
                'info'
            );
        }
    }

    createKioskUI() {
        const kioskHTML = `
            <div class="kiosk-settings-panel" id="kiosk-panel">
                <h3>Erweiterte Kiosk-Einstellungen</h3>
                
                <div class="kiosk-display-detection">
                    <h4>Display-Erkennung</h4>
                    <div class="detected-display" id="detected-display">
                        <div class="display-info">
                            <span class="display-resolution"></span>
                            <span class="display-type"></span>
                            <span class="display-dpr"></span>
                        </div>
                        <button type="button" class="btn btn-outline btn-sm" onclick="kioskSettings.detectDisplay()">
                            <i class="fas fa-search mr-1"></i>Neu erkennen
                        </button>
                    </div>
                </div>
                
                <div class="kiosk-advanced-options">
                    <label class="setting-item">
                        <span>Screensaver-Timeout (Minuten)</span>
                        <input type="number" name="screensaver_timeout" min="1" max="60" value="10">
                    </label>
                    
                    <label class="setting-item">
                        <span>Rotation-Intervall (Sekunden)</span>
                        <input type="number" name="rotation_interval" min="5" max="300" value="30">
                    </label>
                    
                    <label class="setting-item">
                        <span>Max. Inaktivität (Minuten)</span>
                        <input type="number" name="max_inactivity" min="5" max="1440" value="60">
                    </label>
                </div>
                
                <div class="kiosk-power-management">
                    <h4>Energieverwaltung</h4>
                    <label class="toggle-option">
                        <input type="checkbox" name="power_save_mode">
                        <span class="toggle-label">Energiesparmodus</span>
                        <small>Reduziert Animationen bei Inaktivität</small>
                    </label>
                    
                    <label class="toggle-option">
                        <input type="checkbox" name="wake_on_motion">
                        <span class="toggle-label">Bewegungserkennung</span>
                        <small>Aktiviert Display bei Bewegung (falls unterstützt)</small>
                    </label>
                </div>
            </div>
        `;
        
        const systemStep = document.querySelector('.wizard-step[data-step="6"] .step-content');
        if (systemStep) {
            systemStep.insertAdjacentHTML('beforeend', kioskHTML);
        }
    }

    detectDisplay() {
        this.setupDisplayDetection();
        document.querySelector('.display-resolution').textContent = `${window.innerWidth}x${window.innerHeight}`;
        document.querySelector('.display-dpr').textContent = `${window.devicePixelRatio}x DPR`;
        
        // Auto-detect display type
        const width = window.innerWidth;
        let displayType = 'Unknown';
        
        if (width < 768) displayType = 'Mobile';
        else if (width < 1024) displayType = 'Small Tablet';
        else if (width < 1366) displayType = 'Large Tablet';
        else if (width < 1920) displayType = '1080p Monitor';
        else if (width < 2560) displayType = '1440p Monitor';
        else displayType = '4K+ Monitor';
        
        document.querySelector('.display-type').textContent = displayType;
    }
}

class ThemeSettings {
    init() {
        console.log('🎨 SUB-AGENT 3: Theme Settings initialized');
        this.createThemeEditor();
    }

    createThemeEditor() {
        const themeHTML = `
            <div class="theme-editor-panel" id="theme-panel">
                <h3>Theme-Editor</h3>
                
                <div class="color-customization">
                    <h4>Farbpalette anpassen</h4>
                    <div class="color-inputs">
                        <label class="color-input">
                            <span>Primärfarbe</span>
                            <input type="color" name="theme_primary" value="#40E0D0">
                        </label>
                        <label class="color-input">
                            <span>Sekundärfarbe</span>
                            <input type="color" name="theme_secondary" value="#00A86B">
                        </label>
                        <label class="color-input">
                            <span>Akzentfarbe</span>
                            <input type="color" name="theme_accent" value="#FF7F50">
                        </label>
                    </div>
                </div>
                
                <div class="typography-settings">
                    <h4>Typografie</h4>
                    <label class="setting-item">
                        <span>Hauptschriftart</span>
                        <select name="theme_font_family">
                            <option value="sarabun" selected>Sarabun (Thai-optimiert)</option>
                            <option value="noto-thai">Noto Sans Thai</option>
                            <option value="roboto">Roboto</option>
                            <option value="inter">Inter</option>
                            <option value="system">System-Schrift</option>
                        </select>
                    </label>
                    
                    <label class="setting-item">
                        <span>Schrift-Gewicht</span>
                        <select name="theme_font_weight">
                            <option value="300">Light</option>
                            <option value="400">Normal</option>
                            <option value="500">Medium</option>
                            <option value="600" selected>Semibold</option>
                            <option value="700">Bold</option>
                        </select>
                    </label>
                </div>
            </div>
        `;
        
        const designStep = document.querySelector('.wizard-step[data-step="4"] .step-content');
        if (designStep) {
            designStep.insertAdjacentHTML('beforeend', themeHTML);
        }
    }
}

class BackupSettings {
    init() {
        console.log('💾 SUB-AGENT 3: Backup Settings initialized');
        this.createBackupUI();
    }

    createBackupUI() {
        const backupHTML = `
            <div class="backup-settings-panel" id="backup-panel">
                <h3>Backup & Wiederherstellung</h3>
                
                <div class="backup-options">
                    <div class="backup-item">
                        <h4>Automatische Backups</h4>
                        <label class="setting-item">
                            <span>Frequenz</span>
                            <select name="backup_frequency">
                                <option value="disabled">Deaktiviert</option>
                                <option value="hourly">Stündlich</option>
                                <option value="daily" selected>Täglich</option>
                                <option value="weekly">Wöchentlich</option>
                            </select>
                        </label>
                        
                        <label class="setting-item">
                            <span>Aufbewahrung (Tage)</span>
                            <input type="number" name="backup_retention" min="1" max="365" value="30">
                        </label>
                    </div>
                    
                    <div class="backup-item">
                        <h4>Backup-Inhalte</h4>
                        <div class="backup-content-options">
                            <label class="toggle-option">
                                <input type="checkbox" name="backup_database" checked>
                                <span class="toggle-label">Datenbank</span>
                            </label>
                            <label class="toggle-option">
                                <input type="checkbox" name="backup_config" checked>
                                <span class="toggle-label">Konfiguration</span>
                            </label>
                            <label class="toggle-option">
                                <input type="checkbox" name="backup_assets">
                                <span class="toggle-label">Assets (Bilder, etc.)</span>
                            </label>
                            <label class="toggle-option">
                                <input type="checkbox" name="backup_logs">
                                <span class="toggle-label">Logs</span>
                            </label>
                        </div>
                    </div>
                </div>
                
                <div class="backup-actions">
                    <button type="button" class="btn btn-outline" onclick="backupSettings.createBackup()">
                        <i class="fas fa-save mr-2"></i>Sofort-Backup erstellen
                    </button>
                    <button type="button" class="btn btn-outline" onclick="backupSettings.restoreBackup()">
                        <i class="fas fa-upload mr-2"></i>Backup wiederherstellen
                    </button>
                </div>
            </div>
        `;
        
        const systemStep = document.querySelector('.wizard-step[data-step="6"] .step-content');
        if (systemStep) {
            systemStep.insertAdjacentHTML('beforeend', backupHTML);
        }
    }

    async createBackup() {
        try {
            const response = await fetch('/admin/api/create-backup', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                }
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `qr-portal-backup-${new Date().toISOString().split('T')[0]}.zip`;
                a.click();
                URL.revokeObjectURL(url);
                
                window.wizardController.showNotification('Backup erfolgreich erstellt', 'success');
            }
        } catch (error) {
            window.wizardController.showNotification('Backup-Erstellung fehlgeschlagen', 'error');
        }
    }

    restoreBackup() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.zip,.json';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                this.uploadBackup(file);
            }
        };
        input.click();
    }

    async uploadBackup(file) {
        const formData = new FormData();
        formData.append('backup_file', file);
        formData.append('csrf_token', document.querySelector('input[name="csrf_token"]').value);
        
        try {
            const response = await fetch('/admin/api/restore-backup', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.wizardController.showNotification('Backup erfolgreich wiederhergestellt', 'success');
                setTimeout(() => location.reload(), 2000);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            window.wizardController.showNotification('Backup-Wiederherstellung fehlgeschlagen', 'error');
        }
    }
}

class SecuritySettings {
    init() {
        console.log('🛡️ SUB-AGENT 3: Security Settings initialized');
        this.createSecurityUI();
    }

    createSecurityUI() {
        const securityHTML = `
            <div class="security-settings-panel" id="security-panel">
                <h3>Erweiterte Sicherheitseinstellungen</h3>
                
                <div class="security-options">
                    <div class="security-section">
                        <h4>Zugriffskontrolle</h4>
                        <label class="setting-item">
                            <span>Session-Timeout (Minuten)</span>
                            <input type="number" name="session_timeout" min="5" max="480" value="60">
                        </label>
                        
                        <label class="setting-item">
                            <span>Max. Login-Versuche</span>
                            <input type="number" name="max_login_attempts" min="3" max="10" value="5">
                        </label>
                        
                        <label class="toggle-option">
                            <input type="checkbox" name="enable_2fa">
                            <span class="toggle-label">Zwei-Faktor-Authentifizierung</span>
                            <small>Zusätzliche Sicherheit mit TOTP</small>
                        </label>
                    </div>
                    
                    <div class="security-section">
                        <h4>Datenintegrität</h4>
                        <label class="toggle-option">
                            <input type="checkbox" name="enable_integrity_checks" checked>
                            <span class="toggle-label">Integritätsprüfungen</span>
                            <small>Prüft Datenintegrität bei jedem Start</small>
                        </label>
                        
                        <label class="toggle-option">
                            <input type="checkbox" name="encrypt_sensitive_data">
                            <span class="toggle-label">Daten verschlüsseln</span>
                            <small>Verschlüsselt sensible Konfigurationsdaten</small>
                        </label>
                    </div>
                    
                    <div class="security-section">
                        <h4>Monitoring & Logs</h4>
                        <label class="setting-item">
                            <span>Log-Level</span>
                            <select name="log_level">
                                <option value="ERROR">Error only</option>
                                <option value="WARNING">Warning+</option>
                                <option value="INFO" selected>Info+</option>
                                <option value="DEBUG">Debug (alle)</option>
                            </select>
                        </label>
                        
                        <label class="toggle-option">
                            <input type="checkbox" name="enable_audit_log" checked>
                            <span class="toggle-label">Audit-Log</span>
                            <small>Protokolliert alle Admin-Aktionen</small>
                        </label>
                    </div>
                </div>
            </div>
        `;
        
        const systemStep = document.querySelector('.wizard-step[data-step="6"] .step-content');
        if (systemStep) {
            systemStep.insertAdjacentHTML('beforeend', securityHTML);
        }
    }
}

// Global instances for template access
window.performanceSettings = new PerformanceSettings();
window.kioskSettings = new KioskModeSettings();
window.themeSettings = new ThemeSettings();
window.backupSettings = new BackupSettings();
window.securitySettings = new SecuritySettings();

// Initialize advanced settings when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.wizard-container')) {
        window.advancedSettingsEngine = new AdvancedSettingsEngine();
    }
});