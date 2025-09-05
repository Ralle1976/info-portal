"""
Legal Compliance Service for Thailand PDPA and EU GDPR
Handles consent management, legal documents, and data subject rights
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, date
from typing import Optional, Dict, List, Any
from sqlmodel import Session, select
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

from ..models import (
    CookieConsent, LegalDocument, DataProcessingPurpose, 
    DataSubjectRequest, ComplianceLog, DataRetentionPolicy, ConsentType
)
from ..database import engine


class LegalComplianceService:
    """Service for managing legal compliance with Thai PDPA and EU GDPR"""
    
    def __init__(self):
        self.engine = engine
        
    def _hash_identifier(self, identifier: str) -> str:
        """Hash identifiers for privacy protection"""
        return hashlib.sha256(f"{identifier}__salt_legal_2024".encode()).hexdigest()
    
    def _get_session_id(self, request) -> str:
        """Get or create anonymous session ID"""
        session_id = request.session.get('legal_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['legal_session_id'] = session_id
        return session_id
    
    def record_consent(self, request, consent_data: Dict[str, Any]) -> bool:
        """Record user consent for PDPA/GDPR compliance"""
        try:
            with Session(self.engine) as session:
                # Get identifiers
                session_id = self._get_session_id(request)
                ip_hash = self._hash_identifier(request.environ.get('REMOTE_ADDR', ''))
                user_agent_hash = self._hash_identifier(request.environ.get('HTTP_USER_AGENT', ''))
                
                # Check if consent already exists for this session
                existing_consent = session.exec(
                    select(CookieConsent).where(CookieConsent.session_id == session_id)
                ).first()
                
                if existing_consent and not existing_consent.withdrawn_at:
                    # Update existing consent
                    existing_consent.functional_consent = consent_data.get('functional', False)
                    existing_consent.analytics_consent = consent_data.get('analytics', False)
                    existing_consent.marketing_consent = consent_data.get('marketing', False)
                    existing_consent.medical_disclaimer_accepted = consent_data.get('medical_disclaimer', False)
                    existing_consent.language = consent_data.get('language', 'th')
                    existing_consent.consent_source = consent_data.get('source', 'banner')
                    existing_consent.updated_at = datetime.utcnow()
                    consent_record = existing_consent
                else:
                    # Create new consent record
                    consent_record = CookieConsent(
                        session_id=session_id,
                        ip_address_hash=ip_hash,
                        user_agent_hash=user_agent_hash,
                        consent_version=consent_data.get('version', '1.0'),
                        necessary_consent=True,  # Always true for technical necessity
                        functional_consent=consent_data.get('functional', False),
                        analytics_consent=consent_data.get('analytics', False),
                        marketing_consent=consent_data.get('marketing', False),
                        medical_disclaimer_accepted=consent_data.get('medical_disclaimer', False),
                        language=consent_data.get('language', 'th'),
                        consent_source=consent_data.get('source', 'banner'),
                        expires_at=datetime.utcnow() + timedelta(days=395)  # 13 months max per GDPR
                    )
                    session.add(consent_record)
                
                session.commit()
                
                # Log the consent for compliance
                self.log_compliance_event(
                    session_id_hash=self._hash_identifier(session_id),
                    ip_hash=ip_hash,
                    log_type="consent",
                    action="consent_recorded",
                    details={
                        "consent_types": consent_data,
                        "version": consent_data.get('version', '1.0'),
                        "language": consent_data.get('language', 'th')
                    },
                    compliance_frameworks=["PDPA", "GDPR"]
                )
                
                return True
                
        except Exception as e:
            self.log_compliance_event(
                log_type="consent",
                action="consent_error",
                details={"error": str(e)},
                severity="critical",
                compliance_frameworks=["PDPA", "GDPR"]
            )
            return False
    
    def get_user_consent(self, request) -> Optional[Dict[str, Any]]:
        """Get current user consent status"""
        try:
            with Session(self.engine) as session:
                session_id = self._get_session_id(request)
                
                consent = session.exec(
                    select(CookieConsent).where(
                        CookieConsent.session_id == session_id,
                        CookieConsent.withdrawn_at.is_(None),
                        CookieConsent.expires_at > datetime.utcnow()
                    )
                ).first()
                
                if not consent:
                    return None
                
                return {
                    "necessary": consent.necessary_consent,
                    "functional": consent.functional_consent,
                    "analytics": consent.analytics_consent,
                    "marketing": consent.marketing_consent,
                    "medical_disclaimer": consent.medical_disclaimer_accepted,
                    "version": consent.consent_version,
                    "language": consent.language,
                    "expires_at": consent.expires_at.isoformat(),
                    "given_at": consent.created_at.isoformat()
                }
                
        except Exception as e:
            self.log_compliance_event(
                log_type="consent",
                action="consent_retrieval_error",
                details={"error": str(e)},
                severity="warning"
            )
            return None
    
    def withdraw_consent(self, request, consent_types: List[str] = None) -> bool:
        """Withdraw user consent (GDPR Art. 7(3), PDPA rights)"""
        try:
            with Session(self.engine) as session:
                session_id = self._get_session_id(request)
                
                consent = session.exec(
                    select(CookieConsent).where(
                        CookieConsent.session_id == session_id,
                        CookieConsent.withdrawn_at.is_(None)
                    )
                ).first()
                
                if consent:
                    if consent_types is None:
                        # Withdraw all non-necessary consent
                        consent.functional_consent = False
                        consent.analytics_consent = False
                        consent.marketing_consent = False
                        consent.withdrawn_at = datetime.utcnow()
                    else:
                        # Withdraw specific consent types
                        if 'functional' in consent_types:
                            consent.functional_consent = False
                        if 'analytics' in consent_types:
                            consent.analytics_consent = False
                        if 'marketing' in consent_types:
                            consent.marketing_consent = False
                    
                    consent.updated_at = datetime.utcnow()
                    session.commit()
                    
                    self.log_compliance_event(
                        session_id_hash=self._hash_identifier(session_id),
                        log_type="consent",
                        action="consent_withdrawn",
                        details={"withdrawn_types": consent_types or "all"},
                        compliance_frameworks=["PDPA", "GDPR"]
                    )
                    
                    return True
                    
        except Exception as e:
            self.log_compliance_event(
                log_type="consent",
                action="withdrawal_error",
                details={"error": str(e)},
                severity="critical"
            )
            
        return False
    
    def get_legal_document(self, document_type: str, language: str = "th", version: str = None) -> Optional[LegalDocument]:
        """Get legal document (Privacy Policy, Terms, etc.)"""
        try:
            with Session(self.engine) as session:
                query = select(LegalDocument).where(
                    LegalDocument.document_type == document_type,
                    LegalDocument.language == language,
                    LegalDocument.is_active == True
                )
                
                if version:
                    query = query.where(LegalDocument.version == version)
                else:
                    query = query.order_by(LegalDocument.version.desc())
                
                return session.exec(query).first()
                
        except Exception as e:
            self.log_compliance_event(
                log_type="legal_document",
                action="retrieval_error",
                details={"document_type": document_type, "language": language, "error": str(e)},
                severity="warning"
            )
            return None
    
    def create_data_subject_request(self, request_type: str, email: str, details: str, language: str = "th") -> Optional[str]:
        """Create data subject request (GDPR Art. 15-20, PDPA rights)"""
        try:
            with Session(self.engine) as session:
                # Generate verification code
                verification_code = secrets.token_urlsafe(32)
                
                # Create request
                data_request = DataSubjectRequest(
                    request_type=request_type,
                    session_id_hash=self._hash_identifier(f"email_{email}"),
                    email=email,
                    language=language,
                    request_details=details,
                    verification_code=verification_code,
                    deadline=datetime.utcnow() + timedelta(days=30)  # 30 days for both GDPR and PDPA
                )
                
                session.add(data_request)
                session.commit()
                
                # Log the request
                self.log_compliance_event(
                    log_type="data_request",
                    action="request_created",
                    details={
                        "request_type": request_type,
                        "language": language,
                        "email_domain": email.split('@')[1] if '@' in email else "unknown"
                    },
                    compliance_frameworks=["PDPA", "GDPR"]
                )
                
                # Send verification email (simplified)
                self._send_verification_email(email, verification_code, language)
                
                return verification_code
                
        except Exception as e:
            self.log_compliance_event(
                log_type="data_request",
                action="creation_error",
                details={"error": str(e)},
                severity="critical"
            )
            return None
    
    def verify_data_subject_request(self, verification_code: str) -> bool:
        """Verify data subject request via email code"""
        try:
            with Session(self.engine) as session:
                request = session.exec(
                    select(DataSubjectRequest).where(
                        DataSubjectRequest.verification_code == verification_code,
                        DataSubjectRequest.verified_at.is_(None)
                    )
                ).first()
                
                if request:
                    request.verified_at = datetime.utcnow()
                    request.status = "verified"
                    session.commit()
                    
                    self.log_compliance_event(
                        log_type="data_request",
                        action="request_verified",
                        details={"request_id": request.id, "request_type": request.request_type},
                        compliance_frameworks=["PDPA", "GDPR"]
                    )
                    
                    return True
                    
        except Exception as e:
            self.log_compliance_event(
                log_type="data_request",
                action="verification_error",
                details={"error": str(e)},
                severity="warning"
            )
            
        return False
    
    def log_compliance_event(self, log_type: str, action: str, details: Dict[str, Any] = None, 
                           session_id_hash: str = None, ip_hash: str = None, 
                           severity: str = "info", compliance_frameworks: List[str] = None):
        """Log compliance events for audit trail"""
        try:
            with Session(self.engine) as session:
                log_entry = ComplianceLog(
                    log_type=log_type,
                    session_id_hash=session_id_hash,
                    ip_address_hash=ip_hash,
                    action=action,
                    details=details or {},
                    severity=severity,
                    compliance_framework=compliance_frameworks or [],
                    retention_until=datetime.utcnow() + timedelta(days=2555)  # 7 years retention
                )
                
                session.add(log_entry)
                session.commit()
                
        except Exception as e:
            # Critical: If we can't log compliance events, this is a major issue
            print(f"CRITICAL: Failed to log compliance event: {e}")
    
    def _send_verification_email(self, email: str, verification_code: str, language: str):
        """Send verification email for data subject requests"""
        # Simplified email sending - in production, use proper email service
        try:
            # This would be implemented with actual email service
            print(f"Verification email sent to {email} with code {verification_code} in {language}")
            
        except Exception as e:
            self.log_compliance_event(
                log_type="email",
                action="verification_email_failed",
                details={"error": str(e), "language": language},
                severity="warning"
            )
    
    def cleanup_expired_data(self) -> Dict[str, int]:
        """Clean up expired data according to retention policies"""
        cleanup_stats = {}
        
        try:
            with Session(self.engine) as session:
                # Clean up expired consents
                expired_consents = session.exec(
                    select(CookieConsent).where(
                        CookieConsent.expires_at < datetime.utcnow()
                    )
                ).all()
                
                for consent in expired_consents:
                    session.delete(consent)
                
                cleanup_stats['expired_consents'] = len(expired_consents)
                
                # Clean up old compliance logs based on retention policies
                retention_policies = session.exec(select(DataRetentionPolicy)).all()
                
                for policy in retention_policies:
                    if policy.auto_delete:
                        cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_period_days)
                        
                        # This would be expanded based on data_type
                        old_logs = session.exec(
                            select(ComplianceLog).where(
                                ComplianceLog.created_at < cutoff_date,
                                ComplianceLog.requires_retention == False
                            )
                        ).all()
                        
                        for log in old_logs:
                            session.delete(log)
                        
                        cleanup_stats[f'old_{policy.data_type}'] = len(old_logs)
                
                session.commit()
                
                self.log_compliance_event(
                    log_type="cleanup",
                    action="data_cleanup_completed",
                    details=cleanup_stats,
                    compliance_frameworks=["PDPA", "GDPR"]
                )
                
        except Exception as e:
            self.log_compliance_event(
                log_type="cleanup",
                action="cleanup_error",
                details={"error": str(e)},
                severity="critical"
            )
            cleanup_stats['errors'] = 1
        
        return cleanup_stats
    
    def export_user_data(self, session_id: str) -> Dict[str, Any]:
        """Export all user data for portability (GDPR Art. 20, PDPA rights)"""
        try:
            with Session(self.engine) as session:
                session_hash = self._hash_identifier(session_id)
                
                # Get consent records
                consents = session.exec(
                    select(CookieConsent).where(CookieConsent.session_id == session_id)
                ).all()
                
                # Get compliance logs
                logs = session.exec(
                    select(ComplianceLog).where(ComplianceLog.session_id_hash == session_hash)
                ).all()
                
                export_data = {
                    "export_date": datetime.utcnow().isoformat(),
                    "session_id": session_id,
                    "consents": [
                        {
                            "consent_version": c.consent_version,
                            "necessary_consent": c.necessary_consent,
                            "functional_consent": c.functional_consent,
                            "analytics_consent": c.analytics_consent,
                            "marketing_consent": c.marketing_consent,
                            "medical_disclaimer_accepted": c.medical_disclaimer_accepted,
                            "language": c.language,
                            "consent_source": c.consent_source,
                            "created_at": c.created_at.isoformat(),
                            "expires_at": c.expires_at.isoformat(),
                            "withdrawn_at": c.withdrawn_at.isoformat() if c.withdrawn_at else None
                        }
                        for c in consents
                    ],
                    "compliance_logs": [
                        {
                            "log_type": log.log_type,
                            "action": log.action,
                            "details": log.details,
                            "created_at": log.created_at.isoformat()
                        }
                        for log in logs
                    ]
                }
                
                self.log_compliance_event(
                    session_id_hash=session_hash,
                    log_type="data_export",
                    action="user_data_exported",
                    details={"record_count": len(consents) + len(logs)},
                    compliance_frameworks=["PDPA", "GDPR"]
                )
                
                return export_data
                
        except Exception as e:
            self.log_compliance_event(
                log_type="data_export",
                action="export_error",
                details={"error": str(e)},
                severity="critical"
            )
            return {}
    
    def check_compliance_status(self) -> Dict[str, Any]:
        """Check overall compliance status"""
        try:
            with Session(self.engine) as session:
                # Check if required legal documents exist
                required_docs = ['privacy_policy', 'terms', 'impressum', 'medical_disclaimer']
                languages = ['th', 'de', 'en']
                
                missing_docs = []
                for doc_type in required_docs:
                    for lang in languages:
                        doc = session.exec(
                            select(LegalDocument).where(
                                LegalDocument.document_type == doc_type,
                                LegalDocument.language == lang,
                                LegalDocument.is_active == True
                            )
                        ).first()
                        
                        if not doc:
                            missing_docs.append(f"{doc_type}_{lang}")
                
                # Check consent statistics
                total_consents = session.exec(select(CookieConsent)).all()
                active_consents = [c for c in total_consents if not c.withdrawn_at and c.expires_at > datetime.utcnow()]
                
                # Check pending data requests
                pending_requests = session.exec(
                    select(DataSubjectRequest).where(DataSubjectRequest.status.in_(['pending', 'verified', 'processing']))
                ).all()
                
                overdue_requests = [r for r in pending_requests if r.deadline < datetime.utcnow()]
                
                return {
                    "compliance_score": 100 - (len(missing_docs) * 10) - (len(overdue_requests) * 20),
                    "missing_documents": missing_docs,
                    "total_consents": len(total_consents),
                    "active_consents": len(active_consents),
                    "pending_data_requests": len(pending_requests),
                    "overdue_requests": len(overdue_requests),
                    "last_checked": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.log_compliance_event(
                log_type="compliance_check",
                action="status_check_error", 
                details={"error": str(e)},
                severity="critical"
            )
            return {"compliance_score": 0, "error": str(e)}


# Global service instance
legal_service = LegalComplianceService()