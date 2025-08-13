"""
Dead Letter Queue Implementation
Day 8: Message Queue System
Generated: 2024-11-18

Handle failed messages with retry and recovery mechanisms
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import redis.asyncio as redis


class DeadLetterQueue:
    """Dead letter queue for handling failed messages"""

    def __init__(self, queue_name: str, config: Optional[Dict] = None):
        self.queue_name = queue_name
        self.config = config or {
            "redis_url": "redis://localhost:6379",
            "max_retention_days": 7,
            "auto_requeue_threshold": 24,  # hours
            "enable_analytics": True,
        }
        self._redis_client = None
        self._local_storage = []  # Fallback for testing

    async def _get_redis_client(self):
        """Get or create Redis client connection"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(self.config["redis_url"], decode_responses=True)
            except Exception:
                # Use local storage as fallback
                pass
        return self._redis_client

    def add_failed_message(self, message: Dict) -> str:
        """Add failed message to dead letter queue"""
        dlq_entry = {
            "id": message.get("id", str(uuid.uuid4())),
            "original_message": message,
            "failed_at": datetime.utcnow().isoformat(),
            "failure_reason": message.get("failure_reason", "Unknown error"),
            "retry_count": message.get("retry_count", 0),
            "original_queue": message.get("original_queue", "unknown"),
            "dlq_entry_id": str(uuid.uuid4()),
        }

        # Store locally for testing
        self._local_storage.append(dlq_entry)

        return dlq_entry["dlq_entry_id"]

    async def add_failed_message_async(self, message: Dict) -> str:
        """Asynchronously add failed message to DLQ"""
        dlq_entry = {
            "id": message.get("id", str(uuid.uuid4())),
            "original_message": message,
            "failed_at": datetime.utcnow().isoformat(),
            "failure_reason": message.get("failure_reason", "Unknown error"),
            "retry_count": message.get("retry_count", 0),
            "original_queue": message.get("original_queue", "unknown"),
            "dlq_entry_id": str(uuid.uuid4()),
        }

        redis_client = await self._get_redis_client()
        if redis_client:
            # Store in Redis with expiration
            retention_seconds = self.config["max_retention_days"] * 24 * 3600
            await redis_client.setex(
                f"{self.queue_name}:{dlq_entry['dlq_entry_id']}",
                retention_seconds,
                json.dumps(dlq_entry),
            )

            # Add to index for querying
            await redis_client.zadd(
                f"{self.queue_name}_index",
                {dlq_entry["dlq_entry_id"]: datetime.utcnow().timestamp()},
            )
        else:
            # Fallback to local storage
            self._local_storage.append(dlq_entry)

        return dlq_entry["dlq_entry_id"]

    def get_failed_messages(self, limit: int = 100) -> List[Dict]:
        """Get failed messages from DLQ"""
        return self._local_storage[:limit]

    async def get_failed_messages_async(self, limit: int = 100) -> List[Dict]:
        """Asynchronously get failed messages from DLQ"""
        redis_client = await self._get_redis_client()
        if redis_client:
            # Get message IDs from index (most recent first)
            message_ids = await redis_client.zrevrange(f"{self.queue_name}_index", 0, limit - 1)

            # Fetch actual messages
            messages = []
            for msg_id in message_ids:
                serialized_msg = await redis_client.get(f"{self.queue_name}:{msg_id}")
                if serialized_msg:
                    messages.append(json.loads(serialized_msg))

            return messages
        else:
            # Fallback to local storage
            return self._local_storage[:limit]

    def requeue_message(self, dlq_entry_id: str) -> Optional[Dict]:
        """Requeue failed message for retry"""
        # Find message in local storage
        for i, entry in enumerate(self._local_storage):
            if entry["dlq_entry_id"] == dlq_entry_id:
                # Reset for requeue
                original_message = entry["original_message"].copy()
                original_message["retry_count"] = 0
                original_message["requeued_at"] = datetime.utcnow().isoformat()
                original_message["requeued_from_dlq"] = True

                # Remove from DLQ
                self._local_storage.pop(i)

                return original_message

        # Try to find by id field instead
        for i, entry in enumerate(self._local_storage):
            if entry["id"] == dlq_entry_id:
                # Reset for requeue
                original_message = entry["original_message"].copy()
                original_message["retry_count"] = 0
                original_message["requeued_at"] = datetime.utcnow().isoformat()
                original_message["requeued_from_dlq"] = True

                # Remove from DLQ
                self._local_storage.pop(i)

                return original_message

        return None

    async def requeue_message_async(self, dlq_entry_id: str) -> Optional[Dict]:
        """Asynchronously requeue failed message"""
        redis_client = await self._get_redis_client()
        if redis_client:
            # Get message from Redis
            serialized_msg = await redis_client.get(f"{self.queue_name}:{dlq_entry_id}")
            if serialized_msg:
                entry = json.loads(serialized_msg)

                # Prepare for requeue
                original_message = entry["original_message"].copy()
                original_message["retry_count"] = 0
                original_message["requeued_at"] = datetime.utcnow().isoformat()
                original_message["requeued_from_dlq"] = True

                # Remove from DLQ
                await redis_client.delete(f"{self.queue_name}:{dlq_entry_id}")
                await redis_client.zrem(f"{self.queue_name}_index", dlq_entry_id)

                return original_message
        else:
            # Fallback to local method
            return self.requeue_message(dlq_entry_id)

        return None

    async def analyze_failure_patterns(self) -> Dict:
        """Analyze patterns in failed messages"""
        messages = await self.get_failed_messages_async(1000)  # Analyze last 1000

        if not messages:
            return {"status": "no_data"}

        # Group by failure reason
        failure_reasons = {}
        failure_by_queue = {}
        failure_by_hour = {}

        for msg in messages:
            # Failure reasons
            reason = msg.get("failure_reason", "unknown")
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

            # Original queue
            orig_queue = msg.get("original_queue", "unknown")
            failure_by_queue[orig_queue] = failure_by_queue.get(orig_queue, 0) + 1

            # Failure time patterns
            failed_at = datetime.fromisoformat(msg["failed_at"])
            hour = failed_at.hour
            failure_by_hour[hour] = failure_by_hour.get(hour, 0) + 1

        analysis = {
            "total_failures": len(messages),
            "most_common_reason": max(failure_reasons.keys(), key=lambda k: failure_reasons[k]),
            "failure_reasons": failure_reasons,
            "failure_by_queue": failure_by_queue,
            "peak_failure_hour": max(failure_by_hour.keys(), key=lambda k: failure_by_hour[k]),
            "recommendations": self._generate_failure_recommendations(
                failure_reasons, failure_by_queue, failure_by_hour
            ),
        }

        return analysis

    def _generate_failure_recommendations(
        self, reasons: Dict, queues: Dict, hours: Dict
    ) -> List[str]:
        """Generate recommendations based on failure analysis"""
        recommendations = []

        # Check for dominant failure reasons
        total_failures = sum(reasons.values())
        for reason, count in reasons.items():
            if count / total_failures > 0.5:
                recommendations.append(
                    f"High frequency of '{reason}' failures - investigate root cause"
                )

        # Check for problematic queues
        total_queue_failures = sum(queues.values())
        for queue, count in queues.items():
            if count / total_queue_failures > 0.7:
                recommendations.append(
                    f"Queue '{queue}' has high failure rate - review message processing"
                )

        # Check for time-based patterns
        max_hour_failures = max(hours.values())
        if max_hour_failures > total_failures * 0.3:
            peak_hour = max(hours.keys(), key=lambda k: hours[k])
            recommendations.append(
                f"Failure spike at hour {peak_hour} - check system load patterns"
            )

        return recommendations

    async def auto_requeue_eligible_messages(self) -> int:
        """Automatically requeue messages that meet retry criteria"""
        threshold_hours = self.config.get("auto_requeue_threshold", 24)
        threshold_time = datetime.utcnow() - timedelta(hours=threshold_hours)

        messages = await self.get_failed_messages_async()
        requeued_count = 0

        for msg in messages:
            failed_at = datetime.fromisoformat(msg["failed_at"])

            # Check if message is eligible for auto-requeue
            if (
                failed_at < threshold_time
                and msg.get("retry_count", 0) < 2
                and not msg.get("permanent_failure", False)  # Max 2 auto-retries
            ):
                requeued_msg = await self.requeue_message_async(msg["dlq_entry_id"])
                if requeued_msg:
                    requeued_count += 1

                    # Re-enqueue to original queue
                    from .message_queue import MessageQueue

                    original_queue = MessageQueue(msg.get("original_queue", "default"))
                    await original_queue.enqueue(requeued_msg)

        return requeued_count

    async def cleanup_expired_messages(self) -> int:
        """Clean up messages that have exceeded retention period"""
        retention_days = self.config.get("max_retention_days", 7)
        cutoff_time = datetime.utcnow() - timedelta(days=retention_days)

        redis_client = await self._get_redis_client()
        if redis_client:
            # Get all message IDs older than cutoff
            old_message_ids = await redis_client.zrangebyscore(
                f"{self.queue_name}_index", 0, cutoff_time.timestamp()
            )

            # Remove expired messages
            cleanup_count = 0
            for msg_id in old_message_ids:
                await redis_client.delete(f"{self.queue_name}:{msg_id}")
                await redis_client.zrem(f"{self.queue_name}_index", msg_id)
                cleanup_count += 1

            return cleanup_count
        else:
            # Local cleanup
            initial_count = len(self._local_storage)
            self._local_storage = [
                msg
                for msg in self._local_storage
                if datetime.fromisoformat(msg["failed_at"]) > cutoff_time
            ]
            return initial_count - len(self._local_storage)

    async def get_dlq_statistics(self) -> Dict:
        """Get comprehensive DLQ statistics"""
        messages = await self.get_failed_messages_async()

        if not messages:
            return {"status": "empty", "message_count": 0}

        # Calculate statistics
        total_messages = len(messages)
        retry_counts = [msg.get("retry_count", 0) for msg in messages]

        # Age analysis
        current_time = datetime.utcnow()
        ages_hours = []
        for msg in messages:
            failed_at = datetime.fromisoformat(msg["failed_at"])
            age_hours = (current_time - failed_at).total_seconds() / 3600
            ages_hours.append(age_hours)

        stats = {
            "total_messages": total_messages,
            "average_retry_count": sum(retry_counts) / len(retry_counts),
            "max_retry_count": max(retry_counts),
            "average_age_hours": sum(ages_hours) / len(ages_hours),
            "oldest_message_hours": max(ages_hours),
            "messages_eligible_for_requeue": sum(
                1 for age in ages_hours if age >= self.config.get("auto_requeue_threshold", 24)
            ),
            "size_mb": len(json.dumps(messages)) / (1024 * 1024),
        }

        return stats
