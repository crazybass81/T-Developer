from typing import Dict, Any, Optional, List
import json
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime

class StateStore(ABC):
    """Abstract base class for agent state storage"""
    
    @abstractmethod
    async def save_state(self, agent_id: str, state: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    async def load_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def delete_state(self, agent_id: str) -> None:
        pass
    
    @abstractmethod
    async def list_states(self, prefix: str = "") -> List[str]:
        pass

class MemoryStateStore(StateStore):
    """In-memory state store for development/testing"""
    
    def __init__(self):
        self._states: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def save_state(self, agent_id: str, state: Dict[str, Any]) -> None:
        async with self._lock:
            self._states[agent_id] = {
                **state,
                '_saved_at': datetime.utcnow().isoformat()
            }
    
    async def load_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            return self._states.get(agent_id)
    
    async def delete_state(self, agent_id: str) -> None:
        async with self._lock:
            self._states.pop(agent_id, None)
    
    async def list_states(self, prefix: str = "") -> List[str]:
        async with self._lock:
            return [
                agent_id for agent_id in self._states.keys()
                if agent_id.startswith(prefix)
            ]

class FileStateStore(StateStore):
    """File-based state store"""
    
    def __init__(self, base_path: str = "./agent_states"):
        self.base_path = base_path
        import os
        os.makedirs(base_path, exist_ok=True)
    
    async def save_state(self, agent_id: str, state: Dict[str, Any]) -> None:
        file_path = f"{self.base_path}/{agent_id}.json"
        state_with_meta = {
            **state,
            '_saved_at': datetime.utcnow().isoformat()
        }
        
        with open(file_path, 'w') as f:
            json.dump(state_with_meta, f, indent=2)
    
    async def load_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        file_path = f"{self.base_path}/{agent_id}.json"
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    async def delete_state(self, agent_id: str) -> None:
        file_path = f"{self.base_path}/{agent_id}.json"
        try:
            import os
            os.remove(file_path)
        except FileNotFoundError:
            pass
    
    async def list_states(self, prefix: str = "") -> List[str]:
        import os
        import glob
        
        pattern = f"{self.base_path}/{prefix}*.json"
        files = glob.glob(pattern)
        
        return [
            os.path.basename(f).replace('.json', '')
            for f in files
        ]

class StateManager:
    """Manages agent state persistence and synchronization"""
    
    def __init__(self, store: StateStore):
        self.store = store
        self._state_cache: Dict[str, Dict[str, Any]] = {}
        self._dirty_states: set = set()
    
    async def save_agent_state(self, agent_id: str, state: Dict[str, Any]) -> None:
        """Save agent state"""
        self._state_cache[agent_id] = state.copy()
        self._dirty_states.add(agent_id)
        await self.store.save_state(agent_id, state)
    
    async def load_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent state"""
        # Check cache first
        if agent_id in self._state_cache:
            return self._state_cache[agent_id].copy()
        
        # Load from store
        state = await self.store.load_state(agent_id)
        if state:
            self._state_cache[agent_id] = state.copy()
        
        return state
    
    async def delete_agent_state(self, agent_id: str) -> None:
        """Delete agent state"""
        self._state_cache.pop(agent_id, None)
        self._dirty_states.discard(agent_id)
        await self.store.delete_state(agent_id)
    
    async def sync_dirty_states(self) -> None:
        """Sync all dirty states to persistent storage"""
        for agent_id in list(self._dirty_states):
            if agent_id in self._state_cache:
                await self.store.save_state(agent_id, self._state_cache[agent_id])
        
        self._dirty_states.clear()
    
    async def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of all agent states"""
        agent_ids = await self.store.list_states()
        
        return {
            'total_agents': len(agent_ids),
            'cached_states': len(self._state_cache),
            'dirty_states': len(self._dirty_states),
            'agent_ids': agent_ids
        }