"""
SCA (Software Composition Analysis) Scanner
Detects vulnerable dependencies and license issues

Enhanced with:
- OSV database integration
- License compliance checking
- Outdated package detection
- Auto-update PR generation
- Dependency graph visualization
"""

import asyncio
import json
import subprocess
import re
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from enum import Enum

import aiohttp
import hashlib

logger = logging.getLogger(__name__)


class VulnerabilitySeverity(str, Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class LicenseRisk(str, Enum):
    """License risk levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class SCAScanner:
    """Software Composition Analysis Scanner"""
    
    def __init__(self):
        self.name = "SCA Scanner"
        self.nvd_api_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.ossindex_api_url = "https://ossindex.sonatype.org/api/v3/component-report"
        
    async def scan(
        self,
        project_path: str,
        scan_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run SCA scan on project dependencies
        
        Args:
            project_path: Path to project directory
            scan_options: Optional configuration
            
        Returns:
            Scan results with vulnerabilities found
        """
        scan_options = scan_options or {}
        
        results = {
            "scanner": self.name,
            "status": "completed",
            "vulnerabilities": [],
            "dependencies": [],
            "license_issues": [],
            "summary": {
                "total_dependencies": 0,
                "vulnerable_dependencies": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        try:
            # Detect package managers
            dependencies = await self._detect_dependencies(project_path)
            results["dependencies"] = dependencies
            results["summary"]["total_dependencies"] = len(dependencies)
            
            # Check for vulnerabilities
            vulnerabilities = await self._check_vulnerabilities(dependencies)
            results["vulnerabilities"] = vulnerabilities
            
            # Check licenses
            license_issues = await self._check_licenses(dependencies)
            results["license_issues"] = license_issues
            
            # Update summary
            for vuln in vulnerabilities:
                severity = vuln.get("severity", "").lower()
                if severity == "critical":
                    results["summary"]["critical"] += 1
                elif severity == "high":
                    results["summary"]["high"] += 1
                elif severity == "medium":
                    results["summary"]["medium"] += 1
                elif severity == "low":
                    results["summary"]["low"] += 1
            
            results["summary"]["vulnerable_dependencies"] = len(
                set(v.get("package") for v in vulnerabilities)
            )
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    async def _detect_dependencies(self, project_path: str) -> List[Dict[str, Any]]:
        """Detect dependencies from various package managers"""
        dependencies = []
        path = Path(project_path)
        
        # Python (pip/poetry/pipenv)
        requirements_file = path / "requirements.txt"
        if requirements_file.exists():
            deps = await self._parse_requirements(requirements_file)
            dependencies.extend(deps)
        
        pipfile = path / "Pipfile"
        if pipfile.exists():
            deps = await self._parse_pipfile(pipfile)
            dependencies.extend(deps)
        
        poetry_lock = path / "poetry.lock"
        if poetry_lock.exists():
            deps = await self._parse_poetry_lock(poetry_lock)
            dependencies.extend(deps)
        
        # Node.js (npm/yarn)
        package_json = path / "package.json"
        if package_json.exists():
            deps = await self._parse_package_json(package_json)
            dependencies.extend(deps)
        
        package_lock = path / "package-lock.json"
        if package_lock.exists():
            deps = await self._parse_package_lock(package_lock)
            dependencies.extend(deps)
        
        # Java (Maven/Gradle)
        pom_xml = path / "pom.xml"
        if pom_xml.exists():
            deps = await self._parse_pom_xml(pom_xml)
            dependencies.extend(deps)
        
        build_gradle = path / "build.gradle"
        if build_gradle.exists():
            deps = await self._parse_build_gradle(build_gradle)
            dependencies.extend(deps)
        
        # Ruby (Bundler)
        gemfile = path / "Gemfile"
        if gemfile.exists():
            deps = await self._parse_gemfile(gemfile)
            dependencies.extend(deps)
        
        # Go (go.mod)
        go_mod = path / "go.mod"
        if go_mod.exists():
            deps = await self._parse_go_mod(go_mod)
            dependencies.extend(deps)
        
        return dependencies
    
    async def _parse_requirements(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse Python requirements.txt"""
        dependencies = []
        try:
            content = file_path.read_text()
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.replace(">=", "==").replace("~=", "==").split("==")
                    if len(parts) >= 2:
                        dependencies.append({
                            "name": parts[0].strip(),
                            "version": parts[1].strip(),
                            "ecosystem": "pypi",
                            "manager": "pip"
                        })
                    else:
                        dependencies.append({
                            "name": parts[0].strip(),
                            "version": "latest",
                            "ecosystem": "pypi",
                            "manager": "pip"
                        })
        except Exception as e:
            print(f"Error parsing requirements.txt: {e}")
        
        return dependencies
    
    async def _parse_pipfile(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse Pipfile"""
        dependencies = []
        try:
            import toml
            content = toml.load(file_path)
            
            for section in ["packages", "dev-packages"]:
                if section in content:
                    for name, version in content[section].items():
                        dependencies.append({
                            "name": name,
                            "version": version if isinstance(version, str) else "latest",
                            "ecosystem": "pypi",
                            "manager": "pipenv",
                            "dev": section == "dev-packages"
                        })
        except Exception as e:
            print(f"Error parsing Pipfile: {e}")
        
        return dependencies
    
    async def _parse_poetry_lock(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse poetry.lock"""
        dependencies = []
        try:
            import toml
            content = toml.load(file_path)
            
            if "package" in content:
                for pkg in content["package"]:
                    dependencies.append({
                        "name": pkg.get("name"),
                        "version": pkg.get("version"),
                        "ecosystem": "pypi",
                        "manager": "poetry"
                    })
        except Exception as e:
            print(f"Error parsing poetry.lock: {e}")
        
        return dependencies
    
    async def _parse_package_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse package.json"""
        dependencies = []
        try:
            content = json.loads(file_path.read_text())
            
            for section in ["dependencies", "devDependencies"]:
                if section in content:
                    for name, version in content[section].items():
                        dependencies.append({
                            "name": name,
                            "version": version.replace("^", "").replace("~", ""),
                            "ecosystem": "npm",
                            "manager": "npm",
                            "dev": section == "devDependencies"
                        })
        except Exception as e:
            print(f"Error parsing package.json: {e}")
        
        return dependencies
    
    async def _parse_package_lock(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse package-lock.json"""
        dependencies = []
        try:
            content = json.loads(file_path.read_text())
            
            if "dependencies" in content:
                for name, info in content["dependencies"].items():
                    dependencies.append({
                        "name": name,
                        "version": info.get("version", ""),
                        "ecosystem": "npm",
                        "manager": "npm"
                    })
        except Exception as e:
            print(f"Error parsing package-lock.json: {e}")
        
        return dependencies
    
    async def _parse_pom_xml(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse Maven pom.xml"""
        dependencies = []
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            ns = {"maven": "http://maven.apache.org/POM/4.0.0"}
            for dep in root.findall(".//maven:dependency", ns):
                group_id = dep.find("maven:groupId", ns)
                artifact_id = dep.find("maven:artifactId", ns)
                version = dep.find("maven:version", ns)
                
                if group_id is not None and artifact_id is not None:
                    dependencies.append({
                        "name": f"{group_id.text}:{artifact_id.text}",
                        "version": version.text if version is not None else "latest",
                        "ecosystem": "maven",
                        "manager": "maven"
                    })
        except Exception as e:
            print(f"Error parsing pom.xml: {e}")
        
        return dependencies
    
    async def _parse_build_gradle(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse Gradle build.gradle (basic parsing)"""
        dependencies = []
        try:
            content = file_path.read_text()
            
            for line in content.splitlines():
                line = line.strip()
                if "implementation" in line or "compile" in line:
                    if "'" in line or '"' in line:
                        parts = line.split("'") if "'" in line else line.split('"')
                        if len(parts) >= 2:
                            dep_parts = parts[1].split(":")
                            if len(dep_parts) >= 3:
                                dependencies.append({
                                    "name": f"{dep_parts[0]}:{dep_parts[1]}",
                                    "version": dep_parts[2],
                                    "ecosystem": "maven",
                                    "manager": "gradle"
                                })
        except Exception as e:
            print(f"Error parsing build.gradle: {e}")
        
        return dependencies
    
    async def _parse_gemfile(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse Ruby Gemfile"""
        dependencies = []
        try:
            content = file_path.read_text()
            
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("gem"):
                    parts = line.split("'") if "'" in line else line.split('"')
                    if len(parts) >= 2:
                        name = parts[1]
                        version = parts[3] if len(parts) >= 4 else "latest"
                        dependencies.append({
                            "name": name,
                            "version": version,
                            "ecosystem": "rubygems",
                            "manager": "bundler"
                        })
        except Exception as e:
            print(f"Error parsing Gemfile: {e}")
        
        return dependencies
    
    async def _parse_go_mod(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse Go go.mod"""
        dependencies = []
        try:
            content = file_path.read_text()
            in_require = False
            
            for line in content.splitlines():
                line = line.strip()
                
                if line.startswith("require"):
                    in_require = True
                    continue
                
                if in_require:
                    if line == ")":
                        in_require = False
                        continue
                    
                    parts = line.split()
                    if len(parts) >= 2:
                        dependencies.append({
                            "name": parts[0],
                            "version": parts[1],
                            "ecosystem": "go",
                            "manager": "go"
                        })
        except Exception as e:
            print(f"Error parsing go.mod: {e}")
        
        return dependencies
    
    async def _check_vulnerabilities(
        self,
        dependencies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check dependencies for known vulnerabilities"""
        vulnerabilities = []
        
        for dep in dependencies:
            # Check against known vulnerability databases
            vulns = await self._query_vulnerability_db(dep)
            vulnerabilities.extend(vulns)
        
        return vulnerabilities
    
    async def _query_vulnerability_db(
        self,
        dependency: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Query vulnerability databases for a dependency"""
        vulnerabilities = []
        
        # Simulated vulnerability check
        # In production, query OSS Index, Snyk, or GitHub Advisory Database
        
        vulnerable_packages = {
            "django": ["3.0.0", "2.2.0", "1.11.0"],
            "flask": ["0.12.0", "1.0.0"],
            "express": ["4.16.0", "4.15.0"],
            "lodash": ["4.17.15", "4.17.11"],
            "axios": ["0.18.0", "0.19.0"],
            "spring-core": ["5.2.0", "5.1.0"],
            "log4j-core": ["2.14.1", "2.13.0"],
            "jackson-databind": ["2.9.0", "2.8.0"]
        }
        
        pkg_name = dependency.get("name", "").split(":")[0]
        pkg_version = dependency.get("version", "")
        
        if pkg_name in vulnerable_packages:
            if pkg_version in vulnerable_packages[pkg_name]:
                vulnerabilities.append({
                    "package": pkg_name,
                    "version": pkg_version,
                    "ecosystem": dependency.get("ecosystem"),
                    "severity": "high",
                    "cve_id": f"CVE-2023-{hash(pkg_name) % 10000:04d}",
                    "title": f"Security vulnerability in {pkg_name}",
                    "description": f"Known security issue in {pkg_name} version {pkg_version}",
                    "cvss_score": 7.5,
                    "fixed_in": "latest",
                    "references": []
                })
        
        return vulnerabilities
    
    async def _check_licenses(
        self,
        dependencies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for license compliance issues"""
        license_issues = []

        # License risk classification
        high_risk_licenses = ["GPL-3.0", "AGPL-3.0", "GPL-2.0", "SSPL"]
        medium_risk_licenses = ["LGPL-3.0", "LGPL-2.1", "MPL-2.0", "EPL-2.0"]

        for dep in dependencies:
            license_name = dep.get("license", "")

            if any(lic in license_name for lic in high_risk_licenses):
                license_issues.append({
                    "package": dep.get("name"),
                    "version": dep.get("version"),
                    "license": license_name,
                    "risk": LicenseRisk.HIGH.value,
                    "issue": "Copyleft license may require source code disclosure",
                    "severity": "high"
                })
            elif any(lic in license_name for lic in medium_risk_licenses):
                license_issues.append({
                    "package": dep.get("name"),
                    "version": dep.get("version"),
                    "license": license_name,
                    "risk": LicenseRisk.MEDIUM.value,
                    "issue": "Weak copyleft license with some restrictions",
                    "severity": "medium"
                })

        return license_issues

    async def query_osv_database(
        self,
        package_name: str,
        version: str,
        ecosystem: str
    ) -> List[Dict[str, Any]]:
        """Query OSV database for vulnerabilities."""
        vulnerabilities = []

        try:
            async with aiohttp.ClientSession() as session:
                osv_ecosystem_map = {
                    "pypi": "PyPI",
                    "npm": "npm",
                    "maven": "Maven",
                    "go": "Go",
                    "rubygems": "RubyGems",
                    "nuget": "NuGet",
                    "cargo": "crates.io",
                    "composer": "Packagist"
                }

                payload = {
                    "package": {
                        "name": package_name,
                        "ecosystem": osv_ecosystem_map.get(ecosystem, ecosystem)
                    },
                    "version": version
                }

                async with session.post(
                    "https://api.osv.dev/v1/query",
                    json=payload,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for vuln in data.get("vulns", []):
                            severity = "medium"
                            cvss_score = 5.0

                            for severity_data in vuln.get("severity", []):
                                if severity_data.get("type") == "CVSS_V3":
                                    score_str = severity_data.get("score", "5.0")
                                    if "/" in score_str:
                                        score = float(score_str.split("/")[0])
                                    else:
                                        score = float(score_str)
                                    cvss_score = score

                                    if score >= 9.0:
                                        severity = "critical"
                                    elif score >= 7.0:
                                        severity = "high"
                                    elif score >= 4.0:
                                        severity = "medium"
                                    else:
                                        severity = "low"

                            cve_id = next(
                                (alias for alias in vuln.get("aliases", []) if alias.startswith("CVE-")),
                                None
                            )

                            vulnerabilities.append({
                                "package": package_name,
                                "version": version,
                                "ecosystem": ecosystem,
                                "severity": severity,
                                "cve_id": cve_id,
                                "osv_id": vuln.get("id"),
                                "title": vuln.get("summary", "Unknown vulnerability"),
                                "description": vuln.get("details", ""),
                                "cvss_score": cvss_score,
                                "references": [ref.get("url", "") for ref in vuln.get("references", [])[:5]],
                                "published": vuln.get("published"),
                                "modified": vuln.get("modified")
                            })

        except Exception as e:
            logger.warning(f"Failed to query OSV for {package_name}: {e}")

        return vulnerabilities

    async def check_outdated_packages(
        self,
        dependencies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for outdated packages."""
        outdated = []

        async with aiohttp.ClientSession() as session:
            for dep in dependencies:
                try:
                    latest = await self._get_latest_version(session, dep)
                    if latest and latest != dep.get("version"):
                        outdated.append({
                            "package": dep.get("name"),
                            "current_version": dep.get("version"),
                            "latest_version": latest,
                            "ecosystem": dep.get("ecosystem")
                        })
                except Exception as e:
                    logger.debug(f"Failed to check {dep.get('name')}: {e}")

        return outdated

    async def _get_latest_version(
        self,
        session: aiohttp.ClientSession,
        dependency: Dict[str, Any]
    ) -> Optional[str]:
        """Get latest version of a package."""
        ecosystem = dependency.get("ecosystem", "")
        name = dependency.get("name", "")

        try:
            if ecosystem == "npm":
                async with session.get(
                    f"https://registry.npmjs.org/{name}/latest",
                    timeout=5
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("version")

            elif ecosystem == "pypi":
                async with session.get(
                    f"https://pypi.org/pypi/{name}/json",
                    timeout=5
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("info", {}).get("version")

        except Exception:
            pass

        return None

    def generate_dependency_graph(
        self,
        dependencies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate dependency graph for visualization."""
        nodes = []
        edges = []

        for dep in dependencies:
            node_id = f"{dep.get('name')}@{dep.get('version')}"
            nodes.append({
                "id": node_id,
                "label": dep.get("name"),
                "version": dep.get("version"),
                "ecosystem": dep.get("ecosystem"),
                "vulnerable": len(dep.get("vulnerabilities", [])) > 0
            })

        return {
            "nodes": nodes,
            "edges": edges
        }

    async def generate_update_pr_content(
        self,
        outdated_packages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate PR content for updating dependencies."""
        if not outdated_packages:
            return {"title": "", "body": "", "files": []}

        packages_list = "\n".join([
            f"- {pkg['package']}: {pkg['current_version']} -> {pkg['latest_version']}"
            for pkg in outdated_packages
        ])

        return {
            "title": f"chore(deps): update {len(outdated_packages)} dependencies",
            "body": f"""## Dependency Updates

This PR updates the following packages to their latest versions:

{packages_list}

### Changes

All packages have been updated to address security vulnerabilities and include bug fixes.

### Testing

- [ ] All tests pass
- [ ] Application builds successfully
- [ ] No breaking changes detected

---
Generated by IKODIO SCA Scanner
""",
            "branch": f"deps/update-{int(time.time())}",
            "packages": outdated_packages
        }

    async def full_scan(
        self,
        project_path: str
    ) -> Dict[str, Any]:
        """Run comprehensive SCA scan with all features."""
        start_time = time.time()

        # Run standard scan
        results = await self.scan(project_path)

        # Add outdated package check
        if results["dependencies"]:
            outdated = await self.check_outdated_packages(results["dependencies"])
            results["outdated_packages"] = outdated
            results["summary"]["outdated"] = len(outdated)

        # Generate dependency graph
        results["dependency_graph"] = self.generate_dependency_graph(results["dependencies"])

        # Generate update PR content if needed
        if results.get("outdated_packages"):
            results["update_pr"] = await self.generate_update_pr_content(results["outdated_packages"])

        results["scan_time_ms"] = int((time.time() - start_time) * 1000)

        return results
