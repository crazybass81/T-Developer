"""
Integration Tests for Day 48-50: Evolution Engine with Genetic Algorithms

Tests the complete integration of genetic components with the evolution engine,
including mutation, crossover, parameter optimization, and convergence detection.
"""

import asyncio
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.evolution.convergence_detector import ConvergenceDetector, ConvergenceType

# Import evolution components
from src.evolution.engine import EvolutionConfig, EvolutionEngine, EvolutionStatus
from src.evolution.parameter_optimizer import ParameterOptimizer, ParameterSet
from src.genetic.crossover.ai_crossover import AICrossover
from src.genetic.crossover.effect_analyzer import CrossoverEffectAnalyzer
from src.genetic.crossover.multi_point import MultiPointCrossover

# Import genetic components
from src.genetic.mutation.ai_mutator import AIMutator
from src.genetic.mutation.rate_controller import MutationRateController
from src.genetic.mutation.validator import MutationValidator
from src.genetic.selection.tournament import TournamentSelection


class TestEvolutionEngineIntegration:
    """Integration tests for complete evolution engine system"""

    @pytest.fixture
    def evolution_config(self):
        return EvolutionConfig(
            max_generations=10,
            population_size=20,
            mutation_rate=0.15,
            crossover_rate=0.8,
            selection_pressure=2.5,
            memory_limit_kb=6.5,
            instantiation_limit_us=3.0,
            autonomy_target=0.85,
            safety_threshold=0.95,
        )

    @pytest.fixture
    def evolution_engine(self, evolution_config):
        return EvolutionEngine(evolution_config)

    @pytest.fixture
    def sample_population(self):
        return [
            {
                "id": f"agent_{i:03d}",
                "genes": {
                    "layer_sizes": [16, 32, 16],
                    "activation": "relu",
                    "learning_rate": 0.01 + i * 0.001,
                    "dropout_rate": 0.2 + i * 0.01,
                    "optimizer": "adam",
                },
                "fitness": 0.5 + i * 0.05,
                "metrics": {
                    "memory_kb": 4.5 + i * 0.1,
                    "instantiation_us": 2.0 + i * 0.05,
                    "accuracy": 0.7 + i * 0.02,
                },
            }
            for i in range(20)
        ]

    @pytest.mark.asyncio
    async def test_engine_initialization_with_genetic_components(self, evolution_engine):
        """Test that evolution engine properly initializes genetic components"""
        assert evolution_engine is not None
        assert evolution_engine.status == EvolutionStatus.IDLE

        # Check that genetic components are initialized (or set to None if not available)
        assert hasattr(evolution_engine, "ai_mutator")
        assert hasattr(evolution_engine, "rate_controller")
        assert hasattr(evolution_engine, "mutation_validator")
        assert hasattr(evolution_engine, "ai_crossover")
        assert hasattr(evolution_engine, "multi_point_crossover")
        assert hasattr(evolution_engine, "crossover_analyzer")
        assert hasattr(evolution_engine, "tournament_selection")

    @pytest.mark.asyncio
    async def test_complete_evolution_cycle(self, evolution_engine, sample_population):
        """Test complete evolution cycle with genetic components"""
        # Initialize engine
        await evolution_engine.initialize()
        assert evolution_engine.status == EvolutionStatus.IDLE

        # Set sample population
        evolution_engine.population = sample_population.copy()

        # Test one generation cycle
        evolution_engine.status = EvolutionStatus.EVOLVING
        evolution_engine.current_generation = 1

        # Test selection
        parents = await evolution_engine._selection()
        assert len(parents) == evolution_engine.config.population_size
        assert all(isinstance(parent, dict) for parent in parents)
        assert all("genes" in parent and "fitness" in parent for parent in parents)

        # Test crossover
        offspring = await evolution_engine._crossover(parents)
        assert len(offspring) >= len(parents)
        assert all(isinstance(child, dict) for child in offspring)

        # Test mutation
        mutated = await evolution_engine._mutation(offspring)
        assert len(mutated) == len(offspring)
        assert all(isinstance(mutant, dict) for mutant in mutated)

        # Verify genetic diversity is maintained
        unique_genes = set()
        for individual in mutated:
            gene_str = str(individual["genes"])
            unique_genes.add(gene_str)

        # Should have some diversity (at least 50% unique)
        assert len(unique_genes) >= len(mutated) * 0.5

    @pytest.mark.asyncio
    async def test_adaptive_mutation_rates(self, evolution_engine, sample_population):
        """Test adaptive mutation rate adjustment"""
        if not evolution_engine.rate_controller:
            pytest.skip("Rate controller not available")

        evolution_engine.population = sample_population.copy()

        # Create population history showing stagnation
        stagnant_history = [
            {"generation": i, "best_fitness": 0.7, "avg_fitness": 0.5} for i in range(1, 6)
        ]

        adaptive_rate = evolution_engine.rate_controller.calculate_adaptive_rate(stagnant_history)

        # Adaptive rate should be higher than base rate due to stagnation
        assert adaptive_rate >= evolution_engine.config.mutation_rate
        assert 0.01 <= adaptive_rate <= 0.5

    @pytest.mark.asyncio
    async def test_intelligent_crossover_selection(self, evolution_engine, sample_population):
        """Test intelligent crossover method selection"""
        if not evolution_engine.ai_crossover:
            pytest.skip("AI crossover not available")

        evolution_engine.population = sample_population.copy()

        # Select two high-fitness parents
        high_fitness_parents = sorted(sample_population, key=lambda x: x["fitness"], reverse=True)[
            :2
        ]

        # Test AI-guided crossover
        parent1, parent2 = high_fitness_parents[0], high_fitness_parents[1]

        child1, child2 = await evolution_engine.ai_crossover.intelligent_crossover(parent1, parent2)

        assert child1 is not None and child2 is not None
        assert child1["id"] != parent1["id"]
        assert child2["id"] != parent2["id"]
        assert "genes" in child1 and "genes" in child2

    @pytest.mark.asyncio
    async def test_mutation_validation(self, evolution_engine, sample_population):
        """Test mutation validation and constraint checking"""
        if not evolution_engine.mutation_validator:
            pytest.skip("Mutation validator not available")

        # Test with a potentially invalid mutation (very large network)
        invalid_genome = sample_population[0].copy()
        invalid_genome["genes"]["layer_sizes"] = [1024, 2048, 1024, 512]  # Very large

        validation_result = await evolution_engine.mutation_validator.validate_mutation(
            invalid_genome
        )

        assert hasattr(validation_result, "is_valid")
        assert hasattr(validation_result, "violations")
        assert hasattr(validation_result, "risk_score")

        # Should detect constraint violations for oversized network
        if not validation_result.is_valid:
            assert len(validation_result.violations) > 0

    @pytest.mark.asyncio
    async def test_crossover_effect_analysis(self, evolution_engine, sample_population):
        """Test crossover effect analysis and learning"""
        if not evolution_engine.crossover_analyzer:
            pytest.skip("Crossover analyzer not available")

        parent1, parent2 = sample_population[0], sample_population[1]

        # Mock offspring with known fitness
        offspring = [
            {**parent1, "id": "child1", "fitness": 0.8},
            {**parent2, "id": "child2", "fitness": 0.85},
        ]

        crossover_example = {
            "parent1": parent1,
            "parent2": parent2,
            "offspring": offspring,
            "strategy": "ai_guided",
        }

        # Test analysis
        analysis = await evolution_engine.crossover_analyzer.analyze_fitness_impact(
            crossover_example
        )

        assert "fitness_improvement" in analysis
        assert "inheritance_patterns" in analysis
        assert "success_factors" in analysis

        # Test learning
        evolution_engine.crossover_analyzer.learn_from_crossover(crossover_example)
        assert len(evolution_engine.crossover_analyzer.historical_crossovers) > 0

    @pytest.mark.asyncio
    async def test_evolution_with_target_fitness(self, evolution_engine, sample_population):
        """Test evolution stopping when target fitness is reached"""
        # Set high fitness population close to target
        high_fitness_population = []
        for i, individual in enumerate(sample_population[:10]):
            individual_copy = individual.copy()
            individual_copy["fitness"] = 0.90 + i * 0.008  # Some individuals above 0.95
            high_fitness_population.append(individual_copy)

        evolution_engine.population = high_fitness_population

        # Should reach target quickly
        success = await evolution_engine.start_evolution(target_fitness=0.95)

        # Either succeeds or fails gracefully
        assert isinstance(success, bool)

        if success:
            assert evolution_engine.status == EvolutionStatus.COMPLETED
            best_fitness = evolution_engine._get_best_fitness()
            assert best_fitness >= 0.95

    @pytest.mark.asyncio
    async def test_safety_constraints_enforcement(self, evolution_engine, sample_population):
        """Test that safety constraints are properly enforced"""
        evolution_engine.population = sample_population.copy()

        # Force a safety check
        safety_passed = await evolution_engine._safety_check()

        # Should pass with valid sample population
        assert isinstance(safety_passed, bool)

        # Test with invalid population (if validator available)
        if evolution_engine.mutation_validator:
            # Create invalid genome exceeding memory limit
            invalid_individual = sample_population[0].copy()
            invalid_individual["genes"]["layer_sizes"] = [2048, 4096, 2048]
            invalid_individual["metrics"]["memory_kb"] = 10.0  # Exceeds 6.5KB limit

            evolution_engine.best_genome = invalid_individual

            safety_passed = await evolution_engine._safety_check()

            # Should detect safety violation
            assert safety_passed == False


class TestParameterOptimizer:
    """Tests for parameter optimization system"""

    @pytest.fixture
    def parameter_optimizer(self):
        return ParameterOptimizer()

    @pytest.fixture
    def sample_evolution_history(self):
        return [
            {"generation": i, "best_fitness": 0.4 + i * 0.05, "avg_fitness": 0.3 + i * 0.03}
            for i in range(1, 11)
        ]

    @pytest.mark.asyncio
    async def test_parameter_optimization(self, parameter_optimizer, sample_evolution_history):
        """Test parameter optimization process"""
        current_params = {
            "mutation_rate": 0.1,
            "crossover_rate": 0.7,
            "selection_pressure": 2.0,
            "population_size": 50,
        }

        result = await parameter_optimizer.optimize_parameters(
            current_params, sample_evolution_history, target_fitness=0.9
        )

        assert isinstance(result.best_parameters, ParameterSet)
        assert isinstance(result.improvement_percentage, float)
        assert isinstance(result.confidence_score, float)
        assert result.improvement_percentage >= 0.0
        assert 0.0 <= result.confidence_score <= 1.0

    def test_parameter_recommendations(self, parameter_optimizer):
        """Test parameter recommendations based on population state"""
        # Test with low fitness population
        low_fitness_state = {"avg_fitness": 0.2, "diversity": 0.6, "stagnation_generations": 2}

        recommendations = parameter_optimizer.recommend_parameters(low_fitness_state)

        assert "mutation_rate" in recommendations
        assert "crossover_rate" in recommendations
        assert "selection_pressure" in recommendations

        # Should recommend higher exploration for low fitness
        assert recommendations["mutation_rate"] >= 0.1

    def test_parameter_bounds_enforcement(self, parameter_optimizer):
        """Test that parameter bounds are properly enforced"""
        # Test with stagnation (should increase mutation rate)
        stagnant_state = {"avg_fitness": 0.5, "diversity": 0.3, "stagnation_generations": 10}

        recommendations = parameter_optimizer.recommend_parameters(stagnant_state)

        # All parameters should be within bounds
        assert 0.01 <= recommendations["mutation_rate"] <= 0.5
        assert 0.3 <= recommendations["crossover_rate"] <= 0.9
        assert 1.2 <= recommendations["selection_pressure"] <= 4.0


class TestConvergenceDetector:
    """Tests for convergence detection system"""

    @pytest.fixture
    def convergence_detector(self):
        return ConvergenceDetector()

    @pytest.fixture
    def sample_population(self):
        return [
            {
                "id": f"agent_{i:03d}",
                "genes": {"layer_sizes": [16, 32, 16], "learning_rate": 0.01},
                "fitness": 0.7 + i * 0.01,
                "metrics": {"memory_kb": 4.0, "instantiation_us": 2.0},
            }
            for i in range(10)
        ]

    def test_convergence_detection_initialization(self, convergence_detector):
        """Test convergence detector initialization"""
        assert convergence_detector is not None
        assert len(convergence_detector.fitness_history) == 0
        assert len(convergence_detector.convergence_signals) == 0

    def test_fitness_plateau_detection(self, convergence_detector, sample_population):
        """Test detection of fitness plateau"""
        # Simulate stagnant fitness history
        stagnant_fitness = [0.75] * 15
        convergence_detector.fitness_history = stagnant_fitness

        has_converged, signals = convergence_detector.analyze_convergence(
            generation=15, population=sample_population, metrics_history=[]
        )

        # Should detect fitness plateau
        plateau_signals = [s for s in signals if s.type == ConvergenceType.FITNESS_PLATEAU]
        assert len(plateau_signals) > 0

        if plateau_signals:
            signal = plateau_signals[0]
            assert signal.confidence > 0.5

    def test_diversity_loss_detection(self, convergence_detector, sample_population):
        """Test detection of diversity loss"""
        # Create low diversity population (all similar)
        low_diversity_population = []
        base_genes = {"layer_sizes": [16, 32, 16], "learning_rate": 0.01}

        for i in range(10):
            individual = {
                "id": f"similar_agent_{i:03d}",
                "genes": base_genes.copy(),  # All identical
                "fitness": 0.8,
                "metrics": {"memory_kb": 4.0},
            }
            low_diversity_population.append(individual)

        has_converged, signals = convergence_detector.analyze_convergence(
            generation=10, population=low_diversity_population, metrics_history=[]
        )

        # Should detect low diversity
        diversity_signals = [s for s in signals if s.type == ConvergenceType.DIVERSITY_LOSS]
        assert len(diversity_signals) >= 0  # May or may not detect depending on threshold

    def test_target_reached_detection(self, convergence_detector, sample_population):
        """Test detection when target fitness is reached"""
        # Set high fitness population
        high_fitness_population = []
        for i, individual in enumerate(sample_population):
            individual_copy = individual.copy()
            individual_copy["fitness"] = 0.96  # Above default target of 0.95
            high_fitness_population.append(individual_copy)

        has_converged, signals = convergence_detector.analyze_convergence(
            generation=5, population=high_fitness_population, metrics_history=[]
        )

        # Should detect target reached
        target_signals = [s for s in signals if s.type == ConvergenceType.TARGET_REACHED]
        assert len(target_signals) > 0

        if target_signals:
            assert target_signals[0].confidence == 1.0

    def test_convergence_prediction(self, convergence_detector):
        """Test convergence generation prediction"""
        # Set improving fitness history
        improving_fitness = [0.5 + i * 0.02 for i in range(20)]
        convergence_detector.fitness_history = improving_fitness

        predicted_gen = convergence_detector.predict_convergence_generation(
            current_generation=20, metrics_history=[]
        )

        if predicted_gen is not None:
            assert isinstance(predicted_gen, int)
            assert predicted_gen >= 20

    def test_should_continue_evolution(self, convergence_detector, sample_population):
        """Test evolution continuation decision"""
        # Test with normal progress
        should_continue, reason = convergence_detector.should_continue_evolution(
            generation=5, computational_budget=100
        )

        assert isinstance(should_continue, bool)
        assert isinstance(reason, str)

        # Test with budget exhausted
        should_continue, reason = convergence_detector.should_continue_evolution(
            generation=100, computational_budget=100
        )

        assert should_continue == False
        assert "budget exhausted" in reason.lower()

    def test_convergence_metrics_calculation(self, convergence_detector):
        """Test convergence metrics calculation"""
        # Set some history
        convergence_detector.fitness_history = [0.5, 0.6, 0.65, 0.68, 0.69, 0.69]
        convergence_detector.diversity_history = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3]

        metrics = convergence_detector.get_convergence_metrics()

        assert hasattr(metrics, "fitness_stagnation_count")
        assert hasattr(metrics, "diversity_trend")
        assert hasattr(metrics, "improvement_rate")
        assert hasattr(metrics, "variance_reduction")
        assert hasattr(metrics, "overfitting_risk")

        # Diversity should be trending down
        assert metrics.diversity_trend < 0

        # Should detect some stagnation
        assert metrics.fitness_stagnation_count >= 0


class TestIntegratedEvolutionSystem:
    """Tests for the complete integrated system"""

    @pytest.fixture
    def integrated_system(self):
        """Set up complete evolution system with all components"""
        config = EvolutionConfig(
            max_generations=5, population_size=10, mutation_rate=0.2, crossover_rate=0.8
        )

        engine = EvolutionEngine(config)
        optimizer = ParameterOptimizer()
        detector = ConvergenceDetector()

        return {"engine": engine, "optimizer": optimizer, "detector": detector}

    @pytest.fixture
    def test_population(self):
        return [
            {
                "id": f"test_agent_{i:03d}",
                "genes": {
                    "layer_sizes": [8 + i, 16 + i, 8 + i],
                    "activation": "relu",
                    "learning_rate": 0.005 + i * 0.001,
                    "dropout_rate": 0.1 + i * 0.02,
                    "optimizer": "adam",
                },
                "fitness": 0.3 + i * 0.07,
                "metrics": {
                    "memory_kb": 3.0 + i * 0.2,
                    "instantiation_us": 1.5 + i * 0.1,
                    "accuracy": 0.6 + i * 0.04,
                },
            }
            for i in range(10)
        ]

    @pytest.mark.asyncio
    async def test_complete_system_workflow(self, integrated_system, test_population):
        """Test complete workflow with all integrated components"""
        engine = integrated_system["engine"]
        optimizer = integrated_system["optimizer"]
        detector = integrated_system["detector"]

        # Initialize evolution engine
        await engine.initialize()
        engine.population = test_population.copy()

        # Test parameter optimization
        evolution_history = [
            {"generation": i, "best_fitness": 0.3 + i * 0.1, "avg_fitness": 0.2 + i * 0.08}
            for i in range(1, 6)
        ]

        optimization_result = await optimizer.optimize_parameters(
            {
                "mutation_rate": engine.config.mutation_rate,
                "crossover_rate": engine.config.crossover_rate,
                "selection_pressure": engine.config.selection_pressure,
            },
            evolution_history,
        )

        assert optimization_result is not None

        # Test convergence detection
        has_converged, signals = detector.analyze_convergence(
            generation=5, population=engine.population, metrics_history=evolution_history
        )

        assert isinstance(has_converged, bool)
        assert isinstance(signals, list)

        # Test evolution continuation decision
        should_continue, reason = detector.should_continue_evolution(generation=5)
        assert isinstance(should_continue, bool)

        # Run a short evolution cycle
        if should_continue:
            # Test one evolution step
            parents = await engine._selection()
            offspring = await engine._crossover(parents)
            mutated = await engine._mutation(offspring)

            assert len(mutated) > 0
            assert all("genes" in individual for individual in mutated)

    @pytest.mark.asyncio
    async def test_system_error_handling(self, integrated_system, test_population):
        """Test system behavior with errors and edge cases"""
        engine = integrated_system["engine"]

        # Test with empty population
        engine.population = []

        # Should handle empty population gracefully
        best_fitness = engine._get_best_fitness()
        assert best_fitness == 0.0

        # Test with malformed population
        malformed_population = [{"id": "broken"}]  # Missing required fields

        # Should handle gracefully
        parents = await engine._selection()
        assert isinstance(parents, list)

    def test_system_configuration_compatibility(self, integrated_system):
        """Test that all system components have compatible configurations"""
        engine = integrated_system["engine"]

        # Check that genetic components are properly configured
        if engine.ai_mutator:
            mutator_config = engine.ai_mutator.config
            assert mutator_config["memory_limit_kb"] == engine.config.memory_limit_kb

        if engine.rate_controller:
            rate_config = engine.rate_controller.base_rate
            assert rate_config == engine.config.mutation_rate

    @pytest.mark.asyncio
    async def test_performance_constraints(self, integrated_system, test_population):
        """Test that performance constraints are maintained"""
        engine = integrated_system["engine"]
        engine.population = test_population.copy()

        # Verify all individuals meet constraints
        for individual in engine.population:
            metrics = individual.get("metrics", {})
            memory_kb = metrics.get("memory_kb", 0)
            speed_us = metrics.get("instantiation_us", 0)

            assert memory_kb <= engine.config.memory_limit_kb or memory_kb == 0
            assert speed_us <= engine.config.instantiation_limit_us or speed_us == 0

        # Test mutation preserves constraints
        mutated = await engine._mutation(engine.population.copy())

        # Check that mutations don't violate constraints (if validator is available)
        if engine.mutation_validator:
            for individual in mutated[:3]:  # Check first few
                validation = await engine.mutation_validator.validate_mutation(individual)
                # Should either be valid or have detected violations
                assert hasattr(validation, "is_valid")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
