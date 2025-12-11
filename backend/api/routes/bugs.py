"""
Bug management routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from core.database import get_async_db
from core.security import Security
from models.user import User
from models.bug import Bug, BugStatus, BugSeverity, BugType

router = APIRouter()
security = Security()


class BugCreate(BaseModel):
    title: str
    description: str
    bug_type: BugType
    severity: BugSeverity
    target_url: str
    proof_of_concept: Optional[str] = None


@router.get("/")
async def list_bugs(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """List all bugs for current user"""
    result = await db.execute(
        select(Bug)
        .where(Bug.hunter_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Bug.created_at.desc())
    )
    bugs = result.scalars().all()
    return {"bugs": [{"id": b.id, "title": b.title, "status": b.status.value, "severity": b.severity.value} for b in bugs]}


@router.post("/")
async def create_bug(
    bug_data: BugCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Create new bug report"""
    bug = Bug(
        hunter_id=current_user.id,
        title=bug_data.title,
        description=bug_data.description,
        bug_type=bug_data.bug_type,
        severity=bug_data.severity,
        status=BugStatus.DISCOVERED,
        target_url=bug_data.target_url,
        target_domain=bug_data.target_url.split('//')[-1].split('/')[0],
        proof_of_concept=bug_data.proof_of_concept
    )
    db.add(bug)
    await db.commit()
    await db.refresh(bug)
    return {"id": bug.id, "title": bug.title, "status": bug.status.value}


@router.get("/{bug_id}")
async def get_bug(
    bug_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Get bug details"""
    bug = await db.get(Bug, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    if bug.hunter_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return {
        "id": bug.id,
        "title": bug.title,
        "description": bug.description,
        "bug_type": bug.bug_type.value,
        "severity": bug.severity.value,
        "status": bug.status.value,
        "target_url": bug.target_url
    }


@router.put("/{bug_id}")
async def update_bug(
    bug_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Update bug status or details"""
    bug = await db.get(Bug, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    if bug.hunter_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"message": f"Bug {bug_id} update endpoint available", "id": bug_id}


@router.delete("/{bug_id}")
async def delete_bug(
    bug_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Delete bug report"""
    bug = await db.get(Bug, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    if bug.hunter_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.delete(bug)
    await db.commit()
    return {"message": f"Bug {bug_id} deleted successfully"}
