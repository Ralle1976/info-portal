# Changelog

All notable changes to QR-Info-Portal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release preparation
- GitHub repository setup
- Comprehensive documentation structure

## [1.0.0] - 2025-08-27

### Added
- 🌐 **Multi-language support** (DE/TH/EN) with automatic detection
- 📱 **Responsive design** optimized for all devices
- 🎨 **Thai-inspired medical design system** with modern aesthetics
- 📊 **Admin dashboard** with secure authentication
- 🖥️ **Kiosk modes** (single/triple/rotation) for on-site displays
- 📅 **Flexible scheduling** with regular hours and exceptions
- 🔒 **GDPR/PDPA compliance** with privacy controls
- 📧 **Contact management** with QR code generation
- 🗺️ **Google Maps integration** for directions
- 📈 **Status management** (Present/Vacation/Training/Conference)
- 🔧 **Setup wizard** for easy initial configuration
- 📋 **Help system** with FAQ and user manual
- 🎯 **Appointment booking system** (indicative slots)
- 🔐 **Security enhancements** with CSRF protection
- 📲 **Social media QR codes** for LINE, Facebook, etc.

### Technical Features
- **Backend**: Python 3.11+, Flask 3.0
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Tailwind CSS, HTMX, Alpine.js
- **QR Generation**: Python qrcode with PNG/SVG output
- **Logging**: Structured logging with rotation
- **Testing**: Comprehensive test suite with pytest
- **Docker**: Full containerization support
- **CI/CD**: GitHub Actions workflow ready

### Security
- Basic authentication for admin panel
- CSRF token protection
- Input validation and sanitization
- Secure session management
- Rate limiting on sensitive endpoints

### Documentation
- Complete API documentation
- Installation guides
- Admin and user manuals
- Configuration reference
- Troubleshooting guide
- Contributing guidelines

## [0.9.0] - 2025-08-20 (Beta)

### Added
- Beta testing phase
- Core functionality implementation
- Basic admin interface
- QR code generation
- Multi-language framework

### Fixed
- Various UI/UX improvements
- Translation consistency
- Mobile responsiveness issues

## [0.5.0] - 2025-08-15 (Alpha)

### Added
- Project initialization
- Basic Flask application structure
- Database models
- Initial templating system

### Known Issues
- Limited browser testing
- Incomplete translations
- Basic error handling

---

## Version History Format

### Version Numbering
- **MAJOR** version for incompatible API changes
- **MINOR** version for functionality additions (backwards-compatible)
- **PATCH** version for backwards-compatible bug fixes

### Change Categories
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

### Links
[Unreleased]: https://github.com/Ralle1976/qr-info-portal/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Ralle1976/qr-info-portal/releases/tag/v1.0.0
[0.9.0]: https://github.com/Ralle1976/qr-info-portal/releases/tag/v0.9.0
[0.5.0]: https://github.com/Ralle1976/qr-info-portal/releases/tag/v0.5.0