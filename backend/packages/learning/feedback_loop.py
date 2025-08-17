"""
Feedback Loop System for T-Developer

This module implements a continuous improvement feedback loop that measures
learning effectiveness, analyzes outcomes, and automatically adjusts
learning strategies to optimize performance over time.

The FeedbackLoop monitors system performance, tracks improvements,
and provides closed-loop optimization of the learning system.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import statistics
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from .failure_analyzer import FailureAnalyzer
from .knowledge_graph import KnowledgeGraph
from .memory_curator import Memory, MemoryCurator
from .pattern_database import PatternDatabase
from .recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT: int = 30
LEARNING_WINDOW_DAYS: int = 30
MIN_SAMPLE_SIZE: int = 5
IMPROVEMENT_THRESHOLD: float = 0.05  # 5% improvement threshold


class MetricType(Enum):
    """Types of metrics tracked by the feedback loop."""

    PATTERN_EFFECTIVENESS = "pattern_effectiveness"
    FAILURE_REDUCTION = "failure_reduction"
    RECOMMENDATION_ACCURACY = "recommendation_accuracy"
    CYCLE_EFFICIENCY = "cycle_efficiency"
    KNOWLEDGE_GROWTH = "knowledge_growth"
    MEMORY_RETENTION = "memory_retention"
    SYSTEM_PERFORMANCE = "system_performance"


class LearningObjective(Enum):
    """Learning objectives that the system optimizes for."""

    REDUCE_CYCLE_TIME = "reduce_cycle_time"
    IMPROVE_SUCCESS_RATE = "improve_success_rate"
    INCREASE_CODE_QUALITY = "increase_code_quality"
    ENHANCE_SECURITY = "enhance_security"
    BOOST_PERFORMANCE = "boost_performance"
    MINIMIZE_FAILURES = "minimize_failures"


@dataclass
class LearningMetrics:
    """Container for learning effectiveness metrics.

    Attributes:
        timestamp: When metrics were measured
        pattern_effectiveness: How effective applied patterns are
        failure_reduction_rate: Rate of failure reduction over time
        recommendation_accuracy: Accuracy of recommendations
        cycle_efficiency: Efficiency of evolution cycles
        knowledge_growth_rate: Rate of knowledge base growth
        memory_retention_score: How well memories are retained and used
        system_performance_score: Overall system performance
        improvement_velocity: Rate of improvement over time
        learning_velocity: How quickly the system learns
    """

    timestamp: datetime
    pattern_effectiveness: float = 0.0
    failure_reduction_rate: float = 0.0
    recommendation_accuracy: float = 0.0
    cycle_efficiency: float = 0.0
    knowledge_growth_rate: float = 0.0
    memory_retention_score: float = 0.0
    system_performance_score: float = 0.0
    improvement_velocity: float = 0.0
    learning_velocity: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "pattern_effectiveness": self.pattern_effectiveness,
            "failure_reduction_rate": self.failure_reduction_rate,
            "recommendation_accuracy": self.recommendation_accuracy,
            "cycle_efficiency": self.cycle_efficiency,
            "knowledge_growth_rate": self.knowledge_growth_rate,
            "memory_retention_score": self.memory_retention_score,
            "system_performance_score": self.system_performance_score,
            "improvement_velocity": self.improvement_velocity,
            "learning_velocity": self.learning_velocity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LearningMetrics:
        """Create metrics from dictionary."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    def get_overall_score(self) -> float:
        """Calculate overall learning effectiveness score."""
        weights = {
            "pattern_effectiveness": 0.2,
            "failure_reduction_rate": 0.15,
            "recommendation_accuracy": 0.15,
            "cycle_efficiency": 0.15,
            "knowledge_growth_rate": 0.1,
            "memory_retention_score": 0.1,
            "system_performance_score": 0.1,
            "improvement_velocity": 0.05,
        }

        weighted_sum = 0.0
        for metric, weight in weights.items():
            value = getattr(self, metric, 0.0)
            weighted_sum += value * weight

        return min(1.0, max(0.0, weighted_sum))


@dataclass
class LearningInsight:
    """Insight discovered through feedback analysis.

    Attributes:
        id: Unique insight identifier
        type: Type of insight
        title: Brief insight title
        description: Detailed description
        impact: Estimated impact of addressing this insight
        confidence: Confidence in the insight
        supporting_data: Data supporting the insight
        recommended_actions: Actions recommended based on insight
        priority: Priority level for addressing insight
        created_at: When insight was discovered
    """

    id: str
    type: str
    title: str
    description: str
    impact: float
    confidence: float
    supporting_data: dict[str, Any]
    recommended_actions: list[str]
    priority: str = "medium"
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert insight to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "impact": self.impact,
            "confidence": self.confidence,
            "supporting_data": self.supporting_data,
            "recommended_actions": self.recommended_actions,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
        }


class MetricsCalculator:
    """Calculates learning effectiveness metrics."""

    def __init__(self):
        """Initialize metrics calculator."""
        self.logger = logging.getLogger(self.__class__.__name__)

    async def calculate_pattern_effectiveness(
        self,
        pattern_db: PatternDatabase,
        time_window: timedelta = timedelta(days=LEARNING_WINDOW_DAYS),
    ) -> float:
        """Calculate effectiveness of applied patterns.

        Args:
            pattern_db: Pattern database
            time_window: Time window for analysis

        Returns:
            Pattern effectiveness score (0-1)
        """
        try:
            all_patterns = await pattern_db.get_all_patterns()

            if not all_patterns:
                return 0.0

            effectiveness_scores = []
            cutoff_time = datetime.now() - time_window

            for pattern in all_patterns:
                # Only consider patterns used in the time window
                if pattern.last_used and pattern.last_used >= cutoff_time:
                    # Weight by usage count and success rate
                    usage_weight = min(1.0, pattern.usage_count / 10)
                    effectiveness = pattern.success_rate * usage_weight
                    effectiveness_scores.append(effectiveness)

            if not effectiveness_scores:
                return 0.0

            return statistics.mean(effectiveness_scores)

        except Exception as e:
            self.logger.error(f"Failed to calculate pattern effectiveness: {e}")
            return 0.0

    async def calculate_failure_reduction_rate(
        self,
        failure_analyzer: FailureAnalyzer,
        time_window: timedelta = timedelta(days=LEARNING_WINDOW_DAYS),
    ) -> float:
        """Calculate rate of failure reduction over time.

        Args:
            failure_analyzer: Failure analyzer
            time_window: Time window for analysis

        Returns:
            Failure reduction rate (0-1)
        """
        try:
            # Get failure statistics
            stats = await failure_analyzer.get_failure_statistics()

            if not stats or "total_failures" not in stats:
                return 0.0

            # Calculate trend in failure frequency
            # This is simplified - in practice you'd analyze time series data
            total_failures = stats["total_failures"]
            total_patterns = stats.get("total_patterns", 1)

            # Assume each pattern prevents some failures
            prevention_effectiveness = min(1.0, total_patterns / max(1, total_failures))

            return prevention_effectiveness

        except Exception as e:
            self.logger.error(f"Failed to calculate failure reduction rate: {e}")
            return 0.0

    async def calculate_recommendation_accuracy(
        self, recommendation_engine: RecommendationEngine
    ) -> float:
        """Calculate accuracy of recommendations.

        Args:
            recommendation_engine: Recommendation engine

        Returns:
            Recommendation accuracy score (0-1)
        """
        try:
            analytics = await recommendation_engine.get_recommendation_analytics()

            # Use application rate as proxy for accuracy
            # Applied recommendations are assumed to be accurate
            application_rate = analytics.get("application_rate", 0.0)

            # Adjust for confidence - higher confidence recommendations
            # should have higher accuracy expectations
            avg_confidence = analytics.get("avg_confidence", 0.5)

            # Accuracy score combines application rate with confidence
            accuracy = application_rate * (0.5 + 0.5 * avg_confidence)

            return min(1.0, accuracy)

        except Exception as e:
            self.logger.error(f"Failed to calculate recommendation accuracy: {e}")
            return 0.0

    async def calculate_cycle_efficiency(self, memory_curator: MemoryCurator) -> float:
        """Calculate efficiency of evolution cycles.

        Args:
            memory_curator: Memory curator

        Returns:
            Cycle efficiency score (0-1)
        """
        try:
            # Get recent evolution cycle memories
            recent_memories = await memory_curator.get_recent_memories(
                memory_type="evolution_cycle", hours=24 * LEARNING_WINDOW_DAYS
            )

            if not recent_memories:
                return 0.0

            efficiency_scores = []

            for memory in recent_memories:
                cycle_data = memory.data

                # Calculate efficiency based on duration and success
                duration = cycle_data.get("duration", 0)
                success = cycle_data.get("success", False)

                if duration > 0:
                    # Normalize duration (assuming 300 seconds is baseline)
                    duration_score = max(0.0, 1.0 - (duration / 300))

                    # Weight by success
                    if success:
                        efficiency = duration_score
                    else:
                        efficiency = duration_score * 0.1  # Failed cycles get very low efficiency

                    efficiency_scores.append(efficiency)

            if not efficiency_scores:
                return 0.0

            return statistics.mean(efficiency_scores)

        except Exception as e:
            self.logger.error(f"Failed to calculate cycle efficiency: {e}")
            return 0.0

    async def calculate_knowledge_growth_rate(self, knowledge_graph: KnowledgeGraph) -> float:
        """Calculate rate of knowledge base growth.

        Args:
            knowledge_graph: Knowledge graph

        Returns:
            Knowledge growth rate (0-1)
        """
        try:
            stats = await knowledge_graph.get_graph_statistics()

            total_nodes = stats.get("total_nodes", 0)
            total_relationships = stats.get("total_relationships", 0)

            # Simple growth rate calculation
            # In practice, you'd track this over time
            if total_nodes == 0:
                return 0.0

            # Relationship density as proxy for knowledge richness
            density = stats.get("density", 0.0)

            # Growth rate based on node count and density
            node_score = min(1.0, total_nodes / 1000)  # Normalize to 1000 nodes
            density_score = min(1.0, density * 10)  # Amplify density

            growth_rate = (node_score + density_score) / 2
            return growth_rate

        except Exception as e:
            self.logger.error(f"Failed to calculate knowledge growth rate: {e}")
            return 0.0

    async def calculate_memory_retention_score(self, memory_curator: MemoryCurator) -> float:
        """Calculate memory retention effectiveness.

        Args:
            memory_curator: Memory curator

        Returns:
            Memory retention score (0-1)
        """
        try:
            stats = await memory_curator.get_memory_statistics()

            cache_hit_rate = stats.get("cache_hit_rate", 0.0)
            total_memories = stats.get("total_memories", 0)

            if total_memories == 0:
                return 0.0

            # Memory retention combines cache efficiency with memory volume
            volume_score = min(1.0, total_memories / 1000)  # Normalize to 1000 memories
            efficiency_score = cache_hit_rate

            retention_score = (volume_score + efficiency_score) / 2
            return retention_score

        except Exception as e:
            self.logger.error(f"Failed to calculate memory retention score: {e}")
            return 0.0

    async def calculate_system_performance_score(
        self, recent_metrics: list[LearningMetrics]
    ) -> float:
        """Calculate overall system performance score.

        Args:
            recent_metrics: Recent learning metrics

        Returns:
            System performance score (0-1)
        """
        try:
            if not recent_metrics:
                return 0.0

            # Calculate weighted average of all metrics
            total_score = 0.0

            for metrics in recent_metrics:
                overall_score = metrics.get_overall_score()
                total_score += overall_score

            performance_score = total_score / len(recent_metrics)
            return performance_score

        except Exception as e:
            self.logger.error(f"Failed to calculate system performance score: {e}")
            return 0.0


class InsightGenerator:
    """Generates insights from learning metrics and trends."""

    def __init__(self):
        """Initialize insight generator."""
        self.logger = logging.getLogger(self.__class__.__name__)

    async def generate_insights(
        self, metrics_history: list[LearningMetrics], current_metrics: LearningMetrics
    ) -> list[LearningInsight]:
        """Generate insights from metrics history.

        Args:
            metrics_history: Historical metrics
            current_metrics: Current metrics

        Returns:
            List of generated insights
        """
        insights = []

        try:
            # Trend analysis insights
            trend_insights = await self._analyze_trends(metrics_history, current_metrics)
            insights.extend(trend_insights)

            # Performance insights
            performance_insights = await self._analyze_performance(current_metrics)
            insights.extend(performance_insights)

            # Optimization insights
            optimization_insights = await self._identify_optimization_opportunities(current_metrics)
            insights.extend(optimization_insights)

            return insights

        except Exception as e:
            self.logger.error(f"Failed to generate insights: {e}")
            return []

    async def _analyze_trends(
        self, metrics_history: list[LearningMetrics], current_metrics: LearningMetrics
    ) -> list[LearningInsight]:
        """Analyze trends in metrics."""
        insights = []

        if len(metrics_history) < 2:
            return insights

        # Calculate trends for each metric
        metrics_to_analyze = [
            "pattern_effectiveness",
            "failure_reduction_rate",
            "recommendation_accuracy",
            "cycle_efficiency",
        ]

        for metric_name in metrics_to_analyze:
            trend = self._calculate_trend(metrics_history, metric_name)

            if abs(trend) > IMPROVEMENT_THRESHOLD:
                insight = self._create_trend_insight(metric_name, trend, current_metrics)
                if insight:
                    insights.append(insight)

        return insights

    def _calculate_trend(self, metrics_history: list[LearningMetrics], metric_name: str) -> float:
        """Calculate trend for a specific metric."""
        values = []

        for metrics in metrics_history:
            value = getattr(metrics, metric_name, 0.0)
            values.append(value)

        if len(values) < 2:
            return 0.0

        # Simple linear trend calculation
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))

        if n * x2_sum - x_sum * x_sum == 0:
            return 0.0

        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)

        # Normalize slope to percentage change
        if y_sum > 0:
            trend = slope / (y_sum / n)
        else:
            trend = 0.0

        return trend

    def _create_trend_insight(
        self, metric_name: str, trend: float, current_metrics: LearningMetrics
    ) -> Optional[LearningInsight]:
        """Create insight for metric trend."""
        try:
            current_value = getattr(current_metrics, metric_name, 0.0)

            if trend > 0:
                # Positive trend
                insight = LearningInsight(
                    id=f"insight_{hashlib.md5(f'trend_pos_{metric_name}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}",
                    type="positive_trend",
                    title=f"Improving {metric_name.replace('_', ' ').title()}",
                    description=f"The {metric_name.replace('_', ' ')} has been improving by {trend:.1%} over recent cycles. Current value: {current_value:.1%}",
                    impact=min(1.0, abs(trend) * 2),
                    confidence=min(1.0, abs(trend) * 5),
                    supporting_data={
                        "metric": metric_name,
                        "trend": trend,
                        "current_value": current_value,
                    },
                    recommended_actions=[
                        f"Continue current strategies that are improving {metric_name.replace('_', ' ')}",
                        "Analyze what factors are driving this improvement",
                        "Consider scaling successful approaches",
                    ],
                    priority="low",  # Positive trends are lower priority
                )
            else:
                # Negative trend
                insight = LearningInsight(
                    id=f"insight_{hashlib.md5(f'trend_neg_{metric_name}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}",
                    type="negative_trend",
                    title=f"Declining {metric_name.replace('_', ' ').title()}",
                    description=f"The {metric_name.replace('_', ' ')} has been declining by {abs(trend):.1%} over recent cycles. Current value: {current_value:.1%}",
                    impact=min(1.0, abs(trend) * 3),
                    confidence=min(1.0, abs(trend) * 5),
                    supporting_data={
                        "metric": metric_name,
                        "trend": trend,
                        "current_value": current_value,
                    },
                    recommended_actions=[
                        f"Investigate causes of declining {metric_name.replace('_', ' ')}",
                        "Review recent changes that might have impacted performance",
                        "Consider reverting to previous successful strategies",
                    ],
                    priority="high" if abs(trend) > 0.1 else "medium",
                )

            return insight

        except Exception as e:
            self.logger.error(f"Failed to create trend insight: {e}")
            return None

    async def _analyze_performance(self, current_metrics: LearningMetrics) -> list[LearningInsight]:
        """Analyze current performance levels."""
        insights = []

        # Identify low-performing metrics
        performance_thresholds = {
            "pattern_effectiveness": 0.7,
            "failure_reduction_rate": 0.6,
            "recommendation_accuracy": 0.8,
            "cycle_efficiency": 0.6,
            "knowledge_growth_rate": 0.5,
            "memory_retention_score": 0.7,
        }

        for metric_name, threshold in performance_thresholds.items():
            current_value = getattr(current_metrics, metric_name, 0.0)

            if current_value < threshold:
                insight = self._create_performance_insight(metric_name, current_value, threshold)
                if insight:
                    insights.append(insight)

        return insights

    def _create_performance_insight(
        self, metric_name: str, current_value: float, threshold: float
    ) -> Optional[LearningInsight]:
        """Create insight for low performance."""
        try:
            gap = threshold - current_value

            improvement_actions = {
                "pattern_effectiveness": [
                    "Review pattern selection criteria",
                    "Improve pattern matching algorithms",
                    "Update patterns based on recent failures",
                ],
                "failure_reduction_rate": [
                    "Enhance failure analysis capabilities",
                    "Improve prevention rule generation",
                    "Increase proactive monitoring",
                ],
                "recommendation_accuracy": [
                    "Refine recommendation algorithms",
                    "Improve context analysis",
                    "Increase feedback collection",
                ],
                "cycle_efficiency": [
                    "Optimize evolution cycle workflows",
                    "Reduce unnecessary steps",
                    "Improve parallel processing",
                ],
                "knowledge_growth_rate": [
                    "Increase knowledge extraction frequency",
                    "Improve relationship discovery",
                    "Enhance data quality",
                ],
                "memory_retention_score": [
                    "Optimize memory retention policies",
                    "Improve cache strategies",
                    "Enhance memory relevance scoring",
                ],
            }

            insight = LearningInsight(
                id=f"insight_{hashlib.md5(f'perf_{metric_name}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}",
                type="performance_issue",
                title=f"Low {metric_name.replace('_', ' ').title()}",
                description=f"The {metric_name.replace('_', ' ')} is below target threshold. Current: {current_value:.1%}, Target: {threshold:.1%}, Gap: {gap:.1%}",
                impact=gap,
                confidence=0.8,
                supporting_data={
                    "metric": metric_name,
                    "current_value": current_value,
                    "threshold": threshold,
                    "gap": gap,
                },
                recommended_actions=improvement_actions.get(metric_name, []),
                priority="high" if gap > 0.2 else "medium",
            )

            return insight

        except Exception as e:
            self.logger.error(f"Failed to create performance insight: {e}")
            return None

    async def _identify_optimization_opportunities(
        self, current_metrics: LearningMetrics
    ) -> list[LearningInsight]:
        """Identify optimization opportunities."""
        insights = []

        # Look for imbalanced metrics that could be optimized
        overall_score = current_metrics.get_overall_score()

        metric_values = {
            "pattern_effectiveness": current_metrics.pattern_effectiveness,
            "failure_reduction_rate": current_metrics.failure_reduction_rate,
            "recommendation_accuracy": current_metrics.recommendation_accuracy,
            "cycle_efficiency": current_metrics.cycle_efficiency,
        }

        # Find the lowest performing metric
        min_metric = min(metric_values.items(), key=lambda x: x[1])
        max_metric = max(metric_values.items(), key=lambda x: x[1])

        if max_metric[1] - min_metric[1] > 0.3:  # Significant imbalance
            insight = LearningInsight(
                id=f"insight_{hashlib.md5(f'balance_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}",
                type="optimization_opportunity",
                title="Metric Imbalance Detected",
                description=f"There's a significant performance gap between {max_metric[0].replace('_', ' ')} ({max_metric[1]:.1%}) and {min_metric[0].replace('_', ' ')} ({min_metric[1]:.1%}). Focusing on the underperforming area could improve overall system effectiveness.",
                impact=0.8,
                confidence=0.7,
                supporting_data={
                    "high_metric": max_metric[0],
                    "high_value": max_metric[1],
                    "low_metric": min_metric[0],
                    "low_value": min_metric[1],
                    "gap": max_metric[1] - min_metric[1],
                },
                recommended_actions=[
                    f"Focus improvement efforts on {min_metric[0].replace('_', ' ')}",
                    "Reallocate resources from high-performing to low-performing areas",
                    "Investigate why this metric is underperforming",
                ],
                priority="medium",
            )

            insights.append(insight)

        return insights


class FeedbackLoop:
    """Main feedback loop system for continuous learning improvement.

    Monitors learning effectiveness, identifies opportunities for improvement,
    and automatically adjusts strategies to optimize performance.

    Example:
        >>> feedback_loop = FeedbackLoop(pattern_db, failure_analyzer, ...)
        >>> await feedback_loop.initialize()
        >>> metrics = await feedback_loop.measure_learning_effectiveness()
        >>> insights = await feedback_loop.generate_insights()
    """

    def __init__(
        self,
        pattern_db: PatternDatabase,
        failure_analyzer: FailureAnalyzer,
        memory_curator: MemoryCurator,
        knowledge_graph: KnowledgeGraph,
        recommendation_engine: RecommendationEngine,
    ):
        """Initialize feedback loop.

        Args:
            pattern_db: Pattern database
            failure_analyzer: Failure analyzer
            memory_curator: Memory curator
            knowledge_graph: Knowledge graph
            recommendation_engine: Recommendation engine
        """
        self.pattern_db = pattern_db
        self.failure_analyzer = failure_analyzer
        self.memory_curator = memory_curator
        self.knowledge_graph = knowledge_graph
        self.recommendation_engine = recommendation_engine

        self.metrics_calculator = MetricsCalculator()
        self.insight_generator = InsightGenerator()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Storage for metrics and insights
        self.metrics_history: deque = deque(maxlen=100)  # Keep last 100 measurements
        self.current_insights: list[LearningInsight] = []
        self.learning_objectives: list[LearningObjective] = [
            LearningObjective.IMPROVE_SUCCESS_RATE,
            LearningObjective.REDUCE_CYCLE_TIME,
            LearningObjective.MINIMIZE_FAILURES,
        ]

    async def initialize(self) -> None:
        """Initialize the feedback loop system."""
        # Take initial measurement
        initial_metrics = await self.measure_learning_effectiveness()
        self.metrics_history.append(initial_metrics)

        self.logger.info("Feedback loop initialized")

    async def measure_learning_effectiveness(self) -> LearningMetrics:
        """Measure current learning effectiveness across all metrics.

        Returns:
            Current learning metrics
        """
        try:
            timestamp = datetime.now()

            # Calculate all metrics in parallel for efficiency
            tasks = [
                self.metrics_calculator.calculate_pattern_effectiveness(self.pattern_db),
                self.metrics_calculator.calculate_failure_reduction_rate(self.failure_analyzer),
                self.metrics_calculator.calculate_recommendation_accuracy(
                    self.recommendation_engine
                ),
                self.metrics_calculator.calculate_cycle_efficiency(self.memory_curator),
                self.metrics_calculator.calculate_knowledge_growth_rate(self.knowledge_graph),
                self.metrics_calculator.calculate_memory_retention_score(self.memory_curator),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Extract results, using 0.0 for any failures
            pattern_effectiveness = results[0] if not isinstance(results[0], Exception) else 0.0
            failure_reduction_rate = results[1] if not isinstance(results[1], Exception) else 0.0
            recommendation_accuracy = results[2] if not isinstance(results[2], Exception) else 0.0
            cycle_efficiency = results[3] if not isinstance(results[3], Exception) else 0.0
            knowledge_growth_rate = results[4] if not isinstance(results[4], Exception) else 0.0
            memory_retention_score = results[5] if not isinstance(results[5], Exception) else 0.0

            # Calculate derived metrics
            system_performance_score = (
                await self.metrics_calculator.calculate_system_performance_score(
                    list(self.metrics_history)
                )
            )

            improvement_velocity = self._calculate_improvement_velocity()
            learning_velocity = self._calculate_learning_velocity()

            metrics = LearningMetrics(
                timestamp=timestamp,
                pattern_effectiveness=pattern_effectiveness,
                failure_reduction_rate=failure_reduction_rate,
                recommendation_accuracy=recommendation_accuracy,
                cycle_efficiency=cycle_efficiency,
                knowledge_growth_rate=knowledge_growth_rate,
                memory_retention_score=memory_retention_score,
                system_performance_score=system_performance_score,
                improvement_velocity=improvement_velocity,
                learning_velocity=learning_velocity,
            )

            # Store metrics
            self.metrics_history.append(metrics)

            # Store metrics in memory curator
            await self._store_metrics_memory(metrics)

            self.logger.info(
                f"Learning effectiveness measured: overall score {metrics.get_overall_score():.1%}"
            )
            return metrics

        except Exception as e:
            self.logger.error(f"Failed to measure learning effectiveness: {e}")
            # Return default metrics on failure
            return LearningMetrics(timestamp=datetime.now())

    def _calculate_improvement_velocity(self) -> float:
        """Calculate rate of improvement over time."""
        if len(self.metrics_history) < 2:
            return 0.0

        recent_scores = [m.get_overall_score() for m in list(self.metrics_history)[-10:]]

        if len(recent_scores) < 2:
            return 0.0

        # Calculate average improvement per measurement
        improvements = []
        for i in range(1, len(recent_scores)):
            improvement = recent_scores[i] - recent_scores[i - 1]
            improvements.append(improvement)

        return statistics.mean(improvements) if improvements else 0.0

    def _calculate_learning_velocity(self) -> float:
        """Calculate how quickly the system is learning."""
        if len(self.metrics_history) < 3:
            return 0.0

        # Learning velocity is the rate at which metrics are improving
        recent_metrics = list(self.metrics_history)[-5:]

        velocity_factors = []

        for metric_name in [
            "pattern_effectiveness",
            "recommendation_accuracy",
            "knowledge_growth_rate",
        ]:
            values = [getattr(m, metric_name, 0.0) for m in recent_metrics]

            if len(values) >= 2:
                # Calculate acceleration (second derivative)
                deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
                if len(deltas) >= 2:
                    accelerations = [deltas[i] - deltas[i - 1] for i in range(1, len(deltas))]
                    avg_acceleration = statistics.mean(accelerations) if accelerations else 0.0
                    velocity_factors.append(max(0.0, avg_acceleration))

        return statistics.mean(velocity_factors) if velocity_factors else 0.0

    async def _store_metrics_memory(self, metrics: LearningMetrics) -> None:
        """Store metrics as memory for future analysis."""
        try:
            memory = Memory(
                id=f"memory_{hashlib.md5(f'metrics_{metrics.timestamp.isoformat()}'.encode()).hexdigest()[:8]}",
                type="learning_metrics",
                timestamp=metrics.timestamp,
                data=metrics.to_dict(),
                metadata={
                    "importance": 0.8,
                    "tags": ["metrics", "learning", "feedback"],
                    "retention_score": 0.9,
                },
            )

            await self.memory_curator.store_memory(memory)

        except Exception as e:
            self.logger.error(f"Failed to store metrics memory: {e}")

    async def generate_insights(self) -> list[LearningInsight]:
        """Generate insights based on current metrics and trends.

        Returns:
            List of learning insights
        """
        try:
            if not self.metrics_history:
                return []

            current_metrics = self.metrics_history[-1]
            historical_metrics = list(self.metrics_history)[:-1]

            insights = await self.insight_generator.generate_insights(
                historical_metrics, current_metrics
            )

            # Store insights
            self.current_insights = insights

            # Store insights as memories
            for insight in insights:
                await self._store_insight_memory(insight)

            self.logger.info(f"Generated {len(insights)} learning insights")
            return insights

        except Exception as e:
            self.logger.error(f"Failed to generate insights: {e}")
            return []

    async def _store_insight_memory(self, insight: LearningInsight) -> None:
        """Store insight as memory."""
        try:
            memory = Memory(
                id=f"memory_{insight.id}",
                type="learning_insight",
                timestamp=insight.created_at,
                data=insight.to_dict(),
                metadata={
                    "importance": insight.impact,
                    "tags": ["insight", "learning", insight.type],
                    "retention_score": insight.confidence,
                },
            )

            await self.memory_curator.store_memory(memory)

        except Exception as e:
            self.logger.error(f"Failed to store insight memory: {e}")

    async def optimize_learning_strategies(self) -> list[str]:
        """Optimize learning strategies based on insights.

        Returns:
            List of optimization actions taken
        """
        try:
            actions_taken = []

            # Get current insights
            if not self.current_insights:
                self.current_insights = await self.generate_insights()

            # Prioritize insights by impact and confidence
            prioritized_insights = sorted(
                self.current_insights, key=lambda x: x.impact * x.confidence, reverse=True
            )

            # Apply optimization actions
            for insight in prioritized_insights[:5]:  # Top 5 insights
                optimization_actions = await self._apply_insight_optimizations(insight)
                actions_taken.extend(optimization_actions)

            self.logger.info(f"Applied {len(actions_taken)} optimization actions")
            return actions_taken

        except Exception as e:
            self.logger.error(f"Failed to optimize learning strategies: {e}")
            return []

    async def _apply_insight_optimizations(self, insight: LearningInsight) -> list[str]:
        """Apply optimizations based on an insight."""
        actions_taken = []

        try:
            if insight.type == "negative_trend":
                # Handle negative trends
                if "pattern_effectiveness" in insight.supporting_data.get("metric", ""):
                    # Optimize pattern selection
                    await self._optimize_pattern_selection()
                    actions_taken.append("Optimized pattern selection criteria")

                elif "recommendation_accuracy" in insight.supporting_data.get("metric", ""):
                    # Improve recommendation algorithms
                    await self._tune_recommendation_algorithms()
                    actions_taken.append("Tuned recommendation algorithms")

            elif insight.type == "performance_issue":
                metric = insight.supporting_data.get("metric", "")

                if metric == "cycle_efficiency":
                    # Optimize cycle workflows
                    await self._optimize_cycle_workflows()
                    actions_taken.append("Optimized evolution cycle workflows")

                elif metric == "memory_retention_score":
                    # Improve memory retention policies
                    await self._optimize_memory_retention()
                    actions_taken.append("Optimized memory retention policies")

            elif insight.type == "optimization_opportunity":
                # Address metric imbalances
                low_metric = insight.supporting_data.get("low_metric", "")

                if low_metric:
                    await self._focus_improvement_efforts(low_metric)
                    actions_taken.append(f"Focused improvement on {low_metric}")

        except Exception as e:
            self.logger.error(f"Failed to apply insight optimizations: {e}")

        return actions_taken

    async def _optimize_pattern_selection(self) -> None:
        """Optimize pattern selection criteria."""
        # This would implement pattern selection optimization
        # For now, just log the action
        self.logger.info("Optimizing pattern selection criteria")

    async def _tune_recommendation_algorithms(self) -> None:
        """Tune recommendation algorithms."""
        # This would implement recommendation algorithm tuning
        self.logger.info("Tuning recommendation algorithms")

    async def _optimize_cycle_workflows(self) -> None:
        """Optimize evolution cycle workflows."""
        # This would implement cycle workflow optimization
        self.logger.info("Optimizing evolution cycle workflows")

    async def _optimize_memory_retention(self) -> None:
        """Optimize memory retention policies."""
        # This would implement memory retention optimization
        self.logger.info("Optimizing memory retention policies")

    async def _focus_improvement_efforts(self, metric: str) -> None:
        """Focus improvement efforts on specific metric."""
        self.logger.info(f"Focusing improvement efforts on {metric}")

    async def get_learning_dashboard(self) -> dict[str, Any]:
        """Get comprehensive learning dashboard data.

        Returns:
            Dashboard data dictionary
        """
        try:
            if not self.metrics_history:
                current_metrics = await self.measure_learning_effectiveness()
            else:
                current_metrics = self.metrics_history[-1]

            if not self.current_insights:
                self.current_insights = await self.generate_insights()

            dashboard = {
                "current_metrics": current_metrics.to_dict(),
                "overall_score": current_metrics.get_overall_score(),
                "metrics_trend": self._calculate_metrics_trend(),
                "active_insights": [insight.to_dict() for insight in self.current_insights],
                "learning_objectives_progress": await self._calculate_objectives_progress(),
                "improvement_velocity": current_metrics.improvement_velocity,
                "learning_velocity": current_metrics.learning_velocity,
                "recommendations": await self._get_improvement_recommendations(),
                "metrics_history_summary": self._get_metrics_history_summary(),
            }

            return dashboard

        except Exception as e:
            self.logger.error(f"Failed to get learning dashboard: {e}")
            return {"error": str(e)}

    def _calculate_metrics_trend(self) -> dict[str, float]:
        """Calculate trend for each metric."""
        if len(self.metrics_history) < 2:
            return {}

        trends = {}
        metrics_names = [
            "pattern_effectiveness",
            "failure_reduction_rate",
            "recommendation_accuracy",
            "cycle_efficiency",
            "knowledge_growth_rate",
            "memory_retention_score",
        ]

        for metric_name in metrics_names:
            values = [getattr(m, metric_name, 0.0) for m in self.metrics_history]

            if len(values) >= 2:
                # Simple trend calculation (recent vs. older average)
                recent_avg = statistics.mean(values[-3:]) if len(values) >= 3 else values[-1]
                older_avg = statistics.mean(values[:-3]) if len(values) >= 6 else values[0]

                if older_avg > 0:
                    trend = (recent_avg - older_avg) / older_avg
                else:
                    trend = 0.0

                trends[metric_name] = trend

        return trends

    async def _calculate_objectives_progress(self) -> dict[str, float]:
        """Calculate progress towards learning objectives."""
        progress = {}

        if not self.metrics_history:
            return progress

        current_metrics = self.metrics_history[-1]

        # Map objectives to metrics
        objective_metrics = {
            LearningObjective.IMPROVE_SUCCESS_RATE: "pattern_effectiveness",
            LearningObjective.REDUCE_CYCLE_TIME: "cycle_efficiency",
            LearningObjective.MINIMIZE_FAILURES: "failure_reduction_rate",
            LearningObjective.INCREASE_CODE_QUALITY: "pattern_effectiveness",
            LearningObjective.ENHANCE_SECURITY: "failure_reduction_rate",
            LearningObjective.BOOST_PERFORMANCE: "cycle_efficiency",
        }

        for objective in self.learning_objectives:
            metric_name = objective_metrics.get(objective)
            if metric_name:
                metric_value = getattr(current_metrics, metric_name, 0.0)
                progress[objective.value] = metric_value

        return progress

    async def _get_improvement_recommendations(self) -> list[str]:
        """Get recommendations for improving learning effectiveness."""
        recommendations = []

        if not self.current_insights:
            return recommendations

        # Extract recommended actions from insights
        for insight in self.current_insights[:3]:  # Top 3 insights
            recommendations.extend(insight.recommended_actions)

        return recommendations

    def _get_metrics_history_summary(self) -> dict[str, Any]:
        """Get summary of metrics history."""
        if not self.metrics_history:
            return {}

        overall_scores = [m.get_overall_score() for m in self.metrics_history]

        return {
            "measurements_count": len(self.metrics_history),
            "current_score": overall_scores[-1] if overall_scores else 0.0,
            "average_score": statistics.mean(overall_scores) if overall_scores else 0.0,
            "best_score": max(overall_scores) if overall_scores else 0.0,
            "worst_score": min(overall_scores) if overall_scores else 0.0,
            "score_trend": overall_scores[-1] - overall_scores[0]
            if len(overall_scores) >= 2
            else 0.0,
        }
