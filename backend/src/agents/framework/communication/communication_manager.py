"""
T-Developer Agent Communication System - Unified Implementation

Combines communication.py and communication_manager.py functionality
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from ..core.base_agent import AgentMessage

logger = logging.getLogger(__name__)


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"


class CommunicationProtocol:
    def __init__(self):
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()

    def register_handler(self, message_type: str, handler: Callable):
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)

    async def send_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        if message.type == "request":
            future = asyncio.Future()
            self.pending_requests[message.id] = future
            await self.message_queue.put(message)
            return await future
        else:
            await self.message_queue.put(message)
            return None


class MessageBus(ABC):
    """Abstract message bus interface"""

    @abstractmethod
    async def publish(self, channel: str, message: AgentMessage) -> None:
        pass

    @abstractmethod
    def subscribe(self, channel: str, handler: Callable[[AgentMessage], None]) -> None:
        pass

    @abstractmethod
    def unsubscribe(self, channel: str) -> None:
        pass


class InMemoryMessageBus(MessageBus):
    """Memory-based message bus for development"""

    def __init__(self):
        self.handlers: Dict[str, Set[Callable[[AgentMessage], None]]] = {}

    async def publish(self, channel: str, message: AgentMessage) -> None:
        """Publish message to channel"""
        if channel in self.handlers:
            for handler in self.handlers[channel]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message)
                    else:
                        handler(message)
                except Exception as e:
                    logger.error(f"Message handler error: {e}")

    def subscribe(self, channel: str, handler: Callable[[AgentMessage], None]) -> None:
        """Subscribe to channel"""
        if channel not in self.handlers:
            self.handlers[channel] = set()
        self.handlers[channel].add(handler)

    def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from channel"""
        if channel in self.handlers:
            del self.handlers[channel]


class AgentCommunicationManager:
    """Manages agent communication and routing"""

    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.agents: Dict[str, Any] = {}
        self.routing_table: Dict[str, List[str]] = {}

    def register_agent(self, agent_id: str, agent: Any, channels: List[str]) -> None:
        """Register agent with communication channels"""
        self.agents[agent_id] = agent

        for channel in channels:
            if channel not in self.routing_table:
                self.routing_table[channel] = []
            self.routing_table[channel].append(agent_id)

            # Subscribe to channel
            async def message_handler(message: AgentMessage):
                if message.target == agent_id or message.target == "broadcast":
                    response = await agent.handle_message(message)
                    if response and response.type == "response":
                        await self.send_message(response)

            self.message_bus.subscribe(channel, message_handler)

    async def send_message(self, message: AgentMessage) -> None:
        """Send message to target agent or broadcast"""
        if message.target and message.target != "broadcast":
            await self.message_bus.publish(f"agent:{message.target}", message)
        elif message.target == "broadcast":
            await self.message_bus.publish("agent:broadcast", message)


class AgentCommunicationMixin:
    """Mixin for agent communication capabilities"""

    def __init__(self):
        self.protocol = CommunicationProtocol()
        self.agent_id = str(uuid.uuid4())

    async def send_request(
        self, recipient_id: str, content: Dict[str, Any]
    ) -> Optional[AgentMessage]:
        message = AgentMessage(
            id=str(uuid.uuid4()),
            type="request",
            source=self.agent_id,
            target=recipient_id,
            payload=content,
            timestamp=datetime.utcnow(),
        )
        return await self.protocol.send_message(message)

    async def send_notification(self, recipient_id: str, content: Dict[str, Any]):
        message = AgentMessage(
            id=str(uuid.uuid4()),
            type="notification",
            source=self.agent_id,
            target=recipient_id,
            payload=content,
            timestamp=datetime.utcnow(),
        )
        await self.protocol.send_message(message)


@dataclass
class RPCCall:
    resolve: Callable
    reject: Callable
    timeout_handle: Any


class AgentRPC:
    """Agent RPC communication system"""

    def __init__(self, communication_manager: AgentCommunicationManager):
        self.communication_manager = communication_manager
        self.pending_calls: Dict[str, RPCCall] = {}

    async def call(self, target_agent: str, method: str, params: Any, timeout: float = 30.0) -> Any:
        """Make RPC call to target agent"""
        call_id = f"rpc-{asyncio.get_event_loop().time()}-{id(self)}"

        message = AgentMessage(
            id=call_id,
            type="request",
            source="rpc-client",
            target=target_agent,
            payload={"method": method, "params": params},
            timestamp=datetime.utcnow(),
        )

        future = asyncio.Future()

        def timeout_callback():
            if call_id in self.pending_calls:
                del self.pending_calls[call_id]
                if not future.done():
                    future.set_exception(TimeoutError(f"RPC call timeout: {method}"))

        timeout_handle = asyncio.get_event_loop().call_later(timeout, timeout_callback)

        self.pending_calls[call_id] = RPCCall(
            resolve=lambda result: future.set_result(result) if not future.done() else None,
            reject=lambda error: future.set_exception(error) if not future.done() else None,
            timeout_handle=timeout_handle,
        )

        await self.communication_manager.send_message(message)
        return await future
