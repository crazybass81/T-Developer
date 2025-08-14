"""Day 46: Gene Pool Management System - 6.3KB"""
import random
from collections import defaultdict
from typing import Any, Dict, List, Optional


class GenePool:
    """Manages population of genomes with selection and evolution"""

    def __init__(self, size: int = 100):
        """Initialize gene pool with given size"""
        from backend.src.genetic.genome import Genome

        self.size = size
        self.genomes: List[Genome] = []
        self.generation = 0
        self.history = []
        self.elite_ratio = 0.1
        self.mutation_rate = 0.01

        # Initialize population
        for _ in range(size):
            self.genomes.append(Genome())

        # Track statistics
        self.stats = {
            "total_genomes_created": size,
            "total_mutations": 0,
            "total_crossovers": 0,
            "best_fitness_history": [],
            "avg_fitness_history": [],
            "diversity_history": [],
        }

    def add(self, genome: "Genome") -> None:
        """Add new genome to the pool"""
        self.genomes.append(genome)
        self.stats["total_genomes_created"] += 1

        # Maintain size limit
        if len(self.genomes) > self.size * 1.5:
            self.cull_weak(keep_ratio=0.67)

    def remove(self, genome: "Genome") -> None:
        """Remove genome from the pool"""
        if genome in self.genomes:
            self.genomes.remove(genome)

    def cull_weak(self, keep_ratio: float = 0.5) -> None:
        """Remove weakest genomes from pool"""
        # Sort by fitness
        self.genomes.sort(key=lambda g: g.calculate_fitness(), reverse=True)

        # Keep only top performers
        keep_count = max(1, int(len(self.genomes) * keep_ratio))
        removed = self.genomes[keep_count:]
        self.genomes = self.genomes[:keep_count]

        # Track removed genomes
        for genome in removed:
            self.history.append(
                {
                    "generation": self.generation,
                    "action": "culled",
                    "fitness": genome.calculate_fitness(),
                }
            )

    def get_elite(self, count: Optional[int] = None) -> List["Genome"]:
        """Get elite genomes from pool"""
        if count is None:
            count = max(1, int(len(self.genomes) * self.elite_ratio))

        # Sort by fitness
        sorted_genomes = sorted(self.genomes, key=lambda g: g.calculate_fitness(), reverse=True)

        return sorted_genomes[:count]

    def get_random(self, count: int = 1) -> List["Genome"]:
        """Get random genomes from pool"""
        count = min(count, len(self.genomes))
        return random.sample(self.genomes, count)

    def tournament_select(self, tournament_size: int = 3) -> "Genome":
        """Select genome using tournament selection"""
        tournament = random.sample(self.genomes, min(tournament_size, len(self.genomes)))
        return max(tournament, key=lambda g: g.calculate_fitness())

    def roulette_select(self) -> "Genome":
        """Select genome using roulette wheel selection"""
        # Calculate total fitness
        fitnesses = [g.calculate_fitness() for g in self.genomes]
        total_fitness = sum(fitnesses)

        if total_fitness == 0:
            return random.choice(self.genomes)

        # Create roulette wheel
        selection_point = random.uniform(0, total_fitness)
        current_sum = 0

        for genome, fitness in zip(self.genomes, fitnesses):
            current_sum += fitness
            if current_sum >= selection_point:
                return genome

        return self.genomes[-1]  # Fallback

    def breed(self, parent1: "Genome", parent2: "Genome") -> "Genome":
        """Create offspring from two parent genomes"""
        # Crossover
        offspring = parent1.crossover(parent2)

        # Apply mutation
        if random.random() < self.mutation_rate:
            offspring.mutate(self.mutation_rate)
            self.stats["total_mutations"] += 1

        self.stats["total_crossovers"] += 1
        return offspring

    def evolve_generation(self) -> None:
        """Evolve pool to next generation"""
        from backend.src.genetic.genome import Genome

        new_genomes = []

        # Keep elite genomes
        elite = self.get_elite()
        new_genomes.extend(elite)

        # Generate offspring
        while len(new_genomes) < self.size:
            # Select parents
            parent1 = self.tournament_select()
            parent2 = self.tournament_select()

            # Create offspring
            if parent1 != parent2:
                offspring = self.breed(parent1, parent2)
                new_genomes.append(offspring)
            else:
                # If same parent selected, just mutate
                offspring = Genome(parent1.dna.copy())
                offspring.mutate(self.mutation_rate * 2)
                new_genomes.append(offspring)

        # Replace population
        self.genomes = new_genomes[: self.size]
        self.generation += 1

        # Update statistics
        self._update_statistics()

    def diversity_score(self) -> float:
        """Calculate diversity score of the pool"""
        if len(self.genomes) < 2:
            return 0.0

        total_distance = 0.0
        comparisons = 0

        # Sample random pairs to calculate diversity
        sample_size = min(50, len(self.genomes))
        sample = random.sample(self.genomes, sample_size)

        for i in range(len(sample)):
            for j in range(i + 1, len(sample)):
                total_distance += sample[i].distance_to(sample[j])
                comparisons += 1

        if comparisons == 0:
            return 0.0

        return total_distance / comparisons

    def get_statistics(self) -> Dict[str, Any]:
        """Get pool statistics"""
        fitnesses = [g.calculate_fitness() for g in self.genomes]

        return {
            "size": len(self.genomes),
            "generation": self.generation,
            "avg_fitness": sum(fitnesses) / len(fitnesses) if fitnesses else 0,
            "best_fitness": max(fitnesses) if fitnesses else 0,
            "worst_fitness": min(fitnesses) if fitnesses else 0,
            "diversity": self.diversity_score(),
            "total_mutations": self.stats["total_mutations"],
            "total_crossovers": self.stats["total_crossovers"],
            "elite_count": len(self.get_elite()),
        }

    def _update_statistics(self) -> None:
        """Update internal statistics tracking"""
        stats = self.get_statistics()

        self.stats["best_fitness_history"].append(stats["best_fitness"])
        self.stats["avg_fitness_history"].append(stats["avg_fitness"])
        self.stats["diversity_history"].append(stats["diversity"])

        # Keep history limited
        max_history = 100
        for key in ["best_fitness_history", "avg_fitness_history", "diversity_history"]:
            if len(self.stats[key]) > max_history:
                self.stats[key] = self.stats[key][-max_history:]

    def find_by_traits(self, traits: Dict[str, Any]) -> List["Genome"]:
        """Find genomes matching specific traits"""
        matches = []

        for genome in self.genomes:
            genes = genome.dna["genes"]
            match = True

            for key, value in traits.items():
                if key in genes:
                    if isinstance(value, (int, float)):
                        # Numeric comparison with tolerance
                        if abs(genes[key] - value) > 0.1:
                            match = False
                            break
                    elif isinstance(value, list):
                        # List comparison
                        if set(genes[key]) != set(value):
                            match = False
                            break
                    else:
                        # Direct comparison
                        if genes[key] != value:
                            match = False
                            break

            if match:
                matches.append(genome)

        return matches

    def inject_diversity(self, count: int = 10) -> None:
        """Inject new random genomes for diversity"""
        from backend.src.genetic.genome import Genome

        for _ in range(count):
            new_genome = Genome()
            # Apply stronger mutations for diversity
            new_genome.mutate(rate=0.3)
            self.add(new_genome)

    def save_elite(self, count: int = 5) -> List[Dict[str, Any]]:
        """Save elite genomes for later restoration"""
        elite = self.get_elite(count)
        saved = []

        for genome in elite:
            saved.append(
                {
                    "dna": genome.dna.copy(),
                    "fitness": genome.calculate_fitness(),
                    "generation": self.generation,
                }
            )

        return saved

    def load_genomes(self, saved: List[Dict[str, Any]]) -> None:
        """Load saved genomes into pool"""
        from backend.src.genetic.genome import Genome

        for save_data in saved:
            genome = Genome(save_data["dna"])
            self.add(genome)

    def get_convergence_metric(self) -> float:
        """Calculate convergence metric (0=diverse, 1=converged)"""
        if len(self.stats["best_fitness_history"]) < 10:
            return 0.0

        # Check fitness plateau
        recent = self.stats["best_fitness_history"][-10:]
        variance = max(recent) - min(recent)

        # Check diversity decline
        diversity = self.diversity_score()

        # Combined metric
        convergence = (1.0 - variance) * 0.5 + (1.0 - diversity) * 0.5
        return max(0.0, min(1.0, convergence))
