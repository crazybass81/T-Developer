"""Planner Agent - Creates hierarchical execution plans from research data."""

import json
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional

from packages.agents.base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent

logger = logging.getLogger("agents.planner")


@dataclass
class Task:
    """Represents a single task in the plan."""

    id: str
    name: str
    description: str
    estimated_hours: float
    dependencies: list[str]  # Task IDs this depends on
    priority: str  # high, medium, low
    category: str  # dev, test, docs, refactor, etc.
    status: str = "pending"  # pending, in_progress, completed
    assigned_to: Optional[str] = None
    actual_hours: Optional[float] = None
    completion_date: Optional[datetime] = None

    def can_start_after(self, completed_tasks: list[str]) -> bool:
        """Check if task can start given completed tasks."""
        return all(dep in completed_tasks for dep in self.dependencies)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "estimated_hours": self.estimated_hours,
            "dependencies": self.dependencies,
            "priority": self.priority,
            "category": self.category,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "actual_hours": self.actual_hours,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
        }


@dataclass
class Milestone:
    """Represents a project milestone."""

    id: str
    name: str
    tasks: list[str]  # Task IDs in this milestone
    deadline: datetime
    success_criteria: list[str] = field(default_factory=list)
    completed_tasks: list[str] = field(default_factory=list)

    @property
    def progress(self) -> float:
        """Calculate progress percentage."""
        if not self.tasks:
            return 0.0
        return (len(self.completed_tasks) / len(self.tasks)) * 100

    @property
    def is_complete(self) -> bool:
        """Check if milestone is complete."""
        return set(self.completed_tasks) == set(self.tasks)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "tasks": self.tasks,
            "deadline": self.deadline.isoformat(),
            "success_criteria": self.success_criteria,
            "completed_tasks": self.completed_tasks,
            "progress": self.progress,
            "is_complete": self.is_complete,
        }


@dataclass
class Plan:
    """Represents a complete execution plan."""

    id: str
    goal: str
    tasks: list[Task]
    milestones: list[Milestone]
    total_estimated_hours: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate plan consistency."""
        # Check for circular dependencies
        task_dict = {t.id: t for t in self.tasks}
        visited = set()
        rec_stack = set()

        def has_cycle(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            task = task_dict.get(task_id)
            if task:
                for dep in task.dependencies:
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        return True

            rec_stack.remove(task_id)
            return False

        for task in self.tasks:
            if task.id not in visited:
                if has_cycle(task.id):
                    return False

        return True

    def get_critical_path(self) -> list[str]:
        """Find critical path through tasks."""
        if not self.tasks:
            return []

        # Build adjacency list
        graph = {t.id: t.dependencies for t in self.tasks}
        times = {t.id: t.estimated_hours for t in self.tasks}

        # Find tasks with no dependencies (start nodes)
        start_tasks = [t.id for t in self.tasks if not t.dependencies]
        if not start_tasks:
            return []

        # Calculate longest path
        longest_path = []
        max_time = 0

        def dfs(task_id: str, path: list[str], time: float):
            nonlocal longest_path, max_time

            path.append(task_id)
            time += times.get(task_id, 0)

            # Find tasks that depend on current task
            dependents = [t.id for t in self.tasks if task_id in t.dependencies]

            if not dependents:
                if time > max_time:
                    max_time = time
                    longest_path = path.copy()
            else:
                for dep in dependents:
                    dfs(dep, path.copy(), time)

        for start in start_tasks:
            dfs(start, [], 0)

        return longest_path

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "goal": self.goal,
            "tasks": [t.to_dict() for t in self.tasks],
            "milestones": [m.to_dict() for m in self.milestones],
            "total_estimated_hours": self.total_estimated_hours,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
            "critical_path": self.get_critical_path(),
            "is_valid": self.validate(),
        }


@dataclass
class PlannerConfig:
    """Configuration for planner agent."""

    max_hours_per_task: float = 4.0  # Maximum hours for a single task
    min_hours_per_task: float = 0.5  # Minimum hours for a single task
    buffer_percentage: int = 20  # Buffer to add to time estimates
    parallel_tasks_limit: int = 3  # Max parallel tasks
    enable_ai_planning: bool = True
    ai_model: str = "claude-3-sonnet"
    use_historical_data: bool = True
    planning_horizon_days: int = 30


class TaskDecomposer:
    """Decomposes goals into executable tasks."""

    def decompose(
        self, goal: str, research_data: dict[str, Any], max_hours_per_task: float = 4.0
    ) -> list[Task]:
        """Decompose goal into tasks based on research data.

        Args:
            goal: High-level goal
            research_data: Data from research agent
            max_hours_per_task: Maximum hours per task

        Returns:
            List of tasks
        """
        tasks = []

        # Extract improvements from research
        improvements = research_data.get("improvements", [])
        references = research_data.get("external_references", {})
        recommendations = references.get("recommendations", {})

        # Check for migration steps in recommendations
        migration_steps = recommendations.get("migration_steps", [])

        if migration_steps:
            # Create tasks from migration steps
            for i, step in enumerate(migration_steps):
                task = Task(
                    id=f"task-{uuid.uuid4().hex[:8]}",
                    name=step,
                    description=f"Migration step: {step}",
                    estimated_hours=min(4.0, 8.0 / len(migration_steps)),
                    dependencies=[f"task-{i-1}"] if i > 0 else [],
                    priority="high" if i == 0 else "medium",
                    category="migration",
                )
                tasks.append(task)

        # Create tasks from improvements
        for i, improvement in enumerate(improvements):
            task_id = f"task-{uuid.uuid4().hex[:8]}"

            # Determine task details from improvement
            task_type = improvement.get("type", "refactor")
            location = improvement.get("location", "unknown")
            priority = improvement.get("priority", "medium")

            task = Task(
                id=task_id,
                name=f"{task_type.title()} - {location}",
                description=improvement.get("suggestion", f"Apply {task_type} to {location}"),
                estimated_hours=self._estimate_task_hours(improvement),
                dependencies=[],  # Will be set by dependency analyzer
                priority=priority,
                category=task_type,
            )

            # Split if exceeds max hours
            if task.estimated_hours > max_hours_per_task:
                subtasks = self._split_task(task, max_hours_per_task)
                tasks.extend(subtasks)
            else:
                tasks.append(task)

        # If no specific tasks, create generic ones based on goal
        if not tasks:
            tasks = self._create_generic_tasks(goal, max_hours_per_task)

        return tasks

    def _estimate_task_hours(self, improvement: dict[str, Any]) -> float:
        """Estimate hours for a task."""
        # Simple heuristic based on type
        type_hours = {
            "refactor": 3.0,
            "test": 2.0,
            "docs": 1.0,
            "logging": 1.5,
            "security": 4.0,
            "performance": 3.5,
            "migration": 4.0,
        }

        task_type = improvement.get("type", "refactor")
        base_hours = type_hours.get(task_type, 2.0)

        # Adjust based on complexity
        complexity = improvement.get("complexity", "medium")
        if complexity == "high":
            base_hours *= 1.5
        elif complexity == "low":
            base_hours *= 0.7

        return round(base_hours, 1)

    def _split_task(self, task: Task, max_hours: float) -> list[Task]:
        """Split a large task into smaller subtasks."""
        subtasks = []
        num_parts = int(task.estimated_hours / max_hours) + 1
        hours_per_part = task.estimated_hours / num_parts

        for i in range(num_parts):
            subtask = Task(
                id=f"{task.id}-{i+1}",
                name=f"{task.name} (Part {i+1}/{num_parts})",
                description=f"{task.description} - Part {i+1} of {num_parts}",
                estimated_hours=round(hours_per_part, 1),
                dependencies=[] if i == 0 else [f"{task.id}-{i}"],
                priority=task.priority,
                category=task.category,
            )
            subtasks.append(subtask)

        return subtasks

    def _create_generic_tasks(self, goal: str, max_hours: float) -> list[Task]:
        """Create generic tasks when no specific improvements found."""
        return [
            Task(
                id=f"task-{uuid.uuid4().hex[:8]}",
                name="Analyze current state",
                description=f"Analyze current state for: {goal}",
                estimated_hours=2.0,
                dependencies=[],
                priority="high",
                category="analysis",
            ),
            Task(
                id=f"task-{uuid.uuid4().hex[:8]}",
                name="Design solution",
                description=f"Design solution for: {goal}",
                estimated_hours=3.0,
                dependencies=[],
                priority="high",
                category="design",
            ),
            Task(
                id=f"task-{uuid.uuid4().hex[:8]}",
                name="Implement changes",
                description=f"Implement: {goal}",
                estimated_hours=4.0,
                dependencies=[],
                priority="medium",
                category="development",
            ),
            Task(
                id=f"task-{uuid.uuid4().hex[:8]}",
                name="Test and validate",
                description=f"Test implementation of: {goal}",
                estimated_hours=2.0,
                dependencies=[],
                priority="high",
                category="testing",
            ),
        ]


class TimeEstimator:
    """Estimates time for tasks."""

    def estimate(
        self,
        task_data: dict[str, Any],
        historical_data: Optional[list[dict[str, Any]]] = None,
        buffer_percentage: int = 0,
    ) -> float:
        """Estimate time for a task.

        Args:
            task_data: Task information
            historical_data: Historical task data
            buffer_percentage: Buffer to add

        Returns:
            Estimated hours
        """
        base_hours = 2.0  # Default

        # Use historical data if available
        if historical_data:
            similar_tasks = [h for h in historical_data if h.get("type") == task_data.get("type")]

            if similar_tasks:
                # Interpolate based on scope
                task_files = task_data.get("files", 1)
                estimates = []

                for hist in similar_tasks:
                    hist_files = hist.get("files", 1)
                    hist_hours = hist.get("actual_hours", 2)

                    # Linear interpolation
                    estimated = (task_files / hist_files) * hist_hours
                    estimates.append(estimated)

                base_hours = sum(estimates) / len(estimates)
        else:
            # Heuristic estimation
            task_type = task_data.get("type", "unknown")
            complexity = task_data.get("complexity", "medium")

            type_hours = {
                "refactoring": 3.0,
                "testing": 2.5,
                "documentation": 1.5,
                "feature": 4.0,
                "bugfix": 2.0,
                "optimization": 3.5,
                "unknown": 2.0,
            }

            base_hours = type_hours.get(task_type, 2.0)

            # Adjust for complexity
            if complexity == "high":
                base_hours *= 1.5
            elif complexity == "low":
                base_hours *= 0.7

        # Add buffer
        if buffer_percentage > 0:
            base_hours *= 1 + buffer_percentage / 100

        return round(base_hours, 1)


class DependencyAnalyzer:
    """Analyzes and sets task dependencies."""

    def analyze(
        self, tasks: list[Task], file_dependencies: Optional[dict[str, list[str]]] = None
    ) -> None:
        """Analyze and set task dependencies.

        Args:
            tasks: List of tasks to analyze
            file_dependencies: File dependency graph
        """
        if not file_dependencies:
            # Simple sequential dependencies for now
            for i in range(1, len(tasks)):
                # Some tasks can be parallel
                if tasks[i].category != tasks[i - 1].category:
                    tasks[i].dependencies = []
                else:
                    tasks[i].dependencies = [tasks[i - 1].id]
            return

        # Map tasks to files they affect
        task_files = {}
        for task in tasks:
            # Extract file from task name/description
            files = self._extract_files(task.name + " " + task.description)
            task_files[task.id] = files

        # Set dependencies based on file dependencies
        for i, task in enumerate(tasks):
            task_deps = []
            my_files = task_files.get(task.id, [])

            # If no files extracted from task, try to find them in description
            if not my_files and "test" in task.name.lower():
                # For test tasks, they depend on the files being tested
                my_files = ["tests/test_derived.py"]  # Default test file
                task_files[task.id] = my_files

            for j, other in enumerate(tasks[:i]):
                other_files = task_files.get(other.id, [])

                # Check if any of my files depend on other's files
                for my_file in my_files:
                    deps = file_dependencies.get(my_file, [])
                    if any(dep in other_files for dep in deps):
                        task_deps.append(other.id)
                        break

                    # Also check if the file itself is in other_files
                    for dep in deps:
                        if dep in other_files:
                            task_deps.append(other.id)
                            break

            task.dependencies = task_deps

    def _extract_files(self, text: str) -> list[str]:
        """Extract file names from text."""
        # Simple pattern matching for .py, .js, .ts files
        pattern = r"\b(\w+\.(?:py|js|ts|jsx|tsx))\b"
        return re.findall(pattern, text)

    def has_circular_dependency(self, deps: dict[str, list[str]]) -> bool:
        """Check for circular dependencies.

        Args:
            deps: Dependency graph

        Returns:
            True if circular dependency exists
        """
        visited = set()
        rec_stack = set()

        def visit(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in deps.get(node, []):
                if neighbor not in visited:
                    if visit(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in deps:
            if node not in visited:
                if visit(node):
                    return True

        return False

    def topological_sort(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks in topological order.

        Args:
            tasks: List of tasks

        Returns:
            Topologically sorted tasks
        """
        # Create a mapping from task ID to task
        task_map = {t.id: t for t in tasks}

        # Build reverse adjacency list (task -> tasks that depend on it)
        dependents = {t.id: [] for t in tasks}
        in_degree = {t.id: len(t.dependencies) for t in tasks}

        for task in tasks:
            for dep in task.dependencies:
                if dep in dependents:
                    dependents[dep].append(task.id)

        # Find tasks with no dependencies (can start immediately)
        queue = [t for t in tasks if in_degree[t.id] == 0]
        sorted_tasks = []

        while queue:
            # Sort by priority for tasks at same level
            queue.sort(
                key=lambda t: ({"high": 0, "medium": 1, "low": 2}.get(t.priority, 3), t.name)
            )

            task = queue.pop(0)
            sorted_tasks.append(task)

            # Update in-degrees for dependent tasks
            for dependent_id in dependents[task.id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(task_map[dependent_id])

        return sorted_tasks


class PlannerAgent(BaseAgent):
    """Agent that creates execution plans from research data."""

    def __init__(self, name: str, config: Optional[PlannerConfig] = None):
        """Initialize planner agent.

        Args:
            name: Agent name
            config: Planner configuration
        """
        super().__init__(name, {"timeout": 300})
        self.config = config or PlannerConfig()
        self.decomposer = TaskDecomposer()
        self.estimator = TimeEstimator()
        self.analyzer = DependencyAnalyzer()

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Create execution plan.

        Args:
            input: Agent input with goal and research data

        Returns:
            Execution plan
        """
        try:
            goal = input.payload.get("goal", "")
            research_data = input.payload.get("research_data", {})
            constraints = input.payload.get("constraints", {})

            # Decompose goal into tasks
            tasks = self.decomposer.decompose(goal, research_data, self.config.max_hours_per_task)

            # Estimate time for each task
            historical_data = None
            if self.config.use_historical_data:
                historical_data = self._load_historical_data()

            for task in tasks:
                if task.estimated_hours == 0:
                    task.estimated_hours = self.estimator.estimate(
                        {"type": task.category, "complexity": "medium"},
                        historical_data,
                        self.config.buffer_percentage,
                    )

            # Analyze dependencies
            file_deps = research_data.get("file_dependencies")
            self.analyzer.analyze(tasks, file_deps)

            # Sort tasks
            sorted_tasks = self.analyzer.topological_sort(tasks)

            # Create milestones
            milestones = self._create_milestones(sorted_tasks, constraints)

            # Calculate total time
            total_hours = sum(t.estimated_hours for t in sorted_tasks)

            # Apply constraints
            max_hours = constraints.get("max_hours")
            if max_hours and total_hours > max_hours:
                sorted_tasks = self._prioritize_tasks(sorted_tasks, max_hours)
                total_hours = sum(t.estimated_hours for t in sorted_tasks)

            # Create plan
            plan = Plan(
                id=f"plan-{uuid.uuid4().hex[:8]}",
                goal=goal,
                tasks=sorted_tasks,
                milestones=milestones,
                total_estimated_hours=total_hours,
                created_at=datetime.now(),
                metadata={
                    "research_summary": research_data.get("summary", {}),
                    "constraints": constraints,
                },
            )

            # Validate plan
            if not plan.validate():
                logger.warning("Plan has circular dependencies, attempting to fix")
                plan = self._fix_circular_dependencies(plan)

            # Use AI for plan enhancement if enabled
            if self.config.enable_ai_planning and input.payload.get("use_ai"):
                plan = await self._enhance_with_ai(plan)

            # Create output
            plan_artifact = Artifact(kind="plan", ref=f"{plan.id}.json", content=plan.to_dict())

            # Create Gantt chart artifact
            gantt_artifact = Artifact(
                kind="visualization",
                ref=f"{plan.id}-gantt.json",
                content=self._create_gantt_data(plan),
            )

            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.OK,
                artifacts=[plan_artifact, gantt_artifact],
                metrics={
                    "tasks_created": len(sorted_tasks),
                    "total_hours": total_hours,
                    "milestones": len(milestones),
                    "critical_path_length": len(plan.get_critical_path()),
                },
            )

        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return AgentOutput(task_id=input.task_id, status=AgentStatus.FAIL, error=str(e))

    def _create_milestones(self, tasks: list[Task], constraints: dict[str, Any]) -> list[Milestone]:
        """Create milestones from tasks and constraints.

        Args:
            tasks: List of tasks
            constraints: Planning constraints

        Returns:
            List of milestones
        """
        milestones = []

        # Check for explicit milestones in constraints
        if "milestones" in constraints:
            for m_data in constraints["milestones"]:
                milestone = Milestone(
                    id=f"m-{uuid.uuid4().hex[:8]}",
                    name=m_data["name"],
                    tasks=[],  # Will be assigned
                    deadline=datetime.fromisoformat(m_data["deadline"])
                    if isinstance(m_data["deadline"], str)
                    else m_data["deadline"],
                    success_criteria=m_data.get("criteria", []),
                )
                milestones.append(milestone)
        else:
            # Auto-create milestones based on task categories
            categories = list(set(t.category for t in tasks))
            base_date = datetime.now()

            for i, category in enumerate(categories):
                cat_tasks = [t.id for t in tasks if t.category == category]
                milestone = Milestone(
                    id=f"m-{uuid.uuid4().hex[:8]}",
                    name=f"{category.title()} Complete",
                    tasks=cat_tasks,
                    deadline=base_date + timedelta(days=(i + 1) * 7),
                    success_criteria=[f"All {category} tasks completed"],
                )
                milestones.append(milestone)

        # Assign tasks to milestones if not already assigned
        if milestones and not milestones[0].tasks:
            tasks_per_milestone = len(tasks) // len(milestones)
            for i, milestone in enumerate(milestones):
                start_idx = i * tasks_per_milestone
                end_idx = start_idx + tasks_per_milestone if i < len(milestones) - 1 else len(tasks)
                milestone.tasks = [t.id for t in tasks[start_idx:end_idx]]

        return milestones

    def _prioritize_tasks(self, tasks: list[Task], max_hours: float) -> list[Task]:
        """Prioritize tasks to fit within time constraint.

        Args:
            tasks: List of tasks
            max_hours: Maximum hours available

        Returns:
            Prioritized list of tasks
        """
        # Sort by priority and dependencies
        priority_order = {"high": 0, "medium": 1, "low": 2}
        tasks.sort(key=lambda t: (priority_order.get(t.priority, 3), len(t.dependencies)))

        selected = []
        total = 0

        for task in tasks:
            if total + task.estimated_hours <= max_hours:
                selected.append(task)
                total += task.estimated_hours
            elif task.priority == "high":
                # Try to include high priority by removing low priority
                low_priority = [t for t in selected if t.priority == "low"]
                if low_priority:
                    removed = low_priority[0]
                    selected.remove(removed)
                    total -= removed.estimated_hours
                    if total + task.estimated_hours <= max_hours:
                        selected.append(task)
                        total += task.estimated_hours

        return selected

    def _fix_circular_dependencies(self, plan: Plan) -> Plan:
        """Fix circular dependencies in plan.

        Args:
            plan: Plan with circular dependencies

        Returns:
            Fixed plan
        """
        # Simple fix: remove dependencies that create cycles
        for task in plan.tasks:
            if task.dependencies:
                # Keep only first dependency to break cycles
                task.dependencies = task.dependencies[:1]

        return plan

    def _create_gantt_data(self, plan: Plan) -> dict[str, Any]:
        """Create Gantt chart data from plan.

        Args:
            plan: Execution plan

        Returns:
            Gantt chart data
        """
        gantt_data = {"title": plan.goal, "tasks": [], "milestones": []}

        # Calculate start dates for tasks
        start_date = datetime.now()
        task_dates = {}

        for task in plan.tasks:
            deps_complete = start_date
            if task.dependencies:
                # Find latest dependency completion
                for dep_id in task.dependencies:
                    if dep_id in task_dates:
                        dep_end = task_dates[dep_id]["end"]
                        if dep_end > deps_complete:
                            deps_complete = dep_end

            task_start = deps_complete
            task_end = task_start + timedelta(hours=task.estimated_hours)

            task_dates[task.id] = {"start": task_start, "end": task_end}

            gantt_data["tasks"].append(
                {
                    "id": task.id,
                    "name": task.name,
                    "start": task_start.isoformat(),
                    "end": task_end.isoformat(),
                    "progress": 0,
                    "dependencies": task.dependencies,
                }
            )

        # Add milestones
        for milestone in plan.milestones:
            gantt_data["milestones"].append(
                {
                    "id": milestone.id,
                    "name": milestone.name,
                    "date": milestone.deadline.isoformat(),
                    "tasks": milestone.tasks,
                }
            )

        return gantt_data

    def _load_historical_data(self) -> Optional[list[dict[str, Any]]]:
        """Load historical task data.

        Returns:
            Historical data or None
        """
        # Would load from database or file
        # For now, return sample data
        return [
            {"type": "refactoring", "files": 5, "actual_hours": 4},
            {"type": "testing", "files": 10, "actual_hours": 3},
            {"type": "documentation", "files": 3, "actual_hours": 1.5},
        ]

    async def _enhance_with_ai(self, plan: Plan) -> Plan:
        """Enhance plan using AI.

        Args:
            plan: Initial plan

        Returns:
            Enhanced plan
        """
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            prompt = f"""Review and enhance this execution plan:

Goal: {plan.goal}
Tasks: {len(plan.tasks)}
Total Hours: {plan.total_estimated_hours}

Current tasks:
{json.dumps([t.to_dict() for t in plan.tasks[:10]], indent=2)}

Please suggest:
1. Missing tasks
2. Better time estimates
3. Optimal task ordering
4. Risk mitigation steps

Return as JSON with keys: missing_tasks, time_adjustments, ordering_changes, risks"""

            response = await client.messages.create(
                model=self.config.ai_model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            suggestions = json.loads(response.content[0].text)

            # Apply suggestions (simplified)
            if suggestions.get("missing_tasks"):
                # Would add missing tasks
                pass

            return plan

        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")
            return plan

    async def validate(self, output: AgentOutput) -> bool:
        """Validate planner output.

        Args:
            output: Output to validate

        Returns:
            True if valid
        """
        if output.status != AgentStatus.OK:
            return False

        if not output.artifacts:
            return False

        # Check for plan artifact
        plan_artifact = next(
            (a for a in output.artifacts if isinstance(a, dict) and a.get("kind") == "plan"), None
        )

        if not plan_artifact:
            return False

        # Validate plan content
        plan = plan_artifact.get("content", {})
        required_fields = ["goal", "tasks", "total_estimated_hours"]

        return all(field in plan for field in required_fields)

    def get_capabilities(self) -> dict[str, Any]:
        """Get agent capabilities.

        Returns:
            Capabilities dictionary
        """
        return {
            "name": self.name,
            "version": "1.0.0",
            "supported_intents": ["plan", "schedule", "organize"],
            "features": [
                "task_decomposition",
                "time_estimation",
                "dependency_analysis",
                "milestone_creation",
                "gantt_visualization",
                "critical_path_analysis",
            ],
            "max_hours_per_task": self.config.max_hours_per_task,
            "buffer_percentage": self.config.buffer_percentage,
            "ai_enabled": self.config.enable_ai_planning,
        }
