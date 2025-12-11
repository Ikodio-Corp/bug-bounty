"""
Training Pipeline Orchestrator - Coordinates the complete training pipeline
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from enum import Enum

from backend.models.ml_training import (
    MLTrainingJob,
    MLModelVersion,
    TrainingJobStatus,
    ModelVersionStatus
)
from backend.models.ml_feedback import MLPredictionFeedback
from backend.integrations.ml_client import ml_client
from backend.tasks.ml_training_tasks import train_model
from backend.services.ml_ab_testing_service import MLABTestingService

logger = logging.getLogger(__name__)


class PipelineStage(str, Enum):
    """Training pipeline stages"""
    DATA_COLLECTION = "data_collection"
    DATA_VALIDATION = "data_validation"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_TRAINING = "model_training"
    MODEL_EVALUATION = "model_evaluation"
    MODEL_TESTING = "model_testing"
    DEPLOYMENT = "deployment"


class TrainingPipelineOrchestrator:
    """Orchestrates the complete model training pipeline"""
    
    def __init__(self, db: Session):
        self.db = db
        self.current_stage = None
        self.pipeline_state = {}
    
    async def run_full_pipeline(
        self,
        model_type: str,
        trigger: str = "scheduled",
        user_id: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run the complete training pipeline from data collection to deployment
        
        Args:
            model_type: Type of model to train
            trigger: What triggered the pipeline (scheduled, manual, feedback)
            user_id: User ID if manually triggered
            config: Pipeline configuration
        
        Returns:
            Pipeline execution results
        """
        logger.info(f"Starting training pipeline for {model_type} (trigger: {trigger})")
        
        pipeline_start = datetime.utcnow()
        config = config or {}
        
        try:
            # Stage 1: Data Collection
            self.current_stage = PipelineStage.DATA_COLLECTION
            data_result = await self._collect_training_data(model_type, config)
            
            if not data_result["success"]:
                return self._pipeline_failed("data_collection", data_result["error"])
            
            # Stage 2: Data Validation
            self.current_stage = PipelineStage.DATA_VALIDATION
            validation_result = await self._validate_training_data(data_result["data"], config)
            
            if not validation_result["success"]:
                return self._pipeline_failed("data_validation", validation_result["error"])
            
            # Stage 3: Feature Engineering
            self.current_stage = PipelineStage.FEATURE_ENGINEERING
            features_result = await self._engineer_features(data_result["data"], config)
            
            # Stage 4: Create Training Job
            training_job = MLTrainingJob(
                job_type=trigger,
                model_type=model_type,
                training_data_count=len(data_result["data"]),
                config=config,
                status=TrainingJobStatus.RUNNING,
                started_at=datetime.utcnow(),
                triggered_by_user_id=user_id
            )
            self.db.add(training_job)
            self.db.commit()
            self.db.refresh(training_job)
            
            # Stage 5: Model Training
            self.current_stage = PipelineStage.MODEL_TRAINING
            training_result = await self._train_model(
                model_type=model_type,
                training_job_id=training_job.id,
                training_data=data_result["data"],
                config=config
            )
            
            if not training_result["success"]:
                training_job.status = TrainingJobStatus.FAILED
                training_job.error_message = training_result["error"]
                training_job.completed_at = datetime.utcnow()
                self.db.commit()
                return self._pipeline_failed("model_training", training_result["error"])
            
            model_version = training_result["model_version"]
            
            # Stage 6: Model Evaluation
            self.current_stage = PipelineStage.MODEL_EVALUATION
            evaluation_result = await self._evaluate_model(model_version, config)
            
            # Stage 7: Model Testing (A/B Test Setup)
            self.current_stage = PipelineStage.MODEL_TESTING
            testing_result = await self._setup_ab_test(model_version, config)
            
            # Stage 8: Deployment Decision
            self.current_stage = PipelineStage.DEPLOYMENT
            deployment_result = await self._deploy_if_better(
                model_version=model_version,
                evaluation_result=evaluation_result,
                config=config
            )
            
            # Complete training job
            training_job.status = TrainingJobStatus.COMPLETED
            training_job.completed_at = datetime.utcnow()
            training_job.duration_seconds = (
                training_job.completed_at - training_job.started_at
            ).total_seconds()
            training_job.result = {
                "model_version_id": model_version.id,
                "evaluation": evaluation_result,
                "testing": testing_result,
                "deployment": deployment_result
            }
            self.db.commit()
            
            pipeline_duration = (datetime.utcnow() - pipeline_start).total_seconds()
            
            logger.info(f"Training pipeline completed in {pipeline_duration:.2f}s")
            
            return {
                "success": True,
                "training_job_id": training_job.id,
                "model_version_id": model_version.id,
                "pipeline_duration_seconds": pipeline_duration,
                "stages": {
                    "data_collection": data_result,
                    "data_validation": validation_result,
                    "feature_engineering": features_result,
                    "model_training": training_result,
                    "model_evaluation": evaluation_result,
                    "model_testing": testing_result,
                    "deployment": deployment_result
                }
            }
            
        except Exception as e:
            logger.error(f"Pipeline error at stage {self.current_stage}: {e}")
            return self._pipeline_failed(self.current_stage, str(e))
    
    async def _collect_training_data(
        self,
        model_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 1: Collect training data"""
        try:
            # Get feedback data from last X days
            days_back = config.get("data_collection_days", 30)
            since_date = datetime.utcnow() - timedelta(days=days_back)
            
            feedback = self.db.query(MLPredictionFeedback).filter(
                MLPredictionFeedback.feedback_submitted_at >= since_date
            ).all()
            
            training_data = []
            for f in feedback:
                training_data.append({
                    "feedback_id": f.id,
                    "prediction_id": f.prediction_id,
                    "features": {
                        "confidence": f.confidence_score,
                        "predicted_vulnerability": f.predicted_vulnerability,
                        "predicted_type": f.predicted_type,
                        "predicted_severity": f.predicted_severity
                    },
                    "label": f.actual_vulnerability,
                    "is_correct": f.is_correct
                })
            
            logger.info(f"Collected {len(training_data)} training samples")
            
            return {
                "success": True,
                "data": training_data,
                "sample_count": len(training_data),
                "date_range": {
                    "start": since_date.isoformat(),
                    "end": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            return {"success": False, "error": str(e)}
    
    async def _validate_training_data(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 2: Validate training data quality"""
        try:
            min_samples = config.get("min_training_samples", 100)
            
            if len(data) < min_samples:
                return {
                    "success": False,
                    "error": f"Insufficient training data: {len(data)} < {min_samples}"
                }
            
            # Check for label balance
            positive_samples = sum(1 for d in data if d.get("label") == True)
            negative_samples = len(data) - positive_samples
            
            balance_ratio = min(positive_samples, negative_samples) / max(positive_samples, negative_samples)
            
            if balance_ratio < 0.3:  # Require at least 30% balance
                logger.warning(f"Imbalanced dataset: ratio={balance_ratio:.2f}")
            
            return {
                "success": True,
                "sample_count": len(data),
                "positive_samples": positive_samples,
                "negative_samples": negative_samples,
                "balance_ratio": balance_ratio
            }
            
        except Exception as e:
            logger.error(f"Error validating training data: {e}")
            return {"success": False, "error": str(e)}
    
    async def _engineer_features(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 3: Feature engineering"""
        try:
            # Feature engineering would happen here
            # For now, just log
            logger.info(f"Feature engineering on {len(data)} samples")
            
            return {
                "success": True,
                "features_engineered": True,
                "feature_count": len(data[0]["features"]) if data else 0
            }
            
        except Exception as e:
            logger.error(f"Error in feature engineering: {e}")
            return {"success": False, "error": str(e)}
    
    async def _train_model(
        self,
        model_type: str,
        training_job_id: int,
        training_data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 4: Train the model"""
        try:
            # Call ML engine to train model
            training_result = ml_client.train_model(
                model_type=model_type,
                training_data=training_data,
                config=config
            )
            
            # Create model version
            model_version = MLModelVersion(
                model_type=model_type,
                version=training_result["version"],
                training_job_id=training_job_id,
                training_samples=len(training_data),
                training_duration_seconds=training_result.get("training_time", 0),
                metrics=training_result.get("metrics", {}),
                model_path=training_result.get("model_path"),
                config=config,
                status=ModelVersionStatus.TRAINED,
                created_at=datetime.utcnow()
            )
            
            self.db.add(model_version)
            self.db.commit()
            self.db.refresh(model_version)
            
            logger.info(f"Model trained: version={model_version.version}")
            
            return {
                "success": True,
                "model_version": model_version,
                "metrics": training_result.get("metrics", {}),
                "training_time": training_result.get("training_time", 0)
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {"success": False, "error": str(e)}
    
    async def _evaluate_model(
        self,
        model_version: MLModelVersion,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 5: Evaluate model performance"""
        try:
            # Get evaluation from ML engine
            evaluation = ml_client.evaluate_model(
                model_type=model_version.model_type,
                version_id=model_version.id
            )
            
            logger.info(f"Model evaluated: accuracy={evaluation.get('accuracy', 0):.4f}")
            
            return {
                "success": True,
                "metrics": evaluation
            }
            
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {"success": False, "error": str(e)}
    
    async def _setup_ab_test(
        self,
        model_version: MLModelVersion,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 6: Setup A/B test if needed"""
        try:
            # Check if A/B testing is enabled
            if not config.get("enable_ab_testing", True):
                return {"success": True, "ab_test_created": False}
            
            # Find current production model
            production_model = self.db.query(MLModelVersion).filter(
                MLModelVersion.model_type == model_version.model_type,
                MLModelVersion.is_production == True
            ).first()
            
            if not production_model:
                logger.info("No production model to test against")
                return {"success": True, "ab_test_created": False}
            
            # Create A/B test
            ab_service = MLABTestingService(self.db)
            ab_test = await ab_service.create_ab_test(
                name=f"Test: {production_model.version} vs {model_version.version}",
                description=f"Automated A/B test for new model version {model_version.version}",
                model_a_version_id=production_model.id,
                model_b_version_id=model_version.id,
                traffic_split_percentage=config.get("ab_test_traffic_split", 10.0),
                duration_days=config.get("ab_test_duration_days", 7)
            )
            
            # Start the test
            await ab_service.start_ab_test(ab_test.id)
            
            logger.info(f"A/B test created: {ab_test.name}")
            
            return {
                "success": True,
                "ab_test_created": True,
                "ab_test_id": ab_test.id
            }
            
        except Exception as e:
            logger.error(f"Error setting up A/B test: {e}")
            return {"success": False, "error": str(e)}
    
    async def _deploy_if_better(
        self,
        model_version: MLModelVersion,
        evaluation_result: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 7: Deploy model if it's better than current production"""
        try:
            auto_deploy = config.get("auto_deploy", False)
            
            if not auto_deploy:
                logger.info("Auto-deployment disabled")
                return {"success": True, "deployed": False, "reason": "auto_deploy_disabled"}
            
            # Get current production model
            production_model = self.db.query(MLModelVersion).filter(
                MLModelVersion.model_type == model_version.model_type,
                MLModelVersion.is_production == True
            ).first()
            
            # If no production model, deploy this one
            if not production_model:
                model_version.is_production = True
                model_version.status = ModelVersionStatus.PRODUCTION
                model_version.deployed_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Model {model_version.version} deployed to production (first model)")
                
                return {"success": True, "deployed": True, "reason": "first_production_model"}
            
            # Compare with production model
            new_accuracy = evaluation_result.get("metrics", {}).get("accuracy", 0)
            prod_accuracy = production_model.metrics.get("accuracy", 0)
            
            min_improvement = config.get("min_accuracy_improvement", 0.02)  # 2% improvement
            
            if new_accuracy > prod_accuracy + min_improvement:
                # Deploy new model
                production_model.is_production = False
                production_model.status = ModelVersionStatus.ARCHIVED
                
                model_version.is_production = True
                model_version.status = ModelVersionStatus.PRODUCTION
                model_version.deployed_at = datetime.utcnow()
                model_version.replaced_by_version_id = production_model.id
                
                self.db.commit()
                
                logger.info(f"Model {model_version.version} deployed to production (better performance)")
                
                return {
                    "success": True,
                    "deployed": True,
                    "reason": "performance_improvement",
                    "new_accuracy": new_accuracy,
                    "old_accuracy": prod_accuracy
                }
            else:
                logger.info(f"Model not deployed (insufficient improvement: {new_accuracy:.4f} vs {prod_accuracy:.4f})")
                
                return {
                    "success": True,
                    "deployed": False,
                    "reason": "insufficient_improvement",
                    "new_accuracy": new_accuracy,
                    "old_accuracy": prod_accuracy
                }
            
        except Exception as e:
            logger.error(f"Error in deployment decision: {e}")
            return {"success": False, "error": str(e)}
    
    def _pipeline_failed(self, stage: str, error: str) -> Dict[str, Any]:
        """Handle pipeline failure"""
        logger.error(f"Pipeline failed at stage {stage}: {error}")
        
        return {
            "success": False,
            "failed_stage": stage,
            "error": error
        }
