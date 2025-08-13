"""
Compatibility Checker
Day 16: Migration Framework - Compatibility Validation
Generated: 2025-08-13

Checks compatibility with T-Developer framework and target constraints
"""

import ast
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class CompatibilityLevel(Enum):
    """Compatibility levels"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CompatibilityResult:
    """Result of compatibility checking"""

    agent_name: str
    compatibility_level: CompatibilityLevel = CompatibilityLevel.MEDIUM
    python_compatible: bool = True
    framework_compatible: bool = True
    memory_compliant: bool = True
    instantiation_compliant: bool = True
    estimated_memory_kb: float = 0.0
    estimated_instantiation_us: float = 0.0
    dependency_conflicts: List[str] = field(default_factory=list)
    compatibility_issues: List[str] = field(default_factory=list)
    async_issues: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)
    performance_issues: List[str] = field(default_factory=list)
    migration_suggestions: List[str] = field(default_factory=list)


class CompatibilityChecker:
    """Checks code compatibility with T-Developer framework"""

    def __init__(
        self,
        target_python_version: str = "3.9",
        target_framework_version: str = "1.0.0",
        memory_limit_kb: float = 6.5,
        instantiation_limit_us: float = 3.0,
    ):
        self.target_python_version = target_python_version
        self.target_framework_version = target_framework_version
        self.memory_limit_kb = memory_limit_kb
        self.instantiation_limit_us = instantiation_limit_us

        # Python version features
        self.version_features = {
            "3.10": ["match", "case", "union types with |"],
            "3.11": ["exception groups", "task groups"],
            "3.12": ["f-string improvements"],
        }

        # Deprecated patterns
        self.deprecated_patterns = {
            "imp": "Use importlib instead",
            "distutils": "Use setuptools instead",
            "optparse": "Use argparse instead",
        }

        # Security risks
        self.security_risks = [
            (r"subprocess\.run\([^)]*shell=True", "command injection risk"),
            (r"eval\(", "code injection risk"),
            (r"exec\(", "code execution risk"),
            (r"open\([^)]*\+.*filename", "path traversal risk"),
        ]

    def check_compatibility(self, code: str, agent_name: str) -> CompatibilityResult:
        """Check comprehensive compatibility"""
        result = CompatibilityResult(agent_name=agent_name)

        # Check Python version compatibility
        result.python_compatible = self._check_python_compatibility(code, result)

        # Check framework compatibility
        result.framework_compatible = self._check_framework_compatibility(code, result)

        # Check memory compliance
        result.estimated_memory_kb = self._estimate_memory_usage(code)
        result.memory_compliant = result.estimated_memory_kb <= self.memory_limit_kb

        # Check instantiation time
        result.estimated_instantiation_us = self._estimate_instantiation_time(code)
        result.instantiation_compliant = (
            result.estimated_instantiation_us <= self.instantiation_limit_us
        )

        # Check dependencies
        self._check_dependencies(code, result)

        # Check async patterns
        self._check_async_patterns(code, result)

        # Check security
        self._check_security_issues(code, result)

        # Check performance patterns
        self._check_performance_patterns(code, result)

        # Calculate overall compatibility level
        result.compatibility_level = self._calculate_compatibility_level(result)

        # Generate migration suggestions
        result.migration_suggestions = self._generate_migration_suggestions(result)

        return result

    def batch_check(self, code_samples: List[Tuple[str, str]]) -> List[CompatibilityResult]:
        """Check compatibility for multiple code samples"""
        results = []
        for filename, code in code_samples:
            agent_name = filename.replace(".py", "")
            result = self.check_compatibility(code, agent_name)
            results.append(result)
        return results

    def generate_report(self, result: CompatibilityResult) -> Dict:
        """Generate comprehensive compatibility report"""
        score = 100
        if not result.python_compatible:
            score -= 30
        if not result.framework_compatible:
            score -= 25
        if not result.memory_compliant:
            score -= 20
        if not result.instantiation_compliant:
            score -= 15

        score -= len(result.security_issues) * 5
        score -= len(result.performance_issues) * 3
        score = max(0, score)

        return {
            "summary": {
                "agent_name": result.agent_name,
                "compatibility_level": result.compatibility_level.value,
                "compatibility_score": score,
            },
            "issues": {
                "python_issues": result.compatibility_issues,
                "async_issues": result.async_issues,
                "security_issues": result.security_issues,
                "performance_issues": result.performance_issues,
            },
            "recommendations": result.migration_suggestions,
            "compatibility_score": score,
            "metrics": {
                "memory_usage_kb": result.estimated_memory_kb,
                "instantiation_time_us": result.estimated_instantiation_us,
                "memory_compliant": result.memory_compliant,
                "instantiation_compliant": result.instantiation_compliant,
            },
        }

    def _check_python_compatibility(self, code: str, result: CompatibilityResult) -> bool:
        """Check Python version compatibility"""
        compatible = True

        # Check for Python 3.10+ features
        if re.search(r"\bmatch\b.*:", code) or re.search(r"\bcase\b.*:", code):
            result.compatibility_issues.append("Uses match statement (Python 3.10+)")
            compatible = False

        # Check for other version-specific features
        for version, features in self.version_features.items():
            if version > self.target_python_version:
                for feature in features:
                    if feature.lower() in code.lower():
                        result.compatibility_issues.append(f"Uses {feature} (Python {version}+)")
                        compatible = False

        return compatible

    def _check_framework_compatibility(self, code: str, result: CompatibilityResult) -> bool:
        """Check T-Developer framework compatibility"""
        # Check for required patterns
        has_execute_method = "def execute(" in code or "async def execute(" in code
        has_capabilities_method = "def get_capabilities(" in code

        if has_execute_method and has_capabilities_method:
            return True

        if not has_execute_method:
            result.compatibility_issues.append("Missing execute() method")
        if not has_capabilities_method:
            result.compatibility_issues.append("Missing get_capabilities() method")

        return False

    def _check_dependencies(self, code: str, result: CompatibilityResult):
        """Check for dependency conflicts"""
        # Check for deprecated modules
        for deprecated, suggestion in self.deprecated_patterns.items():
            if f"import {deprecated}" in code or f"from {deprecated}" in code:
                result.dependency_conflicts.append(f"{deprecated} is deprecated: {suggestion}")
                result.compatibility_issues.append(f"Uses deprecated module: {deprecated}")

    def _check_async_patterns(self, code: str, result: CompatibilityResult):
        """Check async/await patterns"""
        has_async = "async def" in code
        has_blocking_calls = False

        # Check for blocking calls in async context
        if has_async:
            blocking_patterns = ["requests.", "time.sleep(", "subprocess.run("]
            for pattern in blocking_patterns:
                if pattern in code:
                    result.async_issues.append(f"Blocking call in async context: {pattern}")
                    has_blocking_calls = True

        # Check for sync patterns that should be async
        if not has_async and ("requests." in code):
            result.async_issues.append("Synchronous HTTP calls should be converted to async")

    def _check_security_issues(self, code: str, result: CompatibilityResult):
        """Check for security issues"""
        for pattern, issue in self.security_risks:
            if re.search(pattern, code):
                result.security_issues.append(issue)

    def _check_performance_patterns(self, code: str, result: CompatibilityResult):
        """Check for performance issues"""
        # Check for inefficient string concatenation
        if re.search(r"result\s*=\s*result\s*\+", code):
            result.performance_issues.append(
                "Inefficient string concatenation - use join() instead"
            )

        # Check for linear search in loops
        if re.search(r"for.*in.*:.*if.*==.*return", code, re.DOTALL):
            result.performance_issues.append("Linear search pattern - consider using sets or dicts")

        # Check for O(n) membership tests in loops
        if re.search(r"if.*in.*list", code):
            result.performance_issues.append("O(n) membership test - consider using sets")

    def _estimate_memory_usage(self, code: str) -> float:
        """Estimate memory usage in KB"""
        # Basic estimation
        lines = len(code.split("\n"))
        imports = code.count("import")
        classes = code.count("class")
        functions = code.count("def")

        # Rough estimation formula
        memory_kb = (lines * 0.1) + (imports * 0.2) + (classes * 0.5) + (functions * 0.1)
        return round(memory_kb, 2)

    def _estimate_instantiation_time(self, code: str) -> float:
        """Estimate instantiation time in microseconds"""
        complexity = 0
        complexity += code.count("import") * 0.3
        complexity += code.count("class") * 0.4
        complexity += code.count("__init__") * 0.2

        # Heavy operations
        if "heavy_computation" in code or "HeavyProcessor" in code:
            complexity += 2.0

        return min(1.0 + complexity, 5.0)  # Cap at 5μs

    def _calculate_compatibility_level(self, result: CompatibilityResult) -> CompatibilityLevel:
        """Calculate overall compatibility level"""
        issues_count = (
            len(result.compatibility_issues)
            + len(result.async_issues)
            + len(result.security_issues)
            + len(result.performance_issues)
        )

        compliance_score = 0
        if result.python_compatible:
            compliance_score += 1
        if result.framework_compatible:
            compliance_score += 1
        if result.memory_compliant:
            compliance_score += 1
        if result.instantiation_compliant:
            compliance_score += 1

        # Stricter thresholds for clearer differentiation
        if compliance_score >= 4 and issues_count <= 1:
            return CompatibilityLevel.HIGH
        elif compliance_score >= 2 and issues_count <= 3:
            return CompatibilityLevel.MEDIUM
        else:
            return CompatibilityLevel.LOW

    def _generate_migration_suggestions(self, result: CompatibilityResult) -> List[str]:
        """Generate migration suggestions"""
        suggestions = []

        if not result.python_compatible:
            suggestions.append("Update code to be compatible with Python 3.9")

        if not result.framework_compatible:
            suggestions.append("Add execute() and get_capabilities() methods")

        if not result.memory_compliant:
            suggestions.append(
                f"Reduce memory usage from {result.estimated_memory_kb}KB to under {self.memory_limit_kb}KB"
            )

        if not result.instantiation_compliant:
            suggestions.append("Optimize initialization to reduce instantiation time")

        if result.async_issues:
            suggestions.append("Convert synchronous HTTP calls to async using aiohttp")

        if result.security_issues:
            suggestions.append("Address security vulnerabilities before migration")

        if result.performance_issues:
            suggestions.append("Optimize performance patterns for better efficiency")

        return suggestions
