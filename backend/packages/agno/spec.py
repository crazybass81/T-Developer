"""Agent Specification models for Agno.

This module defines the structure of agent specifications
following the agent_spec.yaml format from the architecture docs.
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class AgentCapability(str, Enum):
    """Types of agent capabilities."""
    
    ANALYZE = "analyze"
    GENERATE = "generate"
    TRANSFORM = "transform"
    VALIDATE = "validate"
    ORCHESTRATE = "orchestrate"
    OBSERVE = "observe"
    CURATE = "curate"


class MemoryAccess(str, Enum):
    """Memory context access types."""
    
    O_CTX = "O_CTX"  # Orchestrator context
    A_CTX = "A_CTX"  # Agent context
    S_CTX = "S_CTX"  # Shared context
    U_CTX = "U_CTX"  # User context
    OBS_CTX = "OBS_CTX"  # Observer context


class AgentInputSchema(BaseModel):
    """Schema for agent inputs."""
    
    name: str = Field(description="Input parameter name")
    type: str = Field(description="Data type (string, dict, list, etc.)")
    required: bool = Field(default=True, description="Whether this input is required")
    description: str = Field(default="", description="Description of the input")
    default: Optional[Any] = Field(default=None, description="Default value if not required")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "code",
                "type": "string",
                "required": True,
                "description": "Source code to analyze"
            }
        }


class AgentOutputSchema(BaseModel):
    """Schema for agent outputs."""
    
    name: str = Field(description="Output field name")
    type: str = Field(description="Data type")
    description: str = Field(default="", description="Description of the output")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "analysis",
                "type": "dict",
                "description": "Code analysis results"
            }
        }


class AgentPolicy(BaseModel):
    """Agent policies and constraints."""
    
    ai_first: bool = Field(default=True, description="Use AI by default (AIFIRST-001)")
    dedup_required: bool = Field(default=True, description="Check for duplicates (DD-Gate)")
    pii_allowed: bool = Field(default=False, description="Can handle PII data")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout_seconds: int = Field(default=300, description="Execution timeout")
    cost_limit_usd: Optional[float] = Field(default=None, description="Cost limit per execution")
    
    @validator('timeout_seconds')
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError("Timeout must be positive")
        if v > 3600:
            raise ValueError("Timeout cannot exceed 1 hour")
        return v


class NonFunctionalRequirements(BaseModel):
    """Non-functional requirements for the agent."""
    
    latency_p95_ms: Optional[int] = Field(default=None, description="95th percentile latency")
    throughput_rps: Optional[int] = Field(default=None, description="Required requests per second")
    availability_percent: Optional[float] = Field(default=99.0, description="Required availability")
    cost_per_1k_tokens_max_usd: Optional[float] = Field(default=None, description="Max cost per 1k tokens")


@dataclass
class AgentSpec:
    """Complete agent specification.
    
    This represents the full agent_spec.yaml structure that Agno creates
    and uses to request implementation from Claude Code.
    
    Attributes:
        name: Unique agent name
        version: Semantic version
        purpose: What the agent does
        capability: Primary capability type
        inputs: List of input schemas
        outputs: List of output schemas
        policies: Agent policies
        memory_read: Memory contexts to read from
        memory_write: Memory contexts to write to
        dependencies: Other agents this depends on
        tools: External tools/APIs needed
        tests: Test specifications
        non_functionals: Performance requirements
        deployment: Deployment configuration
        tags: Categorization tags
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    name: str
    version: str = "1.0.0"
    purpose: str = ""
    capability: AgentCapability = AgentCapability.ANALYZE
    
    inputs: List[AgentInputSchema] = field(default_factory=list)
    outputs: List[AgentOutputSchema] = field(default_factory=list)
    policies: AgentPolicy = field(default_factory=AgentPolicy)
    
    memory_read: List[MemoryAccess] = field(default_factory=lambda: [MemoryAccess.S_CTX])
    memory_write: List[MemoryAccess] = field(default_factory=lambda: [MemoryAccess.A_CTX])
    
    dependencies: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    tests: List[Dict[str, Any]] = field(default_factory=list)
    
    non_functionals: Optional[NonFunctionalRequirements] = None
    deployment: Dict[str, Any] = field(default_factory=dict)
    
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_yaml(self) -> str:
        """Convert specification to YAML format.
        
        Returns:
            YAML string representation
        """
        data = {
            "name": self.name,
            "version": self.version,
            "purpose": self.purpose,
            "capability": self.capability.value,
            "inputs": [inp.dict() for inp in self.inputs],
            "outputs": [out.dict() for out in self.outputs],
            "policies": self.policies.dict(),
            "memory": {
                "read": [ctx.value for ctx in self.memory_read],
                "write": [ctx.value for ctx in self.memory_write]
            },
            "dependencies": self.dependencies,
            "tools": self.tools,
            "tests": self.tests,
            "deployment": self.deployment,
            "tags": self.tags,
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat()
            }
        }
        
        if self.non_functionals:
            data["non_functionals"] = self.non_functionals.dict(exclude_none=True)
        
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> AgentSpec:
        """Create specification from YAML string.
        
        Args:
            yaml_str: YAML string representation
            
        Returns:
            AgentSpec instance
        """
        data = yaml.safe_load(yaml_str)
        
        # Parse inputs
        inputs = [AgentInputSchema(**inp) for inp in data.get("inputs", [])]
        
        # Parse outputs
        outputs = [AgentOutputSchema(**out) for out in data.get("outputs", [])]
        
        # Parse policies
        policies = AgentPolicy(**data.get("policies", {}))
        
        # Parse memory access
        memory = data.get("memory", {})
        memory_read = [MemoryAccess(ctx) for ctx in memory.get("read", ["S_CTX"])]
        memory_write = [MemoryAccess(ctx) for ctx in memory.get("write", ["A_CTX"])]
        
        # Parse non-functionals
        non_functionals = None
        if "non_functionals" in data:
            non_functionals = NonFunctionalRequirements(**data["non_functionals"])
        
        # Parse metadata
        metadata = data.get("metadata", {})
        created_at = datetime.fromisoformat(metadata.get("created_at", datetime.utcnow().isoformat()))
        updated_at = datetime.fromisoformat(metadata.get("updated_at", datetime.utcnow().isoformat()))
        
        return cls(
            name=data["name"],
            version=data.get("version", "1.0.0"),
            purpose=data.get("purpose", ""),
            capability=AgentCapability(data.get("capability", "analyze")),
            inputs=inputs,
            outputs=outputs,
            policies=policies,
            memory_read=memory_read,
            memory_write=memory_write,
            dependencies=data.get("dependencies", []),
            tools=data.get("tools", []),
            tests=data.get("tests", []),
            non_functionals=non_functionals,
            deployment=data.get("deployment", {}),
            tags=data.get("tags", []),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def save_to_file(self, path: Path) -> None:
        """Save specification to a YAML file.
        
        Args:
            path: Path to save the file
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(self.to_yaml())
    
    @classmethod
    def load_from_file(cls, path: Path) -> AgentSpec:
        """Load specification from a YAML file.
        
        Args:
            path: Path to the YAML file
            
        Returns:
            AgentSpec instance
        """
        with open(path, "r") as f:
            return cls.from_yaml(f.read())
    
    def validate(self) -> List[str]:
        """Validate the specification.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.name:
            errors.append("Agent name is required")
        
        if not self.purpose:
            errors.append("Agent purpose is required")
        
        if not self.inputs:
            errors.append("At least one input is required")
        
        if not self.outputs:
            errors.append("At least one output is required")
        
        # Check for duplicate input names
        input_names = [inp.name for inp in self.inputs]
        if len(input_names) != len(set(input_names)):
            errors.append("Duplicate input names found")
        
        # Check for duplicate output names
        output_names = [out.name for out in self.outputs]
        if len(output_names) != len(set(output_names)):
            errors.append("Duplicate output names found")
        
        return errors