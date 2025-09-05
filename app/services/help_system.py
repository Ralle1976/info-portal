"""
QR Info Portal - In-App Help System
Provides contextual help, tooltips, and guidance for users
"""

from typing import Dict, List, Optional
import json
import os
from flask import current_app
from werkzeug.local import LocalProxy

def safe_current_app():
    """Safely get current_app, return None if not available"""
    try:
        return current_app._get_current_object()
    except RuntimeError:
        return None

class HelpSystem:
    """Central help system providing contextual assistance throughout the application"""
    
    def __init__(self):
        self.help_data = {}
        self.load_help_content()
    
    def load_help_content(self):
        """Load help content from JSON files"""
        try:
            # Determine help directory - handle both app context and standalone
            app = safe_current_app()
            if app and hasattr(app, 'root_path'):
                help_dir = os.path.join(app.root_path, 'static', 'help')
            else:
                # Fallback for when not in app context
                help_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'help')
            
            # Load help content for different languages
            for lang in ['de', 'th', 'en']:
                help_file = os.path.join(help_dir, f'help_{lang}.json')
                if os.path.exists(help_file):
                    with open(help_file, 'r', encoding='utf-8') as f:
                        self.help_data[lang] = json.load(f)
                else:
                    self.help_data[lang] = self.get_default_help_content(lang)
                        
        except Exception as e:
            # Log only if current_app is available
            app = safe_current_app()
            if app and hasattr(app, 'logger'):
                app.logger.error(f"Error loading help content: {e}")
            else:
                print(f"Help System: Error loading help content: {e}")
            
            # Fallback to default content
            for lang in ['de', 'th', 'en']:
                self.help_data[lang] = self.get_default_help_content(lang)
    
    def get_help_for_page(self, page_id: str, language: str = 'de') -> Dict:
        """Get help content for a specific page"""
        if language not in self.help_data:
            language = 'de'  # Fallback to German
        
        page_help = self.help_data[language].get('pages', {}).get(page_id, {})
        
        return {
            'title': page_help.get('title', 'Hilfe'),
            'description': page_help.get('description', ''),
            'sections': page_help.get('sections', []),
            'quick_actions': page_help.get('quick_actions', []),
            'tooltips': page_help.get('tooltips', {}),
            'faqs': page_help.get('faqs', [])
        }
    
    def get_tooltip(self, element_id: str, page_id: str = 'general', language: str = 'de') -> str:
        """Get tooltip text for a specific UI element"""
        if language not in self.help_data:
            language = 'de'
        
        page_tooltips = self.help_data[language].get('pages', {}).get(page_id, {}).get('tooltips', {})
        general_tooltips = self.help_data[language].get('tooltips', {})
        
        return page_tooltips.get(element_id) or general_tooltips.get(element_id, '')
    
    def get_contextual_help(self, context: str, language: str = 'de') -> Dict:
        """Get contextual help based on current user action"""
        if language not in self.help_data:
            language = 'de'
        
        contextual_help = self.help_data[language].get('contextual', {}).get(context, {})
        
        return {
            'message': contextual_help.get('message', ''),
            'steps': contextual_help.get('steps', []),
            'tips': contextual_help.get('tips', []),
            'warnings': contextual_help.get('warnings', [])
        }
    
    def get_quick_start_guide(self, user_type: str = 'visitor', language: str = 'de') -> Dict:
        """Get quick start guide for different user types"""
        if language not in self.help_data:
            language = 'de'
        
        guide = self.help_data[language].get('quick_start', {}).get(user_type, {})
        
        return {
            'title': guide.get('title', 'Schnellstart'),
            'steps': guide.get('steps', []),
            'completed_message': guide.get('completed_message', 'Herzlichen Glückwunsch!')
        }
    
    def search_help(self, query: str, language: str = 'de') -> List[Dict]:
        """Search through help content"""
        if language not in self.help_data:
            language = 'de'
        
        results = []
        query_lower = query.lower()
        
        # Search through pages
        pages = self.help_data[language].get('pages', {})
        for page_id, page_data in pages.items():
            # Search in title and description
            if (query_lower in page_data.get('title', '').lower() or 
                query_lower in page_data.get('description', '').lower()):
                
                results.append({
                    'type': 'page',
                    'id': page_id,
                    'title': page_data.get('title', ''),
                    'description': page_data.get('description', ''),
                    'relevance': 'high'
                })
            
            # Search in sections
            for section in page_data.get('sections', []):
                if query_lower in section.get('content', '').lower():
                    results.append({
                        'type': 'section',
                        'page_id': page_id,
                        'title': section.get('title', ''),
                        'content': section.get('content', ''),
                        'relevance': 'medium'
                    })
        
        # Search through FAQs
        faqs = self.help_data[language].get('faqs', [])
        for faq in faqs:
            if (query_lower in faq.get('question', '').lower() or 
                query_lower in faq.get('answer', '').lower()):
                
                results.append({
                    'type': 'faq',
                    'question': faq.get('question', ''),
                    'answer': faq.get('answer', ''),
                    'relevance': 'high'
                })
        
        return results
    
    def get_default_help_content(self, language: str) -> Dict:
        """Default help content if files are not available"""
        
        if language == 'de':
            return {
                "pages": {
                    "home": {
                        "title": "Startseite",
                        "description": "Die Hauptseite des QR Info Portals mit aktuellen Informationen",
                        "sections": [
                            {
                                "title": "Status-Banner",
                                "content": "Zeigt den aktuellen Status der Praxis an - geöffnet, geschlossen, Urlaub, etc."
                            },
                            {
                                "title": "Öffnungszeiten",
                                "content": "Aktuelle Öffnungszeiten für heute, diese Woche und diesen Monat"
                            },
                            {
                                "title": "Kontakt",
                                "content": "Telefonnummer, E-Mail und Adresse der Praxis"
                            }
                        ],
                        "tooltips": {
                            "status_banner": "Aktueller Status der Praxis",
                            "language_switch": "Sprache ändern",
                            "qr_code": "QR-Code für einfachen Zugang"
                        },
                        "quick_actions": [
                            "Telefonnummer anrufen",
                            "E-Mail senden",
                            "Route in Google Maps öffnen"
                        ]
                    },
                    "admin_dashboard": {
                        "title": "Admin Dashboard",
                        "description": "Zentrale Verwaltung für das QR Info Portal",
                        "sections": [
                            {
                                "title": "Erste Schritte",
                                "content": "Nach der ersten Anmeldung sollten Sie Ihre Praxis-Informationen aktualisieren"
                            },
                            {
                                "title": "Status verwalten",
                                "content": "Ändern Sie den aktuellen Status (geöffnet, Urlaub, etc.)"
                            },
                            {
                                "title": "Öffnungszeiten",
                                "content": "Verwalten Sie reguläre Öffnungszeiten und Ausnahmen"
                            }
                        ],
                        "tooltips": {
                            "status_card": "Aktueller Status Ihrer Praxis",
                            "hours_card": "Öffnungszeiten verwalten",
                            "announcements_card": "Wichtige Mitteilungen bearbeiten"
                        }
                    }
                },
                "tooltips": {
                    "save_button": "Änderungen speichern",
                    "cancel_button": "Änderungen verwerfen",
                    "delete_button": "Element löschen",
                    "edit_button": "Element bearbeiten"
                },
                "contextual": {
                    "first_login": {
                        "message": "Willkommen im Admin-Bereich! Lassen Sie uns Ihre Praxis einrichten.",
                        "steps": [
                            "Praxis-Name und Kontaktdaten eingeben",
                            "Öffnungszeiten festlegen",
                            "Aktuellen Status setzen",
                            "Erste Mitteilung erstellen"
                        ]
                    },
                    "status_change": {
                        "message": "Status wird sofort für alle Besucher sichtbar sein.",
                        "tips": [
                            "Bei Urlaub: Rückkehrdatum angeben",
                            "Bei Notfällen: Kontaktinformationen hinterlassen"
                        ]
                    }
                },
                "faqs": [
                    {
                        "question": "Wie ändere ich den Status?",
                        "answer": "Gehen Sie zu 'Status' im Admin-Menü und wählen Sie den gewünschten Status aus."
                    },
                    {
                        "question": "Werden Änderungen sofort sichtbar?",
                        "answer": "Ja, alle Änderungen werden sofort auf der öffentlichen Seite angezeigt."
                    }
                ]
            }
        elif language == 'th':
            return {
                "pages": {
                    "home": {
                        "title": "หน้าแรก",
                        "description": "หน้าหลักของ QR Info Portal พร้อมข้อมูลล่าสุด",
                        "sections": [
                            {
                                "title": "แบนเนอร์สถานะ",
                                "content": "แสดงสถานะปัจจุบันของคลินิก - เปิด, ปิด, ลาพักร้อน, ฯลฯ"
                            }
                        ]
                    }
                },
                "faqs": []
            }
        else:  # English
            return {
                "pages": {
                    "home": {
                        "title": "Homepage",
                        "description": "Main page of the QR Info Portal with current information",
                        "sections": [
                            {
                                "title": "Status Banner",
                                "content": "Shows current practice status - open, closed, vacation, etc."
                            }
                        ]
                    }
                },
                "faqs": []
            }

# Global help system instance
help_system = HelpSystem()

def get_help_context(page_id: str, language: str = 'de') -> Dict:
    """Template helper function to get help context"""
    return help_system.get_help_for_page(page_id, language)

def get_tooltip_text(element_id: str, page_id: str = 'general', language: str = 'de') -> str:
    """Template helper function to get tooltip text"""
    return help_system.get_tooltip(element_id, page_id, language)