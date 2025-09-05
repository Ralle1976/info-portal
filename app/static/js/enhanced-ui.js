/**
 * Enhanced UI/UX JavaScript for QR Info Portal
 * Provides interactive features, animations, and improved user experience
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeEnhancedUI();
});

/**
 * Main initialization function
 */
function initializeEnhancedUI() {
    console.log('🎨 Enhanced UI initializing...');
    
    // Initialize all components
    initializeClock();
    initializeAnimations();
    initializeInteractiveElements();
    initializeFormEnhancements();
    initializeTouchOptimizations();
    initializeLanguageSupport();
    
    console.log('✅ Enhanced UI initialized successfully');
}

/**
 * Live Clock with Bangkok timezone
 */
function initializeClock() {
    function updateAllClocks() {
        const now = new Date();
        const bangkokTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Bangkok"}));
        
        const timeString = bangkokTime.toLocaleTimeString('th-TH', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
        
        const dateString = bangkokTime.toLocaleDateString('de-DE', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        // Update all clock elements
        const clockElements = document.querySelectorAll('#clock, #current-time, #live-time, #header-time');
        clockElements.forEach(element => {
            if (element) {
                element.textContent = timeString;
            }
        });
        
        // Update date elements
        const dateElements = document.querySelectorAll('.current-date');
        dateElements.forEach(element => {
            if (element) {
                element.textContent = dateString;
            }
        });
        
        // Update kiosk time specifically
        const kioskTime = document.getElementById('kiosk-time');
        if (kioskTime) {
            kioskTime.textContent = timeString;
        }
    }
    
    // Update immediately and then every second
    updateAllClocks();
    setInterval(updateAllClocks, 1000);
}

/**
 * Animation system
 */
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                entry.target.classList.add('animate-slide-up');
            }
        });
    }, observerOptions);
    
    // Observe all cards and animated elements
    const animatedElements = document.querySelectorAll('.card-enhanced, .animate-on-scroll');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(el);
    });
    
    // Staggered animation for multiple cards
    const cards = document.querySelectorAll('.card-enhanced');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.animationDelay = `${index * 0.1}s`;
        }, index * 50);
    });
}

/**
 * Interactive elements enhancements
 */
function initializeInteractiveElements() {
    // Enhanced hover effects for buttons
    const buttons = document.querySelectorAll('.btn-enhanced, .nav-item-enhanced, .lang-option');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
        
        // Touch feedback for mobile
        button.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        button.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Status indicator pulse animation
    const statusIndicators = document.querySelectorAll('.status-pulse');
    statusIndicators.forEach(indicator => {
        setInterval(() => {
            indicator.style.opacity = '0.7';
            setTimeout(() => {
                indicator.style.opacity = '1';
            }, 500);
        }, 2000);
    });
    
    // Interactive contact cards
    const contactCards = document.querySelectorAll('[href^="tel:"], [href^="mailto:"]');
    contactCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Add click feedback
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
            
            // Show confirmation for mobile
            if (window.innerWidth <= 768) {
                const type = this.href.startsWith('tel:') ? 'Telefon' : 'E-Mail';
                showNotification(`${type} wird geöffnet...`, 'info', 2000);
            }
        });
    });
}

/**
 * Form enhancements
 */
function initializeFormEnhancements() {
    const forms = document.querySelectorAll('.admin-form, form');
    forms.forEach(form => {
        // Enhanced validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            // Real-time validation feedback
            input.addEventListener('blur', function() {
                validateInput(this);
            });
            
            // Clear validation on focus
            input.addEventListener('focus', function() {
                this.classList.remove('border-red-500', 'border-green-500');
            });
            
            // Auto-resize textareas
            if (input.tagName === 'TEXTAREA') {
                input.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = this.scrollHeight + 'px';
                });
            }
        });
        
        // Form submission with loading state
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Wird gespeichert...';
                submitBtn.disabled = true;
            }
        });
    });
}

/**
 * Input validation helper
 */
function validateInput(input) {
    const value = input.value.trim();
    const isRequired = input.hasAttribute('required');
    const type = input.type;
    
    let isValid = true;
    
    if (isRequired && !value) {
        isValid = false;
    } else if (type === 'email' && value && !isValidEmail(value)) {
        isValid = false;
    } else if (type === 'tel' && value && !isValidPhone(value)) {
        isValid = false;
    }
    
    if (isValid) {
        input.classList.remove('border-red-500');
        input.classList.add('border-green-500');
    } else {
        input.classList.remove('border-green-500');
        input.classList.add('border-red-500');
    }
    
    return isValid;
}

/**
 * Email validation
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Phone validation (basic)
 */
function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[0-9\s\-\(\)]{8,}$/;
    return phoneRegex.test(phone);
}

/**
 * Touch and mobile optimizations
 */
function initializeTouchOptimizations() {
    // Improve touch targets
    const smallTargets = document.querySelectorAll('a, button');
    smallTargets.forEach(target => {
        const rect = target.getBoundingClientRect();
        if (rect.width < 44 || rect.height < 44) {
            target.style.minWidth = '44px';
            target.style.minHeight = '44px';
            target.style.display = 'inline-flex';
            target.style.alignItems = 'center';
            target.style.justifyContent = 'center';
        }
    });
    
    // Prevent zoom on input focus (iOS Safari)
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        if (input.style.fontSize === '' || parseFloat(input.style.fontSize) < 16) {
            input.style.fontSize = '16px';
        }
    });
    
    // Swipe gestures for mobile navigation
    let touchStartX = 0;
    let touchStartY = 0;
    
    document.addEventListener('touchstart', function(e) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchend', function(e) {
        if (!touchStartX || !touchStartY) return;
        
        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;
        
        const diffX = touchStartX - touchEndX;
        const diffY = touchStartY - touchEndY;
        
        // Horizontal swipe detection
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
            if (diffX > 0) {
                // Swipe left - next page
                handleSwipeLeft();
            } else {
                // Swipe right - previous page
                handleSwipeRight();
            }
        }
    });
}

/**
 * Swipe gesture handlers
 */
function handleSwipeLeft() {
    const currentPath = window.location.pathname;
    if (currentPath === '/') {
        window.location.href = '/week';
    } else if (currentPath === '/week') {
        window.location.href = '/month';
    }
}

function handleSwipeRight() {
    const currentPath = window.location.pathname;
    if (currentPath === '/month') {
        window.location.href = '/week';
    } else if (currentPath === '/week') {
        window.location.href = '/';
    }
}

/**
 * Language-specific enhancements
 */
function initializeLanguageSupport() {
    const lang = document.documentElement.lang || 'de';
    
    // Apply language-specific CSS classes
    document.body.classList.add(`lang-${lang}`);
    
    // Adjust typography for Thai text
    if (lang === 'th') {
        const textElements = document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6');
        textElements.forEach(el => {
            if (containsThaiText(el.textContent)) {
                el.style.lineHeight = '1.7';
                el.style.letterSpacing = '0.025em';
            }
        });
    }
}

/**
 * Check if text contains Thai characters
 */
function containsThaiText(text) {
    const thaiRegex = /[\u0E00-\u0E7F]/;
    return thaiRegex.test(text);
}

/**
 * Enhanced notification system
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} show`;
    
    const iconMap = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">
                <i class="fas ${iconMap[type] || iconMap.info}"></i>
            </div>
            <div class="flex-1">
                <p class="font-medium">${message}</p>
            </div>
            <button onclick="this.closest('.notification').remove()" class="text-gray-400 hover:text-gray-600 ml-2">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove notification
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }, duration);
    
    return notification;
}

/**
 * Loading overlay system
 */
function showLoading(message = 'Lädt...') {
    const existingOverlay = document.getElementById('global-loading');
    if (existingOverlay) return;
    
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'global-loading';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <p class="font-medium mt-4">${message}</p>
        </div>
    `;
    
    document.body.appendChild(overlay);
    return overlay;
}

function hideLoading() {
    const overlay = document.getElementById('global-loading');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => {
            overlay.remove();
        }, 300);
    }
}

/**
 * Accessibility enhancements
 */
function initializeAccessibility() {
    // Skip link for keyboard navigation
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Zum Hauptinhalt springen';
    skipLink.className = 'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-thai-turquoise text-white px-4 py-2 rounded z-50';
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add main content landmark
    const main = document.querySelector('main');
    if (main && !main.id) {
        main.id = 'main-content';
    }
    
    // Improve button accessibility
    const buttons = document.querySelectorAll('button, [role="button"]');
    buttons.forEach(button => {
        if (!button.getAttribute('aria-label') && !button.textContent.trim()) {
            button.setAttribute('aria-label', 'Button');
        }
    });
    
    // Announce page changes for screen readers
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                const announcement = document.createElement('div');
                announcement.setAttribute('aria-live', 'polite');
                announcement.setAttribute('aria-atomic', 'true');
                announcement.className = 'sr-only';
                announcement.textContent = 'Seite wurde aktualisiert';
                document.body.appendChild(announcement);
                
                setTimeout(() => {
                    announcement.remove();
                }, 1000);
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

/**
 * Performance optimizations
 */
function initializePerformanceOptimizations() {
    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => imageObserver.observe(img));
    }
    
    // Debounced scroll handler
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        if (scrollTimeout) clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            // Handle scroll-dependent operations here
            updateScrollProgress();
        }, 16); // ~60fps
    }, { passive: true });
}

/**
 * Update scroll progress indicator
 */
function updateScrollProgress() {
    const scrollTop = window.pageYOffset;
    const docHeight = document.body.scrollHeight - window.innerHeight;
    const scrollPercent = (scrollTop / docHeight) * 100;
    
    const progressBar = document.getElementById('scroll-progress');
    if (progressBar) {
        progressBar.style.width = scrollPercent + '%';
    }
}

/**
 * Error handling
 */
window.addEventListener('error', (e) => {
    console.error('JavaScript Error:', e.error);
    // Only show user-friendly errors, not technical ones
    if (e.error && !e.error.stack) {
        showNotification('Ein Fehler ist aufgetreten. Seite wird aktualisiert.', 'error', 3000);
        setTimeout(() => window.location.reload(), 3000);
    }
});

// Export functions for global use
window.enhancedUI = {
    showNotification,
    showLoading,
    hideLoading,
    validateInput,
    updateScrollProgress
};