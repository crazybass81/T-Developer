"""
Recommendation Engine for T-Developer

This module implements an intelligent recommendation system that provides
suggestions for improvements, patterns to apply, and actions to take
based on learned knowledge and A/B testing results.

The RecommendationEngine analyzes current context against historical
patterns and performance data to suggest optimal evolution strategies.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import random
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from .knowledge_graph import KnowledgeGraph, KnowledgeNode
from .memory_curator import Memory, MemoryCurator
from .pattern_database import Pattern, PatternDatabase

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT: int = 30
MAX_RECOMMENDATIONS: int = 20
MIN_CONFIDENCE_THRESHOLD: float = 0.6
A_B_TEST_DURATION_HOURS: int = 24


class RecommendationType(Enum):
    """Types of recommendations that can be made."""

    PATTERN_APPLICATION = "pattern_application"
    FAILURE_PREVENTION = "failure_prevention"
    OPTIMIZATION = "optimization"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    PERFORMANCE = "performance"


class RecommendationPriority(Enum):
    """Priority levels for recommendations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Recommendation:
    """A recommendation for action.

    Attributes:
        id: Unique recommendation identifier
        type: Type of recommendation
        priority: Priority level
        title: Short descriptive title
        description: Detailed description
        context: Context where recommendation applies
        action: Specific action to take
        expected_outcome: Expected outcome if applied
        confidence: Confidence in recommendation (0-1)
        reasoning: Explanation of why this is recommended
        supporting_evidence: Evidence supporting the recommendation
        estimated_effort: Estimated effort to implement
        estimated_impact: Estimated impact if implemented
        prerequisites: Prerequisites for applying recommendation
        risks: Potential risks of applying recommendation
        created_at: When recommendation was created
        expires_at: When recommendation expires
        applied: Whether recommendation has been applied
        ab_test_group: A/B test group (if applicable)
    """

    id: str
    type: RecommendationType
    priority: RecommendationPriority
    title: str
    description: str
    context: dict[str, Any]
    action: dict[str, Any]
    expected_outcome: dict[str, Any]
    confidence: float
    reasoning: str
    supporting_evidence: list[str]
    estimated_effort: str
    estimated_impact: str
    prerequisites: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    applied: bool = False
    ab_test_group: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert recommendation to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "context": self.context,
            "action": self.action,
            "expected_outcome": self.expected_outcome,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "supporting_evidence": self.supporting_evidence,
            "estimated_effort": self.estimated_effort,
            "estimated_impact": self.estimated_impact,
            "prerequisites": self.prerequisites,
            "risks": self.risks,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "applied": self.applied,
            "ab_test_group": self.ab_test_group,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Recommendation:
        """Create recommendation from dictionary."""
        data["type"] = RecommendationType(data["type"])
        data["priority"] = RecommendationPriority(data["priority"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("expires_at"):
            data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return cls(**data)

    def is_expired(self) -> bool:
        """Check if recommendation has expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    def get_urgency_score(self) -> float:
        """Calculate urgency score based on priority and expiration."""
        priority_scores = {
            RecommendationPriority.CRITICAL: 1.0,
            RecommendationPriority.HIGH: 0.8,
            RecommendationPriority.MEDIUM: 0.6,
            RecommendationPriority.LOW: 0.4,
        }

        base_score = priority_scores[self.priority]

        # Increase urgency as expiration approaches
        if self.expires_at:
            time_until_expiry = self.expires_at - datetime.now()
            if time_until_expiry.total_seconds() > 0:
                days_until_expiry = time_until_expiry.days + 1
                urgency_multiplier = max(
                    1.0, 7.0 / days_until_expiry
                )  # More urgent as expiry approaches
                base_score *= urgency_multiplier

        return min(1.0, base_score)


class RecommendationGenerator(ABC):
    """Abstract base class for recommendation generators."""

    @abstractmethod
    async def generate_recommendations(self, context: dict[str, Any]) -> list[Recommendation]:
        """Generate recommendations for the given context.

        Args:
            context: Current context for recommendations

        Returns:
            List of recommendations
        """
        pass


class PatternRecommendationGenerator(RecommendationGenerator):
    """Generates recommendations based on applicable patterns."""

    def __init__(self, pattern_db: PatternDatabase):
        """Initialize pattern recommendation generator.

        Args:
            pattern_db: Pattern database
        """
        self.pattern_db = pattern_db
        self.logger = logging.getLogger(self.__class__.__name__)

    async def generate_recommendations(self, context: dict[str, Any]) -> list[Recommendation]:
        """Generate pattern-based recommendations."""
        try:
            recommendations = []

            # Find applicable patterns
            applicable_patterns = await self._find_applicable_patterns(context)

            for pattern, relevance_score in applicable_patterns:
                recommendation = await self._pattern_to_recommendation(
                    pattern, context, relevance_score
                )
                if recommendation:
                    recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            self.logger.error(f"Failed to generate pattern recommendations: {e}")
            return []

    async def _find_applicable_patterns(
        self, context: dict[str, Any]
    ) -> list[tuple[Pattern, float]]:
        """Find patterns applicable to the current context."""
        all_patterns = await self.pattern_db.get_all_patterns()

        applicable_patterns = []
        for pattern in all_patterns:
            relevance_score = await self._calculate_pattern_relevance(pattern, context)
            if relevance_score >= MIN_CONFIDENCE_THRESHOLD:
                applicable_patterns.append((pattern, relevance_score))

        # Sort by relevance
        applicable_patterns.sort(key=lambda x: x[1], reverse=True)
        return applicable_patterns[:10]  # Top 10 most relevant

    async def _calculate_pattern_relevance(
        self, pattern: Pattern, context: dict[str, Any]
    ) -> float:
        """Calculate how relevant a pattern is to the current context."""
        relevance_factors = []

        # Context matching
        context_match = self._calculate_context_match(pattern.context, context)
        relevance_factors.append(context_match * 0.4)

        # Pattern confidence
        relevance_factors.append(pattern.confidence * 0.3)

        # Success rate
        relevance_factors.append(pattern.success_rate * 0.2)

        # Usage frequency (normalized)
        frequency_score = min(1.0, pattern.usage_count / 10)
        relevance_factors.append(frequency_score * 0.1)

        return sum(relevance_factors)

    def _calculate_context_match(
        self, pattern_context: dict[str, Any], current_context: dict[str, Any]
    ) -> float:
        """Calculate how well pattern context matches current context."""
        if not pattern_context or not current_context:
            return 0.0

        matches = 0
        total_keys = 0

        for key, pattern_value in pattern_context.items():
            total_keys += 1

            if key in current_context:
                current_value = current_context[key]

                if isinstance(pattern_value, list) and isinstance(current_value, list):
                    # Calculate overlap for lists
                    pattern_set = set(pattern_value)
                    current_set = set(current_value)
                    if pattern_set and current_set:
                        overlap = len(pattern_set.intersection(current_set))
                        union = len(pattern_set.union(current_set))
                        matches += overlap / union
                elif pattern_value == current_value:
                    matches += 1
                elif isinstance(pattern_value, dict) and isinstance(current_value, (int, float)):
                    # Handle range matching
                    if "min" in pattern_value and "max" in pattern_value:
                        if pattern_value["min"] <= current_value <= pattern_value["max"]:
                            matches += 1
                    elif "min" in pattern_value and current_value >= pattern_value["min"]:
                        matches += 0.5
                    elif "max" in pattern_value and current_value <= pattern_value["max"]:
                        matches += 0.5

        return matches / total_keys if total_keys > 0 else 0.0

    async def _pattern_to_recommendation(
        self, pattern: Pattern, context: dict[str, Any], relevance_score: float
    ) -> Optional[Recommendation]:
        """Convert a pattern to a recommendation."""
        try:
            # Determine priority based on pattern and context
            priority = self._determine_priority(pattern, context, relevance_score)

            recommendation = Recommendation(
                id=f"rec_{hashlib.md5(f'pattern_{pattern.id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}",
                type=self._map_pattern_category_to_recommendation_type(pattern.category),
                priority=priority,
                title=f"Apply {pattern.name}",
                description=f"{pattern.description}\n\nThis pattern has been successful {pattern.usage_count} times with a {pattern.success_rate:.1%} success rate.",
                context=context,
                action=pattern.action,
                expected_outcome=pattern.outcome,
                confidence=relevance_score,
                reasoning=f"Pattern '{pattern.name}' is highly relevant to your current context. {self._generate_reasoning(pattern, context)}",
                supporting_evidence=[
                    f"Success rate: {pattern.success_rate:.1%}",
                    f"Used successfully {pattern.usage_count} times",
                    f"Confidence score: {pattern.confidence:.1%}",
                    f"Relevance to current context: {relevance_score:.1%}",
                ],
                estimated_effort=self._estimate_effort(pattern),
                estimated_impact=self._estimate_impact(pattern),
                prerequisites=pattern.prerequisites,
                risks=self._identify_risks(pattern),
                expires_at=datetime.now() + timedelta(days=7),  # Patterns expire in a week
            )

            return recommendation

        except Exception as e:
            self.logger.error(f"Failed to convert pattern to recommendation: {e}")
            return None

    def _map_pattern_category_to_recommendation_type(self, category: str) -> RecommendationType:
        """Map pattern category to recommendation type."""
        mapping = {
            "testing": RecommendationType.TESTING,
            "documentation": RecommendationType.DOCUMENTATION,
            "security": RecommendationType.SECURITY,
            "performance": RecommendationType.PERFORMANCE,
            "refactoring": RecommendationType.REFACTORING,
            "improvement": RecommendationType.OPTIMIZATION,
            "fix": RecommendationType.FAILURE_PREVENTION,
        }
        return mapping.get(category, RecommendationType.OPTIMIZATION)

    def _determine_priority(
        self, pattern: Pattern, context: dict[str, Any], relevance_score: float
    ) -> RecommendationPriority:
        """Determine priority for pattern recommendation."""
        # High priority for security and critical patterns
        if pattern.category == "security":
            return RecommendationPriority.CRITICAL

        # High priority for high-confidence, high-relevance patterns
        if pattern.confidence >= 0.9 and relevance_score >= 0.8:
            return RecommendationPriority.HIGH

        # Medium priority for moderately confident patterns
        if pattern.confidence >= 0.7 and relevance_score >= 0.6:
            return RecommendationPriority.MEDIUM

        return RecommendationPriority.LOW

    def _generate_reasoning(self, pattern: Pattern, context: dict[str, Any]) -> str:
        """Generate reasoning for why pattern is recommended."""
        reasons = []

        if pattern.success_rate >= 0.9:
            reasons.append("This pattern has a very high success rate.")

        if pattern.usage_count >= 10:
            reasons.append("This pattern has been proven effective in many similar situations.")

        if pattern.category == "security":
            reasons.append("Implementing this pattern will improve security posture.")
        elif pattern.category == "performance":
            reasons.append("This pattern can significantly improve performance.")
        elif pattern.category == "testing":
            reasons.append("This pattern will increase test coverage and code quality.")

        # Check context-specific reasons
        if "test_coverage" in context and context["test_coverage"] < 80:
            if pattern.category == "testing":
                reasons.append("Your current test coverage is below recommended levels.")

        if "complexity_score" in context and context["complexity_score"] > 70:
            if pattern.category == "refactoring":
                reasons.append("Your code complexity is high and could benefit from refactoring.")

        return (
            " ".join(reasons)
            if reasons
            else "This pattern matches your current development context."
        )

    def _estimate_effort(self, pattern: Pattern) -> str:
        """Estimate effort required to implement pattern."""
        if pattern.category in ["documentation", "testing"]:
            return "Low to Medium"
        elif pattern.category in ["refactoring", "performance"]:
            return "Medium to High"
        elif pattern.category == "security":
            return "Medium"
        else:
            return "Low"

    def _estimate_impact(self, pattern: Pattern) -> str:
        """Estimate impact of implementing pattern."""
        if pattern.success_rate >= 0.9:
            return "High"
        elif pattern.success_rate >= 0.7:
            return "Medium to High"
        elif pattern.success_rate >= 0.5:
            return "Medium"
        else:
            return "Low to Medium"

    def _identify_risks(self, pattern: Pattern) -> list[str]:
        """Identify potential risks of applying pattern."""
        risks = []

        if pattern.category == "refactoring":
            risks.append("May introduce bugs if not carefully implemented")
            risks.append("Could temporarily reduce development velocity")

        if pattern.category == "performance":
            risks.append("May increase code complexity")
            risks.append("Could affect maintainability")

        if pattern.success_rate < 0.8:
            risks.append("Pattern has moderate success rate - careful monitoring recommended")

        if pattern.conflicts:
            risks.append(f"May conflict with patterns: {', '.join(pattern.conflicts)}")

        return risks


class KnowledgeRecommendationGenerator(RecommendationGenerator):
    """Generates recommendations based on knowledge graph insights."""

    def __init__(self, knowledge_graph: KnowledgeGraph):
        """Initialize knowledge recommendation generator.

        Args:
            knowledge_graph: Knowledge graph
        """
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger(self.__class__.__name__)

    async def generate_recommendations(self, context: dict[str, Any]) -> list[Recommendation]:
        """Generate knowledge-based recommendations."""
        try:
            recommendations = []

            # Find relevant nodes in knowledge graph
            relevant_nodes = await self._find_relevant_nodes(context)

            for node, relevance_score in relevant_nodes:
                node_recommendations = await self._node_to_recommendations(
                    node, context, relevance_score
                )
                recommendations.extend(node_recommendations)

            return recommendations

        except Exception as e:
            self.logger.error(f"Failed to generate knowledge recommendations: {e}")
            return []

    async def _find_relevant_nodes(
        self, context: dict[str, Any]
    ) -> list[tuple[KnowledgeNode, float]]:
        """Find relevant nodes in the knowledge graph."""
        # This is a simplified implementation
        # In practice, you'd use more sophisticated graph algorithms

        relevant_nodes = []

        # Search for nodes based on context
        query = {"node_criteria": {"min_importance": 0.6}, "limit": 20}

        nodes = await self.knowledge_graph.query_graph(query)

        for node in nodes:
            relevance_score = self._calculate_node_relevance(node, context)
            if relevance_score >= 0.5:
                relevant_nodes.append((node, relevance_score))

        relevant_nodes.sort(key=lambda x: x[1], reverse=True)
        return relevant_nodes[:10]

    def _calculate_node_relevance(self, node: KnowledgeNode, context: dict[str, Any]) -> float:
        """Calculate relevance of a knowledge node to current context."""
        relevance_factors = []

        # Node importance
        relevance_factors.append(node.importance * 0.4)

        # Tag matching
        context_tags = context.get("tags", [])
        if context_tags and node.tags:
            tag_overlap = len(set(context_tags).intersection(set(node.tags)))
            tag_relevance = tag_overlap / len(context_tags) if context_tags else 0
            relevance_factors.append(tag_relevance * 0.3)
        else:
            relevance_factors.append(0.0)

        # Property matching
        property_relevance = self._calculate_property_match(node.properties, context)
        relevance_factors.append(property_relevance * 0.3)

        return sum(relevance_factors)

    def _calculate_property_match(
        self, node_properties: dict[str, Any], context: dict[str, Any]
    ) -> float:
        """Calculate property matching between node and context."""
        if not node_properties or not context:
            return 0.0

        matches = 0
        total = 0

        for key, value in node_properties.items():
            if key in context:
                total += 1
                if context[key] == value:
                    matches += 1

        return matches / total if total > 0 else 0.0

    async def _node_to_recommendations(
        self, node: KnowledgeNode, context: dict[str, Any], relevance_score: float
    ) -> list[Recommendation]:
        """Convert knowledge node to recommendations."""
        recommendations = []

        if node.type.value == "pattern":
            # For pattern nodes, recommend applying the pattern
            rec = await self._create_pattern_node_recommendation(node, context, relevance_score)
            if rec:
                recommendations.append(rec)

        elif node.type.value == "failure":
            # For failure nodes, recommend prevention measures
            rec = await self._create_failure_prevention_recommendation(
                node, context, relevance_score
            )
            if rec:
                recommendations.append(rec)

        return recommendations

    async def _create_pattern_node_recommendation(
        self, node: KnowledgeNode, context: dict[str, Any], relevance_score: float
    ) -> Optional[Recommendation]:
        """Create recommendation from pattern node."""
        try:
            recommendation = Recommendation(
                id=f"rec_{hashlib.md5(f'knode_{node.id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}",
                type=RecommendationType.PATTERN_APPLICATION,
                priority=RecommendationPriority.MEDIUM,
                title=f"Consider {node.label}",
                description=f"Knowledge graph analysis suggests applying pattern: {node.label}",
                context=context,
                action={"type": "apply_pattern", "pattern_id": node.id},
                expected_outcome={"improvement": "positive"},
                confidence=relevance_score,
                reasoning=f"This pattern node has high relevance in the knowledge graph with importance score {node.importance:.2f}",
                supporting_evidence=[
                    f"Node importance: {node.importance:.2f}",
                    f"Relevance score: {relevance_score:.2f}",
                    f"Connected to {len(node.tags)} related concepts",
                ],
                estimated_effort="Medium",
                estimated_impact="Medium",
                expires_at=datetime.now() + timedelta(days=5),
            )

            return recommendation

        except Exception as e:
            self.logger.error(f"Failed to create pattern node recommendation: {e}")
            return None

    async def _create_failure_prevention_recommendation(
        self, node: KnowledgeNode, context: dict[str, Any], relevance_score: float
    ) -> Optional[Recommendation]:
        """Create failure prevention recommendation from failure node."""
        try:
            recommendation = Recommendation(
                id=f"rec_{hashlib.md5(f'fail_{node.id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}",
                type=RecommendationType.FAILURE_PREVENTION,
                priority=RecommendationPriority.HIGH,
                title=f"Prevent {node.label}",
                description=f"Take preventive measures against failure pattern: {node.label}",
                context=context,
                action={"type": "prevent_failure", "failure_pattern": node.id},
                expected_outcome={"failure_risk": "reduced"},
                confidence=relevance_score,
                reasoning=f"Knowledge graph analysis identifies potential failure risk: {node.label}",
                supporting_evidence=[
                    f"Failure pattern importance: {node.importance:.2f}",
                    f"Context relevance: {relevance_score:.2f}",
                    "Proactive prevention recommended",
                ],
                estimated_effort="Low to Medium",
                estimated_impact="High",
                expires_at=datetime.now() + timedelta(days=3),
            )

            return recommendation

        except Exception as e:
            self.logger.error(f"Failed to create failure prevention recommendation: {e}")
            return None


class ABTestManager:
    """Manages A/B testing for recommendations."""

    def __init__(self):
        """Initialize A/B test manager."""
        self.active_tests: dict[str, dict[str, Any]] = {}
        self.test_results: dict[str, dict[str, Any]] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create_ab_test(
        self,
        test_name: str,
        recommendation_variants: list[Recommendation],
        traffic_split: Optional[list[float]] = None,
    ) -> str:
        """Create a new A/B test for recommendations.

        Args:
            test_name: Name of the test
            recommendation_variants: List of recommendation variants to test
            traffic_split: Traffic split percentages (defaults to equal split)

        Returns:
            Test ID
        """
        if not recommendation_variants:
            raise ValueError("Must provide at least one recommendation variant")

        if not traffic_split:
            traffic_split = [1.0 / len(recommendation_variants)] * len(recommendation_variants)

        if len(traffic_split) != len(recommendation_variants):
            raise ValueError("Traffic split must match number of variants")

        if abs(sum(traffic_split) - 1.0) > 0.01:
            raise ValueError("Traffic split must sum to 1.0")

        test_id = f"test_{hashlib.md5(f'{test_name}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"

        self.active_tests[test_id] = {
            "name": test_name,
            "variants": recommendation_variants,
            "traffic_split": traffic_split,
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(hours=A_B_TEST_DURATION_HOURS),
            "assignments": {},  # user_id -> variant_index
            "metrics": {
                i: {"applications": 0, "successes": 0, "failures": 0}
                for i in range(len(recommendation_variants))
            },
        }

        # Assign test groups to recommendations
        for i, recommendation in enumerate(recommendation_variants):
            recommendation.ab_test_group = f"{test_id}_variant_{i}"

        self.logger.info(
            f"Created A/B test: {test_id} with {len(recommendation_variants)} variants"
        )
        return test_id

    async def assign_user_to_variant(self, test_id: str, user_id: str) -> Optional[Recommendation]:
        """Assign user to a test variant and return the recommendation.

        Args:
            test_id: Test identifier
            user_id: User identifier

        Returns:
            Recommendation for assigned variant, or None if test not found
        """
        if test_id not in self.active_tests:
            return None

        test = self.active_tests[test_id]

        # Check if test has expired
        if datetime.now() > test["end_time"]:
            await self._end_test(test_id)
            return None

        # Check if user already assigned
        if user_id in test["assignments"]:
            variant_index = test["assignments"][user_id]
            return test["variants"][variant_index]

        # Assign user to variant based on traffic split
        variant_index = self._select_variant(test["traffic_split"])
        test["assignments"][user_id] = variant_index

        return test["variants"][variant_index]

    def _select_variant(self, traffic_split: list[float]) -> int:
        """Select variant based on traffic split."""
        random_value = random.random()
        cumulative = 0.0

        for i, split in enumerate(traffic_split):
            cumulative += split
            if random_value <= cumulative:
                return i

        return len(traffic_split) - 1  # Fallback to last variant

    async def record_test_result(
        self, test_id: str, user_id: str, applied: bool, success: bool
    ) -> None:
        """Record result of applying a test recommendation.

        Args:
            test_id: Test identifier
            user_id: User identifier
            applied: Whether recommendation was applied
            success: Whether application was successful
        """
        if test_id not in self.active_tests:
            return

        test = self.active_tests[test_id]

        if user_id not in test["assignments"]:
            return

        variant_index = test["assignments"][user_id]
        metrics = test["metrics"][variant_index]

        if applied:
            metrics["applications"] += 1
            if success:
                metrics["successes"] += 1
            else:
                metrics["failures"] += 1

        self.logger.debug(
            f"Recorded test result for {test_id}, variant {variant_index}: applied={applied}, success={success}"
        )

    async def get_test_results(self, test_id: str) -> Optional[dict[str, Any]]:
        """Get current results for an A/B test.

        Args:
            test_id: Test identifier

        Returns:
            Test results dictionary, or None if test not found
        """
        if test_id not in self.active_tests and test_id not in self.test_results:
            return None

        if test_id in self.test_results:
            return self.test_results[test_id]

        test = self.active_tests[test_id]

        results = {
            "test_id": test_id,
            "name": test["name"],
            "start_time": test["start_time"].isoformat(),
            "end_time": test["end_time"].isoformat(),
            "status": "active" if datetime.now() <= test["end_time"] else "completed",
            "variants": [],
            "statistical_significance": None,
            "winning_variant": None,
        }

        total_assignments = len(test["assignments"])

        for i, variant in enumerate(test["variants"]):
            metrics = test["metrics"][i]
            variant_assignments = sum(
                1 for assignment in test["assignments"].values() if assignment == i
            )

            success_rate = (
                metrics["successes"] / metrics["applications"] if metrics["applications"] > 0 else 0
            )
            conversion_rate = (
                metrics["applications"] / variant_assignments if variant_assignments > 0 else 0
            )

            variant_result = {
                "variant_index": i,
                "recommendation_title": variant.title,
                "assignments": variant_assignments,
                "applications": metrics["applications"],
                "successes": metrics["successes"],
                "failures": metrics["failures"],
                "success_rate": success_rate,
                "conversion_rate": conversion_rate,
            }

            results["variants"].append(variant_result)

        # Calculate statistical significance
        if len(results["variants"]) >= 2:
            results["statistical_significance"] = self._calculate_statistical_significance(
                results["variants"]
            )
            results["winning_variant"] = self._determine_winning_variant(results["variants"])

        return results

    def _calculate_statistical_significance(self, variants: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate statistical significance between variants."""
        # Simplified chi-square test implementation
        # In practice, you'd use a proper statistical library

        if len(variants) < 2:
            return {"significant": False, "p_value": 1.0}

        # Compare first two variants
        v1, v2 = variants[0], variants[1]

        # Chi-square test for success rates
        n1, n2 = v1["applications"], v2["applications"]
        s1, s2 = v1["successes"], v2["successes"]

        if n1 == 0 or n2 == 0:
            return {"significant": False, "p_value": 1.0}

        p1, p2 = s1 / n1, s2 / n2
        p_pooled = (s1 + s2) / (n1 + n2)

        if p_pooled == 0 or p_pooled == 1:
            return {"significant": False, "p_value": 1.0}

        # Simplified z-test
        se = math.sqrt(p_pooled * (1 - p_pooled) * (1 / n1 + 1 / n2))
        z_score = abs(p1 - p2) / se if se > 0 else 0

        # Rough p-value approximation
        p_value = 2 * (1 - self._standard_normal_cdf(abs(z_score)))

        return {"significant": p_value < 0.05, "p_value": p_value, "z_score": z_score}

    def _standard_normal_cdf(self, x: float) -> float:
        """Approximate standard normal CDF."""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def _determine_winning_variant(self, variants: list[dict[str, Any]]) -> Optional[int]:
        """Determine winning variant based on success rate."""
        if not variants:
            return None

        best_variant = max(variants, key=lambda v: v["success_rate"])
        return best_variant["variant_index"]

    async def _end_test(self, test_id: str) -> None:
        """End an active test and move results to completed tests."""
        if test_id in self.active_tests:
            results = await self.get_test_results(test_id)
            if results:
                self.test_results[test_id] = results

            del self.active_tests[test_id]
            self.logger.info(f"Ended A/B test: {test_id}")


class RecommendationEngine:
    """Main recommendation engine system.

    Generates intelligent recommendations based on patterns, knowledge graph,
    and A/B testing results to optimize evolution strategies.

    Example:
        >>> engine = RecommendationEngine(pattern_db, knowledge_graph, memory_curator)
        >>> await engine.initialize()
        >>> recommendations = await engine.get_recommendations(context)
        >>> await engine.apply_recommendation(recommendation_id, user_id)
    """

    def __init__(
        self,
        pattern_db: PatternDatabase,
        knowledge_graph: KnowledgeGraph,
        memory_curator: MemoryCurator,
    ):
        """Initialize recommendation engine.

        Args:
            pattern_db: Pattern database
            knowledge_graph: Knowledge graph
            memory_curator: Memory curator
        """
        self.pattern_db = pattern_db
        self.knowledge_graph = knowledge_graph
        self.memory_curator = memory_curator

        self.generators = [
            PatternRecommendationGenerator(pattern_db),
            KnowledgeRecommendationGenerator(knowledge_graph),
        ]

        self.ab_test_manager = ABTestManager()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Recommendation storage
        self.active_recommendations: dict[str, Recommendation] = {}
        self.applied_recommendations: dict[str, Recommendation] = {}

    async def initialize(self) -> None:
        """Initialize the recommendation engine."""
        self.logger.info("Recommendation engine initialized")

    async def get_recommendations(
        self,
        context: dict[str, Any],
        user_id: Optional[str] = None,
        max_recommendations: int = MAX_RECOMMENDATIONS,
    ) -> list[Recommendation]:
        """Get recommendations for the given context.

        Args:
            context: Current context for recommendations
            user_id: User ID for A/B testing (optional)
            max_recommendations: Maximum number of recommendations

        Returns:
            List of recommendations sorted by priority and confidence
        """
        try:
            all_recommendations = []

            # Generate recommendations from all generators
            for generator in self.generators:
                try:
                    recommendations = await generator.generate_recommendations(context)
                    all_recommendations.extend(recommendations)
                except Exception as e:
                    self.logger.error(f"Error in generator {generator.__class__.__name__}: {e}")

            # Filter and deduplicate recommendations
            filtered_recommendations = await self._filter_recommendations(
                all_recommendations, context
            )

            # Apply A/B testing if user_id provided
            if user_id:
                filtered_recommendations = await self._apply_ab_testing(
                    filtered_recommendations, user_id
                )

            # Sort by priority and confidence
            sorted_recommendations = await self._sort_recommendations(filtered_recommendations)

            # Store active recommendations
            for rec in sorted_recommendations[:max_recommendations]:
                self.active_recommendations[rec.id] = rec

            self.logger.info(f"Generated {len(sorted_recommendations)} recommendations for context")
            return sorted_recommendations[:max_recommendations]

        except Exception as e:
            self.logger.error(f"Failed to get recommendations: {e}")
            return []

    async def _filter_recommendations(
        self, recommendations: list[Recommendation], context: dict[str, Any]
    ) -> list[Recommendation]:
        """Filter recommendations based on quality and relevance."""
        filtered = []
        seen_actions = set()

        for rec in recommendations:
            # Skip expired recommendations
            if rec.is_expired():
                continue

            # Skip low confidence recommendations
            if rec.confidence < MIN_CONFIDENCE_THRESHOLD:
                continue

            # Skip duplicate actions
            action_key = json.dumps(rec.action, sort_keys=True)
            if action_key in seen_actions:
                continue
            seen_actions.add(action_key)

            # Apply context-specific filters
            if await self._is_recommendation_applicable(rec, context):
                filtered.append(rec)

        return filtered

    async def _is_recommendation_applicable(
        self, recommendation: Recommendation, context: dict[str, Any]
    ) -> bool:
        """Check if recommendation is applicable to current context."""
        # Check prerequisites
        for prerequisite in recommendation.prerequisites:
            if not self._check_prerequisite(prerequisite, context):
                return False

        # Check context compatibility
        if not self._check_context_compatibility(recommendation.context, context):
            return False

        return True

    def _check_prerequisite(self, prerequisite: str, context: dict[str, Any]) -> bool:
        """Check if prerequisite is met in current context."""
        # Simplified prerequisite checking
        # In practice, this would be more sophisticated

        if "python" in prerequisite.lower():
            return context.get("language") == "python"
        elif "test" in prerequisite.lower():
            return context.get("has_tests", False)
        elif "git" in prerequisite.lower():
            return context.get("has_git", False)

        return True  # Default to True for unknown prerequisites

    def _check_context_compatibility(
        self, rec_context: dict[str, Any], current_context: dict[str, Any]
    ) -> bool:
        """Check if recommendation context is compatible with current context."""
        # Check required context keys
        for key, value in rec_context.items():
            if key.startswith("required_") and key[9:] not in current_context:
                return False

        return True

    async def _apply_ab_testing(
        self, recommendations: list[Recommendation], user_id: str
    ) -> list[Recommendation]:
        """Apply A/B testing to recommendations."""
        # For now, just return original recommendations
        # In practice, this would select test variants
        return recommendations

    async def _sort_recommendations(
        self, recommendations: list[Recommendation]
    ) -> list[Recommendation]:
        """Sort recommendations by priority and confidence."""

        def sort_key(rec: Recommendation) -> tuple[float, float, float]:
            priority_scores = {
                RecommendationPriority.CRITICAL: 4.0,
                RecommendationPriority.HIGH: 3.0,
                RecommendationPriority.MEDIUM: 2.0,
                RecommendationPriority.LOW: 1.0,
            }

            return (priority_scores[rec.priority], rec.confidence, rec.get_urgency_score())

        return sorted(recommendations, key=sort_key, reverse=True)

    async def apply_recommendation(
        self, recommendation_id: str, user_id: Optional[str] = None, success: Optional[bool] = None
    ) -> bool:
        """Apply a recommendation and record the result.

        Args:
            recommendation_id: Recommendation identifier
            user_id: User applying the recommendation
            success: Whether application was successful (None if not yet determined)

        Returns:
            True if recommendation was found and marked as applied
        """
        if recommendation_id not in self.active_recommendations:
            return False

        recommendation = self.active_recommendations[recommendation_id]
        recommendation.applied = True

        # Move to applied recommendations
        self.applied_recommendations[recommendation_id] = recommendation
        del self.active_recommendations[recommendation_id]

        # Record A/B test result if applicable
        if recommendation.ab_test_group and user_id:
            test_id = recommendation.ab_test_group.split("_variant_")[0]
            await self.ab_test_manager.record_test_result(
                test_id, user_id, applied=True, success=success if success is not None else True
            )

        # Store memory of recommendation application
        await self._store_recommendation_memory(recommendation, user_id, success)

        self.logger.info(f"Applied recommendation: {recommendation_id}")
        return True

    async def _store_recommendation_memory(
        self, recommendation: Recommendation, user_id: Optional[str], success: Optional[bool]
    ) -> None:
        """Store memory of recommendation application."""
        try:
            memory_data = {
                "recommendation_id": recommendation.id,
                "type": recommendation.type.value,
                "priority": recommendation.priority.value,
                "applied_by": user_id,
                "success": success,
                "context": recommendation.context,
                "action": recommendation.action,
            }

            await self.memory_curator.store_memory(
                Memory(
                    id=f"memory_{hashlib.md5(f'rec_{recommendation.id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}",
                    type="recommendation_result",
                    timestamp=datetime.now(),
                    data=memory_data,
                    metadata={
                        "importance": 0.7,
                        "tags": ["recommendation", recommendation.type.value],
                        "retention_score": 0.8,
                    },
                )
            )

        except Exception as e:
            self.logger.error(f"Failed to store recommendation memory: {e}")

    async def get_recommendation_analytics(self) -> dict[str, Any]:
        """Get analytics about recommendation performance.

        Returns:
            Dictionary containing recommendation analytics
        """
        try:
            analytics = {
                "total_recommendations_generated": len(self.active_recommendations)
                + len(self.applied_recommendations),
                "active_recommendations": len(self.active_recommendations),
                "applied_recommendations": len(self.applied_recommendations),
                "application_rate": 0.0,
                "type_distribution": defaultdict(int),
                "priority_distribution": defaultdict(int),
                "avg_confidence": 0.0,
                "ab_tests": {
                    "active": len(self.ab_test_manager.active_tests),
                    "completed": len(self.ab_test_manager.test_results),
                },
            }

            all_recommendations = list(self.active_recommendations.values()) + list(
                self.applied_recommendations.values()
            )

            if all_recommendations:
                # Application rate
                applied_count = len(self.applied_recommendations)
                total_count = len(all_recommendations)
                analytics["application_rate"] = applied_count / total_count

                # Type and priority distribution
                confidences = []
                for rec in all_recommendations:
                    analytics["type_distribution"][rec.type.value] += 1
                    analytics["priority_distribution"][rec.priority.value] += 1
                    confidences.append(rec.confidence)

                # Average confidence
                analytics["avg_confidence"] = sum(confidences) / len(confidences)

            return dict(analytics)

        except Exception as e:
            self.logger.error(f"Failed to get recommendation analytics: {e}")
            return {"error": str(e)}
