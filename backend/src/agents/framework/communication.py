# backend/src/agents/framework/communication.py
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
import uuid
from datetime import datetime

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"

@dataclass
class AgentMessage:
    id: str
    type: MessageType
    sender_id: str
    recipient_id: Optional[str]
    content: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type.value,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id
        }

class CommunicationProtocol:
    def __init__(self):
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
    
    def register_handler(self, message_type: str, handler: Callable):
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    async def send_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        if message.type == MessageType.REQUEST:
            future = asyncio.Future()
            self.pending_requests[message.id] = future
            await self.message_queue.put(message)
            return await future
        else:
            await self.message_queue.put(message)
            return None
    
    async def handle_message(self, message: AgentMessage):
        if message.type == MessageType.RESPONSE and message.correlation_id:
            future = self.pending_requests.pop(message.correlation_id, None)
            if future:
                future.set_result(message)
                return
        
        handlers = self.message_handlers.get(message.type.value, [])
        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                print(f"Handler error: {e}")

class AgentCommunicationMixin:
    def __init__(self):
        self.protocol = CommunicationProtocol()
        self.agent_id = str(uuid.uuid4())
    
    async def send_request(self, recipient_id: str, content: Dict[str, Any]) -> Optional[AgentMessage]:
        message = AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.REQUEST,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            content=content,
            timestamp=datetime.utcnow()
        )
        return await self.protocol.send_message(message)
    
    async def send_notification(self, recipient_id: str, content: Dict[str, Any]):
        message = AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.NOTIFICATION,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            content=content,
            timestamp=datetime.utcnow()
        )
        await self.protocol.send_message(message)
    
    async def broadcast(self, content: Dict[str, Any]):
        message = AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.BROADCAST,
            sender_id=self.agent_id,
            recipient_id=None,
            content=content,
            timestamp=datetime.utcnow()
        )
        await self.protocol.send_message(message)