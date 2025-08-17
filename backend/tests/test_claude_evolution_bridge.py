"""
Tests for Claude Evolution Bridge integration.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.core.evolution_engine import EvolutionConfig, EvolutionResult
from backend.packages.integration.claude_evolution_bridge import (
    ClaudeEvolutionBridge,
    IntegrationConfig,
)


@pytest.fixture
async def bridge():
    """Create a Claude Evolution Bridge for testing."""
    config = IntegrationConfig(
        enable_claude_refactor=True,
        enable_context_analysis=True,
        enable_memory_learning=True,
        claude_code_confidence_threshold=0.7,
        max_claude_suggestions=5
    )
    bridge = ClaudeEvolutionBridge(config)
    
    # Mock the components
    bridge.evolution_engine = AsyncMock()
    bridge.context_manager = AsyncMock()
    bridge.memory_system = AsyncMock()
    bridge.claude_refactor = AsyncMock()
    bridge.context_analyzer = AsyncMock()
    
    await bridge.initialize()
    return bridge


@pytest.fixture
def evolution_config():
    """Create a sample evolution configuration."""
    return EvolutionConfig(
        target_path="/test/path/module.py",
        max_cycles=2,
        focus_areas=["quality", "performance"],
        dry_run=True,
        max_files=5,
        enable_code_modification=False
    )


@pytest.fixture
def mock_evolution_result():
    """Create a mock evolution result."""
    return EvolutionResult(
        cycle_number=1,
        research_result={"focus_areas": ["quality"]},
        plan_result={"recommendations_followed": 3, "total_recommendations": 5},
        implementation_result={
            "changes": [
                {"type": "refactor", "success": True},
                {"type": "optimize", "success": True}
            ]
        },
        evaluation_result={"success": True},
        metrics={"coverage": 0.85, "complexity": 70},
        duration=120.0,
        success=True
    )


class TestClaudeEvolutionBridge:
    """Test Claude Evolution Bridge functionality."""

    @pytest.mark.asyncio
    async def test_initialization(self, bridge):
        """Test bridge initialization."""
        assert bridge.config.enable_claude_refactor is True
        assert bridge.config.enable_context_analysis is True
        assert bridge.config.enable_memory_learning is True
        assert bridge.claude_suggestions == []
        assert bridge.integration_metrics == {}

    @pytest.mark.asyncio
    async def test_pre_evolution_analysis(self, bridge, evolution_config):
        """Test pre-evolution analysis with Claude Code."""
        # Mock responses
        bridge.context_analyzer.execute.return_value = {
            "success": True,
            "analysis": {"key_elements": ["class:TestClass"]},
            "risks": {"high": [], "medium": [], "low": []},
            "recommendations": {
                "recommendations": {
                    "immediate": ["Add type hints", "Improve docstrings"]
                }
            }
        }
        
        bridge.claude_refactor.execute.return_value = {
            "suggestions": [
                {"description": "Refactor method", "confidence": 0.9},
                {"description": "Optimize loop", "confidence": 0.8},
                {"description": "Minor cleanup", "confidence": 0.6}  # Below threshold
            ]
        }
        
        # Run analysis
        analysis = await bridge._pre_evolution_analysis(evolution_config)
        
        # Verify analysis
        assert "context" in analysis
        assert "claude_suggestions" in analysis
        assert "risks" in analysis
        assert "recommendations" in analysis
        
        # Check filtered suggestions
        assert len(bridge.claude_suggestions) == 2  # Only high confidence
        assert bridge.claude_suggestions[0]["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_apply_pre_analysis_insights(self, bridge):
        """Test applying pre-analysis insights."""
        analysis = {
            "recommendations": {
                "recommendations": {
                    "immediate": ["Test recommendation"]
                }
            },
            "risks": {"high": ["Security risk"]},
        }
        
        bridge.claude_suggestions = [{"description": "Test suggestion"}]
        
        # Apply insights
        await bridge._apply_pre_analysis_insights(analysis)
        
        # Verify context creation
        bridge.context_manager.create_task_context.assert_called_once()
        
        # Verify memory update
        bridge.memory_system.update_working_memory.assert_called_once_with(
            "evolution_insights",
            {
                "claude_suggestions": [{"description": "Test suggestion"}],
                "risks": {"high": ["Security risk"]},
                "recommendations": {
                    "recommendations": {
                        "immediate": ["Test recommendation"]
                    }
                }
            }
        )

    @pytest.mark.asyncio
    async def test_enhance_evolution_with_claude(self, bridge, evolution_config):
        """Test complete Claude-enhanced evolution."""
        # Mock evolution results
        mock_results = [
            MagicMock(
                cycle_number=1,
                success=True,
                metrics={"coverage": 0.8},
                implementation_result={"changes": []},
                research_result={"focus_areas": ["quality"]}
            )
        ]
        
        bridge.evolution_engine.run_evolution.return_value = mock_results
        bridge._pre_evolution_analysis = AsyncMock(return_value={})
        bridge._apply_pre_analysis_insights = AsyncMock()
        bridge._post_evolution_learning = AsyncMock()
        
        # Run enhanced evolution
        results = await bridge.enhance_evolution_with_claude(evolution_config)
        
        # Verify process
        assert len(results) == 1
        bridge._pre_evolution_analysis.assert_called_once()
        bridge._apply_pre_analysis_insights.assert_called_once()
        bridge._post_evolution_learning.assert_called_once()

    @pytest.mark.asyncio
    async def test_enhance_result_with_claude(self, bridge, mock_evolution_result):
        """Test enhancing evolution result with Claude analysis."""
        # Mock Claude review
        bridge.claude_refactor.execute.return_value = {
            "suggestions_implemented": True,
            "quality_improved": True,
            "risks_mitigated": False
        }
        
        # Enhance result
        enhanced = await bridge._enhance_result_with_claude(
            mock_evolution_result,
            cycle_number=1
        )
        
        # Verify enhancement
        assert "claude_review" in enhanced.implementation_result
        assert "cycle_1" in bridge.integration_metrics
        
        # Check metrics calculation
        metrics = bridge.integration_metrics["cycle_1"]
        assert "claude_contribution" in metrics
        assert "context_utilization" in metrics
        assert "memory_impact" in metrics

    @pytest.mark.asyncio
    async def test_filter_suggestions(self, bridge):
        """Test filtering suggestions by confidence."""
        suggestions = [
            {"description": "High confidence", "confidence": 0.9},
            {"description": "Medium confidence", "confidence": 0.75},
            {"description": "Low confidence", "confidence": 0.5},
            {"description": "Very low", "confidence": 0.3},
        ]
        
        bridge.config.claude_code_confidence_threshold = 0.7
        filtered = bridge._filter_suggestions(suggestions)
        
        assert len(filtered) == 2
        assert filtered[0]["confidence"] == 0.9
        assert filtered[1]["confidence"] == 0.75

    @pytest.mark.asyncio
    async def test_post_evolution_learning(self, bridge, mock_evolution_result):
        """Test post-evolution learning process."""
        results = [mock_evolution_result]
        
        # Run learning
        await bridge._post_evolution_learning(results)
        
        # Verify pattern storage
        bridge.memory_system.store_semantic.assert_called()
        
        # Verify experience storage
        bridge.memory_system.store_experience.assert_called_once()
        
        # Verify memory consolidation
        bridge.memory_system.consolidate_memories.assert_called_once()

    @pytest.mark.asyncio
    async def test_calculate_claude_contribution(self, bridge):
        """Test calculating Claude's contribution to results."""
        # Test with Claude suggestions implemented
        result = MagicMock(
            implementation_result={
                "claude_review": {
                    "suggestions_implemented": True,
                    "quality_improved": True,
                    "risks_mitigated": True
                }
            }
        )
        
        contribution = bridge._calculate_claude_contribution(result)
        assert contribution == 1.0  # Maximum contribution
        
        # Test with partial implementation
        result.implementation_result["claude_review"]["risks_mitigated"] = False
        contribution = bridge._calculate_claude_contribution(result)
        assert contribution == 0.8
        
        # Test with no implementation
        result.implementation_result = {}
        contribution = bridge._calculate_claude_contribution(result)
        assert contribution == 0.0

    @pytest.mark.asyncio
    async def test_calculate_context_utilization(self, bridge):
        """Test calculating context utilization."""
        # Test with recommendations followed
        result = MagicMock(
            plan_result={
                "recommendations_followed": 4,
                "total_recommendations": 5
            }
        )
        
        utilization = bridge._calculate_context_utilization(result)
        assert utilization == 0.8
        
        # Test with no recommendations
        result.plan_result = {
            "recommendations_followed": 0,
            "total_recommendations": 0
        }
        
        utilization = bridge._calculate_context_utilization(result)
        assert utilization == 0.0

    @pytest.mark.asyncio
    async def test_calculate_reward(self, bridge):
        """Test reward calculation for reinforcement learning."""
        # Test successful result with good metrics
        result = MagicMock(
            success=True,
            metrics={"coverage": 0.9, "quality": 0.8},
            duration=200  # Under 5 minutes
        )
        
        reward = bridge._calculate_reward(result)
        assert reward > 0.5  # Should be relatively high
        
        # Test failed result
        result.success = False
        result.duration = 400  # Over 5 minutes
        
        reward = bridge._calculate_reward(result)
        assert reward < 0.5  # Should be lower

    @pytest.mark.asyncio
    async def test_get_integration_status(self, bridge):
        """Test getting integration status."""
        bridge.claude_suggestions = [{"test": "suggestion"}]
        bridge.memory_system.get_memory_stats.return_value = {
            "semantic_count": 10,
            "pattern_count": 5
        }
        
        status = await bridge.get_integration_status()
        
        assert status["claude_enabled"] is True
        assert status["context_enabled"] is True
        assert status["memory_enabled"] is True
        assert status["suggestions_count"] == 1
        assert "memory_stats" in status

    @pytest.mark.asyncio
    async def test_export_integration_report(self, bridge):
        """Test exporting integration report."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            report_path = f.name
        
        # Mock data
        bridge.claude_suggestions = [{"suggestion": "test"}]
        bridge.integration_metrics = {"cycle_1": {"test": 0.5}}
        bridge.memory_system.recall_semantic.return_value = []
        bridge.memory_system.get_memory_stats.return_value = {}
        
        # Export report
        await bridge.export_integration_report(report_path)
        
        # Verify report
        with open(report_path, "r") as f:
            report = json.load(f)
        
        assert "timestamp" in report
        assert "status" in report
        assert "claude_suggestions" in report
        assert "metrics" in report
        assert "memory_patterns" in report
        
        # Cleanup
        Path(report_path).unlink()

    @pytest.mark.asyncio
    async def test_store_successful_patterns(self, bridge, mock_evolution_result):
        """Test storing successful evolution patterns."""
        await bridge._store_successful_patterns(mock_evolution_result)
        
        # Verify semantic storage was called for each successful change
        assert bridge.memory_system.store_semantic.call_count == 2

    @pytest.mark.asyncio
    async def test_enhanced_broadcast(self, bridge):
        """Test enhanced broadcast functionality."""
        bridge.claude_suggestions = [{"test": "suggestion"}]
        
        message = {"type": "evolution:planning"}
        await bridge._enhanced_broadcast(message)
        
        # Verify Claude suggestions added
        assert "claude_suggestions" in message
        assert message["claude_suggestions"] == [{"test": "suggestion"}]

    @pytest.mark.asyncio
    async def test_calculate_memory_impact(self, bridge):
        """Test calculating memory system impact."""
        bridge.memory_system.get_memory_stats.return_value = {
            "pattern_count": 50,
            "avg_pattern_success": 0.8
        }
        
        impact = await bridge._calculate_memory_impact()
        assert impact == 0.4  # (50/100) * 0.8

    @pytest.mark.asyncio
    async def test_get_learned_patterns(self, bridge):
        """Test retrieving learned patterns."""
        # Mock memory recall
        mock_memory = MagicMock(
            importance=0.8,
            access_count=5,
            content={"pattern": "test"}
        )
        
        bridge.memory_system.recall_semantic.return_value = [
            ("evolution_pattern_test", mock_memory)
        ]
        
        patterns = await bridge._get_learned_patterns()
        
        assert len(patterns) == 1
        assert patterns[0]["concept"] == "evolution_pattern_test"
        assert patterns[0]["importance"] == 0.8
        assert patterns[0]["access_count"] == 5