"""
Evolution Parameter Optimizer

Automatically tunes genetic algorithm parameters for optimal performance
based on population dynamics and evolution progress.
"""

import logging
import statistics
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Available optimization strategies"""

    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"
    PERFORMANCE_BASED = "performance_based"


@dataclass
class ParameterSet:
    """Set of evolution parameters"""

    mutation_rate: float
    crossover_rate: float
    selection_pressure: float
    population_size: int
    fitness_score: float = 0.0
    generation_tested: int = 0


@dataclass
class OptimizationResult:
    """Result of parameter optimization"""

    best_parameters: ParameterSet
    improvement_percentage: float
    confidence_score: float
    generations_tested: int
    optimization_time: float


class ParameterOptimizer:
    """
    Genetic Algorithm Parameter Optimizer

    Automatically tunes GA parameters for optimal evolution performance
    using meta-evolution and statistical analysis.
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize parameter optimizer"""
        self.config = config or {
            "optimization_generations": 20,
            "parameter_population_size": 8,
            "convergence_threshold": 0.95,
            "min_improvement": 0.05,
            "max_optimization_time": 300,  # seconds
            "memory_limit_kb": 6.5,
            "speed_limit_us": 3.0,
        }

        self.strategy = OptimizationStrategy.ADAPTIVE
        self.parameter_history: List[ParameterSet] = []
        self.optimization_history: List[OptimizationResult] = []

        # Parameter bounds
        self.parameter_bounds = {
            "mutation_rate": (0.01, 0.5),
            "crossover_rate": (0.3, 0.9),
            "selection_pressure": (1.2, 4.0),
            "population_size": (20, 100),
        }

        logger.info("Parameter Optimizer initialized")

    async def optimize_parameters(
        self,
        current_parameters: Dict[str, Any],
        evolution_history: List[Dict],
        target_fitness: float = 0.9,
    ) -> OptimizationResult:
        """
        Optimize genetic algorithm parameters

        Args:
            current_parameters: Current GA parameters
            evolution_history: Historical evolution data
            target_fitness: Target fitness to optimize for

        Returns:
            Optimization result with best parameters
        """
        start_time = time.time()

        try:
            logger.info("Starting parameter optimization")

            # Analyze current performance
            current_performance = self._analyze_performance(evolution_history)

            # Generate parameter candidates
            candidates = self._generate_parameter_candidates(
                current_parameters, current_performance
            )

            # Evaluate parameter sets
            evaluated_candidates = await self._evaluate_candidates(candidates, evolution_history)

            # Select best parameters
            best_params = self._select_best_parameters(evaluated_candidates, current_performance)

            # Calculate improvement
            improvement = self._calculate_improvement(
                current_performance, best_params.fitness_score
            )

            optimization_time = time.time() - start_time

            result = OptimizationResult(
                best_parameters=best_params,
                improvement_percentage=improvement,
                confidence_score=self._calculate_confidence(evaluated_candidates),
                generations_tested=len(evaluated_candidates),
                optimization_time=optimization_time,
            )

            # Record optimization
            self.optimization_history.append(result)

            logger.info(f"Parameter optimization completed: {improvement:.2f}% improvement")
            return result

        except Exception as e:
            logger.error(f"Parameter optimization failed: {e}")
            # Return current parameters as fallback
            return OptimizationResult(
                best_parameters=ParameterSet(
                    mutation_rate=current_parameters.get("mutation_rate", 0.1),
                    crossover_rate=current_parameters.get("crossover_rate", 0.7),
                    selection_pressure=current_parameters.get("selection_pressure", 2.0),
                    population_size=current_parameters.get("population_size", 50),
                ),
                improvement_percentage=0.0,
                confidence_score=0.5,
                generations_tested=0,
                optimization_time=time.time() - start_time,
            )

    def recommend_parameters(self, population_state: Dict[str, Any]) -> Dict[str, float]:
        """
        Recommend parameters based on current population state

        Args:
            population_state: Current population statistics

        Returns:
            Recommended parameter values
        """
        try:
            avg_fitness = population_state.get("avg_fitness", 0.5)
            diversity = population_state.get("diversity", 0.5)
            stagnation_gens = population_state.get("stagnation_generations", 0)

            # Base recommendations
            recommendations = {
                "mutation_rate": 0.1,
                "crossover_rate": 0.7,
                "selection_pressure": 2.0,
                "population_size": 50,
            }

            # Adjust based on fitness level
            if avg_fitness < 0.3:
                # Low fitness - increase exploration
                recommendations["mutation_rate"] *= 1.5
                recommendations["crossover_rate"] *= 1.1
                recommendations["selection_pressure"] *= 0.8
            elif avg_fitness > 0.8:
                # High fitness - fine-tuning
                recommendations["mutation_rate"] *= 0.7
                recommendations["selection_pressure"] *= 1.3

            # Adjust based on diversity
            if diversity < 0.3:
                # Low diversity - increase exploration
                recommendations["mutation_rate"] *= 1.3
                recommendations["crossover_rate"] *= 1.2
            elif diversity > 0.8:
                # High diversity - increase exploitation
                recommendations["selection_pressure"] *= 1.2

            # Adjust for stagnation
            if stagnation_gens > 5:
                recommendations["mutation_rate"] *= 2.0
                recommendations["crossover_rate"] *= 1.3
                recommendations["selection_pressure"] *= 0.7

            # Apply bounds
            for param, value in recommendations.items():
                if param in self.parameter_bounds:
                    min_val, max_val = self.parameter_bounds[param]
                    recommendations[param] = max(min_val, min(max_val, value))

            return recommendations

        except Exception as e:
            logger.error(f"Parameter recommendation failed: {e}")
            return {"mutation_rate": 0.1, "crossover_rate": 0.7, "selection_pressure": 2.0}

    async def auto_tune(self, evolution_engine, optimization_budget: int = 100) -> Dict[str, float]:
        """
        Automatically tune parameters using the evolution engine

        Args:
            evolution_engine: Evolution engine instance
            optimization_budget: Maximum evaluations budget

        Returns:
            Optimized parameters
        """
        try:
            logger.info(f"Starting auto-tuning with budget {optimization_budget}")

            best_params = None
            best_score = 0.0
            evaluations = 0

            # Generate initial parameter sets
            param_population = self._generate_initial_population()

            while evaluations < optimization_budget:
                # Evaluate current population
                for param_set in param_population:
                    if evaluations >= optimization_budget:
                        break

                    # Test parameters with evolution engine
                    score = await self._evaluate_parameter_set(evolution_engine, param_set)
                    param_set.fitness_score = score

                    if score > best_score:
                        best_score = score
                        best_params = param_set

                    evaluations += 1
                    logger.debug(
                        f"Evaluated {evaluations}/{optimization_budget}: score={score:.4f}"
                    )

                # Evolve parameter population
                if evaluations < optimization_budget:
                    param_population = self._evolve_parameter_population(param_population)

            if best_params:
                return {
                    "mutation_rate": best_params.mutation_rate,
                    "crossover_rate": best_params.crossover_rate,
                    "selection_pressure": best_params.selection_pressure,
                    "population_size": best_params.population_size,
                }
            else:
                # Fallback to default parameters
                return {"mutation_rate": 0.1, "crossover_rate": 0.7, "selection_pressure": 2.0}

        except Exception as e:
            logger.error(f"Auto-tuning failed: {e}")
            return {"mutation_rate": 0.1, "crossover_rate": 0.7, "selection_pressure": 2.0}

    # Private helper methods

    def _analyze_performance(self, evolution_history: List[Dict]) -> float:
        """Analyze current evolution performance"""
        if not evolution_history:
            return 0.5

        recent_history = (
            evolution_history[-10:] if len(evolution_history) >= 10 else evolution_history
        )

        # Calculate average fitness improvement
        improvements = []
        for i in range(1, len(recent_history)):
            prev_fitness = recent_history[i - 1].get("best_fitness", 0)
            curr_fitness = recent_history[i].get("best_fitness", 0)
            improvement = curr_fitness - prev_fitness
            improvements.append(improvement)

        if improvements:
            avg_improvement = statistics.mean(improvements)
            # Normalize to 0-1 range
            normalized_score = max(0.0, min(1.0, 0.5 + avg_improvement * 5))
            return normalized_score

        return 0.5

    def _generate_parameter_candidates(
        self, current_params: Dict[str, Any], current_performance: float
    ) -> List[ParameterSet]:
        """Generate parameter candidates for evaluation"""
        import random

        candidates = []

        # Current parameters as baseline
        baseline = ParameterSet(
            mutation_rate=current_params.get("mutation_rate", 0.1),
            crossover_rate=current_params.get("crossover_rate", 0.7),
            selection_pressure=current_params.get("selection_pressure", 2.0),
            population_size=current_params.get("population_size", 50),
        )
        candidates.append(baseline)

        # Generate variations
        for _ in range(self.config["parameter_population_size"] - 1):
            candidate = ParameterSet(
                mutation_rate=self._mutate_parameter(
                    baseline.mutation_rate, "mutation_rate", current_performance
                ),
                crossover_rate=self._mutate_parameter(
                    baseline.crossover_rate, "crossover_rate", current_performance
                ),
                selection_pressure=self._mutate_parameter(
                    baseline.selection_pressure, "selection_pressure", current_performance
                ),
                population_size=int(
                    self._mutate_parameter(
                        baseline.population_size, "population_size", current_performance
                    )
                ),
            )
            candidates.append(candidate)

        return candidates

    def _mutate_parameter(self, value: float, param_name: str, performance: float) -> float:
        """Mutate a single parameter value"""
        import random

        if param_name not in self.parameter_bounds:
            return value

        min_val, max_val = self.parameter_bounds[param_name]

        # Mutation strength based on performance
        if performance < 0.3:
            mutation_strength = 0.3  # Large changes for poor performance
        elif performance > 0.7:
            mutation_strength = 0.1  # Small changes for good performance
        else:
            mutation_strength = 0.2  # Medium changes

        # Apply mutation
        change = random.uniform(-mutation_strength, mutation_strength) * value
        new_value = value + change

        # Apply bounds
        new_value = max(min_val, min(max_val, new_value))

        return new_value

    async def _evaluate_candidates(
        self, candidates: List[ParameterSet], evolution_history: List[Dict]
    ) -> List[ParameterSet]:
        """Evaluate parameter candidates using simulation"""
        try:
            # Simple evaluation based on historical patterns
            for candidate in candidates:
                # Simulate fitness based on parameter relationships
                fitness = self._simulate_parameter_fitness(candidate, evolution_history)
                candidate.fitness_score = fitness

            return candidates

        except Exception as e:
            logger.error(f"Candidate evaluation failed: {e}")
            return candidates

    def _simulate_parameter_fitness(self, params: ParameterSet, history: List[Dict]) -> float:
        """Simulate expected fitness for parameter set"""
        # Simplified fitness simulation
        base_fitness = 0.5

        # Mutation rate contribution
        if 0.05 <= params.mutation_rate <= 0.15:
            base_fitness += 0.1
        elif params.mutation_rate > 0.3:
            base_fitness -= 0.1

        # Crossover rate contribution
        if 0.6 <= params.crossover_rate <= 0.8:
            base_fitness += 0.1

        # Selection pressure contribution
        if 1.5 <= params.selection_pressure <= 3.0:
            base_fitness += 0.1

        # Population size contribution
        if 30 <= params.population_size <= 70:
            base_fitness += 0.1

        return max(0.0, min(1.0, base_fitness))

    def _select_best_parameters(
        self, candidates: List[ParameterSet], current_performance: float
    ) -> ParameterSet:
        """Select best parameter set from candidates"""
        if not candidates:
            return ParameterSet(0.1, 0.7, 2.0, 50)

        # Sort by fitness score
        candidates.sort(key=lambda x: x.fitness_score, reverse=True)

        best = candidates[0]

        # Only accept if significantly better than current
        if best.fitness_score > current_performance + self.config["min_improvement"]:
            return best
        else:
            # Return current parameters if no significant improvement
            return candidates[0]  # At least return the best candidate

    def _calculate_improvement(self, current_score: float, new_score: float) -> float:
        """Calculate improvement percentage"""
        if current_score == 0:
            return 100.0 if new_score > 0 else 0.0

        improvement = ((new_score - current_score) / current_score) * 100
        return max(0.0, improvement)

    def _calculate_confidence(self, candidates: List[ParameterSet]) -> float:
        """Calculate confidence in optimization result"""
        if len(candidates) < 2:
            return 0.5

        scores = [c.fitness_score for c in candidates]
        if not scores:
            return 0.5

        # Confidence based on variance in scores
        variance = statistics.variance(scores) if len(scores) > 1 else 0
        confidence = 1.0 - min(1.0, variance)

        return max(0.1, confidence)

    def _generate_initial_population(self) -> List[ParameterSet]:
        """Generate initial parameter population for auto-tuning"""
        import random

        population = []

        for _ in range(self.config["parameter_population_size"]):
            param_set = ParameterSet(
                mutation_rate=random.uniform(*self.parameter_bounds["mutation_rate"]),
                crossover_rate=random.uniform(*self.parameter_bounds["crossover_rate"]),
                selection_pressure=random.uniform(*self.parameter_bounds["selection_pressure"]),
                population_size=random.randint(
                    int(self.parameter_bounds["population_size"][0]),
                    int(self.parameter_bounds["population_size"][1]),
                ),
            )
            population.append(param_set)

        return population

    async def _evaluate_parameter_set(self, evolution_engine, param_set: ParameterSet) -> float:
        """Evaluate a parameter set using the evolution engine"""
        try:
            # This would run a short evolution with these parameters
            # For now, return simulated fitness
            return self._simulate_parameter_fitness(param_set, [])

        except Exception as e:
            logger.error(f"Parameter set evaluation failed: {e}")
            return 0.0

    def _evolve_parameter_population(self, population: List[ParameterSet]) -> List[ParameterSet]:
        """Evolve the parameter population using genetic operations"""
        import random

        # Sort by fitness
        population.sort(key=lambda x: x.fitness_score, reverse=True)

        # Keep top 50%
        survivors = population[: len(population) // 2]

        # Generate offspring
        offspring = []
        while len(offspring) < len(population) - len(survivors):
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)

            # Simple crossover
            child = ParameterSet(
                mutation_rate=(parent1.mutation_rate + parent2.mutation_rate) / 2,
                crossover_rate=(parent1.crossover_rate + parent2.crossover_rate) / 2,
                selection_pressure=(parent1.selection_pressure + parent2.selection_pressure) / 2,
                population_size=int((parent1.population_size + parent2.population_size) / 2),
            )

            # Apply mutation
            child.mutation_rate = self._mutate_parameter(
                child.mutation_rate, "mutation_rate", parent1.fitness_score
            )
            child.crossover_rate = self._mutate_parameter(
                child.crossover_rate, "crossover_rate", parent1.fitness_score
            )
            child.selection_pressure = self._mutate_parameter(
                child.selection_pressure, "selection_pressure", parent1.fitness_score
            )
            child.population_size = int(
                self._mutate_parameter(
                    child.population_size, "population_size", parent1.fitness_score
                )
            )

            offspring.append(child)

        return survivors + offspring

    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        if not self.optimization_history:
            return {"total_optimizations": 0, "average_improvement": 0.0}

        improvements = [opt.improvement_percentage for opt in self.optimization_history]

        return {
            "total_optimizations": len(self.optimization_history),
            "average_improvement": statistics.mean(improvements),
            "max_improvement": max(improvements),
            "average_confidence": statistics.mean(
                [opt.confidence_score for opt in self.optimization_history]
            ),
            "last_optimization_time": self.optimization_history[-1].optimization_time,
        }
