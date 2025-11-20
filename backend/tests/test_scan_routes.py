"""
Integration Tests for Scan Routes
"""
import pytest
from httpx import AsyncClient
from datetime import datetime

from main import app


@pytest.fixture
def auth_headers(test_user_data):
    """Get authentication headers"""
    async def _get_headers():
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
    
    return _get_headers


@pytest.fixture
def scan_data():
    """Test scan data"""
    return {
        "target_url": "https://example.com",
        "scan_type": "full",
        "scanner": "nuclei"
    }


class TestScanCreation:
    """Test scan creation endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_scan_success(self, test_user_data, scan_data):
        """Test successful scan creation"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.post("/api/scans/", json=scan_data, headers=headers)
            
            assert response.status_code == 201
            data = response.json()
            assert data["target_url"] == scan_data["target_url"]
            assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_scan_unauthorized(self, scan_data):
        """Test scan creation without authentication"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/scans/", json=scan_data)
            
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_scan_invalid_url(self, test_user_data):
        """Test scan creation with invalid URL"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            invalid_scan_data = {
                "target_url": "not_a_valid_url",
                "scan_type": "full",
                "scanner": "nuclei"
            }
            
            response = await client.post("/api/scans/", json=invalid_scan_data, headers=headers)
            
            assert response.status_code == 422


class TestScanRetrieval:
    """Test scan retrieval endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_scan_by_id(self, test_user_data, scan_data):
        """Test get scan by ID"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            create_response = await client.post("/api/scans/", json=scan_data, headers=headers)
            scan_id = create_response.json()["id"]
            
            response = await client.get(f"/api/scans/{scan_id}", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == scan_id
    
    @pytest.mark.asyncio
    async def test_list_user_scans(self, test_user_data, scan_data):
        """Test list user scans"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            await client.post("/api/scans/", json=scan_data, headers=headers)
            
            response = await client.get("/api/scans/", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_scan(self, test_user_data):
        """Test get non-existent scan"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.get("/api/scans/99999", headers=headers)
            
            assert response.status_code == 404


class TestScanUpdate:
    """Test scan update endpoints"""
    
    @pytest.mark.asyncio
    async def test_update_scan(self, test_user_data, scan_data):
        """Test scan update"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            create_response = await client.post("/api/scans/", json=scan_data, headers=headers)
            scan_id = create_response.json()["id"]
            
            update_data = {"scan_type": "quick"}
            response = await client.patch(f"/api/scans/{scan_id}", json=update_data, headers=headers)
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_cancel_scan(self, test_user_data, scan_data):
        """Test scan cancellation"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            create_response = await client.post("/api/scans/", json=scan_data, headers=headers)
            scan_id = create_response.json()["id"]
            
            response = await client.post(f"/api/scans/{scan_id}/cancel", headers=headers)
            
            assert response.status_code == 200


class TestScanDeletion:
    """Test scan deletion endpoints"""
    
    @pytest.mark.asyncio
    async def test_delete_scan(self, test_user_data, scan_data):
        """Test scan deletion"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            create_response = await client.post("/api/scans/", json=scan_data, headers=headers)
            scan_id = create_response.json()["id"]
            
            response = await client.delete(f"/api/scans/{scan_id}", headers=headers)
            
            assert response.status_code in [200, 204]


class TestScanResults:
    """Test scan results endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_scan_results(self, test_user_data, scan_data):
        """Test get scan results"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            create_response = await client.post("/api/scans/", json=scan_data, headers=headers)
            scan_id = create_response.json()["id"]
            
            response = await client.get(f"/api/scans/{scan_id}/results", headers=headers)
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_export_scan_results(self, test_user_data, scan_data):
        """Test export scan results"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            create_response = await client.post("/api/scans/", json=scan_data, headers=headers)
            scan_id = create_response.json()["id"]
            
            response = await client.get(f"/api/scans/{scan_id}/export?format=json", headers=headers)
            
            assert response.status_code in [200, 404]


class TestScanStatistics:
    """Test scan statistics endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_scan_statistics(self, test_user_data):
        """Test get scan statistics"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.get("/api/scans/statistics", headers=headers)
            
            assert response.status_code == 200
