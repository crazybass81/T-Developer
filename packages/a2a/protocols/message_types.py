"""Standard message types for A2A communication.

Phase 4: A2A External Integration
P4-T2: A2A Protocol Implementation
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class MessageType(Enum):
    """A2A message types."""

    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    HANDSHAKE = "handshake"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    CAPABILITY_DISCOVERY = "capability_discovery"
    REGISTRATION = "registration"
    DEREGISTRATION = "deregistration"


class MessagePriority(Enum):
    """Message priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class ResponseStatus(Enum):
    """Response status codes."""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"
    SERVICE_UNAVAILABLE = "service_unavailable"


@dataclass
class MessageHeader:
    """A2A message header.

    Attributes:
        message_id: Unique message identifier
        message_type: Type of message
        timestamp: Message timestamp
        sender_id: Sender agent identifier
        receiver_id: Receiver agent identifier (optional for broadcasts)
        correlation_id: Correlation ID for request/response pairs
        priority: Message priority
        ttl_seconds: Time-to-live in seconds
        retry_count: Number of retries attempted
        trace_id: Distributed tracing identifier
        version: Protocol version
    """

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.REQUEST
    timestamp: float = field(default_factory=time.time)
    sender_id: str = ""
    receiver_id: Optional[str] = None
    correlation_id: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL
    ttl_seconds: int = 300
    retry_count: int = 0
    trace_id: Optional[str] = None
    version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert header to dictionary."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "correlation_id": self.correlation_id,
            "priority": self.priority.value,
            "ttl_seconds": self.ttl_seconds,
            "retry_count": self.retry_count,
            "trace_id": self.trace_id,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MessageHeader:
        """Create header from dictionary."""
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            message_type=MessageType(data.get("message_type", "request")),
            timestamp=data.get("timestamp", time.time()),
            sender_id=data.get("sender_id", ""),
            receiver_id=data.get("receiver_id"),
            correlation_id=data.get("correlation_id"),
            priority=MessagePriority(data.get("priority", 2)),
            ttl_seconds=data.get("ttl_seconds", 300),
            retry_count=data.get("retry_count", 0),
            trace_id=data.get("trace_id"),
            version=data.get("version", "1.0"),
        )

    def is_expired(self) -> bool:
        """Check if message has expired."""
        return time.time() - self.timestamp > self.ttl_seconds


@dataclass
class MessagePayload:
    """A2A message payload.

    Attributes:
        capability: Target capability name
        action: Action to perform
        parameters: Action parameters
        data: Message data
        metadata: Additional metadata
    """

    capability: Optional[str] = None
    action: Optional[str] = None
    parameters: dict[str, Any] = field(default_factory=dict)
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert payload to dictionary."""
        return {
            "capability": self.capability,
            "action": self.action,
            "parameters": self.parameters,
            "data": self.data,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MessagePayload:
        """Create payload from dictionary."""
        return cls(
            capability=data.get("capability"),
            action=data.get("action"),
            parameters=data.get("parameters", {}),
            data=data.get("data", {}),
            metadata=data.get("metadata", {}),
        )


@dataclass
class A2AMessage:
    """Complete A2A message.

    Attributes:
        header: Message header
        payload: Message payload
    """

    header: MessageHeader
    payload: MessagePayload

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary."""
        return {"header": self.header.to_dict(), "payload": self.payload.to_dict()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> A2AMessage:
        """Create message from dictionary."""
        return cls(
            header=MessageHeader.from_dict(data.get("header", {})),
            payload=MessagePayload.from_dict(data.get("payload", {})),
        )

    def create_response(
        self,
        status: ResponseStatus,
        data: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> A2AMessage:
        """Create response message."""
        response_header = MessageHeader(
            message_type=MessageType.RESPONSE,
            sender_id=self.header.receiver_id or "",
            receiver_id=self.header.sender_id,
            correlation_id=self.header.message_id,
            trace_id=self.header.trace_id,
            version=self.header.version,
        )

        response_payload = MessagePayload(
            data={"status": status.value, "result": data or {}, "error": error},
            metadata={
                "original_message_id": self.header.message_id,
                "processing_time": time.time() - self.header.timestamp,
            },
        )

        return A2AMessage(header=response_header, payload=response_payload)

    def is_request(self) -> bool:
        """Check if message is a request."""
        return self.header.message_type == MessageType.REQUEST

    def is_response(self) -> bool:
        """Check if message is a response."""
        return self.header.message_type == MessageType.RESPONSE

    def is_notification(self) -> bool:
        """Check if message is a notification."""
        return self.header.message_type == MessageType.NOTIFICATION


# Specific message types


@dataclass
class CapabilityInfo:
    """Capability information.

    Attributes:
        name: Capability name
        version: Capability version
        description: Capability description
        input_schema: Input schema
        output_schema: Output schema
        tags: Capability tags
        rate_limit: Rate limit information
        auth_required: Whether authentication is required
    """

    name: str
    version: str = "1.0.0"
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    rate_limit: Optional[dict[str, Any]] = None
    auth_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "tags": self.tags,
            "rate_limit": self.rate_limit,
            "auth_required": self.auth_required,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CapabilityInfo:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            input_schema=data.get("input_schema", {}),
            output_schema=data.get("output_schema", {}),
            tags=data.get("tags", []),
            rate_limit=data.get("rate_limit"),
            auth_required=data.get("auth_required", True),
        )


@dataclass
class AgentInfo:
    """Agent information.

    Attributes:
        agent_id: Agent identifier
        agent_name: Agent name
        agent_type: Agent type
        version: Agent version
        description: Agent description
        endpoint: Agent endpoint
        capabilities: Available capabilities
        status: Agent status
        metadata: Additional metadata
    """

    agent_id: str
    agent_name: str
    agent_type: str = "external"
    version: str = "1.0.0"
    description: str = ""
    endpoint: str = ""
    capabilities: list[CapabilityInfo] = field(default_factory=list)
    status: str = "active"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "version": self.version,
            "description": self.description,
            "endpoint": self.endpoint,
            "capabilities": [cap.to_dict() for cap in self.capabilities],
            "status": self.status,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentInfo:
        """Create from dictionary."""
        capabilities = [
            CapabilityInfo.from_dict(cap_data) for cap_data in data.get("capabilities", [])
        ]

        return cls(
            agent_id=data["agent_id"],
            agent_name=data["agent_name"],
            agent_type=data.get("agent_type", "external"),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            endpoint=data.get("endpoint", ""),
            capabilities=capabilities,
            status=data.get("status", "active"),
            metadata=data.get("metadata", {}),
        )


def create_handshake_message(
    sender_id: str, agent_info: AgentInfo, protocol_version: str = "1.0"
) -> A2AMessage:
    """Create handshake message."""
    header = MessageHeader(
        message_type=MessageType.HANDSHAKE, sender_id=sender_id, version=protocol_version
    )

    payload = MessagePayload(
        data=agent_info.to_dict(),
        metadata={
            "protocol_version": protocol_version,
            "handshake_timestamp": datetime.now().isoformat(),
        },
    )

    return A2AMessage(header=header, payload=payload)


def create_heartbeat_message(
    sender_id: str, status: str = "healthy", metrics: Optional[dict[str, Any]] = None
) -> A2AMessage:
    """Create heartbeat message."""
    header = MessageHeader(
        message_type=MessageType.HEARTBEAT,
        sender_id=sender_id,
        priority=MessagePriority.LOW,
        ttl_seconds=60,
    )

    payload = MessagePayload(
        data={"status": status, "metrics": metrics or {}, "timestamp": datetime.now().isoformat()}
    )

    return A2AMessage(header=header, payload=payload)


def create_capability_discovery_message(
    sender_id: str,
    query_tags: Optional[list[str]] = None,
    query_capabilities: Optional[list[str]] = None,
) -> A2AMessage:
    """Create capability discovery message."""
    header = MessageHeader(message_type=MessageType.CAPABILITY_DISCOVERY, sender_id=sender_id)

    payload = MessagePayload(
        data={"query_tags": query_tags or [], "query_capabilities": query_capabilities or []}
    )

    return A2AMessage(header=header, payload=payload)


def create_registration_message(sender_id: str, agent_info: AgentInfo) -> A2AMessage:
    """Create registration message."""
    header = MessageHeader(message_type=MessageType.REGISTRATION, sender_id=sender_id)

    payload = MessagePayload(data=agent_info.to_dict())

    return A2AMessage(header=header, payload=payload)


def create_error_message(
    sender_id: str,
    error_code: str,
    error_message: str,
    correlation_id: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
) -> A2AMessage:
    """Create error message."""
    header = MessageHeader(
        message_type=MessageType.ERROR, sender_id=sender_id, correlation_id=correlation_id
    )

    payload = MessagePayload(
        data={
            "error_code": error_code,
            "error_message": error_message,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        }
    )

    return A2AMessage(header=header, payload=payload)


def create_request_message(
    sender_id: str,
    receiver_id: str,
    capability: str,
    action: str,
    parameters: Optional[dict[str, Any]] = None,
    priority: MessagePriority = MessagePriority.NORMAL,
    trace_id: Optional[str] = None,
) -> A2AMessage:
    """Create request message."""
    header = MessageHeader(
        message_type=MessageType.REQUEST,
        sender_id=sender_id,
        receiver_id=receiver_id,
        priority=priority,
        trace_id=trace_id,
    )

    payload = MessagePayload(capability=capability, action=action, parameters=parameters or {})

    return A2AMessage(header=header, payload=payload)


def create_notification_message(
    sender_id: str,
    event_type: str,
    event_data: dict[str, Any],
    receiver_id: Optional[str] = None,
    priority: MessagePriority = MessagePriority.NORMAL,
) -> A2AMessage:
    """Create notification message."""
    header = MessageHeader(
        message_type=MessageType.NOTIFICATION,
        sender_id=sender_id,
        receiver_id=receiver_id,
        priority=priority,
    )

    payload = MessagePayload(
        action=event_type, data=event_data, metadata={"event_timestamp": datetime.now().isoformat()}
    )

    return A2AMessage(header=header, payload=payload)
