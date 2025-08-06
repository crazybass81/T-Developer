# backend/src/agents/implementations/search/cache_integration.py
from typing import Dict, List, Any, Optional
import asyncio
import time
from dataclasses import dataclass

from .caching_system import SearchCacheManager, CacheWarmer, CacheInvalidator, CacheAnalytics
from .cache_strategies import HybridCacheStrategy, CacheDecision

@dataclass
class CacheConfig:
    enabled: bool = True
    redis_url: str = "redis://localhost:6379"
    local_cache_size: int = 1000
    default_ttl: int = 3600
    max_cache_size_mb: int = 512
    warming_enabled: bool = True
    analytics_enabled: bool = True

class IntegratedCacheSystem:
    """통합 캐시 시스템"""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache_manager = SearchCacheManager(config.redis_url)
        self.cache_strategy = HybridCacheStrategy()
        self.cache_warmer = CacheWarmer(self.cache_manager)
        self.cache_invalidator = CacheInvalidator(self.cache_manager)
        self.cache_analytics = CacheAnalytics(self.cache_manager)
        
        self.performance_metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_response_time': 0.0,
            'cache_size_mb': 0.0
        }

    async def initialize(self):
        """캐시 시스템 초기화"""
        if not self.config.enabled:
            return

        await self.cache_manager.initialize()
        
        # 백그라운드 작업 시작
        asyncio.create_task(self._background_maintenance())
        
        print("✅ 통합 캐시 시스템 초기화 완료")

    async def get_cached_results(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """캐시된 검색 결과 조회"""
        
        if not self.config.enabled:
            return None

        start_time = time.time()
        
        try:
            results = await self.cache_manager.get(query, filters, context)
            
            # 성능 메트릭 업데이트
            response_time = time.time() - start_time
            if results is not None:
                self.performance_metrics['cache_hits'] += 1
                await self._update_response_time(response_time)
                return results
            else:
                self.performance_metrics['cache_misses'] += 1
                return None
                
        except Exception as e:
            print(f"캐시 조회 오류: {e}")
            return None

    async def cache_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        filters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """검색 결과 캐싱"""
        
        if not self.config.enabled or not results:
            return False

        try:
            # 캐시 전략에 따른 결정
            decision = await self.cache_strategy.should_cache(
                query, results, context or {}
            )
            
            if not decision.should_cache:
                return False

            # 캐시 저장
            await self.cache_manager.set(
                query=query,
                results=results,
                filters=filters,
                context=context,
                ttl=decision.ttl
            )
            
            return True
            
        except Exception as e:
            print(f"캐시 저장 오류: {e}")
            return False

    async def invalidate_cache(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """이벤트 기반 캐시 무효화"""
        
        if not self.config.enabled:
            return

        try:
            await self.cache_invalidator.invalidate_by_event(
                event_type, event_data
            )
        except Exception as e:
            print(f"캐시 무효화 오류: {e}")

    async def warm_cache(
        self,
        search_logs: List[Dict[str, Any]]
    ) -> None:
        """캐시 워밍"""
        
        if not self.config.enabled or not self.config.warming_enabled:
            return

        try:
            await self.cache_warmer.warm_popular_queries(search_logs)
        except Exception as e:
            print(f"캐시 워밍 오류: {e}")

    async def get_cache_analytics(self) -> Dict[str, Any]:
        """캐시 분석 데이터 조회"""
        
        if not self.config.enabled or not self.config.analytics_enabled:
            return {}

        try:
            analytics = await self.cache_analytics.analyze_performance()
            
            # 성능 메트릭 추가
            analytics.update(self.performance_metrics)
            
            return analytics
            
        except Exception as e:
            print(f"캐시 분석 오류: {e}")
            return {}

    async def _background_maintenance(self):
        """백그라운드 유지보수 작업"""
        
        while True:
            try:
                # 30분마다 실행
                await asyncio.sleep(1800)
                
                # 캐시 분석
                if self.config.analytics_enabled:
                    analytics = await self.get_cache_analytics()
                    await self._process_analytics(analytics)
                
                # 메트릭 리셋 (1시간마다)
                if int(time.time()) % 3600 == 0:
                    await self._reset_metrics()
                    
            except Exception as e:
                print(f"백그라운드 유지보수 오류: {e}")

    async def _process_analytics(self, analytics: Dict[str, Any]):
        """분석 결과 처리"""
        
        hit_rate = analytics.get('hit_rate', 0)
        
        # 히트율이 낮으면 경고
        if hit_rate < 0.3:
            print(f"⚠️ 캐시 히트율이 낮습니다: {hit_rate:.2%}")
        
        # 권장사항 출력
        recommendations = analytics.get('recommendations', [])
        for rec in recommendations:
            print(f"💡 캐시 최적화 권장: {rec}")

    async def _update_response_time(self, response_time: float):
        """응답 시간 업데이트"""
        
        current_avg = self.performance_metrics['avg_response_time']
        total_hits = self.performance_metrics['cache_hits']
        
        # 이동 평균 계산
        if total_hits == 1:
            self.performance_metrics['avg_response_time'] = response_time
        else:
            self.performance_metrics['avg_response_time'] = (
                (current_avg * (total_hits - 1) + response_time) / total_hits
            )

    async def _reset_metrics(self):
        """메트릭 리셋"""
        
        # 이전 메트릭 로그
        print(f"📊 캐시 성능 (지난 1시간): "
              f"히트율 {self.performance_metrics['cache_hits']}/{self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses']}, "
              f"평균 응답시간 {self.performance_metrics['avg_response_time']:.3f}s")
        
        # 메트릭 초기화
        self.performance_metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_response_time': 0.0,
            'cache_size_mb': 0.0
        }

class CacheMiddleware:
    """캐시 미들웨어"""

    def __init__(self, cache_system: IntegratedCacheSystem):
        self.cache_system = cache_system

    async def __call__(
        self,
        search_func,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """캐시 미들웨어 실행"""

        # 1. 캐시에서 조회
        cached_results = await self.cache_system.get_cached_results(
            query, filters, context
        )
        
        if cached_results is not None:
            return cached_results

        # 2. 실제 검색 수행
        results = await search_func(query, filters, context)

        # 3. 결과 캐싱
        await self.cache_system.cache_results(
            query, results, filters, context
        )

        return results

# 사용 예시
async def create_search_agent_with_cache():
    """캐시가 통합된 Search Agent 생성 예시"""
    
    # 캐시 설정
    cache_config = CacheConfig(
        enabled=True,
        redis_url="redis://localhost:6379",
        local_cache_size=1000,
        default_ttl=3600,
        warming_enabled=True,
        analytics_enabled=True
    )
    
    # 통합 캐시 시스템 생성
    cache_system = IntegratedCacheSystem(cache_config)
    await cache_system.initialize()
    
    # 캐시 미들웨어 생성
    cache_middleware = CacheMiddleware(cache_system)
    
    return cache_system, cache_middleware