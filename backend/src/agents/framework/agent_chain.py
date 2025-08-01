# backend/src/agents/framework/agent_chain.py
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio

class ChainType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"

@dataclass
class ChainStep:
    agent_id: str
    action: str
    inputs: Dict[str, Any]
    condition: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class AgentChain:
    id: str
    name: str
    type: ChainType
    steps: List[ChainStep]
    context: Dict[str, Any] = None

class AgentChainManager:
    def __init__(self):
        self.chains: Dict[str, AgentChain] = {}
        self.agent_handlers: Dict[str, Callable] = {}
        self.chain_results: Dict[str, Dict[str, Any]] = {}
    
    def register_agent_handler(self, agent_id: str, handler: Callable):
        self.agent_handlers[agent_id] = handler
    
    def create_chain(self, name: str, chain_type: ChainType, steps: List[ChainStep]) -> str:
        import uuid
        chain_id = str(uuid.uuid4())
        chain = AgentChain(
            id=chain_id,
            name=name,
            type=chain_type,
            steps=steps,
            context={}
        )
        self.chains[chain_id] = chain
        return chain_id
    
    async def execute_chain(self, chain_id: str, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        chain = self.chains.get(chain_id)
        if not chain:
            raise ValueError(f"Chain {chain_id} not found")
        
        chain.context.update(initial_input)
        
        if chain.type == ChainType.SEQUENTIAL:
            return await self._execute_sequential(chain)
        elif chain.type == ChainType.PARALLEL:
            return await self._execute_parallel(chain)
        elif chain.type == ChainType.CONDITIONAL:
            return await self._execute_conditional(chain)
        elif chain.type == ChainType.LOOP:
            return await self._execute_loop(chain)
    
    async def _execute_sequential(self, chain: AgentChain) -> Dict[str, Any]:
        results = {}
        current_context = chain.context.copy()
        
        for step in chain.steps:
            if step.condition and not self._evaluate_condition(step.condition, current_context):
                continue
            
            result = await self._execute_step(step, current_context)
            results[step.agent_id] = result
            current_context.update(result)
        
        return results
    
    async def _execute_parallel(self, chain: AgentChain) -> Dict[str, Any]:
        tasks = []
        for step in chain.steps:
            if not step.condition or self._evaluate_condition(step.condition, chain.context):
                task = asyncio.create_task(self._execute_step(step, chain.context))
                tasks.append((step.agent_id, task))
        
        results = {}
        for agent_id, task in tasks:
            results[agent_id] = await task
        
        return results
    
    async def _execute_conditional(self, chain: AgentChain) -> Dict[str, Any]:
        for step in chain.steps:
            if step.condition and self._evaluate_condition(step.condition, chain.context):
                result = await self._execute_step(step, chain.context)
                return {step.agent_id: result}
        return {}
    
    async def _execute_loop(self, chain: AgentChain) -> Dict[str, Any]:
        results = []
        current_context = chain.context.copy()
        max_iterations = current_context.get('max_iterations', 10)
        
        for i in range(max_iterations):
            iteration_results = {}
            should_continue = False
            
            for step in chain.steps:
                if step.condition and not self._evaluate_condition(step.condition, current_context):
                    continue
                
                result = await self._execute_step(step, current_context)
                iteration_results[step.agent_id] = result
                current_context.update(result)
                
                if result.get('continue_loop', False):
                    should_continue = True
            
            results.append(iteration_results)
            if not should_continue:
                break
        
        return {'iterations': results}
    
    async def _execute_step(self, step: ChainStep, context: Dict[str, Any]) -> Dict[str, Any]:
        handler = self.agent_handlers.get(step.agent_id)
        if not handler:
            raise ValueError(f"No handler for agent {step.agent_id}")
        
        inputs = step.inputs.copy()
        inputs.update(context)
        
        for attempt in range(step.max_retries + 1):
            try:
                return await handler(step.action, inputs)
            except Exception as e:
                if attempt == step.max_retries:
                    raise e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False