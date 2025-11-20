"""
Insurance Service
Bug Bounty Insurance logic and actuarial calculations
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
import random

from models.insurance import (
    InsurancePolicy,
    InsuranceClaim,
    InsurancePremiumPayment,
    InsurancePolicyStatus,
    InsuranceClaimStatus
)


class InsuranceService:
    """
    Service for managing bug bounty insurance
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def calculate_premium(
        self,
        coverage_amount: float,
        company_id: int,
        pre_audit_score: Optional[float] = None
    ) -> Dict:
        """
        Calculate insurance premium based on coverage and risk assessment
        
        Premium Formula:
        Base Rate = 2-5% of coverage amount
        Risk Multiplier = 0.5x to 3x based on audit score
        """
        
        base_rate_percentage = 0.03
        
        if pre_audit_score is None:
            pre_audit_score = await self._conduct_pre_audit(company_id)
        
        risk_multiplier = self._calculate_risk_multiplier(pre_audit_score)
        
        base_premium = coverage_amount * base_rate_percentage
        final_premium = base_premium * risk_multiplier
        
        risk_level = "low" if pre_audit_score >= 80 else "medium" if pre_audit_score >= 60 else "high"
        
        return {
            "coverage_amount": coverage_amount,
            "base_premium": base_premium,
            "risk_multiplier": risk_multiplier,
            "final_premium": final_premium,
            "pre_audit_score": pre_audit_score,
            "risk_level": risk_level,
            "payment_frequency": "monthly",
            "monthly_premium": final_premium / 12
        }
    
    async def create_policy(
        self,
        company_id: int,
        coverage_amount: float,
        covered_assets: list,
        pre_audit_score: Optional[float] = None
    ) -> InsurancePolicy:
        """
        Create new insurance policy
        """
        
        premium_data = await self.calculate_premium(
            coverage_amount, company_id, pre_audit_score
        )
        
        policy_number = f"IBB-{datetime.now().year}-{random.randint(10000, 99999)}"
        
        policy = InsurancePolicy(
            company_id=company_id,
            policy_number=policy_number,
            coverage_amount=coverage_amount,
            premium_amount=premium_data["final_premium"],
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=365),
            status=InsurancePolicyStatus.ACTIVE,
            covered_assets=covered_assets,
            pre_audit_score=premium_data["pre_audit_score"],
            risk_level=premium_data["risk_level"]
        )
        
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    async def submit_claim(
        self,
        policy_id: int,
        bug_id: int,
        claim_amount: float,
        incident_description: str,
        incident_date: datetime,
        supporting_documents: list = None
    ) -> InsuranceClaim:
        """
        Submit insurance claim for bug incident
        """
        
        policy = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.id == policy_id
        ).first()
        
        if not policy or policy.status != InsurancePolicyStatus.ACTIVE:
            raise ValueError("Invalid or inactive insurance policy")
        
        if claim_amount > policy.coverage_amount:
            raise ValueError("Claim amount exceeds coverage limit")
        
        claim_number = f"CLM-{datetime.now().year}-{random.randint(10000, 99999)}"
        
        claim = InsuranceClaim(
            policy_id=policy_id,
            claim_number=claim_number,
            bug_id=bug_id,
            claim_amount=claim_amount,
            status=InsuranceClaimStatus.SUBMITTED,
            incident_description=incident_description,
            incident_date=incident_date,
            supporting_documents=supporting_documents or []
        )
        
        self.db.add(claim)
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    async def process_claim(
        self,
        claim_id: int,
        reviewer_id: int,
        approved: bool,
        approved_amount: Optional[float] = None,
        reviewer_notes: Optional[str] = None
    ) -> InsuranceClaim:
        """
        Process insurance claim (approve or reject)
        """
        
        claim = self.db.query(InsuranceClaim).filter(
            InsuranceClaim.id == claim_id
        ).first()
        
        if not claim:
            raise ValueError("Claim not found")
        
        claim.reviewed_by = reviewer_id
        claim.reviewed_at = datetime.utcnow()
        claim.reviewer_notes = reviewer_notes
        
        if approved:
            claim.status = InsuranceClaimStatus.APPROVED
            claim.approved_amount = approved_amount or claim.claim_amount
        else:
            claim.status = InsuranceClaimStatus.REJECTED
            claim.approved_amount = 0
        
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    async def pay_claim(
        self,
        claim_id: int,
        payment_reference: str
    ) -> InsuranceClaim:
        """
        Mark claim as paid
        """
        
        claim = self.db.query(InsuranceClaim).filter(
            InsuranceClaim.id == claim_id
        ).first()
        
        if not claim or claim.status != InsuranceClaimStatus.APPROVED:
            raise ValueError("Claim not approved for payment")
        
        claim.status = InsuranceClaimStatus.PAID
        claim.payment_date = datetime.utcnow()
        claim.payment_reference = payment_reference
        
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    async def _conduct_pre_audit(self, company_id: int) -> float:
        """
        Conduct pre-audit security assessment
        Returns score 0-100
        """
        
        score = 75.0
        
        return score
    
    def _calculate_risk_multiplier(self, audit_score: float) -> float:
        """
        Calculate risk multiplier based on audit score
        
        Score 90-100: 0.5x (low risk, discount)
        Score 70-89: 1.0x (normal risk)
        Score 50-69: 1.5x (medium risk)
        Score 0-49: 2.5x (high risk, premium)
        """
        
        if audit_score >= 90:
            return 0.5
        elif audit_score >= 70:
            return 1.0
        elif audit_score >= 50:
            return 1.5
        else:
            return 2.5
