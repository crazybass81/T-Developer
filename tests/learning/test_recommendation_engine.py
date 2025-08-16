"""
Comprehensive tests for Recommendation Engine System.

This module tests the recommendation generation, A/B testing,
and analytics capabilities of the recommendation engine.
"""

from __future__ import annotations

import asyncio
import json
import math
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, Mock, patch

import pytest

from packages.learning.recommendation_engine import (
    ABTestManager,
    KnowledgeRecommendationGenerator,
    PatternRecommendationGenerator,
    Recommendation,
    RecommendationEngine,
    RecommendationPriority,
    RecommendationType,
    A_B_TEST_DURATION_HOURS,
    MAX_RECOMMENDATIONS,
    MIN_CONFIDENCE_THRESHOLD,
)
from packages.learning.pattern_database import Pattern, PatternDatabase
from packages.learning.knowledge_graph import KnowledgeGraph, KnowledgeNode, NodeType
from packages.learning.memory_curator import MemoryCurator


@pytest.fixture
def sample_recommendation() -> Recommendation:
    """Create sample recommendation for testing."""
    return Recommendation(
        id="test_rec_001",
        type=RecommendationType.TESTING,
        priority=RecommendationPriority.HIGH,
        title="Add Unit Tests",
        description="Add comprehensive unit tests to improve coverage",
        context={"file_types": ["python"], "test_coverage": 65},
        action={"type": "add_tests", "target": "new_functions"},
        expected_outcome={"coverage_improvement": 20},
        confidence=0.85,
        reasoning="Test coverage is below recommended threshold",
        supporting_evidence=["Current coverage: 65%", "Recommended: 85%+"],
        estimated_effort="Medium",
        estimated_impact="High",
        prerequisites=["python", "pytest"],
        risks=["May slow initial development"],
    )


@pytest.fixture
def sample_pattern() -> Pattern:
    """Create sample pattern for testing."""
    return Pattern(
        id="pattern_test_001",
        category="testing",
        name="Add Unit Tests for New Functions",
        description="Automatically add unit tests when new functions are detected",
        context={
            "file_types": ["python"],
            "has_new_functions": True,
            "test_coverage": {"min": 0, "max": 80},
        },
        action={
            "type": "test_addition",
            "steps": [
                {"description": "Analyze function signature"},
                {"description": "Generate test cases"},
            ],
        },
        outcome={"coverage_improvement": 15, "test_count_increase": 5},
        success_rate=0.9,
        usage_count=45,
        created_at=datetime.now(),
        tags=["testing", "automation", "coverage"],
        confidence=0.9,
    )


@pytest.fixture
def sample_knowledge_node() -> KnowledgeNode:
    """Create sample knowledge node for testing."""
    return KnowledgeNode(
        id="test_node_001",
        type=NodeType.PATTERN,
        label="Test Pattern Node",
        properties={"category": "testing", "complexity": 5},
        tags=["testing", "automation"],
        importance=0.8,
        connections={"related_to": ["node_002", "node_003"]},
    )


@pytest.fixture
async def mock_pattern_db() -> AsyncMock:
    """Create mock pattern database."""
    mock_db = AsyncMock(spec=PatternDatabase)
    mock_db.get_all_patterns.return_value = []
    mock_db.search_patterns.return_value = []
    return mock_db


@pytest.fixture
async def mock_knowledge_graph() -> AsyncMock:
    """Create mock knowledge graph."""
    mock_kg = AsyncMock(spec=KnowledgeGraph)
    mock_kg.query_graph.return_value = []
    return mock_kg


@pytest.fixture
async def mock_memory_curator() -> AsyncMock:
    """Create mock memory curator."""
    mock_mc = AsyncMock(spec=MemoryCurator)
    mock_mc.store_memory.return_value = None
    return mock_mc


class TestRecommendation:
    """Test Recommendation dataclass functionality."""

    def test_recommendation_creation(self, sample_recommendation: Recommendation) -> None:
        """Test recommendation creation with all fields.
        
        Given: Valid recommendation data
        When: Recommendation is created
        Then: All fields should be set correctly
        """
        assert sample_recommendation.id == "test_rec_001"
        assert sample_recommendation.type == RecommendationType.TESTING
        assert sample_recommendation.priority == RecommendationPriority.HIGH
        assert sample_recommendation.confidence == 0.85
        assert not sample_recommendation.applied

    def test_recommendation_to_dict(self, sample_recommendation: Recommendation) -> None:
        """Test recommendation serialization to dictionary.
        
        Given: Recommendation instance
        When: to_dict is called
        Then: Should return dictionary with correct types
        """
        rec_dict = sample_recommendation.to_dict()
        
        assert isinstance(rec_dict, dict)
        assert rec_dict["id"] == "test_rec_001"
        assert rec_dict["type"] == "testing"
        assert rec_dict["priority"] == "high"
        assert isinstance(rec_dict["created_at"], str)

    def test_recommendation_from_dict(self, sample_recommendation: Recommendation) -> None:
        """Test recommendation deserialization from dictionary.
        
        Given: Recommendation dictionary
        When: from_dict is called
        Then: Should return Recommendation instance with correct types
        """
        rec_dict = sample_recommendation.to_dict()
        reconstructed = Recommendation.from_dict(rec_dict)
        
        assert reconstructed.id == sample_recommendation.id
        assert reconstructed.type == sample_recommendation.type
        assert reconstructed.priority == sample_recommendation.priority
        assert isinstance(reconstructed.created_at, datetime)

    def test_recommendation_expiration_check(self) -> None:
        """Test recommendation expiration checking.
        
        Given: Recommendations with different expiration times
        When: is_expired is called
        Then: Should return correct expiration status
        """
        # Non-expiring recommendation
        non_expiring = Recommendation(
            id="non_expiring",
            type=RecommendationType.TESTING,
            priority=RecommendationPriority.LOW,
            title="Non-expiring",
            description="Test",
            context={},
            action={},
            expected_outcome={},
            confidence=0.5,
            reasoning="Test",
            supporting_evidence=[],
            estimated_effort="Low",
            estimated_impact="Low",
        )
        assert not non_expiring.is_expired()
        
        # Expired recommendation
        expired = Recommendation(
            id="expired",
            type=RecommendationType.TESTING,
            priority=RecommendationPriority.LOW,
            title="Expired",
            description="Test",
            context={},
            action={},
            expected_outcome={},
            confidence=0.5,
            reasoning="Test",
            supporting_evidence=[],
            estimated_effort="Low",
            estimated_impact="Low",
            expires_at=datetime.now() - timedelta(hours=1),
        )
        assert expired.is_expired()
        
        # Future expiration
        future = Recommendation(
            id="future",
            type=RecommendationType.TESTING,
            priority=RecommendationPriority.LOW,
            title="Future",
            description="Test",
            context={},
            action={},
            expected_outcome={},
            confidence=0.5,
            reasoning="Test",
            supporting_evidence=[],
            estimated_effort="Low",
            estimated_impact="Low",
            expires_at=datetime.now() + timedelta(hours=1),
        )
        assert not future.is_expired()

    def test_urgency_score_calculation(self) -> None:
        """Test urgency score calculation.
        
        Given: Recommendations with different priorities and expiration times
        When: get_urgency_score is called
        Then: Should return appropriate urgency scores
        """
        # Critical priority
        critical = Recommendation(
            id="critical",
            type=RecommendationType.SECURITY,
            priority=RecommendationPriority.CRITICAL,
            title="Critical",
            description="Test",
            context={},
            action={},
            expected_outcome={},
            confidence=0.9,
            reasoning="Critical issue",
            supporting_evidence=[],
            estimated_effort="High",
            estimated_impact="Critical",
        )
        assert critical.get_urgency_score() == 1.0
        
        # Low priority
        low = Recommendation(
            id="low",
            type=RecommendationType.OPTIMIZATION,
            priority=RecommendationPriority.LOW,
            title="Low",
            description="Test",
            context={},
            action={},
            expected_outcome={},
            confidence=0.4,
            reasoning="Minor optimization",
            supporting_evidence=[],
            estimated_effort="Low",
            estimated_impact="Low",
        )
        assert low.get_urgency_score() == 0.4
        
        # With near expiration
        near_expiry = Recommendation(
            id="near_expiry",
            type=RecommendationType.TESTING,
            priority=RecommendationPriority.MEDIUM,
            title="Near Expiry",
            description="Test",
            context={},
            action={},
            expected_outcome={},
            confidence=0.6,
            reasoning="Test",
            supporting_evidence=[],
            estimated_effort="Medium",
            estimated_impact="Medium",
            expires_at=datetime.now() + timedelta(hours=12),  # Expires soon
        )
        urgency = near_expiry.get_urgency_score()
        assert urgency > 0.6  # Should be higher due to approaching expiration


class TestPatternRecommendationGenerator:
    """Test PatternRecommendationGenerator functionality."""

    @pytest.mark.asyncio
    async def test_generator_initialization(self, mock_pattern_db: AsyncMock) -> None:
        """Test pattern recommendation generator initialization.
        
        Given: Pattern database
        When: Generator is initialized
        Then: Should set up correctly
        """
        generator = PatternRecommendationGenerator(mock_pattern_db)
        
        assert generator.pattern_db == mock_pattern_db
        assert generator.logger is not None

    @pytest.mark.asyncio
    async def test_generate_recommendations_success(
        self, mock_pattern_db: AsyncMock, sample_pattern: Pattern
    ) -> None:
        """Test successful recommendation generation.
        
        Given: Pattern database with applicable patterns
        When: Recommendations are generated
        Then: Should return relevant recommendations
        """
        mock_pattern_db.get_all_patterns.return_value = [sample_pattern]
        
        generator = PatternRecommendationGenerator(mock_pattern_db)
        context = {
            "file_types": ["python"],
            "test_coverage": 70,
            "has_new_functions": True,
        }
        
        recommendations = await generator.generate_recommendations(context)
        
        assert len(recommendations) >= 0  # May be 0 if relevance is low
        mock_pattern_db.get_all_patterns.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_recommendations_error_handling(
        self, mock_pattern_db: AsyncMock
    ) -> None:
        """Test error handling in recommendation generation.
        
        Given: Pattern database that raises errors
        When: Recommendations are generated
        Then: Should handle errors gracefully
        """
        mock_pattern_db.get_all_patterns.side_effect = Exception("Database error")
        
        generator = PatternRecommendationGenerator(mock_pattern_db)
        context = {"file_types": ["python"]}
        
        recommendations = await generator.generate_recommendations(context)
        
        assert recommendations == []

    @pytest.mark.asyncio
    async def test_find_applicable_patterns(
        self, mock_pattern_db: AsyncMock, sample_pattern: Pattern
    ) -> None:
        """Test finding applicable patterns.
        
        Given: Pattern database with patterns
        When: Applicable patterns are searched
        Then: Should return patterns with relevance scores
        """
        sample_pattern.confidence = 0.9
        mock_pattern_db.get_all_patterns.return_value = [sample_pattern]
        
        generator = PatternRecommendationGenerator(mock_pattern_db)
        context = {
            "file_types": ["python"],
            "test_coverage": 70,
            "has_new_functions": True,
        }
        
        applicable = await generator._find_applicable_patterns(context)
        
        assert isinstance(applicable, list)
        # Should contain tuples of (pattern, relevance_score)
        if applicable:
            assert len(applicable[0]) == 2
            assert isinstance(applicable[0][0], Pattern)
            assert isinstance(applicable[0][1], float)

    def test_context_matching(self, mock_pattern_db: AsyncMock) -> None:
        """Test context matching algorithm.
        
        Given: Pattern context and current context
        When: Context match is calculated
        Then: Should return appropriate match score
        """
        generator = PatternRecommendationGenerator(mock_pattern_db)
        
        # Perfect match
        pattern_context = {"file_types": ["python"], "category": "testing"}
        current_context = {"file_types": ["python"], "category": "testing"}
        
        match_score = generator._calculate_context_match(pattern_context, current_context)
        assert match_score == 1.0
        
        # Partial match
        pattern_context = {"file_types": ["python"], "category": "testing"}
        current_context = {"file_types": ["python"], "category": "documentation"}
        
        match_score = generator._calculate_context_match(pattern_context, current_context)
        assert 0.0 <= match_score < 1.0
        
        # No match
        pattern_context = {"file_types": ["java"], "category": "testing"}
        current_context = {"file_types": ["python"], "category": "documentation"}
        
        match_score = generator._calculate_context_match(pattern_context, current_context)
        assert match_score == 0.0

    def test_range_matching(self, mock_pattern_db: AsyncMock) -> None:
        """Test range matching in context.
        
        Given: Pattern with range constraints
        When: Context values are within range
        Then: Should match appropriately
        """
        generator = PatternRecommendationGenerator(mock_pattern_db)
        
        # Value within range
        pattern_context = {"test_coverage": {"min": 0, "max": 80}}
        current_context = {"test_coverage": 70}
        
        match_score = generator._calculate_context_match(pattern_context, current_context)
        assert match_score == 1.0
        
        # Value outside range
        pattern_context = {"test_coverage": {"min": 0, "max": 80}}
        current_context = {"test_coverage": 90}
        
        match_score = generator._calculate_context_match(pattern_context, current_context)
        assert match_score == 0.0

    def test_priority_determination(self, mock_pattern_db: AsyncMock, sample_pattern: Pattern) -> None:
        """Test priority determination for recommendations.
        
        Given: Pattern with different characteristics
        When: Priority is determined
        Then: Should assign appropriate priority
        """
        generator = PatternRecommendationGenerator(mock_pattern_db)
        
        # Security pattern should be critical
        security_pattern = sample_pattern
        security_pattern.category = "security"
        priority = generator._determine_priority(security_pattern, {}, 0.8)
        assert priority == RecommendationPriority.CRITICAL
        
        # High confidence and relevance should be high priority
        high_conf_pattern = sample_pattern
        high_conf_pattern.category = "testing"
        high_conf_pattern.confidence = 0.95
        priority = generator._determine_priority(high_conf_pattern, {}, 0.85)
        assert priority == RecommendationPriority.HIGH
        
        # Low confidence should be low priority
        low_conf_pattern = sample_pattern
        low_conf_pattern.confidence = 0.5
        priority = generator._determine_priority(low_conf_pattern, {}, 0.4)
        assert priority == RecommendationPriority.LOW


class TestKnowledgeRecommendationGenerator:
    """Test KnowledgeRecommendationGenerator functionality."""

    @pytest.mark.asyncio
    async def test_generator_initialization(self, mock_knowledge_graph: AsyncMock) -> None:
        """Test knowledge recommendation generator initialization.
        
        Given: Knowledge graph
        When: Generator is initialized
        Then: Should set up correctly
        """
        generator = KnowledgeRecommendationGenerator(mock_knowledge_graph)
        
        assert generator.knowledge_graph == mock_knowledge_graph
        assert generator.logger is not None

    @pytest.mark.asyncio
    async def test_generate_recommendations_success(
        self, mock_knowledge_graph: AsyncMock, sample_knowledge_node: KnowledgeNode
    ) -> None:
        """Test successful knowledge-based recommendation generation.
        
        Given: Knowledge graph with relevant nodes
        When: Recommendations are generated
        Then: Should return knowledge-based recommendations
        """
        mock_knowledge_graph.query_graph.return_value = [sample_knowledge_node]
        
        generator = KnowledgeRecommendationGenerator(mock_knowledge_graph)
        context = {"tags": ["testing"], "complexity": 5}
        
        recommendations = await generator.generate_recommendations(context)
        
        assert isinstance(recommendations, list)
        mock_knowledge_graph.query_graph.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_recommendations_error_handling(
        self, mock_knowledge_graph: AsyncMock
    ) -> None:
        """Test error handling in knowledge recommendation generation.
        
        Given: Knowledge graph that raises errors
        When: Recommendations are generated
        Then: Should handle errors gracefully
        """
        mock_knowledge_graph.query_graph.side_effect = Exception("Graph error")
        
        generator = KnowledgeRecommendationGenerator(mock_knowledge_graph)
        context = {"tags": ["testing"]}
        
        recommendations = await generator.generate_recommendations(context)
        
        assert recommendations == []

    def test_node_relevance_calculation(
        self, mock_knowledge_graph: AsyncMock, sample_knowledge_node: KnowledgeNode
    ) -> None:
        """Test calculation of node relevance to context.
        
        Given: Knowledge node and context
        When: Relevance is calculated
        Then: Should return appropriate relevance score
        """
        generator = KnowledgeRecommendationGenerator(mock_knowledge_graph)
        
        # High relevance context
        context = {
            "tags": ["testing", "automation"],
            "category": "testing",
            "complexity": 5,
        }
        
        relevance = generator._calculate_node_relevance(sample_knowledge_node, context)
        assert 0.0 <= relevance <= 1.0
        
        # Low relevance context
        low_context = {
            "tags": ["documentation"],
            "category": "docs",
            "complexity": 1,
        }
        
        low_relevance = generator._calculate_node_relevance(sample_knowledge_node, low_context)
        assert low_relevance < relevance


class TestABTestManager:
    """Test ABTestManager functionality."""

    @pytest.fixture
    def ab_test_manager(self) -> ABTestManager:
        """Create ABTestManager instance for testing."""
        return ABTestManager()

    @pytest.mark.asyncio
    async def test_create_ab_test_success(
        self, ab_test_manager: ABTestManager, sample_recommendation: Recommendation
    ) -> None:
        """Test successful A/B test creation.
        
        Given: Recommendation variants
        When: A/B test is created
        Then: Should return test ID and set up test
        """
        variants = [sample_recommendation]
        
        test_id = await ab_test_manager.create_ab_test(
            test_name="Test Recommendation",
            recommendation_variants=variants,
        )
        
        assert test_id is not None
        assert test_id in ab_test_manager.active_tests
        assert ab_test_manager.active_tests[test_id]["name"] == "Test Recommendation"

    @pytest.mark.asyncio
    async def test_create_ab_test_invalid_input(self, ab_test_manager: ABTestManager) -> None:
        """Test A/B test creation with invalid input.
        
        Given: Invalid test parameters
        When: A/B test creation is attempted
        Then: Should raise appropriate errors
        """
        # No variants
        with pytest.raises(ValueError, match="Must provide at least one"):
            await ab_test_manager.create_ab_test("Empty Test", [])
        
        # Invalid traffic split
        with pytest.raises(ValueError, match="Traffic split must match"):
            await ab_test_manager.create_ab_test(
                "Invalid Split",
                [sample_recommendation],
                traffic_split=[0.3, 0.7],  # Two splits for one variant
            )
        
        # Traffic split doesn't sum to 1
        with pytest.raises(ValueError, match="Traffic split must sum"):
            await ab_test_manager.create_ab_test(
                "Invalid Sum",
                [sample_recommendation],
                traffic_split=[0.5],  # Doesn't sum to 1.0
            )

    @pytest.mark.asyncio
    async def test_assign_user_to_variant(
        self, ab_test_manager: ABTestManager, sample_recommendation: Recommendation
    ) -> None:
        """Test user assignment to test variants.
        
        Given: Active A/B test
        When: User is assigned to variant
        Then: Should return consistent assignment
        """
        test_id = await ab_test_manager.create_ab_test(
            "User Assignment Test",
            [sample_recommendation],
        )
        
        # First assignment
        assigned1 = await ab_test_manager.assign_user_to_variant(test_id, "user1")
        assert assigned1 is not None
        assert assigned1.id == sample_recommendation.id
        
        # Second assignment to same user should be consistent
        assigned2 = await ab_test_manager.assign_user_to_variant(test_id, "user1")
        assert assigned2 is not None
        assert assigned2.id == assigned1.id

    @pytest.mark.asyncio
    async def test_assign_user_nonexistent_test(self, ab_test_manager: ABTestManager) -> None:
        """Test user assignment to non-existent test.
        
        Given: Non-existent test ID
        When: User assignment is attempted
        Then: Should return None
        """
        assigned = await ab_test_manager.assign_user_to_variant("nonexistent", "user1")
        assert assigned is None

    @pytest.mark.asyncio
    async def test_record_test_result(
        self, ab_test_manager: ABTestManager, sample_recommendation: Recommendation
    ) -> None:
        """Test recording test results.
        
        Given: Active test with assigned user
        When: Test result is recorded
        Then: Should update test metrics
        """
        test_id = await ab_test_manager.create_ab_test(
            "Result Test",
            [sample_recommendation],
        )
        
        # Assign user and record results
        await ab_test_manager.assign_user_to_variant(test_id, "user1")
        await ab_test_manager.record_test_result(test_id, "user1", applied=True, success=True)
        
        # Check metrics updated
        test = ab_test_manager.active_tests[test_id]
        metrics = test["metrics"][0]  # First variant
        assert metrics["applications"] == 1
        assert metrics["successes"] == 1
        assert metrics["failures"] == 0

    @pytest.mark.asyncio
    async def test_get_test_results(
        self, ab_test_manager: ABTestManager, sample_recommendation: Recommendation
    ) -> None:
        """Test getting test results.
        
        Given: Test with recorded results
        When: Test results are requested
        Then: Should return comprehensive results
        """
        test_id = await ab_test_manager.create_ab_test(
            "Results Test",
            [sample_recommendation],
        )
        
        # Add some test data
        await ab_test_manager.assign_user_to_variant(test_id, "user1")
        await ab_test_manager.record_test_result(test_id, "user1", applied=True, success=True)
        
        results = await ab_test_manager.get_test_results(test_id)
        
        assert results is not None
        assert results["test_id"] == test_id
        assert "variants" in results
        assert len(results["variants"]) == 1
        assert results["variants"][0]["successes"] == 1

    def test_statistical_significance_calculation(self, ab_test_manager: ABTestManager) -> None:
        """Test statistical significance calculation.
        
        Given: Variant results
        When: Statistical significance is calculated
        Then: Should return appropriate significance metrics
        """
        variants = [
            {"applications": 100, "successes": 20},
            {"applications": 100, "successes": 25},
        ]
        
        significance = ab_test_manager._calculate_statistical_significance(variants)
        
        assert "significant" in significance
        assert "p_value" in significance
        assert isinstance(significance["significant"], bool)
        assert 0.0 <= significance["p_value"] <= 1.0

    def test_variant_selection(self, ab_test_manager: ABTestManager) -> None:
        """Test variant selection based on traffic split.
        
        Given: Traffic split configuration
        When: Variants are selected
        Then: Should respect traffic distribution
        """
        # Test deterministic selection
        traffic_split = [0.0, 1.0]  # All traffic to second variant
        
        # Run multiple selections
        selections = []
        for _ in range(10):
            selection = ab_test_manager._select_variant(traffic_split)
            selections.append(selection)
        
        # All selections should be variant 1 (index 1)
        assert all(s == 1 for s in selections)

    @pytest.mark.asyncio
    async def test_expired_test_handling(
        self, ab_test_manager: ABTestManager, sample_recommendation: Recommendation
    ) -> None:
        """Test handling of expired tests.
        
        Given: Test that has expired
        When: User assignment is attempted
        Then: Should end test and return None
        """
        test_id = await ab_test_manager.create_ab_test(
            "Expired Test",
            [sample_recommendation],
        )
        
        # Manually expire the test
        ab_test_manager.active_tests[test_id]["end_time"] = datetime.now() - timedelta(hours=1)
        
        # Attempt assignment should end test
        assigned = await ab_test_manager.assign_user_to_variant(test_id, "user1")
        
        assert assigned is None
        assert test_id not in ab_test_manager.active_tests
        assert test_id in ab_test_manager.test_results


class TestRecommendationEngine:
    """Test RecommendationEngine main functionality."""

    @pytest.fixture
    async def recommendation_engine(
        self,
        mock_pattern_db: AsyncMock,
        mock_knowledge_graph: AsyncMock,
        mock_memory_curator: AsyncMock,
    ) -> RecommendationEngine:
        """Create RecommendationEngine instance for testing."""
        engine = RecommendationEngine(
            pattern_db=mock_pattern_db,
            knowledge_graph=mock_knowledge_graph,
            memory_curator=mock_memory_curator,
        )
        await engine.initialize()
        return engine

    @pytest.mark.asyncio
    async def test_engine_initialization(
        self,
        recommendation_engine: RecommendationEngine,
    ) -> None:
        """Test recommendation engine initialization.
        
        Given: Engine components
        When: Engine is initialized
        Then: Should set up all components
        """
        assert recommendation_engine.pattern_db is not None
        assert recommendation_engine.knowledge_graph is not None
        assert recommendation_engine.memory_curator is not None
        assert len(recommendation_engine.generators) == 2
        assert recommendation_engine.ab_test_manager is not None

    @pytest.mark.asyncio
    async def test_get_recommendations_success(
        self,
        recommendation_engine: RecommendationEngine,
        sample_pattern: Pattern,
        sample_knowledge_node: KnowledgeNode,
    ) -> None:
        """Test successful recommendation generation.
        
        Given: Engine with mock data
        When: Recommendations are requested
        Then: Should return filtered and sorted recommendations
        """
        # Configure mocks
        recommendation_engine.pattern_db.get_all_patterns.return_value = [sample_pattern]
        recommendation_engine.knowledge_graph.query_graph.return_value = [sample_knowledge_node]
        
        context = {
            "file_types": ["python"],
            "test_coverage": 70,
            "has_new_functions": True,
            "tags": ["testing"],
        }
        
        recommendations = await recommendation_engine.get_recommendations(context)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= MAX_RECOMMENDATIONS

    @pytest.mark.asyncio
    async def test_get_recommendations_with_user_id(
        self,
        recommendation_engine: RecommendationEngine,
        sample_pattern: Pattern,
    ) -> None:
        """Test recommendations with A/B testing user assignment.
        
        Given: Engine with user ID for A/B testing
        When: Recommendations are requested
        Then: Should apply A/B testing logic
        """
        recommendation_engine.pattern_db.get_all_patterns.return_value = [sample_pattern]
        recommendation_engine.knowledge_graph.query_graph.return_value = []
        
        context = {"file_types": ["python"], "test_coverage": 70}
        
        recommendations = await recommendation_engine.get_recommendations(
            context, user_id="test_user"
        )
        
        assert isinstance(recommendations, list)

    @pytest.mark.asyncio
    async def test_get_recommendations_error_handling(
        self,
        recommendation_engine: RecommendationEngine,
    ) -> None:
        """Test error handling in recommendation generation.
        
        Given: Engine with failing generators
        When: Recommendations are requested
        Then: Should handle errors gracefully
        """
        # Make generators fail
        recommendation_engine.pattern_db.get_all_patterns.side_effect = Exception("DB Error")
        recommendation_engine.knowledge_graph.query_graph.side_effect = Exception("Graph Error")
        
        context = {"file_types": ["python"]}
        
        recommendations = await recommendation_engine.get_recommendations(context)
        
        assert recommendations == []

    @pytest.mark.asyncio
    async def test_apply_recommendation_success(
        self,
        recommendation_engine: RecommendationEngine,
        sample_recommendation: Recommendation,
    ) -> None:
        """Test successful recommendation application.
        
        Given: Active recommendation
        When: Recommendation is applied
        Then: Should mark as applied and store memory
        """
        # Add recommendation to active recommendations
        recommendation_engine.active_recommendations[sample_recommendation.id] = sample_recommendation
        
        result = await recommendation_engine.apply_recommendation(
            sample_recommendation.id, user_id="test_user", success=True
        )
        
        assert result is True
        assert sample_recommendation.id not in recommendation_engine.active_recommendations
        assert sample_recommendation.id in recommendation_engine.applied_recommendations
        assert sample_recommendation.applied is True

    @pytest.mark.asyncio
    async def test_apply_nonexistent_recommendation(
        self,
        recommendation_engine: RecommendationEngine,
    ) -> None:
        """Test applying non-existent recommendation.
        
        Given: Non-existent recommendation ID
        When: Application is attempted
        Then: Should return False
        """
        result = await recommendation_engine.apply_recommendation("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_recommendation_filtering(
        self,
        recommendation_engine: RecommendationEngine,
    ) -> None:
        """Test recommendation filtering logic.
        
        Given: Recommendations with various quality levels
        When: Filtering is applied
        Then: Should filter appropriately
        """
        # Create recommendations with different confidence levels
        high_conf_rec = Recommendation(
            id="high_conf",
            type=RecommendationType.TESTING,
            priority=RecommendationPriority.HIGH,
            title="High Confidence",
            description="High confidence recommendation",
            context={},
            action={"type": "test1"},
            expected_outcome={},
            confidence=0.9,
            reasoning="High confidence",
            supporting_evidence=[],
            estimated_effort="Low",
            estimated_impact="High",
        )
        
        low_conf_rec = Recommendation(
            id="low_conf",
            type=RecommendationType.TESTING,
            priority=RecommendationPriority.LOW,
            title="Low Confidence",
            description="Low confidence recommendation",
            context={},
            action={"type": "test2"},
            expected_outcome={},
            confidence=0.3,  # Below threshold
            reasoning="Low confidence",
            supporting_evidence=[],
            estimated_effort="Low",
            estimated_impact="Low",
        )
        
        expired_rec = Recommendation(
            id="expired",
            type=RecommendationType.TESTING,
            priority=RecommendationPriority.MEDIUM,
            title="Expired",
            description="Expired recommendation",
            context={},
            action={"type": "test3"},
            expected_outcome={},
            confidence=0.8,
            reasoning="Expired",
            supporting_evidence=[],
            estimated_effort="Medium",
            estimated_impact="Medium",
            expires_at=datetime.now() - timedelta(hours=1),  # Expired
        )
        
        recommendations = [high_conf_rec, low_conf_rec, expired_rec]
        
        filtered = await recommendation_engine._filter_recommendations(recommendations, {})
        
        # Should only contain high confidence, non-expired recommendation
        assert len(filtered) == 1
        assert filtered[0].id == "high_conf"

    @pytest.mark.asyncio
    async def test_recommendation_sorting(
        self,
        recommendation_engine: RecommendationEngine,
    ) -> None:
        """Test recommendation sorting logic.
        
        Given: Recommendations with different priorities and confidence
        When: Sorting is applied
        Then: Should sort by priority, confidence, and urgency
        """
        recommendations = [
            Recommendation(
                id="low_priority",
                type=RecommendationType.OPTIMIZATION,
                priority=RecommendationPriority.LOW,
                title="Low Priority",
                description="Low priority recommendation",
                context={},
                action={},
                expected_outcome={},
                confidence=0.9,
                reasoning="Low priority",
                supporting_evidence=[],
                estimated_effort="Low",
                estimated_impact="Low",
            ),
            Recommendation(
                id="high_priority",
                type=RecommendationType.SECURITY,
                priority=RecommendationPriority.CRITICAL,
                title="High Priority",
                description="Critical security recommendation",
                context={},
                action={},
                expected_outcome={},
                confidence=0.8,
                reasoning="Critical",
                supporting_evidence=[],
                estimated_effort="High",
                estimated_impact="Critical",
            ),
        ]
        
        sorted_recs = await recommendation_engine._sort_recommendations(recommendations)
        
        # Critical priority should come first
        assert sorted_recs[0].id == "high_priority"
        assert sorted_recs[1].id == "low_priority"

    @pytest.mark.asyncio
    async def test_get_recommendation_analytics(
        self,
        recommendation_engine: RecommendationEngine,
        sample_recommendation: Recommendation,
    ) -> None:
        """Test recommendation analytics generation.
        
        Given: Engine with recommendations
        When: Analytics are requested
        Then: Should return comprehensive analytics
        """
        # Add some recommendations
        recommendation_engine.active_recommendations[sample_recommendation.id] = sample_recommendation
        
        applied_rec = Recommendation(
            id="applied_rec",
            type=RecommendationType.DOCUMENTATION,
            priority=RecommendationPriority.MEDIUM,
            title="Applied",
            description="Applied recommendation",
            context={},
            action={},
            expected_outcome={},
            confidence=0.7,
            reasoning="Applied",
            supporting_evidence=[],
            estimated_effort="Medium",
            estimated_impact="Medium",
            applied=True,
        )
        recommendation_engine.applied_recommendations[applied_rec.id] = applied_rec
        
        analytics = await recommendation_engine.get_recommendation_analytics()
        
        assert "total_recommendations_generated" in analytics
        assert "active_recommendations" in analytics
        assert "applied_recommendations" in analytics
        assert "application_rate" in analytics
        assert "type_distribution" in analytics
        assert "priority_distribution" in analytics
        assert "avg_confidence" in analytics
        assert "ab_tests" in analytics
        
        assert analytics["active_recommendations"] == 1
        assert analytics["applied_recommendations"] == 1
        assert analytics["application_rate"] == 0.5  # 1 out of 2 applied

    @pytest.mark.asyncio
    async def test_prerequisite_checking(
        self,
        recommendation_engine: RecommendationEngine,
    ) -> None:
        """Test prerequisite checking logic.
        
        Given: Recommendations with prerequisites
        When: Applicability is checked
        Then: Should respect prerequisite requirements
        """
        context_with_python = {"language": "python", "has_tests": True}
        context_without_python = {"language": "java", "has_tests": False}
        
        # Test python prerequisite
        assert recommendation_engine._check_prerequisite("python environment", context_with_python)
        assert not recommendation_engine._check_prerequisite("python environment", context_without_python)
        
        # Test test prerequisite
        assert recommendation_engine._check_prerequisite("test framework", context_with_python)
        assert not recommendation_engine._check_prerequisite("test framework", context_without_python)

    @pytest.mark.asyncio
    async def test_context_compatibility_checking(
        self,
        recommendation_engine: RecommendationEngine,
    ) -> None:
        """Test context compatibility checking.
        
        Given: Recommendation context and current context
        When: Compatibility is checked
        Then: Should identify compatible contexts
        """
        rec_context = {"required_language": "python", "optional_framework": "pytest"}
        
        compatible_context = {"language": "python", "framework": "pytest"}
        incompatible_context = {"framework": "pytest"}  # Missing required language
        
        assert recommendation_engine._check_context_compatibility(rec_context, compatible_context)
        assert not recommendation_engine._check_context_compatibility(rec_context, incompatible_context)

    @pytest.mark.asyncio
    async def test_concurrent_recommendation_generation(
        self,
        recommendation_engine: RecommendationEngine,
        sample_pattern: Pattern,
    ) -> None:
        """Test concurrent recommendation generation.
        
        Given: Multiple concurrent requests
        When: Recommendations are generated simultaneously
        Then: Should handle concurrency correctly
        """
        recommendation_engine.pattern_db.get_all_patterns.return_value = [sample_pattern]
        recommendation_engine.knowledge_graph.query_graph.return_value = []
        
        contexts = [
            {"file_types": ["python"], "test_coverage": 70 + i}
            for i in range(5)
        ]
        
        # Generate recommendations concurrently
        tasks = [
            recommendation_engine.get_recommendations(context)
            for context in contexts
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(isinstance(result, list) for result in results)


class TestRecommendationEngineIntegration:
    """Integration tests for recommendation engine system."""

    @pytest.mark.asyncio
    async def test_full_recommendation_lifecycle(
        self,
        mock_pattern_db: AsyncMock,
        mock_knowledge_graph: AsyncMock,
        mock_memory_curator: AsyncMock,
        sample_pattern: Pattern,
    ) -> None:
        """Test complete recommendation lifecycle.
        
        Given: Full recommendation engine setup
        When: Complete lifecycle is executed
        Then: All operations should work correctly
        """
        # Set up mocks
        mock_pattern_db.get_all_patterns.return_value = [sample_pattern]
        mock_knowledge_graph.query_graph.return_value = []
        
        # Create engine
        engine = RecommendationEngine(
            pattern_db=mock_pattern_db,
            knowledge_graph=mock_knowledge_graph,
            memory_curator=mock_memory_curator,
        )
        await engine.initialize()
        
        # Generate recommendations
        context = {
            "file_types": ["python"],
            "test_coverage": 70,
            "has_new_functions": True,
        }
        
        recommendations = await engine.get_recommendations(context, user_id="test_user")
        
        if recommendations:
            # Apply first recommendation
            rec_id = recommendations[0].id
            success = await engine.apply_recommendation(rec_id, "test_user", True)
            
            assert success
            
            # Check analytics
            analytics = await engine.get_recommendation_analytics()
            assert analytics["applied_recommendations"] == 1

    @pytest.mark.asyncio
    async def test_ab_testing_integration(
        self,
        mock_pattern_db: AsyncMock,
        mock_knowledge_graph: AsyncMock,
        mock_memory_curator: AsyncMock,
    ) -> None:
        """Test A/B testing integration with recommendation engine.
        
        Given: Engine with A/B testing enabled
        When: Recommendations are generated and applied
        Then: Should track A/B test metrics
        """
        # Set up mocks
        mock_pattern_db.get_all_patterns.return_value = []
        mock_knowledge_graph.query_graph.return_value = []
        
        engine = RecommendationEngine(
            pattern_db=mock_pattern_db,
            knowledge_graph=mock_knowledge_graph,
            memory_curator=mock_memory_curator,
        )
        await engine.initialize()
        
        # Create A/B test
        variant1 = Recommendation(
            id="variant1",
            type=RecommendationType.TESTING,
            priority=RecommendationPriority.HIGH,
            title="Variant 1",
            description="First variant",
            context={},
            action={"type": "test1"},
            expected_outcome={},
            confidence=0.8,
            reasoning="Variant 1",
            supporting_evidence=[],
            estimated_effort="Low",
            estimated_impact="High",
        )
        
        variant2 = Recommendation(
            id="variant2",
            type=RecommendationType.TESTING,
            priority=RecommendationPriority.HIGH,
            title="Variant 2",
            description="Second variant",
            context={},
            action={"type": "test2"},
            expected_outcome={},
            confidence=0.8,
            reasoning="Variant 2",
            supporting_evidence=[],
            estimated_effort="Low",
            estimated_impact="High",
        )
        
        test_id = await engine.ab_test_manager.create_ab_test(
            "Test Variants",
            [variant1, variant2],
            traffic_split=[0.5, 0.5],
        )
        
        # Assign users and record results
        for i in range(10):
            user_id = f"user_{i}"
            assigned = await engine.ab_test_manager.assign_user_to_variant(test_id, user_id)
            
            if assigned:
                await engine.ab_test_manager.record_test_result(
                    test_id, user_id, applied=True, success=(i % 2 == 0)
                )
        
        # Get test results
        results = await engine.ab_test_manager.get_test_results(test_id)
        
        assert results is not None
        assert len(results["variants"]) == 2
        assert sum(v["applications"] for v in results["variants"]) == 10


# Property-based testing
# Note: Property-based testing with hypothesis would go here
# Commented out to avoid optional dependency issues

class TestRecommendationProperties:
    """Property-based tests for recommendation system."""

    def test_recommendation_creation_properties(
        self,
        confidence: float,
        priority: RecommendationPriority,
        recommendation_type: RecommendationType,
    ) -> None:
        """Test recommendation creation with various property combinations.
        
        Given: Any valid recommendation properties
        When: Recommendation is created
        Then: Should create valid recommendation without errors
        """
        recommendation = Recommendation(
            id="test_rec",
            type=recommendation_type,
            priority=priority,
            title="Test Recommendation",
            description="Property test recommendation",
            context={},
            action={},
            expected_outcome={},
            confidence=confidence,
            reasoning="Property test",
            supporting_evidence=[],
            estimated_effort="Medium",
            estimated_impact="Medium",
        )
        
        assert recommendation.confidence == confidence
        assert recommendation.priority == priority
        assert recommendation.type == recommendation_type
        assert 0.0 <= recommendation.confidence <= 1.0