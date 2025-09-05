/**
 * KIOSK MODE ENHANCED JAVASCRIPT
 * Version: 3.0
 * Purpose: Professional medical facility kiosk interface management
 * Features: Clock, Auto-refresh, Fullscreen, Error handling, Performance monitoring
 */

class KioskManager {
    constructor() {
        this.config = {
            refreshInterval: 120000, // 2 minutes
            clockInterval: 1000,     // 1 second
            timezone: 'Asia/Bangkok',
            language: this.detectLanguage(), // Auto-detect from URL or default to Thai
            performanceThreshold: 30, // FPS
            maxPerformanceIssues: 10
        };
        
        this.state = {
            isRunning: false,
            refreshTimer: null,
            clockTimer: null,
            performanceIssues: 0,
            lastFrameTime: performance.now(),
            interactions: 0,
            startTime: Date.now()
        };
        
        this.elements = {
            clock: null,
            date: null,
            refreshTimer: null,
            refreshIcon: null,
            statusIcon: null,
            qrOverlay: null
        };
        
        this.init();
    }
    
    /**
     * Detect language from URL parameter or default to Thai
     */
    detectLanguage() {
        const urlParams = new URLSearchParams(window.location.search);
        const langParam = urlParams.get('lang');
        
        // Thai-First approach: Default to Thai if no parameter
        if (!langParam) return 'th';
        
        // Support only Thai and English in kiosk mode (no German)
        return ['th', 'en'].includes(langParam) ? langParam : 'th';
    }
    
    /**
     * Get localized weekday names
     */
    getWeekdayNames() {
        const weekdays = {
            'th': ['อา.', 'จ.', 'อ.', 'พ.', 'พฤ.', 'ศ.', 'ส.'],
            'en': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
            'de': ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa']
        };
        return weekdays[this.config.language] || weekdays['th'];
    }
    
    /**
     * Get localized month names
     */
    getMonthNames() {
        const months = {
            'th': ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'],
            'en': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'de': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
        };
        return months[this.config.language] || months['th'];
    }
    
    /**
     * Initialize the kiosk manager
     */
    init() {
        console.log('🖥️ Initializing Enhanced Kiosk Mode...');
        
        this.bindElements();
        this.setupEventListeners();
        this.preventDefaultBehaviors();
        this.initializeClock();
        this.initializeAutoRefresh();
        this.initializeFullscreen();
        this.initializeAnimations();
        this.initializePerformanceMonitoring();
        this.initializeErrorHandling();
        
        this.state.isRunning = true;
        
        console.log('✅ Kiosk Mode initialized successfully');
        this.logSystemInfo();
    }
    
    /**
     * Bind DOM elements
     */
    bindElements() {
        this.elements.clock = document.getElementById('kiosk-clock') || 
                             document.getElementById('mega-clock') || 
                             document.querySelector('.kiosk-clock');
        this.elements.date = document.getElementById('kiosk-date') || 
                            document.getElementById('mega-date') || 
                            document.querySelector('.kiosk-date');
        this.elements.refreshTimer = document.getElementById('refresh-timer');
        this.elements.refreshIcon = document.getElementById('refresh-icon');
        this.elements.statusIcon = document.querySelector('.kiosk-status-icon i') || 
                                   document.querySelector('.status-mega-icon i');
        this.elements.qrOverlay = document.querySelector('.kiosk-qr-overlay') || 
                                  document.querySelector('.qr-overlay');
    }
    
    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Keyboard shortcuts for kiosk management
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
        
        // Error handling
        window.addEventListener('error', this.handleError.bind(this));
        window.addEventListener('unhandledrejection', this.handlePromiseRejection.bind(this));
        
        // Visibility change (for performance optimization)
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        
        // Network status
        window.addEventListener('online', this.handleNetworkOnline.bind(this));
        window.addEventListener('offline', this.handleNetworkOffline.bind(this));
        
        // Resize events for responsive adjustments
        window.addEventListener('resize', this.debounce(this.handleResize.bind(this), 250));
        
        // Touch/interaction tracking (for screensaver)
        ['click', 'touchstart', 'mousemove', 'keydown'].forEach(event => {
            document.addEventListener(event, this.handleInteraction.bind(this), { passive: true });
        });
    }
    
    /**
     * Prevent default browser behaviors
     */
    preventDefaultBehaviors() {
        // Prevent context menu
        document.addEventListener('contextmenu', e => e.preventDefault());
        
        // Prevent text selection
        document.addEventListener('selectstart', e => e.preventDefault());
        
        // Prevent drag and drop
        document.addEventListener('dragstart', e => e.preventDefault());
        
        // Prevent certain keyboard combinations
        document.addEventListener('keydown', e => {
            // Prevent F5, Ctrl+R (refresh)
            if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
                if (!e.ctrlKey || !e.altKey) { // Allow Ctrl+Alt+R for admin refresh
                    e.preventDefault();
                }
            }
            
            // Prevent F11 (fullscreen toggle) - we manage this ourselves
            if (e.key === 'F11') {
                e.preventDefault();
            }
            
            // Prevent Alt+Tab, Ctrl+Alt+Delete, etc.
            if (e.altKey && e.key === 'Tab') {
                e.preventDefault();
            }
            
            // Prevent Windows key combinations
            if (e.metaKey) {
                e.preventDefault();
            }
        });
    }
    
    /**
     * Initialize the live clock
     */
    initializeClock() {
        if (!this.elements.clock) {
            console.warn('⚠️ Clock element not found');
            return;
        }
        
        const updateClock = () => {
            try {
                const now = new Date();
                const bangkokTime = new Date(now.toLocaleString(\"en-US\", {
                    timeZone: this.config.timezone
                }));
                
                // Format time with blinking colons
                const hours = String(bangkokTime.getHours()).padStart(2, '0');
                const minutes = String(bangkokTime.getMinutes()).padStart(2, '0');
                const seconds = String(bangkokTime.getSeconds()).padStart(2, '0');
                
                const colonOpacity = bangkokTime.getSeconds() % 2 ? '1' : '0.3';
                
                this.elements.clock.innerHTML = `${hours}<span style=\"opacity: ${colonOpacity};\">:</span>${minutes}<span style=\"opacity: ${colonOpacity};\">:</span>${seconds}`;
                
                // Update date if element exists - THAI-FIRST approach
                if (this.elements.date) {
                    const dateOptions = {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        timeZone: this.config.timezone
                    };
                    
                    const thaiDate = bangkokTime.toLocaleDateString('th-TH', dateOptions);
                    const englishDate = bangkokTime.toLocaleDateString('en-US', dateOptions);
                    
                    // Thai-First: Thai primary, English secondary, NO German in kiosk
                    if (this.config.language === 'th') {
                        this.elements.date.innerHTML = `
                            <span class=\"text-thai-primary\">${thaiDate}</span><br>
                            <span style=\"font-size: 0.8em; opacity: 0.7; color: #666;\">${englishDate}</span>
                        `;
                    } else if (this.config.language === 'en') {
                        this.elements.date.innerHTML = `
                            <span class=\"text-english-primary\">${englishDate}</span><br>
                            <span style=\"font-size: 0.8em; opacity: 0.7; color: #666;\">${thaiDate}</span>
                        `;
                    }
                }
                
            } catch (error) {
                console.error('Clock update error:', error);
                this.elements.clock.textContent = '--:--:--';
            }
        };
        
        // Update immediately and then every second
        updateClock();
        this.state.clockTimer = setInterval(updateClock, this.config.clockInterval);
        
        console.log('⏰ Clock initialized');
    }
    
    /**
     * Initialize auto-refresh functionality
     */
    initializeAutoRefresh() {
        let timeLeft = this.config.refreshInterval / 1000;
        
        const updateTimer = () => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            if (this.elements.refreshTimer) {
                this.elements.refreshTimer.textContent = `${minutes}:${String(seconds).padStart(2, '0')}`;
            }
            
            if (timeLeft <= 0) {
                this.performRefresh();
                return;
            }
            
            if (timeLeft <= 10 && this.elements.refreshIcon) {
                this.elements.refreshIcon.classList.add('spinning');
            }
            
            timeLeft--;
        };
        
        // Update timer display immediately and then every second
        updateTimer();
        this.state.refreshTimer = setInterval(updateTimer, 1000);
        
        console.log(`🔄 Auto-refresh initialized (${this.config.refreshInterval / 1000}s)`);
    }
    
    /**
     * Perform page refresh with smooth transition
     */
    performRefresh() {
        console.log('🔄 Performing auto-refresh...');
        
        // Add refresh animation
        if (this.elements.refreshIcon) {
            this.elements.refreshIcon.classList.add('spinning');
        }
        
        // Fade out effect
        document.body.style.transition = 'opacity 0.5s ease-out';
        document.body.style.opacity = '0.7';
        
        // Perform refresh after animation
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }
    
    /**
     * Initialize fullscreen functionality
     */
    initializeFullscreen() {
        let hasInteracted = false;
        
        const tryFullscreen = () => {
            if (!hasInteracted && !document.fullscreenElement) {
                document.documentElement.requestFullscreen()
                    .then(() => {
                        console.log('📺 Fullscreen activated');
                        hasInteracted = true;
                    })
                    .catch(err => {
                        console.warn('⚠️ Fullscreen not available:', err.message);
                        hasInteracted = true;
                    });
            }
        };
        
        // Try fullscreen on any user interaction
        ['click', 'touchstart', 'keydown'].forEach(event => {
            document.addEventListener(event, tryFullscreen, { once: true });
        });
        
        // Handle fullscreen change
        document.addEventListener('fullscreenchange', () => {
            if (document.fullscreenElement) {
                document.body.classList.add('kiosk-fullscreen');
            } else {
                document.body.classList.remove('kiosk-fullscreen');
                console.log('📺 Fullscreen deactivated');
            }
        });
        
        console.log('📺 Fullscreen handler initialized');
    }
    
    /**
     * Initialize entrance animations
     */
    initializeAnimations() {
        // Add entrance animations with stagger
        const sections = document.querySelectorAll('.kiosk-column, .today-section, .week-section, .preview-section, .kiosk-time-card');
        
        sections.forEach((section, index) => {
            section.style.opacity = '0';
            section.style.transform = 'translateY(20px)';
            section.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
            
            setTimeout(() => {
                section.style.opacity = '1';
                section.style.transform = 'translateY(0)';
            }, 200 + (index * 150));
        });
        
        // QR code pulse animation
        if (this.elements.qrOverlay) {
            setInterval(() => {
                this.elements.qrOverlay.style.transform = 'scale(1.03)';
                setTimeout(() => {
                    this.elements.qrOverlay.style.transform = 'scale(1)';
                }, 300);
            }, 8000);
        }
        
        // Status icon animation
        if (this.elements.statusIcon) {
            this.elements.statusIcon.style.animation = 'kiosk-status-pulse 3s ease-in-out infinite';
        }
        
        console.log('✨ Animations initialized');
    }
    
    /**
     * Initialize performance monitoring
     */
    initializePerformanceMonitoring() {
        const checkPerformance = () => {
            const now = performance.now();
            const fps = Math.round(1000 / (now - this.state.lastFrameTime));
            this.state.lastFrameTime = now;
            
            if (fps < this.config.performanceThreshold) {
                this.state.performanceIssues++;
                
                if (this.state.performanceIssues > this.config.maxPerformanceIssues) {
                    console.warn('⚠️ Performance issues detected, reloading...');
                    this.showNotification('Leistung optimieren...', 'info');
                    
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                }
            } else {
                this.state.performanceIssues = Math.max(0, this.state.performanceIssues - 1);
            }
            
            // Log performance metrics every 30 seconds
            if (Math.floor(now / 30000) > Math.floor((now - 1000) / 30000)) {
                console.log(`📊 Performance: ${fps}fps, Issues: ${this.state.performanceIssues}, Uptime: ${Math.floor((now - this.state.startTime) / 60000)}min`);
            }
        };
        
        setInterval(checkPerformance, 1000);
        console.log('📊 Performance monitoring initialized');
    }
    
    /**
     * Initialize comprehensive error handling
     */
    initializeErrorHandling() {
        console.log('🛡️ Error handling initialized');
    }
    
    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(e) {
        // Ctrl+Alt+R: Force refresh
        if (e.ctrlKey && e.altKey && e.key === 'r') {
            e.preventDefault();
            console.log('🔄 Manual refresh triggered');
            this.performRefresh();
        }
        
        // Ctrl+Alt+F: Toggle fullscreen
        if (e.ctrlKey && e.altKey && e.key === 'f') {
            e.preventDefault();
            if (document.fullscreenElement) {
                document.exitFullscreen();
            } else {
                document.documentElement.requestFullscreen();
            }
        }
        
        // Ctrl+Alt+I: Show system info
        if (e.ctrlKey && e.altKey && e.key === 'i') {
            e.preventDefault();
            this.showSystemInfo();
        }
        
        // Ctrl+Alt+H: Show help
        if (e.ctrlKey && e.altKey && e.key === 'h') {
            e.preventDefault();
            this.showHelp();
        }
        
        // Escape: Exit fullscreen (admin only)
        if (e.key === 'Escape' && (e.ctrlKey && e.altKey)) {
            if (document.fullscreenElement) {
                document.exitFullscreen();
            }
        }
    }
    
    /**
     * Handle JavaScript errors
     */
    handleError(event) {
        console.error('❌ JavaScript Error:', event.error);
        
        const errorInfo = {
            message: event.error?.message || 'Unknown error',
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            timestamp: new Date().toISOString()
        };
        
        this.showErrorIndicator(errorInfo.message);
        
        // Log to localStorage for debugging
        this.logError('js_error', errorInfo);
    }
    
    /**
     * Handle Promise rejections
     */
    handlePromiseRejection(event) {
        console.error('❌ Unhandled Promise Rejection:', event.reason);
        
        this.showErrorIndicator('System error detected');
        this.logError('promise_rejection', {
            reason: event.reason?.toString() || 'Unknown rejection',
            timestamp: new Date().toISOString()
        });
        
        // Prevent default browser behavior
        event.preventDefault();
    }
    
    /**
     * Handle visibility change (tab focus/blur)
     */
    handleVisibilityChange() {
        if (document.hidden) {
            console.log('👁️ Page hidden - pausing animations');
            document.body.classList.add('kiosk-hidden');
        } else {
            console.log('👁️ Page visible - resuming animations');
            document.body.classList.remove('kiosk-hidden');
        }
    }
    
    /**
     * Handle network online
     */
    handleNetworkOnline() {
        console.log('🌐 Network connection restored');
        this.showNotification('Verbindung wiederhergestellt', 'success');
        document.body.classList.remove('kiosk-offline');
    }
    
    /**
     * Handle network offline
     */
    handleNetworkOffline() {
        console.log('🌐 Network connection lost');
        this.showNotification('Keine Internetverbindung', 'warning');
        document.body.classList.add('kiosk-offline');
    }
    
    /**
     * Handle window resize
     */
    handleResize() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        console.log(`📐 Resize detected: ${width}x${height}`);
        
        // Adjust font sizes for different screen sizes
        if (width >= 2560) {
            document.documentElement.style.setProperty('--kiosk-scale', '1.5');
        } else if (width >= 1920) {
            document.documentElement.style.setProperty('--kiosk-scale', '1.2');
        } else {
            document.documentElement.style.setProperty('--kiosk-scale', '1');
        }
    }
    
    /**
     * Handle user interactions (for screensaver/power management)
     */
    handleInteraction() {
        this.state.interactions++;
        
        // Wake up screen if in sleep mode
        if (document.body.classList.contains('kiosk-screensaver')) {
            document.body.classList.remove('kiosk-screensaver');
            console.log('💤 Screensaver deactivated');
        }
    }
    
    /**
     * Show error indicator
     */
    showErrorIndicator(message) {
        const indicator = document.createElement('div');
        indicator.className = 'kiosk-error-indicator';
        indicator.innerHTML = `
            <i class=\"fas fa-exclamation-triangle\"></i>
            <span>${message}</span>
        `;
        
        indicator.style.cssText = `
            position: fixed;
            top: 2rem;
            left: 2rem;
            background: var(--kiosk-closed);
            color: var(--kiosk-white);
            padding: 1rem 2rem;
            border-radius: 1rem;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            z-index: 9999;
            box-shadow: var(--kiosk-shadow-xl);
            animation: kiosk-slide-up 0.3s ease-out;
        `;
        
        document.body.appendChild(indicator);
        
        setTimeout(() => {
            indicator.style.animation = 'kiosk-fade-out 0.5s ease-out forwards';
            setTimeout(() => indicator.remove(), 500);
        }, 5000);
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const colors = {
            success: 'var(--kiosk-open)',
            warning: 'var(--kiosk-warning)',
            error: 'var(--kiosk-closed)',
            info: 'var(--kiosk-info)'
        };
        
        const icons = {
            success: 'fas fa-check-circle',
            warning: 'fas fa-exclamation-triangle',
            error: 'fas fa-times-circle',
            info: 'fas fa-info-circle'
        };
        
        const notification = document.createElement('div');
        notification.className = 'kiosk-notification';
        notification.innerHTML = `
            <i class=\"${icons[type]}\"></i>
            <span>${message}</span>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 2rem;
            right: 2rem;
            background: ${colors[type]};
            color: var(--kiosk-white);
            padding: 1rem 2rem;
            border-radius: 1rem;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            z-index: 9999;
            box-shadow: var(--kiosk-shadow-xl);
            animation: kiosk-slide-down 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'kiosk-fade-out 0.5s ease-out forwards';
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }
    
    /**
     * Show system information
     */
    showSystemInfo() {
        const uptime = Math.floor((Date.now() - this.state.startTime) / 60000);
        const info = `
            🖥️ Kiosk System Info:
            • Uptime: ${uptime} minutes
            • Interactions: ${this.state.interactions}
            • Performance Issues: ${this.state.performanceIssues}
            • Screen: ${window.innerWidth}x${window.innerHeight}
            • Network: ${navigator.onLine ? 'Online' : 'Offline'}
            • Fullscreen: ${document.fullscreenElement ? 'Yes' : 'No'}
        `;
        
        console.log(info);
        this.showNotification('System-Info in Konsole', 'info');
    }
    
    /**
     * Show help information
     */
    showHelp() {
        const help = `
            🎮 Kiosk Shortcuts:
            • Ctrl+Alt+R: Refresh
            • Ctrl+Alt+F: Toggle Fullscreen
            • Ctrl+Alt+I: System Info
            • Ctrl+Alt+H: This Help
            • Ctrl+Alt+Escape: Exit Fullscreen
        `;
        
        console.log(help);
        this.showNotification('Hilfe in Konsole angezeigt', 'info');
    }
    
    /**
     * Log errors to localStorage for debugging
     */
    logError(type, details) {
        try {
            const logs = JSON.parse(localStorage.getItem('kiosk_error_logs') || '[]');
            logs.push({
                type,
                details,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href
            });
            
            // Keep only last 50 logs
            if (logs.length > 50) {
                logs.splice(0, logs.length - 50);
            }
            
            localStorage.setItem('kiosk_error_logs', JSON.stringify(logs));
        } catch (e) {
            console.warn('Failed to save error log:', e);
        }
    }
    
    /**
     * Log system information
     */
    logSystemInfo() {
        console.log(`
🖥️ KIOSK MODE SYSTEM INFO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 Display: ${window.innerWidth}x${window.innerHeight} (${window.devicePixelRatio}x DPR)
🌐 Network: ${navigator.onLine ? 'Online' : 'Offline'}
💾 Storage: ${navigator.storage ? 'Available' : 'Not Available'}
🎯 Fullscreen: ${document.fullscreenElement ? 'Active' : 'Inactive'}
🔧 User Agent: ${navigator.userAgent}
⏰ Timezone: ${Intl.DateTimeFormat().resolvedOptions().timeZone}
📱 Touch: ${navigator.maxTouchPoints > 0 ? 'Supported' : 'Not Supported'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        `);
    }
    
    /**
     * Utility: Debounce function
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
    
    /**
     * Cleanup function
     */
    destroy() {
        console.log('🧹 Cleaning up Kiosk Manager...');
        
        if (this.state.clockTimer) {
            clearInterval(this.state.clockTimer);
        }
        
        if (this.state.refreshTimer) {
            clearInterval(this.state.refreshTimer);
        }
        
        this.state.isRunning = false;
        
        console.log('✅ Kiosk Manager cleaned up');
    }
}

// Initialize kiosk manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're in kiosk mode
    if (document.querySelector('[data-kiosk]') || 
        document.body.classList.contains('kiosk-mode') ||
        window.location.pathname.includes('/kiosk/')) {
        
        window.kioskManager = new KioskManager();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.kioskManager) {
        window.kioskManager.destroy();
    }
});

// CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes kiosk-slide-up {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes kiosk-slide-down {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes kiosk-fade-out {
        from {
            opacity: 1;
            transform: scale(1);
        }
        to {
            opacity: 0;
            transform: scale(0.95);
        }
    }
    
    .kiosk-hidden * {
        animation-play-state: paused !important;
    }
    
    .kiosk-offline::after {
        content: '⚠️ OFFLINE';
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 2rem 3rem;
        border-radius: 1rem;
        font-size: 2rem;
        font-weight: bold;
        z-index: 10000;
        backdrop-filter: blur(10px);
    }
`;
document.head.appendChild(style);