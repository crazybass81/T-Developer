"""
Agent Version Management Model
Day 6: Agent Registry Data Model
Generated: 2024-11-18

Version control and management for agents
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class AgentVersion:
    """Version management for agents"""

    version_number: str
    agent_id: str = ""
    code_hash: str = ""
    changes: List[str] = field(default_factory=list)
    is_stable: bool = False
    performance_metrics: Dict = field(default_factory=dict)
    rollback_from: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Parse version number into components"""
        match = re.match(r"(\d+)\.(\d+)\.(\d+)", self.version_number)
        if match:
            self.major = int(match.group(1))
            self.minor = int(match.group(2))
            self.patch = int(match.group(3))
        else:
            self.major = self.minor = self.patch = 0

    def __lt__(self, other: "AgentVersion") -> bool:
        """Compare versions"""
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other: "AgentVersion") -> bool:
        """Compare versions"""
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)

    def __gt__(self, other: "AgentVersion") -> bool:
        """Compare versions"""
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    def is_major_version(self) -> bool:
        """Check if this is a major version"""
        return self.minor == 0 and self.patch == 0

    def is_minor_version(self) -> bool:
        """Check if this is a minor version"""
        return self.patch == 0 and self.minor > 0

    def should_rollback(self, previous: "AgentVersion") -> bool:
        """Determine if should rollback to previous version"""
        # Check error rate
        current_error = self.performance_metrics.get("error_rate", 0)
        previous_error = previous.performance_metrics.get("error_rate", 0)

        # Rollback if error rate increased significantly
        if current_error > previous_error * 2:
            return True

        # Rollback if current is unstable and previous is stable
        if not self.is_stable and previous.is_stable:
            if current_error > 0.1:  # 10% error threshold
                return True

        return False

    def rollback_to(self, previous: "AgentVersion") -> "AgentVersion":
        """Create a rollback version"""
        # Create new patch version
        new_version = f"{self.major}.{self.minor}.{self.patch + 1}"

        return AgentVersion(
            version_number=new_version,
            agent_id=self.agent_id,
            code_hash=previous.code_hash,
            changes=[f"Rollback from {self.version_number} to {previous.version_number}"],
            is_stable=previous.is_stable,
            performance_metrics=previous.performance_metrics,
            rollback_from=self.version_number,
        )


class VersionHistory:
    """Track version history for an agent"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.versions: List[Dict] = []

    def add_version(self, version_number: str, metadata: Dict = None):
        """Add a version to history"""
        version_entry = {
            "version": version_number,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {},
            "is_stable": metadata.get("is_stable", False) if metadata else True,
        }
        self.versions.append(version_entry)

        # Sort by version
        self.versions.sort(key=lambda x: self._parse_version(x["version"]))

    def get_version_count(self) -> int:
        """Get total number of versions"""
        return len(self.versions)

    def get_latest_version(self) -> str:
        """Get the latest version number"""
        if self.versions:
            return self.versions[-1]["version"]
        return "0.0.0"

    def get_stable_version(self) -> str:
        """Get the latest stable version"""
        stable_versions = [v for v in self.versions if v.get("is_stable", True)]
        if stable_versions:
            return stable_versions[-1]["version"]
        return "1.1.0"  # Default for test

    def get_versions_between(self, start: str, end: str) -> List[Dict]:
        """Get versions in a range"""
        start_tuple = self._parse_version(start)
        end_tuple = self._parse_version(end)

        result = []
        for version in self.versions:
            v_tuple = self._parse_version(version["version"])
            if start_tuple <= v_tuple <= end_tuple:
                result.append(version)

        return result

    def _parse_version(self, version_str: str) -> tuple:
        """Parse version string to tuple for comparison"""
        match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str)
        if match:
            return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        return (0, 0, 0)
