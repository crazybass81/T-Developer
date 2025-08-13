"""
Cache Manager Module
Advanced caching system for search results and component data
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from collections import OrderedDict


class CacheManager:
    """Advanced cache management with TTL and intelligent invalidation"""

    def __init__(self):
        # Multi-level cache structure
        self.cache_layers = {
            "memory": MemoryCache(max_size=1000, default_ttl=300),  # 5 minutes
            "session": SessionCache(max_size=500, default_ttl=1800),  # 30 minutes
            "persistent": PersistentCache(max_size=100, default_ttl=3600),  # 1 hour
        }

        # Cache configuration
        self.config = {
            "enable_compression": True,
            "enable_analytics": True,
            "max_key_length": 250,
            "cleanup_interval": 300,  # seconds
            "hit_ratio_threshold": 0.7,
            "cache_warming_enabled": True,
        }

        # Cache analytics
        self.analytics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "invalidations": 0,
            "size_bytes": 0,
            "last_cleanup": datetime.now(),
        }

        # Key patterns for intelligent invalidation
        self.invalidation_patterns = {
            "query_pattern": r"query:",
            "component_pattern": r"component:",
            "search_pattern": r"search:",
            "recommendation_pattern": r"rec:",
        }

        # Background cleanup task
        self.cleanup_task = None
        self._start_background_cleanup()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with multi-level lookup"""

        # Generate cache key
        cache_key = self._generate_cache_key(key)

        # Try each cache layer in order
        for layer_name, cache_layer in self.cache_layers.items():
            try:
                value = await cache_layer.get(cache_key)
                if value is not None:
                    self.analytics["hits"] += 1

                    # Promote to higher cache layers if needed
                    if layer_name != "memory":
                        await self.cache_layers["memory"].set(cache_key, value, ttl=300)

                    # Decompress if needed
                    if self.config["enable_compression"]:
                        value = self._decompress_value(value)

                    return value

            except Exception as e:
                # Continue to next layer on error
                continue

        self.analytics["misses"] += 1
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in appropriate cache layers"""

        cache_key = self._generate_cache_key(key)

        # Compress value if needed
        if self.config["enable_compression"]:
            value = self._compress_value(value)

        # Determine appropriate cache layers based on key pattern
        target_layers = self._determine_cache_layers(cache_key, ttl)

        success = False
        for layer_name in target_layers:
            cache_layer = self.cache_layers[layer_name]
            layer_ttl = ttl or cache_layer.default_ttl

            try:
                await cache_layer.set(cache_key, value, layer_ttl)
                success = True
            except Exception as e:
                # Log error but continue with other layers
                continue

        if success:
            self.analytics["sets"] += 1
            self._update_size_analytics(cache_key, value)

        return success

    async def delete(self, key: str) -> bool:
        """Delete from all cache layers"""

        cache_key = self._generate_cache_key(key)
        success = False

        for cache_layer in self.cache_layers.values():
            try:
                if await cache_layer.delete(cache_key):
                    success = True
            except Exception:
                continue

        if success:
            self.analytics["invalidations"] += 1

        return success

    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries matching pattern"""

        total_cleared = 0

        for cache_layer in self.cache_layers.values():
            try:
                cleared = await cache_layer.clear(pattern)
                total_cleared += cleared
            except Exception:
                continue

        self.analytics["invalidations"] += total_cleared
        return total_cleared

    async def exists(self, key: str) -> bool:
        """Check if key exists in any cache layer"""

        cache_key = self._generate_cache_key(key)

        for cache_layer in self.cache_layers.values():
            try:
                if await cache_layer.exists(cache_key):
                    return True
            except Exception:
                continue

        return False

    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""

        # Create deterministic key from arguments
        key_parts = []

        # Add positional arguments
        for arg in args:
            if isinstance(arg, dict):
                # Sort dict for consistency
                sorted_items = sorted(arg.items())
                key_parts.append(json.dumps(sorted_items, sort_keys=True))
            else:
                key_parts.append(str(arg))

        # Add keyword arguments
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(json.dumps(sorted_kwargs, sort_keys=True))

        # Combine and hash
        key_string = "|".join(key_parts)

        # Truncate if too long
        if len(key_string) > self.config["max_key_length"]:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            key_string = key_string[:200] + ":" + key_hash

        return key_string

    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive cache status"""

        status = {
            "enabled": True,
            "analytics": self.analytics.copy(),
            "layers": {},
            "hit_ratio": self._calculate_hit_ratio(),
            "total_size_mb": self.analytics["size_bytes"] / (1024 * 1024),
            "last_cleanup": self.analytics["last_cleanup"].isoformat(),
        }

        # Get status for each layer
        for layer_name, cache_layer in self.cache_layers.items():
            layer_status = await cache_layer.get_status()
            status["layers"][layer_name] = layer_status

        return status

    async def warm_cache(self, warming_data: Dict[str, Any]) -> int:
        """Warm cache with frequently used data"""

        if not self.config["cache_warming_enabled"]:
            return 0

        warmed_count = 0

        # Warm with popular search results
        popular_queries = warming_data.get("popular_queries", [])
        for query_data in popular_queries:
            key = self.generate_key("search", query_data["query"])
            await self.set(key, query_data["results"], ttl=1800)  # 30 minutes
            warmed_count += 1

        # Warm with frequently accessed components
        popular_components = warming_data.get("popular_components", [])
        for component_data in popular_components:
            key = self.generate_key("component", component_data["id"])
            await self.set(key, component_data, ttl=3600)  # 1 hour
            warmed_count += 1

        # Warm with common recommendations
        common_recommendations = warming_data.get("common_recommendations", [])
        for rec_data in common_recommendations:
            key = self.generate_key("rec", rec_data["context"])
            await self.set(key, rec_data["recommendations"], ttl=1800)
            warmed_count += 1

        return warmed_count

    async def invalidate_pattern(self, pattern: str, reason: str = "manual") -> int:
        """Invalidate cache entries matching pattern"""

        invalidated = await self.clear(pattern)

        # Log invalidation reason
        self.analytics[f"invalidation_{reason}"] = (
            self.analytics.get(f"invalidation_{reason}", 0) + invalidated
        )

        return invalidated

    def _generate_cache_key(self, key: str) -> str:
        """Generate normalized cache key"""

        # Add prefix for namespacing
        prefixed_key = f"search_agent:{key}"

        # Normalize key
        normalized_key = prefixed_key.lower().strip()

        return normalized_key

    def _determine_cache_layers(self, key: str, ttl: Optional[int]) -> List[str]:
        """Determine which cache layers to use"""

        layers = ["memory"]  # Always cache in memory

        # Add session layer for medium-term storage
        if ttl is None or ttl >= 300:  # 5+ minutes
            layers.append("session")

        # Add persistent layer for long-term storage
        if ttl is None or ttl >= 1800:  # 30+ minutes
            layers.append("persistent")

        # Special patterns
        if "component:" in key:
            layers = ["memory", "persistent"]  # Skip session for components
        elif "search:" in key:
            layers = ["memory", "session"]  # No persistence for searches

        return layers

    def _compress_value(self, value: Any) -> Any:
        """Compress value for storage (simplified implementation)"""

        if not self.config["enable_compression"]:
            return value

        # Simple JSON compression for demonstration
        # In production, use proper compression like gzip
        if isinstance(value, (dict, list)):
            return {
                "__compressed": True,
                "__data": json.dumps(value, separators=(",", ":")),
            }

        return value

    def _decompress_value(self, value: Any) -> Any:
        """Decompress value from storage"""

        if isinstance(value, dict) and value.get("__compressed"):
            return json.loads(value["__data"])

        return value

    def _calculate_hit_ratio(self) -> float:
        """Calculate cache hit ratio"""

        total_requests = self.analytics["hits"] + self.analytics["misses"]
        if total_requests == 0:
            return 0.0

        return self.analytics["hits"] / total_requests

    def _update_size_analytics(self, key: str, value: Any):
        """Update size analytics"""

        # Estimate size (simplified)
        size_bytes = len(str(key)) + len(str(value))
        self.analytics["size_bytes"] += size_bytes

    def _start_background_cleanup(self):
        """Start background cleanup task"""

        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        """Background cleanup loop"""

        while True:
            try:
                await asyncio.sleep(self.config["cleanup_interval"])
                await self._perform_cleanup()
                self.analytics["last_cleanup"] = datetime.now()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error and continue
                await asyncio.sleep(60)  # Wait before retry

    async def _perform_cleanup(self):
        """Perform cache cleanup"""

        cleanup_tasks = []

        # Cleanup each cache layer
        for cache_layer in self.cache_layers.values():
            cleanup_tasks.append(cache_layer.cleanup_expired())

        await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        # Reset size analytics if hit ratio is too low
        if self._calculate_hit_ratio() < self.config["hit_ratio_threshold"]:
            await self.clear()  # Clear all caches
            self.analytics["size_bytes"] = 0

    def __del__(self):
        """Cleanup on destruction"""
        if self.cleanup_task:
            self.cleanup_task.cancel()


class MemoryCache:
    """In-memory LRU cache"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = OrderedDict()
        self.expiry_times = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""

        # Check if expired
        if key in self.expiry_times:
            if datetime.now() > self.expiry_times[key]:
                await self.delete(key)
                return None

        # Get value and move to end (LRU)
        if key in self.cache:
            value = self.cache[key]
            self.cache.move_to_end(key)
            return value

        return None

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in memory cache"""

        # Remove oldest items if at capacity
        while len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            await self.delete(oldest_key)

        # Set value and expiry
        self.cache[key] = value
        self.expiry_times[key] = datetime.now() + timedelta(seconds=ttl)

        return True

    async def delete(self, key: str) -> bool:
        """Delete from memory cache"""

        deleted = key in self.cache
        self.cache.pop(key, None)
        self.expiry_times.pop(key, None)

        return deleted

    async def exists(self, key: str) -> bool:
        """Check if key exists"""

        if key in self.cache:
            # Check expiry
            if key in self.expiry_times:
                if datetime.now() > self.expiry_times[key]:
                    await self.delete(key)
                    return False
            return True

        return False

    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries"""

        if pattern is None:
            cleared = len(self.cache)
            self.cache.clear()
            self.expiry_times.clear()
            return cleared

        # Pattern-based clearing
        keys_to_delete = [k for k in self.cache.keys() if pattern in k]
        for key in keys_to_delete:
            await self.delete(key)

        return len(keys_to_delete)

    async def cleanup_expired(self) -> int:
        """Remove expired entries"""

        now = datetime.now()
        expired_keys = [
            key for key, expiry_time in self.expiry_times.items() if now > expiry_time
        ]

        for key in expired_keys:
            await self.delete(key)

        return len(expired_keys)

    async def get_status(self) -> Dict[str, Any]:
        """Get cache status"""

        return {
            "type": "memory",
            "size": len(self.cache),
            "max_size": self.max_size,
            "utilization": len(self.cache) / self.max_size,
            "expired_entries": len(
                [k for k, exp in self.expiry_times.items() if datetime.now() > exp]
            ),
        }


class SessionCache:
    """Session-based cache with longer TTL"""

    def __init__(self, max_size: int = 500, default_ttl: int = 1800):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.access_times = {}
        self.expiry_times = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from session cache"""

        # Check if expired
        if key in self.expiry_times:
            if datetime.now() > self.expiry_times[key]:
                await self.delete(key)
                return None

        # Update access time and return value
        if key in self.cache:
            self.access_times[key] = datetime.now()
            return self.cache[key]

        return None

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in session cache"""

        # Remove least recently used items if at capacity
        while len(self.cache) >= self.max_size:
            lru_key = min(self.access_times.keys(), key=self.access_times.get)
            await self.delete(lru_key)

        # Set value, access time, and expiry
        now = datetime.now()
        self.cache[key] = value
        self.access_times[key] = now
        self.expiry_times[key] = now + timedelta(seconds=ttl)

        return True

    async def delete(self, key: str) -> bool:
        """Delete from session cache"""

        deleted = key in self.cache
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.expiry_times.pop(key, None)

        return deleted

    async def exists(self, key: str) -> bool:
        """Check if key exists"""

        if key in self.cache:
            # Check expiry
            if key in self.expiry_times:
                if datetime.now() > self.expiry_times[key]:
                    await self.delete(key)
                    return False
            return True

        return False

    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries"""

        if pattern is None:
            cleared = len(self.cache)
            self.cache.clear()
            self.access_times.clear()
            self.expiry_times.clear()
            return cleared

        # Pattern-based clearing
        keys_to_delete = [k for k in self.cache.keys() if pattern in k]
        for key in keys_to_delete:
            await self.delete(key)

        return len(keys_to_delete)

    async def cleanup_expired(self) -> int:
        """Remove expired entries"""

        now = datetime.now()
        expired_keys = [
            key for key, expiry_time in self.expiry_times.items() if now > expiry_time
        ]

        for key in expired_keys:
            await self.delete(key)

        return len(expired_keys)

    async def get_status(self) -> Dict[str, Any]:
        """Get cache status"""

        return {
            "type": "session",
            "size": len(self.cache),
            "max_size": self.max_size,
            "utilization": len(self.cache) / self.max_size,
            "expired_entries": len(
                [k for k, exp in self.expiry_times.items() if datetime.now() > exp]
            ),
        }


class PersistentCache:
    """Persistent cache for long-term storage"""

    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.metadata = {}  # Store TTL and other metadata

    async def get(self, key: str) -> Optional[Any]:
        """Get value from persistent cache"""

        if key not in self.cache:
            return None

        # Check expiry
        metadata = self.metadata.get(key, {})
        expiry_time = metadata.get("expiry_time")

        if expiry_time and datetime.now() > expiry_time:
            await self.delete(key)
            return None

        # Update last accessed time
        self.metadata[key]["last_accessed"] = datetime.now()

        return self.cache[key]

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in persistent cache"""

        # Remove oldest items if at capacity
        while len(self.cache) >= self.max_size:
            # Find least recently accessed
            oldest_key = min(
                self.metadata.keys(),
                key=lambda k: self.metadata[k].get("last_accessed", datetime.min),
            )
            await self.delete(oldest_key)

        # Set value and metadata
        now = datetime.now()
        self.cache[key] = value
        self.metadata[key] = {
            "created_time": now,
            "last_accessed": now,
            "expiry_time": now + timedelta(seconds=ttl),
            "ttl": ttl,
        }

        return True

    async def delete(self, key: str) -> bool:
        """Delete from persistent cache"""

        deleted = key in self.cache
        self.cache.pop(key, None)
        self.metadata.pop(key, None)

        return deleted

    async def exists(self, key: str) -> bool:
        """Check if key exists"""

        if key in self.cache:
            # Check expiry
            metadata = self.metadata.get(key, {})
            expiry_time = metadata.get("expiry_time")

            if expiry_time and datetime.now() > expiry_time:
                await self.delete(key)
                return False

            return True

        return False

    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries"""

        if pattern is None:
            cleared = len(self.cache)
            self.cache.clear()
            self.metadata.clear()
            return cleared

        # Pattern-based clearing
        keys_to_delete = [k for k in self.cache.keys() if pattern in k]
        for key in keys_to_delete:
            await self.delete(key)

        return len(keys_to_delete)

    async def cleanup_expired(self) -> int:
        """Remove expired entries"""

        now = datetime.now()
        expired_keys = [
            key
            for key, meta in self.metadata.items()
            if meta.get("expiry_time") and now > meta["expiry_time"]
        ]

        for key in expired_keys:
            await self.delete(key)

        return len(expired_keys)

    async def get_status(self) -> Dict[str, Any]:
        """Get cache status"""

        now = datetime.now()

        return {
            "type": "persistent",
            "size": len(self.cache),
            "max_size": self.max_size,
            "utilization": len(self.cache) / self.max_size,
            "expired_entries": len(
                [
                    k
                    for k, meta in self.metadata.items()
                    if meta.get("expiry_time") and now > meta["expiry_time"]
                ]
            ),
            "average_age_minutes": self._calculate_average_age(),
        }

    def _calculate_average_age(self) -> float:
        """Calculate average age of cached items"""

        if not self.metadata:
            return 0.0

        now = datetime.now()
        total_age = 0.0

        for meta in self.metadata.values():
            created_time = meta.get("created_time", now)
            age_seconds = (now - created_time).total_seconds()
            total_age += age_seconds

        average_age_seconds = total_age / len(self.metadata)
        return average_age_seconds / 60.0  # Convert to minutes
