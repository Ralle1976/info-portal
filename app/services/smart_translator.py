"""
Smart Translation Engine for QR Info Portal
Automatically translates ANY text/enum/code to user-friendly multilingual content
"""

import re
from typing import Dict, Any, Optional, Union
from enum import Enum
from app.models import StatusType
from app.services.i18n import I18nService


class SmartTranslator:
    """
    Universal translation system that can handle:
    - Enum values (StatusType.BILDUNGSURLAUB → "Educational Leave")
    - Technical terms (database_connection → "Database Connection") 
    - CamelCase (firstName → "First Name")
    - Snake_case (user_email → "User Email")
    - Any unknown text with intelligent fallbacks
    """
    
    # Core translation mappings for all languages
    UNIVERSAL_TRANSLATIONS = {
        # Status Types - Complete mapping
        'StatusType.ANWESEND': {
            'th': 'เปิดให้บริการ',
            'en': 'Currently Available', 
            'de': 'Anwesend'
        },
        'StatusType.URLAUB': {
            'th': 'ปิดทำการ - ลาพักผ่อน',
            'en': 'Closed - On Vacation',
            'de': 'Im Urlaub'
        },
        'StatusType.BILDUNGSURLAUB': {
            'th': 'ปิดทำการ - อบรมเพิ่มพูนความรู้',
            'en': 'Closed - Educational Training',
            'de': 'Fortbildung'
        },
        'StatusType.KONGRESS': {
            'th': 'ปิดทำการ - เข้าร่วมการประชุม',
            'en': 'Closed - At Conference', 
            'de': 'Kongressbesuch'
        },
        'StatusType.SONSTIGES': {
            'th': 'ปิดทำการ - เหตุผลอื่น',
            'en': 'Closed - Other Reason',
            'de': 'Sonstiges'
        },
        
        # Common technical terms
        'ANWESEND': {
            'th': 'เปิดให้บริการ',
            'en': 'Available',
            'de': 'Verfügbar'
        },
        'URLAUB': {
            'th': 'ลาพักผ่อน', 
            'en': 'Vacation',
            'de': 'Urlaub'
        },
        'BILDUNGSURLAUB': {
            'th': 'อบรมเพิ่มพูนความรู้',
            'en': 'Educational Training',
            'de': 'Fortbildung'
        },
        'KONGRESS': {
            'th': 'การประชุม',
            'en': 'Conference',
            'de': 'Kongress'
        },
        'SONSTIGES': {
            'th': 'อื่น ๆ',
            'en': 'Other',
            'de': 'Sonstiges'
        },
        
        # Database/System terms
        'database_connection': {
            'th': 'การเชื่อมต่อฐานข้อมูล',
            'en': 'Database Connection',
            'de': 'Datenbankverbindung'
        },
        'server_status': {
            'th': 'สถานะเซิร์ฟเวอร์',
            'en': 'Server Status', 
            'de': 'Serverstatus'
        },
        'system_online': {
            'th': 'ระบบออนไลน์',
            'en': 'System Online',
            'de': 'System Online'
        },
        'system_offline': {
            'th': 'ระบบออฟไลน์',
            'en': 'System Offline',
            'de': 'System Offline'
        }
    }
    
    @classmethod
    def translate(cls, text: Union[str, Enum, Any], language: str = None) -> str:
        """
        Universal translation function that handles ANY input.
        
        Args:
            text: Any text, enum, or object to translate
            language: Target language (th, en, de) - auto-detects if None
            
        Returns:
            Human-readable translated string
        """
        if not text:
            return ""
            
        # Get current language if not specified
        if not language:
            language = I18nService.get_current_language()
        
        # Convert input to string for processing
        text_str = str(text)
        
        # 1. Direct mapping lookup (highest priority)
        if text_str in cls.UNIVERSAL_TRANSLATIONS:
            return cls.UNIVERSAL_TRANSLATIONS[text_str].get(language, text_str)
        
        # 2. Handle Enum types specially
        if hasattr(text, '__class__') and hasattr(text.__class__, '__name__'):
            enum_key = f"{text.__class__.__name__}.{text_str}"
            if enum_key in cls.UNIVERSAL_TRANSLATIONS:
                return cls.UNIVERSAL_TRANSLATIONS[enum_key].get(language, text_str)
        
        # 3. Try without enum prefix (BILDUNGSURLAUB instead of StatusType.BILDUNGSURLAUB)
        if '.' in text_str:
            simple_key = text_str.split('.')[-1]
            if simple_key in cls.UNIVERSAL_TRANSLATIONS:
                return cls.UNIVERSAL_TRANSLATIONS[simple_key].get(language, simple_key)
        
        # 4. Intelligent fallback processing
        return cls._intelligent_fallback(text_str, language)
    
    @classmethod
    def _intelligent_fallback(cls, text: str, language: str) -> str:
        """
        Intelligent fallback for unknown terms using pattern recognition.
        """
        # Remove common prefixes/suffixes
        cleaned = text.replace('StatusType.', '').replace('_', ' ').replace('-', ' ')
        
        # Handle CamelCase (firstName → First Name)
        camel_split = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', cleaned)
        
        # Handle SCREAMING_SNAKE_CASE
        if text.isupper():
            words = cleaned.lower().split()
            cleaned = ' '.join(word.capitalize() for word in words)
        else:
            cleaned = camel_split
            
        # Language-specific formatting
        if language == 'th':
            # For Thai, add basic prefixes for technical terms
            if any(tech_word in text.lower() for tech_word in ['status', 'type', 'enum', 'class']):
                return f"สถานะ: {cleaned}"
            return cleaned
        elif language == 'de':
            # German: Capitalize first word
            return cleaned.capitalize()
        else:
            # English: Title case
            return cleaned.title()
    
    @classmethod 
    def add_translation(cls, key: str, translations: Dict[str, str]):
        """Add new translation dynamically."""
        cls.UNIVERSAL_TRANSLATIONS[key] = translations
    
    @classmethod
    def translate_status_message(cls, status_type: StatusType, description: str = None, 
                                date_from: str = None, date_to: str = None, 
                                language: str = None) -> str:
        """
        Create a complete, user-friendly status message.
        
        Args:
            status_type: StatusType enum
            description: Optional description
            date_from: Start date
            date_to: End date  
            language: Target language
            
        Returns:
            Complete translated status message
        """
        if not language:
            language = I18nService.get_current_language()
            
        # Get base status translation
        status_text = cls.translate(status_type, language)
        
        # Build complete message based on language
        if language == 'th':
            message = status_text
            if description:
                message += f" - {description}"
            if date_to:
                message += f" (กลับมาให้บริการ {date_to})"
            elif date_from:
                message += f" (เริ่มตั้งแต่ {date_from})"
        elif language == 'en': 
            message = status_text
            if description:
                message += f" - {description}"
            if date_to:
                message += f" (Back on {date_to})"
            elif date_from:
                message += f" (Since {date_from})"
        else:  # German
            message = status_text
            if description:
                message += f" - {description}"
            if date_to:
                message += f" (Zurück ab {date_to})"
            elif date_from:
                message += f" (Seit {date_from})"
                
        return message
    
    @classmethod
    def get_available_translations(cls) -> Dict[str, Dict[str, str]]:
        """Get all available translations for debugging."""
        return cls.UNIVERSAL_TRANSLATIONS.copy()
    
    @classmethod
    def validate_coverage(cls) -> Dict[str, Any]:
        """Validate translation coverage across all languages."""
        languages = ['th', 'en', 'de']
        stats = {
            'total_keys': len(cls.UNIVERSAL_TRANSLATIONS),
            'complete_translations': 0,
            'missing_by_language': {lang: [] for lang in languages},
            'coverage_rate': {}
        }
        
        for key, translations in cls.UNIVERSAL_TRANSLATIONS.items():
            complete = True
            for lang in languages:
                if lang not in translations or not translations[lang]:
                    stats['missing_by_language'][lang].append(key)
                    complete = False
            if complete:
                stats['complete_translations'] += 1
        
        # Calculate coverage rates
        for lang in languages:
            missing_count = len(stats['missing_by_language'][lang])
            coverage = ((stats['total_keys'] - missing_count) / stats['total_keys'] * 100) if stats['total_keys'] > 0 else 0
            stats['coverage_rate'][lang] = round(coverage, 1)
            
        return stats


# Global convenience function for templates and views
def smart_translate(text: Union[str, Enum, Any], language: str = None) -> str:
    """Global convenience function for smart translation."""
    return SmartTranslator.translate(text, language)


# Template filter function
def smart_translate_filter(text: Union[str, Enum, Any], language: str = None) -> str:
    """Jinja2 template filter for smart translation."""
    return SmartTranslator.translate(text, language)