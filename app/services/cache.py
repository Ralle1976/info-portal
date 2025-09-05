"""
High-Performance Caching Service für QR-Info-Portal
Implementiert Redis-basiertes Caching mit Fallback
"""
import os
import hashlib
import json
import pickle
from typing import Any, Optional, Callable, List
from datetime import datetime, timedelta
from functools import wraps

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.logging_config import get_logger

logger = get_logger('cache')


class CacheService:
    """High-Performance Caching mit Redis-Fallback"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.cache_stats = {'hits': 0, 'misses': 0, 'errors': 0}
        
        # Redis Connection Setup
        if REDIS_AVAILABLE:
            try:
                redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
                self.redis_client = redis.from_url(redis_url, decode_responses=False)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis not available, using memory cache: {e}")
                self.redis_client = None
        else:
            logger.info("Redis not installed, using memory cache")
    
    def _generate_key(self, key: str, **kwargs) -> str:
        """Generiert Cache-Key mit optionalen Parametern"""
        if kwargs:
            key_data = f"{key}:{json.dumps(kwargs, sort_keys=True)}"
            return hashlib.md5(key_data.encode()).hexdigest()[:16]
        return key
    
    def get(self, key: str, **kwargs) -> Any:
        """Holt Wert aus Cache"""
        cache_key = self._generate_key(key, **kwargs)
        
        try:
            # Redis Cache
            if self.redis_client:
                value = self.redis_client.get(cache_key)
                if value is not None:
                    self.cache_stats['hits'] += 1
                    return pickle.loads(value)
            
            # Memory Cache Fallback
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if entry['expires_at'] > datetime.now():
                    self.cache_stats['hits'] += 1
                    return entry['value']
                else:
                    del self.memory_cache[cache_key]
            
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {cache_key}: {e}")
            self.cache_stats['errors'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300, **kwargs) -> bool:
        """Speichert Wert im Cache"""
        cache_key = self._generate_key(key, **kwargs)
        
        try:
            # Redis Cache
            if self.redis_client:
                serialized_value = pickle.dumps(value)
                self.redis_client.setex(cache_key, ttl_seconds, serialized_value)
                return True
            
            # Memory Cache Fallback
            self.memory_cache[cache_key] = {
                'value': value,
                'expires_at': datetime.now() + timedelta(seconds=ttl_seconds)
            }
            
            # Memory Cache Cleanup (keep only 1000 entries)
            if len(self.memory_cache) > 1000:
                oldest_keys = sorted(
                    self.memory_cache.keys(),
                    key=lambda k: self.memory_cache[k]['expires_at']
                )[:100]
                for old_key in oldest_keys:
                    del self.memory_cache[old_key]
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {cache_key}: {e}")
            self.cache_stats['errors'] += 1
            return False
    
    def delete(self, key: str, **kwargs) -> bool:
        """Löscht Wert aus Cache"""
        cache_key = self._generate_key(key, **kwargs)
        
        try:
            # Redis Cache
            if self.redis_client:
                self.redis_client.delete(cache_key)
            
            # Memory Cache
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error for key {cache_key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> bool:
        """Löscht alle Keys die einem Pattern entsprechen"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(f"{pattern}*")
                if keys:
                    self.redis_client.delete(*keys)
            
            # Memory Cache Pattern Clearing
            keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(pattern)]
            for key in keys_to_delete:
                del self.memory_cache[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Gibt Cache-Statistiken zurück"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'backend': 'redis' if self.redis_client else 'memory',
            'hit_rate': round(hit_rate, 2),
            **self.cache_stats,
            'memory_cache_size': len(self.memory_cache)
        }


# Global Cache Instance
cache = CacheService()


def cached(ttl_seconds: int = 300, key_func: Optional[Callable] = None):
    """Decorator für Function Caching"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                func_name = f"{func.__module__}.{func.__name__}"
                args_str = str(args) + str(sorted(kwargs.items()))
                cache_key = hashlib.md5(f"{func_name}:{args_str}".encode()).hexdigest()[:16]
            
            # Try cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            return result
        
        return wrapper
    return decorator


def cache_template_fragment(template_name: str, ttl_seconds: int = 300):
    """Cache für Template Fragmente"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate key based on template and params
            key_data = f"template:{template_name}:{str(kwargs)}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()[:16]
            
            # Try cache
            cached_html = cache.get(cache_key)
            if cached_html is not None:
                return cached_html
            
            # Render template and cache
            html = func(*args, **kwargs)
            cache.set(cache_key, html, ttl_seconds)
            return html
        
        return wrapper
    return decorator


def invalidate_cache_on_update(cache_patterns: List[str]):
    """Decorator um Cache bei Updates zu invalidieren"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Clear related cache patterns
            for pattern in cache_patterns:
                cache.clear_pattern(pattern)
                logger.info(f"Cache pattern '{pattern}' invalidated")
            
            return result
        return wrapper
    return decorator