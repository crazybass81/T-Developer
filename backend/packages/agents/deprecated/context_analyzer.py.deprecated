"""
Context Analyzer Agent for T-Developer v2.

This agent specializes in analyzing and understanding context to provide
better decision-making and code generation capabilities.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.core.shared_context import SharedContextStore, TaskContext
from backend.packages.agents.base import BaseAgent
from backend.packages.learning.memory_curator import Memory, MemoryCurator

logger = logging.getLogger(__name__)


@dataclass
class ContextAnalysis:
    """Result of context analysis."""

    analysis_id: str
    context_type: str
    relevance_score: float
    key_elements: list[str]
    dependencies: list[str]
    risks: list[str]
    recommendations: list[str]
    patterns_detected: list[str]
    metadata: dict[str, Any]


class ContextAnalyzerAgent(BaseAgent):
    """
    Agent specialized in analyzing context for better understanding.

    Capabilities:
    - Analyze code context and dependencies
    - Identify patterns and anti-patterns
    - Assess risks and provide recommendations
    - Understand task requirements in context
    - Bridge between Claude Code and T-Developer context
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize the Context Analyzer Agent."""
        super().__init__(config)
        self.context_store = SharedContextStore()
        self.memory_curator = MemoryCurator()
        self.analysis_cache: dict[str, ContextAnalysis] = {}
        self.pattern_library = self._load_pattern_library()

    async def initialize(self) -> None:
        """Initialize the agent and its subsystems."""
        await super().initialize()
        # Context store and memory curator initialize themselves
        await super().initialize()
        logger.info("Context Analyzer Agent initialized")

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Execute context analysis task.

        Args:
            task: Task containing:
                - action: Type of analysis (analyze_code, analyze_task, analyze_evolution)
                - target: What to analyze
                - depth: Analysis depth (shallow, normal, deep)
                - include_memory: Whether to include memory context

        Returns:
            Analysis results with context insights
        """
        action = task.get("action", "analyze_code")
        target = task.get("target", "")
        depth = task.get("depth", "normal")
        include_memory = task.get("include_memory", True)

        logger.info(f"Executing context analysis: {action} on {target}")

        try:
            if action == "analyze_code":
                result = await self._analyze_code_context(target, depth, include_memory)
            elif action == "analyze_task":
                result = await self._analyze_task_context(task, depth, include_memory)
            elif action == "analyze_evolution":
                result = await self._analyze_evolution_context(task, include_memory)
            elif action == "analyze_dependencies":
                result = await self._analyze_dependencies(target, depth)
            elif action == "find_patterns":
                result = await self._find_patterns(target, include_memory)
            elif action == "assess_risk":
                result = await self._assess_risk(task)
            elif action == "generate_recommendations":
                result = await self._generate_recommendations(task, include_memory)
            else:
                result = {"error": f"Unknown action: {action}"}

            # Store in memory if successful
            if "error" not in result and include_memory:
                await self._store_analysis_in_memory(action, target, result)

            return result

        except Exception as e:
            logger.error(f"Context analysis failed: {e}")
            return {"error": str(e), "action": action, "target": target}

    async def _analyze_code_context(
        self, file_path: str, depth: str, include_memory: bool
    ) -> dict[str, Any]:
        """Analyze code file context."""
        analysis = ContextAnalysis(
            analysis_id=f"code_{datetime.now().timestamp()}",
            context_type="code",
            relevance_score=0.0,
            key_elements=[],
            dependencies=[],
            risks=[],
            recommendations=[],
            patterns_detected=[],
            metadata={"file": file_path, "depth": depth},
        )

        # Get file context - simplified for now
        file_context = {"file": file_path, "related_files": [], "recent_changes": []}

        # Analyze file content
        if Path(file_path).exists():
            with open(file_path) as f:
                content = f.read()

            # Extract key elements
            analysis.key_elements = self._extract_key_elements(content)

            # Find dependencies
            analysis.dependencies = self._extract_dependencies(content)

            # Detect patterns
            analysis.patterns_detected = self._detect_patterns(content)

            # Assess code quality risks
            analysis.risks = self._assess_code_risks(content)

            # Generate recommendations
            analysis.recommendations = self._generate_code_recommendations(
                content, analysis.patterns_detected, analysis.risks
            )

            # Calculate relevance score
            analysis.relevance_score = self._calculate_relevance(
                file_context, analysis.key_elements
            )

        # Include memory context if requested
        if include_memory:
            memory_context = await self._get_memory_context(file_path)
            analysis.metadata["memory_context"] = memory_context

        return {"analysis": analysis.__dict__, "file_context": file_context, "success": True}

    async def _analyze_task_context(
        self, task: dict[str, Any], depth: str, include_memory: bool
    ) -> dict[str, Any]:
        """Analyze task context for better understanding."""
        task_id = task.get("task_id", f"task_{datetime.now().timestamp()}")

        # Create task context
        task_context = TaskContext(
            task_id=task_id,
            task_type=task.get("type", "unknown"),
            description=task.get("description", ""),
            target_files=task.get("files", []),
            requirements=task.get("requirements", []),
        )

        analysis = ContextAnalysis(
            analysis_id=f"task_{datetime.now().timestamp()}",
            context_type="task",
            relevance_score=0.0,
            key_elements=[],
            dependencies=[],
            risks=[],
            recommendations=[],
            patterns_detected=[],
            metadata={"task_id": task_id, "depth": depth},
        )

        # Analyze task requirements
        requirements = task.get("requirements", [])
        for req in requirements:
            elements = self._extract_requirements_elements(req)
            analysis.key_elements.extend(elements)

        # Find relevant patterns from memory
        if include_memory:
            # Find patterns in memory
            patterns = []  # Simplified - MemoryCurator doesn't have find_patterns
            analysis.patterns_detected = [p.pattern_id for p in patterns[:5]]

            # Get recommendations from successful patterns
            for pattern in patterns[:3]:
                if pattern.success_rate > 0.7:
                    analysis.recommendations.append(
                        f"Apply pattern {pattern.description} (success rate: {pattern.success_rate:.1%})"
                    )

        # Assess task complexity and risks
        complexity = self._assess_task_complexity(task)
        if complexity > 0.7:
            analysis.risks.append("High complexity task - consider breaking down")

        # Get project context
        project_context = {"project": {"patterns": {}}}  # Simplified
        analysis.relevance_score = self._calculate_task_relevance(task, project_context)

        return {
            "analysis": analysis.__dict__,
            "task_context": task_context.__dict__ if task_context else {},
            "complexity": complexity,
            "success": True,
        }

    async def _analyze_evolution_context(
        self, task: dict[str, Any], include_memory: bool
    ) -> dict[str, Any]:
        """Analyze evolution context for learning."""
        evolution_id = task.get("evolution_id", f"evo_{datetime.now().timestamp()}")

        analysis = ContextAnalysis(
            analysis_id=f"evolution_{datetime.now().timestamp()}",
            context_type="evolution",
            relevance_score=0.0,
            key_elements=[],
            dependencies=[],
            risks=[],
            recommendations=[],
            patterns_detected=[],
            metadata={"evolution_id": evolution_id},
        )

        # Get evolution context from store
        evo_ctx = await self.context_store.get_context(evolution_id)
        evolution_context = evo_ctx.to_dict() if evo_ctx else {}

        # Analyze past evolutions for patterns
        if include_memory:
            # Search for evolution experiences in memory
            memories = await self.memory_curator.search_memories({"type": "evolution"}, limit=20)
            experiences = []  # Convert memories to experiences

            # Extract successful patterns
            for exp in experiences:
                if exp.reward > 0.7:
                    analysis.patterns_detected.append(
                        f"Successful evolution pattern from {exp.experience_id}"
                    )

            # Generate recommendations based on past successes
            if experiences:
                avg_reward = sum(e.reward for e in experiences) / len(experiences)
                if avg_reward > 0.6:
                    analysis.recommendations.append(
                        "Previous evolutions show positive trend - continue current approach"
                    )
                else:
                    analysis.recommendations.append(
                        "Consider adjusting evolution strategy based on past results"
                    )

        # Assess evolution risks
        cycle_count = task.get("cycle", 0)
        if cycle_count > 50:
            analysis.risks.append("High cycle count - check for infinite loops")

        metrics_delta = task.get("metrics_delta", {})
        if any(v < 0 for v in metrics_delta.values()):
            analysis.risks.append("Negative metric changes detected")

        return {
            "analysis": analysis.__dict__,
            "evolution_context": evolution_context,
            "success": True,
        }

    async def _analyze_dependencies(self, target: str, depth: str) -> dict[str, Any]:
        """Analyze dependencies for a target."""
        dependencies = {"direct": [], "transitive": [], "circular": [], "missing": []}

        if Path(target).exists() and target.endswith(".py"):
            with open(target) as f:
                content = f.read()

            # Extract imports
            import_pattern = re.compile(r"^\s*(?:from|import)\s+([^\s]+)", re.MULTILINE)
            imports = import_pattern.findall(content)

            dependencies["direct"] = imports

            # Check for circular dependencies (simplified)
            for imp in imports:
                if imp.startswith("backend.packages"):
                    # Check if imported module imports current module
                    module_path = imp.replace(".", "/") + ".py"
                    if Path(module_path).exists():
                        with open(module_path) as f:
                            if Path(target).stem in f.read():
                                dependencies["circular"].append(imp)

            # Deep analysis if requested
            if depth == "deep":
                for imp in imports[:10]:  # Limit for performance
                    sub_deps = await self._get_transitive_dependencies(imp)
                    dependencies["transitive"].extend(sub_deps)

        return {
            "target": target,
            "dependencies": dependencies,
            "dependency_count": len(dependencies["direct"]),
            "has_circular": len(dependencies["circular"]) > 0,
            "success": True,
        }

    async def _find_patterns(self, target: str, include_memory: bool) -> dict[str, Any]:
        """Find patterns in code or behavior."""
        patterns_found = []

        # Code patterns
        if Path(target).exists() and target.endswith(".py"):
            with open(target) as f:
                content = f.read()

            # Check against pattern library
            for pattern_name, pattern_regex in self.pattern_library.items():
                if re.search(pattern_regex, content):
                    patterns_found.append(
                        {"name": pattern_name, "type": "code", "location": target}
                    )

        # Memory patterns
        if include_memory:
            # Find patterns in memory
            memory_patterns = []  # Simplified
            for pattern in memory_patterns:
                patterns_found.append(
                    {
                        "name": pattern.description,
                        "type": "learned",
                        "success_rate": pattern.success_rate,
                        "usage_count": pattern.usage_count,
                    }
                )

        return {
            "target": target,
            "patterns": patterns_found,
            "pattern_count": len(patterns_found),
            "success": True,
        }

    async def _assess_risk(self, task: dict[str, Any]) -> dict[str, Any]:
        """Assess risks in the given context."""
        risks = {"high": [], "medium": [], "low": []}

        target = task.get("target", "")

        # Check for security risks
        if Path(target).exists() and target.endswith(".py"):
            with open(target) as f:
                content = f.read()

            # High risk patterns
            if "eval(" in content or "exec(" in content:
                risks["high"].append("Dynamic code execution detected")

            if re.search(r'(api_key|secret|password)\s*=\s*["\']', content, re.IGNORECASE):
                risks["high"].append("Potential hardcoded secrets")

            # Medium risk patterns
            if "pickle.loads" in content:
                risks["medium"].append("Pickle deserialization - potential security risk")

            if "try:" not in content and "except" in content:
                risks["medium"].append("Exception handling might be incomplete")

            # Low risk patterns
            if "logger" not in content and "logging" not in content:
                risks["low"].append("No logging detected")

        # Task-specific risks
        if task.get("type") == "evolution":
            if task.get("cycle", 0) > 100:
                risks["high"].append("Evolution cycle count very high")

        risk_score = len(risks["high"]) * 1.0 + len(risks["medium"]) * 0.5 + len(risks["low"]) * 0.2

        return {
            "risks": risks,
            "risk_score": min(1.0, risk_score / 5),
            "total_risks": sum(len(r) for r in risks.values()),
            "success": True,
        }

    async def _generate_recommendations(
        self, task: dict[str, Any], include_memory: bool
    ) -> dict[str, Any]:
        """Generate contextual recommendations."""
        recommendations = {"immediate": [], "short_term": [], "long_term": []}

        # Get current context
        context = {"project": {"patterns": {}}}  # Simplified

        # Get insights from memory
        if include_memory:
            # Get successful patterns from memory
            patterns = []  # Simplified
            for pattern in patterns[:3]:
                if pattern.success_rate > 0.8:
                    recommendations["immediate"].append(
                        f"Apply proven pattern: {pattern.description}"
                    )

            # Get similar past experiences from memory
            memories = await self.memory_curator.search_memories(
                {"type": task.get("type")}, limit=5
            )
            experiences = []  # Convert memories to experiences

            if experiences:
                recommendations["short_term"].append(
                    "Review successful past implementations for guidance"
                )

        # Project-specific recommendations
        if context.get("project", {}).get("patterns"):
            recommendations["immediate"].append(
                "Follow established project patterns for consistency"
            )

        # Evolution recommendations
        if task.get("type") == "evolution":
            recommendations["long_term"].append(
                "Continuously monitor metrics to ensure positive evolution"
            )

        return {
            "recommendations": recommendations,
            "total_recommendations": sum(len(r) for r in recommendations.values()),
            "context_based": True,
            "success": True,
        }

    def _extract_key_elements(self, content: str) -> list[str]:
        """Extract key elements from code."""
        elements = []

        # Classes
        class_pattern = re.compile(r"class\s+(\w+)")
        elements.extend(f"class:{c}" for c in class_pattern.findall(content))

        # Functions
        func_pattern = re.compile(r"def\s+(\w+)")
        elements.extend(f"function:{f}" for f in func_pattern.findall(content))

        # Async functions
        async_pattern = re.compile(r"async\s+def\s+(\w+)")
        elements.extend(f"async_function:{f}" for f in async_pattern.findall(content))

        return elements

    def _extract_dependencies(self, content: str) -> list[str]:
        """Extract dependencies from code."""
        dependencies = []

        # Import statements
        import_pattern = re.compile(r"^\s*import\s+([^\s]+)", re.MULTILINE)
        dependencies.extend(import_pattern.findall(content))

        # From imports
        from_pattern = re.compile(r"^\s*from\s+([^\s]+)\s+import", re.MULTILINE)
        dependencies.extend(from_pattern.findall(content))

        return list(set(dependencies))

    def _detect_patterns(self, content: str) -> list[str]:
        """Detect code patterns."""
        patterns = []

        # Common patterns
        if "class.*BaseAgent" in content:
            patterns.append("agent_inheritance")

        if "@dataclass" in content:
            patterns.append("dataclass_usage")

        if "async def" in content:
            patterns.append("async_programming")

        if "try:" in content and "except" in content:
            patterns.append("exception_handling")

        if "logger" in content or "logging" in content:
            patterns.append("logging_implemented")

        return patterns

    def _assess_code_risks(self, content: str) -> list[str]:
        """Assess risks in code."""
        risks = []

        # Security risks
        if "eval(" in content or "exec(" in content:
            risks.append("Dynamic code execution risk")

        if re.search(r"open\([^,)]*\)", content):
            risks.append("File operations without explicit mode")

        # Quality risks
        if content.count("# TODO") > 5:
            risks.append("Many TODOs indicate incomplete implementation")

        if "test" not in content and len(content) > 1000:
            risks.append("Large file without apparent tests")

        return risks

    def _generate_code_recommendations(
        self, content: str, patterns: list[str], risks: list[str]
    ) -> list[str]:
        """Generate code-specific recommendations."""
        recommendations = []

        # Based on missing patterns
        if "exception_handling" not in patterns and len(content) > 500:
            recommendations.append("Add exception handling for robustness")

        if "logging_implemented" not in patterns:
            recommendations.append("Add logging for better debugging")

        # Based on risks
        if "Dynamic code execution risk" in risks:
            recommendations.append("Replace eval/exec with safer alternatives")

        # General improvements
        if content.count("\n") > 200 and "class" not in content:
            recommendations.append("Consider refactoring into classes for better organization")

        return recommendations

    def _calculate_relevance(self, file_context: dict[str, Any], key_elements: list[str]) -> float:
        """Calculate relevance score."""
        score = 0.5  # Base score

        # Increase score based on related files
        if file_context.get("related_files"):
            score += min(0.2, len(file_context["related_files"]) * 0.05)

        # Increase score based on recent changes
        if file_context.get("recent_changes"):
            score += min(0.2, len(file_context["recent_changes"]) * 0.1)

        # Increase score based on key elements
        if len(key_elements) > 10:
            score += 0.1

        return min(1.0, score)

    def _extract_requirements_elements(self, requirement: str) -> list[str]:
        """Extract key elements from requirement text."""
        elements = []

        # Technical terms
        tech_terms = ["api", "database", "cache", "queue", "service", "agent", "model"]
        for term in tech_terms:
            if term in requirement.lower():
                elements.append(f"tech:{term}")

        # Actions
        action_terms = ["create", "update", "delete", "process", "analyze", "generate"]
        for term in action_terms:
            if term in requirement.lower():
                elements.append(f"action:{term}")

        return elements

    def _assess_task_complexity(self, task: dict[str, Any]) -> float:
        """Assess task complexity."""
        complexity = 0.3  # Base complexity

        # File count
        files = task.get("files", [])
        complexity += min(0.3, len(files) * 0.05)

        # Requirement count
        requirements = task.get("requirements", [])
        complexity += min(0.2, len(requirements) * 0.04)

        # Task type complexity
        complex_types = ["evolution", "refactor", "architecture"]
        if task.get("type") in complex_types:
            complexity += 0.2

        return min(1.0, complexity)

    def _calculate_task_relevance(
        self, task: dict[str, Any], project_context: dict[str, Any]
    ) -> float:
        """Calculate task relevance to project."""
        relevance = 0.5  # Base relevance

        # Check if task aligns with project patterns
        if project_context.get("project", {}).get("patterns"):
            task_desc = task.get("description", "").lower()
            for pattern in project_context["project"]["patterns"].values():
                if str(pattern).lower() in task_desc:
                    relevance += 0.1

        return min(1.0, relevance)

    async def _get_transitive_dependencies(self, module: str) -> list[str]:
        """Get transitive dependencies of a module."""
        # Simplified implementation
        return []

    def _load_pattern_library(self) -> dict[str, str]:
        """Load pattern detection library."""
        return {
            "singleton": r"class\s+\w+.*:\s*_instance\s*=\s*None",
            "factory": r"class\s+\w*Factory",
            "observer": r"class\s+\w*Observer",
            "strategy": r"class\s+\w*Strategy",
            "decorator": r"@\w+",
            "context_manager": r"__enter__.*__exit__",
            "generator": r"\byield\b",
            "comprehension": r"\[.*for.*in.*\]",
            "lambda": r"lambda\s+\w+:",
            "type_hints": r":\s*(?:str|int|float|bool|List|Dict|Optional)",
        }

    async def _get_memory_context(self, target: str) -> dict[str, Any]:
        """Get relevant memory context."""
        # Get memories related to target
        memories = await self.memory_curator.search_memories({"concept": target}, limit=3)
        semantic = [(m.content.get("concept", ""), m) for m in memories]

        # Working memory simplified
        working = {}

        return {
            "semantic_memories": [
                {"concept": concept, "importance": mem.importance} for concept, mem in semantic
            ],
            "working_memory_keys": list(working.keys()),
        }

    async def _store_analysis_in_memory(
        self, action: str, target: str, result: dict[str, Any]
    ) -> None:
        """Store analysis results in memory."""
        # Store analysis in memory
        memory = Memory(
            memory_id=f"{action}_{target}_{datetime.now().timestamp()}",
            type="analysis",
            content={"concept": f"{action}:{target}", "result": result},
            timestamp=datetime.now(),
            importance=0.6,
        )
        await self.memory_curator.store_memory(memory)

        logger.debug(f"Stored analysis in memory: {action}:{target}")
