"""
Test suite for Agent Registry Data Models
Day 6: TDD Implementation - RED Phase
Generated: 2024-11-18

Testing requirements:
1. Agent metadata schema
2. AI analysis result storage
3. Version management system
4. Evolution history tracking
"""

import json
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


class TestAgentModel:
    """Test Agent core model"""

    def test_agent_creation(self):
        """Test creating a new agent with metadata"""
        from src.models.agent import Agent

        agent = Agent(
            name="nl_input_agent",
            description="Natural Language Input Processing Agent",
            version="1.0.0",
            size_kb=5.8,
            instantiation_us=2.7,
            capabilities=["text_processing", "intent_extraction"],
        )

        assert agent.id is not None
        assert agent.name == "nl_input_agent"
        assert agent.size_kb == 5.8
        assert agent.instantiation_us == 2.7
        assert agent.meets_constraints() is True
        assert agent.fitness_score == 0.0  # Initial fitness

    def test_constraint_validation(self):
        """Test agent constraint validation (6.5KB, 3us)"""
        from src.models.agent import Agent

        # Valid agent
        valid_agent = Agent(name="valid_agent", size_kb=6.4, instantiation_us=2.9)
        assert valid_agent.meets_constraints() is True

        # Size violation
        large_agent = Agent(name="large_agent", size_kb=7.0, instantiation_us=2.5)
        assert large_agent.meets_constraints() is False
        violations = large_agent.get_violations()
        assert "size" in violations

        # Speed violation
        slow_agent = Agent(name="slow_agent", size_kb=5.0, instantiation_us=3.5)
        assert slow_agent.meets_constraints() is False
        violations = slow_agent.get_violations()
        assert "speed" in violations

    def test_agent_metadata(self):
        """Test agent metadata storage and retrieval"""
        from src.models.agent import Agent

        metadata = {
            "author": "Evolution Engine",
            "framework": "Agno",
            "deployment": "AgentCore",
            "tags": ["core", "production", "optimized"],
        }

        agent = Agent(name="metadata_agent", metadata=metadata)

        assert agent.metadata["author"] == "Evolution Engine"
        assert "production" in agent.metadata["tags"]
        assert agent.get_tag_count() == 3

    def test_agent_serialization(self):
        """Test agent serialization to/from JSON"""
        from src.models.agent import Agent

        agent = Agent(name="serialization_test", version="2.1.0", capabilities=["search", "filter"])

        # Serialize
        json_data = agent.to_json()
        data = json.loads(json_data)

        assert data["name"] == "serialization_test"
        assert data["version"] == "2.1.0"
        assert "search" in data["capabilities"]

        # Deserialize
        restored = Agent.from_json(json_data)
        assert restored.name == agent.name
        assert restored.version == agent.version
        assert restored.capabilities == agent.capabilities


class TestAgentVersion:
    """Test Agent Version Management"""

    def test_version_creation(self):
        """Test creating agent versions"""
        from src.models.agent_version import AgentVersion

        version = AgentVersion(
            agent_id="agent_001",
            version_number="1.2.3",
            code_hash="abc123def456",
            changes=["Added retry logic", "Optimized memory usage"],
        )

        assert version.agent_id == "agent_001"
        assert version.version_number == "1.2.3"
        assert version.is_stable is False  # New versions start unstable
        assert len(version.changes) == 2

    def test_version_comparison(self):
        """Test version comparison and ordering"""
        from src.models.agent_version import AgentVersion

        v1 = AgentVersion(version_number="1.0.0")
        v2 = AgentVersion(version_number="1.2.0")
        v3 = AgentVersion(version_number="2.0.0")

        assert v1 < v2 < v3
        assert v3.is_major_version() is True
        assert v2.is_minor_version() is True

    def test_version_rollback(self):
        """Test version rollback functionality"""
        from src.models.agent_version import AgentVersion

        current = AgentVersion(
            version_number="2.0.0", is_stable=False, performance_metrics={"error_rate": 0.15}
        )

        previous = AgentVersion(
            version_number="1.9.0", is_stable=True, performance_metrics={"error_rate": 0.02}
        )

        assert current.should_rollback(previous) is True
        rollback_version = current.rollback_to(previous)
        assert rollback_version.version_number == "2.0.1"
        assert rollback_version.rollback_from == "2.0.0"

    def test_version_history(self):
        """Test version history tracking"""
        from src.models.agent_version import VersionHistory

        history = VersionHistory(agent_id="agent_001")

        # Add versions
        history.add_version("1.0.0", {"initial": True})
        history.add_version("1.1.0", {"bug_fixes": 5})
        history.add_version("2.0.0", {"breaking_changes": True})

        assert history.get_version_count() == 3
        assert history.get_latest_version() == "2.0.0"
        assert history.get_stable_version() == "1.1.0"

        # Get version range
        versions = history.get_versions_between("1.0.0", "2.0.0")
        assert len(versions) == 3


class TestEvolutionHistory:
    """Test Evolution History Tracking"""

    def test_evolution_record_creation(self):
        """Test creating evolution history records"""
        from src.models.evolution_history import EvolutionRecord

        record = EvolutionRecord(
            agent_id="agent_001",
            generation=5,
            parent_ids=["parent_001", "parent_002"],
            mutations=["code_optimization", "memory_reduction"],
            fitness_score=0.85,
            constraints_met=True,
        )

        assert record.generation == 5
        assert len(record.parent_ids) == 2
        assert record.fitness_score == 0.85
        assert record.is_successful() is True

    def test_evolution_lineage(self):
        """Test tracking agent evolution lineage"""
        from src.models.evolution_history import EvolutionLineage

        lineage = EvolutionLineage(root_agent_id="original_001")

        # Add evolution steps
        child1 = lineage.add_evolution(
            parent_id="original_001", child_id="evolved_001", generation=1, fitness_improvement=0.1
        )

        child2 = lineage.add_evolution(
            parent_id="evolved_001", child_id="evolved_002", generation=2, fitness_improvement=0.15
        )

        assert lineage.get_generation_count() == 2
        assert lineage.get_total_fitness_improvement() == 0.25
        assert lineage.get_best_agent() == "evolved_002"

        # Get ancestry
        ancestors = lineage.get_ancestors("evolved_002")
        assert len(ancestors) == 2
        assert "original_001" in ancestors

    def test_evolution_metrics(self):
        """Test evolution metrics and statistics"""
        from src.models.evolution_history import EvolutionMetrics

        metrics = EvolutionMetrics()

        # Add evolution results
        metrics.record_evolution(
            agent_id="agent_001", generation=1, fitness=0.7, size_kb=5.5, speed_us=2.8
        )

        metrics.record_evolution(
            agent_id="agent_002", generation=2, fitness=0.8, size_kb=5.2, speed_us=2.5
        )

        stats = metrics.get_statistics()
        assert stats["avg_fitness"] == 0.75
        assert stats["avg_size_kb"] == 5.35
        assert stats["avg_speed_us"] == 2.65
        assert stats["fitness_trend"] == "improving"

    def test_evolution_patterns(self):
        """Test identifying successful evolution patterns"""
        from src.models.evolution_history import PatternAnalyzer

        analyzer = PatternAnalyzer()

        # Add successful patterns
        analyzer.record_pattern(
            pattern_type="memory_optimization", success_rate=0.85, avg_improvement=0.12
        )

        analyzer.record_pattern(
            pattern_type="speed_optimization", success_rate=0.92, avg_improvement=0.18
        )

        best_patterns = analyzer.get_best_patterns(top_n=1)
        assert best_patterns[0]["type"] == "speed_optimization"
        assert best_patterns[0]["success_rate"] == 0.92


class TestAIAnalysisResult:
    """Test AI Analysis Result Storage"""

    def test_analysis_result_creation(self):
        """Test storing AI analysis results"""
        from src.models.ai_analysis import AIAnalysisResult

        result = AIAnalysisResult(
            agent_id="agent_001",
            analysis_type="performance",
            ai_model="claude-3",
            findings={
                "bottlenecks": ["database_query", "api_call"],
                "recommendations": ["add_caching", "batch_requests"],
                "estimated_improvement": 0.25,
            },
        )

        assert result.ai_model == "claude-3"
        assert len(result.findings["bottlenecks"]) == 2
        assert result.findings["estimated_improvement"] == 0.25

    def test_consensus_analysis(self):
        """Test consensus from multiple AI models"""
        from src.models.ai_analysis import ConsensusAnalyzer

        analyzer = ConsensusAnalyzer()

        # Add results from different AI models
        analyzer.add_result("claude", {"issue": "memory_leak", "confidence": 0.9})

        analyzer.add_result("gpt4", {"issue": "memory_leak", "confidence": 0.85})

        analyzer.add_result("gemini", {"issue": "memory_leak", "confidence": 0.8})

        consensus = analyzer.get_consensus()
        assert consensus["agreed_issue"] == "memory_leak"
        assert consensus["confidence"] == 0.85  # Average
        assert consensus["agreement_level"] == "high"

    def test_analysis_history(self):
        """Test tracking analysis history over time"""
        from src.models.ai_analysis import AnalysisHistory

        history = AnalysisHistory(agent_id="agent_001")

        # Add analysis results over time
        history.add_analysis(timestamp=datetime(2024, 11, 1), findings={"score": 0.7})

        history.add_analysis(timestamp=datetime(2024, 11, 15), findings={"score": 0.85})

        trend = history.get_trend()
        assert trend == "improving"
        assert history.get_improvement_rate() == pytest.approx(0.15, 0.01)


class TestAgentGenePool:
    """Test Agent Gene Pool for Evolution"""

    def test_gene_pool_creation(self):
        """Test creating and managing agent gene pool"""
        from src.models.agent_gene_pool import AgentGenePool

        pool = AgentGenePool(max_size=100)

        # Add agents to pool
        pool.add_agent("agent_001", fitness=0.8, genes={"trait1": 0.5})
        pool.add_agent("agent_002", fitness=0.9, genes={"trait1": 0.7})
        pool.add_agent("agent_003", fitness=0.6, genes={"trait1": 0.3})

        assert pool.size() == 3
        assert pool.get_best_agent() == "agent_002"
        assert pool.get_average_fitness() == pytest.approx(0.766, 0.01)

    def test_selection_pressure(self):
        """Test selection pressure in gene pool"""
        from src.models.agent_gene_pool import AgentGenePool

        pool = AgentGenePool(max_size=10)

        # Add agents with varying fitness
        for i in range(20):
            pool.add_agent(f"agent_{i}", fitness=i * 0.05)

        # Pool should keep only top 10
        assert pool.size() == 10
        survivors = pool.get_all_agents()
        min_fitness = min(a["fitness"] for a in survivors)
        assert min_fitness >= 0.5  # Bottom half eliminated

    def test_genetic_diversity(self):
        """Test maintaining genetic diversity"""
        from src.models.agent_gene_pool import GeneticDiversity

        diversity = GeneticDiversity()

        # Add similar agents
        diversity.add_genome("agent_001", {"a": 1, "b": 2})
        diversity.add_genome("agent_002", {"a": 1, "b": 2})

        assert diversity.calculate_diversity() < 0.1  # Low diversity

        # Add diverse agent
        diversity.add_genome("agent_003", {"a": 5, "b": 8})
        assert diversity.calculate_diversity() > 0.5  # Higher diversity


class TestFitnessFunction:
    """Test Fitness Function Definition and Tracking"""

    def test_fitness_calculation(self):
        """Test fitness function calculation"""
        from src.models.fitness_function import FitnessCalculator

        calculator = FitnessCalculator()

        metrics = {
            "speed_us": 2.5,  # Good (< 3.0)
            "size_kb": 5.8,  # Good (< 6.5)
            "error_rate": 0.02,
            "success_rate": 0.98,
            "cost_per_call": 0.001,
        }

        fitness = calculator.calculate(metrics)
        assert 0 <= fitness <= 1
        assert fitness > 0.5  # Should be good fitness

    def test_weighted_fitness(self):
        """Test weighted fitness calculation"""
        from src.models.fitness_function import WeightedFitness

        fitness = WeightedFitness(weights={"performance": 0.4, "reliability": 0.3, "cost": 0.3})

        scores = {"performance": 0.9, "reliability": 0.95, "cost": 0.7}

        total = fitness.calculate(scores)
        assert total == pytest.approx(0.85, 0.01)

    def test_fitness_tracking(self):
        """Test fitness tracking over generations"""
        from src.models.fitness_function import FitnessTracker

        tracker = FitnessTracker()

        # Track fitness over generations
        tracker.record(generation=1, agent_id="a1", fitness=0.6)
        tracker.record(generation=2, agent_id="a2", fitness=0.7)
        tracker.record(generation=3, agent_id="a3", fitness=0.75)

        assert tracker.get_best_fitness() == 0.75
        assert tracker.get_improvement_rate() > 0
        assert tracker.is_converging() is False  # Still improving


@pytest.mark.integration
class TestAgentRegistryIntegration:
    """Integration tests for complete Agent Registry"""

    def test_full_agent_lifecycle(self):
        """Test complete agent lifecycle from creation to evolution"""
        from src.models.agent import Agent
        from src.models.agent_version import AgentVersion
        from src.models.evolution_history import EvolutionRecord

        # Create initial agent
        agent = Agent(name="lifecycle_test", version="1.0.0", size_kb=5.5, instantiation_us=2.8)

        assert agent.meets_constraints() is True

        # Create version
        version = AgentVersion(agent_id=agent.id, version_number="1.0.0", code_hash="initial_hash")

        # Evolve agent
        evolution = EvolutionRecord(
            agent_id=agent.id, generation=1, mutations=["optimize_memory"], fitness_score=0.85
        )

        # Update agent after evolution
        agent.size_kb = 5.2  # Improved
        agent.fitness_score = 0.85

        assert agent.size_kb < 5.5  # Improved
        assert agent.fitness_score == 0.85
