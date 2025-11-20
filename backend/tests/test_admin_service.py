"""
Test admin dashboard functionality
"""
import pytest
from services.admin_service import AdminService
from models.user import User
from models.bug import Bug
from datetime import datetime, timedelta


@pytest.fixture
def admin_service():
    return AdminService()


@pytest.fixture
def admin_user(db_session):
    """Create an admin user"""
    admin = User(
        username="admin",
        email="admin@ikodio.com",
        hashed_password="hashed_password",
        role="admin",
        is_verified=True,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    return admin


class TestAdminDashboard:
    """Test admin dashboard statistics"""
    
    def test_get_platform_stats(self, admin_service, db_session, admin_user):
        """Test getting platform statistics"""
        stats = admin_service.get_platform_stats(db_session)
        
        assert "total_users" in stats
        assert "total_bugs" in stats
        assert "total_scans" in stats
        assert "total_revenue" in stats
        assert stats["total_users"] >= 0
    
    def test_get_user_growth(self, admin_service, db_session, admin_user):
        """Test user growth statistics"""
        growth = admin_service.get_user_growth(db_session, days=30)
        
        assert "labels" in growth
        assert "data" in growth
        assert len(growth["labels"]) == 30
    
    def test_get_revenue_stats(self, admin_service, db_session, admin_user):
        """Test revenue statistics"""
        revenue = admin_service.get_revenue_stats(db_session, days=30)
        
        assert "total_revenue" in revenue
        assert "daily_revenue" in revenue
        assert revenue["total_revenue"] >= 0


class TestUserManagement:
    """Test user management functions"""
    
    def test_get_all_users(self, admin_service, db_session, admin_user, test_user):
        """Test retrieving all users"""
        users = admin_service.get_all_users(db_session, skip=0, limit=10)
        
        assert len(users) >= 2
        assert any(u.username == "admin" for u in users)
    
    def test_suspend_user(self, admin_service, db_session, admin_user, test_user):
        """Test suspending a user"""
        result = admin_service.suspend_user(db_session, test_user.id, reason="Test suspension")
        
        assert result is True
        db_session.refresh(test_user)
        assert test_user.is_active is False
    
    def test_activate_user(self, admin_service, db_session, admin_user, test_user):
        """Test activating a suspended user"""
        admin_service.suspend_user(db_session, test_user.id)
        result = admin_service.activate_user(db_session, test_user.id)
        
        assert result is True
        db_session.refresh(test_user)
        assert test_user.is_active is True
    
    def test_delete_user(self, admin_service, db_session, admin_user):
        """Test deleting a user"""
        # Create a test user to delete
        user = User(
            username="to_delete",
            email="delete@test.com",
            hashed_password="hashed"
        )
        db_session.add(user)
        db_session.commit()
        
        user_id = user.id
        result = admin_service.delete_user(db_session, user_id)
        
        assert result is True
        assert db_session.query(User).filter_by(id=user_id).first() is None


class TestBugManagement:
    """Test bug management functions"""
    
    def test_get_all_bugs(self, admin_service, db_session, admin_user):
        """Test retrieving all bugs"""
        bugs = admin_service.get_all_bugs(db_session, skip=0, limit=10)
        
        assert isinstance(bugs, list)
    
    def test_update_bug_status(self, admin_service, db_session, admin_user, test_user):
        """Test updating bug status"""
        # Create a test bug
        bug = Bug(
            title="Test Bug",
            description="Description",
            severity="high",
            status="pending",
            reporter_id=test_user.id
        )
        db_session.add(bug)
        db_session.commit()
        
        result = admin_service.update_bug_status(
            db_session, 
            bug.id, 
            "verified"
        )
        
        assert result is True
        db_session.refresh(bug)
        assert bug.status == "verified"
    
    def test_assign_bug_bounty(self, admin_service, db_session, admin_user, test_user):
        """Test assigning bounty to a bug"""
        bug = Bug(
            title="Bounty Bug",
            description="High severity bug",
            severity="critical",
            status="verified",
            reporter_id=test_user.id
        )
        db_session.add(bug)
        db_session.commit()
        
        result = admin_service.assign_bug_bounty(
            db_session,
            bug.id,
            amount=500.00
        )
        
        assert result is True
        db_session.refresh(bug)
        assert bug.bounty_amount == 500.00


class TestSystemSettings:
    """Test system settings management"""
    
    def test_get_settings(self, admin_service, db_session, admin_user):
        """Test retrieving system settings"""
        settings = admin_service.get_system_settings(db_session)
        
        assert isinstance(settings, dict)
    
    def test_update_settings(self, admin_service, db_session, admin_user):
        """Test updating system settings"""
        new_settings = {
            "maintenance_mode": False,
            "max_upload_size": 10485760,
            "email_notifications": True
        }
        
        result = admin_service.update_system_settings(db_session, new_settings)
        
        assert result is True
    
    def test_maintenance_mode(self, admin_service, db_session, admin_user):
        """Test maintenance mode toggle"""
        result = admin_service.toggle_maintenance_mode(db_session, enabled=True)
        
        assert result is True
        
        settings = admin_service.get_system_settings(db_session)
        assert settings.get("maintenance_mode") is True
