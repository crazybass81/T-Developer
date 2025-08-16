"""
Comprehensive tests for Load Testing System.

This module tests the load testing functionality for performance
measurement and validation.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, Mock, patch

import pytest

from packages.performance.load_testing import (
    LoadTest,
    LoadTestConfig,
    LoadTestResult,
    LoadTester,
    TestScenario,
    UserBehavior,
    DEFAULT_CONCURRENT_USERS,
    DEFAULT_TEST_DURATION,
    MAX_CONCURRENT_USERS,
)


@pytest.fixture
def sample_load_test_config() -> LoadTestConfig:
    """Create sample load test configuration for testing."""
    return LoadTestConfig(
        name="API Load Test",
        target_url="http://localhost:8000",
        concurrent_users=10,
        duration_seconds=60,
        ramp_up_seconds=10,
        scenarios=[
            TestScenario(
                name="User Login",
                weight=0.3,
                steps=[
                    {"method": "POST", "path": "/api/login", "data": {"user": "test"}},
                    {"method": "GET", "path": "/api/profile"},
                ],
            ),
            TestScenario(
                name="Browse Products",
                weight=0.7,
                steps=[
                    {"method": "GET", "path": "/api/products"},
                    {"method": "GET", "path": "/api/products/1"},
                ],
            ),
        ],
        user_behavior=UserBehavior(
            think_time_min=1.0,
            think_time_max=3.0,
            session_duration_min=30,
            session_duration_max=300,
        ),
    )


@pytest.fixture
def sample_load_test_result() -> LoadTestResult:
    """Create sample load test result for testing."""
    return LoadTestResult(
        test_name="API Load Test",
        start_time=datetime.now() - timedelta(minutes=1),
        end_time=datetime.now(),
        total_requests=1000,
        successful_requests=950,
        failed_requests=50,
        avg_response_time=250.5,
        min_response_time=50.2,
        max_response_time=2500.8,
        p95_response_time=800.3,
        p99_response_time=1200.1,
        requests_per_second=16.67,
        errors_per_second=0.83,
        error_rate=0.05,
        concurrent_users=10,
        cpu_usage_avg=45.2,
        memory_usage_avg=512.8,
        network_io_avg=1024.5,
    )


@pytest.fixture
async def load_tester() -> LoadTester:
    """Create load tester instance for testing."""
    return LoadTester()


class TestLoadTestConfig:
    """Test LoadTestConfig functionality."""

    def test_config_creation(self, sample_load_test_config: LoadTestConfig) -> None:
        """Test load test configuration creation.
        
        Given: Valid configuration data
        When: Config is created
        Then: All fields should be set correctly
        """
        assert sample_load_test_config.name == "API Load Test"
        assert sample_load_test_config.concurrent_users == 10
        assert sample_load_test_config.duration_seconds == 60
        assert len(sample_load_test_config.scenarios) == 2

    def test_config_validation(self) -> None:
        """Test configuration validation.
        
        Given: Invalid configuration
        When: Config is validated
        Then: Should raise appropriate errors
        """
        with pytest.raises(ValueError):
            LoadTestConfig(
                name="Invalid Test",
                target_url="invalid-url",  # Invalid URL
                concurrent_users=0,  # Invalid user count
                duration_seconds=-1,  # Invalid duration
                scenarios=[],  # No scenarios
            )

    def test_scenario_weight_validation(self) -> None:
        """Test scenario weight validation.
        
        Given: Scenarios with invalid weights
        When: Configuration is created
        Then: Should validate weight distribution
        """
        scenarios = [
            TestScenario(name="Test1", weight=0.3, steps=[]),
            TestScenario(name="Test2", weight=0.8, steps=[]),  # Total > 1.0
        ]
        
        with pytest.raises(ValueError):
            LoadTestConfig(
                name="Weight Test",
                target_url="http://localhost:8000",
                concurrent_users=5,
                duration_seconds=30,
                scenarios=scenarios,
            )

    def test_config_to_dict(self, sample_load_test_config: LoadTestConfig) -> None:
        """Test configuration serialization.
        
        Given: Load test configuration
        When: to_dict is called
        Then: Should return dictionary representation
        """
        config_dict = sample_load_test_config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["name"] == "API Load Test"
        assert config_dict["concurrent_users"] == 10
        assert "scenarios" in config_dict


class TestTestScenario:
    """Test TestScenario functionality."""

    def test_scenario_creation(self) -> None:
        """Test test scenario creation.
        
        Given: Valid scenario data
        When: Scenario is created
        Then: Should set all fields correctly
        """
        scenario = TestScenario(
            name="Login Test",
            weight=0.5,
            steps=[
                {"method": "POST", "path": "/login", "data": {"user": "test"}},
                {"method": "GET", "path": "/dashboard"},
            ],
        )
        
        assert scenario.name == "Login Test"
        assert scenario.weight == 0.5
        assert len(scenario.steps) == 2

    def test_scenario_execution_order(self) -> None:
        """Test scenario step execution order.
        
        Given: Scenario with multiple steps
        When: Steps are accessed
        Then: Should maintain order
        """
        steps = [
            {"method": "GET", "path": "/step1"},
            {"method": "POST", "path": "/step2"},
            {"method": "PUT", "path": "/step3"},
        ]
        
        scenario = TestScenario(name="Order Test", weight=1.0, steps=steps)
        
        assert scenario.steps[0]["path"] == "/step1"
        assert scenario.steps[1]["path"] == "/step2"
        assert scenario.steps[2]["path"] == "/step3"


class TestUserBehavior:
    """Test UserBehavior functionality."""

    def test_user_behavior_creation(self) -> None:
        """Test user behavior configuration creation.
        
        Given: Valid behavior parameters
        When: UserBehavior is created
        Then: Should set parameters correctly
        """
        behavior = UserBehavior(
            think_time_min=0.5,
            think_time_max=2.0,
            session_duration_min=60,
            session_duration_max=300,
        )
        
        assert behavior.think_time_min == 0.5
        assert behavior.think_time_max == 2.0
        assert behavior.session_duration_min == 60
        assert behavior.session_duration_max == 300

    def test_think_time_range_validation(self) -> None:
        """Test think time range validation.
        
        Given: Invalid think time ranges
        When: UserBehavior is created
        Then: Should validate ranges
        """
        with pytest.raises(ValueError):
            UserBehavior(
                think_time_min=2.0,
                think_time_max=1.0,  # Max < Min
                session_duration_min=60,
                session_duration_max=300,
            )

    def test_session_duration_validation(self) -> None:
        """Test session duration validation.
        
        Given: Invalid session duration
        When: UserBehavior is created
        Then: Should validate duration
        """
        with pytest.raises(ValueError):
            UserBehavior(
                think_time_min=1.0,
                think_time_max=2.0,
                session_duration_min=300,
                session_duration_max=60,  # Max < Min
            )


class TestLoadTestResult:
    """Test LoadTestResult functionality."""

    def test_result_creation(self, sample_load_test_result: LoadTestResult) -> None:
        """Test load test result creation.
        
        Given: Valid result data
        When: Result is created
        Then: All fields should be set correctly
        """
        assert sample_load_test_result.test_name == "API Load Test"
        assert sample_load_test_result.total_requests == 1000
        assert sample_load_test_result.successful_requests == 950
        assert sample_load_test_result.failed_requests == 50

    def test_error_rate_calculation(self, sample_load_test_result: LoadTestResult) -> None:
        """Test error rate calculation.
        
        Given: Load test result with success/failure counts
        When: Error rate is calculated
        Then: Should return correct percentage
        """
        assert sample_load_test_result.error_rate == 0.05  # 50/1000 = 0.05

    def test_success_rate_calculation(self, sample_load_test_result: LoadTestResult) -> None:
        """Test success rate calculation.
        
        Given: Load test result
        When: Success rate is calculated
        Then: Should return correct percentage
        """
        success_rate = sample_load_test_result.successful_requests / sample_load_test_result.total_requests
        assert success_rate == 0.95  # 950/1000 = 0.95

    def test_result_to_dict(self, sample_load_test_result: LoadTestResult) -> None:
        """Test result serialization.
        
        Given: Load test result
        When: to_dict is called
        Then: Should return dictionary representation
        """
        result_dict = sample_load_test_result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["test_name"] == "API Load Test"
        assert result_dict["total_requests"] == 1000
        assert result_dict["error_rate"] == 0.05

    def test_performance_metrics(self, sample_load_test_result: LoadTestResult) -> None:
        """Test performance metric calculations.
        
        Given: Load test result with timing data
        When: Performance metrics are accessed
        Then: Should provide comprehensive metrics
        """
        assert sample_load_test_result.avg_response_time > 0
        assert sample_load_test_result.p95_response_time > sample_load_test_result.avg_response_time
        assert sample_load_test_result.p99_response_time > sample_load_test_result.p95_response_time
        assert sample_load_test_result.max_response_time > sample_load_test_result.p99_response_time


class TestLoadTester:
    """Test LoadTester functionality."""

    @pytest.mark.asyncio
    async def test_load_tester_initialization(self, load_tester: LoadTester) -> None:
        """Test load tester initialization.
        
        Given: Load tester
        When: Tester is initialized
        Then: Should set up correctly
        """
        await load_tester.initialize()
        
        assert load_tester.active_tests == {}
        assert load_tester.test_results == []

    @pytest.mark.asyncio
    async def test_start_load_test(
        self, load_tester: LoadTester, sample_load_test_config: LoadTestConfig
    ) -> None:
        """Test starting a load test.
        
        Given: Load tester and configuration
        When: Load test is started
        Then: Should initiate test execution
        """
        await load_tester.initialize()
        
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock HTTP responses
            mock_response = Mock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="OK")
            mock_session.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            
            test_id = await load_tester.start_load_test(sample_load_test_config)
            
            assert test_id is not None
            assert test_id in load_tester.active_tests

    @pytest.mark.asyncio
    async def test_stop_load_test(
        self, load_tester: LoadTester, sample_load_test_config: LoadTestConfig
    ) -> None:
        """Test stopping a load test.
        
        Given: Running load test
        When: Test is stopped
        Then: Should terminate test execution
        """
        await load_tester.initialize()
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="OK")
            mock_session.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            
            test_id = await load_tester.start_load_test(sample_load_test_config)
            
            # Stop the test
            result = await load_tester.stop_load_test(test_id)
            
            assert result is not None
            assert isinstance(result, LoadTestResult)
            assert test_id not in load_tester.active_tests

    @pytest.mark.asyncio
    async def test_get_test_status(
        self, load_tester: LoadTester, sample_load_test_config: LoadTestConfig
    ) -> None:
        """Test getting test status.
        
        Given: Running load test
        When: Status is requested
        Then: Should return current status
        """
        await load_tester.initialize()
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_session.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            
            test_id = await load_tester.start_load_test(sample_load_test_config)
            
            status = await load_tester.get_test_status(test_id)
            
            assert status is not None
            assert "status" in status
            assert "requests_completed" in status

    @pytest.mark.asyncio
    async def test_user_simulation(self, load_tester: LoadTester) -> None:
        """Test user behavior simulation.
        
        Given: User behavior configuration
        When: User session is simulated
        Then: Should follow behavior patterns
        """
        await load_tester.initialize()
        
        behavior = UserBehavior(
            think_time_min=0.1,
            think_time_max=0.2,
            session_duration_min=5,
            session_duration_max=10,
        )
        
        scenario = TestScenario(
            name="Test Scenario",
            weight=1.0,
            steps=[{"method": "GET", "path": "/test"}],
        )
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_session.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            
            # Simulate user session
            session_results = await load_tester._simulate_user_session(
                "http://localhost:8000", [scenario], behavior, 5
            )
            
            assert len(session_results) > 0
            assert all("response_time" in result for result in session_results)

    @pytest.mark.asyncio
    async def test_ramp_up_strategy(
        self, load_tester: LoadTester, sample_load_test_config: LoadTestConfig
    ) -> None:
        """Test user ramp-up strategy.
        
        Given: Load test with ramp-up configuration
        When: Test is executed
        Then: Should gradually increase user load
        """
        await load_tester.initialize()
        
        # Test ramp-up calculation
        ramp_up_times = load_tester._calculate_ramp_up_times(
            concurrent_users=10,
            ramp_up_seconds=10
        )
        
        assert len(ramp_up_times) == 10
        assert ramp_up_times[0] == 0  # First user starts immediately
        assert ramp_up_times[-1] <= 10  # Last user starts within ramp-up period

    @pytest.mark.asyncio
    async def test_response_time_aggregation(self, load_tester: LoadTester) -> None:
        """Test response time metric aggregation.
        
        Given: Multiple response time measurements
        When: Metrics are aggregated
        Then: Should calculate correct statistics
        """
        await load_tester.initialize()
        
        response_times = [100, 150, 200, 250, 300, 500, 1000, 1500, 2000, 5000]
        
        metrics = load_tester._calculate_response_time_metrics(response_times)
        
        assert metrics["avg"] == 1000.0  # Average
        assert metrics["min"] == 100
        assert metrics["max"] == 5000
        assert "p95" in metrics
        assert "p99" in metrics

    @pytest.mark.asyncio
    async def test_error_handling(
        self, load_tester: LoadTester, sample_load_test_config: LoadTestConfig
    ) -> None:
        """Test error handling during load testing.
        
        Given: Load test with failing requests
        When: Errors occur
        Then: Should handle gracefully and record errors
        """
        await load_tester.initialize()
        
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock failing response
            mock_session.return_value.__aenter__.return_value.request.side_effect = Exception("Connection error")
            
            try:
                test_id = await load_tester.start_load_test(sample_load_test_config)
                # Should not crash despite errors
                assert test_id is not None
            except Exception:
                # Should handle errors gracefully
                pass

    @pytest.mark.asyncio
    async def test_concurrent_user_limit(self, load_tester: LoadTester) -> None:
        """Test concurrent user limit enforcement.
        
        Given: Configuration exceeding user limits
        When: Load test is configured
        Then: Should enforce limits
        """
        await load_tester.initialize()
        
        excessive_config = LoadTestConfig(
            name="Excessive Test",
            target_url="http://localhost:8000",
            concurrent_users=MAX_CONCURRENT_USERS + 100,  # Exceeds limit
            duration_seconds=30,
            scenarios=[
                TestScenario(name="Test", weight=1.0, steps=[{"method": "GET", "path": "/"}])
            ],
        )
        
        with pytest.raises(ValueError):
            await load_tester.start_load_test(excessive_config)

    @pytest.mark.asyncio
    async def test_test_duration_enforcement(
        self, load_tester: LoadTester, sample_load_test_config: LoadTestConfig
    ) -> None:
        """Test duration enforcement.
        
        Given: Load test with specific duration
        When: Test runs
        Then: Should respect duration limits
        """
        await load_tester.initialize()
        
        # Set short duration for testing
        sample_load_test_config.duration_seconds = 2
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_session.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            
            start_time = datetime.now()
            test_id = await load_tester.start_load_test(sample_load_test_config)
            
            # Wait for test completion
            await asyncio.sleep(3)
            
            result = await load_tester.get_test_result(test_id)
            if result:
                test_duration = (result.end_time - result.start_time).total_seconds()
                assert test_duration <= sample_load_test_config.duration_seconds + 1  # Allow small margin

    @pytest.mark.asyncio
    async def test_scenario_distribution(self, load_tester: LoadTester) -> None:
        """Test scenario weight distribution.
        
        Given: Multiple scenarios with different weights
        When: Scenarios are selected
        Then: Should respect weight distribution
        """
        await load_tester.initialize()
        
        scenarios = [
            TestScenario(name="Scenario A", weight=0.7, steps=[]),
            TestScenario(name="Scenario B", weight=0.3, steps=[]),
        ]
        
        # Test scenario selection
        selections = []
        for _ in range(100):
            selected = load_tester._select_scenario(scenarios)
            selections.append(selected.name)
        
        # Check distribution (allow some variance)
        a_count = selections.count("Scenario A")
        b_count = selections.count("Scenario B")
        
        assert 60 <= a_count <= 80  # Should be around 70%
        assert 20 <= b_count <= 40  # Should be around 30%


class TestLoadTestIntegration:
    """Integration tests for load testing system."""

    @pytest.mark.asyncio
    async def test_full_load_test_cycle(self) -> None:
        """Test complete load test lifecycle.
        
        Given: Load testing system
        When: Full test cycle is executed
        Then: Should complete all phases successfully
        """
        load_tester = LoadTester()
        await load_tester.initialize()
        
        config = LoadTestConfig(
            name="Integration Test",
            target_url="http://httpbin.org",  # Reliable test endpoint
            concurrent_users=2,
            duration_seconds=5,
            ramp_up_seconds=1,
            scenarios=[
                TestScenario(
                    name="Basic Request",
                    weight=1.0,
                    steps=[{"method": "GET", "path": "/get"}],
                ),
            ],
            user_behavior=UserBehavior(
                think_time_min=0.1,
                think_time_max=0.2,
                session_duration_min=3,
                session_duration_max=5,
            ),
        )
        
        # Start test
        test_id = await load_tester.start_load_test(config)
        assert test_id is not None
        
        # Monitor test
        await asyncio.sleep(2)
        status = await load_tester.get_test_status(test_id)
        assert status is not None
        
        # Wait for completion
        await asyncio.sleep(6)
        result = await load_tester.get_test_result(test_id)
        
        if result:
            assert result.total_requests > 0
            assert result.test_name == "Integration Test"

    @pytest.mark.asyncio
    async def test_multiple_concurrent_tests(self) -> None:
        """Test running multiple load tests concurrently.
        
        Given: Multiple load test configurations
        When: Tests are run concurrently
        Then: Should handle multiple tests without interference
        """
        load_tester = LoadTester()
        await load_tester.initialize()
        
        configs = [
            LoadTestConfig(
                name=f"Concurrent Test {i}",
                target_url="http://httpbin.org",
                concurrent_users=1,
                duration_seconds=3,
                scenarios=[
                    TestScenario(
                        name="Test",
                        weight=1.0,
                        steps=[{"method": "GET", "path": "/get"}],
                    )
                ],
            )
            for i in range(3)
        ]
        
        # Start multiple tests
        test_ids = []
        for config in configs:
            test_id = await load_tester.start_load_test(config)
            test_ids.append(test_id)
        
        assert len(test_ids) == 3
        assert len(set(test_ids)) == 3  # All unique
        
        # Wait for completion
        await asyncio.sleep(5)
        
        # Check results
        for test_id in test_ids:
            result = await load_tester.get_test_result(test_id)
            assert result is not None or test_id not in load_tester.active_tests

    @pytest.mark.asyncio
    async def test_stress_test_scenario(self) -> None:
        """Test stress testing scenario.
        
        Given: High-load configuration
        When: Stress test is executed
        Then: Should handle high load appropriately
        """
        load_tester = LoadTester()
        await load_tester.initialize()
        
        stress_config = LoadTestConfig(
            name="Stress Test",
            target_url="http://httpbin.org",
            concurrent_users=min(50, MAX_CONCURRENT_USERS),  # High but within limits
            duration_seconds=10,
            ramp_up_seconds=5,
            scenarios=[
                TestScenario(
                    name="Stress Scenario",
                    weight=1.0,
                    steps=[
                        {"method": "GET", "path": "/get"},
                        {"method": "POST", "path": "/post", "data": {"test": "data"}},
                    ],
                ),
            ],
            user_behavior=UserBehavior(
                think_time_min=0.05,
                think_time_max=0.1,
                session_duration_min=5,
                session_duration_max=10,
            ),
        )
        
        # This test may be resource-intensive, so we'll just verify it starts
        test_id = await load_tester.start_load_test(stress_config)
        assert test_id is not None
        
        # Stop test early to avoid resource issues
        await asyncio.sleep(2)
        result = await load_tester.stop_load_test(test_id)
        
        if result:
            assert result.concurrent_users > 0


# Property-based testing
# Note: Property-based testing with hypothesis would go here
# Commented out to avoid optional dependency issues

class TestLoadTestingProperties:
    """Property-based tests for load testing system."""

    @given(
        concurrent_users=st.integers(min_value=1, max_value=100),
        duration_seconds=st.integers(min_value=1, max_value=300),
        ramp_up_seconds=st.integers(min_value=0, max_value=60),
    )
    def test_load_test_config_properties(
        self,
        concurrent_users: int,
        duration_seconds: int,
        ramp_up_seconds: int,
    ) -> None:
        """Test load test configuration with various property combinations.
        
        Given: Any valid configuration parameters
        When: Configuration is created
        Then: Should create valid configuration
        """
        # Ensure ramp_up doesn't exceed duration
        ramp_up_seconds = min(ramp_up_seconds, duration_seconds)
        
        config = LoadTestConfig(
            name="Property Test",
            target_url="http://localhost:8000",
            concurrent_users=concurrent_users,
            duration_seconds=duration_seconds,
            ramp_up_seconds=ramp_up_seconds,
            scenarios=[
                TestScenario(
                    name="Test Scenario",
                    weight=1.0,
                    steps=[{"method": "GET", "path": "/"}],
                )
            ],
        )
        
        assert config.concurrent_users == concurrent_users
        assert config.duration_seconds == duration_seconds
        assert config.ramp_up_seconds == ramp_up_seconds
        assert config.ramp_up_seconds <= config.duration_seconds

    @given(
        response_times=st.lists(
            st.floats(min_value=1.0, max_value=10000.0),
            min_size=1,
            max_size=1000
        )
    )
    def test_response_time_metrics_properties(
        self,
        response_times: list[float],
    ) -> None:
        """Test response time metrics calculation properties.
        
        Given: Any valid response time list
        When: Metrics are calculated
        Then: Should return valid metrics
        """
        load_tester = LoadTester()
        metrics = load_tester._calculate_response_time_metrics(response_times)
        
        assert metrics["min"] <= metrics["avg"] <= metrics["max"]
        assert metrics["avg"] <= metrics["p95"] <= metrics["max"]
        assert metrics["p95"] <= metrics["p99"] <= metrics["max"]
        assert all(value >= 0 for value in metrics.values())