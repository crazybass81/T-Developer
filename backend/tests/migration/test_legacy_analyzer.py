"""
Test suite for Legacy Analyzer
Day 16: Migration Framework - TDD Implementation
Generated: 2025-08-13

Testing requirements:
1. Legacy agent code analysis and pattern detection
2. Dependency extraction and compatibility checks
3. Performance baseline assessment
4. Migration complexity scoring
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.migration.legacy_analyzer import AnalysisResult, LegacyAnalyzer, MigrationComplexity


class TestLegacyAnalyzer:
    """Test suite for legacy agent analyzer"""

    @pytest.fixture
    def analyzer(self):
        return LegacyAnalyzer()

    @pytest.fixture
    def sample_legacy_code(self):
        return """
import requests
import json
from typing import Dict, List

class LegacyAgent:
    def __init__(self):
        self.dependencies = ["requests", "json"]

    def process(self, input_data: Dict) -> Dict:
        # Legacy synchronous processing
        result = requests.get("http://api.example.com/data")
        return {"data": json.loads(result.text)}

    def validate_input(self, data):
        # No type hints, old style
        if not data:
            return False
        return True
"""

    def test_analyze_code_basic_functionality(self, analyzer, sample_legacy_code):
        """Test basic code analysis functionality"""
        result = analyzer.analyze_code(sample_legacy_code, "test_agent")

        assert isinstance(result, AnalysisResult)
        assert result.agent_name == "test_agent"
        assert result.complexity in [
            MigrationComplexity.LOW,
            MigrationComplexity.MEDIUM,
            MigrationComplexity.HIGH,
        ]
        assert len(result.dependencies) > 0
        assert "requests" in result.dependencies

    def test_detect_legacy_patterns(self, analyzer, sample_legacy_code):
        """Test legacy pattern detection"""
        result = analyzer.analyze_code(sample_legacy_code, "test_agent")

        # Should detect synchronous HTTP calls
        assert "synchronous_http" in result.legacy_patterns
        # Should detect missing async/await patterns
        assert "no_async_patterns" in result.legacy_patterns

    def test_dependency_extraction(self, analyzer):
        """Test dependency extraction from code"""
        code_with_imports = """
import os
import sys
import requests
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
"""

        dependencies = analyzer._extract_dependencies(code_with_imports)

        assert "requests" in dependencies
        assert "numpy" in dependencies
        assert "typing" in dependencies
        # Built-ins should be filtered out
        assert "os" not in dependencies
        assert "sys" not in dependencies

    def test_complexity_scoring_simple_agent(self, analyzer):
        """Test complexity scoring for simple agents"""
        simple_code = """
def simple_function():
    return "hello"
"""

        result = analyzer.analyze_code(simple_code, "simple_agent")
        assert result.complexity == MigrationComplexity.LOW

    def test_complexity_scoring_complex_agent(self, analyzer):
        """Test complexity scoring for complex agents"""
        complex_code = """
import threading
import asyncio
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

class ComplexAgent:
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.processes = []

    def complex_processing(self):
        with self.thread_pool as executor:
            futures = []
            for i in range(100):
                future = executor.submit(self.worker_function, i)
                futures.append(future)

        # Complex async patterns
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    def worker_function(self, data):
        return data * 2
"""

        result = analyzer.analyze_code(complex_code, "complex_agent")
        assert result.complexity in [MigrationComplexity.MEDIUM, MigrationComplexity.HIGH]

    def test_performance_baseline_assessment(self, analyzer, sample_legacy_code):
        """Test performance baseline assessment"""
        result = analyzer.analyze_code(sample_legacy_code, "test_agent")

        assert result.performance_baseline is not None
        assert "estimated_memory_kb" in result.performance_baseline
        assert "estimated_response_time_ms" in result.performance_baseline
        assert result.performance_baseline["estimated_memory_kb"] > 0

    def test_migration_recommendations(self, analyzer, sample_legacy_code):
        """Test generation of migration recommendations"""
        result = analyzer.analyze_code(sample_legacy_code, "test_agent")

        assert len(result.migration_recommendations) > 0
        # Should recommend async conversion
        recommendations_text = str(result.migration_recommendations)
        assert "async" in recommendations_text.lower()

    def test_analyze_file_path(self, analyzer, tmp_path):
        """Test analyzing code from file path"""
        test_file = tmp_path / "test_agent.py"
        test_file.write_text(
            """
def test_function():
    return "test"
"""
        )

        result = analyzer.analyze_file(str(test_file))
        assert result.agent_name == "test_agent"
        assert result.complexity == MigrationComplexity.LOW

    def test_batch_analysis(self, analyzer, tmp_path):
        """Test batch analysis of multiple files"""
        # Create test files
        agent1 = tmp_path / "agent1.py"
        agent2 = tmp_path / "agent2.py"

        agent1.write_text("def simple1(): return 1")
        agent2.write_text("def simple2(): return 2")

        results = analyzer.batch_analyze([str(agent1), str(agent2)])

        assert len(results) == 2
        assert results[0].agent_name == "agent1"
        assert results[1].agent_name == "agent2"

    def test_error_handling_invalid_code(self, analyzer):
        """Test error handling for invalid Python code"""
        invalid_code = """
def invalid_function(
    # Missing closing parenthesis and colon
    print("invalid")
"""

        result = analyzer.analyze_code(invalid_code, "invalid_agent")
        assert result.has_errors
        assert len(result.error_messages) > 0

    def test_modernization_opportunities(self, analyzer):
        """Test detection of modernization opportunities"""
        old_style_code = """
def old_style_function(data):
    # No type hints
    result = {}
    for item in data:
        result[item["key"]] = item["value"]
    return result

class OldStyleClass:
    def __init__(self):
        pass

    def method_without_types(self, param1, param2):
        return param1 + param2
"""

        result = analyzer.analyze_code(old_style_code, "old_style_agent")

        assert "missing_type_hints" in result.modernization_opportunities
        assert "dict_comprehension_opportunity" in result.modernization_opportunities
