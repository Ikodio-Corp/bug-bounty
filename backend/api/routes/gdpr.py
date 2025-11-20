from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from core.database import get_db
from core.security import get_current_user
from models.user import User
from services.audit_service import AuditService
import json

router = APIRouter()

@router.get("/users/me/data-export")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    audit_service = AuditService(db)
    
    await audit_service.log_data_access(
        user_id=current_user.id,
        resource_type="user_data",
        resource_id=str(current_user.id),
        action="export"
    )
    
    user_data = {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "subscription_tier": current_user.subscription_tier,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified
        },
        "scans": [],
        "bugs": [],
        "payments": [],
        "audit_logs": await audit_service.get_user_activity(current_user.id, limit=1000),
        "export_date": datetime.utcnow().isoformat(),
        "export_format": "JSON"
    }
    
    return user_data

@router.delete("/users/me")
async def request_account_deletion(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    audit_service = AuditService(db)
    
    grace_period_end = datetime.utcnow() + timedelta(days=30)
    
    current_user.deletion_requested_at = datetime.utcnow()
    current_user.deletion_scheduled_at = grace_period_end
    db.commit()
    
    await audit_service.log_data_modification(
        user_id=current_user.id,
        resource_type="user",
        resource_id=str(current_user.id),
        action="request_deletion",
        changes={"deletion_requested": True},
        ip_address=request.client.host if request and request.client else None
    )
    
    return {
        "message": "Account deletion scheduled",
        "grace_period_ends": grace_period_end.isoformat(),
        "deletion_id": f"del_{current_user.id}_{int(datetime.utcnow().timestamp())}"
    }

@router.post("/users/me/cancel-deletion")
async def cancel_account_deletion(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.deletion_requested_at:
        raise HTTPException(status_code=400, detail="No deletion request found")
    
    current_user.deletion_requested_at = None
    current_user.deletion_scheduled_at = None
    db.commit()
    
    audit_service = AuditService(db)
    await audit_service.log_data_modification(
        user_id=current_user.id,
        resource_type="user",
        resource_id=str(current_user.id),
        action="cancel_deletion",
        changes={"deletion_cancelled": True}
    )
    
    return {"message": "Account deletion cancelled"}

@router.get("/users/me/consent")
async def get_consent_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    consent = {
        "marketing_emails": current_user.consent_marketing,
        "analytics": current_user.consent_analytics,
        "third_party_sharing": current_user.consent_third_party,
        "profiling": current_user.consent_profiling
    }
    
    return consent

@router.put("/users/me/consent")
async def update_consent_settings(
    consent_data: Dict[str, bool],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    changes = {}
    
    if "marketing_emails" in consent_data:
        current_user.consent_marketing = consent_data["marketing_emails"]
        changes["consent_marketing"] = consent_data["marketing_emails"]
    
    if "analytics" in consent_data:
        current_user.consent_analytics = consent_data["analytics"]
        changes["consent_analytics"] = consent_data["analytics"]
    
    if "third_party_sharing" in consent_data:
        current_user.consent_third_party = consent_data["third_party_sharing"]
        changes["consent_third_party"] = consent_data["third_party_sharing"]
    
    if "profiling" in consent_data:
        current_user.consent_profiling = consent_data["profiling"]
        changes["consent_profiling"] = consent_data["profiling"]
    
    current_user.consent_updated_at = datetime.utcnow()
    db.commit()
    
    audit_service = AuditService(db)
    await audit_service.log_data_modification(
        user_id=current_user.id,
        resource_type="consent",
        resource_id=str(current_user.id),
        action="update",
        changes=changes
    )
    
    return {"message": "Consent preferences updated", "consent": consent_data}

@router.get("/users/me/access-logs")
async def get_access_logs(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    audit_service = AuditService(db)
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    logs = await audit_service.get_user_activity(
        user_id=current_user.id,
        start_date=start_date,
        event_types=["authentication", "data_access", "api_call"]
    )
    
    simplified_logs = [
        {
            "timestamp": log["timestamp"],
            "action": log["action"],
            "ip_address": log.get("ip_address"),
            "status": log["status"]
        }
        for log in logs
    ]
    
    return simplified_logs

@router.post("/users/me/object-processing")
async def object_to_processing(
    processing_type: str,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    valid_types = ["marketing", "profiling", "automated_decision"]
    
    if processing_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid processing type. Must be one of: {', '.join(valid_types)}"
        )
    
    if processing_type == "marketing":
        current_user.consent_marketing = False
    elif processing_type == "profiling":
        current_user.consent_profiling = False
    elif processing_type == "automated_decision":
        current_user.consent_automated_decision = False
    
    db.commit()
    
    audit_service = AuditService(db)
    await audit_service.log_data_modification(
        user_id=current_user.id,
        resource_type="processing_objection",
        resource_id=str(current_user.id),
        action="object",
        changes={
            "processing_type": processing_type,
            "reason": reason
        }
    )
    
    return {
        "message": f"Objection to {processing_type} processing recorded",
        "processing_type": processing_type
    }

@router.post("/users/me/rectify")
async def request_data_rectification(
    field: str,
    current_value: str,
    requested_value: str,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    audit_service = AuditService(db)
    
    await audit_service.log_data_modification(
        user_id=current_user.id,
        resource_type="rectification_request",
        resource_id=str(current_user.id),
        action="request",
        changes={
            "field": field,
            "current_value": current_value,
            "requested_value": requested_value,
            "reason": reason
        }
    )
    
    return {
        "message": "Data rectification request submitted",
        "request_id": f"rect_{current_user.id}_{int(datetime.utcnow().timestamp())}",
        "status": "pending_review"
    }

@router.get("/privacy/policy")
async def get_privacy_policy():
    return {
        "version": "1.0.0",
        "effective_date": "2024-01-01",
        "last_updated": "2024-01-01",
        "dpo_contact": "dpo@ikodio.com",
        "policy_url": "https://ikodio.com/privacy",
        "data_controller": {
            "name": "IKODIO Ltd",
            "address": "London, United Kingdom",
            "email": "privacy@ikodio.com"
        },
        "data_protection_officer": {
            "email": "dpo@ikodio.com",
            "response_time": "48 hours"
        },
        "user_rights": [
            "Right to access",
            "Right to rectification",
            "Right to erasure",
            "Right to data portability",
            "Right to object",
            "Right to restrict processing",
            "Right to withdraw consent"
        ],
        "data_retention": {
            "active_users": "indefinite",
            "inactive_users": "2 years",
            "deleted_users": "30 days grace period",
            "audit_logs": "90 days",
            "payment_records": "7 years"
        }
    }
