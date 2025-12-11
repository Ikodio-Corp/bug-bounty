"""
API Rate Limiting Middleware for ML Endpoints
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Optional
from datetime import datetime, timedelta
import asyncio

from backend.core.redis import redis_client
from backend.core.logging import setup_logging

logger = setup_logging()


class MLRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware specifically for ML endpoints
    Prevents abuse and ensures fair usage
    """
    
    def __init__(
        self,
        app,
        default_rate_limit: int = 100,
        default_window_seconds: int = 3600,
        burst_limit: int = 10,
        burst_window_seconds: int = 60
    ):
        super().__init__(app)
        self.default_rate_limit = default_rate_limit
        self.default_window_seconds = default_window_seconds
        self.burst_limit = burst_limit
        self.burst_window_seconds = burst_window_seconds
        
        # Endpoint-specific limits
        self.endpoint_limits = {
            "/ml/feedback/submit": {"limit": 1000, "window": 3600},
            "/ml/confidence/evaluate": {"limit": 500, "window": 3600},
            "/ml/confidence/calibrate": {"limit": 10, "window": 3600},
            "/ml/performance": {"limit": 100, "window": 3600},
            "/ml/statistics": {"limit": 200, "window": 3600},
            "/ml/models/compare": {"limit": 50, "window": 3600},
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Check if this is an ML endpoint
        if not request.url.path.startswith("/ml/"):
            return await call_next(request)
        
        # Get user identifier
        user_id = self._get_user_id(request)
        
        if not user_id:
            return await call_next(request)
        
        # Check rate limits
        try:
            is_allowed, limit_info = await self._check_rate_limit(
                user_id,
                request.url.path,
                request.method
            )
            
            if not is_allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Try again in {limit_info['retry_after']} seconds",
                        "limit": limit_info["limit"],
                        "remaining": 0,
                        "reset_at": limit_info["reset_at"]
                    },
                    headers={
                        "X-RateLimit-Limit": str(limit_info["limit"]),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(limit_info["reset_at"]),
                        "Retry-After": str(limit_info["retry_after"])
                    }
                )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(limit_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(limit_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(limit_info["reset_at"])
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return await call_next(request)
    
    async def _check_rate_limit(
        self,
        user_id: str,
        path: str,
        method: str
    ) -> tuple[bool, Dict]:
        """
        Check if request is within rate limits
        
        Returns:
            Tuple of (is_allowed, limit_info)
        """
        # Get endpoint-specific limits or use defaults
        endpoint_config = self._get_endpoint_config(path)
        rate_limit = endpoint_config["limit"]
        window_seconds = endpoint_config["window"]
        
        # Create rate limit keys
        key = f"rate_limit:ml:{user_id}:{path}:{method}"
        burst_key = f"rate_limit:burst:ml:{user_id}:{path}:{method}"
        
        current_time = datetime.utcnow()
        
        # Check burst limit (short window)
        burst_count = await self._get_request_count(burst_key)
        if burst_count >= self.burst_limit:
            reset_time = await self._get_key_ttl(burst_key)
            return False, {
                "limit": self.burst_limit,
                "remaining": 0,
                "reset_at": int((current_time + timedelta(seconds=reset_time)).timestamp()),
                "retry_after": reset_time
            }
        
        # Check main rate limit
        request_count = await self._get_request_count(key)
        
        if request_count >= rate_limit:
            reset_time = await self._get_key_ttl(key)
            return False, {
                "limit": rate_limit,
                "remaining": 0,
                "reset_at": int((current_time + timedelta(seconds=reset_time)).timestamp()),
                "retry_after": reset_time
            }
        
        # Increment counters
        await self._increment_counter(key, window_seconds)
        await self._increment_counter(burst_key, self.burst_window_seconds)
        
        return True, {
            "limit": rate_limit,
            "remaining": rate_limit - request_count - 1,
            "reset_at": int((current_time + timedelta(seconds=window_seconds)).timestamp()),
            "retry_after": 0
        }
    
    async def _get_request_count(self, key: str) -> int:
        """Get current request count from Redis"""
        try:
            count = await redis_client.get(key)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"Error getting request count: {e}")
            return 0
    
    async def _increment_counter(self, key: str, ttl: int):
        """Increment request counter in Redis"""
        try:
            await redis_client.incr(key)
            await redis_client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Error incrementing counter: {e}")
    
    async def _get_key_ttl(self, key: str) -> int:
        """Get TTL for Redis key"""
        try:
            ttl = await redis_client.ttl(key)
            return ttl if ttl > 0 else 0
        except Exception as e:
            logger.error(f"Error getting TTL: {e}")
            return 0
    
    def _get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request"""
        try:
            # Try to get from user object if available
            if hasattr(request.state, "user"):
                return str(request.state.user.id)
            
            # Fallback to IP address
            client_ip = request.client.host if request.client else "unknown"
            return f"ip:{client_ip}"
            
        except Exception as e:
            logger.error(f"Error getting user ID: {e}")
            return None
    
    def _get_endpoint_config(self, path: str) -> Dict:
        """Get rate limit configuration for endpoint"""
        for endpoint, config in self.endpoint_limits.items():
            if endpoint in path:
                return config
        
        return {
            "limit": self.default_rate_limit,
            "window": self.default_window_seconds
        }


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts limits based on system load
    """
    
    def __init__(self):
        self.base_limits = {
            "free": 50,
            "pro": 200,
            "enterprise": 1000
        }
        self.current_multiplier = 1.0
    
    async def get_user_limit(
        self,
        user_tier: str,
        current_load: float
    ) -> int:
        """
        Get adaptive rate limit for user based on tier and system load
        
        Args:
            user_tier: User subscription tier
            current_load: Current system load (0-1)
            
        Returns:
            Adjusted rate limit
        """
        base_limit = self.base_limits.get(user_tier, self.base_limits["free"])
        
        # Reduce limits if system is under heavy load
        if current_load > 0.8:
            self.current_multiplier = 0.5
        elif current_load > 0.6:
            self.current_multiplier = 0.75
        else:
            self.current_multiplier = 1.0
        
        return int(base_limit * self.current_multiplier)
    
    async def get_system_load(self) -> float:
        """
        Get current system load
        
        Returns:
            Load factor between 0 and 1
        """
        try:
            # Get active requests from Redis
            active_key = "system:active_ml_requests"
            active_requests = await redis_client.get(active_key)
            active_requests = int(active_requests) if active_requests else 0
            
            # Calculate load (simple implementation)
            max_concurrent = 100
            load = min(active_requests / max_concurrent, 1.0)
            
            return load
            
        except Exception as e:
            logger.error(f"Error getting system load: {e}")
            return 0.0


# Global rate limiter instance
adaptive_limiter = AdaptiveRateLimiter()
