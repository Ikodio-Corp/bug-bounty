"""
Rate Limiting Middleware
Prevent API abuse and DDoS attacks
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
import time
from collections import defaultdict
import asyncio


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, rate: int, per: int):
        """
        Args:
            rate: Number of requests allowed
            per: Time window in seconds
        """
        self.rate = rate
        self.per = per
        self.buckets: Dict[str, Tuple[float, int]] = defaultdict(lambda: (time.time(), rate))
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        last_time, tokens = self.buckets[key]
        
        # Refill tokens based on time passed
        time_passed = now - last_time
        new_tokens = min(self.rate, tokens + (time_passed * self.rate / self.per))
        
        if new_tokens >= 1:
            self.buckets[key] = (now, new_tokens - 1)
            return True
        else:
            self.buckets[key] = (now, new_tokens)
            return False
    
    def get_remaining(self, key: str) -> int:
        """Get remaining tokens"""
        _, tokens = self.buckets.get(key, (time.time(), self.rate))
        return int(tokens)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with different tiers
    
    Tiers:
    - Anonymous: 100 requests/hour
    - Authenticated: 1000 requests/hour
    - Premium: 10000 requests/hour
    - Enterprise: Unlimited
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.anonymous_limiter = RateLimiter(rate=100, per=3600)  # 100/hour
        self.auth_limiter = RateLimiter(rate=1000, per=3600)  # 1000/hour
        self.premium_limiter = RateLimiter(rate=10000, per=3600)  # 10k/hour
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/docs", "/api/redoc"]:
            return await call_next(request)
        
        # Determine user tier and limiter
        user_id = self._get_user_id(request)
        user_tier = self._get_user_tier(request)
        
        if user_tier == "enterprise":
            # No rate limiting for enterprise
            pass
        elif user_tier == "premium":
            limiter = self.premium_limiter
            key = f"premium:{user_id}"
        elif user_tier == "authenticated":
            limiter = self.auth_limiter
            key = f"auth:{user_id}"
        else:
            limiter = self.anonymous_limiter
            key = f"anon:{self._get_client_ip(request)}"
        
        # Check rate limit
        if user_tier != "enterprise":
            if not limiter.is_allowed(key):
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "retry_after": 60,
                        "tier": user_tier,
                        "upgrade_url": "/api/plans"
                    }
                )
        
        response = await call_next(request)
        
        # Add rate limit headers
        if user_tier != "enterprise":
            response.headers["X-RateLimit-Limit"] = str(limiter.rate)
            response.headers["X-RateLimit-Remaining"] = str(limiter.get_remaining(key))
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + limiter.per))
        
        return response
    
    def _get_user_id(self, request: Request) -> str:
        """Extract user ID from request"""
        # TODO: Extract from JWT token
        return request.headers.get("X-User-ID", "anonymous")
    
    def _get_user_tier(self, request: Request) -> str:
        """Get user subscription tier"""
        # TODO: Get from database
        tier = request.headers.get("X-User-Tier", "anonymous")
        return tier.lower()
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
