from typing import Dict, Any, Optional
import asyncio
from dataclasses import dataclass
from datetime import datetime
from .base_agent import BaseAgent, AgentStatus
from .lifecycle import LifecycleEvent

@dataclass
class TerminationOptions:
    """Options for agent termination"""
    wait_for_completion: bool = True
    completion_timeout: int = 30000  # milliseconds
    save_state: bool = True
    force_timeout: int = 5000  # milliseconds

@dataclass
class TerminationResult:
    """Result of agent termination"""
    agent_id: str
    success: bool = False
    forced_shutdown: bool = False
    error: Optional[str] = None
    terminated_at: Optional[datetime] = None
    duration_ms: int = 0

class AgentTerminator:
    """Manages agent termination process"""
    
    def __init__(self):
        self.graceful_shutdown_timeout = 30000  # 30 seconds
        self.force_shutdown_timeout = 5000  # 5 seconds
    
    async def terminate_agent(
        self,
        agent: BaseAgent,
        options: TerminationOptions = None
    ) -> TerminationResult:
        """Terminate agent with proper cleanup"""
        
        if options is None:
            options = TerminationOptions()
        
        result = TerminationResult(agent_id=agent.agent_id)
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Signal termination intent
            await self._signal_termination(agent)
            
            # Step 2: Stop accepting new tasks
            await self._stop_accepting_tasks(agent)
            
            # Step 3: Wait for current tasks to complete
            if options.wait_for_completion:
                await self._wait_for_task_completion(agent, options.completion_timeout)
            
            # Step 4: Save agent state
            if options.save_state:
                await self._save_final_state(agent)
            
            # Step 5: Cleanup resources
            await self._cleanup_resources(agent)
            
            # Step 6: Graceful shutdown
            await asyncio.wait_for(
                self._graceful_shutdown(agent),
                timeout=self.graceful_shutdown_timeout / 1000
            )
            
            result.success = True
            result.terminated_at = datetime.utcnow()
            
        except asyncio.TimeoutError:
            # Force shutdown if graceful fails
            await self._force_shutdown(agent)
            result.forced_shutdown = True
            result.error = "Graceful shutdown timeout, forced termination"
            
        except Exception as e:
            await self._force_shutdown(agent)
            result.forced_shutdown = True
            result.error = str(e)
        
        finally:
            result.duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        return result
    
    async def _signal_termination(self, agent: BaseAgent) -> None:
        """Signal termination intent to agent"""
        if hasattr(agent, 'lifecycle'):
            await agent.lifecycle.transition_to(LifecycleEvent.STOPPING)
        await agent.update_status(AgentStatus.TERMINATED)
    
    async def _stop_accepting_tasks(self, agent: BaseAgent) -> None:
        """Stop agent from accepting new tasks"""
        if hasattr(agent, 'accepting_tasks'):
            agent.accepting_tasks = False
    
    async def _wait_for_task_completion(self, agent: BaseAgent, timeout: int) -> None:
        """Wait for current tasks to complete"""
        start_time = datetime.utcnow()
        
        while self._has_active_tasks(agent):
            if (datetime.utcnow() - start_time).total_seconds() * 1000 > timeout:
                raise asyncio.TimeoutError("Task completion timeout")
            
            await asyncio.sleep(0.1)
    
    async def _save_final_state(self, agent: BaseAgent) -> None:
        """Save agent's final state"""
        if hasattr(agent, 'save_state'):
            await agent.save_state()
    
    async def _cleanup_resources(self, agent: BaseAgent) -> None:
        """Cleanup agent resources"""
        await agent.cleanup()
    
    async def _graceful_shutdown(self, agent: BaseAgent) -> None:
        """Perform graceful shutdown"""
        if hasattr(agent, 'lifecycle'):
            await agent.lifecycle.transition_to(LifecycleEvent.STOPPED)
            await agent.lifecycle.transition_to(LifecycleEvent.TERMINATED)
    
    async def _force_shutdown(self, agent: BaseAgent) -> None:
        """Force shutdown agent"""
        try:
            if hasattr(agent, 'lifecycle'):
                await agent.lifecycle.transition_to(LifecycleEvent.TERMINATED)
            await agent.update_status(AgentStatus.TERMINATED)
        except Exception:
            pass  # Ignore errors during force shutdown
    
    def _has_active_tasks(self, agent: BaseAgent) -> bool:
        """Check if agent has active tasks"""
        return (hasattr(agent, 'active_tasks') and 
                getattr(agent, 'active_tasks', 0) > 0)