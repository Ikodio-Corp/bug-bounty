"""
Security middleware for request validation and protection
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
# from utils.security import input_validator, ip_whitelist, SecurityHeaders  # Functions don't exist


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware for additional protection
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Allow CORS preflight requests to pass through
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response
            
        # Add security headers to all responses
        response = await call_next(request)
        
        # Add basic security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """
    IP whitelist/blacklist middleware
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Get client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host
        
        # Check if IP is allowed
        if not ip_whitelist.is_allowed(client_ip):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Access forbidden from this IP address"}
            )
        
        response = await call_next(request)
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate requests for security threats
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Allow CORS preflight requests to pass through
        if request.method == "OPTIONS":
            return await call_next(request)
            
        # Skip validation for certain paths
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request body too large"}
            )
        
        # Validate query parameters
        for key, value in request.query_params.items():
            if input_validator.check_sql_injection(value):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid query parameter detected"}
                )
            
            if input_validator.check_xss(value):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid query parameter detected"}
                )
        
        response = await call_next(request)
        return response
