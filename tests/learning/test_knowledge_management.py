"""
Tests for Knowledge Management System

This module contains comprehensive tests for the knowledge management
components including memory curator, knowledge graph, recommendation engine,
and feedback loop systems.
"""

import os
import tempfile
from datetime import datetime, timedelta

import pytest

from packages.learning.failure_analyzer import FailureAnalyzer
from packages.learning.feedback_loop import FeedbackLoop, LearningInsight, LearningMetrics
from packages.learning.knowledge_graph import (
    GraphStorage,
    KnowledgeGraph,
    KnowledgeNode,
    KnowledgeRelationship,
    NodeType,
    RelationshipType,
)
from packages.learning.memory_curator import Memory, MemoryCurator, SQLiteStorage
from packages.learning.pattern_database import PatternDatabase
from packages.learning.recommendation_engine import (
    Recommendation,
    RecommendationEngine,
    RecommendationPriority,
    RecommendationType,
)


class TestMemory:
    """Test Memory data structure."""

    def test_memory_creation(self):
        """Test creating a memory."""
        memory = Memory(
            id="memory_001",
            type="evolution_cycle",
            timestamp=datetime.now(),
            data={"phase": "implementation", "success": True},
            metadata={"importance": 0.8, "tags": ["test"]},
        )

        assert memory.id == "memory_001"
        assert memory.type == "evolution_cycle"
        assert memory.data["success"] is True
        assert memory.get_importance() == 0.8

    def test_memory_to_dict_and_from_dict(self):
        """Test memory serialization and deserialization."""
        original = Memory(
            id="memory_002",
            type="pattern_extraction",
            timestamp=datetime.now(),
            data={"patterns": ["pattern1", "pattern2"]},
            metadata={"importance": 0.7, "tags": ["patterns"]},
            cycle_id="cycle_123",
        )

        # Serialize to dict
        memory_dict = original.to_dict()
        assert isinstance(memory_dict, dict)
        assert memory_dict["id"] == "memory_002"

        # Deserialize from dict
        restored = Memory.from_dict(memory_dict)
        assert restored.id == original.id
        assert restored.type == original.type
        assert restored.data == original.data
        assert restored.cycle_id == original.cycle_id

    def test_memory_expiration(self):
        """Test memory expiration functionality."""
        # Expired memory
        expired_memory = Memory(
            id="expired",
            type="test",
            timestamp=datetime.now(),
            data={},
            metadata={},
            expires_at=datetime.now() - timedelta(hours=1),
        )

        assert expired_memory.is_expired() is True

        # Non-expired memory
        valid_memory = Memory(
            id="valid",
            type="test",
            timestamp=datetime.now(),
            data={},
            metadata={},
            expires_at=datetime.now() + timedelta(hours=1),
        )

        assert valid_memory.is_expired() is False

    def test_memory_access_tracking(self):
        """Test memory access count tracking."""
        memory = Memory(
            id="test_access",
            type="test",
            timestamp=datetime.now(),
            data={},
            metadata={"access_count": 0},
        )

        initial_count = memory.metadata.get("access_count", 0)

        memory.increment_access_count()
        assert memory.metadata["access_count"] == initial_count + 1
        assert "last_accessed" in memory.metadata

    def test_memory_relevance_decay(self):
        """Test memory relevance decay calculation."""
        # Recent memory with access
        recent_memory = Memory(
            id="recent",
            type="test",
            timestamp=datetime.now() - timedelta(days=1),
            data={},
            metadata={"access_count": 5},
        )

        decay = recent_memory.calculate_relevance_decay()
        assert isinstance(decay, float)
        assert decay > 0.0

        # Old memory without access
        old_memory = Memory(
            id="old",
            type="test",
            timestamp=datetime.now() - timedelta(days=60),
            data={},
            metadata={"access_count": 0},
        )

        old_decay = old_memory.calculate_relevance_decay()
        assert old_decay < decay  # Should have lower relevance


class TestSQLiteStorage:
    """Test SQLite storage backend."""

    @pytest.fixture
    async def sqlite_storage(self):
        """Create temporary SQLite storage."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        storage = SQLiteStorage(db_path)
        await storage.initialize()

        yield storage

        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_storage_initialization(self, sqlite_storage):
        """Test storage initialization."""
        # Should initialize without errors
        assert sqlite_storage.db_path is not None

    @pytest.mark.asyncio
    async def test_store_and_get_memory(self, sqlite_storage):
        """Test storing and retrieving memory."""
        memory = Memory(
            id="test_store_001",
            type="test_type",
            timestamp=datetime.now(),
            data={"key": "value"},
            metadata={"importance": 0.8, "tags": ["test"]},
        )

        # Store memory
        await sqlite_storage.store_memory(memory)

        # Retrieve memory
        retrieved = await sqlite_storage.get_memory("test_store_001")

        assert retrieved is not None
        assert retrieved.id == memory.id
        assert retrieved.type == memory.type
        assert retrieved.data == memory.data

    @pytest.mark.asyncio
    async def test_update_memory(self, sqlite_storage):
        """Test updating existing memory."""
        memory = Memory(
            id="test_update_001",
            type="test_type",
            timestamp=datetime.now(),
            data={"key": "value"},
            metadata={"importance": 0.8},
        )

        # Store initial memory
        await sqlite_storage.store_memory(memory)

        # Update memory
        memory.data["updated"] = True
        memory.metadata["importance"] = 0.9
        await sqlite_storage.update_memory(memory)

        # Retrieve updated memory
        retrieved = await sqlite_storage.get_memory("test_update_001")

        assert retrieved.data["updated"] is True
        assert retrieved.metadata["importance"] == 0.9

    @pytest.mark.asyncio
    async def test_delete_memory(self, sqlite_storage):
        """Test deleting memory."""
        memory = Memory(
            id="test_delete_001", type="test_type", timestamp=datetime.now(), data={}, metadata={}
        )

        # Store memory
        await sqlite_storage.store_memory(memory)

        # Verify it exists
        retrieved = await sqlite_storage.get_memory("test_delete_001")
        assert retrieved is not None

        # Delete memory
        deleted = await sqlite_storage.delete_memory("test_delete_001")
        assert deleted is True

        # Verify it's gone
        retrieved = await sqlite_storage.get_memory("test_delete_001")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_search_memories(self, sqlite_storage):
        """Test searching memories by criteria."""
        # Store test memories
        memories = [
            Memory(
                id="search_001",
                type="type_a",
                timestamp=datetime.now(),
                data={},
                metadata={"importance": 0.8},
            ),
            Memory(
                id="search_002",
                type="type_b",
                timestamp=datetime.now(),
                data={},
                metadata={"importance": 0.6},
            ),
            Memory(
                id="search_003",
                type="type_a",
                timestamp=datetime.now(),
                data={},
                metadata={"importance": 0.9},
            ),
        ]

        for memory in memories:
            await sqlite_storage.store_memory(memory)

        # Search by type
        type_a_memories = await sqlite_storage.search_memories({"type": "type_a"})
        assert len(type_a_memories) == 2

        # Search by minimum importance
        important_memories = await sqlite_storage.search_memories({"min_importance": 0.7})
        assert len(important_memories) >= 2

    @pytest.mark.asyncio
    async def test_get_memories_by_type(self, sqlite_storage):
        """Test getting memories by specific type."""
        # Store memories of different types
        memory1 = Memory(
            id="type_test_001",
            type="evolution_cycle",
            timestamp=datetime.now(),
            data={},
            metadata={},
        )

        memory2 = Memory(
            id="type_test_002",
            type="pattern_extraction",
            timestamp=datetime.now(),
            data={},
            metadata={},
        )

        await sqlite_storage.store_memory(memory1)
        await sqlite_storage.store_memory(memory2)

        # Get by type
        evolution_memories = await sqlite_storage.get_memories_by_type("evolution_cycle")
        pattern_memories = await sqlite_storage.get_memories_by_type("pattern_extraction")

        assert len(evolution_memories) >= 1
        assert len(pattern_memories) >= 1
        assert evolution_memories[0].type == "evolution_cycle"
        assert pattern_memories[0].type == "pattern_extraction"

    @pytest.mark.asyncio
    async def test_cleanup_expired_memories(self, sqlite_storage):
        """Test cleaning up expired memories."""
        # Store expired memory
        expired_memory = Memory(
            id="expired_cleanup_001",
            type="test",
            timestamp=datetime.now(),
            data={},
            metadata={},
            expires_at=datetime.now() - timedelta(hours=1),
        )

        # Store valid memory
        valid_memory = Memory(
            id="valid_cleanup_001",
            type="test",
            timestamp=datetime.now(),
            data={},
            metadata={},
            expires_at=datetime.now() + timedelta(hours=1),
        )

        await sqlite_storage.store_memory(expired_memory)
        await sqlite_storage.store_memory(valid_memory)

        # Cleanup expired memories
        cleaned_count = await sqlite_storage.cleanup_expired_memories()

        assert cleaned_count >= 1

        # Verify expired memory is gone
        retrieved_expired = await sqlite_storage.get_memory("expired_cleanup_001")
        assert retrieved_expired is None

        # Verify valid memory remains
        retrieved_valid = await sqlite_storage.get_memory("valid_cleanup_001")
        assert retrieved_valid is not None


class TestMemoryCurator:
    """Test MemoryCurator main class."""

    @pytest.fixture
    async def memory_curator(self):
        """Create memory curator with SQLite storage."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        storage = SQLiteStorage(db_path)
        curator = MemoryCurator(storage)
        await curator.initialize()

        yield curator

        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_curator_initialization(self, memory_curator):
        """Test memory curator initialization."""
        assert memory_curator.storage is not None
        assert memory_curator.retention_policy is not None

    @pytest.mark.asyncio
    async def test_store_and_get_memory(self, memory_curator):
        """Test storing and retrieving memory via curator."""
        memory = Memory(
            id="curator_test_001",
            type="test_memory",
            timestamp=datetime.now(),
            data={"test": "data"},
            metadata={"importance": 0.8, "tags": ["test"]},
        )

        # Store memory
        await memory_curator.store_memory(memory)

        # Retrieve memory
        retrieved = await memory_curator.get_memory("curator_test_001")

        assert retrieved is not None
        assert retrieved.id == memory.id
        assert retrieved.data == memory.data

    @pytest.mark.asyncio
    async def test_store_evolution_cycle_memory(self, memory_curator):
        """Test storing evolution cycle memory."""
        memory = await memory_curator.store_evolution_cycle_memory(
            cycle_id="cycle_123",
            phase="implementation",
            task="add_tests",
            inputs={"file": "test.py"},
            outputs={"tests": 5},
            duration=45.0,
            success=True,
            metrics_before={"coverage": 70.0},
            metrics_after={"coverage": 85.0},
            patterns_used=["pattern_001"],
            new_patterns=["pattern_002"],
        )

        assert memory is not None
        assert memory.type == "evolution_cycle"
        assert memory.cycle_id == "cycle_123"
        assert memory.data["success"] is True
        assert memory.data["duration"] == 45.0

    @pytest.mark.asyncio
    async def test_store_pattern_extraction_memory(self, memory_curator):
        """Test storing pattern extraction memory."""
        memory = await memory_curator.store_pattern_extraction_memory(
            source_cycle="cycle_456",
            extracted_patterns=["pattern_003", "pattern_004"],
            confidence_scores={"pattern_003": 0.8, "pattern_004": 0.9},
            extraction_method="ast_analysis",
        )

        assert memory is not None
        assert memory.type == "pattern_extraction"
        assert memory.data["source_cycle"] == "cycle_456"
        assert len(memory.data["extracted_patterns"]) == 2
        assert memory.data["extraction_method"] == "ast_analysis"

    @pytest.mark.asyncio
    async def test_store_performance_metric_memory(self, memory_curator):
        """Test storing performance metric memory."""
        memory = await memory_curator.store_performance_metric_memory(
            metric_name="test_coverage",
            value=85.0,
            baseline=70.0,
            improvement=0.214,  # 21.4% improvement
            measurement_context={"phase": "testing"},
        )

        assert memory is not None
        assert memory.type == "performance_metric"
        assert memory.data["metric_name"] == "test_coverage"
        assert memory.data["value"] == 85.0
        assert memory.data["improvement"] == 0.214

    @pytest.mark.asyncio
    async def test_search_memories(self, memory_curator):
        """Test searching memories via curator."""
        # Store test memories
        await memory_curator.store_memory(
            Memory(
                id="search_curator_001",
                type="evolution_cycle",
                timestamp=datetime.now(),
                data={"phase": "implementation"},
                metadata={"importance": 0.8, "tags": ["test"]},
            )
        )

        await memory_curator.store_memory(
            Memory(
                id="search_curator_002",
                type="pattern_extraction",
                timestamp=datetime.now(),
                data={"method": "ast"},
                metadata={"importance": 0.7, "tags": ["patterns"]},
            )
        )

        # Search by type
        evolution_memories = await memory_curator.search_memories({"type": "evolution_cycle"})
        assert len(evolution_memories) >= 1

        # Search by tags
        pattern_memories = await memory_curator.search_memories({"tags": ["patterns"]})
        assert len(pattern_memories) >= 1

    @pytest.mark.asyncio
    async def test_get_recent_memories(self, memory_curator):
        """Test getting recent memories."""
        # Store memories at different times
        old_memory = Memory(
            id="old_memory_001",
            type="test",
            timestamp=datetime.now() - timedelta(days=2),
            data={},
            metadata={},
        )

        recent_memory = Memory(
            id="recent_memory_001",
            type="test",
            timestamp=datetime.now() - timedelta(hours=1),
            data={},
            metadata={},
        )

        await memory_curator.store_memory(old_memory)
        await memory_curator.store_memory(recent_memory)

        # Get memories from last 24 hours
        recent_memories = await memory_curator.get_recent_memories(hours=24)

        # Should include recent but not old memory
        recent_ids = [m.id for m in recent_memories]
        assert "recent_memory_001" in recent_ids

    @pytest.mark.asyncio
    async def test_cleanup_old_memories(self, memory_curator):
        """Test cleaning up old memories."""
        # Store old memory with low retention score
        old_memory = Memory(
            id="cleanup_old_001",
            type="test",
            timestamp=datetime.now() - timedelta(days=100),
            data={},
            metadata={"importance": 0.2, "retention_score": 0.1},
        )

        # Store important memory that shouldn't be cleaned
        important_memory = Memory(
            id="cleanup_important_001",
            type="test",
            timestamp=datetime.now() - timedelta(days=100),
            data={},
            metadata={"importance": 0.9, "retention_score": 0.8},
        )

        await memory_curator.store_memory(old_memory)
        await memory_curator.store_memory(important_memory)

        # Cleanup memories older than 30 days
        cleaned_count = await memory_curator.cleanup_old_memories(days=30)

        # Should clean some memories
        assert cleaned_count >= 0

    @pytest.mark.asyncio
    async def test_get_memory_statistics(self, memory_curator):
        """Test getting memory statistics."""
        # Store some test memories
        for i in range(3):
            await memory_curator.store_memory(
                Memory(
                    id=f"stats_test_{i}",
                    type="evolution_cycle" if i % 2 == 0 else "pattern_extraction",
                    timestamp=datetime.now(),
                    data={},
                    metadata={},
                )
            )

        stats = await memory_curator.get_memory_statistics()

        assert isinstance(stats, dict)
        assert "total_memories" in stats
        assert "type_counts" in stats
        assert "cache_hit_rate" in stats
        assert stats["total_memories"] >= 3


class TestKnowledgeNode:
    """Test KnowledgeNode data structure."""

    def test_knowledge_node_creation(self):
        """Test creating a knowledge node."""
        node = KnowledgeNode(
            id="node_001",
            type=NodeType.PATTERN,
            label="Test Pattern",
            properties={"category": "testing", "success_rate": 0.8},
            created_at=datetime.now(),
            last_updated=datetime.now(),
            importance=0.7,
            tags=["pattern", "testing"],
        )

        assert node.id == "node_001"
        assert node.type == NodeType.PATTERN
        assert node.label == "Test Pattern"
        assert node.importance == 0.7
        assert "testing" in node.tags

    def test_knowledge_node_serialization(self):
        """Test node serialization and deserialization."""
        original = KnowledgeNode(
            id="node_002",
            type=NodeType.FAILURE,
            label="Test Failure",
            properties={"severity": "high"},
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )

        # Serialize
        node_dict = original.to_dict()
        assert isinstance(node_dict, dict)
        assert node_dict["id"] == "node_002"
        assert node_dict["type"] == "failure"

        # Deserialize
        restored = KnowledgeNode.from_dict(node_dict)
        assert restored.id == original.id
        assert restored.type == original.type
        assert restored.label == original.label


class TestKnowledgeRelationship:
    """Test KnowledgeRelationship data structure."""

    def test_knowledge_relationship_creation(self):
        """Test creating a knowledge relationship."""
        relationship = KnowledgeRelationship(
            id="rel_001",
            source_id="node_001",
            target_id="node_002",
            type=RelationshipType.CAUSES,
            strength=0.8,
            properties={"context": "testing"},
            created_at=datetime.now(),
            confidence=0.9,
        )

        assert relationship.id == "rel_001"
        assert relationship.source_id == "node_001"
        assert relationship.target_id == "node_002"
        assert relationship.type == RelationshipType.CAUSES
        assert relationship.strength == 0.8
        assert relationship.confidence == 0.9

    def test_knowledge_relationship_serialization(self):
        """Test relationship serialization."""
        original = KnowledgeRelationship(
            id="rel_002",
            source_id="node_003",
            target_id="node_004",
            type=RelationshipType.IMPROVES,
            strength=0.7,
            properties={},
            created_at=datetime.now(),
        )

        # Serialize
        rel_dict = original.to_dict()
        assert isinstance(rel_dict, dict)
        assert rel_dict["type"] == "improves"

        # Deserialize
        restored = KnowledgeRelationship.from_dict(rel_dict)
        assert restored.id == original.id
        assert restored.type == original.type
        assert restored.strength == original.strength


class TestKnowledgeGraph:
    """Test KnowledgeGraph main class."""

    @pytest.fixture
    async def knowledge_graph(self):
        """Create knowledge graph with temporary storage."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        storage = GraphStorage(db_path)
        graph = KnowledgeGraph(storage)
        await graph.initialize()

        yield graph

        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_graph_initialization(self, knowledge_graph):
        """Test knowledge graph initialization."""
        assert knowledge_graph.storage is not None
        assert knowledge_graph.analyzer is not None

    @pytest.mark.asyncio
    async def test_add_node(self, knowledge_graph):
        """Test adding a node to the graph."""
        node = KnowledgeNode(
            id="test_node_001",
            type=NodeType.PATTERN,
            label="Test Pattern Node",
            properties={"category": "testing"},
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )

        await knowledge_graph.add_node(node)

        # Verify node was added
        retrieved = await knowledge_graph.get_node("test_node_001")
        assert retrieved is not None
        assert retrieved.id == node.id
        assert retrieved.label == node.label

    @pytest.mark.asyncio
    async def test_add_relationship(self, knowledge_graph):
        """Test adding a relationship between nodes."""
        # First add nodes
        node1 = KnowledgeNode(
            id="rel_test_node_001",
            type=NodeType.PATTERN,
            label="Pattern Node",
            properties={},
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )

        node2 = KnowledgeNode(
            id="rel_test_node_002",
            type=NodeType.FAILURE,
            label="Failure Node",
            properties={},
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )

        await knowledge_graph.add_node(node1)
        await knowledge_graph.add_node(node2)

        # Add relationship
        relationship = await knowledge_graph.add_relationship(
            source_id="rel_test_node_001",
            target_id="rel_test_node_002",
            relationship_type=RelationshipType.PREVENTS,
            strength=0.8,
            confidence=0.9,
        )

        assert relationship is not None
        assert relationship.source_id == "rel_test_node_001"
        assert relationship.target_id == "rel_test_node_002"
        assert relationship.type == RelationshipType.PREVENTS

    @pytest.mark.asyncio
    async def test_find_related_nodes(self, knowledge_graph):
        """Test finding related nodes."""
        # Create a small graph structure
        nodes = [
            KnowledgeNode(
                id=f"related_test_node_{i}",
                type=NodeType.PATTERN,
                label=f"Node {i}",
                properties={},
                created_at=datetime.now(),
                last_updated=datetime.now(),
            )
            for i in range(3)
        ]

        for node in nodes:
            await knowledge_graph.add_node(node)

        # Add relationships
        await knowledge_graph.add_relationship(
            "related_test_node_0", "related_test_node_1", RelationshipType.LEADS_TO, 0.8
        )
        await knowledge_graph.add_relationship(
            "related_test_node_1", "related_test_node_2", RelationshipType.IMPROVES, 0.7
        )

        # Find related nodes
        related = await knowledge_graph.find_related_nodes("related_test_node_0", max_depth=2)

        assert isinstance(related, list)
        # Should find nodes connected within max_depth

    @pytest.mark.asyncio
    async def test_get_graph_statistics(self, knowledge_graph):
        """Test getting graph statistics."""
        # Add some nodes and relationships
        for i in range(3):
            node = KnowledgeNode(
                id=f"stats_node_{i}",
                type=NodeType.PATTERN,
                label=f"Stats Node {i}",
                properties={},
                created_at=datetime.now(),
                last_updated=datetime.now(),
            )
            await knowledge_graph.add_node(node)

        stats = await knowledge_graph.get_graph_statistics()

        assert isinstance(stats, dict)
        assert "total_nodes" in stats
        assert "total_relationships" in stats
        assert "node_types" in stats
        assert stats["total_nodes"] >= 3

    @pytest.mark.asyncio
    async def test_create_pattern_node(self, knowledge_graph):
        """Test creating a pattern node."""
        pattern_data = {
            "name": "Test Pattern",
            "category": "testing",
            "success_rate": 0.85,
            "usage_count": 10,
            "confidence": 0.9,
        }

        node = await knowledge_graph.create_pattern_node("pattern_123", pattern_data)

        assert node.type == NodeType.PATTERN
        assert node.label == "Test Pattern"
        assert node.properties["category"] == "testing"
        assert node.properties["success_rate"] == 0.85

    @pytest.mark.asyncio
    async def test_create_failure_node(self, knowledge_graph):
        """Test creating a failure node."""
        failure_data = {
            "signature": "ImportError: module not found",
            "category": "dependency_error",
            "severity": "high",
            "frequency": 5,
            "root_cause": "Missing dependency",
        }

        node = await knowledge_graph.create_failure_node("failure_456", failure_data)

        assert node.type == NodeType.FAILURE
        assert node.label == "ImportError: module not found"
        assert node.properties["category"] == "dependency_error"
        assert node.properties["severity"] == "high"


class TestRecommendation:
    """Test Recommendation data structure."""

    def test_recommendation_creation(self):
        """Test creating a recommendation."""
        recommendation = Recommendation(
            id="rec_001",
            type=RecommendationType.PATTERN_APPLICATION,
            priority=RecommendationPriority.HIGH,
            title="Apply Test Pattern",
            description="Apply the test pattern to improve coverage",
            context={"file_types": ["python"]},
            action={"type": "add_tests"},
            expected_outcome={"coverage_improvement": 15},
            confidence=0.8,
            reasoning="Pattern has high success rate",
            supporting_evidence=["85% success rate", "Used 10 times"],
            estimated_effort="Medium",
            estimated_impact="High",
        )

        assert recommendation.id == "rec_001"
        assert recommendation.type == RecommendationType.PATTERN_APPLICATION
        assert recommendation.priority == RecommendationPriority.HIGH
        assert recommendation.confidence == 0.8

    def test_recommendation_serialization(self):
        """Test recommendation serialization."""
        original = Recommendation(
            id="rec_002",
            type=RecommendationType.TESTING,
            priority=RecommendationPriority.MEDIUM,
            title="Add Unit Tests",
            description="Add comprehensive unit tests",
            context={},
            action={},
            expected_outcome={},
            confidence=0.7,
            reasoning="Tests needed",
            supporting_evidence=[],
            estimated_effort="Low",
            estimated_impact="Medium",
        )

        # Serialize
        rec_dict = original.to_dict()
        assert isinstance(rec_dict, dict)
        assert rec_dict["type"] == "testing"

        # Deserialize
        restored = Recommendation.from_dict(rec_dict)
        assert restored.id == original.id
        assert restored.type == original.type

    def test_recommendation_expiration(self):
        """Test recommendation expiration."""
        # Expired recommendation
        expired_rec = Recommendation(
            id="expired_rec",
            type=RecommendationType.OPTIMIZATION,
            priority=RecommendationPriority.LOW,
            title="Expired",
            description="Expired recommendation",
            context={},
            action={},
            expected_outcome={},
            confidence=0.5,
            reasoning="Test",
            supporting_evidence=[],
            estimated_effort="Low",
            estimated_impact="Low",
            expires_at=datetime.now() - timedelta(hours=1),
        )

        assert expired_rec.is_expired() is True

    def test_recommendation_urgency_score(self):
        """Test recommendation urgency score calculation."""
        # High priority, near expiration
        urgent_rec = Recommendation(
            id="urgent_rec",
            type=RecommendationType.SECURITY,
            priority=RecommendationPriority.CRITICAL,
            title="Security Fix",
            description="Critical security fix needed",
            context={},
            action={},
            expected_outcome={},
            confidence=0.9,
            reasoning="Security vulnerability",
            supporting_evidence=[],
            estimated_effort="High",
            estimated_impact="Critical",
            expires_at=datetime.now() + timedelta(hours=1),  # Soon to expire
        )

        urgency = urgent_rec.get_urgency_score()
        assert isinstance(urgency, float)
        assert urgency > 0.5  # Should be urgent


class TestLearningMetrics:
    """Test LearningMetrics data structure."""

    def test_learning_metrics_creation(self):
        """Test creating learning metrics."""
        metrics = LearningMetrics(
            timestamp=datetime.now(),
            pattern_effectiveness=0.8,
            failure_reduction_rate=0.7,
            recommendation_accuracy=0.85,
            cycle_efficiency=0.75,
            knowledge_growth_rate=0.6,
            memory_retention_score=0.8,
            system_performance_score=0.78,
            improvement_velocity=0.05,
            learning_velocity=0.03,
        )

        assert metrics.pattern_effectiveness == 0.8
        assert metrics.failure_reduction_rate == 0.7
        assert metrics.recommendation_accuracy == 0.85

    def test_learning_metrics_overall_score(self):
        """Test overall score calculation."""
        metrics = LearningMetrics(
            timestamp=datetime.now(),
            pattern_effectiveness=0.8,
            failure_reduction_rate=0.7,
            recommendation_accuracy=0.9,
            cycle_efficiency=0.8,
            knowledge_growth_rate=0.6,
            memory_retention_score=0.75,
            system_performance_score=0.8,
            improvement_velocity=0.05,
        )

        overall_score = metrics.get_overall_score()
        assert isinstance(overall_score, float)
        assert 0.0 <= overall_score <= 1.0

    def test_learning_metrics_serialization(self):
        """Test metrics serialization."""
        original = LearningMetrics(
            timestamp=datetime.now(), pattern_effectiveness=0.8, failure_reduction_rate=0.7
        )

        # Serialize
        metrics_dict = original.to_dict()
        assert isinstance(metrics_dict, dict)
        assert "timestamp" in metrics_dict

        # Deserialize
        restored = LearningMetrics.from_dict(metrics_dict)
        assert restored.pattern_effectiveness == original.pattern_effectiveness
        assert restored.failure_reduction_rate == original.failure_reduction_rate


class TestLearningInsight:
    """Test LearningInsight data structure."""

    def test_learning_insight_creation(self):
        """Test creating a learning insight."""
        insight = LearningInsight(
            id="insight_001",
            type="performance_issue",
            title="Low Pattern Effectiveness",
            description="Pattern effectiveness is below target",
            impact=0.8,
            confidence=0.9,
            supporting_data={"metric": "pattern_effectiveness", "value": 0.6},
            recommended_actions=["Review pattern selection", "Update patterns"],
            priority="high",
        )

        assert insight.id == "insight_001"
        assert insight.type == "performance_issue"
        assert insight.impact == 0.8
        assert insight.confidence == 0.9
        assert insight.priority == "high"

    def test_learning_insight_serialization(self):
        """Test insight serialization."""
        original = LearningInsight(
            id="insight_002",
            type="trend_analysis",
            title="Improving Metrics",
            description="Metrics are trending upward",
            impact=0.6,
            confidence=0.8,
            supporting_data={},
            recommended_actions=[],
        )

        insight_dict = original.to_dict()
        assert isinstance(insight_dict, dict)
        assert insight_dict["id"] == "insight_002"
        assert insight_dict["type"] == "trend_analysis"


@pytest.mark.asyncio
async def test_knowledge_management_integration():
    """Integration test for knowledge management components."""
    # Create temporary databases
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as memory_tmp:
        memory_db_path = memory_tmp.name
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as graph_tmp:
        graph_db_path = graph_tmp.name
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as pattern_tmp:
        pattern_db_path = pattern_tmp.name

    try:
        # Initialize components
        memory_storage = SQLiteStorage(memory_db_path)
        memory_curator = MemoryCurator(memory_storage)
        await memory_curator.initialize()

        graph_storage = GraphStorage(graph_db_path)
        knowledge_graph = KnowledgeGraph(graph_storage)
        await knowledge_graph.initialize()

        pattern_db = PatternDatabase(pattern_db_path)
        await pattern_db.initialize()

        failure_analyzer = FailureAnalyzer()
        await failure_analyzer.initialize()

        recommendation_engine = RecommendationEngine(pattern_db, knowledge_graph, memory_curator)
        await recommendation_engine.initialize()

        feedback_loop = FeedbackLoop(
            pattern_db, failure_analyzer, memory_curator, knowledge_graph, recommendation_engine
        )
        await feedback_loop.initialize()

        # Test basic workflow

        # 1. Store some memories
        evolution_memory = await memory_curator.store_evolution_cycle_memory(
            cycle_id="integration_cycle_001",
            phase="implementation",
            task="add_tests",
            inputs={"file": "test.py"},
            outputs={"tests": 5},
            duration=45.0,
            success=True,
            metrics_before={"coverage": 70.0},
            metrics_after={"coverage": 85.0},
        )

        # 2. Add knowledge graph nodes
        pattern_node = await knowledge_graph.create_pattern_node(
            "integration_pattern_001",
            {
                "name": "Test Addition Pattern",
                "category": "testing",
                "success_rate": 0.9,
                "usage_count": 15,
                "confidence": 0.95,
            },
        )

        # 3. Measure learning effectiveness
        metrics = await feedback_loop.measure_learning_effectiveness()
        assert isinstance(metrics, LearningMetrics)
        assert metrics.get_overall_score() >= 0.0

        # 4. Generate insights
        insights = await feedback_loop.generate_insights()
        assert isinstance(insights, list)

        # 5. Get recommendations
        context = {"phase": "implementation", "task": "improve_tests", "file_types": ["python"]}

        recommendations = await recommendation_engine.get_recommendations(context)
        assert isinstance(recommendations, list)

        # 6. Get learning dashboard
        dashboard = await feedback_loop.get_learning_dashboard()
        assert isinstance(dashboard, dict)
        assert "current_metrics" in dashboard
        assert "overall_score" in dashboard

        print("Integration test completed successfully!")

    finally:
        # Cleanup
        for db_path in [memory_db_path, graph_db_path, pattern_db_path]:
            if os.path.exists(db_path):
                os.unlink(db_path)
