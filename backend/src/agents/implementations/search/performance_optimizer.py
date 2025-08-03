# backend/src/agents/implementations/search/performance_optimizer.py
from typing import Dict, List, Any, Optional
import asyncio
import time
from dataclasses import dataclass
from collections import defaultdict
import numpy as np

@dataclass
class PerformanceMetrics:
    avg_response_time: float
    p95_response_time: float
    cache_hit_rate: float
    query_throughput: float
    error_rate: float
    memory_usage_mb: float

@dataclass
class OptimizationResult:
    optimization_type: str
    improvement_percentage: float
    before_metrics: PerformanceMetrics
    after_metrics: PerformanceMetrics
    recommendations: List[str]

class SearchPerformanceOptimizer:
    """검색 성능 최적화 시스템"""

    def __init__(self):
        self.cache_optimizer = CacheOptimizer()
        self.query_optimizer = QueryOptimizer()
        self.index_optimizer = IndexOptimizer()
        self.resource_optimizer = ResourceOptimizer()
        
        # 성능 임계값
        self.thresholds = {
            'response_time_ms': 100,
            'cache_hit_rate': 0.8,
            'error_rate': 0.01,
            'memory_usage_mb': 512
        }

    async def optimize_search_performance(
        self,
        search_logs: List[Dict[str, Any]],
        current_config: Dict[str, Any]
    ) -> OptimizationResult:
        """검색 성능 종합 최적화"""

        # 현재 성능 측정
        before_metrics = self._calculate_metrics(search_logs)

        # 병렬 최적화 실행
        optimization_tasks = [
            self.cache_optimizer.optimize(search_logs),
            self.query_optimizer.optimize(search_logs),
            self.index_optimizer.optimize(search_logs),
            self.resource_optimizer.optimize(search_logs)
        ]

        optimizations = await asyncio.gather(*optimization_tasks)

        # 최적화 적용
        optimized_config = await self._apply_optimizations(
            current_config,
            optimizations
        )

        # 최적화 후 성능 예측
        after_metrics = await self._predict_performance(
            before_metrics,
            optimizations
        )

        # 개선율 계산
        improvement = self._calculate_improvement(
            before_metrics,
            after_metrics
        )

        return OptimizationResult(
            optimization_type="comprehensive",
            improvement_percentage=improvement,
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            recommendations=self._generate_recommendations(optimizations)
        )

    def _calculate_metrics(
        self,
        search_logs: List[Dict[str, Any]]
    ) -> PerformanceMetrics:
        """성능 메트릭 계산"""

        response_times = [log.get('response_time_ms', 0) for log in search_logs]
        cache_hits = sum(1 for log in search_logs if log.get('cache_hit', False))
        errors = sum(1 for log in search_logs if log.get('error', False))

        return PerformanceMetrics(
            avg_response_time=np.mean(response_times),
            p95_response_time=np.percentile(response_times, 95),
            cache_hit_rate=cache_hits / len(search_logs) if search_logs else 0,
            query_throughput=len(search_logs) / 3600,  # per hour
            error_rate=errors / len(search_logs) if search_logs else 0,
            memory_usage_mb=self._estimate_memory_usage(search_logs)
        )

    async def _apply_optimizations(
        self,
        config: Dict[str, Any],
        optimizations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """최적화 설정 적용"""

        optimized_config = config.copy()

        for opt in optimizations:
            if opt['type'] == 'cache':
                optimized_config.update(opt['cache_settings'])
            elif opt['type'] == 'query':
                optimized_config.update(opt['query_settings'])
            elif opt['type'] == 'index':
                optimized_config.update(opt['index_settings'])
            elif opt['type'] == 'resource':
                optimized_config.update(opt['resource_settings'])

        return optimized_config

class CacheOptimizer:
    """캐시 최적화기"""

    async def optimize(
        self,
        search_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """캐시 최적화"""

        # 쿼리 빈도 분석
        query_frequency = defaultdict(int)
        for log in search_logs:
            query_frequency[log.get('query', '')] += 1

        # 캐시 히트율 분석
        cache_performance = self._analyze_cache_performance(search_logs)

        # 최적 캐시 크기 계산
        optimal_cache_size = self._calculate_optimal_cache_size(
            query_frequency,
            cache_performance
        )

        # TTL 최적화
        optimal_ttl = self._calculate_optimal_ttl(search_logs)

        return {
            'type': 'cache',
            'cache_settings': {
                'cache_size': optimal_cache_size,
                'ttl_seconds': optimal_ttl,
                'eviction_policy': 'lru',
                'preload_popular_queries': True
            },
            'expected_improvement': 0.3
        }

    def _analyze_cache_performance(
        self,
        search_logs: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """캐시 성능 분석"""

        total_queries = len(search_logs)
        cache_hits = sum(1 for log in search_logs if log.get('cache_hit', False))
        
        hit_rate = cache_hits / total_queries if total_queries > 0 else 0
        
        # 캐시 히트 시 평균 응답 시간
        hit_times = [
            log['response_time_ms'] for log in search_logs 
            if log.get('cache_hit', False)
        ]
        
        # 캐시 미스 시 평균 응답 시간
        miss_times = [
            log['response_time_ms'] for log in search_logs 
            if not log.get('cache_hit', False)
        ]

        return {
            'hit_rate': hit_rate,
            'avg_hit_time': np.mean(hit_times) if hit_times else 0,
            'avg_miss_time': np.mean(miss_times) if miss_times else 0
        }

class QueryOptimizer:
    """쿼리 최적화기"""

    async def optimize(
        self,
        search_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """쿼리 최적화"""

        # 느린 쿼리 식별
        slow_queries = self._identify_slow_queries(search_logs)

        # 쿼리 패턴 분석
        query_patterns = self._analyze_query_patterns(search_logs)

        # 배치 처리 기회 식별
        batch_opportunities = self._identify_batch_opportunities(search_logs)

        return {
            'type': 'query',
            'query_settings': {
                'enable_query_batching': len(batch_opportunities) > 0,
                'batch_size': 10,
                'query_timeout_ms': 5000,
                'parallel_search_enabled': True,
                'max_parallel_searches': 5
            },
            'slow_queries': slow_queries,
            'expected_improvement': 0.25
        }

    def _identify_slow_queries(
        self,
        search_logs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """느린 쿼리 식별"""

        # 95 퍼센타일 기준으로 느린 쿼리 식별
        response_times = [log.get('response_time_ms', 0) for log in search_logs]
        threshold = np.percentile(response_times, 95)

        slow_queries = []
        for log in search_logs:
            if log.get('response_time_ms', 0) > threshold:
                slow_queries.append({
                    'query': log.get('query', ''),
                    'response_time': log.get('response_time_ms', 0),
                    'result_count': log.get('result_count', 0)
                })

        return slow_queries[:10]  # 상위 10개

class IndexOptimizer:
    """인덱스 최적화기"""

    async def optimize(
        self,
        search_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """인덱스 최적화"""

        # 검색 패턴 분석
        search_patterns = self._analyze_search_patterns(search_logs)

        # 인덱스 효율성 분석
        index_efficiency = self._analyze_index_efficiency(search_logs)

        # 최적 인덱스 구조 제안
        optimal_indexes = self._suggest_optimal_indexes(search_patterns)

        return {
            'type': 'index',
            'index_settings': {
                'rebuild_indexes': index_efficiency < 0.7,
                'add_composite_indexes': len(optimal_indexes) > 0,
                'enable_fuzzy_search': True,
                'index_update_frequency': 'hourly'
            },
            'suggested_indexes': optimal_indexes,
            'expected_improvement': 0.2
        }

    def _analyze_search_patterns(
        self,
        search_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """검색 패턴 분석"""

        # 검색 필드 빈도
        field_usage = defaultdict(int)
        
        # 검색어 길이 분포
        query_lengths = []
        
        # 필터 사용 패턴
        filter_usage = defaultdict(int)

        for log in search_logs:
            query = log.get('query', '')
            query_lengths.append(len(query.split()))
            
            # 필터 분석
            filters = log.get('filters', {})
            for filter_name in filters.keys():
                filter_usage[filter_name] += 1

        return {
            'avg_query_length': np.mean(query_lengths),
            'most_used_filters': dict(filter_usage),
            'query_complexity': self._calculate_query_complexity(search_logs)
        }

class ResourceOptimizer:
    """리소스 최적화기"""

    async def optimize(
        self,
        search_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """리소스 최적화"""

        # 메모리 사용 패턴 분석
        memory_patterns = self._analyze_memory_usage(search_logs)

        # CPU 사용률 분석
        cpu_patterns = self._analyze_cpu_usage(search_logs)

        # 동시성 최적화
        concurrency_settings = self._optimize_concurrency(search_logs)

        return {
            'type': 'resource',
            'resource_settings': {
                'max_memory_mb': memory_patterns['recommended_limit'],
                'worker_pool_size': concurrency_settings['optimal_workers'],
                'connection_pool_size': concurrency_settings['optimal_connections'],
                'enable_compression': True,
                'garbage_collection_frequency': 'medium'
            },
            'expected_improvement': 0.15
        }

    def _analyze_memory_usage(
        self,
        search_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """메모리 사용 분석"""

        # 결과 크기별 메모리 사용량 추정
        result_sizes = [log.get('result_count', 0) for log in search_logs]
        avg_result_size = np.mean(result_sizes)
        
        # 메모리 사용량 추정 (결과당 1KB 가정)
        estimated_memory_per_query = avg_result_size * 1024  # bytes
        
        # 동시 쿼리 수 고려
        concurrent_queries = max(10, len(search_logs) // 100)
        
        recommended_limit = (estimated_memory_per_query * concurrent_queries) // (1024 * 1024)  # MB

        return {
            'avg_result_size': avg_result_size,
            'estimated_memory_per_query': estimated_memory_per_query,
            'recommended_limit': max(256, recommended_limit)  # 최소 256MB
        }

    def _optimize_concurrency(
        self,
        search_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """동시성 최적화"""

        # 시간대별 쿼리 분포 분석
        hourly_distribution = defaultdict(int)
        for log in search_logs:
            hour = log.get('timestamp', '').split('T')[1][:2] if 'timestamp' in log else '00'
            hourly_distribution[hour] += 1

        # 피크 시간대 식별
        peak_hour_queries = max(hourly_distribution.values()) if hourly_distribution else 10
        
        # 최적 워커 수 계산 (피크 시간 기준)
        optimal_workers = min(50, max(5, peak_hour_queries // 10))
        
        # 커넥션 풀 크기 (워커의 2배)
        optimal_connections = optimal_workers * 2

        return {
            'peak_queries_per_hour': peak_hour_queries,
            'optimal_workers': optimal_workers,
            'optimal_connections': optimal_connections
        }