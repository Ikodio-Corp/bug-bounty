"""
Advanced caching utilities for performance optimization
"""
import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
from core.redis import get_redis


class CacheManager:
    """Centralized cache management with Redis"""
    
    def __init__(self):
        self.redis = get_redis()
        self.default_ttl = 3600  # 1 hour
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            return self.redis.setex(key, ttl, serialized)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return 0
    
    def invalidate_user_cache(self, user_id: int):
        """Invalidate all cache entries for a user"""
        pattern = f"cache:*user:{user_id}*"
        return self.delete_pattern(pattern)
    
    def invalidate_scan_cache(self, scan_id: int):
        """Invalidate all cache entries for a scan"""
        pattern = f"cache:*scan:{scan_id}*"
        return self.delete_pattern(pattern)
    
    def invalidate_bug_cache(self, bug_id: int):
        """Invalidate all cache entries for a bug"""
        pattern = f"cache:*bug:{bug_id}*"
        return self.delete_pattern(pattern)


cache_manager = CacheManager()


def cache_result(ttl: int = 3600, key_prefix: str = "default"):
    """
    Decorator to cache function results
    
    Usage:
        @cache_result(ttl=1800, key_prefix="user_profile")
        def get_user_profile(user_id: int):
            return expensive_database_query(user_id)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def cache_paginated_result(ttl: int = 600, key_prefix: str = "paginated"):
    """
    Decorator for caching paginated results
    Includes page and limit in cache key
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, page: int = 1, limit: int = 10, **kwargs):
            cache_key = cache_manager._generate_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                page=page,
                limit=limit,
                **kwargs
            )
            
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            result = func(*args, page=page, limit=limit, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


class CacheWarmer:
    """Pre-populate cache with frequently accessed data"""
    
    def __init__(self):
        self.cache = cache_manager
    
    def warm_user_data(self, user_id: int):
        """Pre-cache user related data"""
        from backend.services.auth_service import AuthService
        from backend.core.database import get_db
        
        db = next(get_db())
        auth_service = AuthService(db)
        
        # Cache user profile
        user = auth_service.get_user_by_id(user_id)
        if user:
            key = f"cache:user:{user_id}:profile"
            self.cache.set(key, user.__dict__, ttl=7200)
    
    def warm_leaderboard(self):
        """Pre-cache leaderboard data"""
        from backend.services.auth_service import AuthService
        from backend.core.database import get_db
        
        db = next(get_db())
        # Cache top 100 users
        key = "cache:leaderboard:top100"
        # Query and cache leaderboard
        # self.cache.set(key, leaderboard_data, ttl=1800)
    
    def warm_marketplace(self):
        """Pre-cache marketplace popular items"""
        from backend.services.marketplace_service import MarketplaceService
        from backend.core.database import get_db
        
        db = next(get_db())
        service = MarketplaceService(db)
        
        # Cache top tools
        key = "cache:marketplace:top_tools"
        # self.cache.set(key, top_tools, ttl=3600)


cache_warmer = CacheWarmer()
