"""영향도 분석 에이전트 (ImpactAnalyzer)

이 에이전트는 코드 변경이 시스템 전체에 미치는 영향을 분석하고 예측하는 
역할을 합니다. 의존성 매트릭스를 생성하고 변경의 파급 효과를 평가하여
안전한 구현을 지원합니다.

주요 기능:
1. 변경 영향도 분석 및 예측
2. 의존성 매트릭스 생성 및 시각화
3. 직접/간접 영향 범위 식별
4. 리스크 레벨 평가 및 분류
5. 다운스트림 영향 분석
6. 순환 의존성 감지
7. 단일 장애점(SPOF) 식별
8. 기술 부채 평가

입력:
- changes (List[Dict]): 변경 사항 목록
- codebase_analysis (Dict): 코드베이스 분석 결과
- test_coverage (Dict, optional): 테스트 커버리지 정보
- historical_data (Dict, optional): 과거 변경 이력

출력:
- ImpactReport: 영향도 분석 보고서
  - change_impacts: 각 변경의 영향도
  - dependency_matrix: 의존성 매트릭스
  - risk_assessment: 리스크 평가
  - blast_radius: 영향 범위
  - recommendations: 권장사항
  - system_report: 시스템 전체 보고서

문서 참조 관계:
- 입력 참조:
  * CodeAnalysisAgent 보고서: 코드 구조 정보
  * BehaviorAnalyzer 보고서: 행동 패턴 정보
  * StaticAnalyzer 보고서: 정적 분석 결과
  * QualityGate 보고서: 품질 메트릭
- 출력 참조:
  * ExternalResearcher: 영향도 기반 리서치
  * GapAnalyzer: 영향도 기반 갭 분석
  * PlannerAgent: 영향도 고려 계획 수립

영향 유형:
- DIRECT: 직접적 영향 (호출/참조)
- INDIRECT: 간접적 영향 (전이적 의존성)
- TEST: 테스트 영향
- DOWNSTREAM: 다운스트림 영향
- RUNTIME: 런타임 영향

리스크 레벨:
- CRITICAL: 핵심 기능 영향, 즉시 조치 필요
- HIGH: 주요 기능 영향, 신중한 검토 필요
- MEDIUM: 일반 기능 영향, 표준 검토 필요
- LOW: 제한적 영향, 기본 검토

분석 기법:
- 정적 의존성 분석
- 동적 호출 그래프 분석
- 데이터 흐름 분석
- 제어 흐름 분석
- 클러스터링 분석

사용 예시:
    analyzer = ImpactAnalyzer(memory_hub)
    task = AgentTask(
        intent="analyze_impact",
        inputs={
            "changes": [
                {"file": "auth.py", "component": "login", "type": "modify"}
            ],
            "codebase_analysis": static_analysis_result
        }
    )
    result = await analyzer.execute(task)
    impact_report = result.data  # 영향도 분석 보고서

작성자: T-Developer v2
버전: 2.0.0
최종 수정: 2024-12-20
"""

from __future__ import annotations

import ast
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import networkx as nx

from backend.packages.agents.base import BaseAgent, AgentResult, AgentTask, TaskStatus
from backend.packages.agents.static_analyzer import StaticAnalyzer, CodebaseAnalysis
from backend.packages.agents.ai_providers import get_ai_provider
from backend.packages.memory import ContextType, MemoryHub


@dataclass
class ImpactArea:
    """Represents an area affected by a change."""
    
    file_path: str
    component: str  # function/class name
    impact_type: str  # direct, indirect, test, downstream
    risk_level: str  # low, medium, high, critical
    confidence: float  # 0-1 confidence score
    reason: str


@dataclass
class ChangeImpact:
    """Impact analysis for a single change."""
    
    changed_file: str
    changed_component: str
    change_type: str  # add, modify, delete
    
    direct_impacts: List[ImpactArea] = field(default_factory=list)
    indirect_impacts: List[ImpactArea] = field(default_factory=list)
    test_impacts: List[ImpactArea] = field(default_factory=list)
    downstream_impacts: List[ImpactArea] = field(default_factory=list)
    
    total_files_affected: int = 0
    risk_score: float = 0.0
    blast_radius: int = 0  # Number of components affected


@dataclass
class DependencyMatrix:
    """Matrix showing dependencies between components."""
    
    components: List[str]
    dependencies: Dict[str, List[str]]  # component -> list of dependencies
    reverse_dependencies: Dict[str, List[str]]  # component -> list of dependents
    coupling_scores: Dict[Tuple[str, str], float]  # pair -> coupling strength
    clusters: List[List[str]]  # Highly coupled component groups


@dataclass
class SystemReport:
    """Comprehensive system state report."""
    
    timestamp: str
    
    # System metrics
    total_files: int = 0
    total_components: int = 0
    total_dependencies: int = 0
    
    # Architecture metrics
    avg_coupling: float = 0.0
    max_coupling: float = 0.0
    cyclomatic_complexity: int = 0
    
    # Quality metrics
    test_coverage: float = 0.0
    code_duplication: float = 0.0
    technical_debt_score: float = 0.0
    
    # Risk areas
    high_risk_components: List[Dict[str, Any]] = field(default_factory=list)
    single_points_of_failure: List[str] = field(default_factory=list)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    
    # Dependency analysis
    dependency_matrix: Optional[DependencyMatrix] = None
    
    # Change history
    recent_changes: List[Dict[str, Any]] = field(default_factory=list)
    change_frequency_map: Dict[str, int] = field(default_factory=dict)


class ImpactAnalyzer(BaseAgent):
    """AI-driven impact analyzer for intelligent change prediction.
    
    This agent uses AI to:
    1. Predict cascading effects of changes
    2. Identify hidden dependencies
    3. Estimate risk levels with reasoning
    4. Generate mitigation strategies
    5. Learn from historical change patterns
    6. Detect architectural anti-patterns
    7. Suggest refactoring opportunities
    """
    
    def __init__(
        self,
        memory_hub: Optional[MemoryHub] = None,
        static_analyzer: Optional[StaticAnalyzer] = None,
        **kwargs: Any
    ) -> None:
        """Initialize the Impact Analyzer.
        
        Args:
            memory_hub: Memory Hub instance
            static_analyzer: Static analyzer instance
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__(
            name="ImpactAnalyzer",
            version="2.0.0",  # AI-enhanced version
            memory_hub=memory_hub,
            **kwargs
        )
        
        self.logger = logging.getLogger(__name__)
        self.static_analyzer = static_analyzer or StaticAnalyzer()
        self.dependency_graph = None
        self.ai_provider = None  # Lazy load AI provider
    
    async def execute(self, task) -> AgentResult:
        """Execute impact analysis.
        
        Args:
            task: The analysis task (dict or AgentTask) containing:
                - project_path: Path to project root
                - analysis_type: 'impact', 'report', or 'matrix'
                - changes: List of changed files (for impact analysis)
                - include_tests: Include test impact analysis
                
        Returns:
            AgentResult containing analysis results
        """
        try:
            # Handle both dict and AgentTask inputs
            if isinstance(task, dict):
                inputs = task
            else:
                inputs = task.inputs
            
            # Extract parameters
            project_path = inputs.get("project_path", ".")
            analysis_type = inputs.get("analysis_type", "report")
            changes = inputs.get("changes", [])
            include_tests = inputs.get("include_tests", True)
            
            # Build or load dependency graph
            await self._build_dependency_graph(project_path)
            
            result_data = {}
            
            if analysis_type == "impact":
                # Analyze change impact
                impacts = await self._analyze_changes(changes, include_tests)
                result_data = self._format_impact_results(impacts)
                
            elif analysis_type == "matrix":
                # Generate dependency matrix
                matrix = await self._generate_dependency_matrix(project_path)
                result_data = self._format_matrix_results(matrix)
                
            else:  # report
                # Generate comprehensive report
                report = await self._generate_system_report(project_path)
                result_data = self._format_report_results(report)
            
            # Store in memory if available
            if self.memory_hub:
                await self._store_analysis(analysis_type, result_data)
            
            return self.format_result(
                success=True,
                data=result_data,
                metadata={"agent": self.name, "version": self.version}
            )
            
        except Exception as e:
            self.logger.error(f"Impact analysis failed: {e}")
            return self.format_result(
                success=False,
                error=str(e)
            )
    
    async def _build_dependency_graph(self, project_path: str) -> None:
        """Build dependency graph for the project.
        
        Args:
            project_path: Path to project
        """
        # Use static analyzer to get codebase analysis
        analysis = await self.static_analyzer.analyze_codebase(project_path)
        
        # Build NetworkX graph
        self.dependency_graph = nx.DiGraph()
        
        # Add nodes for all files and components
        for file_path, metrics in analysis.metrics_by_file.items():
            # Add file node
            self.dependency_graph.add_node(
                file_path,
                type="file",
                metrics=metrics
            )
            
            # Add component nodes
            for func in metrics.functions:
                node_id = f"{file_path}::{func}"
                self.dependency_graph.add_node(
                    node_id,
                    type="function",
                    name=func,
                    file=file_path
                )
                # Link to file
                self.dependency_graph.add_edge(file_path, node_id)
            
            for cls in metrics.classes:
                node_id = f"{file_path}::{cls}"
                self.dependency_graph.add_node(
                    node_id,
                    type="class",
                    name=cls,
                    file=file_path
                )
                # Link to file
                self.dependency_graph.add_edge(file_path, node_id)
        
        # Add dependency edges
        for file_path, dependencies in analysis.dependency_graph.items():
            for dep in dependencies:
                if dep in self.dependency_graph:
                    self.dependency_graph.add_edge(file_path, dep)
        
        # Add contract/interface relationships
        for file_path, contracts in analysis.contracts.items():
            for contract in contracts:
                if contract['type'] == 'method':
                    # Link methods to their classes
                    class_node = f"{file_path}::{contract['class']}"
                    method_node = f"{file_path}::{contract['class']}.{contract['name']}"
                    if class_node in self.dependency_graph:
                        self.dependency_graph.add_node(
                            method_node,
                            type="method",
                            contract=contract
                        )
                        self.dependency_graph.add_edge(class_node, method_node)
    
    async def _analyze_changes(
        self,
        changes: List[Dict[str, Any]],
        include_tests: bool
    ) -> List[ChangeImpact]:
        """Analyze impact of changes.
        
        Args:
            changes: List of changes with file and type
            include_tests: Whether to include test impact
            
        Returns:
            List of change impacts
        """
        impacts = []
        
        for change in changes:
            file_path = change.get("file")
            component = change.get("component", "")
            change_type = change.get("type", "modify")
            
            if not file_path:
                continue
            
            impact = ChangeImpact(
                changed_file=file_path,
                changed_component=component,
                change_type=change_type
            )
            
            # Find direct impacts (immediate dependencies)
            if file_path in self.dependency_graph:
                direct_deps = list(self.dependency_graph.successors(file_path))
                for dep in direct_deps:
                    impact.direct_impacts.append(ImpactArea(
                        file_path=dep if ':' not in dep else dep.split('::')[0],
                        component=dep.split('::')[1] if '::' in dep else "",
                        impact_type="direct",
                        risk_level=self._assess_risk_level(change_type, "direct"),
                        confidence=0.9,
                        reason=f"Directly depends on {file_path}"
                    ))
            
            # Find indirect impacts (transitive dependencies)
            if file_path in self.dependency_graph:
                # Use BFS to find impacts up to 3 levels deep
                indirect_deps = set()
                current_level = set(self.dependency_graph.successors(file_path))
                for _ in range(2):  # 2 more levels after direct
                    next_level = set()
                    for node in current_level:
                        next_level.update(self.dependency_graph.successors(node))
                    indirect_deps.update(next_level)
                    current_level = next_level
                
                for dep in indirect_deps:
                    impact.indirect_impacts.append(ImpactArea(
                        file_path=dep if ':' not in dep else dep.split('::')[0],
                        component=dep.split('::')[1] if '::' in dep else "",
                        impact_type="indirect",
                        risk_level=self._assess_risk_level(change_type, "indirect"),
                        confidence=0.6,
                        reason=f"Transitively depends on {file_path}"
                    ))
            
            # Find test impacts
            if include_tests:
                test_impacts = self._find_test_impacts(file_path, component)
                impact.test_impacts = test_impacts
            
            # Find downstream impacts (reverse dependencies)
            if file_path in self.dependency_graph:
                downstream = list(self.dependency_graph.predecessors(file_path))
                for dep in downstream:
                    impact.downstream_impacts.append(ImpactArea(
                        file_path=dep if ':' not in dep else dep.split('::')[0],
                        component=dep.split('::')[1] if '::' in dep else "",
                        impact_type="downstream",
                        risk_level=self._assess_risk_level(change_type, "downstream"),
                        confidence=0.7,
                        reason=f"Provides functionality to {file_path}"
                    ))
            
            # Calculate metrics
            all_impacts = (
                impact.direct_impacts + 
                impact.indirect_impacts + 
                impact.test_impacts + 
                impact.downstream_impacts
            )
            
            unique_files = set(i.file_path for i in all_impacts)
            impact.total_files_affected = len(unique_files)
            impact.blast_radius = len(all_impacts)
            
            # Calculate risk score
            # Use AI for risk assessment
            impact.risk_score = await self._calculate_risk_score_with_ai(impact)
            
            impacts.append(impact)
        
        return impacts
    
    def _find_test_impacts(
        self,
        file_path: str,
        component: str
    ) -> List[ImpactArea]:
        """Find tests that might be affected by changes.
        
        Args:
            file_path: Changed file path
            component: Changed component name
            
        Returns:
            List of test impacts
        """
        test_impacts = []
        
        # Find test files
        base_name = Path(file_path).stem
        test_patterns = [
            f"test_{base_name}",
            f"{base_name}_test",
            f"tests/{base_name}",
            f"test/{base_name}"
        ]
        
        for node in self.dependency_graph.nodes():
            if any(pattern in node.lower() for pattern in test_patterns):
                test_impacts.append(ImpactArea(
                    file_path=node if ':' not in node else node.split('::')[0],
                    component=node.split('::')[1] if '::' in node else "",
                    impact_type="test",
                    risk_level="high",
                    confidence=0.8,
                    reason=f"Tests for {file_path} may need updates"
                ))
        
        return test_impacts
    
    def _assess_risk_level(self, change_type: str, impact_type: str) -> str:
        """Assess risk level based on change and impact type.
        
        Args:
            change_type: Type of change
            impact_type: Type of impact
            
        Returns:
            Risk level
        """
        risk_matrix = {
            ("delete", "direct"): "critical",
            ("delete", "indirect"): "high",
            ("delete", "downstream"): "high",
            ("modify", "direct"): "high",
            ("modify", "indirect"): "medium",
            ("modify", "downstream"): "medium",
            ("add", "direct"): "low",
            ("add", "indirect"): "low",
            ("add", "downstream"): "low"
        }
        
        return risk_matrix.get((change_type, impact_type), "medium")
    
    async def _calculate_risk_score_with_ai(self, impact: ChangeImpact) -> float:
        """Calculate risk score using AI for intelligent prediction.
        
        Args:
            impact: Change impact analysis
            
        Returns:
            Risk score (0-100)
        """
        # Initialize AI provider if needed
        if not self.ai_provider:
            self.ai_provider = get_ai_provider()
        
        # Prepare context for AI
        context = {
            "changed_file": impact.changed_file,
            "changed_component": impact.changed_component,
            "change_type": impact.change_type,
            "direct_impacts": len(impact.direct_impacts),
            "indirect_impacts": len(impact.indirect_impacts),
            "blast_radius": impact.blast_radius
        }
        
        try:
            prompt = f"""Analyze this change impact and provide risk score (0-100):
            Change: {context['changed_component']} in {context['changed_file']}
            Type: {context['change_type']}
            Direct impacts: {context['direct_impacts']}
            Indirect impacts: {context['indirect_impacts']}
            Total affected: {context['blast_radius']}
            
            Return a number between 0-100 representing the risk level."""
            
            response = await self.ai_provider.analyze(prompt)
            # Extract number from response
            import re
            numbers = re.findall(r'\d+', response)
            if numbers:
                return min(float(numbers[0]), 100)
        except Exception as e:
            self.logger.debug(f"AI risk assessment failed: {e}")
        
        # Fallback to rule-based
        return self._calculate_risk_score_fallback(impact)
    
    def _calculate_risk_score_fallback(self, impact: ChangeImpact) -> float:
        """Fallback rule-based risk calculation.
        
        Args:
            impact: Change impact analysis
            
        Returns:
            Risk score (0-100)
        """
        score = 0.0
        
        # Risk weights
        weights = {
            "critical": 25,
            "high": 15,
            "medium": 5,
            "low": 1
        }
        
        # Count risk levels
        for area in impact.direct_impacts:
            score += weights.get(area.risk_level, 0) * area.confidence
        
        for area in impact.indirect_impacts:
            score += weights.get(area.risk_level, 0) * area.confidence * 0.5
        
        for area in impact.test_impacts:
            score += weights.get(area.risk_level, 0) * area.confidence * 0.7
        
        # Factor in blast radius
        score += min(impact.blast_radius * 0.5, 20)
        
        # Cap at 100
        return min(score, 100)
    
    async def _generate_dependency_matrix(
        self,
        project_path: str
    ) -> DependencyMatrix:
        """Generate dependency matrix for the project.
        
        Args:
            project_path: Path to project
            
        Returns:
            Dependency matrix
        """
        matrix = DependencyMatrix(
            components=[],
            dependencies={},
            reverse_dependencies={},
            coupling_scores={},
            clusters=[]
        )
        
        # Get all components
        components = [
            node for node in self.dependency_graph.nodes()
            if self.dependency_graph.nodes[node].get('type') in ['class', 'function']
        ]
        matrix.components = components
        
        # Build dependency maps
        for comp in components:
            # Forward dependencies
            deps = list(self.dependency_graph.successors(comp))
            matrix.dependencies[comp] = [d for d in deps if d in components]
            
            # Reverse dependencies
            rev_deps = list(self.dependency_graph.predecessors(comp))
            matrix.reverse_dependencies[comp] = [d for d in rev_deps if d in components]
        
        # Calculate coupling scores
        for comp1 in components:
            for comp2 in components:
                if comp1 != comp2:
                    # Count shared dependencies
                    shared_deps = set(matrix.dependencies.get(comp1, [])) & \
                                 set(matrix.dependencies.get(comp2, []))
                    
                    # Count mutual dependencies
                    mutual = (comp2 in matrix.dependencies.get(comp1, []) or
                             comp1 in matrix.dependencies.get(comp2, []))
                    
                    # Calculate coupling score
                    score = len(shared_deps) * 0.3
                    if mutual:
                        score += 0.7
                    
                    if score > 0:
                        matrix.coupling_scores[(comp1, comp2)] = min(score, 1.0)
        
        # Find clusters (highly coupled components)
        if components:
            # Use community detection
            try:
                import community
                partition = community.best_partition(
                    self.dependency_graph.to_undirected()
                )
                
                clusters_dict = {}
                for node, cluster_id in partition.items():
                    if node in components:
                        if cluster_id not in clusters_dict:
                            clusters_dict[cluster_id] = []
                        clusters_dict[cluster_id].append(node)
                
                matrix.clusters = list(clusters_dict.values())
            except ImportError:
                # Fallback: simple connected components
                undirected = self.dependency_graph.to_undirected()
                for comp_set in nx.connected_components(undirected):
                    cluster = [n for n in comp_set if n in components]
                    if len(cluster) > 1:
                        matrix.clusters.append(cluster)
        
        return matrix
    
    async def _generate_system_report(
        self,
        project_path: str
    ) -> SystemReport:
        """Generate comprehensive system report.
        
        Args:
            project_path: Path to project
            
        Returns:
            System report
        """
        report = SystemReport(timestamp=datetime.now().isoformat())
        
        # Get static analysis
        analysis = await self.static_analyzer.analyze_codebase(project_path)
        
        # Basic metrics
        report.total_files = analysis.total_files
        report.total_components = len([
            n for n in self.dependency_graph.nodes()
            if self.dependency_graph.nodes[n].get('type') in ['class', 'function']
        ])
        report.total_dependencies = self.dependency_graph.number_of_edges()
        
        # Architecture metrics
        if report.total_components > 0:
            # Average coupling
            degrees = [self.dependency_graph.degree(n) for n in self.dependency_graph.nodes()]
            report.avg_coupling = sum(degrees) / len(degrees) if degrees else 0
            report.max_coupling = max(degrees) if degrees else 0
        
        # Complexity
        total_complexity = sum(
            m.cyclomatic_complexity for m in analysis.metrics_by_file.values()
        )
        report.cyclomatic_complexity = total_complexity
        
        # Quality metrics
        report.test_coverage = analysis.test_coverage_estimate
        
        # Find high-risk components
        for node in self.dependency_graph.nodes():
            node_data = self.dependency_graph.nodes[node]
            if node_data.get('type') in ['class', 'function']:
                in_degree = self.dependency_graph.in_degree(node)
                out_degree = self.dependency_graph.out_degree(node)
                
                # High coupling = high risk
                if in_degree + out_degree > 10:
                    report.high_risk_components.append({
                        "component": node,
                        "in_degree": in_degree,
                        "out_degree": out_degree,
                        "total_coupling": in_degree + out_degree,
                        "reason": "High coupling"
                    })
        
        # Find single points of failure
        for node in self.dependency_graph.nodes():
            if self.dependency_graph.in_degree(node) > 5:
                # Many components depend on this
                report.single_points_of_failure.append(node)
        
        # Find circular dependencies
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            report.circular_dependencies = [
                cycle for cycle in cycles if len(cycle) <= 5
            ][:10]  # Limit to 10 most relevant
        except:
            pass
        
        # Generate dependency matrix
        report.dependency_matrix = await self._generate_dependency_matrix(project_path)
        
        # Get change history from memory if available
        if self.memory_hub:
            recent_changes = await self._get_recent_changes()
            report.recent_changes = recent_changes
            
            # Calculate change frequency
            for change in recent_changes:
                file_path = change.get("file", "")
                if file_path:
                    report.change_frequency_map[file_path] = \
                        report.change_frequency_map.get(file_path, 0) + 1
        
        # Calculate technical debt score (simplified)
        debt_factors = [
            (100 - report.test_coverage) * 0.3,  # Low test coverage
            len(report.circular_dependencies) * 5,  # Circular deps
            len(report.high_risk_components) * 2,  # High risk components
            (report.max_coupling / 10) * 10 if report.max_coupling > 10 else 0  # High coupling
        ]
        report.technical_debt_score = min(sum(debt_factors), 100)
        
        return report
    
    async def _get_recent_changes(self) -> List[Dict[str, Any]]:
        """Get recent changes from memory.
        
        Returns:
            List of recent changes
        """
        if not self.memory_hub:
            return []
        
        # Search for recent change records
        results = await self.search_memory(
            ContextType.A_CTX,
            tags=["change", "impact"],
            limit=20
        )
        
        changes = []
        for result in results:
            if isinstance(result, dict) and "value" in result:
                changes.append(result["value"])
        
        return changes
    
    def _format_impact_results(
        self,
        impacts: List[ChangeImpact]
    ) -> Dict[str, Any]:
        """Format impact analysis results.
        
        Args:
            impacts: List of change impacts
            
        Returns:
            Formatted results
        """
        total_risk = sum(i.risk_score for i in impacts)
        total_affected = sum(i.total_files_affected for i in impacts)
        
        return {
            "summary": {
                "changes_analyzed": len(impacts),
                "total_files_affected": total_affected,
                "average_risk_score": total_risk / len(impacts) if impacts else 0,
                "max_risk_score": max((i.risk_score for i in impacts), default=0)
            },
            "impacts": [
                {
                    "file": impact.changed_file,
                    "component": impact.changed_component,
                    "change_type": impact.change_type,
                    "risk_score": impact.risk_score,
                    "blast_radius": impact.blast_radius,
                    "direct_impacts": len(impact.direct_impacts),
                    "indirect_impacts": len(impact.indirect_impacts),
                    "test_impacts": len(impact.test_impacts),
                    "high_risk_areas": [
                        {
                            "file": area.file_path,
                            "component": area.component,
                            "risk": area.risk_level,
                            "reason": area.reason
                        }
                        for area in impact.direct_impacts
                        if area.risk_level in ["high", "critical"]
                    ][:5]
                }
                for impact in impacts
            ]
        }
    
    def _format_matrix_results(
        self,
        matrix: DependencyMatrix
    ) -> Dict[str, Any]:
        """Format dependency matrix results.
        
        Args:
            matrix: Dependency matrix
            
        Returns:
            Formatted results
        """
        # Find most coupled pairs
        coupled_pairs = sorted(
            matrix.coupling_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "summary": {
                "total_components": len(matrix.components),
                "total_dependencies": sum(len(deps) for deps in matrix.dependencies.values()),
                "average_dependencies": sum(len(deps) for deps in matrix.dependencies.values()) / 
                                      len(matrix.components) if matrix.components else 0,
                "clusters_found": len(matrix.clusters)
            },
            "highly_coupled": [
                {
                    "component1": pair[0][0],
                    "component2": pair[0][1],
                    "coupling_score": pair[1]
                }
                for pair in coupled_pairs
            ],
            "clusters": [
                {
                    "id": i,
                    "size": len(cluster),
                    "components": cluster[:10]  # Limit display
                }
                for i, cluster in enumerate(matrix.clusters)
            ],
            "most_depended_on": sorted(
                [
                    {
                        "component": comp,
                        "dependents": len(matrix.reverse_dependencies.get(comp, []))
                    }
                    for comp in matrix.components
                ],
                key=lambda x: x["dependents"],
                reverse=True
            )[:10]
        }
    
    def _format_report_results(self, report: SystemReport) -> Dict[str, Any]:
        """Format system report results.
        
        Args:
            report: System report
            
        Returns:
            Formatted results
        """
        return {
            "system_health": {
                "technical_debt_score": report.technical_debt_score,
                "test_coverage": report.test_coverage,
                "avg_coupling": report.avg_coupling,
                "cyclomatic_complexity": report.cyclomatic_complexity
            },
            "metrics": {
                "total_files": report.total_files,
                "total_components": report.total_components,
                "total_dependencies": report.total_dependencies
            },
            "risks": {
                "high_risk_components": report.high_risk_components[:5],
                "single_points_of_failure": report.single_points_of_failure[:5],
                "circular_dependencies": len(report.circular_dependencies)
            },
            "change_hotspots": sorted(
                [
                    {"file": file, "changes": count}
                    for file, count in report.change_frequency_map.items()
                ],
                key=lambda x: x["changes"],
                reverse=True
            )[:10],
            "recommendations": self._generate_recommendations(report)
        }
    
    def _generate_recommendations(self, report: SystemReport) -> List[str]:
        """Generate recommendations based on system report.
        
        Args:
            report: System report
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Test coverage
        if report.test_coverage < 70:
            recommendations.append(
                f"Improve test coverage from {report.test_coverage:.0f}% to at least 70%"
            )
        
        # Technical debt
        if report.technical_debt_score > 50:
            recommendations.append(
                f"High technical debt score ({report.technical_debt_score:.0f}). "
                "Consider refactoring high-risk components"
            )
        
        # Circular dependencies
        if report.circular_dependencies:
            recommendations.append(
                f"Resolve {len(report.circular_dependencies)} circular dependencies "
                "to improve maintainability"
            )
        
        # Single points of failure
        if report.single_points_of_failure:
            top_spof = report.single_points_of_failure[0]
            recommendations.append(
                f"Reduce coupling for '{top_spof}' - it's a single point of failure"
            )
        
        # High coupling
        if report.avg_coupling > 5:
            recommendations.append(
                "Average coupling is high. Consider breaking down tightly coupled components"
            )
        
        # Complexity
        if report.cyclomatic_complexity > 100:
            recommendations.append(
                "High overall complexity. Simplify complex functions and classes"
            )
        
        return recommendations
    
    async def _store_analysis(
        self,
        analysis_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Store analysis results in memory.
        
        Args:
            analysis_type: Type of analysis
            data: Analysis data
        """
        if not self.memory_hub:
            return
        
        # Store in agent context
        await self.write_memory(
            ContextType.A_CTX,
            f"impact_{analysis_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            {
                "type": analysis_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            },
            ttl_seconds=86400 * 7,  # 7 days
            tags=["impact", analysis_type, "analysis"]
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
        
        # Check analysis type
        analysis_type = task.inputs.get("analysis_type", "report")
        if analysis_type not in ["impact", "report", "matrix"]:
            return False
        
        # For impact analysis, need changes
        if analysis_type == "impact":
            if "changes" not in task.inputs:
                return False
        
        return True