"""
Legacy Agent Analyzer
Day 16: Migration Framework - Legacy Agent Analysis
Generated: 2025-08-13

Analyzes legacy agent code to determine migration complexity and requirements
"""

import ast
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class MigrationComplexity(Enum):
    """Migration complexity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class AnalysisResult:
    """Result of legacy agent analysis"""

    agent_name: str
    complexity: MigrationComplexity
    dependencies: List[str] = field(default_factory=list)
    legacy_patterns: Set[str] = field(default_factory=set)
    modernization_opportunities: Set[str] = field(default_factory=set)
    performance_baseline: Dict[str, float] = field(default_factory=dict)
    migration_recommendations: List[str] = field(default_factory=list)
    has_errors: bool = False
    error_messages: List[str] = field(default_factory=list)


class LegacyAnalyzer:
    """Analyzes legacy agent code for migration planning"""

    def __init__(self):
        self.builtin_modules = {
            "os",
            "sys",
            "time",
            "datetime",
            "json",
            "logging",
            "traceback",
            "collections",
            "itertools",
            "functools",
            "re",
            "math",
            "random",
            "pathlib",
            "urllib",
            "http",
            "email",
            "xml",
            "html",
            "csv",
        }

    def analyze_code(self, code: str, agent_name: str) -> AnalysisResult:
        """Analyze agent code and return migration analysis"""
        result = AnalysisResult(agent_name=agent_name, complexity=MigrationComplexity.LOW)

        try:
            # Parse code to AST
            tree = ast.parse(code)

            # Extract dependencies
            result.dependencies = self._extract_dependencies(code)

            # Detect legacy patterns
            result.legacy_patterns = self._detect_legacy_patterns(code, tree)

            # Find modernization opportunities
            result.modernization_opportunities = self._find_modernization_opportunities(code, tree)

            # Calculate performance baseline
            result.performance_baseline = self._calculate_performance_baseline(code, tree)

            # Determine complexity
            result.complexity = self._calculate_complexity(result)

            # Generate recommendations
            result.migration_recommendations = self._generate_recommendations(result)

        except SyntaxError as e:
            result.has_errors = True
            result.error_messages.append(f"Syntax error: {str(e)}")
            result.complexity = MigrationComplexity.HIGH

        except Exception as e:
            result.has_errors = True
            result.error_messages.append(f"Analysis error: {str(e)}")
            result.complexity = MigrationComplexity.HIGH

        return result

    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analyze agent file and return migration analysis"""
        path = Path(file_path)
        agent_name = path.stem

        try:
            code = path.read_text(encoding="utf-8")
            return self.analyze_code(code, agent_name)
        except Exception as e:
            result = AnalysisResult(agent_name=agent_name, complexity=MigrationComplexity.HIGH)
            result.has_errors = True
            result.error_messages.append(f"File reading error: {str(e)}")
            return result

    def batch_analyze(self, file_paths: List[str]) -> List[AnalysisResult]:
        """Analyze multiple agent files"""
        results = []
        for file_path in file_paths:
            result = self.analyze_file(file_path)
            results.append(result)
        return results

    def _extract_dependencies(self, code: str) -> List[str]:
        """Extract dependencies from import statements"""
        dependencies = []

        # Find import statements
        import_patterns = [
            r"^import\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            r"^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import",
        ]

        lines = code.split("\n")
        for line in lines:
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    module_name = match.group(1)
                    # Filter out built-in modules
                    if module_name not in self.builtin_modules:
                        if module_name not in dependencies:
                            dependencies.append(module_name)

        return dependencies

    def _detect_legacy_patterns(self, code: str, tree: ast.AST) -> Set[str]:
        """Detect legacy patterns in the code"""
        patterns = set()

        # Detect synchronous HTTP calls
        if re.search(r"requests\.(get|post|put|delete)", code):
            patterns.add("synchronous_http")

        # Check for async patterns
        if "async def" not in code and "await" not in code:
            if any(dep in ["requests", "urllib"] for dep in self._extract_dependencies(code)):
                patterns.add("no_async_patterns")

        # Check for old string formatting
        if re.search(r"%[sd]", code) or re.search(r"\.format\(", code):
            patterns.add("old_string_formatting")

        # Check for missing type hints
        has_type_hints = "typing" in code or "->" in code or ":" in code
        if not has_type_hints:
            patterns.add("missing_type_hints")

        return patterns

    def _find_modernization_opportunities(self, code: str, tree: ast.AST) -> Set[str]:
        """Find opportunities for modernization"""
        opportunities = set()

        # Check for type hints opportunity
        if "typing" not in code and ("def " in code or "class " in code):
            opportunities.add("missing_type_hints")

        # Check for dict comprehension opportunities (for loops that build dicts)
        if re.search(r"for\s+\w+\s+in\s+\w+:\s*\n\s*\w+\[.*?\]\s*=", code, re.MULTILINE):
            opportunities.add("dict_comprehension_opportunity")

        # Check for list comprehension opportunities
        if re.search(r"for\s+\w+\s+in\s+\w+:\s*\n\s*\w+\.append\(", code):
            opportunities.add("list_comprehension_opportunity")

        # Check for f-string opportunities
        if ".format(" in code or "% " in code:
            opportunities.add("fstring_opportunity")

        return opportunities

    def _calculate_performance_baseline(self, code: str, tree: ast.AST) -> Dict[str, float]:
        """Calculate performance baseline metrics"""
        baseline = {}

        # Estimate memory usage based on code size
        code_lines = len(code.split("\n"))
        estimated_memory = code_lines * 0.1  # Rough estimate: 0.1KB per line
        baseline["estimated_memory_kb"] = round(estimated_memory, 2)

        # Estimate response time based on complexity
        complexity_score = len(self._extract_dependencies(code)) + code_lines / 10
        baseline["estimated_response_time_ms"] = round(complexity_score * 10, 2)

        return baseline

    def _calculate_complexity(self, result: AnalysisResult) -> MigrationComplexity:
        """Calculate migration complexity based on analysis results"""
        complexity_score = 0

        # Add points for legacy patterns
        complexity_score += len(result.legacy_patterns) * 2

        # Add points for dependencies (more dependencies = more complexity)
        complexity_score += len(result.dependencies)

        # Add points for concurrent/threading patterns
        concurrent_deps = ["threading", "asyncio", "multiprocessing"]
        if any(dep in result.dependencies for dep in concurrent_deps):
            complexity_score += 3

        # Add points for modernization opportunities
        complexity_score += len(result.modernization_opportunities)

        # Add points for errors
        if result.has_errors:
            complexity_score += 10

        # Determine complexity level
        if complexity_score <= 3:
            return MigrationComplexity.LOW
        elif complexity_score <= 8:
            return MigrationComplexity.MEDIUM
        else:
            return MigrationComplexity.HIGH

    def _generate_recommendations(self, result: AnalysisResult) -> List[str]:
        """Generate migration recommendations"""
        recommendations = []

        if "synchronous_http" in result.legacy_patterns:
            recommendations.append("Convert synchronous HTTP calls to async using aiohttp")

        if "no_async_patterns" in result.legacy_patterns:
            recommendations.append("Add async/await patterns for better performance")

        if "missing_type_hints" in result.modernization_opportunities:
            recommendations.append("Add type hints for better code quality")

        if "fstring_opportunity" in result.modernization_opportunities:
            recommendations.append("Convert to f-strings for better performance")

        if result.performance_baseline.get("estimated_memory_kb", 0) > 6.5:
            recommendations.append("Optimize code size to meet 6.5KB constraint")

        return recommendations
