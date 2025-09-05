# 🖨️ QR Info Portal - Printable Reference Sheets

**Ready-to-print reference materials for staff and visitors**

---

## 📄 Quick Start Card (A5 Format)

```
┌─────────────────────────────────────────────────────────────────────┐
│                      🏥 QR INFO PORTAL                              │
│                     QUICK START GUIDE                               │
│                                                                     │
│ FOR VISITORS:                                                       │
│ 1. 📱 Scan QR code with phone camera                               │
│ 2. 👆 Tap the notification that appears                            │
│ 3. 🌐 Portal opens automatically in browser                        │
│ 4. 🇩🇪🇹🇭🇬🇧 Choose language (top-right flags)                    │
│ 5. 👀 Check status banner and today's hours                        │
│                                                                     │
│ FOR STAFF:                                                         │
│ 1. 💻 Go to: your-domain.com/admin                                 │
│ 2. 🔑 Login: admin / [password from .env]                          │
│ 3. 📊 Update status, hours, or announcements                       │
│ 4. 💾 Save changes                                                 │
│ 5. ✅ Changes appear immediately on public site                     │
│                                                                     │
│ EMERGENCY CONTACTS:                                                 │
│ 🚨 Emergency: +66 38 123 999 (24/7)                               │
│ 🔧 Tech Support: +66 38 123 456 (Business hours)                  │
│ 📧 Email: tech@pattaya-medical.com                                 │
│                                                                     │
│ COMMON FIXES:                                                       │
│ • QR won't scan → Clean camera lens, better lighting               │
│ • Site won't load → Hard refresh (Ctrl+F5), try incognito         │
│ • Admin can't login → Check password in .env file                  │
│ • Changes not saving → Check browser console (F12) for errors      │
│                                                                     │
│ 📋 Version 1.0 | Updated: 2025-08-23                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Admin Cheat Sheet (A4 Landscape)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                          🔑 ADMIN DASHBOARD CHEAT SHEET                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                             │
│ LOGIN & ACCESS:                                                                                             │
│ • URL: your-domain.com/admin                                                                                │
│ • Username: admin                                                                                           │
│ • Password: Check .env file (ADMIN_PASSWORD=...)                                                           │
│ • Reset password: Edit .env → ADMIN_PASSWORD=newpass → Restart server                                      │
│                                                                                                             │
│ STATUS MANAGEMENT:              │ OPENING HOURS:                    │ QUICK ACTIONS:                      │
│ • ANWESEND = Present/Open       │ • Format: 08:30-12:00,13:00-16:00 │ • Generate QR: /qr?size=large      │
│ • URLAUB = Vacation/Holiday     │ • Multiple periods: Use commas    │ • View public site: / (new tab)    │
│ • BILDUNGSURLAUB = Training     │ • Closed days: Leave empty        │ • Quick status: Dashboard cards     │
│ • KONGRESS = Conference         │ • Exceptions override regular     │ • Backup config: Download YAML     │
│ • SONSTIGES = Other/Custom      │ • Time zone: Asia/Bangkok          │ • Check logs: Browser console F12  │
│                                 │                                    │                                     │
│ COMMON TASKS:                                                                                               │
│ 1. Change Status:        Dashboard → Status Card → Edit → Select Type → Set Dates → Add Note → Save       │
│ 2. Update Hours:         Öffnungszeiten → Select Day → Enter Times → Validate Format → Save                │
│ 3. Add Exception:        Öffnungszeiten → Ausnahmen → Add Date → Mark Closed/Different Hours → Save        │
│ 4. Create Announcement:  Hinweise → New → Title/Body → Select Languages → Set Priority → Save              │
│ 5. Generate QR Codes:    Dashboard → QR Generator → Select Size/Format → Download → Test Scan              │
│                                                                                                             │
│ TROUBLESHOOTING:                                                                                            │
│ Problem                    → Solution                                                                       │
│ Changes not appearing      → Hard refresh browser (Ctrl+F5), check form errors                            │
│ Can't login               → Verify password in .env, try incognito mode, restart server                   │
│ Database errors           → Check permissions: chmod 664 data/portal.db                                   │
│ Time wrong                → Verify timezone in config.yml: "Asia/Bangkok"                                 │
│ QR codes not generating   → Check SITE_URL in .env, verify network access                                 │
│                                                                                                             │
│ TIME FORMATS (CRITICAL):                       │ STATUS EXAMPLES:                                          │
│ ✅ CORRECT:   08:30-12:00, 13:00-16:00        │ • Emergency closure: SONSTIGES + "Notfall - heute zu"    │
│ ✅ CORRECT:   09:00-17:00                     │ • Vacation: URLAUB + start/end dates + "Urlaub bis..."   │
│ ✅ CORRECT:   14:30-18:30                     │ • Training: BILDUNGSURLAUB + dates + "Fortbildung..."    │
│ ❌ WRONG:     8:30AM-12PM, 9-17, 08.30-12.00  │ • Conference: KONGRESS + dates + "Kongress in..."        │
│                                                │ • Normal: ANWESEND (no dates needed)                     │
│                                                                                                             │
│ 📞 SUPPORT ESCALATION:                         │ 📋 DAILY CHECKLIST:                                      │
│ 1. Check this cheat sheet                     │ □ Verify public site loads correctly                     │
│ 2. Try incognito browser mode                 │ □ Check status banner is current                         │
│ 3. Look for errors in F12 console             │ □ Confirm today's hours are accurate                     │
│ 4. Email: tech@pattaya-medical.com            │ □ Test QR code scanning                                  │
│ 5. Emergency: +66 38 123 999                  │ □ Review any pending announcements                       │
│                                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📱 QR Code Poster (A3 Format)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                        🏥 LABOR PATTAYA                            │
│                     AKTUELLE INFORMATIONEN                         │
│                    CURRENT INFORMATION                              │
│                      ข้อมูลปัจจุบัน                                   │
│                                                                     │
│                                                                     │
│                     ████████████████████                           │
│                     ████████████████████                           │
│                     ████████████████████                           │
│                     ████████████████████                           │
│                     ████████████████████                           │
│                     ████████████████████                           │
│                     ████████████████████                           │
│                     ████████████████████                           │
│                     ████████████████████                           │
│                     ████████████████████                           │
│                                                                     │
│                                                                     │
│              📱 SCAN MIT HANDY-KAMERA                              │
│              📱 SCAN WITH PHONE CAMERA                             │
│              📱 สแกนด้วยกล้องโทรศัพท์                                │
│                                                                     │
│                                                                     │
│        🔗 Oder direkt: http://your-domain.com                      │
│        🔗 Or directly: http://your-domain.com                      │
│        🔗 หรือโดยตรง: http://your-domain.com                        │
│                                                                     │
│                                                                     │
│                      ℹ️ HIER ERHALTEN SIE:                         │
│                     ℹ️ HERE YOU CAN FIND:                          │
│                     ℹ️ ที่นี่คุณสามารถหา:                            │
│                                                                     │
│            • Aktuelle Öffnungszeiten / Current hours               │
│            • Status (Offen/Geschlossen) / Status (Open/Closed)     │
│            • Kontakt & Anfahrt / Contact & Directions              │
│            • Wichtige Hinweise / Important notices                 │
│            • ข้อมูลเวลาทำการ / สถานะ / ติดต่อ / ประกาศสำคัญ          │
│                                                                     │
│                                                                     │
│                    📞 NOTFALL / EMERGENCY:                          │
│                       +66 38 123 999                               │
│                                                                     │
│                                                                     │
│            🕐 24/7 VERFÜGBAR / AVAILABLE / ใช้ได้ตลอด 24 ชม.         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Kiosk Instructions Card

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🖥️ KIOSK SYSTEM SETUP CARD                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ DISPLAY SETUP:                                                      │
│                                                                     │
│ Single Display Mode:                                               │
│ • URL: your-domain.com/kiosk/single                                │
│ • Shows: Today's status, hours, current time                       │
│ • Best for: Small displays, waiting rooms                          │
│                                                                     │
│ Triple Display Mode:                                               │
│ • URL: your-domain.com/kiosk/triple                                │
│ • Shows: Today | Week view | Preview + QR code                     │
│ • Best for: Large displays, reception areas                        │
│                                                                     │
│ BROWSER SETTINGS:                                                   │
│ 1. Set homepage to kiosk URL                                       │
│ 2. Enable full-screen mode (F11)                                   │
│ 3. Disable screen saver                                            │
│ 4. Set auto-refresh to 60 seconds                                  │
│ 5. Hide bookmarks bar and tabs                                     │
│                                                                     │
│ RECOMMENDED BROWSER EXTENSIONS:                                     │
│ • Full Screen (Chrome): Auto full-screen                           │
│ • Auto Refresh Plus: Automatic page reload                         │
│ • Kiosk Mode: Disable user interactions                            │
│                                                                     │
│ HARDWARE RECOMMENDATIONS:                                           │
│ • Display size: Minimum 24" for triple mode                        │
│ • Resolution: 1920×1080 or higher                                  │
│ • Network: Stable wired connection preferred                       │
│ • Power: Uninterruptible power supply (UPS)                        │
│                                                                     │
│ MAINTENANCE SCHEDULE:                                               │
│ Daily:   Check display is on and showing current info              │
│ Weekly:  Clean screen, check network connection                     │
│ Monthly: Restart system, check for browser updates                 │
│                                                                     │
│ TROUBLESHOOTING:                                                    │
│ • Screen frozen → Press F5 to refresh                              │
│ • Wrong time → Check system timezone                               │
│ • No internet → Check network cable/WiFi                           │
│ • Blank screen → Check power, press space bar                      │
│                                                                     │
│ 🆘 EMERGENCY FALLBACK:                                             │
│ If kiosk fails completely, post printed backup sign:               │
│ "System maintenance - call +66 38 123 456 for information"         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Daily Operations Checklist

```
┌─────────────────────────────────────────────────────────────────────┐
│                   📋 DAILY OPERATIONS CHECKLIST                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Date: ________________    Staff Member: ______________________      │
│                                                                     │
│ MORNING STARTUP (Before opening):                                   │
│                                                                     │
│ □ Check main portal loads: your-domain.com                         │
│ □ Verify status banner shows correct info                           │
│ □ Confirm today's opening hours are displayed                       │
│ □ Test QR code scanning with phone                                  │
│ □ Check kiosk displays are running and current                      │
│ □ Verify all three languages work (DE/TH/EN)                        │
│                                                                     │
│ MIDDAY CHECK (Around lunch):                                       │
│                                                                     │
│ □ Status still accurate (especially if hours change)               │
│ □ Kiosk displays refreshing properly                               │
│ □ No error messages on screens                                     │
│ □ Internet connection stable                                        │
│                                                                     │
│ EVENING SHUTDOWN (After closing):                                  │
│                                                                     │
│ □ Update status if different hours tomorrow                         │
│ □ Add any announcements for tomorrow/next day                       │
│ □ Check for system update notifications                             │
│ □ Note any issues to report to tech support                        │
│                                                                     │
│ WEEKLY TASKS (Mark day completed):                                  │
│                                                                     │
│ □ Monday: Review upcoming week schedule                             │
│ □ Tuesday: Check QR code quality on printed materials               │
│ □ Wednesday: Clean kiosk screens and check brightness               │
│ □ Thursday: Test admin panel functions                              │
│ □ Friday: Review week's issues, plan updates                        │
│                                                                     │
│ ISSUES FOUND TODAY:                                                │
│ ________________________________________________________________   │
│ ________________________________________________________________   │
│ ________________________________________________________________   │
│                                                                     │
│ Action taken / Follow-up needed:                                   │
│ ________________________________________________________________   │
│ ________________________________________________________________   │
│                                                                     │
│ 📞 Report serious issues to: +66 38 123 456                       │
│ 📧 Email non-urgent issues to: tech@pattaya-medical.com           │
│                                                                     │
│ ✅ Checklist completed at: ____:____ by: _____________________     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚨 Emergency Response Card

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🚨 EMERGENCY RESPONSE CARD                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                   ⚡ SYSTEM COMPLETELY DOWN                         │
│                                                                     │
│ IMMEDIATE ACTIONS (First 5 minutes):                               │
│ 1. 📝 Post physical backup sign at entrance                        │
│ 2. 📞 Call emergency support: +66 38 123 999                       │
│ 3. 📧 Email: emergency@pattaya-medical.com                         │
│ 4. 📋 Note time system went down: ____:____                        │
│                                                                     │
│ BACKUP COMMUNICATION:                                               │
│ • Post paper sign with today's hours and status                    │
│ • Use social media to inform regular patients                      │
│ • Update voicemail message if applicable                            │
│ • Have staff inform visitors personally                             │
│                                                                     │
│                   ⚠️ PARTIAL SYSTEM FAILURE                        │
│                                                                     │
│ QR Codes Not Working:                                              │
│ • Verify internet connection                                       │
│ • Check SITE_URL in .env file                                      │
│ • Regenerate QR codes in admin panel                               │
│ • Call tech support if problem persists                            │
│                                                                     │
│ Admin Panel Not Accessible:                                        │
│ • Try different browser/device                                     │
│ • Check admin password in .env                                     │
│ • Restart server if possible                                       │
│ • Use manual updates temporarily                                   │
│                                                                     │
│ Status/Hours Not Updating:                                         │
│ • Hard refresh browsers (Ctrl+F5)                                  │
│ • Check database file permissions                                  │
│ • Try updating from different computer                             │
│ • Post physical notice as backup                                   │
│                                                                     │
│                   📞 ESCALATION CONTACTS                           │
│                                                                     │
│ Level 1 - Immediate (24/7):                                       │
│ 🚨 +66 38 123 999 (Emergency hotline)                             │
│ 💬 WhatsApp: +66 38 123 456                                        │
│                                                                     │
│ Level 2 - Technical (Business hours):                             │
│ 📧 tech@pattaya-medical.com                                        │
│ 📞 +66 38 123 456 (Mon-Fri 9 AM - 5 PM)                          │
│                                                                     │
│                   📝 INCIDENT REPORTING                            │
│                                                                     │
│ Date/Time: ________________________                               │
│ Problem Description: ____________________________________          │
│ _______________________________________________________          │
│ _______________________________________________________          │
│ Actions Taken: _________________________________________          │
│ _______________________________________________________          │
│ Resolution: ____________________________________________          │
│ _______________________________________________________          │
│ Reported by: ___________________________________________          │
│                                                                     │
│               🏥 BACKUP OPERATING PROCEDURES                       │
│                                                                     │
│ While system is down:                                              │
│ 1. Use printed schedules and status boards                         │
│ 2. Inform visitors verbally of current status                      │
│ 3. Take notes of changes needed for when system returns            │
│ 4. Document all manual communications made                          │
│                                                                     │
│                   ✅ POST-INCIDENT CHECKLIST                       │
│                                                                     │
│ After system restoration:                                          │
│ □ Verify all functions working normally                            │
│ □ Update any missed status/schedule changes                        │
│ □ Test QR codes and kiosk displays                                 │
│ □ Remove temporary physical signage                                 │
│ □ Complete incident report                                          │
│ □ Brief staff on any permanent changes made                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Staff Training Card

```
┌─────────────────────────────────────────────────────────────────────┐
│                      👩‍⚕️ STAFF TRAINING CARD                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ NEW STAFF ORIENTATION CHECKLIST:                                   │
│                                                                     │
│ □ Show location of QR codes around facility                        │
│ □ Demonstrate QR code scanning with personal phone                  │
│ □ Walk through public portal (all three languages)                 │
│ □ Explain status meanings and when to update                        │
│ □ Show admin login process and dashboard                            │
│ □ Practice updating status and opening hours                        │
│ □ Review daily checklist and responsibilities                       │
│ □ Explain emergency procedures and contacts                         │
│                                                                     │
│ KEY CONCEPTS TO UNDERSTAND:                                        │
│                                                                     │
│ Status Types:                                                      │
│ • ANWESEND (Green) = Normal operations                             │
│ • URLAUB (Orange) = Vacation/Holiday                               │
│ • BILDUNGSURLAUB (Blue) = Training/Education                       │
│ • KONGRESS (Purple) = Conference/Event                             │
│ • SONSTIGES (Gray) = Other/Custom message                          │
│                                                                     │
│ When to Update Status:                                             │
│ • Planned closures (vacations, training, holidays)                 │
│ • Unexpected closures (emergencies, illness)                       │
│ • Schedule changes (early closing, late opening)                   │
│ • Special announcements (new services, notices)                    │
│                                                                     │
│ Time Format Rules:                                                 │
│ • Always use 24-hour format: 08:30, 14:00, 17:30                  │
│ • Separate ranges with dash: 09:00-12:00                           │
│ • Multiple periods with comma: 08:30-12:00,13:00-16:00             │
│ • Leave blank for closed days                                      │
│                                                                     │
│ COMMON QUESTIONS FROM VISITORS:                                    │
│                                                                     │
│ Q: "The QR code won't scan"                                        │
│ A: "Try cleaning your camera lens and ensuring good lighting.       │
│     You can also type the URL directly: your-domain.com"           │
│                                                                     │
│ Q: "The website is in the wrong language"                          │
│ A: "Look for the flag icons in the top-right corner and            │
│     tap your preferred language flag."                             │
│                                                                     │
│ Q: "The hours shown are wrong"                                     │
│ A: "Let me check our system and update it if needed.               │
│     The current hours should be..."                                │
│                                                                     │
│ Q: "When will you be back if you're closed?"                       │
│ A: "Check the status banner - it shows our expected return date.   │
│     You can also call us at +66 38 123 456."                      │
│                                                                     │
│ PATIENT COMMUNICATION TIPS:                                        │
│                                                                     │
│ • Always verify information before giving to patients              │
│ • If unsure, check the admin dashboard for current status          │
│ • Keep language simple and clear                                   │
│ • Offer to help scan QR code if patient has difficulty             │
│ • Provide written backup if system is down                         │
│                                                                     │
│ TRAINING COMPETENCY CHECKLIST:                                     │
│                                                                     │
│ Can demonstrate:                              Verified by:         │
│ □ QR code scanning                            ________________     │
│ □ Language switching                          ________________     │
│ □ Admin panel login                           ________________     │
│ □ Status updates                              ________________     │
│ □ Hours management                            ________________     │
│ □ Emergency procedures                        ________________     │
│                                                                     │
│ Training completed: _________________ by: ____________________     │
│                                                                     │
│ 📞 Questions? Contact supervisor or tech support +66 38 123 456    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content":"Create comprehensive user manual in three languages (DE/TH/EN)","status":"completed","priority":"high","id":"1"},{"content":"Create admin guide with screenshots and step-by-step instructions","status":"completed","priority":"high","id":"2"},{"content":"Create installation and setup documentation","status":"completed","priority":"high","id":"3"},{"content":"Create in-app help system with contextual assistance","status":"completed","priority":"high","id":"4"},{"content":"Create interactive tooltips and help overlays","status":"completed","priority":"high","id":"5"},{"content":"Create troubleshooting guide and FAQ","status":"completed","priority":"medium","id":"6"},{"content":"Create API documentation for developers","status":"completed","priority":"medium","id":"7"},{"content":"Create configuration reference guide","status":"completed","priority":"medium","id":"8"},{"content":"Create getting started wizard for new users","status":"completed","priority":"medium","id":"9"},{"content":"Create quick reference cards and visual guides","status":"completed","priority":"low","id":"10"}]