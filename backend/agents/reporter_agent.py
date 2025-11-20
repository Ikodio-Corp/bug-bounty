"""
Reporter Agent - AI-powered report generation
"""

from typing import Dict, Any, List
import openai
from datetime import datetime

from core.config import settings


class ReporterAgent:
    """AI agent for generating vulnerability reports"""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
    
    async def generate_summary(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate executive summary of vulnerabilities"""
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_vulnerabilities": len(vulnerabilities),
            "severity_breakdown": self._get_severity_breakdown(vulnerabilities),
            "executive_summary": self._generate_executive_summary(vulnerabilities),
            "top_vulnerabilities": vulnerabilities[:5],
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
        
        if settings.OPENAI_API_KEY and vulnerabilities:
            report["ai_summary"] = await self._generate_ai_summary(vulnerabilities)
        
        return report
    
    def _get_severity_breakdown(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Get breakdown by severity"""
        return {
            "critical": sum(1 for v in vulnerabilities if v.get("severity") == "critical"),
            "high": sum(1 for v in vulnerabilities if v.get("severity") == "high"),
            "medium": sum(1 for v in vulnerabilities if v.get("severity") == "medium"),
            "low": sum(1 for v in vulnerabilities if v.get("severity") == "low")
        }
    
    def _generate_executive_summary(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> str:
        """Generate executive summary"""
        total = len(vulnerabilities)
        critical = sum(1 for v in vulnerabilities if v.get("severity") == "critical")
        high = sum(1 for v in vulnerabilities if v.get("severity") == "high")
        
        if critical > 0:
            risk_level = "CRITICAL"
        elif high > 0:
            risk_level = "HIGH"
        elif total > 5:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        summary = f"""
Security Assessment Summary

Total Vulnerabilities Found: {total}
Risk Level: {risk_level}

The security assessment identified {critical} critical and {high} high severity vulnerabilities that require immediate attention. These vulnerabilities could potentially lead to system compromise, data breaches, or service disruption.

Immediate action is required to address critical and high severity findings to reduce the attack surface and protect sensitive assets.
        """
        
        return summary.strip()
    
    def _generate_recommendations(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
        high_vulns = [v for v in vulnerabilities if v.get("severity") == "high"]
        
        if critical_vulns:
            recommendations.append(
                f"URGENT: Address {len(critical_vulns)} critical vulnerabilities immediately"
            )
        
        if high_vulns:
            recommendations.append(
                f"HIGH PRIORITY: Remediate {len(high_vulns)} high severity issues within 7 days"
            )
        
        vuln_types = set(v.get("type") for v in vulnerabilities)
        
        if "sqli" in vuln_types:
            recommendations.append("Implement prepared statements and parameterized queries")
        
        if "xss" in vuln_types:
            recommendations.append("Deploy Content Security Policy and input validation")
        
        if "rce" in vuln_types:
            recommendations.append("Review and sanitize all command execution points")
        
        recommendations.append("Conduct regular security assessments")
        recommendations.append("Implement security awareness training for developers")
        
        return recommendations
    
    async def _generate_ai_summary(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> str:
        """Generate AI-powered detailed summary"""
        
        try:
            vuln_details = "\n".join([
                f"- {v['title']}: {v['description'][:100]}... (Severity: {v['severity']})"
                for v in vulnerabilities[:10]
            ])
            
            prompt = f"""
Generate a comprehensive security assessment report summary based on these vulnerabilities:

{vuln_details}

Include:
1. Executive summary
2. Key findings
3. Business impact
4. Prioritized remediation roadmap
5. Long-term security recommendations

Keep it professional and actionable.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior security consultant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"AI summary generation failed: {str(e)}"
    
    async def generate_report(
        self,
        title: str,
        description: str,
        severity: str,
        proof_of_concept: str,
        target_url: str
    ) -> Dict[str, Any]:
        """Generate detailed vulnerability report"""
        
        report = {
            "title": title,
            "description": description,
            "severity": severity,
            "target_url": target_url,
            "proof_of_concept": proof_of_concept,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        if settings.OPENAI_API_KEY:
            try:
                prompt = f"""
Generate a detailed security vulnerability report:

Title: {title}
Severity: {severity}
Target: {target_url}
Description: {description}

Include:
1. Technical analysis
2. Proof of concept explanation
3. Impact assessment
4. Step-by-step reproduction
5. Remediation steps
                """
                
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a security researcher."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.7
                )
                
                report["detailed_report"] = response.choices[0].message.content
            
            except Exception as e:
                report["detailed_report"] = f"Detailed report generation failed: {str(e)}"
        
        return report
