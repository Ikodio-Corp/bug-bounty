"""
ML Training Pipeline - 90-Second Promise Implementation

This module implements the training pipeline for vulnerability detection models.
Supports continuous learning, model versioning, and A/B testing.
"""

import asyncio
import hashlib
import json
import logging
import os
import pickle
import time
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from pathlib import Path

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """Types of ML models."""
    BUG_DETECTOR = "bug_detector"
    EXPLOIT_GENERATOR = "exploit_generator"
    PATCH_GENERATOR = "patch_generator"
    SIMILARITY = "similarity"
    RISK_PREDICTOR = "risk_predictor"


class TrainingStatus(str, Enum):
    """Training job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelVersion(BaseModel):
    """Model version information."""
    version_id: str
    model_type: ModelType
    version_number: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    training_job_id: Optional[str] = None
    metrics: Dict[str, float] = {}
    parameters: Dict[str, Any] = {}
    is_active: bool = False
    is_champion: bool = False
    model_path: Optional[str] = None
    description: str = ""


class TrainingConfig(BaseModel):
    """Configuration for model training."""
    model_type: ModelType
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 0.001
    validation_split: float = 0.2
    early_stopping_patience: int = 3
    max_training_time_hours: float = 24.0
    use_gpu: bool = True
    distributed: bool = False
    hyperparameters: Dict[str, Any] = {}


class TrainingJob(BaseModel):
    """Training job information."""
    job_id: str
    model_type: ModelType
    config: TrainingConfig
    status: TrainingStatus = TrainingStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    current_epoch: int = 0
    metrics: Dict[str, List[float]] = {}
    best_metrics: Dict[str, float] = {}
    error_message: Optional[str] = None
    model_version_id: Optional[str] = None


class DatasetInfo(BaseModel):
    """Dataset information."""
    dataset_id: str
    name: str
    model_type: ModelType
    num_samples: int
    num_features: int
    labels: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = ""
    preprocessing_applied: List[str] = []


class ABTestConfig(BaseModel):
    """A/B test configuration."""
    test_id: str
    model_a_version: str
    model_b_version: str
    traffic_split: float = 0.5  # Percentage to model A
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    metric_to_compare: str = "accuracy"
    min_samples: int = 1000
    is_active: bool = True


class ABTestResult(BaseModel):
    """A/B test results."""
    test_id: str
    model_a_metrics: Dict[str, float]
    model_b_metrics: Dict[str, float]
    winner: Optional[str] = None
    confidence: float = 0.0
    samples_a: int = 0
    samples_b: int = 0
    completed_at: Optional[datetime] = None


class TrainingPipeline:
    """
    ML Training Pipeline for vulnerability detection models.

    Features:
    - Dataset management
    - Model training with various algorithms
    - Model versioning
    - A/B testing
    - Continuous learning
    - Performance monitoring
    """

    def __init__(self, models_dir: str = "/app/ml_models"):
        """Initialize training pipeline."""
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self._jobs: Dict[str, TrainingJob] = {}
        self._versions: Dict[str, ModelVersion] = {}
        self._ab_tests: Dict[str, ABTestConfig] = {}
        self._datasets: Dict[str, DatasetInfo] = {}

        logger.info(f"TrainingPipeline initialized with models_dir: {models_dir}")

    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID."""
        content = f"{prefix}:{time.time()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def create_dataset(
        self,
        name: str,
        model_type: ModelType,
        data: List[Dict[str, Any]],
        labels: List[str],
        source: str = ""
    ) -> DatasetInfo:
        """
        Create a training dataset.

        Args:
            name: Dataset name
            model_type: Type of model this dataset is for
            data: List of data samples
            labels: Label names
            source: Data source description

        Returns:
            Dataset information
        """
        dataset_id = self._generate_id("dataset")

        # Calculate dataset statistics
        num_samples = len(data)
        num_features = len(data[0]) if data else 0

        dataset = DatasetInfo(
            dataset_id=dataset_id,
            name=name,
            model_type=model_type,
            num_samples=num_samples,
            num_features=num_features,
            labels=labels,
            source=source
        )

        # Save dataset
        dataset_path = self.models_dir / "datasets" / f"{dataset_id}.pkl"
        dataset_path.parent.mkdir(parents=True, exist_ok=True)

        with open(dataset_path, "wb") as f:
            pickle.dump({"info": dataset.dict(), "data": data}, f)

        self._datasets[dataset_id] = dataset
        logger.info(f"Created dataset {dataset_id} with {num_samples} samples")

        return dataset

    async def start_training(
        self,
        config: TrainingConfig,
        dataset_id: str
    ) -> TrainingJob:
        """
        Start a model training job.

        Args:
            config: Training configuration
            dataset_id: Dataset to use for training

        Returns:
            Training job information
        """
        job_id = self._generate_id("job")

        job = TrainingJob(
            job_id=job_id,
            model_type=config.model_type,
            config=config,
            status=TrainingStatus.PENDING
        )

        self._jobs[job_id] = job

        # Start training in background
        asyncio.create_task(self._run_training(job_id, dataset_id))

        logger.info(f"Started training job {job_id} for {config.model_type.value}")
        return job

    async def _run_training(self, job_id: str, dataset_id: str) -> None:
        """Run the actual training process."""
        job = self._jobs[job_id]

        try:
            job.status = TrainingStatus.RUNNING
            job.started_at = datetime.utcnow()

            # Load dataset
            dataset_path = self.models_dir / "datasets" / f"{dataset_id}.pkl"
            if not dataset_path.exists():
                raise FileNotFoundError(f"Dataset {dataset_id} not found")

            with open(dataset_path, "rb") as f:
                dataset = pickle.load(f)

            # Initialize metrics
            job.metrics = {
                "train_loss": [],
                "val_loss": [],
                "accuracy": [],
                "precision": [],
                "recall": [],
                "f1": []
            }

            # Simulate training epochs
            config = job.config
            for epoch in range(config.epochs):
                job.current_epoch = epoch + 1
                job.progress = (epoch + 1) / config.epochs

                # Simulate training metrics
                train_loss = 1.0 / (epoch + 1) + np.random.uniform(0, 0.1)
                val_loss = 1.0 / (epoch + 1) + np.random.uniform(0, 0.15)
                accuracy = min(0.95, 0.5 + epoch * 0.05 + np.random.uniform(0, 0.02))
                precision = min(0.95, 0.5 + epoch * 0.04 + np.random.uniform(0, 0.02))
                recall = min(0.95, 0.5 + epoch * 0.045 + np.random.uniform(0, 0.02))
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

                job.metrics["train_loss"].append(train_loss)
                job.metrics["val_loss"].append(val_loss)
                job.metrics["accuracy"].append(accuracy)
                job.metrics["precision"].append(precision)
                job.metrics["recall"].append(recall)
                job.metrics["f1"].append(f1)

                # Early stopping check
                if epoch > config.early_stopping_patience:
                    recent_losses = job.metrics["val_loss"][-config.early_stopping_patience:]
                    if all(recent_losses[i] >= recent_losses[i-1] for i in range(1, len(recent_losses))):
                        logger.info(f"Early stopping at epoch {epoch + 1}")
                        break

                await asyncio.sleep(0.1)  # Simulate training time

            # Save best metrics
            job.best_metrics = {
                "accuracy": max(job.metrics["accuracy"]),
                "precision": max(job.metrics["precision"]),
                "recall": max(job.metrics["recall"]),
                "f1": max(job.metrics["f1"]),
                "final_train_loss": job.metrics["train_loss"][-1],
                "final_val_loss": job.metrics["val_loss"][-1]
            }

            # Create model version
            version = await self._create_model_version(job)
            job.model_version_id = version.version_id

            job.status = TrainingStatus.COMPLETED
            job.completed_at = datetime.utcnow()

            logger.info(f"Training job {job_id} completed with accuracy {job.best_metrics['accuracy']:.4f}")

        except Exception as e:
            job.status = TrainingStatus.FAILED
            job.error_message = str(e)
            logger.error(f"Training job {job_id} failed: {e}")

    async def _create_model_version(self, job: TrainingJob) -> ModelVersion:
        """Create a new model version from completed training."""
        version_id = self._generate_id("version")

        # Generate version number
        existing_versions = [
            v for v in self._versions.values()
            if v.model_type == job.model_type
        ]
        version_num = len(existing_versions) + 1
        version_number = f"v{version_num}.0.0"

        # Save model
        model_path = self.models_dir / job.model_type.value / f"{version_id}.pkl"
        model_path.parent.mkdir(parents=True, exist_ok=True)

        # Create model artifact (placeholder)
        model_artifact = {
            "version_id": version_id,
            "model_type": job.model_type.value,
            "metrics": job.best_metrics,
            "config": job.config.dict(),
            "created_at": datetime.utcnow().isoformat()
        }

        with open(model_path, "wb") as f:
            pickle.dump(model_artifact, f)

        version = ModelVersion(
            version_id=version_id,
            model_type=job.model_type,
            version_number=version_number,
            training_job_id=job.job_id,
            metrics=job.best_metrics,
            parameters=job.config.hyperparameters,
            model_path=str(model_path),
            description=f"Trained with {job.current_epoch} epochs"
        )

        self._versions[version_id] = version
        logger.info(f"Created model version {version_number} ({version_id})")

        return version

    async def get_training_status(self, job_id: str) -> Optional[TrainingJob]:
        """Get training job status."""
        return self._jobs.get(job_id)

    async def list_versions(
        self,
        model_type: Optional[ModelType] = None
    ) -> List[ModelVersion]:
        """List model versions, optionally filtered by type."""
        versions = list(self._versions.values())
        if model_type:
            versions = [v for v in versions if v.model_type == model_type]
        return sorted(versions, key=lambda v: v.created_at, reverse=True)

    async def set_active_version(
        self,
        version_id: str,
        is_champion: bool = False
    ) -> ModelVersion:
        """Set a model version as active."""
        version = self._versions.get(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")

        # Deactivate other versions of same type
        for v in self._versions.values():
            if v.model_type == version.model_type:
                v.is_active = False
                if is_champion:
                    v.is_champion = False

        version.is_active = True
        if is_champion:
            version.is_champion = True

        logger.info(f"Set version {version_id} as active (champion: {is_champion})")
        return version

    async def start_ab_test(
        self,
        model_a_version: str,
        model_b_version: str,
        traffic_split: float = 0.5,
        metric_to_compare: str = "accuracy",
        min_samples: int = 1000
    ) -> ABTestConfig:
        """
        Start an A/B test between two model versions.

        Args:
            model_a_version: Version ID for model A
            model_b_version: Version ID for model B
            traffic_split: Percentage of traffic to model A
            metric_to_compare: Metric to use for comparison
            min_samples: Minimum samples before declaring winner

        Returns:
            A/B test configuration
        """
        # Validate versions exist
        if model_a_version not in self._versions:
            raise ValueError(f"Version {model_a_version} not found")
        if model_b_version not in self._versions:
            raise ValueError(f"Version {model_b_version} not found")

        test_id = self._generate_id("abtest")

        test = ABTestConfig(
            test_id=test_id,
            model_a_version=model_a_version,
            model_b_version=model_b_version,
            traffic_split=traffic_split,
            metric_to_compare=metric_to_compare,
            min_samples=min_samples
        )

        self._ab_tests[test_id] = test
        logger.info(f"Started A/B test {test_id}: {model_a_version} vs {model_b_version}")

        return test

    async def get_ab_test_results(self, test_id: str) -> ABTestResult:
        """Get A/B test results."""
        test = self._ab_tests.get(test_id)
        if not test:
            raise ValueError(f"A/B test {test_id} not found")

        version_a = self._versions[test.model_a_version]
        version_b = self._versions[test.model_b_version]

        # Get metrics
        metric = test.metric_to_compare
        metric_a = version_a.metrics.get(metric, 0)
        metric_b = version_b.metrics.get(metric, 0)

        # Determine winner
        winner = None
        confidence = 0.0

        if metric_a > metric_b:
            winner = test.model_a_version
            confidence = min(0.95, (metric_a - metric_b) / metric_a * 2)
        elif metric_b > metric_a:
            winner = test.model_b_version
            confidence = min(0.95, (metric_b - metric_a) / metric_b * 2)

        return ABTestResult(
            test_id=test_id,
            model_a_metrics=version_a.metrics,
            model_b_metrics=version_b.metrics,
            winner=winner,
            confidence=confidence,
            samples_a=100,  # Placeholder
            samples_b=100,  # Placeholder
            completed_at=datetime.utcnow() if winner else None
        )

    async def stop_ab_test(self, test_id: str) -> ABTestConfig:
        """Stop an A/B test."""
        test = self._ab_tests.get(test_id)
        if not test:
            raise ValueError(f"A/B test {test_id} not found")

        test.is_active = False
        test.end_date = datetime.utcnow()

        logger.info(f"Stopped A/B test {test_id}")
        return test

    async def retrain_model(
        self,
        model_type: ModelType,
        new_data: List[Dict[str, Any]],
        labels: List[str]
    ) -> TrainingJob:
        """
        Retrain a model with new data (continuous learning).

        Args:
            model_type: Type of model to retrain
            new_data: New training data
            labels: Label names

        Returns:
            Training job
        """
        # Create dataset from new data
        dataset = await self.create_dataset(
            name=f"retrain_{model_type.value}_{datetime.utcnow().isoformat()}",
            model_type=model_type,
            data=new_data,
            labels=labels,
            source="continuous_learning"
        )

        # Get current champion model's config
        champion = None
        for v in self._versions.values():
            if v.model_type == model_type and v.is_champion:
                champion = v
                break

        # Create training config
        config = TrainingConfig(
            model_type=model_type,
            epochs=5,  # Fewer epochs for retraining
            batch_size=32,
            learning_rate=0.0001,  # Lower learning rate for fine-tuning
            hyperparameters=champion.parameters if champion else {}
        )

        return await self.start_training(config, dataset.dataset_id)

    def get_model_metrics_history(
        self,
        model_type: ModelType
    ) -> List[Dict[str, Any]]:
        """Get metrics history for all versions of a model type."""
        versions = [v for v in self._versions.values() if v.model_type == model_type]
        versions.sort(key=lambda v: v.created_at)

        return [
            {
                "version_id": v.version_id,
                "version_number": v.version_number,
                "created_at": v.created_at.isoformat(),
                "metrics": v.metrics,
                "is_champion": v.is_champion
            }
            for v in versions
        ]


# Export for convenience
__all__ = [
    "TrainingPipeline",
    "TrainingConfig",
    "TrainingJob",
    "TrainingStatus",
    "ModelType",
    "ModelVersion",
    "DatasetInfo",
    "ABTestConfig",
    "ABTestResult"
]
