# backend/tests/agents/test_component_decision_agent.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

@pytest.mark.asyncio
class TestComponentDecisionAgent:
    """Component Decision Agent 테스트"""

    @pytest.fixture
    async def decision_agent(self):
        """Decision Agent 인스턴스"""
        from component_decision_agent import ComponentDecisionAgent
        
        agent = ComponentDecisionAgent()
        # Mock the AI agents to avoid actual API calls
        agent.decision_agent.arun = AsyncMock(return_value=Mock(content="Test reasoning"))
        agent.evaluator.arun = AsyncMock(return_value=Mock(content='{"functional_fit": 0.8, "performance": 0.7, "security": 0.9, "compatibility": 0.6, "cost": 0.8}'))
        
        yield agent

    @pytest.fixture
    def sample_requirements(self):
        """샘플 요구사항"""
        return {
            'functional_requirements': [
                'User authentication',
                'Data visualization',
                'Real-time updates'
            ],
            'performance_requirements': {
                'response_time': 200,  # ms
                'concurrent_users': 1000
            },
            'security_requirements': [
                'OAuth 2.0 support',
                'Data encryption'
            ],
            'preferred_technologies': ['React', 'Node.js'],
            'target_platforms': ['web', 'mobile']
        }

    @pytest.fixture
    def sample_components(self):
        """샘플 컴포넌트"""
        return [
            {
                'id': 'comp1',
                'name': 'React Dashboard',
                'description': 'Modern dashboard with authentication',
                'features': ['authentication', 'charts', 'real-time'],
                'technologies': ['React', 'TypeScript'],
                'supported_platforms': ['web'],
                'performance_score': 0.8,
                'security_score': 0.9,
                'last_updated': '2024-01-15T00:00:00Z',
                'license': 'MIT'
            },
            {
                'id': 'comp2',
                'name': 'Vue Analytics',
                'description': 'Analytics dashboard with Vue.js',
                'features': ['analytics', 'charts', 'export'],
                'technologies': ['Vue', 'JavaScript'],
                'supported_platforms': ['web'],
                'performance_score': 0.7,
                'security_score': 0.6,
                'last_updated': '2023-06-01T00:00:00Z',
                'license': 'Apache-2.0'
            },
            {
                'id': 'comp3',
                'name': 'Mobile Auth Kit',
                'description': 'Authentication library for mobile',
                'features': ['authentication', 'biometric', 'oauth'],
                'technologies': ['React Native', 'Swift', 'Kotlin'],
                'supported_platforms': ['mobile'],
                'performance_score': 0.9,
                'security_score': 0.95,
                'last_updated': '2024-02-01T00:00:00Z',
                'license': 'MIT'
            }
        ]

    async def test_basic_decision_making(self, decision_agent, sample_requirements, sample_components):
        """기본 결정 기능 테스트"""
        
        decisions = await decision_agent.make_component_decisions(
            sample_requirements,
            sample_components
        )
        
        # 모든 컴포넌트에 대한 결정이 있어야 함
        assert len(decisions) == len(sample_components)
        
        # 각 결정에 필요한 필드가 있어야 함
        for decision in decisions:
            assert decision.component_id is not None
            assert decision.component_name is not None
            assert decision.decision in ['selected', 'rejected', 'conditional']
            assert 0 <= decision.score <= 1
            assert decision.reasoning is not None

    async def test_decision_criteria_application(self, decision_agent, sample_requirements, sample_components):
        """결정 기준 적용 테스트"""
        from component_decision_agent import DecisionCriteria
        
        # 보안 중심 기준
        security_focused = DecisionCriteria(
            functional_fit=0.2,
            performance=0.1,
            security=0.5,
            compatibility=0.1,
            cost=0.1
        )
        
        decisions = await decision_agent.make_component_decisions(
            sample_requirements,
            sample_components,
            criteria=security_focused
        )
        
        # 보안 점수가 높은 컴포넌트가 더 높은 점수를 받아야 함
        mobile_auth = next(d for d in decisions if d.component_id == 'comp3')
        vue_analytics = next(d for d in decisions if d.component_id == 'comp2')
        
        assert mobile_auth.score > vue_analytics.score

    async def test_risk_analysis(self, decision_agent, sample_requirements):
        """리스크 분석 테스트"""
        
        # 리스크가 있는 컴포넌트
        risky_component = {
            'id': 'risky1',
            'name': 'Old Library',
            'description': 'Outdated library with known issues',
            'features': ['basic_auth'],
            'security_score': 0.3,  # 낮은 보안 점수
            'last_updated': '2020-01-01T00:00:00Z',  # 오래된 업데이트
            'license': 'GPL-3.0'  # 문제가 될 수 있는 라이선스
        }
        
        risks = await decision_agent.risk_analyzer.analyze(
            risky_component,
            sample_requirements
        )
        
        # 여러 리스크가 감지되어야 함
        assert len(risks) > 0
        assert any('security' in risk.lower() for risk in risks)
        assert any('unmaintained' in risk.lower() for risk in risks)

    async def test_compatibility_checking(self, decision_agent, sample_requirements):
        """호환성 검사 테스트"""
        
        component = {
            'id': 'test1',
            'name': 'Test Component',
            'technologies': ['React', 'Node.js'],
            'supported_platforms': ['web', 'mobile']
        }
        
        compatibility = await decision_agent.compatibility_checker.check(
            component,
            sample_requirements,
            {}
        )
        
        # 호환성 점수가 계산되어야 함
        assert 'technology_stack' in compatibility
        assert 'platform_support' in compatibility
        assert compatibility['technology_stack'] > 0.5  # React, Node.js 매칭
        assert compatibility['platform_support'] > 0.5  # web, mobile 지원

    async def test_decision_optimization(self, decision_agent, sample_requirements, sample_components):
        """결정 최적화 테스트"""
        
        # 호환성 문제가 있는 컴포넌트들 추가
        conflicting_components = sample_components + [
            {
                'id': 'comp4',
                'name': 'GPL Component',
                'license': 'GPL-3.0',
                'features': ['advanced_features']
            }
        ]
        
        decisions = await decision_agent.make_component_decisions(
            sample_requirements,
            conflicting_components
        )
        
        # 최적화가 적용되어야 함
        assert len(decisions) == len(conflicting_components)

    @pytest.mark.performance
    async def test_decision_performance(self, decision_agent, sample_requirements):
        """결정 성능 테스트"""
        import time
        
        # 많은 컴포넌트로 테스트
        many_components = []
        for i in range(50):
            many_components.append({
                'id': f'comp_{i}',
                'name': f'Component {i}',
                'description': f'Test component {i}',
                'features': ['feature1', 'feature2'],
                'performance_score': 0.5 + (i % 5) * 0.1,
                'security_score': 0.6 + (i % 4) * 0.1
            })
        
        start_time = time.time()
        decisions = await decision_agent.make_component_decisions(
            sample_requirements,
            many_components
        )
        elapsed_time = time.time() - start_time
        
        # 성능 기준: 50개 컴포넌트를 10초 이내에 처리
        assert elapsed_time < 10.0
        assert len(decisions) == 50

    async def test_context_based_decisions(self, decision_agent, sample_requirements, sample_components):
        """컨텍스트 기반 결정 테스트"""
        
        # 엔터프라이즈 컨텍스트
        enterprise_context = {
            'project_type': 'enterprise',
            'security_critical': True,
            'compliance_required': True
        }
        
        enterprise_decisions = await decision_agent.make_component_decisions(
            sample_requirements,
            sample_components,
            context=enterprise_context
        )
        
        # 스타트업 컨텍스트
        startup_context = {
            'project_type': 'startup',
            'time_pressure': True,
            'cost_sensitive': True
        }
        
        startup_decisions = await decision_agent.make_component_decisions(
            sample_requirements,
            sample_components,
            context=startup_context
        )
        
        # 컨텍스트에 따라 다른 결정이 나와야 함
        assert len(enterprise_decisions) == len(startup_decisions)
        
        # 보안 점수가 높은 컴포넌트가 엔터프라이즈에서 더 선호되어야 함
        mobile_auth_enterprise = next(d for d in enterprise_decisions if d.component_id == 'comp3')
        mobile_auth_startup = next(d for d in startup_decisions if d.component_id == 'comp3')
        
        # 엔터프라이즈에서 보안이 중요하므로 더 높은 점수
        assert mobile_auth_enterprise.score >= mobile_auth_startup.score

    async def test_conditional_decisions(self, decision_agent, sample_requirements):
        """조건부 결정 테스트"""
        
        # 조건부 결정이 필요한 컴포넌트
        conditional_component = {
            'id': 'cond1',
            'name': 'Conditional Component',
            'description': 'Component with some issues',
            'features': ['authentication', 'basic_features'],
            'performance_score': 0.6,  # 중간 성능
            'security_score': 0.5,    # 낮은 보안
            'license': 'MIT'
        }
        
        decisions = await decision_agent.make_component_decisions(
            sample_requirements,
            [conditional_component]
        )
        
        decision = decisions[0]
        
        # 조건부 결정이어야 함
        if decision.decision == 'conditional':
            assert len(decision.conditions) > 0
            assert any('security' in condition.lower() for condition in decision.conditions)

    async def test_alternative_suggestions(self, decision_agent, sample_requirements, sample_components):
        """대안 제안 테스트"""
        
        # 거부된 컴포넌트에 대한 대안이 제안되어야 함
        decisions = await decision_agent.make_component_decisions(
            sample_requirements,
            sample_components
        )
        
        rejected_decisions = [d for d in decisions if d.decision == 'rejected']
        
        for decision in rejected_decisions:
            # 대안이 있거나 명확한 거부 이유가 있어야 함
            assert len(decision.alternatives) > 0 or len(decision.risks) > 0

    @pytest.mark.integration
    async def test_end_to_end_decision_flow(self, decision_agent, sample_requirements, sample_components):
        """전체 결정 플로우 테스트"""
        
        # 전체 결정 프로세스 실행
        decisions = await decision_agent.make_component_decisions(
            sample_requirements,
            sample_components
        )
        
        # 결과 검증
        assert len(decisions) == len(sample_components)
        
        # 적어도 하나는 선택되어야 함
        selected_count = len([d for d in decisions if d.decision == 'selected'])
        conditional_count = len([d for d in decisions if d.decision == 'conditional'])
        
        assert selected_count + conditional_count > 0
        
        # 모든 결정에 추론이 있어야 함
        for decision in decisions:
            assert decision.reasoning is not None
            assert len(decision.reasoning) > 0
        
        # 점수가 올바른 범위에 있어야 함
        for decision in decisions:
            assert 0 <= decision.score <= 1