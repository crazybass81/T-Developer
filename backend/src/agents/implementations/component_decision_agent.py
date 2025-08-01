# Task 4.5: Component Decision Agent 구현

from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory import ConversationSummaryMemory
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
import json
from enum import Enum

class DecisionCriteria(Enum):
    PERFORMANCE = "performance"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"
    SECURITY = "security"
    COST = "cost"
    TEAM_EXPERTISE = "team_expertise"

@dataclass
class ComponentOption:
    name: str
    type: str
    description: str
    pros: List[str]
    cons: List[str]
    score: float
    criteria_scores: Dict[str, float]
    dependencies: List[str]
    license: str
    maturity_level: str

@dataclass
class DecisionContext:
    project_requirements: Dict[str, Any]
    technical_constraints: Dict[str, Any]
    team_capabilities: Dict[str, Any]
    budget_constraints: Dict[str, Any]
    timeline: str

class ComponentDecisionAgent:
    """컴포넌트 선택을 위한 의사결정 에이전트"""

    def __init__(self):
        self.agent = Agent(
            name="Component-Decision-Maker",
            model=AwsBedrock(
                id="anthropic.claude-3-opus-v1:0",
                region="us-east-1"
            ),
            role="Senior software architect specializing in component selection",
            instructions=[
                "분석된 요구사항을 바탕으로 최적의 컴포넌트 조합 결정",
                "성능, 확장성, 유지보수성, 보안성을 종합적으로 고려",
                "팀의 기술 역량과 프로젝트 제약사항 반영",
                "의사결정 근거를 명확하게 제시",
                "대안 옵션과 트레이드오프 분석 제공"
            ],
            memory=ConversationSummaryMemory(
                storage_type="dynamodb",
                table_name="t-dev-decision-context"
            ),
            tools=[
                ComponentEvaluator(),
                PerformanceBenchmarker(),
                SecurityAnalyzer(),
                CostCalculator(),
                CompatibilityChecker()
            ],
            temperature=0.2
        )
        
        self.decision_engine = DecisionEngine()
        self.component_registry = ComponentRegistry()

    async def make_component_decisions(
        self,
        parsed_requirements: Dict[str, Any],
        available_components: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """컴포넌트 의사결정 수행"""

        # 1. 의사결정 컨텍스트 구성
        context = await self._build_decision_context(parsed_requirements)

        # 2. 컴포넌트 옵션 평가
        evaluated_options = await self._evaluate_component_options(
            available_components, context
        )

        # 3. 최적 조합 결정
        optimal_combination = await self._find_optimal_combination(
            evaluated_options, context
        )

        # 4. 의사결정 검증
        validation_result = await self._validate_decisions(
            optimal_combination, context
        )

        return {
            "selected_components": optimal_combination,
            "decision_rationale": validation_result.rationale,
            "alternatives": validation_result.alternatives,
            "risk_assessment": validation_result.risks,
            "implementation_plan": await self._generate_implementation_plan(
                optimal_combination
            )
        }

    async def _evaluate_component_options(
        self,
        components: List[Dict[str, Any]],
        context: DecisionContext
    ) -> List[ComponentOption]:
        """컴포넌트 옵션들을 평가"""

        evaluation_tasks = []
        for component in components:
            task = asyncio.create_task(
                self._evaluate_single_component(component, context)
            )
            evaluation_tasks.append(task)

        evaluated_components = await asyncio.gather(*evaluation_tasks)
        
        # 점수 기준으로 정렬
        return sorted(evaluated_components, key=lambda x: x.score, reverse=True)

    async def _evaluate_single_component(
        self,
        component: Dict[str, Any],
        context: DecisionContext
    ) -> ComponentOption:
        """단일 컴포넌트 평가"""

        # AI 에이전트를 통한 종합 평가
        evaluation_prompt = f"""
        다음 컴포넌트를 프로젝트 요구사항에 맞춰 평가해주세요:

        컴포넌트: {component['name']}
        설명: {component.get('description', '')}
        
        프로젝트 요구사항:
        - 기능 요구사항: {context.project_requirements.get('functional', [])}
        - 비기능 요구사항: {context.project_requirements.get('non_functional', [])}
        - 기술적 제약사항: {context.technical_constraints}
        
        다음 기준으로 평가 (1-10점):
        1. 성능 (Performance)
        2. 확장성 (Scalability)  
        3. 유지보수성 (Maintainability)
        4. 보안성 (Security)
        5. 비용 효율성 (Cost Efficiency)
        6. 팀 적합성 (Team Fit)

        각 기준별 점수와 근거를 제시하고, 장단점을 명확히 분석해주세요.
        """

        evaluation_result = await self.agent.arun(evaluation_prompt)
        
        # 평가 결과 파싱
        parsed_evaluation = await self._parse_evaluation_result(
            evaluation_result, component
        )

        return ComponentOption(
            name=component['name'],
            type=component.get('type', 'unknown'),
            description=component.get('description', ''),
            pros=parsed_evaluation['pros'],
            cons=parsed_evaluation['cons'],
            score=parsed_evaluation['overall_score'],
            criteria_scores=parsed_evaluation['criteria_scores'],
            dependencies=component.get('dependencies', []),
            license=component.get('license', 'unknown'),
            maturity_level=component.get('maturity', 'stable')
        )

class DecisionEngine:
    """의사결정 엔진"""

    def __init__(self):
        self.criteria_weights = {
            DecisionCriteria.PERFORMANCE: 0.25,
            DecisionCriteria.SCALABILITY: 0.20,
            DecisionCriteria.MAINTAINABILITY: 0.20,
            DecisionCriteria.SECURITY: 0.15,
            DecisionCriteria.COST: 0.10,
            DecisionCriteria.TEAM_EXPERTISE: 0.10
        }

    async def calculate_weighted_score(
        self,
        component: ComponentOption,
        context: DecisionContext
    ) -> float:
        """가중치를 적용한 종합 점수 계산"""

        # 프로젝트 특성에 따른 가중치 조정
        adjusted_weights = await self._adjust_weights_for_context(context)

        weighted_score = 0.0
        for criteria, weight in adjusted_weights.items():
            criteria_score = component.criteria_scores.get(criteria.value, 5.0)
            weighted_score += criteria_score * weight

        return weighted_score

    async def _adjust_weights_for_context(
        self,
        context: DecisionContext
    ) -> Dict[DecisionCriteria, float]:
        """컨텍스트에 따른 가중치 조정"""

        weights = self.criteria_weights.copy()

        # 프로젝트 유형별 가중치 조정
        project_type = context.project_requirements.get('type', 'web')
        
        if project_type == 'enterprise':
            weights[DecisionCriteria.SECURITY] *= 1.5
            weights[DecisionCriteria.MAINTAINABILITY] *= 1.3
        elif project_type == 'startup':
            weights[DecisionCriteria.COST] *= 1.5
            weights[DecisionCriteria.PERFORMANCE] *= 1.2
        elif project_type == 'high_traffic':
            weights[DecisionCriteria.PERFORMANCE] *= 1.8
            weights[DecisionCriteria.SCALABILITY] *= 1.6

        # 정규화
        total_weight = sum(weights.values())
        return {k: v/total_weight for k, v in weights.items()}

class ComponentEvaluator:
    """컴포넌트 평가 도구"""

    async def evaluate_performance(self, component: Dict[str, Any]) -> float:
        """성능 평가"""
        # 벤치마크 데이터, 커뮤니티 피드백 등을 종합
        performance_indicators = {
            'throughput': component.get('throughput_rps', 0),
            'latency': component.get('avg_latency_ms', 1000),
            'memory_usage': component.get('memory_mb', 100),
            'cpu_efficiency': component.get('cpu_efficiency', 0.5)
        }
        
        # 정규화된 점수 계산
        score = await self._calculate_performance_score(performance_indicators)
        return min(10.0, max(1.0, score))

    async def evaluate_security(self, component: Dict[str, Any]) -> float:
        """보안성 평가"""
        security_factors = {
            'vulnerability_count': component.get('known_vulnerabilities', 0),
            'last_security_update': component.get('last_security_update', ''),
            'security_certifications': component.get('certifications', []),
            'encryption_support': component.get('supports_encryption', False)
        }
        
        score = await self._calculate_security_score(security_factors)
        return min(10.0, max(1.0, score))

class CompatibilityChecker:
    """호환성 검사 도구"""

    async def check_compatibility(
        self,
        components: List[ComponentOption]
    ) -> Dict[str, Any]:
        """컴포넌트 간 호환성 검사"""

        compatibility_matrix = {}
        conflicts = []
        
        for i, comp1 in enumerate(components):
            for j, comp2 in enumerate(components[i+1:], i+1):
                compatibility = await self._check_pair_compatibility(comp1, comp2)
                
                key = f"{comp1.name}-{comp2.name}"
                compatibility_matrix[key] = compatibility
                
                if compatibility['status'] == 'conflict':
                    conflicts.append({
                        'component1': comp1.name,
                        'component2': comp2.name,
                        'issue': compatibility['issue'],
                        'severity': compatibility['severity']
                    })

        return {
            'compatibility_matrix': compatibility_matrix,
            'conflicts': conflicts,
            'overall_compatibility': len(conflicts) == 0
        }

    async def _check_pair_compatibility(
        self,
        comp1: ComponentOption,
        comp2: ComponentOption
    ) -> Dict[str, Any]:
        """두 컴포넌트 간 호환성 검사"""

        # 의존성 충돌 검사
        dependency_conflicts = set(comp1.dependencies) & set(comp2.dependencies)
        
        # 라이선스 호환성 검사
        license_compatible = await self._check_license_compatibility(
            comp1.license, comp2.license
        )
        
        # 기술 스택 호환성
        tech_compatible = await self._check_tech_compatibility(comp1, comp2)

        if dependency_conflicts:
            return {
                'status': 'conflict',
                'issue': f'Dependency conflicts: {list(dependency_conflicts)}',
                'severity': 'high'
            }
        elif not license_compatible:
            return {
                'status': 'warning',
                'issue': 'License compatibility concerns',
                'severity': 'medium'
            }
        elif not tech_compatible:
            return {
                'status': 'warning',
                'issue': 'Technology stack mismatch',
                'severity': 'low'
            }
        else:
            return {
                'status': 'compatible',
                'issue': None,
                'severity': None
            }

# SubTask 4.5.2: 다중 기준 의사결정 시스템
class MultiCriteriaDecisionSystem:
    """다중 기준 의사결정 시스템 (MCDM)"""

    def __init__(self):
        self.methods = {
            'ahp': self._analytic_hierarchy_process,
            'topsis': self._topsis_method,
            'weighted_sum': self._weighted_sum_method
        }

    async def make_decision(
        self,
        alternatives: List[ComponentOption],
        criteria: Dict[str, float],
        method: str = 'topsis'
    ) -> Dict[str, Any]:
        """다중 기준 의사결정 수행"""

        if method not in self.methods:
            raise ValueError(f"Unknown method: {method}")

        decision_method = self.methods[method]
        result = await decision_method(alternatives, criteria)

        return {
            'method_used': method,
            'ranking': result['ranking'],
            'scores': result['scores'],
            'sensitivity_analysis': await self._sensitivity_analysis(
                alternatives, criteria, method
            )
        }

    async def _topsis_method(
        self,
        alternatives: List[ComponentOption],
        criteria: Dict[str, float]
    ) -> Dict[str, Any]:
        """TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)"""

        import numpy as np

        # 의사결정 매트릭스 구성
        matrix = []
        for alt in alternatives:
            row = [alt.criteria_scores.get(criterion, 5.0) for criterion in criteria.keys()]
            matrix.append(row)

        matrix = np.array(matrix)
        
        # 정규화
        normalized = matrix / np.sqrt(np.sum(matrix**2, axis=0))
        
        # 가중치 적용
        weights = np.array(list(criteria.values()))
        weighted = normalized * weights
        
        # 이상적 해와 부정적 이상적 해
        ideal_positive = np.max(weighted, axis=0)
        ideal_negative = np.min(weighted, axis=0)
        
        # 거리 계산
        distances_positive = np.sqrt(np.sum((weighted - ideal_positive)**2, axis=1))
        distances_negative = np.sqrt(np.sum((weighted - ideal_negative)**2, axis=1))
        
        # TOPSIS 점수
        scores = distances_negative / (distances_positive + distances_negative)
        
        # 순위 매기기
        ranking = sorted(
            zip(alternatives, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            'ranking': [(alt.name, score) for alt, score in ranking],
            'scores': dict(zip([alt.name for alt in alternatives], scores))
        }

# SubTask 4.5.3: 리스크 평가 시스템
class RiskAssessmentSystem:
    """컴포넌트 선택 리스크 평가"""

    def __init__(self):
        self.risk_categories = {
            'technical': TechnicalRiskAnalyzer(),
            'operational': OperationalRiskAnalyzer(),
            'strategic': StrategicRiskAnalyzer(),
            'compliance': ComplianceRiskAnalyzer()
        }

    async def assess_risks(
        self,
        selected_components: List[ComponentOption],
        context: DecisionContext
    ) -> Dict[str, Any]:
        """종합 리스크 평가"""

        risk_assessment = {
            'overall_risk_level': 'low',
            'risk_categories': {},
            'mitigation_strategies': [],
            'monitoring_recommendations': []
        }

        total_risk_score = 0
        category_count = 0

        for category, analyzer in self.risk_categories.items():
            category_risks = await analyzer.analyze(selected_components, context)
            
            risk_assessment['risk_categories'][category] = category_risks
            total_risk_score += category_risks['risk_score']
            category_count += 1

            # 완화 전략 수집
            risk_assessment['mitigation_strategies'].extend(
                category_risks.get('mitigation_strategies', [])
            )

        # 전체 리스크 레벨 결정
        avg_risk_score = total_risk_score / category_count
        if avg_risk_score > 7:
            risk_assessment['overall_risk_level'] = 'high'
        elif avg_risk_score > 4:
            risk_assessment['overall_risk_level'] = 'medium'

        return risk_assessment

class TechnicalRiskAnalyzer:
    """기술적 리스크 분석"""

    async def analyze(
        self,
        components: List[ComponentOption],
        context: DecisionContext
    ) -> Dict[str, Any]:
        """기술적 리스크 분석"""

        risks = []
        risk_score = 0

        for component in components:
            # 성숙도 리스크
            if component.maturity_level in ['alpha', 'beta']:
                risks.append({
                    'type': 'maturity',
                    'component': component.name,
                    'description': f'{component.name} is in {component.maturity_level} stage',
                    'impact': 'high',
                    'probability': 'medium'
                })
                risk_score += 3

            # 의존성 리스크
            if len(component.dependencies) > 10:
                risks.append({
                    'type': 'dependency_complexity',
                    'component': component.name,
                    'description': f'High number of dependencies ({len(component.dependencies)})',
                    'impact': 'medium',
                    'probability': 'high'
                })
                risk_score += 2

            # 성능 리스크
            performance_score = component.criteria_scores.get('performance', 5)
            if performance_score < 6:
                risks.append({
                    'type': 'performance',
                    'component': component.name,
                    'description': 'Below average performance rating',
                    'impact': 'high',
                    'probability': 'medium'
                })
                risk_score += 2

        return {
            'risks': risks,
            'risk_score': min(10, risk_score),
            'mitigation_strategies': await self._generate_mitigation_strategies(risks)
        }

    async def _generate_mitigation_strategies(
        self,
        risks: List[Dict[str, Any]]
    ) -> List[str]:
        """완화 전략 생성"""

        strategies = []
        
        for risk in risks:
            if risk['type'] == 'maturity':
                strategies.append(
                    f"Monitor {risk['component']} development closely and have fallback options ready"
                )
            elif risk['type'] == 'dependency_complexity':
                strategies.append(
                    f"Implement dependency management strategy for {risk['component']}"
                )
            elif risk['type'] == 'performance':
                strategies.append(
                    f"Conduct performance testing and optimization for {risk['component']}"
                )

        return strategies

# SubTask 4.5.4: 의사결정 추적 시스템
class DecisionTrackingSystem:
    """의사결정 과정 추적 및 기록"""

    def __init__(self):
        self.decision_history = []
        self.decision_rationale_db = DecisionRationaleDB()

    async def track_decision(
        self,
        decision_id: str,
        context: DecisionContext,
        alternatives: List[ComponentOption],
        selected: List[ComponentOption],
        rationale: str
    ):
        """의사결정 추적"""

        decision_record = {
            'decision_id': decision_id,
            'timestamp': datetime.utcnow().isoformat(),
            'context': {
                'project_type': context.project_requirements.get('type'),
                'constraints': context.technical_constraints,
                'team_size': context.team_capabilities.get('size'),
                'budget_level': context.budget_constraints.get('level')
            },
            'alternatives_considered': [
                {
                    'name': alt.name,
                    'score': alt.score,
                    'pros': alt.pros,
                    'cons': alt.cons
                }
                for alt in alternatives
            ],
            'selected_components': [
                {
                    'name': comp.name,
                    'selection_reason': rationale
                }
                for comp in selected
            ],
            'decision_criteria': await self._extract_decision_criteria(context),
            'decision_maker': 'ComponentDecisionAgent',
            'confidence_level': await self._calculate_confidence_level(selected, alternatives)
        }

        # 저장
        await self.decision_rationale_db.store_decision(decision_record)
        self.decision_history.append(decision_record)

        return decision_record

    async def generate_decision_report(
        self,
        decision_id: str
    ) -> Dict[str, Any]:
        """의사결정 보고서 생성"""

        decision = await self.decision_rationale_db.get_decision(decision_id)
        
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")

        report = {
            'executive_summary': await self._generate_executive_summary(decision),
            'detailed_analysis': await self._generate_detailed_analysis(decision),
            'risk_assessment': await self._generate_risk_summary(decision),
            'implementation_roadmap': await self._generate_implementation_roadmap(decision),
            'success_metrics': await self._define_success_metrics(decision),
            'review_schedule': await self._create_review_schedule(decision)
        }

        return report

    async def _generate_executive_summary(
        self,
        decision: Dict[str, Any]
    ) -> str:
        """경영진 요약 생성"""

        selected_names = [comp['name'] for comp in decision['selected_components']]
        
        summary = f"""
        ## 컴포넌트 선택 의사결정 요약

        **선택된 컴포넌트**: {', '.join(selected_names)}
        
        **의사결정 근거**: 
        {decision.get('rationale', '상세 분석을 통한 최적 선택')}
        
        **예상 효과**:
        - 개발 시간 단축
        - 유지보수성 향상
        - 확장성 확보
        
        **주요 리스크**: 
        {await self._summarize_key_risks(decision)}
        
        **권장 사항**:
        - 단계적 구현 접근
        - 지속적 모니터링
        - 팀 교육 실시
        """

        return summary.strip()