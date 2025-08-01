from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TypeVar, Generic
import asyncio
from dataclasses import dataclass
from enum import Enum
import uuid
from datetime import datetime

T = TypeVar('T')
R = TypeVar('R')

class AgentStatus(Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    TERMINATED = "terminated"

@dataclass
class AgentMetadata:
    agent_id: str
    agent_type: str
    version: str
    capabilities: List[str]
    created_at: datetime
    last_active: datetime

@dataclass
class AgentContext:
    project_id: str
    session_id: str
    user_id: str
    parent_agent_id: Optional[str]
    execution_context: Dict[str, Any]
    shared_memory: Dict[str, Any]

class BaseAgent(ABC, Generic[T, R]):
    """Base class for all T-Developer agents"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.agent_id = str(uuid.uuid4())
        self.config = agent_config
        self.status = AgentStatus.IDLE
        self.metadata = self._create_metadata()
        self.context: Optional[AgentContext] = None
        self.logger = self._setup_logger()
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize agent resources and connections"""
        pass
        
    @abstractmethod
    async def execute(self, input_data: T) -> R:
        """Execute agent's primary function"""
        pass
        
    @abstractmethod
    async def validate_input(self, input_data: T) -> bool:
        """Validate input data before processing"""
        pass
        
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up agent resources"""
        pass
    
    def _create_metadata(self) -> AgentMetadata:
        """Create agent metadata"""
        return AgentMetadata(
            agent_id=self.agent_id,
            agent_type=self.config.get('agent_type', 'unknown'),
            version=self.config.get('version', '1.0.0'),
            capabilities=self.config.get('capabilities', []),
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
    
    def _setup_logger(self):
        """Setup agent logger"""
        import logging
        logger = logging.getLogger(f"agent.{self.agent_id}")
        logger.setLevel(logging.INFO)
        return logger
    
    async def set_context(self, context: AgentContext) -> None:
        """Set agent execution context"""
        self.context = context
        self.metadata.last_active = datetime.utcnow()
    
    async def get_status(self) -> AgentStatus:
        """Get current agent status"""
        return self.status
    
    async def update_status(self, status: AgentStatus) -> None:
        """Update agent status"""
        self.status = status
        self.metadata.last_active = datetime.utcnow()