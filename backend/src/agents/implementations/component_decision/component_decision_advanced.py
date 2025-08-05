# Task 4.5 계속: Component Decision Agent 고급 기능

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

# SubTask 4.5.2: 아키텍처 패턴 매칭 시스템
class ArchitecturePatternMatcher:
    """아키텍처 패턴 기반 컴포넌트 매칭"""

    def __init__(self):
        self.patterns = {
            'microservices': {
                'required_components': ['api_gateway', 'service_discovery', 'message_queue'],
                'recommended_components': ['monitoring', 'logging', 'circuit_breaker'],
                'anti_patterns': ['monolithic_database', 'shared_state']
            },
            'serverless': {
                'required_components': ['function_runtime', 'event_triggers'],
                'recommended_components': ['api_gateway', 'database_proxy'],
                'anti_patterns': ['persistent_connections', 'long_running_processes']
            },
            'event_driven': {
                'required_components': ['event_bus', 'event_store'],
                'recommended_components': ['saga_orchestrator', 'event_sourcing'],
                'anti_patterns': ['synchronous_coupling', 'shared_database']
            }
        }

    async def match_components_to_pattern(
        self,
        architecture_pattern: str,
        available_components: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """아키텍처 패턴에 맞는 컴포넌트 매칭"""

        if architecture_pattern not in self.patterns:
            return {'error': f'Unknown pattern: {architecture_pattern}'}

        pattern_config = self.patterns[architecture_pattern]
        
        # 필수 컴포넌트 매칭
        required_matches = await self._find_component_matches(
            pattern_config['required_components'],
            available_components
        )
        
        # 권장 컴포넌트 매칭
        recommended_matches = await self._find_component_matches(
            pattern_config['recommended_components'],
            available_components
        )
        
        # 안티패턴 검사
        anti_pattern_violations = await self._check_anti_patterns(
            pattern_config['anti_patterns'],
            available_components
        )

        return {
            'pattern': architecture_pattern,
            'required_components': required_matches,
            'recommended_components': recommended_matches,
            'anti_pattern_violations': anti_pattern_violations,
            'pattern_compliance_score': await self._calculate_compliance_score(
                required_matches, recommended_matches, anti_pattern_violations
            )
        }

    async def _find_component_matches(
        self,
        required_types: List[str],
        available_components: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """컴포넌트 타입별 매칭"""

        matches = {}
        
        for req_type in required_types:
            matches[req_type] = [
                comp for comp in available_components
                if comp.get('type') == req_type or req_type in comp.get('categories', [])
            ]

        return matches

# SubTask 4.5.3: 성능 예측 시스템
class PerformancePredictor:
    """컴포넌트 조합의 성능 예측"""

    def __init__(self):
        self.performance_models = {
            'latency': LatencyPredictor(),
            'throughput': ThroughputPredictor(),
            'resource_usage': ResourceUsagePredictor()
        }

    async def predict_performance(
        self,
        component_combination: List[ComponentOption],
        expected_load: Dict[str, Any]
    ) -> Dict[str, Any]:
        """성능 예측 수행"""

        predictions = {}
        
        for metric, predictor in self.performance_models.items():
            prediction = await predictor.predict(component_combination, expected_load)
            predictions[metric] = prediction

        # 종합 성능 점수
        overall_score = await self._calculate_overall_performance_score(predictions)

        return {
            'predictions': predictions,
            'overall_performance_score': overall_score,
            'bottlenecks': await self._identify_bottlenecks(predictions),
            'optimization_suggestions': await self._generate_optimization_suggestions(
                component_combination, predictions
            )
        }

class LatencyPredictor:
    """지연 시간 예측"""

    async def predict(
        self,
        components: List[ComponentOption],
        load: Dict[str, Any]
    ) -> Dict[str, float]:
        """지연 시간 예측"""

        # 컴포넌트별 기본 지연 시간
        base_latencies = {}
        for comp in components:
            base_latencies[comp.name] = await self._get_base_latency(comp)

        # 네트워크 지연 시간 추가
        network_latency = await self._calculate_network_latency(components)
        
        # 부하에 따른 지연 시간 증가
        load_factor = await self._calculate_load_factor(load)

        predictions = {}
        for comp_name, base_latency in base_latencies.items():
            predicted_latency = base_latency * load_factor + network_latency
            predictions[comp_name] = predicted_latency

        # 전체 시스템 지연 시간 (직렬 연결 가정)
        predictions['total_system_latency'] = sum(predictions.values())

        return predictions

    async def _get_base_latency(self, component: ComponentOption) -> float:
        """컴포넌트 기본 지연 시간 조회"""
        
        # 벤치마크 데이터베이스에서 조회
        benchmark_data = await self._query_benchmark_db(component.name)
        
        if benchmark_data:
            return benchmark_data.get('avg_latency_ms', 10.0)
        
        # 기본값 (컴포넌트 타입별)
        default_latencies = {
            'database': 5.0,
            'cache': 1.0,
            'api_gateway': 2.0,
            'message_queue': 3.0,
            'compute': 10.0
        }
        
        return default_latencies.get(component.type, 10.0)

# SubTask 4.5.4: 비용 최적화 시스템
class CostOptimizer:
    """비용 최적화 기반 컴포넌트 선택"""

    def __init__(self):
        self.cost_models = {
            'development': DevelopmentCostModel(),
            'operational': OperationalCostModel(),
            'maintenance': MaintenanceCostModel(),
            'licensing': LicensingCostModel()
        }

    async def optimize_for_cost(
        self,
        component_alternatives: List[List[ComponentOption]],
        budget_constraints: Dict[str, float],
        time_horizon: int = 24  # months
    ) -> Dict[str, Any]:
        """비용 최적화된 컴포넌트 조합 선택"""

        optimization_results = []

        for combination in component_alternatives:
            total_cost = await self._calculate_total_cost(combination, time_horizon)
            
            if await self._meets_budget_constraints(total_cost, budget_constraints):
                cost_breakdown = await self._get_cost_breakdown(combination, time_horizon)
                
                optimization_results.append({
                    'combination': combination,
                    'total_cost': total_cost,
                    'cost_breakdown': cost_breakdown,
                    'cost_efficiency_score': await self._calculate_cost_efficiency(
                        combination, total_cost
                    )
                })

        # 비용 효율성 기준 정렬
        optimization_results.sort(key=lambda x: x['cost_efficiency_score'], reverse=True)

        return {
            'optimal_combination': optimization_results[0] if optimization_results else None,
            'all_viable_options': optimization_results,
            'cost_savings_analysis': await self._analyze_cost_savings(optimization_results),
            'budget_utilization': await self._calculate_budget_utilization(
                optimization_results[0] if optimization_results else None,
                budget_constraints
            )
        }

    async def _calculate_total_cost(
        self,
        components: List[ComponentOption],
        time_horizon: int
    ) -> Dict[str, float]:
        """총 비용 계산"""

        total_costs = {
            'development': 0.0,
            'operational': 0.0,
            'maintenance': 0.0,
            'licensing': 0.0
        }

        for component in components:
            for cost_type, model in self.cost_models.items():
                cost = await model.calculate_cost(component, time_horizon)
                total_costs[cost_type] += cost

        total_costs['total'] = sum(total_costs.values())
        return total_costs

class DevelopmentCostModel:
    """개발 비용 모델"""

    async def calculate_cost(
        self,
        component: ComponentOption,
        time_horizon: int
    ) -> float:
        """개발 비용 계산"""

        # 기본 개발 시간 추정
        base_dev_time = await self._estimate_development_time(component)
        
        # 팀 숙련도에 따른 조정
        skill_factor = await self._get_skill_adjustment_factor(component)
        
        # 복잡도에 따른 조정
        complexity_factor = await self._get_complexity_factor(component)
        
        adjusted_dev_time = base_dev_time * skill_factor * complexity_factor
        
        # 시간당 개발 비용 (평균 개발자 시급)
        hourly_rate = 100.0  # USD
        
        return adjusted_dev_time * hourly_rate

    async def _estimate_development_time(self, component: ComponentOption) -> float:
        """개발 시간 추정 (시간 단위)"""
        
        # 컴포넌트 타입별 기본 개발 시간
        base_times = {
            'database': 40.0,
            'api_gateway': 60.0,
            'authentication': 80.0,
            'message_queue': 50.0,
            'monitoring': 30.0,
            'cache': 20.0
        }
        
        return base_times.get(component.type, 50.0)

# SubTask 4.5.5: 의사결정 검증 시스템
class DecisionValidator:
    """의사결정 결과 검증"""

    def __init__(self):
        self.validation_rules = [
            ArchitecturalConsistencyRule(),
            PerformanceRequirementRule(),
            SecurityComplianceRule(),
            BudgetConstraintRule(),
            TeamCapabilityRule()
        ]

    async def validate_decision(
        self,
        selected_components: List[ComponentOption],
        context: DecisionContext,
        decision_rationale: str
    ) -> Dict[str, Any]:
        """의사결정 검증"""

        validation_results = {
            'is_valid': True,
            'validation_score': 0.0,
            'rule_results': [],
            'warnings': [],
            'errors': [],
            'recommendations': []
        }

        total_score = 0.0
        rule_count = 0

        for rule in self.validation_rules:
            result = await rule.validate(selected_components, context)
            
            validation_results['rule_results'].append({
                'rule_name': rule.__class__.__name__,
                'passed': result['passed'],
                'score': result['score'],
                'message': result['message']
            })

            if not result['passed']:
                validation_results['is_valid'] = False
                validation_results['errors'].append(result['message'])
            
            if result.get('warning'):
                validation_results['warnings'].append(result['warning'])
            
            if result.get('recommendation'):
                validation_results['recommendations'].append(result['recommendation'])

            total_score += result['score']
            rule_count += 1

        validation_results['validation_score'] = total_score / rule_count if rule_count > 0 else 0

        return validation_results

class ArchitecturalConsistencyRule:
    """아키텍처 일관성 검증 규칙"""

    async def validate(
        self,
        components: List[ComponentOption],
        context: DecisionContext
    ) -> Dict[str, Any]:
        """아키텍처 일관성 검증"""

        # 아키텍처 패턴 추출
        intended_pattern = context.project_requirements.get('architecture_pattern')
        
        if not intended_pattern:
            return {
                'passed': True,
                'score': 7.0,
                'message': 'No specific architecture pattern specified',
                'warning': 'Consider defining architecture pattern for better consistency'
            }

        # 패턴 일관성 검사
        consistency_score = await self._check_pattern_consistency(
            components, intended_pattern
        )

        passed = consistency_score >= 7.0

        return {
            'passed': passed,
            'score': consistency_score,
            'message': f'Architecture consistency score: {consistency_score:.1f}/10',
            'recommendation': await self._generate_consistency_recommendation(
                components, intended_pattern, consistency_score
            ) if not passed else None
        }

    async def _check_pattern_consistency(
        self,
        components: List[ComponentOption],
        pattern: str
    ) -> float:
        """패턴 일관성 점수 계산"""

        pattern_requirements = {
            'microservices': {
                'required': ['api_gateway', 'service_discovery'],
                'discouraged': ['shared_database', 'monolithic_cache']
            },
            'serverless': {
                'required': ['function_runtime'],
                'discouraged': ['persistent_connections', 'stateful_services']
            }
        }

        if pattern not in pattern_requirements:
            return 5.0  # 중간 점수

        requirements = pattern_requirements[pattern]
        score = 10.0

        # 필수 컴포넌트 확인
        component_types = [comp.type for comp in components]
        for required in requirements['required']:
            if required not in component_types:
                score -= 2.0

        # 권장하지 않는 컴포넌트 확인
        for discouraged in requirements['discouraged']:
            if discouraged in component_types:
                score -= 1.5

        return max(0.0, score)

# SubTask 4.5.6: 실시간 모니터링 시스템
class DecisionMonitoringSystem:
    """의사결정 모니터링 및 피드백"""

    def __init__(self):
        self.metrics_collector = DecisionMetricsCollector()
        self.feedback_analyzer = FeedbackAnalyzer()
        self.decision_tracker = DecisionTracker()

    async def monitor_decision_outcomes(
        self,
        decision_id: str,
        monitoring_period: int = 30  # days
    ) -> Dict[str, Any]:
        """의사결정 결과 모니터링"""

        # 성과 메트릭 수집
        performance_metrics = await self.metrics_collector.collect_metrics(
            decision_id, monitoring_period
        )

        # 사용자 피드백 분석
        feedback_analysis = await self.feedback_analyzer.analyze_feedback(
            decision_id, monitoring_period
        )

        # 예측 vs 실제 비교
        prediction_accuracy = await self._compare_predictions_vs_actual(
            decision_id, performance_metrics
        )

        # 학습 포인트 추출
        learning_points = await self._extract_learning_points(
            decision_id, performance_metrics, feedback_analysis
        )

        return {
            'decision_id': decision_id,
            'monitoring_period_days': monitoring_period,
            'performance_metrics': performance_metrics,
            'feedback_analysis': feedback_analysis,
            'prediction_accuracy': prediction_accuracy,
            'learning_points': learning_points,
            'recommendations_for_future': await self._generate_future_recommendations(
                learning_points
            )
        }

class DecisionMetricsCollector:
    """의사결정 메트릭 수집기"""

    async def collect_metrics(
        self,
        decision_id: str,
        period_days: int
    ) -> Dict[str, Any]:
        """메트릭 수집"""

        # 개발 진행 메트릭
        development_metrics = await self._collect_development_metrics(
            decision_id, period_days
        )

        # 성능 메트릭
        performance_metrics = await self._collect_performance_metrics(
            decision_id, period_days
        )

        # 비용 메트릭
        cost_metrics = await self._collect_cost_metrics(
            decision_id, period_days
        )

        # 품질 메트릭
        quality_metrics = await self._collect_quality_metrics(
            decision_id, period_days
        )

        return {
            'development': development_metrics,
            'performance': performance_metrics,
            'cost': cost_metrics,
            'quality': quality_metrics,
            'overall_satisfaction_score': await self._calculate_overall_satisfaction(
                development_metrics, performance_metrics, cost_metrics, quality_metrics
            )
        }

    async def _collect_development_metrics(
        self,
        decision_id: str,
        period_days: int
    ) -> Dict[str, Any]:
        """개발 관련 메트릭 수집"""

        return {
            'development_velocity': await self._get_development_velocity(decision_id),
            'integration_issues_count': await self._count_integration_issues(decision_id),
            'time_to_first_deployment': await self._get_time_to_deployment(decision_id),
            'developer_productivity_score': await self._calculate_productivity_score(decision_id),
            'code_quality_metrics': await self._get_code_quality_metrics(decision_id)
        }

# 테스트 및 검증
class ComponentDecisionAgentTest:
    """Component Decision Agent 테스트"""

    async def run_comprehensive_test(self):
        """종합 테스트 실행"""

        # 테스트 데이터 준비
        test_requirements = {
            'functional': ['user_authentication', 'data_storage', 'api_endpoints'],
            'non_functional': ['high_availability', 'scalability', 'security'],
            'technical': ['microservices_architecture', 'cloud_native']
        }

        test_components = [
            {
                'name': 'PostgreSQL',
                'type': 'database',
                'description': 'Relational database',
                'dependencies': ['libpq'],
                'license': 'PostgreSQL'
            },
            {
                'name': 'Redis',
                'type': 'cache',
                'description': 'In-memory cache',
                'dependencies': [],
                'license': 'BSD'
            },
            {
                'name': 'Kong',
                'type': 'api_gateway',
                'description': 'API Gateway',
                'dependencies': ['nginx'],
                'license': 'Apache-2.0'
            }
        ]

        # 에이전트 초기화
        agent = ComponentDecisionAgent()

        # 의사결정 실행
        result = await agent.make_component_decisions(
            test_requirements, test_components
        )

        # 결과 검증
        assert 'selected_components' in result
        assert 'decision_rationale' in result
        assert 'risk_assessment' in result

        print("✅ Component Decision Agent test passed")
        return result

if __name__ == "__main__":
    # 테스트 실행
    test = ComponentDecisionAgentTest()
    asyncio.run(test.run_comprehensive_test())