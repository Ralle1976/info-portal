"""
Geocoding Service for QR Info Portal
Automatically generates coordinates from addresses
"""

import requests
import logging
from typing import Optional, Tuple, Dict, Any
import time

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for converting addresses to coordinates"""
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'QR-Info-Portal-Pattaya/1.0 (Medical Lab Geocoding)'
        }
    
    def get_coordinates_from_address(self, address: str, country: str = "Thailand") -> Optional[Tuple[float, float]]:
        """
        Get latitude and longitude from address
        
        Args:
            address: Street address or place name
            country: Country to search in (default: Thailand)
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            # Prepare search query
            full_address = f"{address}, {country}" if country not in address else address
            
            params = {
                'q': full_address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'th' if country.lower() == 'thailand' else None
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            logger.info(f"Geocoding address: {full_address}")
            
            # Make request with rate limiting
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Geocoding API error: {response.status_code}")
                return None
            
            data = response.json()
            
            if not data:
                logger.warning(f"No results found for address: {address}")
                return None
            
            result = data[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            
            logger.info(f"Found coordinates: {lat}, {lon} for {address}")
            
            # Respect OpenStreetMap usage policy (1 request per second)
            time.sleep(1)
            
            return (lat, lon)
            
        except requests.RequestException as e:
            logger.error(f"Network error during geocoding: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Data parsing error during geocoding: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during geocoding: {e}")
            return None
    
    def get_address_details(self, address: str, country: str = "Thailand") -> Optional[Dict[str, Any]]:
        """
        Get detailed information about an address
        
        Args:
            address: Street address or place name
            country: Country to search in
        
        Returns:
            Dictionary with detailed address information or None
        """
        try:
            full_address = f"{address}, {country}" if country not in address else address
            
            params = {
                'q': full_address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1,
                'countrycodes': 'th' if country.lower() == 'thailand' else None
            }
            
            params = {k: v for k, v in params.items() if v is not None}
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            if not data:
                return None
            
            result = data[0]
            
            # Extract useful information
            details = {
                'latitude': float(result['lat']),
                'longitude': float(result['lon']),
                'display_name': result.get('display_name', ''),
                'formatted_address': result.get('display_name', ''),
                'address_components': result.get('address', {}),
                'place_id': result.get('place_id'),
                'osm_type': result.get('osm_type'),
                'osm_id': result.get('osm_id'),
                'importance': result.get('importance', 0)
            }
            
            # Sleep to respect rate limits
            time.sleep(1)
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting address details: {e}")
            return None
    
    def generate_maps_link(self, latitude: float, longitude: float, label: str = "") -> str:
        """
        Generate Google Maps link from coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate  
            label: Optional label for the location
        
        Returns:
            Google Maps URL
        """
        if label:
            # Format: https://maps.google.com/?q=lat,lng(Label)
            return f"https://maps.google.com/?q={latitude},{longitude}({label})"
        else:
            # Format: https://maps.google.com/?q=lat,lng
            return f"https://maps.google.com/?q={latitude},{longitude}"
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate if coordinates are reasonable for Thailand
        
        Args:
            latitude: Latitude to validate
            longitude: Longitude to validate
        
        Returns:
            True if coordinates seem valid for Thailand
        """
        # Thailand bounds (approximate)
        # Latitude: 5.6 to 20.5
        # Longitude: 97.3 to 105.6
        
        if not (-90 <= latitude <= 90):
            return False
        if not (-180 <= longitude <= 180):
            return False
            
        # Check if in Thailand region (loose bounds)
        if 5.0 <= latitude <= 21.0 and 97.0 <= longitude <= 106.0:
            return True
            
        # Accept coordinates that might be close to Thailand
        logger.warning(f"Coordinates {latitude}, {longitude} are outside typical Thailand bounds")
        return True  # Don't be too restrictive
    
    def update_config_coordinates(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Update configuration with geocoded coordinates
        
        Args:
            address: Address to geocode
        
        Returns:
            Dictionary with updated location data or None
        """
        details = self.get_address_details(address)
        
        if not details:
            return None
        
        lat = details['latitude']
        lng = details['longitude']
        
        if not self.validate_coordinates(lat, lng):
            logger.warning(f"Invalid coordinates for Thailand: {lat}, {lng}")
            return None
        
        location_data = {
            'address': details['formatted_address'],
            'latitude': lat,
            'longitude': lng,
            'maps_link': self.generate_maps_link(lat, lng, "Labor Pattaya"),
            'geocoded_at': time.time(),
            'geocoding_source': 'OpenStreetMap/Nominatim'
        }
        
        return location_data


# Create service instance
geocoding_service = GeocodingService()


def geocode_address(address: str, country: str = "Thailand") -> Optional[Tuple[float, float]]:
    """
    Convenience function to geocode an address
    
    Args:
        address: Address to geocode
        country: Country for geocoding
    
    Returns:
        Tuple of (latitude, longitude) or None
    """
    return geocoding_service.get_coordinates_from_address(address, country)


def generate_maps_url(latitude: float, longitude: float, label: str = "") -> str:
    """
    Convenience function to generate Google Maps URL
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        label: Optional location label
    
    Returns:
        Google Maps URL
    """
    return geocoding_service.generate_maps_link(latitude, longitude, label)