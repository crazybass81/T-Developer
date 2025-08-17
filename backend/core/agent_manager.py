#!/usr/bin/env python3
"""Agent Manager for T-Developer - manages agent lifecycle and task execution."""

import asyncio
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent))

from backend.packages.agents.base import AgentInput, AgentOutput, AgentStatus, BaseAgent
from backend.packages.agents.code_analysis import CodeAnalysisAgent
from backend.packages.agents.evaluator import EvaluatorAgent
from backend.packages.agents.planner import PlannerAgent
from backend.packages.agents.refactor import RefactorAgent
from backend.packages.agents.research import ResearchAgent

logger = logging.getLogger(__name__)


@dataclass
class AgentTask:
    """Represents a task for an agent."""

    id: str
    agent_type: str
    input: AgentInput
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: Optional[AgentOutput] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class AgentManager:
    """Manages agent instances and task execution."""

    def __init__(self):
        """Initialize agent manager."""
        self.agents: dict[str, BaseAgent] = {}
        self.tasks: dict[str, AgentTask] = {}
        self.task_queue: Optional[asyncio.Queue] = None
        self.running = False
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize agent instances using existing implementations."""
        try:
            # Try to import and use ResearchConfig for proper initialization
            from packages.agents.research import ResearchConfig

            # Initialize each agent with proper config objects
            research_config = ResearchConfig(
                max_files_to_scan=100,
                enable_reference_search=True,  # Enable external search
                enable_ai_analysis=True,  # Enable AI analysis
            )
            self.agents["research"] = ResearchAgent(name="research", config=research_config)
            logger.info("Initialized ResearchAgent")

            # Initialize CodeAnalysisAgent
            from packages.agents.code_analysis import CodeAnalysisConfig

            code_analysis_config = CodeAnalysisConfig(
                max_files_to_scan=50, enable_deep_analysis=True
            )
            self.agents["code_analysis"] = CodeAnalysisAgent(
                name="code_analysis", config=code_analysis_config
            )
            logger.info("Initialized CodeAnalysisAgent")

            # PlannerAgent needs PlannerConfig
            from packages.agents.planner import PlannerConfig

            planner_config = PlannerConfig(
                max_hours_per_task=4.0, enable_ai_planning=False  # Disable AI for now
            )
            self.agents["planner"] = PlannerAgent(name="planner", config=planner_config)
            logger.info("Initialized PlannerAgent")

            # RefactorAgent needs RefactorConfig
            from packages.agents.refactor import RefactorConfig

            refactor_config = RefactorConfig(
                use_claude_code=False,  # Use our SimpleRefactor instead
                create_pull_request=False,
                auto_commit=False,
                sandbox_mode=False,  # Enable actual modifications
            )
            self.agents["refactor"] = RefactorAgent(name="refactor", config=refactor_config)
            logger.info("Initialized RefactorAgent")

            # EvaluatorAgent needs EvaluatorConfig
            from packages.agents.evaluator import EvaluatorConfig

            evaluator_config = EvaluatorConfig(
                measure_coverage=False,  # Disable coverage for now
                run_tests=False,  # Disable tests for now
                analyze_complexity=False,  # Disable complexity for now
                check_documentation=True,  # Enable doc checking
            )
            self.agents["evaluator"] = EvaluatorAgent(name="evaluator", config=evaluator_config)
            logger.info("Initialized EvaluatorAgent")

        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            # Use mock agents if real ones fail
            self._use_mock_agents()

    def _use_mock_agents(self):
        """Use mock agents for testing when real agents unavailable."""
        logger.warning("Using mock agents for testing")

        class MockAgent(BaseAgent):
            async def execute(self, input: AgentInput) -> AgentOutput:
                await asyncio.sleep(1)  # Simulate work
                return AgentOutput(
                    task_id=input.task_id, status=AgentStatus.OK, metrics={"mock": True}
                )

            def validate(self, input: AgentInput) -> bool:
                """Validate input - always return True for mock."""
                return True

            def get_capabilities(self) -> dict[str, Any]:
                """Get agent capabilities."""
                return {"type": self.name, "mock": True, "capabilities": ["simulate"]}

        for agent_type in ["research", "code_analysis", "planner", "refactor", "evaluator"]:
            self.agents[agent_type] = MockAgent(name=agent_type)

    async def submit_task(self, agent_type: str, payload: dict[str, Any]) -> str:
        """Submit a task to an agent.

        Args:
            agent_type: Type of agent (research, planner, refactor, evaluator)
            payload: Task payload

        Returns:
            Task ID
        """
        task_id = str(uuid4())

        agent_input = AgentInput(
            intent=agent_type,
            task_id=task_id,
            payload=payload,
            context={"timestamp": datetime.now().isoformat()},
        )

        task = AgentTask(id=task_id, agent_type=agent_type, input=agent_input)

        self.tasks[task_id] = task

        # Ensure queue is initialized
        if self.task_queue is None:
            self.task_queue = asyncio.Queue()

        await self.task_queue.put(task)

        logger.info(f"Submitted task {task_id} to {agent_type} agent")
        return task_id

    async def execute_task(self, task: AgentTask) -> AgentOutput:
        """Execute a single task.

        Args:
            task: Task to execute

        Returns:
            Agent output
        """
        agent = self.agents.get(task.agent_type)
        if not agent:
            raise ValueError(f"Unknown agent type: {task.agent_type}")

        task.status = "running"
        task.started_at = datetime.now()

        try:
            logger.info(f"Executing task {task.id} with {task.agent_type} agent")
            output = await agent.execute(task.input)

            task.status = "completed"
            task.completed_at = datetime.now()
            task.output = output

            logger.info(f"Task {task.id} completed successfully")
            return output

        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            task.status = "failed"
            task.completed_at = datetime.now()
            task.error = str(e)

            return AgentOutput(task_id=task.id, status=AgentStatus.FAIL, error=str(e))

    async def start_worker(self):
        """Start background worker to process tasks."""
        # Initialize queue in the correct event loop
        if self.task_queue is None:
            self.task_queue = asyncio.Queue()

        self.running = True
        logger.info("Agent manager worker started")

        while self.running:
            try:
                # Wait for task with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)

                # Execute task
                await self.execute_task(task)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")

    def stop_worker(self):
        """Stop background worker."""
        self.running = False
        self.task_queue = None
        logger.info("Agent manager worker stopped")

    def get_task_status(self, task_id: str) -> Optional[dict[str, Any]]:
        """Get status of a task.

        Args:
            task_id: Task ID

        Returns:
            Task status dictionary
        """
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "id": task.id,
            "agent_type": task.agent_type,
            "status": task.status,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error": task.error,
            "output": task.output.__dict__ if task.output else None,
        }

    def get_agent_status(self) -> list[dict[str, Any]]:
        """Get status of all agents.

        Returns:
            List of agent status dictionaries
        """
        status = []
        for agent_type, agent in self.agents.items():
            # Count tasks for this agent
            total_tasks = sum(1 for t in self.tasks.values() if t.agent_type == agent_type)
            completed_tasks = sum(
                1
                for t in self.tasks.values()
                if t.agent_type == agent_type and t.status == "completed"
            )
            failed_tasks = sum(
                1
                for t in self.tasks.values()
                if t.agent_type == agent_type and t.status == "failed"
            )

            status.append(
                {
                    "type": agent_type,
                    "name": agent.name,
                    "status": "ready",  # Simplified for now
                    "metrics": {
                        "total_tasks": total_tasks,
                        "completed_tasks": completed_tasks,
                        "failed_tasks": failed_tasks,
                        "success_rate": (completed_tasks / total_tasks * 100)
                        if total_tasks > 0
                        else 0,
                    },
                }
            )

        return status


# Singleton instance
_manager_instance: Optional[AgentManager] = None


def get_agent_manager() -> AgentManager:
    """Get singleton agent manager instance."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = AgentManager()
    return _manager_instance
