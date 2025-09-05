/* ================================================
   MEDICAL SERVICE ICONS - SVG SYSTEM
   Version: 1.0 - Design Modernization Agent
   Purpose: Custom SVG icons for medical services
   ================================================ */

const MedicalIcons = {
  // Blood Test / Blutabnahme - Blood drop with test tube
  bloodTest: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C10.9 2 10 2.9 10 4C10 5.1 10.9 6 12 6C13.1 6 14 5.1 14 4C14 2.9 13.1 2 12 2Z"/>
      <path d="M12 8C8.13 8 5 11.13 5 15C5 18.87 8.13 22 12 22C15.87 22 19 18.87 19 15C19 11.13 15.87 8 12 8ZM12 20C9.24 20 7 17.76 7 15C7 12.24 9.24 10 12 10C14.76 10 17 12.24 17 15C17 17.76 14.76 20 12 20Z"/>
      <circle cx="12" cy="15" r="2"/>
      <path d="M11 6H13V8H11Z"/>
    </svg>
  `,

  // Medical Consultation / Ärztliche Beratung - Stethoscope
  consultation: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M15.5 2C17.4 2 19 3.6 19 5.5C19 7.4 17.4 9 15.5 9C13.6 9 12 7.4 12 5.5C12 3.6 13.6 2 15.5 2ZM15.5 4C14.7 4 14 4.7 14 5.5C14 6.3 14.7 7 15.5 7C16.3 7 17 6.3 17 5.5C17 4.7 16.3 4 15.5 4Z"/>
      <path d="M8.5 2C10.4 2 12 3.6 12 5.5C12 7.4 10.4 9 8.5 9C6.6 9 5 7.4 5 5.5C5 3.6 6.6 2 8.5 2ZM8.5 4C7.7 4 7 4.7 7 5.5C7 6.3 7.7 7 8.5 7C9.3 7 10 6.3 10 5.5C10 4.7 9.3 4 8.5 4Z"/>
      <path d="M12 9V12C12 16.97 7.97 21 3 21H2V19H3C6.86 19 10 15.86 10 12V11C10.6 10.4 11.3 10 12 10C12.7 10 13.4 10.4 14 11V12C14 15.86 17.14 19 21 19H22V21H21C16.03 21 12 16.97 12 12V9Z"/>
      <circle cx="19" cy="16" r="2"/>
    </svg>
  `,

  // Vaccination / Impfung - Syringe
  vaccination: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M3.5 8L8 3.5L9.5 5L5.83 8.67L7.24 10.08L10.91 6.41L12.33 7.83L8.66 11.5L10.08 12.91L13.75 9.24L15.17 10.66L11.5 14.33L12.91 15.75L16.58 12.08L18 13.5L13.5 18L12 16.5V18.5H4V10.5L3.5 8Z"/>
      <path d="M20.5 2.5L19 4L15.5 0.5L17 -1L20.5 2.5Z"/>
      <rect x="14" y="4" width="2" height="8" rx="1" transform="rotate(45 15 8)"/>
    </svg>
  `,

  // Follow-up / Nachgespräch - Chat bubbles with medical cross
  followup: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M20 2H4C2.9 2 2 2.9 2 4V16C2 17.1 2.9 18 4 18H6L10 22L14 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H13.17L10 19.17L6.83 16H4V4H20V16Z"/>
      <path d="M11 6H13V10H17V12H13V16H11V12H7V10H11V6Z"/>
    </svg>
  `,

  // Results Pickup / Ergebnisse abholen - Clipboard with checkmark
  resultsPickup: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M19 3H14.82C14.4 1.84 13.3 1 12 1S9.6 1.84 9.18 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM12 3C12.55 3 13 3.45 13 4S12.55 5 12 5 11 4.55 11 4 11.45 3 12 3ZM19 19H5V5H7V7H17V5H19V19Z"/>
      <path d="M10 17L6 13L7.41 11.59L10 14.17L16.59 7.58L18 9L10 17Z"/>
    </svg>
  `,

  // Laboratory / Labor - Microscope
  laboratory: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M13 4H11V2H13V4ZM17 3V5H15V8L19 12V18H5V12L9 8V5H7V3H17ZM15 10.5L13.5 9V5H10.5V9L9 10.5V11.5L10.5 13H13.5L15 11.5V10.5ZM7 20V22H17V20H7Z"/>
      <circle cx="12" cy="10" r="1.5"/>
    </svg>
  `,

  // Health Checkup / Vorsorge - Heart with pulse
  checkup: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 21.35L10.55 20.03C5.4 15.36 2 12.27 2 8.5C2 5.41 4.42 3 7.5 3C9.24 3 10.91 3.81 12 5.08C13.09 3.81 14.76 3 16.5 3C19.58 3 22 5.41 22 8.5C22 12.27 18.6 15.36 13.45 20.03L12 21.35Z"/>
      <path d="M7 11H9L10.5 8.5L13.5 15.5L15 13H17V15H14L13.5 15.5L10.5 8.5L9 11H7V11Z" fill="white"/>
    </svg>
  `,

  // Medication / Medikation - Pills
  medication: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M17 15C15.34 15 14 16.34 14 18S15.34 21 17 21 20 19.66 20 18 18.66 15 17 15ZM17 19C16.45 19 16 18.55 16 18S16.45 17 17 17 18 17.45 18 18 17.55 19 17 19Z"/>
      <path d="M7 3C4.79 3 3 4.79 3 7V17C3 19.21 4.79 21 7 21H9V19H7C5.9 19 5 18.1 5 17V7C5 5.9 5.9 5 7 5H9V3H7Z"/>
      <rect x="8" y="6" width="4" height="12" rx="2"/>
      <path d="M15 6C16.1 6 17 6.9 17 8V12C17 13.1 16.1 14 15 14H13V12H15V8H13V6H15Z"/>
    </svg>
  `
};

// Function to get icon HTML
function getMedicalIcon(iconName, className = '') {
  const icon = MedicalIcons[iconName];
  if (!icon) {
    console.warn(`Medical icon "${iconName}" not found`);
    return '<i class="fas fa-question-circle"></i>'; // Fallback
  }
  
  return `<div class="medical-icon ${className}">${icon}</div>`;
}

// Function to get icon by service type
function getServiceIcon(serviceType, className = '') {
  const serviceMap = {
    'Blutabnahme': 'bloodTest',
    'Blood Test': 'bloodTest',
    'เจาะเลือด': 'bloodTest',
    
    'Vorgespräch': 'consultation',
    'Ärztliche Beratung': 'consultation',
    'Medical Consultation': 'consultation',
    'ปรึกษาแพทย์': 'consultation',
    
    'Impfung': 'vaccination',
    'Vaccination': 'vaccination',
    'วัคซีน': 'vaccination',
    
    'Nachgespräch': 'followup',
    'Follow-up': 'followup',
    'ติดตาม': 'followup',
    
    'Ergebnisse abholen': 'resultsPickup',
    'Result Pickup': 'resultsPickup',
    'รับผลตรวจ': 'resultsPickup'
  };
  
  const iconName = serviceMap[serviceType] || 'laboratory';
  return getMedicalIcon(iconName, className);
}

// Initialize icons when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Replace service icons in the services section
  const serviceItems = document.querySelectorAll('.service-item, [data-service-type]');
  
  serviceItems.forEach(item => {
    const serviceType = item.dataset.serviceType || 
                       item.querySelector('.service-title, .font-medium')?.textContent?.trim();
    
    if (serviceType) {
      const iconContainer = item.querySelector('.service-icon-container, .bg-thai-turquoise');
      
      if (iconContainer) {
        // Get appropriate service icon class
        let serviceClass = 'service-icon-consultation'; // default
        
        if (serviceType.includes('Blutabnahme') || serviceType.includes('Blood') || serviceType.includes('เจาะเลือด')) {
          serviceClass = 'service-icon-blood';
        } else if (serviceType.includes('Impfung') || serviceType.includes('Vaccination') || serviceType.includes('วัคซีน')) {
          serviceClass = 'service-icon-vaccination';
        } else if (serviceType.includes('Nachgespräch') || serviceType.includes('Follow') || serviceType.includes('ติดตาม')) {
          serviceClass = 'service-icon-followup';
        } else if (serviceType.includes('Ergebnisse') || serviceType.includes('Result') || serviceType.includes('รับผล')) {
          serviceClass = 'service-icon-results';
        }
        
        // Replace Font Awesome icon with custom SVG
        const existingIcon = iconContainer.querySelector('i, .medical-icon');
        if (existingIcon) {
          existingIcon.outerHTML = getServiceIcon(serviceType, `service-icon ${serviceClass}`);
        }
      }
    }
  });
  
  // Add hover effects for service items
  const modernServiceItems = document.querySelectorAll('.service-item-modern, [data-hover-effect="modern"]');
  modernServiceItems.forEach(item => {
    item.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-4px) scale(1.02)';
    });
    
    item.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0) scale(1)';
    });
  });
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { MedicalIcons, getMedicalIcon, getServiceIcon };
}