"""
ML Training Tasks - Celery tasks for automated model training and retraining
"""
from celery import Task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import numpy as np
from backend.tasks.celery_config import celery_app
from backend.core.database import get_db
from backend.integrations.ml_client import ml_client
from backend.models.ml_feedback import (
    MLPredictionFeedback,
    MLModelPerformance,
    MLTrainingJob,
    MLModelVersion
)
from backend.models.bug import Bug, Scan

logger = logging.getLogger(__name__)


class MLTrainingTask(Task):
    """Base class for ML training tasks with error handling"""
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 300}
    retry_backoff = True
    retry_jitter = True


@celery_app.task(base=MLTrainingTask, bind=True, name="backend.tasks.ml_training_tasks.scheduled_model_retraining")
def scheduled_model_retraining(self):
    """
    Scheduled task to retrain models daily with accumulated feedback
    Runs at 2 AM daily
    """
    logger.info("Starting scheduled model retraining")
    
    db = next(get_db())
    try:
        # Get all feedback since last training
        last_training = db.query(MLTrainingJob).filter(
            MLTrainingJob.status == "completed"
        ).order_by(MLTrainingJob.completed_at.desc()).first()
        
        since_date = last_training.completed_at if last_training else datetime.utcnow() - timedelta(days=7)
        
        feedback_count = db.query(MLPredictionFeedback).filter(
            MLPredictionFeedback.feedback_submitted_at >= since_date
        ).count()
        
        if feedback_count < 50:
            logger.info(f"Not enough feedback for retraining: {feedback_count} items")
            return {
                "status": "skipped",
                "reason": "insufficient_feedback",
                "feedback_count": feedback_count
            }
        
        # Create training job
        training_job = MLTrainingJob(
            job_type="scheduled_retraining",
            model_type="rule_based",
            training_data_count=feedback_count,
            status="running",
            started_at=datetime.utcnow(),
            config={
                "since_date": since_date.isoformat(),
                "feedback_count": feedback_count,
                "training_type": "full_retraining"
            }
        )
        db.add(training_job)
        db.commit()
        
        # Trigger training via ML client
        result = train_model.delay(
            model_type="rule_based",
            training_job_id=training_job.id,
            include_feedback_since=since_date.isoformat()
        )
        
        training_job.celery_task_id = result.id
        db.commit()
        
        logger.info(f"Scheduled retraining started: job_id={training_job.id}, task_id={result.id}")
        
        return {
            "status": "started",
            "training_job_id": training_job.id,
            "task_id": result.id,
            "feedback_count": feedback_count
        }
        
    except Exception as e:
        logger.error(f"Error in scheduled retraining: {e}")
        raise
    finally:
        db.close()


@celery_app.task(base=MLTrainingTask, bind=True, name="backend.tasks.ml_training_tasks.process_feedback_incremental")
def process_feedback_incremental(self):
    """
    Process new feedback for incremental learning
    Runs hourly
    """
    logger.info("Starting incremental learning from feedback")
    
    db = next(get_db())
    try:
        # Get unprocessed feedback
        unprocessed_feedback = db.query(MLPredictionFeedback).filter(
            MLPredictionFeedback.used_for_training == False,
            MLPredictionFeedback.feedback_submitted_at >= datetime.utcnow() - timedelta(hours=1)
        ).all()
        
        if len(unprocessed_feedback) < 10:
            logger.info(f"Not enough feedback for incremental learning: {len(unprocessed_feedback)} items")
            return {
                "status": "skipped",
                "feedback_count": len(unprocessed_feedback)
            }
        
        # Prepare feedback data for ML engine
        feedback_data = []
        for feedback in unprocessed_feedback:
            bug = db.query(Bug).filter(Bug.id == feedback.bug_id).first()
            if bug:
                feedback_data.append({
                    "prediction_id": feedback.prediction_id,
                    "features": _extract_bug_features(bug),
                    "actual_label": feedback.actual_vulnerability,
                    "confidence": feedback.confidence_score,
                    "is_correct": feedback.is_correct
                })
        
        # Send to ML engine for incremental learning
        try:
            result = ml_client.incremental_learning(
                model_type="rule_based",
                feedback_data=feedback_data
            )
            
            # Mark feedback as processed
            for feedback in unprocessed_feedback:
                feedback.used_for_training = True
                feedback.training_processed_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Incremental learning completed: {len(feedback_data)} samples processed")
            
            return {
                "status": "completed",
                "feedback_processed": len(feedback_data),
                "model_updated": result.get("model_updated", False)
            }
            
        except Exception as e:
            logger.error(f"Error in incremental learning: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
        
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise
    finally:
        db.close()


@celery_app.task(base=MLTrainingTask, bind=True, name="backend.tasks.ml_training_tasks.train_model")
def train_model(
    self,
    model_type: str,
    training_job_id: int,
    include_feedback_since: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
):
    """
    Train a new model version
    
    Args:
        model_type: Type of model to train
        training_job_id: Database ID of training job
        include_feedback_since: ISO datetime string for feedback cutoff
        config: Additional training configuration
    """
    logger.info(f"Starting model training: type={model_type}, job_id={training_job_id}")
    
    db = next(get_db())
    try:
        training_job = db.query(MLTrainingJob).filter(
            MLTrainingJob.id == training_job_id
        ).first()
        
        if not training_job:
            raise ValueError(f"Training job {training_job_id} not found")
        
        # Collect training data
        training_data = _collect_training_data(db, include_feedback_since)
        
        training_job.training_data_count = len(training_data)
        training_job.status = "training"
        db.commit()
        
        # Train model via ML engine
        try:
            training_result = ml_client.train_model(
                model_type=model_type,
                training_data=training_data,
                config=config or {}
            )
            
            # Create new model version
            model_version = MLModelVersion(
                model_type=model_type,
                version=training_result["version"],
                training_job_id=training_job_id,
                training_samples=len(training_data),
                training_duration_seconds=training_result.get("training_time", 0),
                metrics=training_result.get("metrics", {}),
                model_path=training_result.get("model_path"),
                config=config or {},
                status="trained",
                created_at=datetime.utcnow()
            )
            db.add(model_version)
            
            # Update training job
            training_job.status = "completed"
            training_job.completed_at = datetime.utcnow()
            training_job.result = {
                "model_version_id": model_version.id,
                "metrics": training_result.get("metrics", {}),
                "training_time": training_result.get("training_time", 0)
            }
            
            db.commit()
            
            logger.info(f"Model training completed: job_id={training_job_id}, version={model_version.version}")
            
            return {
                "status": "completed",
                "training_job_id": training_job_id,
                "model_version_id": model_version.id,
                "version": model_version.version,
                "metrics": training_result.get("metrics", {})
            }
            
        except Exception as e:
            training_job.status = "failed"
            training_job.error_message = str(e)
            training_job.completed_at = datetime.utcnow()
            db.commit()
            raise
        
    except Exception as e:
        logger.error(f"Error in model training: {e}")
        raise
    finally:
        db.close()


@celery_app.task(base=MLTrainingTask, name="backend.tasks.ml_training_tasks.cleanup_old_training_data")
def cleanup_old_training_data():
    """
    Cleanup old training data and logs
    Runs weekly on Sunday at 3 AM
    """
    logger.info("Starting cleanup of old training data")
    
    db = next(get_db())
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # Delete old training jobs
        deleted_jobs = db.query(MLTrainingJob).filter(
            MLTrainingJob.completed_at < cutoff_date,
            MLTrainingJob.status.in_(["completed", "failed"])
        ).delete()
        
        # Archive old model versions (keep production models)
        archived_versions = db.query(MLModelVersion).filter(
            MLModelVersion.created_at < cutoff_date,
            MLModelVersion.is_production == False
        ).update({"status": "archived"})
        
        db.commit()
        
        logger.info(f"Cleanup completed: jobs={deleted_jobs}, versions={archived_versions}")
        
        return {
            "status": "completed",
            "deleted_jobs": deleted_jobs,
            "archived_versions": archived_versions
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def _collect_training_data(db: Session, since_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Collect training data from bugs and feedback"""
    query = db.query(Bug).filter(Bug.status != "draft")
    
    if since_date:
        cutoff = datetime.fromisoformat(since_date)
        query = query.filter(Bug.created_at >= cutoff)
    
    bugs = query.all()
    
    training_data = []
    for bug in bugs:
        features = _extract_bug_features(bug)
        training_data.append({
            "bug_id": bug.id,
            "features": features,
            "label": bug.verified,
            "severity": bug.severity,
            "type": bug.vulnerability_type
        })
    
    return training_data


def _extract_bug_features(bug: Bug) -> Dict[str, Any]:
    """Extract features from bug for ML training"""
    return {
        "title_length": len(bug.title) if bug.title else 0,
        "description_length": len(bug.description) if bug.description else 0,
        "has_poc": bool(bug.proof_of_concept),
        "severity": bug.severity or 0,
        "vulnerability_type": bug.vulnerability_type or "unknown",
        "status": bug.status,
        "has_attachment": bool(bug.attachment_url),
        "bounty_amount": float(bug.bounty_amount) if bug.bounty_amount else 0.0
    }
