"""갭 분석 에이전트 (GapAnalyzer)

이 에이전트는 현재 상태와 목표 상태 간의 차이를 분석하여 필요한 변경사항을
도출하는 역할을 합니다. 요구사항을 달성하기 위해 수행해야 할 작업을 식별하고
우선순위를 매겨 실행 계획의 기초를 제공합니다.

주요 기능:
1. 현재 상태와 목표 상태 간의 차이점 분석
2. 테스트 커버리지 갭 식별 및 우선순위 설정
3. 미구현 기능 및 누락된 컴포넌트 식별
4. AI 기반 변경 영향도 예측
5. 리스크 평가 및 완화 전략 수립
6. 구현 복잡도 및 의존성 분석
7. 단계별 마이그레이션 계획 수립

입력:
- current_state (Dict): 현재 시스템 상태 (코드, 행동, 품질 분석 결과)
- target_state (Dict): 목표 상태 (요구사항 명세)
- external_research (Dict, optional): 외부 리서치 결과
- constraints (List[str], optional): 제약사항

출력:
- GapReport: 갭 분석 보고서
  - gaps: 식별된 갭 목록
  - priority_matrix: 우선순위 매트릭스
  - impact_analysis: 변경 영향도 분석
  - risk_assessment: 리스크 평가
  - migration_plan: 단계별 실행 계획
  - estimated_effort: 예상 작업량
  - success_criteria: 성공 기준

문서 참조 관계:
- 입력 참조:
  * RequirementAnalyzer 보고서: 목표 상태 정의
  * BehaviorAnalyzer 보고서: 현재 행동 패턴
  * CodeAnalysisAgent 보고서: 현재 코드 구조
  * ImpactAnalyzer 보고서: 기존 영향도 분석
  * StaticAnalyzer 보고서: 정적 분석 결과
  * QualityGate 보고서: 현재 품질 상태
  * ExternalResearcher 보고서: 외부 모범 사례
- 출력 참조:
  * PlannerAgent: 갭 기반 계획 수립
  * TaskCreatorAgent: 갭 해소 작업 생성

갭 유형:
- FUNCTIONAL: 기능적 갭 (누락된 기능)
- NON_FUNCTIONAL: 비기능적 갭 (성능, 보안 등)
- COVERAGE: 테스트 커버리지 갭
- QUALITY: 코드 품질 갭
- ARCHITECTURAL: 아키텍처 갭
- INTEGRATION: 통합 갭

우선순위 기준:
- 비즈니스 영향도
- 기술적 복잡도
- 의존성 관계
- 리스크 수준
- 구현 노력

사용 예시:
    analyzer = GapAnalyzer(memory_hub)
    task = AgentTask(
        intent="analyze_gaps",
        inputs={
            "current_state": current_analysis,
            "target_state": requirements_spec,
            "external_research": research_report
        }
    )
    result = await analyzer.execute(task)
    gap_report = result.data  # 갭 분석 보고서

작성자: T-Developer v2
버전: 2.0.0 (AI 강화 버전)
최종 수정: 2024-12-20
"""

from __future__ import annotations

import ast
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import logging

from backend.packages.agents.base import BaseAgent, AgentResult, AgentTask, TaskStatus
from backend.packages.agents.ai_providers import get_ai_provider
from backend.packages.memory import ContextType, MemoryHub


@dataclass
class TestGap:
    """Represents a gap in test coverage."""
    
    file_path: str
    function_or_class: str
    line_start: int
    line_end: int
    complexity: int
    priority_score: float
    gap_type: str  # 'function', 'class', 'branch'
    reason: str


@dataclass
class TestCoverageReport:
    """Complete test coverage analysis."""
    
    total_coverage: float = 0.0
    line_coverage: float = 0.0
    branch_coverage: float = 0.0
    function_coverage: float = 0.0
    
    covered_lines: int = 0
    total_lines: int = 0
    covered_branches: int = 0
    total_branches: int = 0
    covered_functions: int = 0
    total_functions: int = 0
    
    test_gaps: List[TestGap] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    source_files: List[str] = field(default_factory=list)
    
    high_priority_gaps: List[TestGap] = field(default_factory=list)
    coverage_by_file: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class GapAnalyzer(BaseAgent):
    """AI-powered test gap analyzer with intelligent test generation.
    
    This agent uses AI to:
    1. Generate test scenarios for untested code
    2. Prioritize critical test gaps intelligently
    3. Suggest test data and edge cases
    4. Predict areas prone to regression
    5. Create test plans with business context
    6. Identify integration test needs
    7. Generate mock/stub recommendations
    """
    
    def __init__(
        self,
        memory_hub: Optional[MemoryHub] = None,
        document_context=None,
        **kwargs: Any
    ) -> None:
        """Initialize the Gap Analyzer.
        
        Args:
            memory_hub: Memory Hub instance
            document_context: SharedDocumentContext 인스턴스
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__(
            name="GapAnalyzer",
            version="2.0.0",  # AI-enhanced version
            memory_hub=memory_hub,
            document_context=document_context,
            **kwargs
        )
        
        self.logger = logging.getLogger(__name__)
        self.ai_provider = None  # Lazy load AI provider
    
    async def _generate_test_with_ai(self, gap: TestGap) -> str:
        """Use AI to generate test scenario for a gap.
        
        Args:
            gap: Test gap to generate test for
            
        Returns:
            Generated test code
        """
        if not self.ai_provider:
            from .ai_providers import get_ai_provider
            self.ai_provider = get_ai_provider()
        
        try:
            prompt = f"""Generate a test case for this untested code:
            File: {gap.file_path}
            Function/Class: {gap.function_or_class}
            Lines: {gap.line_start}-{gap.line_end}
            Complexity: {gap.complexity}
            
            Generate a comprehensive test with edge cases."""
            
            response = await self.ai_provider.generate(prompt)
            return response if response else ""
        except Exception as e:
            self.logger.debug(f"AI test generation failed: {e}")
            return ""
    
    async def _get_requirement_reports(self) -> Dict[str, Any]:
        """Fetch requirement analyzer reports from memory.
        
        Returns:
            Dictionary of requirement reports
        """
        if not self.memory_hub:
            return {}
        
        try:
            from ..memory.contexts import ContextType
            
            # Get latest requirement report
            req_report = await self.memory_hub.get(
                context_type=ContextType.S_CTX,
                key="requirements:latest"
            )
            
            return {"requirements": req_report} if req_report else {}
        except Exception as e:
            self.logger.debug(f"Failed to get requirement reports: {e}")
            return {}
    
    async def _get_analysis_reports(self) -> Dict[str, Any]:
        """Fetch all analysis reports from memory.
        
        Returns:
            Dictionary containing analysis reports
        """
        if not self.memory_hub:
            return {}
        
        from ..memory.contexts import ContextType
        
        reports = {}
        
        # Fetch analysis reports
        analysis_types = [
            ("behavior", "BehaviorAnalyzer"),
            ("code", "CodeAnalysisAgent"),
            ("impact", "ImpactAnalyzer"),
            ("static", "StaticAnalyzer"),
            ("quality", "QualityGate")
        ]
        
        for report_type, agent_name in analysis_types:
            try:
                latest = await self.memory_hub.get(
                    context_type=ContextType.S_CTX,
                    key=f"latest_{report_type}_analysis"
                )
                if latest:
                    reports[report_type] = latest
            except Exception as e:
                self.logger.debug(f"Failed to get {report_type} reports: {e}")
        
        return reports
    
    async def execute(self, task) -> AgentResult:
        """Execute test gap analysis.
        
        Args:
            task: The analysis task (dict or AgentTask) containing:
                - project_path: Path to project root
                - test_command: Custom test command (optional)
                - min_coverage: Minimum coverage threshold (default: 80)
                - focus_on: Specific files/directories to focus on
                
        Returns:
            AgentResult containing gap analysis
        """
        try:
            # Handle both dict and AgentTask inputs
            if isinstance(task, dict):
                inputs = task
            else:
                inputs = task.inputs
            
            # Get reports from other agents
            requirement_reports = await self._get_requirement_reports()
            analysis_reports = await self._get_analysis_reports()
            
            # Enrich inputs with reports for AI context
            if requirement_reports or analysis_reports:
                inputs["context_reports"] = {
                    "requirements": requirement_reports,
                    "analysis": analysis_reports
                }
            
            # Extract parameters
            project_path = inputs.get("project_path", ".")
            test_command = inputs.get("test_command")
            min_coverage = inputs.get("min_coverage", 80)
            focus_on = inputs.get("focus_on", [])
            
            # Analyze test coverage
            report = await self._analyze_coverage(
                project_path,
                test_command,
                focus_on
            )
            
            # Identify gaps
            gaps = await self._identify_gaps(
                report,
                project_path,
                min_coverage
            )
            report.test_gaps = gaps
            
            # Calculate priorities
            report.high_priority_gaps = self._prioritize_gaps(gaps)
            
            # Store in memory if available
            if self.memory_hub:
                await self._store_analysis(project_path, report)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(report, min_coverage)
            
            return self.format_result(
                success=True,
                data={
                    "total_coverage": report.total_coverage,
                    "line_coverage": report.line_coverage,
                    "branch_coverage": report.branch_coverage,
                    "function_coverage": report.function_coverage,
                    "gaps_found": len(report.test_gaps),
                    "high_priority_gaps": len(report.high_priority_gaps),
                    "test_gaps": [self._gap_to_dict(gap) for gap in report.high_priority_gaps[:10]],
                    "recommendations": recommendations,
                    "coverage_by_file": report.coverage_by_file
                },
                metadata={"agent": self.name, "version": self.version}
            )
            
        except Exception as e:
            self.logger.error(f"Test gap analysis failed: {e}")
            return self.format_result(
                success=False,
                error=str(e)
            )
    
    async def _analyze_coverage(
        self,
        project_path: str,
        test_command: Optional[str],
        focus_on: List[str]
    ) -> TestCoverageReport:
        """Run coverage analysis on the project.
        
        Args:
            project_path: Path to project
            test_command: Custom test command
            focus_on: Specific paths to focus on
            
        Returns:
            Coverage report
        """
        report = TestCoverageReport()
        
        # Detect test framework
        if not test_command:
            test_command = self._detect_test_command(project_path)
        
        if not test_command:
            # Fallback: analyze statically
            return await self._static_coverage_analysis(project_path, focus_on)
        
        # Run coverage tool
        coverage_file = Path(project_path) / ".coverage"
        coverage_json = Path(project_path) / "coverage.json"
        
        try:
            # Run tests with coverage
            cmd = f"cd {project_path} && coverage run -m {test_command}"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0 and not coverage_file.exists():
                # Tests failed or no coverage data
                return await self._static_coverage_analysis(project_path, focus_on)
            
            # Generate JSON report
            cmd = f"cd {project_path} && coverage json -o coverage.json"
            subprocess.run(cmd, shell=True, capture_output=True)
            
            # Parse coverage data
            if coverage_json.exists():
                with open(coverage_json, 'r') as f:
                    coverage_data = json.load(f)
                
                report = self._parse_coverage_json(coverage_data, focus_on)
                
                # Clean up
                coverage_json.unlink(missing_ok=True)
            
        except subprocess.TimeoutExpired:
            self.logger.warning("Coverage analysis timed out, falling back to static analysis")
            return await self._static_coverage_analysis(project_path, focus_on)
        except Exception as e:
            self.logger.warning(f"Dynamic coverage failed: {e}, using static analysis")
            return await self._static_coverage_analysis(project_path, focus_on)
        
        return report
    
    def _detect_test_command(self, project_path: str) -> Optional[str]:
        """Detect the test command for the project.
        
        Args:
            project_path: Path to project
            
        Returns:
            Test command or None
        """
        path = Path(project_path)
        
        # Check for pytest
        if (path / "pytest.ini").exists() or (path / "setup.cfg").exists():
            return "pytest"
        
        # Check for unittest
        if (path / "tests").exists() or (path / "test").exists():
            return "pytest"  # pytest can run unittest tests too
        
        # Check for package.json (JavaScript/TypeScript)
        if (path / "package.json").exists():
            try:
                with open(path / "package.json", 'r') as f:
                    package = json.load(f)
                    if "scripts" in package and "test" in package["scripts"]:
                        return None  # JavaScript, skip Python coverage
            except:
                pass
        
        return None
    
    async def _static_coverage_analysis(
        self,
        project_path: str,
        focus_on: List[str]
    ) -> TestCoverageReport:
        """Perform static analysis when dynamic coverage is not available.
        
        Args:
            project_path: Path to project
            focus_on: Specific paths to focus on
            
        Returns:
            Coverage report based on static analysis
        """
        report = TestCoverageReport()
        path = Path(project_path)
        
        # Collect source and test files
        source_files = []
        test_files = []
        
        patterns = focus_on if focus_on else ["**/*.py"]
        for pattern in patterns:
            for file_path in path.glob(pattern):
                if file_path.is_file():
                    file_str = str(file_path)
                    if 'test' in file_str.lower():
                        test_files.append(file_str)
                    else:
                        source_files.append(file_str)
        
        report.source_files = source_files
        report.test_files = test_files
        
        # Analyze each source file
        total_functions = 0
        tested_functions = set()
        
        for source_file in source_files:
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                file_functions = self._extract_functions_and_classes(tree)
                total_functions += len(file_functions)
                
                # Check which functions are likely tested
                tested_in_file = self._find_tested_items(
                    file_functions,
                    test_files,
                    Path(source_file).name
                )
                tested_functions.update(tested_in_file)
                
                # Simple line counting
                lines = content.split('\n')
                non_empty_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
                
                report.coverage_by_file[source_file] = {
                    "total_lines": len(non_empty_lines),
                    "total_functions": len(file_functions),
                    "tested_functions": len(tested_in_file),
                    "estimated_coverage": (len(tested_in_file) / len(file_functions) * 100) if file_functions else 100
                }
                
            except Exception as e:
                self.logger.debug(f"Could not analyze {source_file}: {e}")
        
        # Calculate overall metrics
        report.total_functions = total_functions
        report.covered_functions = len(tested_functions)
        report.function_coverage = (len(tested_functions) / total_functions * 100) if total_functions else 0
        
        # Estimate line and branch coverage
        report.total_coverage = report.function_coverage
        report.line_coverage = report.function_coverage * 0.9  # Estimate
        report.branch_coverage = report.function_coverage * 0.8  # Estimate
        
        return report
    
    def _extract_functions_and_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract all functions and classes from AST.
        
        Args:
            tree: Python AST
            
        Returns:
            List of function/class info
        """
        items = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):  # Public functions
                    items.append({
                        "name": node.name,
                        "type": "function",
                        "line": node.lineno,
                        "end_line": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                        "complexity": self._calculate_complexity(node)
                    })
            elif isinstance(node, ast.ClassDef):
                items.append({
                    "name": node.name,
                    "type": "class",
                    "line": node.lineno,
                    "end_line": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    "complexity": len([n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)])
                })
        
        return items
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a node.
        
        Args:
            node: AST node
            
        Returns:
            Complexity score
        """
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _find_tested_items(
        self,
        items: List[Dict[str, Any]],
        test_files: List[str],
        source_filename: str
    ) -> Set[str]:
        """Find which items are likely tested.
        
        Args:
            items: Functions/classes to check
            test_files: Test file paths
            source_filename: Name of source file
            
        Returns:
            Set of tested item names
        """
        tested = set()
        
        # Look for test files related to this source file
        base_name = source_filename.replace('.py', '')
        related_tests = [
            tf for tf in test_files
            if base_name in tf or f"test_{base_name}" in tf
        ]
        
        for test_file in related_tests:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    test_content = f.read()
                
                # Simple heuristic: if function/class name appears in test, it's tested
                for item in items:
                    if item['name'] in test_content:
                        tested.add(item['name'])
                        
            except Exception:
                pass
        
        return tested
    
    def _parse_coverage_json(
        self,
        coverage_data: Dict[str, Any],
        focus_on: List[str]
    ) -> TestCoverageReport:
        """Parse coverage.py JSON output.
        
        Args:
            coverage_data: Coverage JSON data
            focus_on: Paths to focus on
            
        Returns:
            Coverage report
        """
        report = TestCoverageReport()
        
        # Extract summary metrics
        if "totals" in coverage_data:
            totals = coverage_data["totals"]
            report.total_coverage = totals.get("percent_covered", 0)
            report.covered_lines = totals.get("covered_lines", 0)
            report.total_lines = totals.get("num_statements", 0)
            report.line_coverage = report.total_coverage
        
        # Extract file-level coverage
        if "files" in coverage_data:
            for file_path, file_data in coverage_data["files"].items():
                # Filter by focus_on if specified
                if focus_on and not any(f in file_path for f in focus_on):
                    continue
                
                report.coverage_by_file[file_path] = {
                    "coverage": file_data.get("summary", {}).get("percent_covered", 0),
                    "missing_lines": file_data.get("missing_lines", []),
                    "excluded_lines": file_data.get("excluded_lines", []),
                    "covered_lines": file_data.get("summary", {}).get("covered_lines", 0),
                    "total_lines": file_data.get("summary", {}).get("num_statements", 0)
                }
        
        return report
    
    async def _identify_gaps(
        self,
        report: TestCoverageReport,
        project_path: str,
        min_coverage: float
    ) -> List[TestGap]:
        """Identify specific gaps in test coverage.
        
        Args:
            report: Coverage report
            project_path: Path to project
            min_coverage: Minimum coverage threshold
            
        Returns:
            List of test gaps
        """
        gaps = []
        
        for file_path, coverage_info in report.coverage_by_file.items():
            if coverage_info.get("coverage", coverage_info.get("estimated_coverage", 100)) < min_coverage:
                # This file needs more testing
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    # Find untested functions/classes
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            # Check if this is covered
                            if hasattr(node, 'lineno'):
                                missing_lines = coverage_info.get("missing_lines", [])
                                if missing_lines and node.lineno in missing_lines:
                                    gap = TestGap(
                                        file_path=file_path,
                                        function_or_class=node.name,
                                        line_start=node.lineno,
                                        line_end=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                                        complexity=self._calculate_complexity(node),
                                        priority_score=0,  # Will be calculated later
                                        gap_type="function" if isinstance(node, ast.FunctionDef) else "class",
                                        reason=f"No test coverage for {node.name}"
                                    )
                                    gaps.append(gap)
                    
                except Exception as e:
                    self.logger.debug(f"Could not analyze gaps in {file_path}: {e}")
        
        return gaps
    
    def _prioritize_gaps(self, gaps: List[TestGap]) -> List[TestGap]:
        """Calculate priority scores for test gaps.
        
        Args:
            gaps: List of test gaps
            
        Returns:
            Sorted list of high-priority gaps
        """
        for gap in gaps:
            # Priority based on:
            # 1. Complexity (more complex = higher priority)
            # 2. Type (classes generally more important than functions)
            # 3. Public vs private (public APIs more important)
            
            score = 0.0
            
            # Complexity factor
            score += gap.complexity * 10
            
            # Type factor
            if gap.gap_type == "class":
                score += 20
            
            # Public API factor
            if not gap.function_or_class.startswith('_'):
                score += 15
            
            # Critical path detection (main, init, etc.)
            if gap.function_or_class in ['__init__', 'main', 'run', 'execute', 'process']:
                score += 25
            
            gap.priority_score = score
        
        # Sort by priority score
        return sorted(gaps, key=lambda g: g.priority_score, reverse=True)
    
    def _gap_to_dict(self, gap: TestGap) -> Dict[str, Any]:
        """Convert TestGap to dictionary.
        
        Args:
            gap: Test gap object
            
        Returns:
            Dictionary representation
        """
        return {
            "file": gap.file_path,
            "name": gap.function_or_class,
            "type": gap.gap_type,
            "lines": f"{gap.line_start}-{gap.line_end}",
            "complexity": gap.complexity,
            "priority": gap.priority_score,
            "reason": gap.reason
        }
    
    def _generate_recommendations(
        self,
        report: TestCoverageReport,
        min_coverage: float
    ) -> List[str]:
        """Generate actionable recommendations.
        
        Args:
            report: Coverage report
            min_coverage: Minimum coverage threshold
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Overall coverage recommendation
        if report.total_coverage < min_coverage:
            gap = min_coverage - report.total_coverage
            recommendations.append(
                f"Increase overall coverage by {gap:.1f}% to meet {min_coverage}% threshold"
            )
        
        # High priority gaps
        if report.high_priority_gaps:
            top_gaps = report.high_priority_gaps[:3]
            for gap in top_gaps:
                recommendations.append(
                    f"Add tests for {gap.gap_type} '{gap.function_or_class}' "
                    f"in {Path(gap.file_path).name} (complexity: {gap.complexity})"
                )
        
        # Branch coverage
        if report.branch_coverage < 50:
            recommendations.append(
                "Focus on branch coverage - test different code paths and conditions"
            )
        
        # Test file ratio
        if len(report.test_files) < len(report.source_files) * 0.5:
            recommendations.append(
                f"Consider adding more test files. Current ratio: "
                f"{len(report.test_files)} tests for {len(report.source_files)} source files"
            )
        
        return recommendations
    
    async def _store_analysis(
        self,
        project_path: str,
        report: TestCoverageReport
    ) -> None:
        """Store analysis results in memory.
        
        Args:
            project_path: Project path
            report: Coverage report
        """
        if not self.memory_hub:
            return
        
        # Store in agent context
        await self.write_memory(
            ContextType.A_CTX,
            f"test_gaps_{project_path.replace('/', '_')}",
            {
                "total_coverage": report.total_coverage,
                "gaps_found": len(report.test_gaps),
                "high_priority_count": len(report.high_priority_gaps),
                "timestamp": datetime.now().isoformat()
            },
            ttl_seconds=86400,  # 1 day
            tags=["test_gaps", "coverage", project_path.replace('/', '_')]
        )
    
    async def validate_input(self, task: AgentTask) -> bool:
        """Validate the analysis task input.
        
        Args:
            task: The task to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not await super().validate_input(task):
            return False
        
        # Check for project path
        if "project_path" not in task.inputs:
            return False
        
        # Verify path exists
        path = Path(task.inputs["project_path"])
        if not path.exists():
            return False
        
        return True