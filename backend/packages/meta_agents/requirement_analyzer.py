"""Requirement Analyzer - AI-powered requirement analysis system."""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("meta_agents.requirement_analyzer")


class RequirementType(Enum):
    """Types of requirements."""

    FUNCTIONAL = "FUNCTIONAL"
    NON_FUNCTIONAL = "NON_FUNCTIONAL"
    CONSTRAINT = "CONSTRAINT"
    BUSINESS = "BUSINESS"
    TECHNICAL = "TECHNICAL"


class Priority(Enum):
    """Requirement priority levels."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Requirement:
    """Individual requirement representation."""

    id: str
    type: RequirementType
    priority: Priority
    description: str
    acceptance_criteria: list[str]
    dependencies: list[str]
    effort_hours: float
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate requirement completeness.

        Returns:
            True if valid
        """
        if not self.acceptance_criteria:
            return False
        if not self.description:
            return False
        if self.effort_hours < 0:
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "priority": self.priority.value,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
            "dependencies": self.dependencies,
            "effort_hours": self.effort_hours,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class AnalysisConfig:
    """Configuration for requirement analysis."""

    use_ai: bool = True
    use_consensus: bool = True
    min_confidence: float = 0.7
    max_requirements: int = 100
    auto_prioritize: bool = True
    estimate_effort: bool = True
    ai_models: list[str] = field(default_factory=lambda: ["claude", "gpt"])


class ConsensusEngine:
    """Multi-model consensus for requirement analysis."""

    def __init__(self):
        """Initialize consensus engine."""
        self.models = ["claude", "gpt"]
        self.weights = {"claude": 0.6, "gpt": 0.4}

    async def analyze(self, text: str) -> dict[str, Any]:
        """Analyze requirements using multiple models.

        Args:
            text: Requirements text

        Returns:
            Consensus analysis result
        """
        # Simulate calling multiple models
        responses = []

        claude_response = await self._call_claude(text)
        if claude_response:
            responses.append(claude_response)

        gpt_response = await self._call_gpt(text)
        if gpt_response:
            responses.append(gpt_response)

        # Calculate consensus
        consensus = self.calculate_consensus(responses)

        return {
            "consensus": consensus,
            "confidence": consensus.get("agreement_score", 0),
            "raw_responses": responses,
        }

    async def _call_claude(self, text: str) -> Optional[dict[str, Any]]:
        """Call Claude API (simulated).

        Args:
            text: Input text

        Returns:
            Claude's analysis
        """
        # In production, would call actual API
        return {
            "requirements": [
                {"type": "FUNCTIONAL", "description": "Extracted requirement", "priority": "HIGH"}
            ]
        }

    async def _call_gpt(self, text: str) -> Optional[dict[str, Any]]:
        """Call GPT API (simulated).

        Args:
            text: Input text

        Returns:
            GPT's analysis
        """
        # In production, would call actual API
        return {
            "requirements": [
                {"type": "FUNCTIONAL", "description": "Extracted requirement", "priority": "HIGH"}
            ]
        }

    def calculate_consensus(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate consensus from multiple responses.

        Args:
            responses: List of model responses

        Returns:
            Consensus result
        """
        if not responses:
            return {"requirements": [], "agreement_score": 0}

        # Extract all requirements
        all_reqs = []
        for response in responses:
            all_reqs.extend(response.get("requirements", []))

        # Calculate agreement score
        if len(responses) > 1:
            # Simple agreement: check if types and priorities match
            type_counts = {}
            priority_counts = {}

            for req in all_reqs:
                req_type = req.get("type", "")
                priority = req.get("priority", "")

                type_counts[req_type] = type_counts.get(req_type, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1

            # Agreement score based on most common values
            max_type_agreement = max(type_counts.values()) if type_counts else 0
            max_priority_agreement = max(priority_counts.values()) if priority_counts else 0

            # If there's complete disagreement, score should be low
            total_items = len(all_reqs)
            if total_items > 0:
                agreement_score = (max_type_agreement + max_priority_agreement) / (2 * total_items)
            else:
                agreement_score = 0
        else:
            agreement_score = 1.0

        # Check for conflicts
        conflicts = []
        if agreement_score < 0.5:
            conflicts.append("Low agreement between models")

        return {
            "requirements": all_reqs,
            "agreement_score": agreement_score,
            "conflicts": conflicts,
        }


class PatternMatcher:
    """Pattern matching for requirement detection."""

    def __init__(self):
        """Initialize pattern matcher."""
        self.functional_keywords = [
            "should",
            "must",
            "shall",
            "will",
            "can",
            "feature",
            "functionality",
            "capability",
            "user",
            "system",
            "admin",
            "customer",
        ]
        self.nonfunctional_keywords = [
            "performance",
            "security",
            "scalability",
            "reliability",
            "availability",
            "uptime",
            "response time",
            "throughput",
            "concurrent",
            "encryption",
            "backup",
            "disaster recovery",
        ]
        self.constraint_keywords = [
            "constraint",
            "limitation",
            "budget",
            "deadline",
            "must use",
            "restricted",
            "compatible",
            "existing",
        ]

    def detect_patterns(self, text: str) -> dict[str, Any]:
        """Detect requirement patterns in text.

        Args:
            text: Input text

        Returns:
            Detected patterns
        """
        text_lower = text.lower()

        # Count keyword occurrences
        functional_score = sum(1 for kw in self.functional_keywords if kw in text_lower)
        nonfunctional_score = sum(1 for kw in self.nonfunctional_keywords if kw in text_lower)
        constraint_score = sum(1 for kw in self.constraint_keywords if kw in text_lower)

        # Determine primary type
        scores = {
            RequirementType.FUNCTIONAL: functional_score,
            RequirementType.NON_FUNCTIONAL: nonfunctional_score,
            RequirementType.CONSTRAINT: constraint_score,
        }
        primary_type = max(scores, key=scores.get)

        # Extract features
        features = self._extract_features(text)

        # Detect categories
        categories = []
        if "performance" in text_lower or "response time" in text_lower:
            categories.append("performance")
        if "security" in text_lower or "encryption" in text_lower:
            categories.append("security")
        if "user" in text_lower or "authentication" in text_lower:
            categories.append("authentication")

        # Extract constraints
        constraints = []
        if "budget" in text_lower:
            constraints.append("budget")
        if "deadline" in text_lower or "by q" in text_lower:
            constraints.append("timeline")
        if "must use" in text_lower or "compatible" in text_lower:
            constraints.append("technology")

        # Extract keywords for functional requirements
        keywords = []
        if "authentication" in text_lower or "login" in text_lower:
            keywords.append("authentication")
        if "api" in text_lower:
            keywords.append("api")
        if "database" in text_lower:
            keywords.append("database")

        return {
            "type": primary_type,
            "features": features,
            "categories": categories,
            "constraints": constraints,
            "keywords": keywords,
        }

    def _extract_features(self, text: str) -> list[str]:
        """Extract feature descriptions from text.

        Args:
            text: Input text

        Returns:
            List of features
        """
        features = []

        # Look for bullet points or numbered lists
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith(("-", "*", "•")) or re.match(r"^\d+\.", line):
                # Clean up the line
                feature = re.sub(r"^[-*•\d.]\s*", "", line)
                if feature:
                    features.append(feature)

        return features

    def extract_acceptance_criteria(self, text: str) -> list[str]:
        """Extract acceptance criteria from text.

        Args:
            text: Input text

        Returns:
            List of acceptance criteria
        """
        criteria = []

        # Look for acceptance criteria section
        text_lower = text.lower()
        if "acceptance criteria" in text_lower:
            # Find the section
            start_idx = text_lower.index("acceptance criteria")
            section = text[start_idx:]

            # Extract bullet points after the header
            lines = section.split("\n")[1:]  # Skip the header line
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith(("-", "*", "•")) or re.match(r"^\d+\.", line):
                    criterion = re.sub(r"^[-*•\d.]\s*", "", line)
                    if criterion:
                        criteria.append(criterion)
                elif "user story" in line.lower() or not line[0].isalpha():
                    # Stop if we hit another section
                    break

        return criteria


class RequirementAnalyzer:
    """Main requirement analyzer agent."""

    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize requirement analyzer.

        Args:
            config: Analysis configuration
        """
        self.config = config or AnalysisConfig()
        self.consensus_engine = ConsensusEngine()
        self.pattern_matcher = PatternMatcher()
        self._requirement_counter = 0

    async def analyze_requirements(self, text: str) -> dict[str, Any]:
        """Analyze text-based requirements.

        Args:
            text: Requirements text

        Returns:
            Analysis result
        """
        # Detect patterns
        patterns = self.pattern_matcher.detect_patterns(text)

        # Extract requirements
        requirements = []
        features = patterns.get("features", [])

        for feature in features[: self.config.max_requirements]:
            self._requirement_counter += 1
            req = Requirement(
                id=f"REQ-{self._requirement_counter:03d}",
                type=patterns["type"],
                priority=Priority.MEDIUM,  # Default priority
                description=feature,
                acceptance_criteria=[feature],  # Simple criteria
                dependencies=[],
                effort_hours=2.0,  # Default estimate
            )
            requirements.append(req)

        # Separate by type
        functional = [r for r in requirements if r.type == RequirementType.FUNCTIONAL]
        non_functional = [r for r in requirements if r.type == RequirementType.NON_FUNCTIONAL]

        # Create summary
        summary = {
            "total_requirements": len(requirements),
            "functional_count": len(functional),
            "non_functional_count": len(non_functional),
            "estimated_effort": sum(r.effort_hours for r in requirements),
        }

        return {
            "requirements": requirements,
            "functional": functional,
            "non_functional": non_functional,
            "patterns": patterns,
            "summary": summary,
        }

    async def analyze_user_stories(self, stories: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze user stories.

        Args:
            stories: List of user stories

        Returns:
            Analysis result
        """
        requirements = []

        for story in stories:
            self._requirement_counter += 1

            # Extract acceptance criteria
            criteria = story.get("acceptance_criteria", [])

            req = Requirement(
                id=f"REQ-{self._requirement_counter:03d}",
                type=RequirementType.FUNCTIONAL,
                priority=Priority.MEDIUM,
                description=story.get("description", story.get("title", "")),
                acceptance_criteria=criteria,
                dependencies=[],
                effort_hours=len(criteria) * 1.0,  # 1 hour per criterion
            )

            requirements.append(req)

        total_effort = sum(r.effort_hours for r in requirements)

        return {
            "requirements": requirements,
            "total_effort": total_effort,
            "story_count": len(stories),
        }

    def prioritize_requirements(self, requirements: list[Requirement]) -> list[Requirement]:
        """Prioritize requirements.

        Args:
            requirements: List of requirements

        Returns:
            Prioritized list
        """
        # Define priority order
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3,
        }

        # Sort by priority and dependencies
        def sort_key(req: Requirement) -> tuple[int, int]:
            priority_score = priority_order[req.priority]
            dependency_score = len(req.dependencies)
            return (priority_score, dependency_score)

        return sorted(requirements, key=sort_key)

    async def estimate_effort(self, requirement: Requirement) -> Requirement:
        """Estimate effort for a requirement.

        Args:
            requirement: Requirement to estimate

        Returns:
            Requirement with effort estimate
        """
        # Simple heuristic based on acceptance criteria
        base_hours = len(requirement.acceptance_criteria) * 1.0

        # Adjust based on type
        if requirement.type == RequirementType.NON_FUNCTIONAL:
            base_hours *= 1.5  # Non-functional usually takes longer

        # Apply 4-hour rule
        if base_hours > 4.0:
            # Break down into subtasks
            num_subtasks = int(base_hours / 4.0) + 1
            requirement.effort_hours = 4.0
            requirement.metadata["breakdown"] = {
                "original_estimate": base_hours,
                "subtasks": num_subtasks,
                "subtask_hours": base_hours / num_subtasks,
            }
        else:
            requirement.effort_hours = base_hours
            requirement.metadata["breakdown"] = {"original_estimate": base_hours, "subtasks": 1}

        return requirement

    async def generate_document(self, requirements: list[Requirement]) -> str:
        """Generate requirements document.

        Args:
            requirements: List of requirements

        Returns:
            Markdown document
        """
        doc = ["# Requirements Document"]
        doc.append(f"\nGenerated: {datetime.now().isoformat()}")
        doc.append(f"\nTotal Requirements: {len(requirements)}")

        # Group by type
        by_type = {}
        for req in requirements:
            if req.type not in by_type:
                by_type[req.type] = []
            by_type[req.type].append(req)

        # Add sections
        for req_type, reqs in by_type.items():
            doc.append(f"\n## {req_type.value.replace('_', ' ').title()} Requirements")

            for req in reqs:
                doc.append(f"\n### {req.id}: {req.description}")
                doc.append(f"**Priority:** {req.priority.value}")
                doc.append(f"**Effort:** {req.effort_hours} hours")

                if req.acceptance_criteria:
                    doc.append("\n**Acceptance Criteria:**")
                    for criterion in req.acceptance_criteria:
                        doc.append(f"- {criterion}")

                if req.dependencies:
                    doc.append(f"\n**Dependencies:** {', '.join(req.dependencies)}")

        # Add summary
        total_effort = sum(r.effort_hours for r in requirements)
        doc.append("\n## Summary")
        doc.append(f"- Total Requirements: {len(requirements)}")
        doc.append(f"- Total Effort: {total_effort} hours")
        doc.append(f"- Estimated Days: {total_effort / 8:.1f} days")

        return "\n".join(doc)
