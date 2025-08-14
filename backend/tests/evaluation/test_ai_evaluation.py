"""Test AI-based Evaluation Engine - Day 43"""
from typing import Any, Dict

import pytest


def test_ai_evaluator():
    """Test AI-based evaluation"""
    from src.evaluation.ai_evaluator import AIEvaluator

    evaluator = AIEvaluator()

    # Test with good code
    good_code = '''
class DataProcessor:
    """Process data with error handling and validation."""

    def __init__(self):
        self.processed_count = 0
        self.errors = []

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data with validation."""
        try:
            if not data:
                raise ValueError("Empty data")

            # Validate and transform
            result = {
                "id": data.get("id"),
                "value": data.get("value", 0) * 2,
                "status": "processed"
            }

            self.processed_count += 1
            return result

        except Exception as e:
            self.errors.append(str(e))
            raise
    '''

    result = evaluator.evaluate("agent_001", good_code)

    assert result["agent_id"] == "agent_001"
    assert "ai_scores" in result
    assert "consensus_score" in result
    assert result["consensus_score"] > 5  # Should be decent
    assert result["evolution_readiness"] in [
        "highly_ready",
        "ready",
        "conditionally_ready",
        "needs_improvement",
        "not_ready",
    ]
    assert len(result["recommendations"]) <= 3

    # Test multi-model consensus
    consensus = evaluator.get_multi_model_consensus("agent_001", good_code)
    assert consensus["agent_id"] == "agent_001"
    assert len(consensus["models_used"]) == 3
    assert consensus["agreement_level"] >= 0
    assert consensus["final_readiness"] in [
        "highly_ready",
        "ready",
        "conditionally_ready",
        "needs_improvement",
        "not_ready",
    ]

    # Test with poor code
    poor_code = """
def x(d):
    return d * 2
    """

    result2 = evaluator.evaluate("agent_002", poor_code)
    assert result2["consensus_score"] < result["consensus_score"]  # Should be worse
    assert len(result2["weaknesses"]) > 0

    print("✅ AI Evaluator tests passed")


def test_evolution_scorer():
    """Test evolution fitness scoring"""
    from src.evaluation.evolution_scorer import EvolutionScorer

    scorer = EvolutionScorer()

    # Test with good metrics
    good_metrics = {
        "error_resilience": 85,
        "resource_efficiency": 80,
        "adaptation_speed": 75,
        "code_quality": 90,
        "modularity": 85,
        "interface_compatibility": 80,
        "novelty_score": 70,
        "feature_diversity": 75,
        "solution_creativity": 65,
        "speed_score": 85,
        "memory_score": 80,
        "scalability_score": 75,
        "interoperability": 85,
        "api_stability": 90,
        "documentation_quality": 80,
    }

    result = scorer.calculate_fitness("agent_001", good_metrics, generation=1)

    assert result["agent_id"] == "agent_001"
    assert result["generation"] == 1
    assert "component_scores" in result
    assert result["total_fitness"] > 70  # Good fitness
    assert result["evolution_class"] in ["elite", "breeder"]
    assert result["mutation_probability"] > 0
    assert result["crossover_priority"] > 0

    # Test with poor metrics
    poor_metrics = {
        "error_resilience": 30,
        "resource_efficiency": 25,
        "code_quality": 35,
        "speed_score": 20,
        "memory_score": 30,
    }

    result2 = scorer.calculate_fitness("agent_002", poor_metrics, generation=1)
    assert result2["total_fitness"] < 50
    assert result2["evolution_class"] in ["mutable", "eliminate"]

    # Test parent selection
    parents = scorer.select_parents(generation=1, count=2)
    assert len(parents) <= 2
    if len(parents) == 2:
        assert parents[0]["evolution_class"] in ["elite", "breeder"]

    # Test offspring potential
    if len(parents) == 2:
        potential = scorer.calculate_offspring_potential(parents[0], parents[1])
        assert potential > 0
        assert potential <= 100

    # Test generation summary
    summary = scorer.get_generation_summary(1)
    assert summary["generation"] == 1
    assert summary["population_size"] >= 2
    assert "average_fitness" in summary
    assert "class_distribution" in summary

    print("✅ Evolution Scorer tests passed")


def test_adaptation_analyzer():
    """Test adaptation analysis"""
    from src.evaluation.adaptation_analyzer import AdaptationAnalyzer

    analyzer = AdaptationAnalyzer()

    # Test with adaptable state
    good_state = {
        "agent_id": "agent_001",
        "modularity": 0.8,
        "test_coverage": 0.85,
        "complexity": 8,
        "documentation": 0.7,
        "performance_score": 75,
        "efficiency": 70,
        "security_score": 85,
    }

    result = analyzer.analyze("agent_001", good_state, environment="high_load")

    assert result["agent_id"] == "agent_001"
    assert result["environment"] == "high_load"
    assert result["adaptation_score"] > 60  # Good adaptability
    assert len(result["recommended_mutations"]) > 0
    assert "risk_assessment" in result
    assert result["expected_improvement"] > 0
    assert result["strategy"] in ["incremental", "aggressive", "adaptive", "conservative"]

    # Test mutation recommendations
    mutations = result["recommended_mutations"]
    if mutations:
        assert all("type" in m for m in mutations)
        assert all("priority" in m for m in mutations)
        assert all("risk_level" in m for m in mutations)

    # Test with poor state
    poor_state = {
        "agent_id": "agent_002",
        "modularity": 0.3,
        "test_coverage": 0.4,
        "complexity": 20,
        "documentation": 0.2,
    }

    result2 = analyzer.analyze("agent_002", poor_state, environment="stable")
    assert result2["adaptation_score"] < result["adaptation_score"]

    # Test adaptation success prediction
    proposed = ["optimization", "caching", "refactoring"]
    success_prob = analyzer.predict_adaptation_success("agent_001", proposed)
    assert 0 <= success_prob <= 1

    # Test adaptation report
    report = analyzer.get_adaptation_report("agent_001")
    assert report["agent_id"] == "agent_001"
    assert report["total_adaptations"] >= 1
    assert "average_score" in report
    assert "preferred_strategy" in report

    print("✅ Adaptation Analyzer tests passed")


def test_integrated_ai_evaluation():
    """Test integrated AI evaluation system"""
    from src.evaluation.adaptation_analyzer import AdaptationAnalyzer
    from src.evaluation.ai_evaluator import AIEvaluator
    from src.evaluation.evolution_scorer import EvolutionScorer

    # Initialize components
    ai_eval = AIEvaluator()
    evo_scorer = EvolutionScorer()
    adapt_analyzer = AdaptationAnalyzer()

    # Sample agent code
    agent_code = '''
import asyncio
from typing import Dict, Any

class SmartAgent:
    """Intelligent agent with adaptation capabilities."""

    def __init__(self):
        self.state = {}
        self.performance_metrics = {}

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input with async support."""
        try:
            # Validate input
            if not input_data:
                raise ValueError("Invalid input")

            # Process asynchronously
            result = await self._async_process(input_data)

            # Update metrics
            self._update_metrics(result)

            return result

        except Exception as e:
            return {"error": str(e)}

    async def _async_process(self, data: Dict) -> Dict:
        """Async processing logic."""
        await asyncio.sleep(0.01)
        return {"processed": data}

    def _update_metrics(self, result: Dict):
        """Update performance metrics."""
        self.performance_metrics["processed"] = self.performance_metrics.get("processed", 0) + 1
    '''

    # Step 1: AI Evaluation
    ai_result = ai_eval.evaluate("smart_agent", agent_code)
    assert ai_result["consensus_score"] > 6  # Should be good

    # Step 2: Evolution Scoring
    metrics = {
        "error_resilience": ai_result["consensus_score"] * 10,
        "code_quality": ai_result["ai_scores"]["code_quality"]["average"] * 10,
        "modularity": 75,
        "novelty_score": 65,
        "speed_score": 70,
        "api_stability": 80,
    }

    evo_result = evo_scorer.calculate_fitness("smart_agent", metrics, generation=5)
    assert evo_result["total_fitness"] > 50

    # Step 3: Adaptation Analysis
    state = {
        "agent_id": "smart_agent",
        "modularity": 0.75,
        "test_coverage": 0.7,
        "complexity": 10,
        "performance_score": evo_result["total_fitness"],
    }

    adapt_result = adapt_analyzer.analyze("smart_agent", state, environment="rapid_change")
    assert adapt_result["adaptation_score"] > 50

    # Combined fitness assessment
    combined_fitness = {
        "agent_id": "smart_agent",
        "ai_evaluation": ai_result["consensus_score"],
        "evolution_fitness": evo_result["total_fitness"],
        "adaptation_potential": adapt_result["adaptation_score"],
        "overall_fitness": (
            ai_result["consensus_score"]
            + evo_result["total_fitness"]
            + adapt_result["adaptation_score"]
        )
        / 3,
        "evolution_ready": evo_result["evolution_class"] in ["elite", "breeder"],
        "recommended_strategy": adapt_result["strategy"],
    }

    assert combined_fitness["overall_fitness"] > 40
    assert combined_fitness["evolution_ready"] in [True, False]

    print("✅ Integrated AI Evaluation tests passed")


def test_evaluation_performance():
    """Test AI evaluation performance"""
    import time

    from src.evaluation.adaptation_analyzer import AdaptationAnalyzer
    from src.evaluation.ai_evaluator import AIEvaluator
    from src.evaluation.evolution_scorer import EvolutionScorer

    # Test instantiation speed
    start = time.time()
    for _ in range(100):
        AIEvaluator()
        EvolutionScorer()
        AdaptationAnalyzer()
    elapsed = time.time() - start
    avg_time = elapsed / 300

    print(f"  Average instantiation time: {avg_time * 1000:.2f}ms")
    assert avg_time < 0.001  # Less than 1ms

    # Test evaluation speed
    ai_eval = AIEvaluator()
    code = "def test(): return 42"

    start = time.time()
    for _ in range(100):
        ai_eval.evaluate(f"agent_{_}", code)
    elapsed = time.time() - start

    print(f"  Average AI evaluation time: {elapsed/100 * 1000:.2f}ms")
    assert elapsed / 100 < 0.01  # Less than 10ms

    print("✅ AI Evaluation Performance tests passed")


if __name__ == "__main__":
    print("🧪 Testing Day 43: AI-based Evaluation Engine...")
    print("=" * 50)

    test_ai_evaluator()
    test_evolution_scorer()
    test_adaptation_analyzer()
    test_integrated_ai_evaluation()
    test_evaluation_performance()

    print("\n" + "=" * 50)
    print("✅ All Day 43 tests passed!")
    print("AI-based evaluation engine is operational")
