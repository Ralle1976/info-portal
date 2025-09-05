"""
Unit Tests für Next Opening Calculator
Testet Edge Cases und komplexe Szenarien für die Status-Logic

Diese Tests stellen sicher, dass die intelligente Öffnungszeit-Berechnung
korrekt funktioniert unter verschiedenen Bedingungen:
- Verschiedene Status-Typen
- Thailändische Feiertage
- Wochenenden und Ausnahmen
- Timezone-Handling (Bangkok)
- Cache-Performance
"""

import pytest
from datetime import date, datetime, time, timedelta
from unittest.mock import patch, MagicMock
import pytz

from app.services.next_opening_calculator import (
    NextOpeningCalculator, TodayStatus, NextOpening, ClosureReason,
    get_smart_status, get_today_remaining_slots, is_open_now
)
from app.services.status import StatusService
from app.services.schedule import ScheduleService
from app.models import Status, StatusType


class TestNextOpeningCalculator:
    """Haupttests für NextOpeningCalculator"""
    
    def setup_method(self):
        """Setup für jeden Test"""
        # Clear cache before each test
        NextOpeningCalculator._cache.clear()
        NextOpeningCalculator._last_cache_clear = datetime.now()
    
    @patch('app.services.next_opening_calculator.datetime')
    def test_get_current_bangkok_time(self, mock_datetime):
        """Test Bangkok Timezone Handling"""
        # Mock current time
        mock_now = datetime(2025, 8, 23, 14, 30)  # UTC
        mock_datetime.now.return_value = mock_now
        
        # Test with Bangkok timezone
        with patch.object(NextOpeningCalculator, 'BANGKOK_TZ') as mock_tz:
            mock_tz.localize.return_value = mock_now
            result = NextOpeningCalculator.get_current_bangkok_time()
            
            mock_datetime.now.assert_called_with(NextOpeningCalculator.BANGKOK_TZ)
    
    @patch('app.services.next_opening_calculator.StatusService')
    @patch('app.services.next_opening_calculator.ScheduleService')  
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_get_today_status_open_now(self, mock_time, mock_schedule, mock_status):
        """Test TodayStatus wenn aktuell geöffnet"""
        # Mock current time - Friday 14:30
        mock_now = datetime(2025, 8, 22, 14, 30)  # Friday
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        # Mock status - present
        mock_status_obj = MagicMock()
        mock_status_obj.type = StatusType.ANWESEND
        mock_status.get_current_status.return_value = mock_status_obj
        
        # Mock schedule - open with remaining slots
        mock_schedule.get_hours_for_date.return_value = {
            'closed': False,
            'time_ranges': ['08:30-12:00', '13:00-16:00'],
            'note': None
        }
        
        result = NextOpeningCalculator.get_today_status()
        
        assert isinstance(result, TodayStatus)
        assert result.is_open_now == True
        assert result.closes_at == '16:00'
        assert result.remaining_slots == ['14:30-16:00']
        assert result.closure_reason is None
    
    @patch('app.services.next_opening_calculator.StatusService')
    @patch('app.services.next_opening_calculator.ScheduleService')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_get_today_status_absent(self, mock_time, mock_schedule, mock_status):
        """Test TodayStatus bei Abwesenheit"""
        # Mock current time
        mock_now = datetime(2025, 8, 22, 10, 0)
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        # Mock status - vacation
        mock_status_obj = MagicMock()
        mock_status_obj.type = StatusType.URLAUB
        mock_status_obj.description = "Sommerurlaub"
        mock_status_obj.date_from = date(2025, 8, 20)
        mock_status_obj.date_to = date(2025, 8, 30)
        mock_status.get_current_status.return_value = mock_status_obj
        
        result = NextOpeningCalculator.get_today_status()
        
        assert result.is_open_now == False
        assert result.remaining_slots == []
        assert result.closure_reason == ClosureReason.VACATION
        assert result.closure_note == "Sommerurlaub (20.08. - 30.08.2025)"
    
    @patch('app.services.next_opening_calculator.StatusService')
    @patch('app.services.next_opening_calculator.ScheduleService')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_get_today_status_closed_weekend(self, mock_time, mock_schedule, mock_status):
        """Test TodayStatus am Wochenende"""
        # Mock current time - Sunday
        mock_now = datetime(2025, 8, 24, 10, 0)  # Sunday
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        # Mock status - present
        mock_status_obj = MagicMock()
        mock_status_obj.type = StatusType.ANWESEND
        mock_status.get_current_status.return_value = mock_status_obj
        
        # Mock schedule - closed on weekend
        mock_schedule.get_hours_for_date.return_value = {
            'closed': True,
            'time_ranges': [],
            'note': None
        }
        
        result = NextOpeningCalculator.get_today_status()
        
        assert result.is_open_now == False
        assert result.remaining_slots == []
        assert result.closure_reason == ClosureReason.WEEKEND
    
    @patch('app.services.next_opening_calculator.StatusService')
    @patch('app.services.next_opening_calculator.ScheduleService')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_get_today_status_opens_soon(self, mock_time, mock_schedule, mock_status):
        """Test TodayStatus kurz vor Öffnung"""
        # Mock current time - 08:00 (opens at 08:30)
        mock_now = datetime(2025, 8, 22, 8, 0)
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        # Mock status - present
        mock_status_obj = MagicMock()
        mock_status_obj.type = StatusType.ANWESEND
        mock_status.get_current_status.return_value = mock_status_obj
        
        # Mock schedule - opens soon
        mock_schedule.get_hours_for_date.return_value = {
            'closed': False,
            'time_ranges': ['08:30-12:00', '13:00-16:00'],
            'note': None
        }
        
        result = NextOpeningCalculator.get_today_status()
        
        assert result.is_open_now == False
        assert result.next_slot_time == '08:30'
        assert result.minutes_until_next == 30
        assert result.closure_reason == ClosureReason.NOT_OPEN_YET
        assert len(result.remaining_slots) == 2
    
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_today_status')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator._is_absent_on_date')
    @patch('app.services.next_opening_calculator.ScheduleService')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_get_next_opening_today_remaining(self, mock_time, mock_schedule, mock_absent, mock_today):
        """Test get_next_opening mit verbleibenden heutigen Slots"""
        # Mock current time
        mock_now = datetime(2025, 8, 22, 10, 0)
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        # Mock today status with remaining slots
        today_status = TodayStatus(
            is_open_now=False,
            remaining_slots=['13:00-16:00'],
            next_slot_time='13:00',
            closes_at=None,
            closure_reason=None,
            closure_note=None,
            minutes_until_next=180
        )
        mock_today.return_value = today_status
        
        result = NextOpeningCalculator.get_next_opening(exclude_today=False)
        
        assert isinstance(result, NextOpening)
        assert result.date == mock_now.date()
        assert result.time == '13:00'
        assert result.is_today == True
        assert result.is_tomorrow == False
        assert result.days_until == 0
    
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_today_status')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator._is_absent_on_date')
    @patch('app.services.next_opening_calculator.ScheduleService')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_get_next_opening_tomorrow(self, mock_time, mock_schedule, mock_absent, mock_today):
        """Test get_next_opening für morgen"""
        # Mock current time - late Friday
        mock_now = datetime(2025, 8, 22, 17, 0)
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        # Mock today status - no remaining slots
        today_status = TodayStatus(
            is_open_now=False,
            remaining_slots=[],
            next_slot_time=None,
            closes_at=None,
            closure_reason=None,
            closure_note=None,
            minutes_until_next=None
        )
        mock_today.return_value = today_status
        
        # Mock absence check - not absent
        mock_absent.return_value = False
        
        # Mock tomorrow schedule - Saturday closed, Monday open
        def mock_get_hours(target_date):
            if target_date.weekday() == 5:  # Saturday
                return {'closed': True, 'time_ranges': [], 'note': None}
            elif target_date.weekday() == 6:  # Sunday  
                return {'closed': True, 'time_ranges': [], 'note': None}
            else:  # Monday
                return {'closed': False, 'time_ranges': ['08:30-12:00'], 'note': None}
        
        mock_schedule.get_hours_for_date.side_effect = mock_get_hours
        
        result = NextOpeningCalculator.get_next_opening(exclude_today=False)
        
        assert result is not None
        assert result.days_until >= 1  # At least tomorrow or later
        assert result.is_today == False
        assert result.time == '08:30'
    
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_today_status')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator._is_absent_on_date')
    @patch('app.services.next_opening_calculator.ScheduleService')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_get_next_opening_long_absence(self, mock_time, mock_schedule, mock_absent, mock_today):
        """Test get_next_opening während langer Abwesenheit"""
        # Mock current time
        mock_now = datetime(2025, 8, 22, 10, 0)
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        # Mock today status - absent
        today_status = TodayStatus(
            is_open_now=False,
            remaining_slots=[],
            next_slot_time=None,
            closes_at=None,
            closure_reason=ClosureReason.VACATION,
            closure_note="Lange Abwesenheit",
            minutes_until_next=None
        )
        mock_today.return_value = today_status
        
        # Mock absence - absent for next 10 days
        def mock_is_absent(check_date):
            start_date = date(2025, 8, 22)
            end_date = date(2025, 9, 1)
            return start_date <= check_date <= end_date
        
        mock_absent.side_effect = mock_is_absent
        
        # Mock schedule - normal schedule after absence
        def mock_get_hours(target_date):
            if target_date > date(2025, 9, 1):  # After absence
                return {'closed': False, 'time_ranges': ['08:30-12:00'], 'note': None}
            return {'closed': False, 'time_ranges': ['08:30-12:00'], 'note': None}
        
        mock_schedule.get_hours_for_date.side_effect = mock_get_hours
        
        result = NextOpeningCalculator.get_next_opening(exclude_today=False)
        
        assert result is not None
        assert result.days_until >= 10  # After absence period
        assert result.time == '08:30'
    
    @patch('app.services.next_opening_calculator.NextOpeningCalculator._is_absent_on_date')
    @patch('app.services.next_opening_calculator.ScheduleService')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_get_next_opening_no_opening_found(self, mock_time, mock_schedule, mock_absent):
        """Test get_next_opening wenn kein Öffnungstermin gefunden wird"""
        # Mock current time
        mock_now = datetime(2025, 8, 22, 10, 0)
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        # Mock absence - always absent
        mock_absent.return_value = True
        
        # Mock schedule - always closed
        mock_schedule.get_hours_for_date.return_value = {
            'closed': True, 'time_ranges': [], 'note': None
        }
        
        result = NextOpeningCalculator.get_next_opening(exclude_today=True)
        
        assert result is None
    
    def test_cache_functionality(self):
        """Test Cache-Mechanismus"""
        # Clear cache
        NextOpeningCalculator._cache.clear()
        
        # Test cache miss and hit
        with patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time') as mock_time:
            mock_time.return_value = datetime(2025, 8, 22, 10, 0, tzinfo=NextOpeningCalculator.BANGKOK_TZ)
            
            with patch('app.services.next_opening_calculator.StatusService') as mock_status:
                mock_status_obj = MagicMock()
                mock_status_obj.type = StatusType.ANWESEND
                mock_status.get_current_status.return_value = mock_status_obj
                
                with patch('app.services.next_opening_calculator.ScheduleService') as mock_schedule:
                    mock_schedule.get_hours_for_date.return_value = {
                        'closed': True, 'time_ranges': [], 'note': None
                    }
                    
                    # First call - cache miss
                    result1 = NextOpeningCalculator.get_today_status()
                    
                    # Second call - cache hit (should not call mocks again)
                    result2 = NextOpeningCalculator.get_today_status()
                    
                    assert result1.closure_reason == result2.closure_reason
                    # Verify cache was used (status service called only once)
                    assert mock_status.get_current_status.call_count == 1
    
    def test_cache_expiration(self):
        """Test Cache-Ablauf"""
        # Set cache timeout to 0 for immediate expiration
        original_timeout = NextOpeningCalculator._cache_timeout
        NextOpeningCalculator._cache_timeout = timedelta(seconds=0)
        
        try:
            with patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time') as mock_time:
                mock_time.return_value = datetime(2025, 8, 22, 10, 0, tzinfo=NextOpeningCalculator.BANGKOK_TZ)
                
                # Add something to cache
                NextOpeningCalculator._cache['test'] = 'value'
                
                # Call _clear_expired_cache
                NextOpeningCalculator._clear_expired_cache()
                
                # Cache should be cleared
                assert len(NextOpeningCalculator._cache) == 0
        
        finally:
            # Restore original timeout
            NextOpeningCalculator._cache_timeout = original_timeout


class TestClosureExplanation:
    """Tests für mehrsprachige Schließungserklärungen"""
    
    @patch('app.services.next_opening_calculator.StatusService')
    @patch('app.services.next_opening_calculator.ScheduleService')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_get_closure_explanation_thai(self, mock_time, mock_schedule, mock_status):
        """Test Schließungserklärung auf Thai"""
        # Mock current time
        mock_now = datetime(2025, 8, 22, 10, 0)
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        # Mock status - education leave
        mock_status_obj = MagicMock()
        mock_status_obj.type = StatusType.BILDUNGSURLAUB
        mock_status_obj.description = "Fortbildung"
        mock_status_obj.date_from = date(2025, 8, 22)
        mock_status_obj.date_to = date(2025, 8, 25)
        mock_status.get_current_status.return_value = mock_status_obj
        
        # Mock schedule
        mock_schedule.get_hours_for_date.return_value = {
            'closed': False, 'time_ranges': ['08:30-12:00'], 'note': None
        }
        
        with patch('app.services.next_opening_calculator.NextOpeningCalculator.get_next_opening'):
            result = NextOpeningCalculator.get_closure_explanation(lang='th')
            
            assert result['reason'] == 'EDUCATION'
            assert 'อบรมเพิ่มพูนความรู้' in result['message']
            assert result['note'] == 'Fortbildung (22.08. - 25.08.2025)'
    
    @patch('app.services.next_opening_calculator.StatusService')
    @patch('app.services.next_opening_calculator.ScheduleService') 
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_get_closure_explanation_german(self, mock_time, mock_schedule, mock_status):
        """Test Schließungserklärung auf Deutsch"""
        # Mock current time - Weekend
        mock_now = datetime(2025, 8, 24, 10, 0)  # Sunday
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        # Mock status - present
        mock_status_obj = MagicMock()
        mock_status_obj.type = StatusType.ANWESEND
        mock_status.get_current_status.return_value = mock_status_obj
        
        # Mock schedule - closed on weekend
        mock_schedule.get_hours_for_date.return_value = {
            'closed': True, 'time_ranges': [], 'note': None
        }
        
        with patch('app.services.next_opening_calculator.NextOpeningCalculator.get_next_opening'):
            result = NextOpeningCalculator.get_closure_explanation(lang='de')
            
            assert result['reason'] == 'WEEKEND'
            assert result['message'] == 'Wochenende'


class TestSmartStatusMessage:
    """Tests für intelligente Status-Nachrichten"""
    
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_today_status')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_next_opening')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_closure_explanation')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_smart_status_open_now(self, mock_time, mock_closure, mock_next, mock_today):
        """Test Smart Status wenn aktuell geöffnet"""
        # Mock current time
        mock_now = datetime(2025, 8, 22, 10, 0)
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        # Mock today status - open now
        today_status = TodayStatus(
            is_open_now=True,
            remaining_slots=['10:00-12:00'],
            next_slot_time=None,
            closes_at='12:00',
            closure_reason=None,
            closure_note=None,
            minutes_until_next=None
        )
        mock_today.return_value = today_status
        
        result = NextOpeningCalculator.get_smart_status_message(lang='th')
        
        assert result['status_type'] == 'open'
        assert result['is_open'] == True
        assert 'เปิดให้บริการอยู่' in result['main_message']
        assert '12:00' in result['main_message']
    
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_today_status')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_next_opening')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_closure_explanation')
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_smart_status_opens_soon(self, mock_time, mock_closure, mock_next, mock_today):
        """Test Smart Status kurz vor Öffnung"""
        # Mock current time
        mock_now = datetime(2025, 8, 22, 8, 0)
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        # Mock today status - opens soon
        today_status = TodayStatus(
            is_open_now=False,
            remaining_slots=['08:30-12:00'],
            next_slot_time='08:30',
            closes_at=None,
            closure_reason=None,
            closure_note=None,
            minutes_until_next=30
        )
        mock_today.return_value = today_status
        
        result = NextOpeningCalculator.get_smart_status_message(lang='th')
        
        assert result['status_type'] == 'opening_soon'
        assert result['opens_soon'] == True
        assert 'เปิดในอีก 30 นาที' in result['main_message']


class TestTemplateFunctions:
    """Tests für Template-Helper Funktionen"""
    
    def test_get_smart_status(self):
        """Test Template-Funktion get_smart_status"""
        with patch('app.services.next_opening_calculator.NextOpeningCalculator.get_smart_status_message') as mock:
            mock.return_value = {'status_type': 'open', 'message': 'Test'}
            
            result = get_smart_status('th')
            
            mock.assert_called_once_with('th')
            assert result['status_type'] == 'open'
    
    def test_get_today_remaining_slots(self):
        """Test Template-Funktion get_today_remaining_slots"""
        with patch('app.services.next_opening_calculator.NextOpeningCalculator.get_today_status') as mock:
            mock_status = TodayStatus(
                is_open_now=False,
                remaining_slots=['13:00-16:00'],
                next_slot_time='13:00',
                closes_at=None,
                closure_reason=None,
                closure_note=None,
                minutes_until_next=180
            )
            mock.return_value = mock_status
            
            result = get_today_remaining_slots()
            
            assert result == ['13:00-16:00']
    
    def test_is_open_now(self):
        """Test Template-Funktion is_open_now"""
        with patch('app.services.next_opening_calculator.NextOpeningCalculator.get_today_status') as mock:
            mock_status = TodayStatus(
                is_open_now=True,
                remaining_slots=[],
                next_slot_time=None,
                closes_at='16:00',
                closure_reason=None,
                closure_note=None,
                minutes_until_next=None
            )
            mock.return_value = mock_status
            
            result = is_open_now()
            
            assert result == True


class TestEdgeCases:
    """Tests für Edge Cases und Grenzfälle"""
    
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_new_year_transition(self, mock_time):
        """Test Jahreswechsel"""
        # Mock New Year's Eve 23:59
        mock_now = datetime(2025, 12, 31, 23, 59)
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        with patch('app.services.next_opening_calculator.StatusService') as mock_status:
            mock_status_obj = MagicMock()
            mock_status_obj.type = StatusType.ANWESEND
            mock_status.get_current_status.return_value = mock_status_obj
            
            with patch('app.services.next_opening_calculator.ScheduleService') as mock_schedule:
                # Closed on New Year's Eve
                mock_schedule.get_hours_for_date.return_value = {
                    'closed': True, 'time_ranges': [], 'note': 'Silvester'
                }
                
                result = NextOpeningCalculator.get_today_status()
                
                assert result.is_open_now == False
                assert result.closure_reason == ClosureReason.EXCEPTION
    
    @patch('app.services.next_opening_calculator.NextOpeningCalculator.get_current_bangkok_time')
    def test_midnight_boundary(self, mock_time):
        """Test Mitternachts-Grenze"""
        # Mock midnight
        mock_now = datetime(2025, 8, 23, 0, 0)
        mock_time.return_value = mock_now.replace(tzinfo=NextOpeningCalculator.BANGKOK_TZ)
        
        with patch('app.services.next_opening_calculator.StatusService') as mock_status:
            mock_status_obj = MagicMock()
            mock_status_obj.type = StatusType.ANWESEND
            mock_status.get_current_status.return_value = mock_status_obj
            
            with patch('app.services.next_opening_calculator.ScheduleService') as mock_schedule:
                mock_schedule.get_hours_for_date.return_value = {
                    'closed': False, 'time_ranges': ['08:30-12:00'], 'note': None
                }
                
                result = NextOpeningCalculator.get_today_status()
                
                assert result.is_open_now == False
                assert result.next_slot_time == '08:30'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])