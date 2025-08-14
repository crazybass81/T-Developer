"""Test Multi-dimensional Evaluation System - Day 42"""
from typing import Any, Dict

import pytest


def test_performance_evaluator():
    """Test performance evaluation"""
    from src.evaluation.performance_evaluator import PerformanceEvaluator

    evaluator = PerformanceEvaluator()

    # Test with good performance metrics
    good_metrics = {
        "response_time": 100,  # ms
        "throughput": 800,  # req/sec
        "latency": 20,  # ms
        "cpu_usage": 45,  # %
        "memory_usage": 50,  # %
        "io_operations": 200,  # ops
        "concurrent_users": 750,
        "load_capacity": 7500,
        "elastic_scaling": 0.8,
        "error_rate": 0.5,  # %
        "crash_frequency": 0,
        "recovery_time": 30,  # seconds
        "cache_hit_rate": 85,  # %
        "query_optimization": 0.8,
        "resource_pooling": 0.75,
    }

    result = evaluator.evaluate("test_agent_001", good_metrics)

    assert result["agent_id"] == "test_agent_001"
    assert "dimensions" in result
    assert "overall_score" in result
    assert result["overall_score"] > 70  # Good performance
    assert len(result["recommendations"]) == 0 or result["recommendations"][0]["priority"] != "high"

    # Test with poor performance metrics
    poor_metrics = {
        "response_time": 2000,  # ms (slow)
        "throughput": 50,  # req/sec (low)
        "cpu_usage": 95,  # % (high)
        "memory_usage": 92,  # % (high)
        "error_rate": 15,  # % (high)
    }

    result2 = evaluator.evaluate("test_agent_002", poor_metrics)
    assert result2["overall_score"] < 50  # Poor performance
    assert len(result2["recommendations"]) > 0
    assert result2["recommendations"][0]["priority"] == "high"

    # Test comparison
    comparison = evaluator.compare_agents(["test_agent_001", "test_agent_002"])
    assert comparison["best_performer"] == "test_agent_001"

    # Test trends
    for i in range(5):
        evaluator.evaluate("test_agent_001", good_metrics)

    trends = evaluator.get_trends("test_agent_001", window=5)
    assert trends["overall_trend"] in ["stable", "improving", "degrading"]

    print("✅ Performance Evaluator tests passed")


def test_quality_evaluator():
    """Test quality evaluation"""
    from src.evaluation.quality_evaluator import QualityEvaluator

    evaluator = QualityEvaluator()

    # Test with high quality code
    good_code = '''
"""Module for processing user data with proper documentation."""
from typing import List, Dict, Any
import logging

class UserProcessor:
    """Process user data with validation and error handling."""

    def __init__(self):
        """Initialize the processor."""
        self.logger = logging.getLogger(__name__)
        self.processed_count = 0

    def process_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single user's data.

        Args:
            user_data: Dictionary containing user information

        Returns:
            Processed user data
        """
        try:
            # Validate input
            if not user_data or not isinstance(user_data, dict):
                raise ValueError("Invalid user data")

            # Process the data
            result = {
                "id": user_data.get("id"),
                "name": user_data.get("name", "").strip(),
                "processed": True
            }

            self.processed_count += 1
            return result

        except Exception as e:
            self.logger.error(f"Error processing user: {e}")
            raise

    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return {"processed": self.processed_count}
'''

    result = evaluator.evaluate("test_agent_001", good_code)

    assert result["agent_id"] == "test_agent_001"
    assert "dimensions" in result
    assert result["overall_score"] > 60  # Good quality
    assert "maintainability" in result["dimensions"]
    assert "reliability" in result["dimensions"]
    assert "documentation" in result["dimensions"]

    # Test with poor quality code
    poor_code = """
def proc(d):
    password = "hardcoded_password"
    query = f"SELECT * FROM users WHERE id = {d['id']}"
    x = d['n']
    y = x * 2
    z = y + 10
    if z > 100:
        if x > 50:
            if y > 75:
                return True
    return False
"""

    result2 = evaluator.evaluate("test_agent_002", poor_code)
    assert result2["overall_score"] < 50  # Poor quality
    assert len(result2["issues"]) > 0
    assert any(issue["type"] == "security" for issue in result2["issues"])
    assert len(result2["suggestions"]) > 0

    print("✅ Quality Evaluator tests passed")


def test_business_evaluator():
    """Test business value evaluation"""
    from src.evaluation.business_evaluator import BusinessEvaluator

    evaluator = BusinessEvaluator()

    # Test with high business value metrics
    good_metrics = {
        "conversion_rate": 6,  # %
        "average_order_value": 175,  # $
        "customer_lifetime_value": 1200,  # $
        "operational_cost": 4000,  # $/month
        "resource_utilization": 85,  # %
        "automation_rate": 75,  # %
        "user_rating": 4.6,  # stars
        "nps_score": 55,  # points
        "retention_rate": 92,  # %
        "task_completion_rate": 96,  # %
        "time_savings": 25,  # hours/week
        "throughput": 120,  # tasks/hour
        "feature_adoption": 65,  # %
        "competitive_advantage": 8.5,  # score
        "time_to_market": 25,  # days
    }

    result = evaluator.evaluate("test_agent_001", good_metrics)

    assert result["agent_id"] == "test_agent_001"
    assert "dimensions" in result
    assert result["overall_score"] > 70  # High business value
    assert result["roi_estimate"] > 0
    assert "value_proposition" in result
    assert "exceptional" in result["value_proposition"] or "strong" in result["value_proposition"]

    # Test revenue impact dimension
    assert "revenue_impact" in result["dimensions"]
    assert result["dimensions"]["revenue_impact"]["score"] > 70

    # Test with poor business metrics
    poor_metrics = {
        "conversion_rate": 1,  # % (low)
        "average_order_value": 50,  # $ (low)
        "operational_cost": 15000,  # $/month (high)
        "user_rating": 2.5,  # stars (low)
        "retention_rate": 40,  # % (low)
    }

    result2 = evaluator.evaluate("test_agent_002", poor_metrics)
    assert result2["overall_score"] < 50  # Low business value
    assert len(result2["recommendations"]) > 0
    assert result2["recommendations"][0]["priority"] in ["high", "medium"]

    # Test period comparison
    for i in range(10):
        evaluator.evaluate("test_agent_003", good_metrics)

    comparison = evaluator.compare_periods("test_agent_003", 0, 5)
    assert "improvement" in comparison
    assert "dimension_changes" in comparison

    print("✅ Business Evaluator tests passed")


def test_integrated_evaluation():
    """Test integrated multi-dimensional evaluation"""
    from src.evaluation.business_evaluator import BusinessEvaluator
    from src.evaluation.performance_evaluator import PerformanceEvaluator
    from src.evaluation.quality_evaluator import QualityEvaluator

    # Initialize all evaluators
    perf_eval = PerformanceEvaluator()
    qual_eval = QualityEvaluator()
    biz_eval = BusinessEvaluator()

    agent_id = "integrated_agent_001"

    # Performance metrics
    perf_metrics = {
        "response_time": 150,
        "throughput": 600,
        "cpu_usage": 55,
        "memory_usage": 60,
        "error_rate": 1.5,
    }

    # Quality code
    code = '''
def calculate_total(items: List[Dict]) -> float:
    """Calculate total with validation."""
    if not items:
        return 0.0
    try:
        return sum(item.get("price", 0) for item in items)
    except Exception as e:
        logging.error(f"Calculation error: {e}")
        return 0.0
'''

    # Business metrics
    biz_metrics = {
        "conversion_rate": 4.5,
        "operational_cost": 6000,
        "user_rating": 4.2,
        "retention_rate": 85,
    }

    # Evaluate across all dimensions
    perf_result = perf_eval.evaluate(agent_id, perf_metrics)
    qual_result = qual_eval.evaluate(agent_id, code)
    biz_result = biz_eval.evaluate(agent_id, biz_metrics)

    # Combine scores (weighted average)
    combined_score = (
        perf_result["overall_score"] * 0.3
        + qual_result["overall_score"] * 0.3
        + biz_result["overall_score"] * 0.4
    )

    assert combined_score > 50  # Above average across all dimensions

    # Create fitness profile
    fitness_profile = {
        "agent_id": agent_id,
        "performance": perf_result["overall_score"],
        "quality": qual_result["overall_score"],
        "business": biz_result["overall_score"],
        "combined": combined_score,
        "evolution_readiness": "ready" if combined_score > 60 else "needs_improvement",
    }

    assert fitness_profile["evolution_readiness"] in ["ready", "needs_improvement"]

    print("✅ Integrated Evaluation tests passed")


def test_evaluation_performance():
    """Test evaluation system performance"""
    import time

    from src.evaluation.business_evaluator import BusinessEvaluator
    from src.evaluation.performance_evaluator import PerformanceEvaluator
    from src.evaluation.quality_evaluator import QualityEvaluator

    # Test instantiation speed
    start = time.time()
    for _ in range(100):
        PerformanceEvaluator()
        QualityEvaluator()
        BusinessEvaluator()
    elapsed = time.time() - start
    avg_time = elapsed / 300  # 3 evaluators * 100 iterations

    print(f"  Average instantiation time: {avg_time * 1000:.2f}ms")
    assert avg_time < 0.001  # Less than 1ms per instantiation

    # Test evaluation speed
    perf_eval = PerformanceEvaluator()
    metrics = {"response_time": 100, "throughput": 500}

    start = time.time()
    for _ in range(100):
        perf_eval.evaluate(f"agent_{_}", metrics)
    elapsed = time.time() - start

    print(f"  Average evaluation time: {elapsed/100 * 1000:.2f}ms")
    assert elapsed / 100 < 0.01  # Less than 10ms per evaluation

    print("✅ Evaluation Performance tests passed")


if __name__ == "__main__":
    print("🧪 Testing Day 42: Multi-dimensional Evaluation System...")
    print("=" * 50)

    test_performance_evaluator()
    test_quality_evaluator()
    test_business_evaluator()
    test_integrated_evaluation()
    test_evaluation_performance()

    print("\n" + "=" * 50)
    print("✅ All Day 42 tests passed!")
    print("Multi-dimensional evaluation system is operational")
