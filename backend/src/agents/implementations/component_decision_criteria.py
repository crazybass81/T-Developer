# backend/src/agents/implementations/component_decision_criteria.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np

class CriteriaType(Enum):
    FUNCTIONAL = "functional"
    TECHNICAL = "technical"
    BUSINESS = "business"
    RISK = "risk"

@dataclass
class DecisionCriterion:
    name: str
    type: CriteriaType
    weight: float
    threshold: float
    description: str
    evaluation_method: str

class ComponentDecisionCriteria:
    """컴포넌트 결정 기준 관리"""

    def __init__(self):
        self.criteria = self._initialize_default_criteria()
        self.context_adjustments = {}

    def _initialize_default_criteria(self) -> Dict[str, DecisionCriterion]:
        """기본 결정 기준 초기화"""
        return {
            'functional_coverage': DecisionCriterion(
                name='Functional Coverage',
                type=CriteriaType.FUNCTIONAL,
                weight=0.25,
                threshold=0.7,
                description='How well the component covers required functionality',
                evaluation_method='feature_matching'
            ),
            'performance': DecisionCriterion(
                name='Performance',
                type=CriteriaType.TECHNICAL,
                weight=0.20,
                threshold=0.6,
                description='Performance characteristics and benchmarks',
                evaluation_method='benchmark_analysis'
            ),
            'security': DecisionCriterion(
                name='Security',
                type=CriteriaType.RISK,
                weight=0.20,
                threshold=0.8,
                description='Security features and vulnerability history',
                evaluation_method='security_assessment'
            ),
            'maintainability': DecisionCriterion(
                name='Maintainability',
                type=CriteriaType.TECHNICAL,
                weight=0.15,
                threshold=0.6,
                description='Code quality and maintenance status',
                evaluation_method='quality_metrics'
            ),
            'compatibility': DecisionCriterion(
                name='Compatibility',
                type=CriteriaType.TECHNICAL,
                weight=0.10,
                threshold=0.7,
                description='Integration and compatibility aspects',
                evaluation_method='compatibility_check'
            ),
            'cost_effectiveness': DecisionCriterion(
                name='Cost Effectiveness',
                type=CriteriaType.BUSINESS,
                weight=0.10,
                threshold=0.5,
                description='Cost vs benefit analysis',
                evaluation_method='cost_analysis'
            )
        }

    def adjust_for_context(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, DecisionCriterion]:
        """컨텍스트에 따른 기준 조정"""
        
        adjusted_criteria = self.criteria.copy()
        
        # 프로젝트 타입에 따른 조정
        project_type = context.get('project_type', 'general')
        
        if project_type == 'enterprise':
            # 엔터프라이즈: 보안과 호환성 중시
            adjusted_criteria['security'].weight = 0.3
            adjusted_criteria['compatibility'].weight = 0.15
            adjusted_criteria['functional_coverage'].weight = 0.2
        
        elif project_type == 'startup':
            # 스타트업: 기능과 비용 중시
            adjusted_criteria['functional_coverage'].weight = 0.3
            adjusted_criteria['cost_effectiveness'].weight = 0.2
            adjusted_criteria['security'].weight = 0.15
        
        elif project_type == 'high_performance':
            # 고성능: 성능 최우선
            adjusted_criteria['performance'].weight = 0.4
            adjusted_criteria['functional_coverage'].weight = 0.2
            adjusted_criteria['security'].weight = 0.15
        
        # 도메인에 따른 조정
        domain = context.get('domain', 'general')
        
        if domain in ['fintech', 'healthcare', 'government']:
            # 규제 도메인: 보안과 컴플라이언스 강화
            adjusted_criteria['security'].weight *= 1.5
            adjusted_criteria['security'].threshold = 0.9
        
        # 가중치 정규화
        total_weight = sum(c.weight for c in adjusted_criteria.values())
        for criterion in adjusted_criteria.values():
            criterion.weight /= total_weight
        
        return adjusted_criteria

    def get_evaluation_matrix(
        self,
        components: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """평가 매트릭스 생성"""
        
        criteria = self.adjust_for_context(context or {})
        
        # 컴포넌트 x 기준 매트릭스
        matrix = np.zeros((len(components), len(criteria)))
        
        for i, component in enumerate(components):
            for j, (name, criterion) in enumerate(criteria.items()):
                score = self._evaluate_criterion(component, criterion)
                matrix[i, j] = score
        
        return matrix

    def _evaluate_criterion(
        self,
        component: Dict[str, Any],
        criterion: DecisionCriterion
    ) -> float:
        """단일 기준 평가"""
        
        if criterion.evaluation_method == 'feature_matching':
            return self._evaluate_functional_coverage(component)
        elif criterion.evaluation_method == 'benchmark_analysis':
            return self._evaluate_performance(component)
        elif criterion.evaluation_method == 'security_assessment':
            return self._evaluate_security(component)
        elif criterion.evaluation_method == 'quality_metrics':
            return self._evaluate_maintainability(component)
        elif criterion.evaluation_method == 'compatibility_check':
            return self._evaluate_compatibility(component)
        elif criterion.evaluation_method == 'cost_analysis':
            return self._evaluate_cost_effectiveness(component)
        else:
            return 0.5  # 기본값

    def _evaluate_functional_coverage(self, component: Dict[str, Any]) -> float:
        """기능 커버리지 평가"""
        features = component.get('features', [])
        required_features = component.get('required_features', [])
        
        if not required_features:
            return 1.0
        
        covered = len(set(features) & set(required_features))
        return covered / len(required_features)

    def _evaluate_performance(self, component: Dict[str, Any]) -> float:
        """성능 평가"""
        benchmarks = component.get('benchmarks', {})
        
        # 간단한 성능 점수 계산
        scores = []
        
        if 'response_time' in benchmarks:
            # 응답시간이 낮을수록 좋음
            response_time = benchmarks['response_time']
            score = max(0, 1 - (response_time / 1000))  # 1초 기준
            scores.append(score)
        
        if 'throughput' in benchmarks:
            # 처리량이 높을수록 좋음
            throughput = benchmarks['throughput']
            score = min(1, throughput / 1000)  # 1000 RPS 기준
            scores.append(score)
        
        return np.mean(scores) if scores else 0.5

    def _evaluate_security(self, component: Dict[str, Any]) -> float:
        """보안 평가"""
        security_info = component.get('security', {})
        
        score = 0.5  # 기본 점수
        
        # 취약점 개수
        vulnerabilities = security_info.get('vulnerabilities', 0)
        if vulnerabilities == 0:
            score += 0.3
        elif vulnerabilities <= 2:
            score += 0.1
        else:
            score -= 0.2
        
        # 보안 인증
        if security_info.get('security_certified', False):
            score += 0.2
        
        # 최근 보안 업데이트
        if security_info.get('recent_security_update', False):
            score += 0.1
        
        return max(0, min(1, score))

    def _evaluate_maintainability(self, component: Dict[str, Any]) -> float:
        """유지보수성 평가"""
        maintenance = component.get('maintenance', {})
        
        scores = []
        
        # 코드 품질
        code_quality = maintenance.get('code_quality_score', 0.5)
        scores.append(code_quality)
        
        # 문서화 수준
        documentation = maintenance.get('documentation_score', 0.5)
        scores.append(documentation)
        
        # 커뮤니티 활성도
        community = maintenance.get('community_activity', 0.5)
        scores.append(community)
        
        # 업데이트 빈도
        update_frequency = maintenance.get('update_frequency', 0.5)
        scores.append(update_frequency)
        
        return np.mean(scores)

    def _evaluate_compatibility(self, component: Dict[str, Any]) -> float:
        """호환성 평가"""
        compatibility = component.get('compatibility', {})
        
        scores = []
        
        # 플랫폼 지원
        platform_support = compatibility.get('platform_support', 0.5)
        scores.append(platform_support)
        
        # 버전 호환성
        version_compatibility = compatibility.get('version_compatibility', 0.5)
        scores.append(version_compatibility)
        
        # API 안정성
        api_stability = compatibility.get('api_stability', 0.5)
        scores.append(api_stability)
        
        return np.mean(scores)

    def _evaluate_cost_effectiveness(self, component: Dict[str, Any]) -> float:
        """비용 효율성 평가"""
        cost_info = component.get('cost', {})
        
        # 라이선스 비용
        license_cost = cost_info.get('license_cost', 0)  # 0 = 무료
        
        # 구현 비용
        implementation_cost = cost_info.get('implementation_effort', 0.5)
        
        # 유지보수 비용
        maintenance_cost = cost_info.get('maintenance_cost', 0.5)
        
        # 총 비용 (낮을수록 좋음)
        total_cost = (license_cost + implementation_cost + maintenance_cost) / 3
        
        return 1 - total_cost


class DecisionThresholdManager:
    """결정 임계값 관리"""

    def __init__(self):
        self.thresholds = {
            'accept': 0.8,      # 즉시 수용
            'conditional': 0.6,  # 조건부 수용
            'review': 0.4,      # 재검토 필요
            'reject': 0.0       # 거부
        }

    def get_decision_level(self, score: float) -> str:
        """점수에 따른 결정 수준"""
        
        if score >= self.thresholds['accept']:
            return 'accept'
        elif score >= self.thresholds['conditional']:
            return 'conditional'
        elif score >= self.thresholds['review']:
            return 'review'
        else:
            return 'reject'

    def adjust_thresholds(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """컨텍스트에 따른 임계값 조정"""
        
        adjusted = self.thresholds.copy()
        
        # 엄격한 요구사항
        if context.get('strict_requirements', False):
            adjusted['accept'] = 0.9
            adjusted['conditional'] = 0.7
            adjusted['review'] = 0.5
        
        # 유연한 요구사항
        elif context.get('flexible_requirements', False):
            adjusted['accept'] = 0.7
            adjusted['conditional'] = 0.5
            adjusted['review'] = 0.3
        
        # 시간 압박
        if context.get('time_pressure', False):
            for key in adjusted:
                adjusted[key] *= 0.9  # 모든 임계값을 10% 낮춤
        
        return adjusted