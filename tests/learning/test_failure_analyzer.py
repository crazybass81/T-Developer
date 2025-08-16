"""
Comprehensive tests for Failure Analyzer System.

This module tests the failure analysis and prevention system
for T-Developer learning.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, Mock

import pytest

from packages.learning.failure_analyzer import (
    FailureAnalyzer,
    FailurePattern,
    FailureCategory,
    FailureSeverity,
    FailureContext,
    MIN_FAILURE_FREQUENCY,
)


@pytest.fixture
def sample_failure_report() -> FailureReport:
    """Create sample failure report for testing."""
    return FailureReport(
        id="failure_001",
        timestamp=datetime.now(),
        failure_type=FailureType.EXECUTION_ERROR,
        component="test_runner",
        error_message="Test execution timeout",
        context={
            "test_file": "test_integration.py",
            "timeout": 300,
            "environment": "staging",
        },
        stack_trace="Traceback...",
        severity="high",
        resolved=False,
    )


@pytest.fixture
def sample_failure_pattern() -> FailurePattern:
    """Create sample failure pattern for testing."""
    return FailurePattern(
        id="pattern_001",
        name="Test Timeout Pattern",
        description="Tests timing out in staging environment",
        failure_type=FailureType.EXECUTION_ERROR,
        frequency=5,
        affected_components=["test_runner", "integration_tests"],
        common_contexts={
            "environment": "staging",
            "timeout_range": [250, 350],
        },
        potential_causes=[
            "Slow database queries",
            "Network latency",
            "Resource contention",
        ],
        suggested_fixes=[
            "Increase timeout values",
            "Optimize database queries",
            "Add retry logic",
        ],
        confidence=0.85,
        created_at=datetime.now(),
    )


@pytest.fixture
def sample_root_cause_analysis() -> RootCauseAnalysis:
    """Create sample root cause analysis for testing."""
    return RootCauseAnalysis(
        failure_id="failure_001",
        primary_cause="Database connection timeout",
        contributing_factors=[
            "High database load",
            "Network latency spikes",
            "Insufficient connection pool size",
        ],
        evidence=[
            "Database logs show slow queries",
            "Network monitoring shows latency spikes",
            "Connection pool exhaustion events",
        ],
        confidence=0.9,
        analysis_method="automated_pattern_matching",
        timestamp=datetime.now(),
    )


@pytest.fixture
async def mock_memory_curator() -> AsyncMock:
    """Create mock memory curator."""
    mock_curator = AsyncMock()
    mock_curator.search_memories.return_value = []
    mock_curator.store_memory.return_value = None
    return mock_curator


@pytest.fixture
async def failure_analyzer(mock_memory_curator: AsyncMock) -> FailureAnalyzer:
    """Create failure analyzer instance for testing."""
    return FailureAnalyzer(memory_curator=mock_memory_curator)


class TestFailureReport:
    """Test FailureReport functionality."""

    def test_failure_report_creation(self, sample_failure_report: FailureReport) -> None:
        """Test failure report creation.
        
        Given: Valid failure report data
        When: Report is created
        Then: All fields should be set correctly
        """
        assert sample_failure_report.id == "failure_001"
        assert sample_failure_report.failure_type == FailureType.EXECUTION_ERROR
        assert sample_failure_report.component == "test_runner"
        assert sample_failure_report.severity == "high"
        assert not sample_failure_report.resolved

    def test_failure_report_to_dict(self, sample_failure_report: FailureReport) -> None:
        """Test failure report serialization.
        
        Given: Failure report
        When: to_dict is called
        Then: Should return dictionary with correct structure
        """
        report_dict = sample_failure_report.to_dict()
        
        assert isinstance(report_dict, dict)
        assert report_dict["id"] == "failure_001"
        assert report_dict["failure_type"] == "execution_error"
        assert isinstance(report_dict["timestamp"], str)

    def test_failure_report_from_dict(self, sample_failure_report: FailureReport) -> None:
        """Test failure report deserialization.
        
        Given: Report dictionary
        When: from_dict is called
        Then: Should return FailureReport with correct types
        """
        report_dict = sample_failure_report.to_dict()
        reconstructed = FailureReport.from_dict(report_dict)
        
        assert reconstructed.id == sample_failure_report.id
        assert reconstructed.failure_type == sample_failure_report.failure_type
        assert isinstance(reconstructed.timestamp, datetime)

    def test_failure_severity_classification(self) -> None:
        """Test failure severity classification.
        
        Given: Different failure types
        When: Severity is determined
        Then: Should classify appropriately
        """
        critical_failure = FailureReport(
            id="critical",
            timestamp=datetime.now(),
            failure_type=FailureType.SYSTEM_CRASH,
            component="core",
            error_message="System crash",
            context={},
            severity="critical",
        )
        
        assert critical_failure.severity == "critical"
        
        low_failure = FailureReport(
            id="low",
            timestamp=datetime.now(),
            failure_type=FailureType.WARNING,
            component="ui",
            error_message="Minor UI issue",
            context={},
            severity="low",
        )
        
        assert low_failure.severity == "low"


class TestFailurePattern:
    """Test FailurePattern functionality."""

    def test_failure_pattern_creation(self, sample_failure_pattern: FailurePattern) -> None:
        """Test failure pattern creation.
        
        Given: Valid pattern data
        When: Pattern is created
        Then: All fields should be set correctly
        """
        assert sample_failure_pattern.id == "pattern_001"
        assert sample_failure_pattern.name == "Test Timeout Pattern"
        assert sample_failure_pattern.frequency == 5
        assert sample_failure_pattern.confidence == 0.85

    def test_pattern_to_dict(self, sample_failure_pattern: FailurePattern) -> None:
        """Test pattern serialization.
        
        Given: Failure pattern
        When: to_dict is called
        Then: Should return dictionary with all fields
        """
        pattern_dict = sample_failure_pattern.to_dict()
        
        assert isinstance(pattern_dict, dict)
        assert pattern_dict["name"] == "Test Timeout Pattern"
        assert pattern_dict["frequency"] == 5

    def test_pattern_matching(self, sample_failure_pattern: FailurePattern) -> None:
        """Test pattern matching against failure reports.
        
        Given: Failure pattern and matching report
        When: Pattern matching is performed
        Then: Should identify matches
        """
        matching_report = FailureReport(
            id="match_test",
            timestamp=datetime.now(),
            failure_type=FailureType.EXECUTION_ERROR,
            component="test_runner",
            error_message="Test timeout in staging",
            context={"environment": "staging", "timeout": 300},
        )
        
        # This would be part of the pattern matching logic
        assert sample_failure_pattern.failure_type == matching_report.failure_type


class TestRootCauseAnalysis:
    """Test RootCauseAnalysis functionality."""

    def test_root_cause_analysis_creation(
        self, sample_root_cause_analysis: RootCauseAnalysis
    ) -> None:
        """Test root cause analysis creation.
        
        Given: Valid analysis data
        When: Analysis is created
        Then: All fields should be set correctly
        """
        assert sample_root_cause_analysis.failure_id == "failure_001"
        assert sample_root_cause_analysis.primary_cause == "Database connection timeout"
        assert len(sample_root_cause_analysis.contributing_factors) == 3
        assert sample_root_cause_analysis.confidence == 0.9

    def test_analysis_to_dict(self, sample_root_cause_analysis: RootCauseAnalysis) -> None:
        """Test analysis serialization.
        
        Given: Root cause analysis
        When: to_dict is called
        Then: Should return dictionary with all fields
        """
        analysis_dict = sample_root_cause_analysis.to_dict()
        
        assert isinstance(analysis_dict, dict)
        assert analysis_dict["primary_cause"] == "Database connection timeout"
        assert len(analysis_dict["contributing_factors"]) == 3


class TestFailureAnalyzer:
    """Test FailureAnalyzer functionality."""

    @pytest.mark.asyncio
    async def test_analyzer_initialization(self, failure_analyzer: FailureAnalyzer) -> None:
        """Test failure analyzer initialization.
        
        Given: Memory curator
        When: Analyzer is initialized
        Then: Should set up correctly
        """
        await failure_analyzer.initialize()
        
        assert failure_analyzer.memory_curator is not None
        assert failure_analyzer.failure_patterns == []

    @pytest.mark.asyncio
    async def test_record_failure(
        self, failure_analyzer: FailureAnalyzer, sample_failure_report: FailureReport
    ) -> None:
        """Test recording a failure.
        
        Given: Failure analyzer and failure report
        When: Failure is recorded
        Then: Should store in memory and trigger analysis
        """
        await failure_analyzer.initialize()
        
        await failure_analyzer.record_failure(sample_failure_report)
        
        # Verify memory storage was called
        failure_analyzer.memory_curator.store_memory.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_failure_patterns(
        self, failure_analyzer: FailureAnalyzer, mock_memory_curator: AsyncMock
    ) -> None:
        """Test analyzing failure patterns.
        
        Given: Failure analyzer with historical failures
        When: Pattern analysis is performed
        Then: Should identify patterns
        """
        await failure_analyzer.initialize()
        
        # Mock failure memories
        from packages.learning.memory_curator import Memory
        failure_memories = [
            Memory(
                id="fail_mem_1",
                type="failure_report",
                timestamp=datetime.now(),
                data={
                    "failure_type": "execution_error",
                    "component": "test_runner",
                    "error_message": "timeout",
                },
                metadata={"severity": "high"},
            ),
            Memory(
                id="fail_mem_2",
                type="failure_report",
                timestamp=datetime.now(),
                data={
                    "failure_type": "execution_error",
                    "component": "test_runner",
                    "error_message": "timeout",
                },
                metadata={"severity": "high"},
            ),
        ]
        mock_memory_curator.search_memories.return_value = failure_memories
        
        patterns = await failure_analyzer.analyze_failure_patterns()
        
        assert isinstance(patterns, list)

    @pytest.mark.asyncio
    async def test_perform_root_cause_analysis(
        self, failure_analyzer: FailureAnalyzer, sample_failure_report: FailureReport
    ) -> None:
        """Test performing root cause analysis.
        
        Given: Failure analyzer and failure report
        When: Root cause analysis is performed
        Then: Should return analysis with causes
        """
        await failure_analyzer.initialize()
        
        analysis = await failure_analyzer.perform_root_cause_analysis(sample_failure_report)
        
        assert isinstance(analysis, RootCauseAnalysis)
        assert analysis.failure_id == sample_failure_report.id
        assert analysis.primary_cause is not None
        assert 0.0 <= analysis.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_get_failure_statistics(
        self, failure_analyzer: FailureAnalyzer, mock_memory_curator: AsyncMock
    ) -> None:
        """Test getting failure statistics.
        
        Given: Failure analyzer with historical data
        When: Statistics are requested
        Then: Should return comprehensive stats
        """
        await failure_analyzer.initialize()
        
        # Mock failure data
        from packages.learning.memory_curator import Memory
        failure_memories = [
            Memory(
                id="stat_mem_1",
                type="failure_report",
                timestamp=datetime.now(),
                data={"failure_type": "execution_error", "component": "test_runner"},
                metadata={"severity": "high"},
            ),
        ]
        mock_memory_curator.search_memories.return_value = failure_memories
        
        stats = await failure_analyzer.get_failure_statistics()
        
        assert isinstance(stats, dict)
        assert "total_failures" in stats
        assert "failure_types" in stats
        assert "components" in stats

    @pytest.mark.asyncio
    async def test_predict_failure_risk(
        self, failure_analyzer: FailureAnalyzer, mock_memory_curator: AsyncMock
    ) -> None:
        """Test predicting failure risk.
        
        Given: Context and historical failure data
        When: Failure risk is predicted
        Then: Should return risk assessment
        """
        await failure_analyzer.initialize()
        
        context = {
            "component": "test_runner",
            "environment": "staging",
            "time_of_day": "peak_hours",
        }
        
        risk = await failure_analyzer.predict_failure_risk(context)
        
        assert isinstance(risk, dict)
        assert "risk_score" in risk
        assert "contributing_factors" in risk
        assert 0.0 <= risk["risk_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_generate_prevention_recommendations(
        self, failure_analyzer: FailureAnalyzer, sample_failure_pattern: FailurePattern
    ) -> None:
        """Test generating prevention recommendations.
        
        Given: Failure analyzer with known patterns
        When: Prevention recommendations are requested
        Then: Should return actionable recommendations
        """
        await failure_analyzer.initialize()
        
        # Add pattern to analyzer
        failure_analyzer.failure_patterns = [sample_failure_pattern]
        
        recommendations = await failure_analyzer.generate_prevention_recommendations()
        
        assert isinstance(recommendations, list)

    @pytest.mark.asyncio
    async def test_categorize_failure(
        self, failure_analyzer: FailureAnalyzer, sample_failure_report: FailureReport
    ) -> None:
        """Test failure categorization.
        
        Given: Failure report
        When: Failure is categorized
        Then: Should assign appropriate category
        """
        await failure_analyzer.initialize()
        
        category = await failure_analyzer._categorize_failure(sample_failure_report)
        
        assert isinstance(category, str)
        assert category in ["infrastructure", "code", "environment", "external", "unknown"]

    @pytest.mark.asyncio
    async def test_detect_failure_clusters(
        self, failure_analyzer: FailureAnalyzer, mock_memory_curator: AsyncMock
    ) -> None:
        """Test detecting failure clusters.
        
        Given: Multiple related failures
        When: Cluster detection is performed
        Then: Should group related failures
        """
        await failure_analyzer.initialize()
        
        # Mock clustered failures
        from packages.learning.memory_curator import Memory
        clustered_failures = [
            Memory(
                id=f"cluster_mem_{i}",
                type="failure_report",
                timestamp=datetime.now() - timedelta(minutes=i*5),
                data={
                    "failure_type": "execution_error",
                    "component": "database",
                    "error_message": "connection timeout",
                },
                metadata={},
            )
            for i in range(5)
        ]
        mock_memory_curator.search_memories.return_value = clustered_failures
        
        clusters = await failure_analyzer._detect_failure_clusters()
        
        assert isinstance(clusters, list)

    @pytest.mark.asyncio
    async def test_calculate_pattern_confidence(
        self, failure_analyzer: FailureAnalyzer
    ) -> None:
        """Test calculating pattern confidence.
        
        Given: Failure pattern with occurrences
        When: Confidence is calculated
        Then: Should return appropriate confidence score
        """
        await failure_analyzer.initialize()
        
        # Test with high frequency pattern
        high_freq_confidence = failure_analyzer._calculate_pattern_confidence(
            frequency=10, total_failures=12
        )
        
        assert 0.0 <= high_freq_confidence <= 1.0
        assert high_freq_confidence > 0.7  # Should be high confidence
        
        # Test with low frequency pattern
        low_freq_confidence = failure_analyzer._calculate_pattern_confidence(
            frequency=2, total_failures=20
        )
        
        assert low_freq_confidence < high_freq_confidence

    @pytest.mark.asyncio
    async def test_update_failure_patterns(
        self, failure_analyzer: FailureAnalyzer, sample_failure_report: FailureReport
    ) -> None:
        """Test updating failure patterns with new data.
        
        Given: Existing patterns and new failure
        When: Patterns are updated
        Then: Should modify patterns based on new data
        """
        await failure_analyzer.initialize()
        
        # Add initial pattern
        pattern = FailurePattern(
            id="update_test",
            name="Update Test Pattern",
            description="Test pattern",
            failure_type=FailureType.EXECUTION_ERROR,
            frequency=3,
            affected_components=["test_runner"],
            common_contexts={},
            potential_causes=[],
            suggested_fixes=[],
            confidence=0.6,
            created_at=datetime.now(),
        )
        failure_analyzer.failure_patterns = [pattern]
        
        await failure_analyzer._update_patterns_with_failure(sample_failure_report)
        
        # Pattern should be updated
        updated_pattern = failure_analyzer.failure_patterns[0]
        assert updated_pattern.frequency >= 3  # Should not decrease

    @pytest.mark.asyncio
    async def test_resolve_failure(
        self, failure_analyzer: FailureAnalyzer, sample_failure_report: FailureReport
    ) -> None:
        """Test marking failure as resolved.
        
        Given: Recorded failure
        When: Failure is resolved
        Then: Should update failure status
        """
        await failure_analyzer.initialize()
        
        resolution_info = {
            "resolved_by": "automatic_retry",
            "resolution_time": datetime.now(),
            "fix_applied": "increased_timeout",
        }
        
        await failure_analyzer.resolve_failure(sample_failure_report.id, resolution_info)
        
        # Should have stored resolution memory
        failure_analyzer.memory_curator.store_memory.assert_called()

    @pytest.mark.asyncio
    async def test_failure_trend_analysis(
        self, failure_analyzer: FailureAnalyzer, mock_memory_curator: AsyncMock
    ) -> None:
        """Test analyzing failure trends over time.
        
        Given: Historical failure data
        When: Trend analysis is performed
        Then: Should identify trends
        """
        await failure_analyzer.initialize()
        
        # Mock trending failure data
        from packages.learning.memory_curator import Memory
        trend_memories = []
        for i in range(30):  # 30 days of data
            trend_memories.append(
                Memory(
                    id=f"trend_mem_{i}",
                    type="failure_report",
                    timestamp=datetime.now() - timedelta(days=i),
                    data={"failure_type": "execution_error"},
                    metadata={},
                )
            )
        mock_memory_curator.search_memories.return_value = trend_memories
        
        trends = await failure_analyzer.analyze_failure_trends(days=30)
        
        assert isinstance(trends, dict)
        assert "trend_direction" in trends
        assert "failure_rate" in trends


class TestFailureAnalyzerIntegration:
    """Integration tests for failure analyzer system."""

    @pytest.mark.asyncio
    async def test_full_failure_analysis_workflow(
        self, mock_memory_curator: AsyncMock
    ) -> None:
        """Test complete failure analysis workflow.
        
        Given: Failure analyzer with multiple failures
        When: Complete analysis workflow is executed
        Then: Should record, analyze, and provide insights
        """
        analyzer = FailureAnalyzer(memory_curator=mock_memory_curator)
        await analyzer.initialize()
        
        # Record multiple failures
        failures = [
            FailureReport(
                id=f"workflow_fail_{i}",
                timestamp=datetime.now() - timedelta(hours=i),
                failure_type=FailureType.EXECUTION_ERROR,
                component="test_runner",
                error_message=f"Timeout error {i}",
                context={"environment": "staging"},
            )
            for i in range(5)
        ]
        
        for failure in failures:
            await analyzer.record_failure(failure)
        
        # Analyze patterns
        patterns = await analyzer.analyze_failure_patterns()
        
        # Get statistics
        stats = await analyzer.get_failure_statistics()
        
        # Generate recommendations
        recommendations = await analyzer.generate_prevention_recommendations()
        
        # Verify workflow completed
        assert isinstance(patterns, list)
        assert isinstance(stats, dict)
        assert isinstance(recommendations, list)

    @pytest.mark.asyncio
    async def test_concurrent_failure_analysis(
        self, mock_memory_curator: AsyncMock
    ) -> None:
        """Test concurrent failure analysis operations.
        
        Given: Multiple failure reports
        When: Failures are processed concurrently
        Then: Should handle concurrency correctly
        """
        analyzer = FailureAnalyzer(memory_curator=mock_memory_curator)
        await analyzer.initialize()
        
        # Create multiple failures
        failures = [
            FailureReport(
                id=f"concurrent_fail_{i}",
                timestamp=datetime.now(),
                failure_type=FailureType.EXECUTION_ERROR,
                component=f"component_{i % 3}",
                error_message=f"Error {i}",
                context={},
            )
            for i in range(10)
        ]
        
        # Process concurrently
        tasks = [analyzer.record_failure(failure) for failure in failures]
        await asyncio.gather(*tasks)
        
        # Verify all were processed
        assert mock_memory_curator.store_memory.call_count == 10

    @pytest.mark.asyncio
    async def test_failure_analysis_performance(
        self, mock_memory_curator: AsyncMock
    ) -> None:
        """Test failure analyzer performance with large datasets.
        
        Given: Large number of failures
        When: Analysis is performed
        Then: Should maintain reasonable performance
        """
        import time
        
        analyzer = FailureAnalyzer(memory_curator=mock_memory_curator)
        await analyzer.initialize()
        
        # Mock large dataset
        from packages.learning.memory_curator import Memory
        large_dataset = [
            Memory(
                id=f"perf_mem_{i}",
                type="failure_report",
                timestamp=datetime.now() - timedelta(hours=i),
                data={
                    "failure_type": "execution_error",
                    "component": f"comp_{i % 10}",
                    "error_message": f"Error {i}",
                },
                metadata={},
            )
            for i in range(1000)
        ]
        mock_memory_curator.search_memories.return_value = large_dataset
        
        # Test analysis performance
        start_time = time.time()
        patterns = await analyzer.analyze_failure_patterns()
        analysis_time = time.time() - start_time
        
        # Basic performance assertion
        assert analysis_time < 10.0  # Should complete in under 10 seconds
        assert isinstance(patterns, list)


# Property-based testing
# Note: Property-based testing with hypothesis would go here
# Commented out to avoid optional dependency issues

class TestFailureAnalyzerProperties:
    """Property-based tests for failure analyzer system."""

    def test_pattern_confidence_properties(
        self,
        frequency: int,
        total_failures: int,
    ) -> None:
        """Test pattern confidence calculation properties.
        
        Given: Any valid frequency and total failure counts
        When: Confidence is calculated
        Then: Should return valid confidence score
        """
        # Ensure frequency doesn't exceed total
        frequency = min(frequency, total_failures)
        
        analyzer = FailureAnalyzer(memory_curator=AsyncMock())
        confidence = analyzer._calculate_pattern_confidence(frequency, total_failures)
        
        assert 0.0 <= confidence <= 1.0
        
        # Higher frequency should generally mean higher confidence
        if frequency == total_failures:
            assert confidence > 0.8  # Perfect pattern should have high confidence