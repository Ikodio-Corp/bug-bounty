"""
ML Feedback Service - Handle user feedback and confidence calibration
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from backend.models.ml_feedback import (
    MLPredictionFeedback,
    MLModelPerformance,
    ConfidenceScoreCalibration
)
from backend.models.bug import Bug, Scan
from backend.integrations.ml_client import ml_client

logger = logging.getLogger(__name__)


class MLFeedbackService:
    """
    Service for managing ML prediction feedback and confidence scoring
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def submit_feedback(
        self,
        user_id: int,
        prediction_id: int,
        is_correct: bool,
        actual_vulnerability: Optional[bool] = None,
        actual_type: Optional[str] = None,
        actual_severity: Optional[float] = None,
        feedback_notes: Optional[str] = None,
        bug_id: Optional[int] = None,
        scan_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Submit feedback for ML prediction
        
        Args:
            user_id: User submitting feedback
            prediction_id: ML prediction ID
            is_correct: Whether prediction was correct
            actual_vulnerability: Actual vulnerability status
            actual_type: Actual vulnerability type
            actual_severity: Actual severity score
            feedback_notes: Additional notes
            bug_id: Related bug ID
            scan_id: Related scan ID
            
        Returns:
            Feedback record dictionary
        """
        try:
            # Get original prediction data
            if bug_id:
                result = await self.db.execute(
                    select(Bug).where(Bug.id == bug_id)
                )
                bug = result.scalar_one_or_none()
                
                if bug:
                    predicted_vulnerability = bug.ml_predicted_vulnerability
                    predicted_type = bug.ml_predicted_type
                    predicted_severity = bug.ml_predicted_severity
                    confidence_score = bug.ml_confidence_score
                    prediction_made_at = bug.ml_predicted_at
                else:
                    raise ValueError(f"Bug {bug_id} not found")
            else:
                # Default values if no bug reference
                predicted_vulnerability = None
                predicted_type = None
                predicted_severity = None
                confidence_score = 0.0
                prediction_made_at = datetime.utcnow()
            
            # Calculate response time
            response_time_hours = None
            if prediction_made_at:
                delta = datetime.utcnow() - prediction_made_at
                response_time_hours = delta.total_seconds() / 3600
            
            # Create feedback record
            feedback = MLPredictionFeedback(
                prediction_id=prediction_id,
                bug_id=bug_id,
                scan_id=scan_id,
                user_id=user_id,
                predicted_vulnerability=predicted_vulnerability,
                predicted_type=predicted_type,
                predicted_severity=predicted_severity,
                confidence_score=confidence_score,
                is_correct=is_correct,
                actual_vulnerability=actual_vulnerability,
                actual_type=actual_type,
                actual_severity=actual_severity,
                feedback_type="user",
                feedback_notes=feedback_notes,
                response_time_hours=response_time_hours,
                prediction_made_at=prediction_made_at
            )
            
            self.db.add(feedback)
            await self.db.commit()
            await self.db.refresh(feedback)
            
            # Submit to ML service for retraining
            try:
                await ml_client.submit_feedback(
                    prediction_id=prediction_id,
                    is_correct=is_correct,
                    actual_label=actual_vulnerability,
                    feedback_notes=feedback_notes
                )
                
                feedback.synced_to_ml_at = datetime.utcnow()
                await self.db.commit()
                
            except Exception as e:
                logger.warning(f"Failed to sync feedback to ML service: {e}")
            
            logger.info(f"Feedback submitted for prediction {prediction_id}")
            
            return {
                "feedback_id": feedback.id,
                "prediction_id": prediction_id,
                "is_correct": is_correct,
                "submitted_at": feedback.feedback_submitted_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            await self.db.rollback()
            raise
    
    async def get_confidence_score_reliability(
        self,
        model_type: str,
        confidence_score: float
    ) -> Dict[str, Any]:
        """
        Get reliability information for a confidence score
        
        Args:
            model_type: Model type
            confidence_score: Confidence score to evaluate
            
        Returns:
            Reliability information
        """
        try:
            # Find calibration for this confidence range
            result = await self.db.execute(
                select(ConfidenceScoreCalibration).where(
                    and_(
                        ConfidenceScoreCalibration.model_type == model_type,
                        ConfidenceScoreCalibration.confidence_range_min <= confidence_score,
                        ConfidenceScoreCalibration.confidence_range_max >= confidence_score
                    )
                ).order_by(ConfidenceScoreCalibration.updated_at.desc())
            )
            
            calibration = result.scalar_one_or_none()
            
            if not calibration:
                # Return default reliability based on confidence
                return self._default_reliability(confidence_score)
            
            return {
                "confidence_score": confidence_score,
                "actual_accuracy": calibration.actual_accuracy,
                "sample_count": calibration.sample_count,
                "reliability_level": calibration.reliability_level,
                "recommended_threshold": calibration.recommended_threshold,
                "calibrated": True
            }
            
        except Exception as e:
            logger.error(f"Error getting confidence reliability: {e}")
            return self._default_reliability(confidence_score)
    
    def _default_reliability(self, confidence_score: float) -> Dict[str, Any]:
        """Return default reliability estimate"""
        if confidence_score >= 0.9:
            level = "very_high"
        elif confidence_score >= 0.7:
            level = "high"
        elif confidence_score >= 0.5:
            level = "medium"
        else:
            level = "low"
        
        return {
            "confidence_score": confidence_score,
            "actual_accuracy": None,
            "sample_count": 0,
            "reliability_level": level,
            "recommended_threshold": 0.7,
            "calibrated": False
        }
    
    async def calibrate_confidence_scores(
        self,
        model_type: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Calibrate confidence scores based on feedback data
        
        Args:
            model_type: Model type to calibrate
            days: Days of data to analyze
            
        Returns:
            List of calibration results
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all feedback for this model type
            result = await self.db.execute(
                select(MLPredictionFeedback).where(
                    MLPredictionFeedback.feedback_submitted_at >= cutoff_date
                ).order_by(MLPredictionFeedback.confidence_score)
            )
            
            feedbacks = result.scalars().all()
            
            if not feedbacks:
                logger.warning(f"No feedback data for calibration of {model_type}")
                return []
            
            # Define confidence ranges
            ranges = [
                (0.0, 0.5),
                (0.5, 0.7),
                (0.7, 0.85),
                (0.85, 0.95),
                (0.95, 1.0)
            ]
            
            calibrations = []
            
            for range_min, range_max in ranges:
                range_feedbacks = [
                    f for f in feedbacks
                    if range_min <= f.confidence_score < range_max
                ]
                
                if not range_feedbacks:
                    continue
                
                correct_count = sum(1 for f in range_feedbacks if f.is_correct)
                actual_accuracy = correct_count / len(range_feedbacks)
                
                # Determine reliability level
                if actual_accuracy >= 0.9:
                    reliability = "very_high"
                elif actual_accuracy >= 0.75:
                    reliability = "high"
                elif actual_accuracy >= 0.6:
                    reliability = "medium"
                else:
                    reliability = "low"
                
                # Create or update calibration
                calibration = ConfidenceScoreCalibration(
                    model_type=model_type,
                    confidence_range_min=range_min,
                    confidence_range_max=range_max,
                    actual_accuracy=actual_accuracy,
                    sample_count=len(range_feedbacks),
                    reliability_level=reliability,
                    recommended_threshold=0.7 if actual_accuracy >= 0.75 else 0.8,
                    calibrated_from=cutoff_date,
                    calibrated_to=datetime.utcnow()
                )
                
                self.db.add(calibration)
                
                calibrations.append({
                    "range": f"{range_min}-{range_max}",
                    "actual_accuracy": round(actual_accuracy, 4),
                    "sample_count": len(range_feedbacks),
                    "reliability_level": reliability
                })
            
            await self.db.commit()
            
            logger.info(f"Calibrated {len(calibrations)} confidence ranges for {model_type}")
            
            return calibrations
            
        except Exception as e:
            logger.error(f"Error calibrating confidence scores: {e}")
            await self.db.rollback()
            return []
    
    async def calculate_model_performance(
        self,
        model_type: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Calculate model performance metrics from feedback
        
        Args:
            model_type: Model type
            days: Days to analyze
            
        Returns:
            Performance metrics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await self.db.execute(
                select(MLPredictionFeedback).where(
                    MLPredictionFeedback.feedback_submitted_at >= cutoff_date
                )
            )
            
            feedbacks = result.scalars().all()
            
            if not feedbacks:
                return {
                    "model_type": model_type,
                    "period_days": days,
                    "total_feedback": 0
                }
            
            # Calculate metrics
            total = len(feedbacks)
            correct = sum(1 for f in feedbacks if f.is_correct)
            
            # True/False Positives/Negatives
            tp = sum(1 for f in feedbacks if f.predicted_vulnerability and f.actual_vulnerability)
            fp = sum(1 for f in feedbacks if f.predicted_vulnerability and not f.actual_vulnerability)
            tn = sum(1 for f in feedbacks if not f.predicted_vulnerability and not f.actual_vulnerability)
            fn = sum(1 for f in feedbacks if not f.predicted_vulnerability and f.actual_vulnerability)
            
            accuracy = correct / total if total > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            avg_confidence = sum(f.confidence_score for f in feedbacks) / total if total > 0 else 0
            
            # Store performance record
            performance = MLModelPerformance(
                model_id=0,  # Will be updated with actual model ID
                model_type=model_type,
                model_version="1.0.0",
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1_score,
                total_predictions=total,
                correct_predictions=correct,
                false_positives=fp,
                false_negatives=fn,
                period_start=cutoff_date,
                period_end=datetime.utcnow(),
                average_confidence=avg_confidence
            )
            
            self.db.add(performance)
            await self.db.commit()
            
            return {
                "model_type": model_type,
                "period_days": days,
                "total_feedback": total,
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1_score, 4),
                "average_confidence": round(avg_confidence, 4),
                "confusion_matrix": {
                    "true_positive": tp,
                    "false_positive": fp,
                    "true_negative": tn,
                    "false_negative": fn
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating model performance: {e}")
            return {"error": str(e)}
    
    async def get_feedback_statistics(
        self,
        user_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get feedback statistics
        
        Args:
            user_id: Optional user filter
            days: Days to analyze
            
        Returns:
            Statistics dictionary
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = select(MLPredictionFeedback).where(
                MLPredictionFeedback.feedback_submitted_at >= cutoff_date
            )
            
            if user_id:
                query = query.where(MLPredictionFeedback.user_id == user_id)
            
            result = await self.db.execute(query)
            feedbacks = result.scalars().all()
            
            if not feedbacks:
                return {
                    "total_feedback": 0,
                    "period_days": days
                }
            
            correct_feedback = sum(1 for f in feedbacks if f.is_correct)
            avg_response_time = sum(
                f.response_time_hours for f in feedbacks if f.response_time_hours
            ) / len([f for f in feedbacks if f.response_time_hours])
            
            feedback_by_type = {}
            for f in feedbacks:
                feedback_by_type[f.feedback_type] = feedback_by_type.get(f.feedback_type, 0) + 1
            
            return {
                "total_feedback": len(feedbacks),
                "correct_predictions": correct_feedback,
                "incorrect_predictions": len(feedbacks) - correct_feedback,
                "accuracy_rate": round(correct_feedback / len(feedbacks), 4),
                "average_response_time_hours": round(avg_response_time, 2),
                "feedback_by_type": feedback_by_type,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting feedback statistics: {e}")
            return {"error": str(e)}
