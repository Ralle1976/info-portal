/**
 * KIOSK PERFORMANCE OPTIMIZATIONS
 * Version: 1.0
 * Purpose: Eliminate flicker and improve performance for long-running kiosk displays
 */

class KioskPerformanceManager {
    constructor() {
        this.config = {
            refreshInterval: 120000, // 2 minutes
            contentRefreshUrl: '/api/kiosk/refresh',
            maxRetries: 3,
            performanceThreshold: 30, // FPS
            memoryThreshold: 100, // MB
            cacheDuration: 60000 // 1 minute
        };
        
        this.cache = new Map();
        this.retryCount = 0;
        this.performanceMetrics = {
            fps: 0,
            memoryUsage: 0,
            renderTime: 0
        };
        
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing Kiosk Performance Manager...');
        
        this.initializeFlickerFreeRefresh();
        this.initializeMemoryOptimization();
        this.initializeRenderOptimization();
        this.initializeNetworkOptimization();
        this.initializePerformanceMonitoring();
        
        console.log('✅ Performance Manager initialized');
    }
    
    /**
     * FLICKER-FREE AUTO-REFRESH SYSTEM
     */
    initializeFlickerFreeRefresh() {
        let refreshTimeLeft = this.config.refreshInterval / 1000;
        
        const updateContent = async () => {
            try {
                // Pre-fetch content in background
                const response = await fetch(window.location.pathname + '?ajax=1', {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                    cache: 'no-cache'
                });
                
                if (response.ok) {
                    const html = await response.text();
                    
                    // Parse and update only changed content
                    const parser = new DOMParser();
                    const newDoc = parser.parseFromString(html, 'text/html');
                    
                    // Update specific sections without page reload
                    this.updateContentSections(newDoc);
                    
                    console.log('🔄 Content refreshed seamlessly');
                    this.retryCount = 0;
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (error) {
                console.warn('⚠️ Content refresh failed, falling back to page reload:', error);
                this.retryCount++;
                
                if (this.retryCount >= this.config.maxRetries) {
                    // Smooth page reload as last resort
                    this.performSmoothReload();
                }
            }
        };
        
        const updateTimer = () => {
            if (refreshTimeLeft <= 0) {
                updateContent();
                refreshTimeLeft = this.config.refreshInterval / 1000;
                return;
            }
            refreshTimeLeft--;
        };
        
        setInterval(updateTimer, 1000);
        console.log('🔄 Flicker-free refresh initialized');
    }
    
    /**
     * Update content sections without full page reload
     */
    updateContentSections(newDoc) {
        const sectionsToUpdate = [
            '.kiosk-status-banner',
            '.kiosk-hours-section',
            '.kiosk-week-grid',
            '.kiosk-preview-list',
            '#clock',
            '.kiosk-date'
        ];
        
        sectionsToUpdate.forEach(selector => {
            const currentElement = document.querySelector(selector);
            const newElement = newDoc.querySelector(selector);
            
            if (currentElement && newElement) {
                // Fade out, update, fade in
                currentElement.style.transition = 'opacity 0.3s ease';
                currentElement.style.opacity = '0.7';
                
                setTimeout(() => {
                    currentElement.innerHTML = newElement.innerHTML;
                    currentElement.style.opacity = '1';
                }, 300);
            }
        });
    }
    
    /**
     * Smooth reload with minimal flicker
     */
    performSmoothReload() {
        // Create overlay
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, #F0FDF4, #E0F2FE);
            display: flex; align-items: center; justify-content: center;
            z-index: 10000; opacity: 0;
            transition: opacity 0.5s ease;
        `;
        overlay.innerHTML = `
            <div style="text-align: center; color: #00A86B;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">
                    <i class="fas fa-sync-alt fa-spin"></i>
                </div>
                <div style="font-size: 1.5rem; font-weight: 600;">
                    กำลังปรับปรุงข้อมูล<br>
                    <span style="font-size: 1rem; opacity: 0.7;">Updating Information</span>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Smooth fade in
        requestAnimationFrame(() => {
            overlay.style.opacity = '1';
            
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        });
    }
    
    /**
     * MEMORY OPTIMIZATION
     */
    initializeMemoryOptimization() {
        // Cleanup unused DOM elements
        const cleanup = () => {
            // Remove hidden elements
            document.querySelectorAll('[style*="display: none"]').forEach(el => {
                if (!el.dataset.keepHidden) {
                    el.remove();
                }
            });
            
            // Clean up old notifications
            document.querySelectorAll('.kiosk-notification, .kiosk-error-indicator').forEach(el => {
                if (Date.now() - parseInt(el.dataset.created || '0') > 10000) {
                    el.remove();
                }
            });
            
            // Force garbage collection if available
            if (window.gc) {
                window.gc();
            }
        };
        
        // Run cleanup every 5 minutes
        setInterval(cleanup, 5 * 60 * 1000);
        
        // Monitor memory usage
        if (performance.memory) {
            setInterval(() => {
                const memUsage = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024);
                this.performanceMetrics.memoryUsage = memUsage;
                
                if (memUsage > this.config.memoryThreshold) {
                    console.warn(`⚠️ High memory usage: ${memUsage}MB`);
                    cleanup();
                    
                    if (memUsage > this.config.memoryThreshold * 1.5) {
                        console.log('🔄 Reloading due to memory pressure...');
                        this.performSmoothReload();
                    }
                }
            }, 30000);
        }
        
        console.log('💾 Memory optimization initialized');
    }
    
    /**
     * RENDER OPTIMIZATION
     */
    initializeRenderOptimization() {
        // Use GPU acceleration for animations
        const acceleratedElements = document.querySelectorAll('.enhanced-card, .kiosk-column, .kiosk-time-card');
        acceleratedElements.forEach(el => {
            el.style.willChange = 'transform, opacity';
            el.style.transform = 'translateZ(0)'; // Force GPU layer
        });
        
        // Optimize clock updates to reduce repaints
        this.optimizeClockUpdates();
        
        // Use intersection observer for viewport optimizations
        this.initializeViewportOptimization();
        
        console.log('🎨 Render optimization initialized');
    }
    
    /**
     * Optimize clock updates to reduce DOM thrashing
     */
    optimizeClockUpdates() {
        const clockElement = document.getElementById('clock');
        if (!clockElement) return;
        
        let lastTimeString = '';
        
        const updateClock = () => {
            const now = new Date();
            const bangkokTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Bangkok"}));
            
            const hours = String(bangkokTime.getHours()).padStart(2, '0');
            const minutes = String(bangkokTime.getMinutes()).padStart(2, '0');
            const seconds = String(bangkokTime.getSeconds()).padStart(2, '0');
            const timeString = `${hours}:${minutes}:${seconds}`;
            
            // Only update if time actually changed
            if (timeString !== lastTimeString) {
                const colonOpacity = bangkokTime.getSeconds() % 2 ? '1' : '0.3';
                
                // Use innerHTML only when necessary, textContent for time
                if (clockElement.innerHTML.includes(':')) {
                    clockElement.innerHTML = `${hours}<span style="opacity: ${colonOpacity}; transition: opacity 0.3s ease;">:</span>${minutes}<span style="opacity: ${colonOpacity}; transition: opacity 0.3s ease;">:</span>${seconds}`;
                } else {
                    clockElement.textContent = timeString;
                }
                
                lastTimeString = timeString;
            }
        };
        
        // Use requestAnimationFrame for smoother updates
        const clockTick = () => {
            updateClock();
            requestAnimationFrame(clockTick);
        };
        
        requestAnimationFrame(clockTick);
    }
    
    /**
     * Viewport optimization with Intersection Observer
     */
    initializeViewportOptimization() {
        if (!window.IntersectionObserver) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-viewport');
                    // Enable animations for visible elements
                    entry.target.style.animationPlayState = 'running';
                } else {
                    entry.target.classList.remove('in-viewport');
                    // Pause animations for hidden elements
                    entry.target.style.animationPlayState = 'paused';
                }
            });
        }, {
            rootMargin: '50px',
            threshold: 0.1
        });
        
        // Observe animated elements
        document.querySelectorAll('.enhanced-fade-in, .kiosk-time-card, .status-icon-animate').forEach(el => {
            observer.observe(el);
        });
        
        console.log('👁️ Viewport optimization initialized');
    }
    
    /**
     * NETWORK OPTIMIZATION
     */
    initializeNetworkOptimization() {
        // Cache frequently accessed resources
        this.initializeSmartCaching();
        
        // Preload next refresh content
        this.preloadContent();
        
        console.log('🌐 Network optimization initialized');
    }
    
    /**
     * Smart caching system
     */
    initializeSmartCaching() {
        const originalFetch = window.fetch;
        
        window.fetch = async (url, options = {}) => {
            const cacheKey = `${url}_${JSON.stringify(options)}`;
            const cached = this.cache.get(cacheKey);
            
            if (cached && Date.now() - cached.timestamp < this.config.cacheDuration) {
                console.log(`📦 Cache hit: ${url}`);
                return new Response(cached.data);
            }
            
            try {
                const response = await originalFetch(url, options);
                
                if (response.ok) {
                    const clonedResponse = response.clone();
                    const data = await clonedResponse.text();
                    
                    this.cache.set(cacheKey, {
                        data,
                        timestamp: Date.now()
                    });
                    
                    console.log(`📦 Cache stored: ${url}`);
                }
                
                return response;
            } catch (error) {
                console.warn(`🌐 Network error: ${url}`, error);
                throw error;
            }
        };
    }
    
    /**
     * Preload content for faster refresh
     */
    preloadContent() {
        // Preload next refresh 10 seconds before it's needed
        setInterval(() => {
            const preloadUrl = window.location.pathname + '?ajax=1&preload=1';
            
            fetch(preloadUrl, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                cache: 'no-cache'
            }).catch(() => {
                // Ignore preload errors
            });
        }, (this.config.refreshInterval - 10000));
        
        console.log('📡 Content preloading initialized');
    }
    
    /**
     * PERFORMANCE MONITORING
     */
    initializePerformanceMonitoring() {
        let frameCount = 0;
        let lastTime = performance.now();
        
        const measureFPS = () => {
            frameCount++;
            const currentTime = performance.now();
            
            if (currentTime >= lastTime + 1000) {
                this.performanceMetrics.fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
                frameCount = 0;
                lastTime = currentTime;
                
                // Log performance issues
                if (this.performanceMetrics.fps < this.config.performanceThreshold) {
                    console.warn(`⚠️ Low FPS detected: ${this.performanceMetrics.fps}`);
                }
            }
            
            requestAnimationFrame(measureFPS);
        };
        
        requestAnimationFrame(measureFPS);
        
        // Performance summary every minute
        setInterval(() => {
            const summary = {
                fps: this.performanceMetrics.fps,
                memory: this.performanceMetrics.memoryUsage,
                cacheSize: this.cache.size,
                uptime: Math.floor((Date.now() - this.startTime) / 60000)
            };
            
            console.log('📊 Performance Summary:', summary);
        }, 60000);
        
        console.log('📊 Performance monitoring initialized');
    }
    
    /**
     * Get performance metrics
     */
    getMetrics() {
        return {
            ...this.performanceMetrics,
            cacheSize: this.cache.size,
            retryCount: this.retryCount
        };
    }
    
    /**
     * Cleanup
     */
    destroy() {
        console.log('🧹 Cleaning up Performance Manager...');
        this.cache.clear();
    }
}

// Auto-initialize for kiosk pages
if (document.querySelector('[data-kiosk]') || document.body.classList.contains('kiosk-mode')) {
    document.addEventListener('DOMContentLoaded', () => {
        window.kioskPerformance = new KioskPerformanceManager();
    });
}

// Export for manual initialization
window.KioskPerformanceManager = KioskPerformanceManager;