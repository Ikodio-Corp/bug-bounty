"""
Real-Time Scanner - 90-Second Promise Implementation

This module implements real-time scanning capabilities with async processing,
streaming results, and performance optimization for the 90-second promise.
"""

import asyncio
import hashlib
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional, Set
from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ScanType(str, Enum):
    """Types of scans."""
    QUICK = "quick"  # 90 seconds
    STANDARD = "standard"  # 5 minutes
    DEEP = "deep"  # 30 minutes
    CONTINUOUS = "continuous"  # Ongoing


class ScanStatus(str, Enum):
    """Scan status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ScanTarget(BaseModel):
    """Scan target information."""
    target_id: str
    target_type: str  # file, directory, repository, url
    path: str
    language: Optional[str] = None
    framework: Optional[str] = None
    size_bytes: int = 0
    file_count: int = 0


class ScanResult(BaseModel):
    """Individual scan result."""
    result_id: str
    scan_id: str
    target: ScanTarget
    vulnerabilities: List[Dict[str, Any]] = []
    exploits: List[Dict[str, Any]] = []
    patches: List[Dict[str, Any]] = []
    scan_time_ms: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ScanJob(BaseModel):
    """Scan job information."""
    scan_id: str
    scan_type: ScanType
    targets: List[ScanTarget]
    status: ScanStatus = ScanStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    files_scanned: int = 0
    total_files: int = 0
    vulnerabilities_found: int = 0
    total_scan_time_ms: int = 0
    error_message: Optional[str] = None
    results: List[ScanResult] = []


class RealTimeScannerConfig(BaseModel):
    """Configuration for real-time scanner."""
    max_concurrent_scans: int = 10
    max_file_size_mb: int = 10
    timeout_quick_seconds: int = 90
    timeout_standard_seconds: int = 300
    timeout_deep_seconds: int = 1800
    enable_exploit_generation: bool = True
    enable_patch_generation: bool = True
    enable_streaming: bool = True
    supported_languages: List[str] = ["python", "javascript", "typescript", "java", "go", "php", "ruby"]


class RealTimeScanner:
    """
    Real-Time Vulnerability Scanner implementing the 90-second promise.

    Features:
    - Quick scan (90 seconds)
    - Async processing
    - Streaming results
    - Automatic exploit/patch generation
    - Performance monitoring
    """

    def __init__(self, config: Optional[RealTimeScannerConfig] = None):
        """Initialize the real-time scanner."""
        self.config = config or RealTimeScannerConfig()

        self._active_scans: Dict[str, ScanJob] = {}
        self._scan_semaphore = asyncio.Semaphore(self.config.max_concurrent_scans)

        # Import models
        self._bug_detector = None
        self._exploit_generator = None
        self._patch_generator = None

        logger.info("RealTimeScanner initialized")

    async def _initialize_models(self) -> None:
        """Initialize ML models lazily."""
        if self._bug_detector is None:
            from ..models.bug_detector import BugDetectorModel
            self._bug_detector = BugDetectorModel()
            await self._bug_detector.load_models()

        if self._exploit_generator is None and self.config.enable_exploit_generation:
            from ..models.exploit_generator import ExploitGeneratorModel
            self._exploit_generator = ExploitGeneratorModel()

        if self._patch_generator is None and self.config.enable_patch_generation:
            from ..models.patch_generator import PatchGeneratorModel
            self._patch_generator = PatchGeneratorModel()

    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID."""
        content = f"{prefix}:{time.time()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension."""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".go": "go",
            ".php": "php",
            ".rb": "ruby",
            ".cs": "csharp",
            ".cpp": "cpp",
            ".c": "c",
            ".rs": "rust",
        }

        path = Path(file_path)
        return extension_map.get(path.suffix.lower())

    async def create_scan(
        self,
        targets: List[Dict[str, Any]],
        scan_type: ScanType = ScanType.QUICK
    ) -> ScanJob:
        """
        Create a new scan job.

        Args:
            targets: List of scan targets
            scan_type: Type of scan

        Returns:
            Scan job
        """
        scan_id = self._generate_id("scan")

        # Convert targets
        scan_targets = []
        total_files = 0

        for target in targets:
            scan_target = ScanTarget(
                target_id=self._generate_id("target"),
                target_type=target.get("type", "file"),
                path=target["path"],
                language=target.get("language") or self._detect_language(target["path"]),
                framework=target.get("framework"),
                size_bytes=target.get("size_bytes", 0),
                file_count=target.get("file_count", 1)
            )
            scan_targets.append(scan_target)
            total_files += scan_target.file_count

        job = ScanJob(
            scan_id=scan_id,
            scan_type=scan_type,
            targets=scan_targets,
            total_files=total_files
        )

        self._active_scans[scan_id] = job
        logger.info(f"Created scan job {scan_id} with {len(scan_targets)} targets")

        return job

    async def start_scan(self, scan_id: str) -> ScanJob:
        """
        Start a scan job.

        Args:
            scan_id: Scan job ID

        Returns:
            Updated scan job
        """
        job = self._active_scans.get(scan_id)
        if not job:
            raise ValueError(f"Scan {scan_id} not found")

        if job.status != ScanStatus.PENDING:
            raise ValueError(f"Scan {scan_id} is not pending")

        # Start scan in background
        asyncio.create_task(self._run_scan(scan_id))

        return job

    async def _run_scan(self, scan_id: str) -> None:
        """Run the actual scan."""
        job = self._active_scans[scan_id]

        async with self._scan_semaphore:
            try:
                await self._initialize_models()

                job.status = ScanStatus.RUNNING
                job.started_at = datetime.utcnow()
                start_time = time.time()

                # Get timeout based on scan type
                timeout_map = {
                    ScanType.QUICK: self.config.timeout_quick_seconds,
                    ScanType.STANDARD: self.config.timeout_standard_seconds,
                    ScanType.DEEP: self.config.timeout_deep_seconds,
                }
                timeout = timeout_map.get(job.scan_type, 90)

                # Scan each target
                for i, target in enumerate(job.targets):
                    # Check timeout
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        logger.warning(f"Scan {scan_id} timeout after {elapsed:.2f}s")
                        break

                    result = await self._scan_target(job, target)
                    job.results.append(result)
                    job.vulnerabilities_found += len(result.vulnerabilities)
                    job.files_scanned += target.file_count
                    job.progress = (i + 1) / len(job.targets)

                job.total_scan_time_ms = int((time.time() - start_time) * 1000)
                job.status = ScanStatus.COMPLETED
                job.completed_at = datetime.utcnow()

                logger.info(
                    f"Scan {scan_id} completed: {job.vulnerabilities_found} vulnerabilities "
                    f"in {job.total_scan_time_ms}ms"
                )

            except Exception as e:
                job.status = ScanStatus.FAILED
                job.error_message = str(e)
                logger.error(f"Scan {scan_id} failed: {e}")

    async def _scan_target(self, job: ScanJob, target: ScanTarget) -> ScanResult:
        """Scan a single target."""
        start_time = time.time()
        result_id = self._generate_id("result")

        vulnerabilities = []
        exploits = []
        patches = []

        try:
            # Read file content (in production, this would read actual files)
            # For now, we'll use the path as a placeholder
            code = target.path  # Placeholder

            # Detect vulnerabilities
            if self._bug_detector:
                detections = await self._bug_detector.detect(
                    code=code,
                    file_path=target.path,
                    language=target.language
                )

                for detection in detections:
                    vuln_dict = {
                        "vulnerability_id": detection.vulnerability_id,
                        "vulnerability_type": detection.vulnerability_type.value,
                        "severity": detection.severity.value,
                        "confidence": detection.confidence,
                        "title": detection.title,
                        "description": detection.description,
                        "line_number": detection.line_number,
                        "code_snippet": detection.code_snippet,
                        "cwe_id": detection.cwe_id,
                        "cvss_score": detection.cvss_score,
                        "remediation": detection.remediation
                    }
                    vulnerabilities.append(vuln_dict)

                    # Generate exploit if enabled
                    if self.config.enable_exploit_generation and self._exploit_generator:
                        try:
                            from ..models.exploit_generator import ExploitLanguage, SophisticationLevel

                            language = ExploitLanguage.PYTHON
                            if target.language == "javascript":
                                language = ExploitLanguage.JAVASCRIPT

                            exploit = await self._exploit_generator.generate(
                                vulnerability_type=detection.vulnerability_type.value,
                                target_url=f"http://target/{target.path}",
                                vulnerable_param="param",
                                language=language,
                                sophistication=SophisticationLevel.INTERMEDIATE
                            )

                            exploits.append({
                                "exploit_id": exploit.exploit_id,
                                "vulnerability_id": detection.vulnerability_id,
                                "language": exploit.language.value,
                                "code": exploit.code[:500]  # Truncate for storage
                            })
                        except Exception as e:
                            logger.warning(f"Failed to generate exploit: {e}")

                    # Generate patch if enabled
                    if self.config.enable_patch_generation and self._patch_generator:
                        try:
                            from ..models.patch_generator import PatchLanguage

                            lang = PatchLanguage.PYTHON
                            if target.language in ["javascript", "typescript"]:
                                lang = PatchLanguage.JAVASCRIPT

                            patch = await self._patch_generator.generate(
                                vulnerability_id=detection.vulnerability_id,
                                vulnerability_type=detection.vulnerability_type.value,
                                original_code=code,
                                file_path=target.path,
                                language=lang
                            )

                            patches.append({
                                "patch_id": patch.patch_id,
                                "vulnerability_id": detection.vulnerability_id,
                                "description": patch.description,
                                "diff_preview": patch.diffs[0].diff_text[:300] if patch.diffs else ""
                            })
                        except Exception as e:
                            logger.warning(f"Failed to generate patch: {e}")

        except Exception as e:
            logger.error(f"Error scanning target {target.path}: {e}")

        return ScanResult(
            result_id=result_id,
            scan_id=job.scan_id,
            target=target,
            vulnerabilities=vulnerabilities,
            exploits=exploits,
            patches=patches,
            scan_time_ms=int((time.time() - start_time) * 1000)
        )

    async def stream_results(
        self,
        scan_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream scan results as they become available.

        Args:
            scan_id: Scan job ID

        Yields:
            Scan results
        """
        job = self._active_scans.get(scan_id)
        if not job:
            raise ValueError(f"Scan {scan_id} not found")

        last_result_count = 0

        while job.status in [ScanStatus.PENDING, ScanStatus.RUNNING]:
            # Yield new results
            if len(job.results) > last_result_count:
                for result in job.results[last_result_count:]:
                    yield {
                        "type": "result",
                        "data": result.dict()
                    }
                last_result_count = len(job.results)

            # Yield progress update
            yield {
                "type": "progress",
                "data": {
                    "scan_id": scan_id,
                    "progress": job.progress,
                    "files_scanned": job.files_scanned,
                    "vulnerabilities_found": job.vulnerabilities_found
                }
            }

            await asyncio.sleep(0.5)

        # Yield any remaining results
        for result in job.results[last_result_count:]:
            yield {
                "type": "result",
                "data": result.dict()
            }

        # Yield completion
        yield {
            "type": "completed",
            "data": {
                "scan_id": scan_id,
                "status": job.status.value,
                "total_vulnerabilities": job.vulnerabilities_found,
                "total_scan_time_ms": job.total_scan_time_ms
            }
        }

    async def quick_scan(
        self,
        code: str,
        file_path: str = "unknown.py",
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform a quick 90-second scan on code.

        Args:
            code: Source code to scan
            file_path: File path
            language: Programming language

        Returns:
            Scan results
        """
        start_time = time.time()

        await self._initialize_models()

        # Detect vulnerabilities
        vulnerabilities = []
        if self._bug_detector:
            detections = await asyncio.wait_for(
                self._bug_detector.detect(code, file_path, language),
                timeout=80  # Leave time for exploit/patch generation
            )

            vulnerabilities = [
                {
                    "vulnerability_id": d.vulnerability_id,
                    "vulnerability_type": d.vulnerability_type.value,
                    "severity": d.severity.value,
                    "confidence": d.confidence,
                    "title": d.title,
                    "description": d.description,
                    "line_number": d.line_number,
                    "cwe_id": d.cwe_id,
                    "cvss_score": d.cvss_score,
                    "remediation": d.remediation
                }
                for d in detections
            ]

        scan_time = int((time.time() - start_time) * 1000)

        # Check 90-second promise
        if scan_time > 90000:
            logger.warning(f"Quick scan exceeded 90s: {scan_time}ms")

        return {
            "vulnerabilities": vulnerabilities,
            "scan_time_ms": scan_time,
            "files_scanned": 1,
            "promise_kept": scan_time <= 90000
        }

    def get_scan_status(self, scan_id: str) -> Optional[ScanJob]:
        """Get scan job status."""
        return self._active_scans.get(scan_id)

    def list_active_scans(self) -> List[ScanJob]:
        """List all active scans."""
        return [
            job for job in self._active_scans.values()
            if job.status in [ScanStatus.PENDING, ScanStatus.RUNNING]
        ]

    async def cancel_scan(self, scan_id: str) -> ScanJob:
        """Cancel a running scan."""
        job = self._active_scans.get(scan_id)
        if not job:
            raise ValueError(f"Scan {scan_id} not found")

        if job.status in [ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED]:
            raise ValueError(f"Scan {scan_id} already finished")

        job.status = ScanStatus.CANCELLED
        logger.info(f"Cancelled scan {scan_id}")

        return job


# Singleton instance
_scanner: Optional[RealTimeScanner] = None


def get_scanner() -> RealTimeScanner:
    """Get the global scanner instance."""
    global _scanner
    if _scanner is None:
        _scanner = RealTimeScanner()
    return _scanner


# Export for convenience
__all__ = [
    "RealTimeScanner",
    "RealTimeScannerConfig",
    "ScanJob",
    "ScanResult",
    "ScanTarget",
    "ScanType",
    "ScanStatus",
    "get_scanner"
]
