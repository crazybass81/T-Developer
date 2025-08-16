"""
Integration tests for Phase 7 - Learning & Intelligence System.

This module tests the complete integration of all Phase 7 components
including pattern recognition, knowledge graph, memory curation,
and the learning feedback loop.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Learning system imports
from packages.learning.failure_analyzer import FailureAnalyzer
from packages.learning.feedback_loop import FeedbackLoop
from packages.learning.knowledge_graph import KnowledgeGraph
from packages.learning.learning_integration import LearningIntegration
from packages.learning.memory_curator import Memory, MemoryCurator
from packages.learning.pattern_database import Pattern, PatternDatabase
from packages.learning.pattern_recognition import PatternRecognizer
from packages.learning.recommendation_engine import RecommendationEngine

# Agent imports for integration
from packages.agents.planner import PlannerAgent
from packages.agents.refactor import RefactorAgent
from packages.runtime.agentcore import AgentCore


class TestPhase7Integration:
    """Integration tests for Phase 7 Learning & Intelligence System."""

    @pytest.fixture
    async def learning_system(self, tmp_path):
        """Create complete learning system for integration testing."""
        # Initialize databases
        pattern_db = PatternDatabase(str(tmp_path / "patterns.db"))
        await pattern_db.initialize()

        # Initialize components
        memory_curator = MemoryCurator(
            max_memories=1000,
            retention_days=30,
            importance_threshold=0.3
        )
        await memory_curator.initialize()

        knowledge_graph = KnowledgeGraph()
        await knowledge_graph.initialize()

        failure_analyzer = FailureAnalyzer(pattern_db)
        
        pattern_recognizer = PatternRecognizer(pattern_db)
        
        recommendation_engine = RecommendationEngine(
            pattern_db=pattern_db,
            memory_curator=memory_curator
        )
        
        feedback_loop = FeedbackLoop(
            pattern_db=pattern_db,
            memory_curator=memory_curator,
            knowledge_graph=knowledge_graph
        )

        # Create integrated system
        learning_integration = LearningIntegration(
            pattern_recognizer=pattern_recognizer,
            failure_analyzer=failure_analyzer,
            memory_curator=memory_curator,
            knowledge_graph=knowledge_graph,
            recommendation_engine=recommendation_engine,
            feedback_loop=feedback_loop
        )
        
        await learning_integration.initialize()
        
        return {
            "integration": learning_integration,
            "pattern_db": pattern_db,
            "memory_curator": memory_curator,
            "knowledge_graph": knowledge_graph,
            "failure_analyzer": failure_analyzer,
            "feedback_loop": feedback_loop
        }

    @pytest.mark.asyncio
    async def test_complete_learning_cycle(self, learning_system):
        """Test complete learning cycle from evolution to pattern extraction."""
        integration = learning_system["integration"]
        pattern_db = learning_system["pattern_db"]
        
        # Simulate an evolution cycle
        evolution_result = {
            "id": "cycle_001",
            "phase": "refactoring",
            "success": True,
            "changes": {
                "files_modified": 5,
                "lines_added": 150,
                "lines_removed": 75
            },
            "metrics": {
                "docstring_coverage": {"before": 0.7, "after": 0.85},
                "test_coverage": {"before": 0.8, "after": 0.9},
                "complexity": {"before": 12, "after": 8}
            },
            "duration": 120,
            "agent": "RefactorAgent"
        }
        
        # Process evolution feedback
        feedback_result = await learning_system["feedback_loop"].process_evolution_feedback(
            evolution_result
        )
        
        assert feedback_result["status"] == "processed"
        assert "pattern_extracted" in feedback_result
        
        # Verify pattern was stored
        patterns = await pattern_db.search_patterns({"category": "improvement"})
        assert len(patterns) > 0
        
        # Verify memory was created
        memories = await learning_system["memory_curator"].search_memories(
            {"type": "evolution_cycle"}
        )
        assert len(memories) > 0

    @pytest.mark.asyncio
    async def test_failure_analysis_integration(self, learning_system):
        """Test failure analysis and prevention recommendation flow."""
        integration = learning_system["integration"]
        failure_analyzer = learning_system["failure_analyzer"]
        
        # Simulate a failure
        failure_data = {
            "id": "failure_001",
            "type": "test_failure",
            "error": "AssertionError: Expected 100, got 95",
            "context": {
                "test_name": "test_performance_metric",
                "module": "packages.performance.optimizer",
                "line": 245
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Analyze failure
        analysis = await failure_analyzer.analyze_failure(failure_data)
        
        assert analysis is not None
        assert "root_causes" in analysis
        assert "prevention_strategies" in analysis
        
        # Get prevention recommendations
        plan_data = {
            "tasks": [
                {
                    "id": "task_001",
                    "name": "Optimize performance module",
                    "category": "optimization"
                }
            ]
        }
        
        risk_assessments = await integration.plan_analyzer.assess_plan_risks(plan_data)
        
        assert len(risk_assessments) > 0
        assert risk_assessments[0].mitigation_strategies

    @pytest.mark.asyncio
    async def test_knowledge_graph_evolution(self, learning_system):
        """Test knowledge graph building and querying."""
        knowledge_graph = learning_system["knowledge_graph"]
        
        # Add knowledge from multiple evolution cycles
        for i in range(5):
            node = await knowledge_graph.add_node(
                id=f"pattern_{i}",
                label=f"Pattern {i}",
                type="pattern",
                properties={
                    "success_rate": 0.8 + (i * 0.02),
                    "usage_count": 10 + i,
                    "category": "optimization" if i % 2 == 0 else "refactoring"
                }
            )
            
            # Create relationships
            if i > 0:
                await knowledge_graph.add_edge(
                    source_id=f"pattern_{i-1}",
                    target_id=f"pattern_{i}",
                    relationship="evolves_to",
                    properties={"confidence": 0.7 + (i * 0.05)}
                )
        
        # Query for optimization patterns
        query = {
            "node_criteria": {
                "type": "pattern",
                "min_importance": 0.5
            },
            "relationship_filter": "evolves_to",
            "limit": 3
        }
        
        results = await knowledge_graph.query_graph(query)
        
        assert len(results) > 0
        assert results[0].type == "pattern"
        
        # Test path finding
        path = await knowledge_graph.find_path("pattern_0", "pattern_4")
        assert path is not None
        assert len(path) == 5  # 5 nodes in path from 0 to 4

    @pytest.mark.asyncio
    async def test_pattern_recognition_flow(self, learning_system):
        """Test pattern recognition and application recommendation."""
        pattern_recognizer = learning_system["integration"].pattern_recognizer
        pattern_db = learning_system["pattern_db"]
        
        # Create successful patterns
        for i in range(3):
            pattern = Pattern(
                id=f"success_pattern_{i}",
                name=f"Successful Pattern {i}",
                category="improvement",
                context={"file_type": "python", "complexity": "high"},
                action={"type": "refactor", "approach": f"approach_{i}"},
                outcome={"metrics_improved": True, "by_percentage": 15 + i * 5},
                success_rate=0.85 + i * 0.05,
                usage_count=20 + i * 10,
                confidence=0.8 + i * 0.05,
                created_at=datetime.now(),
                last_used=datetime.now()
            )
            await pattern_db.store_pattern(pattern)
        
        # Test pattern recognition for new context
        new_context = {
            "file_type": "python",
            "complexity": "high",
            "current_metrics": {
                "coverage": 0.7,
                "complexity": 15
            }
        }
        
        # Find applicable patterns
        applicable = await pattern_recognizer.find_applicable_patterns(
            new_context,
            min_confidence=0.7
        )
        
        assert len(applicable) > 0
        assert applicable[0].success_rate >= 0.85
        
        # Test pattern matching
        matches = await pattern_recognizer.match_patterns(
            {"type": "refactor"},
            new_context
        )
        
        assert len(matches) > 0

    @pytest.mark.asyncio
    async def test_recommendation_engine_integration(self, learning_system):
        """Test recommendation engine with learning system."""
        recommendation_engine = learning_system["integration"].recommendation_engine
        
        # Create context for recommendations
        context = {
            "phase": "planning",
            "goal": "improve_test_coverage",
            "current_metrics": {
                "test_coverage": 0.75,
                "docstring_coverage": 0.80
            },
            "constraints": {
                "time_limit_hours": 4,
                "max_files_to_modify": 10
            }
        }
        
        # Get recommendations
        recommendations = await recommendation_engine.get_recommendations(
            context,
            limit=5
        )
        
        assert len(recommendations) > 0
        assert recommendations[0].confidence > 0
        assert recommendations[0].priority in ["HIGH", "MEDIUM", "LOW"]
        
        # Test recommendation learning
        feedback = {
            "recommendation_id": recommendations[0].id,
            "applied": True,
            "success": True,
            "actual_outcome": {
                "test_coverage": 0.85,
                "time_taken_hours": 3
            }
        }
        
        await recommendation_engine.process_feedback(
            recommendations[0].id,
            feedback
        )
        
        # Verify feedback was incorporated
        updated_recs = await recommendation_engine.get_recommendations(
            context,
            limit=5
        )
        
        # Should adjust confidence based on feedback
        assert updated_recs[0].confidence != recommendations[0].confidence

    @pytest.mark.asyncio
    async def test_memory_curation_lifecycle(self, learning_system):
        """Test memory storage, retrieval, and pruning."""
        memory_curator = learning_system["memory_curator"]
        
        # Store various types of memories
        memory_types = ["evolution_cycle", "failure", "success_pattern", "optimization"]
        
        for i, mem_type in enumerate(memory_types):
            memory = Memory(
                id=f"memory_{mem_type}_{i}",
                type=mem_type,
                timestamp=datetime.now() - timedelta(days=i),
                data={
                    "result": "success" if i % 2 == 0 else "failure",
                    "metrics": {"improvement": 0.1 * (i + 1)}
                },
                metadata={
                    "importance": 0.5 + (i * 0.1),
                    "tags": [mem_type, "test"],
                    "retention_score": 0.6 + (i * 0.05)
                }
            )
            await memory_curator.store_memory(memory)
        
        # Test memory search
        evolution_memories = await memory_curator.search_memories(
            {"type": "evolution_cycle"}
        )
        assert len(evolution_memories) > 0
        
        # Test memory consolidation
        await memory_curator.consolidate_memories()
        
        # Test memory retrieval by importance
        important_memories = await memory_curator.get_important_memories(
            min_importance=0.7
        )
        assert all(m.metadata["importance"] >= 0.7 for m in important_memories)
        
        # Test memory pruning
        initial_count = await memory_curator.get_memory_count()
        await memory_curator.prune_old_memories(days=30)
        final_count = await memory_curator.get_memory_count()
        
        assert final_count <= initial_count

    @pytest.mark.asyncio
    async def test_plan_enhancement_with_learning(self, learning_system):
        """Test plan enhancement using learned patterns and insights."""
        integration = learning_system["integration"]
        
        # Create a basic plan
        original_plan = {
            "id": "plan_001",
            "goal": "Improve code quality",
            "tasks": [
                {
                    "id": "task_1",
                    "name": "Add docstrings",
                    "category": "documentation",
                    "estimated_hours": 2
                },
                {
                    "id": "task_2",
                    "name": "Refactor complex functions",
                    "category": "refactoring",
                    "estimated_hours": 4
                },
                {
                    "id": "task_3",
                    "name": "Add unit tests",
                    "category": "testing",
                    "estimated_hours": 3
                }
            ]
        }
        
        # Enhance plan with learning
        enhanced_plan = await integration.enhance_plan(original_plan)
        
        assert "learning_enhancements" in enhanced_plan
        assert "efficiency_insights" in enhanced_plan["learning_enhancements"]
        assert "risk_assessments" in enhanced_plan["learning_enhancements"]
        assert "optimizations_applied" in enhanced_plan["learning_enhancements"]
        
        # Verify optimizations were applied
        if enhanced_plan["learning_enhancements"]["optimizations_applied"]:
            opt = enhanced_plan["learning_enhancements"]["optimizations_applied"][0]
            assert "confidence" in opt
            assert "impact" in opt

    @pytest.mark.asyncio
    async def test_continuous_learning_feedback(self, learning_system):
        """Test continuous learning through feedback loops."""
        feedback_loop = learning_system["feedback_loop"]
        
        # Simulate multiple evolution cycles
        for i in range(3):
            result = {
                "cycle_id": f"cycle_{i}",
                "success": i != 1,  # Second cycle fails
                "metrics_delta": {
                    "coverage": 0.05 * (i + 1) if i != 1 else -0.02,
                    "complexity": -2 * (i + 1) if i != 1 else 3
                },
                "patterns_applied": [f"pattern_{j}" for j in range(i)],
                "duration": 60 + (i * 30)
            }
            
            feedback = await feedback_loop.process_evolution_feedback(result)
            
            assert feedback["status"] == "processed"
            
            # Failed cycle should trigger failure analysis
            if not result["success"]:
                assert "failure_analysis" in feedback
        
        # Measure learning effectiveness
        effectiveness = await feedback_loop.measure_learning_effectiveness()
        
        assert effectiveness.success_rate >= 0  # Should have some success rate
        assert effectiveness.total_cycles == 3
        assert effectiveness.patterns_discovered >= 0

    @pytest.mark.asyncio
    async def test_cross_component_integration(self, learning_system):
        """Test integration between all Phase 7 components."""
        integration = learning_system["integration"]
        
        # Create comprehensive test scenario
        
        # 1. Store initial patterns and memories
        pattern = Pattern(
            id="integrated_pattern",
            name="Integration Test Pattern",
            category="optimization",
            context={"applicable_to": "all"},
            action={"optimize": True},
            outcome={"expected_improvement": 0.2},
            success_rate=0.9,
            usage_count=10,
            confidence=0.85,
            created_at=datetime.now(),
            last_used=datetime.now()
        )
        await learning_system["pattern_db"].store_pattern(pattern)
        
        # 2. Add to knowledge graph
        await learning_system["knowledge_graph"].add_node(
            id="integrated_pattern",
            label="Integration Pattern",
            type="pattern",
            properties={"success_rate": 0.9}
        )
        
        # 3. Create memory
        memory = Memory(
            id="integrated_memory",
            type="pattern_application",
            timestamp=datetime.now(),
            data={"pattern_id": "integrated_pattern", "result": "success"},
            metadata={"importance": 0.8, "tags": ["integration"], "retention_score": 0.9}
        )
        await learning_system["memory_curator"].store_memory(memory)
        
        # 4. Get comprehensive insights
        plan_context = {
            "tasks": [{"id": "t1", "category": "optimization", "name": "Optimize code"}]
        }
        
        insights = await integration.get_learning_insights(plan_context)
        
        assert "learning_metrics" in insights
        assert "efficiency_insights" in insights
        assert "risk_assessments" in insights
        assert "applicable_patterns" in insights
        assert "recommendations" in insights
        
        # 5. Verify all components contributed
        assert insights["applicable_patterns"]  # Pattern system working
        assert insights["recommendations"]  # Recommendation engine working
        
        # 6. Test feedback incorporation
        feedback_data = {
            "pattern_application": {
                "pattern_id": "integrated_pattern",
                "success": True,
                "improvement": 0.25
            }
        }
        
        await learning_system["feedback_loop"].process_evolution_feedback(feedback_data)
        
        # Pattern success rate should be updated
        updated_pattern = await learning_system["pattern_db"].get_pattern("integrated_pattern")
        assert updated_pattern is not None


class TestPhase7Performance:
    """Performance and scalability tests for Phase 7."""

    @pytest.mark.asyncio
    async def test_pattern_database_performance(self, tmp_path):
        """Test pattern database performance with large datasets."""
        pattern_db = PatternDatabase(str(tmp_path / "perf_patterns.db"))
        await pattern_db.initialize()
        
        # Store many patterns
        start_time = asyncio.get_event_loop().time()
        
        for i in range(100):
            pattern = Pattern(
                id=f"perf_pattern_{i}",
                name=f"Performance Pattern {i}",
                category="optimization" if i % 3 == 0 else "refactoring",
                context={"index": i},
                action={"type": "action"},
                outcome={"result": "success"},
                success_rate=0.5 + (i % 50) / 100,
                usage_count=i,
                confidence=0.7,
                created_at=datetime.now(),
                last_used=datetime.now()
            )
            await pattern_db.store_pattern(pattern)
        
        store_time = asyncio.get_event_loop().time() - start_time
        
        # Should complete in reasonable time
        assert store_time < 5.0  # 5 seconds for 100 patterns
        
        # Test search performance
        search_start = asyncio.get_event_loop().time()
        
        results = await pattern_db.search_patterns(
            {"category": "optimization", "min_success_rate": 0.7}
        )
        
        search_time = asyncio.get_event_loop().time() - search_start
        
        assert search_time < 0.5  # 500ms for search
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_memory_curator_scalability(self):
        """Test memory curator with large number of memories."""
        curator = MemoryCurator(max_memories=1000)
        await curator.initialize()
        
        # Store many memories
        for i in range(500):
            memory = Memory(
                id=f"scale_memory_{i}",
                type="test",
                timestamp=datetime.now() - timedelta(seconds=i),
                data={"index": i},
                metadata={
                    "importance": i / 1000,
                    "tags": [f"tag_{i % 10}"],
                    "retention_score": 0.5
                }
            )
            await curator.store_memory(memory)
        
        # Test retrieval performance
        start_time = asyncio.get_event_loop().time()
        
        memories = await curator.search_memories({"tags": ["tag_5"]})
        
        search_time = asyncio.get_event_loop().time() - start_time
        
        assert search_time < 1.0  # Should be fast
        assert len(memories) == 50  # Should find all tag_5 memories

    @pytest.mark.asyncio
    async def test_knowledge_graph_scalability(self):
        """Test knowledge graph with many nodes and edges."""
        graph = KnowledgeGraph()
        await graph.initialize()
        
        # Create a large graph
        for i in range(100):
            await graph.add_node(
                id=f"node_{i}",
                label=f"Node {i}",
                type="concept",
                properties={"value": i}
            )
            
            # Create edges to previous nodes
            if i > 0:
                for j in range(max(0, i - 3), i):
                    await graph.add_edge(
                        source_id=f"node_{j}",
                        target_id=f"node_{i}",
                        relationship="connects_to",
                        properties={"weight": 1.0}
                    )
        
        # Test query performance
        start_time = asyncio.get_event_loop().time()
        
        results = await graph.query_graph({
            "node_criteria": {"type": "concept"},
            "limit": 10
        })
        
        query_time = asyncio.get_event_loop().time() - start_time
        
        assert query_time < 1.0
        assert len(results) == 10
        
        # Test path finding performance
        path_start = asyncio.get_event_loop().time()
        
        path = await graph.find_path("node_0", "node_50")
        
        path_time = asyncio.get_event_loop().time() - path_start
        
        assert path_time < 2.0  # Should find path quickly
        assert path is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])