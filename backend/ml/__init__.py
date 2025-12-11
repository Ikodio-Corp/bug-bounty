"""
ML Package - 90-Second Promise Implementation

This package provides ML capabilities for vulnerability detection,
exploit generation, and patch generation.
"""

from .models.bug_detector import (
    BugDetectorModel,
    BugDetectorConfig,
    DetectionResult,
    VulnerabilityType,
    SeverityLevel
)
# from .models.exploit_generator import (
#     ExploitGeneratorModel,
#     ExploitGeneratorConfig,
#     GeneratedExploit,
#     ExploitLanguage,
#     SophisticationLevel
# )
from .models.patch_generator import (
    PatchGeneratorModel,
    PatchGeneratorConfig,
    GeneratedPatch,
    PatchLanguage,
    Framework
)
from .inference.predictor import (
    MLPredictor,
    PredictionRequest,
    PredictionResult,
    get_predictor
)
from .inference.real_time_scanner import (
    RealTimeScanner,
    ScanJob,
    ScanResult,
    get_scanner
)
from .training.pipeline import (
    TrainingPipeline,
    TrainingConfig,
    TrainingJob,
    ModelVersion
)

__all__ = [
    # Models
    "BugDetectorModel",
    "BugDetectorConfig",
    "DetectionResult",
    "VulnerabilityType",
    "SeverityLevel",
    # "ExploitGeneratorModel",
    # "ExploitGeneratorConfig",
    # "GeneratedExploit",
    # "ExploitLanguage",
    # "SophisticationLevel",
    "PatchGeneratorModel",
    "PatchGeneratorConfig",
    "GeneratedPatch",
    "PatchLanguage",
    "Framework",
    # Inference
    "MLPredictor",
    "PredictionRequest",
    "PredictionResult",
    "get_predictor",
    "RealTimeScanner",
    "ScanJob",
    "ScanResult",
    "get_scanner",
    # Training
    "TrainingPipeline",
    "TrainingConfig",
    "TrainingJob",
    "ModelVersion",
]
