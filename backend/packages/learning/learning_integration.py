"""
Learning Integration for T-Developer Planning Phase

This module integrates the learning system with the planning phase,
providing intelligent plan optimization based on learned patterns,
failure prevention, and continuous improvement feedback.

The LearningIntegration enhances planning by applying historical
knowledge to create more effective and efficient evolution plans.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from .failure_analyzer import FailureAnalyzer
from .feedback_loop import FeedbackLoop
from .knowledge_graph import KnowledgeGraph
from .memory_curator import Memory, MemoryCurator
from .pattern_database import PatternDatabase
from .pattern_recognition import PatternRecognizer
from .recommendation_engine import RecommendationEngine, RecommendationType

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT: int = 30
MIN_PATTERN_CONFIDENCE: float = 0.7


@dataclass
class PlanOptimization:
    """Plan optimization suggestion based on learning.

    Attributes:
        id: Unique optimization identifier
        type: Type of optimization (efficiency, quality, risk_reduction)
        description: Human-readable description
        impact: Estimated impact (0-1)
        confidence: Confidence in optimization (0-1)
        applicable_tasks: Task IDs this optimization applies to
        modifications: Specific modifications to make
        reasoning: Why this optimization is recommended
        evidence: Supporting evidence from learning system
    """

    id: str
    type: str
    description: str
    impact: float
    confidence: float
    applicable_tasks: list[str]
    modifications: dict[str, Any]
    reasoning: str
    evidence: list[str]


@dataclass
class RiskAssessment:
    """Risk assessment for plan tasks based on failure history.

    Attributes:
        task_id: Task identifier
        risk_level: Risk level (low, medium, high, critical)
        risk_score: Numeric risk score (0-1)
        failure_modes: Potential failure modes
        mitigation_strategies: Suggested mitigation strategies
        prevention_patterns: Patterns that can prevent failures
    """

    task_id: str
    risk_level: str
    risk_score: float
    failure_modes: list[str]
    mitigation_strategies: list[str]
    prevention_patterns: list[str]


@dataclass
class EfficiencyInsight:
    """Efficiency insight based on historical performance.

    Attributes:
        task_type: Type of task
        average_duration: Average historical duration
        efficiency_factors: Factors that improve efficiency
        bottlenecks: Common bottlenecks
        optimization_opportunities: Specific optimization opportunities
    """

    task_type: str
    average_duration: float
    efficiency_factors: list[str]
    bottlenecks: list[str]
    optimization_opportunities: list[str]


class PlanAnalyzer:
    """Analyzes plans using learning system knowledge."""

    def __init__(
        self,
        pattern_db: PatternDatabase,
        failure_analyzer: FailureAnalyzer,
        memory_curator: MemoryCurator,
    ):
        """Initialize plan analyzer.

        Args:
            pattern_db: Pattern database
            failure_analyzer: Failure analyzer
            memory_curator: Memory curator
        """
        self.pattern_db = pattern_db
        self.failure_analyzer = failure_analyzer
        self.memory_curator = memory_curator
        self.logger = logging.getLogger(self.__class__.__name__)

    async def analyze_plan_efficiency(self, plan_data: dict[str, Any]) -> list[EfficiencyInsight]:
        """Analyze plan efficiency based on historical data.

        Args:
            plan_data: Plan data to analyze

        Returns:
            List of efficiency insights
        """
        try:
            insights = []
            tasks = plan_data.get("tasks", [])

            # Group tasks by type
            task_types = self._group_tasks_by_type(tasks)

            for task_type, type_tasks in task_types.items():
                insight = await self._analyze_task_type_efficiency(task_type, type_tasks)
                if insight:
                    insights.append(insight)

            return insights

        except Exception as e:
            self.logger.error(f"Failed to analyze plan efficiency: {e}")
            return []

    def _group_tasks_by_type(self, tasks: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Group tasks by type/category."""
        groups = {}

        for task in tasks:
            task_type = task.get("category", "unknown")
            if task_type not in groups:
                groups[task_type] = []
            groups[task_type].append(task)

        return groups

    async def _analyze_task_type_efficiency(
        self, task_type: str, tasks: list[dict[str, Any]]
    ) -> Optional[EfficiencyInsight]:
        """Analyze efficiency for a specific task type."""
        try:
            # Get historical data for this task type
            historical_memories = await self.memory_curator.search_memories(
                {"type": "evolution_cycle", "tags": [task_type]}
            )

            if not historical_memories:
                return None

            # Calculate average duration
            durations = []
            success_factors = []
            bottleneck_indicators = []

            for memory in historical_memories:
                cycle_data = memory.data
                duration = cycle_data.get("duration", 0)
                success = cycle_data.get("success", False)

                if duration > 0:
                    durations.append(duration)

                if success:
                    # Identify success factors
                    if duration < 60:  # Fast execution
                        success_factors.append("fast_execution")
                    if cycle_data.get("patterns_used"):
                        success_factors.append("pattern_usage")
                else:
                    # Identify bottlenecks
                    if duration > 300:  # Slow execution
                        bottleneck_indicators.append("slow_execution")
                    error_msg = cycle_data.get("error_message", "")
                    if "timeout" in error_msg.lower():
                        bottleneck_indicators.append("timeout_issues")

            if not durations:
                return None

            # Calculate statistics
            avg_duration = sum(durations) / len(durations)
            common_success_factors = self._find_common_items(success_factors)
            common_bottlenecks = self._find_common_items(bottleneck_indicators)

            # Generate optimization opportunities
            optimizations = []
            if avg_duration > 120:  # Over 2 minutes
                optimizations.append("Consider breaking into smaller subtasks")
            if "timeout_issues" in common_bottlenecks:
                optimizations.append("Implement timeout handling and retry logic")
            if "pattern_usage" in common_success_factors:
                optimizations.append("Apply proven patterns for this task type")

            insight = EfficiencyInsight(
                task_type=task_type,
                average_duration=avg_duration,
                efficiency_factors=common_success_factors,
                bottlenecks=common_bottlenecks,
                optimization_opportunities=optimizations,
            )

            return insight

        except Exception as e:
            self.logger.error(f"Failed to analyze task type efficiency: {e}")
            return None

    def _find_common_items(self, items: list[str]) -> list[str]:
        """Find commonly occurring items in a list."""
        if not items:
            return []

        item_counts = {}
        for item in items:
            item_counts[item] = item_counts.get(item, 0) + 1

        # Return items that appear in at least 20% of cases
        threshold = max(1, len(items) * 0.2)
        common_items = [item for item, count in item_counts.items() if count >= threshold]

        return common_items

    async def assess_plan_risks(self, plan_data: dict[str, Any]) -> list[RiskAssessment]:
        """Assess risks for plan tasks based on failure history.

        Args:
            plan_data: Plan data to assess

        Returns:
            List of risk assessments
        """
        try:
            assessments = []
            tasks = plan_data.get("tasks", [])

            # Get failure patterns
            failure_stats = await self.failure_analyzer.get_failure_statistics()

            for task in tasks:
                assessment = await self._assess_task_risk(task, failure_stats)
                if assessment:
                    assessments.append(assessment)

            return assessments

        except Exception as e:
            self.logger.error(f"Failed to assess plan risks: {e}")
            return []

    async def _assess_task_risk(
        self, task: dict[str, Any], failure_stats: dict[str, Any]
    ) -> Optional[RiskAssessment]:
        """Assess risk for a specific task."""
        try:
            task_id = task.get("id", "")
            task_category = task.get("category", "unknown")
            task_name = task.get("name", "").lower()

            # Calculate base risk score
            risk_score = 0.0
            failure_modes = []
            mitigation_strategies = []

            # Check for high-risk keywords
            high_risk_keywords = ["deploy", "production", "database", "migration", "refactor"]
            medium_risk_keywords = ["test", "integration", "api", "security"]

            for keyword in high_risk_keywords:
                if keyword in task_name:
                    risk_score += 0.3
                    failure_modes.append(f"Risk associated with {keyword} operations")

            for keyword in medium_risk_keywords:
                if keyword in task_name:
                    risk_score += 0.2
                    failure_modes.append(f"Moderate risk for {keyword} tasks")

            # Check historical failure rates for this category
            category_failures = failure_stats.get("categories", {}).get(task_category, {})
            if category_failures:
                failure_frequency = category_failures.get("frequency", 0)
                if failure_frequency > 5:
                    risk_score += 0.4
                    failure_modes.append(f"High historical failure rate for {task_category}")
                elif failure_frequency > 2:
                    risk_score += 0.2
                    failure_modes.append(f"Moderate historical failure rate for {task_category}")

            # Determine risk level
            if risk_score >= 0.8:
                risk_level = "critical"
            elif risk_score >= 0.6:
                risk_level = "high"
            elif risk_score >= 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"

            # Generate mitigation strategies
            if risk_score > 0.5:
                mitigation_strategies.extend(
                    [
                        "Implement comprehensive testing before execution",
                        "Create rollback plan",
                        "Monitor execution closely",
                    ]
                )

            if "deploy" in task_name or "production" in task_name:
                mitigation_strategies.extend(
                    [
                        "Use blue-green deployment strategy",
                        "Implement canary releases",
                        "Prepare emergency rollback procedures",
                    ]
                )

            # Find applicable prevention patterns
            prevention_patterns = await self._find_prevention_patterns(task_category)

            assessment = RiskAssessment(
                task_id=task_id,
                risk_level=risk_level,
                risk_score=min(1.0, risk_score),
                failure_modes=failure_modes,
                mitigation_strategies=mitigation_strategies,
                prevention_patterns=prevention_patterns,
            )

            return assessment

        except Exception as e:
            self.logger.error(f"Failed to assess task risk: {e}")
            return None

    async def _find_prevention_patterns(self, task_category: str) -> list[str]:
        """Find patterns that can prevent failures for task category."""
        try:
            # Get patterns that improve reliability for this category
            patterns = await self.pattern_db.search_patterns(
                {"category": "fix", "min_success_rate": 0.8}  # Prevention patterns
            )

            applicable_patterns = []
            for pattern in patterns:
                # Check if pattern context matches task category
                context = pattern.context
                if task_category in str(context).lower() or any(
                    tag in context.get("tags", []) for tag in [task_category, "prevention"]
                ):
                    applicable_patterns.append(pattern.name)

            return applicable_patterns[:5]  # Return top 5

        except Exception as e:
            self.logger.error(f"Failed to find prevention patterns: {e}")
            return []


class PlanOptimizer:
    """Optimizes plans using learning system insights."""

    def __init__(
        self,
        pattern_recognizer: PatternRecognizer,
        recommendation_engine: RecommendationEngine,
        knowledge_graph: KnowledgeGraph,
    ):
        """Initialize plan optimizer.

        Args:
            pattern_recognizer: Pattern recognizer
            recommendation_engine: Recommendation engine
            knowledge_graph: Knowledge graph
        """
        self.pattern_recognizer = pattern_recognizer
        self.recommendation_engine = recommendation_engine
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger(self.__class__.__name__)

    async def optimize_plan(self, plan_data: dict[str, Any]) -> list[PlanOptimization]:
        """Generate plan optimizations based on learning.

        Args:
            plan_data: Plan data to optimize

        Returns:
            List of plan optimizations
        """
        try:
            optimizations = []

            # Get applicable patterns
            pattern_optimizations = await self._generate_pattern_optimizations(plan_data)
            optimizations.extend(pattern_optimizations)

            # Get recommendations
            recommendation_optimizations = await self._generate_recommendation_optimizations(
                plan_data
            )
            optimizations.extend(recommendation_optimizations)

            # Get knowledge graph insights
            knowledge_optimizations = await self._generate_knowledge_optimizations(plan_data)
            optimizations.extend(knowledge_optimizations)

            # Sort by impact and confidence
            optimizations.sort(key=lambda x: x.impact * x.confidence, reverse=True)

            return optimizations[:10]  # Return top 10 optimizations

        except Exception as e:
            self.logger.error(f"Failed to optimize plan: {e}")
            return []

    async def _generate_pattern_optimizations(
        self, plan_data: dict[str, Any]
    ) -> list[PlanOptimization]:
        """Generate optimizations based on applicable patterns."""
        optimizations = []

        try:
            tasks = plan_data.get("tasks", [])

            for task in tasks:
                task_context = {
                    "category": task.get("category"),
                    "name": task.get("name", "").lower(),
                    "description": task.get("description", "").lower(),
                }

                # Find applicable patterns
                applicable_patterns = await self.pattern_recognizer.find_applicable_patterns(
                    task_context, limit=3
                )

                for pattern in applicable_patterns:
                    if pattern.confidence >= MIN_PATTERN_CONFIDENCE:
                        optimization = PlanOptimization(
                            id=f"pattern_opt_{pattern.id}_{task.get('id')}",
                            type="efficiency",
                            description=f"Apply {pattern.name} to improve {task.get('name')}",
                            impact=pattern.success_rate * 0.8,  # Moderate impact estimate
                            confidence=pattern.confidence,
                            applicable_tasks=[task.get("id")],
                            modifications={
                                "pattern_to_apply": pattern.id,
                                "suggested_changes": pattern.action,
                            },
                            reasoning=f"Pattern '{pattern.name}' has {pattern.success_rate:.1%} success rate and applies to this task type",
                            evidence=[
                                f"Success rate: {pattern.success_rate:.1%}",
                                f"Used {pattern.usage_count} times",
                                f"Confidence: {pattern.confidence:.1%}",
                            ],
                        )
                        optimizations.append(optimization)

        except Exception as e:
            self.logger.error(f"Failed to generate pattern optimizations: {e}")

        return optimizations

    async def _generate_recommendation_optimizations(
        self, plan_data: dict[str, Any]
    ) -> list[PlanOptimization]:
        """Generate optimizations based on recommendations."""
        optimizations = []

        try:
            # Get recommendations for plan context
            plan_context = {
                "phase": "planning",
                "task_count": len(plan_data.get("tasks", [])),
                "estimated_hours": sum(
                    task.get("estimated_hours", 0) for task in plan_data.get("tasks", [])
                ),
                "categories": list(
                    set(
                        task.get("category")
                        for task in plan_data.get("tasks", [])
                        if task.get("category")
                    )
                ),
            }

            recommendations = await self.recommendation_engine.get_recommendations(plan_context)

            for rec in recommendations[:5]:  # Top 5 recommendations
                if rec.type in [RecommendationType.OPTIMIZATION, RecommendationType.PERFORMANCE]:
                    optimization = PlanOptimization(
                        id=f"rec_opt_{rec.id}",
                        type="quality",
                        description=rec.title,
                        impact=rec.confidence * 0.7,
                        confidence=rec.confidence,
                        applicable_tasks=[],  # Apply to whole plan
                        modifications={
                            "recommendation": rec.action,
                            "expected_outcome": rec.expected_outcome,
                        },
                        reasoning=rec.reasoning,
                        evidence=rec.supporting_evidence,
                    )
                    optimizations.append(optimization)

        except Exception as e:
            self.logger.error(f"Failed to generate recommendation optimizations: {e}")

        return optimizations

    async def _generate_knowledge_optimizations(
        self, plan_data: dict[str, Any]
    ) -> list[PlanOptimization]:
        """Generate optimizations based on knowledge graph insights."""
        optimizations = []

        try:
            # Get knowledge graph statistics
            stats = await self.knowledge_graph.get_graph_statistics()

            if stats.get("total_nodes", 0) == 0:
                return optimizations

            # Look for optimization opportunities in the graph
            tasks = plan_data.get("tasks", [])

            for task in tasks:
                task_category = task.get("category", "unknown")

                # Query for related knowledge nodes
                query = {"node_criteria": {"type": "pattern", "min_importance": 0.7}, "limit": 5}

                related_nodes = await self.knowledge_graph.query_graph(query)

                for node in related_nodes:
                    if task_category.lower() in node.label.lower():
                        optimization = PlanOptimization(
                            id=f"knowledge_opt_{node.id}_{task.get('id')}",
                            type="knowledge_based",
                            description=f"Apply knowledge from {node.label} to {task.get('name')}",
                            impact=node.importance * 0.6,
                            confidence=0.7,  # Moderate confidence for knowledge-based optimizations
                            applicable_tasks=[task.get("id")],
                            modifications={
                                "knowledge_node": node.id,
                                "suggested_approach": node.properties,
                            },
                            reasoning="Knowledge graph contains relevant information for this task type",
                            evidence=[
                                f"Node importance: {node.importance:.1%}",
                                f"Related to {task_category} tasks",
                            ],
                        )
                        optimizations.append(optimization)

        except Exception as e:
            self.logger.error(f"Failed to generate knowledge optimizations: {e}")

        return optimizations


class LearningIntegration:
    """Main learning integration system for planning phase.

    Integrates all learning components to enhance planning with
    historical knowledge, pattern recognition, and intelligent optimization.

    Example:
        >>> integration = LearningIntegration(learning_components...)
        >>> await integration.initialize()
        >>> optimized_plan = await integration.enhance_plan(original_plan)
    """

    def __init__(
        self,
        pattern_recognizer: PatternRecognizer,
        failure_analyzer: FailureAnalyzer,
        memory_curator: MemoryCurator,
        knowledge_graph: KnowledgeGraph,
        recommendation_engine: RecommendationEngine,
        feedback_loop: FeedbackLoop,
    ):
        """Initialize learning integration.

        Args:
            pattern_recognizer: Pattern recognizer
            failure_analyzer: Failure analyzer
            memory_curator: Memory curator
            knowledge_graph: Knowledge graph
            recommendation_engine: Recommendation engine
            feedback_loop: Feedback loop
        """
        self.pattern_recognizer = pattern_recognizer
        self.failure_analyzer = failure_analyzer
        self.memory_curator = memory_curator
        self.knowledge_graph = knowledge_graph
        self.recommendation_engine = recommendation_engine
        self.feedback_loop = feedback_loop

        # Initialize sub-components
        self.plan_analyzer = PlanAnalyzer(
            pattern_recognizer.pattern_db, failure_analyzer, memory_curator
        )

        self.plan_optimizer = PlanOptimizer(
            pattern_recognizer, recommendation_engine, knowledge_graph
        )

        self.logger = logging.getLogger(self.__class__.__name__)

    async def initialize(self) -> None:
        """Initialize learning integration system."""
        self.logger.info("Learning integration initialized")

    async def enhance_plan(self, plan_data: dict[str, Any]) -> dict[str, Any]:
        """Enhance plan with learning-based optimizations.

        Args:
            plan_data: Original plan data

        Returns:
            Enhanced plan with learning optimizations
        """
        try:
            enhanced_plan = plan_data.copy()

            # Analyze plan efficiency
            efficiency_insights = await self.plan_analyzer.analyze_plan_efficiency(plan_data)

            # Assess plan risks
            risk_assessments = await self.plan_analyzer.assess_plan_risks(plan_data)

            # Generate optimizations
            optimizations = await self.plan_optimizer.optimize_plan(plan_data)

            # Apply high-impact optimizations
            enhanced_plan = await self._apply_optimizations(enhanced_plan, optimizations)

            # Add learning metadata
            enhanced_plan["learning_enhancements"] = {
                "efficiency_insights": [
                    self._insight_to_dict(insight) for insight in efficiency_insights
                ],
                "risk_assessments": [
                    self._assessment_to_dict(assessment) for assessment in risk_assessments
                ],
                "optimizations_applied": [
                    self._optimization_to_dict(opt) for opt in optimizations[:5]
                ],
                "enhancement_timestamp": datetime.now().isoformat(),
                "learning_confidence": self._calculate_enhancement_confidence(optimizations),
            }

            # Store enhanced plan as memory
            await self._store_plan_memory(enhanced_plan, optimizations)

            self.logger.info(f"Enhanced plan with {len(optimizations)} optimizations")
            return enhanced_plan

        except Exception as e:
            self.logger.error(f"Failed to enhance plan: {e}")
            return plan_data  # Return original plan on failure

    async def _apply_optimizations(
        self, plan_data: dict[str, Any], optimizations: list[PlanOptimization]
    ) -> dict[str, Any]:
        """Apply high-impact optimizations to the plan."""
        enhanced_plan = plan_data.copy()

        # Apply optimizations with high impact and confidence
        high_impact_optimizations = [
            opt for opt in optimizations if opt.impact * opt.confidence >= 0.6
        ]

        for optimization in high_impact_optimizations[:3]:  # Apply top 3
            try:
                enhanced_plan = await self._apply_single_optimization(enhanced_plan, optimization)
            except Exception as e:
                self.logger.error(f"Failed to apply optimization {optimization.id}: {e}")

        return enhanced_plan

    async def _apply_single_optimization(
        self, plan_data: dict[str, Any], optimization: PlanOptimization
    ) -> dict[str, Any]:
        """Apply a single optimization to the plan."""
        enhanced_plan = plan_data.copy()
        modifications = optimization.modifications

        if optimization.type == "efficiency":
            # Apply efficiency improvements
            if "pattern_to_apply" in modifications:
                enhanced_plan = await self._apply_pattern_optimization(enhanced_plan, optimization)

        elif optimization.type == "quality":
            # Apply quality improvements
            if "recommendation" in modifications:
                enhanced_plan = await self._apply_recommendation_optimization(
                    enhanced_plan, optimization
                )

        elif optimization.type == "knowledge_based":
            # Apply knowledge-based improvements
            enhanced_plan = await self._apply_knowledge_optimization(enhanced_plan, optimization)

        return enhanced_plan

    async def _apply_pattern_optimization(
        self, plan_data: dict[str, Any], optimization: PlanOptimization
    ) -> dict[str, Any]:
        """Apply pattern-based optimization."""
        enhanced_plan = plan_data.copy()

        # Find pattern details
        pattern_id = optimization.modifications.get("pattern_to_apply")
        if pattern_id:
            pattern = await self.pattern_recognizer.pattern_db.get_pattern(pattern_id)
            if pattern:
                # Apply pattern suggestions to applicable tasks
                tasks = enhanced_plan.get("tasks", [])
                for task in tasks:
                    if task.get("id") in optimization.applicable_tasks:
                        # Add pattern guidance to task
                        if "learning_guidance" not in task:
                            task["learning_guidance"] = {}
                        task["learning_guidance"]["pattern"] = {
                            "id": pattern.id,
                            "name": pattern.name,
                            "action": pattern.action,
                            "confidence": pattern.confidence,
                        }

        return enhanced_plan

    async def _apply_recommendation_optimization(
        self, plan_data: dict[str, Any], optimization: PlanOptimization
    ) -> dict[str, Any]:
        """Apply recommendation-based optimization."""
        enhanced_plan = plan_data.copy()

        # Add recommendation guidance to plan metadata
        if "learning_guidance" not in enhanced_plan:
            enhanced_plan["learning_guidance"] = {}

        enhanced_plan["learning_guidance"]["recommendations"] = enhanced_plan[
            "learning_guidance"
        ].get("recommendations", [])
        enhanced_plan["learning_guidance"]["recommendations"].append(
            {
                "optimization_id": optimization.id,
                "description": optimization.description,
                "action": optimization.modifications.get("recommendation", {}),
                "confidence": optimization.confidence,
            }
        )

        return enhanced_plan

    async def _apply_knowledge_optimization(
        self, plan_data: dict[str, Any], optimization: PlanOptimization
    ) -> dict[str, Any]:
        """Apply knowledge-based optimization."""
        enhanced_plan = plan_data.copy()

        # Add knowledge insights to applicable tasks
        tasks = enhanced_plan.get("tasks", [])
        for task in tasks:
            if task.get("id") in optimization.applicable_tasks:
                if "learning_guidance" not in task:
                    task["learning_guidance"] = {}
                task["learning_guidance"]["knowledge_insight"] = {
                    "node_id": optimization.modifications.get("knowledge_node"),
                    "suggested_approach": optimization.modifications.get("suggested_approach", {}),
                    "reasoning": optimization.reasoning,
                }

        return enhanced_plan

    def _calculate_enhancement_confidence(self, optimizations: list[PlanOptimization]) -> float:
        """Calculate overall confidence in plan enhancements."""
        if not optimizations:
            return 0.0

        # Weight by impact and average confidence
        weighted_confidence = sum(opt.impact * opt.confidence for opt in optimizations)
        total_weight = sum(opt.impact for opt in optimizations)

        if total_weight > 0:
            return weighted_confidence / total_weight
        else:
            return 0.0

    async def _store_plan_memory(
        self, enhanced_plan: dict[str, Any], optimizations: list[PlanOptimization]
    ) -> None:
        """Store enhanced plan as learning memory."""
        try:
            memory = Memory(
                id=f"memory_plan_{enhanced_plan.get('id', 'unknown')}",
                type="enhanced_plan",
                timestamp=datetime.now(),
                data={
                    "plan_id": enhanced_plan.get("id"),
                    "task_count": len(enhanced_plan.get("tasks", [])),
                    "estimated_hours": sum(
                        task.get("estimated_hours", 0) for task in enhanced_plan.get("tasks", [])
                    ),
                    "optimizations_count": len(optimizations),
                    "enhancement_confidence": self._calculate_enhancement_confidence(optimizations),
                },
                metadata={
                    "importance": 0.7,
                    "tags": ["planning", "enhancement", "learning"],
                    "retention_score": 0.8,
                },
            )

            await self.memory_curator.store_memory(memory)

        except Exception as e:
            self.logger.error(f"Failed to store plan memory: {e}")

    def _insight_to_dict(self, insight: EfficiencyInsight) -> dict[str, Any]:
        """Convert efficiency insight to dictionary."""
        return {
            "task_type": insight.task_type,
            "average_duration": insight.average_duration,
            "efficiency_factors": insight.efficiency_factors,
            "bottlenecks": insight.bottlenecks,
            "optimization_opportunities": insight.optimization_opportunities,
        }

    def _assessment_to_dict(self, assessment: RiskAssessment) -> dict[str, Any]:
        """Convert risk assessment to dictionary."""
        return {
            "task_id": assessment.task_id,
            "risk_level": assessment.risk_level,
            "risk_score": assessment.risk_score,
            "failure_modes": assessment.failure_modes,
            "mitigation_strategies": assessment.mitigation_strategies,
            "prevention_patterns": assessment.prevention_patterns,
        }

    def _optimization_to_dict(self, optimization: PlanOptimization) -> dict[str, Any]:
        """Convert plan optimization to dictionary."""
        return {
            "id": optimization.id,
            "type": optimization.type,
            "description": optimization.description,
            "impact": optimization.impact,
            "confidence": optimization.confidence,
            "applicable_tasks": optimization.applicable_tasks,
            "reasoning": optimization.reasoning,
            "evidence": optimization.evidence,
        }

    async def get_learning_insights(self, plan_data: dict[str, Any]) -> dict[str, Any]:
        """Get comprehensive learning insights for a plan.

        Args:
            plan_data: Plan data to analyze

        Returns:
            Dictionary containing learning insights
        """
        try:
            insights = {}

            # Get current learning metrics
            current_metrics = await self.feedback_loop.measure_learning_effectiveness()
            insights["learning_metrics"] = current_metrics.to_dict()

            # Get efficiency insights
            efficiency_insights = await self.plan_analyzer.analyze_plan_efficiency(plan_data)
            insights["efficiency_insights"] = [
                self._insight_to_dict(i) for i in efficiency_insights
            ]

            # Get risk assessments
            risk_assessments = await self.plan_analyzer.assess_plan_risks(plan_data)
            insights["risk_assessments"] = [self._assessment_to_dict(a) for a in risk_assessments]

            # Get applicable patterns
            plan_context = {
                "categories": list(
                    set(task.get("category") for task in plan_data.get("tasks", []))
                ),
                "estimated_duration": sum(
                    task.get("estimated_hours", 0) for task in plan_data.get("tasks", [])
                ),
            }

            patterns = await self.pattern_recognizer.find_applicable_patterns(plan_context)
            insights["applicable_patterns"] = [
                {
                    "id": p.id,
                    "name": p.name,
                    "category": p.category,
                    "success_rate": p.success_rate,
                    "confidence": p.confidence,
                }
                for p in patterns[:5]
            ]

            # Get recommendations
            recommendations = await self.recommendation_engine.get_recommendations(plan_context)
            insights["recommendations"] = [
                {
                    "id": r.id,
                    "title": r.title,
                    "type": r.type.value,
                    "priority": r.priority.value,
                    "confidence": r.confidence,
                }
                for r in recommendations[:5]
            ]

            return insights

        except Exception as e:
            self.logger.error(f"Failed to get learning insights: {e}")
            return {"error": str(e)}
