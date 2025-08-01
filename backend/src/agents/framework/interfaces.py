from typing import Any, Dict, List, Optional, Protocol
from abc import ABC, abstractmethod
from dataclasses import dataclass
from .base_agent import AgentStatus

@dataclass
class AgentMessage:
    sender_id: str
    receiver_id: str
    message_type: str
    content: Any
    timestamp: str

@dataclass
class HealthCheckResult:
    healthy: bool
    status: str
    details: Dict[str, Any]

@dataclass
class AgentMetrics:
    execution_count: int
    average_response_time: float
    error_rate: float
    memory_usage: int

@dataclass
class CollaborationTask:
    task_id: str
    description: str
    required_capabilities: List[str]
    priority: int

@dataclass
class CollaborationResult:
    task_id: str
    success: bool
    results: Dict[str, Any]
    participants: List[str]

@dataclass
class WorkflowStep:
    step_id: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str]

@dataclass
class StepResult:
    step_id: str
    success: bool
    output: Any
    error: Optional[str]

class IAgent(Protocol):
    """Core agent interface"""
    
    @property
    def agent_id(self) -> str: ...
    
    @property
    def agent_type(self) -> str: ...
    
    @property
    def version(self) -> str: ...
    
    @property
    def status(self) -> AgentStatus: ...
    
    async def initialize(self) -> None: ...
    
    async def execute(self, input_data: Any) -> Any: ...
    
    async def terminate(self) -> None: ...
    
    async def send_message(self, target_agent_id: str, message: AgentMessage) -> None: ...
    
    async def receive_message(self, message: AgentMessage) -> None: ...
    
    async def save_state(self) -> None: ...
    
    async def load_state(self) -> None: ...
    
    async def health_check(self) -> HealthCheckResult: ...
    
    async def get_metrics(self) -> AgentMetrics: ...

class ICollaborativeAgent(IAgent, Protocol):
    """Extended interface for collaborative agents"""
    
    async def request_collaboration(
        self, 
        agent_ids: List[str], 
        task: CollaborationTask
    ) -> CollaborationResult: ...
    
    async def join_collaboration(self, collaboration_id: str) -> None: ...
    
    async def leave_collaboration(self, collaboration_id: str) -> None: ...
    
    async def participate_in_workflow(self, workflow_id: str, role: str) -> None: ...
    
    async def handle_workflow_step(self, step: WorkflowStep) -> StepResult: ...