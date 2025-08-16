"""Specification Agent - Converts requirements into technical specifications.

Phase 5: P5-T1 - Specification Agent
Processes user requirements and generates complete service specifications.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent


class RequirementType(Enum):
    """Types of requirements."""

    CRUD = "crud"
    SEARCH = "search"
    AUTH = "authentication"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    REPORTING = "reporting"


class NFRCategory(Enum):
    """Non-functional requirement categories."""

    PERFORMANCE = "performance"
    SECURITY = "security"
    AVAILABILITY = "availability"
    SCALABILITY = "scalability"
    USABILITY = "usability"
    MAINTAINABILITY = "maintainability"


@dataclass
class UserStory:
    """User story representation."""

    actor: str
    action: str
    benefit: str
    acceptance_criteria: list[str] = field(default_factory=list)


@dataclass
class FunctionalRequirement:
    """Functional requirement specification."""

    type: str
    entity: Optional[str] = None
    operations: list[str] = field(default_factory=list)
    description: str = ""
    fields: list[str] = field(default_factory=list)

    def has_crud(self) -> bool:
        """Check if requirement includes CRUD operations."""
        crud_ops = {"create", "read", "update", "delete"}
        return bool(crud_ops.intersection(set(self.operations)))


@dataclass
class NonFunctionalRequirement:
    """Non-functional requirement specification."""

    category: str
    target: str
    description: str = ""
    metric: Optional[str] = None
    threshold: Optional[float] = None


@dataclass
class APIEndpoint:
    """API endpoint specification."""

    method: str
    path: str
    description: str = ""
    request_body: Optional[dict] = None
    response: Optional[dict] = None
    parameters: list[dict] = field(default_factory=list)


@dataclass
class DataModel:
    """Data model specification."""

    name: str
    fields: list[dict[str, Any]]
    relationships: list[dict] = field(default_factory=list)

    def has_relation(self, entity: str) -> bool:
        """Check if model has relationship with entity."""
        return any(r.get("to") == entity or r.get("from") == entity for r in self.relationships)


@dataclass
class Relationship:
    """Entity relationship specification."""

    type: str  # one-to-one, one-to-many, many-to-many
    from_entity: str
    to_entity: str
    foreign_key: Optional[str] = None


@dataclass
class TestScenario:
    """Test scenario specification."""

    type: str  # positive, negative, edge
    description: str
    steps: list[str] = field(default_factory=list)
    expected_result: str = ""

    @property
    def has_steps(self) -> bool:
        """Check if scenario has steps defined."""
        return len(self.steps) > 0


@dataclass
class AcceptanceCriterion:
    """Acceptance criterion specification."""

    description: str
    is_testable: bool = True
    test_scenarios: list[TestScenario] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Specification validation result."""

    is_complete: bool
    is_valid: bool = True
    missing_elements: list[str] = field(default_factory=list)
    inconsistencies: list[str] = field(default_factory=list)


@dataclass
class Ambiguity:
    """Detected ambiguity in requirements."""

    term: str
    context: str
    suggestion: str = ""


@dataclass
class ClarificationQuestion:
    """Clarification question for requirements."""

    question: str
    area: str
    priority: str = "medium"  # high, medium, low


@dataclass
class ERDDiagram:
    """Entity Relationship Diagram."""

    format: str  # mermaid, plantuml, graphviz
    content: str


@dataclass
class ServiceSpecification:
    """Complete service specification."""

    service_name: str = ""
    functional_requirements: list[FunctionalRequirement] = field(default_factory=list)
    non_functional_requirements: list[NonFunctionalRequirement] = field(default_factory=list)
    openapi_spec: Optional[dict] = None
    data_models: list[DataModel] = field(default_factory=list)
    acceptance_criteria: list[AcceptanceCriterion] = field(default_factory=list)
    clarification_questions: list[ClarificationQuestion] = field(default_factory=list)

    def is_valid(self) -> bool:
        """Check if specification is valid."""
        return (
            bool(self.functional_requirements)
            and bool(self.openapi_spec)
            and bool(self.data_models)
        )


class RequirementParser:
    """Parse and extract requirements from text."""

    def __init__(self):
        """Initialize requirement parser."""
        self.user_story_pattern = re.compile(
            r"As (?:a|an) (\w+),?\s*I want to ([^,]+)(?:,?\s*so that (.+))?"
        )

    async def parse_user_stories(self, text: str) -> list[UserStory]:
        """Parse user stories from text."""
        stories = []

        for match in self.user_story_pattern.finditer(text):
            story = UserStory(
                actor=match.group(1),
                action=match.group(2).strip(),
                benefit=match.group(3).strip() if match.group(3) else "",
            )
            stories.append(story)

        return stories

    async def extract_functional_requirements(self, text: str) -> list[FunctionalRequirement]:
        """Extract functional requirements from description."""
        requirements = []

        # Look for CRUD operations
        if any(word in text.lower() for word in ["create", "read", "update", "delete", "crud"]):
            # Extract entities
            entities = self._extract_entities(text)
            for entity in entities:
                req = FunctionalRequirement(
                    type="CRUD",
                    entity=entity,
                    operations=["create", "read", "update", "delete"],
                    description=f"CRUD operations for {entity}",
                )
                requirements.append(req)

        # Look for search functionality
        if "search" in text.lower():
            req = FunctionalRequirement(
                type="search", operations=["search"], description="Search functionality"
            )
            requirements.append(req)

        # Look for authentication
        if any(word in text.lower() for word in ["login", "register", "authenticate"]):
            req = FunctionalRequirement(
                type="authentication",
                operations=["register", "login", "logout"],
                description="User authentication",
            )
            requirements.append(req)

        return requirements

    async def extract_non_functional_requirements(
        self, text: str
    ) -> list[NonFunctionalRequirement]:
        """Extract non-functional requirements from description."""
        nfrs = []

        # Performance requirements
        if any(
            word in text.lower() for word in ["performance", "latency", "response", "concurrent"]
        ):
            # Extract numbers for metrics
            numbers = re.findall(r"\d+(?:\.\d+)?(?:\s*(?:ms|s|users|rps))?", text)
            for num in numbers:
                if "ms" in num or "response" in text.lower():
                    nfr = NonFunctionalRequirement(
                        category="performance", target=num, description="Response time requirement"
                    )
                    nfrs.append(nfr)
                elif "users" in num:
                    nfr = NonFunctionalRequirement(
                        category="performance",
                        target=num,
                        description="Concurrent users requirement",
                    )
                    nfrs.append(nfr)

        # Security requirements
        if any(
            word in text.lower() for word in ["security", "encrypt", "secure", "authentication"]
        ):
            nfr = NonFunctionalRequirement(
                category="security", target="encrypted", description="Security requirement"
            )
            nfrs.append(nfr)

        # Availability requirements
        if any(word in text.lower() for word in ["uptime", "availability", "99.9%"]):
            nfr = NonFunctionalRequirement(
                category="availability", target="99.9%", description="Availability requirement"
            )
            nfrs.append(nfr)

        # Scalability requirements
        if any(word in text.lower() for word in ["scale", "scaling", "horizontal", "vertical"]):
            nfr = NonFunctionalRequirement(
                category="scalability", target="horizontal", description="Scalability requirement"
            )
            nfrs.append(nfr)

        return nfrs

    async def parse_api_requirements(self, text: str) -> list[APIEndpoint]:
        """Parse API endpoint requirements."""
        endpoints = []

        # Pattern for API endpoints
        api_pattern = re.compile(r"(GET|POST|PUT|DELETE|PATCH)\s+([/\w{}]+)(?:\s*-\s*(.+))?")

        for match in api_pattern.finditer(text):
            endpoint = APIEndpoint(
                method=match.group(1),
                path=match.group(2),
                description=match.group(3).strip() if match.group(3) else "",
            )
            endpoints.append(endpoint)

        return endpoints

    def _extract_entities(self, text: str) -> list[str]:
        """Extract entity names from text."""
        entities = []

        # Common entity patterns
        entity_words = [
            "user",
            "post",
            "comment",
            "product",
            "order",
            "customer",
            "article",
            "category",
            "tag",
            "role",
            "permission",
        ]

        for word in entity_words:
            if word in text.lower():
                entities.append(word.capitalize())

        return entities


class OpenAPIGenerator:
    """Generate OpenAPI specifications."""

    async def generate_spec(
        self, title: str, version: str, requirements: list[FunctionalRequirement]
    ) -> dict:
        """Generate OpenAPI specification from requirements."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": title,
                "version": version,
                "description": f"API specification for {title}",
            },
            "paths": {},
            "components": {"schemas": {}},
        }

        # Generate paths for each requirement
        for req in requirements:
            if req.type == "CRUD" and req.entity:
                paths = self._generate_crud_paths(req.entity)
                spec["paths"].update(paths)

        return spec

    def _generate_crud_paths(self, entity: str) -> dict:
        """Generate CRUD paths for an entity."""
        entity_lower = entity.lower()
        entity_plural = entity_lower + "s"

        return {
            f"/{entity_plural}": {
                "get": {
                    "summary": f"List all {entity_plural}",
                    "responses": {"200": {"description": f"List of {entity_plural}"}},
                },
                "post": {
                    "summary": f"Create a new {entity_lower}",
                    "responses": {"201": {"description": f"{entity} created"}},
                },
            },
            f"/{entity_plural}/{{id}}": {
                "get": {
                    "summary": f"Get {entity_lower} by ID",
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": f"{entity} details"}},
                },
                "put": {
                    "summary": f"Update {entity_lower}",
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": f"{entity} updated"}},
                },
                "delete": {
                    "summary": f"Delete {entity_lower}",
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"204": {"description": f"{entity} deleted"}},
                },
            },
        }

    async def generate_schemas(self, entities: list[dict]) -> dict:
        """Generate data schemas for entities."""
        schemas = {}

        for entity in entities:
            schema = {"type": "object", "properties": {}}

            for field in entity.get("fields", []):
                # Infer field type
                if field == "id":
                    schema["properties"][field] = {"type": "string", "format": "uuid"}
                elif "email" in field:
                    schema["properties"][field] = {"type": "string", "format": "email"}
                elif "date" in field or "created" in field or "updated" in field:
                    schema["properties"][field] = {"type": "string", "format": "date-time"}
                elif field.endswith("_id"):
                    schema["properties"][field] = {"type": "string", "format": "uuid"}
                else:
                    schema["properties"][field] = {"type": "string"}

            schemas[entity["name"]] = schema

        return schemas

    async def add_authentication(self, spec: dict, auth_type: str) -> dict:
        """Add authentication to OpenAPI spec."""
        if "components" not in spec:
            spec["components"] = {}

        if "securitySchemes" not in spec["components"]:
            spec["components"]["securitySchemes"] = {}

        if auth_type == "bearer":
            spec["components"]["securitySchemes"]["bearerAuth"] = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }

        return spec


class DataModelGenerator:
    """Generate data models and relationships."""

    async def create_models(self, requirements: list[FunctionalRequirement]) -> list[DataModel]:
        """Create data models from requirements."""
        models = []

        for req in requirements:
            if req.entity:
                fields = []

                # Default fields
                fields.append({"name": "id", "type": "uuid", "primary": True})

                # Add fields from requirement
                for field_name in req.fields:
                    field_type = self._infer_field_type(field_name)
                    fields.append({"name": field_name, "type": field_type})

                # Add timestamps
                if req.type == "CRUD":
                    fields.append({"name": "created_at", "type": "datetime"})
                    fields.append({"name": "updated_at", "type": "datetime"})

                model = DataModel(name=req.entity, fields=fields)

                # Add relationships based on field names
                for field in fields:
                    if field["name"].endswith("_id"):
                        related_entity = field["name"][:-3].capitalize()
                        model.relationships.append({"type": "many-to-one", "to": related_entity})

                models.append(model)

        return models

    async def define_relationships(self, entities: list[dict]) -> list[Relationship]:
        """Define relationships between entities."""
        relationships = []

        for entity in entities:
            for field in entity.get("fields", []):
                if field.endswith("_id"):
                    # Foreign key relationship
                    related_entity = field[:-3].capitalize()
                    rel = Relationship(
                        type="one-to-many",
                        from_entity=related_entity,
                        to_entity=entity["name"],
                        foreign_key=field,
                    )
                    relationships.append(rel)

        return relationships

    async def generate_erd(self, models: list[dict], relationships: list[dict]) -> ERDDiagram:
        """Generate ERD diagram."""
        # Generate Mermaid format
        content = ["erDiagram"]

        # Add entities
        for model in models:
            content.append(f"    {model['name']} {{")
            for field in model.get("fields", []):
                content.append(f"        {field} string")
            content.append("    }")

        # Add relationships
        for rel in relationships:
            rel_type = "||--o{" if rel.get("type") == "one-to-many" else "||--||"
            content.append(f"    {rel['from']} {rel_type} {rel['to']} : has")

        return ERDDiagram(format="mermaid", content="\n".join(content))

    def _infer_field_type(self, field_name: str) -> str:
        """Infer field type from name."""
        if "email" in field_name:
            return "email"
        elif "password" in field_name:
            return "password"
        elif field_name.endswith("_id"):
            return "uuid"
        elif "date" in field_name or "time" in field_name:
            return "datetime"
        elif "price" in field_name or "amount" in field_name:
            return "decimal"
        elif "count" in field_name or "quantity" in field_name:
            return "integer"
        else:
            return "string"


class AcceptanceCriteria:
    """Generate acceptance criteria for features."""

    async def generate_criteria(self, user_story: dict) -> list[AcceptanceCriterion]:
        """Generate acceptance criteria from user story."""
        criteria = []

        action = user_story.get("action", "")

        if "create" in action or "register" in action:
            criteria.extend(
                [
                    AcceptanceCriterion(
                        description="User can successfully create with valid data", is_testable=True
                    ),
                    AcceptanceCriterion(
                        description="System validates required fields", is_testable=True
                    ),
                    AcceptanceCriterion(
                        description="System rejects duplicate entries", is_testable=True
                    ),
                ]
            )

            if "email" in action.lower() or "account" in action.lower():
                criteria.append(
                    AcceptanceCriterion(
                        description="System validates email format", is_testable=True
                    )
                )
                criteria.append(
                    AcceptanceCriterion(
                        description="Password meets security requirements", is_testable=True
                    )
                )

        return criteria

    async def generate_test_scenarios(self, criteria: list[str]) -> list[TestScenario]:
        """Generate test scenarios from acceptance criteria."""
        scenarios = []

        for criterion in criteria:
            if "valid" in criterion.lower():
                scenario = TestScenario(
                    type="positive",
                    description=f"Test: {criterion}",
                    steps=[
                        "Prepare valid test data",
                        "Execute operation",
                        "Verify success response",
                    ],
                    expected_result="Operation succeeds",
                )
                scenarios.append(scenario)

            if "reject" in criterion.lower() or "invalid" in criterion.lower():
                scenario = TestScenario(
                    type="negative",
                    description=f"Test: {criterion}",
                    steps=[
                        "Prepare invalid test data",
                        "Execute operation",
                        "Verify error response",
                    ],
                    expected_result="Operation fails with appropriate error",
                )
                scenarios.append(scenario)

        return scenarios


class SpecValidator:
    """Validate service specifications."""

    async def validate_completeness(self, spec: ServiceSpecification) -> ValidationResult:
        """Validate specification completeness."""
        missing = []

        if not spec.functional_requirements:
            missing.append("functional_requirements")
        if not spec.non_functional_requirements:
            missing.append("non_functional_requirements")
        if not spec.openapi_spec:
            missing.append("openapi_spec")
        if not spec.data_models:
            missing.append("data_models")
        if not spec.acceptance_criteria:
            missing.append("acceptance_criteria")

        return ValidationResult(is_complete=len(missing) == 0, missing_elements=missing)

    async def detect_inconsistencies(self, spec: ServiceSpecification) -> list[dict]:
        """Detect inconsistencies in specification."""
        inconsistencies = []

        # Check if all entities in API spec have data models
        if spec.openapi_spec and spec.functional_requirements:
            api_paths = spec.openapi_spec.get("paths", {})
            entities_in_api = set()

            for path in api_paths.keys():
                # Extract entity name from path
                parts = path.strip("/").split("/")
                if parts:
                    entity = parts[0].rstrip("s").capitalize()
                    entities_in_api.add(entity)

            entities_in_reqs = {req.entity for req in spec.functional_requirements if req.entity}

            # Find entities in API but not in requirements
            missing_in_reqs = entities_in_api - entities_in_reqs
            for entity in missing_in_reqs:
                inconsistencies.append(
                    {
                        "type": "missing_requirement",
                        "description": f"{entity} in API spec but not in requirements",
                    }
                )

        return inconsistencies


class AmbiguityDetector:
    """Detect ambiguities in requirements."""

    def __init__(self):
        """Initialize ambiguity detector."""
        self.ambiguous_terms = {
            "fast",
            "slow",
            "many",
            "few",
            "good",
            "bad",
            "high",
            "low",
            "soon",
            "later",
            "some",
            "several",
            "appropriate",
            "adequate",
            "sufficient",
            "reasonable",
        }

    async def detect_ambiguities(self, text: str) -> list[Ambiguity]:
        """Detect ambiguous terms in requirements."""
        ambiguities = []

        words = text.lower().split()
        for word in words:
            if word in self.ambiguous_terms:
                ambiguity = Ambiguity(
                    term=word, context=text[:50], suggestion=f"Specify exact value for '{word}'"
                )
                ambiguities.append(ambiguity)

        return ambiguities

    async def score_clarity(self, text: str) -> float:
        """Score requirement clarity (0-1)."""
        # Start with perfect score
        score = 1.0

        # Deduct for ambiguous terms
        ambiguities = await self.detect_ambiguities(text)
        score -= len(ambiguities) * 0.1

        # Boost for specific metrics
        if any(char.isdigit() for char in text):
            score += 0.1

        # Boost for specific units
        if any(unit in text.lower() for unit in ["ms", "seconds", "%", "users", "mb", "gb"]):
            score += 0.1

        return max(0, min(1, score))


class ClarificationGenerator:
    """Generate clarification questions for requirements."""

    async def generate_questions(self, gaps: list[dict]) -> list[ClarificationQuestion]:
        """Generate clarification questions for identified gaps."""
        questions = []

        for gap in gaps:
            gap_type = gap.get("type", "")

            if gap_type == "missing_detail":
                area = gap.get("area", "")
                question = ClarificationQuestion(
                    question=f"What are the specific requirements for {area}?",
                    area=area,
                    priority="high",
                )
                questions.append(question)

            elif gap_type == "ambiguous_term":
                term = gap.get("term", "")
                context = gap.get("context", "")
                question = ClarificationQuestion(
                    question=f"What specific value should be used for '{term}' in the context of {context}?",
                    area="clarity",
                    priority="medium",
                )
                questions.append(question)

            elif gap_type == "missing_requirement":
                area = gap.get("area", "")
                question = ClarificationQuestion(
                    question=f"Are there any requirements for {area}?", area=area, priority="medium"
                )
                questions.append(question)

        return questions


class SpecificationAgent(BaseAgent):
    """Main specification agent for requirement processing."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize specification agent."""
        super().__init__("SpecificationAgent", config)
        self.parser = RequirementParser()
        self.openapi_gen = OpenAPIGenerator()
        self.model_gen = DataModelGenerator()
        self.criteria_gen = AcceptanceCriteria()
        self.validator = SpecValidator()
        self.ambiguity_detector = AmbiguityDetector()
        self.clarification_gen = ClarificationGenerator()

    async def process_requirements(self, requirements_text: str) -> ServiceSpecification:
        """Process requirements text into complete specification."""
        spec = ServiceSpecification()

        # Parse requirements
        spec.functional_requirements = await self.parser.extract_functional_requirements(
            requirements_text
        )
        spec.non_functional_requirements = await self.parser.extract_non_functional_requirements(
            requirements_text
        )

        # Generate OpenAPI spec
        if spec.functional_requirements:
            spec.openapi_spec = await self.openapi_gen.generate_spec(
                title="Service API", version="1.0.0", requirements=spec.functional_requirements
            )

        # Generate data models
        spec.data_models = await self.model_gen.create_models(spec.functional_requirements)

        # Generate acceptance criteria
        user_stories = await self.parser.parse_user_stories(requirements_text)
        for story in user_stories:
            criteria = await self.criteria_gen.generate_criteria(
                {"actor": story.actor, "action": story.action, "benefit": story.benefit}
            )
            spec.acceptance_criteria.extend(criteria)

        # Detect ambiguities and generate questions
        ambiguities = await self.ambiguity_detector.detect_ambiguities(requirements_text)
        if ambiguities:
            gaps = [
                {"type": "ambiguous_term", "term": a.term, "context": a.context}
                for a in ambiguities
            ]
            spec.clarification_questions = await self.clarification_gen.generate_questions(gaps)

        return spec

    async def generate_specification(
        self,
        service_name: str,
        user_stories: list[str],
        performance_requirements: Optional[dict] = None,
    ) -> ServiceSpecification:
        """Generate complete service specification."""
        spec = ServiceSpecification(service_name=service_name)

        # Process user stories
        all_text = " ".join(user_stories)
        parsed_stories = await self.parser.parse_user_stories(all_text)

        # Extract requirements
        spec.functional_requirements = await self.parser.extract_functional_requirements(all_text)

        # Add performance requirements
        if performance_requirements:
            for key, value in performance_requirements.items():
                nfr = NonFunctionalRequirement(
                    category="performance", target=value, description=f"{key} requirement"
                )
                spec.non_functional_requirements.append(nfr)

        # Generate OpenAPI spec
        spec.openapi_spec = await self.openapi_gen.generate_spec(
            title=service_name, version="1.0.0", requirements=spec.functional_requirements
        )

        # Generate data models
        spec.data_models = await self.model_gen.create_models(spec.functional_requirements)

        # Generate acceptance criteria
        for story in parsed_stories:
            criteria = await self.criteria_gen.generate_criteria(
                {"actor": story.actor, "action": story.action, "benefit": story.benefit}
            )
            spec.acceptance_criteria.extend(criteria)

        return spec

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Execute specification agent task.

        Args:
            input: Agent input containing requirements text or specification request

        Returns:
            Agent output with generated specification artifacts
        """
        try:
            self.logger.info(f"Processing specification task: {input.task_id}")

            intent = input.intent
            payload = input.payload

            if intent == "process_requirements":
                return await self._process_requirements(input)
            elif intent == "generate_specification":
                return await self._generate_specification(input)
            elif intent == "validate_specification":
                return await self._validate_specification(input)
            else:
                return AgentOutput(
                    task_id=input.task_id,
                    status=AgentStatus.FAIL,
                    error=f"Unknown intent: {intent}",
                )

        except Exception as e:
            self.logger.error(f"Specification agent failed: {e}")
            return AgentOutput(task_id=input.task_id, status=AgentStatus.FAIL, error=str(e))

    async def _process_requirements(self, input: AgentInput) -> AgentOutput:
        """Process requirements text into complete specification."""
        requirements_text = input.payload.get("requirements_text", "")
        service_name = input.payload.get("service_name", "Service")

        if not requirements_text:
            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.FAIL,
                error="No requirements text provided",
            )

        spec = await self.process_requirements(requirements_text)
        spec.service_name = service_name

        # Create artifacts
        artifacts = [
            Artifact(
                kind="specification",
                ref="service_specification",
                content=spec,
                metadata={
                    "service_name": service_name,
                    "components": len(spec.functional_requirements),
                },
            ),
            Artifact(
                kind="openapi",
                ref="openapi_spec",
                content=spec.openapi_spec,
                metadata={"version": "3.0.0", "endpoints": len(spec.openapi_spec.get("paths", {}))},
            ),
        ]

        # Calculate metrics
        metrics = {
            "functional_requirements_count": len(spec.functional_requirements),
            "non_functional_requirements_count": len(spec.non_functional_requirements),
            "data_models_count": len(spec.data_models),
            "acceptance_criteria_count": len(spec.acceptance_criteria),
            "clarification_questions_count": len(spec.clarification_questions),
            "clarity_score": await self.ambiguity_detector.score_clarity(requirements_text),
        }

        return AgentOutput(
            task_id=input.task_id, status=AgentStatus.OK, artifacts=artifacts, metrics=metrics
        )

    async def _generate_specification(self, input: AgentInput) -> AgentOutput:
        """Generate complete service specification from structured input."""
        service_name = input.payload.get("service_name", "")
        user_stories = input.payload.get("user_stories", [])
        performance_requirements = input.payload.get("performance_requirements", {})

        if not service_name or not user_stories:
            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.FAIL,
                error="Service name and user stories are required",
            )

        spec = await self.generate_specification(
            service_name=service_name,
            user_stories=user_stories,
            performance_requirements=performance_requirements,
        )

        # Validate specification
        validation_result = await self.validator.validate_completeness(spec)

        artifacts = [
            Artifact(
                kind="specification",
                ref="service_specification",
                content=spec,
                metadata={"service_name": service_name, "is_valid": spec.is_valid()},
            ),
            Artifact(
                kind="validation",
                ref="validation_result",
                content=validation_result,
                metadata={"is_complete": validation_result.is_complete},
            ),
        ]

        metrics = {
            "specification_completeness": 1.0 if validation_result.is_complete else 0.5,
            "missing_elements_count": len(validation_result.missing_elements),
            "functional_requirements_count": len(spec.functional_requirements),
            "data_models_count": len(spec.data_models),
        }

        status = AgentStatus.OK if spec.is_valid() else AgentStatus.RETRY

        return AgentOutput(
            task_id=input.task_id, status=status, artifacts=artifacts, metrics=metrics
        )

    async def _validate_specification(self, input: AgentInput) -> AgentOutput:
        """Validate an existing specification."""
        spec_data = input.payload.get("specification")

        if not spec_data:
            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.FAIL,
                error="No specification provided for validation",
            )

        # Convert dict to ServiceSpecification if needed
        if isinstance(spec_data, dict):
            spec = ServiceSpecification(**spec_data)
        else:
            spec = spec_data

        validation_result = await self.validator.validate_completeness(spec)
        inconsistencies = await self.validator.detect_inconsistencies(spec)

        artifacts = [
            Artifact(
                kind="validation",
                ref="validation_result",
                content=validation_result,
                metadata={"is_complete": validation_result.is_complete},
            ),
            Artifact(
                kind="inconsistencies",
                ref="inconsistencies",
                content=inconsistencies,
                metadata={"count": len(inconsistencies)},
            ),
        ]

        metrics = {
            "completeness_score": 1.0 if validation_result.is_complete else 0.5,
            "inconsistencies_count": len(inconsistencies),
            "missing_elements_count": len(validation_result.missing_elements),
        }

        status = (
            AgentStatus.OK
            if validation_result.is_complete and not inconsistencies
            else AgentStatus.RETRY
        )

        return AgentOutput(
            task_id=input.task_id, status=status, artifacts=artifacts, metrics=metrics
        )

    async def validate(self, output: AgentOutput) -> bool:
        """Validate the agent's output.

        Args:
            output: Output to validate

        Returns:
            True if output is valid
        """
        if output.status == AgentStatus.FAIL:
            return False

        # Check for required artifacts
        artifact_kinds = {artifact.kind for artifact in output.artifacts}

        if "specification" not in artifact_kinds:
            return False

        # Check metrics
        required_metrics = ["functional_requirements_count", "data_models_count"]
        for metric in required_metrics:
            if metric not in output.metrics:
                return False

        return True

    def get_capabilities(self) -> dict[str, Any]:
        """Return agent capabilities for discovery.

        Returns:
            Dictionary of capabilities
        """
        return {
            "name": "SpecificationAgent",
            "version": "1.0.0",
            "description": "Converts natural language requirements into technical specifications",
            "intents": ["process_requirements", "generate_specification", "validate_specification"],
            "inputs": {
                "process_requirements": {
                    "requirements_text": "string",
                    "service_name": "string (optional)",
                },
                "generate_specification": {
                    "service_name": "string",
                    "user_stories": "list[string]",
                    "performance_requirements": "dict (optional)",
                },
                "validate_specification": {"specification": "ServiceSpecification"},
            },
            "outputs": {
                "artifacts": ["specification", "openapi", "validation"],
                "metrics": ["functional_requirements_count", "clarity_score", "completeness_score"],
            },
            "features": [
                "NLP requirement parsing",
                "OpenAPI 3.0 generation",
                "Data model generation",
                "Acceptance criteria creation",
                "Ambiguity detection",
                "Specification validation",
            ],
        }
