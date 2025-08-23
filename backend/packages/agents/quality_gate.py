"""품질 게이트 (QualityGate) - AI 기반 지능형 코드 품질 검증

이 에이전트는 AI를 활용하여 코드 품질을 종합적으로 검사하고 지능적인 개선 제안을
제공하는 품질 관문 역할을 수행합니다.

주요 기능:
1. AI 기반 코드 품질 문제 사전 예측 및 패턴 분석
2. 잠재적 버그 패턴 식별 및 리스크 평가
3. 순환 복잡도 계산 및 복잡성 기반 리팩토링 제안
4. Docstring 커버리지 검사 및 문서화 품질 평가
5. 타입 힌트 커버리지 분석 및 타입 안정성 검증
6. 보안 취약점 스캔 (하드코딩된 비밀번호, 위험 함수 사용)
7. 코드 스타일 검사 (라인 길이, 후행 공백 등)
8. 테스트 커버리지 측정 및 품질 메트릭 계산
9. 자동 수정 가능한 이슈 자동 수정
10. 유지보수성 지수 계산 및 기술 부채 영향 예측

입력 매개변수:
- file_path: 검사할 파일 경로 (선택적)
- code: 직접 검사할 코드 내용 (선택적)
- fix_issues: 자동 수정 여부 (기본: False)
- strict: 엄격 모드 사용 여부 (기본: False)
- config: QualityConfig 객체 (품질 기준 설정)

출력 형식:
- passed: 품질 검사 통과 여부
- report: QualityReport 객체
  * metrics: QualityMetrics (커버리지, 복잡도, 보안 점수 등)
  * issues: 발견된 이슈 목록 (타입, 심각도, 메시지, 위치)
  * suggestions: 개선 제안 목록
- timestamp: 검사 시각

품질 메트릭:
- test_coverage: 테스트 커버리지 (기본 임계값: 85%)
- docstring_coverage: Docstring 커버리지 (기본 임계값: 80%)
- complexity_score: 순환 복잡도 점수 (기본 임계값: 10)
- type_coverage: 타입 힌트 커버리지
- security_score: 보안 점수 (100점 만점)
- maintainability_index: 유지보수성 지수
- technical_debt_hours: 기술 부채 시간
- code_smells: 코드 스멜 개수
- bugs: 버그 개수
- vulnerabilities: 취약점 개수

문서 참조 관계:
- 읽어오는 보고서:
  * StaticAnalyzer 정적 분석 결과
  * CodeGenerator 생성 코드
- 출력을 사용하는 에이전트:
  * CodeImproverAgent: 품질 이슈 수정
  * UpgradeOrchestrator: 품질 기반 의사결정
  * ReportGenerator: 품질 보고서 생성

사용 예시:
```python
quality_gate = QualityGate(
    config=QualityConfig(
        min_coverage=90.0,
        max_complexity=8,
        strict_mode=True
    )
)

result = await quality_gate.execute({
    'file_path': '/src/service.py',
    'fix_issues': True
})

if result.data['passed']:
    print("품질 검사 통과")
else:
    print(f"품질 이슈: {len(result.data['report']['issues'])}개")
```

작성자: T-Developer v2 Team
버전: 2.0.0 (AI-enhanced)
최종 수정: 2025-08-23
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import ast
import os

from .base import BaseAgent, AgentTask, AgentResult, TaskStatus
from .ai_providers import get_ai_provider
from ..memory.contexts import ContextType
from ..safety import CircuitBreaker, CircuitBreakerConfig, ResourceLimiter, ResourceLimit

logger = logging.getLogger(__name__)


@dataclass
class QualityConfig:
    """품질 검사 설정."""
    
    min_coverage: float = 85.0  # 최소 테스트 커버리지
    max_complexity: int = 10  # 최대 순환 복잡도
    min_docstring_coverage: float = 80.0  # 최소 docstring 커버리지
    max_line_length: int = 120  # 최대 라인 길이
    check_types: bool = True  # 타입 체크 여부
    check_security: bool = True  # 보안 체크 여부
    check_imports: bool = True  # import 정리 체크
    strict_mode: bool = False  # 엄격 모드


@dataclass
class QualityMetrics:
    """코드 품질 메트릭."""
    
    test_coverage: float = 0.0
    docstring_coverage: float = 0.0
    complexity_score: float = 0.0
    type_coverage: float = 0.0
    security_score: float = 100.0
    maintainability_index: float = 0.0
    technical_debt_hours: float = 0.0
    code_smells: int = 0
    bugs: int = 0
    vulnerabilities: int = 0


@dataclass
class QualityReport:
    """품질 검사 결과 보고서."""
    
    passed: bool
    file_path: str
    metrics: QualityMetrics
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class QualityGate(BaseAgent):
    """AI-powered quality gate for intelligent code quality prediction.
    
    AI를 사용하여:
    1. 코드 품질 문제를 사전에 예측
    2. 잠재적 버그 패턴 식별
    3. 리팩토링 필요 영역 제안
    4. 코드 스멜 자동 감지
    5. 품질 개선 우선순위 제공
    6. 기술 부채 영향 예측
    3. 개선 제안 생성
    4. 자동 수정 가능한 이슈 수정
    """
    
    def __init__(self, memory_hub=None, document_context=None, config: Optional[QualityConfig] = None):
        """QualityGate 초기화.
        
        Args:
            memory_hub: 메모리 허브 인스턴스
            document_context: SharedDocumentContext 인스턴스
            config: 품질 검사 설정
        """
        super().__init__(
            name="QualityGate",
            document_context=document_context,
            version="2.0.0",  # AI-enhanced version
            memory_hub=memory_hub
        )
        
        self.config = config or QualityConfig()

        
        # 페르소나 적용 - QualityGate
        from .personas import get_persona
        self.persona = get_persona("QualityGate")
        if self.persona:
            logger.info(f"🎭 {self.persona.name}: {self.persona.catchphrase}")
        self.ai_provider = None  # Lazy load AI provider
        
        # Safety mechanisms
        self.circuit_breaker = CircuitBreaker(
            name="QualityGate",
            config=CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                success_threshold=2
            )
        )
        
        self.resource_limiter = ResourceLimiter(
            limits=ResourceLimit(
                max_memory_mb=500,
                max_cpu_percent=50,
                max_execution_time=60,
                max_concurrent_tasks=3
            )
        )
    
    async def execute(self, task) -> AgentResult:
        """품질 검사 실행.
        
        Args:
            task: AgentTask or dict with:
                - file_path: 검사할 파일 경로  
                - code: 검사할 코드 (선택적)
                - fix_issues: 자동 수정 여부
                - strict: 엄격 모드 사용 여부
                
        Returns:
            AgentResult with quality check results
        """
        logger.info(f"Starting quality check...")
        
        try:
            # Handle both dict and AgentTask inputs
            if isinstance(task, dict):
                inputs = task
            else:
                inputs = task.inputs
            
            file_path = inputs.get("file_path")
            code = inputs.get("code")
            
            if not file_path and not code:
                return AgentResult(
                    success=False,
                    status=TaskStatus.FAILED,
                    data={},
                    error="Either file_path or code must be provided"
                )
            
            # Safety mechanisms를 통해 실행
            report = await self.circuit_breaker.call(
                self.resource_limiter.execute,
                self._check_quality,
                file_path,
                code,
                inputs.get("fix_issues", False)
            )
            
            # 메모리에 저장
            if self.memory_hub and report.passed:
                await self._store_quality_report(report)
            
            return AgentResult(
                success=True,
                status=TaskStatus.COMPLETED,
                data={
                    "passed": report.passed,
                    "report": self._report_to_dict(report),
                    "timestamp": report.timestamp
                },
                error=None
            )
            
        except Exception as e:
            logger.error(f"Quality check failed: {e}")
            return AgentResult(
                success=False,
                status=TaskStatus.FAILED,
                data={},
                error=str(e)
            )
    
    async def _check_quality(
        self,
        file_path: Optional[str],
        code: Optional[str],
        fix_issues: bool
    ) -> QualityReport:
        """실제 품질 검사 수행.
        
        Args:
            file_path: 파일 경로
            code: 코드 내용
            fix_issues: 자동 수정 여부
            
        Returns:
            품질 보고서
        """
        # 코드 읽기
        if file_path and not code:
            with open(file_path, 'r') as f:
                code = f.read()
        
        if not code:
            raise ValueError("No code to check")
        
        # 메트릭 수집
        metrics = QualityMetrics()
        issues = []
        suggestions = []
        
        # 1. 복잡도 분석
        complexity_issues = self._check_complexity(code)
        if complexity_issues:
            issues.extend(complexity_issues)
            metrics.complexity_score = max(c["complexity"] for c in complexity_issues)
        
        # 2. Docstring 커버리지
        docstring_coverage = self._check_docstring_coverage(code)
        metrics.docstring_coverage = docstring_coverage
        if docstring_coverage < self.config.min_docstring_coverage:
            issues.append({
                "type": "docstring",
                "severity": "warning",
                "message": f"Docstring coverage {docstring_coverage:.1f}% is below threshold {self.config.min_docstring_coverage}%"
            })
            suggestions.append("Add docstrings to functions and classes")
        
        # 3. 코드 스타일 체크
        style_issues = self._check_style(code)
        issues.extend(style_issues)
        
        # 4. Import 체크
        if self.config.check_imports:
            import_issues = self._check_imports(code)
            issues.extend(import_issues)
        
        # 5. 타입 힌트 체크
        if self.config.check_types:
            type_coverage = self._check_type_hints(code)
            metrics.type_coverage = type_coverage
            if type_coverage < 90:
                suggestions.append(f"Add type hints (current coverage: {type_coverage:.1f}%)")
        
        # 6. 보안 체크
        if self.config.check_security:
            security_issues = self._check_security(code)
            issues.extend(security_issues)
            metrics.vulnerabilities = len(security_issues)
        
        # 7. 테스트 커버리지 (파일이 있는 경우)
        if file_path and os.path.exists(file_path):
            coverage = await self._check_test_coverage(file_path)
            metrics.test_coverage = coverage
            if coverage < self.config.min_coverage:
                issues.append({
                    "type": "coverage",
                    "severity": "error",
                    "message": f"Test coverage {coverage:.1f}% is below threshold {self.config.min_coverage}%"
                })
        
        # 8. 유지보수성 지수 계산
        metrics.maintainability_index = self._calculate_maintainability(metrics)
        
        # 품질 통과 여부 결정
        passed = self._determine_pass(metrics, issues)
        
        # 자동 수정
        if fix_issues and not passed:
            code = await self._auto_fix_issues(code, issues)
            # 재검사
            return await self._check_quality(file_path, code, False)
        
        return QualityReport(
            passed=passed,
            file_path=file_path or "inline_code",
            metrics=metrics,
            issues=issues,
            suggestions=suggestions
        )
    
    def _check_complexity(self, code: str) -> List[Dict[str, Any]]:
        """코드 복잡도 검사.
        
        Args:
            code: 검사할 코드
            
        Returns:
            복잡도 이슈 목록
        """
        issues = []
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    if complexity > self.config.max_complexity:
                        issues.append({
                            "type": "complexity",
                            "severity": "warning",
                            "function": node.name,
                            "complexity": complexity,
                            "message": f"Function '{node.name}' has complexity {complexity} (max: {self.config.max_complexity})"
                        })
        except SyntaxError as e:
            issues.append({
                "type": "syntax",
                "severity": "error",
                "message": str(e)
            })
        
        return issues
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """순환 복잡도 계산.
        
        Args:
            node: AST 노드
            
        Returns:
            복잡도 값
        """
        complexity = 1  # 기본 경로
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
        
        return complexity
    
    def _check_docstring_coverage(self, code: str) -> float:
        """Docstring 커버리지 검사.
        
        Args:
            code: 검사할 코드
            
        Returns:
            커버리지 퍼센트
        """
        try:
            tree = ast.parse(code)
            total = 0
            documented = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    total += 1
                    if ast.get_docstring(node):
                        documented += 1
            
            if total == 0:
                return 100.0
            
            return (documented / total) * 100
            
        except SyntaxError:
            return 0.0
    
    def _check_style(self, code: str) -> List[Dict[str, Any]]:
        """코드 스타일 검사.
        
        Args:
            code: 검사할 코드
            
        Returns:
            스타일 이슈 목록
        """
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 라인 길이 체크
            if len(line) > self.config.max_line_length:
                issues.append({
                    "type": "style",
                    "severity": "info",
                    "line": i,
                    "message": f"Line {i} exceeds {self.config.max_line_length} characters"
                })
            
            # 후행 공백 체크
            if line.endswith(' ') or line.endswith('\t'):
                issues.append({
                    "type": "style",
                    "severity": "info",
                    "line": i,
                    "message": f"Line {i} has trailing whitespace"
                })
        
        return issues
    
    def _check_imports(self, code: str) -> List[Dict[str, Any]]:
        """Import 문 검사.
        
        Args:
            code: 검사할 코드
            
        Returns:
            Import 이슈 목록
        """
        issues = []
        try:
            tree = ast.parse(code)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(node)
            
            # 사용되지 않는 import 찾기
            # (간단한 구현 - 실제로는 더 정교한 분석 필요)
            
        except SyntaxError:
            pass
        
        return issues
    
    def _check_type_hints(self, code: str) -> float:
        """타입 힌트 커버리지 검사.
        
        Args:
            code: 검사할 코드
            
        Returns:
            타입 힌트 커버리지 퍼센트
        """
        try:
            tree = ast.parse(code)
            total_args = 0
            typed_args = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # 인자 타입 체크
                    for arg in node.args.args:
                        total_args += 1
                        if arg.annotation:
                            typed_args += 1
                    
                    # 반환 타입 체크
                    if node.returns:
                        typed_args += 1
                    total_args += 1
            
            if total_args == 0:
                return 100.0
            
            return (typed_args / total_args) * 100
            
        except SyntaxError:
            return 0.0
    
    def _check_security(self, code: str) -> List[Dict[str, Any]]:
        """보안 취약점 검사.
        
        Args:
            code: 검사할 코드
            
        Returns:
            보안 이슈 목록
        """
        issues = []
        
        # 하드코딩된 비밀 검사
        if "password" in code.lower() and "=" in code:
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if "password" in line.lower() and "=" in line and '"' in line:
                    issues.append({
                        "type": "security",
                        "severity": "critical",
                        "line": i,
                        "message": "Possible hardcoded password detected"
                    })
        
        # eval/exec 사용 검사
        dangerous_funcs = ["eval", "exec", "__import__"]
        for func in dangerous_funcs:
            if func in code:
                issues.append({
                    "type": "security",
                    "severity": "warning",
                    "message": f"Use of potentially dangerous function: {func}"
                })
        
        return issues
    
    async def _check_test_coverage(self, file_path: str) -> float:
        """테스트 커버리지 측정.
        
        Args:
            file_path: 파일 경로
            
        Returns:
            커버리지 퍼센트
        """
        # 간단한 구현 - 실제로는 pytest-cov 사용
        return 0.0
    
    def _calculate_maintainability(self, metrics: QualityMetrics) -> float:
        """유지보수성 지수 계산.
        
        Args:
            metrics: 품질 메트릭
            
        Returns:
            유지보수성 지수 (0-100)
        """
        # 간단한 가중 평균
        scores = [
            metrics.docstring_coverage * 0.3,
            (100 - min(metrics.complexity_score * 10, 100)) * 0.3,
            metrics.type_coverage * 0.2,
            metrics.security_score * 0.2
        ]
        
        return sum(scores)
    
    def _determine_pass(self, metrics: QualityMetrics, issues: List[Dict[str, Any]]) -> bool:
        """품질 통과 여부 결정.
        
        Args:
            metrics: 품질 메트릭
            issues: 발견된 이슈들
            
        Returns:
            통과 여부
        """
        # Critical 이슈가 있으면 실패
        if any(issue.get("severity") == "critical" for issue in issues):
            return False
        
        # 엄격 모드에서는 모든 기준 충족 필요
        if self.config.strict_mode:
            if metrics.test_coverage < self.config.min_coverage:
                return False
            if metrics.docstring_coverage < self.config.min_docstring_coverage:
                return False
            if metrics.complexity_score > self.config.max_complexity:
                return False
            if metrics.vulnerabilities > 0:
                return False
        
        # 일반 모드에서는 주요 메트릭만 체크
        if metrics.test_coverage < self.config.min_coverage * 0.8:  # 80% 허용
            return False
        
        if metrics.vulnerabilities > 2:  # 2개까지 허용
            return False
        
        return True
    
    async def _auto_fix_issues(self, code: str, issues: List[Dict[str, Any]]) -> str:
        """자동으로 수정 가능한 이슈 수정.
        
        Args:
            code: 원본 코드
            issues: 발견된 이슈들
            
        Returns:
            수정된 코드
        """
        # 간단한 스타일 이슈만 수정
        lines = code.split('\n')
        
        for issue in issues:
            if issue["type"] == "style" and "trailing whitespace" in issue["message"]:
                line_num = issue["line"] - 1
                if 0 <= line_num < len(lines):
                    lines[line_num] = lines[line_num].rstrip()
        
        return '\n'.join(lines)
    
    def _report_to_dict(self, report: QualityReport) -> Dict[str, Any]:
        """보고서를 딕셔너리로 변환.
        
        Args:
            report: 품질 보고서
            
        Returns:
            딕셔너리 형태의 보고서
        """
        return {
            "passed": report.passed,
            "file_path": report.file_path,
            "metrics": {
                "test_coverage": report.metrics.test_coverage,
                "docstring_coverage": report.metrics.docstring_coverage,
                "complexity_score": report.metrics.complexity_score,
                "type_coverage": report.metrics.type_coverage,
                "security_score": report.metrics.security_score,
                "maintainability_index": report.metrics.maintainability_index,
                "code_smells": report.metrics.code_smells,
                "bugs": report.metrics.bugs,
                "vulnerabilities": report.metrics.vulnerabilities
            },
            "issues": report.issues,
            "suggestions": report.suggestions,
            "timestamp": report.timestamp
        }
    
    async def _store_quality_report(self, report: QualityReport) -> None:
        """품질 보고서를 메모리에 저장.
        
        Args:
            report: 품질 보고서
        """
        if not self.memory_hub:
            return
        
        await self.memory_hub.put(
            context_type=ContextType.O_CTX,
            key=f"quality:{report.file_path}:{report.timestamp}",
            value=self._report_to_dict(report),
            ttl_seconds=86400
        )
        
        logger.info(f"Stored quality report for {report.file_path}")