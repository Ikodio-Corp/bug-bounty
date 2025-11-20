"""
ML API Routes - 90-Second Promise Implementation

This module provides REST API endpoints for all ML operations including
vulnerability scanning, exploit generation, patch generation, and model management.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ...services.ml_service import (
    get_ml_service,
    MLService,
    ScanRequest,
    ExploitRequest,
    PatchRequest,
    TrainingRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["ML Pipeline"])


# Request/Response Models
class QuickScanRequest(BaseModel):
    """Request for quick 90-second scan."""
    code: str = Field(..., description="Source code to scan")
    file_path: str = Field(default="unknown.py", description="File path")
    language: Optional[str] = Field(default=None, description="Programming language")
    generate_exploits: bool = Field(default=True, description="Generate exploit POCs")
    generate_patches: bool = Field(default=True, description="Generate patches")


class BatchScanRequest(BaseModel):
    """Request for batch scanning."""
    files: List[Dict[str, str]] = Field(..., description="List of files with path and content")
    scan_type: str = Field(default="quick", description="Scan type: quick, standard, deep")


class ExploitGenerationRequest(BaseModel):
    """Request for exploit generation."""
    vulnerability_type: str = Field(..., description="Type of vulnerability")
    target_url: str = Field(..., description="Target URL")
    vulnerable_param: str = Field(..., description="Vulnerable parameter")
    language: str = Field(default="python", description="Exploit language")
    sophistication: str = Field(default="intermediate", description="Sophistication level")


class PatchGenerationRequest(BaseModel):
    """Request for patch generation."""
    vulnerability_id: str = Field(..., description="Vulnerability ID")
    vulnerability_type: str = Field(..., description="Vulnerability type")
    original_code: str = Field(..., description="Original vulnerable code")
    file_path: str = Field(..., description="File path")
    language: str = Field(default="python", description="Programming language")
    framework: Optional[str] = Field(default=None, description="Framework")


class ModelTrainingRequest(BaseModel):
    """Request for model training."""
    model_type: str = Field(..., description="Model type to train")
    dataset_id: str = Field(..., description="Dataset ID to use")
    epochs: int = Field(default=10, description="Number of training epochs")
    batch_size: int = Field(default=32, description="Batch size")
    learning_rate: float = Field(default=0.001, description="Learning rate")


class DatasetCreationRequest(BaseModel):
    """Request for dataset creation."""
    name: str = Field(..., description="Dataset name")
    model_type: str = Field(..., description="Model type")
    data: List[Dict[str, Any]] = Field(..., description="Training data")
    labels: List[str] = Field(..., description="Label names")
    source: str = Field(default="", description="Data source")


class ABTestRequest(BaseModel):
    """Request for A/B test."""
    model_a_version: str = Field(..., description="Version ID for model A")
    model_b_version: str = Field(..., description="Version ID for model B")
    traffic_split: float = Field(default=0.5, description="Traffic split (0-1)")


# Dependency
async def get_service() -> MLService:
    """Get ML service instance."""
    return get_ml_service()


# Endpoints
@router.post("/scan/quick", response_model=Dict[str, Any])
async def quick_scan(
    request: QuickScanRequest,
    service: MLService = Depends(get_service)
):
    """
    Perform a quick 90-second vulnerability scan.

    This endpoint implements the 90-second promise for vulnerability detection.
    It will scan the provided code and optionally generate exploits and patches.

    - **code**: Source code to scan
    - **file_path**: Path to the file (for language detection)
    - **language**: Programming language (auto-detected if not provided)
    - **generate_exploits**: Whether to generate exploit POCs
    - **generate_patches**: Whether to generate patches
    """
    try:
        scan_request = ScanRequest(
            code=request.code,
            file_path=request.file_path,
            language=request.language,
            scan_type="quick",
            generate_exploits=request.generate_exploits,
            generate_patches=request.generate_patches
        )

        result = await service.scan_code(scan_request)

        return {
            "success": True,
            "scan_id": result.scan_id,
            "vulnerabilities": result.vulnerabilities,
            "exploits": result.exploits,
            "patches": result.patches,
            "scan_time_ms": result.scan_time_ms,
            "promise_kept": result.promise_kept,
            "statistics": result.statistics
        }

    except Exception as e:
        logger.error(f"Quick scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan/batch", response_model=Dict[str, Any])
async def batch_scan(
    request: BatchScanRequest,
    background_tasks: BackgroundTasks,
    service: MLService = Depends(get_service)
):
    """
    Start a batch scan for multiple files.

    Returns a scan ID that can be used to check progress and results.
    """
    try:
        # For batch scans, we create individual scans and aggregate
        results = []
        total_vulnerabilities = 0

        for file_info in request.files:
            scan_request = ScanRequest(
                code=file_info.get("content", ""),
                file_path=file_info.get("path", "unknown"),
                language=file_info.get("language"),
                scan_type=request.scan_type
            )

            result = await service.scan_code(scan_request)
            results.append({
                "file_path": file_info.get("path"),
                "vulnerabilities": result.vulnerabilities,
                "scan_time_ms": result.scan_time_ms
            })
            total_vulnerabilities += len(result.vulnerabilities)

        return {
            "success": True,
            "files_scanned": len(request.files),
            "total_vulnerabilities": total_vulnerabilities,
            "results": results
        }

    except Exception as e:
        logger.error(f"Batch scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exploit/generate", response_model=Dict[str, Any])
async def generate_exploit(
    request: ExploitGenerationRequest,
    service: MLService = Depends(get_service)
):
    """
    Generate exploit POC for a vulnerability.

    Generates proof-of-concept exploit code in the specified language
    and sophistication level.

    - **vulnerability_type**: Type (sql_injection, xss, command_injection, etc.)
    - **target_url**: Target URL for the exploit
    - **vulnerable_param**: Vulnerable parameter name
    - **language**: Exploit language (python, javascript, bash, etc.)
    - **sophistication**: Level (basic, intermediate, advanced)
    """
    try:
        exploit_request = ExploitRequest(
            vulnerability_type=request.vulnerability_type,
            target_url=request.target_url,
            vulnerable_param=request.vulnerable_param,
            language=request.language,
            sophistication=request.sophistication
        )

        result = await service.generate_exploit(exploit_request)

        return {
            "success": True,
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Exploit generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/patch/generate", response_model=Dict[str, Any])
async def generate_patch(
    request: PatchGenerationRequest,
    service: MLService = Depends(get_service)
):
    """
    Generate patch for a vulnerability.

    Generates secure code fix with validation tests and rollback instructions.

    - **vulnerability_id**: ID of the vulnerability
    - **vulnerability_type**: Type of vulnerability
    - **original_code**: Original vulnerable code
    - **file_path**: File path
    - **language**: Programming language
    - **framework**: Optional framework (django, flask, express, etc.)
    """
    try:
        patch_request = PatchRequest(
            vulnerability_id=request.vulnerability_id,
            vulnerability_type=request.vulnerability_type,
            original_code=request.original_code,
            file_path=request.file_path,
            language=request.language,
            framework=request.framework
        )

        result = await service.generate_patch(patch_request)

        return {
            "success": True,
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Patch generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/training/start", response_model=Dict[str, Any])
async def start_training(
    request: ModelTrainingRequest,
    service: MLService = Depends(get_service)
):
    """
    Start model training job.

    Starts a background training job for the specified model type.
    Use /training/{job_id}/status to check progress.

    - **model_type**: Type of model (bug_detector, exploit_generator, etc.)
    - **dataset_id**: Dataset to use for training
    - **epochs**: Number of training epochs
    - **batch_size**: Batch size
    - **learning_rate**: Learning rate
    """
    try:
        training_request = TrainingRequest(
            model_type=request.model_type,
            dataset_id=request.dataset_id,
            epochs=request.epochs,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate
        )

        result = await service.start_training(training_request)

        return {
            "success": True,
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Training start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training/{job_id}/status", response_model=Dict[str, Any])
async def get_training_status(
    job_id: str,
    service: MLService = Depends(get_service)
):
    """
    Get training job status.

    Returns current status, progress, and metrics for a training job.
    """
    try:
        result = await service.get_training_status(job_id)

        return {
            "success": True,
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Get training status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/versions", response_model=Dict[str, Any])
async def list_model_versions(
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    service: MLService = Depends(get_service)
):
    """
    List all model versions.

    Returns list of all model versions, optionally filtered by type.
    """
    try:
        versions = await service.list_model_versions(model_type)

        return {
            "success": True,
            "versions": versions
        }

    except Exception as e:
        logger.error(f"List versions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{version_id}/activate", response_model=Dict[str, Any])
async def activate_model(
    version_id: str,
    is_champion: bool = Query(False, description="Set as champion model"),
    service: MLService = Depends(get_service)
):
    """
    Set a model version as active.

    Activates the specified model version for inference.
    """
    try:
        result = await service.set_active_model(version_id, is_champion)

        return {
            "success": True,
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Activate model failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-test/start", response_model=Dict[str, Any])
async def start_ab_test(
    request: ABTestRequest,
    service: MLService = Depends(get_service)
):
    """
    Start A/B test between two model versions.

    Splits traffic between two models to compare performance.
    """
    try:
        result = await service.start_ab_test(
            model_a_version=request.model_a_version,
            model_b_version=request.model_b_version,
            traffic_split=request.traffic_split
        )

        return {
            "success": True,
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Start A/B test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ab-test/{test_id}/results", response_model=Dict[str, Any])
async def get_ab_test_results(
    test_id: str,
    service: MLService = Depends(get_service)
):
    """
    Get A/B test results.

    Returns metrics comparison and winner determination.
    """
    try:
        result = await service.get_ab_test_results(test_id)

        return {
            "success": True,
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Get A/B test results failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasets", response_model=Dict[str, Any])
async def create_dataset(
    request: DatasetCreationRequest,
    service: MLService = Depends(get_service)
):
    """
    Create a training dataset.

    Creates a new dataset that can be used for model training.
    """
    try:
        result = await service.create_dataset(
            name=request.name,
            model_type=request.model_type,
            data=request.data,
            labels=request.labels,
            source=request.source
        )

        return {
            "success": True,
            **result
        }

    except Exception as e:
        logger.error(f"Create dataset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=Dict[str, Any])
async def get_metrics(
    service: MLService = Depends(get_service)
):
    """
    Get ML service metrics.

    Returns performance metrics, active versions, and system status.
    """
    try:
        result = await service.get_metrics()

        return {
            "success": True,
            **result
        }

    except Exception as e:
        logger.error(f"Get metrics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-types", response_model=Dict[str, Any])
async def get_supported_types():
    """
    Get supported vulnerability types, languages, and frameworks.

    Returns all supported options for scanning and generation.
    """
    return {
        "success": True,
        "vulnerability_types": [
            "sql_injection", "xss", "command_injection", "path_traversal",
            "ssrf", "xxe", "deserialization", "hardcoded_secrets",
            "crypto_weakness", "csrf", "open_redirect", "file_upload",
            "idor", "template_injection", "prototype_pollution"
        ],
        "exploit_languages": [
            "python", "bash", "javascript", "curl", "powershell", "ruby", "go", "php"
        ],
        "patch_languages": [
            "python", "javascript", "typescript", "java", "go", "php", "ruby", "csharp"
        ],
        "frameworks": [
            "django", "flask", "fastapi", "express", "nestjs",
            "spring_boot", "rails", "laravel", "gin", "aspnet"
        ],
        "sophistication_levels": [
            "basic", "intermediate", "advanced"
        ],
        "scan_types": [
            "quick", "standard", "deep", "continuous"
        ]
    }


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    ML service health check.

    Returns service health status and readiness.
    """
    return {
        "status": "healthy",
        "service": "ml_pipeline",
        "version": "1.0.0",
        "features": {
            "vulnerability_detection": True,
            "exploit_generation": True,
            "patch_generation": True,
            "model_training": True,
            "ab_testing": True
        }
    }
