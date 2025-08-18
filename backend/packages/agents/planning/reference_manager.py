"""Reference Manager for Planning Agents.

Manages references from analysis/research agents to inform planning decisions.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger("agents.planning.references")


@dataclass
class Reference:
    """A reference from analysis or external research."""

    source: str  # "code_analysis", "external_research", "best_practices"
    relevance_score: float
    content: dict[str, Any]
    applicable_to: list[str]  # ["generation", "refactor", "migration", "evolution"]

    def is_applicable_to(self, planner_type: str) -> bool:
        """Check if reference is applicable to a planner type."""
        return planner_type in self.applicable_to


class ReferenceManager:
    """Manages references for planning decisions."""

    def __init__(self):
        """Initialize reference manager."""
        self.references: list[Reference] = []

    async def collect_references(
        self,
        analysis_results: Optional[dict[str, Any]] = None,
        research_results: Optional[dict[str, Any]] = None,
    ) -> list[Reference]:
        """Collect references from various sources.

        Args:
            analysis_results: Results from code analysis agents
            research_results: Results from external research agents

        Returns:
            List of applicable references
        """
        references = []

        # Process code analysis results
        if analysis_results:
            references.extend(await self._process_analysis_results(analysis_results))

        # Process external research results
        if research_results:
            references.extend(await self._process_research_results(research_results))

        # Sort by relevance
        references.sort(key=lambda r: r.relevance_score, reverse=True)

        self.references = references
        return references

    async def _process_analysis_results(self, analysis_results: dict[str, Any]) -> list[Reference]:
        """Process code analysis results into references."""
        references = []

        # Extract patterns from code analysis
        if "patterns" in analysis_results:
            for pattern in analysis_results["patterns"]:
                ref = Reference(
                    source="code_analysis",
                    relevance_score=pattern.get("frequency", 0.5),
                    content={
                        "pattern": pattern["name"],
                        "description": pattern.get("description", ""),
                        "examples": pattern.get("examples", []),
                        "recommendations": pattern.get("recommendations", []),
                    },
                    applicable_to=["refactor", "evolution"],
                )
                references.append(ref)

        # Extract improvement suggestions
        if "improvements" in analysis_results:
            for improvement in analysis_results["improvements"]:
                ref = Reference(
                    source="code_analysis",
                    relevance_score=improvement.get("priority", 0.5),
                    content={
                        "type": improvement["type"],
                        "location": improvement.get("location", ""),
                        "suggestion": improvement.get("suggestion", ""),
                        "impact": improvement.get("impact", "medium"),
                    },
                    applicable_to=["refactor", "migration"],
                )
                references.append(ref)

        # Extract architecture insights
        if "architecture" in analysis_results:
            arch = analysis_results["architecture"]
            ref = Reference(
                source="code_analysis",
                relevance_score=0.8,
                content={
                    "current_architecture": arch.get("type", "unknown"),
                    "components": arch.get("components", []),
                    "dependencies": arch.get("dependencies", {}),
                    "tech_stack": arch.get("tech_stack", {}),
                },
                applicable_to=["generation", "migration", "evolution"],
            )
            references.append(ref)

        return references

    async def _process_research_results(self, research_results: dict[str, Any]) -> list[Reference]:
        """Process external research results into references."""
        references = []

        # Extract best practices
        if "best_practices" in research_results:
            for practice in research_results["best_practices"]:
                ref = Reference(
                    source="best_practices",
                    relevance_score=practice.get("popularity", 0.7),
                    content={
                        "practice": practice["name"],
                        "description": practice.get("description", ""),
                        "benefits": practice.get("benefits", []),
                        "implementation": practice.get("implementation", ""),
                    },
                    applicable_to=["generation", "refactor", "evolution"],
                )
                references.append(ref)

        # Extract similar projects
        if "similar_projects" in research_results:
            for project in research_results["similar_projects"]:
                ref = Reference(
                    source="external_research",
                    relevance_score=project.get("similarity", 0.6),
                    content={
                        "project_name": project["name"],
                        "architecture": project.get("architecture", ""),
                        "tech_stack": project.get("tech_stack", {}),
                        "lessons_learned": project.get("lessons_learned", []),
                    },
                    applicable_to=["generation", "migration"],
                )
                references.append(ref)

        # Extract migration patterns
        if "migration_patterns" in research_results:
            for pattern in research_results["migration_patterns"]:
                ref = Reference(
                    source="external_research",
                    relevance_score=pattern.get("success_rate", 0.7),
                    content={
                        "pattern_name": pattern["name"],
                        "from_stack": pattern.get("from", {}),
                        "to_stack": pattern.get("to", {}),
                        "strategy": pattern.get("strategy", ""),
                        "duration": pattern.get("average_duration", "unknown"),
                    },
                    applicable_to=["migration"],
                )
                references.append(ref)

        # Extract technology trends
        if "technology_trends" in research_results:
            for trend in research_results["technology_trends"]:
                ref = Reference(
                    source="external_research",
                    relevance_score=trend.get("adoption_rate", 0.5),
                    content={
                        "technology": trend["name"],
                        "category": trend.get("category", ""),
                        "maturity": trend.get("maturity", "emerging"),
                        "use_cases": trend.get("use_cases", []),
                    },
                    applicable_to=["generation", "evolution"],
                )
                references.append(ref)

        return references

    def get_references_for_planner(
        self, planner_type: str, max_references: int = 5
    ) -> list[Reference]:
        """Get relevant references for a specific planner type.

        Args:
            planner_type: Type of planner (generation, refactor, migration, evolution)
            max_references: Maximum number of references to return

        Returns:
            List of relevant references
        """
        applicable_refs = [ref for ref in self.references if ref.is_applicable_to(planner_type)]

        return applicable_refs[:max_references]

    def format_references_for_prompt(self, references: list[Reference]) -> str:
        """Format references for inclusion in AI prompts.

        Args:
            references: List of references to format

        Returns:
            Formatted string for prompt inclusion
        """
        if not references:
            return "No relevant references available."

        formatted = "## Relevant References:\n\n"

        for i, ref in enumerate(references, 1):
            formatted += (
                f"### Reference {i} (Source: {ref.source}, Relevance: {ref.relevance_score:.2f})\n"
            )
            formatted += json.dumps(ref.content, indent=2)
            formatted += "\n\n"

        return formatted

    def extract_patterns(self, references: list[Reference]) -> dict[str, list[str]]:
        """Extract common patterns from references.

        Args:
            references: List of references

        Returns:
            Dictionary of pattern categories and patterns
        """
        patterns = {
            "architectures": [],
            "technologies": [],
            "best_practices": [],
            "anti_patterns": [],
        }

        for ref in references:
            content = ref.content

            # Extract architectures
            if "architecture" in content:
                arch = content["architecture"]
                if arch and arch not in patterns["architectures"]:
                    patterns["architectures"].append(arch)

            # Extract technologies
            if "tech_stack" in content:
                for tech in content["tech_stack"].values():
                    if tech and tech not in patterns["technologies"]:
                        patterns["technologies"].append(tech)

            # Extract best practices
            if "practice" in content:
                practice = content["practice"]
                if practice and practice not in patterns["best_practices"]:
                    patterns["best_practices"].append(practice)

            # Extract anti-patterns
            if "anti_pattern" in content:
                anti = content["anti_pattern"]
                if anti and anti not in patterns["anti_patterns"]:
                    patterns["anti_patterns"].append(anti)

        return patterns

    def calculate_confidence_score(
        self, plan: dict[str, Any], references: list[Reference]
    ) -> float:
        """Calculate confidence score for a plan based on references.

        Args:
            plan: The generated plan
            references: Supporting references

        Returns:
            Confidence score between 0 and 1
        """
        if not references:
            return 0.5  # Neutral confidence without references

        confidence = 0.0
        weights = 0.0

        for ref in references:
            # Weight by relevance score
            weight = ref.relevance_score

            # Check alignment with reference
            alignment = self._calculate_alignment(plan, ref.content)

            confidence += alignment * weight
            weights += weight

        return confidence / weights if weights > 0 else 0.5

    def _calculate_alignment(
        self, plan: dict[str, Any], reference_content: dict[str, Any]
    ) -> float:
        """Calculate alignment between plan and reference."""
        alignment_score = 0.5  # Base score

        # Check technology alignment
        if "tech_stack" in reference_content and "technology_decisions" in plan:
            plan_tech = set(plan["technology_decisions"].values())
            ref_tech = set(reference_content["tech_stack"].values())

            if plan_tech and ref_tech:
                overlap = len(plan_tech & ref_tech)
                total = len(plan_tech | ref_tech)
                alignment_score += 0.2 * (overlap / total if total > 0 else 0)

        # Check pattern alignment
        if "pattern" in reference_content:
            pattern = reference_content["pattern"].lower()
            plan_str = json.dumps(plan).lower()

            if pattern in plan_str:
                alignment_score += 0.2

        # Check strategy alignment
        if "strategy" in reference_content and "strategy" in plan:
            if reference_content["strategy"] == plan["strategy"]:
                alignment_score += 0.1

        return min(alignment_score, 1.0)
