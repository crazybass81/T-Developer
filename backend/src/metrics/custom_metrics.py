"""CustomMetrics - Day 41
Custom metrics definition for evolution fitness - Size: ~6.5KB"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MetricCategory(Enum):
    """Metric categories for evolution"""

    PERFORMANCE = "performance"
    QUALITY = "quality"
    INNOVATION = "innovation"
    EFFICIENCY = "efficiency"
    RELIABILITY = "reliability"
    SCALABILITY = "scalability"


class CustomMetrics:
    """Define and manage custom metrics for evolution - Size optimized to 6.5KB"""

    def __init__(self):
        self.metrics_definitions = self._initialize_metrics()
        self.metrics_data = {}
        self.thresholds = self._initialize_thresholds()
        self.weights = self._initialize_weights()

    def _initialize_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Initialize custom metric definitions"""
        return {
            # Performance metrics
            "response_time_p95": {
                "category": MetricCategory.PERFORMANCE,
                "unit": "ms",
                "description": "95th percentile response time",
                "optimal_range": (0, 200),
                "critical_threshold": 1000,
            },
            "throughput": {
                "category": MetricCategory.PERFORMANCE,
                "unit": "req/sec",
                "description": "Requests per second",
                "optimal_range": (100, 10000),
                "critical_threshold": 10,
            },
            "memory_efficiency": {
                "category": MetricCategory.EFFICIENCY,
                "unit": "KB",
                "description": "Memory usage per agent",
                "optimal_range": (0, 6.5),
                "critical_threshold": 10,
            },
            # Quality metrics
            "code_coverage": {
                "category": MetricCategory.QUALITY,
                "unit": "%",
                "description": "Test coverage percentage",
                "optimal_range": (85, 100),
                "critical_threshold": 60,
            },
            "complexity_score": {
                "category": MetricCategory.QUALITY,
                "unit": "points",
                "description": "Cyclomatic complexity",
                "optimal_range": (1, 10),
                "critical_threshold": 20,
            },
            "bug_density": {
                "category": MetricCategory.QUALITY,
                "unit": "bugs/kloc",
                "description": "Bugs per thousand lines of code",
                "optimal_range": (0, 1),
                "critical_threshold": 5,
            },
            # Innovation metrics
            "feature_novelty": {
                "category": MetricCategory.INNOVATION,
                "unit": "score",
                "description": "Novelty of generated features",
                "optimal_range": (0.5, 1.0),
                "critical_threshold": 0.1,
            },
            "adaptation_rate": {
                "category": MetricCategory.INNOVATION,
                "unit": "%/gen",
                "description": "Rate of successful adaptations",
                "optimal_range": (10, 50),
                "critical_threshold": 1,
            },
            # Reliability metrics
            "error_rate": {
                "category": MetricCategory.RELIABILITY,
                "unit": "%",
                "description": "Percentage of failed operations",
                "optimal_range": (0, 1),
                "critical_threshold": 10,
            },
            "uptime": {
                "category": MetricCategory.RELIABILITY,
                "unit": "%",
                "description": "System availability",
                "optimal_range": (99.9, 100),
                "critical_threshold": 95,
            },
            "recovery_time": {
                "category": MetricCategory.RELIABILITY,
                "unit": "seconds",
                "description": "Mean time to recovery",
                "optimal_range": (0, 60),
                "critical_threshold": 300,
            },
            # Scalability metrics
            "horizontal_scalability": {
                "category": MetricCategory.SCALABILITY,
                "unit": "ratio",
                "description": "Performance scaling with instances",
                "optimal_range": (0.8, 1.0),
                "critical_threshold": 0.5,
            },
            "resource_utilization": {
                "category": MetricCategory.EFFICIENCY,
                "unit": "%",
                "description": "Average resource usage",
                "optimal_range": (50, 80),
                "critical_threshold": 95,
            },
        }

    def _initialize_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize metric thresholds"""
        return {"excellent": 0.9, "good": 0.7, "acceptable": 0.5, "poor": 0.3, "critical": 0.1}

    def _initialize_weights(self) -> Dict[MetricCategory, float]:
        """Initialize category weights for evolution"""
        return {
            MetricCategory.PERFORMANCE: 0.25,
            MetricCategory.QUALITY: 0.20,
            MetricCategory.INNOVATION: 0.20,
            MetricCategory.EFFICIENCY: 0.15,
            MetricCategory.RELIABILITY: 0.15,
            MetricCategory.SCALABILITY: 0.05,
        }

    def record_metric(self, name: str, value: float, agent_id: str = None) -> bool:
        """Record a custom metric value"""
        if name not in self.metrics_definitions:
            return False

        key = f"{agent_id}_{name}" if agent_id else name

        if key not in self.metrics_data:
            self.metrics_data[key] = []

        self.metrics_data[key].append(
            {
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "normalized": self._normalize_value(name, value),
            }
        )

        # Keep only last 1000 entries for memory efficiency
        if len(self.metrics_data[key]) > 1000:
            self.metrics_data[key] = self.metrics_data[key][-1000:]

        return True

    def _normalize_value(self, metric_name: str, value: float) -> float:
        """Normalize metric value to 0-1 range"""
        if metric_name not in self.metrics_definitions:
            return 0.0

        metric_def = self.metrics_definitions[metric_name]
        optimal_min, optimal_max = metric_def["optimal_range"]
        critical = metric_def["critical_threshold"]

        # Handle inverse metrics (lower is better)
        if metric_name in [
            "response_time_p95",
            "complexity_score",
            "bug_density",
            "error_rate",
            "recovery_time",
        ]:
            if value <= optimal_min:
                return 1.0
            elif value >= critical:
                return 0.0
            elif value <= optimal_max:
                return 1.0 - (value - optimal_min) / (optimal_max - optimal_min) * 0.2
            else:
                return 0.8 * (critical - value) / (critical - optimal_max)

        # Handle normal metrics (higher is better)
        else:
            if value >= optimal_max:
                return 1.0
            elif value <= critical:
                return 0.0
            elif value >= optimal_min:
                return 0.8 + (value - optimal_min) / (optimal_max - optimal_min) * 0.2
            else:
                return (value - critical) / (optimal_min - critical) * 0.8

    def calculate_fitness_contribution(self, agent_id: str) -> Dict[str, float]:
        """Calculate fitness contribution from custom metrics"""
        contributions = {}
        category_scores = {cat: [] for cat in MetricCategory}

        # Calculate scores for each metric
        for metric_name, metric_def in self.metrics_definitions.items():
            key = f"{agent_id}_{metric_name}"
            if key in self.metrics_data and self.metrics_data[key]:
                # Use latest value
                latest = self.metrics_data[key][-1]
                category = metric_def["category"]
                category_scores[category].append(latest["normalized"])

        # Calculate category averages
        for category, scores in category_scores.items():
            if scores:
                contributions[category.value] = sum(scores) / len(scores)
            else:
                contributions[category.value] = 0.5  # Default neutral score

        # Calculate weighted total
        total = 0.0
        for category, weight in self.weights.items():
            total += contributions.get(category.value, 0.5) * weight

        contributions["total"] = total
        return contributions

    def get_metric_trend(
        self, metric_name: str, agent_id: str = None, window: int = 10
    ) -> Dict[str, Any]:
        """Analyze metric trend over recent window"""
        key = f"{agent_id}_{metric_name}" if agent_id else metric_name

        if key not in self.metrics_data or len(self.metrics_data[key]) < 2:
            return {"trend": "stable", "change": 0.0}

        recent = self.metrics_data[key][-window:]
        values = [entry["value"] for entry in recent]

        # Calculate trend
        if len(values) >= 2:
            change = (values[-1] - values[0]) / values[0] if values[0] != 0 else 0

            if abs(change) < 0.05:
                trend = "stable"
            elif change > 0:
                trend = "improving" if self._is_positive_direction(metric_name) else "degrading"
            else:
                trend = "degrading" if self._is_positive_direction(metric_name) else "improving"

            return {
                "trend": trend,
                "change": change,
                "current": values[-1],
                "average": sum(values) / len(values),
            }

        return {"trend": "stable", "change": 0.0}

    def _is_positive_direction(self, metric_name: str) -> bool:
        """Check if higher values are better for this metric"""
        inverse_metrics = [
            "response_time_p95",
            "complexity_score",
            "bug_density",
            "error_rate",
            "recovery_time",
            "memory_efficiency",
        ]
        return metric_name not in inverse_metrics

    def identify_bottlenecks(self, agent_id: str) -> List[Dict[str, Any]]:
        """Identify metrics that are bottlenecks for evolution"""
        bottlenecks = []

        for metric_name, metric_def in self.metrics_definitions.items():
            key = f"{agent_id}_{metric_name}"
            if key in self.metrics_data and self.metrics_data[key]:
                latest = self.metrics_data[key][-1]

                # Check if below acceptable threshold
                if latest["normalized"] < self.thresholds["acceptable"]:
                    bottlenecks.append(
                        {
                            "metric": metric_name,
                            "category": metric_def["category"].value,
                            "current_value": latest["value"],
                            "normalized_score": latest["normalized"],
                            "severity": self._get_severity(latest["normalized"]),
                        }
                    )

        # Sort by severity
        return sorted(bottlenecks, key=lambda x: x["normalized_score"])

    def _get_severity(self, normalized_value: float) -> str:
        """Get severity level based on normalized value"""
        for level, threshold in sorted(self.thresholds.items(), key=lambda x: x[1], reverse=True):
            if normalized_value >= threshold:
                return level
        return "critical"

    def export_metrics(self, agent_id: str = None) -> Dict[str, Any]:
        """Export all metrics for an agent"""
        export_data = {"timestamp": datetime.now().isoformat(), "metrics": {}}

        for metric_name in self.metrics_definitions:
            key = f"{agent_id}_{metric_name}" if agent_id else metric_name
            if key in self.metrics_data and self.metrics_data[key]:
                latest = self.metrics_data[key][-1]
                export_data["metrics"][metric_name] = {
                    "value": latest["value"],
                    "normalized": latest["normalized"],
                    "timestamp": latest["timestamp"],
                }

        if agent_id:
            export_data["fitness_contribution"] = self.calculate_fitness_contribution(agent_id)
            export_data["bottlenecks"] = self.identify_bottlenecks(agent_id)

        return export_data
