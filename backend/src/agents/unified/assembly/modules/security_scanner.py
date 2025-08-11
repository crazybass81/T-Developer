"""
Security Scanner Module for Assembly Agent
Scans for security vulnerabilities and compliance issues
"""

from typing import Dict, List, Any, Optional
import asyncio
import re
import json
import hashlib
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SecurityVulnerability:
    vulnerability_id: str
    severity: str  # critical, high, medium, low
    category: str
    title: str
    description: str
    file_path: str
    line_number: int
    cwe_id: str  # Common Weakness Enumeration ID
    recommendation: str
    confidence: str  # high, medium, low

@dataclass
class SecurityResult:
    success: bool
    security_score: float
    vulnerabilities: List[SecurityVulnerability]
    compliance_status: Dict[str, bool]
    security_report: Dict[str, Any]
    scans_completed: int
    processing_time: float
    error: str = ""

class SecurityScanner:
    """Advanced security scanning system"""
    
    def __init__(self):
        self.version = "1.0.0"
        
        self.security_rules = {
            'injection': [
                {
                    'pattern': r'eval\s*\(',
                    'title': 'Code Injection Vulnerability',
                    'description': 'Use of eval() function can lead to code injection',
                    'severity': 'critical',
                    'cwe': 'CWE-94',
                    'recommendation': 'Avoid using eval(). Use JSON.parse() for JSON data or safer alternatives.'
                },
                {
                    'pattern': r'innerHTML\s*=\s*.*\+',
                    'title': 'DOM-based XSS Vulnerability',
                    'description': 'Dynamic innerHTML assignment can lead to XSS',
                    'severity': 'high',
                    'cwe': 'CWE-79',
                    'recommendation': 'Use textContent, createElement, or sanitize HTML content.'
                },
                {
                    'pattern': r'document\.write\s*\(',
                    'title': 'DOM-based XSS Vulnerability',
                    'description': 'document.write() can introduce XSS vulnerabilities',
                    'severity': 'high',
                    'cwe': 'CWE-79',
                    'recommendation': 'Use safer DOM manipulation methods.'
                },
                {
                    'pattern': r'dangerouslySetInnerHTML',
                    'title': 'Potential XSS Vulnerability',
                    'description': 'dangerouslySetInnerHTML can introduce XSS if not properly sanitized',
                    'severity': 'medium',
                    'cwe': 'CWE-79',
                    'recommendation': 'Ensure HTML content is properly sanitized before using dangerouslySetInnerHTML.'
                }
            ],
            'authentication': [
                {
                    'pattern': r'password\s*[=:]\s*["\'][^"\s]+["\']',
                    'title': 'Hardcoded Password',
                    'description': 'Hardcoded passwords in source code',
                    'severity': 'critical',
                    'cwe': 'CWE-798',
                    'recommendation': 'Use environment variables or secure credential storage.'
                },
                {
                    'pattern': r'api[_-]?key\s*[=:]\s*["\'][^"\s]+["\']',
                    'title': 'Hardcoded API Key',
                    'description': 'API keys should not be hardcoded',
                    'severity': 'critical',
                    'cwe': 'CWE-798',
                    'recommendation': 'Use environment variables for API keys.'
                },
                {
                    'pattern': r'secret\s*[=:]\s*["\'][^"\s]+["\']',
                    'title': 'Hardcoded Secret',
                    'description': 'Secrets should not be hardcoded in source code',
                    'severity': 'high',
                    'cwe': 'CWE-798',
                    'recommendation': 'Use secure secret management systems.'
                },
                {
                    'pattern': r'localStorage\.setItem\s*\(.*password',
                    'title': 'Sensitive Data in Local Storage',
                    'description': 'Storing sensitive data in localStorage is insecure',
                    'severity': 'medium',
                    'cwe': 'CWE-922',
                    'recommendation': 'Use secure storage methods for sensitive data.'
                }
            ],
            'crypto': [
                {
                    'pattern': r'MD5|SHA1',
                    'title': 'Weak Cryptographic Hash',
                    'description': 'MD5 and SHA1 are cryptographically weak',
                    'severity': 'medium',
                    'cwe': 'CWE-327',
                    'recommendation': 'Use stronger hashing algorithms like SHA-256 or bcrypt.'
                },
                {
                    'pattern': r'Math\.random\(\)',
                    'title': 'Weak Random Number Generator',
                    'description': 'Math.random() is not cryptographically secure',
                    'severity': 'low',
                    'cwe': 'CWE-338',
                    'recommendation': 'Use crypto.getRandomValues() for security-sensitive random numbers.'
                },
                {
                    'pattern': r'btoa\s*\([^)]*password',
                    'title': 'Base64 Encoding of Sensitive Data',
                    'description': 'Base64 is encoding, not encryption',
                    'severity': 'medium',
                    'cwe': 'CWE-327',
                    'recommendation': 'Use proper encryption for sensitive data.'
                }
            ],
            'data_exposure': [
                {
                    'pattern': r'console\.log\s*\([^)]*password',
                    'title': 'Sensitive Data in Logs',
                    'description': 'Logging sensitive data can lead to exposure',
                    'severity': 'medium',
                    'cwe': 'CWE-532',
                    'recommendation': 'Remove or sanitize sensitive data from logs.'
                },
                {
                    'pattern': r'alert\s*\([^)]*password',
                    'title': 'Sensitive Data in Alert',
                    'description': 'Displaying sensitive data in alerts',
                    'severity': 'medium',
                    'cwe': 'CWE-532',
                    'recommendation': 'Remove sensitive data from user-visible alerts.'
                },
                {
                    'pattern': r'\.env\s*\.',
                    'title': 'Environment File Access',
                    'description': 'Direct access to .env files in client code',
                    'severity': 'low',
                    'cwe': 'CWE-200',
                    'recommendation': 'Ensure .env files are not accessible in production.'
                }
            ],
            'input_validation': [
                {
                    'pattern': r'exec\s*\(',
                    'title': 'Command Injection Risk',
                    'description': 'exec() can lead to command injection',
                    'severity': 'critical',
                    'cwe': 'CWE-78',
                    'recommendation': 'Validate and sanitize all input before using exec().'
                },
                {
                    'pattern': r'system\s*\(',
                    'title': 'Command Injection Risk',
                    'description': 'system() calls can lead to command injection',
                    'severity': 'critical',
                    'cwe': 'CWE-78',
                    'recommendation': 'Validate input and use safer alternatives.'
                },
                {
                    'pattern': r'os\.system\s*\(',
                    'title': 'Command Injection Risk',
                    'description': 'os.system() can lead to command injection',
                    'severity': 'critical',
                    'cwe': 'CWE-78',
                    'recommendation': 'Use subprocess with proper input validation.'
                }
            ]
        }
        
        self.compliance_checks = {
            'owasp_top_10': [
                'injection',
                'authentication',
                'data_exposure',
                'crypto'
            ],
            'gdpr_compliance': [
                'data_exposure',
                'crypto'
            ],
            'pci_dss': [
                'authentication',
                'crypto',
                'data_exposure'
            ]
        }
    
    async def scan_security(
        self,
        analyzed_files: Dict[str, str],
        context: Dict[str, Any]
    ) -> SecurityResult:
        """Perform comprehensive security scan"""
        
        start_time = datetime.now()
        vulnerabilities = []
        scans_completed = 0
        
        try:
            # Scan for each security rule category
            for category, rules in self.security_rules.items():
                category_vulns = await self._scan_category(
                    analyzed_files, category, rules
                )
                vulnerabilities.extend(category_vulns)
                scans_completed += len(rules)
            
            # Additional context-specific scans
            framework = context.get('framework', 'react')
            framework_vulns = await self._scan_framework_specific(
                analyzed_files, framework
            )
            vulnerabilities.extend(framework_vulns)
            scans_completed += len(framework_vulns)
            
            # Dependency vulnerability scan
            dependency_vulns = await self._scan_dependencies(
                analyzed_files
            )
            vulnerabilities.extend(dependency_vulns)
            scans_completed += 1
            
            # Calculate security score
            security_score = self._calculate_security_score(vulnerabilities)
            
            # Check compliance status
            compliance_status = self._check_compliance(vulnerabilities)
            
            # Generate security report
            security_report = {
                'total_vulnerabilities': len(vulnerabilities),
                'vulnerabilities_by_severity': self._group_by_severity(vulnerabilities),
                'vulnerabilities_by_category': self._group_by_category(vulnerabilities),
                'security_score': security_score,
                'compliance_status': compliance_status,
                'scans_completed': scans_completed,
                'scan_timestamp': datetime.now().isoformat(),
                'recommendations': self._get_top_recommendations(vulnerabilities)
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return SecurityResult(
                success=True,
                security_score=security_score,
                vulnerabilities=vulnerabilities,
                compliance_status=compliance_status,
                security_report=security_report,
                scans_completed=scans_completed,
                processing_time=processing_time
            )
            
        except Exception as e:
            return SecurityResult(
                success=False,
                security_score=0.0,
                vulnerabilities=[],
                compliance_status={},
                security_report={},
                scans_completed=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    async def _scan_category(
        self,
        files: Dict[str, str],
        category: str,
        rules: List[Dict[str, str]]
    ) -> List[SecurityVulnerability]:
        """Scan files for specific category of vulnerabilities"""
        
        vulnerabilities = []
        
        for rule in rules:
            pattern = rule['pattern']
            
            for file_path, content in files.items():
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                
                for match in matches:
                    line_number = content[:match.start()].count('\n') + 1
                    
                    vulnerability_id = self._generate_vulnerability_id(
                        file_path, line_number, rule['title']
                    )
                    
                    vulnerabilities.append(SecurityVulnerability(
                        vulnerability_id=vulnerability_id,
                        severity=rule['severity'],
                        category=category,
                        title=rule['title'],
                        description=rule['description'],
                        file_path=file_path,
                        line_number=line_number,
                        cwe_id=rule['cwe'],
                        recommendation=rule['recommendation'],
                        confidence='high'
                    ))
        
        return vulnerabilities
    
    async def _scan_framework_specific(
        self,
        files: Dict[str, str],
        framework: str
    ) -> List[SecurityVulnerability]:
        """Scan for framework-specific security issues"""
        
        vulnerabilities = []
        
        framework_rules = {
            'react': [
                {
                    'pattern': r'React\.createElement\s*\(\s*["\']script["\']',
                    'title': 'Dynamic Script Element Creation',
                    'description': 'Creating script elements dynamically can be dangerous',
                    'severity': 'high',
                    'cwe': 'CWE-79',
                    'recommendation': 'Avoid creating script elements dynamically'
                }
            ],
            'vue': [
                {
                    'pattern': r'v-html\s*=',
                    'title': 'Potential XSS via v-html',
                    'description': 'v-html directive can introduce XSS if not sanitized',
                    'severity': 'medium',
                    'cwe': 'CWE-79',
                    'recommendation': 'Sanitize HTML content before using v-html'
                }
            ],
            'angular': [
                {
                    'pattern': r'\[innerHTML\]\s*=',
                    'title': 'Potential XSS via innerHTML binding',
                    'description': 'innerHTML binding can introduce XSS',
                    'severity': 'medium',
                    'cwe': 'CWE-79',
                    'recommendation': 'Use Angular sanitization or avoid innerHTML binding'
                }
            ],
            'express': [
                {
                    'pattern': r'res\.send\s*\([^)]*req\.',
                    'title': 'Potential Injection via Direct Request Data',
                    'description': 'Sending request data directly without validation',
                    'severity': 'high',
                    'cwe': 'CWE-79',
                    'recommendation': 'Validate and sanitize request data before sending'
                }
            ]
        }
        
        if framework in framework_rules:
            for rule in framework_rules[framework]:
                for file_path, content in files.items():
                    matches = re.finditer(rule['pattern'], content, re.MULTILINE)
                    
                    for match in matches:
                        line_number = content[:match.start()].count('\n') + 1
                        
                        vulnerability_id = self._generate_vulnerability_id(
                            file_path, line_number, rule['title']
                        )
                        
                        vulnerabilities.append(SecurityVulnerability(
                            vulnerability_id=vulnerability_id,
                            severity=rule['severity'],
                            category='framework_specific',
                            title=rule['title'],
                            description=rule['description'],
                            file_path=file_path,
                            line_number=line_number,
                            cwe_id=rule['cwe'],
                            recommendation=rule['recommendation'],
                            confidence='medium'
                        ))
        
        return vulnerabilities
    
    async def _scan_dependencies(
        self,
        files: Dict[str, str]
    ) -> List[SecurityVulnerability]:
        """Scan for known vulnerable dependencies"""
        
        vulnerabilities = []
        
        # Known vulnerable packages (simplified list)
        vulnerable_packages = {
            'lodash': {
                'versions': ['<4.17.11'],
                'vulnerability': 'Prototype Pollution',
                'severity': 'high',
                'cwe': 'CWE-1321'
            },
            'moment': {
                'versions': ['<2.29.2'],
                'vulnerability': 'ReDoS vulnerability',
                'severity': 'medium',
                'cwe': 'CWE-1333'
            },
            'axios': {
                'versions': ['<0.21.2'],
                'vulnerability': 'SSRF vulnerability',
                'severity': 'medium',
                'cwe': 'CWE-918'
            }
        }
        
        if 'package.json' in files:
            try:
                package_data = json.loads(files['package.json'])
                dependencies = {**package_data.get('dependencies', {}), 
                              **package_data.get('devDependencies', {})}
                
                for dep_name, version in dependencies.items():
                    if dep_name in vulnerable_packages:
                        vuln_info = vulnerable_packages[dep_name]
                        
                        # Simplified version check (in production, use proper semver)
                        is_vulnerable = self._is_version_vulnerable(
                            version, vuln_info['versions']
                        )
                        
                        if is_vulnerable:
                            vulnerability_id = self._generate_vulnerability_id(
                                'package.json', 0, f"Vulnerable {dep_name}"
                            )
                            
                            vulnerabilities.append(SecurityVulnerability(
                                vulnerability_id=vulnerability_id,
                                severity=vuln_info['severity'],
                                category='dependency',
                                title=f"Vulnerable Dependency: {dep_name}",
                                description=f"{dep_name} {version} has known {vuln_info['vulnerability']}",
                                file_path='package.json',
                                line_number=0,
                                cwe_id=vuln_info['cwe'],
                                recommendation=f"Update {dep_name} to a secure version",
                                confidence='high'
                            ))
                        
            except json.JSONDecodeError:
                pass
        
        return vulnerabilities
    
    def _generate_vulnerability_id(self, file_path: str, line_number: int, title: str) -> str:
        """Generate unique vulnerability ID"""
        
        content = f"{file_path}:{line_number}:{title}"
        hash_obj = hashlib.md5(content.encode())
        return f"SEC-{hash_obj.hexdigest()[:8].upper()}"
    
    def _calculate_security_score(self, vulnerabilities: List[SecurityVulnerability]) -> float:
        """Calculate overall security score"""
        
        if not vulnerabilities:
            return 100.0
        
        severity_penalties = {
            'critical': 25,
            'high': 15,
            'medium': 8,
            'low': 3
        }
        
        total_penalty = 0
        for vuln in vulnerabilities:
            penalty = severity_penalties.get(vuln.severity, 0)
            total_penalty += penalty
        
        score = max(0, 100 - total_penalty)
        return score
    
    def _check_compliance(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, bool]:
        """Check compliance with security standards"""
        
        compliance_status = {}
        
        for standard, required_categories in self.compliance_checks.items():
            # Check if there are critical/high vulnerabilities in required categories
            critical_vulns = [
                v for v in vulnerabilities
                if v.category in required_categories and v.severity in ['critical', 'high']
            ]
            
            compliance_status[standard] = len(critical_vulns) == 0
        
        return compliance_status
    
    def _group_by_severity(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, int]:
        """Group vulnerabilities by severity"""
        
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for vuln in vulnerabilities:
            if vuln.severity in severity_counts:
                severity_counts[vuln.severity] += 1
        
        return severity_counts
    
    def _group_by_category(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, int]:
        """Group vulnerabilities by category"""
        
        category_counts = {}
        
        for vuln in vulnerabilities:
            if vuln.category not in category_counts:
                category_counts[vuln.category] = 0
            category_counts[vuln.category] += 1
        
        return category_counts
    
    def _get_top_recommendations(self, vulnerabilities: List[SecurityVulnerability], limit: int = 5) -> List[str]:
        """Get top security recommendations"""
        
        # Sort by severity and get unique recommendations
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_vulns = sorted(
            vulnerabilities,
            key=lambda v: severity_order.get(v.severity, 4)
        )
        
        recommendations = []
        seen_recommendations = set()
        
        for vuln in sorted_vulns:
            if vuln.recommendation not in seen_recommendations:
                recommendations.append(vuln.recommendation)
                seen_recommendations.add(vuln.recommendation)
                
                if len(recommendations) >= limit:
                    break
        
        return recommendations
    
    def _is_version_vulnerable(self, version: str, vulnerable_versions: List[str]) -> bool:
        """Check if version matches vulnerable version patterns"""
        
        # Simplified vulnerability check (in production, use proper semver)
        for vuln_pattern in vulnerable_versions:
            if vuln_pattern.startswith('<'):
                target_version = vuln_pattern[1:]
                # Simple comparison (would need proper semver in production)
                if version.replace('^', '').replace('~', '') < target_version:
                    return True
        
        return False
