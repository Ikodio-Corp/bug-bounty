"""
Load testing configuration using Locust
"""
from locust import HttpUser, task, between
import random
import json


class BugBountyUser(HttpUser):
    """Simulated user for load testing"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before starting tasks"""
        self.login()
    
    def login(self):
        """Authenticate user"""
        response = self.client.post("/api/auth/login", json={
            "username": f"testuser{random.randint(1, 100)}",
            "password": "testpassword123"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}
    
    @task(3)
    def view_dashboard(self):
        """View dashboard"""
        self.client.get("/api/dashboard", headers=self.headers)
    
    @task(5)
    def list_bugs(self):
        """List all bugs"""
        self.client.get("/api/bugs", headers=self.headers)
    
    @task(2)
    def view_bug_details(self):
        """View specific bug"""
        bug_id = random.randint(1, 100)
        self.client.get(f"/api/bugs/{bug_id}", headers=self.headers)
    
    @task(1)
    def submit_bug(self):
        """Submit new bug report"""
        self.client.post("/api/bugs", headers=self.headers, json={
            "title": f"Test Bug {random.randint(1, 10000)}",
            "description": "This is a test bug for load testing",
            "severity": random.choice(["low", "medium", "high", "critical"]),
            "target_url": "https://example.com",
            "proof_of_concept": "Test POC"
        })
    
    @task(2)
    def list_scans(self):
        """List security scans"""
        self.client.get("/api/scans", headers=self.headers)
    
    @task(1)
    def start_scan(self):
        """Start new security scan"""
        self.client.post("/api/scans", headers=self.headers, json={
            "target_url": "https://example.com",
            "scan_type": "quick"
        })
    
    @task(3)
    def browse_marketplace(self):
        """Browse marketplace tools"""
        self.client.get("/api/marketplace/tools", headers=self.headers)
    
    @task(1)
    def search_marketplace(self):
        """Search marketplace"""
        query = random.choice(["scanner", "analyzer", "exploit", "tool"])
        self.client.get(f"/api/marketplace/search?q={query}", headers=self.headers)
    
    @task(2)
    def view_leaderboard(self):
        """View leaderboard"""
        self.client.get("/api/leaderboard", headers=self.headers)
    
    @task(1)
    def view_profile(self):
        """View user profile"""
        self.client.get("/api/users/me", headers=self.headers)
    
    @task(1)
    def list_guilds(self):
        """List guilds"""
        self.client.get("/api/guilds", headers=self.headers)


class AdminUser(HttpUser):
    """Simulated admin user"""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login as admin"""
        response = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "adminpassword"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}
    
    @task(5)
    def view_admin_dashboard(self):
        """View admin dashboard"""
        self.client.get("/api/admin/dashboard", headers=self.headers)
    
    @task(3)
    def list_all_users(self):
        """List all users"""
        self.client.get("/api/admin/users", headers=self.headers)
    
    @task(2)
    def moderate_bugs(self):
        """View bugs for moderation"""
        self.client.get("/api/admin/bugs?status=pending", headers=self.headers)
    
    @task(1)
    def approve_bug(self):
        """Approve a bug"""
        bug_id = random.randint(1, 50)
        self.client.put(f"/api/admin/bugs/{bug_id}/approve", headers=self.headers)
    
    @task(2)
    def view_analytics(self):
        """View platform analytics"""
        self.client.get("/api/admin/analytics", headers=self.headers)


class ScannerUser(HttpUser):
    """Heavy scanner user"""
    
    wait_time = between(5, 10)
    
    def on_start(self):
        """Login"""
        response = self.client.post("/api/auth/login", json={
            "username": "scanner_user",
            "password": "scannerpass123"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}
    
    @task(8)
    def start_quick_scan(self):
        """Start quick scan"""
        self.client.post("/api/scans", headers=self.headers, json={
            "target_url": f"https://example{random.randint(1, 10)}.com",
            "scan_type": "quick"
        })
    
    @task(2)
    def start_full_scan(self):
        """Start full scan"""
        self.client.post("/api/scans", headers=self.headers, json={
            "target_url": f"https://example{random.randint(1, 10)}.com",
            "scan_type": "full"
        })
    
    @task(5)
    def check_scan_status(self):
        """Check scan status"""
        scan_id = random.randint(1, 100)
        self.client.get(f"/api/scans/{scan_id}/status", headers=self.headers)


class ApiUser(HttpUser):
    """API-only user"""
    
    wait_time = between(0.5, 2)
    
    def on_start(self):
        """Get API key"""
        self.headers = {"X-API-Key": "test_api_key_12345"}
    
    @task(10)
    def api_list_bugs(self):
        """API: List bugs"""
        self.client.get("/api/v1/bugs", headers=self.headers)
    
    @task(5)
    def api_get_bug(self):
        """API: Get specific bug"""
        bug_id = random.randint(1, 100)
        self.client.get(f"/api/v1/bugs/{bug_id}", headers=self.headers)
    
    @task(3)
    def api_create_bug(self):
        """API: Create bug"""
        self.client.post("/api/v1/bugs", headers=self.headers, json={
            "title": f"API Test Bug {random.randint(1, 10000)}",
            "description": "Test bug via API",
            "severity": "medium",
            "target_url": "https://api-test.com"
        })
    
    @task(8)
    def api_list_scans(self):
        """API: List scans"""
        self.client.get("/api/v1/scans", headers=self.headers)
    
    @task(2)
    def api_get_stats(self):
        """API: Get statistics"""
        self.client.get("/api/v1/stats", headers=self.headers)
