"""
Next Opening Calculator Service - Intelligente "Nächster Öffnungstermin"-Logic
Thai-First Implementation für das QR-Info-Portal

This service provides comprehensive logic for calculating the next opening time,
considering status, exceptions, holidays, and special closures.
Bangkok timezone (Asia/Bangkok) is used throughout.
"""

from datetime import date, datetime, time, timedelta
from typing import Optional, Dict, List, Tuple
from sqlmodel import Session, select
import pytz
import logging
from dataclasses import dataclass
from enum import Enum

from app.models import Status, StatusType, StandardHours, HourException
from app.database import engine
from app.services.status import StatusService
from app.services.schedule import ScheduleService

logger = logging.getLogger(__name__)


class ClosureReason(Enum):
    """Gründe für Schließungen - mehrsprachig"""
    ABSENT = "ABSENT"
    VACATION = "VACATION" 
    EDUCATION = "EDUCATION"
    CONGRESS = "CONGRESS"
    OTHER = "OTHER"
    EXCEPTION = "EXCEPTION"  # Sonderfall/Feiertag
    WEEKEND = "WEEKEND"
    NOT_OPEN_YET = "NOT_OPEN_YET"  # Heute noch nicht geöffnet


@dataclass
class NextOpening:
    """Nächster Öffnungstermin mit Details"""
    date: date
    time: str  # "08:30" Format
    datetime_bangkok: datetime
    days_until: int
    time_slots: List[str]  # Alle verfügbaren Zeitfenster
    closure_reason: Optional[ClosureReason] = None
    closure_note: Optional[str] = None
    is_today: bool = False
    is_tomorrow: bool = False
    is_weekend: bool = False
    
    def to_dict(self) -> Dict:
        """Konvertierung für Template-Nutzung"""
        return {
            'date': self.date,
            'time': self.time,
            'datetime_bangkok': self.datetime_bangkok,
            'days_until': self.days_until,
            'time_slots': self.time_slots,
            'closure_reason': self.closure_reason.value if self.closure_reason else None,
            'closure_note': self.closure_note,
            'is_today': self.is_today,
            'is_tomorrow': self.is_tomorrow,
            'is_weekend': self.is_weekend
        }


@dataclass
class TodayStatus:
    """Heutiger Status mit verbleibenden Slots"""
    is_open_now: bool
    remaining_slots: List[str]
    next_slot_time: Optional[str]
    closes_at: Optional[str]
    closure_reason: Optional[ClosureReason]
    closure_note: Optional[str]
    minutes_until_next: Optional[int]
    
    def to_dict(self) -> Dict:
        return {
            'is_open_now': self.is_open_now,
            'remaining_slots': self.remaining_slots,
            'next_slot_time': self.next_slot_time,
            'closes_at': self.closes_at,
            'closure_reason': self.closure_reason.value if self.closure_reason else None,
            'closure_note': self.closure_note,
            'minutes_until_next': self.minutes_until_next
        }


class NextOpeningCalculator:
    """
    Hauptklasse für die Berechnung der nächsten Öffnungszeiten
    Berücksichtigt Status, Ausnahmen, Feiertage und Sonderschließungen
    """
    
    BANGKOK_TZ = pytz.timezone('Asia/Bangkok')
    MAX_LOOKAHEAD_DAYS = 14  # Maximaler Vorlauf für Suche
    
    # Cache für Performance (15 Minuten)
    _cache = {}
    _cache_timeout = timedelta(minutes=15)
    _last_cache_clear = datetime.now()
    
    @classmethod
    def _clear_expired_cache(cls):
        """Lösche abgelaufene Cache-Einträge"""
        now = datetime.now()
        if now - cls._last_cache_clear > cls._cache_timeout:
            cls._cache.clear()
            cls._last_cache_clear = now
    
    @classmethod
    def get_current_bangkok_time(cls) -> datetime:
        """Aktuelle Zeit in Bangkok Timezone"""
        return datetime.now(cls.BANGKOK_TZ)
    
    @classmethod
    def get_today_status(cls) -> TodayStatus:
        """
        Detaillierter Status für heute mit verbleibenden Slots
        """
        cls._clear_expired_cache()
        cache_key = f"today_status_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        now = cls.get_current_bangkok_time()
        today = now.date()
        current_time = now.time()
        
        # Prüfe aktuellen Status (Abwesenheit)
        status = StatusService.get_current_status()
        if status and status.type != StatusType.ANWESEND:
            closure_reason, closure_note = cls._get_closure_reason_and_note(status)
            result = TodayStatus(
                is_open_now=False,
                remaining_slots=[],
                next_slot_time=None,
                closes_at=None,
                closure_reason=closure_reason,
                closure_note=closure_note,
                minutes_until_next=None
            )
            cls._cache[cache_key] = result
            return result
        
        # Hole heutige Öffnungszeiten
        hours = ScheduleService.get_hours_for_date(today)
        
        if hours['closed']:
            closure_reason = ClosureReason.WEEKEND if today.weekday() >= 5 else ClosureReason.EXCEPTION
            result = TodayStatus(
                is_open_now=False,
                remaining_slots=[],
                next_slot_time=None,
                closes_at=None,
                closure_reason=closure_reason,
                closure_note=hours.get('note'),
                minutes_until_next=None
            )
            cls._cache[cache_key] = result
            return result
        
        # Analysiere Zeitfenster
        remaining_slots = []
        next_slot_time = None
        closes_at = None
        is_open_now = False
        minutes_until_next = None
        
        for time_range in hours['time_ranges']:
            start_str, end_str = time_range.split('-')
            start_time = datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.strptime(end_str, '%H:%M').time()
            
            # Prüfe ob aktuell geöffnet
            if start_time <= current_time <= end_time:
                is_open_now = True
                closes_at = end_str
            
            # Sammle zukünftige Slots
            if current_time < start_time:
                remaining_slots.append(time_range)
                if not next_slot_time:
                    next_slot_time = start_str
                    # Berechne Minuten bis nächster Öffnung
                    next_datetime = cls.BANGKOK_TZ.localize(
                        datetime.combine(today, start_time)
                    )
                    minutes_until_next = int((next_datetime - now).total_seconds() / 60)
            elif current_time < end_time:
                # Aktuell geöffnet, zeige verbleibendes Zeitfenster
                remaining_slots.append(f"{current_time.strftime('%H:%M')}-{end_str}")
        
        result = TodayStatus(
            is_open_now=is_open_now,
            remaining_slots=remaining_slots,
            next_slot_time=next_slot_time,
            closes_at=closes_at,
            closure_reason=ClosureReason.NOT_OPEN_YET if not is_open_now and remaining_slots else None,
            closure_note=None,
            minutes_until_next=minutes_until_next
        )
        
        cls._cache[cache_key] = result
        return result
    
    @classmethod
    def get_next_opening(cls, exclude_today: bool = False) -> Optional[NextOpening]:
        """
        Berechne nächsten Öffnungstermin mit intelligenter Lookahead-Logic
        
        Args:
            exclude_today: Wenn True, ignoriere heutige verbleibende Slots
        """
        cls._clear_expired_cache()
        cache_key = f"next_opening_{exclude_today}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        now = cls.get_current_bangkok_time()
        current_date = now.date()
        
        # Prüfe zuerst heutige verbleibende Slots (außer exclude_today=True)
        if not exclude_today:
            today_status = cls.get_today_status()
            if today_status.next_slot_time:
                result = NextOpening(
                    date=current_date,
                    time=today_status.next_slot_time,
                    datetime_bangkok=cls.BANGKOK_TZ.localize(
                        datetime.combine(current_date, datetime.strptime(today_status.next_slot_time, '%H:%M').time())
                    ),
                    days_until=0,
                    time_slots=today_status.remaining_slots,
                    is_today=True,
                    is_tomorrow=False,
                    is_weekend=False
                )
                cls._cache[cache_key] = result
                return result
        
        # Suche in zukünftigen Tagen
        for i in range(1, cls.MAX_LOOKAHEAD_DAYS + 1):
            check_date = current_date + timedelta(days=i)
            
            # Prüfe Status-Abwesenheiten
            if cls._is_absent_on_date(check_date):
                continue
            
            # Hole Öffnungszeiten für diesen Tag
            hours = ScheduleService.get_hours_for_date(check_date)
            
            if not hours['closed'] and hours['time_ranges']:
                first_slot = hours['time_ranges'][0]
                first_time = first_slot.split('-')[0]
                
                result = NextOpening(
                    date=check_date,
                    time=first_time,
                    datetime_bangkok=cls.BANGKOK_TZ.localize(
                        datetime.combine(check_date, datetime.strptime(first_time, '%H:%M').time())
                    ),
                    days_until=i,
                    time_slots=hours['time_ranges'],
                    is_today=False,
                    is_tomorrow=(i == 1),
                    is_weekend=(check_date.weekday() >= 5),
                    closure_note=hours.get('note')
                )
                cls._cache[cache_key] = result
                return result
        
        # Kein Öffnungstermin in den nächsten 14 Tagen gefunden
        return None
    
    @classmethod
    def get_closure_explanation(cls, lang: str = 'th') -> Dict:
        """
        Mehrsprachige Erklärung warum geschlossen ist
        
        Args:
            lang: Sprache (th, de, en)
        """
        now = cls.get_current_bangkok_time()
        status = StatusService.get_current_status()
        today_hours = ScheduleService.get_hours_for_date(now.date())
        next_opening = cls.get_next_opening()
        
        messages = {
            'th': {
                ClosureReason.ABSENT: 'ไม่อยู่ในสถานที่',
                ClosureReason.VACATION: 'ลาพักร้อน',
                ClosureReason.EDUCATION: 'อบรมเพิ่มพูนความรู้',
                ClosureReason.CONGRESS: 'เข้าร่วมประชุมวิชาการ',
                ClosureReason.OTHER: 'ไม่สามารถให้บริการได้',
                ClosureReason.EXCEPTION: 'วันหยุดพิเศษ',
                ClosureReason.WEEKEND: 'วันหยุดสุดสาปดาห์',
                ClosureReason.NOT_OPEN_YET: 'ยังไม่เปิดให้บริการในวันนี้'
            },
            'de': {
                ClosureReason.ABSENT: 'Nicht anwesend',
                ClosureReason.VACATION: 'Urlaub',
                ClosureReason.EDUCATION: 'Fortbildung',
                ClosureReason.CONGRESS: 'Kongress',
                ClosureReason.OTHER: 'Sonstige Gründe',
                ClosureReason.EXCEPTION: 'Sonderöffnungszeiten',
                ClosureReason.WEEKEND: 'Wochenende',
                ClosureReason.NOT_OPEN_YET: 'Heute noch nicht geöffnet'
            },
            'en': {
                ClosureReason.ABSENT: 'Not present',
                ClosureReason.VACATION: 'Vacation',
                ClosureReason.EDUCATION: 'Continuing education',
                ClosureReason.CONGRESS: 'Conference',
                ClosureReason.OTHER: 'Other reasons',
                ClosureReason.EXCEPTION: 'Special hours',
                ClosureReason.WEEKEND: 'Weekend',
                ClosureReason.NOT_OPEN_YET: 'Not open yet today'
            }
        }
        
        # Bestimme Grund der Schließung
        closure_reason = None
        closure_note = None
        
        if status and status.type != StatusType.ANWESEND:
            closure_reason, closure_note = cls._get_closure_reason_and_note(status)
        elif today_hours['closed']:
            if today_hours.get('note'):
                closure_reason = ClosureReason.EXCEPTION
                closure_note = today_hours['note']
            else:
                closure_reason = ClosureReason.WEEKEND if now.date().weekday() >= 5 else ClosureReason.EXCEPTION
        else:
            closure_reason = ClosureReason.NOT_OPEN_YET
        
        result = {
            'reason': closure_reason.value if closure_reason else None,
            'message': messages.get(lang, messages['th']).get(closure_reason, '') if closure_reason else '',
            'note': closure_note,
            'next_opening': next_opening.to_dict() if next_opening else None,
            'current_time': now.strftime('%H:%M'),
            'current_date': now.date().isoformat()
        }
        
        return result
    
    @classmethod
    def _is_absent_on_date(cls, check_date: date) -> bool:
        """Prüfe ob an einem bestimmten Datum abwesend"""
        status = StatusService.get_current_status()
        
        if not status or status.type == StatusType.ANWESEND:
            return False
        
        if not status.date_from or not status.date_to:
            return False
        
        return status.date_from <= check_date <= status.date_to
    
    @classmethod
    def _get_closure_reason_and_note(cls, status: Status) -> Tuple[ClosureReason, Optional[str]]:
        """Mappe Status-Typ zu ClosureReason"""
        mapping = {
            StatusType.ANWESEND: None,
            StatusType.URLAUB: ClosureReason.VACATION,
            StatusType.BILDUNGSURLAUB: ClosureReason.EDUCATION,
            StatusType.KONGRESS: ClosureReason.CONGRESS,
            StatusType.SONSTIGES: ClosureReason.OTHER
        }
        
        reason = mapping.get(status.type, ClosureReason.ABSENT)
        note = status.description
        
        # Erweitere Note mit Zeitraum falls verfügbar
        if status.date_from and status.date_to and reason != ClosureReason.ABSENT:
            period_note = f"{status.date_from.strftime('%d.%m.')} - {status.date_to.strftime('%d.%m.%Y')}"
            note = f"{note} ({period_note})" if note else period_note
        
        return reason, note
    
    @classmethod
    def get_extended_forecast(cls, days: int = 7) -> List[Dict]:
        """
        Erweiterte Vorhersage für die nächsten N Tage
        Für Kiosk-Anzeigen und Wochenübersicht
        """
        now = cls.get_current_bangkok_time()
        current_date = now.date()
        forecast = []
        
        for i in range(days):
            check_date = current_date + timedelta(days=i)
            hours = ScheduleService.get_hours_for_date(check_date)
            
            day_info = {
                'date': check_date,
                'day_name': check_date.strftime('%A'),
                'is_today': (i == 0),
                'is_tomorrow': (i == 1),
                'is_weekend': check_date.weekday() >= 5,
                'hours': hours,
                'is_absent': cls._is_absent_on_date(check_date),
                'available': not hours['closed'] and not cls._is_absent_on_date(check_date)
            }
            
            # Für heute: spezielle Behandlung
            if i == 0:
                today_status = cls.get_today_status()
                day_info.update({
                    'today_status': today_status.to_dict(),
                    'remaining_slots': today_status.remaining_slots,
                    'is_open_now': today_status.is_open_now
                })
            
            forecast.append(day_info)
        
        return forecast
    
    @classmethod
    def get_smart_status_message(cls, lang: str = 'th') -> Dict:
        """
        Intelligente Status-Nachricht basierend auf aktueller Situation
        Für Homepage und Kiosk-Display
        """
        now = cls.get_current_bangkok_time()
        today_status = cls.get_today_status()
        next_opening = cls.get_next_opening()
        
        templates = {
            'th': {
                'open_now': 'เปิดให้บริการอยู่ - ปิดเวลา {closes_at}',
                'open_soon': 'เปิดในอีก {minutes} นาที ({next_time})',
                'closed_today': 'ปิดทำการวันนี้',
                'closed_with_reason': 'ปิดทำการ: {reason}',
                'next_opening': 'เปิดครั้งต่อไป: {date} เวลา {time}',
                'no_opening_soon': 'ไม่มีกำหนดเปิดใน 2 สัปดาห์ข้างหน้า'
            },
            'de': {
                'open_now': 'Geöffnet - Schließt um {closes_at}',
                'open_soon': 'Öffnet in {minutes} Minuten ({next_time})',
                'closed_today': 'Heute geschlossen',
                'closed_with_reason': 'Geschlossen: {reason}',
                'next_opening': 'Nächste Öffnung: {date} um {time}',
                'no_opening_soon': 'Keine Öffnung in den nächsten 2 Wochen geplant'
            },
            'en': {
                'open_now': 'Open now - Closes at {closes_at}',
                'open_soon': 'Opens in {minutes} minutes ({next_time})',
                'closed_today': 'Closed today',
                'closed_with_reason': 'Closed: {reason}',
                'next_opening': 'Next opening: {date} at {time}',
                'no_opening_soon': 'No opening scheduled in the next 2 weeks'
            }
        }
        
        t = templates.get(lang, templates['th'])
        
        if today_status.is_open_now:
            message = t['open_now'].format(closes_at=today_status.closes_at)
            status_type = 'open'
        elif today_status.next_slot_time and today_status.minutes_until_next and today_status.minutes_until_next <= 120:
            message = t['open_soon'].format(
                minutes=today_status.minutes_until_next,
                next_time=today_status.next_slot_time
            )
            status_type = 'opening_soon'
        elif today_status.closure_reason:
            closure_explanation = cls.get_closure_explanation(lang)
            message = t['closed_with_reason'].format(reason=closure_explanation['message'])
            if closure_explanation['note']:
                message += f" ({closure_explanation['note']})"
            status_type = 'closed_with_reason'
        else:
            message = t['closed_today']
            status_type = 'closed'
        
        # Nächste Öffnung hinzufügen
        next_info = None
        if next_opening:
            next_date_str = next_opening.date.strftime('%d.%m.')
            if next_opening.is_tomorrow:
                next_date_str = 'พรุ่งนี้' if lang == 'th' else ('Morgen' if lang == 'de' else 'Tomorrow')
            elif next_opening.is_today:
                next_date_str = 'วันนี้' if lang == 'th' else ('Heute' if lang == 'de' else 'Today')
            
            next_info = t['next_opening'].format(
                date=next_date_str,
                time=next_opening.time
            )
        else:
            next_info = t['no_opening_soon']
        
        return {
            'main_message': message,
            'status_type': status_type,
            'next_opening_message': next_info,
            'is_open': today_status.is_open_now,
            'opens_soon': today_status.minutes_until_next is not None and today_status.minutes_until_next <= 60,
            'today_status': today_status.to_dict(),
            'next_opening': next_opening.to_dict() if next_opening else None,
            'current_time': now.strftime('%H:%M'),
            'current_date': now.date().isoformat()
        }


# Convenience Functions für Template-Nutzung

def get_smart_status(lang: str = 'th') -> Dict:
    """Template-Funktion: Hole intelligenten Status"""
    return NextOpeningCalculator.get_smart_status_message(lang)

def get_today_remaining_slots() -> List[str]:
    """Template-Funktion: Verbleibende Slots heute"""
    return NextOpeningCalculator.get_today_status().remaining_slots

def get_next_opening_info(lang: str = 'th') -> Optional[Dict]:
    """Template-Funktion: Nächste Öffnungsinfo"""
    next_opening = NextOpeningCalculator.get_next_opening()
    if next_opening:
        return next_opening.to_dict()
    return None

def is_open_now() -> bool:
    """Template-Funktion: Aktuell geöffnet?"""
    return NextOpeningCalculator.get_today_status().is_open_now

def get_closure_reason(lang: str = 'th') -> str:
    """Template-Funktion: Grund der Schließung"""
    explanation = NextOpeningCalculator.get_closure_explanation(lang)
    return explanation.get('message', '')

def minutes_until_next_opening() -> Optional[int]:
    """Template-Funktion: Minuten bis nächste Öffnung"""
    return NextOpeningCalculator.get_today_status().minutes_until_next