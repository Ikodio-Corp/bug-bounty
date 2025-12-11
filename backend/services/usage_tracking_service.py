"""
Usage Tracking Service
Track and enforce subscription limits
"""

from typing import Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.user import User, SubscriptionTier
from models.usage import ScanUsage, AutoFixUsage, APIUsage, StorageUsage


class UsageTrackingService:
    """Service for tracking and enforcing usage limits"""
    
    # Subscription tier limits (matching migration pricing)
    SCAN_LIMITS = {
        SubscriptionTier.FREE: 10,
        SubscriptionTier.PROFESSIONAL: 50,
        SubscriptionTier.BUSINESS: 200,
        SubscriptionTier.ENTERPRISE: None,  # Unlimited
        SubscriptionTier.GOVERNMENT: None,  # Unlimited
    }
    
    AUTOFIX_LIMITS = {
        SubscriptionTier.FREE: 0,
        SubscriptionTier.PROFESSIONAL: 20,
        SubscriptionTier.BUSINESS: None,  # Unlimited
        SubscriptionTier.ENTERPRISE: None,  # Unlimited
        SubscriptionTier.GOVERNMENT: None,  # Unlimited
    }
    
    API_LIMITS = {
        SubscriptionTier.FREE: 1000,
        SubscriptionTier.PROFESSIONAL: 5000,
        SubscriptionTier.BUSINESS: 25000,
        SubscriptionTier.ENTERPRISE: None,  # Unlimited
        SubscriptionTier.GOVERNMENT: None,  # Unlimited
    }
    
    STORAGE_LIMITS_GB = {
        SubscriptionTier.FREE: 1,
        SubscriptionTier.PROFESSIONAL: 10,
        SubscriptionTier.BUSINESS: 50,
        SubscriptionTier.ENTERPRISE: 500,
        SubscriptionTier.GOVERNMENT: 1000,
    }
    
    # Combined tier limits for easy access
    TIER_LIMITS = {
        'free': {
            'scans_per_month': 10,
            'autofixes_per_month': 0,
            'api_requests_per_month': 1000,
            'storage_gb': 1
        },
        'professional': {
            'scans_per_month': 50,
            'autofixes_per_month': 20,
            'api_requests_per_month': 5000,
            'storage_gb': 10
        },
        'business': {
            'scans_per_month': 200,
            'autofixes_per_month': None,  # Unlimited
            'api_requests_per_month': 25000,
            'storage_gb': 50
        },
        'enterprise': {
            'scans_per_month': None,  # Unlimited
            'autofixes_per_month': None,  # Unlimited
            'api_requests_per_month': None,  # Unlimited
            'storage_gb': 500
        },
        'government': {
            'scans_per_month': None,  # Unlimited
            'autofixes_per_month': None,  # Unlimited
            'api_requests_per_month': None,  # Unlimited
            'storage_gb': 1000
        }
    }
    
    RETENTION_DAYS = {
        SubscriptionTier.FREE: 30,
        SubscriptionTier.PROFESSIONAL: 365,
        SubscriptionTier.BUSINESS: 1095,  # 3 years
        SubscriptionTier.ENTERPRISE: 1825,  # 5 years
        SubscriptionTier.GOVERNMENT: None,  # Forever
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    @staticmethod
    def get_current_month() -> str:
        """Get current month in YYYY-MM format"""
        return datetime.utcnow().strftime("%Y-%m")
    
    def get_or_create_scan_usage(self, user: User) -> ScanUsage:
        """Get or create scan usage record for current month"""
        month = self.get_current_month()
        limit = self.SCAN_LIMITS.get(user.subscription_tier, 10)
        
        usage = self.db.query(ScanUsage).filter(
            and_(
                ScanUsage.user_id == user.id,
                ScanUsage.month == month
            )
        ).first()
        
        if not usage:
            usage = ScanUsage(
                user_id=user.id,
                month=month,
                scan_count=0,
                limit=limit if limit is not None else 999999
            )
            self.db.add(usage)
            self.db.commit()
            self.db.refresh(usage)
        
        return usage
    
    def check_scan_limit(self, user: User) -> Dict[str, any]:
        """Check if user can perform scan"""
        usage = self.get_or_create_scan_usage(user)
        limit = self.SCAN_LIMITS.get(user.subscription_tier)
        
        if limit is None:  # Unlimited
            return {
                "allowed": True,
                "current": usage.scan_count,
                "limit": "unlimited",
                "remaining": "unlimited"
            }
        
        if usage.scan_count >= limit:
            return {
                "allowed": False,
                "current": usage.scan_count,
                "limit": limit,
                "remaining": 0,
                "message": f"Scan limit reached ({usage.scan_count}/{limit})",
                "upgrade_tier": "professional" if user.subscription_tier == SubscriptionTier.FREE else "business"
            }
        
        return {
            "allowed": True,
            "current": usage.scan_count,
            "limit": limit,
            "remaining": limit - usage.scan_count
        }
    
    def increment_scan_count(self, user: User) -> ScanUsage:
        """Increment scan count for user"""
        usage = self.get_or_create_scan_usage(user)
        usage.scan_count += 1
        usage.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(usage)
        return usage
    
    def get_or_create_autofix_usage(self, user: User) -> AutoFixUsage:
        """Get or create auto-fix usage record for current month"""
        month = self.get_current_month()
        limit = self.AUTOFIX_LIMITS.get(user.subscription_tier, 0)
        
        usage = self.db.query(AutoFixUsage).filter(
            and_(
                AutoFixUsage.user_id == user.id,
                AutoFixUsage.month == month
            )
        ).first()
        
        if not usage:
            usage = AutoFixUsage(
                user_id=user.id,
                month=month,
                fix_count=0,
                limit=limit
            )
            self.db.add(usage)
            self.db.commit()
            self.db.refresh(usage)
        
        return usage
    
    def check_autofix_limit(self, user: User) -> Dict[str, any]:
        """Check if user can use auto-fix"""
        usage = self.get_or_create_autofix_usage(user)
        limit = self.AUTOFIX_LIMITS.get(user.subscription_tier)
        
        if limit is None:  # Unlimited
            return {
                "allowed": True,
                "current": usage.fix_count,
                "limit": "unlimited",
                "remaining": "unlimited"
            }
        
        if limit == 0:  # No access
            return {
                "allowed": False,
                "current": 0,
                "limit": 0,
                "remaining": 0,
                "message": "Auto-fix not available on Free plan",
                "upgrade_tier": "professional"
            }
        
        if usage.fix_count >= limit:
            return {
                "allowed": False,
                "current": usage.fix_count,
                "limit": limit,
                "remaining": 0,
                "message": f"Auto-fix limit reached ({usage.fix_count}/{limit})",
                "upgrade_tier": "business"
            }
        
        return {
            "allowed": True,
            "current": usage.fix_count,
            "limit": limit,
            "remaining": limit - usage.fix_count
        }
    
    def increment_autofix_count(self, user: User) -> AutoFixUsage:
        """Increment auto-fix count for user"""
        usage = self.get_or_create_autofix_usage(user)
        usage.fix_count += 1
        usage.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(usage)
        return usage
    
    def get_or_create_api_usage(self, user: User) -> APIUsage:
        """Get or create API usage record for current month"""
        month = self.get_current_month()
        limit = self.API_LIMITS.get(user.subscription_tier, 0)
        
        usage = self.db.query(APIUsage).filter(
            and_(
                APIUsage.user_id == user.id,
                APIUsage.month == month
            )
        ).first()
        
        if not usage:
            usage = APIUsage(
                user_id=user.id,
                month=month,
                request_count=0,
                limit=limit
            )
            self.db.add(usage)
            self.db.commit()
            self.db.refresh(usage)
        
        return usage
    
    def check_api_limit(self, user: User) -> Dict[str, any]:
        """Check if user can make API request"""
        usage = self.get_or_create_api_usage(user)
        limit = self.API_LIMITS.get(user.subscription_tier)
        
        if limit is None:  # Unlimited
            return {
                "allowed": True,
                "current": usage.request_count,
                "limit": "unlimited",
                "remaining": "unlimited"
            }
        
        if usage.request_count >= limit:
            return {
                "allowed": False,
                "current": usage.request_count,
                "limit": limit,
                "remaining": 0,
                "message": f"API limit reached ({usage.request_count}/{limit})",
                "upgrade_tier": "business" if user.subscription_tier == SubscriptionTier.PROFESSIONAL else "enterprise"
            }
        
        return {
            "allowed": True,
            "current": usage.request_count,
            "limit": limit,
            "remaining": limit - usage.request_count
        }
    
    def increment_api_count(self, user: User) -> APIUsage:
        """Increment API request count for user"""
        usage = self.get_or_create_api_usage(user)
        usage.request_count += 1
        usage.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(usage)
        return usage
    
    def get_or_create_storage_usage(self, user: User) -> StorageUsage:
        """Get or create storage usage record"""
        limit_gb = self.STORAGE_LIMITS_GB.get(user.subscription_tier, 1)
        bytes_limit = limit_gb * 1024 * 1024 * 1024 if limit_gb else 999999999999
        
        usage = self.db.query(StorageUsage).filter(
            StorageUsage.user_id == user.id
        ).first()
        
        if not usage:
            usage = StorageUsage(
                user_id=user.id,
                bytes_used=0,
                bytes_limit=bytes_limit,
                retention_days=30 if user.subscription_tier == SubscriptionTier.FREE else 365
            )
            self.db.add(usage)
            self.db.commit()
            self.db.refresh(usage)
        
        return usage
    
    def check_storage_limit(self, user: User, additional_bytes: int = 0) -> Dict[str, any]:
        """Check if user has storage available"""
        usage = self.get_or_create_storage_usage(user)
        limit_gb = self.STORAGE_LIMITS_GB.get(user.subscription_tier)
        
        if limit_gb is None:
            limit_gb = self.STORAGE_LIMITS_GB.get(user.subscription_tier, 1000)
        
        bytes_limit = limit_gb * 1024 * 1024 * 1024
        current_gb = usage.bytes_used / (1024 * 1024 * 1024)
        remaining_bytes = bytes_limit - usage.bytes_used
        
        if usage.bytes_used + additional_bytes > bytes_limit:
            return {
                "allowed": False,
                "current_gb": round(current_gb, 2),
                "limit_gb": limit_gb,
                "remaining_gb": round(remaining_bytes / (1024 * 1024 * 1024), 2),
                "message": f"Storage limit exceeded ({round(current_gb, 2)}GB/{limit_gb}GB)",
                "upgrade_tier": "professional" if user.subscription_tier == SubscriptionTier.FREE else "business"
            }
        
        return {
            "allowed": True,
            "current_gb": round(current_gb, 2),
            "limit_gb": limit_gb,
            "remaining_gb": round(remaining_bytes / (1024 * 1024 * 1024), 2)
        }
    
    def update_storage_usage(self, user: User, bytes_added: int) -> StorageUsage:
        """Update storage usage for user"""
        usage = self.get_or_create_storage_usage(user)
        usage.bytes_used += bytes_added
        usage.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(usage)
        return usage
    
    def get_usage_summary(self, user: User) -> Dict[str, any]:
        """Get complete usage summary for user"""
        scan_check = self.check_scan_limit(user)
        autofix_check = self.check_autofix_limit(user)
        api_check = self.check_api_limit(user)
        storage_check = self.check_storage_limit(user)
        
        return {
            "user_id": user.id,
            "subscription_tier": user.subscription_tier.value,
            "month": self.get_current_month(),
            "scans": {
                "used": scan_check["current"],
                "limit": scan_check["limit"],
                "remaining": scan_check["remaining"]
            },
            "autofixes": {
                "used": autofix_check["current"],
                "limit": autofix_check["limit"],
                "remaining": autofix_check["remaining"]
            },
            "api_requests": {
                "used": api_check["current"],
                "limit": api_check["limit"],
                "remaining": api_check["remaining"]
            },
            "storage": {
                "used_gb": storage_check["current_gb"],
                "limit_gb": storage_check["limit_gb"],
                "remaining_gb": storage_check["remaining_gb"]
            }
        }


def get_usage_tracking_service(db: Session) -> UsageTrackingService:
    """Dependency for getting usage tracking service"""
    return UsageTrackingService(db)
