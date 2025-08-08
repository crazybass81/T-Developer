from typing import Dict, List, Callable, Optional, Set
from enum import Enum
import asyncio
from datetime import datetime

class LifecycleEvent(Enum):
    CREATED = "created"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    STARTED = "started"
    EXECUTING = "executing"
    PAUSING = "pausing"
    PAUSED = "paused"
    RESUMING = "resuming"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"

class LifecycleStateMachine:
    """State machine for agent lifecycle management"""
    
    def __init__(self):
        self.current_state = LifecycleEvent.CREATED
        self.state_history: List[tuple[LifecycleEvent, datetime]] = [
            (self.current_state, datetime.utcnow())
        ]
        self.transitions = self._define_transitions()
        self.state_handlers: Dict[LifecycleEvent, List[Callable]] = {}
        
    def _define_transitions(self) -> Dict[LifecycleEvent, Set[LifecycleEvent]]:
        """Define valid state transitions"""
        return {
            LifecycleEvent.CREATED: {LifecycleEvent.INITIALIZING},
            LifecycleEvent.INITIALIZING: {LifecycleEvent.INITIALIZED, LifecycleEvent.ERROR},
            LifecycleEvent.INITIALIZED: {LifecycleEvent.STARTING},
            LifecycleEvent.STARTING: {LifecycleEvent.STARTED, LifecycleEvent.ERROR},
            LifecycleEvent.STARTED: {LifecycleEvent.EXECUTING, LifecycleEvent.STOPPING},
            LifecycleEvent.EXECUTING: {LifecycleEvent.STARTED, LifecycleEvent.PAUSING, LifecycleEvent.ERROR},
            LifecycleEvent.PAUSING: {LifecycleEvent.PAUSED, LifecycleEvent.ERROR},
            LifecycleEvent.PAUSED: {LifecycleEvent.RESUMING, LifecycleEvent.STOPPING},
            LifecycleEvent.RESUMING: {LifecycleEvent.STARTED, LifecycleEvent.ERROR},
            LifecycleEvent.STOPPING: {LifecycleEvent.STOPPED, LifecycleEvent.ERROR},
            LifecycleEvent.STOPPED: {LifecycleEvent.TERMINATED},
            LifecycleEvent.ERROR: {LifecycleEvent.STOPPING, LifecycleEvent.TERMINATED},
            LifecycleEvent.TERMINATED: set()
        }
    
    def can_transition_to(self, target_state: LifecycleEvent) -> bool:
        """Check if transition to target state is valid"""
        return target_state in self.transitions.get(self.current_state, set())
    
    async def transition_to(self, target_state: LifecycleEvent) -> bool:
        """Transition to target state if valid"""
        if not self.can_transition_to(target_state):
            return False
        
        old_state = self.current_state
        self.current_state = target_state
        self.state_history.append((target_state, datetime.utcnow()))
        
        # Execute state handlers
        await self._execute_handlers(target_state, old_state)
        
        return True
    
    def register_handler(self, state: LifecycleEvent, handler: Callable) -> None:
        """Register a handler for a specific state"""
        if state not in self.state_handlers:
            self.state_handlers[state] = []
        self.state_handlers[state].append(handler)
    
    async def _execute_handlers(self, new_state: LifecycleEvent, old_state: LifecycleEvent) -> None:
        """Execute registered handlers for state transition"""
        if new_state in self.state_handlers:
            for handler in self.state_handlers[new_state]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(old_state, new_state)
                    else:
                        handler(old_state, new_state)
                except Exception as e:
                    print(f"Handler error: {e}")
    
    def get_state_history(self) -> List[tuple[LifecycleEvent, datetime]]:
        """Get complete state history"""
        return self.state_history.copy()
    
    def get_current_state(self) -> LifecycleEvent:
        """Get current state"""
        return self.current_state