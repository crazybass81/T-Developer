"""
CostOptimizer - Day 32
AI cost optimization system
Size: ~6.5KB (optimized)
"""

import statistics
import time
from collections import defaultdict
from typing import Any, Dict, List


class CostOptimizer:
    """Optimizes AI model usage costs"""

    def __init__(self):
        self.models = self._init_model_pricing()
        self.usage_history = []
        self.optimizations = []
        self.budget = {"daily": None, "monthly": None}
        self.feature_usage = defaultdict(lambda: {"tokens": 0, "cost": 0})
        self.daily_usage = defaultdict(float)

    def calculate_cost(self, usage: Dict[str, Any]) -> Dict[str, float]:
        """Calculate cost for usage"""
        model = usage.get("model", "gpt-3.5")
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)

        pricing = self.models.get(model, self.models["gpt-3.5"])

        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]

        return {
            "input_cost": round(input_cost, 4),
            "output_cost": round(output_cost, 4),
            "total_cost": round(input_cost + output_cost, 4),
            "model": model,
        }

    def optimize_model_selection(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Select optimal model for task"""
        task_type = task.get("type", "general")
        complexity = task.get("complexity", "medium")
        max_budget = task.get("max_budget", float("inf"))

        # Model selection logic
        if complexity == "low":
            model = "gpt-3.5-turbo"
            tokens = 500
        elif complexity == "medium":
            model = "gpt-3.5"
            tokens = 1000
        else:
            model = "gpt-4" if max_budget > 0.5 else "gpt-3.5"
            tokens = 2000

        cost = self.calculate_cost(
            {
                "model": model,
                "input_tokens": tokens // 2,
                "output_tokens": tokens // 2,
            }
        )

        return {
            "model": model,
            "estimated_cost": cost["total_cost"],
            "reasoning": f"Selected for {complexity} complexity {task_type}",
        }

    def optimize_batch(self, requests: List[Dict]) -> Dict[str, Any]:
        """Optimize batch processing"""
        batch_size = 10
        num_batches = (len(requests) + batch_size - 1) // batch_size

        # Calculate savings from batching
        individual_cost = len(requests) * 0.01  # Example base cost
        batched_cost = num_batches * 0.08  # Bulk discount

        return {
            "batches": num_batches,
            "batch_size": batch_size,
            "estimated_savings": round(individual_cost - batched_cost, 2),
            "optimization": "batch_processing",
        }

    def recommend_cache_strategy(self, queries: List[str]) -> Dict[str, Any]:
        """Recommend caching strategy"""
        query_counts = defaultdict(int)
        for query in queries:
            query_counts[query] += 1

        # Find cacheable queries (repeated more than once)
        cache_candidates = [q for q, count in query_counts.items() if count > 1]

        total_queries = len(queries)
        cached_queries = sum(query_counts[q] - 1 for q in cache_candidates)
        hit_rate = cached_queries / total_queries if total_queries > 0 else 0

        return {
            "cache_candidates": cache_candidates[:5],  # Top 5
            "estimated_hit_rate": round(hit_rate, 2),
            "potential_savings": round(hit_rate * 0.5, 2),  # 50% cost reduction
        }

    def track_usage(self, usage: Dict[str, Any]):
        """Track usage data"""
        usage["timestamp"] = time.time()
        self.usage_history.append(usage)

        # Track daily usage
        cost = self.calculate_cost(usage)
        today = time.strftime("%Y-%m-%d")
        self.daily_usage[today] += cost["total_cost"]

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        if not self.usage_history:
            return {"total_requests": 0, "total_tokens": 0}

        total_requests = len(self.usage_history)
        total_tokens = sum(
            u.get("input_tokens", 0) + u.get("output_tokens", 0) for u in self.usage_history
        )

        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "average_tokens_per_request": total_tokens // max(1, total_requests),
        }

    def set_budget(self, daily: float = None, monthly: float = None):
        """Set budget limits"""
        if daily:
            self.budget["daily"] = daily
        if monthly:
            self.budget["monthly"] = monthly

    def check_budget_status(self) -> Dict[str, Any]:
        """Check budget status"""
        today = time.strftime("%Y-%m-%d")
        daily_spent = self.daily_usage.get(today, 0)

        # Calculate monthly spent
        current_month = time.strftime("%Y-%m")
        monthly_spent = sum(
            cost for day, cost in self.daily_usage.items() if day.startswith(current_month)
        )

        daily_limit = self.budget.get("daily")
        monthly_limit = self.budget.get("monthly")

        within_budget = True
        if daily_limit is not None:
            within_budget = within_budget and (daily_spent < daily_limit)
        if monthly_limit is not None:
            within_budget = within_budget and (monthly_spent < monthly_limit)

        return {
            "daily_remaining": round(daily_limit - daily_spent, 2) if daily_limit else float("inf"),
            "monthly_remaining": round(monthly_limit - monthly_spent, 2)
            if monthly_limit
            else float("inf"),
            "within_budget": within_budget,
            "daily_spent": round(daily_spent, 2),
            "monthly_spent": round(monthly_spent, 2),
        }

    def forecast_costs(self, days: int = 30) -> Dict[str, Any]:
        """Forecast future costs"""
        if len(self.usage_history) < 7:
            # Not enough data
            return {"predicted_cost": 0, "confidence": 0}

        # Calculate average daily cost from history
        recent_costs = list(self.daily_usage.values())[-7:]
        avg_daily = statistics.mean(recent_costs) if recent_costs else 0

        predicted = avg_daily * days
        confidence = min(0.9, len(recent_costs) / 30)  # More data = higher confidence

        return {
            "predicted_cost": round(predicted, 2),
            "confidence": round(confidence, 2),
            "based_on_days": len(recent_costs),
        }

    def get_recommendations(self, usage: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get optimization recommendations"""
        recommendations = []

        # Check model usage
        if usage.get("models", {}).get("gpt-4", 0) > 0.5:
            recommendations.append(
                {
                    "action": "Use GPT-3.5 for simpler tasks",
                    "potential_savings": 0.7,
                    "difficulty": "easy",
                }
            )

        # Check caching
        if usage.get("cache_hit_rate", 0) < 0.3:
            recommendations.append(
                {
                    "action": "Implement response caching",
                    "potential_savings": 0.3,
                    "difficulty": "medium",
                }
            )

        # Check prompt length
        if usage.get("average_prompt_length", 0) > 500:
            recommendations.append(
                {
                    "action": "Optimize prompt length",
                    "potential_savings": 0.2,
                    "difficulty": "easy",
                }
            )

        return recommendations

    def compare_models(self, task_type: str, tokens: int) -> List[Dict[str, Any]]:
        """Compare model costs"""
        comparison = []

        for model, pricing in self.models.items():
            cost = self.calculate_cost(
                {
                    "model": model,
                    "input_tokens": tokens // 2,
                    "output_tokens": tokens // 2,
                }
            )

            comparison.append(
                {
                    "model": model,
                    "cost": cost["total_cost"],
                    "suitable_for": self._get_model_suitability(model),
                }
            )

        return sorted(comparison, key=lambda x: x["cost"])

    def optimize_tokens(self, prompt: str) -> Dict[str, Any]:
        """Optimize token usage"""
        original_tokens = len(prompt.split())

        # Simple optimization: remove redundant words
        optimized = " ".join(prompt.split())  # Remove extra spaces
        optimized = optimized.replace("very ", "").replace("really ", "")

        optimized_tokens = len(optimized.split())

        return {
            "optimized_prompt": optimized,
            "tokens_saved": max(0, original_tokens - optimized_tokens),
            "percentage_saved": round((1 - optimized_tokens / max(1, original_tokens)) * 100, 1),
        }

    def optimize_rate_limits(self, requests: List[Dict], max_rpm: int = 60) -> Dict[str, Any]:
        """Optimize for rate limits"""
        # Sort by priority
        sorted_requests = sorted(requests, key=lambda x: x.get("priority", 0), reverse=True)

        # Create schedule
        batches = []
        for i in range(0, len(sorted_requests), max_rpm):
            batches.append(sorted_requests[i : i + max_rpm])

        return {
            "schedule": batches,
            "estimated_time": len(batches),  # minutes
            "prioritized": True,
        }

    def create_fallback_strategy(
        self, primary: str, budget_threshold: float = 0.8
    ) -> Dict[str, str]:
        """Create fallback model strategy"""
        fallback_map = {
            "gpt-4": "gpt-3.5",
            "gpt-3.5": "gpt-3.5-turbo",
            "claude": "gpt-3.5",
        }

        return {
            "primary": primary,
            "fallback": fallback_map.get(primary, "gpt-3.5-turbo"),
            "threshold": budget_threshold,
            "strategy": "cost_based_fallback",
        }

    def allocate_costs(self, usage: List[Dict]) -> Dict[str, float]:
        """Allocate costs across projects"""
        project_costs = defaultdict(float)

        for item in usage:
            project = item.get("project", "default")
            # Ensure we have token data
            if "tokens" in item:
                item["input_tokens"] = item["tokens"]
                item["output_tokens"] = 0
            cost = self.calculate_cost(item)
            project_costs[project] += cost["total_cost"]

        return dict(project_costs)

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect cost anomalies"""
        if len(self.usage_history) < 10:
            return []

        # Calculate average and std dev
        costs = [self.calculate_cost(u)["total_cost"] for u in self.usage_history[-20:]]

        if not costs:
            return []

        avg = statistics.mean(costs)
        std = statistics.stdev(costs) if len(costs) > 1 else 0

        anomalies = []
        for i, cost in enumerate(costs[-5:]):  # Check last 5
            if cost > avg + 2 * std:  # 2 standard deviations
                anomalies.append(
                    {
                        "index": i,
                        "cost": cost,
                        "deviation": round((cost - avg) / max(std, 0.01), 2),
                    }
                )

        return anomalies

    def track_optimization(self, strategy: str, saved: float):
        """Track optimization savings"""
        self.optimizations.append(
            {
                "strategy": strategy,
                "saved": saved,
                "timestamp": time.time(),
            }
        )

    def generate_savings_report(self) -> Dict[str, Any]:
        """Generate savings report"""
        if not self.optimizations:
            return {"total_saved": 0, "by_strategy": {}}

        total = sum(opt["saved"] for opt in self.optimizations)

        by_strategy = defaultdict(float)
        for opt in self.optimizations:
            by_strategy[opt["strategy"]] += opt["saved"]

        return {
            "total_saved": round(total, 2),
            "by_strategy": dict(by_strategy),
            "optimization_count": len(self.optimizations),
        }

    def track_feature_usage(self, feature: str, tokens: int, cost: float):
        """Track usage per feature"""
        self.feature_usage[feature]["tokens"] += tokens
        self.feature_usage[feature]["cost"] += cost

    def get_feature_costs(self) -> Dict[str, float]:
        """Get costs per feature"""
        return {feature: round(data["cost"], 2) for feature, data in self.feature_usage.items()}

    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for budget alerts"""
        alerts = []
        status = self.check_budget_status()

        # Check daily budget
        if self.budget.get("daily"):
            daily_percent = (1 - status["daily_remaining"] / self.budget["daily"]) * 100

            if daily_percent > 80:
                alerts.append(
                    {
                        "type": "budget_warning",
                        "level": "high" if daily_percent > 90 else "medium",
                        "message": f"Daily budget {daily_percent:.0f}% used",
                    }
                )

        return alerts

    def _init_model_pricing(self) -> Dict[str, Dict[str, float]]:
        """Initialize model pricing"""
        return {
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "gpt-3.5": {"input": 0.0015, "output": 0.002},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "claude": {"input": 0.01, "output": 0.02},
        }

    def _get_model_suitability(self, model: str) -> str:
        """Get model suitability description"""
        suitability = {
            "gpt-3.5-turbo": "Simple tasks, high speed",
            "gpt-3.5": "General tasks, good balance",
            "gpt-4": "Complex reasoning, high quality",
            "claude": "Long context, analysis",
        }
        return suitability.get(model, "General purpose")
