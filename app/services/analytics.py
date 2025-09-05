"""
Analytics Service for QR Info Portal
Tracks visitor behavior and generates statistics for admin dashboard
Privacy-compliant with PDPA/GDPR requirements
"""

import hashlib
import json
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Any
from user_agents import parse as parse_user_agent
from sqlmodel import Session, select, func
from app.models import VisitorAnalytics, DailyStatistics
from app.database import get_session


class AnalyticsService:
    """Service for tracking and analyzing visitor behavior"""
    
    def __init__(self):
        self.session_timeout_minutes = 30
    
    def _get_client_ip(self, request) -> str:
        """
        Get real client IP address, handling reverse proxies and load balancers
        Production-ready for HTTPS/CDN setups
        """
        # Check for IP in standard proxy headers (for production HTTPS setups)
        proxy_headers = [
            'HTTP_X_FORWARDED_FOR',      # Standard proxy header
            'HTTP_X_REAL_IP',            # Nginx proxy
            'HTTP_CF_CONNECTING_IP',     # Cloudflare
            'HTTP_X_CLUSTER_CLIENT_IP',  # Cluster load balancer
            'HTTP_FORWARDED_FOR',        # RFC 7239
            'HTTP_FORWARDED'             # RFC 7239
        ]
        
        for header in proxy_headers:
            value = request.environ.get(header)
            if value:
                # Take first IP if comma-separated (proxy chain)
                ip = value.split(',')[0].strip()
                if self._is_valid_ip(ip):
                    return ip
        
        # Fallback to direct connection IP
        return request.environ.get('REMOTE_ADDR', '127.0.0.1')
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            parts = ip.split('.')
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except (ValueError, AttributeError):
            return False
    
    def _is_secure_connection(self, request) -> bool:
        """
        Check if connection is secure (HTTPS)
        Handles various proxy/load balancer configurations
        """
        # Direct HTTPS check
        if request.environ.get('HTTPS') == 'on':
            return True
            
        # Check scheme
        if request.environ.get('REQUEST_SCHEME') == 'https':
            return True
            
        # Check proxy headers for HTTPS
        if request.environ.get('HTTP_X_FORWARDED_PROTO') == 'https':
            return True
            
        if request.environ.get('HTTP_X_FORWARDED_SSL') == 'on':
            return True
            
        # Check standard port
        server_port = request.environ.get('SERVER_PORT', '80')
        if server_port == '443':
            return True
            
        return False
    
    def _get_protocol_version(self, request) -> str:
        """Get HTTP protocol version (HTTP/1.1, HTTP/2, HTTP/3)"""
        # Try to get from server variables
        protocol = request.environ.get('SERVER_PROTOCOL', 'HTTP/1.1')
        
        # Check for HTTP/2 indicators
        if request.environ.get('HTTP2') == 'on':
            return 'HTTP/2'
            
        # Check via headers that indicate HTTP/2
        if 'h2' in request.environ.get('HTTP_UPGRADE', '').lower():
            return 'HTTP/2'
            
        return protocol
        
    def _get_session_hash(self, ip_address: str, user_agent: str) -> str:
        """Create anonymized session hash from IP and User Agent"""
        # Create hash that doesn't store actual IP/User Agent
        combined = f"{ip_address}:{user_agent}:{date.today().isoformat()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _parse_user_agent(self, user_agent_string: str) -> Dict[str, str]:
        """Parse user agent to extract device info"""
        try:
            ua = parse_user_agent(user_agent_string)
            
            # Device type detection
            if ua.is_mobile:
                device_type = "mobile"
            elif ua.is_tablet:
                device_type = "tablet"
            else:
                device_type = "desktop"
                
            return {
                'device_type': device_type,
                'browser_family': ua.browser.family.lower() if ua.browser.family else None,
                'operating_system': ua.os.family.lower() if ua.os.family else None
            }
        except Exception:
            return {
                'device_type': 'unknown',
                'browser_family': None,
                'operating_system': None
            }
    
    def _detect_referrer_type(self, referrer: str, user_agent: str) -> str:
        """Detect how user arrived at the site"""
        if not referrer:
            # Check if it might be a QR code scan based on user agent patterns
            if any(keyword in user_agent.lower() for keyword in ['camera', 'scanner', 'qr']):
                return 'qr'
            return 'direct'
        
        referrer_lower = referrer.lower()
        
        # Social media platforms
        social_platforms = ['facebook.com', 'line.me', 'instagram.com', 'twitter.com', 'tiktok.com']
        if any(platform in referrer_lower for platform in social_platforms):
            return 'social'
        
        # Search engines
        search_engines = ['google.com', 'bing.com', 'duckduckgo.com', 'yahoo.com']
        if any(search in referrer_lower for search in search_engines):
            return 'search'
        
        # If referrer exists but doesn't match known patterns
        return 'referral'
    
    def track_visit(self, 
                   request,
                   page_path: str = "/",
                   qr_campaign: Optional[str] = None,
                   analytics_consent: bool = False) -> Optional[int]:
        """
        Track a visitor page visit
        Returns analytics record ID if created, None if consent not given
        """
        
        # Only track if user has given analytics consent
        if not analytics_consent:
            return None
            
        try:
            # Get request information - Production-ready for HTTPS/HTTP2
            ip_address = self._get_client_ip(request)
            user_agent = request.environ.get('HTTP_USER_AGENT', '')
            referrer = request.environ.get('HTTP_REFERER', '')
            preferred_language = request.environ.get('HTTP_ACCEPT_LANGUAGE', 'th')[:2]
            
            # Check if connection is secure (HTTPS)
            is_secure = self._is_secure_connection(request)
            
            # Parse user agent
            device_info = self._parse_user_agent(user_agent)
            
            # Create session hash
            session_hash = self._get_session_hash(ip_address, user_agent)
            
            # Detect referrer type
            referrer_type = self._detect_referrer_type(referrer, user_agent)
            
            # Check if returning visitor (seen this session hash before)
            with get_session() as db:
                existing_visitor = db.exec(
                    select(VisitorAnalytics)
                    .where(VisitorAnalytics.session_hash == session_hash)
                    .where(VisitorAnalytics.visit_date >= date.today() - timedelta(days=30))
                ).first()
                
                is_returning = existing_visitor is not None
                
                # Detect QR code scan
                is_qr_scan = (
                    qr_campaign is not None or 
                    referrer_type == 'qr' or 
                    'qr=' in request.query_string.decode('utf-8', errors='ignore')
                )
                
                # Get protocol version
                protocol_version = self._get_protocol_version(request)
                
                # Create analytics record
                analytics_record = VisitorAnalytics(
                    visit_date=date.today(),
                    page_path=page_path,
                    referrer_type=referrer_type,
                    is_secure_connection=is_secure,
                    protocol_version=protocol_version,
                    device_type=device_info['device_type'],
                    browser_family=device_info['browser_family'],
                    operating_system=device_info['operating_system'],
                    preferred_language=preferred_language,
                    qr_code_scan=is_qr_scan,
                    qr_campaign=qr_campaign,
                    session_hash=session_hash,
                    is_returning_visitor=is_returning,
                    analytics_consent=True,
                    ip_anonymized=True
                )
                
                db.add(analytics_record)
                db.commit()
                db.refresh(analytics_record)
                
                # Update daily statistics
                self._update_daily_stats(db, analytics_record)
                
                return analytics_record.id
                
        except Exception as e:
            print(f"Analytics tracking error: {e}")
            return None
    
    def _update_daily_stats(self, db: Session, analytics_record: VisitorAnalytics):
        """Update daily aggregated statistics"""
        try:
            # Get or create today's statistics
            today_stats = db.exec(
                select(DailyStatistics)
                .where(DailyStatistics.stats_date == date.today())
            ).first()
            
            if not today_stats:
                today_stats = DailyStatistics(stats_date=date.today())
                db.add(today_stats)
            
            # Update counters
            today_stats.total_visits += 1
            
            if not analytics_record.is_returning_visitor:
                today_stats.unique_visitors += 1
            else:
                today_stats.returning_visitors += 1
                
            if analytics_record.qr_code_scan:
                today_stats.qr_scans += 1
            
            # Page view counts
            if analytics_record.page_path == "/":
                today_stats.homepage_views += 1
            elif analytics_record.page_path == "/week":
                today_stats.week_views += 1
            elif analytics_record.page_path == "/month":
                today_stats.month_views += 1
            elif "/kiosk" in analytics_record.page_path:
                today_stats.kiosk_views += 1
            
            # Device breakdown
            if analytics_record.device_type == "mobile":
                today_stats.mobile_visits += 1
            elif analytics_record.device_type == "tablet":
                today_stats.tablet_visits += 1
            elif analytics_record.device_type == "desktop":
                today_stats.desktop_visits += 1
            
            # Language breakdown
            if analytics_record.preferred_language == "th":
                today_stats.thai_visitors += 1
            elif analytics_record.preferred_language == "en":
                today_stats.english_visitors += 1
            elif analytics_record.preferred_language == "de":
                today_stats.german_visitors += 1
            
            # Referrer breakdown
            if analytics_record.referrer_type == "direct":
                today_stats.direct_visits += 1
            elif analytics_record.referrer_type == "qr":
                today_stats.qr_visits += 1
            elif analytics_record.referrer_type == "social":
                today_stats.social_visits += 1
            elif analytics_record.referrer_type == "search":
                today_stats.search_visits += 1
            
            today_stats.updated_at = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            print(f"Error updating daily statistics: {e}")
            db.rollback()
    
    def get_daily_stats(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get daily statistics for a date range"""
        try:
            with get_session() as db:
                stats = db.exec(
                    select(DailyStatistics)
                    .where(DailyStatistics.stats_date >= start_date)
                    .where(DailyStatistics.stats_date <= end_date)
                    .order_by(DailyStatistics.stats_date)
                ).all()
                
                return [
                    {
                        'date': stat.stats_date.isoformat(),
                        'total_visits': stat.total_visits,
                        'unique_visitors': stat.unique_visitors,
                        'qr_scans': stat.qr_scans,
                        'returning_visitors': stat.returning_visitors,
                        'homepage_views': stat.homepage_views,
                        'week_views': stat.week_views,
                        'month_views': stat.month_views,
                        'mobile_visits': stat.mobile_visits,
                        'tablet_visits': stat.tablet_visits,
                        'desktop_visits': stat.desktop_visits,
                        'thai_visitors': stat.thai_visitors,
                        'english_visitors': stat.english_visitors,
                        'german_visitors': stat.german_visitors,
                        'direct_visits': stat.direct_visits,
                        'qr_visits': stat.qr_visits,
                        'social_visits': stat.social_visits,
                        'search_visits': stat.search_visits
                    }
                    for stat in stats
                ]
        except Exception as e:
            print(f"Error getting daily stats: {e}")
            return []
    
    def get_summary_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get summary statistics for the last N days"""
        try:
            start_date = date.today() - timedelta(days=days)
            
            with get_session() as db:
                # Get aggregated totals
                result = db.exec(
                    select(
                        func.sum(DailyStatistics.total_visits).label('total_visits'),
                        func.sum(DailyStatistics.unique_visitors).label('unique_visitors'),
                        func.sum(DailyStatistics.qr_scans).label('qr_scans'),
                        func.sum(DailyStatistics.homepage_views).label('homepage_views'),
                        func.sum(DailyStatistics.mobile_visits).label('mobile_visits'),
                        func.sum(DailyStatistics.thai_visitors).label('thai_visitors'),
                        func.avg(DailyStatistics.total_visits).label('avg_daily_visits')
                    )
                    .where(DailyStatistics.stats_date >= start_date)
                ).first()
                
                if not result:
                    return {
                        'period_days': days,
                        'total_visits': 0,
                        'unique_visitors': 0,
                        'qr_scans': 0,
                        'homepage_views': 0,
                        'mobile_percentage': 0,
                        'thai_percentage': 0,
                        'avg_daily_visits': 0
                    }
                
                total_visits = result.total_visits or 0
                mobile_visits = result.mobile_visits or 0
                thai_visitors = result.thai_visitors or 0
                
                return {
                    'period_days': days,
                    'total_visits': total_visits,
                    'unique_visitors': result.unique_visitors or 0,
                    'qr_scans': result.qr_scans or 0,
                    'homepage_views': result.homepage_views or 0,
                    'mobile_percentage': round((mobile_visits / total_visits * 100), 1) if total_visits > 0 else 0,
                    'thai_percentage': round((thai_visitors / total_visits * 100), 1) if total_visits > 0 else 0,
                    'avg_daily_visits': round(result.avg_daily_visits or 0, 1)
                }
                
        except Exception as e:
            print(f"Error getting summary stats: {e}")
            return {
                'period_days': days,
                'total_visits': 0,
                'unique_visitors': 0,
                'qr_scans': 0,
                'homepage_views': 0,
                'mobile_percentage': 0,
                'thai_percentage': 0,
                'avg_daily_visits': 0
            }
    
    def get_popular_times(self, days: int = 7) -> Dict[str, Any]:
        """Get popular visit times analysis"""
        try:
            start_date = date.today() - timedelta(days=days)
            
            with get_session() as db:
                # Get hourly visit distribution
                visits_by_hour = db.exec(
                    select(
                        func.extract('hour', VisitorAnalytics.visit_time).label('hour'),
                        func.count(VisitorAnalytics.id).label('visit_count')
                    )
                    .where(VisitorAnalytics.visit_date >= start_date)
                    .where(VisitorAnalytics.analytics_consent == True)
                    .group_by(func.extract('hour', VisitorAnalytics.visit_time))
                    .order_by(func.extract('hour', VisitorAnalytics.visit_time))
                ).all()
                
                hourly_data = {int(row.hour): row.visit_count for row in visits_by_hour}
                
                # Find peak hour
                peak_hour = max(hourly_data, key=hourly_data.get) if hourly_data else 9
                peak_visits = hourly_data.get(peak_hour, 0)
                
                return {
                    'period_days': days,
                    'hourly_visits': hourly_data,
                    'peak_hour': peak_hour,
                    'peak_hour_visits': peak_visits,
                    'business_hours_visits': sum(hourly_data.get(hour, 0) for hour in range(8, 17)),
                    'after_hours_visits': sum(hourly_data.get(hour, 0) for hour in list(range(0, 8)) + list(range(17, 24)))
                }
                
        except Exception as e:
            print(f"Error getting popular times: {e}")
            return {
                'period_days': days,
                'hourly_visits': {},
                'peak_hour': 9,
                'peak_hour_visits': 0,
                'business_hours_visits': 0,
                'after_hours_visits': 0
            }


# Global analytics service instance
analytics_service = AnalyticsService()