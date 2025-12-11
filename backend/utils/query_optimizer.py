"""
Database query optimization utilities
"""
from typing import List, Optional, Any
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session, joinedload, selectinload, subqueryload
from models.bug import Bug  # , Scan  # Scan doesn't exist
from models.user import User
from models.marketplace import Tool


class QueryOptimizer:
    """Optimize database queries for better performance"""
    
    @staticmethod
    def get_bugs_with_relations(
        db: Session,
        filters: Optional[dict] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[Bug]:
        """
        Optimized bug query with eager loading of relations
        Prevents N+1 query problem
        """
        query = db.query(Bug).options(
            joinedload(Bug.reporter),
            joinedload(Bug.assigned_to),
            selectinload(Bug.comments),
            selectinload(Bug.attachments)
        )
        
        if filters:
            if filters.get('severity'):
                query = query.filter(Bug.severity == filters['severity'])
            if filters.get('status'):
                query = query.filter(Bug.status == filters['status'])
            if filters.get('reporter_id'):
                query = query.filter(Bug.reporter_id == filters['reporter_id'])
        
        # Add ordering
        query = query.order_by(Bug.created_at.desc())
        
        # Pagination
        offset = (page - 1) * limit
        return query.offset(offset).limit(limit).all()
    
    @staticmethod
    def get_bugs_count(db: Session, filters: Optional[dict] = None) -> int:
        """
        Optimized count query
        Uses COUNT(*) without loading objects
        """
        query = db.query(func.count(Bug.id))
        
        if filters:
            if filters.get('severity'):
                query = query.filter(Bug.severity == filters['severity'])
            if filters.get('status'):
                query = query.filter(Bug.status == filters['status'])
            if filters.get('reporter_id'):
                query = query.filter(Bug.reporter_id == filters['reporter_id'])
        
        return query.scalar()
    
    @staticmethod
    def get_user_statistics(db: Session, user_id: int) -> dict:
        """
        Optimized user statistics query
        Uses aggregation instead of loading all records
        """
        stats = {
            'total_bugs': db.query(func.count(Bug.id))
                .filter(Bug.reporter_id == user_id).scalar(),
            'critical_bugs': db.query(func.count(Bug.id))
                .filter(and_(Bug.reporter_id == user_id, Bug.severity == 'critical')).scalar(),
            'high_bugs': db.query(func.count(Bug.id))
                .filter(and_(Bug.reporter_id == user_id, Bug.severity == 'high')).scalar(),
            'total_bounty': db.query(func.sum(Bug.bounty_amount))
                .filter(and_(Bug.reporter_id == user_id, Bug.status == 'resolved')).scalar() or 0,
            'total_scans': db.query(func.count(Scan.id))
                .filter(Scan.user_id == user_id).scalar(),
        }
        
        return stats
    
    @staticmethod
    def get_marketplace_tools_optimized(
        db: Session,
        category: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[Tool]:
        """
        Optimized marketplace query with creator info
        """
        query = db.query(Tool).options(
            joinedload(Tool.creator)
        ).filter(Tool.status == 'active')
        
        if category:
            query = query.filter(Tool.category == category)
        
        # Order by popularity (downloads * rating)
        query = query.order_by(
            (Tool.downloads * Tool.rating).desc()
        )
        
        offset = (page - 1) * limit
        return query.offset(offset).limit(limit).all()
    
    @staticmethod
    def get_scan_with_vulnerabilities(
        db: Session,
        scan_id: int
    ) -> Optional[Scan]:
        """
        Optimized scan query with all vulnerabilities
        Uses selectinload for one-to-many relationship
        """
        return db.query(Scan).options(
            joinedload(Scan.user),
            selectinload(Scan.vulnerabilities),
            selectinload(Scan.bugs)
        ).filter(Scan.id == scan_id).first()
    
    @staticmethod
    def bulk_update_bug_status(
        db: Session,
        bug_ids: List[int],
        new_status: str
    ) -> int:
        """
        Optimized bulk update
        Uses single UPDATE query instead of updating one by one
        """
        result = db.query(Bug).filter(Bug.id.in_(bug_ids)).update(
            {Bug.status: new_status},
            synchronize_session=False
        )
        db.commit()
        return result
    
    @staticmethod
    def get_user_leaderboard(
        db: Session,
        limit: int = 100
    ) -> List[dict]:
        """
        Optimized leaderboard query
        Aggregates data without loading full user objects
        """
        query = db.query(
            User.id,
            User.username,
            User.avatar_url,
            func.count(Bug.id).label('bug_count'),
            func.sum(Bug.bounty_amount).label('total_earnings'),
            User.reputation
        ).join(Bug, User.id == Bug.reporter_id) \
         .filter(Bug.status == 'resolved') \
         .group_by(User.id) \
         .order_by(func.sum(Bug.bounty_amount).desc()) \
         .limit(limit)
        
        results = query.all()
        
        return [
            {
                'user_id': r.id,
                'username': r.username,
                'avatar_url': r.avatar_url,
                'bug_count': r.bug_count,
                'total_earnings': float(r.total_earnings or 0),
                'reputation': r.reputation
            }
            for r in results
        ]
    
    @staticmethod
    def search_bugs_optimized(
        db: Session,
        search_term: str,
        filters: Optional[dict] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[Bug]:
        """
        Optimized full-text search for bugs
        Uses ILIKE for case-insensitive search
        """
        query = db.query(Bug).options(
            joinedload(Bug.reporter)
        )
        
        # Search in title and description
        search_filter = or_(
            Bug.title.ilike(f'%{search_term}%'),
            Bug.description.ilike(f'%{search_term}%')
        )
        query = query.filter(search_filter)
        
        if filters:
            if filters.get('severity'):
                query = query.filter(Bug.severity == filters['severity'])
            if filters.get('status'):
                query = query.filter(Bug.status == filters['status'])
        
        query = query.order_by(Bug.created_at.desc())
        
        offset = (page - 1) * limit
        return query.offset(offset).limit(limit).all()


class IndexManager:
    """Manage database indexes for optimization"""
    
    @staticmethod
    def create_performance_indexes(db: Session):
        """
        Create indexes for frequently queried columns
        Run this during deployment
        """
        indexes = [
            # Bug indexes
            "CREATE INDEX IF NOT EXISTS idx_bug_status ON bugs(status)",
            "CREATE INDEX IF NOT EXISTS idx_bug_severity ON bugs(severity)",
            "CREATE INDEX IF NOT EXISTS idx_bug_reporter ON bugs(reporter_id)",
            "CREATE INDEX IF NOT EXISTS idx_bug_created ON bugs(created_at)",
            
            # Scan indexes
            "CREATE INDEX IF NOT EXISTS idx_scan_user ON scans(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_scan_status ON scans(status)",
            "CREATE INDEX IF NOT EXISTS idx_scan_created ON scans(created_at)",
            
            # Tool indexes
            "CREATE INDEX IF NOT EXISTS idx_tool_category ON tools(category)",
            "CREATE INDEX IF NOT EXISTS idx_tool_status ON tools(status)",
            "CREATE INDEX IF NOT EXISTS idx_tool_creator ON tools(creator_id)",
            
            # User indexes
            "CREATE INDEX IF NOT EXISTS idx_user_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_user_username ON users(username)",
            
            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_bug_status_severity ON bugs(status, severity)",
            "CREATE INDEX IF NOT EXISTS idx_scan_user_status ON scans(user_id, status)",
        ]
        
        for index_sql in indexes:
            try:
                db.execute(index_sql)
            except Exception as e:
                print(f"Index creation error: {e}")
        
        db.commit()


query_optimizer = QueryOptimizer()
index_manager = IndexManager()
