"""
ML Integration API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.core.database import get_async_db
from backend.core.security import Security
from backend.models.user import User
from backend.services.ml_feedback_service import MLFeedbackService
from backend.services.enhanced_scan_service import EnhancedScanService
from backend.integrations.ml_client import ml_client

router = APIRouter(prefix="/ml", tags=["ML Integration"])
security = Security()


class FeedbackSubmitRequest(BaseModel):
    """Request model for submitting ML feedback"""
    prediction_id: int = Field(..., description="ML prediction ID")
    is_correct: bool = Field(..., description="Whether prediction was correct")
    actual_vulnerability: Optional[bool] = Field(None, description="Actual vulnerability status")
    actual_type: Optional[str] = Field(None, description="Actual vulnerability type")
    actual_severity: Optional[float] = Field(None, ge=0, le=10, description="Actual severity score")
    feedback_notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    bug_id: Optional[int] = Field(None, description="Related bug ID")
    scan_id: Optional[int] = Field(None, description="Related scan ID")


class ConfidenceScoreRequest(BaseModel):
    """Request model for confidence score evaluation"""
    model_type: str = Field(default="rule_based", description="Model type")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score to evaluate")


class ModelPerformanceRequest(BaseModel):
    """Request model for model performance calculation"""
    model_type: str = Field(default="rule_based", description="Model type")
    days: int = Field(default=7, ge=1, le=365, description="Days to analyze")


@router.post("/feedback/submit")
async def submit_feedback(
    request: FeedbackSubmitRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Submit feedback for ML prediction
    
    User confirms or corrects ML prediction to improve model accuracy
    """
    try:
        feedback_service = MLFeedbackService(db)
        
        result = await feedback_service.submit_feedback(
            user_id=current_user.id,
            prediction_id=request.prediction_id,
            is_correct=request.is_correct,
            actual_vulnerability=request.actual_vulnerability,
            actual_type=request.actual_type,
            actual_severity=request.actual_severity,
            feedback_notes=request.feedback_notes,
            bug_id=request.bug_id,
            scan_id=request.scan_id
        )
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            **result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.post("/confidence/evaluate")
async def evaluate_confidence_score(
    request: ConfidenceScoreRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Evaluate reliability of a confidence score
    
    Get information about how accurate predictions are at a given confidence level
    """
    try:
        feedback_service = MLFeedbackService(db)
        
        reliability = await feedback_service.get_confidence_score_reliability(
            model_type=request.model_type,
            confidence_score=request.confidence_score
        )
        
        return reliability
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate confidence score: {str(e)}"
        )


@router.post("/confidence/calibrate")
async def calibrate_confidence_scores(
    model_type: str = "rule_based",
    days: int = 30,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Calibrate confidence scores based on feedback
    
    Requires admin privileges
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    try:
        feedback_service = MLFeedbackService(db)
        
        calibrations = await feedback_service.calibrate_confidence_scores(
            model_type=model_type,
            days=days
        )
        
        return {
            "success": True,
            "model_type": model_type,
            "calibrations": calibrations
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calibration failed: {str(e)}"
        )


@router.get("/performance/{model_type}")
async def get_model_performance(
    model_type: str,
    days: int = 7,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Get model performance metrics based on feedback
    """
    try:
        feedback_service = MLFeedbackService(db)
        
        performance = await feedback_service.calculate_model_performance(
            model_type=model_type,
            days=days
        )
        
        return performance
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance: {str(e)}"
        )


@router.get("/statistics/feedback")
async def get_feedback_statistics(
    days: int = 30,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Get feedback statistics
    """
    try:
        feedback_service = MLFeedbackService(db)
        
        stats = await feedback_service.get_feedback_statistics(
            user_id=current_user.id if current_user.role != "admin" else None,
            days=days
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/statistics/predictions")
async def get_prediction_statistics(
    days: int = 30,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Get ML prediction statistics for user scans
    """
    try:
        scan_service = EnhancedScanService(db)
        
        stats = await scan_service.get_ml_statistics(
            user_id=current_user.id if current_user.role != "admin" else None,
            days=days
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/models/list")
async def list_ml_models(
    model_type: Optional[str] = None,
    is_production: Optional[bool] = None,
    current_user: User = Depends(security.get_current_user)
):
    """
    List available ML models
    """
    try:
        models = await ml_client.list_models(
            model_type=model_type,
            is_production=is_production
        )
        
        return {
            "models": models,
            "count": len(models)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list models: {str(e)}"
        )


@router.get("/models/{model_id}/report")
async def get_model_report(
    model_id: int,
    current_user: User = Depends(security.get_current_user)
):
    """
    Get comprehensive model evaluation report
    """
    try:
        report = await ml_client.get_evaluation_report(model_id)
        
        return report
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get report: {str(e)}"
        )


@router.get("/models/{model_id}/drift")
async def analyze_model_drift(
    model_id: int,
    recent_predictions: int = 100,
    current_user: User = Depends(security.get_current_user)
):
    """
    Analyze model performance drift
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    try:
        drift = await ml_client.get_model_drift(
            model_id=model_id,
            recent_predictions=recent_predictions
        )
        
        return drift
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze drift: {str(e)}"
        )


@router.get("/health")
async def check_ml_service_health(
    current_user: User = Depends(security.get_current_user)
):
    """
    Check ML service health status
    """
    try:
        is_healthy = await ml_client.health_check()
        
        return {
            "ml_service": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "ml_service": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/models/compare")
async def compare_models(
    model_ids: List[int],
    current_user: User = Depends(security.get_current_user)
):
    """
    Compare multiple ML models
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    try:
        comparison = await ml_client.compare_models(model_ids)
        
        return comparison
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare models: {str(e)}"
        )
