"""
Agent Model
Day 6: Agent Registry Data Model
Generated: 2024-11-18

Core model for agent metadata and constraint validation
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class Agent:
    """Agent model with metadata and constraint validation"""

    # Required fields
    name: str

    # Optional fields with defaults
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    version: str = "1.0.0"
    size_kb: float = 0.0
    instantiation_us: float = 0.0
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    fitness_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Constraints
    MAX_SIZE_KB: float = 6.5
    MAX_INSTANTIATION_US: float = 3.0

    def meets_constraints(self) -> bool:
        """Check if agent meets size and speed constraints"""
        return (
            self.size_kb <= self.MAX_SIZE_KB and self.instantiation_us <= self.MAX_INSTANTIATION_US
        )

    def get_violations(self) -> List[str]:
        """Get list of constraint violations"""
        violations = []

        if self.size_kb > self.MAX_SIZE_KB:
            violations.append("size")

        if self.instantiation_us > self.MAX_INSTANTIATION_US:
            violations.append("speed")

        return violations

    def get_tag_count(self) -> int:
        """Get count of tags in metadata"""
        if "tags" in self.metadata:
            return len(self.metadata["tags"])
        return 0

    def to_json(self) -> str:
        """Serialize agent to JSON"""
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "size_kb": self.size_kb,
            "instantiation_us": self.instantiation_us,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
            "fitness_score": self.fitness_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "Agent":
        """Deserialize agent from JSON"""
        data = json.loads(json_str)

        # Convert datetime strings back to datetime objects
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        return cls(**data)

    def update(self, **kwargs):
        """Update agent attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def calculate_efficiency_score(self) -> float:
        """Calculate overall efficiency score"""
        size_score = max(0, 1 - (self.size_kb / self.MAX_SIZE_KB))
        speed_score = max(0, 1 - (self.instantiation_us / self.MAX_INSTANTIATION_US))

        # Weighted average
        return size_score * 0.4 + speed_score * 0.6

    def __repr__(self) -> str:
        return (
            f"Agent(name='{self.name}', version='{self.version}', "
            f"size={self.size_kb}KB, speed={self.instantiation_us}μs, "
            f"fitness={self.fitness_score:.2f})"
        )
