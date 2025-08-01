"""
Test suite for Matching Rate Agent
"""

import pytest
import asyncio
import numpy as np
from matching_rate_agent import (
    MatchingRateAgent, SemanticSimilarityAnalyzer, CompatibilityAnalyzer,
    PerformancePredictor, MatchingScore, ComponentMatch
)

@pytest.fixture
def sample_requirement():
    return {
        'name': 'Frontend Framework',
        'description': 'Modern reactive frontend framework for building user interfaces',
        'required_features': [
            'component-based architecture',
            'virtual DOM',
            'state management',
            'routing',
            'testing support'
        ],
        'tech_stack': ['javascript', 'typescript', 'webpack'],
        'performance_requirements': {
            'max_bundle_size_kb': 200,
            'max_load_time_ms': 2000,
            'max_memory_mb': 50
        },
        'target_platforms': ['web', 'mobile'],
        'license_requirements': 'mit',
        'version_requirements': {
            'node': '>=16.0.0',
            'typescript': '>=4.0.0'
        }
    }

@pytest.fixture
def sample_components():
    return [
        {
            'id': 'react-18',
            'name': 'React',
            'version': '18.2.0',
            'description': 'A JavaScript library for building user interfaces with virtual DOM',
            'features': [
                'component-based architecture',
                'virtual DOM',
                'hooks',
                'concurrent features',
                'server-side rendering'
            ],
            'supported_platforms': ['web', 'mobile', 'desktop'],
            'license': 'MIT',
            'maturity': 'stable',
            'community_support': True
        },
        {
            'id': 'vue-3',
            'name': 'Vue',
            'version': '3.3.0',
            'description': 'Progressive JavaScript framework for building user interfaces',
            'features': [
                'component-based architecture',
                'reactive data binding',
                'template syntax',
                'composition API',
                'built-in state management'
            ],
            'supported_platforms': ['web'],
            'license': 'MIT',
            'maturity': 'stable',
            'community_support': True
        },
        {
            'id': 'angular-16',
            'name': 'Angular',
            'version': '16.0.0',
            'description': 'Platform for building mobile and desktop web applications',
            'features': [
                'component-based architecture',
                'dependency injection',
                'TypeScript support',
                'routing',
                'testing framework'
            ],
            'supported_platforms': ['web', 'mobile'],
            'license': 'MIT',
            'maturity': 'stable',
            'community_support': True
        }
    ]

class TestSemanticSimilarityAnalyzer:
    """Semantic Similarity Analyzer 테스트"""
    
    @pytest.mark.asyncio
    async def test_semantic_similarity_calculation(self):
        analyzer = SemanticSimilarityAnalyzer()
        
        # 유사한 텍스트
        text1 = "React is a JavaScript library for building user interfaces"
        text2 = "React is a JS framework for creating UI components"
        
        similarity = await analyzer.calculate_semantic_similarity(text1, text2)
        
        # 유사한 텍스트는 높은 유사도를 가져야 함
        assert similarity > 0.5
        assert 0 <= similarity <= 1
    
    @pytest.mark.asyncio
    async def test_feature_overlap_analysis(self):
        analyzer = SemanticSimilarityAnalyzer()
        
        required_features = ['component-based', 'virtual DOM', 'state management']
        component_features = ['component-based architecture', 'virtual DOM', 'hooks']
        
        overlap = await analyzer.analyze_feature_overlap(
            required_features, component_features
        )
        
        assert 'overlap_ratio' in overlap
        assert 'coverage_score' in overlap
        assert 'exact_matches' in overlap
        assert 'semantic_matches' in overlap
        
        # 일부 기능이 겹치므로 0보다 큰 값
        assert overlap['overlap_ratio'] > 0
    
    @pytest.mark.asyncio
    async def test_empty_features_handling(self):
        analyzer = SemanticSimilarityAnalyzer()
        
        overlap = await analyzer.analyze_feature_overlap([], ['feature1', 'feature2'])
        
        assert overlap['overlap_ratio'] == 0.0
        assert overlap['coverage_score'] == 0.0

class TestCompatibilityAnalyzer:
    """Compatibility Analyzer 테스트"""
    
    @pytest.mark.asyncio
    async def test_technical_compatibility_analysis(self, sample_components):
        analyzer = CompatibilityAnalyzer()
        
        react_component = sample_components[0]  # React
        tech_stack = ['javascript', 'typescript', 'webpack']
        
        compatibility = await analyzer.analyze_technical_compatibility(
            react_component, tech_stack
        )
        
        assert len(compatibility) == len(tech_stack)
        assert all(0 <= score <= 1 for score in compatibility.values())
        
        # React는 JavaScript와 높은 호환성
        assert compatibility['javascript'] > 0.8
    
    @pytest.mark.asyncio
    async def test_version_compatibility_check(self, sample_components):
        analyzer = CompatibilityAnalyzer()
        
        component = sample_components[0]
        required_versions = {
            'node': '>=16.0.0',
            'typescript': '>=4.0.0'
        }
        
        compatibility = await analyzer.check_version_compatibility(
            component, required_versions
        )
        
        assert isinstance(compatibility, dict)
        assert all(isinstance(v, bool) for v in compatibility.values())

class TestPerformancePredictor:
    """Performance Predictor 테스트"""
    
    @pytest.mark.asyncio
    async def test_performance_impact_prediction(self, sample_components):
        predictor = PerformancePredictor()
        
        react_component = sample_components[0]
        performance_reqs = {
            'max_bundle_size_kb': 200,
            'max_load_time_ms': 2000,
            'max_memory_mb': 50
        }
        
        impact = await predictor.predict_performance_impact(
            react_component, performance_reqs
        )
        
        assert 'performance_score' in impact
        assert 0 <= impact['performance_score'] <= 1
        
        # 추가 메트릭 확인
        if 'bundle_size_score' in impact:
            assert 0 <= impact['bundle_size_score'] <= 1
    
    @pytest.mark.asyncio
    async def test_unknown_component_handling(self):
        predictor = PerformancePredictor()
        
        unknown_component = {'name': 'UnknownFramework', 'version': '1.0.0'}
        performance_reqs = {'max_bundle_size_kb': 100}
        
        impact = await predictor.predict_performance_impact(
            unknown_component, performance_reqs
        )
        
        # 알려지지 않은 컴포넌트는 기본 점수
        assert impact['performance_score'] == 0.5

class TestMatchingRateAgent:
    """Matching Rate Agent 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_matching_score_calculation(self, sample_requirement, sample_components):
        agent = MatchingRateAgent()
        
        react_component = sample_components[0]  # React
        
        score = await agent.calculate_matching_score(
            sample_requirement, react_component
        )
        
        # 점수 구조 검증
        assert isinstance(score, MatchingScore)
        assert 0 <= score.overall_score <= 1
        assert 0 <= score.functional_score <= 1
        assert 0 <= score.technical_score <= 1
        assert 0 <= score.performance_score <= 1
        assert 0 <= score.compatibility_score <= 1
        assert 0 <= score.confidence <= 1
        assert isinstance(score.explanation, str)
        assert len(score.explanation) > 0
    
    @pytest.mark.asyncio
    async def test_custom_weights(self, sample_requirement, sample_components):
        agent = MatchingRateAgent()
        
        # 성능 중심 가중치
        performance_weights = {
            'functional': 0.2,
            'technical': 0.2,
            'performance': 0.5,
            'compatibility': 0.1
        }
        
        react_component = sample_components[0]
        
        score = await agent.calculate_matching_score(
            sample_requirement, react_component, performance_weights
        )
        
        # 성능 점수가 전체 점수에 큰 영향을 미쳐야 함
        assert isinstance(score, MatchingScore)
        assert score.overall_score is not None
    
    @pytest.mark.asyncio
    async def test_batch_matching_calculation(self, sample_requirement, sample_components):
        agent = MatchingRateAgent()
        
        matches = await agent.batch_calculate_matching(
            sample_requirement, sample_components
        )
        
        # 결과 검증
        assert len(matches) == len(sample_components)
        assert all(isinstance(match, ComponentMatch) for match in matches)
        
        # 점수순 정렬 확인
        scores = [match.matching_score.overall_score for match in matches]
        assert scores == sorted(scores, reverse=True)
        
        # 각 매치 객체 검증
        for match in matches:
            assert match.component_id is not None
            assert match.component_name is not None
            assert isinstance(match.pros, list)
            assert isinstance(match.cons, list)
            assert match.integration_effort is not None
            assert isinstance(match.risks, list)
    
    @pytest.mark.asyncio
    async def test_functional_score_calculation(self, sample_requirement, sample_components):
        agent = MatchingRateAgent()
        
        react_component = sample_components[0]
        
        functional_score = await agent._calculate_functional_score(
            sample_requirement, react_component
        )
        
        assert 0 <= functional_score <= 1
        
        # React는 요구사항과 높은 기능적 매칭을 가져야 함
        assert functional_score > 0.5
    
    @pytest.mark.asyncio
    async def test_technical_score_calculation(self, sample_requirement, sample_components):
        agent = MatchingRateAgent()
        
        react_component = sample_components[0]
        
        technical_score = await agent._calculate_technical_score(
            sample_requirement, react_component
        )
        
        assert 0 <= technical_score <= 1
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self):
        agent = MatchingRateAgent()
        
        # 일관된 점수들 (높은 신뢰도)
        high_confidence = await agent._calculate_confidence(0.8, 0.85, 0.82, 0.83)
        assert high_confidence > 0.7
        
        # 불일치하는 점수들 (낮은 신뢰도)
        low_confidence = await agent._calculate_confidence(0.9, 0.3, 0.8, 0.2)
        assert low_confidence < high_confidence
    
    @pytest.mark.asyncio
    async def test_pros_cons_analysis(self, sample_requirement, sample_components):
        agent = MatchingRateAgent()
        
        # 높은 점수를 가진 매칭 스코어 생성
        high_score = MatchingScore(
            overall_score=0.9,
            functional_score=0.9,
            technical_score=0.85,
            performance_score=0.8,
            compatibility_score=0.9,
            confidence=0.85,
            explanation="High quality match"
        )
        
        pros, cons = await agent._analyze_pros_cons(
            sample_requirement, sample_components[0], high_score
        )
        
        # 높은 점수는 더 많은 장점을 가져야 함
        assert len(pros) >= len(cons)
        assert all(isinstance(pro, str) for pro in pros)
        assert all(isinstance(con, str) for con in cons)
    
    @pytest.mark.asyncio
    async def test_integration_effort_estimation(self):
        agent = MatchingRateAgent()
        
        # 다양한 점수에 대한 통합 노력 추정
        high_score = MatchingScore(0.9, 0.9, 0.9, 0.9, 0.9, 0.9, "")
        medium_score = MatchingScore(0.7, 0.7, 0.7, 0.7, 0.7, 0.7, "")
        low_score = MatchingScore(0.3, 0.3, 0.3, 0.3, 0.3, 0.3, "")
        
        high_effort = await agent._estimate_integration_effort(high_score)
        medium_effort = await agent._estimate_integration_effort(medium_score)
        low_effort = await agent._estimate_integration_effort(low_score)
        
        assert "Low" in high_effort
        assert "Medium" in medium_effort
        assert "High" in low_effort or "Very High" in low_effort

class TestPerformance:
    """성능 테스트"""
    
    @pytest.mark.asyncio
    async def test_batch_processing_performance(self, sample_requirement):
        agent = MatchingRateAgent()
        
        # 많은 컴포넌트 생성
        components = []
        for i in range(20):
            components.append({
                'id': f'comp_{i}',
                'name': f'Component{i}',
                'version': '1.0.0',
                'description': f'Test component {i}',
                'features': ['feature1', 'feature2'],
                'supported_platforms': ['web'],
                'license': 'MIT'
            })
        
        import time
        start_time = time.time()
        
        matches = await agent.batch_calculate_matching(
            sample_requirement, components
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 20개 컴포넌트를 10초 이내에 처리
        assert processing_time < 10
        assert len(matches) == 20
    
    @pytest.mark.asyncio
    async def test_caching_effectiveness(self):
        analyzer = SemanticSimilarityAnalyzer()
        
        text1 = "React framework for building UIs"
        text2 = "Vue framework for creating interfaces"
        
        # 첫 번째 호출
        start_time = time.time()
        similarity1 = await analyzer.calculate_semantic_similarity(text1, text2)
        first_call_time = time.time() - start_time
        
        # 두 번째 호출 (캐시 사용)
        start_time = time.time()
        similarity2 = await analyzer.calculate_semantic_similarity(text1, text2)
        second_call_time = time.time() - start_time
        
        # 결과는 동일해야 함
        assert similarity1 == similarity2
        
        # 두 번째 호출이 더 빨라야 함 (캐시 효과)
        assert second_call_time < first_call_time

class TestEdgeCases:
    """엣지 케이스 테스트"""
    
    @pytest.mark.asyncio
    async def test_empty_requirement(self, sample_components):
        agent = MatchingRateAgent()
        
        empty_requirement = {}
        
        score = await agent.calculate_matching_score(
            empty_requirement, sample_components[0]
        )
        
        # 빈 요구사항에도 기본 점수 제공
        assert isinstance(score, MatchingScore)
        assert 0 <= score.overall_score <= 1
    
    @pytest.mark.asyncio
    async def test_missing_component_fields(self, sample_requirement):
        agent = MatchingRateAgent()
        
        minimal_component = {
            'name': 'MinimalComponent',
            'version': '1.0.0'
        }
        
        score = await agent.calculate_matching_score(
            sample_requirement, minimal_component
        )
        
        # 최소한의 정보로도 점수 계산 가능
        assert isinstance(score, MatchingScore)
        assert score.overall_score is not None
    
    @pytest.mark.asyncio
    async def test_invalid_weights(self, sample_requirement, sample_components):
        agent = MatchingRateAgent()
        
        # 잘못된 가중치 (합이 1이 아님)
        invalid_weights = {
            'functional': 0.5,
            'technical': 0.5,
            'performance': 0.5,
            'compatibility': 0.5
        }
        
        # 에러 없이 처리되어야 함
        score = await agent.calculate_matching_score(
            sample_requirement, sample_components[0], invalid_weights
        )
        
        assert isinstance(score, MatchingScore)

if __name__ == "__main__":
    pytest.main([__file__])