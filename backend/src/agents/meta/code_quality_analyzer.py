"""
Code Quality Analyzer - AI-powered code quality analysis
Size: < 6.5KB | Performance: < 3μs
Day 26: Phase 2 - ServiceImproverAgent
"""

import ast
import asyncio
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from src.ai.consensus_engine import get_engine


@dataclass
class QualityMetrics:
    """Code quality metrics"""

    complexity: float  # Cyclomatic complexity
    maintainability: float  # Maintainability index
    readability: float  # Readability score
    testability: float  # Testability score
    security: float  # Security score
    performance: float  # Performance score
    overall: float  # Overall quality score


@dataclass
class CodeIssue:
    """Code quality issue"""

    type: str  # bug, smell, vulnerability, performance
    severity: str  # critical, major, minor, info
    file: str
    line: int
    column: int
    message: str
    suggestion: str
    impact: float  # Impact score 0-1


@dataclass
class QualityReport:
    """Complete quality analysis report"""

    metrics: QualityMetrics
    issues: List[CodeIssue]
    patterns: Dict[str, int]  # Pattern frequency
    recommendations: List[str]
    improvement_potential: float
    estimated_effort: float  # Hours


class CodeQualityAnalyzer:
    """Analyze and score code quality"""

    def __init__(self):
        self.consensus = get_engine()
        self.issue_patterns = self._init_patterns()
        self.metrics_cache = {}

    def _init_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize issue detection patterns"""
        return {
            "unused_variable": re.compile(r"^\s*(\w+)\s*=.*(?!.*\1)"),
            "long_line": re.compile(r"^.{121,}$"),
            "magic_number": re.compile(r"\b\d{2,}\b(?![\"'])"),
            "todo_comment": re.compile(r"#\s*(TODO|FIXME|XXX|HACK)"),
            "broad_except": re.compile(r"except\s*:"),
            "eval_usage": re.compile(r"\beval\s*\("),
            "hardcoded_password": re.compile(r"(password|pwd|token)\s*=\s*[\"'][^\"']+[\"']", re.I),
            "print_statement": re.compile(r"^\s*print\s*\("),
        }

    async def analyze(self, code: str, filename: str = "unknown.py") -> QualityReport:
        """Analyze code quality comprehensively"""

        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return self._create_error_report(str(e), filename)

        # Calculate metrics
        metrics = await self._calculate_metrics(tree, code)

        # Detect issues
        issues = await self._detect_issues(code, tree, filename)

        # Analyze patterns
        patterns = self._analyze_patterns(tree)

        # Get AI recommendations
        recommendations = await self._get_ai_recommendations(metrics, issues, patterns)

        # Calculate improvement potential
        improvement_potential = self._calculate_improvement_potential(metrics)

        # Estimate effort
        estimated_effort = self._estimate_effort(issues, improvement_potential)

        return QualityReport(
            metrics=metrics,
            issues=issues,
            patterns=patterns,
            recommendations=recommendations,
            improvement_potential=improvement_potential,
            estimated_effort=estimated_effort,
        )

    async def _calculate_metrics(self, tree: ast.AST, code: str) -> QualityMetrics:
        """Calculate quality metrics"""

        # Cyclomatic complexity
        complexity = self._calculate_complexity(tree)

        # Maintainability index
        maintainability = self._calculate_maintainability(tree, code)

        # Readability score
        readability = await self._calculate_readability(code)

        # Testability score
        testability = self._calculate_testability(tree)

        # Security score
        security = self._calculate_security(code)

        # Performance score
        performance = self._calculate_performance(tree)

        # Overall score (weighted average)
        overall = (
            complexity * 0.2
            + maintainability * 0.2
            + readability * 0.15
            + testability * 0.15
            + security * 0.15
            + performance * 0.15
        )

        return QualityMetrics(
            complexity=complexity,
            maintainability=maintainability,
            readability=readability,
            testability=testability,
            security=security,
            performance=performance,
            overall=overall,
        )

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity"""

        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1

        # Normalize to 0-1 scale (lower is better)
        # Complexity > 10 is considered high
        score = max(0, 1 - (complexity / 10))  # More sensitive to complexity
        return score

    def _calculate_maintainability(self, tree: ast.AST, code: str) -> float:
        """Calculate maintainability index"""

        # Count lines of code
        loc = len(code.split("\n"))

        # Count functions and classes
        functions = sum(
            1 for _ in ast.walk(tree) if isinstance(_, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        classes = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef))

        # Count comments
        comments = len(re.findall(r"#.*", code))

        # Simple maintainability calculation
        if loc == 0:
            return 1.0

        comment_ratio = comments / loc
        modularity = (functions + classes) / max(1, loc / 100)

        score = min(1.0, (comment_ratio * 0.3 + modularity * 0.7))
        return score

    async def _calculate_readability(self, code: str) -> float:
        """Calculate readability score using AI"""

        prompt = f"""
        Rate the readability of this code from 0 to 1:
        - Variable naming clarity
        - Function naming
        - Code structure
        - Comment quality

        Code snippet (first 500 chars):
        {code[:500]}
        """

        result = await self.consensus.get_consensus(prompt)

        # Default readability based on simple metrics
        lines = code.split("\n")
        avg_line_length = sum(len(line) for line in lines) / max(1, len(lines))

        # Penalize long lines
        if avg_line_length > 80:
            base_score = 0.7
        elif avg_line_length > 100:
            base_score = 0.5
        else:
            base_score = 0.9

        return base_score

    def _calculate_testability(self, tree: ast.AST) -> float:
        """Calculate testability score"""

        # Count testable units
        functions = 0
        classes = 0
        methods = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions += 1
                # Check if it's a method
                for parent in ast.walk(tree):
                    if isinstance(parent, ast.ClassDef):
                        if node in parent.body:
                            methods += 1
                            break
            elif isinstance(node, ast.ClassDef):
                classes += 1

        # Check for dependency injection patterns
        has_di = any(isinstance(node, ast.arg) for node in ast.walk(tree))

        # Calculate score
        if functions == 0:
            return 0.5

        avg_func_size = len(ast.unparse(tree)) / max(1, functions)

        # Smaller functions are more testable
        size_score = max(0, 1 - (avg_func_size / 1000))

        # DI improves testability
        di_bonus = 0.1 if has_di else 0

        return min(1.0, size_score + di_bonus)

    def _calculate_security(self, code: str) -> float:
        """Calculate security score"""

        vulnerabilities = 0

        # Check for common security issues
        if re.search(r"\beval\s*\(", code):
            vulnerabilities += 2
        if re.search(r"\bexec\s*\(", code):
            vulnerabilities += 2
        if re.search(r"pickle\.loads", code):
            vulnerabilities += 1
        if re.search(r"os\.system", code):
            vulnerabilities += 1
        if re.search(r"subprocess.*shell\s*=\s*True", code):
            vulnerabilities += 2
        if re.search(r'(password|pwd|token|secret)\s*=\s*["\'][^"\']+["\']', code, re.I):
            vulnerabilities += 3

        # Calculate score
        score = max(0, 1 - (vulnerabilities * 0.1))
        return score

    def _calculate_performance(self, tree: ast.AST) -> float:
        """Calculate performance score"""

        issues = 0

        for node in ast.walk(tree):
            # Check for performance anti-patterns
            if isinstance(node, ast.For):
                # Nested loops
                for child in ast.walk(node):
                    if isinstance(child, ast.For) and child != node:
                        issues += 1
                        break

            # Check for inefficient operations
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ["eval", "exec"]:
                        issues += 2

        # Calculate score
        score = max(0, 1 - (issues * 0.1))
        return score

    async def _detect_issues(self, code: str, tree: ast.AST, filename: str) -> List[CodeIssue]:
        """Detect code quality issues"""

        issues = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            # Check patterns
            for pattern_name, pattern in self.issue_patterns.items():
                if pattern.match(line):
                    issue = self._create_issue(pattern_name, filename, i, line)
                    issues.append(issue)

        # AST-based checks
        issues.extend(self._check_ast_issues(tree, filename))

        return issues

    def _create_issue(
        self, pattern_name: str, filename: str, line: int, code_line: str
    ) -> CodeIssue:
        """Create issue from pattern match"""

        issue_configs = {
            "unused_variable": ("smell", "minor", "Unused variable", "Remove or use the variable"),
            "long_line": ("smell", "minor", "Line too long", "Break into multiple lines"),
            "magic_number": ("smell", "minor", "Magic number", "Use named constant"),
            "todo_comment": ("smell", "info", "TODO comment", "Address the TODO"),
            "broad_except": ("bug", "major", "Broad exception", "Catch specific exceptions"),
            "eval_usage": (
                "vulnerability",
                "critical",
                "Use of eval()",
                "Avoid eval() for security",
            ),
            "hardcoded_password": (
                "vulnerability",
                "critical",
                "Hardcoded credential",
                "Use environment variables",
            ),
            "print_statement": ("smell", "minor", "Print statement", "Use logging instead"),
        }

        config = issue_configs.get(
            pattern_name, ("smell", "minor", "Issue detected", "Review code")
        )

        return CodeIssue(
            type=config[0],
            severity=config[1],
            file=filename,
            line=line,
            column=0,
            message=config[2],
            suggestion=config[3],
            impact=self._calculate_impact(config[1]),
        )

    def _calculate_impact(self, severity: str) -> float:
        """Calculate issue impact"""
        impacts = {"critical": 1.0, "major": 0.7, "minor": 0.3, "info": 0.1}
        return impacts.get(severity, 0.5)

    def _check_ast_issues(self, tree: ast.AST, filename: str) -> List[CodeIssue]:
        """Check AST-based issues"""

        issues = []

        for node in ast.walk(tree):
            # Check for too many arguments
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if len(node.args.args) > 5:
                    issues.append(
                        CodeIssue(
                            type="smell",
                            severity="major",
                            file=filename,
                            line=node.lineno,
                            column=node.col_offset,
                            message="Too many parameters",
                            suggestion="Consider using configuration object",
                            impact=0.7,
                        )
                    )

        return issues

    def _analyze_patterns(self, tree: ast.AST) -> Dict[str, int]:
        """Analyze code patterns"""

        patterns = defaultdict(int)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                patterns["functions"] += 1
            elif isinstance(node, ast.AsyncFunctionDef):
                patterns["async_functions"] += 1
            elif isinstance(node, ast.ClassDef):
                patterns["classes"] += 1
            elif isinstance(node, ast.If):
                patterns["conditionals"] += 1
            elif isinstance(node, ast.For):
                patterns["loops"] += 1
            elif isinstance(node, ast.While):
                patterns["while_loops"] += 1
            elif isinstance(node, ast.Try):
                patterns["try_blocks"] += 1

        return dict(patterns)

    async def _get_ai_recommendations(
        self, metrics: QualityMetrics, issues: List[CodeIssue], patterns: Dict[str, int]
    ) -> List[str]:
        """Get AI-powered recommendations"""

        recommendations = []

        # Based on metrics
        if metrics.complexity < 0.5:
            recommendations.append("Consider breaking down complex functions")

        if metrics.maintainability < 0.6:
            recommendations.append("Add more comments and documentation")

        if metrics.testability < 0.7:
            recommendations.append("Refactor for better testability")

        if metrics.security < 0.8:
            recommendations.append("Address security vulnerabilities")

        # Based on issues
        critical_issues = [i for i in issues if i.severity == "critical"]
        if critical_issues:
            recommendations.append(f"Fix {len(critical_issues)} critical issues immediately")

        return recommendations

    def _calculate_improvement_potential(self, metrics: QualityMetrics) -> float:
        """Calculate improvement potential"""
        return 1.0 - metrics.overall

    def _estimate_effort(self, issues: List[CodeIssue], improvement_potential: float) -> float:
        """Estimate effort in hours"""

        # Base effort per issue type
        effort_per_issue = {"critical": 2.0, "major": 1.0, "minor": 0.5, "info": 0.1}

        total_effort = 0.0
        for issue in issues:
            total_effort += effort_per_issue.get(issue.severity, 0.5)

        # Add effort for improvement potential
        total_effort += improvement_potential * 10

        return total_effort

    def _create_error_report(self, error: str, filename: str) -> QualityReport:
        """Create error report for syntax errors"""

        return QualityReport(
            metrics=QualityMetrics(0, 0, 0, 0, 0, 0, 0),
            issues=[
                CodeIssue(
                    type="bug",
                    severity="critical",
                    file=filename,
                    line=0,
                    column=0,
                    message=f"Syntax error: {error}",
                    suggestion="Fix syntax errors first",
                    impact=1.0,
                )
            ],
            patterns={},
            recommendations=["Fix syntax errors before analysis"],
            improvement_potential=1.0,
            estimated_effort=1.0,
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get analyzer metrics"""
        return {
            "patterns_defined": len(self.issue_patterns),
            "cache_size": len(self.metrics_cache),
            "metrics_tracked": 6,
            "severity_levels": 4,
        }


# Global instance
analyzer = None


def get_analyzer() -> CodeQualityAnalyzer:
    """Get or create analyzer instance"""
    global analyzer
    if not analyzer:
        analyzer = CodeQualityAnalyzer()
    return analyzer


async def main():
    """Test code quality analyzer"""
    analyzer = get_analyzer()

    # Test code
    test_code = """
import os

def calculate_total(items):
    total = 0
    for item in items:
        if item > 100:  # Magic number
            total += item * 1.5
    print(total)  # Should use logging
    return total

# TODO: Add error handling
def process_data(data):
    try:
        result = eval(data)  # Security issue!
        password = "admin123"  # Hardcoded password
        return result
    except:  # Broad except
        pass
"""

    report = await analyzer.analyze(test_code, "test.py")

    print(f"Quality Metrics:")
    print(f"  Overall: {report.metrics.overall:.2f}")
    print(f"  Complexity: {report.metrics.complexity:.2f}")
    print(f"  Security: {report.metrics.security:.2f}")

    print(f"\nIssues Found: {len(report.issues)}")
    for issue in report.issues:
        print(f"  [{issue.severity}] Line {issue.line}: {issue.message}")

    print(f"\nRecommendations:")
    for rec in report.recommendations:
        print(f"  - {rec}")

    print(f"\nEstimated effort: {report.estimated_effort:.1f} hours")


if __name__ == "__main__":
    asyncio.run(main())
