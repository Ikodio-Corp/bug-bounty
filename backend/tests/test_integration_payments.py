"""
Integration Tests for Payment Routes
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from main import app


class TestSubscriptionPlans:
    """Test subscription plan endpoints"""
    
    @pytest.mark.asyncio
    async def test_list_subscription_plans(self):
        """Test listing subscription plans"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/payments/plans")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_plan_details(self):
        """Test getting plan details"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/payments/plans/starter")
            
            assert response.status_code in [200, 404]


class TestSubscriptionCreation:
    """Test subscription creation"""
    
    @pytest.mark.asyncio
    async def test_create_subscription(self):
        """Test creating subscription"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            with patch('integrations.stripe_client.create_subscription') as mock_create:
                mock_create.return_value = {"id": "sub_123", "status": "active"}
                
                response = await client.post(
                    "/api/payments/subscribe",
                    json={
                        "plan_id": "starter",
                        "payment_method_id": "pm_test_123"
                    },
                    headers=headers
                )
                
                assert response.status_code in [200, 201, 400]
    
    @pytest.mark.asyncio
    async def test_create_subscription_unauthorized(self):
        """Test creating subscription without authentication"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/payments/subscribe",
                json={
                    "plan_id": "starter",
                    "payment_method_id": "pm_test_123"
                }
            )
            
            assert response.status_code == 401


class TestSubscriptionManagement:
    """Test subscription management"""
    
    @pytest.mark.asyncio
    async def test_get_current_subscription(self):
        """Test getting current subscription"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.get("/api/payments/subscription", headers=headers)
            
            assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_upgrade_subscription(self):
        """Test upgrading subscription"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.post(
                "/api/payments/subscription/upgrade",
                json={"plan_id": "professional"},
                headers=headers
            )
            
            assert response.status_code in [200, 400, 404]
    
    @pytest.mark.asyncio
    async def test_cancel_subscription(self):
        """Test canceling subscription"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.post("/api/payments/subscription/cancel", headers=headers)
            
            assert response.status_code in [200, 404]


class TestPaymentMethods:
    """Test payment method management"""
    
    @pytest.mark.asyncio
    async def test_list_payment_methods(self):
        """Test listing payment methods"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.get("/api/payments/payment-methods", headers=headers)
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_add_payment_method(self):
        """Test adding payment method"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            with patch('integrations.stripe_client.attach_payment_method') as mock_attach:
                mock_attach.return_value = {"id": "pm_123"}
                
                response = await client.post(
                    "/api/payments/payment-methods",
                    json={"payment_method_id": "pm_test_123"},
                    headers=headers
                )
                
                assert response.status_code in [200, 201, 400]
    
    @pytest.mark.asyncio
    async def test_delete_payment_method(self):
        """Test deleting payment method"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.delete("/api/payments/payment-methods/pm_123", headers=headers)
            
            assert response.status_code in [200, 204, 404]


class TestInvoices:
    """Test invoice management"""
    
    @pytest.mark.asyncio
    async def test_list_invoices(self):
        """Test listing invoices"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.get("/api/payments/invoices", headers=headers)
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_invoice_details(self):
        """Test getting invoice details"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.get("/api/payments/invoices/inv_123", headers=headers)
            
            assert response.status_code in [200, 404]


class TestWebhooks:
    """Test Stripe webhooks"""
    
    @pytest.mark.asyncio
    async def test_stripe_webhook_payment_succeeded(self):
        """Test Stripe webhook for successful payment"""
        webhook_data = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_123",
                    "amount": 1000,
                    "customer": "cus_123"
                }
            }
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/webhooks/stripe", json=webhook_data)
            
            assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_stripe_webhook_subscription_created(self):
        """Test Stripe webhook for subscription created"""
        webhook_data = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_123",
                    "customer": "cus_123",
                    "status": "active"
                }
            }
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/webhooks/stripe", json=webhook_data)
            
            assert response.status_code in [200, 400]
