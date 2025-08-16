"""A2A communication protocol implementation.

Phase 4: A2A External Integration
P4-T2: A2A Protocol Implementation
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Optional

from .message_types import (
    A2AMessage,
    AgentInfo,
    CapabilityInfo,
    MessagePriority,
    MessageType,
    ResponseStatus,
    create_error_message,
    create_heartbeat_message,
)


class ProtocolError(Exception):
    """Base exception for protocol errors."""

    pass


class MessageValidationError(ProtocolError):
    """Exception for message validation errors."""

    pass


class ProtocolVersionError(ProtocolError):
    """Exception for protocol version mismatches."""

    pass


class RateLimitError(ProtocolError):
    """Exception for rate limit violations."""

    pass


@dataclass
class MessageFilter:
    """Filter for incoming messages.

    Attributes:
        message_types: Allowed message types
        sender_ids: Allowed sender IDs
        capabilities: Allowed capabilities
        priority_threshold: Minimum priority level
        require_auth: Whether authentication is required
    """

    message_types: set[MessageType] = field(default_factory=set)
    sender_ids: set[str] = field(default_factory=set)
    capabilities: set[str] = field(default_factory=set)
    priority_threshold: MessagePriority = MessagePriority.LOW
    require_auth: bool = True


@dataclass
class RateLimitConfig:
    """Rate limiting configuration.

    Attributes:
        requests_per_minute: Maximum requests per minute
        burst_size: Maximum burst size
        window_size: Time window in seconds
    """

    requests_per_minute: int = 60
    burst_size: int = 10
    window_size: int = 60


class MessageValidator:
    """Validates A2A messages."""

    SUPPORTED_VERSIONS = {"1.0"}
    MAX_MESSAGE_SIZE = 1024 * 1024  # 1MB

    @classmethod
    def validate_message(cls, message: A2AMessage) -> None:
        """Validate message structure and content.

        Args:
            message: Message to validate

        Raises:
            MessageValidationError: If message is invalid
        """
        # Validate header
        cls._validate_header(message.header)

        # Validate payload
        cls._validate_payload(message.payload)

        # Validate message size
        message_size = len(json.dumps(message.to_dict()))
        if message_size > cls.MAX_MESSAGE_SIZE:
            raise MessageValidationError(
                f"Message size {message_size} exceeds limit {cls.MAX_MESSAGE_SIZE}"
            )

    @classmethod
    def _validate_header(cls, header) -> None:
        """Validate message header."""
        if not header.message_id:
            raise MessageValidationError("Message ID is required")

        if header.version not in cls.SUPPORTED_VERSIONS:
            raise ProtocolVersionError(f"Unsupported protocol version: {header.version}")

        if not header.sender_id:
            raise MessageValidationError("Sender ID is required")

        if header.is_expired():
            raise MessageValidationError("Message has expired")

    @classmethod
    def _validate_payload(cls, payload) -> None:
        """Validate message payload."""
        # Basic payload validation
        if payload.capability and not isinstance(payload.capability, str):
            raise MessageValidationError("Capability must be a string")

        if payload.action and not isinstance(payload.action, str):
            raise MessageValidationError("Action must be a string")


class RateLimiter:
    """Rate limiter for A2A messages."""

    def __init__(self, config: RateLimitConfig):
        """Initialize rate limiter.

        Args:
            config: Rate limiting configuration
        """
        self.config = config
        self.request_counts: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_rate_limit(self, sender_id: str) -> bool:
        """Check if sender is within rate limits.

        Args:
            sender_id: Sender identifier

        Returns:
            True if within limits
        """
        async with self._lock:
            current_time = time.time()
            window_start = current_time - self.config.window_size

            # Clean old requests
            self.request_counts[sender_id] = [
                req_time for req_time in self.request_counts[sender_id] if req_time > window_start
            ]

            # Check rate limit
            request_count = len(self.request_counts[sender_id])
            if request_count >= self.config.requests_per_minute:
                return False

            # Record this request
            self.request_counts[sender_id].append(current_time)
            return True


class MessageRouter:
    """Routes messages to appropriate handlers."""

    def __init__(self):
        """Initialize message router."""
        self.handlers: dict[MessageType, list[Callable]] = defaultdict(list)
        self.capability_handlers: dict[str, list[Callable]] = defaultdict(list)
        self.filters: list[MessageFilter] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def register_handler(
        self, message_type: MessageType, handler: Callable[[A2AMessage], None]
    ) -> None:
        """Register message handler.

        Args:
            message_type: Message type to handle
            handler: Handler function
        """
        self.handlers[message_type].append(handler)
        self.logger.info(f"Registered handler for {message_type.value}")

    def register_capability_handler(
        self, capability: str, handler: Callable[[A2AMessage], A2AMessage]
    ) -> None:
        """Register capability handler.

        Args:
            capability: Capability name
            handler: Handler function
        """
        self.capability_handlers[capability].append(handler)
        self.logger.info(f"Registered capability handler for {capability}")

    def add_filter(self, message_filter: MessageFilter) -> None:
        """Add message filter.

        Args:
            message_filter: Filter to add
        """
        self.filters.append(message_filter)

    def should_accept_message(self, message: A2AMessage) -> bool:
        """Check if message should be accepted.

        Args:
            message: Message to check

        Returns:
            True if message should be accepted
        """
        for filter_obj in self.filters:
            # Check message type
            if (
                filter_obj.message_types
                and message.header.message_type not in filter_obj.message_types
            ):
                return False

            # Check sender
            if filter_obj.sender_ids and message.header.sender_id not in filter_obj.sender_ids:
                return False

            # Check capability
            if (
                filter_obj.capabilities
                and message.payload.capability
                and message.payload.capability not in filter_obj.capabilities
            ):
                return False

            # Check priority
            if message.header.priority.value < filter_obj.priority_threshold.value:
                return False

        return True

    async def route_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Route message to appropriate handler.

        Args:
            message: Message to route

        Returns:
            Response message if applicable
        """
        if not self.should_accept_message(message):
            self.logger.warning(f"Message rejected by filters: {message.header.message_id}")
            return None

        try:
            # Route by message type
            handlers = self.handlers.get(message.header.message_type, [])
            for handler in handlers:
                await self._call_handler(handler, message)

            # Route by capability for requests
            if message.header.message_type == MessageType.REQUEST and message.payload.capability:
                capability_handlers = self.capability_handlers.get(message.payload.capability, [])
                for handler in capability_handlers:
                    response = await self._call_handler(handler, message)
                    if response:
                        return response

            return None

        except Exception as e:
            self.logger.error(f"Error routing message: {e}")
            return create_error_message(
                sender_id="router",
                error_code="ROUTING_ERROR",
                error_message=str(e),
                correlation_id=message.header.message_id,
            )

    async def _call_handler(self, handler: Callable, message: A2AMessage) -> Optional[A2AMessage]:
        """Call message handler safely."""
        try:
            if asyncio.iscoroutinefunction(handler):
                return await handler(message)
            else:
                return handler(message)
        except Exception as e:
            self.logger.error(f"Handler error: {e}")
            raise


class A2AProtocol:
    """A2A communication protocol implementation."""

    def __init__(
        self,
        agent_id: str,
        agent_info: AgentInfo,
        rate_limit_config: Optional[RateLimitConfig] = None,
    ):
        """Initialize A2A protocol.

        Args:
            agent_id: This agent's identifier
            agent_info: This agent's information
            rate_limit_config: Rate limiting configuration
        """
        self.agent_id = agent_id
        self.agent_info = agent_info
        self.rate_limiter = RateLimiter(rate_limit_config or RateLimitConfig())
        self.message_router = MessageRouter()
        self.validator = MessageValidator()
        self.logger = logging.getLogger(f"{self.__class__.__name__}[{agent_id}]")

        # Protocol state
        self.connected_agents: dict[str, AgentInfo] = {}
        self.pending_requests: dict[str, A2AMessage] = {}
        self.heartbeat_interval = 30
        self.heartbeat_task: Optional[asyncio.Task] = None

        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register default protocol handlers."""
        self.message_router.register_handler(MessageType.HANDSHAKE, self._handle_handshake)

        self.message_router.register_handler(MessageType.HEARTBEAT, self._handle_heartbeat)

        self.message_router.register_handler(
            MessageType.CAPABILITY_DISCOVERY, self._handle_capability_discovery
        )

        self.message_router.register_handler(MessageType.REGISTRATION, self._handle_registration)

        self.message_router.register_handler(MessageType.RESPONSE, self._handle_response)

    async def process_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Process incoming message.

        Args:
            message: Incoming message

        Returns:
            Response message if applicable

        Raises:
            MessageValidationError: If message is invalid
            RateLimitError: If rate limit exceeded
        """
        # Validate message
        self.validator.validate_message(message)

        # Check rate limits
        if not await self.rate_limiter.check_rate_limit(message.header.sender_id):
            raise RateLimitError(f"Rate limit exceeded for {message.header.sender_id}")

        # Route message
        response = await self.message_router.route_message(message)

        # Log message processing
        self.logger.debug(
            f"Processed {message.header.message_type.value} message "
            f"from {message.header.sender_id}"
        )

        return response

    async def send_message(
        self, message: A2AMessage, transport: Callable[[A2AMessage], None]
    ) -> None:
        """Send message using transport.

        Args:
            message: Message to send
            transport: Transport function
        """
        # Validate outgoing message
        self.validator.validate_message(message)

        # Store pending requests
        if message.header.message_type == MessageType.REQUEST:
            self.pending_requests[message.header.message_id] = message

        # Send via transport
        await transport(message)

        self.logger.debug(
            f"Sent {message.header.message_type.value} message " f"to {message.header.receiver_id}"
        )

    def register_capability_handler(
        self, capability: str, handler: Callable[[A2AMessage], A2AMessage]
    ) -> None:
        """Register capability handler.

        Args:
            capability: Capability name
            handler: Handler function
        """
        self.message_router.register_capability_handler(capability, handler)

    def add_message_filter(self, message_filter: MessageFilter) -> None:
        """Add message filter.

        Args:
            message_filter: Filter to add
        """
        self.message_router.add_filter(message_filter)

    async def start_heartbeat(self) -> None:
        """Start heartbeat task."""
        if self.heartbeat_task and not self.heartbeat_task.done():
            return

        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.logger.info("Started heartbeat task")

    async def stop_heartbeat(self) -> None:
        """Stop heartbeat task."""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Stopped heartbeat task")

    async def _heartbeat_loop(self) -> None:
        """Background heartbeat loop."""
        while True:
            try:
                # Create heartbeat message
                heartbeat = create_heartbeat_message(
                    sender_id=self.agent_id,
                    status="healthy",
                    metrics={
                        "connected_agents": len(self.connected_agents),
                        "pending_requests": len(self.pending_requests),
                    },
                )

                # This would be sent via transport in real implementation
                self.logger.debug("Heartbeat sent")

                await asyncio.sleep(self.heartbeat_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(self.heartbeat_interval)

    async def _handle_handshake(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Handle handshake message."""
        try:
            agent_info = AgentInfo.from_dict(message.payload.data)
            self.connected_agents[agent_info.agent_id] = agent_info

            self.logger.info(f"Handshake received from {agent_info.agent_id}")

            # Return handshake response
            return message.create_response(
                status=ResponseStatus.SUCCESS, data=self.agent_info.to_dict()
            )

        except Exception as e:
            self.logger.error(f"Handshake error: {e}")
            return message.create_response(status=ResponseStatus.ERROR, error=str(e))

    async def _handle_heartbeat(self, message: A2AMessage) -> None:
        """Handle heartbeat message."""
        sender_id = message.header.sender_id
        status = message.payload.data.get("status", "unknown")

        self.logger.debug(f"Heartbeat from {sender_id}: {status}")

        # Update agent status if known
        if sender_id in self.connected_agents:
            self.connected_agents[sender_id].status = status

    async def _handle_capability_discovery(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Handle capability discovery message."""
        query_tags = message.payload.data.get("query_tags", [])
        query_capabilities = message.payload.data.get("query_capabilities", [])

        # Filter capabilities based on query
        matching_capabilities = []
        for capability in self.agent_info.capabilities:
            # Match by tags
            if query_tags and not set(query_tags).intersection(set(capability.tags)):
                continue

            # Match by capability name
            if query_capabilities and capability.name not in query_capabilities:
                continue

            matching_capabilities.append(capability.to_dict())

        return message.create_response(
            status=ResponseStatus.SUCCESS,
            data={
                "agent_info": self.agent_info.to_dict(),
                "matching_capabilities": matching_capabilities,
            },
        )

    async def _handle_registration(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Handle registration message."""
        try:
            agent_info = AgentInfo.from_dict(message.payload.data)
            self.connected_agents[agent_info.agent_id] = agent_info

            self.logger.info(f"Agent registered: {agent_info.agent_id}")

            return message.create_response(status=ResponseStatus.SUCCESS, data={"registered": True})

        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return message.create_response(status=ResponseStatus.ERROR, error=str(e))

    async def _handle_response(self, message: A2AMessage) -> None:
        """Handle response message."""
        correlation_id = message.header.correlation_id
        if correlation_id and correlation_id in self.pending_requests:
            # Remove from pending requests
            del self.pending_requests[correlation_id]
            self.logger.debug(f"Received response for request {correlation_id}")
        else:
            self.logger.warning(f"Received response for unknown request {correlation_id}")

    def get_connected_agents(self) -> list[AgentInfo]:
        """Get list of connected agents."""
        return list(self.connected_agents.values())

    def get_agent_capabilities(self, agent_id: str) -> list[CapabilityInfo]:
        """Get capabilities for specific agent."""
        if agent_id in self.connected_agents:
            return self.connected_agents[agent_id].capabilities
        return []
