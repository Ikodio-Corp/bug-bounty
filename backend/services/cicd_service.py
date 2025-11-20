"""
CI/CD Pipeline Service - CI/CD Integration Implementation

This service orchestrates CI/CD pipeline integrations for automated
security scanning across GitHub Actions, GitLab CI, Bitbucket Pipelines,
Jenkins, and other CI/CD platforms.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PipelineProvider(str, Enum):
    """Supported CI/CD providers."""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    BITBUCKET_PIPELINES = "bitbucket_pipelines"
    JENKINS = "jenkins"
    CIRCLECI = "circleci"
    TRAVIS_CI = "travis_ci"
    AZURE_PIPELINES = "azure_pipelines"


class ScanTrigger(str, Enum):
    """Scan trigger types."""
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    MERGE_REQUEST = "merge_request"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    RELEASE = "release"
    TAG = "tag"


class ScanStatus(str, Enum):
    """Scan status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    CANCELLED = "cancelled"


class PipelineScanConfig(BaseModel):
    """Configuration for pipeline scan."""
    provider: PipelineProvider
    repository: str
    branch: str
    commit_sha: str
    trigger: ScanTrigger
    pr_number: Optional[int] = None
    workspace: Optional[str] = None  # For Bitbucket
    installation_id: Optional[int] = None  # For GitHub Apps
    project_id: Optional[int] = None  # For GitLab
    scan_type: str = "quick"
    fail_on_severity: str = "high"  # critical, high, medium, low
    block_pr: bool = True
    inline_comments: bool = True
    generate_report: bool = True


class PipelineScanResult(BaseModel):
    """Result of pipeline scan."""
    scan_id: str
    status: ScanStatus
    provider: PipelineProvider
    repository: str
    commit_sha: str
    vulnerabilities_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    should_block: bool
    scan_time_ms: int
    report_url: Optional[str] = None
    check_run_id: Optional[int] = None


class CICDService:
    """
    CI/CD Pipeline Integration Service.

    Orchestrates security scanning across multiple CI/CD platforms with:
    - Unified webhook handling
    - Automated scan triggering
    - Status reporting
    - PR/MR commenting
    - Quality gates
    """

    def __init__(self):
        """Initialize CI/CD service."""
        self._github_app = None
        self._gitlab_ci = None
        self._bitbucket = None
        self._ml_service = None
        self._active_scans: Dict[str, Dict[str, Any]] = {}

    async def initialize(self) -> None:
        """Initialize integrations."""
        from ..integrations import (
            create_github_app,
            create_gitlab_ci,
            create_bitbucket_integration
        )
        from .ml_service import get_ml_service

        self._github_app = create_github_app()
        self._gitlab_ci = create_gitlab_ci()
        self._bitbucket = create_bitbucket_integration()
        self._ml_service = get_ml_service()

        logger.info("CICDService initialized")

    async def trigger_scan(
        self,
        config: PipelineScanConfig
    ) -> PipelineScanResult:
        """
        Trigger security scan for a pipeline.

        Args:
            config: Scan configuration

        Returns:
            Scan result
        """
        await self.initialize()

        scan_id = f"cicd_{int(time.time() * 1000)}"
        start_time = time.time()

        # Track active scan
        self._active_scans[scan_id] = {
            "config": config,
            "status": ScanStatus.RUNNING,
            "started_at": datetime.utcnow()
        }

        try:
            # Set pending status
            await self._set_pending_status(config, scan_id)

            # Get files to scan
            files = await self._get_changed_files(config)

            # Perform security scan
            vulnerabilities = []
            for file_info in files:
                try:
                    content = await self._get_file_content(config, file_info["path"])
                    if content:
                        from .ml_service import ScanRequest
                        scan_request = ScanRequest(
                            code=content,
                            file_path=file_info["path"],
                            scan_type=config.scan_type
                        )
                        result = await self._ml_service.scan_code(scan_request)
                        vulnerabilities.extend(result.vulnerabilities)
                except Exception as e:
                    logger.warning(f"Error scanning {file_info['path']}: {e}")

            # Calculate counts
            critical = sum(1 for v in vulnerabilities if v.get("severity", "").lower() == "critical")
            high = sum(1 for v in vulnerabilities if v.get("severity", "").lower() == "high")
            medium = sum(1 for v in vulnerabilities if v.get("severity", "").lower() == "medium")
            low = sum(1 for v in vulnerabilities if v.get("severity", "").lower() == "low")

            # Determine if should block
            should_block = self._should_block_pr(
                critical, high, medium, low,
                config.fail_on_severity
            )

            scan_time = int((time.time() - start_time) * 1000)

            # Update status
            status = ScanStatus.FAILURE if should_block else ScanStatus.SUCCESS
            check_run_id = await self._update_status(
                config, scan_id, status, vulnerabilities, scan_time
            )

            # Add inline comments if enabled
            if config.inline_comments and vulnerabilities:
                await self._add_inline_comments(config, vulnerabilities)

            # Create result
            result = PipelineScanResult(
                scan_id=scan_id,
                status=status,
                provider=config.provider,
                repository=config.repository,
                commit_sha=config.commit_sha,
                vulnerabilities_count=len(vulnerabilities),
                critical_count=critical,
                high_count=high,
                medium_count=medium,
                low_count=low,
                should_block=should_block,
                scan_time_ms=scan_time,
                check_run_id=check_run_id
            )

            self._active_scans[scan_id]["result"] = result
            self._active_scans[scan_id]["status"] = status

            return result

        except Exception as e:
            logger.error(f"Pipeline scan failed: {e}")
            self._active_scans[scan_id]["status"] = ScanStatus.ERROR
            await self._set_error_status(config, scan_id, str(e))
            raise

    def _should_block_pr(
        self,
        critical: int,
        high: int,
        medium: int,
        low: int,
        fail_on_severity: str
    ) -> bool:
        """Determine if PR should be blocked based on severity threshold."""
        thresholds = {
            "critical": critical > 0,
            "high": critical > 0 or high > 0,
            "medium": critical > 0 or high > 0 or medium > 0,
            "low": critical > 0 or high > 0 or medium > 0 or low > 0
        }
        return thresholds.get(fail_on_severity.lower(), False)

    async def _set_pending_status(
        self,
        config: PipelineScanConfig,
        scan_id: str
    ) -> None:
        """Set pending status on the CI/CD platform."""
        try:
            if config.provider == PipelineProvider.GITHUB_ACTIONS:
                token = await self._github_app.get_installation_token(config.installation_id)
                await self._github_app.create_check_run(
                    token=token,
                    repository=config.repository,
                    head_sha=config.commit_sha,
                    name="Security Scan"
                )

            elif config.provider == PipelineProvider.GITLAB_CI:
                # Get token from config or environment
                token = ""  # Should come from config
                await self._gitlab_ci.create_commit_status(
                    token=token,
                    project_id=config.project_id,
                    sha=config.commit_sha,
                    state="pending",
                    name="security-scan",
                    description="Security scan in progress..."
                )

            elif config.provider == PipelineProvider.BITBUCKET_PIPELINES:
                token = await self._bitbucket.get_access_token()
                parts = config.repository.split("/")
                await self._bitbucket.create_build_status(
                    token=token,
                    workspace=parts[0] if len(parts) > 1 else config.workspace,
                    repo_slug=parts[-1],
                    commit=config.commit_sha,
                    state="INPROGRESS",
                    key="security-scan",
                    name="Security Scan",
                    description="Scanning for vulnerabilities..."
                )

        except Exception as e:
            logger.warning(f"Failed to set pending status: {e}")

    async def _update_status(
        self,
        config: PipelineScanConfig,
        scan_id: str,
        status: ScanStatus,
        vulnerabilities: List[Dict[str, Any]],
        scan_time_ms: int
    ) -> Optional[int]:
        """Update status on the CI/CD platform."""
        check_run_id = None

        try:
            if config.provider == PipelineProvider.GITHUB_ACTIONS:
                token = await self._github_app.get_installation_token(config.installation_id)

                # Format output
                output = self._github_app.format_scan_results_for_check(
                    vulnerabilities, config.repository
                )

                conclusion = "success" if status == ScanStatus.SUCCESS else "failure"

                # Create check run with results
                result = await self._github_app.create_check_run(
                    token=token,
                    repository=config.repository,
                    head_sha=config.commit_sha,
                    name="Security Scan"
                )
                check_run_id = result.get("id")

                # Update with conclusion
                from ..integrations.github_app import CheckStatus, CheckConclusion
                await self._github_app.update_check_run(
                    token=token,
                    repository=config.repository,
                    check_run_id=check_run_id,
                    status=CheckStatus.COMPLETED,
                    conclusion=CheckConclusion.SUCCESS if status == ScanStatus.SUCCESS else CheckConclusion.FAILURE,
                    output=output
                )

                # Add PR comment if applicable
                if config.pr_number:
                    comment = self._format_pr_comment(vulnerabilities, scan_time_ms)
                    await self._github_app.create_pr_comment(
                        token=token,
                        repository=config.repository,
                        pr_number=config.pr_number,
                        body=comment
                    )

            elif config.provider == PipelineProvider.GITLAB_CI:
                token = ""  # Should come from config
                state = "success" if status == ScanStatus.SUCCESS else "failed"

                await self._gitlab_ci.create_commit_status(
                    token=token,
                    project_id=config.project_id,
                    sha=config.commit_sha,
                    state=state,
                    name="security-scan",
                    description=f"Found {len(vulnerabilities)} vulnerabilities"
                )

                # Add MR comment if applicable
                if config.pr_number:
                    comment = self._gitlab_ci.format_scan_results_for_mr(
                        vulnerabilities, scan_time_ms
                    )
                    await self._gitlab_ci.create_mr_note(
                        token=token,
                        project_id=config.project_id,
                        mr_iid=config.pr_number,
                        body=comment
                    )

            elif config.provider == PipelineProvider.BITBUCKET_PIPELINES:
                token = await self._bitbucket.get_access_token()
                parts = config.repository.split("/")
                workspace = parts[0] if len(parts) > 1 else config.workspace
                repo_slug = parts[-1]

                state = "SUCCESSFUL" if status == ScanStatus.SUCCESS else "FAILED"

                await self._bitbucket.create_build_status(
                    token=token,
                    workspace=workspace,
                    repo_slug=repo_slug,
                    commit=config.commit_sha,
                    state=state,
                    key="security-scan",
                    name="Security Scan",
                    description=f"Found {len(vulnerabilities)} vulnerabilities"
                )

                # Add PR comment if applicable
                if config.pr_number:
                    comment = self._bitbucket.format_scan_results_for_pr(
                        vulnerabilities, scan_time_ms
                    )
                    await self._bitbucket.create_pr_comment(
                        token=token,
                        workspace=workspace,
                        repo_slug=repo_slug,
                        pr_id=config.pr_number,
                        content=comment
                    )

        except Exception as e:
            logger.error(f"Failed to update status: {e}")

        return check_run_id

    async def _set_error_status(
        self,
        config: PipelineScanConfig,
        scan_id: str,
        error_message: str
    ) -> None:
        """Set error status on the CI/CD platform."""
        try:
            if config.provider == PipelineProvider.GITHUB_ACTIONS:
                token = await self._github_app.get_installation_token(config.installation_id)
                from ..integrations.github_app import CheckStatus, CheckConclusion

                result = await self._github_app.create_check_run(
                    token=token,
                    repository=config.repository,
                    head_sha=config.commit_sha,
                    name="Security Scan"
                )

                await self._github_app.update_check_run(
                    token=token,
                    repository=config.repository,
                    check_run_id=result.get("id"),
                    status=CheckStatus.COMPLETED,
                    conclusion=CheckConclusion.FAILURE,
                    output={
                        "title": "Scan Error",
                        "summary": f"An error occurred during scanning: {error_message}"
                    }
                )

            elif config.provider == PipelineProvider.GITLAB_CI:
                token = ""
                await self._gitlab_ci.create_commit_status(
                    token=token,
                    project_id=config.project_id,
                    sha=config.commit_sha,
                    state="failed",
                    name="security-scan",
                    description=f"Error: {error_message[:100]}"
                )

            elif config.provider == PipelineProvider.BITBUCKET_PIPELINES:
                token = await self._bitbucket.get_access_token()
                parts = config.repository.split("/")
                await self._bitbucket.create_build_status(
                    token=token,
                    workspace=parts[0] if len(parts) > 1 else config.workspace,
                    repo_slug=parts[-1],
                    commit=config.commit_sha,
                    state="FAILED",
                    key="security-scan",
                    name="Security Scan",
                    description=f"Error: {error_message[:100]}"
                )

        except Exception as e:
            logger.error(f"Failed to set error status: {e}")

    async def _get_changed_files(
        self,
        config: PipelineScanConfig
    ) -> List[Dict[str, Any]]:
        """Get list of changed files from the CI/CD platform."""
        files = []

        try:
            if config.provider == PipelineProvider.GITHUB_ACTIONS and config.pr_number:
                token = await self._github_app.get_installation_token(config.installation_id)
                # Fetch PR files via GitHub API
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"https://api.github.com/repos/{config.repository}/pulls/{config.pr_number}/files",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Accept": "application/vnd.github+json"
                        }
                    )
                    if response.status_code == 200:
                        for f in response.json():
                            files.append({
                                "path": f["filename"],
                                "status": f["status"]
                            })

            elif config.provider == PipelineProvider.GITLAB_CI and config.pr_number:
                token = ""
                changes = await self._gitlab_ci.get_mr_changes(
                    token=token,
                    project_id=config.project_id,
                    mr_iid=config.pr_number
                )
                for change in changes.get("changes", []):
                    files.append({
                        "path": change.get("new_path") or change.get("old_path"),
                        "status": "modified"
                    })

            elif config.provider == PipelineProvider.BITBUCKET_PIPELINES and config.pr_number:
                token = await self._bitbucket.get_access_token()
                parts = config.repository.split("/")
                pr_files = await self._bitbucket.get_pr_files(
                    token=token,
                    workspace=parts[0] if len(parts) > 1 else config.workspace,
                    repo_slug=parts[-1],
                    pr_id=config.pr_number
                )
                files = pr_files

        except Exception as e:
            logger.warning(f"Failed to get changed files: {e}")

        return files

    async def _get_file_content(
        self,
        config: PipelineScanConfig,
        file_path: str
    ) -> Optional[str]:
        """Get file content from the repository."""
        try:
            if config.provider == PipelineProvider.GITHUB_ACTIONS:
                token = await self._github_app.get_installation_token(config.installation_id)
                return await self._github_app.get_file_content(
                    token=token,
                    repository=config.repository,
                    file_path=file_path,
                    ref=config.commit_sha
                )

            elif config.provider == PipelineProvider.GITLAB_CI:
                token = ""
                return await self._gitlab_ci.get_file_content(
                    token=token,
                    project_id=config.project_id,
                    file_path=file_path,
                    ref=config.commit_sha
                )

            elif config.provider == PipelineProvider.BITBUCKET_PIPELINES:
                token = await self._bitbucket.get_access_token()
                parts = config.repository.split("/")
                return await self._bitbucket.get_file_content(
                    token=token,
                    workspace=parts[0] if len(parts) > 1 else config.workspace,
                    repo_slug=parts[-1],
                    file_path=file_path,
                    ref=config.commit_sha
                )

        except Exception as e:
            logger.warning(f"Failed to get file content for {file_path}: {e}")
            return None

    async def _add_inline_comments(
        self,
        config: PipelineScanConfig,
        vulnerabilities: List[Dict[str, Any]]
    ) -> None:
        """Add inline comments for vulnerabilities."""
        try:
            if config.provider == PipelineProvider.GITHUB_ACTIONS and config.pr_number:
                token = await self._github_app.get_installation_token(config.installation_id)

                for vuln in vulnerabilities[:10]:  # Limit to 10 comments
                    file_path = vuln.get("file_path", "")
                    line = vuln.get("line_number", vuln.get("line", 0))

                    if file_path and line:
                        body = self._format_inline_comment(vuln)
                        await self._github_app.create_pr_review_comment(
                            token=token,
                            repository=config.repository,
                            pr_number=config.pr_number,
                            commit_id=config.commit_sha,
                            path=file_path,
                            line=line,
                            body=body
                        )

            elif config.provider == PipelineProvider.GITLAB_CI and config.pr_number:
                token = ""

                # Get MR info for SHA values
                mr_changes = await self._gitlab_ci.get_mr_changes(
                    token=token,
                    project_id=config.project_id,
                    mr_iid=config.pr_number
                )

                for vuln in vulnerabilities[:10]:
                    file_path = vuln.get("file_path", "")
                    line = vuln.get("line_number", vuln.get("line", 0))

                    if file_path and line:
                        body = self._gitlab_ci.format_vulnerability_for_inline(vuln)
                        await self._gitlab_ci.create_inline_comment(
                            token=token,
                            project_id=config.project_id,
                            mr_iid=config.pr_number,
                            body=body,
                            base_sha=mr_changes.get("diff_refs", {}).get("base_sha", ""),
                            head_sha=mr_changes.get("diff_refs", {}).get("head_sha", ""),
                            start_sha=mr_changes.get("diff_refs", {}).get("start_sha", ""),
                            file_path=file_path,
                            line=line
                        )

            elif config.provider == PipelineProvider.BITBUCKET_PIPELINES and config.pr_number:
                token = await self._bitbucket.get_access_token()
                parts = config.repository.split("/")

                for vuln in vulnerabilities[:10]:
                    file_path = vuln.get("file_path", "")
                    line = vuln.get("line_number", vuln.get("line", 0))

                    if file_path and line:
                        body = self._bitbucket.format_vulnerability_for_inline(vuln)
                        await self._bitbucket.create_inline_comment(
                            token=token,
                            workspace=parts[0] if len(parts) > 1 else config.workspace,
                            repo_slug=parts[-1],
                            pr_id=config.pr_number,
                            content=body,
                            file_path=file_path,
                            line=line
                        )

        except Exception as e:
            logger.warning(f"Failed to add inline comments: {e}")

    def _format_pr_comment(
        self,
        vulnerabilities: List[Dict[str, Any]],
        scan_time_ms: int
    ) -> str:
        """Format PR comment with scan results."""
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

        summary = " | ".join(summary_parts)

        # Build table
        rows = []
        for vuln in vulnerabilities[:20]:
            severity = vuln.get("severity", "unknown").upper()
            vuln_type = vuln.get("vulnerability_type", "Unknown")
            file_path = vuln.get("file_path", "")
            line = vuln.get("line_number", "")
            location = f"`{file_path}:{line}`" if file_path else "-"

            rows.append(f"| {severity} | {vuln_type} | {location} |")

        table = "\n".join(rows)

        return f"""## Security Scan Results

**Summary:** {summary}

| Severity | Type | Location |
|----------|------|----------|
{table}

---
Scan completed in {scan_time_ms / 1000:.2f}s | Total: {len(vulnerabilities)} vulnerabilities
"""

    def _format_inline_comment(self, vulnerability: Dict[str, Any]) -> str:
        """Format inline comment for a vulnerability."""
        severity = vulnerability.get("severity", "unknown").upper()
        vuln_type = vulnerability.get("vulnerability_type", "Unknown")
        description = vulnerability.get("description", "")
        recommendation = vulnerability.get("recommendation", "")

        comment = f"""**{severity}: {vuln_type}**

{description}
"""

        if recommendation:
            comment += f"\n**Recommendation:** {recommendation}"

        return comment

    def get_active_scans(self) -> List[Dict[str, Any]]:
        """Get list of active scans."""
        return [
            {
                "scan_id": scan_id,
                "config": scan_data.get("config"),
                "status": scan_data.get("status"),
                "started_at": scan_data.get("started_at")
            }
            for scan_id, scan_data in self._active_scans.items()
        ]

    def generate_github_actions_yaml(self) -> str:
        """Generate GitHub Actions workflow YAML for security scanning."""
        return """name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Security Scan
        uses: ikodio/security-scan-action@v1
        with:
          api-key: ${{ secrets.IKODIO_API_KEY }}
          fail-on-severity: high
          scan-type: quick
"""

    def generate_gitlab_ci_yaml(self) -> str:
        """Generate GitLab CI configuration for security scanning."""
        return """stages:
  - test
  - security

security-scan:
  stage: security
  image: ikodio/scanner:latest
  script:
    - ikodio-scan --api-key $IKODIO_API_KEY --fail-on-severity high
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
"""

    def generate_bitbucket_pipelines_yaml(self) -> str:
        """Generate Bitbucket Pipelines configuration for security scanning."""
        return """image: ikodio/scanner:latest

pipelines:
  default:
    - step:
        name: Security Scan
        script:
          - ikodio-scan --api-key $IKODIO_API_KEY --fail-on-severity high

  pull-requests:
    '**':
      - step:
          name: Security Scan
          script:
            - ikodio-scan --api-key $IKODIO_API_KEY --fail-on-severity high
"""


# Singleton instance
_cicd_service: Optional[CICDService] = None


def get_cicd_service() -> CICDService:
    """Get the global CI/CD service instance."""
    global _cicd_service
    if _cicd_service is None:
        _cicd_service = CICDService()
    return _cicd_service


__all__ = [
    "CICDService",
    "PipelineProvider",
    "ScanTrigger",
    "ScanStatus",
    "PipelineScanConfig",
    "PipelineScanResult",
    "get_cicd_service"
]
