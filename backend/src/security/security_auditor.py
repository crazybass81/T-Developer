"""
Security Auditor for T-Developer Pipeline
Comprehensive security scanning and vulnerability detection
"""

import logging
import re
import ast
import os
import json
import hashlib
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import bandit
import semgrep

logger = logging.getLogger(__name__)

@dataclass
class SecurityVulnerability:
    """Security vulnerability definition"""
    id: str
    severity: str  # critical, high, medium, low
    category: str
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    cwe_id: str
    recommendation: str
    confidence: str  # high, medium, low

@dataclass
class SecurityAuditResult:
    """Security audit result"""
    scan_timestamp: datetime
    total_files_scanned: int
    vulnerabilities: List[SecurityVulnerability]
    security_score: float  # 0-100
    compliance_status: Dict[str, bool]
    recommendations: List[str]
    false_positives: int = 0

class SecurityAuditor:
    """Comprehensive security auditor"""
    
    def __init__(self):
        self.version = "1.0.0"
        
        # Security rules and patterns
        self.security_rules = {
            'sql_injection': [
                {
                    'pattern': r'(SELECT|INSERT|UPDATE|DELETE).*\+.*\w+',
                    'severity': 'critical',
                    'cwe': 'CWE-89',
                    'description': 'Potential SQL injection vulnerability'
                },
                {
                    'pattern': r'(execute|query)\s*\(\s*["\'].*\+',
                    'severity': 'critical', 
                    'cwe': 'CWE-89',
                    'description': 'SQL query concatenation detected'
                }
            ],
            'xss': [
                {
                    'pattern': r'innerHTML\s*=.*\+',
                    'severity': 'high',
                    'cwe': 'CWE-79',
                    'description': 'Potential XSS through innerHTML'
                },
                {
                    'pattern': r'document\.write\s*\(',
                    'severity': 'high',
                    'cwe': 'CWE-79', 
                    'description': 'Use of document.write can lead to XSS'
                }
            ],
            'hardcoded_secrets': [
                {
                    'pattern': r'(password|pwd|pass)\s*[=:]\s*["\'][^"\']{8,}["\']',
                    'severity': 'critical',
                    'cwe': 'CWE-798',
                    'description': 'Hardcoded password detected'
                },
                {
                    'pattern': r'(api_key|apikey|secret_key)\s*[=:]\s*["\'][^"\']{16,}["\']',
                    'severity': 'critical',
                    'cwe': 'CWE-798',
                    'description': 'Hardcoded API key detected'
                },
                {
                    'pattern': r'(token|jwt)\s*[=:]\s*["\'][^"\']{32,}["\']',
                    'severity': 'high',
                    'cwe': 'CWE-798',
                    'description': 'Hardcoded token detected'
                }
            ],
            'insecure_crypto': [
                {
                    'pattern': r'(MD5|SHA1)\s*\(',
                    'severity': 'medium',
                    'cwe': 'CWE-327',
                    'description': 'Weak cryptographic hash function'
                },
                {
                    'pattern': r'Math\.random\(\)',
                    'severity': 'low',
                    'cwe': 'CWE-338',
                    'description': 'Insecure random number generation'
                }
            ],
            'command_injection': [
                {
                    'pattern': r'(exec|system|shell_exec|passthru)\s*\(\s*.*\$',
                    'severity': 'critical',
                    'cwe': 'CWE-78',
                    'description': 'Potential command injection'
                },
                {
                    'pattern': r'subprocess\.(call|run|Popen).*shell=True',
                    'severity': 'high',
                    'cwe': 'CWE-78',
                    'description': 'Shell injection risk in subprocess'
                }
            ],
            'path_traversal': [
                {
                    'pattern': r'\.\./',
                    'severity': 'medium',
                    'cwe': 'CWE-22',
                    'description': 'Potential path traversal'
                },
                {
                    'pattern': r'os\.path\.join.*\.\.',
                    'severity': 'medium',
                    'cwe': 'CWE-22',
                    'description': 'Path traversal in os.path.join'
                }
            ]
        }
        
        # Compliance frameworks
        self.compliance_checks = {
            'owasp_top_10': [
                'sql_injection', 'xss', 'hardcoded_secrets', 
                'insecure_crypto', 'command_injection'
            ],
            'pci_dss': [
                'hardcoded_secrets', 'insecure_crypto', 'path_traversal'
            ],
            'hipaa': [
                'hardcoded_secrets', 'insecure_crypto'
            ],
            'gdpr': [
                'hardcoded_secrets', 'path_traversal'
            ]
        }
    
    async def audit_codebase(self, codebase_path: str) -> SecurityAuditResult:
        """Perform comprehensive security audit of codebase"""
        
        scan_start = datetime.now()
        vulnerabilities = []
        files_scanned = 0
        
        try:
            # Scan all source files
            for root, dirs, files in os.walk(codebase_path):
                # Skip common non-source directories
                dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', '.pytest_cache'}]
                
                for file in files:
                    if self._is_source_file(file):
                        file_path = os.path.join(root, file)
                        file_vulns = await self._scan_file(file_path)
                        vulnerabilities.extend(file_vulns)
                        files_scanned += 1
            
            # Run external security tools
            external_vulns = await self._run_external_security_tools(codebase_path)
            vulnerabilities.extend(external_vulns)
            
            # Calculate security score
            security_score = self._calculate_security_score(vulnerabilities)
            
            # Check compliance
            compliance_status = self._check_compliance(vulnerabilities)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(vulnerabilities)
            
            return SecurityAuditResult(
                scan_timestamp=scan_start,
                total_files_scanned=files_scanned,
                vulnerabilities=vulnerabilities,
                security_score=security_score,
                compliance_status=compliance_status,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            return SecurityAuditResult(
                scan_timestamp=scan_start,
                total_files_scanned=files_scanned,
                vulnerabilities=[],
                security_score=0.0,
                compliance_status={},
                recommendations=[f"Audit failed: {str(e)}"]
            )
    
    async def _scan_file(self, file_path: str) -> List[SecurityVulnerability]:
        """Scan individual file for vulnerabilities"""
        
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Apply security rules
            for category, rules in self.security_rules.items():
                for rule in rules:
                    pattern = rule['pattern']
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    
                    for match in matches:
                        line_number = content[:match.start()].count('\n') + 1
                        
                        # Extract code snippet
                        lines = content.split('\n')
                        start_line = max(0, line_number - 2)
                        end_line = min(len(lines), line_number + 1)
                        code_snippet = '\n'.join(lines[start_line:end_line])
                        
                        vuln_id = hashlib.md5(
                            f"{file_path}:{line_number}:{pattern}".encode()
                        ).hexdigest()[:8]
                        
                        vulnerability = SecurityVulnerability(
                            id=f"SEC-{vuln_id}",
                            severity=rule['severity'],
                            category=category,
                            title=rule['description'],
                            description=f"{rule['description']} in {os.path.basename(file_path)}",
                            file_path=file_path,
                            line_number=line_number,
                            code_snippet=code_snippet,
                            cwe_id=rule['cwe'],
                            recommendation=self._get_recommendation(category, rule),
                            confidence='medium'
                        )
                        
                        vulnerabilities.append(vulnerability)
            
            # Additional Python-specific checks
            if file_path.endswith('.py'):
                python_vulns = await self._scan_python_file(file_path, content)
                vulnerabilities.extend(python_vulns)
            
            # JavaScript/TypeScript specific checks
            elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                js_vulns = await self._scan_javascript_file(file_path, content)
                vulnerabilities.extend(js_vulns)
                
        except Exception as e:
            logger.warning(f"Failed to scan file {file_path}: {e}")
        
        return vulnerabilities
    
    async def _scan_python_file(self, file_path: str, content: str) -> List[SecurityVulnerability]:
        """Python-specific security scanning"""
        
        vulnerabilities = []
        
        try:
            # Parse AST for deeper analysis
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Check for eval/exec usage
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        vuln = SecurityVulnerability(
                            id=f"PY-{hashlib.md5(f'{file_path}:{node.lineno}'.encode()).hexdigest()[:8]}",
                            severity='critical',
                            category='code_injection',
                            title='Use of eval() or exec()',
                            description='eval() and exec() can execute arbitrary code',
                            file_path=file_path,
                            line_number=node.lineno,
                            code_snippet=content.split('\n')[node.lineno-1] if node.lineno <= len(content.split('\n')) else '',
                            cwe_id='CWE-94',
                            recommendation='Use safer alternatives like ast.literal_eval() for data parsing',
                            confidence='high'
                        )
                        vulnerabilities.append(vuln)
                
                # Check for pickle usage (deserialization risk)
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == 'pickle':
                            vuln = SecurityVulnerability(
                                id=f"PY-{hashlib.md5(f'{file_path}:{node.lineno}:pickle'.encode()).hexdigest()[:8]}",
                                severity='medium',
                                category='deserialization',
                                title='Use of pickle module',
                                description='pickle can execute arbitrary code during deserialization',
                                file_path=file_path,
                                line_number=node.lineno,
                                code_snippet=content.split('\n')[node.lineno-1] if node.lineno <= len(content.split('\n')) else '',
                                cwe_id='CWE-502',
                                recommendation='Use safer serialization formats like JSON',
                                confidence='medium'
                            )
                            vulnerabilities.append(vuln)
                            
        except SyntaxError:
            # File has syntax errors, skip AST analysis
            pass
        except Exception as e:
            logger.warning(f"Python AST analysis failed for {file_path}: {e}")
        
        return vulnerabilities
    
    async def _scan_javascript_file(self, file_path: str, content: str) -> List[SecurityVulnerability]:
        """JavaScript/TypeScript-specific security scanning"""
        
        vulnerabilities = []
        
        # Check for dangerous functions
        dangerous_patterns = [
            (r'dangerouslySetInnerHTML', 'high', 'CWE-79', 'Potential XSS via dangerouslySetInnerHTML'),
            (r'Function\s*\(\s*["\'].*["\']', 'critical', 'CWE-94', 'Dynamic code execution with Function()'),
            (r'setTimeout\s*\(\s*["\'].*["\']', 'medium', 'CWE-94', 'Code injection via setTimeout string'),
            (r'setInterval\s*\(\s*["\'].*["\']', 'medium', 'CWE-94', 'Code injection via setInterval string'),
        ]
        
        for pattern, severity, cwe, description in dangerous_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                line_number = content[:match.start()].count('\n') + 1
                lines = content.split('\n')
                code_snippet = lines[line_number-1] if line_number <= len(lines) else ''
                
                vuln = SecurityVulnerability(
                    id=f"JS-{hashlib.md5(f'{file_path}:{line_number}:{pattern}'.encode()).hexdigest()[:8]}",
                    severity=severity,
                    category='code_injection',
                    title=description,
                    description=f"{description} in {os.path.basename(file_path)}",
                    file_path=file_path,
                    line_number=line_number,
                    code_snippet=code_snippet,
                    cwe_id=cwe,
                    recommendation=self._get_js_recommendation(pattern),
                    confidence='medium'
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    async def _run_external_security_tools(self, codebase_path: str) -> List[SecurityVulnerability]:
        """Run external security scanning tools"""
        
        vulnerabilities = []
        
        try:
            # Run Bandit for Python security
            bandit_results = await self._run_bandit(codebase_path)
            vulnerabilities.extend(bandit_results)
            
            # Run Semgrep for multi-language security
            semgrep_results = await self._run_semgrep(codebase_path)
            vulnerabilities.extend(semgrep_results)
            
        except Exception as e:
            logger.warning(f"External security tools failed: {e}")
        
        return vulnerabilities
    
    async def _run_bandit(self, codebase_path: str) -> List[SecurityVulnerability]:
        """Run Bandit Python security scanner"""
        
        vulnerabilities = []
        
        try:
            cmd = ['bandit', '-r', codebase_path, '-f', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                bandit_output = json.loads(result.stdout)
                
                for issue in bandit_output.get('results', []):
                    vuln = SecurityVulnerability(
                        id=f"BANDIT-{issue['test_id']}",
                        severity=issue['issue_severity'].lower(),
                        category='bandit',
                        title=issue['test_name'],
                        description=issue['issue_text'],
                        file_path=issue['filename'],
                        line_number=issue['line_number'],
                        code_snippet=issue['code'],
                        cwe_id=f"CWE-{issue.get('cwe', 'Unknown')}",
                        recommendation=issue.get('issue_text', 'Review Bandit documentation'),
                        confidence=issue['issue_confidence'].lower()
                    )
                    vulnerabilities.append(vuln)
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.warning(f"Bandit scan failed: {e}")
        except FileNotFoundError:
            logger.warning("Bandit not installed, skipping Python security scan")
        
        return vulnerabilities
    
    async def _run_semgrep(self, codebase_path: str) -> List[SecurityVulnerability]:
        """Run Semgrep multi-language security scanner"""
        
        vulnerabilities = []
        
        try:
            cmd = ['semgrep', '--config=auto', '--json', codebase_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                semgrep_output = json.loads(result.stdout)
                
                for result_item in semgrep_output.get('results', []):
                    vuln = SecurityVulnerability(
                        id=f"SEMGREP-{result_item['check_id']}",
                        severity=result_item.get('extra', {}).get('severity', 'medium').lower(),
                        category='semgrep',
                        title=result_item.get('extra', {}).get('message', 'Security issue'),
                        description=result_item.get('extra', {}).get('message', ''),
                        file_path=result_item['path'],
                        line_number=result_item['start']['line'],
                        code_snippet=result_item.get('extra', {}).get('lines', ''),
                        cwe_id=result_item.get('extra', {}).get('metadata', {}).get('cwe', 'Unknown'),
                        recommendation=result_item.get('extra', {}).get('fix', 'Review Semgrep documentation'),
                        confidence='high'
                    )
                    vulnerabilities.append(vuln)
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.warning(f"Semgrep scan failed: {e}")
        except FileNotFoundError:
            logger.warning("Semgrep not installed, skipping multi-language security scan")
        
        return vulnerabilities
    
    def _is_source_file(self, filename: str) -> bool:
        """Check if file is a source code file"""
        
        source_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h',
            '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.sql',
            '.html', '.htm', '.xml', '.yaml', '.yml', '.json'
        }
        
        return any(filename.endswith(ext) for ext in source_extensions)
    
    def _calculate_security_score(self, vulnerabilities: List[SecurityVulnerability]) -> float:
        """Calculate overall security score (0-100)"""
        
        if not vulnerabilities:
            return 100.0
        
        severity_weights = {
            'critical': 25,
            'high': 15,
            'medium': 8,
            'low': 3
        }
        
        total_penalty = sum(
            severity_weights.get(vuln.severity, 5) 
            for vuln in vulnerabilities
        )
        
        # Calculate score with maximum penalty cap
        max_penalty = 100
        penalty_ratio = min(total_penalty / max_penalty, 1.0)
        
        return max(0, 100 - (penalty_ratio * 100))
    
    def _check_compliance(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, bool]:
        """Check compliance with security frameworks"""
        
        compliance_status = {}
        
        # Group vulnerabilities by category
        vuln_categories = {vuln.category for vuln in vulnerabilities}
        critical_vulns = {vuln.category for vuln in vulnerabilities if vuln.severity == 'critical'}
        
        for framework, required_categories in self.compliance_checks.items():
            # Check if any critical vulnerabilities exist in required categories
            has_critical_issues = bool(critical_vulns.intersection(required_categories))
            compliance_status[framework] = not has_critical_issues
        
        return compliance_status
    
    def _generate_recommendations(self, vulnerabilities: List[SecurityVulnerability]) -> List[str]:
        """Generate security recommendations"""
        
        recommendations = []
        
        # Group by category and severity
        category_counts = {}
        for vuln in vulnerabilities:
            key = f"{vuln.category}_{vuln.severity}"
            category_counts[key] = category_counts.get(key, 0) + 1
        
        # Priority recommendations based on critical issues
        critical_categories = {
            vuln.category for vuln in vulnerabilities 
            if vuln.severity == 'critical'
        }
        
        if 'sql_injection' in critical_categories:
            recommendations.append("CRITICAL: Implement parameterized queries to prevent SQL injection")
        
        if 'hardcoded_secrets' in critical_categories:
            recommendations.append("CRITICAL: Remove hardcoded secrets and use environment variables")
        
        if 'command_injection' in critical_categories:
            recommendations.append("CRITICAL: Sanitize input and avoid shell command execution")
        
        # General recommendations
        if len(vulnerabilities) > 10:
            recommendations.append("Consider implementing automated security testing in CI/CD pipeline")
        
        if any(vuln.severity in ['critical', 'high'] for vuln in vulnerabilities):
            recommendations.append("Perform manual security code review for high-risk areas")
        
        # Add specific recommendations from vulnerabilities
        unique_recommendations = set()
        for vuln in vulnerabilities:
            if vuln.severity in ['critical', 'high'] and vuln.recommendation:
                unique_recommendations.add(vuln.recommendation)
        
        recommendations.extend(list(unique_recommendations)[:5])  # Limit to top 5
        
        return recommendations
    
    def _get_recommendation(self, category: str, rule: Dict[str, str]) -> str:
        """Get recommendation for specific vulnerability category"""
        
        recommendations = {
            'sql_injection': 'Use parameterized queries or prepared statements',
            'xss': 'Sanitize and validate all user inputs, use content security policy',
            'hardcoded_secrets': 'Use environment variables or secure secret management',
            'insecure_crypto': 'Use strong cryptographic algorithms (SHA-256, bcrypt)',
            'command_injection': 'Validate inputs and avoid shell command execution',
            'path_traversal': 'Validate and sanitize file paths, use allowlists'
        }
        
        return recommendations.get(category, 'Review security best practices for this vulnerability type')
    
    def _get_js_recommendation(self, pattern: str) -> str:
        """Get JavaScript-specific recommendations"""
        
        if 'dangerouslySetInnerHTML' in pattern:
            return 'Sanitize HTML content or use safer React patterns'
        elif 'Function' in pattern:
            return 'Avoid dynamic code execution, use safer alternatives'
        elif 'setTimeout' in pattern or 'setInterval' in pattern:
            return 'Use function references instead of string code in timers'
        else:
            return 'Follow JavaScript security best practices'
    
    def generate_security_report(self, audit_result: SecurityAuditResult) -> str:
        """Generate human-readable security report"""
        
        report = f"""
# Security Audit Report

**Scan Date**: {audit_result.scan_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Files Scanned**: {audit_result.total_files_scanned}
**Security Score**: {audit_result.security_score:.1f}/100

## Vulnerability Summary

Total Vulnerabilities: {len(audit_result.vulnerabilities)}

By Severity:
- Critical: {len([v for v in audit_result.vulnerabilities if v.severity == 'critical'])}
- High: {len([v for v in audit_result.vulnerabilities if v.severity == 'high'])}
- Medium: {len([v for v in audit_result.vulnerabilities if v.severity == 'medium'])}
- Low: {len([v for v in audit_result.vulnerabilities if v.severity == 'low'])}

## Compliance Status

"""
        
        for framework, status in audit_result.compliance_status.items():
            status_emoji = "✅" if status else "❌"
            report += f"- {framework.upper()}: {status_emoji} {'Compliant' if status else 'Non-compliant'}\n"
        
        report += "\n## Top Recommendations\n\n"
        
        for i, rec in enumerate(audit_result.recommendations[:5], 1):
            report += f"{i}. {rec}\n"
        
        if audit_result.vulnerabilities:
            report += "\n## Critical Vulnerabilities\n\n"
            
            critical_vulns = [v for v in audit_result.vulnerabilities if v.severity == 'critical']
            for vuln in critical_vulns[:5]:  # Show top 5 critical
                report += f"**{vuln.id}**: {vuln.title}\n"
                report += f"- File: {vuln.file_path}:{vuln.line_number}\n"
                report += f"- CWE: {vuln.cwe_id}\n"
                report += f"- Recommendation: {vuln.recommendation}\n\n"
        
        return report