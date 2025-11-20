"""
GitHub App Integration

Implements GitHub App functionality for:
- Webhook event handling (push, PR, release)
- Auto-scanning on PR
- Status checks
- Inline PR comments for vulnerabilities
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

import aiohttp
import jwt
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WebhookEvent(str, Enum):
    """GitHub webhook events."""
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_REVIEW = "pull_request_review"
    RELEASE = "release"
    INSTALLATION = "installation"
    CHECK_RUN = "check_run"
    CHECK_SUITE = "check_suite"


class CheckStatus(str, Enum):
    """Check run status."""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class CheckConclusion(str, Enum):
    """Check run conclusion."""
    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    ACTION_REQUIRED = "action_required"


class GitHubAppConfig(BaseModel):
    """GitHub App configuration."""
    app_id: str
    private_key: str
    webhook_secret: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None


class InstallationInfo(BaseModel):
    """GitHub App installation info."""
    installation_id: int
    account_login: str
    account_type: str
    repository_selection: str
    access_tokens_url: str
    repositories_url: str


class PullRequestInfo(BaseModel):
    """Pull request information."""
    number: int
    title: str
    state: str
    head_sha: str
    base_sha: str
    head_ref: str
    base_ref: str
    repository: str
    author: str


class GitHubApp:
    """
    GitHub App Integration.

    Features:
    - JWT authentication
    - Webhook handling
    - Check runs API
    - PR comments
    - Status updates
    """

    def __init__(self, config: GitHubAppConfig):
        """Initialize GitHub App."""
        self.config = config
        self._installation_tokens: Dict[int, Dict[str, Any]] = {}
        self._api_base = "https://api.github.com"

        logger.info(f"GitHubApp initialized with app_id: {config.app_id}")

    def _generate_jwt(self) -> str:
        """Generate JWT for GitHub App authentication."""
        now = int(time.time())

        payload = {
            "iat": now - 60,  # Issued at time (60 seconds in the past)
            "exp": now + 600,  # Expiration time (10 minutes)
            "iss": self.config.app_id  # GitHub App ID
        }

        return jwt.encode(payload, self.config.private_key, algorithm="RS256")

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify GitHub webhook signature.

        Args:
            payload: Request body bytes
            signature: X-Hub-Signature-256 header value

        Returns:
            True if signature is valid
        """
        if not signature:
            return False

        expected = hmac.new(
            self.config.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(f"sha256={expected}", signature)

    async def get_installation_token(self, installation_id: int) -> str:
        """
        Get installation access token.

        Args:
            installation_id: GitHub App installation ID

        Returns:
            Access token
        """
        # Check cache
        if installation_id in self._installation_tokens:
            cached = self._installation_tokens[installation_id]
            if cached["expires_at"] > datetime.utcnow().isoformat():
                return cached["token"]

        # Get new token
        jwt_token = self._generate_jwt()

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._api_base}/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    self._installation_tokens[installation_id] = {
                        "token": data["token"],
                        "expires_at": data["expires_at"]
                    }
                    return data["token"]
                else:
                    error = await response.text()
                    raise Exception(f"Failed to get installation token: {error}")

    async def handle_webhook(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle incoming webhook event.

        Args:
            event_type: X-GitHub-Event header value
            payload: Webhook payload

        Returns:
            Processing result
        """
        logger.info(f"Handling webhook event: {event_type}")

        handlers = {
            "push": self._handle_push,
            "pull_request": self._handle_pull_request,
            "pull_request_review": self._handle_pr_review,
            "installation": self._handle_installation,
            "check_suite": self._handle_check_suite,
        }

        handler = handlers.get(event_type)
        if handler:
            return await handler(payload)
        else:
            return {"status": "ignored", "event": event_type}

    async def _handle_push(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle push event."""
        repository = payload.get("repository", {}).get("full_name")
        ref = payload.get("ref")
        commits = payload.get("commits", [])
        installation_id = payload.get("installation", {}).get("id")

        logger.info(f"Push to {repository} ({ref}): {len(commits)} commits")

        # Trigger scan for the push
        return {
            "status": "processed",
            "event": "push",
            "repository": repository,
            "ref": ref,
            "commits": len(commits),
            "action": "scan_triggered"
        }

    async def _handle_pull_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pull request event."""
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        repository = payload.get("repository", {}).get("full_name")
        installation_id = payload.get("installation", {}).get("id")

        pr_info = PullRequestInfo(
            number=pr.get("number"),
            title=pr.get("title"),
            state=pr.get("state"),
            head_sha=pr.get("head", {}).get("sha"),
            base_sha=pr.get("base", {}).get("sha"),
            head_ref=pr.get("head", {}).get("ref"),
            base_ref=pr.get("base", {}).get("ref"),
            repository=repository,
            author=pr.get("user", {}).get("login")
        )

        logger.info(f"PR #{pr_info.number} {action} in {repository}")

        # Handle different PR actions
        if action in ["opened", "synchronize", "reopened"]:
            # Create check run and trigger scan
            if installation_id:
                token = await self.get_installation_token(installation_id)
                check_run = await self.create_check_run(
                    token,
                    repository,
                    pr_info.head_sha,
                    "IKODIO Security Scan"
                )

                return {
                    "status": "processed",
                    "event": "pull_request",
                    "action": action,
                    "pr_number": pr_info.number,
                    "repository": repository,
                    "check_run_id": check_run.get("id"),
                    "scan_triggered": True
                }

        return {
            "status": "processed",
            "event": "pull_request",
            "action": action,
            "pr_number": pr_info.number,
            "repository": repository
        }

    async def _handle_pr_review(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pull request review event."""
        action = payload.get("action")
        review = payload.get("review", {})

        return {
            "status": "processed",
            "event": "pull_request_review",
            "action": action,
            "state": review.get("state")
        }

    async def _handle_installation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle installation event."""
        action = payload.get("action")
        installation = payload.get("installation", {})

        installation_info = InstallationInfo(
            installation_id=installation.get("id"),
            account_login=installation.get("account", {}).get("login"),
            account_type=installation.get("account", {}).get("type"),
            repository_selection=installation.get("repository_selection"),
            access_tokens_url=installation.get("access_tokens_url"),
            repositories_url=installation.get("repositories_url")
        )

        logger.info(f"Installation {action}: {installation_info.account_login}")

        return {
            "status": "processed",
            "event": "installation",
            "action": action,
            "installation_id": installation_info.installation_id,
            "account": installation_info.account_login
        }

    async def _handle_check_suite(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle check suite event."""
        action = payload.get("action")
        check_suite = payload.get("check_suite", {})

        if action == "requested":
            # Create check runs for the suite
            pass

        return {
            "status": "processed",
            "event": "check_suite",
            "action": action
        }

    async def create_check_run(
        self,
        token: str,
        repository: str,
        head_sha: str,
        name: str
    ) -> Dict[str, Any]:
        """
        Create a check run.

        Args:
            token: Installation access token
            repository: Repository full name (owner/repo)
            head_sha: Commit SHA
            name: Check run name

        Returns:
            Check run data
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._api_base}/repos/{repository}/check-runs",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "name": name,
                    "head_sha": head_sha,
                    "status": CheckStatus.IN_PROGRESS.value,
                    "started_at": datetime.utcnow().isoformat() + "Z"
                }
            ) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error = await response.text()
                    logger.error(f"Failed to create check run: {error}")
                    return {}

    async def update_check_run(
        self,
        token: str,
        repository: str,
        check_run_id: int,
        status: CheckStatus,
        conclusion: Optional[CheckConclusion] = None,
        output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update a check run.

        Args:
            token: Installation access token
            repository: Repository full name
            check_run_id: Check run ID
            status: New status
            conclusion: Conclusion (required if status is completed)
            output: Output object with title, summary, annotations

        Returns:
            Updated check run data
        """
        data = {"status": status.value}

        if status == CheckStatus.COMPLETED:
            data["conclusion"] = conclusion.value if conclusion else CheckConclusion.SUCCESS.value
            data["completed_at"] = datetime.utcnow().isoformat() + "Z"

        if output:
            data["output"] = output

        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"{self._api_base}/repos/{repository}/check-runs/{check_run_id}",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    logger.error(f"Failed to update check run: {error}")
                    return {}

    async def create_pr_comment(
        self,
        token: str,
        repository: str,
        pr_number: int,
        body: str
    ) -> Dict[str, Any]:
        """
        Create a comment on a pull request.

        Args:
            token: Installation access token
            repository: Repository full name
            pr_number: PR number
            body: Comment body (markdown)

        Returns:
            Comment data
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._api_base}/repos/{repository}/issues/{pr_number}/comments",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={"body": body}
            ) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error = await response.text()
                    logger.error(f"Failed to create PR comment: {error}")
                    return {}

    async def create_pr_review_comment(
        self,
        token: str,
        repository: str,
        pr_number: int,
        commit_id: str,
        path: str,
        line: int,
        body: str
    ) -> Dict[str, Any]:
        """
        Create an inline review comment on a PR.

        Args:
            token: Installation access token
            repository: Repository full name
            pr_number: PR number
            commit_id: Commit SHA
            path: File path
            line: Line number
            body: Comment body

        Returns:
            Comment data
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._api_base}/repos/{repository}/pulls/{pr_number}/comments",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "body": body,
                    "commit_id": commit_id,
                    "path": path,
                    "line": line
                }
            ) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error = await response.text()
                    logger.error(f"Failed to create review comment: {error}")
                    return {}

    async def get_pr_files(
        self,
        token: str,
        repository: str,
        pr_number: int
    ) -> List[Dict[str, Any]]:
        """
        Get files changed in a pull request.

        Args:
            token: Installation access token
            repository: Repository full name
            pr_number: PR number

        Returns:
            List of file changes
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self._api_base}/repos/{repository}/pulls/{pr_number}/files",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []

    async def get_file_content(
        self,
        token: str,
        repository: str,
        path: str,
        ref: str
    ) -> Optional[str]:
        """
        Get file content from repository.

        Args:
            token: Installation access token
            repository: Repository full name
            path: File path
            ref: Git reference (branch, tag, SHA)

        Returns:
            File content
        """
        import base64

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self._api_base}/repos/{repository}/contents/{path}",
                params={"ref": ref},
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get("content", "")
                    return base64.b64decode(content).decode("utf-8")
                else:
                    return None

    def format_scan_results_for_check(
        self,
        vulnerabilities: List[Dict[str, Any]],
        repository: str
    ) -> Dict[str, Any]:
        """
        Format scan results for check run output.

        Args:
            vulnerabilities: List of vulnerabilities
            repository: Repository name

        Returns:
            Check run output object
        """
        # Count by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for vuln in vulnerabilities:
            sev = vuln.get("severity", "medium").lower()
            if sev in severity_counts:
                severity_counts[sev] += 1

        # Determine conclusion
        if severity_counts["critical"] > 0 or severity_counts["high"] > 0:
            conclusion = "failure"
        elif severity_counts["medium"] > 0:
            conclusion = "neutral"
        else:
            conclusion = "success"

        # Build summary
        summary = f"""## Security Scan Results

**Repository**: {repository}

### Summary
- Critical: {severity_counts['critical']}
- High: {severity_counts['high']}
- Medium: {severity_counts['medium']}
- Low: {severity_counts['low']}

**Total**: {len(vulnerabilities)} vulnerabilities found
"""

        # Build annotations
        annotations = []
        for vuln in vulnerabilities[:50]:  # GitHub limits to 50
            annotation = {
                "path": vuln.get("file_path", "unknown"),
                "start_line": vuln.get("line_number", 1),
                "end_line": vuln.get("line_number", 1),
                "annotation_level": "failure" if vuln.get("severity") in ["critical", "high"] else "warning",
                "message": f"{vuln.get('title', 'Vulnerability')}: {vuln.get('description', '')}",
                "title": vuln.get("vulnerability_type", "Security Issue")
            }
            annotations.append(annotation)

        return {
            "title": f"IKODIO Security Scan - {len(vulnerabilities)} issues found",
            "summary": summary,
            "annotations": annotations,
            "conclusion": conclusion
        }


# Export for convenience
__all__ = [
    "GitHubApp",
    "GitHubAppConfig",
    "WebhookEvent",
    "CheckStatus",
    "CheckConclusion",
    "InstallationInfo",
    "PullRequestInfo"
]
