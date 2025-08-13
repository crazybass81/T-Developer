"""
Monitoring and Metrics System
Tracks performance, health, and usage metrics
"""
import asyncio
import logging
import statistics
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from src.services.aws_clients import get_cloudwatch_client

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class MetricUnit(Enum):
    """Metric units"""

    COUNT = "Count"
    BYTES = "Bytes"
    SECONDS = "Seconds"
    MILLISECONDS = "Milliseconds"
    PERCENT = "Percent"
    NONE = "None"


@dataclass
class Metric:
    """Individual metric data"""

    name: str
    type: MetricType
    unit: MetricUnit = MetricUnit.NONE
    value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)

    def to_cloudwatch_format(self) -> Dict[str, Any]:
        """Convert to CloudWatch metric format"""
        return {
            "MetricName": self.name,
            "Value": self.value,
            "Unit": self.unit.value,
            "Timestamp": self.timestamp,
            "Dimensions": [{"Name": k, "Value": v} for k, v in self.tags.items()],
        }


@dataclass
class HealthCheck:
    """Health check result"""

    name: str
    status: str  # healthy, unhealthy, degraded
    message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)

    def is_healthy(self) -> bool:
        """Check if component is healthy"""
        return self.status == "healthy"


class MetricsCollector:
    """Collects and aggregates metrics"""

    def __init__(
        self,
        namespace: str = "T-Developer",
        buffer_size: int = 1000,
        flush_interval: int = 60,
    ):
        self.namespace = namespace
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval

        # Metrics storage
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, deque] = {}
        self._timers: Dict[str, List[float]] = {}

        # Metrics buffer for batch sending
        self._buffer: deque = deque(maxlen=buffer_size)

        # CloudWatch client
        self._cloudwatch = None
        self._last_flush = datetime.utcnow()

    async def initialize(self, use_cloudwatch: bool = False):
        """Initialize metrics collector"""
        if use_cloudwatch:
            self._cloudwatch = get_cloudwatch_client()

    def increment_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None) -> None:
        """Increment a counter metric"""
        key = self._make_key(name, tags)
        if key not in self._counters:
            self._counters[key] = 0
        self._counters[key] += value

        # Add to buffer
        self._add_metric(
            Metric(
                name=name,
                type=MetricType.COUNTER,
                unit=MetricUnit.COUNT,
                value=value,
                tags=tags or {},
            )
        )

    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Set a gauge metric"""
        key = self._make_key(name, tags)
        self._gauges[key] = value

        # Add to buffer
        self._add_metric(
            Metric(
                name=name,
                type=MetricType.GAUGE,
                unit=MetricUnit.NONE,
                value=value,
                tags=tags or {},
            )
        )

    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Record a histogram value"""
        key = self._make_key(name, tags)
        if key not in self._histograms:
            self._histograms[key] = deque(maxlen=1000)
        self._histograms[key].append(value)

        # Add to buffer
        self._add_metric(Metric(name=name, type=MetricType.HISTOGRAM, value=value, tags=tags or {}))

    def record_timer(self, name: str, duration_ms: float, tags: Dict[str, str] = None) -> None:
        """Record a timer duration"""
        key = self._make_key(name, tags)
        if key not in self._timers:
            self._timers[key] = []
        self._timers[key].append(duration_ms)

        # Add to buffer
        self._add_metric(
            Metric(
                name=name,
                type=MetricType.TIMER,
                unit=MetricUnit.MILLISECONDS,
                value=duration_ms,
                tags=tags or {},
            )
        )

    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create unique key for metric"""
        if not tags:
            return name

        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}:{tag_str}"

    def _add_metric(self, metric: Metric) -> None:
        """Add metric to buffer"""
        self._buffer.append(metric)

        # Check if we should flush
        if len(self._buffer) >= self.buffer_size:
            asyncio.create_task(self.flush())
        elif (datetime.utcnow() - self._last_flush).total_seconds() > self.flush_interval:
            asyncio.create_task(self.flush())

    async def flush(self) -> int:
        """Flush metrics to CloudWatch"""
        if not self._buffer:
            return 0

        metrics_to_send = list(self._buffer)
        self._buffer.clear()
        self._last_flush = datetime.utcnow()

        if self._cloudwatch:
            # Send to CloudWatch in batches
            batch_size = 20
            for i in range(0, len(metrics_to_send), batch_size):
                batch = metrics_to_send[i : i + batch_size]

                for metric in batch:
                    self._cloudwatch.put_metric(
                        namespace=self.namespace,
                        metric_name=metric.name,
                        value=metric.value,
                        unit=metric.unit.value,
                        dimensions=metric.tags,
                    )

        return len(metrics_to_send)

    def get_counter(self, name: str, tags: Dict[str, str] = None) -> float:
        """Get counter value"""
        key = self._make_key(name, tags)
        return self._counters.get(key, 0)

    def get_gauge(self, name: str, tags: Dict[str, str] = None) -> float:
        """Get gauge value"""
        key = self._make_key(name, tags)
        return self._gauges.get(key, 0)

    def get_histogram_stats(self, name: str, tags: Dict[str, str] = None) -> Dict[str, float]:
        """Get histogram statistics"""
        key = self._make_key(name, tags)
        values = list(self._histograms.get(key, []))

        if not values:
            return {"count": 0}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stddev": statistics.stdev(values) if len(values) > 1 else 0,
        }

    def get_timer_stats(self, name: str, tags: Dict[str, str] = None) -> Dict[str, float]:
        """Get timer statistics"""
        key = self._make_key(name, tags)
        durations = self._timers.get(key, [])

        if not durations:
            return {"count": 0}

        return {
            "count": len(durations),
            "min": min(durations),
            "max": max(durations),
            "mean": statistics.mean(durations),
            "median": statistics.median(durations),
            "p95": self._percentile(durations, 0.95),
            "p99": self._percentile(durations, 0.99),
        }

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histogram_stats": {
                key: self.get_histogram_stats(key.split(":")[0], self._parse_tags(key))
                for key in self._histograms.keys()
            },
            "timer_stats": {
                key: self.get_timer_stats(key.split(":")[0], self._parse_tags(key))
                for key in self._timers.keys()
            },
        }

    def _parse_tags(self, key: str) -> Dict[str, str]:
        """Parse tags from key"""
        if ":" not in key:
            return {}

        tag_str = key.split(":", 1)[1]
        tags = {}
        for pair in tag_str.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                tags[k] = v

        return tags

    def reset(self) -> None:
        """Reset all metrics"""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._timers.clear()
        self._buffer.clear()


class HealthMonitor:
    """Monitors system health"""

    def __init__(self):
        self._health_checks: Dict[str, Callable] = {}
        self._last_results: Dict[str, HealthCheck] = {}
        self._check_interval = 30  # seconds
        self._monitoring = False

    def register_health_check(self, name: str, check_func: Callable) -> None:
        """Register a health check"""
        self._health_checks[name] = check_func
        logger.info(f"Registered health check: {name}")

    async def check_health(self, name: Optional[str] = None) -> Dict[str, HealthCheck]:
        """Run health checks"""
        results = {}

        if name:
            # Check specific component
            if name in self._health_checks:
                try:
                    result = await self._health_checks[name]()
                    if not isinstance(result, HealthCheck):
                        result = HealthCheck(name=name, status="healthy" if result else "unhealthy")
                    results[name] = result
                except Exception as e:
                    results[name] = HealthCheck(name=name, status="unhealthy", message=str(e))
        else:
            # Check all components
            for check_name, check_func in self._health_checks.items():
                try:
                    result = await check_func()
                    if not isinstance(result, HealthCheck):
                        result = HealthCheck(
                            name=check_name, status="healthy" if result else "unhealthy"
                        )
                    results[check_name] = result
                except Exception as e:
                    results[check_name] = HealthCheck(
                        name=check_name, status="unhealthy", message=str(e)
                    )

        # Update last results
        self._last_results.update(results)

        return results

    async def start_monitoring(self) -> None:
        """Start continuous health monitoring"""
        if self._monitoring:
            return

        self._monitoring = True
        logger.info("Started health monitoring")

        while self._monitoring:
            try:
                await self.check_health()
                await asyncio.sleep(self._check_interval)
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(self._check_interval)

    def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        self._monitoring = False
        logger.info("Stopped health monitoring")

    def get_overall_health(self) -> str:
        """Get overall system health"""
        if not self._last_results:
            return "unknown"

        unhealthy_count = sum(1 for check in self._last_results.values() if not check.is_healthy())

        if unhealthy_count == 0:
            return "healthy"
        elif unhealthy_count < len(self._last_results) / 2:
            return "degraded"
        else:
            return "unhealthy"

    def get_health_report(self) -> Dict[str, Any]:
        """Get detailed health report"""
        return {
            "overall_status": self.get_overall_health(),
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                name: {
                    "status": check.status,
                    "message": check.message,
                    "timestamp": check.timestamp.isoformat(),
                    "details": check.details,
                }
                for name, check in self._last_results.items()
            },
        }


class PerformanceTracker:
    """Tracks performance metrics"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self._active_timers: Dict[str, float] = {}

    def start_timer(self, name: str, tags: Dict[str, str] = None) -> str:
        """Start a performance timer"""
        timer_id = f"{name}:{id(tags) if tags else 'notags'}:{time.time()}"
        self._active_timers[timer_id] = time.time()
        return timer_id

    def stop_timer(self, timer_id: str) -> float:
        """Stop a timer and record duration"""
        if timer_id not in self._active_timers:
            logger.warning(f"Timer {timer_id} not found")
            return 0

        start_time = self._active_timers.pop(timer_id)
        duration_ms = (time.time() - start_time) * 1000

        # Extract name and tags from timer_id
        parts = timer_id.split(":", 2)
        name = parts[0]

        self.metrics.record_timer(name, duration_ms)

        return duration_ms

    def track_memory_usage(self) -> float:
        """Track current memory usage"""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024

        self.metrics.set_gauge("memory_usage_mb", memory_mb)

        return memory_mb

    def track_cpu_usage(self) -> float:
        """Track current CPU usage"""
        import psutil

        cpu_percent = psutil.cpu_percent(interval=0.1)

        self.metrics.set_gauge("cpu_usage_percent", cpu_percent)

        return cpu_percent

    async def track_agent_performance(
        self, agent_name: str, execution_time_ms: float, success: bool
    ) -> None:
        """Track agent performance metrics"""
        tags = {"agent": agent_name}

        # Record execution time
        self.metrics.record_timer(f"agent_execution_time", execution_time_ms, tags)

        # Track success/failure
        if success:
            self.metrics.increment_counter("agent_success", tags=tags)
        else:
            self.metrics.increment_counter("agent_failure", tags=tags)

        # Track throughput
        self.metrics.increment_counter("agent_requests", tags=tags)


# Singleton instances
_metrics_collector: Optional[MetricsCollector] = None
_health_monitor: Optional[HealthMonitor] = None
_performance_tracker: Optional[PerformanceTracker] = None


def get_metrics_collector() -> MetricsCollector:
    """Get singleton metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_health_monitor() -> HealthMonitor:
    """Get singleton health monitor"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


def get_performance_tracker() -> PerformanceTracker:
    """Get singleton performance tracker"""
    global _performance_tracker
    if _performance_tracker is None:
        _performance_tracker = PerformanceTracker(get_metrics_collector())
    return _performance_tracker


# Export classes and functions
__all__ = [
    "MetricType",
    "MetricUnit",
    "Metric",
    "HealthCheck",
    "MetricsCollector",
    "HealthMonitor",
    "PerformanceTracker",
    "get_metrics_collector",
    "get_health_monitor",
    "get_performance_tracker",
]
