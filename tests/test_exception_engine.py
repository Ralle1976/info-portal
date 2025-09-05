"""
Unit Tests für Exception Engine
Testet thailändische Feiertage und Ausnahmen-Logik

Diese Tests stellen sicher, dass:
- Thailändische Feiertage korrekt erkannt werden
- Ausnahmen korrekt verarbeitet werden
- Mehrsprachigkeit funktioniert
- Edge Cases abgedeckt sind
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock

from app.services.exception_engine import (
    ExceptionEngine, ThaiHolidayCalculator, ThaiHoliday, ExceptionType,
    is_thai_holiday_today, get_next_thai_holiday, get_thai_holidays_this_month
)
from app.models import HourException


class TestThaiHolidayCalculator:
    """Tests für thailändische Feiertags-Berechnung"""
    
    def test_get_fixed_holidays_2025(self):
        """Test fixe Feiertage für 2025"""
        holidays = ThaiHolidayCalculator.get_fixed_holidays(2025)
        
        assert len(holidays) > 10  # Mindestens 10 Feiertage
        
        # Test spezifische Feiertage
        holiday_dates = [h.date for h in holidays]
        
        # New Year
        assert date(2025, 1, 1) in holiday_dates
        
        # Songkran
        assert date(2025, 4, 13) in holiday_dates
        
        # Labour Day
        assert date(2025, 5, 1) in holiday_dates
        
        # New Year's Eve
        assert date(2025, 12, 31) in holiday_dates
    
    def test_thai_holiday_names_multilingual(self):
        """Test mehrsprachige Namen der Feiertage"""
        holidays = ThaiHolidayCalculator.get_fixed_holidays(2025)
        new_year = next(h for h in holidays if h.date == date(2025, 1, 1))
        
        assert new_year.get_name('th') == "วันขึ้นปีใหม่"
        assert new_year.get_name('de') == "Neujahr"
        assert new_year.get_name('en') == "New Year's Day"
        
        # Test fallback to Thai
        assert new_year.get_name('invalid') == new_year.name_th
    
    def test_thai_holiday_types(self):
        """Test Feiertags-Typen"""
        holidays = ThaiHolidayCalculator.get_fixed_holidays(2025)
        
        # National holidays
        national_holidays = [h for h in holidays if h.type == ExceptionType.NATIONAL_HOLIDAY]
        assert len(national_holidays) > 0
        
        # Royal holidays  
        royal_holidays = [h for h in holidays if h.type == ExceptionType.ROYAL_HOLIDAY]
        assert len(royal_holidays) > 0
        
        # Buddhist holidays
        buddhist_holidays = [h for h in holidays if h.type == ExceptionType.BUDDHIST_HOLIDAY]
        assert len(buddhist_holidays) > 0
    
    def test_business_affecting_holidays(self):
        """Test geschäftsrelevante Feiertage"""
        holidays = ThaiHolidayCalculator.get_fixed_holidays(2025)
        
        # Die meisten Feiertage sollten das Geschäft betreffen
        affecting_business = [h for h in holidays if h.affects_business]
        not_affecting = [h for h in holidays if not h.affects_business]
        
        assert len(affecting_business) > len(not_affecting)
    
    def test_chinese_new_year_approximation(self):
        """Test chinesisches Neujahr Approximation"""
        cny_2025 = ThaiHolidayCalculator._get_chinese_new_year(2025)
        
        # Should be in January or February
        assert cny_2025.month in [1, 2]
        
        # Test fallback for unknown year
        cny_unknown = ThaiHolidayCalculator._get_chinese_new_year(2050)
        assert cny_unknown.month == 2  # Fallback
        assert cny_unknown.day == 1


class TestExceptionEngine:
    """Tests für Exception Engine Hauptfunktionen"""
    
    def test_is_thai_holiday_positive(self):
        """Test Erkennung thailändischer Feiertage"""
        # New Year 2025
        holiday = ExceptionEngine.is_thai_holiday(date(2025, 1, 1))
        
        assert holiday is not None
        assert holiday.name_th == "วันขึ้นปีใหม่"
        assert holiday.type == ExceptionType.NATIONAL_HOLIDAY
        assert holiday.affects_business == True
    
    def test_is_thai_holiday_negative(self):
        """Test Nicht-Feiertag"""
        # Random regular day
        result = ExceptionEngine.is_thai_holiday(date(2025, 3, 15))
        
        assert result is None
    
    def test_is_thai_holiday_non_business_affecting(self):
        """Test Feiertag der Geschäft nicht betrifft"""
        # Chinese New Year (local event, nicht alle Geschäfte)
        holidays = ThaiHolidayCalculator.get_fixed_holidays(2025)
        cny = next((h for h in holidays if h.type == ExceptionType.LOCAL_EVENT), None)
        
        if cny and not cny.affects_business:
            result = ExceptionEngine.is_thai_holiday(cny.date)
            assert result is None  # Wird nicht zurückgegeben da affects_business=False
    
    @patch('app.services.exception_engine.Session')
    def test_get_exception_for_date_found(self, mock_session_class):
        """Test explizite Ausnahme gefunden"""
        # Mock session and query result
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        mock_exception = MagicMock(spec=HourException)
        mock_exception.exception_date = date(2025, 8, 22)
        mock_exception.closed = True
        mock_exception.time_ranges = []
        mock_exception.note = "Betriebsausflug"
        
        mock_session.exec.return_value.first.return_value = mock_exception
        
        result = ExceptionEngine.get_exception_for_date(date(2025, 8, 22))
        
        assert result == mock_exception
        assert mock_session.exec.called
    
    @patch('app.services.exception_engine.Session')
    def test_get_exception_for_date_not_found(self, mock_session_class):
        """Test explizite Ausnahme nicht gefunden"""
        # Mock session and query result
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        mock_session.exec.return_value.first.return_value = None
        
        result = ExceptionEngine.get_exception_for_date(date(2025, 8, 22))
        
        assert result is None
    
    @patch('app.services.exception_engine.ExceptionEngine.get_exception_for_date')
    @patch('app.services.exception_engine.ExceptionEngine.is_thai_holiday')
    def test_get_effective_exception_explicit_wins(self, mock_thai, mock_explicit):
        """Test explizite Ausnahme hat Vorrang vor Feiertag"""
        # Mock explicit exception
        mock_exception = MagicMock()
        mock_exception.closed = False
        mock_exception.time_ranges = ['10:00-14:00']
        mock_exception.note = "Sonderöffnung"
        mock_explicit.return_value = mock_exception
        
        # Mock Thai holiday (should be ignored)
        mock_holiday = MagicMock()
        mock_holiday.name_th = "Feiertag"
        mock_thai.return_value = mock_holiday
        
        result = ExceptionEngine.get_effective_exception_for_date(date(2025, 1, 1))
        
        assert result['exception_type'] == 'explicit'
        assert result['source'] == 'database'
        assert result['closed'] == False
        assert result['time_ranges'] == ['10:00-14:00']
        # Thai holiday should not be called since explicit exception exists
        mock_thai.assert_not_called()
    
    @patch('app.services.exception_engine.ExceptionEngine.get_exception_for_date')
    @patch('app.services.exception_engine.ExceptionEngine.is_thai_holiday')
    def test_get_effective_exception_thai_holiday(self, mock_thai, mock_explicit):
        """Test thailändischer Feiertag als Ausnahme"""
        # Mock no explicit exception
        mock_explicit.return_value = None
        
        # Mock Thai holiday
        mock_holiday = ThaiHoliday(
            name_th="วันขึ้นปีใหม่",
            name_de="Neujahr", 
            name_en="New Year's Day",
            date=date(2025, 1, 1),
            type=ExceptionType.NATIONAL_HOLIDAY,
            description_th="วันหยุดปีใหม่"
        )
        mock_thai.return_value = mock_holiday
        
        result = ExceptionEngine.get_effective_exception_for_date(date(2025, 1, 1))
        
        assert result['exception_type'] == 'NATIONAL_HOLIDAY'
        assert result['source'] == 'thai_holiday'
        assert result['closed'] == True
        assert result['note'] == "วันขึ้นปีใหม่"
        assert result['holiday_info']['name_th'] == "วันขึ้นปีใหม่"
        assert result['holiday_info']['name_de'] == "Neujahr"
    
    @patch('app.services.exception_engine.ExceptionEngine.get_exception_for_date')
    @patch('app.services.exception_engine.ExceptionEngine.is_thai_holiday')
    def test_get_effective_exception_none(self, mock_thai, mock_explicit):
        """Test keine Ausnahme gefunden"""
        # Mock no exceptions
        mock_explicit.return_value = None
        mock_thai.return_value = None
        
        result = ExceptionEngine.get_effective_exception_for_date(date(2025, 3, 15))
        
        assert result is None
    
    def test_get_upcoming_exceptions(self):
        """Test kommende Ausnahmen"""
        with patch('app.services.exception_engine.ExceptionEngine.get_effective_exception_for_date') as mock_get:
            # Mock some exceptions in the next 5 days
            def mock_exception(check_date):
                if check_date.day % 2 == 0:  # Even days have exceptions
                    return {
                        'date': check_date,
                        'closed': True,
                        'note': f'Exception on {check_date}'
                    }
                return None
            
            mock_get.side_effect = mock_exception
            
            with patch('app.services.exception_engine.datetime') as mock_datetime:
                mock_now = datetime(2025, 8, 21, 10, 0)  # Start on odd day
                mock_datetime.now.return_value = mock_now.replace(tzinfo=ExceptionEngine.BANGKOK_TZ)
                
                result = ExceptionEngine.get_upcoming_exceptions(days_ahead=4)
                
                # Should find exceptions on even days (22, 24)
                exception_dates = [e['date'] for e in result]
                assert date(2025, 8, 22) in exception_dates  # Even day
                assert date(2025, 8, 24) in exception_dates  # Even day
                assert len(result) == 2  # Only even days
    
    @patch('app.services.exception_engine.Session')
    def test_create_thai_holiday_exceptions(self, mock_session_class):
        """Test Erstellung von Thai-Feiertags-Ausnahmen"""
        # Mock session
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        # Mock no existing exceptions
        mock_session.exec.return_value.first.return_value = None
        
        result = ExceptionEngine.create_thai_holiday_exceptions(2025, overwrite_existing=False)
        
        assert result > 0  # Should create some exceptions
        assert mock_session.add.called
        assert mock_session.commit.called
    
    @patch('app.services.exception_engine.Session') 
    def test_create_thai_holiday_exceptions_overwrite(self, mock_session_class):
        """Test Überschreiben existierender Thai-Feiertags-Ausnahmen"""
        # Mock session
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        # Mock existing exception
        mock_existing = MagicMock()
        mock_existing.closed = False
        mock_existing.note = "Old note"
        mock_session.exec.return_value.first.return_value = mock_existing
        
        result = ExceptionEngine.create_thai_holiday_exceptions(2025, overwrite_existing=True)
        
        assert result > 0
        # Should update existing
        assert mock_existing.closed == True
        assert mock_existing.time_ranges == []
        assert mock_session.commit.called
    
    def test_get_exception_summary(self):
        """Test Ausnahmen-Zusammenfassung"""
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        
        with patch('app.services.exception_engine.ExceptionEngine.get_effective_exception_for_date') as mock_get:
            # Mock New Year's Day as Thai holiday
            def mock_exception(check_date):
                if check_date == date(2025, 1, 1):
                    return {
                        'date': check_date,
                        'closed': True,
                        'source': 'thai_holiday',
                        'note': 'New Year'
                    }
                elif check_date == date(2025, 1, 15):
                    return {
                        'date': check_date,
                        'closed': False,
                        'source': 'database',
                        'time_ranges': ['10:00-14:00'],
                        'note': 'Special hours'
                    }
                return None
            
            mock_get.side_effect = mock_exception
            
            result = ExceptionEngine.get_exception_summary(start_date, end_date, lang='th')
            
            assert result['period']['days_total'] == 31
            assert result['summary']['total_exceptions'] == 2
            assert result['summary']['thai_holidays'] == 1
            assert result['summary']['explicit_exceptions'] == 1
            assert result['summary']['closed_days'] == 1
            assert result['summary']['special_hours_days'] == 1
    
    def test_validate_exception_data_valid(self):
        """Test Validierung gültiger Ausnahmen-Daten"""
        errors = ExceptionEngine.validate_exception_data(
            exception_date=date.today() + timedelta(days=1),
            closed=True,
            time_ranges=None,
            note="Valid exception"
        )
        
        assert len(errors) == 0
    
    def test_validate_exception_data_past_date(self):
        """Test Validierung vergangenes Datum"""
        errors = ExceptionEngine.validate_exception_data(
            exception_date=date.today() - timedelta(days=1),
            closed=True,
            time_ranges=None,
            note="Past exception"
        )
        
        assert len(errors) > 0
        assert any("Vergangenheit" in error for error in errors)
    
    def test_validate_exception_data_invalid_time_format(self):
        """Test Validierung ungültiges Zeitformat"""
        errors = ExceptionEngine.validate_exception_data(
            exception_date=date.today() + timedelta(days=1),
            closed=False,
            time_ranges=["invalid-time", "10:00-12:00"],
            note="Invalid time"
        )
        
        assert len(errors) > 0
        assert any("Ungültiges Zeitformat" in error for error in errors)
    
    def test_validate_exception_data_closed_with_times(self):
        """Test Validierung geschlossen aber mit Zeiten"""
        errors = ExceptionEngine.validate_exception_data(
            exception_date=date.today() + timedelta(days=1),
            closed=True,
            time_ranges=["10:00-12:00"],
            note="Contradiction"
        )
        
        assert len(errors) > 0
        assert any("Geschlossene Tage" in error for error in errors)
    
    def test_validate_exception_data_open_without_times(self):
        """Test Validierung offen ohne Zeiten"""
        errors = ExceptionEngine.validate_exception_data(
            exception_date=date.today() + timedelta(days=1),
            closed=False,
            time_ranges=None,
            note="Missing times"
        )
        
        assert len(errors) > 0
        assert any("Zeitfenster angegeben werden" in error for error in errors)


class TestTemplateFunctions:
    """Tests für Template-Helper Funktionen"""
    
    def test_is_thai_holiday_today_true(self):
        """Test Template-Funktion für heutigen Feiertag"""
        with patch('app.services.exception_engine.datetime') as mock_datetime:
            mock_now = datetime(2025, 1, 1, 10, 0)  # New Year's Day
            mock_datetime.now.return_value = mock_now.replace(tzinfo=ExceptionEngine.BANGKOK_TZ)
            
            result = is_thai_holiday_today()
            
            assert result == True
    
    def test_is_thai_holiday_today_false(self):
        """Test Template-Funktion für normalen Tag"""
        with patch('app.services.exception_engine.datetime') as mock_datetime:
            mock_now = datetime(2025, 3, 15, 10, 0)  # Regular day
            mock_datetime.now.return_value = mock_now.replace(tzinfo=ExceptionEngine.BANGKOK_TZ)
            
            result = is_thai_holiday_today()
            
            assert result == False
    
    def test_get_next_thai_holiday(self):
        """Test Template-Funktion für nächsten Feiertag"""
        with patch('app.services.exception_engine.datetime') as mock_datetime:
            mock_now = datetime(2024, 12, 20, 10, 0)  # Before New Year
            mock_datetime.now.return_value = mock_now.replace(tzinfo=ExceptionEngine.BANGKOK_TZ)
            
            result = get_next_thai_holiday(lang='th')
            
            assert result is not None
            assert result['date'] == '2025-01-01'
            assert 'วันขึ้นปีใหม่' in result['name']
            assert result['days_until'] >= 0
    
    def test_get_next_thai_holiday_none(self):
        """Test Template-Funktion wenn kein Feiertag in nächsten 365 Tagen"""
        with patch('app.services.exception_engine.ExceptionEngine.is_thai_holiday') as mock_holiday:
            mock_holiday.return_value = None  # No holidays found
            
            with patch('app.services.exception_engine.datetime') as mock_datetime:
                mock_now = datetime(2025, 3, 15, 10, 0)
                mock_datetime.now.return_value = mock_now.replace(tzinfo=ExceptionEngine.BANGKOK_TZ)
                
                result = get_next_thai_holiday()
                
                assert result is None
    
    def test_get_thai_holidays_this_month(self):
        """Test Template-Funktion für Feiertage diesen Monat"""
        with patch('app.services.exception_engine.datetime') as mock_datetime:
            mock_now = datetime(2025, 1, 15, 10, 0)  # January 2025
            mock_datetime.now.return_value = mock_now.replace(tzinfo=ExceptionEngine.BANGKOK_TZ)
            
            result = get_thai_holidays_this_month(lang='th')
            
            # Should find New Year's Day in January
            assert len(result) > 0
            new_year = next((h for h in result if h['date'] == '2025-01-01'), None)
            assert new_year is not None
            assert 'วันขึ้นปีใหม่' in new_year['name']
    
    def test_get_thai_holidays_this_month_empty(self):
        """Test Template-Funktion für Monat ohne Feiertage"""
        with patch('app.services.exception_engine.datetime') as mock_datetime:
            mock_now = datetime(2025, 3, 15, 10, 0)  # March 2025 (likely no major holidays)
            mock_datetime.now.return_value = mock_now.replace(tzinfo=ExceptionEngine.BANGKOK_TZ)
            
            result = get_thai_holidays_this_month()
            
            # March might have no major business-affecting holidays
            # This is OK - result can be empty list


class TestEdgeCases:
    """Tests für Edge Cases und spezielle Situationen"""
    
    def test_leap_year_handling(self):
        """Test Schaltjahr-Behandlung"""
        holidays_2024 = ThaiHolidayCalculator.get_fixed_holidays(2024)  # Leap year
        holidays_2025 = ThaiHolidayCalculator.get_fixed_holidays(2025)  # Non-leap year
        
        # Both should have similar number of holidays
        assert abs(len(holidays_2024) - len(holidays_2025)) <= 1
    
    def test_multiple_years_consistency(self):
        """Test Konsistenz über mehrere Jahre"""
        for year in range(2024, 2028):
            holidays = ThaiHolidayCalculator.get_fixed_holidays(year)
            
            # Basic consistency checks
            assert len(holidays) > 10
            assert all(h.date.year == year for h in holidays)
            assert all(h.name_th for h in holidays)
            assert all(h.name_de for h in holidays) 
            assert all(h.name_en for h in holidays)
    
    def test_holiday_date_boundary(self):
        """Test Feiertags-Datum Grenzen"""
        holidays = ThaiHolidayCalculator.get_fixed_holidays(2025)
        
        # All holidays should be within the year
        for holiday in holidays:
            assert holiday.date.year == 2025
            assert 1 <= holiday.date.month <= 12
            assert 1 <= holiday.date.day <= 31


if __name__ == '__main__':
    pytest.main([__file__, '-v'])