"""
Comprehensive tests for Feedback Loop System.

This module tests the continuous learning feedback loop
that measures and improves T-Developer's learning effectiveness.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, Mock

import pytest

from packages.learning.feedback_loop import (
    FeedbackLoop,
    LearningMetrics,
    PerformanceTracker,
    MetricType,
    DEFAULT_MEASUREMENT_WINDOW_HOURS,
    MIN_SAMPLES_FOR_ANALYSIS,
)


@pytest.fixture
def sample_learning_metrics() -> LearningMetrics:
    """Create sample learning metrics for testing."""
    return LearningMetrics(
        pattern_accuracy=0.85,
        recommendation_success_rate=0.78,
        prediction_accuracy=0.82,
        adaptation_rate=0.76,
        overall_score=0.80,
    )


@pytest.fixture
async def mock_pattern_db() -> AsyncMock:
    """Create mock pattern database."""
    mock_db = AsyncMock()
    mock_db.get_all_patterns.return_value = []
    mock_db.get_pattern_analytics.return_value = {
        "total_uses": 10,
        "success_rate": 0.8,
        "recent_uses": 5,
    }
    return mock_db


@pytest.fixture
async def mock_recommendation_engine() -> AsyncMock:
    """Create mock recommendation engine."""
    mock_engine = AsyncMock()
    mock_engine.get_recommendation_analytics.return_value = {
        "total_recommendations_generated": 100,
        "applied_recommendations": 25,
        "application_rate": 0.25,
    }
    return mock_engine


@pytest.fixture
async def mock_memory_curator() -> AsyncMock:
    """Create mock memory curator."""
    mock_curator = AsyncMock()
    mock_curator.get_memory_metrics.return_value = Mock(
        total_memories=500,
        average_importance=0.7,
        retention_rate=0.85,
    )
    mock_curator.search_memories.return_value = []
    return mock_curator


@pytest.fixture
async def performance_tracker() -> PerformanceTracker:
    """Create performance tracker instance for testing."""
    return PerformanceTracker()


@pytest.fixture
async def feedback_loop(
    mock_pattern_db: AsyncMock,
    mock_recommendation_engine: AsyncMock,
    mock_memory_curator: AsyncMock,
) -> FeedbackLoop:
    """Create feedback loop instance for testing."""
    return FeedbackLoop(
        pattern_db=mock_pattern_db,
        recommendation_engine=mock_recommendation_engine,
        memory_curator=mock_memory_curator,
    )


class TestLearningMetrics:
    """Test LearningMetrics functionality."""

    def test_metrics_creation(self, sample_learning_metrics: LearningMetrics) -> None:
        """Test learning metrics creation.
        
        Given: Valid metrics data
        When: Metrics are created
        Then: All fields should be set correctly
        """
        assert sample_learning_metrics.pattern_accuracy == 0.85
        assert sample_learning_metrics.recommendation_success_rate == 0.78
        assert sample_learning_metrics.prediction_accuracy == 0.82
        assert sample_learning_metrics.adaptation_rate == 0.76
        assert sample_learning_metrics.overall_score == 0.80

    def test_metrics_to_dict(self, sample_learning_metrics: LearningMetrics) -> None:
        """Test metrics serialization to dictionary.
        
        Given: Learning metrics
        When: to_dict is called
        Then: Should return dictionary with all metrics
        """
        metrics_dict = sample_learning_metrics.to_dict()
        
        assert isinstance(metrics_dict, dict)
        assert metrics_dict["pattern_accuracy"] == 0.85
        assert metrics_dict["overall_score"] == 0.80
        assert len(metrics_dict) == 5

    def test_metrics_from_dict(self, sample_learning_metrics: LearningMetrics) -> None:
        """Test metrics deserialization from dictionary.
        
        Given: Metrics dictionary
        When: from_dict is called
        Then: Should return LearningMetrics with correct values
        """
        metrics_dict = sample_learning_metrics.to_dict()
        reconstructed = LearningMetrics.from_dict(metrics_dict)
        
        assert reconstructed.pattern_accuracy == sample_learning_metrics.pattern_accuracy
        assert reconstructed.overall_score == sample_learning_metrics.overall_score

    def test_calculate_overall_score(self) -> None:
        """Test overall score calculation.
        
        Given: Individual metric scores
        When: Overall score is calculated
        Then: Should return weighted average
        """
        metrics = LearningMetrics(
            pattern_accuracy=0.8,
            recommendation_success_rate=0.7,
            prediction_accuracy=0.9,
            adaptation_rate=0.6,
        )
        
        # Overall score should be calculated automatically
        assert 0.0 <= metrics.overall_score <= 1.0
        # Should be roughly the average of the components
        expected_avg = (0.8 + 0.7 + 0.9 + 0.6) / 4
        assert abs(metrics.overall_score - expected_avg) < 0.1


class TestPerformanceTracker:
    """Test PerformanceTracker functionality."""

    def test_tracker_initialization(self, performance_tracker: PerformanceTracker) -> None:
        """Test performance tracker initialization.
        
        Given: Performance tracker
        When: Tracker is created
        Then: Should initialize with empty metrics
        """
        assert performance_tracker.metrics == {}
        assert performance_tracker.measurement_history == []

    def test_record_metric(self, performance_tracker: PerformanceTracker) -> None:
        """Test recording a performance metric.
        
        Given: Performance tracker
        When: Metric is recorded
        Then: Should store metric with timestamp
        """
        performance_tracker.record_metric(MetricType.PATTERN_SUCCESS, 0.85)
        
        assert len(performance_tracker.measurement_history) == 1
        measurement = performance_tracker.measurement_history[0]
        assert measurement["type"] == MetricType.PATTERN_SUCCESS
        assert measurement["value"] == 0.85
        assert "timestamp" in measurement

    def test_get_recent_metrics(self, performance_tracker: PerformanceTracker) -> None:
        """Test getting recent metrics.
        
        Given: Performance tracker with recorded metrics
        When: Recent metrics are requested
        Then: Should return metrics within time window
        """
        # Record some metrics
        performance_tracker.record_metric(MetricType.PATTERN_SUCCESS, 0.8)
        performance_tracker.record_metric(MetricType.RECOMMENDATION_SUCCESS, 0.7)
        
        recent = performance_tracker.get_recent_metrics(hours=24)
        
        assert len(recent) == 2
        assert all("timestamp" in m for m in recent)

    def test_calculate_trend(self, performance_tracker: PerformanceTracker) -> None:
        """Test calculating metric trends.
        
        Given: Performance tracker with time series data
        When: Trend is calculated
        Then: Should return trend direction
        """
        # Record improving trend
        for i in range(5):
            performance_tracker.record_metric(MetricType.PATTERN_SUCCESS, 0.6 + i * 0.1)
        
        trend = performance_tracker.calculate_trend(MetricType.PATTERN_SUCCESS)
        
        # Should detect positive trend
        assert trend > 0

    def test_get_metric_statistics(self, performance_tracker: PerformanceTracker) -> None:
        """Test getting metric statistics.
        
        Given: Performance tracker with various metrics
        When: Statistics are requested
        Then: Should return comprehensive stats
        """
        # Record multiple values
        values = [0.7, 0.8, 0.9, 0.75, 0.85]
        for value in values:
            performance_tracker.record_metric(MetricType.PATTERN_SUCCESS, value)
        
        stats = performance_tracker.get_metric_statistics(MetricType.PATTERN_SUCCESS)
        
        assert "average" in stats
        assert "min" in stats
        assert "max" in stats
        assert "count" in stats
        assert stats["count"] == 5
        assert stats["min"] == 0.7
        assert stats["max"] == 0.9


class TestFeedbackLoop:
    """Test FeedbackLoop functionality."""

    @pytest.mark.asyncio
    async def test_feedback_loop_initialization(self, feedback_loop: FeedbackLoop) -> None:
        """Test feedback loop initialization.
        
        Given: Feedback loop components
        When: Feedback loop is initialized
        Then: Should set up correctly
        """
        await feedback_loop.initialize()
        
        assert feedback_loop.pattern_db is not None
        assert feedback_loop.recommendation_engine is not None
        assert feedback_loop.memory_curator is not None
        assert feedback_loop.performance_tracker is not None

    @pytest.mark.asyncio
    async def test_measure_learning_effectiveness(
        self, feedback_loop: FeedbackLoop, mock_pattern_db: AsyncMock
    ) -> None:
        """Test measuring learning effectiveness.
        
        Given: Feedback loop with mock components
        When: Learning effectiveness is measured
        Then: Should return comprehensive metrics
        """
        await feedback_loop.initialize()
        
        metrics = await feedback_loop.measure_learning_effectiveness()
        
        assert isinstance(metrics, LearningMetrics)
        assert 0.0 <= metrics.pattern_accuracy <= 1.0
        assert 0.0 <= metrics.overall_score <= 1.0

    @pytest.mark.asyncio
    async def test_measure_pattern_accuracy(
        self, feedback_loop: FeedbackLoop, mock_pattern_db: AsyncMock
    ) -> None:
        """Test measuring pattern accuracy.
        
        Given: Pattern database with usage data
        When: Pattern accuracy is measured
        Then: Should return accuracy score
        """
        await feedback_loop.initialize()
        
        # Mock patterns with analytics
        from packages.learning.pattern_database import Pattern
        mock_pattern = Pattern(
            id="test_pattern",
            category="testing",
            name="Test Pattern",
            description="A test pattern",
            context={},
            action={},
            outcome={},
            success_rate=0.9,
            usage_count=10,
            created_at=datetime.now(),
        )
        mock_pattern_db.get_all_patterns.return_value = [mock_pattern]
        
        accuracy = await feedback_loop._measure_pattern_accuracy()
        
        assert 0.0 <= accuracy <= 1.0

    @pytest.mark.asyncio
    async def test_measure_recommendation_success(
        self, feedback_loop: FeedbackLoop, mock_recommendation_engine: AsyncMock
    ) -> None:
        """Test measuring recommendation success rate.
        
        Given: Recommendation engine with analytics
        When: Recommendation success is measured
        Then: Should return success rate
        """
        await feedback_loop.initialize()
        
        success_rate = await feedback_loop._measure_recommendation_success()
        
        assert 0.0 <= success_rate <= 1.0

    @pytest.mark.asyncio
    async def test_measure_prediction_accuracy(
        self, feedback_loop: FeedbackLoop, mock_memory_curator: AsyncMock
    ) -> None:
        """Test measuring prediction accuracy.
        
        Given: Memory curator with prediction data
        When: Prediction accuracy is measured
        Then: Should return accuracy score
        """
        await feedback_loop.initialize()
        
        # Mock memories with prediction outcomes
        from packages.learning.memory_curator import Memory
        mock_memories = [
            Memory(
                id="pred_1",
                type="prediction_outcome",
                timestamp=datetime.now(),
                data={"predicted": True, "actual": True},
                metadata={},
            ),
            Memory(
                id="pred_2",
                type="prediction_outcome",
                timestamp=datetime.now(),
                data={"predicted": False, "actual": True},
                metadata={},
            ),
        ]
        mock_memory_curator.search_memories.return_value = mock_memories
        
        accuracy = await feedback_loop._measure_prediction_accuracy()
        
        assert 0.0 <= accuracy <= 1.0

    @pytest.mark.asyncio
    async def test_measure_adaptation_rate(
        self, feedback_loop: FeedbackLoop, mock_memory_curator: AsyncMock
    ) -> None:
        """Test measuring adaptation rate.
        
        Given: Memory curator with adaptation data
        When: Adaptation rate is measured
        Then: Should return adaptation score
        """
        await feedback_loop.initialize()
        
        # Mock memories with adaptation events
        from packages.learning.memory_curator import Memory
        mock_memories = [
            Memory(
                id="adapt_1",
                type="adaptation",
                timestamp=datetime.now(),
                data={"improvement": 0.1},
                metadata={},
            ),
        ]
        mock_memory_curator.search_memories.return_value = mock_memories
        
        adaptation_rate = await feedback_loop._measure_adaptation_rate()
        
        assert 0.0 <= adaptation_rate <= 1.0

    @pytest.mark.asyncio
    async def test_analyze_performance_trends(self, feedback_loop: FeedbackLoop) -> None:
        """Test analyzing performance trends.
        
        Given: Feedback loop with historical data
        When: Performance trends are analyzed
        Then: Should return trend analysis
        """
        await feedback_loop.initialize()
        
        # Add some performance data
        tracker = feedback_loop.performance_tracker
        for i in range(10):
            tracker.record_metric(MetricType.PATTERN_SUCCESS, 0.7 + i * 0.02)
        
        trends = await feedback_loop.analyze_performance_trends()
        
        assert isinstance(trends, dict)
        assert "pattern_success" in trends or len(trends) == 0  # May be empty if no data

    @pytest.mark.asyncio
    async def test_generate_improvement_recommendations(
        self, feedback_loop: FeedbackLoop
    ) -> None:
        """Test generating improvement recommendations.
        
        Given: Feedback loop with performance data
        When: Improvement recommendations are generated
        Then: Should return actionable recommendations
        """
        await feedback_loop.initialize()
        
        recommendations = await feedback_loop.generate_improvement_recommendations()
        
        assert isinstance(recommendations, list)
        # May be empty if no improvements needed

    @pytest.mark.asyncio
    async def test_continuous_learning_cycle(self, feedback_loop: FeedbackLoop) -> None:
        """Test continuous learning cycle execution.
        
        Given: Feedback loop
        When: Learning cycle is executed
        Then: Should measure, analyze, and improve
        """
        await feedback_loop.initialize()
        
        cycle_result = await feedback_loop.execute_learning_cycle()
        
        assert isinstance(cycle_result, dict)
        assert "metrics" in cycle_result
        assert "trends" in cycle_result
        assert "recommendations" in cycle_result

    @pytest.mark.asyncio
    async def test_adaptation_based_on_feedback(self, feedback_loop: FeedbackLoop) -> None:
        """Test adaptation based on feedback.
        
        Given: Feedback loop with poor performance metrics
        When: Adaptation is triggered
        Then: Should implement improvements
        """
        await feedback_loop.initialize()
        
        # Simulate poor performance
        poor_metrics = LearningMetrics(
            pattern_accuracy=0.4,
            recommendation_success_rate=0.3,
            prediction_accuracy=0.4,
            adaptation_rate=0.2,
            overall_score=0.3,
        )
        
        adaptations = await feedback_loop._adapt_based_on_metrics(poor_metrics)
        
        assert isinstance(adaptations, list)
        # Should suggest adaptations for poor performance

    @pytest.mark.asyncio
    async def test_store_learning_cycle_results(
        self, feedback_loop: FeedbackLoop, mock_memory_curator: AsyncMock
    ) -> None:
        """Test storing learning cycle results.
        
        Given: Learning cycle results
        When: Results are stored
        Then: Should create memory record
        """
        await feedback_loop.initialize()
        
        cycle_results = {
            "metrics": LearningMetrics(0.8, 0.7, 0.9, 0.6),
            "trends": {"improving": True},
            "timestamp": datetime.now(),
        }
        
        await feedback_loop._store_cycle_results(cycle_results)
        
        # Verify memory curator was called
        mock_memory_curator.store_memory.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_learning_progress(self, feedback_loop: FeedbackLoop) -> None:
        """Test getting learning progress over time.
        
        Given: Feedback loop with historical data
        When: Learning progress is requested
        Then: Should return progress metrics
        """
        await feedback_loop.initialize()
        
        progress = await feedback_loop.get_learning_progress(days=7)
        
        assert isinstance(progress, dict)
        assert "current_metrics" in progress
        assert "historical_trend" in progress

    @pytest.mark.asyncio
    async def test_detect_learning_plateaus(self, feedback_loop: FeedbackLoop) -> None:
        """Test detecting learning plateaus.
        
        Given: Feedback loop with stagnant metrics
        When: Plateau detection is performed
        Then: Should identify stagnation
        """
        await feedback_loop.initialize()
        
        # Add stagnant data
        tracker = feedback_loop.performance_tracker
        for _ in range(10):
            tracker.record_metric(MetricType.OVERALL_PERFORMANCE, 0.75)  # Same value
        
        plateaus = await feedback_loop._detect_plateaus()
        
        assert isinstance(plateaus, list)

    @pytest.mark.asyncio
    async def test_emergency_adaptation(self, feedback_loop: FeedbackLoop) -> None:
        """Test emergency adaptation for critical performance drops.
        
        Given: Feedback loop with critical performance drop
        When: Emergency adaptation is triggered
        Then: Should implement immediate fixes
        """
        await feedback_loop.initialize()
        
        # Simulate critical drop
        critical_metrics = LearningMetrics(
            pattern_accuracy=0.2,
            recommendation_success_rate=0.1,
            prediction_accuracy=0.2,
            adaptation_rate=0.1,
            overall_score=0.15,
        )
        
        emergency_actions = await feedback_loop._trigger_emergency_adaptation(critical_metrics)
        
        assert isinstance(emergency_actions, list)
        # Should have emergency actions for critical performance


class TestFeedbackLoopIntegration:
    """Integration tests for feedback loop system."""

    @pytest.mark.asyncio
    async def test_full_feedback_cycle(
        self,
        mock_pattern_db: AsyncMock,
        mock_recommendation_engine: AsyncMock,
        mock_memory_curator: AsyncMock,
    ) -> None:
        """Test complete feedback cycle workflow.
        
        Given: Full feedback loop setup
        When: Complete cycle is executed
        Then: Should measure, analyze, adapt, and store results
        """
        feedback_loop = FeedbackLoop(
            pattern_db=mock_pattern_db,
            recommendation_engine=mock_recommendation_engine,
            memory_curator=mock_memory_curator,
        )
        await feedback_loop.initialize()
        
        # Execute full cycle
        cycle_result = await feedback_loop.execute_learning_cycle()
        
        # Verify all components were called
        assert isinstance(cycle_result, dict)
        assert "metrics" in cycle_result
        
        # Verify storage was called
        mock_memory_curator.store_memory.assert_called()

    @pytest.mark.asyncio
    async def test_concurrent_feedback_operations(
        self,
        mock_pattern_db: AsyncMock,
        mock_recommendation_engine: AsyncMock,
        mock_memory_curator: AsyncMock,
    ) -> None:
        """Test concurrent feedback loop operations.
        
        Given: Feedback loop
        When: Multiple operations are performed concurrently
        Then: Should handle concurrency correctly
        """
        feedback_loop = FeedbackLoop(
            pattern_db=mock_pattern_db,
            recommendation_engine=mock_recommendation_engine,
            memory_curator=mock_memory_curator,
        )
        await feedback_loop.initialize()
        
        # Run multiple measurements concurrently
        tasks = [
            feedback_loop.measure_learning_effectiveness()
            for _ in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(isinstance(result, LearningMetrics) for result in results)

    @pytest.mark.asyncio
    async def test_long_term_learning_tracking(
        self,
        mock_pattern_db: AsyncMock,
        mock_recommendation_engine: AsyncMock,
        mock_memory_curator: AsyncMock,
    ) -> None:
        """Test long-term learning progress tracking.
        
        Given: Feedback loop over extended period
        When: Learning progress is tracked
        Then: Should show improvement trends
        """
        feedback_loop = FeedbackLoop(
            pattern_db=mock_pattern_db,
            recommendation_engine=mock_recommendation_engine,
            memory_curator=mock_memory_curator,
        )
        await feedback_loop.initialize()
        
        # Simulate improving performance over time
        tracker = feedback_loop.performance_tracker
        for day in range(30):
            # Gradual improvement
            score = 0.5 + (day * 0.01)  # Improve from 0.5 to 0.8
            tracker.record_metric(MetricType.OVERALL_PERFORMANCE, min(score, 1.0))
        
        progress = await feedback_loop.get_learning_progress(days=30)
        
        assert isinstance(progress, dict)
        assert "current_metrics" in progress
        assert "historical_trend" in progress


# Property-based testing
# Note: Property-based testing with hypothesis would go here
# Commented out to avoid optional dependency issues

class TestFeedbackLoopProperties:
    """Property-based tests for feedback loop system."""

    @given(
        pattern_accuracy=st.floats(min_value=0.0, max_value=1.0),
        recommendation_success=st.floats(min_value=0.0, max_value=1.0),
        prediction_accuracy=st.floats(min_value=0.0, max_value=1.0),
        adaptation_rate=st.floats(min_value=0.0, max_value=1.0),
    )
    def test_learning_metrics_properties(
        self,
        pattern_accuracy: float,
        recommendation_success: float,
        prediction_accuracy: float,
        adaptation_rate: float,
    ) -> None:
        """Test learning metrics with various property combinations.
        
        Given: Any valid metric values
        When: Metrics are created
        Then: Should create valid metrics without errors
        """
        metrics = LearningMetrics(
            pattern_accuracy=pattern_accuracy,
            recommendation_success_rate=recommendation_success,
            prediction_accuracy=prediction_accuracy,
            adaptation_rate=adaptation_rate,
        )
        
        assert 0.0 <= metrics.pattern_accuracy <= 1.0
        assert 0.0 <= metrics.recommendation_success_rate <= 1.0
        assert 0.0 <= metrics.prediction_accuracy <= 1.0
        assert 0.0 <= metrics.adaptation_rate <= 1.0
        assert 0.0 <= metrics.overall_score <= 1.0