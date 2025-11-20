"""
Bug schemas - Pydantic models for bug-related requests/responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BugSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class BugStatus(str, Enum):
    SUBMITTED = "submitted"
    TRIAGING = "triaging"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    FIXED = "fixed"
    VERIFIED = "verified"
    CLOSED = "closed"


class BugCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=20)
    severity: BugSeverity
    vulnerability_type: str = Field(..., max_length=100)
    target_url: str
    proof_of_concept: str
    impact: str
    remediation: Optional[str] = None
    cvss_score: Optional[float] = Field(None, ge=0.0, le=10.0)


class BugUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = None
    severity: Optional[BugSeverity] = None
    status: Optional[BugStatus] = None
    vulnerability_type: Optional[str] = None
    remediation: Optional[str] = None


class BugResponse(BaseModel):
    bug_id: int
    title: str
    description: str
    severity: BugSeverity
    status: BugStatus
    vulnerability_type: str
    target_url: str
    cvss_score: Optional[float]
    reward_amount: Optional[float]
    hunter_id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BugListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    bugs: List[BugResponse]
