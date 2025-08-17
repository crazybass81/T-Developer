"""
Tests for Context Analyzer Agent.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.packages.agents.context_analyzer import (
    ContextAnalysis,
    ContextAnalyzerAgent,
)


@pytest.fixture
async def context_analyzer():
    """Create a context analyzer agent for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            "project_root": tmpdir,
            "memory_path": tmpdir + "/memory",
        }
        agent = ContextAnalyzerAgent(config)
        await agent.initialize()
        yield agent


@pytest.fixture
def sample_python_file():
    """Create a sample Python file for testing."""
    content = '''"""Sample module for testing."""

import os
import sys
from typing import List, Optional

class SampleClass:
    """A sample class."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(__name__)
    
    async def process(self, data: List[str]) -> Optional[str]:
        """Process data asynchronously."""
        try:
            result = await self._internal_process(data)
            return result
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return None
    
    async def _internal_process(self, data: List[str]) -> str:
        """Internal processing logic."""
        return " ".join(data)

def helper_function(value: int) -> int:
    """Helper function."""
    return value * 2

# TODO: Add more functionality
# TODO: Improve error handling
'''
    return content


class TestContextAnalyzerAgent:
    """Test Context Analyzer Agent functionality."""

    @pytest.mark.asyncio
    async def test_initialization(self, context_analyzer):
        """Test agent initialization."""
        assert context_analyzer.context_manager is not None
        assert context_analyzer.memory_system is not None
        assert context_analyzer.pattern_library is not None

    @pytest.mark.asyncio
    async def test_analyze_code_context(self, context_analyzer, sample_python_file):
        """Test analyzing code context."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(sample_python_file)
            file_path = f.name

        result = await context_analyzer.execute({
            "action": "analyze_code",
            "target": file_path,
            "depth": "normal",
        })

        assert result["success"]
        assert "analysis" in result
        assert "file_context" in result

        analysis = result["analysis"]
        assert analysis["context_type"] == "code"
        assert len(analysis["key_elements"]) > 0
        assert "class:SampleClass" in analysis["key_elements"]
        assert "async_function:process" in analysis["key_elements"]

        # Cleanup
        Path(file_path).unlink()

    @pytest.mark.asyncio
    async def test_analyze_task_context(self, context_analyzer):
        """Test analyzing task context."""
        task = {
            "task_id": "test_task",
            "type": "refactor",
            "description": "Refactor module for better performance",
            "files": ["module.py", "test_module.py"],
            "requirements": [
                "Improve API response time",
                "Add database caching",
                "Update service architecture",
            ],
        }

        result = await context_analyzer.execute({
            "action": "analyze_task",
            **task,
            "depth": "deep",
        })

        assert result["success"]
        assert "analysis" in result
        assert "task_context" in result
        assert "complexity" in result

        analysis = result["analysis"]
        assert analysis["context_type"] == "task"
        assert len(analysis["key_elements"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_evolution_context(self, context_analyzer):
        """Test analyzing evolution context."""
        result = await context_analyzer.execute({
            "action": "analyze_evolution",
            "evolution_id": "evo_test",
            "cycle": 10,
            "metrics_delta": {
                "coverage": 0.05,
                "complexity": -5,
                "performance": 0.1,
            },
        })

        assert result["success"]
        assert "analysis" in result
        assert "evolution_context" in result

        analysis = result["analysis"]
        assert analysis["context_type"] == "evolution"

    @pytest.mark.asyncio
    async def test_analyze_dependencies(self, context_analyzer, sample_python_file):
        """Test analyzing dependencies."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(sample_python_file)
            file_path = f.name

        result = await context_analyzer.execute({
            "action": "analyze_dependencies",
            "target": file_path,
            "depth": "normal",
        })

        assert result["success"]
        assert "dependencies" in result
        assert "direct" in result["dependencies"]
        
        # Check detected imports
        deps = result["dependencies"]["direct"]
        assert "os" in deps
        assert "sys" in deps
        assert "typing" in deps

        # Cleanup
        Path(file_path).unlink()

    @pytest.mark.asyncio
    async def test_find_patterns(self, context_analyzer, sample_python_file):
        """Test finding patterns in code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(sample_python_file)
            file_path = f.name

        result = await context_analyzer.execute({
            "action": "find_patterns",
            "target": file_path,
            "include_memory": False,
        })

        assert result["success"]
        assert "patterns" in result
        assert result["pattern_count"] >= 0

        # Check for expected patterns
        pattern_names = [p["name"] for p in result["patterns"]]
        # Decorator pattern should be detected if decorators exist
        # Type hints pattern should be detected
        assert any("type_hints" in name for name in pattern_names)

        # Cleanup
        Path(file_path).unlink()

    @pytest.mark.asyncio
    async def test_assess_risk(self, context_analyzer):
        """Test risk assessment."""
        # Test with risky code
        risky_code = '''
api_key = "secret_key_123"
password = "admin123"

def dangerous_function(user_input):
    eval(user_input)  # Security risk
    exec(user_input)  # Another security risk
'''
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(risky_code)
            file_path = f.name

        result = await context_analyzer.execute({
            "action": "assess_risk",
            "target": file_path,
        })

        assert result["success"]
        assert "risks" in result
        assert len(result["risks"]["high"]) > 0
        assert result["risk_score"] > 0.5

        # Check specific risks detected
        high_risks = result["risks"]["high"]
        assert any("Dynamic code execution" in r for r in high_risks)
        assert any("hardcoded secrets" in r for r in high_risks)

        # Cleanup
        Path(file_path).unlink()

    @pytest.mark.asyncio
    async def test_generate_recommendations(self, context_analyzer):
        """Test generating recommendations."""
        task = {
            "type": "refactor",
            "description": "Improve code quality and performance",
        }

        result = await context_analyzer.execute({
            "action": "generate_recommendations",
            **task,
            "include_memory": True,
        })

        assert result["success"]
        assert "recommendations" in result
        assert "immediate" in result["recommendations"]
        assert "short_term" in result["recommendations"]
        assert "long_term" in result["recommendations"]

    @pytest.mark.asyncio
    async def test_extract_key_elements(self, context_analyzer):
        """Test extracting key elements from code."""
        code = """
class TestClass:
    pass

async def async_function():
    pass

def regular_function():
    pass
"""
        elements = context_analyzer._extract_key_elements(code)
        
        assert "class:TestClass" in elements
        assert "async_function:async_function" in elements
        assert "function:regular_function" in elements

    @pytest.mark.asyncio
    async def test_extract_dependencies(self, context_analyzer):
        """Test extracting dependencies from code."""
        code = """
import os
import sys
from pathlib import Path
from typing import List, Dict
from backend.packages import agents
"""
        dependencies = context_analyzer._extract_dependencies(code)
        
        assert "os" in dependencies
        assert "sys" in dependencies
        assert "pathlib" in dependencies
        assert "typing" in dependencies
        assert "backend.packages" in dependencies

    @pytest.mark.asyncio
    async def test_detect_patterns(self, context_analyzer):
        """Test detecting code patterns."""
        code = """
@dataclass
class MyClass(BaseAgent):
    pass

async def process():
    try:
        logger.info("Processing")
        result = await do_something()
    except Exception as e:
        logger.error(f"Error: {e}")
"""
        patterns = context_analyzer._detect_patterns(code)
        
        assert "agent_inheritance" in patterns
        assert "dataclass_usage" in patterns
        assert "async_programming" in patterns
        assert "exception_handling" in patterns
        assert "logging_implemented" in patterns

    @pytest.mark.asyncio
    async def test_assess_code_risks(self, context_analyzer):
        """Test assessing code risks."""
        risky_code = """
# TODO: Fix this
# TODO: Implement that
# TODO: Review security
# TODO: Add tests
# TODO: Optimize performance
# TODO: Handle edge cases

def process(data):
    eval(data)
    with open(file_path) as f:
        content = f.read()
"""
        risks = context_analyzer._assess_code_risks(risky_code)
        
        assert any("Dynamic code execution" in r for r in risks)
        assert any("TODOs" in r for r in risks)
        assert any("File operations" in r for r in risks)

    @pytest.mark.asyncio
    async def test_generate_code_recommendations(self, context_analyzer):
        """Test generating code recommendations."""
        code = """
def process_data(data):
    result = []
    for item in data:
        processed = item * 2
        result.append(processed)
    return result
"""
        patterns = []
        risks = []
        
        recommendations = context_analyzer._generate_code_recommendations(
            code, patterns, risks
        )
        
        assert any("exception handling" in r for r in recommendations)
        assert any("logging" in r for r in recommendations)

    @pytest.mark.asyncio
    async def test_assess_task_complexity(self, context_analyzer):
        """Test assessing task complexity."""
        simple_task = {
            "type": "fix",
            "files": ["single_file.py"],
            "requirements": ["Fix bug"],
        }
        
        complex_task = {
            "type": "refactor",
            "files": ["file1.py", "file2.py", "file3.py", "file4.py", "file5.py"],
            "requirements": [
                "Redesign architecture",
                "Improve performance",
                "Add caching",
                "Update API",
                "Migrate database",
            ],
        }
        
        simple_complexity = context_analyzer._assess_task_complexity(simple_task)
        complex_complexity = context_analyzer._assess_task_complexity(complex_task)
        
        assert simple_complexity < 0.5
        assert complex_complexity > 0.7

    @pytest.mark.asyncio
    async def test_pattern_library(self, context_analyzer):
        """Test pattern library detection."""
        patterns = context_analyzer._load_pattern_library()
        
        assert "singleton" in patterns
        assert "factory" in patterns
        assert "decorator" in patterns
        assert "type_hints" in patterns

    @pytest.mark.asyncio
    async def test_caching_mechanism(self, context_analyzer):
        """Test analysis caching."""
        task = {
            "action": "analyze_task",
            "task_id": "cache_test",
            "type": "test",
            "description": "Test caching",
        }

        # First execution
        result1 = await context_analyzer.execute(task)
        
        # Store in cache manually
        context_analyzer.analysis_cache["cache_test"] = result1
        
        # Should use cache
        assert "cache_test" in context_analyzer.analysis_cache

    @pytest.mark.asyncio
    async def test_error_handling(self, context_analyzer):
        """Test error handling in analysis."""
        # Invalid action
        result = await context_analyzer.execute({
            "action": "invalid_action",
            "target": "test",
        })
        
        assert "error" in result
        assert "Unknown action" in result["error"]

    @pytest.mark.asyncio
    async def test_memory_integration(self, context_analyzer):
        """Test integration with memory system."""
        # Store something in memory
        await context_analyzer.memory_system.store_semantic(
            "test_concept",
            "test_content",
            0.7
        )
        
        # Analyze with memory
        result = await context_analyzer.execute({
            "action": "find_patterns",
            "target": "test",
            "include_memory": True,
        })
        
        assert result["success"]