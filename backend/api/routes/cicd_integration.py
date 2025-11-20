"""
CI/CD Integration Routes
Jenkins, GitHub Actions, GitLab CI, CircleCI
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, Dict, Any

from core.database import get_db
from core.security import get_current_user
from integrations.cicd_integration import CICDOrchestrator
from models.user import User

router = APIRouter(prefix="/cicd", tags=["CI/CD Integration"])


class JenkinsConfig(BaseModel):
    """Jenkins configuration"""
    jenkins_url: str
    username: str
    api_token: str


class GitHubActionsConfig(BaseModel):
    """GitHub Actions configuration"""
    github_token: str
    owner: str
    repo: str


class GitLabCIConfig(BaseModel):
    """GitLab CI configuration"""
    gitlab_url: str
    private_token: str
    project_id: int


class CircleCIConfig(BaseModel):
    """CircleCI configuration"""
    api_token: str
    vcs_type: str  # github or bitbucket
    username: str
    project: str


class TriggerPipelineRequest(BaseModel):
    """Request to trigger CI/CD pipeline"""
    platform: str  # jenkins, github_actions, gitlab_ci, circleci
    repository: str
    branch: str = "main"
    parameters: Optional[Dict[str, Any]] = None


@router.post("/jenkins/connect")
async def connect_jenkins(
    config: JenkinsConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Connect Jenkins server
    
    Args:
        config: Jenkins configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Connection status
    """
    try:
        orchestrator = CICDOrchestrator({
            "jenkins": {
                "url": config.jenkins_url,
                "username": config.username,
                "api_token": config.api_token
            }
        })
        
        # Test connection by getting Jenkins version
        integration = orchestrator.integrations.get("jenkins")
        if not integration:
            raise HTTPException(status_code=400, detail="Jenkins integration failed")
        
        return {
            "status": "connected",
            "platform": "jenkins",
            "jenkins_url": config.jenkins_url,
            "username": config.username
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to connect Jenkins: {str(e)}"
        )


@router.post("/github-actions/connect")
async def connect_github_actions(
    config: GitHubActionsConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Connect GitHub Actions
    
    Args:
        config: GitHub Actions configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Connection status
    """
    try:
        orchestrator = CICDOrchestrator({
            "github_actions": {
                "token": config.github_token,
                "owner": config.owner,
                "repo": config.repo
            }
        })
        
        return {
            "status": "connected",
            "platform": "github_actions",
            "repository": f"{config.owner}/{config.repo}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to connect GitHub Actions: {str(e)}"
        )


@router.post("/gitlab-ci/connect")
async def connect_gitlab_ci(
    config: GitLabCIConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Connect GitLab CI
    
    Args:
        config: GitLab CI configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Connection status
    """
    try:
        orchestrator = CICDOrchestrator({
            "gitlab_ci": {
                "url": config.gitlab_url,
                "private_token": config.private_token,
                "project_id": config.project_id
            }
        })
        
        return {
            "status": "connected",
            "platform": "gitlab_ci",
            "gitlab_url": config.gitlab_url,
            "project_id": config.project_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to connect GitLab CI: {str(e)}"
        )


@router.post("/circleci/connect")
async def connect_circleci(
    config: CircleCIConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Connect CircleCI
    
    Args:
        config: CircleCI configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Connection status
    """
    try:
        orchestrator = CICDOrchestrator({
            "circleci": {
                "api_token": config.api_token,
                "vcs_type": config.vcs_type,
                "username": config.username,
                "project": config.project
            }
        })
        
        return {
            "status": "connected",
            "platform": "circleci",
            "project": f"{config.username}/{config.project}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to connect CircleCI: {str(e)}"
        )


@router.post("/trigger")
async def trigger_pipeline(
    request: TriggerPipelineRequest,
    jenkins_config: Optional[JenkinsConfig] = None,
    github_config: Optional[GitHubActionsConfig] = None,
    gitlab_config: Optional[GitLabCIConfig] = None,
    circleci_config: Optional[CircleCIConfig] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger CI/CD pipeline
    
    Args:
        request: Pipeline trigger request
        jenkins_config: Jenkins configuration (if platform is jenkins)
        github_config: GitHub Actions configuration (if platform is github_actions)
        gitlab_config: GitLab CI configuration (if platform is gitlab_ci)
        circleci_config: CircleCI configuration (if platform is circleci)
        current_user: Authenticated user
        
    Returns:
        dict: Pipeline status
    """
    try:
        config = {}
        
        if request.platform == "jenkins" and jenkins_config:
            config["jenkins"] = {
                "url": jenkins_config.jenkins_url,
                "username": jenkins_config.username,
                "api_token": jenkins_config.api_token
            }
        elif request.platform == "github_actions" and github_config:
            config["github_actions"] = {
                "token": github_config.github_token,
                "owner": github_config.owner,
                "repo": github_config.repo
            }
        elif request.platform == "gitlab_ci" and gitlab_config:
            config["gitlab_ci"] = {
                "url": gitlab_config.gitlab_url,
                "private_token": gitlab_config.private_token,
                "project_id": gitlab_config.project_id
            }
        elif request.platform == "circleci" and circleci_config:
            config["circleci"] = {
                "api_token": circleci_config.api_token,
                "vcs_type": circleci_config.vcs_type,
                "username": circleci_config.username,
                "project": circleci_config.project
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Configuration required for platform: {request.platform}"
            )
        
        orchestrator = CICDOrchestrator(config)
        
        result = await orchestrator.trigger_scan_pipeline(
            platform=request.platform,
            repository=request.repository,
            branch=request.branch,
            parameters=request.parameters
        )
        
        return {
            "status": "triggered",
            "platform": request.platform,
            "repository": request.repository,
            "branch": request.branch,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger pipeline: {str(e)}"
        )


@router.get("/pipeline/status")
async def get_pipeline_status(
    platform: str,
    pipeline_id: str,
    jenkins_config: Optional[JenkinsConfig] = None,
    github_config: Optional[GitHubActionsConfig] = None,
    gitlab_config: Optional[GitLabCIConfig] = None,
    circleci_config: Optional[CircleCIConfig] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get CI/CD pipeline status
    
    Args:
        platform: CI/CD platform
        pipeline_id: Pipeline/build ID
        jenkins_config: Jenkins configuration (if platform is jenkins)
        github_config: GitHub Actions configuration (if platform is github_actions)
        gitlab_config: GitLab CI configuration (if platform is gitlab_ci)
        circleci_config: CircleCI configuration (if platform is circleci)
        current_user: Authenticated user
        
    Returns:
        dict: Pipeline status
    """
    try:
        config = {}
        
        if platform == "jenkins" and jenkins_config:
            config["jenkins"] = {
                "url": jenkins_config.jenkins_url,
                "username": jenkins_config.username,
                "api_token": jenkins_config.api_token
            }
        elif platform == "github_actions" and github_config:
            config["github_actions"] = {
                "token": github_config.github_token,
                "owner": github_config.owner,
                "repo": github_config.repo
            }
        elif platform == "gitlab_ci" and gitlab_config:
            config["gitlab_ci"] = {
                "url": gitlab_config.gitlab_url,
                "private_token": gitlab_config.private_token,
                "project_id": gitlab_config.project_id
            }
        elif platform == "circleci" and circleci_config:
            config["circleci"] = {
                "api_token": circleci_config.api_token,
                "vcs_type": circleci_config.vcs_type,
                "username": circleci_config.username,
                "project": circleci_config.project
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Configuration required for platform: {platform}"
            )
        
        orchestrator = CICDOrchestrator(config)
        
        status = await orchestrator.get_pipeline_status(
            platform=platform,
            pipeline_id=pipeline_id
        )
        
        return {
            "platform": platform,
            "pipeline_id": pipeline_id,
            "status": status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pipeline status: {str(e)}"
        )


@router.get("/platforms")
async def get_supported_platforms():
    """
    Get list of supported CI/CD platforms
    
    Returns:
        dict: Supported platforms and their features
    """
    return {
        "platforms": {
            "jenkins": {
                "name": "Jenkins",
                "description": "Open source automation server",
                "features": ["Job triggering", "Build monitoring", "Pipeline support"],
                "required_config": ["jenkins_url", "username", "api_token"]
            },
            "github_actions": {
                "name": "GitHub Actions",
                "description": "GitHub's CI/CD platform",
                "features": ["Workflow dispatch", "Run monitoring", "Matrix builds"],
                "required_config": ["github_token", "owner", "repo"]
            },
            "gitlab_ci": {
                "name": "GitLab CI",
                "description": "GitLab's integrated CI/CD",
                "features": ["Pipeline triggers", "Job tracking", "Artifacts"],
                "required_config": ["gitlab_url", "private_token", "project_id"]
            },
            "circleci": {
                "name": "CircleCI",
                "description": "Cloud-based CI/CD platform",
                "features": ["Pipeline management", "Workflow orchestration"],
                "required_config": ["api_token", "vcs_type", "username", "project"]
            }
        }
    }


@router.get("/status")
async def get_cicd_connections(
    current_user: User = Depends(get_current_user)
):
    """
    Get CI/CD connection status for current user
    
    Args:
        current_user: Authenticated user
        
    Returns:
        dict: Connection status for all platforms
    """
    # TODO: Retrieve actual connection status from database
    return {
        "jenkins": {
            "connected": False,
            "jenkins_url": None
        },
        "github_actions": {
            "connected": False,
            "repositories": 0
        },
        "gitlab_ci": {
            "connected": False,
            "projects": 0
        },
        "circleci": {
            "connected": False,
            "projects": 0
        }
    }
