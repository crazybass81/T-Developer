from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import json
import os
import sqlite3
import redis
from datetime import datetime, timedelta

class MemoryLayer(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

class WorkingMemory(MemoryLayer):
    def __init__(self, max_size: int = 1000):
        self.memory: Dict[str, Any] = {}
        self.access_count: Dict[str, int] = {}
        self.max_size = max_size
        
    async def get(self, key: str) -> Optional[Any]:
        if key in self.memory:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.memory[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if len(self.memory) >= self.max_size:
            await self._evict_lru()
        
        self.memory[key] = value
        self.access_count[key] = 1
        
        if ttl:
            asyncio.create_task(self._expire_key(key, ttl))
    
    async def delete(self, key: str) -> None:
        self.memory.pop(key, None)
        self.access_count.pop(key, None)
    
    async def _evict_lru(self) -> None:
        if self.access_count:
            lru_key = min(self.access_count, key=self.access_count.get)
            await self.delete(lru_key)
    
    async def _expire_key(self, key: str, ttl: int) -> None:
        await asyncio.sleep(ttl)
        await self.delete(key)

class ShortTermMemory(MemoryLayer):
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        
    async def get(self, key: str) -> Optional[Any]:
        value = self.redis_client.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        serialized = json.dumps(value, default=str)
        if ttl:
            self.redis_client.setex(key, ttl, serialized)
        else:
            self.redis_client.set(key, serialized)
    
    async def delete(self, key: str) -> None:
        self.redis_client.delete(key)

class LongTermMemory(MemoryLayer):
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
    
    async def get(self, key: str) -> Optional[Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM memory WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        if result:
            cursor.execute(
                'UPDATE memory SET access_count = access_count + 1 WHERE key = ?',
                (key,)
            )
            conn.commit()
            value = json.loads(result[0])
            conn.close()
            return value
        
        conn.close()
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        conn = sqlite3.connect(self.db_path)
        serialized = json.dumps(value, default=str)
        
        conn.execute(
            'INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)',
            (key, serialized)
        )
        conn.commit()
        conn.close()
    
    async def delete(self, key: str) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute('DELETE FROM memory WHERE key = ?', (key,))
        conn.commit()
        conn.close()

class HierarchicalMemorySystem:
    def __init__(self):
        self.working_memory = WorkingMemory()
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()
    
    async def remember(self, key: str, value: Any, importance: str = 'normal') -> None:
        if importance == 'critical':
            await self.working_memory.set(key, value)
            await self.short_term_memory.set(key, value, ttl=86400)
            await self.long_term_memory.set(key, value)
        elif importance == 'high':
            await self.short_term_memory.set(key, value, ttl=3600)
            await self.long_term_memory.set(key, value)
        else:
            await self.working_memory.set(key, value)
    
    async def recall(self, key: str) -> Optional[Any]:
        # Check working memory first
        value = await self.working_memory.get(key)
        if value is not None:
            return value
        
        # Check short-term memory
        value = await self.short_term_memory.get(key)
        if value is not None:
            await self.working_memory.set(key, value)
            return value
        
        # Check long-term memory
        value = await self.long_term_memory.get(key)
        if value is not None:
            await self.short_term_memory.set(key, value, ttl=3600)
            await self.working_memory.set(key, value)
            return value
        
        return None
    
    async def forget(self, key: str) -> None:
        await self.working_memory.delete(key)
        await self.short_term_memory.delete(key)
        await self.long_term_memory.delete(key)