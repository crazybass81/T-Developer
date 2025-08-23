"""Template for generating new agents.

This is a template file used by Agno to generate new agent implementations.
It provides the basic structure that all agents should follow.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from backend.packages.agents.base import BaseAgent, AgentTask, AgentResult, TaskStatus
from backend.packages.memory import ContextType


class {{agent_name}}Agent(BaseAgent):
    """{{purpose}}
    
    This agent is responsible for {{detailed_purpose}}.
    
    Capabilities:
    {{capabilities_list}}
    
    Memory Access:
    - Read: {{memory_read}}
    - Write: {{memory_write}}
    """
    
    def __init__(
        self,
        memory_hub: Optional[MemoryHub] = None,
        **kwargs: Any
    ) -> None:
        """Initialize the {{agent_name}} Agent.
        
        Args:
            memory_hub: Memory Hub instance for context storage
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__(
            name="{{agent_name}}Agent",
            version="{{version}}",
            memory_hub=memory_hub,
            **kwargs
        )
        
        # Agent-specific initialization
        self._initialize_agent()
    
    def _initialize_agent(self) -> None:
        """Initialize agent-specific components."""
        # TODO: Add agent-specific initialization
        pass
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Execute the agent's main task.
        
        Args:
            task: The task to execute containing:
                {{input_descriptions}}
            
        Returns:
            AgentResult containing:
                {{output_descriptions}}
        """
        start_time = time.time()
        
        try:
            # Step 1: Validate input
            if not await self.validate_input(task):
                return self.format_result(
                    success=False,
                    error="Invalid input: {{validation_error_message}}"
                )
            
            # Step 2: Extract parameters
            {{parameter_extraction}}
            
            # Step 3: Read relevant context from memory
            context = await self._read_context(task)
            
            # Step 4: Perform main operation
            result_data = await self._perform_operation(
                {{operation_parameters}},
                context=context
            )
            
            # Step 5: Store results in memory
            await self._store_results(task, result_data)
            
            # Step 6: Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Step 7: Log execution
            await self.log_execution(task, AgentResult(
                success=True,
                status=TaskStatus.COMPLETED,
                data=result_data,
                execution_time_ms=execution_time_ms
            ))
            
            # Step 8: Return formatted result
            return self.format_result(
                success=True,
                data=result_data,
                execution_time_ms=execution_time_ms,
                metadata={"agent": self.name, "version": self.version}
            )
            
        except asyncio.TimeoutError:
            error_msg = "Operation timed out"
            await self.log_execution(task, AgentResult(
                success=False,
                status=TaskStatus.TIMEOUT,
                error=error_msg
            ))
            return self.format_result(success=False, error=error_msg)
            
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            await self.log_execution(task, AgentResult(
                success=False,
                status=TaskStatus.FAILED,
                error=error_msg
            ))
            return self.format_result(success=False, error=error_msg)
    
    async def validate_input(self, task: AgentTask) -> bool:
        """Validate the task input.
        
        Args:
            task: The task to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Call parent validation
        if not await super().validate_input(task):
            return False
        
        # Agent-specific validation
        {{input_validation}}
        
        return True
    
    async def _read_context(self, task: AgentTask) -> Dict[str, Any]:
        """Read relevant context from memory.
        
        Args:
            task: The current task
            
        Returns:
            Context dictionary
        """
        context = {}
        
        if not self.memory_hub:
            return context
        
        # Read from allowed contexts
        {{memory_read_implementation}}
        
        return context
    
    async def _perform_operation(
        self,
        {{operation_signature}},
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform the main agent operation.
        
        Args:
            {{operation_args_docs}}
            context: Context from memory
            
        Returns:
            Operation results
        """
        # Main operation implementation
        {{operation_implementation}}
        
        return {
            {{return_structure}}
        }
    
    async def _store_results(
        self,
        task: AgentTask,
        result_data: Dict[str, Any]
    ) -> None:
        """Store operation results in memory.
        
        Args:
            task: The executed task
            result_data: Results to store
        """
        if not self.memory_hub:
            return
        
        # Store in allowed contexts
        {{memory_write_implementation}}
        
        # Store summary in shared context
        await self.write_memory(
            ContextType.S_CTX,
            f"latest_{{agent_name_lower}}_{task.task_id}",
            {
                "task_id": task.task_id,
                "intent": task.intent,
                "summary": {{result_summary}},
                "timestamp": time.time()
            },
            ttl_seconds=3600,  # Keep for 1 hour
            tags=["{{agent_name_lower}}", "result", task.intent]
        )