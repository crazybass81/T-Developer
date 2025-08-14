"""BusinessEvaluator - Day 42
Business value evaluation across multiple dimensions - Size: ~6.5KB"""
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class BusinessEvaluator:
    """Evaluate agent business value across multiple dimensions - Size optimized to 6.5KB"""

    def __init__(self):
        self.dimensions = self._initialize_dimensions()
        self.metrics = self._initialize_metrics()
        self.weights = self._initialize_weights()
        self.benchmarks = self._initialize_benchmarks()
        self.history = {}

    def _initialize_dimensions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize business dimensions"""
        return {
            "revenue_impact": {
                "metrics": ["conversion_rate", "average_order_value", "customer_lifetime_value"],
                "weight": 0.3,
                "priority": "high",
            },
            "cost_efficiency": {
                "metrics": ["operational_cost", "resource_utilization", "automation_rate"],
                "weight": 0.25,
                "priority": "high",
            },
            "user_satisfaction": {
                "metrics": ["user_rating", "nps_score", "retention_rate"],
                "weight": 0.2,
                "priority": "medium",
            },
            "productivity": {
                "metrics": ["task_completion_rate", "time_savings", "throughput"],
                "weight": 0.15,
                "priority": "medium",
            },
            "innovation": {
                "metrics": ["feature_adoption", "competitive_advantage", "time_to_market"],
                "weight": 0.1,
                "priority": "low",
            },
        }

    def _initialize_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Initialize business metrics"""
        return {
            "conversion_rate": {"unit": "%", "target": 5, "baseline": 2},
            "average_order_value": {"unit": "$", "target": 150, "baseline": 100},
            "customer_lifetime_value": {"unit": "$", "target": 1000, "baseline": 500},
            "operational_cost": {"unit": "$/month", "target": 5000, "baseline": 10000},
            "resource_utilization": {"unit": "%", "target": 80, "baseline": 60},
            "automation_rate": {"unit": "%", "target": 70, "baseline": 30},
            "user_rating": {"unit": "stars", "target": 4.5, "baseline": 3.5},
            "nps_score": {"unit": "points", "target": 50, "baseline": 20},
            "retention_rate": {"unit": "%", "target": 90, "baseline": 70},
            "task_completion_rate": {"unit": "%", "target": 95, "baseline": 80},
            "time_savings": {"unit": "hours/week", "target": 20, "baseline": 5},
            "throughput": {"unit": "tasks/hour", "target": 100, "baseline": 50},
            "feature_adoption": {"unit": "%", "target": 60, "baseline": 20},
            "competitive_advantage": {"unit": "score", "target": 8, "baseline": 5},
            "time_to_market": {"unit": "days", "target": 30, "baseline": 90},
        }

    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize metric weights within dimensions"""
        return {
            "conversion_rate": 0.4,
            "average_order_value": 0.35,
            "customer_lifetime_value": 0.25,
            "operational_cost": 0.4,
            "resource_utilization": 0.3,
            "automation_rate": 0.3,
            "user_rating": 0.35,
            "nps_score": 0.35,
            "retention_rate": 0.3,
            "task_completion_rate": 0.4,
            "time_savings": 0.35,
            "throughput": 0.25,
            "feature_adoption": 0.35,
            "competitive_advantage": 0.35,
            "time_to_market": 0.3,
        }

    def _initialize_benchmarks(self) -> Dict[str, float]:
        """Initialize industry benchmarks"""
        return {
            "conversion_rate": 3.5,
            "user_rating": 4.0,
            "nps_score": 35,
            "retention_rate": 80,
            "automation_rate": 50,
        }

    def evaluate(self, agent_id: str, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Evaluate agent business value"""
        evaluation = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "dimensions": {},
            "overall_score": 0,
            "roi_estimate": 0,
            "recommendations": [],
            "value_proposition": "",
        }

        # Evaluate each dimension
        for dim_name, dim_config in self.dimensions.items():
            dim_score = self._evaluate_dimension(dim_name, dim_config, metrics)
            evaluation["dimensions"][dim_name] = dim_score

        # Calculate overall score
        evaluation["overall_score"] = self._calculate_overall_score(evaluation["dimensions"])

        # Calculate ROI
        evaluation["roi_estimate"] = self._calculate_roi(metrics)

        # Generate recommendations
        evaluation["recommendations"] = self._generate_recommendations(evaluation["dimensions"])

        # Create value proposition
        evaluation["value_proposition"] = self._create_value_proposition(evaluation)

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
        """Evaluate a business dimension"""
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
                    "vs_target": self._compare_to_target(metric_name, metrics[metric_name]),
                    "vs_baseline": self._compare_to_baseline(metric_name, metrics[metric_name]),
                }

        dimension_score = (sum(scores) / weights_sum) if weights_sum > 0 else 50

        return {
            "score": dimension_score,
            "normalized": dimension_score / 100,
            "details": details,
            "priority": dim_config["priority"],
            "impact_level": self._get_impact_level(dimension_score),
        }

    def _calculate_metric_score(self, metric_name: str, value: float) -> float:
        """Calculate score for a business metric"""
        if metric_name not in self.metrics:
            return 50

        metric_info = self.metrics[metric_name]
        target = metric_info["target"]
        baseline = metric_info["baseline"]

        # Inverse metrics (lower is better)
        if metric_name in ["operational_cost", "time_to_market"]:
            if value <= target:
                return 100
            elif value <= baseline:
                # Linear interpolation between target and baseline
                return 50 + 50 * (baseline - value) / (baseline - target)
            else:
                # Score decreases beyond baseline
                return max(0, 50 * (2 * baseline - value) / baseline)

        # Normal metrics (higher is better)
        else:
            if value >= target:
                return 100
            elif value >= baseline:
                # Linear interpolation between baseline and target
                return 50 + 50 * (value - baseline) / (target - baseline)
            else:
                # Score decreases below baseline
                return max(0, 50 * value / baseline)

    def _compare_to_target(self, metric_name: str, value: float) -> float:
        """Compare value to target"""
        if metric_name not in self.metrics:
            return 0

        target = self.metrics[metric_name]["target"]

        if metric_name in ["operational_cost", "time_to_market"]:
            # Lower is better
            return ((target - value) / target) * 100 if target != 0 else 0
        else:
            # Higher is better
            return ((value - target) / target) * 100 if target != 0 else 0

    def _compare_to_baseline(self, metric_name: str, value: float) -> float:
        """Compare value to baseline"""
        if metric_name not in self.metrics:
            return 0

        baseline = self.metrics[metric_name]["baseline"]

        if metric_name in ["operational_cost", "time_to_market"]:
            # Lower is better
            return ((baseline - value) / baseline) * 100 if baseline != 0 else 0
        else:
            # Higher is better
            return ((value - baseline) / baseline) * 100 if baseline != 0 else 0

    def _get_impact_level(self, score: float) -> str:
        """Get business impact level"""
        if score >= 80:
            return "transformational"
        elif score >= 60:
            return "significant"
        elif score >= 40:
            return "moderate"
        elif score >= 20:
            return "marginal"
        else:
            return "minimal"

    def _calculate_overall_score(self, dimensions: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall business value score"""
        total = 0
        total_weight = 0

        for dim_name, dim_result in dimensions.items():
            if dim_name in self.dimensions:
                weight = self.dimensions[dim_name]["weight"]
                total += dim_result["score"] * weight
                total_weight += weight

        return total / total_weight if total_weight > 0 else 0

    def _calculate_roi(self, metrics: Dict[str, float]) -> float:
        """Calculate estimated ROI"""
        # Simplified ROI calculation
        revenue_increase = metrics.get("conversion_rate", 0) * metrics.get("average_order_value", 0)
        cost_reduction = self.metrics["operational_cost"]["baseline"] - metrics.get(
            "operational_cost", self.metrics["operational_cost"]["baseline"]
        )
        time_value = metrics.get("time_savings", 0) * 50  # $50/hour estimated value

        total_benefit = revenue_increase + cost_reduction + time_value
        total_cost = metrics.get("operational_cost", self.metrics["operational_cost"]["baseline"])

        if total_cost > 0:
            roi = ((total_benefit - total_cost) / total_cost) * 100
            return round(roi, 2)
        return 0

    def _generate_recommendations(
        self, dimensions: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate business improvement recommendations"""
        recommendations = []

        for dim_name, dim_result in dimensions.items():
            if dim_result["impact_level"] in ["minimal", "marginal"]:
                priority = "high" if dim_result["priority"] == "high" else "medium"

                for metric_name, metric_data in dim_result["details"].items():
                    if metric_data["score"] < 50:
                        recommendations.append(
                            {
                                "dimension": dim_name,
                                "metric": metric_name,
                                "current_value": metric_data["value"],
                                "target_value": self.metrics[metric_name]["target"],
                                "priority": priority,
                                "potential_impact": self._estimate_impact(metric_name),
                                "action": self._suggest_action(metric_name),
                            }
                        )

        return sorted(recommendations, key=lambda x: x["priority"] == "high", reverse=True)[:5]

    def _estimate_impact(self, metric_name: str) -> str:
        """Estimate potential business impact"""
        high_impact = ["conversion_rate", "customer_lifetime_value", "operational_cost"]
        medium_impact = ["user_rating", "retention_rate", "automation_rate"]

        if metric_name in high_impact:
            return "high"
        elif metric_name in medium_impact:
            return "medium"
        else:
            return "low"

    def _suggest_action(self, metric_name: str) -> str:
        """Suggest action for improvement"""
        actions = {
            "conversion_rate": "Optimize user experience and checkout flow",
            "average_order_value": "Implement upselling and cross-selling strategies",
            "customer_lifetime_value": "Improve retention and loyalty programs",
            "operational_cost": "Automate repetitive tasks and optimize resources",
            "resource_utilization": "Implement better load balancing and scaling",
            "automation_rate": "Identify and automate manual processes",
            "user_rating": "Address user feedback and improve UX",
            "nps_score": "Focus on customer satisfaction initiatives",
            "retention_rate": "Implement engagement and retention strategies",
            "task_completion_rate": "Optimize workflows and remove bottlenecks",
            "time_savings": "Streamline processes and reduce manual work",
            "throughput": "Optimize performance and parallel processing",
            "feature_adoption": "Improve onboarding and feature discovery",
            "competitive_advantage": "Innovate and differentiate offerings",
            "time_to_market": "Streamline development and deployment processes",
        }
        return actions.get(metric_name, f"Optimize {metric_name}")

    def _create_value_proposition(self, evaluation: Dict[str, Any]) -> str:
        """Create value proposition statement"""
        score = evaluation["overall_score"]
        roi = evaluation["roi_estimate"]

        if score >= 80:
            level = "exceptional"
        elif score >= 60:
            level = "strong"
        elif score >= 40:
            level = "moderate"
        else:
            level = "developing"

        top_dimension = max(evaluation["dimensions"].items(), key=lambda x: x[1]["score"])[
            0
        ].replace("_", " ")

        return f"Delivers {level} business value with {roi:.1f}% ROI, excelling in {top_dimension}"

    def compare_periods(
        self, agent_id: str, period1_start: int, period2_start: int
    ) -> Dict[str, Any]:
        """Compare business metrics between two periods"""
        if agent_id not in self.history or len(self.history[agent_id]) < 2:
            return {"error": "Insufficient data"}

        history = self.history[agent_id]
        period1 = history[period1_start : period1_start + 5] if period1_start < len(history) else []
        period2 = history[period2_start : period2_start + 5] if period2_start < len(history) else []

        if not period1 or not period2:
            return {"error": "Invalid period ranges"}

        comparison = {
            "agent_id": agent_id,
            "period1_avg": sum(e["overall_score"] for e in period1) / len(period1),
            "period2_avg": sum(e["overall_score"] for e in period2) / len(period2),
            "improvement": 0,
            "dimension_changes": {},
        }

        comparison["improvement"] = comparison["period2_avg"] - comparison["period1_avg"]

        # Compare dimensions
        for dim_name in self.dimensions:
            p1_scores = [
                e["dimensions"][dim_name]["score"] for e in period1 if dim_name in e["dimensions"]
            ]
            p2_scores = [
                e["dimensions"][dim_name]["score"] for e in period2 if dim_name in e["dimensions"]
            ]

            if p1_scores and p2_scores:
                p1_avg = sum(p1_scores) / len(p1_scores)
                p2_avg = sum(p2_scores) / len(p2_scores)
                comparison["dimension_changes"][dim_name] = {
                    "before": p1_avg,
                    "after": p2_avg,
                    "change": p2_avg - p1_avg,
                }

        return comparison
