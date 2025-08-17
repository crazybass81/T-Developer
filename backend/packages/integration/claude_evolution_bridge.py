"""
Claude Code and Evolution System Integration Bridge.

This module connects Claude Code capabilities with the existing T-Developer
evolution system for enhanced self-improvement.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from backend.core.evolution_engine import EvolutionConfig, EvolutionEngine, EvolutionResult
from backend.core.shared_context import SharedContextStore
from backend.packages.agents.context_analyzer import ContextAnalyzerAgent
from backend.packages.agents.refactor import RefactorAgent
from backend.packages.learning.memory_curator import MemoryCurator

logger = logging.getLogger(__name__)


@dataclass
class IntegrationConfig:
    """Configuration for Claude Code integration."""

    enable_claude_refactor: bool = True
    enable_context_analysis: bool = True
    enable_memory_learning: bool = True
    claude_code_confidence_threshold: float = 0.8
    max_claude_suggestions: int = 10


class ClaudeEvolutionBridge:
    """
    Bridge between Claude Code and Evolution System.

    This class integrates:
    - Claude Code's refactoring capabilities
    - Advanced context understanding
    - Memory-based learning
    - Existing evolution engine
    """

    def __init__(self, config: Optional[IntegrationConfig] = None):
        """Initialize the integration bridge."""
        self.config = config or IntegrationConfig()

        # Initialize components
        self.evolution_engine = EvolutionEngine()
        self.context_store = SharedContextStore()
        self.memory_curator = MemoryCurator()

        # Initialize Claude Code agents
        self.refactor_agent = RefactorAgent("claude_refactor")
        self.context_analyzer = ContextAnalyzerAgent({})

        # State tracking
        self.active_evolution_id: Optional[str] = None
        self.claude_suggestions: list[dict[str, Any]] = []
        self.integration_metrics: dict[str, float] = {}

    async def initialize(self) -> None:
        """Initialize all components."""
        # Context store and memory curator initialize themselves
        await self.context_analyzer.initialize()

        logger.info("Claude Evolution Bridge initialized")

    async def enhance_evolution_with_claude(
        self, evolution_config: EvolutionConfig
    ) -> list[EvolutionResult]:
        """
        Enhance evolution cycle with Claude Code capabilities.

        Args:
            evolution_config: Standard evolution configuration

        Returns:
            Enhanced evolution results
        """
        logger.info(f"Starting Claude-enhanced evolution for {evolution_config.target_path}")

        # Pre-evolution analysis with Claude Code
        if self.config.enable_context_analysis:
            pre_analysis = await self._pre_evolution_analysis(evolution_config)
            await self._apply_pre_analysis_insights(pre_analysis)

        # Run evolution with Claude Code enhancements
        results = await self._run_enhanced_evolution(evolution_config)

        # Post-evolution learning
        if self.config.enable_memory_learning:
            await self._post_evolution_learning(results)

        return results

    async def _pre_evolution_analysis(self, config: EvolutionConfig) -> dict[str, Any]:
        """Perform pre-evolution analysis using Claude Code."""
        logger.info("Performing pre-evolution analysis with Claude Code")

        analysis = {}

        # Analyze target with context analyzer
        context_analysis = await self.context_analyzer.execute(
            {
                "action": "analyze_code",
                "target": config.target_path,
                "depth": "deep",
                "include_memory": True,
            }
        )
        analysis["context"] = context_analysis

        # Get improvement suggestions from Claude Code
        if self.config.enable_claude_refactor:
            suggestions = await self.refactor_agent.execute(
                {
                    "action": "analyze",
                    "target": config.target_path,
                    "focus_areas": config.focus_areas,
                }
            )

            # Filter high-confidence suggestions
            filtered_suggestions = self._filter_suggestions(suggestions.get("suggestions", []))
            self.claude_suggestions = filtered_suggestions[: self.config.max_claude_suggestions]
            analysis["claude_suggestions"] = self.claude_suggestions

        # Analyze risks and dependencies
        risk_analysis = await self.context_analyzer.execute(
            {"action": "assess_risk", "target": config.target_path}
        )
        analysis["risks"] = risk_analysis

        # Get recommendations
        recommendations = await self.context_analyzer.execute(
            {
                "action": "generate_recommendations",
                "type": "evolution",
                "description": f"Evolution for {config.target_path}",
                "include_memory": True,
            }
        )
        analysis["recommendations"] = recommendations

        return analysis

    async def _apply_pre_analysis_insights(self, analysis: dict[str, Any]) -> None:
        """Apply insights from pre-analysis to guide evolution."""
        # Store insights in context
        # Store task insights in context
        await self.context_store.update_context(
            "task_insights",
            {
                "task_id": f"evolution_{datetime.now().timestamp()}",
                "task_type": "evolution",
                "description": "Claude-enhanced evolution",
                "requirements": analysis.get("recommendations", {})
                .get("recommendations", {})
                .get("immediate", []),
            },
        )

        # Store insights in memory
        from backend.packages.learning.memory_curator import Memory

        memory = Memory(
            memory_id=f"evolution_insights_{datetime.now().timestamp()}",
            type="insights",
            content={
                "claude_suggestions": self.claude_suggestions,
                "risks": analysis.get("risks", {}),
                "recommendations": analysis.get("recommendations", {}),
            },
            timestamp=datetime.now(),
            importance=0.8,
        )
        await self.memory_curator.store_memory(memory)

    async def _run_enhanced_evolution(self, config: EvolutionConfig) -> list[EvolutionResult]:
        """Run evolution with Claude Code enhancements."""
        # Create enhanced configuration
        enhanced_config = EvolutionConfig(
            target_path=config.target_path,
            max_cycles=config.max_cycles,
            focus_areas=config.focus_areas + ["claude_suggestions"],
            dry_run=config.dry_run,
            max_files=config.max_files,
            enable_code_modification=config.enable_code_modification,
        )

        # Hook into evolution process
        original_broadcast = self.evolution_engine.broadcast
        self.evolution_engine.broadcast = self._enhanced_broadcast

        try:
            # Run evolution
            results = await self.evolution_engine.run_evolution(enhanced_config)

            # Enhance results with Claude Code insights
            for i, result in enumerate(results):
                result = await self._enhance_result_with_claude(result, i)
                results[i] = result

            return results

        finally:
            # Restore original broadcast
            self.evolution_engine.broadcast = original_broadcast

    async def _enhanced_broadcast(self, message: dict[str, Any]) -> None:
        """Enhanced broadcast with Claude Code insights."""
        # Add Claude suggestions to relevant broadcasts
        if message.get("type") == "evolution:planning":
            message["claude_suggestions"] = self.claude_suggestions

        # Log the broadcast
        logger.info(f"Enhanced broadcast: {message}")

    async def _enhance_result_with_claude(
        self, result: EvolutionResult, cycle_number: int
    ) -> EvolutionResult:
        """Enhance evolution result with Claude Code analysis."""
        # Analyze implementation with Claude Code
        if self.config.enable_claude_refactor and result.implementation_result:
            claude_review = await self.refactor_agent.execute(
                {
                    "action": "review",
                    "changes": result.implementation_result,
                    "context": {"cycle": cycle_number, "metrics": result.metrics},
                }
            )

            # Add Claude's review to result
            result.implementation_result["claude_review"] = claude_review

        # Calculate integration metrics
        self.integration_metrics[f"cycle_{cycle_number}"] = {
            "claude_contribution": self._calculate_claude_contribution(result),
            "context_utilization": self._calculate_context_utilization(result),
            "memory_impact": await self._calculate_memory_impact(),
        }

        return result

    async def _post_evolution_learning(self, results: list[EvolutionResult]) -> None:
        """Learn from evolution results."""
        logger.info("Performing post-evolution learning")

        for result in results:
            # Store successful patterns
            if result.success:
                await self._store_successful_patterns(result)

            # Store experience as memory
            from backend.packages.learning.memory_curator import Memory

            memory = Memory(
                memory_id=f"evolution_experience_{result.cycle_number}_{datetime.now().timestamp()}",
                type="experience",
                content={
                    "task_type": "evolution",
                    "state_before": {"metrics": result.metrics},
                    "action": {
                        "cycle": result.cycle_number,
                        "focus_areas": result.research_result.get("focus_areas", []),
                    },
                    "state_after": {"metrics": result.metrics},
                    "reward": self._calculate_reward(result),
                },
                timestamp=datetime.now(),
                importance=0.7,
            )
            await self.memory_curator.store_memory(memory)

        # Cleanup expired memories periodically
        await self.memory_curator.storage.cleanup_expired_memories()

    async def _store_successful_patterns(self, result: EvolutionResult) -> None:
        """Store successful evolution patterns."""
        # Extract patterns from implementation
        if result.implementation_result:
            for change in result.implementation_result.get("changes", []):
                if change.get("success"):
                    from backend.packages.learning.memory_curator import Memory

                    memory = Memory(
                        memory_id=f"pattern_{change.get('type', 'unknown')}_{datetime.now().timestamp()}",
                        type="pattern",
                        content={
                            "concept": f"evolution_pattern_{change.get('type', 'unknown')}",
                            "pattern": change,
                            "metrics_impact": result.metrics,
                            "cycle": result.cycle_number,
                        },
                        timestamp=datetime.now(),
                        importance=0.7,
                    )
                    await self.memory_curator.store_memory(memory)

    def _filter_suggestions(self, suggestions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter suggestions based on confidence threshold."""
        filtered = []
        for suggestion in suggestions:
            confidence = suggestion.get("confidence", 0)
            if confidence >= self.config.claude_code_confidence_threshold:
                filtered.append(suggestion)

        # Sort by confidence
        filtered.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        return filtered

    def _calculate_claude_contribution(self, result: EvolutionResult) -> float:
        """Calculate Claude Code's contribution to the result."""
        contribution = 0.0

        # Check if Claude suggestions were implemented
        if result.implementation_result:
            claude_review = result.implementation_result.get("claude_review", {})
            if claude_review.get("suggestions_implemented"):
                contribution += 0.5

            if claude_review.get("quality_improved"):
                contribution += 0.3

            if claude_review.get("risks_mitigated"):
                contribution += 0.2

        return min(1.0, contribution)

    def _calculate_context_utilization(self, result: EvolutionResult) -> float:
        """Calculate how well context was utilized."""
        utilization = 0.0

        # Check if recommendations were followed
        if result.plan_result:
            recommendations_followed = result.plan_result.get("recommendations_followed", 0)
            total_recommendations = result.plan_result.get("total_recommendations", 1)
            utilization = (
                recommendations_followed / total_recommendations if total_recommendations > 0 else 0
            )

        return utilization

    async def _calculate_memory_impact(self) -> float:
        """Calculate memory system impact."""
        # Get memory statistics
        memories = await self.memory_curator.search_memories({}, limit=100)
        stats = {
            "total_memories": len(memories),
            "pattern_count": len([m for m in memories if m.type == "pattern"]),
            "avg_pattern_success": 0.5,  # Simplified
        }

        # Calculate impact based on pattern usage
        pattern_count = stats.get("pattern_count", 0)
        pattern_success = stats.get("avg_pattern_success", 0)

        impact = (pattern_count / 100) * pattern_success  # Normalize
        return min(1.0, impact)

    def _calculate_reward(self, result: EvolutionResult) -> float:
        """Calculate reward for reinforcement learning."""
        reward = 0.0

        # Base reward for success
        if result.success:
            reward += 0.5

        # Reward for metric improvements
        for metric, value in result.metrics.items():
            if value > 0:  # Assuming positive is good
                reward += value * 0.1

        # Reward for efficiency
        if result.duration < 300:  # Less than 5 minutes
            reward += 0.2

        return min(1.0, reward)

    async def get_integration_status(self) -> dict[str, Any]:
        """Get current integration status."""
        return {
            "claude_enabled": self.config.enable_claude_refactor,
            "context_enabled": self.config.enable_context_analysis,
            "memory_enabled": self.config.enable_memory_learning,
            "active_evolution": self.active_evolution_id,
            "suggestions_count": len(self.claude_suggestions),
            "integration_metrics": self.integration_metrics,
            "memory_stats": {
                "total_memories": len(await self.memory_curator.search_memories({}, limit=100))
            },
        }

    async def export_integration_report(self, file_path: str) -> None:
        """Export integration report."""
        import json

        report = {
            "timestamp": datetime.now().isoformat(),
            "status": await self.get_integration_status(),
            "claude_suggestions": self.claude_suggestions,
            "metrics": self.integration_metrics,
            "memory_patterns": await self._get_learned_patterns(),
        }

        with open(file_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Integration report exported to {file_path}")

    async def _get_learned_patterns(self) -> list[dict[str, Any]]:
        """Get patterns learned from evolution."""
        patterns = []

        # Get evolution pattern memories
        memories = await self.memory_curator.search_memories({"type": "pattern"}, limit=20)

        for memory in memories:
            patterns.append(
                {
                    "concept": memory.content.get("concept", ""),
                    "importance": memory.importance,
                    "access_count": memory.access_count,
                    "content": memory.content,
                }
            )

        return patterns
