"""Caching Layer - Multi-level caching for T-Developer.

Phase 6: P6-T1 - Performance Optimization
Implement comprehensive caching strategies.
"""

from __future__ import annotations

import asyncio
import gzip
import hashlib
import logging
import pickle
import threading
from abc import ABC, abstractmethod
from collections import OrderedDict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Generic, Optional, TypeVar

# Type variables
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# Constants
DEFAULT_TTL: int = 3600  # 1 hour
DEFAULT_MAX_SIZE: int = 1000
CACHE_VERSION: str = "1.0"

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry(Generic[T]):
    """Cache entry with metadata."""

    value: T
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def access(self) -> None:
        """Record access to this entry."""
        self.access_count += 1
        self.last_accessed = datetime.now()


@dataclass
class CacheStats:
    """Cache performance statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    memory_usage: int = 0  # bytes

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def miss_rate(self) -> float:
        """Calculate miss rate."""
        return 1.0 - self.hit_rate


class CacheBackend(ABC, Generic[K, V]):
    """Abstract cache backend."""

    @abstractmethod
    async def get(self, key: K) -> Optional[V]:
        """Get value by key."""
        pass

    @abstractmethod
    async def set(self, key: K, value: V, ttl: Optional[int] = None) -> None:
        """Set value with optional TTL."""
        pass

    @abstractmethod
    async def delete(self, key: K) -> bool:
        """Delete key."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all entries."""
        pass

    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pass


class MemoryCache(CacheBackend[str, Any]):
    """In-memory LRU cache with TTL support."""

    def __init__(self, max_size: int = DEFAULT_MAX_SIZE, default_ttl: int = DEFAULT_TTL):
        """Initialize memory cache.

        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry[Any]] = OrderedDict()
        self._stats = CacheStats()
        self._lock = threading.RLock()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None

            entry = self._cache[key]

            # Check expiration
            if entry.is_expired():
                del self._cache[key]
                self._stats.misses += 1
                self._stats.evictions += 1
                return None

            # Move to end (most recently used)
            entry.access()
            self._cache.move_to_end(key)
            self._stats.hits += 1

            return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value with optional TTL."""
        with self._lock:
            # Calculate expiration
            expires_at = None
            if ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            elif self.default_ttl > 0:
                expires_at = datetime.now() + timedelta(seconds=self.default_ttl)

            # Calculate size (approximate)
            try:
                size_bytes = len(pickle.dumps(value))
            except Exception:
                size_bytes = 0

            # Create entry
            entry = CacheEntry(
                value=value, created_at=datetime.now(), expires_at=expires_at, size_bytes=size_bytes
            )

            # Add to cache
            self._cache[key] = entry
            self._cache.move_to_end(key)

            # Evict if necessary
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats.evictions += 1

            self._update_stats()

    async def delete(self, key: str) -> bool:
        """Delete key."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._update_stats()
                return True
            return False

    async def clear(self) -> None:
        """Clear all entries."""
        with self._lock:
            self._cache.clear()
            self._update_stats()

    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                evictions=self._stats.evictions,
                size=len(self._cache),
                memory_usage=sum(entry.size_bytes for entry in self._cache.values()),
            )

    def _update_stats(self) -> None:
        """Update cache statistics."""
        self._stats.size = len(self._cache)
        self._stats.memory_usage = sum(entry.size_bytes for entry in self._cache.values())


class FileCache(CacheBackend[str, Any]):
    """Persistent file-based cache."""

    def __init__(self, cache_dir: Path, max_size: int = DEFAULT_MAX_SIZE):
        """Initialize file cache.

        Args:
            cache_dir: Directory to store cache files
            max_size: Maximum number of cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size = max_size
        self._stats = CacheStats()
        self._lock = asyncio.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        async with self._lock:
            cache_file = self._get_cache_file(key)

            if not cache_file.exists():
                self._stats.misses += 1
                return None

            try:
                with gzip.open(cache_file, "rb") as f:
                    data = pickle.load(f)

                # Check expiration
                if "expires_at" in data and data["expires_at"]:
                    if datetime.now() > data["expires_at"]:
                        cache_file.unlink()
                        self._stats.misses += 1
                        self._stats.evictions += 1
                        return None

                # Update access time
                cache_file.touch()
                self._stats.hits += 1

                return data["value"]

            except Exception as e:
                self.logger.error(f"Error reading cache file {cache_file}: {e}")
                self._stats.misses += 1
                return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value with optional TTL."""
        async with self._lock:
            cache_file = self._get_cache_file(key)

            # Calculate expiration
            expires_at = None
            if ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl)

            data = {
                "value": value,
                "created_at": datetime.now(),
                "expires_at": expires_at,
                "version": CACHE_VERSION,
            }

            try:
                with gzip.open(cache_file, "wb") as f:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

                # Cleanup old files if necessary
                await self._cleanup_old_files()

            except Exception as e:
                self.logger.error(f"Error writing cache file {cache_file}: {e}")

    async def delete(self, key: str) -> bool:
        """Delete key."""
        async with self._lock:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink()
                return True
            return False

    async def clear(self) -> None:
        """Clear all entries."""
        async with self._lock:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()

    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return CacheStats(
            hits=self._stats.hits,
            misses=self._stats.misses,
            evictions=self._stats.evictions,
            size=len(cache_files),
            memory_usage=total_size,
        )

    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    async def _cleanup_old_files(self) -> None:
        """Cleanup old cache files."""
        cache_files = list(self.cache_dir.glob("*.cache"))

        if len(cache_files) <= self.max_size:
            return

        # Sort by access time (oldest first)
        cache_files.sort(key=lambda f: f.stat().st_atime)

        # Remove oldest files
        files_to_remove = len(cache_files) - self.max_size
        for cache_file in cache_files[:files_to_remove]:
            cache_file.unlink()
            self._stats.evictions += 1


class MultiLevelCache(CacheBackend[str, Any]):
    """Multi-level cache with L1 (memory) and L2 (file) backends."""

    def __init__(self, memory_cache: MemoryCache, file_cache: Optional[FileCache] = None):
        """Initialize multi-level cache.

        Args:
            memory_cache: L1 memory cache
            file_cache: Optional L2 file cache
        """
        self.l1_cache = memory_cache
        self.l2_cache = file_cache
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache hierarchy."""
        # Try L1 cache first
        value = await self.l1_cache.get(key)
        if value is not None:
            return value

        # Try L2 cache if available
        if self.l2_cache:
            value = await self.l2_cache.get(key)
            if value is not None:
                # Promote to L1 cache
                await self.l1_cache.set(key, value)
                return value

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in both cache levels."""
        # Set in L1 cache
        await self.l1_cache.set(key, value, ttl)

        # Set in L2 cache if available
        if self.l2_cache:
            await self.l2_cache.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        """Delete from both cache levels."""
        l1_deleted = await self.l1_cache.delete(key)
        l2_deleted = False

        if self.l2_cache:
            l2_deleted = await self.l2_cache.delete(key)

        return l1_deleted or l2_deleted

    async def clear(self) -> None:
        """Clear both cache levels."""
        await self.l1_cache.clear()
        if self.l2_cache:
            await self.l2_cache.clear()

    async def get_stats(self) -> dict[str, CacheStats]:
        """Get statistics from both cache levels."""
        stats = {"l1": await self.l1_cache.get_stats()}

        if self.l2_cache:
            stats["l2"] = await self.l2_cache.get_stats()

        return stats


class CacheManager:
    """Central cache manager for T-Developer."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize cache manager.

        Args:
            config: Cache configuration
        """
        self.config = config or {}
        self._caches: dict[str, CacheBackend] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize default caches
        self._setup_default_caches()

    def _setup_default_caches(self) -> None:
        """Setup default cache instances."""
        # Memory cache for frequently accessed data
        memory_cache = MemoryCache(
            max_size=self.config.get("memory_cache_size", 1000),
            default_ttl=self.config.get("memory_cache_ttl", 3600),
        )

        # File cache for persistent data
        cache_dir = Path(self.config.get("cache_dir", "/tmp/t-developer-cache"))
        file_cache = FileCache(
            cache_dir=cache_dir, max_size=self.config.get("file_cache_size", 5000)
        )

        # Multi-level cache
        multi_cache = MultiLevelCache(memory_cache, file_cache)

        # Register caches
        self._caches["memory"] = memory_cache
        self._caches["file"] = file_cache
        self._caches["default"] = multi_cache

    def get_cache(self, name: str = "default") -> CacheBackend:
        """Get cache by name."""
        if name not in self._caches:
            raise ValueError(f"Cache '{name}' not found")
        return self._caches[name]

    def register_cache(self, name: str, cache: CacheBackend) -> None:
        """Register a new cache."""
        self._caches[name] = cache

    async def get_all_stats(self) -> dict[str, Any]:
        """Get statistics from all caches."""
        stats = {}

        for name, cache in self._caches.items():
            try:
                cache_stats = await cache.get_stats()
                if isinstance(cache_stats, dict):
                    stats[name] = cache_stats
                else:
                    stats[name] = {
                        "hits": cache_stats.hits,
                        "misses": cache_stats.misses,
                        "hit_rate": cache_stats.hit_rate,
                        "size": cache_stats.size,
                        "memory_usage": cache_stats.memory_usage,
                    }
            except Exception as e:
                self.logger.error(f"Error getting stats for cache '{name}': {e}")
                stats[name] = {"error": str(e)}

        return stats


# Cache decorators
def cached(
    cache_name: str = "default", ttl: Optional[int] = None, key_func: Optional[Callable] = None
) -> Callable:
    """Decorator for caching function results.

    Args:
        cache_name: Name of cache to use
        ttl: Time to live for cached value
        key_func: Function to generate cache key
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get cache instance
            cache_manager = CacheManager()
            cache = cache_manager.get_cache(cache_name)

            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = _generate_cache_key(func, args, kwargs)

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Store in cache
            await cache.set(cache_key, result, ttl)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def cache_result(ttl: int = DEFAULT_TTL, cache_name: str = "default") -> Callable:
    """Simple cache decorator for function results."""
    return cached(cache_name=cache_name, ttl=ttl)


def _generate_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    """Generate cache key from function and arguments."""
    # Create key from function name and arguments
    key_parts = [func.__name__]

    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            # Use hash for complex objects
            key_parts.append(str(hash(str(arg))))

    # Add keyword arguments
    for key, value in sorted(kwargs.items()):
        if isinstance(value, (str, int, float, bool)):
            key_parts.append(f"{key}={value}")
        else:
            key_parts.append(f"{key}={hash(str(value))}")

    # Create final key
    cache_key = ":".join(key_parts)

    # Hash if too long
    if len(cache_key) > 250:
        cache_key = hashlib.md5(cache_key.encode()).hexdigest()

    return cache_key


@asynccontextmanager
async def cache_context(cache_name: str = "default"):
    """Context manager for cache operations."""
    cache_manager = CacheManager()
    cache = cache_manager.get_cache(cache_name)

    try:
        yield cache
    finally:
        # Cleanup or finalization if needed
        pass


# Usage examples and helper functions
async def warm_cache(cache: CacheBackend, data: dict[str, Any]) -> None:
    """Warm up cache with initial data."""
    for key, value in data.items():
        await cache.set(key, value)

    logger.info(f"Warmed cache with {len(data)} entries")


async def cache_health_check(cache_manager: CacheManager) -> dict[str, Any]:
    """Perform health check on all caches."""
    health_status = {
        "status": "healthy",
        "caches": {},
        "overall_hit_rate": 0.0,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        stats = await cache_manager.get_all_stats()

        total_hits = 0
        total_requests = 0

        for cache_name, cache_stats in stats.items():
            if "error" in cache_stats:
                health_status["caches"][cache_name] = {
                    "status": "error",
                    "error": cache_stats["error"],
                }
                health_status["status"] = "degraded"
                continue

            # Handle multi-level cache stats
            if isinstance(cache_stats, dict) and "l1" in cache_stats:
                l1_stats = cache_stats["l1"]
                hits = l1_stats.hits if hasattr(l1_stats, "hits") else l1_stats.get("hits", 0)
                misses = (
                    l1_stats.misses if hasattr(l1_stats, "misses") else l1_stats.get("misses", 0)
                )
            else:
                hits = (
                    cache_stats.hits if hasattr(cache_stats, "hits") else cache_stats.get("hits", 0)
                )
                misses = (
                    cache_stats.misses
                    if hasattr(cache_stats, "misses")
                    else cache_stats.get("misses", 0)
                )

            total_hits += hits
            total_requests += hits + misses

            hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0

            health_status["caches"][cache_name] = {
                "status": "healthy",
                "hit_rate": hit_rate,
                "size": cache_stats.size
                if hasattr(cache_stats, "size")
                else cache_stats.get("size", 0),
            }

        # Calculate overall hit rate
        if total_requests > 0:
            health_status["overall_hit_rate"] = total_hits / total_requests

    except Exception as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)

    return health_status
