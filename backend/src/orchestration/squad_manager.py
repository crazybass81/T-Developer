"""Agent Squad Manager - Coordinates multiple agents < 6.5KB"""
import asyncio
import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class SquadRole(Enum):
    LEADER = "leader"
    WORKER = "worker"
    VALIDATOR = "validator"
    COORDINATOR = "coordinator"


@dataclass
class AgentTask:
    id: str
    agent_name: str
    input_data: Dict[str, Any]
    dependencies: List[str]
    priority: int
    status: str = "pending"
    result: Optional[Dict] = None
    error: Optional[str] = None


class SquadManager:
    def __init__(self, squad_name: str):
        self.squad_name = squad_name
        self.agents: Dict[str, Dict] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self.running_tasks: Set[str] = set()
        self.completed_tasks: Set[str] = set()
        self.task_graph: Dict[str, List[str]] = {}
        self.max_parallel = 10
        self.timeout = 30

    def register_agent(self, agent_name: str, role: SquadRole, capabilities: List[str]):
        """Register agent in squad"""
        self.agents[agent_name] = {
            "role": role,
            "capabilities": capabilities,
            "status": "ready",
            "tasks_completed": 0,
            "last_active": time.time(),
        }

    def add_task(self, task: AgentTask):
        """Add task to execution queue"""
        self.tasks[task.id] = task
        # Build dependency graph
        self.task_graph[task.id] = task.dependencies

    def _get_ready_tasks(self) -> List[str]:
        """Get tasks ready for execution"""
        ready = []
        for task_id, task in self.tasks.items():
            if task.status == "pending":
                # Check if all dependencies are completed
                deps_completed = all(dep in self.completed_tasks for dep in task.dependencies)
                if deps_completed:
                    ready.append(task_id)
        # Sort by priority
        ready.sort(key=lambda x: self.tasks[x].priority, reverse=True)
        return ready[: self.max_parallel - len(self.running_tasks)]

    async def execute_squad(self) -> Dict[str, Any]:
        """Execute all tasks with squad coordination"""
        results = {"success": [], "failed": [], "skipped": []}

        while self.tasks:
            # Get ready tasks
            ready_tasks = self._get_ready_tasks()

            if not ready_tasks and not self.running_tasks:
                # No tasks can run - check for cycles
                pending = [t for t in self.tasks if self.tasks[t].status == "pending"]
                if pending:
                    results["failed"].extend(pending)
                    break

            # Start ready tasks
            tasks_to_run = []
            for task_id in ready_tasks:
                task = self.tasks[task_id]
                task.status = "running"
                self.running_tasks.add(task_id)
                tasks_to_run.append(self._execute_task(task))

            if tasks_to_run:
                # Execute in parallel
                task_results = await asyncio.gather(*tasks_to_run, return_exceptions=True)

                # Process results
                for task_id, result in zip(ready_tasks, task_results):
                    self.running_tasks.remove(task_id)
                    task = self.tasks[task_id]

                    if isinstance(result, Exception):
                        task.status = "failed"
                        task.error = str(result)
                        results["failed"].append(task_id)
                    else:
                        task.status = "completed"
                        task.result = result
                        self.completed_tasks.add(task_id)
                        results["success"].append(task_id)

                    # Remove completed task
                    del self.tasks[task_id]

            else:
                # Wait a bit if nothing to run
                await asyncio.sleep(0.1)

        return {
            "squad": self.squad_name,
            "results": results,
            "agents": self.agents,
            "execution_time": time.time(),
        }

    async def _execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute single task"""
        try:
            # Get agent for task
            agent = self.agents.get(task.agent_name)
            if not agent:
                raise ValueError(f"Agent {task.agent_name} not found")

            # Update agent status
            agent["status"] = "busy"
            agent["last_active"] = time.time()

            # Simulate agent execution (replace with actual agent call)
            await asyncio.sleep(0.1)  # Simulated work

            # Update agent metrics
            agent["tasks_completed"] += 1
            agent["status"] = "ready"

            return {
                "task_id": task.id,
                "agent": task.agent_name,
                "status": "success",
                "data": {"processed": True},
            }

        except Exception as e:
            if task.agent_name in self.agents:
                self.agents[task.agent_name]["status"] = "ready"
            raise e

    def get_squad_status(self) -> Dict[str, Any]:
        """Get current squad status"""
        return {
            "squad_name": self.squad_name,
            "total_agents": len(self.agents),
            "ready_agents": sum(1 for a in self.agents.values() if a["status"] == "ready"),
            "busy_agents": sum(1 for a in self.agents.values() if a["status"] == "busy"),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == "pending"]),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
        }

    def validate_task_graph(self) -> bool:
        """Check for cycles in task dependencies"""
        visited = set()
        rec_stack = set()

        def has_cycle(task_id):
            visited.add(task_id)
            rec_stack.add(task_id)

            for dep in self.task_graph.get(task_id, []):
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True

            rec_stack.remove(task_id)
            return False

        for task_id in self.task_graph:
            if task_id not in visited:
                if has_cycle(task_id):
                    return False
        return True

    def get_execution_plan(self) -> List[List[str]]:
        """Get parallel execution plan"""
        plan = []
        temp_completed = set()
        temp_tasks = dict(self.tasks)

        while temp_tasks:
            batch = []
            for task_id, task in temp_tasks.items():
                if task.status == "pending":
                    deps_met = all(d in temp_completed for d in task.dependencies)
                    if deps_met:
                        batch.append(task_id)

            if not batch:
                break

            plan.append(batch)
            temp_completed.update(batch)
            for task_id in batch:
                del temp_tasks[task_id]

        return plan


# Example usage
if __name__ == "__main__":

    async def test_squad():
        squad = SquadManager("test_squad")

        # Register agents
        squad.register_agent("nl_input", SquadRole.LEADER, ["parsing", "validation"])
        squad.register_agent("parser", SquadRole.WORKER, ["parsing", "extraction"])
        squad.register_agent("generator", SquadRole.WORKER, ["generation", "synthesis"])

        # Add tasks with dependencies
        squad.add_task(AgentTask("t1", "nl_input", {"text": "test"}, [], 10))
        squad.add_task(AgentTask("t2", "parser", {"data": "test"}, ["t1"], 5))
        squad.add_task(AgentTask("t3", "generator", {"template": "test"}, ["t2"], 1))

        # Validate graph
        if not squad.validate_task_graph():
            print("Error: Circular dependencies detected")
            return

        # Get execution plan
        plan = squad.get_execution_plan()
        print(f"Execution plan: {plan}")

        # Execute squad
        results = await squad.execute_squad()
        print(f"Results: {json.dumps(results, indent=2)}")

    asyncio.run(test_squad())
