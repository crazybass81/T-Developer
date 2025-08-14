"""
Uniform Crossover Implementation

Advanced uniform crossover with fitness-biased selection,
diversity preservation, and adaptive probability control.
"""

import logging
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class BiasStrategy(Enum):
    """Selection bias strategies"""

    NONE = "none"
    FITNESS_WEIGHTED = "fitness_weighted"
    DIVERSITY_PRESERVING = "diversity_preserving"
    PERFORMANCE_BASED = "performance_based"


class UniformCrossover:
    """
    Uniform crossover with intelligent gene selection

    Features:
    - Fitness-biased gene selection
    - Diversity preservation
    - Adaptive crossover probability
    - Constraint-aware crossover
    """

    def __init__(self, probability: float = 0.5, config: Optional[Dict] = None):
        """Initialize uniform crossover"""
        self.probability = probability
        self.config = config or {
            "memory_limit_kb": 6.5,
            "speed_limit_us": 3.0,
            "diversity_threshold": 0.3,
            "fitness_bias_strength": 0.3,
        }

        self.bias_strategy = BiasStrategy.FITNESS_WEIGHTED
        self.diversity_preservation = True
        self.adaptive_probability = True

        # Track selection statistics
        self.selection_stats = {
            "total_selections": 0,
            "parent1_selections": 0,
            "parent2_selections": 0,
            "diversity_preserved": 0,
        }

        logger.info(f"Uniform crossover initialized with probability {probability}")

    async def crossover(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Perform uniform crossover between parents

        Args:
            parent1: First parent genome
            parent2: Second parent genome

        Returns:
            Tuple of two offspring genomes
        """
        try:
            # Calculate selection probabilities
            selection_probs = self.calculate_selection_probabilities(parent1, parent2)

            # Adapt crossover probability if enabled
            if self.adaptive_probability:
                current_prob = self.adapt_probability(parent1, parent2)
            else:
                current_prob = self.probability

            # Create offspring
            offspring1 = self._create_offspring(parent1, parent2, selection_probs, current_prob)
            offspring2 = self._create_offspring(parent2, parent1, selection_probs, current_prob)

            # Ensure diversity if enabled
            if self.diversity_preservation:
                offspring1, offspring2 = self._preserve_diversity(
                    parent1, parent2, offspring1, offspring2
                )

            # Validate offspring
            offspring1 = await self._validate_offspring(offspring1)
            offspring2 = await self._validate_offspring(offspring2)

            # Update statistics
            self._update_statistics(parent1, parent2, offspring1, offspring2)

            return offspring1, offspring2

        except Exception as e:
            logger.error(f"Uniform crossover failed: {e}")
            # Return copies of parents as fallback
            return self._copy_parent(parent1), self._copy_parent(parent2)

    def calculate_selection_probabilities(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate gene selection probabilities based on bias strategy

        Returns:
            Dictionary with selection weights
        """
        fitness1 = parent1.get("fitness", 0.0)
        fitness2 = parent2.get("fitness", 0.0)

        if self.bias_strategy == BiasStrategy.NONE:
            return {"parent1_weight": 0.5, "parent2_weight": 0.5}

        elif self.bias_strategy == BiasStrategy.FITNESS_WEIGHTED:
            total_fitness = fitness1 + fitness2
            if total_fitness == 0:
                return {"parent1_weight": 0.5, "parent2_weight": 0.5}

            # Higher fitness gets higher probability
            bias_strength = self.config["fitness_bias_strength"]
            base_prob = 0.5

            fitness_advantage1 = (fitness1 - fitness2) * bias_strength
            prob1 = base_prob + fitness_advantage1
            prob1 = max(0.1, min(0.9, prob1))  # Keep within bounds
            prob2 = 1.0 - prob1

            return {"parent1_weight": prob1, "parent2_weight": prob2}

        elif self.bias_strategy == BiasStrategy.DIVERSITY_PRESERVING:
            # Favor genes that increase diversity
            diversity_score = self.calculate_diversity_score(parent1, parent2)
            if diversity_score < self.config["diversity_threshold"]:
                # Low diversity, favor different genes
                return {"parent1_weight": 0.3, "parent2_weight": 0.7}
            else:
                # High diversity, normal selection
                return {"parent1_weight": 0.5, "parent2_weight": 0.5}

        else:  # PERFORMANCE_BASED
            # Consider both fitness and constraint compliance
            perf1 = self._calculate_performance_score(parent1)
            perf2 = self._calculate_performance_score(parent2)

            total_perf = perf1 + perf2
            if total_perf == 0:
                return {"parent1_weight": 0.5, "parent2_weight": 0.5}

            return {"parent1_weight": perf1 / total_perf, "parent2_weight": perf2 / total_perf}

    def calculate_diversity_score(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> float:
        """
        Calculate diversity score between parents

        Returns:
            Diversity score (0-1, higher = more diverse)
        """
        genes1 = parent1.get("genes", {})
        genes2 = parent2.get("genes", {})

        if not genes1 or not genes2:
            return 0.0

        differences = 0
        total_genes = 0

        for gene_name in genes1.keys():
            if gene_name in genes2:
                total_genes += 1
                if not self._genes_equal(genes1[gene_name], genes2[gene_name]):
                    differences += 1

        return differences / max(total_genes, 1)

    def adapt_probability(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any], diversity: Optional[float] = None
    ) -> float:
        """
        Adapt crossover probability based on parent characteristics

        Returns:
            Adapted crossover probability
        """
        if diversity is None:
            diversity = self.calculate_diversity_score(parent1, parent2)

        base_prob = self.probability

        # Adjust based on diversity
        if diversity < 0.2:
            # Low diversity, increase crossover
            adapted_prob = base_prob * 1.3
        elif diversity > 0.8:
            # High diversity, reduce crossover slightly
            adapted_prob = base_prob * 0.9
        else:
            adapted_prob = base_prob

        # Adjust based on fitness levels
        fitness1 = parent1.get("fitness", 0.0)
        fitness2 = parent2.get("fitness", 0.0)
        avg_fitness = (fitness1 + fitness2) / 2

        if avg_fitness < 0.3:
            # Low fitness, more crossover for exploration
            adapted_prob *= 1.2
        elif avg_fitness > 0.8:
            # High fitness, careful crossover
            adapted_prob *= 0.8

        return max(0.1, min(0.9, adapted_prob))

    def _create_offspring(
        self,
        primary_parent: Dict[str, Any],
        secondary_parent: Dict[str, Any],
        selection_probs: Dict[str, float],
        crossover_prob: float,
    ) -> Dict[str, Any]:
        """Create offspring using uniform selection"""

        offspring = self._copy_parent(primary_parent)

        genes1 = primary_parent.get("genes", {})
        genes2 = secondary_parent.get("genes", {})

        # Generate new ID
        offspring["id"] = f"uniform_{int(time.time() * 1000000) % 1000000:06d}"
        offspring["fitness"] = 0.0

        # Uniform gene selection
        for gene_name in genes1.keys():
            if gene_name in genes2:
                # Decide which parent to take gene from
                if random.random() < crossover_prob:
                    # Apply crossover - choose based on selection probabilities
                    prob_primary = selection_probs.get("parent1_weight", 0.5)
                    if primary_parent == genes1 and random.random() > prob_primary:
                        offspring["genes"][gene_name] = genes2[gene_name]
                    elif primary_parent != genes1 and random.random() < prob_primary:
                        offspring["genes"][gene_name] = genes1[gene_name]
                # else keep gene from primary parent (no crossover for this gene)

        return offspring

    def _preserve_diversity(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
        offspring1: Dict[str, Any],
        offspring2: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Ensure diversity preservation in offspring

        Returns:
            Tuple of diversity-preserved offspring
        """
        # Check if offspring are too similar to parents or each other
        diversity_parent1 = self.calculate_diversity_score(offspring1, parent1)
        diversity_parent2 = self.calculate_diversity_score(offspring2, parent2)
        diversity_offspring = self.calculate_diversity_score(offspring1, offspring2)

        min_diversity = self.config["diversity_threshold"]

        # If offspring are too similar to parents, inject some mutations
        if diversity_parent1 < min_diversity:
            offspring1 = self._inject_diversity(offspring1, parent1)

        if diversity_parent2 < min_diversity:
            offspring2 = self._inject_diversity(offspring2, parent2)

        # If offspring are too similar to each other, diversify one
        if diversity_offspring < min_diversity:
            offspring2 = self._inject_diversity(offspring2, offspring1)

        return offspring1, offspring2

    def _inject_diversity(
        self, target: Dict[str, Any], reference: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Inject diversity into target genome"""
        genes = target.get("genes", {})
        ref_genes = reference.get("genes", {})

        # Select a random gene to diversify
        gene_names = list(genes.keys())
        if not gene_names:
            return target

        gene_to_diversify = random.choice(gene_names)

        if gene_to_diversify == "learning_rate":
            # Modify learning rate
            current_lr = genes.get("learning_rate", 0.01)
            genes["learning_rate"] = current_lr * random.uniform(0.7, 1.5)
            genes["learning_rate"] = max(0.0001, min(0.2, genes["learning_rate"]))

        elif gene_to_diversify == "dropout_rate":
            # Modify dropout rate
            genes["dropout_rate"] = random.uniform(0.1, 0.6)

        elif gene_to_diversify == "activation" and gene_to_diversify in ref_genes:
            # Choose different activation
            activations = ["relu", "tanh", "sigmoid", "leaky_relu"]
            current = genes.get("activation", "relu")
            available = [a for a in activations if a != current]
            if available:
                genes["activation"] = random.choice(available)

        elif gene_to_diversify == "layer_sizes":
            # Slightly modify layer sizes
            layer_sizes = genes.get("layer_sizes", [16, 32, 16]).copy()
            if layer_sizes:
                idx = random.randint(0, len(layer_sizes) - 1)
                layer_sizes[idx] = max(4, int(layer_sizes[idx] * random.uniform(0.8, 1.3)))
                genes["layer_sizes"] = layer_sizes

        return target

    async def _validate_offspring(self, offspring: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and repair offspring if necessary"""
        genes = offspring.get("genes", {})

        # Validate numeric ranges
        if "learning_rate" in genes:
            lr = genes["learning_rate"]
            genes["learning_rate"] = max(0.0001, min(0.2, lr))

        if "dropout_rate" in genes:
            dr = genes["dropout_rate"]
            genes["dropout_rate"] = max(0.0, min(0.9, dr))

        # Validate layer sizes
        if "layer_sizes" in genes:
            layer_sizes = genes["layer_sizes"]
            if not isinstance(layer_sizes, list) or len(layer_sizes) == 0:
                genes["layer_sizes"] = [16, 32, 16]  # Default
            else:
                genes["layer_sizes"] = [max(4, min(512, size)) for size in layer_sizes]

        # Check memory constraint
        if self._estimate_memory_usage(offspring) > self.config["memory_limit_kb"]:
            genes = self._reduce_memory_usage(genes)

        return offspring

    def _estimate_memory_usage(self, genome: Dict[str, Any]) -> float:
        """Estimate memory usage in KB"""
        genes = genome.get("genes", {})
        layer_sizes = genes.get("layer_sizes", [16, 32, 16])

        total_params = 0
        for i in range(len(layer_sizes) - 1):
            total_params += layer_sizes[i] * layer_sizes[i + 1]

        memory_kb = (total_params * 4 + 1024) / 1024
        return memory_kb

    def _reduce_memory_usage(self, genes: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce memory usage to meet constraints"""
        layer_sizes = genes.get("layer_sizes", [])

        if len(layer_sizes) > 3:
            # Remove a layer
            genes["layer_sizes"] = layer_sizes[:-1]
        elif len(layer_sizes) > 0:
            # Reduce layer sizes
            genes["layer_sizes"] = [max(4, size // 2) for size in layer_sizes]

        return genes

    def _calculate_performance_score(self, parent: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        fitness = parent.get("fitness", 0.0)
        metrics = parent.get("metrics", {})

        memory_kb = metrics.get("memory_kb", 3.0)
        speed_us = metrics.get("instantiation_us", 2.0)

        # Penalty for constraint violations
        memory_penalty = max(0, memory_kb - self.config["memory_limit_kb"]) * 0.1
        speed_penalty = max(0, speed_us - self.config["speed_limit_us"]) * 0.1

        performance = fitness - memory_penalty - speed_penalty
        return max(0.0, performance)

    def _genes_equal(self, gene1: Any, gene2: Any) -> bool:
        """Check if two genes are equal"""
        if type(gene1) != type(gene2):
            return False

        if isinstance(gene1, list):
            return len(gene1) == len(gene2) and all(g1 == g2 for g1, g2 in zip(gene1, gene2))

        return gene1 == gene2

    def _copy_parent(self, parent: Dict[str, Any]) -> Dict[str, Any]:
        """Create deep copy of parent"""
        import json

        return json.loads(json.dumps(parent))

    def _update_statistics(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
        offspring1: Dict[str, Any],
        offspring2: Dict[str, Any],
    ) -> None:
        """Update selection statistics"""
        self.selection_stats["total_selections"] += 1

        # Track diversity preservation
        diversity_preserved = (
            self.calculate_diversity_score(offspring1, parent1)
            >= self.config["diversity_threshold"]
            or self.calculate_diversity_score(offspring2, parent2)
            >= self.config["diversity_threshold"]
        )

        if diversity_preserved:
            self.selection_stats["diversity_preserved"] += 1

    def get_selection_statistics(self) -> Dict[str, Any]:
        """Get current selection statistics"""
        total = max(1, self.selection_stats["total_selections"])
        return {
            "total_crossovers": total,
            "diversity_preservation_rate": self.selection_stats["diversity_preserved"] / total,
            "bias_strategy": self.bias_strategy.value,
            "current_probability": self.probability,
        }
