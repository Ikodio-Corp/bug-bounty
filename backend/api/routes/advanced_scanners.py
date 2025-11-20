"""
Advanced Scanner Routes
SCA, Secret Detection, Container, IaC Scanning
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import tempfile
import os

from core.database import get_db
from core.security import get_current_user
from scanners.sca_scanner import SCAScanner
from scanners.secret_scanner import SecretScanner
from scanners.container_scanner import ContainerScanner
from scanners.iac_scanner import IaCScanner
from models.user import User

router = APIRouter(prefix="/scanners", tags=["Advanced Scanners"])


class SCAScanRequest(BaseModel):
    """Request model for SCA scanning"""
    repository_path: str
    package_managers: Optional[List[str]] = None


class SecretScanRequest(BaseModel):
    """Request model for secret scanning"""
    directory: str
    file_extensions: Optional[List[str]] = None


class ContainerScanRequest(BaseModel):
    """Request model for container scanning"""
    dockerfile_path: Optional[str] = None
    image_name: Optional[str] = None


class IaCScanRequest(BaseModel):
    """Request model for IaC scanning"""
    directory: str
    file_types: Optional[List[str]] = None


@router.post("/sca/scan")
async def scan_dependencies(
    request: SCAScanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform Software Composition Analysis (SCA) scan
    
    Scans dependencies for known vulnerabilities
    
    Args:
        request: SCA scan configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Vulnerability findings from dependencies
    """
    try:
        scanner = SCAScanner()
        
        results = await scanner.scan(
            repository_path=request.repository_path,
            package_managers=request.package_managers
        )
        
        # Store scan results in database
        # TODO: Create ScanResult model and save
        
        return {
            "scan_type": "sca",
            "status": "completed",
            "repository": request.repository_path,
            "total_dependencies": results.get("total_dependencies", 0),
            "vulnerable_dependencies": results.get("vulnerable_dependencies", 0),
            "vulnerabilities": results.get("vulnerabilities", []),
            "license_issues": results.get("license_issues", []),
            "summary": {
                "critical": sum(
                    1 for v in results.get("vulnerabilities", [])
                    if v.get("severity") == "critical"
                ),
                "high": sum(
                    1 for v in results.get("vulnerabilities", [])
                    if v.get("severity") == "high"
                ),
                "medium": sum(
                    1 for v in results.get("vulnerabilities", [])
                    if v.get("severity") == "medium"
                ),
                "low": sum(
                    1 for v in results.get("vulnerabilities", [])
                    if v.get("severity") == "low"
                )
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SCA scan failed: {str(e)}"
        )


@router.post("/sca/scan-file")
async def scan_dependency_file(
    file: UploadFile = File(...),
    package_manager: str = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Scan single dependency file
    
    Args:
        file: Dependency file (package.json, requirements.txt, etc.)
        package_manager: Package manager type (npm, pip, maven, etc.)
        current_user: Authenticated user
        
    Returns:
        dict: Vulnerability findings
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            scanner = SCAScanner()
            
            # Create temporary directory with the file
            tmp_dir = tempfile.mkdtemp()
            file_path = os.path.join(tmp_dir, file.filename)
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            results = await scanner.scan(
                repository_path=tmp_dir,
                package_managers=[package_manager]
            )
            
            # Cleanup
            os.remove(file_path)
            os.rmdir(tmp_dir)
            
            return {
                "scan_type": "sca",
                "status": "completed",
                "file": file.filename,
                "package_manager": package_manager,
                "vulnerabilities": results.get("vulnerabilities", []),
                "total_dependencies": results.get("total_dependencies", 0),
                "vulnerable_dependencies": results.get("vulnerable_dependencies", 0)
            }
            
        finally:
            os.remove(tmp_path)
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File scan failed: {str(e)}"
        )


@router.post("/secrets/scan")
async def scan_secrets(
    request: SecretScanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Scan for hardcoded secrets and credentials
    
    Args:
        request: Secret scan configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Detected secrets and credentials
    """
    try:
        scanner = SecretScanner()
        
        results = await scanner.scan(
            directory=request.directory,
            file_extensions=request.file_extensions
        )
        
        return {
            "scan_type": "secret",
            "status": "completed",
            "directory": request.directory,
            "files_scanned": results.get("files_scanned", 0),
            "secrets_found": len(results.get("secrets", [])),
            "secrets": results.get("secrets", []),
            "summary": {
                "high_risk": sum(
                    1 for s in results.get("secrets", [])
                    if s.get("severity") == "high"
                ),
                "medium_risk": sum(
                    1 for s in results.get("secrets", [])
                    if s.get("severity") == "medium"
                ),
                "low_risk": sum(
                    1 for s in results.get("secrets", [])
                    if s.get("severity") == "low"
                )
            },
            "recommendations": results.get("recommendations", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Secret scan failed: {str(e)}"
        )


@router.post("/secrets/scan-file")
async def scan_file_for_secrets(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Scan single file for secrets
    
    Args:
        file: File to scan
        current_user: Authenticated user
        
    Returns:
        dict: Detected secrets
    """
    try:
        scanner = SecretScanner()
        content = await file.read()
        
        secrets = scanner.scan_content(
            content=content.decode('utf-8'),
            filename=file.filename
        )
        
        return {
            "scan_type": "secret",
            "status": "completed",
            "file": file.filename,
            "secrets_found": len(secrets),
            "secrets": secrets
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File scan failed: {str(e)}"
        )


@router.post("/container/scan")
async def scan_container(
    request: ContainerScanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Scan Docker container or Dockerfile for security issues
    
    Args:
        request: Container scan configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Container security findings
    """
    try:
        scanner = ContainerScanner()
        
        results = await scanner.scan(
            dockerfile_path=request.dockerfile_path,
            image_name=request.image_name
        )
        
        return {
            "scan_type": "container",
            "status": "completed",
            "dockerfile": request.dockerfile_path,
            "image": request.image_name,
            "issues_found": len(results.get("issues", [])),
            "issues": results.get("issues", []),
            "summary": {
                "critical": sum(
                    1 for i in results.get("issues", [])
                    if i.get("severity") == "critical"
                ),
                "high": sum(
                    1 for i in results.get("issues", [])
                    if i.get("severity") == "high"
                ),
                "medium": sum(
                    1 for i in results.get("issues", [])
                    if i.get("severity") == "medium"
                ),
                "low": sum(
                    1 for i in results.get("issues", [])
                    if i.get("severity") == "low"
                )
            },
            "recommendations": results.get("recommendations", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Container scan failed: {str(e)}"
        )


@router.post("/container/scan-dockerfile")
async def scan_dockerfile_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Scan uploaded Dockerfile
    
    Args:
        file: Dockerfile to scan
        current_user: Authenticated user
        
    Returns:
        dict: Security findings
    """
    try:
        # Save uploaded Dockerfile temporarily
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.dockerfile') as tmp:
            content = await file.read()
            tmp.write(content.decode('utf-8'))
            tmp_path = tmp.name
        
        try:
            scanner = ContainerScanner()
            results = await scanner.scan(dockerfile_path=tmp_path)
            
            return {
                "scan_type": "container",
                "status": "completed",
                "file": file.filename,
                "issues_found": len(results.get("issues", [])),
                "issues": results.get("issues", []),
                "recommendations": results.get("recommendations", [])
            }
            
        finally:
            os.remove(tmp_path)
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dockerfile scan failed: {str(e)}"
        )


@router.post("/iac/scan")
async def scan_infrastructure(
    request: IaCScanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Scan Infrastructure as Code for misconfigurations
    
    Supports: Terraform, Kubernetes, CloudFormation
    
    Args:
        request: IaC scan configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Infrastructure security findings
    """
    try:
        scanner = IaCScanner()
        
        results = await scanner.scan(
            directory=request.directory,
            file_types=request.file_types
        )
        
        return {
            "scan_type": "iac",
            "status": "completed",
            "directory": request.directory,
            "files_scanned": results.get("files_scanned", 0),
            "issues_found": len(results.get("issues", [])),
            "issues": results.get("issues", []),
            "summary": {
                "critical": sum(
                    1 for i in results.get("issues", [])
                    if i.get("severity") == "critical"
                ),
                "high": sum(
                    1 for i in results.get("issues", [])
                    if i.get("severity") == "high"
                ),
                "medium": sum(
                    1 for i in results.get("issues", [])
                    if i.get("severity") == "medium"
                ),
                "low": sum(
                    1 for i in results.get("issues", [])
                    if i.get("severity") == "low"
                )
            },
            "by_type": {
                "terraform": results.get("terraform_issues", 0),
                "kubernetes": results.get("kubernetes_issues", 0),
                "cloudformation": results.get("cloudformation_issues", 0)
            },
            "recommendations": results.get("recommendations", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"IaC scan failed: {str(e)}"
        )


@router.post("/iac/scan-file")
async def scan_iac_file(
    file: UploadFile = File(...),
    file_type: str = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Scan single IaC file
    
    Args:
        file: IaC file (Terraform, K8s manifest, CloudFormation)
        file_type: Type of IaC file (terraform, kubernetes, cloudformation)
        current_user: Authenticated user
        
    Returns:
        dict: Security findings
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            scanner = IaCScanner()
            
            # Create temporary directory with the file
            tmp_dir = tempfile.mkdtemp()
            file_path = os.path.join(tmp_dir, file.filename)
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            results = await scanner.scan(
                directory=tmp_dir,
                file_types=[file_type]
            )
            
            # Cleanup
            os.remove(file_path)
            os.rmdir(tmp_dir)
            
            return {
                "scan_type": "iac",
                "status": "completed",
                "file": file.filename,
                "file_type": file_type,
                "issues_found": len(results.get("issues", [])),
                "issues": results.get("issues", []),
                "recommendations": results.get("recommendations", [])
            }
            
        finally:
            os.remove(tmp_path)
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"IaC file scan failed: {str(e)}"
        )


@router.get("/supported-types")
async def get_supported_scanner_types():
    """
    Get list of supported scanner types and their capabilities
    
    Returns:
        dict: Scanner types and configurations
    """
    return {
        "scanners": {
            "sca": {
                "name": "Software Composition Analysis",
                "description": "Scan dependencies for known vulnerabilities",
                "package_managers": [
                    "pip", "npm", "maven", "gradle", "bundler", "composer", "go", "cargo"
                ],
                "output": ["vulnerabilities", "licenses", "outdated_packages"]
            },
            "secret": {
                "name": "Secret Detection",
                "description": "Detect hardcoded secrets and credentials",
                "patterns": [
                    "AWS keys", "API tokens", "Private keys", "Database URLs",
                    "OAuth tokens", "JWT tokens", "SSH keys", "Passwords"
                ],
                "file_types": [".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env"]
            },
            "container": {
                "name": "Container Security",
                "description": "Scan Docker containers and images",
                "checks": [
                    "Base image vulnerabilities", "Dockerfile best practices",
                    "Exposed ports", "Running as root", "Secrets in layers"
                ]
            },
            "iac": {
                "name": "Infrastructure as Code",
                "description": "Scan IaC for misconfigurations",
                "supported": ["Terraform", "Kubernetes", "CloudFormation"],
                "checks": [
                    "Security misconfigurations", "Compliance violations",
                    "Best practices", "Resource policies"
                ]
            }
        }
    }
