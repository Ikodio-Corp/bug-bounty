"""
DAO schemas - Pydantic models for DAO governance requests/responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ProposalType(str, Enum):
    FEATURE = "feature"
    PARAMETER_CHANGE = "parameter_change"
    TREASURY = "treasury"
    GOVERNANCE = "governance"


class ProposalStatus(str, Enum):
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"
    CANCELLED = "cancelled"


class VoteType(str, Enum):
    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"


class ProposalCreateRequest(BaseModel):
    title: str = Field(..., min_length=10, max_length=255)
    description: str = Field(..., min_length=50)
    proposal_type: ProposalType
    execution_data: Optional[dict] = None


class ProposalResponse(BaseModel):
    proposal_id: int
    title: str
    description: str
    proposal_type: ProposalType
    proposer_id: int
    status: ProposalStatus
    votes_for: int
    votes_against: int
    votes_abstain: int
    total_voting_power: int
    quorum_reached: bool
    created_at: datetime
    voting_ends_at: datetime
    
    class Config:
        from_attributes = True


class VoteCreateRequest(BaseModel):
    proposal_id: int
    vote_type: VoteType


class VoteResponse(BaseModel):
    vote_id: int
    proposal_id: int
    voter_id: int
    vote_type: VoteType
    voting_power: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenBalanceResponse(BaseModel):
    user_id: int
    balance: float
    staked_balance: float
    voting_power: int
    total_earned: float
    total_spent: float
    
    class Config:
        from_attributes = True


class StakeCreateRequest(BaseModel):
    amount: float = Field(..., gt=0)
    duration_days: int = Field(..., ge=30, le=1095)


class StakeResponse(BaseModel):
    stake_id: int
    user_id: int
    amount: float
    start_date: datetime
    end_date: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
