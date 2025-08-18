"""Generation Planner Agent - Plans for new project/service creation.

Uses Claude Code with Tree of Thoughts approach for optimal planning.
"""

import json
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Optional

from ..base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent
from .tot_planner_base import PlannerPromptBuilder, PlanPath, Thought, TreeOfThoughtsPlanner

logger = logging.getLogger("agents.planning.generation")


@dataclass
class GenerationTask:
    """Task for new code generation."""

    id: str
    name: str
    description: str
    phase: str  # scaffold, core, feature, test, deploy
    estimated_hours: float
    dependencies: list[str]
    blueprint_template: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "phase": self.phase,
            "estimated_hours": self.estimated_hours,
            "dependencies": self.dependencies,
            "blueprint_template": self.blueprint_template,
        }


class GenerationPlannerToT(TreeOfThoughtsPlanner):
    """Tree of Thoughts planner for generation tasks."""

    async def generate_initial_thoughts(self, context: dict[str, Any]) -> list[Thought]:
        """Generate initial generation approaches."""
        prompt = PlannerPromptBuilder.build_generation_prompt(
            requirements=context.get("requirements", {}),
            references=context.get("references", []),
            thought_stage="initial",
        )

        # In production, call Claude API
        # For now, return example thoughts
        return [
            Thought(
                id=f"thought-{uuid.uuid4().hex[:8]}",
                content="Microservices architecture with event-driven communication",
                parent_id=None,
                depth=0,
                score=0.0,
                reasoning="Scalable and maintainable for complex requirements",
            ),
            Thought(
                id=f"thought-{uuid.uuid4().hex[:8]}",
                content="Monolithic architecture with modular design",
                parent_id=None,
                depth=0,
                score=0.0,
                reasoning="Simpler to develop and deploy initially",
            ),
            Thought(
                id=f"thought-{uuid.uuid4().hex[:8]}",
                content="Serverless architecture with managed services",
                parent_id=None,
                depth=0,
                score=0.0,
                reasoning="Cost-effective and automatically scalable",
            ),
        ]

    async def expand_thought(self, thought: Thought, context: dict[str, Any]) -> list[Thought]:
        """Expand generation thought into detailed steps."""
        prompt = PlannerPromptBuilder.build_generation_prompt(
            requirements=context.get("requirements", {}),
            references=context.get("references", []),
            thought_stage="expand",
        )

        # Generate child thoughts based on parent
        children = []
        # In production, use Claude to generate these
        return children

    async def evaluate_thought(self, thought: Thought, context: dict[str, Any]) -> float:
        """Evaluate generation thought quality."""
        prompt = PlannerPromptBuilder.build_generation_prompt(
            requirements=context.get("requirements", {}),
            references=context.get("references", []),
            thought_stage="evaluate",
        )

        # In production, use Claude to evaluate
        # For now, return a score based on simple heuristics
        score = 0.7
        if "microservices" in thought.content.lower():
            score += 0.1
        if "serverless" in thought.content.lower():
            score += 0.05
        return min(score, 1.0)

    async def is_complete_plan(self, path: list[Thought], context: dict[str, Any]) -> bool:
        """Check if generation plan is complete."""
        # A complete plan should have scaffold, core, features, testing, deployment
        required_phases = {"scaffold", "core", "features", "testing", "deployment"}
        covered_phases = set()

        for thought in path:
            for phase in required_phases:
                if phase in thought.content.lower():
                    covered_phases.add(phase)

        return len(covered_phases) >= 4  # At least 4 out of 5 phases


class GenerationPlannerAgent(BaseAgent):
    """Plans new project/service generation using Claude Code with Tree of Thoughts.

    Specializes in:
    - Tree of Thoughts exploration for optimal approach
    - Sequential build phases (scaffold → core → features)
    - Blueprint template selection
    - Technology stack decisions
    - Reference-based learning from similar projects
    """

    def __init__(self, name: str = "generation_planner"):
        """Initialize generation planner."""
        super().__init__(name, {"timeout": 300})
        self.claude_models = {
            "simple": "claude-3-haiku",  # Simple CRUD apps
            "medium": "claude-3-sonnet",  # Standard microservices
            "complex": "claude-3-opus",  # Complex architectures
        }
        self.tot_planner = GenerationPlannerToT(max_depth=5, beam_width=3)

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Create generation plan using Claude Code with Tree of Thoughts.

        Args:
            input: Contains project requirements and constraints

        Returns:
            Generation plan with phases and tasks
        """
        try:
            # Extract requirements
            requirements = input.payload.get("requirements", {})
            project_type = input.payload.get("project_type", "api")
            tech_stack = input.payload.get("tech_stack", {})
            constraints = input.payload.get("constraints", {})
            references = input.payload.get("references", [])

            # Determine complexity
            complexity = self._assess_complexity(requirements, project_type)
            model = self.claude_models.get(complexity, "claude-3-sonnet")

            logger.info(f"Using {model} with ToT for {complexity} complexity generation planning")

            # Prepare context for ToT planning
            tot_context = {
                "requirements": requirements,
                "project_type": project_type,
                "tech_stack": tech_stack,
                "constraints": constraints,
                "references": references,
                "model": model,
            }

            # Execute Tree of Thoughts planning
            plan_paths = await self.tot_planner.plan_with_tot(tot_context)

            # Select the best plan path
            best_path = plan_paths[0] if plan_paths else None

            if best_path:
                # Convert ToT path to traditional plan format
                plan = await self._convert_tot_to_plan(
                    best_path, requirements, project_type, tech_stack, model
                )
            else:
                # Fallback to traditional planning if ToT fails
                plan = await self._create_generation_plan_with_claude(
                    requirements=requirements,
                    project_type=project_type,
                    tech_stack=tech_stack,
                    constraints=constraints,
                    model=model,
                )

            # Create artifact
            artifact = Artifact(kind="plan", ref="generation_plan", content=plan)

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
                },
            )

        except Exception as e:
            logger.error(f"Generation planning failed: {e}")
            return AgentOutput(task_id=input.task_id, status=AgentStatus.FAIL, error=str(e))

    def _assess_complexity(self, requirements: dict, project_type: str) -> str:
        """Assess project complexity for model selection."""
        score = 0

        # Check requirements complexity
        if len(requirements.get("features", [])) > 10:
            score += 3
        elif len(requirements.get("features", [])) > 5:
            score += 2
        else:
            score += 1

        # Check project type
        complex_types = ["microservices", "distributed", "ml-platform", "data-pipeline"]
        medium_types = ["api", "webapp", "cli", "batch-processor"]

        if project_type in complex_types:
            score += 3
        elif project_type in medium_types:
            score += 2
        else:
            score += 1

        # Check integrations
        integrations = requirements.get("integrations", [])
        if len(integrations) > 5:
            score += 3
        elif len(integrations) > 2:
            score += 2
        else:
            score += 1

        # Determine complexity
        if score >= 7:
            return "complex"
        elif score >= 4:
            return "medium"
        else:
            return "simple"

    async def _convert_tot_to_plan(
        self,
        plan_path: PlanPath,
        requirements: dict,
        project_type: str,
        tech_stack: dict,
        model: str,
    ) -> dict[str, Any]:
        """Convert Tree of Thoughts path to executable plan format."""

        phases = []
        tasks = []
        task_id = 1

        # Convert thoughts to phases and tasks
        current_phase = None
        phase_tasks = []

        for thought in plan_path.thoughts:
            # Determine phase from thought content
            phase_name = self._extract_phase_name(thought.content)

            if phase_name != current_phase:
                if current_phase and phase_tasks:
                    phases.append(
                        {
                            "name": current_phase,
                            "tasks": [f"task-{t:03d}" for t in phase_tasks],
                            "estimated_hours": len(phase_tasks) * 4,
                        }
                    )
                current_phase = phase_name
                phase_tasks = []

            # Create task from thought
            task = {
                "id": f"task-{task_id:03d}",
                "name": thought.content[:50],
                "description": thought.reasoning,
                "phase": phase_name,
                "estimated_hours": 4,
                "dependencies": [],
                "blueprint_template": None,
            }
            tasks.append(task)
            phase_tasks.append(task_id)
            task_id += 1

        # Add final phase
        if current_phase and phase_tasks:
            phases.append(
                {
                    "name": current_phase,
                    "tasks": [f"task-{t:03d}" for t in phase_tasks],
                    "estimated_hours": len(phase_tasks) * 4,
                }
            )

        return {
            "project_name": f"new-{project_type}-service",
            "phases": phases,
            "tasks": tasks,
            "total_hours": len(tasks) * 4,
            "technology_decisions": tech_stack,
            "model_used": model,
            "planning_method": "Tree of Thoughts",
            "tot_metrics": {
                "paths_explored": len(plan_path.thoughts),
                "best_score": plan_path.total_score,
                "feasibility": plan_path.feasibility,
                "completeness": plan_path.completeness,
                "risk_level": plan_path.risk_level,
            },
        }

    def _extract_phase_name(self, thought_content: str) -> str:
        """Extract phase name from thought content."""
        phases = ["scaffold", "core", "features", "testing", "deployment"]
        for phase in phases:
            if phase in thought_content.lower():
                return phase
        return "general"

    async def _create_generation_plan_with_claude(
        self, requirements: dict, project_type: str, tech_stack: dict, constraints: dict, model: str
    ) -> dict[str, Any]:
        """Create generation plan using Claude Code."""

        # Prepare Claude Code prompt
        prompt = f"""
        Create a detailed generation plan for a new {project_type} project.

        Requirements:
        {json.dumps(requirements, indent=2)}

        Tech Stack:
        {json.dumps(tech_stack, indent=2)}

        Constraints:
        - Timeline: {constraints.get('timeline', 'flexible')}
        - Budget: {constraints.get('budget', 'medium')}
        - Team Size: {constraints.get('team_size', 'small')}

        Create a plan with:
        1. Sequential phases (scaffold, core, features, testing, deployment)
        2. Specific tasks for each phase
        3. Time estimates
        4. Dependencies between tasks
        5. Blueprint templates to use
        6. Technology decisions

        Output as JSON with structure:
        {{
            "project_name": "...",
            "phases": [
                {{
                    "name": "scaffold",
                    "description": "...",
                    "tasks": [...],
                    "estimated_hours": N
                }}
            ],
            "tasks": [
                {{
                    "id": "task-001",
                    "name": "...",
                    "phase": "scaffold",
                    "estimated_hours": N,
                    "dependencies": [],
                    "blueprint_template": "..."
                }}
            ],
            "total_hours": N,
            "critical_path": [...],
            "technology_decisions": {{...}}
        }}
        """

        # For now, simulate Claude Code response
        # In production, this would call actual Claude Code CLI
        plan = self._simulate_claude_response(requirements, project_type, tech_stack, model)

        return plan

    def _simulate_claude_response(
        self, requirements: dict, project_type: str, tech_stack: dict, model: str
    ) -> dict[str, Any]:
        """Simulate Claude Code response for testing."""

        # Create realistic generation plan
        phases = [
            {
                "name": "scaffold",
                "description": "Project structure and basic setup",
                "tasks": ["task-001", "task-002"],
                "estimated_hours": 4,
            },
            {
                "name": "core",
                "description": "Core functionality implementation",
                "tasks": ["task-003", "task-004", "task-005"],
                "estimated_hours": 16,
            },
            {
                "name": "features",
                "description": "Feature implementation",
                "tasks": ["task-006", "task-007"],
                "estimated_hours": 24,
            },
            {
                "name": "testing",
                "description": "Testing and quality assurance",
                "tasks": ["task-008", "task-009"],
                "estimated_hours": 8,
            },
            {
                "name": "deployment",
                "description": "Deployment and CI/CD setup",
                "tasks": ["task-010"],
                "estimated_hours": 4,
            },
        ]

        tasks = [
            {
                "id": "task-001",
                "name": "Initialize project structure",
                "phase": "scaffold",
                "estimated_hours": 2,
                "dependencies": [],
                "blueprint_template": f"{project_type}-scaffold",
            },
            {
                "id": "task-002",
                "name": "Setup development environment",
                "phase": "scaffold",
                "estimated_hours": 2,
                "dependencies": ["task-001"],
                "blueprint_template": "dev-environment",
            },
            {
                "id": "task-003",
                "name": "Implement data models",
                "phase": "core",
                "estimated_hours": 6,
                "dependencies": ["task-002"],
                "blueprint_template": "data-models",
            },
            {
                "id": "task-004",
                "name": "Create API endpoints",
                "phase": "core",
                "estimated_hours": 6,
                "dependencies": ["task-003"],
                "blueprint_template": "api-endpoints",
            },
            {
                "id": "task-005",
                "name": "Implement business logic",
                "phase": "core",
                "estimated_hours": 4,
                "dependencies": ["task-003"],
                "blueprint_template": None,
            },
            {
                "id": "task-006",
                "name": "Add authentication",
                "phase": "features",
                "estimated_hours": 8,
                "dependencies": ["task-004"],
                "blueprint_template": "auth-system",
            },
            {
                "id": "task-007",
                "name": "Implement additional features",
                "phase": "features",
                "estimated_hours": 16,
                "dependencies": ["task-004", "task-005"],
                "blueprint_template": None,
            },
            {
                "id": "task-008",
                "name": "Write unit tests",
                "phase": "testing",
                "estimated_hours": 4,
                "dependencies": ["task-005", "task-007"],
                "blueprint_template": "test-suite",
            },
            {
                "id": "task-009",
                "name": "Integration testing",
                "phase": "testing",
                "estimated_hours": 4,
                "dependencies": ["task-008"],
                "blueprint_template": None,
            },
            {
                "id": "task-010",
                "name": "Setup CI/CD pipeline",
                "phase": "deployment",
                "estimated_hours": 4,
                "dependencies": ["task-009"],
                "blueprint_template": "cicd-pipeline",
            },
        ]

        return {
            "project_name": f"new-{project_type}-service",
            "phases": phases,
            "tasks": tasks,
            "total_hours": sum(p["estimated_hours"] for p in phases),
            "critical_path": ["task-001", "task-002", "task-003", "task-004", "task-006"],
            "technology_decisions": {
                "language": tech_stack.get("language", "python"),
                "framework": tech_stack.get("framework", "fastapi"),
                "database": tech_stack.get("database", "postgresql"),
                "deployment": tech_stack.get("deployment", "kubernetes"),
            },
            "model_used": model,
            "complexity_assessment": "Analyzed and planned based on requirements",
        }
