"""Day 47: Roulette Wheel Selection Algorithm - 6.2KB"""
import math
import random
from typing import Any, Dict, List, Optional, Tuple


class RouletteSelector:
    """Roulette wheel selection for genetic algorithms"""

    def __init__(self):
        """Initialize roulette selector"""
        self.selection_history = []
        self.fitness_scaling = "linear"  # linear, exponential, rank
        self.stats = {"total_selections": 0, "avg_selected_fitness": 0.0, "selection_variance": 0.0}

    def select(self, population: List["Genome"], temperature: float = 1.0) -> "Genome":
        """Select individual using roulette wheel selection"""
        if not population:
            raise ValueError("Population cannot be empty")

        # Calculate fitness values
        fitnesses = [g.calculate_fitness() for g in population]

        # Handle edge case where all fitnesses are zero
        if all(f == 0 for f in fitnesses):
            selected = random.choice(population)
            self._update_stats(selected)
            return selected

        # Scale fitnesses
        scaled_fitnesses = self._scale_fitnesses(fitnesses, temperature)

        # Calculate total fitness
        total_fitness = sum(scaled_fitnesses)

        if total_fitness == 0:
            selected = random.choice(population)
            self._update_stats(selected)
            return selected

        # Spin the wheel
        selection_point = random.uniform(0, total_fitness)
        cumulative = 0.0

        for individual, fitness in zip(population, scaled_fitnesses):
            cumulative += fitness
            if cumulative >= selection_point:
                self._update_stats(individual)
                return individual

        # Fallback (should not reach here)
        selected = population[-1]
        self._update_stats(selected)
        return selected

    def select_batch(
        self, population: List["Genome"], count: int, unique: bool = False
    ) -> List["Genome"]:
        """Select multiple individuals using roulette wheel"""
        if unique and count > len(population):
            raise ValueError("Cannot select more unique individuals than population size")

        selected = []
        selected_ids = set()

        # Pre-calculate for efficiency
        fitnesses = [g.calculate_fitness() for g in population]
        scaled_fitnesses = self._scale_fitnesses(fitnesses)
        total_fitness = sum(scaled_fitnesses)

        if total_fitness == 0:
            # Random selection if all zero fitness
            if unique:
                return random.sample(population, count)
            else:
                return [random.choice(population) for _ in range(count)]

        # Create cumulative distribution
        cumulative = []
        cum_sum = 0.0
        for f in scaled_fitnesses:
            cum_sum += f
            cumulative.append(cum_sum)

        attempts = 0
        max_attempts = count * 10

        while len(selected) < count and attempts < max_attempts:
            # Binary search for efficiency
            point = random.uniform(0, total_fitness)
            idx = self._binary_search(cumulative, point)
            individual = population[idx]

            if unique:
                if id(individual) not in selected_ids:
                    selected.append(individual)
                    selected_ids.add(id(individual))
            else:
                selected.append(individual)

            attempts += 1

        return selected

    def stochastic_universal_sampling(
        self, population: List["Genome"], count: int
    ) -> List["Genome"]:
        """Stochastic Universal Sampling (SUS) variant"""
        if not population:
            return []

        # Calculate fitnesses
        fitnesses = [g.calculate_fitness() for g in population]
        total_fitness = sum(fitnesses)

        if total_fitness == 0:
            return random.sample(population, min(count, len(population)))

        # Calculate selection interval
        interval = total_fitness / count

        # Random starting point
        start = random.uniform(0, interval)

        # Select individuals at regular intervals
        selected = []
        cumulative = 0.0
        current_point = start

        for i, (individual, fitness) in enumerate(zip(population, fitnesses)):
            cumulative += fitness

            while current_point <= cumulative and len(selected) < count:
                selected.append(individual)
                current_point += interval

        return selected

    def rank_based_roulette(self, population: List["Genome"]) -> "Genome":
        """Roulette selection based on rank rather than raw fitness"""
        # Rank population
        ranked = sorted(population, key=lambda g: g.calculate_fitness(), reverse=True)

        # Assign rank-based probabilities
        n = len(ranked)
        rank_values = []

        for i in range(n):
            # Linear ranking: best gets n, worst gets 1
            rank_values.append(n - i)

        # Standard roulette on ranks
        total = sum(rank_values)
        point = random.uniform(0, total)

        cumulative = 0.0
        for individual, rank_val in zip(ranked, rank_values):
            cumulative += rank_val
            if cumulative >= point:
                self._update_stats(individual)
                return individual

        return ranked[-1]

    def exponential_roulette(self, population: List["Genome"], base: float = 2.0) -> "Genome":
        """Exponential scaling for stronger selection pressure"""
        fitnesses = [g.calculate_fitness() for g in population]

        # Exponential scaling
        exp_fitnesses = [base**f for f in fitnesses]
        total = sum(exp_fitnesses)

        if total == 0:
            return random.choice(population)

        point = random.uniform(0, total)
        cumulative = 0.0

        for individual, exp_fit in zip(population, exp_fitnesses):
            cumulative += exp_fit
            if cumulative >= point:
                self._update_stats(individual)
                return individual

        return population[-1]

    def sigma_scaled_roulette(self, population: List["Genome"]) -> "Genome":
        """Sigma scaling to handle negative and similar fitnesses"""
        fitnesses = [g.calculate_fitness() for g in population]

        if len(fitnesses) < 2:
            return population[0] if population else None

        # Calculate mean and std dev
        mean = sum(fitnesses) / len(fitnesses)
        variance = sum((f - mean) ** 2 for f in fitnesses) / len(fitnesses)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0

        # Sigma scaling
        c = 2.0  # Typical value
        scaled = []
        for f in fitnesses:
            if std_dev > 0:
                scaled_val = 1 + (f - mean) / (c * std_dev)
            else:
                scaled_val = 1.0
            scaled.append(max(0.0, scaled_val))  # Ensure non-negative

        total = sum(scaled)
        if total == 0:
            return random.choice(population)

        # Standard roulette on scaled values
        point = random.uniform(0, total)
        cumulative = 0.0

        for individual, scaled_fit in zip(population, scaled):
            cumulative += scaled_fit
            if cumulative >= point:
                self._update_stats(individual)
                return individual

        return population[-1]

    def _scale_fitnesses(self, fitnesses: List[float], temperature: float = 1.0) -> List[float]:
        """Scale fitness values based on current scaling method"""
        if self.fitness_scaling == "exponential":
            return [math.exp(f / temperature) for f in fitnesses]
        elif self.fitness_scaling == "rank":
            # Convert to ranks
            sorted_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
            ranks = [0] * len(fitnesses)
            for rank, idx in enumerate(sorted_indices):
                ranks[idx] = len(fitnesses) - rank
            return ranks
        else:  # linear
            # Shift to ensure all positive
            min_fit = min(fitnesses)
            if min_fit < 0:
                return [f - min_fit + 0.01 for f in fitnesses]
            return fitnesses

    def _binary_search(self, cumulative: List[float], target: float) -> int:
        """Binary search for efficiency in large populations"""
        left, right = 0, len(cumulative) - 1

        while left < right:
            mid = (left + right) // 2
            if cumulative[mid] < target:
                left = mid + 1
            else:
                right = mid

        return left

    def _update_stats(self, selected: "Genome") -> None:
        """Update selection statistics"""
        self.stats["total_selections"] += 1

        fitness = selected.calculate_fitness()

        # Running average
        alpha = 0.1
        self.stats["avg_selected_fitness"] = (1 - alpha) * self.stats[
            "avg_selected_fitness"
        ] + alpha * fitness

        # Track history
        self.selection_history.append(fitness)
        if len(self.selection_history) > 1000:
            self.selection_history = self.selection_history[-1000:]

        # Calculate variance
        if len(self.selection_history) > 1:
            mean = sum(self.selection_history) / len(self.selection_history)
            variance = sum((f - mean) ** 2 for f in self.selection_history)
            self.stats["selection_variance"] = variance / len(self.selection_history)

    def get_selection_distribution(self) -> Dict[str, float]:
        """Get distribution of selections"""
        if not self.selection_history:
            return {}

        # Create histogram
        bins = 10
        min_val = min(self.selection_history)
        max_val = max(self.selection_history)

        if min_val == max_val:
            return {str(min_val): 1.0}

        bin_size = (max_val - min_val) / bins
        distribution = {}

        for i in range(bins):
            bin_min = min_val + i * bin_size
            bin_max = bin_min + bin_size
            count = sum(1 for f in self.selection_history if bin_min <= f < bin_max)
            distribution[f"{bin_min:.2f}-{bin_max:.2f}"] = count / len(self.selection_history)

        return distribution
