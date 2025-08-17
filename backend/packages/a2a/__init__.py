"""A2A (Agent-to-Agent) Broker Package.

Phase 4: A2A External Integration
Enables communication between T-Developer and external specialized agents.
"""

from .broker import (
    A2ABroker,
    AgentCapability,
    AgentRegistry,
    AgentRequest,
    AgentResponse,
    AuditLogger,
    AuthManager,
    BrokerConfig,
    BrokerStatus,
    PolicyEngine,
    RateLimiter,
)

__all__ = [
    "A2ABroker",
    "BrokerConfig",
    "BrokerStatus",
    "AgentCapability",
    "AgentRegistry",
    "PolicyEngine",
    "AuthManager",
    "RateLimiter",
    "AuditLogger",
    "AgentRequest",
    "AgentResponse",
]

__version__ = "1.0.0"
