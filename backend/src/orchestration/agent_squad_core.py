"""
T-Developer MVP - Agent Squad Core Orchestration

AWS Agent Squad 기반 멀티 에이전트 오케스트레이션 시스템
"""

import asyncio
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    id: str
    agent_type: str
    input_data: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class AgentSquadOrchestrator:
    """Agent Squad 기반 오케스트레이터"""

    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.task_queue: List[AgentTask] = []
        self.running_tasks: Dict[str, AgentTask] = {}
        self.max_concurrent = 10

    async def register_agent(self, agent_type: str, agent_instance: Any):
        """에이전트 등록"""
        self.agents[agent_type] = agent_instance

    async def execute_task(self, agent_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """단일 태스크 실행"""
        task = AgentTask(id=str(uuid.uuid4()), agent_type=agent_type, input_data=input_data)

        if agent_type not in self.agents:
            raise ValueError(f"Agent type {agent_type} not registered")

        try:
            task.status = TaskStatus.RUNNING
            self.running_tasks[task.id] = task

            agent = self.agents[agent_type]
            result = await agent.execute(input_data)

            task.status = TaskStatus.COMPLETED
            task.result = result

            return result

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            raise
        finally:
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]

    async def execute_workflow(self, workflow: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """워크플로우 실행"""
        results = []

        for step in workflow:
            if step.get("parallel", False):
                # 병렬 실행
                tasks = []
                for agent_config in step["agents"]:
                    task = self.execute_task(agent_config["type"], agent_config["input"])
                    tasks.append(task)

                step_results = await asyncio.gather(*tasks, return_exceptions=True)
                results.extend(step_results)
            else:
                # 순차 실행
                result = await self.execute_task(step["agent_type"], step["input_data"])
                results.append(result)

        return results

    def get_status(self) -> Dict[str, Any]:
        """오케스트레이터 상태 조회"""
        return {
            "registered_agents": list(self.agents.keys()),
            "queued_tasks": len(self.task_queue),
            "running_tasks": len(self.running_tasks),
            "max_concurrent": self.max_concurrent,
        }
