"""
Evolution Engine Core Implementation

This module handles the autonomous evolution of agents with 85% AI autonomy.
Implements genetic algorithms and self-improvement mechanisms.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import genetic algorithm components
try:
    from ..genetic.crossover.ai_crossover import AICrossover
    from ..genetic.crossover.effect_analyzer import CrossoverEffectAnalyzer
    from ..genetic.crossover.multi_point import MultiPointCrossover
    from ..genetic.mutation.ai_mutator import AIMutator
    from ..genetic.mutation.rate_controller import MutationRateController
    from ..genetic.mutation.validator import MutationValidator
    from ..genetic.selection.tournament import TournamentSelection
except ImportError:
    # Fallback for development
    AIMutator = None
    MutationRateController = None
    MutationValidator = None
    AICrossover = None
    MultiPointCrossover = None
    CrossoverEffectAnalyzer = None
    TournamentSelection = None
    logger.warning("Genetic algorithm components not available")

logger = logging.getLogger(__name__)


class EvolutionStatus(Enum):
    """Evolution status states"""

    IDLE = "idle"
    INITIALIZING = "initializing"
    EVOLVING = "evolving"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class EvolutionMetrics:
    """Metrics for tracking evolution performance"""

    generation: int = 0
    fitness_score: float = 0.0
    memory_usage_kb: float = 0.0
    instantiation_time_us: float = 0.0
    autonomy_level: float = 0.85
    safety_score: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EvolutionConfig:
    """Configuration for evolution engine"""

    max_generations: int = 100
    population_size: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    selection_pressure: float = 2.0
    memory_limit_kb: float = 6.5
    instantiation_limit_us: float = 3.0
    autonomy_target: float = 0.85
    safety_threshold: float = 0.95
    checkpoint_interval: int = 10
    enable_parallel: bool = True


class EvolutionEngine:
    """
    Core Evolution Engine for AI Autonomous System

    Handles genetic evolution of agents with strict constraints:
    - Memory limit: 6.5KB per agent
    - Instantiation time: < 3μs
    - AI autonomy: 85%
    """

    def __init__(self, config: Optional[EvolutionConfig] = None):
        """Initialize Evolution Engine with configuration"""
        self.config = config or EvolutionConfig()
        self.status = EvolutionStatus.IDLE
        self.current_generation = 0
        self.population: List[Dict[str, Any]] = []
        self.best_genome: Optional[Dict[str, Any]] = None
        self.metrics_history: List[EvolutionMetrics] = []
        self.checkpoints: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

        # Initialize paths
        self.evolution_dir = Path("/home/ec2-user/T-DeveloperMVP/backend/data/evolution")
        self.checkpoint_dir = self.evolution_dir / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Initialize genetic algorithm components
        self._initialize_genetic_components()

        logger.info(f"Evolution Engine initialized with config: {self.config}")

    async def initialize(self) -> bool:
        """
        Initialize evolution engine and validate environment

        Returns:
            bool: True if initialization successful
        """
        async with self._lock:
            try:
                self.status = EvolutionStatus.INITIALIZING
                logger.info("Initializing Evolution Engine...")

                # Validate environment
                if not await self._validate_environment():
                    raise RuntimeError("Environment validation failed")

                # Load or create initial population
                if not await self._initialize_population():
                    raise RuntimeError("Population initialization failed")

                # Set up monitoring
                await self._setup_monitoring()

                self.status = EvolutionStatus.IDLE
                logger.info("Evolution Engine initialized successfully")
                return True

            except Exception as e:
                logger.error(f"Initialization failed: {str(e)}")
                self.status = EvolutionStatus.FAILED
                return False

    def _initialize_genetic_components(self):
        """Initialize genetic algorithm components"""
        try:
            if AIMutator:
                self.ai_mutator = AIMutator(
                    {
                        "memory_limit_kb": self.config.memory_limit_kb,
                        "speed_limit_us": self.config.instantiation_limit_us,
                    }
                )
            else:
                self.ai_mutator = None

            if MutationRateController:
                self.rate_controller = MutationRateController(
                    {"base_rate": self.config.mutation_rate, "min_rate": 0.01, "max_rate": 0.5}
                )
            else:
                self.rate_controller = None

            if MutationValidator:
                self.mutation_validator = MutationValidator(
                    {
                        "memory_limit_kb": self.config.memory_limit_kb,
                        "speed_limit_us": self.config.instantiation_limit_us,
                    }
                )
            else:
                self.mutation_validator = None

            if AICrossover:
                self.ai_crossover = AICrossover(
                    {
                        "memory_limit_kb": self.config.memory_limit_kb,
                        "speed_limit_us": self.config.instantiation_limit_us,
                    }
                )
            else:
                self.ai_crossover = None

            if MultiPointCrossover:
                self.multi_point_crossover = MultiPointCrossover(
                    {"num_points": 2, "crossover_probability": self.config.crossover_rate}
                )
            else:
                self.multi_point_crossover = None

            if CrossoverEffectAnalyzer:
                self.crossover_analyzer = CrossoverEffectAnalyzer()
            else:
                self.crossover_analyzer = None

            if TournamentSelection:
                self.tournament_selection = TournamentSelection(
                    {
                        "tournament_size": int(self.config.selection_pressure * 2),
                        "pressure": self.config.selection_pressure,
                    }
                )
            else:
                self.tournament_selection = None

            logger.info("Genetic algorithm components initialized")
        except Exception as e:
            logger.error(f"Failed to initialize genetic components: {e}")
            # Set all components to None for fallback
            for attr in [
                "ai_mutator",
                "rate_controller",
                "mutation_validator",
                "ai_crossover",
                "multi_point_crossover",
                "crossover_analyzer",
                "tournament_selection",
            ]:
                setattr(self, attr, None)

    async def start_evolution(self, target_fitness: float = 0.95) -> bool:
        """
        Start the evolution process

        Args:
            target_fitness: Target fitness score to achieve

        Returns:
            bool: True if evolution completed successfully
        """
        async with self._lock:
            if self.status == EvolutionStatus.EVOLVING:
                logger.warning("Evolution already in progress")
                return False

            try:
                self.status = EvolutionStatus.EVOLVING
                logger.info(f"Starting evolution with target fitness: {target_fitness}")

                while self.current_generation < self.config.max_generations:
                    # Evaluate population fitness
                    await self._evaluate_population()

                    # Check if target reached
                    best_fitness = self._get_best_fitness()
                    if best_fitness >= target_fitness:
                        logger.info(
                            f"Target fitness {target_fitness} achieved at generation {self.current_generation}"
                        )
                        break

                    # Selection
                    parents = await self._selection()

                    # Crossover
                    offspring = await self._crossover(parents)

                    # Mutation
                    mutated = await self._mutation(offspring)

                    # Replace population
                    self.population = mutated

                    # Update metrics
                    await self._update_metrics()

                    # Checkpoint if needed
                    if self.current_generation % self.config.checkpoint_interval == 0:
                        await self._save_checkpoint()

                    self.current_generation += 1

                    # Safety check
                    if not await self._safety_check():
                        logger.error("Safety check failed, stopping evolution")
                        await self.emergency_stop()
                        return False

                self.status = EvolutionStatus.COMPLETED
                logger.info(f"Evolution completed at generation {self.current_generation}")
                return True

            except Exception as e:
                logger.error(f"Evolution failed: {str(e)}")
                self.status = EvolutionStatus.FAILED
                return False

    async def emergency_stop(self) -> bool:
        """
        Emergency stop for evolution process

        Returns:
            bool: True if stopped successfully
        """
        logger.warning("EMERGENCY STOP initiated")
        self.status = EvolutionStatus.ROLLED_BACK

        # Save current state
        await self._save_emergency_checkpoint()

        # Clear population
        self.population = []

        logger.info("Evolution stopped and state saved")
        return True

    async def rollback(self, checkpoint_id: Optional[str] = None) -> bool:
        """
        Rollback to a previous checkpoint

        Args:
            checkpoint_id: Specific checkpoint to rollback to (None for last safe)

        Returns:
            bool: True if rollback successful
        """
        try:
            if checkpoint_id:
                checkpoint_path = self.checkpoint_dir / f"checkpoint_{checkpoint_id}.json"
            else:
                # Find last safe checkpoint
                checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_*.json"))
                if not checkpoints:
                    logger.error("No checkpoints found")
                    return False
                checkpoint_path = checkpoints[-1]

            # Load checkpoint
            with open(checkpoint_path, "r") as f:
                checkpoint_data = json.load(f)

            # Restore state
            self.population = checkpoint_data["population"]
            self.current_generation = checkpoint_data["generation"]
            self.best_genome = checkpoint_data.get("best_genome")

            self.status = EvolutionStatus.ROLLED_BACK
            logger.info(f"Rolled back to checkpoint: {checkpoint_path.name}")
            return True

        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return False

    # Private helper methods

    async def _validate_environment(self) -> bool:
        """Validate environment constraints"""
        # Check memory limits
        import psutil

        available_memory = psutil.virtual_memory().available / 1024 / 1024  # MB
        if available_memory < 1000:  # Need at least 1GB
            logger.warning(f"Low memory: {available_memory:.2f}MB available")
            return False

        return True

    async def _initialize_population(self) -> bool:
        """Initialize the agent population"""
        try:
            # Create initial random population
            self.population = []
            for _ in range(self.config.population_size):
                genome = self._create_random_genome()
                self.population.append(genome)

            logger.info(f"Initialized population with {len(self.population)} agents")
            return True

        except Exception as e:
            logger.error(f"Population initialization failed: {str(e)}")
            return False

    def _create_random_genome(self) -> Dict[str, Any]:
        """Create a random genome for an agent"""
        import random

        return {
            "id": f"agent_{time.time()}_{random.randint(1000, 9999)}",
            "genes": {
                "layer_sizes": [random.randint(8, 32) for _ in range(random.randint(2, 4))],
                "activation": random.choice(["relu", "tanh", "sigmoid"]),
                "learning_rate": random.uniform(0.001, 0.1),
                "dropout_rate": random.uniform(0.1, 0.5),
                "optimizer": random.choice(["adam", "sgd", "rmsprop"]),
            },
            "fitness": 0.0,
            "metrics": {
                "memory_kb": 0.0,
                "instantiation_us": 0.0,
                "accuracy": 0.0,
            },
        }

    async def _setup_monitoring(self) -> None:
        """Set up monitoring for evolution process"""
        # This would integrate with CloudWatch or similar
        logger.info("Monitoring setup completed")

    async def _evaluate_population(self) -> None:
        """Evaluate fitness of all agents in population"""
        for genome in self.population:
            genome["fitness"] = await self._evaluate_fitness(genome)

    async def _evaluate_fitness(self, genome: Dict[str, Any]) -> float:
        """
        Evaluate fitness of a single genome

        Fitness is based on:
        - Accuracy/performance (40%)
        - Memory efficiency (30%)
        - Instantiation speed (20%)
        - Complexity penalty (10%)
        """
        import random  # Placeholder for actual evaluation

        # Simulate evaluation (replace with actual implementation)
        accuracy = random.uniform(0.6, 0.95)
        memory_kb = random.uniform(4.0, 8.0)
        instantiation_us = random.uniform(2.0, 5.0)

        # Calculate fitness components
        accuracy_score = accuracy * 0.4

        # Memory score (6.5KB limit)
        memory_score = (
            max(
                0,
                (self.config.memory_limit_kb - memory_kb) / self.config.memory_limit_kb,
            )
            * 0.3
        )

        # Speed score (3μs limit)
        speed_score = (
            max(
                0,
                (self.config.instantiation_limit_us - instantiation_us)
                / self.config.instantiation_limit_us,
            )
            * 0.2
        )

        # Complexity penalty
        complexity = len(genome["genes"]["layer_sizes"])
        complexity_score = max(0, 1 - (complexity / 10)) * 0.1

        fitness = accuracy_score + memory_score + speed_score + complexity_score

        # Update genome metrics
        genome["metrics"]["memory_kb"] = memory_kb
        genome["metrics"]["instantiation_us"] = instantiation_us
        genome["metrics"]["accuracy"] = accuracy

        return fitness

    def _get_best_fitness(self) -> float:
        """Get the best fitness score in current population"""
        if not self.population:
            return 0.0
        return max(g.get("fitness", 0.0) for g in self.population)

    async def _selection(self) -> List[Dict[str, Any]]:
        """
        Select parents for next generation using enhanced selection
        """
        try:
            if self.tournament_selection:
                # Use advanced tournament selection
                parents = await self.tournament_selection.select(
                    population=self.population,
                    num_parents=self.config.population_size,
                    fitness_key="fitness",
                )
                return parents
            else:
                # Fallback to simple tournament selection
                return await self._fallback_selection()
        except Exception as e:
            logger.error(f"Advanced selection failed: {e}")
            return await self._fallback_selection()

    async def _fallback_selection(self) -> List[Dict[str, Any]]:
        """Fallback selection method"""
        import random

        parents = []
        tournament_size = max(2, int(self.config.selection_pressure * 2))

        for _ in range(self.config.population_size):
            tournament = random.sample(self.population, min(tournament_size, len(self.population)))
            winner = max(tournament, key=lambda x: x["fitness"])
            parents.append(winner.copy())

        return parents

    async def _crossover(self, parents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform intelligent crossover between parents to create offspring
        """
        try:
            offspring = []

            # Calculate adaptive crossover rate if rate controller is available
            current_rate = self.config.crossover_rate
            if self.rate_controller:
                population_history = [
                    {
                        "generation": self.current_generation,
                        "best_fitness": self._get_best_fitness(),
                        "avg_fitness": self._get_average_fitness(),
                    }
                ]
                # Note: Rate controller is for mutation, but principle applies
                # Here we would need a crossover rate controller

            for i in range(0, len(parents) - 1, 2):
                parent1, parent2 = parents[i], parents[i + 1]

                if self._should_crossover(parent1, parent2, current_rate):
                    # Try AI-guided crossover first
                    if self.ai_crossover:
                        try:
                            child1, child2 = await self.ai_crossover.intelligent_crossover(
                                parent1, parent2
                            )
                            offspring.extend([child1, child2])

                            # Record crossover for analysis
                            if self.crossover_analyzer:
                                crossover_example = {
                                    "parent1": parent1,
                                    "parent2": parent2,
                                    "offspring": [child1, child2],
                                    "strategy": "ai_guided",
                                }
                                self.crossover_analyzer.learn_from_crossover(crossover_example)

                        except Exception as e:
                            logger.warning(f"AI crossover failed, using fallback: {e}")
                            child1, child2 = await self._fallback_crossover(parent1, parent2)
                            offspring.extend([child1, child2])
                    else:
                        # Use multi-point crossover
                        child1, child2 = await self._fallback_crossover(parent1, parent2)
                        offspring.extend([child1, child2])
                else:
                    # No crossover, keep parents
                    offspring.extend([parent1.copy(), parent2.copy()])

            # Handle odd number of parents
            if len(parents) % 2 == 1:
                offspring.append(parents[-1].copy())

            return offspring

        except Exception as e:
            logger.error(f"Advanced crossover failed: {e}")
            return await self._fallback_crossover_list(parents)

    def _should_crossover(self, parent1: Dict, parent2: Dict, rate: float) -> bool:
        """Determine if crossover should be performed"""
        import random

        # Basic probability check
        if random.random() >= rate:
            return False

        # Additional checks could be added here
        # e.g., fitness similarity, diversity considerations
        return True

    async def _fallback_crossover(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Fallback crossover method"""
        if self.multi_point_crossover:
            try:
                return await self.multi_point_crossover.crossover(parent1, parent2)
            except Exception as e:
                logger.warning(f"Multi-point crossover failed: {e}")

        # Ultimate fallback - single point crossover
        return self._single_point_crossover(parent1, parent2)

    async def _fallback_crossover_list(self, parents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback crossover for entire parent list"""
        import random

        offspring = []

        for i in range(0, len(parents) - 1, 2):
            parent1, parent2 = parents[i], parents[i + 1]

            if random.random() < self.config.crossover_rate:
                child1, child2 = self._single_point_crossover(parent1, parent2)
                offspring.extend([child1, child2])
            else:
                offspring.extend([parent1.copy(), parent2.copy()])

        if len(parents) % 2 == 1:
            offspring.append(parents[-1].copy())

        return offspring

    def _single_point_crossover(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Perform single-point crossover between two parents"""
        import random

        child1 = parent1.copy()
        child2 = parent2.copy()

        # Crossover genes
        genes1 = parent1["genes"].copy()
        genes2 = parent2["genes"].copy()

        # Random crossover point
        gene_keys = list(genes1.keys())
        crossover_point = random.randint(1, len(gene_keys) - 1)

        # Swap genes after crossover point
        for key in gene_keys[crossover_point:]:
            genes1[key], genes2[key] = genes2[key], genes1[key]

        child1["genes"] = genes1
        child2["genes"] = genes2

        # Reset fitness and metrics
        for child in [child1, child2]:
            child["fitness"] = 0.0
            child["id"] = f"agent_{time.time()}_{random.randint(1000, 9999)}"

        return child1, child2

    async def _mutation(self, offspring: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply intelligent mutation to offspring
        """
        try:
            # Calculate adaptive mutation rate
            current_rate = self.config.mutation_rate
            if self.rate_controller:
                population_history = self._build_population_history()
                current_rate = self.rate_controller.calculate_adaptive_rate(population_history)
                logger.debug(f"Adaptive mutation rate: {current_rate:.4f}")

            mutated_offspring = []

            for genome in offspring:
                if self._should_mutate(genome, current_rate):
                    # Try AI-guided mutation first
                    if self.ai_mutator:
                        try:
                            mutated_genome = await self.ai_mutator.guided_mutation(genome)

                            # Validate mutation if validator available
                            if mutated_genome and self.mutation_validator:
                                validation_result = await self.mutation_validator.validate_mutation(
                                    mutated_genome
                                )
                                if validation_result.is_valid:
                                    mutated_offspring.append(mutated_genome)
                                else:
                                    logger.warning(
                                        f"Mutation validation failed: {validation_result.violations}"
                                    )
                                    # Try fallback mutation
                                    fallback_mutated = await self._fallback_mutation(genome)
                                    mutated_offspring.append(fallback_mutated)
                            elif mutated_genome:
                                mutated_offspring.append(mutated_genome)
                            else:
                                # AI mutation failed, use fallback
                                fallback_mutated = await self._fallback_mutation(genome)
                                mutated_offspring.append(fallback_mutated)

                        except Exception as e:
                            logger.warning(f"AI mutation failed, using fallback: {e}")
                            fallback_mutated = await self._fallback_mutation(genome)
                            mutated_offspring.append(fallback_mutated)
                    else:
                        # Use fallback mutation
                        fallback_mutated = await self._fallback_mutation(genome)
                        mutated_offspring.append(fallback_mutated)
                else:
                    # No mutation
                    mutated_offspring.append(genome)

            return mutated_offspring

        except Exception as e:
            logger.error(f"Advanced mutation failed: {e}")
            return await self._fallback_mutation_list(offspring)

    def _should_mutate(self, genome: Dict, rate: float) -> bool:
        """Determine if mutation should be applied"""
        import random

        return random.random() < rate

    async def _fallback_mutation(self, genome: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback mutation method"""
        import random

        mutated = genome.copy()

        genes = mutated["genes"]
        gene_key = random.choice(list(genes.keys()))

        if gene_key == "layer_sizes":
            if random.random() < 0.5 and len(genes["layer_sizes"]) > 2:
                genes["layer_sizes"].pop(random.randint(0, len(genes["layer_sizes"]) - 1))
            else:
                if random.random() < 0.5:
                    genes["layer_sizes"].append(random.randint(8, 32))
                else:
                    idx = random.randint(0, len(genes["layer_sizes"]) - 1)
                    genes["layer_sizes"][idx] = random.randint(8, 32)

        elif gene_key == "learning_rate":
            genes["learning_rate"] *= random.uniform(0.5, 2.0)
            genes["learning_rate"] = max(0.0001, min(0.1, genes["learning_rate"]))

        elif gene_key == "dropout_rate":
            genes["dropout_rate"] = random.uniform(0.1, 0.5)

        elif gene_key == "activation":
            genes["activation"] = random.choice(["relu", "tanh", "sigmoid"])

        elif gene_key == "optimizer":
            genes["optimizer"] = random.choice(["adam", "sgd", "rmsprop"])

        # Update ID and reset fitness
        mutated["id"] = f"mutated_{int(time.time() * 1000000) % 1000000:06d}"
        mutated["fitness"] = 0.0

        return mutated

    async def _fallback_mutation_list(
        self, offspring: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Fallback mutation for entire offspring list"""
        mutated = []
        for genome in offspring:
            if self._should_mutate(genome, self.config.mutation_rate):
                mutated_genome = await self._fallback_mutation(genome)
                mutated.append(mutated_genome)
            else:
                mutated.append(genome)
        return mutated

    def _build_population_history(self) -> List[Dict]:
        """Build population history for rate adaptation"""
        return [
            {
                "generation": self.current_generation,
                "best_fitness": self._get_best_fitness(),
                "avg_fitness": self._get_average_fitness(),
            }
        ]

    def _get_average_fitness(self) -> float:
        """Get average fitness of current population"""
        if not self.population:
            return 0.0
        fitnesses = [g.get("fitness", 0.0) for g in self.population]
        return sum(fitnesses) / len(fitnesses)

    async def _update_metrics(self) -> None:
        """Update evolution metrics"""
        best_genome = max(self.population, key=lambda x: x["fitness"])
        self.best_genome = best_genome

        metrics = EvolutionMetrics(
            generation=self.current_generation,
            fitness_score=best_genome["fitness"],
            memory_usage_kb=best_genome["metrics"]["memory_kb"],
            instantiation_time_us=best_genome["metrics"]["instantiation_us"],
            autonomy_level=self.config.autonomy_target,
            safety_score=1.0,  # Will be calculated by safety check
        )

        self.metrics_history.append(metrics)

        logger.info(
            f"Generation {self.current_generation}: "
            f"Best fitness={metrics.fitness_score:.4f}, "
            f"Memory={metrics.memory_usage_kb:.2f}KB, "
            f"Speed={metrics.instantiation_time_us:.2f}μs"
        )

    async def _safety_check(self) -> bool:
        """
        Perform safety check on current evolution state

        Returns:
            bool: True if safe to continue
        """
        if not self.best_genome:
            return True

        # Check memory constraint
        if self.best_genome["metrics"]["memory_kb"] > self.config.memory_limit_kb:
            logger.warning(
                f"Memory limit exceeded: {self.best_genome['metrics']['memory_kb']}KB > {self.config.memory_limit_kb}KB"
            )
            return False

        # Check instantiation time
        if self.best_genome["metrics"]["instantiation_us"] > self.config.instantiation_limit_us:
            logger.warning(
                f"Instantiation time exceeded: {self.best_genome['metrics']['instantiation_us']}μs > {self.config.instantiation_limit_us}μs"
            )
            return False

        # Check for malicious patterns (placeholder)
        # This would include checks for:
        # - Infinite loops
        # - Excessive resource consumption
        # - Unauthorized operations
        # - Data exfiltration attempts

        return True

    async def _save_checkpoint(self) -> None:
        """Save current evolution state as checkpoint"""
        checkpoint_data = {
            "generation": self.current_generation,
            "population": self.population,
            "best_genome": self.best_genome,
            "metrics": [
                {
                    "generation": m.generation,
                    "fitness_score": m.fitness_score,
                    "memory_usage_kb": m.memory_usage_kb,
                    "instantiation_time_us": m.instantiation_time_us,
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in self.metrics_history[-10:]  # Last 10 metrics
            ],
            "timestamp": datetime.now().isoformat(),
        }

        checkpoint_file = self.checkpoint_dir / f"checkpoint_gen{self.current_generation:04d}.json"
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

        self.checkpoints.append(checkpoint_data)
        logger.info(f"Checkpoint saved: {checkpoint_file.name}")

    async def _save_emergency_checkpoint(self) -> None:
        """Save emergency checkpoint during emergency stop"""
        checkpoint_data = {
            "generation": self.current_generation,
            "population": self.population,
            "best_genome": self.best_genome,
            "status": "emergency_stop",
            "timestamp": datetime.now().isoformat(),
        }

        checkpoint_file = (
            self.checkpoint_dir / f"emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

        logger.info(f"Emergency checkpoint saved: {checkpoint_file.name}")


# CLI interface for direct execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evolution Engine CLI")
    parser.add_argument("--init", action="store_true", help="Initialize evolution engine")
    parser.add_argument("--start", action="store_true", help="Start evolution")
    parser.add_argument("--stop", action="store_true", help="Emergency stop")
    parser.add_argument("--rollback", action="store_true", help="Rollback to last checkpoint")
    parser.add_argument("--status", action="store_true", help="Show current status")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    async def main():
        engine = EvolutionEngine()

        if args.init:
            success = await engine.initialize()
            print(f"Initialization {'successful' if success else 'failed'}")

        elif args.start:
            if await engine.initialize():
                success = await engine.start_evolution()
                print(f"Evolution {'completed' if success else 'failed'}")

        elif args.stop:
            success = await engine.emergency_stop()
            print(f"Emergency stop {'successful' if success else 'failed'}")

        elif args.rollback:
            success = await engine.rollback()
            print(f"Rollback {'successful' if success else 'failed'}")

        elif args.status:
            print(f"Status: {engine.status.value}")
            print(f"Generation: {engine.current_generation}")
            if engine.best_genome:
                print(f"Best fitness: {engine.best_genome['fitness']:.4f}")

    asyncio.run(main())
