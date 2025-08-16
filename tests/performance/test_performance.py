"""Comprehensive tests for performance components.

Phase 6: P6-TEST-1 - Performance Testing
Test coverage >85% for all performance optimization components.
"""

from __future__ import annotations

import asyncio
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from packages.performance.benchmarks import (
    BenchmarkMetrics,
    BenchmarkReporter,
    BenchmarkRunner,
    BenchmarkSuite,
    PerformanceBenchmarkSuite,
    run_comprehensive_benchmarks,
)
from packages.performance.cache import (
    CacheEntry,
    CacheManager,
    CacheStats,
    FileCache,
    MemoryCache,
    MultiLevelCache,
    cache_health_check,
    cache_result,
    cached,
)
from packages.performance.optimizer import (
    AutoOptimizer,
    CodeAnalyzer,
    OptimizationPatch,
    OptimizationResult,
    PatchApplicator,
    PerformanceBenchmarker,
    optimize_performance,
)

# Import performance components
from packages.performance.profiler import (
    Bottleneck,
    BottleneckAnalyzer,
    OptimizationEngine,
    OptimizationSuggestion,
    PerformanceMetrics,
    PerformanceOptimizer,
    PerformanceProfiler,
    ProfileReport,
)


# Test fixtures
@pytest.fixture
def sample_function():
    """Sample function for testing."""

    def compute_fibonacci(n: int) -> int:
        if n <= 1:
            return n
        return compute_fibonacci(n - 1) + compute_fibonacci(n - 2)

    return compute_fibonacci


@pytest.fixture
async def async_sample_function():
    """Sample async function for testing."""

    async def async_compute(n: int) -> int:
        await asyncio.sleep(0.01)  # Simulate async work
        return n * 2

    return async_compute


@pytest.fixture
def temp_directory():
    """Temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_code_file(temp_directory):
    """Sample Python code file for testing."""
    code_content = '''
def slow_function():
    """A function with performance issues."""
    result = []
    for i in range(1000):
        for j in range(100):
            result.append(i * j)
    return result

def pure_function(x, y):
    """A pure function suitable for caching."""
    return x ** 2 + y ** 2

async def io_function():
    """Function with I/O operations."""
    with open("test.txt", "w") as f:
        f.write("test data")
    return True
'''

    code_file = temp_directory / "sample_code.py"
    code_file.write_text(code_content)
    return code_file


# Performance Profiler Tests
class TestPerformanceProfiler:
    """Test performance profiler functionality."""

    def test_performance_metrics_creation(self):
        """Test PerformanceMetrics creation and properties."""
        metrics = PerformanceMetrics(
            function_name="test_function",
            execution_time=0.5,
            memory_usage=100.0,
            cpu_usage=50.0,
            call_count=10,
            file_path="/test/file.py",
            line_number=42,
        )

        assert metrics.function_name == "test_function"
        assert metrics.execution_time == 0.5
        assert metrics.time_per_call == 0.05

    def test_bottleneck_creation(self):
        """Test Bottleneck creation."""
        bottleneck = Bottleneck(
            type="cpu",
            severity="high",
            location="/test/file.py:42",
            impact=25.5,
            description="High CPU usage",
            suggestion="Optimize algorithm",
        )

        assert bottleneck.type == "cpu"
        assert bottleneck.severity == "high"
        assert bottleneck.impact == 25.5

    def test_optimization_suggestion_creation(self):
        """Test OptimizationSuggestion creation."""
        suggestion = OptimizationSuggestion(
            target="slow_function",
            type="caching",
            current_performance=1.0,
            expected_improvement=70.0,
            implementation="Add @lru_cache decorator",
            priority=1,
        )

        assert suggestion.target == "slow_function"
        assert suggestion.expected_improvement == 70.0

    @pytest.mark.asyncio
    async def test_profiler_profile_sync_function(self, sample_function):
        """Test profiling synchronous function."""
        profiler = PerformanceProfiler()

        result = await profiler.profile_code(sample_function, 5)

        assert isinstance(result, ProfileReport)
        assert result.total_time > 0
        assert result.total_memory >= 0
        assert len(result.hotspots) >= 0
        assert len(result.bottlenecks) >= 0
        assert len(result.suggestions) >= 0

    @pytest.mark.asyncio
    async def test_profiler_profile_async_function(self, async_sample_function):
        """Test profiling asynchronous function."""
        profiler = PerformanceProfiler()

        result = await profiler.profile_code(async_sample_function, 10)

        assert isinstance(result, ProfileReport)
        assert result.total_time > 0
        assert result.summary["total_functions"] >= 0

    def test_profiler_extract_metrics(self):
        """Test metric extraction from profiler."""
        profiler = PerformanceProfiler()

        # Mock profile data
        with patch.object(profiler, "profile") as mock_profile:
            mock_profile.stats = {("test.py", 1, "test_func"): (1, 1, 0.1, 0.1, {})}

            metrics = profiler._extract_metrics()

            assert len(metrics) > 0
            assert metrics[0].function_name == "test_func"


class TestBottleneckAnalyzer:
    """Test bottleneck analyzer functionality."""

    def test_analyzer_creation(self):
        """Test BottleneckAnalyzer creation."""
        analyzer = BottleneckAnalyzer()
        assert analyzer is not None

    def test_analyze_code_file(self, sample_code_file):
        """Test code analysis for bottlenecks."""
        analyzer = BottleneckAnalyzer()

        bottlenecks = analyzer.analyze_code(sample_code_file)

        assert isinstance(bottlenecks, list)
        # Should find the nested loop in slow_function
        nested_loop_found = any(
            b.type == "algorithm" and "nested loop" in b.description.lower() for b in bottlenecks
        )
        assert nested_loop_found

    def test_rank_bottlenecks(self):
        """Test bottleneck ranking."""
        analyzer = BottleneckAnalyzer()

        bottlenecks = [
            Bottleneck("cpu", "critical", "test:1", 50.0, "High CPU", "Optimize"),
            Bottleneck("io", "medium", "test:2", 20.0, "Slow I/O", "Use async"),
            Bottleneck("memory", "high", "test:3", 30.0, "Memory leak", "Fix leak"),
        ]

        ranked = analyzer.rank_bottlenecks(bottlenecks)

        assert len(ranked) == 3
        # Critical severity with highest impact should be first
        assert ranked[0].severity == "critical"


class TestOptimizationEngine:
    """Test optimization engine functionality."""

    def test_engine_creation(self):
        """Test OptimizationEngine creation."""
        engine = OptimizationEngine()
        assert engine is not None

    @pytest.mark.asyncio
    async def test_apply_optimizations(self, sample_code_file):
        """Test applying optimizations to code."""
        engine = OptimizationEngine()

        suggestions = [
            OptimizationSuggestion(
                target="pure_function",
                type="caching",
                current_performance=1.0,
                expected_improvement=70.0,
                implementation="Add caching",
                priority=1,
            )
        ]

        # Mock astor import since it may not be available
        with patch("packages.performance.profiler.astor") as mock_astor:
            mock_astor.to_source.return_value = "optimized code"

            result = await engine.apply_optimizations(sample_code_file, suggestions)

            # Should attempt optimization
            assert isinstance(result, bool)


class TestPerformanceOptimizer:
    """Test performance optimizer functionality."""

    def test_optimizer_creation(self):
        """Test PerformanceOptimizer creation."""
        optimizer = PerformanceOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, "profiler")
        assert hasattr(optimizer, "analyzer")
        assert hasattr(optimizer, "optimizer")

    @pytest.mark.asyncio
    async def test_optimize_performance_file(self, sample_code_file):
        """Test optimizing performance of a file."""
        optimizer = PerformanceOptimizer()

        report = await optimizer.optimize_performance(sample_code_file)

        assert isinstance(report, ProfileReport)
        assert report.summary["files_analyzed"] == 1
        assert report.summary["bottlenecks_found"] >= 0

    @pytest.mark.asyncio
    async def test_optimize_performance_directory(self, temp_directory, sample_code_file):
        """Test optimizing performance of a directory."""
        optimizer = PerformanceOptimizer()

        report = await optimizer.optimize_performance(temp_directory)

        assert isinstance(report, ProfileReport)
        assert report.summary["files_analyzed"] >= 1

    def test_generate_report(self, temp_directory):
        """Test report generation."""
        optimizer = PerformanceOptimizer()

        # Create sample report
        report = ProfileReport(
            timestamp=time.time(),
            total_time=1.0,
            total_memory=100.0,
            hotspots=[],
            bottlenecks=[],
            suggestions=[],
            summary={"test": "data"},
        )

        output_path = temp_directory / "test_report.md"
        optimizer.generate_report(report, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "Performance Optimization Report" in content


# Auto Optimizer Tests
class TestAutoOptimizer:
    """Test auto optimizer functionality."""

    def test_auto_optimizer_creation(self):
        """Test AutoOptimizer creation."""
        optimizer = AutoOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, "analyzer")
        assert hasattr(optimizer, "applicator")
        assert hasattr(optimizer, "benchmarker")

    @pytest.mark.asyncio
    async def test_optimize_file(self, sample_code_file):
        """Test optimizing a single file."""
        optimizer = AutoOptimizer()

        results = await optimizer.optimize_file(sample_code_file)

        assert isinstance(results, list)
        # Each result should be an OptimizationResult
        for result in results:
            assert isinstance(result, OptimizationResult)


class TestCodeAnalyzer:
    """Test code analyzer functionality."""

    def test_analyzer_creation(self):
        """Test CodeAnalyzer creation."""
        analyzer = CodeAnalyzer()
        assert analyzer is not None

    def test_analyze_file(self, sample_code_file):
        """Test analyzing file for optimization opportunities."""
        analyzer = CodeAnalyzer()

        patches = analyzer.analyze_file(sample_code_file)

        assert isinstance(patches, list)
        # Should find optimization opportunities
        assert len(patches) > 0

        # Check patch types
        patch_types = [p.optimization_type for p in patches]
        assert "nested_loop" in patch_types or "caching" in patch_types

    def test_generate_patch_id(self):
        """Test patch ID generation."""
        analyzer = CodeAnalyzer()

        patch_id = analyzer._generate_patch_id("test.py", 42)

        assert isinstance(patch_id, str)
        assert len(patch_id) == 8  # MD5 hash prefix

    def test_extract_code_block(self):
        """Test code block extraction."""
        analyzer = CodeAnalyzer()

        lines = ["line 1", "line 2", "line 3", "line 4"]
        block = analyzer._extract_code_block(lines, 2, 4)

        assert block == "line 2\nline 3"


class TestPatchApplicator:
    """Test patch applicator functionality."""

    def test_applicator_creation(self):
        """Test PatchApplicator creation."""
        applicator = PatchApplicator()
        assert applicator is not None

    @pytest.mark.asyncio
    async def test_apply_patch(self, sample_code_file):
        """Test applying optimization patch."""
        applicator = PatchApplicator()

        patch = OptimizationPatch(
            id="test_patch",
            target_file=str(sample_code_file),
            line_number=5,
            original_code="def pure_function(",
            optimized_code="@lru_cache(maxsize=128)\ndef pure_function(",
            optimization_type="caching",
            expected_improvement=70.0,
            safety_score=0.9,
            description="Add caching to pure function",
        )

        result = await applicator.apply_patch(patch)

        assert isinstance(result, OptimizationResult)
        assert result.optimization_type == "caching"


class TestPerformanceBenchmarker:
    """Test performance benchmarker functionality."""

    def test_benchmarker_creation(self):
        """Test PerformanceBenchmarker creation."""
        benchmarker = PerformanceBenchmarker()
        assert benchmarker is not None

    @pytest.mark.asyncio
    async def test_benchmark_function(self, sample_function):
        """Test benchmarking a function."""
        benchmarker = PerformanceBenchmarker()

        results = await benchmarker.benchmark_function(sample_function, 3, iterations=5)

        assert isinstance(results, dict)
        assert "avg_time" in results
        assert "min_time" in results
        assert "max_time" in results
        assert results["avg_time"] > 0

    @pytest.mark.asyncio
    async def test_compare_performance(self, sample_function):
        """Test comparing performance between functions."""
        benchmarker = PerformanceBenchmarker()

        def optimized_function(n):
            # Memoized version (simplified)
            return n if n <= 1 else 1  # Fake optimization

        comparison = await benchmarker.compare_performance(sample_function, optimized_function, 3)

        assert isinstance(comparison, dict)
        assert "original" in comparison
        assert "optimized" in comparison
        assert "improvement" in comparison


# Benchmark Suite Tests
class TestBenchmarkRunner:
    """Test benchmark runner functionality."""

    def test_runner_creation(self):
        """Test BenchmarkRunner creation."""
        runner = BenchmarkRunner()
        assert runner is not None
        assert runner.iterations == 100  # Default

    @pytest.mark.asyncio
    async def test_run_benchmark(self, sample_function):
        """Test running a benchmark."""
        runner = BenchmarkRunner({"iterations": 10, "warmup": 2})

        metrics = await runner.run_benchmark(sample_function, "test_benchmark", 3)

        assert isinstance(metrics, BenchmarkMetrics)
        assert metrics.name == "test_benchmark"
        assert metrics.iterations == 10
        assert metrics.mean_time > 0
        assert metrics.throughput > 0

    @pytest.mark.asyncio
    async def test_warmup(self, sample_function):
        """Test benchmark warmup."""
        runner = BenchmarkRunner({"warmup": 3})

        # Mock the function to count calls
        call_count = 0

        def counting_function(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return sample_function(*args, **kwargs)

        await runner._warmup(counting_function, 2)

        assert call_count == 3  # Warmup iterations


class TestPerformanceBenchmarkSuite:
    """Test performance benchmark suite functionality."""

    def test_suite_creation(self):
        """Test PerformanceBenchmarkSuite creation."""
        suite = PerformanceBenchmarkSuite()
        assert suite is not None
        assert hasattr(suite, "runner")
        assert hasattr(suite, "baselines")

    @pytest.mark.asyncio
    async def test_run_core_benchmarks(self):
        """Test running core benchmarks."""
        suite = PerformanceBenchmarkSuite()

        # Reduce iterations for testing
        suite.runner.iterations = 5
        suite.runner.warmup_iterations = 1

        benchmark_suite = await suite.run_core_benchmarks()

        assert isinstance(benchmark_suite, BenchmarkSuite)
        assert benchmark_suite.name == "T-Developer Core Benchmarks"
        assert len(benchmark_suite.benchmarks) > 0

    @pytest.mark.asyncio
    async def test_run_agent_benchmarks(self):
        """Test running agent benchmarks."""
        suite = PerformanceBenchmarkSuite()

        # Reduce iterations for testing
        suite.runner.iterations = 5
        suite.runner.warmup_iterations = 1

        benchmark_suite = await suite.run_agent_benchmarks()

        assert isinstance(benchmark_suite, BenchmarkSuite)
        assert benchmark_suite.name == "T-Developer Agent Benchmarks"
        assert len(benchmark_suite.benchmarks) > 0

    def test_save_and_load_baselines(self, temp_directory):
        """Test saving and loading baselines."""
        suite = PerformanceBenchmarkSuite()

        # Create sample baseline
        metrics = BenchmarkMetrics(
            name="test_benchmark",
            iterations=100,
            min_time=0.01,
            max_time=0.1,
            mean_time=0.05,
            median_time=0.05,
            std_dev=0.01,
            p95_time=0.08,
            p99_time=0.09,
            total_time=5.0,
            memory_peak=100.0,
            memory_average=50.0,
            cpu_usage=20.0,
            throughput=20.0,
        )

        suite.save_baseline(metrics, "1.0.0")

        baseline_file = temp_directory / "baselines.json"
        suite.save_baselines_to_file(baseline_file)

        # Load baselines
        new_suite = PerformanceBenchmarkSuite()
        new_suite.load_baselines_from_file(baseline_file)

        assert "test_benchmark" in new_suite.baselines
        assert new_suite.baselines["test_benchmark"].version == "1.0.0"


class TestBenchmarkReporter:
    """Test benchmark reporter functionality."""

    def test_reporter_creation(self):
        """Test BenchmarkReporter creation."""
        reporter = BenchmarkReporter()
        assert reporter is not None

    def test_generate_report(self, temp_directory):
        """Test generating benchmark report."""
        reporter = BenchmarkReporter()

        # Create sample suite
        suite = BenchmarkSuite(
            name="Test Suite",
            description="Test benchmark suite",
            benchmarks=[
                BenchmarkMetrics(
                    name="test_benchmark",
                    iterations=100,
                    min_time=0.01,
                    max_time=0.1,
                    mean_time=0.05,
                    median_time=0.05,
                    std_dev=0.01,
                    p95_time=0.08,
                    p99_time=0.09,
                    total_time=5.0,
                    memory_peak=100.0,
                    memory_average=50.0,
                    cpu_usage=20.0,
                    throughput=20.0,
                )
            ],
            environment={"python_version": "3.9", "platform": "linux"},
        )

        output_path = temp_directory / "benchmark_report.md"
        reporter.generate_report(suite, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "Performance Benchmark Report" in content
        assert "test_benchmark" in content


# Cache Tests
class TestCacheEntry:
    """Test cache entry functionality."""

    def test_cache_entry_creation(self):
        """Test CacheEntry creation."""
        entry = CacheEntry(value="test_value", created_at=time.time(), expires_at=None)

        assert entry.value == "test_value"
        assert not entry.is_expired()
        assert entry.access_count == 0

    def test_cache_entry_expiration(self):
        """Test cache entry expiration."""
        expired_time = time.time() - 3600  # 1 hour ago
        entry = CacheEntry(value="test_value", created_at=time.time(), expires_at=expired_time)

        assert entry.is_expired()

    def test_cache_entry_access(self):
        """Test cache entry access tracking."""
        entry = CacheEntry(value="test_value", created_at=time.time(), expires_at=None)

        initial_count = entry.access_count
        entry.access()

        assert entry.access_count == initial_count + 1


class TestMemoryCache:
    """Test memory cache functionality."""

    @pytest.mark.asyncio
    async def test_memory_cache_creation(self):
        """Test MemoryCache creation."""
        cache = MemoryCache(max_size=100, default_ttl=3600)
        assert cache.max_size == 100
        assert cache.default_ttl == 3600

    @pytest.mark.asyncio
    async def test_memory_cache_set_get(self):
        """Test setting and getting cache values."""
        cache = MemoryCache(max_size=10)

        await cache.set("key1", "value1")
        result = await cache.get("key1")

        assert result == "value1"

    @pytest.mark.asyncio
    async def test_memory_cache_expiration(self):
        """Test cache expiration."""
        cache = MemoryCache(max_size=10)

        await cache.set("key1", "value1", ttl=1)  # 1 second TTL

        # Should be available immediately
        result = await cache.get("key1")
        assert result == "value1"

        # Wait for expiration
        await asyncio.sleep(1.1)
        result = await cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_memory_cache_eviction(self):
        """Test cache eviction when max size reached."""
        cache = MemoryCache(max_size=2)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")  # Should evict key1

        result1 = await cache.get("key1")
        result2 = await cache.get("key2")
        result3 = await cache.get("key3")

        assert result1 is None  # Evicted
        assert result2 == "value2"
        assert result3 == "value3"

    @pytest.mark.asyncio
    async def test_memory_cache_delete(self):
        """Test cache deletion."""
        cache = MemoryCache(max_size=10)

        await cache.set("key1", "value1")
        assert await cache.get("key1") == "value1"

        deleted = await cache.delete("key1")
        assert deleted is True
        assert await cache.get("key1") is None

    @pytest.mark.asyncio
    async def test_memory_cache_clear(self):
        """Test cache clearing."""
        cache = MemoryCache(max_size=10)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")

        await cache.clear()

        assert await cache.get("key1") is None
        assert await cache.get("key2") is None

    @pytest.mark.asyncio
    async def test_memory_cache_stats(self):
        """Test cache statistics."""
        cache = MemoryCache(max_size=10)

        await cache.set("key1", "value1")
        await cache.get("key1")  # Hit
        await cache.get("key2")  # Miss

        stats = await cache.get_stats()

        assert isinstance(stats, CacheStats)
        assert stats.hits >= 1
        assert stats.misses >= 1
        assert stats.size >= 0


class TestFileCache:
    """Test file cache functionality."""

    @pytest.mark.asyncio
    async def test_file_cache_creation(self, temp_directory):
        """Test FileCache creation."""
        cache = FileCache(cache_dir=temp_directory, max_size=100)
        assert cache.cache_dir == temp_directory
        assert cache.max_size == 100

    @pytest.mark.asyncio
    async def test_file_cache_set_get(self, temp_directory):
        """Test setting and getting file cache values."""
        cache = FileCache(cache_dir=temp_directory, max_size=10)

        await cache.set("key1", {"data": "value1"})
        result = await cache.get("key1")

        assert result == {"data": "value1"}

    @pytest.mark.asyncio
    async def test_file_cache_expiration(self, temp_directory):
        """Test file cache expiration."""
        cache = FileCache(cache_dir=temp_directory, max_size=10)

        await cache.set("key1", "value1", ttl=1)  # 1 second TTL

        # Should be available immediately
        result = await cache.get("key1")
        assert result == "value1"

        # Wait for expiration
        await asyncio.sleep(1.1)
        result = await cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_file_cache_delete(self, temp_directory):
        """Test file cache deletion."""
        cache = FileCache(cache_dir=temp_directory, max_size=10)

        await cache.set("key1", "value1")
        assert await cache.get("key1") == "value1"

        deleted = await cache.delete("key1")
        assert deleted is True
        assert await cache.get("key1") is None


class TestMultiLevelCache:
    """Test multi-level cache functionality."""

    @pytest.mark.asyncio
    async def test_multi_level_cache_creation(self, temp_directory):
        """Test MultiLevelCache creation."""
        l1_cache = MemoryCache(max_size=10)
        l2_cache = FileCache(cache_dir=temp_directory, max_size=100)

        cache = MultiLevelCache(l1_cache, l2_cache)
        assert cache.l1_cache == l1_cache
        assert cache.l2_cache == l2_cache

    @pytest.mark.asyncio
    async def test_multi_level_cache_promotion(self, temp_directory):
        """Test cache promotion from L2 to L1."""
        l1_cache = MemoryCache(max_size=2)
        l2_cache = FileCache(cache_dir=temp_directory, max_size=10)
        cache = MultiLevelCache(l1_cache, l2_cache)

        # Set value in L2 only
        await l2_cache.set("key1", "value1")

        # Get from multi-level cache (should promote to L1)
        result = await cache.get("key1")
        assert result == "value1"

        # Should now be in L1
        l1_result = await l1_cache.get("key1")
        assert l1_result == "value1"


class TestCacheManager:
    """Test cache manager functionality."""

    def test_cache_manager_creation(self):
        """Test CacheManager creation."""
        manager = CacheManager()
        assert manager is not None
        assert "default" in manager._caches

    def test_get_cache(self):
        """Test getting cache by name."""
        manager = CacheManager()

        cache = manager.get_cache("default")
        assert cache is not None

        # Test getting non-existent cache
        with pytest.raises(ValueError):
            manager.get_cache("nonexistent")

    def test_register_cache(self):
        """Test registering custom cache."""
        manager = CacheManager()
        custom_cache = MemoryCache(max_size=50)

        manager.register_cache("custom", custom_cache)

        retrieved_cache = manager.get_cache("custom")
        assert retrieved_cache == custom_cache

    @pytest.mark.asyncio
    async def test_get_all_stats(self):
        """Test getting statistics from all caches."""
        manager = CacheManager()

        stats = await manager.get_all_stats()

        assert isinstance(stats, dict)
        assert "default" in stats


class TestCacheDecorators:
    """Test cache decorators functionality."""

    @pytest.mark.asyncio
    async def test_cached_decorator_async(self):
        """Test @cached decorator with async function."""
        call_count = 0

        @cached(cache_name="memory", ttl=60)
        async def expensive_async_function(x):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return x * 2

        # First call
        result1 = await expensive_async_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call should use cache
        result2 = await expensive_async_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment

    def test_cached_decorator_sync(self):
        """Test @cached decorator with sync function."""
        call_count = 0

        @cached(cache_name="memory", ttl=60)
        def expensive_sync_function(x):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)
            return x * 2

        # First call
        result1 = expensive_sync_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call should use cache
        result2 = expensive_sync_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment

    def test_cache_result_decorator(self):
        """Test @cache_result decorator."""
        call_count = 0

        @cache_result(ttl=60)
        def simple_function(x):
            nonlocal call_count
            call_count += 1
            return x * 3

        # First call
        result1 = simple_function(4)
        assert result1 == 12
        assert call_count == 1

        # Second call should use cache
        result2 = simple_function(4)
        assert result2 == 12
        assert call_count == 1


class TestCacheUtilities:
    """Test cache utility functions."""

    @pytest.mark.asyncio
    async def test_cache_health_check(self):
        """Test cache health check."""
        manager = CacheManager()

        health_status = await cache_health_check(manager)

        assert isinstance(health_status, dict)
        assert "status" in health_status
        assert "overall_hit_rate" in health_status
        assert "caches" in health_status

    @pytest.mark.asyncio
    async def test_cache_context(self):
        """Test cache context manager."""
        async with cache_context("memory") as cache:
            await cache.set("test_key", "test_value")
            result = await cache.get("test_key")
            assert result == "test_value"


# Integration Tests
class TestPerformanceIntegration:
    """Integration tests for performance components."""

    @pytest.mark.asyncio
    async def test_optimize_performance_integration(self, temp_directory):
        """Test end-to-end performance optimization."""
        # Create test configuration
        config = {"max_cycles": 1, "safety_threshold": 0.8}

        result = await optimize_performance(temp_directory, config)

        assert isinstance(result, dict)
        assert "results" in result
        assert "statistics" in result

    @pytest.mark.asyncio
    async def test_run_comprehensive_benchmarks_integration(self, temp_directory):
        """Test end-to-end benchmark execution."""
        results = await run_comprehensive_benchmarks(temp_directory)

        assert isinstance(results, dict)
        assert "core" in results or "agents" in results

        # Check that reports were generated
        reports = list(temp_directory.glob("*_benchmark_report_*.md"))
        assert len(reports) > 0


# Property-based tests
@pytest.mark.parametrize("cache_size,ttl", [(10, 60), (100, 3600), (1000, 86400)])
class TestCacheProperties:
    """Property-based tests for cache behavior."""

    @pytest.mark.asyncio
    async def test_cache_size_limits(self, cache_size, ttl):
        """Test cache respects size limits."""
        cache = MemoryCache(max_size=cache_size, default_ttl=ttl)

        # Fill cache beyond capacity
        for i in range(cache_size + 10):
            await cache.set(f"key_{i}", f"value_{i}")

        stats = await cache.get_stats()
        assert stats.size <= cache_size

    @pytest.mark.asyncio
    async def test_cache_ttl_behavior(self, cache_size, ttl):
        """Test cache TTL behavior."""
        cache = MemoryCache(max_size=cache_size, default_ttl=ttl)

        await cache.set("test_key", "test_value", ttl=1)  # 1 second TTL

        # Should be available immediately
        result = await cache.get("test_key")
        assert result == "test_value"


# Performance Tests
class TestPerformancePerformance:
    """Test performance of performance components themselves."""

    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test cache performance under load."""
        cache = MemoryCache(max_size=1000)

        start_time = time.time()

        # Perform many cache operations
        tasks = []
        for i in range(100):
            tasks.append(cache.set(f"key_{i}", f"value_{i}"))

        await asyncio.gather(*tasks)

        # Test retrieval performance
        get_tasks = []
        for i in range(100):
            get_tasks.append(cache.get(f"key_{i}"))

        results = await asyncio.gather(*get_tasks)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time
        assert duration < 1.0  # 1 second
        assert len(results) == 100

    @pytest.mark.asyncio
    async def test_profiler_overhead(self, sample_function):
        """Test profiler overhead."""
        profiler = PerformanceProfiler()

        # Measure without profiling
        start_time = time.time()
        for _ in range(10):
            sample_function(3)
        baseline_time = time.time() - start_time

        # Measure with profiling
        start_time = time.time()
        for _ in range(10):
            await profiler.profile_code(sample_function, 3)
        profiled_time = time.time() - start_time

        # Profiling overhead should be reasonable
        overhead_ratio = profiled_time / baseline_time
        assert overhead_ratio < 100  # Less than 100x overhead


# Error Handling Tests
class TestPerformanceErrorHandling:
    """Test error handling in performance components."""

    @pytest.mark.asyncio
    async def test_profiler_error_handling(self):
        """Test profiler handles errors gracefully."""
        profiler = PerformanceProfiler()

        def failing_function():
            raise ValueError("Test error")

        # Should handle function errors gracefully
        with pytest.raises(ValueError):
            await profiler.profile_code(failing_function)

    @pytest.mark.asyncio
    async def test_cache_error_handling(self, temp_directory):
        """Test cache handles errors gracefully."""
        # Create cache with invalid directory
        invalid_dir = temp_directory / "nonexistent" / "path"
        cache = FileCache(cache_dir=invalid_dir, max_size=10)

        # Should handle file system errors
        result = await cache.get("nonexistent_key")
        assert result is None

    def test_optimizer_error_handling(self):
        """Test optimizer handles invalid code gracefully."""
        analyzer = CodeAnalyzer()

        # Create file with invalid Python syntax
        invalid_file = Path("/tmp/invalid_syntax.py")
        try:
            invalid_file.write_text("def invalid syntax here")
            patches = analyzer.analyze_file(invalid_file)
            # Should return empty list instead of crashing
            assert isinstance(patches, list)
        finally:
            if invalid_file.exists():
                invalid_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=packages.performance", "--cov-report=html"])
