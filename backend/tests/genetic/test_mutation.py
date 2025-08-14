"""
Test cases for Day 48: AI Guide Mutation

Tests all mutation components including AI-guided mutation, rate control,
effect prediction, and mutation validation.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.genetic.mutation.ai_mutator import AIMutator
from src.genetic.mutation.effect_predictor import MutationEffectPredictor
from src.genetic.mutation.rate_controller import MutationRateController
from src.genetic.mutation.validator import MutationValidator


class TestAIMutator:
    """Tests for AI-guided mutation system"""

    @pytest.fixture
    def sample_genome(self):
        return {
            "id": "test_agent_001",
            "genes": {
                "layer_sizes": [16, 32, 16],
                "activation": "relu",
                "learning_rate": 0.01,
                "dropout_rate": 0.2,
                "optimizer": "adam",
            },
            "fitness": 0.85,
            "metrics": {"memory_kb": 5.2, "instantiation_us": 2.5, "accuracy": 0.89},
        }

    @pytest.fixture
    def ai_mutator(self):
        return AIMutator()

    def test_ai_mutator_initialization(self, ai_mutator):
        """Test AIMutator initialization"""
        assert ai_mutator is not None
        assert hasattr(ai_mutator, "mutation_strategies")
        assert hasattr(ai_mutator, "ai_client")

    @pytest.mark.asyncio
    async def test_guided_mutation(self, ai_mutator, sample_genome):
        """Test AI-guided mutation with fitness prediction"""
        # Mock AI analysis
        with patch.object(ai_mutator, "_analyze_genome") as mock_analyze:
            mock_analyze.return_value = {
                "weak_areas": ["learning_rate", "dropout_rate"],
                "suggested_mutations": ["decrease_lr", "adjust_dropout"],
                "confidence": 0.85,
            }

            mutated = await ai_mutator.guided_mutation(sample_genome)

            assert mutated is not None
            assert mutated["id"] != sample_genome["id"]
            assert "genes" in mutated
            mock_analyze.assert_called_once()

    @pytest.mark.asyncio
    async def test_strategic_mutation(self, ai_mutator, sample_genome):
        """Test strategic mutation selection"""
        strategies = await ai_mutator.get_mutation_strategies(sample_genome)

        assert isinstance(strategies, list)
        assert len(strategies) > 0
        for strategy in strategies:
            assert "name" in strategy
            assert "priority" in strategy
            assert "expected_improvement" in strategy

    @pytest.mark.asyncio
    async def test_fitness_aware_mutation(self, ai_mutator, sample_genome):
        """Test fitness-aware mutation"""
        low_fitness_genome = sample_genome.copy()
        low_fitness_genome["fitness"] = 0.3

        high_fitness_genome = sample_genome.copy()
        high_fitness_genome["fitness"] = 0.95

        low_mutations = await ai_mutator.guided_mutation(low_fitness_genome)
        high_mutations = await ai_mutator.guided_mutation(high_fitness_genome)

        # Low fitness should get more aggressive mutations
        assert low_mutations is not None
        assert high_mutations is not None

    def test_mutation_intensity_calculation(self, ai_mutator, sample_genome):
        """Test calculation of mutation intensity"""
        intensity = ai_mutator.calculate_mutation_intensity(sample_genome)

        assert 0.0 <= intensity <= 1.0

        # Test with different fitness levels
        low_fitness = sample_genome.copy()
        low_fitness["fitness"] = 0.2
        high_intensity = ai_mutator.calculate_mutation_intensity(low_fitness)

        high_fitness = sample_genome.copy()
        high_fitness["fitness"] = 0.9
        low_intensity = ai_mutator.calculate_mutation_intensity(high_fitness)

        assert high_intensity > low_intensity


class TestMutationRateController:
    """Tests for dynamic mutation rate control"""

    @pytest.fixture
    def rate_controller(self):
        return MutationRateController()

    @pytest.fixture
    def population_history(self):
        return [
            {"generation": 1, "best_fitness": 0.5, "avg_fitness": 0.3},
            {"generation": 2, "best_fitness": 0.6, "avg_fitness": 0.4},
            {"generation": 3, "best_fitness": 0.6, "avg_fitness": 0.4},  # Stagnation
            {"generation": 4, "best_fitness": 0.6, "avg_fitness": 0.4},  # Stagnation
        ]

    def test_rate_controller_initialization(self, rate_controller):
        """Test rate controller initialization"""
        assert rate_controller.base_rate == 0.1
        assert rate_controller.min_rate == 0.01
        assert rate_controller.max_rate == 0.5
        assert rate_controller.adaptation_factor == 0.1

    def test_adaptive_rate_calculation(self, rate_controller, population_history):
        """Test adaptive mutation rate calculation"""
        rate = rate_controller.calculate_adaptive_rate(population_history)

        assert isinstance(rate, float)
        assert rate_controller.min_rate <= rate <= rate_controller.max_rate

    def test_stagnation_detection(self, rate_controller, population_history):
        """Test detection of fitness stagnation"""
        is_stagnant = rate_controller.detect_stagnation(population_history, window=3)

        assert isinstance(is_stagnant, bool)
        # Should detect stagnation in last 3 generations
        assert is_stagnant == True

    def test_diversity_based_adjustment(self, rate_controller):
        """Test diversity-based rate adjustment"""
        high_diversity = 0.8
        low_diversity = 0.2

        high_div_rate = rate_controller.adjust_for_diversity(0.1, high_diversity)
        low_div_rate = rate_controller.adjust_for_diversity(0.1, low_diversity)

        # Low diversity should increase mutation rate
        assert low_div_rate > high_div_rate

    def test_rate_bounds_enforcement(self, rate_controller):
        """Test mutation rate bounds enforcement"""
        # Test minimum bound
        too_low = rate_controller.enforce_bounds(-0.1)
        assert too_low == rate_controller.min_rate

        # Test maximum bound
        too_high = rate_controller.enforce_bounds(1.0)
        assert too_high == rate_controller.max_rate

        # Test normal range
        normal = rate_controller.enforce_bounds(0.15)
        assert normal == 0.15


class TestMutationEffectPredictor:
    """Tests for mutation effect prediction"""

    @pytest.fixture
    def effect_predictor(self):
        return MutationEffectPredictor()

    @pytest.fixture
    def mutation_example(self, sample_genome):
        return {
            "genome": sample_genome,
            "mutation_type": "learning_rate_adjustment",
            "old_value": 0.01,
            "new_value": 0.005,
            "gene_path": "genes.learning_rate",
        }

    def test_predictor_initialization(self, effect_predictor):
        """Test effect predictor initialization"""
        assert effect_predictor is not None
        assert hasattr(effect_predictor, "prediction_models")
        assert hasattr(effect_predictor, "historical_data")

    @pytest.mark.asyncio
    async def test_fitness_prediction(self, effect_predictor, mutation_example):
        """Test fitness change prediction"""
        prediction = await effect_predictor.predict_fitness_change(mutation_example)

        assert isinstance(prediction, dict)
        assert "predicted_delta" in prediction
        assert "confidence" in prediction
        assert "reasoning" in prediction
        assert isinstance(prediction["predicted_delta"], float)
        assert 0.0 <= prediction["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_constraint_violation_prediction(self, effect_predictor, mutation_example):
        """Test constraint violation prediction"""
        violations = await effect_predictor.predict_constraint_violations(mutation_example)

        assert isinstance(violations, dict)
        assert "memory_risk" in violations
        assert "speed_risk" in violations
        assert "safety_risk" in violations

    @pytest.mark.asyncio
    async def test_multi_objective_prediction(self, effect_predictor, mutation_example):
        """Test multi-objective impact prediction"""
        impacts = await effect_predictor.predict_multi_objective_impact(mutation_example)

        assert isinstance(impacts, dict)
        assert "accuracy" in impacts
        assert "memory" in impacts
        assert "speed" in impacts
        assert "stability" in impacts

    def test_historical_learning(self, effect_predictor):
        """Test learning from historical mutations"""
        mutation_history = [
            {
                "mutation": {"type": "lr_decrease", "factor": 0.5},
                "before_fitness": 0.7,
                "after_fitness": 0.8,
                "actual_delta": 0.1,
            }
        ]

        effect_predictor.learn_from_history(mutation_history)

        # Should update internal models
        assert len(effect_predictor.historical_data) > 0

    def test_confidence_calculation(self, effect_predictor, mutation_example):
        """Test prediction confidence calculation"""
        confidence = effect_predictor.calculate_confidence(mutation_example)

        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0


class TestMutationValidator:
    """Tests for mutation validation"""

    @pytest.fixture
    def validator(self):
        return MutationValidator()

    @pytest.fixture
    def valid_mutation(self, sample_genome):
        mutated = sample_genome.copy()
        mutated["genes"]["learning_rate"] = 0.005  # Valid change
        return mutated

    @pytest.fixture
    def invalid_mutation(self, sample_genome):
        mutated = sample_genome.copy()
        mutated["genes"]["layer_sizes"] = [1000, 2000]  # Too large, violates memory
        return mutated

    def test_validator_initialization(self, validator):
        """Test validator initialization"""
        assert validator is not None
        assert hasattr(validator, "constraints")
        assert hasattr(validator, "safety_checks")

    @pytest.mark.asyncio
    async def test_basic_validation(self, validator, valid_mutation):
        """Test basic mutation validation"""
        result = await validator.validate_mutation(valid_mutation)

        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "violations" in result
        assert "risk_score" in result

    @pytest.mark.asyncio
    async def test_constraint_validation(self, validator, invalid_mutation):
        """Test constraint violation detection"""
        result = await validator.validate_mutation(invalid_mutation)

        assert result["is_valid"] == False
        assert len(result["violations"]) > 0

    @pytest.mark.asyncio
    async def test_safety_validation(self, validator, sample_genome):
        """Test safety validation"""
        # Create potentially unsafe mutation
        unsafe_mutation = sample_genome.copy()
        unsafe_mutation["genes"]["malicious_code"] = 'eval("__import__("os").system("rm -rf /"))'

        result = await validator.validate_safety(unsafe_mutation)

        assert isinstance(result, dict)
        assert "is_safe" in result
        assert "threats" in result

    @pytest.mark.asyncio
    async def test_memory_constraint_validation(self, validator, sample_genome):
        """Test memory constraint validation"""
        # Create mutation that violates memory constraint
        memory_violating = sample_genome.copy()
        memory_violating["genes"]["layer_sizes"] = [512, 1024, 512, 256]  # Very large

        result = await validator.validate_constraints(memory_violating)

        assert "memory_violation" in result or not result.get("is_valid", True)

    @pytest.mark.asyncio
    async def test_speed_constraint_validation(self, validator, sample_genome):
        """Test instantiation speed validation"""
        result = await validator.validate_constraints(sample_genome)

        assert "speed_check" in result or "is_valid" in result

    def test_risk_scoring(self, validator, sample_genome):
        """Test mutation risk scoring"""
        risk_score = validator.calculate_risk_score(sample_genome)

        assert isinstance(risk_score, float)
        assert 0.0 <= risk_score <= 1.0

    def test_validation_rules(self, validator):
        """Test validation rule system"""
        rules = validator.get_validation_rules()

        assert isinstance(rules, dict)
        assert "memory_limit" in rules
        assert "speed_limit" in rules
        assert "safety_patterns" in rules


class TestMutationIntegration:
    """Integration tests for mutation components"""

    @pytest.fixture
    def mutation_system(self):
        """Complete mutation system setup"""
        return {
            "mutator": AIMutator(),
            "rate_controller": MutationRateController(),
            "predictor": MutationEffectPredictor(),
            "validator": MutationValidator(),
        }

    @pytest.fixture
    def sample_genome(self):
        return {
            "id": "integration_test_001",
            "genes": {
                "layer_sizes": [16, 32, 16],
                "activation": "relu",
                "learning_rate": 0.01,
                "dropout_rate": 0.2,
                "optimizer": "adam",
            },
            "fitness": 0.75,
            "metrics": {"memory_kb": 4.8, "instantiation_us": 2.1, "accuracy": 0.82},
        }

    @pytest.mark.asyncio
    async def test_complete_mutation_pipeline(self, mutation_system, sample_genome):
        """Test complete mutation pipeline"""
        mutator = mutation_system["mutator"]
        rate_controller = mutation_system["rate_controller"]
        predictor = mutation_system["predictor"]
        validator = mutation_system["validator"]

        # 1. Determine mutation rate
        population_history = [{"generation": 1, "best_fitness": 0.7, "avg_fitness": 0.5}]
        mutation_rate = rate_controller.calculate_adaptive_rate(population_history)

        # 2. Generate mutation candidates
        candidates = await mutator.guided_mutation(sample_genome)

        # 3. Predict effects
        mutation_example = {
            "genome": sample_genome,
            "mutation_type": "guided_mutation",
            "candidates": [candidates] if candidates else [],
        }
        prediction = await predictor.predict_fitness_change(mutation_example)

        # 4. Validate mutation
        if candidates:
            validation = await validator.validate_mutation(candidates)

            assert validation is not None
            assert "is_valid" in validation

        assert mutation_rate > 0
        assert prediction is not None

    @pytest.mark.asyncio
    async def test_adaptive_mutation_flow(self, mutation_system, sample_genome):
        """Test adaptive mutation flow"""
        rate_controller = mutation_system["rate_controller"]
        mutator = mutation_system["mutator"]

        # Simulate stagnation
        stagnant_history = [
            {"generation": i, "best_fitness": 0.7, "avg_fitness": 0.5} for i in range(1, 6)
        ]

        # Should increase mutation rate due to stagnation
        adaptive_rate = rate_controller.calculate_adaptive_rate(stagnant_history)

        # Apply higher intensity mutations
        mutation_intensity = mutator.calculate_mutation_intensity(sample_genome)

        assert adaptive_rate >= rate_controller.base_rate
        assert 0.0 <= mutation_intensity <= 1.0

    def test_mutation_validation_integration(self, mutation_system, sample_genome):
        """Test mutation validation integration"""
        validator = mutation_system["validator"]

        # Test with different risk levels
        low_risk_genome = sample_genome.copy()
        high_risk_genome = sample_genome.copy()
        high_risk_genome["genes"]["layer_sizes"] = [1024, 2048, 1024]  # High memory

        low_risk_score = validator.calculate_risk_score(low_risk_genome)
        high_risk_score = validator.calculate_risk_score(high_risk_genome)

        assert high_risk_score > low_risk_score

    @pytest.mark.asyncio
    async def test_feedback_learning_loop(self, mutation_system, sample_genome):
        """Test feedback learning from mutations"""
        predictor = mutation_system["predictor"]

        # Simulate mutation results
        mutation_results = [
            {
                "mutation": {"type": "lr_adjustment", "factor": 0.5},
                "before_fitness": 0.7,
                "after_fitness": 0.8,
                "actual_delta": 0.1,
            }
        ]

        # Learn from results
        predictor.learn_from_history(mutation_results)

        # Subsequent predictions should be more accurate
        mutation_example = {"genome": sample_genome, "mutation_type": "lr_adjustment"}
        prediction = await predictor.predict_fitness_change(mutation_example)

        assert prediction["confidence"] > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
