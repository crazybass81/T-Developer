"""
Core interfaces for the 9-agent pipeline
Defines data models for agent communication
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

# Type variables for generic types
T = TypeVar("T")
R = TypeVar("R")


class ProcessingStatus(Enum):
    """Agent processing status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ProjectType(Enum):
    """Supported project types"""

    WEB_APPLICATION = "web_application"
    MOBILE_APPLICATION = "mobile_application"
    DESKTOP_APPLICATION = "desktop_application"
    API_SERVICE = "api_service"
    LIBRARY = "library"
    CLI_TOOL = "cli_tool"
    MICROSERVICE = "microservice"
    FULL_STACK = "full_stack"


class Framework(Enum):
    """Supported frameworks"""

    REACT = "react"
    NEXTJS = "nextjs"
    VUE = "vue"
    ANGULAR = "angular"
    SVELTE = "svelte"
    EXPRESS = "express"
    FASTAPI = "fastapi"
    DJANGO = "django"
    FLASK = "flask"
    SPRING = "spring"


@dataclass
class PipelineContext:
    """Context shared across all agents in the pipeline"""

    pipeline_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    environment: str = "development"
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Performance tracking
    start_time: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    end_time: Optional[float] = None

    # Resource limits
    max_execution_time: int = 300  # 5 minutes
    max_memory_mb: int = 512
    max_file_size_mb: int = 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pipeline_id": self.pipeline_id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "environment": self.environment,
            "metadata": self.metadata,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "max_execution_time": self.max_execution_time,
            "max_memory_mb": self.max_memory_mb,
            "max_file_size_mb": self.max_file_size_mb,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineContext":
        """Create from dictionary"""
        return cls(
            pipeline_id=data.get("pipeline_id", str(uuid.uuid4())),
            project_id=data.get("project_id", str(uuid.uuid4())),
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.utcnow(),
            environment=data.get("environment", "development"),
            metadata=data.get("metadata", {}),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            max_execution_time=data.get("max_execution_time", 300),
            max_memory_mb=data.get("max_memory_mb", 512),
            max_file_size_mb=data.get("max_file_size_mb", 100),
        )


@dataclass
class AgentInput(Generic[T]):
    """Generic input wrapper for agents"""

    data: T
    context: PipelineContext
    previous_results: List["AgentResult"] = field(default_factory=list)

    def get_previous_result(self, agent_name: str) -> Optional["AgentResult"]:
        """Get result from a specific previous agent"""
        for result in self.previous_results:
            if result.agent_name == agent_name:
                return result
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "data": self.data
            if isinstance(self.data, (dict, list, str, int, float, bool))
            else str(self.data),
            "context": self.context.to_dict(),
            "previous_results": [r.to_dict() for r in self.previous_results],
        }


@dataclass
class AgentResult(Generic[R]):
    """Generic result wrapper for agents"""

    agent_name: str
    agent_version: str = "1.0.0"
    status: ProcessingStatus = ProcessingStatus.PENDING
    data: Optional[R] = None
    error: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None

    # Performance metrics
    execution_time_ms: float = 0.0
    memory_usage_mb: float = 0.0

    # Quality metrics
    confidence: float = 1.0
    quality_score: float = 1.0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def is_successful(self) -> bool:
        """Check if result is successful"""
        return self.status == ProcessingStatus.COMPLETED and self.error is None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "status": self.status.value,
            "data": self.data
            if isinstance(self.data, (dict, list, str, int, float, bool))
            else str(self.data),
            "error": self.error,
            "error_details": self.error_details,
            "execution_time_ms": self.execution_time_ms,
            "memory_usage_mb": self.memory_usage_mb,
            "confidence": self.confidence,
            "quality_score": self.quality_score,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentResult":
        """Create from dictionary"""
        return cls(
            agent_name=data["agent_name"],
            agent_version=data.get("agent_version", "1.0.0"),
            status=ProcessingStatus(data["status"]),
            data=data.get("data"),
            error=data.get("error"),
            error_details=data.get("error_details"),
            execution_time_ms=data.get("execution_time_ms", 0.0),
            memory_usage_mb=data.get("memory_usage_mb", 0.0),
            confidence=data.get("confidence", 1.0),
            quality_score=data.get("quality_score", 1.0),
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.utcnow(),
        )


@dataclass
class ValidationResult:
    """Result of data validation"""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        """Add validation error"""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add validation warning"""
        self.warnings.append(warning)


class BaseAgent:
    """Base class for all pipeline agents"""

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time_ms": 0.0,
            "average_execution_time_ms": 0.0,
        }

    async def validate_input(self, input_data: AgentInput[T]) -> ValidationResult:
        """Validate input data"""
        result = ValidationResult(is_valid=True)

        # Basic validation
        if input_data is None:
            result.add_error("Input data is None")

        if input_data.context is None:
            result.add_error("Pipeline context is None")

        return result

    async def process(self, input_data: AgentInput[T]) -> AgentResult[R]:
        """Process input and return result - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement process method")

    async def execute(self, input_data: AgentInput[T]) -> AgentResult[R]:
        """Execute agent with validation and metrics"""
        start_time = datetime.utcnow()

        # Validate input
        validation = await self.validate_input(input_data)
        if not validation.is_valid:
            return AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                status=ProcessingStatus.FAILED,
                error="Validation failed",
                error_details={"errors": validation.errors},
            )

        try:
            # Process input
            result = await self.process(input_data)

            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result.execution_time_ms = execution_time

            self.update_metrics(result.is_successful(), execution_time)

            return result

        except Exception as e:
            import traceback

            # Create error result
            result = AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                status=ProcessingStatus.FAILED,
                error=str(e),
                error_details={
                    "exception_type": type(e).__name__,
                    "traceback": traceback.format_exc(),
                },
            )

            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result.execution_time_ms = execution_time
            self.update_metrics(False, execution_time)

            return result

    def update_metrics(self, success: bool, execution_time_ms: float) -> None:
        """Update agent metrics"""
        self.metrics["total_executions"] += 1

        if success:
            self.metrics["successful_executions"] += 1
        else:
            self.metrics["failed_executions"] += 1

        self.metrics["total_execution_time_ms"] += execution_time_ms
        self.metrics["average_execution_time_ms"] = (
            self.metrics["total_execution_time_ms"] / self.metrics["total_executions"]
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        return {
            **self.metrics,
            "success_rate": (
                self.metrics["successful_executions"] / self.metrics["total_executions"]
                if self.metrics["total_executions"] > 0
                else 0
            ),
        }


# Export all interfaces
__all__ = [
    "ProcessingStatus",
    "ProjectType",
    "Framework",
    "PipelineContext",
    "AgentInput",
    "AgentResult",
    "ValidationResult",
    "BaseAgent",
]
