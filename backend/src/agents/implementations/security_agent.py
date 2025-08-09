"""
Security Agent
보안 검증 및 취약점 스캔 에이전트
"""

import asyncio
import re
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging

from src.agents.base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class SecurityIssue:
    """보안 이슈"""
    severity: str  # critical, high, medium, low
    type: str  # injection, xss, csrf, etc.
    file: str
    line: int
    description: str
    recommendation: str
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None


@dataclass
class SecurityScanResult:
    """보안 스캔 결과"""
    issues: List[SecurityIssue] = field(default_factory=list)
    total_issues: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    security_score: float = 100.0
    passed: bool = True
    scan_duration: float = 0.0
    recommendations: List[str] = field(default_factory=list)


class SecurityAgent(BaseAgent):
    """
    코드 보안 검증 에이전트
    
    주요 기능:
    - OWASP Top 10 취약점 검사
    - SQL Injection 검사
    - XSS 취약점 검사
    - 민감 정보 노출 검사
    - 의존성 취약점 검사
    - 보안 설정 검증
    """
    
    def __init__(self, environment: str = "production"):
        super().__init__(environment)
        self.name = "SecurityAgent"
        
        # 보안 패턴 정의
        self.security_patterns = self._init_security_patterns()
        
        # 민감 정보 패턴
        self.sensitive_patterns = self._init_sensitive_patterns()
        
        # 안전하지 않은 함수들
        self.unsafe_functions = self._init_unsafe_functions()
    
    def _init_security_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """보안 패턴 초기화"""
        return {
            'sql_injection': [
                {
                    'pattern': r'(SELECT|INSERT|UPDATE|DELETE).*\+.*["\']',
                    'description': 'Potential SQL injection via string concatenation',
                    'severity': 'critical',
                    'cwe': 'CWE-89'
                },
                {
                    'pattern': r'f["\'].*{.*}.*(?:SELECT|INSERT|UPDATE|DELETE)',
                    'description': 'SQL query using f-string interpolation',
                    'severity': 'high',
                    'cwe': 'CWE-89'
                }
            ],
            'xss': [
                {
                    'pattern': r'innerHTML\s*=\s*[^\'"]',
                    'description': 'Direct innerHTML assignment without sanitization',
                    'severity': 'high',
                    'cwe': 'CWE-79'
                },
                {
                    'pattern': r'document\.write\([^\'"]',
                    'description': 'document.write with user input',
                    'severity': 'high',
                    'cwe': 'CWE-79'
                },
                {
                    'pattern': r'dangerouslySetInnerHTML',
                    'description': 'React dangerouslySetInnerHTML usage',
                    'severity': 'medium',
                    'cwe': 'CWE-79'
                }
            ],
            'path_traversal': [
                {
                    'pattern': r'\.\./',
                    'description': 'Path traversal pattern detected',
                    'severity': 'high',
                    'cwe': 'CWE-22'
                },
                {
                    'pattern': r'os\.path\.join\([^,)]*request',
                    'description': 'Path join with user input',
                    'severity': 'high',
                    'cwe': 'CWE-22'
                }
            ],
            'command_injection': [
                {
                    'pattern': r'os\.system\(',
                    'description': 'os.system usage (command injection risk)',
                    'severity': 'critical',
                    'cwe': 'CWE-78'
                },
                {
                    'pattern': r'subprocess\.call\([^,\]]*shell=True',
                    'description': 'subprocess with shell=True',
                    'severity': 'critical',
                    'cwe': 'CWE-78'
                },
                {
                    'pattern': r'eval\(',
                    'description': 'eval() function usage',
                    'severity': 'critical',
                    'cwe': 'CWE-95'
                }
            ],
            'weak_crypto': [
                {
                    'pattern': r'md5|MD5',
                    'description': 'Weak cryptographic hash (MD5)',
                    'severity': 'medium',
                    'cwe': 'CWE-327'
                },
                {
                    'pattern': r'sha1|SHA1',
                    'description': 'Weak cryptographic hash (SHA1)',
                    'severity': 'medium',
                    'cwe': 'CWE-327'
                },
                {
                    'pattern': r'DES|3DES',
                    'description': 'Weak encryption algorithm',
                    'severity': 'high',
                    'cwe': 'CWE-327'
                }
            ],
            'hardcoded_secrets': [
                {
                    'pattern': r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
                    'description': 'Hardcoded password',
                    'severity': 'critical',
                    'cwe': 'CWE-798'
                },
                {
                    'pattern': r'(?:api[_-]?key|apikey)\s*=\s*["\'][^"\']+["\']',
                    'description': 'Hardcoded API key',
                    'severity': 'critical',
                    'cwe': 'CWE-798'
                },
                {
                    'pattern': r'(?:secret|token)\s*=\s*["\'][^"\']+["\']',
                    'description': 'Hardcoded secret/token',
                    'severity': 'critical',
                    'cwe': 'CWE-798'
                }
            ],
            'cors': [
                {
                    'pattern': r'Access-Control-Allow-Origin.*\*',
                    'description': 'CORS wildcard origin',
                    'severity': 'medium',
                    'cwe': 'CWE-346'
                }
            ],
            'csrf': [
                {
                    'pattern': r'csrf_exempt',
                    'description': 'CSRF protection disabled',
                    'severity': 'high',
                    'cwe': 'CWE-352'
                }
            ]
        }
    
    def _init_sensitive_patterns(self) -> List[re.Pattern]:
        """민감 정보 패턴 초기화"""
        return [
            re.compile(r'[A-Za-z0-9+/]{40}'),  # Base64 encoded secrets
            re.compile(r'(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}'),  # GitHub tokens
            re.compile(r'sk-[A-Za-z0-9]{48}'),  # OpenAI API keys
            re.compile(r'AKIA[0-9A-Z]{16}'),  # AWS Access Key
            re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),  # UUID
            re.compile(r'(?:r|s)k-live-[0-9a-zA-Z]{24,}'),  # Stripe keys
            re.compile(r'sq0csp-[0-9A-Za-z\-_]{43}'),  # Square OAuth
        ]
    
    def _init_unsafe_functions(self) -> Dict[str, List[str]]:
        """안전하지 않은 함수 목록"""
        return {
            'python': [
                'eval', 'exec', 'compile', '__import__',
                'os.system', 'subprocess.call', 'subprocess.Popen',
                'pickle.loads', 'yaml.load', 'input'
            ],
            'javascript': [
                'eval', 'Function', 'setTimeout', 'setInterval',
                'innerHTML', 'outerHTML', 'document.write',
                'document.writeln', 'insertAdjacentHTML'
            ],
            'typescript': [
                'eval', 'Function', 'setTimeout', 'setInterval',
                'innerHTML', 'outerHTML', 'document.write'
            ]
        }
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        보안 스캔 실행
        
        Args:
            input_data: 생성된 코드 및 프로젝트 정보
            
        Returns:
            보안 스캔 결과
        """
        try:
            logger.info("Starting security scan...")
            
            code_files = input_data.get('code_files', {})
            dependencies = input_data.get('dependencies', {})
            config_files = input_data.get('config_files', {})
            
            result = SecurityScanResult()
            
            # 1. 코드 보안 스캔
            code_issues = await self._scan_code_security(code_files)
            result.issues.extend(code_issues)
            
            # 2. 의존성 취약점 스캔
            dep_issues = await self._scan_dependencies(dependencies)
            result.issues.extend(dep_issues)
            
            # 3. 설정 파일 보안 검증
            config_issues = await self._scan_config_security(config_files)
            result.issues.extend(config_issues)
            
            # 4. 민감 정보 노출 검사
            sensitive_issues = await self._scan_sensitive_data(code_files)
            result.issues.extend(sensitive_issues)
            
            # 5. 보안 헤더 검증
            header_issues = await self._check_security_headers(code_files)
            result.issues.extend(header_issues)
            
            # 통계 계산
            result.total_issues = len(result.issues)
            result.critical_count = sum(1 for i in result.issues if i.severity == 'critical')
            result.high_count = sum(1 for i in result.issues if i.severity == 'high')
            result.medium_count = sum(1 for i in result.issues if i.severity == 'medium')
            result.low_count = sum(1 for i in result.issues if i.severity == 'low')
            
            # 보안 점수 계산
            result.security_score = self._calculate_security_score(result)
            
            # 통과 여부 결정
            result.passed = result.critical_count == 0 and result.high_count <= 2
            
            # 권장사항 생성
            result.recommendations = self._generate_recommendations(result)
            
            logger.info(f"Security scan completed. Score: {result.security_score:.1f}/100")
            
            return AgentResult(
                success=True,
                data={
                    'scan_result': result,
                    'security_score': result.security_score,
                    'passed': result.passed,
                    'summary': {
                        'total_issues': result.total_issues,
                        'critical': result.critical_count,
                        'high': result.high_count,
                        'medium': result.medium_count,
                        'low': result.low_count
                    }
                },
                metadata={
                    'agent': self.name,
                    'scan_patterns': len(self.security_patterns),
                    'files_scanned': len(code_files)
                }
            )
            
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                data={}
            )
    
    async def _scan_code_security(self, code_files: Dict[str, str]) -> List[SecurityIssue]:
        """코드 보안 스캔"""
        issues = []
        
        for file_path, content in code_files.items():
            lines = content.split('\n')
            
            # 각 보안 패턴 검사
            for category, patterns in self.security_patterns.items():
                for pattern_info in patterns:
                    pattern = re.compile(pattern_info['pattern'], re.IGNORECASE)
                    
                    for line_num, line in enumerate(lines, 1):
                        if pattern.search(line):
                            issue = SecurityIssue(
                                severity=pattern_info['severity'],
                                type=category,
                                file=file_path,
                                line=line_num,
                                description=pattern_info['description'],
                                recommendation=self._get_recommendation(category),
                                cwe_id=pattern_info.get('cwe'),
                                owasp_category=self._get_owasp_category(category)
                            )
                            issues.append(issue)
            
            # 안전하지 않은 함수 검사
            file_ext = file_path.split('.')[-1]
            language = self._get_language_from_ext(file_ext)
            
            if language in self.unsafe_functions:
                for unsafe_func in self.unsafe_functions[language]:
                    pattern = re.compile(rf'\b{re.escape(unsafe_func)}\b')
                    for line_num, line in enumerate(lines, 1):
                        if pattern.search(line):
                            issue = SecurityIssue(
                                severity='high',
                                type='unsafe_function',
                                file=file_path,
                                line=line_num,
                                description=f'Unsafe function "{unsafe_func}" usage',
                                recommendation=f'Replace {unsafe_func} with a safer alternative',
                                cwe_id='CWE-676'
                            )
                            issues.append(issue)
        
        return issues
    
    async def _scan_dependencies(self, dependencies: Dict[str, Any]) -> List[SecurityIssue]:
        """의존성 취약점 스캔"""
        issues = []
        
        # 알려진 취약한 패키지 버전 (예시)
        vulnerable_packages = {
            'express': {'<4.17.3': 'CVE-2022-24999'},
            'lodash': {'<4.17.21': 'CVE-2021-23337'},
            'axios': {'<0.21.2': 'CVE-2021-3749'},
            'django': {'<3.2.13': 'CVE-2022-28346'},
            'flask': {'<2.2.2': 'CVE-2023-30861'}
        }
        
        for package, version in dependencies.items():
            if package in vulnerable_packages:
                for vuln_version, cve in vulnerable_packages[package].items():
                    # 간단한 버전 비교 (실제로는 더 정교한 비교 필요)
                    if self._is_vulnerable_version(version, vuln_version):
                        issue = SecurityIssue(
                            severity='high',
                            type='vulnerable_dependency',
                            file='package.json',
                            line=0,
                            description=f'{package}@{version} has known vulnerability {cve}',
                            recommendation=f'Update {package} to latest version',
                            cwe_id='CWE-1104'
                        )
                        issues.append(issue)
        
        return issues
    
    async def _scan_config_security(self, config_files: Dict[str, Any]) -> List[SecurityIssue]:
        """설정 파일 보안 검증"""
        issues = []
        
        # 보안 설정 체크리스트
        security_configs = {
            'debug_mode': {'severity': 'high', 'description': 'Debug mode enabled in production'},
            'allow_all_origins': {'severity': 'medium', 'description': 'CORS allows all origins'},
            'no_https': {'severity': 'high', 'description': 'HTTPS not enforced'},
            'weak_session': {'severity': 'medium', 'description': 'Weak session configuration'}
        }
        
        for config_file, config_data in config_files.items():
            if isinstance(config_data, dict):
                # Debug 모드 체크
                if config_data.get('debug', False) or config_data.get('DEBUG', False):
                    issue = SecurityIssue(
                        severity='high',
                        type='insecure_config',
                        file=config_file,
                        line=0,
                        description='Debug mode is enabled',
                        recommendation='Disable debug mode in production',
                        cwe_id='CWE-489'
                    )
                    issues.append(issue)
                
                # CORS 설정 체크
                cors_config = config_data.get('cors', {})
                if cors_config.get('origin') == '*':
                    issue = SecurityIssue(
                        severity='medium',
                        type='insecure_cors',
                        file=config_file,
                        line=0,
                        description='CORS allows all origins',
                        recommendation='Restrict CORS to specific origins',
                        cwe_id='CWE-346'
                    )
                    issues.append(issue)
        
        return issues
    
    async def _scan_sensitive_data(self, code_files: Dict[str, str]) -> List[SecurityIssue]:
        """민감 정보 노출 검사"""
        issues = []
        
        for file_path, content in code_files.items():
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # 민감 정보 패턴 검사
                for pattern in self.sensitive_patterns:
                    if pattern.search(line):
                        # 주석이나 환경변수 참조가 아닌 경우만
                        if not line.strip().startswith('#') and 'process.env' not in line:
                            issue = SecurityIssue(
                                severity='critical',
                                type='sensitive_data_exposure',
                                file=file_path,
                                line=line_num,
                                description='Potential sensitive data exposure',
                                recommendation='Move sensitive data to environment variables',
                                cwe_id='CWE-798'
                            )
                            issues.append(issue)
                            break
        
        return issues
    
    async def _check_security_headers(self, code_files: Dict[str, str]) -> List[SecurityIssue]:
        """보안 헤더 검증"""
        issues = []
        
        # 필수 보안 헤더
        required_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Content-Security-Policy',
            'Strict-Transport-Security',
            'X-XSS-Protection'
        ]
        
        # 서버 설정 파일 찾기
        for file_path, content in code_files.items():
            if 'server' in file_path.lower() or 'app' in file_path.lower():
                for header in required_headers:
                    if header not in content:
                        issue = SecurityIssue(
                            severity='medium',
                            type='missing_security_header',
                            file=file_path,
                            line=0,
                            description=f'Missing security header: {header}',
                            recommendation=f'Add {header} header',
                            cwe_id='CWE-693'
                        )
                        issues.append(issue)
        
        return issues
    
    def _calculate_security_score(self, result: SecurityScanResult) -> float:
        """보안 점수 계산"""
        score = 100.0
        
        # 심각도별 감점
        score -= result.critical_count * 20
        score -= result.high_count * 10
        score -= result.medium_count * 5
        score -= result.low_count * 2
        
        return max(0, score)
    
    def _generate_recommendations(self, result: SecurityScanResult) -> List[str]:
        """보안 권장사항 생성"""
        recommendations = []
        
        if result.critical_count > 0:
            recommendations.append("🚨 즉시 Critical 취약점을 수정하세요")
        
        if result.high_count > 0:
            recommendations.append("⚠️ High 수준 취약점을 우선 처리하세요")
        
        # 카테고리별 권장사항
        issue_types = set(issue.type for issue in result.issues)
        
        if 'sql_injection' in issue_types:
            recommendations.append("💉 Prepared statements 또는 ORM 사용")
        
        if 'xss' in issue_types:
            recommendations.append("🔒 사용자 입력 검증 및 이스케이프 처리")
        
        if 'hardcoded_secrets' in issue_types:
            recommendations.append("🔑 환경 변수 또는 시크릿 관리 서비스 사용")
        
        if 'vulnerable_dependency' in issue_types:
            recommendations.append("📦 의존성을 최신 버전으로 업데이트")
        
        if not result.issues:
            recommendations.append("✅ 보안 검사를 통과했습니다!")
        
        return recommendations
    
    def _get_recommendation(self, category: str) -> str:
        """카테고리별 권장사항"""
        recommendations = {
            'sql_injection': 'Use parameterized queries or ORM',
            'xss': 'Sanitize and escape user input',
            'path_traversal': 'Validate and sanitize file paths',
            'command_injection': 'Avoid shell commands or use safe alternatives',
            'weak_crypto': 'Use strong cryptographic algorithms (SHA-256+)',
            'hardcoded_secrets': 'Use environment variables or secret management',
            'cors': 'Configure CORS with specific origins',
            'csrf': 'Enable CSRF protection'
        }
        return recommendations.get(category, 'Review and fix security issue')
    
    def _get_owasp_category(self, category: str) -> str:
        """OWASP Top 10 카테고리 매핑"""
        owasp_mapping = {
            'sql_injection': 'A03:2021 - Injection',
            'xss': 'A03:2021 - Injection',
            'path_traversal': 'A01:2021 - Broken Access Control',
            'command_injection': 'A03:2021 - Injection',
            'weak_crypto': 'A02:2021 - Cryptographic Failures',
            'hardcoded_secrets': 'A07:2021 - Identification and Authentication Failures',
            'cors': 'A05:2021 - Security Misconfiguration',
            'csrf': 'A01:2021 - Broken Access Control'
        }
        return owasp_mapping.get(category, 'A00:2021 - Other')
    
    def _get_language_from_ext(self, ext: str) -> str:
        """파일 확장자로 언어 판별"""
        ext_mapping = {
            'py': 'python',
            'js': 'javascript',
            'jsx': 'javascript',
            'ts': 'typescript',
            'tsx': 'typescript'
        }
        return ext_mapping.get(ext, 'unknown')
    
    def _is_vulnerable_version(self, current: str, vulnerable: str) -> bool:
        """버전 취약성 체크 (간단한 구현)"""
        # 실제로는 semantic versioning 라이브러리 사용 필요
        if vulnerable.startswith('<'):
            return True  # 간단한 구현
        return False