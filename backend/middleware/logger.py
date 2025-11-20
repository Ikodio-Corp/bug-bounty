"""
Request Logger Middleware
Advanced logging with request/response tracking
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import time
import logging
import json
from typing import Callable

logger = logging.getLogger("ikodio.requests")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Log all requests with detailed information
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Generate request ID
        request_id = self._generate_request_id()
        
        # Log request start
        start_time = time.time()
        
        logger.info(
            f"[{request_id}] {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("User-Agent"),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"[{request_id}] Completed in {duration:.3f}s with status {response.status_code}",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration_seconds": duration,
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration:.3f}"
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                f"[{request_id}] Failed after {duration:.3f}s: {str(e)}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "duration_seconds": duration,
                }
            )
            raise
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
