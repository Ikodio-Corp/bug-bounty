"""
User leaderboard endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta

from core.database import get_db
from models.user import User

router = APIRouter()


@router.get("/users/leaderboard")
async def get_leaderboard(
    timeframe: str = Query("all", regex="^(all|month|week)$"),
    category: str = Query("reputation", regex="^(reputation|bounties|bugs)$"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get leaderboard of top hunters"""
    query = db.query(User).filter(User.is_active == True)
    
    if timeframe == "month":
        start_date = datetime.utcnow() - timedelta(days=30)
        query = query.filter(User.created_at >= start_date)
    elif timeframe == "week":
        start_date = datetime.utcnow() - timedelta(days=7)
        query = query.filter(User.created_at >= start_date)
    
    if category == "reputation":
        query = query.order_by(desc(User.reputation_score))
    elif category == "bounties":
        query = query.order_by(desc(User.total_bounties_earned))
    elif category == "bugs":
        query = query.order_by(desc(User.total_bugs_found))
    
    hunters = query.limit(limit).all()
    
    leaderboard = []
    for hunter in hunters:
        leaderboard.append({
            "id": hunter.id,
            "username": hunter.username,
            "avatar_url": hunter.avatar_url,
            "location": hunter.location,
            "reputation_score": hunter.reputation_score,
            "total_bounties_earned": hunter.total_bounties_earned,
            "total_bugs_found": hunter.total_bugs_found,
            "hunter_rank": hunter.hunter_rank
        })
    
    return {
        "leaderboard": leaderboard,
        "timeframe": timeframe,
        "category": category,
        "total": len(leaderboard)
    }
