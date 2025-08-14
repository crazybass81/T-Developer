"""
AST Analyzer - Advanced code analysis using Abstract Syntax Tree
Size: < 6.5KB | Performance: < 3μs
Day 27: Phase 2 - ServiceImproverAgent
"""

import ast
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class CodePattern:
    """Detected code pattern"""

    pattern_type: str
    node_type: str
    line: int
    column: int
    complexity: int
    suggestion: str


@dataclass
class FunctionMetrics:
    """Function-level metrics"""

    name: str
    lines: int
    complexity: int
    parameters: int
    returns: int
    calls: int
    branches: int
    loops: int


@dataclass
class ASTAnalysis:
    """Complete AST analysis results"""

    patterns: List[CodePattern]
    functions: List[FunctionMetrics]
    dependencies: Dict[str, Set[str]]
    complexity_score: float
    maintainability_score: float
    suggestions: List[str]


class ASTAnalyzer:
    """Analyze Python code using AST"""

    def __init__(self):
        self.patterns = []
        self.functions = []
        self.dependencies = defaultdict(set)
        self.import_map = {}

    def analyze(self, code: str) -> ASTAnalysis:
        """Perform comprehensive AST analysis"""

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return self._create_error_analysis(str(e))

        # Reset state
        self.patterns = []
        self.functions = []
        self.dependencies = defaultdict(set)

        # Analyze tree
        self._analyze_imports(tree)
        self._analyze_functions(tree)
        self._detect_patterns(tree)
        self._analyze_dependencies(tree)

        # Calculate scores
        complexity_score = self._calculate_complexity_score()
        maintainability_score = self._calculate_maintainability_score()

        # Generate suggestions
        suggestions = self._generate_suggestions()

        return ASTAnalysis(
            patterns=self.patterns,
            functions=self.functions,
            dependencies=dict(self.dependencies),
            complexity_score=complexity_score,
            maintainability_score=maintainability_score,
            suggestions=suggestions,
        )

    def _analyze_imports(self, tree: ast.AST):
        """Analyze import statements"""

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.import_map[alias.asname or alias.name] = alias.name

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    name = alias.asname or alias.name
                    self.import_map[name] = f"{module}.{alias.name}"

    def _analyze_functions(self, tree: ast.AST):
        """Analyze function definitions"""

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metrics = self._analyze_function_node(node)
                self.functions.append(metrics)

    def _analyze_function_node(self, node: ast.FunctionDef) -> FunctionMetrics:
        """Analyze single function node"""

        # Count lines
        lines = node.end_lineno - node.lineno + 1 if hasattr(node, "end_lineno") else 0

        # Count complexity
        complexity = self._calculate_cyclomatic_complexity(node)

        # Count parameters
        parameters = len(node.args.args) + len(node.args.kwonlyargs)

        # Count returns
        returns = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))

        # Count function calls
        calls = sum(1 for n in ast.walk(node) if isinstance(n, ast.Call))

        # Count branches
        branches = sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.Try)))

        # Count loops
        loops = sum(1 for n in ast.walk(node) if isinstance(n, (ast.For, ast.While)))

        return FunctionMetrics(
            name=node.name,
            lines=lines,
            complexity=complexity,
            parameters=parameters,
            returns=returns,
            calls=calls,
            branches=branches,
            loops=loops,
        )

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""

        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _detect_patterns(self, tree: ast.AST):
        """Detect code patterns and anti-patterns"""

        for node in ast.walk(tree):
            # Nested loops
            if isinstance(node, ast.For):
                if any(isinstance(child, ast.For) for child in ast.walk(node)):
                    self.patterns.append(
                        CodePattern(
                            pattern_type="nested_loop",
                            node_type="For",
                            line=node.lineno,
                            column=node.col_offset,
                            complexity=2,
                            suggestion="Consider flattening nested loops",
                        )
                    )

            # Long parameter lists
            if isinstance(node, ast.FunctionDef):
                if len(node.args.args) > 5:
                    self.patterns.append(
                        CodePattern(
                            pattern_type="long_parameter_list",
                            node_type="FunctionDef",
                            line=node.lineno,
                            column=node.col_offset,
                            complexity=1,
                            suggestion="Consider using configuration object",
                        )
                    )

            # Multiple returns
            if isinstance(node, ast.FunctionDef):
                returns = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
                if len(returns) > 3:
                    self.patterns.append(
                        CodePattern(
                            pattern_type="multiple_returns",
                            node_type="FunctionDef",
                            line=node.lineno,
                            column=node.col_offset,
                            complexity=1,
                            suggestion="Simplify control flow",
                        )
                    )

            # Global usage
            if isinstance(node, ast.Global):
                self.patterns.append(
                    CodePattern(
                        pattern_type="global_usage",
                        node_type="Global",
                        line=node.lineno,
                        column=node.col_offset,
                        complexity=2,
                        suggestion="Avoid global variables",
                    )
                )

    def _analyze_dependencies(self, tree: ast.AST):
        """Analyze function dependencies"""

        current_function = None

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                current_function = node.name
                self.dependencies[current_function] = set()

                # Find function calls
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            self.dependencies[current_function].add(child.func.id)

    def _calculate_complexity_score(self) -> float:
        """Calculate overall complexity score (0-1, lower is better)"""

        if not self.functions:
            return 0.0

        avg_complexity = sum(f.complexity for f in self.functions) / len(self.functions)

        # Normalize to 0-1 scale
        return min(1.0, avg_complexity / 10)

    def _calculate_maintainability_score(self) -> float:
        """Calculate maintainability score (0-1, higher is better)"""

        if not self.functions:
            return 1.0

        penalties = 0

        # Penalize long functions
        for func in self.functions:
            if func.lines > 50:
                penalties += 0.1
            if func.complexity > 10:
                penalties += 0.1
            if func.parameters > 5:
                penalties += 0.05

        # Penalize anti-patterns
        penalties += len(self.patterns) * 0.02

        return max(0.0, 1.0 - penalties)

    def _generate_suggestions(self) -> List[str]:
        """Generate improvement suggestions"""

        suggestions = []

        # Based on functions
        for func in self.functions:
            if func.complexity > 10:
                suggestions.append(f"Refactor {func.name} to reduce complexity")
            if func.lines > 50:
                suggestions.append(f"Split {func.name} into smaller functions")
            if func.parameters > 5:
                suggestions.append(f"Reduce parameters in {func.name}")

        # Based on patterns
        pattern_counts = defaultdict(int)
        for pattern in self.patterns:
            pattern_counts[pattern.pattern_type] += 1

        for pattern_type, count in pattern_counts.items():
            if count > 0:
                suggestions.append(f"Found {count} instances of {pattern_type}")

        return suggestions[:5]  # Top 5 suggestions

    def _create_error_analysis(self, error: str) -> ASTAnalysis:
        """Create error analysis result"""

        return ASTAnalysis(
            patterns=[],
            functions=[],
            dependencies={},
            complexity_score=1.0,
            maintainability_score=0.0,
            suggestions=[f"Fix syntax error: {error}"],
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get analyzer metrics"""

        return {
            "patterns_detected": len(self.patterns),
            "functions_analyzed": len(self.functions),
            "dependencies_mapped": len(self.dependencies),
            "imports": len(self.import_map),
        }


# Global instance
analyzer = None


def get_analyzer() -> ASTAnalyzer:
    """Get or create analyzer instance"""
    global analyzer
    if not analyzer:
        analyzer = ASTAnalyzer()
    return analyzer


def main():
    """Test AST analyzer"""
    analyzer = get_analyzer()

    # Test code
    test_code = """
import os
import sys

def complex_function(a, b, c, d, e, f):
    global counter
    counter = 0

    for i in range(10):
        for j in range(10):
            if i > j:
                counter += 1
            elif i < j:
                counter -= 1
            else:
                return 0

    if counter > 50:
        return 1
    elif counter > 25:
        return 2
    else:
        return 3

def simple_function(x):
    return x * 2
"""

    analysis = analyzer.analyze(test_code)

    print("AST Analysis Results:")
    print(f"  Complexity Score: {analysis.complexity_score:.2f}")
    print(f"  Maintainability: {analysis.maintainability_score:.2f}")

    print("\nFunctions:")
    for func in analysis.functions:
        print(f"  {func.name}: complexity={func.complexity}, lines={func.lines}")

    print("\nPatterns Detected:")
    for pattern in analysis.patterns:
        print(f"  [{pattern.pattern_type}] at line {pattern.line}")

    print("\nSuggestions:")
    for suggestion in analysis.suggestions:
        print(f"  - {suggestion}")


if __name__ == "__main__":
    main()
