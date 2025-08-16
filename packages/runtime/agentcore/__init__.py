"""AgentCore - AWS-integrated runtime for agent lifecycle management.

Phase 2: AWS Integration - Complete Runtime Package
"""

from .agentcore import (
    Agent,
    AgentCore,
    AgentMemory,
    AgentState,
    ExecutionContext,
    ResourceMonitor,
    Task,
    TaskQueue,
    TaskResult,
    TaskStatus,
)
from .bedrock_integration import BedrockClient, BedrockResponse, BedrockService
from .bedrock_integration import RateLimiter as BedrockRateLimiter
from .bedrock_integration import StreamChunk, TokenManager, TokenUsage
from .cloudwatch_integration import (
    AlarmState,
    CloudWatchClient,
    CloudWatchService,
    DashboardWidget,
    LogEvent,
    MetricData,
    MetricUnit,
)
from .xray_integration import (
    AnnotationType,
    TraceAnnotation,
    TraceContext,
    TraceMetadata,
    TraceSegment,
    XRayClient,
    XRayService,
)

__all__ = [
    # Core runtime
    "AgentCore",
    "Agent",
    "Task",
    "TaskResult",
    "TaskQueue",
    "AgentState",
    "TaskStatus",
    "AgentMemory",
    "ExecutionContext",
    "ResourceMonitor",
    # Bedrock integration
    "BedrockService",
    "BedrockClient",
    "BedrockResponse",
    "StreamChunk",
    "TokenUsage",
    "TokenManager",
    "BedrockRateLimiter",
    # CloudWatch integration
    "CloudWatchService",
    "CloudWatchClient",
    "MetricData",
    "LogEvent",
    "DashboardWidget",
    "MetricUnit",
    "AlarmState",
    # X-Ray integration
    "XRayService",
    "XRayClient",
    "TraceContext",
    "TraceSegment",
    "TraceAnnotation",
    "TraceMetadata",
    "AnnotationType",
]

__version__ = "2.0.0"
__author__ = "T-Developer System"
__description__ = "AWS-integrated agent runtime for T-Developer v2"
