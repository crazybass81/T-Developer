"""
Event Bus System for agent communication
Implements pub/sub pattern for decoupled agent messaging
"""
import asyncio
import json
from typing import Dict, Any, List, Callable, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in the system"""

    # Pipeline events
    PIPELINE_STARTED = "pipeline.started"
    PIPELINE_COMPLETED = "pipeline.completed"
    PIPELINE_FAILED = "pipeline.failed"
    PIPELINE_CANCELLED = "pipeline.cancelled"

    # Agent events
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    AGENT_TIMEOUT = "agent.timeout"
    AGENT_RETRY = "agent.retry"

    # Data events
    DATA_VALIDATED = "data.validated"
    DATA_TRANSFORMED = "data.transformed"
    DATA_STORED = "data.stored"

    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    SYSTEM_INFO = "system.info"

    # Resource events
    RESOURCE_LIMIT_REACHED = "resource.limit_reached"
    RESOURCE_CLEANUP = "resource.cleanup"


class EventPriority(Enum):
    """Event priority levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """Event data structure"""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.SYSTEM_INFO
    source: str = "system"
    target: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = EventPriority.NORMAL
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "target": self.target,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "data": self.data,
            "metadata": self.metadata,
            "correlation_id": self.correlation_id,
            "retry_count": self.retry_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create event from dictionary"""
        return cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            event_type=EventType(data["event_type"])
            if "event_type" in data
            else EventType.SYSTEM_INFO,
            source=data.get("source", "system"),
            target=data.get("target"),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.utcnow(),
            priority=EventPriority(data["priority"])
            if "priority" in data
            else EventPriority.NORMAL,
            data=data.get("data", {}),
            metadata=data.get("metadata", {}),
            correlation_id=data.get("correlation_id"),
            retry_count=data.get("retry_count", 0),
        )


class EventHandler:
    """Base class for event handlers"""

    def __init__(
        self,
        name: str,
        handler_func: Callable,
        event_types: Optional[List[EventType]] = None,
        priority_threshold: EventPriority = EventPriority.LOW,
    ):
        self.name = name
        self.handler_func = handler_func
        self.event_types = event_types or []
        self.priority_threshold = priority_threshold
        self.processed_events = 0
        self.failed_events = 0

    async def handle(self, event: Event) -> Any:
        """Handle an event"""
        try:
            # Check if handler should process this event
            if not self.should_handle(event):
                return None

            # Process event
            result = await self.handler_func(event)
            self.processed_events += 1
            return result

        except Exception as e:
            self.failed_events += 1
            logger.error(f"Handler {self.name} failed for event {event.event_id}: {e}")
            raise

    def should_handle(self, event: Event) -> bool:
        """Check if handler should process event"""
        # Check event type
        if self.event_types and event.event_type not in self.event_types:
            return False

        # Check priority
        if event.priority.value < self.priority_threshold.value:
            return False

        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics"""
        return {
            "name": self.name,
            "processed_events": self.processed_events,
            "failed_events": self.failed_events,
            "success_rate": (
                self.processed_events / (self.processed_events + self.failed_events)
                if (self.processed_events + self.failed_events) > 0
                else 0
            ),
        }


class EventBus:
    """Central event bus for the system"""

    def __init__(self, max_queue_size: int = 1000, enable_persistence: bool = False):
        self.max_queue_size = max_queue_size
        self.enable_persistence = enable_persistence

        # Event queue
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)

        # Handlers registry
        self._handlers: Dict[str, EventHandler] = {}
        self._event_type_handlers: Dict[EventType, Set[str]] = {}

        # Event history
        self._event_history: List[Event] = []
        self._max_history_size = 1000

        # Processing state
        self._processing = False
        self._processed_count = 0
        self._failed_count = 0

        # Dead letter queue for failed events
        self._dead_letter_queue: List[Event] = []

    def register_handler(self, handler: EventHandler) -> None:
        """Register an event handler"""
        self._handlers[handler.name] = handler

        # Index by event type for faster lookup
        for event_type in handler.event_types:
            if event_type not in self._event_type_handlers:
                self._event_type_handlers[event_type] = set()
            self._event_type_handlers[event_type].add(handler.name)

        logger.info(f"Registered handler: {handler.name}")

    def unregister_handler(self, handler_name: str) -> bool:
        """Unregister an event handler"""
        if handler_name not in self._handlers:
            return False

        handler = self._handlers[handler_name]

        # Remove from event type index
        for event_type in handler.event_types:
            if event_type in self._event_type_handlers:
                self._event_type_handlers[event_type].discard(handler_name)

        # Remove handler
        del self._handlers[handler_name]
        logger.info(f"Unregistered handler: {handler_name}")
        return True

    async def publish(self, event: Event) -> str:
        """Publish an event to the bus"""
        # Add to queue
        try:
            await self._queue.put(event)

            # Add to history
            self._add_to_history(event)

            logger.debug(
                f"Published event: {event.event_id} ({event.event_type.value})"
            )
            return event.event_id

        except asyncio.QueueFull:
            logger.error(f"Event queue is full, dropping event: {event.event_id}")
            raise RuntimeError("Event queue is full")

    async def publish_batch(self, events: List[Event]) -> List[str]:
        """Publish multiple events"""
        event_ids = []
        for event in events:
            event_id = await self.publish(event)
            event_ids.append(event_id)
        return event_ids

    async def start_processing(self) -> None:
        """Start processing events"""
        if self._processing:
            logger.warning("Event processing already started")
            return

        self._processing = True
        logger.info("Started event processing")

        while self._processing:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)

                # Process event
                await self._process_event(event)

            except asyncio.TimeoutError:
                # No events in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error in event processing loop: {e}")

    async def stop_processing(self) -> None:
        """Stop processing events"""
        self._processing = False
        logger.info("Stopped event processing")

        # Process remaining events
        while not self._queue.empty():
            try:
                event = self._queue.get_nowait()
                await self._process_event(event)
            except asyncio.QueueEmpty:
                break

    async def _process_event(self, event: Event) -> None:
        """Process a single event"""
        try:
            # Find applicable handlers
            handlers = self._get_handlers_for_event(event)

            if not handlers:
                logger.debug(f"No handlers for event: {event.event_id}")
                return

            # Execute handlers
            results = []
            for handler in handlers:
                try:
                    result = await handler.handle(event)
                    results.append((handler.name, result))
                except Exception as e:
                    logger.error(f"Handler {handler.name} failed: {e}")

                    # Retry logic
                    if event.retry_count < event.max_retries:
                        event.retry_count += 1
                        await self.publish(event)
                    else:
                        # Add to dead letter queue
                        self._dead_letter_queue.append(event)

            self._processed_count += 1

        except Exception as e:
            self._failed_count += 1
            logger.error(f"Failed to process event {event.event_id}: {e}")
            self._dead_letter_queue.append(event)

    def _get_handlers_for_event(self, event: Event) -> List[EventHandler]:
        """Get handlers that should process the event"""
        handlers = []

        # Get handlers registered for this event type
        if event.event_type in self._event_type_handlers:
            for handler_name in self._event_type_handlers[event.event_type]:
                if handler_name in self._handlers:
                    handler = self._handlers[handler_name]
                    if handler.should_handle(event):
                        handlers.append(handler)

        # Get handlers with no specific event types (catch-all)
        for handler in self._handlers.values():
            if not handler.event_types and handler.should_handle(event):
                handlers.append(handler)

        # Sort by priority threshold (higher priority handlers first)
        handlers.sort(key=lambda h: h.priority_threshold.value, reverse=True)

        return handlers

    def _add_to_history(self, event: Event) -> None:
        """Add event to history"""
        self._event_history.append(event)

        # Trim history if needed
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size :]

    def get_event_history(
        self, event_type: Optional[EventType] = None, limit: int = 100
    ) -> List[Event]:
        """Get event history"""
        history = self._event_history.copy()

        # Filter by event type if specified
        if event_type:
            history = [e for e in history if e.event_type == event_type]

        # Apply limit
        return history[-limit:]

    def get_dead_letter_queue(self) -> List[Event]:
        """Get failed events from dead letter queue"""
        return self._dead_letter_queue.copy()

    def clear_dead_letter_queue(self) -> int:
        """Clear dead letter queue"""
        count = len(self._dead_letter_queue)
        self._dead_letter_queue.clear()
        return count

    async def replay_event(self, event_id: str) -> bool:
        """Replay a specific event"""
        # Find event in history or dead letter queue
        event = None

        for e in self._event_history:
            if e.event_id == event_id:
                event = e
                break

        if not event:
            for e in self._dead_letter_queue:
                if e.event_id == event_id:
                    event = e
                    break

        if not event:
            return False

        # Reset retry count and republish
        event.retry_count = 0
        await self.publish(event)
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            "queue_size": self._queue.qsize(),
            "max_queue_size": self.max_queue_size,
            "processed_events": self._processed_count,
            "failed_events": self._failed_count,
            "handlers_registered": len(self._handlers),
            "event_history_size": len(self._event_history),
            "dead_letter_queue_size": len(self._dead_letter_queue),
            "handler_stats": [
                handler.get_stats() for handler in self._handlers.values()
            ],
        }


# Singleton instance
_event_bus_instance: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get singleton event bus instance"""
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance


# Convenience functions for publishing events
async def publish_pipeline_event(
    event_type: EventType, pipeline_id: str, data: Dict[str, Any] = None
) -> str:
    """Publish a pipeline-related event"""
    event = Event(
        event_type=event_type,
        source="pipeline",
        correlation_id=pipeline_id,
        data=data or {},
        metadata={"pipeline_id": pipeline_id},
    )

    bus = get_event_bus()
    return await bus.publish(event)


async def publish_agent_event(
    event_type: EventType,
    agent_name: str,
    pipeline_id: str,
    data: Dict[str, Any] = None,
) -> str:
    """Publish an agent-related event"""
    event = Event(
        event_type=event_type,
        source=f"agent.{agent_name}",
        correlation_id=pipeline_id,
        data=data or {},
        metadata={"agent_name": agent_name, "pipeline_id": pipeline_id},
    )

    bus = get_event_bus()
    return await bus.publish(event)


# Export classes and functions
__all__ = [
    "EventType",
    "EventPriority",
    "Event",
    "EventHandler",
    "EventBus",
    "get_event_bus",
    "publish_pipeline_event",
    "publish_agent_event",
]
