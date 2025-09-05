"""
Appointment Booking API Routes for QR-Info-Portal
Thai-specific appointment booking endpoints

IMPORTANT: This module is prepared but NOT ACTIVATED
Enable via FEATURE_BOOKING=true in environment
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, date, time
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from sqlmodel import Session
import os
from app.database import get_session
from app.services.booking import BookingManager, BookingServiceError, SlotNotAvailableError, BookingValidationError
from app.services.i18n import I18nService
from app.models_booking import BookingService, ServiceType, ContactMethod, BookingStatus
import logging

# Check if booking feature is enabled
FEATURE_BOOKING = os.getenv('FEATURE_BOOKING', 'false').lower() == 'true'

bp = Blueprint('appointments', __name__, url_prefix='/api/appointments')
logger = logging.getLogger(__name__)


def booking_feature_required(f):
    """Decorator to check if booking feature is enabled"""
    def decorated_function(*args, **kwargs):
        if not FEATURE_BOOKING:
            return jsonify({
                'success': False,
                'error': 'FEATURE_DISABLED',
                'message': 'Booking feature is not enabled'
            }), 503
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@bp.route('/services', methods=['GET'])
@booking_feature_required
def get_services():
    """Get available booking services"""
    try:
        session = get_session()
    try:
        db_session = session
            # Get language from request
            lang = request.args.get('lang', 'th')
            
            # Get active services
            services = db_session.query(BookingService).filter(
                BookingService.active == True
            ).order_by(BookingService.sort_order).all()
            
            services_data = []
            for service in services:
                services_data.append({
                    'id': service.id,
                    'service_type': service.service_type,
                    'name': service.name.get(lang, service.name.get('th', 'บริการ')),
                    'description': service.description.get(lang, service.description.get('th', '')),
                    'duration_minutes': service.duration_minutes,
                    'requires_fasting': service.requires_fasting,
                    'preparation_instructions': service.preparation_instructions.get(lang, ''),
                    'price_thb': service.price_thb,
                    'walk_in_allowed': service.walk_in_allowed
                })
            
            return jsonify({
                'success': True,
                'services': services_data
            })
            
    except Exception as e:
        logger.error(f"Error fetching services: {e}")
        return jsonify({
            'success': False,
            'error': 'SERVER_ERROR',
            'message': 'Failed to fetch services'
        }), 500


@bp.route('/slots', methods=['GET'])
@booking_feature_required
def get_available_slots():
    """Get available booking slots"""
    try:
        # Validate required parameters
        service_id = request.args.get('service_id', type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        preferred_times = request.args.getlist('preferred_times')
        
        if not all([service_id, start_date_str]):
            return jsonify({
                'success': False,
                'error': 'INVALID_PARAMS',
                'message': 'service_id and start_date are required'
            }), 400
        
        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else start_date
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'INVALID_DATE_FORMAT',
                'message': 'Use YYYY-MM-DD format for dates'
            }), 400
        
        session = get_session()
    try:
        db_session = session
            booking_manager = BookingManager(db_session)
            
            slots = booking_manager.get_available_slots(
                service_id=service_id,
                start_date=start_date,
                end_date=end_date,
                preferred_times=preferred_times or None
            )
            
            return jsonify({
                'success': True,
                'slots': slots,
                'total_count': len(slots)
            })
            
    except BookingValidationError as e:
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error fetching slots: {e}")
        return jsonify({
            'success': False,
            'error': 'SERVER_ERROR',
            'message': 'Failed to fetch available slots'
        }), 500


@bp.route('', methods=['POST'])
@booking_feature_required
def create_booking():
    """Create a new booking appointment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['service_id', 'booking_date', 'booking_time', 'contact_phone', 'first_name', 'last_name']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': 'MISSING_FIELDS',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Parse date and time
        try:
            booking_date = datetime.strptime(data['booking_date'], '%Y-%m-%d').date()
            booking_time = datetime.strptime(data['booking_time'], '%H:%M').time()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'INVALID_DATETIME',
                'message': 'Use YYYY-MM-DD for date and HH:MM for time'
            }), 400
        
        session = get_session()
    try:
        db_session = session
            booking_manager = BookingManager(db_session)
            
            # Create booking
            booking = booking_manager.create_booking(
                service_id=data['service_id'],
                booking_date=booking_date,
                booking_time=booking_time,
                contact_phone=data['contact_phone'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data.get('email'),
                line_user_id=data.get('line_user_id'),
                preferred_language=data.get('preferred_language', 'th'),
                patient_notes=data.get('patient_notes'),
                family_members=data.get('family_members')
            )
            
            return jsonify({
                'success': True,
                'booking': {
                    'reference': booking.booking_reference,
                    'confirmation_code': booking.confirmation_code,
                    'booking_date': booking.booking_date.isoformat(),
                    'booking_time': booking.booking_time.strftime('%H:%M'),
                    'buddhist_date': booking.buddhist_date,
                    'status': booking.status
                }
            }), 201
            
    except SlotNotAvailableError:
        return jsonify({
            'success': False,
            'error': 'SLOT_NOT_AVAILABLE',
            'message': 'The requested time slot is no longer available'
        }), 409
    except BookingValidationError as e:
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        return jsonify({
            'success': False,
            'error': 'SERVER_ERROR',
            'message': 'Failed to create booking'
        }), 500


@bp.route('/<booking_reference>', methods=['GET'])
@booking_feature_required
def get_booking_details(booking_reference: str):
    """Get booking details by reference"""
    try:
        session = get_session()
    try:
        db_session = session
            booking_manager = BookingManager(db_session)
            
            # Get booking (this will raise error if not found)
            booking = booking_manager._get_booking_by_reference(booking_reference)
            
            # Get service details
            service = db_session.get(BookingService, booking.service_id)
            
            return jsonify({
                'success': True,
                'booking': {
                    'reference': booking.booking_reference,
                    'service_name': service.name if service else 'Unknown Service',
                    'booking_date': booking.booking_date.isoformat(),
                    'booking_time': booking.booking_time.strftime('%H:%M'),
                    'buddhist_date': booking.buddhist_date,
                    'duration_minutes': booking.duration_minutes,
                    'status': booking.status,
                    'patient_notes': booking.patient_notes,
                    'queue_number': booking.queue_number,
                    'estimated_wait_minutes': booking.estimated_wait_minutes,
                    'created_at': booking.created_at.isoformat()
                }
            })
            
    except BookingValidationError as e:
        return jsonify({
            'success': False,
            'error': 'NOT_FOUND',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error fetching booking: {e}")
        return jsonify({
            'success': False,
            'error': 'SERVER_ERROR',
            'message': 'Failed to fetch booking details'
        }), 500


@bp.route('/<booking_reference>/confirm', methods=['POST'])
@booking_feature_required
def confirm_booking(booking_reference: str):
    """Confirm a booking with confirmation code"""
    try:
        data = request.get_json()
        confirmation_code = data.get('confirmation_code')
        
        if not confirmation_code:
            return jsonify({
                'success': False,
                'error': 'MISSING_CONFIRMATION_CODE',
                'message': 'Confirmation code is required'
            }), 400
        
        session = get_session()
    try:
        db_session = session
            booking_manager = BookingManager(db_session)
            
            booking = booking_manager.confirm_booking(booking_reference, confirmation_code)
            
            return jsonify({
                'success': True,
                'booking': {
                    'reference': booking.booking_reference,
                    'status': booking.status,
                    'confirmed_at': booking.confirmed_at.isoformat() if booking.confirmed_at else None
                }
            })
            
    except BookingValidationError as e:
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error confirming booking: {e}")
        return jsonify({
            'success': False,
            'error': 'SERVER_ERROR',
            'message': 'Failed to confirm booking'
        }), 500


@bp.route('/<booking_reference>/cancel', methods=['PUT'])
@booking_feature_required
def cancel_booking(booking_reference: str):
    """Cancel a booking"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', '')
        
        session = get_session()
    try:
        db_session = session
            booking_manager = BookingManager(db_session)
            
            booking = booking_manager.cancel_booking(
                booking_reference=booking_reference,
                reason=reason,
                cancelled_by="patient"
            )
            
            return jsonify({
                'success': True,
                'booking': {
                    'reference': booking.booking_reference,
                    'status': booking.status
                }
            })
            
    except BookingValidationError as e:
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error cancelling booking: {e}")
        return jsonify({
            'success': False,
            'error': 'SERVER_ERROR',
            'message': 'Failed to cancel booking'
        }), 500


@bp.route('/<booking_reference>/reschedule', methods=['POST'])
@booking_feature_required
def reschedule_booking(booking_reference: str):
    """Reschedule a booking to new date/time"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all([data.get('new_date'), data.get('new_time')]):
            return jsonify({
                'success': False,
                'error': 'MISSING_FIELDS',
                'message': 'new_date and new_time are required'
            }), 400
        
        # Parse new date and time
        try:
            new_date = datetime.strptime(data['new_date'], '%Y-%m-%d').date()
            new_time = datetime.strptime(data['new_time'], '%H:%M').time()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'INVALID_DATETIME',
                'message': 'Use YYYY-MM-DD for date and HH:MM for time'
            }), 400
        
        session = get_session()
    try:
        db_session = session
            booking_manager = BookingManager(db_session)
            
            new_booking = booking_manager.reschedule_booking(
                booking_reference=booking_reference,
                new_date=new_date,
                new_time=new_time,
                reason=data.get('reason', '')
            )
            
            return jsonify({
                'success': True,
                'new_booking': {
                    'reference': new_booking.booking_reference,
                    'confirmation_code': new_booking.confirmation_code,
                    'booking_date': new_booking.booking_date.isoformat(),
                    'booking_time': new_booking.booking_time.strftime('%H:%M'),
                    'status': new_booking.status
                }
            })
            
    except SlotNotAvailableError:
        return jsonify({
            'success': False,
            'error': 'SLOT_NOT_AVAILABLE',
            'message': 'The requested new time slot is not available'
        }), 409
    except BookingValidationError as e:
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error rescheduling booking: {e}")
        return jsonify({
            'success': False,
            'error': 'SERVER_ERROR',
            'message': 'Failed to reschedule booking'
        }), 500


@bp.route('/statistics/<stat_date>', methods=['GET'])
@booking_feature_required
def get_daily_statistics(stat_date: str):
    """Get booking statistics for a specific date (Admin only for now)"""
    try:
        # Parse date
        try:
            date_obj = datetime.strptime(stat_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'INVALID_DATE_FORMAT',
                'message': 'Use YYYY-MM-DD format for date'
            }), 400
        
        session = get_session()
    try:
        db_session = session
            booking_manager = BookingManager(db_session)
            
            stats = booking_manager.get_daily_statistics(date_obj)
            
            return jsonify({
                'success': True,
                'statistics': stats
            })
            
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        return jsonify({
            'success': False,
            'error': 'SERVER_ERROR',
            'message': 'Failed to fetch statistics'
        }), 500


# Widget and Frontend Routes

@bp.route('/widget', methods=['GET'])
@booking_feature_required
def booking_widget():
    """Render booking widget"""
    lang = request.args.get('lang', 'th')
    service_id = request.args.get('service_id', type=int)
    
    try:
        session = get_session()
    try:
        db_session = session
            # Get available services
            services = db_session.query(BookingService).filter(
                BookingService.active == True
            ).order_by(BookingService.sort_order).all()
            
            # If specific service requested, filter
            if service_id:
                services = [s for s in services if s.id == service_id]
            
            return render_template('components/booking_widget.html',
                                 services=services,
                                 lang=lang,
                                 contact_methods=ContactMethod,
                                 service_types=ServiceType)
    
    except Exception as e:
        logger.error(f"Error rendering booking widget: {e}")
        return "Booking widget temporarily unavailable", 500