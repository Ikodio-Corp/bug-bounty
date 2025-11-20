"""
Creator subscription routes - OnlyFans-style creator economy
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.security import Security
from models.user import User

router = APIRouter()
security = Security()


@router.get("/creators")
async def list_creators(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """List creators"""
    # TODO: Implement creator listing
    return {"message": "Creator directory"}


@router.post("/subscribe/{creator_id}")
async def subscribe_to_creator(
    creator_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Subscribe to creator"""
    # TODO: Implement subscription
    return {"message": f"Subscribed to creator {creator_id}"}


@router.get("/subscriptions")
async def get_subscriptions(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Get user subscriptions"""
    # TODO: Implement subscriptions listing
    return {"message": "Your subscriptions"}


@router.get("/earnings")
async def get_creator_earnings(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Get creator earnings"""
    # TODO: Implement earnings retrieval
    return {"message": "Creator earnings"}
