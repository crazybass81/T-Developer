"""Tests for Specification Agent - Service requirement processing and spec generation.

Phase 5: P5-T1 - Specification Agent
Converts user requirements into technical specifications.
"""


import pytest

from packages.agents.spec_agent import (
    AcceptanceCriteria,
    AmbiguityDetector,
    ClarificationGenerator,
    DataModelGenerator,
    FunctionalRequirement,
    NonFunctionalRequirement,
    OpenAPIGenerator,
    RequirementParser,
    ServiceSpecification,
    SpecificationAgent,
    SpecValidator,
)


class TestRequirementParser:
    """Test NLP requirement parsing."""

    @pytest.fixture
    def parser(self):
        """Create requirement parser."""
        return RequirementParser()

    @pytest.mark.asyncio
    async def test_parse_user_story(self, parser):
        """Test parsing user stories."""
        user_story = """
        As a user, I want to create an account so that I can save my preferences.
        As an admin, I want to view all users so that I can manage the system.
        As a user, I want to reset my password so that I can regain access.
        """

        requirements = await parser.parse_user_stories(user_story)

        assert len(requirements) == 3
        assert requirements[0].actor == "user"
        assert requirements[0].action == "create an account"
        assert requirements[0].benefit == "save my preferences"

    @pytest.mark.asyncio
    async def test_extract_functional_requirements(self, parser):
        """Test extracting functional requirements."""
        description = """
        The system should allow users to:
        - Create, read, update, and delete posts
        - Comment on posts
        - Like and share posts
        - Follow other users
        - Search for content
        """

        functional_reqs = await parser.extract_functional_requirements(description)

        assert len(functional_reqs) >= 5
        assert any("CRUD" in req.type for req in functional_reqs)
        assert any("search" in req.description.lower() for req in functional_reqs)

    @pytest.mark.asyncio
    async def test_identify_nfr(self, parser):
        """Test identifying non-functional requirements."""
        description = """
        The system must:
        - Handle 10,000 concurrent users
        - Respond within 200ms for 95% of requests
        - Maintain 99.9% uptime
        - Encrypt all data at rest
        - Support horizontal scaling
        """

        nfrs = await parser.extract_non_functional_requirements(description)

        assert len(nfrs) >= 5
        assert any(nfr.category == "performance" for nfr in nfrs)
        assert any(nfr.category == "security" for nfr in nfrs)
        assert any(nfr.category == "availability" for nfr in nfrs)

    @pytest.mark.asyncio
    async def test_parse_api_requirements(self, parser):
        """Test parsing API requirements."""
        api_desc = """
        API endpoints needed:
        - GET /users - List all users
        - POST /users - Create a new user
        - GET /users/{id} - Get user by ID
        - PUT /users/{id} - Update user
        - DELETE /users/{id} - Delete user
        """

        api_reqs = await parser.parse_api_requirements(api_desc)

        assert len(api_reqs) == 5
        assert api_reqs[0].method == "GET"
        assert api_reqs[0].path == "/users"
        assert api_reqs[1].method == "POST"


class TestOpenAPIGenerator:
    """Test OpenAPI specification generation."""

    @pytest.fixture
    def generator(self):
        """Create OpenAPI generator."""
        return OpenAPIGenerator()

    @pytest.mark.asyncio
    async def test_generate_openapi_spec(self, generator):
        """Test generating OpenAPI specification."""
        requirements = [
            FunctionalRequirement(
                type="CRUD",
                entity="User",
                operations=["create", "read", "update", "delete"],
                description="User management",
            ),
            FunctionalRequirement(
                type="CRUD",
                entity="Post",
                operations=["create", "read", "update", "delete"],
                description="Post management",
            ),
        ]

        spec = await generator.generate_spec(
            title="Blog API", version="1.0.0", requirements=requirements
        )

        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Blog API"
        assert spec["info"]["version"] == "1.0.0"
        assert "/users" in spec["paths"]
        assert "/posts" in spec["paths"]

    @pytest.mark.asyncio
    async def test_generate_schemas(self, generator):
        """Test generating data schemas."""
        entities = [
            {"name": "User", "fields": ["id", "email", "name", "created_at"]},
            {"name": "Post", "fields": ["id", "title", "content", "author_id"]},
        ]

        schemas = await generator.generate_schemas(entities)

        assert "User" in schemas
        assert "Post" in schemas
        assert schemas["User"]["properties"]["email"]["type"] == "string"
        assert schemas["User"]["properties"]["email"]["format"] == "email"

    @pytest.mark.asyncio
    async def test_add_authentication(self, generator):
        """Test adding authentication to spec."""
        spec = {"openapi": "3.0.0", "paths": {"/users": {}}}

        spec_with_auth = await generator.add_authentication(spec, "bearer")

        assert "components" in spec_with_auth
        assert "securitySchemes" in spec_with_auth["components"]
        assert "bearerAuth" in spec_with_auth["components"]["securitySchemes"]


class TestDataModelGenerator:
    """Test data model and ERD generation."""

    @pytest.fixture
    def generator(self):
        """Create data model generator."""
        return DataModelGenerator()

    @pytest.mark.asyncio
    async def test_create_data_models(self, generator):
        """Test creating data models from requirements."""
        requirements = [
            FunctionalRequirement(
                type="CRUD",
                entity="User",
                operations=["create", "read", "update", "delete"],
                fields=["id", "email", "name", "password_hash"],
            ),
            FunctionalRequirement(
                type="CRUD",
                entity="Post",
                operations=["create", "read"],
                fields=["id", "title", "content", "user_id"],
            ),
        ]

        models = await generator.create_models(requirements)

        assert len(models) == 2
        assert models[0].name == "User"
        assert len(models[0].fields) == 4
        assert models[1].name == "Post"
        assert models[1].has_relation("User")

    @pytest.mark.asyncio
    async def test_define_relationships(self, generator):
        """Test defining relationships between entities."""
        entities = [
            {"name": "User", "fields": ["id", "email"]},
            {"name": "Post", "fields": ["id", "user_id"]},
            {"name": "Comment", "fields": ["id", "post_id", "user_id"]},
        ]

        relationships = await generator.define_relationships(entities)

        assert len(relationships) >= 2
        assert any(
            r.type == "one-to-many" and r.from_entity == "User" and r.to_entity == "Post"
            for r in relationships
        )
        assert any(
            r.type == "one-to-many" and r.from_entity == "Post" and r.to_entity == "Comment"
            for r in relationships
        )

    @pytest.mark.asyncio
    async def test_generate_erd(self, generator):
        """Test generating ERD diagram."""
        models = [
            {"name": "User", "fields": ["id", "email", "name"]},
            {"name": "Post", "fields": ["id", "title", "user_id"]},
        ]
        relationships = [{"from": "User", "to": "Post", "type": "one-to-many"}]

        erd = await generator.generate_erd(models, relationships)

        assert erd.format in ["mermaid", "plantuml", "graphviz"]
        assert "User" in erd.content
        assert "Post" in erd.content


class TestAcceptanceCriteria:
    """Test acceptance criteria generation."""

    @pytest.fixture
    def generator(self):
        """Create acceptance criteria generator."""
        return AcceptanceCriteria()

    @pytest.mark.asyncio
    async def test_define_acceptance_criteria(self, generator):
        """Test defining acceptance criteria for features."""
        user_story = {"actor": "user", "action": "create an account", "benefit": "save preferences"}

        criteria = await generator.generate_criteria(user_story)

        assert len(criteria) > 0
        assert all(c.is_testable for c in criteria)
        assert any("email" in c.description.lower() for c in criteria)
        assert any("password" in c.description.lower() for c in criteria)

    @pytest.mark.asyncio
    async def test_generate_test_scenarios(self, generator):
        """Test generating test scenarios from criteria."""
        criteria = [
            "User can register with valid email",
            "System rejects invalid email formats",
            "Password must be at least 8 characters",
        ]

        scenarios = await generator.generate_test_scenarios(criteria)

        assert len(scenarios) >= 3
        assert scenarios[0].type in ["positive", "negative"]
        assert all(s.has_steps for s in scenarios)


class TestSpecValidator:
    """Test specification validation."""

    @pytest.fixture
    def validator(self):
        """Create spec validator."""
        return SpecValidator()

    @pytest.mark.asyncio
    async def test_validate_completeness(self, validator):
        """Test validating specification completeness."""
        spec = ServiceSpecification(
            functional_requirements=[FunctionalRequirement(type="CRUD", entity="User")],
            non_functional_requirements=[
                NonFunctionalRequirement(category="performance", target="<200ms")
            ],
            openapi_spec={"openapi": "3.0.0", "paths": {}},
            data_models=[],
            acceptance_criteria=[],
        )

        validation_result = await validator.validate_completeness(spec)

        assert validation_result.is_complete is False
        assert len(validation_result.missing_elements) > 0
        assert "data_models" in validation_result.missing_elements

    @pytest.mark.asyncio
    async def test_detect_inconsistencies(self, validator):
        """Test detecting inconsistencies in spec."""
        spec = ServiceSpecification(
            functional_requirements=[FunctionalRequirement(type="CRUD", entity="User")],
            openapi_spec={"paths": {"/products": {}}},  # Inconsistent - no Product entity defined
        )

        inconsistencies = await validator.detect_inconsistencies(spec)

        assert len(inconsistencies) > 0
        assert any("Product" in i.description for i in inconsistencies)


class TestAmbiguityDetector:
    """Test ambiguity detection in requirements."""

    @pytest.fixture
    def detector(self):
        """Create ambiguity detector."""
        return AmbiguityDetector()

    @pytest.mark.asyncio
    async def test_detect_ambiguous_terms(self, detector):
        """Test detecting ambiguous terms in requirements."""
        requirement = """
        The system should be fast and handle many users.
        It should have good performance and be secure.
        """

        ambiguities = await detector.detect_ambiguities(requirement)

        assert len(ambiguities) > 0
        assert any(a.term == "fast" for a in ambiguities)
        assert any(a.term == "many" for a in ambiguities)
        assert any(a.term == "good" for a in ambiguities)

    @pytest.mark.asyncio
    async def test_score_clarity(self, detector):
        """Test scoring requirement clarity."""
        clear_req = "The API must respond within 200ms for 95% of requests"
        vague_req = "The system should be fast and reliable"

        clear_score = await detector.score_clarity(clear_req)
        vague_score = await detector.score_clarity(vague_req)

        assert clear_score > vague_score
        assert clear_score > 0.7
        assert vague_score < 0.5


class TestClarificationGenerator:
    """Test generating clarification questions."""

    @pytest.fixture
    def generator(self):
        """Create clarification generator."""
        return ClarificationGenerator()

    @pytest.mark.asyncio
    async def test_generate_clarifications(self, generator):
        """Test generating clarification questions for gaps."""
        gaps = [
            {"type": "missing_detail", "area": "authentication"},
            {"type": "ambiguous_term", "term": "fast", "context": "response time"},
            {"type": "missing_requirement", "area": "error handling"},
        ]

        questions = await generator.generate_questions(gaps)

        assert len(questions) == 3
        assert any("authentication" in q.question.lower() for q in questions)
        assert any(
            "fast" in q.question.lower() or "response" in q.question.lower() for q in questions
        )
        assert any("error" in q.question.lower() for q in questions)


class TestSpecificationAgent:
    """Test main specification agent orchestration."""

    @pytest.fixture
    def agent(self):
        """Create specification agent."""
        return SpecificationAgent()

    @pytest.mark.asyncio
    async def test_process_requirements(self, agent):
        """Test end-to-end requirement processing."""
        requirements_text = """
        Build a blog platform where:
        - Users can register and login
        - Users can create, edit, and delete posts
        - Users can comment on posts
        - System should handle 10,000 users
        - Response time should be under 500ms
        """

        spec = await agent.process_requirements(requirements_text)

        assert isinstance(spec, ServiceSpecification)
        assert len(spec.functional_requirements) > 0
        assert len(spec.non_functional_requirements) > 0
        assert spec.openapi_spec is not None
        assert len(spec.data_models) > 0
        assert len(spec.acceptance_criteria) > 0

    @pytest.mark.asyncio
    async def test_generate_complete_spec(self, agent):
        """Test generating complete service specification."""
        user_stories = [
            "As a user, I want to register an account",
            "As a user, I want to create posts",
            "As an admin, I want to moderate content",
        ]

        spec = await agent.generate_specification(
            service_name="BlogService",
            user_stories=user_stories,
            performance_requirements={"latency": "<200ms", "throughput": ">1000rps"},
        )

        assert spec.service_name == "BlogService"
        assert spec.is_valid()
        assert spec.openapi_spec["info"]["title"] == "BlogService"
        assert len(spec.clarification_questions) >= 0  # May have questions
