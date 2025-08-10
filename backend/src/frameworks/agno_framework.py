"""
Agno Framework Integration
Lightweight agent framework with minimal memory footprint (6.5KB target)
"""
import asyncio
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, TypeVar, Generic
from enum import Enum
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class AgnoConfig:
    """Agno framework configuration"""
    max_memory_kb: float = 6.5
    max_execution_time: int = 30
    enable_caching: bool = True
    enable_monitoring: bool = True
    retry_attempts: int = 3
    retry_delay: int = 1


@dataclass
class AgentContext:
    """Shared context for agent execution"""
    request_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    memory_usage: float = 0.0
    execution_time: float = 0.0


@dataclass
class AgentInput(Generic[T]):
    """Generic input wrapper for agents"""
    data: T
    context: AgentContext
    previous_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AgentResult(Generic[R]):
    """Generic result wrapper for agents"""
    agent_name: str
    status: AgentStatus
    data: Optional[R] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_usage: float = 0.0
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgnoTool(ABC):
    """Base class for Agno tools"""
    
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute tool"""
        pass


class AgnoAgent(ABC, Generic[T, R]):
    """Base Agno agent class with minimal memory footprint"""
    
    def __init__(self, name: str, config: Optional[AgnoConfig] = None):
        self.name = name
        self.config = config or AgnoConfig()
        self.tools: Dict[str, AgnoTool] = {}
        self.cache: Dict[str, Any] = {}
        self._status = AgentStatus.IDLE
        self._metrics: Dict[str, Any] = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0
        }
    
    @abstractmethod
    async def process(self, input_data: AgentInput[T]) -> AgentResult[R]:
        """Process input and return result"""
        pass
    
    def register_tool(self, tool: AgnoTool) -> None:
        """Register a tool for the agent"""
        self.tools[tool.name()] = tool
        logger.debug(f"Registered tool {tool.name()} for agent {self.name}")
    
    async def use_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """Use a registered tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not registered")
        
        tool = self.tools[tool_name]
        return await tool.execute(*args, **kwargs)
    
    def get_cache_key(self, input_data: Any) -> str:
        """Generate cache key for input"""
        import hashlib
        data_str = json.dumps(input_data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if self.config.enable_caching:
            return self.cache.get(key)
        return None
    
    def set_cache(self, key: str, value: Any) -> None:
        """Set value in cache"""
        if self.config.enable_caching:
            # Simple LRU implementation
            if len(self.cache) >= 100:  # Max 100 items
                # Remove oldest item
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self.cache[key] = value
    
    def clear_cache(self) -> None:
        """Clear agent cache"""
        self.cache.clear()
    
    async def execute(self, input_data: AgentInput[T]) -> AgentResult[R]:
        """Execute agent with monitoring and error handling"""
        start_time = time.time()
        self._status = AgentStatus.RUNNING
        
        try:
            # Check cache
            cache_key = self.get_cache_key(input_data.data)
            cached_result = self.get_from_cache(cache_key)
            if cached_result is not None:
                logger.debug(f"Agent {self.name}: Cache hit")
                return cached_result
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self.process(input_data),
                timeout=self.config.max_execution_time
            )
            
            # Update metrics
            execution_time = time.time() - start_time
            self._update_metrics(True, execution_time)
            
            # Set result metadata
            result.execution_time = execution_time
            result.memory_usage = self._estimate_memory_usage()
            
            # Cache result
            self.set_cache(cache_key, result)
            
            self._status = AgentStatus.COMPLETED
            return result
            
        except asyncio.TimeoutError:
            self._status = AgentStatus.TIMEOUT
            self._update_metrics(False, self.config.max_execution_time)
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.TIMEOUT,
                error=f"Agent execution timeout ({self.config.max_execution_time}s)",
                execution_time=self.config.max_execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._status = AgentStatus.FAILED
            self._update_metrics(False, execution_time)
            logger.error(f"Agent {self.name} failed: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
    
    def _update_metrics(self, success: bool, execution_time: float) -> None:
        """Update agent metrics"""
        self._metrics['total_executions'] += 1
        if success:
            self._metrics['successful_executions'] += 1
        else:
            self._metrics['failed_executions'] += 1
        
        self._metrics['total_execution_time'] += execution_time
        self._metrics['average_execution_time'] = (
            self._metrics['total_execution_time'] / 
            self._metrics['total_executions']
        )
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in KB"""
        import sys
        
        # Rough estimation of agent memory usage
        size = sys.getsizeof(self.cache)
        size += sys.getsizeof(self.tools)
        size += sys.getsizeof(self._metrics)
        
        return size / 1024  # Convert to KB
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        return {
            **self._metrics,
            'status': self._status.value,
            'cache_size': len(self.cache),
            'tools_registered': len(self.tools),
            'estimated_memory_kb': self._estimate_memory_usage()
        }
    
    def reset_metrics(self) -> None:
        """Reset agent metrics"""
        self._metrics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0
        }


class AgnoOrchestrator:
    """Orchestrator for managing multiple Agno agents"""
    
    def __init__(self, config: Optional[AgnoConfig] = None):
        self.config = config or AgnoConfig()
        self.agents: Dict[str, AgnoAgent] = {}
        self.pipelines: Dict[str, List[str]] = {}
    
    def register_agent(self, agent: AgnoAgent) -> None:
        """Register an agent"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def create_pipeline(self, name: str, agent_names: List[str]) -> None:
        """Create an agent pipeline"""
        # Validate agents exist
        for agent_name in agent_names:
            if agent_name not in self.agents:
                raise ValueError(f"Agent {agent_name} not registered")
        
        self.pipelines[name] = agent_names
        logger.info(f"Created pipeline {name} with agents: {agent_names}")
    
    async def execute_pipeline(self, pipeline_name: str, 
                              initial_input: Any,
                              context: Optional[AgentContext] = None) -> List[AgentResult]:
        """Execute a pipeline of agents"""
        if pipeline_name not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_name} not found")
        
        agent_names = self.pipelines[pipeline_name]
        results = []
        current_input = initial_input
        
        if context is None:
            import uuid
            context = AgentContext(request_id=str(uuid.uuid4()))
        
        for agent_name in agent_names:
            agent = self.agents[agent_name]
            
            # Prepare input
            agent_input = AgentInput(
                data=current_input,
                context=context,
                previous_results=results.copy()
            )
            
            # Execute agent
            result = await agent.execute(agent_input)
            results.append(result)
            
            # Check for failure
            if result.status == AgentStatus.FAILED:
                logger.error(f"Pipeline {pipeline_name} failed at agent {agent_name}")
                break
            
            # Use result as input for next agent
            current_input = result.data
        
        return results
    
    async def execute_parallel(self, agent_names: List[str], 
                              input_data: Any,
                              context: Optional[AgentContext] = None) -> List[AgentResult]:
        """Execute multiple agents in parallel"""
        if context is None:
            import uuid
            context = AgentContext(request_id=str(uuid.uuid4()))
        
        tasks = []
        for agent_name in agent_names:
            if agent_name not in self.agents:
                logger.warning(f"Agent {agent_name} not found, skipping")
                continue
            
            agent = self.agents[agent_name]
            agent_input = AgentInput(
                data=input_data,
                context=context,
                previous_results=[]
            )
            
            tasks.append(agent.execute(agent_input))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(AgentResult(
                    agent_name=agent_names[i],
                    status=AgentStatus.FAILED,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics for all agents"""
        return {
            agent_name: agent.get_metrics()
            for agent_name, agent in self.agents.items()
        }
    
    def reset_all_metrics(self) -> None:
        """Reset metrics for all agents"""
        for agent in self.agents.values():
            agent.reset_metrics()
    
    def clear_all_caches(self) -> None:
        """Clear caches for all agents"""
        for agent in self.agents.values():
            agent.clear_cache()


# Example tool implementation
class HTTPTool(AgnoTool):
    """HTTP request tool"""
    
    def name(self) -> str:
        return "http_request"
    
    def description(self) -> str:
        return "Make HTTP requests"
    
    async def execute(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Execute HTTP request"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                return {
                    'status': response.status,
                    'headers': dict(response.headers),
                    'body': await response.text()
                }


class DatabaseTool(AgnoTool):
    """Database query tool"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def name(self) -> str:
        return "database_query"
    
    def description(self) -> str:
        return "Execute database queries"
    
    async def execute(self, query: str, params: Dict = None) -> List[Dict]:
        """Execute database query"""
        # Placeholder for actual database implementation
        return [{"result": "placeholder"}]


# Export classes and functions
__all__ = [
    'AgentStatus',
    'AgnoConfig',
    'AgentContext',
    'AgentInput',
    'AgentResult',
    'AgnoTool',
    'AgnoAgent',
    'AgnoOrchestrator',
    'HTTPTool',
    'DatabaseTool'
]