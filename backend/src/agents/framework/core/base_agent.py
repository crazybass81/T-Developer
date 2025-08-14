"""Framework Base Agent"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class AgentStatus(Enum):
    """Agent status enum"""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentMessage:
    """Message structure for agent communication"""

    sender: str
    receiver: str
    content: Any
    metadata: Dict[str, Any] = None


@dataclass
class AgentContext:
    """Context for agent execution"""

    request_id: str
    pipeline_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMetadata:
    """Agent metadata"""

    name: str
    version: str
    capabilities: list = field(default_factory=list)


class BaseAgent(ABC):
    """Base class for framework agents"""

    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process input data"""
        pass
