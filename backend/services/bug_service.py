"""
Bug service - Business logic for bug management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional, List
from datetime import datetime

from models.bug import Bug, BugStatus, BugSeverity, BugType
from models.user import User
from utils.cache import cache_result
from utils.query_optimizer import QueryOptimizer


class BugService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.optimizer = QueryOptimizer(db)
    
    async def create_bug(
        self,
        user_id: int,
        title: str,
        description: str,
        bug_type: BugType,
        severity: BugSeverity,
        target_url: str,
        proof_of_concept: str,
        cvss_score: Optional[float] = None,
        cve_id: Optional[str] = None,
        ai_generated: bool = False,
        ai_confidence: Optional[float] = None
    ) -> Bug:
        """Create new bug report"""
        bug = Bug(
            reporter_id=user_id,
            title=title,
            description=description,
            bug_type=bug_type,
            severity=severity,
            status=BugStatus.PENDING,
            target_url=target_url,
            proof_of_concept=proof_of_concept,
            cvss_score=cvss_score,
            cve_id=cve_id,
            ai_generated=ai_generated,
            ai_confidence=ai_confidence,
            discovery_time_seconds=0
        )
        
        self.db.add(bug)
        await self.db.commit()
        await self.db.refresh(bug)
        
        return bug
    
    @cache_result(ttl=300, key_prefix="bug")
    async def get_bug_by_id(self, bug_id: int) -> Optional[Bug]:
        """Get bug by ID with caching"""
        bugs = await self.optimizer.get_bugs_with_relations([bug_id])
        return bugs[0] if bugs else None
    
    @cache_result(ttl=180, key_prefix="bugs_list")
    async def list_bugs(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[BugStatus] = None,
        severity: Optional[BugSeverity] = None,
        bug_type: Optional[BugType] = None,
        reporter_id: Optional[int] = None
    ) -> List[Bug]:
        """List bugs with filters and caching"""
        query = select(Bug)
        
        filters = []
        if status:
            filters.append(Bug.status == status)
        if severity:
            filters.append(Bug.severity == severity)
        if bug_type:
            filters.append(Bug.bug_type == bug_type)
        if reporter_id:
            filters.append(Bug.reporter_id == reporter_id)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.offset(skip).limit(limit).order_by(Bug.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_bug_status(
        self,
        bug_id: int,
        status: BugStatus,
        validator_id: Optional[int] = None
    ) -> Optional[Bug]:
        """Update bug status"""
        bug = await self.get_bug_by_id(bug_id)
        if not bug:
            return None
        
        bug.status = status
        if validator_id:
            bug.validator_id = validator_id
        
        if status == BugStatus.VALIDATED:
            bug.validated_at = datetime.utcnow()
        elif status == BugStatus.FIXED:
            bug.fixed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(bug)
        
        return bug
    
    async def assign_bug(self, bug_id: int, assignee_id: int) -> Optional[Bug]:
        """Assign bug to user"""
        bug = await self.get_bug_by_id(bug_id)
        if not bug:
            return None
        
        bug.assignee_id = assignee_id
        await self.db.commit()
        await self.db.refresh(bug)
        
        return bug
    
    async def update_bounty(self, bug_id: int, bounty_amount: float) -> Optional[Bug]:
        """Update bug bounty amount"""
        bug = await self.get_bug_by_id(bug_id)
        if not bug:
            return None
        
        bug.bounty_amount = bounty_amount
        await self.db.commit()
        await self.db.refresh(bug)
        
        return bug
    
    async def delete_bug(self, bug_id: int) -> bool:
        """Delete bug"""
        bug = await self.get_bug_by_id(bug_id)
        if not bug:
            return False
        
        await self.db.delete(bug)
        await self.db.commit()
        
        return True
    
    async def get_user_bugs(self, user_id: int) -> List[Bug]:
        """Get all bugs reported by user"""
        result = await self.db.execute(
            select(Bug).where(Bug.reporter_id == user_id)
            .order_by(Bug.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_bugs_by_severity(self, severity: BugSeverity) -> List[Bug]:
        """Get bugs by severity"""
        result = await self.db.execute(
            select(Bug).where(Bug.severity == severity)
            .order_by(Bug.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_pending_bugs(self) -> List[Bug]:
        """Get all pending bugs"""
        result = await self.db.execute(
            select(Bug).where(Bug.status == BugStatus.PENDING)
            .order_by(Bug.created_at.desc())
        )
        return result.scalars().all()
