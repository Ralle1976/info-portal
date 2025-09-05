"""
Exception Engine für Sondertage und Feiertage
Erweiterte Logik für das QR-Info-Portal mit thailändischen Feiertagen

Dieses Modul verwaltet Ausnahmen von regulären Öffnungszeiten:
- Thailändische Feiertage (Buddhist, Royal, National)
- Lokale Sonderveranstaltungen  
- Unternehmensspezifische Schließtage
- Saisonale Anpassungen

Bangkok timezone (Asia/Bangkok) wird durchgängig verwendet.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlmodel import Session, select
import pytz
import logging
from enum import Enum
from dataclasses import dataclass

from app.models import HourException
from app.database import engine

logger = logging.getLogger(__name__)


class ExceptionType(Enum):
    """Typen von Ausnahmen"""
    THAI_HOLIDAY = "THAI_HOLIDAY"
    BUDDHIST_HOLIDAY = "BUDDHIST_HOLIDAY"
    ROYAL_HOLIDAY = "ROYAL_HOLIDAY"
    NATIONAL_HOLIDAY = "NATIONAL_HOLIDAY"
    LOCAL_EVENT = "LOCAL_EVENT"
    COMPANY_CLOSURE = "COMPANY_CLOSURE"
    SEASONAL_ADJUSTMENT = "SEASONAL_ADJUSTMENT"
    EMERGENCY_CLOSURE = "EMERGENCY_CLOSURE"
    EXTENDED_HOURS = "EXTENDED_HOURS"
    SPECIAL_HOURS = "SPECIAL_HOURS"


@dataclass
class ThaiHoliday:
    """Thailändischer Feiertag"""
    name_th: str
    name_de: str
    name_en: str
    date: date
    type: ExceptionType
    is_national: bool = True
    affects_business: bool = True
    description_th: Optional[str] = None
    description_de: Optional[str] = None
    description_en: Optional[str] = None
    
    def get_name(self, lang: str = 'th') -> str:
        """Hole Namen in gewünschter Sprache"""
        return getattr(self, f'name_{lang}', self.name_th)
    
    def get_description(self, lang: str = 'th') -> str:
        """Hole Beschreibung in gewünschter Sprache"""
        desc = getattr(self, f'description_{lang}', None)
        return desc or self.get_name(lang)


class ThaiHolidayCalculator:
    """
    Berechnung thailändischer Feiertage
    Unterstützt sowohl fixe als auch variable Feiertage
    """
    
    BANGKOK_TZ = pytz.timezone('Asia/Bangkok')
    
    @staticmethod
    def get_fixed_holidays(year: int) -> List[ThaiHoliday]:
        """Fixe thailändische Feiertage für ein Jahr"""
        return [
            # New Year
            ThaiHoliday(
                name_th="วันขึ้นปีใหม่",
                name_de="Neujahr",
                name_en="New Year's Day",
                date=date(year, 1, 1),
                type=ExceptionType.NATIONAL_HOLIDAY,
                description_th="วันหยุดปีใหม่สากล"
            ),
            
            # Chinese New Year (variable - approximation)
            ThaiHoliday(
                name_th="วันตรุษจีน",
                name_de="Chinesisches Neujahr",
                name_en="Chinese New Year",
                date=ThaiHolidayCalculator._get_chinese_new_year(year),
                type=ExceptionType.LOCAL_EVENT,
                is_national=False,
                description_th="วันหยุดตรุษจีน (สำหรับธุรกิจจีนไทย)"
            ),
            
            # Makha Bucha (variable Buddhist holiday)
            ThaiHoliday(
                name_th="วันมาฆบูชา", 
                name_de="Makha Bucha Tag",
                name_en="Makha Bucha Day",
                date=ThaiHolidayCalculator._get_makha_bucha(year),
                type=ExceptionType.BUDDHIST_HOLIDAY,
                description_th="วันสำคัญทางพุทธศาสนา"
            ),
            
            # Chakri Day
            ThaiHoliday(
                name_th="วันจักรี",
                name_de="Chakri-Dynastie Tag",
                name_en="Chakri Day",
                date=date(year, 4, 6),
                type=ExceptionType.ROYAL_HOLIDAY,
                description_th="วันคล้ายวันสถาปนาราชวงศ์จักรี"
            ),
            
            # Songkran (Thai New Year)
            ThaiHoliday(
                name_th="วันสงกรานต์",
                name_de="Songkran (Thailändisches Neujahr)",
                name_en="Songkran (Thai New Year)",
                date=date(year, 4, 13),
                type=ExceptionType.NATIONAL_HOLIDAY,
                description_th="วันขึ้นปีใหม่ไทย - เทศกาลสงกรานต์"
            ),
            
            # Labour Day
            ThaiHoliday(
                name_th="วันแรงงาน",
                name_de="Tag der Arbeit", 
                name_en="Labour Day",
                date=date(year, 5, 1),
                type=ExceptionType.NATIONAL_HOLIDAY,
                description_th="วันแรงงานแห่งชาติ"
            ),
            
            # Coronation Day
            ThaiHoliday(
                name_th="วันฉัตรมงคล",
                name_de="Krönungstag",
                name_en="Coronation Day", 
                date=date(year, 5, 4),
                type=ExceptionType.ROYAL_HOLIDAY,
                description_th="วันพระราชพิธีบรมราชาภิเษก"
            ),
            
            # Visakha Bucha (variable)
            ThaiHoliday(
                name_th="วันวิสาขบูชา",
                name_de="Vesak Tag",
                name_en="Visakha Bucha Day",
                date=ThaiHolidayCalculator._get_visakha_bucha(year),
                type=ExceptionType.BUDDHIST_HOLIDAY,
                description_th="วันสำคัญทางพุทธศาสนา"
            ),
            
            # HM Queen's Birthday
            ThaiHoliday(
                name_th="วันเฉลิมพระชนมพรรษาพระราชินี",
                name_de="Geburtstag der Königin",
                name_en="HM Queen's Birthday",
                date=date(year, 6, 3),
                type=ExceptionType.ROYAL_HOLIDAY,
                description_th="วันเฉลิมพระชนมพรรษาสมเด็จพระนางเจ้าฯ พระบรมราชินี"
            ),
            
            # Asanha Bucha (variable)
            ThaiHoliday(
                name_th="วันอาสาฬหบูชา",
                name_de="Asalha Puja Tag",
                name_en="Asanha Bucha Day",
                date=ThaiHolidayCalculator._get_asanha_bucha(year),
                type=ExceptionType.BUDDHIST_HOLIDAY,
                description_th="วันสำคัญทางพุทธศาสนา"
            ),
            
            # Khao Phansa (variable - day after Asanha Bucha)
            ThaiHoliday(
                name_th="วันเข้าพรรษา", 
                name_de="Beginn der Regenzeit-Fastenzeit",
                name_en="Khao Phansa Day",
                date=ThaiHolidayCalculator._get_asanha_bucha(year) + timedelta(days=1),
                type=ExceptionType.BUDDHIST_HOLIDAY,
                description_th="วันเข้าพรรษา"
            ),
            
            # HM King's Birthday
            ThaiHoliday(
                name_th="วันเฉลิมพระชนมพรรษาพระบาทสมเด็จพระเจ้าอยู่หัว",
                name_de="Geburtstag des Königs",
                name_en="HM King's Birthday",
                date=date(year, 7, 28),
                type=ExceptionType.ROYAL_HOLIDAY,
                description_th="วันเฉลิมพระชนมพรรษาพระบาทสมเด็จพระเจ้าอยู่หัว"
            ),
            
            # HM Queen Mother's Birthday
            ThaiHoliday(
                name_th="วันแม่แห่งชาติ",
                name_de="Muttertag",
                name_en="Mother's Day",
                date=date(year, 8, 12),
                type=ExceptionType.ROYAL_HOLIDAY,
                description_th="วันเฉลิมพระชนมพรรษาสมเด็จย่า"
            ),
            
            # HM King Bhumibol's Memorial Day
            ThaiHoliday(
                name_th="วันคล้ายวันสวรรคตพระบาทสมเด็จพระปรมินทรมหาภูมิพลอดุลยเดช",
                name_de="Gedenktag König Bhumibol",
                name_en="HM King Bhumibol Memorial Day",
                date=date(year, 10, 13),
                type=ExceptionType.ROYAL_HOLIDAY,
                description_th="วันคล้ายวันสวรรคตพระบาทสมเด็จพระบรมชนกาธิเบศร"
            ),
            
            # Chulalongkorn Day
            ThaiHoliday(
                name_th="วันปิยมหาราช",
                name_de="Chulalongkorn Tag", 
                name_en="Chulalongkorn Day",
                date=date(year, 10, 23),
                type=ExceptionType.ROYAL_HOLIDAY,
                description_th="วันคล้ายวันสวรรคตพระบาทสมเด็จพระจุลจอมเกล้าเจ้าอยู่หัว"
            ),
            
            # HM King Bhumibol's Birthday
            ThaiHoliday(
                name_th="วันคล้ายวันเฉลิมพระชนมพรรษาพระบาทสมเด็จพระปรมินทรมหาภูมิพลอดุลยเดช และวันพ่อแห่งชาติ",
                name_de="Vatertag / König Bhumibol Geburtstag",
                name_en="Father's Day / HM King Bhumibol's Birthday",
                date=date(year, 12, 5),
                type=ExceptionType.ROYAL_HOLIDAY,
                description_th="วันพ่อแห่งชาติ"
            ),
            
            # Constitution Day
            ThaiHoliday(
                name_th="วันรัฐธรรมนูญ",
                name_de="Verfassungstag",
                name_en="Constitution Day", 
                date=date(year, 12, 10),
                type=ExceptionType.NATIONAL_HOLIDAY,
                description_th="วันรัฐธรรมนูญแห่งราชอาณาจักรไทย"
            ),
            
            # New Year's Eve
            ThaiHoliday(
                name_th="วันสิ้นปี",
                name_de="Silvester",
                name_en="New Year's Eve",
                date=date(year, 12, 31),
                type=ExceptionType.NATIONAL_HOLIDAY,
                description_th="วันสิ้นปี"
            )
        ]
    
    @staticmethod
    def _get_chinese_new_year(year: int) -> date:
        """Approximation für chinesisches Neujahr (vereinfacht)"""
        # Vereinfachte Berechnung - in der Praxis würde man einen Kalenderservice verwenden
        base_dates = {
            2024: date(2024, 2, 10),
            2025: date(2025, 1, 29),
            2026: date(2026, 2, 17),
            2027: date(2027, 2, 6),
            2028: date(2028, 1, 26)
        }
        return base_dates.get(year, date(year, 2, 1))  # Fallback
    
    @staticmethod
    def _get_makha_bucha(year: int) -> date:
        """Approximation für Makha Bucha (vereinfacht)"""
        base_dates = {
            2024: date(2024, 2, 24),
            2025: date(2025, 2, 12),
            2026: date(2026, 3, 4),
            2027: date(2027, 2, 21),
            2028: date(2028, 2, 11)
        }
        return base_dates.get(year, date(year, 2, 15))  # Fallback
    
    @staticmethod
    def _get_visakha_bucha(year: int) -> date:
        """Approximation für Visakha Bucha (vereinfacht)"""
        base_dates = {
            2024: date(2024, 5, 22),
            2025: date(2025, 5, 12),
            2026: date(2026, 5, 31),
            2027: date(2027, 5, 20),
            2028: date(2028, 5, 9)
        }
        return base_dates.get(year, date(year, 5, 15))  # Fallback
    
    @staticmethod
    def _get_asanha_bucha(year: int) -> date:
        """Approximation für Asanha Bucha (vereinfacht)"""
        base_dates = {
            2024: date(2024, 7, 21),
            2025: date(2025, 7, 11),
            2026: date(2026, 7, 30),
            2027: date(2027, 7, 19),
            2028: date(2028, 7, 8)
        }
        return base_dates.get(year, date(year, 7, 15))  # Fallback


class ExceptionEngine:
    """
    Hauptklasse für die Verwaltung von Ausnahmen und Sondertagen
    Integriert thailändische Feiertage mit lokalen Ausnahmen
    """
    
    BANGKOK_TZ = pytz.timezone('Asia/Bangkok')
    
    @staticmethod
    def is_thai_holiday(check_date: date) -> Optional[ThaiHoliday]:
        """Prüfe ob Datum ein thailändischer Feiertag ist"""
        year = check_date.year
        holidays = ThaiHolidayCalculator.get_fixed_holidays(year)
        
        for holiday in holidays:
            if holiday.date == check_date and holiday.affects_business:
                return holiday
        
        return None
    
    @staticmethod
    def get_exception_for_date(check_date: date) -> Optional[HourException]:
        """Hole explizite Ausnahme für Datum"""
        with Session(engine) as session:
            return session.exec(
                select(HourException).where(HourException.exception_date == check_date)
            ).first()
    
    @staticmethod
    def get_effective_exception_for_date(check_date: date) -> Dict:
        """
        Hole effektive Ausnahme für Datum
        Berücksichtigt sowohl explizite Ausnahmen als auch thailändische Feiertage
        """
        # Prüfe explizite Ausnahme zuerst
        explicit_exception = ExceptionEngine.get_exception_for_date(check_date)
        if explicit_exception:
            return {
                'date': check_date,
                'closed': explicit_exception.closed,
                'time_ranges': explicit_exception.time_ranges or [],
                'note': explicit_exception.note,
                'exception_type': 'explicit',
                'source': 'database'
            }
        
        # Prüfe thailändische Feiertage
        thai_holiday = ExceptionEngine.is_thai_holiday(check_date)
        if thai_holiday:
            return {
                'date': check_date,
                'closed': True,  # Feiertage standardmäßig geschlossen
                'time_ranges': [],
                'note': thai_holiday.get_name('th'),
                'exception_type': thai_holiday.type.value,
                'source': 'thai_holiday',
                'holiday_info': {
                    'name_th': thai_holiday.name_th,
                    'name_de': thai_holiday.name_de,
                    'name_en': thai_holiday.name_en,
                    'description_th': thai_holiday.description_th,
                    'description_de': thai_holiday.description_de,
                    'description_en': thai_holiday.description_en,
                    'is_national': thai_holiday.is_national,
                    'type': thai_holiday.type.value
                }
            }
        
        # Keine Ausnahme gefunden
        return None
    
    @staticmethod
    def create_thai_holiday_exceptions(year: int, overwrite_existing: bool = False) -> int:
        """
        Erstelle Ausnahmen für thailändische Feiertage
        
        Args:
            year: Jahr für das Feiertage erstellt werden sollen
            overwrite_existing: Überschreibe existierende Einträge
            
        Returns:
            Anzahl erstellte Ausnahmen
        """
        holidays = ThaiHolidayCalculator.get_fixed_holidays(year)
        created_count = 0
        
        with Session(engine) as session:
            for holiday in holidays:
                if not holiday.affects_business:
                    continue
                
                # Prüfe ob bereits vorhanden
                existing = session.exec(
                    select(HourException).where(HourException.exception_date == holiday.date)
                ).first()
                
                if existing and not overwrite_existing:
                    continue
                
                if existing and overwrite_existing:
                    # Update existing
                    existing.closed = True
                    existing.time_ranges = []
                    existing.note = holiday.get_name('th')
                    existing.updated_at = datetime.now()
                else:
                    # Create new
                    exception = HourException(
                        exception_date=holiday.date,
                        closed=True,
                        time_ranges=[],
                        note=holiday.get_name('th')
                    )
                    session.add(exception)
                
                created_count += 1
            
            session.commit()
        
        logger.info(f"Created/updated {created_count} Thai holiday exceptions for year {year}")
        return created_count
    
    @staticmethod 
    def get_upcoming_exceptions(days_ahead: int = 30) -> List[Dict]:
        """Hole kommende Ausnahmen für die nächsten N Tage"""
        now = datetime.now(ExceptionEngine.BANGKOK_TZ)
        current_date = now.date()
        end_date = current_date + timedelta(days=days_ahead)
        
        exceptions = []
        check_date = current_date
        
        while check_date <= end_date:
            exception = ExceptionEngine.get_effective_exception_for_date(check_date)
            if exception:
                exceptions.append(exception)
            check_date += timedelta(days=1)
        
        return exceptions
    
    @staticmethod
    def get_exception_summary(start_date: date, end_date: date, lang: str = 'th') -> Dict:
        """
        Zusammenfassung aller Ausnahmen in einem Zeitraum
        Optimiert für Admin-Interface und Übersichten
        """
        exceptions = []
        thai_holidays = []
        explicit_exceptions = []
        
        current_date = start_date
        while current_date <= end_date:
            exception = ExceptionEngine.get_effective_exception_for_date(current_date)
            
            if exception:
                exceptions.append(exception)
                
                if exception['source'] == 'thai_holiday':
                    thai_holidays.append(exception)
                else:
                    explicit_exceptions.append(exception)
            
            current_date += timedelta(days=1)
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days_total': (end_date - start_date).days + 1
            },
            'summary': {
                'total_exceptions': len(exceptions),
                'thai_holidays': len(thai_holidays),
                'explicit_exceptions': len(explicit_exceptions),
                'closed_days': len([e for e in exceptions if e['closed']]),
                'special_hours_days': len([e for e in exceptions if not e['closed'] and e['time_ranges']])
            },
            'exceptions': exceptions,
            'thai_holidays': thai_holidays,
            'explicit_exceptions': explicit_exceptions
        }
    
    @staticmethod
    def validate_exception_data(
        exception_date: date,
        closed: bool,
        time_ranges: Optional[List[str]],
        note: Optional[str]
    ) -> List[str]:
        """Validiere Ausnahmen-Daten"""
        errors = []
        
        # Datum-Validierung
        if exception_date < date.today():
            errors.append("Ausnahmedatum kann nicht in der Vergangenheit liegen")
        
        # Zeitfenster-Validierung
        if not closed and not time_ranges:
            errors.append("Wenn nicht geschlossen, müssen Zeitfenster angegeben werden")
        
        if closed and time_ranges:
            errors.append("Geschlossene Tage können keine Zeitfenster haben")
        
        if time_ranges:
            for time_range in time_ranges:
                if '-' not in time_range:
                    errors.append(f"Ungültiges Zeitformat: {time_range}")
                    continue
                
                try:
                    start_str, end_str = time_range.split('-')
                    datetime.strptime(start_str.strip(), '%H:%M')
                    datetime.strptime(end_str.strip(), '%H:%M')
                except ValueError:
                    errors.append(f"Ungültiges Zeitformat: {time_range}")
        
        # Notiz-Validierung
        if note and len(note.strip()) > 200:
            errors.append("Notiz zu lang (max. 200 Zeichen)")
        
        return errors


# Template-Helper Funktionen

def is_thai_holiday_today() -> bool:
    """Template-Funktion: Ist heute ein thailändischer Feiertag?"""
    today = datetime.now(ExceptionEngine.BANGKOK_TZ).date()
    return ExceptionEngine.is_thai_holiday(today) is not None

def get_next_thai_holiday(lang: str = 'th') -> Optional[Dict]:
    """Template-Funktion: Nächster thailändischer Feiertag"""
    today = datetime.now(ExceptionEngine.BANGKOK_TZ).date()
    
    # Prüfe nächste 365 Tage
    for i in range(365):
        check_date = today + timedelta(days=i)
        holiday = ExceptionEngine.is_thai_holiday(check_date)
        
        if holiday:
            return {
                'date': check_date.isoformat(),
                'name': holiday.get_name(lang),
                'description': holiday.get_description(lang),
                'days_until': i,
                'type': holiday.type.value
            }
    
    return None

def get_thai_holidays_this_month(lang: str = 'th') -> List[Dict]:
    """Template-Funktion: Thailändische Feiertage diesen Monat"""
    now = datetime.now(ExceptionEngine.BANGKOK_TZ)
    year = now.year
    month = now.month
    
    # Ersten und letzten Tag des Monats
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    holidays = ThaiHolidayCalculator.get_fixed_holidays(year)
    this_month_holidays = []
    
    for holiday in holidays:
        if first_day <= holiday.date <= last_day and holiday.affects_business:
            this_month_holidays.append({
                'date': holiday.date.isoformat(),
                'name': holiday.get_name(lang),
                'description': holiday.get_description(lang),
                'type': holiday.type.value
            })
    
    return this_month_holidays