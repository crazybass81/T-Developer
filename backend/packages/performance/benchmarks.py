"""Performance Benchmarks - Comprehensive benchmark suite with baselines.

Phase 6: P6-T1 - Performance Optimization
Establish performance baselines and track improvements.
"""

from __future__ import annotations

import asyncio
import gc
import json
import logging
import platform
import statistics
import time
import tracemalloc
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

import psutil

# Constants
BENCHMARK_ITERATIONS: int = 100
WARMUP_ITERATIONS: int = 10
TIMEOUT_SECONDS: int = 60
MIN_EXECUTION_TIME: float = 0.001  # 1ms minimum

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkMetrics:
    """Performance metrics for a benchmark."""

    name: str
    iterations: int
    min_time: float
    max_time: float
    mean_time: float
    median_time: float
    std_dev: float
    p95_time: float
    p99_time: float
    total_time: float
    memory_peak: float  # MB
    memory_average: float  # MB
    cpu_usage: float  # Percentage
    throughput: float  # Operations per second
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkSuite:
    """Collection of related benchmarks."""

    name: str
    description: str
    benchmarks: list[BenchmarkMetrics] = field(default_factory=list)
    baseline_metrics: Optional[dict[str, BenchmarkMetrics]] = None
    environment: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceBaseline:
    """Performance baseline for comparison."""

    name: str
    version: str
    metrics: BenchmarkMetrics
    environment: dict[str, Any]
    created_at: datetime

    def compare_with(self, current: BenchmarkMetrics) -> dict[str, float]:
        """Compare current metrics with baseline."""
        return {
            "time_change": (
                (current.mean_time - self.metrics.mean_time) / self.metrics.mean_time * 100
            ),
            "memory_change": (
                (current.memory_average - self.metrics.memory_average)
                / max(self.metrics.memory_average, 0.001)
                * 100
            ),
            "throughput_change": (
                (current.throughput - self.metrics.throughput)
                / max(self.metrics.throughput, 0.001)
                * 100
            ),
        }


class BenchmarkRunner:
    """Execute and measure benchmark performance."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize benchmark runner.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.iterations = self.config.get("iterations", BENCHMARK_ITERATIONS)
        self.warmup_iterations = self.config.get("warmup", WARMUP_ITERATIONS)
        self.timeout = self.config.get("timeout", TIMEOUT_SECONDS)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def run_benchmark(self, func: Callable, name: str, *args, **kwargs) -> BenchmarkMetrics:
        """Run benchmark for a function.

        Args:
            func: Function to benchmark
            name: Benchmark name
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Benchmark metrics
        """
        self.logger.info(f"Running benchmark: {name}")

        # Warmup
        await self._warmup(func, *args, **kwargs)

        # Collect garbage before benchmarking
        gc.collect()

        # Track memory and CPU
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        times = []
        memory_samples = []
        cpu_samples = []

        # Start memory tracking
        tracemalloc.start()

        try:
            for i in range(self.iterations):
                # Measure execution time
                start_time = time.perf_counter()

                if asyncio.iscoroutinefunction(func):
                    result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout)
                else:
                    result = func(*args, **kwargs)

                end_time = time.perf_counter()
                execution_time = end_time - start_time

                # Ensure minimum execution time for accurate measurement
                if execution_time < MIN_EXECUTION_TIME:
                    self.logger.warning(f"Execution time too small: {execution_time:.6f}s")

                times.append(execution_time)

                # Sample memory and CPU every 10 iterations
                if i % 10 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_samples.append(current_memory)
                    cpu_samples.append(process.cpu_percent())

        finally:
            # Stop memory tracking
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

        # Calculate statistics
        min_time = min(times)
        max_time = max(times)
        mean_time = statistics.mean(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0

        # Calculate percentiles
        sorted_times = sorted(times)
        p95_index = int(0.95 * len(sorted_times))
        p99_index = int(0.99 * len(sorted_times))
        p95_time = sorted_times[p95_index]
        p99_time = sorted_times[p99_index]

        total_time = sum(times)
        throughput = self.iterations / total_time if total_time > 0 else 0

        # Memory metrics
        peak_memory = peak / 1024 / 1024  # Convert to MB
        avg_memory = statistics.mean(memory_samples) if memory_samples else initial_memory
        avg_cpu = statistics.mean(cpu_samples) if cpu_samples else 0

        return BenchmarkMetrics(
            name=name,
            iterations=self.iterations,
            min_time=min_time,
            max_time=max_time,
            mean_time=mean_time,
            median_time=median_time,
            std_dev=std_dev,
            p95_time=p95_time,
            p99_time=p99_time,
            total_time=total_time,
            memory_peak=peak_memory,
            memory_average=avg_memory,
            cpu_usage=avg_cpu,
            throughput=throughput,
            metadata={
                "environment": self._get_environment_info(),
                "function_name": func.__name__,
                "warmup_iterations": self.warmup_iterations,
            },
        )

    async def _warmup(self, func: Callable, *args, **kwargs) -> None:
        """Warmup function execution."""
        for _ in range(self.warmup_iterations):
            if asyncio.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                func(*args, **kwargs)

    def _get_environment_info(self) -> dict[str, Any]:
        """Get environment information."""
        return {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
            "timestamp": datetime.now().isoformat(),
        }


class PerformanceBenchmarkSuite:
    """Comprehensive performance benchmark suite."""

    def __init__(self):
        """Initialize benchmark suite."""
        self.runner = BenchmarkRunner()
        self.baselines: dict[str, PerformanceBaseline] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    async def run_core_benchmarks(self) -> BenchmarkSuite:
        """Run core T-Developer performance benchmarks."""
        suite = BenchmarkSuite(
            name="T-Developer Core Benchmarks",
            description="Core performance benchmarks for T-Developer components",
        )

        # CPU-intensive benchmarks
        cpu_metrics = await self.runner.run_benchmark(
            self._cpu_intensive_task, "CPU Intensive Task"
        )
        suite.benchmarks.append(cpu_metrics)

        # Memory-intensive benchmarks
        memory_metrics = await self.runner.run_benchmark(
            self._memory_intensive_task, "Memory Intensive Task"
        )
        suite.benchmarks.append(memory_metrics)

        # I/O-intensive benchmarks
        io_metrics = await self.runner.run_benchmark(self._io_intensive_task, "I/O Intensive Task")
        suite.benchmarks.append(io_metrics)

        # Async benchmarks
        async_metrics = await self.runner.run_benchmark(self._async_task, "Async Task")
        suite.benchmarks.append(async_metrics)

        # Algorithm benchmarks
        sort_metrics = await self.runner.run_benchmark(
            self._sorting_algorithm, "Sorting Algorithm", 1000
        )
        suite.benchmarks.append(sort_metrics)

        # String processing benchmarks
        string_metrics = await self.runner.run_benchmark(
            self._string_processing, "String Processing"
        )
        suite.benchmarks.append(string_metrics)

        suite.environment = self.runner._get_environment_info()
        return suite

    async def run_agent_benchmarks(self) -> BenchmarkSuite:
        """Run agent-specific performance benchmarks."""
        suite = BenchmarkSuite(
            name="T-Developer Agent Benchmarks",
            description="Performance benchmarks for T-Developer agents",
        )

        # Research agent simulation
        research_metrics = await self.runner.run_benchmark(
            self._simulate_research_agent, "Research Agent Simulation"
        )
        suite.benchmarks.append(research_metrics)

        # Code generation simulation
        codegen_metrics = await self.runner.run_benchmark(
            self._simulate_code_generation, "Code Generation Simulation"
        )
        suite.benchmarks.append(codegen_metrics)

        # Analysis simulation
        analysis_metrics = await self.runner.run_benchmark(
            self._simulate_code_analysis, "Code Analysis Simulation"
        )
        suite.benchmarks.append(analysis_metrics)

        suite.environment = self.runner._get_environment_info()
        return suite

    # Benchmark test functions
    def _cpu_intensive_task(self) -> float:
        """CPU-intensive computation."""
        result = 0
        for i in range(10000):
            result += i**2
        return result

    def _memory_intensive_task(self) -> list[int]:
        """Memory-intensive task."""
        data = list(range(100000))
        # Create some memory pressure
        matrix = [[i * j for j in range(100)] for i in range(100)]
        return len(data) + len(matrix)

    async def _io_intensive_task(self) -> int:
        """I/O-intensive task simulation."""
        # Simulate file operations
        await asyncio.sleep(0.001)  # Simulate I/O delay
        return 42

    async def _async_task(self) -> str:
        """Async task benchmark."""
        # Simulate multiple async operations
        tasks = [asyncio.sleep(0.001) for _ in range(10)]
        await asyncio.gather(*tasks)
        return "completed"

    def _sorting_algorithm(self, size: int) -> list[int]:
        """Sorting algorithm benchmark."""
        import random

        data = [random.randint(1, 1000) for _ in range(size)]
        return sorted(data)

    def _string_processing(self) -> str:
        """String processing benchmark."""
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100
        # Perform various string operations
        result = text.upper().lower().replace(" ", "_").split("_")
        return "".join(result[:10])

    async def _simulate_research_agent(self) -> dict[str, Any]:
        """Simulate research agent workload."""
        # Simulate research operations
        await asyncio.sleep(0.005)  # API call simulation

        # Simulate text processing
        text = "Sample research data " * 1000
        words = text.split()

        # Simulate analysis
        analysis = {"word_count": len(words), "char_count": len(text), "sentiment": "positive"}

        return analysis

    def _simulate_code_generation(self) -> str:
        """Simulate code generation workload."""
        # Simulate template processing
        template = """
        def example_function({params}):
            '''Generated function.'''
            {body}
            return result
        """

        params = ", ".join([f"param{i}" for i in range(5)])
        body = "\n    ".join([f"step_{i} = param{i} * 2" for i in range(5)])

        code = template.format(params=params, body=body)
        return code

    def _simulate_code_analysis(self) -> dict[str, Any]:
        """Simulate code analysis workload."""
        # Simulate AST parsing and analysis
        code_samples = [
            "def func1(): pass",
            "class Example: pass",
            "for i in range(10): print(i)",
        ] * 100

        analysis = {"functions": 0, "classes": 0, "loops": 0}

        for code in code_samples:
            if "def " in code:
                analysis["functions"] += 1
            elif "class " in code:
                analysis["classes"] += 1
            elif "for " in code:
                analysis["loops"] += 1

        return analysis

    def save_baseline(self, benchmark: BenchmarkMetrics, version: str) -> None:
        """Save benchmark as baseline."""
        baseline = PerformanceBaseline(
            name=benchmark.name,
            version=version,
            metrics=benchmark,
            environment=benchmark.metadata.get("environment", {}),
            created_at=datetime.now(),
        )

        self.baselines[benchmark.name] = baseline
        self.logger.info(f"Saved baseline for {benchmark.name} v{version}")

    def compare_with_baseline(self, benchmark: BenchmarkMetrics) -> Optional[dict[str, float]]:
        """Compare benchmark with baseline."""
        if benchmark.name not in self.baselines:
            return None

        baseline = self.baselines[benchmark.name]
        return baseline.compare_with(benchmark)

    def save_baselines_to_file(self, file_path: Path) -> None:
        """Save baselines to JSON file."""
        baselines_data = {}

        for name, baseline in self.baselines.items():
            baselines_data[name] = {
                "name": baseline.name,
                "version": baseline.version,
                "metrics": {
                    "mean_time": baseline.metrics.mean_time,
                    "memory_average": baseline.metrics.memory_average,
                    "throughput": baseline.metrics.throughput,
                    "p95_time": baseline.metrics.p95_time,
                },
                "environment": baseline.environment,
                "created_at": baseline.created_at.isoformat(),
            }

        with open(file_path, "w") as f:
            json.dump(baselines_data, f, indent=2)

        self.logger.info(f"Baselines saved to {file_path}")

    def load_baselines_from_file(self, file_path: Path) -> None:
        """Load baselines from JSON file."""
        if not file_path.exists():
            self.logger.warning(f"Baseline file not found: {file_path}")
            return

        with open(file_path) as f:
            baselines_data = json.load(f)

        for name, data in baselines_data.items():
            metrics = BenchmarkMetrics(
                name=data["name"],
                iterations=100,  # Default
                min_time=data["metrics"]["mean_time"],
                max_time=data["metrics"]["mean_time"],
                mean_time=data["metrics"]["mean_time"],
                median_time=data["metrics"]["mean_time"],
                std_dev=0,
                p95_time=data["metrics"]["p95_time"],
                p99_time=data["metrics"]["p95_time"],
                total_time=data["metrics"]["mean_time"] * 100,
                memory_peak=data["metrics"]["memory_average"],
                memory_average=data["metrics"]["memory_average"],
                cpu_usage=0,
                throughput=data["metrics"]["throughput"],
            )

            baseline = PerformanceBaseline(
                name=data["name"],
                version=data["version"],
                metrics=metrics,
                environment=data["environment"],
                created_at=datetime.fromisoformat(data["created_at"]),
            )

            self.baselines[name] = baseline

        self.logger.info(f"Loaded {len(baselines_data)} baselines from {file_path}")


class BenchmarkReporter:
    """Generate benchmark reports."""

    def generate_report(
        self,
        suite: BenchmarkSuite,
        output_path: Path,
        baselines: Optional[dict[str, PerformanceBaseline]] = None,
    ) -> None:
        """Generate comprehensive benchmark report."""
        report_content = f"""# Performance Benchmark Report

Generated: {suite.timestamp}
Suite: {suite.name}
Description: {suite.description}

## Environment
- Python Version: {suite.environment.get('python_version', 'Unknown')}
- Platform: {suite.environment.get('platform', 'Unknown')}
- CPU Count: {suite.environment.get('cpu_count', 'Unknown')}
- Total Memory: {suite.environment.get('memory_total', 'Unknown'):.1f} GB

## Benchmark Results

| Benchmark | Mean Time (ms) | P95 Time (ms) | Throughput (ops/s) | Memory (MB) | Status |
|-----------|---------------|---------------|-------------------|-------------|---------|
"""

        for benchmark in suite.benchmarks:
            status = "✅"
            baseline_info = ""

            if baselines and benchmark.name in baselines:
                baseline = baselines[benchmark.name]
                comparison = baseline.compare_with(benchmark)

                time_change = comparison["time_change"]
                if time_change > 10:  # 10% slower
                    status = "⚠️ Slower"
                elif time_change < -5:  # 5% faster
                    status = "🚀 Faster"

                baseline_info = f" ({time_change:+.1f}%)"

            report_content += f"| {benchmark.name} | {benchmark.mean_time*1000:.2f} | {benchmark.p95_time*1000:.2f} | {benchmark.throughput:.1f} | {benchmark.memory_average:.1f} | {status}{baseline_info} |\n"

        report_content += "\n## Detailed Results\n"

        for benchmark in suite.benchmarks:
            report_content += f"""
### {benchmark.name}

- **Iterations**: {benchmark.iterations}
- **Mean Time**: {benchmark.mean_time*1000:.3f} ms
- **Median Time**: {benchmark.median_time*1000:.3f} ms
- **Min Time**: {benchmark.min_time*1000:.3f} ms
- **Max Time**: {benchmark.max_time*1000:.3f} ms
- **Standard Deviation**: {benchmark.std_dev*1000:.3f} ms
- **P95 Time**: {benchmark.p95_time*1000:.3f} ms
- **P99 Time**: {benchmark.p99_time*1000:.3f} ms
- **Throughput**: {benchmark.throughput:.1f} operations/second
- **Memory Peak**: {benchmark.memory_peak:.2f} MB
- **Memory Average**: {benchmark.memory_average:.2f} MB
- **CPU Usage**: {benchmark.cpu_usage:.1f}%
"""

            if baselines and benchmark.name in baselines:
                baseline = baselines[benchmark.name]
                comparison = baseline.compare_with(benchmark)

                report_content += f"""
#### Baseline Comparison (vs {baseline.version})
- **Time Change**: {comparison['time_change']:+.1f}%
- **Memory Change**: {comparison['memory_change']:+.1f}%
- **Throughput Change**: {comparison['throughput_change']:+.1f}%
"""

        # Performance targets
        report_content += """
## Performance Targets

| Metric | Target | Status |
|--------|--------|---------|
| P95 Latency | < 200ms | TBD |
| Memory Usage | < 500MB | TBD |
| Throughput | > 100 ops/s | TBD |
| CPU Usage | < 80% | TBD |

## Recommendations

Based on the benchmark results:

1. **Performance Hotspots**: Identify functions with > 100ms execution time
2. **Memory Optimization**: Consider memory usage > 100MB per operation
3. **Throughput**: Target > 100 operations per second for core functions
4. **Caching**: Implement caching for frequently called operations

## Next Steps

1. Set up continuous benchmarking in CI/CD
2. Establish performance regression alerts
3. Optimize identified bottlenecks
4. Update baselines after optimizations
"""

        output_path.write_text(report_content)
        logger.info(f"Benchmark report generated: {output_path}")


# Main benchmark execution function
async def run_comprehensive_benchmarks(output_dir: Path) -> dict[str, BenchmarkSuite]:
    """Run comprehensive performance benchmarks.

    Args:
        output_dir: Directory to save benchmark results

    Returns:
        Dictionary of benchmark suites
    """
    output_dir.mkdir(exist_ok=True)

    benchmark_suite = PerformanceBenchmarkSuite()
    reporter = BenchmarkReporter()

    # Load existing baselines
    baseline_file = output_dir / "baselines.json"
    benchmark_suite.load_baselines_from_file(baseline_file)

    results = {}

    # Run core benchmarks
    logger.info("Running core benchmarks...")
    core_suite = await benchmark_suite.run_core_benchmarks()
    results["core"] = core_suite

    # Run agent benchmarks
    logger.info("Running agent benchmarks...")
    agent_suite = await benchmark_suite.run_agent_benchmarks()
    results["agents"] = agent_suite

    # Generate reports
    timestamp = int(time.time())

    core_report_path = output_dir / f"core_benchmark_report_{timestamp}.md"
    reporter.generate_report(core_suite, core_report_path, benchmark_suite.baselines)

    agent_report_path = output_dir / f"agent_benchmark_report_{timestamp}.md"
    reporter.generate_report(agent_suite, agent_report_path, benchmark_suite.baselines)

    # Save new baselines if they don't exist
    for benchmark in core_suite.benchmarks + agent_suite.benchmarks:
        if benchmark.name not in benchmark_suite.baselines:
            benchmark_suite.save_baseline(benchmark, "1.0.0")

    # Save updated baselines
    benchmark_suite.save_baselines_to_file(baseline_file)

    logger.info(f"Benchmark results saved to {output_dir}")
    return results
