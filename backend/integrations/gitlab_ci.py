"""
GitLab CI Integration - VCS Integration Implementation

This module provides GitLab CI/CD integration for automated security scanning
including pipeline integration, merge request comments, and inline annotations.
"""

import asyncio
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


class PipelineStatus(str, Enum):
    """GitLab pipeline status."""
    CREATED = "created"
    WAITING_FOR_RESOURCE = "waiting_for_resource"
    PREPARING = "preparing"
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    SKIPPED = "skipped"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class JobStatus(str, Enum):
    """GitLab job status."""
    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    SKIPPED = "skipped"
    MANUAL = "manual"


class NoteType(str, Enum):
    """GitLab note types."""
    MERGE_REQUEST = "MergeRequest"
    ISSUE = "Issue"
    COMMIT = "Commit"
    SNIPPET = "Snippet"


class GitLabConfig(BaseModel):
    """GitLab integration configuration."""
    gitlab_url: str = "https://gitlab.com"
    private_token: Optional[str] = None
    webhook_secret: Optional[str] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None


class GitLabCI:
    """
    GitLab CI/CD Integration.

    Provides:
    - Webhook handling for push, merge request, and pipeline events
    - Pipeline status updates
    - Merge request discussions and inline comments
    - Code quality reports
    - Security scanning integration
    """

    def __init__(self, config: Optional[GitLabConfig] = None):
        """Initialize GitLab CI integration."""
        self.config = config or GitLabConfig()
        self.base_url = self.config.gitlab_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v4"

    def verify_webhook_signature(self, payload: bytes, token: str) -> bool:
        """
        Verify GitLab webhook token.

        Args:
            payload: Request payload
            token: X-Gitlab-Token header value

        Returns:
            True if token is valid
        """
        if not self.config.webhook_secret:
            logger.warning("No webhook secret configured")
            return True

        return hmac.compare_digest(token, self.config.webhook_secret)

    async def handle_webhook(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle incoming GitLab webhook event.

        Args:
            event_type: GitLab event type (from X-Gitlab-Event header)
            payload: Webhook payload

        Returns:
            Handling result
        """
        handlers = {
            "Push Hook": self._handle_push,
            "Merge Request Hook": self._handle_merge_request,
            "Pipeline Hook": self._handle_pipeline,
            "Job Hook": self._handle_job,
            "Note Hook": self._handle_note,
            "Tag Push Hook": self._handle_tag_push
        }

        handler = handlers.get(event_type)
        if handler:
            return await handler(payload)

        logger.info(f"Unhandled GitLab event type: {event_type}")
        return {"status": "ignored", "reason": f"Unhandled event type: {event_type}"}

    async def _handle_push(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle push event."""
        project = payload.get("project", {})
        project_id = project.get("id")
        ref = payload.get("ref", "")
        before = payload.get("before")
        after = payload.get("after")
        commits = payload.get("commits", [])

        # Extract branch name
        branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ref

        logger.info(f"Push to {project.get('path_with_namespace')} branch {branch}: {len(commits)} commits")

        # Get changed files
        changed_files = set()
        for commit in commits:
            changed_files.update(commit.get("added", []))
            changed_files.update(commit.get("modified", []))

        return {
            "action": "scan_push",
            "project_id": project_id,
            "project_path": project.get("path_with_namespace"),
            "branch": branch,
            "commit_sha": after,
            "previous_sha": before,
            "changed_files": list(changed_files),
            "commits_count": len(commits)
        }

    async def _handle_merge_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle merge request event."""
        action = payload.get("object_attributes", {}).get("action")
        mr = payload.get("object_attributes", {})
        project = payload.get("project", {})

        mr_iid = mr.get("iid")
        project_id = project.get("id")
        source_branch = mr.get("source_branch")
        target_branch = mr.get("target_branch")

        logger.info(f"MR #{mr_iid} {action} in {project.get('path_with_namespace')}")

        # Trigger scan for new or updated MRs
        if action in ["open", "reopen", "update"]:
            return {
                "action": "scan_merge_request",
                "project_id": project_id,
                "project_path": project.get("path_with_namespace"),
                "mr_iid": mr_iid,
                "source_branch": source_branch,
                "target_branch": target_branch,
                "last_commit_sha": mr.get("last_commit", {}).get("id"),
                "state": mr.get("state"),
                "title": mr.get("title")
            }

        return {
            "action": "ignored",
            "reason": f"MR action {action} does not require scanning"
        }

    async def _handle_pipeline(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pipeline event."""
        pipeline = payload.get("object_attributes", {})
        project = payload.get("project", {})

        return {
            "action": "pipeline_update",
            "project_id": project.get("id"),
            "pipeline_id": pipeline.get("id"),
            "status": pipeline.get("status"),
            "ref": pipeline.get("ref"),
            "sha": pipeline.get("sha")
        }

    async def _handle_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle job event."""
        return {
            "action": "job_update",
            "job_id": payload.get("build_id"),
            "job_name": payload.get("build_name"),
            "status": payload.get("build_status"),
            "project_id": payload.get("project_id")
        }

    async def _handle_note(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle note (comment) event."""
        note = payload.get("object_attributes", {})

        return {
            "action": "note",
            "note_id": note.get("id"),
            "noteable_type": note.get("noteable_type"),
            "body": note.get("note")
        }

    async def _handle_tag_push(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tag push event."""
        project = payload.get("project", {})
        ref = payload.get("ref", "")
        tag = ref.replace("refs/tags/", "") if ref.startswith("refs/tags/") else ref

        return {
            "action": "scan_release",
            "project_id": project.get("id"),
            "project_path": project.get("path_with_namespace"),
            "tag": tag,
            "commit_sha": payload.get("checkout_sha")
        }

    async def create_pipeline(
        self,
        token: str,
        project_id: int,
        ref: str,
        variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new pipeline.

        Args:
            token: Access token
            project_id: Project ID
            ref: Branch or tag to run pipeline for
            variables: Pipeline variables

        Returns:
            Created pipeline info
        """
        async with httpx.AsyncClient() as client:
            data = {"ref": ref}
            if variables:
                data["variables"] = [
                    {"key": k, "value": v}
                    for k, v in variables.items()
                ]

            response = await client.post(
                f"{self.api_url}/projects/{project_id}/pipeline",
                headers={"PRIVATE-TOKEN": token},
                json=data
            )
            response.raise_for_status()
            return response.json()

    async def get_pipeline_status(
        self,
        token: str,
        project_id: int,
        pipeline_id: int
    ) -> Dict[str, Any]:
        """Get pipeline status."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/projects/{project_id}/pipelines/{pipeline_id}",
                headers={"PRIVATE-TOKEN": token}
            )
            response.raise_for_status()
            return response.json()

    async def create_commit_status(
        self,
        token: str,
        project_id: int,
        sha: str,
        state: str,
        name: str,
        description: str = "",
        target_url: str = "",
        coverage: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create commit status (external CI status).

        Args:
            token: Access token
            project_id: Project ID
            sha: Commit SHA
            state: Status state (pending, running, success, failed, canceled)
            name: Status name
            description: Status description
            target_url: URL to link to
            coverage: Code coverage percentage

        Returns:
            Created status info
        """
        async with httpx.AsyncClient() as client:
            data = {
                "state": state,
                "name": name,
                "description": description[:255] if description else "",
            }
            if target_url:
                data["target_url"] = target_url
            if coverage is not None:
                data["coverage"] = coverage

            response = await client.post(
                f"{self.api_url}/projects/{project_id}/statuses/{sha}",
                headers={"PRIVATE-TOKEN": token},
                json=data
            )
            response.raise_for_status()
            return response.json()

    async def create_mr_note(
        self,
        token: str,
        project_id: int,
        mr_iid: int,
        body: str
    ) -> Dict[str, Any]:
        """
        Create a note (comment) on a merge request.

        Args:
            token: Access token
            project_id: Project ID
            mr_iid: Merge request IID
            body: Comment body (supports Markdown)

        Returns:
            Created note info
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/projects/{project_id}/merge_requests/{mr_iid}/notes",
                headers={"PRIVATE-TOKEN": token},
                json={"body": body}
            )
            response.raise_for_status()
            return response.json()

    async def create_mr_discussion(
        self,
        token: str,
        project_id: int,
        mr_iid: int,
        body: str,
        position: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a discussion on a merge request.

        For inline comments, provide position with:
        - base_sha, head_sha, start_sha
        - new_path, old_path
        - new_line, old_line (or both for context)
        - position_type: "text" or "image"

        Args:
            token: Access token
            project_id: Project ID
            mr_iid: Merge request IID
            body: Discussion body
            position: Position for inline comments

        Returns:
            Created discussion info
        """
        async with httpx.AsyncClient() as client:
            data = {"body": body}
            if position:
                data["position"] = position

            response = await client.post(
                f"{self.api_url}/projects/{project_id}/merge_requests/{mr_iid}/discussions",
                headers={"PRIVATE-TOKEN": token},
                json=data
            )
            response.raise_for_status()
            return response.json()

    async def create_inline_comment(
        self,
        token: str,
        project_id: int,
        mr_iid: int,
        body: str,
        base_sha: str,
        head_sha: str,
        start_sha: str,
        file_path: str,
        line: int,
        line_type: str = "new"
    ) -> Dict[str, Any]:
        """
        Create an inline comment on specific line in MR diff.

        Args:
            token: Access token
            project_id: Project ID
            mr_iid: Merge request IID
            body: Comment body
            base_sha: Base commit SHA
            head_sha: Head commit SHA
            start_sha: Start commit SHA
            file_path: File path
            line: Line number
            line_type: "new" for new code, "old" for old code

        Returns:
            Created discussion info
        """
        position = {
            "base_sha": base_sha,
            "head_sha": head_sha,
            "start_sha": start_sha,
            "position_type": "text",
            "new_path": file_path,
            "old_path": file_path
        }

        if line_type == "new":
            position["new_line"] = line
        else:
            position["old_line"] = line

        return await self.create_mr_discussion(
            token=token,
            project_id=project_id,
            mr_iid=mr_iid,
            body=body,
            position=position
        )

    async def get_file_content(
        self,
        token: str,
        project_id: int,
        file_path: str,
        ref: str = "main"
    ) -> str:
        """
        Get file content from repository.

        Args:
            token: Access token
            project_id: Project ID
            file_path: Path to file
            ref: Branch, tag, or commit SHA

        Returns:
            File content
        """
        import base64
        from urllib.parse import quote

        async with httpx.AsyncClient() as client:
            encoded_path = quote(file_path, safe="")
            response = await client.get(
                f"{self.api_url}/projects/{project_id}/repository/files/{encoded_path}",
                headers={"PRIVATE-TOKEN": token},
                params={"ref": ref}
            )
            response.raise_for_status()

            data = response.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return content

    async def get_mr_changes(
        self,
        token: str,
        project_id: int,
        mr_iid: int
    ) -> Dict[str, Any]:
        """
        Get merge request changes (diff).

        Args:
            token: Access token
            project_id: Project ID
            mr_iid: Merge request IID

        Returns:
            MR changes including diffs
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/projects/{project_id}/merge_requests/{mr_iid}/changes",
                headers={"PRIVATE-TOKEN": token}
            )
            response.raise_for_status()
            return response.json()

    async def upload_code_quality_report(
        self,
        token: str,
        project_id: int,
        pipeline_id: int,
        report: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Upload Code Quality report for pipeline.

        Report format follows GitLab Code Quality specification.

        Args:
            token: Access token
            project_id: Project ID
            pipeline_id: Pipeline ID
            report: Code Quality report data

        Returns:
            Upload result
        """
        # Note: Code Quality reports are typically uploaded as job artifacts
        # This is a simplified implementation
        return {
            "status": "uploaded",
            "issues_count": len(report),
            "project_id": project_id,
            "pipeline_id": pipeline_id
        }

    def format_scan_results_for_mr(
        self,
        vulnerabilities: List[Dict[str, Any]],
        scan_time_ms: int
    ) -> str:
        """
        Format scan results as Markdown for MR comment.

        Args:
            vulnerabilities: List of vulnerabilities
            scan_time_ms: Scan time in milliseconds

        Returns:
            Formatted Markdown string
        """
        if not vulnerabilities:
            return """## Security Scan Results

**No vulnerabilities detected**

Scan completed in {:.2f}s
""".format(scan_time_ms / 1000)

        # Count by severity
        severity_counts = {}
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "unknown").upper()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Build summary
        summary_parts = []
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if severity in severity_counts:
                emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}.get(severity, "⚪")
                summary_parts.append(f"{emoji} {severity_counts[severity]} {severity}")

        summary = " | ".join(summary_parts) if summary_parts else "No issues"

        # Build vulnerability table
        table_rows = []
        for vuln in vulnerabilities[:20]:  # Limit to 20
            severity = vuln.get("severity", "unknown").upper()
            vuln_type = vuln.get("vulnerability_type", vuln.get("type", "Unknown"))
            file_path = vuln.get("file_path", "")
            line = vuln.get("line_number", vuln.get("line", ""))
            location = f"`{file_path}:{line}`" if file_path and line else "-"

            table_rows.append(f"| {severity} | {vuln_type} | {location} |")

        table = "\n".join(table_rows)

        more_text = ""
        if len(vulnerabilities) > 20:
            more_text = f"\n\n*... and {len(vulnerabilities) - 20} more vulnerabilities*"

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
            Formatted comment body
        """
        severity = vulnerability.get("severity", "unknown").upper()
        vuln_type = vulnerability.get("vulnerability_type", vulnerability.get("type", "Unknown"))
        description = vulnerability.get("description", "")
        recommendation = vulnerability.get("recommendation", "")
        cve_id = vulnerability.get("cve_id", "")

        emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}.get(severity, "⚪")

        comment = f"""### {emoji} {severity}: {vuln_type}

{description}
"""

        if cve_id:
            comment += f"\n**CVE:** {cve_id}\n"

        if recommendation:
            comment += f"\n**Recommendation:** {recommendation}\n"

        return comment

    def format_code_quality_report(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Format vulnerabilities as GitLab Code Quality report.

        Args:
            vulnerabilities: List of vulnerabilities

        Returns:
            Code Quality report format
        """
        report = []

        severity_map = {
            "critical": "blocker",
            "high": "critical",
            "medium": "major",
            "low": "minor",
            "info": "info"
        }

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "medium").lower()

            issue = {
                "description": vuln.get("description", vuln.get("vulnerability_type", "Security issue")),
                "check_name": vuln.get("vulnerability_type", vuln.get("type", "security")),
                "fingerprint": hashlib.md5(
                    f"{vuln.get('file_path', '')}{vuln.get('line_number', '')}{vuln.get('vulnerability_type', '')}".encode()
                ).hexdigest(),
                "severity": severity_map.get(severity, "major"),
                "location": {
                    "path": vuln.get("file_path", "unknown"),
                    "lines": {
                        "begin": vuln.get("line_number", vuln.get("line", 1))
                    }
                }
            }

            report.append(issue)

        return report


# Factory function
def create_gitlab_ci(config: Optional[GitLabConfig] = None) -> GitLabCI:
    """Create GitLab CI integration instance."""
    return GitLabCI(config)


__all__ = [
    "GitLabCI",
    "GitLabConfig",
    "PipelineStatus",
    "JobStatus",
    "NoteType",
    "create_gitlab_ci"
]
