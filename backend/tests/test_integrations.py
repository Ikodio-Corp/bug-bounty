import pytest
from unittest.mock import Mock, patch
from backend.integrations.stripe_client import StripeClient
from backend.integrations.email_client import EmailClient


class TestStripeClient:
    @pytest.fixture
    def stripe_client(self):
        return StripeClient(api_key="test_key")
    
    def test_create_payment_intent(self, stripe_client):
        with patch('stripe.PaymentIntent.create') as mock_create:
            mock_create.return_value = Mock(
                id="pi_test123",
                amount=9999,
                currency="usd",
                status="requires_payment_method"
            )
            
            payment_intent = stripe_client.create_payment_intent(
                amount=99.99,
                currency="usd",
                customer_id="cus_test123"
            )
            
            assert payment_intent is not None
            assert payment_intent.id == "pi_test123"
            assert payment_intent.amount == 9999
            mock_create.assert_called_once()
    
    def test_create_customer(self, stripe_client):
        with patch('stripe.Customer.create') as mock_create:
            mock_create.return_value = Mock(
                id="cus_test123",
                email="test@example.com"
            )
            
            customer = stripe_client.create_customer(
                email="test@example.com",
                name="Test User"
            )
            
            assert customer is not None
            assert customer.id == "cus_test123"
            assert customer.email == "test@example.com"
    
    def test_create_subscription(self, stripe_client):
        with patch('stripe.Subscription.create') as mock_create:
            mock_create.return_value = Mock(
                id="sub_test123",
                customer="cus_test123",
                status="active"
            )
            
            subscription = stripe_client.create_subscription(
                customer_id="cus_test123",
                price_id="price_test123"
            )
            
            assert subscription is not None
            assert subscription.id == "sub_test123"
            assert subscription.status == "active"
    
    def test_cancel_subscription(self, stripe_client):
        with patch('stripe.Subscription.modify') as mock_modify:
            mock_modify.return_value = Mock(
                id="sub_test123",
                status="canceled"
            )
            
            result = stripe_client.cancel_subscription("sub_test123")
            
            assert result is not None
            assert result.status == "canceled"
    
    def test_retrieve_payment_intent(self, stripe_client):
        with patch('stripe.PaymentIntent.retrieve') as mock_retrieve:
            mock_retrieve.return_value = Mock(
                id="pi_test123",
                status="succeeded"
            )
            
            payment_intent = stripe_client.retrieve_payment_intent("pi_test123")
            
            assert payment_intent is not None
            assert payment_intent.status == "succeeded"
    
    def test_create_refund(self, stripe_client):
        with patch('stripe.Refund.create') as mock_create:
            mock_create.return_value = Mock(
                id="re_test123",
                amount=9999,
                status="succeeded"
            )
            
            refund = stripe_client.create_refund(
                payment_intent_id="pi_test123",
                amount=99.99
            )
            
            assert refund is not None
            assert refund.id == "re_test123"
            assert refund.status == "succeeded"


class TestEmailClient:
    @pytest.fixture
    def email_client(self):
        return EmailClient(
            smtp_host="smtp.example.com",
            smtp_port=587,
            username="test@example.com",
            password="password"
        )
    
    def test_send_email(self, email_client):
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = email_client.send_email(
                to="recipient@example.com",
                subject="Test Email",
                body="This is a test email"
            )
            
            assert result is True
            mock_server.send_message.assert_called_once()
    
    def test_send_verification_email(self, email_client):
        with patch.object(email_client, 'send_email') as mock_send:
            mock_send.return_value = True
            
            result = email_client.send_verification_email(
                to="user@example.com",
                username="testuser",
                verification_token="abc123"
            )
            
            assert result is True
            mock_send.assert_called_once()
            args = mock_send.call_args
            assert "verification" in args[1]["subject"].lower()
    
    def test_send_password_reset_email(self, email_client):
        with patch.object(email_client, 'send_email') as mock_send:
            mock_send.return_value = True
            
            result = email_client.send_password_reset_email(
                to="user@example.com",
                username="testuser",
                reset_token="xyz789"
            )
            
            assert result is True
            mock_send.assert_called_once()
            args = mock_send.call_args
            assert "reset" in args[1]["subject"].lower()
    
    def test_send_bug_notification(self, email_client):
        with patch.object(email_client, 'send_email') as mock_send:
            mock_send.return_value = True
            
            result = email_client.send_bug_notification(
                to="hunter@example.com",
                bug_title="SQL Injection Found",
                bug_url="https://example.com/bugs/123"
            )
            
            assert result is True
            mock_send.assert_called_once()
    
    def test_send_scan_complete_notification(self, email_client):
        with patch.object(email_client, 'send_email') as mock_send:
            mock_send.return_value = True
            
            result = email_client.send_scan_complete_notification(
                to="user@example.com",
                scan_id=123,
                findings_count=5,
                target_url="https://example.com"
            )
            
            assert result is True
            mock_send.assert_called_once()
    
    def test_send_email_failure(self, email_client):
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.return_value.__enter__.side_effect = Exception("Connection failed")
            
            result = email_client.send_email(
                to="recipient@example.com",
                subject="Test",
                body="Test"
            )
            
            assert result is False
    
    def test_send_html_email(self, email_client):
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            html_content = "<html><body><h1>Test</h1></body></html>"
            
            result = email_client.send_html_email(
                to="recipient@example.com",
                subject="HTML Test",
                html_body=html_content
            )
            
            assert result is True
            mock_server.send_message.assert_called_once()
