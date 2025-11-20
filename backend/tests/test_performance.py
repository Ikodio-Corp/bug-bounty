"""
Performance Tests for Critical Endpoints
"""
import pytest
from httpx import AsyncClient
import time
from statistics import mean, median

from main import app


class TestAuthenticationPerformance:
    """Test authentication performance"""
    
    @pytest.mark.asyncio
    async def test_registration_performance(self):
        """Test registration endpoint performance"""
        user_data = {
            "username": "perfuser",
            "email": "perf@example.com",
            "password": "SecurePass123!"
        }
        
        times = []
        async with AsyncClient(app=app, base_url="http://test") as client:
            for i in range(10):
                user_data["username"] = f"perfuser{i}"
                user_data["email"] = f"perf{i}@example.com"
                
                start = time.time()
                response = await client.post("/api/auth/register", json=user_data)
                end = time.time()
                
                if response.status_code == 201:
                    times.append(end - start)
        
        if times:
            avg_time = mean(times)
            median_time = median(times)
            
            assert avg_time < 2.0
            assert median_time < 1.5
    
    @pytest.mark.asyncio
    async def test_login_performance(self):
        """Test login endpoint performance"""
        user_data = {
            "username": "loginperf",
            "email": "loginperf@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=user_data)
            
            times = []
            for _ in range(20):
                start = time.time()
                response = await client.post("/api/auth/login", data={
                    "username": user_data["username"],
                    "password": user_data["password"]
                })
                end = time.time()
                
                if response.status_code == 200:
                    times.append(end - start)
            
            if times:
                avg_time = mean(times)
                assert avg_time < 1.0


class TestScanPerformance:
    """Test scan endpoint performance"""
    
    @pytest.mark.asyncio
    async def test_scan_creation_performance(self):
        """Test scan creation performance"""
        user_data = {
            "username": "scanner",
            "email": "scanner@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            scan_data = {
                "target_url": "https://example.com",
                "scan_type": "quick",
                "scanner": "nuclei"
            }
            
            times = []
            for i in range(10):
                scan_data["target_url"] = f"https://example{i}.com"
                
                start = time.time()
                response = await client.post("/api/scans/", json=scan_data, headers=headers)
                end = time.time()
                
                if response.status_code == 201:
                    times.append(end - start)
            
            if times:
                avg_time = mean(times)
                assert avg_time < 2.0


class TestBugPerformance:
    """Test bug endpoint performance"""
    
    @pytest.mark.asyncio
    async def test_bug_list_performance(self):
        """Test bug listing performance"""
        user_data = {
            "username": "buglister",
            "email": "buglister@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            times = []
            for _ in range(20):
                start = time.time()
                response = await client.get("/api/bugs/", headers=headers)
                end = time.time()
                
                if response.status_code in [200, 404]:
                    times.append(end - start)
            
            if times:
                avg_time = mean(times)
                assert avg_time < 1.0


class TestDatabasePerformance:
    """Test database query performance"""
    
    @pytest.mark.asyncio
    async def test_user_query_performance(self):
        """Test user query performance"""
        user_data = {
            "username": "dbperf",
            "email": "dbperf@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            times = []
            for _ in range(20):
                start = time.time()
                response = await client.get("/api/users/me", headers=headers)
                end = time.time()
                
                if response.status_code == 200:
                    times.append(end - start)
            
            if times:
                avg_time = mean(times)
                assert avg_time < 0.5


class TestConcurrency:
    """Test concurrent request handling"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        import asyncio
        
        user_data = {
            "username": "concurrent",
            "email": "concurrent@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            async def make_request():
                start = time.time()
                response = await client.get("/api/users/me", headers=headers)
                end = time.time()
                return end - start if response.status_code == 200 else None
            
            tasks = [make_request() for _ in range(50)]
            times = await asyncio.gather(*tasks)
            
            valid_times = [t for t in times if t is not None]
            if valid_times:
                avg_time = mean(valid_times)
                max_time = max(valid_times)
                
                assert avg_time < 2.0
                assert max_time < 5.0
