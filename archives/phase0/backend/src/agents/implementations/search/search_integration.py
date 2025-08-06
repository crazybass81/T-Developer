# backend/src/agents/implementations/search_integration.py
from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass
from datetime import datetime

from .search_agent import SearchAgent
from .search_analytics import SearchAnalyticsEngine
from .search_optimization import SearchOptimizer
from .search_cache import SearchCache

@dataclass
class SearchResult:
    query: str
    results: List[Dict[str, Any]]
    total_count: int
    response_time_ms: float
    sources_used: List[str]
    cache_hit: bool

class IntegratedSearchSystem:
    """통합 검색 시스템"""

    def __init__(self):
        self.search_agent = SearchAgent()
        self.analytics_engine = SearchAnalyticsEngine()
        self.optimizer = SearchOptimizer()
        self.cache = SearchCache()
        
        # 검색 로그 저장소
        self.query_logs: List[Dict[str, Any]] = []

    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> SearchResult:
        """통합 검색 실행"""
        
        start_time = datetime.now()
        
        # 1. 쿼리 최적화
        optimized_query = await self.optimizer.optimize_query(query, user_context or {})
        
        # 2. 캐시 확인
        cache_key = self.cache.generate_cache_key(optimized_query, filters)
        cached_result = await self.cache.get_cached_results(cache_key)
        
        if cached_result:
            # 캐시 히트 로깅
            await self._log_search(
                original_query=query,
                optimized_query=optimized_query,
                result_count=len(cached_result),
                response_time_ms=10,  # 캐시는 매우 빠름
                cache_hit=True,
                user_context=user_context
            )
            
            return SearchResult(
                query=query,
                results=cached_result,
                total_count=len(cached_result),
                response_time_ms=10,
                sources_used=['cache'],
                cache_hit=True
            )
        
        # 3. 실제 검색 수행
        search_results = await self.search_agent.search_components(
            optimized_query,
            filters or {}
        )
        
        # 4. 결과 최적화 (재랭킹)
        optimized_results = await self.optimizer.result_ranker.rerank_results(
            search_results.get('results', []),
            optimized_query,
            user_context or {}
        )
        
        # 5. 캐시에 저장
        await self.cache.cache_results(cache_key, optimized_results)
        
        # 6. 응답 시간 계산
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # 7. 검색 로깅
        await self._log_search(
            original_query=query,
            optimized_query=optimized_query,
            result_count=len(optimized_results),
            response_time_ms=response_time,
            cache_hit=False,
            user_context=user_context
        )
        
        return SearchResult(
            query=query,
            results=optimized_results,
            total_count=len(optimized_results),
            response_time_ms=response_time,
            sources_used=search_results.get('sources_used', []),
            cache_hit=False
        )

    async def get_search_analytics(
        self,
        time_range: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """검색 분석 데이터 조회"""
        
        # 시간 범위 필터링
        filtered_logs = self.query_logs
        if time_range:
            start_time, end_time = time_range
            filtered_logs = [
                log for log in self.query_logs
                if start_time <= log['timestamp'] <= end_time
            ]
        
        # 분석 수행
        analytics = await self.analytics_engine.analyze_search_patterns(filtered_logs)
        
        return {
            'total_queries': analytics.total_queries,
            'unique_queries': analytics.unique_queries,
            'avg_response_time': analytics.avg_response_time,
            'zero_result_rate': analytics.zero_result_rate,
            'top_queries': analytics.top_queries,
            'trends': analytics.query_trends,
            'cache_performance': await self._get_cache_performance()
        }

    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """최적화 추천 조회"""
        
        # 최근 성능 데이터 수집
        recent_logs = self.query_logs[-1000:] if len(self.query_logs) > 1000 else self.query_logs
        
        if not recent_logs:
            return []
        
        # 분석 데이터 준비
        analytics = await self.analytics_engine.analyze_search_patterns(recent_logs)
        
        analytics_data = {
            'zero_result_rate': analytics.zero_result_rate,
            'avg_response_time': analytics.avg_response_time
        }
        
        # 성능 메트릭 계산
        performance_metrics = await self._calculate_performance_metrics(recent_logs)
        
        # 최적화 추천 생성
        recommendations = await self.optimizer.optimize_search_performance(
            analytics_data,
            performance_metrics
        )
        
        return [
            {
                'type': rec.type,
                'priority': rec.priority,
                'description': rec.description,
                'expected_impact': rec.expected_impact,
                'implementation_effort': rec.implementation_effort
            }
            for rec in recommendations
        ]

    async def _log_search(
        self,
        original_query: str,
        optimized_query: str,
        result_count: int,
        response_time_ms: float,
        cache_hit: bool,
        user_context: Optional[Dict[str, Any]]
    ):
        """검색 로깅"""
        
        log_entry = {
            'timestamp': datetime.now(),
            'query': original_query,
            'optimized_query': optimized_query,
            'result_count': result_count,
            'response_time_ms': response_time_ms,
            'cache_hit': cache_hit,
            'user_id': user_context.get('user_id') if user_context else None,
            'session_id': user_context.get('session_id') if user_context else None,
            'clicked_results': []  # 나중에 클릭 추적으로 업데이트
        }
        
        self.query_logs.append(log_entry)
        
        # 로그 크기 관리 (최대 10,000개 유지)
        if len(self.query_logs) > 10000:
            self.query_logs = self.query_logs[-10000:]

    async def _get_cache_performance(self) -> Dict[str, Any]:
        """캐시 성능 메트릭"""
        
        if not self.query_logs:
            return {'hit_rate': 0, 'avg_cache_response_time': 0}
        
        cache_hits = sum(1 for log in self.query_logs if log.get('cache_hit', False))
        total_queries = len(self.query_logs)
        hit_rate = cache_hits / total_queries if total_queries > 0 else 0
        
        cache_response_times = [
            log['response_time_ms'] for log in self.query_logs 
            if log.get('cache_hit', False)
        ]
        avg_cache_time = sum(cache_response_times) / len(cache_response_times) if cache_response_times else 0
        
        return {
            'hit_rate': hit_rate,
            'avg_cache_response_time': avg_cache_time,
            'total_cache_hits': cache_hits
        }

    async def _calculate_performance_metrics(
        self,
        logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """성능 메트릭 계산"""
        
        if not logs:
            return {'mrr': 0, 'cache_hit_rate': 0}
        
        # Mean Reciprocal Rank 계산
        reciprocal_ranks = []
        for log in logs:
            clicked = log.get('clicked_results', [])
            if clicked:
                first_position = min(click.get('position', 0) for click in clicked)
                reciprocal_ranks.append(1 / (first_position + 1))
            else:
                reciprocal_ranks.append(0)
        
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0
        
        # 캐시 히트율
        cache_hits = sum(1 for log in logs if log.get('cache_hit', False))
        cache_hit_rate = cache_hits / len(logs)
        
        return {
            'mrr': mrr,
            'cache_hit_rate': cache_hit_rate
        }

    async def track_click(
        self,
        query: str,
        clicked_result: Dict[str, Any],
        position: int
    ):
        """클릭 추적"""
        
        # 최근 검색 로그에서 해당 쿼리 찾기
        for log in reversed(self.query_logs):
            if log['query'] == query:
                if 'clicked_results' not in log:
                    log['clicked_results'] = []
                
                log['clicked_results'].append({
                    'result_id': clicked_result.get('id'),
                    'position': position,
                    'clicked_at': datetime.now()
                })
                break

    async def get_popular_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """인기 쿼리 조회"""
        
        from collections import Counter
        
        query_counts = Counter(log['query'] for log in self.query_logs)
        popular_queries = query_counts.most_common(limit)
        
        return [
            {
                'query': query,
                'count': count,
                'percentage': count / len(self.query_logs) * 100 if self.query_logs else 0
            }
            for query, count in popular_queries
        ]