"""FitnessCalculator - Day 44
Comprehensive fitness score calculation for evolution - Size: ~6.5KB"""
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class FitnessCalculator:
    """Calculate comprehensive fitness scores for evolution - Size optimized"""

    def __init__(self):
        self.components = self._initialize_components()
        self.weights = self._initialize_weights()
        self.normalization = self._initialize_normalization()
        self.history = {}

    def _initialize_components(self) -> Dict[str, float]:
        """Initialize fitness components and their weights"""
        return {
            "performance": 0.20,
            "quality": 0.20,
            "business": 0.15,
            "evolution": 0.15,
            "adaptation": 0.10,
            "innovation": 0.10,
            "reliability": 0.10,
        }

    def _initialize_weights(self) -> Dict[str, Dict[str, float]]:
        """Initialize detailed weights for sub-metrics"""
        return {
            "performance": {"speed": 0.35, "memory": 0.30, "scalability": 0.20, "efficiency": 0.15},
            "quality": {
                "code_quality": 0.30,
                "test_coverage": 0.25,
                "documentation": 0.20,
                "maintainability": 0.25,
            },
            "business": {
                "roi": 0.35,
                "user_satisfaction": 0.30,
                "cost_efficiency": 0.20,
                "time_to_market": 0.15,
            },
            "evolution": {
                "adaptability": 0.30,
                "mutation_success": 0.25,
                "crossover_compatibility": 0.25,
                "generation_improvement": 0.20,
            },
            "adaptation": {
                "environment_fit": 0.35,
                "change_resilience": 0.35,
                "learning_rate": 0.30,
            },
            "innovation": {"novelty": 0.40, "creativity": 0.35, "problem_solving": 0.25},
            "reliability": {"error_rate": 0.35, "uptime": 0.35, "recovery": 0.30},
        }

    def _initialize_normalization(self) -> Dict[str, Tuple[float, float]]:
        """Initialize normalization ranges (min, max)"""
        return {
            "speed": (0, 1000),
            "memory": (0, 100),
            "roi": (-100, 500),
            "error_rate": (0, 10),
            "novelty": (0, 100),
            "test_coverage": (0, 100),
            "uptime": (90, 100),
        }

    def calculate(self, agent_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive fitness score"""
        result = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "component_scores": {},
            "weighted_scores": {},
            "total_fitness": 0,
            "fitness_class": "",
            "percentile": 0,
            "strengths": [],
            "weaknesses": [],
        }

        # Calculate component scores
        for component, weight in self.components.items():
            score = self._calculate_component(component, metrics)
            result["component_scores"][component] = score
            result["weighted_scores"][component] = score * weight

        # Calculate total fitness
        result["total_fitness"] = sum(result["weighted_scores"].values())

        # Determine fitness class
        result["fitness_class"] = self._classify_fitness(result["total_fitness"])

        # Calculate percentile
        result["percentile"] = self._calculate_percentile(result["total_fitness"])

        # Identify strengths and weaknesses
        result["strengths"] = self._identify_strengths(result["component_scores"])
        result["weaknesses"] = self._identify_weaknesses(result["component_scores"])

        # Store in history
        if agent_id not in self.history:
            self.history[agent_id] = []
        self.history[agent_id].append(result)

        return result

    def _calculate_component(self, component: str, metrics: Dict[str, Any]) -> float:
        """Calculate score for a fitness component"""
        if component not in self.weights:
            return 50.0

        weights = self.weights[component]
        total_score = 0
        total_weight = 0

        for metric, weight in weights.items():
            if metric in metrics:
                normalized = self._normalize_metric(metric, metrics[metric])
                total_score += normalized * weight
                total_weight += weight

        return (total_score / total_weight * 100) if total_weight > 0 else 50.0

    def _normalize_metric(self, metric: str, value: float) -> float:
        """Normalize metric to 0-1 range"""
        if metric in self.normalization:
            min_val, max_val = self.normalization[metric]
            normalized = (value - min_val) / (max_val - min_val)
            return max(0, min(1, normalized))

        # Default normalization for unknown metrics
        if metric in ["error_rate", "cost", "complexity"]:
            # Lower is better
            return max(0, 1 - value / 100)
        else:
            # Higher is better
            return min(1, value / 100)

    def _classify_fitness(self, fitness: float) -> str:
        """Classify fitness level"""
        if fitness >= 85:
            return "elite"
        elif fitness >= 70:
            return "superior"
        elif fitness >= 55:
            return "average"
        elif fitness >= 40:
            return "below_average"
        else:
            return "poor"

    def _calculate_percentile(self, fitness: float) -> float:
        """Calculate percentile based on historical data"""
        all_scores = []
        for agent_history in self.history.values():
            all_scores.extend([h["total_fitness"] for h in agent_history])

        if not all_scores:
            return 50.0

        below = sum(1 for s in all_scores if s < fitness)
        return (below / len(all_scores)) * 100

    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Identify top strengths"""
        sorted_components = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [comp for comp, score in sorted_components[:3] if score >= 70]

    def _identify_weaknesses(self, scores: Dict[str, float]) -> List[str]:
        """Identify main weaknesses"""
        sorted_components = sorted(scores.items(), key=lambda x: x[1])
        return [comp for comp, score in sorted_components[:3] if score < 50]

    def calculate_evolution_potential(
        self, agent_id: str, current_fitness: float, metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate evolution potential"""
        potential = {
            "agent_id": agent_id,
            "current_fitness": current_fitness,
            "improvement_potential": 0,
            "mutation_benefit": 0,
            "crossover_benefit": 0,
            "recommended_evolution": "",
        }

        # Calculate improvement potential
        max_possible = 100
        potential["improvement_potential"] = max_possible - current_fitness

        # Estimate mutation benefit
        if current_fitness < 60:
            potential["mutation_benefit"] = 20
            potential["recommended_evolution"] = "aggressive_mutation"
        elif current_fitness < 75:
            potential["mutation_benefit"] = 10
            potential["recommended_evolution"] = "moderate_mutation"
        else:
            potential["mutation_benefit"] = 5
            potential["recommended_evolution"] = "fine_tuning"

        # Estimate crossover benefit
        diversity_score = metrics.get("diversity", 50)
        potential["crossover_benefit"] = min(15, diversity_score / 5)

        return potential

    def compare_generations(self, agent_id: str, gen1: int, gen2: int) -> Dict[str, Any]:
        """Compare fitness between generations"""
        if agent_id not in self.history:
            return {"error": "No history available"}

        history = self.history[agent_id]
        if gen1 >= len(history) or gen2 >= len(history):
            return {"error": "Invalid generation numbers"}

        fitness1 = history[gen1]["total_fitness"]
        fitness2 = history[gen2]["total_fitness"]

        comparison = {
            "agent_id": agent_id,
            "generation_1": {"gen": gen1, "fitness": fitness1},
            "generation_2": {"gen": gen2, "fitness": fitness2},
            "improvement": fitness2 - fitness1,
            "improvement_rate": ((fitness2 - fitness1) / fitness1 * 100) if fitness1 > 0 else 0,
            "component_changes": {},
        }

        # Compare components
        for component in self.components:
            score1 = history[gen1]["component_scores"].get(component, 0)
            score2 = history[gen2]["component_scores"].get(component, 0)
            comparison["component_changes"][component] = {
                "before": score1,
                "after": score2,
                "change": score2 - score1,
            }

        return comparison

    def predict_future_fitness(self, agent_id: str, generations_ahead: int = 5) -> float:
        """Predict future fitness based on trend"""
        if agent_id not in self.history or len(self.history[agent_id]) < 2:
            return 50.0

        history = self.history[agent_id]
        recent = history[-min(10, len(history)) :]

        # Calculate trend
        fitness_values = [h["total_fitness"] for h in recent]
        n = len(fitness_values)

        # Simple linear regression
        x_mean = (n - 1) / 2
        y_mean = sum(fitness_values) / n

        num = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(fitness_values))
        den = sum((i - x_mean) ** 2 for i in range(n))

        if den == 0:
            return fitness_values[-1]

        slope = num / den
        intercept = y_mean - slope * x_mean

        # Predict future
        future_fitness = intercept + slope * (n - 1 + generations_ahead)

        return max(0, min(100, future_fitness))

    def get_fitness_report(self, agent_id: str) -> Dict[str, Any]:
        """Generate comprehensive fitness report"""
        if agent_id not in self.history:
            return {"error": "No fitness data available"}

        history = self.history[agent_id]
        latest = history[-1]

        report = {
            "agent_id": agent_id,
            "current_fitness": latest["total_fitness"],
            "fitness_class": latest["fitness_class"],
            "percentile": latest["percentile"],
            "evaluations": len(history),
            "trend": self._calculate_trend(history),
            "average_fitness": sum(h["total_fitness"] for h in history) / len(history),
            "best_fitness": max(h["total_fitness"] for h in history),
            "component_analysis": latest["component_scores"],
            "strengths": latest["strengths"],
            "weaknesses": latest["weaknesses"],
            "evolution_potential": self.calculate_evolution_potential(
                agent_id, latest["total_fitness"], {}
            ),
            "predicted_fitness": self.predict_future_fitness(agent_id),
        }

        return report

    def _calculate_trend(self, history: List[Dict]) -> str:
        """Calculate fitness trend"""
        if len(history) < 2:
            return "insufficient_data"

        recent = history[-5:]
        values = [h["total_fitness"] for h in recent]

        # Check trend
        increasing = all(values[i] <= values[i + 1] for i in range(len(values) - 1))
        decreasing = all(values[i] >= values[i + 1] for i in range(len(values) - 1))

        if increasing:
            return "improving"
        elif decreasing:
            return "declining"
        else:
            return "stable"
