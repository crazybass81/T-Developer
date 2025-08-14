"""Day 47: Elite Selection Algorithm - 6.1KB"""
import random
from collections import deque
from typing import Any, Dict, List, Optional, Tuple


class EliteSelector:
    """Elite selection strategy for genetic algorithms"""

    def __init__(self):
        """Initialize elite selector"""
        self.elite_history = deque(maxlen=100)
        self.generation_count = 0
        self.hall_of_fame = []  # Best individuals ever
        self.hall_of_fame_size = 10
        self.stats = {
            "avg_elite_fitness": 0.0,
            "elite_improvement_rate": 0.0,
            "elite_diversity": 0.0,
            "total_elite_selected": 0,
        }

    def select(self, population: List["Genome"], elite_size: int) -> List["Genome"]:
        """Select elite individuals from population"""
        if not population:
            return []

        if elite_size >= len(population):
            return population.copy()

        # Sort by fitness
        sorted_pop = sorted(population, key=lambda g: g.calculate_fitness(), reverse=True)

        # Select top individuals
        elite = sorted_pop[:elite_size]

        # Update statistics and history
        self._update_elite_history(elite)
        self._update_hall_of_fame(elite)

        return elite

    def select_by_ratio(self, population: List["Genome"], ratio: float) -> List["Genome"]:
        """Select elite by percentage of population"""
        if not population:
            return []

        elite_size = max(1, int(len(population) * ratio))
        return self.select(population, elite_size)

    def select_with_diversity(
        self, population: List["Genome"], elite_size: int, diversity_weight: float = 0.3
    ) -> List["Genome"]:
        """Select elite considering both fitness and diversity"""
        if elite_size >= len(population):
            return population.copy()

        # Calculate combined scores
        scores = []
        for individual in population:
            fitness_score = individual.calculate_fitness()

            # Calculate diversity contribution
            diversity_score = self._calculate_diversity_contribution(individual, population)

            # Combined score
            combined = fitness_score * (1 - diversity_weight) + diversity_score * diversity_weight
            scores.append((individual, combined))

        # Sort by combined score
        scores.sort(key=lambda x: x[1], reverse=True)

        # Select top individuals
        elite = [ind for ind, _ in scores[:elite_size]]

        self._update_elite_history(elite)
        return elite

    def tiered_elite(
        self, population: List["Genome"], tiers: List[Tuple[float, int]]
    ) -> List["Genome"]:
        """Select elite in tiers with different criteria"""
        elite = []
        remaining = population.copy()

        for tier_ratio, tier_size in tiers:
            if not remaining or tier_size == 0:
                break

            # Select from remaining population
            tier_elite = self.select(remaining, tier_size)
            elite.extend(tier_elite)

            # Remove selected from remaining
            for ind in tier_elite:
                remaining.remove(ind)

        return elite

    def adaptive_elite(
        self, population: List["Genome"], generation: int, base_ratio: float = 0.1
    ) -> List["Genome"]:
        """Adaptively adjust elite size based on generation"""
        # Start with more exploration, gradually increase elitism
        max_ratio = 0.3
        min_ratio = 0.05

        # Sigmoid-like progression
        import math

        progress = generation / 100.0  # Normalize to typical run length
        factor = 1 / (1 + math.exp(-5 * (progress - 0.5)))

        # Interpolate ratio
        ratio = min_ratio + (max_ratio - min_ratio) * factor
        ratio = min(max_ratio, max(min_ratio, ratio))

        return self.select_by_ratio(population, ratio)

    def preserve_elite(
        self, old_population: List["Genome"], new_population: List["Genome"], preserve_count: int
    ) -> List["Genome"]:
        """Ensure best individuals survive to next generation"""
        # Get elite from old population
        old_elite = self.select(old_population, preserve_count)

        # Get worst individuals in new population
        new_sorted = sorted(new_population, key=lambda g: g.calculate_fitness())

        # Replace worst with elite
        result = new_sorted[preserve_count:] + old_elite

        # Shuffle to avoid position bias
        random.shuffle(result)

        return result

    def multi_objective_elite(
        self, population: List["Genome"], objectives: Dict[str, float], elite_size: int
    ) -> List["Genome"]:
        """Select elite based on multiple objectives"""
        # Calculate Pareto front
        pareto_front = self._find_pareto_front(population, objectives)

        if len(pareto_front) <= elite_size:
            # If Pareto front is small enough, take all
            elite = pareto_front

            # Fill remaining with best overall
            if len(elite) < elite_size:
                remaining = [p for p in population if p not in elite]
                remaining.sort(key=lambda g: g.calculate_fitness(), reverse=True)
                elite.extend(remaining[: elite_size - len(elite)])
        else:
            # Select from Pareto front using crowding distance
            elite = self._select_from_pareto(pareto_front, elite_size)

        self._update_elite_history(elite)
        return elite

    def _find_pareto_front(
        self, population: List["Genome"], objectives: Dict[str, float]
    ) -> List["Genome"]:
        """Find Pareto-optimal individuals"""
        pareto_front = []

        for candidate in population:
            dominated = False

            for other in population:
                if candidate == other:
                    continue

                # Check if other dominates candidate
                if self._dominates(other, candidate, objectives):
                    dominated = True
                    break

            if not dominated:
                pareto_front.append(candidate)

        return pareto_front

    def _dominates(self, ind1: "Genome", ind2: "Genome", objectives: Dict[str, float]) -> bool:
        """Check if ind1 dominates ind2"""
        better_in_any = False

        for obj_name, weight in objectives.items():
            val1 = self._get_objective_value(ind1, obj_name)
            val2 = self._get_objective_value(ind2, obj_name)

            if weight > 0:  # Maximize
                if val1 < val2:
                    return False
                if val1 > val2:
                    better_in_any = True
            else:  # Minimize
                if val1 > val2:
                    return False
                if val1 < val2:
                    better_in_any = True

        return better_in_any

    def _get_objective_value(self, genome: "Genome", objective: str) -> float:
        """Get objective value for genome"""
        if objective == "fitness":
            return genome.calculate_fitness()
        elif objective == "size":
            return genome.dna["genes"].get("memory", 0)
        elif objective == "speed":
            return genome.dna["genes"].get("speed", 0)
        elif objective == "diversity":
            return len(genome.dna["genes"].get("capabilities", []))
        else:
            return 0.0

    def _select_from_pareto(self, pareto_front: List["Genome"], count: int) -> List["Genome"]:
        """Select from Pareto front using crowding distance"""
        # Simple selection: random sample
        # Could implement crowding distance for better diversity
        return random.sample(pareto_front, count)

    def _calculate_diversity_contribution(
        self, individual: "Genome", population: List["Genome"]
    ) -> float:
        """Calculate how much diversity an individual adds"""
        # Average distance to others
        distances = []
        sample_size = min(20, len(population))
        sample = random.sample(population, sample_size)

        for other in sample:
            if other != individual:
                distances.append(individual.distance_to(other))

        if not distances:
            return 0.0

        return sum(distances) / len(distances)

    def _update_elite_history(self, elite: List["Genome"]) -> None:
        """Update elite history and statistics"""
        if not elite:
            return

        fitnesses = [g.calculate_fitness() for g in elite]
        avg_fitness = sum(fitnesses) / len(fitnesses)

        self.elite_history.append(
            {
                "generation": self.generation_count,
                "avg_fitness": avg_fitness,
                "best_fitness": max(fitnesses),
                "size": len(elite),
            }
        )

        # Update running statistics
        alpha = 0.1
        self.stats["avg_elite_fitness"] = (1 - alpha) * self.stats[
            "avg_elite_fitness"
        ] + alpha * avg_fitness

        self.stats["total_elite_selected"] += len(elite)
        self.generation_count += 1

    def _update_hall_of_fame(self, elite: List["Genome"]) -> None:
        """Update hall of fame with best individuals ever"""
        # Add new elite to hall of fame
        self.hall_of_fame.extend(elite)

        # Keep only unique and best
        seen = set()
        unique_hall = []
        for genome in self.hall_of_fame:
            hash_val = genome.to_hash()
            if hash_val not in seen:
                seen.add(hash_val)
                unique_hall.append(genome)

        # Sort and keep best
        unique_hall.sort(key=lambda g: g.calculate_fitness(), reverse=True)
        self.hall_of_fame = unique_hall[: self.hall_of_fame_size]
