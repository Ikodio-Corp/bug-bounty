"""
Auto-Fix API Routes
90-Second Bug Finding and Fixing Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl
from typing import Optional, List

from core.database import get_async_db
from core.security import Security
from models.user import User
from services.auto_fix_service import AutoFixService


router = APIRouter()
security = Security()


class AutoFixRequest(BaseModel):
    """Request model for auto-fix"""
    target_url: HttpUrl
    repository_url: Optional[HttpUrl] = None
    auto_deploy: bool = False
    run_async: bool = False  # Run in background


class AutoFixResponse(BaseModel):
    """Response model for auto-fix"""
    fix_id: str
    status: str
    target_url: str
    bugs_found: int
    fixes_generated: int
    tests_passed: int
    total_time_seconds: float
    deployment_status: Optional[dict] = None


@router.post("/auto-fix", response_model=AutoFixResponse)
async def run_auto_fix(
    request: AutoFixRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    🚀 90-Second Bug Finding + Auto-Fix
    
    Revolutionary pipeline:
    1. Scan & Detect (30s)
    2. Generate Fix (30s)
    3. Test Fix (20s)
    4. Deploy PR (10s)
    
    Example:
    ```
    POST /auto-fix
    {
        "target_url": "https://example.com",
        "repository_url": "https://github.com/user/repo",
        "auto_deploy": true
    }
    ```
    """
    service = AutoFixService(db)
    
    if request.run_async:
        # Run in background
        background_tasks.add_task(
            service.run_auto_fix,
            target_url=str(request.target_url),
            user_id=current_user.id,
            repository_url=str(request.repository_url) if request.repository_url else None,
            auto_deploy=request.auto_deploy
        )
        
        return {
            "fix_id": "pending",
            "status": "processing",
            "target_url": str(request.target_url),
            "message": "Fix running in background. Check status with GET /auto-fix/{fix_id}"
        }
    
    # Run synchronously
    result = await service.run_auto_fix(
        target_url=str(request.target_url),
        user_id=current_user.id,
        repository_url=str(request.repository_url) if request.repository_url else None,
        auto_deploy=request.auto_deploy
    )
    
    return AutoFixResponse(
        fix_id=result["fix_id"],
        status=result["status"],
        target_url=result["target_url"],
        bugs_found=len(result.get("bugs_found", [])),
        fixes_generated=len(result.get("fixes_generated", [])),
        tests_passed=result.get("tests_passed", 0),
        total_time_seconds=result.get("total_time_seconds", 0),
        deployment_status=result.get("deployment_status")
    )


@router.get("/auto-fix/{fix_id}")
async def get_fix_status(
    fix_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Get status of a fix session
    """
    service = AutoFixService(db)
    status = await service.get_fix_status(fix_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Fix session not found")
    
    return status


@router.get("/auto-fix")
async def list_fixes(
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    List all fix sessions for current user
    """
    service = AutoFixService(db)
    fixes = await service.list_fixes(current_user.id, limit)
    
    return {
        "fixes": fixes,
        "total": len(fixes)
    }


@router.get("/auto-fix/stats")
async def get_auto_fix_stats(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Get auto-fix statistics
    """
    # TODO: Implement statistics
    return {
        "total_fixes": 0,
        "bugs_found": 0,
        "fixes_deployed": 0,
        "average_time_seconds": 0,
        "success_rate": 0.0
    }
