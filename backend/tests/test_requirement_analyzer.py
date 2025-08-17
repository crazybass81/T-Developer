"""Tests for Requirement Analyzer - TDD approach."""

from unittest.mock import patch

import pytest
from packages.meta_agents.requirement_analyzer import (
    AnalysisConfig,
    ConsensusEngine,
    PatternMatcher,
    Priority,
    Requirement,
    RequirementAnalyzer,
    RequirementType,
)


class TestRequirement:
    """Test requirement data model."""

    def test_requirement_creation(self):
        """Test creating a requirement."""
        req = Requirement(
            id="REQ-001",
            type=RequirementType.FUNCTIONAL,
            priority=Priority.HIGH,
            description="User should be able to login",
            acceptance_criteria=["Login form exists", "Authentication works"],
            dependencies=["REQ-002"],
            effort_hours=4.0,
        )

        assert req.id == "REQ-001"
        assert req.type == RequirementType.FUNCTIONAL
        assert req.priority == Priority.HIGH
        assert len(req.acceptance_criteria) == 2
        assert req.effort_hours == 4.0

    def test_requirement_validation(self):
        """Test requirement validation."""
        req = Requirement(
            id="REQ-001",
            type=RequirementType.FUNCTIONAL,
            priority=Priority.HIGH,
            description="User login",
            acceptance_criteria=[],
            dependencies=[],
            effort_hours=4.0,
        )

        # Should not have empty acceptance criteria
        assert req.validate() is False

        req.acceptance_criteria = ["Login works"]
        assert req.validate() is True

    def test_requirement_to_dict(self):
        """Test converting requirement to dictionary."""
        req = Requirement(
            id="REQ-001",
            type=RequirementType.FUNCTIONAL,
            priority=Priority.HIGH,
            description="User login",
            acceptance_criteria=["Login works"],
            dependencies=[],
            effort_hours=4.0,
        )

        req_dict = req.to_dict()
        assert req_dict["id"] == "REQ-001"
        assert req_dict["type"] == "FUNCTIONAL"
        assert req_dict["priority"] == "HIGH"


class TestConsensusEngine:
    """Test consensus engine for multi-model analysis."""

    @pytest.fixture
    def engine(self):
        """Create consensus engine."""
        return ConsensusEngine()

    @pytest.mark.asyncio
    async def test_analyze_with_multiple_models(self, engine):
        """Test analyzing requirements with multiple AI models."""
        text = "Build a REST API for user authentication with JWT tokens"

        # Mock AI responses
        with patch.object(engine, "_call_claude") as mock_claude:
            with patch.object(engine, "_call_gpt") as mock_gpt:
                mock_claude.return_value = {
                    "requirements": [
                        {
                            "type": "FUNCTIONAL",
                            "description": "JWT authentication",
                            "priority": "HIGH",
                        }
                    ]
                }
                mock_gpt.return_value = {
                    "requirements": [
                        {
                            "type": "FUNCTIONAL",
                            "description": "JWT token generation",
                            "priority": "HIGH",
                        }
                    ]
                }

                result = await engine.analyze(text)

                assert "consensus" in result
                assert "confidence" in result
                assert result["confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_consensus_calculation(self, engine):
        """Test consensus calculation between models."""
        responses = [
            {"requirements": [{"type": "FUNCTIONAL", "priority": "HIGH"}]},
            {"requirements": [{"type": "FUNCTIONAL", "priority": "HIGH"}]},
            {"requirements": [{"type": "FUNCTIONAL", "priority": "MEDIUM"}]},
        ]

        consensus = engine.calculate_consensus(responses)

        # Should find majority consensus on HIGH priority
        assert consensus["agreement_score"] > 0.6
        assert len(consensus["requirements"]) > 0

    @pytest.mark.asyncio
    async def test_conflict_resolution(self, engine):
        """Test resolving conflicts between models."""
        responses = [
            {"requirements": [{"type": "FUNCTIONAL", "priority": "HIGH"}]},
            {"requirements": [{"type": "NON_FUNCTIONAL", "priority": "LOW"}]},
        ]

        consensus = engine.calculate_consensus(responses)

        # Should handle conflicts gracefully
        assert "conflicts" in consensus
        assert consensus["agreement_score"] <= 0.5  # Low agreement when models disagree


class TestPatternMatcher:
    """Test pattern matching for requirement detection."""

    @pytest.fixture
    def matcher(self):
        """Create pattern matcher."""
        return PatternMatcher()

    def test_detect_functional_requirements(self, matcher):
        """Test detecting functional requirements."""
        text = """
        The system should allow users to:
        - Create new accounts
        - Login with email/password
        - Reset forgotten passwords
        - Update profile information
        """

        patterns = matcher.detect_patterns(text)

        assert patterns["type"] == RequirementType.FUNCTIONAL
        assert len(patterns["features"]) >= 4
        assert "authentication" in patterns["keywords"]

    def test_detect_nonfunctional_requirements(self, matcher):
        """Test detecting non-functional requirements."""
        text = """
        Performance requirements:
        - Response time < 200ms
        - Support 1000 concurrent users
        - 99.9% uptime
        - Data encryption at rest
        """

        patterns = matcher.detect_patterns(text)

        assert patterns["type"] == RequirementType.NON_FUNCTIONAL
        assert "performance" in patterns["categories"]
        assert "security" in patterns["categories"]

    def test_detect_constraints(self, matcher):
        """Test detecting project constraints."""
        text = """
        Project constraints:
        - Must be completed by Q2 2025
        - Budget limited to $50,000
        - Use existing AWS infrastructure
        - Compatible with Python 3.9+
        """

        patterns = matcher.detect_patterns(text)

        assert patterns["type"] == RequirementType.CONSTRAINT
        assert "timeline" in patterns["constraints"]
        assert "budget" in patterns["constraints"]
        assert "technology" in patterns["constraints"]

    def test_extract_acceptance_criteria(self, matcher):
        """Test extracting acceptance criteria."""
        text = """
        User Story: As a user, I want to login

        Acceptance Criteria:
        - Login form displays email and password fields
        - Validation shows errors for invalid input
        - Successful login redirects to dashboard
        - Failed login shows error message
        """

        criteria = matcher.extract_acceptance_criteria(text)

        assert len(criteria) == 4
        assert any("login form" in c.lower() for c in criteria)
        assert any("validation" in c.lower() for c in criteria)


class TestAnalysisConfig:
    """Test analysis configuration."""

    def test_default_config(self):
        """Test default configuration."""
        config = AnalysisConfig()

        assert config.use_ai is True
        assert config.use_consensus is True
        assert config.min_confidence == 0.7
        assert config.max_requirements == 100
        assert config.auto_prioritize is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = AnalysisConfig(
            use_ai=False, use_consensus=False, min_confidence=0.9, max_requirements=50
        )

        assert config.use_ai is False
        assert config.min_confidence == 0.9
        assert config.max_requirements == 50


class TestRequirementAnalyzer:
    """Test requirement analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create requirement analyzer."""
        config = AnalysisConfig(use_ai=False)
        return RequirementAnalyzer(config)

    @pytest.mark.asyncio
    async def test_analyze_text_requirements(self, analyzer):
        """Test analyzing text-based requirements."""
        text = """
        Build an e-commerce platform with the following features:
        1. User registration and authentication
        2. Product catalog with search
        3. Shopping cart functionality
        4. Payment processing
        5. Order tracking

        Non-functional requirements:
        - Support 10,000 concurrent users
        - Page load time < 2 seconds
        - 99.9% availability
        """

        result = await analyzer.analyze_requirements(text)

        assert "requirements" in result
        assert len(result["requirements"]) > 0
        assert "functional" in result
        assert "non_functional" in result
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_analyze_user_stories(self, analyzer):
        """Test analyzing user stories."""
        stories = [
            {
                "title": "User Login",
                "description": "As a user, I want to login so I can access my account",
                "acceptance_criteria": [
                    "Login with email/password",
                    "Remember me option",
                    "Forgot password link",
                ],
            },
            {
                "title": "Product Search",
                "description": "As a customer, I want to search products",
                "acceptance_criteria": ["Search by name", "Filter by category", "Sort by price"],
            },
        ]

        result = await analyzer.analyze_user_stories(stories)

        assert len(result["requirements"]) == 2
        assert all(r.type == RequirementType.FUNCTIONAL for r in result["requirements"])
        assert result["total_effort"] > 0

    @pytest.mark.asyncio
    async def test_prioritize_requirements(self, analyzer):
        """Test requirement prioritization."""
        requirements = [
            Requirement(
                id="REQ-001",
                type=RequirementType.FUNCTIONAL,
                priority=Priority.LOW,
                description="Nice to have feature",
                acceptance_criteria=["Works"],
                dependencies=[],
                effort_hours=2.0,
            ),
            Requirement(
                id="REQ-002",
                type=RequirementType.FUNCTIONAL,
                priority=Priority.CRITICAL,
                description="Core functionality",
                acceptance_criteria=["Must work"],
                dependencies=[],
                effort_hours=4.0,
            ),
            Requirement(
                id="REQ-003",
                type=RequirementType.NON_FUNCTIONAL,
                priority=Priority.HIGH,
                description="Security requirement",
                acceptance_criteria=["Secure"],
                dependencies=["REQ-002"],
                effort_hours=3.0,
            ),
        ]

        prioritized = analyzer.prioritize_requirements(requirements)

        # Critical should come first
        assert prioritized[0].id == "REQ-002"
        # Then high priority
        assert prioritized[1].id == "REQ-003"
        # Low priority last
        assert prioritized[2].id == "REQ-001"

    @pytest.mark.asyncio
    async def test_estimate_effort(self, analyzer):
        """Test effort estimation."""
        requirement = Requirement(
            id="REQ-001",
            type=RequirementType.FUNCTIONAL,
            priority=Priority.HIGH,
            description="Implement user authentication with OAuth2",
            acceptance_criteria=[
                "Support Google OAuth",
                "Support GitHub OAuth",
                "Store user profiles",
                "Generate JWT tokens",
            ],
            dependencies=[],
            effort_hours=0,  # Not estimated yet
        )

        estimated = await analyzer.estimate_effort(requirement)

        assert estimated.effort_hours > 0
        assert estimated.effort_hours <= 4.0  # Should follow 4-hour rule
        assert "breakdown" in estimated.metadata

    @pytest.mark.asyncio
    async def test_generate_requirements_document(self, analyzer):
        """Test generating requirements document."""
        requirements = [
            Requirement(
                id="REQ-001",
                type=RequirementType.FUNCTIONAL,
                priority=Priority.HIGH,
                description="User authentication",
                acceptance_criteria=["Login works"],
                dependencies=[],
                effort_hours=4.0,
            )
        ]

        document = await analyzer.generate_document(requirements)

        assert "# Requirements Document" in document
        assert "## Functional Requirements" in document
        assert "REQ-001" in document
        assert "Total Effort" in document
