"""
Secret Scanner - Detects hardcoded secrets and credentials
"""

import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import hashlib


class SecretScanner:
    """Scanner for detecting secrets in code"""
    
    def __init__(self):
        self.name = "Secret Scanner"
        self.patterns = self._initialize_patterns()
        
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize regex patterns for secret detection"""
        return {
            "aws_access_key": {
                "pattern": r"AKIA[0-9A-Z]{16}",
                "description": "AWS Access Key ID",
                "severity": "critical"
            },
            "aws_secret_key": {
                "pattern": r"aws_secret_access_key\s*=\s*['\"]([A-Za-z0-9/+=]{40})['\"]",
                "description": "AWS Secret Access Key",
                "severity": "critical"
            },
            "github_token": {
                "pattern": r"gh[pousr]_[A-Za-z0-9]{36}",
                "description": "GitHub Personal Access Token",
                "severity": "critical"
            },
            "github_oauth": {
                "pattern": r"gho_[A-Za-z0-9]{36}",
                "description": "GitHub OAuth Token",
                "severity": "critical"
            },
            "slack_token": {
                "pattern": r"xox[baprs]-[0-9]{10,12}-[0-9]{10,12}-[A-Za-z0-9]{24}",
                "description": "Slack Token",
                "severity": "high"
            },
            "slack_webhook": {
                "pattern": r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+",
                "description": "Slack Webhook URL",
                "severity": "medium"
            },
            "google_api_key": {
                "pattern": r"AIza[0-9A-Za-z\\-_]{35}",
                "description": "Google API Key",
                "severity": "high"
            },
            "google_oauth": {
                "pattern": r"[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com",
                "description": "Google OAuth Client ID",
                "severity": "medium"
            },
            "stripe_api_key": {
                "pattern": r"sk_live_[0-9a-zA-Z]{24}",
                "description": "Stripe Live API Key",
                "severity": "critical"
            },
            "stripe_restricted_key": {
                "pattern": r"rk_live_[0-9a-zA-Z]{24}",
                "description": "Stripe Restricted Key",
                "severity": "high"
            },
            "twilio_api_key": {
                "pattern": r"SK[0-9a-fA-F]{32}",
                "description": "Twilio API Key",
                "severity": "high"
            },
            "sendgrid_api_key": {
                "pattern": r"SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}",
                "description": "SendGrid API Key",
                "severity": "high"
            },
            "mailgun_api_key": {
                "pattern": r"key-[0-9a-zA-Z]{32}",
                "description": "MailGun API Key",
                "severity": "high"
            },
            "mailchimp_api_key": {
                "pattern": r"[0-9a-f]{32}-us[0-9]{1,2}",
                "description": "MailChimp API Key",
                "severity": "high"
            },
            "heroku_api_key": {
                "pattern": r"[hH][eE][rR][oO][kK][uU].*[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",
                "description": "Heroku API Key",
                "severity": "high"
            },
            "private_key": {
                "pattern": r"-----BEGIN (RSA |EC |DSA |PGP )?PRIVATE KEY( BLOCK)?-----",
                "description": "Private Key",
                "severity": "critical"
            },
            "jwt_token": {
                "pattern": r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
                "description": "JWT Token",
                "severity": "medium"
            },
            "generic_api_key": {
                "pattern": r"[aA][pP][iI]_?[kK][eE][yY]\s*[:=]\s*['\"]([0-9a-zA-Z]{32,45})['\"]",
                "description": "Generic API Key",
                "severity": "high"
            },
            "generic_secret": {
                "pattern": r"[sS][eE][cC][rR][eE][tT]\s*[:=]\s*['\"]([0-9a-zA-Z]{32,45})['\"]",
                "description": "Generic Secret",
                "severity": "high"
            },
            "password_in_url": {
                "pattern": r"[a-zA-Z]{3,10}://[^/\\s:@]{3,20}:[^/\\s:@]{3,20}@.{1,100}",
                "description": "Password in URL",
                "severity": "high"
            },
            "database_url": {
                "pattern": r"(postgres|mysql|mongodb|redis)://[^\\s]+:[^\\s]+@[^\\s]+",
                "description": "Database Connection String",
                "severity": "high"
            },
            "npm_token": {
                "pattern": r"npm_[A-Za-z0-9]{36}",
                "description": "NPM Access Token",
                "severity": "high"
            },
            "docker_token": {
                "pattern": r"dckr_pat_[A-Za-z0-9_-]{32,}",
                "description": "Docker Access Token",
                "severity": "high"
            },
            "gitlab_token": {
                "pattern": r"glpat-[A-Za-z0-9_-]{20}",
                "description": "GitLab Personal Access Token",
                "severity": "critical"
            },
            "bitbucket_token": {
                "pattern": r"BBDC-[A-Za-z0-9_-]{32,}",
                "description": "Bitbucket Access Token",
                "severity": "high"
            },
            "azure_pat": {
                "pattern": r"[a-z0-9]{52}",
                "description": "Azure Personal Access Token",
                "severity": "high"
            },
            "basic_auth": {
                "pattern": r"[aA]uthorization:\s*[bB]asic\s+[A-Za-z0-9+/=]{20,}",
                "description": "Basic Authentication Header",
                "severity": "medium"
            },
            "bearer_token": {
                "pattern": r"[aA]uthorization:\s*[bB]earer\s+[A-Za-z0-9_-]{20,}",
                "description": "Bearer Token",
                "severity": "medium"
            }
        }
    
    async def scan(
        self,
        target_path: str,
        scan_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Scan directory for secrets
        
        Args:
            target_path: Path to scan
            scan_options: Optional configuration
            
        Returns:
            Scan results with secrets found
        """
        scan_options = scan_options or {}
        
        results = {
            "scanner": self.name,
            "status": "completed",
            "secrets": [],
            "files_scanned": 0,
            "summary": {
                "total_secrets": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "by_type": {}
            }
        }
        
        try:
            path = Path(target_path)
            
            if path.is_file():
                await self._scan_file(path, results)
            elif path.is_dir():
                await self._scan_directory(path, results, scan_options)
            
            # Update summary
            for secret in results["secrets"]:
                severity = secret.get("severity", "medium").lower()
                results["summary"][severity] = results["summary"].get(severity, 0) + 1
                
                secret_type = secret.get("type")
                results["summary"]["by_type"][secret_type] = \
                    results["summary"]["by_type"].get(secret_type, 0) + 1
            
            results["summary"]["total_secrets"] = len(results["secrets"])
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    async def _scan_directory(
        self,
        directory: Path,
        results: Dict[str, Any],
        scan_options: Dict[str, Any]
    ):
        """Recursively scan directory for secrets"""
        
        # Extensions to scan
        scannable_extensions = {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".php",
            ".sh", ".bash", ".yaml", ".yml", ".json", ".xml", ".env", ".config",
            ".conf", ".properties", ".ini", ".toml", ".txt", ".md", ".sql",
            ".cs", ".cpp", ".c", ".h", ".hpp", ".rs", ".swift", ".kt", ".scala"
        }
        
        # Directories to skip
        skip_dirs = {
            ".git", "node_modules", "venv", "env", ".venv", "__pycache__",
            "dist", "build", ".next", ".nuxt", "vendor", "target", "bin",
            "obj", ".idea", ".vscode", "coverage", ".pytest_cache"
        }
        
        for item in directory.rglob("*"):
            # Skip directories
            if item.is_dir():
                if item.name in skip_dirs:
                    continue
                continue
            
            # Check if file should be scanned
            if item.suffix not in scannable_extensions and item.name not in [".env", ".env.local", ".env.production"]:
                continue
            
            # Skip large files (> 10MB)
            if item.stat().st_size > 10 * 1024 * 1024:
                continue
            
            await self._scan_file(item, results)
    
    async def _scan_file(self, file_path: Path, results: Dict[str, Any]):
        """Scan a single file for secrets"""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            results["files_scanned"] += 1
            
            lines = content.splitlines()
            
            for secret_type, pattern_info in self.patterns.items():
                pattern = pattern_info["pattern"]
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    # Find line number
                    line_num = content[:match.start()].count("\n") + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    # Create redacted version
                    matched_text = match.group(0)
                    if len(matched_text) > 20:
                        redacted = matched_text[:8] + "*" * (len(matched_text) - 12) + matched_text[-4:]
                    else:
                        redacted = "*" * len(matched_text)
                    
                    secret = {
                        "type": secret_type,
                        "description": pattern_info["description"],
                        "severity": pattern_info["severity"],
                        "file": str(file_path),
                        "line": line_num,
                        "line_content": line_content,
                        "matched_text": redacted,
                        "recommendation": self._get_recommendation(secret_type)
                    }
                    
                    # Avoid duplicates
                    if not self._is_duplicate(secret, results["secrets"]):
                        results["secrets"].append(secret)
        
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
    
    def _is_duplicate(self, secret: Dict[str, Any], existing_secrets: List[Dict[str, Any]]) -> bool:
        """Check if secret is duplicate"""
        for existing in existing_secrets:
            if (existing["file"] == secret["file"] and
                existing["line"] == secret["line"] and
                existing["type"] == secret["type"]):
                return True
        return False
    
    def _get_recommendation(self, secret_type: str) -> str:
        """Get remediation recommendation for secret type"""
        recommendations = {
            "aws_access_key": "Rotate AWS credentials immediately and use AWS Secrets Manager or IAM roles",
            "aws_secret_key": "Rotate AWS credentials immediately and use AWS Secrets Manager or IAM roles",
            "github_token": "Revoke token immediately and use GitHub Actions secrets or encrypted secrets",
            "github_oauth": "Revoke OAuth token and regenerate with proper scoping",
            "slack_token": "Revoke and regenerate Slack token, use environment variables",
            "slack_webhook": "Rotate webhook URL and store in secure vault",
            "google_api_key": "Restrict API key and use Google Secret Manager",
            "stripe_api_key": "Roll Stripe API key immediately and use environment variables",
            "private_key": "Remove private key from code and use key management service",
            "jwt_token": "Invalidate JWT token and implement proper token management",
            "password_in_url": "Remove credentials from URL and use environment variables",
            "database_url": "Move connection string to environment variables or secrets manager",
            "generic_api_key": "Rotate API key and use secure configuration management",
            "generic_secret": "Move secret to environment variables or vault service"
        }
        
        return recommendations.get(
            secret_type,
            "Remove secret from code and use environment variables or secrets management service"
        )

    async def scan_git_history(
        self,
        repo_path: str,
        max_commits: int = 100
    ) -> Dict[str, Any]:
        """
        Scan git history for secrets.

        Args:
            repo_path: Path to git repository
            max_commits: Maximum number of commits to scan

        Returns:
            Results with secrets found in git history
        """
        import subprocess

        results = {
            "scanner": self.name,
            "scan_type": "git_history",
            "status": "completed",
            "secrets": [],
            "commits_scanned": 0,
            "summary": {
                "total_secrets": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }

        try:
            # Get list of commits
            cmd = ["git", "-C", repo_path, "log", f"--max-count={max_commits}", "--pretty=format:%H"]
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
            commits = output.decode().strip().split("\n")

            for commit in commits:
                if not commit:
                    continue

                results["commits_scanned"] += 1

                # Get diff for this commit
                cmd = ["git", "-C", repo_path, "show", commit, "--format="]
                diff_output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode(errors="ignore")

                # Scan diff content
                for secret_type, pattern_info in self.patterns.items():
                    pattern = pattern_info["pattern"]
                    matches = re.finditer(pattern, diff_output, re.IGNORECASE)

                    for match in matches:
                        # Create redacted version
                        matched_text = match.group(0)
                        if len(matched_text) > 20:
                            redacted = matched_text[:8] + "*" * (len(matched_text) - 12) + matched_text[-4:]
                        else:
                            redacted = "*" * len(matched_text)

                        secret = {
                            "type": secret_type,
                            "description": pattern_info["description"],
                            "severity": pattern_info["severity"],
                            "commit": commit,
                            "matched_text": redacted,
                            "recommendation": self._get_recommendation(secret_type),
                            "in_history": True
                        }

                        # Avoid duplicates
                        is_dup = any(
                            s["commit"] == secret["commit"] and s["type"] == secret["type"]
                            for s in results["secrets"]
                        )
                        if not is_dup:
                            results["secrets"].append(secret)

            # Update summary
            for secret in results["secrets"]:
                severity = secret.get("severity", "medium").lower()
                results["summary"][severity] = results["summary"].get(severity, 0) + 1

            results["summary"]["total_secrets"] = len(results["secrets"])

        except subprocess.CalledProcessError as e:
            results["status"] = "error"
            results["error"] = f"Git command failed: {e}"
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        return results

    def filter_false_positives(
        self,
        secrets: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter out likely false positives.

        Returns:
            Tuple of (true_positives, false_positives)
        """
        true_positives = []
        false_positives = []

        # Common false positive patterns
        fp_patterns = [
            r"example",
            r"sample",
            r"test",
            r"dummy",
            r"placeholder",
            r"your[-_]?key[-_]?here",
            r"xxx+",
            r"aaa+",
            r"123+",
            r"abc+",
            r"TODO",
            r"FIXME",
        ]

        fp_regex = re.compile("|".join(fp_patterns), re.IGNORECASE)

        for secret in secrets:
            line_content = secret.get("line_content", "").lower()
            file_path = secret.get("file", "").lower()

            # Check if in test file
            is_test_file = any(
                indicator in file_path
                for indicator in ["test", "spec", "mock", "fixture", "example", "sample"]
            )

            # Check for false positive patterns
            is_fp_pattern = fp_regex.search(line_content) is not None

            # Check if it's a placeholder
            is_placeholder = any(
                placeholder in line_content
                for placeholder in ["your_", "replace_", "change_me", "insert_"]
            )

            if is_test_file or is_fp_pattern or is_placeholder:
                secret["false_positive_reason"] = (
                    "test_file" if is_test_file else
                    "fp_pattern" if is_fp_pattern else
                    "placeholder"
                )
                false_positives.append(secret)
            else:
                true_positives.append(secret)

        return true_positives, false_positives

    def calculate_exposure_risk(self, secret: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate exposure risk score for a secret.

        Returns:
            Risk assessment with score and factors
        """
        risk_score = 0
        risk_factors = []

        # Severity factor
        severity_scores = {
            "critical": 40,
            "high": 30,
            "medium": 20,
            "low": 10
        }
        severity = secret.get("severity", "medium").lower()
        risk_score += severity_scores.get(severity, 20)
        risk_factors.append(f"Severity: {severity}")

        # File location factor
        file_path = secret.get("file", "").lower()
        if ".env" in file_path:
            risk_score += 20
            risk_factors.append("Found in .env file")
        elif "config" in file_path:
            risk_score += 15
            risk_factors.append("Found in config file")

        # Secret type factor
        high_risk_types = ["aws_access_key", "private_key", "stripe_api_key", "database_url"]
        if secret.get("type") in high_risk_types:
            risk_score += 20
            risk_factors.append("High-risk secret type")

        # In git history factor
        if secret.get("in_history"):
            risk_score += 10
            risk_factors.append("Found in git history")

        # Determine risk level
        if risk_score >= 80:
            risk_level = "critical"
        elif risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 40:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "score": risk_score,
            "level": risk_level,
            "factors": risk_factors
        }

    async def comprehensive_scan(
        self,
        target_path: str,
        include_git_history: bool = True,
        filter_fps: bool = True
    ) -> Dict[str, Any]:
        """
        Run comprehensive secret scan with all features.

        Args:
            target_path: Path to scan
            include_git_history: Whether to scan git history
            filter_fps: Whether to filter false positives

        Returns:
            Comprehensive scan results
        """
        import time
        start_time = time.time()

        # Run standard scan
        results = await self.scan(target_path)

        # Scan git history if requested
        if include_git_history:
            git_results = await self.scan_git_history(target_path)
            results["git_history"] = {
                "commits_scanned": git_results["commits_scanned"],
                "secrets_found": len(git_results["secrets"])
            }
            results["secrets"].extend(git_results["secrets"])

        # Filter false positives if requested
        if filter_fps:
            true_positives, false_positives = self.filter_false_positives(results["secrets"])
            results["secrets"] = true_positives
            results["false_positives"] = len(false_positives)
            results["summary"]["total_secrets"] = len(true_positives)

        # Calculate risk scores
        for secret in results["secrets"]:
            secret["risk"] = self.calculate_exposure_risk(secret)

        # Sort by risk score
        results["secrets"].sort(
            key=lambda s: s.get("risk", {}).get("score", 0),
            reverse=True
        )

        results["scan_time_ms"] = int((time.time() - start_time) * 1000)

        return results

    def add_custom_pattern(
        self,
        name: str,
        pattern: str,
        description: str,
        severity: str = "high"
    ) -> None:
        """
        Add a custom regex pattern for secret detection.

        Args:
            name: Pattern name
            pattern: Regex pattern
            description: Pattern description
            severity: Severity level
        """
        self.patterns[name] = {
            "pattern": pattern,
            "description": description,
            "severity": severity
        }
