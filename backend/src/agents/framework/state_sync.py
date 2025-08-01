from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
from .state_store import StateStore

class ConflictResolver:
    """Resolves state conflicts between local and remote"""
    
    async def resolve(
        self, 
        local_state: Dict[str, Any], 
        remote_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflicts using timestamp-based strategy"""
        
        local_timestamp = local_state.get('_saved_at', '1970-01-01T00:00:00')
        remote_timestamp = remote_state.get('_saved_at', '1970-01-01T00:00:00')
        
        # Use most recent state
        if remote_timestamp > local_timestamp:
            return remote_state
        else:
            return local_state

class StateSynchronizer:
    """Synchronizes agent state between local and remote stores"""
    
    def __init__(self, local_store: StateStore, remote_store: StateStore):
        self.local_store = local_store
        self.remote_store = remote_store
        self.conflict_resolver = ConflictResolver()
        self.sync_interval = 5000  # 5 seconds
        self._sync_tasks: Dict[str, asyncio.Task] = {}
    
    async def start_sync(self, agent_id: str) -> None:
        """Start synchronization for an agent"""
        if agent_id in self._sync_tasks:
            return
        
        task = asyncio.create_task(self._sync_loop(agent_id))
        self._sync_tasks[agent_id] = task
    
    async def stop_sync(self, agent_id: str) -> None:
        """Stop synchronization for an agent"""
        if agent_id in self._sync_tasks:
            self._sync_tasks[agent_id].cancel()
            del self._sync_tasks[agent_id]
    
    async def _sync_loop(self, agent_id: str) -> None:
        """Main synchronization loop"""
        while True:
            try:
                await self._sync_agent_state(agent_id)
                await asyncio.sleep(self.sync_interval / 1000)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Sync error for agent {agent_id}: {e}")
                await asyncio.sleep(1)  # Brief pause on error
    
    async def _sync_agent_state(self, agent_id: str) -> None:
        """Synchronize state for a single agent"""
        # Load states from both stores
        local_state, remote_state = await asyncio.gather(
            self.local_store.load_state(agent_id),
            self.remote_store.load_state(agent_id),
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(local_state, Exception):
            local_state = None
        if isinstance(remote_state, Exception):
            remote_state = None
        
        # Sync logic
        if local_state and remote_state:
            # Check for conflicts
            if await self._detect_conflict(local_state, remote_state):
                # Resolve conflict
                resolved_state = await self.conflict_resolver.resolve(
                    local_state, remote_state
                )
                
                # Save resolved state to both stores
                await asyncio.gather(
                    self.local_store.save_state(agent_id, resolved_state),
                    self.remote_store.save_state(agent_id, resolved_state)
                )
        elif local_state and not remote_state:
            # Push local to remote
            await self.remote_store.save_state(agent_id, local_state)
        elif not local_state and remote_state:
            # Pull remote to local
            await self.local_store.save_state(agent_id, remote_state)
    
    async def _detect_conflict(
        self, 
        local_state: Dict[str, Any], 
        remote_state: Dict[str, Any]
    ) -> bool:
        """Detect if there's a conflict between states"""
        # Simple conflict detection based on timestamps
        local_timestamp = local_state.get('_saved_at')
        remote_timestamp = remote_state.get('_saved_at')
        
        if not local_timestamp or not remote_timestamp:
            return True  # Assume conflict if no timestamps
        
        # Check if states are significantly different
        time_diff = abs(
            datetime.fromisoformat(local_timestamp.replace('Z', '+00:00')) -
            datetime.fromisoformat(remote_timestamp.replace('Z', '+00:00'))
        ).total_seconds()
        
        return time_diff > 1  # Conflict if more than 1 second apart