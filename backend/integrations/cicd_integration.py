"""
CI/CD Integration Service
Supports Jenkins, GitHub Actions, GitLab CI, CircleCI, Travis CI
"""

import asyncio
import aiohttp
import base64
from typing import Dict, List, Any, Optional


class JenkinsIntegration:
    """Jenkins CI/CD integration"""
    
    def __init__(self, jenkins_url: str, username: str, api_token: str):
        self.jenkins_url = jenkins_url.rstrip("/")
        self.username = username
        self.api_token = api_token
        self.auth = base64.b64encode(
            f"{username}:{api_token}".encode()
        ).decode()
    
    async def trigger_job(
        self,
        job_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Trigger Jenkins job"""
        if parameters:
            url = f"{self.jenkins_url}/job/{job_name}/buildWithParameters"
        else:
            url = f"{self.jenkins_url}/job/{job_name}/build"
        
        headers = {
            "Authorization": f"Basic {self.auth}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=parameters or {}
            ) as response:
                return {
                    "status": response.status,
                    "triggered": response.status in [200, 201]
                }
    
    async def get_build_status(
        self,
        job_name: str,
        build_number: int
    ) -> Dict[str, Any]:
        """Get build status"""
        url = f"{self.jenkins_url}/job/{job_name}/{build_number}/api/json"
        headers = {"Authorization": f"Basic {self.auth}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}
    
    async def get_build_console_output(
        self,
        job_name: str,
        build_number: int
    ) -> str:
        """Get build console output"""
        url = f"{self.jenkins_url}/job/{job_name}/{build_number}/consoleText"
        headers = {"Authorization": f"Basic {self.auth}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    return ""


class GitHubActionsIntegration:
    """GitHub Actions integration"""
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.api_url = "https://api.github.com"
    
    async def trigger_workflow(
        self,
        owner: str,
        repo: str,
        workflow_id: str,
        ref: str = "main",
        inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Trigger GitHub Actions workflow"""
        url = f"{self.api_url}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }
        
        data = {"ref": ref}
        if inputs:
            data["inputs"] = inputs
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                return {
                    "status": response.status,
                    "triggered": response.status == 204
                }
    
    async def get_workflow_runs(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get workflow runs"""
        if workflow_id:
            url = f"{self.api_url}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            url = f"{self.api_url}/repos/{owner}/{repo}/actions/runs"
        
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("workflow_runs", [])
                else:
                    return []
    
    async def get_workflow_run_logs(
        self,
        owner: str,
        repo: str,
        run_id: int
    ) -> bytes:
        """Get workflow run logs"""
        url = f"{self.api_url}/repos/{owner}/{repo}/actions/runs/{run_id}/logs"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    return b""


class GitLabCIIntegration:
    """GitLab CI/CD integration"""
    
    def __init__(self, private_token: str, gitlab_url: str = "https://gitlab.com"):
        self.private_token = private_token
        self.api_url = f"{gitlab_url}/api/v4"
    
    async def trigger_pipeline(
        self,
        project_id: str,
        ref: str = "main",
        variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Trigger GitLab pipeline"""
        url = f"{self.api_url}/projects/{project_id}/pipeline"
        headers = {"PRIVATE-TOKEN": self.private_token}
        
        data = {"ref": ref}
        if variables:
            data["variables"] = [
                {"key": k, "value": v} for k, v in variables.items()
            ]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    return {"error": f"Failed to trigger pipeline: {response.status}"}
    
    async def get_pipeline_status(
        self,
        project_id: str,
        pipeline_id: int
    ) -> Dict[str, Any]:
        """Get pipeline status"""
        url = f"{self.api_url}/projects/{project_id}/pipelines/{pipeline_id}"
        headers = {"PRIVATE-TOKEN": self.private_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}
    
    async def get_pipeline_jobs(
        self,
        project_id: str,
        pipeline_id: int
    ) -> List[Dict[str, Any]]:
        """Get pipeline jobs"""
        url = f"{self.api_url}/projects/{project_id}/pipelines/{pipeline_id}/jobs"
        headers = {"PRIVATE-TOKEN": self.private_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
    
    async def get_job_trace(
        self,
        project_id: str,
        job_id: int
    ) -> str:
        """Get job trace/logs"""
        url = f"{self.api_url}/projects/{project_id}/jobs/{job_id}/trace"
        headers = {"PRIVATE-TOKEN": self.private_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    return ""


class CircleCIIntegration:
    """CircleCI integration"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.api_url = "https://circleci.com/api/v2"
    
    async def trigger_pipeline(
        self,
        project_slug: str,
        branch: str = "main",
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Trigger CircleCI pipeline"""
        url = f"{self.api_url}/project/{project_slug}/pipeline"
        headers = {
            "Circle-Token": self.api_token,
            "Content-Type": "application/json"
        }
        
        data = {"branch": branch}
        if parameters:
            data["parameters"] = parameters
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    return {"error": f"Failed to trigger pipeline: {response.status}"}
    
    async def get_pipeline_workflows(
        self,
        pipeline_id: str
    ) -> List[Dict[str, Any]]:
        """Get pipeline workflows"""
        url = f"{self.api_url}/pipeline/{pipeline_id}/workflow"
        headers = {"Circle-Token": self.api_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("items", [])
                else:
                    return []
    
    async def get_workflow_jobs(
        self,
        workflow_id: str
    ) -> List[Dict[str, Any]]:
        """Get workflow jobs"""
        url = f"{self.api_url}/workflow/{workflow_id}/job"
        headers = {"Circle-Token": self.api_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("items", [])
                else:
                    return []


class CICDOrchestrator:
    """Orchestrator for all CI/CD integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.integrations = {}
        
        if "jenkins" in config:
            self.integrations["jenkins"] = JenkinsIntegration(**config["jenkins"])
        
        if "github_actions" in config:
            self.integrations["github_actions"] = GitHubActionsIntegration(
                **config["github_actions"]
            )
        
        if "gitlab_ci" in config:
            self.integrations["gitlab_ci"] = GitLabCIIntegration(**config["gitlab_ci"])
        
        if "circleci" in config:
            self.integrations["circleci"] = CircleCIIntegration(**config["circleci"])
    
    async def trigger_scan_pipeline(
        self,
        platform: str,
        repository: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Trigger security scan in CI/CD pipeline"""
        
        if platform not in self.integrations:
            return {"error": f"Platform {platform} not configured"}
        
        integration = self.integrations[platform]
        
        if platform == "jenkins":
            return await integration.trigger_job(repository, kwargs.get("parameters"))
        
        elif platform == "github_actions":
            return await integration.trigger_workflow(
                kwargs.get("owner"),
                kwargs.get("repo"),
                kwargs.get("workflow_id"),
                kwargs.get("ref", "main"),
                kwargs.get("inputs")
            )
        
        elif platform == "gitlab_ci":
            return await integration.trigger_pipeline(
                kwargs.get("project_id"),
                kwargs.get("ref", "main"),
                kwargs.get("variables")
            )
        
        elif platform == "circleci":
            return await integration.trigger_pipeline(
                kwargs.get("project_slug"),
                kwargs.get("branch", "main"),
                kwargs.get("parameters")
            )
        
        return {"error": "Unknown platform"}
    
    async def get_pipeline_status(
        self,
        platform: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get pipeline status from any platform"""
        
        if platform not in self.integrations:
            return {"error": f"Platform {platform} not configured"}
        
        integration = self.integrations[platform]
        
        if platform == "jenkins":
            return await integration.get_build_status(
                kwargs.get("job_name"),
                kwargs.get("build_number")
            )
        
        elif platform == "github_actions":
            runs = await integration.get_workflow_runs(
                kwargs.get("owner"),
                kwargs.get("repo"),
                kwargs.get("workflow_id")
            )
            return runs[0] if runs else {}
        
        elif platform == "gitlab_ci":
            return await integration.get_pipeline_status(
                kwargs.get("project_id"),
                kwargs.get("pipeline_id")
            )
        
        return {"error": "Unknown platform"}
