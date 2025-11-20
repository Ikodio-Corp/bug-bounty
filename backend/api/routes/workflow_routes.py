"""
Bug Workflow API Routes - Bug Lifecycle Management Endpoints

This module provides REST API endpoints for bug validation workflow
including state transitions, assignments, and SLA tracking.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...services.bug_workflow import (
    get_workflow_service,
    BugWorkflowService,
    BugStatus,
    BugSeverity
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflow", tags=["Bug Workflow"])


# Request Models
class CreateBugRequest(BaseModel):
    """Request to create bug report."""
    title: str = Field(..., description="Bug title")
    description: str = Field(..., description="Bug description")
    program_id: str = Field(..., description="Program ID")
    vulnerability_type: str = Field(default="", description="Vulnerability type")
    affected_component: str = Field(default="", description="Affected component")
    reproduction_steps: str = Field(default="", description="Steps to reproduce")
    proof_of_concept: str = Field(default="", description="POC code")
    impact: str = Field(default="", description="Impact description")
    suggested_fix: str = Field(default="", description="Suggested fix")
    tags: List[str] = Field(default=[], description="Tags")


class TransitionRequest(BaseModel):
    """Request to transition bug state."""
    to_state: str = Field(..., description="Target state")
    user_id: str = Field(..., description="User performing transition")
    user_role: str = Field(..., description="User role")
    comment: Optional[str] = Field(None, description="Transition comment")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


class AssignRequest(BaseModel):
    """Request to assign bug."""
    assignee_id: str = Field(..., description="Assignee user ID")
    assigned_by: str = Field(..., description="Assigner user ID")


class SeverityUpdateRequest(BaseModel):
    """Request to update severity."""
    severity: str = Field(..., description="New severity")
    cvss_score: Optional[float] = Field(None, description="CVSS score")
    user_id: str = Field(..., description="User ID")


class CommentRequest(BaseModel):
    """Request to add comment."""
    user_id: str = Field(..., description="User ID")
    comment: str = Field(..., description="Comment text")
    is_internal: bool = Field(default=False, description="Internal comment")


# Dependency
async def get_service() -> BugWorkflowService:
    """Get workflow service."""
    return get_workflow_service()


# Bug CRUD Endpoints
@router.post("/bugs", response_model=Dict[str, Any])
async def create_bug(
    request: CreateBugRequest,
    reporter_id: str = Query(..., description="Reporter user ID"),
    service: BugWorkflowService = Depends(get_service)
):
    """
    Create a new bug report.

    Automatically scores severity and priority based on vulnerability type.
    """
    try:
        bug = service.create_bug(request.dict(), reporter_id)

        return {
            "success": True,
            "bug_id": bug.id,
            "status": bug.status.value,
            "severity": bug.severity.value,
            "priority": bug.priority.value
        }

    except Exception as e:
        logger.error(f"Create bug failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bugs/{bug_id}", response_model=Dict[str, Any])
async def get_bug(
    bug_id: str,
    service: BugWorkflowService = Depends(get_service)
):
    """Get bug details."""
    try:
        bug = service.get_bug(bug_id)
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")

        return {
            "success": True,
            "bug": {
                "id": bug.id,
                "title": bug.title,
                "description": bug.description,
                "status": bug.status.value,
                "severity": bug.severity.value,
                "priority": bug.priority.value,
                "reporter_id": bug.reporter_id,
                "assignee_id": bug.assignee_id,
                "program_id": bug.program_id,
                "vulnerability_type": bug.vulnerability_type,
                "affected_component": bug.affected_component,
                "cvss_score": bug.cvss_score,
                "reward_amount": float(bug.reward_amount) if bug.reward_amount else None,
                "created_at": bug.created_at.isoformat(),
                "updated_at": bug.updated_at.isoformat(),
                "validated_at": bug.validated_at.isoformat() if bug.validated_at else None,
                "resolved_at": bug.resolved_at.isoformat() if bug.resolved_at else None,
                "duplicate_of": bug.duplicate_of,
                "tags": bug.tags,
                "history_count": len(bug.history)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get bug failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bugs/{bug_id}/history", response_model=Dict[str, Any])
async def get_bug_history(
    bug_id: str,
    service: BugWorkflowService = Depends(get_service)
):
    """Get bug workflow history."""
    try:
        bug = service.get_bug(bug_id)
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")

        return {
            "success": True,
            "bug_id": bug_id,
            "history": [
                {
                    "action": h.action,
                    "user_id": h.user_id,
                    "timestamp": h.timestamp.isoformat(),
                    "comment": h.comment,
                    "data": h.data
                }
                for h in bug.history
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get bug history failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# State Transition Endpoints
@router.post("/bugs/{bug_id}/transition", response_model=Dict[str, Any])
async def transition_bug(
    bug_id: str,
    request: TransitionRequest,
    service: BugWorkflowService = Depends(get_service)
):
    """
    Transition bug to new state.

    Validates transition based on current state and user role.
    """
    try:
        to_state = BugStatus(request.to_state)

        bug = service.transition(
            bug_id=bug_id,
            to_state=to_state,
            user_id=request.user_id,
            user_role=request.user_role,
            comment=request.comment,
            data=request.data
        )

        return {
            "success": True,
            "bug_id": bug.id,
            "new_status": bug.status.value,
            "message": f"Bug transitioned to {bug.status.value}"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Transition bug failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bugs/{bug_id}/transitions", response_model=Dict[str, Any])
async def get_available_transitions(
    bug_id: str,
    user_role: str = Query(..., description="User role"),
    service: BugWorkflowService = Depends(get_service)
):
    """Get available state transitions for bug."""
    try:
        transitions = service.get_available_transitions(bug_id, user_role)

        return {
            "success": True,
            "bug_id": bug_id,
            "available_transitions": transitions
        }

    except Exception as e:
        logger.error(f"Get transitions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Assignment Endpoints
@router.post("/bugs/{bug_id}/assign", response_model=Dict[str, Any])
async def assign_bug(
    bug_id: str,
    request: AssignRequest,
    service: BugWorkflowService = Depends(get_service)
):
    """Assign bug to user."""
    try:
        bug = service.assign(bug_id, request.assignee_id, request.assigned_by)

        return {
            "success": True,
            "bug_id": bug.id,
            "assignee_id": bug.assignee_id,
            "message": "Bug assigned successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Assign bug failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Severity and Scoring Endpoints
@router.put("/bugs/{bug_id}/severity", response_model=Dict[str, Any])
async def update_severity(
    bug_id: str,
    request: SeverityUpdateRequest,
    service: BugWorkflowService = Depends(get_service)
):
    """Update bug severity and CVSS score."""
    try:
        severity = BugSeverity(request.severity)

        bug = service.update_severity(
            bug_id=bug_id,
            severity=severity,
            cvss_score=request.cvss_score,
            user_id=request.user_id
        )

        return {
            "success": True,
            "bug_id": bug.id,
            "severity": bug.severity.value,
            "priority": bug.priority.value,
            "cvss_score": bug.cvss_score
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Update severity failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Comment Endpoints
@router.post("/bugs/{bug_id}/comments", response_model=Dict[str, Any])
async def add_comment(
    bug_id: str,
    request: CommentRequest,
    service: BugWorkflowService = Depends(get_service)
):
    """Add comment to bug."""
    try:
        bug = service.add_comment(
            bug_id=bug_id,
            user_id=request.user_id,
            comment=request.comment,
            is_internal=request.is_internal
        )

        return {
            "success": True,
            "bug_id": bug.id,
            "message": "Comment added"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Add comment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# SLA Endpoints
@router.get("/bugs/{bug_id}/sla", response_model=Dict[str, Any])
async def get_sla_status(
    bug_id: str,
    service: BugWorkflowService = Depends(get_service)
):
    """Get SLA status for bug."""
    try:
        sla = service.get_sla_status(bug_id)

        if not sla:
            raise HTTPException(status_code=404, detail="Bug not found")

        return {
            "success": True,
            **sla
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get SLA status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Query Endpoints
@router.get("/bugs/by-status/{status}", response_model=Dict[str, Any])
async def get_bugs_by_status(
    status: str,
    service: BugWorkflowService = Depends(get_service)
):
    """Get bugs by status."""
    try:
        bug_status = BugStatus(status)
        bugs = service.get_bugs_by_status(bug_status)

        return {
            "success": True,
            "status": status,
            "count": len(bugs),
            "bugs": [
                {
                    "id": b.id,
                    "title": b.title,
                    "severity": b.severity.value,
                    "priority": b.priority.value,
                    "created_at": b.created_at.isoformat()
                }
                for b in bugs
            ]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Get bugs by status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bugs/by-program/{program_id}", response_model=Dict[str, Any])
async def get_bugs_by_program(
    program_id: str,
    service: BugWorkflowService = Depends(get_service)
):
    """Get bugs by program."""
    try:
        bugs = service.get_bugs_by_program(program_id)

        return {
            "success": True,
            "program_id": program_id,
            "count": len(bugs),
            "bugs": [
                {
                    "id": b.id,
                    "title": b.title,
                    "status": b.status.value,
                    "severity": b.severity.value,
                    "created_at": b.created_at.isoformat()
                }
                for b in bugs
            ]
        }

    except Exception as e:
        logger.error(f"Get bugs by program failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Statistics Endpoints
@router.get("/stats", response_model=Dict[str, Any])
async def get_workflow_stats(
    program_id: Optional[str] = Query(None, description="Filter by program"),
    service: BugWorkflowService = Depends(get_service)
):
    """Get workflow statistics."""
    try:
        stats = service.get_workflow_stats(program_id)

        return {
            "success": True,
            **stats
        }

    except Exception as e:
        logger.error(f"Get workflow stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statuses", response_model=Dict[str, Any])
async def get_all_statuses():
    """Get all available bug statuses."""
    return {
        "success": True,
        "statuses": [
            {"id": s.value, "name": s.name}
            for s in BugStatus
        ]
    }


@router.get("/severities", response_model=Dict[str, Any])
async def get_all_severities():
    """Get all available severity levels."""
    return {
        "success": True,
        "severities": [
            {"id": s.value, "name": s.name}
            for s in BugSeverity
        ]
    }
