"""Evolution Planner Agent - Plans for system evolution and feature additions.

Uses Claude Code with model selection based on evolution complexity.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Optional

from ..base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent

logger = logging.getLogger("agents.planning.evolution")


@dataclass
class EvolutionTask:
    """Task for system evolution."""

    id: str
    name: str
    description: str
    evolution_type: str  # feature, enhancement, optimization, architecture
    scope: str  # component, module, system, ecosystem
    estimated_hours: float
    dependencies: list[str]
    backward_compatible: bool
    feature_flag: Optional[str] = None
    rollout_strategy: str = "gradual"  # gradual, instant, canary, blue_green
    success_metrics: list[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "evolution_type": self.evolution_type,
            "scope": self.scope,
            "estimated_hours": self.estimated_hours,
            "dependencies": self.dependencies,
            "backward_compatible": self.backward_compatible,
            "feature_flag": self.feature_flag,
            "rollout_strategy": self.rollout_strategy,
            "success_metrics": self.success_metrics or [],
        }


class EvolutionPlannerAgent(BaseAgent):
    """Plans system evolution using Claude Code.

    Specializes in:
    - Feature additions with backward compatibility
    - System enhancements and optimizations
    - Architecture evolution patterns
    - Gradual rollout strategies
    - Success metric definition
    """

    def __init__(self, name: str = "evolution_planner"):
        """Initialize evolution planner."""
        super().__init__(name, {"timeout": 300})
        self.claude_models = {
            "minor": "claude-3-haiku",  # Small features, optimizations
            "moderate": "claude-3-sonnet",  # Standard features, enhancements
            "major": "claude-3-opus",  # Architecture changes, major features
        }

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Create evolution plan using Claude Code.

        Args:
            input: Contains evolution requirements and constraints

        Returns:
            Evolution plan with rollout strategy
        """
        try:
            # Extract evolution details
            requirements = input.payload.get("requirements", {})
            current_capabilities = input.payload.get("current_capabilities", {})
            target_capabilities = input.payload.get("target_capabilities", {})
            evolution_type = input.payload.get("evolution_type", "feature")
            constraints = input.payload.get("constraints", {})

            # Assess evolution complexity
            complexity = self._assess_evolution_complexity(
                requirements, current_capabilities, target_capabilities, evolution_type
            )
            model = self.claude_models.get(complexity, "claude-3-sonnet")

            logger.info(f"Using {model} for {complexity} evolution planning")

            # Create plan using Claude Code
            plan = await self._create_evolution_plan_with_claude(
                requirements=requirements,
                current_capabilities=current_capabilities,
                target_capabilities=target_capabilities,
                evolution_type=evolution_type,
                constraints=constraints,
                model=model,
            )

            # Create artifact
            artifact = Artifact(kind="plan", ref="evolution_plan", content=plan)

            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.OK,
                artifacts=[artifact],
                metrics={
                    "complexity": complexity,
                    "model_used": model,
                    "total_phases": len(plan.get("phases", [])),
                    "total_tasks": len(plan.get("tasks", [])),
                    "estimated_hours": plan.get("total_hours", 0),
                    "backward_compatible": plan.get("backward_compatible", True),
                    "feature_flags": len(plan.get("feature_flags", [])),
                    "success_metrics": len(plan.get("success_metrics", [])),
                },
            )

        except Exception as e:
            logger.error(f"Evolution planning failed: {e}")
            return AgentOutput(task_id=input.task_id, status=AgentStatus.FAIL, error=str(e))

    def _assess_evolution_complexity(
        self,
        requirements: dict,
        current_capabilities: dict,
        target_capabilities: dict,
        evolution_type: str,
    ) -> str:
        """Assess evolution complexity for model selection."""
        complexity_score = 0

        # Check evolution type
        major_types = ["architecture", "ecosystem", "platform"]
        moderate_types = ["feature", "enhancement", "integration"]

        if evolution_type in major_types:
            complexity_score += 3
        elif evolution_type in moderate_types:
            complexity_score += 2
        else:
            complexity_score += 1

        # Check capability gap
        new_capabilities = len(target_capabilities.get("new", []))
        if new_capabilities > 10:
            complexity_score += 3
        elif new_capabilities > 5:
            complexity_score += 2
        else:
            complexity_score += 1

        # Check requirements complexity
        features = requirements.get("features", [])
        if len(features) > 15:
            complexity_score += 3
        elif len(features) > 7:
            complexity_score += 2
        else:
            complexity_score += 1

        # Check integration requirements
        integrations = requirements.get("integrations", [])
        if len(integrations) > 5:
            complexity_score += 2
        elif len(integrations) > 2:
            complexity_score += 1

        # Determine complexity level
        if complexity_score >= 9:
            return "major"
        elif complexity_score >= 5:
            return "moderate"
        else:
            return "minor"

    async def _create_evolution_plan_with_claude(
        self,
        requirements: dict,
        current_capabilities: dict,
        target_capabilities: dict,
        evolution_type: str,
        constraints: dict,
        model: str,
    ) -> dict[str, Any]:
        """Create evolution plan using Claude Code."""

        # Prepare Claude Code prompt
        prompt = f"""
        Create a detailed evolution plan for system enhancement.

        Current Capabilities:
        {json.dumps(current_capabilities, indent=2)}

        Target Capabilities:
        {json.dumps(target_capabilities, indent=2)}

        Requirements:
        {json.dumps(requirements, indent=2)}

        Evolution Type: {evolution_type}

        Constraints:
        - Backward Compatibility: {constraints.get('backward_compatible', True)}
        - Max Downtime: {constraints.get('max_downtime', '0')}
        - Rollout Period: {constraints.get('rollout_period', '30 days')}
        - Budget: {constraints.get('budget', 'medium')}

        Create a plan with:
        1. Incremental evolution phases
        2. Feature flags for gradual rollout
        3. Backward compatibility strategy
        4. Success metrics and KPIs
        5. Rollback procedures
        6. Testing and validation stages

        Output as JSON with structure:
        {{
            "evolution_name": "...",
            "strategy": "incremental|big_bang|parallel|experimental",
            "backward_compatible": true/false,
            "phases": [
                {{
                    "name": "foundation",
                    "tasks": [...],
                    "duration_days": N,
                    "can_rollback": true/false
                }}
            ],
            "tasks": [
                {{
                    "id": "evo-001",
                    "name": "...",
                    "evolution_type": "...",
                    "scope": "component|module|system",
                    "estimated_hours": N,
                    "dependencies": [],
                    "backward_compatible": true/false,
                    "feature_flag": "flag_name",
                    "rollout_strategy": "gradual|instant|canary",
                    "success_metrics": [...]
                }}
            ],
            "total_hours": N,
            "feature_flags": [...],
            "success_metrics": [...],
            "rollback_plan": {{...}}
        }}
        """

        # For now, simulate Claude Code response
        # In production, this would call actual Claude Code CLI
        plan = self._simulate_claude_response(
            requirements, current_capabilities, target_capabilities, evolution_type, model
        )

        return plan

    def _simulate_claude_response(
        self,
        requirements: dict,
        current_capabilities: dict,
        target_capabilities: dict,
        evolution_type: str,
        model: str,
    ) -> dict[str, Any]:
        """Simulate Claude Code response for testing."""

        # Create realistic evolution plan
        phases = [
            {
                "name": "foundation",
                "tasks": ["evo-001", "evo-002"],
                "duration_days": 5,
                "description": "Prepare foundation for new capabilities",
                "can_rollback": True,
            },
            {
                "name": "core_features",
                "tasks": ["evo-003", "evo-004", "evo-005"],
                "duration_days": 10,
                "description": "Implement core new features",
                "can_rollback": True,
            },
            {
                "name": "enhancements",
                "tasks": ["evo-006", "evo-007"],
                "duration_days": 7,
                "description": "Add enhancements and optimizations",
                "can_rollback": True,
            },
            {
                "name": "integration",
                "tasks": ["evo-008", "evo-009"],
                "duration_days": 5,
                "description": "Integrate with existing systems",
                "can_rollback": False,
            },
            {
                "name": "rollout",
                "tasks": ["evo-010"],
                "duration_days": 3,
                "description": "Gradual rollout to production",
                "can_rollback": True,
            },
        ]

        tasks = [
            {
                "id": "evo-001",
                "name": "Create abstraction layer",
                "evolution_type": "architecture",
                "scope": "module",
                "estimated_hours": 8,
                "dependencies": [],
                "backward_compatible": True,
                "feature_flag": None,
                "rollout_strategy": "instant",
                "success_metrics": ["API compatibility maintained"],
            },
            {
                "id": "evo-002",
                "name": "Setup feature flag system",
                "evolution_type": "infrastructure",
                "scope": "system",
                "estimated_hours": 6,
                "dependencies": [],
                "backward_compatible": True,
                "feature_flag": None,
                "rollout_strategy": "instant",
                "success_metrics": ["Feature flags operational"],
            },
            {
                "id": "evo-003",
                "name": "Implement new core feature",
                "evolution_type": evolution_type,
                "scope": "module",
                "estimated_hours": 16,
                "dependencies": ["evo-001", "evo-002"],
                "backward_compatible": True,
                "feature_flag": "new_core_feature",
                "rollout_strategy": "gradual",
                "success_metrics": ["Feature works correctly", "No performance regression"],
            },
            {
                "id": "evo-004",
                "name": "Add enhanced capabilities",
                "evolution_type": "enhancement",
                "scope": "component",
                "estimated_hours": 12,
                "dependencies": ["evo-003"],
                "backward_compatible": True,
                "feature_flag": "enhanced_capabilities",
                "rollout_strategy": "canary",
                "success_metrics": ["Capabilities functional", "User adoption > 50%"],
            },
            {
                "id": "evo-005",
                "name": "Optimize performance",
                "evolution_type": "optimization",
                "scope": "module",
                "estimated_hours": 8,
                "dependencies": ["evo-003"],
                "backward_compatible": True,
                "feature_flag": "performance_opt",
                "rollout_strategy": "gradual",
                "success_metrics": ["Response time < 100ms", "CPU usage reduced by 20%"],
            },
            {
                "id": "evo-006",
                "name": "Add monitoring and metrics",
                "evolution_type": "enhancement",
                "scope": "system",
                "estimated_hours": 6,
                "dependencies": ["evo-004", "evo-005"],
                "backward_compatible": True,
                "feature_flag": None,
                "rollout_strategy": "instant",
                "success_metrics": ["Metrics collection active", "Dashboard available"],
            },
            {
                "id": "evo-007",
                "name": "Implement auto-scaling",
                "evolution_type": "enhancement",
                "scope": "system",
                "estimated_hours": 10,
                "dependencies": ["evo-006"],
                "backward_compatible": True,
                "feature_flag": "auto_scaling",
                "rollout_strategy": "canary",
                "success_metrics": ["Auto-scaling triggers correctly", "Cost optimized"],
            },
            {
                "id": "evo-008",
                "name": "Integrate with external systems",
                "evolution_type": "integration",
                "scope": "system",
                "estimated_hours": 12,
                "dependencies": ["evo-004"],
                "backward_compatible": True,
                "feature_flag": "external_integration",
                "rollout_strategy": "gradual",
                "success_metrics": ["Integration successful", "Data sync working"],
            },
            {
                "id": "evo-009",
                "name": "Migrate existing data",
                "evolution_type": "migration",
                "scope": "system",
                "estimated_hours": 8,
                "dependencies": ["evo-008"],
                "backward_compatible": False,
                "feature_flag": None,
                "rollout_strategy": "blue_green",
                "success_metrics": ["Data integrity maintained", "No data loss"],
            },
            {
                "id": "evo-010",
                "name": "Production rollout",
                "evolution_type": "deployment",
                "scope": "ecosystem",
                "estimated_hours": 4,
                "dependencies": ["evo-009"],
                "backward_compatible": True,
                "feature_flag": None,
                "rollout_strategy": "gradual",
                "success_metrics": ["System stable", "SLA maintained", "User satisfaction > 90%"],
            },
        ]

        feature_flags = list(set(t["feature_flag"] for t in tasks if t["feature_flag"]))

        all_metrics = []
        for task in tasks:
            all_metrics.extend(task["success_metrics"])

        return {
            "evolution_name": f"{evolution_type}-evolution",
            "strategy": "incremental",
            "backward_compatible": True,
            "phases": phases,
            "tasks": tasks,
            "total_hours": sum(t["estimated_hours"] for t in tasks),
            "feature_flags": feature_flags,
            "success_metrics": list(set(all_metrics)),
            "rollback_plan": {
                "strategy": "feature_flag_disable",
                "steps": [
                    "Disable all feature flags",
                    "Route traffic to stable version",
                    "Monitor system stability",
                    "Investigate issues",
                    "Fix and re-deploy",
                ],
                "estimated_time": "15 minutes",
            },
            "model_used": model,
            "evolution_assessment": f"Planned {evolution_type} evolution with backward compatibility",
        }
