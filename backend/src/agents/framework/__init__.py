"""
T-Developer Agent Framework - Organized Structure

Core framework for building and managing AI agents in the T-Developer platform.
Organized into logical modules for better maintainability.
"""

# Communication
from .communication.communication_manager import (
    AgentCommunicationManager,
    AgentCommunicationMixin,
    AgentRPC,
    CommunicationProtocol,
    InMemoryMessageBus,
    MessageBus,
    MessageType,
)
from .communication.data_sharing import (
    AgentDataSharingMixin,
    DataSharingManager,
    DataType,
    SharedData,
    ShareScope,
)
from .communication.event_bus import AgentEventMixin, Event, EventPriority
from .communication.message_queue import MessageQueue, MessageRouter, QueueConfig, QueueType
from .core.agent_types import (
    AGENT_SPECIFICATIONS,
    AgentSpec,
    AgentType,
    get_agent_dependencies,
    get_execution_order,
)

# Core Components
from .core.base_agent import AgentContext, AgentMessage, AgentMetadata, AgentStatus, BaseAgent
from .core.interfaces import AgentMetrics, HealthCheckResult, IAgent, ICollaborativeAgent
from .management.agent_factory import AgentFactory

# Management
from .management.agent_manager import AgentInfo, AgentManager
from .management.agent_registry import AgentRegistration, AgentRegistry
from .management.lifecycle import LifecycleEvent, LifecycleStateMachine
from .monitoring.error_handling import AgentError, AgentErrorHandler, ErrorCategory, ErrorSeverity
from .monitoring.error_recovery import ErrorRecoveryManager, RecoveryAction, RecoveryStrategy
from .monitoring.logging_tracing import AgentLogger, AgentLoggingMixin, DistributedTracer, TraceSpan

# Monitoring
from .monitoring.performance_monitor import (
    AgentPerformanceStats,
    PerformanceMetric,
    PerformanceMonitor,
)

# Version
__version__ = "2.0.0"

# Convenience exports
__all__ = [
    # Core
    "BaseAgent",
    "AgentStatus",
    "AgentType",
    "IAgent",
    # Management
    "AgentManager",
    "AgentRegistry",
    "AgentFactory",
    # Communication
    "AgentCommunicationManager",
    "MessageQueue",
    "EventBus",
    # Monitoring
    "PerformanceMonitor",
    "AgentLogger",
    "AgentError",
    # Version
    "__version__",
]
