"""
VCS Integration Routes
GitHub Apps and GitLab Integration
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from core.database import get_db
from core.security import get_current_user
from integrations.vcs_integration import GitHubIntegration, GitLabIntegration
from models.user import User

router = APIRouter(prefix="/vcs", tags=["VCS Integration"])


class GitHubWebhookPayload(BaseModel):
    """GitHub webhook payload model"""
    action: str
    repository: Dict[str, Any]
    pull_request: Optional[Dict[str, Any]] = None
    push: Optional[Dict[str, Any]] = None


class GitLabWebhookPayload(BaseModel):
    """GitLab webhook payload model"""
    object_kind: str
    project: Dict[str, Any]
    merge_request: Optional[Dict[str, Any]] = None


class ConnectGitHubRequest(BaseModel):
    """Request to connect GitHub App"""
    installation_id: int
    app_id: str
    private_key: str


class ConnectGitLabRequest(BaseModel):
    """Request to connect GitLab"""
    private_token: str
    gitlab_url: Optional[str] = "https://gitlab.com"


class TriggerScanRequest(BaseModel):
    """Request to trigger scan on repository"""
    repository: str
    branch: str = "main"
    scan_type: str = "full"


@router.post("/github/connect")
async def connect_github(
    request: ConnectGitHubRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Connect GitHub App to user account
    
    Args:
        request: GitHub App credentials
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Connection status
    """
    try:
        github = GitHubIntegration(
            app_id=request.app_id,
            private_key=request.private_key,
            installation_id=request.installation_id
        )
        
        # Test connection by getting installation info
        installation = await github.get_installation()
        
        # Store GitHub connection info (you should create a VCSConnection model)
        # For now, return success
        
        return {
            "status": "connected",
            "platform": "github",
            "installation_id": request.installation_id,
            "account": installation.get("account", {}).get("login"),
            "repositories_count": installation.get("repository_selection")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to connect GitHub: {str(e)}"
        )


@router.post("/gitlab/connect")
async def connect_gitlab(
    request: ConnectGitLabRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Connect GitLab to user account
    
    Args:
        request: GitLab credentials
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Connection status
    """
    try:
        gitlab = GitLabIntegration(
            private_token=request.private_token,
            gitlab_url=request.gitlab_url
        )
        
        # Test connection by getting user info
        user_info = await gitlab.get_current_user()
        
        return {
            "status": "connected",
            "platform": "gitlab",
            "username": user_info.get("username"),
            "name": user_info.get("name"),
            "gitlab_url": request.gitlab_url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to connect GitLab: {str(e)}"
        )


@router.get("/github/repositories")
async def list_github_repositories(
    installation_id: int,
    app_id: str,
    private_key: str,
    current_user: User = Depends(get_current_user)
):
    """
    List accessible GitHub repositories
    
    Args:
        installation_id: GitHub App installation ID
        app_id: GitHub App ID
        private_key: GitHub App private key
        current_user: Authenticated user
        
    Returns:
        dict: List of repositories
    """
    try:
        github = GitHubIntegration(
            app_id=app_id,
            private_key=private_key,
            installation_id=installation_id
        )
        
        repositories = await github.list_repositories()
        
        return {
            "total": len(repositories),
            "repositories": repositories
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to list repositories: {str(e)}"
        )


@router.get("/gitlab/projects")
async def list_gitlab_projects(
    private_token: str,
    gitlab_url: str = "https://gitlab.com",
    current_user: User = Depends(get_current_user)
):
    """
    List accessible GitLab projects
    
    Args:
        private_token: GitLab private token
        gitlab_url: GitLab instance URL
        current_user: Authenticated user
        
    Returns:
        dict: List of projects
    """
    try:
        gitlab = GitLabIntegration(
            private_token=private_token,
            gitlab_url=gitlab_url
        )
        
        projects = await gitlab.list_projects()
        
        return {
            "total": len(projects),
            "projects": projects
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to list projects: {str(e)}"
        )


@router.post("/github/scan")
async def trigger_github_scan(
    request: TriggerScanRequest,
    installation_id: int = Body(...),
    app_id: str = Body(...),
    private_key: str = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger security scan on GitHub repository
    
    Args:
        request: Scan configuration
        installation_id: GitHub App installation ID
        app_id: GitHub App ID
        private_key: GitHub App private key
        current_user: Authenticated user
        
    Returns:
        dict: Scan status
    """
    try:
        github = GitHubIntegration(
            app_id=app_id,
            private_key=private_key,
            installation_id=installation_id
        )
        
        # Create check run for the scan
        owner, repo = request.repository.split("/")
        
        check_run = await github.create_check_run(
            owner=owner,
            repo=repo,
            name="IKODIO Security Scan",
            head_sha=request.branch,
            status="in_progress",
            output={
                "title": "Security Scan in Progress",
                "summary": f"Running {request.scan_type} security scan..."
            }
        )
        
        # TODO: Actually trigger the scan using your scanner orchestrator
        # For now, return check run info
        
        return {
            "status": "started",
            "repository": request.repository,
            "branch": request.branch,
            "scan_type": request.scan_type,
            "check_run_id": check_run["id"],
            "message": "Security scan initiated"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger scan: {str(e)}"
        )


@router.post("/gitlab/scan")
async def trigger_gitlab_scan(
    request: TriggerScanRequest,
    private_token: str = Body(...),
    project_id: int = Body(...),
    gitlab_url: str = Body(default="https://gitlab.com"),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger security scan on GitLab project
    
    Args:
        request: Scan configuration
        private_token: GitLab private token
        project_id: GitLab project ID
        gitlab_url: GitLab instance URL
        current_user: Authenticated user
        
    Returns:
        dict: Scan status
    """
    try:
        gitlab = GitLabIntegration(
            private_token=private_token,
            gitlab_url=gitlab_url
        )
        
        # Trigger pipeline with security scan
        pipeline = await gitlab.trigger_pipeline(
            project_id=project_id,
            ref=request.branch,
            variables={
                "SCAN_TYPE": request.scan_type,
                "IKODIO_SCAN": "true"
            }
        )
        
        return {
            "status": "started",
            "project_id": project_id,
            "branch": request.branch,
            "scan_type": request.scan_type,
            "pipeline_id": pipeline["id"],
            "pipeline_url": pipeline["web_url"],
            "message": "Security scan pipeline triggered"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger scan: {str(e)}"
        )


@router.post("/github/webhook")
async def github_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    GitHub webhook handler
    
    Args:
        request: FastAPI request with webhook payload
        db: Database session
        
    Returns:
        dict: Success response
    """
    try:
        # Get webhook signature
        signature = request.headers.get("X-Hub-Signature-256")
        
        # TODO: Verify webhook signature
        # github = GitHubIntegration(...)
        # is_valid = github.verify_webhook_signature(payload, signature)
        
        # Get event type
        event_type = request.headers.get("X-GitHub-Event")
        
        # Parse payload
        import json
        payload = await request.body()
        data = json.loads(payload)
        
        # Handle different event types
        if event_type == "push":
            # Handle push event - trigger scan
            repository = data.get("repository", {}).get("full_name")
            branch = data.get("ref", "").replace("refs/heads/", "")
            
            return {
                "status": "received",
                "event": event_type,
                "repository": repository,
                "branch": branch,
                "message": "Push event received, scan will be triggered"
            }
        
        elif event_type == "pull_request":
            # Handle PR event - trigger scan on PR
            action = data.get("action")
            pr_number = data.get("pull_request", {}).get("number")
            
            return {
                "status": "received",
                "event": event_type,
                "action": action,
                "pr_number": pr_number,
                "message": "PR event received"
            }
        
        else:
            return {
                "status": "received",
                "event": event_type,
                "message": f"Event {event_type} received but not handled"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.post("/gitlab/webhook")
async def gitlab_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    GitLab webhook handler
    
    Args:
        request: FastAPI request with webhook payload
        db: Database session
        
    Returns:
        dict: Success response
    """
    try:
        # Get webhook token
        token = request.headers.get("X-Gitlab-Token")
        
        # TODO: Verify webhook token
        
        # Parse payload
        import json
        payload = await request.body()
        data = json.loads(payload)
        
        # Get event type
        object_kind = data.get("object_kind")
        
        # Handle different event types
        if object_kind == "push":
            # Handle push event
            project = data.get("project", {}).get("path_with_namespace")
            branch = data.get("ref", "").replace("refs/heads/", "")
            
            return {
                "status": "received",
                "event": object_kind,
                "project": project,
                "branch": branch,
                "message": "Push event received"
            }
        
        elif object_kind == "merge_request":
            # Handle MR event
            action = data.get("object_attributes", {}).get("action")
            mr_iid = data.get("object_attributes", {}).get("iid")
            
            return {
                "status": "received",
                "event": object_kind,
                "action": action,
                "mr_iid": mr_iid,
                "message": "Merge request event received"
            }
        
        elif object_kind == "pipeline":
            # Handle pipeline event
            pipeline_id = data.get("object_attributes", {}).get("id")
            status = data.get("object_attributes", {}).get("status")
            
            return {
                "status": "received",
                "event": object_kind,
                "pipeline_id": pipeline_id,
                "pipeline_status": status,
                "message": "Pipeline event received"
            }
        
        else:
            return {
                "status": "received",
                "event": object_kind,
                "message": f"Event {object_kind} received but not handled"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.get("/status")
async def get_vcs_connections(
    current_user: User = Depends(get_current_user)
):
    """
    Get VCS connection status for current user
    
    Args:
        current_user: Authenticated user
        
    Returns:
        dict: Connection status for all platforms
    """
    # TODO: Retrieve actual connection status from database
    return {
        "github": {
            "connected": False,
            "installation_id": None,
            "repositories": 0
        },
        "gitlab": {
            "connected": False,
            "gitlab_url": None,
            "projects": 0
        },
        "bitbucket": {
            "connected": False,
            "workspaces": 0
        }
    }
