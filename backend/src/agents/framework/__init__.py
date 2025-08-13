"""
T-Developer Agent Framework - Organized Structure

Core framework for building and managing AI agents in the T-Developer platform.
Organized into logical modules for better maintainability.
"""

# Core Components
from .core.base_agent import (
    BaseAgent,
    AgentStatus,
    AgentMetadata,
    AgentContext,
    AgentMessage,
)
from .core.agent_types import (
    AgentType,
    AgentSpec,
    AGENT_SPECIFICATIONS,
    get_agent_dependencies,
    get_execution_order,
)
from .core.interfaces import (
    IAgent,
    ICollaborativeAgent,
    HealthCheckResult,
    AgentMetrics,
)

# Management
from .management.agent_manager import AgentManager, AgentInfo
from .management.agent_registry import AgentRegistry, AgentRegistration
from .management.agent_factory import AgentFactory
from .management.lifecycle import LifecycleEvent, LifecycleStateMachine

# Communication
from .communication.communication_manager import (
    MessageBus,
    InMemoryMessageBus,
    AgentCommunicationManager,
    AgentRPC,
    AgentCommunicationMixin,
    MessageType,
    CommunicationProtocol,
)
from .communication.message_queue import (
    MessageQueue,
    MessageRouter,
    QueueConfig,
    QueueType,
)
from .communication.event_bus import Event, EventPriority, AgentEventMixin
from .communication.data_sharing import (
    DataSharingManager,
    SharedData,
    ShareScope,
    DataType,
    AgentDataSharingMixin,
)

# Monitoring
from .monitoring.performance_monitor import (
    PerformanceMonitor,
    PerformanceMetric,
    AgentPerformanceStats,
)
from .monitoring.logging_tracing import (
    AgentLogger,
    DistributedTracer,
    AgentLoggingMixin,
    TraceSpan,
)
from .monitoring.error_handling import (
    AgentError,
    ErrorSeverity,
    ErrorCategory,
    AgentErrorHandler,
)
from .monitoring.error_recovery import (
    ErrorRecoveryManager,
    RecoveryStrategy,
    RecoveryAction,
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
