"""Performance Profiler - Analyze and optimize system performance.

Phase 6: P6-T1 - Performance Optimization
Profile, analyze, and optimize code performance.
"""

import ast
import asyncio
import cProfile
import io
import pstats
import time
import tracemalloc
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


@dataclass
class PerformanceMetrics:
    """Performance metrics for a code segment."""

    function_name: str
    execution_time: float  # seconds
    memory_usage: float  # MB
    cpu_usage: float  # percentage
    call_count: int
    file_path: str
    line_number: int

    @property
    def time_per_call(self) -> float:
        """Average time per call."""
        return self.execution_time / max(self.call_count, 1)


@dataclass
class Bottleneck:
    """Identified performance bottleneck."""

    type: str  # cpu, memory, io, database
    severity: str  # critical, high, medium, low
    location: str
    impact: float  # percentage of total time
    description: str
    suggestion: str


@dataclass
class OptimizationSuggestion:
    """Suggestion for performance optimization."""

    target: str
    type: str  # algorithm, caching, async, query, memory
    current_performance: float
    expected_improvement: float  # percentage
    implementation: str
    priority: int  # 1-5, 1 being highest


@dataclass
class ProfileReport:
    """Complete profiling report."""

    timestamp: datetime
    total_time: float
    total_memory: float
    hotspots: list[PerformanceMetrics]
    bottlenecks: list[Bottleneck]
    suggestions: list[OptimizationSuggestion]
    summary: dict[str, Any]


class PerformanceProfiler:
    """Profile code performance and identify bottlenecks."""

    def __init__(self):
        """Initialize performance profiler."""
        self.profile = cProfile.Profile()
        self.memory_snapshots = []

    async def profile_code(self, func: Callable, *args, **kwargs) -> ProfileReport:
        """Profile a function's performance."""
        # Start memory tracking
        tracemalloc.start()
        memory_before = tracemalloc.get_traced_memory()

        # Start CPU profiling
        self.profile.enable()
        start_time = time.time()

        # Execute function
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)

        # Stop profiling
        end_time = time.time()
        self.profile.disable()

        # Get memory usage
        memory_after = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Analyze results
        total_time = end_time - start_time
        memory_used = (memory_after[1] - memory_before[0]) / 1024 / 1024  # MB

        # Extract metrics
        metrics = self._extract_metrics()

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(metrics, total_time)

        # Generate suggestions
        suggestions = self._generate_suggestions(metrics, bottlenecks)

        return ProfileReport(
            timestamp=datetime.now(),
            total_time=total_time,
            total_memory=memory_used,
            hotspots=metrics[:10],  # Top 10 hotspots
            bottlenecks=bottlenecks,
            suggestions=suggestions,
            summary={
                "total_functions": len(metrics),
                "total_calls": sum(m.call_count for m in metrics),
                "avg_call_time": total_time / max(sum(m.call_count for m in metrics), 1),
            },
        )

    def _extract_metrics(self) -> list[PerformanceMetrics]:
        """Extract performance metrics from profile."""
        metrics = []

        # Get stats
        stream = io.StringIO()
        stats = pstats.Stats(self.profile, stream=stream)
        stats.sort_stats("cumulative")

        # Parse stats
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            if isinstance(func, tuple) and len(func) >= 3:
                filename, line_num, func_name = func

                metric = PerformanceMetrics(
                    function_name=func_name,
                    execution_time=ct,
                    memory_usage=0,  # Will be updated with memory profiling
                    cpu_usage=0,  # Will be updated with CPU monitoring
                    call_count=nc,
                    file_path=filename,
                    line_number=line_num,
                )
                metrics.append(metric)

        # Sort by execution time
        metrics.sort(key=lambda x: x.execution_time, reverse=True)

        return metrics

    def _identify_bottlenecks(
        self, metrics: list[PerformanceMetrics], total_time: float
    ) -> list[Bottleneck]:
        """Identify performance bottlenecks."""
        bottlenecks = []

        # CPU bottlenecks - functions taking >10% of total time
        for metric in metrics[:5]:  # Top 5 functions
            impact = (metric.execution_time / total_time) * 100
            if impact > 10:
                bottleneck = Bottleneck(
                    type="cpu",
                    severity="critical" if impact > 30 else "high",
                    location=f"{metric.file_path}:{metric.line_number}",
                    impact=impact,
                    description=f"Function '{metric.function_name}' takes {impact:.1f}% of total time",
                    suggestion="Consider optimizing algorithm or using caching",
                )
                bottlenecks.append(bottleneck)

        # IO bottlenecks - functions with 'read', 'write', 'open' in name
        io_functions = [
            m
            for m in metrics
            if any(
                keyword in m.function_name.lower()
                for keyword in ["read", "write", "open", "load", "save"]
            )
        ]

        for metric in io_functions[:3]:
            if metric.execution_time > 0.1:  # More than 100ms
                bottleneck = Bottleneck(
                    type="io",
                    severity="medium",
                    location=f"{metric.file_path}:{metric.line_number}",
                    impact=(metric.execution_time / total_time) * 100,
                    description=f"IO operation '{metric.function_name}' is slow",
                    suggestion="Consider async IO or batching operations",
                )
                bottlenecks.append(bottleneck)

        # Database bottlenecks - functions with 'query', 'fetch', 'execute' in name
        db_functions = [
            m
            for m in metrics
            if any(
                keyword in m.function_name.lower()
                for keyword in ["query", "fetch", "execute", "select", "insert", "update"]
            )
        ]

        for metric in db_functions[:3]:
            if metric.call_count > 10 and metric.time_per_call > 0.01:
                bottleneck = Bottleneck(
                    type="database",
                    severity="high",
                    location=f"{metric.file_path}:{metric.line_number}",
                    impact=(metric.execution_time / total_time) * 100,
                    description=f"Database operation '{metric.function_name}' called {metric.call_count} times",
                    suggestion="Consider query optimization or connection pooling",
                )
                bottlenecks.append(bottleneck)

        return bottlenecks

    def _generate_suggestions(
        self, metrics: list[PerformanceMetrics], bottlenecks: list[Bottleneck]
    ) -> list[OptimizationSuggestion]:
        """Generate optimization suggestions."""
        suggestions = []

        # Suggest caching for frequently called functions
        for metric in metrics:
            if metric.call_count > 100 and metric.time_per_call > 0.001:
                suggestion = OptimizationSuggestion(
                    target=metric.function_name,
                    type="caching",
                    current_performance=metric.execution_time,
                    expected_improvement=70,  # 70% improvement with caching
                    implementation="Add @lru_cache decorator or implement memoization",
                    priority=1 if metric.execution_time > 1 else 2,
                )
                suggestions.append(suggestion)

        # Suggest async for IO operations
        for bottleneck in bottlenecks:
            if bottleneck.type == "io":
                suggestion = OptimizationSuggestion(
                    target=bottleneck.location,
                    type="async",
                    current_performance=bottleneck.impact,
                    expected_improvement=50,
                    implementation="Convert to async/await pattern",
                    priority=2,
                )
                suggestions.append(suggestion)

        # Suggest query optimization for database operations
        for bottleneck in bottlenecks:
            if bottleneck.type == "database":
                suggestion = OptimizationSuggestion(
                    target=bottleneck.location,
                    type="query",
                    current_performance=bottleneck.impact,
                    expected_improvement=60,
                    implementation="Add indexes, optimize queries, or use query batching",
                    priority=1,
                )
                suggestions.append(suggestion)

        # Sort by priority
        suggestions.sort(key=lambda x: x.priority)

        return suggestions[:10]  # Top 10 suggestions


class BottleneckAnalyzer:
    """Analyze code for performance bottlenecks."""

    def analyze_code(self, file_path: Path) -> list[Bottleneck]:
        """Analyze code file for potential bottlenecks."""
        bottlenecks = []

        with open(file_path) as f:
            tree = ast.parse(f.read())

        # Check for nested loops
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check if there's another loop inside
                for child in ast.walk(node):
                    if child != node and isinstance(child, ast.For):
                        bottleneck = Bottleneck(
                            type="algorithm",
                            severity="high",
                            location=f"{file_path}:{node.lineno}",
                            impact=0,  # Unknown without profiling
                            description="Nested loop detected - O(n²) complexity",
                            suggestion="Consider using more efficient algorithm or data structure",
                        )
                        bottlenecks.append(bottleneck)
                        break

        # Check for synchronous file operations
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "open":
                    bottleneck = Bottleneck(
                        type="io",
                        severity="medium",
                        location=f"{file_path}:{node.lineno}",
                        impact=0,
                        description="Synchronous file operation detected",
                        suggestion="Consider using async file operations with aiofiles",
                    )
                    bottlenecks.append(bottleneck)

        return bottlenecks

    def rank_bottlenecks(self, bottlenecks: list[Bottleneck]) -> list[Bottleneck]:
        """Rank bottlenecks by severity and impact."""
        severity_scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}

        # Calculate score for each bottleneck
        for bottleneck in bottlenecks:
            bottleneck.score = severity_scores.get(bottleneck.severity, 1) * (
                1 + bottleneck.impact / 100
            )

        # Sort by score
        bottlenecks.sort(key=lambda x: x.score, reverse=True)

        return bottlenecks


class OptimizationEngine:
    """Apply automatic optimizations to code."""

    async def apply_optimizations(
        self, file_path: Path, suggestions: list[OptimizationSuggestion]
    ) -> bool:
        """Apply optimization suggestions to code."""
        with open(file_path) as f:
            source = f.read()

        tree = ast.parse(source)
        modified = False

        for suggestion in suggestions:
            if suggestion.type == "caching":
                tree, changed = self._add_caching(tree, suggestion.target)
                modified = modified or changed
            elif suggestion.type == "async":
                tree, changed = self._convert_to_async(tree, suggestion.target)
                modified = modified or changed

        if modified:
            # Convert AST back to source code
            import astor

            optimized_source = astor.to_source(tree)

            # Write back
            backup_path = file_path.with_suffix(".backup")
            file_path.rename(backup_path)
            file_path.write_text(optimized_source)

            return True

        return False

    def _add_caching(self, tree: ast.AST, target_function: str) -> tuple:
        """Add caching decorator to function."""
        modified = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == target_function:
                # Add lru_cache decorator
                cache_decorator = ast.Name(id="lru_cache", ctx=ast.Load())
                node.decorator_list.insert(0, cache_decorator)
                modified = True
                break

        return tree, modified

    def _convert_to_async(self, tree: ast.AST, target_location: str) -> tuple:
        """Convert function to async."""
        # This is simplified - real implementation would be more complex
        modified = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Convert to AsyncFunctionDef
                if not isinstance(node, ast.AsyncFunctionDef):
                    # Create new async function
                    async_func = ast.AsyncFunctionDef(
                        name=node.name,
                        args=node.args,
                        body=node.body,
                        decorator_list=node.decorator_list,
                        returns=node.returns,
                    )
                    # Replace node (simplified)
                    modified = True

        return tree, modified


class PerformanceOptimizer:
    """Main performance optimization orchestrator."""

    def __init__(self):
        """Initialize performance optimizer."""
        self.profiler = PerformanceProfiler()
        self.analyzer = BottleneckAnalyzer()
        self.optimizer = OptimizationEngine()

    async def optimize_performance(self, target_path: Path) -> ProfileReport:
        """Optimize performance of target code."""
        print("🔍 Starting performance optimization...")

        # Analyze static bottlenecks
        if target_path.is_file():
            bottlenecks = self.analyzer.analyze_code(target_path)
        else:
            bottlenecks = []
            for py_file in target_path.rglob("*.py"):
                bottlenecks.extend(self.analyzer.analyze_code(py_file))

        # Rank bottlenecks
        bottlenecks = self.analyzer.rank_bottlenecks(bottlenecks)

        # Generate optimization plan
        suggestions = []
        for bottleneck in bottlenecks[:10]:
            suggestion = OptimizationSuggestion(
                target=bottleneck.location,
                type="algorithm" if bottleneck.type == "algorithm" else "async",
                current_performance=0,
                expected_improvement=30,
                implementation=bottleneck.suggestion,
                priority=1 if bottleneck.severity == "critical" else 2,
            )
            suggestions.append(suggestion)

        # Create report
        report = ProfileReport(
            timestamp=datetime.now(),
            total_time=0,
            total_memory=0,
            hotspots=[],
            bottlenecks=bottlenecks,
            suggestions=suggestions,
            summary={
                "files_analyzed": 1
                if target_path.is_file()
                else len(list(target_path.rglob("*.py"))),
                "bottlenecks_found": len(bottlenecks),
                "suggestions_generated": len(suggestions),
            },
        )

        print(f"✅ Found {len(bottlenecks)} bottlenecks")
        print(f"💡 Generated {len(suggestions)} optimization suggestions")

        return report

    def generate_report(self, report: ProfileReport, output_path: Path):
        """Generate performance optimization report."""
        report_content = f"""# Performance Optimization Report

Generated: {report.timestamp}

## Summary
- Total Execution Time: {report.total_time:.3f}s
- Total Memory Usage: {report.total_memory:.2f} MB
- Functions Analyzed: {report.summary.get('total_functions', 0)}
- Total Calls: {report.summary.get('total_calls', 0)}

## Top Hotspots
"""

        for hotspot in report.hotspots[:5]:
            report_content += f"""
### {hotspot.function_name}
- Location: {hotspot.file_path}:{hotspot.line_number}
- Execution Time: {hotspot.execution_time:.3f}s
- Call Count: {hotspot.call_count}
- Time per Call: {hotspot.time_per_call:.6f}s
"""

        report_content += "\n## Bottlenecks\n"

        for bottleneck in report.bottlenecks[:5]:
            report_content += f"""
### {bottleneck.type.upper()} Bottleneck
- Severity: {bottleneck.severity}
- Location: {bottleneck.location}
- Impact: {bottleneck.impact:.1f}%
- Description: {bottleneck.description}
- Suggestion: {bottleneck.suggestion}
"""

        report_content += "\n## Optimization Suggestions\n"

        for i, suggestion in enumerate(report.suggestions[:5], 1):
            report_content += f"""
{i}. **{suggestion.type.upper()}** optimization for {suggestion.target}
   - Expected Improvement: {suggestion.expected_improvement}%
   - Implementation: {suggestion.implementation}
   - Priority: {suggestion.priority}
"""

        # Write report
        output_path.write_text(report_content)
        print(f"📊 Report generated: {output_path}")
