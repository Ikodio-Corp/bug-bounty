"""
Admin API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from core.database import get_db
from middleware.auth import get_current_user, check_permissions
from models.user import User
from services.admin_service import AdminService

router = APIRouter()


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserRoleUpdate(BaseModel):
    role: str


class BugValidation(BaseModel):
    bounty_amount: float


class BugRejection(BaseModel):
    reason: str


@router.get("/admin/overview")
async def get_platform_overview(
    current_user: User = Depends(check_permissions("admin")),
    db: Session = Depends(get_db)
):
    """Get platform overview statistics"""
    admin_service = AdminService(db)
    overview = admin_service.get_platform_overview()
    
    return overview


@router.get("/admin/users")
async def get_users_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(check_permissions("admin")),
    db: Session = Depends(get_db)
):
    """Get paginated users list with filters"""
    admin_service = AdminService(db)
    users = admin_service.get_users_list(
        page=page,
        per_page=per_page,
        search=search,
        role=role,
        status=status
    )
    
    return users


@router.put("/admin/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    current_user: User = Depends(check_permissions("admin")),
    db: Session = Depends(get_db)
):
    """Update user active status"""
    admin_service = AdminService(db)
    result = admin_service.update_user_status(user_id, data.is_active)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


@router.put("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    data: UserRoleUpdate,
    current_user: User = Depends(check_permissions("admin")),
    db: Session = Depends(get_db)
):
    """Update user role"""
    admin_service = AdminService(db)
    result = admin_service.update_user_role(user_id, data.role)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(check_permissions("admin")),
    db: Session = Depends(get_db)
):
    """Delete user account"""
    admin_service = AdminService(db)
    result = admin_service.delete_user(user_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/admin/bugs")
async def get_bugs_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(check_permissions("admin")),
    db: Session = Depends(get_db)
):
    """Get paginated bugs list with filters"""
    admin_service = AdminService(db)
    bugs = admin_service.get_bugs_list(
        page=page,
        per_page=per_page,
        status=status,
        severity=severity,
        search=search
    )
    
    return bugs


@router.post("/admin/bugs/{bug_id}/validate")
async def validate_bug(
    bug_id: int,
    data: BugValidation,
    current_user: User = Depends(check_permissions("admin")),
    db: Session = Depends(get_db)
):
    """Validate bug and set bounty"""
    admin_service = AdminService(db)
    result = admin_service.validate_bug(bug_id, data.bounty_amount)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


@router.post("/admin/bugs/{bug_id}/reject")
async def reject_bug(
    bug_id: int,
    data: BugRejection,
    current_user: User = Depends(check_permissions("admin")),
    db: Session = Depends(get_db)
):
    """Reject bug with reason"""
    admin_service = AdminService(db)
    result = admin_service.reject_bug(bug_id, data.reason)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


@router.get("/admin/scans")
async def get_scans_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(check_permissions("admin")),
    db: Session = Depends(get_db)
):
    """Get paginated scans list with filters"""
    admin_service = AdminService(db)
    scans = admin_service.get_scans_list(
        page=page,
        per_page=per_page,
        status=status
    )
    
    return scans


@router.get("/admin/analytics")
async def get_analytics_data(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(check_permissions("admin")),
    db: Session = Depends(get_db)
):
    """Get analytics data for admin dashboard"""
    admin_service = AdminService(db)
    analytics = admin_service.get_analytics_data(days)
    
    return analytics
