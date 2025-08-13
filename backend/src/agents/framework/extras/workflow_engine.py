# backend/src/agents/framework/workflow_engine.py
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import uuid
from datetime import datetime


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


@dataclass
class WorkflowStep:
    id: str
    name: str
    type: StepType
    agent_id: str
    action: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any] = None
    condition: Optional[str] = None
    dependencies: List[str] = None
    timeout: int = 300


@dataclass
class Workflow:
    id: str
    name: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = None


class WorkflowEngine:
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.step_handlers: Dict[str, Callable] = {}
        self.running_workflows: Dict[str, asyncio.Task] = {}

    def register_step_handler(self, action: str, handler: Callable):
        self.step_handlers[action] = handler

    async def create_workflow(self, name: str, steps: List[WorkflowStep]) -> str:
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            id=workflow_id, name=name, steps=steps, created_at=datetime.utcnow()
        )
        self.workflows[workflow_id] = workflow
        return workflow_id

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.status = WorkflowStatus.RUNNING
        task = asyncio.create_task(self._run_workflow(workflow))
        self.running_workflows[workflow_id] = task

        try:
            results = await task
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()
            workflow.results = results
            return results
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            raise e
        finally:
            self.running_workflows.pop(workflow_id, None)

    async def _run_workflow(self, workflow: Workflow) -> Dict[str, Any]:
        results = {}
        step_results = {}

        # Build dependency graph
        dependency_graph = self._build_dependency_graph(workflow.steps)
        execution_order = self._topological_sort(dependency_graph)

        for step_id in execution_order:
            step = next(s for s in workflow.steps if s.id == step_id)

            # Check condition
            if step.condition and not self._evaluate_condition(
                step.condition, step_results
            ):
                continue

            # Execute step
            handler = self.step_handlers.get(step.action)
            if handler:
                try:
                    result = await asyncio.wait_for(
                        handler(step.inputs, step_results), timeout=step.timeout
                    )
                    step_results[step_id] = result
                    step.outputs = result
                except asyncio.TimeoutError:
                    raise Exception(f"Step {step_id} timed out")

        return step_results

    def _build_dependency_graph(
        self, steps: List[WorkflowStep]
    ) -> Dict[str, List[str]]:
        graph = {step.id: step.dependencies or [] for step in steps}
        return graph

    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        visited = set()
        temp_visited = set()
        result = []

        def visit(node):
            if node in temp_visited:
                raise Exception("Circular dependency detected")
            if node not in visited:
                temp_visited.add(node)
                for dep in graph.get(node, []):
                    visit(dep)
                temp_visited.remove(node)
                visited.add(node)
                result.append(node)

        for node in graph:
            if node not in visited:
                visit(node)

        return result

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        # Simple condition evaluation
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False
