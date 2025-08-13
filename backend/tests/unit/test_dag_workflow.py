#!/usr/bin/env python3
"""
Unit Tests for DAG Workflow Engine
Tests the workflow orchestration and execution
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.core.workflow.dag_engine import (
    DAGWorkflowEngine,
    WorkflowNode,
    NodeStatus,
    ExecutionStrategy,
    WorkflowExecution,
)


class TestDAGWorkflow:
    """Test suite for DAG workflow engine"""

    @pytest.fixture
    def engine(self):
        """Create workflow engine instance"""
        return DAGWorkflowEngine(
            max_parallel_nodes=5, max_retries=2, default_timeout=10
        )

    @pytest.fixture
    def simple_workflow_nodes(self):
        """Create simple linear workflow nodes"""
        return [
            WorkflowNode(
                node_id="start",
                agent_id="agent_start",
                name="Start Node",
                dependencies=[],
            ),
            WorkflowNode(
                node_id="process",
                agent_id="agent_process",
                name="Process Node",
                dependencies=["start"],
            ),
            WorkflowNode(
                node_id="end",
                agent_id="agent_end",
                name="End Node",
                dependencies=["process"],
            ),
        ]

    @pytest.fixture
    def complex_workflow_nodes(self):
        """Create complex workflow with parallel branches"""
        return [
            WorkflowNode(
                node_id="start",
                agent_id="agent_start",
                name="Start Node",
                dependencies=[],
                priority=10,
            ),
            WorkflowNode(
                node_id="branch1",
                agent_id="agent_branch1",
                name="Branch 1",
                dependencies=["start"],
                priority=5,
            ),
            WorkflowNode(
                node_id="branch2",
                agent_id="agent_branch2",
                name="Branch 2",
                dependencies=["start"],
                priority=8,
            ),
            WorkflowNode(
                node_id="merge",
                agent_id="agent_merge",
                name="Merge Node",
                dependencies=["branch1", "branch2"],
            ),
            WorkflowNode(
                node_id="end",
                agent_id="agent_end",
                name="End Node",
                dependencies=["merge"],
            ),
        ]

    def test_workflow_creation(self, engine, simple_workflow_nodes):
        """Test workflow creation and validation"""
        # Create valid workflow
        success = engine.create_workflow(
            workflow_id="test_workflow",
            nodes=simple_workflow_nodes,
            metadata={"description": "Test workflow"},
        )

        assert success == True
        assert "test_workflow" in engine.workflows
        assert len(engine.workflows["test_workflow"].nodes) == 3

    def test_cyclic_workflow_detection(self, engine):
        """Test detection of cycles in workflow"""
        # Create workflow with cycle
        cyclic_nodes = [
            WorkflowNode("node1", "agent1", "Node 1", dependencies=[]),
            WorkflowNode("node2", "agent2", "Node 2", dependencies=["node1"]),
            WorkflowNode("node3", "agent3", "Node 3", dependencies=["node2"]),
            WorkflowNode(
                "node1", "agent1", "Node 1", dependencies=["node3"]
            ),  # Creates cycle
        ]

        success = engine.create_workflow(
            workflow_id="cyclic_workflow", nodes=cyclic_nodes
        )

        assert success == False

    def test_invalid_dependency(self, engine):
        """Test workflow with non-existent dependency"""
        invalid_nodes = [
            WorkflowNode("node1", "agent1", "Node 1", dependencies=[]),
            WorkflowNode("node2", "agent2", "Node 2", dependencies=["non_existent"]),
        ]

        success = engine.create_workflow(
            workflow_id="invalid_workflow", nodes=invalid_nodes
        )

        assert success == False

    @pytest.mark.asyncio
    async def test_sequential_execution(self, engine, simple_workflow_nodes):
        """Test sequential workflow execution"""
        # Create workflow
        engine.create_workflow(
            workflow_id="sequential_test", nodes=simple_workflow_nodes
        )

        # Execute workflow
        execution = await engine.execute_workflow(
            workflow_id="sequential_test",
            input_data={"test": "data"},
            strategy=ExecutionStrategy.SEQUENTIAL,
        )

        assert execution.status == "completed"
        assert execution.workflow_id == "sequential_test"
        assert len(execution.node_executions) == 3

        # Check all nodes succeeded
        for node_exec in execution.node_executions.values():
            assert node_exec.status == NodeStatus.SUCCESS

        # Check metrics
        assert execution.metrics["success_count"] == 3
        assert execution.metrics["failed_count"] == 0
        assert execution.metrics["success_rate"] == 1.0

    @pytest.mark.asyncio
    async def test_parallel_execution(self, engine, complex_workflow_nodes):
        """Test parallel workflow execution"""
        # Create workflow
        engine.create_workflow(
            workflow_id="parallel_test", nodes=complex_workflow_nodes
        )

        # Execute workflow
        execution = await engine.execute_workflow(
            workflow_id="parallel_test",
            input_data={"test": "parallel"},
            strategy=ExecutionStrategy.PARALLEL,
        )

        assert execution.status == "completed"
        assert len(execution.node_executions) == 5

        # Check that branches could execute in parallel
        branch1_exec = execution.node_executions["branch1"]
        branch2_exec = execution.node_executions["branch2"]

        # Both branches should have started (parallel execution)
        assert branch1_exec.started_at is not None
        assert branch2_exec.started_at is not None

        # Merge should only start after both branches complete
        merge_exec = execution.node_executions["merge"]
        assert merge_exec.started_at >= branch1_exec.completed_at
        assert merge_exec.started_at >= branch2_exec.completed_at

    @pytest.mark.asyncio
    async def test_priority_execution(self, engine, complex_workflow_nodes):
        """Test priority-based execution"""
        # Create workflow
        engine.create_workflow(
            workflow_id="priority_test", nodes=complex_workflow_nodes
        )

        # Execute with priority strategy
        execution = await engine.execute_workflow(
            workflow_id="priority_test", strategy=ExecutionStrategy.PRIORITY
        )

        assert execution.status == "completed"

        # Check that higher priority nodes executed first when possible
        # branch2 has priority 8, branch1 has priority 5
        # So branch2 should start before or at same time as branch1
        branch1_exec = execution.node_executions["branch1"]
        branch2_exec = execution.node_executions["branch2"]

        assert branch2_exec.started_at <= branch1_exec.started_at

    def test_workflow_visualization(self, engine, simple_workflow_nodes):
        """Test workflow visualization generation"""
        engine.create_workflow(workflow_id="viz_test", nodes=simple_workflow_nodes)

        mermaid = engine.visualize_workflow("viz_test")

        assert "graph TD" in mermaid
        assert "start[Start Node]" in mermaid
        assert "process[Process Node]" in mermaid
        assert "end[End Node]" in mermaid
        assert "start --> process" in mermaid
        assert "process --> end" in mermaid

    @pytest.mark.asyncio
    async def test_node_retry_logic(self, engine):
        """Test node retry on failure"""
        # This test would require mocking agent execution to fail
        # For now, just verify retry count is set
        nodes = [
            WorkflowNode(
                node_id="retry_node",
                agent_id="agent_retry",
                name="Retry Node",
                dependencies=[],
                retry_count=3,
            )
        ]

        engine.create_workflow(workflow_id="retry_test", nodes=nodes)

        execution = await engine.execute_workflow(workflow_id="retry_test")

        node_exec = execution.node_executions["retry_node"]
        assert node_exec.retries_left == 3  # Initial retry count

    @pytest.mark.asyncio
    async def test_conditional_execution(self, engine):
        """Test conditional node execution"""
        nodes = [
            WorkflowNode(
                node_id="start", agent_id="agent_start", name="Start", dependencies=[]
            ),
            WorkflowNode(
                node_id="conditional",
                agent_id="agent_cond",
                name="Conditional Node",
                dependencies=["start"],
                condition="should_execute",
            ),
        ]

        engine.create_workflow(workflow_id="conditional_test", nodes=nodes)

        # Execute with condition false
        execution = await engine.execute_workflow(
            workflow_id="conditional_test", input_data={"should_execute": False}
        )

        # Conditional node should be skipped
        cond_exec = execution.node_executions["conditional"]
        assert cond_exec.status == NodeStatus.SKIPPED

    def test_execution_status_tracking(self, engine):
        """Test execution status retrieval"""
        nodes = [WorkflowNode("node1", "agent1", "Node 1", dependencies=[])]

        engine.create_workflow(workflow_id="status_test", nodes=nodes)

        # Start execution asynchronously
        loop = asyncio.new_event_loop()
        execution = loop.run_until_complete(engine.execute_workflow("status_test"))

        # Check status retrieval
        status = engine.get_execution_status(execution.execution_id)
        assert status is not None
        assert status.execution_id == execution.execution_id
        assert status.workflow_id == "status_test"

    def test_cleanup(self, engine, simple_workflow_nodes):
        """Test engine cleanup"""
        engine.create_workflow(workflow_id="cleanup_test", nodes=simple_workflow_nodes)

        # Cleanup
        engine.cleanup()

        assert len(engine.workflows) == 0
        assert len(engine.executions) == 0


def run_tests():
    """Run tests standalone"""
    print("\n" + "=" * 50)
    print("Running DAG Workflow Engine Tests")
    print("=" * 50 + "\n")

    test = TestDAGWorkflow()
    engine = DAGWorkflowEngine()

    # Test 1: Workflow creation
    print("1. Testing workflow creation...")
    simple_nodes = [
        WorkflowNode("start", "agent1", "Start", []),
        WorkflowNode("end", "agent2", "End", ["start"]),
    ]
    success = engine.create_workflow("test1", simple_nodes)
    print(f"   ✓ Workflow created: {success}")

    # Test 2: Visualization
    print("\n2. Testing visualization...")
    viz = engine.visualize_workflow("test1")
    print(f"   ✓ Visualization generated: {len(viz)} chars")

    # Test 3: Execution
    print("\n3. Testing workflow execution...")
    loop = asyncio.new_event_loop()
    execution = loop.run_until_complete(engine.execute_workflow("test1"))
    print(f"   ✓ Execution completed: {execution.status}")
    print(f"   Success rate: {execution.metrics['success_rate']:.0%}")

    # Test 4: Complex workflow
    print("\n4. Testing complex workflow...")
    complex_nodes = [
        WorkflowNode("start", "agent1", "Start", []),
        WorkflowNode("parallel1", "agent2", "Parallel 1", ["start"]),
        WorkflowNode("parallel2", "agent3", "Parallel 2", ["start"]),
        WorkflowNode("merge", "agent4", "Merge", ["parallel1", "parallel2"]),
        WorkflowNode("end", "agent5", "End", ["merge"]),
    ]
    engine.create_workflow("complex", complex_nodes)
    execution = loop.run_until_complete(
        engine.execute_workflow("complex", strategy=ExecutionStrategy.PARALLEL)
    )
    print(f"   ✓ Complex workflow executed: {execution.metrics['total_nodes']} nodes")
    print(
        f"   Success: {execution.metrics['success_count']}, Failed: {execution.metrics['failed_count']}"
    )

    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("=" * 50 + "\n")

    loop.close()
    engine.cleanup()


if __name__ == "__main__":
    run_tests()
