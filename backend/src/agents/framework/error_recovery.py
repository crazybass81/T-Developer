# backend/src/agents/framework/error_recovery.py
from typing import Dict, Any, List, Optional, Callable
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from .error_handling import AgentError, ErrorCategory
from datetime import datetime

@dataclass
class RecoveryStrategy:
    name: str
    description: str
    applicable_errors: List[ErrorCategory]
    max_attempts: int = 3
    backoff_multiplier: float = 2.0

class RecoveryAction(ABC):
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> bool:
        pass

class RetryAction(RecoveryAction):
    def __init__(self, delay: float = 1.0):
        self.delay = delay
    
    async def execute(self, context: Dict[str, Any]) -> bool:
        await asyncio.sleep(self.delay)
        return True

class RestartAction(RecoveryAction):
    async def execute(self, context: Dict[str, Any]) -> bool:
        agent = context.get('agent')
        if agent:
            await agent.restart()
            return True
        return False

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def can_execute(self) -> bool:
        if self.state == 'closed':
            return True
        elif self.state == 'open':
            if self.last_failure_time and \
               (asyncio.get_event_loop().time() - self.last_failure_time) > self.recovery_timeout:
                self.state = 'half-open'
                return True
            return False
        else:  # half-open
            return True
    
    def record_success(self):
        self.failure_count = 0
        self.state = 'closed'
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'

class CompensationAction(RecoveryAction):
    def __init__(self, compensation_func: Callable):
        self.compensation_func = compensation_func
    
    async def execute(self, context: Dict[str, Any]) -> bool:
        try:
            await self.compensation_func(context)
            return True
        except Exception:
            return False

class FallbackAction(RecoveryAction):
    def __init__(self, fallback_func: Callable):
        self.fallback_func = fallback_func
    
    async def execute(self, context: Dict[str, Any]) -> bool:
        try:
            result = await self.fallback_func(context)
            context['fallback_result'] = result
            return True
        except Exception:
            return False

class ErrorRecoveryManager:
    def __init__(self):
        self.strategies: Dict[str, RecoveryStrategy] = {}
        self.recovery_actions: Dict[str, RecoveryAction] = {
            'retry': RetryAction(),
            'restart': RestartAction()
        }
        self.recovery_history: List[Dict] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.compensation_handlers: Dict[str, Callable] = {}
        self.fallback_handlers: Dict[str, Callable] = {}
    
    def register_strategy(self, strategy: RecoveryStrategy, action: RecoveryAction):
        self.strategies[strategy.name] = strategy
        self.recovery_actions[strategy.name] = action
    
    def register_compensation_handler(self, error_type: str, handler: Callable):
        self.compensation_handlers[error_type] = handler
    
    def register_fallback_handler(self, error_type: str, handler: Callable):
        self.fallback_handlers[error_type] = handler
    
    def get_circuit_breaker(self, agent_id: str) -> CircuitBreaker:
        if agent_id not in self.circuit_breakers:
            self.circuit_breakers[agent_id] = CircuitBreaker()
        return self.circuit_breakers[agent_id]
    
    async def recover_from_error(self, error: AgentError, context: Dict[str, Any]) -> bool:
        agent_id = context.get('agent_id', 'unknown')
        circuit_breaker = self.get_circuit_breaker(agent_id)
        
        if not circuit_breaker.can_execute():
            return await self._execute_fallback(error, context)
        
        applicable_strategies = [
            s for s in self.strategies.values()
            if error.category in s.applicable_errors
        ]
        
        for strategy in applicable_strategies:
            if await self._attempt_recovery(strategy, error, context):
                circuit_breaker.record_success()
                return True
        
        circuit_breaker.record_failure()
        return await self._execute_fallback(error, context)
    
    async def _attempt_recovery(self, strategy: RecoveryStrategy, error: AgentError, context: Dict[str, Any]) -> bool:
        action = self.recovery_actions.get(strategy.name)
        if not action:
            return False
        
        for attempt in range(strategy.max_attempts):
            try:
                delay = strategy.backoff_multiplier ** attempt
                await asyncio.sleep(delay)
                
                if await action.execute(context):
                    self.recovery_history.append({
                        'strategy': strategy.name,
                        'error': error.error_code,
                        'attempt': attempt + 1,
                        'success': True,
                        'timestamp': asyncio.get_event_loop().time()
                    })
                    return True
            except Exception as e:
                self.recovery_history.append({
                    'strategy': strategy.name,
                    'error': error.error_code,
                    'attempt': attempt + 1,
                    'success': False,
                    'exception': str(e),
                    'timestamp': asyncio.get_event_loop().time()
                })
                continue
        
        return False
    
    async def _execute_fallback(self, error: AgentError, context: Dict[str, Any]) -> bool:
        fallback_handler = self.fallback_handlers.get(error.error_code)
        if fallback_handler:
            action = FallbackAction(fallback_handler)
            return await action.execute(context)
        return False
    
    async def execute_compensation(self, error: AgentError, context: Dict[str, Any]) -> bool:
        compensation_handler = self.compensation_handlers.get(error.error_code)
        if compensation_handler:
            action = CompensationAction(compensation_handler)
            return await action.execute(context)
        return False
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        total_attempts = len(self.recovery_history)
        successful_recoveries = sum(1 for h in self.recovery_history if h['success'])
        
        strategy_stats = {}
        for history in self.recovery_history:
            strategy = history['strategy']
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {'attempts': 0, 'successes': 0}
            strategy_stats[strategy]['attempts'] += 1
            if history['success']:
                strategy_stats[strategy]['successes'] += 1
        
        return {
            'total_attempts': total_attempts,
            'successful_recoveries': successful_recoveries,
            'success_rate': successful_recoveries / total_attempts if total_attempts > 0 else 0,
            'strategy_statistics': strategy_stats,
            'circuit_breaker_states': {
                agent_id: cb.state for agent_id, cb in self.circuit_breakers.items()
            }
        }