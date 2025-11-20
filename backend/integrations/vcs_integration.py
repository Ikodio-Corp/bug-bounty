"""
GitHub Integration Service
Handles GitHub Apps, webhooks, and repository scanning
"""

import hmac
import hashlib
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import jwt


class GitHubIntegration:
    """GitHub Apps and API integration"""
    
    def __init__(
        self,
        app_id: str,
        private_key: str,
        webhook_secret: str,
        installation_id: Optional[str] = None
    ):
        self.app_id = app_id
        self.private_key = private_key
        self.webhook_secret = webhook_secret
        self.installation_id = installation_id
        self.api_url = "https://api.github.com"
        
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature"""
        if not signature:
            return False
        
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        signature_parts = signature.split("=")
        if len(signature_parts) != 2:
            return False
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    def generate_jwt(self) -> str:
        """Generate JWT for GitHub App authentication"""
        now = int(datetime.utcnow().timestamp())
        
        payload = {
            "iat": now,
            "exp": now + (10 * 60),
            "iss": self.app_id
        }
        
        token = jwt.encode(payload, self.private_key, algorithm="RS256")
        return token
    
    async def get_installation_token(self, installation_id: str = None) -> str:
        """Get installation access token"""
        inst_id = installation_id or self.installation_id
        
        jwt_token = self.generate_jwt()
        
        url = f"{self.api_url}/app/installations/{inst_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                if response.status == 201:
                    data = await response.json()
                    return data.get("token")
                else:
                    raise Exception(f"Failed to get installation token: {response.status}")
    
    async def get_repository_contents(
        self,
        owner: str,
        repo: str,
        path: str = "",
        ref: str = "main"
    ) -> List[Dict[str, Any]]:
        """Get repository contents"""
        token = await self.get_installation_token()
        
        url = f"{self.api_url}/repos/{owner}/{repo}/contents/{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        params = {"ref": ref}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
    
    async def create_check_run(
        self,
        owner: str,
        repo: str,
        name: str,
        head_sha: str,
        status: str = "in_progress",
        conclusion: Optional[str] = None,
        output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a check run for a commit"""
        token = await self.get_installation_token()
        
        url = f"{self.api_url}/repos/{owner}/{repo}/check-runs"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        
        data = {
            "name": name,
            "head_sha": head_sha,
            "status": status
        }
        
        if conclusion:
            data["conclusion"] = conclusion
        
        if output:
            data["output"] = output
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    raise Exception(f"Failed to create check run: {response.status}")
    
    async def update_check_run(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
        status: str = "completed",
        conclusion: str = "success",
        output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update a check run"""
        token = await self.get_installation_token()
        
        url = f"{self.api_url}/repos/{owner}/{repo}/check-runs/{check_run_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        
        data = {
            "status": status,
            "conclusion": conclusion
        }
        
        if output:
            data["output"] = output
        
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to update check run: {response.status}")
    
    async def create_issue_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str
    ) -> Dict[str, Any]:
        """Create a comment on an issue or PR"""
        token = await self.get_installation_token()
        
        url = f"{self.api_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        
        data = {"body": body}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    raise Exception(f"Failed to create comment: {response.status}")
    
    async def create_pull_request_review(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        event: str = "COMMENT",
        body: Optional[str] = None,
        comments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create a pull request review"""
        token = await self.get_installation_token()
        
        url = f"{self.api_url}/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        
        data = {"event": event}
        if body:
            data["body"] = body
        if comments:
            data["comments"] = comments
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to create review: {response.status}")
    
    async def get_pull_request_files(
        self,
        owner: str,
        repo: str,
        pull_number: int
    ) -> List[Dict[str, Any]]:
        """Get files changed in a pull request"""
        token = await self.get_installation_token()
        
        url = f"{self.api_url}/repos/{owner}/{repo}/pulls/{pull_number}/files"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
    
    async def create_commit_status(
        self,
        owner: str,
        repo: str,
        sha: str,
        state: str,
        context: str,
        description: Optional[str] = None,
        target_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a commit status"""
        token = await self.get_installation_token()
        
        url = f"{self.api_url}/repos/{owner}/{repo}/statuses/{sha}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        
        data = {
            "state": state,
            "context": context
        }
        
        if description:
            data["description"] = description
        if target_url:
            data["target_url"] = target_url
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    raise Exception(f"Failed to create status: {response.status}")


class GitLabIntegration:
    """GitLab API integration"""
    
    def __init__(self, private_token: str, gitlab_url: str = "https://gitlab.com"):
        self.private_token = private_token
        self.gitlab_url = gitlab_url
        self.api_url = f"{gitlab_url}/api/v4"
    
    def verify_webhook_signature(self, payload: str, token: str) -> bool:
        """Verify GitLab webhook token"""
        return token == self.private_token
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details"""
        url = f"{self.api_url}/projects/{project_id}"
        headers = {"PRIVATE-TOKEN": self.private_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}
    
    async def get_repository_files(
        self,
        project_id: str,
        path: str = "",
        ref: str = "main"
    ) -> List[Dict[str, Any]]:
        """Get repository files"""
        url = f"{self.api_url}/projects/{project_id}/repository/tree"
        headers = {"PRIVATE-TOKEN": self.private_token}
        params = {"path": path, "ref": ref}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
    
    async def create_commit_status(
        self,
        project_id: str,
        sha: str,
        state: str,
        name: str,
        description: Optional[str] = None,
        target_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create commit status"""
        url = f"{self.api_url}/projects/{project_id}/statuses/{sha}"
        headers = {"PRIVATE-TOKEN": self.private_token}
        
        data = {
            "state": state,
            "name": name
        }
        
        if description:
            data["description"] = description
        if target_url:
            data["target_url"] = target_url
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    raise Exception(f"Failed to create status: {response.status}")
    
    async def create_merge_request_note(
        self,
        project_id: str,
        merge_request_iid: int,
        body: str
    ) -> Dict[str, Any]:
        """Create note on merge request"""
        url = f"{self.api_url}/projects/{project_id}/merge_requests/{merge_request_iid}/notes"
        headers = {"PRIVATE-TOKEN": self.private_token}
        data = {"body": body}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    raise Exception(f"Failed to create note: {response.status}")
    
    async def get_merge_request_changes(
        self,
        project_id: str,
        merge_request_iid: int
    ) -> Dict[str, Any]:
        """Get merge request changes"""
        url = f"{self.api_url}/projects/{project_id}/merge_requests/{merge_request_iid}/changes"
        headers = {"PRIVATE-TOKEN": self.private_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}
