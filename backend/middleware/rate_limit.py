"""
Rate limiting middleware
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time

from core.redis import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
    
    async def dispatch(self, request: Request, call_next: Callable):
        client_ip = request.client.host
        redis_client = get_redis()
        
        key = f"rate_limit:{client_ip}"
        current = redis_client.get(key)
        
        if current and int(current) >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds."
            )
        
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.period)
        pipe.execute()
        
        response = await call_next(request)
        
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.calls - int(redis_client.get(key) or 0)))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.period)
        
        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware with security"""
    
    def __init__(self, app, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["http://localhost:3000"]
    
    async def dispatch(self, request: Request, call_next: Callable):
        origin = request.headers.get("origin")
        
        response = await call_next(request)
        
        if origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With"
            response.headers["Access-Control-Max-Age"] = "600"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for monitoring"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"{request.method} {request.url.path} "
            f"completed in {process_time:.3f}s "
            f"with status {response.status_code}"
        )
        
        return response
