"""EvolutionScorer - Day 43
Evolution-specific fitness scoring - Size: ~6.5KB"""
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class EvolutionScorer:
    """Score agents for evolution fitness - Size optimized to 6.5KB"""

    def __init__(self):
        self.fitness_components = self._initialize_components()
        self.weights = self._initialize_weights()
        self.thresholds = self._initialize_thresholds()
        self.generation_history = {}
        self.population_stats = {}

    def _initialize_components(self) -> Dict[str, Dict[str, Any]]:
        """Initialize fitness components"""
        return {
            "survival": {
                "metrics": ["error_resilience", "resource_efficiency", "adaptation_speed"],
                "weight": 0.25,
                "mutation_factor": 1.2,
            },
            "reproduction": {
                "metrics": ["code_quality", "modularity", "interface_compatibility"],
                "weight": 0.2,
                "mutation_factor": 1.0,
            },
            "innovation": {
                "metrics": ["novelty_score", "feature_diversity", "solution_creativity"],
                "weight": 0.2,
                "mutation_factor": 1.5,
            },
            "performance": {
                "metrics": ["speed_score", "memory_score", "scalability_score"],
                "weight": 0.2,
                "mutation_factor": 1.1,
            },
            "cooperation": {
                "metrics": ["interoperability", "api_stability", "documentation_quality"],
                "weight": 0.15,
                "mutation_factor": 0.9,
            },
        }

    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize metric weights for evolution"""
        return {
            # Survival metrics
            "error_resilience": 0.4,
            "resource_efficiency": 0.35,
            "adaptation_speed": 0.25,
            # Reproduction metrics
            "code_quality": 0.4,
            "modularity": 0.35,
            "interface_compatibility": 0.25,
            # Innovation metrics
            "novelty_score": 0.4,
            "feature_diversity": 0.35,
            "solution_creativity": 0.25,
            # Performance metrics
            "speed_score": 0.35,
            "memory_score": 0.35,
            "scalability_score": 0.3,
            # Cooperation metrics
            "interoperability": 0.4,
            "api_stability": 0.35,
            "documentation_quality": 0.25,
        }

    def _initialize_thresholds(self) -> Dict[str, float]:
        """Initialize evolution thresholds"""
        return {
            "elite": 90,  # Top performers, preserved
            "breeding": 70,  # Can reproduce
            "mutation": 50,  # Subject to mutation
            "elimination": 30,  # Removed from population
        }

    def calculate_fitness(
        self, agent_id: str, metrics: Dict[str, float], generation: int = 0
    ) -> Dict[str, Any]:
        """Calculate evolution fitness score"""
        fitness_result = {
            "agent_id": agent_id,
            "generation": generation,
            "timestamp": datetime.now().isoformat(),
            "component_scores": {},
            "total_fitness": 0,
            "evolution_class": "",
            "mutation_probability": 0,
            "crossover_priority": 0,
        }

        # Calculate component scores
        for comp_name, comp_config in self.fitness_components.items():
            comp_score = self._calculate_component_score(comp_name, comp_config, metrics)
            fitness_result["component_scores"][comp_name] = comp_score

        # Calculate total fitness
        fitness_result["total_fitness"] = self._calculate_total_fitness(
            fitness_result["component_scores"]
        )

        # Determine evolution class
        fitness_result["evolution_class"] = self._determine_evolution_class(
            fitness_result["total_fitness"]
        )

        # Calculate mutation probability
        fitness_result["mutation_probability"] = self._calculate_mutation_probability(
            fitness_result["total_fitness"], generation
        )

        # Calculate crossover priority
        fitness_result["crossover_priority"] = self._calculate_crossover_priority(
            fitness_result["component_scores"]
        )

        # Store in generation history
        if generation not in self.generation_history:
            self.generation_history[generation] = []
        self.generation_history[generation].append(fitness_result)

        # Update population stats
        self._update_population_stats(generation, fitness_result)

        return fitness_result

    def _calculate_component_score(
        self, comp_name: str, comp_config: Dict[str, Any], metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate score for a fitness component"""
        scores = []
        weights_sum = 0
        details = {}

        for metric_name in comp_config["metrics"]:
            if metric_name in metrics:
                metric_value = metrics[metric_name]
                weight = self.weights.get(metric_name, 1.0)

                # Normalize to 0-100 scale
                normalized = min(100, max(0, metric_value))
                weighted_score = normalized * weight

                scores.append(weighted_score)
                weights_sum += weight
                details[metric_name] = {
                    "value": metric_value,
                    "normalized": normalized,
                    "weighted": weighted_score,
                }

        component_score = (sum(scores) / weights_sum) if weights_sum > 0 else 50

        return {
            "score": component_score,
            "normalized": component_score / 100,
            "details": details,
            "mutation_factor": comp_config["mutation_factor"],
        }

    def _calculate_total_fitness(self, component_scores: Dict[str, Dict]) -> float:
        """Calculate total fitness score"""
        total = 0
        total_weight = 0

        for comp_name, comp_score in component_scores.items():
            if comp_name in self.fitness_components:
                weight = self.fitness_components[comp_name]["weight"]
                total += comp_score["score"] * weight
                total_weight += weight

        return total / total_weight if total_weight > 0 else 50

    def _determine_evolution_class(self, fitness: float) -> str:
        """Determine evolution class based on fitness"""
        if fitness >= self.thresholds["elite"]:
            return "elite"
        elif fitness >= self.thresholds["breeding"]:
            return "breeder"
        elif fitness >= self.thresholds["mutation"]:
            return "mutable"
        else:
            return "eliminate"

    def _calculate_mutation_probability(self, fitness: float, generation: int) -> float:
        """Calculate mutation probability"""
        # Base mutation rate
        base_rate = 0.1

        # Adjust based on fitness (lower fitness = higher mutation)
        fitness_factor = (100 - fitness) / 100

        # Adjust based on generation (stabilize over time)
        generation_factor = math.exp(-generation / 50)

        # Calculate final probability
        mutation_prob = base_rate + (fitness_factor * 0.3) + (generation_factor * 0.1)

        return min(0.5, max(0.01, mutation_prob))

    def _calculate_crossover_priority(self, component_scores: Dict[str, Dict]) -> float:
        """Calculate crossover priority for breeding"""
        # Prioritize agents with balanced high scores
        scores = [cs["score"] for cs in component_scores.values()]

        if not scores:
            return 0

        # Calculate mean and variance
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)

        # High mean with low variance is ideal
        priority = mean * (1 - variance / 1000)

        return min(100, max(0, priority))

    def _update_population_stats(self, generation: int, fitness_result: Dict[str, Any]):
        """Update population statistics"""
        if generation not in self.population_stats:
            self.population_stats[generation] = {
                "count": 0,
                "total_fitness": 0,
                "elite_count": 0,
                "breeder_count": 0,
                "mutable_count": 0,
                "eliminate_count": 0,
            }

        stats = self.population_stats[generation]
        stats["count"] += 1
        stats["total_fitness"] += fitness_result["total_fitness"]
        stats[f"{fitness_result['evolution_class']}_count"] += 1

    def select_parents(self, generation: int, count: int = 2) -> List[Dict[str, Any]]:
        """Select parents for reproduction using tournament selection"""
        if generation not in self.generation_history:
            return []

        population = self.generation_history[generation]
        eligible = [
            agent for agent in population if agent["evolution_class"] in ["elite", "breeder"]
        ]

        if len(eligible) < count:
            return eligible

        # Tournament selection
        selected = []
        tournament_size = min(5, len(eligible))

        for _ in range(count):
            tournament = []
            for _ in range(tournament_size):
                idx = hash(datetime.now()) % len(eligible)
                tournament.append(eligible[idx])

            # Select best from tournament
            winner = max(tournament, key=lambda x: x["total_fitness"])
            selected.append(winner)

        return selected

    def calculate_offspring_potential(self, parent1: Dict, parent2: Dict) -> float:
        """Calculate potential fitness of offspring"""
        # Average parent fitness
        avg_fitness = (parent1["total_fitness"] + parent2["total_fitness"]) / 2

        # Bonus for complementary strengths
        complement_bonus = 0
        for component in self.fitness_components:
            if (
                component in parent1["component_scores"]
                and component in parent2["component_scores"]
            ):
                score1 = parent1["component_scores"][component]["score"]
                score2 = parent2["component_scores"][component]["score"]

                # Bonus if parents have different strengths
                if abs(score1 - score2) > 20:
                    complement_bonus += 5

        # Add genetic diversity bonus
        diversity_bonus = 10 if parent1["agent_id"] != parent2["agent_id"] else 0

        return min(100, avg_fitness + complement_bonus + diversity_bonus)

    def get_generation_summary(self, generation: int) -> Dict[str, Any]:
        """Get summary statistics for a generation"""
        if generation not in self.population_stats:
            return {"error": "Generation not found"}

        stats = self.population_stats[generation]
        population = self.generation_history.get(generation, [])

        summary = {
            "generation": generation,
            "population_size": stats["count"],
            "average_fitness": stats["total_fitness"] / stats["count"] if stats["count"] > 0 else 0,
            "class_distribution": {
                "elite": stats["elite_count"],
                "breeder": stats["breeder_count"],
                "mutable": stats["mutable_count"],
                "eliminate": stats["eliminate_count"],
            },
        }

        if population:
            fitness_scores = [agent["total_fitness"] for agent in population]
            summary["best_fitness"] = max(fitness_scores)
            summary["worst_fitness"] = min(fitness_scores)
            summary["fitness_variance"] = self._calculate_variance(fitness_scores)

        return summary

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if not values:
            return 0

        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)

    def get_evolution_trajectory(self, start_gen: int = 0, end_gen: int = None) -> Dict[str, Any]:
        """Get evolution trajectory across generations"""
        if end_gen is None:
            end_gen = max(self.generation_history.keys()) if self.generation_history else 0

        trajectory = {
            "start_generation": start_gen,
            "end_generation": end_gen,
            "fitness_progression": [],
            "population_changes": [],
            "evolution_rate": 0,
        }

        for gen in range(start_gen, end_gen + 1):
            if gen in self.population_stats:
                stats = self.population_stats[gen]
                avg_fitness = stats["total_fitness"] / stats["count"] if stats["count"] > 0 else 0
                trajectory["fitness_progression"].append(
                    {
                        "generation": gen,
                        "average_fitness": avg_fitness,
                        "population_size": stats["count"],
                    }
                )

        # Calculate evolution rate
        if len(trajectory["fitness_progression"]) >= 2:
            start_fitness = trajectory["fitness_progression"][0]["average_fitness"]
            end_fitness = trajectory["fitness_progression"][-1]["average_fitness"]
            generations = end_gen - start_gen

            if generations > 0:
                trajectory["evolution_rate"] = (end_fitness - start_fitness) / generations

        return trajectory
