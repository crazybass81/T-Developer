"""Quality Gate - Code quality metrics and enforcement."""

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("evaluation.quality_gate")


@dataclass
class QualityConfig:
    """Configuration for quality checks."""

    min_docstring_coverage: float = 80.0
    max_complexity: int = 10
    max_maintainability_index: int = 100
    min_maintainability_index: int = 20
    max_line_length: int = 100
    max_file_lines: int = 500
    check_type_hints: bool = True
    excluded_paths: list[str] = field(
        default_factory=lambda: ["tests/", "test_", ".git/", "__pycache__/", ".venv/", "venv/"]
    )


@dataclass
class QualityMetrics:
    """Quality metrics for codebase."""

    docstring_coverage: float = 0.0
    cyclomatic_complexity: float = 0.0
    maintainability_index: float = 0.0
    lines_of_code: int = 0
    test_coverage: float = 0.0
    type_hint_coverage: float = 0.0

    def passes_thresholds(self, config: QualityConfig) -> bool:
        """Check if metrics pass configured thresholds."""
        if self.docstring_coverage < config.min_docstring_coverage:
            return False
        if self.cyclomatic_complexity > config.max_complexity:
            return False
        if self.maintainability_index < config.min_maintainability_index:
            return False
        if self.maintainability_index > config.max_maintainability_index:
            return False
        return True


@dataclass
class ComplexityResult:
    """Result of complexity analysis."""

    average_complexity: float = 0.0
    max_complexity: float = 0.0
    complex_functions: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DocstringCoverage:
    """Docstring coverage result."""

    total_items: int = 0
    documented_items: int = 0
    coverage_percentage: float = 0.0
    missing_docstrings: list[str] = field(default_factory=list)


@dataclass
class TypeHintCoverage:
    """Type hint coverage result."""

    total_parameters: int = 0
    typed_parameters: int = 0
    coverage_percentage: float = 0.0
    missing_hints: list[str] = field(default_factory=list)


@dataclass
class QualityResult:
    """Overall quality check result."""

    passed: bool = True
    total_files: int = 0
    files_with_issues: int = 0
    metrics: QualityMetrics = field(default_factory=QualityMetrics)
    issues: list[dict[str, Any]] = field(default_factory=list)
    scan_duration_seconds: float = 0.0


class ComplexityAnalyzer:
    """Analyzes code complexity metrics."""

    def analyze_file(self, file_path: Path) -> ComplexityResult:
        """Analyze complexity of a Python file."""
        result = ComplexityResult()

        try:
            with open(file_path) as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            complexities = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    complexities.append(complexity)

                    if complexity > 10:  # Track complex functions
                        result.complex_functions.append(
                            {"name": node.name, "complexity": complexity, "line": node.lineno}
                        )

            if complexities:
                result.average_complexity = sum(complexities) / len(complexities)
                result.max_complexity = max(complexities)

        except Exception as e:
            logger.error(f"Failed to analyze complexity for {file_path}: {e}")

        return result

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Decision points increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
                # Extra complexity for elif branches
                if hasattr(child, "orelse") and child.orelse:
                    # Check if it's an elif (not just else)
                    if isinstance(child.orelse[0] if child.orelse else None, ast.If):
                        complexity += 1
            elif isinstance(child, ast.BoolOp):
                # and/or operators add branches
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += sum(1 for _ in child.ifs)
            # Add extra complexity for nested if statements
            elif isinstance(child, ast.IfExp):  # Ternary operator
                complexity += 1

        return complexity

    def calculate_maintainability_index(self, file_path: Path) -> float:
        """Calculate maintainability index for a file."""
        try:
            with open(file_path) as f:
                content = f.read()

            lines = content.splitlines()
            loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])

            # Simplified maintainability index calculation
            # Real formula involves Halstead volume and cyclomatic complexity
            complexity_result = self.analyze_file(file_path)
            avg_complexity = complexity_result.average_complexity or 1

            # Basic approximation: MI = 171 - 5.2*ln(V) - 0.23*G - 16.2*ln(L)
            # Using simplified version
            import math

            if loc == 0:
                return 100.0

            # Simplified calculation
            mi = 171 - 5.2 * math.log(max(loc, 1)) - 0.23 * avg_complexity

            # Clamp between 0 and 100
            return max(0.0, min(100.0, mi))

        except Exception as e:
            logger.error(f"Failed to calculate MI for {file_path}: {e}")
            return 50.0  # Default middle value


class DocstringAnalyzer:
    """Analyzes docstring coverage."""

    def analyze_file(self, file_path: Path) -> DocstringCoverage:
        """Analyze docstring coverage for a Python file."""
        coverage = DocstringCoverage()

        try:
            with open(file_path) as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))

            # Check module docstring
            has_module_docstring = ast.get_docstring(tree) is not None
            if has_module_docstring:
                coverage.documented_items += 1
                coverage.total_items += 1
            else:
                # Only count module if it doesn't have a docstring
                coverage.total_items += 1

            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    coverage.total_items += 1

                    if ast.get_docstring(node):
                        coverage.documented_items += 1
                    else:
                        coverage.missing_docstrings.append(f"{file_path}:{node.lineno} {node.name}")

            if coverage.total_items > 0:
                coverage.coverage_percentage = (
                    coverage.documented_items / coverage.total_items * 100
                )

        except Exception as e:
            logger.error(f"Failed to analyze docstrings for {file_path}: {e}")

        return coverage

    def check_type_hints(self, file_path: Path) -> TypeHintCoverage:
        """Check type hint coverage for a Python file."""
        coverage = TypeHintCoverage()

        try:
            with open(file_path) as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Count parameters
                    for arg in node.args.args:
                        if arg.arg != "self":
                            coverage.total_parameters += 1
                            if arg.annotation:
                                coverage.typed_parameters += 1
                            else:
                                coverage.missing_hints.append(
                                    f"{file_path}:{node.lineno} {node.name}.{arg.arg}"
                                )

                    # Check return type
                    if node.name != "__init__":
                        coverage.total_parameters += 1  # Count return as parameter
                        if node.returns:
                            coverage.typed_parameters += 1
                        else:
                            coverage.missing_hints.append(
                                f"{file_path}:{node.lineno} {node.name} (return)"
                            )

            if coverage.total_parameters > 0:
                coverage.coverage_percentage = (
                    coverage.typed_parameters / coverage.total_parameters * 100
                )

        except Exception as e:
            logger.error(f"Failed to check type hints for {file_path}: {e}")

        return coverage


class QualityGate:
    """Main quality gate orchestrator."""

    def __init__(self, config: Optional[QualityConfig] = None):
        """Initialize quality gate."""
        self.config = config or QualityConfig()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.docstring_analyzer = DocstringAnalyzer()

    async def analyze_codebase(self, target_path: Path) -> QualityResult:
        """Analyze entire codebase quality."""
        import time

        start_time = time.time()

        result = QualityResult()

        # Collect Python files
        python_files = []

        # Ensure path is Path object
        target_path = Path(target_path)

        if not target_path.exists():
            logger.error(f"Target path does not exist: {target_path}")
            return result

        if target_path.is_dir():
            # Use rglob for recursive globbing
            python_files = list(target_path.rglob("*.py"))
            logger.debug(f"Found {len(python_files)} Python files in {target_path}")
        elif target_path.is_file() and target_path.suffix == ".py":
            python_files = [target_path]

        # Filter excluded paths
        filtered_files = []
        for file_path in python_files:
            skip = False
            for excluded in self.config.excluded_paths:
                if excluded in str(file_path):
                    skip = True
                    break
            if not skip:
                filtered_files.append(file_path)

        logger.debug(f"After filtering: {len(filtered_files)} files from {len(python_files)} total")

        result.total_files = len(filtered_files)

        # Aggregate metrics
        total_complexity = 0.0
        total_mi = 0.0
        total_loc = 0
        docstring_totals = {"total": 0, "documented": 0}
        type_hint_totals = {"total": 0, "typed": 0}

        for file_path in filtered_files:
            # Complexity analysis
            complexity_result = self.complexity_analyzer.analyze_file(file_path)
            if complexity_result.average_complexity > 0:
                total_complexity += complexity_result.average_complexity

            # Maintainability index
            mi = self.complexity_analyzer.calculate_maintainability_index(file_path)
            total_mi += mi

            # Lines of code
            try:
                with open(file_path) as f:
                    lines = f.readlines()
                    total_loc += len([l for l in lines if l.strip()])
            except:
                pass

            # Docstring coverage
            doc_coverage = self.docstring_analyzer.analyze_file(file_path)
            docstring_totals["total"] += doc_coverage.total_items
            docstring_totals["documented"] += doc_coverage.documented_items

            # Type hints
            if self.config.check_type_hints:
                type_coverage = self.docstring_analyzer.check_type_hints(file_path)
                type_hint_totals["total"] += type_coverage.total_parameters
                type_hint_totals["typed"] += type_coverage.typed_parameters

            # Check for issues
            file_issues = await self.check_file_quality(file_path)
            if file_issues:
                result.files_with_issues += 1
                result.issues.extend(file_issues)

        # Calculate average metrics
        if result.total_files > 0:
            result.metrics.cyclomatic_complexity = total_complexity / result.total_files
            result.metrics.maintainability_index = total_mi / result.total_files

        result.metrics.lines_of_code = total_loc

        if docstring_totals["total"] > 0:
            result.metrics.docstring_coverage = (
                docstring_totals["documented"] / docstring_totals["total"] * 100
            )

        if type_hint_totals["total"] > 0:
            result.metrics.type_hint_coverage = (
                type_hint_totals["typed"] / type_hint_totals["total"] * 100
            )

        # Determine pass/fail
        result.passed = result.metrics.passes_thresholds(self.config)

        result.scan_duration_seconds = time.time() - start_time

        return result

    async def check_file_quality(self, file_path: Path) -> list[dict[str, Any]]:
        """Check quality issues in a single file."""
        issues = []

        # Check file size
        try:
            with open(file_path) as f:
                lines = f.readlines()

            if len(lines) > self.config.max_file_lines:
                issues.append(
                    {
                        "file": str(file_path),
                        "issue": f"File too long ({len(lines)} lines)",
                        "severity": "medium",
                    }
                )

            # Check line length
            for i, line in enumerate(lines, 1):
                if len(line.rstrip()) > self.config.max_line_length:
                    issues.append(
                        {
                            "file": str(file_path),
                            "issue": "Line too long",
                            "line": i,
                            "length": len(line.rstrip()),
                            "severity": "low",
                        }
                    )
                    break  # Only report first occurrence

        except Exception as e:
            logger.error(f"Failed to check file {file_path}: {e}")

        # Check complexity
        complexity_result = self.complexity_analyzer.analyze_file(file_path)
        for func in complexity_result.complex_functions:
            if func["complexity"] > self.config.max_complexity:
                issues.append(
                    {
                        "file": str(file_path),
                        "issue": "High complexity",
                        "function": func["name"],
                        "complexity": func["complexity"],
                        "line": func["line"],
                        "severity": "high",
                    }
                )

        # Check docstrings
        doc_coverage = self.docstring_analyzer.analyze_file(file_path)
        if doc_coverage.coverage_percentage < self.config.min_docstring_coverage:
            for missing in doc_coverage.missing_docstrings[:3]:  # Limit to 3
                parts = missing.split(":")
                issues.append(
                    {
                        "file": str(file_path),
                        "issue": "Missing docstring",
                        "location": parts[-1] if parts else "unknown",
                        "line": int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0,
                        "severity": "medium",
                    }
                )

        return issues

    async def generate_report(self, result: QualityResult) -> str:
        """Generate human-readable quality report."""
        report = ["# Quality Gate Report\n"]

        # Status
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        report.append(f"## Status: {status}\n")

        report.append(f"**Scan Duration:** {result.scan_duration_seconds:.2f} seconds\n")
        report.append(f"**Total Files:** {result.total_files}\n")
        report.append(f"**Files with Issues:** {result.files_with_issues}\n")

        # Metrics
        report.append("\n## Quality Metrics\n")
        report.append(f"- Docstring Coverage: {result.metrics.docstring_coverage:.1f}%")
        report.append(f"- Cyclomatic Complexity: {result.metrics.cyclomatic_complexity:.1f}")
        report.append(f"- Maintainability Index: {result.metrics.maintainability_index:.1f}")
        report.append(f"- Lines of Code: {result.metrics.lines_of_code}")

        if result.metrics.test_coverage > 0:
            report.append(f"- Test Coverage: {result.metrics.test_coverage:.1f}%")
        if result.metrics.type_hint_coverage > 0:
            report.append(f"- Type Hint Coverage: {result.metrics.type_hint_coverage:.1f}%")

        # Issues
        if result.issues:
            report.append("\n## Quality Issues\n")

            # Group by severity
            for severity in ["high", "medium", "low"]:
                severity_issues = [i for i in result.issues if i.get("severity") == severity]

                if severity_issues:
                    report.append(f"\n### {severity.upper()} Severity\n")

                    for issue in severity_issues[:10]:  # Limit display
                        file_info = f"`{issue.get('file', 'unknown')}"
                        if issue.get("line"):
                            file_info += f":{issue['line']}"
                        file_info += "`"

                        report.append(f"- {file_info}: {issue.get('issue', 'Unknown issue')}")

                        if issue.get("complexity"):
                            report.append(f"  - Complexity: {issue['complexity']}")
                        if issue.get("function"):
                            report.append(f"  - Function: {issue['function']}")

        return "\n".join(report)

    async def create_github_comment(self, result: QualityResult) -> str:
        """Create GitHub PR comment with quality results."""
        status_emoji = "✅" if result.passed else "❌"
        status_text = "**PASSED**" if result.passed else "**FAILED**"

        comment = ["## 📊 Code Quality Results\n", f"{status_emoji} {status_text}\n"]

        # Metrics summary
        comment.append(f"**Docstring Coverage:** {result.metrics.docstring_coverage:.1f}%")
        comment.append(f"**Complexity:** {result.metrics.cyclomatic_complexity:.1f}")
        comment.append(f"**Maintainability:** {result.metrics.maintainability_index:.1f}")

        if result.metrics.test_coverage > 0:
            comment.append(f"**Test Coverage:** {result.metrics.test_coverage:.1f}%")

        # Top issues
        if result.issues:
            high_issues = [i for i in result.issues if i.get("severity") == "high"][:3]

            if high_issues:
                comment.append("\n### ⚠️ Top Quality Issues\n")

                for issue in high_issues:
                    location = f"`{issue.get('file', '')}:{issue.get('line', '')}`"
                    comment.append(f"- {issue.get('issue', '')}: {location}")

        if not result.passed:
            comment.append("\n❗ **Action Required:** Please improve code quality before merging.")

        return "\n".join(comment)
