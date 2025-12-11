"""
Test notification system
"""
import pytest
from tasks.notification_tasks import (
    send_email_notification,
    send_push_notification,
    send_slack_notification,
    send_bulk_notifications
)
from models.user import User


class TestEmailNotifications:
    """Test email notification tasks"""
    
    def test_send_email_notification(self, db_session, test_user):
        """Test sending email notification"""
        result = send_email_notification.apply(args=[
            test_user.email,
            "Test Notification",
            "This is a test email notification"
        ]).get()
        
        assert result is not None
        assert result["status"] == "sent"
    
    def test_send_bug_alert_email(self, db_session, test_user):
        """Test sending bug alert email"""
        bug_data = {
            "id": 1,
            "title": "Critical XSS Found",
            "severity": "critical",
            "url": "https://app.com/bug/1"
        }
        
        result = send_email_notification.apply(args=[
            test_user.email,
            "Critical Bug Alert",
            f"New critical bug found: {bug_data['title']}",
            {"bug": bug_data}
        ]).get()
        
        assert result["status"] == "sent"
    
    def test_send_bounty_payment_email(self, db_session, test_user):
        """Test sending bounty payment notification"""
        payment_data = {
            "amount": 500.00,
            "bug_id": 1,
            "payment_method": "stripe"
        }
        
        result = send_email_notification.apply(args=[
            test_user.email,
            "Bounty Payment Received",
            f"You received ${payment_data['amount']} for bug #{payment_data['bug_id']}"
        ]).get()
        
        assert result["status"] == "sent"


class TestPushNotifications:
    """Test push notification tasks"""
    
    def test_send_push_notification(self, db_session, test_user):
        """Test sending push notification"""
        result = send_push_notification.apply(args=[
            test_user.id,
            "Test Push",
            "This is a test push notification"
        ]).get()
        
        assert result is not None
    
    def test_send_scan_complete_notification(self, db_session, test_user):
        """Test sending scan completion notification"""
        scan_data = {
            "id": 1,
            "target": "https://example.com",
            "vulnerabilities_found": 5
        }
        
        result = send_push_notification.apply(args=[
            test_user.id,
            "Scan Complete",
            f"Found {scan_data['vulnerabilities_found']} vulnerabilities"
        ]).get()
        
        assert result is not None


class TestSlackNotifications:
    """Test Slack notification tasks"""
    
    def test_send_slack_notification(self):
        """Test sending Slack notification"""
        result = send_slack_notification.apply(args=[
            "#security-alerts",
            "Test Slack notification"
        ]).get()
        
        assert result is not None
    
    def test_send_critical_bug_alert(self):
        """Test sending critical bug alert to Slack"""
        bug_data = {
            "id": 1,
            "title": "SQL Injection in Admin Panel",
            "severity": "critical",
            "reporter": "security_researcher"
        }
        
        message = f" Critical Bug Alert\n*{bug_data['title']}*\nReported by: {bug_data['reporter']}"
        
        result = send_slack_notification.apply(args=[
            "#critical-bugs",
            message
        ]).get()
        
        assert result is not None


class TestBulkNotifications:
    """Test bulk notification tasks"""
    
    def test_send_bulk_notifications(self, db_session):
        """Test sending bulk notifications"""
        users = [
            {"id": 1, "email": "user1@test.com"},
            {"id": 2, "email": "user2@test.com"},
            {"id": 3, "email": "user3@test.com"}
        ]
        
        result = send_bulk_notifications.apply(args=[
            users,
            "Platform Update",
            "New features are now available"
        ]).get()
        
        assert result is not None
        assert result["sent_count"] == 3
    
    def test_send_security_alert_to_all(self, db_session):
        """Test sending security alert to all users"""
        alert = {
            "title": "Security Update Required",
            "message": "Please update your password",
            "priority": "high"
        }
        
        result = send_bulk_notifications.apply(args=[
            "all_users",
            alert["title"],
            alert["message"]
        ]).get()
        
        assert result is not None


class TestNotificationPreferences:
    """Test notification preference handling"""
    
    def test_respect_user_preferences(self, db_session, test_user):
        """Test respecting user notification preferences"""
        # Set user preferences to disable email
        test_user.notification_preferences = {
            "email": False,
            "push": True,
            "slack": False
        }
        db_session.commit()
        
        # Should not send email
        result = send_email_notification.apply(args=[
            test_user.email,
            "Test",
            "This should not be sent"
        ]).get()
        
        assert result["status"] == "skipped"
    
    def test_notification_frequency_limits(self, db_session, test_user):
        """Test notification frequency limiting"""
        # Send multiple notifications rapidly
        for i in range(5):
            send_email_notification.apply(args=[
                test_user.email,
                f"Notification {i}",
                f"Message {i}"
            ])
        
        # Should be rate limited after threshold
        result = send_email_notification.apply(args=[
            test_user.email,
            "Rate Limited",
            "This should be rate limited"
        ]).get()
        
        assert "rate_limited" in result or result["status"] == "sent"


class TestNotificationTemplates:
    """Test notification templates"""
    
    def test_bug_verification_template(self, db_session, test_user):
        """Test bug verification email template"""
        bug_data = {
            "id": 1,
            "title": "XSS Vulnerability",
            "severity": "high"
        }
        
        result = send_email_notification.apply(args=[
            test_user.email,
            "Bug Verified",
            None,  # Will use template
            {"template": "bug_verified", "data": bug_data}
        ]).get()
        
        assert result["status"] == "sent"
        assert result["template_used"] == "bug_verified"
    
    def test_welcome_email_template(self, db_session):
        """Test welcome email template"""
        new_user = {
            "email": "newuser@test.com",
            "username": "newuser"
        }
        
        result = send_email_notification.apply(args=[
            new_user["email"],
            "Welcome to IKODIO",
            None,
            {"template": "welcome", "data": new_user}
        ]).get()
        
        assert result["status"] == "sent"
