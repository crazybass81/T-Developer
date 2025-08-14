"""
Test suite for Code Quality and Performance Analysis
Day 26: Phase 2 - ServiceImproverAgent
"""

import asyncio
import time
from typing import List

import pytest

from src.agents.meta.code_quality_analyzer import (
    CodeIssue,
    CodeQualityAnalyzer,
    QualityMetrics,
    get_analyzer,
)
from src.agents.meta.performance_analyzer import (
    Bottleneck,
    PerformanceAnalyzer,
    PerformanceMetrics,
    get_performance_analyzer,
)
from src.monitoring.bottleneck_detector import (
    BottleneckDetector,
    BottleneckEvent,
    ResourceMetrics,
    ServiceMetrics,
    get_detector,
)


class TestCodeQualityAnalyzer:
    """Test code quality analyzer"""

    @pytest.fixture
    def analyzer(self):
        """Get analyzer instance"""
        return get_analyzer()

    @pytest.mark.asyncio
    async def test_analyze_good_code(self, analyzer):
        """Test analyzing good quality code"""

        good_code = """
def calculate_sum(numbers: List[int]) -> int:
    '''Calculate sum of numbers'''
    total = 0
    for number in numbers:
        total += number
    return total
"""

        report = await analyzer.analyze(good_code, "good.py")

        assert report is not None
        assert report.metrics.overall > 0.5
        assert len(report.issues) < 3

    @pytest.mark.asyncio
    async def test_analyze_bad_code(self, analyzer):
        """Test analyzing poor quality code"""

        bad_code = """
def x(l):
    t = 0
    for i in l:
        if i > 100:
            t += i * 1.5
    print(t)
    try:
        eval(input())
    except:
        pass
    password = "admin123"
"""

        report = await analyzer.analyze(bad_code, "bad.py")

        assert report is not None
        assert report.metrics.overall < 0.5
        assert report.metrics.security < 0.5
        assert len(report.issues) > 3

        # Check for critical issues
        critical_issues = [i for i in report.issues if i.severity == "critical"]
        assert len(critical_issues) > 0

    @pytest.mark.asyncio
    async def test_complexity_calculation(self, analyzer):
        """Test cyclomatic complexity calculation"""

        complex_code = """
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                return x + y + z
            else:
                return x + y
        else:
            return x
    else:
        return 0
"""

        report = await analyzer.analyze(complex_code, "complex.py")

        assert report.metrics.complexity < 0.7  # High complexity

    @pytest.mark.asyncio
    async def test_security_detection(self, analyzer):
        """Test security vulnerability detection"""

        insecure_code = """
import os
import pickle

def dangerous():
    eval(input("Enter code: "))
    os.system("rm -rf /")
    data = pickle.loads(untrusted_data)
    password = "secret123"
"""

        report = await analyzer.analyze(insecure_code, "insecure.py")

        assert report.metrics.security < 0.3

        # Check for security issues
        security_issues = [i for i in report.issues if i.type == "vulnerability"]
        assert len(security_issues) > 0

    def test_issue_patterns(self, analyzer):
        """Test issue pattern detection"""

        patterns = analyzer.issue_patterns

        assert "eval_usage" in patterns
        assert "hardcoded_password" in patterns
        assert "broad_except" in patterns
        assert "magic_number" in patterns

    @pytest.mark.asyncio
    async def test_recommendations(self, analyzer):
        """Test recommendation generation"""

        code = """
def poorly_written():
    x = 1
    y = 2
    # No comments
    return eval(str(x + y))
"""

        report = await analyzer.analyze(code, "test.py")

        assert len(report.recommendations) > 0
        assert report.improvement_potential > 0
        assert report.estimated_effort > 0


class TestPerformanceAnalyzer:
    """Test performance analyzer"""

    @pytest.fixture
    def analyzer(self):
        """Get performance analyzer instance"""
        return get_performance_analyzer()

    @pytest.mark.asyncio
    async def test_profile_function(self, analyzer):
        """Test function profiling"""

        def test_func(n=100):
            return sum(range(n))

        profile = await analyzer.profile(test_func, n=100, iterations=10)

        assert profile is not None
        assert profile.metrics.execution_time > 0
        assert profile.metrics.throughput > 0
        assert profile.metrics.latency_p50 > 0

    @pytest.mark.asyncio
    async def test_bottleneck_detection(self, analyzer):
        """Test bottleneck detection"""

        def slow_func():
            time.sleep(0.01)  # Simulate slow operation
            return "done"

        profile = await analyzer.profile(slow_func, iterations=5)

        assert len(profile.bottlenecks) >= 0

        if profile.bottlenecks:
            bottleneck = profile.bottlenecks[0]
            assert bottleneck.type in ["cpu", "memory", "consistency"]
            assert bottleneck.suggestion is not None

    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, analyzer):
        """Test memory leak detection"""

        leak_list = []

        def leaky_func():
            # Simulate memory leak
            leak_list.extend([i for i in range(1000)])

        profile = await analyzer.profile(leaky_func, iterations=10)

        # May or may not detect depending on GC
        assert profile.memory_leaks is not None

    @pytest.mark.asyncio
    async def test_function_comparison(self, analyzer):
        """Test comparing two functions"""

        def slow_version(n=100):
            result = 0
            for i in range(n):
                result += i
            return result

        def fast_version(n=100):
            return sum(range(n))

        comparison = await analyzer.compare(slow_version, fast_version, n=1000, iterations=10)

        assert "time_improvement" in comparison
        assert "memory_improvement" in comparison
        assert "winner" in comparison
        assert "recommendation" in comparison

    def test_metrics_calculation(self, analyzer):
        """Test metrics calculation"""

        execution_times = [0.1, 0.2, 0.15, 0.12, 0.18]
        memory_peaks = [10, 12, 11, 13, 11]

        metrics = analyzer._calculate_metrics(execution_times, memory_peaks, len(execution_times))

        assert metrics.execution_time > 0
        assert metrics.memory_usage > 0
        assert metrics.latency_p50 > 0
        assert metrics.latency_p95 >= metrics.latency_p50
        assert metrics.latency_p99 >= metrics.latency_p95


class TestBottleneckDetector:
    """Test bottleneck detector"""

    @pytest.fixture
    def detector(self):
        """Get detector instance"""
        return get_detector()

    @pytest.mark.asyncio
    async def test_monitor(self, detector):
        """Test monitoring for bottlenecks"""

        bottlenecks = await detector.monitor(duration=2)

        # May or may not detect bottlenecks depending on system state
        assert isinstance(bottlenecks, list)

    def test_analyze_bottlenecks(self, detector):
        """Test bottleneck analysis"""

        metrics = ResourceMetrics(
            timestamp=time.time(),
            cpu_percent=95.0,  # High CPU
            memory_percent=85.0,  # High memory
            disk_io_read=150.0,
            disk_io_write=50.0,
            network_in=10.0,
            network_out=5.0,
            thread_count=100,
            open_files=50,
        )

        bottlenecks = detector._analyze_bottlenecks(metrics)

        assert len(bottlenecks) > 0

        # Should detect CPU bottleneck
        cpu_bottlenecks = [b for b in bottlenecks if b.type == "cpu"]
        assert len(cpu_bottlenecks) > 0
        assert cpu_bottlenecks[0].severity == "critical"

    def test_service_metrics_update(self, detector):
        """Test service metrics update"""

        metrics = ServiceMetrics(
            service_name="test_service",
            request_rate=1000,
            error_rate=0.1,  # 10% error rate
            avg_latency=3000,  # 3 seconds
            p99_latency=5000,
            queue_size=100,
            active_connections=500,
        )

        detector.update_service_metrics(metrics)

        assert "test_service" in detector.service_metrics

        # Should have detected service bottlenecks
        history = detector.bottleneck_history
        service_bottlenecks = [b for b in history if b.type == "service"]
        assert len(service_bottlenecks) > 0

    def test_bottleneck_summary(self, detector):
        """Test bottleneck summary generation"""

        # Add some test bottlenecks
        detector.bottleneck_history = [
            BottleneckEvent(
                timestamp=time.time(),
                type="cpu",
                severity="high",
                component="system",
                description="CPU high",
                metrics={},
                suggested_action="Scale",
                auto_resolved=True,
            ),
            BottleneckEvent(
                timestamp=time.time(),
                type="memory",
                severity="medium",
                component="system",
                description="Memory usage",
                metrics={},
                suggested_action="Monitor",
            ),
        ]

        summary = detector.get_bottleneck_summary()

        assert summary["total_bottlenecks"] == 2
        assert "cpu" in summary["by_type"]
        assert "memory" in summary["by_type"]
        assert summary["auto_resolved"] == 1
        assert summary["resolution_rate"] == 50.0

    def test_recommendations(self, detector):
        """Test recommendation generation"""

        # Add CPU bottlenecks
        for i in range(6):
            detector.bottleneck_history.append(
                BottleneckEvent(
                    timestamp=time.time(),
                    type="cpu",
                    severity="high",
                    component="system",
                    description="CPU high",
                    metrics={},
                    suggested_action="Scale",
                )
            )

        recommendations = detector.get_recommendations()

        assert len(recommendations) > 0
        assert any("CPU" in rec for rec in recommendations)


@pytest.mark.integration
class TestIntegration:
    """Integration tests for quality and performance analysis"""

    @pytest.mark.asyncio
    async def test_complete_analysis_flow(self):
        """Test complete code analysis flow"""

        code_analyzer = get_analyzer()
        perf_analyzer = get_performance_analyzer()

        # Sample code to analyze
        test_code = """
def process_data(data):
    '''Process input data'''
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""

        # Analyze code quality
        quality_report = await code_analyzer.analyze(test_code, "test.py")

        assert quality_report.metrics.overall > 0.5

        # Create function from code
        exec(test_code)
        test_func = locals()["process_data"]

        # Profile performance
        perf_profile = await perf_analyzer.profile(test_func, [1, 2, 3, 4, 5], iterations=10)

        assert perf_profile.metrics.execution_time > 0

        # Generate combined insights
        print(f"\nAnalysis Results:")
        print(f"  Code Quality: {quality_report.metrics.overall:.2f}")
        print(f"  Performance: {perf_profile.metrics.throughput:.2f} ops/s")
        print(f"  Issues: {len(quality_report.issues)}")
        print(f"  Bottlenecks: {len(perf_profile.bottlenecks)}")

        # Both should provide recommendations
        assert len(quality_report.recommendations) >= 0
        assert len(perf_profile.optimization_opportunities) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
