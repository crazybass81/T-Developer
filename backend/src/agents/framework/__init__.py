"""
T-Developer Agent Framework - Optimized Structure

Core framework for building and managing AI agents in the T-Developer platform.
Integrates with Agno Framework for ultra-high performance and AWS Agent Squad for orchestration.
"""

# Core Components
from .base_agent import BaseAgent, AgentStatus, AgentMetadata, AgentContext, AgentMessage
from .agent_manager import AgentManager, AgentInfo
from .agent_types import AgentType, AgentSpec, AGENT_SPECIFICATIONS, get_agent_dependencies, get_execution_order
from .interfaces import IAgent, ICollaborativeAgent, HealthCheckResult, AgentMetrics
from .agent_factory import AgentFactory
from .capabilities import Capability, CapabilityType, CapabilityMixin

# Communication (Unified)
from .communication_manager import (
    MessageBus, InMemoryMessageBus, AgentCommunicationManager, 
    AgentRPC, AgentCommunicationMixin, MessageType, CommunicationProtocol
)
from .message_queue import MessageQueue, MessageRouter, QueueConfig, QueueType
from .event_bus import Event, EventPriority, AgentEventMixin

# Lifecycle Management
from .lifecycle import LifecycleEvent, LifecycleStateMachine
from .initialization import AgentInitializer, InitializationConfig, InitializationResult
from .termination import AgentTerminator, TerminationOptions, TerminationResult
from .lifecycle_events import LifecycleEventHandler, LifecycleEventData, EventBus

# Workflow & Coordination
from .workflow_engine import WorkflowEngine, Workflow, WorkflowStep, WorkflowStatus
from .agent_chain_manager import AgentChainManager, AgentChain, ChainType, ChainStep, ChainStatus
from .parallel_coordinator import ParallelCoordinator, ParallelTask, TaskResult
from .dependency_manager import DependencyManager, Dependency, DependencyType

# State & Data Management
from .state_store import StateStore, MemoryStateStore, FileStateStore, StateManager
from .data_sharing import DataSharingManager, SharedData, ShareScope, DataType, AgentDataSharingMixin

# Configuration & Error Handling
from .config_schema import AgentConfig, ResourceRequirement, NetworkConfig, LogLevel
from .error_handling import AgentError, ErrorSeverity, ErrorCategory, AgentErrorHandler
from .error_recovery import ErrorRecoveryManager, RecoveryStrategy, RecoveryAction

# Monitoring & Management
from .performance_monitor import PerformanceMonitor, PerformanceMetric, AgentPerformanceStats
from .logging_tracing import AgentLogger, DistributedTracer, AgentLoggingMixin, TraceSpan
from .agent_registry import AgentRegistry, AgentRegistration
from .version_manager import VersionManager, AgentVersion

# Advanced Features
from .collaboration_patterns import PatternLibrary, CollaborationPattern, PatternType
from .sync_async_layer import SyncAsyncBridge, CommunicationLayer, CommunicationConfig
from .deployment_scaling import AgentDeploymentManager, DeploymentTarget, ScalingConfig, ScalingPolicy

__all__ = [
    # Core classes
    'BaseAgent', 'AgentStatus', 'AgentMetadata', 'AgentContext', 'AgentMessage',
    'AgentManager', 'AgentInfo',
    'AgentType', 'AgentSpec', 'AGENT_SPECIFICATIONS', 'get_agent_dependencies', 'get_execution_order',
    'IAgent', 'ICollaborativeAgent', 'HealthCheckResult', 'AgentMetrics',
    'AgentFactory',
    'Capability', 'CapabilityType', 'CapabilityMixin',
    
    # Communication (Unified)
    'MessageBus', 'InMemoryMessageBus', 'AgentCommunicationManager', 
    'AgentRPC', 'AgentCommunicationMixin', 'MessageType', 'CommunicationProtocol',
    'MessageQueue', 'MessageRouter', 'QueueConfig', 'QueueType',
    'Event', 'EventPriority', 'AgentEventMixin',
    
    # Lifecycle
    'LifecycleEvent', 'LifecycleStateMachine',
    'AgentInitializer', 'InitializationConfig', 'InitializationResult',
    'AgentTerminator', 'TerminationOptions', 'TerminationResult',
    'LifecycleEventHandler', 'LifecycleEventData', 'EventBus',
    
    # Workflow & Coordination
    'WorkflowEngine', 'Workflow', 'WorkflowStep', 'WorkflowStatus',
    'AgentChainManager', 'AgentChain', 'ChainType', 'ChainStep', 'ChainStatus',
    'ParallelCoordinator', 'ParallelTask', 'TaskResult',
    'DependencyManager', 'Dependency', 'DependencyType',
    
    # State & Data
    'StateStore', 'MemoryStateStore', 'FileStateStore', 'StateManager',
    'DataSharingManager', 'SharedData', 'ShareScope', 'DataType', 'AgentDataSharingMixin',
    
    # Configuration & Error
    'AgentConfig', 'ResourceRequirement', 'NetworkConfig', 'LogLevel',
    'AgentError', 'ErrorSeverity', 'ErrorCategory', 'AgentErrorHandler',
    'ErrorRecoveryManager', 'RecoveryStrategy', 'RecoveryAction',
    
    # Monitoring & Management
    'PerformanceMonitor', 'PerformanceMetric', 'AgentPerformanceStats',
    'AgentLogger', 'DistributedTracer', 'AgentLoggingMixin', 'TraceSpan',
    'AgentRegistry', 'AgentRegistration',
    'VersionManager', 'AgentVersion',
    
    # Advanced Features
    'PatternLibrary', 'CollaborationPattern', 'PatternType',
    'SyncAsyncBridge', 'CommunicationLayer', 'CommunicationConfig',
    'AgentDeploymentManager', 'DeploymentTarget', 'ScalingConfig', 'ScalingPolicy'
]

__version__ = "1.0.0"

# Framework performance targets (Agno integration)
PERFORMANCE_TARGETS = {
    "instantiation_time_us": 3,
    "memory_per_agent_kb": 6.5,
    "max_concurrent_agents": 10000,
    "session_duration_hours": 8
}

# Framework organization
FRAMEWORK_STRUCTURE = {
    "core_files": 6,
    "communication_files": 3,
    "lifecycle_files": 4,
    "workflow_files": 4,
    "state_files": 2,
    "config_error_files": 3,
    "monitoring_files": 4,
    "advanced_files": 3,
    "total_files": 29  # Reduced from 36
}