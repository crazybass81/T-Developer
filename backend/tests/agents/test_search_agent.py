import pytest
import asyncio
from unittest.mock import Mock, patch
from backend.src.agents.implementations.search.search_agent import (
    MultiSourceSearchEngine,
    IntelligentQueryExpander,
    RealtimeIndexingSystem,
    SearchResultRanker,
    SearchResult
)

class TestSearchAgent:
    """Search Agent 테스트"""

    @pytest.fixture
    def sample_search_results(self):
        return [
            SearchResult(
                component_id='comp_001',
                name='react-component',
                description='A React UI component',
                source='npm',
                relevance_score=0.9,
                metadata={'downloads': 100000, 'stars': 500}
            ),
            SearchResult(
                component_id='comp_002',
                name='vue-component',
                description='A Vue UI component',
                source='npm',
                relevance_score=0.8,
                metadata={'downloads': 50000, 'stars': 300}
            )
        ]

    @pytest.mark.asyncio
    async def test_multi_source_search(self):
        """다중 소스 검색 테스트"""
        search_engine = MultiSourceSearchEngine()
        
        results = await search_engine.search_components(
            'react component',
            {'language': 'javascript'}
        )
        
        assert isinstance(results, list)
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_query_expansion(self):
        """쿼리 확장 테스트"""
        expander = IntelligentQueryExpander()
        
        expanded_queries = await expander.expand_query(
            'ui component',
            {'framework': 'react'}
        )
        
        assert isinstance(expanded_queries, list)
        assert len(expanded_queries) > 1
        assert 'ui component' in expanded_queries

    @pytest.mark.asyncio
    async def test_realtime_indexing(self):
        """실시간 인덱싱 테스트"""
        indexer = RealtimeIndexingSystem()
        
        component = {
            'id': 'test_comp',
            'name': 'test-component',
            'description': 'A test component for UI'
        }
        
        await indexer.index_component(component)
        
        assert 'test_comp' in indexer.index
        assert 'keywords' in indexer.index['test_comp']

    @pytest.mark.asyncio
    async def test_result_ranking(self, sample_search_results):
        """검색 결과 랭킹 테스트"""
        ranker = SearchResultRanker()
        
        ranked_results = await ranker.rank_results(
            sample_search_results,
            'react component',
            {'framework': 'react'}
        )
        
        assert len(ranked_results) == len(sample_search_results)
        assert ranked_results[0].relevance_score >= ranked_results[1].relevance_score

    @pytest.mark.asyncio
    async def test_popularity_calculation(self, sample_search_results):
        """인기도 계산 테스트"""
        ranker = SearchResultRanker()
        
        popularity_score = ranker._calculate_popularity(sample_search_results[0])
        
        assert 0.0 <= popularity_score <= 1.0

    @pytest.mark.asyncio
    async def test_recency_calculation(self, sample_search_results):
        """최신성 계산 테스트"""
        ranker = SearchResultRanker()
        
        # 최신 업데이트 정보 추가
        sample_search_results[0].metadata['last_updated'] = '2024-01-01T00:00:00'
        
        recency_score = ranker._calculate_recency(sample_search_results[0])
        
        assert 0.0 <= recency_score <= 1.0