"""Test template for generated agents.

This template is used by Agno to generate test suites for new agents.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Any, Dict

from backend.packages.agents import AgentTask, AgentResult, TaskStatus
from backend.packages.memory import MemoryHub, ContextType
from {{agent_module}} import {{agent_name}}Agent


@pytest.fixture
async def memory_hub():
    """Create a mock memory hub for testing."""
    hub = Mock(spec=MemoryHub)
    hub.get = AsyncMock(return_value=None)
    hub.put = AsyncMock(return_value=True)
    hub.search = AsyncMock(return_value=[])
    return hub


@pytest.fixture
async def agent(memory_hub):
    """Create an agent instance for testing."""
    return {{agent_name}}Agent(memory_hub=memory_hub)


@pytest.fixture
def valid_task():
    """Create a valid task for testing."""
    return AgentTask(
        intent="{{primary_intent}}",
        inputs={
            {{valid_inputs}}
        },
        policy={
            "ai_first": True,
            "dedup": True
        },
        deadline_seconds=300
    )


class Test{{agent_name}}Agent:
    """Test suite for {{agent_name}}Agent."""
    
    @pytest.mark.asyncio
    async def test_successful_execution(self, agent, valid_task):
        """Test successful task execution.
        
        Given: A valid task with all required inputs
        When: The agent executes the task
        Then: It should return a successful result
        """
        # Execute the task
        result = await agent.execute(valid_task)
        
        # Verify success
        assert result.success is True
        assert result.status == TaskStatus.COMPLETED
        assert result.data is not None
        assert result.error is None
        
        # Verify expected outputs
        {{output_assertions}}
    
    @pytest.mark.asyncio
    async def test_input_validation_missing_required(self, agent):
        """Test input validation with missing required fields.
        
        Given: A task missing required inputs
        When: The agent attempts to execute
        Then: It should return a validation error
        """
        invalid_task = AgentTask(
            intent="{{primary_intent}}",
            inputs={}  # Missing required inputs
        )
        
        result = await agent.execute(invalid_task)
        
        assert result.success is False
        assert "Invalid input" in result.error
    
    @pytest.mark.asyncio
    async def test_input_validation_invalid_type(self, agent):
        """Test input validation with invalid types.
        
        Given: A task with invalid input types
        When: The agent attempts to execute
        Then: It should return a validation error
        """
        invalid_task = AgentTask(
            intent="{{primary_intent}}",
            inputs={
                {{invalid_type_inputs}}
            }
        )
        
        result = await agent.execute(invalid_task)
        
        assert result.success is False
        assert result.error is not None
    
    @pytest.mark.asyncio
    async def test_memory_read_operations(self, agent, valid_task, memory_hub):
        """Test memory read operations.
        
        Given: A task that requires context from memory
        When: The agent executes
        Then: It should read from the correct memory contexts
        """
        # Setup memory mock to return test data
        test_context = {"previous_result": "test_data"}
        memory_hub.get.return_value = test_context
        
        # Execute
        result = await agent.execute(valid_task)
        
        # Verify memory reads
        assert memory_hub.get.called
        {{memory_read_assertions}}
    
    @pytest.mark.asyncio
    async def test_memory_write_operations(self, agent, valid_task, memory_hub):
        """Test memory write operations.
        
        Given: A successful task execution
        When: The agent completes the task
        Then: It should write results to memory
        """
        # Execute
        result = await agent.execute(valid_task)
        
        # Verify memory writes
        assert memory_hub.put.called
        {{memory_write_assertions}}
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, agent):
        """Test timeout handling.
        
        Given: A task that takes too long
        When: The timeout is exceeded
        Then: It should return a timeout error
        """
        slow_task = AgentTask(
            intent="{{primary_intent}}",
            inputs={{valid_inputs}},
            deadline_seconds=0.1  # Very short timeout
        )
        
        # Mock slow operation
        with patch.object(agent, '_perform_operation', side_effect=asyncio.TimeoutError):
            result = await agent.execute(slow_task)
        
        assert result.success is False
        assert result.status == TaskStatus.TIMEOUT
        assert "timeout" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_exception_handling(self, agent, valid_task):
        """Test exception handling.
        
        Given: An unexpected error during execution
        When: The agent encounters an exception
        Then: It should handle it gracefully
        """
        # Mock operation to raise exception
        with patch.object(agent, '_perform_operation', side_effect=Exception("Test error")):
            result = await agent.execute(valid_task)
        
        assert result.success is False
        assert result.status == TaskStatus.FAILED
        assert "Test error" in result.error
    
    @pytest.mark.asyncio
    async def test_execution_logging(self, agent, valid_task, memory_hub):
        """Test execution logging.
        
        Given: A task execution
        When: The task completes (success or failure)
        Then: Execution should be logged to memory
        """
        # Execute
        result = await agent.execute(valid_task)
        
        # Check that execution was logged
        calls = [call for call in memory_hub.put.call_args_list 
                if "execution" in str(call)]
        assert len(calls) > 0
    
    @pytest.mark.parametrize("input_values,expected_success", [
        {{parametrized_test_cases}}
    ])
    @pytest.mark.asyncio
    async def test_various_inputs(self, agent, input_values, expected_success):
        """Test various input combinations.
        
        Given: Different input combinations
        When: The agent processes them
        Then: It should handle each appropriately
        """
        task = AgentTask(
            intent="{{primary_intent}}",
            inputs=input_values
        )
        
        result = await agent.execute(task)
        assert result.success == expected_success
    
    @pytest.mark.asyncio
    async def test_concurrent_execution(self, agent, valid_task):
        """Test concurrent task execution.
        
        Given: Multiple tasks executed concurrently
        When: The agent processes them
        Then: All should complete successfully
        """
        # Create multiple tasks
        tasks = [valid_task for _ in range(5)]
        
        # Execute concurrently
        results = await asyncio.gather(
            *[agent.execute(task) for task in tasks]
        )
        
        # Verify all succeeded
        assert all(r.success for r in results)
        assert len(results) == 5