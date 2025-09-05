from typing import Dict, Optional
from flask import request, session
import json
import os
from datetime import datetime, date
from .date_formatter import DateFormatterService


class I18nService:
    """Thai-First internationalization service with optional EN subtitles"""
    
    SUPPORTED_LANGUAGES = ['th', 'de', 'en']
    DEFAULT_LANGUAGE = 'th'
    PRIMARY_LANGUAGE = 'th'  # Always show Thai as primary
    SUBTITLE_LANGUAGE = 'en'  # Optional English subtitles
    
    translations = {}
    
    @classmethod
    def load_translations(cls):
        """Load translation files"""
        translations_dir = os.path.join(os.path.dirname(__file__), '..', 'translations')
        
        for lang in cls.SUPPORTED_LANGUAGES:
            file_path = os.path.join(translations_dir, f'{lang}.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    cls.translations[lang] = json.load(f)
            else:
                cls.translations[lang] = {}
    
    @classmethod
    def get_current_language(cls) -> str:
        """Get current language from session or request"""
        try:
            # Check URL parameter first (highest priority)
            if hasattr(request, 'args') and request.args.get('lang'):
                lang_param = request.args.get('lang')
                if lang_param in cls.SUPPORTED_LANGUAGES:
                    # Also save to session for consistency
                    session['language'] = lang_param
                    return lang_param
            
            # Check session second
            if hasattr(session, 'get') and session.get('language'):
                return session['language']
            
            # Check Accept-Language header
            if hasattr(request, 'accept_languages') and request.accept_languages:
                best_match = request.accept_languages.best_match(cls.SUPPORTED_LANGUAGES)
                if best_match:
                    return best_match
        except RuntimeError:
            # Outside of request context
            pass
        
        return cls.DEFAULT_LANGUAGE
    
    @classmethod
    def set_language(cls, language: str):
        """Set language in session"""
        try:
            if language in cls.SUPPORTED_LANGUAGES:
                session['language'] = language
        except RuntimeError:
            # Outside of request context
            pass
    
    @classmethod
    def translate(cls, key: str, language: Optional[str] = None, **kwargs) -> str:
        """Translate a key to current or specified language (supports nested keys with dot notation)"""
        if not cls.translations:
            cls.load_translations()
        
        lang = language or cls.get_current_language()
        
        # Handle nested keys (e.g., "ui_common.bangkok_time")
        def get_nested_value(data, key_path):
            keys = key_path.split('.')
            value = data
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return None
            return value
        
        # Try to get translation for current language
        translation = get_nested_value(cls.translations.get(lang, {}), key)
        
        # Fallback to default language
        if not translation and lang != cls.DEFAULT_LANGUAGE:
            translation = get_nested_value(cls.translations.get(cls.DEFAULT_LANGUAGE, {}), key)
        
        # Fallback to key itself
        if not translation:
            translation = key
        
        # Format with parameters if any
        if kwargs and isinstance(translation, str):
            try:
                translation = translation.format(**kwargs)
            except:
                pass
        
        return translation
    
    @classmethod
    def translate_thai_first(cls, key: str, with_subtitle: bool = True, **kwargs) -> Dict[str, str]:
        """Get Thai-first translation with optional English subtitle"""
        if not cls.translations:
            cls.load_translations()
        
        result = {
            'primary': cls.translate(key, language='th', **kwargs),
            'subtitle': None
        }
        
        # Add English subtitle if requested and not in Thai context
        if with_subtitle and cls.get_current_language() != 'en':
            result['subtitle'] = cls.translate(key, language='en', **kwargs)
        
        return result
    
    @classmethod
    def get_translations_for_language(cls, language: str) -> Dict:
        """Get all translations for a language"""
        if not cls.translations:
            cls.load_translations()
        
        return cls.translations.get(language, {})
    
    # Date and Time Formatting Methods
    @classmethod
    def format_date(cls, date_obj, format_type: str = 'short') -> str:
        """Format date according to current language settings"""
        current_lang = cls.get_current_language()
        return DateFormatterService.format_date(date_obj, current_lang, format_type)
    
    @classmethod
    def format_time(cls, time_obj, format_type: str = 'short') -> str:
        """Format time according to current language settings"""
        current_lang = cls.get_current_language()
        return DateFormatterService.format_time(time_obj, current_lang, format_type)
    
    @classmethod
    def format_datetime(cls, datetime_obj) -> str:
        """Format datetime according to current language settings"""
        current_lang = cls.get_current_language()
        return DateFormatterService.format_datetime(datetime_obj, current_lang)
    
    @classmethod
    def format_weekday(cls, date_obj) -> str:
        """Format weekday according to current language settings"""
        current_lang = cls.get_current_language()
        return DateFormatterService.format_weekday(date_obj, current_lang)
    
    @classmethod
    def format_month_year(cls, date_obj) -> str:
        """Format month and year according to current language settings"""
        current_lang = cls.get_current_language()
        return DateFormatterService.format_month_year(date_obj, current_lang)
    
    @classmethod
    def format_time_range(cls, start_time: str, end_time: str) -> str:
        """Format time range according to current language settings"""
        current_lang = cls.get_current_language()
        return DateFormatterService.get_time_range_format(start_time, end_time, current_lang)
    
    @classmethod
    def get_calendar_settings(cls) -> dict:
        """Get calendar settings for current language"""
        current_lang = cls.get_current_language()
        return DateFormatterService.get_calendar_settings(current_lang)


# Convenience function for templates
def t(key: str, **kwargs) -> str:
    """Template helper for translations"""
    return I18nService.translate(key, **kwargs)

# Thai-first convenience function for templates
def t_thai(key: str, with_subtitle: bool = True, **kwargs) -> Dict[str, str]:
    """Template helper for Thai-first translations with optional subtitle"""
    return I18nService.translate_thai_first(key, with_subtitle=with_subtitle, **kwargs)

# Date and Time formatting convenience functions for templates
def format_date(date_obj, format_type: str = 'short') -> str:
    """Template helper for date formatting"""
    return I18nService.format_date(date_obj, format_type)

def format_time(time_obj, format_type: str = 'short') -> str:
    """Template helper for time formatting"""
    return I18nService.format_time(time_obj, format_type)

def format_datetime(datetime_obj) -> str:
    """Template helper for datetime formatting"""
    return I18nService.format_datetime(datetime_obj)

def format_weekday(date_obj) -> str:
    """Template helper for weekday formatting"""
    return I18nService.format_weekday(date_obj)

def format_month_year(date_obj) -> str:
    """Template helper for month/year formatting"""
    return I18nService.format_month_year(date_obj)

def format_time_range(start_time: str, end_time: str) -> str:
    """Template helper for time range formatting"""
    return I18nService.format_time_range(start_time, end_time)