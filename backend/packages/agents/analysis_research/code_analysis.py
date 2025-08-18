"""Code Analysis Agent - Analyzes internal codebase for improvements."""

import ast
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent

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

    def scan_directory(
        self,
        path: Path,
        max_files: int = 100,
        ignore_patterns: Optional[list[str]] = None,
        focus_patterns: Optional[list[str]] = None,
    ) -> list[Path]:
        """Scan directory for relevant files."""
        if ignore_patterns is None:
            ignore_patterns = ["__pycache__", ".git", "node_modules", ".venv", "dist", "build"]

        files = []

        for item in path.rglob("*"):
            if item.is_file():
                # Skip ignored patterns
                if any(pattern in str(item) for pattern in ignore_patterns):
                    continue

                # Check if matches focus patterns
                if focus_patterns:
                    if not any(item.match(pattern) for pattern in focus_patterns):
                        continue

                files.append(item)

        return files[:max_files]

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

                        # Check nesting depth
                        depth = self._get_nesting_depth(node)
                        if depth > 4:
                            smells.append(
                                {
                                    "type": "deep_nesting",
                                    "location": f"{file_path}:{node.lineno}",
                                    "function": node.name,
                                    "details": f"Nesting depth: {depth}",
                                    "severity": "medium",
                                }
                            )

                    # God class
                    if isinstance(node, ast.ClassDef):
                        method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                        if method_count > 20:
                            smells.append(
                                {
                                    "type": "god_class",
                                    "location": f"{file_path}:{node.lineno}",
                                    "class": node.name,
                                    "details": f"{method_count} methods",
                                    "severity": "high",
                                }
                            )

            # Check for TODO/FIXME comments
            todo_count = sum(1 for line in lines if "TODO" in line or "FIXME" in line)
            if todo_count > 3:
                smells.append(
                    {
                        "type": "too_many_todos",
                        "location": str(file_path),
                        "details": f"{todo_count} TODOs/FIXMEs",
                        "severity": "low",
                    }
                )

        except Exception as e:
            logger.warning(f"Failed to check smells in {file_path}: {e}")

        return smells

    def _get_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Get maximum nesting depth of a node."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                child_depth = self._get_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth


class PatternDetector:
    """Detects design patterns and anti-patterns."""

    def detect_patterns(self, file_path: Path) -> list[str]:
        """Detect design patterns in file."""
        patterns = []

        try:
            content = file_path.read_text().lower()

            # Pattern detection based on keywords and structure
            pattern_keywords = {
                "singleton": ["_instance", "singleton", "__new__"],
                "factory": ["factory", "create", "build"],
                "observer": ["observer", "notify", "subscribe", "attach"],
                "strategy": ["strategy", "algorithm", "context"],
                "decorator": ["decorator", "wrapper", "functools.wraps"],
                "adapter": ["adapter", "adapt", "wrapper"],
                "facade": ["facade", "interface", "simplified"],
                "proxy": ["proxy", "surrogate", "placeholder"],
            }

            for pattern, keywords in pattern_keywords.items():
                if any(keyword in content for keyword in keywords):
                    patterns.append(pattern)

        except Exception as e:
            logger.warning(f"Failed to detect patterns in {file_path}: {e}")

        return patterns

    def detect_antipatterns(self, file_path: Path) -> list[str]:
        """Detect anti-patterns in file."""
        antipatterns = []

        try:
            content = file_path.read_text()

            # Global state mutation
            if "global " in content:
                antipatterns.append("global_state_mutation")

            # Magic numbers
            if re.search(r"\b\d{3,}\b", content):
                antipatterns.append("magic_numbers")

            # Spaghetti code indicators
            if file_path.suffix == ".py":
                tree = ast.parse(content)

                # Check for excessive coupling
                import_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Import))
                import_from_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ImportFrom))
                total_imports = import_count + import_from_count

                if total_imports > 20:
                    antipatterns.append("excessive_coupling")

                # Check for copy-paste programming
                func_bodies = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_body = ast.unparse(node) if hasattr(ast, "unparse") else ""
                        if func_body in func_bodies and len(func_body) > 100:
                            antipatterns.append("copy_paste_programming")
                            break
                        func_bodies.append(func_body)

        except Exception as e:
            logger.warning(f"Failed to detect antipatterns in {file_path}: {e}")

        return list(set(antipatterns))


class ImprovementFinder:
    """Finds improvement opportunities in code."""

    def find_improvements(self, file_path: Path, metrics: dict[str, Any]) -> list[dict[str, Any]]:
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
                                    "suggestion": "Add docstring describing function purpose, args, and returns",
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
                                    "suggestion": "Add return type hint",
                                }
                            )

                        # Missing parameter type hints
                        for arg in node.args.args:
                            if not arg.annotation and arg.arg != "self":
                                improvements.append(
                                    {
                                        "type": "missing_param_type",
                                        "location": f"{file_path}:{node.lineno}",
                                        "function": node.name,
                                        "parameter": arg.arg,
                                        "priority": "low",
                                        "effort": "low",
                                        "impact": "type_safety",
                                        "suggestion": f"Add type hint for parameter '{arg.arg}'",
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
                                    "suggestion": "Add class docstring describing purpose and usage",
                                }
                            )

            # Check for long lines
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                if len(line) > 100:
                    improvements.append(
                        {
                            "type": "long_line",
                            "location": f"{file_path}:{i}",
                            "priority": "low",
                            "effort": "low",
                            "impact": "readability",
                            "suggestion": "Break line into multiple lines (max 100 chars)",
                        }
                    )

            # Low documentation coverage
            if metrics.get("docstring_coverage", 0) < 50:
                improvements.append(
                    {
                        "type": "low_documentation",
                        "location": str(file_path),
                        "coverage": metrics["docstring_coverage"],
                        "priority": "high",
                        "effort": "medium",
                        "impact": "maintainability",
                        "suggestion": f"Increase docstring coverage from {metrics['docstring_coverage']:.1f}% to at least 80%",
                    }
                )

        except Exception as e:
            logger.warning(f"Failed to find improvements in {file_path}: {e}")

        return improvements

    def score_improvements(self, improvements: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Score and prioritize improvements."""
        priority_scores = {"high": 3, "medium": 2, "low": 1}
        effort_scores = {"low": 3, "medium": 2, "high": 1}
        impact_scores = {
            "security": 1.0,
            "performance": 0.8,
            "maintainability": 0.6,
            "documentation": 0.5,
            "type_safety": 0.4,
            "readability": 0.3,
            "style": 0.2,
        }

        for imp in improvements:
            priority = priority_scores.get(imp.get("priority", "low"), 1)
            effort = effort_scores.get(imp.get("effort", "medium"), 2)
            impact = impact_scores.get(imp.get("impact", "readability"), 0.3)

            # Weighted score
            imp["score"] = (priority * 0.4 + effort * 0.3 + impact * 3) / 1.7

        return sorted(improvements, key=lambda x: x.get("score", 0), reverse=True)


class CodeAnalysisAgent(BaseAgent):
    """Agent for analyzing internal codebase.

    This agent focuses on internal code analysis without external references.
    It uses shared analyzers to detect patterns, smells, and improvements.
    """

    def __init__(self, name: str = "code_analysis", config: Optional[CodeAnalysisConfig] = None):
        """Initialize code analysis agent.

        Args:
            name: Agent name
            config: Analysis configuration
        """
        super().__init__(name, {"timeout": 300})
        self.config = config or CodeAnalysisConfig()
        self.analyzer = CodebaseAnalyzer()
        self.detector = PatternDetector()
        self.finder = ImprovementFinder()
        # context_store is inherited from BaseAgent

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Execute code analysis task.

        Args:
            input: Agent input with target_path

        Returns:
            Analysis results with improvements and metrics
        """
        evolution_id = None

        try:
            target_path = Path(input.payload.get("target_path", "."))
            evolution_id = input.payload.get("evolution_id") or (
                input.context.get("evolution_id") if input.context else None
            )
            focus_areas = input.payload.get("focus_areas", [])

            # Create new evolution context if not provided
            if not evolution_id:
                evolution_id = await self.context_store.create_context(
                    target_path=str(target_path), focus_areas=focus_areas
                )
                self.logger.info(f"Created new evolution context: {evolution_id}")

            # Update phase
            await self.context_store.update_phase("code_analysis", evolution_id)

            # Scan for files
            files = self.analyzer.scan_directory(
                target_path,
                max_files=self.config.max_files_to_scan,
                ignore_patterns=self.config.ignore_patterns,
                focus_patterns=self.config.focus_patterns,
            )

            # Analyze each file
            all_metrics = []
            all_smells = []
            all_patterns = []
            all_antipatterns = []
            all_improvements = []

            for file_path in files:
                # Skip large files
                if file_path.stat().st_size > self.config.max_file_size_mb * 1024 * 1024:
                    continue

                # Analyze metrics
                metrics = self.analyzer.analyze_file(file_path)
                all_metrics.append(metrics)

                # Find issues and patterns
                smells = self.analyzer.find_code_smells(file_path)
                patterns = self.detector.detect_patterns(file_path)
                antipatterns = self.detector.detect_antipatterns(file_path)
                improvements = self.finder.find_improvements(file_path, metrics)

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

            # Calculate aggregate metrics
            total_lines = sum(m["lines"] for m in all_metrics)
            avg_complexity = (
                sum(m["complexity"] for m in all_metrics) / len(all_metrics) if all_metrics else 0
            )
            avg_docstring_coverage = (
                sum(m["docstring_coverage"] for m in all_metrics) / len(all_metrics)
                if all_metrics
                else 0
            )
            avg_type_hints_coverage = (
                sum(m["type_hints_coverage"] for m in all_metrics) / len(all_metrics)
                if all_metrics
                else 0
            )

            # Prepare report
            report = {
                "summary": {
                    "files_analyzed": len(files),
                    "total_lines": total_lines,
                    "avg_complexity": round(avg_complexity, 2),
                    "avg_docstring_coverage": round(avg_docstring_coverage, 1),
                    "avg_type_hints_coverage": round(avg_type_hints_coverage, 1),
                    "improvements_found": len(filtered_improvements),
                    "code_smells": len(all_smells),
                    "patterns_detected": len(set(all_patterns)),
                    "antipatterns_found": len(set(all_antipatterns)),
                },
                "improvements": filtered_improvements[:20],  # Top 20
                "code_smells": all_smells[:10],  # Top 10
                "patterns": list(set(all_patterns)),
                "antipatterns": list(set(all_antipatterns)),
                "metrics_by_file": all_metrics[:10],  # Top 10 files
            }

            # Store in SharedContextStore
            await self.context_store.store_original_analysis(
                files_analyzed=len(files),
                metrics=report["summary"],
                issues=all_smells[:50],
                improvements=filtered_improvements[:50],
                evolution_id=evolution_id,
            )

            # Store current state for other agents
            await self.context_store.update_context(
                section="current_state",
                data={
                    "analysis_complete": True,
                    "report": report,
                    "top_issues": all_smells[:10],
                    "top_improvements": filtered_improvements[:10],
                    "detected_patterns": list(set(all_patterns)),
                    "detected_antipatterns": list(set(all_antipatterns)),
                },
                evolution_id=evolution_id,
            )

            self.logger.info(f"Stored comprehensive analysis in context {evolution_id}")

            # Create output artifact
            report_artifact = Artifact(
                kind="report", ref="code-analysis-report.json", content=report
            )

            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.OK,
                artifacts=[report_artifact],
                metrics={
                    "evolution_id": evolution_id,
                    "files_analyzed": len(files),
                    "improvements_found": len(filtered_improvements),
                    "avg_complexity": avg_complexity,
                    "avg_docstring_coverage": avg_docstring_coverage,
                },
                context={"evolution_id": evolution_id},  # Pass evolution_id to next agent
            )

        except Exception as e:
            logger.error(f"Code analysis failed: {e}")
            if evolution_id:
                await self.context_store.add_error(str(e), evolution_id)
            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.FAIL,
                error=str(e),
                context={"evolution_id": evolution_id} if evolution_id else None,
            )

    async def validate(self, output: AgentOutput) -> bool:
        """Validate analysis output.

        Args:
            output: Output to validate

        Returns:
            True if valid
        """
        if output.status != AgentStatus.OK:
            return False

        if not output.artifacts:
            return False

        # Check for report artifact
        for artifact in output.artifacts:
            if isinstance(artifact, dict):
                if artifact.get("kind") == "report":
                    return True
            elif hasattr(artifact, "kind") and artifact.kind == "report":
                return True

        return False

    def get_capabilities(self) -> dict[str, Any]:
        """Get agent capabilities.

        Returns:
            Capabilities dictionary
        """
        return {
            "name": self.name,
            "version": "2.0.0",
            "supported_intents": ["analyze", "scan", "review", "metrics"],
            "features": [
                "code_metrics",
                "complexity_analysis",
                "pattern_detection",
                "antipattern_detection",
                "code_smell_detection",
                "improvement_suggestions",
                "docstring_coverage",
                "type_hints_coverage",
            ],
            "config": {
                "max_files": self.config.max_files_to_scan,
                "deep_analysis": self.config.enable_deep_analysis,
                "security_check": self.config.check_security,
                "performance_check": self.config.check_performance,
                "maintainability_check": self.config.check_maintainability,
            },
        }
