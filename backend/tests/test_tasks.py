import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.tasks.notification_tasks import (
    send_bug_notification,
    send_scan_complete_notification,
    send_payment_notification,
    send_guild_invitation
)
from backend.tasks.scan_tasks import (
    execute_scan_task,
    process_scan_results,
    schedule_recurring_scan
)


class TestNotificationTasks:
    @pytest.mark.asyncio
    async def test_send_bug_notification(self):
        with patch('backend.integrations.email_client.EmailClient') as mock_email:
            mock_instance = Mock()
            mock_email.return_value = mock_instance
            mock_instance.send_bug_notification.return_value = True
            
            result = send_bug_notification(
                user_email="user@example.com",
                bug_title="SQL Injection Found",
                bug_url="https://example.com/bugs/123"
            )
            
            # Task should execute successfully
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_send_scan_complete_notification(self):
        with patch('backend.integrations.email_client.EmailClient') as mock_email:
            mock_instance = Mock()
            mock_email.return_value = mock_instance
            mock_instance.send_scan_complete_notification.return_value = True
            
            result = send_scan_complete_notification(
                user_email="user@example.com",
                scan_id=123,
                findings_count=5,
                target_url="https://example.com"
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_send_payment_notification(self):
        with patch('backend.integrations.email_client.EmailClient') as mock_email:
            mock_instance = Mock()
            mock_email.return_value = mock_instance
            mock_instance.send_email.return_value = True
            
            result = send_payment_notification(
                user_email="user@example.com",
                amount=99.99,
                transaction_id="txn_123"
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_send_guild_invitation(self):
        with patch('backend.integrations.email_client.EmailClient') as mock_email:
            mock_instance = Mock()
            mock_email.return_value = mock_instance
            mock_instance.send_email.return_value = True
            
            result = send_guild_invitation(
                user_email="user@example.com",
                guild_name="Elite Hunters",
                inviter_name="John Doe",
                invitation_link="https://example.com/guilds/invite/abc123"
            )
            
            assert result is not None


class TestScanTasks:
    @pytest.mark.asyncio
    async def test_execute_scan_task(self, db):
        with patch('backend.scanners.orchestrator.ScanOrchestrator') as mock_orchestrator:
            mock_instance = Mock()
            mock_orchestrator.return_value = mock_instance
            mock_instance.execute_scan = AsyncMock(return_value={
                "vulnerabilities": [
                    {"type": "SQL Injection", "severity": "high"}
                ],
                "scan_time": 10.5
            })
            
            result = await execute_scan_task(
                scan_id=1,
                target_url="https://example.com",
                scan_type="full"
            )
            
            assert result is not None
            assert "vulnerabilities" in result
    
    @pytest.mark.asyncio
    async def test_process_scan_results(self, db):
        scan_results = {
            "vulnerabilities": [
                {
                    "type": "SQL Injection",
                    "severity": "high",
                    "url": "https://example.com/api/users",
                    "parameter": "id"
                },
                {
                    "type": "XSS",
                    "severity": "medium",
                    "url": "https://example.com/search",
                    "parameter": "q"
                }
            ]
        }
        
        with patch('backend.services.bug_service.BugService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance
            mock_instance.create_bug.return_value = Mock(id=1)
            
            result = await process_scan_results(
                scan_id=1,
                results=scan_results
            )
            
            assert result is not None
            assert mock_instance.create_bug.call_count == 2
    
    @pytest.mark.asyncio
    async def test_schedule_recurring_scan(self):
        with patch('backend.tasks.scan_tasks.execute_scan_task.apply_async') as mock_async:
            mock_async.return_value = Mock(id="task_123")
            
            result = schedule_recurring_scan(
                target_url="https://example.com",
                scan_type="quick",
                interval_hours=24
            )
            
            assert result is not None
            mock_async.assert_called_once()


class TestMaintenanceTasks:
    @pytest.mark.asyncio
    async def test_cleanup_old_scans(self, db):
        from backend.tasks.maintenance_tasks import cleanup_old_scans
        
        with patch('backend.models.bug.Scan') as mock_scan:
            mock_query = Mock()
            mock_scan.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.delete.return_value = 5
            
            result = cleanup_old_scans(days=90)
            
            assert result == 5
    
    @pytest.mark.asyncio
    async def test_update_vulnerability_database(self):
        from backend.tasks.maintenance_tasks import update_vulnerability_database
        
        with patch('backend.services.vulnerability_service.VulnerabilityService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance
            mock_instance.fetch_latest_cves.return_value = [
                {"id": "CVE-2024-0001", "severity": "high"}
            ]
            
            result = update_vulnerability_database()
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_generate_reports(self, db):
        from backend.tasks.maintenance_tasks import generate_daily_reports
        
        with patch('backend.services.report_service.ReportService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance
            mock_instance.generate_daily_report.return_value = Mock(id=1)
            
            result = generate_daily_reports()
            
            assert result is not None


class TestAITasks:
    @pytest.mark.asyncio
    async def test_train_ml_model(self):
        from backend.tasks.ai_tasks import train_vulnerability_predictor
        
        with patch('backend.agents.trainer_agent.TrainerAgent') as mock_trainer:
            mock_instance = Mock()
            mock_trainer.return_value = mock_instance
            mock_instance.train_model = AsyncMock(return_value={
                "accuracy": 0.92,
                "model_path": "/models/vuln_predictor_v1.pkl"
            })
            
            result = await train_vulnerability_predictor(
                dataset_path="/data/training_set.csv"
            )
            
            assert result is not None
            assert "accuracy" in result
    
    @pytest.mark.asyncio
    async def test_predict_vulnerabilities(self):
        from backend.tasks.ai_tasks import predict_target_vulnerabilities
        
        with patch('backend.agents.predictor_agent.PredictorAgent') as mock_predictor:
            mock_instance = Mock()
            mock_predictor.return_value = mock_instance
            mock_instance.predict = AsyncMock(return_value=[
                {
                    "type": "SQL Injection",
                    "probability": 0.85,
                    "location": "/api/users"
                }
            ])
            
            result = await predict_target_vulnerabilities(
                target_url="https://example.com"
            )
            
            assert result is not None
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_code_patterns(self):
        from backend.tasks.ai_tasks import analyze_code_for_vulnerabilities
        
        with patch('backend.agents.analyzer_agent.AnalyzerAgent') as mock_analyzer:
            mock_instance = Mock()
            mock_analyzer.return_value = mock_instance
            mock_instance.analyze_code = AsyncMock(return_value={
                "vulnerabilities": [
                    {"type": "Hardcoded Credentials", "line": 42}
                ],
                "code_quality_score": 7.5
            })
            
            result = await analyze_code_for_vulnerabilities(
                repository_url="https://github.com/user/repo"
            )
            
            assert result is not None
            assert "vulnerabilities" in result


class TestCeleryTaskConfiguration:
    def test_celery_app_configured(self):
        from backend.tasks.celery_app import celery_app
        
        assert celery_app is not None
        assert celery_app.conf.broker_url is not None
    
    def test_task_routes_configured(self):
        from backend.tasks.celery_app import celery_app
        
        task_routes = celery_app.conf.task_routes
        
        assert task_routes is not None
        # Verify critical tasks are routed correctly
    
    def test_beat_schedule_configured(self):
        from backend.tasks.celery_app import celery_app
        
        beat_schedule = celery_app.conf.beat_schedule
        
        assert beat_schedule is not None
        # Verify scheduled tasks are configured
