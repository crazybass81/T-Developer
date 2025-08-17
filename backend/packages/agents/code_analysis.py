"""Code Analysis Agent - Analyzes internal codebase for improvements."""

import ast
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from packages.agents.base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent

logger = logging.getLogger("agents.code_analysis")


@dataclass
class CodeAnalysisConfig:
    """Configuration for code analysis agent."""

    max_files_to_scan: int = 100
    max_file_size_mb: float = 10
    ignore_patterns: list[str] = field(
        default_factory=lambda: ["__pycache__", ".git", "node_modules", ".venv", "dist", "build"]
    )
    focus_patterns: list[str] = field(default_factory=lambda: ["*.py", "*.js", "*.ts"])
    min_improvement_score: float = 0.3
    enable_deep_analysis: bool = True
    check_security: bool = True
    check_performance: bool = True
    check_maintainability: bool = True


class CodebaseAnalyzer:
    """Analyzes codebase structure and metrics."""

    def scan_directory(self, path: Path, config: CodeAnalysisConfig) -> list[Path]:
        """Scan directory for relevant files."""
        files = []

        for item in path.rglob("*"):
            if item.is_file():
                # Skip ignored patterns
                if any(pattern in str(item) for pattern in config.ignore_patterns):
                    continue

                # Check if matches focus patterns
                if config.focus_patterns:
                    if not any(item.match(pattern) for pattern in config.focus_patterns):
                        continue

                files.append(item)

        return files[: config.max_files_to_scan]

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """Analyze a single file for metrics."""
        metrics = {
            "path": str(file_path),
            "size_bytes": file_path.stat().st_size,
            "lines": 0,
            "complexity": 0,
            "functions": 0,
            "classes": 0,
            "docstring_coverage": 0,
            "type_hints_coverage": 0,
        }

        try:
            content = file_path.read_text()
            lines = content.splitlines()
            metrics["lines"] = len(lines)

            if file_path.suffix == ".py":
                tree = ast.parse(content)

                # Count elements
                functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

                metrics["functions"] = len(functions)
                metrics["classes"] = len(classes)

                # Calculate complexity
                metrics["complexity"] = self._calculate_complexity(tree)

                # Check docstrings
                funcs_with_docstring = sum(1 for f in functions if ast.get_docstring(f))
                if functions:
                    metrics["docstring_coverage"] = funcs_with_docstring / len(functions) * 100

                # Check type hints
                funcs_with_hints = sum(
                    1 for f in functions if f.returns or any(arg.annotation for arg in f.args.args)
                )
                if functions:
                    metrics["type_hints_coverage"] = funcs_with_hints / len(functions) * 100

        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")

        return metrics

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def find_code_smells(self, file_path: Path) -> list[dict[str, Any]]:
        """Detect code smells in file."""
        smells = []

        try:
            content = file_path.read_text()
            lines = content.splitlines()

            # Long file
            if len(lines) > 500:
                smells.append(
                    {
                        "type": "long_file",
                        "location": str(file_path),
                        "details": f"{len(lines)} lines",
                        "severity": "medium",
                    }
                )

            if file_path.suffix == ".py":
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    # Long function
                    if isinstance(node, ast.FunctionDef):
                        func_lines = node.end_lineno - node.lineno if node.end_lineno else 0
                        if func_lines > 50:
                            smells.append(
                                {
                                    "type": "long_function",
                                    "location": f"{file_path}:{node.lineno}",
                                    "function": node.name,
                                    "details": f"{func_lines} lines",
                                    "severity": "medium",
                                }
                            )

                        # Too many parameters
                        if len(node.args.args) > 5:
                            smells.append(
                                {
                                    "type": "too_many_parameters",
                                    "location": f"{file_path}:{node.lineno}",
                                    "function": node.name,
                                    "details": f"{len(node.args.args)} parameters",
                                    "severity": "low",
                                }
                            )

                    # Large class
                    if isinstance(node, ast.ClassDef):
                        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                        if len(methods) > 20:
                            smells.append(
                                {
                                    "type": "large_class",
                                    "location": f"{file_path}:{node.lineno}",
                                    "class": node.name,
                                    "details": f"{len(methods)} methods",
                                    "severity": "high",
                                }
                            )

        except Exception as e:
            logger.warning(f"Failed to detect code smells in {file_path}: {e}")

        return smells


class PatternDetector:
    """Detects design patterns and anti-patterns."""

    def detect_patterns(self, file_path: Path) -> list[dict[str, Any]]:
        """Detect design patterns in file."""
        patterns = []

        try:
            content = file_path.read_text()

            if file_path.suffix == ".py":
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Singleton pattern
                        has_instance = any(
                            isinstance(n, ast.AnnAssign) and n.target.id == "_instance"
                            for n in node.body
                            if isinstance(n, ast.AnnAssign) and hasattr(n.target, "id")
                        )
                        has_new = any(
                            isinstance(n, ast.FunctionDef) and n.name == "__new__"
                            for n in node.body
                        )
                        if has_instance or has_new:
                            patterns.append(
                                {
                                    "type": "singleton",
                                    "location": f"{file_path}:{node.lineno}",
                                    "class": node.name,
                                }
                            )

                        # Factory pattern
                        create_methods = [
                            n
                            for n in node.body
                            if isinstance(n, ast.FunctionDef) and "create" in n.name.lower()
                        ]
                        if len(create_methods) >= 2:
                            patterns.append(
                                {
                                    "type": "factory",
                                    "location": f"{file_path}:{node.lineno}",
                                    "class": node.name,
                                    "methods": [m.name for m in create_methods],
                                }
                            )

        except Exception as e:
            logger.warning(f"Failed to detect patterns in {file_path}: {e}")

        return patterns

    def detect_antipatterns(self, file_path: Path) -> list[dict[str, Any]]:
        """Detect anti-patterns in file."""
        antipatterns = []

        try:
            content = file_path.read_text()

            # God object detection
            if file_path.suffix == ".py":
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                        attributes = []

                        # Count attributes in __init__
                        for method in methods:
                            if method.name == "__init__":
                                for stmt in method.body:
                                    if isinstance(stmt, ast.Assign):
                                        for target in stmt.targets:
                                            if isinstance(target, ast.Attribute):
                                                attributes.append(target.attr)

                        if len(methods) > 20 or len(attributes) > 15:
                            antipatterns.append(
                                {
                                    "type": "god_object",
                                    "location": f"{file_path}:{node.lineno}",
                                    "class": node.name,
                                    "methods": len(methods),
                                    "attributes": len(attributes),
                                    "severity": "high",
                                }
                            )

            # Global state mutation
            if "global " in content:
                antipatterns.append(
                    {"type": "global_state", "location": str(file_path), "severity": "medium"}
                )

            # Magic numbers
            magic_numbers = re.findall(r"\b\d{3,}\b", content)
            if magic_numbers:
                antipatterns.append(
                    {
                        "type": "magic_numbers",
                        "location": str(file_path),
                        "instances": len(magic_numbers),
                        "severity": "low",
                    }
                )

        except Exception as e:
            logger.warning(f"Failed to detect antipatterns in {file_path}: {e}")

        return antipatterns


class ImprovementFinder:
    """Finds improvement opportunities in code."""

    def find_improvements(self, file_path: Path, metrics: dict) -> list[dict[str, Any]]:
        """Find improvement opportunities."""
        improvements = []

        try:
            content = file_path.read_text()

            if file_path.suffix == ".py":
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    # Missing docstrings
                    if isinstance(node, ast.FunctionDef):
                        if not ast.get_docstring(node):
                            improvements.append(
                                {
                                    "type": "missing_docstring",
                                    "location": f"{file_path}:{node.lineno}",
                                    "function": node.name,
                                    "priority": "medium",
                                    "effort": "low",
                                    "impact": "documentation",
                                }
                            )

                        # Missing type hints
                        if not node.returns:
                            improvements.append(
                                {
                                    "type": "missing_return_type",
                                    "location": f"{file_path}:{node.lineno}",
                                    "function": node.name,
                                    "priority": "low",
                                    "effort": "low",
                                    "impact": "type_safety",
                                }
                            )

                    # Missing class docstrings
                    if isinstance(node, ast.ClassDef):
                        if not ast.get_docstring(node):
                            improvements.append(
                                {
                                    "type": "missing_class_docstring",
                                    "location": f"{file_path}:{node.lineno}",
                                    "class": node.name,
                                    "priority": "medium",
                                    "effort": "low",
                                    "impact": "documentation",
                                }
                            )

            # Low test coverage hint
            if metrics.get("docstring_coverage", 0) < 50:
                improvements.append(
                    {
                        "type": "low_documentation",
                        "location": str(file_path),
                        "coverage": metrics["docstring_coverage"],
                        "priority": "high",
                        "effort": "medium",
                        "impact": "maintainability",
                    }
                )

        except Exception as e:
            logger.warning(f"Failed to find improvements in {file_path}: {e}")

        return improvements

    def score_improvements(self, improvements: list[dict]) -> list[dict]:
        """Score and prioritize improvements."""
        priority_scores = {"high": 3, "medium": 2, "low": 1}
        effort_scores = {"low": 3, "medium": 2, "high": 1}

        for imp in improvements:
            priority = priority_scores.get(imp.get("priority", "low"), 1)
            effort = effort_scores.get(imp.get("effort", "medium"), 2)
            imp["score"] = (priority * 2 + effort) / 3  # Weighted score

        return sorted(improvements, key=lambda x: x.get("score", 0), reverse=True)


class CodeAnalysisAgent(BaseAgent):
    """Agent for analyzing internal codebase."""

    def __init__(self, name: str = "code_analysis", config: Optional[CodeAnalysisConfig] = None):
        """Initialize code analysis agent."""
        super().__init__(name, {"timeout": 300})
        self.config = config or CodeAnalysisConfig()
        self.analyzer = CodebaseAnalyzer()
        self.detector = PatternDetector()
        self.finder = ImprovementFinder()

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Execute code analysis task."""
        try:
            target_path = Path(input.payload.get("target_path", "."))

            # Handle both file and directory
            if target_path.is_file():
                files = [target_path]
            else:
                files = self.analyzer.scan_directory(target_path, self.config)

            # Analyze files
            all_metrics = []
            all_smells = []
            all_patterns = []
            all_antipatterns = []
            all_improvements = []

            for file in files:
                # Skip large files
                if file.stat().st_size > self.config.max_file_size_mb * 1024 * 1024:
                    continue

                # Analyze metrics
                metrics = self.analyzer.analyze_file(file)
                all_metrics.append(metrics)

                # Detect issues
                smells = self.analyzer.find_code_smells(file)
                patterns = self.detector.detect_patterns(file)
                antipatterns = self.detector.detect_antipatterns(file)
                improvements = self.finder.find_improvements(file, metrics)

                all_smells.extend(smells)
                all_patterns.extend(patterns)
                all_antipatterns.extend(antipatterns)
                all_improvements.extend(improvements)

            # Score and filter improvements
            scored_improvements = self.finder.score_improvements(all_improvements)
            filtered_improvements = [
                imp
                for imp in scored_improvements
                if imp.get("score", 0) >= self.config.min_improvement_score
            ]

            # Calculate summary metrics
            total_lines = sum(m["lines"] for m in all_metrics)
            avg_complexity = (
                sum(m["complexity"] for m in all_metrics) / len(all_metrics) if all_metrics else 0
            )
            avg_docstring_coverage = (
                sum(m["docstring_coverage"] for m in all_metrics) / len(all_metrics)
                if all_metrics
                else 0
            )

            # Store analysis results in context store
            evolution_id = input.context.get("evolution_id") if input.context else None
            await self.context_store.store_original_analysis(
                files_analyzed=len(all_metrics),
                metrics={
                    "total_lines": total_lines,
                    "avg_complexity": round(avg_complexity, 2),
                    "avg_docstring_coverage": round(avg_docstring_coverage, 2),
                },
                issues=[
                    {"type": "code_smell", "items": all_smells},
                    {"type": "antipattern", "items": all_antipatterns},
                ],
                improvements=filtered_improvements,
                evolution_id=evolution_id,
            )
            self.logger.info(
                f"Stored analysis results in context store for evolution {evolution_id or 'current'}"
            )

            # Create artifacts
            artifacts = [
                Artifact(
                    kind="report",
                    ref="metrics.json",
                    content=json.dumps(all_metrics, indent=2),
                    metadata={"files_analyzed": len(all_metrics)},
                ),
                Artifact(
                    kind="report",
                    ref="improvements.json",
                    content=json.dumps(filtered_improvements, indent=2),
                    metadata={"total_improvements": len(filtered_improvements)},
                ),
            ]

            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.OK,
                artifacts=artifacts,
                metrics={
                    "files_analyzed": len(all_metrics),
                    "total_lines": total_lines,
                    "avg_complexity": round(avg_complexity, 2),
                    "avg_docstring_coverage": round(avg_docstring_coverage, 2),
                    "code_smells_count": len(all_smells),
                    "patterns_detected": len(all_patterns),
                    "antipatterns_detected": len(all_antipatterns),
                    "improvements_found": len(filtered_improvements),
                    "issues_found": len(all_smells) + len(all_antipatterns),
                    "improvements": filtered_improvements,
                    "patterns": all_patterns,
                    "antipatterns": all_antipatterns,
                    "code_smells": all_smells,
                },
            )

        except Exception as e:
            logger.error(f"Code analysis failed: {e}")
            return AgentOutput(task_id=input.task_id, status=AgentStatus.FAIL, error=str(e))

    def validate(self, input: AgentInput) -> bool:
        """Validate input for code analysis."""
        if "target_path" not in input.payload:
            logger.error("Missing target_path in input")
            return False

        target_path = Path(input.payload["target_path"])
        if not target_path.exists():
            logger.error(f"Target path does not exist: {target_path}")
            return False

        return True

    def get_capabilities(self) -> dict[str, Any]:
        """Get agent capabilities."""
        return {
            "type": "code_analysis",
            "name": self.name,
            "version": "1.0.0",
            "supported_languages": ["python", "javascript", "typescript"],
            "analysis_types": [
                "metrics",
                "code_smells",
                "patterns",
                "antipatterns",
                "improvements",
            ],
            "max_files": self.config.max_files_to_scan,
            "features": {
                "complexity_analysis": True,
                "docstring_coverage": True,
                "type_hints_coverage": True,
                "pattern_detection": True,
                "antipattern_detection": True,
                "improvement_suggestions": True,
            },
        }
