from typing import Dict, List, Callable, Any, Optional
import asyncio
from dataclasses import dataclass
from datetime import datetime
from .lifecycle import LifecycleEvent

@dataclass
class LifecycleEventData:
    event_type: LifecycleEvent
    agent_id: str
    timestamp: datetime
    metadata: Dict[str, Any]
    source: str

class EventHandler:
    """Wrapper for event handlers with priority"""
    
    def __init__(self, handler: Callable, priority: int = 0):
        self.handler = handler
        self.priority = priority
    
    async def execute(self, event_data: LifecycleEventData) -> None:
        """Execute the handler"""
        if asyncio.iscoroutinefunction(self.handler):
            await self.handler(event_data)
        else:
            self.handler(event_data)

class EventBus:
    """Simple event bus for lifecycle events"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
    
    async def publish(self, topic: str, data: Any) -> None:
        """Publish event to topic"""
        if topic in self.subscribers:
            for handler in self.subscribers[topic]:
                try:
                    await handler(data)
                except Exception as e:
                    print(f"Event handler error: {e}")
    
    def subscribe(self, topic: str, handler: Callable) -> None:
        """Subscribe to topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(handler)

class LifecycleEventHandler:
    """Handles lifecycle events for agents"""
    
    def __init__(self):
        self.event_handlers: Dict[LifecycleEvent, List[EventHandler]] = {}
        self.event_history: List[LifecycleEventData] = []
        self.event_bus = EventBus()
        self.max_history = 1000
        
    def register_handler(
        self,
        event_type: LifecycleEvent,
        handler: Callable,
        priority: int = 0
    ) -> None:
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
            
        self.event_handlers[event_type].append(
            EventHandler(handler=handler, priority=priority)
        )
        
        # Sort by priority
        self.event_handlers[event_type].sort(
            key=lambda x: x.priority,
            reverse=True
        )
    
    async def emit_event(self, event_data: LifecycleEventData) -> None:
        """Emit a lifecycle event"""
        # Record in history
        self.event_history.append(event_data)
        
        # Maintain history size
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        # Publish to event bus
        await self.event_bus.publish(
            topic=f"agent.lifecycle.{event_data.event_type.value}",
            data=event_data
        )
        
        # Execute registered handlers
        if event_data.event_type in self.event_handlers:
            handlers = self.event_handlers[event_data.event_type]
            
            for handler in handlers:
                try:
                    await handler.execute(event_data)
                except Exception as e:
                    await self._handle_handler_error(handler, event_data, e)
    
    async def _handle_handler_error(
        self, 
        handler: EventHandler, 
        event_data: LifecycleEventData, 
        error: Exception
    ) -> None:
        """Handle errors in event handlers"""
        error_event = LifecycleEventData(
            event_type=LifecycleEvent.ERROR,
            agent_id=event_data.agent_id,
            timestamp=datetime.utcnow(),
            metadata={
                "original_event": event_data.event_type.value,
                "handler_error": str(error),
                "handler_priority": handler.priority
            },
            source="event_handler"
        )
        
        # Emit error event (but don't recurse)
        self.event_history.append(error_event)
    
    def get_event_history(
        self, 
        agent_id: Optional[str] = None,
        event_type: Optional[LifecycleEvent] = None,
        limit: int = 100
    ) -> List[LifecycleEventData]:
        """Get filtered event history"""
        filtered = self.event_history
        
        if agent_id:
            filtered = [e for e in filtered if e.agent_id == agent_id]
        
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        return filtered[-limit:]
    
    def get_agent_lifecycle_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get lifecycle summary for specific agent"""
        agent_events = [e for e in self.event_history if e.agent_id == agent_id]
        
        if not agent_events:
            return {"agent_id": agent_id, "events": 0, "current_state": "unknown"}
        
        # Count events by type
        event_counts = {}
        for event in agent_events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Get current state (last event)
        current_state = agent_events[-1].event_type.value
        
        # Calculate uptime
        created_event = next((e for e in agent_events if e.event_type == LifecycleEvent.CREATED), None)
        uptime_seconds = 0
        if created_event:
            uptime_seconds = (datetime.utcnow() - created_event.timestamp).total_seconds()
        
        return {
            "agent_id": agent_id,
            "events": len(agent_events),
            "current_state": current_state,
            "event_counts": event_counts,
            "uptime_seconds": uptime_seconds,
            "first_event": agent_events[0].timestamp.isoformat(),
            "last_event": agent_events[-1].timestamp.isoformat()
        }