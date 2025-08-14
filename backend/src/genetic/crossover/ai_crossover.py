"""
AI-Guided Crossover System

Intelligent crossover using AI analysis to identify gene synergies,
predict offspring performance, and select optimal crossover strategies.
"""

import asyncio
import logging
import statistics
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class CrossoverStrategy(Enum):
    """AI-guided crossover strategies"""

    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    EXPLORATORY = "exploratory"
    SYNERGISTIC = "synergistic"


@dataclass
class SynergyAnalysis:
    """Results of gene synergy analysis"""

    synergy_score: float
    gene_interactions: Dict[str, Dict[str, float]]
    complementary_genes: List[str]
    conflicting_genes: List[str]
    confidence: float


class AICrossover:
    """
    AI-guided crossover system

    Features:
    - Gene synergy detection
    - Performance prediction
    - Strategic crossover selection
    - Learning from outcomes
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize AI crossover system"""
        self.config = config or {
            "memory_limit_kb": 6.5,
            "speed_limit_us": 3.0,
            "confidence_threshold": 0.7,
            "synergy_threshold": 0.6,
            "learning_rate": 0.1,
        }

        self.analysis_strategies = ["fitness_analysis", "compatibility_check", "synergy_detection"]
        self.crossover_patterns = {}
        self.performance_history = []
        self.strategy_effectiveness = {strategy.value: 0.5 for strategy in CrossoverStrategy}

        logger.info("AI Crossover initialized")

    async def intelligent_crossover(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Perform AI-guided intelligent crossover

        Returns:
            Tuple of optimized offspring
        """
        try:
            # Analyze parents for optimal crossover strategy
            analysis = await self._analyze_parents(parent1, parent2)

            # Select crossover strategy
            strategy = self.select_crossover_strategy(parent1, parent2)

            # Apply strategic crossover
            if strategy == CrossoverStrategy.SYNERGISTIC:
                offspring = await self._synergistic_crossover(parent1, parent2, analysis)
            elif strategy == CrossoverStrategy.CONSERVATIVE:
                offspring = await self._conservative_crossover(parent1, parent2)
            elif strategy == CrossoverStrategy.AGGRESSIVE:
                offspring = await self._aggressive_crossover(parent1, parent2)
            else:  # BALANCED or default
                offspring = await self._balanced_crossover(parent1, parent2, analysis)

            # Validate and optimize offspring
            offspring1, offspring2 = await self._optimize_offspring(offspring[0], offspring[1])

            return offspring1, offspring2

        except Exception as e:
            logger.error(f"AI crossover failed: {e}")
            return await self._fallback_crossover(parent1, parent2)

    async def detect_synergies(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> SynergyAnalysis:
        """
        Detect gene synergies between parents

        Returns:
            Synergy analysis results
        """
        genes1 = parent1.get("genes", {})
        genes2 = parent2.get("genes", {})

        gene_interactions = {}
        complementary_genes = []
        conflicting_genes = []
        synergy_scores = []

        for gene1_name, gene1_val in genes1.items():
            gene_interactions[gene1_name] = {}

            for gene2_name, gene2_val in genes2.items():
                if gene1_name == gene2_name:
                    continue

                # Calculate interaction score
                interaction_score = self._calculate_interaction_score(
                    gene1_name, gene1_val, gene2_name, gene2_val
                )

                gene_interactions[gene1_name][gene2_name] = interaction_score
                synergy_scores.append(interaction_score)

                # Identify complementary/conflicting pairs
                if interaction_score > 0.7:
                    complementary_genes.append(f"{gene1_name}-{gene2_name}")
                elif interaction_score < 0.3:
                    conflicting_genes.append(f"{gene1_name}-{gene2_name}")

        # Overall synergy score
        synergy_score = statistics.mean(synergy_scores) if synergy_scores else 0.5
        confidence = min(0.9, len(synergy_scores) * 0.1)

        return SynergyAnalysis(
            synergy_score=synergy_score,
            gene_interactions=gene_interactions,
            complementary_genes=complementary_genes,
            conflicting_genes=conflicting_genes,
            confidence=confidence,
        )

    async def predict_offspring_performance(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict offspring performance using AI analysis

        Returns:
            Performance prediction with confidence
        """
        fitness1 = parent1.get("fitness", 0.0)
        fitness2 = parent2.get("fitness", 0.0)

        # Base prediction from parent fitness
        base_fitness = (fitness1 + fitness2) / 2

        # Analyze compatibility
        compatibility = await self._analyze_compatibility(parent1, parent2)

        # Predict based on historical patterns
        historical_prediction = self._predict_from_history(parent1, parent2)

        # Combine predictions
        predicted_fitness = (
            base_fitness * 0.4 + compatibility * base_fitness * 0.3 + historical_prediction * 0.3
        )

        # Calculate confidence
        confidence = min(0.95, compatibility * 0.5 + len(self.performance_history) * 0.01)

        # Identify risk factors
        risk_factors = []
        if compatibility < 0.3:
            risk_factors.append("low_compatibility")

        metrics1 = parent1.get("metrics", {})
        metrics2 = parent2.get("metrics", {})

        if (metrics1.get("memory_kb", 0) + metrics2.get("memory_kb", 0)) > self.config[
            "memory_limit_kb"
        ]:
            risk_factors.append("memory_risk")

        return {
            "expected_fitness": predicted_fitness,
            "confidence": confidence,
            "risk_factors": risk_factors,
            "base_fitness": base_fitness,
            "compatibility_bonus": compatibility * base_fitness * 0.3,
        }

    def select_crossover_strategy(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> CrossoverStrategy:
        """
        Select optimal crossover strategy using AI analysis

        Returns:
            Selected crossover strategy
        """
        fitness1 = parent1.get("fitness", 0.0)
        fitness2 = parent2.get("fitness", 0.0)
        avg_fitness = (fitness1 + fitness2) / 2

        # Strategy selection based on AI analysis
        if avg_fitness > 0.8:
            # High fitness parents - be conservative
            strategy = CrossoverStrategy.CONSERVATIVE
        elif avg_fitness < 0.3:
            # Low fitness parents - be aggressive for improvement
            strategy = CrossoverStrategy.AGGRESSIVE
        elif abs(fitness1 - fitness2) > 0.3:
            # Very different fitness - explore synergies
            strategy = CrossoverStrategy.SYNERGISTIC
        else:
            # Moderate fitness - balanced approach
            strategy = CrossoverStrategy.BALANCED

        # Adjust based on strategy effectiveness history
        best_strategy = max(self.strategy_effectiveness.items(), key=lambda x: x[1])
        if best_strategy[1] > 0.8 and len(self.performance_history) > 20:
            # Use most effective strategy if we have confidence
            strategy = CrossoverStrategy(best_strategy[0])

        logger.debug(f"Selected strategy: {strategy.value} for fitness {avg_fitness:.3f}")
        return strategy

    def learn_from_history(self, crossover_history: List[Dict]) -> None:
        """
        Learn from historical crossover outcomes

        Args:
            crossover_history: List of crossover result data
        """
        for result in crossover_history:
            try:
                strategy_used = result.get("strategy_used", "balanced")
                offspring_fitness = result.get("offspring_fitness", [])
                parent_fitness = result.get("parent_fitness", [])

                if offspring_fitness and parent_fitness:
                    # Calculate improvement
                    avg_offspring_fitness = statistics.mean(offspring_fitness)
                    avg_parent_fitness = statistics.mean(parent_fitness)
                    improvement = avg_offspring_fitness - avg_parent_fitness

                    # Update strategy effectiveness
                    if strategy_used in self.strategy_effectiveness:
                        current_eff = self.strategy_effectiveness[strategy_used]
                        learning_rate = self.config["learning_rate"]

                        # Positive improvement increases effectiveness
                        if improvement > 0:
                            new_eff = current_eff + learning_rate * improvement
                        else:
                            new_eff = current_eff - learning_rate * abs(improvement) * 0.5

                        self.strategy_effectiveness[strategy_used] = max(0.1, min(1.0, new_eff))

                self.performance_history.append(result)

            except Exception as e:
                logger.error(f"Failed to learn from crossover history: {e}")

        # Keep history manageable
        if len(self.performance_history) > 200:
            self.performance_history = self.performance_history[-100:]

        logger.info(f"Learned from {len(crossover_history)} crossover outcomes")

    # Private implementation methods

    async def _analyze_parents(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Comprehensive parent analysis"""
        return {
            "complementary_genes": await self._find_complementary_genes(parent1, parent2),
            "synergy_potential": (await self.detect_synergies(parent1, parent2)).synergy_score,
            "recommended_strategy": "best_of_both"
            if abs(parent1.get("fitness", 0) - parent2.get("fitness", 0)) < 0.1
            else "selective",
        }

    async def _find_complementary_genes(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> List[str]:
        """Find complementary genes between parents"""
        complementary = []
        genes1 = parent1.get("genes", {})
        genes2 = parent2.get("genes", {})

        # Simple complementarity detection
        if genes1.get("learning_rate", 0) != genes2.get("learning_rate", 0):
            complementary.append("learning_rate")

        if genes1.get("layer_sizes", []) != genes2.get("layer_sizes", []):
            complementary.append("layer_sizes")

        return complementary

    def _calculate_interaction_score(
        self, gene1_name: str, gene1_val: Any, gene2_name: str, gene2_val: Any
    ) -> float:
        """Calculate interaction score between genes"""
        # Simplified interaction scoring
        if gene1_name == "learning_rate" and gene2_name == "layer_sizes":
            # Higher learning rates work better with smaller networks
            if isinstance(gene2_val, list):
                network_size = sum(gene2_val) if gene2_val else 48
                optimal_lr_range = 0.01 if network_size > 100 else 0.05

                lr_value = gene1_val if isinstance(gene1_val, (int, float)) else 0.01
                score = 1.0 - abs(lr_value - optimal_lr_range) / optimal_lr_range
                return max(0.0, min(1.0, score))

        return 0.5  # Default neutral interaction

    async def _analyze_compatibility(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> float:
        """Analyze parent compatibility"""
        genes1 = parent1.get("genes", {})
        genes2 = parent2.get("genes", {})

        if not genes1 or not genes2:
            return 0.0

        compatibility_scores = []

        # Check layer size compatibility
        layers1 = genes1.get("layer_sizes", [])
        layers2 = genes2.get("layer_sizes", [])

        if layers1 and layers2:
            # Similar complexity is more compatible
            size_diff = abs(sum(layers1) - sum(layers2)) / max(sum(layers1), sum(layers2), 1)
            layer_compatibility = 1.0 - min(1.0, size_diff)
            compatibility_scores.append(layer_compatibility)

        # Check parameter value compatibility
        for param in ["learning_rate", "dropout_rate"]:
            if param in genes1 and param in genes2:
                val1, val2 = genes1[param], genes2[param]
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    param_diff = abs(val1 - val2) / max(abs(val1), abs(val2), 0.001)
                    param_compatibility = 1.0 - min(1.0, param_diff)
                    compatibility_scores.append(param_compatibility)

        return statistics.mean(compatibility_scores) if compatibility_scores else 0.5

    def _predict_from_history(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> float:
        """Predict performance based on historical data"""
        if not self.performance_history:
            return (parent1.get("fitness", 0) + parent2.get("fitness", 0)) / 2

        # Simple pattern matching
        similar_cases = []
        target_avg_fitness = (parent1.get("fitness", 0) + parent2.get("fitness", 0)) / 2

        for case in self.performance_history[-50:]:  # Use recent history
            case_parents = case.get("parents", [])
            if len(case_parents) >= 2:
                case_avg_fitness = statistics.mean([p.get("fitness", 0) for p in case_parents])
                if abs(case_avg_fitness - target_avg_fitness) < 0.2:
                    offspring_fitness = case.get("offspring_fitness", [])
                    if offspring_fitness:
                        similar_cases.append(statistics.mean(offspring_fitness))

        if similar_cases:
            return statistics.mean(similar_cases)
        else:
            return target_avg_fitness * 1.05  # Slight optimism

    # Strategy implementations (simplified for 6.5KB limit)

    async def _synergistic_crossover(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any], analysis: Dict
    ) -> Tuple[Dict, Dict]:
        """Crossover focused on gene synergies"""
        return await self._balanced_crossover(parent1, parent2, analysis)

    async def _conservative_crossover(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> Tuple[Dict, Dict]:
        """Conservative crossover preserving best genes"""
        fitness1, fitness2 = parent1.get("fitness", 0), parent2.get("fitness", 0)

        if fitness1 > fitness2:
            primary, secondary = parent1, parent2
        else:
            primary, secondary = parent2, parent1

        offspring1 = self._copy_genome(primary)
        offspring2 = self._copy_genome(secondary)

        # Minor gene exchange
        genes1, genes2 = offspring1["genes"], offspring2["genes"]
        if "learning_rate" in genes1 and "learning_rate" in genes2:
            genes2["learning_rate"] = (genes1["learning_rate"] + genes2["learning_rate"]) / 2

        return offspring1, offspring2

    async def _aggressive_crossover(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> Tuple[Dict, Dict]:
        """Aggressive crossover for exploration"""
        offspring1 = self._copy_genome(parent1)
        offspring2 = self._copy_genome(parent2)

        # Extensive gene mixing
        genes1, genes2 = offspring1["genes"], offspring2["genes"]

        # Swap major components
        if "layer_sizes" in genes1 and "layer_sizes" in genes2:
            genes1["layer_sizes"], genes2["layer_sizes"] = (
                genes2["layer_sizes"],
                genes1["layer_sizes"],
            )

        return offspring1, offspring2

    async def _balanced_crossover(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any], analysis: Dict
    ) -> Tuple[Dict, Dict]:
        """Balanced crossover strategy"""
        offspring1 = self._copy_genome(parent1)
        offspring2 = self._copy_genome(parent2)

        # Strategic gene mixing based on analysis
        complementary = analysis.get("complementary_genes", [])

        for gene in complementary:
            if gene in offspring1["genes"] and gene in offspring2["genes"]:
                # Mix complementary genes
                offspring1["genes"][gene], offspring2["genes"][gene] = (
                    offspring2["genes"][gene],
                    offspring1["genes"][gene],
                )

        return offspring1, offspring2

    async def _optimize_offspring(self, offspring1: Dict, offspring2: Dict) -> Tuple[Dict, Dict]:
        """Optimize offspring after crossover"""
        # Generate new IDs and reset fitness
        offspring1["id"] = f"ai_cross_{int(time.time() * 1000000) % 1000000:06d}_1"
        offspring2["id"] = f"ai_cross_{int(time.time() * 1000000) % 1000000:06d}_2"
        offspring1["fitness"] = 0.0
        offspring2["fitness"] = 0.0

        return offspring1, offspring2

    async def _fallback_crossover(
        self, parent1: Dict[str, Any], parent2: Dict[str, Any]
    ) -> Tuple[Dict, Dict]:
        """Simple fallback crossover"""
        return self._copy_genome(parent1), self._copy_genome(parent2)

    def _copy_genome(self, genome: Dict[str, Any]) -> Dict[str, Any]:
        """Deep copy genome"""
        import json

        return json.loads(json.dumps(genome))
