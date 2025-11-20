"""
Metrics Middleware
Collect and export Prometheus metrics
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from prometheus_client import Counter, Histogram, Gauge
import time


# Define Prometheus metrics
request_count = Counter(
    "ikodio_requests_total",
    "Total request count",
    ["method", "endpoint", "status"]
)

request_duration = Histogram(
    "ikodio_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"]
)

active_requests = Gauge(
    "ikodio_active_requests",
    "Number of active requests"
)

bugs_found_total = Counter(
    "ikodio_bugs_found_total",
    "Total bugs found",
    ["severity", "type"]
)

fixes_deployed_total = Counter(
    "ikodio_fixes_deployed_total",
    "Total fixes deployed",
    ["confidence", "status"]
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Collect metrics for Prometheus monitoring
    """
    
    async def dispatch(self, request: Request, call_next):
        # Increment active requests
        active_requests.inc()
        
        # Start timer
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            
            request_count.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            request_duration.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            return response
            
        finally:
            # Decrement active requests
            active_requests.dec()
