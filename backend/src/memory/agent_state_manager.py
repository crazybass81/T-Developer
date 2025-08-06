from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import gzip
import sqlite3
import uuid
import os

@dataclass
class Checkpoint:
    id: str
    timestamp: datetime
    state: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class AgentState:
    agent_id: str
    session_id: str
    context: Dict[str, Any]
    memory: Dict[str, Any]
    last_activity: datetime
    checkpoints: List[Checkpoint]

class StateStore:
    def __init__(self, db_path: str = "agent_states.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS agent_states (
                agent_id TEXT,
                session_id TEXT,
                data BLOB,
                timestamp TIMESTAMP,
                ttl INTEGER,
                PRIMARY KEY (agent_id, session_id)
            )
        ''')
        conn.commit()
        conn.close()
    
    async def save(self, agent_id: str, session_id: str, data: bytes, ttl: int = 86400):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            'INSERT OR REPLACE INTO agent_states VALUES (?, ?, ?, ?, ?)',
            (agent_id, session_id, data, datetime.utcnow(), ttl)
        )
        conn.commit()
        conn.close()
    
    async def load(self, agent_id: str, session_id: str) -> Optional[bytes]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT data FROM agent_states WHERE agent_id = ? AND session_id = ?',
            (agent_id, session_id)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

class CompressionEngine:
    async def compress(self, data: str) -> bytes:
        return gzip.compress(data.encode('utf-8'))
    
    async def decompress(self, data: bytes) -> str:
        return gzip.decompress(data).decode('utf-8')

class AgentStateManager:
    def __init__(self):
        self.state_store = StateStore()
        self.compression_engine = CompressionEngine()
    
    async def save_state(self, state: AgentState) -> None:
        # Create checkpoint if needed (before serialization)
        if self._should_create_checkpoint(state):
            await self._create_checkpoint(state)
        
        # Serialize state
        serialized = self._serialize_state(state)
        
        # Compress
        compressed = await self.compression_engine.compress(serialized)
        
        # Save to store
        await self.state_store.save(
            state.agent_id,
            state.session_id,
            compressed,
            self._calculate_ttl(state)
        )
    
    async def load_state(self, agent_id: str, session_id: str) -> Optional[AgentState]:
        # Load from store
        compressed_data = await self.state_store.load(agent_id, session_id)
        if not compressed_data:
            return None
        
        # Decompress
        serialized = await self.compression_engine.decompress(compressed_data)
        
        # Deserialize
        state = self._deserialize_state(serialized)
        
        # Validate
        if not self._validate_state(state):
            raise ValueError("Invalid agent state")
        
        return state
    
    def _serialize_state(self, state: AgentState) -> str:
        # Convert datetime objects to ISO strings
        state_dict = asdict(state)
        state_dict['last_activity'] = state.last_activity.isoformat()
        
        for checkpoint in state_dict['checkpoints']:
            checkpoint['timestamp'] = checkpoint['timestamp'].isoformat()
        
        return json.dumps(state_dict, default=str)
    
    def _deserialize_state(self, serialized: str) -> AgentState:
        data = json.loads(serialized)
        
        # Convert ISO strings back to datetime
        data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        
        checkpoints = []
        for cp_data in data['checkpoints']:
            cp_data['timestamp'] = datetime.fromisoformat(cp_data['timestamp'])
            checkpoints.append(Checkpoint(**cp_data))
        
        data['checkpoints'] = checkpoints
        return AgentState(**data)
    
    def _validate_state(self, state: AgentState) -> bool:
        return (
            state.agent_id and
            state.session_id and
            isinstance(state.context, dict) and
            isinstance(state.memory, dict) and
            isinstance(state.last_activity, datetime)
        )
    
    def _calculate_ttl(self, state: AgentState) -> int:
        # TTL based on last activity (24 hours default)
        return 86400
    
    def _should_create_checkpoint(self, state: AgentState) -> bool:
        if not state.checkpoints:
            return True
        
        last_checkpoint = state.checkpoints[-1]
        time_since_last = datetime.utcnow() - last_checkpoint.timestamp
        
        # Create checkpoint every 1 second for testing
        return time_since_last > timedelta(seconds=1)
    
    async def _create_checkpoint(self, state: AgentState) -> None:
        checkpoint = Checkpoint(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            state={
                'context': state.context.copy(),
                'memory': state.memory.copy()
            },
            metadata={
                'memory_size': len(json.dumps(state.memory)),
                'context_keys': list(state.context.keys())
            }
        )
        
        state.checkpoints.append(checkpoint)
        
        # Keep only last 10 checkpoints
        if len(state.checkpoints) > 10:
            state.checkpoints = state.checkpoints[-10:]
    
    async def restore_from_checkpoint(
        self,
        agent_id: str,
        session_id: str,
        checkpoint_id: str
    ) -> Optional[AgentState]:
        state = await self.load_state(agent_id, session_id)
        if not state:
            return None
        
        # Find checkpoint
        checkpoint = next(
            (cp for cp in state.checkpoints if cp.id == checkpoint_id),
            None
        )
        
        if not checkpoint:
            return None
        
        # Restore state from checkpoint
        state.context = checkpoint.state['context']
        state.memory = checkpoint.state['memory']
        state.last_activity = datetime.utcnow()
        
        return state