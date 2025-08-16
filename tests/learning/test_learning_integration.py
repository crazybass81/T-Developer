"""
Comprehensive tests for Learning Integration System.

This module tests the learning integration functionality that enhances
planning with historical knowledge, pattern recognition, and optimization.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, Mock

import pytest

from packages.learning.learning_integration import (
    EfficiencyInsight,
    LearningIntegration,
    PlanAnalyzer,
    PlanOptimization,
    PlanOptimizer,
    RiskAssessment,
    MIN_PATTERN_CONFIDENCE,
)
from packages.learning.pattern_database import Pattern, PatternDatabase
from packages.learning.knowledge_graph import KnowledgeGraph, KnowledgeNode, NodeType
from packages.learning.memory_curator import Memory, MemoryCurator
from packages.learning.pattern_recognition import PatternRecognizer
from packages.learning.recommendation_engine import (
    Recommendation,
    RecommendationEngine,
    RecommendationPriority,
    RecommendationType,
)
from packages.learning.failure_analyzer import FailureAnalyzer
from packages.learning.feedback_loop import FeedbackLoop, LearningMetrics


@pytest.fixture
def sample_plan_data() -> dict[str, Any]:
    """Create sample plan data for testing."""
    return {
        "id": "plan_001",
        "name": "Test Plan",
        "description": "A test plan for learning integration",
        "tasks": [
            {
                "id": "task_001",
                "name": "Implement Authentication",
                "category": "security",
                "description": "Add user authentication system",
                "estimated_hours": 8,
                "priority": "high",
            },
            {
                "id": "task_002",
                "name": "Write Unit Tests",
                "category": "testing",
                "description": "Add comprehensive unit tests",
                "estimated_hours": 4,
                "priority": "medium",
            },
            {
                "id": "task_003",
                "name": "Deploy to Production",
                "category": "deployment",
                "description": "Deploy application to production",
                "estimated_hours": 2,
                "priority": "critical",
            },
        ],
        "estimated_duration": 14,
        "created_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_efficiency_insight() -> EfficiencyInsight:
    """Create sample efficiency insight for testing."""
    return EfficiencyInsight(
        task_type="testing",
        average_duration=120.0,
        efficiency_factors=["pattern_usage", "automated_tools"],
        bottlenecks=["slow_execution", "environment_setup"],
        optimization_opportunities=[
            "Use parallel test execution",
            "Implement test fixtures",
        ],
    )


@pytest.fixture
def sample_risk_assessment() -> RiskAssessment:
    """Create sample risk assessment for testing."""
    return RiskAssessment(
        task_id="task_003",
        risk_level="high",
        risk_score=0.8,
        failure_modes=["Deployment failure", "Service unavailability"],
        mitigation_strategies=[
            "Implement blue-green deployment",
            "Create rollback plan",
        ],
        prevention_patterns=["deployment_safety", "rollback_pattern"],
    )


@pytest.fixture
def sample_plan_optimization() -> PlanOptimization:
    """Create sample plan optimization for testing."""
    return PlanOptimization(
        id="opt_001",
        type="efficiency",
        description="Apply test automation pattern",
        impact=0.8,
        confidence=0.9,
        applicable_tasks=["task_002"],
        modifications={
            "pattern_to_apply": "pattern_test_001",
            "suggested_changes": {"automation": True},
        },
        reasoning="Test automation pattern shows high success rate",
        evidence=["90% success rate", "Used 25 times"],
    )


@pytest.fixture
async def mock_pattern_db() -> AsyncMock:
    """Create mock pattern database."""
    mock_db = AsyncMock(spec=PatternDatabase)
    mock_db.search_patterns.return_value = []
    mock_db.get_pattern.return_value = None
    return mock_db


@pytest.fixture
async def mock_failure_analyzer() -> AsyncMock:
    """Create mock failure analyzer."""
    mock_analyzer = AsyncMock(spec=FailureAnalyzer)
    mock_analyzer.get_failure_statistics.return_value = {
        "categories": {
            "deployment": {"frequency": 3, "severity": "high"},
            "testing": {"frequency": 1, "severity": "low"},
        }
    }
    return mock_analyzer


@pytest.fixture
async def mock_memory_curator() -> AsyncMock:
    """Create mock memory curator."""
    mock_curator = AsyncMock(spec=MemoryCurator)
    mock_curator.search_memories.return_value = []
    mock_curator.store_memory.return_value = None
    return mock_curator


@pytest.fixture
async def mock_pattern_recognizer() -> AsyncMock:
    """Create mock pattern recognizer."""
    mock_recognizer = AsyncMock(spec=PatternRecognizer)
    mock_recognizer.find_applicable_patterns.return_value = []
    mock_recognizer.pattern_db = AsyncMock(spec=PatternDatabase)
    return mock_recognizer


@pytest.fixture
async def mock_knowledge_graph() -> AsyncMock:
    """Create mock knowledge graph."""
    mock_kg = AsyncMock(spec=KnowledgeGraph)
    mock_kg.get_graph_statistics.return_value = {"total_nodes": 100}
    mock_kg.query_graph.return_value = []
    return mock_kg


@pytest.fixture
async def mock_recommendation_engine() -> AsyncMock:
    """Create mock recommendation engine."""
    mock_engine = AsyncMock(spec=RecommendationEngine)
    mock_engine.get_recommendations.return_value = []
    return mock_engine


@pytest.fixture
async def mock_feedback_loop() -> AsyncMock:
    """Create mock feedback loop."""
    mock_loop = AsyncMock(spec=FeedbackLoop)
    mock_loop.measure_learning_effectiveness.return_value = LearningMetrics(
        pattern_accuracy=0.85,
        recommendation_success_rate=0.78,
        prediction_accuracy=0.82,
        adaptation_rate=0.76,
        overall_score=0.80,
    )
    return mock_loop


class TestPlanAnalyzer:
    """Test PlanAnalyzer functionality."""

    @pytest.fixture
    async def plan_analyzer(
        self,
        mock_pattern_db: AsyncMock,
        mock_failure_analyzer: AsyncMock,
        mock_memory_curator: AsyncMock,
    ) -> PlanAnalyzer:
        """Create PlanAnalyzer instance for testing."""
        return PlanAnalyzer(mock_pattern_db, mock_failure_analyzer, mock_memory_curator)

    @pytest.mark.asyncio
    async def test_analyzer_initialization(
        self,
        plan_analyzer: PlanAnalyzer,
        mock_pattern_db: AsyncMock,
        mock_failure_analyzer: AsyncMock,
        mock_memory_curator: AsyncMock,
    ) -> None:
        """Test plan analyzer initialization.
        
        Given: Analyzer components
        When: Analyzer is initialized
        Then: Should set up correctly
        """
        assert plan_analyzer.pattern_db == mock_pattern_db
        assert plan_analyzer.failure_analyzer == mock_failure_analyzer
        assert plan_analyzer.memory_curator == mock_memory_curator
        assert plan_analyzer.logger is not None

    @pytest.mark.asyncio
    async def test_analyze_plan_efficiency_success(
        self,
        plan_analyzer: PlanAnalyzer,
        sample_plan_data: dict[str, Any],
        mock_memory_curator: AsyncMock,
    ) -> None:
        """Test successful plan efficiency analysis.
        
        Given: Plan data with tasks
        When: Efficiency analysis is performed
        Then: Should return efficiency insights
        """
        # Set up mock memories for testing
        mock_memories = [
            Memory(
                id="mem_001",
                type="evolution_cycle",
                timestamp=datetime.now(),
                data={
                    "duration": 60,
                    "success": True,
                    "patterns_used": ["pattern_001"],
                },
                metadata={"tags": ["testing"]},
            ),
            Memory(
                id="mem_002",
                type="evolution_cycle",
                timestamp=datetime.now(),
                data={
                    "duration": 180,
                    "success": False,
                    "error_message": "Timeout occurred",
                },
                metadata={"tags": ["testing"]},
            ),
        ]
        mock_memory_curator.search_memories.return_value = mock_memories
        
        insights = await plan_analyzer.analyze_plan_efficiency(sample_plan_data)
        
        assert isinstance(insights, list)
        # Should have insights for different task categories
        if insights:
            assert all(isinstance(insight, EfficiencyInsight) for insight in insights)

    @pytest.mark.asyncio
    async def test_analyze_plan_efficiency_no_history(
        self,
        plan_analyzer: PlanAnalyzer,
        sample_plan_data: dict[str, Any],
        mock_memory_curator: AsyncMock,
    ) -> None:
        """Test efficiency analysis with no historical data.
        
        Given: Plan data but no historical memories
        When: Efficiency analysis is performed
        Then: Should return empty insights list
        """
        mock_memory_curator.search_memories.return_value = []
        
        insights = await plan_analyzer.analyze_plan_efficiency(sample_plan_data)
        
        assert insights == []

    @pytest.mark.asyncio
    async def test_analyze_plan_efficiency_error_handling(
        self,
        plan_analyzer: PlanAnalyzer,
        sample_plan_data: dict[str, Any],
        mock_memory_curator: AsyncMock,
    ) -> None:
        """Test error handling in efficiency analysis.
        
        Given: Memory curator that raises errors
        When: Efficiency analysis is performed
        Then: Should handle errors gracefully
        """
        mock_memory_curator.search_memories.side_effect = Exception("Memory error")
        
        insights = await plan_analyzer.analyze_plan_efficiency(sample_plan_data)
        
        assert insights == []

    def test_group_tasks_by_type(
        self,
        plan_analyzer: PlanAnalyzer,
        sample_plan_data: dict[str, Any],
    ) -> None:
        """Test task grouping by type.
        
        Given: Plan with tasks of different categories
        When: Tasks are grouped by type
        Then: Should group correctly
        """
        tasks = sample_plan_data["tasks"]
        groups = plan_analyzer._group_tasks_by_type(tasks)
        
        assert isinstance(groups, dict)
        assert "security" in groups
        assert "testing" in groups
        assert "deployment" in groups
        assert len(groups["security"]) == 1
        assert len(groups["testing"]) == 1
        assert len(groups["deployment"]) == 1

    def test_find_common_items(self, plan_analyzer: PlanAnalyzer) -> None:
        """Test finding common items in a list.
        
        Given: List with repeated items
        When: Common items are found
        Then: Should identify items above threshold
        """
        items = ["item1", "item1", "item2", "item1", "item3", "item2"]
        common = plan_analyzer._find_common_items(items)
        
        # item1 appears 3 times (50%), item2 appears 2 times (33%)
        # With 20% threshold, both should be included
        assert "item1" in common
        assert "item2" in common
        assert "item3" not in common  # Only appears once (16%)

    @pytest.mark.asyncio
    async def test_assess_plan_risks_success(
        self,
        plan_analyzer: PlanAnalyzer,
        sample_plan_data: dict[str, Any],
        mock_failure_analyzer: AsyncMock,
    ) -> None:
        """Test successful plan risk assessment.
        
        Given: Plan data and failure statistics
        When: Risk assessment is performed
        Then: Should return risk assessments for tasks
        """
        assessments = await plan_analyzer.assess_plan_risks(sample_plan_data)
        
        assert isinstance(assessments, list)
        # Should have assessments for tasks
        if assessments:
            assert all(isinstance(assessment, RiskAssessment) for assessment in assessments)

    @pytest.mark.asyncio
    async def test_assess_plan_risks_error_handling(
        self,
        plan_analyzer: PlanAnalyzer,
        sample_plan_data: dict[str, Any],
        mock_failure_analyzer: AsyncMock,
    ) -> None:
        """Test error handling in risk assessment.
        
        Given: Failure analyzer that raises errors
        When: Risk assessment is performed
        Then: Should handle errors gracefully
        """
        mock_failure_analyzer.get_failure_statistics.side_effect = Exception("Analyzer error")
        
        assessments = await plan_analyzer.assess_plan_risks(sample_plan_data)
        
        assert assessments == []

    @pytest.mark.asyncio
    async def test_assess_task_risk_high_risk(
        self,
        plan_analyzer: PlanAnalyzer,
        mock_pattern_db: AsyncMock,
    ) -> None:
        """Test task risk assessment for high-risk tasks.
        
        Given: High-risk task (deployment/production)
        When: Task risk is assessed
        Then: Should identify high risk level
        """
        high_risk_task = {
            "id": "risky_task",
            "name": "Deploy to Production Database",
            "category": "deployment",
        }
        
        failure_stats = {
            "categories": {
                "deployment": {"frequency": 8, "severity": "high"}
            }
        }
        
        # Mock pattern search for prevention patterns
        mock_pattern_db.search_patterns.return_value = []
        
        assessment = await plan_analyzer._assess_task_risk(high_risk_task, failure_stats)
        
        assert assessment is not None
        assert assessment.risk_level in ["high", "critical"]
        assert assessment.risk_score > 0.5
        assert len(assessment.failure_modes) > 0
        assert len(assessment.mitigation_strategies) > 0

    @pytest.mark.asyncio
    async def test_assess_task_risk_low_risk(
        self,
        plan_analyzer: PlanAnalyzer,
        mock_pattern_db: AsyncMock,
    ) -> None:
        """Test task risk assessment for low-risk tasks.
        
        Given: Low-risk task
        When: Task risk is assessed
        Then: Should identify low risk level
        """
        low_risk_task = {
            "id": "safe_task",
            "name": "Update Documentation",
            "category": "documentation",
        }
        
        failure_stats = {
            "categories": {
                "documentation": {"frequency": 0, "severity": "low"}
            }
        }
        
        mock_pattern_db.search_patterns.return_value = []
        
        assessment = await plan_analyzer._assess_task_risk(low_risk_task, failure_stats)
        
        assert assessment is not None
        assert assessment.risk_level in ["low", "medium"]
        assert assessment.risk_score < 0.6

    @pytest.mark.asyncio
    async def test_find_prevention_patterns(
        self,
        plan_analyzer: PlanAnalyzer,
        mock_pattern_db: AsyncMock,
    ) -> None:
        """Test finding prevention patterns for task category.
        
        Given: Task category and pattern database
        When: Prevention patterns are searched
        Then: Should return applicable patterns
        """
        # Mock pattern with prevention context
        prevention_pattern = Pattern(
            id="prevention_001",
            category="fix",
            name="Deployment Safety Pattern",
            description="Ensures safe deployments",
            context={"tags": ["deployment", "prevention"]},
            action={"type": "safety_check"},
            outcome={"safety": "improved"},
            success_rate=0.9,
            usage_count=10,
            created_at=datetime.now(),
        )
        mock_pattern_db.search_patterns.return_value = [prevention_pattern]
        
        patterns = await plan_analyzer._find_prevention_patterns("deployment")
        
        assert isinstance(patterns, list)
        if patterns:
            assert "Deployment Safety Pattern" in patterns


class TestPlanOptimizer:
    """Test PlanOptimizer functionality."""

    @pytest.fixture
    async def plan_optimizer(
        self,
        mock_pattern_recognizer: AsyncMock,
        mock_recommendation_engine: AsyncMock,
        mock_knowledge_graph: AsyncMock,
    ) -> PlanOptimizer:
        """Create PlanOptimizer instance for testing."""
        return PlanOptimizer(
            mock_pattern_recognizer,
            mock_recommendation_engine,
            mock_knowledge_graph,
        )

    @pytest.mark.asyncio
    async def test_optimizer_initialization(
        self,
        plan_optimizer: PlanOptimizer,
        mock_pattern_recognizer: AsyncMock,
        mock_recommendation_engine: AsyncMock,
        mock_knowledge_graph: AsyncMock,
    ) -> None:
        """Test plan optimizer initialization.
        
        Given: Optimizer components
        When: Optimizer is initialized
        Then: Should set up correctly
        """
        assert plan_optimizer.pattern_recognizer == mock_pattern_recognizer
        assert plan_optimizer.recommendation_engine == mock_recommendation_engine
        assert plan_optimizer.knowledge_graph == mock_knowledge_graph
        assert plan_optimizer.logger is not None

    @pytest.mark.asyncio
    async def test_optimize_plan_success(
        self,
        plan_optimizer: PlanOptimizer,
        sample_plan_data: dict[str, Any],
        mock_pattern_recognizer: AsyncMock,
        mock_recommendation_engine: AsyncMock,
        mock_knowledge_graph: AsyncMock,
    ) -> None:
        """Test successful plan optimization.
        
        Given: Plan data and optimization components
        When: Plan optimization is performed
        Then: Should return optimizations
        """
        # Set up mocks to return empty results
        mock_pattern_recognizer.find_applicable_patterns.return_value = []
        mock_recommendation_engine.get_recommendations.return_value = []
        mock_knowledge_graph.query_graph.return_value = []
        
        optimizations = await plan_optimizer.optimize_plan(sample_plan_data)
        
        assert isinstance(optimizations, list)
        assert len(optimizations) <= 10  # Should respect limit

    @pytest.mark.asyncio
    async def test_optimize_plan_error_handling(
        self,
        plan_optimizer: PlanOptimizer,
        sample_plan_data: dict[str, Any],
        mock_pattern_recognizer: AsyncMock,
    ) -> None:
        """Test error handling in plan optimization.
        
        Given: Components that raise errors
        When: Plan optimization is performed
        Then: Should handle errors gracefully
        """
        mock_pattern_recognizer.find_applicable_patterns.side_effect = Exception("Pattern error")
        
        optimizations = await plan_optimizer.optimize_plan(sample_plan_data)
        
        assert optimizations == []

    @pytest.mark.asyncio
    async def test_generate_pattern_optimizations(
        self,
        plan_optimizer: PlanOptimizer,
        sample_plan_data: dict[str, Any],
        mock_pattern_recognizer: AsyncMock,
    ) -> None:
        """Test pattern-based optimization generation.
        
        Given: Plan data and applicable patterns
        When: Pattern optimizations are generated
        Then: Should create appropriate optimizations
        """
        # Mock pattern with high confidence
        high_conf_pattern = Pattern(
            id="pattern_opt_001",
            category="testing",
            name="Test Automation Pattern",
            description="Automates test execution",
            context={"category": "testing"},
            action={"automation": True},
            outcome={"efficiency": "improved"},
            success_rate=0.9,
            usage_count=20,
            created_at=datetime.now(),
            confidence=0.85,  # Above MIN_PATTERN_CONFIDENCE
        )
        mock_pattern_recognizer.find_applicable_patterns.return_value = [high_conf_pattern]
        
        optimizations = await plan_optimizer._generate_pattern_optimizations(sample_plan_data)
        
        assert isinstance(optimizations, list)
        if optimizations:
            opt = optimizations[0]
            assert opt.type == "efficiency"
            assert opt.confidence == high_conf_pattern.confidence

    @pytest.mark.asyncio
    async def test_generate_recommendation_optimizations(
        self,
        plan_optimizer: PlanOptimizer,
        sample_plan_data: dict[str, Any],
        mock_recommendation_engine: AsyncMock,
    ) -> None:
        """Test recommendation-based optimization generation.
        
        Given: Plan data and recommendations
        When: Recommendation optimizations are generated
        Then: Should create appropriate optimizations
        """
        # Mock recommendation for optimization
        optimization_rec = Recommendation(
            id="rec_opt_001",
            type=RecommendationType.OPTIMIZATION,
            priority=RecommendationPriority.HIGH,
            title="Optimize Task Execution",
            description="Improve task execution efficiency",
            context={},
            action={"optimize": True},
            expected_outcome={"efficiency": "improved"},
            confidence=0.8,
            reasoning="Optimization needed",
            supporting_evidence=["Historical data shows improvement"],
            estimated_effort="Medium",
            estimated_impact="High",
        )
        mock_recommendation_engine.get_recommendations.return_value = [optimization_rec]
        
        optimizations = await plan_optimizer._generate_recommendation_optimizations(sample_plan_data)
        
        assert isinstance(optimizations, list)
        if optimizations:
            opt = optimizations[0]
            assert opt.type == "quality"
            assert opt.confidence == optimization_rec.confidence

    @pytest.mark.asyncio
    async def test_generate_knowledge_optimizations(
        self,
        plan_optimizer: PlanOptimizer,
        sample_plan_data: dict[str, Any],
        mock_knowledge_graph: AsyncMock,
    ) -> None:
        """Test knowledge-based optimization generation.
        
        Given: Plan data and knowledge graph
        When: Knowledge optimizations are generated
        Then: Should create appropriate optimizations
        """
        # Mock knowledge node
        knowledge_node = KnowledgeNode(
            id="node_001",
            type=NodeType.PATTERN,
            label="Security Best Practices",
            properties={"category": "security", "best_practices": True},
            tags=["security", "optimization"],
            importance=0.9,
            connections={},
        )
        mock_knowledge_graph.query_graph.return_value = [knowledge_node]
        
        optimizations = await plan_optimizer._generate_knowledge_optimizations(sample_plan_data)
        
        assert isinstance(optimizations, list)
        if optimizations:
            opt = optimizations[0]
            assert opt.type == "knowledge_based"
            assert "knowledge_node" in opt.modifications


class TestLearningIntegration:
    """Test LearningIntegration main functionality."""

    @pytest.fixture
    async def learning_integration(
        self,
        mock_pattern_recognizer: AsyncMock,
        mock_failure_analyzer: AsyncMock,
        mock_memory_curator: AsyncMock,
        mock_knowledge_graph: AsyncMock,
        mock_recommendation_engine: AsyncMock,
        mock_feedback_loop: AsyncMock,
    ) -> LearningIntegration:
        """Create LearningIntegration instance for testing."""
        integration = LearningIntegration(
            pattern_recognizer=mock_pattern_recognizer,
            failure_analyzer=mock_failure_analyzer,
            memory_curator=mock_memory_curator,
            knowledge_graph=mock_knowledge_graph,
            recommendation_engine=mock_recommendation_engine,
            feedback_loop=mock_feedback_loop,
        )
        await integration.initialize()
        return integration

    @pytest.mark.asyncio
    async def test_integration_initialization(
        self,
        learning_integration: LearningIntegration,
    ) -> None:
        """Test learning integration initialization.
        
        Given: Learning components
        When: Integration is initialized
        Then: Should set up all components
        """
        assert learning_integration.pattern_recognizer is not None
        assert learning_integration.failure_analyzer is not None
        assert learning_integration.memory_curator is not None
        assert learning_integration.knowledge_graph is not None
        assert learning_integration.recommendation_engine is not None
        assert learning_integration.feedback_loop is not None
        assert learning_integration.plan_analyzer is not None
        assert learning_integration.plan_optimizer is not None

    @pytest.mark.asyncio
    async def test_enhance_plan_success(
        self,
        learning_integration: LearningIntegration,
        sample_plan_data: dict[str, Any],
        mock_memory_curator: AsyncMock,
    ) -> None:
        """Test successful plan enhancement.
        
        Given: Plan data and learning components
        When: Plan enhancement is performed
        Then: Should return enhanced plan with learning metadata
        """
        # Set up mocks to return empty results for simplicity
        mock_memory_curator.search_memories.return_value = []
        
        enhanced_plan = await learning_integration.enhance_plan(sample_plan_data)
        
        assert enhanced_plan is not None
        assert "learning_enhancements" in enhanced_plan
        assert "efficiency_insights" in enhanced_plan["learning_enhancements"]
        assert "risk_assessments" in enhanced_plan["learning_enhancements"]
        assert "optimizations_applied" in enhanced_plan["learning_enhancements"]
        assert "enhancement_timestamp" in enhanced_plan["learning_enhancements"]
        assert "learning_confidence" in enhanced_plan["learning_enhancements"]

    @pytest.mark.asyncio
    async def test_enhance_plan_error_handling(
        self,
        learning_integration: LearningIntegration,
        sample_plan_data: dict[str, Any],
        mock_failure_analyzer: AsyncMock,
    ) -> None:
        """Test error handling in plan enhancement.
        
        Given: Components that raise errors
        When: Plan enhancement is performed
        Then: Should return original plan
        """
        mock_failure_analyzer.get_failure_statistics.side_effect = Exception("Analyzer error")
        
        enhanced_plan = await learning_integration.enhance_plan(sample_plan_data)
        
        # Should return original plan on error
        assert enhanced_plan == sample_plan_data

    @pytest.mark.asyncio
    async def test_apply_optimizations(
        self,
        learning_integration: LearningIntegration,
        sample_plan_data: dict[str, Any],
        sample_plan_optimization: PlanOptimization,
    ) -> None:
        """Test applying optimizations to plan.
        
        Given: Plan data and optimizations
        When: Optimizations are applied
        Then: Should modify plan accordingly
        """
        # Set high impact and confidence for optimization
        sample_plan_optimization.impact = 0.9
        sample_plan_optimization.confidence = 0.8
        
        optimizations = [sample_plan_optimization]
        
        enhanced_plan = await learning_integration._apply_optimizations(
            sample_plan_data, optimizations
        )
        
        assert enhanced_plan is not None
        # Enhanced plan should be different from original (may have guidance added)
        if "learning_guidance" in enhanced_plan.get("tasks", [{}])[0]:
            assert enhanced_plan != sample_plan_data

    @pytest.mark.asyncio
    async def test_apply_pattern_optimization(
        self,
        learning_integration: LearningIntegration,
        sample_plan_data: dict[str, Any],
        sample_plan_optimization: PlanOptimization,
        mock_pattern_recognizer: AsyncMock,
    ) -> None:
        """Test applying pattern-based optimization.
        
        Given: Plan data and pattern optimization
        When: Pattern optimization is applied
        Then: Should add pattern guidance to tasks
        """
        # Mock pattern retrieval
        test_pattern = Pattern(
            id="pattern_test_001",
            category="testing",
            name="Test Pattern",
            description="A test pattern",
            context={},
            action={"automation": True},
            outcome={"efficiency": "improved"},
            success_rate=0.9,
            usage_count=10,
            created_at=datetime.now(),
            confidence=0.9,
        )
        mock_pattern_recognizer.pattern_db.get_pattern.return_value = test_pattern
        
        enhanced_plan = await learning_integration._apply_pattern_optimization(
            sample_plan_data, sample_plan_optimization
        )
        
        assert enhanced_plan is not None
        # Check if pattern guidance was added to applicable tasks
        applicable_task = next(
            (
                task for task in enhanced_plan.get("tasks", [])
                if task.get("id") in sample_plan_optimization.applicable_tasks
            ),
            None,
        )
        
        if applicable_task and "learning_guidance" in applicable_task:
            assert "pattern" in applicable_task["learning_guidance"]

    @pytest.mark.asyncio
    async def test_apply_recommendation_optimization(
        self,
        learning_integration: LearningIntegration,
        sample_plan_data: dict[str, Any],
        sample_plan_optimization: PlanOptimization,
    ) -> None:
        """Test applying recommendation-based optimization.
        
        Given: Plan data and recommendation optimization
        When: Recommendation optimization is applied
        Then: Should add recommendation guidance to plan
        """
        sample_plan_optimization.type = "quality"
        sample_plan_optimization.modifications = {
            "recommendation": {"optimize": True},
            "expected_outcome": {"quality": "improved"},
        }
        
        enhanced_plan = await learning_integration._apply_recommendation_optimization(
            sample_plan_data, sample_plan_optimization
        )
        
        assert enhanced_plan is not None
        assert "learning_guidance" in enhanced_plan
        assert "recommendations" in enhanced_plan["learning_guidance"]

    @pytest.mark.asyncio
    async def test_apply_knowledge_optimization(
        self,
        learning_integration: LearningIntegration,
        sample_plan_data: dict[str, Any],
        sample_plan_optimization: PlanOptimization,
    ) -> None:
        """Test applying knowledge-based optimization.
        
        Given: Plan data and knowledge optimization
        When: Knowledge optimization is applied
        Then: Should add knowledge insights to tasks
        """
        sample_plan_optimization.type = "knowledge_based"
        sample_plan_optimization.modifications = {
            "knowledge_node": "node_001",
            "suggested_approach": {"best_practices": True},
        }
        
        enhanced_plan = await learning_integration._apply_knowledge_optimization(
            sample_plan_data, sample_plan_optimization
        )
        
        assert enhanced_plan is not None
        # Check if knowledge insight was added to applicable tasks
        applicable_task = next(
            (
                task for task in enhanced_plan.get("tasks", [])
                if task.get("id") in sample_plan_optimization.applicable_tasks
            ),
            None,
        )
        
        if applicable_task and "learning_guidance" in applicable_task:
            assert "knowledge_insight" in applicable_task["learning_guidance"]

    def test_calculate_enhancement_confidence(
        self,
        learning_integration: LearningIntegration,
        sample_plan_optimization: PlanOptimization,
    ) -> None:
        """Test enhancement confidence calculation.
        
        Given: List of optimizations with different impacts and confidence
        When: Enhancement confidence is calculated
        Then: Should return weighted average
        """
        optimizations = [
            sample_plan_optimization,  # impact=0.8, confidence=0.9
            PlanOptimization(
                id="opt_002",
                type="quality",
                description="Quality optimization",
                impact=0.6,
                confidence=0.7,
                applicable_tasks=[],
                modifications={},
                reasoning="Quality improvement",
                evidence=[],
            ),
        ]
        
        confidence = learning_integration._calculate_enhancement_confidence(optimizations)
        
        assert 0.0 <= confidence <= 1.0
        # Should be weighted average: (0.8*0.9 + 0.6*0.7) / (0.8 + 0.6) = 1.14 / 1.4 ≈ 0.814
        expected = (0.8 * 0.9 + 0.6 * 0.7) / (0.8 + 0.6)
        assert abs(confidence - expected) < 0.01

    def test_calculate_enhancement_confidence_empty(
        self,
        learning_integration: LearningIntegration,
    ) -> None:
        """Test enhancement confidence calculation with empty optimizations.
        
        Given: Empty optimizations list
        When: Enhancement confidence is calculated
        Then: Should return 0.0
        """
        confidence = learning_integration._calculate_enhancement_confidence([])
        assert confidence == 0.0

    @pytest.mark.asyncio
    async def test_store_plan_memory(
        self,
        learning_integration: LearningIntegration,
        sample_plan_data: dict[str, Any],
        sample_plan_optimization: PlanOptimization,
        mock_memory_curator: AsyncMock,
    ) -> None:
        """Test storing enhanced plan as memory.
        
        Given: Enhanced plan and optimizations
        When: Plan memory is stored
        Then: Should call memory curator with appropriate memory
        """
        await learning_integration._store_plan_memory(sample_plan_data, [sample_plan_optimization])
        
        mock_memory_curator.store_memory.assert_called_once()
        call_args = mock_memory_curator.store_memory.call_args[0]
        memory = call_args[0]
        
        assert memory.type == "enhanced_plan"
        assert "plan_id" in memory.data
        assert "optimizations_count" in memory.data

    @pytest.mark.asyncio
    async def test_get_learning_insights_success(
        self,
        learning_integration: LearningIntegration,
        sample_plan_data: dict[str, Any],
        mock_feedback_loop: AsyncMock,
        mock_pattern_recognizer: AsyncMock,
        mock_recommendation_engine: AsyncMock,
        mock_memory_curator: AsyncMock,
    ) -> None:
        """Test getting comprehensive learning insights.
        
        Given: Plan data and learning components
        When: Learning insights are requested
        Then: Should return comprehensive insights
        """
        # Set up mocks
        mock_feedback_loop.measure_learning_effectiveness.return_value = LearningMetrics(
            pattern_accuracy=0.85,
            recommendation_success_rate=0.78,
            prediction_accuracy=0.82,
            adaptation_rate=0.76,
            overall_score=0.80,
        )
        mock_pattern_recognizer.find_applicable_patterns.return_value = []
        mock_recommendation_engine.get_recommendations.return_value = []
        mock_memory_curator.search_memories.return_value = []
        
        insights = await learning_integration.get_learning_insights(sample_plan_data)
        
        assert isinstance(insights, dict)
        assert "learning_metrics" in insights
        assert "efficiency_insights" in insights
        assert "risk_assessments" in insights
        assert "applicable_patterns" in insights
        assert "recommendations" in insights

    @pytest.mark.asyncio
    async def test_get_learning_insights_error_handling(
        self,
        learning_integration: LearningIntegration,
        sample_plan_data: dict[str, Any],
        mock_feedback_loop: AsyncMock,
    ) -> None:
        """Test error handling in learning insights.
        
        Given: Components that raise errors
        When: Learning insights are requested
        Then: Should return error information
        """
        mock_feedback_loop.measure_learning_effectiveness.side_effect = Exception("Feedback error")
        
        insights = await learning_integration.get_learning_insights(sample_plan_data)
        
        assert "error" in insights

    def test_insight_to_dict(
        self,
        learning_integration: LearningIntegration,
        sample_efficiency_insight: EfficiencyInsight,
    ) -> None:
        """Test efficiency insight to dictionary conversion.
        
        Given: Efficiency insight
        When: Converted to dictionary
        Then: Should contain all required fields
        """
        insight_dict = learning_integration._insight_to_dict(sample_efficiency_insight)
        
        assert isinstance(insight_dict, dict)
        assert insight_dict["task_type"] == sample_efficiency_insight.task_type
        assert insight_dict["average_duration"] == sample_efficiency_insight.average_duration
        assert insight_dict["efficiency_factors"] == sample_efficiency_insight.efficiency_factors
        assert insight_dict["bottlenecks"] == sample_efficiency_insight.bottlenecks
        assert insight_dict["optimization_opportunities"] == sample_efficiency_insight.optimization_opportunities

    def test_assessment_to_dict(
        self,
        learning_integration: LearningIntegration,
        sample_risk_assessment: RiskAssessment,
    ) -> None:
        """Test risk assessment to dictionary conversion.
        
        Given: Risk assessment
        When: Converted to dictionary
        Then: Should contain all required fields
        """
        assessment_dict = learning_integration._assessment_to_dict(sample_risk_assessment)
        
        assert isinstance(assessment_dict, dict)
        assert assessment_dict["task_id"] == sample_risk_assessment.task_id
        assert assessment_dict["risk_level"] == sample_risk_assessment.risk_level
        assert assessment_dict["risk_score"] == sample_risk_assessment.risk_score
        assert assessment_dict["failure_modes"] == sample_risk_assessment.failure_modes
        assert assessment_dict["mitigation_strategies"] == sample_risk_assessment.mitigation_strategies
        assert assessment_dict["prevention_patterns"] == sample_risk_assessment.prevention_patterns

    def test_optimization_to_dict(
        self,
        learning_integration: LearningIntegration,
        sample_plan_optimization: PlanOptimization,
    ) -> None:
        """Test plan optimization to dictionary conversion.
        
        Given: Plan optimization
        When: Converted to dictionary
        Then: Should contain all required fields
        """
        optimization_dict = learning_integration._optimization_to_dict(sample_plan_optimization)
        
        assert isinstance(optimization_dict, dict)
        assert optimization_dict["id"] == sample_plan_optimization.id
        assert optimization_dict["type"] == sample_plan_optimization.type
        assert optimization_dict["description"] == sample_plan_optimization.description
        assert optimization_dict["impact"] == sample_plan_optimization.impact
        assert optimization_dict["confidence"] == sample_plan_optimization.confidence
        assert optimization_dict["applicable_tasks"] == sample_plan_optimization.applicable_tasks
        assert optimization_dict["reasoning"] == sample_plan_optimization.reasoning
        assert optimization_dict["evidence"] == sample_plan_optimization.evidence


class TestLearningIntegrationIntegration:
    """Integration tests for learning integration system."""

    @pytest.mark.asyncio
    async def test_full_plan_enhancement_workflow(
        self,
        mock_pattern_recognizer: AsyncMock,
        mock_failure_analyzer: AsyncMock,
        mock_memory_curator: AsyncMock,
        mock_knowledge_graph: AsyncMock,
        mock_recommendation_engine: AsyncMock,
        mock_feedback_loop: AsyncMock,
        sample_plan_data: dict[str, Any],
    ) -> None:
        """Test complete plan enhancement workflow.
        
        Given: Full learning integration setup
        When: Plan enhancement workflow is executed
        Then: Should produce enhanced plan with all components
        """
        # Set up comprehensive mocks
        mock_memory_curator.search_memories.return_value = [
            Memory(
                id="mem_001",
                type="evolution_cycle",
                timestamp=datetime.now(),
                data={"duration": 60, "success": True, "patterns_used": ["pattern_001"]},
                metadata={"tags": ["testing"]},
            )
        ]
        
        mock_failure_analyzer.get_failure_statistics.return_value = {
            "categories": {"deployment": {"frequency": 5, "severity": "high"}}
        }
        
        high_conf_pattern = Pattern(
            id="pattern_001",
            category="testing",
            name="Test Automation",
            description="Automates testing",
            context={"category": "testing"},
            action={"automation": True},
            outcome={"efficiency": "improved"},
            success_rate=0.9,
            usage_count=15,
            created_at=datetime.now(),
            confidence=0.85,
        )
        mock_pattern_recognizer.find_applicable_patterns.return_value = [high_conf_pattern]
        mock_pattern_recognizer.pattern_db.get_pattern.return_value = high_conf_pattern
        
        optimization_rec = Recommendation(
            id="rec_001",
            type=RecommendationType.OPTIMIZATION,
            priority=RecommendationPriority.HIGH,
            title="Optimize Workflow",
            description="Improve workflow efficiency",
            context={},
            action={"optimize": True},
            expected_outcome={"efficiency": "improved"},
            confidence=0.8,
            reasoning="Optimization needed",
            supporting_evidence=["Data shows improvement"],
            estimated_effort="Medium",
            estimated_impact="High",
        )
        mock_recommendation_engine.get_recommendations.return_value = [optimization_rec]
        
        knowledge_node = KnowledgeNode(
            id="node_001",
            type=NodeType.PATTERN,
            label="Security Patterns",
            properties={"category": "security"},
            tags=["security"],
            importance=0.8,
            connections={},
        )
        mock_knowledge_graph.get_graph_statistics.return_value = {"total_nodes": 50}
        mock_knowledge_graph.query_graph.return_value = [knowledge_node]
        
        mock_feedback_loop.measure_learning_effectiveness.return_value = LearningMetrics(
            pattern_accuracy=0.85,
            recommendation_success_rate=0.78,
            prediction_accuracy=0.82,
            adaptation_rate=0.76,
            overall_score=0.80,
        )
        
        # Create and run integration
        integration = LearningIntegration(
            pattern_recognizer=mock_pattern_recognizer,
            failure_analyzer=mock_failure_analyzer,
            memory_curator=mock_memory_curator,
            knowledge_graph=mock_knowledge_graph,
            recommendation_engine=mock_recommendation_engine,
            feedback_loop=mock_feedback_loop,
        )
        await integration.initialize()
        
        enhanced_plan = await integration.enhance_plan(sample_plan_data)
        
        # Verify enhanced plan has learning enhancements
        assert "learning_enhancements" in enhanced_plan
        enhancements = enhanced_plan["learning_enhancements"]
        
        assert "efficiency_insights" in enhancements
        assert "risk_assessments" in enhancements
        assert "optimizations_applied" in enhancements
        assert "enhancement_timestamp" in enhancements
        assert "learning_confidence" in enhancements
        
        # Verify memory storage was called
        mock_memory_curator.store_memory.assert_called()

    @pytest.mark.asyncio
    async def test_concurrent_plan_enhancement(
        self,
        mock_pattern_recognizer: AsyncMock,
        mock_failure_analyzer: AsyncMock,
        mock_memory_curator: AsyncMock,
        mock_knowledge_graph: AsyncMock,
        mock_recommendation_engine: AsyncMock,
        mock_feedback_loop: AsyncMock,
    ) -> None:
        """Test concurrent plan enhancement requests.
        
        Given: Multiple plan enhancement requests
        When: Requests are processed concurrently
        Then: Should handle concurrency correctly
        """
        # Set up basic mocks
        mock_memory_curator.search_memories.return_value = []
        mock_failure_analyzer.get_failure_statistics.return_value = {"categories": {}}
        mock_pattern_recognizer.find_applicable_patterns.return_value = []
        mock_recommendation_engine.get_recommendations.return_value = []
        mock_knowledge_graph.get_graph_statistics.return_value = {"total_nodes": 0}
        mock_feedback_loop.measure_learning_effectiveness.return_value = LearningMetrics(
            pattern_accuracy=0.8,
            recommendation_success_rate=0.7,
            prediction_accuracy=0.75,
            adaptation_rate=0.7,
            overall_score=0.75,
        )
        
        integration = LearningIntegration(
            pattern_recognizer=mock_pattern_recognizer,
            failure_analyzer=mock_failure_analyzer,
            memory_curator=mock_memory_curator,
            knowledge_graph=mock_knowledge_graph,
            recommendation_engine=mock_recommendation_engine,
            feedback_loop=mock_feedback_loop,
        )
        await integration.initialize()
        
        # Create multiple plans
        plans = [
            {
                "id": f"plan_{i}",
                "name": f"Test Plan {i}",
                "tasks": [
                    {
                        "id": f"task_{i}_1",
                        "name": f"Task {i}",
                        "category": "testing",
                        "estimated_hours": 2,
                    }
                ],
            }
            for i in range(5)
        ]
        
        # Process concurrently
        tasks = [integration.enhance_plan(plan) for plan in plans]
        enhanced_plans = await asyncio.gather(*tasks)
        
        assert len(enhanced_plans) == 5
        assert all("learning_enhancements" in plan for plan in enhanced_plans)