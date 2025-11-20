"""
Admin service for platform management
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta

from models.user import User
from models.bug import Bug
from models.community import Scan
from core.redis import get_redis


class AdminService:
    """Service for admin operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = get_redis()
    
    def get_platform_overview(self) -> Dict:
        """Get platform overview statistics"""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(
            User.is_active == True,
            User.last_login >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        total_bugs = self.db.query(Bug).count()
        pending_bugs = self.db.query(Bug).filter(Bug.validated == False).count()
        validated_bugs = self.db.query(Bug).filter(Bug.validated == True).count()
        
        total_scans = self.db.query(Scan).count()
        active_scans = self.db.query(Scan).filter(
            Scan.status.in_(['pending', 'running'])
        ).count()
        
        total_bounties = self.db.query(func.sum(Bug.bounty_amount)).filter(
            Bug.validated == True
        ).scalar() or 0
        
        recent_revenue = self.db.query(func.sum(Bug.bounty_amount)).filter(
            Bug.validated == True,
            Bug.created_at >= datetime.utcnow() - timedelta(days=30)
        ).scalar() or 0
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users
            },
            "bugs": {
                "total": total_bugs,
                "pending": pending_bugs,
                "validated": validated_bugs,
                "rejected": total_bugs - pending_bugs - validated_bugs
            },
            "scans": {
                "total": total_scans,
                "active": active_scans,
                "completed": total_scans - active_scans
            },
            "revenue": {
                "total": float(total_bounties),
                "this_month": float(recent_revenue)
            }
        }
    
    def get_users_list(
        self,
        page: int = 1,
        per_page: int = 50,
        search: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict:
        """Get paginated users list with filters"""
        query = self.db.query(User)
        
        if search:
            query = query.filter(
                (User.username.ilike(f"%{search}%")) |
                (User.email.ilike(f"%{search}%")) |
                (User.full_name.ilike(f"%{search}%"))
            )
        
        if role:
            query = query.filter(User.role == role)
        
        if status == "active":
            query = query.filter(User.is_active == True)
        elif status == "inactive":
            query = query.filter(User.is_active == False)
        elif status == "verified":
            query = query.filter(User.is_verified == True)
        elif status == "unverified":
            query = query.filter(User.is_verified == False)
        
        total = query.count()
        users = query.order_by(desc(User.created_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        return {
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "subscription_tier": user.subscription_tier,
                    "reputation_score": user.reputation_score,
                    "total_bugs_found": user.total_bugs_found,
                    "total_bounties_earned": user.total_bounties_earned,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
                for user in users
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }
    
    def update_user_status(self, user_id: int, is_active: bool) -> Dict:
        """Update user active status"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "message": "User not found"}
        
        user.is_active = is_active
        self.db.commit()
        
        return {
            "success": True,
            "message": f"User {'activated' if is_active else 'deactivated'} successfully"
        }
    
    def update_user_role(self, user_id: int, role: str) -> Dict:
        """Update user role"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "message": "User not found"}
        
        user.role = role
        self.db.commit()
        
        return {"success": True, "message": "User role updated successfully"}
    
    def get_bugs_list(
        self,
        page: int = 1,
        per_page: int = 50,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict:
        """Get paginated bugs list with filters"""
        query = self.db.query(Bug)
        
        if search:
            query = query.filter(
                (Bug.title.ilike(f"%{search}%")) |
                (Bug.description.ilike(f"%{search}%"))
            )
        
        if status == "pending":
            query = query.filter(Bug.validated == False)
        elif status == "validated":
            query = query.filter(Bug.validated == True)
        elif status == "paid":
            query = query.filter(Bug.paid_out == True)
        
        if severity:
            query = query.filter(Bug.severity == severity)
        
        total = query.count()
        bugs = query.order_by(desc(Bug.created_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        return {
            "bugs": [
                {
                    "id": bug.id,
                    "title": bug.title,
                    "severity": bug.severity,
                    "vulnerability_type": bug.vulnerability_type,
                    "validated": bug.validated,
                    "paid_out": bug.paid_out,
                    "bounty_amount": float(bug.bounty_amount) if bug.bounty_amount else 0,
                    "hunter_id": bug.hunter_id,
                    "target_url": bug.target_url,
                    "created_at": bug.created_at.isoformat()
                }
                for bug in bugs
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }
    
    def validate_bug(self, bug_id: int, bounty_amount: float) -> Dict:
        """Validate bug and set bounty"""
        bug = self.db.query(Bug).filter(Bug.id == bug_id).first()
        if not bug:
            return {"success": False, "message": "Bug not found"}
        
        bug.validated = True
        bug.bounty_amount = bounty_amount
        bug.validated_at = datetime.utcnow()
        
        hunter = self.db.query(User).filter(User.id == bug.hunter_id).first()
        if hunter:
            hunter.total_bugs_found += 1
            hunter.total_bounties_earned += bounty_amount
            hunter.reputation_score += int(bounty_amount / 10)
        
        self.db.commit()
        
        return {"success": True, "message": "Bug validated successfully"}
    
    def reject_bug(self, bug_id: int, reason: str) -> Dict:
        """Reject bug with reason"""
        bug = self.db.query(Bug).filter(Bug.id == bug_id).first()
        if not bug:
            return {"success": False, "message": "Bug not found"}
        
        bug.validated = False
        bug.rejection_reason = reason
        self.db.commit()
        
        return {"success": True, "message": "Bug rejected successfully"}
    
    def get_scans_list(
        self,
        page: int = 1,
        per_page: int = 50,
        status: Optional[str] = None
    ) -> Dict:
        """Get paginated scans list with filters"""
        query = self.db.query(Scan)
        
        if status:
            query = query.filter(Scan.status == status)
        
        total = query.count()
        scans = query.order_by(desc(Scan.created_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        return {
            "scans": [
                {
                    "id": scan.id,
                    "target_url": scan.target_url,
                    "scan_type": scan.scan_type,
                    "status": scan.status,
                    "vulnerabilities_found": scan.vulnerabilities_found,
                    "user_id": scan.user_id,
                    "progress": scan.progress,
                    "created_at": scan.created_at.isoformat(),
                    "completed_at": scan.completed_at.isoformat() if scan.completed_at else None
                }
                for scan in scans
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }
    
    def get_analytics_data(self, days: int = 30) -> Dict:
        """Get analytics data for admin dashboard"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        new_users = self.db.query(func.count(User.id)).filter(
            User.created_at >= start_date
        ).scalar()
        
        new_bugs = self.db.query(func.count(Bug.id)).filter(
            Bug.created_at >= start_date
        ).scalar()
        
        new_scans = self.db.query(func.count(Scan.id)).filter(
            Scan.created_at >= start_date
        ).scalar()
        
        daily_stats = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            users_count = self.db.query(func.count(User.id)).filter(
                and_(User.created_at >= day_start, User.created_at < day_end)
            ).scalar()
            
            bugs_count = self.db.query(func.count(Bug.id)).filter(
                and_(Bug.created_at >= day_start, Bug.created_at < day_end)
            ).scalar()
            
            scans_count = self.db.query(func.count(Scan.id)).filter(
                and_(Scan.created_at >= day_start, Scan.created_at < day_end)
            ).scalar()
            
            daily_stats.append({
                "date": day_start.strftime('%Y-%m-%d'),
                "users": users_count,
                "bugs": bugs_count,
                "scans": scans_count
            })
        
        return {
            "period": f"Last {days} days",
            "new_users": new_users,
            "new_bugs": new_bugs,
            "new_scans": new_scans,
            "daily_stats": list(reversed(daily_stats))
        }
    
    def delete_user(self, user_id: int) -> Dict:
        """Delete user account"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "message": "User not found"}
        
        if user.role == "admin":
            return {"success": False, "message": "Cannot delete admin user"}
        
        self.db.delete(user)
        self.db.commit()
        
        return {"success": True, "message": "User deleted successfully"}
