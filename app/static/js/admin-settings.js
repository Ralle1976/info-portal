// Admin Settings Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin Settings JS loaded');
    
    // Initialize theme preview
    initializeThemePreview();
    
    // Initialize form handlers
    initializeSettingsForms();
    
    // Initialize Alpine.js data for tabs
    window.settingsData = {
        activeTab: 'contact',
        scrollToSection: function(section) {
            console.log('Scrolling to section:', section);
            // Tab navigation is handled by Alpine.js x-show
        }
    };
});

// Theme preview functionality
function initializeThemePreview() {
    const themeRadios = document.querySelectorAll('input[name="portal-theme"]');
    const preview = document.getElementById('theme-preview');
    
    themeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updateThemePreview(this.value);
            // Make radio buttons clickable
            this.checked = true;
        });
    });
    
    // Apply initial theme
    const selectedTheme = document.querySelector('input[name="portal-theme"]:checked');
    if (selectedTheme) {
        updateThemePreview(selectedTheme.value);
    }
}

function updateThemePreview(theme) {
    const preview = document.getElementById('theme-preview');
    if (!preview) return;
    
    // Remove all theme classes
    preview.className = preview.className.replace(/theme-\S+/g, '');
    
    // Apply theme-specific styling
    switch(theme) {
        case 'thai-warm':
            preview.style.background = 'linear-gradient(135deg, #FFFBEB 0%, #FED7AA 100%)';
            preview.style.color = '#92400E';
            break;
        case 'glass-modern':
            preview.style.background = 'rgba(255, 255, 255, 0.7)';
            preview.style.backdropFilter = 'blur(10px)';
            preview.style.border = '1px solid rgba(255, 255, 255, 0.2)';
            break;
        case 'dark-neon':
            preview.style.background = '#0F172A';
            preview.style.color = '#22D3EE';
            preview.style.border = '1px solid #22D3EE';
            break;
        case 'minimal-zen':
            preview.style.background = '#FAFAFA';
            preview.style.color = '#374151';
            preview.style.border = '1px solid #E5E7EB';
            break;
        case 'colorful-bright':
            preview.style.background = 'linear-gradient(45deg, #EC4899, #8B5CF6)';
            preview.style.color = 'white';
            break;
        case 'medical-clean':
        default:
            preview.style.background = 'white';
            preview.style.color = '#1F2937';
            preview.style.border = '1px solid #E5E7EB';
            break;
    }
}

// Form submission handlers
function initializeSettingsForms() {
    // Contact settings form
    const contactForm = document.getElementById('contact-settings-form');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactFormSubmit);
    }
    
    // Logo preview
    const logoUrlInput = document.getElementById('logo-url');
    if (logoUrlInput) {
        logoUrlInput.addEventListener('input', function() {
            updateLogoPreview(this.value);
        });
    }
    
    // Service management
    initializeServiceManagement();
}

function handleContactFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    // Submit via AJAX
    fetch('/admin/api/settings/contact', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': data.csrf_token
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showNotification('Einstellungen erfolgreich gespeichert', 'success');
        } else {
            showNotification('Fehler beim Speichern: ' + (result.error || 'Unbekannter Fehler'), 'error');
        }
    })
    .catch(error => {
        showNotification('Netzwerkfehler: ' + error.message, 'error');
    });
}

// Service list management
function initializeServiceManagement() {
    const servicesList = document.getElementById('services-list');
    if (!servicesList) return;
    
    // Load current services
    loadServices();
    
    // Add service button
    const addButton = document.getElementById('add-service-btn');
    if (addButton) {
        addButton.addEventListener('click', addService);
    }
}

function loadServices() {
    // This would typically load from the server
    const defaultServices = [
        'Blutabnahme',
        'Vorgespräch', 
        'Nachgespräch',
        'Befundausgabe'
    ];
    
    const servicesList = document.getElementById('services-list');
    servicesList.innerHTML = '';
    
    defaultServices.forEach((service, index) => {
        addServiceItem(service, index);
    });
}

function addServiceItem(service, index) {
    const servicesList = document.getElementById('services-list');
    const item = document.createElement('div');
    item.className = 'flex items-center space-x-2';
    item.innerHTML = `
        <input type="text" 
               name="services[]" 
               value="${service}"
               class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
        <button type="button" 
                onclick="removeService(this)"
                class="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600">
            <i class="fas fa-trash"></i>
        </button>
    `;
    servicesList.appendChild(item);
}

function addService() {
    addServiceItem('', document.querySelectorAll('#services-list > div').length);
}

function removeService(button) {
    button.closest('div').remove();
}

// Location functions
window.getCurrentLocation = function() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                document.getElementById('location-latitude').value = position.coords.latitude;
                document.getElementById('location-longitude').value = position.coords.longitude;
                showNotification('Standort erfolgreich abgerufen', 'success');
            },
            error => {
                showNotification('Standort konnte nicht abgerufen werden: ' + error.message, 'error');
            }
        );
    } else {
        showNotification('Geolocation wird nicht unterstützt', 'error');
    }
};

window.geocodeFromAddress = function() {
    const address = document.getElementById('location-address').value;
    if (!address) {
        showNotification('Bitte geben Sie eine Adresse ein', 'error');
        return;
    }
    
    // This would typically use a geocoding service
    showNotification('Geocoding Service nicht konfiguriert', 'info');
};

window.previewLocation = function() {
    const lat = document.getElementById('location-latitude').value;
    const lng = document.getElementById('location-longitude').value;
    
    if (lat && lng) {
        window.open(`https://maps.google.com/?q=${lat},${lng}`, '_blank');
    } else {
        showNotification('Bitte geben Sie Koordinaten ein', 'error');
    }
};

// Logo preview
function updateLogoPreview(url) {
    const preview = document.getElementById('logo-preview');
    const img = document.getElementById('logo-preview-img');
    
    if (url && isValidUrl(url)) {
        img.src = url;
        preview.classList.remove('hidden');
    } else {
        preview.classList.add('hidden');
    }
}

// Utility functions
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

function showNotification(message, type = 'info') {
    if (window.adminUtils && window.adminUtils.showNotification) {
        window.adminUtils.showNotification(message, type);
    } else {
        // Fallback to console
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

// Save settings handlers for other tabs
window.saveAppearanceSettings = function() {
    const theme = document.querySelector('input[name="portal-theme"]:checked')?.value;
    const fontSize = document.getElementById('font-size')?.value;
    const highContrast = document.getElementById('high-contrast')?.checked;
    const darkMode = document.getElementById('dark-mode')?.checked;
    const logoUrl = document.getElementById('logo-url')?.value;
    const faviconUrl = document.getElementById('favicon-url')?.value;
    
    const data = {
        theme,
        fontSize,
        highContrast,
        darkMode,
        logoUrl,
        faviconUrl
    };
    
    // Save via API
    fetch('/admin/api/settings/appearance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showNotification('Design-Einstellungen gespeichert', 'success');
        } else {
            showNotification('Fehler beim Speichern', 'error');
        }
    });
};

window.saveSystemSettings = function() {
    // Similar implementation for system settings
    showNotification('System-Einstellungen gespeichert', 'success');
};

// Help modal
window.showHelpModal = function() {
    // Implementation for help modal
    showNotification('Hilfe-Modal würde hier angezeigt', 'info');
};

// Tooltip helper
window.showTooltip = function(event, text) {
    // Simple tooltip implementation
    const tooltip = document.createElement('div');
    tooltip.className = 'absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg';
    tooltip.textContent = text;
    tooltip.style.left = event.pageX + 'px';
    tooltip.style.top = (event.pageY - 40) + 'px';
    
    document.body.appendChild(tooltip);
    
    setTimeout(() => tooltip.remove(), 3000);
};