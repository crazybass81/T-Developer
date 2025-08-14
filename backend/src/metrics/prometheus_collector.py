"""PrometheusCollector - Day 41
Prometheus metrics collection infrastructure - Size: ~6.5KB"""
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class MetricType(Enum):
    """Metric types"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class PrometheusCollector:
    """Collect metrics for evolution fitness evaluation - Size optimized to 6.5KB"""

    def __init__(self):
        self.metrics = {}
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.summaries = {}
        self.labels = {}
        self.collection_interval = 10  # seconds
        self.retention_period = 86400  # 24 hours in seconds

    def register_metric(
        self, name: str, metric_type: MetricType, description: str = "", labels: List[str] = None
    ) -> bool:
        """Register a new metric"""
        if name in self.metrics:
            return False

        self.metrics[name] = {
            "type": metric_type,
            "description": description,
            "labels": labels or [],
            "created_at": datetime.now().isoformat(),
        }

        # Initialize based on type
        if metric_type == MetricType.COUNTER:
            self.counters[name] = 0
        elif metric_type == MetricType.GAUGE:
            self.gauges[name] = 0
        elif metric_type == MetricType.HISTOGRAM:
            self.histograms[name] = []
        elif metric_type == MetricType.SUMMARY:
            self.summaries[name] = []

        return True

    def increment_counter(
        self, name: str, value: float = 1.0, labels: Dict[str, str] = None
    ) -> bool:
        """Increment a counter metric"""
        if name not in self.counters:
            return False

        label_key = self._create_label_key(name, labels)
        if label_key not in self.counters:
            self.counters[label_key] = 0

        self.counters[label_key] += value
        self._record_timestamp(name, label_key)
        return True

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> bool:
        """Set a gauge metric"""
        if name not in self.metrics or self.metrics[name]["type"] != MetricType.GAUGE:
            self.register_metric(name, MetricType.GAUGE)

        label_key = self._create_label_key(name, labels)
        self.gauges[label_key] = value
        self._record_timestamp(name, label_key)
        return True

    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None) -> bool:
        """Record a histogram observation"""
        if name not in self.metrics or self.metrics[name]["type"] != MetricType.HISTOGRAM:
            self.register_metric(name, MetricType.HISTOGRAM)

        label_key = self._create_label_key(name, labels)
        if label_key not in self.histograms:
            self.histograms[label_key] = []

        self.histograms[label_key].append({"value": value, "timestamp": time.time()})

        # Maintain size limit
        self._cleanup_old_observations(self.histograms[label_key])
        return True

    def observe_summary(self, name: str, value: float, labels: Dict[str, str] = None) -> bool:
        """Record a summary observation"""
        if name not in self.metrics or self.metrics[name]["type"] != MetricType.SUMMARY:
            self.register_metric(name, MetricType.SUMMARY)

        label_key = self._create_label_key(name, labels)
        if label_key not in self.summaries:
            self.summaries[label_key] = []

        self.summaries[label_key].append({"value": value, "timestamp": time.time()})

        # Maintain size limit
        self._cleanup_old_observations(self.summaries[label_key])
        return True

    def collect_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Collect metrics for a specific agent"""
        metrics = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "performance": {},
            "resource_usage": {},
            "quality": {},
        }

        # Performance metrics
        metrics["performance"]["response_time"] = self._get_metric_value(
            f"agent_{agent_id}_response_time", MetricType.HISTOGRAM
        )
        metrics["performance"]["throughput"] = self._get_metric_value(
            f"agent_{agent_id}_throughput", MetricType.GAUGE
        )
        metrics["performance"]["error_rate"] = self._get_metric_value(
            f"agent_{agent_id}_errors", MetricType.COUNTER
        )

        # Resource usage
        metrics["resource_usage"]["memory"] = self._get_metric_value(
            f"agent_{agent_id}_memory", MetricType.GAUGE
        )
        metrics["resource_usage"]["cpu"] = self._get_metric_value(
            f"agent_{agent_id}_cpu", MetricType.GAUGE
        )

        # Quality metrics
        metrics["quality"]["test_coverage"] = self._get_metric_value(
            f"agent_{agent_id}_coverage", MetricType.GAUGE
        )
        metrics["quality"]["code_complexity"] = self._get_metric_value(
            f"agent_{agent_id}_complexity", MetricType.GAUGE
        )

        return metrics

    def get_aggregated_metrics(
        self, metric_name: str, aggregation: str = "avg", time_window: int = 3600
    ) -> float:
        """Get aggregated metric value over time window"""
        if metric_name in self.histograms:
            values = self._get_recent_values(self.histograms[metric_name], time_window)
        elif metric_name in self.summaries:
            values = self._get_recent_values(self.summaries[metric_name], time_window)
        else:
            return self._get_simple_metric_value(metric_name)

        if not values:
            return 0.0

        if aggregation == "avg":
            return sum(values) / len(values)
        elif aggregation == "min":
            return min(values)
        elif aggregation == "max":
            return max(values)
        elif aggregation == "sum":
            return sum(values)
        elif aggregation == "p50":
            return self._percentile(values, 50)
        elif aggregation == "p95":
            return self._percentile(values, 95)
        elif aggregation == "p99":
            return self._percentile(values, 99)
        else:
            return 0.0

    def export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format"""
        output = []

        # Export counters
        for name, value in self.counters.items():
            if name in self.metrics:
                desc = self.metrics[name].get("description", "")
                output.append(f"# HELP {name} {desc}")
                output.append(f"# TYPE {name} counter")
            output.append(f"{name} {value}")

        # Export gauges
        for name, value in self.gauges.items():
            if name in self.metrics:
                desc = self.metrics[name].get("description", "")
                output.append(f"# HELP {name} {desc}")
                output.append(f"# TYPE {name} gauge")
            output.append(f"{name} {value}")

        # Export histograms (simplified)
        for name, observations in self.histograms.items():
            if observations:
                values = [obs["value"] for obs in observations[-100:]]  # Last 100
                output.append(f"{name}_count {len(values)}")
                output.append(f"{name}_sum {sum(values)}")

        return "\n".join(output)

    def _create_label_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Create unique key for labeled metric"""
        if not labels:
            return name

        label_str = ",".join([f'{k}="{v}"' for k, v in sorted(labels.items())])
        return f"{name}{{{label_str}}}"

    def _record_timestamp(self, name: str, label_key: str):
        """Record timestamp for metric update"""
        if label_key not in self.labels:
            self.labels[label_key] = []
        self.labels[label_key].append(time.time())

    def _cleanup_old_observations(self, observations: List[Dict[str, Any]]):
        """Remove old observations beyond retention period"""
        cutoff_time = time.time() - self.retention_period
        while observations and observations[0]["timestamp"] < cutoff_time:
            observations.pop(0)

    def _get_metric_value(self, name: str, metric_type: MetricType) -> Any:
        """Get current value of a metric"""
        if metric_type == MetricType.COUNTER:
            return self.counters.get(name, 0)
        elif metric_type == MetricType.GAUGE:
            return self.gauges.get(name, 0)
        elif metric_type == MetricType.HISTOGRAM:
            if name in self.histograms and self.histograms[name]:
                values = [obs["value"] for obs in self.histograms[name][-10:]]
                return sum(values) / len(values) if values else 0
        elif metric_type == MetricType.SUMMARY:
            if name in self.summaries and self.summaries[name]:
                values = [obs["value"] for obs in self.summaries[name][-10:]]
                return sum(values) / len(values) if values else 0
        return 0

    def _get_simple_metric_value(self, name: str) -> float:
        """Get simple metric value"""
        if name in self.counters:
            return self.counters[name]
        elif name in self.gauges:
            return self.gauges[name]
        return 0.0

    def _get_recent_values(
        self, observations: List[Dict[str, Any]], time_window: int
    ) -> List[float]:
        """Get recent values within time window"""
        cutoff_time = time.time() - time_window
        return [obs["value"] for obs in observations if obs["timestamp"] > cutoff_time]

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        return {
            "total_metrics": len(self.metrics),
            "counters": len(self.counters),
            "gauges": len(self.gauges),
            "histograms": len(self.histograms),
            "summaries": len(self.summaries),
            "last_collection": datetime.now().isoformat(),
        }
