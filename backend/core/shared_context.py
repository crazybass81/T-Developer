"""Shared Context Store for Evolution Process.

This module provides a centralized storage for all evolution-related data,
enabling better coordination between agents and tracking of the entire process.
Enhanced with Claude Code integration and advanced context management.
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class ProjectContext:
    """Complete project context information."""
    
    project_root: Path
    language: str
    framework: Optional[str] = None
    dependencies: Dict[str, str] = field(default_factory=dict)
    structure: Dict[str, List[str]] = field(default_factory=dict)
    recent_changes: List[Dict[str, Any]] = field(default_factory=list)
    active_tasks: List[str] = field(default_factory=list)
    patterns: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskContext:
    """Context for a specific task or operation."""
    
    task_id: str
    task_type: str
    description: str
    target_files: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EvolutionContext:
    """Container for all evolution-related data."""

    evolution_id: str
    created_at: datetime
    target_path: str
    focus_areas: list[str]
    phase: str = "initialization"
    cycle: int = 0

    # Phase 1: Analysis & Research
    original_analysis: dict[str, Any] = field(default_factory=dict)
    external_research: dict[str, Any] = field(default_factory=dict)

    # Phase 2: Planning
    improvement_plan: dict[str, Any] = field(default_factory=dict)
    objectives: List[str] = field(default_factory=list)

    # Phase 3: Implementation
    implementation_log: dict[str, Any] = field(default_factory=dict)
    changes_made: List[Dict[str, Any]] = field(default_factory=list)

    # Phase 4: Evaluation
    current_state: dict[str, Any] = field(default_factory=dict)
    evaluation_results: dict[str, Any] = field(default_factory=dict)
    
    # Learning & Patterns
    patterns_learned: List[Dict[str, Any]] = field(default_factory=list)
    improvements: Dict[str, float] = field(default_factory=dict)
    
    # Metrics
    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)
    success_rate: float = 0.0

    # Metadata
    status: str = "initialized"
    current_phase: str = "initialization"
    error_log: list[str] = field(default_factory=list)
    rollback_points: List[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvolutionContext":
        """Create from dictionary."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


class SharedContextStore:
    """Centralized storage for evolution contexts.

    This store maintains all data generated during the evolution process,
    allowing agents to share information and avoid duplication.
    """

    def __init__(self):
        """Initialize the context store."""
        self.contexts: dict[str, EvolutionContext] = {}
        self.lock = asyncio.Lock()
        self.current_evolution_id: Optional[str] = None
        logger.info("SharedContextStore initialized")

    async def create_context(self, target_path: str, focus_areas: list[str]) -> str:
        """Create a new evolution context.

        Args:
            target_path: Path to target file/directory
            focus_areas: Areas to focus on during evolution

        Returns:
            Evolution ID
        """
        async with self.lock:
            evolution_id = str(uuid4())

            context = EvolutionContext(
                evolution_id=evolution_id,
                created_at=datetime.now(),
                target_path=target_path,
                focus_areas=focus_areas,
            )

            self.contexts[evolution_id] = context
            self.current_evolution_id = evolution_id

            logger.info(f"Created evolution context: {evolution_id}")
            return evolution_id

    async def get_context(self, evolution_id: Optional[str] = None) -> Optional[EvolutionContext]:
        """Get evolution context.

        Args:
            evolution_id: Evolution ID (uses current if not provided)

        Returns:
            Evolution context or None
        """
        evolution_id = evolution_id or self.current_evolution_id
        if not evolution_id:
            return None

        async with self.lock:
            return self.contexts.get(evolution_id)

    async def update_context(
        self, section: str, data: dict[str, Any], evolution_id: Optional[str] = None
    ) -> bool:
        """Update a section of the evolution context.

        Args:
            section: Section to update (e.g., 'original_analysis')
            data: Data to store
            evolution_id: Evolution ID (uses current if not provided)

        Returns:
            Success status
        """
        evolution_id = evolution_id or self.current_evolution_id
        if not evolution_id:
            logger.error("No evolution ID provided")
            return False

        async with self.lock:
            context = self.contexts.get(evolution_id)
            if not context:
                logger.error(f"Context not found: {evolution_id}")
                return False

            # Update the specified section
            if hasattr(context, section):
                if isinstance(getattr(context, section), dict):
                    # Merge with existing data
                    current_data = getattr(context, section)
                    current_data.update(data)
                else:
                    # Replace data
                    setattr(context, section, data)

                logger.info(f"Updated {section} for evolution {evolution_id}")
                return True
            else:
                logger.error(f"Invalid section: {section}")
                return False

    async def store_original_analysis(
        self,
        files_analyzed: int,
        metrics: dict[str, Any],
        issues: list[dict[str, Any]],
        improvements: list[dict[str, Any]],
        evolution_id: Optional[str] = None,
    ) -> bool:
        """Store original code analysis results.

        Args:
            files_analyzed: Number of files analyzed
            metrics: Code metrics
            issues: Detected issues
            improvements: Suggested improvements
            evolution_id: Evolution ID

        Returns:
            Success status
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": files_analyzed,
            "metrics": metrics,
            "issues": issues,
            "improvements": improvements,
        }

        return await self.update_context("original_analysis", data, evolution_id)

    async def store_external_research(
        self,
        best_practices: list[str],
        references: list[dict[str, Any]],
        patterns: list[dict[str, Any]],
        evolution_id: Optional[str] = None,
    ) -> bool:
        """Store external research results.

        Args:
            best_practices: Best practices found
            references: External references
            patterns: Design patterns discovered
            evolution_id: Evolution ID

        Returns:
            Success status
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "best_practices": best_practices,
            "references": references,
            "patterns": patterns,
        }

        return await self.update_context("external_research", data, evolution_id)

    async def store_improvement_plan(
        self,
        tasks: list[dict[str, Any]],
        priorities: list[str],
        dependencies: dict[str, list[str]],
        evolution_id: Optional[str] = None,
    ) -> bool:
        """Store improvement plan.

        Args:
            tasks: List of planned tasks
            priorities: Task priorities
            dependencies: Task dependencies
            evolution_id: Evolution ID

        Returns:
            Success status
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "tasks": tasks,
            "priorities": priorities,
            "dependencies": dependencies,
            "estimated_impact": self._calculate_impact(tasks),
        }

        return await self.update_context("improvement_plan", data, evolution_id)

    async def store_implementation_log(
        self,
        modified_files: list[str],
        changes: list[dict[str, Any]],
        rollback_points: list[dict[str, Any]],
        evolution_id: Optional[str] = None,
    ) -> bool:
        """Store implementation log.

        Args:
            modified_files: List of modified files
            changes: List of changes made
            rollback_points: Rollback checkpoints
            evolution_id: Evolution ID

        Returns:
            Success status
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "modified_files": modified_files,
            "changes": changes,
            "rollback_points": rollback_points,
            "total_changes": len(changes),
        }

        return await self.update_context("implementation_log", data, evolution_id)

    async def store_evaluation_results(
        self,
        goals_achieved: list[str],
        metrics_comparison: dict[str, Any],
        success_rate: float,
        evolution_id: Optional[str] = None,
    ) -> bool:
        """Store evaluation results.

        Args:
            goals_achieved: List of achieved goals
            metrics_comparison: Before/after metrics comparison
            success_rate: Overall success rate
            evolution_id: Evolution ID

        Returns:
            Success status
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "goals_achieved": goals_achieved,
            "metrics_comparison": metrics_comparison,
            "success_rate": success_rate,
            "verdict": "success" if success_rate >= 0.7 else "partial",
        }

        return await self.update_context("evaluation_results", data, evolution_id)

    async def get_comparison_data(self, evolution_id: Optional[str] = None) -> dict[str, Any]:
        """Get comparison data for evaluation.

        Args:
            evolution_id: Evolution ID

        Returns:
            Dictionary with before/plan/after data
        """
        context = await self.get_context(evolution_id)
        if not context:
            return {}

        return {
            "before": context.original_analysis,
            "plan": context.improvement_plan,
            "after": context.current_state,
            "implementation": context.implementation_log,
        }

    async def update_phase(self, phase: str, evolution_id: Optional[str] = None) -> bool:
        """Update current phase.

        Args:
            phase: New phase name
            evolution_id: Evolution ID

        Returns:
            Success status
        """
        evolution_id = evolution_id or self.current_evolution_id
        if not evolution_id:
            return False

        async with self.lock:
            context = self.contexts.get(evolution_id)
            if context:
                context.current_phase = phase
                context.status = f"running_{phase}"
                logger.info(f"Updated phase to {phase} for evolution {evolution_id}")
                return True

        return False

    async def add_error(self, error: str, evolution_id: Optional[str] = None) -> bool:
        """Add error to log.

        Args:
            error: Error message
            evolution_id: Evolution ID

        Returns:
            Success status
        """
        evolution_id = evolution_id or self.current_evolution_id
        if not evolution_id:
            return False

        async with self.lock:
            context = self.contexts.get(evolution_id)
            if context:
                context.error_log.append(f"{datetime.now().isoformat()}: {error}")
                return True

        return False

    async def export_context(
        self, evolution_id: Optional[str] = None, file_path: Optional[str] = None
    ) -> Optional[str]:
        """Export context to JSON file.

        Args:
            evolution_id: Evolution ID
            file_path: Output file path

        Returns:
            File path or None
        """
        context = await self.get_context(evolution_id)
        if not context:
            return None

        if not file_path:
            file_path = (
                f"evolution_{context.evolution_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        try:
            with open(file_path, "w") as f:
                json.dump(context.to_dict(), f, indent=2)

            logger.info(f"Exported context to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to export context: {e}")
            return None

    def _calculate_impact(self, tasks: list[dict[str, Any]]) -> float:
        """Calculate estimated impact of tasks.

        Args:
            tasks: List of tasks

        Returns:
            Impact score (0-1)
        """
        if not tasks:
            return 0.0

        # Simple heuristic based on task types and priorities
        impact_weights = {
            "add_docstrings": 0.3,
            "add_type_hints": 0.2,
            "reduce_complexity": 0.5,
            "fix_bug": 0.8,
            "optimize": 0.4,
            "refactor": 0.6,
        }

        total_impact = 0
        for task in tasks:
            task_type = task.get("type", "unknown")
            priority = task.get("priority", "medium")

            base_impact = impact_weights.get(task_type, 0.1)

            # Adjust by priority
            if priority == "high":
                base_impact *= 1.5
            elif priority == "low":
                base_impact *= 0.7

            total_impact += base_impact

        # Normalize to 0-1 range
        return min(1.0, total_impact / len(tasks))

    async def get_all_contexts(self) -> list[dict[str, Any]]:
        """Get all evolution contexts.

        Returns:
            List of context summaries
        """
        async with self.lock:
            summaries = []
            for evolution_id, context in self.contexts.items():
                summaries.append(
                    {
                        "evolution_id": evolution_id,
                        "created_at": context.created_at.isoformat(),
                        "target_path": context.target_path,
                        "status": context.status,
                        "current_phase": context.current_phase,
                        "focus_areas": context.focus_areas,
                        "has_errors": len(context.error_log) > 0,
                    }
                )
            return summaries


# Singleton instance
_context_store: Optional[SharedContextStore] = None


def get_context_store() -> SharedContextStore:
    """Get singleton context store instance.

    Returns:
        SharedContextStore instance
    """
    global _context_store
    if _context_store is None:
        _context_store = SharedContextStore()
    return _context_store
