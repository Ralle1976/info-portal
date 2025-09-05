"""
Legal Labels Management Service
Verwaltet alle konfigurierbaren Texte und Labels für Legal Compliance
Unterstützt länderspezifische Datumsformate und Überschriften
"""

from typing import Dict, Any, Optional
from datetime import datetime, date
import json
from sqlmodel import Session, select
from ..models import Settings
from ..database import engine


class LegalLabelsService:
    """Service für konfigurierbare Legal Labels und Texte"""
    
    def __init__(self):
        self.engine = engine
        self._cache = {}
        
    def get_legal_config(self, language: str = 'th') -> Dict[str, Any]:
        """Hole komplette Legal-Konfiguration für eine Sprache"""
        cache_key = f"legal_config_{language}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        try:
            with Session(self.engine) as session:
                config_record = session.exec(
                    select(Settings).where(Settings.key == f"legal_labels_{language}")
                ).first()
                
                if config_record:
                    config = config_record.value
                else:
                    # Fallback auf Standard-Konfiguration
                    config = self._get_default_config(language)
                    
                self._cache[cache_key] = config
                return config
                
        except Exception:
            return self._get_default_config(language)
    
    def update_legal_config(self, language: str, config: Dict[str, Any]) -> bool:
        """Aktualisiere Legal-Konfiguration für eine Sprache"""
        try:
            with Session(self.engine) as session:
                config_record = session.exec(
                    select(Settings).where(Settings.key == f"legal_labels_{language}")
                ).first()
                
                if config_record:
                    config_record.value = config
                    config_record.updated_at = datetime.utcnow()
                else:
                    config_record = Settings(
                        key=f"legal_labels_{language}",
                        value=config
                    )
                    session.add(config_record)
                
                session.commit()
                
                # Cache invalidieren
                cache_key = f"legal_config_{language}"
                if cache_key in self._cache:
                    del self._cache[cache_key]
                    
                return True
                
        except Exception:
            return False
    
    def get_label(self, key: str, language: str = 'th', default: str = None) -> str:
        """Hole ein spezifisches Label"""
        config = self.get_legal_config(language)
        
        # Nested key support (z.B. "compliance.dashboard.title")
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default or key
                
        return value if isinstance(value, str) else default or key
    
    def format_date(self, date_obj: date, language: str = 'th') -> str:
        """Formatiere Datum länderspezifisch"""
        config = self.get_legal_config(language)
        date_format = config.get('date_formats', {}).get('date', '%d.%m.%Y')
        
        if language == 'th':
            # Thai Buddhistic year
            thai_year = date_obj.year + 543
            return date_obj.strftime(date_format).replace(str(date_obj.year), str(thai_year))
        elif language == 'en':
            return date_obj.strftime('%m/%d/%Y')
        else:  # DE
            return date_obj.strftime('%d.%m.%Y')
    
    def format_datetime(self, datetime_obj: datetime, language: str = 'th') -> str:
        """Formatiere Datum/Zeit länderspezifisch"""
        config = self.get_legal_config(language)
        datetime_format = config.get('date_formats', {}).get('datetime', '%d.%m.%Y %H:%M')
        
        if language == 'th':
            # Thai Buddhistic year
            thai_year = datetime_obj.year + 543
            return datetime_obj.strftime(datetime_format).replace(str(datetime_obj.year), str(thai_year))
        elif language == 'en':
            return datetime_obj.strftime('%m/%d/%Y %I:%M %p')
        else:  # DE
            return datetime_obj.strftime('%d.%m.%Y %H:%M')
    
    def get_data_protection_authority(self, language: str = 'th') -> Dict[str, str]:
        """Hole Datenschutzbehörde-Informationen länderspezifisch"""
        config = self.get_legal_config(language)
        return config.get('data_protection_authority', {})
    
    def get_legal_contact(self, language: str = 'th') -> Dict[str, str]:
        """Hole Legal Contact Informationen"""
        config = self.get_legal_config(language)
        return config.get('legal_contact', {})
    
    def _get_default_config(self, language: str) -> Dict[str, Any]:
        """Standard-Konfiguration für eine Sprache"""
        
        if language == 'th':
            return {
                "site_title": "ห้องปฏิบัติการพัทยา",
                "compliance": {
                    "dashboard": {
                        "title": "แดชบอร์ดการปฏิบัติตามกฎหมาย",
                        "description": "การจัดการความปฏิบัติตาม PDPA ประเทศไทยและ GDPR สหภาพยุโรป",
                        "compliance_score": "คะแนนการปฏิบัติตาม",
                        "active_consents": "การยินยอมที่ใช้งานอยู่",
                        "pending_requests": "คำขอที่รอดำเนินการ",
                        "overdue_requests": "คำขอที่เกินกำหนด"
                    },
                    "documents": {
                        "title": "เอกสารทางกฎหมาย",
                        "privacy_policy": "นโยบายความเป็นส่วนตัว",
                        "terms_of_service": "ข้อกำหนดการให้บริการ",
                        "impressum": "ข้อมูลทางกฎหมาย",
                        "medical_disclaimer": "ข้อความปฏิเสธความรับผิดชอบทางการแพทย์"
                    },
                    "consent": {
                        "title": "การจัดการความยินยอม",
                        "necessary": "จำเป็น",
                        "functional": "การทำงาน",
                        "analytics": "การวิเคราะห์",
                        "marketing": "การตลาด",
                        "medical_disclaimer": "ข้อปฏิเสธทางการแพทย์"
                    },
                    "rights": {
                        "access": "สิทธิในการเข้าถึงข้อมูล",
                        "rectification": "สิทธิในการแก้ไขข้อมูล",
                        "erasure": "สิทธิในการลบข้อมูล",
                        "portability": "สิทธิในการนำข้อมูลออก",
                        "objection": "สิทธิในการคัดค้าน",
                        "restriction": "สิทธิในการจำกัดการประมวลผล"
                    }
                },
                "date_formats": {
                    "date": "%d/%m/%Y",
                    "datetime": "%d/%m/%Y %H:%M น.",
                    "time": "%H:%M น."
                },
                "data_protection_authority": {
                    "name": "สำนักงานคณะกรรมการคุ้มครองข้อมูลส่วนบุคคล",
                    "name_en": "Personal Data Protection Committee Office",
                    "website": "https://www.pdpc.go.th",
                    "email": "info@pdpc.go.th",
                    "phone": "+66 2 142 1033",
                    "address": "ชั้น 7 อาคารรัฐประศาสนภักดี ศูนย์ราชการเฉลิมพระเกียรติ แขวงทุ่งสองห้อง เขตหลักสี่ กรุงเทพฯ 10210"
                },
                "legal_contact": {
                    "title": "เจ้าหน้าที่คุ้มครองข้อมูล",
                    "name": "ฝ่ายกฎหมาย ห้องปฏิบัติการพัทยา",
                    "email": "privacy@laborpattaya.com",
                    "phone": "+66 38 123 456",
                    "address": "ซอยบัวขาว พัทยา ประเทศไทย"
                },
                "legal_basis": {
                    "pdpa_consent": "ความยินยอม (มาตรา 19 PDPA)",
                    "pdpa_legitimate": "ประโยชน์โดยชอบธรรม (มาตรา 24 PDPA)",
                    "pdpa_contract": "การปฏิบัติตามสัญญา (มาตรา 24 PDPA)",
                    "pdpa_legal": "การปฏิบัติตามกฎหมาย (มาตรา 24 PDPA)"
                }
            }
            
        elif language == 'de':
            return {
                "site_title": "Labor Pattaya",
                "compliance": {
                    "dashboard": {
                        "title": "Legal Compliance Dashboard",
                        "description": "Verwaltung der Thailand PDPA und EU DSGVO Compliance",
                        "compliance_score": "Compliance-Score",
                        "active_consents": "Aktive Einwilligungen",
                        "pending_requests": "Ausstehende Anfragen",
                        "overdue_requests": "Überfällige Anfragen"
                    },
                    "documents": {
                        "title": "Rechtsdokumente",
                        "privacy_policy": "Datenschutzerklärung",
                        "terms_of_service": "Nutzungsbedingungen",
                        "impressum": "Impressum",
                        "medical_disclaimer": "Medizinischer Haftungsausschluss"
                    },
                    "consent": {
                        "title": "Einwilligungsverwaltung",
                        "necessary": "Notwendig",
                        "functional": "Funktional",
                        "analytics": "Analytik",
                        "marketing": "Marketing",
                        "medical_disclaimer": "Medizinischer Haftungsausschluss"
                    },
                    "rights": {
                        "access": "Recht auf Auskunft",
                        "rectification": "Recht auf Berichtigung",
                        "erasure": "Recht auf Löschung",
                        "portability": "Recht auf Datenübertragbarkeit",
                        "objection": "Widerspruchsrecht",
                        "restriction": "Recht auf Einschränkung der Verarbeitung"
                    }
                },
                "date_formats": {
                    "date": "%d.%m.%Y",
                    "datetime": "%d.%m.%Y %H:%M",
                    "time": "%H:%M"
                },
                "data_protection_authority": {
                    "name": "Personal Data Protection Committee Office Thailand",
                    "name_de": "Datenschutzbehörde Thailand",
                    "website": "https://www.pdpc.go.th",
                    "email": "info@pdpc.go.th",
                    "phone": "+66 2 142 1033",
                    "address": "7th Floor, Government Complex, Chaeng Watthana Road, Bangkok 10210, Thailand"
                },
                "legal_contact": {
                    "title": "Datenschutzbeauftragter",
                    "name": "Rechtsabteilung Labor Pattaya",
                    "email": "privacy@laborpattaya.com",
                    "phone": "+66 38 123 456",
                    "address": "Soi Buakhao, Pattaya, Thailand"
                },
                "legal_basis": {
                    "gdpr_consent": "Einwilligung (Art. 6 Abs. 1 lit. a DSGVO)",
                    "gdpr_contract": "Vertrag (Art. 6 Abs. 1 lit. b DSGVO)",
                    "gdpr_legal": "Rechtliche Verpflichtung (Art. 6 Abs. 1 lit. c DSGVO)",
                    "gdpr_legitimate": "Berechtigte Interessen (Art. 6 Abs. 1 lit. f DSGVO)"
                }
            }
            
        else:  # EN
            return {
                "site_title": "Laboratory Pattaya",
                "compliance": {
                    "dashboard": {
                        "title": "Legal Compliance Dashboard",
                        "description": "Management of Thailand PDPA and EU GDPR Compliance",
                        "compliance_score": "Compliance Score",
                        "active_consents": "Active Consents",
                        "pending_requests": "Pending Requests",
                        "overdue_requests": "Overdue Requests"
                    },
                    "documents": {
                        "title": "Legal Documents",
                        "privacy_policy": "Privacy Policy",
                        "terms_of_service": "Terms of Service",
                        "impressum": "Legal Notice",
                        "medical_disclaimer": "Medical Disclaimer"
                    },
                    "consent": {
                        "title": "Consent Management",
                        "necessary": "Necessary",
                        "functional": "Functional",
                        "analytics": "Analytics",
                        "marketing": "Marketing",
                        "medical_disclaimer": "Medical Disclaimer"
                    },
                    "rights": {
                        "access": "Right to Access",
                        "rectification": "Right to Rectification",
                        "erasure": "Right to Erasure",
                        "portability": "Right to Data Portability",
                        "objection": "Right to Object",
                        "restriction": "Right to Restriction of Processing"
                    }
                },
                "date_formats": {
                    "date": "%m/%d/%Y",
                    "datetime": "%m/%d/%Y %I:%M %p",
                    "time": "%I:%M %p"
                },
                "data_protection_authority": {
                    "name": "Personal Data Protection Committee Office",
                    "name_th": "สำนักงานคณะกรรมการคุ้มครองข้อมูลส่วนบุคคล",
                    "website": "https://www.pdpc.go.th",
                    "email": "info@pdpc.go.th",
                    "phone": "+66 2 142 1033",
                    "address": "7th Floor, Government Complex, Chaeng Watthana Road, Bangkok 10210, Thailand"
                },
                "legal_contact": {
                    "title": "Data Protection Officer",
                    "name": "Legal Department Laboratory Pattaya",
                    "email": "privacy@laborpattaya.com",
                    "phone": "+66 38 123 456",
                    "address": "Soi Buakhao, Pattaya, Thailand"
                },
                "legal_basis": {
                    "pdpa_consent": "Consent (Section 19 PDPA)",
                    "pdpa_legitimate": "Legitimate Interest (Section 24 PDPA)",
                    "pdpa_contract": "Contract Performance (Section 24 PDPA)",
                    "pdpa_legal": "Legal Obligation (Section 24 PDPA)",
                    "gdpr_consent": "Consent (Art. 6(1)(a) GDPR)",
                    "gdpr_contract": "Contract (Art. 6(1)(b) GDPR)",
                    "gdpr_legal": "Legal Obligation (Art. 6(1)(c) GDPR)",
                    "gdpr_legitimate": "Legitimate Interests (Art. 6(1)(f) GDPR)"
                }
            }
    
    def get_all_languages(self) -> list:
        """Hole alle verfügbaren Sprachen"""
        return ['th', 'de', 'en']
    
    def export_config(self, language: str) -> Dict[str, Any]:
        """Exportiere Konfiguration für Backup"""
        return self.get_legal_config(language)
    
    def import_config(self, language: str, config: Dict[str, Any]) -> bool:
        """Importiere Konfiguration aus Backup"""
        return self.update_legal_config(language, config)
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, list]:
        """Validiere Konfiguration und gebe Fehler zurück"""
        errors = {}
        required_sections = ['compliance', 'date_formats', 'data_protection_authority', 'legal_contact']
        
        for section in required_sections:
            if section not in config:
                if 'missing_sections' not in errors:
                    errors['missing_sections'] = []
                errors['missing_sections'].append(section)
        
        # Validiere Datumsformate
        if 'date_formats' in config:
            date_formats = config['date_formats']
            required_formats = ['date', 'datetime', 'time']
            
            for fmt in required_formats:
                if fmt not in date_formats:
                    if 'missing_date_formats' not in errors:
                        errors['missing_date_formats'] = []
                    errors['missing_date_formats'].append(fmt)
        
        return errors
    
    def clear_cache(self):
        """Leere den Label-Cache"""
        self._cache.clear()


# Global service instance
legal_labels = LegalLabelsService()