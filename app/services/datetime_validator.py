from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, time, timedelta
import pytz
from enum import Enum
from dataclasses import dataclass, field

class ConflictType(str, Enum):
    """Types of conflicts that can occur"""
    OVERLAP = "overlap"
    GAP_TOO_SMALL = "gap_too_small"
    INVALID_ORDER = "invalid_order"
    PAST_DATE = "past_date"
    TOO_SHORT = "too_short"
    TOO_LONG = "too_long"
    BUSINESS_HOURS = "business_hours"

@dataclass
class ValidationError:
    """Represents a validation error with details"""
    type: ConflictType
    message: str
    field: str
    severity: str = "error"  # "error", "warning", "info"
    suggestions: List[str] = field(default_factory=list)

@dataclass
class TimeSlot:
    """Represents a time slot for validation"""
    start_datetime: datetime
    end_datetime: datetime
    type: str = "general"
    id: Optional[int] = None
    description: Optional[str] = None

class DateTimeValidator:
    """Smart datetime validation service with Bangkok timezone support"""
    
    BANGKOK_TZ = pytz.timezone('Asia/Bangkok')
    
    # Business rules
    MIN_ABSENCE_HOURS = 4  # Minimum absence duration in hours
    MAX_ABSENCE_DAYS = 90  # Maximum absence duration in days
    MIN_GAP_BETWEEN_SLOTS = 30  # Minimum gap in minutes between availability slots
    WORKING_HOURS_START = time(8, 0)  # 8:00 AM
    WORKING_HOURS_END = time(18, 0)    # 6:00 PM
    
    @classmethod
    def get_current_time(cls) -> datetime:
        """Get current time in Bangkok timezone"""
        return datetime.now(cls.BANGKOK_TZ)
    
    @classmethod
    def validate_absence_period(cls, start_date: date, start_time: time, 
                               end_date: date, end_time: time,
                               existing_absences: List[TimeSlot] = None,
                               current_id: Optional[int] = None) -> List[ValidationError]:
        """
        Comprehensive validation for absence periods with conflict detection
        
        Args:
            start_date: Start date of absence
            start_time: Start time of absence  
            end_date: End date of absence
            end_time: End time of absence
            existing_absences: List of existing absence periods
            current_id: ID of current absence being edited (to exclude from conflicts)
        
        Returns:
            List of validation errors and warnings
        """
        errors = []
        
        # Create datetime objects with Bangkok timezone
        start_dt = cls.BANGKOK_TZ.localize(datetime.combine(start_date, start_time))
        end_dt = cls.BANGKOK_TZ.localize(datetime.combine(end_date, end_time))
        current_dt = cls.get_current_time()
        
        # Basic order validation
        if start_dt >= end_dt:
            errors.append(ValidationError(
                type=ConflictType.INVALID_ORDER,
                field="end_datetime",
                message="Endzeit muss nach der Startzeit liegen",
                suggestions=["Prüfen Sie die eingegebenen Zeiten"]
            ))
            return errors  # Stop validation if basic order is wrong
        
        # Past date validation
        if start_dt < current_dt:
            if start_dt.date() < current_dt.date():
                errors.append(ValidationError(
                    type=ConflictType.PAST_DATE,
                    field="start_date",
                    message="Startdatum kann nicht in der Vergangenheit liegen",
                    severity="error"
                ))
            else:
                # Same day, but time has passed
                errors.append(ValidationError(
                    type=ConflictType.PAST_DATE,
                    field="start_time", 
                    message="Startzeit liegt in der Vergangenheit",
                    severity="warning",
                    suggestions=["Verwenden Sie die aktuelle Zeit oder später"]
                ))
        
        # Duration validation
        duration = end_dt - start_dt
        duration_hours = duration.total_seconds() / 3600
        duration_days = duration.days + (duration.seconds / 86400)
        
        if duration_hours < cls.MIN_ABSENCE_HOURS:
            errors.append(ValidationError(
                type=ConflictType.TOO_SHORT,
                field="duration",
                message=f"Abwesenheit ist sehr kurz ({duration_hours:.1f} Stunden)",
                severity="warning",
                suggestions=["Erwägen Sie eine längere Abwesenheit oder nutzen Sie Ausnahmen"]
            ))
        
        if duration_days > cls.MAX_ABSENCE_DAYS:
            errors.append(ValidationError(
                type=ConflictType.TOO_LONG,
                field="duration", 
                message=f"Abwesenheit ist sehr lang ({duration_days:.0f} Tage)",
                severity="warning",
                suggestions=["Teilen Sie lange Abwesenheiten in mehrere Perioden auf"]
            ))
        
        # Overlap validation with existing absences
        if existing_absences:
            overlaps = cls._find_overlaps(
                TimeSlot(start_dt, end_dt, "absence"),
                existing_absences,
                exclude_id=current_id
            )
            
            for overlap in overlaps:
                errors.append(ValidationError(
                    type=ConflictType.OVERLAP,
                    field="period",
                    message=f"Überschneidung mit bestehender Abwesenheit: {overlap.description or 'Unbenannt'}",
                    severity="error",
                    suggestions=[
                        "Passen Sie das Start- oder Enddatum an",
                        "Löschen Sie die überschneidende Abwesenheit",
                        "Kombinieren Sie die Abwesenheiten"
                    ]
                ))
        
        return errors
    
    @classmethod
    def validate_opening_hours(cls, day_ranges: List[str]) -> List[ValidationError]:
        """
        Validate opening hour ranges for a single day
        
        Args:
            day_ranges: List of time ranges in format ["09:00-12:00", "14:00-18:00"]
        
        Returns:
            List of validation errors
        """
        errors = []
        parsed_ranges = []
        
        # Parse and validate individual ranges
        for i, range_str in enumerate(day_ranges):
            try:
                start_str, end_str = range_str.split('-')
                start_time = time.fromisoformat(start_str.strip())
                end_time = time.fromisoformat(end_str.strip())
                
                if start_time >= end_time:
                    errors.append(ValidationError(
                        type=ConflictType.INVALID_ORDER,
                        field=f"range_{i}",
                        message=f"Ungültige Zeitspanne: {range_str}",
                        suggestions=["Endzeit muss nach Startzeit liegen"]
                    ))
                    continue
                
                parsed_ranges.append((start_time, end_time, i))
                
            except ValueError:
                errors.append(ValidationError(
                    type=ConflictType.INVALID_ORDER,
                    field=f"range_{i}",
                    message=f"Ungültiges Zeitformat: {range_str}",
                    suggestions=["Verwenden Sie das Format HH:MM-HH:MM"]
                ))
        
        # Check for overlaps between ranges
        parsed_ranges.sort()  # Sort by start time
        for i in range(len(parsed_ranges) - 1):
            current_end = parsed_ranges[i][1]
            next_start = parsed_ranges[i + 1][0]
            
            if current_end > next_start:
                errors.append(ValidationError(
                    type=ConflictType.OVERLAP,
                    field=f"range_{parsed_ranges[i][2]}_range_{parsed_ranges[i+1][2]}",
                    message=f"Überschneidende Zeitspannen: {day_ranges[parsed_ranges[i][2]]} und {day_ranges[parsed_ranges[i+1][2]]}",
                    suggestions=["Passen Sie die Zeiten an oder kombinieren Sie die Spannen"]
                ))
            elif current_end == next_start:
                # Adjacent ranges - could be combined
                errors.append(ValidationError(
                    type=ConflictType.GAP_TOO_SMALL,
                    field=f"range_{parsed_ranges[i][2]}_range_{parsed_ranges[i+1][2]}",
                    message=f"Aneinandergrenzende Zeitspannen könnten kombiniert werden",
                    severity="info",
                    suggestions=[f"Kombinieren zu: {parsed_ranges[i][0].strftime('%H:%M')}-{parsed_ranges[i+1][1].strftime('%H:%M')}"]
                ))
        
        return errors
    
    @classmethod
    def validate_availability_slot(cls, slot_date: date, start_time: time, end_time: time,
                                 existing_slots: List[TimeSlot] = None,
                                 opening_hours: List[str] = None,
                                 current_id: Optional[int] = None) -> List[ValidationError]:
        """
        Validate availability slot with business hours and overlap checks
        
        Args:
            slot_date: Date of the availability slot
            start_time: Start time of slot
            end_time: End time of slot  
            existing_slots: Existing availability slots for same date
            opening_hours: Opening hours for that day (if any)
            current_id: ID of current slot being edited
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Create datetime objects
        slot_start = cls.BANGKOK_TZ.localize(datetime.combine(slot_date, start_time))
        slot_end = cls.BANGKOK_TZ.localize(datetime.combine(slot_date, end_time))
        current_dt = cls.get_current_time()
        
        # Basic validation
        if start_time >= end_time:
            errors.append(ValidationError(
                type=ConflictType.INVALID_ORDER,
                field="time_range",
                message="Endzeit muss nach der Startzeit liegen",
                suggestions=["Prüfen Sie die eingegebenen Zeiten"]
            ))
            return errors
        
        # Past date validation
        if slot_start < current_dt:
            severity = "error" if slot_date < current_dt.date() else "warning"
            errors.append(ValidationError(
                type=ConflictType.PAST_DATE,
                field="slot_datetime",
                message="Verfügbarkeits-Slot liegt in der Vergangenheit",
                severity=severity
            ))
        
        # Business hours validation
        if opening_hours:
            within_hours = cls._is_within_opening_hours(start_time, end_time, opening_hours)
            if not within_hours:
                errors.append(ValidationError(
                    type=ConflictType.BUSINESS_HOURS,
                    field="time_range",
                    message="Verfügbarkeits-Slot liegt außerhalb der Öffnungszeiten",
                    severity="warning",
                    suggestions=["Prüfen Sie die Öffnungszeiten für diesen Tag"]
                ))
        
        # Overlap validation
        if existing_slots:
            current_slot = TimeSlot(slot_start, slot_end, "availability", current_id)
            overlaps = cls._find_overlaps(current_slot, existing_slots, exclude_id=current_id)
            
            for overlap in overlaps:
                errors.append(ValidationError(
                    type=ConflictType.OVERLAP,
                    field="time_range",
                    message=f"Überschneidung mit bestehendem Slot: {overlap.start_datetime.strftime('%H:%M')}-{overlap.end_datetime.strftime('%H:%M')}",
                    suggestions=["Passen Sie die Zeit an oder löschen Sie den anderen Slot"]
                ))
        
        # Minimum gap validation
        if existing_slots:
            gaps = cls._check_minimum_gaps(
                TimeSlot(slot_start, slot_end, "availability"),
                existing_slots,
                exclude_id=current_id
            )
            
            for gap_error in gaps:
                errors.append(gap_error)
        
        return errors
    
    @classmethod
    def suggest_optimal_times(cls, target_date: date, duration_minutes: int,
                            existing_slots: List[TimeSlot] = None,
                            opening_hours: List[str] = None) -> List[Dict[str, Any]]:
        """
        Suggest optimal time slots for a given date
        
        Args:
            target_date: Target date for suggestions
            duration_minutes: Desired duration in minutes
            existing_slots: Existing slots to avoid
            opening_hours: Available opening hours
        
        Returns:
            List of suggested time slots with confidence scores
        """
        suggestions = []
        
        # Use opening hours or default business hours
        if opening_hours:
            available_periods = cls._parse_opening_hours(opening_hours)
        else:
            available_periods = [(cls.WORKING_HOURS_START, cls.WORKING_HOURS_END)]
        
        for start_time, end_time in available_periods:
            current_time = start_time
            
            while True:
                # Calculate slot end time
                slot_start = current_time
                slot_end_dt = datetime.combine(date.today(), current_time) + timedelta(minutes=duration_minutes)
                slot_end = slot_end_dt.time()
                
                # Check if slot fits in this period
                if slot_end > end_time:
                    break
                
                # Create test slot
                test_slot = TimeSlot(
                    cls.BANGKOK_TZ.localize(datetime.combine(target_date, slot_start)),
                    cls.BANGKOK_TZ.localize(datetime.combine(target_date, slot_end))
                )
                
                # Check for conflicts
                conflicts = cls._find_overlaps(test_slot, existing_slots or [])
                gap_errors = cls._check_minimum_gaps(test_slot, existing_slots or [])
                
                if not conflicts and not gap_errors:
                    confidence = cls._calculate_confidence_score(slot_start, slot_end)
                    suggestions.append({
                        'start_time': slot_start.strftime('%H:%M'),
                        'end_time': slot_end.strftime('%H:%M'),
                        'confidence': confidence,
                        'reason': cls._get_suggestion_reason(slot_start, confidence)
                    })
                
                # Move to next possible slot (15-minute intervals)
                current_time = (datetime.combine(date.today(), current_time) + timedelta(minutes=15)).time()
        
        # Sort by confidence score
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:5]  # Return top 5 suggestions
    
    @staticmethod
    def _find_overlaps(target_slot: TimeSlot, existing_slots: List[TimeSlot],
                      exclude_id: Optional[int] = None) -> List[TimeSlot]:
        """Find overlapping slots"""
        overlaps = []
        
        for slot in existing_slots:
            if exclude_id and slot.id == exclude_id:
                continue
            
            # Check for overlap
            if (target_slot.start_datetime < slot.end_datetime and 
                target_slot.end_datetime > slot.start_datetime):
                overlaps.append(slot)
        
        return overlaps
    
    @classmethod
    def _check_minimum_gaps(cls, target_slot: TimeSlot, existing_slots: List[TimeSlot],
                           exclude_id: Optional[int] = None) -> List[ValidationError]:
        """Check minimum gaps between slots"""
        errors = []
        min_gap = timedelta(minutes=cls.MIN_GAP_BETWEEN_SLOTS)
        
        for slot in existing_slots:
            if exclude_id and slot.id == exclude_id:
                continue
            
            # Check gap before target slot
            if slot.end_datetime <= target_slot.start_datetime:
                gap = target_slot.start_datetime - slot.end_datetime
                if gap < min_gap:
                    errors.append(ValidationError(
                        type=ConflictType.GAP_TOO_SMALL,
                        field="time_range",
                        message=f"Zu kleiner Abstand zum vorherigen Slot ({gap.total_seconds()//60:.0f} min)",
                        severity="warning",
                        suggestions=[f"Mindestabstand: {cls.MIN_GAP_BETWEEN_SLOTS} Minuten"]
                    ))
            
            # Check gap after target slot  
            elif target_slot.end_datetime <= slot.start_datetime:
                gap = slot.start_datetime - target_slot.end_datetime
                if gap < min_gap:
                    errors.append(ValidationError(
                        type=ConflictType.GAP_TOO_SMALL,
                        field="time_range",
                        message=f"Zu kleiner Abstand zum nächsten Slot ({gap.total_seconds()//60:.0f} min)",
                        severity="warning",
                        suggestions=[f"Mindestabstand: {cls.MIN_GAP_BETWEEN_SLOTS} Minuten"]
                    ))
        
        return errors
    
    @staticmethod
    def _is_within_opening_hours(start_time: time, end_time: time, 
                               opening_hours: List[str]) -> bool:
        """Check if time slot is within opening hours"""
        for hours_str in opening_hours:
            try:
                open_start_str, open_end_str = hours_str.split('-')
                open_start = time.fromisoformat(open_start_str.strip())
                open_end = time.fromisoformat(open_end_str.strip())
                
                if start_time >= open_start and end_time <= open_end:
                    return True
            except ValueError:
                continue
        
        return False
    
    @staticmethod
    def _parse_opening_hours(opening_hours: List[str]) -> List[Tuple[time, time]]:
        """Parse opening hours into time tuples"""
        periods = []
        for hours_str in opening_hours:
            try:
                start_str, end_str = hours_str.split('-')
                start_time = time.fromisoformat(start_str.strip())
                end_time = time.fromisoformat(end_str.strip())
                periods.append((start_time, end_time))
            except ValueError:
                continue
        return periods
    
    @staticmethod
    def _calculate_confidence_score(start_time: time, end_time: time) -> int:
        """Calculate confidence score for time suggestion (0-100)"""
        score = 50  # Base score
        
        # Prefer mid-morning or early afternoon
        if time(9, 0) <= start_time <= time(11, 0):
            score += 20
        elif time(14, 0) <= start_time <= time(16, 0):
            score += 15
        elif time(8, 0) <= start_time <= time(9, 0):
            score += 10
        elif time(16, 0) <= start_time <= time(17, 0):
            score += 5
        
        # Penalize very early or late times
        if start_time < time(8, 0) or end_time > time(18, 0):
            score -= 20
        
        # Prefer round times (e.g., 9:00 vs 9:15)
        if start_time.minute == 0:
            score += 10
        elif start_time.minute == 30:
            score += 5
        
        return max(0, min(100, score))
    
    @staticmethod
    def _get_suggestion_reason(start_time: time, confidence: int) -> str:
        """Get human-readable reason for suggestion"""
        if confidence >= 80:
            return "Optimal verfügbar"
        elif confidence >= 60:
            return "Gut verfügbar"
        elif confidence >= 40:
            return "Verfügbar"
        else:
            return "Eingeschränkt verfügbar"