"""
Date and Time Formatting Service - Country/Language Specific
Provides localized date and time formatting for different countries and languages
"""
from datetime import datetime, date, time
from typing import Union, Optional, Dict, Any
import locale
import calendar

class DateFormatterService:
    """Service for formatting dates and times according to language/region"""
    
    # Format configurations by language/country
    FORMATS = {
        'th': {  # Thailand
            'country': 'Thailand',
            'locale': 'th_TH.UTF-8',
            'date_format': '%d/%m/%Y',          # 24/08/2025 (dd/mm/yyyy)
            'date_format_long': '%d %B %Y',     # 24 สิงหาคม 2025
            'time_format': '%H:%M',             # 14:30 (24-hour)
            'time_format_long': '%H:%M:%S',     # 14:30:45
            'datetime_format': '%d/%m/%Y %H:%M', # 24/08/2025 14:30
            'weekday_format': '%A',             # วันจันทร์
            'month_year': '%B %Y',              # สิงหาคม 2025
            'first_day_of_week': 0,             # Monday (ISO standard in Thailand)
            'am_pm': False,                     # Use 24-hour format
        },
        'de': {  # Germany
            'country': 'Germany',
            'locale': 'de_DE.UTF-8',
            'date_format': '%d.%m.%Y',          # 24.08.2025 (dd.mm.yyyy)
            'date_format_long': '%d. %B %Y',    # 24. August 2025
            'time_format': '%H:%M',             # 14:30 (24-hour)
            'time_format_long': '%H:%M:%S',     # 14:30:45
            'datetime_format': '%d.%m.%Y %H:%M', # 24.08.2025 14:30
            'weekday_format': '%A',             # Montag
            'month_year': '%B %Y',              # August 2025
            'first_day_of_week': 0,             # Monday (German standard)
            'am_pm': False,                     # Use 24-hour format
        },
        'en': {  # English (International/US)
            'country': 'United States',
            'locale': 'en_US.UTF-8',
            'date_format': '%m/%d/%Y',          # 08/24/2025 (mm/dd/yyyy)
            'date_format_long': '%B %d, %Y',    # August 24, 2025
            'time_format': '%I:%M %p',          # 2:30 PM (12-hour)
            'time_format_long': '%I:%M:%S %p',  # 2:30:45 PM
            'datetime_format': '%m/%d/%Y %I:%M %p', # 08/24/2025 2:30 PM
            'weekday_format': '%A',             # Monday
            'month_year': '%B %Y',              # August 2025
            'first_day_of_week': 6,             # Sunday (US standard)
            'am_pm': True,                      # Use 12-hour format with AM/PM
        }
    }
    
    # Thai month names (for better localization)
    THAI_MONTHS = {
        1: 'มกราคม', 2: 'กุมภาพันธ์', 3: 'มีนาคม', 4: 'เมษายน',
        5: 'พฤษภาคม', 6: 'มิถุนายน', 7: 'กรกฎาคม', 8: 'สิงหาคม',
        9: 'กันยายน', 10: 'ตุลาคม', 11: 'พฤศจิกายน', 12: 'ธันวาคม'
    }
    
    # Thai day names
    THAI_WEEKDAYS = {
        0: 'วันจันทร์', 1: 'วันอังคาร', 2: 'วันพุธ', 3: 'วันพฤหัสบดี',
        4: 'วันศุกร์', 5: 'วันเสาร์', 6: 'วันอาทิตย์'
    }
    
    @classmethod
    def get_language_format(cls, lang: str) -> Dict[str, Any]:
        """Get format configuration for language"""
        return cls.FORMATS.get(lang, cls.FORMATS['en'])  # Default to English
    
    @classmethod
    def format_date(cls, date_obj: Union[datetime, date], lang: str = 'en', format_type: str = 'short') -> str:
        """
        Format date according to language/country conventions
        
        Args:
            date_obj: Date or datetime object to format
            lang: Language code ('th', 'de', 'en')
            format_type: 'short' or 'long' format
            
        Returns:
            Formatted date string
        """
        if date_obj is None:
            return ""
        
        # Convert datetime to date if needed
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        
        fmt_config = cls.get_language_format(lang)
        
        if format_type == 'long':
            format_str = fmt_config['date_format_long']
        else:
            format_str = fmt_config['date_format']
        
        # Special handling for Thai
        if lang == 'th':
            return cls._format_thai_date(date_obj, format_type)
        
        try:
            return date_obj.strftime(format_str)
        except Exception:
            # Fallback to ISO format
            return date_obj.isoformat()
    
    @classmethod
    def format_time(cls, time_obj: Union[datetime, time], lang: str = 'en', format_type: str = 'short') -> str:
        """
        Format time according to language/country conventions
        
        Args:
            time_obj: Time or datetime object to format
            lang: Language code ('th', 'de', 'en')
            format_type: 'short' or 'long' format
            
        Returns:
            Formatted time string
        """
        if time_obj is None:
            return ""
        
        # Convert datetime to time if needed
        if isinstance(time_obj, datetime):
            time_obj = time_obj.time()
        
        fmt_config = cls.get_language_format(lang)
        
        if format_type == 'long':
            format_str = fmt_config['time_format_long']
        else:
            format_str = fmt_config['time_format']
        
        try:
            # For time objects, we need to create a datetime to use strftime
            if isinstance(time_obj, time):
                # Create a dummy date to format time
                dummy_datetime = datetime.combine(date.today(), time_obj)
                return dummy_datetime.strftime(format_str)
            else:
                return time_obj.strftime(format_str)
        except Exception:
            # Fallback to HH:MM format
            if isinstance(time_obj, time):
                return f"{time_obj.hour:02d}:{time_obj.minute:02d}"
            return time_obj.strftime('%H:%M')
    
    @classmethod
    def format_datetime(cls, datetime_obj: datetime, lang: str = 'en') -> str:
        """
        Format datetime according to language/country conventions
        
        Args:
            datetime_obj: Datetime object to format
            lang: Language code ('th', 'de', 'en')
            
        Returns:
            Formatted datetime string
        """
        if datetime_obj is None:
            return ""
        
        fmt_config = cls.get_language_format(lang)
        format_str = fmt_config['datetime_format']
        
        # Special handling for Thai
        if lang == 'th':
            date_part = cls._format_thai_date(datetime_obj.date(), 'short')
            time_part = datetime_obj.strftime('%H:%M')
            return f"{date_part} {time_part}"
        
        try:
            return datetime_obj.strftime(format_str)
        except Exception:
            # Fallback to ISO format
            return datetime_obj.isoformat()
    
    @classmethod
    def format_weekday(cls, date_obj: Union[datetime, date], lang: str = 'en') -> str:
        """
        Format weekday name according to language
        
        Args:
            date_obj: Date or datetime object
            lang: Language code ('th', 'de', 'en')
            
        Returns:
            Localized weekday name
        """
        if date_obj is None:
            return ""
        
        # Convert datetime to date if needed
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        
        # Special handling for Thai
        if lang == 'th':
            return cls.THAI_WEEKDAYS.get(date_obj.weekday(), 'วันจันทร์')
        
        fmt_config = cls.get_language_format(lang)
        
        try:
            return date_obj.strftime(fmt_config['weekday_format'])
        except Exception:
            # Fallback to English
            english_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return english_days[date_obj.weekday()]
    
    @classmethod
    def format_month_year(cls, date_obj: Union[datetime, date], lang: str = 'en') -> str:
        """
        Format month and year according to language
        
        Args:
            date_obj: Date or datetime object
            lang: Language code ('th', 'de', 'en')
            
        Returns:
            Localized month and year
        """
        if date_obj is None:
            return ""
        
        # Convert datetime to date if needed
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        
        # Special handling for Thai
        if lang == 'th':
            month_name = cls.THAI_MONTHS.get(date_obj.month, 'มกราคม')
            return f"{month_name} {date_obj.year}"
        
        fmt_config = cls.get_language_format(lang)
        
        try:
            return date_obj.strftime(fmt_config['month_year'])
        except Exception:
            # Fallback to English
            return date_obj.strftime('%B %Y')
    
    @classmethod
    def get_time_range_format(cls, start_time: str, end_time: str, lang: str = 'en') -> str:
        """
        Format time range according to language conventions
        
        Args:
            start_time: Start time string (HH:MM format)
            end_time: End time string (HH:MM format)
            lang: Language code
            
        Returns:
            Formatted time range string
        """
        if not start_time or not end_time:
            return ""
        
        fmt_config = cls.get_language_format(lang)
        
        # Parse times
        try:
            start_dt = datetime.strptime(start_time, '%H:%M')
            end_dt = datetime.strptime(end_time, '%H:%M')
            
            if fmt_config['am_pm']:
                # 12-hour format with AM/PM
                start_str = start_dt.strftime('%I:%M %p').lstrip('0')
                end_str = end_dt.strftime('%I:%M %p').lstrip('0')
            else:
                # 24-hour format
                start_str = start_dt.strftime('%H:%M')
                end_str = end_dt.strftime('%H:%M')
            
            # Use appropriate separator
            if lang == 'de':
                return f"{start_str}-{end_str}"  # German style
            elif lang == 'th':
                return f"{start_str}-{end_str}"  # Thai style (24-hour)
            else:
                return f"{start_str} - {end_str}"  # English style with spaces
                
        except Exception:
            # Fallback to original format
            return f"{start_time}-{end_time}"
    
    @classmethod
    def _format_thai_date(cls, date_obj: date, format_type: str) -> str:
        """Format date specifically for Thai language"""
        if format_type == 'long':
            day = date_obj.day
            month_name = cls.THAI_MONTHS.get(date_obj.month, 'มกราคม')
            year = date_obj.year
            return f"{day} {month_name} {year}"
        else:
            # Short format: dd/mm/yyyy
            return date_obj.strftime('%d/%m/%Y')
    
    @classmethod
    def get_calendar_settings(cls, lang: str = 'en') -> Dict[str, Any]:
        """
        Get calendar settings for language/country
        
        Args:
            lang: Language code
            
        Returns:
            Dictionary with calendar settings
        """
        fmt_config = cls.get_language_format(lang)
        
        return {
            'first_day_of_week': fmt_config['first_day_of_week'],
            'date_format': fmt_config['date_format'],
            'time_format': fmt_config['time_format'],
            'use_am_pm': fmt_config['am_pm'],
            'country': fmt_config['country']
        }