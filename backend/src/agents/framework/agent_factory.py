from typing import Type, Dict, Any, Optional
from abc import ABC, abstractmethod
import importlib
import inspect
from .base_agent import BaseAgent

class AgentFactory:
    """Factory for creating and managing agent instances"""
    
    _registry: Dict[str, Type[BaseAgent]] = {}
    _instances: Dict[str, BaseAgent] = {}
    
    @classmethod
    def register_agent(cls, agent_type: str, agent_class: Type[BaseAgent]) -> None:
        """Register an agent type in the factory"""
        if agent_type in cls._registry:
            raise ValueError(f"Agent type '{agent_type}' is already registered")
        
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"{agent_class} must be a subclass of BaseAgent")
            
        cls._registry[agent_type] = agent_class
    
    @classmethod
    def create_agent(
        cls,
        agent_type: str,
        config: Dict[str, Any],
        singleton: bool = False
    ) -> BaseAgent:
        """Create an agent instance"""
        if agent_type not in cls._registry:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        if singleton and agent_type in cls._instances:
            return cls._instances[agent_type]
        
        agent_class = cls._registry[agent_type]
        agent_instance = agent_class(config)
        
        if singleton:
            cls._instances[agent_type] = agent_instance
            
        return agent_instance
    
    @classmethod
    def discover_agents(cls, module_path: str) -> None:
        """Auto-discover and register agents from a module"""
        module = importlib.import_module(module_path)
        
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseAgent) and 
                obj is not BaseAgent):
                
                agent_type = getattr(obj, 'AGENT_TYPE', name.lower())
                cls.register_agent(agent_type, obj)
    
    @classmethod
    def list_registered_agents(cls) -> Dict[str, Type[BaseAgent]]:
        """Get all registered agent types"""
        return cls._registry.copy()
    
    @classmethod
    def get_agent_info(cls, agent_type: str) -> Dict[str, Any]:
        """Get information about a registered agent type"""
        if agent_type not in cls._registry:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls._registry[agent_type]
        return {
            'type': agent_type,
            'class': agent_class.__name__,
            'module': agent_class.__module__,
            'doc': agent_class.__doc__
        }