"""
Day 11: Workflow Execution Engine Foundation
Lightweight execution engine for workflow orchestration (< 6.5KB constraint)
"""

import asyncio
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from .dag_validator import DAGValidator
from .parser import WorkflowDefinition, WorkflowStep


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepExecution:
    """Minimal step execution tracker"""

    def __init__(self, step: WorkflowStep):
        self.step_id = step.id
        self.status = ExecutionStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.result = None
        self.error = None

    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class WorkflowEngine:
    """Lightweight workflow execution engine"""

    def __init__(self):
        self.validator = DAGValidator()
        self.executions = {}

    async def execute_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Execute workflow with DAG-based scheduling"""
        execution_id = f"{workflow.id}_{int(time.time())}"

        # Validate workflow
        validation = self.validator.validate_dag(workflow)
        if not validation["is_valid_dag"]:
            return {
                "status": "failed",
                "error": "Invalid DAG",
                "cycles": validation["cycles_detected"],
            }

        # Get execution order
        execution_levels = self.validator.get_execution_order(workflow)

        # Initialize step executions
        step_executions = {step.id: StepExecution(step) for step in workflow.steps}

        execution_result = {
            "execution_id": execution_id,
            "workflow_id": workflow.id,
            "status": "running",
            "start_time": time.time(),
            "levels_completed": 0,
            "total_levels": len(execution_levels),
            "step_results": {},
        }

        try:
            # Execute levels sequentially, steps in parallel
            for level_idx, level_steps in enumerate(execution_levels):
                level_tasks = []

                for step_id in level_steps:
                    step = next(s for s in workflow.steps if s.id == step_id)
                    task = self._execute_step(step, step_executions[step_id])
                    level_tasks.append(task)

                # Wait for all steps in level to complete
                await asyncio.gather(*level_tasks)
                execution_result["levels_completed"] = level_idx + 1

            # Collect results
            for step_id, step_exec in step_executions.items():
                execution_result["step_results"][step_id] = {
                    "status": step_exec.status.value,
                    "duration": step_exec.duration,
                    "result": step_exec.result,
                    "error": step_exec.error,
                }

            execution_result["status"] = "completed"

        except Exception as e:
            execution_result["status"] = "failed"
            execution_result["error"] = str(e)

        execution_result["end_time"] = time.time()
        execution_result["total_duration"] = (
            execution_result["end_time"] - execution_result["start_time"]
        )

        self.executions[execution_id] = execution_result
        return execution_result

    async def _execute_step(self, step: WorkflowStep, step_exec: StepExecution):
        """Execute individual workflow step"""
        step_exec.start_time = time.time()
        step_exec.status = ExecutionStatus.RUNNING

        try:
            # Simulate step execution (placeholder for actual agent/service calls)
            await asyncio.sleep(0.1)  # Simulate work

            step_exec.result = {
                "step_id": step.id,
                "step_type": step.type,
                "outputs": step.outputs,
                "execution_time": datetime.utcnow().isoformat(),
            }
            step_exec.status = ExecutionStatus.COMPLETED

        except Exception as e:
            step_exec.error = str(e)
            step_exec.status = ExecutionStatus.FAILED

        step_exec.end_time = time.time()

    def get_execution_status(self, execution_id: str):
        """Get execution status"""
        return self.executions.get(execution_id)

    def list_executions(self) -> List[Dict]:
        """List all executions"""
        return [
            {
                "execution_id": k,
                "workflow_id": v["workflow_id"],
                "status": v["status"],
                "duration": v.get("total_duration", 0),
            }
            for k, v in self.executions.items()
        ]


if __name__ == "__main__":
    # Example usage
    from .parser import SAMPLE_WORKFLOWS, WorkflowParser

    async def test_engine():
        parser = WorkflowParser()
        engine = WorkflowEngine()

        workflow = parser.parse_dict(SAMPLE_WORKFLOWS["data_processing"])
        result = await engine.execute_workflow(workflow)

        print(f"Execution: {result['status']}")
        print(f"Duration: {result['total_duration']:.2f}s")
        print(f"Steps: {len(result['step_results'])}")

    asyncio.run(test_engine())
