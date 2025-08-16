"""Tests for Evaluator Agent - TDD approach."""

import asyncio
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from packages.agents.base import AgentInput, AgentOutput, AgentStatus
from packages.agents.evaluator import (
    EvaluationReport,
    EvaluatorAgent,
    EvaluatorConfig,
    MetricsCollector,
    PerformanceBenchmark,
    QualityAnalyzer,
    QualityMetrics,
    TestRunner,
)


class TestQualityMetrics:
    """Test QualityMetrics dataclass."""

    def test_metrics_creation(self):
        """Test creating quality metrics."""
        metrics = QualityMetrics(
            code_coverage=85.5,
            test_pass_rate=95.0,
            cyclomatic_complexity=12,
            maintainability_index=75,
            technical_debt_hours=10.5,
            documentation_coverage=60.0,
        )

        assert metrics.code_coverage == 85.5
        assert metrics.test_pass_rate == 95.0
        assert metrics.cyclomatic_complexity == 12
        assert metrics.maintainability_index == 75

    def test_metrics_scoring(self):
        """Test calculating overall quality score."""
        metrics = QualityMetrics(
            code_coverage=80,
            test_pass_rate=100,
            cyclomatic_complexity=10,
            maintainability_index=80,
            documentation_coverage=70,
        )

        score = metrics.calculate_score()
        assert 0 <= score <= 100
        assert score > 70  # Good metrics should have high score

    def test_metrics_comparison(self):
        """Test comparing before/after metrics."""
        before = QualityMetrics(
            code_coverage=60, test_pass_rate=80, cyclomatic_complexity=20, maintainability_index=60
        )

        after = QualityMetrics(
            code_coverage=85, test_pass_rate=95, cyclomatic_complexity=12, maintainability_index=75
        )

        improvement = after.compare_with(before)
        assert improvement["code_coverage"]["change"] == 25
        assert improvement["code_coverage"]["improved"] is True
        assert improvement["cyclomatic_complexity"]["improved"] is True  # Lower is better


class TestMetricsCollector:
    """Test metrics collector."""

    @pytest.fixture
    def collector(self):
        """Create metrics collector."""
        return MetricsCollector()

    @pytest.mark.asyncio
    async def test_collect_code_coverage(self, collector, tmp_path):
        """Test collecting code coverage metrics."""
        # Create mock coverage file
        coverage_file = tmp_path / ".coverage"
        coverage_data = {
            "files": {
                "main.py": {"executed_lines": 80, "total_lines": 100},
                "utils.py": {"executed_lines": 45, "total_lines": 50},
            }
        }
        coverage_file.write_text(json.dumps(coverage_data))

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Total coverage: 85%")

            coverage = await collector.get_code_coverage(str(tmp_path))

            assert coverage > 0
            assert coverage <= 100

    @pytest.mark.asyncio
    async def test_collect_complexity_metrics(self, collector, tmp_path):
        """Test collecting complexity metrics."""
        test_file = tmp_path / "complex.py"
        test_file.write_text(
            """
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
        )

        complexity = await collector.get_complexity(str(test_file))

        assert complexity > 1  # Has conditional statements
        assert complexity < 100  # Not insanely complex

    @pytest.mark.asyncio
    async def test_collect_maintainability_index(self, collector, tmp_path):
        """Test calculating maintainability index."""
        test_file = tmp_path / "sample.py"
        test_file.write_text(
            """
def hello():
    '''Say hello.'''
    return "Hello, World!"

def goodbye():
    return "Goodbye!"
"""
        )

        mi = await collector.get_maintainability_index(str(test_file))

        assert 0 <= mi <= 100
        assert mi > 50  # Simple code should have decent MI


class TestQualityAnalyzer:
    """Test quality analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create quality analyzer."""
        return QualityAnalyzer()

    def test_analyze_test_results(self, analyzer):
        """Test analyzing test results."""
        test_output = """
============================= test session starts ==============================
collected 50 items

tests/test_main.py::test_function1 PASSED                                [ 2%]
tests/test_main.py::test_function2 PASSED                                [ 4%]
tests/test_main.py::test_function3 FAILED                               [ 6%]
tests/test_utils.py::test_helper PASSED                                  [ 8%]

========================= 47 passed, 3 failed in 2.5s ==========================
"""

        analysis = analyzer.analyze_test_output(test_output)

        assert analysis["total"] == 50
        assert analysis["passed"] == 47
        assert analysis["failed"] == 3
        assert analysis["pass_rate"] == 94.0

    def test_analyze_documentation(self, analyzer, tmp_path):
        """Test analyzing documentation coverage."""
        test_file = tmp_path / "documented.py"
        test_file.write_text(
            '''
def documented():
    """This function is documented."""
    pass

def undocumented():
    pass

class DocumentedClass:
    """This class is documented."""

    def method(self):
        """This method is documented."""
        pass
'''
        )

        doc_coverage = analyzer.analyze_documentation(str(test_file))

        assert doc_coverage > 0
        assert doc_coverage <= 100
        assert doc_coverage > 60  # Most items are documented

    def test_detect_code_smells(self, analyzer):
        """Test detecting code smells."""
        code = """
def very_long_function_with_many_parameters(a, b, c, d, e, f, g, h):
    # Too many parameters
    x = 1
    y = 2
    z = 3
    # ... lots of code ...
    return x + y + z

class GodObject:
    def __init__(self):
        self.a = 1
        self.b = 2
        # ... 20+ attributes ...

    def method1(self): pass
    def method2(self): pass
    # ... 30+ methods ...
"""

        smells = analyzer.detect_code_smells(code)

        assert len(smells) > 0
        assert any("parameters" in smell.lower() for smell in smells)


class TestTestRunner:
    """Test test runner."""

    @pytest.fixture
    def runner(self):
        """Create test runner."""
        return TestRunner()

    @pytest.mark.asyncio
    async def test_run_unit_tests(self, runner):
        """Test running unit tests."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="All tests passed", stderr="")

            result = await runner.run_tests("pytest")

            assert result["success"] is True
            assert "All tests passed" in result["output"]

    @pytest.mark.asyncio
    async def test_run_integration_tests(self, runner):
        """Test running integration tests."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Integration tests: OK")

            result = await runner.run_integration_tests()

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_run_security_scan(self, runner):
        """Test running security scan."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=json.dumps({"vulnerabilities": [], "score": 100})
            )

            result = await runner.run_security_scan()

            assert result["vulnerabilities"] == []
            assert result["score"] == 100


class TestPerformanceBenchmark:
    """Test performance benchmark."""

    @pytest.fixture
    def benchmark(self):
        """Create performance benchmark."""
        return PerformanceBenchmark()

    @pytest.mark.asyncio
    async def test_measure_execution_time(self, benchmark):
        """Test measuring execution time."""

        async def sample_function():
            await asyncio.sleep(0.01)
            return "done"

        time_ms = await benchmark.measure_execution_time(sample_function)

        assert time_ms > 10  # At least 10ms
        assert time_ms < 100  # But not too long

    @pytest.mark.asyncio
    async def test_measure_memory_usage(self, benchmark):
        """Test measuring memory usage."""

        def memory_function():
            data = [i for i in range(1000)]
            return sum(data)

        memory_mb = await benchmark.measure_memory_usage(memory_function)

        assert memory_mb > 0
        assert memory_mb < 100  # Reasonable memory usage

    @pytest.mark.asyncio
    async def test_run_load_test(self, benchmark):
        """Test running load test."""

        async def api_endpoint():
            await asyncio.sleep(0.001)
            return {"status": "ok"}

        results = await benchmark.run_load_test(
            api_endpoint, requests_per_second=10, duration_seconds=1
        )

        assert results["total_requests"] >= 10
        assert results["success_rate"] > 0
        assert "avg_response_time" in results


class TestEvaluationReport:
    """Test evaluation report."""

    def test_report_creation(self):
        """Test creating evaluation report."""
        metrics = QualityMetrics(
            code_coverage=85, test_pass_rate=95, cyclomatic_complexity=10, maintainability_index=75
        )

        report = EvaluationReport(
            id="eval-001",
            timestamp=datetime.now(),
            metrics_before=None,
            metrics_after=metrics,
            test_results={"passed": 95, "failed": 5},
            performance_results={},
            recommendations=["Improve documentation", "Add more tests"],
            overall_score=85.0,
        )

        assert report.id == "eval-001"
        assert report.overall_score == 85.0
        assert len(report.recommendations) == 2

    def test_report_with_comparison(self):
        """Test report with before/after comparison."""
        before = QualityMetrics(code_coverage=60)
        after = QualityMetrics(code_coverage=85)

        report = EvaluationReport(
            id="eval-002",
            timestamp=datetime.now(),
            metrics_before=before,
            metrics_after=after,
            test_results={},
            performance_results={},
            recommendations=[],
            overall_score=85.0,
        )

        improvement = report.calculate_improvement()
        assert improvement["code_coverage"]["improved"] is True
        assert improvement["code_coverage"]["change"] == 25


class TestEvaluatorConfig:
    """Test evaluator configuration."""

    def test_default_config(self):
        """Test default configuration."""
        config = EvaluatorConfig()

        assert config.run_tests is True
        assert config.measure_coverage is True
        assert config.analyze_complexity is True
        assert config.check_documentation is True
        assert config.min_coverage == 80
        assert config.max_complexity == 10

    def test_custom_config(self):
        """Test custom configuration."""
        config = EvaluatorConfig(
            run_tests=False, min_coverage=90, max_complexity=5, run_security_scan=True
        )

        assert config.run_tests is False
        assert config.min_coverage == 90
        assert config.max_complexity == 5
        assert config.run_security_scan is True


class TestEvaluatorAgent:
    """Test evaluator agent."""

    @pytest.fixture
    def agent(self):
        """Create evaluator agent."""
        config = EvaluatorConfig(
            run_tests=True,
            measure_coverage=True,
            run_performance_tests=False,  # Disable for testing
        )
        return EvaluatorAgent("evaluator", config)

    @pytest.mark.asyncio
    async def test_evaluate_changes(self, agent):
        """Test evaluating code changes."""
        input_data = AgentInput(
            intent="evaluate",
            task_id="test-001",
            payload={
                "changes": [
                    {"file": "main.py", "type": "modify", "description": "Added type hints"}
                ],
                "target_path": ".",
                "before_metrics": {"code_coverage": 60, "test_pass_rate": 85},
            },
        )

        with patch.object(agent.metrics_collector, "get_code_coverage") as mock_coverage:
            mock_coverage.return_value = 85.0

            with patch.object(agent.test_runner, "run_tests") as mock_tests:
                mock_tests.return_value = {"success": True, "output": "All tests passed"}

                output = await agent.execute(input_data)

                assert output.status == AgentStatus.OK
                assert len(output.artifacts) > 0
                assert any(a.kind == "evaluation_report" for a in output.artifacts)

    @pytest.mark.asyncio
    async def test_validate_output(self, agent):
        """Test output validation."""
        valid_output = AgentOutput(
            task_id="test-002",
            status=AgentStatus.OK,
            artifacts=[
                {
                    "kind": "evaluation_report",
                    "ref": "report.json",
                    "content": {"overall_score": 85},
                }
            ],
            metrics={"quality_score": 85},
        )

        assert await agent.validate(valid_output) is True

        invalid_output = AgentOutput(
            task_id="test-003", status=AgentStatus.OK, artifacts=[], metrics={}
        )

        assert await agent.validate(invalid_output) is False

    def test_get_capabilities(self, agent):
        """Test capabilities declaration."""
        capabilities = agent.get_capabilities()

        assert capabilities["name"] == "evaluator"
        assert "evaluate" in capabilities["supported_intents"]
        assert "quality_metrics" in capabilities["features"]
        assert "test_execution" in capabilities["features"]
