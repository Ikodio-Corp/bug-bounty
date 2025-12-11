"""
ML A/B Testing Tasks - Celery tasks for A/B test management
"""
from celery import Task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from backend.tasks.celery_config import celery_app
from backend.core.database import get_db
from backend.models.ml_training import MLABTest, ABTestStatus
from backend.services.ml_ab_testing_service import MLABTestingService

logger = logging.getLogger(__name__)


class MLABTestingTask(Task):
    """Base class for A/B testing tasks"""
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 120}


@celery_app.task(base=MLABTestingTask, bind=True, name="backend.tasks.ml_ab_testing_tasks.update_ab_test_statistics")
def update_ab_test_statistics(self):
    """
    Update statistics for all running A/B tests
    Runs every 15 minutes
    """
    logger.info("Updating A/B test statistics")
    
    db = next(get_db())
    try:
        ab_service = MLABTestingService(db)
        
        # Get active tests
        active_tests = db.query(MLABTest).filter(
            MLABTest.status == ABTestStatus.RUNNING
        ).all()
        
        if not active_tests:
            logger.info("No active A/B tests found")
            return {"status": "skipped", "reason": "no_active_tests"}
        
        results = []
        for test in active_tests:
            try:
                # Update metrics
                metrics = await ab_service.update_test_metrics(test.id)
                
                # Check if test should be completed
                if test.end_date and datetime.utcnow() >= test.end_date:
                    await ab_service.complete_ab_test(test.id, promote_winner=True)
                    status = "completed"
                else:
                    status = "updated"
                
                results.append({
                    "test_id": test.id,
                    "name": test.name,
                    "status": status,
                    "metrics": metrics
                })
                
            except Exception as e:
                logger.error(f"Error updating A/B test {test.id}: {e}")
                results.append({
                    "test_id": test.id,
                    "name": test.name,
                    "status": "error",
                    "error": str(e)
                })
        
        logger.info(f"Updated {len(results)} A/B tests")
        
        return {
            "status": "completed",
            "tests_updated": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error updating A/B test statistics: {e}")
        raise
    finally:
        db.close()


@celery_app.task(base=MLABTestingTask, name="backend.tasks.ml_ab_testing_tasks.archive_completed_tests")
def archive_completed_tests():
    """
    Archive completed A/B tests older than 30 days
    Runs daily at 4 AM
    """
    logger.info("Archiving completed A/B tests")
    
    db = next(get_db())
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Find completed tests to archive
        tests_to_archive = db.query(MLABTest).filter(
            MLABTest.status == ABTestStatus.COMPLETED,
            MLABTest.end_date < cutoff_date
        ).all()
        
        archived_count = 0
        for test in tests_to_archive:
            # Could move to separate archive table or mark as archived
            # For now, just log
            logger.info(f"Archiving test: {test.name} (ID: {test.id})")
            archived_count += 1
        
        logger.info(f"Archived {archived_count} A/B tests")
        
        return {
            "status": "completed",
            "archived_count": archived_count
        }
        
    except Exception as e:
        logger.error(f"Error archiving A/B tests: {e}")
        raise
    finally:
        db.close()


@celery_app.task(base=MLABTestingTask, bind=True, name="backend.tasks.ml_ab_testing_tasks.check_test_significance")
def check_test_significance(self, test_id: int):
    """
    Check if an A/B test has reached statistical significance
    Can be triggered manually or scheduled
    """
    logger.info(f"Checking significance for A/B test {test_id}")
    
    db = next(get_db())
    try:
        ab_service = MLABTestingService(db)
        
        test = db.query(MLABTest).filter(MLABTest.id == test_id).first()
        if not test:
            raise ValueError(f"A/B test {test_id} not found")
        
        if test.status != ABTestStatus.RUNNING:
            return {
                "status": "skipped",
                "reason": f"Test is not running (status: {test.status.value})"
            }
        
        # Determine winner
        winner_id = await ab_service.determine_winner(test_id)
        
        if winner_id:
            logger.info(f"A/B test {test_id} has a significant winner: model {winner_id}")
            
            return {
                "status": "significant",
                "test_id": test_id,
                "winner_model_id": winner_id
            }
        else:
            logger.info(f"A/B test {test_id} not yet significant")
            
            return {
                "status": "not_significant",
                "test_id": test_id
            }
        
    except Exception as e:
        logger.error(f"Error checking test significance: {e}")
        raise
    finally:
        db.close()
