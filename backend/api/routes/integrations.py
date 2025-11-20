"""
Integration API routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from core.database import get_db
from middleware.auth import get_current_user
from models.user import User
from models.bug import Bug
from services.integration_service import IntegrationService

router = APIRouter()


class JiraIntegrationRequest(BaseModel):
    bug_id: int
    project_key: str
    issue_type: str = "Bug"


class LinearIntegrationRequest(BaseModel):
    bug_id: int
    team_id: str


class HackerOneIntegrationRequest(BaseModel):
    bug_id: int
    program_handle: str


class BugcrowdIntegrationRequest(BaseModel):
    bug_id: int
    program_code: str


@router.post("/integrations/jira/sync")
async def sync_to_jira(
    data: JiraIntegrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync bug to Jira"""
    bug = db.query(Bug).filter(Bug.id == data.bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    
    if bug.hunter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    bug_data = {
        "title": bug.title,
        "description": bug.description,
        "severity": bug.severity.value,
        "vulnerability_type": bug.bug_type.value
    }
    
    integration_service = IntegrationService()
    result = await integration_service.sync_to_jira(
        bug_data,
        data.project_key,
        data.issue_type
    )
    await integration_service.close()
    
    if result["success"]:
        bug.jira_issue_key = result["jira_issue_key"]
        bug.jira_issue_id = result["jira_issue_id"]
        db.commit()
    
    return result


@router.post("/integrations/linear/sync")
async def sync_to_linear(
    data: LinearIntegrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync bug to Linear"""
    bug = db.query(Bug).filter(Bug.id == data.bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    
    if bug.hunter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    bug_data = {
        "title": bug.title,
        "description": bug.description,
        "severity": bug.severity.value,
        "vulnerability_type": bug.bug_type.value
    }
    
    integration_service = IntegrationService()
    result = await integration_service.sync_to_linear(bug_data, data.team_id)
    await integration_service.close()
    
    if result["success"]:
        bug.linear_issue_id = result["linear_issue_id"]
        bug.linear_issue_identifier = result["linear_issue_identifier"]
        db.commit()
    
    return result


@router.post("/integrations/hackerone/sync")
async def sync_to_hackerone(
    data: HackerOneIntegrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync bug to HackerOne"""
    bug = db.query(Bug).filter(Bug.id == data.bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    
    if bug.hunter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    bug_data = {
        "title": bug.title,
        "description": bug.description,
        "severity": bug.severity.value,
        "vulnerability_type": bug.bug_type.value
    }
    
    integration_service = IntegrationService()
    result = await integration_service.sync_to_hackerone(
        bug_data,
        data.program_handle
    )
    await integration_service.close()
    
    if result["success"]:
        bug.platform_name = "hackerone"
        bug.platform_report_id = result["hackerone_report_id"]
        db.commit()
    
    return result


@router.post("/integrations/bugcrowd/sync")
async def sync_to_bugcrowd(
    data: BugcrowdIntegrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync bug to Bugcrowd"""
    bug = db.query(Bug).filter(Bug.id == data.bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    
    if bug.hunter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    bug_data = {
        "title": bug.title,
        "description": bug.description,
        "severity": bug.severity.value,
        "vulnerability_type": bug.bug_type.value,
        "target_url": bug.target_url
    }
    
    integration_service = IntegrationService()
    result = await integration_service.sync_to_bugcrowd(
        bug_data,
        data.program_code
    )
    await integration_service.close()
    
    if result["success"]:
        bug.platform_name = "bugcrowd"
        bug.platform_report_id = result["bugcrowd_submission_id"]
        db.commit()
    
    return result


@router.get("/integrations/status/{bug_id}")
async def get_integration_status(
    bug_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get integration status for a bug"""
    bug = db.query(Bug).filter(Bug.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    
    if bug.hunter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return {
        "bug_id": bug.id,
        "integrations": {
            "jira": {
                "synced": bug.jira_issue_key is not None,
                "issue_key": bug.jira_issue_key,
                "issue_id": bug.jira_issue_id
            },
            "linear": {
                "synced": bug.linear_issue_id is not None,
                "issue_id": bug.linear_issue_id,
                "identifier": bug.linear_issue_identifier
            },
            "platform": {
                "name": bug.platform_name,
                "report_id": bug.platform_report_id
            }
        }
    }
