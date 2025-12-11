"""
Usage API Routes - Track and display user usage across all subscription limits
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from core.database import get_db
from core.security import get_current_user
from models.user import User
from services.usage_tracking_service import UsageTrackingService

router = APIRouter(prefix="/api/usage", tags=["usage"])


@router.get("/summary")
async def get_usage_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive usage summary for current user
    
    Returns:
        - Scan usage (current, limit, percentage)
        - Auto-fix usage (current, limit, percentage)
        - API usage (current, limit, percentage)
        - Storage usage (current, limit, percentage)
        - Subscription tier info
        - Upgrade recommendations if near limits
    """
    usage_service = UsageTrackingService(db)
    summary = usage_service.get_usage_summary(current_user)
    
    # Add tier info
    summary['subscription'] = {
        'tier': current_user.subscription_tier.value,
        'status': current_user.subscription_status,
        'expires_at': current_user.subscription_end_date.isoformat() if current_user.subscription_end_date else None
    }
    
    # Check if near any limits (>80%)
    warnings = []
    if summary['scans']['percentage'] >= 80:
        warnings.append({
            'type': 'scans',
            'message': f"You've used {summary['scans']['percentage']:.0f}% of your scan limit",
            'action': 'Consider upgrading to increase your limit'
        })
    if summary['autofixes']['percentage'] >= 80:
        warnings.append({
            'type': 'autofixes',
            'message': f"You've used {summary['autofixes']['percentage']:.0f}% of your auto-fix limit",
            'action': 'Upgrade to get more auto-fixes'
        })
    if summary['api']['percentage'] >= 80:
        warnings.append({
            'type': 'api',
            'message': f"You've used {summary['api']['percentage']:.0f}% of your API limit",
            'action': 'Upgrade for higher API limits'
        })
    
    summary['warnings'] = warnings
    
    return summary


@router.get("/scans")
async def get_scan_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed scan usage information
    
    Returns:
        - Current month usage
        - Limit based on tier
        - Remaining scans
        - Usage history (last 6 months)
        - Allowed status
    """
    usage_service = UsageTrackingService(db)
    
    # Check current limit
    limit_check = usage_service.check_scan_limit(current_user)
    
    # Get historical data (last 6 months)
    from models.usage import ScanUsage
    from datetime import datetime, timedelta
    from sqlalchemy import desc
    
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    history = db.query(ScanUsage).filter(
        ScanUsage.user_id == current_user.id,
        ScanUsage.month >= six_months_ago.strftime('%Y-%m')
    ).order_by(desc(ScanUsage.month)).all()
    
    return {
        'current': {
            'count': limit_check['current'],
            'limit': limit_check['limit'],
            'remaining': limit_check['remaining'],
            'allowed': limit_check['allowed'],
            'percentage': (limit_check['current'] / limit_check['limit'] * 100) if limit_check['limit'] else 0
        },
        'history': [
            {
                'month': record.month,
                'count': record.scan_count,
                'limit': record.limit
            }
            for record in history
        ],
        'tier': current_user.subscription_tier.value,
        'upgrade_recommendation': None if limit_check['allowed'] else {
            'tier': limit_check.get('upgrade_tier'),
            'message': limit_check.get('message')
        }
    }


@router.get("/autofixes")
async def get_autofix_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed auto-fix usage information
    """
    usage_service = UsageTrackingService(db)
    
    # Check current limit
    limit_check = usage_service.check_autofix_limit(current_user)
    
    # Get historical data
    from models.usage import AutoFixUsage
    from datetime import datetime, timedelta
    from sqlalchemy import desc
    
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    history = db.query(AutoFixUsage).filter(
        AutoFixUsage.user_id == current_user.id,
        AutoFixUsage.month >= six_months_ago.strftime('%Y-%m')
    ).order_by(desc(AutoFixUsage.month)).all()
    
    return {
        'current': {
            'count': limit_check['current'],
            'limit': limit_check['limit'],
            'remaining': limit_check['remaining'],
            'allowed': limit_check['allowed'],
            'percentage': (limit_check['current'] / limit_check['limit'] * 100) if limit_check['limit'] else 0
        },
        'history': [
            {
                'month': record.month,
                'count': record.fix_count,
                'limit': record.limit
            }
            for record in history
        ],
        'tier': current_user.subscription_tier.value,
        'upgrade_recommendation': None if limit_check['allowed'] else {
            'tier': limit_check.get('upgrade_tier'),
            'message': limit_check.get('message')
        }
    }


@router.get("/api-requests")
async def get_api_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed API request usage information
    """
    usage_service = UsageTrackingService(db)
    
    # Check current limit
    limit_check = usage_service.check_api_limit(current_user)
    
    # Get historical data
    from models.usage import APIUsage
    from datetime import datetime, timedelta
    from sqlalchemy import desc
    
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    history = db.query(APIUsage).filter(
        APIUsage.user_id == current_user.id,
        APIUsage.month >= six_months_ago.strftime('%Y-%m')
    ).order_by(desc(APIUsage.month)).all()
    
    return {
        'current': {
            'count': limit_check['current'],
            'limit': limit_check['limit'],
            'remaining': limit_check['remaining'],
            'allowed': limit_check['allowed'],
            'percentage': (limit_check['current'] / limit_check['limit'] * 100) if limit_check['limit'] else 0
        },
        'history': [
            {
                'month': record.month,
                'count': record.request_count,
                'limit': record.limit
            }
            for record in history
        ],
        'tier': current_user.subscription_tier.value,
        'upgrade_recommendation': None if limit_check['allowed'] else {
            'tier': limit_check.get('upgrade_tier'),
            'message': limit_check.get('message')
        }
    }


@router.get("/storage")
async def get_storage_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed storage usage information
    """
    from models.usage import StorageUsage
    
    storage = db.query(StorageUsage).filter(
        StorageUsage.user_id == current_user.id
    ).first()
    
    if not storage:
        # Initialize storage tracking
        usage_service = UsageTrackingService(db)
        limits = usage_service.STORAGE_LIMITS_MB
        retention = usage_service.RETENTION_DAYS
        
        tier_limit_mb = limits.get(current_user.subscription_tier, limits['FREE'])
        tier_retention = retention.get(current_user.subscription_tier, retention['FREE'])
        
        storage = StorageUsage(
            user_id=current_user.id,
            bytes_used=0,
            bytes_limit=tier_limit_mb * 1024 * 1024,  # Convert MB to bytes
            retention_days=tier_retention
        )
        db.add(storage)
        db.commit()
        db.refresh(storage)
    
    bytes_used = storage.bytes_used
    bytes_limit = storage.bytes_limit
    percentage = (bytes_used / bytes_limit * 100) if bytes_limit > 0 else 0
    
    return {
        'current': {
            'bytes': bytes_used,
            'megabytes': round(bytes_used / (1024 * 1024), 2),
            'gigabytes': round(bytes_used / (1024 * 1024 * 1024), 2),
            'limit_bytes': bytes_limit,
            'limit_megabytes': round(bytes_limit / (1024 * 1024), 2),
            'limit_gigabytes': round(bytes_limit / (1024 * 1024 * 1024), 2),
            'percentage': round(percentage, 2),
            'remaining_bytes': bytes_limit - bytes_used
        },
        'retention_days': storage.retention_days,
        'tier': current_user.subscription_tier.value,
        'upgrade_recommendation': {
            'tier': 'PROFESSIONAL',
            'message': 'Upgrade untuk storage 10 GB dan retensi 1 tahun'
        } if percentage >= 80 and current_user.subscription_tier.value == 'FREE' else None
    }


@router.post("/reset-demo")
async def reset_demo_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Reset usage counters for demo/testing purposes
    Only available in development mode
    """
    import os
    
    if os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reset endpoint only available in development"
        )
    
    from models.usage import ScanUsage, AutoFixUsage, APIUsage, StorageUsage
    from datetime import datetime
    
    current_month = datetime.utcnow().strftime('%Y-%m')
    
    # Reset scan usage
    db.query(ScanUsage).filter(
        ScanUsage.user_id == current_user.id,
        ScanUsage.month == current_month
    ).delete()
    
    # Reset autofix usage
    db.query(AutoFixUsage).filter(
        AutoFixUsage.user_id == current_user.id,
        AutoFixUsage.month == current_month
    ).delete()
    
    # Reset API usage
    db.query(APIUsage).filter(
        APIUsage.user_id == current_user.id,
        APIUsage.month == current_month
    ).delete()
    
    # Reset storage usage
    db.query(StorageUsage).filter(
        StorageUsage.user_id == current_user.id
    ).update({'bytes_used': 0})
    
    db.commit()
    
    return {'message': 'Usage counters reset successfully'}
