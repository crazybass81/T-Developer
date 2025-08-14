"""
Dynamic Mutation Rate Controller

Automatically adjusts mutation rates based on population diversity,
fitness stagnation, and evolutionary progress to maintain optimal exploration.
"""

import logging
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AdaptationMode(Enum):
    """Adaptation modes for rate control"""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    DYNAMIC = "dynamic"


@dataclass
class RateMetrics:
    """Metrics for rate adaptation"""

    current_rate: float
    fitness_trend: float
    diversity_index: float
    stagnation_count: int
    adjustment_reason: str


class MutationRateController:
    """
    Dynamic mutation rate controller

    Adjusts mutation rates based on:
    - Population diversity
    - Fitness stagnation
    - Evolutionary progress
    - Constraint violations
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize rate controller"""
        self.base_rate = 0.1
        self.min_rate = 0.01
        self.max_rate = 0.5
        self.adaptation_factor = 0.1
        self.stagnation_threshold = 3
        self.diversity_threshold = 0.3

        if config:
            self.base_rate = config.get("base_rate", self.base_rate)
            self.min_rate = config.get("min_rate", self.min_rate)
            self.max_rate = config.get("max_rate", self.max_rate)
            self.adaptation_factor = config.get("adaptation_factor", self.adaptation_factor)

        self.adaptation_mode = AdaptationMode.DYNAMIC
        self.rate_history: List[RateMetrics] = []

        logger.info(f"Rate controller initialized: base={self.base_rate}")

    def calculate_adaptive_rate(self, population_history: List[Dict]) -> float:
        """
        Calculate adaptive mutation rate based on population history

        Args:
            population_history: List of generation statistics

        Returns:
            Adaptive mutation rate
        """
        if not population_history:
            return self.base_rate

        try:
            # Calculate fitness trend
            fitness_trend = self._calculate_fitness_trend(population_history)

            # Check for stagnation
            is_stagnant = self.detect_stagnation(population_history)

            # Calculate diversity (simulated for now)
            diversity = self._estimate_diversity(population_history)

            # Base adjustment
            rate = self.base_rate
            adjustment_reason = "base_rate"

            # Adjust for stagnation
            if is_stagnant:
                rate *= 1 + self.adaptation_factor * 2
                adjustment_reason = "stagnation_detected"

            # Adjust for fitness trend
            if fitness_trend < -0.01:  # Declining fitness
                rate *= 1 + self.adaptation_factor
                adjustment_reason = "declining_fitness"
            elif fitness_trend > 0.05:  # Rapid improvement
                rate *= 1 - self.adaptation_factor * 0.5
                adjustment_reason = "rapid_improvement"

            # Adjust for diversity
            rate = self.adjust_for_diversity(rate, diversity)

            # Enforce bounds
            final_rate = self.enforce_bounds(rate)

            # Record metrics
            metrics = RateMetrics(
                current_rate=final_rate,
                fitness_trend=fitness_trend,
                diversity_index=diversity,
                stagnation_count=self._count_stagnation_generations(population_history),
                adjustment_reason=adjustment_reason,
            )
            self.rate_history.append(metrics)

            # Keep history manageable
            if len(self.rate_history) > 100:
                self.rate_history = self.rate_history[-50:]

            logger.debug(f"Adaptive rate: {final_rate:.4f} (reason: {adjustment_reason})")
            return final_rate

        except Exception as e:
            logger.error(f"Rate calculation failed: {e}")
            return self.base_rate

    def detect_stagnation(self, population_history: List[Dict], window: int = 5) -> bool:
        """
        Detect fitness stagnation in population

        Args:
            population_history: Generation statistics
            window: Number of generations to check

        Returns:
            True if stagnation detected
        """
        if len(population_history) < window:
            return False

        recent_generations = population_history[-window:]
        fitness_values = [gen.get("best_fitness", 0) for gen in recent_generations]

        # Check if fitness hasn't improved significantly
        if len(set(fitness_values)) == 1:  # All values identical
            return True

        # Check if improvement is minimal
        fitness_range = max(fitness_values) - min(fitness_values)
        if fitness_range < 0.01:  # Less than 1% improvement
            return True

        return False

    def adjust_for_diversity(self, base_rate: float, diversity: float) -> float:
        """
        Adjust mutation rate based on population diversity

        Args:
            base_rate: Current mutation rate
            diversity: Population diversity index (0-1)

        Returns:
            Adjusted mutation rate
        """
        if diversity < self.diversity_threshold:
            # Low diversity, increase mutation to explore
            multiplier = 1 + (self.diversity_threshold - diversity) * 2
            return base_rate * multiplier
        elif diversity > 0.8:
            # High diversity, reduce mutation to exploit
            multiplier = 1 - (diversity - 0.8) * 0.5
            return base_rate * multiplier

        return base_rate

    def enforce_bounds(self, rate: float) -> float:
        """
        Enforce mutation rate bounds

        Args:
            rate: Proposed mutation rate

        Returns:
            Rate within valid bounds
        """
        return max(self.min_rate, min(self.max_rate, rate))

    def get_rate_schedule(self, max_generations: int) -> List[float]:
        """
        Generate mutation rate schedule for evolution

        Args:
            max_generations: Total number of generations

        Returns:
            List of mutation rates for each generation
        """
        schedule = []

        for generation in range(max_generations):
            progress = generation / max_generations

            if self.adaptation_mode == AdaptationMode.CONSERVATIVE:
                # Gradually decrease rate
                rate = self.base_rate * (1 - progress * 0.5)
            elif self.adaptation_mode == AdaptationMode.AGGRESSIVE:
                # Start high, decrease rapidly
                rate = self.base_rate * (2 - progress * 1.5)
            elif self.adaptation_mode == AdaptationMode.MODERATE:
                # Slight curve
                rate = self.base_rate * (1.2 - progress * 0.4)
            else:  # DYNAMIC
                # Will be calculated adaptively
                rate = self.base_rate

            schedule.append(self.enforce_bounds(rate))

        return schedule

    def update_adaptation_mode(self, mode: AdaptationMode) -> None:
        """Update adaptation mode"""
        self.adaptation_mode = mode
        logger.info(f"Adaptation mode updated to: {mode.value}")

    def get_current_metrics(self) -> Optional[RateMetrics]:
        """Get current rate metrics"""
        return self.rate_history[-1] if self.rate_history else None

    def reset_history(self) -> None:
        """Reset rate adaptation history"""
        self.rate_history.clear()
        logger.info("Rate history reset")

    def _calculate_fitness_trend(self, population_history: List[Dict]) -> float:
        """Calculate fitness trend over recent generations"""
        if len(population_history) < 3:
            return 0.0

        # Use last 5 generations or all available
        recent = population_history[-5:]
        fitness_values = [gen.get("best_fitness", 0) for gen in recent]

        # Calculate simple slope
        n = len(fitness_values)
        if n < 2:
            return 0.0

        x_values = list(range(n))
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(fitness_values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, fitness_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return slope

    def _estimate_diversity(self, population_history: List[Dict]) -> float:
        """Estimate population diversity (simplified)"""
        if not population_history:
            return 0.5  # Default moderate diversity

        latest = population_history[-1]

        # Simple diversity estimation based on fitness spread
        best_fitness = latest.get("best_fitness", 0)
        avg_fitness = latest.get("avg_fitness", 0)

        if best_fitness == 0:
            return 0.5

        # Higher spread = higher diversity
        fitness_spread = abs(best_fitness - avg_fitness) / max(best_fitness, 0.01)
        diversity = min(1.0, fitness_spread * 2)

        return diversity

    def _count_stagnation_generations(self, population_history: List[Dict]) -> int:
        """Count consecutive stagnation generations"""
        if len(population_history) < 2:
            return 0

        stagnation_count = 0
        previous_fitness = None

        # Check from most recent backwards
        for generation in reversed(population_history[-10:]):  # Check last 10
            current_fitness = generation.get("best_fitness", 0)

            if previous_fitness is not None:
                if abs(current_fitness - previous_fitness) < 0.01:
                    stagnation_count += 1
                else:
                    break

            previous_fitness = current_fitness

        return stagnation_count

    def get_recommended_parameters(self, population_stats: Dict) -> Dict[str, float]:
        """
        Get recommended genetic algorithm parameters

        Args:
            population_stats: Current population statistics

        Returns:
            Recommended parameters
        """
        diversity = population_stats.get("diversity", 0.5)
        avg_fitness = population_stats.get("avg_fitness", 0.5)
        stagnation = population_stats.get("stagnation_generations", 0)

        recommendations = {
            "mutation_rate": self.base_rate,
            "crossover_rate": 0.7,
            "selection_pressure": 2.0,
            "elitism_ratio": 0.1,
        }

        # Adjust based on diversity
        if diversity < 0.3:
            recommendations["mutation_rate"] *= 1.5
            recommendations["crossover_rate"] *= 0.9

        # Adjust for fitness level
        if avg_fitness < 0.3:
            recommendations["selection_pressure"] = 1.5  # Less pressure
        elif avg_fitness > 0.8:
            recommendations["selection_pressure"] = 3.0  # More pressure

        # Adjust for stagnation
        if stagnation > 3:
            recommendations["mutation_rate"] *= 2.0
            recommendations["elitism_ratio"] *= 0.5

        return recommendations
