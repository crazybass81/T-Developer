"""
Comprehensive tests for Pattern Database System.

This module tests the pattern storage and retrieval system,
including caching, search capabilities, and analytics.
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, Mock, patch

import pytest
import aiosqlite

from packages.learning.pattern_database import (
    Pattern,
    PatternCache,
    PatternDatabase,
    DATABASE_FILE,
    MAX_CACHE_SIZE,
    CACHE_TTL_SECONDS,
)


@pytest.fixture
async def temp_db_path() -> AsyncGenerator[str, None]:
    """Create temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
async def pattern_db(temp_db_path: str) -> AsyncGenerator[PatternDatabase, None]:
    """Create pattern database instance for testing."""
    db = PatternDatabase(temp_db_path)
    await db.initialize()
    yield db


@pytest.fixture
def sample_pattern() -> Pattern:
    """Create sample pattern for testing."""
    return Pattern(
        id="test_pattern_001",
        category="testing",
        name="Test Pattern",
        description="A test pattern for unit testing",
        context={"file_types": ["python"], "test_coverage": {"min": 0, "max": 80}},
        action={
            "type": "test_addition",
            "steps": [
                {"description": "Analyze function signature"},
                {"description": "Generate test cases"},
            ],
        },
        outcome={"coverage_improvement": 15, "test_count_increase": 5},
        success_rate=0.9,
        usage_count=0,
        created_at=datetime.now(),
        tags=["testing", "automation"],
        confidence=0.9,
    )


@pytest.fixture
def pattern_cache() -> PatternCache:
    """Create pattern cache instance for testing."""
    return PatternCache(max_size=10, ttl=60)


class TestPattern:
    """Test Pattern dataclass functionality."""

    def test_pattern_creation(self, sample_pattern: Pattern) -> None:
        """Test pattern creation with all fields.
        
        Given: Valid pattern data
        When: Pattern is created
        Then: All fields should be set correctly
        """
        assert sample_pattern.id == "test_pattern_001"
        assert sample_pattern.category == "testing"
        assert sample_pattern.success_rate == 0.9
        assert sample_pattern.tags == ["testing", "automation"]
        assert sample_pattern.confidence == 0.9

    def test_pattern_to_dict(self, sample_pattern: Pattern) -> None:
        """Test pattern serialization to dictionary.
        
        Given: Pattern instance
        When: to_dict is called
        Then: Should return dictionary with ISO datetime strings
        """
        pattern_dict = sample_pattern.to_dict()
        
        assert isinstance(pattern_dict, dict)
        assert pattern_dict["id"] == "test_pattern_001"
        assert isinstance(pattern_dict["created_at"], str)
        assert "T" in pattern_dict["created_at"]  # ISO format

    def test_pattern_from_dict(self, sample_pattern: Pattern) -> None:
        """Test pattern deserialization from dictionary.
        
        Given: Pattern dictionary
        When: from_dict is called
        Then: Should return Pattern instance with correct types
        """
        pattern_dict = sample_pattern.to_dict()
        reconstructed = Pattern.from_dict(pattern_dict)
        
        assert reconstructed.id == sample_pattern.id
        assert reconstructed.category == sample_pattern.category
        assert isinstance(reconstructed.created_at, datetime)
        assert reconstructed.success_rate == sample_pattern.success_rate

    def test_pattern_round_trip(self, sample_pattern: Pattern) -> None:
        """Test pattern serialization round trip.
        
        Given: Pattern instance
        When: Converting to dict and back
        Then: Should preserve all data
        """
        pattern_dict = sample_pattern.to_dict()
        reconstructed = Pattern.from_dict(pattern_dict)
        
        assert reconstructed.id == sample_pattern.id
        assert reconstructed.context == sample_pattern.context
        assert reconstructed.action == sample_pattern.action
        assert reconstructed.outcome == sample_pattern.outcome


class TestPatternCache:
    """Test PatternCache functionality."""

    def test_cache_initialization(self) -> None:
        """Test cache initialization with custom parameters.
        
        Given: Custom cache parameters
        When: Cache is created
        Then: Should set parameters correctly
        """
        cache = PatternCache(max_size=50, ttl=120)
        
        assert cache.max_size == 50
        assert cache.ttl == 120
        assert len(cache._cache) == 0
        assert len(cache._access_times) == 0

    def test_cache_put_and_get(self, pattern_cache: PatternCache, sample_pattern: Pattern) -> None:
        """Test basic cache put and get operations.
        
        Given: Empty cache and pattern
        When: Pattern is put and retrieved
        Then: Should return the same pattern
        """
        pattern_cache.put(sample_pattern)
        retrieved = pattern_cache.get(sample_pattern.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_pattern.id
        assert retrieved.category == sample_pattern.category

    def test_cache_miss(self, pattern_cache: PatternCache) -> None:
        """Test cache miss for non-existent pattern.
        
        Given: Empty cache
        When: Non-existent pattern is requested
        Then: Should return None
        """
        retrieved = pattern_cache.get("non_existent")
        assert retrieved is None

    def test_cache_expiration(self, sample_pattern: Pattern) -> None:
        """Test cache entry expiration.
        
        Given: Cache with short TTL
        When: Entry expires
        Then: Should return None and clean up
        """
        cache = PatternCache(max_size=10, ttl=0)  # Immediate expiration
        cache.put(sample_pattern)
        
        # Entry should expire immediately
        retrieved = cache.get(sample_pattern.id)
        assert retrieved is None
        assert sample_pattern.id not in cache._cache

    def test_cache_lru_eviction(self, pattern_cache: PatternCache) -> None:
        """Test LRU eviction when cache is full.
        
        Given: Cache at capacity
        When: New pattern is added
        Then: LRU pattern should be evicted
        """
        cache = PatternCache(max_size=2, ttl=300)
        
        # Fill cache
        pattern1 = Pattern(
            id="p1", category="test", name="P1", description="Pattern 1",
            context={}, action={}, outcome={}, success_rate=0.9,
            usage_count=0, created_at=datetime.now()
        )
        pattern2 = Pattern(
            id="p2", category="test", name="P2", description="Pattern 2",
            context={}, action={}, outcome={}, success_rate=0.9,
            usage_count=0, created_at=datetime.now()
        )
        pattern3 = Pattern(
            id="p3", category="test", name="P3", description="Pattern 3",
            context={}, action={}, outcome={}, success_rate=0.9,
            usage_count=0, created_at=datetime.now()
        )
        
        cache.put(pattern1)
        cache.put(pattern2)
        
        # Access pattern1 to make it more recently used
        cache.get("p1")
        
        # Add pattern3 - should evict pattern2 (LRU)
        cache.put(pattern3)
        
        assert cache.get("p1") is not None  # Still in cache
        assert cache.get("p2") is None      # Evicted
        assert cache.get("p3") is not None  # Just added

    def test_cache_clear(self, pattern_cache: PatternCache, sample_pattern: Pattern) -> None:
        """Test cache clear operation.
        
        Given: Cache with entries
        When: Clear is called
        Then: All entries should be removed
        """
        pattern_cache.put(sample_pattern)
        assert len(pattern_cache._cache) == 1
        
        pattern_cache.clear()
        assert len(pattern_cache._cache) == 0
        assert len(pattern_cache._access_times) == 0


class TestPatternDatabase:
    """Test PatternDatabase functionality."""

    @pytest.mark.asyncio
    async def test_database_initialization(self, temp_db_path: str) -> None:
        """Test database initialization and table creation.
        
        Given: New database path
        When: Database is initialized
        Then: Tables should be created
        """
        db = PatternDatabase(temp_db_path)
        await db.initialize()
        
        assert db._initialized is True
        
        # Verify tables exist
        async with aiosqlite.connect(temp_db_path) as conn:
            async with conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ) as cursor:
                tables = [row[0] for row in await cursor.fetchall()]
                
        expected_tables = ["patterns", "pattern_usage", "pattern_relationships"]
        for table in expected_tables:
            assert table in tables

    @pytest.mark.asyncio
    async def test_store_and_get_pattern(
        self, pattern_db: PatternDatabase, sample_pattern: Pattern
    ) -> None:
        """Test storing and retrieving patterns.
        
        Given: Pattern database and sample pattern
        When: Pattern is stored and retrieved
        Then: Should return identical pattern
        """
        await pattern_db.store_pattern(sample_pattern)
        retrieved = await pattern_db.get_pattern(sample_pattern.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_pattern.id
        assert retrieved.category == sample_pattern.category
        assert retrieved.context == sample_pattern.context
        assert retrieved.action == sample_pattern.action

    @pytest.mark.asyncio
    async def test_get_nonexistent_pattern(self, pattern_db: PatternDatabase) -> None:
        """Test retrieving non-existent pattern.
        
        Given: Empty database
        When: Non-existent pattern is requested
        Then: Should return None
        """
        retrieved = await pattern_db.get_pattern("non_existent")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_update_pattern(
        self, pattern_db: PatternDatabase, sample_pattern: Pattern
    ) -> None:
        """Test updating an existing pattern.
        
        Given: Stored pattern
        When: Pattern is modified and updated
        Then: Changes should be persisted
        """
        await pattern_db.store_pattern(sample_pattern)
        
        # Modify pattern
        sample_pattern.success_rate = 0.95
        sample_pattern.usage_count = 10
        
        await pattern_db.update_pattern(sample_pattern)
        retrieved = await pattern_db.get_pattern(sample_pattern.id)
        
        assert retrieved is not None
        assert retrieved.success_rate == 0.95
        assert retrieved.usage_count == 10

    @pytest.mark.asyncio
    async def test_delete_pattern(
        self, pattern_db: PatternDatabase, sample_pattern: Pattern
    ) -> None:
        """Test deleting a pattern.
        
        Given: Stored pattern
        When: Pattern is deleted
        Then: Should no longer be retrievable
        """
        await pattern_db.store_pattern(sample_pattern)
        
        # Verify pattern exists
        retrieved = await pattern_db.get_pattern(sample_pattern.id)
        assert retrieved is not None
        
        # Delete pattern
        deleted = await pattern_db.delete_pattern(sample_pattern.id)
        assert deleted is True
        
        # Verify pattern is gone
        retrieved = await pattern_db.get_pattern(sample_pattern.id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_pattern(self, pattern_db: PatternDatabase) -> None:
        """Test deleting non-existent pattern.
        
        Given: Empty database
        When: Non-existent pattern deletion is attempted
        Then: Should return False
        """
        deleted = await pattern_db.delete_pattern("non_existent")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_search_patterns_by_category(
        self, pattern_db: PatternDatabase, sample_pattern: Pattern
    ) -> None:
        """Test searching patterns by category.
        
        Given: Patterns with different categories
        When: Search by specific category
        Then: Should return only matching patterns
        """
        # Store patterns with different categories
        await pattern_db.store_pattern(sample_pattern)
        
        other_pattern = Pattern(
            id="other_pattern",
            category="performance",
            name="Performance Pattern",
            description="A performance pattern",
            context={}, action={}, outcome={},
            success_rate=0.8, usage_count=0,
            created_at=datetime.now()
        )
        await pattern_db.store_pattern(other_pattern)
        
        # Search by category
        testing_patterns = await pattern_db.search_patterns({"category": "testing"})
        performance_patterns = await pattern_db.search_patterns({"category": "performance"})
        
        assert len(testing_patterns) >= 1
        assert len(performance_patterns) >= 1
        assert all(p.category == "testing" for p in testing_patterns)
        assert all(p.category == "performance" for p in performance_patterns)

    @pytest.mark.asyncio
    async def test_search_patterns_by_success_rate(
        self, pattern_db: PatternDatabase
    ) -> None:
        """Test searching patterns by minimum success rate.
        
        Given: Patterns with different success rates
        When: Search by minimum success rate
        Then: Should return only patterns meeting threshold
        """
        high_success_pattern = Pattern(
            id="high_success",
            category="test",
            name="High Success",
            description="High success pattern",
            context={}, action={}, outcome={},
            success_rate=0.95, usage_count=0,
            created_at=datetime.now()
        )
        
        low_success_pattern = Pattern(
            id="low_success",
            category="test",
            name="Low Success",
            description="Low success pattern",
            context={}, action={}, outcome={},
            success_rate=0.6, usage_count=0,
            created_at=datetime.now()
        )
        
        await pattern_db.store_pattern(high_success_pattern)
        await pattern_db.store_pattern(low_success_pattern)
        
        # Search with high threshold
        high_patterns = await pattern_db.search_patterns({"min_success_rate": 0.9})
        
        assert len(high_patterns) >= 1
        assert all(p.success_rate >= 0.9 for p in high_patterns)

    @pytest.mark.asyncio
    async def test_search_patterns_by_tags(
        self, pattern_db: PatternDatabase
    ) -> None:
        """Test searching patterns by tags.
        
        Given: Patterns with different tags
        When: Search by specific tags
        Then: Should return patterns containing any specified tag
        """
        tagged_pattern = Pattern(
            id="tagged_pattern",
            category="test",
            name="Tagged Pattern",
            description="Pattern with tags",
            context={}, action={}, outcome={},
            success_rate=0.8, usage_count=0,
            created_at=datetime.now(),
            tags=["automation", "testing", "quality"]
        )
        
        await pattern_db.store_pattern(tagged_pattern)
        
        # Search by tags
        automation_patterns = await pattern_db.search_patterns({"tags": ["automation"]})
        quality_patterns = await pattern_db.search_patterns({"tags": ["quality"]})
        
        assert len(automation_patterns) >= 1
        assert len(quality_patterns) >= 1

    @pytest.mark.asyncio
    async def test_get_all_patterns(
        self, pattern_db: PatternDatabase, sample_pattern: Pattern
    ) -> None:
        """Test retrieving all patterns.
        
        Given: Database with stored patterns
        When: get_all_patterns is called
        Then: Should return all patterns
        """
        await pattern_db.store_pattern(sample_pattern)
        
        all_patterns = await pattern_db.get_all_patterns()
        assert len(all_patterns) >= 1
        assert any(p.id == sample_pattern.id for p in all_patterns)

    @pytest.mark.asyncio
    async def test_get_patterns_by_category(
        self, pattern_db: PatternDatabase, sample_pattern: Pattern
    ) -> None:
        """Test getting patterns by category convenience method.
        
        Given: Patterns with specific category
        When: get_patterns_by_category is called
        Then: Should return patterns of that category
        """
        await pattern_db.store_pattern(sample_pattern)
        
        testing_patterns = await pattern_db.get_patterns_by_category("testing")
        assert len(testing_patterns) >= 1
        assert all(p.category == "testing" for p in testing_patterns)

    @pytest.mark.asyncio
    async def test_get_top_patterns(
        self, pattern_db: PatternDatabase
    ) -> None:
        """Test getting top patterns by usage and success rate.
        
        Given: Database with patterns
        When: get_top_patterns is called
        Then: Should return patterns sorted by quality metrics
        """
        top_patterns = await pattern_db.get_top_patterns(limit=5)
        assert len(top_patterns) <= 5
        
        # Should be sorted by success rate and usage count
        if len(top_patterns) > 1:
            for i in range(len(top_patterns) - 1):
                current = top_patterns[i]
                next_pattern = top_patterns[i + 1]
                
                # Either higher success rate or same success rate with higher usage
                assert (
                    current.success_rate >= next_pattern.success_rate
                    or (
                        current.success_rate == next_pattern.success_rate
                        and current.usage_count >= next_pattern.usage_count
                    )
                )

    @pytest.mark.asyncio
    async def test_record_pattern_usage(
        self, pattern_db: PatternDatabase, sample_pattern: Pattern
    ) -> None:
        """Test recording pattern usage analytics.
        
        Given: Stored pattern
        When: Pattern usage is recorded
        Then: Should update usage statistics
        """
        await pattern_db.store_pattern(sample_pattern)
        
        # Record successful usage
        await pattern_db.record_pattern_usage(
            pattern_id=sample_pattern.id,
            context={"task": "test_improvement"},
            success=True,
            metrics_before={"coverage": 80.0},
            metrics_after={"coverage": 85.0}
        )
        
        # Verify usage count increased
        updated_pattern = await pattern_db.get_pattern(sample_pattern.id)
        assert updated_pattern is not None
        assert updated_pattern.usage_count == sample_pattern.usage_count + 1
        assert updated_pattern.last_used is not None

    @pytest.mark.asyncio
    async def test_get_pattern_analytics(
        self, pattern_db: PatternDatabase, sample_pattern: Pattern
    ) -> None:
        """Test getting pattern analytics.
        
        Given: Pattern with usage history
        When: Analytics are requested
        Then: Should return comprehensive analytics data
        """
        await pattern_db.store_pattern(sample_pattern)
        
        # Record some usage
        await pattern_db.record_pattern_usage(
            pattern_id=sample_pattern.id,
            context={"task": "test1"},
            success=True
        )
        await pattern_db.record_pattern_usage(
            pattern_id=sample_pattern.id,
            context={"task": "test2"},
            success=False
        )
        
        analytics = await pattern_db.get_pattern_analytics(sample_pattern.id)
        
        assert "total_uses" in analytics
        assert "success_rate" in analytics
        assert "recent_uses" in analytics
        assert analytics["total_uses"] == 2
        assert analytics["success_rate"] == 0.5  # 1 success out of 2

    @pytest.mark.asyncio
    async def test_cleanup_old_patterns(self, pattern_db: PatternDatabase) -> None:
        """Test cleanup of old unused patterns.
        
        Given: Old pattern with low usage
        When: Cleanup is performed
        Then: Should remove old patterns
        """
        old_pattern = Pattern(
            id="old_pattern",
            category="test",
            name="Old Pattern",
            description="An old unused pattern",
            context={}, action={}, outcome={},
            success_rate=0.5, usage_count=1,
            created_at=datetime.now() - timedelta(days=100),
            last_used=datetime.now() - timedelta(days=100)
        )
        
        await pattern_db.store_pattern(old_pattern)
        
        # Cleanup patterns older than 50 days
        removed_count = await pattern_db.cleanup_old_patterns(days=50)
        
        assert removed_count >= 0
        
        # Verify old pattern is gone
        retrieved = await pattern_db.get_pattern("old_pattern")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_cache_integration(
        self, pattern_db: PatternDatabase, sample_pattern: Pattern
    ) -> None:
        """Test cache integration with database operations.
        
        Given: Pattern database with caching
        When: Pattern is stored and retrieved multiple times
        Then: Should use cache for subsequent retrievals
        """
        await pattern_db.store_pattern(sample_pattern)
        
        # First retrieval - from database
        pattern1 = await pattern_db.get_pattern(sample_pattern.id)
        assert pattern1 is not None
        
        # Second retrieval - should be from cache
        pattern2 = await pattern_db.get_pattern(sample_pattern.id)
        assert pattern2 is not None
        assert pattern2.id == pattern1.id

    @pytest.mark.asyncio
    async def test_predefined_patterns_loaded(self, pattern_db: PatternDatabase) -> None:
        """Test that predefined patterns are loaded during initialization.
        
        Given: Newly initialized database
        When: Database is created
        Then: Should contain predefined patterns
        """
        all_patterns = await pattern_db.get_all_patterns()
        
        # Should have at least the 50+ predefined patterns
        assert len(all_patterns) >= 50
        
        # Check for some expected predefined patterns
        pattern_ids = [p.id for p in all_patterns]
        assert "pattern_test_001" in pattern_ids
        assert "pattern_doc_001" in pattern_ids
        assert "pattern_refactor_001" in pattern_ids

    @pytest.mark.asyncio
    async def test_error_handling_storage(self, pattern_db: PatternDatabase) -> None:
        """Test error handling in storage operations.
        
        Given: Invalid pattern data
        When: Storage operations fail
        Then: Should handle errors gracefully
        """
        # Test with closed database connection
        with patch('aiosqlite.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            
            with pytest.raises(RuntimeError):
                invalid_pattern = Pattern(
                    id="invalid", category="test", name="Invalid",
                    description="Invalid pattern", context={}, action={}, outcome={},
                    success_rate=0.5, usage_count=0, created_at=datetime.now()
                )
                await pattern_db.store_pattern(invalid_pattern)

    @pytest.mark.asyncio
    async def test_concurrent_access(self, pattern_db: PatternDatabase) -> None:
        """Test concurrent database access.
        
        Given: Multiple concurrent operations
        When: Operations are performed simultaneously
        Then: Should handle concurrency correctly
        """
        patterns = []
        for i in range(5):
            pattern = Pattern(
                id=f"concurrent_{i}",
                category="test",
                name=f"Concurrent Pattern {i}",
                description=f"Pattern for concurrent test {i}",
                context={}, action={}, outcome={},
                success_rate=0.8, usage_count=0,
                created_at=datetime.now()
            )
            patterns.append(pattern)
        
        # Store patterns concurrently
        tasks = [pattern_db.store_pattern(p) for p in patterns]
        await asyncio.gather(*tasks)
        
        # Retrieve patterns concurrently
        retrieve_tasks = [pattern_db.get_pattern(p.id) for p in patterns]
        retrieved_patterns = await asyncio.gather(*retrieve_tasks)
        
        assert len(retrieved_patterns) == 5
        assert all(p is not None for p in retrieved_patterns)


class TestPatternDatabaseIntegration:
    """Integration tests for pattern database system."""

    @pytest.mark.asyncio
    async def test_full_pattern_lifecycle(self, pattern_db: PatternDatabase) -> None:
        """Test complete pattern lifecycle from creation to deletion.
        
        Given: Empty database
        When: Pattern goes through full lifecycle
        Then: All operations should work correctly
        """
        # Create pattern
        pattern = Pattern(
            id="lifecycle_test",
            category="integration",
            name="Lifecycle Test Pattern",
            description="Pattern for testing full lifecycle",
            context={"test": True},
            action={"type": "test"},
            outcome={"success": True},
            success_rate=0.85,
            usage_count=0,
            created_at=datetime.now(),
            tags=["integration", "test"]
        )
        
        # Store pattern
        await pattern_db.store_pattern(pattern)
        
        # Retrieve and verify
        retrieved = await pattern_db.get_pattern(pattern.id)
        assert retrieved is not None
        assert retrieved.id == pattern.id
        
        # Update pattern
        pattern.success_rate = 0.9
        await pattern_db.update_pattern(pattern)
        
        # Record usage
        await pattern_db.record_pattern_usage(
            pattern_id=pattern.id,
            context={"test_run": 1},
            success=True,
            metrics_before={"quality": 80},
            metrics_after={"quality": 85}
        )
        
        # Get analytics
        analytics = await pattern_db.get_pattern_analytics(pattern.id)
        assert analytics["total_uses"] == 1
        assert analytics["success_rate"] == 1.0
        
        # Search pattern
        search_results = await pattern_db.search_patterns({"category": "integration"})
        assert len(search_results) >= 1
        assert any(p.id == pattern.id for p in search_results)
        
        # Delete pattern
        deleted = await pattern_db.delete_pattern(pattern.id)
        assert deleted is True
        
        # Verify deletion
        final_check = await pattern_db.get_pattern(pattern.id)
        assert final_check is None

    @pytest.mark.asyncio
    async def test_pattern_relationships_and_search(
        self, pattern_db: PatternDatabase
    ) -> None:
        """Test complex pattern relationships and advanced search.
        
        Given: Multiple related patterns
        When: Complex searches are performed
        Then: Should return correct results
        """
        # Create related patterns
        patterns = [
            Pattern(
                id=f"related_{i}",
                category="testing" if i % 2 == 0 else "documentation",
                name=f"Related Pattern {i}",
                description=f"Pattern {i} for relationship testing",
                context={"complexity": i * 2},
                action={"type": "test" if i % 2 == 0 else "doc"},
                outcome={"improvement": i * 5},
                success_rate=0.7 + (i * 0.05),
                usage_count=i,
                created_at=datetime.now(),
                tags=["related", f"group_{i // 2}"],
                confidence=0.8 + (i * 0.02)
            )
            for i in range(6)
        ]
        
        # Store all patterns
        for pattern in patterns:
            await pattern_db.store_pattern(pattern)
        
        # Test multi-criteria search
        results = await pattern_db.search_patterns({
            "category": "testing",
            "min_success_rate": 0.75,
            "min_confidence": 0.8,
            "tags": ["related"]
        })
        
        assert len(results) >= 1
        assert all(
            p.category == "testing" and
            p.success_rate >= 0.75 and
            p.confidence >= 0.8 and
            "related" in p.tags
            for p in results
        )
        
        # Test top patterns
        top_patterns = await pattern_db.get_top_patterns(limit=3)
        assert len(top_patterns) <= 3
        
        # Verify sorting (by success rate DESC, usage count DESC)
        if len(top_patterns) > 1:
            for i in range(len(top_patterns) - 1):
                current = top_patterns[i]
                next_pattern = top_patterns[i + 1]
                assert current.success_rate >= next_pattern.success_rate

    @pytest.mark.asyncio 
    async def test_performance_with_large_dataset(
        self, pattern_db: PatternDatabase
    ) -> None:
        """Test database performance with larger dataset.
        
        Given: Large number of patterns
        When: Operations are performed
        Then: Should maintain reasonable performance
        """
        # Create many patterns
        patterns = []
        for i in range(100):
            pattern = Pattern(
                id=f"perf_test_{i:03d}",
                category=f"category_{i % 5}",
                name=f"Performance Test Pattern {i}",
                description=f"Pattern {i} for performance testing",
                context={"index": i},
                action={"type": "performance_test"},
                outcome={"result": i * 2},
                success_rate=0.5 + (i % 50) * 0.01,
                usage_count=i % 20,
                created_at=datetime.now(),
                tags=[f"perf_{i % 10}", "testing"]
            )
            patterns.append(pattern)
        
        # Batch store patterns
        import time
        start_time = time.time()
        
        tasks = [pattern_db.store_pattern(p) for p in patterns]
        await asyncio.gather(*tasks)
        
        store_time = time.time() - start_time
        
        # Test search performance
        start_time = time.time()
        search_results = await pattern_db.search_patterns({
            "min_success_rate": 0.8,
            "tags": ["testing"]
        })
        search_time = time.time() - start_time
        
        # Basic performance assertions
        assert store_time < 30.0  # Should store 100 patterns in under 30 seconds
        assert search_time < 5.0  # Should search in under 5 seconds
        assert len(search_results) > 0


# Note: Property-based testing with hypothesis would go here
# Commented out to avoid optional dependency issues