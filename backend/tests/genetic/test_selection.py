"""Day 47: Tests for Selection Algorithms"""
import unittest
from typing import List
from unittest.mock import Mock, patch


class TestTournamentSelection(unittest.TestCase):
    """Test suite for tournament selection"""

    def setUp(self):
        """Set up test fixtures"""
        from backend.src.genetic.genome import Genome
        from backend.src.genetic.selection.tournament import TournamentSelector

        self.selector = TournamentSelector()
        self.population = [Genome() for _ in range(100)]

    def test_basic_tournament(self):
        """Test basic tournament selection"""
        selected = self.selector.select(self.population, tournament_size=3)
        self.assertIsNotNone(selected)
        self.assertIn(selected, self.population)

    def test_tournament_size_effect(self):
        """Test that larger tournaments favor better fitness"""
        # Small tournament
        selections_small = []
        for _ in range(100):
            selected = self.selector.select(self.population, tournament_size=2)
            selections_small.append(selected.calculate_fitness())

        # Large tournament
        selections_large = []
        for _ in range(100):
            selected = self.selector.select(self.population, tournament_size=10)
            selections_large.append(selected.calculate_fitness())

        # Large tournaments should have higher average fitness
        self.assertGreater(
            sum(selections_large) / len(selections_large),
            sum(selections_small) / len(selections_small),
        )

    def test_batch_selection(self):
        """Test selecting multiple individuals"""
        selected = self.selector.select_batch(self.population, count=10)
        self.assertEqual(len(selected), 10)
        # Should have unique selections
        self.assertEqual(len(set(id(s) for s in selected)), 10)


class TestRouletteSelection(unittest.TestCase):
    """Test suite for roulette wheel selection"""

    def setUp(self):
        """Set up test fixtures"""
        from backend.src.genetic.genome import Genome
        from backend.src.genetic.selection.roulette import RouletteSelector

        self.selector = RouletteSelector()
        self.population = [Genome() for _ in range(50)]

    def test_basic_roulette(self):
        """Test basic roulette selection"""
        selected = self.selector.select(self.population)
        self.assertIsNotNone(selected)
        self.assertIn(selected, self.population)

    def test_fitness_proportional(self):
        """Test that selection is proportional to fitness"""
        # Count selections
        selection_counts = {}
        for _ in range(1000):
            selected = self.selector.select(self.population)
            key = id(selected)
            selection_counts[key] = selection_counts.get(key, 0) + 1

        # Higher fitness should be selected more often
        for genome in self.population:
            if genome.calculate_fitness() > 0.7:
                # High fitness genomes should be selected
                self.assertIn(id(genome), selection_counts)

    def test_zero_fitness_handling(self):
        """Test handling when all fitnesses are zero"""
        # Mock zero fitness
        for genome in self.population:
            genome._fitness_cache = 0.0

        selected = self.selector.select(self.population)
        # Should still return a valid selection
        self.assertIsNotNone(selected)
        self.assertIn(selected, self.population)


class TestEliteSelection(unittest.TestCase):
    """Test suite for elite selection"""

    def setUp(self):
        """Set up test fixtures"""
        from backend.src.genetic.genome import Genome
        from backend.src.genetic.selection.elite import EliteSelector

        self.selector = EliteSelector()
        self.population = [Genome() for _ in range(50)]

    def test_basic_elite(self):
        """Test basic elite selection"""
        elite = self.selector.select(self.population, elite_size=5)
        self.assertEqual(len(elite), 5)

        # Should be sorted by fitness
        fitnesses = [g.calculate_fitness() for g in elite]
        self.assertEqual(fitnesses, sorted(fitnesses, reverse=True))

    def test_elite_ratio(self):
        """Test elite selection by ratio"""
        elite = self.selector.select_by_ratio(self.population, ratio=0.1)
        expected_size = int(len(self.population) * 0.1)
        self.assertEqual(len(elite), expected_size)

    def test_elite_persistence(self):
        """Test that elite are actually the best"""
        elite = self.selector.select(self.population, elite_size=10)
        elite_fitnesses = [g.calculate_fitness() for g in elite]

        non_elite = [g for g in self.population if g not in elite]
        if non_elite:
            max_non_elite = max(g.calculate_fitness() for g in non_elite)
            min_elite = min(elite_fitnesses)
            self.assertGreaterEqual(min_elite, max_non_elite)


class TestAdaptiveSelection(unittest.TestCase):
    """Test suite for adaptive selection strategy"""

    def setUp(self):
        """Set up test fixtures"""
        from backend.src.genetic.genome import Genome
        from backend.src.genetic.selection.adaptive import AdaptiveSelector

        self.selector = AdaptiveSelector()
        self.population = [Genome() for _ in range(100)]

    def test_strategy_switching(self):
        """Test adaptive strategy switching"""
        # Early generation - more exploration
        selected1 = self.selector.select(self.population, generation=1, diversity=0.8)
        self.assertIsNotNone(selected1)

        # Late generation - more exploitation
        selected2 = self.selector.select(self.population, generation=100, diversity=0.2)
        self.assertIsNotNone(selected2)

    def test_diversity_adaptation(self):
        """Test adaptation based on diversity"""
        # Low diversity - increase exploration
        strategy1 = self.selector.get_strategy(diversity=0.2)
        self.assertEqual(strategy1, "exploration")

        # High diversity - increase exploitation
        strategy2 = self.selector.get_strategy(diversity=0.9)
        self.assertEqual(strategy2, "exploitation")

        # Medium diversity - balanced
        strategy3 = self.selector.get_strategy(diversity=0.5)
        self.assertEqual(strategy3, "balanced")

    def test_pressure_adjustment(self):
        """Test selection pressure adjustment"""
        # Calculate pressure for different scenarios
        pressure1 = self.selector.calculate_pressure(generation=10, convergence=0.1)
        pressure2 = self.selector.calculate_pressure(generation=50, convergence=0.8)

        # Later generation with high convergence should have lower pressure
        self.assertLess(pressure2, pressure1)

    def test_hybrid_selection(self):
        """Test hybrid selection combining multiple methods"""
        selected = self.selector.hybrid_select(
            self.population, methods=["tournament", "roulette", "elite"], weights=[0.5, 0.3, 0.2]
        )
        self.assertEqual(len(selected), len(self.population))


if __name__ == "__main__":
    unittest.main()
