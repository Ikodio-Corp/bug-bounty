"""
Bitbucket Integration - VCS Integration Implementation

This module provides Bitbucket integration for automated security scanning
including webhook handling, PR comments, and build status updates.
"""

import hashlib
import hmac
import logging
import time
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BuildState(str, Enum):
    """Bitbucket build state."""
    INPROGRESS = "INPROGRESS"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    STOPPED = "STOPPED"


class PullRequestState(str, Enum):
    """Bitbucket PR state."""
    OPEN = "OPEN"
    MERGED = "MERGED"
    DECLINED = "DECLINED"
    SUPERSEDED = "SUPERSEDED"


class BitbucketConfig(BaseModel):
    """Bitbucket integration configuration."""
    base_url: str = "https://api.bitbucket.org/2.0"
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    webhook_secret: Optional[str] = None
    access_token: Optional[str] = None


class BitbucketIntegration:
    """
    Bitbucket Integration for security scanning.

    Provides:
    - Webhook handling for push, PR, and pipeline events
    - Build status updates
    - PR comments and inline annotations
    - Repository file access
    """

    def __init__(self, config: Optional[BitbucketConfig] = None):
        """Initialize Bitbucket integration."""
        self.config = config or BitbucketConfig()
        self.api_url = self.config.base_url.rstrip("/")

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Bitbucket webhook signature.

        Args:
            payload: Request payload
            signature: X-Hub-Signature header value

        Returns:
            True if signature is valid
        """
        if not self.config.webhook_secret:
            logger.warning("No webhook secret configured")
            return True

        expected = hmac.new(
            self.config.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(f"sha256={expected}", signature)

    async def get_access_token(self) -> str:
        """
        Get OAuth2 access token using client credentials.

        Returns:
            Access token
        """
        if self.config.access_token:
            return self.config.access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://bitbucket.org/site/oauth2/access_token",
                data={"grant_type": "client_credentials"},
                auth=(self.config.client_id, self.config.client_secret)
            )
            response.raise_for_status()
            return response.json()["access_token"]

    async def handle_webhook(
        self,
        event_key: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle incoming Bitbucket webhook event.

        Args:
            event_key: Event key (from X-Event-Key header)
            payload: Webhook payload

        Returns:
            Handling result
        """
        handlers = {
            "repo:push": self._handle_push,
            "pullrequest:created": self._handle_pr_created,
            "pullrequest:updated": self._handle_pr_updated,
            "pullrequest:fulfilled": self._handle_pr_merged,
            "repo:commit_status_created": self._handle_build_status,
            "repo:commit_status_updated": self._handle_build_status
        }

        handler = handlers.get(event_key)
        if handler:
            return await handler(payload)

        logger.info(f"Unhandled Bitbucket event: {event_key}")
        return {"status": "ignored", "reason": f"Unhandled event: {event_key}"}

    async def _handle_push(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle push event."""
        repository = payload.get("repository", {})
        push = payload.get("push", {})
        changes = push.get("changes", [])

        workspace = repository.get("workspace", {}).get("slug", "")
        repo_slug = repository.get("slug", "")

        # Collect changed files from all commits
        changed_files = set()
        commits = []

        for change in changes:
            new_target = change.get("new", {})
            if new_target:
                commit_hash = new_target.get("target", {}).get("hash", "")
                branch = new_target.get("name", "")
                commits.append({
                    "hash": commit_hash,
                    "branch": branch
                })

        logger.info(f"Push to {workspace}/{repo_slug}: {len(commits)} changes")

        return {
            "action": "scan_push",
            "workspace": workspace,
            "repo_slug": repo_slug,
            "full_name": repository.get("full_name"),
            "commits": commits,
            "changed_files": list(changed_files)
        }

    async def _handle_pr_created(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PR created event."""
        return await self._handle_pr_event(payload, "created")

    async def _handle_pr_updated(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PR updated event."""
        return await self._handle_pr_event(payload, "updated")

    async def _handle_pr_event(
        self,
        payload: Dict[str, Any],
        action: str
    ) -> Dict[str, Any]:
        """Handle PR events."""
        pr = payload.get("pullrequest", {})
        repository = payload.get("repository", {})

        workspace = repository.get("workspace", {}).get("slug", "")
        repo_slug = repository.get("slug", "")

        source = pr.get("source", {})
        destination = pr.get("destination", {})

        logger.info(f"PR #{pr.get('id')} {action} in {workspace}/{repo_slug}")

        return {
            "action": "scan_pull_request",
            "workspace": workspace,
            "repo_slug": repo_slug,
            "pr_id": pr.get("id"),
            "title": pr.get("title"),
            "state": pr.get("state"),
            "source_branch": source.get("branch", {}).get("name"),
            "source_commit": source.get("commit", {}).get("hash"),
            "destination_branch": destination.get("branch", {}).get("name"),
            "author": pr.get("author", {}).get("display_name")
        }

    async def _handle_pr_merged(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PR merged event."""
        pr = payload.get("pullrequest", {})
        repository = payload.get("repository", {})

        return {
            "action": "pr_merged",
            "workspace": repository.get("workspace", {}).get("slug"),
            "repo_slug": repository.get("slug"),
            "pr_id": pr.get("id"),
            "merge_commit": pr.get("merge_commit", {}).get("hash")
        }

    async def _handle_build_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle build status event."""
        commit_status = payload.get("commit_status", {})

        return {
            "action": "build_status_update",
            "state": commit_status.get("state"),
            "name": commit_status.get("name"),
            "url": commit_status.get("url")
        }

    async def create_build_status(
        self,
        token: str,
        workspace: str,
        repo_slug: str,
        commit: str,
        state: BuildState,
        key: str,
        name: str,
        description: str = "",
        url: str = ""
    ) -> Dict[str, Any]:
        """
        Create build status for a commit.

        Args:
            token: Access token
            workspace: Workspace slug
            repo_slug: Repository slug
            commit: Commit hash
            state: Build state
            key: Unique key for this status
            name: Status name
            description: Status description
            url: URL to link to

        Returns:
            Created status info
        """
        async with httpx.AsyncClient() as client:
            data = {
                "state": state.value,
                "key": key,
                "name": name,
                "description": description[:255] if description else ""
            }
            if url:
                data["url"] = url

            response = await client.post(
                f"{self.api_url}/repositories/{workspace}/{repo_slug}/commit/{commit}/statuses/build",
                headers={"Authorization": f"Bearer {token}"},
                json=data
            )
            response.raise_for_status()
            return response.json()

    async def create_pr_comment(
        self,
        token: str,
        workspace: str,
        repo_slug: str,
        pr_id: int,
        content: str
    ) -> Dict[str, Any]:
        """
        Create a comment on a pull request.

        Args:
            token: Access token
            workspace: Workspace slug
            repo_slug: Repository slug
            pr_id: Pull request ID
            content: Comment content (Markdown supported)

        Returns:
            Created comment info
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments",
                headers={"Authorization": f"Bearer {token}"},
                json={"content": {"raw": content}}
            )
            response.raise_for_status()
            return response.json()

    async def create_inline_comment(
        self,
        token: str,
        workspace: str,
        repo_slug: str,
        pr_id: int,
        content: str,
        file_path: str,
        line: int
    ) -> Dict[str, Any]:
        """
        Create an inline comment on a specific line in PR diff.

        Args:
            token: Access token
            workspace: Workspace slug
            repo_slug: Repository slug
            pr_id: Pull request ID
            content: Comment content
            file_path: Path to file
            line: Line number

        Returns:
            Created comment info
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "content": {"raw": content},
                    "inline": {
                        "path": file_path,
                        "to": line
                    }
                }
            )
            response.raise_for_status()
            return response.json()

    async def get_file_content(
        self,
        token: str,
        workspace: str,
        repo_slug: str,
        file_path: str,
        ref: str = "main"
    ) -> str:
        """
        Get file content from repository.

        Args:
            token: Access token
            workspace: Workspace slug
            repo_slug: Repository slug
            file_path: Path to file
            ref: Branch, tag, or commit

        Returns:
            File content
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/repositories/{workspace}/{repo_slug}/src/{ref}/{file_path}",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.text

    async def get_pr_diff(
        self,
        token: str,
        workspace: str,
        repo_slug: str,
        pr_id: int
    ) -> str:
        """
        Get pull request diff.

        Args:
            token: Access token
            workspace: Workspace slug
            repo_slug: Repository slug
            pr_id: Pull request ID

        Returns:
            Diff content
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/diff",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.text

    async def get_pr_files(
        self,
        token: str,
        workspace: str,
        repo_slug: str,
        pr_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get list of files changed in PR.

        Args:
            token: Access token
            workspace: Workspace slug
            repo_slug: Repository slug
            pr_id: Pull request ID

        Returns:
            List of changed files
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/diffstat",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            data = response.json()

            files = []
            for item in data.get("values", []):
                files.append({
                    "path": item.get("new", {}).get("path") or item.get("old", {}).get("path"),
                    "status": item.get("status"),
                    "lines_added": item.get("lines_added", 0),
                    "lines_removed": item.get("lines_removed", 0)
                })

            return files

    async def create_report(
        self,
        token: str,
        workspace: str,
        repo_slug: str,
        commit: str,
        report_id: str,
        title: str,
        details: str,
        report_type: str = "SECURITY",
        result: str = "PASSED",
        data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a code insights report.

        Args:
            token: Access token
            workspace: Workspace slug
            repo_slug: Repository slug
            commit: Commit hash
            report_id: Unique report ID
            title: Report title
            details: Report details
            report_type: Report type (SECURITY, COVERAGE, TEST, BUG)
            result: Result (PASSED, FAILED, PENDING)
            data: Report data items

        Returns:
            Created report info
        """
        async with httpx.AsyncClient() as client:
            report_data = {
                "title": title,
                "details": details,
                "report_type": report_type,
                "result": result
            }
            if data:
                report_data["data"] = data

            response = await client.put(
                f"{self.api_url}/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{report_id}",
                headers={"Authorization": f"Bearer {token}"},
                json=report_data
            )
            response.raise_for_status()
            return response.json()

    async def add_report_annotations(
        self,
        token: str,
        workspace: str,
        repo_slug: str,
        commit: str,
        report_id: str,
        annotations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Add annotations to a code insights report.

        Args:
            token: Access token
            workspace: Workspace slug
            repo_slug: Repository slug
            commit: Commit hash
            report_id: Report ID
            annotations: List of annotations

        Returns:
            Result info
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{report_id}/annotations",
                headers={"Authorization": f"Bearer {token}"},
                json=annotations
            )
            response.raise_for_status()
            return response.json()

    def format_scan_results_for_pr(
        self,
        vulnerabilities: List[Dict[str, Any]],
        scan_time_ms: int
    ) -> str:
        """
        Format scan results as Markdown for PR comment.

        Args:
            vulnerabilities: List of vulnerabilities
            scan_time_ms: Scan time in milliseconds

        Returns:
            Formatted Markdown string
        """
        if not vulnerabilities:
            return f"""## Security Scan Results

**No vulnerabilities detected**

Scan completed in {scan_time_ms / 1000:.2f}s
"""

        # Count by severity
        severity_counts = {}
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "unknown").upper()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Build summary
        summary_parts = []
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if severity in severity_counts:
                summary_parts.append(f"{severity_counts[severity]} {severity}")

        summary = " | ".join(summary_parts) if summary_parts else "No issues"

        # Build vulnerability list
        vuln_list = []
        for vuln in vulnerabilities[:15]:
            severity = vuln.get("severity", "unknown").upper()
            vuln_type = vuln.get("vulnerability_type", vuln.get("type", "Unknown"))
            file_path = vuln.get("file_path", "")
            line = vuln.get("line_number", vuln.get("line", ""))
            location = f"`{file_path}:{line}`" if file_path and line else "-"

            vuln_list.append(f"| {severity} | {vuln_type} | {location} |")

        table = "\n".join(vuln_list)

        more_text = ""
        if len(vulnerabilities) > 15:
            more_text = f"\n\n*... and {len(vulnerabilities) - 15} more vulnerabilities*"

        return f"""## Security Scan Results

**Summary:** {summary}

| Severity | Type | Location |
|----------|------|----------|
{table}{more_text}

---
Scan completed in {scan_time_ms / 1000:.2f}s | Total: {len(vulnerabilities)} vulnerabilities
"""

    def format_vulnerability_for_inline(self, vulnerability: Dict[str, Any]) -> str:
        """
        Format single vulnerability for inline comment.

        Args:
            vulnerability: Vulnerability data

        Returns:
            Formatted comment content
        """
        severity = vulnerability.get("severity", "unknown").upper()
        vuln_type = vulnerability.get("vulnerability_type", vulnerability.get("type", "Unknown"))
        description = vulnerability.get("description", "")
        recommendation = vulnerability.get("recommendation", "")

        comment = f"""**{severity}: {vuln_type}**

{description}
"""

        if recommendation:
            comment += f"\n**Recommendation:** {recommendation}\n"

        return comment

    def format_annotations_for_report(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Format vulnerabilities as Bitbucket report annotations.

        Args:
            vulnerabilities: List of vulnerabilities

        Returns:
            List of annotations
        """
        severity_map = {
            "critical": "CRITICAL",
            "high": "HIGH",
            "medium": "MEDIUM",
            "low": "LOW"
        }

        annotations = []
        for i, vuln in enumerate(vulnerabilities):
            severity = vuln.get("severity", "medium").lower()

            annotation = {
                "external_id": f"vuln-{i}",
                "path": vuln.get("file_path", "unknown"),
                "line": vuln.get("line_number", vuln.get("line", 1)),
                "summary": vuln.get("vulnerability_type", vuln.get("type", "Security issue")),
                "details": vuln.get("description", ""),
                "annotation_type": "VULNERABILITY",
                "severity": severity_map.get(severity, "MEDIUM")
            }

            annotations.append(annotation)

        return annotations


# Factory function
def create_bitbucket_integration(
    config: Optional[BitbucketConfig] = None
) -> BitbucketIntegration:
    """Create Bitbucket integration instance."""
    return BitbucketIntegration(config)


__all__ = [
    "BitbucketIntegration",
    "BitbucketConfig",
    "BuildState",
    "PullRequestState",
    "create_bitbucket_integration"
]
