from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
from sqlmodel import Session, select
from app.models import StandardHours, HourException, Availability
from app.database import engine
import pytz
import logging

logger = logging.getLogger(__name__)


class ScheduleService:
    TIMEZONE = pytz.timezone('Asia/Bangkok')
    
    @staticmethod
    def get_hours_for_date(target_date: date) -> Dict:
        """Get opening hours for a specific date"""
        with Session(engine) as session:
            # Check for exceptions first
            exception = session.exec(
                select(HourException).where(HourException.exception_date == target_date)
            ).first()
            
            if exception:
                return {
                    'date': target_date,
                    'closed': exception.closed,
                    'time_ranges': exception.time_ranges,
                    'note': exception.note,
                    'is_exception': True
                }
            
            # Get standard hours for this day
            day_of_week = target_date.weekday()
            standard = session.exec(
                select(StandardHours).where(StandardHours.day_of_week == day_of_week)
            ).first()
            
            if standard:
                return {
                    'date': target_date,
                    'closed': len(standard.time_ranges) == 0,
                    'time_ranges': standard.time_ranges,
                    'note': None,
                    'is_exception': False
                }
            
            return {
                'date': target_date,
                'closed': True,
                'time_ranges': [],
                'note': None,
                'is_exception': False
            }
    
    @staticmethod
    def get_week_schedule(start_date: Optional[date] = None) -> List[Dict]:
        """Get schedule for a week starting from given date"""
        if not start_date:
            start_date = datetime.now(ScheduleService.TIMEZONE).date()
        
        # Find Monday of the week
        days_since_monday = start_date.weekday()
        week_start = start_date - timedelta(days=days_since_monday)
        
        schedule = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            schedule.append(ScheduleService.get_hours_for_date(day))
        
        return schedule
    
    @staticmethod
    def get_month_schedule(year: int, month: int) -> List[Dict]:
        """Get schedule for entire month"""
        first_day = date(year, month, 1)
        
        # Calculate last day of month
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        schedule = []
        current = first_day
        while current <= last_day:
            schedule.append(ScheduleService.get_hours_for_date(current))
            current += timedelta(days=1)
        
        return schedule
    
    @staticmethod
    def get_availability_for_date(target_date: date) -> Optional[Availability]:
        """Get availability slots for a specific date"""
        with Session(engine) as session:
            return session.exec(
                select(Availability).where(Availability.availability_date == target_date)
            ).first()
    
    @staticmethod
    def is_open_now() -> bool:
        """Check if currently open"""
        now = datetime.now(ScheduleService.TIMEZONE)
        today_hours = ScheduleService.get_hours_for_date(now.date())
        
        if today_hours['closed']:
            return False
        
        current_time = now.time()
        for time_range in today_hours['time_ranges']:
            start_str, end_str = time_range.split('-')
            start_time = datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.strptime(end_str, '%H:%M').time()
            
            if start_time <= current_time <= end_time:
                return True
        
        return False
    
    @staticmethod
    def get_opening_status() -> Dict:
        """Get detailed opening status with next opening/closing time"""
        now = datetime.now(ScheduleService.TIMEZONE)
        today_hours = ScheduleService.get_hours_for_date(now.date())
        is_open = ScheduleService.is_open_now()
        
        status = {
            'is_open': is_open,
            'current_time': now.strftime('%H:%M'),
            'current_date': now.date(),
            'today_closed': today_hours['closed'],
            'message_key': None,
            'next_change': None
        }
        
        if today_hours['closed']:
            status['message_key'] = 'closed_today'
            next_open = ScheduleService.get_next_open_time()
            if next_open:
                status['next_change'] = next_open
        elif is_open:
            status['message_key'] = 'currently_open'
            # Find when we close next
            current_time = now.time()
            for time_range in today_hours['time_ranges']:
                start_str, end_str = time_range.split('-')
                start_time = datetime.strptime(start_str, '%H:%M').time()
                end_time = datetime.strptime(end_str, '%H:%M').time()
                
                if start_time <= current_time <= end_time:
                    status['next_change'] = {
                        'date': now.date(),
                        'time': end_str,
                        'action': 'closes'
                    }
                    break
        else:
            status['message_key'] = 'currently_closed'
            # Find next opening today or tomorrow
            current_time = now.time()
            for time_range in today_hours['time_ranges']:
                start_str, end_str = time_range.split('-')
                start_time = datetime.strptime(start_str, '%H:%M').time()
                
                if current_time < start_time:
                    status['next_change'] = {
                        'date': now.date(),
                        'time': start_str,
                        'action': 'opens'
                    }
                    break
            
            if not status['next_change']:
                next_open = ScheduleService.get_next_open_time()
                if next_open:
                    status['next_change'] = next_open
                    status['next_change']['action'] = 'opens'
        
        return status
    
    @staticmethod
    def get_next_open_time() -> Optional[Dict]:
        """Get next opening time"""
        now = datetime.now(ScheduleService.TIMEZONE)
        current_date = now.date()
        
        # Check up to 14 days ahead
        for i in range(14):
            check_date = current_date + timedelta(days=i)
            hours = ScheduleService.get_hours_for_date(check_date)
            
            if not hours['closed'] and hours['time_ranges']:
                # If today, check if any time range is still ahead
                if i == 0:
                    current_time = now.strftime('%H:%M')
                    for time_range in hours['time_ranges']:
                        start, _ = time_range.split('-')
                        if start > current_time:
                            return {
                                'date': check_date,
                                'time': start,
                                'time_range': time_range
                            }
                else:
                    # Future date, return first time range
                    return {
                        'date': check_date,
                        'time': hours['time_ranges'][0].split('-')[0],
                        'time_range': hours['time_ranges'][0]
                    }
        
        return None
    
    @staticmethod
    def get_weekly_hours() -> Dict:
        """Get weekly standard hours"""
        weekly_hours = {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': []
        }
        
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        with Session(engine) as session:
            for i, day in enumerate(weekdays):
                standard = session.exec(
                    select(StandardHours).where(StandardHours.day_of_week == i)
                ).first()
                
                if standard and standard.time_ranges:
                    weekly_hours[day] = standard.time_ranges
        
        return weekly_hours
    
    @staticmethod
    def update_weekly_hours(weekly_hours: Dict) -> bool:
        """Update weekly standard hours"""
        try:
            weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            
            with Session(engine) as session:
                for i, day in enumerate(weekdays):
                    hours = weekly_hours.get(day, [])
                    
                    # Find existing standard hours
                    standard = session.exec(
                        select(StandardHours).where(StandardHours.day_of_week == i)
                    ).first()
                    
                    if standard:
                        # Update existing
                        standard.time_ranges = hours
                        standard.updated_at = datetime.now()
                    else:
                        # Create new
                        standard = StandardHours(
                            day_of_week=i,
                            time_ranges=hours
                        )
                        session.add(standard)
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating weekly hours: {e}")
            return False