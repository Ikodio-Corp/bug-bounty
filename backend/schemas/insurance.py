"""
Insurance schemas - Pydantic models for insurance-related requests/responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class CompanySize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class IndustryRisk(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ClaimStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class PremiumCalculationRequest(BaseModel):
    coverage_amount: float = Field(..., gt=0)
    company_size: CompanySize
    industry_risk: IndustryRisk
    previous_incidents: int = Field(0, ge=0)
    has_security_team: bool = True


class PremiumCalculationResponse(BaseModel):
    base_rate: float
    risk_multiplier: float
    annual_premium: float
    monthly_premium: float
    coverage_amount: float
    breakdown: dict


class PolicyCreateRequest(BaseModel):
    coverage_amount: float = Field(..., gt=0)
    premium_amount: float = Field(..., gt=0)
    duration_days: int = Field(365, ge=30, le=1095)
    company_size: CompanySize
    industry_risk: IndustryRisk


class PolicyResponse(BaseModel):
    policy_id: int
    company_id: int
    coverage_amount: float
    premium_amount: float
    status: PolicyStatus
    start_date: datetime
    end_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClaimCreateRequest(BaseModel):
    policy_id: int
    incident_description: str = Field(..., min_length=50)
    estimated_damage: float = Field(..., gt=0)
    incident_date: datetime
    supporting_documents: Optional[list] = None


class ClaimResponse(BaseModel):
    claim_id: int
    policy_id: int
    company_id: int
    incident_description: str
    estimated_damage: float
    approved_amount: Optional[float]
    status: ClaimStatus
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
