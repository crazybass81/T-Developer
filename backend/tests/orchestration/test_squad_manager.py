"""Tests for Squad Manager"""
import asyncio

import pytest

from src.orchestration.squad_manager import AgentTask, SquadManager, SquadRole


class TestSquadManager:
    def test_squad_initialization(self):
        """Test squad manager initialization"""
        squad = SquadManager("test_squad")
        assert squad.squad_name == "test_squad"
        assert squad.max_parallel == 10
        assert len(squad.agents) == 0
        assert len(squad.tasks) == 0

    def test_agent_registration(self):
        """Test agent registration"""
        squad = SquadManager("test_squad")
        squad.register_agent("agent1", SquadRole.LEADER, ["capability1", "capability2"])

        assert "agent1" in squad.agents
        assert squad.agents["agent1"]["role"] == SquadRole.LEADER
        assert squad.agents["agent1"]["capabilities"] == ["capability1", "capability2"]
        assert squad.agents["agent1"]["status"] == "ready"

    def test_task_addition(self):
        """Test adding tasks"""
        squad = SquadManager("test_squad")
        task = AgentTask("t1", "agent1", {"data": "test"}, [], 10)
        squad.add_task(task)

        assert "t1" in squad.tasks
        assert squad.tasks["t1"].agent_name == "agent1"
        assert squad.tasks["t1"].priority == 10
        assert squad.tasks["t1"].status == "pending"

    def test_dependency_validation(self):
        """Test task dependency validation"""
        squad = SquadManager("test_squad")

        # Add tasks with dependencies
        squad.add_task(AgentTask("t1", "agent1", {}, [], 10))
        squad.add_task(AgentTask("t2", "agent2", {}, ["t1"], 5))
        squad.add_task(AgentTask("t3", "agent3", {}, ["t2"], 1))

        # Should be valid (no cycles)
        assert squad.validate_task_graph() == True

        # Add circular dependency
        squad.add_task(AgentTask("t4", "agent4", {}, ["t5"], 1))
        squad.add_task(AgentTask("t5", "agent5", {}, ["t4"], 1))

        # Should detect cycle
        assert squad.validate_task_graph() == False

    def test_ready_tasks(self):
        """Test getting ready tasks"""
        squad = SquadManager("test_squad")

        # Add tasks with dependencies
        squad.add_task(AgentTask("t1", "agent1", {}, [], 10))
        squad.add_task(AgentTask("t2", "agent2", {}, ["t1"], 5))
        squad.add_task(AgentTask("t3", "agent3", {}, [], 8))

        # t1 and t3 should be ready (no dependencies)
        ready = squad._get_ready_tasks()
        assert "t1" in ready or "t3" in ready
        assert "t2" not in ready  # Has dependency on t1

    def test_execution_plan(self):
        """Test execution plan generation"""
        squad = SquadManager("test_squad")

        # Create task graph
        squad.add_task(AgentTask("t1", "agent1", {}, [], 10))
        squad.add_task(AgentTask("t2", "agent2", {}, [], 10))
        squad.add_task(AgentTask("t3", "agent3", {}, ["t1", "t2"], 5))
        squad.add_task(AgentTask("t4", "agent4", {}, ["t3"], 1))

        plan = squad.get_execution_plan()

        # First batch should have t1 and t2 (parallel)
        assert len(plan[0]) == 2
        assert "t1" in plan[0]
        assert "t2" in plan[0]

        # Second batch should have t3
        assert len(plan[1]) == 1
        assert "t3" in plan[1]

        # Third batch should have t4
        assert len(plan[2]) == 1
        assert "t4" in plan[2]

    @pytest.mark.asyncio
    async def test_squad_execution(self):
        """Test squad execution"""
        squad = SquadManager("test_squad")

        # Register agents
        squad.register_agent("agent1", SquadRole.LEADER, ["capability1"])
        squad.register_agent("agent2", SquadRole.WORKER, ["capability2"])

        # Add tasks
        squad.add_task(AgentTask("t1", "agent1", {"data": "test1"}, [], 10))
        squad.add_task(AgentTask("t2", "agent2", {"data": "test2"}, ["t1"], 5))

        # Execute
        results = await squad.execute_squad()

        assert results["squad"] == "test_squad"
        assert "t1" in results["results"]["success"]
        assert "t2" in results["results"]["success"]
        assert len(results["results"]["failed"]) == 0

    def test_squad_status(self):
        """Test squad status reporting"""
        squad = SquadManager("test_squad")

        # Setup squad
        squad.register_agent("agent1", SquadRole.LEADER, ["capability1"])
        squad.register_agent("agent2", SquadRole.WORKER, ["capability2"])
        squad.add_task(AgentTask("t1", "agent1", {}, [], 10))
        squad.completed_tasks.add("t0")  # Simulate completed task

        status = squad.get_squad_status()

        assert status["squad_name"] == "test_squad"
        assert status["total_agents"] == 2
        assert status["ready_agents"] == 2
        assert status["pending_tasks"] == 1
        assert status["completed_tasks"] == 1

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test parallel task execution"""
        squad = SquadManager("test_squad")
        squad.max_parallel = 2  # Limit parallel execution

        # Register agents
        for i in range(5):
            squad.register_agent(f"agent{i}", SquadRole.WORKER, [])

        # Add independent tasks
        for i in range(5):
            squad.add_task(AgentTask(f"t{i}", f"agent{i}", {}, [], 10 - i))

        # Execute and verify parallelism
        results = await squad.execute_squad()
        assert len(results["results"]["success"]) == 5
