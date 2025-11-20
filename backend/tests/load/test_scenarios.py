"""
Load Testing Scenarios for IKODIO BugBounty Platform
Comprehensive performance testing with Locust
"""

from locust import HttpUser, task, between, SequentialTaskSet, TaskSet
import random
import json
from datetime import datetime, timedelta

class AuthTaskSet(SequentialTaskSet):
    """Authentication flow testing"""
    
    @task
    def login(self):
        """Test login endpoint"""
        self.client.post("/api/auth/login", json={
            "email": f"user{random.randint(1, 1000)}@example.com",
            "password": "TestPassword123!"
        })
    
    @task
    def register(self):
        """Test registration endpoint"""
        timestamp = datetime.now().isoformat()
        self.client.post("/api/auth/register", json={
            "email": f"newuser{timestamp}@example.com",
            "password": "TestPassword123!",
            "username": f"user_{timestamp}"
        })
    
    @task
    def refresh_token(self):
        """Test token refresh"""
        self.client.post("/api/auth/refresh")
    
    @task
    def logout(self):
        """Test logout endpoint"""
        self.client.post("/api/auth/logout")
        self.interrupt()  # End sequence


class BugReportTaskSet(TaskSet):
    """Bug reporting and management testing"""
    
    @task(3)
    def list_bugs(self):
        """Test bug listing with pagination"""
        page = random.randint(1, 10)
        per_page = random.choice([10, 25, 50, 100])
        self.client.get(f"/api/bugs?page={page}&per_page={per_page}")
    
    @task(2)
    def filter_bugs(self):
        """Test bug filtering"""
        severity = random.choice(["low", "medium", "high", "critical"])
        status = random.choice(["open", "in_progress", "resolved", "closed"])
        self.client.get(f"/api/bugs?severity={severity}&status={status}")
    
    @task(1)
    def create_bug(self):
        """Test bug creation"""
        self.client.post("/api/bugs", json={
            "title": f"Test Bug {random.randint(1, 10000)}",
            "description": "This is a test bug report for load testing",
            "severity": random.choice(["low", "medium", "high", "critical"]),
            "category": random.choice(["xss", "sqli", "csrf", "rce", "idor"]),
            "url": "https://example.com/vulnerable",
            "steps_to_reproduce": "1. Step 1\n2. Step 2\n3. Step 3"
        })
    
    @task(2)
    def get_bug_detail(self):
        """Test single bug retrieval"""
        bug_id = random.randint(1, 1000)
        self.client.get(f"/api/bugs/{bug_id}")
    
    @task(1)
    def update_bug(self):
        """Test bug update"""
        bug_id = random.randint(1, 1000)
        self.client.patch(f"/api/bugs/{bug_id}", json={
            "status": random.choice(["open", "in_progress", "resolved"])
        })
    
    @task(1)
    def add_comment(self):
        """Test adding comment to bug"""
        bug_id = random.randint(1, 1000)
        self.client.post(f"/api/bugs/{bug_id}/comments", json={
            "content": f"Test comment at {datetime.now().isoformat()}"
        })


class ScanTaskSet(TaskSet):
    """Security scanning testing"""
    
    @task(2)
    def list_scans(self):
        """Test scan listing"""
        self.client.get("/api/scans")
    
    @task(1)
    def create_scan(self):
        """Test scan creation"""
        self.client.post("/api/scans", json={
            "target": f"https://target{random.randint(1, 100)}.example.com",
            "scan_type": random.choice(["quick", "full", "custom"]),
            "scanner": random.choice(["zap", "nuclei", "burp", "custom"])
        })
    
    @task(3)
    def get_scan_status(self):
        """Test scan status check"""
        scan_id = random.randint(1, 500)
        self.client.get(f"/api/scans/{scan_id}")
    
    @task(2)
    def get_scan_results(self):
        """Test scan results retrieval"""
        scan_id = random.randint(1, 500)
        self.client.get(f"/api/scans/{scan_id}/results")
    
    @task(1)
    def cancel_scan(self):
        """Test scan cancellation"""
        scan_id = random.randint(1, 500)
        self.client.post(f"/api/scans/{scan_id}/cancel")


class AnalyticsTaskSet(TaskSet):
    """Analytics endpoint testing"""
    
    @task(3)
    def get_analytics(self):
        """Test basic analytics"""
        time_range = random.choice(["24h", "7d", "30d", "90d"])
        self.client.get(f"/api/analytics?range={time_range}")
    
    @task(2)
    def get_advanced_analytics(self):
        """Test advanced analytics"""
        time_range = random.choice(["24h", "7d", "30d", "90d"])
        self.client.get(f"/api/analytics/advanced?range={time_range}")
    
    @task(1)
    def export_analytics(self):
        """Test analytics export"""
        format_type = random.choice(["csv", "json", "pdf"])
        self.client.get(f"/api/analytics/export?format={format_type}&range=7d")
    
    @task(2)
    def get_dashboard_metrics(self):
        """Test dashboard metrics"""
        self.client.get("/api/analytics/dashboard")


class MarketplaceTaskSet(TaskSet):
    """Marketplace testing"""
    
    @task(3)
    def browse_marketplace(self):
        """Test marketplace browsing"""
        page = random.randint(1, 5)
        self.client.get(f"/api/marketplace?page={page}")
    
    @task(2)
    def search_marketplace(self):
        """Test marketplace search"""
        query = random.choice(["scanner", "tool", "course", "service"])
        self.client.get(f"/api/marketplace/search?q={query}")
    
    @task(1)
    def get_item_details(self):
        """Test item detail retrieval"""
        item_id = random.randint(1, 100)
        self.client.get(f"/api/marketplace/items/{item_id}")
    
    @task(1)
    def purchase_item(self):
        """Test purchase flow"""
        item_id = random.randint(1, 100)
        self.client.post(f"/api/marketplace/purchase", json={
            "item_id": item_id,
            "payment_method": "stripe"
        })


class WebSocketTaskSet(TaskSet):
    """WebSocket connection testing"""
    
    @task
    def connect_websocket(self):
        """Test WebSocket connection"""
        # Note: Locust doesn't natively support WebSocket
        # This would require additional library like locust-plugins
        pass


class NormalUser(HttpUser):
    """Normal user behavior simulation"""
    wait_time = between(1, 5)
    weight = 10
    
    tasks = {
        BugReportTaskSet: 5,
        ScanTaskSet: 3,
        AnalyticsTaskSet: 2,
        MarketplaceTaskSet: 1,
    }
    
    def on_start(self):
        """Login before starting tasks"""
        self.client.post("/api/auth/login", json={
            "email": f"user{random.randint(1, 1000)}@example.com",
            "password": "TestPassword123!"
        })


class PowerUser(HttpUser):
    """Power user with higher activity"""
    wait_time = between(0.5, 2)
    weight = 3
    
    tasks = {
        BugReportTaskSet: 6,
        ScanTaskSet: 5,
        AnalyticsTaskSet: 3,
        MarketplaceTaskSet: 2,
    }
    
    def on_start(self):
        """Login before starting tasks"""
        self.client.post("/api/auth/login", json={
            "email": f"poweruser{random.randint(1, 100)}@example.com",
            "password": "TestPassword123!"
        })


class AdminUser(HttpUser):
    """Admin user with full access"""
    wait_time = between(2, 8)
    weight = 1
    
    tasks = {
        AnalyticsTaskSet: 5,
        BugReportTaskSet: 3,
        ScanTaskSet: 2,
    }
    
    def on_start(self):
        """Login as admin"""
        self.client.post("/api/auth/login", json={
            "email": "admin@ikodio.com",
            "password": "AdminPassword123!"
        })
    
    @task(3)
    def admin_dashboard(self):
        """Access admin dashboard"""
        self.client.get("/api/admin/dashboard")
    
    @task(2)
    def manage_users(self):
        """Manage users"""
        self.client.get("/api/admin/users")
    
    @task(1)
    def system_health(self):
        """Check system health"""
        self.client.get("/api/health")


class BurstTrafficUser(HttpUser):
    """Simulate burst traffic patterns"""
    wait_time = between(0.1, 0.5)
    weight = 2
    
    @task(10)
    def rapid_requests(self):
        """Generate rapid requests"""
        endpoints = [
            "/api/bugs",
            "/api/scans",
            "/api/analytics",
            "/api/marketplace"
        ]
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)


class DatabaseShardingTest(HttpUser):
    """Test database sharding performance"""
    wait_time = between(1, 3)
    weight = 2
    
    @task
    def test_cross_shard_query(self):
        """Test queries across shards"""
        # Query users from different shards
        user_ids = [random.randint(1, 10000) for _ in range(5)]
        self.client.post("/api/users/batch", json={"user_ids": user_ids})
    
    @task
    def test_shard_specific_query(self):
        """Test shard-specific query"""
        shard_id = random.randint(0, 2)
        self.client.get(f"/api/bugs?shard={shard_id}")


class ConcurrentScanTest(HttpUser):
    """Test concurrent scanning capacity"""
    wait_time = between(0.5, 2)
    weight = 3
    
    @task
    def concurrent_scans(self):
        """Launch multiple concurrent scans"""
        for _ in range(random.randint(1, 5)):
            self.client.post("/api/scans", json={
                "target": f"https://target{random.randint(1, 1000)}.example.com",
                "scan_type": "quick"
            })


class RateLimitTest(HttpUser):
    """Test rate limiting implementation"""
    wait_time = between(0, 0.1)
    weight = 1
    
    @task
    def hammer_endpoint(self):
        """Test rate limiting"""
        endpoint = random.choice(["/api/bugs", "/api/scans", "/api/analytics"])
        for _ in range(100):
            response = self.client.get(endpoint)
            if response.status_code == 429:
                print(f"Rate limit hit: {endpoint}")
                break


class CacheEfficiencyTest(HttpUser):
    """Test caching performance"""
    wait_time = between(0.5, 1)
    weight = 2
    
    @task(5)
    def cached_analytics(self):
        """Test cached analytics endpoint"""
        # Same time range to hit cache
        self.client.get("/api/analytics?range=7d")
    
    @task(2)
    def cache_miss(self):
        """Force cache miss"""
        random_range = random.choice(["1h", "6h", "12h", "24h"])
        self.client.get(f"/api/analytics?range={random_range}")
