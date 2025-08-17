"""Tests for Research Agent implementation."""

import json
from unittest.mock import AsyncMock, Mock

import pytest
from packages.agents.base import AgentInput, AgentOutput, AgentStatus
from packages.agents.research import (
    CodebaseAnalyzer,
    ImprovementFinder,
    PatternDetector,
    ResearchAgent,
    ResearchConfig,
)


class TestResearchConfig:
    """Test research agent configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ResearchConfig()

        assert config.max_files_to_scan == 100
        assert config.max_file_size_mb == 10
        assert config.ignore_patterns == [
            "__pycache__",
            ".git",
            "node_modules",
            ".venv",
            "dist",
            "build",
        ]
        assert config.focus_patterns == ["*.py", "*.js", "*.ts"]
        assert config.min_improvement_score == 0.3

    def test_custom_config(self):
        """Test custom configuration."""
        config = ResearchConfig(
            max_files_to_scan=50, min_improvement_score=0.5, enable_ai_analysis=True
        )

        assert config.max_files_to_scan == 50
        assert config.min_improvement_score == 0.5
        assert config.enable_ai_analysis is True


class TestCodebaseAnalyzer:
    """Test codebase analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return CodebaseAnalyzer()

    def test_scan_directory(self, analyzer, tmp_path):
        """Test directory scanning."""
        # Create test files
        (tmp_path / "main.py").write_text("def main(): pass")
        (tmp_path / "test.py").write_text("def test(): pass")
        (tmp_path / "README.md").write_text("# Test")
        (tmp_path / "__pycache__").mkdir()

        files = analyzer.scan_directory(tmp_path)

        assert len(files) == 3  # Excludes __pycache__
        assert any(f.name == "main.py" for f in files)
        assert any(f.name == "test.py" for f in files)

    def test_analyze_file_complexity(self, analyzer, tmp_path):
        """Test file complexity analysis."""
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

class TestClass:
    def method1(self):
        pass

    def method2(self):
        for i in range(10):
            if i % 2 == 0:
                print(i)
"""
        )

        metrics = analyzer.analyze_file(test_file)

        assert "complexity" in metrics
        assert "lines" in metrics
        assert "functions" in metrics
        assert "classes" in metrics
        assert metrics["complexity"] > 5  # High complexity

    def test_find_code_smells(self, analyzer, tmp_path):
        """Test code smell detection."""
        test_file = tmp_path / "smelly.py"
        test_file.write_text(
            """
def do_everything(data, flag1, flag2, flag3, flag4, flag5):
    # Too many parameters
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    # Too many variables

    if flag1:
        if flag2:
            if flag3:
                if flag4:
                    if flag5:
                        # Too deeply nested
                        return data

    # Duplicate code
    result = []
    for item in data:
        result.append(item * 2)

    result2 = []
    for item in data:
        result2.append(item * 2)

    return result
"""
        )

        smells = analyzer.find_code_smells(test_file)

        assert len(smells) > 0
        assert any("parameters" in s.lower() for s in smells)
        assert any("nested" in s.lower() for s in smells)


class TestPatternDetector:
    """Test pattern detection."""

    @pytest.fixture
    def detector(self):
        """Create pattern detector."""
        return PatternDetector()

    def test_detect_design_patterns(self, detector, tmp_path):
        """Test design pattern detection."""
        test_file = tmp_path / "patterns.py"
        test_file.write_text(
            """
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class Observer:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self):
        for observer in self._observers:
            observer.update()

class Factory:
    @staticmethod
    def create(type_name):
        if type_name == "A":
            return TypeA()
        elif type_name == "B":
            return TypeB()
"""
        )

        patterns = detector.detect_patterns(test_file)

        assert "singleton" in patterns
        assert "observer" in patterns
        assert "factory" in patterns

    def test_detect_anti_patterns(self, detector, tmp_path):
        """Test anti-pattern detection."""
        test_file = tmp_path / "antipatterns.py"
        test_file.write_text(
            """
class GodObject:
    def __init__(self):
        self.db = Database()
        self.cache = Cache()
        self.logger = Logger()
        self.validator = Validator()
        self.serializer = Serializer()

    def do_everything(self):
        # Too many responsibilities
        pass

    def process_data(self):
        pass

    def validate_input(self):
        pass

    def save_to_db(self):
        pass

def spaghetti_code():
    goto_label1()
    goto_label2()
    goto_label3()
    # Unstructured flow

global_var = []

def modify_global():
    global global_var
    global_var.append(1)  # Global state mutation
"""
        )

        antipatterns = detector.detect_antipatterns(test_file)

        assert len(antipatterns) > 0
        assert any("god" in p.lower() for p in antipatterns)
        assert any("global" in p.lower() for p in antipatterns)


class TestImprovementFinder:
    """Test improvement finder."""

    @pytest.fixture
    def finder(self):
        """Create improvement finder."""
        return ImprovementFinder()

    def test_find_refactoring_opportunities(self, finder, tmp_path):
        """Test refactoring opportunity detection."""
        test_file = tmp_path / "refactor.py"
        test_file.write_text(
            """
def calculate_price(quantity, price):
    # Missing type hints
    if quantity > 100:
        return quantity * price * 0.9
    elif quantity > 50:
        return quantity * price * 0.95
    else:
        return quantity * price

def process_data(data):
    # No docstring
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

class OldStyleClass:
    # Old-style class definition
    def __init__(self):
        self.value = 0
"""
        )

        opportunities = finder.find_refactoring_opportunities(test_file)

        assert len(opportunities) > 0
        assert any(o["type"] == "missing_type_hints" for o in opportunities)
        assert any(o["type"] == "missing_docstring" for o in opportunities)

    def test_score_improvements(self, finder):
        """Test improvement scoring."""
        improvements = [
            {"type": "performance", "impact": "high", "effort": "low"},
            {"type": "readability", "impact": "medium", "effort": "low"},
            {"type": "security", "impact": "critical", "effort": "low"},  # Changed to low effort
            {"type": "style", "impact": "low", "effort": "low"},
        ]

        scored = finder.score_improvements(improvements)

        # Security should rank highest (critical * low effort * security type = 1.0)
        assert scored[0]["type"] == "security"
        # Style should rank lowest
        assert scored[-1]["type"] == "style"


class TestResearchAgent:
    """Test research agent."""

    @pytest.fixture
    def agent(self):
        """Create research agent."""
        config = ResearchConfig(enable_ai_analysis=False)
        return ResearchAgent("research", config)

    @pytest.mark.asyncio
    async def test_execute_research(self, agent, tmp_path):
        """Test research execution."""
        # Create test codebase
        (tmp_path / "app.py").write_text(
            """
def main():
    # TODO: Add error handling
    data = load_data()
    process(data)

def load_data():
    return [1, 2, 3]

def process(data):
    for item in data:
        print(item)
"""
        )

        input_data = AgentInput(
            intent="research",
            task_id="test-001",
            payload={"target_path": str(tmp_path), "focus": ["improvement", "refactoring"]},
        )

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.OK
        assert len(output.artifacts) > 0
        assert any(a.kind == "report" for a in output.artifacts)
        assert "improvements_found" in output.metrics

    @pytest.mark.asyncio
    async def test_execute_with_ai_analysis(self, agent):
        """Test research with AI analysis."""
        agent.config.enable_ai_analysis = True

        # Mock the anthropic module import
        import sys

        mock_anthropic = Mock()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text=json.dumps(
                    {
                        "improvements": [
                            {
                                "type": "error_handling",
                                "description": "Add try-catch blocks",
                                "priority": "high",
                            }
                        ],
                        "patterns": ["singleton", "factory"],
                        "score": 0.75,
                    }
                )
            )
        ]

        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        # Temporarily add the mock to sys.modules
        sys.modules["anthropic"] = mock_anthropic

        try:
            input_data = AgentInput(
                intent="research", task_id="test-002", payload={"target_path": ".", "use_ai": True}
            )

            output = await agent.execute(input_data)

            assert output.status == AgentStatus.OK
            mock_client.messages.create.assert_called_once()
        finally:
            # Clean up the mock
            if "anthropic" in sys.modules:
                del sys.modules["anthropic"]

    @pytest.mark.asyncio
    async def test_validate_output(self, agent):
        """Test output validation."""
        valid_output = AgentOutput(
            task_id="test-003",
            status=AgentStatus.OK,
            artifacts=[
                {"kind": "report", "ref": "research-report.json", "content": {"improvements": []}}
            ],
            metrics={"files_analyzed": 10},
        )

        assert await agent.validate(valid_output) is True

        invalid_output = AgentOutput(
            task_id="test-004", status=AgentStatus.OK, artifacts=[], metrics={}  # No artifacts
        )

        assert await agent.validate(invalid_output) is False

    def test_get_capabilities(self, agent):
        """Test capabilities declaration."""
        capabilities = agent.get_capabilities()

        assert "name" in capabilities
        assert capabilities["name"] == "research"
        assert "version" in capabilities
        assert "supported_intents" in capabilities
        assert "research" in capabilities["supported_intents"]
        assert "pattern_detection" in capabilities["features"]
        assert "improvements" in capabilities["features"]
