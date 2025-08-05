from typing import Dict, List, Any, Optional
import asyncio
import time
from dataclasses import dataclass
from cachetools import TTLCache
import hashlib

@dataclass
class PerformanceMetrics:
    processing_time: float
    cache_hit_rate: float
    memory_usage_mb: float
    concurrent_requests: int
    error_rate: float

class NLPerformanceOptimizer:
    """NL Agent 성능 최적화"""
    
    def __init__(self):
        # 결과 캐싱 (1시간 TTL)
        self.result_cache = TTLCache(maxsize=1000, ttl=3600)
        
        # 요청 배치 처리
        self.batch_queue = asyncio.Queue(maxsize=50)
        self.batch_processor_task = None
        
        # 성능 메트릭
        self.metrics = PerformanceMetrics(
            processing_time=0.0,
            cache_hit_rate=0.0,
            memory_usage_mb=0.0,
            concurrent_requests=0,
            error_rate=0.0
        )
        
        # 통계
        self.total_requests = 0
        self.cache_hits = 0
        self.errors = 0
    
    async def initialize(self):
        """최적화 모듈 초기화"""
        self.batch_processor_task = asyncio.create_task(self._batch_processor())
    
    async def optimize_processing(
        self,
        description: str,
        processor_func: callable,
        use_cache: bool = True,
        use_batching: bool = False
    ) -> Any:
        """최적화된 처리"""
        
        self.total_requests += 1
        
        # 1. 캐시 확인
        if use_cache:
            cache_key = self._generate_cache_key(description)
            cached_result = self.result_cache.get(cache_key)
            if cached_result:
                self.cache_hits += 1
                return cached_result
        
        # 2. 배치 처리 여부 확인
        if use_batching and self._should_batch(description):
            return await self._add_to_batch(description, processor_func)
        
        # 3. 직접 처리
        try:
            start_time = time.time()
            result = await processor_func(description)
            processing_time = time.time() - start_time
            
            # 캐시에 저장
            if use_cache:
                self.result_cache[cache_key] = result
            
            # 메트릭 업데이트
            self._update_metrics(processing_time)
            
            return result
            
        except Exception as e:
            self.errors += 1
            raise e
    
    def _generate_cache_key(self, description: str) -> str:
        """캐시 키 생성"""
        return hashlib.md5(description.encode()).hexdigest()
    
    def _should_batch(self, description: str) -> bool:
        """배치 처리 여부 결정"""
        # 짧은 요청은 배치 처리
        return len(description) < 500 and self.batch_queue.qsize() < 10
    
    async def _add_to_batch(self, description: str, processor_func: callable) -> Any:
        """배치 큐에 추가"""
        future = asyncio.Future()
        await self.batch_queue.put({
            'description': description,
            'processor': processor_func,
            'future': future
        })
        return await future
    
    async def _batch_processor(self):
        """배치 처리 워커"""
        batch = []
        
        while True:
            try:
                # 배치 수집 (최대 100ms 대기)
                timeout = 0.1
                deadline = asyncio.get_event_loop().time() + timeout
                
                while len(batch) < 5:  # 최대 배치 크기
                    remaining = deadline - asyncio.get_event_loop().time()
                    if remaining <= 0:
                        break
                    
                    try:
                        item = await asyncio.wait_for(
                            self.batch_queue.get(),
                            timeout=remaining
                        )
                        batch.append(item)
                    except asyncio.TimeoutError:
                        break
                
                # 배치 처리
                if batch:
                    await self._process_batch(batch)
                    batch = []
                
            except Exception as e:
                print(f"Batch processor error: {e}")
                await asyncio.sleep(1)
    
    async def _process_batch(self, batch: List[Dict]) -> None:
        """배치 처리 실행"""
        tasks = []
        
        for item in batch:
            task = asyncio.create_task(
                self._process_batch_item(item)
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_batch_item(self, item: Dict) -> None:
        """배치 아이템 처리"""
        try:
            result = await item['processor'](item['description'])
            item['future'].set_result(result)
        except Exception as e:
            item['future'].set_exception(e)
    
    def _update_metrics(self, processing_time: float):
        """메트릭 업데이트"""
        self.metrics.processing_time = processing_time
        self.metrics.cache_hit_rate = self.cache_hits / self.total_requests if self.total_requests > 0 else 0
        self.metrics.error_rate = self.errors / self.total_requests if self.total_requests > 0 else 0
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        return {
            'total_requests': self.total_requests,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': self.metrics.cache_hit_rate,
            'error_rate': self.metrics.error_rate,
            'avg_processing_time': self.metrics.processing_time,
            'cache_size': len(self.result_cache),
            'batch_queue_size': self.batch_queue.qsize()
        }
    
    async def cleanup(self):
        """정리"""
        if self.batch_processor_task:
            self.batch_processor_task.cancel()
            try:
                await self.batch_processor_task
            except asyncio.CancelledError:
                pass