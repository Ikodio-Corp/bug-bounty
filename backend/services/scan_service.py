"""
Scan service - Business logic for security scanning
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime

from models.bug import Scan
from utils.cache import cache_result
from utils.query_optimizer import QueryOptimizer


class ScanService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.optimizer = QueryOptimizer(db)
    
    async def create_scan(
        self,
        user_id: int,
        target_url: str,
        scan_type: str,
        target_platform: Optional[str] = None
    ) -> Scan:
        """Create new scan"""
        scan = Scan(
            user_id=user_id,
            target_url=target_url,
            scan_type=scan_type,
            target_platform=target_platform,
            status="queued",
            start_time=datetime.utcnow()
        )
        
        self.db.add(scan)
        await self.db.commit()
        await self.db.refresh(scan)
        
        return scan
    
    @cache_result(ttl=180, key_prefix="scan")
    async def get_scan_by_id(self, scan_id: int) -> Optional[Scan]:
        """Get scan by ID with caching"""
        result = await self.db.execute(
            select(Scan).where(Scan.id == scan_id)
        )
        return result.scalar_one_or_none()
    
    async def update_scan_status(
        self,
        scan_id: int,
        status: str,
        results: Optional[dict] = None,
        error_message: Optional[str] = None
    ) -> Optional[Scan]:
        """Update scan status and results"""
        scan = await self.get_scan_by_id(scan_id)
        if not scan:
            return None
        
        scan.status = status
        
        if status == "completed":
            scan.end_time = datetime.utcnow()
            if scan.start_time:
                duration = (scan.end_time - scan.start_time).total_seconds()
                scan.duration_seconds = int(duration)
        
        if results:
            scan.results = results
            scan.vulnerabilities_found = results.get("vulnerabilities_found", 0)
        
        if error_message:
            scan.error_message = error_message
        
        await self.db.commit()
        await self.db.refresh(scan)
        
        return scan
    
    @cache_result(ttl=120, key_prefix="user_scans")
    async def list_user_scans(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Scan]:
        """List scans by user with caching"""
        result = await self.db.execute(
            select(Scan).where(Scan.user_id == user_id)
            .order_by(Scan.created_at.desc())
            .offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def get_active_scans(self) -> List[Scan]:
        """Get all active scans"""
        result = await self.db.execute(
            select(Scan).where(Scan.status.in_(["queued", "running"]))
            .order_by(Scan.created_at.asc())
        )
        return result.scalars().all()
