# backend/src/agents/framework/message_queue.py
import asyncio
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import json
from .communication import AgentMessage, MessageType

try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    aioredis = None

class QueueType(Enum):
    MEMORY = "memory"
    REDIS = "redis"
    SQS = "sqs"

@dataclass
class QueueConfig:
    type: QueueType
    connection_string: Optional[str] = None
    max_size: int = 1000
    timeout: int = 30

class MessageQueue:
    def __init__(self, config: QueueConfig):
        self.config = config
        self.queues: Dict[str, asyncio.Queue] = {}
        self.redis_client: Optional[aioredis.Redis] = None
        self.message_handlers: Dict[str, List[Callable]] = {}
    
    async def initialize(self):
        if self.config.type == QueueType.REDIS:
            if not REDIS_AVAILABLE:
                raise ImportError("aioredis is required for Redis queue type")
            self.redis_client = await aioredis.from_url(
                self.config.connection_string or "redis://localhost:6379"
            )
    
    async def enqueue(self, queue_name: str, message: AgentMessage):
        if self.config.type == QueueType.MEMORY:
            if queue_name not in self.queues:
                self.queues[queue_name] = asyncio.Queue(maxsize=self.config.max_size)
            await self.queues[queue_name].put(message.to_dict())
        
        elif self.config.type == QueueType.REDIS and self.redis_client:
            await self.redis_client.lpush(
                f"queue:{queue_name}", 
                json.dumps(message.to_dict())
            )
    
    async def dequeue(self, queue_name: str) -> Optional[AgentMessage]:
        if self.config.type == QueueType.MEMORY:
            if queue_name in self.queues:
                try:
                    data = await asyncio.wait_for(
                        self.queues[queue_name].get(),
                        timeout=self.config.timeout
                    )
                    return self._dict_to_message(data)
                except asyncio.TimeoutError:
                    return None
        
        elif self.config.type == QueueType.REDIS and self.redis_client:
            result = await self.redis_client.brpop(
                f"queue:{queue_name}",
                timeout=self.config.timeout
            )
            if result:
                data = json.loads(result[1])
                return self._dict_to_message(data)
        
        return None
    
    def _dict_to_message(self, data: Dict[str, Any]) -> AgentMessage:
        from datetime import datetime
        return AgentMessage(
            id=data['id'],
            type=MessageType(data['type']),
            sender_id=data['sender_id'],
            recipient_id=data.get('recipient_id'),
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            correlation_id=data.get('correlation_id')
        )
    
    async def get_queue_size(self, queue_name: str) -> int:
        if self.config.type == QueueType.MEMORY:
            return self.queues.get(queue_name, asyncio.Queue()).qsize()
        elif self.config.type == QueueType.REDIS and self.redis_client:
            return await self.redis_client.llen(f"queue:{queue_name}")
        return 0

class MessageRouter:
    def __init__(self, queue: MessageQueue):
        self.queue = queue
        self.routing_rules: Dict[str, str] = {}
        self.agent_queues: Dict[str, str] = {}
    
    def register_agent(self, agent_id: str, queue_name: str):
        self.agent_queues[agent_id] = queue_name
    
    async def route_message(self, message: AgentMessage):
        if message.recipient_id:
            queue_name = self.agent_queues.get(message.recipient_id, 'default')
        else:
            queue_name = 'broadcast'
        
        await self.queue.enqueue(queue_name, message)
    
    async def start_routing(self):
        while True:
            try:
                message = await self.queue.dequeue('incoming')
                if message:
                    await self.route_message(message)
            except Exception as e:
                print(f"Routing error: {e}")
                await asyncio.sleep(1)