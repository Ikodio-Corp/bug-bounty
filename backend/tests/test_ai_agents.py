"""
Test AI agents functionality
"""
import pytest
from agents.orchestrator import AgentOrchestrator
from agents.scanner_agent import ScannerAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.predictor_agent import PredictorAgent
from agents.trainer_agent import TrainerAgent
from agents.reporter_agent import ReporterAgent


@pytest.fixture
def orchestrator():
    return AgentOrchestrator()


@pytest.fixture
def scanner_agent():
    return ScannerAgent()


@pytest.fixture
def analyzer_agent():
    return AnalyzerAgent()


@pytest.fixture
def predictor_agent():
    return PredictorAgent()


class TestAgentOrchestrator:
    """Test agent orchestration"""
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator is not None
        assert hasattr(orchestrator, 'agents')
    
    def test_execute_scan_workflow(self, orchestrator, db_session):
        """Test executing full scan workflow"""
        target = "https://example.com"
        scan_type = "comprehensive"
        
        result = orchestrator.execute_scan_workflow(
            db_session,
            target=target,
            scan_type=scan_type
        )
        
        assert result is not None
        assert "scan_id" in result
        assert "status" in result
    
    def test_coordinate_agents(self, orchestrator):
        """Test agent coordination"""
        task = {
            "type": "security_scan",
            "target": "https://test.com",
            "agents": ["scanner", "analyzer"]
        }
        
        result = orchestrator.coordinate_agents(task)
        
        assert isinstance(result, dict)


class TestScannerAgent:
    """Test scanner agent"""
    
    def test_scanner_initialization(self, scanner_agent):
        """Test scanner agent initializes"""
        assert scanner_agent is not None
    
    def test_perform_scan(self, scanner_agent):
        """Test performing security scan"""
        target = "https://example.com"
        scan_config = {
            "scan_type": "quick",
            "depth": 2,
            "timeout": 300
        }
        
        result = scanner_agent.scan(target, scan_config)
        
        assert result is not None
        assert "vulnerabilities" in result
    
    def test_scan_with_custom_rules(self, scanner_agent):
        """Test scanning with custom rules"""
        target = "https://example.com"
        custom_rules = [
            {"type": "xss", "pattern": "<script>"},
            {"type": "sqli", "pattern": "' OR '1'='1"}
        ]
        
        result = scanner_agent.scan_with_rules(target, custom_rules)
        
        assert isinstance(result, dict)


class TestAnalyzerAgent:
    """Test analyzer agent"""
    
    def test_analyzer_initialization(self, analyzer_agent):
        """Test analyzer agent initializes"""
        assert analyzer_agent is not None
    
    def test_analyze_vulnerabilities(self, analyzer_agent):
        """Test analyzing vulnerabilities"""
        vulnerabilities = [
            {
                "type": "XSS",
                "severity": "high",
                "location": "/login",
                "description": "Reflected XSS in login form"
            },
            {
                "type": "SQL Injection",
                "severity": "critical",
                "location": "/api/users",
                "description": "SQL injection in user endpoint"
            }
        ]
        
        result = analyzer_agent.analyze(vulnerabilities)
        
        assert result is not None
        assert "analysis" in result
        assert "recommendations" in result
    
    def test_prioritize_findings(self, analyzer_agent):
        """Test prioritizing scan findings"""
        findings = [
            {"severity": "low", "exploitability": 0.3},
            {"severity": "critical", "exploitability": 0.9},
            {"severity": "medium", "exploitability": 0.5}
        ]
        
        result = analyzer_agent.prioritize(findings)
        
        assert len(result) == 3
        assert result[0]["severity"] == "critical"
    
    def test_generate_exploit_chain(self, analyzer_agent):
        """Test generating exploit chains"""
        vulnerabilities = [
            {"type": "XSS", "location": "/page1"},
            {"type": "CSRF", "location": "/page2"}
        ]
        
        result = analyzer_agent.generate_exploit_chain(vulnerabilities)
        
        assert isinstance(result, dict)


class TestPredictorAgent:
    """Test predictor agent"""
    
    def test_predictor_initialization(self, predictor_agent):
        """Test predictor agent initializes"""
        assert predictor_agent is not None
    
    def test_predict_vulnerabilities(self, predictor_agent):
        """Test predicting potential vulnerabilities"""
        code_sample = """
        def login(username, password):
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            return db.execute(query)
        """
        
        result = predictor_agent.predict(code_sample)
        
        assert result is not None
        assert "predictions" in result
        assert len(result["predictions"]) > 0
    
    def test_forecast_vulnerability_trends(self, predictor_agent, db_session):
        """Test forecasting vulnerability trends"""
        result = predictor_agent.forecast_trends(db_session, days=30)
        
        assert result is not None
        assert "forecast" in result
    
    def test_risk_assessment(self, predictor_agent):
        """Test risk assessment"""
        system_data = {
            "technologies": ["React", "Node.js", "PostgreSQL"],
            "exposure": "public",
            "security_measures": ["HTTPS", "CORS"]
        }
        
        result = predictor_agent.assess_risk(system_data)
        
        assert "risk_score" in result
        assert 0 <= result["risk_score"] <= 100


class TestTrainerAgent:
    """Test trainer agent"""
    
    def test_trainer_initialization(self):
        """Test trainer agent initializes"""
        trainer = TrainerAgent()
        assert trainer is not None
    
    def test_train_model(self, db_session):
        """Test training AI model"""
        trainer = TrainerAgent()
        
        training_data = [
            {"input": "SELECT * FROM users WHERE id=1", "label": "safe"},
            {"input": "SELECT * FROM users WHERE id=1' OR '1'='1", "label": "vulnerable"}
        ]
        
        result = trainer.train(training_data)
        
        assert result is not None
        assert "accuracy" in result
    
    def test_evaluate_model(self):
        """Test evaluating model performance"""
        trainer = TrainerAgent()
        
        test_data = [
            {"input": "safe code", "label": "safe"},
            {"input": "malicious code", "label": "vulnerable"}
        ]
        
        result = trainer.evaluate(test_data)
        
        assert "metrics" in result


class TestReporterAgent:
    """Test reporter agent"""
    
    def test_reporter_initialization(self):
        """Test reporter agent initializes"""
        reporter = ReporterAgent()
        assert reporter is not None
    
    def test_generate_report(self, db_session):
        """Test generating security report"""
        reporter = ReporterAgent()
        
        scan_data = {
            "scan_id": 1,
            "target": "https://example.com",
            "vulnerabilities": [
                {"type": "XSS", "severity": "high"},
                {"type": "CSRF", "severity": "medium"}
            ],
            "summary": {
                "total_found": 2,
                "critical": 0,
                "high": 1,
                "medium": 1,
                "low": 0
            }
        }
        
        result = reporter.generate_report(scan_data, format="pdf")
        
        assert result is not None
        assert "report_path" in result
    
    def test_generate_executive_summary(self):
        """Test generating executive summary"""
        reporter = ReporterAgent()
        
        scan_results = {
            "total_scans": 10,
            "vulnerabilities_found": 25,
            "critical_issues": 3,
            "remediation_rate": 0.85
        }
        
        result = reporter.generate_executive_summary(scan_results)
        
        assert isinstance(result, str)
        assert len(result) > 0
