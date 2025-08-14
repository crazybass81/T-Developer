"""Test Fitness Calculator and Evaluation Dashboard - Day 44-45"""
from typing import Any, Dict

import pytest


def test_fitness_calculator():
    """Test fitness calculation"""
    from src.evolution.fitness_calculator import FitnessCalculator

    calculator = FitnessCalculator()

    # Test with comprehensive metrics
    good_metrics = {
        # Performance metrics
        "speed": 850,  # ms
        "memory": 45,  # %
        "scalability": 85,
        "efficiency": 80,
        # Quality metrics
        "code_quality": 85,
        "test_coverage": 90,
        "documentation": 75,
        "maintainability": 80,
        # Business metrics
        "roi": 150,
        "user_satisfaction": 85,
        "cost_efficiency": 75,
        "time_to_market": 70,
        # Evolution metrics
        "adaptability": 80,
        "mutation_success": 75,
        "crossover_compatibility": 85,
        "generation_improvement": 70,
        # Other metrics
        "environment_fit": 85,
        "novelty": 75,
        "error_rate": 2,
        "uptime": 98,
    }

    result = calculator.calculate("agent_001", good_metrics)

    assert result["agent_id"] == "agent_001"
    assert "component_scores" in result
    assert "total_fitness" in result
    assert result["total_fitness"] > 60  # Should be good
    assert result["fitness_class"] in ["elite", "superior", "average"]
    assert len(result["strengths"]) > 0

    # Test evolution potential
    potential = calculator.calculate_evolution_potential(
        "agent_001", result["total_fitness"], good_metrics
    )
    assert "improvement_potential" in potential
    assert "mutation_benefit" in potential
    assert "recommended_evolution" in potential

    # Test with poor metrics
    poor_metrics = {"speed": 100, "memory": 90, "test_coverage": 30, "error_rate": 8, "uptime": 92}

    result2 = calculator.calculate("agent_002", poor_metrics)
    assert result2["total_fitness"] < result["total_fitness"]
    assert len(result2["weaknesses"]) > 0

    # Test generation comparison
    calculator.calculate("agent_001", good_metrics)  # Gen 2
    comparison = calculator.compare_generations("agent_001", 0, 1)
    assert "improvement" in comparison
    assert "component_changes" in comparison

    # Test future prediction
    prediction = calculator.predict_future_fitness("agent_001", generations_ahead=5)
    assert 0 <= prediction <= 100

    # Test fitness report
    report = calculator.get_fitness_report("agent_001")
    assert report["agent_id"] == "agent_001"
    assert "current_fitness" in report
    assert "trend" in report
    assert "evolution_potential" in report

    print("✅ Fitness Calculator tests passed")


def test_evaluation_dashboard():
    """Test evaluation dashboard"""
    from src.evolution.evaluation_dashboard import EvaluationDashboard

    dashboard = EvaluationDashboard()

    # Update agent data
    agent_data = {"fitness": 75, "error_rate": 2.5, "performance": 80, "quality": 70}

    dashboard.update_agent("agent_001", agent_data)

    # Update generation
    generation_summary = {
        "agents": ["agent_001", "agent_002"],
        "average_fitness": 72.5,
        "best_fitness": 75,
        "worst_fitness": 70,
    }

    dashboard.update_generation(1, generation_summary)

    # Test overview
    overview = dashboard.get_overview()
    assert "active_agents" in overview
    assert "average_fitness" in overview
    assert "status" in overview
    assert overview["status"] in ["healthy", "warning", "critical"]

    # Test agent details
    details = dashboard.get_agent_details("agent_001")
    assert details["agent_id"] == "agent_001"
    assert "current_fitness" in details
    assert "trend" in details
    assert "performance_chart" in details

    # Test fitness decline alert
    declining_data = {
        "fitness": 60,  # Declined from 75
        "error_rate": 6,  # Increased
        "performance": 65,
    }

    dashboard.update_agent("agent_001", declining_data)

    # Check alerts
    alerts = dashboard.get_alerts()
    assert len(alerts) > 0  # Should have alerts for decline and error rate

    # Test top performers
    dashboard.update_agent("agent_002", {"fitness": 85, "error_rate": 1})
    dashboard.update_agent("agent_003", {"fitness": 65, "error_rate": 3})

    top = dashboard.get_top_performers(count=2)
    assert len(top) <= 2
    assert top[0]["fitness"] >= top[1]["fitness"] if len(top) == 2 else True

    # Test generation comparison
    dashboard.update_generation(
        2, {"agents": ["agent_001", "agent_002", "agent_003"], "average_fitness": 70}
    )

    comparison = dashboard.get_generation_comparison(1, 2)
    assert "fitness_change" in comparison
    assert "agent_change" in comparison

    # Test evolution summary
    summary = dashboard.get_evolution_summary()
    assert "total_generations" in summary
    assert "fitness_progression" in summary
    assert "evolution_rate" in summary

    # Test export
    export = dashboard.export_data()
    assert "overview" in export
    assert "top_performers" in export

    print("✅ Evaluation Dashboard tests passed")


def test_integrated_fitness_system():
    """Test integrated fitness and dashboard system"""
    from src.evolution.evaluation_dashboard import EvaluationDashboard
    from src.evolution.fitness_calculator import FitnessCalculator

    calculator = FitnessCalculator()
    dashboard = EvaluationDashboard()

    # Simulate evolution over multiple generations
    agents = ["agent_001", "agent_002", "agent_003"]

    for generation in range(5):
        generation_data = {
            "agents": [],
            "average_fitness": 0,
            "best_fitness": 0,
            "worst_fitness": 100,
        }

        for agent_id in agents:
            # Generate metrics (improving over time)
            base_fitness = 50 + generation * 5
            variation = hash(agent_id) % 20 - 10

            metrics = {
                "speed": 800 + generation * 20,
                "memory": max(30, 60 - generation * 5),
                "test_coverage": min(95, 60 + generation * 8),
                "error_rate": max(0.5, 5 - generation),
                "roi": 100 + generation * 30,
                "adaptability": 60 + generation * 5,
            }

            # Calculate fitness
            fitness_result = calculator.calculate(agent_id, metrics)

            # Update dashboard
            dashboard_data = {
                "fitness": fitness_result["total_fitness"],
                "error_rate": metrics["error_rate"],
                "generation": generation,
                **fitness_result["component_scores"],
            }

            dashboard.update_agent(agent_id, dashboard_data)

            # Update generation data
            generation_data["agents"].append(agent_id)
            generation_data["average_fitness"] += fitness_result["total_fitness"]
            generation_data["best_fitness"] = max(
                generation_data["best_fitness"], fitness_result["total_fitness"]
            )
            generation_data["worst_fitness"] = min(
                generation_data["worst_fitness"], fitness_result["total_fitness"]
            )

        # Finalize generation
        generation_data["average_fitness"] /= len(agents)
        dashboard.update_generation(generation, generation_data)

    # Verify evolution progress
    evolution_summary = dashboard.get_evolution_summary()
    assert evolution_summary["total_generations"] == 5
    assert evolution_summary["evolution_rate"] > 0  # Should show improvement

    # Check top performers
    top_performers = dashboard.get_top_performers(count=3)
    assert len(top_performers) == 3

    # Verify fitness reports
    for agent_id in agents:
        report = calculator.get_fitness_report(agent_id)
        assert report["evaluations"] == 5
        assert report["trend"] in ["improving", "stable", "declining"]

        # Check prediction
        predicted = report["predicted_fitness"]
        current = report["current_fitness"]
        assert abs(predicted - current) < 50  # Reasonable prediction

    # Check dashboard overview
    overview = dashboard.get_overview()
    assert overview["active_agents"] == 3
    assert overview["generations"] == 5
    assert overview["status"] == "healthy"  # Should be healthy with improvements

    print("✅ Integrated Fitness System tests passed")


def test_performance():
    """Test performance of fitness and dashboard system"""
    import time

    from src.evolution.evaluation_dashboard import EvaluationDashboard
    from src.evolution.fitness_calculator import FitnessCalculator

    # Test instantiation speed
    start = time.time()
    for _ in range(100):
        FitnessCalculator()
        EvaluationDashboard()
    elapsed = time.time() - start
    avg_time = elapsed / 200

    print(f"  Average instantiation time: {avg_time * 1000:.2f}ms")
    assert avg_time < 0.001  # Less than 1ms

    # Test calculation speed
    calculator = FitnessCalculator()
    metrics = {"speed": 500, "memory": 50, "test_coverage": 80}

    start = time.time()
    for i in range(100):
        calculator.calculate(f"agent_{i}", metrics)
    elapsed = time.time() - start

    print(f"  Average calculation time: {elapsed/100 * 1000:.2f}ms")
    assert elapsed / 100 < 0.01  # Less than 10ms

    # Test dashboard update speed
    dashboard = EvaluationDashboard()

    start = time.time()
    for i in range(100):
        dashboard.update_agent(f"agent_{i}", {"fitness": 70 + i % 30})
    elapsed = time.time() - start

    print(f"  Average dashboard update time: {elapsed/100 * 1000:.2f}ms")
    assert elapsed / 100 < 0.005  # Less than 5ms

    print("✅ Performance tests passed")


if __name__ == "__main__":
    print("🧪 Testing Day 44-45: Fitness Calculator and Evaluation Dashboard...")
    print("=" * 50)

    test_fitness_calculator()
    test_evaluation_dashboard()
    test_integrated_fitness_system()
    test_performance()

    print("\n" + "=" * 50)
    print("✅ All Day 44-45 tests passed!")
    print("Fitness calculation and dashboard system operational")
