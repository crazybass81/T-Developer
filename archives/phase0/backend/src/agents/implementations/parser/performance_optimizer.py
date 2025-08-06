"""
Parser Agent - Performance Optimization
캐싱, 병렬 처리, 메모리 최적화
"""

from typing import Dict, List, Any, Optional
import asyncio
import time
from dataclasses import dataclass
import psutil
import gc
from concurrent.futures import ThreadPoolExecutor
import redis
import pickle
import hashlib
from functools import wraps

@dataclass
class PerformanceMetrics:
    latency_p50: float
    latency_p95: float
    latency_p99: float
    throughput: float
    error_rate: float
    cache_hit_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float

class PerformanceOptimizer:
    """Parser Agent 성능 최적화"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.metrics = PerformanceMetrics(0, 0, 0, 0, 0, 0, 0, 0)
        self.request_times = []
        self.cache_hits = 0
        self.cache_misses = 0
        self.error_count = 0
        self.total_requests = 0
        
        # 스레드 풀 (CPU 집약적 작업용)
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # 메모리 풀
        self.memory_pool = MemoryPool()
        
        # 배치 처리기
        self.batch_processor = BatchProcessor()
    
    def performance_monitor(self, func):
        """성능 모니터링 데코레이터"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                self._record_success(start_time)
                return result
            except Exception as e:
                self._record_error(start_time)
                raise e
        
        return wrapper
    
    def _record_success(self, start_time: float):
        """성공 요청 기록"""
        elapsed = time.time() - start_time
        self.request_times.append(elapsed)
        self.total_requests += 1
        
        # 최근 1000개 요청만 유지
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]
    
    def _record_error(self, start_time: float):
        """에러 요청 기록"""
        elapsed = time.time() - start_time
        self.request_times.append(elapsed)
        self.error_count += 1
        self.total_requests += 1
    
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """성능 메트릭 계산"""
        
        if not self.request_times:
            return self.metrics
        
        # 지연시간 계산
        sorted_times = sorted(self.request_times)
        n = len(sorted_times)
        
        p50_idx = int(n * 0.5)
        p95_idx = int(n * 0.95)
        p99_idx = int(n * 0.99)
        
        latency_p50 = sorted_times[p50_idx] * 1000  # ms
        latency_p95 = sorted_times[p95_idx] * 1000
        latency_p99 = sorted_times[p99_idx] * 1000
        
        # 처리량 계산 (requests/second)
        if self.request_times:
            time_window = max(self.request_times) - min(self.request_times)
            throughput = len(self.request_times) / max(time_window, 1)
        else:
            throughput = 0
        
        # 에러율 계산
        error_rate = (self.error_count / max(self.total_requests, 1)) * 100
        
        # 캐시 적중률
        total_cache_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / max(total_cache_requests, 1)) * 100
        
        # 시스템 리소스
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # MB
        cpu_usage = psutil.cpu_percent()
        
        self.metrics = PerformanceMetrics(
            latency_p50=latency_p50,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            throughput=throughput,
            error_rate=error_rate,
            cache_hit_rate=cache_hit_rate,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage
        )
        
        return self.metrics
    
    async def optimize_memory_usage(self):
        """메모리 사용량 최적화"""
        
        # 가비지 컬렉션 강제 실행
        gc.collect()
        
        # 메모리 풀 정리
        self.memory_pool.cleanup()
        
        # 오래된 캐시 항목 정리
        await self._cleanup_old_cache_entries()
        
        # 메트릭 히스토리 정리
        if len(self.request_times) > 500:
            self.request_times = self.request_times[-500:]
    
    async def _cleanup_old_cache_entries(self):
        """오래된 캐시 항목 정리"""
        
        # Redis에서 TTL이 짧은 키들 정리
        keys = await self.redis.keys("parser_cache:*")
        
        for key in keys:
            ttl = await self.redis.ttl(key)
            if ttl < 300:  # 5분 미만 남은 키들 삭제
                await self.redis.delete(key)


class AdvancedCaching:
    """고급 캐싱 시스템"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.local_cache = {}  # L1 캐시
        self.cache_stats = {'hits': 0, 'misses': 0}
    
    async def get(self, key: str) -> Optional[Any]:
        """계층화된 캐시에서 조회"""
        
        # L1 캐시 확인
        if key in self.local_cache:
            self.cache_stats['hits'] += 1
            return self.local_cache[key]
        
        # L2 캐시 (Redis) 확인
        cached_data = await self.redis.get(f"parser_cache:{key}")
        
        if cached_data:
            data = pickle.loads(cached_data)
            # L1 캐시에 저장
            self.local_cache[key] = data
            self.cache_stats['hits'] += 1
            return data
        
        self.cache_stats['misses'] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """계층화된 캐시에 저장"""
        
        # L1 캐시에 저장
        self.local_cache[key] = value
        
        # L2 캐시 (Redis)에 저장
        await self.redis.setex(
            f"parser_cache:{key}",
            ttl,
            pickle.dumps(value)
        )
        
        # L1 캐시 크기 제한
        if len(self.local_cache) > 1000:
            # LRU 방식으로 오래된 항목 제거
            oldest_key = next(iter(self.local_cache))
            del self.local_cache[oldest_key]
    
    async def invalidate(self, pattern: str):
        """패턴 매칭으로 캐시 무효화"""
        
        # L1 캐시 무효화
        keys_to_remove = [k for k in self.local_cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self.local_cache[key]
        
        # L2 캐시 무효화
        redis_keys = await self.redis.keys(f"parser_cache:*{pattern}*")
        if redis_keys:
            await self.redis.delete(*redis_keys)


class ParallelProcessor:
    """병렬 처리 최적화"""
    
    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
    
    async def process_requirements_parallel(
        self, requirements: List[str], processor_func
    ) -> List[Any]:
        """요구사항 병렬 처리"""
        
        async def process_single(req: str):
            async with self.semaphore:
                return await processor_func(req)
        
        # 병렬 처리 실행
        tasks = [process_single(req) for req in requirements]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 예외 처리
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Processing error: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def batch_process(
        self, items: List[Any], batch_size: int, processor_func
    ) -> List[Any]:
        """배치 처리"""
        
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # 배치 병렬 처리
            batch_results = await self.process_requirements_parallel(
                batch, processor_func
            )
            
            results.extend(batch_results)
            
            # 배치 간 짧은 대기 (시스템 부하 방지)
            await asyncio.sleep(0.01)
        
        return results


class MemoryPool:
    """메모리 풀 관리"""
    
    def __init__(self):
        self.pools = {
            'small': [],    # < 1KB
            'medium': [],   # 1KB - 10KB
            'large': []     # > 10KB
        }
        self.max_pool_size = 100
    
    def get_buffer(self, size: int) -> bytearray:
        """버퍼 할당"""
        
        pool_type = self._get_pool_type(size)
        pool = self.pools[pool_type]
        
        if pool:
            buffer = pool.pop()
            if len(buffer) >= size:
                return buffer
        
        # 새 버퍼 생성
        return bytearray(size)
    
    def return_buffer(self, buffer: bytearray):
        """버퍼 반환"""
        
        pool_type = self._get_pool_type(len(buffer))
        pool = self.pools[pool_type]
        
        if len(pool) < self.max_pool_size:
            # 버퍼 초기화
            buffer[:] = b'\x00' * len(buffer)
            pool.append(buffer)
    
    def _get_pool_type(self, size: int) -> str:
        """풀 타입 결정"""
        if size < 1024:
            return 'small'
        elif size < 10240:
            return 'medium'
        else:
            return 'large'
    
    def cleanup(self):
        """풀 정리"""
        for pool in self.pools.values():
            pool.clear()


class BatchProcessor:
    """배치 처리 최적화"""
    
    def __init__(self, batch_size: int = 50, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.pending_items = []
        self.last_flush = time.time()
    
    async def add_item(self, item: Any, processor_func) -> Optional[List[Any]]:
        """아이템 추가 및 배치 처리"""
        
        self.pending_items.append(item)
        
        # 배치 크기 또는 시간 조건 확인
        should_flush = (
            len(self.pending_items) >= self.batch_size or
            time.time() - self.last_flush >= self.flush_interval
        )
        
        if should_flush:
            return await self.flush(processor_func)
        
        return None
    
    async def flush(self, processor_func) -> List[Any]:
        """배치 플러시"""
        
        if not self.pending_items:
            return []
        
        items_to_process = self.pending_items.copy()
        self.pending_items.clear()
        self.last_flush = time.time()
        
        # 배치 처리 실행
        results = await processor_func(items_to_process)
        
        return results


class OptimizedParserAgent:
    """성능 최적화된 Parser Agent"""
    
    def __init__(self, base_parser_agent, redis_client: redis.Redis):
        self.base_agent = base_parser_agent
        self.optimizer = PerformanceOptimizer(redis_client)
        self.cache = AdvancedCaching(redis_client)
        self.parallel_processor = ParallelProcessor()
        
        # 성능 모니터링 적용
        self.parse_requirements = self.optimizer.performance_monitor(
            self._optimized_parse_requirements
        )
    
    async def _optimized_parse_requirements(
        self, description: str, **kwargs
    ) -> Any:
        """최적화된 요구사항 파싱"""
        
        # 캐시 키 생성
        cache_key = hashlib.md5(description.encode()).hexdigest()
        
        # 캐시 확인
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # 메모리 사용량 확인 및 최적화
        if psutil.virtual_memory().percent > 80:
            await self.optimizer.optimize_memory_usage()
        
        # 기본 파싱 실행
        result = await self.base_agent.parse_requirements(description, **kwargs)
        
        # 결과 캐싱
        await self.cache.set(cache_key, result)
        
        return result
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """성능 보고서 생성"""
        
        metrics = await self.optimizer.get_performance_metrics()
        
        return {
            'performance_metrics': metrics.__dict__,
            'cache_statistics': self.cache.cache_stats,
            'system_resources': {
                'memory_percent': psutil.virtual_memory().percent,
                'cpu_percent': psutil.cpu_percent(),
                'disk_usage': psutil.disk_usage('/').percent
            },
            'optimization_recommendations': await self._generate_optimization_recommendations(metrics)
        }
    
    async def _generate_optimization_recommendations(
        self, metrics: PerformanceMetrics
    ) -> List[str]:
        """최적화 권장사항 생성"""
        
        recommendations = []
        
        if metrics.latency_p95 > 2000:  # 2초 이상
            recommendations.append("Consider increasing cache TTL or adding more cache layers")
        
        if metrics.cache_hit_rate < 50:
            recommendations.append("Cache hit rate is low, review caching strategy")
        
        if metrics.memory_usage_mb > 1000:  # 1GB 이상
            recommendations.append("High memory usage detected, consider memory optimization")
        
        if metrics.cpu_usage_percent > 80:
            recommendations.append("High CPU usage, consider scaling horizontally")
        
        if metrics.error_rate > 5:  # 5% 이상
            recommendations.append("High error rate detected, review error handling")
        
        return recommendations