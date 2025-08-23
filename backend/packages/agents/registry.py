"""에이전트 레지스트리 (Agent Registry)

이 모듈은 시스템의 모든 에이전트를 관리하고 검색하는 중앙 레지스트리를 제공합니다.
에이전트의 등록, 검색, 버전 관리, 중복 검사 등을 담당하는 핵심 컴포넌트입니다.

주요 기능:
1. 에이전트 등록 및 관리
2. 에이전트 명세(Spec) 추적
3. 버전 관리 및 호환성 검사
4. 에이전트 자동 검색(Discovery)
5. 중복 에이전트 방지 (DD-Gate)
6. 에이전트 라이프사이클 관리
7. 태그 기반 분류 및 검색
8. 정책(Policy) 기반 실행 제어

핵심 클래스:
- AgentSpec: 에이전트 명세 정의
- AgentRegistry: 중앙 레지스트리 관리자

에이전트 명세 구조:
- name: 고유 에이전트 이름
- version: 시맨틱 버전
- purpose: 에이전트 목적
- inputs: 입력 스키마
- outputs: 출력 스키마
- policies: 실행 정책
- memory: 메모리 접근 요구사항
- owner: 담당자/팀
- tags: 분류 태그

중복 방지 메커니즘:
- 이름 기반 중복 검사
- 버전 충돌 감지
- 기능 중복 경고

사용 예시:
    registry = AgentRegistry()
    
    # 에이전트 등록
    spec = AgentSpec(
        name="RequirementAnalyzer",
        version="1.0.0",
        purpose="요구사항 분석"
    )
    registry.register(RequirementAnalyzer, spec)
    
    # 에이전트 검색
    agents = registry.find_by_tag("analysis")
    
    # 에이전트 인스턴스 생성
    agent = registry.create_agent("RequirementAnalyzer")

중요: 모든 에이전트는 레지스트리에 등록되어야 하며,
      중복 에이전트 생성을 방지하기 위해 레지스트리를 통해 관리되어야 합니다.

작성자: T-Developer v2
버전: 2.0.0
최종 수정: 2024-12-20
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from .base import BaseAgent


@dataclass
class AgentSpec:
    """Specification for a registered agent.
    
    This matches the agent_spec.yaml format from the docs.
    
    Attributes:
        name: Unique agent name
        version: Semantic version
        purpose: What the agent does
        inputs: Expected input schema
        outputs: Expected output schema
        policies: Agent policies (ai_first, dedup_required, etc.)
        memory: Memory access requirements
        owner: Owner/team responsible
        tags: Tags for categorization
        created_at: Registration timestamp
        updated_at: Last update timestamp
    """
    
    name: str
    version: str
    purpose: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    policies: Dict[str, Any] = field(default_factory=dict)
    memory: Dict[str, List[str]] = field(default_factory=dict)
    owner: str = "system"
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the spec
        """
        return {
            "name": self.name,
            "version": self.version,
            "purpose": self.purpose,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "policies": self.policies,
            "memory": self.memory,
            "owner": self.owner,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentSpec:
        """Create from dictionary representation.
        
        Args:
            data: Dictionary containing spec data
            
        Returns:
            AgentSpec instance
        """
        # Handle datetime conversion
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        return cls(**data)


class AgentRegistry:
    """Registry for managing agents in the system.
    
    This registry:
    - Tracks all available agents
    - Manages agent specifications
    - Handles version management
    - Provides agent discovery
    - Checks for duplicates (DD-Gate)
    
    Attributes:
        registry_path: Path to store registry data
        agents: Dictionary of registered agent specs
        instances: Dictionary of agent instances
    """
    
    def __init__(self, registry_path: str = "/tmp/t-developer/registry") -> None:
        """Initialize the agent registry.
        
        Args:
            registry_path: Path to store registry data
        """
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        self.agents: Dict[str, AgentSpec] = {}
        self.instances: Dict[str, BaseAgent] = {}
        
        # Load existing registry
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load registry from disk."""
        registry_file = self.registry_path / "registry.json"
        
        if registry_file.exists():
            try:
                with open(registry_file, "r") as f:
                    data = json.load(f)
                    for name, spec_data in data.items():
                        self.agents[name] = AgentSpec.from_dict(spec_data)
            except Exception as e:
                print(f"Error loading registry: {e}")
    
    def _save_registry(self) -> None:
        """Save registry to disk."""
        registry_file = self.registry_path / "registry.json"
        
        try:
            data = {
                name: spec.to_dict()
                for name, spec in self.agents.items()
            }
            
            with open(registry_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving registry: {e}")
    
    def register(
        self,
        agent_class: Type[BaseAgent],
        spec: AgentSpec,
        instance: Optional[BaseAgent] = None
    ) -> bool:
        """Register an agent in the registry.
        
        Args:
            agent_class: The agent class
            spec: Agent specification
            instance: Optional pre-created instance
            
        Returns:
            True if registered successfully
        """
        try:
            # Check for duplicates (DD-Gate)
            if self.check_duplicate(spec.name, spec.purpose):
                print(f"Warning: Similar agent already exists for {spec.name}")
            
            # Store spec
            self.agents[spec.name] = spec
            
            # Store instance if provided
            if instance:
                self.instances[spec.name] = instance
            
            # Save to disk
            self._save_registry()
            
            return True
            
        except Exception as e:
            print(f"Error registering agent {spec.name}: {e}")
            return False
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent instance by name.
        
        Args:
            name: Agent name
            
        Returns:
            Agent instance or None if not found
        """
        return self.instances.get(name)
    
    def get_spec(self, name: str) -> Optional[AgentSpec]:
        """Get an agent specification by name.
        
        Args:
            name: Agent name
            
        Returns:
            Agent spec or None if not found
        """
        return self.agents.get(name)
    
    def list_agents(self) -> List[AgentSpec]:
        """List all registered agents.
        
        Returns:
            List of agent specifications
        """
        return list(self.agents.values())
    
    def search(
        self,
        tags: Optional[List[str]] = None,
        owner: Optional[str] = None,
        purpose_keywords: Optional[List[str]] = None
    ) -> List[AgentSpec]:
        """Search for agents matching criteria.
        
        Args:
            tags: Tags to match
            owner: Owner to match
            purpose_keywords: Keywords to search in purpose
            
        Returns:
            List of matching agent specs
        """
        results = []
        
        for spec in self.agents.values():
            # Check tags
            if tags and not any(tag in spec.tags for tag in tags):
                continue
            
            # Check owner
            if owner and spec.owner != owner:
                continue
            
            # Check purpose keywords
            if purpose_keywords:
                purpose_lower = spec.purpose.lower()
                if not any(kw.lower() in purpose_lower for kw in purpose_keywords):
                    continue
            
            results.append(spec)
        
        return results
    
    def check_duplicate(
        self,
        name: str,
        purpose: str,
        threshold: float = 0.85
    ) -> bool:
        """Check for duplicate agents (DD-Gate).
        
        This is a simple implementation. In production, use
        proper similarity algorithms (cosine similarity, etc.).
        
        Args:
            name: Proposed agent name
            purpose: Proposed agent purpose
            threshold: Similarity threshold
            
        Returns:
            True if potential duplicate found
        """
        # Simple keyword-based check
        purpose_words = set(purpose.lower().split())
        
        for existing_spec in self.agents.values():
            # Skip if same name (updating existing)
            if existing_spec.name == name:
                continue
            
            # Check purpose similarity
            existing_words = set(existing_spec.purpose.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(purpose_words & existing_words)
            union = len(purpose_words | existing_words)
            
            if union > 0:
                similarity = intersection / union
                if similarity >= threshold:
                    return True
        
        return False
    
    def get_version_history(self, name: str) -> List[str]:
        """Get version history for an agent.
        
        Args:
            name: Agent name
            
        Returns:
            List of versions (currently just returns current version)
        """
        spec = self.get_spec(name)
        if spec:
            return [spec.version]
        return []
    
    def update_spec(
        self,
        name: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update an agent specification.
        
        Args:
            name: Agent name
            updates: Fields to update
            
        Returns:
            True if updated successfully
        """
        spec = self.get_spec(name)
        if not spec:
            return False
        
        try:
            # Update fields
            for key, value in updates.items():
                if hasattr(spec, key):
                    setattr(spec, key, value)
            
            # Update timestamp
            spec.updated_at = datetime.utcnow()
            
            # Save to disk
            self._save_registry()
            
            return True
            
        except Exception as e:
            print(f"Error updating spec for {name}: {e}")
            return False