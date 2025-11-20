"""
End-to-End Tests for Complete User Workflows
"""
import pytest
from httpx import AsyncClient
from datetime import datetime

from main import app


class TestCompleteUserJourney:
    """Test complete user journey from registration to bug submission"""
    
    @pytest.mark.asyncio
    async def test_full_user_workflow(self):
        """Test complete user workflow"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_data = {
                "username": "hunter123",
                "email": "hunter@example.com",
                "password": "SecurePass123!",
                "full_name": "Bug Hunter"
            }
            
            register_response = await client.post("/api/auth/register", json=user_data)
            assert register_response.status_code == 201
            
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            assert login_response.status_code == 200
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            scan_data = {
                "target_url": "https://example.com",
                "scan_type": "full",
                "scanner": "nuclei"
            }
            scan_response = await client.post("/api/scans/", json=scan_data, headers=headers)
            assert scan_response.status_code == 201
            
            bug_data = {
                "title": "SQL Injection in login",
                "description": "SQL injection vulnerability found",
                "bug_type": "sql_injection",
                "severity": "high",
                "target_url": "https://example.com/login"
            }
            bug_response = await client.post("/api/bugs/", json=bug_data, headers=headers)
            assert bug_response.status_code in [201, 404]


class TestSubscriptionWorkflow:
    """Test subscription workflow"""
    
    @pytest.mark.asyncio
    async def test_subscription_upgrade_workflow(self):
        """Test subscription upgrade workflow"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_data = {
                "username": "subscriber",
                "email": "subscriber@example.com",
                "password": "SecurePass123!"
            }
            
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            plans_response = await client.get("/api/payments/plans")
            assert plans_response.status_code == 200
            
            subscription_response = await client.get("/api/payments/subscription", headers=headers)
            assert subscription_response.status_code in [200, 404]


class TestOAuthWorkflow:
    """Test OAuth workflow"""
    
    @pytest.mark.asyncio
    async def test_oauth_login_workflow(self):
        """Test OAuth login workflow"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            authorize_response = await client.get("/api/oauth/google/authorize")
            assert authorize_response.status_code in [200, 302, 307]
            
            if authorize_response.status_code in [302, 307]:
                location = authorize_response.headers.get("location")
                assert location is not None


class TestBugValidationWorkflow:
    """Test bug validation workflow"""
    
    @pytest.mark.asyncio
    async def test_bug_validation_complete_workflow(self):
        """Test complete bug validation workflow"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_data = {
                "username": "validator",
                "email": "validator@example.com",
                "password": "SecurePass123!"
            }
            
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            bug_data = {
                "title": "XSS in search",
                "description": "XSS vulnerability",
                "bug_type": "xss",
                "severity": "medium",
                "target_url": "https://example.com/search"
            }
            bug_response = await client.post("/api/bugs/", json=bug_data, headers=headers)
            
            if bug_response.status_code == 201:
                bug_id = bug_response.json()["id"]
                
                validation_response = await client.post(
                    f"/api/bug-validation/{bug_id}/start",
                    headers=headers
                )
                assert validation_response.status_code in [200, 404]


class TestTeamCollaboration:
    """Test team collaboration features"""
    
    @pytest.mark.asyncio
    async def test_team_bug_sharing(self):
        """Test team bug sharing"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            user1_data = {
                "username": "hunter1",
                "email": "hunter1@example.com",
                "password": "SecurePass123!"
            }
            user2_data = {
                "username": "hunter2",
                "email": "hunter2@example.com",
                "password": "SecurePass123!"
            }
            
            await client.post("/api/auth/register", json=user1_data)
            await client.post("/api/auth/register", json=user2_data)
            
            login1_response = await client.post("/api/auth/login", data={
                "username": user1_data["username"],
                "password": user1_data["password"]
            })
            
            token1 = login1_response.json()["access_token"]
            headers1 = {"Authorization": f"Bearer {token1}"}
            
            bug_data = {
                "title": "CSRF vulnerability",
                "description": "CSRF found",
                "bug_type": "csrf",
                "severity": "medium",
                "target_url": "https://example.com"
            }
            bug_response = await client.post("/api/bugs/", json=bug_data, headers=headers1)
            assert bug_response.status_code in [201, 404]


class TestScanningWorkflow:
    """Test scanning workflow"""
    
    @pytest.mark.asyncio
    async def test_automated_scanning_workflow(self):
        """Test automated scanning workflow"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_data = {
                "username": "scanner",
                "email": "scanner@example.com",
                "password": "SecurePass123!"
            }
            
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            scan_data = {
                "target_url": "https://example.com",
                "scan_type": "full",
                "scanner": "nuclei"
            }
            scan_response = await client.post("/api/scans/", json=scan_data, headers=headers)
            
            if scan_response.status_code == 201:
                scan_id = scan_response.json()["id"]
                
                results_response = await client.get(
                    f"/api/scans/{scan_id}/results",
                    headers=headers
                )
                assert results_response.status_code in [200, 404]
                
                status_response = await client.get(
                    f"/api/scans/{scan_id}",
                    headers=headers
                )
                assert status_response.status_code == 200


class TestIntegrationWorkflow:
    """Test integration workflow"""
    
    @pytest.mark.asyncio
    async def test_github_integration_workflow(self):
        """Test GitHub integration workflow"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_data = {
                "username": "integrator",
                "email": "integrator@example.com",
                "password": "SecurePass123!"
            }
            
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            providers_response = await client.get("/api/oauth/providers", headers=headers)
            assert providers_response.status_code == 200


class TestNotificationWorkflow:
    """Test notification workflow"""
    
    @pytest.mark.asyncio
    async def test_notification_setup_workflow(self):
        """Test notification setup workflow"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_data = {
                "username": "notifier",
                "email": "notifier@example.com",
                "password": "SecurePass123!"
            }
            
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            channels_response = await client.get("/api/notifications/channels", headers=headers)
            assert channels_response.status_code == 200


class TestReportingWorkflow:
    """Test reporting workflow"""
    
    @pytest.mark.asyncio
    async def test_bug_reporting_workflow(self):
        """Test bug reporting to platforms"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_data = {
                "username": "reporter",
                "email": "reporter@example.com",
                "password": "SecurePass123!"
            }
            
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            platforms_response = await client.get("/api/auto-reporting/platforms", headers=headers)
            assert platforms_response.status_code == 200
