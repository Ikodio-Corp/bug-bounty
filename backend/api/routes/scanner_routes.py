"""
Scanner API Routes - Security Scanning Endpoints

This module provides REST API endpoints for all security scanners
including SCA, Secret, Container, and IaC scanning.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scanners", tags=["Security Scanners"])


# Request Models
class SCASccanRequest(BaseModel):
    """Request for SCA scan."""
    project_path: str = Field(..., description="Project path to scan")
    include_dev: bool = Field(default=False, description="Include dev dependencies")


class SecretScanRequest(BaseModel):
    """Request for secret scan."""
    target_path: str = Field(..., description="Path to scan")
    include_git_history: bool = Field(default=True, description="Scan git history")
    filter_false_positives: bool = Field(default=True, description="Filter FPs")
    custom_patterns: List[Dict[str, str]] = Field(default=[], description="Custom patterns")


class ContainerScanRequest(BaseModel):
    """Request for container scan."""
    target: str = Field(..., description="Image name or Dockerfile path")
    use_trivy: bool = Field(default=True, description="Use Trivy scanner")
    severity_filter: str = Field(default="CRITICAL,HIGH", description="Severity filter")


class IaCScanRequest(BaseModel):
    """Request for IaC scan."""
    target: str = Field(..., description="File or directory path")
    use_checkov: bool = Field(default=False, description="Use Checkov")


class CodeScanRequest(BaseModel):
    """Request for code scan."""
    code: str = Field(..., description="Source code to scan")
    file_path: str = Field(default="unknown", description="File path")
    language: Optional[str] = Field(None, description="Programming language")


# SCA Scanner Endpoints
@router.post("/sca/scan", response_model=Dict[str, Any])
async def sca_scan(request: SCASccanRequest):
    """
    Run Software Composition Analysis scan.

    Analyzes dependencies for vulnerabilities and license issues.
    """
    try:
        from ...scanners.sca_scanner import SCAScanner

        scanner = SCAScanner()
        results = await scanner.full_scan(request.project_path)

        return {
            "success": True,
            "scanner": "SCA Scanner",
            **results
        }

    except Exception as e:
        logger.error(f"SCA scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sca/check-package", response_model=Dict[str, Any])
async def check_package(
    package_name: str = Query(..., description="Package name"),
    version: str = Query(..., description="Package version"),
    ecosystem: str = Query(default="npm", description="Package ecosystem")
):
    """Check single package for vulnerabilities."""
    try:
        from ...scanners.sca_scanner import SCAScanner

        scanner = SCAScanner()
        vulnerabilities = await scanner.query_osv_database(package_name, version, ecosystem)

        return {
            "success": True,
            "package": package_name,
            "version": version,
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities
        }

    except Exception as e:
        logger.error(f"Package check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Secret Scanner Endpoints
@router.post("/secrets/scan", response_model=Dict[str, Any])
async def secret_scan(request: SecretScanRequest):
    """
    Run secret detection scan.

    Detects hardcoded secrets, API keys, and credentials.
    """
    try:
        from ...scanners.secret_scanner import SecretScanner

        scanner = SecretScanner()
        results = await scanner.comprehensive_scan(
            target_path=request.target_path,
            include_git_history=request.include_git_history,
            filter_fps=request.filter_false_positives
        )

        return {
            "success": True,
            "scanner": "Secret Scanner",
            **results
        }

    except Exception as e:
        logger.error(f"Secret scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/secrets/scan-content", response_model=Dict[str, Any])
async def scan_content_for_secrets(
    content: str,
    file_path: str = Query(default="unknown", description="File path")
):
    """Scan content string for secrets."""
    try:
        from ...scanners.secret_scanner import SecretScanner

        scanner = SecretScanner()
        results = await scanner.scan(content, file_path)

        return {
            "success": True,
            "scanner": "Secret Scanner",
            **results
        }

    except Exception as e:
        logger.error(f"Content scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Container Scanner Endpoints
@router.post("/container/scan", response_model=Dict[str, Any])
async def container_scan(request: ContainerScanRequest):
    """
    Run container security scan.

    Analyzes Docker images and Dockerfiles for vulnerabilities.
    """
    try:
        from ...scanners.container_scanner import ContainerScanner

        scanner = ContainerScanner()
        results = await scanner.comprehensive_scan(
            target=request.target,
            use_trivy=request.use_trivy
        )

        return {
            "success": True,
            "scanner": "Container Scanner",
            **results
        }

    except Exception as e:
        logger.error(f"Container scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/container/sbom", response_model=Dict[str, Any])
async def generate_sbom(
    image_name: str = Query(..., description="Docker image name"),
    format: str = Query(default="cyclonedx", description="SBOM format")
):
    """Generate Software Bill of Materials for container image."""
    try:
        from ...scanners.container_scanner import ContainerScanner

        scanner = ContainerScanner()
        results = await scanner.generate_sbom(image_name, format)

        return {
            "success": True,
            **results
        }

    except Exception as e:
        logger.error(f"SBOM generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# IaC Scanner Endpoints
@router.post("/iac/scan", response_model=Dict[str, Any])
async def iac_scan(request: IaCScanRequest):
    """
    Run Infrastructure as Code scan.

    Analyzes Terraform, Kubernetes, CloudFormation, and Ansible.
    """
    try:
        from ...scanners.iac_scanner import IaCScanner

        scanner = IaCScanner()
        results = await scanner.comprehensive_scan(
            target=request.target,
            use_checkov=request.use_checkov
        )

        return {
            "success": True,
            "scanner": "IaC Scanner",
            **results
        }

    except Exception as e:
        logger.error(f"IaC scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Code Scanner Endpoints (using ML)
@router.post("/code/scan", response_model=Dict[str, Any])
async def code_scan(request: CodeScanRequest):
    """
    Run ML-powered code vulnerability scan.

    Uses the 90-second ML pipeline for vulnerability detection.
    """
    try:
        from ...services.ml_service import get_ml_service, ScanRequest

        service = get_ml_service()
        scan_request = ScanRequest(
            code=request.code,
            file_path=request.file_path,
            language=request.language,
            scan_type="quick",
            generate_exploits=True,
            generate_patches=True
        )

        result = await service.scan_code(scan_request)

        return {
            "success": True,
            "scanner": "ML Code Scanner",
            "scan_id": result.scan_id,
            "vulnerabilities": result.vulnerabilities,
            "exploits_generated": len(result.exploits),
            "patches_generated": len(result.patches),
            "scan_time_ms": result.scan_time_ms,
            "promise_kept": result.promise_kept,
            "statistics": result.statistics
        }

    except Exception as e:
        logger.error(f"Code scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Comprehensive Scan Endpoint
@router.post("/comprehensive", response_model=Dict[str, Any])
async def comprehensive_scan(
    target: str = Query(..., description="Target to scan"),
    include_sca: bool = Query(default=True),
    include_secrets: bool = Query(default=True),
    include_iac: bool = Query(default=True)
):
    """
    Run comprehensive security scan.

    Combines multiple scanners for thorough analysis.
    """
    try:
        results = {
            "success": True,
            "target": target,
            "scanners_run": []
        }

        if include_sca:
            from ...scanners.sca_scanner import SCAScanner
            scanner = SCAScanner()
            sca_results = await scanner.scan(target)
            results["sca"] = sca_results
            results["scanners_run"].append("SCA")

        if include_secrets:
            from ...scanners.secret_scanner import SecretScanner
            scanner = SecretScanner()
            secret_results = await scanner.scan(target)
            results["secrets"] = secret_results
            results["scanners_run"].append("Secrets")

        if include_iac:
            from ...scanners.iac_scanner import IaCScanner
            scanner = IaCScanner()
            iac_results = await scanner.scan(target)
            results["iac"] = iac_results
            results["scanners_run"].append("IaC")

        return results

    except Exception as e:
        logger.error(f"Comprehensive scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Scanner Info Endpoints
@router.get("/available", response_model=Dict[str, Any])
async def get_available_scanners():
    """Get list of available scanners."""
    return {
        "success": True,
        "scanners": [
            {
                "id": "sca",
                "name": "SCA Scanner",
                "description": "Software Composition Analysis for dependencies"
            },
            {
                "id": "secrets",
                "name": "Secret Scanner",
                "description": "Detect hardcoded secrets and credentials"
            },
            {
                "id": "container",
                "name": "Container Scanner",
                "description": "Docker image and Dockerfile security"
            },
            {
                "id": "iac",
                "name": "IaC Scanner",
                "description": "Infrastructure as Code security analysis"
            },
            {
                "id": "code",
                "name": "ML Code Scanner",
                "description": "ML-powered vulnerability detection"
            }
        ]
    }


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Scanner service health check."""
    return {
        "status": "healthy",
        "service": "scanners",
        "version": "1.0.0"
    }
