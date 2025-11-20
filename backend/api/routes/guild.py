"""
Guild routes - Community guilds and governance
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.security import Security
from models.user import User

router = APIRouter()
security = Security()


@router.get("/")
async def list_guilds(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """List all guilds"""
    # TODO: Implement guild listing
    return {"message": "Guild listing"}


@router.post("/join/{guild_id}")
async def join_guild(
    guild_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Join guild"""
    # TODO: Implement guild joining
    return {"message": f"Joined guild {guild_id}"}


@router.get("/{guild_id}/proposals")
async def list_guild_proposals(
    guild_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """List guild proposals"""
    # TODO: Implement proposal listing
    return {"message": f"Guild {guild_id} proposals"}


@router.post("/{guild_id}/proposals")
async def create_guild_proposal(
    guild_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Create guild proposal"""
    # TODO: Implement proposal creation
    return {"message": "Proposal created"}
