import pytest
import asyncio
from unittest.mock import Mock, patch
from backend.src.agents.implementations.matching_rate.matching_rate_agent import (
    MultiDimensionalMatcher,
    SemanticSimilarityAnalyzer,
    DynamicWeightAdjuster,
    MatchingExplainer
)

class TestMatchingRateAgent:
    """Matching Rate Agent 테스트"""

    @pytest.fixture
    def sample_requirement(self):
        return {
            'id': 'req_001',
            'description': 'Need a responsive UI component',
            'features': ['responsive', 'accessible', 'fast'],
            'technology_stack': {'framework': 'react', 'language': 'javascript'}
        }

    @pytest.fixture
    def sample_component(self):
        return {
            'id': 'comp_001',
            'name': 'react-component',
            'features': ['responsive', 'accessible', 'customizable'],
            'technology_stack': {'framework': 'react', 'language': 'javascript'}
        }

    @pytest.mark.asyncio
    async def test_multidimensional_matching(self, sample_requirement, sample_component):
        """다차원 매칭 테스트"""
        matcher = MultiDimensionalMatcher()
        
        result = await matcher.calculate_matching_score(
            sample_requirement,
            sample_component
        )
        
        assert result.overall_score >= 0.0
        assert result.overall_score <= 1.0
        assert 'functional' in result.dimension_scores
        assert 'technical' in result.dimension_scores
        assert result.confidence >= 0.0

    @pytest.mark.asyncio
    async def test_semantic_similarity(self):
        """의미적 유사도 테스트"""
        analyzer = SemanticSimilarityAnalyzer()
        
        similarity = await analyzer.calculate_semantic_similarity(
            "responsive web component",
            "mobile-friendly UI element"
        )
        
        assert 0.0 <= similarity <= 1.0

    @pytest.mark.asyncio
    async def test_dynamic_weight_adjustment(self):
        """동적 가중치 조정 테스트"""
        adjuster = DynamicWeightAdjuster()
        
        project_context = {'priority': 'performance'}
        user_preferences = {'prefer_stability': True}
        
        weights = await adjuster.adjust_weights(
            project_context,
            user_preferences
        )
        
        assert abs(sum(weights.values()) - 1.0) < 0.001
        assert weights['performance'] > adjuster.base_weights['performance']

    @pytest.mark.asyncio
    async def test_matching_explanation(self, sample_requirement, sample_component):
        """매칭 설명 생성 테스트"""
        explainer = MatchingExplainer()
        matcher = MultiDimensionalMatcher()
        
        matching_result = await matcher.calculate_matching_score(
            sample_requirement,
            sample_component
        )
        
        explanation = await explainer.generate_explanation(
            matching_result,
            sample_requirement,
            sample_component
        )
        
        assert 'summary' in explanation
        assert 'strengths' in explanation
        assert 'weaknesses' in explanation
        assert 'suggestions' in explanation