"""
ML Training and Auto-Learning API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from backend.core.database import get_db
from backend.core.security import get_current_user, require_admin
from backend.models.user import User
from backend.models.ml_training import (
    MLTrainingJob,
    MLModelVersion,
    MLABTest,
    MLModelMonitoring,
    MLModelRollback,
    TrainingJobStatus,
    ModelVersionStatus,
    ABTestStatus
)
from backend.services.ml_ab_testing_service import MLABTestingService
from backend.services.training_pipeline_orchestrator import TrainingPipelineOrchestrator
from backend.tasks.ml_training_tasks import train_model, scheduled_model_retraining
from backend.tasks.ml_monitoring_tasks import perform_rollback

router = APIRouter(prefix="/ml/training", tags=["ML Training"])


# Request/Response Schemas
class TrainingJobCreate(BaseModel):
    model_type: str = Field(..., description="Type of model to train")
    trigger: str = Field(default="manual", description="What triggered training")
    config: Optional[dict] = Field(default=None, description="Training configuration")


class TrainingJobResponse(BaseModel):
    id: int
    job_type: str
    model_type: str
    status: str
    training_data_count: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    result: Optional[dict]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class ModelVersionResponse(BaseModel):
    id: int
    model_type: str
    version: str
    status: str
    is_production: bool
    training_samples: Optional[int]
    metrics: Optional[dict]
    deployed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ABTestCreate(BaseModel):
    name: str = Field(..., description="Test name")
    description: str = Field(..., description="Test description")
    model_a_version_id: int = Field(..., description="Control model version ID")
    model_b_version_id: int = Field(..., description="Experiment model version ID")
    traffic_split_percentage: float = Field(default=50.0, ge=0, le=100)
    duration_days: int = Field(default=7, ge=1, le=90)


class ABTestResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    model_a_version_id: int
    model_b_version_id: int
    traffic_split_percentage: float
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    model_a_predictions: int
    model_b_predictions: int
    winner_model_version_id: Optional[int]
    
    class Config:
        from_attributes = True


class ModelRollbackRequest(BaseModel):
    from_version_id: int = Field(..., description="Version to rollback from")
    to_version_id: int = Field(..., description="Version to rollback to")
    reason: str = Field(..., description="Reason for rollback")


# Training Job Endpoints
@router.post("/jobs", response_model=TrainingJobResponse, status_code=status.HTTP_201_CREATED)
async def create_training_job(
    job_data: TrainingJobCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create and start a new model training job
    Admin only
    """
    # Create training job
    training_job = MLTrainingJob(
        job_type=job_data.trigger,
        model_type=job_data.model_type,
        status=TrainingJobStatus.PENDING,
        config=job_data.config or {},
        triggered_by_user_id=current_user.id,
        created_at=datetime.utcnow()
    )
    
    db.add(training_job)
    db.commit()
    db.refresh(training_job)
    
    # Start training in background
    task = train_model.delay(
        model_type=job_data.model_type,
        training_job_id=training_job.id,
        config=job_data.config
    )
    
    training_job.celery_task_id = task.id
    training_job.status = TrainingJobStatus.RUNNING
    training_job.started_at = datetime.utcnow()
    db.commit()
    
    return training_job


@router.get("/jobs", response_model=List[TrainingJobResponse])
async def list_training_jobs(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    model_type: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List training jobs with filtering
    Admin only
    """
    query = db.query(MLTrainingJob).order_by(MLTrainingJob.created_at.desc())
    
    if status:
        query = query.filter(MLTrainingJob.status == status)
    
    if model_type:
        query = query.filter(MLTrainingJob.model_type == model_type)
    
    jobs = query.offset(skip).limit(limit).all()
    
    return jobs


@router.get("/jobs/{job_id}", response_model=TrainingJobResponse)
async def get_training_job(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get training job details
    Admin only
    """
    job = db.query(MLTrainingJob).filter(MLTrainingJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training job {job_id} not found"
        )
    
    return job


@router.post("/jobs/scheduled-retrain", status_code=status.HTTP_202_ACCEPTED)
async def trigger_scheduled_retraining(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Manually trigger scheduled retraining
    Admin only
    """
    task = scheduled_model_retraining.delay()
    
    return {
        "message": "Scheduled retraining triggered",
        "task_id": task.id
    }


# Model Version Endpoints
@router.get("/models", response_model=List[ModelVersionResponse])
async def list_model_versions(
    skip: int = 0,
    limit: int = 50,
    model_type: Optional[str] = None,
    production_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List model versions"""
    query = db.query(MLModelVersion).order_by(MLModelVersion.created_at.desc())
    
    if model_type:
        query = query.filter(MLModelVersion.model_type == model_type)
    
    if production_only:
        query = query.filter(MLModelVersion.is_production == True)
    
    models = query.offset(skip).limit(limit).all()
    
    return models


@router.get("/models/{version_id}", response_model=ModelVersionResponse)
async def get_model_version(
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get model version details"""
    model = db.query(MLModelVersion).filter(MLModelVersion.id == version_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model version {version_id} not found"
        )
    
    return model


@router.post("/models/{version_id}/promote", response_model=ModelVersionResponse)
async def promote_to_production(
    version_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Promote a model version to production
    Admin only
    """
    model = db.query(MLModelVersion).filter(MLModelVersion.id == version_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model version {version_id} not found"
        )
    
    if model.status != ModelVersionStatus.TRAINED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only trained models can be promoted to production"
        )
    
    # Demote current production model
    current_production = db.query(MLModelVersion).filter(
        MLModelVersion.model_type == model.model_type,
        MLModelVersion.is_production == True
    ).first()
    
    if current_production:
        current_production.is_production = False
        current_production.status = ModelVersionStatus.ARCHIVED
    
    # Promote new model
    model.is_production = True
    model.status = ModelVersionStatus.PRODUCTION
    model.deployed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(model)
    
    return model


# A/B Testing Endpoints
@router.post("/ab-tests", response_model=ABTestResponse, status_code=status.HTTP_201_CREATED)
async def create_ab_test(
    test_data: ABTestCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new A/B test
    Admin only
    """
    ab_service = MLABTestingService(db)
    
    ab_test = await ab_service.create_ab_test(
        name=test_data.name,
        description=test_data.description,
        model_a_version_id=test_data.model_a_version_id,
        model_b_version_id=test_data.model_b_version_id,
        traffic_split_percentage=test_data.traffic_split_percentage,
        duration_days=test_data.duration_days,
        user_id=current_user.id
    )
    
    return ab_test


@router.get("/ab-tests", response_model=List[ABTestResponse])
async def list_ab_tests(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List A/B tests
    Admin only
    """
    query = db.query(MLABTest).order_by(MLABTest.created_at.desc())
    
    if status:
        query = query.filter(MLABTest.status == status)
    
    tests = query.offset(skip).limit(limit).all()
    
    return tests


@router.get("/ab-tests/{test_id}", response_model=dict)
async def get_ab_test_summary(
    test_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive A/B test summary
    Admin only
    """
    ab_service = MLABTestingService(db)
    
    summary = await ab_service.get_test_summary(test_id)
    
    return summary


@router.post("/ab-tests/{test_id}/start", response_model=ABTestResponse)
async def start_ab_test(
    test_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Start an A/B test
    Admin only
    """
    ab_service = MLABTestingService(db)
    
    ab_test = await ab_service.start_ab_test(test_id)
    
    return ab_test


@router.post("/ab-tests/{test_id}/complete", response_model=ABTestResponse)
async def complete_ab_test(
    test_id: int,
    promote_winner: bool = False,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Complete an A/B test and optionally promote winner
    Admin only
    """
    ab_service = MLABTestingService(db)
    
    ab_test = await ab_service.complete_ab_test(test_id, promote_winner=promote_winner)
    
    return ab_test


# Monitoring Endpoints
@router.get("/monitoring")
async def get_monitoring_data(
    model_version_id: Optional[int] = None,
    hours: int = 24,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get model monitoring data
    Admin only
    """
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(MLModelMonitoring).filter(
        MLModelMonitoring.window_start >= since
    ).order_by(MLModelMonitoring.window_start.desc())
    
    if model_version_id:
        query = query.filter(MLModelMonitoring.model_version_id == model_version_id)
    
    monitoring_data = query.all()
    
    return {
        "monitoring_windows": len(monitoring_data),
        "data": [
            {
                "model_version_id": m.model_version_id,
                "window_start": m.window_start.isoformat(),
                "window_end": m.window_end.isoformat(),
                "predictions_count": m.predictions_count,
                "accuracy": m.accuracy,
                "avg_latency_ms": m.avg_latency_ms,
                "p95_latency_ms": m.p95_latency_ms,
                "error_rate": m.error_rate,
                "alert_triggered": m.alert_triggered,
                "alert_type": m.alert_type,
                "alert_message": m.alert_message
            }
            for m in monitoring_data
        ]
    }


@router.get("/monitoring/alerts")
async def get_recent_alerts(
    hours: int = 24,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get recent monitoring alerts
    Admin only
    """
    since = datetime.utcnow() - timedelta(hours=hours)
    
    alerts = db.query(MLModelMonitoring).filter(
        MLModelMonitoring.alert_triggered == True,
        MLModelMonitoring.created_at >= since
    ).order_by(MLModelMonitoring.created_at.desc()).all()
    
    return {
        "alert_count": len(alerts),
        "alerts": [
            {
                "model_version_id": a.model_version_id,
                "alert_type": a.alert_type,
                "alert_message": a.alert_message,
                "created_at": a.created_at.isoformat(),
                "window_start": a.window_start.isoformat(),
                "metrics": {
                    "accuracy": a.accuracy,
                    "p95_latency_ms": a.p95_latency_ms,
                    "error_rate": a.error_rate
                }
            }
            for a in alerts
        ]
    }


# Rollback Endpoints
@router.post("/rollback", status_code=status.HTTP_202_ACCEPTED)
async def trigger_model_rollback(
    rollback_data: ModelRollbackRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Trigger manual model rollback
    Admin only
    """
    task = perform_rollback.delay(
        from_version_id=rollback_data.from_version_id,
        to_version_id=rollback_data.to_version_id,
        reason=rollback_data.reason,
        metrics={},
        user_id=current_user.id
    )
    
    return {
        "message": "Rollback initiated",
        "task_id": task.id
    }


@router.get("/rollbacks")
async def list_rollbacks(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List model rollbacks
    Admin only
    """
    rollbacks = db.query(MLModelRollback).order_by(
        MLModelRollback.rolled_back_at.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        "rollbacks": [
            {
                "id": r.id,
                "from_version_id": r.from_version_id,
                "to_version_id": r.to_version_id,
                "reason": r.reason,
                "trigger": r.trigger,
                "description": r.description,
                "rolled_back_at": r.rolled_back_at.isoformat(),
                "trigger_metrics": r.trigger_metrics
            }
            for r in rollbacks
        ]
    }


# Pipeline Endpoints
@router.post("/pipeline/run", status_code=status.HTTP_202_ACCEPTED)
async def run_training_pipeline(
    model_type: str,
    config: Optional[dict] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Run complete training pipeline
    Admin only
    """
    orchestrator = TrainingPipelineOrchestrator(db)
    
    result = await orchestrator.run_full_pipeline(
        model_type=model_type,
        trigger="manual",
        user_id=current_user.id,
        config=config or {}
    )
    
    return result
