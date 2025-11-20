"""
Input Validation Middleware for IKODIO BugBounty Platform
Comprehensive input validation and sanitization
"""

from fastapi import Request, HTTPException, status
from typing import Callable
import re
import html
from urllib.parse import unquote


class InputValidationMiddleware:
    """Validate and sanitize all incoming requests"""
    
    # Suspicious patterns that might indicate attacks
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
    ]
    
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
        r"('\s*or\s*'1'\s*=\s*'1)",
        r"(;\s*drop\s+table\s+)",
        r"(exec\s*\()",
        r"(insert\s+into\s+)",
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r'([;&|]\s*\w+)',
        r'(\$\(.*?\))',
        r'(`.*?`)',
        r'(\.\./)',
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\./',
        r'\.\.\\',
        r'%2e%2e%2f',
        r'%2e%2e/',
    ]
    
    def __init__(self, app):
        self.app = app
    
    def _check_xss(self, value: str) -> bool:
        """Check for XSS patterns"""
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    def _check_sql_injection(self, value: str) -> bool:
        """Check for SQL injection patterns"""
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    def _check_command_injection(self, value: str) -> bool:
        """Check for command injection patterns"""
        for pattern in self.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value):
                return True
        return False
    
    def _check_path_traversal(self, value: str) -> bool:
        """Check for path traversal patterns"""
        for pattern in self.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string input"""
        # HTML escape
        value = html.escape(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Normalize whitespace
        value = ' '.join(value.split())
        
        return value
    
    def _validate_value(self, value: str, path: str = "") -> str:
        """Validate a single value"""
        if not isinstance(value, str):
            return value
        
        # URL decode
        decoded = unquote(value)
        
        # Check for various attack patterns
        if self._check_xss(decoded):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Potential XSS attack detected in {path}"
            )
        
        if self._check_sql_injection(decoded):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Potential SQL injection detected in {path}"
            )
        
        if self._check_command_injection(decoded):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Potential command injection detected in {path}"
            )
        
        if self._check_path_traversal(decoded):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Potential path traversal detected in {path}"
            )
        
        return value
    
    def _validate_dict(self, data: dict, path: str = ""):
        """Recursively validate dictionary"""
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(value, str):
                self._validate_value(value, current_path)
            elif isinstance(value, dict):
                self._validate_dict(value, current_path)
            elif isinstance(value, list):
                self._validate_list(value, current_path)
    
    def _validate_list(self, data: list, path: str = ""):
        """Recursively validate list"""
        for i, value in enumerate(data):
            current_path = f"{path}[{i}]"
            
            if isinstance(value, str):
                self._validate_value(value, current_path)
            elif isinstance(value, dict):
                self._validate_dict(value, current_path)
            elif isinstance(value, list):
                self._validate_list(value, current_path)
    
    async def __call__(self, request: Request, call_next: Callable):
        # Skip validation for certain paths
        skip_paths = ["/docs", "/redoc", "/openapi.json", "/metrics", "/health"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Validate query parameters
        for key, value in request.query_params.items():
            self._validate_value(value, f"query.{key}")
        
        # Validate path parameters
        for key, value in request.path_params.items():
            self._validate_value(value, f"path.{key}")
        
        # Validate headers (selective)
        suspicious_headers = ["User-Agent", "Referer", "X-Forwarded-For"]
        for header in suspicious_headers:
            value = request.headers.get(header)
            if value:
                self._validate_value(value, f"header.{header}")
        
        # Validate JSON body (if present)
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    body = await request.json()
                    if isinstance(body, dict):
                        self._validate_dict(body, "body")
                    elif isinstance(body, list):
                        self._validate_list(body, "body")
                except Exception:
                    pass  # Let the route handler deal with invalid JSON
        
        response = await call_next(request)
        return response


async def input_validation_middleware(request: Request, call_next: Callable):
    """Input validation middleware function"""
    middleware = InputValidationMiddleware(None)
    return await middleware(request, call_next)
