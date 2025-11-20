"""
Infrastructure as Code (IaC) Scanner
Scans Terraform, CloudFormation, Kubernetes manifests for security issues
"""

import asyncio
import json
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
import re


class IaCScanner:
    """Infrastructure as Code security scanner"""
    
    def __init__(self):
        self.name = "IaC Scanner"
        
    async def scan(
        self,
        target_path: str,
        scan_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Scan IaC files for security misconfigurations
        
        Args:
            target_path: Path to IaC files
            scan_options: Optional configuration
            
        Returns:
            Scan results with issues found
        """
        scan_options = scan_options or {}
        
        results = {
            "scanner": self.name,
            "status": "completed",
            "issues": [],
            "files_scanned": 0,
            "summary": {
                "total_issues": 0,
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
                await self._scan_directory(path, results)
            
            # Update summary
            for issue in results["issues"]:
                severity = issue.get("severity", "medium").lower()
                results["summary"][severity] = results["summary"].get(severity, 0) + 1
                
                issue_type = issue.get("type")
                results["summary"]["by_type"][issue_type] = \
                    results["summary"]["by_type"].get(issue_type, 0) + 1
            
            results["summary"]["total_issues"] = len(results["issues"])
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    async def _scan_directory(self, directory: Path, results: Dict[str, Any]):
        """Scan directory for IaC files"""
        
        iac_patterns = {
            "*.tf": self._scan_terraform,
            "*.tfvars": self._scan_terraform_vars,
            "*.yaml": self._scan_kubernetes,
            "*.yml": self._scan_kubernetes,
            "*.json": self._scan_cloudformation
        }
        
        for pattern, scanner_func in iac_patterns.items():
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    await self._scan_file(file_path, results)
    
    async def _scan_file(self, file_path: Path, results: Dict[str, Any]):
        """Scan individual IaC file"""
        
        results["files_scanned"] += 1
        
        try:
            if file_path.suffix == ".tf":
                await self._scan_terraform(file_path, results)
            elif file_path.suffix == ".tfvars":
                await self._scan_terraform_vars(file_path, results)
            elif file_path.suffix in [".yaml", ".yml"]:
                await self._scan_kubernetes(file_path, results)
            elif file_path.suffix == ".json":
                content = json.loads(file_path.read_text())
                if "AWSTemplateFormatVersion" in content:
                    await self._scan_cloudformation(file_path, results)
        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
    
    async def _scan_terraform(self, file_path: Path, results: Dict[str, Any]):
        """Scan Terraform files for security issues"""
        
        try:
            content = file_path.read_text()
            lines = content.splitlines()
            
            # Check for common Terraform security issues
            
            # 1. Hardcoded credentials
            credential_patterns = [
                r'access_key\s*=\s*["\']AKIA[A-Z0-9]+["\']',
                r'secret_key\s*=\s*["\'][A-Za-z0-9/+=]+["\']',
                r'password\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ]
            
            for idx, line in enumerate(lines, 1):
                for pattern in credential_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        results["issues"].append({
                            "type": "hardcoded_credentials",
                            "severity": "critical",
                            "file": str(file_path),
                            "line": idx,
                            "description": "Hardcoded credentials found in Terraform",
                            "recommendation": "Use variables or AWS Secrets Manager",
                            "code": line.strip()
                        })
            
            # 2. Public S3 buckets
            if re.search(r'resource\s+"aws_s3_bucket"', content):
                if re.search(r'acl\s*=\s*["\']public-read["\']', content) or \
                   re.search(r'acl\s*=\s*["\']public-read-write["\']', content):
                    results["issues"].append({
                        "type": "public_s3_bucket",
                        "severity": "critical",
                        "file": str(file_path),
                        "description": "S3 bucket with public ACL",
                        "recommendation": "Restrict S3 bucket access, use private ACL",
                        "resource": "aws_s3_bucket"
                    })
            
            # 3. Unencrypted storage
            if re.search(r'resource\s+"aws_db_instance"', content):
                if not re.search(r'storage_encrypted\s*=\s*true', content):
                    results["issues"].append({
                        "type": "unencrypted_storage",
                        "severity": "high",
                        "file": str(file_path),
                        "description": "RDS instance without encryption",
                        "recommendation": "Enable storage_encrypted = true",
                        "resource": "aws_db_instance"
                    })
            
            # 4. Security group with open ports
            if re.search(r'resource\s+"aws_security_group"', content):
                if re.search(r'cidr_blocks\s*=\s*\[["\']0\.0\.0\.0/0["\']', content):
                    results["issues"].append({
                        "type": "open_security_group",
                        "severity": "high",
                        "file": str(file_path),
                        "description": "Security group allowing traffic from 0.0.0.0/0",
                        "recommendation": "Restrict CIDR blocks to specific IPs",
                        "resource": "aws_security_group"
                    })
            
            # 5. Missing encryption for EBS
            if re.search(r'resource\s+"aws_ebs_volume"', content):
                if not re.search(r'encrypted\s*=\s*true', content):
                    results["issues"].append({
                        "type": "unencrypted_ebs",
                        "severity": "high",
                        "file": str(file_path),
                        "description": "EBS volume without encryption",
                        "recommendation": "Enable encrypted = true",
                        "resource": "aws_ebs_volume"
                    })
            
            # 6. IAM policy with wildcards
            if re.search(r'"Effect":\s*"Allow"', content):
                if re.search(r'"Action":\s*"\*"', content) or \
                   re.search(r'"Resource":\s*"\*"', content):
                    results["issues"].append({
                        "type": "overly_permissive_iam",
                        "severity": "high",
                        "file": str(file_path),
                        "description": "IAM policy with wildcard permissions",
                        "recommendation": "Use principle of least privilege",
                        "resource": "iam_policy"
                    })
            
            # 7. Missing MFA for IAM users
            if re.search(r'resource\s+"aws_iam_user"', content):
                results["issues"].append({
                    "type": "missing_mfa",
                    "severity": "medium",
                    "file": str(file_path),
                    "description": "IAM user without MFA enforcement",
                    "recommendation": "Enable MFA for all IAM users",
                    "resource": "aws_iam_user"
                })
            
        except Exception as e:
            print(f"Error scanning Terraform file: {e}")
    
    async def _scan_terraform_vars(self, file_path: Path, results: Dict[str, Any]):
        """Scan Terraform variable files"""
        
        try:
            content = file_path.read_text()
            
            # Check for secrets in tfvars
            if re.search(r'(password|secret|key|token)\s*=', content, re.IGNORECASE):
                results["issues"].append({
                    "type": "secrets_in_tfvars",
                    "severity": "high",
                    "file": str(file_path),
                    "description": "Potential secrets in tfvars file",
                    "recommendation": "Use environment variables or vault"
                })
        
        except Exception as e:
            print(f"Error scanning tfvars: {e}")
    
    async def _scan_kubernetes(self, file_path: Path, results: Dict[str, Any]):
        """Scan Kubernetes manifests for security issues"""
        
        try:
            content = file_path.read_text()
            docs = yaml.safe_load_all(content)
            
            for doc in docs:
                if not doc or not isinstance(doc, dict):
                    continue
                
                kind = doc.get("kind", "")
                
                if kind == "Pod" or kind == "Deployment":
                    await self._check_pod_security(doc, file_path, results)
                
                elif kind == "Service":
                    await self._check_service_security(doc, file_path, results)
                
                elif kind == "NetworkPolicy":
                    await self._check_network_policy(doc, file_path, results)
        
        except Exception as e:
            print(f"Error scanning Kubernetes manifest: {e}")
    
    async def _check_pod_security(self, doc: Dict, file_path: Path, results: Dict[str, Any]):
        """Check Pod/Deployment security"""
        
        spec = doc.get("spec", {})
        if "template" in spec:
            spec = spec["template"]["spec"]
        
        # Check for privileged containers
        containers = spec.get("containers", [])
        for container in containers:
            security_context = container.get("securityContext", {})
            
            if security_context.get("privileged"):
                results["issues"].append({
                    "type": "privileged_container",
                    "severity": "critical",
                    "file": str(file_path),
                    "description": "Container running in privileged mode",
                    "recommendation": "Remove privileged: true unless absolutely necessary",
                    "resource": container.get("name")
                })
            
            if not security_context.get("runAsNonRoot"):
                results["issues"].append({
                    "type": "container_as_root",
                    "severity": "high",
                    "file": str(file_path),
                    "description": "Container may run as root",
                    "recommendation": "Set runAsNonRoot: true",
                    "resource": container.get("name")
                })
            
            if not security_context.get("readOnlyRootFilesystem"):
                results["issues"].append({
                    "type": "writable_filesystem",
                    "severity": "medium",
                    "file": str(file_path),
                    "description": "Container filesystem is writable",
                    "recommendation": "Set readOnlyRootFilesystem: true",
                    "resource": container.get("name")
                })
        
        # Check for hostNetwork
        if spec.get("hostNetwork"):
            results["issues"].append({
                "type": "host_network",
                "severity": "high",
                "file": str(file_path),
                "description": "Pod using host network",
                "recommendation": "Avoid hostNetwork unless necessary"
            })
        
        # Check for hostPID/hostIPC
        if spec.get("hostPID") or spec.get("hostIPC"):
            results["issues"].append({
                "type": "host_namespace",
                "severity": "high",
                "file": str(file_path),
                "description": "Pod using host PID/IPC namespace",
                "recommendation": "Avoid hostPID and hostIPC"
            })
    
    async def _check_service_security(self, doc: Dict, file_path: Path, results: Dict[str, Any]):
        """Check Service security"""
        
        spec = doc.get("spec", {})
        
        # Check for LoadBalancer without source ranges
        if spec.get("type") == "LoadBalancer":
            if not spec.get("loadBalancerSourceRanges"):
                results["issues"].append({
                    "type": "public_load_balancer",
                    "severity": "high",
                    "file": str(file_path),
                    "description": "LoadBalancer without source IP restrictions",
                    "recommendation": "Add loadBalancerSourceRanges to restrict access"
                })
    
    async def _check_network_policy(self, doc: Dict, file_path: Path, results: Dict[str, Any]):
        """Check NetworkPolicy configuration"""
        
        spec = doc.get("spec", {})
        
        # Check for overly permissive policies
        ingress = spec.get("ingress", [])
        if not ingress:
            results["issues"].append({
                "type": "no_network_policy",
                "severity": "medium",
                "file": str(file_path),
                "description": "NetworkPolicy with no ingress rules",
                "recommendation": "Define explicit ingress rules"
            })
    
    async def _scan_cloudformation(self, file_path: Path, results: Dict[str, Any]):
        """Scan CloudFormation templates"""
        
        try:
            content = json.loads(file_path.read_text())
            resources = content.get("Resources", {})
            
            for resource_name, resource in resources.items():
                resource_type = resource.get("Type", "")
                properties = resource.get("Properties", {})
                
                # Check S3 buckets
                if resource_type == "AWS::S3::Bucket":
                    if properties.get("AccessControl") in ["PublicRead", "PublicReadWrite"]:
                        results["issues"].append({
                            "type": "public_s3_bucket",
                            "severity": "critical",
                            "file": str(file_path),
                            "description": f"Public S3 bucket: {resource_name}",
                            "recommendation": "Use private access control",
                            "resource": resource_name
                        })
                
                # Check RDS encryption
                if resource_type == "AWS::RDS::DBInstance":
                    if not properties.get("StorageEncrypted"):
                        results["issues"].append({
                            "type": "unencrypted_rds",
                            "severity": "high",
                            "file": str(file_path),
                            "description": f"Unencrypted RDS instance: {resource_name}",
                            "recommendation": "Enable StorageEncrypted",
                            "resource": resource_name
                        })
        
        except Exception as e:
            print(f"Error scanning CloudFormation: {e}")
