"""
ML Monitoring Tasks - Performance monitoring and alerting
"""
from celery import Task
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import numpy as np

from backend.tasks.celery_config import celery_app
from backend.core.database import get_db
from backend.integrations.ml_client import ml_client
from backend.models.ml_training import (
    MLModelMonitoring,
    MLModelVersion,
    MLModelRollback,
    ModelVersionStatus
)
from backend.models.ml_feedback import MLPredictionFeedback
from backend.models.bug import Bug, Scan

logger = logging.getLogger(__name__)


class MLMonitoringTask(Task):
    """Base class for ML monitoring tasks"""
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 60}
    retry_backoff = True


@celery_app.task(base=MLMonitoringTask, bind=True, name="backend.tasks.ml_monitoring_tasks.monitor_model_performance")
def monitor_model_performance(self):
    """
    Monitor model performance in real-time
    Runs every 30 minutes
    """
    logger.info("Starting model performance monitoring")
    
    db = next(get_db())
    try:
        # Get production models
        production_models = db.query(MLModelVersion).filter(
            MLModelVersion.is_production == True
        ).all()
        
        if not production_models:
            logger.warning("No production models found")
            return {"status": "skipped", "reason": "no_production_models"}
        
        results = []
        for model in production_models:
            monitoring_data = _collect_monitoring_data(db, model.id, window_minutes=30)
            
            if monitoring_data:
                # Create monitoring record
                monitoring = MLModelMonitoring(
                    model_version_id=model.id,
                    window_start=monitoring_data["window_start"],
                    window_end=monitoring_data["window_end"],
                    window_size_minutes=30,
                    predictions_count=monitoring_data["predictions_count"],
                    accuracy=monitoring_data.get("accuracy"),
                    precision=monitoring_data.get("precision"),
                    recall=monitoring_data.get("recall"),
                    f1_score=monitoring_data.get("f1_score"),
                    avg_latency_ms=monitoring_data.get("avg_latency_ms"),
                    p50_latency_ms=monitoring_data.get("p50_latency_ms"),
                    p95_latency_ms=monitoring_data.get("p95_latency_ms"),
                    p99_latency_ms=monitoring_data.get("p99_latency_ms"),
                    error_count=monitoring_data.get("error_count", 0),
                    error_rate=monitoring_data.get("error_rate", 0.0),
                    data_drift_score=monitoring_data.get("data_drift_score"),
                    concept_drift_score=monitoring_data.get("concept_drift_score")
                )
                
                # Check for alerts
                alert = _check_for_alerts(monitoring_data, model)
                if alert:
                    monitoring.alert_triggered = True
                    monitoring.alert_type = alert["type"]
                    monitoring.alert_message = alert["message"]
                    logger.warning(f"Alert triggered for model {model.id}: {alert['message']}")
                
                db.add(monitoring)
                results.append({
                    "model_version_id": model.id,
                    "model_type": model.model_type,
                    "metrics": monitoring_data,
                    "alert": alert
                })
        
        db.commit()
        
        logger.info(f"Monitoring completed for {len(results)} models")
        
        return {
            "status": "completed",
            "models_monitored": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in performance monitoring: {e}")
        raise
    finally:
        db.close()


@celery_app.task(base=MLMonitoringTask, bind=True, name="backend.tasks.ml_monitoring_tasks.check_rollback_conditions")
def check_rollback_conditions(self):
    """
    Check if any models need to be rolled back due to performance issues
    Runs every 10 minutes
    """
    logger.info("Checking rollback conditions")
    
    db = next(get_db())
    try:
        production_models = db.query(MLModelVersion).filter(
            MLModelVersion.is_production == True
        ).all()
        
        rollbacks = []
        for model in production_models:
            # Get recent monitoring data (last 30 minutes)
            recent_monitoring = db.query(MLModelMonitoring).filter(
                MLModelMonitoring.model_version_id == model.id,
                MLModelMonitoring.window_start >= datetime.utcnow() - timedelta(minutes=30)
            ).all()
            
            if not recent_monitoring:
                continue
            
            # Check for rollback conditions
            should_rollback, reason, metrics = _should_rollback_model(recent_monitoring, model)
            
            if should_rollback:
                # Find previous production model to rollback to
                previous_model = db.query(MLModelVersion).filter(
                    MLModelVersion.model_type == model.model_type,
                    MLModelVersion.id != model.id,
                    MLModelVersion.status == ModelVersionStatus.PRODUCTION
                ).order_by(MLModelVersion.deployed_at.desc()).first()
                
                if not previous_model:
                    # Find last successful model
                    previous_model = db.query(MLModelVersion).filter(
                        MLModelVersion.model_type == model.model_type,
                        MLModelVersion.id != model.id,
                        MLModelVersion.status == ModelVersionStatus.TRAINED
                    ).order_by(MLModelVersion.created_at.desc()).first()
                
                if previous_model:
                    # Perform rollback
                    rollback = perform_rollback.delay(
                        from_version_id=model.id,
                        to_version_id=previous_model.id,
                        reason=reason,
                        metrics=metrics
                    )
                    
                    rollbacks.append({
                        "from_version": model.id,
                        "to_version": previous_model.id,
                        "reason": reason,
                        "task_id": rollback.id
                    })
                    
                    logger.warning(f"Initiated rollback from model {model.id} to {previous_model.id}: {reason}")
        
        return {
            "status": "completed",
            "rollbacks_initiated": len(rollbacks),
            "rollbacks": rollbacks
        }
        
    except Exception as e:
        logger.error(f"Error checking rollback conditions: {e}")
        raise
    finally:
        db.close()


@celery_app.task(base=MLMonitoringTask, bind=True, name="backend.tasks.ml_monitoring_tasks.perform_rollback")
def perform_rollback(
    self,
    from_version_id: int,
    to_version_id: int,
    reason: str,
    metrics: Dict[str, Any],
    user_id: Optional[int] = None
):
    """
    Perform model rollback
    
    Args:
        from_version_id: Model version to rollback from
        to_version_id: Model version to rollback to
        reason: Reason for rollback
        metrics: Metrics that triggered rollback
        user_id: User ID if manual rollback
    """
    logger.info(f"Performing rollback from version {from_version_id} to {to_version_id}")
    
    db = next(get_db())
    try:
        from_model = db.query(MLModelVersion).filter(
            MLModelVersion.id == from_version_id
        ).first()
        to_model = db.query(MLModelVersion).filter(
            MLModelVersion.id == to_version_id
        ).first()
        
        if not from_model or not to_model:
            raise ValueError("Invalid model version IDs")
        
        # Demote current model
        from_model.is_production = False
        from_model.status = ModelVersionStatus.ARCHIVED
        
        # Promote rollback target
        to_model.is_production = True
        to_model.status = ModelVersionStatus.PRODUCTION
        to_model.deployed_at = datetime.utcnow()
        
        # Record rollback
        rollback = MLModelRollback(
            from_version_id=from_version_id,
            to_version_id=to_version_id,
            reason=reason,
            trigger="automatic" if not user_id else "manual",
            trigger_metrics=metrics,
            rolled_back_at=datetime.utcnow(),
            triggered_by_user_id=user_id,
            description=f"Rollback from v{from_model.version} to v{to_model.version}: {reason}"
        )
        
        db.add(rollback)
        db.commit()
        
        # Notify ML engine about rollback
        try:
            ml_client.set_production_model(
                model_type=to_model.model_type,
                version_id=to_model.id
            )
        except Exception as e:
            logger.error(f"Error notifying ML engine about rollback: {e}")
        
        logger.info(f"Rollback completed: {from_model.version} -> {to_model.version}")
        
        return {
            "status": "completed",
            "from_version": from_model.version,
            "to_version": to_model.version,
            "rollback_id": rollback.id
        }
        
    except Exception as e:
        logger.error(f"Error performing rollback: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(base=MLMonitoringTask, name="backend.tasks.ml_monitoring_tasks.generate_daily_performance_report")
def generate_daily_performance_report():
    """
    Generate daily performance report for all production models
    Runs at 6 AM daily
    """
    logger.info("Generating daily performance report")
    
    db = next(get_db())
    try:
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        production_models = db.query(MLModelVersion).filter(
            MLModelVersion.is_production == True
        ).all()
        
        report = {
            "date": yesterday.date().isoformat(),
            "models": []
        }
        
        for model in production_models:
            # Get all monitoring data from yesterday
            monitoring_data = db.query(MLModelMonitoring).filter(
                MLModelMonitoring.model_version_id == model.id,
                MLModelMonitoring.window_start >= yesterday,
                MLModelMonitoring.window_start < datetime.utcnow()
            ).all()
            
            if not monitoring_data:
                continue
            
            # Aggregate metrics
            model_report = {
                "model_version_id": model.id,
                "model_type": model.model_type,
                "version": model.version,
                "total_predictions": sum(m.predictions_count for m in monitoring_data),
                "avg_accuracy": np.mean([m.accuracy for m in monitoring_data if m.accuracy]),
                "avg_latency_ms": np.mean([m.avg_latency_ms for m in monitoring_data if m.avg_latency_ms]),
                "p95_latency_ms": np.percentile([m.p95_latency_ms for m in monitoring_data if m.p95_latency_ms], 95) if any(m.p95_latency_ms for m in monitoring_data) else None,
                "total_errors": sum(m.error_count for m in monitoring_data),
                "error_rate": np.mean([m.error_rate for m in monitoring_data if m.error_rate]),
                "alerts_triggered": sum(1 for m in monitoring_data if m.alert_triggered),
                "monitoring_windows": len(monitoring_data)
            }
            
            report["models"].append(model_report)
        
        logger.info(f"Daily report generated for {len(report['models'])} models")
        
        # Store report (could be sent via email, stored in database, etc.)
        return report
        
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        raise
    finally:
        db.close()


def _collect_monitoring_data(db: Session, model_version_id: int, window_minutes: int = 30) -> Dict[str, Any]:
    """Collect monitoring data for a model version"""
    window_start = datetime.utcnow() - timedelta(minutes=window_minutes)
    window_end = datetime.utcnow()
    
    # Get predictions made in this window
    predictions = db.query(MLPredictionFeedback).filter(
        MLPredictionFeedback.feedback_submitted_at >= window_start,
        MLPredictionFeedback.feedback_submitted_at < window_end
    ).all()
    
    if not predictions:
        return None
    
    # Calculate metrics
    correct_predictions = sum(1 for p in predictions if p.is_correct)
    total_with_feedback = len([p for p in predictions if p.is_correct is not None])
    
    accuracy = correct_predictions / total_with_feedback if total_with_feedback > 0 else None
    
    # Calculate latency metrics (mock data - would come from actual prediction logs)
    latencies = [np.random.randint(10, 200) for _ in predictions]  # Replace with actual latency data
    
    return {
        "window_start": window_start,
        "window_end": window_end,
        "predictions_count": len(predictions),
        "accuracy": accuracy,
        "precision": None,  # Would need more detailed data
        "recall": None,
        "f1_score": None,
        "avg_latency_ms": np.mean(latencies) if latencies else None,
        "p50_latency_ms": np.percentile(latencies, 50) if latencies else None,
        "p95_latency_ms": np.percentile(latencies, 95) if latencies else None,
        "p99_latency_ms": np.percentile(latencies, 99) if latencies else None,
        "error_count": 0,
        "error_rate": 0.0,
        "data_drift_score": None,
        "concept_drift_score": None
    }


def _check_for_alerts(monitoring_data: Dict[str, Any], model: MLModelVersion) -> Optional[Dict[str, str]]:
    """Check if monitoring data triggers any alerts"""
    
    # Accuracy drop alert
    if monitoring_data.get("accuracy") is not None:
        baseline_accuracy = model.metrics.get("accuracy", 0.8) if model.metrics else 0.8
        if monitoring_data["accuracy"] < baseline_accuracy * 0.9:  # 10% drop
            return {
                "type": "accuracy_drop",
                "message": f"Accuracy dropped to {monitoring_data['accuracy']:.4f} (baseline: {baseline_accuracy:.4f})"
            }
    
    # High latency alert
    if monitoring_data.get("p95_latency_ms") is not None:
        if monitoring_data["p95_latency_ms"] > 500:  # 500ms threshold
            return {
                "type": "high_latency",
                "message": f"P95 latency: {monitoring_data['p95_latency_ms']:.2f}ms exceeds 500ms threshold"
            }
    
    # High error rate alert
    if monitoring_data.get("error_rate") is not None:
        if monitoring_data["error_rate"] > 0.05:  # 5% error rate
            return {
                "type": "high_error_rate",
                "message": f"Error rate: {monitoring_data['error_rate']:.2%} exceeds 5% threshold"
            }
    
    return None


def _should_rollback_model(
    monitoring_data: List[MLModelMonitoring],
    model: MLModelVersion
) -> tuple[bool, str, Dict[str, Any]]:
    """Determine if a model should be rolled back"""
    
    if len(monitoring_data) < 3:
        return False, "", {}
    
    # Check for consistent accuracy drop
    accuracies = [m.accuracy for m in monitoring_data if m.accuracy is not None]
    if accuracies:
        avg_accuracy = np.mean(accuracies)
        baseline_accuracy = model.metrics.get("accuracy", 0.8) if model.metrics else 0.8
        
        if avg_accuracy < baseline_accuracy * 0.85:  # 15% drop triggers rollback
            return True, "accuracy_drop", {
                "current_accuracy": avg_accuracy,
                "baseline_accuracy": baseline_accuracy,
                "drop_percentage": (baseline_accuracy - avg_accuracy) / baseline_accuracy
            }
    
    # Check for high latency
    p95_latencies = [m.p95_latency_ms for m in monitoring_data if m.p95_latency_ms is not None]
    if p95_latencies:
        avg_p95_latency = np.mean(p95_latencies)
        if avg_p95_latency > 1000:  # 1 second
            return True, "high_latency", {
                "p95_latency_ms": avg_p95_latency
            }
    
    # Check for high error rate
    error_rates = [m.error_rate for m in monitoring_data if m.error_rate is not None]
    if error_rates:
        avg_error_rate = np.mean(error_rates)
        if avg_error_rate > 0.1:  # 10% error rate
            return True, "high_error_rate", {
                "error_rate": avg_error_rate
            }
    
    return False, "", {}
