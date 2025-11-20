from fastapi import Request
from utils.security_utils import SecurityHeaders

async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    
    headers = SecurityHeaders.get_headers()
    for header, value in headers.items():
        response.headers[header] = value
    
    return response
