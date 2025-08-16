"""
Memory Curator System for T-Developer

This module implements the memory management system for T-Developer learning,
providing persistent storage and retrieval of learning data using DynamoDB.

The MemoryCurator manages learning memories with intelligent retention,
fast retrieval, and automatic cleanup of obsolete memories.
"""

from __future__ import annotations

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

import aiosqlite
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT: int = 30
MAX_MEMORY_AGE_DAYS: int = 90
DEFAULT_RETENTION_SCORE: float = 0.8
MEMORY_BATCH_SIZE: int = 25


@dataclass
class Memory:
    """Learning memory data structure.

    Attributes:
        id: Unique memory identifier
        type: Type of memory (evolution_cycle, pattern_extraction, etc.)
        timestamp: When memory was created
        data: Core memory data
        metadata: Additional metadata including importance and retention
        cycle_id: Associated evolution cycle ID
        agent_id: Agent that created this memory
        relationships: Relationships with other memories
        expires_at: When memory expires (optional)
    """

    id: str
    type: str
    timestamp: datetime
    data: dict[str, Any]
    metadata: dict[str, Any]
    cycle_id: Optional[str] = None
    agent_id: Optional[str] = None
    relationships: Optional[dict[str, Any]] = None
    expires_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert memory to dictionary for storage."""
        result = asdict(self)
        # Convert datetime objects to ISO strings
        result["timestamp"] = self.timestamp.isoformat()
        if self.expires_at:
            result["expires_at"] = self.expires_at.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Memory:
        """Create memory from dictionary."""
        # Convert ISO strings back to datetime objects
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        if data.get("expires_at"):
            data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return cls(**data)

    def get_importance(self) -> float:
        """Get importance score for this memory."""
        return self.metadata.get("importance", DEFAULT_RETENTION_SCORE)

    def get_retention_score(self) -> float:
        """Get retention score for this memory."""
        return self.metadata.get("retention_score", DEFAULT_RETENTION_SCORE)

    def increment_access_count(self) -> None:
        """Increment access count and update last accessed time."""
        self.metadata["access_count"] = self.metadata.get("access_count", 0) + 1
        self.metadata["last_accessed"] = datetime.now().isoformat()

    def is_expired(self) -> bool:
        """Check if memory has expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    def calculate_relevance_decay(self) -> float:
        """Calculate relevance decay based on age and access patterns."""
        age_days = (datetime.now() - self.timestamp).days
        access_count = self.metadata.get("access_count", 0)

        # Base decay: memories become less relevant over time
        age_decay = max(0.1, 1.0 - (age_days / MAX_MEMORY_AGE_DAYS))

        # Access boost: frequently accessed memories stay relevant longer
        access_boost = min(2.0, 1.0 + (access_count / 10))

        return age_decay * access_boost


class MemoryStorage(ABC):
    """Abstract base class for memory storage backends."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend."""
        pass

    @abstractmethod
    async def store_memory(self, memory: Memory) -> None:
        """Store a memory."""
        pass

    @abstractmethod
    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory by ID."""
        pass

    @abstractmethod
    async def update_memory(self, memory: Memory) -> None:
        """Update an existing memory."""
        pass

    @abstractmethod
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        pass

    @abstractmethod
    async def search_memories(self, criteria: dict[str, Any], limit: int = 100) -> list[Memory]:
        """Search memories by criteria."""
        pass

    @abstractmethod
    async def get_memories_by_type(self, memory_type: str) -> list[Memory]:
        """Get all memories of a specific type."""
        pass

    @abstractmethod
    async def cleanup_expired_memories(self) -> int:
        """Remove expired memories and return count of removed."""
        pass


class DynamoDBStorage(MemoryStorage):
    """DynamoDB storage backend for memories."""

    def __init__(self, table_name: str = "t-developer-memories", region_name: str = "us-east-1"):
        """Initialize DynamoDB storage.

        Args:
            table_name: DynamoDB table name
            region_name: AWS region name
        """
        self.table_name = table_name
        self.region_name = region_name
        self.dynamodb = None
        self.table = None
        self.logger = logging.getLogger(self.__class__.__name__)

    async def initialize(self) -> None:
        """Initialize DynamoDB connection and create table if needed."""
        try:
            # Try to create DynamoDB client
            self.dynamodb = boto3.resource("dynamodb", region_name=self.region_name)

            # Check if table exists, create if it doesn't
            await self._ensure_table_exists()

            self.table = self.dynamodb.Table(self.table_name)
            self.logger.info(f"DynamoDB storage initialized with table: {self.table_name}")

        except (NoCredentialsError, ClientError) as e:
            self.logger.warning(f"DynamoDB not available ({e}), falling back to SQLite")
            raise

    async def _ensure_table_exists(self) -> None:
        """Ensure the DynamoDB table exists, create if it doesn't."""
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load()  # This will raise an exception if table doesn't exist

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Table doesn't exist, create it
                await self._create_table()
            else:
                raise

    async def _create_table(self) -> None:
        """Create the DynamoDB table with appropriate schema."""
        table = self.dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],  # Partition key
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "type", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "type-timestamp-index",
                    "KeySchema": [
                        {"AttributeName": "type", "KeyType": "HASH"},
                        {"AttributeName": "timestamp", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "BillingMode": "PAY_PER_REQUEST",
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        # Wait for table to be created
        table.wait_until_exists()
        self.logger.info(f"Created DynamoDB table: {self.table_name}")

    async def store_memory(self, memory: Memory) -> None:
        """Store a memory in DynamoDB."""
        try:
            item = memory.to_dict()
            # Convert nested objects to JSON strings for DynamoDB
            item["data"] = json.dumps(item["data"])
            item["metadata"] = json.dumps(item["metadata"])
            if item.get("relationships"):
                item["relationships"] = json.dumps(item["relationships"])

            self.table.put_item(Item=item)
            self.logger.debug(f"Stored memory: {memory.id}")

        except ClientError as e:
            self.logger.error(f"Failed to store memory {memory.id}: {e}")
            raise

    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory by ID from DynamoDB."""
        try:
            response = self.table.get_item(Key={"id": memory_id})

            if "Item" in response:
                item = response["Item"]
                # Convert JSON strings back to objects
                item["data"] = json.loads(item["data"])
                item["metadata"] = json.loads(item["metadata"])
                if item.get("relationships"):
                    item["relationships"] = json.loads(item["relationships"])

                memory = Memory.from_dict(item)
                memory.increment_access_count()
                await self.update_memory(memory)  # Update access count
                return memory

            return None

        except ClientError as e:
            self.logger.error(f"Failed to get memory {memory_id}: {e}")
            return None

    async def update_memory(self, memory: Memory) -> None:
        """Update an existing memory in DynamoDB."""
        await self.store_memory(memory)  # DynamoDB put_item handles updates

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory from DynamoDB."""
        try:
            response = self.table.delete_item(Key={"id": memory_id}, ReturnValues="ALL_OLD")
            return "Attributes" in response

        except ClientError as e:
            self.logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    async def search_memories(self, criteria: dict[str, Any], limit: int = 100) -> list[Memory]:
        """Search memories by criteria using DynamoDB."""
        try:
            memories = []

            if "type" in criteria:
                # Use GSI for type-based queries
                response = self.table.query(
                    IndexName="type-timestamp-index",
                    KeyConditionExpression=boto3.dynamodb.conditions.Key("type").eq(
                        criteria["type"]
                    ),
                    Limit=limit,
                    ScanIndexForward=False,  # Most recent first
                )

                for item in response.get("Items", []):
                    memory = self._item_to_memory(item)
                    if memory and self._matches_criteria(memory, criteria):
                        memories.append(memory)
            else:
                # Full table scan for other criteria
                response = self.table.scan(Limit=limit)

                for item in response.get("Items", []):
                    memory = self._item_to_memory(item)
                    if memory and self._matches_criteria(memory, criteria):
                        memories.append(memory)

            return memories

        except ClientError as e:
            self.logger.error(f"Failed to search memories: {e}")
            return []

    async def get_memories_by_type(self, memory_type: str) -> list[Memory]:
        """Get all memories of a specific type."""
        return await self.search_memories({"type": memory_type})

    async def cleanup_expired_memories(self) -> int:
        """Remove expired memories from DynamoDB."""
        try:
            # Scan for expired memories
            now = datetime.now().isoformat()
            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr("expires_at").lt(now)
            )

            deleted_count = 0
            for item in response.get("Items", []):
                memory_id = item["id"]
                if await self.delete_memory(memory_id):
                    deleted_count += 1

            self.logger.info(f"Cleaned up {deleted_count} expired memories")
            return deleted_count

        except ClientError as e:
            self.logger.error(f"Failed to cleanup expired memories: {e}")
            return 0

    def _item_to_memory(self, item: dict[str, Any]) -> Optional[Memory]:
        """Convert DynamoDB item to Memory object."""
        try:
            # Convert JSON strings back to objects
            item["data"] = json.loads(item["data"])
            item["metadata"] = json.loads(item["metadata"])
            if item.get("relationships"):
                item["relationships"] = json.loads(item["relationships"])

            return Memory.from_dict(item)

        except Exception as e:
            self.logger.error(f"Failed to convert item to memory: {e}")
            return None

    def _matches_criteria(self, memory: Memory, criteria: dict[str, Any]) -> bool:
        """Check if memory matches search criteria."""
        for key, value in criteria.items():
            if key == "type" and memory.type != value:
                return False
            elif key == "cycle_id" and memory.cycle_id != value:
                return False
            elif key == "agent_id" and memory.agent_id != value:
                return False
            elif key == "min_importance" and memory.get_importance() < value:
                return False
            elif key == "tags" and not any(tag in memory.metadata.get("tags", []) for tag in value):
                return False

        return True


class SQLiteStorage(MemoryStorage):
    """SQLite storage backend for memories (fallback when DynamoDB unavailable)."""

    def __init__(self, db_path: str = "memories.db"):
        """Initialize SQLite storage.

        Args:
            db_path: Database file path
        """
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)

    async def initialize(self) -> None:
        """Initialize SQLite database and create tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    cycle_id TEXT,
                    agent_id TEXT,
                    relationships TEXT,
                    expires_at TEXT
                )
            """
            )

            # Create indexes for performance
            await db.execute("CREATE INDEX IF NOT EXISTS idx_memories_type ON memories (type)")
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories (timestamp)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_cycle_id ON memories (cycle_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_expires_at ON memories (expires_at)"
            )

            await db.commit()

        self.logger.info(f"SQLite storage initialized at {self.db_path}")

    async def store_memory(self, memory: Memory) -> None:
        """Store a memory in SQLite."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                memory_dict = memory.to_dict()
                await db.execute(
                    """
                    INSERT OR REPLACE INTO memories
                    (id, type, timestamp, data, metadata, cycle_id, agent_id, relationships, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        memory.id,
                        memory.type,
                        memory.timestamp.isoformat(),
                        json.dumps(memory.data),
                        json.dumps(memory.metadata),
                        memory.cycle_id,
                        memory.agent_id,
                        json.dumps(memory.relationships) if memory.relationships else None,
                        memory.expires_at.isoformat() if memory.expires_at else None,
                    ),
                )
                await db.commit()

            self.logger.debug(f"Stored memory: {memory.id}")

        except Exception as e:
            self.logger.error(f"Failed to store memory {memory.id}: {e}")
            raise

    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory by ID from SQLite."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT * FROM memories WHERE id = ?", (memory_id,)
                ) as cursor:
                    row = await cursor.fetchone()

                if row:
                    memory = self._row_to_memory(row)
                    if memory:
                        memory.increment_access_count()
                        await self.update_memory(memory)
                    return memory

            return None

        except Exception as e:
            self.logger.error(f"Failed to get memory {memory_id}: {e}")
            return None

    async def update_memory(self, memory: Memory) -> None:
        """Update an existing memory in SQLite."""
        await self.store_memory(memory)  # INSERT OR REPLACE handles updates

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory from SQLite."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                await db.commit()
                return cursor.rowcount > 0

        except Exception as e:
            self.logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    async def search_memories(self, criteria: dict[str, Any], limit: int = 100) -> list[Memory]:
        """Search memories by criteria using SQLite."""
        try:
            where_clauses = []
            params = []

            # Build WHERE clause
            if "type" in criteria:
                where_clauses.append("type = ?")
                params.append(criteria["type"])

            if "cycle_id" in criteria:
                where_clauses.append("cycle_id = ?")
                params.append(criteria["cycle_id"])

            if "agent_id" in criteria:
                where_clauses.append("agent_id = ?")
                params.append(criteria["agent_id"])

            # Build query
            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
            query = f"""
                SELECT * FROM memories
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ?
            """
            params.append(limit)

            memories = []
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(query, params) as cursor:
                    async for row in cursor:
                        memory = self._row_to_memory(row)
                        if memory and self._matches_criteria(memory, criteria):
                            memories.append(memory)

            return memories

        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            return []

    async def get_memories_by_type(self, memory_type: str) -> list[Memory]:
        """Get all memories of a specific type."""
        return await self.search_memories({"type": memory_type})

    async def cleanup_expired_memories(self) -> int:
        """Remove expired memories from SQLite."""
        try:
            now = datetime.now().isoformat()
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "DELETE FROM memories WHERE expires_at IS NOT NULL AND expires_at < ?", (now,)
                )
                await db.commit()

                deleted_count = cursor.rowcount
                self.logger.info(f"Cleaned up {deleted_count} expired memories")
                return deleted_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup expired memories: {e}")
            return 0

    def _row_to_memory(self, row: tuple) -> Optional[Memory]:
        """Convert SQLite row to Memory object."""
        try:
            return Memory(
                id=row[0],
                type=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                data=json.loads(row[3]),
                metadata=json.loads(row[4]),
                cycle_id=row[5],
                agent_id=row[6],
                relationships=json.loads(row[7]) if row[7] else None,
                expires_at=datetime.fromisoformat(row[8]) if row[8] else None,
            )
        except Exception as e:
            self.logger.error(f"Failed to convert row to memory: {e}")
            return None

    def _matches_criteria(self, memory: Memory, criteria: dict[str, Any]) -> bool:
        """Check if memory matches search criteria."""
        for key, value in criteria.items():
            if key == "min_importance" and memory.get_importance() < value:
                return False
            elif key == "tags" and not any(tag in memory.metadata.get("tags", []) for tag in value):
                return False

        return True


class MemoryCurator:
    """Main memory curation system.

    Manages learning memories with intelligent storage, retrieval,
    and lifecycle management. Automatically handles retention policies
    and provides fast access to relevant memories.

    Example:
        >>> curator = MemoryCurator()
        >>> await curator.initialize()
        >>> memory = Memory(...)
        >>> await curator.store_memory(memory)
        >>> memories = await curator.search_memories({"type": "pattern_extraction"})
    """

    def __init__(
        self,
        storage: Optional[MemoryStorage] = None,
        retention_policy: Optional[dict[str, Any]] = None,
    ):
        """Initialize memory curator.

        Args:
            storage: Storage backend (creates DynamoDB or SQLite if None)
            retention_policy: Memory retention policy configuration
        """
        self.storage = storage
        self.retention_policy = retention_policy or self._get_default_retention_policy()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._memory_cache: dict[str, Memory] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    async def initialize(self) -> None:
        """Initialize the memory curator."""
        if not self.storage:
            # Try DynamoDB first, fallback to SQLite
            try:
                self.storage = DynamoDBStorage()
                await self.storage.initialize()
            except Exception as e:
                self.logger.warning(f"DynamoDB unavailable, using SQLite: {e}")
                self.storage = SQLiteStorage()
                await self.storage.initialize()
        else:
            await self.storage.initialize()

        self.logger.info("Memory curator initialized")

    async def store_memory(self, memory: Memory) -> None:
        """Store a memory with automatic retention policy application.

        Args:
            memory: Memory to store

        Raises:
            ValueError: If memory is invalid
            RuntimeError: If storage fails
        """
        if not memory.id or not memory.type:
            raise ValueError("Memory must have id and type")

        # Apply retention policy
        await self._apply_retention_policy(memory)

        try:
            await self.storage.store_memory(memory)

            # Cache the memory
            self._memory_cache[memory.id] = memory

            # Limit cache size
            if len(self._memory_cache) > 1000:
                await self._cleanup_cache()

            self.logger.debug(f"Stored memory: {memory.id}")

        except Exception as e:
            self.logger.error(f"Failed to store memory {memory.id}: {e}")
            raise RuntimeError(f"Memory storage failed: {e}")

    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory if found, None otherwise
        """
        # Check cache first
        if memory_id in self._memory_cache:
            self._cache_hits += 1
            return self._memory_cache[memory_id]

        self._cache_misses += 1

        try:
            memory = await self.storage.get_memory(memory_id)

            if memory and not memory.is_expired():
                # Cache for future access
                self._memory_cache[memory_id] = memory
                return memory
            elif memory and memory.is_expired():
                # Remove expired memory
                await self.delete_memory(memory_id)

            return None

        except Exception as e:
            self.logger.error(f"Failed to get memory {memory_id}: {e}")
            return None

    async def search_memories(self, criteria: dict[str, Any], limit: int = 100) -> list[Memory]:
        """Search memories by criteria.

        Args:
            criteria: Search criteria dictionary
            limit: Maximum number of results

        Returns:
            List of matching memories
        """
        try:
            memories = await self.storage.search_memories(criteria, limit)

            # Filter out expired memories
            valid_memories = []
            for memory in memories:
                if not memory.is_expired():
                    valid_memories.append(memory)
                else:
                    # Remove expired memory
                    await self.delete_memory(memory.id)

            # Sort by relevance
            sorted_memories = await self._sort_by_relevance(valid_memories, criteria)

            return sorted_memories

        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            return []

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory.

        Args:
            memory_id: Memory identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            # Remove from cache
            if memory_id in self._memory_cache:
                del self._memory_cache[memory_id]

            return await self.storage.delete_memory(memory_id)

        except Exception as e:
            self.logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    async def store_evolution_cycle_memory(
        self,
        cycle_id: str,
        phase: str,
        task: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        duration: float,
        success: bool,
        metrics_before: dict[str, float],
        metrics_after: dict[str, float],
        patterns_used: list[str] = None,
        new_patterns: list[str] = None,
    ) -> Memory:
        """Store memory for an evolution cycle.

        Args:
            cycle_id: Evolution cycle ID
            phase: Evolution phase
            task: Task executed
            inputs: Task inputs
            outputs: Task outputs
            duration: Execution duration
            success: Whether task succeeded
            metrics_before: Metrics before execution
            metrics_after: Metrics after execution
            patterns_used: Patterns used in execution
            new_patterns: New patterns discovered

        Returns:
            Created memory object
        """
        memory = Memory(
            id=f"memory_{hashlib.md5(cycle_id.encode()).hexdigest()[:8]}",
            type="evolution_cycle",
            timestamp=datetime.now(),
            cycle_id=cycle_id,
            data={
                "phase": phase,
                "task": task,
                "inputs": inputs,
                "outputs": outputs,
                "duration": duration,
                "success": success,
                "metrics_before": metrics_before,
                "metrics_after": metrics_after,
                "patterns_used": patterns_used or [],
                "new_patterns": new_patterns or [],
            },
            metadata={
                "importance": self._calculate_cycle_importance(
                    success, metrics_before, metrics_after
                ),
                "tags": [phase, task, "evolution_cycle"],
                "retention_score": 0.9 if success else 0.6,
            },
        )

        await self.store_memory(memory)
        return memory

    async def store_pattern_extraction_memory(
        self,
        source_cycle: str,
        extracted_patterns: list[str],
        confidence_scores: dict[str, float],
        extraction_method: str,
    ) -> Memory:
        """Store memory for pattern extraction.

        Args:
            source_cycle: Source evolution cycle
            extracted_patterns: List of extracted pattern IDs
            confidence_scores: Confidence scores for patterns
            extraction_method: Method used for extraction

        Returns:
            Created memory object
        """
        memory = Memory(
            id=f"memory_{hashlib.md5(f'pattern_{source_cycle}'.encode()).hexdigest()[:8]}",
            type="pattern_extraction",
            timestamp=datetime.now(),
            cycle_id=source_cycle,
            data={
                "source_cycle": source_cycle,
                "extracted_patterns": extracted_patterns,
                "confidence_scores": confidence_scores,
                "extraction_method": extraction_method,
            },
            metadata={
                "importance": min(
                    1.0, len(extracted_patterns) / 5
                ),  # Up to 5 patterns = max importance
                "tags": ["pattern_extraction", extraction_method],
                "retention_score": 0.8,
            },
        )

        await self.store_memory(memory)
        return memory

    async def store_performance_metric_memory(
        self,
        metric_name: str,
        value: float,
        baseline: float,
        improvement: float,
        measurement_context: dict[str, Any],
    ) -> Memory:
        """Store memory for performance metrics.

        Args:
            metric_name: Name of the metric
            value: Current metric value
            baseline: Baseline value
            improvement: Improvement percentage
            measurement_context: Context of measurement

        Returns:
            Created memory object
        """
        memory = Memory(
            id=f"memory_{hashlib.md5(f'metric_{metric_name}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}",
            type="performance_metric",
            timestamp=datetime.now(),
            data={
                "metric_name": metric_name,
                "value": value,
                "baseline": baseline,
                "improvement": improvement,
                "measurement_context": measurement_context,
            },
            metadata={
                "importance": min(1.0, abs(improvement) / 0.5),  # 50% improvement = max importance
                "tags": ["performance", metric_name],
                "retention_score": 0.7
                + min(0.3, abs(improvement)),  # Higher retention for bigger improvements
            },
        )

        await self.store_memory(memory)
        return memory

    async def get_recent_memories(
        self, memory_type: Optional[str] = None, hours: int = 24, limit: int = 50
    ) -> list[Memory]:
        """Get recent memories within specified timeframe.

        Args:
            memory_type: Filter by memory type (optional)
            hours: Number of hours to look back
            limit: Maximum number of memories

        Returns:
            List of recent memories
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        criteria = {}
        if memory_type:
            criteria["type"] = memory_type

        all_memories = await self.search_memories(
            criteria, limit * 2
        )  # Get extra to filter by time

        # Filter by time and sort by recency
        recent_memories = [memory for memory in all_memories if memory.timestamp >= cutoff_time]

        recent_memories.sort(key=lambda m: m.timestamp, reverse=True)
        return recent_memories[:limit]

    async def get_related_memories(
        self, memory_id: str, relation_types: list[str] = None, limit: int = 20
    ) -> list[Memory]:
        """Get memories related to a specific memory.

        Args:
            memory_id: Source memory ID
            relation_types: Types of relationships to follow
            limit: Maximum number of related memories

        Returns:
            List of related memories
        """
        source_memory = await self.get_memory(memory_id)
        if not source_memory or not source_memory.relationships:
            return []

        related_memory_ids = []

        # Collect related memory IDs based on relationship types
        relationships = source_memory.relationships

        if not relation_types or "causes" in relation_types:
            related_memory_ids.extend(relationships.get("causes", []))

        if not relation_types or "effects" in relation_types:
            related_memory_ids.extend(relationships.get("effects", []))

        if not relation_types or "correlations" in relation_types:
            correlations = relationships.get("correlations", [])
            for correlation in correlations:
                if isinstance(correlation, dict) and "memory_id" in correlation:
                    related_memory_ids.append(correlation["memory_id"])

        # Retrieve related memories
        related_memories = []
        for memory_id in related_memory_ids[:limit]:
            memory = await self.get_memory(memory_id)
            if memory:
                related_memories.append(memory)

        return related_memories

    async def cleanup_old_memories(self, days: int = MAX_MEMORY_AGE_DAYS) -> int:
        """Remove old memories based on retention policy.

        Args:
            days: Age threshold in days

        Returns:
            Number of memories cleaned up
        """
        try:
            # First, cleanup expired memories
            expired_count = await self.storage.cleanup_expired_memories()

            # Then cleanup by age and retention score
            cutoff_date = datetime.now() - timedelta(days=days)

            # Get all memories (this might be expensive for large datasets)
            all_memories = await self.search_memories({}, limit=10000)

            cleanup_count = 0
            for memory in all_memories:
                should_cleanup = await self._should_cleanup_memory(memory, cutoff_date)
                if should_cleanup:
                    if await self.delete_memory(memory.id):
                        cleanup_count += 1

            total_cleaned = expired_count + cleanup_count
            self.logger.info(
                f"Cleaned up {total_cleaned} memories ({expired_count} expired, {cleanup_count} old)"
            )
            return total_cleaned

        except Exception as e:
            self.logger.error(f"Failed to cleanup old memories: {e}")
            return 0

    async def get_memory_statistics(self) -> dict[str, Any]:
        """Get statistics about stored memories.

        Returns:
            Dictionary containing memory statistics
        """
        try:
            # Get counts by type
            type_counts = {}
            total_memories = 0

            for memory_type in [
                "evolution_cycle",
                "pattern_extraction",
                "failure_analysis",
                "performance_metric",
                "feedback",
            ]:
                memories = await self.storage.get_memories_by_type(memory_type)
                type_counts[memory_type] = len(memories)
                total_memories += len(memories)

            # Calculate cache statistics
            cache_hit_rate = 0.0
            if self._cache_hits + self._cache_misses > 0:
                cache_hit_rate = self._cache_hits / (self._cache_hits + self._cache_misses)

            stats = {
                "total_memories": total_memories,
                "type_counts": type_counts,
                "cache_size": len(self._memory_cache),
                "cache_hit_rate": cache_hit_rate,
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "storage_type": self.storage.__class__.__name__,
            }

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get memory statistics: {e}")
            return {"error": str(e)}

    def _get_default_retention_policy(self) -> dict[str, Any]:
        """Get default memory retention policy."""
        return {
            "max_age_days": MAX_MEMORY_AGE_DAYS,
            "min_retention_score": 0.3,
            "high_importance_threshold": 0.8,
            "type_policies": {
                "evolution_cycle": {"min_retention_score": 0.5, "max_age_days": 180},
                "pattern_extraction": {"min_retention_score": 0.7, "max_age_days": 365},
                "performance_metric": {"min_retention_score": 0.4, "max_age_days": 90},
                "failure_analysis": {"min_retention_score": 0.8, "max_age_days": 365},
            },
        }

    async def _apply_retention_policy(self, memory: Memory) -> None:
        """Apply retention policy to set expiration and scores."""
        policy = self.retention_policy
        type_policy = policy.get("type_policies", {}).get(memory.type, {})

        # Set retention score if not already set
        if "retention_score" not in memory.metadata:
            memory.metadata["retention_score"] = type_policy.get(
                "min_retention_score", DEFAULT_RETENTION_SCORE
            )

        # Set expiration if not already set
        if not memory.expires_at:
            max_age_days = type_policy.get("max_age_days", policy["max_age_days"])
            memory.expires_at = datetime.now() + timedelta(days=max_age_days)

    async def _should_cleanup_memory(self, memory: Memory, cutoff_date: datetime) -> bool:
        """Determine if memory should be cleaned up."""
        # Don't cleanup if recently accessed
        last_accessed = memory.metadata.get("last_accessed")
        if last_accessed:
            last_accessed_date = datetime.fromisoformat(last_accessed)
            if last_accessed_date > cutoff_date:
                return False

        # Don't cleanup high importance memories
        if memory.get_importance() >= self.retention_policy["high_importance_threshold"]:
            return False

        # Cleanup if old and low retention score
        if memory.timestamp < cutoff_date:
            return memory.get_retention_score() < self.retention_policy["min_retention_score"]

        return False

    def _calculate_cycle_importance(
        self, success: bool, metrics_before: dict[str, float], metrics_after: dict[str, float]
    ) -> float:
        """Calculate importance score for evolution cycle."""
        if not success:
            return 0.3  # Failed cycles have low but non-zero importance

        # Calculate improvement
        improvements = []
        for metric in ["coverage", "complexity", "docstring_coverage"]:
            if metric in metrics_before and metric in metrics_after:
                if metrics_before[metric] > 0:
                    improvement = (metrics_after[metric] - metrics_before[metric]) / metrics_before[
                        metric
                    ]
                    improvements.append(improvement)

        avg_improvement = sum(improvements) / len(improvements) if improvements else 0

        # Scale to 0-1 range
        importance = 0.5 + min(0.5, max(-0.2, avg_improvement))
        return importance

    async def _sort_by_relevance(
        self, memories: list[Memory], criteria: dict[str, Any]
    ) -> list[Memory]:
        """Sort memories by relevance to search criteria."""
        scored_memories = []

        for memory in memories:
            relevance_score = await self._calculate_relevance_score(memory, criteria)
            scored_memories.append((memory, relevance_score))

        # Sort by relevance score (descending)
        scored_memories.sort(key=lambda x: x[1], reverse=True)

        return [memory for memory, score in scored_memories]

    async def _calculate_relevance_score(self, memory: Memory, criteria: dict[str, Any]) -> float:
        """Calculate relevance score for memory given search criteria."""
        score = 0.0

        # Base importance score
        score += memory.get_importance() * 0.3

        # Recency score (newer memories are more relevant)
        age_days = (datetime.now() - memory.timestamp).days
        recency_score = max(0.0, 1.0 - (age_days / 30))  # Decay over 30 days
        score += recency_score * 0.2

        # Access frequency score
        access_count = memory.metadata.get("access_count", 0)
        frequency_score = min(1.0, access_count / 10)  # Cap at 10 accesses
        score += frequency_score * 0.2

        # Tag matching score
        search_tags = criteria.get("tags", [])
        memory_tags = memory.metadata.get("tags", [])
        if search_tags and memory_tags:
            tag_overlap = len(set(search_tags).intersection(set(memory_tags)))
            tag_score = tag_overlap / len(search_tags)
            score += tag_score * 0.3

        return score

    async def _cleanup_cache(self) -> None:
        """Clean up memory cache by removing least recently used entries."""
        # Keep only the 500 most recently accessed memories
        cache_items = list(self._memory_cache.items())

        # Sort by last accessed time
        cache_items.sort(
            key=lambda x: x[1].metadata.get("last_accessed", "1970-01-01"), reverse=True
        )

        # Keep top 500
        self._memory_cache = dict(cache_items[:500])
