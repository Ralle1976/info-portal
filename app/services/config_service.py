"""
Configuration Service for QR Info Portal
Handles reading and processing of config.yml with proper language support
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.services.i18n import I18nService
from app.logging_config import get_logger

logger = get_logger('config_service')


class ConfigService:
    """Service for handling configuration with multi-language support"""
    
    _config_cache = None
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load configuration from config.yml with caching"""
        if cls._config_cache is not None:
            return cls._config_cache
            
        try:
            config_path = Path('config.yml')
            if not config_path.exists():
                logger.error(f"Config file not found: {config_path}")
                return {}
                
            with open(config_path, 'r', encoding='utf-8') as f:
                cls._config_cache = yaml.safe_load(f) or {}
                logger.info("Configuration loaded successfully")
                return cls._config_cache
                
        except Exception as e:
            logger.error(f"Error loading config.yml: {e}")
            return {}
    
    @classmethod
    def reload_config(cls):
        """Force reload of configuration"""
        cls._config_cache = None
        logger.info("Configuration cache cleared - will reload on next access")
    
    @classmethod
    def get_services(cls, language: str = None) -> List[str]:
        """Get services list for specified language"""
        if not language:
            language = I18nService.get_current_language()
            
        config = cls.load_config()
        services_config = config.get('services', {}).get('standard', [])
        
        if not services_config:
            logger.warning("No services configured in config.yml")
            return []
        
        services = []
        for service in services_config:
            if isinstance(service, str):
                # Legacy string format
                services.append(service)
                logger.debug(f"Legacy string service: {service}")
            elif isinstance(service, dict) and 'name' in service:
                # New multilingual format
                if isinstance(service['name'], dict):
                    # Get service name for current language with fallback
                    service_name = service['name'].get(language)
                    if not service_name:
                        # Fallback to German, then English, then first available
                        service_name = (service['name'].get('de') or 
                                      service['name'].get('en') or 
                                      next(iter(service['name'].values()), 'Unknown Service'))
                        logger.debug(f"Used fallback for service in language '{language}': {service_name}")
                    services.append(service_name)
                else:
                    # Simple name field
                    services.append(service['name'])
            else:
                logger.warning(f"Invalid service format in config: {service}")
                services.append(str(service))
        
        logger.info(f"Retrieved {len(services)} services for language '{language}'")
        return services
    
    @classmethod
    def get_site_config(cls) -> Dict[str, Any]:
        """Get site configuration"""
        config = cls.load_config()
        return config.get('site', {})
    
    @classmethod
    def get_location_config(cls) -> Dict[str, Any]:
        """Get location configuration"""
        config = cls.load_config()
        return config.get('location', {})
    
    @classmethod
    def get_contact_config(cls) -> Dict[str, Any]:
        """Get contact configuration"""
        config = cls.load_config()
        return config.get('contact', {})
    
    @classmethod
    def get_status_config(cls) -> Dict[str, Any]:
        """Get current status configuration"""
        config = cls.load_config()
        return config.get('status', {}).get('current', {})
    
    @classmethod
    def get_hours_config(cls) -> Dict[str, Any]:
        """Get opening hours configuration"""
        config = cls.load_config()
        return config.get('hours', {})
    
    @classmethod
    def get_social_media_config(cls) -> Dict[str, Any]:
        """Get social media configuration"""
        config = cls.load_config()
        return config.get('social_media', {})
    
    @classmethod
    def update_services(cls, services: List[Dict[str, Any]]):
        """Update services in configuration"""
        try:
            config = cls.load_config()
            if 'services' not in config:
                config['services'] = {}
            config['services']['standard'] = services
            
            # Save back to file
            config_path = Path('config.yml')
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            
            # Clear cache to force reload
            cls.reload_config()
            logger.info("Services updated in configuration")
            
        except Exception as e:
            logger.error(f"Error updating services: {e}")
            raise
    
    @classmethod
    def validate_config_structure(cls) -> Dict[str, List[str]]:
        """Validate configuration structure and return issues"""
        config = cls.load_config()
        issues = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Check required sections
        required_sections = ['site', 'location', 'contact', 'services', 'status', 'hours']
        for section in required_sections:
            if section not in config:
                issues['errors'].append(f"Missing required section: {section}")
        
        # Check services structure
        services = config.get('services', {}).get('standard', [])
        if services:
            mixed_format = False
            for i, service in enumerate(services):
                if isinstance(service, str):
                    # Legacy format
                    if any(isinstance(s, dict) for s in services):
                        mixed_format = True
                elif isinstance(service, dict):
                    if 'name' not in service:
                        issues['errors'].append(f"Service {i} missing 'name' field")
                    elif isinstance(service['name'], dict):
                        # Check for required languages
                        missing_languages = []
                        for lang in ['th', 'de', 'en']:
                            if lang not in service['name']:
                                missing_languages.append(lang)
                        if missing_languages:
                            issues['warnings'].append(f"Service {i} missing languages: {missing_languages}")
            
            if mixed_format:
                issues['warnings'].append("Services use mixed format (string + object) - consider standardizing")
        
        return issues