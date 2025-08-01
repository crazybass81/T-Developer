from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np

@dataclass
class ParsedRequirement:
    id: str
    description: str
    type: str
    complexity: int

@dataclass
class PrioritizedRequirement:
    requirement: ParsedRequirement
    priority_score: float
    priority_factors: Dict[str, float]
    dependencies: List[str]
    estimated_effort: int  # story points
    business_value: float
    risk_level: float
    recommended_sprint: int

class BusinessValueEstimator:
    async def estimate(self, req: ParsedRequirement, context: Any) -> float:
        # Simple heuristic based on requirement type
        value_map = {
            'core_functionality': 0.9,
            'user_interface': 0.7,
            'performance': 0.6,
            'security': 0.8,
            'integration': 0.5
        }
        return value_map.get(req.type, 0.5)

class EffortEstimator:
    async def estimate(self, req: ParsedRequirement) -> int:
        # Fibonacci sequence for story points
        complexity_to_points = {1: 1, 2: 2, 3: 3, 4: 5, 5: 8}
        return complexity_to_points.get(req.complexity, 5)

class RiskAnalyzer:
    async def analyze(self, req: ParsedRequirement) -> float:
        # Risk based on complexity and type
        risk_factors = {
            'integration': 0.7,
            'performance': 0.6,
            'security': 0.8,
            'core_functionality': 0.4
        }
        base_risk = risk_factors.get(req.type, 0.5)
        complexity_risk = req.complexity * 0.1
        return min(base_risk + complexity_risk, 1.0)

class DependencyResolver:
    def find_dependencies(self, req: ParsedRequirement, all_requirements: List[ParsedRequirement]) -> List[str]:
        dependencies = []
        
        # Simple dependency detection based on keywords
        dependency_keywords = {
            'authentication': ['user_management'],
            'payment': ['user_management', 'security'],
            'reporting': ['data_storage', 'user_management']
        }
        
        req_lower = req.description.lower()
        for keyword, deps in dependency_keywords.items():
            if keyword in req_lower:
                for other_req in all_requirements:
                    if any(dep in other_req.description.lower() for dep in deps):
                        dependencies.append(other_req.id)
        
        return dependencies

class RequirementPrioritizer:
    """요구사항 우선순위 자동 결정"""

    def __init__(self):
        self.value_estimator = BusinessValueEstimator()
        self.effort_estimator = EffortEstimator()
        self.risk_analyzer = RiskAnalyzer()
        self.dependency_resolver = DependencyResolver()

    async def prioritize_requirements(
        self,
        requirements: List[ParsedRequirement],
        project_context: Any
    ) -> List[PrioritizedRequirement]:
        """요구사항 우선순위 결정"""

        prioritized = []

        # 1. 각 요구사항 평가
        for req in requirements:
            # 비즈니스 가치 평가
            business_value = await self.value_estimator.estimate(req, project_context)

            # 구현 노력 추정
            effort = await self.effort_estimator.estimate(req)

            # 리스크 평가
            risk = await self.risk_analyzer.analyze(req)

            # 의존성 분석
            dependencies = self.dependency_resolver.find_dependencies(req, requirements)

            # 우선순위 점수 계산
            priority_score = self._calculate_priority_score(
                business_value,
                effort,
                risk,
                len(dependencies)
            )

            prioritized.append(PrioritizedRequirement(
                requirement=req,
                priority_score=priority_score,
                priority_factors={
                    'business_value': business_value,
                    'effort': effort,
                    'risk': risk,
                    'dependency_count': len(dependencies)
                },
                dependencies=dependencies,
                estimated_effort=effort,
                business_value=business_value,
                risk_level=risk,
                recommended_sprint=0  # 나중에 계산
            ))

        # 2. 의존성 기반 정렬
        prioritized = self._sort_by_dependencies(prioritized)

        # 3. 스프린트 할당
        prioritized = self._assign_to_sprints(prioritized, project_context)

        return prioritized

    def _calculate_priority_score(
        self,
        business_value: float,
        effort: int,
        risk: float,
        dependency_count: int
    ) -> float:
        """우선순위 점수 계산 (WSJF 변형)"""

        time_criticality = 1.0 / (dependency_count + 1)  # 의존성이 적을수록 높음
        risk_reduction = 1.0 - risk  # 리스크가 높은 항목 우선 처리

        numerator = (
            business_value * 0.4 +
            time_criticality * 0.3 +
            risk_reduction * 0.3
        )

        # 작업 크기로 나누기 (0으로 나누기 방지)
        job_size = max(effort, 1)

        return numerator / job_size

    def _sort_by_dependencies(
        self,
        prioritized: List[PrioritizedRequirement]
    ) -> List[PrioritizedRequirement]:
        """의존성을 고려한 정렬"""

        # 의존성 그래프 생성
        dependency_graph = {}
        for p_req in prioritized:
            dependency_graph[p_req.requirement.id] = p_req.dependencies

        # 위상 정렬
        sorted_ids = self._topological_sort(dependency_graph)

        # 정렬된 순서로 재배열
        id_to_req = {p.requirement.id: p for p in prioritized}
        sorted_requirements = []

        for req_id in sorted_ids:
            if req_id in id_to_req:
                sorted_requirements.append(id_to_req[req_id])

        # 위상 정렬에 포함되지 않은 요구사항 추가
        for p_req in prioritized:
            if p_req not in sorted_requirements:
                sorted_requirements.append(p_req)

        return sorted_requirements

    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """위상 정렬 구현"""
        in_degree = {node: 0 for node in graph}
        
        # 진입 차수 계산
        for node in graph:
            for neighbor in graph[node]:
                if neighbor in in_degree:
                    in_degree[neighbor] += 1

        # 진입 차수가 0인 노드들로 시작
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            # 인접 노드들의 진입 차수 감소
            for neighbor in graph.get(node, []):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)

        return result

    def _assign_to_sprints(
        self,
        prioritized: List[PrioritizedRequirement],
        project_context: Any
    ) -> List[PrioritizedRequirement]:
        """스프린트 할당"""
        
        sprint_capacity = 20  # story points per sprint
        current_sprint = 1
        current_capacity = sprint_capacity

        for p_req in prioritized:
            if p_req.estimated_effort > current_capacity:
                current_sprint += 1
                current_capacity = sprint_capacity

            p_req.recommended_sprint = current_sprint
            current_capacity -= p_req.estimated_effort

        return prioritized