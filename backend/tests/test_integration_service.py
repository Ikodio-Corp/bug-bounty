"""
Test integration services
"""
import pytest
from services.integration_service import IntegrationService
from datetime import datetime


@pytest.fixture
def integration_service():
    return IntegrationService()


class TestGitHubIntegration:
    """Test GitHub integration"""
    
    def test_connect_github(self, integration_service, db_session, test_user):
        """Test connecting GitHub account"""
        result = integration_service.connect_github(
            db_session,
            test_user.id,
            access_token="ghp_test_token",
            username="testuser"
        )
        
        assert result is True
    
    def test_import_github_repos(self, integration_service, db_session, test_user):
        """Test importing GitHub repositories"""
        integration_service.connect_github(
            db_session,
            test_user.id,
            access_token="ghp_test_token",
            username="testuser"
        )
        
        repos = integration_service.import_github_repos(db_session, test_user.id)
        
        assert isinstance(repos, list)
    
    def test_sync_github_issues(self, integration_service, db_session, test_user):
        """Test syncing GitHub issues"""
        result = integration_service.sync_github_issues(
            db_session,
            test_user.id,
            repo_name="test-repo"
        )
        
        assert isinstance(result, dict)


class TestJiraIntegration:
    """Test Jira integration"""
    
    def test_connect_jira(self, integration_service, db_session, test_user):
        """Test connecting Jira account"""
        result = integration_service.connect_jira(
            db_session,
            test_user.id,
            site_url="https://company.atlassian.net",
            api_token="jira_api_token",
            email="user@company.com"
        )
        
        assert result is True
    
    def test_create_jira_issue(self, integration_service, db_session, test_user):
        """Test creating Jira issue"""
        integration_service.connect_jira(
            db_session,
            test_user.id,
            site_url="https://company.atlassian.net",
            api_token="jira_api_token",
            email="user@company.com"
        )
        
        issue_data = {
            "project": "SEC",
            "summary": "XSS Vulnerability Found",
            "description": "Cross-site scripting vulnerability in login form",
            "issue_type": "Bug",
            "priority": "High"
        }
        
        result = integration_service.create_jira_issue(
            db_session,
            test_user.id,
            issue_data
        )
        
        assert "issue_key" in result


class TestSlackIntegration:
    """Test Slack integration"""
    
    def test_connect_slack(self, integration_service, db_session, test_user):
        """Test connecting Slack workspace"""
        result = integration_service.connect_slack(
            db_session,
            test_user.id,
            access_token="xoxb-slack-token",
            workspace_id="T1234567890",
            channel_id="C1234567890"
        )
        
        assert result is True
    
    def test_send_slack_notification(self, integration_service, db_session, test_user):
        """Test sending Slack notification"""
        integration_service.connect_slack(
            db_session,
            test_user.id,
            access_token="xoxb-slack-token",
            workspace_id="T1234567890",
            channel_id="C1234567890"
        )
        
        result = integration_service.send_slack_notification(
            db_session,
            test_user.id,
            message="New critical vulnerability found!"
        )
        
        assert result is True


class TestAwsIntegration:
    """Test AWS integration"""
    
    def test_connect_aws(self, integration_service, db_session, test_user):
        """Test connecting AWS account"""
        result = integration_service.connect_aws(
            db_session,
            test_user.id,
            access_key_id="AKIAIOSFODNN7EXAMPLE",
            secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            region="us-east-1"
        )
        
        assert result is True
    
    def test_scan_aws_resources(self, integration_service, db_session, test_user):
        """Test scanning AWS resources"""
        integration_service.connect_aws(
            db_session,
            test_user.id,
            access_key_id="AKIAIOSFODNN7EXAMPLE",
            secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            region="us-east-1"
        )
        
        result = integration_service.scan_aws_resources(db_session, test_user.id)
        
        assert "ec2_instances" in result
        assert "s3_buckets" in result


class TestAzureIntegration:
    """Test Azure integration"""
    
    def test_connect_azure(self, integration_service, db_session, test_user):
        """Test connecting Azure account"""
        result = integration_service.connect_azure(
            db_session,
            test_user.id,
            subscription_id="12345678-1234-1234-1234-123456789012",
            client_id="87654321-4321-4321-4321-210987654321",
            client_secret="azure_client_secret",
            tenant_id="11111111-1111-1111-1111-111111111111"
        )
        
        assert result is True
    
    def test_scan_azure_resources(self, integration_service, db_session, test_user):
        """Test scanning Azure resources"""
        result = integration_service.scan_azure_resources(db_session, test_user.id)
        
        assert isinstance(result, dict)


class TestGcpIntegration:
    """Test GCP integration"""
    
    def test_connect_gcp(self, integration_service, db_session, test_user):
        """Test connecting GCP account"""
        credentials = {
            "type": "service_account",
            "project_id": "test-project-123456",
            "private_key_id": "key123",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
            "client_email": "service-account@test-project-123456.iam.gserviceaccount.com"
        }
        
        result = integration_service.connect_gcp(
            db_session,
            test_user.id,
            credentials
        )
        
        assert result is True
    
    def test_scan_gcp_resources(self, integration_service, db_session, test_user):
        """Test scanning GCP resources"""
        result = integration_service.scan_gcp_resources(db_session, test_user.id)
        
        assert isinstance(result, dict)


class TestIntegrationManagement:
    """Test integration management"""
    
    def test_get_user_integrations(self, integration_service, db_session, test_user):
        """Test getting user integrations"""
        integrations = integration_service.get_user_integrations(db_session, test_user.id)
        
        assert isinstance(integrations, list)
    
    def test_disconnect_integration(self, integration_service, db_session, test_user):
        """Test disconnecting integration"""
        integration_service.connect_github(
            db_session,
            test_user.id,
            access_token="ghp_test_token",
            username="testuser"
        )
        
        result = integration_service.disconnect_integration(
            db_session,
            test_user.id,
            integration_type="github"
        )
        
        assert result is True
    
    def test_update_integration_settings(self, integration_service, db_session, test_user):
        """Test updating integration settings"""
        integration_service.connect_slack(
            db_session,
            test_user.id,
            access_token="xoxb-slack-token",
            workspace_id="T1234567890",
            channel_id="C1234567890"
        )
        
        result = integration_service.update_integration_settings(
            db_session,
            test_user.id,
            integration_type="slack",
            settings={"notifications_enabled": True, "channel_id": "C0987654321"}
        )
        
        assert result is True
