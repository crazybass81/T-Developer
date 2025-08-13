"""
Agent Registration API Models
Pydantic models for agent registration endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent status enum"""
    ANALYZING = "analyzing"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    FAILED = "failed"
    ANALYSIS_FAILED = "analysis_failed"


class AgentCapability(BaseModel):
    """Agent capability model"""
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Capability parameters")


class AgentVersion(BaseModel):
    """Agent version information"""
    version: str = Field(..., description="Version number")
    changelog: str = Field(..., description="Version changelog")
    created_at: datetime = Field(..., description="Version creation time")
    created_by: str = Field(..., description="Version creator")
    code_hash: str = Field(..., description="Code hash for this version")


class AgentExecution(BaseModel):
    """Agent execution record"""
    execution_id: str = Field(..., description="Execution ID")
    started_at: datetime = Field(..., description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Execution completion time")
    status: str = Field(..., description="Execution status")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    tokens_used: Optional[int] = Field(None, description="AI tokens used")
    cost_usd: Optional[float] = Field(None, description="Execution cost in USD")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class AgentRegistrationRequest(BaseModel):
    """Request model for agent registration"""
    agent_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Name of the agent"
    )
    agent_code: str = Field(
        ...,
        min_length=10,
        description="Python code for the agent"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Agent description"
    )
    version: Optional[str] = Field(
        "1.0.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Semantic version"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Tags for categorization"
    )
    dependencies: Optional[Dict[str, str]] = Field(
        None,
        description="Python package dependencies"
    )
    
    @validator('agent_name')
    def validate_agent_name(cls, v):
        """Validate agent name format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Agent name must be alphanumeric with underscores or hyphens only')
        return v
    
    @validator('agent_code')
    def validate_agent_code(cls, v):
        """Basic code validation"""
        if 'class' not in v:
            raise ValueError('Agent code must contain a class definition')
        if 'execute' not in v:
            raise ValueError('Agent code must contain an execute method')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags"""
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v


class AgentRegistrationResponse(BaseModel):
    """Response model for agent registration"""
    status: str = Field(..., description="Registration status")
    agent_id: Optional[str] = Field(None, description="Generated agent ID")
    analysis_task_id: Optional[str] = Field(None, description="Background analysis task ID")
    message: str = Field(..., description="Status message")
    errors: Optional[List[str]] = Field(None, description="Validation errors if any")
    estimated_completion_time: Optional[int] = Field(None, description="Estimated seconds for analysis")


class AgentUpdateRequest(BaseModel):
    """Request model for agent update"""
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Agent name")
    description: Optional[str] = Field(None, max_length=500, description="Agent description")
    code: Optional[str] = Field(None, min_length=10, description="Updated agent code")
    version: Optional[str] = Field(None, pattern=r"^\d+\.\d+\.\d+$", description="New version")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    dependencies: Optional[Dict[str, str]] = Field(None, description="Updated dependencies")


class AgentDetailResponse(BaseModel):
    """Detailed agent information response"""
    agent_id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent name")
    version: str = Field(..., description="Current version")
    description: Optional[str] = Field(None, description="Agent description")
    code: Optional[str] = Field(None, description="Agent code (if authorized)")
    ai_capabilities: Dict[str, Any] = Field(..., description="AI-analyzed capabilities")
    ai_quality_score: Optional[float] = Field(None, description="AI quality assessment score")
    execution_count: int = Field(0, description="Total execution count")
    success_rate: float = Field(0.0, description="Success rate percentage")
    last_executed_at: Optional[datetime] = Field(None, description="Last execution time")
    created_at: datetime = Field(..., description="Creation time")
    created_by: str = Field(..., description="Creator username")
    versions: List[AgentVersion] = Field(..., description="Version history")
    recent_executions: List[AgentExecution] = Field(..., description="Recent execution history")
    tags: Optional[List[str]] = Field(None, description="Agent tags")
    status: Optional[str] = Field(None, description="Agent status")


class AgentListResponse(BaseModel):
    """Response model for agent listing"""
    agents: List[Dict[str, Any]] = Field(..., description="List of agents")
    total_count: int = Field(..., description="Total number of agents")
    limit: int = Field(..., description="Results per page")
    offset: int = Field(..., description="Starting offset")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Applied filters")


class AIAnalysisResult(BaseModel):
    """AI analysis result model"""
    capabilities: List[AgentCapability] = Field(..., description="Detected capabilities")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")
    suggestions: List[str] = Field(..., description="Improvement suggestions")
    security_issues: Optional[List[str]] = Field(None, description="Detected security issues")
    performance_metrics: Dict[str, Any] = Field(..., description="Expected performance metrics")
    ai_model_used: str = Field(..., description="AI model used for analysis")
    analysis_duration_ms: int = Field(..., description="Analysis duration in milliseconds")
    
    model_config = {'protected_namespaces': ()}


class ValidationResult(BaseModel):
    """Code validation result"""
    is_valid: bool = Field(..., description="Validation status")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Code improvement suggestions")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Code metrics")