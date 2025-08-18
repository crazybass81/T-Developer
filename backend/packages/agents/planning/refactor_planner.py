"""Refactor Planner Agent - Plans for code improvement and refactoring.

Uses Claude Code with model selection based on risk and complexity.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Optional

from ..base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent

logger = logging.getLogger("agents.planning.refactor")


@dataclass
class RefactorTask:
    """Task for code refactoring."""

    id: str
    name: str
    description: str
    risk_level: str  # low, medium, high
    scope: str  # file, module, system
    estimated_hours: float
    dependencies: list[str]
    affected_files: list[str]
    refactor_type: str  # rename, extract, inline, restructure, optimize
    rollback_plan: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "risk_level": self.risk_level,
            "scope": self.scope,
            "estimated_hours": self.estimated_hours,
            "dependencies": self.dependencies,
            "affected_files": self.affected_files,
            "refactor_type": self.refactor_type,
            "rollback_plan": self.rollback_plan,
        }


class RefactorPlannerAgent(BaseAgent):
    """Plans code refactoring using Claude Code.

    Specializes in:
    - Risk assessment and mitigation
    - Incremental improvements
    - Test-first approach
    - Rollback strategies
    """

    def __init__(self, name: str = "refactor_planner"):
        """Initialize refactor planner."""
        super().__init__(name, {"timeout": 300})
        self.claude_models = {
            "low_risk": "claude-3-haiku",  # Simple renames, formatting
            "medium_risk": "claude-3-sonnet",  # Module restructuring
            "high_risk": "claude-3-opus",  # System-wide changes
        }

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Create refactoring plan using Claude Code.

        Args:
            input: Contains code analysis and improvement targets

        Returns:
            Refactoring plan with risk assessment
        """
        try:
            # Extract analysis results
            code_analysis = input.payload.get("code_analysis", {})
            improvement_targets = input.payload.get("improvement_targets", [])
            constraints = input.payload.get("constraints", {})
            current_metrics = input.payload.get("current_metrics", {})

            # Assess overall risk
            risk_level = self._assess_refactor_risk(code_analysis, improvement_targets)
            model = self.claude_models.get(f"{risk_level}_risk", "claude-3-sonnet")

            logger.info(f"Using {model} for {risk_level} risk refactoring planning")

            # Create plan using Claude Code
            plan = await self._create_refactor_plan_with_claude(
                code_analysis=code_analysis,
                improvement_targets=improvement_targets,
                current_metrics=current_metrics,
                constraints=constraints,
                model=model,
            )

            # Create artifact
            artifact = Artifact(kind="plan", ref="refactor_plan", content=plan)

            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.OK,
                artifacts=[artifact],
                metrics={
                    "risk_level": risk_level,
                    "model_used": model,
                    "total_tasks": len(plan.get("tasks", [])),
                    "estimated_hours": plan.get("total_hours", 0),
                    "affected_files": len(plan.get("affected_files", [])),
                    "improvement_score": plan.get("expected_improvement", 0),
                },
            )

        except Exception as e:
            logger.error(f"Refactor planning failed: {e}")
            return AgentOutput(task_id=input.task_id, status=AgentStatus.FAIL, error=str(e))

    def _assess_refactor_risk(self, code_analysis: dict, improvement_targets: list) -> str:
        """Assess refactoring risk level."""
        risk_score = 0

        # Check scope of changes
        affected_files = code_analysis.get("affected_files", [])
        if len(affected_files) > 20:
            risk_score += 3
        elif len(affected_files) > 5:
            risk_score += 2
        else:
            risk_score += 1

        # Check complexity
        max_complexity = max(code_analysis.get("complexity_scores", {}).values(), default=0)
        if max_complexity > 20:
            risk_score += 3
        elif max_complexity > 10:
            risk_score += 2
        else:
            risk_score += 1

        # Check improvement targets
        high_risk_targets = [
            "architecture_change",
            "database_migration",
            "api_breaking_change",
            "security_critical",
        ]

        for target in improvement_targets:
            if any(risk in str(target).lower() for risk in high_risk_targets):
                risk_score += 3
                break

        # Determine risk level
        if risk_score >= 7:
            return "high"
        elif risk_score >= 4:
            return "medium"
        else:
            return "low"

    async def _create_refactor_plan_with_claude(
        self,
        code_analysis: dict,
        improvement_targets: list,
        current_metrics: dict,
        constraints: dict,
        model: str,
    ) -> dict[str, Any]:
        """Create refactoring plan using Claude Code."""

        # Prepare Claude Code prompt
        prompt = f"""
        Create a detailed refactoring plan for improving existing code.

        Current Code Analysis:
        {json.dumps(code_analysis, indent=2)}

        Improvement Targets:
        {json.dumps(improvement_targets, indent=2)}

        Current Metrics:
        - Test Coverage: {current_metrics.get('coverage', 'unknown')}
        - Complexity: {current_metrics.get('complexity', 'unknown')}
        - Technical Debt: {current_metrics.get('debt_hours', 'unknown')}

        Constraints:
        - Max Downtime: {constraints.get('max_downtime', 'none')}
        - Team Availability: {constraints.get('team_availability', 'full')}
        - Deadline: {constraints.get('deadline', 'flexible')}

        Create a plan with:
        1. Risk-ordered tasks (low risk first)
        2. Incremental improvements
        3. Test requirements for each change
        4. Rollback strategy for risky changes
        5. Expected improvement metrics
        6. Parallel vs sequential execution

        Output as JSON with structure:
        {{
            "summary": "...",
            "phases": [
                {{
                    "name": "preparation",
                    "tasks": [...],
                    "risk": "low"
                }},
                {{
                    "name": "safe_improvements",
                    "tasks": [...],
                    "risk": "low"
                }},
                {{
                    "name": "moderate_changes",
                    "tasks": [...],
                    "risk": "medium"
                }},
                {{
                    "name": "risky_changes",
                    "tasks": [...],
                    "risk": "high"
                }}
            ],
            "tasks": [
                {{
                    "id": "refactor-001",
                    "name": "...",
                    "risk_level": "low|medium|high",
                    "scope": "file|module|system",
                    "estimated_hours": N,
                    "dependencies": [],
                    "affected_files": [...],
                    "refactor_type": "...",
                    "test_requirements": "...",
                    "rollback_plan": "..."
                }}
            ],
            "total_hours": N,
            "affected_files": [...],
            "expected_improvement": {{
                "coverage": "+N%",
                "complexity": "-N%",
                "performance": "+N%"
            }}
        }}
        """

        # For now, simulate Claude Code response
        # In production, this would call actual Claude Code CLI
        plan = self._simulate_claude_response(
            code_analysis, improvement_targets, current_metrics, model
        )

        return plan

    def _simulate_claude_response(
        self, code_analysis: dict, improvement_targets: list, current_metrics: dict, model: str
    ) -> dict[str, Any]:
        """Simulate Claude Code response for testing."""

        # Create realistic refactoring plan
        phases = [
            {
                "name": "preparation",
                "tasks": ["refactor-001", "refactor-002"],
                "risk": "low",
                "description": "Setup and safety checks",
            },
            {
                "name": "safe_improvements",
                "tasks": ["refactor-003", "refactor-004", "refactor-005"],
                "risk": "low",
                "description": "Low-risk improvements",
            },
            {
                "name": "moderate_changes",
                "tasks": ["refactor-006", "refactor-007"],
                "risk": "medium",
                "description": "Module-level refactoring",
            },
            {
                "name": "risky_changes",
                "tasks": ["refactor-008"],
                "risk": "high",
                "description": "System-wide changes",
            },
        ]

        tasks = [
            {
                "id": "refactor-001",
                "name": "Add comprehensive tests",
                "risk_level": "low",
                "scope": "module",
                "estimated_hours": 4,
                "dependencies": [],
                "affected_files": ["tests/"],
                "refactor_type": "test_addition",
                "test_requirements": "Achieve 80% coverage before proceeding",
                "rollback_plan": "Tests are additive, no rollback needed",
            },
            {
                "id": "refactor-002",
                "name": "Setup monitoring and metrics",
                "risk_level": "low",
                "scope": "system",
                "estimated_hours": 2,
                "dependencies": [],
                "affected_files": ["monitoring/"],
                "refactor_type": "instrumentation",
                "test_requirements": "Verify metrics collection",
                "rollback_plan": "Remove monitoring code",
            },
            {
                "id": "refactor-003",
                "name": "Fix code style issues",
                "risk_level": "low",
                "scope": "file",
                "estimated_hours": 2,
                "dependencies": ["refactor-001"],
                "affected_files": code_analysis.get("files_with_issues", [])[:5],
                "refactor_type": "formatting",
                "test_requirements": "Run existing tests",
                "rollback_plan": "Git revert",
            },
            {
                "id": "refactor-004",
                "name": "Add type hints",
                "risk_level": "low",
                "scope": "module",
                "estimated_hours": 4,
                "dependencies": ["refactor-001"],
                "affected_files": code_analysis.get("files_without_types", [])[:10],
                "refactor_type": "type_annotation",
                "test_requirements": "Type check with mypy",
                "rollback_plan": "Remove type hints",
            },
            {
                "id": "refactor-005",
                "name": "Extract duplicate code",
                "risk_level": "low",
                "scope": "module",
                "estimated_hours": 6,
                "dependencies": ["refactor-001"],
                "affected_files": code_analysis.get("files_with_duplication", [])[:5],
                "refactor_type": "extract",
                "test_requirements": "Unit tests for extracted functions",
                "rollback_plan": "Inline extracted code",
            },
            {
                "id": "refactor-006",
                "name": "Restructure module organization",
                "risk_level": "medium",
                "scope": "module",
                "estimated_hours": 8,
                "dependencies": ["refactor-003", "refactor-004"],
                "affected_files": ["src/module/"],
                "refactor_type": "restructure",
                "test_requirements": "Integration tests pass",
                "rollback_plan": "Restore original structure from backup",
            },
            {
                "id": "refactor-007",
                "name": "Optimize database queries",
                "risk_level": "medium",
                "scope": "module",
                "estimated_hours": 6,
                "dependencies": ["refactor-002"],
                "affected_files": ["src/database/"],
                "refactor_type": "optimize",
                "test_requirements": "Performance benchmarks",
                "rollback_plan": "Revert to original queries",
            },
            {
                "id": "refactor-008",
                "name": "Migrate to new architecture pattern",
                "risk_level": "high",
                "scope": "system",
                "estimated_hours": 16,
                "dependencies": ["refactor-006", "refactor-007"],
                "affected_files": ["src/"],
                "refactor_type": "architecture_change",
                "test_requirements": "Full regression test suite",
                "rollback_plan": "Feature flag to switch between old and new",
            },
        ]

        total_hours = sum(t["estimated_hours"] for t in tasks)

        return {
            "summary": "Incremental refactoring plan with risk mitigation",
            "phases": phases,
            "tasks": tasks,
            "total_hours": total_hours,
            "affected_files": list(set(file for task in tasks for file in task["affected_files"])),
            "expected_improvement": {
                "coverage": "+25%",
                "complexity": "-30%",
                "performance": "+15%",
                "maintainability": "+40%",
            },
            "model_used": model,
            "risk_assessment": "Structured approach from low to high risk changes",
        }
