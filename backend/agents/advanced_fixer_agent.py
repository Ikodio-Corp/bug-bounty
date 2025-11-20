"""
Advanced Fixer Agent - Advanced pattern detection and auto-fix generation
"""

from typing import Dict, Any, List, Optional, Tuple
import re
import ast
import openai
from core.config import settings


class AdvancedFixerAgent:
    """Advanced AI agent for vulnerability pattern detection and auto-fix generation"""
    
    # Supported programming languages
    SUPPORTED_LANGUAGES = [
        "python", "javascript", "typescript", "java", "go", 
        "php", "ruby", "c", "cpp", "csharp", "rust"
    ]
    
    # Advanced vulnerability patterns
    VULNERABILITY_PATTERNS = {
        "sqli": {
            "patterns": [
                r"execute\s*\(\s*['\"].*?\+.*?['\"]",
                r"cursor\.execute\s*\(\s*['\"].*?%.*?['\"].*?%",
                r"query\s*=.*?\+.*?request\.",
                r"sql\s*=.*?f['\"].*?\{.*?\}",
            ],
            "severity": "critical",
            "cwe": "CWE-89",
            "languages": ["python", "php", "java", "csharp"]
        },
        "xss": {
            "patterns": [
                r"innerHTML\s*=\s*[^']",
                r"document\.write\s*\(",
                r"dangerouslySetInnerHTML",
                r"<script>.*?</script>",
                r"eval\s*\(\s*.*?request",
            ],
            "severity": "high",
            "cwe": "CWE-79",
            "languages": ["javascript", "typescript", "php", "java"]
        },
        "rce": {
            "patterns": [
                r"eval\s*\(",
                r"exec\s*\(",
                r"system\s*\(",
                r"shell_exec\s*\(",
                r"os\.system\s*\(",
                r"subprocess\.\w+\s*\(.*?shell\s*=\s*True",
            ],
            "severity": "critical",
            "cwe": "CWE-78",
            "languages": ["python", "php", "javascript", "ruby", "java"]
        },
        "path_traversal": {
            "patterns": [
                r"open\s*\(.*?request\.",
                r"file_get_contents\s*\(.*?\$_",
                r"readFile\s*\(.*?req\.",
                r"\.\.\/",
            ],
            "severity": "high",
            "cwe": "CWE-22",
            "languages": ["python", "php", "javascript", "java", "go"]
        },
        "insecure_deserialization": {
            "patterns": [
                r"pickle\.loads\s*\(",
                r"yaml\.load\s*\(.*?Loader\s*=\s*yaml\.Loader",
                r"unserialize\s*\(",
                r"ObjectInputStream",
            ],
            "severity": "critical",
            "cwe": "CWE-502",
            "languages": ["python", "php", "java"]
        },
        "weak_crypto": {
            "patterns": [
                r"md5\s*\(",
                r"sha1\s*\(",
                r"DES\s*\(",
                r"ECB\s*mode",
                r"Random\s*\(\)",
            ],
            "severity": "medium",
            "cwe": "CWE-327",
            "languages": ["python", "java", "csharp", "javascript"]
        },
        "hardcoded_secrets": {
            "patterns": [
                r"password\s*=\s*['\"][^'\"]+['\"]",
                r"api_key\s*=\s*['\"][^'\"]+['\"]",
                r"secret\s*=\s*['\"][^'\"]+['\"]",
                r"token\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]",
            ],
            "severity": "high",
            "cwe": "CWE-798",
            "languages": ["python", "javascript", "java", "go", "ruby"]
        },
        "xxe": {
            "patterns": [
                r"XMLParser.*?resolve_entities\s*=\s*True",
                r"DocumentBuilder.*?setFeature.*?false",
                r"simplexml_load",
                r"DOMDocument.*?load",
            ],
            "severity": "high",
            "cwe": "CWE-611",
            "languages": ["python", "java", "php"]
        },
        "csrf": {
            "patterns": [
                r"@app\.route.*?methods\s*=\s*\[.*?POST.*?\](?!.*csrf)",
                r"<form.*?method=['\"]post['\"](?!.*csrf)",
                r"fetch\s*\(.*?method:\s*['\"]POST['\"](?!.*csrf)",
            ],
            "severity": "medium",
            "cwe": "CWE-352",
            "languages": ["python", "javascript", "php", "java"]
        },
        "ssrf": {
            "patterns": [
                r"requests\.get\s*\(.*?request\.",
                r"urllib\.request\.urlopen\s*\(.*?request\.",
                r"file_get_contents\s*\(.*?\$_GET",
                r"fetch\s*\(.*?params\.",
            ],
            "severity": "high",
            "cwe": "CWE-918",
            "languages": ["python", "php", "javascript", "java"]
        }
    }
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
    
    async def detect_vulnerabilities(
        self,
        code: str,
        language: str,
        filename: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Advanced vulnerability detection with pattern matching
        
        Args:
            code: Source code to analyze
            language: Programming language
            filename: Optional filename for context
            
        Returns:
            List of detected vulnerabilities with details
        """
        
        if language not in self.SUPPORTED_LANGUAGES:
            return [{
                "error": f"Language '{language}' not supported",
                "supported_languages": self.SUPPORTED_LANGUAGES
            }]
        
        vulnerabilities = []
        
        # Pattern-based detection
        for vuln_type, config in self.VULNERABILITY_PATTERNS.items():
            if language not in config["languages"]:
                continue
            
            for pattern in config["patterns"]:
                matches = list(re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE))
                
                for match in matches:
                    line_number = code[:match.start()].count('\n') + 1
                    
                    vulnerability = {
                        "type": vuln_type,
                        "severity": config["severity"],
                        "cwe": config["cwe"],
                        "line": line_number,
                        "matched_code": match.group(0),
                        "pattern": pattern,
                        "language": language,
                        "filename": filename,
                        "confidence": self._calculate_confidence(match.group(0), vuln_type),
                        "description": self._get_vulnerability_description(vuln_type),
                        "remediation": self._get_remediation_advice(vuln_type, language)
                    }
                    
                    vulnerabilities.append(vulnerability)
        
        # AST-based analysis for Python
        if language == "python":
            ast_vulns = await self._analyze_python_ast(code, filename)
            vulnerabilities.extend(ast_vulns)
        
        # AI-powered deep analysis
        if settings.OPENAI_API_KEY and vulnerabilities:
            ai_analysis = await self._ai_deep_analysis(code, vulnerabilities, language)
            for vuln in vulnerabilities:
                vuln["ai_insights"] = ai_analysis.get(vuln["type"], "")
        
        return vulnerabilities
    
    def _calculate_confidence(self, matched_code: str, vuln_type: str) -> float:
        """
        Calculate confidence score for detected vulnerability
        
        Higher confidence for:
        - Exact pattern matches
        - Multiple indicators
        - Clear vulnerable constructs
        """
        
        confidence = 0.6  # Base confidence
        
        # Increase confidence based on specific indicators
        high_confidence_indicators = {
            "sqli": ["execute", "query", "cursor", "raw"],
            "xss": ["innerHTML", "document.write", "eval"],
            "rce": ["eval", "exec", "system", "shell"],
            "hardcoded_secrets": ["password", "api_key", "secret_key"],
        }
        
        if vuln_type in high_confidence_indicators:
            for indicator in high_confidence_indicators[vuln_type]:
                if indicator in matched_code.lower():
                    confidence += 0.1
        
        # Check for user input indicators
        user_input_patterns = ["request.", "req.", "$_GET", "$_POST", "params."]
        for pattern in user_input_patterns:
            if pattern in matched_code:
                confidence += 0.15
        
        return min(confidence, 1.0)
    
    def _get_vulnerability_description(self, vuln_type: str) -> str:
        """Get detailed vulnerability description"""
        
        descriptions = {
            "sqli": "SQL Injection vulnerability allows attackers to manipulate database queries, potentially leading to unauthorized data access, modification, or deletion.",
            "xss": "Cross-Site Scripting vulnerability allows injection of malicious scripts that execute in users' browsers, potentially stealing sensitive data or performing actions on behalf of users.",
            "rce": "Remote Code Execution vulnerability allows attackers to execute arbitrary commands on the server, potentially leading to complete system compromise.",
            "path_traversal": "Path Traversal vulnerability allows attackers to access files outside the intended directory, potentially exposing sensitive system files.",
            "insecure_deserialization": "Insecure Deserialization can lead to remote code execution when untrusted data is deserialized without proper validation.",
            "weak_crypto": "Use of weak cryptographic algorithms makes encrypted data vulnerable to cryptanalysis and brute-force attacks.",
            "hardcoded_secrets": "Hardcoded credentials or API keys in source code can be discovered by attackers with access to the codebase or compiled binaries.",
            "xxe": "XML External Entity vulnerability allows attackers to interfere with XML processing, potentially leading to file disclosure, SSRF, or denial of service.",
            "csrf": "Cross-Site Request Forgery allows attackers to trick users into performing unintended actions on authenticated applications.",
            "ssrf": "Server-Side Request Forgery allows attackers to make requests from the server to internal resources or external systems."
        }
        
        return descriptions.get(vuln_type, f"Security vulnerability of type: {vuln_type}")
    
    def _get_remediation_advice(self, vuln_type: str, language: str) -> str:
        """Get language-specific remediation advice"""
        
        remediations = {
            "sqli": {
                "python": "Use parameterized queries with SQLAlchemy or psycopg2: `cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))`",
                "php": "Use prepared statements with PDO: `$stmt = $pdo->prepare('SELECT * FROM users WHERE id = ?'); $stmt->execute([$id]);`",
                "java": "Use PreparedStatement: `PreparedStatement stmt = conn.prepareStatement('SELECT * FROM users WHERE id = ?'); stmt.setInt(1, userId);`",
                "javascript": "Use parameterized queries with your database library (e.g., pg, mysql2) and avoid string concatenation in SQL."
            },
            "xss": {
                "javascript": "Use textContent instead of innerHTML, or sanitize input with DOMPurify library.",
                "python": "Use template auto-escaping (Jinja2, Django templates) or manually escape with `html.escape()`.",
                "php": "Use `htmlspecialchars($input, ENT_QUOTES, 'UTF-8')` for output encoding.",
                "java": "Use OWASP Java Encoder or framework-specific escaping methods."
            },
            "rce": {
                "python": "Avoid `eval()` and `exec()`. Use `subprocess` with shell=False and validate inputs. Use `shlex.quote()` for shell arguments.",
                "php": "Avoid `eval()`, `system()`, `exec()`. If necessary, use `escapeshellarg()` and validate inputs against allowlist.",
                "javascript": "Never use `eval()` with user input. Use safer alternatives like JSON.parse() or Function constructor carefully.",
                "java": "Avoid Runtime.exec() with user input. Use ProcessBuilder with validated arguments."
            },
            "hardcoded_secrets": {
                "python": "Use environment variables: `os.environ.get('API_KEY')` or secret management tools like HashiCorp Vault.",
                "javascript": "Use process.env or .env files (never commit .env to version control).",
                "java": "Use configuration files outside the codebase or secret management services.",
                "go": "Use environment variables or secret management libraries like viper."
            },
            "weak_crypto": {
                "python": "Use `hashlib.sha256()` or `hashlib.sha512()` instead of MD5/SHA1. Use `secrets` module for tokens.",
                "java": "Use SHA-256 or stronger. For encryption, use AES with GCM mode.",
                "javascript": "Use Web Crypto API with SHA-256 or stronger algorithms.",
                "csharp": "Use SHA256 or stronger from System.Security.Cryptography."
            }
        }
        
        language_remediation = remediations.get(vuln_type, {})
        return language_remediation.get(language, f"Follow security best practices to fix {vuln_type} vulnerability.")
    
    async def _analyze_python_ast(self, code: str, filename: str) -> List[Dict[str, Any]]:
        """Advanced Python AST analysis"""
        
        vulnerabilities = []
        
        try:
            tree = ast.parse(code, filename=filename)
            
            for node in ast.walk(tree):
                # Detect dangerous function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        
                        # Check for dangerous functions
                        if func_name in ["eval", "exec", "compile"]:
                            vulnerabilities.append({
                                "type": "rce",
                                "severity": "critical",
                                "cwe": "CWE-78",
                                "line": node.lineno,
                                "matched_code": f"{func_name}()",
                                "language": "python",
                                "filename": filename,
                                "confidence": 0.9,
                                "description": f"Dangerous use of {func_name}() function",
                                "remediation": "Avoid using eval/exec with untrusted input. Use safer alternatives."
                            })
                
                # Detect hardcoded strings that look like secrets
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id.lower()
                            if any(secret in var_name for secret in ["password", "secret", "key", "token"]):
                                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                    if len(node.value.value) > 8:  # Likely a real secret
                                        vulnerabilities.append({
                                            "type": "hardcoded_secrets",
                                            "severity": "high",
                                            "cwe": "CWE-798",
                                            "line": node.lineno,
                                            "matched_code": f"{var_name} = '***'",
                                            "language": "python",
                                            "filename": filename,
                                            "confidence": 0.8,
                                            "description": "Hardcoded sensitive credential detected",
                                            "remediation": "Use environment variables or secret management system"
                                        })
        
        except SyntaxError:
            pass  # Invalid Python code
        
        return vulnerabilities
    
    async def _ai_deep_analysis(
        self,
        code: str,
        vulnerabilities: List[Dict[str, Any]],
        language: str
    ) -> Dict[str, str]:
        """Use AI for deep vulnerability analysis"""
        
        if not settings.OPENAI_API_KEY:
            return {}
        
        try:
            vuln_summary = "\n".join([
                f"- {v['type']} at line {v['line']}: {v['matched_code'][:50]}"
                for v in vulnerabilities[:5]
            ])
            
            prompt = f"""
Analyze these potential security vulnerabilities in {language} code:

{vuln_summary}

For each vulnerability:
1. Confirm if it's a real vulnerability or false positive
2. Explain the security impact
3. Suggest specific code fix

Code context (first 200 chars):
{code[:200]}
"""
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior security engineer specializing in code security."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            insights = response.choices[0].message.content
            
            # Parse insights per vulnerability type
            result = {}
            for vuln in vulnerabilities:
                result[vuln["type"]] = insights
            
            return result
        
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}
    
    async def generate_fix(
        self,
        vulnerability: Dict[str, Any],
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Generate automatic fix for detected vulnerability
        
        Returns:
            {
                "original_code": str,
                "fixed_code": str,
                "explanation": str,
                "confidence": float,
                "manual_review_required": bool
            }
        """
        
        vuln_type = vulnerability["type"]
        line_number = vulnerability.get("line", 0)
        
        # Extract code context
        lines = code.split('\n')
        start_line = max(0, line_number - 3)
        end_line = min(len(lines), line_number + 2)
        code_context = '\n'.join(lines[start_line:end_line])
        
        # Rule-based fixes for common patterns
        rule_based_fix = self._apply_rule_based_fix(
            vuln_type, code_context, language
        )
        
        if rule_based_fix:
            return rule_based_fix
        
        # AI-powered fix generation
        if settings.OPENAI_API_KEY:
            return await self._ai_generate_fix(
                vulnerability, code_context, language
            )
        
        return {
            "original_code": code_context,
            "fixed_code": None,
            "explanation": "Automatic fix not available. Manual review required.",
            "confidence": 0.0,
            "manual_review_required": True
        }
    
    def _apply_rule_based_fix(
        self,
        vuln_type: str,
        code: str,
        language: str
    ) -> Optional[Dict[str, Any]]:
        """Apply rule-based fixes for common patterns"""
        
        fixed_code = code
        explanation = ""
        confidence = 0.7
        
        if vuln_type == "sqli" and language == "python":
            # Replace string concatenation with parameterized query
            if "+=" in code or "+" in code:
                fixed_code = re.sub(
                    r'execute\s*\(\s*[\'"](.+?)[\'"].*?\+.*?\)',
                    r'execute("\1 WHERE id = %s", (user_input,))',
                    code
                )
                explanation = "Replaced string concatenation with parameterized query using placeholders."
                confidence = 0.8
        
        elif vuln_type == "xss" and language == "javascript":
            # Replace innerHTML with textContent
            if "innerHTML" in code:
                fixed_code = code.replace("innerHTML", "textContent")
                explanation = "Replaced innerHTML with textContent to prevent XSS."
                confidence = 0.9
        
        elif vuln_type == "hardcoded_secrets":
            # Replace hardcoded secret with environment variable
            match = re.search(r'(\w+)\s*=\s*[\'"]([^\'"]+)[\'"]', code)
            if match:
                var_name = match.group(1)
                fixed_code = re.sub(
                    r'(\w+)\s*=\s*[\'"][^\'"]+[\'"]',
                    f'{var_name} = os.environ.get("{var_name.upper()}")',
                    code
                )
                explanation = f"Replaced hardcoded {var_name} with environment variable."
                confidence = 0.85
        
        if fixed_code != code:
            return {
                "original_code": code,
                "fixed_code": fixed_code,
                "explanation": explanation,
                "confidence": confidence,
                "manual_review_required": confidence < 0.8
            }
        
        return None
    
    async def _ai_generate_fix(
        self,
        vulnerability: Dict[str, Any],
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """Use AI to generate fix"""
        
        try:
            prompt = f"""
Fix this {vulnerability['type']} vulnerability in {language}:

Vulnerable code:
```{language}
{code}
```

Vulnerability: {vulnerability['description']}
CWE: {vulnerability['cwe']}

Provide:
1. Fixed code (complete, runnable)
2. Explanation of the fix
3. Any important notes

Format:
FIXED_CODE:
```
<fixed code here>
```

EXPLANATION:
<explanation here>
"""
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert security engineer. Provide secure, production-ready code fixes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            
            # Parse response
            fixed_code_match = re.search(r'FIXED_CODE:\s*```[^\n]*\n(.*?)```', content, re.DOTALL)
            explanation_match = re.search(r'EXPLANATION:\s*(.+)', content, re.DOTALL)
            
            fixed_code = fixed_code_match.group(1).strip() if fixed_code_match else None
            explanation = explanation_match.group(1).strip() if explanation_match else "AI-generated fix"
            
            return {
                "original_code": code,
                "fixed_code": fixed_code,
                "explanation": explanation,
                "confidence": 0.75,
                "manual_review_required": True
            }
        
        except Exception as e:
            return {
                "original_code": code,
                "fixed_code": None,
                "explanation": f"AI fix generation failed: {str(e)}",
                "confidence": 0.0,
                "manual_review_required": True
            }
