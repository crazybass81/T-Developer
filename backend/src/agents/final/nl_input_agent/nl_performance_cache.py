"""
T-Developer MVP - NL Input Agent Performance Optimization & Caching
Task 4.3.4: 성능 최적화 및 캐싱 시스템
"""

from typing import Dict, List, Any, Optional, Tuple
import asyncio
import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
import redis.asyncio as redis

@dataclass
class CacheConfig:
    ttl: int = 3600  # 1 hour
    max_size: int = 1000
    enable_compression: bool = True

@dataclass
class PerformanceMetrics:
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time: float = 0.0
    total_requests: int = 0

class NLPerformanceCache:
    """NL Input Agent 성능 최적화 및 캐싱 시스템"""
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.redis_client: Optional[redis.Redis] = None
        self.local_cache: Dict[str, Tuple[Any, float]] = {}
        self.metrics = PerformanceMetrics()
        self.batch_queue: List[Tuple[str, Any]] = []
        self.batch_size = 10
        
    async def initialize(self):
        """캐시 시스템 초기화"""
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True
            )
            await self.redis_client.ping()
        except:
            self.redis_client = None  # Fallback to local cache
    
    def _generate_cache_key(self, description: str, context: Dict = None) -> str:
        """캐시 키 생성"""
        content = f"{description}:{json.dumps(context or {}, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def get_cached_result(
        self, 
        description: str, 
        context: Dict = None
    ) -> Optional[Any]:
        """캐시된 결과 조회"""
        cache_key = self._generate_cache_key(description, context)
        
        # Redis 캐시 확인
        if self.redis_client:
            try:
                cached = await self.redis_client.get(f"nl:{cache_key}")
                if cached:
                    self.metrics.cache_hits += 1
                    return json.loads(cached)
            except:
                pass
        
        # 로컬 캐시 확인
        if cache_key in self.local_cache:
            data, timestamp = self.local_cache[cache_key]
            if time.time() - timestamp < self.config.ttl:
                self.metrics.cache_hits += 1
                return data
            else:
                del self.local_cache[cache_key]
        
        self.metrics.cache_misses += 1
        return None
    
    async def cache_result(
        self, 
        description: str, 
        result: Any, 
        context: Dict = None
    ):
        """결과 캐싱"""
        cache_key = self._generate_cache_key(description, context)
        
        # Redis 캐시 저장
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"nl:{cache_key}",
                    self.config.ttl,
                    json.dumps(result, default=str)
                )
            except:
                pass
        
        # 로컬 캐시 저장
        if len(self.local_cache) >= self.config.max_size:
            # LRU 제거
            oldest_key = min(self.local_cache.keys(), 
                           key=lambda k: self.local_cache[k][1])
            del self.local_cache[oldest_key]
        
        self.local_cache[cache_key] = (result, time.time())
    
    async def batch_process(
        self, 
        requests: List[Tuple[str, Dict]]
    ) -> List[Any]:
        """배치 처리 최적화"""
        results = []
        uncached_requests = []
        
        # 캐시된 결과 먼저 수집
        for description, context in requests:
            cached = await self.get_cached_result(description, context)
            if cached:
                results.append(cached)
            else:
                uncached_requests.append((description, context))
        
        # 캐시되지 않은 요청들을 병렬 처리
        if uncached_requests:
            tasks = [
                self._process_single_request(desc, ctx) 
                for desc, ctx in uncached_requests
            ]
            new_results = await asyncio.gather(*tasks)
            
            # 새 결과들 캐싱
            for (desc, ctx), result in zip(uncached_requests, new_results):
                await self.cache_result(desc, result, ctx)
            
            results.extend(new_results)
        
        return results
    
    async def _process_single_request(self, description: str, context: Dict) -> Any:
        """단일 요청 처리 (실제 NL 처리 로직 호출)"""
        # 실제 구현에서는 NLInputAgent.process_description 호출
        await asyncio.sleep(0.1)  # 시뮬레이션
        return {"processed": description, "context": context}

class MemoryOptimizer:
    """메모리 사용량 최적화"""
    
    def __init__(self):
        self.memory_threshold = 100 * 1024 * 1024  # 100MB
        self.cleanup_interval = 300  # 5분
        
    async def start_memory_monitor(self):
        """메모리 모니터링 시작"""
        while True:
            await asyncio.sleep(self.cleanup_interval)
            await self._cleanup_memory()
    
    async def _cleanup_memory(self):
        """메모리 정리"""
        import gc
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss
        
        if memory_usage > self.memory_threshold:
            gc.collect()

class ParallelProcessor:
    """병렬 처리 최적화"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
    
    async def process_parallel(
        self, 
        tasks: List[Tuple[str, Dict]]
    ) -> List[Any]:
        """병렬 처리"""
        async def process_with_semaphore(task):
            async with self.semaphore:
                return await self._process_task(task)
        
        return await asyncio.gather(*[
            process_with_semaphore(task) for task in tasks
        ])
    
    async def _process_task(self, task: Tuple[str, Dict]) -> Any:
        """개별 태스크 처리"""
        description, context = task
        # 실제 처리 로직
        await asyncio.sleep(0.1)
        return {"result": f"processed_{description}"}

class NLPerformanceOptimizer:
    """NL Input Agent 통합 성능 최적화"""
    
    def __init__(self):
        self.cache = NLPerformanceCache()
        self.memory_optimizer = MemoryOptimizer()
        self.parallel_processor = ParallelProcessor()
        self.metrics = PerformanceMetrics()
    
    async def initialize(self):
        """성능 최적화 시스템 초기화"""
        await self.cache.initialize()
        asyncio.create_task(self.memory_optimizer.start_memory_monitor())
    
    async def optimized_process(
        self, 
        description: str, 
        context: Dict = None
    ) -> Any:
        """최적화된 처리"""
        start_time = time.time()
        
        # 캐시 확인
        cached_result = await self.cache.get_cached_result(description, context)
        if cached_result:
            self._update_metrics(time.time() - start_time, True)
            return cached_result
        
        # 실제 처리
        result = await self._actual_process(description, context)
        
        # 결과 캐싱
        await self.cache.cache_result(description, result, context)
        
        self._update_metrics(time.time() - start_time, False)
        return result
    
    async def batch_optimized_process(
        self, 
        requests: List[Tuple[str, Dict]]
    ) -> List[Any]:
        """배치 최적화 처리"""
        return await self.cache.batch_process(requests)
    
    async def _actual_process(self, description: str, context: Dict) -> Any:
        """실제 NL 처리 (NLInputAgent 호출)"""
        # 실제 구현에서는 NLInputAgent.process_description 호출
        await asyncio.sleep(0.5)  # 시뮬레이션
        return {
            "description": description,
            "processed_at": datetime.now().isoformat(),
            "context": context
        }
    
    def _update_metrics(self, response_time: float, cache_hit: bool):
        """메트릭 업데이트"""
        self.metrics.total_requests += 1
        
        # 평균 응답 시간 계산
        total_time = self.metrics.avg_response_time * (self.metrics.total_requests - 1)
        self.metrics.avg_response_time = (total_time + response_time) / self.metrics.total_requests
        
        if cache_hit:
            self.metrics.cache_hits += 1
        else:
            self.metrics.cache_misses += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 조회"""
        cache_hit_rate = 0
        if self.metrics.total_requests > 0:
            cache_hit_rate = self.metrics.cache_hits / self.metrics.total_requests
        
        return {
            "total_requests": self.metrics.total_requests,
            "cache_hit_rate": cache_hit_rate,
            "avg_response_time": self.metrics.avg_response_time,
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses
        }