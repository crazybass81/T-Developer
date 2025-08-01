"""
Matching Rate Agent 테스트
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from backend.src.agents.implementations.matching_rate_agent import (
    MatchingRateAgent,
    ComponentProfile,
    MatchingResult
)

class TestMatchingRateAgent:
    """Matching Rate Agent 테스트"""

    @pytest.fixture
    def matching_agent(self):
        return MatchingRateAgent()

    @pytest.fixture
    def sample_requirements(self):
        return [
            {
                'id': 'req-001',
                'description': 'User authentication system',
                'features': ['login', 'logout', 'password_reset'],
                'required_features': ['login', 'logout'],
                'technology_stack': ['react', 'nodejs'],
                'performance_requirements': {
                    'response_time': 200,
                    'throughput': 1000
                },
                'target_platforms': ['web', 'mobile']
            }
        ]

    @pytest.fixture
    def sample_components(self):
        return [
            ComponentProfile(
                id='comp-001',
                name='Auth Component',
                description='Complete authentication solution',
                features=['login', 'logout', 'password_reset', 'oauth'],
                tech_stack=['react', 'nodejs', 'jwt'],
                performance_metrics={
                    'response_time': 150,
                    'throughput': 1200
                },
                compatibility_info={
                    'platforms': ['web', 'mobile'],
                    'supported_versions': {'react': '18.0', 'nodejs': '16.0'}
                },
                metadata={}
            )
        ]

    @pytest.mark.asyncio
    async def test_calculate_matching_rates(self, matching_agent, sample_requirements, sample_components):
        """매칭률 계산 테스트"""
        with patch.object(matching_agent.agent, 'arun') as mock_arun:
            mock_arun.return_value = Mock(content='{"confidence": 0.9, "reasoning": "High compatibility", "risks": []}')
            
            results = await matching_agent.calculate_matching_rates(
                sample_requirements,
                sample_components
            )
            
            assert len(results) == 1
            assert len(results[0]) == 1
            
            match_result = results[0][0]
            assert isinstance(match_result, MatchingResult)
            assert match_result.component_id == 'comp-001'
            assert match_result.requirement_id == 'req-001'
            assert 0 <= match_result.overall_score <= 1

    @pytest.mark.asyncio
    async def test_functional_match_calculation(self, matching_agent, sample_requirements, sample_components):
        """기능적 매칭 점수 계산 테스트"""
        requirement = sample_requirements[0]
        component = sample_components[0]
        
        score = await matching_agent._calculate_functional_match(requirement, component)
        
        # 모든 필수 기능이 포함되어 있으므로 높은 점수 예상
        assert score > 0.7

    @pytest.mark.asyncio
    async def test_technical_match_calculation(self, matching_agent, sample_requirements, sample_components):
        """기술적 매칭 점수 계산 테스트"""
        requirement = sample_requirements[0]
        component = sample_components[0]
        
        score = await matching_agent._calculate_technical_match(requirement, component)
        
        # 기술 스택이 일치하므로 높은 점수 예상
        assert score > 0.8

    @pytest.mark.asyncio
    async def test_performance_match_calculation(self, matching_agent, sample_requirements, sample_components):
        """성능 매칭 점수 계산 테스트"""
        requirement = sample_requirements[0]
        component = sample_components[0]
        
        score = await matching_agent._calculate_performance_match(requirement, component)
        
        # 컴포넌트 성능이 요구사항을 만족하므로 높은 점수 예상
        assert score >= 1.0

    def test_conflicting_tech_detection(self, matching_agent):
        """기술 스택 충돌 감지 테스트"""
        # React와 Vue는 충돌
        assert matching_agent._is_conflicting_tech('react', {'vue', 'nodejs'})
        
        # React와 Node.js는 충돌하지 않음
        assert not matching_agent._is_conflicting_tech('react', {'nodejs', 'express'})

    def test_version_compatibility(self, matching_agent):
        """버전 호환성 테스트"""
        # 같은 메이저 버전, 높은 마이너 버전은 호환
        assert matching_agent._is_version_compatible('16.0', '16.5')
        
        # 낮은 마이너 버전은 비호환
        assert not matching_agent._is_version_compatible('16.5', '16.0')
        
        # 다른 메이저 버전은 비호환
        assert not matching_agent._is_version_compatible('16.0', '18.0')

    def test_text_extraction(self, matching_agent, sample_requirements, sample_components):
        """텍스트 추출 테스트"""
        req_text = matching_agent._extract_requirement_text(sample_requirements[0])
        comp_text = matching_agent._extract_component_text(sample_components[0])
        
        assert 'authentication' in req_text.lower()
        assert 'login' in req_text
        
        assert 'authentication' in comp_text.lower()
        assert 'react' in comp_text