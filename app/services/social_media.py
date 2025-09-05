"""
Social Media Integration Service
Handles integration with various social media platforms for the QR Info Portal
Provides QR code generation for social media links and content sharing
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select
import json
import qrcode
import io
import base64
from PIL import Image

from ..models import SocialMediaConfig, Settings
from ..database import get_session


class SocialMediaService:
    """Service for managing social media integrations"""
    
    def __init__(self, config=None):
        self.supported_platforms = [
            'line', 'facebook', 'instagram', 'tiktok', 
            'whatsapp', 'youtube', 'google_business'
        ]
        self._config = config or {}
        self._loaded_config = None
    
    @property
    def config(self):
        """Get consolidated config for all platforms"""
        if self._loaded_config is None:
            self._loaded_config = {}
            try:
                session = get_session()
                try:
                    configs = session.exec(
                        select(SocialMediaConfig).where(SocialMediaConfig.enabled == True)
                    ).all()
                    for config in configs:
                        self._loaded_config[config.platform] = config.config
                finally:
                    session.close()
            except Exception as e:
                # Fallback to empty config if database is not available
                print(f"Warning: Could not load social media config from database: {e}")
                self._loaded_config = self._config
        return self._loaded_config
    
    def get_platform_config(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific platform"""
        session = get_session()
        try:
            config = session.exec(
                select(SocialMediaConfig).where(SocialMediaConfig.platform == platform)
            ).first()
            
            if config and config.enabled:
                return config.config
            return None
        finally:
            session.close()
    
    def get_enabled_platforms(self) -> List[str]:
        """Get list of enabled platforms"""
        session = get_session()
        try:
            enabled_configs = session.exec(
                select(SocialMediaConfig).where(SocialMediaConfig.enabled == True)
            ).all()
            
            return [config.platform for config in enabled_configs]
        finally:
            session.close()
    
    def generate_qr_code(self, platform: str, size: str = 'medium') -> Optional[str]:
        """Generate QR code for platform URL"""
        config = self.get_platform_config(platform)
        if not config or not config.get('qr_enabled', False):
            return None
        
        url = config.get('url')
        if not url:
            return None
        
        # Size mapping
        size_mapping = {
            'small': (150, 150),
            'medium': (300, 300),
            'large': (600, 600)
        }
        
        qr_size = size_mapping.get(size, (300, 300))
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize(qr_size, Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def get_platform_urls(self) -> Dict[str, str]:
        """Get all enabled platform URLs"""
        urls = {}
        for platform in self.get_enabled_platforms():
            config = self.get_platform_config(platform)
            if config and config.get('url'):
                urls[platform] = config['url']
        
        return urls
    
    def get_social_media_stats(self) -> Dict[str, Any]:
        """Get social media statistics for admin dashboard"""
        enabled_platforms = self.get_enabled_platforms()
        
        return {
            'enabled_platforms': len(enabled_platforms),
            'platforms': enabled_platforms,
            'qr_enabled_count': len([
                p for p in enabled_platforms 
                if self.get_platform_config(p).get('qr_enabled', False)
            ])
        }
    
    def update_platform_config(self, platform: str, config: Dict[str, Any]) -> bool:
        """Update platform configuration"""
        if platform not in self.supported_platforms:
            return False
        
        session = get_session()
        try:
            platform_config = session.exec(
                select(SocialMediaConfig).where(SocialMediaConfig.platform == platform)
            ).first()
            
            if platform_config:
                platform_config.config = config
                platform_config.enabled = config.get('enabled', False)
                platform_config.qr_enabled = config.get('qr_enabled', False)
                platform_config.updated_at = datetime.utcnow()
            else:
                platform_config = SocialMediaConfig(
                    platform=platform,
                    enabled=config.get('enabled', False),
                    config=config,
                    qr_enabled=config.get('qr_enabled', False)
                )
                session.add(platform_config)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error updating platform config: {e}")
            return False
        finally:
            session.close()
    
    def get_platforms_for_display(self) -> List[Dict[str, Any]]:
        """Get platforms formatted for template display - returns list of enabled platforms with valid URLs"""
        result = []
        
        # Check if social media is globally enabled
        if not self.is_social_media_enabled():
            return result
        
        # Load config from yaml file for platform definitions
        import yaml
        try:
            with open('config.yml', 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
                social_config = yaml_config.get('social_media', {})
        except Exception as e:
            print(f"Warning: Could not load config.yml: {e}")
            social_config = {}
        
        # Only include platforms that are enabled and have valid URLs
        if social_config.get('enabled', False):
            platforms_config = social_config.get('platforms', {})
            
            for platform_name, platform_config in platforms_config.items():
                if (platform_config.get('enabled', False) and 
                    platform_config.get('url') and 
                    platform_config['url'].strip()):
                    
                    # Platform icon and color mapping
                    platform_display = self._get_platform_display_info(platform_name)
                    
                    result.append({
                        'name': platform_name,
                        'display_name': platform_display['display_name'],
                        'url': platform_config['url'],
                        'username': platform_config.get('username') or platform_config.get('official_account', ''),
                        'icon': platform_display['icon'],
                        'color': platform_display['color'],
                        'qr_enabled': platform_config.get('qr_enabled', False)
                    })
        
        return result
    
    def generate_platform_qr(self, platform: str, size: str = 'medium') -> Optional[str]:
        """Generate QR code file for a platform and return filename"""
        qr_data = self.generate_qr_code(platform, size)
        if not qr_data:
            return None
        
        import os
        from pathlib import Path
        import base64
        
        # Ensure static/qr directory exists
        qr_dir = Path("app/static/qr")
        qr_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{platform}_{size}.png"
        file_path = qr_dir / filename
        
        # Save QR code as PNG file
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(qr_data))
        
        return filename
    
    def is_social_media_enabled(self) -> bool:
        """Check if social media features are globally enabled"""
        try:
            import yaml
            with open('config.yml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('social_media', {}).get('enabled', False)
        except Exception:
            return False
    
    def has_enabled_platforms(self) -> bool:
        """Check if there are any enabled platforms with valid URLs"""
        return len(self.get_platforms_for_display()) > 0
    
    def _get_platform_display_info(self, platform_name: str) -> Dict[str, str]:
        """Get display information for a platform"""
        platform_info = {
            'line': {
                'display_name': 'LINE',
                'icon': 'fab fa-line',
                'color': '#00C300'
            },
            'facebook': {
                'display_name': 'Facebook',
                'icon': 'fab fa-facebook-f',
                'color': '#1877F2'
            },
            'instagram': {
                'display_name': 'Instagram',
                'icon': 'fab fa-instagram',
                'color': '#E4405F'
            },
            'tiktok': {
                'display_name': 'TikTok',
                'icon': 'fab fa-tiktok',
                'color': '#000000'
            },
            'whatsapp': {
                'display_name': 'WhatsApp',
                'icon': 'fab fa-whatsapp',
                'color': '#25D366'
            },
            'youtube': {
                'display_name': 'YouTube',
                'icon': 'fab fa-youtube',
                'color': '#FF0000'
            },
            'google_business': {
                'display_name': 'Google Business',
                'icon': 'fab fa-google',
                'color': '#4285F4'
            }
        }
        
        return platform_info.get(platform_name, {
            'display_name': platform_name.replace('_', ' ').title(),
            'icon': 'fas fa-external-link-alt',
            'color': '#6B7280'
        })
    
    def format_content_for_platform(self, platform: str, content: str, language: str) -> str:
        """Format content for specific social media platform"""
        # Basic content formatting based on platform requirements
        if platform == 'line':
            # LINE allows up to 5000 characters
            return content[:5000]
        elif platform == 'facebook':
            # Facebook allows up to 63,206 characters but recommend shorter
            return content[:2000]
        elif platform == 'instagram':
            # Instagram allows up to 2200 characters
            return content[:2200]
        elif platform == 'tiktok':
            # TikTok allows up to 300 characters
            return content[:300]
        elif platform == 'whatsapp':
            # WhatsApp allows up to 65,536 characters but recommend shorter
            return content[:1000]
        else:
            return content


# Global service instance
social_media_service = SocialMediaService()