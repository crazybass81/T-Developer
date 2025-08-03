# backend/src/agents/nl_input/requirement_prioritizer.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class PrioritizedRequirement:
    requirement: Dict[str, Any]
    priority_score: float
    priority_factors: Dict[str, float]
    dependencies: List[str]
    estimated_effort: int  # story points
    business_value: float
    risk_level: float
    recommended_sprint: int

class RequirementPrioritizer:
    """완성된 요구사항 우선순위 자동화"""

    def __init__(self):
        self.value_weights = {
            'user_impact': 0.3,
            'business_value': 0.25,
            'strategic_alignment': 0.2,
            'revenue_impact': 0.15,
            'compliance': 0.1
        }
        
        self.effort_weights = {
            'complexity': 0.4,
            'dependencies': 0.3,
            'technical_risk': 0.2,
            'resource_availability': 0.1
        }

    async def prioritize_requirements(
        self,
        requirements: List[Dict[str, Any]],
        project_context: Dict[str, Any]
    ) -> List[PrioritizedRequirement]:
        """요구사항 우선순위 결정 - 완성된 WSJF 구현"""

        prioritized = []

        for req in requirements:
            # 비즈니스 가치 평가
            business_value = self._calculate_business_value(req, project_context)
            
            # 구현 노력 추정
            effort = self._estimate_effort(req)
            
            # 리스크 평가
            risk = self._assess_risk(req)
            
            # 의존성 분석
            dependencies = self._analyze_dependencies(req, requirements)
            
            # WSJF 점수 계산
            wsjf_score = self._calculate_wsjf_score(
                business_value, effort, risk, len(dependencies)
            )

            prioritized_req = PrioritizedRequirement(
                requirement=req,
                priority_score=wsjf_score,
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
            )
            
            prioritized.append(prioritized_req)

        # 의존성 기반 정렬
        sorted_requirements = self._sort_by_dependencies(prioritized)
        
        # 스프린트 할당
        final_requirements = self._assign_to_sprints(sorted_requirements, project_context)

        return final_requirements

    def _calculate_business_value(self, requirement: Dict[str, Any], context: Dict[str, Any]) -> float:
        """비즈니스 가치 계산"""
        value_score = 0.0

        # 사용자 영향도
        if 'user_impact' in requirement:
            impact_map = {'high': 1.0, 'medium': 0.6, 'low': 0.3}
            user_impact = impact_map.get(requirement['user_impact'], 0.5)
            value_score += user_impact * self.value_weights['user_impact']

        # 비즈니스 가치
        if 'business_priority' in requirement:
            priority_map = {'critical': 1.0, 'high': 0.8, 'medium': 0.5, 'low': 0.2}
            business_priority = priority_map.get(requirement['business_priority'], 0.5)
            value_score += business_priority * self.value_weights['business_value']

        # 전략적 정렬
        if context.get('strategic_goals'):
            alignment = self._calculate_strategic_alignment(requirement, context['strategic_goals'])
            value_score += alignment * self.value_weights['strategic_alignment']

        # 수익 영향
        if 'revenue_impact' in requirement:
            revenue_score = min(requirement['revenue_impact'] / 100000, 1.0)  # 정규화
            value_score += revenue_score * self.value_weights['revenue_impact']

        # 규정 준수
        if requirement.get('compliance_required', False):
            value_score += 1.0 * self.value_weights['compliance']

        return min(value_score, 1.0)

    def _estimate_effort(self, requirement: Dict[str, Any]) -> int:
        """구현 노력 추정 (스토리 포인트)"""
        base_effort = 3  # 기본 노력

        # 복잡도 기반 조정
        complexity_map = {'simple': 1, 'medium': 3, 'complex': 8, 'very_complex': 13}
        complexity = requirement.get('complexity', 'medium')
        effort = complexity_map.get(complexity, 3)

        # 기술적 위험 조정
        if requirement.get('technical_risk', 'low') == 'high':
            effort *= 1.5

        # 외부 의존성 조정
        external_deps = len(requirement.get('external_dependencies', []))
        effort += external_deps * 2

        return int(effort)

    def _assess_risk(self, requirement: Dict[str, Any]) -> float:
        """리스크 평가"""
        risk_score = 0.0

        # 기술적 위험
        tech_risk_map = {'low': 0.1, 'medium': 0.5, 'high': 0.9}
        tech_risk = tech_risk_map.get(requirement.get('technical_risk', 'medium'), 0.5)
        risk_score += tech_risk * 0.4

        # 비즈니스 위험
        business_risk_map = {'low': 0.1, 'medium': 0.5, 'high': 0.9}
        business_risk = business_risk_map.get(requirement.get('business_risk', 'low'), 0.1)
        risk_score += business_risk * 0.3

        # 일정 위험
        if requirement.get('has_deadline', False):
            risk_score += 0.2

        # 리소스 위험
        if requirement.get('requires_specialist', False):
            risk_score += 0.1

        return min(risk_score, 1.0)

    def _calculate_wsjf_score(self, business_value: float, effort: int, risk: float, dependency_count: int) -> float:
        """WSJF (Weighted Shortest Job First) 점수 계산 - 완성된 구현"""
        
        # 시간 중요도 (의존성이 적을수록 높음)
        time_criticality = 1.0 / (dependency_count + 1)
        
        # 위험 감소 가치 (위험이 높은 항목을 우선 처리)
        risk_reduction = 1.0 - risk
        
        # 분자: 비즈니스 가치 + 시간 중요도 + 위험 감소
        numerator = (
            business_value * 0.4 +
            time_criticality * 0.3 +
            risk_reduction * 0.3
        )
        
        # 분모: 작업 크기 (0으로 나누기 방지)
        job_size = max(effort, 1)
        
        return numerator / job_size

    def _analyze_dependencies(self, requirement: Dict[str, Any], all_requirements: List[Dict[str, Any]]) -> List[str]:
        """의존성 분석"""
        dependencies = []
        req_id = requirement.get('id', '')

        for other_req in all_requirements:
            if other_req.get('id') == req_id:
                continue
                
            # 명시적 의존성
            if req_id in other_req.get('depends_on', []):
                dependencies.append(other_req.get('id', ''))
            
            # 암시적 의존성 (키워드 기반)
            if self._has_implicit_dependency(requirement, other_req):
                dependencies.append(other_req.get('id', ''))

        return dependencies

    def _has_implicit_dependency(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> bool:
        """암시적 의존성 확인"""
        # 인증 시스템이 필요한 기능들
        if 'authentication' in req2.get('description', '').lower():
            if any(keyword in req1.get('description', '').lower() 
                   for keyword in ['login', 'user', 'profile', 'dashboard']):
                return True
        
        # 데이터베이스가 필요한 기능들
        if 'database' in req2.get('description', '').lower():
            if any(keyword in req1.get('description', '').lower() 
                   for keyword in ['store', 'save', 'retrieve', 'data']):
                return True
        
        return False

    def _sort_by_dependencies(self, requirements: List[PrioritizedRequirement]) -> List[PrioritizedRequirement]:
        """의존성을 고려한 정렬"""
        # 위상 정렬 구현
        sorted_reqs = []
        remaining = requirements.copy()
        
        while remaining:
            # 의존성이 없거나 모든 의존성이 해결된 요구사항 찾기
            ready = []
            for req in remaining:
                if not req.dependencies or all(
                    dep_id in [r.requirement.get('id') for r in sorted_reqs] 
                    for dep_id in req.dependencies
                ):
                    ready.append(req)
            
            if not ready:
                # 순환 의존성이 있는 경우 우선순위 점수로 정렬
                ready = [max(remaining, key=lambda r: r.priority_score)]
            
            # 우선순위 점수로 정렬
            ready.sort(key=lambda r: r.priority_score, reverse=True)
            
            # 첫 번째 요구사항 추가
            sorted_reqs.append(ready[0])
            remaining.remove(ready[0])
        
        return sorted_reqs

    def _assign_to_sprints(self, requirements: List[PrioritizedRequirement], context: Dict[str, Any]) -> List[PrioritizedRequirement]:
        """스프린트 할당"""
        sprint_capacity = context.get('sprint_capacity', 20)  # 스토리 포인트
        current_sprint = 1
        current_capacity = 0
        
        for req in requirements:
            if current_capacity + req.estimated_effort > sprint_capacity:
                current_sprint += 1
                current_capacity = 0
            
            req.recommended_sprint = current_sprint
            current_capacity += req.estimated_effort
        
        return requirements

    def _calculate_strategic_alignment(self, requirement: Dict[str, Any], strategic_goals: List[str]) -> float:
        """전략적 정렬 계산"""
        req_desc = requirement.get('description', '').lower()
        alignment_score = 0.0
        
        for goal in strategic_goals:
            goal_keywords = goal.lower().split()
            matches = sum(1 for keyword in goal_keywords if keyword in req_desc)
            if matches > 0:
                alignment_score += matches / len(goal_keywords)
        
        return min(alignment_score / len(strategic_goals) if strategic_goals else 0, 1.0)