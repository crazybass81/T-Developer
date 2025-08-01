"""
T-Developer Agent Framework

Core framework for building and managing AI agents in the T-Developer platform.
Integrates with Agno Framework for ultra-high performance and AWS Agent Squad for orchestration.
"""

from .base_agent import BaseAgent, AgentStatus, AgentMetadata, AgentContext
from .interfaces import IAgent, ICollaborativeAgent, AgentMessage, HealthCheckResult, AgentMetrics
from .agent_factory import AgentFactory
from .capabilities import Capability, CapabilityType, CapabilityMixin
from .lifecycle import LifecycleEvent, LifecycleStateMachine
from .initialization import AgentInitializer, InitializationConfig, InitializationResult
from .state_store import StateStore, MemoryStateStore, FileStateStore, StateManager
from .termination import AgentTerminator, TerminationOptions, TerminationResult
from .lifecycle_events import LifecycleEventHandler, LifecycleEventData, EventBus
from .state_sync import StateSynchronizer, ConflictResolver
from .config_schema import AgentConfig, ResourceRequirement, NetworkConfig, LogLevel
from .error_handling import AgentError, ErrorSeverity, ErrorCategory, AgentErrorHandler
from .error_recovery import ErrorRecoveryManager, RecoveryStrategy, RecoveryAction
from .communication import MessageType, CommunicationProtocol, AgentCommunicationMixin
from .message_queue import MessageQueue, MessageRouter, QueueConfig, QueueType
from .event_bus import Event, EventPriority, AgentEventMixin
from .sync_async_layer import SyncAsyncBridge, CommunicationLayer, CommunicationConfig
from .data_sharing import DataSharingManager, SharedData, ShareScope, DataType, AgentDataSharingMixin
from .workflow_engine import WorkflowEngine, Workflow, WorkflowStep, WorkflowStatus
from .agent_chain import AgentChainManager, AgentChain, ChainType, ChainStep
from .parallel_coordinator import ParallelCoordinator, ParallelTask, TaskResult
from .dependency_manager import DependencyManager, Dependency, DependencyType
from .collaboration_patterns import PatternLibrary, CollaborationPattern, PatternType
from .agent_registry import AgentRegistry, AgentRegistration
from .performance_monitor import PerformanceMonitor, PerformanceMetric, AgentPerformanceStats
from .logging_tracing import AgentLogger, DistributedTracer, AgentLoggingMixin, TraceSpan
from .version_manager import VersionManager, AgentVersion
from .deployment_scaling import AgentDeploymentManager, DeploymentTarget, ScalingConfig, ScalingPolicy

__all__ = [
    # Base classes
    'BaseAgent',
    'AgentStatus', 
    'AgentMetadata',
    'AgentContext',
    
    # Interfaces
    'IAgent',
    'ICollaborativeAgent',
    'AgentMessage',
    'HealthCheckResult',
    'AgentMetrics',
    
    # Factory
    'AgentFactory',
    
    # Capabilities
    'Capability',
    'CapabilityType',
    'CapabilityMixin',
    
    # Lifecycle
    'LifecycleEvent',
    'LifecycleStateMachine',
    'LifecycleEventHandler',
    'LifecycleEventData',
    'EventBus',
    
    # Initialization & Termination
    'AgentInitializer',
    'InitializationConfig',
    'InitializationResult',
    'AgentTerminator',
    'TerminationOptions',
    'TerminationResult',
    
    # State management
    'StateStore',
    'MemoryStateStore',
    'FileStateStore',
    'StateManager',
    'StateSynchronizer',
    'ConflictResolver',
    
    # Configuration
    'AgentConfig',
    'ResourceRequirement',
    'NetworkConfig',
    'LogLevel',
    
    # Error handling
    'AgentError',
    'ErrorSeverity',
    'ErrorCategory',
    'AgentErrorHandler',
    
    # Error recovery
    'ErrorRecoveryManager',
    'RecoveryStrategy',
    'RecoveryAction',
    
    # Communication
    'MessageType',
    'CommunicationProtocol',
    'AgentCommunicationMixin',
    
    # Message queue
    'MessageQueue',
    'MessageRouter',
    'QueueConfig',
    'QueueType',
    
    # Event system
    'Event',
    'EventPriority',
    'AgentEventMixin',
    
    # Sync/Async layer
    'SyncAsyncBridge',
    'CommunicationLayer',
    'CommunicationConfig',
    
    # Data sharing
    'DataSharingManager',
    'SharedData',
    'ShareScope',
    'DataType',
    'AgentDataSharingMixin',
    
    # Workflow engine
    'WorkflowEngine',
    'Workflow',
    'WorkflowStep',
    'WorkflowStatus',
    
    # Agent chains
    'AgentChainManager',
    'AgentChain',
    'ChainType',
    'ChainStep',
    
    # Parallel coordination
    'ParallelCoordinator',
    'ParallelTask',
    'TaskResult',
    
    # Dependency management
    'DependencyManager',
    'Dependency',
    'DependencyType',
    
    # Collaboration patterns
    'PatternLibrary',
    'CollaborationPattern',
    'PatternType',
    
    # Agent registry
    'AgentRegistry',
    'AgentRegistration',
    
    # Performance monitoring
    'PerformanceMonitor',
    'PerformanceMetric',
    'AgentPerformanceStats',
    
    # Logging & tracing
    'AgentLogger',
    'DistributedTracer',
    'AgentLoggingMixin',
    'TraceSpan',
    
    # Version management
    'VersionManager',
    'AgentVersion',
    
    # Deployment & scaling
    'AgentDeploymentManager',
    'DeploymentTarget',
    'ScalingConfig',
    'ScalingPolicy'
]

__version__ = "1.0.0"

# Framework performance targets (Agno integration)
PERFORMANCE_TARGETS = {
    "instantiation_time_us": 3,
    "memory_per_agent_kb": 6.5,
    "max_concurrent_agents": 10000,
    "session_duration_hours": 8
}