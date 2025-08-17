"""Tests for AgentCore runtime.

Phase 2: AWS Integration - Test Suite
"""

import asyncio

import pytest
from packages.runtime.agentcore import (
    Agent,
    AgentCore,
    AgentMemory,
    AgentState,
    ExecutionContext,
    Task,
    TaskResult,
    TaskStatus,
)


class MockAgent(Agent):
    """Mock agent for testing."""

    def __init__(self, agent_id: str, fail_on_task: bool = False):
        super().__init__(agent_id, "mock", {})
        self.fail_on_task = fail_on_task
        self.executed_tasks = []

    async def initialize(self) -> bool:
        """Initialize mock agent."""
        return True

    async def execute_task(self, task: Task, context: ExecutionContext) -> TaskResult:
        """Execute mock task."""
        self.executed_tasks.append(task.id)

        if self.fail_on_task:
            return TaskResult(task_id=task.id, status=TaskStatus.FAILED, error="Mock failure")

        return TaskResult(
            task_id=task.id,
            status=TaskStatus.COMPLETED,
            result={"message": f"Task {task.id} completed"},
        )

    async def cleanup(self) -> None:
        """Clean up mock agent."""
        pass


@pytest.fixture
async def agent_core():
    """Create AgentCore instance for testing."""
    config = {
        "max_queue_size": 100,
        "max_concurrent_tasks": 5,
        "bedrock": {"region": "us-east-1", "timeout": 10},
    }

    core = AgentCore(config=config)
    await core.start()

    yield core

    await core.shutdown()


@pytest.fixture
def mock_agent():
    """Create mock agent for testing."""
    return MockAgent("test-agent-1")


@pytest.fixture
def failing_agent():
    """Create failing mock agent for testing."""
    return MockAgent("test-agent-2", fail_on_task=True)


@pytest.fixture
def sample_task():
    """Create sample task for testing."""
    return Task(
        id="test-task-1",
        type="test",
        payload={"action": "test_action", "data": "test_data"},
        agent_id="test-agent-1",
    )


class TestAgentCore:
    """Test AgentCore functionality."""

    @pytest.mark.asyncio
    async def test_agent_registration(self, agent_core: AgentCore, mock_agent: MockAgent):
        """Test agent registration."""
        # Register agent
        success = await agent_core.register_agent(mock_agent)
        assert success is True

        # Check agent is registered
        assert mock_agent.id in agent_core.agents
        assert agent_core.agents[mock_agent.id].state == AgentState.READY

        # Try to register same agent again
        success = await agent_core.register_agent(mock_agent)
        assert success is False

    @pytest.mark.asyncio
    async def test_agent_unregistration(self, agent_core: AgentCore, mock_agent: MockAgent):
        """Test agent unregistration."""
        # Register agent first
        await agent_core.register_agent(mock_agent)
        assert mock_agent.id in agent_core.agents

        # Unregister agent
        success = await agent_core.unregister_agent(mock_agent.id)
        assert success is True
        assert mock_agent.id not in agent_core.agents

        # Try to unregister non-existent agent
        success = await agent_core.unregister_agent("non-existent")
        assert success is False

    @pytest.mark.asyncio
    async def test_task_submission(
        self, agent_core: AgentCore, mock_agent: MockAgent, sample_task: Task
    ):
        """Test task submission."""
        # Register agent first
        await agent_core.register_agent(mock_agent)

        # Submit task
        success = await agent_core.submit_task(sample_task)
        assert success is True

        # Wait for task execution
        await asyncio.sleep(0.1)

        # Check task result
        result = await agent_core.get_task_result(sample_task.id)
        assert result is not None
        assert result.status == TaskStatus.COMPLETED
        assert sample_task.id in mock_agent.executed_tasks

    @pytest.mark.asyncio
    async def test_task_submission_unknown_agent(self, agent_core: AgentCore, sample_task: Task):
        """Test task submission for unknown agent."""
        # Submit task without registering agent
        success = await agent_core.submit_task(sample_task)
        assert success is False

    @pytest.mark.asyncio
    async def test_task_execution_failure(self, agent_core: AgentCore, failing_agent: MockAgent):
        """Test task execution failure handling."""
        # Register failing agent
        await agent_core.register_agent(failing_agent)

        # Create task for failing agent
        task = Task(
            id="failing-task", type="test", payload={"action": "fail"}, agent_id=failing_agent.id
        )

        # Submit task
        await agent_core.submit_task(task)

        # Wait for task execution
        await asyncio.sleep(0.1)

        # Check task result
        result = await agent_core.get_task_result(task.id)
        assert result is not None
        assert result.status == TaskStatus.FAILED
        assert result.error == "Mock failure"

    @pytest.mark.asyncio
    async def test_task_cancellation(self, agent_core: AgentCore, mock_agent: MockAgent):
        """Test task cancellation."""
        # Register agent
        await agent_core.register_agent(mock_agent)

        # Create task
        task = Task(
            id="cancel-task", type="test", payload={"action": "test"}, agent_id=mock_agent.id
        )

        # Submit task
        await agent_core.submit_task(task)

        # Cancel task immediately
        success = await agent_core.cancel_task(task.id)
        assert success is True

        # Check task result
        result = await agent_core.get_task_result(task.id)
        assert result is not None
        assert result.status == TaskStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_agent_status(self, agent_core: AgentCore, mock_agent: MockAgent):
        """Test agent status retrieval."""
        # Register agent
        await agent_core.register_agent(mock_agent)

        # Get specific agent status
        status = await agent_core.get_agent_status(mock_agent.id)
        assert status["id"] == mock_agent.id
        assert status["type"] == "mock"
        assert status["state"] == AgentState.READY.value

        # Get all agents status
        all_status = await agent_core.get_agent_status()
        assert mock_agent.id in all_status

    @pytest.mark.asyncio
    async def test_queue_status(self, agent_core: AgentCore, mock_agent: MockAgent):
        """Test queue status retrieval."""
        # Register agent
        await agent_core.register_agent(mock_agent)

        # Get initial queue status
        status = await agent_core.get_queue_status()
        assert status["queue_size"] == 0
        assert status["running_tasks"] == 0

        # Submit multiple tasks
        for i in range(3):
            task = Task(
                id=f"queue-task-{i}",
                type="test",
                payload={"action": "test"},
                agent_id=mock_agent.id,
            )
            await agent_core.submit_task(task)

        # Wait for tasks to process
        await asyncio.sleep(0.2)

        # Check final queue status
        status = await agent_core.get_queue_status()
        assert status["completed_tasks"] >= 3


class TestAgentMemory:
    """Test agent memory functionality."""

    def test_memory_initialization(self):
        """Test memory initialization."""
        memory = AgentMemory()
        assert len(memory.short_term) == 0
        assert len(memory.long_term) == 0
        assert len(memory.working) == 0
        assert len(memory.episodic) == 0

    def test_short_term_memory(self):
        """Test short-term memory operations."""
        memory = AgentMemory(max_short_term=3)

        # Add entries
        memory.add_short_term({"type": "interaction", "data": "test1"})
        memory.add_short_term({"type": "interaction", "data": "test2"})
        memory.add_short_term({"type": "interaction", "data": "test3"})

        assert len(memory.short_term) == 3

        # Add one more to trigger trimming
        memory.add_short_term({"type": "interaction", "data": "test4"})

        assert len(memory.short_term) == 3
        assert memory.short_term[0]["data"] == "test2"  # First entry removed
        assert memory.short_term[-1]["data"] == "test4"  # Last entry added

    def test_working_memory(self):
        """Test working memory operations."""
        memory = AgentMemory(max_working=2)

        # Add entries
        memory.add_working("key1", "value1")
        memory.add_working("key2", "value2")

        assert len(memory.working) == 2
        assert memory.working["key1"]["value"] == "value1"

        # Add one more to trigger trimming
        memory.add_working("key3", "value3")

        assert len(memory.working) == 2
        assert "key1" not in memory.working  # Oldest entry removed
        assert "key3" in memory.working  # New entry added

    def test_memory_context(self):
        """Test memory context retrieval."""
        memory = AgentMemory()

        # Add data to different memory types
        memory.add_short_term({"type": "test", "data": "short"})
        memory.add_working("current_task", "working_data")
        memory.long_term["learned_pattern"] = "pattern_data"

        context = memory.get_context()

        assert "short_term" in context
        assert "working" in context
        assert "long_term_keys" in context
        assert len(context["short_term"]) <= 10  # Limited to last 10
        assert "current_task" in context["working"]
        assert "learned_pattern" in context["long_term_keys"]


class TestTaskQueue:
    """Test task queue functionality."""

    @pytest.mark.asyncio
    async def test_task_priority_ordering(self, agent_core: AgentCore, mock_agent: MockAgent):
        """Test task priority ordering in queue."""
        await agent_core.register_agent(mock_agent)

        # Create tasks with different priorities
        low_priority_task = Task(
            id="low-priority",
            type="test",
            payload={"action": "test"},
            agent_id=mock_agent.id,
            priority=1,
        )

        high_priority_task = Task(
            id="high-priority",
            type="test",
            payload={"action": "test"},
            agent_id=mock_agent.id,
            priority=10,
        )

        medium_priority_task = Task(
            id="medium-priority",
            type="test",
            payload={"action": "test"},
            agent_id=mock_agent.id,
            priority=5,
        )

        # Submit in random order
        await agent_core.submit_task(low_priority_task)
        await agent_core.submit_task(high_priority_task)
        await agent_core.submit_task(medium_priority_task)

        # Wait for execution
        await asyncio.sleep(0.2)

        # High priority should execute first
        assert mock_agent.executed_tasks[0] == "high-priority"

    @pytest.mark.asyncio
    async def test_task_timeout(self, agent_core: AgentCore):
        """Test task timeout handling."""

        # Create agent that takes long time
        class SlowAgent(MockAgent):
            async def execute_task(self, task: Task, context: ExecutionContext) -> TaskResult:
                await asyncio.sleep(1)  # Long execution
                return await super().execute_task(task, context)

        slow_agent = SlowAgent("slow-agent")
        await agent_core.register_agent(slow_agent)

        # Create task with short timeout
        task = Task(
            id="timeout-task",
            type="test",
            payload={"action": "test"},
            agent_id=slow_agent.id,
            timeout_seconds=0.1,  # Very short timeout
        )

        await agent_core.submit_task(task)

        # Wait for timeout
        await asyncio.sleep(0.3)

        # Check task result
        result = await agent_core.get_task_result(task.id)
        assert result is not None
        assert result.status == TaskStatus.TIMEOUT


@pytest.mark.asyncio
async def test_concurrent_task_execution(agent_core: AgentCore):
    """Test concurrent task execution."""
    # Register multiple agents
    agents = []
    for i in range(3):
        agent = MockAgent(f"concurrent-agent-{i}")
        agents.append(agent)
        await agent_core.register_agent(agent)

    # Submit tasks concurrently
    tasks = []
    for i in range(9):  # 3 tasks per agent
        agent_id = f"concurrent-agent-{i % 3}"
        task = Task(
            id=f"concurrent-task-{i}", type="test", payload={"action": "test"}, agent_id=agent_id
        )
        tasks.append(task)
        await agent_core.submit_task(task)

    # Wait for all tasks to complete
    await asyncio.sleep(0.5)

    # Check all tasks completed
    completed_count = 0
    for task in tasks:
        result = await agent_core.get_task_result(task.id)
        if result and result.status == TaskStatus.COMPLETED:
            completed_count += 1

    assert completed_count == 9
