"""Agent Squad Framework - Multi-Agent Orchestration for T-Developer"""

__version__ = "0.1.0"

from typing import Dict, Any, List, Optional
import asyncio
from dataclasses import dataclass

@dataclass
class AgentSquadConfig:
    """Configuration for Agent Squad"""
    max_agents: int = 9
    timeout: int = 300
    retry_count: int = 3
    enable_parallel: bool = True
    
class AgentSquad:
    """Main Agent Squad orchestrator"""
    
    def __init__(self, config: Optional[AgentSquadConfig] = None):
        self.config = config or AgentSquadConfig()
        self.agents: List[Any] = []
        
    async def register_agent(self, agent: Any) -> None:
        """Register an agent to the squad"""
        self.agents.append(agent)
        
    async def execute_pipeline(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent pipeline"""
        result = input_data
        for agent in self.agents:
            if hasattr(agent, 'execute'):
                result = await agent.execute(result)
        return result
        
    async def execute_parallel(self, input_data: Dict[str, Any], agents: List[Any]) -> List[Dict[str, Any]]:
        """Execute agents in parallel"""
        tasks = [agent.execute(input_data) for agent in agents if hasattr(agent, 'execute')]
        return await asyncio.gather(*tasks)

__all__ = ['AgentSquad', 'AgentSquadConfig']