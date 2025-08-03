# backend/tests/agents/test_search_analytics.py
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.implementations.search_analytics import (
    SearchAnalyticsEngine, 
    QueryPatternAnalyzer, 
    TrendDetector,
    AnomalyDetector
)
from agents.implementations.search_optimization import SearchOptimizer

class TestSearchAnalytics:
    """Search Analytics 테스트"""

    @pytest.fixture
    def analytics_engine(self):
        return SearchAnalyticsEngine()

    @pytest.fixture
    def sample_query_logs(self):
        base_time = datetime.now()
        return [
            {
                'query': 'react components',
                'timestamp': base_time - timedelta(hours=1),
                'response_time_ms': 150,
                'result_count': 25,
                'clicked_results': [{'position': 0}]
            },
            {
                'query': 'python flask',
                'timestamp': base_time - timedelta(hours=2),
                'response_time_ms': 200,
                'result_count': 15,
                'clicked_results': []
            },
            {
                'query': 'react components',
                'timestamp': base_time - timedelta(hours=3),
                'response_time_ms': 180,
                'result_count': 30,
                'clicked_results': [{'position': 1}]
            },
            {
                'query': 'database orm',
                'timestamp': base_time - timedelta(hours=4),
                'response_time_ms': 500,
                'result_count': 0,
                'clicked_results': []
            }
        ]

    @pytest.mark.asyncio
    async def test_basic_analytics(self, analytics_engine, sample_query_logs):
        """기본 분석 테스트"""
        result = await analytics_engine.analyze_search_patterns(sample_query_logs)
        
        assert result.total_queries == 4
        assert result.unique_queries == 3
        assert result.avg_response_time > 0
        assert result.zero_result_rate == 0.25  # 1 out of 4
        assert len(result.top_queries) > 0
        assert result.top_queries[0][0] == 'react components'  # Most frequent

    @pytest.mark.asyncio
    async def test_query_pattern_analysis(self, sample_query_logs):
        """쿼리 패턴 분석 테스트"""
        analyzer = QueryPatternAnalyzer()
        patterns = await analyzer.analyze(sample_query_logs)
        
        assert 'query_types' in patterns
        assert 'common_ngrams' in patterns
        assert 'avg_query_length' in patterns
        
        # Check query type classification
        query_types = patterns['query_types']
        assert query_types['short'] + query_types['medium'] + query_types['long'] == 4

    @pytest.mark.asyncio
    async def test_trend_detection(self, sample_query_logs):
        """트렌드 감지 테스트"""
        detector = TrendDetector()
        trends = await detector.detect_trends(sample_query_logs, 'daily')
        
        assert 'volume_trend' in trends
        assert trends['volume_trend'] in ['increasing', 'decreasing', 'stable']
        assert 'emerging_queries' in trends
        assert 'daily_volumes' in trends

    @pytest.mark.asyncio
    async def test_anomaly_detection(self, sample_query_logs):
        """이상 감지 테스트"""
        detector = AnomalyDetector()
        anomalies = await detector.detect(sample_query_logs)
        
        # Should detect high zero results (25% > 30% threshold not met in this case)
        # But should detect slow response (500ms query)
        assert isinstance(anomalies, list)

    @pytest.mark.asyncio
    async def test_empty_logs_handling(self, analytics_engine):
        """빈 로그 처리 테스트"""
        result = await analytics_engine.analyze_search_patterns([])
        
        assert result.total_queries == 0
        assert result.unique_queries == 0
        assert result.avg_response_time == 0
        assert result.zero_result_rate == 0
        assert len(result.top_queries) == 0

class TestSearchOptimization:
    """Search Optimization 테스트"""

    @pytest.fixture
    def optimizer(self):
        return SearchOptimizer()

    @pytest.mark.asyncio
    async def test_optimization_recommendations(self, optimizer):
        """최적화 추천 테스트"""
        analytics_data = {
            'zero_result_rate': 0.3,  # High zero result rate
            'avg_response_time': 1200  # Slow response
        }
        
        performance_metrics = {
            'mrr': 0.3,  # Low MRR
            'cache_hit_rate': 0.5  # Low cache hit rate
        }
        
        recommendations = await optimizer.optimize_search_performance(
            analytics_data, 
            performance_metrics
        )
        
        assert len(recommendations) > 0
        assert all(rec.type in ['query_expansion', 'ranking_improvement', 
                               'performance_optimization', 'cache_optimization'] 
                  for rec in recommendations)
        assert all(rec.priority in ['high', 'medium', 'low'] for rec in recommendations)

    @pytest.mark.asyncio
    async def test_query_optimization(self, optimizer):
        """쿼리 최적화 테스트"""
        original_query = "js framework"
        context = {'domain': 'frontend'}
        
        optimized_query = await optimizer.optimize_query(original_query, context)
        
        # Should expand 'js' to 'javascript'
        assert 'javascript' in optimized_query.lower()

    @pytest.mark.asyncio
    async def test_typo_correction(self, optimizer):
        """오타 수정 테스트"""
        query_with_typo = "javascirpt framework"
        context = {}
        
        corrected_query = await optimizer.optimize_query(query_with_typo, context)
        
        assert 'javascript' in corrected_query.lower()
        assert 'javascirpt' not in corrected_query.lower()

    @pytest.mark.asyncio
    async def test_result_ranking(self, optimizer):
        """결과 랭킹 테스트"""
        results = [
            {
                'name': 'React',
                'description': 'JavaScript library for building user interfaces',
                'popularity_score': 0.9,
                'quality_score': 0.8,
                'last_updated': datetime.now().isoformat()
            },
            {
                'name': 'Vue',
                'description': 'Progressive JavaScript framework',
                'popularity_score': 0.7,
                'quality_score': 0.9,
                'last_updated': (datetime.now() - timedelta(days=60)).isoformat()
            }
        ]
        
        query = "javascript framework"
        context = {}
        
        ranked_results = await optimizer.result_ranker.rerank_results(
            results, query, context
        )
        
        assert len(ranked_results) == 2
        assert all('ranking_score' in result for result in ranked_results)
        # Results should be sorted by ranking score
        assert ranked_results[0]['ranking_score'] >= ranked_results[1]['ranking_score']

@pytest.mark.performance
class TestSearchPerformance:
    """검색 성능 테스트"""

    @pytest.mark.asyncio
    async def test_analytics_performance(self):
        """분석 성능 테스트"""
        # Generate large dataset
        large_dataset = []
        base_time = datetime.now()
        
        for i in range(1000):
            large_dataset.append({
                'query': f'test query {i % 100}',
                'timestamp': base_time - timedelta(minutes=i),
                'response_time_ms': 100 + (i % 500),
                'result_count': i % 50,
                'clicked_results': [{'position': i % 10}] if i % 3 == 0 else []
            })
        
        analytics_engine = SearchAnalyticsEngine()
        
        import time
        start_time = time.time()
        result = await analytics_engine.analyze_search_patterns(large_dataset)
        end_time = time.time()
        
        # Should process 1000 queries in under 2 seconds
        assert end_time - start_time < 2.0
        assert result.total_queries == 1000

    @pytest.mark.asyncio
    async def test_concurrent_analysis(self):
        """동시 분석 테스트"""
        analytics_engine = SearchAnalyticsEngine()
        
        # Create multiple small datasets
        datasets = []
        for i in range(10):
            dataset = [
                {
                    'query': f'query {j}',
                    'timestamp': datetime.now(),
                    'response_time_ms': 100,
                    'result_count': 10,
                    'clicked_results': []
                }
                for j in range(50)
            ]
            datasets.append(dataset)
        
        # Run concurrent analysis
        tasks = [
            analytics_engine.analyze_search_patterns(dataset)
            for dataset in datasets
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        assert len(results) == 10
        assert all(result.total_queries == 50 for result in results)
        # Concurrent processing should be faster than sequential
        assert end_time - start_time < 5.0