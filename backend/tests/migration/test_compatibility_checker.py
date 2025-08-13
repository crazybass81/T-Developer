"""
Test suite for Compatibility Checker
Day 16: Migration Framework - TDD Implementation
Generated: 2025-08-13

Testing requirements:
1. Python version compatibility checking
2. Dependency version conflicts detection
3. T-Developer framework compatibility
4. Performance constraint validation
"""

from unittest.mock import MagicMock, patch

import pytest

from src.migration.compatibility_checker import (
    CompatibilityChecker,
    CompatibilityLevel,
    CompatibilityResult,
)


class TestCompatibilityChecker:
    """Test suite for compatibility checker"""

    @pytest.fixture
    def checker(self):
        return CompatibilityChecker(
            target_python_version="3.9",
            target_framework_version="1.0.0",
            memory_limit_kb=6.5,
            instantiation_limit_us=3.0,
        )

    def test_check_python_version_compatibility(self, checker):
        """Test Python version compatibility checking"""
        # Compatible code
        compatible_code = """
def simple_function():
    return "hello"
"""

        result = checker.check_compatibility(compatible_code, "test_agent")

        assert isinstance(result, CompatibilityResult)
        assert result.python_compatible
        assert result.compatibility_level in [
            CompatibilityLevel.HIGH,
            CompatibilityLevel.MEDIUM,
            CompatibilityLevel.LOW,
        ]

    def test_detect_incompatible_python_features(self, checker):
        """Test detection of incompatible Python features"""
        # Code using Python 3.10+ features
        incompatible_code = """
def process_data(data):
    match data:  # Pattern matching (Python 3.10+)
        case {"type": "user", "name": str(name)}:
            return f"User: {name}"
        case {"type": "admin"}:
            return "Administrator"
        case _:
            return "Unknown"
"""

        result = checker.check_compatibility(incompatible_code, "test_agent")

        assert not result.python_compatible
        assert "match statement" in str(result.compatibility_issues).lower()

    def test_dependency_compatibility_check(self, checker):
        """Test dependency version compatibility"""
        code_with_deps = """
import requests  # Should check version compatibility
import numpy
import pandas
from typing import Dict, List

def process_with_deps():
    pass
"""

        result = checker.check_compatibility(code_with_deps, "test_agent")

        assert hasattr(result, "dependency_conflicts")
        assert isinstance(result.dependency_conflicts, list)

    def test_memory_constraint_validation(self, checker):
        """Test memory constraint validation"""
        # Code that might exceed memory limits
        memory_heavy_code = """
LARGE_DATA = {
    f"key_{i}": f"very_long_value_string_that_consumes_memory_{i}" * 100
    for i in range(1000)
}

class MemoryHeavyAgent:
    def __init__(self):
        self.cache = {}
        self.large_buffer = [0] * 10000
        self.data_store = LARGE_DATA.copy()
"""

        result = checker.check_compatibility(memory_heavy_code, "heavy_agent")

        assert hasattr(result, "memory_compliant")
        assert hasattr(result, "estimated_memory_kb")

    def test_instantiation_time_validation(self, checker):
        """Test instantiation time constraint validation"""
        # Code with slow instantiation
        slow_instantiation_code = """
import time
import heavy_computation_library

class SlowAgent:
    def __init__(self):
        # Simulate slow initialization
        self.processor = heavy_computation_library.HeavyProcessor()
        self.cache = self._build_large_cache()

    def _build_large_cache(self):
        return {i: i**2 for i in range(10000)}
"""

        result = checker.check_compatibility(slow_instantiation_code, "slow_agent")

        assert hasattr(result, "instantiation_compliant")
        assert hasattr(result, "estimated_instantiation_us")

    def test_framework_compatibility(self, checker):
        """Test T-Developer framework compatibility"""
        # Code compatible with T-Developer framework
        framework_compatible_code = """
from typing import Dict, Any
import asyncio

class CompatibleAgent:
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "data": "processed"}

    def get_capabilities(self) -> Dict[str, Any]:
        return {"type": "processor", "version": "1.0"}
"""

        result = checker.check_compatibility(framework_compatible_code, "compatible_agent")

        assert result.framework_compatible
        assert result.compatibility_level == CompatibilityLevel.HIGH

    def test_detect_deprecated_patterns(self, checker):
        """Test detection of deprecated patterns"""
        deprecated_code = """
import imp  # Deprecated module
from distutils.util import strtobool  # Deprecated

def old_style_import():
    module = imp.load_source('module', 'path/to/module.py')
    return module

def use_deprecated_function():
    return strtobool("true")
"""

        result = checker.check_compatibility(deprecated_code, "deprecated_agent")

        assert len(result.compatibility_issues) > 0
        assert any("deprecated" in issue.lower() for issue in result.compatibility_issues)

    def test_async_compatibility_check(self, checker):
        """Test async/await pattern compatibility"""
        # Mix of sync and async patterns
        mixed_async_code = """
import asyncio
import requests

async def async_function():
    return "async result"

def sync_function():
    # This will block in async context
    response = requests.get("http://example.com")
    return response.json()

class MixedAgent:
    async def execute(self, data):
        sync_result = sync_function()  # Problematic
        async_result = await async_function()  # Good
        return {"sync": sync_result, "async": async_result}
"""

        result = checker.check_compatibility(mixed_async_code, "mixed_agent")

        assert len(result.async_issues) > 0
        assert "blocking call in async" in str(result.async_issues).lower()

    def test_security_compatibility(self, checker):
        """Test security pattern compatibility"""
        insecure_code = """
import os
import subprocess

def risky_function(user_input):
    # Security risk - command injection
    command = f"ls {user_input}"
    result = subprocess.run(command, shell=True, capture_output=True)
    return result.stdout

def another_risk(filename):
    # Security risk - path traversal
    with open(f"/data/{filename}", 'r') as file:
        return file.read()
"""

        result = checker.check_compatibility(insecure_code, "risky_agent")

        assert len(result.security_issues) > 0
        assert any(
            "injection" in issue.lower() or "traversal" in issue.lower()
            for issue in result.security_issues
        )

    def test_performance_pattern_compatibility(self, checker):
        """Test performance pattern compatibility"""
        performance_issues_code = """
def inefficient_function(data):
    # Inefficient string concatenation
    result = ""
    for item in data:
        result = result + str(item)  # Should use join()
    return result

def inefficient_search(items, target):
    # Inefficient linear search
    for item in items:
        if item == target:
            return True
    return False

class InefficiientAgent:
    def __init__(self):
        self.data = []

    def add_item(self, item):
        # Inefficient list operations
        if item not in self.data:  # O(n) check
            self.data.append(item)
"""

        result = checker.check_compatibility(performance_issues_code, "inefficient_agent")

        assert len(result.performance_issues) > 0
        assert any(
            "concatenation" in issue.lower() or "inefficient" in issue.lower()
            for issue in result.performance_issues
        )

    def test_generate_compatibility_report(self, checker):
        """Test comprehensive compatibility report generation"""
        test_code = """
import requests
from typing import Dict

def simple_function(data: Dict) -> str:
    response = requests.get("http://api.example.com")
    return response.text
"""

        result = checker.check_compatibility(test_code, "test_agent")
        report = checker.generate_report(result)

        assert isinstance(report, dict)
        assert "summary" in report
        assert "issues" in report
        assert "recommendations" in report
        assert "compatibility_score" in report

    def test_batch_compatibility_check(self, checker):
        """Test batch compatibility checking"""
        code_samples = [
            ("agent1.py", "def simple(): return 1"),
            ("agent2.py", "async def async_simple(): return 2"),
            ("agent3.py", "import deprecated_module"),
        ]

        results = checker.batch_check(code_samples)

        assert len(results) == 3
        assert all(isinstance(result, CompatibilityResult) for result in results)

    def test_compatibility_level_calculation(self, checker):
        """Test compatibility level calculation logic"""
        # High compatibility code
        high_compat_code = """
from typing import Dict, Any
import asyncio

async def modern_function(data: Dict[str, Any]) -> Dict[str, Any]:
    return {"processed": data}
"""

        result = checker.check_compatibility(high_compat_code, "modern_agent")
        assert result.compatibility_level == CompatibilityLevel.HIGH

        # Low compatibility code
        low_compat_code = """
import imp
import deprecated_module

def old_function():
    match data:  # Python 3.10+ feature
        case {"type": "test"}:
            return "test"
"""

        result = checker.check_compatibility(low_compat_code, "old_agent")
        assert result.compatibility_level == CompatibilityLevel.LOW

    def test_migration_suggestions(self, checker):
        """Test generation of migration suggestions"""
        problematic_code = """
import requests

def sync_function():
    response = requests.get("http://example.com")
    return response.json()
"""

        result = checker.check_compatibility(problematic_code, "sync_agent")

        assert len(result.migration_suggestions) > 0
        suggestions_text = " ".join(result.migration_suggestions)
        assert "async" in suggestions_text.lower() or "aiohttp" in suggestions_text.lower()
