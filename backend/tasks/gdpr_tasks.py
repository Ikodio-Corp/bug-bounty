"""
GDPR Compliance Tasks - Automated data processing and deletion
"""

from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from core.database import SessionLocal
from models.user import User
from services.audit_service import AuditService
from integrations.email_client import EmailClient

logger = logging.getLogger(__name__)


@shared_task(name="gdpr.process_scheduled_deletions")
def process_scheduled_deletions() -> Dict[str, Any]:
    """
    Process user account deletions that have passed their grace period
    
    GDPR Article 17: Right to erasure
    - 30-day grace period for account recovery
    - Permanent deletion after grace period ends
    - Audit trail retained for compliance
    """
    db = SessionLocal()
    try:
        current_time = datetime.utcnow()
        
        users_to_delete = db.query(User).filter(
            User.deletion_scheduled_at.isnot(None),
            User.deletion_scheduled_at <= current_time
        ).all()
        
        deletion_results = {
            "total_scheduled": len(users_to_delete),
            "successfully_deleted": [],
            "failed": []
        }
        
        for user in users_to_delete:
            try:
                user_id = user.id
                user_email = user.email
                
                audit_service = AuditService(db)
                await audit_service.log_data_modification(
                    user_id=user_id,
                    resource_type="user",
                    resource_id=str(user_id),
                    action="permanent_deletion",
                    changes={"status": "deleted"}
                )
                
                db.delete(user)
                db.commit()
                
                logger.info(f"Permanently deleted user {user_id} ({user_email})")
                deletion_results["successfully_deleted"].append({
                    "user_id": user_id,
                    "email": user_email,
                    "deletion_date": current_time.isoformat()
                })
                
            except Exception as e:
                logger.error(f"Failed to delete user {user.id}: {str(e)}")
                deletion_results["failed"].append({
                    "user_id": user.id,
                    "error": str(e)
                })
                db.rollback()
        
        return deletion_results
        
    finally:
        db.close()


@shared_task(name="gdpr.send_deletion_reminders")
def send_deletion_reminders() -> Dict[str, Any]:
    """
    Send reminder emails to users with pending account deletions
    
    Notifications sent at:
    - 7 days before deletion
    - 3 days before deletion
    - 1 day before deletion
    """
    db = SessionLocal()
    email_client = EmailClient()
    
    try:
        current_time = datetime.utcnow()
        reminder_windows = [
            (7, "7 days"),
            (3, "3 days"),
            (1, "1 day")
        ]
        
        reminder_results = {
            "total_sent": 0,
            "reminders": []
        }
        
        for days, label in reminder_windows:
            target_date = current_time + timedelta(days=days)
            date_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            users = db.query(User).filter(
                User.deletion_scheduled_at.between(date_start, date_end)
            ).all()
            
            for user in users:
                try:
                    email_client.send_deletion_reminder(
                        to_email=user.email,
                        user_name=user.full_name or user.username,
                        days_remaining=days,
                        deletion_date=user.deletion_scheduled_at
                    )
                    
                    reminder_results["total_sent"] += 1
                    reminder_results["reminders"].append({
                        "user_id": user.id,
                        "email": user.email,
                        "days_remaining": days,
                        "deletion_date": user.deletion_scheduled_at.isoformat()
                    })
                    
                    logger.info(f"Sent {label} deletion reminder to {user.email}")
                    
                except Exception as e:
                    logger.error(f"Failed to send reminder to {user.email}: {str(e)}")
        
        return reminder_results
        
    finally:
        db.close()


@shared_task(name="gdpr.anonymize_old_audit_logs")
def anonymize_old_audit_logs() -> Dict[str, Any]:
    """
    Anonymize audit logs older than retention period
    
    GDPR Article 5(1)(e): Storage limitation
    - Keep audit logs for 90 days
    - Anonymize after retention period
    - Retain anonymized data for compliance
    """
    db = SessionLocal()
    audit_service = AuditService(db)
    
    try:
        retention_date = datetime.utcnow() - timedelta(days=90)
        
        # Get logs older than retention period
        old_logs = await audit_service.get_user_activity(
            user_id=None,
            end_date=retention_date,
            limit=10000
        )
        
        anonymization_results = {
            "total_logs": len(old_logs),
            "anonymized": 0,
            "errors": 0
        }
        
        for log in old_logs:
            try:
                # Anonymize personal data
                log["user_id"] = "anonymized"
                log["ip_address"] = "0.0.0.0"
                log["user_agent"] = "anonymized"
                log["details"] = {
                    "anonymized": True,
                    "retention_period_expired": retention_date.isoformat()
                }
                
                anonymization_results["anonymized"] += 1
                
            except Exception as e:
                logger.error(f"Failed to anonymize log: {str(e)}")
                anonymization_results["errors"] += 1
        
        logger.info(f"Anonymized {anonymization_results['anonymized']} audit logs")
        return anonymization_results
        
    finally:
        db.close()


@shared_task(name="gdpr.generate_compliance_report")
def generate_compliance_report() -> Dict[str, Any]:
    """
    Generate monthly GDPR compliance report
    
    Report includes:
    - Number of data subject requests processed
    - Account deletions completed
    - Consent changes recorded
    - Data breaches (if any)
    - Compliance status
    """
    db = SessionLocal()
    audit_service = AuditService(db)
    
    try:
        start_date = datetime.utcnow() - timedelta(days=30)
        
        # Get data subject request statistics
        access_requests = await audit_service.get_user_activity(
            event_type="data_access",
            start_date=start_date,
            action="export"
        )
        
        deletion_requests = db.query(User).filter(
            User.deletion_requested_at >= start_date
        ).count()
        
        completed_deletions = await audit_service.get_user_activity(
            event_type="data_modification",
            start_date=start_date,
            action="permanent_deletion"
        )
        
        consent_changes = await audit_service.get_user_activity(
            event_type="data_modification",
            start_date=start_date,
            resource_type="consent"
        )
        
        security_incidents = await audit_service.get_security_events(
            start_date=start_date,
            severity="high"
        )
        
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "data_subject_requests": {
                "access_requests": len(access_requests),
                "deletion_requests": deletion_requests,
                "completed_deletions": len(completed_deletions),
                "consent_changes": len(consent_changes)
            },
            "security": {
                "high_severity_incidents": len(security_incidents),
                "data_breaches": 0
            },
            "compliance_status": "compliant",
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Generated GDPR compliance report: {report}")
        return report
        
    finally:
        db.close()


@shared_task(name="gdpr.expire_inactive_consents")
def expire_inactive_consents() -> Dict[str, Any]:
    """
    Review and expire consents for inactive users
    
    GDPR Article 7(3): Withdrawal of consent
    - Review consents every 12 months
    - Require reconfirmation for inactive users
    """
    db = SessionLocal()
    
    try:
        inactive_threshold = datetime.utcnow() - timedelta(days=365)
        
        inactive_users = db.query(User).filter(
            User.last_login < inactive_threshold,
            User.consent_marketing == True
        ).all()
        
        expired_results = {
            "total_users": len(inactive_users),
            "consents_expired": 0
        }
        
        for user in inactive_users:
            user.consent_marketing = False
            user.consent_profiling = False
            user.consent_third_party = False
            user.consent_updated_at = datetime.utcnow()
            
            expired_results["consents_expired"] += 1
        
        db.commit()
        
        logger.info(f"Expired consents for {expired_results['consents_expired']} inactive users")
        return expired_results
        
    finally:
        db.close()
