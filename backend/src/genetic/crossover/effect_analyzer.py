"""
Crossover Effect Analyzer

Analyzes the effects of crossover operations on fitness, diversity,
and population evolution to optimize future crossover decisions.
"""

import logging
import statistics
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AnalysisMethod(Enum):
    """Available analysis methods"""

    FITNESS_IMPACT = "fitness_impact"
    DIVERSITY_IMPACT = "diversity_impact"
    GENE_CONTRIBUTION = "gene_contribution"
    POPULATION_TRENDS = "population_trends"


@dataclass
class CrossoverAnalysis:
    """Results of crossover analysis"""

    fitness_improvement: float
    inheritance_patterns: Dict[str, float]
    success_factors: List[str]
    diversity_change: float
    recommendation: str


class CrossoverEffectAnalyzer:
    """
    Analyzes crossover effects for optimization

    Tracks and analyzes:
    - Fitness impact of crossovers
    - Gene inheritance patterns
    - Diversity effects
    - Population-level trends
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize crossover effect analyzer"""
        self.config = config or {
            "analysis_window": 50,
            "success_threshold": 0.05,
            "diversity_weight": 0.3,
            "fitness_weight": 0.7,
        }

        self.analysis_methods = {
            AnalysisMethod.FITNESS_IMPACT: self._analyze_fitness_impact_detailed,
            AnalysisMethod.DIVERSITY_IMPACT: self._analyze_diversity_impact_detailed,
            AnalysisMethod.GENE_CONTRIBUTION: self._analyze_gene_contribution_detailed,
            AnalysisMethod.POPULATION_TRENDS: self._analyze_population_trends_detailed,
        }

        self.historical_crossovers: List[Dict] = []
        self.gene_success_rates: Dict[str, List[float]] = {}
        self.strategy_performance: Dict[str, List[float]] = {}

        logger.info("Crossover Effect Analyzer initialized")

    async def analyze_fitness_impact(self, crossover_example: Dict[str, Any]) -> CrossoverAnalysis:
        """
        Analyze fitness impact of crossover operation

        Args:
            crossover_example: Crossover operation data

        Returns:
            Analysis results
        """
        try:
            parent1 = crossover_example["parent1"]
            parent2 = crossover_example["parent2"]
            offspring = crossover_example["offspring"]

            # Calculate fitness improvements
            parent_fitness = [parent1.get("fitness", 0), parent2.get("fitness", 0)]
            offspring_fitness = [child.get("fitness", 0) for child in offspring]

            avg_parent_fitness = statistics.mean(parent_fitness)
            avg_offspring_fitness = statistics.mean(offspring_fitness)

            fitness_improvement = avg_offspring_fitness - avg_parent_fitness

            # Analyze inheritance patterns
            inheritance_patterns = self._analyze_inheritance_patterns(parent1, parent2, offspring)

            # Identify success factors
            success_factors = self._identify_success_factors(crossover_example, fitness_improvement)

            # Calculate diversity change
            diversity_change = self._calculate_diversity_change(parent1, parent2, offspring)

            # Generate recommendation
            recommendation = self._generate_recommendation(
                fitness_improvement, diversity_change, inheritance_patterns
            )

            return CrossoverAnalysis(
                fitness_improvement=fitness_improvement,
                inheritance_patterns=inheritance_patterns,
                success_factors=success_factors,
                diversity_change=diversity_change,
                recommendation=recommendation,
            )

        except Exception as e:
            logger.error(f"Fitness impact analysis failed: {e}")
            return CrossoverAnalysis(0.0, {}, [], 0.0, "analysis_failed")

    async def analyze_gene_contributions(
        self, crossover_example: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze individual gene contributions to crossover success

        Returns:
            Gene contribution analysis
        """
        contributions = {}

        try:
            parent1 = crossover_example["parent1"]
            parent2 = crossover_example["parent2"]
            offspring = crossover_example["offspring"]

            genes1 = parent1.get("genes", {})
            genes2 = parent2.get("genes", {})

            for gene_name in genes1.keys():
                if gene_name in genes2:
                    contribution = self._calculate_gene_contribution(
                        gene_name, genes1[gene_name], genes2[gene_name], offspring
                    )

                    contributions[gene_name] = {
                        "impact_score": contribution["impact"],
                        "inheritance_success": contribution["inheritance_success"],
                        "diversity_contribution": contribution["diversity"],
                        "constraint_compliance": contribution["compliance"],
                    }

            return contributions

        except Exception as e:
            logger.error(f"Gene contribution analysis failed: {e}")
            return {}

    async def analyze_diversity_impact(self, crossover_example: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze diversity impact of crossover

        Returns:
            Diversity impact analysis
        """
        try:
            parent1 = crossover_example["parent1"]
            parent2 = crossover_example["parent2"]
            offspring = crossover_example["offspring"]

            # Calculate initial diversity
            initial_diversity = self._calculate_genome_diversity([parent1, parent2])

            # Calculate post-crossover diversity
            all_genomes = [parent1, parent2] + offspring
            final_diversity = self._calculate_genome_diversity(all_genomes)

            diversity_change = final_diversity - initial_diversity

            # Analyze exploration vs exploitation
            exploration_benefit = self._calculate_exploration_benefit(offspring, [parent1, parent2])

            return {
                "diversity_change": diversity_change,
                "exploration_benefit": exploration_benefit,
                "novelty_score": self._calculate_novelty_score(offspring),
                "preservation_score": self._calculate_preservation_score(
                    parent1, parent2, offspring
                ),
            }

        except Exception as e:
            logger.error(f"Diversity impact analysis failed: {e}")
            return {"diversity_change": 0.0, "exploration_benefit": 0.0}

    def calculate_success_metrics(self, crossover_example: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate comprehensive crossover success metrics

        Returns:
            Success metrics dictionary
        """
        try:
            parent1 = crossover_example["parent1"]
            parent2 = crossover_example["parent2"]
            offspring = crossover_example["offspring"]

            # Improvement rate
            parent_fitness = [parent1.get("fitness", 0), parent2.get("fitness", 0)]
            offspring_fitness = [child.get("fitness", 0) for child in offspring]

            improvement_rate = (
                statistics.mean(offspring_fitness) - statistics.mean(parent_fitness)
            ) / max(statistics.mean(parent_fitness), 0.001)

            # Diversity preservation
            diversity_preservation = self._calculate_diversity_preservation(
                parent1, parent2, offspring
            )

            # Constraint compliance
            constraint_compliance = self._calculate_constraint_compliance(offspring)

            # Innovation score
            innovation_score = self._calculate_innovation_score(offspring, [parent1, parent2])

            return {
                "improvement_rate": improvement_rate,
                "diversity_preservation": diversity_preservation,
                "constraint_compliance": constraint_compliance,
                "innovation_score": innovation_score,
                "overall_success": (
                    improvement_rate * 0.4
                    + diversity_preservation * 0.2
                    + constraint_compliance * 0.3
                    + innovation_score * 0.1
                ),
            }

        except Exception as e:
            logger.error(f"Success metrics calculation failed: {e}")
            return {
                "improvement_rate": 0.0,
                "diversity_preservation": 0.0,
                "constraint_compliance": 0.0,
            }

    async def analyze_population_trends(self, population_data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze population-level crossover trends

        Returns:
            Population trend analysis
        """
        if not population_data:
            return {"success_rate_trend": 0.0, "improvement_trend": 0.0}

        try:
            # Success rate trend
            success_rates = []
            improvement_values = []

            for gen_data in population_data:
                total_crossovers = gen_data.get("crossovers", 0)
                successful_crossovers = gen_data.get("successful_crossovers", 0)

                if total_crossovers > 0:
                    success_rate = successful_crossovers / total_crossovers
                    success_rates.append(success_rate)

                improvement = gen_data.get("avg_fitness_improvement", 0)
                improvement_values.append(improvement)

            # Calculate trends
            success_rate_trend = self._calculate_trend(success_rates) if success_rates else 0.0
            improvement_trend = (
                self._calculate_trend(improvement_values) if improvement_values else 0.0
            )

            # Overall population health
            population_health = {
                "success_rate_avg": statistics.mean(success_rates) if success_rates else 0.0,
                "improvement_avg": statistics.mean(improvement_values)
                if improvement_values
                else 0.0,
                "trend_strength": abs(success_rate_trend) + abs(improvement_trend),
            }

            return {
                "success_rate_trend": success_rate_trend,
                "improvement_trend": improvement_trend,
                "population_health": population_health,
                "recommendations": self._generate_population_recommendations(
                    success_rate_trend, improvement_trend
                ),
            }

        except Exception as e:
            logger.error(f"Population trend analysis failed: {e}")
            return {"success_rate_trend": 0.0, "improvement_trend": 0.0}

    def learn_from_crossover(self, crossover_example: Dict[str, Any]) -> None:
        """
        Learn from crossover outcome

        Args:
            crossover_example: Crossover operation and results
        """
        try:
            # Store historical data
            self.historical_crossovers.append(
                {"timestamp": time.time(), "example": crossover_example, "analyzed": False}
            )

            # Update gene success rates
            self._update_gene_success_rates(crossover_example)

            # Update strategy performance
            strategy = crossover_example.get("strategy", "unknown")
            if strategy in self.strategy_performance:
                fitness_improvement = self._calculate_fitness_improvement(crossover_example)
                self.strategy_performance[strategy].append(fitness_improvement)
            else:
                self.strategy_performance[strategy] = [0.0]

            # Keep history manageable
            if len(self.historical_crossovers) > self.config["analysis_window"] * 2:
                self.historical_crossovers = self.historical_crossovers[
                    -self.config["analysis_window"] :
                ]

        except Exception as e:
            logger.error(f"Learning from crossover failed: {e}")

    async def recommend_crossover_strategy(
        self, population_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recommend crossover strategy based on population state

        Returns:
            Strategy recommendations
        """
        try:
            avg_fitness = population_state.get("avg_fitness", 0.5)
            diversity_index = population_state.get("diversity_index", 0.5)
            stagnation_gens = population_state.get("stagnation_generations", 0)

            # Base recommendations
            recommendations = {
                "recommended_strategy": "balanced",
                "crossover_rate": 0.7,
                "reasoning": "default_recommendation",
            }

            # Adjust based on fitness level
            if avg_fitness < 0.3:
                recommendations["recommended_strategy"] = "aggressive"
                recommendations["crossover_rate"] = 0.8
                recommendations["reasoning"] = "low_fitness_exploration"
            elif avg_fitness > 0.8:
                recommendations["recommended_strategy"] = "conservative"
                recommendations["crossover_rate"] = 0.6
                recommendations["reasoning"] = "high_fitness_exploitation"

            # Adjust based on diversity
            if diversity_index < 0.3:
                recommendations["crossover_rate"] *= 1.2
                recommendations["reasoning"] += "_diversity_boost"
            elif diversity_index > 0.8:
                recommendations["crossover_rate"] *= 0.9
                recommendations["reasoning"] += "_diversity_control"

            # Adjust for stagnation
            if stagnation_gens > 5:
                recommendations["recommended_strategy"] = "exploratory"
                recommendations["crossover_rate"] = 0.9
                recommendations["reasoning"] = "stagnation_breaking"

            # Use historical performance data
            if self.strategy_performance:
                best_strategy = max(
                    self.strategy_performance.items(),
                    key=lambda x: statistics.mean(x[1]) if x[1] else 0,
                )
                if statistics.mean(best_strategy[1]) > 0.1:
                    recommendations["recommended_strategy"] = best_strategy[0]
                    recommendations["reasoning"] += f"_historical_best_{best_strategy[0]}"

            return recommendations

        except Exception as e:
            logger.error(f"Strategy recommendation failed: {e}")
            return {"recommended_strategy": "balanced", "crossover_rate": 0.7}

    # Private helper methods (simplified for space)

    def _analyze_inheritance_patterns(
        self, parent1: Dict, parent2: Dict, offspring: List[Dict]
    ) -> Dict[str, float]:
        """Analyze gene inheritance patterns"""
        patterns = {}
        genes1 = parent1.get("genes", {})

        for gene_name in genes1.keys():
            inheritance_score = 0.0
            for child in offspring:
                child_genes = child.get("genes", {})
                if gene_name in child_genes:
                    if child_genes[gene_name] == genes1[gene_name]:
                        inheritance_score += 0.5
                    elif gene_name in parent2.get("genes", {}):
                        if child_genes[gene_name] == parent2["genes"][gene_name]:
                            inheritance_score += 0.5

            patterns[gene_name] = inheritance_score / max(len(offspring), 1)

        return patterns

    def _calculate_gene_contribution(
        self, gene_name: str, gene1: Any, gene2: Any, offspring: List[Dict]
    ) -> Dict[str, float]:
        """Calculate individual gene contribution"""
        return {
            "impact": 0.5,  # Simplified
            "inheritance_success": 0.7,
            "diversity": 0.6,
            "compliance": 0.9,
        }

    def _calculate_genome_diversity(self, genomes: List[Dict]) -> float:
        """Calculate diversity among genomes"""
        if len(genomes) < 2:
            return 0.0

        differences = 0
        comparisons = 0

        for i in range(len(genomes)):
            for j in range(i + 1, len(genomes)):
                genes1 = genomes[i].get("genes", {})
                genes2 = genomes[j].get("genes", {})

                for gene_name in genes1.keys():
                    if gene_name in genes2:
                        comparisons += 1
                        if genes1[gene_name] != genes2[gene_name]:
                            differences += 1

        return differences / max(comparisons, 1)

    def _identify_success_factors(self, crossover_example: Dict, improvement: float) -> List[str]:
        """Identify factors contributing to success"""
        factors = []

        if improvement > 0.1:
            factors.append("significant_improvement")

        if improvement > 0:
            factors.append("positive_outcome")

        return factors

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction and strength"""
        if len(values) < 2:
            return 0.0

        # Simple linear trend
        n = len(values)
        x_values = list(range(n))

        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        return numerator / max(denominator, 0.001)

    # Additional helper methods (simplified)

    def _calculate_fitness_improvement(self, example: Dict) -> float:
        """Calculate fitness improvement from crossover"""
        parent1 = example.get("parent1", {})
        parent2 = example.get("parent2", {})
        offspring = example.get("offspring", [])

        if not offspring:
            return 0.0

        parent_avg = (parent1.get("fitness", 0) + parent2.get("fitness", 0)) / 2
        offspring_avg = statistics.mean([child.get("fitness", 0) for child in offspring])

        return offspring_avg - parent_avg

    def _update_gene_success_rates(self, example: Dict) -> None:
        """Update gene-level success rates"""
        improvement = self._calculate_fitness_improvement(example)

        genes1 = example.get("parent1", {}).get("genes", {})
        for gene_name in genes1.keys():
            if gene_name not in self.gene_success_rates:
                self.gene_success_rates[gene_name] = []

            self.gene_success_rates[gene_name].append(improvement)

            # Keep manageable history
            if len(self.gene_success_rates[gene_name]) > 50:
                self.gene_success_rates[gene_name] = self.gene_success_rates[gene_name][-25:]

    # Placeholder methods for comprehensive analysis

    def _generate_recommendation(
        self, fitness_imp: float, diversity_change: float, patterns: Dict
    ) -> str:
        """Generate crossover recommendation"""
        if fitness_imp > 0.1:
            return "continue_current_strategy"
        elif diversity_change < -0.2:
            return "increase_exploration"
        else:
            return "balanced_approach"

    def _calculate_diversity_change(
        self, parent1: Dict, parent2: Dict, offspring: List[Dict]
    ) -> float:
        """Calculate diversity change from crossover"""
        return 0.1  # Simplified

    def _calculate_exploration_benefit(self, offspring: List[Dict], parents: List[Dict]) -> float:
        """Calculate exploration benefit"""
        return 0.15  # Simplified

    def _calculate_novelty_score(self, offspring: List[Dict]) -> float:
        """Calculate novelty score of offspring"""
        return 0.2  # Simplified

    def _calculate_preservation_score(
        self, parent1: Dict, parent2: Dict, offspring: List[Dict]
    ) -> float:
        """Calculate how well good traits are preserved"""
        return 0.8  # Simplified

    def _calculate_diversity_preservation(
        self, parent1: Dict, parent2: Dict, offspring: List[Dict]
    ) -> float:
        """Calculate diversity preservation score"""
        return 0.7  # Simplified

    def _calculate_constraint_compliance(self, offspring: List[Dict]) -> float:
        """Calculate constraint compliance score"""
        return 0.9  # Simplified

    def _calculate_innovation_score(self, offspring: List[Dict], parents: List[Dict]) -> float:
        """Calculate innovation score"""
        return 0.3  # Simplified

    def _generate_population_recommendations(
        self, success_trend: float, improvement_trend: float
    ) -> List[str]:
        """Generate population-level recommendations"""
        recommendations = []

        if success_trend < -0.1:
            recommendations.append("increase_crossover_diversity")

        if improvement_trend < -0.05:
            recommendations.append("adjust_selection_pressure")

        return recommendations

    # Detailed analysis method placeholders

    async def _analyze_fitness_impact_detailed(self, data: Dict) -> Dict:
        return await self.analyze_fitness_impact(data)

    async def _analyze_diversity_impact_detailed(self, data: Dict) -> Dict:
        return await self.analyze_diversity_impact(data)

    async def _analyze_gene_contribution_detailed(self, data: Dict) -> Dict:
        return await self.analyze_gene_contributions(data)

    async def _analyze_population_trends_detailed(self, data: List[Dict]) -> Dict:
        return await self.analyze_population_trends(data)
