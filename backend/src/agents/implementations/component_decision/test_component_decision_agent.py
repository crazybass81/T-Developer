"""
Test suite for Component Decision Agent
"""

import pytest
import asyncio
from component_decision_agent import (
    ComponentDecisionAgent, ComponentOption, DecisionCriteria,
    ArchitectureAnalyzer, SecurityAnalyzer, PerformanceAnalyzer
)

@pytest.fixture
def sample_components():
    return [
        ComponentOption(
            name="React",
            version="18.2.0",
            pros=["Large ecosystem", "Virtual DOM", "Component reusability"],
            cons=["Learning curve", "Frequent updates"],
            compatibility_score=0.9,
            performance_score=0.8,
            security_score=0.85,
            maintenance_score=0.9,
            cost_score=0.95
        ),
        ComponentOption(
            name="Vue",
            version="3.3.0",
            pros=["Easy learning", "Good documentation", "Progressive framework"],
            cons=["Smaller ecosystem", "Less job market"],
            compatibility_score=0.85,
            performance_score=0.85,
            security_score=0.8,
            maintenance_score=0.85,
            cost_score=0.9
        ),
        ComponentOption(
            name="Angular",
            version="16.0.0",
            pros=["Full framework", "TypeScript support", "Enterprise ready"],
            cons=["Complex", "Heavy", "Steep learning curve"],
            compatibility_score=0.8,
            performance_score=0.75,
            security_score=0.9,
            maintenance_score=0.8,
            cost_score=0.7
        )
    ]

@pytest.fixture
def sample_requirements():
    return {
        'project_type': 'web_application',
        'team_size': 8,
        'scalability_needs': 'high',
        'domain_complexity': 'medium',
        'security_requirements': {
            'compliance_standards': ['GDPR'],
            'authentication': 'OAuth2',
            'data_encryption': True
        },
        'performance_requirements': {
            'max_latency_ms': 200,
            'min_throughput_rps': 1000,
            'target_users': 100000
        },
        'architecture_requirements': {
            'pattern': 'microservices',
            'deployment': 'cloud',
            'monitoring': True
        }
    }

class TestArchitectureAnalyzer:
    """Architecture Analyzer 테스트"""
    
    @pytest.mark.asyncio
    async def test_architecture_fit_analysis(self):
        analyzer = ArchitectureAnalyzer()
        
        requirements = {
            'team_size': 15,
            'scalability_needs': 'high',
            'domain_complexity': 'high'
        }
        constraints = {'budget': 'high', 'timeline': 'flexible'}
        
        scores = await analyzer.analyze_architecture_fit(requirements, constraints)
        
        # 큰 팀과 높은 확장성 요구사항에서는 마이크로서비스가 높은 점수
        assert scores['microservices'] > scores['monolith']
        assert scores['microservices'] > 0.7
        assert all(0 <= score <= 1 for score in scores.values())
    
    @pytest.mark.asyncio
    async def test_monolith_preference_small_team(self):
        analyzer = ArchitectureAnalyzer()
        
        requirements = {
            'team_size': 3,
            'scalability_needs': 'low',
            'domain_complexity': 'low'
        }
        constraints = {}
        
        scores = await analyzer.analyze_architecture_fit(requirements, constraints)
        
        # 작은 팀과 낮은 복잡도에서는 모놀리스가 선호
        assert scores['monolith'] >= scores['microservices']

class TestSecurityAnalyzer:
    """Security Analyzer 테스트"""
    
    @pytest.mark.asyncio
    async def test_vulnerability_check(self, sample_components):
        analyzer = SecurityAnalyzer()
        
        react_component = sample_components[0]  # React
        
        analysis = await analyzer.analyze_security_requirements(
            react_component,
            {'compliance_standards': ['GDPR'], 'authentication': 'OAuth2'}
        )
        
        assert 'vulnerability_score' in analysis
        assert 'compliance_score' in analysis
        assert 'security_features' in analysis
        assert 'recommendations' in analysis
        
        # React는 알려진 안전한 프레임워크
        assert analysis['vulnerability_score'] >= 0.8
    
    @pytest.mark.asyncio
    async def test_compliance_analysis(self, sample_components):
        analyzer = SecurityAnalyzer()
        
        component = sample_components[0]
        strict_requirements = {
            'compliance_standards': ['HIPAA', 'PCI-DSS'],
            'data_encryption': True
        }
        
        analysis = await analyzer.analyze_security_requirements(
            component, strict_requirements
        )
        
        # 엄격한 규정 준수 요구사항
        assert analysis['compliance_score'] <= 0.9

class TestPerformanceAnalyzer:
    """Performance Analyzer 테스트"""
    
    @pytest.mark.asyncio
    async def test_performance_impact_analysis(self, sample_components):
        analyzer = PerformanceAnalyzer()
        
        react_component = sample_components[0]
        performance_reqs = {
            'max_latency_ms': 100,
            'min_throughput_rps': 5000
        }
        
        analysis = await analyzer.analyze_performance_impact(
            react_component, performance_reqs
        )
        
        assert 'latency_impact' in analysis
        assert 'throughput_impact' in analysis
        assert 'resource_usage' in analysis
        assert 'scalability_score' in analysis
        assert 'optimization_suggestions' in analysis
        
        # 지연 시간이 합리적 범위 내
        assert analysis['latency_impact'] < 200
    
    @pytest.mark.asyncio
    async def test_scalability_analysis(self, sample_components):
        analyzer = PerformanceAnalyzer()
        
        for component in sample_components:
            scalability = await analyzer._analyze_scalability(component)
            assert 0 <= scalability <= 1

class TestComponentDecisionAgent:
    """Component Decision Agent 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_component_decision_making(self, sample_components, sample_requirements):
        agent = ComponentDecisionAgent()
        
        decision = await agent.make_component_decision(
            sample_components, sample_requirements
        )
        
        # 결정 구조 검증
        assert decision.selected_option is not None
        assert 0 <= decision.confidence_score <= 1
        assert decision.reasoning is not None
        assert len(decision.alternatives) > 0
        assert decision.risk_assessment is not None
        assert len(decision.implementation_plan) > 0
        
        # 선택된 옵션이 입력 옵션 중 하나인지 확인
        assert decision.selected_option in sample_components
    
    @pytest.mark.asyncio
    async def test_decision_with_custom_criteria(self, sample_components, sample_requirements):
        agent = ComponentDecisionAgent()
        
        # 보안을 최우선으로 하는 기준
        security_focused_criteria = DecisionCriteria(
            performance_weight=0.1,
            security_weight=0.5,
            compatibility_weight=0.2,
            maintenance_weight=0.1,
            cost_weight=0.1
        )
        
        decision = await agent.make_component_decision(
            sample_components, sample_requirements, security_focused_criteria
        )
        
        # 보안 점수가 높은 컴포넌트가 선택되어야 함
        assert decision.selected_option.security_score >= 0.8
    
    @pytest.mark.asyncio
    async def test_architecture_comparison(self, sample_requirements):
        agent = ComponentDecisionAgent()
        
        architectures = ['microservices', 'monolith', 'serverless']
        
        comparison = await agent.compare_architectures(
            architectures, sample_requirements
        )
        
        assert 'recommended_architecture' in comparison
        assert 'confidence' in comparison
        assert 'comparison_scores' in comparison
        assert 'reasoning' in comparison
        
        # 추천된 아키텍처가 입력 옵션 중 하나
        assert comparison['recommended_architecture'] in architectures
        
        # 높은 확장성 요구사항에서는 마이크로서비스 선호
        assert comparison['comparison_scores']['microservices'] > 0.5
    
    @pytest.mark.asyncio
    async def test_integration_approach_evaluation(self, sample_components):
        agent = ComponentDecisionAgent()
        
        integration_reqs = {
            'scalability': 'high',
            'complexity': 'medium',
            'real_time': True
        }
        
        evaluation = await agent.evaluate_integration_approach(
            sample_components, integration_reqs
        )
        
        assert 'recommended_approach' in evaluation
        assert 'confidence' in evaluation
        assert 'evaluation_scores' in evaluation
        assert 'integration_plan' in evaluation
        
        # 높은 확장성 요구사항에서는 이벤트 드리븐 선호
        assert evaluation['evaluation_scores']['event_driven'] > 0.7
    
    @pytest.mark.asyncio
    async def test_risk_assessment(self, sample_components, sample_requirements):
        agent = ComponentDecisionAgent()
        
        # 낮은 호환성 점수를 가진 컴포넌트 생성
        risky_component = ComponentOption(
            name="RiskyFramework",
            version="0.1.0",
            pros=["New features"],
            cons=["Unstable", "No community"],
            compatibility_score=0.3,
            performance_score=0.5,
            security_score=0.4,
            maintenance_score=0.2,
            cost_score=0.8
        )
        
        analysis = await agent._analyze_option(risky_component, sample_requirements)
        risks = await agent._assess_risks(risky_component, analysis)
        
        # 위험이 식별되어야 함
        assert len(risks['technical_risks']) > 0 or len(risks['business_risks']) > 0
        assert len(risks['mitigation_strategies']) > 0
    
    @pytest.mark.asyncio
    async def test_implementation_plan_generation(self, sample_components, sample_requirements):
        agent = ComponentDecisionAgent()
        
        plan = await agent._generate_implementation_plan(
            sample_components[0], sample_requirements
        )
        
        # 구현 계획이 생성되어야 함
        assert len(plan) >= 5
        assert all(isinstance(step, str) for step in plan)
        
        # 보안 요구사항이 있으면 보안 관련 단계 포함
        plan_text = ' '.join(plan)
        assert 'security' in plan_text.lower()

class TestPerformance:
    """성능 테스트"""
    
    @pytest.mark.asyncio
    async def test_decision_speed(self, sample_components, sample_requirements):
        agent = ComponentDecisionAgent()
        
        import time
        start_time = time.time()
        
        decision = await agent.make_component_decision(
            sample_components, sample_requirements
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 결정이 5초 이내에 완료되어야 함
        assert processing_time < 5
        assert decision is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_decisions(self, sample_components, sample_requirements):
        agent = ComponentDecisionAgent()
        
        # 동시에 여러 결정 요청
        tasks = []
        for i in range(5):
            task = agent.make_component_decision(
                sample_components, sample_requirements
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # 모든 결정이 성공적으로 완료
        assert len(results) == 5
        assert all(result.selected_option is not None for result in results)

class TestEdgeCases:
    """엣지 케이스 테스트"""
    
    @pytest.mark.asyncio
    async def test_empty_options_list(self, sample_requirements):
        agent = ComponentDecisionAgent()
        
        with pytest.raises(Exception):
            await agent.make_component_decision([], sample_requirements)
    
    @pytest.mark.asyncio
    async def test_single_option(self, sample_requirements):
        agent = ComponentDecisionAgent()
        
        single_option = [ComponentOption(
            name="OnlyOption",
            version="1.0.0",
            pros=["Only choice"],
            cons=["No alternatives"],
            compatibility_score=0.7,
            performance_score=0.7,
            security_score=0.7,
            maintenance_score=0.7,
            cost_score=0.7
        )]
        
        decision = await agent.make_component_decision(
            single_option, sample_requirements
        )
        
        # 유일한 옵션이 선택되어야 함
        assert decision.selected_option == single_option[0]
        assert len(decision.alternatives) == 0
    
    @pytest.mark.asyncio
    async def test_equal_score_options(self, sample_requirements):
        agent = ComponentDecisionAgent()
        
        # 동일한 점수를 가진 옵션들
        equal_options = [
            ComponentOption(
                name=f"Option{i}",
                version="1.0.0",
                pros=["Good"],
                cons=["Average"],
                compatibility_score=0.8,
                performance_score=0.8,
                security_score=0.8,
                maintenance_score=0.8,
                cost_score=0.8
            )
            for i in range(3)
        ]
        
        decision = await agent.make_component_decision(
            equal_options, sample_requirements
        )
        
        # 결정이 내려져야 함 (AI 추가 분석으로 차별화)
        assert decision.selected_option is not None
        assert decision.confidence_score > 0

if __name__ == "__main__":
    pytest.main([__file__])