"""
Test additional features services
"""
import pytest
from services.additional_features_service import AdditionalFeaturesService
from datetime import datetime, timedelta


@pytest.fixture
def service():
    return AdditionalFeaturesService()


class TestCertificateService:
    """Test certificate management"""
    
    def test_create_certificate(self, service, db_session, test_user):
        """Test creating a certificate"""
        certificate_data = {
            "user_id": test_user.id,
            "name": "Bug Bounty Hunter Certification",
            "issuer": "IKODIO Security Academy",
            "type": "certification",
            "issued_at": datetime.utcnow(),
            "credential_id": "CERT-2025-001",
            "skills": ["Web Security", "API Testing", "OWASP Top 10"],
            "verified": True
        }
        
        certificate = service.create_certificate(db_session, certificate_data)
        
        assert certificate.id is not None
        assert certificate.name == certificate_data["name"]
        assert certificate.credential_id == certificate_data["credential_id"]
        assert len(certificate.skills) == 3
    
    def test_get_user_certificates(self, service, db_session, test_user):
        """Test retrieving user certificates"""
        # Create test certificates
        for i in range(3):
            service.create_certificate(db_session, {
                "user_id": test_user.id,
                "name": f"Certificate {i+1}",
                "issuer": "IKODIO",
                "type": "course",
                "issued_at": datetime.utcnow(),
                "credential_id": f"CERT-{i+1}"
            })
        
        certificates = service.get_user_certificates(db_session, test_user.id)
        assert len(certificates) == 3
    
    def test_verify_certificate(self, service, db_session, test_user):
        """Test certificate verification"""
        certificate = service.create_certificate(db_session, {
            "user_id": test_user.id,
            "name": "Test Certificate",
            "issuer": "IKODIO",
            "type": "achievement",
            "issued_at": datetime.utcnow(),
            "credential_id": "CERT-VERIFY-001"
        })
        
        verified = service.verify_certificate(db_session, certificate.credential_id)
        assert verified is True


class TestWebhookService:
    """Test webhook management"""
    
    def test_create_webhook(self, service, db_session, test_user):
        """Test creating a webhook"""
        webhook_data = {
            "user_id": test_user.id,
            "name": "Bug Notification Webhook",
            "url": "https://example.com/webhook",
            "events": ["bug.created", "bug.updated", "scan.completed"],
            "active": True
        }
        
        webhook = service.create_webhook(db_session, webhook_data)
        
        assert webhook.id is not None
        assert webhook.url == webhook_data["url"]
        assert len(webhook.events) == 3
        assert webhook.secret is not None
    
    def test_trigger_webhook(self, service, db_session, test_user):
        """Test triggering a webhook"""
        webhook = service.create_webhook(db_session, {
            "user_id": test_user.id,
            "name": "Test Webhook",
            "url": "https://httpbin.org/post",
            "events": ["test.event"],
            "active": True
        })
        
        payload = {
            "event": "test.event",
            "data": {"message": "Test notification"}
        }
        
        result = service.trigger_webhook(db_session, webhook.id, payload)
        assert result["success"] is True
    
    def test_get_webhook_deliveries(self, service, db_session, test_user):
        """Test retrieving webhook deliveries"""
        webhook = service.create_webhook(db_session, {
            "user_id": test_user.id,
            "name": "Test Webhook",
            "url": "https://httpbin.org/post",
            "events": ["test.event"],
            "active": True
        })
        
        # Trigger webhook multiple times
        for i in range(3):
            service.trigger_webhook(db_session, webhook.id, {
                "event": "test.event",
                "data": {"count": i}
            })
        
        deliveries = service.get_webhook_deliveries(db_session, webhook.id)
        assert len(deliveries) >= 3


class TestReportService:
    """Test report generation"""
    
    def test_create_report(self, service, db_session, test_user):
        """Test creating a report"""
        report_data = {
            "user_id": test_user.id,
            "type": "security",
            "title": "Monthly Security Report",
            "format": "pdf",
            "date_range_days": 30
        }
        
        report = service.create_report(db_session, report_data)
        
        assert report.id is not None
        assert report.status == "generating"
        assert report.type == "security"
    
    def test_generate_security_report(self, service, db_session, test_user):
        """Test generating security report"""
        report = service.create_report(db_session, {
            "user_id": test_user.id,
            "type": "security",
            "title": "Security Assessment",
            "format": "json",
            "date_range_days": 7
        })
        
        generated = service.generate_report(db_session, report.id)
        
        assert generated.status == "ready"
        assert generated.data is not None
        assert "summary" in generated.data
    
    def test_get_user_reports(self, service, db_session, test_user):
        """Test retrieving user reports"""
        # Create multiple reports
        for i in range(3):
            service.create_report(db_session, {
                "user_id": test_user.id,
                "type": "vulnerability",
                "title": f"Report {i+1}",
                "format": "pdf",
                "date_range_days": 30
            })
        
        reports = service.get_user_reports(db_session, test_user.id)
        assert len(reports) == 3
    
    def test_download_report(self, service, db_session, test_user):
        """Test downloading a report"""
        report = service.create_report(db_session, {
            "user_id": test_user.id,
            "type": "compliance",
            "title": "Compliance Report",
            "format": "csv",
            "date_range_days": 90
        })
        
        service.generate_report(db_session, report.id)
        
        # Simulate download
        result = service.download_report(db_session, report.id)
        assert result is not None
        assert report.download_count == 1
