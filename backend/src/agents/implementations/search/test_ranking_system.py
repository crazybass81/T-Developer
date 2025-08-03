# backend/src/agents/implementations/search/test_ranking_system.py
import pytest
import asyncio
from unittest.mock import Mock, patch
import numpy as np

@pytest.mark.asyncio
class TestSearchResultRanker:
    """검색 결과 랭킹 시스템 테스트"""

    @pytest.fixture
    def ranker(self):
        from ranking_system import SearchResultRanker
        return SearchResultRanker()

    @pytest.fixture
    def sample_results(self):
        return [
            {
                'id': 'comp1',
                'name': 'React Component Library',
                'description': 'Modern React components',
                'github_stars': 1000,
                'downloads': 50000,
                'category': 'ui-library',
                'tags': ['react', 'components', 'ui'],
                'version': '2.1.0',
                'days_since_last_update': 30
            },
            {
                'id': 'comp2', 
                'name': 'Vue UI Kit',
                'description': 'Vue.js user interface components',
                'github_stars': 500,
                'downloads': 25000,
                'category': 'ui-library',
                'tags': ['vue', 'ui', 'components'],
                'version': '1.5.0',
                'days_since_last_update': 60
            }
        ]

    async def test_basic_ranking(self, ranker, sample_results):
        """기본 랭킹 테스트"""
        
        ranked = await ranker.rank_results(
            sample_results,
            query="react components",
            context={'tech_stack': ['react']}
        )

        assert len(ranked) == 2
        assert all(hasattr(r, 'final_score') for r in ranked)
        assert all(hasattr(r, 'rank_position') for r in ranked)
        
        # 점수 순으로 정렬되어 있는지 확인
        scores = [r.final_score for r in ranked]
        assert scores == sorted(scores, reverse=True)

    async def test_relevance_scoring(self, ranker):
        """관련성 점수 테스트"""
        
        from ranking_system import RelevanceScorer
        scorer = RelevanceScorer()

        component = {
            'name': 'React Button Component',
            'description': 'Customizable button for React apps',
            'tags': ['react', 'button', 'ui'],
            'category': 'component'
        }

        # 정확한 매칭
        score1 = await scorer.extract(component, "react button", None)
        assert score1 > 0.8

        # 부분 매칭
        score2 = await scorer.extract(component, "button component", None)
        assert 0.3 < score2 < 0.8

    async def test_popularity_scoring(self, ranker):
        """인기도 점수 테스트"""
        
        from ranking_system import PopularityScorer
        scorer = PopularityScorer()

        # 높은 인기도
        popular_comp = {
            'github_stars': 10000,
            'downloads': 1000000,
            'forks': 1000
        }
        
        high_score = await scorer.extract(popular_comp, "test", None)
        assert high_score > 0.7

        # 낮은 인기도
        unpopular_comp = {
            'github_stars': 10,
            'downloads': 100,
            'forks': 5
        }
        
        low_score = await scorer.extract(unpopular_comp, "test", None)
        assert low_score < 0.3

    async def test_quality_scoring(self, ranker):
        """품질 점수 테스트"""
        
        from ranking_system import QualityScorer
        scorer = QualityScorer()

        # 고품질 컴포넌트
        quality_comp = {
            'has_readme': True,
            'has_documentation': True,
            'test_coverage': 90,
            'open_issues': 5,
            'closed_issues': 95,
            'days_since_last_commit': 7
        }
        
        high_score = await scorer.extract(quality_comp, "test", None)
        assert high_score > 0.7

    async def test_diversification(self, ranker, sample_results):
        """다양성 조정 테스트"""
        
        from diversification import ResultDiversifier
        diversifier = ResultDiversifier()

        # 모든 결과가 같은 카테고리인 경우
        same_category_results = []
        for i in range(5):
            result = Mock()
            result.component = {
                'id': f'comp{i}',
                'category': 'ui-library',
                'name': f'Component {i}',
                'description': f'Description {i}'
            }
            result.final_score = 1.0 - (i * 0.1)
            same_category_results.append(result)

        diversified = await diversifier.diversify_results(same_category_results)
        
        # 다양성 조정 후 결과 수가 줄어들어야 함
        assert len(diversified) <= len(same_category_results)

    async def test_learning_to_rank(self, ranker):
        """Learning to Rank 테스트"""
        
        from learning_to_rank import LearningToRankModel
        ltr_model = LearningToRankModel()

        # 훈련 데이터 생성
        training_data = []
        for i in range(200):
            training_data.append({
                'query': f'query_{i % 10}',
                'relevance_score': np.random.random(),
                'popularity_score': np.random.random(),
                'quality_score': np.random.random(),
                'freshness_score': np.random.random(),
                'compatibility_score': np.random.random(),
                'click_through_rate': np.random.random(),
                'dwell_time': np.random.random() * 100,
                'query_component_match': np.random.random(),
                'relevance_label': np.random.randint(0, 5)
            })

        # 모델 훈련
        results = await ltr_model.train(training_data)
        
        assert 'ndcg_score' in results
        assert 'feature_importance' in results
        assert ltr_model.is_trained

        # 예측 테스트
        test_features = [[0.8, 0.6, 0.7, 0.5, 0.9, 0.3, 25.0, 0.8]]
        scores = await ltr_model.predict_scores(test_features)
        
        assert len(scores) == 1
        assert 0 <= scores[0] <= 5