"""
Performance Optimizer for T-Developer Pipeline
Handles caching, profiling, resource optimization and bottleneck identification
"""

import asyncio
import logging
import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import pickle
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for pipeline stages"""
    stage_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    cache_hit_rate: float
    throughput: float
    latency_p95: float
    errors_per_minute: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass 
class ResourceUsage:
    """System resource usage snapshot"""
    cpu_percent: float
    memory_percent: float
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
    open_files: int
    threads: int
    timestamp: datetime = field(default_factory=datetime.now)

class MemoryCache:
    """High-performance in-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = {}
        self.lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key not in self.cache:
                return None
                
            # Check TTL
            if time.time() - self.access_times[key] > self.ttl_seconds:
                del self.cache[key]
                del self.access_times[key]
                return None
                
            # Update access time
            self.access_times[key] = time.time()
            return self.cache[key]
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache"""
        with self.lock:
            # Evict oldest if at capacity
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
                
            self.cache[key] = value
            self.access_times[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": getattr(self, '_hit_count', 0) / getattr(self, '_access_count', 1),
                "ttl_seconds": self.ttl_seconds
            }

class PersistentCache:
    """Disk-based persistent cache for large objects"""
    
    def __init__(self, cache_dir: str = "/tmp/t_developer_cache", max_size_mb: int = 500):
        self.cache_dir = cache_dir
        self.max_size_mb = max_size_mb
        self.index_file = f"{cache_dir}/index.json"
        
        import os
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load existing index
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Dict]:
        """Load cache index from disk"""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_index(self) -> None:
        """Save cache index to disk"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2, default=str)
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from persistent cache"""
        if key not in self.index:
            return None
            
        entry = self.index[key]
        
        # Check TTL
        if datetime.now() > datetime.fromisoformat(entry['expires_at']):
            self.delete(key)
            return None
        
        try:
            file_path = f"{self.cache_dir}/{entry['filename']}"
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, pickle.PickleError):
            self.delete(key)
            return None
    
    def put(self, key: str, value: Any, ttl_hours: int = 24) -> None:
        """Put item in persistent cache"""
        # Clean up expired entries
        self._cleanup_expired()
        
        # Serialize object
        filename = f"cache_{hash(key)}_{int(time.time())}.pkl"
        file_path = f"{self.cache_dir}/{filename}"
        
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(value, f)
                
            # Update index
            self.index[key] = {
                'filename': filename,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
                'size_bytes': os.path.getsize(file_path)
            }
            
            self._save_index()
            
            # Check total cache size and evict if necessary
            self._evict_if_needed()
            
        except Exception as e:
            logger.error(f"Failed to cache item {key}: {e}")
    
    def delete(self, key: str) -> None:
        """Delete item from cache"""
        if key in self.index:
            entry = self.index[key]
            file_path = f"{self.cache_dir}/{entry['filename']}"
            
            try:
                import os
                os.remove(file_path)
            except FileNotFoundError:
                pass
                
            del self.index[key]
            self._save_index()
    
    def _cleanup_expired(self) -> None:
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        for key, entry in self.index.items():
            if now > datetime.fromisoformat(entry['expires_at']):
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
    
    def _evict_if_needed(self) -> None:
        """Evict oldest entries if cache size exceeds limit"""
        total_size = sum(entry['size_bytes'] for entry in self.index.values())
        max_size_bytes = self.max_size_mb * 1024 * 1024
        
        if total_size <= max_size_bytes:
            return
            
        # Sort by creation time and remove oldest
        entries_by_age = sorted(
            self.index.items(),
            key=lambda x: x[1]['created_at']
        )
        
        for key, entry in entries_by_age:
            self.delete(key)
            total_size -= entry['size_bytes']
            
            if total_size <= max_size_bytes:
                break

class PerformanceProfiler:
    """Real-time performance profiler for pipeline stages"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.resource_history: deque = deque(maxlen=window_size)
        self.bottlenecks: Dict[str, float] = {}
        
    def record_stage_metrics(self, stage_name: str, metrics: PerformanceMetrics) -> None:
        """Record performance metrics for a stage"""
        self.metrics_history[stage_name].append(metrics)
        
        # Update bottleneck analysis
        avg_time = sum(m.execution_time for m in self.metrics_history[stage_name]) / len(self.metrics_history[stage_name])
        self.bottlenecks[stage_name] = avg_time
    
    def record_resource_usage(self) -> None:
        """Record current system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            net_io = psutil.net_io_counters()
            
            resource_usage = ResourceUsage(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_io={
                    'read_bytes_per_sec': disk_io.read_bytes if disk_io else 0,
                    'write_bytes_per_sec': disk_io.write_bytes if disk_io else 0
                },
                network_io={
                    'bytes_sent_per_sec': net_io.bytes_sent if net_io else 0,
                    'bytes_recv_per_sec': net_io.bytes_recv if net_io else 0
                },
                open_files=len(psutil.Process().open_files()),
                threads=psutil.Process().num_threads()
            )
            
            self.resource_history.append(resource_usage)
            
        except Exception as e:
            logger.warning(f"Failed to record resource usage: {e}")
    
    def get_bottlenecks(self, threshold_percentile: float = 0.9) -> List[Tuple[str, float]]:
        """Identify performance bottlenecks"""
        if not self.bottlenecks:
            return []
        
        # Calculate threshold
        times = list(self.bottlenecks.values())
        times.sort()
        threshold = times[int(len(times) * threshold_percentile)] if times else 0
        
        # Find stages above threshold
        bottlenecks = [
            (stage, time) for stage, time in self.bottlenecks.items()
            if time >= threshold
        ]
        
        return sorted(bottlenecks, key=lambda x: x[1], reverse=True)
    
    def get_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        # Analyze bottlenecks
        bottlenecks = self.get_bottlenecks()
        if bottlenecks:
            slowest_stage, time = bottlenecks[0]
            recommendations.append(f"Optimize {slowest_stage} - slowest stage ({time:.2f}s avg)")
        
        # Analyze resource usage
        if self.resource_history:
            avg_cpu = sum(r.cpu_percent for r in self.resource_history) / len(self.resource_history)
            avg_memory = sum(r.memory_percent for r in self.resource_history) / len(self.resource_history)
            
            if avg_cpu > 80:
                recommendations.append("High CPU usage detected - consider parallel processing")
            
            if avg_memory > 80:
                recommendations.append("High memory usage - implement memory optimization")
            
            # Check for resource spikes
            cpu_spikes = [r for r in self.resource_history if r.cpu_percent > 90]
            if len(cpu_spikes) > len(self.resource_history) * 0.1:
                recommendations.append("Frequent CPU spikes - review algorithm complexity")
        
        return recommendations

class PerformanceOptimizer:
    """Main performance optimization coordinator"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {
            'enable_caching': True,
            'cache_ttl_hours': 24,
            'max_cache_size_mb': 500,
            'enable_profiling': True,
            'optimization_interval': 60,  # seconds
            'parallel_execution_threshold': 2.0,  # seconds
            'memory_optimization_threshold': 80  # percent
        }
        
        # Initialize caches
        self.memory_cache = MemoryCache() if self.config['enable_caching'] else None
        self.persistent_cache = PersistentCache(max_size_mb=self.config['max_cache_size_mb']) if self.config['enable_caching'] else None
        
        # Initialize profiler
        self.profiler = PerformanceProfiler() if self.config['enable_profiling'] else None
        
        # Optimization state
        self.optimization_history: List[Dict[str, Any]] = []
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=2)
        
        # Start background monitoring
        self.monitoring_task = None
        if self.profiler:
            self.monitoring_task = asyncio.create_task(self._background_monitoring())
    
    async def optimize_stage_execution(
        self, 
        stage_name: str, 
        execution_func: Callable, 
        input_data: Dict[str, Any]
    ) -> Tuple[Any, PerformanceMetrics]:
        """Optimize execution of a pipeline stage"""
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(stage_name, input_data)
            if self.memory_cache:
                cached_result = self.memory_cache.get(cache_key)
                if cached_result is not None:
                    logger.info(f"Cache hit for {stage_name}")
                    
                    metrics = PerformanceMetrics(
                        stage_name=stage_name,
                        execution_time=0.001,  # Cache access time
                        memory_usage=0,
                        cpu_usage=0,
                        cache_hit_rate=1.0,
                        throughput=1000.0,  # Very high for cached results
                        latency_p95=0.001,
                        errors_per_minute=0
                    )
                    
                    return cached_result, metrics
            
            # Check persistent cache
            if self.persistent_cache:
                cached_result = self.persistent_cache.get(cache_key)
                if cached_result is not None:
                    logger.info(f"Persistent cache hit for {stage_name}")
                    
                    # Also store in memory cache for faster access
                    if self.memory_cache:
                        self.memory_cache.put(cache_key, cached_result)
                    
                    metrics = PerformanceMetrics(
                        stage_name=stage_name,
                        execution_time=0.01,  # Disk cache access time
                        memory_usage=0,
                        cpu_usage=0,
                        cache_hit_rate=1.0,
                        throughput=100.0,
                        latency_p95=0.01,
                        errors_per_minute=0
                    )
                    
                    return cached_result, metrics
            
            # Determine execution strategy
            execution_strategy = await self._determine_execution_strategy(stage_name, input_data)
            
            # Execute with chosen strategy
            if execution_strategy == 'parallel':
                result = await self._execute_parallel(execution_func, input_data)
            elif execution_strategy == 'async':
                result = await self._execute_async(execution_func, input_data)
            else:
                result = await self._execute_sync(execution_func, input_data)
            
            # Calculate metrics
            execution_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_usage = end_memory - start_memory
            
            metrics = PerformanceMetrics(
                stage_name=stage_name,
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=psutil.cpu_percent(),
                cache_hit_rate=0.0,  # No cache hit
                throughput=1.0 / execution_time if execution_time > 0 else 0,
                latency_p95=execution_time,
                errors_per_minute=0
            )
            
            # Cache result if beneficial
            if execution_time > 1.0:  # Only cache expensive operations
                if self.memory_cache:
                    self.memory_cache.put(cache_key, result)
                if self.persistent_cache:
                    self.persistent_cache.put(cache_key, result, ttl_hours=self.config['cache_ttl_hours'])
            
            # Record metrics
            if self.profiler:
                self.profiler.record_stage_metrics(stage_name, metrics)
            
            return result, metrics
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            metrics = PerformanceMetrics(
                stage_name=stage_name,
                execution_time=execution_time,
                memory_usage=0,
                cpu_usage=0,
                cache_hit_rate=0.0,
                throughput=0,
                latency_p95=execution_time,
                errors_per_minute=1.0
            )
            
            if self.profiler:
                self.profiler.record_stage_metrics(stage_name, metrics)
            
            raise e
    
    async def _determine_execution_strategy(self, stage_name: str, input_data: Dict[str, Any]) -> str:
        """Determine optimal execution strategy for a stage"""
        
        # Check historical performance
        if self.profiler and stage_name in self.profiler.metrics_history:
            recent_metrics = list(self.profiler.metrics_history[stage_name])[-10:]
            avg_time = sum(m.execution_time for m in recent_metrics) / len(recent_metrics)
            
            # Use parallel execution for slow stages
            if avg_time > self.config['parallel_execution_threshold']:
                return 'parallel'
        
        # Check input data size
        data_size = len(str(input_data))
        if data_size > 10000:  # Large input
            return 'async'
        
        return 'sync'
    
    async def _execute_parallel(self, func: Callable, input_data: Dict[str, Any]) -> Any:
        """Execute function in parallel (for CPU-bound tasks)"""
        
        loop = asyncio.get_event_loop()
        
        # Split work if possible
        if hasattr(func, '__self__') and hasattr(func.__self__, 'process_parallel'):
            return await loop.run_in_executor(
                self.process_pool,
                func.__self__.process_parallel,
                input_data
            )
        else:
            return await loop.run_in_executor(
                self.thread_pool,
                func,
                input_data
            )
    
    async def _execute_async(self, func: Callable, input_data: Dict[str, Any]) -> Any:
        """Execute function asynchronously"""
        
        if asyncio.iscoroutinefunction(func):
            return await func(input_data)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self.thread_pool, func, input_data)
    
    async def _execute_sync(self, func: Callable, input_data: Dict[str, Any]) -> Any:
        """Execute function synchronously"""
        
        if asyncio.iscoroutinefunction(func):
            return await func(input_data)
        else:
            return func(input_data)
    
    def _generate_cache_key(self, stage_name: str, input_data: Dict[str, Any]) -> str:
        """Generate cache key for stage execution"""
        
        import hashlib
        import json
        
        # Extract key components for cache key
        cache_components = {
            'stage': stage_name,
            'user_input': input_data.get('user_input', '')[:500],  # Limit size
            'framework': input_data.get('framework', ''),
            'project_type': input_data.get('project_type', ''),
            'version': '1.0'  # Cache version
        }
        
        cache_string = json.dumps(cache_components, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()[:16]
    
    async def _background_monitoring(self) -> None:
        """Background task for continuous performance monitoring"""
        
        while True:
            try:
                if self.profiler:
                    self.profiler.record_resource_usage()
                
                # Run optimization if needed
                await self._run_periodic_optimization()
                
                await asyncio.sleep(self.config['optimization_interval'])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _run_periodic_optimization(self) -> None:
        """Run periodic optimization based on collected metrics"""
        
        if not self.profiler or not self.profiler.resource_history:
            return
        
        # Check if optimization is needed
        recent_resources = list(self.profiler.resource_history)[-10:]
        avg_memory = sum(r.memory_percent for r in recent_resources) / len(recent_resources)
        
        optimization_actions = []
        
        # Memory optimization
        if avg_memory > self.config['memory_optimization_threshold']:
            if self.memory_cache:
                old_size = len(self.memory_cache.cache)
                self.memory_cache.clear()
                optimization_actions.append(f"Cleared memory cache ({old_size} entries)")
        
        # Cache optimization
        if self.persistent_cache:
            self.persistent_cache._cleanup_expired()
            optimization_actions.append("Cleaned up expired persistent cache entries")
        
        # Log optimizations
        if optimization_actions:
            logger.info(f"Performed optimizations: {'; '.join(optimization_actions)}")
            
            self.optimization_history.append({
                'timestamp': datetime.now().isoformat(),
                'actions': optimization_actions,
                'memory_before': avg_memory
            })
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'cache_stats': {},
            'resource_usage': {},
            'bottlenecks': [],
            'recommendations': [],
            'optimization_history': self.optimization_history[-10:]  # Last 10 optimizations
        }
        
        # Cache statistics
        if self.memory_cache:
            report['cache_stats']['memory_cache'] = self.memory_cache.stats()
        
        # Resource usage
        if self.profiler and self.profiler.resource_history:
            recent_resources = list(self.profiler.resource_history)[-10:]
            report['resource_usage'] = {
                'avg_cpu_percent': sum(r.cpu_percent for r in recent_resources) / len(recent_resources),
                'avg_memory_percent': sum(r.memory_percent for r in recent_resources) / len(recent_resources),
                'avg_threads': sum(r.threads for r in recent_resources) / len(recent_resources)
            }
        
        # Bottlenecks and recommendations
        if self.profiler:
            report['bottlenecks'] = self.profiler.get_bottlenecks()
            report['recommendations'] = self.profiler.get_recommendations()
        
        return report
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        
        try:
            if self.monitoring_task:
                self.monitoring_task.cancel()
                await self.monitoring_task
        except asyncio.CancelledError:
            pass
        
        # Shutdown executors
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
        # Clear caches
        if self.memory_cache:
            self.memory_cache.clear()
        
        logger.info("PerformanceOptimizer cleanup completed")