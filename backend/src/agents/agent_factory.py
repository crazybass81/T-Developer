# backend/src/agents/agent_factory.py
from typing import Dict, Any, Optional
from .implementations.component_decision_agent import ComponentDecisionAgent
from .implementations.match_rate_agent import MatchRateAgent
from .implementations.search_agent import SearchAgent
from .implementations.generation_agent import GenerationAgent

class AgentFactory:
    """T-Developer 에이전트 팩토리"""
    
    _instances: Dict[str, Any] = {}
    
    @classmethod
    async def get_agent(cls, agent_type: str, config: Optional[Dict[str, Any]] = None) -> Any:
        """에이전트 인스턴스 반환 (싱글톤)"""
        
        if agent_type not in cls._instances:
            cls._instances[agent_type] = await cls._create_agent(agent_type, config)
        
        return cls._instances[agent_type]
    
    @classmethod
    async def _create_agent(cls, agent_type: str, config: Optional[Dict[str, Any]]) -> Any:
        """에이전트 생성"""
        
        agents = {
            'component_decision': ComponentDecisionAgent,
            'match_rate': MatchRateAgent,
            'search': SearchAgent,
            'generation': GenerationAgent
        }
        
        if agent_type not in agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = agents[agent_type]
        
        if config:
            return agent_class(**config)
        else:
            return agent_class()
    
    @classmethod
    def list_available_agents(cls) -> list:
        """사용 가능한 에이전트 목록"""
        return [
            'component_decision',
            'match_rate', 
            'search',
            'generation'
        ]
    
    @classmethod
    async def initialize_all_agents(cls) -> Dict[str, Any]:
        """모든 에이전트 초기화"""
        
        agents = {}
        
        for agent_type in cls.list_available_agents():
            try:
                agents[agent_type] = await cls.get_agent(agent_type)
                print(f"✅ {agent_type} agent initialized")
            except Exception as e:
                print(f"❌ Failed to initialize {agent_type} agent: {e}")
        
        return agents