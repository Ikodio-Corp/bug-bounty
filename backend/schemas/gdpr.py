"""
GDPR Compliance Schemas - Request and response models
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ConsentPreferences(BaseModel):
    """User consent preferences"""
    marketing_emails: bool = Field(default=False, description="Consent to marketing communications")
    analytics: bool = Field(default=True, description="Consent to analytics and performance monitoring")
    third_party_sharing: bool = Field(default=False, description="Consent to share data with third parties")
    profiling: bool = Field(default=False, description="Consent to profiling and personalization")


class ConsentUpdate(BaseModel):
    """Update consent preferences"""
    marketing_emails: Optional[bool] = None
    analytics: Optional[bool] = None
    third_party_sharing: Optional[bool] = None
    profiling: Optional[bool] = None


class DataExportRequest(BaseModel):
    """Request data export"""
    format: str = Field(default="json", description="Export format: json or csv")
    include_audit_logs: bool = Field(default=True, description="Include audit logs in export")


class DataExportResponse(BaseModel):
    """Data export response"""
    user: Dict[str, Any]
    scans: List[Dict[str, Any]]
    bugs: List[Dict[str, Any]]
    payments: List[Dict[str, Any]]
    audit_logs: Optional[List[Dict[str, Any]]]
    export_date: str
    export_format: str


class AccountDeletionRequest(BaseModel):
    """Request account deletion"""
    reason: Optional[str] = Field(None, description="Reason for deletion")
    confirmation: bool = Field(..., description="User must confirm deletion")


class AccountDeletionResponse(BaseModel):
    """Account deletion response"""
    message: str
    grace_period_ends: str
    deletion_id: str


class ProcessingObjection(BaseModel):
    """Object to data processing"""
    processing_type: str = Field(..., description="Type: marketing, profiling, or automated_decision")
    reason: Optional[str] = Field(None, description="Reason for objection")


class DataRectificationRequest(BaseModel):
    """Request data rectification"""
    field: str = Field(..., description="Field to rectify")
    current_value: str = Field(..., description="Current incorrect value")
    requested_value: str = Field(..., description="Requested correct value")
    reason: str = Field(..., description="Reason for rectification")


class DataRectificationResponse(BaseModel):
    """Data rectification response"""
    message: str
    request_id: str
    status: str


class PrivacyPolicyResponse(BaseModel):
    """Privacy policy information"""
    version: str
    effective_date: str
    last_updated: str
    dpo_contact: EmailStr
    policy_url: str
    data_controller: Dict[str, str]
    data_protection_officer: Dict[str, str]
    user_rights: List[str]
    data_retention: Dict[str, str]


class AccessLogEntry(BaseModel):
    """Access log entry"""
    timestamp: str
    action: str
    ip_address: Optional[str]
    status: str


class UserActivity(BaseModel):
    """User activity summary"""
    user_id: int
    total_logins: int
    last_login: Optional[str]
    data_exports: int
    consent_changes: int
    security_events: int


class GDPRComplianceStatus(BaseModel):
    """GDPR compliance status"""
    compliant: bool
    last_audit: str
    data_processing_agreements: int
    consent_rate: float
    data_subject_requests_resolved: int
    average_response_time_hours: int


class DataProcessingRecord(BaseModel):
    """Record of processing activities"""
    id: int
    processing_activity: str
    purpose: str
    legal_basis: str
    data_categories: List[str]
    data_subjects: List[str]
    recipients: List[str]
    retention_period: str
    security_measures: List[str]
    created_at: str
    updated_at: str
