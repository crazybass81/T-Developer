"""
Fitness Function Definition and Tracking Model
Day 6: Agent Registry Data Model
Generated: 2024-11-18

Calculate and track fitness scores for agent evolution
"""

from typing import Dict, List


class FitnessCalculator:
    """Calculate fitness scores for agents"""

    def __init__(self):
        self.weights = {"performance": 0.4, "reliability": 0.3, "efficiency": 0.3}

    def calculate(self, metrics: Dict) -> float:
        """Calculate overall fitness score"""
        # Performance score (speed and size)
        performance_score = self._calculate_performance(metrics)

        # Reliability score (error rate, success rate)
        reliability_score = self._calculate_reliability(metrics)

        # Efficiency score (cost, resource usage)
        efficiency_score = self._calculate_efficiency(metrics)

        # Weighted average
        fitness = (
            performance_score * self.weights["performance"]
            + reliability_score * self.weights["reliability"]
            + efficiency_score * self.weights["efficiency"]
        )

        return max(0.0, min(1.0, fitness))

    def _calculate_performance(self, metrics: Dict) -> float:
        """Calculate performance score"""
        speed_us = metrics.get("speed_us", 3.0)
        size_kb = metrics.get("size_kb", 6.5)

        # Speed score (lower is better)
        speed_score = max(0, 1 - (speed_us / 3.0))  # 3μs max

        # Size score (lower is better)
        size_score = max(0, 1 - (size_kb / 6.5))  # 6.5KB max

        return (speed_score + size_score) / 2

    def _calculate_reliability(self, metrics: Dict) -> float:
        """Calculate reliability score"""
        error_rate = metrics.get("error_rate", 0.0)
        success_rate = metrics.get("success_rate", 1.0)

        # Error rate score (lower is better)
        error_score = max(0, 1 - (error_rate * 10))  # 10% error = 0 score

        # Success rate score (higher is better)
        success_score = success_rate

        return (error_score + success_score) / 2

    def _calculate_efficiency(self, metrics: Dict) -> float:
        """Calculate efficiency score"""
        cost_per_call = metrics.get("cost_per_call", 0.001)

        # Cost score (lower is better)
        # Assume $0.01 per call is the baseline
        cost_score = max(0, 1 - (cost_per_call / 0.01))

        return cost_score


class WeightedFitness:
    """Fitness calculator with custom weights"""

    def __init__(self, weights: Dict):
        self.weights = weights
        # Normalize weights to sum to 1
        total = sum(weights.values())
        self.weights = {k: v / total for k, v in weights.items()}

    def calculate(self, scores: Dict) -> float:
        """Calculate weighted fitness score"""
        total = 0.0
        for component, score in scores.items():
            weight = self.weights.get(component, 0.0)
            total += score * weight

        return max(0.0, min(1.0, total))


class FitnessTracker:
    """Track fitness over generations"""

    def __init__(self):
        self.records: List[Dict] = []

    def record(self, generation: int, agent_id: str, fitness: float):
        """Record fitness for an agent in a generation"""
        self.records.append({"generation": generation, "agent_id": agent_id, "fitness": fitness})

        # Sort by generation
        self.records.sort(key=lambda x: x["generation"])

    def get_best_fitness(self) -> float:
        """Get the best fitness score recorded"""
        if not self.records:
            return 0.0

        return max(r["fitness"] for r in self.records)

    def get_average_fitness(self, generation: int = None) -> float:
        """Get average fitness for a generation or overall"""
        if generation is not None:
            gen_records = [r for r in self.records if r["generation"] == generation]
        else:
            gen_records = self.records

        if not gen_records:
            return 0.0

        return sum(r["fitness"] for r in gen_records) / len(gen_records)

    def get_improvement_rate(self) -> float:
        """Calculate improvement rate over generations"""
        if len(self.records) < 2:
            return 0.0

        # Group by generation
        generations = {}
        for record in self.records:
            gen = record["generation"]
            if gen not in generations:
                generations[gen] = []
            generations[gen].append(record["fitness"])

        # Calculate average for each generation
        gen_averages = []
        for gen in sorted(generations.keys()):
            avg = sum(generations[gen]) / len(generations[gen])
            gen_averages.append(avg)

        if len(gen_averages) < 2:
            return 0.0

        # Linear regression slope
        n = len(gen_averages)
        x_sum = sum(range(n))
        y_sum = sum(gen_averages)
        xy_sum = sum(i * y for i, y in enumerate(gen_averages))
        x2_sum = sum(i * i for i in range(n))

        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope

    def is_converging(self, window_size: int = 5) -> bool:
        """Check if fitness is converging (plateauing)"""
        if len(self.records) < window_size:
            return False

        # Get recent fitness values
        recent = self.records[-window_size:]
        fitness_values = [r["fitness"] for r in recent]

        # Calculate variance
        mean = sum(fitness_values) / len(fitness_values)
        variance = sum((f - mean) ** 2 for f in fitness_values) / len(fitness_values)

        # Low variance indicates convergence
        return variance < 0.01  # Threshold for convergence

    def get_fitness_history(self) -> List[float]:
        """Get fitness history over time"""
        return [r["fitness"] for r in self.records]
