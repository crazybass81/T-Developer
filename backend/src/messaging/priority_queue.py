"""
Priority Message Queue Implementation
Day 8: Message Queue System
Generated: 2024-11-18

Priority-based message queue using Redis sorted sets
"""

import heapq
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import redis.asyncio as redis


class PriorityMessageQueue:
    """Priority-based message queue with multiple priority levels"""

    def __init__(self, queue_name: str, config: Optional[Dict] = None):
        self.queue_name = queue_name
        self.config = config or {"redis_url": "redis://localhost:6379"}
        self._redis_client = None

        # In-memory priority queue for testing without Redis
        self._local_queue = []
        self._use_redis = True

    async def _get_redis_client(self):
        """Get or create Redis client connection"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(self.config["redis_url"], decode_responses=True)
                # Test connection
                await self._redis_client.ping()
            except Exception:
                # Fall back to local queue if Redis not available
                self._use_redis = False
        return self._redis_client

    def add_message(self, message: Dict) -> str:
        """Add message to priority queue (synchronous for testing)"""
        message_id = str(uuid.uuid4())
        priority = message.get("priority", 5)  # Default medium priority

        queue_message = {
            "id": message_id,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": priority,
            **message,
        }

        # For synchronous testing, always use local queue
        heapq.heappush(self._local_queue, (priority, message_id, queue_message))

        return message_id

    def get_next_message(self) -> Optional[Dict]:
        """Get next highest priority message (synchronous for testing)"""
        # For synchronous testing, always use local queue
        if self._local_queue:
            priority, message_id, message = heapq.heappop(self._local_queue)
            return message

        return None

    async def enqueue_with_priority(self, message: Dict, priority: int = 5) -> str:
        """Add message to priority queue with specific priority"""
        message_id = str(uuid.uuid4())

        queue_message = {
            "id": message_id,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": priority,
            **message,
        }

        if self._use_redis:
            redis_client = await self._get_redis_client()

            # Use sorted set with priority as score (lower score = higher priority)
            await redis_client.zadd(self.queue_name, {json.dumps(queue_message): priority})
        else:
            # Local queue fallback
            heapq.heappush(self._local_queue, (priority, message_id, queue_message))

        return message_id

    async def dequeue_highest_priority(self) -> Optional[Dict]:
        """Remove and return highest priority message"""
        if self._use_redis:
            redis_client = await self._get_redis_client()

            # Get lowest score (highest priority) with ZPOPMIN
            result = await redis_client.zpopmin(self.queue_name, count=1)

            if result:
                serialized_message, priority = result[0]
                return json.loads(serialized_message)
        else:
            # Local queue fallback
            if self._local_queue:
                priority, message_id, message = heapq.heappop(self._local_queue)
                return message

        return None

    async def peek_by_priority(self, priority: int) -> List[Dict]:
        """Look at messages of specific priority without removing"""
        if self._use_redis:
            redis_client = await self._get_redis_client()

            # Get messages with specific priority score
            serialized_messages = await redis_client.zrangebyscore(
                self.queue_name, priority, priority
            )

            return [json.loads(msg) for msg in serialized_messages]
        else:
            # Local queue - filter by priority
            return [msg for prio, msg_id, msg in self._local_queue if prio == priority]

    async def get_priority_distribution(self) -> Dict[int, int]:
        """Get count of messages by priority level"""
        if self._use_redis:
            redis_client = await self._get_redis_client()

            # Get all messages with scores
            messages_with_scores = await redis_client.zrange(
                self.queue_name, 0, -1, withscores=True
            )

            distribution = {}
            for _, priority in messages_with_scores:
                priority = int(priority)
                distribution[priority] = distribution.get(priority, 0) + 1

            return distribution
        else:
            # Local queue distribution
            distribution = {}
            for priority, _, _ in self._local_queue:
                distribution[priority] = distribution.get(priority, 0) + 1
            return distribution

    async def size(self) -> int:
        """Get total number of messages in queue"""
        if self._use_redis:
            redis_client = await self._get_redis_client()
            return await redis_client.zcard(self.queue_name)
        else:
            return len(self._local_queue)

    async def clear_priority(self, priority: int):
        """Remove all messages of specific priority"""
        if self._use_redis:
            redis_client = await self._get_redis_client()
            await redis_client.zremrangebyscore(self.queue_name, priority, priority)
        else:
            # Local queue - remove messages with specific priority
            self._local_queue = [
                (prio, msg_id, msg) for prio, msg_id, msg in self._local_queue if prio != priority
            ]
            heapq.heapify(self._local_queue)


class AdaptivePriorityQueue(PriorityMessageQueue):
    """Priority queue that adapts priorities based on processing patterns"""

    def __init__(self, queue_name: str, config: Optional[Dict] = None):
        super().__init__(queue_name, config)
        self.priority_adjustments = {}
        self.processing_history = []

    async def enqueue_with_adaptive_priority(self, message: Dict) -> str:
        """Add message with priority adjusted based on historical performance"""
        base_priority = message.get("priority", 5)
        message_type = message.get("type", "unknown")

        # Adjust priority based on historical performance
        adjustment = self.priority_adjustments.get(message_type, 0)
        adjusted_priority = max(1, min(10, base_priority + adjustment))

        message["original_priority"] = base_priority
        message["adjusted_priority"] = adjusted_priority

        return await self.enqueue_with_priority(message, adjusted_priority)

    def record_processing_result(self, message: Dict, processing_time_ms: float, success: bool):
        """Record processing result to adjust future priorities"""
        message_type = message.get("type", "unknown")

        self.processing_history.append(
            {
                "message_type": message_type,
                "processing_time_ms": processing_time_ms,
                "success": success,
                "timestamp": datetime.utcnow(),
            }
        )

        # Update priority adjustments based on performance
        self._update_priority_adjustments()

    def _update_priority_adjustments(self):
        """Update priority adjustments based on processing history"""
        # Group by message type
        type_stats = {}

        for record in self.processing_history[-100:]:  # Last 100 records
            msg_type = record["message_type"]
            if msg_type not in type_stats:
                type_stats[msg_type] = {"total_time": 0, "success_count": 0, "total_count": 0}

            type_stats[msg_type]["total_time"] += record["processing_time_ms"]
            type_stats[msg_type]["total_count"] += 1
            if record["success"]:
                type_stats[msg_type]["success_count"] += 1

        # Calculate adjustments
        for msg_type, stats in type_stats.items():
            if stats["total_count"] > 0:
                avg_time = stats["total_time"] / stats["total_count"]
                success_rate = stats["success_count"] / stats["total_count"]

                # Adjust priority based on performance
                # Faster processing and higher success rate = higher priority (lower number)
                if avg_time < 100 and success_rate > 0.9:  # Fast and reliable
                    self.priority_adjustments[msg_type] = -1  # Increase priority
                elif avg_time > 1000 or success_rate < 0.5:  # Slow or unreliable
                    self.priority_adjustments[msg_type] = 1  # Decrease priority
                else:
                    self.priority_adjustments[msg_type] = 0  # No adjustment


class CircuitBreakerPriorityQueue(PriorityMessageQueue):
    """Priority queue with circuit breaker pattern for failing message types"""

    def __init__(self, queue_name: str, config: Optional[Dict] = None):
        super().__init__(queue_name, config)
        self.circuit_breakers = {}  # message_type -> circuit breaker state

    async def enqueue_with_circuit_breaker(self, message: Dict) -> str:
        """Add message to queue, checking circuit breaker state"""
        msg_type = message.get("type", "unknown")

        # Check circuit breaker state
        if self._is_circuit_open(msg_type):
            # Circuit is open, reject message or send to alternate queue
            message["circuit_breaker_status"] = "rejected"
            return await self._handle_circuit_open(message)

        # Circuit is closed or half-open, allow message
        return await self.enqueue_with_priority(message)

    def _is_circuit_open(self, message_type: str) -> bool:
        """Check if circuit breaker is open for message type"""
        circuit = self.circuit_breakers.get(message_type)
        if not circuit:
            return False

        return circuit.get("state") == "open"

    async def _handle_circuit_open(self, message: Dict) -> str:
        """Handle message when circuit breaker is open"""
        # For now, send to alternate queue with lower priority
        alternate_priority = 8  # Lower priority
        message["circuit_breaker_alternate"] = True

        return await self.enqueue_with_priority(message, alternate_priority)

    def record_circuit_breaker_event(self, message_type: str, success: bool):
        """Record success/failure for circuit breaker logic"""
        if message_type not in self.circuit_breakers:
            self.circuit_breakers[message_type] = {
                "state": "closed",
                "failure_count": 0,
                "success_count": 0,
                "last_failure_time": None,
                "failure_threshold": 5,
                "recovery_timeout": 60,  # seconds
            }

        circuit = self.circuit_breakers[message_type]

        if success:
            circuit["success_count"] += 1
            circuit["failure_count"] = 0  # Reset failure count on success

            # If in half-open state and success, close circuit
            if circuit["state"] == "half_open":
                circuit["state"] = "closed"
        else:
            circuit["failure_count"] += 1
            circuit["last_failure_time"] = datetime.utcnow()

            # Open circuit if failure threshold exceeded
            if circuit["failure_count"] >= circuit["failure_threshold"]:
                circuit["state"] = "open"

    def _check_circuit_recovery(self, message_type: str):
        """Check if circuit should transition to half-open state"""
        circuit = self.circuit_breakers.get(message_type)
        if not circuit or circuit["state"] != "open":
            return

        # Check if recovery timeout has passed
        if circuit["last_failure_time"]:
            time_since_failure = (datetime.utcnow() - circuit["last_failure_time"]).total_seconds()
            if time_since_failure >= circuit["recovery_timeout"]:
                circuit["state"] = "half_open"
                circuit["failure_count"] = 0


class PriorityQueueMonitor:
    """Monitor priority queue performance and health"""

    def __init__(self, queue: PriorityMessageQueue):
        self.queue = queue
        self.metrics = {
            "messages_by_priority": {},
            "processing_times_by_priority": {},
            "priority_changes": [],
            "circuit_breaker_events": [],
        }

    async def collect_metrics(self) -> Dict:
        """Collect current queue metrics"""
        priority_distribution = await self.queue.get_priority_distribution()
        queue_size = await self.queue.size()

        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_size": queue_size,
            "priority_distribution": priority_distribution,
            "priority_levels": len(priority_distribution),
            "highest_priority_count": priority_distribution.get(1, 0),
            "lowest_priority_count": priority_distribution.get(10, 0),
        }

        return metrics

    def analyze_priority_patterns(self) -> Dict:
        """Analyze patterns in priority queue usage"""
        if not self.metrics["priority_changes"]:
            return {"status": "insufficient_data"}

        analysis = {
            "priority_volatility": self._calculate_priority_volatility(),
            "most_common_priority": self._find_most_common_priority(),
            "priority_trend": self._analyze_priority_trend(),
            "recommendations": self._generate_recommendations(),
        }

        return analysis

    def _calculate_priority_volatility(self) -> float:
        """Calculate how much priorities change over time"""
        if len(self.metrics["priority_changes"]) < 2:
            return 0.0

        changes = [
            abs(a - b)
            for a, b in zip(
                self.metrics["priority_changes"][:-1], self.metrics["priority_changes"][1:]
            )
        ]

        return sum(changes) / len(changes)

    def _find_most_common_priority(self) -> int:
        """Find the most commonly used priority level"""
        priority_counts = {}
        for priority in self.metrics["priority_changes"]:
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        if priority_counts:
            return max(priority_counts.keys(), key=lambda k: priority_counts[k])
        return 5  # Default

    def _analyze_priority_trend(self) -> str:
        """Analyze trend in priority usage"""
        if len(self.metrics["priority_changes"]) < 5:
            return "insufficient_data"

        recent = self.metrics["priority_changes"][-5:]
        trend = sum(recent) / len(recent)

        if trend < 3:
            return "trending_high_priority"
        elif trend > 7:
            return "trending_low_priority"
        else:
            return "stable"

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for queue optimization"""
        recommendations = []

        # Check for common patterns and suggest optimizations
        if self._calculate_priority_volatility() > 2:
            recommendations.append(
                "Consider reviewing priority assignment logic - high volatility detected"
            )

        most_common = self._find_most_common_priority()
        if most_common in [1, 10]:  # Extreme priorities
            recommendations.append(
                f"Most messages use extreme priority {most_common} - consider more balanced distribution"
            )

        return recommendations
