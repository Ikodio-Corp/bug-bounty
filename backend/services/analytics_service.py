"""
Analytics service for tracking metrics and insights
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta

from models.bug import Bug
# from models.community import Scan  # Model doesn't exist
from models.user import User
from core.redis import get_redis


class AnalyticsService:
    """Service for analytics and metrics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = get_redis()
    
    def get_dashboard_stats(self, user_id: int) -> Dict:
        """Get dashboard statistics for user"""
        cache_key = f"analytics:dashboard:{user_id}"
        cached = self.redis_client.get(cache_key)
        
        if cached:
            return eval(cached)
        
        user = self.db.query(User).filter(User.id == user_id).first()
        
        total_scans = self.db.query(Scan).filter(Scan.user_id == user_id).count()
        total_bugs = self.db.query(Bug).filter(Bug.hunter_id == user_id).count()
        validated_bugs = self.db.query(Bug).filter(
            Bug.hunter_id == user_id,
            Bug.validated == True
        ).count()
        
        active_scans = self.db.query(Scan).filter(
            Scan.user_id == user_id,
            Scan.status.in_(['pending', 'running'])
        ).count()
        
        recent_earnings = self.db.query(func.sum(Bug.bounty_amount)).filter(
            Bug.hunter_id == user_id,
            Bug.validated == True,
            Bug.created_at >= datetime.utcnow() - timedelta(days=30)
        ).scalar() or 0
        
        stats = {
            "total_scans": total_scans,
            "total_bugs": total_bugs,
            "validated_bugs": validated_bugs,
            "active_scans": active_scans,
            "total_earnings": user.total_bounties_earned,
            "recent_earnings": float(recent_earnings),
            "reputation_score": user.reputation_score,
            "hunter_rank": user.hunter_rank,
            "validation_rate": (validated_bugs / total_bugs * 100) if total_bugs > 0 else 0
        }
        
        self.redis_client.setex(cache_key, 300, str(stats))
        
        return stats
    
    def get_platform_stats(self) -> Dict:
        """Get overall platform statistics"""
        cache_key = "analytics:platform:stats"
        cached = self.redis_client.get(cache_key)
        
        if cached:
            return eval(cached)
        
        total_users = self.db.query(User).filter(User.is_active == True).count()
        total_scans = self.db.query(Scan).count()
        total_bugs = self.db.query(Bug).count()
        total_bounties = self.db.query(func.sum(Bug.bounty_amount)).filter(
            Bug.validated == True
        ).scalar() or 0
        
        active_hunters = self.db.query(User).filter(
            User.is_active == True,
            User.total_bugs_found > 0
        ).count()
        
        stats = {
            "total_users": total_users,
            "active_hunters": active_hunters,
            "total_scans": total_scans,
            "total_bugs": total_bugs,
            "total_bounties_paid": float(total_bounties),
            "avg_bounty": float(total_bounties / total_bugs) if total_bugs > 0 else 0
        }
        
        self.redis_client.setex(cache_key, 600, str(stats))
        
        return stats
    
    def get_scan_statistics(self, user_id: int) -> Dict:
        """Get scan statistics for user"""
        scans = self.db.query(Scan).filter(Scan.user_id == user_id).all()
        
        total = len(scans)
        completed = len([s for s in scans if s.status == 'completed'])
        failed = len([s for s in scans if s.status == 'failed'])
        
        total_vulns = sum(s.vulnerabilities_found for s in scans)
        avg_vulns = total_vulns / completed if completed > 0 else 0
        
        severity_breakdown = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for scan in scans:
            if scan.severity_breakdown:
                for severity, count in scan.severity_breakdown.items():
                    if severity in severity_breakdown:
                        severity_breakdown[severity] += count
        
        return {
            "total_scans": total,
            "completed_scans": completed,
            "failed_scans": failed,
            "total_vulnerabilities": total_vulns,
            "avg_vulnerabilities_per_scan": avg_vulns,
            "severity_breakdown": severity_breakdown
        }
    
    def get_bug_trends(self, user_id: int, days: int = 30) -> Dict:
        """Get bug submission trends"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        bugs = self.db.query(Bug).filter(
            Bug.hunter_id == user_id,
            Bug.created_at >= start_date
        ).all()
        
        daily_counts = {}
        for bug in bugs:
            date_str = bug.created_at.strftime('%Y-%m-%d')
            daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
        
        severity_counts = {
            "critical": len([b for b in bugs if b.severity == 'critical']),
            "high": len([b for b in bugs if b.severity == 'high']),
            "medium": len([b for b in bugs if b.severity == 'medium']),
            "low": len([b for b in bugs if b.severity == 'low'])
        }
        
        return {
            "daily_submissions": daily_counts,
            "severity_distribution": severity_counts,
            "total_period": len(bugs),
            "validation_rate": len([b for b in bugs if b.validated]) / len(bugs) * 100 if bugs else 0
        }
    
    def get_earnings_breakdown(self, user_id: int) -> Dict:
        """Get earnings breakdown by severity and period"""
        bugs = self.db.query(Bug).filter(
            Bug.hunter_id == user_id,
            Bug.validated == True
        ).all()
        
        by_severity = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for bug in bugs:
            if bug.severity in by_severity:
                by_severity[bug.severity] += float(bug.bounty_amount)
        
        this_month = [b for b in bugs if b.created_at >= datetime.utcnow() - timedelta(days=30)]
        last_month = [b for b in bugs if 
                     datetime.utcnow() - timedelta(days=60) <= b.created_at < datetime.utcnow() - timedelta(days=30)]
        
        this_month_total = sum(float(b.bounty_amount) for b in this_month)
        last_month_total = sum(float(b.bounty_amount) for b in last_month)
        
        growth = ((this_month_total - last_month_total) / last_month_total * 100) if last_month_total > 0 else 0
        
        return {
            "by_severity": by_severity,
            "this_month": this_month_total,
            "last_month": last_month_total,
            "month_over_month_growth": growth,
            "total_all_time": sum(by_severity.values())
        }
    
    def get_top_vulnerabilities(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get most common vulnerability types found by user"""
        bugs = self.db.query(Bug).filter(Bug.hunter_id == user_id).all()
        
        vuln_counts = {}
        for bug in bugs:
            vuln_type = bug.vulnerability_type
            if vuln_type:
                vuln_counts[vuln_type] = vuln_counts.get(vuln_type, 0) + 1
        
        sorted_vulns = sorted(vuln_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [
            {"vulnerability_type": vuln, "count": count}
            for vuln, count in sorted_vulns
        ]
