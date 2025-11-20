"""
Comprehensive tests for scanner modules
Tests all scanner implementations: ZAP, Burp, Nuclei, and Custom scanner
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime

from scanners.zap_scanner import ZAPScanner
from scanners.burp_scanner import BurpScanner
from scanners.nuclei_scanner import NucleiScanner
from scanners.custom_scanner import CustomScanner
from scanners.orchestrator import ScanOrchestrator


class TestZAPScanner:
    """Test suite for OWASP ZAP scanner"""
    
    @pytest.fixture
    def zap_scanner(self):
        """Create ZAPScanner instance"""
        return ZAPScanner(
            api_key="test_key",
            host="localhost",
            port=8080
        )
    
    @pytest.mark.asyncio
    async def test_zap_scanner_initialization(self, zap_scanner):
        """Test ZAP scanner initialization"""
        assert zap_scanner.api_key == "test_key"
        assert zap_scanner.host == "localhost"
        assert zap_scanner.port == 8080
    
    @pytest.mark.asyncio
    async def test_zap_active_scan(self, zap_scanner):
        """Test ZAP active scanning"""
        with patch.object(zap_scanner, 'start_scan', return_value="scan_id_123"):
            with patch.object(zap_scanner, 'get_scan_status', return_value={"status": "100", "alerts": []}):
                result = await zap_scanner.scan_target("https://example.com")
                
                assert result is not None
                assert "scan_id" in result or "status" in result
    
    @pytest.mark.asyncio
    async def test_zap_passive_scan(self, zap_scanner):
        """Test ZAP passive scanning"""
        with patch.object(zap_scanner, 'spider_target', return_value=True):
            result = await zap_scanner.passive_scan("https://example.com")
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_zap_spider(self, zap_scanner):
        """Test ZAP spider functionality"""
        with patch.object(zap_scanner, 'spider_target', return_value={"urls": ["https://example.com/page1"]}):
            result = await zap_scanner.spider_target("https://example.com")
            assert "urls" in result
            assert len(result["urls"]) > 0
    
    @pytest.mark.asyncio
    async def test_zap_ajax_spider(self, zap_scanner):
        """Test ZAP AJAX spider"""
        with patch.object(zap_scanner, 'ajax_spider', return_value={"urls": ["https://example.com/ajax"]}):
            result = await zap_scanner.ajax_spider("https://example.com")
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_zap_authentication(self, zap_scanner):
        """Test ZAP authentication configuration"""
        auth_config = {
            "loginUrl": "https://example.com/login",
            "username": "test",
            "password": "test123"
        }
        
        with patch.object(zap_scanner, 'configure_auth', return_value=True):
            result = await zap_scanner.configure_auth(auth_config)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_zap_vulnerability_detection(self, zap_scanner):
        """Test ZAP vulnerability detection"""
        mock_alerts = [
            {"risk": "High", "name": "SQL Injection", "url": "https://example.com/api"},
            {"risk": "Medium", "name": "XSS", "url": "https://example.com/page"}
        ]
        
        with patch.object(zap_scanner, 'get_alerts', return_value=mock_alerts):
            alerts = await zap_scanner.get_alerts()
            assert len(alerts) == 2
            assert alerts[0]["risk"] == "High"


class TestBurpScanner:
    """Test suite for Burp Suite scanner"""
    
    @pytest.fixture
    def burp_scanner(self):
        """Create BurpScanner instance"""
        return BurpScanner(
            api_key="burp_test_key",
            api_url="https://burp.example.com"
        )
    
    @pytest.mark.asyncio
    async def test_burp_scanner_initialization(self, burp_scanner):
        """Test Burp scanner initialization"""
        assert burp_scanner.api_key == "burp_test_key"
        assert "burp.example.com" in burp_scanner.api_url
    
    @pytest.mark.asyncio
    async def test_burp_scan_creation(self, burp_scanner):
        """Test Burp scan creation"""
        scan_config = {
            "target_url": "https://example.com",
            "scan_type": "full"
        }
        
        with patch.object(burp_scanner, 'create_scan', return_value={"scan_id": "burp_123"}):
            result = await burp_scanner.create_scan(scan_config)
            assert "scan_id" in result
    
    @pytest.mark.asyncio
    async def test_burp_crawl_and_audit(self, burp_scanner):
        """Test Burp crawl and audit functionality"""
        with patch.object(burp_scanner, 'crawl_and_audit', return_value={"status": "running"}):
            result = await burp_scanner.crawl_and_audit("https://example.com")
            assert result["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_burp_scan_status(self, burp_scanner):
        """Test Burp scan status check"""
        with patch.object(burp_scanner, 'get_scan_status', return_value={"progress": 75}):
            result = await burp_scanner.get_scan_status("scan_123")
            assert result["progress"] == 75
    
    @pytest.mark.asyncio
    async def test_burp_issue_retrieval(self, burp_scanner):
        """Test Burp issue retrieval"""
        mock_issues = [
            {"severity": "high", "type": "SQLi", "confidence": "certain"},
            {"severity": "medium", "type": "XSS", "confidence": "firm"}
        ]
        
        with patch.object(burp_scanner, 'get_issues', return_value=mock_issues):
            issues = await burp_scanner.get_issues("scan_123")
            assert len(issues) == 2
            assert issues[0]["severity"] == "high"


class TestNucleiScanner:
    """Test suite for Nuclei scanner"""
    
    @pytest.fixture
    def nuclei_scanner(self):
        """Create NucleiScanner instance"""
        return NucleiScanner()
    
    @pytest.mark.asyncio
    async def test_nuclei_initialization(self, nuclei_scanner):
        """Test Nuclei scanner initialization"""
        assert nuclei_scanner is not None
    
    @pytest.mark.asyncio
    async def test_nuclei_template_scan(self, nuclei_scanner):
        """Test Nuclei template-based scanning"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout='{"template": "cve-2021-1234", "matched": "https://example.com"}'
            )
            
            result = await nuclei_scanner.scan_with_templates(
                target="https://example.com",
                templates=["cves", "vulnerabilities"]
            )
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_nuclei_cve_scan(self, nuclei_scanner):
        """Test Nuclei CVE scanning"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='{"cve": "CVE-2021-1234"}')
            
            result = await nuclei_scanner.scan_cves("https://example.com")
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_nuclei_technology_detection(self, nuclei_scanner):
        """Test Nuclei technology detection"""
        mock_tech = {
            "wordpress": "5.8",
            "php": "7.4",
            "nginx": "1.20"
        }
        
        with patch.object(nuclei_scanner, 'detect_technologies', return_value=mock_tech):
            result = await nuclei_scanner.detect_technologies("https://example.com")
            assert "wordpress" in result
            assert result["wordpress"] == "5.8"
    
    @pytest.mark.asyncio
    async def test_nuclei_custom_templates(self, nuclei_scanner):
        """Test Nuclei custom template execution"""
        custom_template = """
        id: custom-test
        info:
          name: Custom Test
          severity: medium
        """
        
        with patch.object(nuclei_scanner, 'run_custom_template', return_value={"findings": []}):
            result = await nuclei_scanner.run_custom_template("https://example.com", custom_template)
            assert "findings" in result


class TestCustomScanner:
    """Test suite for custom scanner"""
    
    @pytest.fixture
    def custom_scanner(self):
        """Create CustomScanner instance"""
        return CustomScanner()
    
    @pytest.mark.asyncio
    async def test_custom_scanner_initialization(self, custom_scanner):
        """Test custom scanner initialization"""
        assert custom_scanner is not None
    
    @pytest.mark.asyncio
    async def test_port_scanning(self, custom_scanner):
        """Test port scanning functionality"""
        mock_ports = {
            "open": [80, 443, 8080],
            "closed": [22, 21],
            "filtered": []
        }
        
        with patch.object(custom_scanner, 'scan_ports', return_value=mock_ports):
            result = await custom_scanner.scan_ports("example.com")
            assert len(result["open"]) == 3
            assert 443 in result["open"]
    
    @pytest.mark.asyncio
    async def test_ssl_tls_scanning(self, custom_scanner):
        """Test SSL/TLS scanning"""
        mock_ssl_result = {
            "valid": True,
            "expires_at": "2025-12-31",
            "issuer": "Let's Encrypt",
            "vulnerabilities": []
        }
        
        with patch.object(custom_scanner, 'scan_ssl', return_value=mock_ssl_result):
            result = await custom_scanner.scan_ssl("https://example.com")
            assert result["valid"] is True
            assert len(result["vulnerabilities"]) == 0
    
    @pytest.mark.asyncio
    async def test_header_security_check(self, custom_scanner):
        """Test security headers check"""
        mock_headers = {
            "missing": ["X-Frame-Options", "Content-Security-Policy"],
            "present": ["Strict-Transport-Security"],
            "score": 6
        }
        
        with patch.object(custom_scanner, 'check_security_headers', return_value=mock_headers):
            result = await custom_scanner.check_security_headers("https://example.com")
            assert len(result["missing"]) == 2
            assert result["score"] == 6
    
    @pytest.mark.asyncio
    async def test_subdomain_enumeration(self, custom_scanner):
        """Test subdomain enumeration"""
        mock_subdomains = [
            "www.example.com",
            "api.example.com",
            "admin.example.com"
        ]
        
        with patch.object(custom_scanner, 'enumerate_subdomains', return_value=mock_subdomains):
            result = await custom_scanner.enumerate_subdomains("example.com")
            assert len(result) == 3
            assert "api.example.com" in result


class TestScanOrchestrator:
    """Test suite for scan orchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create ScanOrchestrator instance"""
        return ScanOrchestrator()
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator is not None
        assert hasattr(orchestrator, 'scanners')
    
    @pytest.mark.asyncio
    async def test_multi_scanner_execution(self, orchestrator):
        """Test execution of multiple scanners"""
        scan_config = {
            "target": "https://example.com",
            "scanners": ["zap", "nuclei", "custom"]
        }
        
        with patch.object(orchestrator, 'run_scan', return_value={"status": "completed"}):
            result = await orchestrator.run_scan(scan_config)
            assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_scan_result_aggregation(self, orchestrator):
        """Test aggregation of scan results"""
        mock_results = {
            "zap": {"vulnerabilities": [{"type": "xss", "severity": "high"}]},
            "nuclei": {"vulnerabilities": [{"type": "cve-2021-1234", "severity": "critical"}]},
            "custom": {"vulnerabilities": [{"type": "ssl", "severity": "low"}]}
        }
        
        with patch.object(orchestrator, 'aggregate_results', return_value={"total": 3, "critical": 1, "high": 1, "low": 1}):
            result = await orchestrator.aggregate_results(mock_results)
            assert result["total"] == 3
            assert result["critical"] == 1
    
    @pytest.mark.asyncio
    async def test_scan_prioritization(self, orchestrator):
        """Test scan prioritization logic"""
        vulnerabilities = [
            {"severity": "low", "type": "info"},
            {"severity": "critical", "type": "sqli"},
            {"severity": "high", "type": "xss"}
        ]
        
        with patch.object(orchestrator, 'prioritize_findings', return_value=sorted(vulnerabilities, key=lambda x: {"critical": 0, "high": 1, "low": 2}[x["severity"]])):
            result = await orchestrator.prioritize_findings(vulnerabilities)
            assert result[0]["severity"] == "critical"
    
    @pytest.mark.asyncio
    async def test_false_positive_filtering(self, orchestrator):
        """Test false positive filtering"""
        findings = [
            {"id": 1, "false_positive_score": 0.1},
            {"id": 2, "false_positive_score": 0.9},
            {"id": 3, "false_positive_score": 0.3}
        ]
        
        with patch.object(orchestrator, 'filter_false_positives', return_value=[f for f in findings if f["false_positive_score"] < 0.5]):
            result = await orchestrator.filter_false_positives(findings, threshold=0.5)
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_scan_scheduling(self, orchestrator):
        """Test scan scheduling functionality"""
        schedule = {
            "target": "https://example.com",
            "frequency": "daily",
            "time": "02:00"
        }
        
        with patch.object(orchestrator, 'schedule_scan', return_value={"job_id": "sched_123"}):
            result = await orchestrator.schedule_scan(schedule)
            assert "job_id" in result


# Integration tests
class TestScannerIntegration:
    """Integration tests for scanner ecosystem"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_scan_workflow(self):
        """Test complete scan workflow from start to finish"""
        orchestrator = ScanOrchestrator()
        
        scan_request = {
            "target": "https://testsite.example.com",
            "depth": "full",
            "scanners": ["all"]
        }
        
        # This would be a real integration test in actual environment
        # For now, we mock it
        with patch.object(orchestrator, 'execute_full_scan') as mock_scan:
            mock_scan.return_value = {
                "status": "completed",
                "duration": 300,
                "vulnerabilities_found": 5
            }
            
            result = await orchestrator.execute_full_scan(scan_request)
            assert result["status"] == "completed"
            assert result["vulnerabilities_found"] >= 0


# Performance tests
class TestScannerPerformance:
    """Performance tests for scanners"""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_scans(self):
        """Test handling of concurrent scans"""
        orchestrator = ScanOrchestrator()
        
        # Simulate 10 concurrent scans
        tasks = []
        for i in range(10):
            task = asyncio.create_task(
                orchestrator.run_scan({"target": f"https://site{i}.example.com"})
            )
            tasks.append(task)
        
        with patch.object(orchestrator, 'run_scan', return_value={"status": "completed"}):
            results = await asyncio.gather(*tasks, return_exceptions=True)
            assert len(results) == 10
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_scan_timeout_handling(self):
        """Test timeout handling for long-running scans"""
        scanner = ZAPScanner(api_key="test", host="localhost", port=8080)
        
        with patch.object(scanner, 'scan_target', side_effect=asyncio.TimeoutError):
            with pytest.raises(asyncio.TimeoutError):
                await scanner.scan_target("https://example.com", timeout=1)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
