"""
Celery configuration and app
"""

from celery import Celery
from celery.schedules import crontab

from core.config import settings

# Create Celery app
celery_app = Celery(
    "ikodio_bugbounty",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task routing
celery_app.conf.task_routes = {
    "tasks.scan_tasks.*": {"queue": "scanner"},
    "tasks.ai_tasks.*": {"queue": "ai"},
    "tasks.notification_tasks.*": {"queue": "general"},
}

# Periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-old-scans": {
        "task": "tasks.maintenance_tasks.cleanup_old_scans",
        "schedule": crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
    "update-security-scores": {
        "task": "tasks.intelligence_tasks.update_all_security_scores",
        "schedule": crontab(hour=0, minute=0),  # Run at midnight
    },
    "process-guild-contributions": {
        "task": "tasks.guild_tasks.process_contributions",
        "schedule": crontab(hour=1, minute=0),  # Run at 1 AM daily
    },
    "process-scheduled-deletions": {
        "task": "gdpr.process_scheduled_deletions",
        "schedule": crontab(hour=3, minute=0),  # Run at 3 AM daily
    },
    "send-deletion-reminders": {
        "task": "gdpr.send_deletion_reminders",
        "schedule": crontab(hour=10, minute=0),  # Run at 10 AM daily
    },
    "anonymize-old-audit-logs": {
        "task": "gdpr.anonymize_old_audit_logs",
        "schedule": crontab(hour=4, minute=0),  # Run at 4 AM daily
    },
    "generate-compliance-report": {
        "task": "gdpr.generate_compliance_report",
        "schedule": crontab(day_of_month=1, hour=6, minute=0),  # First day of month at 6 AM
    },
    "expire-inactive-consents": {
        "task": "gdpr.expire_inactive_consents",
        "schedule": crontab(day_of_week=0, hour=5, minute=0),  # Sunday at 5 AM
    },
}

# Import tasks to register them
from tasks import scan_tasks, ai_tasks, notification_tasks, maintenance_tasks, gdpr_tasks

# Register tasks
celery_app.task(scan_tasks.execute_scan, name="tasks.scan_tasks.execute_scan")
celery_app.task(scan_tasks.generate_ai_report, name="tasks.scan_tasks.generate_ai_report")
celery_app.task(scan_tasks.analyze_exploit_chain, name="tasks.scan_tasks.analyze_exploit_chain")
celery_app.task(scan_tasks.process_payment, name="tasks.scan_tasks.process_payment")
celery_app.task(scan_tasks.send_notification_email, name="tasks.scan_tasks.send_notification_email")
