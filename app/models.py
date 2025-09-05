from typing import Optional, List, Any
from datetime import datetime, date, time, timedelta
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash


class StatusType(str, Enum):
    ANWESEND = "ANWESEND"
    URLAUB = "URLAUB"
    BILDUNGSURLAUB = "BILDUNGSURLAUB"
    KONGRESS = "KONGRESS"
    SONSTIGES = "SONSTIGES"


class Status(SQLModel, table=True):
    """Current status of the laboratory"""
    id: Optional[int] = Field(default=None, primary_key=True)
    type: StatusType = Field(default=StatusType.ANWESEND)
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    description: Optional[str] = None
    next_return: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StandardHours(SQLModel, table=True):
    """Standard weekly opening hours"""
    id: Optional[int] = Field(default=None, primary_key=True)
    day_of_week: int = Field(ge=0, le=6)  # 0=Monday, 6=Sunday
    time_ranges: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class HourException(SQLModel, table=True):
    """Exceptions to standard hours (holidays, special days)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    exception_date: date = Field(index=True)
    closed: bool = Field(default=False)
    time_ranges: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # New fields for enhanced functionality
    recurring: bool = Field(default=False)  # Is this a recurring exception
    recurring_pattern: Optional[str] = None  # weekly, monthly, yearly
    end_date: Optional[date] = None  # When does recurring end


class Availability(SQLModel, table=True):
    """Indicative availability slots"""
    id: Optional[int] = Field(default=None, primary_key=True)
    availability_date: date = Field(index=True)
    start_time: time = Field()
    end_time: time = Field()
    slot_type: str = Field(default="general")  # general, urgent, consultation, etc.
    capacity: int = Field(default=1)
    note: Optional[str] = None
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Legacy field for backward compatibility
    time_slots: List[str] = Field(default_factory=list, sa_column=Column(JSON))


class Announcement(SQLModel, table=True):
    """News and announcements"""
    id: Optional[int] = Field(default=None, primary_key=True)
    lang: str = Field(default="de", index=True)
    title: str
    body: str
    priority: str = Field(default="normal")  # low, normal, high, urgent
    category: str = Field(default="general")  # general, maintenance, holiday, etc.
    active: bool = Field(default=True)
    start_date: Optional[date] = None  # When announcement becomes active
    end_date: Optional[date] = None    # When announcement expires
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Settings(SQLModel, table=True):
    """General settings stored as key-value pairs"""
    key: str = Field(primary_key=True)
    value: dict = Field(default_factory=dict, sa_column=Column(JSON))
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SocialMediaPost(SQLModel, table=True):
    """Social media posts/content for sharing"""
    id: Optional[int] = Field(default=None, primary_key=True)
    platform: str = Field(index=True)  # line, facebook, instagram, etc.
    post_type: str = Field(default="announcement")  # announcement, hours, status, general
    title: Optional[str] = None
    content: str
    image_url: Optional[str] = None
    lang: str = Field(default="th", index=True)
    scheduled_for: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    post_url: Optional[str] = None  # URL after posting
    engagement_stats: dict = Field(default_factory=dict, sa_column=Column(JSON))
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SocialMediaConfig(SQLModel, table=True):
    """Social media platform configurations"""
    platform: str = Field(primary_key=True)  # line, facebook, instagram, etc.
    enabled: bool = Field(default=True)
    config: dict = Field(default_factory=dict, sa_column=Column(JSON))  # platform-specific settings
    credentials: dict = Field(default_factory=dict, sa_column=Column(JSON))  # API keys, tokens (encrypted)
    qr_enabled: bool = Field(default=True)
    last_sync: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ShareableContent(SQLModel, table=True):
    """Content that can be shared on social media"""
    id: Optional[int] = Field(default=None, primary_key=True)
    content_type: str = Field(index=True)  # hours, status, announcement, availability
    reference_id: Optional[int] = Field(index=True)  # ID of related record
    share_title: dict = Field(default_factory=dict, sa_column=Column(JSON))  # multilingual titles
    share_description: dict = Field(default_factory=dict, sa_column=Column(JSON))  # multilingual descriptions
    share_image: Optional[str] = None
    share_url: str
    platforms: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # which platforms to share to
    share_count: int = Field(default=0)
    last_shared: Optional[datetime] = None
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChangeLog(SQLModel, table=True):
    """Log of admin changes for rollback functionality"""
    id: Optional[int] = Field(default=None, primary_key=True)
    table_name: str = Field(index=True)
    record_id: Optional[int] = Field(index=True)
    action: str = Field()  # create, update, delete
    old_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    new_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    admin_user: str = Field()
    admin_ip: Optional[str] = None
    rollback_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    is_rolled_back: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# === LEGAL COMPLIANCE MODELS ===

class ConsentType(str, Enum):
    """Types of consent according to PDPA Thailand and GDPR"""
    NECESSARY = "NECESSARY"  # Technically necessary cookies/processing
    FUNCTIONAL = "FUNCTIONAL"  # Functional cookies (language, preferences)
    ANALYTICS = "ANALYTICS"  # Analytics/statistics
    MARKETING = "MARKETING"  # Marketing/advertising
    MEDICAL_DISCLAIMER = "MEDICAL_DISCLAIMER"  # Medical service disclaimers


class CookieConsent(SQLModel, table=True):
    """User consent tracking for PDPA/GDPR compliance"""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)  # Anonymous session identifier
    ip_address_hash: str = Field(index=True)  # Hashed IP (not stored directly)
    user_agent_hash: str  # Hashed user agent for fraud detection
    consent_version: str = Field()  # Version of privacy policy/terms
    necessary_consent: bool = Field(default=True)  # Always true
    functional_consent: bool = Field(default=False)
    analytics_consent: bool = Field(default=False)  
    marketing_consent: bool = Field(default=False)
    medical_disclaimer_accepted: bool = Field(default=False)
    language: str = Field(default="th")  # Language consent was given in
    consent_source: str = Field()  # "banner", "settings", "admin"
    withdrawn_at: Optional[datetime] = None
    expires_at: datetime  # Consent expiration (13 months max per GDPR)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LegalDocument(SQLModel, table=True):
    """Legal documents (Privacy Policy, Terms, Impressum) - multilingual"""
    id: Optional[int] = Field(default=None, primary_key=True)
    document_type: str = Field(index=True)  # "privacy_policy", "terms", "impressum", "medical_disclaimer"
    language: str = Field(index=True)  # "th", "de", "en"
    version: str = Field()  # Version number (e.g., "1.0", "1.1")
    title: str
    content: str  # Full legal text in markdown/HTML
    effective_date: date
    last_review_date: Optional[date] = None
    next_review_date: Optional[date] = None
    is_active: bool = Field(default=True)
    requires_consent: bool = Field(default=True)
    created_by: str  # Admin user who created
    approved_by: Optional[str] = None  # Legal approval
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DataProcessingPurpose(SQLModel, table=True):
    """Data processing purposes per PDPA Article 19"""
    id: Optional[int] = Field(default=None, primary_key=True)
    purpose_code: str = Field(unique=True)  # "website_operation", "analytics", "marketing"
    purpose_name: dict = Field(sa_column=Column(JSON))  # Multilingual names
    description: dict = Field(sa_column=Column(JSON))  # Multilingual descriptions
    legal_basis_th: str  # PDPA legal basis (consent, legitimate_interest, etc.)
    legal_basis_eu: str  # GDPR legal basis (Art. 6)
    data_categories: List[str] = Field(sa_column=Column(JSON))  # Types of data processed
    retention_period_days: int  # How long data is kept
    third_party_sharing: bool = Field(default=False)  # Shared with third parties?
    third_parties: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    requires_explicit_consent: bool = Field(default=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DataSubjectRequest(SQLModel, table=True):
    """Data subject requests (GDPR Art. 15-20, PDPA rights)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    request_type: str  # "access", "rectification", "erasure", "portability", "objection", "restriction"
    session_id_hash: str = Field(index=True)  # To identify the requester
    email: str = Field(index=True)  # Contact email
    language: str = Field(default="th")
    request_details: str  # Description of the request
    verification_code: str  # Code sent to email for verification
    verified_at: Optional[datetime] = None
    status: str = Field(default="pending")  # pending, verified, processing, completed, rejected
    response_text: Optional[str] = None
    response_sent_at: Optional[datetime] = None
    data_export: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # For portability requests
    processed_by: Optional[str] = None  # Admin user
    deadline: datetime  # Response deadline (30 days GDPR, 30 days PDPA)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ComplianceLog(SQLModel, table=True):
    """Comprehensive logging for legal compliance"""
    id: Optional[int] = Field(default=None, primary_key=True)
    log_type: str = Field(index=True)  # "consent", "data_request", "policy_update", "data_breach", "audit"
    session_id_hash: Optional[str] = Field(index=True)
    ip_address_hash: Optional[str] = Field(index=True)
    user_agent_hash: Optional[str] = None
    action: str  # Specific action taken
    details: dict = Field(default_factory=dict, sa_column=Column(JSON))
    severity: str = Field(default="info")  # info, warning, critical
    requires_retention: bool = Field(default=True)  # Must be kept for legal purposes
    retention_until: Optional[datetime] = None  # When can this log be deleted
    compliance_framework: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # ["PDPA", "GDPR", "Medical"]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DataRetentionPolicy(SQLModel, table=True):
    """Data retention policies per data type"""
    id: Optional[int] = Field(default=None, primary_key=True)
    data_type: str = Field(unique=True)  # "consent_logs", "analytics", "admin_logs", etc.
    description: dict = Field(sa_column=Column(JSON))  # Multilingual description
    retention_period_days: int
    legal_basis_th: str  # Why we keep this data (PDPA)
    legal_basis_eu: str  # Why we keep this data (GDPR)
    auto_delete: bool = Field(default=True)  # Automatically delete after retention
    anonymization_after_days: Optional[int] = None  # Anonymize before deletion
    backup_retention_days: Optional[int] = None  # How long in backups
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AdminUser(SQLModel, table=True):
    """Admin user with hashed password"""
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str = Field()
    email: Optional[str] = None
    last_login: Optional[datetime] = None
    login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
        self.updated_at = datetime.utcnow()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self) -> bool:
        """Check if account is temporarily locked"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def record_login_attempt(self, success: bool):
        """Record login attempt and handle locking logic"""
        if success:
            self.login_attempts = 0
            self.locked_until = None
            self.last_login = datetime.utcnow()
        else:
            self.login_attempts += 1
            # Lock after 5 failed attempts for 15 minutes
            if self.login_attempts >= 5:
                self.locked_until = datetime.utcnow() + timedelta(minutes=15)
        self.updated_at = datetime.utcnow()


class VisitorAnalytics(SQLModel, table=True):
    """Analytics for tracking main page visits (privacy-compliant)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Basic visit information
    visit_date: date = Field(index=True)
    visit_time: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Page information
    page_path: str = Field(index=True)  # "/", "/week", "/month", etc.
    referrer_type: Optional[str] = None  # "qr", "direct", "social", "search"
    
    # Security and Protocol (Production-ready)
    is_secure_connection: bool = Field(default=False)  # HTTPS indicator
    protocol_version: str = Field(default="HTTP/1.1")  # HTTP/1.1, HTTP/2, HTTP/3
    
    # Device/Browser info (anonymized)
    device_type: Optional[str] = None  # "mobile", "tablet", "desktop"
    browser_family: Optional[str] = None  # "chrome", "safari", "firefox"
    operating_system: Optional[str] = None  # "android", "ios", "windows"
    
    # Language and location (general)
    preferred_language: str = Field(default="th")
    country_code: Optional[str] = None  # "TH", "DE", "US" (from IP geolocation, not stored)
    timezone_offset: Optional[int] = None  # Client timezone offset in minutes
    
    # QR-specific tracking
    qr_code_scan: bool = Field(default=False)
    qr_campaign: Optional[str] = None  # Different QR codes for different locations
    
    # Session information (anonymized)
    session_hash: str = Field(index=True)  # Anonymized session ID
    is_returning_visitor: bool = Field(default=False)
    
    # User interaction
    time_on_page_seconds: Optional[int] = None
    pages_visited: int = Field(default=1)
    interaction_events: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # ["language_change", "week_view", etc.]
    
    # Performance metrics
    page_load_time_ms: Optional[int] = None  # Client-side page load time
    first_contentful_paint_ms: Optional[int] = None  # Web Vitals
    largest_contentful_paint_ms: Optional[int] = None  # Web Vitals
    
    # Privacy compliance
    analytics_consent: bool = Field(default=False)
    ip_anonymized: bool = Field(default=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DailyStatistics(SQLModel, table=True):
    """Daily aggregated statistics for performance and reporting"""
    id: Optional[int] = Field(default=None, primary_key=True)
    stats_date: date = Field(unique=True, index=True)
    
    # Visit statistics
    total_visits: int = Field(default=0)
    unique_visitors: int = Field(default=0)
    qr_scans: int = Field(default=0)
    returning_visitors: int = Field(default=0)
    
    # Page views
    homepage_views: int = Field(default=0)
    week_views: int = Field(default=0)
    month_views: int = Field(default=0)
    kiosk_views: int = Field(default=0)
    
    # Device breakdown
    mobile_visits: int = Field(default=0)
    tablet_visits: int = Field(default=0)
    desktop_visits: int = Field(default=0)
    
    # Language breakdown
    thai_visitors: int = Field(default=0)
    english_visitors: int = Field(default=0)
    german_visitors: int = Field(default=0)
    
    # Engagement metrics
    avg_session_duration_seconds: Optional[float] = None
    avg_pages_per_visit: Optional[float] = None
    bounce_rate_percent: Optional[float] = None
    
    # Popular times
    peak_hour: Optional[int] = None  # Hour with most visits (0-23)
    peak_hour_visits: Optional[int] = None
    
    # Referrer statistics
    direct_visits: int = Field(default=0)
    qr_visits: int = Field(default=0)
    social_visits: int = Field(default=0)
    search_visits: int = Field(default=0)
    
    # Status at time of visit (for correlation)
    status_when_visited: Optional[str] = None  # Most common status during visits
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)