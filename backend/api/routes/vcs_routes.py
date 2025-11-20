"""
VCS API Routes - Version Control System Integration Endpoints

This module provides REST API endpoints for VCS integrations
including repository management, file access, and PR/MR operations.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vcs", tags=["VCS Integration"])


# Request Models
class GitHubAppInstallRequest(BaseModel):
    """Request to install GitHub App."""
    installation_id: int = Field(..., description="Installation ID")
    repositories: List[str] = Field(default=[], description="Selected repositories")


class CreateCheckRunRequest(BaseModel):
    """Request to create GitHub Check Run."""
    repository: str = Field(..., description="Repository full name")
    head_sha: str = Field(..., description="Commit SHA")
    name: str = Field(default="Security Scan", description="Check name")


class PRCommentRequest(BaseModel):
    """Request to add PR comment."""
    repository: str = Field(..., description="Repository full name")
    pr_number: int = Field(..., description="PR/MR number")
    body: str = Field(..., description="Comment body")


class InlineCommentRequest(BaseModel):
    """Request for inline comment."""
    repository: str = Field(..., description="Repository full name")
    pr_number: int = Field(..., description="PR/MR number")
    file_path: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")
    body: str = Field(..., description="Comment body")
    commit_id: str = Field(..., description="Commit SHA")


class GetFileRequest(BaseModel):
    """Request to get file content."""
    repository: str = Field(..., description="Repository")
    file_path: str = Field(..., description="File path")
    ref: str = Field(default="main", description="Branch/tag/commit")


# GitHub Endpoints
@router.post("/github/check-run", response_model=Dict[str, Any])
async def create_github_check_run(
    request: CreateCheckRunRequest,
    installation_id: int = Query(..., description="Installation ID")
):
    """Create GitHub Check Run for a commit."""
    try:
        from ...integrations import create_github_app

        app = create_github_app()
        token = await app.get_installation_token(installation_id)

        result = await app.create_check_run(
            token=token,
            repository=request.repository,
            head_sha=request.head_sha,
            name=request.name
        )

        return {
            "success": True,
            "check_run_id": result.get("id"),
            "url": result.get("html_url")
        }

    except Exception as e:
        logger.error(f"Create check run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/github/pr-comment", response_model=Dict[str, Any])
async def create_github_pr_comment(
    request: PRCommentRequest,
    installation_id: int = Query(..., description="Installation ID")
):
    """Add comment to GitHub PR."""
    try:
        from ...integrations import create_github_app

        app = create_github_app()
        token = await app.get_installation_token(installation_id)

        result = await app.create_pr_comment(
            token=token,
            repository=request.repository,
            pr_number=request.pr_number,
            body=request.body
        )

        return {
            "success": True,
            "comment_id": result.get("id"),
            "url": result.get("html_url")
        }

    except Exception as e:
        logger.error(f"Create PR comment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/github/inline-comment", response_model=Dict[str, Any])
async def create_github_inline_comment(
    request: InlineCommentRequest,
    installation_id: int = Query(..., description="Installation ID")
):
    """Add inline comment to GitHub PR."""
    try:
        from ...integrations import create_github_app

        app = create_github_app()
        token = await app.get_installation_token(installation_id)

        result = await app.create_pr_review_comment(
            token=token,
            repository=request.repository,
            pr_number=request.pr_number,
            commit_id=request.commit_id,
            path=request.file_path,
            line=request.line,
            body=request.body
        )

        return {
            "success": True,
            "comment_id": result.get("id")
        }

    except Exception as e:
        logger.error(f"Create inline comment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/file", response_model=Dict[str, Any])
async def get_github_file(
    repository: str = Query(..., description="Repository full name"),
    file_path: str = Query(..., description="File path"),
    ref: str = Query(default="main", description="Branch/tag/commit"),
    installation_id: int = Query(..., description="Installation ID")
):
    """Get file content from GitHub repository."""
    try:
        from ...integrations import create_github_app

        app = create_github_app()
        token = await app.get_installation_token(installation_id)

        content = await app.get_file_content(
            token=token,
            repository=repository,
            file_path=file_path,
            ref=ref
        )

        return {
            "success": True,
            "file_path": file_path,
            "content": content
        }

    except Exception as e:
        logger.error(f"Get file failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# GitLab Endpoints
@router.post("/gitlab/mr-comment", response_model=Dict[str, Any])
async def create_gitlab_mr_comment(
    project_id: int = Query(..., description="Project ID"),
    mr_iid: int = Query(..., description="MR IID"),
    body: str = Query(..., description="Comment body"),
    token: str = Query(..., description="Access token")
):
    """Add comment to GitLab MR."""
    try:
        from ...integrations import create_gitlab_ci

        gitlab = create_gitlab_ci()
        result = await gitlab.create_mr_note(
            token=token,
            project_id=project_id,
            mr_iid=mr_iid,
            body=body
        )

        return {
            "success": True,
            "note_id": result.get("id")
        }

    except Exception as e:
        logger.error(f"Create MR comment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gitlab/commit-status", response_model=Dict[str, Any])
async def create_gitlab_commit_status(
    project_id: int = Query(..., description="Project ID"),
    sha: str = Query(..., description="Commit SHA"),
    state: str = Query(..., description="Status state"),
    name: str = Query(default="security-scan", description="Status name"),
    description: str = Query(default="", description="Description"),
    token: str = Query(..., description="Access token")
):
    """Create commit status in GitLab."""
    try:
        from ...integrations import create_gitlab_ci

        gitlab = create_gitlab_ci()
        result = await gitlab.create_commit_status(
            token=token,
            project_id=project_id,
            sha=sha,
            state=state,
            name=name,
            description=description
        )

        return {
            "success": True,
            "status_id": result.get("id")
        }

    except Exception as e:
        logger.error(f"Create commit status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gitlab/file", response_model=Dict[str, Any])
async def get_gitlab_file(
    project_id: int = Query(..., description="Project ID"),
    file_path: str = Query(..., description="File path"),
    ref: str = Query(default="main", description="Branch/tag/commit"),
    token: str = Query(..., description="Access token")
):
    """Get file content from GitLab repository."""
    try:
        from ...integrations import create_gitlab_ci

        gitlab = create_gitlab_ci()
        content = await gitlab.get_file_content(
            token=token,
            project_id=project_id,
            file_path=file_path,
            ref=ref
        )

        return {
            "success": True,
            "file_path": file_path,
            "content": content
        }

    except Exception as e:
        logger.error(f"Get file failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Bitbucket Endpoints
@router.post("/bitbucket/pr-comment", response_model=Dict[str, Any])
async def create_bitbucket_pr_comment(
    workspace: str = Query(..., description="Workspace slug"),
    repo_slug: str = Query(..., description="Repository slug"),
    pr_id: int = Query(..., description="PR ID"),
    content: str = Query(..., description="Comment content")
):
    """Add comment to Bitbucket PR."""
    try:
        from ...integrations import create_bitbucket_integration

        bitbucket = create_bitbucket_integration()
        token = await bitbucket.get_access_token()

        result = await bitbucket.create_pr_comment(
            token=token,
            workspace=workspace,
            repo_slug=repo_slug,
            pr_id=pr_id,
            content=content
        )

        return {
            "success": True,
            "comment_id": result.get("id")
        }

    except Exception as e:
        logger.error(f"Create PR comment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bitbucket/build-status", response_model=Dict[str, Any])
async def create_bitbucket_build_status(
    workspace: str = Query(..., description="Workspace slug"),
    repo_slug: str = Query(..., description="Repository slug"),
    commit: str = Query(..., description="Commit hash"),
    state: str = Query(..., description="Build state"),
    key: str = Query(default="security-scan", description="Status key"),
    name: str = Query(default="Security Scan", description="Status name"),
    description: str = Query(default="", description="Description")
):
    """Create build status in Bitbucket."""
    try:
        from ...integrations import create_bitbucket_integration, BuildState

        bitbucket = create_bitbucket_integration()
        token = await bitbucket.get_access_token()

        result = await bitbucket.create_build_status(
            token=token,
            workspace=workspace,
            repo_slug=repo_slug,
            commit=commit,
            state=BuildState(state),
            key=key,
            name=name,
            description=description
        )

        return {
            "success": True,
            "status": result
        }

    except Exception as e:
        logger.error(f"Create build status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bitbucket/file", response_model=Dict[str, Any])
async def get_bitbucket_file(
    workspace: str = Query(..., description="Workspace slug"),
    repo_slug: str = Query(..., description="Repository slug"),
    file_path: str = Query(..., description="File path"),
    ref: str = Query(default="main", description="Branch/tag/commit")
):
    """Get file content from Bitbucket repository."""
    try:
        from ...integrations import create_bitbucket_integration

        bitbucket = create_bitbucket_integration()
        token = await bitbucket.get_access_token()

        content = await bitbucket.get_file_content(
            token=token,
            workspace=workspace,
            repo_slug=repo_slug,
            file_path=file_path,
            ref=ref
        )

        return {
            "success": True,
            "file_path": file_path,
            "content": content
        }

    except Exception as e:
        logger.error(f"Get file failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Provider Info Endpoints
@router.get("/providers", response_model=Dict[str, Any])
async def get_vcs_providers():
    """Get list of supported VCS providers."""
    return {
        "success": True,
        "providers": [
            {
                "id": "github",
                "name": "GitHub",
                "features": ["apps", "check_runs", "pr_comments", "inline_comments"]
            },
            {
                "id": "gitlab",
                "name": "GitLab",
                "features": ["pipelines", "mr_discussions", "commit_status"]
            },
            {
                "id": "bitbucket",
                "name": "Bitbucket",
                "features": ["pipelines", "pr_comments", "build_status", "code_insights"]
            }
        ]
    }


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """VCS integration service health check."""
    return {
        "status": "healthy",
        "service": "vcs_integration",
        "version": "1.0.0"
    }
