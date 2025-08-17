"""Tests for WorkflowComposer implementation."""

from unittest.mock import AsyncMock

import pytest
from packages.meta_agents.workflow_composer import (
    Parallelizer,
    ResourceAllocator,
    WorkflowComposer,
    WorkflowConfig,
    WorkflowStep,
)


class TestWorkflowConfig:
    """Test workflow configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = WorkflowConfig()

        assert config.max_parallel_tasks == 5
        assert config.enable_optimization is True
        assert config.resource_limits == {"cpu": 4, "memory_gb": 8, "time_minutes": 60}
        assert config.retry_policy == {"max_retries": 3, "backoff_seconds": 30}

    def test_custom_config(self):
        """Test custom configuration."""
        config = WorkflowConfig(
            max_parallel_tasks=10, enable_optimization=False, resource_limits={"cpu": 8}
        )

        assert config.max_parallel_tasks == 10
        assert config.enable_optimization is False
        assert config.resource_limits["cpu"] == 8


class TestWorkflowStep:
    """Test workflow step."""

    def test_step_creation(self):
        """Test creating workflow step."""
        step = WorkflowStep(
            id="step-1",
            name="Process Data",
            agent="DataProcessor",
            dependencies=["step-0"],
            inputs={"data": "input"},
            estimated_duration=30,
        )

        assert step.id == "step-1"
        assert step.name == "Process Data"
        assert step.agent == "DataProcessor"
        assert step.dependencies == ["step-0"]
        assert step.inputs == {"data": "input"}
        assert step.estimated_duration == 30

    def test_step_validation(self):
        """Test step validation."""
        step = WorkflowStep(id="step-1", name="Test Step", agent="TestAgent")

        assert step.validate() is True

        # Invalid step (no agent)
        invalid_step = WorkflowStep(id="step-2", name="Invalid", agent="")

        assert invalid_step.validate() is False


class TestParallelizer:
    """Test workflow parallelizer."""

    def test_identify_parallel_tasks(self):
        """Test identifying tasks that can run in parallel."""
        parallelizer = Parallelizer()

        tasks = [
            {"id": "1", "dependencies": []},
            {"id": "2", "dependencies": []},
            {"id": "3", "dependencies": ["1"]},
            {"id": "4", "dependencies": ["2"]},
            {"id": "5", "dependencies": ["3", "4"]},
        ]

        parallel_groups = parallelizer.identify_parallel_tasks(tasks)

        # Tasks 1 and 2 can run in parallel (no dependencies)
        assert len(parallel_groups[0]) == 2
        assert "1" in parallel_groups[0]
        assert "2" in parallel_groups[0]

        # Tasks 3 and 4 can run in parallel (independent dependencies)
        assert len(parallel_groups[1]) == 2
        assert "3" in parallel_groups[1]
        assert "4" in parallel_groups[1]

        # Task 5 runs alone (depends on 3 and 4)
        assert len(parallel_groups[2]) == 1
        assert "5" in parallel_groups[2]

    def test_optimize_execution_order(self):
        """Test optimizing task execution order."""
        parallelizer = Parallelizer()

        tasks = [
            {"id": "1", "estimated_time": 10, "dependencies": []},
            {"id": "2", "estimated_time": 5, "dependencies": []},
            {"id": "3", "estimated_time": 15, "dependencies": ["1"]},
        ]

        optimized = parallelizer.optimize_execution_order(tasks)

        # Shorter tasks should be prioritized when possible
        assert optimized[0]["id"] == "2"  # Shortest independent task
        assert optimized[1]["id"] == "1"  # Next independent task
        assert optimized[2]["id"] == "3"  # Dependent task

    def test_calculate_critical_path(self):
        """Test critical path calculation."""
        parallelizer = Parallelizer()

        workflow = {
            "1": {"duration": 10, "dependencies": []},
            "2": {"duration": 5, "dependencies": []},
            "3": {"duration": 15, "dependencies": ["1"]},
            "4": {"duration": 8, "dependencies": ["2"]},
            "5": {"duration": 10, "dependencies": ["3", "4"]},
        }

        critical_path = parallelizer.calculate_critical_path(workflow)

        # Critical path: 1 -> 3 -> 5 (10 + 15 + 10 = 35)
        assert critical_path["path"] == ["1", "3", "5"]
        assert critical_path["duration"] == 35


class TestResourceAllocator:
    """Test resource allocator."""

    def test_allocate_resources(self):
        """Test resource allocation."""
        allocator = ResourceAllocator()

        task = {"id": "task-1", "requirements": {"cpu": 2, "memory_gb": 4, "gpu": False}}

        allocation = allocator.allocate(
            task, available_resources={"cpu": 8, "memory_gb": 16, "gpu": 1}
        )

        assert allocation["cpu"] == 2
        assert allocation["memory_gb"] == 4
        assert allocation["gpu"] == 0

    def test_check_resource_availability(self):
        """Test checking resource availability."""
        allocator = ResourceAllocator()

        available = {"cpu": 4, "memory_gb": 8}

        # Requirements within limits
        assert allocator.can_allocate({"cpu": 2, "memory_gb": 4}, available) is True

        # Requirements exceed limits
        assert allocator.can_allocate({"cpu": 6, "memory_gb": 4}, available) is False

    def test_optimize_resource_usage(self):
        """Test resource usage optimization."""
        allocator = ResourceAllocator()

        tasks = [
            {"id": "1", "requirements": {"cpu": 2, "memory_gb": 4}},
            {"id": "2", "requirements": {"cpu": 1, "memory_gb": 2}},
            {"id": "3", "requirements": {"cpu": 3, "memory_gb": 6}},
        ]

        schedule = allocator.optimize_schedule(
            tasks, available_resources={"cpu": 4, "memory_gb": 8}
        )

        # Should schedule tasks that fit within resource limits
        assert len(schedule["parallel"]) <= 2  # Can't run all 3 in parallel
        total_cpu = sum(t["requirements"]["cpu"] for t in schedule["parallel"])
        assert total_cpu <= 4


class TestWorkflowComposer:
    """Test workflow composer."""

    @pytest.fixture
    def composer(self):
        """Create workflow composer."""
        config = WorkflowConfig()
        return WorkflowComposer(config)

    @pytest.mark.asyncio
    async def test_compose_workflow(self, composer):
        """Test composing workflow from requirements."""
        requirements = [
            {"id": "REQ-1", "description": "Create user API", "agents": ["UserAgent"]},
            {
                "id": "REQ-2",
                "description": "Add authentication",
                "agents": ["AuthAgent"],
                "depends_on": ["REQ-1"],
            },
        ]

        workflow = await composer.compose(requirements)

        assert workflow["id"].startswith("workflow-")
        assert len(workflow["steps"]) == 2
        assert workflow["steps"][0].agent == "UserAgent"
        assert workflow["steps"][1].agent == "AuthAgent"
        assert workflow["steps"][1].dependencies == ["step-0"]

    @pytest.mark.asyncio
    async def test_validate_workflow(self, composer):
        """Test workflow validation."""
        valid_workflow = {
            "steps": [
                WorkflowStep(id="step-1", name="Step 1", agent="Agent1", dependencies=[]),
                WorkflowStep(id="step-2", name="Step 2", agent="Agent2", dependencies=["step-1"]),
            ]
        }

        assert await composer.validate(valid_workflow) is True

        # Workflow with circular dependency
        invalid_workflow = {
            "steps": [
                WorkflowStep(id="step-1", name="Step 1", agent="Agent1", dependencies=["step-2"]),
                WorkflowStep(id="step-2", name="Step 2", agent="Agent2", dependencies=["step-1"]),
            ]
        }

        assert await composer.validate(invalid_workflow) is False

    @pytest.mark.asyncio
    async def test_optimize_workflow(self, composer):
        """Test workflow optimization."""
        workflow = {
            "steps": [
                {"id": "1", "agent": "Agent1", "dependencies": [], "estimated_duration": 10},
                {"id": "2", "agent": "Agent2", "dependencies": [], "estimated_duration": 5},
                {
                    "id": "3",
                    "agent": "Agent3",
                    "dependencies": ["1", "2"],
                    "estimated_duration": 15,
                },
            ]
        }

        optimized = await composer.optimize(workflow)

        assert "parallel_groups" in optimized
        assert "critical_path" in optimized
        assert "estimated_duration" in optimized

        # Steps 1 and 2 should be in the same parallel group
        assert len(optimized["parallel_groups"][0]) == 2

    @pytest.mark.asyncio
    async def test_execute_workflow(self, composer):
        """Test workflow execution."""
        # Create mock agent executor
        mock_executor = AsyncMock()
        mock_executor.execute.return_value = {"status": "success", "output": {"result": "done"}}

        composer.agent_executor = mock_executor

        workflow = {
            "id": "test-workflow",
            "steps": [
                WorkflowStep(
                    id="step-1",
                    name="Test Step",
                    agent="TestAgent",
                    dependencies=[],
                    inputs={"test": "data"},
                )
            ],
        }

        result = await composer.execute(workflow)

        assert result["status"] == "completed"
        assert result["workflow_id"] == "test-workflow"
        assert len(result["step_results"]) == 1
        mock_executor.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_step_failure(self, composer):
        """Test handling step failures."""
        # Create mock agent executor that fails
        mock_executor = AsyncMock()
        mock_executor.execute.side_effect = Exception("Agent failed")

        composer.agent_executor = mock_executor

        workflow = {
            "id": "test-workflow",
            "steps": [
                WorkflowStep(
                    id="step-1", name="Failing Step", agent="FailingAgent", dependencies=[]
                )
            ],
        }

        result = await composer.execute(workflow)

        assert result["status"] == "failed"
        assert "error" in result["step_results"][0]

    @pytest.mark.asyncio
    async def test_workflow_with_retries(self, composer):
        """Test workflow with retry policy."""
        call_count = 0

        async def flaky_executor(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return {"status": "success"}

        mock_executor = AsyncMock()
        mock_executor.execute = flaky_executor

        composer.agent_executor = mock_executor
        composer.config.retry_policy["max_retries"] = 3

        workflow = {
            "id": "test-workflow",
            "steps": [
                WorkflowStep(id="step-1", name="Flaky Step", agent="FlakyAgent", dependencies=[])
            ],
        }

        result = await composer.execute(workflow)

        assert result["status"] == "completed"
        assert call_count == 2  # Failed once, succeeded on retry

    @pytest.mark.asyncio
    async def test_save_workflow(self, composer, tmp_path):
        """Test saving workflow to file."""
        workflow = {
            "id": "test-workflow",
            "name": "Test Workflow",
            "steps": [{"id": "step-1", "name": "Step 1", "agent": "Agent1"}],
        }

        output_file = tmp_path / "workflow.json"
        await composer.save(workflow, output_file)

        assert output_file.exists()

        # Load and verify
        import json

        with open(output_file) as f:
            loaded = json.load(f)

        assert loaded["id"] == workflow["id"]
        assert len(loaded["steps"]) == 1

    @pytest.mark.asyncio
    async def test_load_workflow(self, composer, tmp_path):
        """Test loading workflow from file."""
        workflow = {
            "id": "test-workflow",
            "name": "Test Workflow",
            "steps": [{"id": "step-1", "name": "Step 1", "agent": "Agent1"}],
        }

        # Save workflow
        import json

        workflow_file = tmp_path / "workflow.json"
        with open(workflow_file, "w") as f:
            json.dump(workflow, f)

        # Load workflow
        loaded = await composer.load(workflow_file)

        assert loaded["id"] == workflow["id"]
        assert loaded["name"] == workflow["name"]
        assert len(loaded["steps"]) == 1

    @pytest.mark.asyncio
    async def test_generate_visualization(self, composer):
        """Test generating workflow visualization."""
        workflow = {
            "id": "test-workflow",
            "steps": [
                WorkflowStep(id="step-1", name="Start", agent="Agent1", dependencies=[]),
                WorkflowStep(id="step-2", name="Process", agent="Agent2", dependencies=["step-1"]),
                WorkflowStep(id="step-3", name="End", agent="Agent3", dependencies=["step-2"]),
            ],
        }

        visualization = await composer.generate_visualization(workflow)

        assert "graph" in visualization
        assert "nodes" in visualization
        assert "edges" in visualization
        assert len(visualization["nodes"]) == 3
        assert len(visualization["edges"]) == 2
