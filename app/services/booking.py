"""
Booking Service Layer
Handles all booking business logic

IMPORTANT: This service is prepared but NOT ACTIVATED
Enable via FEATURE_BOOKING=true in environment
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, time, timedelta
from sqlmodel import Session, select, and_, or_, func
import secrets
import hashlib
from app.models_booking import (
    Booking, BookingStatus, BookingSlot, BookingService,
    Patient, PatientType, ContactMethod, ServiceType,
    BookingNotification, BookingRule, WaitingList,
    BookingSlotTemplate, BookingStatistics
)
from app.services.i18n import I18nService
import pytz


class BookingServiceError(Exception):
    """Base exception for booking service"""
    pass


class SlotNotAvailableError(BookingServiceError):
    """Raised when requested slot is not available"""
    pass


class BookingValidationError(BookingServiceError):
    """Raised when booking data is invalid"""
    pass


class BookingManager:
    """Main booking service manager"""
    
    def __init__(self, session: Session, timezone: str = "Asia/Bangkok"):
        self.session = session
        self.timezone = pytz.timezone(timezone)
    
    def create_booking(
        self,
        service_id: int,
        booking_date: date,
        booking_time: time,
        contact_phone: str,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        line_user_id: Optional[str] = None,
        preferred_language: str = "th",
        patient_notes: Optional[str] = None,
        family_members: Optional[List[Dict[str, str]]] = None
    ) -> Booking:
        """Create a new booking"""
        
        # Validate service
        service = self.session.get(BookingService, service_id)
        if not service or not service.active:
            raise BookingValidationError("Service not available")
        
        # Check slot availability
        slot = self._find_or_create_slot(service, booking_date, booking_time)
        if not self._is_slot_available(slot):
            raise SlotNotAvailableError("Requested time slot is not available")
        
        # Find or create patient
        patient = self._find_or_create_patient(
            phone=contact_phone,
            first_name=first_name,
            last_name=last_name,
            email=email,
            line_user_id=line_user_id,
            preferred_language=preferred_language
        )
        
        # Create booking
        booking = Booking(
            booking_reference=Booking.generate_reference(booking_date),
            patient_id=patient.id,
            service_id=service_id,
            slot_id=slot.id,
            booking_date=booking_date,
            booking_time=booking_time,
            duration_minutes=service.duration_minutes,
            patient_type=PatientType.APPOINTMENT,
            status=BookingStatus.PENDING,
            contact_phone=self._encrypt_data(contact_phone),
            contact_line=line_user_id,
            contact_method=ContactMethod.LINE if line_user_id else ContactMethod.SMS,
            buddhist_date=self._to_buddhist_date(booking_date),
            patient_notes=patient_notes,
            confirmation_code=Booking.generate_confirmation_code(),
            family_members=family_members or [],
            source="web"
        )
        
        self.session.add(booking)
        
        # Update slot count
        slot.booked_count += 1
        
        # Handle family bookings
        if family_members:
            booking.family_booking_id = secrets.token_hex(8)
            # Create bookings for family members if needed
        
        self.session.commit()
        
        # Send confirmation
        self._send_booking_confirmation(booking)
        
        return booking
    
    def confirm_booking(self, booking_reference: str, confirmation_code: str) -> Booking:
        """Confirm a booking with code"""
        booking = self._get_booking_by_reference(booking_reference)
        
        if booking.confirmation_code != confirmation_code:
            raise BookingValidationError("Invalid confirmation code")
        
        if booking.status != BookingStatus.PENDING:
            raise BookingValidationError("Booking already confirmed or cancelled")
        
        booking.status = BookingStatus.CONFIRMED
        booking.confirmed_at = datetime.utcnow()
        booking.confirmed_via = "web"
        
        self.session.commit()
        
        return booking
    
    def cancel_booking(
        self, 
        booking_reference: str, 
        reason: Optional[str] = None,
        cancelled_by: str = "patient"
    ) -> Booking:
        """Cancel a booking"""
        booking = self._get_booking_by_reference(booking_reference)
        
        if booking.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
            raise BookingValidationError("Cannot cancel completed or already cancelled booking")
        
        # Update status
        if cancelled_by == "lab":
            booking.status = BookingStatus.CANCELLED_BY_LAB
        else:
            booking.status = BookingStatus.CANCELLED
        
        booking.internal_notes = f"Cancelled by {cancelled_by}: {reason}" if reason else None
        
        # Free up the slot
        if booking.slot:
            booking.slot.booked_count = max(0, booking.slot.booked_count - 1)
        
        self.session.commit()
        
        # Notify waiting list
        self._notify_waiting_list(booking.service_id, booking.booking_date)
        
        return booking
    
    def reschedule_booking(
        self,
        booking_reference: str,
        new_date: date,
        new_time: time,
        reason: Optional[str] = None
    ) -> Booking:
        """Reschedule a booking to new date/time"""
        old_booking = self._get_booking_by_reference(booking_reference)
        
        if old_booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise BookingValidationError("Cannot reschedule this booking")
        
        # Create new booking
        new_booking = self.create_booking(
            service_id=old_booking.service_id,
            booking_date=new_date,
            booking_time=new_time,
            contact_phone=self._decrypt_data(old_booking.contact_phone),
            first_name=self._decrypt_data(old_booking.patient.first_name_encrypted),
            last_name=self._decrypt_data(old_booking.patient.last_name_encrypted),
            email=None,  # Would need to decrypt if stored
            line_user_id=old_booking.contact_line,
            preferred_language=old_booking.patient.preferred_language,
            patient_notes=old_booking.patient_notes
        )
        
        # Link bookings
        old_booking.status = BookingStatus.RESCHEDULED
        old_booking.rescheduled_to = new_booking.id
        old_booking.reschedule_reason = reason
        
        new_booking.rescheduled_from = old_booking.id
        
        # Free up old slot
        if old_booking.slot:
            old_booking.slot.booked_count = max(0, old_booking.slot.booked_count - 1)
        
        self.session.commit()
        
        return new_booking
    
    def get_available_slots(
        self,
        service_id: int,
        start_date: date,
        end_date: date,
        preferred_times: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get available booking slots for date range"""
        service = self.session.get(BookingService, service_id)
        if not service:
            raise BookingValidationError("Service not found")
        
        available_slots = []
        current_date = start_date
        
        while current_date <= end_date:
            # Skip if not an available day for this service
            if current_date.weekday() not in service.available_days:
                current_date += timedelta(days=1)
                continue
            
            # Get slots for this date
            daily_slots = self._get_daily_slots(service, current_date)
            
            for slot_info in daily_slots:
                if self._matches_preferred_time(slot_info['start_time'], preferred_times):
                    available_slots.append({
                        'date': current_date,
                        'buddhist_date': self._to_buddhist_date(current_date),
                        'start_time': slot_info['start_time'],
                        'end_time': slot_info['end_time'],
                        'available_capacity': slot_info['available_capacity'],
                        'total_capacity': slot_info['total_capacity']
                    })
            
            current_date += timedelta(days=1)
        
        return available_slots
    
    def check_in_patient(self, booking_reference: str) -> Tuple[Booking, str]:
        """Check in patient and assign queue number"""
        booking = self._get_booking_by_reference(booking_reference)
        
        if booking.status != BookingStatus.CONFIRMED:
            raise BookingValidationError("Booking must be confirmed before check-in")
        
        # Generate queue number for today
        queue_number = self._generate_queue_number(booking.booking_date)
        
        booking.status = BookingStatus.CHECKED_IN
        booking.checked_in_at = datetime.utcnow()
        booking.queue_number = queue_number
        booking.estimated_wait_minutes = self._estimate_wait_time(booking)
        
        self.session.commit()
        
        return booking, queue_number
    
    def add_to_waiting_list(
        self,
        service_id: int,
        patient_id: int,
        date_from: date,
        date_to: date,
        preferred_times: List[str],
        contact_method: ContactMethod = ContactMethod.LINE
    ) -> WaitingList:
        """Add patient to waiting list"""
        waiting_entry = WaitingList(
            patient_id=patient_id,
            service_id=service_id,
            preferred_date_from=date_from,
            preferred_date_to=date_to,
            preferred_times=preferred_times,
            contact_method=contact_method,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        self.session.add(waiting_entry)
        self.session.commit()
        
        return waiting_entry
    
    def get_daily_statistics(self, stat_date: date) -> Dict[str, Any]:
        """Get booking statistics for a specific date"""
        stats = self.session.exec(
            select(BookingStatistics)
            .where(BookingStatistics.stat_date == stat_date)
        ).all()
        
        total_stats = {
            'date': stat_date,
            'buddhist_date': self._to_buddhist_date(stat_date),
            'total_bookings': sum(s.total_bookings for s in stats),
            'confirmed': sum(s.confirmed_bookings for s in stats),
            'completed': sum(s.completed_bookings for s in stats),
            'no_shows': sum(s.no_shows for s in stats),
            'cancellations': sum(s.cancellations for s in stats),
            'walk_ins': sum(s.walk_ins for s in stats),
            'utilization_rate': 0.0,
            'by_service': []
        }
        
        # Calculate utilization
        total_slots = sum(s.total_slots for s in stats)
        utilized_slots = sum(s.utilized_slots for s in stats)
        if total_slots > 0:
            total_stats['utilization_rate'] = (utilized_slots / total_slots) * 100
        
        # Add per-service stats
        for stat in stats:
            if stat.service_id:
                service = self.session.get(BookingService, stat.service_id)
                total_stats['by_service'].append({
                    'service': service.name if service else 'Unknown',
                    'bookings': stat.total_bookings,
                    'completed': stat.completed_bookings,
                    'no_shows': stat.no_shows
                })
        
        return total_stats
    
    # Private helper methods
    
    def _find_or_create_patient(
        self,
        phone: str,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        line_user_id: Optional[str] = None,
        preferred_language: str = "th"
    ) -> Patient:
        """Find existing patient or create new one"""
        phone_hash = Patient.hash_identifier(phone)
        
        # Try to find by phone hash
        patient = self.session.exec(
            select(Patient).where(Patient.phone_hash == phone_hash)
        ).first()
        
        if not patient:
            # Create new patient
            patient = Patient(
                anonymous_id=Patient.generate_anonymous_id(phone, email),
                first_name_encrypted=self._encrypt_data(first_name),
                last_name_encrypted=self._encrypt_data(last_name),
                phone_hash=phone_hash,
                email_hash=Patient.hash_identifier(email) if email else None,
                line_user_id=line_user_id,
                preferred_language=preferred_language,
                consent_version="1.0",
                consent_given_at=datetime.utcnow(),
                retention_until=datetime.utcnow() + timedelta(days=730)  # 2 years
            )
            self.session.add(patient)
            self.session.commit()
        
        return patient
    
    def _find_or_create_slot(
        self,
        service: BookingService,
        slot_date: date,
        start_time: time
    ) -> BookingSlot:
        """Find existing slot or create new one"""
        # Calculate end time
        end_time = (datetime.combine(date.today(), start_time) + 
                   timedelta(minutes=service.duration_minutes)).time()
        
        # Look for existing slot
        slot = self.session.exec(
            select(BookingSlot)
            .where(
                and_(
                    BookingSlot.slot_date == slot_date,
                    BookingSlot.start_time == start_time,
                    BookingSlot.service_id == service.id
                )
            )
        ).first()
        
        if not slot:
            # Create new slot
            slot = BookingSlot(
                slot_date=slot_date,
                start_time=start_time,
                end_time=end_time,
                service_id=service.id,
                total_capacity=1  # Default, could be from template
            )
            self.session.add(slot)
            self.session.commit()
        
        return slot
    
    def _is_slot_available(self, slot: BookingSlot) -> bool:
        """Check if slot has available capacity"""
        return (
            not slot.is_blocked and 
            slot.booked_count < slot.total_capacity
        )
    
    def _get_booking_by_reference(self, reference: str) -> Booking:
        """Get booking by reference number"""
        booking = self.session.exec(
            select(Booking)
            .where(Booking.booking_reference == reference)
        ).first()
        
        if not booking:
            raise BookingValidationError("Booking not found")
        
        return booking
    
    def _get_daily_slots(
        self,
        service: BookingService,
        slot_date: date
    ) -> List[Dict[str, Any]]:
        """Get all slots for a service on a specific date"""
        # Get templates for this day
        day_of_week = slot_date.weekday()
        templates = self.session.exec(
            select(BookingSlotTemplate)
            .where(
                and_(
                    BookingSlotTemplate.active == True,
                    or_(
                        BookingSlotTemplate.day_of_week == day_of_week,
                        BookingSlotTemplate.day_of_week == None
                    )
                )
            )
        ).all()
        
        slots = []
        for template in templates:
            # Generate slots from template
            current_time = template.start_time
            while current_time < template.end_time:
                end_time = (datetime.combine(date.today(), current_time) + 
                          timedelta(minutes=template.slot_duration_minutes)).time()
                
                # Check existing bookings
                existing_slot = self.session.exec(
                    select(BookingSlot)
                    .where(
                        and_(
                            BookingSlot.slot_date == slot_date,
                            BookingSlot.start_time == current_time,
                            BookingSlot.service_id == service.id
                        )
                    )
                ).first()
                
                if existing_slot:
                    available_capacity = existing_slot.total_capacity - existing_slot.booked_count
                else:
                    available_capacity = template.max_bookings_per_slot
                
                if available_capacity > 0:
                    slots.append({
                        'start_time': current_time,
                        'end_time': end_time,
                        'available_capacity': available_capacity,
                        'total_capacity': template.max_bookings_per_slot
                    })
                
                current_time = end_time
        
        return slots
    
    def _matches_preferred_time(
        self,
        slot_time: time,
        preferred_times: Optional[List[str]]
    ) -> bool:
        """Check if slot matches preferred times"""
        if not preferred_times:
            return True
        
        hour = slot_time.hour
        
        for pref in preferred_times:
            if pref == "morning" and 6 <= hour < 12:
                return True
            elif pref == "afternoon" and 12 <= hour < 18:
                return True
            elif pref == "evening" and 18 <= hour < 22:
                return True
        
        return False
    
    def _to_buddhist_date(self, gregorian_date: date) -> str:
        """Convert Gregorian date to Buddhist Era string"""
        buddhist_year = gregorian_date.year + 543
        thai_months = [
            "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
            "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
            "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
        ]
        month = thai_months[gregorian_date.month - 1]
        return f"{gregorian_date.day} {month} พ.ศ. {buddhist_year}"
    
    def _generate_queue_number(self, booking_date: date) -> str:
        """Generate daily queue number"""
        # Count today's check-ins
        today_count = self.session.exec(
            select(func.count(Booking.id))
            .where(
                and_(
                    Booking.booking_date == booking_date,
                    Booking.queue_number != None
                )
            )
        ).first() or 0
        
        queue_number = today_count + 1
        return f"Q{queue_number:03d}"
    
    def _estimate_wait_time(self, booking: Booking) -> int:
        """Estimate wait time in minutes"""
        # Count pending bookings before this one
        pending_before = self.session.exec(
            select(func.count(Booking.id))
            .where(
                and_(
                    Booking.booking_date == booking.booking_date,
                    Booking.booking_time < booking.booking_time,
                    Booking.status.in_([BookingStatus.CHECKED_IN, BookingStatus.IN_PROGRESS])
                )
            )
        ).first() or 0
        
        # Estimate based on service duration
        service = self.session.get(BookingService, booking.service_id)
        avg_duration = service.duration_minutes if service else 30
        
        return pending_before * avg_duration
    
    def _notify_waiting_list(self, service_id: int, available_date: date):
        """Notify patients on waiting list about available slot"""
        # Get active waiting list entries
        waiting_entries = self.session.exec(
            select(WaitingList)
            .where(
                and_(
                    WaitingList.service_id == service_id,
                    WaitingList.is_active == True,
                    WaitingList.preferred_date_from <= available_date,
                    WaitingList.preferred_date_to >= available_date
                )
            )
            .order_by(WaitingList.created_at)
            .limit(5)  # Notify top 5
        ).all()
        
        for entry in waiting_entries:
            # Send notification (implementation depends on notification service)
            entry.notified_count += 1
            entry.last_notified_at = datetime.utcnow()
    
    def _send_booking_confirmation(self, booking: Booking):
        """Send booking confirmation notification"""
        # Create notification record
        notification = BookingNotification(
            booking_id=booking.id,
            notification_type="confirmation",
            channel=booking.contact_method,
            message=self._generate_confirmation_message(booking),
            language=booking.patient.preferred_language if booking.patient else "th"
        )
        
        self.session.add(notification)
        self.session.commit()
        
        # Actual sending would be handled by notification service
        # This is just a placeholder
        notification.sent_at = datetime.utcnow()
        self.session.commit()
    
    def _generate_confirmation_message(self, booking: Booking) -> str:
        """Generate confirmation message in patient's language"""
        lang = booking.patient.preferred_language if booking.patient else "th"
        service = self.session.get(BookingService, booking.service_id)
        
        if lang == "th":
            return (
                f"ยืนยันการนัดหมาย {booking.booking_reference}\n"
                f"บริการ: {service.name.get('th', 'บริการ')}\n"
                f"วันที่: {booking.buddhist_date}\n"
                f"เวลา: {booking.booking_time.strftime('%H:%M')}\n"
                f"รหัสยืนยัน: {booking.confirmation_code}"
            )
        else:
            return (
                f"Booking Confirmation {booking.booking_reference}\n"
                f"Service: {service.name.get('en', 'Service')}\n"
                f"Date: {booking.booking_date}\n"
                f"Time: {booking.booking_time.strftime('%H:%M')}\n"
                f"Confirmation Code: {booking.confirmation_code}"
            )
    
    def _encrypt_data(self, data: str) -> str:
        """Simple encryption placeholder - should use proper encryption"""
        # In production, use proper encryption library
        return f"ENC:{data}"
    
    def _decrypt_data(self, encrypted: str) -> str:
        """Simple decryption placeholder - should use proper decryption"""
        # In production, use proper decryption library
        if encrypted and encrypted.startswith("ENC:"):
            return encrypted[4:]
        return encrypted or ""