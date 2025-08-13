#!/usr/bin/env python3
"""
Memory Usage Optimization
메모리 사용량 최적화 및 관리
"""

import asyncio
import gc
import logging
import sys
import threading
import tracemalloc
import weakref
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class MemorySnapshot:
    """메모리 스냅샷"""

    timestamp: str
    total_memory_mb: float
    used_memory_mb: float
    available_memory_mb: float
    process_memory_mb: float
    process_memory_percent: float
    gc_stats: Dict[str, int]


class MemoryProfiler:
    """메모리 프로파일러"""

    def __init__(self, top_limit: int = 10):
        self.top_limit = top_limit
        self.is_profiling = False
        self.snapshots = []

    def start_profiling(self):
        """메모리 프로파일링 시작"""
        if not self.is_profiling:
            tracemalloc.start()
            self.is_profiling = True
            logger.info("Memory profiling started")

    def stop_profiling(self):
        """메모리 프로파일링 중지"""
        if self.is_profiling:
            tracemalloc.stop()
            self.is_profiling = False
            logger.info("Memory profiling stopped")

    def take_snapshot(self) -> MemorySnapshot:
        """메모리 스냅샷 생성"""
        # 시스템 메모리 정보
        memory = psutil.virtual_memory()
        process = psutil.Process()

        # 프로세스 메모리 정보
        process_memory = process.memory_info()

        # 가비지 컬렉션 통계
        gc_stats = {f"generation_{i}": len(gc.get_objects(i)) for i in range(3)}

        snapshot = MemorySnapshot(
            timestamp=datetime.now().isoformat(),
            total_memory_mb=memory.total / (1024 * 1024),
            used_memory_mb=memory.used / (1024 * 1024),
            available_memory_mb=memory.available / (1024 * 1024),
            process_memory_mb=process_memory.rss / (1024 * 1024),
            process_memory_percent=process.memory_percent(),
            gc_stats=gc_stats,
        )

        self.snapshots.append(snapshot)
        return snapshot

    def get_top_memory_usage(self) -> List[Dict[str, Any]]:
        """메모리 사용량이 큰 객체들 조회"""
        if not self.is_profiling:
            return []

        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics("lineno")

        results = []
        for index, stat in enumerate(top_stats[: self.top_limit]):
            results.append(
                {
                    "rank": index + 1,
                    "filename": stat.traceback.format()[0],
                    "size_mb": stat.size / (1024 * 1024),
                    "size_bytes": stat.size,
                    "count": stat.count,
                }
            )

        return results

    def compare_snapshots(
        self, snapshot1: MemorySnapshot, snapshot2: MemorySnapshot
    ) -> Dict[str, Any]:
        """두 스냅샷 비교"""
        return {
            "time_diff": snapshot2.timestamp,
            "process_memory_diff_mb": snapshot2.process_memory_mb - snapshot1.process_memory_mb,
            "system_memory_diff_mb": snapshot2.used_memory_mb - snapshot1.used_memory_mb,
            "gc_objects_diff": {
                gen: snapshot2.gc_stats.get(gen, 0) - snapshot1.gc_stats.get(gen, 0)
                for gen in snapshot1.gc_stats.keys()
            },
        }


class MemoryCache:
    """메모리 효율적인 캐시"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = {}
        self.creation_times = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Any:
        """캐시에서 값 조회"""
        with self._lock:
            if key not in self.cache:
                return None

            # TTL 확인
            if self._is_expired(key):
                self._remove_item(key)
                return None

            self.access_times[key] = datetime.now()
            return self.cache[key]

    def set(self, key: str, value: Any):
        """캐시에 값 저장"""
        with self._lock:
            # 캐시 크기 제한 확인
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()

            self.cache[key] = value
            now = datetime.now()
            self.access_times[key] = now
            self.creation_times[key] = now

    def remove(self, key: str):
        """캐시에서 항목 제거"""
        with self._lock:
            self._remove_item(key)

    def clear(self):
        """캐시 전체 비우기"""
        with self._lock:
            self.cache.clear()
            self.access_times.clear()
            self.creation_times.clear()

    def cleanup_expired(self) -> int:
        """만료된 항목들 정리"""
        with self._lock:
            expired_keys = [key for key in self.cache.keys() if self._is_expired(key)]

            for key in expired_keys:
                self._remove_item(key)

            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계"""
        with self._lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": 0,  # 실제 구현에서는 히트율 추적
                "memory_usage_mb": sys.getsizeof(self.cache) / (1024 * 1024),
            }

    def _is_expired(self, key: str) -> bool:
        """항목 만료 확인"""
        if key not in self.creation_times:
            return True

        age = (datetime.now() - self.creation_times[key]).total_seconds()
        return age > self.ttl_seconds

    def _evict_lru(self):
        """LRU 방식으로 가장 오래된 항목 제거"""
        if not self.access_times:
            return

        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self._remove_item(lru_key)

    def _remove_item(self, key: str):
        """항목 제거"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.creation_times.pop(key, None)


class ObjectPool:
    """객체 풀"""

    def __init__(self, factory: Callable, max_size: int = 100):
        self.factory = factory
        self.max_size = max_size
        self.pool = []
        self._lock = threading.Lock()

    def acquire(self):
        """객체 획득"""
        with self._lock:
            if self.pool:
                return self.pool.pop()
            else:
                return self.factory()

    def release(self, obj):
        """객체 반환"""
        with self._lock:
            if len(self.pool) < self.max_size:
                # 객체 초기화/정리 로직이 필요한 경우 여기서 수행
                self._reset_object(obj)
                self.pool.append(obj)

    def _reset_object(self, obj):
        """객체 재사용을 위한 초기화"""
        # 객체 타입에 따른 초기화 로직
        if hasattr(obj, "reset"):
            obj.reset()
        elif hasattr(obj, "clear"):
            obj.clear()

    def size(self) -> int:
        """풀 크기"""
        with self._lock:
            return len(self.pool)


class MemoryOptimizer:
    """메모리 최적화 관리자"""

    def __init__(self):
        self.profiler = MemoryProfiler()
        self.caches = {}
        self.object_pools = {}
        self.optimization_enabled = True
        self.gc_threshold = (700, 10, 10)  # 기본값보다 작게 설정

        # 약한 참조 집합
        self.weak_refs = weakref.WeakSet()

        # 최적화 설정
        self._setup_gc_optimization()

    def _setup_gc_optimization(self):
        """가비지 컬렉션 최적화 설정"""
        # GC threshold 조정
        gc.set_threshold(*self.gc_threshold)

        # GC 디버깅 비활성화 (운영 환경에서)
        gc.set_debug(0)

        logger.info(f"GC optimization configured: threshold={self.gc_threshold}")

    def register_cache(self, name: str, cache: MemoryCache):
        """캐시 등록"""
        self.caches[name] = cache
        logger.info(f"Cache '{name}' registered")

    def register_object_pool(self, name: str, pool: ObjectPool):
        """객체 풀 등록"""
        self.object_pools[name] = pool
        logger.info(f"Object pool '{name}' registered")

    def optimize_memory(self) -> Dict[str, Any]:
        """메모리 최적화 실행"""
        if not self.optimization_enabled:
            return {"message": "Memory optimization disabled"}

        optimization_results = {}

        # 1. 가비지 컬렉션 강제 실행
        gc_result = self._force_garbage_collection()
        optimization_results["garbage_collection"] = gc_result

        # 2. 캐시 정리
        cache_result = self._cleanup_caches()
        optimization_results["cache_cleanup"] = cache_result

        # 3. 메모리 압축 (Python에서는 제한적)
        compression_result = self._compress_memory()
        optimization_results["memory_compression"] = compression_result

        # 4. 약한 참조 정리
        weak_ref_result = self._cleanup_weak_refs()
        optimization_results["weak_ref_cleanup"] = weak_ref_result

        logger.info(f"Memory optimization completed: {optimization_results}")
        return optimization_results

    def _force_garbage_collection(self) -> Dict[str, Any]:
        """강제 가비지 컬렉션"""
        before_objects = len(gc.get_objects())

        # 모든 세대에 대해 GC 실행
        collected = [gc.collect(i) for i in range(3)]

        after_objects = len(gc.get_objects())
        objects_freed = before_objects - after_objects

        return {
            "objects_before": before_objects,
            "objects_after": after_objects,
            "objects_freed": objects_freed,
            "collected_by_generation": collected,
        }

    def _cleanup_caches(self) -> Dict[str, Any]:
        """등록된 캐시들 정리"""
        cleanup_results = {}

        for name, cache in self.caches.items():
            if hasattr(cache, "cleanup_expired"):
                expired_count = cache.cleanup_expired()
                cleanup_results[name] = expired_count

        return cleanup_results

    def _compress_memory(self) -> Dict[str, Any]:
        """메모리 압축 시도"""
        # Python에서는 메모리 압축이 제한적이므로
        # 대신 불필요한 참조 정리

        # 모듈 캐시 정리
        modules_before = len(sys.modules)

        # 사용하지 않는 모듈 정리 (주의: 필요한 모듈을 제거하지 않도록)
        # 실제로는 매우 조심스럽게 접근해야 함

        return {"modules_count": modules_before, "compression_attempted": True}

    def _cleanup_weak_refs(self) -> Dict[str, Any]:
        """약한 참조 정리"""
        initial_count = len(self.weak_refs)

        # 약한 참조 집합은 자동으로 정리되므로 현재 크기만 확인
        current_count = len(self.weak_refs)

        return {"initial_weak_refs": initial_count, "current_weak_refs": current_count}

    @contextmanager
    def memory_monitoring(self, description: str = "operation"):
        """메모리 사용량 모니터링 컨텍스트"""
        if not self.profiler.is_profiling:
            self.profiler.start_profiling()

        snapshot_before = self.profiler.take_snapshot()

        try:
            yield
        finally:
            snapshot_after = self.profiler.take_snapshot()
            diff = self.profiler.compare_snapshots(snapshot_before, snapshot_after)

            logger.info(
                f"Memory usage for '{description}': " f"{diff['process_memory_diff_mb']:.2f} MB"
            )

    def get_memory_report(self) -> Dict[str, Any]:
        """메모리 사용 보고서"""
        current_snapshot = self.profiler.take_snapshot()
        top_usage = self.profiler.get_top_memory_usage()

        # 캐시 통계
        cache_stats = {}
        for name, cache in self.caches.items():
            if hasattr(cache, "get_stats"):
                cache_stats[name] = cache.get_stats()

        # 객체 풀 통계
        pool_stats = {}
        for name, pool in self.object_pools.items():
            pool_stats[name] = {"size": pool.size(), "max_size": pool.max_size}

        return {
            "current_memory": {
                "process_memory_mb": current_snapshot.process_memory_mb,
                "process_memory_percent": current_snapshot.process_memory_percent,
                "system_memory_used_mb": current_snapshot.used_memory_mb,
                "system_memory_available_mb": current_snapshot.available_memory_mb,
            },
            "gc_stats": current_snapshot.gc_stats,
            "top_memory_usage": top_usage,
            "cache_stats": cache_stats,
            "pool_stats": pool_stats,
            "optimization_enabled": self.optimization_enabled,
        }

    def set_memory_limit(self, limit_mb: int):
        """메모리 사용량 제한 설정 (모니터링 목적)"""
        self.memory_limit_mb = limit_mb
        logger.info(f"Memory limit set to: {limit_mb} MB")

    def check_memory_pressure(self) -> bool:
        """메모리 압박 상태 확인"""
        if not hasattr(self, "memory_limit_mb"):
            return False

        current_usage = self.profiler.take_snapshot().process_memory_mb
        return current_usage > (self.memory_limit_mb * 0.8)  # 80% 임계치

    def enable_optimization(self):
        """메모리 최적화 활성화"""
        self.optimization_enabled = True
        logger.info("Memory optimization enabled")

    def disable_optimization(self):
        """메모리 최적화 비활성화"""
        self.optimization_enabled = False
        logger.info("Memory optimization disabled")


# 글로벌 메모리 최적화기
memory_optimizer = MemoryOptimizer()

# 기본 캐시들 생성 및 등록
project_cache = MemoryCache(max_size=100, ttl_seconds=3600)
template_cache = MemoryCache(max_size=50, ttl_seconds=7200)

memory_optimizer.register_cache("projects", project_cache)
memory_optimizer.register_cache("templates", template_cache)


def optimize_memory_periodically():
    """주기적 메모리 최적화"""
    asyncio.create_task(_periodic_optimization())


async def _periodic_optimization():
    """주기적 최적화 태스크"""
    while True:
        try:
            if memory_optimizer.check_memory_pressure():
                logger.warning("Memory pressure detected, running optimization")
                memory_optimizer.optimize_memory()

            await asyncio.sleep(300)  # 5분마다 체크
        except Exception as e:
            logger.error(f"Error in periodic optimization: {e}")
            await asyncio.sleep(60)  # 에러 시 1분 대기


def initialize_memory_optimization():
    """메모리 최적화 초기화"""
    try:
        memory_optimizer.profiler.start_profiling()
        memory_optimizer.set_memory_limit(512)  # 512MB 제한

        # 주기적 최적화 시작
        optimize_memory_periodically()

        logger.info("Memory optimization initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize memory optimization: {e}")
        return False


if __name__ == "__main__":
    # 테스트 실행
    initialize_memory_optimization()

    # 메모리 사용량 테스트
    with memory_optimizer.memory_monitoring("test_operation"):
        # 메모리를 사용하는 작업 시뮬레이션
        large_list = [i for i in range(100000)]

        # 캐시 테스트
        project_cache.set("test_project", {"data": large_list[:1000]})
        cached_data = project_cache.get("test_project")

        print(f"Cached data size: {len(cached_data['data'])}")

    # 최적화 실행
    optimization_result = memory_optimizer.optimize_memory()
    print("Optimization result:", optimization_result)

    # 메모리 보고서
    report = memory_optimizer.get_memory_report()
    print("Memory report:", report)
