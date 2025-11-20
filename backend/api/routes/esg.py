"""
ESG routes - ESG scoring with security integration
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.security import Security
from models.user import User

router = APIRouter()
security = Security()


@router.get("/scores/{company}")
async def get_esg_score(
    company: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Get ESG score"""
    # TODO: Implement ESG score retrieval
    return {"message": f"ESG score for {company}"}


@router.get("/scores")
async def list_esg_scores(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """List ESG scores"""
    # TODO: Implement ESG score listing
    return {"message": "ESG scores"}


@router.post("/scores/calculate")
async def calculate_esg_score(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Calculate ESG score"""
    # TODO: Implement ESG score calculation
    return {"message": "ESG score calculation started"}
