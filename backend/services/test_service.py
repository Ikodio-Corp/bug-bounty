"""
Unit tests service
"""

from typing import Dict, List, Optional
import subprocess
import json
import os


class TestService:
    """Service for running tests"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.backend_path = os.path.join(project_root, "backend")
        self.frontend_path = os.path.join(project_root, "frontend")
    
    def run_backend_tests(
        self,
        path: Optional[str] = None,
        coverage: bool = False
    ) -> Dict:
        """Run backend pytest tests"""
        cmd = ["pytest"]
        
        if path:
            cmd.append(path)
        else:
            cmd.append(os.path.join(self.backend_path, "tests"))
        
        if coverage:
            cmd.extend(["--cov=.", "--cov-report=json", "--cov-report=term"])
        
        cmd.extend(["-v", "--tb=short"])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "errors": "Test execution timed out after 5 minutes",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "errors": str(e),
                "exit_code": -1
            }
    
    def run_frontend_tests(
        self,
        path: Optional[str] = None,
        coverage: bool = False
    ) -> Dict:
        """Run frontend Jest tests"""
        cmd = ["npm", "test", "--", "--passWithNoTests"]
        
        if path:
            cmd.append(path)
        
        if coverage:
            cmd.append("--coverage")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.frontend_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "errors": "Test execution timed out after 5 minutes",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "errors": str(e),
                "exit_code": -1
            }
    
    def run_e2e_tests(self) -> Dict:
        """Run end-to-end tests with Playwright"""
        cmd = ["npx", "playwright", "test"]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.frontend_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "errors": "E2E tests timed out after 10 minutes",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "errors": str(e),
                "exit_code": -1
            }
    
    def get_coverage_summary(self) -> Dict:
        """Get test coverage summary"""
        coverage_file = os.path.join(self.backend_path, "coverage.json")
        
        if not os.path.exists(coverage_file):
            return {
                "exists": False,
                "message": "No coverage data found. Run tests with coverage flag first."
            }
        
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            totals = coverage_data.get("totals", {})
            
            return {
                "exists": True,
                "line_coverage": totals.get("percent_covered", 0),
                "lines_covered": totals.get("covered_lines", 0),
                "lines_total": totals.get("num_statements", 0),
                "branch_coverage": totals.get("percent_covered_display", "0%")
            }
        except Exception as e:
            return {
                "exists": False,
                "message": f"Error reading coverage data: {str(e)}"
            }
    
    def lint_backend(self) -> Dict:
        """Run backend linting with flake8"""
        cmd = ["flake8", ".", "--max-line-length=120", "--exclude=venv,migrations"]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "issues_found": len(result.stdout.splitlines()) if result.stdout else 0
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "errors": str(e),
                "issues_found": 0
            }
    
    def lint_frontend(self) -> Dict:
        """Run frontend linting with ESLint"""
        cmd = ["npm", "run", "lint"]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.frontend_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "errors": str(e)
            }
    
    def type_check_frontend(self) -> Dict:
        """Run TypeScript type checking"""
        cmd = ["npm", "run", "type-check"]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.frontend_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "errors": str(e)
            }
