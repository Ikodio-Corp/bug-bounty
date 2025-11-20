from fastapi import Request
from integrations.sentry_client import sentry_service
from services.audit_service import AuditService
from core.database import get_db
import time

async def audit_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    response_time = time.time() - start_time
    
    user_id = None
    if hasattr(request.state, "user"):
        user_id = request.state.user.id
    
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")
    
    db = next(get_db())
    audit_service = AuditService(db)
    
    try:
        await audit_service.log_api_call(
            user_id=user_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            response_time=response_time,
            ip_address=ip_address,
            user_agent=user_agent
        )
    except Exception as e:
        sentry_service.capture_exception(e, tags={"middleware": "audit"})
    
    return response
