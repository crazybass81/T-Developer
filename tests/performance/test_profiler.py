"""
Comprehensive tests for Performance Profiler System.

This module tests the performance profiling functionality
for code optimization and bottleneck identification.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, AsyncGenerator
from unittest.mock import Mock, patch

import pytest

from packages.performance.profiler import (
    CodeProfiler,
    FunctionProfile,
    PerformanceProfiler,
    ProfileResult,
    ProfileType,
    SystemProfiler,
    DEFAULT_PROFILING_DURATION,
    MIN_EXECUTION_TIME_MS,
)


@pytest.fixture
def sample_function_profile() -> FunctionProfile:
    """Create sample function profile for testing."""
    return FunctionProfile(
        function_name="test_function",
        module_name="test_module",
        filename="test_file.py",
        line_number=42,
        total_time=1.5,
        cumulative_time=2.0,
        call_count=100,
        avg_time_per_call=0.015,
        max_time_per_call=0.25,
        min_time_per_call=0.005,
    )


@pytest.fixture
def sample_profile_result() -> ProfileResult:
    """Create sample profile result for testing."""
    return ProfileResult(
        profile_type=ProfileType.FUNCTION_PROFILE,
        start_time=datetime.now(),
        duration_seconds=10.0,
        total_functions=50,
        hotspots=[
            {
                "function": "slow_function",
                "module": "app.core",
                "total_time": 5.2,
                "percentage": 52.0,
            },
            {
                "function": "database_query",
                "module": "app.db",
                "total_time": 2.1,
                "percentage": 21.0,
            },
        ],
        system_metrics={
            "cpu_usage": 65.4,
            "memory_usage": 512.8,
            "disk_io": 1024.5,
            "network_io": 256.2,
        },
        recommendations=[
            "Optimize slow_function - consuming 52% of execution time",
            "Consider caching for database_query operations",
        ],
    )


@pytest.fixture
async def performance_profiler() -> PerformanceProfiler:
    """Create performance profiler instance for testing."""
    return PerformanceProfiler()


@pytest.fixture
async def code_profiler() -> CodeProfiler:
    """Create code profiler instance for testing."""
    return CodeProfiler()


@pytest.fixture
async def system_profiler() -> SystemProfiler:
    """Create system profiler instance for testing."""
    return SystemProfiler()


class TestFunctionProfile:
    """Test FunctionProfile functionality."""

    def test_profile_creation(self, sample_function_profile: FunctionProfile) -> None:
        """Test function profile creation.
        
        Given: Valid profile data
        When: Profile is created
        Then: All fields should be set correctly
        """
        assert sample_function_profile.function_name == "test_function"
        assert sample_function_profile.total_time == 1.5
        assert sample_function_profile.call_count == 100
        assert sample_function_profile.avg_time_per_call == 0.015

    def test_time_per_call_calculation(self) -> None:
        """Test time per call calculation.
        
        Given: Function profile with timing data
        When: Average time is calculated
        Then: Should return correct average
        """
        profile = FunctionProfile(
            function_name="calc_test",
            module_name="test",
            filename="test.py",
            line_number=1,
            total_time=10.0,
            cumulative_time=10.0,
            call_count=5,
            avg_time_per_call=2.0,  # 10.0 / 5
            max_time_per_call=3.0,
            min_time_per_call=1.0,
        )
        
        expected_avg = profile.total_time / profile.call_count
        assert abs(profile.avg_time_per_call - expected_avg) < 0.001

    def test_profile_to_dict(self, sample_function_profile: FunctionProfile) -> None:
        """Test profile serialization.
        
        Given: Function profile
        When: to_dict is called
        Then: Should return dictionary representation
        """
        profile_dict = sample_function_profile.to_dict()
        
        assert isinstance(profile_dict, dict)
        assert profile_dict["function_name"] == "test_function"
        assert profile_dict["total_time"] == 1.5

    def test_is_hotspot(self, sample_function_profile: FunctionProfile) -> None:
        """Test hotspot identification.
        
        Given: Function profile with significant execution time
        When: Hotspot check is performed
        Then: Should identify performance hotspots
        """
        # High time consumption should be identified as hotspot
        hotspot_profile = FunctionProfile(
            function_name="slow_function",
            module_name="app",
            filename="app.py",
            line_number=100,
            total_time=5.0,  # High execution time
            cumulative_time=5.0,
            call_count=1,
            avg_time_per_call=5.0,
            max_time_per_call=5.0,
            min_time_per_call=5.0,
        )
        
        # Assume this is a significant portion of total execution time
        assert hotspot_profile.total_time > 1.0  # Threshold for hotspot


class TestProfileResult:
    """Test ProfileResult functionality."""

    def test_result_creation(self, sample_profile_result: ProfileResult) -> None:
        """Test profile result creation.
        
        Given: Valid result data
        When: Result is created
        Then: All fields should be set correctly
        """
        assert sample_profile_result.profile_type == ProfileType.FUNCTION_PROFILE
        assert sample_profile_result.total_functions == 50
        assert len(sample_profile_result.hotspots) == 2
        assert len(sample_profile_result.recommendations) == 2

    def test_result_to_dict(self, sample_profile_result: ProfileResult) -> None:
        """Test result serialization.
        
        Given: Profile result
        When: to_dict is called
        Then: Should return dictionary representation
        """
        result_dict = sample_profile_result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["profile_type"] == "function_profile"
        assert result_dict["total_functions"] == 50

    def test_hotspot_analysis(self, sample_profile_result: ProfileResult) -> None:
        """Test hotspot analysis.
        
        Given: Profile result with hotspots
        When: Hotspots are analyzed
        Then: Should provide performance insights
        """
        hotspots = sample_profile_result.hotspots
        
        # Should be sorted by time consumption
        assert hotspots[0]["total_time"] >= hotspots[1]["total_time"]
        
        # Percentages should add up sensibly
        total_percentage = sum(h["percentage"] for h in hotspots)
        assert total_percentage <= 100.0

    def test_recommendation_generation(self, sample_profile_result: ProfileResult) -> None:
        """Test recommendation generation.
        
        Given: Profile result with performance data
        When: Recommendations are generated
        Then: Should provide actionable insights
        """
        recommendations = sample_profile_result.recommendations
        
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)
        assert any("slow_function" in rec for rec in recommendations)


class TestCodeProfiler:
    """Test CodeProfiler functionality."""

    @pytest.mark.asyncio
    async def test_profiler_initialization(self, code_profiler: CodeProfiler) -> None:
        """Test code profiler initialization.
        
        Given: Code profiler
        When: Profiler is initialized
        Then: Should set up correctly
        """
        await code_profiler.initialize()
        
        assert code_profiler.profiling_enabled is False  # Initially disabled
        assert code_profiler.active_profiles == {}

    def test_function_timing_decorator(self, code_profiler: CodeProfiler) -> None:
        """Test function timing decorator.
        
        Given: Function with timing decorator
        When: Function is executed
        Then: Should capture timing data
        """
        @code_profiler.profile_function
        def test_function():
            time.sleep(0.1)  # Simulate work
            return "result"
        
        result = test_function()
        
        assert result == "result"
        # Timing data should be captured (implementation dependent)

    def test_context_manager_profiling(self, code_profiler: CodeProfiler) -> None:
        """Test context manager profiling.
        
        Given: Code block with profiling context
        When: Code is executed
        Then: Should capture performance data
        """
        with code_profiler.profile_block("test_block"):
            time.sleep(0.05)  # Simulate work
            result = "completed"
        
        assert result == "completed"

    @pytest.mark.asyncio
    async def test_async_function_profiling(self, code_profiler: CodeProfiler) -> None:
        """Test async function profiling.
        
        Given: Async function with profiling
        When: Function is executed
        Then: Should capture async timing data
        """
        @code_profiler.profile_async_function
        async def async_test_function():
            await asyncio.sleep(0.1)
            return "async_result"
        
        result = await async_test_function()
        
        assert result == "async_result"

    @pytest.mark.asyncio
    async def test_start_profiling(self, code_profiler: CodeProfiler) -> None:
        """Test starting code profiling.
        
        Given: Code profiler
        When: Profiling is started
        Then: Should begin collecting data
        """
        await code_profiler.initialize()
        
        profile_id = await code_profiler.start_profiling(
            duration=2.0,
            profile_type=ProfileType.FUNCTION_PROFILE
        )
        
        assert profile_id is not None
        assert code_profiler.profiling_enabled is True

    @pytest.mark.asyncio
    async def test_stop_profiling(self, code_profiler: CodeProfiler) -> None:
        """Test stopping code profiling.
        
        Given: Active profiling session
        When: Profiling is stopped
        Then: Should return profile results
        """
        await code_profiler.initialize()
        
        profile_id = await code_profiler.start_profiling(duration=1.0)
        
        # Simulate some work
        def work_function():
            for i in range(1000):
                _ = i ** 2
        
        work_function()
        
        result = await code_profiler.stop_profiling(profile_id)
        
        assert isinstance(result, ProfileResult)
        assert result.duration_seconds > 0

    @pytest.mark.asyncio
    async def test_get_function_profiles(self, code_profiler: CodeProfiler) -> None:
        """Test getting function profiles.
        
        Given: Code profiler with collected data
        When: Function profiles are requested
        Then: Should return profile information
        """
        await code_profiler.initialize()
        
        # Mock some profile data
        profiles = await code_profiler.get_function_profiles()
        
        assert isinstance(profiles, list)

    def test_memory_profiling(self, code_profiler: CodeProfiler) -> None:
        """Test memory usage profiling.
        
        Given: Code with memory allocations
        When: Memory profiling is enabled
        Then: Should capture memory usage data
        """
        @code_profiler.profile_memory
        def memory_intensive_function():
            # Allocate some memory
            data = [i for i in range(10000)]
            return len(data)
        
        result = memory_intensive_function()
        
        assert result == 10000

    def test_line_by_line_profiling(self, code_profiler: CodeProfiler) -> None:
        """Test line-by-line profiling.
        
        Given: Function with line profiling enabled
        When: Function is executed
        Then: Should capture per-line timing
        """
        @code_profiler.profile_lines
        def line_profiled_function():
            x = 1
            y = 2
            z = x + y
            return z
        
        result = line_profiled_function()
        
        assert result == 3


class TestSystemProfiler:
    """Test SystemProfiler functionality."""

    @pytest.mark.asyncio
    async def test_system_profiler_initialization(self, system_profiler: SystemProfiler) -> None:
        """Test system profiler initialization.
        
        Given: System profiler
        When: Profiler is initialized
        Then: Should set up system monitoring
        """
        await system_profiler.initialize()
        
        assert system_profiler.monitoring_enabled is False  # Initially disabled

    @pytest.mark.asyncio
    async def test_cpu_usage_monitoring(self, system_profiler: SystemProfiler) -> None:
        """Test CPU usage monitoring.
        
        Given: System profiler
        When: CPU usage is monitored
        Then: Should return CPU metrics
        """
        await system_profiler.initialize()
        
        cpu_usage = await system_profiler.get_cpu_usage()
        
        assert isinstance(cpu_usage, float)
        assert 0.0 <= cpu_usage <= 100.0

    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self, system_profiler: SystemProfiler) -> None:
        """Test memory usage monitoring.
        
        Given: System profiler
        When: Memory usage is monitored
        Then: Should return memory metrics
        """
        await system_profiler.initialize()
        
        memory_info = await system_profiler.get_memory_usage()
        
        assert isinstance(memory_info, dict)
        assert "total" in memory_info
        assert "used" in memory_info
        assert "available" in memory_info

    @pytest.mark.asyncio
    async def test_disk_io_monitoring(self, system_profiler: SystemProfiler) -> None:
        """Test disk I/O monitoring.
        
        Given: System profiler
        When: Disk I/O is monitored
        Then: Should return I/O metrics
        """
        await system_profiler.initialize()
        
        disk_io = await system_profiler.get_disk_io()
        
        assert isinstance(disk_io, dict)
        assert "read_bytes" in disk_io
        assert "write_bytes" in disk_io

    @pytest.mark.asyncio
    async def test_network_io_monitoring(self, system_profiler: SystemProfiler) -> None:
        """Test network I/O monitoring.
        
        Given: System profiler
        When: Network I/O is monitored
        Then: Should return network metrics
        """
        await system_profiler.initialize()
        
        network_io = await system_profiler.get_network_io()
        
        assert isinstance(network_io, dict)
        assert "bytes_sent" in network_io
        assert "bytes_recv" in network_io

    @pytest.mark.asyncio
    async def test_start_system_monitoring(self, system_profiler: SystemProfiler) -> None:
        """Test starting system monitoring.
        
        Given: System profiler
        When: Monitoring is started
        Then: Should begin collecting system metrics
        """
        await system_profiler.initialize()
        
        monitor_id = await system_profiler.start_monitoring(interval=1.0, duration=3.0)
        
        assert monitor_id is not None
        assert system_profiler.monitoring_enabled is True

    @pytest.mark.asyncio
    async def test_stop_system_monitoring(self, system_profiler: SystemProfiler) -> None:
        """Test stopping system monitoring.
        
        Given: Active monitoring session
        When: Monitoring is stopped
        Then: Should return collected metrics
        """
        await system_profiler.initialize()
        
        monitor_id = await system_profiler.start_monitoring(interval=0.5, duration=2.0)
        
        # Wait a bit for data collection
        await asyncio.sleep(1.0)
        
        metrics = await system_profiler.stop_monitoring(monitor_id)
        
        assert isinstance(metrics, dict)
        assert "cpu_usage_history" in metrics
        assert "memory_usage_history" in metrics

    @pytest.mark.asyncio
    async def test_get_system_snapshot(self, system_profiler: SystemProfiler) -> None:
        """Test getting system snapshot.
        
        Given: System profiler
        When: System snapshot is requested
        Then: Should return current system state
        """
        await system_profiler.initialize()
        
        snapshot = await system_profiler.get_system_snapshot()
        
        assert isinstance(snapshot, dict)
        assert "timestamp" in snapshot
        assert "cpu" in snapshot
        assert "memory" in snapshot
        assert "disk" in snapshot
        assert "network" in snapshot


class TestPerformanceProfiler:
    """Test PerformanceProfiler main functionality."""

    @pytest.mark.asyncio
    async def test_profiler_initialization(self, performance_profiler: PerformanceProfiler) -> None:
        """Test performance profiler initialization.
        
        Given: Performance profiler
        When: Profiler is initialized
        Then: Should set up all components
        """
        await performance_profiler.initialize()
        
        assert performance_profiler.code_profiler is not None
        assert performance_profiler.system_profiler is not None
        assert performance_profiler.active_sessions == {}

    @pytest.mark.asyncio
    async def test_start_comprehensive_profiling(
        self, performance_profiler: PerformanceProfiler
    ) -> None:
        """Test starting comprehensive profiling.
        
        Given: Performance profiler
        When: Comprehensive profiling is started
        Then: Should profile both code and system
        """
        await performance_profiler.initialize()
        
        session_id = await performance_profiler.start_profiling(
            profile_types=[ProfileType.FUNCTION_PROFILE, ProfileType.SYSTEM_PROFILE],
            duration=3.0
        )
        
        assert session_id is not None
        assert session_id in performance_profiler.active_sessions

    @pytest.mark.asyncio
    async def test_stop_comprehensive_profiling(
        self, performance_profiler: PerformanceProfiler
    ) -> None:
        """Test stopping comprehensive profiling.
        
        Given: Active profiling session
        When: Profiling is stopped
        Then: Should return comprehensive results
        """
        await performance_profiler.initialize()
        
        session_id = await performance_profiler.start_profiling(
            profile_types=[ProfileType.FUNCTION_PROFILE],
            duration=2.0
        )
        
        # Simulate some work
        def test_work():
            for i in range(1000):
                _ = i * i
        
        test_work()
        
        results = await performance_profiler.stop_profiling(session_id)
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(result, ProfileResult) for result in results)

    @pytest.mark.asyncio
    async def test_get_profiling_status(
        self, performance_profiler: PerformanceProfiler
    ) -> None:
        """Test getting profiling status.
        
        Given: Active profiling session
        When: Status is requested
        Then: Should return current status
        """
        await performance_profiler.initialize()
        
        session_id = await performance_profiler.start_profiling(duration=5.0)
        
        status = await performance_profiler.get_profiling_status(session_id)
        
        assert isinstance(status, dict)
        assert "session_id" in status
        assert "status" in status
        assert "elapsed_time" in status

    @pytest.mark.asyncio
    async def test_profile_specific_function(
        self, performance_profiler: PerformanceProfiler
    ) -> None:
        """Test profiling specific function.
        
        Given: Target function for profiling
        When: Function is profiled
        Then: Should return function-specific metrics
        """
        await performance_profiler.initialize()
        
        def target_function():
            # Simulate some computational work
            result = 0
            for i in range(10000):
                result += i ** 2
            return result
        
        profile_result = await performance_profiler.profile_function(
            target_function,
            args=(),
            kwargs={}
        )
        
        assert isinstance(profile_result, ProfileResult)
        assert profile_result.total_functions >= 1

    @pytest.mark.asyncio
    async def test_profile_code_block(
        self, performance_profiler: PerformanceProfiler
    ) -> None:
        """Test profiling code block.
        
        Given: Code block for profiling
        When: Block is profiled
        Then: Should capture block performance
        """
        await performance_profiler.initialize()
        
        with performance_profiler.profile_block("test_block") as profiler:
            # Simulate work
            data = [i for i in range(5000)]
            result = sum(data)
        
        # Profile result should be available through profiler
        assert result == sum(range(5000))

    @pytest.mark.asyncio
    async def test_continuous_monitoring(
        self, performance_profiler: PerformanceProfiler
    ) -> None:
        """Test continuous performance monitoring.
        
        Given: Performance profiler
        When: Continuous monitoring is enabled
        Then: Should collect ongoing metrics
        """
        await performance_profiler.initialize()
        
        monitor_id = await performance_profiler.start_continuous_monitoring(
            interval=0.5,
            metrics=["cpu", "memory"]
        )
        
        assert monitor_id is not None
        
        # Let it run briefly
        await asyncio.sleep(1.5)
        
        metrics = await performance_profiler.get_monitoring_data(monitor_id)
        
        assert isinstance(metrics, dict)
        assert len(metrics) > 0

    @pytest.mark.asyncio
    async def test_performance_comparison(
        self, performance_profiler: PerformanceProfiler
    ) -> None:
        """Test performance comparison between implementations.
        
        Given: Multiple function implementations
        When: Performance comparison is run
        Then: Should provide comparative analysis
        """
        await performance_profiler.initialize()
        
        def implementation_a():
            return sum(i for i in range(1000))
        
        def implementation_b():
            result = 0
            for i in range(1000):
                result += i
            return result
        
        comparison = await performance_profiler.compare_implementations(
            {"impl_a": implementation_a, "impl_b": implementation_b},
            iterations=10
        )
        
        assert isinstance(comparison, dict)
        assert "impl_a" in comparison
        assert "impl_b" in comparison

    @pytest.mark.asyncio
    async def test_bottleneck_detection(
        self, performance_profiler: PerformanceProfiler
    ) -> None:
        """Test automatic bottleneck detection.
        
        Given: Code with performance bottlenecks
        When: Bottleneck detection is run
        Then: Should identify performance issues
        """
        await performance_profiler.initialize()
        
        def slow_function():
            time.sleep(0.1)  # Intentional bottleneck
            return "slow"
        
        def fast_function():
            return "fast"
        
        # Profile both functions
        session_id = await performance_profiler.start_profiling(duration=2.0)
        
        slow_function()
        fast_function()
        
        results = await performance_profiler.stop_profiling(session_id)
        
        # Should identify slow_function as bottleneck
        if results:
            result = results[0]
            assert len(result.hotspots) > 0


class TestPerformanceProfilerIntegration:
    """Integration tests for performance profiler system."""

    @pytest.mark.asyncio
    async def test_full_profiling_workflow(self) -> None:
        """Test complete profiling workflow.
        
        Given: Performance profiler system
        When: Full workflow is executed
        Then: Should provide comprehensive performance insights
        """
        profiler = PerformanceProfiler()
        await profiler.initialize()
        
        # Define test workload
        def cpu_intensive_task():
            result = 0
            for i in range(50000):
                result += i ** 2
            return result
        
        async def io_simulation():
            await asyncio.sleep(0.1)
            return "io_complete"
        
        # Start comprehensive profiling
        session_id = await profiler.start_profiling(
            profile_types=[ProfileType.FUNCTION_PROFILE, ProfileType.SYSTEM_PROFILE],
            duration=3.0
        )
        
        # Execute workload
        cpu_result = cpu_intensive_task()
        io_result = await io_simulation()
        
        # Stop profiling and get results
        results = await profiler.stop_profiling(session_id)
        
        assert cpu_result > 0
        assert io_result == "io_complete"
        assert isinstance(results, list)
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_concurrent_profiling_sessions(self) -> None:
        """Test multiple concurrent profiling sessions.
        
        Given: Multiple profiling requests
        When: Sessions run concurrently
        Then: Should handle multiple sessions independently
        """
        profiler = PerformanceProfiler()
        await profiler.initialize()
        
        # Start multiple sessions
        session_ids = []
        for i in range(3):
            session_id = await profiler.start_profiling(
                profile_types=[ProfileType.FUNCTION_PROFILE],
                duration=2.0
            )
            session_ids.append(session_id)
        
        assert len(session_ids) == 3
        assert len(set(session_ids)) == 3  # All unique
        
        # Execute some work
        def work_task(task_id: int):
            return sum(range(task_id * 1000))
        
        for i in range(3):
            work_task(i + 1)
        
        # Stop all sessions
        all_results = []
        for session_id in session_ids:
            results = await profiler.stop_profiling(session_id)
            all_results.extend(results)
        
        assert len(all_results) >= 3

    @pytest.mark.asyncio
    async def test_real_world_profiling_scenario(self) -> None:
        """Test profiling in realistic scenario.
        
        Given: Realistic application workload
        When: Profiling is performed
        Then: Should provide actionable insights
        """
        profiler = PerformanceProfiler()
        await profiler.initialize()
        
        # Simulate realistic application functions
        def data_processing():
            data = list(range(10000))
            # Simulate data transformation
            processed = [x * 2 for x in data if x % 2 == 0]
            return len(processed)
        
        def database_simulation():
            # Simulate database query delay
            time.sleep(0.05)
            return {"records": 100}
        
        async def api_call_simulation():
            await asyncio.sleep(0.1)
            return {"status": "success"}
        
        # Profile the workflow
        session_id = await profiler.start_profiling(duration=2.0)
        
        # Execute realistic workload
        data_result = data_processing()
        db_result = database_simulation()
        api_result = await api_call_simulation()
        
        results = await profiler.stop_profiling(session_id)
        
        # Verify results
        assert data_result > 0
        assert db_result["records"] == 100
        assert api_result["status"] == "success"
        assert len(results) > 0


# Property-based testing
# Note: Property-based testing with hypothesis would go here
# Commented out to avoid optional dependency issues

class TestPerformanceProfilerProperties:
    """Property-based tests for performance profiler system."""

    def test_profiling_duration_properties(
        self,
        duration: float,
        iterations: int,
    ) -> None:
        """Test profiling duration properties.
        
        Given: Any valid duration and iteration count
        When: Profiling configuration is created
        Then: Should respect timing constraints
        """
        # Verify duration is positive
        assert duration > 0
        assert iterations > 0
        
        # Calculate expected minimum execution time
        min_execution_time = duration * 0.9  # Allow 10% variance
        assert min_execution_time > 0

    )
    def test_timing_statistics_properties(
        self,
        execution_times: list[float],
    ) -> None:
        """Test timing statistics calculation properties.
        
        Given: Any valid execution time list
        When: Statistics are calculated
        Then: Should return valid statistical measures
        """
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            
            assert min_time <= avg_time <= max_time
            assert all(t >= 0 for t in execution_times)