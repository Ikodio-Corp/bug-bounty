"""
Social routes - Social network features (LinkedIn-style)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.security import Security
from models.user import User

router = APIRouter()
security = Security()


@router.get("/feed")
async def get_social_feed(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Get social feed"""
    # TODO: Implement social feed
    return {"message": "Social feed"}


@router.post("/posts")
async def create_post(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Create post"""
    # TODO: Implement post creation
    return {"message": "Post created"}


@router.post("/connect/{user_id}")
async def connect_with_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Connect with user"""
    # TODO: Implement connection request
    return {"message": f"Connection request sent to user {user_id}"}


@router.get("/connections")
async def get_connections(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Get connections"""
    # TODO: Implement connections listing
    return {"message": "Connections"}
