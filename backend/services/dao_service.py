"""
DAO Governance Service
Decentralized governance and tokenomics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from models.dao import (
    DAOGovernance,
    DAOProposal,
    DAOVote,
    DAOToken,
    DAOTreasuryTransaction,
    ProposalStatus
)


class DAOService:
    """
    Service for DAO governance and IKOD token management
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_proposal(
        self,
        proposer_id: int,
        title: str,
        description: str,
        proposal_type: str,
        execution_data: Optional[Dict] = None
    ) -> DAOProposal:
        """
        Create new governance proposal
        """
        
        proposer_tokens = self.db.query(DAOToken).filter(
            DAOToken.user_id == proposer_id
        ).first()
        
        dao_config = await self._get_dao_config()
        
        if not proposer_tokens or proposer_tokens.token_balance < dao_config.min_proposal_tokens:
            raise ValueError(f"Insufficient tokens to create proposal. Need {dao_config.min_proposal_tokens} IKOD")
        
        proposal_number = f"PROP-{datetime.now().year}-{await self._get_next_proposal_number()}"
        
        proposal = DAOProposal(
            proposal_number=proposal_number,
            title=title,
            description=description,
            proposer_id=proposer_id,
            proposal_type=proposal_type,
            status=ProposalStatus.DRAFT,
            execution_data=execution_data
        )
        
        self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)
        
        return proposal
    
    async def start_voting(self, proposal_id: int) -> DAOProposal:
        """
        Start voting period for proposal
        """
        
        proposal = self.db.query(DAOProposal).filter(
            DAOProposal.id == proposal_id
        ).first()
        
        if not proposal:
            raise ValueError("Proposal not found")
        
        dao_config = await self._get_dao_config()
        
        proposal.status = ProposalStatus.ACTIVE
        proposal.voting_starts_at = datetime.utcnow()
        proposal.voting_ends_at = datetime.utcnow() + timedelta(hours=dao_config.voting_period_hours)
        
        total_supply = dao_config.circulating_supply
        proposal.total_voting_power = total_supply
        
        self.db.commit()
        self.db.refresh(proposal)
        
        return proposal
    
    async def cast_vote(
        self,
        proposal_id: int,
        voter_id: int,
        vote_choice: str,
        reason: Optional[str] = None
    ) -> DAOVote:
        """
        Cast vote on proposal
        
        vote_choice: "for", "against", "abstain"
        """
        
        proposal = self.db.query(DAOProposal).filter(
            DAOProposal.id == proposal_id
        ).first()
        
        if not proposal or proposal.status != ProposalStatus.ACTIVE:
            raise ValueError("Proposal not available for voting")
        
        if datetime.utcnow() > proposal.voting_ends_at:
            raise ValueError("Voting period has ended")
        
        existing_vote = self.db.query(DAOVote).filter(
            DAOVote.proposal_id == proposal_id,
            DAOVote.voter_id == voter_id
        ).first()
        
        if existing_vote:
            raise ValueError("Already voted on this proposal")
        
        voter_tokens = self.db.query(DAOToken).filter(
            DAOToken.user_id == voter_id
        ).first()
        
        if not voter_tokens or voter_tokens.voting_power <= 0:
            raise ValueError("No voting power")
        
        vote = DAOVote(
            proposal_id=proposal_id,
            voter_id=voter_id,
            vote_choice=vote_choice,
            voting_power=voter_tokens.voting_power,
            reason=reason
        )
        
        self.db.add(vote)
        
        if vote_choice == "for":
            proposal.votes_for += voter_tokens.voting_power
        elif vote_choice == "against":
            proposal.votes_against += voter_tokens.voting_power
        elif vote_choice == "abstain":
            proposal.votes_abstain += voter_tokens.voting_power
        
        self.db.commit()
        self.db.refresh(vote)
        
        return vote
    
    async def finalize_proposal(self, proposal_id: int) -> DAOProposal:
        """
        Finalize proposal after voting period ends
        """
        
        proposal = self.db.query(DAOProposal).filter(
            DAOProposal.id == proposal_id
        ).first()
        
        if not proposal:
            raise ValueError("Proposal not found")
        
        if datetime.utcnow() < proposal.voting_ends_at:
            raise ValueError("Voting period not ended")
        
        dao_config = await self._get_dao_config()
        
        total_votes = proposal.votes_for + proposal.votes_against + proposal.votes_abstain
        quorum_met = (total_votes / proposal.total_voting_power * 100) >= dao_config.quorum_percentage
        
        proposal.quorum_reached = quorum_met
        
        if quorum_met and proposal.votes_for > proposal.votes_against:
            proposal.status = ProposalStatus.PASSED
        else:
            proposal.status = ProposalStatus.REJECTED
        
        self.db.commit()
        self.db.refresh(proposal)
        
        return proposal
    
    async def execute_proposal(
        self,
        proposal_id: int,
        executor_id: int
    ) -> DAOProposal:
        """
        Execute passed proposal
        """
        
        proposal = self.db.query(DAOProposal).filter(
            DAOProposal.id == proposal_id
        ).first()
        
        if not proposal or proposal.status != ProposalStatus.PASSED:
            raise ValueError("Proposal not passed")
        
        proposal.status = ProposalStatus.EXECUTED
        proposal.executed_at = datetime.utcnow()
        proposal.executed_by = executor_id
        
        self.db.commit()
        self.db.refresh(proposal)
        
        return proposal
    
    async def distribute_tokens(
        self,
        user_id: int,
        amount: float,
        source: str
    ) -> DAOToken:
        """
        Distribute IKOD tokens to user
        
        source: "bug_bounty", "marketplace", "governance"
        """
        
        user_tokens = self.db.query(DAOToken).filter(
            DAOToken.user_id == user_id
        ).first()
        
        if not user_tokens:
            user_tokens = DAOToken(
                user_id=user_id,
                token_balance=0,
                staked_balance=0
            )
            self.db.add(user_tokens)
        
        user_tokens.token_balance += amount
        
        if source == "bug_bounty":
            user_tokens.earned_from_bug_bounties += amount
        elif source == "marketplace":
            user_tokens.earned_from_marketplace += amount
        elif source == "governance":
            user_tokens.earned_from_governance += amount
        
        user_tokens.voting_power = user_tokens.token_balance + user_tokens.staked_balance
        
        self.db.commit()
        self.db.refresh(user_tokens)
        
        return user_tokens
    
    async def stake_tokens(
        self,
        user_id: int,
        amount: float
    ) -> DAOToken:
        """
        Stake IKOD tokens to increase voting power
        """
        
        user_tokens = self.db.query(DAOToken).filter(
            DAOToken.user_id == user_id
        ).first()
        
        if not user_tokens or user_tokens.token_balance < amount:
            raise ValueError("Insufficient balance")
        
        user_tokens.token_balance -= amount
        user_tokens.staked_balance += amount
        user_tokens.voting_power = user_tokens.token_balance + user_tokens.staked_balance
        
        self.db.commit()
        self.db.refresh(user_tokens)
        
        return user_tokens
    
    async def get_treasury_balance(self) -> float:
        """
        Get current DAO treasury balance
        """
        
        dao_config = await self._get_dao_config()
        return dao_config.treasury_balance
    
    async def _get_dao_config(self) -> DAOGovernance:
        """
        Get DAO configuration
        """
        
        config = self.db.query(DAOGovernance).first()
        
        if not config:
            config = DAOGovernance()
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        
        return config
    
    async def _get_next_proposal_number(self) -> int:
        """
        Get next proposal number
        """
        
        last_proposal = self.db.query(DAOProposal).order_by(
            DAOProposal.id.desc()
        ).first()
        
        return (last_proposal.id + 1) if last_proposal else 1
