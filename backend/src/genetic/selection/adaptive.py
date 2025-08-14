"""Day 47: Adaptive Selection Strategy - 6.4KB"""
import math
import random
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class SelectionStrategy(Enum):
    """Selection strategy types"""

    EXPLORATION = "exploration"
    EXPLOITATION = "exploitation"
    BALANCED = "balanced"


class AdaptiveSelector:
    """Adaptive selection that changes strategy based on evolution state"""

    def __init__(self):
        """Initialize adaptive selector"""
        from backend.src.genetic.selection.elite import EliteSelector
        from backend.src.genetic.selection.roulette import RouletteSelector
        from backend.src.genetic.selection.tournament import TournamentSelector

        # Initialize component selectors
        self.tournament = TournamentSelector()
        self.roulette = RouletteSelector()
        self.elite = EliteSelector()

        # Adaptive parameters
        self.current_strategy = SelectionStrategy.BALANCED
        self.adaptation_history = []
        self.performance_window = 10

        # Strategy weights
        self.strategy_weights = {
            SelectionStrategy.EXPLORATION: {"tournament": 0.2, "roulette": 0.6, "elite": 0.2},
            SelectionStrategy.EXPLOITATION: {"tournament": 0.6, "roulette": 0.2, "elite": 0.2},
            SelectionStrategy.BALANCED: {"tournament": 0.4, "roulette": 0.3, "elite": 0.3},
        }

        self.stats = {
            "strategy_changes": 0,
            "avg_fitness_improvement": 0.0,
            "convergence_rate": 0.0,
        }

    def select(
        self,
        population: List["Genome"],
        generation: int = 0,
        diversity: float = 0.5,
        convergence: float = 0.0,
    ) -> "Genome":
        """Select individual with adaptive strategy"""
        # Update strategy based on current state
        self._update_strategy(generation, diversity, convergence)

        # Get current weights
        weights = self.strategy_weights[self.current_strategy]

        # Probabilistic method selection
        r = random.random()

        if r < weights["tournament"]:
            # Adjust tournament size based on strategy
            if self.current_strategy == SelectionStrategy.EXPLORATION:
                size = 2  # Small tournament for exploration
            elif self.current_strategy == SelectionStrategy.EXPLOITATION:
                size = 5  # Large tournament for exploitation
            else:
                size = 3  # Medium for balanced

            return self.tournament.select(population, size)

        elif r < weights["tournament"] + weights["roulette"]:
            # Adjust temperature based on strategy
            if self.current_strategy == SelectionStrategy.EXPLORATION:
                temp = 2.0  # High temperature for exploration
            elif self.current_strategy == SelectionStrategy.EXPLOITATION:
                temp = 0.5  # Low temperature for exploitation
            else:
                temp = 1.0  # Normal temperature

            return self.roulette.select(population, temp)

        else:
            # Elite selection
            elite = self.elite.select(population, 1)
            return elite[0] if elite else random.choice(population)

    def get_strategy(self, diversity: float, convergence: float = 0.0) -> str:
        """Get recommended strategy based on metrics"""
        if diversity < 0.3:
            # Low diversity - need exploration
            return SelectionStrategy.EXPLORATION.value
        elif diversity > 0.7 or convergence > 0.7:
            # High diversity or convergence - exploit
            return SelectionStrategy.EXPLOITATION.value
        else:
            # Balanced approach
            return SelectionStrategy.BALANCED.value

    def calculate_pressure(self, generation: int, convergence: float) -> float:
        """Calculate selection pressure"""
        # Base pressure increases with generation
        base_pressure = min(1.0, generation / 100.0)

        # Adjust based on convergence
        if convergence < 0.3:
            # Low convergence - reduce pressure
            pressure = base_pressure * 0.5
        elif convergence > 0.7:
            # High convergence - might be stuck, reduce pressure
            pressure = base_pressure * 0.7
        else:
            # Normal convergence
            pressure = base_pressure

        return max(0.1, min(1.0, pressure))

    def hybrid_select(
        self, population: List["Genome"], methods: List[str], weights: List[float]
    ) -> List["Genome"]:
        """Hybrid selection combining multiple methods"""
        if len(methods) != len(weights):
            raise ValueError("Methods and weights must have same length")

        # Normalize weights
        total_weight = sum(weights)
        if total_weight == 0:
            weights = [1.0 / len(weights)] * len(weights)
        else:
            weights = [w / total_weight for w in weights]

        # Calculate selection counts
        total_size = len(population)
        selections_per_method = []
        remaining = total_size

        for i, weight in enumerate(weights[:-1]):
            count = int(total_size * weight)
            selections_per_method.append(count)
            remaining -= count

        selections_per_method.append(remaining)  # Last method gets remainder

        # Perform selections
        selected = []

        for method, count in zip(methods, selections_per_method):
            if count == 0:
                continue

            if method == "tournament":
                batch = self.tournament.select_batch(population, count)
            elif method == "roulette":
                batch = self.roulette.select_batch(population, count)
            elif method == "elite":
                batch = self.elite.select(population, count)
            else:
                # Random fallback
                batch = random.sample(population, min(count, len(population)))

            selected.extend(batch)

        # Shuffle to avoid method clustering
        random.shuffle(selected)

        return selected[:total_size]

    def adaptive_tournament_size(
        self, population_size: int, generation: int, fitness_variance: float
    ) -> int:
        """Dynamically adjust tournament size"""
        # Base size as percentage of population
        base_size = max(2, int(population_size * 0.05))

        # Adjust based on generation
        gen_factor = min(2.0, 1.0 + generation / 100.0)

        # Adjust based on fitness variance
        if fitness_variance < 0.01:
            # Low variance - need smaller tournaments
            var_factor = 0.5
        elif fitness_variance > 0.1:
            # High variance - can use larger tournaments
            var_factor = 1.5
        else:
            var_factor = 1.0

        size = int(base_size * gen_factor * var_factor)
        return max(2, min(population_size, size))

    def _update_strategy(self, generation: int, diversity: float, convergence: float) -> None:
        """Update selection strategy based on evolution state"""
        old_strategy = self.current_strategy

        # Determine new strategy
        if generation < 20:
            # Early generations - exploration
            self.current_strategy = SelectionStrategy.EXPLORATION
        elif generation > 80 and convergence > 0.8:
            # Late generations with high convergence
            self.current_strategy = SelectionStrategy.EXPLOITATION
        else:
            # Dynamic strategy based on metrics
            strategy_str = self.get_strategy(diversity, convergence)
            self.current_strategy = SelectionStrategy(strategy_str)

        # Track strategy changes
        if old_strategy != self.current_strategy:
            self.stats["strategy_changes"] += 1
            self.adaptation_history.append(
                {
                    "generation": generation,
                    "old_strategy": old_strategy.value,
                    "new_strategy": self.current_strategy.value,
                    "diversity": diversity,
                    "convergence": convergence,
                }
            )

    def analyze_performance(self, population: List["Genome"]) -> Dict[str, float]:
        """Analyze selection performance"""
        if not population:
            return {}

        fitnesses = [g.calculate_fitness() for g in population]

        # Calculate metrics
        avg_fitness = sum(fitnesses) / len(fitnesses)
        max_fitness = max(fitnesses)
        min_fitness = min(fitnesses)

        # Fitness variance
        variance = sum((f - avg_fitness) ** 2 for f in fitnesses) / len(fitnesses)
        std_dev = math.sqrt(variance)

        # Selection intensity
        if std_dev > 0:
            intensity = (max_fitness - avg_fitness) / std_dev
        else:
            intensity = 0.0

        return {
            "avg_fitness": avg_fitness,
            "max_fitness": max_fitness,
            "min_fitness": min_fitness,
            "fitness_variance": variance,
            "selection_intensity": intensity,
            "current_strategy": self.current_strategy.value,
        }

    def reset_adaptation(self) -> None:
        """Reset adaptive parameters"""
        self.current_strategy = SelectionStrategy.BALANCED
        self.adaptation_history = []
        self.stats = {
            "strategy_changes": 0,
            "avg_fitness_improvement": 0.0,
            "convergence_rate": 0.0,
        }
