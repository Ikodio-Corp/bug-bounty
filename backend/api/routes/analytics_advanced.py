"""
Advanced Analytics API endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import Optional

from core.database import get_db
from models.bug import Bug, Scan, BugStatus, BugSeverity
from models.user import User
from models.marketplace import Payment, PaymentStatus
from utils.cache import cache_result

router = APIRouter()


@router.get("/analytics")
@cache_result(ttl=300, key_prefix="analytics")
async def get_analytics(
    range: str = Query("7d", description="Time range: 24h, 7d, 30d, 90d"),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive analytics data"""
    
    # Calculate date range
    now = datetime.utcnow()
    if range == "24h":
        start_date = now - timedelta(hours=24)
    elif range == "7d":
        start_date = now - timedelta(days=7)
    elif range == "30d":
        start_date = now - timedelta(days=30)
    elif range == "90d":
        start_date = now - timedelta(days=90)
    else:
        start_date = now - timedelta(days=7)
    
    # Bug analytics
    bugs_total = await db.scalar(select(func.count(Bug.id)))
    
    # Bugs by status
    bugs_by_status_query = select(
        Bug.status,
        func.count(Bug.id).label('count')
    ).group_by(Bug.status)
    bugs_by_status = await db.execute(bugs_by_status_query)
    bugs_by_status_data = [
        {"name": status.value if hasattr(status, 'value') else str(status), "value": count}
        for status, count in bugs_by_status
    ]
    
    # Bugs by severity
    bugs_by_severity_query = select(
        Bug.severity,
        func.count(Bug.id).label('count')
    ).group_by(Bug.severity)
    bugs_by_severity = await db.execute(bugs_by_severity_query)
    bugs_by_severity_data = [
        {"name": severity.value if hasattr(severity, 'value') else str(severity), "value": count}
        for severity, count in bugs_by_severity
    ]
    
    # Bug trend
    bug_trend_data = await get_trend_data(db, Bug, start_date, now)
    
    # Scan analytics
    scans_total = await db.scalar(select(func.count(Scan.id)))
    scans_active = await db.scalar(
        select(func.count(Scan.id)).where(Scan.status == "running")
    )
    scans_completed = await db.scalar(
        select(func.count(Scan.id)).where(Scan.status == "completed")
    )
    
    scan_trend_data = await get_trend_data(db, Scan, start_date, now)
    
    # User analytics
    users_total = await db.scalar(select(func.count(User.id)))
    users_active = await db.scalar(
        select(func.count(User.id)).where(User.is_active == True)
    )
    
    user_trend_data = await get_trend_data(db, User, start_date, now)
    
    # Revenue analytics
    revenue_query = select(func.sum(Payment.amount)).where(
        Payment.status == PaymentStatus.COMPLETED
    )
    revenue_total = await db.scalar(revenue_query) or 0
    
    # Revenue by source
    revenue_by_source_query = select(
        Payment.payment_type,
        func.sum(Payment.amount).label('total')
    ).where(
        Payment.status == PaymentStatus.COMPLETED
    ).group_by(Payment.payment_type)
    
    revenue_by_source = await db.execute(revenue_by_source_query)
    revenue_by_source_data = [
        {"name": payment_type or "Other", "value": float(total)}
        for payment_type, total in revenue_by_source
    ]
    
    # Revenue trend
    revenue_trend_data = await get_revenue_trend(db, start_date, now)
    
    return {
        "bugs": {
            "total": bugs_total or 0,
            "byStatus": bugs_by_status_data,
            "bySeverity": bugs_by_severity_data,
            "trend": bug_trend_data
        },
        "scans": {
            "total": scans_total or 0,
            "active": scans_active or 0,
            "completed": scans_completed or 0,
            "trend": scan_trend_data
        },
        "users": {
            "total": users_total or 0,
            "active": users_active or 0,
            "trend": user_trend_data
        },
        "revenue": {
            "total": float(revenue_total),
            "bySource": revenue_by_source_data,
            "trend": revenue_trend_data
        }
    }


async def get_trend_data(db: AsyncSession, model, start_date: datetime, end_date: datetime):
    """Get trend data for a model"""
    
    from sqlalchemy import cast, Date
    
    query = select(
        cast(model.created_at, Date).label('date'),
        func.count(model.id).label('count')
    ).where(
        model.created_at >= start_date,
        model.created_at <= end_date
    ).group_by(
        cast(model.created_at, Date)
    ).order_by(
        cast(model.created_at, Date)
    )
    
    result = await db.execute(query)
    
    return [
        {"date": date.strftime("%Y-%m-%d"), "count": count}
        for date, count in result
    ]


async def get_revenue_trend(db: AsyncSession, start_date: datetime, end_date: datetime):
    """Get revenue trend data"""
    
    from sqlalchemy import cast, Date
    
    query = select(
        cast(Payment.created_at, Date).label('date'),
        func.sum(Payment.amount).label('amount')
    ).where(
        Payment.status == PaymentStatus.COMPLETED,
        Payment.created_at >= start_date,
        Payment.created_at <= end_date
    ).group_by(
        cast(Payment.created_at, Date)
    ).order_by(
        cast(Payment.created_at, Date)
    )
    
    result = await db.execute(query)
    
    return [
        {"date": date.strftime("%Y-%m-%d"), "amount": float(amount)}
        for date, amount in result
    ]


@router.get("/analytics/export")
async def export_analytics(
    format: str = Query("csv", description="Export format: csv, json, pdf"),
    range: str = Query("30d", description="Time range"),
    db: AsyncSession = Depends(get_db)
):
    """Export analytics data"""
    
    # Get analytics data
    data = await get_analytics(range, db)
    
    if format == "json":
        return data
    
    elif format == "csv":
        import csv
        from io import StringIO
        from fastapi.responses import StreamingResponse
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(["Metric", "Value"])
        
        # Write data
        writer.writerow(["Total Bugs", data["bugs"]["total"]])
        writer.writerow(["Total Scans", data["scans"]["total"]])
        writer.writerow(["Active Users", data["users"]["active"]])
        writer.writerow(["Total Revenue", data["revenue"]["total"]])
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=analytics_{range}.csv"}
        )
    
    elif format == "pdf":
        # TODO: Implement PDF export
        return {"message": "PDF export not yet implemented"}
    
    return {"error": "Invalid format"}
