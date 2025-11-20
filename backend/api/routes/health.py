"""
Health check routes for monitoring system status
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from redis.asyncio import Redis
import psutil
import time
from typing import Dict, Any

from core.database import get_db
from core.redis import get_redis

router = APIRouter(tags=["health"])

start_time = time.time()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.time() - start_time
    }


@router.get("/health/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Dict[str, Any]:
    """Detailed health check with all system components"""
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.time() - start_time,
        "components": {}
    }
    
    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        await db.commit()
        health_status["components"]["database"] = {
            "status": "healthy",
            "type": "postgresql"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check Redis
    try:
        await redis.ping()
        health_status["components"]["redis"] = {
            "status": "healthy",
            "type": "redis"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # System metrics
    try:
        health_status["components"]["system"] = {
            "status": "healthy",
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    except Exception as e:
        health_status["components"]["system"] = {
            "status": "error",
            "error": str(e)
        }
    
    return health_status


@router.get("/health/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Dict[str, Any]:
    """Kubernetes readiness probe endpoint"""
    
    try:
        # Check database connection
        await db.execute(text("SELECT 1"))
        
        # Check Redis connection
        await redis.ping()
        
        return {
            "status": "ready",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": time.time()
        }


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """Kubernetes liveness probe endpoint"""
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime": time.time() - start_time
    }
