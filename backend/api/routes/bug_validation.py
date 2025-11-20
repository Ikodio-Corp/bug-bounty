"""
Bug Validation Workflow Routes
Multi-stage validation, reviewer assignment, appeals
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.bug import Bug
from sqlalchemy import select

router = APIRouter(prefix="/validation", tags=["Bug Validation"])


class ValidationStage:
    """Validation stages"""
    SUBMITTED = "submitted"
    TRIAGING = "triaging"
    VALIDATING = "validating"
    VERIFIED = "verified"
    REJECTED = "rejected"
    APPEALED = "appealed"


class SubmitValidationRequest(BaseModel):
    """Request to submit bug for validation"""
    bug_id: int
    evidence: Optional[str] = None
    poc_steps: Optional[List[str]] = None


class AssignReviewerRequest(BaseModel):
    """Request to assign reviewer"""
    bug_id: int
    reviewer_id: int


class ValidationVoteRequest(BaseModel):
    """Request to vote on validation"""
    bug_id: int
    vote: str
    comments: str


class AppealRequest(BaseModel):
    """Request to appeal rejection"""
    bug_id: int
    appeal_reason: str
    additional_evidence: Optional[str] = None


class ValidationChecklist(BaseModel):
    """Validation checklist"""
    reproducible: bool
    accurate_severity: bool
    clear_impact: bool
    valid_poc: bool
    not_duplicate: bool


@router.post("/submit")
async def submit_for_validation(
    request: SubmitValidationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit bug for validation workflow
    
    Args:
        request: Validation submission request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Validation status
    """
    try:
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        if bug.hunter_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only submit your own bugs for validation"
            )
        
        # Update bug status to validation stage
        bug.status = ValidationStage.TRIAGING
        bug.validation_submitted_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "submitted",
            "bug_id": request.bug_id,
            "validation_stage": ValidationStage.TRIAGING,
            "message": "Bug submitted for validation. A reviewer will be assigned shortly."
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Validation submission failed: {str(e)}"
        )


@router.post("/assign-reviewer")
async def assign_reviewer(
    request: AssignReviewerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign reviewer to bug validation
    
    Admin only endpoint
    
    Args:
        request: Reviewer assignment request
        current_user: Authenticated user (must be admin)
        db: Database session
        
    Returns:
        dict: Assignment status
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admins can assign reviewers"
            )
        
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        # Verify reviewer exists
        reviewer_result = await db.execute(
            select(User).where(User.id == request.reviewer_id)
        )
        reviewer = reviewer_result.scalar_one_or_none()
        
        if not reviewer:
            raise HTTPException(status_code=404, detail="Reviewer not found")
        
        # Assign reviewer
        bug.reviewer_id = request.reviewer_id
        bug.status = ValidationStage.VALIDATING
        bug.validation_assigned_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "assigned",
            "bug_id": request.bug_id,
            "reviewer_id": request.reviewer_id,
            "reviewer_name": reviewer.username,
            "validation_stage": ValidationStage.VALIDATING
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Reviewer assignment failed: {str(e)}"
        )


@router.post("/vote")
async def submit_validation_vote(
    request: ValidationVoteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit validation vote
    
    Args:
        request: Validation vote request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Vote status
    """
    try:
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        # Check if user is assigned reviewer
        if bug.reviewer_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not assigned as reviewer for this bug"
            )
        
        # Record vote
        if request.vote.lower() == "approve":
            bug.status = ValidationStage.VERIFIED
            bug.validated_at = datetime.utcnow()
            message = "Bug validated successfully"
        elif request.vote.lower() == "reject":
            bug.status = ValidationStage.REJECTED
            bug.rejected_at = datetime.utcnow()
            message = "Bug rejected"
        else:
            raise HTTPException(status_code=400, detail="Invalid vote")
        
        bug.validation_comments = request.comments
        
        await db.commit()
        
        return {
            "status": "recorded",
            "bug_id": request.bug_id,
            "vote": request.vote,
            "validation_stage": bug.status,
            "message": message
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Vote submission failed: {str(e)}"
        )


@router.post("/checklist")
async def submit_validation_checklist(
    bug_id: int = Body(...),
    checklist: ValidationChecklist = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit validation checklist
    
    Args:
        bug_id: Bug ID
        checklist: Validation checklist
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Checklist status
    """
    try:
        result = await db.execute(
            select(Bug).where(Bug.id == bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        # Check if user is assigned reviewer
        if bug.reviewer_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not assigned as reviewer for this bug"
            )
        
        # Calculate checklist score
        checklist_dict = checklist.dict()
        passed_checks = sum(1 for v in checklist_dict.values() if v)
        total_checks = len(checklist_dict)
        score = (passed_checks / total_checks) * 100
        
        # Auto-approve if all checks pass
        if score == 100:
            bug.status = ValidationStage.VERIFIED
            bug.validated_at = datetime.utcnow()
        elif score < 60:
            bug.status = ValidationStage.REJECTED
            bug.rejected_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "submitted",
            "bug_id": bug_id,
            "checklist_score": score,
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "validation_stage": bug.status,
            "checklist_details": checklist_dict
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Checklist submission failed: {str(e)}"
        )


@router.post("/appeal")
async def submit_appeal(
    request: AppealRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit appeal for rejected bug
    
    Args:
        request: Appeal request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Appeal status
    """
    try:
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        if bug.hunter_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only appeal your own bugs"
            )
        
        if bug.status != ValidationStage.REJECTED:
            raise HTTPException(
                status_code=400,
                detail="Only rejected bugs can be appealed"
            )
        
        # Submit appeal
        bug.status = ValidationStage.APPEALED
        bug.appeal_reason = request.appeal_reason
        bug.appeal_submitted_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "appealed",
            "bug_id": request.bug_id,
            "validation_stage": ValidationStage.APPEALED,
            "message": "Appeal submitted. A senior reviewer will review your case."
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Appeal submission failed: {str(e)}"
        )


@router.get("/status/{bug_id}")
async def get_validation_status(
    bug_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get validation status for bug
    
    Args:
        bug_id: Bug ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Validation status details
    """
    try:
        result = await db.execute(
            select(Bug).where(Bug.id == bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        # Get reviewer info if assigned
        reviewer_info = None
        if bug.reviewer_id:
            reviewer_result = await db.execute(
                select(User).where(User.id == bug.reviewer_id)
            )
            reviewer = reviewer_result.scalar_one_or_none()
            if reviewer:
                reviewer_info = {
                    "id": reviewer.id,
                    "username": reviewer.username
                }
        
        return {
            "bug_id": bug_id,
            "validation_stage": bug.status,
            "submitted_at": bug.validation_submitted_at.isoformat() if bug.validation_submitted_at else None,
            "assigned_at": bug.validation_assigned_at.isoformat() if bug.validation_assigned_at else None,
            "validated_at": bug.validated_at.isoformat() if bug.validated_at else None,
            "rejected_at": bug.rejected_at.isoformat() if bug.rejected_at else None,
            "reviewer": reviewer_info,
            "comments": bug.validation_comments,
            "can_appeal": bug.status == ValidationStage.REJECTED and not bug.appeal_submitted_at
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get validation status: {str(e)}"
        )


@router.get("/pending")
async def get_pending_validations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pending validation requests
    
    For reviewers: Get bugs assigned to them
    For admins: Get all pending validations
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Pending validations
    """
    try:
        if current_user.role == "admin":
            # Get all bugs in validation stages
            result = await db.execute(
                select(Bug).where(
                    Bug.status.in_([
                        ValidationStage.TRIAGING,
                        ValidationStage.VALIDATING,
                        ValidationStage.APPEALED
                    ])
                )
            )
        else:
            # Get bugs assigned to current user
            result = await db.execute(
                select(Bug).where(
                    Bug.reviewer_id == current_user.id,
                    Bug.status == ValidationStage.VALIDATING
                )
            )
        
        bugs = result.scalars().all()
        
        pending = []
        for bug in bugs:
            hunter_result = await db.execute(
                select(User).where(User.id == bug.hunter_id)
            )
            hunter = hunter_result.scalar_one_or_none()
            
            pending.append({
                "bug_id": bug.id,
                "title": bug.title,
                "severity": bug.severity,
                "status": bug.status,
                "hunter": hunter.username if hunter else None,
                "submitted_at": bug.validation_submitted_at.isoformat() if bug.validation_submitted_at else None
            })
        
        return {
            "total": len(pending),
            "pending_validations": pending
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pending validations: {str(e)}"
        )


@router.get("/metrics")
async def get_validation_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get validation metrics
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Validation metrics
    """
    try:
        # Get total validations
        total_result = await db.execute(
            select(Bug).where(
                Bug.status.in_([
                    ValidationStage.VERIFIED,
                    ValidationStage.REJECTED
                ])
            )
        )
        total_validations = len(total_result.scalars().all())
        
        # Get verified count
        verified_result = await db.execute(
            select(Bug).where(Bug.status == ValidationStage.VERIFIED)
        )
        verified_count = len(verified_result.scalars().all())
        
        # Get rejected count
        rejected_result = await db.execute(
            select(Bug).where(Bug.status == ValidationStage.REJECTED)
        )
        rejected_count = len(rejected_result.scalars().all())
        
        # Get pending count
        pending_result = await db.execute(
            select(Bug).where(
                Bug.status.in_([
                    ValidationStage.TRIAGING,
                    ValidationStage.VALIDATING
                ])
            )
        )
        pending_count = len(pending_result.scalars().all())
        
        # Get appeals count
        appeals_result = await db.execute(
            select(Bug).where(Bug.status == ValidationStage.APPEALED)
        )
        appeals_count = len(appeals_result.scalars().all())
        
        acceptance_rate = (verified_count / total_validations * 100) if total_validations > 0 else 0
        
        return {
            "total_validations": total_validations,
            "verified": verified_count,
            "rejected": rejected_count,
            "pending": pending_count,
            "appeals": appeals_count,
            "acceptance_rate": round(acceptance_rate, 2),
            "average_validation_time": 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics: {str(e)}"
        )
