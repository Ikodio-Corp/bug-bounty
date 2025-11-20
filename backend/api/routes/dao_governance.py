"""
DAO Governance API Routes
Decentralized governance and IKOD token endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.security import get_current_user
from services.dao_service import DAOService
from models.user import User


router = APIRouter(prefix="/api/dao", tags=["DAO"])


@router.post("/proposals")
async def create_proposal(
    title: str,
    description: str,
    proposal_type: str,
    execution_data: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new governance proposal
    Requires minimum IKOD tokens to propose
    """
    
    service = DAOService(db)
    
    try:
        proposal = await service.create_proposal(
            proposer_id=current_user.id,
            title=title,
            description=description,
            proposal_type=proposal_type,
            execution_data=execution_data
        )
        
        return {
            "success": True,
            "data": {
                "proposal_id": proposal.id,
                "proposal_number": proposal.proposal_number,
                "title": proposal.title,
                "status": proposal.status
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/proposals/{proposal_id}/start-voting")
async def start_voting(
    proposal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start voting period for proposal
    """
    
    service = DAOService(db)
    
    try:
        proposal = await service.start_voting(proposal_id)
        
        return {
            "success": True,
            "data": {
                "proposal_id": proposal.id,
                "status": proposal.status,
                "voting_starts_at": proposal.voting_starts_at,
                "voting_ends_at": proposal.voting_ends_at
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/proposals/{proposal_id}/vote")
async def cast_vote(
    proposal_id: int,
    vote_choice: str,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cast vote on proposal
    vote_choice: "for", "against", "abstain"
    """
    
    service = DAOService(db)
    
    try:
        vote = await service.cast_vote(
            proposal_id=proposal_id,
            voter_id=current_user.id,
            vote_choice=vote_choice,
            reason=reason
        )
        
        return {
            "success": True,
            "data": {
                "vote_id": vote.id,
                "proposal_id": vote.proposal_id,
                "vote_choice": vote.vote_choice,
                "voting_power": vote.voting_power
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/proposals")
async def get_proposals(
    status: str = "active",
    db: Session = Depends(get_db)
):
    """
    Get all proposals
    """
    
    from models.dao import DAOProposal
    
    proposals = db.query(DAOProposal).filter(
        DAOProposal.status == status
    ).all()
    
    return {
        "success": True,
        "data": [
            {
                "proposal_id": proposal.id,
                "proposal_number": proposal.proposal_number,
                "title": proposal.title,
                "status": proposal.status,
                "votes_for": proposal.votes_for,
                "votes_against": proposal.votes_against,
                "votes_abstain": proposal.votes_abstain,
                "voting_ends_at": proposal.voting_ends_at
            }
            for proposal in proposals
        ]
    }


@router.get("/proposals/{proposal_id}")
async def get_proposal(
    proposal_id: int,
    db: Session = Depends(get_db)
):
    """
    Get proposal details
    """
    
    from models.dao import DAOProposal
    
    proposal = db.query(DAOProposal).filter(
        DAOProposal.id == proposal_id
    ).first()
    
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    return {
        "success": True,
        "data": {
            "proposal_id": proposal.id,
            "proposal_number": proposal.proposal_number,
            "title": proposal.title,
            "description": proposal.description,
            "proposal_type": proposal.proposal_type,
            "status": proposal.status,
            "votes_for": proposal.votes_for,
            "votes_against": proposal.votes_against,
            "votes_abstain": proposal.votes_abstain,
            "quorum_reached": proposal.quorum_reached,
            "voting_starts_at": proposal.voting_starts_at,
            "voting_ends_at": proposal.voting_ends_at
        }
    }


@router.get("/tokens/balance")
async def get_token_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's IKOD token balance and voting power
    """
    
    from models.dao import DAOToken
    
    tokens = db.query(DAOToken).filter(
        DAOToken.user_id == current_user.id
    ).first()
    
    if not tokens:
        return {
            "success": True,
            "data": {
                "token_balance": 0,
                "staked_balance": 0,
                "voting_power": 0
            }
        }
    
    return {
        "success": True,
        "data": {
            "token_balance": tokens.token_balance,
            "staked_balance": tokens.staked_balance,
            "voting_power": tokens.voting_power,
            "earned_from_bug_bounties": tokens.earned_from_bug_bounties,
            "earned_from_marketplace": tokens.earned_from_marketplace,
            "earned_from_governance": tokens.earned_from_governance
        }
    }


@router.post("/tokens/stake")
async def stake_tokens(
    amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stake IKOD tokens to increase voting power
    """
    
    service = DAOService(db)
    
    try:
        tokens = await service.stake_tokens(
            user_id=current_user.id,
            amount=amount
        )
        
        return {
            "success": True,
            "data": {
                "token_balance": tokens.token_balance,
                "staked_balance": tokens.staked_balance,
                "voting_power": tokens.voting_power
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/treasury")
async def get_treasury(
    db: Session = Depends(get_db)
):
    """
    Get DAO treasury balance and statistics
    """
    
    service = DAOService(db)
    
    try:
        balance = await service.get_treasury_balance()
        
        return {
            "success": True,
            "data": {
                "treasury_balance": balance
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
