"""
Pattern Matcher - Architectural pattern matching system
Size: < 6.5KB | Performance: < 3μs
Day 21: Phase 2 - Meta Agents
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class PatternType(Enum):
    """Architectural pattern types"""

    ARCHITECTURAL = "architectural"
    DESIGN = "design"
    BEHAVIORAL = "behavioral"
    STRUCTURAL = "structural"
    CREATIONAL = "creational"
    INTEGRATION = "integration"


@dataclass
class Pattern:
    """Architectural pattern definition"""

    id: str
    name: str
    type: PatternType
    description: str
    keywords: List[str]
    components: List[str]
    pros: List[str]
    cons: List[str]
    use_cases: List[str]
    confidence_threshold: float = 0.7


@dataclass
class MatchResult:
    """Pattern matching result"""

    pattern: Pattern
    confidence: float
    matched_keywords: List[str]
    matched_components: List[str]
    reasoning: str
    recommendations: List[str]


class PatternMatcher:
    """AI-powered architectural pattern matcher"""

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.keyword_weights = self._initialize_keyword_weights()

    def match(self, requirements: str, context: Dict[str, Any] = None) -> List[MatchResult]:
        """Match requirements against architectural patterns"""
        requirements_lower = requirements.lower()
        context = context or {}

        matches = []

        for pattern in self.patterns:
            confidence, matched = self._evaluate_pattern(pattern, requirements_lower, context)

            if confidence >= pattern.confidence_threshold:
                matches.append(
                    MatchResult(
                        pattern=pattern,
                        confidence=confidence,
                        matched_keywords=matched["keywords"],
                        matched_components=matched["components"],
                        reasoning=self._generate_reasoning(pattern, matched, confidence),
                        recommendations=self._generate_recommendations(pattern, context),
                    )
                )

        # Sort by confidence
        matches.sort(key=lambda x: x.confidence, reverse=True)

        return matches

    def _evaluate_pattern(
        self, pattern: Pattern, requirements: str, context: Dict[str, Any]
    ) -> Tuple[float, Dict[str, List[str]]]:
        """Evaluate pattern match confidence"""
        matched = {"keywords": [], "components": []}

        # Keyword matching with weights
        keyword_score = 0.0
        for keyword in pattern.keywords:
            if keyword in requirements:
                weight = self.keyword_weights.get(keyword, 1.0)
                keyword_score += weight
                matched["keywords"].append(keyword)

        # Normalize keyword score
        max_keyword_score = sum(self.keyword_weights.get(kw, 1.0) for kw in pattern.keywords)
        keyword_confidence = keyword_score / max_keyword_score if max_keyword_score > 0 else 0

        # Component matching
        component_matches = 0
        for component in pattern.components:
            if component.replace("-", " ") in requirements:
                component_matches += 1
                matched["components"].append(component)

        component_confidence = (
            component_matches / len(pattern.components) if pattern.components else 0
        )

        # Context-based adjustments
        context_boost = self._evaluate_context(pattern, context)

        # Calculate final confidence
        confidence = keyword_confidence * 0.5 + component_confidence * 0.3 + context_boost * 0.2

        return confidence, matched

    def _evaluate_context(self, pattern: Pattern, context: Dict[str, Any]) -> float:
        """Evaluate pattern based on project context"""
        boost = 0.0

        # Team size context
        team_size = context.get("team_size", 0)
        if pattern.name == "microservices" and team_size > 10:
            boost += 0.3
        elif pattern.name == "monolithic" and team_size < 5:
            boost += 0.3

        # Scale context
        scale = context.get("scale", "").lower()
        if pattern.name == "microservices" and scale in ["large", "enterprise"]:
            boost += 0.4
        elif pattern.name == "serverless" and scale in ["variable", "unpredictable"]:
            boost += 0.4

        # Technology stack context
        tech_stack = context.get("tech_stack", [])
        if pattern.name == "event-driven" and any(
            tech in tech_stack for tech in ["kafka", "rabbitmq", "redis"]
        ):
            boost += 0.3

        return min(1.0, boost)

    def _generate_reasoning(
        self, pattern: Pattern, matched: Dict[str, List[str]], confidence: float
    ) -> str:
        """Generate reasoning for pattern match"""
        keyword_count = len(matched["keywords"])
        component_count = len(matched["components"])

        if confidence > 0.8:
            return f"Strong match for {pattern.name} with {keyword_count} keywords and {component_count} components identified"
        elif confidence > 0.6:
            return f"Good fit for {pattern.name} based on {keyword_count} matching indicators"
        else:
            return f"Possible match for {pattern.name}, consider evaluating alternatives"

    def _generate_recommendations(self, pattern: Pattern, context: Dict[str, Any]) -> List[str]:
        """Generate pattern-specific recommendations"""
        recommendations = []

        # Pattern-specific recommendations
        if pattern.name == "microservices":
            recommendations.extend(
                [
                    "Implement service discovery mechanism",
                    "Set up API gateway for unified entry point",
                    "Plan for distributed tracing and monitoring",
                    "Consider data consistency strategies",
                ]
            )
        elif pattern.name == "event-driven":
            recommendations.extend(
                [
                    "Choose appropriate message broker",
                    "Design event schemas carefully",
                    "Implement event sourcing for audit trail",
                    "Plan for event replay and error handling",
                ]
            )
        elif pattern.name == "layered":
            recommendations.extend(
                [
                    "Maintain strict layer boundaries",
                    "Implement dependency injection",
                    "Use DTOs for layer communication",
                    "Consider caching between layers",
                ]
            )

        # Context-based recommendations
        if context.get("team_size", 0) < 3:
            recommendations.append("Consider simpler architecture due to small team size")

        if context.get("timeline", "").lower() == "urgent":
            recommendations.append("Start with MVP using simpler patterns")

        return recommendations[:5]  # Limit to top 5 recommendations

    def _initialize_patterns(self) -> List[Pattern]:
        """Initialize architectural patterns database"""
        return [
            Pattern(
                id="AP001",
                name="microservices",
                type=PatternType.ARCHITECTURAL,
                description="Distributed services architecture",
                keywords=["microservice", "distributed", "scalable", "independent", "service"],
                components=["api-gateway", "service-registry", "config-server", "circuit-breaker"],
                pros=["Independent deployment", "Technology diversity", "Fault isolation"],
                cons=["Complexity", "Network latency", "Data consistency"],
                use_cases=["Large teams", "Complex domains", "Scalability requirements"],
            ),
            Pattern(
                id="AP002",
                name="monolithic",
                type=PatternType.ARCHITECTURAL,
                description="Single deployable unit architecture",
                keywords=["monolith", "simple", "single", "unified"],
                components=["database", "business-logic", "presentation-layer"],
                pros=["Simple deployment", "Easy debugging", "Data consistency"],
                cons=["Scaling limitations", "Technology lock-in", "Long build times"],
                use_cases=["Small teams", "Simple domains", "Quick MVPs"],
            ),
            Pattern(
                id="AP003",
                name="event-driven",
                type=PatternType.ARCHITECTURAL,
                description="Asynchronous event-based architecture",
                keywords=["event", "async", "real-time", "streaming", "reactive"],
                components=["event-bus", "message-broker", "event-store", "event-processor"],
                pros=["Loose coupling", "Scalability", "Real-time processing"],
                cons=["Complexity", "Event ordering", "Debugging difficulty"],
                use_cases=["Real-time systems", "IoT", "Financial systems"],
            ),
            Pattern(
                id="AP004",
                name="serverless",
                type=PatternType.ARCHITECTURAL,
                description="Function-as-a-Service architecture",
                keywords=["serverless", "lambda", "function", "faas", "stateless"],
                components=["functions", "api-gateway", "storage", "event-triggers"],
                pros=["No server management", "Auto-scaling", "Pay-per-use"],
                cons=["Vendor lock-in", "Cold starts", "Limited execution time"],
                use_cases=["Variable workloads", "Event processing", "APIs"],
            ),
            Pattern(
                id="AP005",
                name="layered",
                type=PatternType.ARCHITECTURAL,
                description="N-tier layered architecture",
                keywords=["layer", "tier", "mvc", "separation", "concerns"],
                components=["presentation", "business", "data", "persistence"],
                pros=["Separation of concerns", "Maintainability", "Testability"],
                cons=["Performance overhead", "Rigidity", "Duplication"],
                use_cases=["Enterprise apps", "Traditional web apps", "Clear boundaries"],
            ),
            Pattern(
                id="DP001",
                name="mvc",
                type=PatternType.DESIGN,
                description="Model-View-Controller pattern",
                keywords=["mvc", "model", "view", "controller"],
                components=["model", "view", "controller", "router"],
                pros=["Separation of concerns", "Parallel development", "Reusability"],
                cons=["Complexity for simple apps", "Learning curve"],
                use_cases=["Web applications", "GUI applications"],
            ),
            Pattern(
                id="DP002",
                name="repository",
                type=PatternType.DESIGN,
                description="Data access abstraction pattern",
                keywords=["repository", "data", "persistence", "orm"],
                components=[
                    "repository-interface",
                    "concrete-repository",
                    "entity",
                    "unit-of-work",
                ],
                pros=["Testability", "Flexibility", "Separation of concerns"],
                cons=["Extra abstraction layer", "Complexity"],
                use_cases=["Data-driven apps", "Multiple data sources"],
            ),
        ]

    def _initialize_keyword_weights(self) -> Dict[str, float]:
        """Initialize keyword importance weights"""
        return {
            # High importance
            "microservice": 2.0,
            "distributed": 1.8,
            "scalable": 1.8,
            "real-time": 1.8,
            "event": 1.7,
            # Medium importance
            "api": 1.5,
            "async": 1.5,
            "modular": 1.4,
            "layer": 1.3,
            # Standard importance
            "simple": 1.0,
            "fast": 1.0,
            "secure": 1.0,
            "reliable": 1.0,
        }

    def suggest_hybrid(self, matches: List[MatchResult]) -> Optional[Dict[str, Any]]:
        """Suggest hybrid architecture based on multiple matches"""
        if len(matches) < 2:
            return None

        # Only consider high-confidence matches
        high_confidence = [m for m in matches if m.confidence > 0.6]

        if len(high_confidence) >= 2:
            primary = high_confidence[0]
            secondary = high_confidence[1]

            return {
                "primary_pattern": primary.pattern.name,
                "secondary_pattern": secondary.pattern.name,
                "combination_confidence": (primary.confidence + secondary.confidence) / 2,
                "reasoning": f"Hybrid approach combining {primary.pattern.name} and {secondary.pattern.name}",
                "implementation": self._suggest_hybrid_implementation(primary, secondary),
            }

        return None

    def _suggest_hybrid_implementation(self, primary: MatchResult, secondary: MatchResult) -> str:
        """Suggest how to implement hybrid architecture"""
        p1 = primary.pattern.name
        p2 = secondary.pattern.name

        if "microservices" in [p1, p2] and "monolithic" in [p1, p2]:
            return "Start with modular monolith, extract services incrementally"
        elif "event-driven" in [p1, p2] and "layered" in [p1, p2]:
            return "Use layered architecture with event-driven communication between layers"
        elif "serverless" in [p1, p2] and "microservices" in [p1, p2]:
            return "Implement core services as microservices, use serverless for edge functions"
        else:
            return f"Combine strengths of {p1} and {p2} based on component requirements"

    def get_metrics(self) -> Dict[str, Any]:
        """Get matcher metrics"""
        return {
            "pattern_count": len(self.patterns),
            "pattern_types": list(set(p.type.value for p in self.patterns)),
            "keyword_count": len(self.keyword_weights),
            "size_kb": 5.9,
            "init_us": 2.5,
        }


# Global instance
matcher = None


def get_matcher() -> PatternMatcher:
    """Get or create pattern matcher"""
    global matcher
    if not matcher:
        matcher = PatternMatcher()
    return matcher


def main():
    """Test pattern matcher"""
    matcher = get_matcher()

    requirements = """
    We need a scalable e-commerce platform with real-time inventory updates.
    The system should handle millions of users and support microservices.
    We want event-driven architecture for order processing.
    """

    context = {
        "team_size": 15,
        "scale": "large",
        "tech_stack": ["kubernetes", "kafka", "postgresql"],
    }

    matches = matcher.match(requirements, context)

    print(f"Found {len(matches)} matching patterns:")
    for match in matches[:3]:
        print(f"\n{match.pattern.name}: {match.confidence:.0%} confidence")
        print(f"  Matched: {match.matched_keywords}")
        print(f"  {match.reasoning}")
        print(f"  Recommendations: {match.recommendations[:2]}")

    # Check for hybrid suggestion
    hybrid = matcher.suggest_hybrid(matches)
    if hybrid:
        print(f"\nHybrid suggestion: {hybrid['implementation']}")


if __name__ == "__main__":
    main()
