"""A2A communication protocols for agent-to-agent interaction.

Phase 4: A2A External Integration - Protocol Package
"""

from .a2a_protocol import (
    A2AProtocol,
    MessageFilter,
    MessageRouter,
    MessageValidationError,
    MessageValidator,
    ProtocolError,
    ProtocolVersionError,
    RateLimitConfig,
    RateLimiter,
    RateLimitError,
)
from .discovery import (
    AgentDiscoveryService,
    AgentStatus,
    CapabilityQuery,
    DiscoveredAgent,
    DiscoveryConfig,
    DiscoveryMethod,
    DiscoveryRegistry,
)
from .handshake import (
    AuthenticationProvider,
    HandshakeChallenge,
    HandshakeConfig,
    HandshakeContext,
    HandshakeError,
    HandshakeManager,
    HandshakeState,
    SimpleTokenAuthProvider,
)
from .message_types import (
    A2AMessage,
    AgentInfo,
    CapabilityInfo,
    MessageHeader,
    MessagePayload,
    MessagePriority,
    MessageType,
    ResponseStatus,
    create_capability_discovery_message,
    create_error_message,
    create_handshake_message,
    create_heartbeat_message,
    create_notification_message,
    create_registration_message,
    create_request_message,
)

__all__ = [
    # Message types
    "MessageType",
    "MessagePriority",
    "ResponseStatus",
    "MessageHeader",
    "MessagePayload",
    "A2AMessage",
    "CapabilityInfo",
    "AgentInfo",
    "create_handshake_message",
    "create_heartbeat_message",
    "create_capability_discovery_message",
    "create_registration_message",
    "create_error_message",
    "create_request_message",
    "create_notification_message",
    # Core protocol
    "A2AProtocol",
    "MessageRouter",
    "MessageValidator",
    "MessageFilter",
    "RateLimiter",
    "RateLimitConfig",
    "ProtocolError",
    "MessageValidationError",
    "ProtocolVersionError",
    "RateLimitError",
    # Handshake protocol
    "HandshakeManager",
    "HandshakeState",
    "HandshakeConfig",
    "HandshakeContext",
    "HandshakeChallenge",
    "AuthenticationProvider",
    "SimpleTokenAuthProvider",
    "HandshakeError",
    # Discovery service
    "AgentDiscoveryService",
    "DiscoveryRegistry",
    "DiscoveredAgent",
    "CapabilityQuery",
    "DiscoveryConfig",
    "DiscoveryMethod",
    "AgentStatus",
]

__version__ = "1.0.0"
__author__ = "T-Developer System"
__description__ = "A2A communication protocols for external agent integration"
