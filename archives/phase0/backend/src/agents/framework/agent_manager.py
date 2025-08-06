"""
T-Developer Agent Manager - Python Implementation
Manages agent lifecycle, registration, and communication
"""

from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass
import asyncio
import logging
from .base_agent import BaseAgent, AgentContext, AgentMessage

logger = logging.getLogger(__name__)

@dataclass
class AgentInfo:
    id: str
    name: str
    type: str
    status: str
    created_at: str

class AgentManager:
    """Manages agent lifecycle and communication"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.registry: Dict[str, Type[BaseAgent]] = {}
        self.event_handlers: Dict[str, List[callable]] = {}
    
    def register_agent_type(self, name: str, agent_class: Type[BaseAgent]) -> None:
        """Register an agent type"""
        self.registry[name] = agent_class
        logger.info(f"Agent type registered: {name}")
    
    async def create_agent(self, agent_type: str, **kwargs) -> str:
        """Create a new agent instance"""
        if agent_type not in self.registry:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = self.registry[agent_type]
        agent = agent_class(**kwargs)
        
        self.agents[agent.agent_id] = agent
        
        # Setup event forwarding
        agent.on('started', lambda data: self._emit('agent:started', data))
        agent.on('stopped', lambda data: self._emit('agent:stopped', data))
        
        logger.info(f"Agent created: {agent.agent_id} ({agent_type})")
        return agent.agent_id
    
    async def start_agent(self, agent_id: str, context: AgentContext) -> None:
        """Start an agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent not found: {agent_id}")
        
        agent = self.agents[agent_id]
        await agent.start(context)
    
    async def stop_agent(self, agent_id: str) -> None:
        """Stop and remove an agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent not found: {agent_id}")
        
        agent = self.agents[agent_id]
        await agent.stop()
        del self.agents[agent_id]
    
    async def send_message(self, agent_id: str, message: AgentMessage) -> AgentMessage:
        """Send message to an agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent not found: {agent_id}")
        
        agent = self.agents[agent_id]
        return await agent.handle_message(message)
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[AgentInfo]:
        """List all agents"""
        return [
            AgentInfo(
                id=agent.agent_id,
                name=agent.name,
                type=agent.agent_type,
                status=agent.status.value,
                created_at=agent.metadata.created_at.isoformat()
            )
            for agent in self.agents.values()
        ]
    
    def get_agent_metrics(self) -> List[Dict[str, Any]]:
        """Get metrics from all agents"""
        return [agent.get_metrics() for agent in self.agents.values()]
    
    def on(self, event: str, handler: callable) -> None:
        """Register event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def _emit(self, event: str, data: Any) -> None:
        """Emit event to handlers"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")