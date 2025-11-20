"""
Authentication Middleware
JWT token validation and user context
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from typing import Optional
import jwt

from core.config import settings


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Validate JWT tokens and attach user context to requests
    """
    
    # Paths that don't require authentication
    PUBLIC_PATHS = [
        "/health",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/api/auth/register",
        "/api/auth/login",
        "/api/auth/refresh",
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in self.PUBLIC_PATHS):
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            raise HTTPException(
                status_code=401,
                detail="Missing authentication token"
            )
        
        # Validate Bearer token format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication header format"
            )
        
        token = parts[1]
        
        # Validate JWT token
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Attach user info to request state
            request.state.user_id = payload.get("sub")
            request.state.user_role = payload.get("role")
            request.state.user_email = payload.get("email")
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}"
            )
        
        # Continue processing
        response = await call_next(request)
        return response
