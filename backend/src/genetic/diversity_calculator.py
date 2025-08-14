"""Day 46: Genetic Diversity Calculator - 6.2KB"""
import math
import random
from collections import Counter
from typing import Any, Dict, List, Set, Tuple


class DiversityCalculator:
    """Calculate and manage genetic diversity in populations"""

    def __init__(self):
        """Initialize diversity calculator"""
        self.min_diversity_threshold = 0.3
        self.optimal_diversity = 0.7
        self.diversity_metrics = {
            "hamming": self._hamming_diversity,
            "euclidean": self._euclidean_diversity,
            "cosine": self._cosine_diversity,
            "jaccard": self._jaccard_diversity,
        }

    def hamming_distance(self, gene1: str, gene2: str) -> int:
        """Calculate Hamming distance between two gene sequences"""
        if len(gene1) != len(gene2):
            # Pad shorter sequence
            max_len = max(len(gene1), len(gene2))
            gene1 = gene1.ljust(max_len, "A")
            gene2 = gene2.ljust(max_len, "A")

        distance = sum(c1 != c2 for c1, c2 in zip(gene1, gene2))
        return distance

    def calculate_diversity(self, population: List["Genome"], metric: str = "hamming") -> float:
        """Calculate overall diversity of population"""
        if len(population) < 2:
            return 0.0

        # Use specified metric
        if metric in self.diversity_metrics:
            return self.diversity_metrics[metric](population)
        else:
            return self._hamming_diversity(population)

    def _hamming_diversity(self, population: List["Genome"]) -> float:
        """Calculate diversity using Hamming distance"""
        from backend.src.genetic.encoder import GeneEncoder
        from backend.src.genetic.genome import Genome

        encoder = GeneEncoder()
        sequences = []

        # Encode all genomes
        for genome in population:
            seq = encoder.encode_genome_sequence(genome.dna["genes"])
            sequences.append(seq)

        # Calculate pairwise distances
        total_distance = 0
        comparisons = 0

        for i in range(len(sequences)):
            for j in range(i + 1, min(i + 10, len(sequences))):
                distance = self.hamming_distance(sequences[i], sequences[j])
                # Normalize by sequence length
                if len(sequences[i]) > 0:
                    total_distance += distance / len(sequences[i])
                comparisons += 1

        if comparisons == 0:
            return 0.0

        return min(1.0, total_distance / comparisons)

    def _euclidean_diversity(self, population: List["Genome"]) -> float:
        """Calculate diversity using Euclidean distance"""
        vectors = []

        # Convert genomes to vectors
        for genome in population:
            genes = genome.dna["genes"]
            vector = [
                genes.get("memory", 0) / 6500.0,
                genes.get("speed", 0) / 3.0,
                genes.get("optimization", 0),
                genes.get("learning_rate", 0) * 10,
                genes.get("exploration", 0),
                genes.get("parallelism", 0) / 4.0,
                genes.get("cache_size", 0) / 100.0,
                genes.get("error_tolerance", 0),
            ]
            vectors.append(vector)

        # Calculate pairwise distances
        total_distance = 0
        comparisons = 0

        for i in range(len(vectors)):
            for j in range(i + 1, min(i + 10, len(vectors))):
                distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(vectors[i], vectors[j])))
                total_distance += distance
                comparisons += 1

        if comparisons == 0:
            return 0.0

        # Normalize (max distance in 8D unit cube is sqrt(8))
        return min(1.0, total_distance / (comparisons * math.sqrt(8)))

    def _cosine_diversity(self, population: List["Genome"]) -> float:
        """Calculate diversity using cosine similarity"""
        vectors = []

        for genome in population:
            genes = genome.dna["genes"]
            vector = [
                genes.get("memory", 0),
                genes.get("speed", 0),
                genes.get("optimization", 0),
                genes.get("learning_rate", 0),
                genes.get("parallelism", 0),
            ]
            vectors.append(vector)

        # Calculate average cosine similarity
        total_similarity = 0
        comparisons = 0

        for i in range(len(vectors)):
            for j in range(i + 1, min(i + 10, len(vectors))):
                # Cosine similarity
                dot_product = sum(a * b for a, b in zip(vectors[i], vectors[j]))
                mag1 = math.sqrt(sum(a**2 for a in vectors[i]))
                mag2 = math.sqrt(sum(b**2 for b in vectors[j]))

                if mag1 > 0 and mag2 > 0:
                    similarity = dot_product / (mag1 * mag2)
                    total_similarity += similarity
                    comparisons += 1

        if comparisons == 0:
            return 0.0

        avg_similarity = total_similarity / comparisons
        # Convert similarity to diversity (1 - similarity)
        return 1.0 - abs(avg_similarity)

    def _jaccard_diversity(self, population: List["Genome"]) -> float:
        """Calculate diversity using Jaccard distance on capabilities"""
        capability_sets = []

        for genome in population:
            caps = set(genome.dna["genes"].get("capabilities", []))
            capability_sets.append(caps)

        # Calculate pairwise Jaccard distances
        total_distance = 0
        comparisons = 0

        for i in range(len(capability_sets)):
            for j in range(i + 1, min(i + 10, len(capability_sets))):
                set1 = capability_sets[i]
                set2 = capability_sets[j]

                if len(set1.union(set2)) > 0:
                    jaccard = len(set1.intersection(set2)) / len(set1.union(set2))
                    distance = 1.0 - jaccard
                    total_distance += distance
                    comparisons += 1

        if comparisons == 0:
            return 0.0

        return total_distance / comparisons

    def is_diverse_enough(self, population: List["Genome"], threshold: float = None) -> bool:
        """Check if population meets diversity threshold"""
        if threshold is None:
            threshold = self.min_diversity_threshold

        diversity = self.calculate_diversity(population)
        return diversity >= threshold

    def suggest_diversity_boost(self, population: List["Genome"]) -> Dict[str, Any]:
        """Suggest actions to increase diversity"""
        diversity = self.calculate_diversity(population)
        suggestions = {}

        if diversity < self.min_diversity_threshold:
            # Critical low diversity
            suggestions["mutation_rate"] = 0.1  # High mutation
            suggestions["immigration_count"] = max(5, len(population) // 10)
            suggestions["crossover_points"] = 3  # More crossover points
            suggestions["selection_pressure"] = 0.5  # Lower pressure

        elif diversity < self.optimal_diversity:
            # Below optimal
            suggestions["mutation_rate"] = 0.05
            suggestions["immigration_count"] = max(2, len(population) // 20)
            suggestions["crossover_points"] = 2
            suggestions["selection_pressure"] = 0.7

        else:
            # Good diversity
            suggestions["mutation_rate"] = 0.01
            suggestions["immigration_count"] = 0
            suggestions["crossover_points"] = 1
            suggestions["selection_pressure"] = 0.9

        return suggestions

    def identify_clusters(self, population: List["Genome"]) -> List[List["Genome"]]:
        """Identify genetic clusters in population"""
        clusters = []
        unassigned = population.copy()

        while unassigned:
            # Start new cluster
            cluster = [unassigned.pop(0)]
            cluster_changed = True

            while cluster_changed:
                cluster_changed = False
                for genome in unassigned[:]:
                    # Check distance to cluster members
                    for member in cluster:
                        if genome.distance_to(member) < 0.3:
                            cluster.append(genome)
                            unassigned.remove(genome)
                            cluster_changed = True
                            break

            clusters.append(cluster)

        return clusters

    def shannon_diversity(self, population: List["Genome"]) -> float:
        """Calculate Shannon diversity index"""
        # Get trait distributions
        traits = []
        for genome in population:
            # Create trait signature
            genes = genome.dna["genes"]
            signature = (
                int(genes.get("memory", 0) / 1000),
                int(genes.get("speed", 0)),
                genes.get("architecture", "unknown"),
                len(genes.get("capabilities", [])),
            )
            traits.append(signature)

        # Count frequencies
        trait_counts = Counter(traits)
        total = len(traits)

        # Calculate Shannon index
        shannon = 0.0
        for count in trait_counts.values():
            if count > 0:
                proportion = count / total
                shannon -= proportion * math.log(proportion)

        # Normalize to [0, 1]
        if len(trait_counts) > 1:
            max_shannon = math.log(len(trait_counts))
            return shannon / max_shannon if max_shannon > 0 else 0
        return 0.0

    def niche_count(self, population: List["Genome"]) -> int:
        """Count number of distinct niches in population"""
        niches = set()

        for genome in population:
            genes = genome.dna["genes"]
            # Define niche by key characteristics
            niche = (
                genes.get("architecture", "unknown"),
                tuple(sorted(genes.get("capabilities", []))),
            )
            niches.add(niche)

        return len(niches)

    def recommend_parents(self, population: List["Genome"], count: int = 2) -> List["Genome"]:
        """Recommend diverse parents for breeding"""
        if len(population) < count:
            return population

        selected = []
        remaining = population.copy()

        # Select first parent randomly from top performers
        remaining.sort(key=lambda g: g.calculate_fitness(), reverse=True)
        first = remaining[random.randint(0, min(10, len(remaining) - 1))]
        selected.append(first)
        remaining.remove(first)

        # Select remaining parents for maximum diversity
        while len(selected) < count and remaining:
            max_distance = 0
            best_candidate = None

            for candidate in remaining[:20]:  # Check top 20
                min_distance = float("inf")
                for parent in selected:
                    distance = candidate.distance_to(parent)
                    min_distance = min(min_distance, distance)

                if min_distance > max_distance:
                    max_distance = min_distance
                    best_candidate = candidate

            if best_candidate:
                selected.append(best_candidate)
                remaining.remove(best_candidate)
            else:
                break

        return selected
