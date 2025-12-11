"""
Security scanning routes - 90-second discovery workflow
"""

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.database import get_async_db, get_db
from core.security import Security
from models.user import User
from middleware.subscription_check import check_scan_limit, SubscriptionLimitError
from services.usage_tracking_service import UsageTrackingService

router = APIRouter()
security = Security()


@router.post("/start")
async def start_scan(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user),
    sync_db: Session = Depends(get_db)
):
    """
    Start 90-second security scan
    
    Checks subscription limits before allowing scan.
    Raises HTTP 402 if limit exceeded with upgrade prompt.
    """
    try:
        # Check if user has remaining scans
        check_scan_limit(current_user, sync_db)
        
        # Increment scan counter
        usage_service = UsageTrackingService(sync_db)
        usage_service.increment_scan_count(current_user)
        
        # TODO: Implement actual scan initiation with AI agents
        # For now, return placeholder
        
        return {
            "message": "Scan started successfully",
            "scan_id": 1,
            "tier": current_user.subscription_tier.value,
            "scans_remaining": usage_service.check_scan_limit(current_user)['remaining']
        }
        
    except SubscriptionLimitError as e:
        # This will automatically return HTTP 402 with upgrade info
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{scan_id}")
async def get_scan_status(
    scan_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Get scan status"""
    # TODO: Implement scan status retrieval
    return {"message": f"Scan {scan_id} status"}


@router.get("/{scan_id}/results")
async def get_scan_results(
    scan_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Get scan results"""
    # TODO: Implement scan results retrieval
    return {"message": f"Scan {scan_id} results"}


@router.get("/")
async def list_scans(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """List all scans"""
    # TODO: Implement scan listing
    return {"message": "List scans"}
