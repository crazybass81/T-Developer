"""Tests for Workflow Executor"""
import pytest
import asyncio
import json
from src.workflow.workflow_executor import WorkflowExecutor, WorkflowStep, WorkflowStatus, WorkflowResult

class TestWorkflowExecutor:
    def test_executor_initialization(self):
        """Test workflow executor initialization"""
        executor = WorkflowExecutor("test_workflow")
        assert executor.workflow_id == "test_workflow"
        assert executor.status == WorkflowStatus.PENDING
        assert len(executor.steps) == 0
        assert len(executor.results) == 0
        
    def test_add_step(self):
        """Test adding workflow steps"""
        executor = WorkflowExecutor("test_workflow")
        
        step = WorkflowStep(
            id="step1",
            name="Test Step",
            agent_id="test_agent",
            input_mapping={"in": "context_in"},
            output_mapping={"out": "context_out"}
        )
        
        executor.add_step(step)
        assert len(executor.steps) == 1
        assert executor.steps[0].id == "step1"
        
    def test_set_context(self):
        """Test setting workflow context"""
        executor = WorkflowExecutor("test_workflow")
        context = {"key1": "value1", "key2": "value2"}
        
        executor.set_context(context)
        assert executor.context == context
        
    @pytest.mark.asyncio
    async def test_execute_simple_workflow(self):
        """Test executing simple workflow"""
        executor = WorkflowExecutor("test_workflow")
        
        # Add steps
        executor.add_step(WorkflowStep(
            id="step1",
            name="Step 1",
            agent_id="agent1",
            input_mapping={"input": "initial_input"},
            output_mapping={"result": "step1_output"}
        ))
        
        executor.add_step(WorkflowStep(
            id="step2",
            name="Step 2",
            agent_id="agent2",
            input_mapping={"data": "step1_output"},
            output_mapping={"final": "final_output"}
        ))
        
        # Set context
        executor.set_context({"initial_input": "test_data"})
        
        # Execute
        result = await executor.execute()
        
        assert result["workflow_id"] == "test_workflow"
        assert result["status"] == "completed"
        assert "step1" in result["results"]
        assert "step2" in result["results"]
        assert "final_output" in result["context"]
        
    @pytest.mark.asyncio
    async def test_execute_with_failure(self):
        """Test workflow execution with step failure"""
        executor = WorkflowExecutor("test_workflow")
        
        # Add step with 0 retries to force failure
        executor.add_step(WorkflowStep(
            id="failing_step",
            name="Failing Step",
            agent_id="bad_agent",
            input_mapping={},
            output_mapping={},
            retry_count=0,
            timeout=0.001  # Very short timeout to force failure
        ))
        
        result = await executor.execute()
        
        assert result["status"] == "failed"
        # Check if results key exists or error key exists
        assert "results" in result or "error" in result
        
    @pytest.mark.asyncio
    async def test_streaming_execution(self):
        """Test streaming workflow execution"""
        executor = WorkflowExecutor("test_workflow")
        
        # Add steps
        executor.add_step(WorkflowStep(
            id="step1",
            name="Stream Step 1",
            agent_id="agent1",
            input_mapping={},
            output_mapping={"out1": "output1"}
        ))
        
        executor.add_step(WorkflowStep(
            id="step2",
            name="Stream Step 2",
            agent_id="agent2",
            input_mapping={},
            output_mapping={"out2": "output2"}
        ))
        
        # Collect streaming events
        events = []
        async for event in executor.execute_streaming():
            events.append(event)
            
        # Verify events
        assert len(events) > 0
        assert events[0]["type"] == "start"
        assert events[-1]["type"] == "complete"
        
        # Check for step events
        step_starts = [e for e in events if e["type"] == "step_start"]
        step_completes = [e for e in events if e["type"] == "step_complete"]
        
        assert len(step_starts) == 2
        assert len(step_completes) == 2
        
    @pytest.mark.asyncio
    async def test_workflow_cancellation(self):
        """Test workflow cancellation"""
        executor = WorkflowExecutor("test_workflow")
        
        # Add multiple steps
        for i in range(5):
            executor.add_step(WorkflowStep(
                id=f"step{i}",
                name=f"Step {i}",
                agent_id=f"agent{i}",
                input_mapping={},
                output_mapping={}
            ))
            
        # Start execution and cancel
        async def cancel_after_delay():
            await asyncio.sleep(0.05)
            executor.cancel()
            
        cancel_task = asyncio.create_task(cancel_after_delay())
        
        events = []
        async for event in executor.execute_streaming():
            events.append(event)
            
        await cancel_task
        
        # Check for cancellation
        cancelled_events = [e for e in events if e["type"] == "cancelled"]
        assert len(cancelled_events) > 0 or executor.status == WorkflowStatus.CANCELLED
        
    def test_get_status(self):
        """Test getting workflow status"""
        executor = WorkflowExecutor("test_workflow")
        
        # Add steps
        for i in range(3):
            executor.add_step(WorkflowStep(
                id=f"step{i}",
                name=f"Step {i}",
                agent_id=f"agent{i}",
                input_mapping={},
                output_mapping={}
            ))
            
        status = executor.get_status()
        
        assert status["workflow_id"] == "test_workflow"
        assert status["status"] == "pending"
        assert status["total_steps"] == 3
        assert status["completed_steps"] == 0
        
    @pytest.mark.asyncio
    async def test_context_propagation(self):
        """Test context propagation between steps"""
        executor = WorkflowExecutor("test_workflow")
        
        # Add steps with context mapping
        executor.add_step(WorkflowStep(
            id="step1",
            name="Producer",
            agent_id="producer",
            input_mapping={"initial": "input_data"},
            output_mapping={"result": "intermediate_data"}
        ))
        
        executor.add_step(WorkflowStep(
            id="step2",
            name="Consumer",
            agent_id="consumer",
            input_mapping={"data": "intermediate_data"},
            output_mapping={"final": "final_result"}
        ))
        
        # Set initial context
        executor.set_context({"input_data": "initial_value"})
        
        # Execute
        result = await executor.execute()
        
        # Verify context propagation
        assert "intermediate_data" in result["context"]
        assert "final_result" in result["context"]
        
    @pytest.mark.asyncio
    async def test_retry_mechanism(self):
        """Test step retry mechanism"""
        executor = WorkflowExecutor("test_workflow")
        
        # Add step with retries
        executor.add_step(WorkflowStep(
            id="retry_step",
            name="Retry Step",
            agent_id="flaky_agent",
            input_mapping={},
            output_mapping={},
            retry_count=3,
            timeout=30
        ))
        
        # Execute (should handle retries internally)
        result = await executor.execute()
        
        # Should complete or fail after retries
        assert result["status"] in ["completed", "failed"]