"""
Core Message Queue Implementation
Day 8: Message Queue System
Generated: 2024-11-18

Redis-based message queue with reliability and retry mechanisms
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import redis.asyncio as redis


class MessageQueue:
    """Core message queue with Redis backend"""

    def __init__(self, queue_name: str, config: Optional[Dict] = None):
        self.queue_name = queue_name
        self.config = config or {
            "redis_url": "redis://localhost:6379",
            "max_retries": 3,
            "retry_delay": 1.0,
            "enable_persistence": True,
            "timeout": 30,
        }
        self._redis_client = None

    async def _get_redis_client(self):
        """Get or create Redis client connection"""
        if self._redis_client is None:
            self._redis_client = redis.from_url(self.config["redis_url"], decode_responses=True)
        return self._redis_client

    async def enqueue(self, message: Dict) -> str:
        """Add message to queue with unique ID"""
        # Generate unique message ID
        message_id = str(uuid.uuid4())

        # Prepare message with metadata
        queue_message = {
            "id": message_id,
            "timestamp": datetime.utcnow().isoformat(),
            "retry_count": 0,
            "priority": message.get("priority", 5),  # Default medium priority
            **message,
        }

        # Serialize message
        serialized_message = json.dumps(queue_message)

        # Add to Redis queue (left push for FIFO with right pop)
        redis_client = await self._get_redis_client()
        await redis_client.lpush(self.queue_name, serialized_message)

        # Optionally persist to database for reliability
        if self.config.get("enable_persistence"):
            await self._persist_message(queue_message)

        return message_id

    async def dequeue(self, timeout: Optional[int] = None) -> Optional[Dict]:
        """Remove and return message from queue"""
        timeout = timeout or self.config.get("timeout", 30)

        redis_client = await self._get_redis_client()

        # Blocking right pop (FIFO)
        result = await redis_client.brpop(self.queue_name, timeout=timeout)

        if result is None:
            return None

        queue_name, serialized_message = result
        message = json.loads(serialized_message)

        return message

    async def peek(self, count: int = 1) -> List[Dict]:
        """Look at messages without removing them"""
        redis_client = await self._get_redis_client()

        # Get messages from right (next to be processed)
        serialized_messages = await redis_client.lrange(self.queue_name, -count, -1)

        messages = []
        for serialized_msg in serialized_messages:
            messages.append(json.loads(serialized_msg))

        return messages

    async def size(self) -> int:
        """Get current queue size"""
        redis_client = await self._get_redis_client()
        return await redis_client.llen(self.queue_name)

    async def handle_message_with_retry(self, message: Dict) -> Dict:
        """Process message with retry logic"""
        max_retries = self.config.get("max_retries", 3)
        retry_delay = self.config.get("retry_delay", 1.0)

        for attempt in range(max_retries):
            try:
                # Attempt to process message
                result = await self._process_message(message)
                return {"status": "success", "result": result, "retry_count": attempt}

            except Exception as e:
                message["retry_count"] = attempt + 1
                message["last_error"] = str(e)
                message["last_attempt"] = datetime.utcnow().isoformat()

                if attempt < max_retries - 1:
                    # Wait before retry
                    await asyncio.sleep(retry_delay * (2**attempt))  # Exponential backoff
                else:
                    # Max retries exceeded, move to dead letter queue
                    await self._move_to_dead_letter_queue(message)

        return {
            "status": "failed",
            "retry_count": max_retries,
            "final_error": message.get("last_error"),
        }

    async def _process_message(self, message: Dict) -> Dict:
        """Process individual message (override in subclasses)"""
        # Default implementation - just simulate processing
        await asyncio.sleep(0.01)

        # Simulate occasional failures for testing
        if "test_failure" in message.get("payload", {}):
            raise Exception("Simulated processing failure")

        return {"processed": True, "message_id": message.get("id")}

    async def _persist_message(self, message: Dict):
        """Persist message to database for reliability"""
        # In production, this would write to PostgreSQL/DynamoDB
        # For now, just log the persistence
        pass

    async def _move_to_dead_letter_queue(self, message: Dict):
        """Move failed message to dead letter queue"""
        from .dead_letter_queue import DeadLetterQueue

        dlq = DeadLetterQueue(f"{self.queue_name}_dlq")

        failed_message = {
            **message,
            "failed_at": datetime.utcnow().isoformat(),
            "failure_reason": message.get("last_error", "Unknown error"),
            "original_queue": self.queue_name,
        }

        dlq.add_failed_message(failed_message)

    async def clear(self):
        """Clear all messages from queue"""
        redis_client = await self._get_redis_client()
        await redis_client.delete(self.queue_name)

    async def close(self):
        """Close Redis connection"""
        if self._redis_client:
            await self._redis_client.close()


class BatchMessageQueue(MessageQueue):
    """Message queue optimized for batch processing"""

    def __init__(self, queue_name: str, batch_size: int = 10, config: Optional[Dict] = None):
        super().__init__(queue_name, config)
        self.batch_size = batch_size

    async def enqueue_batch(self, messages: List[Dict]) -> List[str]:
        """Add multiple messages to queue efficiently"""
        message_ids = []
        serialized_messages = []

        for message in messages:
            message_id = str(uuid.uuid4())
            message_ids.append(message_id)

            queue_message = {
                "id": message_id,
                "timestamp": datetime.utcnow().isoformat(),
                "retry_count": 0,
                "priority": message.get("priority", 5),
                **message,
            }

            serialized_messages.append(json.dumps(queue_message))

        # Batch insert to Redis
        redis_client = await self._get_redis_client()
        if serialized_messages:
            await redis_client.lpush(self.queue_name, *serialized_messages)

        return message_ids

    async def dequeue_batch(self, count: Optional[int] = None) -> List[Dict]:
        """Remove and return multiple messages from queue"""
        count = count or self.batch_size

        redis_client = await self._get_redis_client()

        # Use pipeline for efficiency
        pipe = redis_client.pipeline()
        for _ in range(count):
            pipe.rpop(self.queue_name)

        results = await pipe.execute()

        messages = []
        for serialized_message in results:
            if serialized_message:
                messages.append(json.loads(serialized_message))

        return messages


class DelayedMessageQueue(MessageQueue):
    """Message queue that supports delayed message delivery"""

    def __init__(self, queue_name: str, config: Optional[Dict] = None):
        super().__init__(queue_name, config)
        self.delayed_queue_name = f"{queue_name}_delayed"

    async def enqueue_delayed(self, message: Dict, delay_seconds: int) -> str:
        """Add message to queue with delay"""
        message_id = str(uuid.uuid4())

        # Calculate delivery time
        delivery_time = datetime.utcnow().timestamp() + delay_seconds

        delayed_message = {
            "id": message_id,
            "delivery_time": delivery_time,
            "original_message": message,
        }

        # Add to delayed queue (sorted set by delivery time)
        redis_client = await self._get_redis_client()
        await redis_client.zadd(
            self.delayed_queue_name, {json.dumps(delayed_message): delivery_time}
        )

        return message_id

    async def process_delayed_messages(self):
        """Process messages that are ready for delivery"""
        current_time = datetime.utcnow().timestamp()

        redis_client = await self._get_redis_client()

        # Get messages ready for delivery
        ready_messages = await redis_client.zrangebyscore(
            self.delayed_queue_name, 0, current_time, withscores=True
        )

        for serialized_message, delivery_time in ready_messages:
            delayed_message = json.loads(serialized_message)
            original_message = delayed_message["original_message"]

            # Move to main queue
            await self.enqueue(original_message)

            # Remove from delayed queue
            await redis_client.zrem(self.delayed_queue_name, serialized_message)

    async def start_delayed_processor(self, check_interval: int = 5):
        """Start background task to process delayed messages"""
        while True:
            try:
                await self.process_delayed_messages()
                await asyncio.sleep(check_interval)
            except Exception as e:
                # Log error and continue
                print(f"Error processing delayed messages: {e}")
                await asyncio.sleep(check_interval)


class MessageQueueMetrics:
    """Track metrics for message queue performance"""

    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.metrics = {
            "messages_enqueued": 0,
            "messages_dequeued": 0,
            "messages_failed": 0,
            "processing_times": [],
            "queue_sizes": [],
            "start_time": datetime.utcnow(),
        }

    def record_enqueue(self):
        """Record message enqueue event"""
        self.metrics["messages_enqueued"] += 1

    def record_dequeue(self, processing_time_ms: float):
        """Record message dequeue and processing time"""
        self.metrics["messages_dequeued"] += 1
        self.metrics["processing_times"].append(processing_time_ms)

    def record_failure(self):
        """Record message processing failure"""
        self.metrics["messages_failed"] += 1

    def record_queue_size(self, size: int):
        """Record current queue size"""
        self.metrics["queue_sizes"].append({"size": size, "timestamp": datetime.utcnow()})

    def get_metrics_summary(self) -> Dict:
        """Get comprehensive metrics summary"""
        processing_times = self.metrics["processing_times"]

        summary = {
            "queue_name": self.queue_name,
            "messages_enqueued": self.metrics["messages_enqueued"],
            "messages_dequeued": self.metrics["messages_dequeued"],
            "messages_failed": self.metrics["messages_failed"],
            "success_rate": self._calculate_success_rate(),
            "average_processing_time_ms": sum(processing_times) / len(processing_times)
            if processing_times
            else 0,
            "max_processing_time_ms": max(processing_times) if processing_times else 0,
            "current_queue_size": self.metrics["queue_sizes"][-1]["size"]
            if self.metrics["queue_sizes"]
            else 0,
            "uptime_seconds": (datetime.utcnow() - self.metrics["start_time"]).total_seconds(),
        }

        return summary

    def _calculate_success_rate(self) -> float:
        """Calculate message processing success rate"""
        total_processed = self.metrics["messages_dequeued"] + self.metrics["messages_failed"]
        if total_processed == 0:
            return 1.0

        return self.metrics["messages_dequeued"] / total_processed
