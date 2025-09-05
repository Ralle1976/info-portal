"""
Kiosk Rotation Service - Thailand Edition
========================================
Verwaltet die 4-teilige Rotation für das Kiosk-System:
1. NOW - Aktueller Status mit Uhr
2. TODAY - Heutige Öffnungszeiten  
3. WEEK - Wochenübersicht
4. SERVICES - Verfügbare Dienste

Features:
- Bangkok Timezone Support
- Thai-First Display Logic
- Next Opening Calculation
- Monitor Optimization
- Offline Fallback
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pytz
from app.services.status import StatusService
from app.services.schedule import ScheduleService
from app.models import StatusType


class KioskRotationService:
    """Service für die Kiosk-Rotation mit Thailand-spezifischen Features"""
    
    def __init__(self, status_service: StatusService, schedule_service: ScheduleService):
        self.status_service = status_service
        self.schedule_service = schedule_service
        self.bangkok_tz = pytz.timezone('Asia/Bangkok')
        
        # Thai day names mapping
        self.thai_days = {
            'monday': 'วันจันทร์',
            'tuesday': 'วันอังคาร', 
            'wednesday': 'วันพุธ',
            'thursday': 'วันพฤหัสบดี',
            'friday': 'วันศุกร์',
            'saturday': 'วันเสาร์',
            'sunday': 'วันอาทิตย์'
        }
        
        # Thai service descriptions
        self.thai_services = {
            'blood_test': {
                'thai': 'เจาะเลือด',
                'english': 'Blood Test',
                'description_thai': 'เจาะเลือดเพื่อตรวจวิเคราะห์สารต่างๆ ในร่างกาย',
                'description_english': 'Blood collection for various health analyses',
                'icon': 'fas fa-vial',
                'color': '#DC2626'
            },
            'health_checkup': {
                'thai': 'ตรวจสุขภาพ',
                'english': 'Health Checkup', 
                'description_thai': 'ตรวจสุขภาพประจำปีและการตรวจคัดกรอง',
                'description_english': 'Annual health checkups and screening',
                'icon': 'fas fa-stethoscope',
                'color': '#059669'
            },
            'consultation': {
                'thai': 'ปรึกษาแพทย์',
                'english': 'Medical Consultation',
                'description_thai': 'ปรึกษาเรื่องสุขภาพกับแพทย์เชี่ยวชาญ',
                'description_english': 'Consult with medical professionals',
                'icon': 'fas fa-user-md',
                'color': '#0056B3'
            },
            'follow_up': {
                'thai': 'ติดตามผล',
                'english': 'Follow-up',
                'description_thai': 'ติดตามผลการรักษาและตรวจสอบความคืบหน้า',
                'description_english': 'Treatment follow-up and progress monitoring',
                'icon': 'fas fa-clipboard-check',
                'color': '#7C2D12'
            }
        }
    
    def get_bangkok_time(self) -> datetime:
        """Get current time in Bangkok timezone"""
        utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        return utc_now.astimezone(self.bangkok_tz)
    
    def get_rotation_data(self) -> Dict:
        """
        Bereitet alle Daten für die Kiosk-Rotation vor
        Returns: Dictionary mit allen Slide-Daten
        """
        now = self.get_bangkok_time()
        
        return {
            'current_time': now,
            'slides': {
                'now': self._get_now_slide_data(now),
                'today': self._get_today_slide_data(now), 
                'week': self._get_week_slide_data(now),
                'services': self._get_services_slide_data()
            },
            'meta': {
                'rotation_interval': 8000,  # 8 seconds
                'slides_count': 4,
                'timezone': 'Asia/Bangkok',
                'last_update': now.isoformat(),
                'language': 'th-first'  # Thai primary, English secondary
            }
        }
    
    def _get_now_slide_data(self, now: datetime) -> Dict:
        """Slide 1: Aktueller Status und Uhrzeit"""
        current_status = self.status_service.get_current_status()
        
        # Status in Thai und English
        status_thai = self._translate_status_to_thai(current_status.type)
        status_english = self._translate_status_to_english(current_status.type)
        
        # Color coding für Status
        status_color = self._get_status_color(current_status.type)
        
        return {
            'type': 'now',
            'current_time': now,
            'digital_clock': now.strftime('%H:%M:%S'),
            'digital_date': now.strftime('%A, %d %B %Y'),
            'status': {
                'type': current_status.type,
                'thai_text': status_thai,
                'english_text': status_english,
                'color': status_color,
                'note': current_status.description,
                'from_date': current_status.date_from,
                'to_date': current_status.date_to,
                'return_date_thai': self._format_return_date_thai(current_status.date_to) if current_status.date_to else None,
                'return_date_english': self._format_return_date_english(current_status.date_to) if current_status.date_to else None
            }
        }
    
    def _get_today_slide_data(self, now: datetime) -> Dict:
        """Slide 2: Heutige Öffnungszeiten"""
        today_hours = self.schedule_service.get_hours_for_date(now.date())
        next_opening = self._calculate_next_opening(now) if not today_hours or today_hours.get('closed') else None
        
        return {
            'type': 'today',
            'date': now.date(),
            'day_thai': self.thai_days.get(now.strftime('%A').lower(), now.strftime('%A')),
            'day_english': now.strftime('%A'),
            'hours': today_hours,
            'is_open_now': self._is_currently_open(now, today_hours) if today_hours and not today_hours.get('closed') else False,
            'next_opening': next_opening
        }
    
    def _get_week_slide_data(self, now: datetime) -> Dict:
        """Slide 3: Wochenübersicht"""
        # Get Monday of current week
        monday = now - timedelta(days=now.weekday())
        week_data = []
        
        for i in range(7):
            day = monday + timedelta(days=i)
            day_key = day.strftime('%A').lower()
            hours = self.schedule_service.get_hours_for_date(day.date())
            
            week_data.append({
                'date': day.date(),
                'day_thai': self.thai_days.get(day_key, day.strftime('%A')),
                'day_english': day.strftime('%a'),
                'day_key': day_key,
                'hours': hours,
                'is_today': day.date() == now.date(),
                'is_open': bool(hours and not hours.get('closed', True))
            })
        
        return {
            'type': 'week',
            'week_start': monday.date(),
            'days': week_data,
            'current_day_index': now.weekday()
        }
    
    def _get_services_slide_data(self) -> Dict:
        """Slide 4: Verfügbare Services"""
        return {
            'type': 'services',
            'title_thai': 'บริการของเรา',
            'title_english': 'Our Medical Services',
            'services': list(self.thai_services.values()),
            'contact': {
                'phone_display': True,
                'qr_code': True,
                'emergency_info': {
                    'thai': 'ในกรณีฉุกเฉิน โปรดติดต่อ',
                    'english': 'For emergencies, please contact'
                }
            }
        }
    
    def _translate_status_to_thai(self, status_type: StatusType) -> str:
        """Übersetzt Status-Typen ins Thai"""
        translations = {
            StatusType.ANWESEND: 'เปิดให้บริการ',
            StatusType.URLAUB: 'ลาพักผ่อน', 
            StatusType.BILDUNGSURLAUB: 'ลาศึกษา',
            StatusType.KONGRESS: 'ประชุมวิชาการ',
            StatusType.SONSTIGES: 'ปิดทำการชั่วคราว'
        }
        return translations.get(status_type, 'ไม่ทราบสถานะ')
    
    def _translate_status_to_english(self, status_type: StatusType) -> str:
        """Übersetzt Status-Typen ins Englische"""
        translations = {
            StatusType.ANWESEND: 'We are open and ready to serve you',
            StatusType.URLAUB: 'Currently on vacation', 
            StatusType.BILDUNGSURLAUB: 'On educational leave for better service',
            StatusType.KONGRESS: 'Attending medical conference',
            StatusType.SONSTIGES: 'Temporarily closed'
        }
        return translations.get(status_type, 'Status unknown')
    
    def _get_status_color(self, status_type: StatusType) -> str:
        """Gibt die Farbkodierung für Status zurück"""
        colors = {
            StatusType.ANWESEND: '#00FF88',  # Bright green
            StatusType.URLAUB: '#FFD700',   # Gold/yellow
            StatusType.BILDUNGSURLAUB: '#0056B3',  # Blue
            StatusType.KONGRESS: '#9333EA',  # Purple
            StatusType.SONSTIGES: '#FF4444'  # Red
        }
        return colors.get(status_type, '#6B7280')
    
    def _format_return_date_thai(self, return_date: datetime) -> str:
        """Formatiert Rückkehrdatum auf Thai"""
        if not return_date:
            return None
        
        # Thai months
        thai_months = {
            1: 'มกราคม', 2: 'กุมภาพันธ์', 3: 'มีนาคม', 4: 'เมษายน',
            5: 'พฤษภาคม', 6: 'มิถุนายน', 7: 'กรกฎาคม', 8: 'สิงหาคม',
            9: 'กันยายน', 10: 'ตุลาคม', 11: 'พฤศจิกายน', 12: 'ธันวาคม'
        }
        
        thai_month = thai_months.get(return_date.month, str(return_date.month))
        buddhist_year = return_date.year + 543  # Convert to Buddhist calendar
        
        return f"{return_date.day} {thai_month} {buddhist_year}"
    
    def _format_return_date_english(self, return_date: datetime) -> str:
        """Formatiert Rückkehrdatum auf Englisch"""
        if not return_date:
            return None
        return return_date.strftime('%B %d, %Y')
    
    def _calculate_next_opening(self, now: datetime) -> Optional[Dict]:
        """Berechnet die nächste Öffnungszeit"""
        # Check next 14 days
        for i in range(1, 15):
            check_date = (now + timedelta(days=i)).date()
            hours = self.schedule_service.get_hours_for_date(check_date)
            
            if hours and not hours.get('closed', True) and hours.get('time_ranges'):
                next_date = datetime.combine(check_date, datetime.min.time()).replace(tzinfo=self.bangkok_tz)
                
                # Thai day name
                day_key = next_date.strftime('%A').lower()
                day_thai = self.thai_days.get(day_key, next_date.strftime('%A'))
                
                return {
                    'date': check_date,
                    'day_thai': day_thai,
                    'day_english': next_date.strftime('%A'),
                    'first_opening': hours.get('time_ranges', [])[0] if hours.get('time_ranges') else None,
                    'days_until': i,
                    'formatted_thai': f"{day_thai} ({i} วันข้างหน้า)",
                    'formatted_english': f"{next_date.strftime('%A')} (in {i} days)"
                }
        
        return None
    
    def _is_currently_open(self, now: datetime, today_hours) -> bool:
        """Prüft ob aktuell geöffnet"""
        if not today_hours or today_hours.get('closed', True):
            return False
        
        current_time = now.time()
        
        for time_range in today_hours.get('time_ranges', []):
            try:
                start_str, end_str = time_range.split('-')
                start_time = datetime.strptime(start_str.strip(), '%H:%M').time()
                end_time = datetime.strptime(end_str.strip(), '%H:%M').time()
                
                if start_time <= current_time <= end_time:
                    return True
            except (ValueError, AttributeError):
                continue
        
        return False
    
    def get_offline_data(self) -> Dict:
        """Bereit Offline-Fallback-Daten vor"""
        now = self.get_bangkok_time()
        
        return {
            'offline_mode': True,
            'last_update': now.isoformat(),
            'message_thai': 'ระบบออฟไลน์ - ข้อมูลล่าสุด',
            'message_english': 'Offline Mode - Last Updated',
            'contact': {
                'phone': '+66 XX XXX XXXX',  # From config
                'emergency': 'สำหรับเหตุฉุกเฉิน โปรดโทร 1669'
            },
            'basic_info': {
                'thai': 'ห้องปฏิบัติการการแพทย์ พัทยา',
                'english': 'Medical Laboratory Pattaya',
                'services': ['เจาะเลือด', 'ตรวจสุขภาพ', 'ปรึกษาแพทย์']
            }
        }
    
    def validate_rotation_config(self) -> Dict:
        """Validiert Kiosk-Konfiguration"""
        issues = []
        warnings = []
        
        # Check services
        current_status = self.status_service.get_current_status()
        if not current_status:
            issues.append("No status configured")
        
        # Check schedule
        now = self.get_bangkok_time()
        today_hours = self.schedule_service.get_today_hours(now.date())
        
        if not today_hours:
            warnings.append("No schedule for today")
        
        # Check timezone
        try:
            self.get_bangkok_time()
        except Exception as e:
            issues.append(f"Timezone error: {str(e)}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'last_check': now.isoformat()
        }