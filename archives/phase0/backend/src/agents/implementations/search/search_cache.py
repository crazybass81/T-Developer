# backend/src/agents/implementations/search_cache.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta

@dataclass
class CacheEntry:
    key: str
    data: Any
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None

class SearchCache:
    """검색 결과 캐시"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hit_count = 0
        self.miss_count = 0
        
        # 백그라운드 정리 태스크 시작
        asyncio.create_task(self._cleanup_expired())

    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        
        if key not in self.cache:
            self.miss_count += 1
            return None
        
        entry = self.cache[key]
        
        # 만료 확인
        if datetime.now() > entry.expires_at:
            del self.cache[key]
            self.miss_count += 1
            return None
        
        # 액세스 정보 업데이트
        entry.access_count += 1
        entry.last_accessed = datetime.now()
        
        self.hit_count += 1
        return entry.data

    async def set(
        self,
        key: str,
        data: Any,
        ttl: Optional[int] = None
    ) -> None:
        """캐시에 데이터 저장"""
        
        # 캐시 크기 제한 확인
        if len(self.cache) >= self.max_size:
            await self._evict_lru()
        
        ttl = ttl or self.default_ttl
        now = datetime.now()
        
        entry = CacheEntry(
            key=key,
            data=data,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl)
        )
        
        self.cache[key] = entry

    async def delete(self, key: str) -> bool:
        """캐시에서 데이터 삭제"""
        
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    async def clear(self) -> None:
        """캐시 전체 삭제"""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0

    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계"""
        
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }

    async def _evict_lru(self) -> None:
        """LRU 방식으로 캐시 항목 제거"""
        
        if not self.cache:
            return
        
        # 가장 오래 전에 액세스된 항목 찾기
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed or self.cache[k].created_at
        )
        
        del self.cache[lru_key]

    async def _cleanup_expired(self) -> None:
        """만료된 캐시 항목 정리"""
        
        while True:
            try:
                now = datetime.now()
                expired_keys = [
                    key for key, entry in self.cache.items()
                    if now > entry.expires_at
                ]
                
                for key in expired_keys:
                    del self.cache[key]
                
                # 10분마다 정리
                await asyncio.sleep(600)
                
            except Exception as e:
                print(f"Cache cleanup error: {e}")
                await asyncio.sleep(60)


class SearchCacheManager:
    """검색 캐시 관리자"""

    def __init__(self):
        self.result_cache = SearchCache(max_size=500, default_ttl=1800)  # 30분
        self.query_cache = SearchCache(max_size=200, default_ttl=3600)   # 1시간
        self.metadata_cache = SearchCache(max_size=1000, default_ttl=7200)  # 2시간

    def generate_cache_key(
        self,
        query_data: Dict[str, Any],
        cache_type: str = "result"
    ) -> str:
        """캐시 키 생성"""
        
        # 쿼리 데이터를 정규화하여 일관된 키 생성
        normalized_data = self._normalize_query_data(query_data)
        
        # JSON 직렬화 후 해시
        json_str = json.dumps(normalized_data, sort_keys=True)
        hash_obj = hashlib.md5(json_str.encode())
        
        return f"{cache_type}:{hash_obj.hexdigest()}"

    async def get_cached_results(
        self,
        query_data: Dict[str, Any]
    ) -> Optional[List[Any]]:
        """캐시된 검색 결과 조회"""
        
        cache_key = self.generate_cache_key(query_data, "result")
        return await self.result_cache.get(cache_key)

    async def cache_results(
        self,
        query_data: Dict[str, Any],
        results: List[Any],
        ttl: Optional[int] = None
    ) -> None:
        """검색 결과 캐시"""
        
        cache_key = self.generate_cache_key(query_data, "result")
        await self.result_cache.set(cache_key, results, ttl)

    async def get_cached_query(
        self,
        requirements: Dict[str, Any]
    ) -> Optional[List[Any]]:
        """캐시된 쿼리 조회"""
        
        cache_key = self.generate_cache_key(requirements, "query")
        return await self.query_cache.get(cache_key)

    async def cache_query(
        self,
        requirements: Dict[str, Any],
        queries: List[Any],
        ttl: Optional[int] = None
    ) -> None:
        """쿼리 캐시"""
        
        cache_key = self.generate_cache_key(requirements, "query")
        await self.query_cache.set(cache_key, queries, ttl)

    async def get_component_metadata(
        self,
        component_id: str
    ) -> Optional[Dict[str, Any]]:
        """컴포넌트 메타데이터 조회"""
        
        cache_key = f"metadata:{component_id}"
        return await self.metadata_cache.get(cache_key)

    async def cache_component_metadata(
        self,
        component_id: str,
        metadata: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """컴포넌트 메타데이터 캐시"""
        
        cache_key = f"metadata:{component_id}"
        await self.metadata_cache.set(cache_key, metadata, ttl)

    def _normalize_query_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """쿼리 데이터 정규화"""
        
        normalized = {}
        
        # 키워드 정규화
        if 'keywords' in data:
            keywords = data['keywords']
            if isinstance(keywords, list):
                # 소문자 변환 및 정렬
                normalized['keywords'] = sorted([k.lower().strip() for k in keywords])
            else:
                normalized['keywords'] = [str(keywords).lower().strip()]
        
        # 기타 필드 정규화
        for key, value in data.items():
            if key == 'keywords':
                continue
            
            if isinstance(value, str):
                normalized[key] = value.lower().strip()
            elif isinstance(value, list):
                normalized[key] = sorted([str(v).lower().strip() for v in value])
            else:
                normalized[key] = value
        
        return normalized

    async def invalidate_pattern(self, pattern: str) -> int:
        """패턴에 맞는 캐시 항목 무효화"""
        
        invalidated_count = 0
        
        # 결과 캐시에서 패턴 매칭 항목 삭제
        keys_to_delete = [
            key for key in self.result_cache.cache.keys()
            if pattern in key
        ]
        
        for key in keys_to_delete:
            await self.result_cache.delete(key)
            invalidated_count += 1
        
        # 쿼리 캐시에서도 삭제
        keys_to_delete = [
            key for key in self.query_cache.cache.keys()
            if pattern in key
        ]
        
        for key in keys_to_delete:
            await self.query_cache.delete(key)
            invalidated_count += 1
        
        return invalidated_count

    def get_cache_stats(self) -> Dict[str, Any]:
        """전체 캐시 통계"""
        
        return {
            'result_cache': self.result_cache.get_stats(),
            'query_cache': self.query_cache.get_stats(),
            'metadata_cache': self.metadata_cache.get_stats()
        }


class CacheWarmer:
    """캐시 워밍"""

    def __init__(self, cache_manager: SearchCacheManager):
        self.cache_manager = cache_manager
        self.popular_queries = []
        self.warming_in_progress = False

    async def warm_cache(
        self,
        search_agent: Any,
        popular_requirements: List[Dict[str, Any]]
    ) -> None:
        """인기 있는 쿼리로 캐시 워밍"""
        
        if self.warming_in_progress:
            return
        
        self.warming_in_progress = True
        
        try:
            for requirements in popular_requirements:
                # 캐시에 없는 경우에만 검색 실행
                cached_results = await self.cache_manager.get_cached_results(requirements)
                
                if cached_results is None:
                    # 실제 검색 실행
                    results = await search_agent.search_components(requirements)
                    
                    # 결과 캐시
                    await self.cache_manager.cache_results(
                        requirements,
                        results,
                        ttl=7200  # 2시간
                    )
                    
                    # 과부하 방지를 위한 지연
                    await asyncio.sleep(1)
        
        finally:
            self.warming_in_progress = False

    async def schedule_warming(
        self,
        search_agent: Any,
        interval_hours: int = 6
    ) -> None:
        """주기적 캐시 워밍 스케줄링"""
        
        while True:
            try:
                # 인기 있는 요구사항 패턴
                popular_requirements = [
                    {
                        'functional_requirements': ['authentication', 'dashboard'],
                        'technology_stack': ['react', 'javascript']
                    },
                    {
                        'functional_requirements': ['api', 'rest'],
                        'technology_stack': ['node', 'express']
                    },
                    {
                        'functional_requirements': ['database', 'orm'],
                        'technology_stack': ['python', 'django']
                    }
                ]
                
                await self.warm_cache(search_agent, popular_requirements)
                
                # 다음 워밍까지 대기
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                print(f"Cache warming error: {e}")
                await asyncio.sleep(3600)  # 1시간 후 재시도


class CacheAnalyzer:
    """캐시 분석기"""

    def __init__(self, cache_manager: SearchCacheManager):
        self.cache_manager = cache_manager

    async def analyze_cache_performance(self) -> Dict[str, Any]:
        """캐시 성능 분석"""
        
        stats = self.cache_manager.get_cache_stats()
        
        analysis = {
            'overall_performance': self._calculate_overall_performance(stats),
            'cache_efficiency': self._analyze_cache_efficiency(stats),
            'recommendations': self._generate_recommendations(stats)
        }
        
        return analysis

    def _calculate_overall_performance(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """전체 성능 계산"""
        
        total_hits = sum(cache['hit_count'] for cache in stats.values())
        total_requests = sum(cache['total_requests'] for cache in stats.values())
        
        overall_hit_rate = total_hits / total_requests if total_requests > 0 else 0
        
        return {
            'overall_hit_rate': overall_hit_rate,
            'total_requests': total_requests,
            'total_hits': total_hits,
            'performance_grade': self._grade_performance(overall_hit_rate)
        }

    def _analyze_cache_efficiency(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """캐시 효율성 분석"""
        
        efficiency = {}
        
        for cache_name, cache_stats in stats.items():
            utilization = cache_stats['size'] / cache_stats['max_size']
            
            efficiency[cache_name] = {
                'utilization': utilization,
                'hit_rate': cache_stats['hit_rate'],
                'efficiency_score': cache_stats['hit_rate'] * utilization
            }
        
        return efficiency

    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """개선 권장사항 생성"""
        
        recommendations = []
        
        for cache_name, cache_stats in stats.items():
            hit_rate = cache_stats['hit_rate']
            utilization = cache_stats['size'] / cache_stats['max_size']
            
            if hit_rate < 0.5:
                recommendations.append(
                    f"{cache_name}: Low hit rate ({hit_rate:.1%}). "
                    "Consider adjusting TTL or cache key strategy."
                )
            
            if utilization > 0.9:
                recommendations.append(
                    f"{cache_name}: High utilization ({utilization:.1%}). "
                    "Consider increasing cache size."
                )
            
            if utilization < 0.3 and cache_stats['size'] > 0:
                recommendations.append(
                    f"{cache_name}: Low utilization ({utilization:.1%}). "
                    "Consider reducing cache size."
                )
        
        return recommendations

    def _grade_performance(self, hit_rate: float) -> str:
        """성능 등급 매기기"""
        
        if hit_rate >= 0.8:
            return 'A'
        elif hit_rate >= 0.6:
            return 'B'
        elif hit_rate >= 0.4:
            return 'C'
        elif hit_rate >= 0.2:
            return 'D'
        else:
            return 'F'