"""
QR Info Portal - Help Routes
Provides dedicated endpoints for the interactive help system
"""

from flask import Blueprint, jsonify, request, render_template, current_app
from app.services.help_system import help_system
from app.services.i18n import I18nService

help_bp = Blueprint('help', __name__, url_prefix='/help')

@help_bp.route('/search')
def search_help():
    """Search through help content via AJAX"""
    query = request.args.get('q', '').strip()
    language = I18nService.get_current_language()
    
    if not query:
        return jsonify({'results': []})
    
    try:
        results = help_system.search_help(query, language)
        return jsonify({'results': results})
    except Exception as e:
        current_app.logger.error(f"Help search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

@help_bp.route('/context/<page_id>')
def get_page_help():
    """Get help context for a specific page"""
    page_id = request.view_args.get('page_id', 'home')
    language = I18nService.get_current_language()
    
    try:
        help_data = help_system.get_help_for_page(page_id, language)
        return jsonify(help_data)
    except Exception as e:
        current_app.logger.error(f"Error getting help for page {page_id}: {e}")
        return jsonify({'error': 'Help data not available'}), 500

@help_bp.route('/tooltip/<element_id>')
def get_tooltip():
    """Get tooltip text for a specific UI element"""
    element_id = request.view_args.get('element_id')
    page_id = request.args.get('page', 'general')
    language = I18nService.get_current_language()
    
    try:
        tooltip = help_system.get_tooltip(element_id, page_id, language)
        return jsonify({'tooltip': tooltip})
    except Exception as e:
        current_app.logger.error(f"Error getting tooltip for {element_id}: {e}")
        return jsonify({'error': 'Tooltip not available'}), 500

@help_bp.route('/quick-start/<user_type>')
def get_quick_start_guide():
    """Get quick start guide for different user types"""
    user_type = request.view_args.get('user_type', 'visitor')
    language = I18nService.get_current_language()
    
    try:
        guide = help_system.get_quick_start_guide(user_type, language)
        return jsonify(guide)
    except Exception as e:
        current_app.logger.error(f"Error getting quick start guide: {e}")
        return jsonify({'error': 'Guide not available'}), 500

@help_bp.route('/contextual/<context>')
def get_contextual_help():
    """Get contextual help based on user action"""
    context = request.view_args.get('context')
    language = I18nService.get_current_language()
    
    try:
        help_data = help_system.get_contextual_help(context, language)
        return jsonify(help_data)
    except Exception as e:
        current_app.logger.error(f"Error getting contextual help for {context}: {e}")
        return jsonify({'error': 'Contextual help not available'}), 500

@help_bp.route('/faq')
def faq_page():
    """Dedicated FAQ page"""
    language = I18nService.get_current_language()
    
    try:
        # Get all FAQs from help data
        help_data = help_system.help_data.get(language, {})
        faqs = help_data.get('faqs', [])
        
        # Group FAQs by category
        faq_categories = {}
        for faq in faqs:
            category = faq.get('category', 'General')
            if category not in faq_categories:
                faq_categories[category] = []
            faq_categories[category].append(faq)
        
        return render_template('help/faq.html', 
                             faq_categories=faq_categories,
                             page_title='Häufige Fragen')
                             
    except Exception as e:
        current_app.logger.error(f"Error loading FAQ page: {e}")
        return render_template('help/faq.html', 
                             faq_categories={},
                             page_title='Häufige Fragen')

@help_bp.route('/manual')
def user_manual():
    """Interactive user manual"""
    language = I18nService.get_current_language()
    
    try:
        # Get help data for all main pages
        pages_help = {}
        main_pages = ['home', 'admin_dashboard', 'admin_status', 'admin_hours', 'admin_announcements']
        
        for page_id in main_pages:
            pages_help[page_id] = help_system.get_help_for_page(page_id, language)
        
        return render_template('help/manual.html', 
                             pages_help=pages_help,
                             page_title='Benutzerhandbuch')
                             
    except Exception as e:
        current_app.logger.error(f"Error loading user manual: {e}")
        return render_template('help/manual.html', 
                             pages_help={},
                             page_title='Benutzerhandbuch')

@help_bp.route('/getting-started')
def getting_started():
    """Interactive getting started guide"""
    user_type = request.args.get('type', 'visitor')
    language = I18nService.get_current_language()
    
    try:
        guide = help_system.get_quick_start_guide(user_type, language)
        
        return render_template('help/getting_started.html', 
                             guide=guide,
                             user_type=user_type,
                             page_title='Erste Schritte')
                             
    except Exception as e:
        current_app.logger.error(f"Error loading getting started guide: {e}")
        return render_template('help/getting_started.html', 
                             guide={},
                             user_type=user_type,
                             page_title='Erste Schritte')

@help_bp.route('/data/<language>')
def help_data():
    """Return help data as JSON for client-side use"""
    try:
        language = request.view_args.get('language', 'de')
        if language not in help_system.help_data:
            language = 'de'  # Fallback
            
        data = help_system.help_data.get(language, {})
        return jsonify(data)
        
    except Exception as e:
        current_app.logger.error(f"Error serving help data: {e}")
        return jsonify(help_system.get_default_help_content(language)), 500

@help_bp.route('/keyboard-shortcuts')
def keyboard_shortcuts():
    """Show available keyboard shortcuts"""
    shortcuts = {
        'F1': 'Schnellstart-Assistent öffnen',
        'Alt + H': 'Hilfe-Panel umschalten',
        'Escape': 'Alle Hilfe-Fenster schließen',
        '?': 'Tastaturkürzel anzeigen (falls fokussiert)'
    }
    
    return jsonify({'shortcuts': shortcuts})