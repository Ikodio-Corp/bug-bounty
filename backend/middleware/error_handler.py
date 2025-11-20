"""
Error Handler Middleware
Centralized error handling and formatting with Sentry integration
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from integrations.sentry_client import sentry_service
import logging
import traceback
import time

logger = logging.getLogger("ikodio.errors")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler with structured error responses and Sentry integration
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        with sentry_service.start_transaction(
            name=f"{request.method} {request.url.path}",
            op="http.server"
        ) as transaction:
            transaction.set_tag("http.method", request.method)
            transaction.set_tag("http.url", str(request.url))
            
            try:
                response = await call_next(request)
                
                process_time = time.time() - start_time
                transaction.set_measurement("http.response_time", process_time * 1000, "millisecond")
                transaction.set_tag("http.status_code", response.status_code)
                
                if process_time > 1.0:
                    sentry_service.capture_message(
                        f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s",
                        level="warning",
                        tags={"slow_request": "true", "endpoint": request.url.path}
                    )
                
                response.headers["X-Process-Time"] = str(process_time)
                return response
                
            except HTTPException as e:
                if e.status_code >= 500:
                    sentry_service.capture_exception(
                        e,
                        tags={"endpoint": request.url.path, "method": request.method}
                    )
                
                return JSONResponse(
                    status_code=e.status_code,
                    content={
                        "error": e.detail,
                        "status_code": e.status_code,
                        "path": request.url.path,
                    }
                )
                
            except Exception as e:
                logger.error(
                    f"Unhandled exception in {request.method} {request.url.path}",
                    exc_info=True,
                    extra={
                        "path": request.url.path,
                        "method": request.method,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )
                
                sentry_service.set_context("request", {
                    "url": str(request.url),
                    "method": request.method,
                    "headers": dict(request.headers),
                    "client": request.client.host if request.client else None,
                })
                
                sentry_service.add_breadcrumb(
                    message=f"{request.method} {request.url.path}",
                    category="http",
                    level="error",
                    data={"status_code": 500, "reason": str(e)}
                )
                
                event_id = sentry_service.capture_exception(
                    e,
                    tags={"endpoint": request.url.path, "method": request.method}
                )
                
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal server error",
                        "message": str(e) if request.app.debug else "An unexpected error occurred",
                        "status_code": 500,
                        "path": request.url.path,
                        "event_id": event_id
                    }
                )
