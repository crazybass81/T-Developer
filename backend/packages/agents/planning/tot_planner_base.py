"""Tree of Thoughts (ToT) based planning framework for all planners.

Implements a systematic approach to explore multiple planning paths
and select the optimal one based on evaluation criteria.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger("agents.planning.tot")


@dataclass
class Thought:
    """Represents a single thought/step in the planning tree."""

    id: str
    content: str
    parent_id: Optional[str]
    depth: int
    score: float
    reasoning: str
    children: list["Thought"] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


@dataclass
class PlanPath:
    """Represents a complete path from root to leaf in the thought tree."""

    thoughts: list[Thought]
    total_score: float
    feasibility: float
    completeness: float
    risk_level: float

    def to_plan(self) -> dict[str, Any]:
        """Convert the path to an executable plan."""
        return {
            "steps": [t.content for t in self.thoughts],
            "reasoning": [t.reasoning for t in self.thoughts],
            "score": self.total_score,
            "metrics": {
                "feasibility": self.feasibility,
                "completeness": self.completeness,
                "risk_level": self.risk_level,
            },
        }


class TreeOfThoughtsPlanner(ABC):
    """Base class for Tree of Thoughts planning."""

    def __init__(self, max_depth: int = 5, beam_width: int = 3):
        """Initialize ToT planner.

        Args:
            max_depth: Maximum depth of thought tree
            beam_width: Number of top thoughts to keep at each level
        """
        self.max_depth = max_depth
        self.beam_width = beam_width
        self.thought_tree = None

    @abstractmethod
    async def generate_initial_thoughts(self, context: dict[str, Any]) -> list[Thought]:
        """Generate initial thoughts/approaches for the planning task.

        Args:
            context: Planning context including requirements and constraints

        Returns:
            List of initial thoughts
        """
        pass

    @abstractmethod
    async def expand_thought(self, thought: Thought, context: dict[str, Any]) -> list[Thought]:
        """Expand a thought into multiple next-step thoughts.

        Args:
            thought: Current thought to expand
            context: Planning context

        Returns:
            List of child thoughts
        """
        pass

    @abstractmethod
    async def evaluate_thought(self, thought: Thought, context: dict[str, Any]) -> float:
        """Evaluate the quality/promise of a thought.

        Args:
            thought: Thought to evaluate
            context: Planning context

        Returns:
            Score between 0 and 1
        """
        pass

    @abstractmethod
    async def is_complete_plan(self, path: list[Thought], context: dict[str, Any]) -> bool:
        """Check if a path represents a complete plan.

        Args:
            path: Current path of thoughts
            context: Planning context

        Returns:
            True if the plan is complete
        """
        pass

    async def plan_with_tot(self, context: dict[str, Any]) -> list[PlanPath]:
        """Execute Tree of Thoughts planning.

        Args:
            context: Planning context with requirements and constraints

        Returns:
            List of complete plan paths, sorted by score
        """
        logger.info("Starting Tree of Thoughts planning")

        # Generate initial thoughts
        initial_thoughts = await self.generate_initial_thoughts(context)

        # Evaluate and select top thoughts
        for thought in initial_thoughts:
            thought.score = await self.evaluate_thought(thought, context)

        # Sort and keep top beam_width thoughts
        current_level = sorted(initial_thoughts, key=lambda t: t.score, reverse=True)[
            : self.beam_width
        ]

        complete_paths = []

        # Build tree level by level
        for depth in range(1, self.max_depth):
            next_level = []

            for thought in current_level:
                # Check if current path is complete
                path = self._get_path_to_root(thought)
                if await self.is_complete_plan(path, context):
                    complete_paths.append(self._create_plan_path(path))
                    continue

                # Expand thought
                children = await self.expand_thought(thought, context)

                # Evaluate children
                for child in children:
                    child.parent_id = thought.id
                    child.depth = depth
                    child.score = await self.evaluate_thought(child, context)
                    thought.children.append(child)
                    next_level.append(child)

            if not next_level:
                break

            # Select top thoughts for next level
            current_level = sorted(next_level, key=lambda t: t.score, reverse=True)[
                : self.beam_width
            ]

        # Add remaining paths as complete
        for thought in current_level:
            path = self._get_path_to_root(thought)
            complete_paths.append(self._create_plan_path(path))

        # Sort paths by total score
        complete_paths.sort(key=lambda p: p.total_score, reverse=True)

        logger.info(f"Generated {len(complete_paths)} complete plan paths")
        return complete_paths

    def _get_path_to_root(self, thought: Thought) -> list[Thought]:
        """Get path from thought to root."""
        path = []
        current = thought
        while current:
            path.append(current)
            current = self._find_parent(current)
        return list(reversed(path))

    def _find_parent(self, thought: Thought) -> Optional[Thought]:
        """Find parent thought in tree."""
        # This would need proper tree traversal
        # Simplified for illustration
        return None

    def _create_plan_path(self, thoughts: list[Thought]) -> PlanPath:
        """Create a PlanPath from a list of thoughts."""
        total_score = sum(t.score for t in thoughts) / len(thoughts)

        # Calculate path metrics
        feasibility = self._calculate_feasibility(thoughts)
        completeness = self._calculate_completeness(thoughts)
        risk_level = self._calculate_risk(thoughts)

        return PlanPath(
            thoughts=thoughts,
            total_score=total_score,
            feasibility=feasibility,
            completeness=completeness,
            risk_level=risk_level,
        )

    def _calculate_feasibility(self, thoughts: list[Thought]) -> float:
        """Calculate feasibility score for the path."""
        # Implementation would analyze resource requirements, dependencies, etc.
        return 0.8

    def _calculate_completeness(self, thoughts: list[Thought]) -> float:
        """Calculate completeness score for the path."""
        # Implementation would check coverage of requirements
        return 0.9

    def _calculate_risk(self, thoughts: list[Thought]) -> float:
        """Calculate risk level for the path."""
        # Implementation would assess potential failure points
        return 0.2


class PlannerPromptBuilder:
    """Builds specialized prompts for each planner type."""

    @staticmethod
    def build_generation_prompt(
        requirements: dict[str, Any], references: list[dict[str, Any]], thought_stage: str
    ) -> str:
        """Build prompt for generation planning with ToT."""

        base_prompt = f"""
You are planning a new project/service generation. Use Tree of Thoughts approach.

Current Stage: {thought_stage}

Requirements:
{json.dumps(requirements, indent=2)}

Reference Examples from Similar Projects:
{json.dumps(references[:3], indent=2) if references else "No references available"}

"""

        if thought_stage == "initial":
            return (
                base_prompt
                + """
Generate 3-5 different high-level approaches for creating this project.
For each approach, consider:
1. Architecture pattern (monolithic, microservices, serverless, etc.)
2. Technology stack choices
3. Development methodology
4. Key components and their relationships

Output as JSON:
{
    "thoughts": [
        {
            "approach": "Microservices with Event-Driven Architecture",
            "reasoning": "Why this approach fits the requirements",
            "pros": ["scalability", "independent deployment"],
            "cons": ["complexity", "network overhead"],
            "key_components": ["API Gateway", "Service A", "Service B", "Message Queue"]
        }
    ]
}
"""
            )

        elif thought_stage == "expand":
            return (
                base_prompt
                + """
Given the current approach, generate next-level implementation details.
Break down into specific tasks and technical decisions.

Consider:
1. Specific technology choices (frameworks, databases, etc.)
2. Implementation phases
3. Integration points
4. Testing strategy

Output detailed task breakdown with dependencies.
"""
            )

        else:  # evaluate
            return (
                base_prompt
                + """
Evaluate this planning path for:
1. Technical feasibility (0-1)
2. Alignment with requirements (0-1)
3. Resource efficiency (0-1)
4. Maintainability (0-1)
5. Scalability potential (0-1)

Provide overall score and detailed reasoning.
"""
            )

    @staticmethod
    def build_refactor_prompt(
        code_analysis: dict[str, Any],
        improvement_targets: list[str],
        references: list[dict[str, Any]],
        thought_stage: str,
    ) -> str:
        """Build prompt for refactoring planning with ToT."""

        base_prompt = f"""
You are planning code refactoring and improvements. Use Tree of Thoughts approach.

Current Stage: {thought_stage}

Code Analysis:
{json.dumps(code_analysis, indent=2)}

Improvement Targets:
{json.dumps(improvement_targets, indent=2)}

Best Practices from Similar Refactoring:
{json.dumps(references[:3], indent=2) if references else "No references available"}

"""

        if thought_stage == "initial":
            return (
                base_prompt
                + """
Generate 3-5 different refactoring strategies.
For each strategy, consider:
1. Order of operations (what to refactor first)
2. Risk level and mitigation
3. Testing approach
4. Rollback plan

Output as JSON:
{
    "thoughts": [
        {
            "strategy": "Incremental Bottom-Up Refactoring",
            "reasoning": "Start with leaf components to minimize risk",
            "phases": ["Extract utilities", "Refactor data layer", "Update business logic", "Modernize UI"],
            "risk_level": "low",
            "rollback_approach": "Feature flags for gradual rollout"
        }
    ]
}
"""
            )

        elif thought_stage == "expand":
            return (
                base_prompt
                + """
Break down the refactoring strategy into specific tasks.
For each task, specify:
1. Files to modify
2. Refactoring patterns to apply
3. Test requirements
4. Success criteria

Include dependencies between tasks.
"""
            )

        else:  # evaluate
            return (
                base_prompt
                + """
Evaluate this refactoring plan for:
1. Risk assessment (0-1, lower is better)
2. Code quality improvement potential (0-1)
3. Test coverage impact (0-1)
4. Performance impact (0-1)
5. Backward compatibility (0-1)

Provide overall score and risk analysis.
"""
            )

    @staticmethod
    def build_migration_prompt(
        current_stack: dict[str, Any],
        target_stack: dict[str, Any],
        references: list[dict[str, Any]],
        thought_stage: str,
    ) -> str:
        """Build prompt for migration planning with ToT."""

        base_prompt = f"""
You are planning a technology stack migration. Use Tree of Thoughts approach.

Current Stage: {thought_stage}

Current Stack:
{json.dumps(current_stack, indent=2)}

Target Stack:
{json.dumps(target_stack, indent=2)}

Successful Migration Patterns:
{json.dumps(references[:3], indent=2) if references else "No references available"}

"""

        if thought_stage == "initial":
            return (
                base_prompt
                + """
Generate 3-5 different migration strategies.
For each strategy, consider:
1. Migration pattern (big bang, parallel run, gradual, blue-green)
2. Data migration approach
3. Downtime requirements
4. Rollback capability

Output as JSON:
{
    "thoughts": [
        {
            "strategy": "Parallel Run with Gradual Cutover",
            "reasoning": "Minimize risk with side-by-side operation",
            "phases": ["Setup parallel environment", "Sync data", "Route traffic gradually", "Decommission old"],
            "estimated_duration": "6 weeks",
            "downtime": "zero"
        }
    ]
}
"""
            )

        elif thought_stage == "expand":
            return (
                base_prompt
                + """
Detail the migration steps for the chosen strategy.
Include:
1. Environment setup tasks
2. Data migration scripts
3. Testing checkpoints
4. Cutover procedures
5. Monitoring requirements

Specify rollback points and validation criteria.
"""
            )

        else:  # evaluate
            return (
                base_prompt
                + """
Evaluate this migration plan for:
1. Data integrity risk (0-1, lower is better)
2. Service continuity (0-1)
3. Rollback feasibility (0-1)
4. Resource requirements (0-1, lower is better)
5. Timeline realism (0-1)

Provide risk assessment and contingency recommendations.
"""
            )

    @staticmethod
    def build_evolution_prompt(
        current_capabilities: dict[str, Any],
        target_capabilities: dict[str, Any],
        references: list[dict[str, Any]],
        thought_stage: str,
    ) -> str:
        """Build prompt for system evolution planning with ToT."""

        base_prompt = f"""
You are planning system evolution and capability expansion. Use Tree of Thoughts approach.

Current Stage: {thought_stage}

Current System Capabilities:
{json.dumps(current_capabilities, indent=2)}

Target Capabilities:
{json.dumps(target_capabilities, indent=2)}

Evolution Patterns from Similar Systems:
{json.dumps(references[:3], indent=2) if references else "No references available"}

"""

        if thought_stage == "initial":
            return (
                base_prompt
                + """
Generate 3-5 different evolution approaches.
For each approach, consider:
1. Feature rollout strategy
2. Backward compatibility approach
3. User migration path
4. Performance impact

Output as JSON:
{
    "thoughts": [
        {
            "approach": "Modular Feature Addition with Feature Flags",
            "reasoning": "Allow gradual adoption and easy rollback",
            "phases": ["Core enhancement", "Feature modules", "Integration", "Optimization"],
            "compatibility_strategy": "Versioned APIs with deprecation notices",
            "adoption_model": "Opt-in beta → Gradual rollout → General availability"
        }
    ]
}
"""
            )

        elif thought_stage == "expand":
            return (
                base_prompt
                + """
Break down the evolution approach into implementation tasks.
Detail:
1. New components to build
2. Existing components to modify
3. Integration requirements
4. Feature flag configuration
5. Performance benchmarks

Include success metrics for each phase.
"""
            )

        else:  # evaluate
            return (
                base_prompt
                + """
Evaluate this evolution plan for:
1. User disruption (0-1, lower is better)
2. Feature completeness (0-1)
3. System stability impact (0-1, lower is better)
4. Scalability improvement (0-1)
5. Technical debt management (0-1)

Provide adoption forecast and risk analysis.
"""
            )
