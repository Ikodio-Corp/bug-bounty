"""
Integration service for external platforms
"""

from typing import Dict, Optional, List
import httpx
from datetime import datetime

from core.config import settings


class IntegrationService:
    """Service for integrating with external platforms"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def sync_to_jira(
        self,
        bug_data: Dict,
        project_key: str,
        issue_type: str = "Bug"
    ) -> Dict:
        """Sync bug to Jira"""
        if not settings.JIRA_API_URL or not settings.JIRA_API_TOKEN:
            return {"success": False, "message": "Jira not configured"}
        
        headers = {
            "Authorization": f"Bearer {settings.JIRA_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": bug_data["title"],
                "description": bug_data["description"],
                "issuetype": {"name": issue_type},
                "priority": {
                    "name": self._map_severity_to_jira_priority(bug_data["severity"])
                },
                "labels": [bug_data["vulnerability_type"], "ikodio-bugbounty"]
            }
        }
        
        try:
            response = await self.http_client.post(
                f"{settings.JIRA_API_URL}/rest/api/3/issue",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "jira_issue_key": result["key"],
                "jira_issue_id": result["id"]
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def sync_to_linear(
        self,
        bug_data: Dict,
        team_id: str
    ) -> Dict:
        """Sync bug to Linear"""
        if not settings.LINEAR_API_TOKEN:
            return {"success": False, "message": "Linear not configured"}
        
        headers = {
            "Authorization": settings.LINEAR_API_TOKEN,
            "Content-Type": "application/json"
        }
        
        query = """
        mutation IssueCreate($title: String!, $description: String!, $teamId: String!, $priority: Int!) {
          issueCreate(input: {
            title: $title
            description: $description
            teamId: $teamId
            priority: $priority
          }) {
            success
            issue {
              id
              identifier
            }
          }
        }
        """
        
        variables = {
            "title": bug_data["title"],
            "description": bug_data["description"],
            "teamId": team_id,
            "priority": self._map_severity_to_linear_priority(bug_data["severity"])
        }
        
        try:
            response = await self.http_client.post(
                "https://api.linear.app/graphql",
                headers=headers,
                json={"query": query, "variables": variables}
            )
            response.raise_for_status()
            result = response.json()
            
            if result["data"]["issueCreate"]["success"]:
                issue = result["data"]["issueCreate"]["issue"]
                return {
                    "success": True,
                    "linear_issue_id": issue["id"],
                    "linear_issue_identifier": issue["identifier"]
                }
            
            return {"success": False, "message": "Failed to create Linear issue"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def sync_to_hackerone(
        self,
        bug_data: Dict,
        program_handle: str
    ) -> Dict:
        """Sync bug to HackerOne"""
        if not settings.HACKERONE_API_TOKEN:
            return {"success": False, "message": "HackerOne not configured"}
        
        headers = {
            "Authorization": f"token {settings.HACKERONE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "data": {
                "type": "report",
                "attributes": {
                    "title": bug_data["title"],
                    "vulnerability_information": bug_data["description"],
                    "severity_rating": bug_data["severity"],
                    "weakness_id": self._map_type_to_weakness(bug_data["vulnerability_type"])
                }
            }
        }
        
        try:
            response = await self.http_client.post(
                f"https://api.hackerone.com/v1/hackers/programs/{program_handle}/reports",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "hackerone_report_id": result["data"]["id"]
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def sync_to_bugcrowd(
        self,
        bug_data: Dict,
        program_code: str
    ) -> Dict:
        """Sync bug to Bugcrowd"""
        if not settings.BUGCROWD_API_TOKEN:
            return {"success": False, "message": "Bugcrowd not configured"}
        
        headers = {
            "Authorization": f"Token {settings.BUGCROWD_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "title": bug_data["title"],
            "description": bug_data["description"],
            "target": bug_data["target_url"],
            "severity": self._map_severity_to_bugcrowd(bug_data["severity"]),
            "vulnerability_type": bug_data["vulnerability_type"]
        }
        
        try:
            response = await self.http_client.post(
                f"https://api.bugcrowd.com/submissions?program_code={program_code}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "bugcrowd_submission_id": result["id"]
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def sync_to_aws_security_hub(
        self,
        bug_data: Dict,
        region: str = "us-east-1"
    ) -> Dict:
        """Sync bug to AWS Security Hub"""
        # Implementation would use boto3 to send findings
        # Placeholder for AWS integration
        return {"success": False, "message": "AWS Security Hub integration pending"}
    
    async def sync_to_azure_sentinel(
        self,
        bug_data: Dict
    ) -> Dict:
        """Sync bug to Azure Sentinel"""
        # Implementation would use Azure SDK
        # Placeholder for Azure integration
        return {"success": False, "message": "Azure Sentinel integration pending"}
    
    async def sync_to_gcp_scc(
        self,
        bug_data: Dict
    ) -> Dict:
        """Sync bug to Google Cloud Security Command Center"""
        # Implementation would use Google Cloud SDK
        # Placeholder for GCP integration
        return {"success": False, "message": "GCP SCC integration pending"}
    
    def _map_severity_to_jira_priority(self, severity: str) -> str:
        """Map severity to Jira priority"""
        mapping = {
            "critical": "Highest",
            "high": "High",
            "medium": "Medium",
            "low": "Low",
            "info": "Lowest"
        }
        return mapping.get(severity, "Medium")
    
    def _map_severity_to_linear_priority(self, severity: str) -> int:
        """Map severity to Linear priority (1=Urgent, 4=No priority)"""
        mapping = {
            "critical": 1,
            "high": 1,
            "medium": 2,
            "low": 3,
            "info": 4
        }
        return mapping.get(severity, 2)
    
    def _map_severity_to_bugcrowd(self, severity: str) -> int:
        """Map severity to Bugcrowd severity (1-5)"""
        mapping = {
            "critical": 5,
            "high": 4,
            "medium": 3,
            "low": 2,
            "info": 1
        }
        return mapping.get(severity, 3)
    
    def _map_type_to_weakness(self, vuln_type: str) -> int:
        """Map vulnerability type to CWE weakness ID"""
        mapping = {
            "sql_injection": 89,
            "xss": 79,
            "csrf": 352,
            "ssrf": 918,
            "xxe": 611,
            "idor": 639,
            "auth_bypass": 287,
            "rce": 94,
            "lfi": 98,
            "deserialization": 502
        }
        return mapping.get(vuln_type, 1000)
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
