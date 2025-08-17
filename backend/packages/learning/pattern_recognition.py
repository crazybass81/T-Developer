"""
Pattern Recognition System for T-Developer

This module implements the core pattern recognition capabilities,
analyzing successful evolution cycles to identify reusable patterns.

The PatternRecognizer extracts patterns from successful operations,
analyzes code changes, and identifies successful strategies that can
be reused in future evolution cycles.
"""

from __future__ import annotations

import ast
import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional

from .pattern_database import Pattern, PatternDatabase

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT: int = 30
MAX_ANALYSIS_DEPTH: int = 5
MIN_PATTERN_CONFIDENCE: float = 0.7


@dataclass
class EvolutionCycle:
    """Data structure for evolution cycle analysis.

    Attributes:
        id: Unique cycle identifier
        phase: Evolution phase (research, planning, implementation, evaluation)
        task: Specific task being executed
        inputs: Input data for the cycle
        outputs: Output data from the cycle
        duration: Execution duration in seconds
        success: Whether cycle was successful
        metrics_before: Metrics before execution
        metrics_after: Metrics after execution
        code_changes: List of code changes made
        error_messages: Any error messages encountered
    """

    id: str
    phase: str
    task: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    duration: float
    success: bool
    metrics_before: dict[str, float]
    metrics_after: dict[str, float]
    code_changes: list[dict[str, Any]] = field(default_factory=list)
    error_messages: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PatternCandidate:
    """Candidate pattern identified during analysis.

    Attributes:
        context: Context where pattern applies
        action: Actions taken in the pattern
        outcome: Outcome achieved
        confidence: Confidence in pattern effectiveness
        supporting_cycles: Cycles that support this pattern
        frequency: How often this pattern appears
    """

    context: dict[str, Any]
    action: dict[str, Any]
    outcome: dict[str, Any]
    confidence: float
    supporting_cycles: list[str] = field(default_factory=list)
    frequency: int = 1


class PatternExtractor(ABC):
    """Abstract base class for pattern extractors."""

    @abstractmethod
    async def extract(self, cycles: list[EvolutionCycle]) -> list[PatternCandidate]:
        """Extract patterns from evolution cycles.

        Args:
            cycles: List of evolution cycles to analyze

        Returns:
            List of pattern candidates
        """
        pass


class CodePatternExtractor(PatternExtractor):
    """Extracts patterns from code changes."""

    def __init__(self) -> None:
        """Initialize code pattern extractor."""
        self.ast_patterns: dict[str, int] = {}
        self.import_patterns: dict[str, int] = {}
        self.method_patterns: dict[str, int] = {}

    async def extract(self, cycles: list[EvolutionCycle]) -> list[PatternCandidate]:
        """Extract code change patterns.

        Args:
            cycles: Evolution cycles with code changes

        Returns:
            List of code pattern candidates
        """
        successful_cycles = [c for c in cycles if c.success]
        if not successful_cycles:
            return []

        patterns = []

        # Analyze AST patterns
        ast_patterns = await self._extract_ast_patterns(successful_cycles)
        patterns.extend(ast_patterns)

        # Analyze import patterns
        import_patterns = await self._extract_import_patterns(successful_cycles)
        patterns.extend(import_patterns)

        # Analyze method patterns
        method_patterns = await self._extract_method_patterns(successful_cycles)
        patterns.extend(method_patterns)

        return patterns

    async def _extract_ast_patterns(self, cycles: list[EvolutionCycle]) -> list[PatternCandidate]:
        """Extract patterns from AST analysis."""
        patterns = []
        ast_changes: dict[str, list[str]] = {}

        for cycle in cycles:
            for change in cycle.code_changes:
                if change.get("type") == "python" and "content" in change:
                    try:
                        tree = ast.parse(change["content"])
                        ast_signature = self._get_ast_signature(tree)

                        if ast_signature not in ast_changes:
                            ast_changes[ast_signature] = []
                        ast_changes[ast_signature].append(cycle.id)

                    except SyntaxError:
                        continue

        # Create patterns for frequently occurring AST structures
        for signature, cycle_ids in ast_changes.items():
            if len(cycle_ids) >= 2:  # Pattern must appear in at least 2 cycles
                pattern = PatternCandidate(
                    context={"code_structure": signature, "file_types": ["python"]},
                    action={"type": "code_change", "ast_pattern": signature},
                    outcome={
                        "success_rate": 1.0,  # All were successful
                        "improvement_type": "code_structure",
                    },
                    confidence=min(0.9, len(cycle_ids) / len(cycles)),
                    supporting_cycles=cycle_ids,
                    frequency=len(cycle_ids),
                )
                patterns.append(pattern)

        return patterns

    def _get_ast_signature(self, tree: ast.AST) -> str:
        """Generate signature for AST structure."""
        signature_parts = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                signature_parts.append(f"func:{node.name}")
            elif isinstance(node, ast.ClassDef):
                signature_parts.append(f"class:{node.name}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    signature_parts.append(f"import:{alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or "relative"
                signature_parts.append(f"from:{module}")

        return hashlib.md5("|".join(sorted(signature_parts)).encode()).hexdigest()[:8]

    async def _extract_import_patterns(
        self, cycles: list[EvolutionCycle]
    ) -> list[PatternCandidate]:
        """Extract import usage patterns."""
        patterns = []
        import_contexts: dict[str, dict[str, Any]] = {}

        for cycle in cycles:
            cycle_imports = set()

            for change in cycle.code_changes:
                if change.get("type") == "python" and "content" in change:
                    try:
                        tree = ast.parse(change["content"])
                        imports = self._extract_imports(tree)
                        cycle_imports.update(imports)
                    except SyntaxError:
                        continue

            # Track import combinations
            import_signature = "|".join(sorted(cycle_imports))
            if import_signature and len(cycle_imports) > 1:
                if import_signature not in import_contexts:
                    import_contexts[import_signature] = {
                        "imports": list(cycle_imports),
                        "cycles": [],
                        "metrics_improvements": [],
                    }

                import_contexts[import_signature]["cycles"].append(cycle.id)

                # Calculate metrics improvement
                improvement = self._calculate_metrics_improvement(
                    cycle.metrics_before, cycle.metrics_after
                )
                import_contexts[import_signature]["metrics_improvements"].append(improvement)

        # Create patterns for import combinations
        for signature, context in import_contexts.items():
            if len(context["cycles"]) >= 2:
                avg_improvement = sum(context["metrics_improvements"]) / len(
                    context["metrics_improvements"]
                )

                pattern = PatternCandidate(
                    context={"imports_needed": context["imports"], "file_types": ["python"]},
                    action={"type": "code_change", "add_imports": context["imports"]},
                    outcome={"metrics_improvement": avg_improvement, "success_rate": 1.0},
                    confidence=min(0.9, len(context["cycles"]) / len(cycles)),
                    supporting_cycles=context["cycles"],
                    frequency=len(context["cycles"]),
                )
                patterns.append(pattern)

        return patterns

    def _extract_imports(self, tree: ast.AST) -> set[str]:
        """Extract import statements from AST."""
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.add(f"{module}.{alias.name}")

        return imports

    async def _extract_method_patterns(
        self, cycles: list[EvolutionCycle]
    ) -> list[PatternCandidate]:
        """Extract method implementation patterns."""
        patterns = []
        method_signatures: dict[str, list[str]] = {}

        for cycle in cycles:
            for change in cycle.code_changes:
                if change.get("type") == "python" and "content" in change:
                    try:
                        tree = ast.parse(change["content"])
                        methods = self._extract_method_signatures(tree)

                        for signature in methods:
                            if signature not in method_signatures:
                                method_signatures[signature] = []
                            method_signatures[signature].append(cycle.id)

                    except SyntaxError:
                        continue

        # Create patterns for common method signatures
        for signature, cycle_ids in method_signatures.items():
            if len(cycle_ids) >= 2:
                pattern = PatternCandidate(
                    context={"method_signature": signature, "file_types": ["python"]},
                    action={"type": "code_change", "method_pattern": signature},
                    outcome={"success_rate": 1.0, "code_quality": "improved"},
                    confidence=min(0.8, len(cycle_ids) / len(cycles)),
                    supporting_cycles=cycle_ids,
                    frequency=len(cycle_ids),
                )
                patterns.append(pattern)

        return patterns

    def _extract_method_signatures(self, tree: ast.AST) -> list[str]:
        """Extract method signatures from AST."""
        signatures = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                returns = ""
                if node.returns:
                    if isinstance(node.returns, ast.Name):
                        returns = node.returns.id
                    elif isinstance(node.returns, ast.Constant):
                        returns = str(node.returns.value)

                signature = f"{node.name}({','.join(args)})->{returns}"
                signatures.append(signature)

        return signatures

    def _calculate_metrics_improvement(
        self, before: dict[str, float], after: dict[str, float]
    ) -> float:
        """Calculate overall metrics improvement."""
        if not before or not after:
            return 0.0

        improvements = []
        for metric in ["coverage", "complexity", "docstring_coverage"]:
            if metric in before and metric in after:
                if before[metric] > 0:
                    improvement = (after[metric] - before[metric]) / before[metric]
                    improvements.append(improvement)

        return sum(improvements) / len(improvements) if improvements else 0.0


class MetricsPatternExtractor(PatternExtractor):
    """Extracts patterns from metrics improvements."""

    async def extract(self, cycles: list[EvolutionCycle]) -> list[PatternCandidate]:
        """Extract metrics improvement patterns.

        Args:
            cycles: Evolution cycles with metrics data

        Returns:
            List of metrics pattern candidates
        """
        successful_cycles = [c for c in cycles if c.success and c.metrics_after]
        if not successful_cycles:
            return []

        patterns = []

        # Group cycles by improvement type
        improvement_groups = self._group_by_improvement_type(successful_cycles)

        for improvement_type, group_cycles in improvement_groups.items():
            if len(group_cycles) >= 2:
                pattern = await self._create_metrics_pattern(improvement_type, group_cycles)
                if pattern:
                    patterns.append(pattern)

        return patterns

    def _group_by_improvement_type(
        self, cycles: list[EvolutionCycle]
    ) -> dict[str, list[EvolutionCycle]]:
        """Group cycles by type of improvement achieved."""
        groups: dict[str, list[EvolutionCycle]] = {}

        for cycle in cycles:
            improvement_types = self._classify_improvement(cycle)

            for improvement_type in improvement_types:
                if improvement_type not in groups:
                    groups[improvement_type] = []
                groups[improvement_type].append(cycle)

        return groups

    def _classify_improvement(self, cycle: EvolutionCycle) -> list[str]:
        """Classify the type of improvement achieved."""
        improvements = []

        before = cycle.metrics_before
        after = cycle.metrics_after

        if not before or not after:
            return improvements

        # Coverage improvement
        if "coverage" in before and "coverage" in after:
            if after["coverage"] > before["coverage"] + 5:  # 5% improvement
                improvements.append("coverage_improvement")

        # Complexity improvement
        if "complexity" in before and "complexity" in after:
            if after["complexity"] > before["complexity"] + 5:  # 5 point improvement
                improvements.append("complexity_improvement")

        # Documentation improvement
        if "docstring_coverage" in before and "docstring_coverage" in after:
            if after["docstring_coverage"] > before["docstring_coverage"] + 10:  # 10% improvement
                improvements.append("documentation_improvement")

        # Performance improvement
        if "performance_score" in before and "performance_score" in after:
            if after["performance_score"] > before["performance_score"] + 0.1:
                improvements.append("performance_improvement")

        return improvements

    async def _create_metrics_pattern(
        self, improvement_type: str, cycles: list[EvolutionCycle]
    ) -> Optional[PatternCandidate]:
        """Create pattern from metrics improvement data."""
        if not cycles:
            return None

        # Analyze common context
        common_context = self._find_common_context(cycles)

        # Analyze common actions
        common_actions = self._find_common_actions(cycles)

        # Calculate average improvement
        avg_improvement = self._calculate_average_improvement(cycles, improvement_type)

        if not common_actions or avg_improvement <= 0:
            return None

        pattern = PatternCandidate(
            context=common_context,
            action=common_actions,
            outcome={
                "improvement_type": improvement_type,
                "average_improvement": avg_improvement,
                "success_rate": 1.0,
            },
            confidence=min(0.9, len(cycles) / 10),  # Higher confidence with more examples
            supporting_cycles=[c.id for c in cycles],
            frequency=len(cycles),
        )

        return pattern

    def _find_common_context(self, cycles: list[EvolutionCycle]) -> dict[str, Any]:
        """Find common context across cycles."""
        context = {}

        # Common phases
        phases = [c.phase for c in cycles]
        if len(set(phases)) == 1:
            context["phase"] = phases[0]

        # Common task types
        tasks = [c.task for c in cycles]
        task_types = [t.split("_")[0] for t in tasks if "_" in t]
        if task_types and len(set(task_types)) == 1:
            context["task_type"] = task_types[0]

        # Common input patterns
        input_keys = set()
        for cycle in cycles:
            input_keys.update(cycle.inputs.keys())

        common_keys = input_keys
        for cycle in cycles:
            common_keys = common_keys.intersection(set(cycle.inputs.keys()))

        if common_keys:
            context["required_inputs"] = list(common_keys)

        return context

    def _find_common_actions(self, cycles: list[EvolutionCycle]) -> dict[str, Any]:
        """Find common actions across cycles."""
        actions = {"type": "metrics_improvement"}

        # Common code change patterns
        change_types = []
        for cycle in cycles:
            for change in cycle.code_changes:
                if "type" in change:
                    change_types.append(change["type"])

        if change_types:
            most_common_type = max(set(change_types), key=change_types.count)
            actions["primary_change_type"] = most_common_type

        # Common tools used
        tools_used = []
        for cycle in cycles:
            if "tools" in cycle.inputs:
                tools_used.extend(cycle.inputs["tools"])

        if tools_used:
            common_tools = [
                tool for tool in set(tools_used) if tools_used.count(tool) >= len(cycles) / 2
            ]
            if common_tools:
                actions["tools"] = common_tools

        return actions

    def _calculate_average_improvement(
        self, cycles: list[EvolutionCycle], improvement_type: str
    ) -> float:
        """Calculate average improvement for the given type."""
        improvements = []

        metric_map = {
            "coverage_improvement": "coverage",
            "complexity_improvement": "complexity",
            "documentation_improvement": "docstring_coverage",
            "performance_improvement": "performance_score",
        }

        metric_name = metric_map.get(improvement_type)
        if not metric_name:
            return 0.0

        for cycle in cycles:
            before = cycle.metrics_before.get(metric_name, 0)
            after = cycle.metrics_after.get(metric_name, 0)

            if before > 0:
                improvement = (after - before) / before
                improvements.append(improvement)

        return sum(improvements) / len(improvements) if improvements else 0.0


class PatternRecognizer:
    """Main pattern recognition system.

    Analyzes evolution cycles to identify reusable patterns that can
    improve future evolution cycles. Combines multiple extraction
    strategies to build a comprehensive pattern database.

    Example:
        >>> recognizer = PatternRecognizer()
        >>> await recognizer.initialize()
        >>> patterns = await recognizer.extract_patterns(cycles)
        >>> await recognizer.store_patterns(patterns)
    """

    def __init__(self, pattern_db: Optional[PatternDatabase] = None) -> None:
        """Initialize pattern recognizer.

        Args:
            pattern_db: Pattern database instance (creates new if None)
        """
        self.pattern_db = pattern_db or PatternDatabase()
        self.extractors: list[PatternExtractor] = [
            CodePatternExtractor(),
            MetricsPatternExtractor(),
        ]
        self.logger = logging.getLogger(self.__class__.__name__)
        self._analysis_cache: dict[str, list[PatternCandidate]] = {}

    async def initialize(self) -> None:
        """Initialize the pattern recognizer."""
        await self.pattern_db.initialize()
        self.logger.info("Pattern recognizer initialized")

    async def extract_patterns(
        self, cycles: list[EvolutionCycle], min_confidence: float = MIN_PATTERN_CONFIDENCE
    ) -> list[Pattern]:
        """Extract patterns from evolution cycles.

        Args:
            cycles: List of evolution cycles to analyze
            min_confidence: Minimum confidence threshold for patterns

        Returns:
            List of extracted patterns

        Raises:
            ValueError: If cycles list is empty
            TimeoutError: If analysis exceeds timeout
        """
        if not cycles:
            raise ValueError("Cannot extract patterns from empty cycles list")

        self.logger.info(f"Extracting patterns from {len(cycles)} cycles")

        try:
            # Create cache key
            cycle_ids = sorted([c.id for c in cycles])
            cache_key = hashlib.md5("|".join(cycle_ids).encode()).hexdigest()

            # Check cache
            if cache_key in self._analysis_cache:
                candidates = self._analysis_cache[cache_key]
                self.logger.info(f"Using cached analysis for {len(cycles)} cycles")
            else:
                # Extract patterns using all extractors
                all_candidates = []

                for extractor in self.extractors:
                    try:
                        candidates = await asyncio.wait_for(
                            extractor.extract(cycles), timeout=DEFAULT_TIMEOUT
                        )
                        all_candidates.extend(candidates)
                        self.logger.debug(
                            f"{extractor.__class__.__name__} extracted {len(candidates)} candidates"
                        )
                    except asyncio.TimeoutError:
                        self.logger.warning(f"{extractor.__class__.__name__} extraction timed out")
                        continue
                    except Exception as e:
                        self.logger.error(f"Error in {extractor.__class__.__name__}: {e}")
                        continue

                # Cache results
                self._analysis_cache[cache_key] = all_candidates
                candidates = all_candidates

            # Convert candidates to patterns
            patterns = await self._candidates_to_patterns(candidates, min_confidence)

            # Merge similar patterns
            merged_patterns = await self._merge_similar_patterns(patterns)

            self.logger.info(
                f"Extracted {len(merged_patterns)} patterns with confidence >= {min_confidence}"
            )
            return merged_patterns

        except Exception as e:
            self.logger.error(f"Pattern extraction failed: {e}")
            raise

    async def _candidates_to_patterns(
        self, candidates: list[PatternCandidate], min_confidence: float
    ) -> list[Pattern]:
        """Convert pattern candidates to patterns."""
        patterns = []

        for candidate in candidates:
            if candidate.confidence >= min_confidence:
                pattern = Pattern(
                    id=f"pattern_{hashlib.md5(str(candidate).encode()).hexdigest()[:8]}",
                    category=self._classify_pattern_category(candidate),
                    name=self._generate_pattern_name(candidate),
                    description=self._generate_pattern_description(candidate),
                    context=candidate.context,
                    action=candidate.action,
                    outcome=candidate.outcome,
                    success_rate=candidate.confidence,
                    usage_count=candidate.frequency,
                    created_at=datetime.now(),
                    tags=self._generate_pattern_tags(candidate),
                    confidence=candidate.confidence,
                )
                patterns.append(pattern)

        return patterns

    def _classify_pattern_category(self, candidate: PatternCandidate) -> str:
        """Classify pattern category based on candidate."""
        if "improvement_type" in candidate.outcome:
            improvement_type = candidate.outcome["improvement_type"]
            if "coverage" in improvement_type:
                return "testing"
            elif "complexity" in improvement_type:
                return "refactoring"
            elif "documentation" in improvement_type:
                return "documentation"
            elif "performance" in improvement_type:
                return "performance"

        if candidate.action.get("type") == "code_change":
            return "improvement"

        return "optimization"

    def _generate_pattern_name(self, candidate: PatternCandidate) -> str:
        """Generate human-readable pattern name."""
        if "improvement_type" in candidate.outcome:
            improvement = candidate.outcome["improvement_type"].replace("_", " ").title()
            return f"Auto {improvement} Pattern"

        if "ast_pattern" in candidate.action:
            return f"Code Structure Pattern {candidate.action['ast_pattern']}"

        if "imports_needed" in candidate.context:
            imports = candidate.context["imports_needed"][:2]  # First 2 imports
            return f"Import Pattern: {', '.join(imports)}"

        return f"Evolution Pattern {candidate.frequency}x"

    def _generate_pattern_description(self, candidate: PatternCandidate) -> str:
        """Generate pattern description."""
        if "improvement_type" in candidate.outcome:
            improvement = candidate.outcome["improvement_type"]
            avg_improvement = candidate.outcome.get("average_improvement", 0)
            return f"Automatically improves {improvement} by an average of {avg_improvement:.1%}"

        if "ast_pattern" in candidate.action:
            return "Code structure pattern that consistently leads to successful outcomes"

        if "imports_needed" in candidate.context:
            imports = candidate.context["imports_needed"]
            return f"Import combination pattern using {len(imports)} imports"

        return f"Pattern observed in {candidate.frequency} successful evolution cycles"

    def _generate_pattern_tags(self, candidate: PatternCandidate) -> list[str]:
        """Generate tags for pattern."""
        tags = ["auto_extracted"]

        if "improvement_type" in candidate.outcome:
            tags.append(candidate.outcome["improvement_type"])

        if "file_types" in candidate.context:
            tags.extend(candidate.context["file_types"])

        if candidate.action.get("type"):
            tags.append(candidate.action["type"])

        if candidate.frequency >= 5:
            tags.append("high_frequency")
        elif candidate.frequency >= 3:
            tags.append("medium_frequency")
        else:
            tags.append("low_frequency")

        if candidate.confidence >= 0.9:
            tags.append("high_confidence")
        elif candidate.confidence >= 0.7:
            tags.append("medium_confidence")
        else:
            tags.append("low_confidence")

        return list(set(tags))  # Remove duplicates

    async def _merge_similar_patterns(self, patterns: list[Pattern]) -> list[Pattern]:
        """Merge patterns that are very similar."""
        if len(patterns) <= 1:
            return patterns

        merged = []
        used_indices = set()

        for i, pattern1 in enumerate(patterns):
            if i in used_indices:
                continue

            similar_patterns = [pattern1]
            used_indices.add(i)

            for j, pattern2 in enumerate(patterns[i + 1 :], i + 1):
                if j in used_indices:
                    continue

                similarity = await self._calculate_pattern_similarity(pattern1, pattern2)
                if similarity >= 0.8:  # 80% similarity threshold
                    similar_patterns.append(pattern2)
                    used_indices.add(j)

            # Merge similar patterns
            if len(similar_patterns) > 1:
                merged_pattern = await self._merge_patterns(similar_patterns)
                merged.append(merged_pattern)
            else:
                merged.append(pattern1)

        return merged

    async def _calculate_pattern_similarity(self, pattern1: Pattern, pattern2: Pattern) -> float:
        """Calculate similarity between two patterns."""
        similarity_scores = []

        # Category similarity
        if pattern1.category == pattern2.category:
            similarity_scores.append(1.0)
        else:
            similarity_scores.append(0.0)

        # Context similarity
        context_similarity = self._calculate_dict_similarity(pattern1.context, pattern2.context)
        similarity_scores.append(context_similarity)

        # Action similarity
        action_similarity = self._calculate_dict_similarity(pattern1.action, pattern2.action)
        similarity_scores.append(action_similarity)

        # Tag similarity
        tags1 = set(pattern1.tags)
        tags2 = set(pattern2.tags)
        if tags1 or tags2:
            tag_similarity = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
            similarity_scores.append(tag_similarity)

        return sum(similarity_scores) / len(similarity_scores)

    def _calculate_dict_similarity(self, dict1: dict[str, Any], dict2: dict[str, Any]) -> float:
        """Calculate similarity between two dictionaries."""
        if not dict1 and not dict2:
            return 1.0
        if not dict1 or not dict2:
            return 0.0

        all_keys = set(dict1.keys()).union(set(dict2.keys()))
        matching_keys = 0

        for key in all_keys:
            if key in dict1 and key in dict2:
                if dict1[key] == dict2[key]:
                    matching_keys += 1

        return matching_keys / len(all_keys) if all_keys else 0.0

    async def _merge_patterns(self, patterns: list[Pattern]) -> Pattern:
        """Merge multiple similar patterns into one."""
        base_pattern = patterns[0]

        # Combine usage counts and recalculate confidence
        total_usage = sum(p.usage_count for p in patterns)
        avg_confidence = sum(p.confidence for p in patterns) / len(patterns)

        # Merge tags
        all_tags = set()
        for pattern in patterns:
            all_tags.update(pattern.tags)

        merged_pattern = Pattern(
            id=base_pattern.id,
            category=base_pattern.category,
            name=f"Merged {base_pattern.name}",
            description=f"Merged pattern from {len(patterns)} similar patterns: {base_pattern.description}",
            context=base_pattern.context,
            action=base_pattern.action,
            outcome=base_pattern.outcome,
            success_rate=avg_confidence,
            usage_count=total_usage,
            created_at=base_pattern.created_at,
            last_used=max(p.last_used for p in patterns if p.last_used),
            tags=list(all_tags),
            confidence=avg_confidence,
        )

        return merged_pattern

    async def store_patterns(self, patterns: list[Pattern]) -> None:
        """Store extracted patterns in the database.

        Args:
            patterns: List of patterns to store

        Raises:
            RuntimeError: If storage fails
        """
        try:
            stored_count = 0
            for pattern in patterns:
                # Check if pattern already exists
                existing = await self.pattern_db.get_pattern(pattern.id)
                if existing:
                    # Update existing pattern
                    existing.usage_count += pattern.usage_count
                    existing.confidence = (existing.confidence + pattern.confidence) / 2
                    existing.last_used = datetime.now()
                    await self.pattern_db.update_pattern(existing)
                else:
                    # Store new pattern
                    await self.pattern_db.store_pattern(pattern)
                    stored_count += 1

            self.logger.info(
                f"Stored {stored_count} new patterns, updated {len(patterns) - stored_count} existing"
            )

        except Exception as e:
            self.logger.error(f"Failed to store patterns: {e}")
            raise RuntimeError(f"Pattern storage failed: {e}")

    async def find_applicable_patterns(
        self, context: dict[str, Any], limit: int = 10
    ) -> list[Pattern]:
        """Find patterns applicable to the given context.

        Args:
            context: Current context to match patterns against
            limit: Maximum number of patterns to return

        Returns:
            List of applicable patterns sorted by relevance
        """
        try:
            # Get all patterns
            all_patterns = await self.pattern_db.get_all_patterns()

            # Score patterns by relevance to context
            scored_patterns = []
            for pattern in all_patterns:
                relevance_score = await self._calculate_relevance_score(pattern, context)
                if relevance_score > 0.3:  # Minimum relevance threshold
                    scored_patterns.append((pattern, relevance_score))

            # Sort by relevance score
            scored_patterns.sort(key=lambda x: x[1], reverse=True)

            # Return top patterns
            return [pattern for pattern, score in scored_patterns[:limit]]

        except Exception as e:
            self.logger.error(f"Failed to find applicable patterns: {e}")
            return []

    async def _calculate_relevance_score(self, pattern: Pattern, context: dict[str, Any]) -> float:
        """Calculate how relevant a pattern is to the given context."""
        score_components = []

        # Context matching
        context_match = self._calculate_dict_similarity(pattern.context, context)
        score_components.append(context_match * 0.4)  # 40% weight

        # Pattern confidence
        score_components.append(pattern.confidence * 0.3)  # 30% weight

        # Usage frequency (normalized)
        frequency_score = min(1.0, pattern.usage_count / 10)  # Cap at 10 uses
        score_components.append(frequency_score * 0.2)  # 20% weight

        # Recency (patterns used recently are more relevant)
        if pattern.last_used:
            days_since_use = (datetime.now() - pattern.last_used).days
            recency_score = max(0.0, 1.0 - (days_since_use / 30))  # Decay over 30 days
            score_components.append(recency_score * 0.1)  # 10% weight
        else:
            score_components.append(0.0)

        return sum(score_components)

    async def get_pattern_statistics(self) -> dict[str, Any]:
        """Get statistics about the pattern database.

        Returns:
            Dictionary containing pattern statistics
        """
        try:
            all_patterns = await self.pattern_db.get_all_patterns()

            if not all_patterns:
                return {"total_patterns": 0}

            stats = {
                "total_patterns": len(all_patterns),
                "categories": {},
                "average_confidence": sum(p.confidence for p in all_patterns) / len(all_patterns),
                "total_usage": sum(p.usage_count for p in all_patterns),
                "most_used_pattern": max(all_patterns, key=lambda p: p.usage_count).name,
                "highest_confidence_pattern": max(all_patterns, key=lambda p: p.confidence).name,
                "recent_patterns": len(
                    [p for p in all_patterns if p.created_at > datetime.now() - timedelta(days=7)]
                ),
            }

            # Category breakdown
            for pattern in all_patterns:
                category = pattern.category
                if category not in stats["categories"]:
                    stats["categories"][category] = {"count": 0, "avg_confidence": 0.0}
                stats["categories"][category]["count"] += 1

            # Calculate average confidence per category
            for category in stats["categories"]:
                category_patterns = [p for p in all_patterns if p.category == category]
                if category_patterns:
                    avg_confidence = sum(p.confidence for p in category_patterns) / len(
                        category_patterns
                    )
                    stats["categories"][category]["avg_confidence"] = avg_confidence

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get pattern statistics: {e}")
            return {"error": str(e)}
