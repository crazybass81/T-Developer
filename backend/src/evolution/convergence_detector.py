"""
Evolution Convergence Detector

Detects when evolution has converged and determines optimal stopping points
to prevent overfitting and wasted computational resources.
"""

import logging
import statistics
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ConvergenceType(Enum):
    """Types of convergence detection"""

    FITNESS_PLATEAU = "fitness_plateau"
    DIVERSITY_LOSS = "diversity_loss"
    EARLY_STOPPING = "early_stopping"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    TARGET_REACHED = "target_reached"


@dataclass
class ConvergenceSignal:
    """Signal indicating convergence detection"""

    type: ConvergenceType
    confidence: float
    evidence: str
    generation_detected: int
    recommendation: str


@dataclass
class ConvergenceMetrics:
    """Metrics for convergence analysis"""

    fitness_stagnation_count: int
    diversity_trend: float
    improvement_rate: float
    variance_reduction: float
    overfitting_risk: float
    computational_efficiency: float


class ConvergenceDetector:
    """
    Evolution Convergence Detection System

    Monitors evolution progress and detects various convergence conditions
    to optimize computational resources and prevent overfitting.
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize convergence detector"""
        self.config = config or {
            "fitness_plateau_threshold": 0.01,
            "stagnation_generations": 10,
            "diversity_threshold": 0.1,
            "variance_threshold": 0.001,
            "confidence_threshold": 0.8,
            "early_stopping_patience": 15,
            "target_fitness": 0.95,
            "overfitting_threshold": 0.85,
        }

        self.fitness_history: List[float] = []
        self.diversity_history: List[float] = []
        self.convergence_signals: List[ConvergenceSignal] = []
        self.last_improvement_generation = 0
        self.best_fitness_seen = 0.0

        logger.info("Convergence Detector initialized")

    def analyze_convergence(
        self, generation: int, population: List[Dict[str, Any]], metrics_history: List[Dict]
    ) -> Tuple[bool, List[ConvergenceSignal]]:
        """
        Analyze current evolution state for convergence

        Args:
            generation: Current generation number
            population: Current population
            metrics_history: Historical metrics data

        Returns:
            Tuple of (has_converged, convergence_signals)
        """
        try:
            # Update internal state
            self._update_metrics(generation, population, metrics_history)

            # Run convergence checks
            signals = []

            # Check for fitness plateau
            plateau_signal = self._check_fitness_plateau(generation)
            if plateau_signal:
                signals.append(plateau_signal)

            # Check for diversity loss
            diversity_signal = self._check_diversity_loss(generation)
            if diversity_signal:
                signals.append(diversity_signal)

            # Check for early stopping conditions
            early_stop_signal = self._check_early_stopping(generation, metrics_history)
            if early_stop_signal:
                signals.append(early_stop_signal)

            # Check if target reached
            target_signal = self._check_target_reached(generation)
            if target_signal:
                signals.append(target_signal)

            # Check for performance degradation
            degradation_signal = self._check_performance_degradation(generation, metrics_history)
            if degradation_signal:
                signals.append(degradation_signal)

            # Store signals
            self.convergence_signals.extend(signals)

            # Determine if converged
            has_converged = self._determine_convergence(signals)

            if has_converged:
                logger.info(f"Convergence detected at generation {generation}")
                for signal in signals:
                    logger.info(f"  - {signal.type.value}: {signal.evidence}")

            return has_converged, signals

        except Exception as e:
            logger.error(f"Convergence analysis failed: {e}")
            return False, []

    def predict_convergence_generation(
        self, current_generation: int, metrics_history: List[Dict]
    ) -> Optional[int]:
        """
        Predict when convergence is likely to occur

        Returns:
            Predicted generation number or None if unable to predict
        """
        try:
            if len(self.fitness_history) < 5:
                return None

            # Analyze fitness improvement trend
            recent_improvements = []
            for i in range(1, min(10, len(self.fitness_history))):
                improvement = self.fitness_history[-i] - self.fitness_history[-(i + 1)]
                recent_improvements.append(improvement)

            if not recent_improvements:
                return None

            avg_improvement = statistics.mean(recent_improvements)

            if avg_improvement <= 0:
                # Already converged or declining
                return current_generation

            # Estimate generations to reach target
            current_fitness = self.fitness_history[-1]
            target_fitness = self.config["target_fitness"]

            if current_fitness >= target_fitness:
                return current_generation

            fitness_gap = target_fitness - current_fitness
            generations_needed = int(fitness_gap / avg_improvement)

            # Add buffer for decreasing improvement rate
            buffer_generations = max(5, generations_needed // 4)
            predicted_generation = current_generation + generations_needed + buffer_generations

            logger.debug(f"Predicted convergence at generation {predicted_generation}")
            return predicted_generation

        except Exception as e:
            logger.error(f"Convergence prediction failed: {e}")
            return None

    def get_convergence_metrics(self) -> ConvergenceMetrics:
        """Get current convergence metrics"""
        try:
            # Count fitness stagnation
            stagnation_count = 0
            if len(self.fitness_history) >= 2:
                for i in range(len(self.fitness_history) - 1, 0, -1):
                    if (
                        abs(self.fitness_history[i] - self.fitness_history[i - 1])
                        < self.config["fitness_plateau_threshold"]
                    ):
                        stagnation_count += 1
                    else:
                        break

            # Calculate diversity trend
            diversity_trend = 0.0
            if len(self.diversity_history) >= 3:
                recent_diversity = self.diversity_history[-3:]
                diversity_trend = (recent_diversity[-1] - recent_diversity[0]) / len(
                    recent_diversity
                )

            # Calculate improvement rate
            improvement_rate = 0.0
            if len(self.fitness_history) >= 3:
                recent_fitness = self.fitness_history[-3:]
                improvement_rate = (recent_fitness[-1] - recent_fitness[0]) / len(recent_fitness)

            # Calculate variance reduction
            variance_reduction = 0.0
            if len(self.fitness_history) >= 6:
                early_variance = statistics.variance(self.fitness_history[:3])
                recent_variance = statistics.variance(self.fitness_history[-3:])
                if early_variance > 0:
                    variance_reduction = (early_variance - recent_variance) / early_variance

            # Estimate overfitting risk
            overfitting_risk = self._calculate_overfitting_risk()

            # Calculate computational efficiency
            efficiency = self._calculate_computational_efficiency()

            return ConvergenceMetrics(
                fitness_stagnation_count=stagnation_count,
                diversity_trend=diversity_trend,
                improvement_rate=improvement_rate,
                variance_reduction=variance_reduction,
                overfitting_risk=overfitting_risk,
                computational_efficiency=efficiency,
            )

        except Exception as e:
            logger.error(f"Failed to calculate convergence metrics: {e}")
            return ConvergenceMetrics(0, 0.0, 0.0, 0.0, 0.5, 0.5)

    def should_continue_evolution(
        self, generation: int, computational_budget: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Determine if evolution should continue

        Returns:
            Tuple of (should_continue, reason)
        """
        try:
            # Check computational budget
            if computational_budget and generation >= computational_budget:
                return False, f"Computational budget exhausted at generation {generation}"

            # Check recent signals
            recent_signals = [
                s for s in self.convergence_signals if s.generation_detected >= generation - 5
            ]

            # High confidence convergence signals
            high_confidence_signals = [
                s for s in recent_signals if s.confidence >= self.config["confidence_threshold"]
            ]

            if high_confidence_signals:
                signal_types = [s.type.value for s in high_confidence_signals]
                return False, f"High confidence convergence detected: {', '.join(signal_types)}"

            # Check for target fitness reached
            if self.fitness_history and self.fitness_history[-1] >= self.config["target_fitness"]:
                return False, f"Target fitness {self.config['target_fitness']} reached"

            # Check for extended stagnation
            metrics = self.get_convergence_metrics()
            if metrics.fitness_stagnation_count >= self.config["early_stopping_patience"]:
                return (
                    False,
                    f"Extended fitness stagnation ({metrics.fitness_stagnation_count} generations)",
                )

            # Check overfitting risk
            if metrics.overfitting_risk >= self.config["overfitting_threshold"]:
                return False, f"High overfitting risk ({metrics.overfitting_risk:.3f})"

            # Continue evolution
            return True, "Evolution should continue"

        except Exception as e:
            logger.error(f"Continue evolution check failed: {e}")
            return True, "Unable to determine, continuing evolution"

    # Private helper methods

    def _update_metrics(
        self, generation: int, population: List[Dict[str, Any]], metrics_history: List[Dict]
    ) -> None:
        """Update internal metrics"""
        if not population:
            return

        # Update fitness history
        fitnesses = [ind.get("fitness", 0.0) for ind in population]
        best_fitness = max(fitnesses) if fitnesses else 0.0
        self.fitness_history.append(best_fitness)

        if best_fitness > self.best_fitness_seen:
            self.best_fitness_seen = best_fitness
            self.last_improvement_generation = generation

        # Update diversity history
        diversity = self._calculate_population_diversity(population)
        self.diversity_history.append(diversity)

        # Keep history manageable
        max_history = 100
        if len(self.fitness_history) > max_history:
            self.fitness_history = self.fitness_history[-max_history:]
        if len(self.diversity_history) > max_history:
            self.diversity_history = self.diversity_history[-max_history:]

    def _calculate_population_diversity(self, population: List[Dict[str, Any]]) -> float:
        """Calculate population diversity"""
        if len(population) < 2:
            return 0.0

        try:
            differences = 0
            comparisons = 0

            for i in range(len(population)):
                for j in range(i + 1, len(population)):
                    genes1 = population[i].get("genes", {})
                    genes2 = population[j].get("genes", {})

                    for gene_name in genes1.keys():
                        if gene_name in genes2:
                            comparisons += 1
                            if genes1[gene_name] != genes2[gene_name]:
                                differences += 1

            return differences / max(comparisons, 1)

        except Exception as e:
            logger.warning(f"Diversity calculation failed: {e}")
            return 0.5

    def _check_fitness_plateau(self, generation: int) -> Optional[ConvergenceSignal]:
        """Check for fitness plateau"""
        if len(self.fitness_history) < self.config["stagnation_generations"]:
            return None

        recent_fitness = self.fitness_history[-self.config["stagnation_generations"] :]
        fitness_range = max(recent_fitness) - min(recent_fitness)

        if fitness_range < self.config["fitness_plateau_threshold"]:
            confidence = min(0.9, (self.config["stagnation_generations"] - 3) / 10)

            return ConvergenceSignal(
                type=ConvergenceType.FITNESS_PLATEAU,
                confidence=confidence,
                evidence=f"Fitness range {fitness_range:.6f} < {self.config['fitness_plateau_threshold']} for {self.config['stagnation_generations']} generations",
                generation_detected=generation,
                recommendation="Consider increasing mutation rate or changing strategy",
            )

        return None

    def _check_diversity_loss(self, generation: int) -> Optional[ConvergenceSignal]:
        """Check for diversity loss"""
        if len(self.diversity_history) < 3:
            return None

        current_diversity = self.diversity_history[-1]

        if current_diversity < self.config["diversity_threshold"]:
            trend = self.diversity_history[-1] - self.diversity_history[-3]
            confidence = 0.8 if trend < -0.1 else 0.6

            return ConvergenceSignal(
                type=ConvergenceType.DIVERSITY_LOSS,
                confidence=confidence,
                evidence=f"Population diversity {current_diversity:.3f} < {self.config['diversity_threshold']}",
                generation_detected=generation,
                recommendation="Increase mutation rate or introduce new individuals",
            )

        return None

    def _check_early_stopping(
        self, generation: int, metrics_history: List[Dict]
    ) -> Optional[ConvergenceSignal]:
        """Check early stopping conditions"""
        generations_since_improvement = generation - self.last_improvement_generation

        if generations_since_improvement >= self.config["early_stopping_patience"]:
            confidence = min(
                0.95, generations_since_improvement / self.config["early_stopping_patience"]
            )

            return ConvergenceSignal(
                type=ConvergenceType.EARLY_STOPPING,
                confidence=confidence,
                evidence=f"No improvement for {generations_since_improvement} generations",
                generation_detected=generation,
                recommendation="Stop evolution to prevent overfitting",
            )

        return None

    def _check_target_reached(self, generation: int) -> Optional[ConvergenceSignal]:
        """Check if target fitness reached"""
        if not self.fitness_history:
            return None

        current_fitness = self.fitness_history[-1]

        if current_fitness >= self.config["target_fitness"]:
            return ConvergenceSignal(
                type=ConvergenceType.TARGET_REACHED,
                confidence=1.0,
                evidence=f"Target fitness {self.config['target_fitness']} reached with {current_fitness:.4f}",
                generation_detected=generation,
                recommendation="Evolution objective achieved",
            )

        return None

    def _check_performance_degradation(
        self, generation: int, metrics_history: List[Dict]
    ) -> Optional[ConvergenceSignal]:
        """Check for performance degradation"""
        if len(self.fitness_history) < 10:
            return None

        # Check if recent performance is worse than peak
        recent_fitness = statistics.mean(self.fitness_history[-5:])
        peak_fitness = max(self.fitness_history[:-5]) if len(self.fitness_history) > 5 else 0

        if peak_fitness > 0 and recent_fitness < peak_fitness * 0.95:
            degradation = (peak_fitness - recent_fitness) / peak_fitness
            confidence = min(0.8, degradation * 2)

            return ConvergenceSignal(
                type=ConvergenceType.PERFORMANCE_DEGRADATION,
                confidence=confidence,
                evidence=f"Performance degraded by {degradation:.3f} from peak",
                generation_detected=generation,
                recommendation="Consider rollback to earlier generation",
            )

        return None

    def _determine_convergence(self, signals: List[ConvergenceSignal]) -> bool:
        """Determine if evolution has converged based on signals"""
        if not signals:
            return False

        # Check for high-confidence signals
        high_confidence = [
            s for s in signals if s.confidence >= self.config["confidence_threshold"]
        ]

        if high_confidence:
            return True

        # Check for multiple medium-confidence signals
        medium_confidence = [s for s in signals if s.confidence >= 0.6]

        if len(medium_confidence) >= 2:
            return True

        return False

    def _calculate_overfitting_risk(self) -> float:
        """Calculate risk of overfitting"""
        if len(self.fitness_history) < 10:
            return 0.0

        # Look for fitness improvement without diversity improvement
        recent_fitness_trend = (
            self.fitness_history[-1] - self.fitness_history[-5]
            if len(self.fitness_history) >= 5
            else 0
        )
        recent_diversity_trend = (
            self.diversity_history[-1] - self.diversity_history[-5]
            if len(self.diversity_history) >= 5
            else 0
        )

        if recent_fitness_trend > 0 and recent_diversity_trend < -0.1:
            # Fitness improving but diversity decreasing rapidly
            risk = min(1.0, abs(recent_diversity_trend) * 2)
        else:
            risk = 0.1

        return risk

    def _calculate_computational_efficiency(self) -> float:
        """Calculate computational efficiency"""
        if len(self.fitness_history) < 5:
            return 1.0

        # Efficiency based on fitness improvement per generation
        recent_generations = min(10, len(self.fitness_history))
        fitness_improvement = self.fitness_history[-1] - self.fitness_history[-recent_generations]

        if fitness_improvement <= 0:
            return 0.1

        efficiency = fitness_improvement / recent_generations
        return min(1.0, efficiency * 10)  # Scale to 0-1 range

    def get_convergence_summary(self) -> Dict[str, Any]:
        """Get summary of convergence analysis"""
        recent_signals = (
            self.convergence_signals[-10:]
            if len(self.convergence_signals) >= 10
            else self.convergence_signals
        )

        signal_counts = {}
        for signal in recent_signals:
            signal_type = signal.type.value
            signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1

        metrics = self.get_convergence_metrics()

        return {
            "total_signals": len(self.convergence_signals),
            "recent_signal_counts": signal_counts,
            "current_metrics": {
                "fitness_stagnation": metrics.fitness_stagnation_count,
                "diversity_trend": metrics.diversity_trend,
                "improvement_rate": metrics.improvement_rate,
                "overfitting_risk": metrics.overfitting_risk,
            },
            "best_fitness_seen": self.best_fitness_seen,
            "generations_since_improvement": len(self.fitness_history)
            - self.last_improvement_generation
            - 1
            if self.fitness_history
            else 0,
        }
