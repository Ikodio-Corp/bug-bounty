"""
Maintenance tasks
"""

from typing import Dict, Any
import asyncio
from datetime import datetime, timedelta


def run_async(coro):
    """Helper to run async code in sync context"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


def cleanup_old_scans() -> Dict[str, Any]:
    """Cleanup scans older than 90 days"""
    async def _cleanup():
        from core.database import async_session_maker
        from models.bug import Scan
        from sqlalchemy import select, delete
        
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        async with async_session_maker() as db:
            result = await db.execute(
                delete(Scan).where(Scan.created_at < cutoff_date)
            )
            
            await db.commit()
            
            return {"deleted": result.rowcount}
    
    return run_async(_cleanup())


def backup_database() -> Dict[str, Any]:
    """Trigger database backup"""
    import subprocess
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/app/database/backups/backup_{timestamp}.sql.gz"
    
    try:
        subprocess.run(["/app/scripts/backup.sh"], check=True)
        return {"success": True, "backup_file": backup_file}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": str(e)}


def update_statistics() -> Dict[str, Any]:
    """Update platform statistics"""
    async def _update():
        from core.database import async_session_maker
        from models.user import User, UserProfile
        from models.bug import Bug
        from sqlalchemy import select, func
        
        async with async_session_maker() as db:
            total_users = await db.execute(select(func.count(User.id)))
            total_bugs = await db.execute(select(func.count(Bug.id)))
            
            return {
                "total_users": total_users.scalar(),
                "total_bugs": total_bugs.scalar()
            }
    
    return run_async(_update())


def cleanup_expired_sessions() -> Dict[str, Any]:
    """Cleanup expired Redis sessions"""
    async def _cleanup():
        from core.redis import redis_cache
        
        keys_deleted = 0
        
        # Scan for expired session keys
        cursor = 0
        pattern = "session:*"
        
        # This would need proper Redis SCAN implementation
        # Simplified version for now
        
        return {"keys_deleted": keys_deleted}
    
    return run_async(_cleanup())


def process_pending_payments() -> Dict[str, Any]:
    """Process pending payments"""
    async def _process():
        from core.database import async_session_maker
        from models.marketplace import Payment, PaymentStatus
        from sqlalchemy import select
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        async with async_session_maker() as db:
            result = await db.execute(
                select(Payment).where(
                    Payment.status == PaymentStatus.PENDING,
                    Payment.created_at < cutoff_time
                )
            )
            
            pending_payments = result.scalars().all()
            
            processed = 0
            for payment in pending_payments:
                payment.status = PaymentStatus.FAILED
                payment.error_message = "Payment timeout"
                processed += 1
            
            await db.commit()
            
            return {"processed": processed}
    
    return run_async(_process())
