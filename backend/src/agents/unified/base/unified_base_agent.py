"""Unified Base Agent - Core abstractions for all agents"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from src.core.interfaces import AgentResult as CoreAgentResult
from src.core.interfaces import ProcessingStatus


@dataclass
class AgentConfig:
    """Configuration for unified agents"""

    name: str
    version: str = "1.0.0"
    max_retries: int = 3
    timeout: int = 30
    memory_limit_kb: int = 6500  # 6.5KB limit
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentContext:
    """Context for agent execution"""

    pipeline_id: str
    request_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from agent execution"""

    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedBaseAgent(ABC):
    """Base class for all unified agents"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self._initialized = False

    @abstractmethod
    async def process(self, input_data: Any, context: AgentContext) -> AgentResult:
        """Process input and return result"""
        pass

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data"""
        pass

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "initialized": self._initialized,
        }
