"""
Additional backend unit tests
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.user import User
from models.bug import Bug, BugSeverity, BugStatus, BugType
from models.community import Scan, Guild
from services.admin_service import AdminService
from services.analytics_service import AnalyticsService
from services.integration_service import IntegrationService


class TestAdminService:
    """Test admin service functionality"""
    
    def test_get_platform_overview(self, db: Session):
        """Test platform overview statistics"""
        admin_service = AdminService(db)
        overview = admin_service.get_platform_overview()
        
        assert "users" in overview
        assert "bugs" in overview
        assert "scans" in overview
        assert "revenue" in overview
        assert overview["users"]["total"] >= 0
    
    def test_get_users_list(self, db: Session, test_user: User):
        """Test users list retrieval"""
        admin_service = AdminService(db)
        result = admin_service.get_users_list(page=1, per_page=10)
        
        assert "users" in result
        assert "pagination" in result
        assert result["pagination"]["page"] == 1
    
    def test_update_user_status(self, db: Session, test_user: User):
        """Test user status update"""
        admin_service = AdminService(db)
        result = admin_service.update_user_status(test_user.id, False)
        
        assert result["success"] is True
        db.refresh(test_user)
        assert test_user.is_active is False
    
    def test_validate_bug(self, db: Session, test_bug: Bug):
        """Test bug validation"""
        admin_service = AdminService(db)
        result = admin_service.validate_bug(test_bug.id, 500.0)
        
        assert result["success"] is True
        db.refresh(test_bug)
        assert test_bug.validated is True
        assert test_bug.bounty_amount == 500.0


class TestAnalyticsService:
    """Test analytics service functionality"""
    
    def test_get_dashboard_stats(self, db: Session, test_user: User):
        """Test dashboard statistics"""
        analytics_service = AnalyticsService(db)
        stats = analytics_service.get_dashboard_stats(test_user.id)
        
        assert "total_bugs" in stats
        assert "total_scans" in stats
        assert "total_earnings" in stats
        assert stats["total_bugs"] >= 0
    
    def test_get_platform_stats(self, db: Session):
        """Test platform-wide statistics"""
        analytics_service = AnalyticsService(db)
        stats = analytics_service.get_platform_stats()
        
        assert "total_users" in stats
        assert "total_bugs" in stats
        assert "total_bounties_paid" in stats
    
    def test_get_bug_trends(self, db: Session):
        """Test bug trends analysis"""
        analytics_service = AnalyticsService(db)
        trends = analytics_service.get_bug_trends(days=30)
        
        assert "daily_counts" in trends
        assert isinstance(trends["daily_counts"], list)


class TestIntegrationService:
    """Test integration service functionality"""
    
    @pytest.mark.asyncio
    async def test_jira_mapping(self):
        """Test Jira severity mapping"""
        integration_service = IntegrationService()
        
        assert integration_service._map_severity_to_jira_priority("critical") == "Highest"
        assert integration_service._map_severity_to_jira_priority("high") == "High"
        assert integration_service._map_severity_to_jira_priority("medium") == "Medium"
    
    @pytest.mark.asyncio
    async def test_linear_mapping(self):
        """Test Linear priority mapping"""
        integration_service = IntegrationService()
        
        assert integration_service._map_severity_to_linear_priority("critical") == 1
        assert integration_service._map_severity_to_linear_priority("medium") == 2
        assert integration_service._map_severity_to_linear_priority("info") == 4
    
    @pytest.mark.asyncio
    async def test_cwe_mapping(self):
        """Test CWE weakness mapping"""
        integration_service = IntegrationService()
        
        assert integration_service._map_type_to_weakness("sql_injection") == 89
        assert integration_service._map_type_to_weakness("xss") == 79
        assert integration_service._map_type_to_weakness("csrf") == 352


class TestBugModel:
    """Test bug model functionality"""
    
    def test_create_bug(self, db: Session, test_user: User):
        """Test bug creation"""
        bug = Bug(
            hunter_id=test_user.id,
            title="Test SQL Injection",
            description="Test description",
            bug_type=BugType.SQL_INJECTION,
            severity=BugSeverity.HIGH,
            target_url="https://example.com",
            target_domain="example.com"
        )
        db.add(bug)
        db.commit()
        
        assert bug.id is not None
        assert bug.title == "Test SQL Injection"
        assert bug.severity == BugSeverity.HIGH
    
    def test_bug_validation_workflow(self, db: Session, test_bug: Bug):
        """Test bug validation workflow"""
        test_bug.validated = True
        test_bug.bounty_amount = 1000.0
        test_bug.validated_at = datetime.utcnow()
        db.commit()
        
        assert test_bug.validated is True
        assert test_bug.bounty_amount == 1000.0
        assert test_bug.validated_at is not None


class TestScanModel:
    """Test scan model functionality"""
    
    def test_create_scan(self, db: Session, test_user: User):
        """Test scan creation"""
        scan = Scan(
            user_id=test_user.id,
            target_url="https://example.com",
            scan_type="full",
            status="pending"
        )
        db.add(scan)
        db.commit()
        
        assert scan.id is not None
        assert scan.status == "pending"
        assert scan.progress == 0
    
    def test_scan_progress_update(self, db: Session, test_scan: Scan):
        """Test scan progress update"""
        test_scan.progress = 50
        test_scan.status = "running"
        db.commit()
        
        assert test_scan.progress == 50
        assert test_scan.status == "running"


class TestUserModel:
    """Test user model functionality"""
    
    def test_reputation_update(self, db: Session, test_user: User):
        """Test reputation score update"""
        initial_reputation = test_user.reputation_score
        test_user.reputation_score += 100
        db.commit()
        
        assert test_user.reputation_score == initial_reputation + 100
    
    def test_bounty_tracking(self, db: Session, test_user: User):
        """Test bounty earnings tracking"""
        test_user.total_bounties_earned += 500.0
        test_user.total_bugs_found += 1
        db.commit()
        
        assert test_user.total_bounties_earned >= 500.0
        assert test_user.total_bugs_found >= 1


@pytest.fixture
def test_user(db: Session) -> User:
    """Create test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        role="hunter",
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_bug(db: Session, test_user: User) -> Bug:
    """Create test bug"""
    bug = Bug(
        hunter_id=test_user.id,
        title="Test Bug",
        description="Test description",
        bug_type=BugType.XSS,
        severity=BugSeverity.MEDIUM,
        target_url="https://test.com",
        target_domain="test.com"
    )
    db.add(bug)
    db.commit()
    db.refresh(bug)
    return bug


@pytest.fixture
def test_scan(db: Session, test_user: User) -> Scan:
    """Create test scan"""
    scan = Scan(
        user_id=test_user.id,
        target_url="https://test.com",
        scan_type="quick",
        status="pending"
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan
