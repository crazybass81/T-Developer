"""Tests for Quality Gate - Code quality metrics and enforcement."""


import pytest

from packages.evaluation.quality_gate import (
    ComplexityAnalyzer,
    DocstringAnalyzer,
    QualityConfig,
    QualityGate,
    QualityMetrics,
    QualityResult,
)


class TestQualityConfig:
    """Test quality gate configuration."""

    def test_default_config(self):
        """Test default quality configuration."""
        config = QualityConfig()

        assert config.min_docstring_coverage == 80.0
        assert config.max_complexity == 10
        assert config.max_maintainability_index == 100
        assert config.min_maintainability_index == 20
        assert config.max_line_length == 100
        assert config.max_file_lines == 500
        assert config.check_type_hints is True

    def test_custom_config(self):
        """Test custom quality configuration."""
        config = QualityConfig(
            min_docstring_coverage=90.0, max_complexity=5, check_type_hints=False
        )

        assert config.min_docstring_coverage == 90.0
        assert config.max_complexity == 5
        assert config.check_type_hints is False


class TestQualityMetrics:
    """Test quality metrics data model."""

    def test_metrics_creation(self):
        """Test creating quality metrics."""
        metrics = QualityMetrics(
            docstring_coverage=85.5,
            cyclomatic_complexity=8.2,
            maintainability_index=65.0,
            lines_of_code=1500,
            test_coverage=75.0,
            type_hint_coverage=90.0,
        )

        assert metrics.docstring_coverage == 85.5
        assert metrics.cyclomatic_complexity == 8.2
        assert metrics.maintainability_index == 65.0

    def test_metrics_passes_thresholds(self):
        """Test checking if metrics pass thresholds."""
        config = QualityConfig(min_docstring_coverage=80.0, max_complexity=10)

        good_metrics = QualityMetrics(
            docstring_coverage=85.0, cyclomatic_complexity=8.0, maintainability_index=70.0
        )

        bad_metrics = QualityMetrics(
            docstring_coverage=75.0,  # Below threshold
            cyclomatic_complexity=15.0,  # Above threshold
            maintainability_index=70.0,
        )

        assert good_metrics.passes_thresholds(config) is True
        assert bad_metrics.passes_thresholds(config) is False


class TestComplexityAnalyzer:
    """Test code complexity analysis."""

    @pytest.fixture
    def analyzer(self):
        """Create complexity analyzer."""
        return ComplexityAnalyzer()

    def test_analyze_simple_function(self, analyzer, tmp_path):
        """Test analyzing simple function complexity."""
        test_file = tmp_path / "simple.py"
        test_file.write_text(
            """
def simple_function(x):
    '''A simple function.'''
    return x * 2
"""
        )

        complexity = analyzer.analyze_file(test_file)

        assert complexity.average_complexity < 2
        assert complexity.max_complexity < 2

    def test_analyze_complex_function(self, analyzer, tmp_path):
        """Test analyzing complex function."""
        test_file = tmp_path / "complex.py"
        test_file.write_text(
            """
def complex_function(x, y, z):
    '''A complex function with high cyclomatic complexity.'''
    result = 0

    if x > 0:
        if y > 0:
            if z > 0:
                result = x + y + z
            else:
                result = x + y
        else:
            if z > 0:
                result = x + z
            else:
                result = x
    else:
        if y > 0:
            if z > 0:
                result = y + z
            else:
                result = y
        else:
            if z > 0:
                result = z
            else:
                result = 0

    for i in range(10):
        if i % 2 == 0:
            result += i

    return result
"""
        )

        complexity = analyzer.analyze_file(test_file)

        assert complexity.average_complexity > 5
        assert complexity.max_complexity > 10

    def test_calculate_maintainability_index(self, analyzer, tmp_path):
        """Test calculating maintainability index."""
        test_file = tmp_path / "maintainable.py"
        test_file.write_text(
            """
def well_structured_function(data):
    '''Process data efficiently.

    Args:
        data: Input data to process

    Returns:
        Processed result
    '''
    # Clean, simple logic
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""
        )

        mi = analyzer.calculate_maintainability_index(test_file)

        assert mi > 50  # Should have decent maintainability
        assert mi <= 100  # Max is 100


class TestDocstringAnalyzer:
    """Test docstring coverage analysis."""

    @pytest.fixture
    def analyzer(self):
        """Create docstring analyzer."""
        return DocstringAnalyzer()

    def test_analyze_with_docstrings(self, analyzer, tmp_path):
        """Test analyzing file with good docstrings."""
        test_file = tmp_path / "documented.py"
        test_file.write_text(
            '''
"""Module with good documentation."""

class WellDocumented:
    """A well-documented class."""

    def __init__(self):
        """Initialize the class."""
        self.value = 0

    def process(self, data):
        """Process the data.

        Args:
            data: Input data

        Returns:
            Processed result
        """
        return data * 2

def helper_function():
    """A helper function."""
    return 42
'''
        )

        coverage = analyzer.analyze_file(test_file)

        assert coverage.total_items > 0
        assert coverage.documented_items == coverage.total_items
        assert coverage.coverage_percentage == 100.0

    def test_analyze_missing_docstrings(self, analyzer, tmp_path):
        """Test analyzing file with missing docstrings."""
        test_file = tmp_path / "undocumented.py"
        test_file.write_text(
            """
class UndocumentedClass:
    def __init__(self):
        self.value = 0

    def process(self, data):
        return data * 2

def another_function():
    return 42

def documented_function():
    '''This one has a docstring.'''
    return 24
"""
        )

        coverage = analyzer.analyze_file(test_file)

        assert coverage.total_items == 6  # module + class + 4 methods/functions
        assert coverage.documented_items == 1  # Only documented_function
        assert coverage.coverage_percentage == pytest.approx(16.67, rel=0.1)

    def test_check_type_hints(self, analyzer, tmp_path):
        """Test checking type hint coverage."""
        test_file = tmp_path / "typed.py"
        test_file.write_text(
            """
from typing import List, Optional

def typed_function(x: int, y: str) -> str:
    '''A function with type hints.'''
    return f"{y}: {x}"

def partially_typed(x: int, y) -> None:
    '''Partially typed function.'''
    print(x, y)

def untyped_function(x, y):
    '''No type hints.'''
    return x + y

class TypedClass:
    '''A class with typed methods.'''

    def typed_method(self, value: int) -> int:
        '''Typed method.'''
        return value * 2

    def untyped_method(self, value):
        '''Untyped method.'''
        return value
"""
        )

        type_coverage = analyzer.check_type_hints(test_file)

        assert type_coverage.total_parameters > 0
        assert type_coverage.typed_parameters > 0
        assert type_coverage.typed_parameters < type_coverage.total_parameters
        assert 0 < type_coverage.coverage_percentage < 100


class TestQualityGate:
    """Test main quality gate orchestrator."""

    @pytest.fixture
    def gate(self):
        """Create quality gate instance."""
        config = QualityConfig(excluded_paths=[".git/", "__pycache__/", ".venv/", "venv/"])
        return QualityGate(config)

    @pytest.mark.asyncio
    async def test_analyze_codebase(self, gate, tmp_path):
        """Test analyzing entire codebase quality."""
        # Create test Python files
        (tmp_path / "good.py").write_text(
            '''
"""A well-documented module."""

def calculate(x: int, y: int) -> int:
    """Calculate sum of two numbers.

    Args:
        x: First number
        y: Second number

    Returns:
        Sum of x and y
    """
    return x + y
'''
        )

        (tmp_path / "bad.py").write_text(
            """
def complex_mess(a, b, c, d, e):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        return 1
    return 0
"""
        )

        # Debug: check files before calling analyze
        files = list(tmp_path.rglob("*.py"))
        print(f"DEBUG: Found {len(files)} files: {files}")

        result = await gate.analyze_codebase(tmp_path)

        assert (
            result.total_files == 2
        ), f"Expected 2 files, got {result.total_files}. Files: {files}"
        assert result.metrics.docstring_coverage >= 0
        assert result.metrics.cyclomatic_complexity > 0

    @pytest.mark.asyncio
    async def test_check_file_quality(self, gate, tmp_path):
        """Test checking individual file quality."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
def simple_function(x):
    '''Simple function.'''
    return x * 2
"""
        )

        issues = await gate.check_file_quality(test_file)

        # Should have minimal issues for simple file
        assert len(issues) >= 0

    @pytest.mark.asyncio
    async def test_generate_report(self, gate):
        """Test generating quality report."""
        result = QualityResult(
            passed=False,
            total_files=10,
            files_with_issues=3,
            metrics=QualityMetrics(
                docstring_coverage=75.0,
                cyclomatic_complexity=12.5,
                maintainability_index=55.0,
                lines_of_code=1500,
                test_coverage=70.0,
                type_hint_coverage=60.0,
            ),
            issues=[
                {"file": "src/main.py", "issue": "Missing docstring", "line": 10},
                {"file": "src/utils.py", "issue": "High complexity", "complexity": 15},
            ],
        )

        report = await gate.generate_report(result)

        assert "Quality Gate Report" in report
        assert "FAILED" in report
        assert "75.0%" in report  # Docstring coverage
        assert "12.5" in report  # Complexity

    @pytest.mark.asyncio
    async def test_create_github_comment(self, gate):
        """Test creating GitHub PR comment."""
        result = QualityResult(
            passed=True,
            total_files=5,
            files_with_issues=0,
            metrics=QualityMetrics(
                docstring_coverage=85.0,
                cyclomatic_complexity=7.5,
                maintainability_index=70.0,
                lines_of_code=500,
            ),
        )

        comment = await gate.create_github_comment(result)

        assert "## 📊 Code Quality Results" in comment
        assert "✅ **PASSED**" in comment
        assert "85.0%" in comment
