"""
Message Queue System for asynchronous agent communication
Integrates with AWS SQS for distributed processing
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging

from src.services.aws_clients import get_sqs_client

logger = logging.getLogger(__name__)


class QueueType(Enum):
    """Types of message queues"""
    AGENT_TASKS = "agent-tasks"
    PIPELINE_COMMANDS = "pipeline-commands"
    RESULTS = "results"
    NOTIFICATIONS = "notifications"
    DEAD_LETTER = "dead-letter"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Message:
    """Message structure for queue"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    queue_type: QueueType = QueueType.AGENT_TASKS
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    expiration: Optional[datetime] = None
    headers: Dict[str, str] = field(default_factory=dict)
    body: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    
    def to_sqs_format(self) -> Dict[str, Any]:
        """Convert to SQS message format"""
        return {
            "MessageBody": json.dumps(self.body),
            "MessageAttributes": {
                "message_id": {"DataType": "String", "StringValue": self.message_id},
                "queue_type": {"DataType": "String", "StringValue": self.queue_type.value},
                "priority": {"DataType": "Number", "StringValue": str(self.priority.value)},
                "correlation_id": {"DataType": "String", "StringValue": self.correlation_id or ""},
                "timestamp": {"DataType": "String", "StringValue": self.timestamp.isoformat()},
                "retry_count": {"DataType": "Number", "StringValue": str(self.retry_count)}
            }
        }
    
    @classmethod
    def from_sqs_message(cls, sqs_message: Dict[str, Any]) -> 'Message':
        """Create message from SQS format"""
        attrs = sqs_message.get("MessageAttributes", {})
        
        return cls(
            message_id=attrs.get("message_id", {}).get("StringValue", str(uuid.uuid4())),
            queue_type=QueueType(attrs.get("queue_type", {}).get("StringValue", "agent-tasks")),
            priority=MessagePriority(int(attrs.get("priority", {}).get("StringValue", "2"))),
            correlation_id=attrs.get("correlation_id", {}).get("StringValue"),
            timestamp=datetime.fromisoformat(
                attrs.get("timestamp", {}).get("StringValue", datetime.utcnow().isoformat())
            ),
            retry_count=int(attrs.get("retry_count", {}).get("StringValue", "0")),
            body=json.loads(sqs_message.get("Body", "{}"))
        )
    
    def is_expired(self) -> bool:
        """Check if message has expired"""
        if self.expiration is None:
            return False
        return datetime.utcnow() > self.expiration


class MessageQueue:
    """Message queue for agent communication"""
    
    def __init__(self, queue_name: str, queue_type: QueueType,
                 use_sqs: bool = False, queue_url: Optional[str] = None):
        self.queue_name = queue_name
        self.queue_type = queue_type
        self.use_sqs = use_sqs
        self.queue_url = queue_url
        
        # Local queue for in-memory processing
        self._local_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        
        # SQS client
        self._sqs_client = get_sqs_client() if use_sqs else None
        
        # Message handlers
        self._handlers: Dict[str, Callable] = {}
        
        # Processing state
        self._processing = False
        self._processed_count = 0
        self._failed_count = 0
    
    async def send_message(self, message: Message) -> str:
        """Send a message to the queue"""
        try:
            if self.use_sqs and self._sqs_client and self.queue_url:
                # Send to SQS
                message_id = self._sqs_client.send_message(
                    self.queue_url,
                    message.body,
                    message_attributes=message.to_sqs_format()["MessageAttributes"]
                )
                logger.debug(f"Sent message {message.message_id} to SQS queue {self.queue_name}")
                return message_id or message.message_id
            else:
                # Add to local queue (priority based on message priority)
                await self._local_queue.put(
                    (-message.priority.value, message.timestamp, message)
                )
                logger.debug(f"Added message {message.message_id} to local queue {self.queue_name}")
                return message.message_id
                
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    async def receive_messages(self, max_messages: int = 10,
                              wait_time: int = 5) -> List[Message]:
        """Receive messages from the queue"""
        messages = []
        
        try:
            if self.use_sqs and self._sqs_client and self.queue_url:
                # Receive from SQS
                sqs_messages = self._sqs_client.receive_messages(
                    self.queue_url,
                    max_messages=max_messages,
                    wait_time=wait_time
                )
                
                for sqs_msg in sqs_messages:
                    message = Message.from_sqs_message(sqs_msg)
                    message._sqs_receipt_handle = sqs_msg.get("ReceiptHandle")
                    messages.append(message)
            else:
                # Receive from local queue
                deadline = datetime.utcnow() + timedelta(seconds=wait_time)
                
                while len(messages) < max_messages and datetime.utcnow() < deadline:
                    try:
                        remaining_time = (deadline - datetime.utcnow()).total_seconds()
                        if remaining_time <= 0:
                            break
                        
                        priority, timestamp, message = await asyncio.wait_for(
                            self._local_queue.get(),
                            timeout=min(remaining_time, 1.0)
                        )
                        
                        if not message.is_expired():
                            messages.append(message)
                            
                    except asyncio.TimeoutError:
                        break
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to receive messages: {e}")
            return messages
    
    async def delete_message(self, message: Message) -> bool:
        """Delete a message from the queue (acknowledge)"""
        try:
            if self.use_sqs and self._sqs_client and self.queue_url:
                # Delete from SQS
                if hasattr(message, '_sqs_receipt_handle'):
                    return self._sqs_client.delete_message(
                        self.queue_url,
                        message._sqs_receipt_handle
                    )
            
            # For local queue, deletion happens automatically when message is retrieved
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            return False
    
    def register_handler(self, handler_name: str, handler_func: Callable) -> None:
        """Register a message handler"""
        self._handlers[handler_name] = handler_func
        logger.info(f"Registered handler {handler_name} for queue {self.queue_name}")
    
    async def start_processing(self) -> None:
        """Start processing messages"""
        if self._processing:
            logger.warning(f"Queue {self.queue_name} already processing")
            return
        
        self._processing = True
        logger.info(f"Started processing queue {self.queue_name}")
        
        while self._processing:
            try:
                # Receive messages
                messages = await self.receive_messages(max_messages=5, wait_time=5)
                
                if not messages:
                    await asyncio.sleep(1)
                    continue
                
                # Process messages
                for message in messages:
                    await self._process_message(message)
                    
            except Exception as e:
                logger.error(f"Error in message processing loop: {e}")
                await asyncio.sleep(5)
    
    async def stop_processing(self) -> None:
        """Stop processing messages"""
        self._processing = False
        logger.info(f"Stopped processing queue {self.queue_name}")
    
    async def _process_message(self, message: Message) -> None:
        """Process a single message"""
        try:
            # Find and execute handlers
            processed = False
            
            for handler_name, handler_func in self._handlers.items():
                try:
                    result = await handler_func(message)
                    processed = True
                    logger.debug(f"Handler {handler_name} processed message {message.message_id}")
                except Exception as e:
                    logger.error(f"Handler {handler_name} failed: {e}")
            
            if processed:
                # Delete message (acknowledge)
                await self.delete_message(message)
                self._processed_count += 1
            else:
                # No handler processed the message
                logger.warning(f"No handler processed message {message.message_id}")
                
                # Retry or move to dead letter queue
                if message.retry_count < message.max_retries:
                    message.retry_count += 1
                    await self.send_message(message)
                else:
                    await self._move_to_dead_letter(message)
                    
        except Exception as e:
            self._failed_count += 1
            logger.error(f"Failed to process message {message.message_id}: {e}")
            
            # Move to dead letter queue
            await self._move_to_dead_letter(message)
    
    async def _move_to_dead_letter(self, message: Message) -> None:
        """Move message to dead letter queue"""
        # Create dead letter queue message
        dlq_message = Message(
            queue_type=QueueType.DEAD_LETTER,
            priority=MessagePriority.LOW,
            correlation_id=message.correlation_id,
            headers={
                **message.headers,
                "original_queue": self.queue_name,
                "failure_time": datetime.utcnow().isoformat()
            },
            body={
                "original_message": message.body,
                "error": "Processing failed after retries"
            }
        )
        
        # Send to dead letter queue (would need separate DLQ instance)
        logger.warning(f"Moved message {message.message_id} to dead letter queue")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "queue_name": self.queue_name,
            "queue_type": self.queue_type.value,
            "processed_messages": self._processed_count,
            "failed_messages": self._failed_count,
            "handlers_registered": len(self._handlers),
            "local_queue_size": self._local_queue.qsize() if not self.use_sqs else 0
        }


class MessageQueueManager:
    """Manager for multiple message queues"""
    
    def __init__(self, use_sqs: bool = False):
        self.use_sqs = use_sqs
        self._queues: Dict[str, MessageQueue] = {}
        self._default_handlers: Dict[QueueType, List[Callable]] = {}
    
    def create_queue(self, queue_name: str, queue_type: QueueType,
                    queue_url: Optional[str] = None) -> MessageQueue:
        """Create a new message queue"""
        if queue_name in self._queues:
            return self._queues[queue_name]
        
        queue = MessageQueue(
            queue_name=queue_name,
            queue_type=queue_type,
            use_sqs=self.use_sqs,
            queue_url=queue_url
        )
        
        # Register default handlers for this queue type
        if queue_type in self._default_handlers:
            for i, handler in enumerate(self._default_handlers[queue_type]):
                queue.register_handler(f"default_{i}", handler)
        
        self._queues[queue_name] = queue
        logger.info(f"Created queue: {queue_name} ({queue_type.value})")
        
        return queue
    
    def get_queue(self, queue_name: str) -> Optional[MessageQueue]:
        """Get a queue by name"""
        return self._queues.get(queue_name)
    
    def register_default_handler(self, queue_type: QueueType, 
                                handler: Callable) -> None:
        """Register default handler for a queue type"""
        if queue_type not in self._default_handlers:
            self._default_handlers[queue_type] = []
        self._default_handlers[queue_type].append(handler)
    
    async def start_all(self) -> None:
        """Start processing all queues"""
        tasks = []
        for queue in self._queues.values():
            task = asyncio.create_task(queue.start_processing())
            tasks.append(task)
        
        logger.info(f"Started {len(tasks)} queue processors")
    
    async def stop_all(self) -> None:
        """Stop processing all queues"""
        for queue in self._queues.values():
            await queue.stop_processing()
        
        logger.info("Stopped all queue processors")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all queues"""
        return {
            "total_queues": len(self._queues),
            "queue_stats": [
                queue.get_stats() for queue in self._queues.values()
            ]
        }


# Singleton instance
_queue_manager_instance: Optional[MessageQueueManager] = None


def get_queue_manager() -> MessageQueueManager:
    """Get singleton queue manager instance"""
    global _queue_manager_instance
    if _queue_manager_instance is None:
        _queue_manager_instance = MessageQueueManager()
    return _queue_manager_instance


# Export classes and functions
__all__ = [
    'QueueType',
    'MessagePriority',
    'Message',
    'MessageQueue',
    'MessageQueueManager',
    'get_queue_manager'
]