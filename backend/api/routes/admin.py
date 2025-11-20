"""
Admin routes - Platform administration
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.security import Security
from models.user import User, UserRole

router = APIRouter()
security = Security()


async def get_admin_user(current_user: User = Depends(security.get_current_user)):
    """Verify user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/stats")
async def get_platform_stats(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_admin_user)
):
    """Get platform statistics"""
    # TODO: Implement stats retrieval
    return {"message": "Platform statistics"}


@router.get("/users")
async def list_all_users(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_admin_user)
):
    """List all users"""
    # TODO: Implement user listing
    return {"message": "All users"}


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_admin_user)
):
    """Update user status"""
    # TODO: Implement user status update
    return {"message": f"User {user_id} status updated"}


@router.get("/bugs/pending")
async def list_pending_bugs(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_admin_user)
):
    """List pending bug reports"""
    # TODO: Implement pending bugs listing
    return {"message": "Pending bugs"}


@router.post("/bugs/{bug_id}/verify")
async def verify_bug(
    bug_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_admin_user)
):
    """Verify bug report"""
    # TODO: Implement bug verification
    return {"message": f"Bug {bug_id} verified"}
