"""
Event Bus Implementation
Day 8: Message Queue System
Generated: 2024-11-18

Event publishing and subscription system with pattern matching
"""

import fnmatch
import json
import uuid
from datetime import datetime
from typing import Callable, Dict, List, Optional

import redis.asyncio as redis


class EventBus:
    """Event bus for publish/subscribe patterns"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {"redis_url": "redis://localhost:6379"}
        self._redis_client = None
        self._subscribers = {}  # pattern -> [handlers]
        self._local_mode = False

    async def _get_redis_client(self):
        """Get or create Redis client connection"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(self.config["redis_url"], decode_responses=True)
                await self._redis_client.ping()
            except Exception:
                self._local_mode = True
        return self._redis_client

    def subscribe(self, pattern: str, handler: Callable[[Dict], None]):
        """Subscribe to events matching pattern"""
        if pattern not in self._subscribers:
            self._subscribers[pattern] = []
        self._subscribers[pattern].append(handler)

    def unsubscribe(self, pattern: str, handler: Callable[[Dict], None]):
        """Unsubscribe from events"""
        if pattern in self._subscribers:
            if handler in self._subscribers[pattern]:
                self._subscribers[pattern].remove(handler)
            if not self._subscribers[pattern]:
                del self._subscribers[pattern]

    def publish(self, event_type: str, event_data: Dict):
        """Publish event to all matching subscribers"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **event_data,  # Merge event data at top level
        }

        # Find matching subscribers
        for pattern, handlers in self._subscribers.items():
            if self._pattern_matches(pattern, event_type):
                for handler in handlers:
                    try:
                        handler(event)
                    except Exception as e:
                        # Log error but continue with other handlers
                        print(f"Error in event handler: {e}")

    async def publish_async(self, event_type: str, event_data: Dict):
        """Publish event asynchronously via Redis"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **event_data,  # Merge event data at top level
        }

        if not self._local_mode:
            redis_client = await self._get_redis_client()
            if redis_client:
                # Publish to Redis channel
                await redis_client.publish(f"events:{event_type}", json.dumps(event))

        # Also handle local subscribers
        self.publish(event_type, event_data)

    def _pattern_matches(self, pattern: str, event_type: str) -> bool:
        """Check if event type matches subscription pattern"""
        return fnmatch.fnmatch(event_type, pattern)

    async def start_redis_listener(self):
        """Start listening for Redis pub/sub events"""
        if self._local_mode:
            return

        redis_client = await self._get_redis_client()
        if not redis_client:
            return

        pubsub = redis_client.pubsub()

        # Subscribe to all event channels
        await pubsub.psubscribe("events:*")

        try:
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    try:
                        event = json.loads(message["data"])
                        event_type = event["event_type"]

                        # Find matching local subscribers
                        for pattern, handlers in self._subscribers.items():
                            if self._pattern_matches(pattern, event_type):
                                for handler in handlers:
                                    try:
                                        handler(event)
                                    except Exception as e:
                                        print(f"Error in Redis event handler: {e}")
                    except Exception as e:
                        print(f"Error processing Redis message: {e}")
        except Exception as e:
            print(f"Redis listener error: {e}")
        finally:
            await pubsub.unsubscribe()
            await pubsub.close()


class EventFilter:
    """Event filtering and routing system"""

    def __init__(self):
        self.rules = []

    def add_rule(self, rule: Dict):
        """Add filtering rule"""
        required_fields = ["name", "condition", "action"]
        if not all(field in rule for field in required_fields):
            raise ValueError(f"Rule must contain: {required_fields}")

        self.rules.append(rule)

    def remove_rule(self, rule_name: str):
        """Remove filtering rule by name"""
        self.rules = [rule for rule in self.rules if rule["name"] != rule_name]

    def apply_filters(self, event: Dict) -> List[Dict]:
        """Apply all filters to event and return matches"""
        matches = []

        for rule in self.rules:
            try:
                if rule["condition"](event):
                    matches.append({"rule": rule["name"], "action": rule["action"], "event": event})
            except Exception as e:
                print(f"Error applying filter rule {rule['name']}: {e}")

        return matches

    def get_statistics(self) -> Dict:
        """Get filter usage statistics"""
        return {
            "total_rules": len(self.rules),
            "rule_names": [rule["name"] for rule in self.rules],
            "actions": list(set(rule["action"] for rule in self.rules)),
        }


class EventStream:
    """Redis stream-based event processing"""

    def __init__(self, stream_name: str, config: Optional[Dict] = None):
        self.stream_name = stream_name
        self.config = config or {"redis_url": "redis://localhost:6379"}
        self._redis_client = None

    async def _get_redis_client(self):
        """Get or create Redis client connection"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(self.config["redis_url"], decode_responses=True)
            except Exception:
                pass
        return self._redis_client

    async def add_event(self, event_data: Dict) -> str:
        """Add event to stream"""
        redis_client = await self._get_redis_client()
        if redis_client:
            # Flatten event data for Redis stream
            stream_data = {}
            for key, value in event_data.items():
                if isinstance(value, (dict, list)):
                    stream_data[key] = json.dumps(value)
                else:
                    stream_data[key] = str(value)

            event_id = await redis_client.xadd(self.stream_name, stream_data)
            return event_id

        return str(uuid.uuid4())

    async def read_events(self, count: int = 10, block: Optional[int] = None) -> List[Dict]:
        """Read events from stream"""
        redis_client = await self._get_redis_client()
        if redis_client:
            if block:
                # Blocking read for real-time processing
                events = await redis_client.xread({self.stream_name: "$"}, count=count, block=block)
            else:
                # Non-blocking read
                events = await redis_client.xread({self.stream_name: "0"}, count=count)

            processed_events = []
            for stream_name, stream_events in events.items():
                for event_id, event_data in stream_events:
                    # Reconstruct event data
                    processed_event = {"stream": stream_name, "event_id": event_id, "data": {}}

                    for key, value in event_data.items():
                        try:
                            # Try to parse JSON values
                            processed_event["data"][key] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            processed_event["data"][key] = value

                    processed_events.append(processed_event)

            return processed_events

        return []

    async def create_consumer_group(self, group_name: str, consumer_name: str):
        """Create consumer group for distributed processing"""
        redis_client = await self._get_redis_client()
        if redis_client:
            try:
                await redis_client.xgroup_create(
                    self.stream_name, group_name, id="0", mkstream=True
                )
            except Exception:
                # Group might already exist
                pass

    async def read_as_consumer(
        self, group_name: str, consumer_name: str, count: int = 10
    ) -> List[Dict]:
        """Read events as part of consumer group"""
        redis_client = await self._get_redis_client()
        if redis_client:
            events = await redis_client.xreadgroup(
                group_name, consumer_name, {self.stream_name: ">"}, count=count
            )

            processed_events = []
            for stream_name, stream_events in events.items():
                for event_id, event_data in stream_events:
                    processed_event = {
                        "stream": stream_name,
                        "event_id": event_id,
                        "group": group_name,
                        "consumer": consumer_name,
                        "data": event_data,
                    }
                    processed_events.append(processed_event)

            return processed_events

        return []

    async def acknowledge_event(self, group_name: str, event_id: str):
        """Acknowledge processed event"""
        redis_client = await self._get_redis_client()
        if redis_client:
            await redis_client.xack(self.stream_name, group_name, event_id)

    async def get_stream_info(self) -> Dict:
        """Get stream information and statistics"""
        redis_client = await self._get_redis_client()
        if redis_client:
            try:
                info = await redis_client.xinfo_stream(self.stream_name)
                return {
                    "length": info.get("length", 0),
                    "first_entry": info.get("first-entry"),
                    "last_entry": info.get("last-entry"),
                    "groups": info.get("groups", 0),
                }
            except Exception:
                return {"error": "Stream not found or inaccessible"}

        return {"error": "Redis not available"}


class EventMetrics:
    """Track event system metrics"""

    def __init__(self):
        self.metrics = {
            "events_published": 0,
            "events_consumed": 0,
            "subscribers_count": 0,
            "filter_matches": 0,
            "processing_errors": 0,
            "start_time": datetime.utcnow(),
        }

    def record_publish(self):
        """Record event publication"""
        self.metrics["events_published"] += 1

    def record_consume(self):
        """Record event consumption"""
        self.metrics["events_consumed"] += 1

    def record_filter_match(self):
        """Record filter match"""
        self.metrics["filter_matches"] += 1

    def record_error(self):
        """Record processing error"""
        self.metrics["processing_errors"] += 1

    def update_subscriber_count(self, count: int):
        """Update active subscriber count"""
        self.metrics["subscribers_count"] = count

    def get_metrics(self) -> Dict:
        """Get current metrics"""
        uptime = (datetime.utcnow() - self.metrics["start_time"]).total_seconds()

        return {
            **self.metrics,
            "uptime_seconds": uptime,
            "events_per_second": self.metrics["events_published"] / max(uptime, 1),
            "error_rate": self.metrics["processing_errors"]
            / max(self.metrics["events_published"], 1),
        }
