"""
Booking System Models for QR-Info-Portal
Thai-specific appointment booking for medical laboratory

IMPORTANT: This module is prepared but NOT ACTIVATED
Enable via FEATURE_BOOKING=true in environment
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, time, timedelta
from sqlmodel import Field, SQLModel, Column, Relationship
from sqlalchemy import JSON, UniqueConstraint, Index
from enum import Enum
import hashlib
import secrets


class BookingStatus(str, Enum):
    """Booking status states"""
    PENDING = "PENDING"  # Initial booking
    CONFIRMED = "CONFIRMED"  # Confirmed via LINE/SMS
    REMINDER_SENT = "REMINDER_SENT"  # Reminder sent
    CHECKED_IN = "CHECKED_IN"  # Patient arrived
    IN_PROGRESS = "IN_PROGRESS"  # Service being provided
    COMPLETED = "COMPLETED"  # Service completed
    NO_SHOW = "NO_SHOW"  # Did not arrive
    CANCELLED = "CANCELLED"  # Cancelled by patient
    CANCELLED_BY_LAB = "CANCELLED_BY_LAB"  # Cancelled by lab
    RESCHEDULED = "RESCHEDULED"  # Moved to different time


class ServiceType(str, Enum):
    """Types of services offered"""
    BLOOD_TEST = "BLOOD_TEST"  # เจาะเลือด
    CONSULTATION = "CONSULTATION"  # ปรึกษา
    RESULT_PICKUP = "RESULT_PICKUP"  # รับผลตรวจ
    VACCINATION = "VACCINATION"  # ฉีดวัคซีน
    HEALTH_CHECK = "HEALTH_CHECK"  # ตรวจสุขภาพ
    OTHER = "OTHER"  # อื่นๆ


class PatientType(str, Enum):
    """Patient categorization"""
    WALK_IN = "WALK_IN"  # ไม่นัดหมาย
    APPOINTMENT = "APPOINTMENT"  # นัดหมาย
    URGENT = "URGENT"  # เร่งด่วน
    VIP = "VIP"  # VIP customer
    CORPORATE = "CORPORATE"  # Corporate/Insurance


class ContactMethod(str, Enum):
    """Preferred contact methods"""
    LINE = "LINE"  # Most popular in Thailand
    SMS = "SMS"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"


class CalendarSystem(str, Enum):
    """Calendar systems for Thailand"""
    GREGORIAN = "GREGORIAN"  # Western calendar
    BUDDHIST = "BUDDHIST"  # พ.ศ. Buddhist Era


class BookingService(SQLModel, table=True):
    """Service catalog with duration and requirements"""
    __tablename__ = "booking_services"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    service_type: ServiceType = Field(index=True)
    name: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))  # {"th": "เจาะเลือด", "en": "Blood Test", "de": "Bluttest"}
    description: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    duration_minutes: int = Field(default=30)
    buffer_minutes: int = Field(default=10)  # Time between appointments
    requires_fasting: bool = Field(default=False)
    preparation_instructions: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    max_daily_capacity: Optional[int] = Field(default=None)  # Limit per day
    available_days: List[int] = Field(default_factory=lambda: [0,1,2,3,4], sa_column=Column(JSON))  # 0=Mon, 6=Sun
    price_thb: Optional[float] = Field(default=None)
    requires_appointment: bool = Field(default=True)
    walk_in_allowed: bool = Field(default=True)
    active: bool = Field(default=True)
    sort_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BookingSlotTemplate(SQLModel, table=True):
    """Configurable time slots for appointments"""
    __tablename__ = "booking_slot_templates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field()  # "Morning slots", "Afternoon slots"
    day_of_week: Optional[int] = Field(default=None, index=True)  # None = all days, 0-6 = specific day
    start_time: time = Field()
    end_time: time = Field()
    slot_duration_minutes: int = Field(default=30)
    max_bookings_per_slot: int = Field(default=1)
    service_types: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # Which services can use this
    active: bool = Field(default=True)
    valid_from: Optional[date] = Field(default=None)
    valid_until: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BookingSlot(SQLModel, table=True):
    """Actual booking slots (generated from templates)"""
    __tablename__ = "booking_slots"
    __table_args__ = (
        UniqueConstraint("slot_date", "start_time", "service_id"),
        Index("idx_slot_date_time", "slot_date", "start_time"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    slot_date: date = Field(index=True)
    start_time: time = Field()
    end_time: time = Field()
    service_id: Optional[int] = Field(default=None, foreign_key="booking_services.id")
    template_id: Optional[int] = Field(default=None, foreign_key="booking_slot_templates.id")
    total_capacity: int = Field(default=1)
    booked_count: int = Field(default=0)
    walk_in_count: int = Field(default=0)
    is_blocked: bool = Field(default=False)  # Manual block
    block_reason: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    service: Optional["BookingService"] = Relationship(back_populates="slots")
    bookings: List["Booking"] = Relationship(back_populates="slot")


class Patient(SQLModel, table=True):
    """Patient information (PDPA compliant)"""
    __tablename__ = "patients"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Anonymous identifier (for repeat visits without storing personal data)
    anonymous_id: str = Field(unique=True, index=True)  # Generated hash
    
    # Basic info (encrypted at rest)
    first_name_encrypted: Optional[str] = Field(default=None)  # Encrypted
    last_name_encrypted: Optional[str] = Field(default=None)  # Encrypted
    phone_hash: str = Field(index=True)  # Hashed for lookup
    email_hash: Optional[str] = Field(default=None, index=True)  # Hashed
    
    # Thai-specific fields
    line_user_id: Optional[str] = Field(default=None, index=True)  # LINE UserID
    thai_id_hash: Optional[str] = Field(default=None)  # Hashed Thai National ID
    passport_hash: Optional[str] = Field(default=None)  # For foreigners
    
    # Preferences
    preferred_language: str = Field(default="th")
    preferred_contact: ContactMethod = Field(default=ContactMethod.LINE)
    calendar_system: CalendarSystem = Field(default=CalendarSystem.BUDDHIST)
    
    # Medical flags (no details)
    requires_special_care: bool = Field(default=False)
    is_vip: bool = Field(default=False)
    
    # Family linking (for group bookings)
    family_group_id: Optional[str] = Field(default=None, index=True)
    is_family_head: bool = Field(default=False)
    
    # Consent tracking
    consent_version: str = Field()
    consent_given_at: datetime = Field()
    marketing_consent: bool = Field(default=False)
    
    # Data retention
    last_visit: Optional[datetime] = Field(default=None)
    retention_until: datetime = Field()  # Auto-delete after this
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    bookings: List["Booking"] = Relationship(back_populates="patient")
    
    @staticmethod
    def generate_anonymous_id(phone: str, email: Optional[str] = None) -> str:
        """Generate anonymous ID from contact info"""
        data = f"{phone}:{email or ''}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    @staticmethod
    def hash_identifier(identifier: str) -> str:
        """Hash sensitive identifiers"""
        return hashlib.sha256(identifier.encode()).hexdigest()


class Booking(SQLModel, table=True):
    """Appointment bookings"""
    __tablename__ = "bookings"
    __table_args__ = (
        Index("idx_booking_date_time", "booking_date", "booking_time"),
        Index("idx_patient_date", "patient_id", "booking_date"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    booking_reference: str = Field(unique=True, index=True)  # REF-YYYYMMDD-XXXX
    
    # Relationships
    patient_id: Optional[int] = Field(default=None, foreign_key="patients.id")
    service_id: int = Field(foreign_key="booking_services.id")
    slot_id: Optional[int] = Field(default=None, foreign_key="booking_slots.id")
    
    # Booking details
    booking_date: date = Field(index=True)
    booking_time: time = Field()
    duration_minutes: int = Field()
    patient_type: PatientType = Field(default=PatientType.APPOINTMENT)
    status: BookingStatus = Field(default=BookingStatus.PENDING, index=True)
    
    # Contact for this booking (may differ from patient defaults)
    contact_phone: Optional[str] = Field(default=None)  # Encrypted
    contact_line: Optional[str] = Field(default=None)
    contact_method: ContactMethod = Field(default=ContactMethod.LINE)
    
    # Thai-specific
    buddhist_date: Optional[str] = Field(default=None)  # พ.ศ. 2568
    
    # Notes and special requirements
    patient_notes: Optional[str] = Field(default=None)  # From patient
    internal_notes: Optional[str] = Field(default=None)  # From staff
    special_requirements: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Family booking
    family_booking_id: Optional[str] = Field(default=None, index=True)  # Groups family bookings
    family_members: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Confirmation and reminders
    confirmation_code: str = Field()  # 6-digit code
    confirmed_at: Optional[datetime] = Field(default=None)
    confirmed_via: Optional[str] = Field(default=None)  # LINE, SMS, etc.
    
    reminder_sent_at: Optional[datetime] = Field(default=None)
    reminder_method: Optional[str] = Field(default=None)
    
    # Check-in and completion
    checked_in_at: Optional[datetime] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    # No-show tracking
    no_show_count: int = Field(default=0)  # Historical count for this patient
    
    # Rescheduling
    rescheduled_from: Optional[int] = Field(default=None)  # Previous booking ID
    rescheduled_to: Optional[int] = Field(default=None)  # New booking ID
    reschedule_reason: Optional[str] = Field(default=None)
    
    # Queue management
    queue_number: Optional[str] = Field(default=None)  # Daily queue number
    estimated_wait_minutes: Optional[int] = Field(default=None)
    
    # Metadata
    source: str = Field(default="web")  # web, line, phone, walk-in
    ip_address_hash: Optional[str] = Field(default=None)
    user_agent_hash: Optional[str] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    patient: Optional["Patient"] = Relationship(back_populates="bookings")
    service: "BookingService" = Relationship(back_populates="bookings")
    slot: Optional["BookingSlot"] = Relationship(back_populates="bookings")
    notifications: List["BookingNotification"] = Relationship(back_populates="booking")
    
    @staticmethod
    def generate_reference(date: date) -> str:
        """Generate booking reference"""
        date_str = date.strftime("%Y%m%d")
        random_str = secrets.token_hex(2).upper()
        return f"REF-{date_str}-{random_str}"
    
    @staticmethod
    def generate_confirmation_code() -> str:
        """Generate 6-digit confirmation code"""
        return f"{secrets.randbelow(999999):06d}"


class BookingNotification(SQLModel, table=True):
    """Notification log for bookings"""
    __tablename__ = "booking_notifications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    booking_id: int = Field(foreign_key="bookings.id", index=True)
    notification_type: str = Field()  # confirmation, reminder, cancellation
    channel: ContactMethod = Field()
    
    # Channel-specific IDs
    line_message_id: Optional[str] = Field(default=None)
    sms_message_id: Optional[str] = Field(default=None)
    
    # Content
    message: str = Field()
    language: str = Field(default="th")
    
    # Status
    sent_at: Optional[datetime] = Field(default=None)
    delivered_at: Optional[datetime] = Field(default=None)
    read_at: Optional[datetime] = Field(default=None)
    failed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    booking: "Booking" = Relationship(back_populates="notifications")


class BookingRule(SQLModel, table=True):
    """Business rules for booking system"""
    __tablename__ = "booking_rules"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    rule_type: str = Field(index=True)  # max_advance_days, min_advance_hours, etc.
    service_id: Optional[int] = Field(default=None, foreign_key="booking_services.id")
    
    # Rule configuration
    rule_config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Examples:
    # max_advance_days: {"days": 30}
    # min_advance_hours: {"hours": 24}
    # max_bookings_per_patient: {"count": 3, "period_days": 30}
    # blackout_dates: {"dates": ["2025-01-01", "2025-04-13"]}
    # peak_hours: {"hours": ["11:00-13:00"], "capacity_reduction": 0.5}
    
    priority: int = Field(default=0)  # Higher priority rules apply first
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WaitingList(SQLModel, table=True):
    """Waiting list for fully booked slots"""
    __tablename__ = "waiting_lists"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id", index=True)
    service_id: int = Field(foreign_key="booking_services.id")
    
    # Desired booking window
    preferred_date_from: date = Field()
    preferred_date_to: date = Field()
    preferred_times: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # ["morning", "afternoon"]
    
    # Contact preferences
    contact_method: ContactMethod = Field(default=ContactMethod.LINE)
    contact_immediately: bool = Field(default=True)
    
    # Status
    is_active: bool = Field(default=True)
    notified_count: int = Field(default=0)
    last_notified_at: Optional[datetime] = Field(default=None)
    
    # If converted to booking
    converted_to_booking_id: Optional[int] = Field(default=None)
    converted_at: Optional[datetime] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field()  # Auto-remove after this


class BookingStatistics(SQLModel, table=True):
    """Daily booking statistics for analytics"""
    __tablename__ = "booking_statistics"
    __table_args__ = (
        UniqueConstraint("stat_date", "service_id"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    stat_date: date = Field(index=True)
    service_id: Optional[int] = Field(default=None, foreign_key="booking_services.id")
    
    # Counts
    total_bookings: int = Field(default=0)
    confirmed_bookings: int = Field(default=0)
    completed_bookings: int = Field(default=0)
    no_shows: int = Field(default=0)
    cancellations: int = Field(default=0)
    walk_ins: int = Field(default=0)
    
    # Capacity
    total_slots: int = Field(default=0)
    utilized_slots: int = Field(default=0)
    
    # Timing
    avg_wait_minutes: Optional[float] = Field(default=None)
    avg_service_minutes: Optional[float] = Field(default=None)
    
    # Patient demographics
    new_patients: int = Field(default=0)
    returning_patients: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Add relationships to existing models
BookingService.slots = Relationship(back_populates="service")
BookingService.bookings = Relationship(back_populates="service")