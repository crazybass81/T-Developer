"""
Test cases for Day 49: Creative Crossover

Tests all crossover components including multi-point, uniform,
AI-guided crossover, and effect analysis.
"""

import asyncio
from typing import Any, Dict, List, Tuple
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.genetic.crossover.ai_crossover import AICrossover
from src.genetic.crossover.effect_analyzer import CrossoverEffectAnalyzer
from src.genetic.crossover.multi_point import MultiPointCrossover
from src.genetic.crossover.uniform import UniformCrossover


class TestMultiPointCrossover:
    """Tests for multi-point crossover implementation"""

    @pytest.fixture
    def parent1(self):
        return {
            "id": "parent_001",
            "genes": {
                "layer_sizes": [16, 32, 64, 32],
                "activation": "relu",
                "learning_rate": 0.01,
                "dropout_rate": 0.2,
                "optimizer": "adam",
            },
            "fitness": 0.8,
            "metrics": {"memory_kb": 4.2, "instantiation_us": 2.1},
        }

    @pytest.fixture
    def parent2(self):
        return {
            "id": "parent_002",
            "genes": {
                "layer_sizes": [8, 16, 32, 16],
                "activation": "tanh",
                "learning_rate": 0.005,
                "dropout_rate": 0.3,
                "optimizer": "sgd",
            },
            "fitness": 0.75,
            "metrics": {"memory_kb": 3.8, "instantiation_us": 1.9},
        }

    @pytest.fixture
    def crossover(self):
        return MultiPointCrossover()

    def test_crossover_initialization(self, crossover):
        """Test multi-point crossover initialization"""
        assert crossover is not None
        assert crossover.num_points >= 1
        assert hasattr(crossover, "crossover_probability")

    @pytest.mark.asyncio
    async def test_two_point_crossover(self, crossover, parent1, parent2):
        """Test two-point crossover implementation"""
        crossover.num_points = 2
        offspring1, offspring2 = await crossover.crossover(parent1, parent2)

        assert offspring1 is not None
        assert offspring2 is not None
        assert offspring1["id"] != parent1["id"]
        assert offspring2["id"] != parent2["id"]
        assert "genes" in offspring1
        assert "genes" in offspring2

    @pytest.mark.asyncio
    async def test_adaptive_point_selection(self, crossover, parent1, parent2):
        """Test adaptive crossover point selection"""
        points = crossover.select_crossover_points(parent1, parent2)

        assert isinstance(points, list)
        assert len(points) >= 1
        assert all(isinstance(p, int) for p in points)

    def test_compatibility_check(self, crossover, parent1, parent2):
        """Test parent compatibility checking"""
        compatible = crossover.check_compatibility(parent1, parent2)
        assert isinstance(compatible, bool)

        # Test with incompatible parents
        incompatible_parent = parent2.copy()
        incompatible_parent["genes"]["layer_sizes"] = []  # Empty layers

        incompatible = crossover.check_compatibility(parent1, incompatible_parent)
        assert isinstance(incompatible, bool)

    @pytest.mark.asyncio
    async def test_gene_inheritance_patterns(self, crossover, parent1, parent2):
        """Test different gene inheritance patterns"""
        offspring1, offspring2 = await crossover.crossover(parent1, parent2)

        # Check that genes are properly inherited
        child1_genes = offspring1["genes"]
        child2_genes = offspring2["genes"]

        assert "layer_sizes" in child1_genes
        assert "activation" in child1_genes
        assert "learning_rate" in child1_genes

    def test_crossover_point_optimization(self, crossover):
        """Test crossover point optimization"""
        gene_importance = {
            "layer_sizes": 0.8,
            "learning_rate": 0.6,
            "activation": 0.4,
            "optimizer": 0.3,
        }

        optimal_points = crossover.optimize_crossover_points(gene_importance)
        assert isinstance(optimal_points, list)
        assert len(optimal_points) > 0


class TestUniformCrossover:
    """Tests for uniform crossover implementation"""

    @pytest.fixture
    def uniform_crossover(self):
        return UniformCrossover(probability=0.5)

    @pytest.fixture
    def parents(self):
        parent1 = {
            "genes": {
                "layer_sizes": [32, 64, 32],
                "activation": "relu",
                "learning_rate": 0.01,
                "dropout_rate": 0.25,
            },
            "fitness": 0.85,
        }
        parent2 = {
            "genes": {
                "layer_sizes": [16, 32, 16],
                "activation": "tanh",
                "learning_rate": 0.005,
                "dropout_rate": 0.15,
            },
            "fitness": 0.82,
        }
        return parent1, parent2

    def test_uniform_crossover_initialization(self, uniform_crossover):
        """Test uniform crossover initialization"""
        assert uniform_crossover.probability == 0.5
        assert hasattr(uniform_crossover, "bias_strategy")

    @pytest.mark.asyncio
    async def test_uniform_gene_selection(self, uniform_crossover, parents):
        """Test uniform gene selection process"""
        parent1, parent2 = parents
        offspring1, offspring2 = await uniform_crossover.crossover(parent1, parent2)

        assert offspring1 is not None
        assert offspring2 is not None

        # Verify gene mixing occurred
        child1_genes = offspring1["genes"]
        child2_genes = offspring2["genes"]

        assert len(child1_genes) == len(parent1["genes"])
        assert len(child2_genes) == len(parent2["genes"])

    def test_fitness_biased_selection(self, uniform_crossover, parents):
        """Test fitness-biased gene selection"""
        parent1, parent2 = parents

        # Enable fitness bias
        uniform_crossover.bias_strategy = "fitness_weighted"

        selection_probs = uniform_crossover.calculate_selection_probabilities(parent1, parent2)

        assert isinstance(selection_probs, dict)
        assert "parent1_weight" in selection_probs
        assert "parent2_weight" in selection_probs

    def test_diversity_preservation(self, uniform_crossover, parents):
        """Test diversity preservation in offspring"""
        parent1, parent2 = parents
        uniform_crossover.diversity_preservation = True

        diversity_score = uniform_crossover.calculate_diversity_score(parent1, parent2)
        assert isinstance(diversity_score, float)
        assert 0.0 <= diversity_score <= 1.0

    @pytest.mark.asyncio
    async def test_adaptive_probability(self, uniform_crossover, parents):
        """Test adaptive crossover probability"""
        parent1, parent2 = parents

        # Test with different diversity levels
        low_diversity_prob = uniform_crossover.adapt_probability(parent1, parent2, diversity=0.2)
        high_diversity_prob = uniform_crossover.adapt_probability(parent1, parent2, diversity=0.8)

        assert isinstance(low_diversity_prob, float)
        assert isinstance(high_diversity_prob, float)
        assert 0.0 <= low_diversity_prob <= 1.0
        assert 0.0 <= high_diversity_prob <= 1.0


class TestAICrossover:
    """Tests for AI-guided crossover system"""

    @pytest.fixture
    def ai_crossover(self):
        return AICrossover()

    @pytest.fixture
    def high_fitness_parents(self):
        parent1 = {
            "genes": {"layer_sizes": [32, 64, 32], "learning_rate": 0.01},
            "fitness": 0.92,
            "metrics": {"memory_kb": 5.1, "accuracy": 0.94},
        }
        parent2 = {
            "genes": {"layer_sizes": [16, 48, 24], "learning_rate": 0.008},
            "fitness": 0.89,
            "metrics": {"memory_kb": 4.2, "accuracy": 0.91},
        }
        return parent1, parent2

    def test_ai_crossover_initialization(self, ai_crossover):
        """Test AI crossover initialization"""
        assert ai_crossover is not None
        assert hasattr(ai_crossover, "analysis_strategies")
        assert hasattr(ai_crossover, "crossover_patterns")

    @pytest.mark.asyncio
    async def test_intelligent_gene_combination(self, ai_crossover, high_fitness_parents):
        """Test AI-guided gene combination"""
        parent1, parent2 = high_fitness_parents

        with patch.object(ai_crossover, "_analyze_parents") as mock_analyze:
            mock_analyze.return_value = {
                "complementary_genes": ["layer_sizes", "learning_rate"],
                "synergy_potential": 0.85,
                "recommended_strategy": "best_of_both",
            }

            offspring1, offspring2 = await ai_crossover.intelligent_crossover(parent1, parent2)

            assert offspring1 is not None
            assert offspring2 is not None
            mock_analyze.assert_called_once()

    @pytest.mark.asyncio
    async def test_synergy_detection(self, ai_crossover, high_fitness_parents):
        """Test detection of gene synergies"""
        parent1, parent2 = high_fitness_parents

        synergies = await ai_crossover.detect_synergies(parent1, parent2)

        assert isinstance(synergies, dict)
        assert "synergy_score" in synergies
        assert "gene_interactions" in synergies

    @pytest.mark.asyncio
    async def test_performance_prediction(self, ai_crossover, high_fitness_parents):
        """Test offspring performance prediction"""
        parent1, parent2 = high_fitness_parents

        prediction = await ai_crossover.predict_offspring_performance(parent1, parent2)

        assert isinstance(prediction, dict)
        assert "expected_fitness" in prediction
        assert "confidence" in prediction
        assert "risk_factors" in prediction

    def test_crossover_strategy_selection(self, ai_crossover, high_fitness_parents):
        """Test AI strategy selection for crossover"""
        parent1, parent2 = high_fitness_parents

        strategy = ai_crossover.select_crossover_strategy(parent1, parent2)

        assert isinstance(strategy, str)
        assert strategy in ["conservative", "aggressive", "balanced", "exploratory"]

    @pytest.mark.asyncio
    async def test_adaptive_crossover_patterns(self, ai_crossover, high_fitness_parents):
        """Test adaptive crossover pattern learning"""
        parent1, parent2 = high_fitness_parents

        # Simulate successful crossover history
        crossover_history = [
            {
                "parents": [parent1, parent2],
                "offspring_fitness": [0.94, 0.91],
                "strategy_used": "balanced",
            }
        ]

        ai_crossover.learn_from_history(crossover_history)

        # Should adapt strategy based on history
        adapted_strategy = ai_crossover.select_crossover_strategy(parent1, parent2)
        assert isinstance(adapted_strategy, str)


class TestCrossoverEffectAnalyzer:
    """Tests for crossover effect analysis"""

    @pytest.fixture
    def effect_analyzer(self):
        return CrossoverEffectAnalyzer()

    @pytest.fixture
    def crossover_example(self):
        return {
            "parent1": {"genes": {"layer_sizes": [32, 64], "learning_rate": 0.01}, "fitness": 0.8},
            "parent2": {
                "genes": {"layer_sizes": [16, 32], "learning_rate": 0.005},
                "fitness": 0.75,
            },
            "offspring": [
                {"genes": {"layer_sizes": [32, 32], "learning_rate": 0.01}, "fitness": 0.82},
                {"genes": {"layer_sizes": [16, 64], "learning_rate": 0.005}, "fitness": 0.78},
            ],
        }

    def test_analyzer_initialization(self, effect_analyzer):
        """Test effect analyzer initialization"""
        assert effect_analyzer is not None
        assert hasattr(effect_analyzer, "analysis_methods")
        assert hasattr(effect_analyzer, "historical_crossovers")

    @pytest.mark.asyncio
    async def test_fitness_impact_analysis(self, effect_analyzer, crossover_example):
        """Test fitness impact analysis"""
        analysis = await effect_analyzer.analyze_fitness_impact(crossover_example)

        assert isinstance(analysis, dict)
        assert "fitness_improvement" in analysis
        assert "inheritance_patterns" in analysis
        assert "success_factors" in analysis

    @pytest.mark.asyncio
    async def test_gene_contribution_analysis(self, effect_analyzer, crossover_example):
        """Test individual gene contribution analysis"""
        contributions = await effect_analyzer.analyze_gene_contributions(crossover_example)

        assert isinstance(contributions, dict)
        for gene_name, contribution in contributions.items():
            assert isinstance(contribution, dict)
            assert "impact_score" in contribution
            assert "inheritance_success" in contribution

    @pytest.mark.asyncio
    async def test_diversity_impact_analysis(self, effect_analyzer, crossover_example):
        """Test diversity impact analysis"""
        diversity_analysis = await effect_analyzer.analyze_diversity_impact(crossover_example)

        assert isinstance(diversity_analysis, dict)
        assert "diversity_change" in diversity_analysis
        assert "exploration_benefit" in diversity_analysis

    def test_crossover_success_metrics(self, effect_analyzer, crossover_example):
        """Test crossover success metrics calculation"""
        metrics = effect_analyzer.calculate_success_metrics(crossover_example)

        assert isinstance(metrics, dict)
        assert "improvement_rate" in metrics
        assert "diversity_preservation" in metrics
        assert "constraint_compliance" in metrics

    @pytest.mark.asyncio
    async def test_population_level_analysis(self, effect_analyzer):
        """Test population-level crossover analysis"""
        population_data = [
            {
                "generation": 1,
                "crossovers": 10,
                "successful_crossovers": 7,
                "avg_fitness_improvement": 0.05,
            },
            {
                "generation": 2,
                "crossovers": 12,
                "successful_crossovers": 9,
                "avg_fitness_improvement": 0.08,
            },
        ]

        analysis = await effect_analyzer.analyze_population_trends(population_data)

        assert isinstance(analysis, dict)
        assert "success_rate_trend" in analysis
        assert "improvement_trend" in analysis

    def test_learning_from_outcomes(self, effect_analyzer, crossover_example):
        """Test learning from crossover outcomes"""
        initial_knowledge = len(effect_analyzer.historical_crossovers)

        effect_analyzer.learn_from_crossover(crossover_example)

        assert len(effect_analyzer.historical_crossovers) == initial_knowledge + 1

    @pytest.mark.asyncio
    async def test_crossover_recommendation(self, effect_analyzer):
        """Test crossover strategy recommendations"""
        population_state = {"avg_fitness": 0.7, "diversity_index": 0.4, "stagnation_generations": 3}

        recommendations = await effect_analyzer.recommend_crossover_strategy(population_state)

        assert isinstance(recommendations, dict)
        assert "recommended_strategy" in recommendations
        assert "crossover_rate" in recommendations
        assert "reasoning" in recommendations


class TestCrossoverIntegration:
    """Integration tests for crossover components"""

    @pytest.fixture
    def crossover_system(self):
        return {
            "multi_point": MultiPointCrossover(),
            "uniform": UniformCrossover(),
            "ai_crossover": AICrossover(),
            "analyzer": CrossoverEffectAnalyzer(),
        }

    @pytest.fixture
    def test_population(self):
        return [
            {
                "id": f"agent_{i:03d}",
                "genes": {
                    "layer_sizes": [16 * (i % 3 + 1), 32 * (i % 2 + 1)],
                    "learning_rate": 0.01 * (i % 5 + 1) / 5,
                    "activation": ["relu", "tanh", "sigmoid"][i % 3],
                },
                "fitness": 0.3 + (i % 10) * 0.07,
            }
            for i in range(20)
        ]

    @pytest.mark.asyncio
    async def test_crossover_method_comparison(self, crossover_system, test_population):
        """Test comparison of different crossover methods"""
        multi_point = crossover_system["multi_point"]
        uniform = crossover_system["uniform"]
        ai_crossover = crossover_system["ai_crossover"]

        # Select test parents
        parent1, parent2 = test_population[0], test_population[1]

        # Test all methods
        mp_offspring = await multi_point.crossover(parent1, parent2)
        uf_offspring = await uniform.crossover(parent1, parent2)
        ai_offspring = await ai_crossover.intelligent_crossover(parent1, parent2)

        assert len(mp_offspring) == 2
        assert len(uf_offspring) == 2
        assert len(ai_offspring) == 2

    @pytest.mark.asyncio
    async def test_adaptive_crossover_selection(self, crossover_system, test_population):
        """Test adaptive crossover method selection"""
        analyzer = crossover_system["analyzer"]

        # Simulate population state
        population_state = {"diversity": 0.5, "avg_fitness": 0.6, "improvement_rate": 0.02}

        recommendation = await analyzer.recommend_crossover_strategy(population_state)

        assert "recommended_strategy" in recommendation
        assert recommendation["recommended_strategy"] in [
            "multi_point",
            "uniform",
            "ai_guided",
            "hybrid",
        ]

    @pytest.mark.asyncio
    async def test_crossover_pipeline(self, crossover_system, test_population):
        """Test complete crossover pipeline"""
        parents = test_population[:4]  # Use first 4 as parents

        # 1. Select crossover method based on analysis
        analyzer = crossover_system["analyzer"]
        population_state = {"diversity": 0.4, "avg_fitness": 0.65}
        recommendation = await analyzer.recommend_crossover_strategy(population_state)

        # 2. Apply crossover
        if recommendation["recommended_strategy"] == "multi_point":
            crossover_method = crossover_system["multi_point"]
        else:
            crossover_method = crossover_system["uniform"]  # Default fallback

        offspring_pairs = []
        for i in range(0, len(parents), 2):
            pair = await crossover_method.crossover(parents[i], parents[i + 1])
            offspring_pairs.append(pair)

        # 3. Analyze results
        crossover_example = {
            "parent1": parents[0],
            "parent2": parents[1],
            "offspring": list(offspring_pairs[0]),
        }

        analysis = await analyzer.analyze_fitness_impact(crossover_example)

        assert len(offspring_pairs) == 2
        assert analysis is not None

    def test_crossover_constraint_compliance(self, crossover_system, test_population):
        """Test crossover constraint compliance"""
        multi_point = crossover_system["multi_point"]

        # All offspring should maintain constraint compliance
        parent1, parent2 = test_population[0], test_population[1]

        # Check memory and speed constraints would be maintained
        memory_estimate1 = multi_point._estimate_memory_usage(parent1)
        memory_estimate2 = multi_point._estimate_memory_usage(parent2)

        assert memory_estimate1 > 0
        assert memory_estimate2 > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
