"""
CI/CD API Routes - Pipeline Integration Endpoints

This module provides REST API endpoints for CI/CD pipeline integrations
including webhook handlers and scan management.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel, Field

from ...services.cicd_service import (
    get_cicd_service,
    CICDService,
    PipelineProvider,
    ScanTrigger,
    PipelineScanConfig
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cicd", tags=["CI/CD Integration"])


# Request Models
class ManualScanRequest(BaseModel):
    """Request for manual scan trigger."""
    provider: str = Field(..., description="CI/CD provider")
    repository: str = Field(..., description="Repository full name")
    branch: str = Field(..., description="Branch name")
    commit_sha: str = Field(..., description="Commit SHA")
    pr_number: int = Field(default=None, description="PR/MR number")
    workspace: str = Field(default=None, description="Workspace (Bitbucket)")
    installation_id: int = Field(default=None, description="Installation ID (GitHub)")
    project_id: int = Field(default=None, description="Project ID (GitLab)")
    scan_type: str = Field(default="quick", description="Scan type")
    fail_on_severity: str = Field(default="high", description="Fail threshold")


# Dependency
async def get_service() -> CICDService:
    """Get CI/CD service instance."""
    return get_cicd_service()


# Webhook Endpoints
@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
    service: CICDService = Depends(get_service)
):
    """
    Handle GitHub webhook events.

    Processes push, pull_request, and check_suite events
    to trigger security scans.
    """
    try:
        payload = await request.json()
        body = await request.body()

        # Verify signature
        await service.initialize()
        if not service._github_app.verify_webhook_signature(body, x_hub_signature_256 or ""):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Handle webhook
        result = await service._github_app.handle_webhook(x_github_event, payload)

        # Trigger scan if needed
        if result.get("action") in ["scan_push", "scan_pull_request"]:
            config = PipelineScanConfig(
                provider=PipelineProvider.GITHUB_ACTIONS,
                repository=result.get("repository") or result.get("full_name", ""),
                branch=result.get("branch", "main"),
                commit_sha=result.get("head_sha") or result.get("commit_sha", ""),
                trigger=ScanTrigger.PULL_REQUEST if "pr" in result.get("action", "") else ScanTrigger.PUSH,
                pr_number=result.get("pr_number"),
                installation_id=result.get("installation_id")
            )

            scan_result = await service.trigger_scan(config)
            return {
                "status": "scan_triggered",
                "scan_id": scan_result.scan_id,
                "vulnerabilities": scan_result.vulnerabilities_count
            }

        return {"status": "processed", "result": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/gitlab")
async def gitlab_webhook(
    request: Request,
    x_gitlab_event: str = Header(..., alias="X-Gitlab-Event"),
    x_gitlab_token: str = Header(None, alias="X-Gitlab-Token"),
    service: CICDService = Depends(get_service)
):
    """
    Handle GitLab webhook events.

    Processes push, merge_request, and pipeline events
    to trigger security scans.
    """
    try:
        payload = await request.json()
        body = await request.body()

        # Verify token
        await service.initialize()
        if not service._gitlab_ci.verify_webhook_signature(body, x_gitlab_token or ""):
            raise HTTPException(status_code=401, detail="Invalid token")

        # Handle webhook
        result = await service._gitlab_ci.handle_webhook(x_gitlab_event, payload)

        # Trigger scan if needed
        if result.get("action") in ["scan_push", "scan_merge_request"]:
            config = PipelineScanConfig(
                provider=PipelineProvider.GITLAB_CI,
                repository=result.get("project_path", ""),
                branch=result.get("branch") or result.get("source_branch", "main"),
                commit_sha=result.get("commit_sha") or result.get("last_commit_sha", ""),
                trigger=ScanTrigger.MERGE_REQUEST if "merge" in result.get("action", "") else ScanTrigger.PUSH,
                pr_number=result.get("mr_iid"),
                project_id=result.get("project_id")
            )

            scan_result = await service.trigger_scan(config)
            return {
                "status": "scan_triggered",
                "scan_id": scan_result.scan_id,
                "vulnerabilities": scan_result.vulnerabilities_count
            }

        return {"status": "processed", "result": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitLab webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/bitbucket")
async def bitbucket_webhook(
    request: Request,
    x_event_key: str = Header(..., alias="X-Event-Key"),
    x_hub_signature: str = Header(None, alias="X-Hub-Signature"),
    service: CICDService = Depends(get_service)
):
    """
    Handle Bitbucket webhook events.

    Processes push and pullrequest events to trigger security scans.
    """
    try:
        payload = await request.json()
        body = await request.body()

        # Verify signature
        await service.initialize()
        if not service._bitbucket.verify_webhook_signature(body, x_hub_signature or ""):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Handle webhook
        result = await service._bitbucket.handle_webhook(x_event_key, payload)

        # Trigger scan if needed
        if result.get("action") in ["scan_push", "scan_pull_request"]:
            config = PipelineScanConfig(
                provider=PipelineProvider.BITBUCKET_PIPELINES,
                repository=f"{result.get('workspace')}/{result.get('repo_slug')}",
                branch=result.get("source_branch") or result.get("commits", [{}])[0].get("branch", "main"),
                commit_sha=result.get("source_commit") or result.get("commits", [{}])[0].get("hash", ""),
                trigger=ScanTrigger.PULL_REQUEST if "pull" in result.get("action", "") else ScanTrigger.PUSH,
                pr_number=result.get("pr_id"),
                workspace=result.get("workspace")
            )

            scan_result = await service.trigger_scan(config)
            return {
                "status": "scan_triggered",
                "scan_id": scan_result.scan_id,
                "vulnerabilities": scan_result.vulnerabilities_count
            }

        return {"status": "processed", "result": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bitbucket webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Manual Scan Endpoints
@router.post("/scan/trigger", response_model=Dict[str, Any])
async def trigger_manual_scan(
    request: ManualScanRequest,
    service: CICDService = Depends(get_service)
):
    """
    Manually trigger a security scan.

    Use this endpoint to trigger a scan outside of webhook events.
    """
    try:
        config = PipelineScanConfig(
            provider=PipelineProvider(request.provider),
            repository=request.repository,
            branch=request.branch,
            commit_sha=request.commit_sha,
            trigger=ScanTrigger.MANUAL,
            pr_number=request.pr_number,
            workspace=request.workspace,
            installation_id=request.installation_id,
            project_id=request.project_id,
            scan_type=request.scan_type,
            fail_on_severity=request.fail_on_severity
        )

        result = await service.trigger_scan(config)

        return {
            "success": True,
            "scan_id": result.scan_id,
            "status": result.status.value,
            "vulnerabilities_count": result.vulnerabilities_count,
            "critical": result.critical_count,
            "high": result.high_count,
            "medium": result.medium_count,
            "low": result.low_count,
            "should_block": result.should_block,
            "scan_time_ms": result.scan_time_ms
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Manual scan trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scans/active", response_model=Dict[str, Any])
async def get_active_scans(
    service: CICDService = Depends(get_service)
):
    """Get list of active scans."""
    try:
        scans = service.get_active_scans()
        return {
            "success": True,
            "count": len(scans),
            "scans": scans
        }
    except Exception as e:
        logger.error(f"Get active scans failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Configuration Endpoints
@router.get("/config/github-actions", response_model=Dict[str, Any])
async def get_github_actions_config(
    service: CICDService = Depends(get_service)
):
    """Get GitHub Actions workflow configuration."""
    return {
        "success": True,
        "filename": ".github/workflows/security-scan.yml",
        "content": service.generate_github_actions_yaml()
    }


@router.get("/config/gitlab-ci", response_model=Dict[str, Any])
async def get_gitlab_ci_config(
    service: CICDService = Depends(get_service)
):
    """Get GitLab CI configuration."""
    return {
        "success": True,
        "filename": ".gitlab-ci.yml",
        "content": service.generate_gitlab_ci_yaml()
    }


@router.get("/config/bitbucket-pipelines", response_model=Dict[str, Any])
async def get_bitbucket_pipelines_config(
    service: CICDService = Depends(get_service)
):
    """Get Bitbucket Pipelines configuration."""
    return {
        "success": True,
        "filename": "bitbucket-pipelines.yml",
        "content": service.generate_bitbucket_pipelines_yaml()
    }


@router.get("/providers", response_model=Dict[str, Any])
async def get_supported_providers():
    """Get list of supported CI/CD providers."""
    return {
        "success": True,
        "providers": [
            {
                "id": "github_actions",
                "name": "GitHub Actions",
                "webhook_url": "/api/cicd/webhooks/github"
            },
            {
                "id": "gitlab_ci",
                "name": "GitLab CI/CD",
                "webhook_url": "/api/cicd/webhooks/gitlab"
            },
            {
                "id": "bitbucket_pipelines",
                "name": "Bitbucket Pipelines",
                "webhook_url": "/api/cicd/webhooks/bitbucket"
            }
        ]
    }


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """CI/CD service health check."""
    return {
        "status": "healthy",
        "service": "cicd_integration",
        "version": "1.0.0",
        "features": {
            "github_actions": True,
            "gitlab_ci": True,
            "bitbucket_pipelines": True,
            "inline_comments": True,
            "quality_gates": True
        }
    }
