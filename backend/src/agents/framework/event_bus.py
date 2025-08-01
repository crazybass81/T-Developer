# backend/src/agents/framework/event_bus.py
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
from datetime import datetime
import weakref

class EventPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Event:
    id: str
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: EventPriority = EventPriority.NORMAL
    source: Optional[str] = None

@dataclass
class EventSubscription:
    handler: Callable
    priority: int = 0
    filter_func: Optional[Callable] = None

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[EventSubscription]] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000
        self._lock = asyncio.Lock()
    
    def subscribe(self, event_type: str, handler: Callable, priority: int = 0, filter_func: Optional[Callable] = None):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        subscription = EventSubscription(handler, priority, filter_func)
        self.subscribers[event_type].append(subscription)
        
        # Sort by priority (higher first)
        self.subscribers[event_type].sort(key=lambda x: x.priority, reverse=True)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        if event_type in self.subscribers:
            self.subscribers[event_type] = [
                sub for sub in self.subscribers[event_type]
                if sub.handler != handler
            ]
    
    async def publish(self, event: Event):
        async with self._lock:
            # Add to history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)
        
        # Notify subscribers
        subscribers = self.subscribers.get(event.type, [])
        tasks = []
        
        for subscription in subscribers:
            if subscription.filter_func and not subscription.filter_func(event):
                continue
            
            task = asyncio.create_task(self._safe_call_handler(subscription.handler, event))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_call_handler(self, handler: Callable, event: Event):
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            print(f"Event handler error: {e}")
    
    def get_event_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Event]:
        events = self.event_history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]

class AgentEventMixin:
    def __init__(self):
        self.event_bus = EventBus()
        self.agent_id = getattr(self, 'agent_id', 'unknown')
    
    async def emit_event(self, event_type: str, data: Dict[str, Any], priority: EventPriority = EventPriority.NORMAL):
        import uuid
        event = Event(
            id=str(uuid.uuid4()),
            type=event_type,
            data=data,
            timestamp=datetime.utcnow(),
            priority=priority,
            source=self.agent_id
        )
        await self.event_bus.publish(event)
    
    def on_event(self, event_type: str, priority: int = 0):
        def decorator(handler):
            self.event_bus.subscribe(event_type, handler, priority)
            return handler
        return decorator