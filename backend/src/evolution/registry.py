"""
Agent Registry Module

Manages agent storage, versioning, and lifecycle.
Provides CRUD operations for evolved agents.
"""

import asyncio
import json
import logging
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent lifecycle status"""
    CREATED = "created"
    TRAINING = "training"
    TESTING = "testing"
    VALIDATED = "validated"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    QUARANTINED = "quarantined"
    ARCHIVED = "archived"


class AgentType(Enum):
    """Types of agents in the system"""
    NL_INPUT = "nl_input"
    UI_SELECTION = "ui_selection"
    PARSER = "parser"
    COMPONENT_DECISION = "component_decision"
    MATCH_RATE = "match_rate"
    SEARCH = "search"
    GENERATION = "generation"
    ASSEMBLY = "assembly"
    DOWNLOAD = "download"
    META_ORCHESTRATOR = "meta_orchestrator"


@dataclass
class AgentMetrics:
    """Performance metrics for an agent"""
    memory_usage_kb: float = 0.0
    instantiation_time_us: float = 0.0
    execution_time_ms: float = 0.0
    accuracy: float = 0.0
    throughput_ops_per_sec: float = 0.0
    error_rate: float = 0.0
    fitness_score: float = 0.0
    safety_score: float = 1.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class AgentVersion:
    """Version information for an agent"""
    version: str
    created_at: datetime
    created_by: str = "evolution_engine"
    changelog: str = ""
    code_hash: str = ""
    parent_version: Optional[str] = None
    is_stable: bool = False
    metrics: Optional[AgentMetrics] = None


@dataclass
class Agent:
    """Agent entity with full metadata"""
    id: str
    name: str
    agent_type: AgentType
    status: AgentStatus
    code: str
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    versions: List[AgentVersion] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Optional[AgentMetrics] = None
    
    def __post_init__(self):
        """Post-initialization setup"""
        if not self.metrics:
            self.metrics = AgentMetrics()
        
        # Create initial version if none exists
        if not self.versions:
            initial_version = AgentVersion(
                version=self.version,
                created_at=self.created_at,
                code_hash=self._calculate_code_hash(),
                changelog="Initial version"
            )
            self.versions.append(initial_version)
    
    def _calculate_code_hash(self) -> str:
        """Calculate hash of the agent code"""
        return hashlib.sha256(self.code.encode()).hexdigest()[:16]
    
    def update_code(self, new_code: str, changelog: str = "") -> str:
        """
        Update agent code and create new version
        
        Args:
            new_code: New agent code
            changelog: Description of changes
            
        Returns:
            str: New version number
        """
        # Increment version
        major, minor, patch = map(int, self.version.split('.'))
        patch += 1
        new_version = f"{major}.{minor}.{patch}"
        
        # Create version record
        version_record = AgentVersion(
            version=new_version,
            created_at=datetime.now(),
            changelog=changelog,
            code_hash=hashlib.sha256(new_code.encode()).hexdigest()[:16],
            parent_version=self.version
        )
        
        # Update agent
        self.code = new_code
        self.version = new_version
        self.updated_at = datetime.now()
        self.versions.append(version_record)
        
        return new_version
    
    def get_version(self, version: str) -> Optional[AgentVersion]:
        """Get specific version of the agent"""
        for v in self.versions:
            if v.version == version:
                return v
        return None
    
    def get_latest_stable_version(self) -> Optional[AgentVersion]:
        """Get latest stable version"""
        stable_versions = [v for v in self.versions if v.is_stable]
        if stable_versions:
            return max(stable_versions, key=lambda v: v.created_at)
        return None
    
    def mark_version_stable(self, version: str) -> bool:
        """Mark a version as stable"""
        for v in self.versions:
            if v.version == version:
                v.is_stable = True
                return True
        return False


class AgentRegistry:
    """
    Registry for managing evolved agents
    
    Provides:
    - CRUD operations
    - Version management
    - Search and filtering
    - Metrics tracking
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize agent registry"""
        self.data_dir = data_dir or Path("/home/ec2-user/T-DeveloperMVP/backend/data/agents")
        self.registry_file = self.data_dir / "registry.json"
        self.agents_dir = self.data_dir / "agents"
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage
        self.agents: Dict[str, Agent] = {}
        self.type_index: Dict[AgentType, Set[str]] = {t: set() for t in AgentType}
        self.status_index: Dict[AgentStatus, Set[str]] = {s: set() for s in AgentStatus}
        self.tag_index: Dict[str, Set[str]] = {}
        
        self._lock = asyncio.Lock()
        
        logger.info(f"Agent Registry initialized at {self.data_dir}")
    
    async def initialize(self) -> bool:
        """
        Initialize registry and load existing agents
        
        Returns:
            bool: True if initialization successful
        """
        try:
            await self._load_registry()
            logger.info(f"Loaded {len(self.agents)} agents from registry")
            return True
        except Exception as e:
            logger.error(f"Registry initialization failed: {str(e)}")
            return False
    
    async def create_agent(
        self,
        name: str,
        agent_type: AgentType,
        code: str,
        description: str = "",
        tags: Optional[Set[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """
        Create a new agent
        
        Args:
            name: Agent name
            agent_type: Type of agent
            code: Agent implementation code
            description: Agent description
            tags: Optional tags for categorization
            config: Agent configuration
            
        Returns:
            Agent: Created agent
        """
        async with self._lock:
            agent_id = str(uuid.uuid4())
            
            agent = Agent(
                id=agent_id,
                name=name,
                agent_type=agent_type,
                status=AgentStatus.CREATED,
                code=code,
                description=description,
                tags=tags or set(),
                config=config or {}
            )
            
            # Store agent
            self.agents[agent_id] = agent
            
            # Update indexes
            self.type_index[agent_type].add(agent_id)
            self.status_index[AgentStatus.CREATED].add(agent_id)
            
            for tag in agent.tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = set()
                self.tag_index[tag].add(agent_id)
            
            # Save to disk
            await self._save_agent(agent)
            await self._save_registry()
            
            logger.info(f"Created agent {name} ({agent_id}) of type {agent_type.value}")
            return agent
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    async def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        for agent in self.agents.values():
            if agent.name == name:
                return agent
        return None
    
    async def update_agent(self, agent_id: str, **updates) -> bool:
        """
        Update agent fields
        
        Args:
            agent_id: Agent ID
            **updates: Fields to update
            
        Returns:
            bool: True if updated successfully
        """
        async with self._lock:
            agent = self.agents.get(agent_id)
            if not agent:
                return False
            
            # Update fields
            for field, value in updates.items():
                if hasattr(agent, field):
                    old_value = getattr(agent, field)
                    setattr(agent, field, value)
                    
                    # Update indexes if needed
                    if field == 'status':
                        self.status_index[old_value].discard(agent_id)
                        self.status_index[value].add(agent_id)
                    elif field == 'agent_type':
                        self.type_index[old_value].discard(agent_id)
                        self.type_index[value].add(agent_id)
                    elif field == 'tags':
                        # Update tag index
                        for tag in old_value:
                            self.tag_index[tag].discard(agent_id)
                        for tag in value:
                            if tag not in self.tag_index:
                                self.tag_index[tag] = set()
                            self.tag_index[tag].add(agent_id)
            
            agent.updated_at = datetime.now()
            
            # Save changes
            await self._save_agent(agent)
            await self._save_registry()
            
            return True
    
    async def update_agent_code(self, agent_id: str, new_code: str, changelog: str = "") -> Optional[str]:
        """
        Update agent code and create new version
        
        Args:
            agent_id: Agent ID
            new_code: New code
            changelog: Change description
            
        Returns:
            str: New version number if successful
        """
        async with self._lock:
            agent = self.agents.get(agent_id)
            if not agent:
                return None
            
            new_version = agent.update_code(new_code, changelog)
            
            # Save changes
            await self._save_agent(agent)
            await self._save_registry()
            
            logger.info(f"Updated agent {agent.name} to version {new_version}")
            return new_version
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        async with self._lock:
            agent = self.agents.get(agent_id)
            if not agent:
                return False
            
            # Remove from indexes
            self.type_index[agent.agent_type].discard(agent_id)
            self.status_index[agent.status].discard(agent_id)
            
            for tag in agent.tags:
                self.tag_index[tag].discard(agent_id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]
            
            # Remove from storage
            del self.agents[agent_id]
            
            # Delete files
            agent_file = self.agents_dir / f"{agent_id}.json"
            if agent_file.exists():
                agent_file.unlink()
            
            await self._save_registry()
            
            logger.info(f"Deleted agent {agent.name} ({agent_id})")
            return True
    
    async def list_agents(
        self,
        agent_type: Optional[AgentType] = None,
        status: Optional[AgentStatus] = None,
        tags: Optional[Set[str]] = None,
        limit: Optional[int] = None
    ) -> List[Agent]:
        """
        List agents with optional filtering
        
        Args:
            agent_type: Filter by agent type
            status: Filter by status
            tags: Filter by tags (must have all tags)
            limit: Maximum number of agents to return
            
        Returns:
            List of matching agents
        """
        result_ids = set(self.agents.keys())
        
        # Apply filters
        if agent_type:
            result_ids &= self.type_index[agent_type]
        
        if status:
            result_ids &= self.status_index[status]
        
        if tags:
            for tag in tags:
                if tag in self.tag_index:
                    result_ids &= self.tag_index[tag]
                else:
                    result_ids = set()  # Tag doesn't exist
                    break
        
        # Get agents
        agents = [self.agents[agent_id] for agent_id in result_ids]
        
        # Sort by updated_at descending
        agents.sort(key=lambda a: a.updated_at, reverse=True)
        
        # Apply limit
        if limit:
            agents = agents[:limit]
        
        return agents
    
    async def search_agents(self, query: str) -> List[Agent]:
        """
        Search agents by name or description
        
        Args:
            query: Search query
            
        Returns:
            List of matching agents
        """
        query_lower = query.lower()
        matching_agents = []
        
        for agent in self.agents.values():
            if (query_lower in agent.name.lower() or 
                query_lower in agent.description.lower() or
                any(query_lower in tag.lower() for tag in agent.tags)):
                matching_agents.append(agent)
        
        # Sort by relevance (name match first, then description)
        def relevance_score(agent):
            score = 0
            if query_lower in agent.name.lower():
                score += 10
            if query_lower in agent.description.lower():
                score += 5
            if any(query_lower in tag.lower() for tag in agent.tags):
                score += 3
            return score
        
        matching_agents.sort(key=relevance_score, reverse=True)
        return matching_agents
    
    async def get_agents_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Get all agents of a specific type"""
        return await self.list_agents(agent_type=agent_type)
    
    async def get_deployed_agents(self) -> List[Agent]:
        """Get all deployed agents"""
        return await self.list_agents(status=AgentStatus.DEPLOYED)
    
    async def update_agent_metrics(self, agent_id: str, metrics: AgentMetrics) -> bool:
        """Update agent performance metrics"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        
        agent.metrics = metrics
        agent.updated_at = datetime.now()
        
        # Save changes
        await self._save_agent(agent)
        return True
    
    async def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        stats = {
            'total_agents': len(self.agents),
            'by_type': {t.value: len(ids) for t, ids in self.type_index.items()},
            'by_status': {s.value: len(ids) for s, ids in self.status_index.items()},
            'total_tags': len(self.tag_index),
            'most_common_tags': sorted(
                [(tag, len(ids)) for tag, ids in self.tag_index.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
        
        return stats
    
    # Private helper methods
    
    async def _load_registry(self) -> None:
        """Load registry from disk"""
        if not self.registry_file.exists():
            logger.info("No existing registry found, starting fresh")
            return
        
        try:
            with open(self.registry_file, 'r') as f:
                registry_data = json.load(f)
            
            # Load each agent
            for agent_data in registry_data.get('agents', []):
                agent = self._deserialize_agent(agent_data)
                self.agents[agent.id] = agent
                
                # Update indexes
                self.type_index[agent.agent_type].add(agent.id)
                self.status_index[agent.status].add(agent.id)
                
                for tag in agent.tags:
                    if tag not in self.tag_index:
                        self.tag_index[tag] = set()
                    self.tag_index[tag].add(agent.id)
            
        except Exception as e:
            logger.error(f"Failed to load registry: {str(e)}")
            raise
    
    async def _save_registry(self) -> None:
        """Save registry index to disk"""
        try:
            registry_data = {
                'version': '1.0',
                'updated_at': datetime.now().isoformat(),
                'agents': [self._serialize_agent_metadata(agent) for agent in self.agents.values()]
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(registry_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save registry: {str(e)}")
            raise
    
    async def _save_agent(self, agent: Agent) -> None:
        """Save individual agent to disk"""
        try:
            agent_file = self.agents_dir / f"{agent.id}.json"
            agent_data = self._serialize_agent(agent)
            
            with open(agent_file, 'w') as f:
                json.dump(agent_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save agent {agent.id}: {str(e)}")
            raise
    
    def _serialize_agent(self, agent: Agent) -> Dict[str, Any]:
        """Serialize agent to dict"""
        data = asdict(agent)
        
        # Convert enums to strings
        data['agent_type'] = agent.agent_type.value
        data['status'] = agent.status.value
        data['tags'] = list(agent.tags)
        
        return data
    
    def _serialize_agent_metadata(self, agent: Agent) -> Dict[str, Any]:
        """Serialize agent metadata for registry index"""
        return {
            'id': agent.id,
            'name': agent.name,
            'agent_type': agent.agent_type.value,
            'status': agent.status.value,
            'version': agent.version,
            'created_at': agent.created_at.isoformat(),
            'updated_at': agent.updated_at.isoformat(),
            'tags': list(agent.tags),
            'code': agent.code,  # Include code for proper deserialization
            'description': agent.description
        }
    
    def _deserialize_agent(self, data: Dict[str, Any]) -> Agent:
        """Deserialize agent from dict"""
        # Convert strings back to enums
        data['agent_type'] = AgentType(data['agent_type'])
        data['status'] = AgentStatus(data['status'])
        data['tags'] = set(data.get('tags', []))
        
        # Parse datetime strings
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Handle metrics
        if 'metrics' in data and data['metrics']:
            metrics_data = data['metrics']
            if 'last_updated' in metrics_data:
                metrics_data['last_updated'] = datetime.fromisoformat(metrics_data['last_updated'])
            data['metrics'] = AgentMetrics(**metrics_data)
        
        # Handle versions
        if 'versions' in data:
            versions = []
            for v_data in data['versions']:
                v_data['created_at'] = datetime.fromisoformat(v_data['created_at'])
                if 'metrics' in v_data and v_data['metrics']:
                    m_data = v_data['metrics']
                    if 'last_updated' in m_data:
                        m_data['last_updated'] = datetime.fromisoformat(m_data['last_updated'])
                    v_data['metrics'] = AgentMetrics(**m_data)
                versions.append(AgentVersion(**v_data))
            data['versions'] = versions
        
        return Agent(**data)