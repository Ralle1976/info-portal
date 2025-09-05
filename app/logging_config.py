"""
Centralized Logging Configuration for QR Info Portal
Supports different environments with proper log rotation and structured formatting
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


class QRPortalLogFormatter(logging.Formatter):
    """Custom formatter with color support and structured format"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add color for console output
        if hasattr(record, 'color') and record.color:
            color = self.COLORS.get(record.levelname, '')
            reset = self.RESET
        else:
            color = reset = ''
            
        # Structure: [TIMESTAMP] [LEVEL] [MODULE] MESSAGE
        formatted = f"{color}[{self.formatTime(record, '%Y-%m-%d %H:%M:%S')}] " \
                   f"[{record.levelname:8}] [{record.name:20}] {record.getMessage()}{reset}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
            
        return formatted


def setup_logging(app_name="qr-info-portal", log_level="INFO", environment="development"):
    """
    Setup comprehensive logging for the QR Info Portal
    
    Args:
        app_name: Application name for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)  
        environment: Environment (development, production, testing)
    """
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console Handler (with colors for development)
    console_handler = logging.StreamHandler()
    if environment == "development":
        console_formatter = QRPortalLogFormatter()
        # Add color attribute for console logs
        console_handler.addFilter(lambda record: setattr(record, 'color', True) or True)
    else:
        console_formatter = QRPortalLogFormatter()
        console_handler.addFilter(lambda record: setattr(record, 'color', False) or True)
    
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # File Handler - Main Application Log (with rotation)
    app_log_file = log_dir / f"{app_name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_formatter = QRPortalLogFormatter()
    file_handler.addFilter(lambda record: setattr(record, 'color', False) or True)
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    
    # Error Handler - Only Errors and Above
    error_log_file = log_dir / f"{app_name}-errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setFormatter(file_formatter)
    error_handler.addFilter(lambda record: setattr(record, 'color', False) or True)
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)
    
    # Admin Actions Handler - Security & Admin Events
    admin_log_file = log_dir / f"{app_name}-admin.log"
    admin_handler = logging.handlers.RotatingFileHandler(
        admin_log_file,
        maxBytes=2*1024*1024,  # 2MB
        backupCount=10,  # Keep more admin logs for audit
        encoding='utf-8'
    )
    admin_handler.setFormatter(file_formatter)
    admin_handler.addFilter(lambda record: setattr(record, 'color', False) or True)
    admin_handler.addFilter(lambda record: hasattr(record, 'admin_action'))
    logger.addHandler(admin_handler)
    
    # Performance Handler - Slow requests and performance metrics
    if environment in ["production", "staging"]:
        perf_log_file = log_dir / f"{app_name}-performance.log"
        perf_handler = logging.handlers.RotatingFileHandler(
            perf_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        perf_handler.setFormatter(file_formatter)
        perf_handler.addFilter(lambda record: setattr(record, 'color', False) or True)
        perf_handler.addFilter(lambda record: hasattr(record, 'performance'))
        logger.addHandler(perf_handler)
    
    # Initial startup log
    startup_logger = logging.getLogger('qr_portal.startup')
    startup_logger.info(f"=== QR Info Portal Logging Started ===")
    startup_logger.info(f"Environment: {environment}")
    startup_logger.info(f"Log Level: {log_level}")
    startup_logger.info(f"Log Directory: {log_dir.absolute()}")
    startup_logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    return logger


def get_logger(name):
    """Get a logger with standardized naming convention"""
    return logging.getLogger(f"qr_portal.{name}")


def log_admin_action(action, user, details=None, ip_address=None):
    """Log admin actions for security audit"""
    logger = get_logger('admin')
    
    message = f"Admin Action: {action} by {user}"
    if ip_address:
        message += f" from {ip_address}"
    if details:
        message += f" - {details}"
    
    # Add admin_action marker for filtering
    record = logger.makeRecord(
        logger.name, logging.INFO, "", 0, message, (), None
    )
    record.admin_action = True
    logger.handle(record)


def log_performance(endpoint, duration, details=None):
    """Log performance metrics for slow requests"""
    if duration > 1.0:  # Log requests slower than 1 second
        logger = get_logger('performance')
        
        message = f"Slow Request: {endpoint} took {duration:.2f}s"
        if details:
            message += f" - {details}"
        
        record = logger.makeRecord(
            logger.name, logging.WARNING, "", 0, message, (), None
        )
        record.performance = True
        logger.handle(record)


def log_security_event(event_type, details, severity="WARNING"):
    """Log security events"""
    logger = get_logger('security')
    
    level = getattr(logging, severity.upper())
    message = f"Security Event [{event_type}]: {details}"
    
    logger.log(level, message)


def log_smart_translation_event(event, details):
    """Log Smart Translation Engine events"""
    logger = get_logger('smart_translation')
    logger.info(f"Smart Translation [{event}]: {details}")


# Flask Integration Helper
def init_flask_logging(app):
    """Initialize Flask-specific logging"""
    
    # Setup main logging
    environment = app.config.get('FLASK_ENV', 'development')
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    
    setup_logging(
        app_name="qr-info-portal",
        log_level=log_level,
        environment=environment
    )
    
    # Replace Flask's logger
    app.logger = get_logger('flask_app')
    
    # Log startup information
    startup_logger = get_logger('startup')
    startup_logger.info(f"Flask App initialized - Debug: {app.debug}")
    startup_logger.info(f"Secret Key configured: {bool(app.secret_key)}")
    startup_logger.info(f"Environment: {environment}")
    
    return app.logger