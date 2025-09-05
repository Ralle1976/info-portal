# 🎨 QR Info Portal - Visual Guides & Workflows

**Visual step-by-step guides for common tasks and user journeys**

---

## 📱 User Journey: QR Code to Information

```
┌─────────────────────────────────────────────────────────────────────┐
│                      👤 VISITOR JOURNEY FLOWCHART                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   🚪 Arrives at Practice                                            │
│          │                                                          │
│          ▼                                                          │
│   📱 Sees QR Code on Door                                           │
│          │                                                          │
│          ▼                                                          │
│   📷 Scans with Phone Camera                                        │
│          │                                                          │
│     ┌────▼────┐                                                     │
│     │ Success? │                                                     │
│     └─────────┘                                                     │
│          │                                                          │
│    ┌─────▼─────┐                                                    │
│   YES          NO                                                   │
│    │            │                                                   │
│    ▼            ▼                                                   │
│🌐 Portal Opens  ⌨️ Types URL Manually                               │
│    │            │                                                   │
│    └─────┬──────┘                                                   │
│          ▼                                                          │
│   🏠 Sees Homepage                                                  │
│          │                                                          │
│          ▼                                                          │
│   👀 Views Status Banner ──► 🔴 Closed? ──► 📞 See Contact Info    │
│          │                                                          │
│          ▼                                                          │
│   ✅ Open? ──► 📅 Check Today's Hours ──► ⏰ Plan Visit             │
│          │                                                          │
│          ▼                                                          │
│   🌐 Switch Language? ──► 🇩🇪🇹🇭🇬🇧 Choose Flag                  │
│          │                                                          │
│          ▼                                                          │
│   📋 Get Needed Information                                         │
│          │                                                          │
│          ▼                                                          │
│   🚶 Proceeds with Visit or Leaves                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 👩‍⚕️ Admin Journey: Status Update

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🔑 ADMIN STATUS UPDATE WORKFLOW                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   💻 Opens Browser                                                  │
│          │                                                          │
│          ▼                                                          │
│   🌐 Goes to /admin                                                 │
│          │                                                          │
│          ▼                                                          │
│   🔑 Login Screen Appears                                           │
│          │                                                          │
│          ▼                                                          │
│   ⌨️ Enters Username: admin                                         │
│          │                                                          │
│          ▼                                                          │
│   🔐 Enters Password                                                │
│          │                                                          │
│     ┌────▼────┐                                                     │
│     │ Valid?   │                                                     │
│     └─────────┘                                                     │
│          │                                                          │
│    ┌─────▼─────┐                                                    │
│   YES          NO                                                   │
│    │            │                                                   │
│    ▼            ▼                                                   │
│📊 Dashboard    🚫 Error Message                                     │
│    │            │                                                   │
│    ▼            └──► 🔄 Try Again                                   │
│📋 Sees Current Status                                               │
│    │                                                               │
│    ▼                                                               │
│🔧 Needs Update? ──► YES ──► 📝 Click "Status bearbeiten"           │
│    │                        │                                      │
│    NO                       ▼                                      │
│    │               ☑️ Select New Status Type                       │
│    │                        │                                      │
│    │                        ▼                                      │
│    │               📅 Set Date Range (if applicable)               │
│    │                        │                                      │
│    │                        ▼                                      │
│    │               📝 Add Note/Description                         │
│    │                        │                                      │
│    │                        ▼                                      │
│    │               👀 Preview Changes                              │
│    │                        │                                      │
│    │                        ▼                                      │
│    │               💾 Click "Speichern"                            │
│    │                        │                                      │
│    │                        ▼                                      │
│    │               ✅ Success Message                              │
│    │                        │                                      │
│    └────────────────────────▼                                      │
│                    🌐 Check Public Site                            │
│                             │                                      │
│                             ▼                                      │
│                    ✅ Verify Changes Visible                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🕐 Opening Hours Management Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                 ⏰ OPENING HOURS MANAGEMENT FLOW                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   🔑 Admin Logged In                                               │
│          │                                                          │
│          ▼                                                          │
│   🏠 Navigate to "Öffnungszeiten"                                  │
│          │                                                          │
│          ▼                                                          │
│   📅 See Weekly Schedule                                           │
│          │                                                          │
│     ┌────▼────┐                                                     │
│     │ Change  │                                                     │
│     │ Type?   │                                                     │
│     └─────────┘                                                     │
│          │                                                          │
│    ┌─────▼─────┐                                                    │
│  REGULAR     EXCEPTION                                              │
│    │            │                                                   │
│    ▼            ▼                                                   │
│📝 Edit Day    📅 Add Exception                                     │
│    │            │                                                   │
│    ▼            ▼                                                   │
│⌨️ Enter Times  📅 Select Date                                      │
│Format:          │                                                   │
│08:30-12:00      ▼                                                   │
│13:00-16:00     ☑️ Closed or                                         │
│    │           ⌨️ Different Hours                                   │
│    ▼            │                                                   │
│✅ Validate      ▼                                                   │
│Format           💬 Add Note                                         │
│    │            │                                                   │
│    └─────┬──────┘                                                   │
│          ▼                                                          │
│   👀 Preview Changes                                               │
│          │                                                          │
│          ▼                                                          │
│   💾 Save Changes                                                  │
│          │                                                          │
│          ▼                                                          │
│   ✅ Confirmation Message                                          │
│          │                                                          │
│          ▼                                                          │
│   🌐 Check Public Display                                         │
│          │                                                          │
│          ▼                                                          │
│   ✅ Verify Accuracy                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🖼️ QR Code Generation Process

```
┌─────────────────────────────────────────────────────────────────────┐
│                    📱 QR CODE GENERATION WORKFLOW                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   📋 Need QR Code                                                  │
│          │                                                          │
│     ┌────▼────┐                                                     │
│     │ Format  │                                                     │
│     │ Needed? │                                                     │
│     └─────────┘                                                     │
│          │                                                          │
│    ┌─────▼─────┐                                                    │
│   PNG          SVG                                                  │
│  (Print)      (Digital)                                             │
│    │            │                                                   │
│    ▼            ▼                                                   │
│🌐 /qr?size=     🌐 /qr.svg                                         │
│   large          │                                                  │
│    │             │                                                  │
│    ▼             ▼                                                  │
│📥 Download       📥 Download                                        │
│High-res PNG      Scalable SVG                                      │
│    │             │                                                  │
│    ▼             ▼                                                  │
│🖨️ Print Setup   💻 Digital Use                                      │
│• 300+ DPI       • Websites                                         │
│• 2x2 cm min     • Presentations                                    │
│• White bg       • Scalable                                         │
│    │             │                                                  │
│    ▼             ▼                                                  │
│📄 Print &       💾 Save for                                        │
│   Laminate         Later Use                                       │
│    │             │                                                  │
│    └─────┬───────┘                                                  │
│          ▼                                                          │
│   📱 Test Scanning                                                 │
│          │                                                          │
│     ┌────▼────┐                                                     │
│     │ Works?  │                                                     │
│     └─────────┘                                                     │
│          │                                                          │
│    ┌─────▼─────┐                                                    │
│   YES          NO                                                   │
│    │            │                                                   │
│    ▼            ▼                                                   │
│✅ Deploy       🔧 Troubleshoot:                                     │
│                 • Check URL                                        │
│                 • Increase size                                    │
│                 • Better contrast                                  │
│                 • Re-generate                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting Decision Tree

```
┌─────────────────────────────────────────────────────────────────────┐
│                   🚨 TROUBLESHOOTING DECISION TREE                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ❓ Problem Reported                                              │
│          │                                                          │
│     ┌────▼────┐                                                     │
│     │ Problem │                                                     │
│     │ Type?   │                                                     │
│     └─────────┘                                                     │
│          │                                                          │
│  ┌───────┼───────┐                                                  │
│  │       │       │                                                  │
│  ▼       ▼       ▼                                                  │
│🌐 Web   📱 QR   👩‍⚕️ Admin                                           │
│Issue    Issue    Issue                                              │
│  │       │       │                                                  │
│  ▼       ▼       ▼                                                  │
│Can't    Won't    Can't                                              │
│Access   Scan     Login                                              │
│  │       │       │                                                  │
│  ▼       ▼       ▼                                                  │
│🔄 Try   📱 Check 🔑 Check                                           │
│Hard     Camera   Password                                           │
│Refresh    │       │                                                 │
│  │       ▼       ▼                                                  │
│  ▼     🧹 Clean 📝 Reset                                            │
│Different Lens    in .env                                           │
│Browser    │       │                                                 │
│  │       ▼       ▼                                                  │
│  ▼     📏 Check 🔄 Restart                                          │
│Incognito Distance Server                                            │
│Mode       │       │                                                 │
│  │       ▼       ▼                                                  │
│  ▼     💡 Better ✅ Test                                            │
│📞 Call  Lighting Login                                              │
│Support    │       │                                                 │
│          ▼       ▼                                                  │
│        ⌨️ Manual ✅ Success                                          │
│        URL Entry                                                   │
│          │                                                          │
│          ▼                                                          │
│        ✅ Success                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 UI Element Location Guide

```
┌─────────────────────────────────────────────────────────────────────┐
│                      🖥️ UI ELEMENT LOCATIONS                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ PUBLIC HOMEPAGE LAYOUT:                                             │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │                        🏥 HEADER                                │ │
│ │  Logo/Title                         🇩🇪 🇹🇭 🇬🇧 Languages    │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │                     🔴 STATUS BANNER                           │ │
│ │              "Closed - Holiday until 12.09"                   │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │          📅 TODAY'S INFO          ⏰ CURRENT TIME             │ │
│ │       "Heute: 09:00-17:00"         "14:23 Bangkok"           │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │                    📊 VIEW TOGGLE                              │ │
│ │              [Woche] [Monat] [Vorschau]                       │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │                     📋 SCHEDULE VIEW                           │ │
│ │     Mo  Di  Mi  Do  Fr  Sa  So (Week view)                   │ │
│ │  OR Calendar grid (Month view)                               │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │                     📢 ANNOUNCEMENTS                          │ │
│ │    "Fortbildung 2.-12.09. - Wir sind nicht vor Ort"         │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │                     📞 CONTACT & MAP                          │ │
│ │  Phone: +66 38 123 456  |  📍 Map Link                      │ │
│ │  Email: info@practice.com | 🗺️ Directions                    │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ ADMIN DASHBOARD LAYOUT:                                             │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │           🔑 ADMIN HEADER                      👤 Logout       │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │  📊 Dashboard  📅 Hours  📢 Status  ⚙️ Settings              │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │ 📈 STATUS CARD    📅 TODAY CARD    📊 STATS CARD             │ │
│ │ Current: Open     Hours: 9-17      Views: 234                │ │
│ │ [Edit Status]     [Edit Hours]     [View Details]            │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │                      📝 QUICK ACTIONS                          │ │
│ │  [Update Status]  [Add Exception]  [Generate QR]             │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │                      📋 RECENT CHANGES                         │ │
│ │  14:23 - Status changed to "Open"                            │ │
│ │  13:45 - Hours updated for Thursday                          │ │
│ │  12:30 - New announcement added                              │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ KIOSK TRIPLE LAYOUT:                                               │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │    📅 HEUTE      │    📊 WOCHE     │   🔮 VORSCHAU           │ │
│ │                  │                  │                         │ │
│ │  🕘 14:23       │  Mo █████████    │  Nächste Woche:       │ │
│ │                  │  Di █████████    │                         │ │
│ │  Status: OFFEN   │  Mi ████░░░░░    │  Mo-Fr: Normal         │ │
│ │                  │  Do █████████    │  Do: Fortbildung       │ │
│ │  Öffnungszeiten: │  Fr ████████░    │                         │ │
│ │  09:00 - 17:00   │  Sa ░░░░░░░░░    │  📅 Änderungen:       │ │
│ │                  │  So ░░░░░░░░░    │  12.09 - zurück        │ │
│ │                  │                  │                         │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ │                        📱 QR CODE                              │ │
│ │                       ████████████                             │ │
│ │                       ████████████                             │ │
│ │                   Scan for full info                          │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 System Integration Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                   🏗️ SYSTEM ARCHITECTURE DIAGRAM                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 📱 USER DEVICES                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 📱 Mobile Phones    💻 Computers    🖥️ Kiosk Displays          │ │
│ │      │                   │              │                      │ │
│ └──────┼───────────────────┼──────────────┼──────────────────────┘ │
│        │                   │              │                        │
│        ▼                   ▼              ▼                        │
│ 🌐 INTERNET / LOCAL NETWORK                                        │
│        │                   │              │                        │
│        ▼                   ▼              ▼                        │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │                    🔄 LOAD BALANCER                             │ │
│ │                     (Optional)                                 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                │                                    │
│                                ▼                                    │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │                      🐍 FLASK APPLICATION                       │ │
│ │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │ │
│ │  │ Routes  │  │Templates│  │Services │  │  APIs   │           │ │
│ │  │/        │  │  HTML   │  │Business │  │/api/    │           │ │
│ │  │/admin   │  │ Jinja2  │  │ Logic   │  │/qr      │           │ │
│ │  │/kiosk   │  │  i18n   │  │Schedule │  │/healthz │           │ │
│ │  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                │                                    │
│                                ▼                                    │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │                      💾 DATA LAYER                              │ │
│ │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │ │
│ │  │SQLite   │  │Config   │  │Static   │  │  Logs   │           │ │
│ │  │Database │  │YAML     │  │Files    │  │System   │           │ │
│ │  │portal.db│  │Settings │  │CSS/JS   │  │Events   │           │ │
│ │  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ 📊 EXTERNAL INTEGRATIONS                                           │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🗺️ Google Maps  📱 QR Libraries  🌐 CDN Resources             │ │
│ │ 📧 Email SMTP    📞 SMS Gateway   📈 Analytics                 │ │
│ │      (Optional)      (Optional)       (Optional)               │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Checklist Visual

```
┌─────────────────────────────────────────────────────────────────────┐
│                  ✅ IMPLEMENTATION PROGRESS TRACKER                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ PHASE 1: FOUNDATION ✅                                             │
│ ├─ ✅ Project Structure                                            │
│ ├─ ✅ Requirements & Dependencies                                   │
│ ├─ ✅ Configuration System                                         │
│ ├─ ✅ Database Models                                              │
│ └─ ✅ Basic Flask Setup                                            │
│                                                                     │
│ PHASE 2: CORE FEATURES ✅                                          │
│ ├─ ✅ Public Homepage                                              │
│ ├─ ✅ Status Management                                            │
│ ├─ ✅ Opening Hours System                                         │
│ ├─ ✅ Multi-language Support                                       │
│ └─ ✅ QR Code Generation                                           │
│                                                                     │
│ PHASE 3: ADMIN SYSTEM ✅                                           │
│ ├─ ✅ Authentication                                               │
│ ├─ ✅ Admin Dashboard                                              │
│ ├─ ✅ CRUD Operations                                              │
│ ├─ ✅ Form Validation                                              │
│ └─ ✅ Real-time Updates                                            │
│                                                                     │
│ PHASE 4: ADVANCED FEATURES ✅                                      │
│ ├─ ✅ Kiosk Mode                                                   │
│ ├─ ✅ Responsive Design                                            │
│ ├─ ✅ Auto-refresh System                                          │
│ ├─ ✅ Error Handling                                               │
│ └─ ✅ Performance Optimization                                     │
│                                                                     │
│ PHASE 5: DEPLOYMENT ✅                                             │
│ ├─ ✅ Docker Configuration                                         │
│ ├─ ✅ Production Setup                                             │
│ ├─ ✅ Security Hardening                                          │
│ ├─ ✅ Backup System                                               │
│ └─ ✅ Monitoring & Logs                                           │
│                                                                     │
│ PHASE 6: DOCUMENTATION ✅                                          │
│ ├─ ✅ User Manual                                                  │
│ ├─ ✅ Admin Guide                                                  │
│ ├─ ✅ API Documentation                                            │
│ ├─ ✅ Installation Guide                                           │
│ ├─ ✅ Troubleshooting                                              │
│ ├─ ✅ Help System                                                  │
│ └─ ✅ Quick References                                             │
│                                                                     │
│ 🎯 PROJECT STATUS: COMPLETE ✅                                     │
│ 📊 PROGRESS: 100% (42/42 tasks)                                   │
│ 📅 COMPLETION DATE: 2025-08-23                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Brand & Design Guidelines

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🎨 VISUAL DESIGN GUIDELINES                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 🎨 COLOR PALETTE:                                                  │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Primary:   #0891b2 (Cyan 600)     ████████████                │ │
│ │ Secondary: #06b6d4 (Cyan 500)     ████████████                │ │
│ │ Success:   #059669 (Emerald 600)  ████████████                │ │
│ │ Warning:   #d97706 (Amber 600)    ████████████                │ │
│ │ Error:     #dc2626 (Red 600)      ████████████                │ │
│ │ Neutral:   #374151 (Gray 700)     ████████████                │ │
│ │ Light:     #f9fafb (Gray 50)      ████████████                │ │
│ │ Dark:      #111827 (Gray 900)     ████████████                │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ 📝 TYPOGRAPHY:                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Primary Font: Sarabun (Google Fonts)                           │ │
│ │ - Thai and Latin script support                                │ │
│ │ - Weights: 300 (Light), 400 (Regular), 600 (SemiBold)         │ │
│ │ - Clean, medical-appropriate appearance                        │ │
│ │                                                                 │ │
│ │ Fallback: -apple-system, BlinkMacSystemFont, sans-serif       │ │
│ │                                                                 │ │
│ │ Usage:                                                         │ │
│ │ • Headers: Sarabun 600 (SemiBold)                             │ │
│ │ • Body: Sarabun 400 (Regular)                                 │ │
│ │ • Small text: Sarabun 300 (Light)                             │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ 📐 SPACING & LAYOUT:                                               │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ • Tailwind spacing scale (4px base unit)                       │ │
│ │ • Container max-width: 1200px                                  │ │
│ │ • Mobile breakpoints: 640px, 768px, 1024px, 1280px            │ │
│ │ • Card border-radius: 8px (rounded-lg)                        │ │
│ │ • Button padding: py-2 px-4 (8px/16px)                        │ │
│ │ • Section spacing: py-8 (32px vertical)                       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ 🎯 UI COMPONENTS:                                                  │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Status Banner:                                                  │ │
│ │ • Full width, prominent placement                               │ │
│ │ • Color-coded by status (green=open, red=closed, etc.)        │ │
│ │ • Icon + text + optional countdown                             │ │
│ │                                                                 │ │
│ │ Cards:                                                         │ │
│ │ • White background, subtle shadow                              │ │
│ │ • 8px border radius, 16px padding                              │ │
│ │ • Hover effects on interactive elements                       │ │
│ │                                                                 │ │
│ │ Buttons:                                                       │ │
│ │ • Primary: Cyan background, white text                        │ │
│ │ • Secondary: Gray outline, dark text                          │ │
│ │ • Danger: Red background, white text                          │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ 📱 RESPONSIVE BEHAVIOR:                                            │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Mobile First Design:                                           │ │
│ │ • Stack elements vertically on small screens                   │ │
│ │ • Increase touch target sizes (min 44px)                      │ │
│ │ • Simplify navigation for mobile                               │ │
│ │                                                                 │ │
│ │ Desktop Enhancement:                                           │ │
│ │ • Multi-column layouts                                         │ │
│ │ • Hover states and interactions                                │ │
│ │ • Larger typography and spacing                                │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📞 Support Contact Visual

```
┌─────────────────────────────────────────────────────────────────────┐
│                        📞 SUPPORT ESCALATION                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ LEVEL 1: SELF-HELP (0-15 minutes)                                 │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 📖 Check documentation                                          │ │
│ │ 🔧 Try basic troubleshooting                                   │ │
│ │ 🌐 Search FAQ and guides                                       │ │
│ │ 🔄 Restart browser/device                                      │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                ▼                                    │
│ LEVEL 2: COMMUNITY (30 minutes)                                   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 💬 GitHub Issues                                               │ │
│ │ 📧 Community Forums                                            │ │
│ │ 📋 Online Knowledge Base                                       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                ▼                                    │
│ LEVEL 3: TECHNICAL SUPPORT (Business Hours)                       │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 📧 tech@pattaya-medical.com                                    │ │
│ │ 📞 +66 38 123 456 (Mon-Fri 9 AM - 5 PM)                      │ │
│ │ ⏱️ Response: Within 24 hours                                   │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                ▼                                    │
│ LEVEL 4: EMERGENCY (24/7)                                         │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🚨 +66 38 123 999 (Emergency Hotline)                         │ │
│ │ 💬 WhatsApp: +66 38 123 456                                    │ │
│ │ ⏱️ Response: Within 2 hours                                    │ │
│ │ 🔴 Use only for critical system failures                       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ 📋 INFORMATION TO PROVIDE:                                         │
│ • System version and browser                                       │
│ • Error messages (screenshots)                                     │
│ • Steps to reproduce issue                                         │
│ • Recent changes made                                              │
│ • Log files if available                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

**📝 USAGE INSTRUCTIONS:**

1. **Print These Guides**: Use A4/Letter paper, consider laminating for durability
2. **Post Strategically**: Place relevant guides near workstations and public areas
3. **Update Regularly**: Review and update when system changes are made
4. **Train Staff**: Ensure all team members understand the workflows
5. **Keep Digital Copies**: Store PDF versions for easy sharing

**🔄 MAINTENANCE:**
- Review quarterly for accuracy
- Update contact information immediately when changed
- Version control all printed materials with dates
- Gather user feedback to improve visual clarity