"""
Analyzer Agent - AI-powered vulnerability analysis
"""

from typing import Dict, Any, List
import openai
from core.config import settings


class AnalyzerAgent:
    """AI agent for analyzing scan findings"""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
    
    async def analyze_findings(
        self,
        findings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze scan findings and classify vulnerabilities"""
        
        vulnerabilities = []
        
        for finding in findings:
            vulnerability = await self._classify_vulnerability(finding)
            vulnerabilities.append(vulnerability)
        
        analysis = {
            "vulnerabilities": vulnerabilities,
            "summary": {
                "total": len(vulnerabilities),
                "critical": sum(1 for v in vulnerabilities if v["severity"] == "critical"),
                "high": sum(1 for v in vulnerabilities if v["severity"] == "high"),
                "medium": sum(1 for v in vulnerabilities if v["severity"] == "medium"),
                "low": sum(1 for v in vulnerabilities if v["severity"] == "low")
            }
        }
        
        if settings.OPENAI_API_KEY and vulnerabilities:
            analysis["ai_insights"] = await self._generate_insights(vulnerabilities)
        
        return analysis
    
    async def _classify_vulnerability(
        self,
        finding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classify and enrich vulnerability data"""
        
        vuln_type = finding.get("type", "unknown")
        severity = finding.get("severity", "medium")
        
        vulnerability = {
            "type": vuln_type,
            "severity": severity,
            "title": self._generate_title(vuln_type),
            "description": self._generate_description(finding),
            "proof_of_concept": finding.get("payload", ""),
            "evidence": finding.get("evidence", ""),
            "confidence": finding.get("confidence", 0.5),
            "cvss_score": self._calculate_cvss(severity),
            "remediation": self._get_remediation(vuln_type)
        }
        
        return vulnerability
    
    def _generate_title(self, vuln_type: str) -> str:
        """Generate vulnerability title"""
        titles = {
            "xss": "Cross-Site Scripting (XSS) Vulnerability",
            "sqli": "SQL Injection Vulnerability",
            "rce": "Remote Code Execution Vulnerability",
            "csrf": "Cross-Site Request Forgery",
            "ssrf": "Server-Side Request Forgery",
            "lfi": "Local File Inclusion",
            "rfi": "Remote File Inclusion"
        }
        return titles.get(vuln_type, f"Security Vulnerability: {vuln_type.upper()}")
    
    def _generate_description(self, finding: Dict[str, Any]) -> str:
        """Generate detailed description"""
        vuln_type = finding.get("type", "unknown")
        
        descriptions = {
            "xss": "A Cross-Site Scripting vulnerability was discovered that allows injection of malicious scripts into web pages viewed by other users.",
            "sqli": "A SQL Injection vulnerability was identified that could allow attackers to manipulate database queries and access sensitive data.",
            "rce": "A Remote Code Execution vulnerability was found that could allow attackers to execute arbitrary commands on the server.",
            "csrf": "A Cross-Site Request Forgery vulnerability exists that could allow attackers to perform unauthorized actions.",
            "ssrf": "A Server-Side Request Forgery vulnerability was discovered that could allow internal network access."
        }
        
        return descriptions.get(vuln_type, f"A {vuln_type} vulnerability was discovered.")
    
    def _calculate_cvss(self, severity: str) -> float:
        """Calculate CVSS score based on severity"""
        scores = {
            "critical": 9.5,
            "high": 7.5,
            "medium": 5.5,
            "low": 3.0
        }
        return scores.get(severity, 5.0)
    
    def _get_remediation(self, vuln_type: str) -> str:
        """Get remediation advice"""
        remediations = {
            "xss": "Implement proper input validation and output encoding. Use Content Security Policy headers.",
            "sqli": "Use parameterized queries and prepared statements. Implement input validation.",
            "rce": "Sanitize all user inputs. Avoid using eval() or system() with user-supplied data.",
            "csrf": "Implement CSRF tokens. Use SameSite cookie attribute.",
            "ssrf": "Validate and sanitize all URLs. Implement allowlist of permitted domains."
        }
        return remediations.get(vuln_type, "Consult security best practices for remediation.")
    
    async def _generate_insights(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> str:
        """Generate AI insights using OpenAI"""
        
        try:
            vuln_summary = "\n".join([
                f"- {v['title']} (Severity: {v['severity']})"
                for v in vulnerabilities[:5]
            ])
            
            prompt = f"""
Analyze these security vulnerabilities and provide insights:

{vuln_summary}

Provide:
1. Overall risk assessment
2. Potential exploit chains
3. Priority recommendations
"""
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a security analyst expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"AI insights generation failed: {str(e)}"
