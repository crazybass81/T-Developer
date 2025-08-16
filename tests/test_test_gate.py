"""Tests for Test Gate - Automated test coverage and mutation testing."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from packages.evaluation.test_gate import (
    TestGate,
    TestConfig,
    TestResult,
    TestMetrics,
    CoverageAnalyzer,
    MutationTester,
    PropertyTester
)


class TestTestConfig:
    """Test test gate configuration."""
    
    def test_default_config(self):
        """Test default test configuration."""
        config = TestConfig()
        
        assert config.min_coverage == 80.0
        assert config.min_mutation_score == 60.0
        assert config.enable_property_tests is True
        assert config.enable_mutation_tests is True
        assert config.fail_on_low_coverage is True
        assert config.max_test_duration_seconds == 300
        
    def test_custom_config(self):
        """Test custom test configuration."""
        config = TestConfig(
            min_coverage=90.0,
            min_mutation_score=70.0,
            enable_property_tests=False
        )
        
        assert config.min_coverage == 90.0
        assert config.min_mutation_score == 70.0
        assert config.enable_property_tests is False


class TestTestMetrics:
    """Test test metrics data model."""
    
    def test_metrics_creation(self):
        """Test creating test metrics."""
        metrics = TestMetrics(
            line_coverage=85.5,
            branch_coverage=75.0,
            mutation_score=65.0,
            total_tests=100,
            passed_tests=95,
            failed_tests=5,
            skipped_tests=0,
            test_duration_seconds=45.5
        )
        
        assert metrics.line_coverage == 85.5
        assert metrics.branch_coverage == 75.0
        assert metrics.mutation_score == 65.0
        assert metrics.total_tests == 100
        
    def test_metrics_passes_thresholds(self):
        """Test checking if metrics pass thresholds."""
        config = TestConfig(
            min_coverage=80.0,
            min_mutation_score=60.0
        )
        
        good_metrics = TestMetrics(
            line_coverage=85.0,
            branch_coverage=80.0,
            mutation_score=65.0
        )
        
        bad_metrics = TestMetrics(
            line_coverage=75.0,  # Below threshold
            branch_coverage=70.0,
            mutation_score=55.0  # Below threshold
        )
        
        assert good_metrics.passes_thresholds(config) is True
        assert bad_metrics.passes_thresholds(config) is False


class TestCoverageAnalyzer:
    """Test code coverage analysis."""
    
    @pytest.fixture
    def analyzer(self):
        """Create coverage analyzer."""
        return CoverageAnalyzer()
        
    @pytest.mark.asyncio
    async def test_analyze_coverage(self, analyzer, tmp_path):
        """Test analyzing test coverage."""
        # Create test files
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("""
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
""")
        
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_main.py").write_text("""
from src.main import add, multiply

def test_add():
    assert add(2, 3) == 5

def test_multiply():
    assert multiply(2, 3) == 6
""")
        
        # Mock coverage.py output
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = """
Name         Stmts   Miss  Cover   Branch  BrPart  Cover
---------------------------------------------------------
src/main.py     10      3    70%        4       1    75%
---------------------------------------------------------
TOTAL           10      3    70%        4       1    75%
"""
            
            result = await analyzer.analyze_coverage(tmp_path)
            
            assert result.line_coverage == 70.0
            assert result.branch_coverage == 75.0
            assert len(result.uncovered_lines) > 0
            
    @pytest.mark.asyncio
    async def test_find_untested_code(self, analyzer, tmp_path):
        """Test finding untested code."""
        # Create source file
        (tmp_path / "code.py").write_text("""
def tested_function():
    return "tested"

def untested_function():
    return "not tested"

def partially_tested(x):
    if x > 0:
        return "positive"
    else:
        return "negative"
""")
        
        # Mock coverage data
        with patch.object(analyzer, '_get_coverage_data') as mock_coverage:
            mock_coverage.return_value = {
                "files": {
                    str(tmp_path / "code.py"): {
                        "executed_lines": [1, 2, 7, 8, 9],
                        "missing_lines": [5, 6, 11, 12]
                    }
                }
            }
            
            untested = await analyzer.find_untested_code(tmp_path / "code.py")
            
            assert len(untested) > 0
            assert any("untested_function" in item["function"] for item in untested)


class TestMutationTester:
    """Test mutation testing functionality."""
    
    @pytest.fixture
    def tester(self):
        """Create mutation tester."""
        return MutationTester()
        
    @pytest.mark.asyncio
    async def test_run_mutation_tests(self, tester, tmp_path):
        """Test running mutation tests."""
        # Create source and test files
        (tmp_path / "math.py").write_text("""
def calculate(x, y, operation):
    if operation == "add":
        return x + y
    elif operation == "subtract":
        return x - y
    elif operation == "multiply":
        return x * y
    else:
        return 0
""")
        
        (tmp_path / "test_math.py").write_text("""
from math import calculate

def test_add():
    assert calculate(2, 3, "add") == 5

def test_subtract():
    assert calculate(5, 3, "subtract") == 2
""")
        
        # Mock mutmut output
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = """
Killed 15/20 mutants
Survived: 5
Mutation Score: 75.0%
"""
            
            result = await tester.run_mutation_tests(tmp_path)
            
            assert result.total_mutants == 20
            assert result.killed_mutants == 15
            assert result.survived_mutants == 5
            assert result.mutation_score == 75.0
            
    @pytest.mark.asyncio
    async def test_generate_mutants(self, tester, tmp_path):
        """Test generating mutants for code."""
        source_file = tmp_path / "source.py"
        source_file.write_text("""
def compare(a, b):
    if a > b:
        return "greater"
    elif a < b:
        return "less"
    else:
        return "equal"
""")
        
        mutants = await tester.generate_mutants(source_file)
        
        # Should generate mutants for comparison operators
        assert len(mutants) > 0
        assert any(m["type"] == "ComparisonOperator" for m in mutants)


class TestPropertyTester:
    """Test property-based testing."""
    
    @pytest.fixture
    def tester(self):
        """Create property tester."""
        return PropertyTester()
        
    @pytest.mark.asyncio
    async def test_check_properties(self, tester, tmp_path):
        """Test checking property tests."""
        test_file = tmp_path / "test_properties.py"
        test_file.write_text("""
# Note: Property-based testing with hypothesis would go here
# Commented out to avoid optional dependency issues

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    assert a + b == b + a

@given(st.lists(st.integers()))
def test_sort_idempotent(lst):
    sorted_once = sorted(lst)
    sorted_twice = sorted(sorted_once)
    assert sorted_once == sorted_twice
""")
        
        result = await tester.check_properties(test_file)
        
        assert result.total_properties == 2
        assert result.has_property_tests is True
        
    @pytest.mark.asyncio
    async def test_suggest_properties(self, tester, tmp_path):
        """Test suggesting property tests."""
        source_file = tmp_path / "functions.py"
        source_file.write_text("""
def reverse_list(lst):
    return lst[::-1]

def sort_unique(lst):
    return sorted(set(lst))
""")
        
        suggestions = await tester.suggest_properties(source_file)
        
        assert len(suggestions) > 0
        assert len(suggestions) > 0  # Should have at least one suggestion


class TestTestGate:
    """Test main test gate orchestrator."""
    
    @pytest.fixture
    def gate(self):
        """Create test gate instance."""
        config = TestConfig()
        return TestGate(config)
        
    @pytest.mark.asyncio
    async def test_analyze_test_suite(self, gate, tmp_path):
        """Test analyzing entire test suite."""
        # Create project structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "__init__.py").write_text("")
        (src_dir / "app.py").write_text("""
def hello():
    return "Hello, World!"
""")
        
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_app.py").write_text("""
from src.app import hello

def test_hello():
    assert hello() == "Hello, World!"
""")
        
        # Mock test execution with proper TestMetrics instance
        from packages.evaluation.test_gate import TestMetrics, MutationResult
        mock_metrics = TestMetrics(
            line_coverage=85.0,
            branch_coverage=80.0,
            uncovered_lines=[]
        )
        gate.coverage_analyzer = AsyncMock()
        gate.coverage_analyzer.analyze_coverage.return_value = mock_metrics
        
        mock_mutation = MutationResult(
            mutation_score=70.0,
            total_mutants=10,
            killed_mutants=7
        )
        gate.mutation_tester = AsyncMock()
        gate.mutation_tester.run_mutation_tests.return_value = mock_mutation
        
        result = await gate.analyze_test_suite(tmp_path)
        
        assert result.passed is True
        assert result.metrics.line_coverage == 85.0
        assert result.metrics.mutation_score == 70.0
        
    @pytest.mark.asyncio
    async def test_run_tests(self, gate, tmp_path):
        """Test running test suite."""
        # Mock pytest execution
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = """
=================== test session starts ===================
collected 10 items

tests/test_app.py::test_one PASSED
tests/test_app.py::test_two PASSED
tests/test_app.py::test_three FAILED

=================== 2 passed, 1 failed in 0.5s ===================
"""
            
            test_results = await gate.run_tests(tmp_path)
            
            assert test_results["total"] == 3
            assert test_results["passed"] == 2
            assert test_results["failed"] == 1
            
    @pytest.mark.asyncio
    async def test_generate_report(self, gate):
        """Test generating test report."""
        result = TestResult(
            passed=False,
            metrics=TestMetrics(
                line_coverage=75.0,
                branch_coverage=70.0,
                mutation_score=55.0,
                total_tests=100,
                passed_tests=95,
                failed_tests=5
            ),
            uncovered_files=["src/untested.py"],
            survived_mutants=[
                {"file": "src/main.py", "line": 10, "mutation": "Changed + to -"}
            ]
        )
        
        report = await gate.generate_report(result)
        
        assert "Test Gate Report" in report
        assert "FAILED" in report
        assert "75.0%" in report  # Line coverage
        assert "55.0" in report  # Mutation score
        
    @pytest.mark.asyncio
    async def test_create_github_comment(self, gate):
        """Test creating GitHub PR comment."""
        result = TestResult(
            passed=True,
            metrics=TestMetrics(
                line_coverage=90.0,
                branch_coverage=85.0,
                mutation_score=75.0,
                total_tests=50,
                passed_tests=50,
                failed_tests=0
            )
        )
        
        comment = await gate.create_github_comment(result)
        
        assert "## 🧪 Test Results" in comment
        assert "✅ **PASSED**" in comment
        assert "90.0%" in comment
        
    def test_should_fail_build(self, gate):
        """Test build failure decision logic."""
        # Should fail on low coverage
        result_low_coverage = TestResult(
            passed=False,
            metrics=TestMetrics(line_coverage=70.0)  # Below 80% threshold
        )
        assert gate.should_fail_build(result_low_coverage) is True
        
        # Should fail on low mutation score
        result_low_mutation = TestResult(
            passed=False,
            metrics=TestMetrics(
                line_coverage=85.0,
                mutation_score=50.0  # Below 60% threshold
            )
        )
        assert gate.should_fail_build(result_low_mutation) is True
        
        # Should pass with good metrics
        result_good = TestResult(
            passed=True,
            metrics=TestMetrics(
                line_coverage=85.0,
                mutation_score=65.0
            )
        )
        assert gate.should_fail_build(result_good) is False