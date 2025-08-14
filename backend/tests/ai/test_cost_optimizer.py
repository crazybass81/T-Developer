"""
CostOptimizer Tests - Day 32
Tests for AI cost optimization
"""

import pytest

from src.ai.cost_optimizer import CostOptimizer


class TestCostOptimizer:
    """Tests for CostOptimizer"""

    @pytest.fixture
    def optimizer(self):
        """Create CostOptimizer instance"""
        return CostOptimizer()

    @pytest.fixture
    def usage_data(self):
        """Sample usage data"""
        return {
            "model": "gpt-4",
            "input_tokens": 1000,
            "output_tokens": 500,
            "requests": 100,
        }

    def test_optimizer_initialization(self, optimizer):
        """Test CostOptimizer initialization"""
        assert optimizer is not None
        assert hasattr(optimizer, "models")
        assert hasattr(optimizer, "usage_history")

    def test_calculate_cost(self, optimizer, usage_data):
        """Test cost calculation"""
        cost = optimizer.calculate_cost(usage_data)

        assert "total_cost" in cost
        assert "input_cost" in cost
        assert "output_cost" in cost
        assert cost["total_cost"] > 0

    def test_optimize_model_selection(self, optimizer):
        """Test model selection optimization"""
        task = {
            "type": "code_generation",
            "complexity": "medium",
            "max_budget": 1.0,
        }

        recommendation = optimizer.optimize_model_selection(task)

        assert "model" in recommendation
        assert "estimated_cost" in recommendation
        assert recommendation["estimated_cost"] <= task["max_budget"]

    def test_batch_optimization(self, optimizer):
        """Test batch processing optimization"""
        requests = [{"prompt": f"Request {i}"} for i in range(10)]

        optimized = optimizer.optimize_batch(requests)

        assert "batches" in optimized
        assert "estimated_savings" in optimized
        assert optimized["estimated_savings"] >= 0

    def test_cache_strategy(self, optimizer):
        """Test caching strategy"""
        queries = ["Common query"] * 5 + ["Unique query"] * 2

        strategy = optimizer.recommend_cache_strategy(queries)

        assert "cache_candidates" in strategy
        assert "estimated_hit_rate" in strategy
        assert len(strategy["cache_candidates"]) > 0

    def test_usage_tracking(self, optimizer, usage_data):
        """Test usage tracking"""
        optimizer.track_usage(usage_data)

        stats = optimizer.get_usage_stats()
        assert stats["total_requests"] >= 1
        assert stats["total_tokens"] > 0

    def test_budget_monitoring(self, optimizer):
        """Test budget monitoring"""
        optimizer.set_budget(daily=10.0, monthly=250.0)

        status = optimizer.check_budget_status()
        assert "daily_remaining" in status
        assert "monthly_remaining" in status
        assert status["within_budget"] is True

    def test_cost_forecast(self, optimizer):
        """Test cost forecasting"""
        # Add historical data
        for i in range(7):
            optimizer.track_usage(
                {
                    "model": "gpt-3.5",
                    "input_tokens": 1000,
                    "output_tokens": 500,
                    "requests": 50,
                }
            )

        forecast = optimizer.forecast_costs(days=30)

        assert "predicted_cost" in forecast
        assert "confidence" in forecast
        assert forecast["predicted_cost"] > 0

    def test_optimization_recommendations(self, optimizer):
        """Test optimization recommendations"""
        current_usage = {
            "models": {"gpt-4": 0.7, "gpt-3.5": 0.3},
            "average_prompt_length": 500,
            "cache_hit_rate": 0.1,
        }

        recommendations = optimizer.get_recommendations(current_usage)

        assert len(recommendations) > 0
        assert all("action" in r for r in recommendations)
        assert all("potential_savings" in r for r in recommendations)

    def test_model_comparison(self, optimizer):
        """Test model cost comparison"""
        comparison = optimizer.compare_models(task_type="text_generation", tokens=1000)

        assert len(comparison) > 0
        assert all("model" in m for m in comparison)
        assert all("cost" in m for m in comparison)

    def test_token_optimization(self, optimizer):
        """Test token usage optimization"""
        prompt = "This is a very verbose and unnecessarily long prompt " * 10

        optimized = optimizer.optimize_tokens(prompt)

        assert "optimized_prompt" in optimized
        assert "tokens_saved" in optimized
        assert optimized["tokens_saved"] > 0

    def test_rate_limit_optimization(self, optimizer):
        """Test rate limit optimization"""
        requests = [{"priority": i % 3} for i in range(100)]

        scheduled = optimizer.optimize_rate_limits(requests, max_rpm=60)

        assert "schedule" in scheduled
        assert "estimated_time" in scheduled
        assert len(scheduled["schedule"]) > 0

    def test_fallback_strategy(self, optimizer):
        """Test fallback model strategy"""
        strategy = optimizer.create_fallback_strategy(primary="gpt-4", budget_threshold=0.8)

        assert "primary" in strategy
        assert "fallback" in strategy
        assert strategy["fallback"] != strategy["primary"]

    def test_cost_allocation(self, optimizer):
        """Test cost allocation across projects"""
        usage = [
            {"project": "A", "tokens": 1000, "model": "gpt-3.5"},
            {"project": "B", "tokens": 2000, "model": "gpt-4"},
            {"project": "A", "tokens": 500, "model": "gpt-3.5"},
        ]

        allocation = optimizer.allocate_costs(usage)

        assert "A" in allocation
        assert "B" in allocation
        assert allocation["B"] > allocation["A"]

    def test_anomaly_detection(self, optimizer):
        """Test cost anomaly detection"""
        # Normal usage
        for _ in range(10):
            optimizer.track_usage(
                {
                    "model": "gpt-3.5",
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "requests": 5,
                }
            )

        # Anomaly
        optimizer.track_usage(
            {
                "model": "gpt-4",
                "input_tokens": 10000,
                "output_tokens": 5000,
                "requests": 100,
            }
        )

        anomalies = optimizer.detect_anomalies()
        assert len(anomalies) > 0

    def test_savings_report(self, optimizer):
        """Test savings report generation"""
        optimizer.track_optimization("cache", saved=0.5)
        optimizer.track_optimization("batch", saved=0.3)

        report = optimizer.generate_savings_report()

        assert "total_saved" in report
        assert "by_strategy" in report
        assert report["total_saved"] >= 0.8

    def test_cost_per_feature(self, optimizer):
        """Test cost tracking per feature"""
        optimizer.track_feature_usage("search", tokens=100, cost=0.01)
        optimizer.track_feature_usage("generation", tokens=500, cost=0.05)

        costs = optimizer.get_feature_costs()

        assert "search" in costs
        assert "generation" in costs
        assert costs["generation"] > costs["search"]

    def test_budget_alerts(self, optimizer):
        """Test budget alert system"""
        optimizer.set_budget(daily=1.0)

        # Simulate usage near budget (each usage costs ~0.0022)
        for _ in range(400):  # This will exceed 80% of $1 budget
            optimizer.track_usage(
                {
                    "model": "gpt-3.5",
                    "input_tokens": 1000,
                    "output_tokens": 500,
                    "requests": 10,
                }
            )

        alerts = optimizer.check_alerts()
        assert len(alerts) > 0
        assert any("budget" in alert["type"] for alert in alerts)
