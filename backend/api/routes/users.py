"""
User management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.security import Security
from models.user import User

router = APIRouter()
security = Security()


@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(security.get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at
    }


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get user by ID"""
    # TODO: Implement user retrieval with profile data
    return {"message": f"Get user {user_id}"}


@router.put("/me")
async def update_current_user(
    current_user: User = Depends(security.get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update current user profile"""
    # TODO: Implement profile update
    return {"message": "Profile updated"}


@router.get("/me/stats")
async def get_user_stats(
    current_user: User = Depends(security.get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user statistics"""
    # TODO: Implement stats retrieval
    return {"message": "User statistics"}
