"""
ML A/B Testing Service - Model comparison and experiment management
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import random
import logging
from scipy import stats
import numpy as np

from backend.models.ml_training import (
    MLABTest,
    MLABTestPrediction,
    MLModelVersion,
    ABTestStatus
)
from backend.integrations.ml_client import ml_client

logger = logging.getLogger(__name__)


class MLABTestingService:
    """Service for managing ML model A/B tests"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_ab_test(
        self,
        name: str,
        description: str,
        model_a_version_id: int,
        model_b_version_id: int,
        traffic_split_percentage: float = 50.0,
        duration_days: int = 7,
        user_id: Optional[int] = None
    ) -> MLABTest:
        """
        Create a new A/B test between two model versions
        
        Args:
            name: Test name
            description: Test description
            model_a_version_id: Control model version ID
            model_b_version_id: Experiment model version ID
            traffic_split_percentage: % of traffic to model B (0-100)
            duration_days: Test duration in days
            user_id: User creating the test
        """
        # Validate models exist
        model_a = self.db.query(MLModelVersion).filter(
            MLModelVersion.id == model_a_version_id
        ).first()
        model_b = self.db.query(MLModelVersion).filter(
            MLModelVersion.id == model_b_version_id
        ).first()
        
        if not model_a or not model_b:
            raise ValueError("Invalid model version IDs")
        
        if model_a.model_type != model_b.model_type:
            raise ValueError("Models must be of the same type")
        
        # Check for existing active test
        existing_test = self.db.query(MLABTest).filter(
            and_(
                MLABTest.status == ABTestStatus.RUNNING,
                or_(
                    MLABTest.model_a_version_id == model_a_version_id,
                    MLABTest.model_a_version_id == model_b_version_id,
                    MLABTest.model_b_version_id == model_a_version_id,
                    MLABTest.model_b_version_id == model_b_version_id
                )
            )
        ).first()
        
        if existing_test:
            raise ValueError(f"An active A/B test already exists for these models: {existing_test.name}")
        
        # Create A/B test
        ab_test = MLABTest(
            name=name,
            description=description,
            model_a_version_id=model_a_version_id,
            model_b_version_id=model_b_version_id,
            traffic_split_percentage=traffic_split_percentage,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=duration_days),
            status=ABTestStatus.DRAFT,
            created_by_user_id=user_id,
            model_a_predictions=0,
            model_b_predictions=0,
            model_a_metrics={},
            model_b_metrics={}
        )
        
        self.db.add(ab_test)
        self.db.commit()
        self.db.refresh(ab_test)
        
        logger.info(f"Created A/B test: {ab_test.name} (ID: {ab_test.id})")
        
        return ab_test
    
    async def start_ab_test(self, test_id: int) -> MLABTest:
        """Start an A/B test"""
        ab_test = self.db.query(MLABTest).filter(MLABTest.id == test_id).first()
        
        if not ab_test:
            raise ValueError(f"A/B test {test_id} not found")
        
        if ab_test.status != ABTestStatus.DRAFT:
            raise ValueError(f"Cannot start test in {ab_test.status} status")
        
        ab_test.status = ABTestStatus.RUNNING
        ab_test.start_date = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Started A/B test: {ab_test.name}")
        
        return ab_test
    
    def select_model_for_prediction(self, test_id: int) -> Tuple[int, bool]:
        """
        Select which model version to use for a prediction based on traffic split
        
        Returns:
            Tuple of (model_version_id, is_model_a)
        """
        ab_test = self.db.query(MLABTest).filter(
            MLABTest.id == test_id,
            MLABTest.status == ABTestStatus.RUNNING
        ).first()
        
        if not ab_test:
            raise ValueError(f"No running A/B test found with ID {test_id}")
        
        # Random selection based on traffic split
        use_model_b = random.random() * 100 < ab_test.traffic_split_percentage
        
        if use_model_b:
            return ab_test.model_b_version_id, False
        else:
            return ab_test.model_a_version_id, True
    
    async def record_prediction(
        self,
        test_id: int,
        model_version_id: int,
        is_model_a: bool,
        bug_id: Optional[int] = None,
        scan_id: Optional[int] = None,
        prediction_result: Dict[str, Any] = None,
        confidence_score: float = None,
        latency_ms: int = None
    ) -> MLABTestPrediction:
        """Record a prediction made during A/B testing"""
        prediction = MLABTestPrediction(
            ab_test_id=test_id,
            model_version_id=model_version_id,
            is_model_a=is_model_a,
            bug_id=bug_id,
            scan_id=scan_id,
            prediction_result=prediction_result,
            confidence_score=confidence_score,
            latency_ms=latency_ms,
            predicted_at=datetime.utcnow()
        )
        
        self.db.add(prediction)
        
        # Update test counters
        ab_test = self.db.query(MLABTest).filter(MLABTest.id == test_id).first()
        if is_model_a:
            ab_test.model_a_predictions += 1
        else:
            ab_test.model_b_predictions += 1
        
        self.db.commit()
        
        return prediction
    
    async def update_test_metrics(self, test_id: int) -> Dict[str, Any]:
        """Calculate and update metrics for both models in the test"""
        ab_test = self.db.query(MLABTest).filter(MLABTest.id == test_id).first()
        
        if not ab_test:
            raise ValueError(f"A/B test {test_id} not found")
        
        # Get predictions for both models
        model_a_predictions = self.db.query(MLABTestPrediction).filter(
            MLABTestPrediction.ab_test_id == test_id,
            MLABTestPrediction.is_model_a == True
        ).all()
        
        model_b_predictions = self.db.query(MLABTestPrediction).filter(
            MLABTestPrediction.ab_test_id == test_id,
            MLABTestPrediction.is_model_a == False
        ).all()
        
        # Calculate metrics for model A
        model_a_metrics = self._calculate_model_metrics(model_a_predictions)
        
        # Calculate metrics for model B
        model_b_metrics = self._calculate_model_metrics(model_b_predictions)
        
        # Calculate statistical significance
        significance = self._calculate_statistical_significance(
            model_a_predictions,
            model_b_predictions
        )
        
        # Update test
        ab_test.model_a_metrics = model_a_metrics
        ab_test.model_b_metrics = model_b_metrics
        ab_test.statistical_significance = significance
        ab_test.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "model_a_metrics": model_a_metrics,
            "model_b_metrics": model_b_metrics,
            "statistical_significance": significance,
            "sample_size_a": len(model_a_predictions),
            "sample_size_b": len(model_b_predictions)
        }
    
    def _calculate_model_metrics(self, predictions: List[MLABTestPrediction]) -> Dict[str, Any]:
        """Calculate performance metrics for a model"""
        if not predictions:
            return {}
        
        # Accuracy from feedback
        feedback_predictions = [p for p in predictions if p.user_feedback is not None]
        if feedback_predictions:
            correct = sum(1 for p in feedback_predictions if p.user_feedback == "correct")
            accuracy = correct / len(feedback_predictions)
        else:
            accuracy = None
        
        # Confidence metrics
        confidences = [p.confidence_score for p in predictions if p.confidence_score is not None]
        avg_confidence = np.mean(confidences) if confidences else None
        
        # Latency metrics
        latencies = [p.latency_ms for p in predictions if p.latency_ms is not None]
        metrics = {
            "total_predictions": len(predictions),
            "accuracy": accuracy,
            "avg_confidence": avg_confidence,
            "avg_latency_ms": np.mean(latencies) if latencies else None,
            "p50_latency_ms": np.percentile(latencies, 50) if latencies else None,
            "p95_latency_ms": np.percentile(latencies, 95) if latencies else None,
            "p99_latency_ms": np.percentile(latencies, 99) if latencies else None
        }
        
        return metrics
    
    def _calculate_statistical_significance(
        self,
        model_a_predictions: List[MLABTestPrediction],
        model_b_predictions: List[MLABTestPrediction]
    ) -> float:
        """Calculate statistical significance using t-test"""
        # Get feedback results
        a_results = [
            1 if p.user_feedback == "correct" else 0
            for p in model_a_predictions
            if p.user_feedback is not None
        ]
        
        b_results = [
            1 if p.user_feedback == "correct" else 0
            for p in model_b_predictions
            if p.user_feedback is not None
        ]
        
        if len(a_results) < 30 or len(b_results) < 30:
            return None  # Not enough data for significance testing
        
        # Perform two-sample t-test
        try:
            t_stat, p_value = stats.ttest_ind(a_results, b_results)
            return float(p_value)
        except Exception as e:
            logger.error(f"Error calculating statistical significance: {e}")
            return None
    
    async def determine_winner(self, test_id: int, min_significance: float = 0.05) -> Optional[int]:
        """
        Determine the winner of an A/B test
        
        Args:
            test_id: A/B test ID
            min_significance: Minimum p-value for significance (default 0.05)
        
        Returns:
            Winner model version ID or None if no clear winner
        """
        ab_test = self.db.query(MLABTest).filter(MLABTest.id == test_id).first()
        
        if not ab_test:
            raise ValueError(f"A/B test {test_id} not found")
        
        # Update metrics first
        await self.update_test_metrics(test_id)
        
        # Refresh to get updated metrics
        self.db.refresh(ab_test)
        
        model_a_metrics = ab_test.model_a_metrics
        model_b_metrics = ab_test.model_b_metrics
        
        # Check if we have enough data
        if not model_a_metrics or not model_b_metrics:
            return None
        
        if model_a_metrics.get("total_predictions", 0) < 100 or \
           model_b_metrics.get("total_predictions", 0) < 100:
            return None  # Not enough data
        
        # Check statistical significance
        if ab_test.statistical_significance is None or \
           ab_test.statistical_significance > min_significance:
            return None  # Not statistically significant
        
        # Compare performance metrics
        a_accuracy = model_a_metrics.get("accuracy")
        b_accuracy = model_b_metrics.get("accuracy")
        
        if a_accuracy is None or b_accuracy is None:
            return None
        
        # Determine winner based on accuracy
        if b_accuracy > a_accuracy:
            winner_id = ab_test.model_b_version_id
            reason = f"Model B has higher accuracy: {b_accuracy:.4f} vs {a_accuracy:.4f}"
        elif a_accuracy > b_accuracy:
            winner_id = ab_test.model_a_version_id
            reason = f"Model A has higher accuracy: {a_accuracy:.4f} vs {b_accuracy:.4f}"
        else:
            # Tie-breaker: use latency
            a_latency = model_a_metrics.get("avg_latency_ms", float("inf"))
            b_latency = model_b_metrics.get("avg_latency_ms", float("inf"))
            
            if b_latency < a_latency:
                winner_id = ab_test.model_b_version_id
                reason = f"Model B has lower latency: {b_latency:.2f}ms vs {a_latency:.2f}ms"
            else:
                winner_id = ab_test.model_a_version_id
                reason = f"Model A has lower latency: {a_latency:.2f}ms vs {b_latency:.2f}ms"
        
        # Update test with winner
        ab_test.winner_model_version_id = winner_id
        ab_test.winner_determined_at = datetime.utcnow()
        ab_test.winner_reason = reason
        
        self.db.commit()
        
        logger.info(f"A/B test {test_id} winner determined: {winner_id} - {reason}")
        
        return winner_id
    
    async def complete_ab_test(self, test_id: int, promote_winner: bool = False) -> MLABTest:
        """
        Complete an A/B test and optionally promote the winner to production
        
        Args:
            test_id: A/B test ID
            promote_winner: Whether to promote winner to production
        """
        ab_test = self.db.query(MLABTest).filter(MLABTest.id == test_id).first()
        
        if not ab_test:
            raise ValueError(f"A/B test {test_id} not found")
        
        if ab_test.status != ABTestStatus.RUNNING:
            raise ValueError(f"Cannot complete test in {ab_test.status} status")
        
        # Determine winner if not already done
        if not ab_test.winner_model_version_id:
            await self.determine_winner(test_id)
            self.db.refresh(ab_test)
        
        # Complete the test
        ab_test.status = ABTestStatus.COMPLETED
        ab_test.end_date = datetime.utcnow()
        
        # Promote winner to production if requested
        if promote_winner and ab_test.winner_model_version_id:
            winner = self.db.query(MLModelVersion).filter(
                MLModelVersion.id == ab_test.winner_model_version_id
            ).first()
            
            if winner:
                # Demote current production model
                current_production = self.db.query(MLModelVersion).filter(
                    MLModelVersion.model_type == winner.model_type,
                    MLModelVersion.is_production == True
                ).first()
                
                if current_production:
                    current_production.is_production = False
                
                # Promote winner
                winner.is_production = True
                winner.deployed_at = datetime.utcnow()
                
                logger.info(f"Promoted model version {winner.id} to production")
        
        self.db.commit()
        
        return ab_test
    
    async def get_active_tests(self) -> List[MLABTest]:
        """Get all active A/B tests"""
        return self.db.query(MLABTest).filter(
            MLABTest.status == ABTestStatus.RUNNING
        ).all()
    
    async def get_test_summary(self, test_id: int) -> Dict[str, Any]:
        """Get comprehensive summary of an A/B test"""
        ab_test = self.db.query(MLABTest).filter(MLABTest.id == test_id).first()
        
        if not ab_test:
            raise ValueError(f"A/B test {test_id} not found")
        
        # Update metrics
        await self.update_test_metrics(test_id)
        self.db.refresh(ab_test)
        
        return {
            "test_id": ab_test.id,
            "name": ab_test.name,
            "status": ab_test.status.value,
            "start_date": ab_test.start_date.isoformat() if ab_test.start_date else None,
            "end_date": ab_test.end_date.isoformat() if ab_test.end_date else None,
            "traffic_split": ab_test.traffic_split_percentage,
            "model_a": {
                "version_id": ab_test.model_a_version_id,
                "predictions": ab_test.model_a_predictions,
                "metrics": ab_test.model_a_metrics
            },
            "model_b": {
                "version_id": ab_test.model_b_version_id,
                "predictions": ab_test.model_b_predictions,
                "metrics": ab_test.model_b_metrics
            },
            "statistical_significance": ab_test.statistical_significance,
            "winner_version_id": ab_test.winner_model_version_id,
            "winner_reason": ab_test.winner_reason
        }
