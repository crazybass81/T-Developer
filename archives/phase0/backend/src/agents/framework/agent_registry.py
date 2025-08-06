# backend/src/agents/framework/agent_registry.py
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import json

@dataclass
class AgentRegistration:
    agent_id: str
    agent_type: str
    version: str
    capabilities: List[str]
    status: str
    endpoint: Optional[str] = None
    metadata: Dict[str, Any] = None
    registered_at: datetime = None
    last_heartbeat: Optional[datetime] = None
    tags: Set[str] = None

class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, AgentRegistration] = {}
        self.type_index: Dict[str, Set[str]] = {}
        self.capability_index: Dict[str, Set[str]] = {}
        self.tag_index: Dict[str, Set[str]] = {}
    
    def register_agent(self, registration: AgentRegistration) -> bool:
        """Register a new agent"""
        if not registration.registered_at:
            registration.registered_at = datetime.utcnow()
        
        if not registration.tags:
            registration.tags = set()
        
        # Store registration
        self.agents[registration.agent_id] = registration
        
        # Update indexes
        self._update_indexes(registration)
        
        return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent"""
        if agent_id not in self.agents:
            return False
        
        registration = self.agents[agent_id]
        
        # Remove from indexes
        self._remove_from_indexes(registration)
        
        # Remove from main registry
        del self.agents[agent_id]
        
        return True
    
    def update_agent_status(self, agent_id: str, status: str) -> bool:
        """Update agent status"""
        if agent_id not in self.agents:
            return False
        
        self.agents[agent_id].status = status
        self.agents[agent_id].last_heartbeat = datetime.utcnow()
        return True
    
    def heartbeat(self, agent_id: str) -> bool:
        """Record agent heartbeat"""
        if agent_id not in self.agents:
            return False
        
        self.agents[agent_id].last_heartbeat = datetime.utcnow()
        return True
    
    def find_agents_by_type(self, agent_type: str) -> List[AgentRegistration]:
        """Find agents by type"""
        agent_ids = self.type_index.get(agent_type, set())
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
    
    def find_agents_by_capability(self, capability: str) -> List[AgentRegistration]:
        """Find agents by capability"""
        agent_ids = self.capability_index.get(capability, set())
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
    
    def find_agents_by_tag(self, tag: str) -> List[AgentRegistration]:
        """Find agents by tag"""
        agent_ids = self.tag_index.get(tag, set())
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
    
    def find_agents(self, 
                   agent_type: Optional[str] = None,
                   capabilities: Optional[List[str]] = None,
                   tags: Optional[List[str]] = None,
                   status: Optional[str] = None) -> List[AgentRegistration]:
        """Find agents by multiple criteria"""
        candidates = set(self.agents.keys())
        
        # Filter by type
        if agent_type:
            type_agents = self.type_index.get(agent_type, set())
            candidates = candidates.intersection(type_agents)
        
        # Filter by capabilities
        if capabilities:
            for capability in capabilities:
                cap_agents = self.capability_index.get(capability, set())
                candidates = candidates.intersection(cap_agents)
        
        # Filter by tags
        if tags:
            for tag in tags:
                tag_agents = self.tag_index.get(tag, set())
                candidates = candidates.intersection(tag_agents)
        
        # Filter by status
        if status:
            candidates = {aid for aid in candidates 
                         if self.agents[aid].status == status}
        
        return [self.agents[aid] for aid in candidates]
    
    def get_agent_info(self, agent_id: str) -> Optional[AgentRegistration]:
        """Get agent information"""
        return self.agents.get(agent_id)
    
    def list_all_agents(self) -> List[AgentRegistration]:
        """List all registered agents"""
        return list(self.agents.values())
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        total_agents = len(self.agents)
        status_counts = {}
        type_counts = {}
        
        for agent in self.agents.values():
            # Count by status
            status_counts[agent.status] = status_counts.get(agent.status, 0) + 1
            
            # Count by type
            type_counts[agent.agent_type] = type_counts.get(agent.agent_type, 0) + 1
        
        return {
            "total_agents": total_agents,
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "total_types": len(self.type_index),
            "total_capabilities": len(self.capability_index),
            "total_tags": len(self.tag_index)
        }
    
    def cleanup_stale_agents(self, timeout_minutes: int = 30) -> List[str]:
        """Remove agents that haven't sent heartbeat"""
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        stale_agents = []
        
        for agent_id, registration in list(self.agents.items()):
            last_heartbeat = registration.last_heartbeat or registration.registered_at
            
            if last_heartbeat < cutoff_time:
                stale_agents.append(agent_id)
                self.unregister_agent(agent_id)
        
        return stale_agents
    
    def export_registry(self) -> str:
        """Export registry to JSON"""
        export_data = {}
        for agent_id, registration in self.agents.items():
            reg_dict = asdict(registration)
            # Convert datetime objects to ISO strings
            reg_dict['registered_at'] = registration.registered_at.isoformat()
            if registration.last_heartbeat:
                reg_dict['last_heartbeat'] = registration.last_heartbeat.isoformat()
            # Convert set to list
            reg_dict['tags'] = list(registration.tags)
            export_data[agent_id] = reg_dict
        
        return json.dumps(export_data, indent=2)
    
    def _update_indexes(self, registration: AgentRegistration):
        """Update search indexes"""
        agent_id = registration.agent_id
        
        # Type index
        if registration.agent_type not in self.type_index:
            self.type_index[registration.agent_type] = set()
        self.type_index[registration.agent_type].add(agent_id)
        
        # Capability index
        for capability in registration.capabilities:
            if capability not in self.capability_index:
                self.capability_index[capability] = set()
            self.capability_index[capability].add(agent_id)
        
        # Tag index
        for tag in registration.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(agent_id)
    
    def _remove_from_indexes(self, registration: AgentRegistration):
        """Remove from search indexes"""
        agent_id = registration.agent_id
        
        # Type index
        if registration.agent_type in self.type_index:
            self.type_index[registration.agent_type].discard(agent_id)
            if not self.type_index[registration.agent_type]:
                del self.type_index[registration.agent_type]
        
        # Capability index
        for capability in registration.capabilities:
            if capability in self.capability_index:
                self.capability_index[capability].discard(agent_id)
                if not self.capability_index[capability]:
                    del self.capability_index[capability]
        
        # Tag index
        for tag in registration.tags:
            if tag in self.tag_index:
                self.tag_index[tag].discard(agent_id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]