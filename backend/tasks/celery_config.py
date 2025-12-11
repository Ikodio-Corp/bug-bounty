"""
Celery Configuration for ML Auto-Training and Scheduled Tasks
"""
from celery import Celery
from celery.schedules import crontab
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "ml_training",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "backend.tasks.ml_training_tasks",
        "backend.tasks.ml_monitoring_tasks",
        "backend.tasks.ml_ab_testing_tasks"
    ]
)

# Celery Configuration
celery_app.conf.update(
    # Task execution settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "backend.tasks.ml_training_tasks.*": {"queue": "ml_training"},
        "backend.tasks.ml_monitoring_tasks.*": {"queue": "ml_monitoring"},
        "backend.tasks.ml_ab_testing_tasks.*": {"queue": "ml_ab_testing"},
    },
    
    # Task time limits
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3000,  # 50 minutes soft limit
    
    # Task retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=86400,  # 24 hours
    result_persistent=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        # Retrain models daily at 2 AM
        "retrain-models-daily": {
            "task": "backend.tasks.ml_training_tasks.scheduled_model_retraining",
            "schedule": crontab(hour=2, minute=0),
            "options": {"queue": "ml_training"}
        },
        
        # Process feedback for incremental learning every hour
        "incremental-learning-hourly": {
            "task": "backend.tasks.ml_training_tasks.process_feedback_incremental",
            "schedule": crontab(minute=0),
            "options": {"queue": "ml_training"}
        },
        
        # Check model performance every 30 minutes
        "monitor-model-performance": {
            "task": "backend.tasks.ml_monitoring_tasks.monitor_model_performance",
            "schedule": crontab(minute="*/30"),
            "options": {"queue": "ml_monitoring"}
        },
        
        # Update A/B test statistics every 15 minutes
        "update-ab-test-stats": {
            "task": "backend.tasks.ml_ab_testing_tasks.update_ab_test_statistics",
            "schedule": crontab(minute="*/15"),
            "options": {"queue": "ml_ab_testing"}
        },
        
        # Check for model rollback conditions every 10 minutes
        "check-rollback-conditions": {
            "task": "backend.tasks.ml_monitoring_tasks.check_rollback_conditions",
            "schedule": crontab(minute="*/10"),
            "options": {"queue": "ml_monitoring"}
        },
        
        # Cleanup old training data weekly
        "cleanup-training-data": {
            "task": "backend.tasks.ml_training_tasks.cleanup_old_training_data",
            "schedule": crontab(day_of_week=0, hour=3, minute=0),
            "options": {"queue": "ml_training"}
        },
        
        # Archive completed A/B tests daily
        "archive-completed-tests": {
            "task": "backend.tasks.ml_ab_testing_tasks.archive_completed_tests",
            "schedule": crontab(hour=4, minute=0),
            "options": {"queue": "ml_ab_testing"}
        },
        
        # Generate daily performance reports
        "generate-daily-reports": {
            "task": "backend.tasks.ml_monitoring_tasks.generate_daily_performance_report",
            "schedule": crontab(hour=6, minute=0),
            "options": {"queue": "ml_monitoring"}
        },
    },
)

# Task annotations for better monitoring
celery_app.conf.task_annotations = {
    "*": {
        "rate_limit": "10/m",
        "time_limit": 3600,
        "soft_time_limit": 3000,
    },
    "backend.tasks.ml_training_tasks.train_model": {
        "rate_limit": "3/h",  # Limit model training to 3 per hour
        "time_limit": 7200,  # 2 hours for training
        "soft_time_limit": 6600,
    },
    "backend.tasks.ml_training_tasks.scheduled_model_retraining": {
        "rate_limit": "1/d",  # Once per day
        "time_limit": 7200,
    },
}

# Error handling
@celery_app.task(bind=True, max_retries=3)
def debug_task(self):
    """Debug task for testing Celery setup"""
    logger.info(f"Request: {self.request!r}")
    return "Celery is working!"


class CeleryTaskMetrics:
    """Track Celery task metrics for monitoring"""
    
    @staticmethod
    def on_task_prerun(sender=None, task_id=None, task=None, **kwargs):
        """Called before task execution"""
        logger.info(f"Task {task.name} [{task_id}] starting")
    
    @staticmethod
    def on_task_postrun(sender=None, task_id=None, task=None, state=None, **kwargs):
        """Called after task execution"""
        logger.info(f"Task {task.name} [{task_id}] completed with state: {state}")
    
    @staticmethod
    def on_task_failure(sender=None, task_id=None, exception=None, **kwargs):
        """Called when task fails"""
        logger.error(f"Task {sender.name} [{task_id}] failed: {exception}")
    
    @staticmethod
    def on_task_retry(sender=None, task_id=None, reason=None, **kwargs):
        """Called when task is retried"""
        logger.warning(f"Task {sender.name} [{task_id}] retrying: {reason}")


# Register signal handlers
from celery.signals import (
    task_prerun, 
    task_postrun, 
    task_failure, 
    task_retry
)

task_prerun.connect(CeleryTaskMetrics.on_task_prerun)
task_postrun.connect(CeleryTaskMetrics.on_task_postrun)
task_failure.connect(CeleryTaskMetrics.on_task_failure)
task_retry.connect(CeleryTaskMetrics.on_task_retry)


# Task result cache settings
celery_app.conf.result_cache_max = 1000


def get_celery_app():
    """Get Celery app instance"""
    return celery_app
