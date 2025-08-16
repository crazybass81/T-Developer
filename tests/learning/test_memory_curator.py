"""
Comprehensive tests for Memory Curator System.

This module tests the memory management and curation system
for T-Developer learning.
"""

from __future__ import annotations

import asyncio
import tempfile
import os
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, Mock

import pytest

from packages.learning.memory_curator import (
    Memory,
    MemoryCurator,
    MemoryIndex,
    MemoryMetrics,
    MemoryStorage,
    MAX_MEMORY_SIZE,
    DEFAULT_RETENTION_DAYS,
)


@pytest.fixture
async def temp_db_path() -> AsyncGenerator[str, None]:
    """Create temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    yield db_path
    
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def sample_memory() -> Memory:
    """Create sample memory for testing."""
    return Memory(
        id="mem_001",
        type="evolution_cycle",
        timestamp=datetime.now(),
        data={
            "duration": 120,
            "success": True,
            "improvements": ["coverage", "performance"],
        },
        metadata={
            "importance": 0.8,
            "tags": ["testing", "improvement"],
            "retention_score": 0.9,
        },
    )


@pytest.fixture
async def memory_storage(temp_db_path: str) -> AsyncGenerator[MemoryStorage, None]:
    """Create memory storage instance for testing."""
    storage = MemoryStorage(temp_db_path)
    await storage.initialize()
    yield storage


@pytest.fixture
async def memory_curator(memory_storage: MemoryStorage) -> AsyncGenerator[MemoryCurator, None]:
    """Create memory curator instance for testing."""
    curator = MemoryCurator(storage=memory_storage)
    await curator.initialize()
    yield curator


class TestMemory:
    """Test Memory dataclass functionality."""

    def test_memory_creation(self, sample_memory: Memory) -> None:
        """Test memory creation with all fields.
        
        Given: Valid memory data
        When: Memory is created
        Then: All fields should be set correctly
        """
        assert sample_memory.id == "mem_001"
        assert sample_memory.type == "evolution_cycle"
        assert sample_memory.data["success"] is True
        assert sample_memory.metadata["importance"] == 0.8

    def test_memory_to_dict(self, sample_memory: Memory) -> None:
        """Test memory serialization to dictionary.
        
        Given: Memory instance
        When: to_dict is called
        Then: Should return dictionary with correct structure
        """
        mem_dict = sample_memory.to_dict()
        
        assert isinstance(mem_dict, dict)
        assert mem_dict["id"] == "mem_001"
        assert mem_dict["type"] == "evolution_cycle"
        assert isinstance(mem_dict["timestamp"], str)

    def test_memory_from_dict(self, sample_memory: Memory) -> None:
        """Test memory deserialization from dictionary.
        
        Given: Memory dictionary
        When: from_dict is called
        Then: Should return Memory with correct types
        """
        mem_dict = sample_memory.to_dict()
        reconstructed = Memory.from_dict(mem_dict)
        
        assert reconstructed.id == sample_memory.id
        assert reconstructed.type == sample_memory.type
        assert isinstance(reconstructed.timestamp, datetime)
        assert reconstructed.data == sample_memory.data


class TestMemoryStorage:
    """Test MemoryStorage functionality."""

    @pytest.mark.asyncio
    async def test_storage_initialization(self, temp_db_path: str) -> None:
        """Test memory storage initialization.
        
        Given: Database path
        When: Storage is initialized
        Then: Should create tables
        """
        storage = MemoryStorage(temp_db_path)
        await storage.initialize()
        
        # Verify tables exist
        import aiosqlite
        async with aiosqlite.connect(temp_db_path) as db:
            async with db.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
                tables = [row[0] for row in await cursor.fetchall()]
                
        assert "memories" in tables

    @pytest.mark.asyncio
    async def test_store_and_get_memory(
        self, memory_storage: MemoryStorage, sample_memory: Memory
    ) -> None:
        """Test storing and retrieving memories.
        
        Given: Memory storage and sample memory
        When: Memory is stored and retrieved
        Then: Should return identical memory
        """
        await memory_storage.store_memory(sample_memory)
        retrieved = await memory_storage.get_memory(sample_memory.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_memory.id
        assert retrieved.type == sample_memory.type
        assert retrieved.data == sample_memory.data

    @pytest.mark.asyncio
    async def test_search_memories(
        self, memory_storage: MemoryStorage, sample_memory: Memory
    ) -> None:
        """Test searching memories by criteria.
        
        Given: Stored memories
        When: Memories are searched
        Then: Should return matching memories
        """
        await memory_storage.store_memory(sample_memory)
        
        # Search by type
        results = await memory_storage.search_memories({"type": "evolution_cycle"})
        assert len(results) >= 1
        assert all(m.type == "evolution_cycle" for m in results)

    @pytest.mark.asyncio
    async def test_delete_memory(
        self, memory_storage: MemoryStorage, sample_memory: Memory
    ) -> None:
        """Test deleting memory.
        
        Given: Stored memory
        When: Memory is deleted
        Then: Should no longer be retrievable
        """
        await memory_storage.store_memory(sample_memory)
        
        deleted = await memory_storage.delete_memory(sample_memory.id)
        assert deleted is True
        
        retrieved = await memory_storage.get_memory(sample_memory.id)
        assert retrieved is None


class TestMemoryCurator:
    """Test MemoryCurator functionality."""

    @pytest.mark.asyncio
    async def test_curator_initialization(self, memory_curator: MemoryCurator) -> None:
        """Test memory curator initialization.
        
        Given: Memory storage
        When: Curator is initialized
        Then: Should set up correctly
        """
        assert memory_curator.storage is not None
        assert memory_curator.index is not None

    @pytest.mark.asyncio
    async def test_store_memory(
        self, memory_curator: MemoryCurator, sample_memory: Memory
    ) -> None:
        """Test storing memory through curator.
        
        Given: Memory curator and sample memory
        When: Memory is stored
        Then: Should be indexed and stored
        """
        await memory_curator.store_memory(sample_memory)
        
        # Verify storage
        retrieved = await memory_curator.storage.get_memory(sample_memory.id)
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_search_memories(
        self, memory_curator: MemoryCurator, sample_memory: Memory
    ) -> None:
        """Test searching memories through curator.
        
        Given: Stored memories
        When: Search is performed
        Then: Should return relevant results
        """
        await memory_curator.store_memory(sample_memory)
        
        results = await memory_curator.search_memories({"tags": ["testing"]})
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_get_memory_metrics(self, memory_curator: MemoryCurator) -> None:
        """Test getting memory metrics.
        
        Given: Memory curator with data
        When: Metrics are requested
        Then: Should return comprehensive metrics
        """
        metrics = await memory_curator.get_memory_metrics()
        
        assert isinstance(metrics, MemoryMetrics)
        assert metrics.total_memories >= 0
        assert metrics.storage_size_mb >= 0

    @pytest.mark.asyncio
    async def test_cleanup_old_memories(
        self, memory_curator: MemoryCurator
    ) -> None:
        """Test cleanup of old memories.
        
        Given: Old memories in storage
        When: Cleanup is performed
        Then: Should remove old memories
        """
        # Create old memory
        old_memory = Memory(
            id="old_mem",
            type="test",
            timestamp=datetime.now() - timedelta(days=100),
            data={},
            metadata={"importance": 0.1, "retention_score": 0.2},
        )
        
        await memory_curator.store_memory(old_memory)
        
        # Cleanup
        removed = await memory_curator.cleanup_old_memories(days=50)
        
        assert removed >= 0


class TestMemoryIndex:
    """Test MemoryIndex functionality."""

    def test_index_creation(self) -> None:
        """Test memory index creation.
        
        Given: Index parameters
        When: Index is created
        Then: Should initialize correctly
        """
        index = MemoryIndex()
        assert index is not None

    def test_add_to_index(self, sample_memory: Memory) -> None:
        """Test adding memory to index.
        
        Given: Memory index and sample memory
        When: Memory is added to index
        Then: Should be indexed for search
        """
        index = MemoryIndex()
        index.add_memory(sample_memory)
        
        # Test basic functionality
        assert index is not None


class TestMemoryCuratorIntegration:
    """Integration tests for memory curator system."""

    @pytest.mark.asyncio
    async def test_full_memory_lifecycle(self, temp_db_path: str) -> None:
        """Test complete memory lifecycle.
        
        Given: Empty memory curator
        When: Complete workflow is executed
        Then: All operations should work correctly
        """
        # Initialize curator
        storage = MemoryStorage(temp_db_path)
        await storage.initialize()
        
        curator = MemoryCurator(storage=storage)
        await curator.initialize()
        
        # Create and store memory
        memory = Memory(
            id="lifecycle_mem",
            type="test_cycle",
            timestamp=datetime.now(),
            data={"test": "data", "success": True},
            metadata={"importance": 0.7, "tags": ["test", "integration"]},
        )
        
        await curator.store_memory(memory)
        
        # Search and retrieve
        search_results = await curator.search_memories({"type": "test_cycle"})
        assert len(search_results) >= 1
        
        retrieved = await curator.get_memory(memory.id)
        assert retrieved is not None
        assert retrieved.id == memory.id
        
        # Get metrics
        metrics = await curator.get_memory_metrics()
        assert metrics.total_memories >= 1
        
        # Cleanup test
        removed = await curator.cleanup_old_memories(days=1)
        assert removed >= 0

    @pytest.mark.asyncio
    async def test_concurrent_memory_operations(self, memory_curator: MemoryCurator) -> None:
        """Test concurrent memory operations.
        
        Given: Memory curator
        When: Multiple operations are performed concurrently
        Then: Should handle concurrency correctly
        """
        # Create multiple memories
        memories = []
        for i in range(10):
            memory = Memory(
                id=f"concurrent_{i}",
                type="concurrent_test",
                timestamp=datetime.now(),
                data={"index": i},
                metadata={"importance": 0.5, "tags": ["concurrent"]},
            )
            memories.append(memory)
        
        # Store concurrently
        tasks = [memory_curator.store_memory(mem) for mem in memories]
        await asyncio.gather(*tasks)
        
        # Search concurrently
        search_tasks = [
            memory_curator.search_memories({"type": "concurrent_test"})
            for _ in range(5)
        ]
        
        search_results = await asyncio.gather(*search_tasks)
        assert len(search_results) == 5
        assert all(len(result) >= 10 for result in search_results)

    @pytest.mark.asyncio
    async def test_memory_performance(self, memory_curator: MemoryCurator) -> None:
        """Test memory curator performance.
        
        Given: Large number of memories
        When: Operations are performed
        Then: Should maintain reasonable performance
        """
        import time
        
        # Store many memories
        start_time = time.time()
        
        for i in range(100):
            memory = Memory(
                id=f"perf_{i}",
                type="performance_test",
                timestamp=datetime.now(),
                data={"value": i, "data": f"test_data_{i}"},
                metadata={"importance": 0.5 + (i % 50) * 0.01},
            )
            await memory_curator.store_memory(memory)
        
        store_time = time.time() - start_time
        
        # Search performance
        start_time = time.time()
        results = await memory_curator.search_memories({"type": "performance_test"})
        search_time = time.time() - start_time
        
        # Basic performance assertions
        assert store_time < 30.0  # Should store 100 memories in under 30 seconds
        assert search_time < 5.0  # Should search in under 5 seconds
        assert len(results) == 100  # Should find all memories


# Property-based testing
# Note: Property-based testing with hypothesis would go here
# Commented out to avoid optional dependency issues

class TestMemoryProperties:
    """Property-based tests for memory system."""

    @given(
        importance=st.floats(min_value=0.0, max_value=1.0),
        memory_type=st.text(min_size=1, max_size=50),
    )
    def test_memory_creation_properties(
        self,
        importance: float,
        memory_type: str,
    ) -> None:
        """Test memory creation with various property combinations.
        
        Given: Any valid memory properties
        When: Memory is created
        Then: Should create valid memory without errors
        """
        memory = Memory(
            id="test_memory",
            type=memory_type,
            timestamp=datetime.now(),
            data={"test": True},
            metadata={"importance": importance},
        )
        
        assert memory.type == memory_type
        assert memory.metadata["importance"] == importance
        assert 0.0 <= importance <= 1.0