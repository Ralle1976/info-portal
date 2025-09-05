/**
 * Design System JavaScript
 * Advanced UI/UX interactions for QR Info Portal
 */

// Design System Configuration
const DesignSystem = {
  themes: {
    'default': 'thai-turquoise',
    'medical-professional': 'Medical Professional',
    'thai-cultural': 'Thai Cultural Heritage',
    'modern-minimal': 'Modern Minimal',
    'high-contrast': 'High Contrast',
    'dark-mode': 'Dark Mode',
    'warm-sunset': 'Warm Sunset',
    'ocean-breeze': 'Ocean Breeze'
  },
  
  animations: {
    duration: 300,
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
  },
  
  breakpoints: {
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
    '2xl': 1536
  }
};

// Initialize Design System
document.addEventListener('DOMContentLoaded', function() {
  console.log('🎨 Initializing Design System...');
  
  // Initialize all modules
  initializeThemeSystem();
  initializeAnimations();
  initializeAccessibility();
  initializeStatusIndicators();
  initializeFormEnhancements();
  initializeModalSystem();
  initializeNotificationSystem();
  initializeKioskMode();
  initializePerformanceOptimizations();
  
  console.log('✅ Design System initialized successfully');
});

/**
 * Theme System Management
 */
function initializeThemeSystem() {
  // Get saved theme or default
  const savedTheme = localStorage.getItem('qr-portal-theme') || 'default';
  applyTheme(savedTheme);
  
  // Create theme switcher if it doesn't exist
  if (!document.querySelector('.theme-switcher')) {
    createThemeSwitcher();
  }
}

function createThemeSwitcher() {
  const switcher = document.createElement('div');
  switcher.className = 'theme-switcher';
  switcher.innerHTML = `
    <button class="theme-switcher-toggle" aria-label="Change theme" id="theme-toggle">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="5"/>
        <path d="M12 1v6m0 6v6m-9-9h6m6 0h6m-5.64-6.36l4.24 4.24m-4.24 4.24l4.24 4.24m-12.72 0l4.24-4.24m0-4.24l-4.24-4.24"/>
      </svg>
    </button>
    <div class="theme-switcher-menu" id="theme-menu">
      ${Object.entries(DesignSystem.themes).map(([value, label]) => `
        <div class="theme-option" data-theme-value="${value}">
          <div class="theme-preview">
            <div class="theme-preview-primary"></div>
            <div class="theme-preview-secondary"></div>
          </div>
          <span>${label}</span>
        </div>
      `).join('')}
    </div>
  `;
  
  document.body.appendChild(switcher);
  
  // Add event listeners
  const toggle = switcher.querySelector('#theme-toggle');
  const menu = switcher.querySelector('#theme-menu');
  const options = switcher.querySelectorAll('.theme-option');
  
  toggle.addEventListener('click', () => {
    menu.classList.toggle('active');
    toggle.setAttribute('aria-expanded', menu.classList.contains('active'));
  });
  
  options.forEach(option => {
    option.addEventListener('click', () => {
      const theme = option.dataset.themeValue;
      applyTheme(theme);
      menu.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });
  
  // Close menu when clicking outside
  document.addEventListener('click', (e) => {
    if (!switcher.contains(e.target)) {
      menu.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('qr-portal-theme', theme);
  
  // Update active state in theme menu
  document.querySelectorAll('.theme-option').forEach(option => {
    option.classList.toggle('active', option.dataset.themeValue === theme);
  });
  
  // Dispatch theme change event
  window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
}

/**
 * Enhanced Animation System
 */
function initializeAnimations() {
  // Intersection Observer for scroll animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  
  const animationObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        
        // Add stagger delay for child elements
        const children = entry.target.querySelectorAll('.animate-child');
        children.forEach((child, index) => {
          child.style.animationDelay = `${index * 50}ms`;
          child.classList.add('animate-in');
        });
      }
    });
  }, observerOptions);
  
  // Observe all animatable elements
  const animatableElements = document.querySelectorAll('.animate-on-scroll, .card, .status-banner');
  animatableElements.forEach(el => animationObserver.observe(el));
  
  // Page transition animations
  addPageTransitions();
}

function addPageTransitions() {
  // Fade in on page load
  document.body.style.opacity = '0';
  window.addEventListener('load', () => {
    document.body.style.transition = 'opacity 0.3s ease-out';
    document.body.style.opacity = '1';
  });
  
  // Smooth page transitions for navigation
  document.querySelectorAll('a[href^="/"]').forEach(link => {
    link.addEventListener('click', (e) => {
      if (!e.ctrlKey && !e.metaKey && !link.hasAttribute('data-no-transition')) {
        e.preventDefault();
        const href = link.getAttribute('href');
        
        document.body.style.opacity = '0';
        setTimeout(() => {
          window.location.href = href;
        }, 300);
      }
    });
  });
}

/**
 * Accessibility Enhancements
 */
function initializeAccessibility() {
  // Add skip links if not present
  if (!document.querySelector('.skip-links')) {
    const skipLinks = document.createElement('div');
    skipLinks.innerHTML = `
      <a href="#main-content" class="skip-links">Skip to main content</a>
      <a href="#navigation" class="skip-links">Skip to navigation</a>
    `;
    document.body.insertBefore(skipLinks, document.body.firstChild);
  }
  
  // Enhance keyboard navigation
  enhanceKeyboardNavigation();
  
  // Add ARIA live regions
  createAriaLiveRegions();
  
  // Enhance focus management
  enhanceFocusManagement();
}

function enhanceKeyboardNavigation() {
  // Add keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    // Alt + T: Toggle theme
    if (e.altKey && e.key === 't') {
      e.preventDefault();
      document.querySelector('#theme-toggle')?.click();
    }
    
    // Alt + H: Go home
    if (e.altKey && e.key === 'h') {
      e.preventDefault();
      window.location.href = '/';
    }
    
    // Escape: Close modals/menus
    if (e.key === 'Escape') {
      closeAllModals();
      closeAllMenus();
    }
  });
  
  // Enhance tab navigation
  const tabbableElements = 'a[href], button, input, textarea, select, [tabindex]:not([tabindex="-1"])';
  const tabbables = document.querySelectorAll(tabbableElements);
  
  tabbables.forEach(el => {
    el.addEventListener('focus', () => {
      el.classList.add('keyboard-focus');
    });
    
    el.addEventListener('blur', () => {
      el.classList.remove('keyboard-focus');
    });
  });
}

function createAriaLiveRegions() {
  // Status announcements
  if (!document.querySelector('#aria-status')) {
    const statusRegion = document.createElement('div');
    statusRegion.id = 'aria-status';
    statusRegion.setAttribute('aria-live', 'polite');
    statusRegion.setAttribute('aria-atomic', 'true');
    statusRegion.className = 'sr-only';
    document.body.appendChild(statusRegion);
  }
  
  // Alert announcements
  if (!document.querySelector('#aria-alerts')) {
    const alertRegion = document.createElement('div');
    alertRegion.id = 'aria-alerts';
    alertRegion.setAttribute('aria-live', 'assertive');
    alertRegion.setAttribute('aria-atomic', 'true');
    alertRegion.className = 'sr-only';
    document.body.appendChild(alertRegion);
  }
}

function enhanceFocusManagement() {
  // Trap focus in modals
  document.addEventListener('keydown', (e) => {
    const activeModal = document.querySelector('.modal.active');
    if (activeModal && e.key === 'Tab') {
      const focusables = activeModal.querySelectorAll('a[href], button, input, textarea, select, [tabindex]:not([tabindex="-1"])');
      const firstFocusable = focusables[0];
      const lastFocusable = focusables[focusables.length - 1];
      
      if (e.shiftKey && document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable.focus();
      } else if (!e.shiftKey && document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable.focus();
      }
    }
  });
}

/**
 * Status Indicator Enhancements
 */
function initializeStatusIndicators() {
  const statusElements = document.querySelectorAll('.status-indicator, .status-banner');
  
  statusElements.forEach(element => {
    // Add pulse animation for open status
    if (element.classList.contains('status-open')) {
      addPulseAnimation(element);
    }
    
    // Add attention animation for warnings
    if (element.classList.contains('status-warning')) {
      addAttentionAnimation(element);
    }
    
    // Enhance with live updates
    if (element.dataset.liveUpdate) {
      initializeLiveStatusUpdate(element);
    }
  });
}

function addPulseAnimation(element) {
  const dot = document.createElement('span');
  dot.className = 'status-indicator-dot';
  element.prepend(dot);
}

function addAttentionAnimation(element) {
  setInterval(() => {
    element.classList.add('animate-shake');
    setTimeout(() => {
      element.classList.remove('animate-shake');
    }, 500);
  }, 5000);
}

function initializeLiveStatusUpdate(element) {
  const updateInterval = parseInt(element.dataset.updateInterval) || 60000;
  
  setInterval(async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      updateStatusElement(element, data);
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  }, updateInterval);
}

/**
 * Form Enhancement System
 */
function initializeFormEnhancements() {
  // Floating labels
  initializeFloatingLabels();
  
  // Real-time validation
  initializeFormValidation();
  
  // Enhanced select boxes
  initializeCustomSelects();
  
  // Form progress indicators
  initializeFormProgress();
}

function initializeFloatingLabels() {
  const floatingInputs = document.querySelectorAll('.form-floating-input');
  
  floatingInputs.forEach(input => {
    // Check initial state
    if (input.value) {
      input.classList.add('has-value');
    }
    
    // Update on input
    input.addEventListener('input', () => {
      input.classList.toggle('has-value', input.value.length > 0);
    });
    
    // Update on focus/blur
    input.addEventListener('focus', () => {
      input.parentElement.classList.add('focused');
    });
    
    input.addEventListener('blur', () => {
      input.parentElement.classList.remove('focused');
    });
  });
}

function initializeFormValidation() {
  const forms = document.querySelectorAll('form[data-validate]');
  
  forms.forEach(form => {
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
      input.addEventListener('blur', () => validateField(input));
      input.addEventListener('input', () => {
        if (input.classList.contains('is-invalid')) {
          validateField(input);
        }
      });
    });
    
    form.addEventListener('submit', (e) => {
      let isValid = true;
      
      inputs.forEach(input => {
        if (!validateField(input)) {
          isValid = false;
        }
      });
      
      if (!isValid) {
        e.preventDefault();
        showNotification('Please fix the errors in the form', 'error');
      }
    });
  });
}

function validateField(field) {
  const value = field.value.trim();
  const isRequired = field.hasAttribute('required');
  const type = field.type;
  const pattern = field.getAttribute('pattern');
  
  let isValid = true;
  let errorMessage = '';
  
  // Required validation
  if (isRequired && !value) {
    isValid = false;
    errorMessage = 'This field is required';
  }
  
  // Type validation
  else if (value) {
    switch (type) {
      case 'email':
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
          isValid = false;
          errorMessage = 'Please enter a valid email address';
        }
        break;
        
      case 'tel':
        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{8,}$/;
        if (!phoneRegex.test(value)) {
          isValid = false;
          errorMessage = 'Please enter a valid phone number';
        }
        break;
        
      case 'url':
        try {
          new URL(value);
        } catch {
          isValid = false;
          errorMessage = 'Please enter a valid URL';
        }
        break;
    }
    
    // Pattern validation
    if (isValid && pattern) {
      const regex = new RegExp(pattern);
      if (!regex.test(value)) {
        isValid = false;
        errorMessage = field.getAttribute('data-pattern-error') || 'Invalid format';
      }
    }
  }
  
  // Update field state
  field.classList.toggle('is-valid', isValid && value);
  field.classList.toggle('is-invalid', !isValid);
  
  // Update error message
  const errorElement = field.parentElement.querySelector('.form-error');
  if (errorElement) {
    errorElement.textContent = errorMessage;
    errorElement.style.display = isValid ? 'none' : 'block';
  }
  
  return isValid;
}

/**
 * Modal System
 */
function initializeModalSystem() {
  // Auto-initialize modals
  document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const modalId = trigger.dataset.modalTrigger;
      openModal(modalId);
    });
  });
  
  // Close buttons
  document.querySelectorAll('[data-modal-close]').forEach(closeBtn => {
    closeBtn.addEventListener('click', () => {
      const modal = closeBtn.closest('.modal');
      if (modal) {
        closeModal(modal.id);
      }
    });
  });
  
  // Backdrop clicks
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', () => {
      const modalId = backdrop.dataset.modalId;
      if (modalId) {
        closeModal(modalId);
      }
    });
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  const backdrop = document.querySelector(`[data-modal-id="${modalId}"]`) || createModalBackdrop(modalId);
  
  if (modal) {
    // Show backdrop
    backdrop.classList.add('active');
    
    // Show modal
    setTimeout(() => {
      modal.classList.add('active');
      
      // Focus first focusable element
      const firstFocusable = modal.querySelector('a[href], button, input, textarea, select, [tabindex]:not([tabindex="-1"])');
      if (firstFocusable) {
        firstFocusable.focus();
      }
      
      // Announce to screen readers
      announceToScreenReader(`${modal.querySelector('.modal-title')?.textContent || 'Modal'} opened`);
    }, 50);
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  const backdrop = document.querySelector(`[data-modal-id="${modalId}"]`);
  
  if (modal) {
    modal.classList.remove('active');
    
    if (backdrop) {
      setTimeout(() => {
        backdrop.classList.remove('active');
      }, 300);
    }
    
    // Restore body scroll
    document.body.style.overflow = '';
    
    // Return focus to trigger
    const trigger = document.querySelector(`[data-modal-trigger="${modalId}"]`);
    if (trigger) {
      trigger.focus();
    }
    
    // Announce to screen readers
    announceToScreenReader('Modal closed');
  }
}

function closeAllModals() {
  document.querySelectorAll('.modal.active').forEach(modal => {
    closeModal(modal.id);
  });
}

function createModalBackdrop(modalId) {
  const backdrop = document.createElement('div');
  backdrop.className = 'modal-backdrop';
  backdrop.dataset.modalId = modalId;
  document.body.appendChild(backdrop);
  return backdrop;
}

/**
 * Notification System
 */
function initializeNotificationSystem() {
  // Create notification container if it doesn't exist
  if (!document.querySelector('#notification-container')) {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.className = 'fixed top-4 right-4 z-50 pointer-events-none';
    document.body.appendChild(container);
  }
}

function showNotification(message, type = 'info', duration = 5000, options = {}) {
  const container = document.getElementById('notification-container');
  const id = `notification-${Date.now()}`;
  
  const notification = document.createElement('div');
  notification.id = id;
  notification.className = `notification notification-${type} pointer-events-auto transform translate-x-full`;
  
  const icons = {
    success: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>',
    error: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>',
    warning: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>',
    info: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>'
  };
  
  notification.innerHTML = `
    <div class="notification-header">
      <div class="notification-icon">
        ${icons[type] || icons.info}
      </div>
      <div class="notification-content">
        ${options.title ? `<div class="notification-title">${options.title}</div>` : ''}
        <div class="notification-message">${message}</div>
      </div>
      <button class="notification-close" onclick="dismissNotification('${id}')">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
        </svg>
      </button>
    </div>
  `;
  
  container.appendChild(notification);
  
  // Trigger animation
  requestAnimationFrame(() => {
    notification.classList.remove('translate-x-full');
    notification.classList.add('notification-visible');
  });
  
  // Announce to screen readers
  announceToScreenReader(message, type === 'error' ? 'assertive' : 'polite');
  
  // Auto dismiss
  if (duration > 0) {
    setTimeout(() => {
      dismissNotification(id);
    }, duration);
  }
  
  return id;
}

function dismissNotification(id) {
  const notification = document.getElementById(id);
  if (notification) {
    notification.classList.add('translate-x-full');
    notification.classList.remove('notification-visible');
    
    setTimeout(() => {
      notification.remove();
    }, 300);
  }
}

/**
 * Kiosk Mode Enhancements
 */
function initializeKioskMode() {
  if (document.body.classList.contains('kiosk-mode')) {
    // Prevent context menu
    document.addEventListener('contextmenu', (e) => e.preventDefault());
    
    // Prevent text selection
    document.body.style.userSelect = 'none';
    
    // Auto-refresh
    const refreshInterval = parseInt(document.body.dataset.kioskRefresh) || 300000; // 5 minutes default
    setInterval(() => {
      window.location.reload();
    }, refreshInterval);
    
    // Full screen on click
    document.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {
          console.log('Fullscreen request failed:', err);
        });
      }
    });
    
    // Enhanced clock for kiosk
    initializeKioskClock();
  }
}

function initializeKioskClock() {
  const clockElements = document.querySelectorAll('.kiosk-time-display, .time-display-large');
  
  function updateClock() {
    const now = new Date();
    const bangkokTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Bangkok"}));
    
    const hours = String(bangkokTime.getHours()).padStart(2, '0');
    const minutes = String(bangkokTime.getMinutes()).padStart(2, '0');
    const seconds = String(bangkokTime.getSeconds()).padStart(2, '0');
    
    clockElements.forEach(element => {
      element.innerHTML = `${hours}<span class="time-separator">:</span>${minutes}<span class="time-separator">:</span>${seconds}`;
    });
  }
  
  updateClock();
  setInterval(updateClock, 1000);
}

/**
 * Performance Optimizations
 */
function initializePerformanceOptimizations() {
  // Lazy loading images
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
    }, {
      rootMargin: '50px 0px'
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
      imageObserver.observe(img);
    });
  }
  
  // Debounced resize handler
  let resizeTimeout;
  window.addEventListener('resize', () => {
    if (resizeTimeout) clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      handleResize();
    }, 250);
  });
  
  // Prefetch important pages
  prefetchImportantPages();
}

function handleResize() {
  // Update responsive elements
  const width = window.innerWidth;
  document.body.dataset.screenSize = 
    width < DesignSystem.breakpoints.sm ? 'xs' :
    width < DesignSystem.breakpoints.md ? 'sm' :
    width < DesignSystem.breakpoints.lg ? 'md' :
    width < DesignSystem.breakpoints.xl ? 'lg' : 'xl';
}

function prefetchImportantPages() {
  const importantUrls = ['/week', '/month', '/admin'];
  
  importantUrls.forEach(url => {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    document.head.appendChild(link);
  });
}

/**
 * Utility Functions
 */
function announceToScreenReader(message, priority = 'polite') {
  const regionId = priority === 'assertive' ? 'aria-alerts' : 'aria-status';
  const region = document.getElementById(regionId);
  
  if (region) {
    region.textContent = message;
    setTimeout(() => {
      region.textContent = '';
    }, 1000);
  }
}

function closeAllMenus() {
  document.querySelectorAll('.menu.active, .dropdown.active').forEach(menu => {
    menu.classList.remove('active');
  });
}

// Export for global use
window.DesignSystem = {
  showNotification,
  openModal,
  closeModal,
  applyTheme,
  announceToScreenReader
};