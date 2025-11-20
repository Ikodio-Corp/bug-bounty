"""
Scan schemas - Pydantic models for scan-related requests/responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ScanType(str, Enum):
    NUCLEI = "nuclei"
    ZAP = "zap"
    BURP = "burp"
    CUSTOM = "custom"
    FULL = "full"


class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanCreate(BaseModel):
    target_url: str = Field(..., min_length=5)
    scan_type: ScanType
    options: Optional[Dict[str, Any]] = None
    deep_scan: bool = False
    
    @validator('target_url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class ScanResponse(BaseModel):
    scan_id: int
    target_url: str
    scan_type: ScanType
    status: ScanStatus
    progress: float
    vulnerabilities_found: int
    start_time: datetime
    end_time: Optional[datetime]
    user_id: int
    
    class Config:
        from_attributes = True


class VulnerabilityDetail(BaseModel):
    name: str
    severity: str
    description: str
    affected_url: str
    proof: Optional[str]
    remediation: Optional[str]
    cvss_score: Optional[float]


class ScanResultResponse(BaseModel):
    scan_id: int
    target_url: str
    status: ScanStatus
    total_vulnerabilities: int
    critical: int
    high: int
    medium: int
    low: int
    info: int
    vulnerabilities: List[VulnerabilityDetail]
    scan_duration_seconds: Optional[float]
    
    class Config:
        from_attributes = True
