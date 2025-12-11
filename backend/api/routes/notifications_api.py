"""
Notification API routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.security import get_current_user
from models.user import User
from services.notification_service import EmailNotificationService as NotificationService

router = APIRouter()


@router.get("/notifications")
async def get_notifications(
    limit: int = 50,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    notification_service = NotificationService(db)
    
    notifications = await notification_service.get_user_notifications(
        user_id=current_user.id,
        limit=limit,
        unread_only=unread_only
    )
    
    return {
        "notifications": notifications,
        "total": len(notifications)
    }


@router.post("/notifications/{index}/read")
async def mark_notification_read(
    index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification_service = NotificationService(db)
    
    await notification_service.mark_as_read(current_user.id, index)
    
    return {"message": "Notification marked as read"}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    notification_service = NotificationService(db)
    
    await notification_service.mark_all_as_read(current_user.id)
    
    return {"message": "All notifications marked as read"}


@router.get("/notifications/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    notification_service = NotificationService(db)
    
    notifications = await notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=True
    )
    
    return {"count": len(notifications)}


@router.put("/notifications/preferences")
async def update_notification_preferences(
    email_notifications: bool = None,
    push_notifications: bool = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences"""
    if email_notifications is not None:
        current_user.email_notifications = email_notifications
    
    if push_notifications is not None:
        current_user.push_notifications = push_notifications
    
    db.commit()
    
    return {
        "message": "Notification preferences updated",
        "preferences": {
            "email_notifications": current_user.email_notifications,
            "push_notifications": current_user.push_notifications
        }
    }
