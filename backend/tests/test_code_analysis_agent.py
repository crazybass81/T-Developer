"""Tests for CodeAnalysisAgent."""

import json

import pytest
from packages.agents.base import AgentInput, AgentStatus
from packages.agents.code_analysis import (
    CodeAnalysisAgent,
    CodeAnalysisConfig,
    CodebaseAnalyzer,
    ImprovementFinder,
    PatternDetector,
)


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return '''
class SampleClass:
    """A sample class for testing."""

    def __init__(self):
        self.value = 0

    def method_without_docstring(self, param1, param2):
        return param1 + param2

    def method_with_docstring(self, x: int) -> int:
        """This method has a docstring.

        Args:
            x: Input value

        Returns:
            Doubled value
        """
        return x * 2
'''


@pytest.fixture
def sample_complex_code():
    """Sample code with complexity issues."""
    return """
def complex_function(a, b, c, d, e, f, g):  # Too many parameters
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:  # Nested ifs - high complexity
                    return e + f + g
    return 0

class GodObject:  # God object anti-pattern
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
    def method13(self): pass
    def method14(self): pass
    def method15(self): pass
    def method16(self): pass
    def method17(self): pass
    def method18(self): pass
    def method19(self): pass
    def method20(self): pass
    def method21(self): pass  # More than 20 methods
"""


@pytest.fixture
def code_analysis_agent():
    """Create CodeAnalysisAgent instance."""
    config = CodeAnalysisConfig(max_files_to_scan=10, enable_deep_analysis=True)
    return CodeAnalysisAgent(config=config)


@pytest.fixture
def temp_python_file(tmp_path, sample_python_code):
    """Create temporary Python file."""
    file_path = tmp_path / "sample.py"
    file_path.write_text(sample_python_code)
    return file_path


@pytest.fixture
def temp_complex_file(tmp_path, sample_complex_code):
    """Create temporary complex Python file."""
    file_path = tmp_path / "complex.py"
    file_path.write_text(sample_complex_code)
    return file_path


class TestCodebaseAnalyzer:
    """Test CodebaseAnalyzer class."""

    def test_scan_directory(self, tmp_path):
        """Test directory scanning."""
        # Create test files
        (tmp_path / "test1.py").touch()
        (tmp_path / "test2.py").touch()
        (tmp_path / "test.txt").touch()
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "test3.py").touch()

        analyzer = CodebaseAnalyzer()
        config = CodeAnalysisConfig(focus_patterns=["*.py"])

        files = analyzer.scan_directory(tmp_path, config)

        assert len(files) == 3  # Only .py files
        assert all(f.suffix == ".py" for f in files)

    def test_analyze_file_metrics(self, temp_python_file):
        """Test file metrics analysis."""
        analyzer = CodebaseAnalyzer()
        metrics = analyzer.analyze_file(temp_python_file)

        assert metrics["path"] == str(temp_python_file)
        assert metrics["lines"] > 0
        assert metrics["functions"] == 3  # __init__ and 2 methods
        assert metrics["classes"] == 1
        assert metrics["complexity"] > 0
        assert 0 <= metrics["docstring_coverage"] <= 100
        assert 0 <= metrics["type_hints_coverage"] <= 100

    def test_find_code_smells(self, temp_complex_file):
        """Test code smell detection."""
        analyzer = CodebaseAnalyzer()
        smells = analyzer.find_code_smells(temp_complex_file)

        # Should detect large class
        large_class_smells = [s for s in smells if s["type"] == "large_class"]
        assert len(large_class_smells) > 0

        # Should detect too many parameters
        param_smells = [s for s in smells if s["type"] == "too_many_parameters"]
        assert len(param_smells) > 0


class TestPatternDetector:
    """Test PatternDetector class."""

    def test_detect_patterns(self, temp_python_file):
        """Test pattern detection."""
        detector = PatternDetector()
        patterns = detector.detect_patterns(temp_python_file)

        # For simple code, might not have patterns
        assert isinstance(patterns, list)

    def test_detect_antipatterns(self, temp_complex_file):
        """Test antipattern detection."""
        detector = PatternDetector()
        antipatterns = detector.detect_antipatterns(temp_complex_file)

        # Should detect god object
        god_objects = [a for a in antipatterns if a["type"] == "god_object"]
        assert len(god_objects) > 0
        assert god_objects[0]["class"] == "GodObject"


class TestImprovementFinder:
    """Test ImprovementFinder class."""

    def test_find_improvements(self, temp_python_file):
        """Test improvement finding."""
        finder = ImprovementFinder()
        analyzer = CodebaseAnalyzer()

        metrics = analyzer.analyze_file(temp_python_file)
        improvements = finder.find_improvements(temp_python_file, metrics)

        # Should find missing docstring
        missing_docs = [i for i in improvements if i["type"] == "missing_docstring"]
        assert len(missing_docs) > 0

        # Should find missing return type
        missing_types = [i for i in improvements if i["type"] == "missing_return_type"]
        assert len(missing_types) > 0

    def test_score_improvements(self):
        """Test improvement scoring."""
        finder = ImprovementFinder()

        improvements = [
            {"type": "a", "priority": "high", "effort": "low"},
            {"type": "b", "priority": "low", "effort": "high"},
            {"type": "c", "priority": "medium", "effort": "medium"},
        ]

        scored = finder.score_improvements(improvements)

        # High priority + low effort should score highest
        assert scored[0]["type"] == "a"
        assert all("score" in imp for imp in scored)


class TestCodeAnalysisAgent:
    """Test CodeAnalysisAgent."""

    @pytest.mark.asyncio
    async def test_execute_with_file(self, code_analysis_agent, temp_python_file):
        """Test agent execution with single file."""
        input_data = AgentInput(
            intent="analyze", task_id="test-123", payload={"target_path": str(temp_python_file)}
        )

        output = await code_analysis_agent.execute(input_data)

        assert output.status == AgentStatus.OK
        assert output.metrics["files_analyzed"] == 1
        assert output.metrics["total_lines"] > 0
        assert "avg_complexity" in output.metrics
        assert "avg_docstring_coverage" in output.metrics
        assert len(output.artifacts) > 0

    @pytest.mark.asyncio
    async def test_execute_with_directory(self, code_analysis_agent, tmp_path):
        """Test agent execution with directory."""
        # Create multiple files
        (tmp_path / "file1.py").write_text("def func1(): pass")
        (tmp_path / "file2.py").write_text("def func2(): pass")

        input_data = AgentInput(
            intent="analyze", task_id="test-456", payload={"target_path": str(tmp_path)}
        )

        output = await code_analysis_agent.execute(input_data)

        assert output.status == AgentStatus.OK
        assert output.metrics["files_analyzed"] == 2

    @pytest.mark.asyncio
    async def test_execute_with_invalid_path(self, code_analysis_agent):
        """Test agent execution with invalid path."""
        input_data = AgentInput(
            intent="analyze", task_id="test-789", payload={"target_path": "/nonexistent/path"}
        )

        # Should not validate
        assert not code_analysis_agent.validate(input_data)

    def test_get_capabilities(self, code_analysis_agent):
        """Test agent capabilities."""
        capabilities = code_analysis_agent.get_capabilities()

        assert capabilities["type"] == "code_analysis"
        assert "python" in capabilities["supported_languages"]
        assert "metrics" in capabilities["analysis_types"]
        assert capabilities["features"]["complexity_analysis"] is True


class TestIntegration:
    """Integration tests."""

    @pytest.mark.asyncio
    async def test_full_analysis_flow(self, tmp_path, sample_complex_code):
        """Test complete analysis flow."""
        # Setup
        file_path = tmp_path / "project" / "module.py"
        file_path.parent.mkdir(parents=True)
        file_path.write_text(sample_complex_code)

        # Create agent
        config = CodeAnalysisConfig(max_files_to_scan=10, min_improvement_score=0.1)
        agent = CodeAnalysisAgent(config=config)

        # Execute analysis
        input_data = AgentInput(
            intent="analyze",
            task_id="integration-test",
            payload={"target_path": str(tmp_path / "project")},
        )

        output = await agent.execute(input_data)

        # Verify results
        assert output.status == AgentStatus.OK
        assert output.metrics["files_analyzed"] > 0
        assert output.metrics["antipatterns_detected"] > 0  # Should detect god object
        assert output.metrics["improvements_found"] > 0

        # Check artifacts
        metrics_artifact = next(
            (a for a in output.artifacts if a.kind == "report" and a.ref == "metrics.json"), None
        )
        assert metrics_artifact is not None

        # Verify metrics content
        metrics_data = json.loads(metrics_artifact.content)
        assert len(metrics_data) > 0
        assert metrics_data[0]["path"] == str(file_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
