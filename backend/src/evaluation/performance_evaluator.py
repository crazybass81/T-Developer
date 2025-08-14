"""PerformanceEvaluator - Day 42
Multi-dimensional performance evaluation - Size: ~6.5KB"""
import statistics
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


class PerformanceEvaluator:
    """Evaluate agent performance across multiple dimensions - Size optimized to 6.5KB"""

    def __init__(self):
        self.dimensions = self._initialize_dimensions()
        self.weights = self._initialize_weights()
        self.thresholds = self._initialize_thresholds()
        self.history = {}
        self.benchmarks = self._initialize_benchmarks()

    def _initialize_dimensions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize performance dimensions"""
        return {
            "speed": {
                "metrics": ["response_time", "throughput", "latency"],
                "weight": 0.3,
                "critical": True,
            },
            "efficiency": {
                "metrics": ["cpu_usage", "memory_usage", "io_operations"],
                "weight": 0.25,
                "critical": True,
            },
            "scalability": {
                "metrics": ["concurrent_users", "load_capacity", "elastic_scaling"],
                "weight": 0.2,
                "critical": False,
            },
            "stability": {
                "metrics": ["error_rate", "crash_frequency", "recovery_time"],
                "weight": 0.15,
                "critical": True,
            },
            "optimization": {
                "metrics": ["cache_hit_rate", "query_optimization", "resource_pooling"],
                "weight": 0.1,
                "critical": False,
            },
        }

    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize metric weights within dimensions"""
        return {
            "response_time": 0.4,
            "throughput": 0.35,
            "latency": 0.25,
            "cpu_usage": 0.35,
            "memory_usage": 0.4,
            "io_operations": 0.25,
            "concurrent_users": 0.4,
            "load_capacity": 0.35,
            "elastic_scaling": 0.25,
            "error_rate": 0.5,
            "crash_frequency": 0.3,
            "recovery_time": 0.2,
            "cache_hit_rate": 0.4,
            "query_optimization": 0.35,
            "resource_pooling": 0.25,
        }

    def _initialize_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize performance thresholds"""
        return {
            "response_time": {"excellent": 50, "good": 200, "acceptable": 500, "poor": 1000},
            "throughput": {"excellent": 1000, "good": 500, "acceptable": 100, "poor": 10},
            "latency": {"excellent": 10, "good": 50, "acceptable": 100, "poor": 500},
            "cpu_usage": {"excellent": 30, "good": 50, "acceptable": 70, "poor": 90},
            "memory_usage": {"excellent": 40, "good": 60, "acceptable": 75, "poor": 90},
            "io_operations": {"excellent": 100, "good": 500, "acceptable": 1000, "poor": 5000},
            "concurrent_users": {"excellent": 1000, "good": 500, "acceptable": 100, "poor": 10},
            "load_capacity": {"excellent": 10000, "good": 5000, "acceptable": 1000, "poor": 100},
            "elastic_scaling": {"excellent": 0.9, "good": 0.7, "acceptable": 0.5, "poor": 0.3},
            "error_rate": {"excellent": 0.1, "good": 1, "acceptable": 5, "poor": 10},
            "crash_frequency": {"excellent": 0, "good": 1, "acceptable": 5, "poor": 10},
            "recovery_time": {"excellent": 10, "good": 60, "acceptable": 300, "poor": 600},
            "cache_hit_rate": {"excellent": 90, "good": 70, "acceptable": 50, "poor": 30},
            "query_optimization": {"excellent": 0.9, "good": 0.7, "acceptable": 0.5, "poor": 0.3},
            "resource_pooling": {"excellent": 0.9, "good": 0.7, "acceptable": 0.5, "poor": 0.3},
        }

    def _initialize_benchmarks(self) -> Dict[str, float]:
        """Initialize industry benchmarks"""
        return {
            "response_time": 100,  # ms
            "throughput": 750,  # req/sec
            "cpu_usage": 45,  # %
            "memory_usage": 55,  # %
            "error_rate": 0.5,  # %
        }

    def evaluate(self, agent_id: str, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Evaluate agent performance"""
        evaluation = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "dimensions": {},
            "overall_score": 0,
            "recommendations": [],
        }

        # Evaluate each dimension
        for dim_name, dim_config in self.dimensions.items():
            dim_score = self._evaluate_dimension(dim_name, dim_config, metrics)
            evaluation["dimensions"][dim_name] = dim_score

        # Calculate overall score
        evaluation["overall_score"] = self._calculate_overall_score(evaluation["dimensions"])

        # Generate recommendations
        evaluation["recommendations"] = self._generate_recommendations(evaluation["dimensions"])

        # Store in history
        if agent_id not in self.history:
            self.history[agent_id] = []
        self.history[agent_id].append(evaluation)

        # Keep only last 100 evaluations
        if len(self.history[agent_id]) > 100:
            self.history[agent_id] = self.history[agent_id][-100:]

        return evaluation

    def _evaluate_dimension(
        self, dim_name: str, dim_config: Dict[str, Any], metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Evaluate a single dimension"""
        scores = []
        weights_sum = 0
        details = {}

        for metric_name in dim_config["metrics"]:
            if metric_name in metrics:
                score = self._calculate_metric_score(metric_name, metrics[metric_name])
                weight = self.weights.get(metric_name, 1.0)
                weighted_score = score * weight
                scores.append(weighted_score)
                weights_sum += weight
                details[metric_name] = {
                    "value": metrics[metric_name],
                    "score": score,
                    "weighted_score": weighted_score,
                    "rating": self._get_rating(metric_name, metrics[metric_name]),
                }

        dimension_score = (sum(scores) / weights_sum) if weights_sum > 0 else 50

        return {
            "score": dimension_score,
            "normalized": dimension_score / 100,
            "details": details,
            "critical": dim_config["critical"],
            "status": self._get_dimension_status(dimension_score, dim_config["critical"]),
        }

    def _calculate_metric_score(self, metric_name: str, value: float) -> float:
        """Calculate score for a single metric"""
        if metric_name not in self.thresholds:
            return 50  # Default neutral score

        thresholds = self.thresholds[metric_name]

        # Invert for metrics where lower is better
        lower_is_better = metric_name in [
            "response_time",
            "latency",
            "cpu_usage",
            "memory_usage",
            "io_operations",
            "error_rate",
            "crash_frequency",
            "recovery_time",
        ]

        if lower_is_better:
            if value <= thresholds["excellent"]:
                return 100
            elif value <= thresholds["good"]:
                return 75
            elif value <= thresholds["acceptable"]:
                return 50
            elif value <= thresholds["poor"]:
                return 25
            else:
                return 0
        else:
            if value >= thresholds["excellent"]:
                return 100
            elif value >= thresholds["good"]:
                return 75
            elif value >= thresholds["acceptable"]:
                return 50
            elif value >= thresholds["poor"]:
                return 25
            else:
                return 0

    def _get_rating(self, metric_name: str, value: float) -> str:
        """Get rating for a metric value"""
        score = self._calculate_metric_score(metric_name, value)
        if score >= 90:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "acceptable"
        elif score >= 25:
            return "poor"
        else:
            return "critical"

    def _get_dimension_status(self, score: float, is_critical: bool) -> str:
        """Get status for a dimension"""
        if score >= 80:
            return "optimal"
        elif score >= 60:
            return "healthy"
        elif score >= 40:
            return "warning" if not is_critical else "critical"
        else:
            return "critical"

    def _calculate_overall_score(self, dimensions: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall performance score"""
        total = 0
        total_weight = 0

        for dim_name, dim_result in dimensions.items():
            if dim_name in self.dimensions:
                weight = self.dimensions[dim_name]["weight"]
                total += dim_result["score"] * weight
                total_weight += weight

        return total / total_weight if total_weight > 0 else 0

    def _generate_recommendations(
        self, dimensions: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate performance improvement recommendations"""
        recommendations = []

        for dim_name, dim_result in dimensions.items():
            if dim_result["status"] in ["warning", "critical"]:
                for metric_name, metric_data in dim_result["details"].items():
                    if metric_data["rating"] in ["poor", "critical"]:
                        recommendations.append(
                            {
                                "dimension": dim_name,
                                "metric": metric_name,
                                "current_value": metric_data["value"],
                                "target_value": self.thresholds[metric_name]["good"],
                                "priority": "high" if dim_result["critical"] else "medium",
                                "suggestion": self._get_improvement_suggestion(metric_name),
                            }
                        )

        return sorted(recommendations, key=lambda x: x["priority"] == "high", reverse=True)

    def _get_improvement_suggestion(self, metric_name: str) -> str:
        """Get improvement suggestion for a metric"""
        suggestions = {
            "response_time": "Optimize database queries and add caching",
            "throughput": "Scale horizontally or optimize request handling",
            "latency": "Reduce network hops and optimize I/O operations",
            "cpu_usage": "Profile code for CPU hotspots and optimize algorithms",
            "memory_usage": "Check for memory leaks and optimize data structures",
            "error_rate": "Add error handling and improve input validation",
            "recovery_time": "Implement circuit breakers and failover mechanisms",
        }
        return suggestions.get(metric_name, f"Optimize {metric_name}")

    def compare_agents(self, agent_ids: List[str]) -> Dict[str, Any]:
        """Compare performance across multiple agents"""
        if not agent_ids or not all(aid in self.history for aid in agent_ids):
            return {"error": "Missing agent data"}

        comparison = {"agents": {}, "best_performer": None, "dimension_winners": {}}

        for agent_id in agent_ids:
            latest = self.history[agent_id][-1] if self.history[agent_id] else None
            if latest:
                comparison["agents"][agent_id] = {
                    "overall_score": latest["overall_score"],
                    "dimensions": latest["dimensions"],
                }

        # Find best overall performer
        best_score = 0
        for agent_id, data in comparison["agents"].items():
            if data["overall_score"] > best_score:
                best_score = data["overall_score"]
                comparison["best_performer"] = agent_id

        # Find dimension winners
        for dim_name in self.dimensions:
            best_dim_score = 0
            best_dim_agent = None
            for agent_id, data in comparison["agents"].items():
                if dim_name in data["dimensions"]:
                    score = data["dimensions"][dim_name]["score"]
                    if score > best_dim_score:
                        best_dim_score = score
                        best_dim_agent = agent_id
            if best_dim_agent:
                comparison["dimension_winners"][dim_name] = best_dim_agent

        return comparison

    def get_trends(self, agent_id: str, window: int = 10) -> Dict[str, Any]:
        """Get performance trends for an agent"""
        if agent_id not in self.history or len(self.history[agent_id]) < 2:
            return {"error": "Insufficient data"}

        recent = self.history[agent_id][-window:]
        trends = {
            "agent_id": agent_id,
            "window": len(recent),
            "overall_trend": self._calculate_trend([e["overall_score"] for e in recent]),
            "dimension_trends": {},
        }

        for dim_name in self.dimensions:
            scores = [
                e["dimensions"][dim_name]["score"] for e in recent if dim_name in e["dimensions"]
            ]
            if scores:
                trends["dimension_trends"][dim_name] = self._calculate_trend(scores)

        return trends

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values"""
        if len(values) < 2:
            return "stable"

        # Simple linear regression
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n

        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        if abs(slope) < 0.5:
            return "stable"
        elif slope > 0:
            return "improving"
        else:
            return "degrading"
