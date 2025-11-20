from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from core.database import get_db
from core.security import get_current_user
from models.user import User
from services.additional_features_service import (
    CertificateService,
    WebhookService,
    ReportService
)

router = APIRouter()


# Certificate Endpoints
@router.get("/users/certificates")
async def get_certificates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's certificates"""
    service = CertificateService(db)
    certificates = service.get_user_certificates(current_user.id)
    return certificates


@router.get("/users/certificates/{certificate_id}/download")
async def download_certificate(
    certificate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download certificate PDF"""
    service = CertificateService(db)
    pdf_data = service.generate_certificate_pdf(certificate_id, current_user.id)
    
    from fastapi.responses import Response
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=certificate-{certificate_id}.pdf"
        }
    )


@router.get("/certificates/verify/{credential_id}")
async def verify_certificate(
    credential_id: str,
    db: Session = Depends(get_db)
):
    """Verify certificate by credential ID"""
    service = CertificateService(db)
    verification = service.verify_certificate(credential_id)
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )
    
    return verification


# Webhook Endpoints
@router.get("/webhooks")
async def get_webhooks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's webhooks"""
    service = WebhookService(db)
    webhooks = service.get_user_webhooks(current_user.id)
    return webhooks


@router.post("/webhooks")
async def create_webhook(
    webhook_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new webhook"""
    service = WebhookService(db)
    webhook = service.create_webhook(current_user.id, webhook_data)
    return webhook


@router.put("/webhooks/{webhook_id}")
async def update_webhook(
    webhook_id: int,
    webhook_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update webhook"""
    # Implementation would update webhook in database
    return {"status": "success"}


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete webhook"""
    service = WebhookService(db)
    success = service.delete_webhook(webhook_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return {"status": "deleted"}


@router.post("/webhooks/{webhook_id}/test")
async def test_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send test webhook"""
    service = WebhookService(db)
    
    test_payload = {
        "event": "test",
        "timestamp": "2025-11-20T12:00:00Z",
        "data": {
            "message": "This is a test webhook from IKODIO"
        }
    }
    
    success = service.trigger_webhook(webhook_id, "test", test_payload)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test webhook"
        )
    
    return {"status": "sent"}


# Report Endpoints
@router.get("/reports")
async def get_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's reports"""
    service = ReportService(db)
    reports = service.get_user_reports(current_user.id)
    return reports


@router.post("/reports/generate")
async def generate_report(
    report_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a new report"""
    service = ReportService(db)
    
    report_type = report_data.get("type", "security")
    date_range = int(report_data.get("dateRange", 30))
    format = report_data.get("format", "pdf")
    
    report = service.generate_report(
        current_user.id,
        report_type,
        date_range,
        format
    )
    
    return report


@router.get("/reports/{report_id}/download")
async def download_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download report file"""
    # In production, fetch report from database and generate/fetch file
    from fastapi.responses import Response
    
    # Mock PDF data
    pdf_data = b"Mock PDF report data"
    
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report-{report_id}.pdf"
        }
    )


@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete report"""
    service = ReportService(db)
    success = service.delete_report(report_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return {"status": "deleted"}


# Tutorial and Tool Endpoints (mock data)
@router.get("/tutorials")
async def get_tutorials():
    """Get available tutorials"""
    # Mock data - in production, fetch from database
    return []


@router.get("/marketplace/tools")
async def get_tools():
    """Get available security tools"""
    # Mock data - in production, fetch from database
    return []


@router.post("/marketplace/tools/{tool_id}/install")
async def install_tool(
    tool_id: int,
    current_user: User = Depends(get_current_user)
):
    """Install a security tool"""
    # In production, handle tool installation
    return {"status": "installing", "tool_id": tool_id}
