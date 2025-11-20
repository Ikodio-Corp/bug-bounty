from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from models.user import User
from models.bug import Bug

class CertificateService:
    """Service for managing user certificates and achievements"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_certificates(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all certificates for a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        certificates = []
        
        # Add course completion certificates
        # This would be fetched from a certificates table in production
        
        # Add achievement-based certificates
        if user.bugs_submitted >= 10:
            certificates.append({
                "id": 1,
                "name": "Bug Hunter",
                "issuer": "IKODIO Platform",
                "type": "achievement",
                "issued_at": datetime.utcnow(),
                "credential_id": f"BH-{user.id}-{datetime.utcnow().strftime('%Y%m%d')}",
                "skills": ["Bug Hunting", "Vulnerability Analysis"],
                "verified": True
            })
        
        if user.reputation >= 1000:
            certificates.append({
                "id": 2,
                "name": "Elite Security Researcher",
                "issuer": "IKODIO Platform",
                "type": "achievement",
                "issued_at": datetime.utcnow(),
                "credential_id": f"ESR-{user.id}-{datetime.utcnow().strftime('%Y%m%d')}",
                "skills": ["Advanced Exploitation", "Security Research"],
                "verified": True
            })
        
        return certificates
    
    def verify_certificate(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """Verify a certificate by credential ID"""
        # In production, this would check against a certificates database
        # For now, return mock verification
        return {
            "valid": True,
            "credential_id": credential_id,
            "verified_at": datetime.utcnow()
        }
    
    def generate_certificate_pdf(self, certificate_id: int, user_id: int) -> bytes:
        """Generate PDF certificate"""
        # This would use a PDF generation library like ReportLab
        # For now, return mock PDF data
        return b"Mock PDF certificate data"


class WebhookService:
    """Service for managing webhooks"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_webhook(self, user_id: int, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new webhook"""
        import secrets
        
        webhook = {
            "id": secrets.randbelow(1000000),
            "user_id": user_id,
            "name": webhook_data.get("name"),
            "url": webhook_data.get("url"),
            "events": webhook_data.get("events", []),
            "active": True,
            "secret": f"whsec_{secrets.token_urlsafe(32)}",
            "success_count": 0,
            "failure_count": 0,
            "created_at": datetime.utcnow()
        }
        
        # In production, save to database
        return webhook
    
    def trigger_webhook(self, webhook_id: int, event: str, payload: Dict[str, Any]) -> bool:
        """Trigger a webhook with event payload"""
        import httpx
        import hmac
        import hashlib
        
        # In production, fetch webhook from database
        webhook = self.get_webhook(webhook_id)
        if not webhook or not webhook.get("active"):
            return False
        
        if event not in webhook.get("events", []):
            return False
        
        # Create signature
        secret = webhook.get("secret", "").encode()
        message = str(payload).encode()
        signature = hmac.new(secret, message, hashlib.sha256).hexdigest()
        
        headers = {
            "X-IKODIO-Event": event,
            "X-IKODIO-Signature": f"sha256={signature}",
            "Content-Type": "application/json"
        }
        
        try:
            response = httpx.post(
                webhook["url"],
                json=payload,
                headers=headers,
                timeout=30
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook delivery failed: {e}")
            return False
    
    def get_webhook(self, webhook_id: int) -> Optional[Dict[str, Any]]:
        """Get webhook by ID"""
        # In production, fetch from database
        return None
    
    def get_user_webhooks(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all webhooks for a user"""
        # In production, fetch from database
        return []
    
    def delete_webhook(self, webhook_id: int, user_id: int) -> bool:
        """Delete a webhook"""
        # In production, delete from database
        return True


class ReportService:
    """Service for generating security reports"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_report(
        self,
        user_id: int,
        report_type: str,
        date_range: int,
        format: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate a security report"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        start_date = datetime.utcnow() - timedelta(days=date_range)
        
        # Fetch data based on report type
        if report_type == "security":
            data = self._get_security_data(user_id, start_date)
        elif report_type == "vulnerability":
            data = self._get_vulnerability_data(user_id, start_date)
        elif report_type == "compliance":
            data = self._get_compliance_data(user_id, start_date)
        elif report_type == "scan":
            data = self._get_scan_data(user_id, start_date)
        else:
            raise ValueError(f"Invalid report type: {report_type}")
        
        report = {
            "id": secrets.randbelow(1000000),
            "type": report_type,
            "title": f"{report_type.title()} Report - {datetime.utcnow().strftime('%B %Y')}",
            "status": "generating",
            "created_at": datetime.utcnow(),
            "user_id": user_id,
            "format": format,
            "data": data
        }
        
        # In production, queue report generation task
        # For now, mark as ready immediately
        report["status"] = "ready"
        report["size"] = "2.4 MB"
        report["download_url"] = f"/api/reports/{report['id']}/download"
        
        return report
    
    def _get_security_data(self, user_id: int, start_date: datetime) -> Dict[str, Any]:
        """Get security analysis data"""
        bugs = self.db.query(Bug).filter(
            Bug.user_id == user_id,
            Bug.created_at >= start_date
        ).all()
        
        return {
            "total_bugs": len(bugs),
            "critical_bugs": len([b for b in bugs if b.severity == "critical"]),
            "high_bugs": len([b for b in bugs if b.severity == "high"]),
            "medium_bugs": len([b for b in bugs if b.severity == "medium"]),
            "low_bugs": len([b for b in bugs if b.severity == "low"])
        }
    
    def _get_vulnerability_data(self, user_id: int, start_date: datetime) -> Dict[str, Any]:
        """Get vulnerability assessment data"""
        bugs = self.db.query(Bug).filter(
            Bug.user_id == user_id,
            Bug.created_at >= start_date
        ).all()
        
        vulnerability_types = {}
        for bug in bugs:
            vuln_type = bug.type
            vulnerability_types[vuln_type] = vulnerability_types.get(vuln_type, 0) + 1
        
        return {
            "total_vulnerabilities": len(bugs),
            "by_type": vulnerability_types,
            "trends": []
        }
    
    def _get_compliance_data(self, user_id: int, start_date: datetime) -> Dict[str, Any]:
        """Get compliance report data"""
        return {
            "compliance_score": 85,
            "passed_checks": 42,
            "failed_checks": 8,
            "standards": ["OWASP", "PCI-DSS", "GDPR"]
        }
    
    def _get_scan_data(self, user_id: int, start_date: datetime) -> Dict[str, Any]:
        """Get scan summary data"""
        # In production, query scans from database
        return {
            "total_scans": 15,
            "completed_scans": 12,
            "failed_scans": 2,
            "cancelled_scans": 1
        }
    
    def get_user_reports(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all reports for a user"""
        # In production, fetch from database
        return []
    
    def delete_report(self, report_id: int, user_id: int) -> bool:
        """Delete a report"""
        # In production, delete from database
        return True


import secrets
