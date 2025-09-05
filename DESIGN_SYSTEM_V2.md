# QR-INFO-PORTAL: THAI-FIRST DESIGN SYSTEM V2.0

## 🎯 Design Philosophy
**Thai-First Medical Portal** - Ein Design System, das thai kulturelle Elemente mit moderner Medizinästhetik verbindet.

---

## 🎨 CONSOLIDATED COLOR PALETTE

### Primary Colors - Thai Medical Turquoise
```css
--thai-turquoise-50:  #E0FFFE
--thai-turquoise-100: #B0FDFC
--thai-turquoise-200: #80F9FA
--thai-turquoise-300: #50F5F7
--thai-turquoise-400: #20F1F5
--thai-turquoise-500: #14B8A6  /* MAIN BRAND COLOR */
--thai-turquoise-600: #0F9488
--thai-turquoise-700: #0D7377
--thai-turquoise-800: #0A5D61
--thai-turquoise-900: #084748
```

### Secondary Colors - Thai Medical Coral
```css
--thai-coral-50:  #FFF5F1
--thai-coral-100: #FFE6DD
--thai-coral-200: #FFD7C9
--thai-coral-300: #FFC8B5
--thai-coral-400: #FFB9A1
--thai-coral-500: #FF6B6B  /* MAIN ACCENT COLOR */
--thai-coral-600: #E55555
--thai-coral-700: #CC4444
--thai-coral-800: #B23333
--thai-coral-900: #992222
```

### Medical Status Colors - Clear Communication
```css
--medical-open:    #059669  /* Vertrauensvolle Grün */
--medical-closed:  #DC2626  /* Klares Warnsignal Rot */
--medical-warning: #D97706  /* Aufmerksamkeits Orange */
--medical-info:    #2563EB  /* Informatives Blau */
```

### Thai Cultural Accents
```css
--thai-gold:       #FFD700  /* Traditionelles Thai-Gold */
--thai-red:        #DC143C  /* Thai-Tempel Rot */
--thai-green:      #228B22  /* Thai-Natur Grün */
```

---

## 📝 TYPOGRAPHY SYSTEM - SARABUN OPTIMIZED

### Font Stack (Thai-First)
```css
--font-primary: 'Sarabun', 'Noto Sans Thai', 'Inter', system-ui, sans-serif;
--font-display: 'Sarabun', sans-serif;
--font-mono: 'SF Mono', 'Cascadia Code', 'Roboto Mono', monospace;
```

### Type Scale - Thai Language Optimized
```css
--text-xs:   0.75rem   /* 12px - Captions, Meta */
--text-sm:   0.875rem  /* 14px - Body Small, Labels */  
--text-base: 1rem      /* 16px - Body Text (Thai optimiert) */
--text-lg:   1.125rem  /* 18px - Body Large (Thai lesbar) */
--text-xl:   1.25rem   /* 20px - Small Headers */
--text-2xl:  1.5rem    /* 24px - Section Headers */
--text-3xl:  1.875rem  /* 30px - Page Headers */
--text-4xl:  2.25rem   /* 36px - Display Headers */
--text-5xl:  3rem      /* 48px - Hero Text */
```

### Thai Language Adjustments
```css
:lang(th) {
  line-height: 1.75;        /* Erhöht für Thai Schrift */
  letter-spacing: 0.025em;  /* Verbesserte Lesbarkeit */
}
```

---

## 📐 SPACING SYSTEM - THAI-FRIENDLY

### 8pt Grid System
```css
--space-0:  0
--space-1:  0.25rem  /* 4px */
--space-2:  0.5rem   /* 8px */
--space-3:  0.75rem  /* 12px */
--space-4:  1rem     /* 16px - Base Unit */
--space-6:  1.5rem   /* 24px - 1.5x */
--space-8:  2rem     /* 32px - 2x */
--space-10: 2.5rem   /* 40px - 2.5x */
--space-12: 3rem     /* 48px - 3x */
--space-16: 4rem     /* 64px - 4x */
--space-20: 5rem     /* 80px - 5x */
--space-24: 6rem     /* 96px - 6x */
```

### Mobile-First Breakpoints
```css
--breakpoint-sm: 640px    /* Mobile Landscape */
--breakpoint-md: 768px    /* Tablet Portrait */
--breakpoint-lg: 1024px   /* Desktop Small */
--breakpoint-xl: 1280px   /* Desktop Large */
--breakpoint-2xl: 1536px  /* Desktop XL */
```

---

## 🧩 COMPONENT LIBRARY

### 1. BUTTON SYSTEM - Medical Grade

#### Primary Button (Thai Turquoise)
```css
.btn-primary-thai {
  background: linear-gradient(135deg, var(--thai-turquoise-500), var(--thai-turquoise-600));
  color: white;
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-lg);
  font-weight: 600;
  border: none;
  transition: all 300ms ease;
  box-shadow: 0 4px 14px 0 rgba(20, 184, 166, 0.2);
}

.btn-primary-thai:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px 0 rgba(20, 184, 166, 0.4);
}
```

#### Medical Emergency Button
```css
.btn-emergency-thai {
  background: linear-gradient(135deg, var(--medical-closed), #B91C1C);
  color: white;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  animation: pulse-emergency 2s infinite;
}
```

### 2. CARD SYSTEM - Thai Medical

#### Base Card - Thai Style
```css
.card-thai-medical {
  background: white;
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-thai);
  border: 1px solid rgba(20, 184, 166, 0.1);
  position: relative;
  overflow: hidden;
}

.card-thai-medical::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--thai-turquoise-500), var(--thai-coral-500));
}
```

#### Status Card - Clear Medical Communication
```css
.card-status-thai {
  position: relative;
  border-left: 6px solid var(--status-color);
  background: linear-gradient(135deg, var(--status-bg), white);
}

.card-status-open {
  --status-color: var(--medical-open);
  --status-bg: rgba(5, 150, 105, 0.05);
}

.card-status-closed {
  --status-color: var(--medical-closed);
  --status-bg: rgba(220, 38, 38, 0.05);
}
```

### 3. NAVIGATION - Thai Medical

#### Main Navigation
```css
.nav-thai-medical {
  background: linear-gradient(135deg, var(--thai-turquoise-500), var(--thai-turquoise-600));
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(20, 184, 166, 0.2);
  position: sticky;
  top: 0;
  z-index: 50;
}

.nav-item-thai {
  color: white;
  padding: var(--space-4) var(--space-6);
  border-radius: var(--radius-lg);
  transition: all 300ms ease;
  position: relative;
}

.nav-item-thai::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 3px;
  background: var(--thai-coral-500);
  transition: all 300ms ease;
  transform: translateX(-50%);
}

.nav-item-thai:hover::after,
.nav-item-thai.active::after {
  width: 80%;
}
```

### 4. STATUS INDICATORS - Medical Grade

#### Live Status Indicator
```css
.status-thai-live {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  position: relative;
}

.status-thai-live::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse-thai 2s infinite;
}

@keyframes pulse-thai {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.2); }
}
```

---

## 🏥 MEDICAL-SPECIFIC COMPONENTS

### 1. Time Display - Bangkok Timezone
```css
.time-display-thai {
  font-family: var(--font-mono);
  font-size: var(--text-5xl);
  font-weight: 700;
  background: linear-gradient(135deg, var(--thai-turquoise-500), var(--thai-coral-500));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
  position: relative;
}

.time-display-thai::after {
  content: 'เวลาไทย / Bangkok Time';
  position: absolute;
  bottom: -1.5rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--gray-500);
  background: none;
  -webkit-text-fill-color: var(--gray-500);
}
```

### 2. QR Code Container - Thai Style
```css
.qr-container-thai {
  background: linear-gradient(135deg, rgba(20, 184, 166, 0.05), rgba(255, 107, 107, 0.05));
  border: 3px dashed var(--thai-turquoise-300);
  border-radius: var(--radius-2xl);
  padding: var(--space-8);
  text-align: center;
  position: relative;
}

.qr-container-thai::before {
  content: 'สแกนที่นี่ / SCAN HERE';
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 0 var(--space-4);
  color: var(--thai-turquoise-600);
  font-weight: 700;
  font-size: var(--text-sm);
  letter-spacing: 0.1em;
}
```

### 3. Service Icons - Medical Professional
```css
.service-icon-thai {
  width: var(--space-12);
  height: var(--space-12);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: var(--text-xl);
  position: relative;
  overflow: hidden;
}

.service-icon-thai::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.2), transparent);
  opacity: 0;
  transition: opacity 300ms ease;
}

.service-icon-thai:hover::before {
  opacity: 1;
}

/* Service-Specific Variants */
.service-icon-blood { 
  background: linear-gradient(135deg, #DC2626, #991B1B);
}
.service-icon-consultation { 
  background: linear-gradient(135deg, #2563EB, #1D4ED8);
}
.service-icon-vaccination { 
  background: linear-gradient(135deg, #059669, #047857);
}
```

---

## 📱 RESPONSIVE DESIGN - MOBILE-FIRST

### Mobile (320px - 640px)
```css
@media (max-width: 640px) {
  :root {
    --text-base: 0.9rem;     /* Thai Text kleiner auf Mobile */
    --space-base: 0.75rem;   /* Kompaktere Abstände */
  }
  
  .card-thai-medical {
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
  }
  
  .btn-primary-thai {
    padding: var(--space-2) var(--space-4);
    font-size: var(--text-sm);
  }
}
```

### Tablet (641px - 1024px)
```css
@media (min-width: 641px) and (max-width: 1024px) {
  .services-grid-thai {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .kiosk-card-thai {
    padding: var(--space-8);
  }
}
```

### Desktop (1025px+)
```css
@media (min-width: 1025px) {
  .services-grid-thai {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .card-thai-medical:hover {
    transform: translateY(-4px) scale(1.02);
  }
}
```

---

## ♿ ACCESSIBILITY - WCAG 2.1 AA

### Focus States
```css
*:focus-visible {
  outline: 3px solid var(--thai-turquoise-500);
  outline-offset: 2px;
  border-radius: var(--radius-md);
}

.btn-primary-thai:focus-visible {
  box-shadow: 
    0 0 0 3px var(--thai-turquoise-500),
    0 0 0 6px rgba(20, 184, 166, 0.3);
}
```

### High Contrast Mode
```css
@media (prefers-contrast: high) {
  :root {
    --thai-turquoise-500: #0F766E;
    --thai-coral-500: #DC2626;
    --shadow: 0 0 0 2px var(--gray-900);
  }
}
```

### Thai Language Support
```css
:lang(th) {
  font-family: 'Sarabun', 'Noto Sans Thai', sans-serif;
  line-height: 1.75;
  letter-spacing: 0.025em;
}

:lang(th) .text-large {
  font-size: 1.2em; /* Thai Text braucht mehr Platz */
}
```

---

## 🖼️ KIOSK MODE - LARGE DISPLAY OPTIMIZATION

### Triple Layout - Professional Medical
```css
.kiosk-triple-thai {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: var(--space-8);
  padding: var(--space-8);
  min-height: 100vh;
  background: linear-gradient(135deg, #F0FDF4, #E0F2FE);
}

.kiosk-section-thai {
  background: white;
  border-radius: var(--radius-3xl);
  padding: var(--space-10);
  box-shadow: var(--shadow-2xl);
  position: relative;
  overflow: hidden;
}

.kiosk-section-thai::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 8px;
  background: linear-gradient(90deg, 
    var(--thai-turquoise-500) 0%, 
    var(--thai-coral-500) 50%, 
    var(--medical-open) 100%);
}
```

### Kiosk Time Display
```css
.kiosk-time-thai {
  font-family: var(--font-mono);
  font-size: 8rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--thai-turquoise-500), var(--thai-coral-500));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-align: center;
  line-height: 1;
}
```

---

## 🎭 ANIMATION SYSTEM

### Thai Cultural Animations
```css
@keyframes thai-entrance {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes thai-gentle-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
```

### Performance Optimized Transitions
```css
.transition-thai {
  transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

.transition-thai-slow {
  transition: all 500ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
```

---

## 🛠️ IMPLEMENTATION STRATEGY

### Phase 1: CSS Consolidation
1. **Merge fragmented CSS files** in logical order:
   - `design-system-v2.css` (Base + Tokens)
   - `thai-medical-components.css` (Components)  
   - `kiosk-enhanced.css` (Kiosk specific)
   - `responsive-thai.css` (Responsive)

### Phase 2: Component Standardization
1. **Eliminate duplicates**: Remove .card-enhanced, .card-modern → Use .card-thai-medical
2. **Standardize naming**: All components get `-thai` suffix
3. **Consistent spacing**: Use CSS Custom Properties only

### Phase 3: Thai Optimization
1. **Font loading optimization**: Preload Sarabun weights
2. **Thai text rendering**: Optimize for Safari/WebKit
3. **Cultural elements**: Add subtle Thai pattern overlays

### Phase 4: Performance
1. **Critical CSS**: Extract above-fold styles
2. **Async loading**: Non-critical CSS via JS
3. **Purge unused**: Remove Tailwind classes covered by Design System

---

## 📋 COMPONENT SPECIFICATIONS

### Medical Card - Complete Spec
```html
<div class="card-thai-medical card-service-blood">
  <div class="card-header-thai">
    <div class="service-icon-container">
      <div class="service-icon-thai service-icon-blood">
        <svg><!-- Blood test icon --></svg>
      </div>
    </div>
    <div class="service-content-thai">
      <h3 class="service-title-thai">{{ service_name }}</h3>
      <p class="service-description-thai">{{ description }}</p>
    </div>
  </div>
</div>
```

### Status Banner - Complete Spec
```html
<div class="status-banner-thai status-{{ status_type }}">
  <div class="status-icon-thai">
    <i class="fas fa-{{ status_icon }}"></i>
  </div>
  <div class="status-content-thai">
    <h2 class="status-title-thai">{{ status_text }}</h2>
    <p class="status-description-thai">{{ status_note }}</p>
  </div>
  <div class="status-indicator-thai status-live-pulse"></div>
</div>
```

---

## 🎨 BRAND GUIDELINES

### Logo Usage
- **Primary**: Stethoscope icon in Thai Turquoise
- **Background**: White circle with subtle shadow
- **Minimum size**: 32px für Mobile, 48px für Desktop

### Color Usage Rules
- **Primary Actions**: Thai Turquoise Gradient
- **Medical Status**: Medical Green/Red (nicht Thai colors)
- **Thai Cultural**: Gold/Red nur für kulturelle Elemente
- **Never**: Mehr als 3 Farben gleichzeitig verwenden

### Typography Rules
- **Headlines**: Sarabun Bold, Thai Turquoise/Coral Gradient
- **Body Text**: Sarabun Regular, mindestens 16px
- **Thai Text**: Immer 1.75 line-height
- **Monospace**: Nur für Zeit/Datum/Codes

---

## ✅ IMPLEMENTATION CHECKLIST

### Sofort umsetzbar:
- [ ] CSS-Dateien konsolidieren (16 → 4)
- [ ] Component-Duplikate entfernen
- [ ] Sarabun font-loading optimieren
- [ ] Thai language CSS adjustments
- [ ] Color tokens vereinheitlichen

### Phase 2:
- [ ] Component Library dokumentieren  
- [ ] Accessibility testing (Thai content)
- [ ] Performance audit (mobile focus)
- [ ] Print stylesheet für QR codes
- [ ] Icon system standardisieren

### Design System Assets:
- [ ] SVG Icon set (medical + Thai cultural)
- [ ] Component templates (Jinja)
- [ ] Storybook/Documentation
- [ ] Design tokens JSON export
- [ ] Print-ready QR templates

---

## 🚀 PERFORMANCE TARGETS

### Loading Performance
- **First Contentful Paint**: < 1.5s (3G mobile)
- **CSS Bundle size**: < 50KB gzipped
- **Font loading**: < 200ms (Sarabun preload)
- **Component rendering**: < 16ms (60fps)

### Accessibility Targets  
- **WCAG 2.1 AA**: 100% compliance
- **Color contrast**: Minimum 4.5:1
- **Keyboard navigation**: Complete coverage
- **Screen reader**: Semantic markup

### Multi-device Support
- **Mobile**: 320px - 640px (perfect)
- **Tablet**: 641px - 1024px (optimized)
- **Desktop**: 1025px+ (enhanced)
- **Kiosk**: 1920px+ (specialized)

---

**ZIEL**: Ein kohärentes, performantes, zugängliches Design System das thai kulturelle Elemente mit moderner Medizinästhetik professionell verbindet.