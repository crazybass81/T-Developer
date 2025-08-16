"""WorkflowComposer - Automatic workflow configuration for agent orchestration."""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("meta_agents.workflow_composer")


@dataclass
class WorkflowConfig:
    """Configuration for workflow composition."""

    max_parallel_tasks: int = 5
    enable_optimization: bool = True
    resource_limits: dict[str, Any] = field(
        default_factory=lambda: {"cpu": 4, "memory_gb": 8, "time_minutes": 60}
    )
    retry_policy: dict[str, Any] = field(
        default_factory=lambda: {"max_retries": 3, "backoff_seconds": 30}
    )


@dataclass
class WorkflowStep:
    """Individual step in a workflow."""

    id: str
    name: str
    agent: str
    dependencies: list[str] = field(default_factory=list)
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    estimated_duration: int = 30  # minutes
    resource_requirements: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate step configuration."""
        if not self.id or not self.name or not self.agent:
            return False
        return True


class Parallelizer:
    """Manages parallel execution of workflow tasks."""

    def identify_parallel_tasks(self, tasks: list[dict[str, Any]]) -> list[list[str]]:
        """Identify tasks that can run in parallel."""
        task_map = {task["id"]: task for task in tasks}
        parallel_groups = []
        processed = set()

        while len(processed) < len(tasks):
            # Find tasks with no unprocessed dependencies
            ready_tasks = []
            for task in tasks:
                if task["id"] in processed:
                    continue

                deps_ready = all(dep in processed for dep in task.get("dependencies", []))
                if deps_ready:
                    ready_tasks.append(task["id"])

            if not ready_tasks:
                # Handle circular dependencies
                remaining = [t["id"] for t in tasks if t["id"] not in processed]
                if remaining:
                    ready_tasks = [remaining[0]]

            parallel_groups.append(ready_tasks)
            processed.update(ready_tasks)

        return parallel_groups

    def optimize_execution_order(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Optimize task execution order for efficiency."""
        # Sort by estimated time (shortest first for better parallelization)
        independent_tasks = [t for t in tasks if not t.get("dependencies")]
        dependent_tasks = [t for t in tasks if t.get("dependencies")]

        # Sort independent tasks by duration
        independent_tasks.sort(key=lambda x: x.get("estimated_time", 30))

        # Sort dependent tasks by priority and duration
        dependent_tasks.sort(
            key=lambda x: (len(x.get("dependencies", [])), x.get("estimated_time", 30))
        )

        return independent_tasks + dependent_tasks

    def calculate_critical_path(self, workflow: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Calculate the critical path through the workflow."""
        # Calculate earliest start times
        earliest_start = {}

        def calculate_earliest_start(task_id: str) -> int:
            if task_id in earliest_start:
                return earliest_start[task_id]

            task = workflow[task_id]
            dependencies = task.get("dependencies", [])

            if not dependencies:
                earliest_start[task_id] = 0
            else:
                max_finish_time = max(
                    calculate_earliest_start(dep) + workflow[dep]["duration"]
                    for dep in dependencies
                )
                earliest_start[task_id] = max_finish_time

            return earliest_start[task_id]

        # Calculate all earliest start times
        for task_id in workflow:
            calculate_earliest_start(task_id)

        # Find critical path by following the longest path
        critical_path = []

        # Start with tasks that have no successors (final tasks)
        final_tasks = [
            task_id
            for task_id in workflow
            if not any(task_id in task.get("dependencies", []) for task in workflow.values())
        ]

        if final_tasks:
            # Pick the task with the latest finish time
            final_task = max(final_tasks, key=lambda t: earliest_start[t] + workflow[t]["duration"])

            total_duration = earliest_start[final_task] + workflow[final_task]["duration"]

            # Trace back the critical path
            current = final_task
            while current:
                critical_path.insert(0, current)

                # Find the dependency that determines the earliest start time
                dependencies = workflow[current].get("dependencies", [])
                if dependencies:
                    # Find the dependency with the latest finish time
                    current = max(
                        dependencies, key=lambda d: earliest_start[d] + workflow[d]["duration"]
                    )
                else:
                    current = None

        return {"path": critical_path, "duration": total_duration if final_tasks else 0}


class ResourceAllocator:
    """Manages resource allocation for workflow tasks."""

    def allocate(self, task: dict[str, Any], available_resources: dict[str, Any]) -> dict[str, Any]:
        """Allocate resources for a task."""
        requirements = task.get("requirements", {})
        allocation = {}

        for resource, needed in requirements.items():
            available = available_resources.get(resource, 0)

            if resource == "gpu" and not needed:
                allocation[resource] = 0
            else:
                allocation[resource] = min(needed, available)

        return allocation

    def can_allocate(self, requirements: dict[str, Any], available: dict[str, Any]) -> bool:
        """Check if resources can be allocated for requirements."""
        for resource, needed in requirements.items():
            if available.get(resource, 0) < needed:
                return False
        return True

    def optimize_schedule(
        self, tasks: list[dict[str, Any]], available_resources: dict[str, Any]
    ) -> dict[str, Any]:
        """Optimize task scheduling based on resource constraints."""
        parallel_tasks = []
        sequential_tasks = []
        remaining_resources = available_resources.copy()

        for task in tasks:
            requirements = task.get("requirements", {})

            if self.can_allocate(requirements, remaining_resources):
                parallel_tasks.append(task)
                # Subtract allocated resources
                for resource, needed in requirements.items():
                    remaining_resources[resource] = remaining_resources.get(resource, 0) - needed
            else:
                sequential_tasks.append(task)

        return {
            "parallel": parallel_tasks,
            "sequential": sequential_tasks,
            "remaining_resources": remaining_resources,
        }


class WorkflowComposer:
    """Automatic workflow configuration for agent orchestration."""

    def __init__(self, config: Optional[WorkflowConfig] = None):
        """Initialize workflow composer."""
        self.config = config or WorkflowConfig()
        self.parallelizer = Parallelizer()
        self.resource_allocator = ResourceAllocator()
        self.agent_executor = None  # Will be injected

    async def compose(self, requirements: list[dict[str, Any]]) -> dict[str, Any]:
        """Compose workflow from requirements."""
        workflow_id = f"workflow-{uuid.uuid4().hex[:8]}"

        steps = []
        for i, req in enumerate(requirements):
            step_id = f"step-{i}"

            # Map requirement dependencies to step dependencies
            dependencies = []
            if req.get("depends_on"):
                for dep_req_id in req["depends_on"]:
                    # Find the step index for this requirement
                    for j, other_req in enumerate(requirements):
                        if other_req["id"] == dep_req_id:
                            dependencies.append(f"step-{j}")
                            break

            step = WorkflowStep(
                id=step_id,
                name=req.get("description", f"Step {i+1}"),
                agent=req["agents"][0] if req.get("agents") else "DefaultAgent",
                dependencies=dependencies,
                inputs=req.get("inputs", {}),
                estimated_duration=req.get("estimated_duration", 30),
            )

            steps.append(step)

        workflow = {
            "id": workflow_id,
            "name": f"Generated Workflow {workflow_id}",
            "steps": steps,
            "created_at": asyncio.get_event_loop().time(),
            "status": "created",
        }

        return workflow

    async def validate(self, workflow: dict[str, Any]) -> bool:
        """Validate workflow configuration."""
        steps = workflow.get("steps", [])

        if not steps:
            return False

        # Validate each step
        for step in steps:
            if isinstance(step, WorkflowStep):
                if not step.validate():
                    return False
            elif isinstance(step, dict):
                if not step.get("id") or not step.get("agent"):
                    return False

        # Check for circular dependencies using dependency graph
        step_graph = {}
        for step in steps:
            if isinstance(step, WorkflowStep):
                step_id = step.id
                dependencies = step.dependencies
            else:
                step_id = step["id"]
                dependencies = step.get("dependencies", [])
            step_graph[step_id] = dependencies

        if self._has_circular_dependency_in_graph(step_graph):
            return False

        return True

    def _has_circular_dependency_in_graph(self, graph: dict[str, list[str]]) -> bool:
        """Check for circular dependencies using DFS."""
        visited = set()
        rec_stack = set()

        def dfs(node: str) -> bool:
            if node in rec_stack:
                return True
            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if dfs(neighbor):
                    return True

            rec_stack.remove(node)
            return False

        for node_id in graph:
            if node_id not in visited:
                if dfs(node_id):
                    return True

        return False

    async def optimize(self, workflow: dict[str, Any]) -> dict[str, Any]:
        """Optimize workflow for parallel execution."""
        steps = workflow.get("steps", [])

        # Convert steps to task format for optimization
        tasks = []
        for step in steps:
            if isinstance(step, WorkflowStep):
                task = {
                    "id": step.id,
                    "dependencies": step.dependencies,
                    "estimated_time": step.estimated_duration,
                }
            else:
                task = {
                    "id": step["id"],
                    "dependencies": step.get("dependencies", []),
                    "estimated_time": step.get("estimated_duration", 30),
                }
            tasks.append(task)

        # Identify parallel groups
        parallel_groups = self.parallelizer.identify_parallel_tasks(tasks)

        # Calculate critical path
        workflow_dict = {
            task["id"]: {"duration": task["estimated_time"], "dependencies": task["dependencies"]}
            for task in tasks
        }
        critical_path = self.parallelizer.calculate_critical_path(workflow_dict)

        # Calculate total estimated duration
        estimated_duration = critical_path["duration"]

        optimized = workflow.copy()
        optimized.update(
            {
                "parallel_groups": parallel_groups,
                "critical_path": critical_path,
                "estimated_duration": estimated_duration,
                "optimization_applied": True,
            }
        )

        return optimized

    async def execute(self, workflow: dict[str, Any]) -> dict[str, Any]:
        """Execute workflow with parallel processing."""
        workflow_id = workflow["id"]
        steps = workflow.get("steps", [])

        result = {
            "workflow_id": workflow_id,
            "status": "running",
            "step_results": [],
            "started_at": asyncio.get_event_loop().time(),
        }

        try:
            for step in steps:
                step_result = await self._execute_step(step)
                result["step_results"].append(step_result)

                if step_result.get("status") == "failed":
                    result["status"] = "failed"
                    return result

            result["status"] = "completed"
            result["completed_at"] = asyncio.get_event_loop().time()

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    async def _execute_step(self, step: WorkflowStep) -> dict[str, Any]:
        """Execute a single workflow step."""
        step_id = step.id if isinstance(step, WorkflowStep) else step["id"]
        agent = step.agent if isinstance(step, WorkflowStep) else step["agent"]

        max_retries = self.config.retry_policy["max_retries"]
        backoff = self.config.retry_policy["backoff_seconds"]

        for attempt in range(max_retries + 1):
            try:
                if self.agent_executor:
                    result = await self.agent_executor.execute(agent, step)
                    return {
                        "step_id": step_id,
                        "status": "success",
                        "result": result,
                        "attempt": attempt + 1,
                    }
                else:
                    # Mock execution for testing
                    return {
                        "step_id": step_id,
                        "status": "success",
                        "result": {"output": "simulated"},
                        "attempt": attempt + 1,
                    }

            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Step {step_id} failed (attempt {attempt + 1}), retrying...")
                    await asyncio.sleep(backoff)
                else:
                    logger.error(f"Step {step_id} failed after {max_retries + 1} attempts: {e}")
                    return {
                        "step_id": step_id,
                        "status": "failed",
                        "error": str(e),
                        "attempts": attempt + 1,
                    }

    async def save(self, workflow: dict[str, Any], path: Path) -> None:
        """Save workflow to file."""
        # Convert WorkflowStep objects to dictionaries for JSON serialization
        serializable_workflow = self._make_serializable(workflow)

        with open(path, "w") as f:
            json.dump(serializable_workflow, f, indent=2)

    def _make_serializable(self, obj: Any) -> Any:
        """Make object JSON serializable."""
        if isinstance(obj, WorkflowStep):
            return {
                "id": obj.id,
                "name": obj.name,
                "agent": obj.agent,
                "dependencies": obj.dependencies,
                "inputs": obj.inputs,
                "outputs": obj.outputs,
                "estimated_duration": obj.estimated_duration,
                "resource_requirements": obj.resource_requirements,
            }
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        else:
            return obj

    async def load(self, path: Path) -> dict[str, Any]:
        """Load workflow from file."""
        with open(path) as f:
            workflow = json.load(f)

        # Convert step dictionaries back to WorkflowStep objects if needed
        if "steps" in workflow:
            steps = []
            for step_data in workflow["steps"]:
                if isinstance(step_data, dict):
                    step = WorkflowStep(
                        id=step_data["id"],
                        name=step_data["name"],
                        agent=step_data["agent"],
                        dependencies=step_data.get("dependencies", []),
                        inputs=step_data.get("inputs", {}),
                        outputs=step_data.get("outputs", {}),
                        estimated_duration=step_data.get("estimated_duration", 30),
                        resource_requirements=step_data.get("resource_requirements", {}),
                    )
                    steps.append(step)
                else:
                    steps.append(step_data)

            workflow["steps"] = steps

        return workflow

    async def generate_visualization(self, workflow: dict[str, Any]) -> dict[str, Any]:
        """Generate visualization data for workflow."""
        steps = workflow.get("steps", [])

        nodes = []
        edges = []

        # Create nodes
        for step in steps:
            if isinstance(step, WorkflowStep):
                node = {
                    "id": step.id,
                    "label": step.name,
                    "agent": step.agent,
                    "duration": step.estimated_duration,
                }
            else:
                node = {
                    "id": step["id"],
                    "label": step.get("name", step["id"]),
                    "agent": step.get("agent", "Unknown"),
                    "duration": step.get("estimated_duration", 30),
                }
            nodes.append(node)

        # Create edges
        for step in steps:
            if isinstance(step, WorkflowStep):
                step_id = step.id
                dependencies = step.dependencies
            else:
                step_id = step["id"]
                dependencies = step.get("dependencies", [])

            for dep in dependencies:
                edges.append({"from": dep, "to": step_id})

        return {"graph": "directed", "nodes": nodes, "edges": edges, "workflow_id": workflow["id"]}
