from datetime import date, datetime, time
from typing import Optional, List, Dict
from sqlmodel import Session, select
from app.models import Status, StatusType, ChangeLog
from app.database import engine
from app.services.datetime_validator import DateTimeValidator, ValidationError, TimeSlot
from app.services.cache import cache, cached, invalidate_cache_on_update
import json
import pytz


class StatusService:
    @staticmethod
    @cached(ttl_seconds=60)  # Cache für 1 Minute
    def get_current_status() -> Optional[Status]:
        """Get the current active status"""
        with Session(engine) as session:
            # Get latest status
            statement = select(Status).order_by(Status.created_at.desc())
            status = session.exec(statement).first()
            
            if not status:
                # Create default status if none exists
                status = Status(type=StatusType.ANWESEND)
                session.add(status)
                session.commit()
                session.refresh(status)
            
            # Check if status is still valid
            today = date.today()
            if status.date_to and status.date_to < today:
                # Status expired, set to present
                status = Status(type=StatusType.ANWESEND)
                session.add(status)
                session.commit()
                session.refresh(status)
            
            return status
    
    @staticmethod
    def validate_status_update(
        status_type: StatusType,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        description: Optional[str] = None,
        next_return: Optional[date] = None,
        current_id: Optional[int] = None
    ) -> List[ValidationError]:
        """Validate status update with comprehensive checks"""
        errors = []
        
        # For absence statuses, require dates
        if status_type != StatusType.ANWESEND:
            if not date_from:
                errors.append(ValidationError(
                    type="missing_required_field",
                    field="date_from",
                    message="Startdatum ist für Abwesenheiten erforderlich",
                    severity="error"
                ))
                return errors
            
            if not date_to:
                errors.append(ValidationError(
                    type="missing_required_field",
                    field="date_to",
                    message="Enddatum ist für Abwesenheiten erforderlich",
                    severity="error"
                ))
                return errors
            
            # Use datetime validator for comprehensive validation
            start_time = time(0, 0)  # Start of day
            end_time = time(23, 59)  # End of day
            
            # Get existing absences to check for conflicts
            existing_absences = StatusService._get_existing_absences(exclude_id=current_id)
            
            validation_errors = DateTimeValidator.validate_absence_period(
                date_from, start_time, date_to, end_time,
                existing_absences, current_id
            )
            
            errors.extend(validation_errors)
        
        # Validate next_return date
        if next_return:
            if date_to and next_return <= date_to:
                errors.append(ValidationError(
                    type="invalid_order",
                    field="next_return",
                    message="Rückkehrdatum muss nach dem Enddatum liegen",
                    severity="error",
                    suggestions=["Wählen Sie ein Datum nach dem Abwesenheitsende"]
                ))
        
        # Validate description length
        if description and len(description.strip()) > 500:
            errors.append(ValidationError(
                type="value_too_long",
                field="description",
                message="Beschreibung ist zu lang (max. 500 Zeichen)",
                severity="error"
            ))
        
        return errors
    
    @staticmethod
    def update_status(
        status_type: StatusType,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        description: Optional[str] = None,
        next_return: Optional[date] = None,
        admin_user: str = "admin",
        admin_ip: Optional[str] = None,
        validate: bool = True
    ) -> tuple[Optional[Status], List[ValidationError]]:
        """Update the current status with validation and change logging"""
        
        # Validate if requested
        if validate:
            validation_errors = StatusService.validate_status_update(
                status_type, date_from, date_to, description, next_return
            )
            
            # Return errors if validation failed
            critical_errors = [e for e in validation_errors if e.severity == "error"]
            if critical_errors:
                return None, validation_errors
        
        with Session(engine) as session:
            # Get current status for change logging
            current_status = StatusService.get_current_status()
            old_data = None
            if current_status:
                old_data = {
                    "type": current_status.type,
                    "date_from": current_status.date_from.isoformat() if current_status.date_from else None,
                    "date_to": current_status.date_to.isoformat() if current_status.date_to else None,
                    "description": current_status.description,
                    "next_return": current_status.next_return.isoformat() if current_status.next_return else None
                }
            
            # Create new status
            status = Status(
                type=status_type,
                date_from=date_from,
                date_to=date_to,
                description=description.strip() if description else None,
                next_return=next_return,
                updated_at=datetime.utcnow()
            )
            session.add(status)
            session.flush()  # Get ID before commit
            
            # Log change
            new_data = {
                "type": status.type,
                "date_from": status.date_from.isoformat() if status.date_from else None,
                "date_to": status.date_to.isoformat() if status.date_to else None,
                "description": status.description,
                "next_return": status.next_return.isoformat() if status.next_return else None
            }
            
            change_log = ChangeLog(
                table_name="Status",
                record_id=status.id,
                action="create" if not current_status else "update",
                old_data=old_data,
                new_data=new_data,
                admin_user=admin_user,
                admin_ip=admin_ip,
                rollback_data=old_data  # Store for potential rollback
            )
            session.add(change_log)
            
            session.commit()
            session.refresh(status)
            
            return status, validation_errors if validate else []
    
    @staticmethod
    def is_available() -> bool:
        """Check if currently available"""
        status = StatusService.get_current_status()
        return status.type == StatusType.ANWESEND if status else True
    
    @staticmethod
    def _get_existing_absences(exclude_id: Optional[int] = None) -> List[TimeSlot]:
        """Get existing absence periods as TimeSlot objects"""
        absences = []
        
        with Session(engine) as session:
            statement = select(Status).where(
                Status.type != StatusType.ANWESEND,
                Status.date_from.is_not(None),
                Status.date_to.is_not(None)
            )
            
            if exclude_id:
                statement = statement.where(Status.id != exclude_id)
            
            statuses = session.exec(statement).all()
            
            for status in statuses:
                if status.date_from and status.date_to:
                    start_dt = DateTimeValidator.BANGKOK_TZ.localize(
                        datetime.combine(status.date_from, time(0, 0))
                    )
                    end_dt = DateTimeValidator.BANGKOK_TZ.localize(
                        datetime.combine(status.date_to, time(23, 59))
                    )
                    
                    absences.append(TimeSlot(
                        start_dt, end_dt, 
                        type=status.type,
                        id=status.id,
                        description=status.description or f"{status.type} ({status.date_from} - {status.date_to})"
                    ))
        
        return absences
    
    @staticmethod
    def get_status_history(limit: int = 10) -> List[Status]:
        """Get status history"""
        with Session(engine) as session:
            statement = select(Status).order_by(Status.created_at.desc()).limit(limit)
            return list(session.exec(statement).all())
    
    @staticmethod
    def rollback_status(change_id: int, admin_user: str = "admin", admin_ip: Optional[str] = None) -> bool:
        """Rollback a status change using change log"""
        with Session(engine) as session:
            # Find the change log entry
            change_log = session.get(ChangeLog, change_id)
            if not change_log or change_log.table_name != "Status":
                return False
            
            if change_log.is_rolled_back:
                return False  # Already rolled back
            
            # Get rollback data
            rollback_data = change_log.rollback_data
            if not rollback_data:
                return False
            
            # Create status from rollback data
            status = Status(
                type=StatusType(rollback_data["type"]),
                date_from=date.fromisoformat(rollback_data["date_from"]) if rollback_data.get("date_from") else None,
                date_to=date.fromisoformat(rollback_data["date_to"]) if rollback_data.get("date_to") else None,
                description=rollback_data.get("description"),
                next_return=date.fromisoformat(rollback_data["next_return"]) if rollback_data.get("next_return") else None,
                updated_at=datetime.utcnow()
            )
            
            session.add(status)
            session.flush()
            
            # Mark original change as rolled back
            change_log.is_rolled_back = True
            
            # Log the rollback
            rollback_log = ChangeLog(
                table_name="Status",
                record_id=status.id,
                action="rollback",
                old_data=change_log.new_data,
                new_data=rollback_data,
                admin_user=admin_user,
                admin_ip=admin_ip,
                rollback_data=change_log.new_data
            )
            session.add(rollback_log)
            
            session.commit()
            return True
    
    @staticmethod
    def get_enhanced_status_info(lang: str = 'th') -> Dict:
        """
        Erweiterte Status-Informationen mit Next Opening Integration
        Optimiert für Thai-First Ausgabe
        """
        # Import hier um zirkuläre Imports zu vermeiden
        from app.services.next_opening_calculator import NextOpeningCalculator
        
        bangkok_tz = pytz.timezone('Asia/Bangkok')
        now = datetime.now(bangkok_tz)
        
        # Aktueller Status
        current_status = StatusService.get_current_status()
        
        # Smart Status Message vom Calculator
        smart_status = NextOpeningCalculator.get_smart_status_message(lang)
        
        # Today Status Details
        today_status = NextOpeningCalculator.get_today_status()
        
        # Next Opening Info
        next_opening = NextOpeningCalculator.get_next_opening()
        
        # Closure Explanation
        closure_explanation = NextOpeningCalculator.get_closure_explanation(lang)
        
        return {
            'current_status': {
                'type': current_status.type.value if current_status else 'ANWESEND',
                'date_from': current_status.date_from.isoformat() if current_status and current_status.date_from else None,
                'date_to': current_status.date_to.isoformat() if current_status and current_status.date_to else None,
                'description': current_status.description if current_status else None,
                'next_return': current_status.next_return.isoformat() if current_status and current_status.next_return else None
            },
            'smart_status': smart_status,
            'today_status': today_status.to_dict(),
            'next_opening': next_opening.to_dict() if next_opening else None,
            'closure_explanation': closure_explanation,
            'current_time_bangkok': now.strftime('%H:%M'),
            'current_date_bangkok': now.date().isoformat(),
            'is_available': current_status.type == StatusType.ANWESEND if current_status else True
        }
    
    @staticmethod 
    def get_thai_first_status_display(lang: str = 'th') -> Dict:
        """
        Thai-First Status Display für Homepage und Kiosk
        Optimiert für thailändische Nutzer
        """
        enhanced_info = StatusService.get_enhanced_status_info(lang)
        smart_status = enhanced_info['smart_status']
        
        # Thai-spezifische Anpassungen
        display_info = {
            'primary_message': smart_status['main_message'],
            'secondary_message': smart_status['next_opening_message'],
            'status_badge': {
                'type': smart_status['status_type'],
                'is_open': smart_status['is_open'],
                'opens_soon': smart_status['opens_soon']
            },
            'time_info': {
                'current_time': enhanced_info['current_time_bangkok'],
                'current_date': enhanced_info['current_date_bangkok'],
                'remaining_slots': enhanced_info['today_status']['remaining_slots'],
                'minutes_until_next': enhanced_info['today_status']['minutes_until_next']
            },
            'next_opening_details': enhanced_info['next_opening'],
            'closure_reason': enhanced_info['closure_explanation']['reason'],
            'closure_note': enhanced_info['closure_explanation']['note']
        }
        
        return display_info