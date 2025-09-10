from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__)
    
    # Initialize comprehensive logging FIRST
    from app.logging_config import init_flask_logging
    app.logger = init_flask_logging(app)
    
    # SECURE SESSION CONFIGURATION
    import secrets
    from datetime import timedelta
    
    # Generate strong secret key if not provided
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key or secret_key == 'dev-secret-key':
        secret_key = secrets.token_hex(32)
        app.logger.warning("Using generated SECRET_KEY. Set SECRET_KEY environment variable for production!")
    else:
        app.logger.info("SECRET_KEY loaded from environment")
    
    app.config['SECRET_KEY'] = secret_key
    
    # SESSION SECURITY SETTINGS
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
    
    # CSRF PROTECTION SETTINGS
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    
    # SECURITY HEADERS & PERFORMANCE LOGGING
    @app.before_request
    def before_request():
        from flask import request, g
        import time
        g.start_time = time.time()
        
        # Log incoming requests (only for debugging, not in production)
        if app.config.get('LOG_REQUESTS', False):
            app.logger.debug(f"Request: {request.method} {request.path} from {request.remote_addr}")

    @app.after_request
    def security_headers(response):
        from flask import request, g
        from app.logging_config import log_performance
        import time
        
        # Calculate request duration
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            log_performance(request.endpoint or request.path, duration)
        
        # Prevent XSS
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # CSP (Content Security Policy)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        response.headers['Content-Security-Policy'] = csp
        
        return response
    
    # Initialize database
    from app.database import init_database
    with app.app_context():
        app.logger.info("Initializing database...")
        init_database()
        app.logger.info("Database initialized successfully")
    
    # Initialize Performance Caching
    from app.services.cache import cache
    app.cache = cache
    app.logger.info(f"Cache initialized: {cache.get_stats()}")
    
    # Generate QR codes on startup
    from app.services.qr import QRService
    site_url = os.getenv('SITE_URL', 'http://localhost:5000')
    app.logger.info(f"Generating QR codes for site: {site_url}")
    QRService.save_qr_files(site_url)
    app.logger.info("QR codes generated successfully")
    
    # Setup i18n
    from app.services.i18n import t, t_thai, I18nService
    
    # Force load translations on startup
    app.logger.info("Loading translations...")
    I18nService.load_translations()
    app.logger.info("Translations loaded successfully")
    
    # Setup help system
    from app.services.help_system import help_system, get_help_context, get_tooltip_text
    
    # Setup template globals for i18n and help
    app.jinja_env.globals.update(t=t)
    app.jinja_env.globals.update(t_thai=t_thai)
    app.jinja_env.globals.update(get_translation=I18nService.translate)
    app.jinja_env.globals.update(get_current_language=I18nService.get_current_language)
    app.jinja_env.globals.update(SUPPORTED_LANGUAGES=I18nService.SUPPORTED_LANGUAGES)
    app.jinja_env.globals.update(translate_thai_first=I18nService.translate_thai_first)
    app.jinja_env.globals.update(get_help_context=get_help_context)
    app.jinja_env.globals.update(get_tooltip_text=get_tooltip_text)
    app.jinja_env.globals.update(help_system=help_system)
    
    # Additional template helper functions
    @app.template_global()
    def translate_key(key, **kwargs):
        """Template function for translations"""
        return I18nService.translate(key, **kwargs)
    
    @app.template_global()
    def current_lang():
        """Get current language for templates"""
        return I18nService.get_current_language()
    
    @app.template_global()
    def csrf_token():
        """Generate CSRF token for templates"""
        from app.routes_admin import generate_csrf_token
        return generate_csrf_token()
    
    @app.template_global()
    def format_date(date_obj, format_str='%d.%m.%Y'):
        """Format date for templates"""
        if not date_obj:
            return ''
        if isinstance(date_obj, str):
            from datetime import datetime
            try:
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00')).date()
            except:
                return date_obj
        return date_obj.strftime(format_str)
    
    @app.template_global()
    def is_feature_enabled(feature_name):
        """Check if a feature flag is enabled"""
        import os
        return os.environ.get(feature_name, 'false').lower() == 'true'
    
    @app.template_global()
    def format_time(time_obj, format_str='%H:%M'):
        """Format time for templates"""
        if not time_obj:
            return ''
        if isinstance(time_obj, str):
            return time_obj
        return time_obj.strftime(format_str)
    
    @app.template_global()
    def t(key: str, **kwargs) -> str:
        """Template translation function"""
        from app.services.i18n import I18nService
        return I18nService.translate(key, **kwargs)
    
    @app.template_global()
    def current_language():
        """Get current language for templates"""
        from app.services.i18n import I18nService
        return I18nService.get_current_language()
    
    @app.template_global()
    def get_portal_theme():
        """Get the current portal theme from database"""
        try:
            from app.database import engine
            from app.models import Settings
            from sqlmodel import Session, select
            
            with Session(engine) as session:
                theme_setting = session.exec(
                    select(Settings).where(Settings.key == 'portal_theme')
                ).first()
                
                if theme_setting and theme_setting.value.get('theme'):
                    return theme_setting.value.get('theme')
                
                return 'medical-clean'  # default theme
        except Exception:
            return 'medical-clean'  # fallback to default
    
    # Register blueprints
    try:
        from app.routes_public import public_bp
        app.register_blueprint(public_bp)
    except Exception as e:
        print(f"Error loading public routes: {e}")
    
    try:
        from app.routes_admin import admin_bp
        app.register_blueprint(admin_bp)
    except Exception as e:
        print(f"Error loading admin routes: {e}")
    
    # Register legal routes
    try:
        from app.routes_legal import legal_bp, legal_admin_bp
        app.register_blueprint(legal_bp)
        app.register_blueprint(legal_admin_bp)
    except Exception as e:
        print(f"Error loading legal routes: {e}")
    
    # Conditionally register appointment routes if feature is enabled
    if os.getenv('FEATURE_BOOKING', 'false').lower() == 'true':
        from app.routes_appointments import bp as appointments_bp
        app.register_blueprint(appointments_bp)
    
    # Register help system routes
    try:
        from app.routes_help import help_bp
        app.register_blueprint(help_bp)
    except Exception as e:
        print(f"Error loading help routes: {e}")
    
    # Initialize legal compliance services
    from app.services.legal_compliance import legal_service
    from app.services.legal_labels import legal_labels
    
    # Setup legal compliance context (temporarily disabled)
    @app.context_processor
    def legal_context():
        return {
            'legal_labels': None,
            'legal_service': None
        }
    
    # Add legal template filters
    @app.template_filter('legal_format_date')
    def legal_format_date(date_obj, language='th'):
        if not date_obj:
            return ''
        return legal_labels.format_date(date_obj, language)
    
    @app.template_filter('legal_format_datetime')
    def legal_format_datetime(datetime_obj, language='th'):
        if not datetime_obj:
            return ''
        return legal_labels.format_datetime(datetime_obj, language)
    
    @app.template_filter('legal_label')
    def legal_label_filter(key, language='th', default=''):
        return legal_labels.get_label(key, language, default)
    
    # Add Smart Translation filter
    from app.services.smart_translator import smart_translate_filter
    app.template_filter('smart_translate')(smart_translate_filter)
    
    return app