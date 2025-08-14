"""
Test suite for Requirement Analyzer
Day 21: Phase 2 - Meta Agents
"""

import asyncio
from typing import List

import pytest

from src.agents.meta.requirement_analyzer import (
    AnalysisResult,
    Requirement,
    RequirementAnalyzer,
    RequirementType,
    get_analyzer,
)
from src.ai.consensus_engine import ConsensusEngine, get_engine
from src.ai.pattern_matcher import PatternMatcher, get_matcher


class TestRequirementAnalyzer:
    """Test requirement analyzer functionality"""

    @pytest.fixture
    def analyzer(self):
        """Get analyzer instance"""
        return get_analyzer()

    @pytest.mark.asyncio
    async def test_explicit_extraction(self, analyzer):
        """Test explicit requirement extraction"""
        input_text = """
        The system must have user authentication.
        It should support real-time notifications.
        We need a REST API for mobile apps.
        The application must handle 1000 concurrent users.
        """

        result = await analyzer.analyze(input_text)

        assert len(result.requirements) > 0

        # Check for functional requirements
        functional = [r for r in result.requirements if r.type == RequirementType.FUNCTIONAL]
        assert len(functional) > 0

        # Check for technical requirements
        technical = [r for r in result.requirements if r.type == RequirementType.TECHNICAL]
        assert len(technical) > 0

        # Verify requirement properties
        for req in result.requirements:
            assert req.id
            assert req.description
            assert 1 <= req.priority <= 5
            assert 0 <= req.confidence <= 1
            assert req.source in ["user", "ai", "pattern"]

    @pytest.mark.asyncio
    async def test_implicit_inference(self, analyzer):
        """Test implicit requirement inference"""
        input_text = "Build a web application with user login"

        result = await analyzer.analyze(input_text)

        # Should infer security requirements
        implicit = [r for r in result.requirements if r.type == RequirementType.IMPLICIT]
        assert len(implicit) > 0

        # Check for common implicit requirements
        descriptions = [r.description.lower() for r in implicit]
        assert any("security" in d or "authentication" in d for d in descriptions)
        assert any("responsive" in d or "mobile" in d for d in descriptions)

    @pytest.mark.asyncio
    async def test_pattern_matching(self, analyzer):
        """Test architectural pattern matching"""
        input_text = """
        Create a microservices architecture with independent services.
        Each service should be independently deployable.
        Use event-driven communication between services.
        """

        result = await analyzer.analyze(input_text)

        assert len(result.patterns) > 0
        assert "microservices-architecture" in result.patterns
        assert "event-driven-architecture" in result.patterns

    @pytest.mark.asyncio
    async def test_complexity_calculation(self, analyzer):
        """Test complexity score calculation"""
        # Simple requirements
        simple_text = "Create a basic todo list app"
        simple_result = await analyzer.analyze(simple_text)

        # Complex requirements
        complex_text = """
        Build an enterprise e-commerce platform with microservices.
        Must handle millions of users with real-time inventory.
        Integrate with payment gateways, shipping providers, and ERP.
        Support multi-language, multi-currency, and global deployment.
        Implement AI-based recommendation engine and fraud detection.
        """
        complex_result = await analyzer.analyze(complex_text)

        assert simple_result.complexity_score < complex_result.complexity_score
        assert simple_result.complexity_score < 0.5
        assert complex_result.complexity_score > 0.5

    @pytest.mark.asyncio
    async def test_recommendations(self, analyzer):
        """Test recommendation generation"""
        input_text = """
        Build a real-time chat application with video calling.
        Support 10000 concurrent users with low latency.
        """

        result = await analyzer.analyze(input_text)

        assert len(result.recommendations) > 0

        # Should recommend WebSocket or similar for real-time
        recommendations_text = " ".join(result.recommendations).lower()
        assert any(
            tech in recommendations_text for tech in ["websocket", "real-time", "message", "queue"]
        )

    @pytest.mark.asyncio
    async def test_priority_calculation(self, analyzer):
        """Test requirement priority calculation"""
        input_text = """
        The system must have authentication (critical).
        It should have a nice UI.
        Could have dark mode support.
        User data encryption is essential.
        """

        result = await analyzer.analyze(input_text)

        # Find requirements by keywords
        critical = [
            r
            for r in result.requirements
            if "critical" in r.description.lower() or "essential" in r.description.lower()
        ]
        nice_to_have = [
            r
            for r in result.requirements
            if "could" in r.description.lower() or "nice" in r.description.lower()
        ]

        if critical and nice_to_have:
            assert critical[0].priority > nice_to_have[0].priority

    def test_metrics(self, analyzer):
        """Test analyzer metrics"""
        metrics = analyzer.get_metrics()

        assert "models" in metrics
        assert len(metrics["models"]) >= 3
        assert metrics["confidence_threshold"] > 0
        assert metrics["pattern_count"] > 0
        assert metrics["size_kb"] < 6.5
        assert metrics["init_us"] < 3.0


class TestConsensusEngine:
    """Test consensus engine functionality"""

    @pytest.fixture
    def engine(self):
        """Get consensus engine instance"""
        return get_engine()

    @pytest.mark.asyncio
    async def test_multi_model_consensus(self, engine):
        """Test consensus from multiple models"""
        result = await engine.get_consensus(
            prompt="Should we use REST or GraphQL for the API?",
            context={"api_complexity": "high", "client_diversity": "multiple"},
        )

        assert result.final_result is not None
        assert 0 <= result.agreement_score <= 1
        assert 0 <= result.confidence <= 1
        assert len(result.model_responses) >= 2
        assert result.reasoning

    @pytest.mark.asyncio
    async def test_weighted_voting(self, engine):
        """Test weighted voting mechanism"""
        result = await engine.get_consensus(
            prompt="Choose architecture pattern", context={"scale": "large"}
        )

        # Verify voting was applied
        assert result.metadata["consensus_method"] == "weighted_voting"
        assert result.final_result is not None

        # Check model weights were considered
        for response in result.model_responses:
            assert response.provider in engine.voting_weights

    @pytest.mark.asyncio
    async def test_consensus_validation(self, engine):
        """Test consensus validation"""
        result = await engine.get_consensus(prompt="Test prompt", context={})

        # Should pass with default criteria
        valid = await engine.validate_consensus(result, {"min_confidence": 0.5})
        assert valid

        # Should fail with high criteria
        invalid = await engine.validate_consensus(result, {"min_confidence": 0.99})
        assert not invalid

    def test_engine_metrics(self, engine):
        """Test engine metrics"""
        metrics = engine.get_metrics()

        assert "models" in metrics
        assert "voting_weights" in metrics
        assert "min_agreement" in metrics
        assert metrics["size_kb"] < 6.5
        assert metrics["init_us"] < 3.0


class TestPatternMatcher:
    """Test pattern matcher functionality"""

    @pytest.fixture
    def matcher(self):
        """Get pattern matcher instance"""
        return get_matcher()

    def test_pattern_matching(self, matcher):
        """Test basic pattern matching"""
        requirements = """
        Build a distributed system with independent microservices.
        Each service should be scalable and deployable independently.
        """

        matches = matcher.match(requirements)

        assert len(matches) > 0

        # Microservices should be top match
        top_match = matches[0]
        assert "microservice" in top_match.pattern.name
        assert top_match.confidence > 0.5
        assert len(top_match.matched_keywords) > 0

    def test_context_based_matching(self, matcher):
        """Test context-aware pattern matching"""
        requirements = "Build a scalable application"

        # Small team context
        small_team_matches = matcher.match(requirements, {"team_size": 2, "scale": "small"})

        # Large team context
        large_team_matches = matcher.match(requirements, {"team_size": 20, "scale": "enterprise"})

        # Different contexts should affect recommendations
        assert small_team_matches[0].pattern.name != large_team_matches[0].pattern.name

    def test_hybrid_suggestion(self, matcher):
        """Test hybrid architecture suggestion"""
        requirements = """
        Need both microservices flexibility and monolithic simplicity.
        Start simple but prepare for scale.
        """

        matches = matcher.match(requirements)
        hybrid = matcher.suggest_hybrid(matches)

        if hybrid:  # May not always suggest hybrid
            assert "primary_pattern" in hybrid
            assert "secondary_pattern" in hybrid
            assert "implementation" in hybrid
            assert hybrid["combination_confidence"] > 0

    def test_recommendations_generation(self, matcher):
        """Test pattern-specific recommendations"""
        requirements = "Build event-driven real-time system"

        matches = matcher.match(requirements)

        if matches:
            top_match = matches[0]
            assert len(top_match.recommendations) > 0

            # Should have event-related recommendations
            recs_text = " ".join(top_match.recommendations).lower()
            assert any(keyword in recs_text for keyword in ["event", "message", "broker", "async"])

    def test_matcher_metrics(self, matcher):
        """Test matcher metrics"""
        metrics = matcher.get_metrics()

        assert metrics["pattern_count"] > 0
        assert "pattern_types" in metrics
        assert metrics["keyword_count"] > 0
        assert metrics["size_kb"] < 6.5
        assert metrics["init_us"] < 3.0


@pytest.mark.integration
class TestIntegration:
    """Integration tests for Day 21 components"""

    @pytest.mark.asyncio
    async def test_full_requirement_analysis_flow(self):
        """Test complete requirement analysis flow"""
        analyzer = get_analyzer()
        engine = get_engine()
        matcher = get_matcher()

        # Complex input
        input_text = """
        Build an enterprise e-commerce platform.
        Must support millions of users globally.
        Need real-time inventory management.
        Integrate with multiple payment providers.
        Support mobile and web clients.
        Ensure PCI compliance and data security.
        """

        # Analyze requirements
        analysis = await analyzer.analyze(input_text)
        assert len(analysis.requirements) > 5
        assert len(analysis.patterns) > 0
        assert analysis.complexity_score > 0.5

        # Get pattern matches
        pattern_matches = matcher.match(input_text, {"scale": "enterprise"})
        assert len(pattern_matches) > 0

        # Get consensus on architecture
        consensus = await engine.get_consensus(
            prompt=f"Best architecture for: {input_text}",
            context={"requirements": len(analysis.requirements)},
        )
        assert consensus.confidence > 0.5

        print(f"\n=== Integration Test Results ===")
        print(f"Requirements found: {len(analysis.requirements)}")
        print(f"Patterns identified: {analysis.patterns}")
        print(f"Complexity score: {analysis.complexity_score:.2f}")
        print(f"Top pattern match: {pattern_matches[0].pattern.name}")
        print(f"Consensus confidence: {consensus.confidence:.0%}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
