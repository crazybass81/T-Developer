"""🧬 T-Developer Metrics <6.5KB"""
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Metric:
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str]
    unit: str = "count"


@dataclass
class Summary:
    count: int
    avg: float
    min_val: float
    max_val: float
    last_ts: float


class MetricsCollector:
    def __init__(self, max_metrics: int = 500):
        self.metrics = deque(maxlen=max_metrics)
        self.aggregates: Dict[str, Summary] = {}
        self.listeners: List[Callable] = []
        self._lock = threading.Lock()

        self.executions = 0
        self.total_time = 0.0
        self.memory_samples = deque(maxlen=50)
        self.errors = 0
        self.last_errors = deque(maxlen=5)

    def record_metric(
        self, name: str, value: float, tags: Dict[str, str] = None, unit: str = "count"
    ):
        metric = Metric(name, value, time.time(), tags or {}, unit)

        with self._lock:
            self.metrics.append(metric)
            self._update_agg(metric)
            self._notify(metric)

    def record_execution(
        self, agent_id: str, duration_ms: float, success: bool = True, memory_kb: int = 0
    ):
        self.executions += 1
        self.total_time += duration_ms

        tags = {"agent_id": agent_id, "success": str(success)}
        self.record_metric("exec_time", duration_ms, tags, "ms")

        if memory_kb > 0:
            self.record_metric("memory", memory_kb, tags, "kb")
            self.memory_samples.append(memory_kb)

        if not success:
            self.errors += 1
            self.record_metric("errors", 1, tags)

    def record_error(self, agent_id: str, error_type: str, error_msg: str):
        error_info = {
            "agent_id": agent_id,
            "type": error_type,
            "msg": error_msg[:50],
            "ts": time.time(),
        }

        self.last_errors.append(error_info)
        self.record_metric("error_count", 1, {"agent": agent_id, "type": error_type})

    def get_metrics(self, filter_name: str = None, last_n: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            metrics = list(self.metrics)[-last_n:]
            if filter_name:
                metrics = [m for m in metrics if filter_name in m.name]
            return [asdict(m) for m in metrics]

    def get_performance_stats(self) -> Dict[str, Any]:
        avg_time = self.total_time / max(1, self.executions)
        avg_memory = (
            sum(self.memory_samples) / max(1, len(self.memory_samples))
            if self.memory_samples
            else 0
        )
        error_rate = self.errors / max(1, self.executions)

        return {
            "executions": self.executions,
            "avg_time_ms": avg_time,
            "avg_memory_kb": avg_memory,
            "error_rate": error_rate,
            "recent_errors": list(self.last_errors)[-2:],
            "total_metrics": len(self.metrics),
        }

    def get_dashboard(self) -> Dict[str, Any]:
        metrics = self.get_metrics(last_n=30)
        perf = self.get_performance_stats()

        # Simple trend calculation
        recent_times = [m["value"] for m in metrics if m["name"] == "exec_time"][-5:]
        trend = "stable"
        if len(recent_times) >= 3:
            avg_recent = sum(recent_times) / len(recent_times)
            if avg_recent > 1000:
                trend = "slow"
            elif avg_recent < 100:
                trend = "fast"

        return {
            "timestamp": time.time(),
            "performance": perf,
            "trend": trend,
            "health_score": self._health_score(),
        }

    def export_cloudwatch(self) -> List[Dict[str, Any]]:
        cw_metrics = []
        for metric in list(self.metrics)[-30:]:
            cw_metrics.append(
                {
                    "MetricName": metric.name,
                    "Value": metric.value,
                    "Unit": metric.unit.title(),
                    "Timestamp": metric.timestamp,
                    "Dimensions": [{"Name": k, "Value": v} for k, v in metric.tags.items()],
                }
            )
        return cw_metrics

    def _update_agg(self, metric: Metric):
        name = metric.name
        if name not in self.aggregates:
            self.aggregates[name] = Summary(
                1, metric.value, metric.value, metric.value, metric.timestamp
            )
        else:
            agg = self.aggregates[name]
            agg.count += 1
            agg.avg = ((agg.avg * (agg.count - 1)) + metric.value) / agg.count
            agg.min_val = min(agg.min_val, metric.value)
            agg.max_val = max(agg.max_val, metric.value)
            agg.last_ts = metric.timestamp

    def _notify(self, metric: Metric):
        for callback in self.listeners:
            try:
                callback(metric)
            except:
                pass

    def _health_score(self) -> float:
        score = 100.0
        error_rate = self.errors / max(1, self.executions)
        score -= min(30, error_rate * 100)

        if self.executions > 0:
            avg_time = self.total_time / self.executions
            if avg_time > 1000:
                score -= min(20, (avg_time - 1000) / 100)

        return max(0.0, min(100.0, score))


# Global instance
_collector = None


def get_collector() -> MetricsCollector:
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector


def record_execution(agent_id: str, duration_ms: float, success: bool = True, memory_kb: int = 0):
    get_collector().record_execution(agent_id, duration_ms, success, memory_kb)


def record_error(agent_id: str, error_type: str, error_msg: str):
    get_collector().record_error(agent_id, error_type, error_msg)


def get_dashboard() -> Dict[str, Any]:
    return get_collector().get_dashboard()
