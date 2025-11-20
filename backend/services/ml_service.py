"""
ML Service - 90-Second Promise Implementation

This service provides the main interface for all ML operations including
vulnerability detection, exploit generation, patch generation, and model management.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ScanRequest(BaseModel):
    """Request model for scanning."""
    code: str
    file_path: str = "unknown.py"
    language: Optional[str] = None
    scan_type: str = "quick"
    generate_exploits: bool = True
    generate_patches: bool = True


class ScanResponse(BaseModel):
    """Response model for scanning."""
    scan_id: str
    vulnerabilities: List[Dict[str, Any]]
    exploits: List[Dict[str, Any]]
    patches: List[Dict[str, Any]]
    scan_time_ms: int
    promise_kept: bool
    statistics: Dict[str, Any]


class ExploitRequest(BaseModel):
    """Request model for exploit generation."""
    vulnerability_type: str
    target_url: str
    vulnerable_param: str
    language: str = "python"
    sophistication: str = "intermediate"


class PatchRequest(BaseModel):
    """Request model for patch generation."""
    vulnerability_id: str
    vulnerability_type: str
    original_code: str
    file_path: str
    language: str = "python"
    framework: Optional[str] = None


class TrainingRequest(BaseModel):
    """Request model for model training."""
    model_type: str
    dataset_id: str
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 0.001


class MLService:
    """
    Main ML Service for the 90-Second Promise.

    This service orchestrates:
    - Vulnerability detection
    - Exploit generation
    - Patch generation
    - Model training and versioning
    - A/B testing
    - Performance monitoring
    """

    def __init__(self):
        """Initialize ML service."""
        self._initialized = False
        self._scanner = None
        self._predictor = None
        self._training_pipeline = None

        logger.info("MLService created")

    async def initialize(self) -> None:
        """Initialize all ML components."""
        if self._initialized:
            return

        try:
            # Import and initialize components
            from ..ml.inference.real_time_scanner import get_scanner
            from ..ml.inference.predictor import get_predictor
            from ..ml.training.pipeline import TrainingPipeline

            self._scanner = get_scanner()
            self._predictor = get_predictor()
            self._training_pipeline = TrainingPipeline()

            self._initialized = True
            logger.info("MLService initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize MLService: {e}")
            raise

    async def scan_code(self, request: ScanRequest) -> ScanResponse:
        """
        Scan code for vulnerabilities (90-second promise).

        Args:
            request: Scan request

        Returns:
            Scan response with vulnerabilities, exploits, and patches
        """
        await self.initialize()

        import time
        start_time = time.time()

        # Perform quick scan
        scan_result = await self._scanner.quick_scan(
            code=request.code,
            file_path=request.file_path,
            language=request.language
        )

        vulnerabilities = scan_result.get("vulnerabilities", [])
        exploits = []
        patches = []

        # Generate exploits if requested
        if request.generate_exploits and vulnerabilities:
            from ..ml.models.exploit_generator import (
                ExploitGeneratorModel,
                ExploitLanguage,
                SophisticationLevel
            )

            generator = ExploitGeneratorModel()

            for vuln in vulnerabilities[:5]:  # Limit to top 5 for performance
                try:
                    language = ExploitLanguage.PYTHON
                    if request.language == "javascript":
                        language = ExploitLanguage.JAVASCRIPT

                    exploit = await generator.generate(
                        vulnerability_type=vuln["vulnerability_type"],
                        target_url=f"http://target/{request.file_path}",
                        vulnerable_param="param",
                        language=language,
                        sophistication=SophisticationLevel.INTERMEDIATE
                    )

                    exploits.append({
                        "exploit_id": exploit.exploit_id,
                        "vulnerability_id": vuln["vulnerability_id"],
                        "language": exploit.language.value,
                        "title": exploit.title,
                        "code_preview": exploit.code[:500]
                    })
                except Exception as e:
                    logger.warning(f"Failed to generate exploit: {e}")

        # Generate patches if requested
        if request.generate_patches and vulnerabilities:
            from ..ml.models.patch_generator import PatchGeneratorModel, PatchLanguage

            generator = PatchGeneratorModel()

            for vuln in vulnerabilities[:5]:  # Limit to top 5 for performance
                try:
                    language = PatchLanguage.PYTHON
                    if request.language in ["javascript", "typescript"]:
                        language = PatchLanguage.JAVASCRIPT

                    patch = await generator.generate(
                        vulnerability_id=vuln["vulnerability_id"],
                        vulnerability_type=vuln["vulnerability_type"],
                        original_code=request.code,
                        file_path=request.file_path,
                        language=language
                    )

                    patches.append({
                        "patch_id": patch.patch_id,
                        "vulnerability_id": vuln["vulnerability_id"],
                        "title": patch.title,
                        "description": patch.description,
                        "confidence": patch.confidence
                    })
                except Exception as e:
                    logger.warning(f"Failed to generate patch: {e}")

        total_time = int((time.time() - start_time) * 1000)

        # Calculate statistics
        severity_counts = {}
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        statistics = {
            "total_vulnerabilities": len(vulnerabilities),
            "by_severity": severity_counts,
            "exploits_generated": len(exploits),
            "patches_generated": len(patches),
            "average_confidence": sum(v.get("confidence", 0) for v in vulnerabilities) / len(vulnerabilities) if vulnerabilities else 0
        }

        return ScanResponse(
            scan_id=f"scan_{int(time.time() * 1000)}",
            vulnerabilities=vulnerabilities,
            exploits=exploits,
            patches=patches,
            scan_time_ms=total_time,
            promise_kept=total_time <= 90000,
            statistics=statistics
        )

    async def generate_exploit(self, request: ExploitRequest) -> Dict[str, Any]:
        """
        Generate exploit code for a vulnerability.

        Args:
            request: Exploit request

        Returns:
            Generated exploit
        """
        await self.initialize()

        from ..ml.models.exploit_generator import (
            ExploitGeneratorModel,
            ExploitLanguage,
            SophisticationLevel
        )

        generator = ExploitGeneratorModel()

        exploit = await generator.generate(
            vulnerability_type=request.vulnerability_type,
            target_url=request.target_url,
            vulnerable_param=request.vulnerable_param,
            language=ExploitLanguage(request.language),
            sophistication=SophisticationLevel(request.sophistication)
        )

        return {
            "exploit_id": exploit.exploit_id,
            "vulnerability_type": exploit.vulnerability_type,
            "language": exploit.language.value,
            "sophistication": exploit.sophistication.value,
            "title": exploit.title,
            "description": exploit.description,
            "code": exploit.code,
            "usage_instructions": exploit.usage_instructions,
            "prerequisites": exploit.prerequisites,
            "risk_warning": exploit.risk_warning,
            "generation_time_ms": exploit.generation_time_ms
        }

    async def generate_patch(self, request: PatchRequest) -> Dict[str, Any]:
        """
        Generate patch for a vulnerability.

        Args:
            request: Patch request

        Returns:
            Generated patch
        """
        await self.initialize()

        from ..ml.models.patch_generator import PatchGeneratorModel, PatchLanguage, Framework

        generator = PatchGeneratorModel()

        framework = None
        if request.framework:
            framework = Framework(request.framework)

        patch = await generator.generate(
            vulnerability_id=request.vulnerability_id,
            vulnerability_type=request.vulnerability_type,
            original_code=request.original_code,
            file_path=request.file_path,
            language=PatchLanguage(request.language),
            framework=framework
        )

        return {
            "patch_id": patch.patch_id,
            "vulnerability_id": patch.vulnerability_id,
            "vulnerability_type": patch.vulnerability_type,
            "title": patch.title,
            "description": patch.description,
            "diffs": [
                {
                    "file_path": d.file_path,
                    "diff_text": d.diff_text,
                    "additions": d.additions,
                    "deletions": d.deletions
                }
                for d in patch.diffs
            ],
            "validation_tests": patch.validation_tests,
            "rollback_instructions": patch.rollback_instructions,
            "dependencies": patch.dependencies,
            "confidence": patch.confidence,
            "generation_time_ms": patch.generation_time_ms
        }

    async def start_training(self, request: TrainingRequest) -> Dict[str, Any]:
        """
        Start model training job.

        Args:
            request: Training request

        Returns:
            Training job information
        """
        await self.initialize()

        from ..ml.training.pipeline import TrainingConfig, ModelType

        config = TrainingConfig(
            model_type=ModelType(request.model_type),
            epochs=request.epochs,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate
        )

        job = await self._training_pipeline.start_training(config, request.dataset_id)

        return {
            "job_id": job.job_id,
            "model_type": job.model_type.value,
            "status": job.status.value,
            "created_at": job.created_at.isoformat()
        }

    async def get_training_status(self, job_id: str) -> Dict[str, Any]:
        """Get training job status."""
        await self.initialize()

        job = await self._training_pipeline.get_training_status(job_id)
        if not job:
            raise ValueError(f"Training job {job_id} not found")

        return {
            "job_id": job.job_id,
            "model_type": job.model_type.value,
            "status": job.status.value,
            "progress": job.progress,
            "current_epoch": job.current_epoch,
            "metrics": job.metrics,
            "best_metrics": job.best_metrics,
            "error_message": job.error_message,
            "model_version_id": job.model_version_id,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }

    async def list_model_versions(self, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List model versions."""
        await self.initialize()

        from ..ml.training.pipeline import ModelType

        mt = ModelType(model_type) if model_type else None
        versions = await self._training_pipeline.list_versions(mt)

        return [
            {
                "version_id": v.version_id,
                "model_type": v.model_type.value,
                "version_number": v.version_number,
                "metrics": v.metrics,
                "is_active": v.is_active,
                "is_champion": v.is_champion,
                "created_at": v.created_at.isoformat()
            }
            for v in versions
        ]

    async def set_active_model(
        self,
        version_id: str,
        is_champion: bool = False
    ) -> Dict[str, Any]:
        """Set a model version as active."""
        await self.initialize()

        version = await self._training_pipeline.set_active_version(version_id, is_champion)

        return {
            "version_id": version.version_id,
            "model_type": version.model_type.value,
            "version_number": version.version_number,
            "is_active": version.is_active,
            "is_champion": version.is_champion
        }

    async def start_ab_test(
        self,
        model_a_version: str,
        model_b_version: str,
        traffic_split: float = 0.5
    ) -> Dict[str, Any]:
        """Start A/B test between two model versions."""
        await self.initialize()

        test = await self._training_pipeline.start_ab_test(
            model_a_version=model_a_version,
            model_b_version=model_b_version,
            traffic_split=traffic_split
        )

        return {
            "test_id": test.test_id,
            "model_a_version": test.model_a_version,
            "model_b_version": test.model_b_version,
            "traffic_split": test.traffic_split,
            "is_active": test.is_active,
            "start_date": test.start_date.isoformat()
        }

    async def get_ab_test_results(self, test_id: str) -> Dict[str, Any]:
        """Get A/B test results."""
        await self.initialize()

        results = await self._training_pipeline.get_ab_test_results(test_id)

        return {
            "test_id": results.test_id,
            "model_a_metrics": results.model_a_metrics,
            "model_b_metrics": results.model_b_metrics,
            "winner": results.winner,
            "confidence": results.confidence,
            "samples_a": results.samples_a,
            "samples_b": results.samples_b
        }

    async def get_metrics(self) -> Dict[str, Any]:
        """Get ML service metrics."""
        await self.initialize()

        predictor_metrics = self._predictor.get_metrics() if self._predictor else {}

        return {
            "predictor_metrics": {
                k: v.dict() for k, v in predictor_metrics.items()
            } if predictor_metrics else {},
            "active_versions": self._predictor.get_active_versions() if self._predictor else {},
            "active_scans": len(self._scanner.list_active_scans()) if self._scanner else 0
        }

    async def create_dataset(
        self,
        name: str,
        model_type: str,
        data: List[Dict[str, Any]],
        labels: List[str],
        source: str = ""
    ) -> Dict[str, Any]:
        """Create a training dataset."""
        await self.initialize()

        from ..ml.training.pipeline import ModelType

        dataset = await self._training_pipeline.create_dataset(
            name=name,
            model_type=ModelType(model_type),
            data=data,
            labels=labels,
            source=source
        )

        return {
            "dataset_id": dataset.dataset_id,
            "name": dataset.name,
            "model_type": dataset.model_type.value,
            "num_samples": dataset.num_samples,
            "num_features": dataset.num_features,
            "labels": dataset.labels,
            "created_at": dataset.created_at.isoformat()
        }


# Singleton instance
_ml_service: Optional[MLService] = None


def get_ml_service() -> MLService:
    """Get the global ML service instance."""
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
    return _ml_service


# Export for convenience
__all__ = [
    "MLService",
    "ScanRequest",
    "ScanResponse",
    "ExploitRequest",
    "PatchRequest",
    "TrainingRequest",
    "get_ml_service"
]
