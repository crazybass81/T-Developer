# backend/src/agents/framework/version_manager.py
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib
try:
    import semantic_version
    SEMANTIC_VERSION_AVAILABLE = True
except ImportError:
    SEMANTIC_VERSION_AVAILABLE = False
    semantic_version = None

@dataclass
class AgentVersion:
    agent_id: str
    version: str
    code_hash: str
    config_hash: str
    created_at: datetime
    created_by: str
    changelog: str
    dependencies: Dict[str, str]
    metadata: Dict[str, Any]
    is_active: bool = False

class VersionManager:
    def __init__(self):
        self.versions: Dict[str, Dict[str, AgentVersion]] = {}  # agent_id -> version -> AgentVersion
        self.active_versions: Dict[str, str] = {}  # agent_id -> active_version
    
    def create_version(self, 
                      agent_id: str,
                      version: str,
                      code: str,
                      config: Dict[str, Any],
                      changelog: str = "",
                      created_by: str = "system",
                      dependencies: Dict[str, str] = None,
                      metadata: Dict[str, Any] = None) -> AgentVersion:
        """Create a new agent version"""
        
        # Validate semantic version
        if SEMANTIC_VERSION_AVAILABLE:
            try:
                semantic_version.Version(version)
            except ValueError:
                raise ValueError(f"Invalid semantic version: {version}")
        else:
            # Basic version validation without semantic_version
            if not version or not isinstance(version, str):
                raise ValueError(f"Invalid version: {version}")
        
        # Calculate hashes
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
        
        # Create version object
        agent_version = AgentVersion(
            agent_id=agent_id,
            version=version,
            code_hash=code_hash,
            config_hash=config_hash,
            created_at=datetime.utcnow(),
            created_by=created_by,
            changelog=changelog,
            dependencies=dependencies or {},
            metadata=metadata or {}
        )
        
        # Store version
        if agent_id not in self.versions:
            self.versions[agent_id] = {}
        
        if version in self.versions[agent_id]:
            raise ValueError(f"Version {version} already exists for agent {agent_id}")
        
        self.versions[agent_id][version] = agent_version
        
        return agent_version
    
    def set_active_version(self, agent_id: str, version: str) -> bool:
        """Set active version for an agent"""
        if agent_id not in self.versions or version not in self.versions[agent_id]:
            return False
        
        # Deactivate current active version
        current_active = self.active_versions.get(agent_id)
        if current_active and current_active in self.versions[agent_id]:
            self.versions[agent_id][current_active].is_active = False
        
        # Set new active version
        self.versions[agent_id][version].is_active = True
        self.active_versions[agent_id] = version
        
        return True
    
    def get_active_version(self, agent_id: str) -> Optional[AgentVersion]:
        """Get active version for an agent"""
        active_version = self.active_versions.get(agent_id)
        if active_version and agent_id in self.versions:
            return self.versions[agent_id].get(active_version)
        return None
    
    def get_version(self, agent_id: str, version: str) -> Optional[AgentVersion]:
        """Get specific version of an agent"""
        if agent_id in self.versions:
            return self.versions[agent_id].get(version)
        return None
    
    def list_versions(self, agent_id: str) -> List[AgentVersion]:
        """List all versions for an agent"""
        if agent_id not in self.versions:
            return []
        
        versions = list(self.versions[agent_id].values())
        # Sort by semantic version if available, otherwise by string
        if SEMANTIC_VERSION_AVAILABLE:
            try:
                versions.sort(key=lambda v: semantic_version.Version(v.version), reverse=True)
            except ValueError:
                versions.sort(key=lambda v: v.version, reverse=True)
        else:
            versions.sort(key=lambda v: v.version, reverse=True)
        return versions
    
    def delete_version(self, agent_id: str, version: str) -> bool:
        """Delete a version (cannot delete active version)"""
        if agent_id not in self.versions or version not in self.versions[agent_id]:
            return False
        
        # Cannot delete active version
        if self.active_versions.get(agent_id) == version:
            raise ValueError("Cannot delete active version")
        
        del self.versions[agent_id][version]
        return True
    
    def rollback_to_version(self, agent_id: str, version: str) -> bool:
        """Rollback to a previous version"""
        if agent_id not in self.versions or version not in self.versions[agent_id]:
            return False
        
        return self.set_active_version(agent_id, version)
    
    def get_version_diff(self, agent_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """Get differences between two versions"""
        v1 = self.get_version(agent_id, version1)
        v2 = self.get_version(agent_id, version2)
        
        if not v1 or not v2:
            return {}
        
        return {
            "version1": version1,
            "version2": version2,
            "code_changed": v1.code_hash != v2.code_hash,
            "config_changed": v1.config_hash != v2.config_hash,
            "dependencies_changed": v1.dependencies != v2.dependencies,
            "time_diff": (v2.created_at - v1.created_at).total_seconds(),
            "changelog": v2.changelog
        }
    
    def find_compatible_versions(self, agent_id: str, dependency_constraints: Dict[str, str]) -> List[str]:
        """Find versions compatible with dependency constraints"""
        if agent_id not in self.versions:
            return []
        
        compatible_versions = []
        
        for version, agent_version in self.versions[agent_id].items():
            is_compatible = True
            
            for dep_name, constraint in dependency_constraints.items():
                agent_dep_version = agent_version.dependencies.get(dep_name)
                
                if not agent_dep_version:
                    is_compatible = False
                    break
                
                # Check semantic version constraint
                if SEMANTIC_VERSION_AVAILABLE:
                    try:
                        spec = semantic_version.Spec(constraint)
                        if not spec.match(semantic_version.Version(agent_dep_version)):
                            is_compatible = False
                            break
                    except ValueError:
                        is_compatible = False
                        break
                else:
                    # Simple string comparison fallback
                    if agent_dep_version != constraint:
                        is_compatible = False
                        break
            
            if is_compatible:
                compatible_versions.append(version)
        
        # Sort by semantic version if available
        if SEMANTIC_VERSION_AVAILABLE:
            try:
                compatible_versions.sort(key=lambda v: semantic_version.Version(v), reverse=True)
            except ValueError:
                compatible_versions.sort(reverse=True)
        else:
            compatible_versions.sort(reverse=True)
        return compatible_versions
    
    def get_upgrade_path(self, agent_id: str, from_version: str, to_version: str) -> List[str]:
        """Get upgrade path between versions"""
        if agent_id not in self.versions:
            return []
        
        available_versions = list(self.versions[agent_id].keys())
        
        if SEMANTIC_VERSION_AVAILABLE:
            try:
                from_sem = semantic_version.Version(from_version)
                to_sem = semantic_version.Version(to_version)
                
                # Get all versions between from and to
                intermediate_versions = []
                for version in available_versions:
                    sem_ver = semantic_version.Version(version)
                    if from_sem < sem_ver <= to_sem:
                        intermediate_versions.append(version)
                
                # Sort by semantic version
                intermediate_versions.sort(key=lambda v: semantic_version.Version(v))
                
                return [from_version] + intermediate_versions
                
            except ValueError:
                return []
        else:
            # Simple string-based comparison fallback
            intermediate_versions = [v for v in available_versions if from_version < v <= to_version]
            intermediate_versions.sort()
            return [from_version] + intermediate_versions
    
    def create_snapshot(self, agent_id: str) -> Dict[str, Any]:
        """Create snapshot of all versions for an agent"""
        if agent_id not in self.versions:
            return {}
        
        snapshot = {
            "agent_id": agent_id,
            "active_version": self.active_versions.get(agent_id),
            "versions": {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        for version, agent_version in self.versions[agent_id].items():
            snapshot["versions"][version] = {
                "version": agent_version.version,
                "code_hash": agent_version.code_hash,
                "config_hash": agent_version.config_hash,
                "created_at": agent_version.created_at.isoformat(),
                "created_by": agent_version.created_by,
                "changelog": agent_version.changelog,
                "dependencies": agent_version.dependencies,
                "metadata": agent_version.metadata,
                "is_active": agent_version.is_active
            }
        
        return snapshot
    
    def restore_from_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Restore agent versions from snapshot"""
        try:
            agent_id = snapshot["agent_id"]
            
            # Clear existing versions
            if agent_id in self.versions:
                del self.versions[agent_id]
            
            # Restore versions
            self.versions[agent_id] = {}
            
            for version, version_data in snapshot["versions"].items():
                agent_version = AgentVersion(
                    agent_id=agent_id,
                    version=version_data["version"],
                    code_hash=version_data["code_hash"],
                    config_hash=version_data["config_hash"],
                    created_at=datetime.fromisoformat(version_data["created_at"]),
                    created_by=version_data["created_by"],
                    changelog=version_data["changelog"],
                    dependencies=version_data["dependencies"],
                    metadata=version_data["metadata"],
                    is_active=version_data["is_active"]
                )
                
                self.versions[agent_id][version] = agent_version
            
            # Restore active version
            if snapshot.get("active_version"):
                self.active_versions[agent_id] = snapshot["active_version"]
            
            return True
            
        except Exception as e:
            print(f"Error restoring snapshot: {e}")
            return False