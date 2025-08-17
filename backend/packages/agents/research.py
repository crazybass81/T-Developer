"""Research Agent - Analyzes codebase for improvements and searches external references."""

import ast
import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from packages.agents.base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent
from packages.agents.research_references import EnhancedResearchAgent as ReferenceResearcher
from packages.agents.research_references import ReferenceLibrary

logger = logging.getLogger("agents.research")


@dataclass
class ResearchConfig:
    """Configuration for research agent."""

    max_files_to_scan: int = 100
    max_file_size_mb: float = 10
    ignore_patterns: list[str] = field(
        default_factory=lambda: ["__pycache__", ".git", "node_modules", ".venv", "dist", "build"]
    )
    focus_patterns: list[str] = field(default_factory=lambda: ["*.py", "*.js", "*.ts"])
    min_improvement_score: float = 0.3
    enable_ai_analysis: bool = True
    ai_model: str = "claude-3-sonnet"
    enable_reference_search: bool = True
    save_to_library: bool = True
    reference_library_path: str = "references"


class CodebaseAnalyzer:
    """Analyzes codebase structure and metrics."""

    def scan_directory(self, path: Path) -> list[Path]:
        """Scan directory for relevant files.

        Args:
            path: Directory path to scan

        Returns:
            List of file paths
        """
        files = []
        ignore_patterns = ["__pycache__", ".git", "node_modules", ".venv"]

        for item in path.rglob("*"):
            if item.is_file():
                # Skip ignored patterns
                if any(pattern in str(item) for pattern in ignore_patterns):
                    continue
                files.append(item)

        return files

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """Analyze a single file for metrics.

        Args:
            file_path: Path to file

        Returns:
            File metrics dictionary
        """
        metrics = {
            "path": str(file_path),
            "lines": 0,
            "complexity": 0,
            "functions": 0,
            "classes": 0,
        }

        try:
            content = file_path.read_text()
            metrics["lines"] = len(content.splitlines())

            if file_path.suffix == ".py":
                tree = ast.parse(content)
                metrics["functions"] = sum(
                    1 for _ in ast.walk(tree) if isinstance(_, ast.FunctionDef)
                )
                metrics["classes"] = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef))
                metrics["complexity"] = self._calculate_complexity(tree)
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")

        return metrics

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity.

        Args:
            tree: AST tree

        Returns:
            Complexity score
        """
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def find_code_smells(self, file_path: Path) -> list[str]:
        """Find code smells in file.

        Args:
            file_path: Path to file

        Returns:
            List of detected code smells
        """
        smells = []

        try:
            content = file_path.read_text()
            lines = content.splitlines()

            # Check for long functions
            if file_path.suffix == ".py":
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Too many parameters
                        if len(node.args.args) > 5:
                            smells.append(f"Too many parameters in {node.name}")

                        # Check nesting depth
                        depth = self._get_nesting_depth(node)
                        if depth > 4:
                            smells.append(f"Too deeply nested in {node.name}")

            # Check for large files
            if len(lines) > 500:
                smells.append("File too large (>500 lines)")

            # Check for TODO/FIXME comments
            todo_count = sum(1 for line in lines if "TODO" in line or "FIXME" in line)
            if todo_count > 3:
                smells.append(f"Too many TODOs/FIXMEs ({todo_count})")

        except Exception as e:
            logger.warning(f"Failed to check smells in {file_path}: {e}")

        return smells

    def _get_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Get maximum nesting depth of a node.

        Args:
            node: AST node
            depth: Current depth

        Returns:
            Maximum depth
        """
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                child_depth = self._get_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth


class PatternDetector:
    """Detects design patterns and anti-patterns."""

    def detect_patterns(self, file_path: Path) -> list[str]:
        """Detect design patterns in file.

        Args:
            file_path: Path to file

        Returns:
            List of detected patterns
        """
        patterns = []

        try:
            content = file_path.read_text().lower()

            # Simple pattern detection based on keywords
            pattern_keywords = {
                "singleton": ["_instance", "singleton", "__new__"],
                "factory": ["factory", "create", "build"],
                "observer": ["observer", "notify", "subscribe", "attach"],
                "strategy": ["strategy", "algorithm", "context"],
                "decorator": ["decorator", "wrapper", "functools.wraps"],
            }

            for pattern, keywords in pattern_keywords.items():
                if any(keyword in content for keyword in keywords):
                    patterns.append(pattern)

        except Exception as e:
            logger.warning(f"Failed to detect patterns in {file_path}: {e}")

        return patterns

    def detect_antipatterns(self, file_path: Path) -> list[str]:
        """Detect anti-patterns in file.

        Args:
            file_path: Path to file

        Returns:
            List of detected anti-patterns
        """
        antipatterns = []

        try:
            content = file_path.read_text()

            # Check for God Object
            if file_path.suffix == ".py":
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                        # Check for too many methods OR too many attributes
                        attr_count = (
                            sum(
                                1
                                for n in node.body[0].body
                                if isinstance(node.body[0], ast.FunctionDef)
                                and node.body[0].name == "__init__"
                                and isinstance(n, ast.Assign)
                            )
                            if node.body
                            else 0
                        )
                        if method_count > 20 or (method_count > 3 and attr_count > 4):
                            antipatterns.append(f"God object: {node.name}")

            # Check for global state
            if "global " in content:
                antipatterns.append("Global state mutation")

            # Check for magic numbers
            if re.search(r"\b\d{3,}\b", content):
                antipatterns.append("Magic numbers")

        except Exception as e:
            logger.warning(f"Failed to detect antipatterns in {file_path}: {e}")

        return antipatterns


class ImprovementFinder:
    """Finds improvement opportunities."""

    def find_refactoring_opportunities(self, file_path: Path) -> list[dict[str, Any]]:
        """Find refactoring opportunities in file.

        Args:
            file_path: Path to file

        Returns:
            List of refactoring opportunities
        """
        opportunities = []

        try:
            content = file_path.read_text()

            if file_path.suffix == ".py":
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    # Check for missing type hints
                    if isinstance(node, ast.FunctionDef):
                        if not node.returns:
                            opportunities.append(
                                {
                                    "type": "missing_type_hints",
                                    "location": f"{file_path}:{node.lineno}",
                                    "function": node.name,
                                    "suggestion": "Add return type hint",
                                }
                            )

                        # Check for missing docstrings
                        if not ast.get_docstring(node):
                            opportunities.append(
                                {
                                    "type": "missing_docstring",
                                    "location": f"{file_path}:{node.lineno}",
                                    "function": node.name,
                                    "suggestion": "Add docstring",
                                }
                            )

            # Check for long lines
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                if len(line) > 100:
                    opportunities.append(
                        {
                            "type": "long_line",
                            "location": f"{file_path}:{i}",
                            "suggestion": "Break into multiple lines",
                        }
                    )

        except Exception as e:
            logger.warning(f"Failed to find refactoring in {file_path}: {e}")

        return opportunities

    def score_improvements(self, improvements: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Score and rank improvements.

        Args:
            improvements: List of improvements

        Returns:
            Sorted list of scored improvements
        """
        # Scoring weights
        impact_scores = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2}

        effort_scores = {"low": 1.0, "medium": 0.5, "high": 0.2}

        type_scores = {
            "security": 1.0,
            "performance": 0.8,
            "maintainability": 0.6,
            "readability": 0.4,
            "style": 0.2,
        }

        for improvement in improvements:
            impact = improvement.get("impact", "medium")
            effort = improvement.get("effort", "medium")
            imp_type = improvement.get("type", "readability")

            score = (
                impact_scores.get(impact, 0.5)
                * effort_scores.get(effort, 0.5)
                * type_scores.get(imp_type, 0.4)
            )
            improvement["score"] = score

        return sorted(improvements, key=lambda x: x["score"], reverse=True)


class ResearchAgent(BaseAgent):
    """Agent that researches codebase for improvements and external references."""

    def __init__(self, name: str, config: Optional[ResearchConfig] = None):
        """Initialize research agent.

        Args:
            name: Agent name
            config: Research configuration
        """
        super().__init__(name, {"timeout": 600})
        self.config = config or ResearchConfig()
        self.analyzer = CodebaseAnalyzer()
        self.detector = PatternDetector()
        self.finder = ImprovementFinder()
        self.reference_researcher = ReferenceResearcher()
        self.library = ReferenceLibrary(self.config.reference_library_path)

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Execute research task.

        Args:
            input: Agent input

        Returns:
            Research results
        """
        try:
            target_path = Path(input.payload.get("target_path", "."))

            # Scan codebase
            files = self.analyzer.scan_directory(target_path)
            files = files[: self.config.max_files_to_scan]

            # Analyze files
            all_improvements = []
            all_patterns = []
            all_antipatterns = []
            all_smells = []

            for file in files:
                # Skip large files
                if file.stat().st_size > self.config.max_file_size_mb * 1024 * 1024:
                    continue

                # Analyze metrics
                metrics = self.analyzer.analyze_file(file)

                # Find issues
                smells = self.analyzer.find_code_smells(file)
                patterns = self.detector.detect_patterns(file)
                antipatterns = self.detector.detect_antipatterns(file)
                improvements = self.finder.find_refactoring_opportunities(file)

                all_smells.extend(smells)
                all_patterns.extend(patterns)
                all_antipatterns.extend(antipatterns)
                all_improvements.extend(improvements)

            # Score improvements
            scored_improvements = self.finder.score_improvements(all_improvements)

            # Filter by minimum score
            filtered = [
                imp
                for imp in scored_improvements
                if imp.get("score", 0) >= self.config.min_improvement_score
            ]

            # Use AI for deeper analysis if enabled
            if self.config.enable_ai_analysis and input.payload.get("use_ai"):
                ai_insights = await self._ai_analysis(
                    target_path, filtered[:10]  # Top 10 improvements
                )
                if ai_insights:
                    filtered = ai_insights.get("improvements", filtered)

            # Search for external references if enabled
            external_references = {}
            if self.config.enable_reference_search:
                problem = input.payload.get("problem", "")
                requirements = input.payload.get("requirements", [])
                constraints = input.payload.get("constraints", {})

                if problem:
                    external_references = await self.reference_researcher.research_solution(
                        problem=problem, requirements=requirements, constraints=constraints
                    )

                    # Save to library if configured
                    if self.config.save_to_library and external_references:
                        category = input.payload.get("category", "general")
                        await self.reference_researcher.save_research(external_references, category)

            # Create comprehensive report
            report = {
                "summary": {
                    "files_analyzed": len(files),
                    "improvements_found": len(filtered),
                    "patterns_detected": len(set(all_patterns)),
                    "antipatterns_found": len(all_antipatterns),
                    "code_smells": len(all_smells),
                    "external_references_found": len(
                        external_references.get("external_references", {}).get("github", [])
                    ),
                },
                "codebase_analysis": {
                    "improvements": filtered[:20],  # Top 20
                    "patterns": list(set(all_patterns)),
                    "antipatterns": all_antipatterns[:10],
                    "code_smells": all_smells[:10],
                },
                "external_references": external_references,
                "recommendations": external_references.get("recommendations", {})
                if external_references
                else {},
            }

            # Store external research results in context store
            if self.config.enable_reference_search and external_references:
                best_practices = external_references.get("best_practices", [])
                references = external_references.get("external_references", {})
                patterns = external_references.get("patterns", [])

                await self.context_store.store_external_research(
                    best_practices=best_practices,
                    references=[references] if references else [],
                    patterns=patterns,
                    evolution_id=input.context.get("evolution_id") if input.context else None,
                )
                self.logger.info("Stored external research results in context store")

            # Create output
            report_artifact = Artifact(kind="report", ref="research-report.json", content=report)

            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.OK,
                artifacts=[report_artifact],
                metrics={
                    "files_analyzed": len(files),
                    "improvements_found": len(filtered),
                    "execution_time": 0,  # Would be tracked
                },
            )

        except Exception as e:
            logger.error(f"Research execution failed: {e}")
            return AgentOutput(task_id=input.task_id, status=AgentStatus.FAIL, error=str(e))

    async def _ai_analysis(
        self, target_path: Path, improvements: list[dict[str, Any]]
    ) -> Optional[dict[str, Any]]:
        """Use AI for deeper analysis.

        Args:
            target_path: Path being analyzed
            improvements: Initial improvements found

        Returns:
            AI insights
        """
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            prompt = f"""Analyze this codebase research:

Target: {target_path}
Initial improvements found: {json.dumps(improvements, indent=2)}

Please provide:
1. Additional improvement suggestions
2. Patterns you notice
3. Priority ranking
4. Estimated impact score (0-1)

Return as JSON with keys: improvements, patterns, score"""

            response = await client.messages.create(
                model=self.config.ai_model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            return json.loads(response.content[0].text)

        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            return None

    async def validate(self, output: AgentOutput) -> bool:
        """Validate research output.

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
        has_report = False
        for a in output.artifacts:
            if isinstance(a, dict):
                if a.get("kind") == "report":
                    has_report = True
                    break
            elif hasattr(a, "kind") and a.kind == "report":
                has_report = True
                break

        return has_report

    def get_capabilities(self) -> dict[str, Any]:
        """Get agent capabilities.

        Returns:
            Capabilities dictionary
        """
        return {
            "name": self.name,
            "version": "2.0.0",
            "supported_intents": ["research", "analyze", "scan", "reference", "trend"],
            "features": [
                "code_analysis",
                "pattern_detection",
                "improvements",
                "refactoring",
                "code_smells",
                "external_references",
                "technology_trends",
                "solution_recommendations",
                "knowledge_library",
            ],
            "max_files": self.config.max_files_to_scan,
            "ai_enabled": self.config.enable_ai_analysis,
            "reference_search_enabled": self.config.enable_reference_search,
            "library_enabled": self.config.save_to_library,
        }
