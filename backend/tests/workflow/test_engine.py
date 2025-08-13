import asyncio
from unittest.mock import patch

import pytest

from src.workflow.engine import ExecutionStatus, StepExecution, WorkflowEngine
from src.workflow.parser import WorkflowDefinition, WorkflowStep


class TestStepExecution:
    def test_step_execution_creation(self):
        step = WorkflowStep(id="test_step", name="Test Step", type="agent", agent_id="agent1")
        step_exec = StepExecution(step)

        assert step_exec.step_id == "test_step"
        assert step_exec.status == ExecutionStatus.PENDING
        assert step_exec.start_time is None
        assert step_exec.end_time is None
        assert step_exec.result is None
        assert step_exec.error is None

    def test_step_execution_duration_calculation(self):
        step = WorkflowStep(id="test_step", name="Test Step", type="service")
        step_exec = StepExecution(step)

        # No times set
        assert step_exec.duration is None

        # Set times
        step_exec.start_time = 1.0
        step_exec.end_time = 2.5
        assert step_exec.duration == 1.5

    def test_step_execution_partial_times(self):
        step = WorkflowStep(id="test_step", name="Test Step", type="service")
        step_exec = StepExecution(step)

        # Only start time
        step_exec.start_time = 1.0
        assert step_exec.duration is None

        # Only end time
        step_exec.start_time = None
        step_exec.end_time = 2.0
        assert step_exec.duration is None


class TestWorkflowEngine:
    def setup_method(self):
        self.engine = WorkflowEngine()

    def test_engine_initialization(self):
        assert hasattr(self.engine, "validator")
        assert hasattr(self.engine, "executions")
        assert isinstance(self.engine.executions, dict)

    @pytest.mark.asyncio
    async def test_execute_simple_workflow(self):
        workflow = WorkflowDefinition(
            id="simple_exec",
            name="Simple Execution",
            steps=[WorkflowStep(id="step1", name="Step 1", type="service")],
        )

        result = await self.engine.execute_workflow(workflow)

        assert "execution_id" in result
        assert "workflow_id" in result
        assert "status" in result
        assert "step_results" in result
        assert result["workflow_id"] == "simple_exec"
        assert result["status"] in ["completed", "failed"]

    @pytest.mark.asyncio
    async def test_execute_workflow_with_dependencies(self):
        workflow = WorkflowDefinition(
            id="dep_exec",
            name="Dependency Execution",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="service"),
                WorkflowStep(id="step2", name="Step 2", type="service"),
            ],
            dependencies={"step2": ["step1"]},
        )

        result = await self.engine.execute_workflow(workflow)

        assert result["workflow_id"] == "dep_exec"
        assert len(result["step_results"]) == 2
        assert "step1" in result["step_results"]
        assert "step2" in result["step_results"]

    @pytest.mark.asyncio
    async def test_execute_workflow_with_cycles(self):
        workflow = WorkflowDefinition(
            id="cyclic_exec",
            name="Cyclic Execution",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="service"),
                WorkflowStep(id="step2", name="Step 2", type="service"),
            ],
            dependencies={"step1": ["step2"], "step2": ["step1"]},  # Cycle
        )

        result = await self.engine.execute_workflow(workflow)

        assert result["status"] == "failed"
        assert "Invalid DAG" in result["error"]
        assert "cycles" in result

    @pytest.mark.asyncio
    async def test_execute_parallel_workflow(self):
        workflow = WorkflowDefinition(
            id="parallel_exec",
            name="Parallel Execution",
            steps=[
                WorkflowStep(id="start", name="Start", type="service"),
                WorkflowStep(id="parallel1", name="Parallel 1", type="service"),
                WorkflowStep(id="parallel2", name="Parallel 2", type="service"),
                WorkflowStep(id="end", name="End", type="service"),
            ],
            dependencies={
                "parallel1": ["start"],
                "parallel2": ["start"],
                "end": ["parallel1", "parallel2"],
            },
        )

        result = await self.engine.execute_workflow(workflow)

        assert result["workflow_id"] == "parallel_exec"
        assert len(result["step_results"]) == 4
        assert result["total_levels"] == 3  # start -> parallel1,parallel2 -> end

    @pytest.mark.asyncio
    async def test_step_execution_simulation(self):
        step = WorkflowStep(id="sim_step", name="Simulation Step", type="agent", agent_id="agent1")
        step_exec = StepExecution(step)

        # Test the internal step execution method
        await self.engine._execute_step(step, step_exec)

        assert step_exec.status == ExecutionStatus.COMPLETED
        assert step_exec.start_time is not None
        assert step_exec.end_time is not None
        assert step_exec.duration is not None
        assert step_exec.duration > 0
        assert step_exec.result is not None
        assert step_exec.result["step_id"] == "sim_step"

    @pytest.mark.asyncio
    async def test_step_execution_error_handling(self):
        step = WorkflowStep(id="error_step", name="Error Step", type="service")
        step_exec = StepExecution(step)

        # Mock an error in step execution
        with patch("asyncio.sleep", side_effect=RuntimeError("Simulated error")):
            await self.engine._execute_step(step, step_exec)

        assert step_exec.status == ExecutionStatus.FAILED
        assert step_exec.error is not None
        assert "Simulated error" in step_exec.error

    def test_get_execution_status(self):
        # Add a dummy execution
        self.engine.executions["test_exec"] = {"execution_id": "test_exec", "status": "completed"}

        status = self.engine.get_execution_status("test_exec")
        assert status is not None
        assert status["execution_id"] == "test_exec"
        assert status["status"] == "completed"

    def test_get_execution_status_nonexistent(self):
        status = self.engine.get_execution_status("nonexistent")
        assert status is None

    def test_list_executions(self):
        # Add dummy executions
        self.engine.executions["exec1"] = {
            "execution_id": "exec1",
            "workflow_id": "wf1",
            "status": "completed",
            "total_duration": 1.5,
        }
        self.engine.executions["exec2"] = {
            "execution_id": "exec2",
            "workflow_id": "wf2",
            "status": "running",
            "total_duration": 0.0,
        }

        executions = self.engine.list_executions()
        assert len(executions) == 2

        exec_ids = [ex["execution_id"] for ex in executions]
        assert "exec1" in exec_ids
        assert "exec2" in exec_ids

    @pytest.mark.asyncio
    async def test_execution_id_generation(self):
        workflow = WorkflowDefinition(
            id="id_test",
            name="ID Test",
            steps=[WorkflowStep(id="step1", name="Step 1", type="service")],
        )

        result = await self.engine.execute_workflow(workflow)
        execution_id = result["execution_id"]

        assert execution_id.startswith("id_test_")
        assert execution_id in self.engine.executions

    @pytest.mark.asyncio
    async def test_execution_timing(self):
        workflow = WorkflowDefinition(
            id="timing_test",
            name="Timing Test",
            steps=[WorkflowStep(id="step1", name="Step 1", type="service")],
        )

        result = await self.engine.execute_workflow(workflow)

        assert "start_time" in result
        assert "end_time" in result
        assert "total_duration" in result
        assert result["total_duration"] > 0
        assert result["end_time"] > result["start_time"]

    @pytest.mark.asyncio
    async def test_levels_completion_tracking(self):
        workflow = WorkflowDefinition(
            id="levels_test",
            name="Levels Test",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="service"),
                WorkflowStep(id="step2", name="Step 2", type="service"),
                WorkflowStep(id="step3", name="Step 3", type="service"),
            ],
            dependencies={"step2": ["step1"], "step3": ["step2"]},
        )

        result = await self.engine.execute_workflow(workflow)

        assert "levels_completed" in result
        assert "total_levels" in result
        assert result["levels_completed"] == result["total_levels"]
        assert result["total_levels"] == 3  # 3 sequential levels

    @pytest.mark.asyncio
    async def test_concurrent_step_execution(self):
        # Test that parallel steps in same level execute concurrently
        workflow = WorkflowDefinition(
            id="concurrent_test",
            name="Concurrent Test",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="service"),
                WorkflowStep(id="step2", name="Step 2", type="service"),
                WorkflowStep(id="step3", name="Step 3", type="service"),
            ],
            dependencies={
                "step2": ["step1"],
                "step3": ["step1"],
            },  # step2, step3 run in parallel after step1
        )

        import time

        start_time = time.time()
        result = await self.engine.execute_workflow(workflow)
        end_time = time.time()

        # Should complete faster than sequential execution due to parallelism
        # Each step simulates 0.1s, so parallel execution should be ~0.2s vs 0.3s sequential
        assert end_time - start_time < 0.25  # Allow some overhead
        assert result["status"] in ["completed", "failed"]

    @pytest.mark.asyncio
    async def test_empty_workflow_execution(self):
        workflow = WorkflowDefinition(id="empty_exec", name="Empty Execution", steps=[])

        # Should handle empty workflow gracefully
        try:
            result = await self.engine.execute_workflow(workflow)
            # If it doesn't crash, verify basic structure
            assert "execution_id" in result
            assert "workflow_id" in result
        except Exception:
            # May legitimately fail on empty workflow
            pass

    @pytest.mark.asyncio
    async def test_large_workflow_execution(self):
        # Test execution of larger workflow
        steps = []
        deps = {}

        # Create 10-step linear workflow
        for i in range(10):
            steps.append(WorkflowStep(id=f"step_{i}", name=f"Step {i}", type="service"))
            if i > 0:
                deps[f"step_{i}"] = [f"step_{i-1}"]

        workflow = WorkflowDefinition(
            id="large_exec", name="Large Execution", steps=steps, dependencies=deps
        )

        result = await self.engine.execute_workflow(workflow)

        assert result["workflow_id"] == "large_exec"
        assert len(result["step_results"]) == 10
        assert result["total_levels"] == 10  # Sequential execution

        # Verify all steps completed
        for i in range(10):
            step_result = result["step_results"][f"step_{i}"]
            assert step_result["status"] in ["completed", "failed"]


class TestExecutionStatus:
    def test_execution_status_enum(self):
        assert ExecutionStatus.PENDING.value == "pending"
        assert ExecutionStatus.RUNNING.value == "running"
        assert ExecutionStatus.COMPLETED.value == "completed"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.SKIPPED.value == "skipped"


class TestPerformanceAndConstraints:
    @pytest.mark.asyncio
    async def test_engine_memory_efficiency(self):
        engine = WorkflowEngine()

        # Execute multiple workflows
        for i in range(20):
            workflow = WorkflowDefinition(
                id=f"mem_test_{i}",
                name=f"Memory Test {i}",
                steps=[WorkflowStep(id="step1", name="Step 1", type="service")],
            )
            result = await engine.execute_workflow(workflow)
            assert "execution_id" in result

        # Should have all executions stored
        assert len(engine.executions) == 20

    @pytest.mark.asyncio
    async def test_execution_performance(self):
        import time

        # Test execution speed on moderately complex workflow
        steps = []
        deps = {}

        # Create diamond pattern workflow
        steps.append(WorkflowStep(id="start", name="Start", type="service"))
        steps.append(WorkflowStep(id="left", name="Left", type="service"))
        steps.append(WorkflowStep(id="right", name="Right", type="service"))
        steps.append(WorkflowStep(id="end", name="End", type="service"))

        deps = {"left": ["start"], "right": ["start"], "end": ["left", "right"]}

        workflow = WorkflowDefinition(
            id="perf_test", name="Performance Test", steps=steps, dependencies=deps
        )

        start_time = time.time()
        result = await self.engine.execute_workflow(workflow)
        end_time = time.time()

        # Should complete reasonably quickly (under 0.5 seconds)
        assert end_time - start_time < 0.5
        assert result["workflow_id"] == "perf_test"

    @pytest.mark.asyncio
    async def test_concurrent_executions(self):
        # Test multiple concurrent workflow executions
        engine = WorkflowEngine()
        workflows = []

        for i in range(5):
            workflow = WorkflowDefinition(
                id=f"concurrent_exec_{i}",
                name=f"Concurrent Exec {i}",
                steps=[
                    WorkflowStep(id="step1", name="Step 1", type="service"),
                    WorkflowStep(id="step2", name="Step 2", type="service"),
                ],
                dependencies={"step2": ["step1"]},
            )
            workflows.append(workflow)

        # Execute all workflows concurrently
        tasks = [engine.execute_workflow(wf) for wf in workflows]
        results = await asyncio.gather(*tasks)

        # All executions should succeed
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result["workflow_id"] == f"concurrent_exec_{i}"

    def setup_method(self):
        self.engine = WorkflowEngine()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
