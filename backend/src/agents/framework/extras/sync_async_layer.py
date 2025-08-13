# backend/src/agents/framework/sync_async_layer.py
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Union

from .communication import AgentMessage, MessageType


@dataclass
class CommunicationConfig:
    sync_timeout: float = 30.0
    async_timeout: float = 60.0
    max_workers: int = 10
    enable_sync_bridge: bool = True


class SyncAsyncBridge:
    def __init__(self, config: CommunicationConfig):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.sync_handlers: Dict[str, Callable] = {}
        self.async_handlers: Dict[str, Callable] = {}

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    def register_sync_handler(self, message_type: str, handler: Callable):
        self.sync_handlers[message_type] = handler

    def register_async_handler(self, message_type: str, handler: Callable):
        self.async_handlers[message_type] = handler

    async def handle_sync_in_async(self, message: AgentMessage) -> Any:
        """Execute synchronous handler in async context"""
        handler = self.sync_handlers.get(message.type.value)
        if not handler:
            return None

        try:
            result = await asyncio.wait_for(
                self.loop.run_in_executor(self.executor, handler, message),
                timeout=self.config.sync_timeout,
            )
            return result
        except asyncio.TimeoutError:
            raise TimeoutError(f"Sync handler timeout for {message.type.value}")

    def handle_async_in_sync(self, message: AgentMessage) -> Any:
        """Execute async handler in sync context"""
        handler = self.async_handlers.get(message.type.value)
        if not handler:
            return None

        if not self.loop:
            raise RuntimeError("Event loop not set")

        future = asyncio.run_coroutine_threadsafe(
            asyncio.wait_for(handler(message), timeout=self.config.async_timeout),
            self.loop,
        )

        try:
            return future.result(timeout=self.config.async_timeout)
        except Exception as e:
            raise RuntimeError(f"Async handler error: {e}")


class CommunicationLayer:
    def __init__(self, config: CommunicationConfig):
        self.config = config
        self.bridge = SyncAsyncBridge(config)
        self.message_processors: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []

    def add_middleware(self, middleware: Callable):
        self.middleware.append(middleware)

    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        # Apply middleware
        for middleware in self.middleware:
            message = await self._apply_middleware(middleware, message)
            if not message:
                return None

        # Process message
        processor = self.message_processors.get(message.type.value)
        if processor:
            if asyncio.iscoroutinefunction(processor):
                result = await processor(message)
            else:
                result = await self.bridge.handle_sync_in_async(message)

            if result and message.type == MessageType.REQUEST:
                return self._create_response(message, result)

        return None

    async def _apply_middleware(
        self, middleware: Callable, message: AgentMessage
    ) -> Optional[AgentMessage]:
        try:
            if asyncio.iscoroutinefunction(middleware):
                return await middleware(message)
            else:
                return middleware(message)
        except Exception as e:
            print(f"Middleware error: {e}")
            return message

    def _create_response(self, request: AgentMessage, result: Any) -> AgentMessage:
        import uuid
        from datetime import datetime

        return AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.RESPONSE,
            sender_id=request.recipient_id or "system",
            recipient_id=request.sender_id,
            content={"result": result},
            timestamp=datetime.utcnow(),
            correlation_id=request.id,
        )


class AgentCommunicationLayer:
    def __init__(self, agent_id: str, config: CommunicationConfig):
        self.agent_id = agent_id
        self.config = config
        self.comm_layer = CommunicationLayer(config)
        self.active_connections: Dict[str, Any] = {}

    async def send_sync_request(self, recipient_id: str, content: Dict[str, Any]) -> Any:
        """Send synchronous request and wait for response"""
        message = AgentMessage(
            id=str(__import__("uuid").uuid4()),
            type=MessageType.REQUEST,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            content=content,
            timestamp=__import__("datetime").datetime.utcnow(),
        )

        response = await self.comm_layer.process_message(message)
        return response.content.get("result") if response else None

    async def send_async_notification(self, recipient_id: str, content: Dict[str, Any]):
        """Send fire-and-forget notification"""
        message = AgentMessage(
            id=str(__import__("uuid").uuid4()),
            type=MessageType.NOTIFICATION,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            content=content,
            timestamp=__import__("datetime").datetime.utcnow(),
        )

        await self.comm_layer.process_message(message)
