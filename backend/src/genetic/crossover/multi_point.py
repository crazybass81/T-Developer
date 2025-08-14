"""
Multi-Point Crossover Implementation

Advanced multi-point crossover with adaptive point selection
and compatibility checking for genetic evolution.
"""

import logging
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class CrossoverStrategy(Enum):
    """Available crossover strategies"""

    FIXED_POINTS = "fixed_points"
    ADAPTIVE_POINTS = "adaptive_points"
    GENE_IMPORTANCE = "gene_importance"
    FITNESS_WEIGHTED = "fitness_weighted"


@dataclass
class CrossoverPoint:
    """Represents a crossover point"""

    position: int
    gene_name: str
    importance: float
    compatibility_score: float


class MultiPointCrossover:
    """
    Multi-point crossover with intelligent point selection

    Features:
    - Adaptive number of crossover points
    - Gene importance-based selection
    - Parent compatibility checking
    - Constraint-aware crossover
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize multi-point crossover"""
        self.config = config or {
            "num_points": 2,
            "max_points": 4,
            "crossover_probability": 0.8,
            "adaptive_points": True,
            "memory_limit_kb": 6.5,
            "speed_limit_us": 3.0,
        }

        self.num_points = self.config["num_points"]
        self.crossover_probability = self.config["crossover_probability"]
        self.strategy = CrossoverStrategy.ADAPTIVE_POINTS

        # Gene importance weights (can be learned)
        self.gene_importance = {
            "layer_sizes": 0.9,
            "learning_rate": 0.8,
            "activation": 0.6,
            "dropout_rate": 0.7,
            "optimizer": 0.5,
        }

        self.crossover_history: List[Dict] = []

        logger.info("Multi-point crossover initialized")

    async def crossover(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Perform multi-point crossover between parents

        Args:
            parent1: First parent genome
            parent2: Second parent genome

        Returns:
            Tuple of two offspring genomes
        """
        try:
            # Check compatibility
            if not self.check_compatibility(parent1, parent2):
                logger.warning("Parents incompatible, using single-point crossover")
                return await self._single_point_fallback(parent1, parent2)

            # Select crossover points
            crossover_points = self.select_crossover_points(parent1, parent2)

            # Apply crossover with selected points
            offspring1, offspring2 = await self._apply_multi_point_crossover(
                parent1, parent2, crossover_points
            )

            # Validate offspring
            offspring1 = await self._validate_offspring(offspring1)
            offspring2 = await self._validate_offspring(offspring2)

            # Record crossover for learning
            self._record_crossover(parent1, parent2, offspring1, offspring2, crossover_points)

            return offspring1, offspring2

        except Exception as e:
            logger.error(f"Multi-point crossover failed: {e}")
            return await self._single_point_fallback(parent1, parent2)

    def select_crossover_points(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> List[CrossoverPoint]:
        """
        Select optimal crossover points based on strategy

        Returns:
            List of crossover points
        """
        genes1 = parent1.get("genes", {})
        genes2 = parent2.get("genes", {})
        gene_names = list(genes1.keys())

        if not gene_names:
            return []

        points = []

        if self.strategy == CrossoverStrategy.ADAPTIVE_POINTS:
            num_points = min(self._calculate_adaptive_points(parent1, parent2), len(gene_names))
        else:
            num_points = min(self.num_points, len(gene_names))

        # Select points based on gene importance
        gene_scores = []
        for i, gene_name in enumerate(gene_names):
            importance = self.gene_importance.get(gene_name, 0.5)
            compatibility = self._calculate_gene_compatibility(genes1[gene_name], genes2[gene_name])

            score = importance * 0.7 + compatibility * 0.3
            gene_scores.append((i, gene_name, score, importance, compatibility))

        # Sort by score and select top points
        gene_scores.sort(key=lambda x: x[2], reverse=True)

        for i in range(min(num_points, len(gene_scores))):
            pos, gene_name, score, importance, compatibility = gene_scores[i]
            points.append(
                CrossoverPoint(
                    position=pos,
                    gene_name=gene_name,
                    importance=importance,
                    compatibility_score=compatibility,
                )
            )

        return points

    def check_compatibility(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> bool:
        """
        Check if parents are compatible for crossover

        Returns:
            True if parents are compatible
        """
        genes1 = parent1.get("genes", {})
        genes2 = parent2.get("genes", {})

        # Check if they have the same gene structure
        if set(genes1.keys()) != set(genes2.keys()):
            return False

        # Check specific compatibility requirements
        for gene_name in genes1.keys():
            if not self._check_gene_compatibility(gene_name, genes1[gene_name], genes2[gene_name]):
                return False

        return True

    def optimize_crossover_points(self, gene_importance: Dict[str, float]) -> List[int]:
        """
        Optimize crossover points based on gene importance

        Args:
            gene_importance: Dictionary of gene importance scores

        Returns:
            List of optimal crossover point positions
        """
        sorted_genes = sorted(gene_importance.items(), key=lambda x: x[1], reverse=True)

        # Select top genes for crossover points
        num_points = min(self.config["max_points"], len(sorted_genes))
        optimal_points = []

        for i, (gene_name, importance) in enumerate(sorted_genes[:num_points]):
            if importance > 0.5:  # Only consider important genes
                optimal_points.append(i)

        return optimal_points

    def _estimate_memory_usage(self, genome: Dict[str, Any]) -> float:
        """Estimate memory usage for constraint checking"""
        genes = genome.get("genes", {})
        layer_sizes = genes.get("layer_sizes", [16, 32, 16])

        total_params = 0
        for i in range(len(layer_sizes) - 1):
            total_params += layer_sizes[i] * layer_sizes[i + 1]

        memory_kb = (total_params * 4 + 1024) / 1024
        return memory_kb

    async def _apply_multi_point_crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
        crossover_points: List[CrossoverPoint],
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Apply multi-point crossover at specified points"""

        # Deep copy parents
        offspring1 = self._deep_copy_genome(parent1)
        offspring2 = self._deep_copy_genome(parent2)

        # Reset offspring metadata
        offspring1["id"] = f"offspring_{int(time.time() * 1000000) % 1000000:06d}_1"
        offspring2["id"] = f"offspring_{int(time.time() * 1000000) % 1000000:06d}_2"
        offspring1["fitness"] = 0.0
        offspring2["fitness"] = 0.0

        # Apply crossover at each point
        genes1 = offspring1["genes"]
        genes2 = offspring2["genes"]

        # Sort points by position for proper crossover
        sorted_points = sorted(crossover_points, key=lambda x: x.position)

        # Alternate between parents at crossover points
        current_source = 1  # Start with parent1 as source

        for i, point in enumerate(sorted_points):
            gene_name = point.gene_name

            if current_source == 1:
                # Take from parent1 -> offspring1, parent2 -> offspring2
                genes1[gene_name] = parent1["genes"][gene_name]
                genes2[gene_name] = parent2["genes"][gene_name]
            else:
                # Swap sources
                genes1[gene_name] = parent2["genes"][gene_name]
                genes2[gene_name] = parent1["genes"][gene_name]

            # Switch source for next segment
            current_source = 2 if current_source == 1 else 1

        return offspring1, offspring2

    async def _validate_offspring(self, offspring: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix offspring if needed"""
        genes = offspring.get("genes", {})

        # Validate layer sizes
        if "layer_sizes" in genes:
            layer_sizes = genes["layer_sizes"]
            if isinstance(layer_sizes, list) and len(layer_sizes) > 0:
                # Ensure reasonable layer sizes
                genes["layer_sizes"] = [max(4, min(512, size)) for size in layer_sizes]
            else:
                genes["layer_sizes"] = [16, 32, 16]  # Default fallback

        # Validate learning rate
        if "learning_rate" in genes:
            lr = genes["learning_rate"]
            genes["learning_rate"] = max(0.0001, min(0.2, lr))

        # Validate dropout rate
        if "dropout_rate" in genes:
            dr = genes["dropout_rate"]
            genes["dropout_rate"] = max(0.0, min(0.9, dr))

        # Check memory constraint
        estimated_memory = self._estimate_memory_usage(offspring)
        if estimated_memory > self.config["memory_limit_kb"]:
            # Reduce complexity to meet memory constraint
            layer_sizes = genes.get("layer_sizes", [])
            if len(layer_sizes) > 2:
                # Remove a layer or reduce sizes
                if len(layer_sizes) > 3:
                    genes["layer_sizes"] = layer_sizes[:-1]
                else:
                    genes["layer_sizes"] = [max(8, size // 2) for size in layer_sizes]

        return offspring

    def _calculate_adaptive_points(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> int:
        """Calculate adaptive number of crossover points"""
        fitness1 = parent1.get("fitness", 0.0)
        fitness2 = parent2.get("fitness", 0.0)

        # More crossover points for high-fitness parents
        avg_fitness = (fitness1 + fitness2) / 2

        if avg_fitness > 0.8:
            return min(4, self.config["max_points"])
        elif avg_fitness > 0.6:
            return min(3, self.config["max_points"])
        else:
            return min(2, self.config["max_points"])

    def _calculate_gene_compatibility(self, gene1: Any, gene2: Any) -> float:
        """Calculate compatibility score between genes"""
        if type(gene1) != type(gene2):
            return 0.0

        if isinstance(gene1, list) and isinstance(gene2, list):
            if len(gene1) != len(gene2):
                return 0.3  # Different lengths but compatible type
            return 0.8

        if isinstance(gene1, (int, float)) and isinstance(gene2, (int, float)):
            # Numeric compatibility based on similarity
            if gene1 == 0 or gene2 == 0:
                return 0.5
            ratio = min(gene1, gene2) / max(gene1, gene2)
            return 0.5 + ratio * 0.5

        if isinstance(gene1, str) and isinstance(gene2, str):
            return 0.9 if gene1 == gene2 else 0.4

        return 0.5  # Default compatibility

    def _check_gene_compatibility(self, gene_name: str, gene1: Any, gene2: Any) -> bool:
        """Check if specific genes are compatible"""
        # Type compatibility
        if type(gene1) != type(gene2):
            return False

        # Special checks for specific genes
        if gene_name == "layer_sizes":
            if not isinstance(gene1, list) or not isinstance(gene2, list):
                return False
            # Both must be non-empty
            return len(gene1) > 0 and len(gene2) > 0

        return True

    async def _single_point_fallback(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Fallback to single-point crossover"""
        genes1 = parent1.get("genes", {})
        genes2 = parent2.get("genes", {})
        gene_names = list(genes1.keys())

        if not gene_names:
            return parent1.copy(), parent2.copy()

        # Single crossover point
        crossover_point = random.randint(1, len(gene_names) - 1)

        offspring1 = self._deep_copy_genome(parent1)
        offspring2 = self._deep_copy_genome(parent2)

        # Apply single-point crossover
        for i, gene_name in enumerate(gene_names):
            if i >= crossover_point:
                offspring1["genes"][gene_name] = parent2["genes"][gene_name]
                offspring2["genes"][gene_name] = parent1["genes"][gene_name]

        # Update IDs and reset fitness
        offspring1["id"] = f"singlept_{int(time.time() * 1000000) % 1000000:06d}_1"
        offspring2["id"] = f"singlept_{int(time.time() * 1000000) % 1000000:06d}_2"
        offspring1["fitness"] = 0.0
        offspring2["fitness"] = 0.0

        return offspring1, offspring2

    def _deep_copy_genome(self, genome: Dict[str, Any]) -> Dict[str, Any]:
        """Create deep copy of genome"""
        import json

        return json.loads(json.dumps(genome))

    def _record_crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
        offspring1: Dict[str, Any],
        offspring2: Dict[str, Any],
        crossover_points: List[CrossoverPoint],
    ) -> None:
        """Record crossover for learning purposes"""
        record = {
            "timestamp": time.time(),
            "parent_fitnesses": [parent1.get("fitness", 0), parent2.get("fitness", 0)],
            "crossover_points": len(crossover_points),
            "point_details": [
                {
                    "gene": p.gene_name,
                    "importance": p.importance,
                    "compatibility": p.compatibility_score,
                }
                for p in crossover_points
            ],
        }

        self.crossover_history.append(record)

        # Keep history manageable
        if len(self.crossover_history) > 500:
            self.crossover_history = self.crossover_history[-250:]
