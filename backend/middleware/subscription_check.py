"""
Subscription Check Middleware
Enforce subscription limits and tier-based access control
"""

from fastapi import Request, HTTPException, status
from typing import Callable
from models.user import User, SubscriptionTier
from services.usage_tracking_service import UsageTrackingService


class SubscriptionLimitError(HTTPException):
    """Custom exception for subscription limit errors"""
    
    def __init__(self, message: str, upgrade_tier: str, current_usage: dict):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "subscription_limit_reached",
                "message": message,
                "upgrade_tier": upgrade_tier,
                "upgrade_url": f"/pricing?highlight={upgrade_tier}",
                "current_usage": current_usage
            },
            headers={"WWW-Authenticate": "Bearer"}
        )


def check_scan_limit(user: User, db) -> dict:
    """
    Check if user can perform scan
    Raises SubscriptionLimitError if limit reached
    """
    usage_service = UsageTrackingService(db)
    check_result = usage_service.check_scan_limit(user)
    
    if not check_result["allowed"]:
        raise SubscriptionLimitError(
            message=check_result["message"],
            upgrade_tier=check_result["upgrade_tier"],
            current_usage={
                "current": check_result["current"],
                "limit": check_result["limit"],
                "type": "scans"
            }
        )
    
    return check_result


def check_autofix_limit(user: User, db) -> dict:
    """
    Check if user can use auto-fix
    Raises SubscriptionLimitError if limit reached
    """
    usage_service = UsageTrackingService(db)
    check_result = usage_service.check_autofix_limit(user)
    
    if not check_result["allowed"]:
        raise SubscriptionLimitError(
            message=check_result["message"],
            upgrade_tier=check_result["upgrade_tier"],
            current_usage={
                "current": check_result["current"],
                "limit": check_result["limit"],
                "type": "autofixes"
            }
        )
    
    return check_result


def check_api_limit(user: User, db) -> dict:
    """
    Check if user can make API request
    Raises SubscriptionLimitError if limit reached
    """
    usage_service = UsageTrackingService(db)
    check_result = usage_service.check_api_limit(user)
    
    if not check_result["allowed"]:
        raise SubscriptionLimitError(
            message=check_result["message"],
            upgrade_tier=check_result["upgrade_tier"],
            current_usage={
                "current": check_result["current"],
                "limit": check_result["limit"],
                "type": "api_requests"
            }
        )
    
    return check_result


def check_marketplace_access(user: User) -> None:
    """
    Check if user can access marketplace selling features
    Free users can only view, not sell
    """
    if user.subscription_tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "marketplace_access_denied",
                "message": "Marketplace selling is not available on Free plan",
                "upgrade_tier": "professional",
                "upgrade_url": "/pricing?highlight=professional"
            }
        )


def check_team_member_limit(user: User, current_team_size: int) -> None:
    """
    Check if user can add more team members
    """
    team_limits = {
        SubscriptionTier.FREE: 1,
        SubscriptionTier.PROFESSIONAL: 3,
        SubscriptionTier.BUSINESS: 10,
        SubscriptionTier.ENTERPRISE: None,
        SubscriptionTier.GOVERNMENT: None,
    }
    
    limit = team_limits.get(user.subscription_tier, 1)
    
    if limit is not None and current_team_size >= limit:
        upgrade_tier = "professional" if user.subscription_tier == SubscriptionTier.FREE else "business"
        raise SubscriptionLimitError(
            message=f"Team member limit reached ({current_team_size}/{limit})",
            upgrade_tier=upgrade_tier,
            current_usage={
                "current": current_team_size,
                "limit": limit,
                "type": "team_members"
            }
        )


def check_feature_access(user: User, feature: str) -> None:
    """
    Check if user has access to specific feature
    """
    # Define feature access matrix
    feature_access = {
        "ai_scanner": [SubscriptionTier.PROFESSIONAL, SubscriptionTier.BUSINESS, 
                      SubscriptionTier.ENTERPRISE, SubscriptionTier.GOVERNMENT],
        "auto_fix": [SubscriptionTier.PROFESSIONAL, SubscriptionTier.BUSINESS, 
                    SubscriptionTier.ENTERPRISE, SubscriptionTier.GOVERNMENT],
        "api_access": [SubscriptionTier.PROFESSIONAL, SubscriptionTier.BUSINESS, 
                      SubscriptionTier.ENTERPRISE, SubscriptionTier.GOVERNMENT],
        "sso": [SubscriptionTier.BUSINESS, SubscriptionTier.ENTERPRISE, 
               SubscriptionTier.GOVERNMENT],
        "white_label": [SubscriptionTier.ENTERPRISE, SubscriptionTier.GOVERNMENT],
        "on_premise": [SubscriptionTier.ENTERPRISE, SubscriptionTier.GOVERNMENT],
        "air_gapped": [SubscriptionTier.GOVERNMENT],
    }
    
    allowed_tiers = feature_access.get(feature, [])
    
    if user.subscription_tier not in allowed_tiers:
        # Determine upgrade tier
        if feature in ["ai_scanner", "auto_fix", "api_access"]:
            upgrade_tier = "professional"
        elif feature in ["sso"]:
            upgrade_tier = "business"
        else:
            upgrade_tier = "enterprise"
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "feature_access_denied",
                "message": f"Feature '{feature}' is not available on {user.subscription_tier.value} plan",
                "upgrade_tier": upgrade_tier,
                "upgrade_url": f"/pricing?highlight={upgrade_tier}"
            }
        )


def get_commission_rate(user: User) -> float:
    """
    Get marketplace commission rate based on subscription tier
    """
    commission_rates = {
        SubscriptionTier.FREE: 1.0,  # Cannot sell
        SubscriptionTier.PROFESSIONAL: 0.15,  # 15%
        SubscriptionTier.BUSINESS: 0.10,  # 10%
        SubscriptionTier.ENTERPRISE: 0.05,  # 5%
        SubscriptionTier.GOVERNMENT: 0.05,  # 5%
    }
    
    return commission_rates.get(user.subscription_tier, 0.15)
