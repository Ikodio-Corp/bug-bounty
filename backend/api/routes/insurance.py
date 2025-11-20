"""
Insurance API Routes
Bug Bounty Insurance endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.security import get_current_user
from services.insurance_service import InsuranceService
from models.user import User


router = APIRouter(prefix="/api/insurance", tags=["Insurance"])


@router.post("/calculate-premium")
async def calculate_premium(
    coverage_amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate insurance premium for given coverage amount
    """
    
    service = InsuranceService(db)
    
    try:
        premium_data = await service.calculate_premium(
            coverage_amount=coverage_amount,
            company_id=current_user.id
        )
        
        return {
            "success": True,
            "data": premium_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/policies")
async def create_policy(
    coverage_amount: float,
    covered_assets: List[dict],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new insurance policy
    """
    
    service = InsuranceService(db)
    
    try:
        policy = await service.create_policy(
            company_id=current_user.id,
            coverage_amount=coverage_amount,
            covered_assets=covered_assets
        )
        
        return {
            "success": True,
            "data": {
                "policy_id": policy.id,
                "policy_number": policy.policy_number,
                "coverage_amount": policy.coverage_amount,
                "premium_amount": policy.premium_amount,
                "status": policy.status,
                "start_date": policy.start_date,
                "end_date": policy.end_date
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/claims")
async def submit_claim(
    policy_id: int,
    bug_id: int,
    claim_amount: float,
    incident_description: str,
    incident_date: str,
    supporting_documents: List[dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit insurance claim
    """
    
    service = InsuranceService(db)
    
    try:
        from datetime import datetime
        incident_datetime = datetime.fromisoformat(incident_date)
        
        claim = await service.submit_claim(
            policy_id=policy_id,
            bug_id=bug_id,
            claim_amount=claim_amount,
            incident_description=incident_description,
            incident_date=incident_datetime,
            supporting_documents=supporting_documents
        )
        
        return {
            "success": True,
            "data": {
                "claim_id": claim.id,
                "claim_number": claim.claim_number,
                "claim_amount": claim.claim_amount,
                "status": claim.status
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/claims/{claim_id}/process")
async def process_claim(
    claim_id: int,
    approved: bool,
    approved_amount: float = None,
    reviewer_notes: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process insurance claim (approve or reject)
    Admin only
    """
    
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = InsuranceService(db)
    
    try:
        claim = await service.process_claim(
            claim_id=claim_id,
            reviewer_id=current_user.id,
            approved=approved,
            approved_amount=approved_amount,
            reviewer_notes=reviewer_notes
        )
        
        return {
            "success": True,
            "data": {
                "claim_id": claim.id,
                "status": claim.status,
                "approved_amount": claim.approved_amount
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
