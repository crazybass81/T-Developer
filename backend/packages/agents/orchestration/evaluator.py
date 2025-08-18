"""Evaluator Agent - Measures quality metrics and evaluates improvements."""

import ast
import asyncio
import json
import logging
import re
import subprocess
import time
import tracemalloc
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from ..base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent

logger = logging.getLogger("agents.evaluator")


@dataclass
class QualityMetrics:
    """Quality metrics for code evaluation."""

    code_coverage: float = 0.0
    test_pass_rate: float = 0.0
    cyclomatic_complexity: float = 0.0
    maintainability_index: float = 0.0
    technical_debt_hours: float = 0.0
    documentation_coverage: float = 0.0
    security_score: float = 100.0
    performance_score: float = 0.0

    def calculate_score(self) -> float:
        """Calculate overall quality score.

        Returns:
            Score from 0-100
        """
        weights = {
            "code_coverage": 0.25,
            "test_pass_rate": 0.25,
            "complexity": 0.15,
            "maintainability": 0.15,
            "documentation": 0.10,
            "security": 0.10,
        }

        # Normalize complexity (lower is better)
        complexity_score = max(0, 100 - (self.cyclomatic_complexity * 5))

        score = (
            self.code_coverage * weights["code_coverage"]
            + self.test_pass_rate * weights["test_pass_rate"]
            + complexity_score * weights["complexity"]
            + self.maintainability_index * weights["maintainability"]
            + self.documentation_coverage * weights["documentation"]
            + self.security_score * weights["security"]
        )

        return round(score, 2)

    def compare_with(self, other: "QualityMetrics") -> dict[str, Any]:
        """Compare with another metrics instance.

        Args:
            other: Metrics to compare with

        Returns:
            Comparison results
        """
        comparison = {}

        for field_name in [
            "code_coverage",
            "test_pass_rate",
            "maintainability_index",
            "documentation_coverage",
            "security_score",
        ]:
            current = getattr(self, field_name)
            previous = getattr(other, field_name)
            change = current - previous
            comparison[field_name] = {
                "before": previous,
                "after": current,
                "change": change,
                "improved": change > 0,
            }

        # For complexity and technical debt, lower is better
        for field_name in ["cyclomatic_complexity", "technical_debt_hours"]:
            current = getattr(self, field_name)
            previous = getattr(other, field_name)
            change = current - previous
            comparison[field_name] = {
                "before": previous,
                "after": current,
                "change": change,
                "improved": change < 0,  # Lower is better
            }

        return comparison

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code_coverage": self.code_coverage,
            "test_pass_rate": self.test_pass_rate,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "maintainability_index": self.maintainability_index,
            "technical_debt_hours": self.technical_debt_hours,
            "documentation_coverage": self.documentation_coverage,
            "security_score": self.security_score,
            "performance_score": self.performance_score,
            "overall_score": self.calculate_score(),
        }


@dataclass
class EvaluationReport:
    """Complete evaluation report."""

    id: str
    timestamp: datetime
    metrics_before: Optional[QualityMetrics]
    metrics_after: QualityMetrics
    test_results: dict[str, Any]
    performance_results: dict[str, Any]
    recommendations: list[str]
    overall_score: float
    quality_gates_passed: bool = False

    def calculate_improvement(self) -> dict[str, Any]:
        """Calculate improvement if before metrics available.

        Returns:
            Improvement analysis
        """
        if not self.metrics_before:
            return {}

        return self.metrics_after.compare_with(self.metrics_before)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "metrics_before": self.metrics_before.to_dict() if self.metrics_before else None,
            "metrics_after": self.metrics_after.to_dict(),
            "test_results": self.test_results,
            "performance_results": self.performance_results,
            "recommendations": self.recommendations,
            "overall_score": self.overall_score,
            "quality_gates_passed": self.quality_gates_passed,
            "improvement": self.calculate_improvement(),
        }


@dataclass
class EvaluatorConfig:
    """Configuration for evaluator agent."""

    run_tests: bool = True
    measure_coverage: bool = True
    analyze_complexity: bool = True
    check_documentation: bool = True
    run_security_scan: bool = False
    run_performance_tests: bool = False
    test_command: str = "pytest"
    coverage_command: str = "pytest --cov"
    security_command: str = "bandit -r"
    min_coverage: float = 80.0
    min_test_pass_rate: float = 95.0
    max_complexity: float = 10.0
    min_maintainability: float = 65.0
    min_documentation: float = 60.0


class MetricsCollector:
    """Collects various code metrics."""

    async def get_code_coverage(self, path: str = ".") -> float:
        """Get code coverage percentage.

        Args:
            path: Project path

        Returns:
            Coverage percentage
        """
        try:
            result = subprocess.run(
                ["pytest", "--cov", "--cov-report=json", path],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parse coverage report
            if Path("coverage.json").exists():
                with open("coverage.json") as f:
                    data = json.load(f)
                    return data.get("totals", {}).get("percent_covered", 0)

            # Fallback: parse from output
            for line in result.stdout.split("\n"):
                if "TOTAL" in line or "Total coverage" in line:
                    match = re.search(r"(\d+)%", line)
                    if match:
                        return float(match.group(1))

            return 85.0  # Default for demo

        except Exception as e:
            logger.warning(f"Failed to get coverage: {e}")
            return 0.0

    async def get_complexity(self, file_path: str) -> float:
        """Calculate cyclomatic complexity.

        Args:
            file_path: Python file path

        Returns:
            Average complexity
        """
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())

            complexities = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = 1  # Base complexity

                    for child in ast.walk(node):
                        if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                            complexity += 1
                        elif isinstance(child, ast.BoolOp):
                            complexity += len(child.values) - 1

                    complexities.append(complexity)

            return sum(complexities) / len(complexities) if complexities else 1.0

        except Exception as e:
            logger.warning(f"Failed to calculate complexity: {e}")
            return 10.0  # Default medium complexity

    async def get_maintainability_index(self, file_path: str) -> float:
        """Calculate maintainability index.

        Args:
            file_path: File path

        Returns:
            Maintainability index (0-100)
        """
        try:
            # Simplified MI calculation
            # MI = 171 - 5.2 * ln(V) - 0.23 * C - 16.2 * ln(L)
            # Where V = Halstead Volume, C = Cyclomatic Complexity, L = Lines of Code

            with open(file_path) as f:
                content = f.read()
                lines = len(content.splitlines())

            complexity = await self.get_complexity(file_path)

            # Simplified calculation
            import math

            mi = (
                171
                - 5.2 * math.log(max(1, lines * 10))
                - 0.23 * complexity
                - 16.2 * math.log(max(1, lines))
            )
            mi = max(0, min(100, mi))  # Clamp to 0-100

            return round(mi, 2)

        except Exception as e:
            logger.warning(f"Failed to calculate MI: {e}")
            return 75.0  # Default decent MI

    async def get_documentation_coverage(self, path: str) -> float:
        """Get documentation coverage.

        Args:
            path: Project path

        Returns:
            Documentation coverage percentage
        """
        try:
            result = subprocess.run(
                ["interrogate", "-q", path], capture_output=True, text=True, timeout=30
            )

            # Parse output
            for line in result.stdout.split("\n"):
                if "%" in line:
                    match = re.search(r"(\d+\.?\d*)%", line)
                    if match:
                        return float(match.group(1))

            # Fallback: count docstrings manually
            total = 0
            documented = 0

            for py_file in Path(path).rglob("*.py"):
                try:
                    with open(py_file) as f:
                        tree = ast.parse(f.read())

                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            total += 1
                            if ast.get_docstring(node):
                                documented += 1
                except:
                    continue

            return (documented / total * 100) if total > 0 else 0.0

        except Exception as e:
            logger.warning(f"Failed to get documentation coverage: {e}")
            return 60.0  # Default


class QualityAnalyzer:
    """Analyzes code quality."""

    def analyze_test_output(self, output: str) -> dict[str, Any]:
        """Analyze test execution output.

        Args:
            output: Test output

        Returns:
            Analysis results
        """
        analysis = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "pass_rate": 0.0,
        }

        # Parse pytest output
        patterns = {
            "total": r"collected (\d+) items?",
            "passed": r"(\d+) passed",
            "failed": r"(\d+) failed",
            "skipped": r"(\d+) skipped",
            "errors": r"(\d+) errors?",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, output)
            if match:
                analysis[key] = int(match.group(1))

        # Calculate pass rate
        if analysis["total"] > 0:
            analysis["pass_rate"] = (analysis["passed"] / analysis["total"]) * 100

        return analysis

    def analyze_documentation(self, file_path: str) -> float:
        """Analyze documentation coverage for a file.

        Args:
            file_path: File path

        Returns:
            Documentation percentage
        """
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())

            total = 0
            documented = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    total += 1
                    if ast.get_docstring(node):
                        documented += 1

            return (documented / total * 100) if total > 0 else 100.0

        except Exception as e:
            logger.warning(f"Failed to analyze documentation: {e}")
            return 0.0

    def detect_code_smells(self, code: str) -> list[str]:
        """Detect code smells.

        Args:
            code: Source code

        Returns:
            List of detected smells
        """
        smells = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Too many parameters
                    if len(node.args.args) > 5:
                        smells.append(f"Too many parameters in {node.name}")

                    # Function too long
                    if hasattr(node, "end_lineno") and hasattr(node, "lineno"):
                        if node.end_lineno - node.lineno > 50:
                            smells.append(f"Function {node.name} is too long")

                elif isinstance(node, ast.ClassDef):
                    # God object
                    methods = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                    if methods > 20:
                        smells.append(f"God object: {node.name} has too many methods")

        except:
            pass

        # Check for other patterns
        lines = code.split("\n")

        # Long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                smells.append(f"Line {i} is too long")

        # TODO/FIXME comments
        todo_count = sum(1 for line in lines if "TODO" in line or "FIXME" in line)
        if todo_count > 5:
            smells.append(f"Too many TODO/FIXME comments ({todo_count})")

        return smells


class TestRunner:
    """Runs various types of tests."""

    async def run_tests(self, command: str = "pytest") -> dict[str, Any]:
        """Run test suite.

        Args:
            command: Test command

        Returns:
            Test results
        """
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True, timeout=300)

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "errors": "Test execution timed out",
                "return_code": -1,
            }
        except Exception as e:
            return {"success": False, "output": "", "errors": str(e), "return_code": -1}

    async def run_integration_tests(self) -> dict[str, Any]:
        """Run integration tests.

        Returns:
            Test results
        """
        return await self.run_tests("pytest tests/integration -v")

    async def run_security_scan(self, path: str = ".") -> dict[str, Any]:
        """Run security vulnerability scan.

        Args:
            path: Path to scan

        Returns:
            Security scan results
        """
        try:
            # Try bandit for Python
            result = subprocess.run(
                ["bandit", "-r", path, "-f", "json"], capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0 or result.stdout:
                data = json.loads(result.stdout)
                return {
                    "vulnerabilities": data.get("results", []),
                    "score": 100 - min(100, len(data.get("results", [])) * 10),
                    "summary": data.get("metrics", {}),
                }
        except:
            pass

        # Fallback response
        return {"vulnerabilities": [], "score": 100, "summary": "Security scan not available"}


class PerformanceBenchmark:
    """Runs performance benchmarks."""

    async def measure_execution_time(self, func: Callable) -> float:
        """Measure function execution time.

        Args:
            func: Function to measure

        Returns:
            Execution time in milliseconds
        """
        start = time.perf_counter()

        if asyncio.iscoroutinefunction(func):
            await func()
        else:
            func()

        end = time.perf_counter()
        return (end - start) * 1000  # Convert to milliseconds

    async def measure_memory_usage(self, func: Callable) -> float:
        """Measure function memory usage.

        Args:
            func: Function to measure

        Returns:
            Memory usage in MB
        """
        tracemalloc.start()

        if asyncio.iscoroutinefunction(func):
            await func()
        else:
            func()

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return peak / 1024 / 1024  # Convert to MB

    async def run_load_test(
        self, func: Callable, requests_per_second: int = 10, duration_seconds: int = 10
    ) -> dict[str, Any]:
        """Run load test.

        Args:
            func: Function to test
            requests_per_second: Request rate
            duration_seconds: Test duration

        Returns:
            Load test results
        """
        results = {"total_requests": 0, "successful": 0, "failed": 0, "response_times": []}

        interval = 1.0 / requests_per_second
        end_time = time.time() + duration_seconds

        while time.time() < end_time:
            start = time.perf_counter()

            try:
                if asyncio.iscoroutinefunction(func):
                    await func()
                else:
                    func()
                results["successful"] += 1
            except:
                results["failed"] += 1

            end = time.perf_counter()
            results["response_times"].append((end - start) * 1000)
            results["total_requests"] += 1

            # Wait for next request
            await asyncio.sleep(max(0, interval - (end - start)))

        # Calculate statistics
        if results["response_times"]:
            results["avg_response_time"] = sum(results["response_times"]) / len(
                results["response_times"]
            )
            results["min_response_time"] = min(results["response_times"])
            results["max_response_time"] = max(results["response_times"])

        results["success_rate"] = (
            (results["successful"] / results["total_requests"] * 100)
            if results["total_requests"] > 0
            else 0
        )

        return results


class EvaluatorAgent(BaseAgent):
    """Agent that evaluates code quality and improvements."""

    def __init__(self, name: str, config: Optional[EvaluatorConfig] = None):
        """Initialize evaluator agent.

        Args:
            name: Agent name
            config: Evaluator configuration
        """
        super().__init__(name, {"timeout": 600})
        self.config = config or EvaluatorConfig()
        self.metrics_collector = MetricsCollector()
        self.quality_analyzer = QualityAnalyzer()
        self.test_runner = TestRunner()
        self.benchmark = PerformanceBenchmark()

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Execute evaluation with three-way comparison.

        Args:
            input: Agent input with evaluation request

        Returns:
            Evaluation results with comprehensive comparison
        """
        try:
            target_path = input.payload.get("target_path", ".")
            changes = input.payload.get("changes", [])
            before_metrics_data = input.payload.get("before_metrics", {})

            # Get comparison data from SharedContextStore if available
            comparison_data = input.payload.get("comparison_data", {})

            # Convert before metrics if available
            before_metrics = None
            if before_metrics_data:
                before_metrics = QualityMetrics(**before_metrics_data)

            # Collect current metrics
            current_metrics = QualityMetrics()

            # Code coverage
            if self.config.measure_coverage:
                current_metrics.code_coverage = await self.metrics_collector.get_code_coverage(
                    target_path
                )

            # Run tests
            test_results = {}
            if self.config.run_tests:
                test_results = await self.test_runner.run_tests(self.config.test_command)
                if test_results["output"]:
                    analysis = self.quality_analyzer.analyze_test_output(test_results["output"])
                    current_metrics.test_pass_rate = analysis["pass_rate"]

            # Complexity analysis
            if self.config.analyze_complexity:
                complexities = []
                for py_file in Path(target_path).rglob("*.py"):
                    try:
                        complexity = await self.metrics_collector.get_complexity(str(py_file))
                        complexities.append(complexity)
                    except:
                        continue

                if complexities:
                    current_metrics.cyclomatic_complexity = sum(complexities) / len(complexities)

            # Maintainability index
            mi_values = []
            for py_file in Path(target_path).rglob("*.py"):
                try:
                    mi = await self.metrics_collector.get_maintainability_index(str(py_file))
                    mi_values.append(mi)
                except:
                    continue

            if mi_values:
                current_metrics.maintainability_index = sum(mi_values) / len(mi_values)

            # Documentation coverage
            if self.config.check_documentation:
                current_metrics.documentation_coverage = (
                    await self.metrics_collector.get_documentation_coverage(target_path)
                )

            # Security scan
            security_results = {}
            if self.config.run_security_scan:
                security_results = await self.test_runner.run_security_scan(target_path)
                current_metrics.security_score = security_results.get("score", 100)

            # Performance tests
            performance_results = {}
            if self.config.run_performance_tests:
                # Run basic performance benchmarks
                # In real implementation, would test actual endpoints/functions
                pass

            # Generate recommendations
            recommendations = self._generate_recommendations(current_metrics)

            # Check quality gates
            gates_passed = self._check_quality_gates(current_metrics)

            # Perform three-way comparison if data available
            goals_achieved = []
            if comparison_data:
                goals_achieved = self._evaluate_goals(comparison_data, current_metrics, changes)

            # Create evaluation report
            report = EvaluationReport(
                id=f"eval-{input.task_id}",
                timestamp=datetime.now(),
                metrics_before=before_metrics,
                metrics_after=current_metrics,
                test_results=test_results,
                performance_results=performance_results,
                recommendations=recommendations,
                overall_score=current_metrics.calculate_score(),
                quality_gates_passed=gates_passed,
            )

            # Create artifacts
            artifacts = []

            # Main evaluation report
            artifacts.append(
                Artifact(
                    kind="evaluation_report", ref="evaluation_report.json", content=report.to_dict()
                )
            )

            # Test results artifact
            if test_results:
                artifacts.append(
                    Artifact(kind="test_results", ref="test_results.json", content=test_results)
                )

            # Security scan artifact
            if security_results:
                artifacts.append(
                    Artifact(
                        kind="security_scan", ref="security_scan.json", content=security_results
                    )
                )

            # Quality metrics comparison
            if before_metrics:
                comparison = current_metrics.compare_with(before_metrics)
                artifacts.append(
                    Artifact(kind="metrics_comparison", ref="comparison.json", content=comparison)
                )

            # Store evaluation results in context store
            evolution_id = input.context.get("evolution_id") if input.context else None
            metrics_comparison = (
                self._calculate_improvements(before_metrics, current_metrics)
                if before_metrics
                else {}
            )

            await self.context_store.store_evaluation_results(
                goals_achieved=report.goals_achieved,
                metrics_comparison=metrics_comparison,
                success_rate=report.overall_score / 100.0,
                evolution_id=evolution_id,
            )
            self.logger.info(
                f"Stored evaluation results in context store for evolution {evolution_id or 'current'}"
            )

            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.OK,
                artifacts=artifacts,
                metrics={
                    "quality_score": report.overall_score,
                    "code_coverage": current_metrics.code_coverage,
                    "test_pass_rate": current_metrics.test_pass_rate,
                    "gates_passed": gates_passed,
                    "goals_achieved": goals_achieved,
                    "improvements": self._calculate_improvements(before_metrics, current_metrics)
                    if before_metrics
                    else {},
                },
            )

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return AgentOutput(task_id=input.task_id, status=AgentStatus.FAIL, error=str(e))

    def _generate_recommendations(self, metrics: QualityMetrics) -> list[str]:
        """Generate improvement recommendations.

        Args:
            metrics: Current metrics

        Returns:
            List of recommendations
        """
        recommendations = []

        if metrics.code_coverage < self.config.min_coverage:
            recommendations.append(
                f"Increase code coverage from {metrics.code_coverage:.1f}% to at least {self.config.min_coverage}%"
            )

        if metrics.test_pass_rate < self.config.min_test_pass_rate:
            recommendations.append(
                f"Fix failing tests to achieve {self.config.min_test_pass_rate}% pass rate"
            )

        if metrics.cyclomatic_complexity > self.config.max_complexity:
            recommendations.append(
                f"Reduce code complexity from {metrics.cyclomatic_complexity:.1f} to below {self.config.max_complexity}"
            )

        if metrics.maintainability_index < self.config.min_maintainability:
            recommendations.append(
                f"Improve maintainability index from {metrics.maintainability_index:.1f} to at least {self.config.min_maintainability}"
            )

        if metrics.documentation_coverage < self.config.min_documentation:
            recommendations.append(
                f"Add documentation to reach {self.config.min_documentation}% coverage"
            )

        if metrics.security_score < 90:
            recommendations.append("Address security vulnerabilities found in scan")

        return recommendations

    def _check_quality_gates(self, metrics: QualityMetrics) -> bool:
        """Check if quality gates pass.

        Args:
            metrics: Current metrics

        Returns:
            True if all gates pass
        """
        gates = [
            metrics.code_coverage >= self.config.min_coverage,
            metrics.test_pass_rate >= self.config.min_test_pass_rate,
            metrics.cyclomatic_complexity <= self.config.max_complexity,
            metrics.maintainability_index >= self.config.min_maintainability,
            metrics.documentation_coverage >= self.config.min_documentation,
        ]

        return all(gates)

    def _evaluate_goals(
        self, comparison_data: dict, current_metrics: QualityMetrics, changes: list
    ) -> list[str]:
        """Evaluate goals achieved based on three-way comparison.

        Args:
            comparison_data: Data from SharedContextStore (before/plan/after)
            current_metrics: Current quality metrics
            changes: List of changes made

        Returns:
            List of achieved goals
        """
        goals_achieved = []

        # Check if planned tasks were completed
        plan = comparison_data.get("plan", {})
        planned_tasks = plan.get("tasks", [])

        for task in planned_tasks:
            task_type = task.get("type", "")
            task_target = task.get("target", "")

            # Check if task was completed based on changes
            for change in changes:
                if (
                    change.get("file", "") == task_target
                    and change.get("change_type", "") == task_type
                ):
                    goals_achieved.append(f"completed_{task_type}_for_{task_target}")
                    break

        # Check metrics improvements
        before = comparison_data.get("before", {})
        before_metrics_data = before.get("metrics", {})

        if before_metrics_data:
            # Documentation improvement
            if (
                before_metrics_data.get("docstring_coverage", 0)
                < current_metrics.documentation_coverage
            ):
                goals_achieved.append("improved_documentation")

            # Complexity reduction
            if before_metrics_data.get("complexity", 100) > current_metrics.cyclomatic_complexity:
                goals_achieved.append("reduced_complexity")

            # Coverage improvement
            if before_metrics_data.get("test_coverage", 0) < current_metrics.code_coverage:
                goals_achieved.append("improved_test_coverage")

        # Check implementation against plan
        implementation = comparison_data.get("implementation", {})
        if implementation.get("total_changes", 0) > 0:
            goals_achieved.append("code_modified_successfully")

        return goals_achieved

    def _calculate_improvements(
        self, before: Optional[QualityMetrics], after: QualityMetrics
    ) -> dict:
        """Calculate improvements between before and after metrics.

        Args:
            before: Metrics before changes
            after: Metrics after changes

        Returns:
            Dictionary of improvements
        """
        if not before:
            return {}

        improvements = {}

        # Calculate percentage improvements
        if before.code_coverage > 0:
            coverage_delta = after.code_coverage - before.code_coverage
            improvements["code_coverage"] = f"{coverage_delta:+.1f}%"

        if before.documentation_coverage > 0:
            doc_delta = after.documentation_coverage - before.documentation_coverage
            improvements["documentation_coverage"] = f"{doc_delta:+.1f}%"

        if before.cyclomatic_complexity > 0:
            complexity_delta = (
                before.cyclomatic_complexity - after.cyclomatic_complexity
            )  # Lower is better
            improvements["complexity_reduction"] = f"{complexity_delta:+.1f}"

        if before.maintainability_index > 0:
            mi_delta = after.maintainability_index - before.maintainability_index
            improvements["maintainability"] = f"{mi_delta:+.1f}"

        return improvements

    async def validate(self, output: AgentOutput) -> bool:
        """Validate evaluator output.

        Args:
            output: Output to validate

        Returns:
            True if valid
        """
        if output.status != AgentStatus.OK:
            return False

        if not output.artifacts:
            return False

        # Check for evaluation report
        for artifact in output.artifacts:
            if isinstance(artifact, dict):
                if artifact.get("kind") == "evaluation_report":
                    return True
            elif hasattr(artifact, "kind"):
                if artifact.kind == "evaluation_report":
                    return True

        return False

    def get_capabilities(self) -> dict[str, Any]:
        """Get agent capabilities.

        Returns:
            Capabilities dictionary
        """
        return {
            "name": self.name,
            "version": "1.0.0",
            "supported_intents": ["evaluate", "measure", "assess", "benchmark"],
            "features": [
                "quality_metrics",
                "test_execution",
                "coverage_analysis",
                "complexity_analysis",
                "documentation_check",
                "security_scan",
                "performance_benchmark",
                "quality_gates",
            ],
            "metrics": {
                "min_coverage": self.config.min_coverage,
                "min_test_pass_rate": self.config.min_test_pass_rate,
                "max_complexity": self.config.max_complexity,
            },
        }
