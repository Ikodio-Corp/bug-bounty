"""
Main FastAPI application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from core.config import settings
from core.database import init_db, close_db
from core.redis import get_redis, get_async_redis, init_redis, close_redis

# Import all routes
from api.routes import (
    auth,
    users,
    bugs,
    scans,
    marketplace,
    fixes,
    nft,
    intelligence,
    forecasts,
    guild,
    university,
    social,
    courses,
    creators,
    quantum,
    satellite,
    agi,
    geopolitical,
    esg,
    dao,
    admin,
    webhooks,
    ai_agents,
    auto_fix,
    insurance,
    security_score,
    marketplace_extended,
    dao_governance,
    devops_autopilot,
    health,
    # ai_revolution,  # Missing isort dependency
    oauth,
    usage,
    analytics_advanced,
    two_factor,
    saml,
    advanced_scanners,
    payments,
    vcs_integration,
    cicd_integration,
    notifications,
    ml_pipeline,
    bug_validation,
    duplicate_detection,
    issue_tracking,
    auto_reporting,
    # cloud_security,  # Missing google-cloud-securitycenter dependency
    rbac,
    api_docs,
    # audit,  # Missing check_permission function in security
    gdpr,
    websocket,
    profile,
    leaderboard,
    analytics,
    # admin_dashboard,  # Missing check_permissions function
    integrations,
    additional_features,
    ml_integration,
    ml_training
)
from api.routes import notifications_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting Ikodio Bug Bounty Platform...")
    
    # Initialize Sentry
    from integrations.sentry_client import sentry_service
    sentry_service.initialize()
    logger.info("Sentry initialized")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize Redis
    await init_redis()
    logger.info("Redis connected")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    await close_db()
    await close_redis()


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
# IKODIO BugBounty Platform

AI-Powered Bug Bounty Automation Platform with 90-Second Discovery

## Features

- **AI-Powered Scanning**: Automated vulnerability detection
- **Bug Management**: Complete bug lifecycle tracking
- **Marketplace**: Buy and sell security tools and services
- **University**: Educational content for security researchers
- **Guild System**: Collaborative bug bounty teams
- **Advanced Analytics**: Comprehensive dashboards and insights
- **Real-time Notifications**: WebSocket-based updates
- **Multi-scanner Integration**: Support for ZAP, Burp, Nuclei, and custom scanners

## Authentication

All endpoints require JWT bearer token authentication except for:
- `/api/auth/login`
- `/api/auth/register`
- `/health`
- `/api/docs`

To authenticate:
1. POST credentials to `/api/auth/login`
2. Receive access_token in response
3. Include token in Authorization header: `Bearer <token>`

## Rate Limiting

API requests are rate-limited to prevent abuse:
- Default: 60 requests per minute
- Burst: 100 requests
- Rate limit headers included in responses

## Pagination

List endpoints support pagination:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

## Error Responses

Standard error format:
```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "status_code": 400
}
```

## Support

- Documentation: https://docs.ikodio.com
- Email: support@ikodio.com
- GitHub: https://github.com/ikodio/bugbounty
""",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {"name": "Authentication", "description": "User authentication and authorization"},
        {"name": "Bugs", "description": "Bug report management"},
        {"name": "Scans", "description": "Security scanning operations"},
        {"name": "Users", "description": "User management"},
        {"name": "Marketplace", "description": "Buy and sell security products"},
        {"name": "Analytics", "description": "Analytics and reporting"},
        {"name": "Advanced Analytics", "description": "Advanced analytics and exports"},
        {"name": "Guild", "description": "Team collaboration"},
        {"name": "University", "description": "Educational content"},
        {"name": "AI Agents", "description": "AI-powered automation"},
        {"name": "Admin", "description": "Administrative operations"},
        {"name": "Webhooks", "description": "Webhook integrations"},
        {"name": "Health", "description": "System health checks"},
    ],
    lifespan=lifespan
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting middleware
# from middleware.rate_limit import RateLimitMiddleware
# app.add_middleware(RateLimitMiddleware)

# Security middleware
from middleware.security import SecurityMiddleware, RequestValidationMiddleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(RequestValidationMiddleware)

# Security headers middleware
from middleware.security_headers import security_headers_middleware
app.middleware("http")(security_headers_middleware)

# Audit middleware
from middleware.audit_middleware import audit_middleware
app.middleware("http")(audit_middleware)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.3f}s with status {response.status_code}"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "features_enabled": {
            "ai_agents": settings.ENABLE_AI_AGENTS,
            "marketplace": settings.ENABLE_MARKETPLACE,
            "guild": settings.ENABLE_GUILD,
            "university": settings.ENABLE_UNIVERSITY,
            "quantum": settings.ENABLE_QUANTUM,
            "satellite": settings.ENABLE_SATELLITE,
            "geopolitical": settings.ENABLE_GEOPOLITICAL,
            "dao": settings.ENABLE_DAO,
        }
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ikodio Bug Bounty Platform API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


# Include all route modules
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(bugs.router, prefix="/api/bugs", tags=["Bugs"])
app.include_router(scans.router, prefix="/api/scans", tags=["Scans"])
app.include_router(usage.router, tags=["Usage"])  # Usage tracking
app.include_router(marketplace.router, prefix="/api/marketplace", tags=["Marketplace"])
app.include_router(fixes.router, prefix="/api/fixes", tags=["Fixes"])
app.include_router(nft.router, prefix="/api/nft", tags=["NFT"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["Intelligence"])
app.include_router(forecasts.router, prefix="/api/forecasts", tags=["Forecasts"])
app.include_router(guild.router, prefix="/api/guild", tags=["Guild"])
app.include_router(university.router, prefix="/api/university", tags=["University"])
app.include_router(social.router, prefix="/api/social", tags=["Social"])
app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
app.include_router(creators.router, prefix="/api/creators", tags=["Creators"])
app.include_router(quantum.router, prefix="/api/quantum", tags=["Quantum"])
app.include_router(satellite.router, prefix="/api/satellite", tags=["Satellite"])
app.include_router(agi.router, prefix="/api/agi", tags=["AGI"])
app.include_router(geopolitical.router, prefix="/api/geopolitical", tags=["Geopolitical"])
app.include_router(esg.router, prefix="/api/esg", tags=["ESG"])
app.include_router(dao.router, prefix="/api/dao", tags=["DAO"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(ai_agents.router, prefix="/api/ai", tags=["AI Agents"])

#  Revolutionary Features
app.include_router(auto_fix.router, prefix="/api/revolutionary", tags=["Revolutionary 90s Bug Fix"])
app.include_router(insurance.router, tags=["Insurance"])
app.include_router(security_score.router, tags=["Security Score"])
app.include_router(marketplace_extended.router, tags=["Marketplace Extended"])
app.include_router(dao_governance.router, tags=["DAO Governance"])
app.include_router(devops_autopilot.router, tags=["DevOps Autopilot"])

#  MARKET-DISRUPTING AI Services - Replace Entire Job Roles
# app.include_router(ai_revolution.router, tags=["AI Revolution - Job Replacement"])  # Missing isort dependency

#  Authentication & Security
app.include_router(oauth.router, tags=["OAuth2/SSO"])
app.include_router(two_factor.router, tags=["Two-Factor Authentication"])
app.include_router(saml.router, tags=["SAML 2.0 Enterprise SSO"])

#  Advanced Security Scanners
app.include_router(advanced_scanners.router, tags=["Advanced Scanners"])

#  Payment & Subscriptions
app.include_router(payments.router, prefix="/api/payments", tags=["Payments & Subscriptions"])

#  VCS Integration
app.include_router(vcs_integration.router, tags=["VCS Integration"])

#  CI/CD Integration
app.include_router(cicd_integration.router, tags=["CI/CD Integration"])

#  Notification Management
app.include_router(notifications.router, tags=["Notifications"])

#  ML Pipeline (90-second scanning)
app.include_router(ml_pipeline.router, tags=["ML Pipeline"])

# Bug Validation Workflow
app.include_router(bug_validation.router, tags=["Bug Validation"])

# Duplicate Detection
app.include_router(duplicate_detection.router, tags=["Duplicate Detection"])

# Issue Tracking Integration
app.include_router(issue_tracking.router, tags=["Issue Tracking"])

# Auto-Reporting to Platforms
app.include_router(auto_reporting.router, tags=["Auto Reporting"])

# Cloud Provider Security Integration
# app.include_router(cloud_security.router, tags=["Cloud Security"])  # Disabled - missing dependency

# Advanced RBAC
app.include_router(rbac.router, tags=["RBAC"])

# API Documentation
app.include_router(api_docs.router, tags=["API Documentation"])

# Audit Logging
# app.include_router(audit.router, prefix="/api/audit", tags=["Audit & Compliance"])  # Disabled - missing function

# GDPR Compliance
app.include_router(gdpr.router, prefix="/api/gdpr", tags=["GDPR & Privacy"])

# WebSocket routes
app.include_router(websocket.router, prefix="/api", tags=["WebSocket"])

# Profile Management
app.include_router(profile.router, prefix="/api", tags=["Profile"])

# Leaderboard
app.include_router(leaderboard.router, prefix="/api", tags=["Leaderboard"])

# Analytics
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])

# Advanced Analytics
app.include_router(analytics_advanced.router, prefix="/api", tags=["Advanced Analytics"])

# Admin Dashboard
# app.include_router(admin_dashboard.router, prefix="/api", tags=["Admin Dashboard"])  # Disabled - missing function

# Integrations
app.include_router(integrations.router, prefix="/api", tags=["Integrations"])

# Notifications API
app.include_router(notifications_api.router, prefix="/api", tags=["Notifications API"])

# Additional Features (Certificates, Webhooks, Reports, Tools, Tutorials)
app.include_router(additional_features.router, prefix="/api", tags=["Additional Features"])

# ML Integration (Phase 4)
app.include_router(ml_integration.router, prefix="/api", tags=["ML Integration"])

# ML Training & Auto-Learning (Phase 5)
app.include_router(ml_training.router, prefix="/api/ml/training", tags=["ML Training"])

# Health Check
app.include_router(health.router, tags=["Health"])

# Sentry Test Endpoints (development only)
if settings.DEBUG:
    from integrations.sentry_client import router as sentry_router
    app.include_router(sentry_router, prefix="/api/sentry", tags=["Sentry Testing"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )
