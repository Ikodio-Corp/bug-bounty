from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from core.database import get_db
from core.security import get_current_user, check_permission
from models.user import User
from services.audit_service import AuditService
from pydantic import BaseModel

router = APIRouter()

class AuditEventResponse(BaseModel):
    id: str
    timestamp: str
    user_id: Optional[int]
    event_type: str
    resource_type: str
    resource_id: Optional[str]
    action: str
    details: dict
    ip_address: Optional[str]
    status: str

class AuditStatisticsResponse(BaseModel):
    total_events: int
    by_type: dict
    by_status: dict
    unique_users: int
    unique_ips: int
    failed_logins: int
    security_alerts: int
    api_calls: int

@router.get("/audit/user/{user_id}", response_model=List[AuditEventResponse])
async def get_user_audit_logs(
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_types: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id and not check_permission(current_user, "audit", "read"):
        raise HTTPException(status_code=403, detail="Not authorized to view audit logs")
    
    audit_service = AuditService(db)
    
    event_type_list = event_types.split(",") if event_types else None
    
    events = await audit_service.get_user_activity(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        event_types=event_type_list,
        limit=limit
    )
    
    return events

@router.get("/audit/security", response_model=List[AuditEventResponse])
async def get_security_events(
    severity: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_permission(current_user, "audit", "read"):
        raise HTTPException(status_code=403, detail="Not authorized to view security events")
    
    audit_service = AuditService(db)
    events = await audit_service.get_security_events(severity=severity, limit=limit)
    
    return events

@router.get("/audit/failed-logins", response_model=List[AuditEventResponse])
async def get_failed_login_attempts(
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    hours: int = 24,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_permission(current_user, "audit", "read"):
        raise HTTPException(status_code=403, detail="Not authorized to view failed login attempts")
    
    audit_service = AuditService(db)
    since = datetime.utcnow() - timedelta(hours=hours)
    
    events = await audit_service.get_failed_login_attempts(
        username=username,
        ip_address=ip_address,
        since=since
    )
    
    return events

@router.get("/audit/statistics", response_model=AuditStatisticsResponse)
async def get_audit_statistics(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_permission(current_user, "audit", "read"):
        raise HTTPException(status_code=403, detail="Not authorized to view statistics")
    
    audit_service = AuditService(db)
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    stats = await audit_service.get_statistics(start_date, end_date)
    
    return stats

@router.get("/audit/export")
async def export_audit_logs(
    start_date: datetime,
    end_date: datetime,
    format: str = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_permission(current_user, "audit", "export"):
        raise HTTPException(status_code=403, detail="Not authorized to export audit logs")
    
    audit_service = AuditService(db)
    
    data = await audit_service.export_logs(start_date, end_date, format)
    
    from fastapi.responses import Response
    
    if format == "json":
        media_type = "application/json"
        filename = f"audit_logs_{start_date.date()}_{end_date.date()}.json"
    elif format == "csv":
        media_type = "text/csv"
        filename = f"audit_logs_{start_date.date()}_{end_date.date()}.csv"
    else:
        raise HTTPException(status_code=400, detail="Invalid format")
    
    await audit_service.log_data_access(
        user_id=current_user.id,
        resource_type="audit_logs",
        resource_id="export",
        action="export",
        ip_address=None
    )
    
    return Response(
        content=data,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
