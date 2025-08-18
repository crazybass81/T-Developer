"""Migration Planner Agent - Plans for technology stack migrations.

Uses Claude Code with model selection based on migration complexity.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

from ..base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent

logger = logging.getLogger("agents.planning.migration")


@dataclass
class MigrationTask:
    """Task for technology migration."""

    id: str
    name: str
    description: str
    phase: str  # analysis, preparation, pilot, migration, validation, cutover
    migration_type: str  # data, api, platform, framework, database
    estimated_hours: float
    dependencies: list[str]
    rollback_checkpoint: bool  # Can rollback from this point
    parallel_run_required: bool  # Needs parallel operation
    validation_criteria: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "phase": self.phase,
            "migration_type": self.migration_type,
            "estimated_hours": self.estimated_hours,
            "dependencies": self.dependencies,
            "rollback_checkpoint": self.rollback_checkpoint,
            "parallel_run_required": self.parallel_run_required,
            "validation_criteria": self.validation_criteria,
        }


class MigrationPlannerAgent(BaseAgent):
    """Plans technology migrations using Claude Code.

    Specializes in:
    - Zero-downtime migrations
    - Parallel run strategies
    - Data migration safety
    - Rollback checkpoints
    - Validation and cutover
    """

    def __init__(self, name: str = "migration_planner"):
        """Initialize migration planner."""
        super().__init__(name, {"timeout": 300})
        self.claude_models = {
            "small": "claude-3-haiku",  # Library updates, minor version
            "medium": "claude-3-sonnet",  # Framework migrations
            "large": "claude-3-opus",  # Platform/database migrations
        }

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Create migration plan using Claude Code.

        Args:
            input: Contains current and target stack information

        Returns:
            Migration plan with rollback strategy
        """
        try:
            # Extract migration details
            current_stack = input.payload.get("current_stack", {})
            target_stack = input.payload.get("target_stack", {})
            migration_type = input.payload.get("migration_type", "framework")
            constraints = input.payload.get("constraints", {})
            data_volume = input.payload.get("data_volume", "medium")

            # Assess migration scale
            scale = self._assess_migration_scale(
                current_stack, target_stack, migration_type, data_volume
            )
            model = self.claude_models.get(scale, "claude-3-sonnet")

            logger.info(f"Using {model} for {scale} scale migration planning")

            # Create plan using Claude Code
            plan = await self._create_migration_plan_with_claude(
                current_stack=current_stack,
                target_stack=target_stack,
                migration_type=migration_type,
                data_volume=data_volume,
                constraints=constraints,
                model=model,
            )

            # Create artifact
            artifact = Artifact(kind="plan", ref="migration_plan", content=plan)

            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.OK,
                artifacts=[artifact],
                metrics={
                    "scale": scale,
                    "model_used": model,
                    "total_phases": len(plan.get("phases", [])),
                    "total_tasks": len(plan.get("tasks", [])),
                    "estimated_hours": plan.get("total_hours", 0),
                    "rollback_points": plan.get("rollback_points", 0),
                    "parallel_run_duration": plan.get("parallel_run_days", 0),
                },
            )

        except Exception as e:
            logger.error(f"Migration planning failed: {e}")
            return AgentOutput(task_id=input.task_id, status=AgentStatus.FAIL, error=str(e))

    def _assess_migration_scale(
        self, current_stack: dict, target_stack: dict, migration_type: str, data_volume: str
    ) -> str:
        """Assess migration scale for model selection."""
        scale_score = 0

        # Check migration type complexity
        complex_types = ["platform", "database", "microservices"]
        medium_types = ["framework", "api", "runtime"]

        if migration_type in complex_types:
            scale_score += 3
        elif migration_type in medium_types:
            scale_score += 2
        else:
            scale_score += 1

        # Check data volume
        if data_volume == "large":
            scale_score += 3
        elif data_volume == "medium":
            scale_score += 2
        else:
            scale_score += 1

        # Check breaking changes
        major_version_change = self._is_major_version_change(current_stack, target_stack)
        if major_version_change:
            scale_score += 2

        # Determine scale
        if scale_score >= 7:
            return "large"
        elif scale_score >= 4:
            return "medium"
        else:
            return "small"

    def _is_major_version_change(self, current: dict, target: dict) -> bool:
        """Check if migration involves major version changes."""
        for key in current:
            if key in target:
                current_ver = str(current[key]).split(".")[0]
                target_ver = str(target[key]).split(".")[0]
                if current_ver != target_ver:
                    return True
        return False

    async def _create_migration_plan_with_claude(
        self,
        current_stack: dict,
        target_stack: dict,
        migration_type: str,
        data_volume: str,
        constraints: dict,
        model: str,
    ) -> dict[str, Any]:
        """Create migration plan using Claude Code."""

        # Prepare Claude Code prompt
        prompt = f"""
        Create a detailed migration plan for technology stack migration.

        Current Stack:
        {json.dumps(current_stack, indent=2)}

        Target Stack:
        {json.dumps(target_stack, indent=2)}

        Migration Type: {migration_type}
        Data Volume: {data_volume}

        Constraints:
        - Max Downtime: {constraints.get('max_downtime', '0')}
        - Rollback Required: {constraints.get('rollback_required', True)}
        - Team Size: {constraints.get('team_size', 'small')}

        Create a plan with:
        1. Phased migration approach
        2. Parallel run strategy where needed
        3. Rollback checkpoints
        4. Data migration strategy
        5. Validation criteria for each phase
        6. Zero-downtime cutover plan

        Output as JSON with structure:
        {{
            "migration_name": "...",
            "strategy": "big_bang|phased|parallel|blue_green",
            "phases": [
                {{
                    "name": "analysis",
                    "tasks": [...],
                    "duration_days": N
                }}
            ],
            "tasks": [
                {{
                    "id": "migrate-001",
                    "name": "...",
                    "phase": "...",
                    "migration_type": "...",
                    "estimated_hours": N,
                    "dependencies": [],
                    "rollback_checkpoint": true/false,
                    "parallel_run_required": true/false,
                    "validation_criteria": [...]
                }}
            ],
            "total_hours": N,
            "parallel_run_days": N,
            "rollback_points": N,
            "cutover_plan": {{...}}
        }}
        """

        # For now, simulate Claude Code response
        # In production, this would call actual Claude Code CLI
        plan = self._simulate_claude_response(
            current_stack, target_stack, migration_type, data_volume, model
        )

        return plan

    def _simulate_claude_response(
        self,
        current_stack: dict,
        target_stack: dict,
        migration_type: str,
        data_volume: str,
        model: str,
    ) -> dict[str, Any]:
        """Simulate Claude Code response for testing."""

        # Create realistic migration plan
        phases = [
            {
                "name": "analysis",
                "tasks": ["migrate-001", "migrate-002"],
                "duration_days": 3,
                "description": "Analyze current system and dependencies",
            },
            {
                "name": "preparation",
                "tasks": ["migrate-003", "migrate-004"],
                "duration_days": 5,
                "description": "Prepare migration tools and environment",
            },
            {
                "name": "pilot",
                "tasks": ["migrate-005", "migrate-006"],
                "duration_days": 7,
                "description": "Pilot migration with subset of data",
            },
            {
                "name": "migration",
                "tasks": ["migrate-007", "migrate-008", "migrate-009"],
                "duration_days": 10,
                "description": "Main migration execution",
            },
            {
                "name": "validation",
                "tasks": ["migrate-010", "migrate-011"],
                "duration_days": 3,
                "description": "Validate migrated system",
            },
            {
                "name": "cutover",
                "tasks": ["migrate-012"],
                "duration_days": 1,
                "description": "Final cutover to new system",
            },
        ]

        tasks = [
            {
                "id": "migrate-001",
                "name": "Analyze dependencies and impacts",
                "phase": "analysis",
                "migration_type": "analysis",
                "estimated_hours": 8,
                "dependencies": [],
                "rollback_checkpoint": False,
                "parallel_run_required": False,
                "validation_criteria": ["Dependency map complete", "Impact analysis documented"],
            },
            {
                "id": "migrate-002",
                "name": "Create migration test plan",
                "phase": "analysis",
                "migration_type": "planning",
                "estimated_hours": 4,
                "dependencies": ["migrate-001"],
                "rollback_checkpoint": False,
                "parallel_run_required": False,
                "validation_criteria": ["Test cases defined", "Success criteria established"],
            },
            {
                "id": "migrate-003",
                "name": "Setup target environment",
                "phase": "preparation",
                "migration_type": "infrastructure",
                "estimated_hours": 8,
                "dependencies": ["migrate-002"],
                "rollback_checkpoint": True,
                "parallel_run_required": False,
                "validation_criteria": ["Environment accessible", "Configuration validated"],
            },
            {
                "id": "migrate-004",
                "name": "Create migration scripts",
                "phase": "preparation",
                "migration_type": "tooling",
                "estimated_hours": 12,
                "dependencies": ["migrate-003"],
                "rollback_checkpoint": False,
                "parallel_run_required": False,
                "validation_criteria": ["Scripts tested", "Rollback scripts ready"],
            },
            {
                "id": "migrate-005",
                "name": "Migrate pilot data subset",
                "phase": "pilot",
                "migration_type": "data",
                "estimated_hours": 6,
                "dependencies": ["migrate-004"],
                "rollback_checkpoint": True,
                "parallel_run_required": True,
                "validation_criteria": ["Data integrity verified", "Performance acceptable"],
            },
            {
                "id": "migrate-006",
                "name": "Test pilot system",
                "phase": "pilot",
                "migration_type": "validation",
                "estimated_hours": 8,
                "dependencies": ["migrate-005"],
                "rollback_checkpoint": True,
                "parallel_run_required": True,
                "validation_criteria": ["All tests pass", "No data loss"],
            },
            {
                "id": "migrate-007",
                "name": "Start parallel run",
                "phase": "migration",
                "migration_type": migration_type,
                "estimated_hours": 4,
                "dependencies": ["migrate-006"],
                "rollback_checkpoint": True,
                "parallel_run_required": True,
                "validation_criteria": ["Both systems operational", "Data sync working"],
            },
            {
                "id": "migrate-008",
                "name": "Migrate main data",
                "phase": "migration",
                "migration_type": "data",
                "estimated_hours": 16,
                "dependencies": ["migrate-007"],
                "rollback_checkpoint": True,
                "parallel_run_required": True,
                "validation_criteria": ["Data migrated", "Checksums match"],
            },
            {
                "id": "migrate-009",
                "name": "Sync incremental changes",
                "phase": "migration",
                "migration_type": "data",
                "estimated_hours": 8,
                "dependencies": ["migrate-008"],
                "rollback_checkpoint": True,
                "parallel_run_required": True,
                "validation_criteria": ["Systems in sync", "Lag acceptable"],
            },
            {
                "id": "migrate-010",
                "name": "Run validation suite",
                "phase": "validation",
                "migration_type": "validation",
                "estimated_hours": 6,
                "dependencies": ["migrate-009"],
                "rollback_checkpoint": True,
                "parallel_run_required": True,
                "validation_criteria": ["All validations pass", "Performance benchmarks met"],
            },
            {
                "id": "migrate-011",
                "name": "User acceptance testing",
                "phase": "validation",
                "migration_type": "validation",
                "estimated_hours": 8,
                "dependencies": ["migrate-010"],
                "rollback_checkpoint": True,
                "parallel_run_required": True,
                "validation_criteria": ["UAT signed off", "No critical issues"],
            },
            {
                "id": "migrate-012",
                "name": "Execute cutover",
                "phase": "cutover",
                "migration_type": "cutover",
                "estimated_hours": 4,
                "dependencies": ["migrate-011"],
                "rollback_checkpoint": True,
                "parallel_run_required": False,
                "validation_criteria": ["Traffic switched", "Old system decommissioned"],
            },
        ]

        rollback_points = sum(1 for t in tasks if t["rollback_checkpoint"])

        return {
            "migration_name": f"{migration_type}-migration",
            "strategy": "parallel" if data_volume in ["medium", "large"] else "phased",
            "phases": phases,
            "tasks": tasks,
            "total_hours": sum(t["estimated_hours"] for t in tasks),
            "parallel_run_days": 14 if data_volume in ["medium", "large"] else 7,
            "rollback_points": rollback_points,
            "cutover_plan": {
                "strategy": "blue_green",
                "steps": [
                    "Freeze writes to old system",
                    "Final data sync",
                    "Switch DNS/routing",
                    "Validate new system",
                    "Keep old system standby for 24h",
                ],
            },
            "model_used": model,
            "migration_complexity": f"Assessed as {migration_type} migration with {data_volume} data",
        }
