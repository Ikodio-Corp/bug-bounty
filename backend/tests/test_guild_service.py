"""
Test guild/community features
"""
import pytest
from services.guild_service import GuildService
from models.community import GuildMembership, GuildProposal
from datetime import datetime


@pytest.fixture
def guild_service():
    return GuildService()


class TestGuildManagement:
    """Test guild management functions"""
    
    def test_create_guild(self, guild_service, db_session, test_user):
        """Test creating a guild"""
        guild_data = {
            "name": "Security Researchers Guild",
            "description": "A community of security researchers",
            "founder_id": test_user.id,
            "is_public": True,
            "requirements": {
                "min_reputation": 100,
                "min_bugs_found": 5
            }
        }
        
        guild = guild_service.create_guild(db_session, guild_data)
        
        assert guild.id is not None
        assert guild.name == guild_data["name"]
        assert guild.founder_id == test_user.id
    
    def test_join_guild(self, guild_service, db_session, test_user):
        """Test joining a guild"""
        guild = guild_service.create_guild(db_session, {
            "name": "Test Guild",
            "description": "Test description",
            "founder_id": test_user.id,
            "is_public": True
        })
        
        # Create another user
        from models.user import User
        member = User(
            username="member",
            email="member@test.com",
            hashed_password="hashed"
        )
        db_session.add(member)
        db_session.commit()
        
        result = guild_service.join_guild(db_session, guild.id, member.id)
        
        assert result is True
    
    def test_leave_guild(self, guild_service, db_session, test_user):
        """Test leaving a guild"""
        guild = guild_service.create_guild(db_session, {
            "name": "Leave Test Guild",
            "description": "Test",
            "founder_id": test_user.id,
            "is_public": True
        })
        
        from models.user import User
        member = User(
            username="leaving_member",
            email="leaving@test.com",
            hashed_password="hashed"
        )
        db_session.add(member)
        db_session.commit()
        
        guild_service.join_guild(db_session, guild.id, member.id)
        result = guild_service.leave_guild(db_session, guild.id, member.id)
        
        assert result is True
    
    def test_get_guild_members(self, guild_service, db_session, test_user):
        """Test getting guild members"""
        guild = guild_service.create_guild(db_session, {
            "name": "Members Guild",
            "description": "Test",
            "founder_id": test_user.id,
            "is_public": True
        })
        
        members = guild_service.get_guild_members(db_session, guild.id)
        
        assert len(members) >= 1  # At least founder


class TestGuildProposals:
    """Test guild proposal system"""
    
    def test_create_proposal(self, guild_service, db_session, test_user):
        """Test creating a guild proposal"""
        guild = guild_service.create_guild(db_session, {
            "name": "Proposal Guild",
            "description": "Test",
            "founder_id": test_user.id,
            "is_public": True
        })
        
        proposal_data = {
            "guild_id": guild.id,
            "proposer_id": test_user.id,
            "title": "Increase Member Benefits",
            "description": "Proposal to increase member benefits",
            "proposal_type": "benefit_change",
            "voting_deadline": "2025-12-31"
        }
        
        proposal = guild_service.create_proposal(db_session, proposal_data)
        
        assert proposal.id is not None
        assert proposal.status == "active"
    
    def test_vote_on_proposal(self, guild_service, db_session, test_user):
        """Test voting on proposal"""
        guild = guild_service.create_guild(db_session, {
            "name": "Voting Guild",
            "description": "Test",
            "founder_id": test_user.id,
            "is_public": True
        })
        
        proposal = guild_service.create_proposal(db_session, {
            "guild_id": guild.id,
            "proposer_id": test_user.id,
            "title": "Test Proposal",
            "description": "Description",
            "proposal_type": "general",
            "voting_deadline": "2025-12-31"
        })
        
        result = guild_service.vote_on_proposal(
            db_session,
            proposal.id,
            test_user.id,
            vote="yes"
        )
        
        assert result is True
    
    def test_execute_proposal(self, guild_service, db_session, test_user):
        """Test executing approved proposal"""
        guild = guild_service.create_guild(db_session, {
            "name": "Execute Guild",
            "description": "Test",
            "founder_id": test_user.id,
            "is_public": True
        })
        
        proposal = guild_service.create_proposal(db_session, {
            "guild_id": guild.id,
            "proposer_id": test_user.id,
            "title": "Execute Test",
            "description": "Description",
            "proposal_type": "general",
            "voting_deadline": "2025-12-31"
        })
        
        guild_service.vote_on_proposal(db_session, proposal.id, test_user.id, "yes")
        
        result = guild_service.execute_proposal(db_session, proposal.id)
        
        assert result is not None


class TestGuildEvents:
    """Test guild events system"""
    
    def test_create_event(self, guild_service, db_session, test_user):
        """Test creating guild event"""
        guild = guild_service.create_guild(db_session, {
            "name": "Event Guild",
            "description": "Test",
            "founder_id": test_user.id,
            "is_public": True
        })
        
        event_data = {
            "guild_id": guild.id,
            "title": "Security Workshop",
            "description": "Learn about web security",
            "event_date": "2025-12-15",
            "location": "Virtual",
            "max_participants": 50
        }
        
        event = guild_service.create_event(db_session, event_data)
        
        assert event.id is not None
    
    def test_register_for_event(self, guild_service, db_session, test_user):
        """Test registering for event"""
        guild = guild_service.create_guild(db_session, {
            "name": "Register Guild",
            "description": "Test",
            "founder_id": test_user.id,
            "is_public": True
        })
        
        event = guild_service.create_event(db_session, {
            "guild_id": guild.id,
            "title": "Test Event",
            "description": "Description",
            "event_date": "2025-12-20",
            "location": "Online",
            "max_participants": 100
        })
        
        result = guild_service.register_for_event(
            db_session,
            event.id,
            test_user.id
        )
        
        assert result is True


class TestGuildRewards:
    """Test guild reward system"""
    
    def test_distribute_rewards(self, guild_service, db_session, test_user):
        """Test distributing guild rewards"""
        guild = guild_service.create_guild(db_session, {
            "name": "Reward Guild",
            "description": "Test",
            "founder_id": test_user.id,
            "is_public": True
        })
        
        result = guild_service.distribute_rewards(
            db_session,
            guild.id,
            total_amount=1000.00,
            distribution_type="equal"
        )
        
        assert result is not None
    
    def test_claim_reward(self, guild_service, db_session, test_user):
        """Test claiming guild reward"""
        guild = guild_service.create_guild(db_session, {
            "name": "Claim Guild",
            "description": "Test",
            "founder_id": test_user.id,
            "is_public": True
        })
        
        guild_service.distribute_rewards(
            db_session,
            guild.id,
            total_amount=500.00,
            distribution_type="equal"
        )
        
        result = guild_service.claim_reward(db_session, test_user.id, guild.id)
        
        assert result is not None


class TestGuildRanking:
    """Test guild ranking system"""
    
    def test_get_guild_rankings(self, guild_service, db_session):
        """Test getting guild rankings"""
        rankings = guild_service.get_guild_rankings(db_session, limit=10)
        
        assert isinstance(rankings, list)
    
    def test_update_guild_stats(self, guild_service, db_session, test_user):
        """Test updating guild statistics"""
        guild = guild_service.create_guild(db_session, {
            "name": "Stats Guild",
            "description": "Test",
            "founder_id": test_user.id,
            "is_public": True
        })
        
        result = guild_service.update_guild_stats(
            db_session,
            guild.id,
            stats={
                "total_bugs_found": 50,
                "total_bounty_earned": 10000.00,
                "active_members": 15
            }
        )
        
        assert result is True
