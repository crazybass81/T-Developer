# backend/src/agents/implementations/search/caching_system.py
from typing import Dict, List, Any, Optional, Tuple
import asyncio
import time
import hashlib
import json
from dataclasses import dataclass
from collections import OrderedDict
import redis.asyncio as redis

@dataclass
class CacheEntry:
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl: int
    size_bytes: int

@dataclass
class CacheStats:
    hit_count: int
    miss_count: int
    hit_rate: float
    total_size_mb: float
    entry_count: int
    eviction_count: int

class SearchCacheManager:
    """검색 결과 캐싱 시스템"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = None
        self.redis_url = redis_url
        self.local_cache = LRUCache(max_size=1000)
        self.cache_stats = CacheStats(0, 0, 0.0, 0.0, 0, 0)
        
        # 캐시 설정
        self.default_ttl = 3600  # 1시간
        self.max_cache_size_mb = 512
        self.compression_enabled = True

    async def initialize(self):
        """캐시 시스템 초기화"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            print("✅ Redis 연결 성공")
        except Exception as e:
            print(f"⚠️ Redis 연결 실패, 로컬 캐시만 사용: {e}")
            self.redis_client = None

    async def get(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """캐시에서 검색 결과 조회"""

        cache_key = self._generate_cache_key(query, filters, context)

        # 1. 로컬 캐시 확인
        local_result = await self.local_cache.get(cache_key)
        if local_result:
            self.cache_stats.hit_count += 1
            await self._update_access_stats(cache_key, 'local')
            return local_result

        # 2. Redis 캐시 확인
        if self.redis_client:
            redis_result = await self._get_from_redis(cache_key)
            if redis_result:
                # 로컬 캐시에도 저장
                await self.local_cache.set(cache_key, redis_result, ttl=300)
                self.cache_stats.hit_count += 1
                await self._update_access_stats(cache_key, 'redis')
                return redis_result

        # 캐시 미스
        self.cache_stats.miss_count += 1
        return None

    async def set(
        self,
        query: str,
        results: List[Dict[str, Any]],
        filters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> None:
        """검색 결과를 캐시에 저장"""

        cache_key = self._generate_cache_key(query, filters, context)
        cache_ttl = ttl or self.default_ttl

        # 캐시 가치 평가
        if not await self._should_cache(query, results, context):
            return

        # 병렬로 로컬 캐시와 Redis에 저장
        tasks = [
            self.local_cache.set(cache_key, results, cache_ttl)
        ]

        if self.redis_client:
            tasks.append(self._set_to_redis(cache_key, results, cache_ttl))

        await asyncio.gather(*tasks, return_exceptions=True)

    def _generate_cache_key(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """캐시 키 생성"""

        key_data = {
            'query': query.lower().strip(),
            'filters': filters or {},
            'context': {
                'tech_stack': context.get('tech_stack', []) if context else [],
                'category': context.get('category', '') if context else ''
            }
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return f"search:{hashlib.md5(key_string.encode()).hexdigest()}"

    async def _should_cache(
        self,
        query: str,
        results: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """캐시 저장 여부 결정"""

        # 결과가 없으면 캐시하지 않음
        if not results:
            return False

        # 결과가 너무 많으면 캐시하지 않음 (메모리 절약)
        if len(results) > 1000:
            return False

        # 개인화된 결과는 캐시하지 않음
        if context and context.get('user_id'):
            return False

        # 실시간 데이터는 짧은 TTL로 캐시
        if context and context.get('real_time', False):
            return True

        return True

    async def _get_from_redis(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """Redis에서 데이터 조회"""
        try:
            data = await self.redis_client.get(key)
            if data:
                if self.compression_enabled:
                    data = self._decompress(data)
                return json.loads(data)
        except Exception as e:
            print(f"Redis 조회 오류: {e}")
        return None

    async def _set_to_redis(
        self,
        key: str,
        value: List[Dict[str, Any]],
        ttl: int
    ) -> None:
        """Redis에 데이터 저장"""
        try:
            data = json.dumps(value)
            if self.compression_enabled:
                data = self._compress(data)
            
            await self.redis_client.setex(key, ttl, data)
        except Exception as e:
            print(f"Redis 저장 오류: {e}")

    def _compress(self, data: str) -> bytes:
        """데이터 압축"""
        import gzip
        return gzip.compress(data.encode('utf-8'))

    def _decompress(self, data: bytes) -> str:
        """데이터 압축 해제"""
        import gzip
        return gzip.decompress(data).decode('utf-8')

class LRUCache:
    """로컬 LRU 캐시"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.stats = {'hits': 0, 'misses': 0}

    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        if key in self.cache:
            # LRU 순서 업데이트
            value = self.cache.pop(key)
            self.cache[key] = value
            self.stats['hits'] += 1
            
            # TTL 체크
            if value['expires_at'] > time.time():
                return value['data']
            else:
                del self.cache[key]
        
        self.stats['misses'] += 1
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """캐시에 값 저장"""
        # 용량 초과 시 오래된 항목 제거
        while len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)

        self.cache[key] = {
            'data': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }

    def clear(self) -> None:
        """캐시 전체 삭제"""
        self.cache.clear()

class CacheWarmer:
    """캐시 워밍 시스템"""

    def __init__(self, cache_manager: SearchCacheManager):
        self.cache_manager = cache_manager
        self.popular_queries = []
        self.warming_enabled = True

    async def warm_popular_queries(
        self,
        search_logs: List[Dict[str, Any]]
    ) -> None:
        """인기 쿼리 사전 캐싱"""

        if not self.warming_enabled:
            return

        # 인기 쿼리 추출
        query_frequency = {}
        for log in search_logs:
            query = log.get('query', '').lower().strip()
            if len(query) > 2:  # 너무 짧은 쿼리 제외
                query_frequency[query] = query_frequency.get(query, 0) + 1

        # 상위 50개 인기 쿼리
        popular_queries = sorted(
            query_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:50]

        # 병렬로 캐시 워밍
        warming_tasks = []
        for query, frequency in popular_queries:
            if frequency >= 5:  # 최소 5회 이상 검색된 쿼리만
                task = self._warm_single_query(query)
                warming_tasks.append(task)

        if warming_tasks:
            await asyncio.gather(*warming_tasks, return_exceptions=True)
            print(f"✅ {len(warming_tasks)}개 인기 쿼리 캐시 워밍 완료")

    async def _warm_single_query(self, query: str) -> None:
        """단일 쿼리 캐시 워밍"""
        try:
            # 실제 검색 수행 (SearchAgent 호출)
            # 여기서는 시뮬레이션
            mock_results = [
                {'id': f'comp_{i}', 'name': f'Component {i}'}
                for i in range(10)
            ]
            
            await self.cache_manager.set(
                query=query,
                results=mock_results,
                ttl=7200  # 2시간
            )
        except Exception as e:
            print(f"쿼리 '{query}' 캐시 워밍 실패: {e}")

class CacheInvalidator:
    """캐시 무효화 시스템"""

    def __init__(self, cache_manager: SearchCacheManager):
        self.cache_manager = cache_manager
        self.invalidation_patterns = [
            {'pattern': 'component_updated', 'action': 'invalidate_component'},
            {'pattern': 'new_component_added', 'action': 'invalidate_category'},
            {'pattern': 'popularity_changed', 'action': 'invalidate_popular'}
        ]

    async def invalidate_by_event(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """이벤트 기반 캐시 무효화"""

        for pattern in self.invalidation_patterns:
            if pattern['pattern'] == event_type:
                await self._execute_invalidation(
                    pattern['action'],
                    event_data
                )

    async def _execute_invalidation(
        self,
        action: str,
        data: Dict[str, Any]
    ) -> None:
        """무효화 실행"""

        if action == 'invalidate_component':
            component_id = data.get('component_id')
            await self._invalidate_component_cache(component_id)
        
        elif action == 'invalidate_category':
            category = data.get('category')
            await self._invalidate_category_cache(category)
        
        elif action == 'invalidate_popular':
            await self._invalidate_popular_cache()

    async def _invalidate_component_cache(self, component_id: str) -> None:
        """특정 컴포넌트 관련 캐시 무효화"""
        if self.cache_manager.redis_client:
            # Redis에서 패턴 매칭으로 삭제
            pattern = f"search:*{component_id}*"
            keys = await self.cache_manager.redis_client.keys(pattern)
            if keys:
                await self.cache_manager.redis_client.delete(*keys)

class CacheAnalytics:
    """캐시 분석 시스템"""

    def __init__(self, cache_manager: SearchCacheManager):
        self.cache_manager = cache_manager
        self.analytics_data = {
            'hit_rate_history': [],
            'popular_keys': {},
            'eviction_reasons': {}
        }

    async def analyze_performance(self) -> Dict[str, Any]:
        """캐시 성능 분석"""

        stats = self.cache_manager.cache_stats
        
        # 히트율 계산
        total_requests = stats.hit_count + stats.miss_count
        hit_rate = stats.hit_count / total_requests if total_requests > 0 else 0

        # 메모리 효율성
        avg_entry_size = stats.total_size_mb / stats.entry_count if stats.entry_count > 0 else 0

        return {
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'cache_size_mb': stats.total_size_mb,
            'entry_count': stats.entry_count,
            'avg_entry_size_kb': avg_entry_size * 1024,
            'eviction_count': stats.eviction_count,
            'recommendations': self._generate_recommendations(hit_rate, stats)
        }

    def _generate_recommendations(
        self,
        hit_rate: float,
        stats: CacheStats
    ) -> List[str]:
        """캐시 최적화 권장사항"""

        recommendations = []

        if hit_rate < 0.5:
            recommendations.append("캐시 히트율이 낮습니다. TTL 증가를 고려하세요.")
        
        if stats.eviction_count > stats.entry_count * 0.1:
            recommendations.append("캐시 제거가 빈번합니다. 캐시 크기 증가를 고려하세요.")
        
        if stats.total_size_mb > self.cache_manager.max_cache_size_mb * 0.9:
            recommendations.append("캐시 메모리 사용량이 높습니다. 압축 활성화를 고려하세요.")

        return recommendations