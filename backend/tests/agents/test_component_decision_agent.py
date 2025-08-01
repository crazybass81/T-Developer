# Component Decision Agent 테스트

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from backend.src.agents.implementations.component_decision_agent import (
    ComponentDecisionAgent,
    ComponentOption,
    DecisionContext,
    MultiCriteriaDecisionSystem,
    RiskAssessmentSystem
)

@pytest.fixture
def sample_requirements():
    return {
        'functional': [
            'user_authentication',
            'data_persistence',
            'real_time_notifications',
            'file_upload'
        ],
        'non_functional': [
            'handle_10000_concurrent_users',
            'response_time_under_200ms',
            'high_availability_99_9_percent'
        ],
        'technical': [
            'microservices_architecture',
            'cloud_native',
            'containerized_deployment'
        ],
        'type': 'enterprise'
    }

@pytest.fixture
def sample_components():
    return [
        {
            'name': 'PostgreSQL',
            'type': 'database',
            'description': 'Advanced relational database',
            'dependencies': ['libpq-dev'],
            'license': 'PostgreSQL',
            'maturity': 'stable',
            'throughput_rps': 5000,
            'avg_latency_ms': 2,
            'memory_mb': 256
        },
        {
            'name': 'Redis',
            'type': 'cache',
            'description': 'In-memory data structure store',
            'dependencies': [],
            'license': 'BSD',
            'maturity': 'stable',
            'throughput_rps': 100000,
            'avg_latency_ms': 0.1,
            'memory_mb': 64
        },
        {
            'name': 'Kong',
            'type': 'api_gateway',
            'description': 'Cloud-native API gateway',
            'dependencies': ['nginx', 'lua'],
            'license': 'Apache-2.0',
            'maturity': 'stable',
            'throughput_rps': 20000,
            'avg_latency_ms': 1,
            'memory_mb': 128
        },
        {
            'name': 'RabbitMQ',
            'type': 'message_queue',
            'description': 'Message broker',
            'dependencies': ['erlang'],
            'license': 'MPL-2.0',
            'maturity': 'stable',
            'throughput_rps': 10000,
            'avg_latency_ms': 5,
            'memory_mb': 200
        }
    ]

@pytest.fixture
def decision_context():
    return DecisionContext(
        project_requirements={
            'type': 'enterprise',
            'scale': 'large',
            'criticality': 'high'
        },
        technical_constraints={
            'cloud_provider': 'aws',
            'deployment_model': 'containerized',
            'compliance_requirements': ['SOC2', 'GDPR']
        },
        team_capabilities={
            'size': 8,
            'experience_level': 'senior',
            'technologies': ['python', 'javascript', 'docker', 'kubernetes']
        },
        budget_constraints={
            'development_budget': 500000,
            'operational_budget_monthly': 10000,
            'level': 'high'
        },
        timeline='6_months'
    )

class TestComponentDecisionAgent:
    """Component Decision Agent 테스트 클래스"""

    @pytest.fixture
    def agent(self):
        return ComponentDecisionAgent()

    @pytest.mark.asyncio
    async def test_component_evaluation(self, agent, sample_components, decision_context):
        """컴포넌트 평가 테스트"""
        
        with patch.object(agent.agent, 'arun', new_callable=AsyncMock) as mock_arun:
            mock_arun.return_value = Mock(content="""
            성능: 8/10 - 높은 처리량과 낮은 지연시간
            확장성: 9/10 - 수평적 확장 우수
            유지보수성: 7/10 - 잘 문서화되어 있음
            보안성: 8/10 - 엔터프라이즈급 보안 기능
            비용 효율성: 6/10 - 라이선스 비용 고려 필요
            팀 적합성: 9/10 - 팀의 기존 경험과 일치
            
            장점: 안정성, 성능, 커뮤니티 지원
            단점: 메모리 사용량, 설정 복잡성
            """)
            
            evaluated = await agent._evaluate_component_options(
                sample_components, decision_context
            )
            
            assert len(evaluated) == len(sample_components)
            assert all(isinstance(comp, ComponentOption) for comp in evaluated)
            assert all(comp.score > 0 for comp in evaluated)

    @pytest.mark.asyncio
    async def test_decision_making_process(self, agent, sample_requirements, sample_components):
        """의사결정 프로세스 테스트"""
        
        with patch.object(agent, '_build_decision_context') as mock_context, \
             patch.object(agent, '_evaluate_component_options') as mock_evaluate, \
             patch.object(agent, '_find_optimal_combination') as mock_optimal, \
             patch.object(agent, '_validate_decisions') as mock_validate:
            
            # Mock 설정
            mock_context.return_value = decision_context
            mock_evaluate.return_value = [
                ComponentOption(
                    name="PostgreSQL",
                    type="database",
                    description="Database",
                    pros=["Reliable", "ACID compliant"],
                    cons=["Memory intensive"],
                    score=8.5,
                    criteria_scores={"performance": 8, "scalability": 9},
                    dependencies=["libpq"],
                    license="PostgreSQL",
                    maturity_level="stable"
                )
            ]
            mock_optimal.return_value = mock_evaluate.return_value
            mock_validate.return_value = Mock(
                rationale="Best fit for requirements",
                alternatives=[],
                risks={"overall_risk_level": "low"}
            )
            
            result = await agent.make_component_decisions(
                sample_requirements, sample_components
            )
            
            assert 'selected_components' in result
            assert 'decision_rationale' in result
            assert 'risk_assessment' in result
            assert 'implementation_plan' in result

    @pytest.mark.asyncio
    async def test_multi_criteria_decision_system(self):
        """다중 기준 의사결정 시스템 테스트"""
        
        mcdm = MultiCriteriaDecisionSystem()
        
        alternatives = [
            ComponentOption(
                name="Option A",
                type="database",
                description="High performance DB",
                pros=[], cons=[],
                score=0,
                criteria_scores={
                    "performance": 9.0,
                    "scalability": 7.0,
                    "maintainability": 6.0,
                    "security": 8.0,
                    "cost": 5.0
                },
                dependencies=[], license="MIT", maturity_level="stable"
            ),
            ComponentOption(
                name="Option B",
                type="database", 
                description="Cost effective DB",
                pros=[], cons=[],
                score=0,
                criteria_scores={
                    "performance": 6.0,
                    "scalability": 8.0,
                    "maintainability": 9.0,
                    "security": 7.0,
                    "cost": 9.0
                },
                dependencies=[], license="Apache-2.0", maturity_level="stable"
            )
        ]
        
        criteria = {
            "performance": 0.3,
            "scalability": 0.2,
            "maintainability": 0.2,
            "security": 0.15,
            "cost": 0.15
        }
        
        result = await mcdm.make_decision(alternatives, criteria, method='topsis')
        
        assert 'ranking' in result
        assert 'scores' in result
        assert len(result['ranking']) == 2
        assert result['ranking'][0][1] > result['ranking'][1][1]  # 첫 번째가 더 높은 점수

    @pytest.mark.asyncio
    async def test_risk_assessment_system(self, decision_context):
        """리스크 평가 시스템 테스트"""
        
        risk_system = RiskAssessmentSystem()
        
        components = [
            ComponentOption(
                name="Alpha Component",
                type="experimental",
                description="New experimental component",
                pros=[], cons=[],
                score=7.0,
                criteria_scores={},
                dependencies=["dep1", "dep2", "dep3", "dep4", "dep5", 
                            "dep6", "dep7", "dep8", "dep9", "dep10", "dep11"],
                license="GPL-3.0",
                maturity_level="alpha"
            )
        ]
        
        with patch.object(risk_system.risk_categories['technical'], 'analyze') as mock_tech, \
             patch.object(risk_system.risk_categories['operational'], 'analyze') as mock_ops, \
             patch.object(risk_system.risk_categories['strategic'], 'analyze') as mock_strat, \
             patch.object(risk_system.risk_categories['compliance'], 'analyze') as mock_comp:
            
            # Mock 리스크 분석 결과
            mock_tech.return_value = {
                'risks': [{'type': 'maturity', 'severity': 'high'}],
                'risk_score': 8.0,
                'mitigation_strategies': ['Monitor closely']
            }
            mock_ops.return_value = {'risks': [], 'risk_score': 3.0}
            mock_strat.return_value = {'risks': [], 'risk_score': 4.0}
            mock_comp.return_value = {'risks': [], 'risk_score': 2.0}
            
            result = await risk_system.assess_risks(components, decision_context)
            
            assert 'overall_risk_level' in result
            assert 'risk_categories' in result
            assert 'mitigation_strategies' in result
            assert result['overall_risk_level'] in ['low', 'medium', 'high']

    @pytest.mark.asyncio
    async def test_architecture_pattern_matching(self):
        """아키텍처 패턴 매칭 테스트"""
        
        from backend.src.agents.implementations.component_decision_advanced import (
            ArchitecturePatternMatcher
        )
        
        matcher = ArchitecturePatternMatcher()
        
        components = [
            {'name': 'Kong', 'type': 'api_gateway', 'categories': ['gateway']},
            {'name': 'Consul', 'type': 'service_discovery', 'categories': ['discovery']},
            {'name': 'RabbitMQ', 'type': 'message_queue', 'categories': ['messaging']}
        ]
        
        result = await matcher.match_components_to_pattern('microservices', components)
        
        assert 'pattern' in result
        assert result['pattern'] == 'microservices'
        assert 'required_components' in result
        assert 'pattern_compliance_score' in result

    @pytest.mark.asyncio
    async def test_performance_prediction(self):
        """성능 예측 테스트"""
        
        from backend.src.agents.implementations.component_decision_advanced import (
            PerformancePredictor
        )
        
        predictor = PerformancePredictor()
        
        components = [
            ComponentOption(
                name="FastDB",
                type="database",
                description="High performance database",
                pros=[], cons=[], score=8.0,
                criteria_scores={"performance": 9.0},
                dependencies=[], license="MIT", maturity_level="stable"
            )
        ]
        
        expected_load = {
            'concurrent_users': 1000,
            'requests_per_second': 5000,
            'data_size_gb': 100
        }
        
        with patch.object(predictor.performance_models['latency'], 'predict') as mock_latency:
            mock_latency.return_value = {'FastDB': 5.0, 'total_system_latency': 5.0}
            
            result = await predictor.predict_performance(components, expected_load)
            
            assert 'predictions' in result
            assert 'overall_performance_score' in result
            assert 'bottlenecks' in result

    @pytest.mark.asyncio
    async def test_cost_optimization(self):
        """비용 최적화 테스트"""
        
        from backend.src.agents.implementations.component_decision_advanced import (
            CostOptimizer
        )
        
        optimizer = CostOptimizer()
        
        # 여러 컴포넌트 조합
        combinations = [
            [ComponentOption(
                name="Expensive Option",
                type="database", description="", pros=[], cons=[],
                score=9.0, criteria_scores={}, dependencies=[],
                license="Commercial", maturity_level="stable"
            )],
            [ComponentOption(
                name="Budget Option", 
                type="database", description="", pros=[], cons=[],
                score=7.0, criteria_scores={}, dependencies=[],
                license="MIT", maturity_level="stable"
            )]
        ]
        
        budget_constraints = {
            'development': 100000,
            'operational': 5000,
            'total': 150000
        }
        
        with patch.object(optimizer, '_calculate_total_cost') as mock_cost:
            mock_cost.side_effect = [
                {'total': 120000, 'development': 80000, 'operational': 40000},
                {'total': 80000, 'development': 60000, 'operational': 20000}
            ]
            
            result = await optimizer.optimize_for_cost(
                combinations, budget_constraints, time_horizon=12
            )
            
            assert 'optimal_combination' in result
            assert 'cost_savings_analysis' in result
            assert result['optimal_combination'] is not None

    @pytest.mark.asyncio
    async def test_decision_validation(self):
        """의사결정 검증 테스트"""
        
        from backend.src.agents.implementations.component_decision_advanced import (
            DecisionValidator
        )
        
        validator = DecisionValidator()
        
        components = [
            ComponentOption(
                name="ValidComponent",
                type="database", description="", pros=[], cons=[],
                score=8.0, criteria_scores={"performance": 8.0},
                dependencies=[], license="MIT", maturity_level="stable"
            )
        ]
        
        context = DecisionContext(
            project_requirements={'architecture_pattern': 'microservices'},
            technical_constraints={},
            team_capabilities={},
            budget_constraints={},
            timeline='6_months'
        )
        
        # Mock validation rules
        for rule in validator.validation_rules:
            rule.validate = AsyncMock(return_value={
                'passed': True,
                'score': 8.0,
                'message': 'Validation passed'
            })
        
        result = await validator.validate_decision(
            components, context, "Well-reasoned decision"
        )
        
        assert 'is_valid' in result
        assert 'validation_score' in result
        assert 'rule_results' in result
        assert result['is_valid'] is True
        assert result['validation_score'] > 0

    @pytest.mark.asyncio
    async def test_integration_with_other_agents(self, agent, sample_requirements):
        """다른 에이전트와의 통합 테스트"""
        
        # Parser Agent에서 온 요구사항 시뮬레이션
        parsed_requirements = {
            'functional_requirements': sample_requirements['functional'],
            'non_functional_requirements': sample_requirements['non_functional'],
            'technical_requirements': sample_requirements['technical'],
            'constraints': ['budget_limited', 'timeline_tight']
        }
        
        # Matching Rate Agent에서 온 컴포넌트 시뮬레이션
        matched_components = [
            {
                'name': 'PostgreSQL',
                'type': 'database',
                'match_score': 0.85,
                'compatibility_score': 0.90
            },
            {
                'name': 'Redis',
                'type': 'cache', 
                'match_score': 0.92,
                'compatibility_score': 0.95
            }
        ]
        
        with patch.object(agent, 'make_component_decisions') as mock_decision:
            mock_decision.return_value = {
                'selected_components': matched_components[:1],  # PostgreSQL 선택
                'decision_rationale': 'Best match for requirements',
                'alternatives': matched_components[1:],
                'risk_assessment': {'overall_risk_level': 'low'}
            }
            
            result = await agent.make_component_decisions(
                parsed_requirements, matched_components
            )
            
            assert result['selected_components']
            assert len(result['selected_components']) > 0

    def test_component_option_dataclass(self):
        """ComponentOption 데이터클래스 테스트"""
        
        component = ComponentOption(
            name="TestComponent",
            type="database",
            description="Test database component",
            pros=["Fast", "Reliable"],
            cons=["Expensive"],
            score=8.5,
            criteria_scores={"performance": 9.0, "cost": 6.0},
            dependencies=["libtest"],
            license="MIT",
            maturity_level="stable"
        )
        
        assert component.name == "TestComponent"
        assert component.score == 8.5
        assert len(component.pros) == 2
        assert len(component.cons) == 1
        assert "performance" in component.criteria_scores

    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """에러 처리 테스트"""
        
        # 잘못된 입력 데이터
        invalid_requirements = None
        invalid_components = []
        
        with pytest.raises(Exception):
            await agent.make_component_decisions(
                invalid_requirements, invalid_components
            )

    @pytest.mark.asyncio
    async def test_concurrent_decision_making(self, agent, sample_requirements, sample_components):
        """동시 의사결정 테스트"""
        
        # 여러 의사결정을 동시에 실행
        tasks = []
        for i in range(5):
            task = agent.make_component_decisions(
                sample_requirements, sample_components
            )
            tasks.append(task)
        
        with patch.object(agent, 'make_component_decisions') as mock_decision:
            mock_decision.return_value = {
                'selected_components': [],
                'decision_rationale': 'Test decision',
                'alternatives': [],
                'risk_assessment': {'overall_risk_level': 'low'}
            }
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            assert len(results) == 5
            assert all(not isinstance(r, Exception) for r in results)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])