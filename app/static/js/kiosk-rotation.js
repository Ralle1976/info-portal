/*
Kiosk Rotation JavaScript - Thailand Edition v2.0
================================================
Auto-Rotation System mit Thai-First Display Logic
Monitor-Optimierung und Offline-Fallback
Burn-in Prevention und Performance Monitoring
*/

class KioskRotationSystem {
    constructor(config = {}) {
        // Configuration
        this.config = {
            rotationInterval: 8000,          // 8 seconds per slide
            clockUpdateInterval: 1000,       // Update clock every second
            refreshInterval: 300000,         // Auto-refresh every 5 minutes
            burnInPreventionInterval: 300000, // Pixel shift every 5 minutes
            performanceCheckInterval: 30000,  // Check performance every 30 seconds
            maxMemoryUsage: 50000000,        // 50MB memory limit
            ...config
        };
        
        // State
        this.currentSlide = 0;
        this.totalSlides = 4;
        this.rotationTimer = null;
        this.clockTimer = null;
        this.timerInterval = null;
        this.timeLeft = this.config.rotationInterval / 1000;
        this.isPaused = false;
        this.isOffline = !navigator.onLine;
        this.performanceWarnings = 0;
        this.lastInteraction = Date.now();
        
        // Bangkok timezone for accurate time display
        this.bangkokTimezone = 'Asia/Bangkok';
        
        // DOM Elements (will be set in init)
        this.elements = {};
        
        // Slide names for logging
        this.slideNames = ['NOW', 'TODAY', 'WEEK', 'SERVICES'];
        
        this.init();
    }
    
    init() {
        this.log('🎭 Initializing Kiosk Rotation System v2.0 - Thailand Edition');
        this.logSystemInfo();
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }
    
    setup() {
        this.cacheElements();
        this.setupEventListeners();
        this.startRotation();
        this.startClock();
        this.setupAutoRefresh();
        this.setupBurnInPrevention();
        this.setupPerformanceMonitoring();
        this.setupNetworkMonitoring();
        this.preventDefaultBehaviors();
        this.attemptFullscreen();
        
        this.log('✅ Kiosk Rotation System initialized successfully');
        
        // Show initial slide
        this.showSlide(0);
    }
    
    cacheElements() {
        this.elements = {
            slides: document.querySelectorAll('.rotation-slide'),
            dots: document.querySelectorAll('.progress-dot'),
            timerProgress: document.getElementById('timerProgress'),
            timerText: document.getElementById('timerText'),
            mainClock: document.getElementById('mainClock'),
            offlineBanner: document.querySelector('.offline-banner'),
            rotationContainer: document.querySelector('.rotation-container')
        };
        
        this.totalSlides = this.elements.slides.length;
        this.log(`📱 Found ${this.totalSlides} slides`);
    }
    
    setupEventListeners() {
        // Keyboard controls
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // Progress dot navigation
        this.elements.dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                this.goToSlide(index);
                this.lastInteraction = Date.now();
            });
        });
        
        // Network status monitoring
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
        
        // Visibility change handling
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseRotation();
            } else {
                this.resumeRotation();
            }
        });
        
        // Page unload cleanup
        window.addEventListener('beforeunload', () => this.cleanup());
        
        // Mouse movement detection (for burn-in prevention)
        document.addEventListener('mousemove', () => {
            this.lastInteraction = Date.now();
        });
    }
    
    // ========================
    // Rotation Control
    // ========================
    
    startRotation() {
        if (this.isPaused) return;
        
        this.clearTimers();
        this.timeLeft = this.config.rotationInterval / 1000;
        this.updateTimerDisplay();
        
        // Main rotation timer
        this.rotationTimer = setInterval(() => {
            this.nextSlide();
        }, this.config.rotationInterval);
        
        // Countdown timer
        this.timerInterval = setInterval(() => {
            this.timeLeft--;
            this.updateTimerDisplay();
            
            if (this.timeLeft <= 0) {
                this.timeLeft = this.config.rotationInterval / 1000;
            }
        }, 1000);
        
        this.log('▶️ Rotation started');
    }
    
    pauseRotation() {
        this.isPaused = true;
        this.clearTimers();
        this.log('⏸️ Rotation paused');
    }
    
    resumeRotation() {
        this.isPaused = false;
        this.startRotation();
        this.log('▶️ Rotation resumed');
    }
    
    clearTimers() {
        if (this.rotationTimer) {
            clearInterval(this.rotationTimer);
            this.rotationTimer = null;
        }
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
    
    updateTimerDisplay() {
        if (!this.elements.timerProgress || !this.elements.timerText) return;
        
        const progress = (this.timeLeft / (this.config.rotationInterval / 1000)) * 100;
        this.elements.timerProgress.style.width = `${progress}%`;
        this.elements.timerText.textContent = `${this.timeLeft}s`;
        
        // Visual warning when time is running out
        if (this.timeLeft <= 3) {
            this.elements.timerProgress.style.background = '#FF4444';
            this.elements.timerText.classList.add('text-red-400');
        } else {
            this.elements.timerProgress.style.background = 'linear-gradient(90deg, #00FF88, #40E0D0)';
            this.elements.timerText.classList.remove('text-red-400');
        }
    }
    
    // ========================
    // Slide Navigation
    // ========================
    
    nextSlide() {
        this.goToSlide((this.currentSlide + 1) % this.totalSlides);
    }
    
    prevSlide() {
        this.goToSlide((this.currentSlide - 1 + this.totalSlides) % this.totalSlides);
    }
    
    goToSlide(index) {
        if (index === this.currentSlide) return;
        
        // Remove active states
        this.elements.slides[this.currentSlide]?.classList.remove('active');
        this.elements.slides[this.currentSlide]?.classList.add('prev');
        this.elements.dots[this.currentSlide]?.classList.remove('active');
        
        // Update current slide
        const previousSlide = this.currentSlide;
        this.currentSlide = index;
        
        // Add active states
        this.elements.slides[this.currentSlide]?.classList.add('active');
        this.elements.slides[this.currentSlide]?.classList.remove('prev');
        this.elements.dots[this.currentSlide]?.classList.add('active');
        
        // Clean up prev class after animation
        setTimeout(() => {
            this.elements.slides.forEach((slide, i) => {
                if (i !== this.currentSlide) {
                    slide.classList.remove('prev');
                }
            });
        }, 800);
        
        // Restart rotation timer
        this.startRotation();
        
        // Logging with Thai slide names
        const slideName = this.slideNames[this.currentSlide] || `Slide ${this.currentSlide + 1}`;
        this.log(`📍 Switched to ${slideName} (${this.currentSlide + 1}/${this.totalSlides})`);
        
        // Trigger slide-specific actions
        this.onSlideChange(previousSlide, this.currentSlide);
    }
    
    showSlide(index) {
        this.elements.slides.forEach((slide, i) => {
            slide.classList.toggle('active', i === index);
        });
        this.elements.dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });
        this.currentSlide = index;
    }
    
    onSlideChange(fromIndex, toIndex) {
        // Slide-specific initialization
        const slideElement = this.elements.slides[toIndex];
        if (!slideElement) return;
        
        const slideType = slideElement.dataset.slide;
        
        switch (slideType) {
            case 'now':
                this.initializeNowSlide();
                break;
            case 'today':
                this.initializeTodaySlide();
                break;
            case 'week':
                this.initializeWeekSlide();
                break;
            case 'services':
                this.initializeServicesSlide();
                break;
        }
    }
    
    // ========================
    // Clock Management
    // ========================
    
    startClock() {
        this.updateClock();
        this.clockTimer = setInterval(() => this.updateClock(), this.config.clockUpdateInterval);
    }
    
    updateClock() {
        const now = new Date();
        const bangkokTime = new Date(now.toLocaleString("en-US", {timeZone: this.bangkokTimezone}));
        
        const hours = String(bangkokTime.getHours()).padStart(2, '0');
        const minutes = String(bangkokTime.getMinutes()).padStart(2, '0');
        const seconds = String(bangkokTime.getSeconds()).padStart(2, '0');
        
        const timeString = `${hours}:${minutes}:${seconds}`;
        
        // Update main clock
        if (this.elements.mainClock) {
            // Animated colon opacity based on seconds
            const colonOpacity = bangkokTime.getSeconds() % 2 ? '1' : '0.3';
            this.elements.mainClock.innerHTML = `${hours}<span style="opacity: ${colonOpacity}; transition: opacity 0.3s ease;">:</span>${minutes}<span style="opacity: ${colonOpacity}; transition: opacity 0.3s ease;">:</span>${seconds}`;
        }
        
        // Update all other clocks
        document.querySelectorAll('.clock-display, .digital-clock').forEach(clock => {
            if (clock !== this.elements.mainClock) {
                clock.textContent = timeString;
            }
        });
    }
    
    // ========================
    // Slide Initializers
    // ========================
    
    initializeNowSlide() {
        // Add any NOW slide specific animations or data loading
        this.log('🕐 NOW slide active');
    }
    
    initializeTodaySlide() {
        // Add any TODAY slide specific functionality
        this.log('📅 TODAY slide active');
    }
    
    initializeWeekSlide() {
        // Highlight current day in week view
        const today = new Date().getDay();
        document.querySelectorAll('.day-card').forEach((card, index) => {
            card.classList.toggle('today', index === (today === 0 ? 6 : today - 1));
        });
        this.log('📆 WEEK slide active');
    }
    
    initializeServicesSlide() {
        // Add service-specific animations
        this.log('🏥 SERVICES slide active');
    }
    
    // ========================
    // Keyboard Controls
    // ========================
    
    handleKeyboard(e) {
        // Admin controls with Ctrl+Alt
        if (e.ctrlKey && e.altKey) {
            switch(e.key.toLowerCase()) {
                case 'arrowright':
                    e.preventDefault();
                    this.nextSlide();
                    this.lastInteraction = Date.now();
                    break;
                case 'arrowleft':
                    e.preventDefault();
                    this.prevSlide();
                    this.lastInteraction = Date.now();
                    break;
                case 'p':
                    e.preventDefault();
                    this.isPaused ? this.resumeRotation() : this.pauseRotation();
                    break;
                case 'r':
                    e.preventDefault();
                    this.log('🔄 Admin refresh triggered');
                    location.reload();
                    break;
                case 'f':
                    e.preventDefault();
                    this.toggleFullscreen();
                    break;
                case 'i':
                    e.preventDefault();
                    this.showSystemInfo();
                    break;
                case '1':
                case '2':
                case '3':
                case '4':
                    e.preventDefault();
                    this.goToSlide(parseInt(e.key) - 1);
                    break;
            }
        }
        
        // Prevent common browser shortcuts unless admin mode
        if (!e.ctrlKey || !e.altKey) {
            if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
                e.preventDefault();
            }
            if (e.key === 'F11') {
                e.preventDefault();
            }
        }
    }
    
    // ========================
    // Network Monitoring
    // ========================
    
    handleOnline() {
        this.isOffline = false;
        document.body.classList.remove('offline');
        this.log('🌐 Network connection restored');
        
        // Hide offline banner
        if (this.elements.offlineBanner) {
            this.elements.offlineBanner.style.display = 'none';
        }
        
        // Optionally refresh data
        setTimeout(() => {
            this.log('🔄 Refreshing after network restore...');
            location.reload();
        }, 2000);
    }
    
    handleOffline() {
        this.isOffline = true;
        document.body.classList.add('offline');
        this.log('📵 Network connection lost - entering offline mode');
        
        // Show offline banner with timestamp
        if (this.elements.offlineBanner) {
            const lastUpdateElement = this.elements.offlineBanner.querySelector('#lastUpdate');
            if (lastUpdateElement) {
                const now = new Date();
                lastUpdateElement.textContent = now.toLocaleTimeString('th-TH', {
                    timeZone: this.bangkokTimezone
                });
            }
            this.elements.offlineBanner.style.display = 'block';
            
            // Hide after 10 seconds
            setTimeout(() => {
                if (this.elements.offlineBanner && this.isOffline) {
                    this.elements.offlineBanner.style.display = 'none';
                }
            }, 10000);
        }
    }
    
    // ========================
    // Auto Features
    // ========================
    
    setupAutoRefresh() {
        setTimeout(() => {
            this.log('🔄 Auto-refresh triggered');
            // Smooth refresh with fade
            document.body.style.transition = 'opacity 0.8s ease-out';
            document.body.style.opacity = '0.7';
            
            setTimeout(() => {
                location.reload();
            }, 800);
        }, this.config.refreshInterval);
    }
    
    setupBurnInPrevention() {
        // Subtle pixel shifting to prevent burn-in
        setInterval(() => {
            if (this.elements.rotationContainer && Date.now() - this.lastInteraction > 60000) {
                const x = Math.random() * 4 - 2; // -2 to 2 pixels
                const y = Math.random() * 4 - 2;
                this.elements.rotationContainer.style.transform = `translate(${x}px, ${y}px)`;
                
                // Reset after a short time
                setTimeout(() => {
                    if (this.elements.rotationContainer) {
                        this.elements.rotationContainer.style.transform = '';
                    }
                }, 5000);
            }
        }, this.config.burnInPreventionInterval);
    }
    
    setupPerformanceMonitoring() {
        setInterval(() => {
            if (performance.memory) {
                const usedMemory = performance.memory.usedJSHeapSize;
                
                if (usedMemory > this.config.maxMemoryUsage) {
                    this.performanceWarnings++;
                    this.log(`⚠️ High memory usage: ${Math.round(usedMemory / 1024 / 1024)}MB`);
                    
                    // Reload if memory usage is consistently high
                    if (this.performanceWarnings > 3) {
                        this.log('🔄 Reloading due to high memory usage...');
                        location.reload();
                    }
                } else {
                    this.performanceWarnings = Math.max(0, this.performanceWarnings - 1);
                }
            }
        }, this.config.performanceCheckInterval);
    }
    
    preventDefaultBehaviors() {
        // Prevent text selection
        document.addEventListener('selectstart', (e) => e.preventDefault());
        
        // Prevent context menu
        document.addEventListener('contextmenu', (e) => e.preventDefault());
        
        // Prevent drag and drop
        document.addEventListener('dragstart', (e) => e.preventDefault());
        
        // Prevent image saving
        document.addEventListener('dragstart', (e) => {
            if (e.target.tagName === 'IMG') {
                e.preventDefault();
            }
        });
    }
    
    attemptFullscreen() {
        // Try fullscreen on first user interaction
        let hasInteracted = false;
        
        const tryFullscreen = () => {
            if (!hasInteracted && !document.fullscreenElement) {
                document.documentElement.requestFullscreen()
                    .then(() => {
                        this.log('📺 Auto-fullscreen activated');
                        hasInteracted = true;
                    })
                    .catch((err) => {
                        this.log(`📺 Fullscreen not available: ${err.message}`);
                        hasInteracted = true;
                    });
            }
        };
        
        ['click', 'touchstart', 'keydown'].forEach(event => {
            document.addEventListener(event, tryFullscreen, { once: true });
        });
    }
    
    toggleFullscreen() {
        if (document.fullscreenElement) {
            document.exitFullscreen()
                .then(() => this.log('📺 Fullscreen disabled'));
        } else {
            document.documentElement.requestFullscreen()
                .then(() => this.log('📺 Fullscreen enabled'));
        }
    }
    
    // ========================
    // Utility Functions
    // ========================
    
    showSystemInfo() {
        const info = {
            display: `${window.innerWidth}x${window.innerHeight}`,
            dpr: window.devicePixelRatio,
            currentSlide: `${this.currentSlide + 1}/${this.totalSlides} (${this.slideNames[this.currentSlide]})`,
            rotation: `${this.config.rotationInterval/1000}s intervals`,
            network: navigator.onLine ? 'Online' : 'Offline',
            fullscreen: document.fullscreenElement ? 'Active' : 'Inactive',
            memory: performance.memory ? `${Math.round(performance.memory.usedJSHeapSize / 1024 / 1024)}MB` : 'Unknown',
            platform: navigator.platform,
            userAgent: navigator.userAgent,
            timezone: this.bangkokTimezone,
            paused: this.isPaused,
            timeLeft: `${Math.floor(this.timeLeft / 60)}:${String(this.timeLeft % 60).padStart(2, '0')}`
        };
        
        console.log(`
🖥️ KIOSK ROTATION SYSTEM - THAILAND EDITION v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 Display: ${info.display} (${info.dpr}x DPR)
🎯 Current Slide: ${info.currentSlide}
⏱️ Rotation: ${info.rotation} ${info.paused ? '(PAUSED)' : ''}
⏰ Time Left: ${info.timeLeft}
🌐 Network: ${info.network}
🎯 Fullscreen: ${info.fullscreen}
💾 Memory Usage: ${info.memory}
🌏 Timezone: ${info.timezone}
🔧 Platform: ${info.platform}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEYBOARD SHORTCUTS (Ctrl+Alt+):
→/← : Navigate slides    P: Pause/Resume    R: Refresh    F: Fullscreen
I: This info            1-4: Jump to slide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        `);
    }
    
    log(message) {
        const timestamp = new Date().toLocaleTimeString('th-TH', {
            timeZone: this.bangkokTimezone
        });
        console.log(`[${timestamp}] ${message}`);
    }
    
    logSystemInfo() {
        this.log(`📺 Display: ${window.innerWidth}x${window.innerHeight} @ ${window.devicePixelRatio}x DPR`);
        this.log(`🌏 Language: ${document.documentElement.lang || 'unknown'}`);
        this.log(`⏰ Timezone: ${this.bangkokTimezone}`);
        this.log(`🌐 Network: ${navigator.onLine ? 'Online' : 'Offline'}`);
        this.log(`📱 User Agent: ${navigator.userAgent}`);
    }
    
    cleanup() {
        this.clearTimers();
        if (this.clockTimer) {
            clearInterval(this.clockTimer);
        }
        this.log('🧹 Cleanup completed');
    }
}

// Initialize the kiosk system when DOM is ready
let kioskSystem = null;

document.addEventListener('DOMContentLoaded', () => {
    kioskSystem = new KioskRotationSystem();
});

// Global access for debugging
window.kioskSystem = () => kioskSystem;