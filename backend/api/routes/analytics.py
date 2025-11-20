"""
Analytics API routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from middleware.auth import get_current_user
from models.user import User
from services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/analytics/dashboard")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard analytics for current user"""
    analytics_service = AnalyticsService(db)
    stats = analytics_service.get_dashboard_stats(current_user.id)
    
    return stats


@router.get("/analytics/platform")
async def get_platform_analytics(
    db: Session = Depends(get_db)
):
    """Get overall platform statistics"""
    analytics_service = AnalyticsService(db)
    stats = analytics_service.get_platform_stats()
    
    return stats


@router.get("/analytics/scans")
async def get_scan_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get scan statistics for current user"""
    analytics_service = AnalyticsService(db)
    stats = analytics_service.get_scan_statistics(current_user.id)
    
    return stats


@router.get("/analytics/bugs/trends")
async def get_bug_trends(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get bug submission trends"""
    analytics_service = AnalyticsService(db)
    trends = analytics_service.get_bug_trends(current_user.id, days)
    
    return trends


@router.get("/analytics/earnings")
async def get_earnings_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get earnings breakdown"""
    analytics_service = AnalyticsService(db)
    earnings = analytics_service.get_earnings_breakdown(current_user.id)
    
    return earnings


@router.get("/analytics/vulnerabilities/top")
async def get_top_vulnerabilities(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get most common vulnerability types"""
    analytics_service = AnalyticsService(db)
    top_vulns = analytics_service.get_top_vulnerabilities(current_user.id, limit)
    
    return {"vulnerabilities": top_vulns}
