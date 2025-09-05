-- PostgreSQL Migration Script
-- Generated from SQLite database
-- Source: data/portal.db
-- Generated: 2025-08-27T20:47:22.780393

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Table: adminuser
CREATE TABLE adminuser (
    id SERIAL NOT NULL,
    username VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    email VARCHAR,
    last_login TIMESTAMP WITH TIME ZONE,
    login_attempts INTEGER NOT NULL,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: announcement
CREATE TABLE announcement (
    id SERIAL NOT NULL,
    lang VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    body VARCHAR NOT NULL,
    priority VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    active BOOLEAN NOT NULL,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: availability
CREATE TABLE availability (
    id SERIAL NOT NULL,
    availability_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_type VARCHAR NOT NULL,
    capacity INTEGER NOT NULL,
    note VARCHAR,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    time_slots JSONB
);

-- Table: changelog
CREATE TABLE changelog (
    id SERIAL NOT NULL,
    table_name VARCHAR NOT NULL,
    record_id INTEGER,
    action VARCHAR NOT NULL,
    old_data JSONB,
    new_data JSONB,
    admin_user VARCHAR NOT NULL,
    admin_ip VARCHAR,
    rollback_data JSONB,
    is_rolled_back BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: compliancelog
CREATE TABLE compliancelog (
    id SERIAL NOT NULL,
    log_type VARCHAR NOT NULL,
    session_id_hash VARCHAR,
    ip_address_hash VARCHAR,
    user_agent_hash VARCHAR,
    action VARCHAR NOT NULL,
    details JSONB,
    severity VARCHAR NOT NULL,
    requires_retention BOOLEAN NOT NULL,
    retention_until TIMESTAMP WITH TIME ZONE,
    compliance_framework JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: cookieconsent
CREATE TABLE cookieconsent (
    id SERIAL NOT NULL,
    session_id VARCHAR NOT NULL,
    ip_address_hash VARCHAR NOT NULL,
    user_agent_hash VARCHAR NOT NULL,
    consent_version VARCHAR NOT NULL,
    necessary_consent BOOLEAN NOT NULL,
    functional_consent BOOLEAN NOT NULL,
    analytics_consent BOOLEAN NOT NULL,
    marketing_consent BOOLEAN NOT NULL,
    medical_disclaimer_accepted BOOLEAN NOT NULL,
    language VARCHAR NOT NULL,
    consent_source VARCHAR NOT NULL,
    withdrawn_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: dailystatistics
CREATE TABLE dailystatistics (
    id SERIAL NOT NULL,
    stats_date DATE NOT NULL,
    total_visits INTEGER NOT NULL,
    unique_visitors INTEGER NOT NULL,
    qr_scans INTEGER NOT NULL,
    returning_visitors INTEGER NOT NULL,
    homepage_views INTEGER NOT NULL,
    week_views INTEGER NOT NULL,
    month_views INTEGER NOT NULL,
    kiosk_views INTEGER NOT NULL,
    mobile_visits INTEGER NOT NULL,
    tablet_visits INTEGER NOT NULL,
    desktop_visits INTEGER NOT NULL,
    thai_visitors INTEGER NOT NULL,
    english_visitors INTEGER NOT NULL,
    german_visitors INTEGER NOT NULL,
    avg_session_duration_seconds REAL,
    avg_pages_per_visit REAL,
    bounce_rate_percent REAL,
    peak_hour INTEGER,
    peak_hour_visits INTEGER,
    direct_visits INTEGER NOT NULL,
    qr_visits INTEGER NOT NULL,
    social_visits INTEGER NOT NULL,
    search_visits INTEGER NOT NULL,
    status_when_visited VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: dataprocessingpurpose
CREATE TABLE dataprocessingpurpose (
    id SERIAL NOT NULL,
    purpose_code VARCHAR NOT NULL,
    purpose_name JSONB,
    description JSONB,
    legal_basis_th VARCHAR NOT NULL,
    legal_basis_eu VARCHAR NOT NULL,
    data_categories JSONB,
    retention_period_days INTEGER NOT NULL,
    third_party_sharing BOOLEAN NOT NULL,
    third_parties JSONB,
    requires_explicit_consent BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: dataretentionpolicy
CREATE TABLE dataretentionpolicy (
    id SERIAL NOT NULL,
    data_type VARCHAR NOT NULL,
    description JSONB,
    retention_period_days INTEGER NOT NULL,
    legal_basis_th VARCHAR NOT NULL,
    legal_basis_eu VARCHAR NOT NULL,
    auto_delete BOOLEAN NOT NULL,
    anonymization_after_days INTEGER,
    backup_retention_days INTEGER,
    is_active BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: datasubjectrequest
CREATE TABLE datasubjectrequest (
    id SERIAL NOT NULL,
    request_type VARCHAR NOT NULL,
    session_id_hash VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    language VARCHAR NOT NULL,
    request_details VARCHAR NOT NULL,
    verification_code VARCHAR NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR NOT NULL,
    response_text VARCHAR,
    response_sent_at TIMESTAMP WITH TIME ZONE,
    data_export JSONB,
    processed_by VARCHAR,
    deadline TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: hourexception
CREATE TABLE hourexception (
    id SERIAL NOT NULL,
    exception_date DATE NOT NULL,
    closed BOOLEAN NOT NULL,
    time_ranges JSONB,
    note VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    recurring BOOLEAN NOT NULL,
    recurring_pattern VARCHAR,
    end_date DATE
);

-- Table: legaldocument
CREATE TABLE legaldocument (
    id SERIAL NOT NULL,
    document_type VARCHAR NOT NULL,
    language VARCHAR NOT NULL,
    version VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    content VARCHAR NOT NULL,
    effective_date DATE NOT NULL,
    last_review_date DATE,
    next_review_date DATE,
    is_active BOOLEAN NOT NULL,
    requires_consent BOOLEAN NOT NULL,
    created_by VARCHAR NOT NULL,
    approved_by VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: settings
CREATE TABLE settings (
    key VARCHAR NOT NULL,
    value JSONB,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: shareablecontent
CREATE TABLE shareablecontent (
    id SERIAL NOT NULL,
    content_type VARCHAR NOT NULL,
    reference_id INTEGER,
    share_title JSONB,
    share_description JSONB,
    share_image VARCHAR,
    share_url VARCHAR NOT NULL,
    platforms JSONB,
    share_count INTEGER NOT NULL,
    last_shared TIMESTAMP WITH TIME ZONE,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: socialmediaconfig
CREATE TABLE socialmediaconfig (
    platform VARCHAR NOT NULL,
    enabled BOOLEAN NOT NULL,
    config JSONB,
    credentials JSONB,
    qr_enabled BOOLEAN NOT NULL,
    last_sync TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: socialmediapost
CREATE TABLE socialmediapost (
    id SERIAL NOT NULL,
    platform VARCHAR NOT NULL,
    post_type VARCHAR NOT NULL,
    title VARCHAR,
    content VARCHAR NOT NULL,
    image_url VARCHAR,
    lang VARCHAR NOT NULL,
    scheduled_for TIMESTAMP WITH TIME ZONE,
    posted_at TIMESTAMP WITH TIME ZONE,
    post_url VARCHAR,
    engagement_stats JSONB,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: sqlite_stat1
CREATE TABLE sqlite_stat1 (
    tbl ,
    idx ,
    stat 
);

-- Table: standardhours
CREATE TABLE standardhours (
    id SERIAL NOT NULL,
    day_of_week INTEGER NOT NULL,
    time_ranges JSONB,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: status
CREATE TABLE status (
    id SERIAL NOT NULL,
    type VARCHAR(14) NOT NULL,
    date_from DATE,
    date_to DATE,
    description VARCHAR,
    next_return DATE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table: visitoranalytics
CREATE TABLE visitoranalytics (
    id SERIAL NOT NULL,
    visit_date DATE NOT NULL,
    visit_time TIMESTAMP WITH TIME ZONE NOT NULL,
    page_path VARCHAR NOT NULL,
    referrer_type VARCHAR,
    is_secure_connection BOOLEAN NOT NULL,
    protocol_version VARCHAR NOT NULL,
    device_type VARCHAR,
    browser_family VARCHAR,
    operating_system VARCHAR,
    preferred_language VARCHAR NOT NULL,
    country_code VARCHAR,
    timezone_offset INTEGER,
    qr_code_scan BOOLEAN NOT NULL,
    qr_campaign VARCHAR,
    session_hash VARCHAR NOT NULL,
    is_returning_visitor BOOLEAN NOT NULL,
    time_on_page_seconds INTEGER,
    pages_visited INTEGER NOT NULL,
    interaction_events JSONB,
    page_load_time_ms INTEGER,
    first_contentful_paint_ms INTEGER,
    largest_contentful_paint_ms INTEGER,
    analytics_consent BOOLEAN NOT NULL,
    ip_anonymized BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS ix_hourexception_exception_date ON hourexception (exception_date);
CREATE INDEX IF NOT EXISTS ix_availability_availability_date ON availability (availability_date);
CREATE INDEX IF NOT EXISTS ix_announcement_lang ON announcement (lang);
CREATE INDEX IF NOT EXISTS ix_socialmediapost_lang ON socialmediapost (lang);
CREATE INDEX IF NOT EXISTS ix_socialmediapost_platform ON socialmediapost (platform);
CREATE INDEX IF NOT EXISTS ix_shareablecontent_content_type ON shareablecontent (content_type);
CREATE INDEX IF NOT EXISTS ix_shareablecontent_reference_id ON shareablecontent (reference_id);
CREATE INDEX IF NOT EXISTS ix_changelog_record_id ON changelog (record_id);
CREATE INDEX IF NOT EXISTS ix_changelog_table_name ON changelog (table_name);
CREATE INDEX IF NOT EXISTS ix_cookieconsent_ip_address_hash ON cookieconsent (ip_address_hash);
CREATE INDEX IF NOT EXISTS ix_cookieconsent_session_id ON cookieconsent (session_id);
CREATE INDEX IF NOT EXISTS ix_legaldocument_language ON legaldocument (language);
CREATE INDEX IF NOT EXISTS ix_legaldocument_document_type ON legaldocument (document_type);
CREATE INDEX IF NOT EXISTS ix_datasubjectrequest_session_id_hash ON datasubjectrequest (session_id_hash);
CREATE INDEX IF NOT EXISTS ix_datasubjectrequest_email ON datasubjectrequest (email);
CREATE INDEX IF NOT EXISTS ix_compliancelog_ip_address_hash ON compliancelog (ip_address_hash);
CREATE INDEX IF NOT EXISTS ix_compliancelog_log_type ON compliancelog (log_type);
CREATE INDEX IF NOT EXISTS ix_compliancelog_session_id_hash ON compliancelog (session_id_hash);
CREATE UNIQUE INDEX ix_adminuser_username ON adminuser (username);
CREATE INDEX IF NOT EXISTS ix_visitoranalytics_visit_date ON visitoranalytics (visit_date);
CREATE INDEX IF NOT EXISTS ix_visitoranalytics_session_hash ON visitoranalytics (session_hash);
CREATE INDEX IF NOT EXISTS ix_visitoranalytics_visit_time ON visitoranalytics (visit_time);
CREATE INDEX IF NOT EXISTS ix_visitoranalytics_page_path ON visitoranalytics (page_path);
CREATE UNIQUE INDEX ix_dailystatistics_stats_date ON dailystatistics (stats_date);
CREATE INDEX IF NOT EXISTS idx_announcement_active_lang_priority ON announcement(active, lang, priority) WHERE active = 1;
CREATE INDEX IF NOT EXISTS idx_availability_date_active_type ON availability(availability_date, active, slot_type) WHERE active = 1;
CREATE INDEX IF NOT EXISTS idx_hourexception_date_closed ON hourexception(exception_date, closed);
CREATE INDEX IF NOT EXISTS idx_visitoranalytics_date_time ON visitoranalytics(visit_date, visit_time);
CREATE INDEX IF NOT EXISTS idx_visitoranalytics_session_page ON visitoranalytics(session_hash, page_path);
CREATE INDEX IF NOT EXISTS idx_dailystatistics_date_desc ON dailystatistics(stats_date DESC);
CREATE INDEX IF NOT EXISTS idx_compliancelog_type_severity_created ON compliancelog(log_type, severity, created_at);
CREATE INDEX IF NOT EXISTS idx_cookieconsent_session_expires ON cookieconsent(session_id, expires_at) WHERE expires_at > datetime('now');
CREATE INDEX IF NOT EXISTS idx_datasubjectrequest_status_deadline ON datasubjectrequest(status, deadline);
CREATE INDEX IF NOT EXISTS idx_socialmediapost_platform_active_scheduled ON socialmediapost(platform, active, scheduled_for) WHERE active = 1;
CREATE INDEX IF NOT EXISTS idx_shareablecontent_type_active_shared ON shareablecontent(content_type, active, last_shared) WHERE active = 1;
CREATE INDEX IF NOT EXISTS idx_changelog_table_action_created ON changelog(table_name, action, created_at);
CREATE INDEX IF NOT EXISTS idx_changelog_rollback_status ON changelog(is_rolled_back, created_at) WHERE is_rolled_back = 0;
CREATE INDEX IF NOT EXISTS idx_adminuser_username_locked ON adminuser(username, locked_until);
CREATE INDEX IF NOT EXISTS idx_legaldocument_type_lang_active ON legaldocument(document_type, language, is_active) WHERE is_active = 1;
CREATE INDEX IF NOT EXISTS idx_dataprocessingpurpose_active_consent ON dataprocessingpurpose(is_active, requires_explicit_consent) WHERE is_active = 1;
CREATE INDEX IF NOT EXISTS idx_standardhours_day_updated ON standardhours(day_of_week, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_announcement_active_range ON announcement(active, lang, start_date, end_date) WHERE active = 1;
CREATE INDEX IF NOT EXISTS idx_availability_date_range_active ON availability(availability_date, start_time, active) WHERE active = 1;
CREATE INDEX IF NOT EXISTS idx_visitoranalytics_time_series ON visitoranalytics(visit_date DESC, visit_time DESC);
CREATE INDEX IF NOT EXISTS idx_visitoranalytics_session_timeline ON visitoranalytics(session_hash, visit_time ASC);
CREATE INDEX IF NOT EXISTS idx_changelog_recent_activity ON changelog(table_name, created_at DESC) WHERE is_rolled_back = 0;
CREATE INDEX IF NOT EXISTS idx_cookieconsent_active_sessions ON cookieconsent(session_id, expires_at) WHERE expires_at > datetime('now');
CREATE INDEX IF NOT EXISTS idx_compliancelog_retention ON compliancelog(retention_until, requires_retention) WHERE requires_retention = 1;

-- PostgreSQL-specific optimizations

-- Optimize for analytics queries
CREATE INDEX IF NOT EXISTS idx_visitoranalytics_jsonb_gin ON visitoranalytics USING GIN (interaction_events);
CREATE INDEX IF NOT EXISTS idx_announcement_jsonb_gin ON announcement USING GIN ((body::jsonb)) WHERE body::text ~ '^{';

-- Add foreign key constraints
-- ALTER TABLE availability ADD CONSTRAINT fk_availability_service FOREIGN KEY (service_id) REFERENCES booking_service(id);

-- Optimize for Thai text search
CREATE INDEX IF NOT EXISTS idx_announcement_thai_search ON announcement USING GIN (to_tsvector('thai', title || ' ' || body));

-- Update table statistics
ANALYZE;

-- Migration completed
-- Generated on: 2025-08-27T20:47:22.830633