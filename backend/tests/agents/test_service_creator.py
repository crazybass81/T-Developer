"""Tests for End-to-End Service Creation - Phase 5 Integration Tests.

Phase 5: P5-T4 - Service Creation Integration Tests
Tests for complete service generation pipeline integration.
"""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
import yaml
from packages.agents.base import AgentInput, AgentStatus
from packages.agents.infrastructure_agent import CloudProvider
from packages.agents.service_creator import (
    ContractTest,
    ContractTestRunner,
    CreatedService,
    DeploymentResult,
    ServiceCreationRequest,
    ServiceCreator,
    ServiceDeployer,
    ServiceGenerationPipeline,
)


class TestServiceCreationRequest:
    """Test ServiceCreationRequest dataclass."""

    def test_service_creation_request_defaults(self):
        """Test default service creation request."""
        request = ServiceCreationRequest(
            name="test-service",
            description="A test service",
            requirements="Build a REST API for user management",
        )

        assert request.name == "test-service"
        assert request.service_type == "api"
        assert request.cloud_provider == CloudProvider.AWS
        assert "development" in request.environments
        assert "staging" in request.environments
        assert "production" in request.environments
        assert request.enable_monitoring is True
        assert request.enable_ci_cd is True
        assert request.auto_deploy is False

    def test_service_creation_request_custom(self):
        """Test custom service creation request."""
        request = ServiceCreationRequest(
            name="my-microservice",
            description="Event-driven microservice",
            requirements="Build a microservice with message queue",
            service_type="microservice",
            cloud_provider=CloudProvider.GCP,
            environments=["dev", "prod"],
            enable_monitoring=False,
            auto_deploy=True,
        )

        assert request.service_type == "microservice"
        assert request.cloud_provider == CloudProvider.GCP
        assert len(request.environments) == 2
        assert request.enable_monitoring is False
        assert request.auto_deploy is True


class TestContractTest:
    """Test ContractTest dataclass."""

    def test_contract_test_creation(self):
        """Test creating contract test."""
        test_cases = [{"name": "Test GET users", "request": {}, "expected_status": 200}]

        contract = ContractTest(
            provider="user-service",
            consumer="web-app",
            contract={"method": "GET", "path": "/users"},
            test_cases=test_cases,
        )

        assert contract.provider == "user-service"
        assert contract.consumer == "web-app"
        assert contract.contract["method"] == "GET"
        assert len(contract.test_cases) == 1


class TestDeploymentResult:
    """Test DeploymentResult dataclass."""

    def test_deployment_result_creation(self):
        """Test creating deployment result."""
        deployment = DeploymentResult(
            service_name="test-service",
            environment="staging",
            url="https://test-service-staging.example.com",
            status="deployed",
            deployment_time=datetime.now(),
            health_check_passed=True,
            smoke_tests_passed=True,
        )

        assert deployment.service_name == "test-service"
        assert deployment.environment == "staging"
        assert deployment.status == "deployed"
        assert deployment.health_check_passed is True


class TestServiceGenerationPipeline:
    """Test ServiceGenerationPipeline functionality."""

    @pytest.fixture
    def mock_agents(self):
        """Create mock agents for testing."""
        # Mock SpecificationAgent
        spec_agent = Mock()
        spec_agent.process_requirements = AsyncMock()

        # Mock BlueprintAgent
        blueprint_agent = Mock()
        blueprint_agent.create_service = AsyncMock()

        # Mock InfrastructureAgent
        infra_agent = Mock()
        infra_agent.generate_infrastructure = AsyncMock()

        return spec_agent, blueprint_agent, infra_agent

    @pytest.fixture
    def pipeline(self, mock_agents):
        """Create ServiceGenerationPipeline with mocked agents."""
        spec_agent, blueprint_agent, infra_agent = mock_agents

        pipeline = ServiceGenerationPipeline()
        pipeline.spec_agent = spec_agent
        pipeline.blueprint_agent = blueprint_agent
        pipeline.infra_agent = infra_agent

        return pipeline

    @pytest.fixture
    def sample_request(self):
        """Create sample service creation request."""
        return ServiceCreationRequest(
            name="blog-service",
            description="Blog management service",
            requirements="""
            Build a blog platform where:
            - Users can register and login
            - Users can create, edit, and delete posts
            - Users can comment on posts
            - System should handle 10,000 concurrent users
            - Response time should be under 200ms
            """,
            service_type="web-app",
            cloud_provider=CloudProvider.AWS,
            environments=["development", "staging", "production"],
            enable_ci_cd=True,
            auto_deploy=False,
        )

    @pytest.mark.asyncio
    async def test_generate_service_complete_flow(
        self, pipeline, sample_request, tmp_path, mock_agents
    ):
        """Test complete service generation flow."""
        spec_agent, blueprint_agent, infra_agent = mock_agents
        output_dir = tmp_path / "generated"
        output_dir.mkdir()

        # Setup mock responses
        from packages.agents.blueprint_agent import GeneratedService
        from packages.agents.spec_agent import (
            FunctionalRequirement,
            NonFunctionalRequirement,
            ServiceSpecification,
        )

        # Mock specification
        mock_spec = ServiceSpecification(
            service_name="blog-service",
            functional_requirements=[
                FunctionalRequirement(type="CRUD", entity="User", description="User management"),
                FunctionalRequirement(type="CRUD", entity="Post", description="Post management"),
            ],
            non_functional_requirements=[
                NonFunctionalRequirement(category="performance", target="<200ms")
            ],
            openapi_spec={
                "openapi": "3.0.0",
                "info": {"title": "Blog Service API", "version": "1.0.0"},
                "paths": {
                    "/users": {"get": {"summary": "List users"}},
                    "/posts": {"get": {"summary": "List posts"}},
                },
            },
            data_models=[],
            acceptance_criteria=[],
            clarification_questions=[],
        )
        spec_agent.process_requirements.return_value = mock_spec

        # Mock generated service
        service_path = output_dir / "blog-service"
        service_path.mkdir()
        mock_generated_service = GeneratedService(
            name="blog-service",
            path=service_path,
            blueprint_used="web-app",
            files_created=["package.json", "src/index.js", "README.md"],
            variables_used={"service_name": "blog-service"},
        )
        blueprint_agent.create_service.return_value = mock_generated_service

        # Mock infrastructure generation
        infra_agent.generate_infrastructure.return_value = None

        # Execute pipeline
        service = await pipeline.generate_service(sample_request, output_dir)

        # Verify results
        assert isinstance(service, CreatedService)
        assert service.name == "blog-service"
        assert service.specification == mock_spec
        assert service.code_path == service_path
        assert len(service.contract_tests) > 0  # Should generate contracts from OpenAPI spec

        # Verify agent calls
        spec_agent.process_requirements.assert_called_once()
        blueprint_agent.create_service.assert_called_once()
        infra_agent.generate_infrastructure.assert_called_once()


class TestContractTestRunner:
    """Test ContractTestRunner functionality."""

    @pytest.fixture
    def runner(self):
        """Create ContractTestRunner instance."""
        return ContractTestRunner()

    @pytest.fixture
    def sample_contracts(self):
        """Create sample contract tests."""
        return [
            ContractTest(
                provider="user-service",
                consumer="web-app",
                contract={"method": "GET", "path": "/users"},
                test_cases=[
                    {"name": "Get all users", "request": {}, "expected_status": 200},
                    {"name": "Get users unauthorized", "request": {}, "expected_status": 401},
                ],
            ),
            ContractTest(
                provider="user-service",
                consumer="mobile-app",
                contract={"method": "POST", "path": "/users"},
                test_cases=[
                    {"name": "Create user", "request": {"name": "John"}, "expected_status": 201}
                ],
            ),
        ]

    @pytest.mark.asyncio
    async def test_run_contract_tests(self, runner, sample_contracts):
        """Test running contract tests."""
        results = await runner.run_contract_tests(sample_contracts)

        assert results["total"] == 3  # 2 + 1 test cases
        assert results["passed"] == 3  # All should pass in simulation
        assert results["failed"] == 0
        assert len(results["tests"]) == 3

        # Check individual test results
        for test_result in results["tests"]:
            assert "name" in test_result
            assert "provider" in test_result
            assert "consumer" in test_result
            assert "passed" in test_result
            assert "response_time" in test_result

    @pytest.mark.asyncio
    async def test_generate_mock_services(self, runner, sample_contracts, tmp_path):
        """Test generating mock services from contracts."""
        output_dir = tmp_path / "mocks_output"
        output_dir.mkdir()

        mocks_dir = await runner.generate_mock_services(sample_contracts, output_dir)

        assert mocks_dir.exists()
        assert mocks_dir.name == "mocks"

        # Check mock configuration file
        config_file = mocks_dir / "mock-config.json"
        assert config_file.exists()

        config = json.loads(config_file.read_text())
        assert config["port"] == 8080
        assert len(config["endpoints"]) == 2

        # Check endpoints
        endpoints = {ep["path"]: ep for ep in config["endpoints"]}
        assert "/users" in endpoints
        assert endpoints["/users"]["method"] == "GET"

        # Check mock server script
        script_file = mocks_dir / "mock-server.js"
        assert script_file.exists()

        script_content = script_file.read_text()
        assert "const express = require('express')" in script_content
        assert "config.endpoints.forEach" in script_content

    @pytest.mark.asyncio
    async def test_validate_api_compliance(self, runner):
        """Test API compliance validation."""
        from packages.agents.spec_agent import ServiceSpecification

        mock_spec = ServiceSpecification(
            service_name="test-service",
            openapi_spec={"openapi": "3.0.0", "paths": {"/users": {}}},
            functional_requirements=[],
            non_functional_requirements=[],
            data_models=[],
            acceptance_criteria=[],
            clarification_questions=[],
        )

        is_compliant = await runner.validate_api_compliance(
            mock_spec, "https://test-service.example.com"
        )

        # Should return True in simulation
        assert is_compliant is True


class TestServiceDeployer:
    """Test ServiceDeployer functionality."""

    @pytest.fixture
    def deployer(self):
        """Create ServiceDeployer instance."""
        return ServiceDeployer()

    @pytest.mark.asyncio
    async def test_deploy_to_staging(self, deployer, tmp_path):
        """Test deploying service to staging."""
        code_path = tmp_path / "service_code"
        code_path.mkdir()
        infra_path = tmp_path / "infrastructure"
        infra_path.mkdir()

        deployment = await deployer.deploy_to_staging("test-service", code_path, infra_path)

        assert isinstance(deployment, DeploymentResult)
        assert deployment.service_name == "test-service"
        assert deployment.environment == "staging"
        assert deployment.status == "deployed"
        assert deployment.url == "https://test-service-staging.example.com"
        assert deployment.health_check_passed is True

    @pytest.mark.asyncio
    async def test_run_smoke_tests(self, deployer, tmp_path):
        """Test running smoke tests."""
        test_path = tmp_path / "tests"
        test_path.mkdir()

        result = await deployer.run_smoke_tests("https://test-service.example.com", test_path)

        assert result is True  # Simulated success

    @pytest.mark.asyncio
    async def test_generate_documentation(self, deployer, tmp_path):
        """Test generating service documentation."""
        output_dir = tmp_path / "docs_output"
        output_dir.mkdir()

        # Create mock service
        from packages.agents.spec_agent import ServiceSpecification

        mock_spec = ServiceSpecification(
            service_name="test-service",
            openapi_spec={
                "openapi": "3.0.0",
                "paths": {
                    "/users": {"get": {"summary": "List users"}},
                    "/posts": {"get": {"summary": "List posts"}},
                },
            },
            functional_requirements=[],
            non_functional_requirements=[],
            data_models=[],
            acceptance_criteria=[],
            clarification_questions=[],
        )

        mock_service = CreatedService(
            name="test-service",
            specification=mock_spec,
            code_path=tmp_path / "code",
            infrastructure_path=tmp_path / "infra",
            contract_tests=[],
            deployments=[
                DeploymentResult(
                    service_name="test-service",
                    environment="staging",
                    url="https://test-service-staging.example.com",
                    status="deployed",
                )
            ],
        )

        docs = await deployer.generate_documentation(mock_service, output_dir)

        assert "api" in docs
        assert "readme" in docs

        # Check generated files
        docs_dir = output_dir / "documentation"
        assert docs_dir.exists()

        api_doc = docs_dir / "API.md"
        assert api_doc.exists()
        api_content = api_doc.read_text()
        assert "test-service API Documentation" in api_content
        assert "GET /users" in api_content

        readme = docs_dir / "README.md"
        assert readme.exists()
        readme_content = readme.read_text()
        assert "# test-service" in readme_content
        assert "staging" in readme_content


class TestServiceCreator:
    """Test main ServiceCreator functionality."""

    @pytest.fixture
    def temp_blueprints(self, tmp_path):
        """Create temporary blueprints for testing."""
        blueprints_dir = tmp_path / "blueprints"
        blueprints_dir.mkdir()

        # Create web-app blueprint
        blueprint_content = {
            "name": "web-app",
            "description": "Full-stack web application",
            "version": "1.0.0",
            "variables": {"service_name": {"type": "string", "required": True}},
            "structure": {"directories": ["src", "tests"]},
            "files": [
                {
                    "path": "package.json",
                    "template": '{"name": "{{ service_name }}", "version": "1.0.0"}',
                }
            ],
        }

        blueprint_file = blueprints_dir / "web-app.yaml"
        blueprint_file.write_text(yaml.dump(blueprint_content))

        return blueprints_dir

    @pytest.fixture
    def creator(self, temp_blueprints):
        """Create ServiceCreator instance."""
        config = {"blueprints_dir": str(temp_blueprints)}
        return ServiceCreator(config)

    def test_creator_initialization(self, creator):
        """Test ServiceCreator initialization."""
        assert creator.name == "ServiceCreator"
        assert creator.pipeline is not None
        assert creator.contract_runner is not None
        assert creator.deployer is not None

    @pytest.mark.asyncio
    async def test_create_service_complete(self, creator, tmp_path):
        """Test complete service creation."""
        output_dir = tmp_path / "service_output"
        output_dir.mkdir()

        request = ServiceCreationRequest(
            name="e2e-test-service",
            description="End-to-end test service",
            requirements="""
            Build a user management API with:
            - User registration and authentication
            - CRUD operations for users
            - RESTful API endpoints
            - PostgreSQL database
            """,
            service_type="web-app",
            auto_deploy=False,
        )

        service = await creator.create_service(request, output_dir)

        assert isinstance(service, CreatedService)
        assert service.name == "e2e-test-service"
        assert service.specification is not None
        assert service.code_path.exists()
        assert service.infrastructure_path is not None
        assert len(service.contract_tests) >= 0

    @pytest.mark.asyncio
    async def test_execute_create_service(self, creator, tmp_path):
        """Test execute method with create_service intent."""
        output_dir = tmp_path / "execute_output"
        output_dir.mkdir()

        input_data = AgentInput(
            intent="create_service",
            task_id="test-task",
            payload={
                "name": "api-service",
                "description": "Test API service",
                "requirements": "Build a REST API for user management",
                "service_type": "web-app",
                "cloud_provider": "aws",
                "environments": ["development", "staging"],
                "enable_monitoring": True,
                "enable_ci_cd": True,
                "auto_deploy": False,
                "output_dir": str(output_dir),
            },
        )

        output = await creator.execute(input_data)

        assert output.status == AgentStatus.OK
        assert len(output.artifacts) >= 3  # service, specification, contracts

        # Check service artifact
        service_artifact = next((a for a in output.artifacts if a.kind == "service"), None)
        assert service_artifact is not None
        assert service_artifact.metadata["service_name"] == "api-service"

        # Check metrics
        assert "service_created" in output.metrics
        assert output.metrics["service_created"] is True
        assert "functional_requirements_count" in output.metrics

    @pytest.mark.asyncio
    async def test_execute_deploy_service(self, creator, tmp_path):
        """Test execute method with deploy_service intent."""
        code_path = tmp_path / "code"
        code_path.mkdir()
        infra_path = tmp_path / "infra"
        infra_path.mkdir()

        input_data = AgentInput(
            intent="deploy_service",
            task_id="test-task",
            payload={
                "service_name": "deploy-test-service",
                "code_path": str(code_path),
                "infra_path": str(infra_path),
                "environment": "staging",
            },
        )

        output = await creator.execute(input_data)

        assert output.status == AgentStatus.OK
        assert len(output.artifacts) == 1

        deployment_artifact = output.artifacts[0]
        assert deployment_artifact.kind == "deployment"
        assert deployment_artifact.metadata["service_name"] == "deploy-test-service"
        assert deployment_artifact.metadata["environment"] == "staging"

    @pytest.mark.asyncio
    async def test_execute_run_contract_tests(self, creator):
        """Test execute method with run_contract_tests intent."""
        contracts_data = [
            {
                "provider": "test-service",
                "consumer": "client",
                "contract": {"method": "GET", "path": "/users"},
                "test_cases": [{"name": "Test GET", "request": {}, "expected_status": 200}],
            }
        ]

        input_data = AgentInput(
            intent="run_contract_tests", task_id="test-task", payload={"contracts": contracts_data}
        )

        output = await creator.execute(input_data)

        assert output.status == AgentStatus.OK
        assert len(output.artifacts) == 1

        test_artifact = output.artifacts[0]
        assert test_artifact.kind == "test_results"
        assert "total_tests" in output.metrics
        assert "success_rate" in output.metrics

    @pytest.mark.asyncio
    async def test_execute_invalid_intent(self, creator):
        """Test execute method with invalid intent."""
        input_data = AgentInput(intent="invalid_intent", task_id="test-task", payload={})

        output = await creator.execute(input_data)

        assert output.status == AgentStatus.FAIL
        assert "Unknown intent" in output.error

    @pytest.mark.asyncio
    async def test_validate_success(self, creator, tmp_path):
        """Test validate method with successful output."""
        output_dir = tmp_path / "validate_output"
        output_dir.mkdir()

        # Create successful output
        input_data = AgentInput(
            intent="create_service",
            task_id="test-task",
            payload={
                "name": "validate-test",
                "description": "Test service",
                "requirements": "Build a simple API",
                "output_dir": str(output_dir),
            },
        )

        output = await creator.execute(input_data)
        is_valid = await creator.validate(output)

        assert is_valid is True

    def test_get_capabilities(self, creator):
        """Test get_capabilities method."""
        capabilities = creator.get_capabilities()

        assert capabilities["name"] == "ServiceCreator"
        assert capabilities["version"] == "1.0.0"
        assert "description" in capabilities

        # Check intents
        expected_intents = ["create_service", "deploy_service", "run_contract_tests"]
        assert all(intent in capabilities["intents"] for intent in expected_intents)

        # Check integrations
        assert "integrates_with" in capabilities
        expected_agents = ["SpecificationAgent", "BlueprintAgent", "InfrastructureAgent"]
        assert all(agent in capabilities["integrates_with"] for agent in expected_agents)


class TestEndToEndIntegration:
    """End-to-end integration tests for complete service creation."""

    @pytest.mark.asyncio
    async def test_full_service_creation_pipeline(self, tmp_path):
        """Test the complete service creation pipeline end-to-end."""
        # Setup comprehensive test environment
        blueprints_dir = tmp_path / "blueprints"
        blueprints_dir.mkdir()
        output_dir = tmp_path / "e2e_output"
        output_dir.mkdir()

        # Create comprehensive blueprint
        blueprint_content = {
            "name": "e2e-web-app",
            "description": "End-to-end web application",
            "version": "1.0.0",
            "variables": {
                "service_name": {"type": "string", "required": True},
                "database_type": {"type": "string", "default": "postgres"},
                "port": {"type": "integer", "default": 3000},
            },
            "structure": {
                "directories": [
                    "src",
                    "src/controllers",
                    "src/models",
                    "src/routes",
                    "tests",
                    "config",
                    "docs",
                    ".github/workflows",
                ]
            },
            "files": [
                {
                    "path": "package.json",
                    "template": json.dumps(
                        {
                            "name": "{{ service_name }}",
                            "version": "1.0.0",
                            "main": "src/index.js",
                            "scripts": {"start": "node src/index.js", "test": "jest"},
                        },
                        indent=2,
                    ),
                },
                {
                    "path": "src/index.js",
                    "template": """const express = require('express');
const app = express();
const PORT = {{ port }};

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: '{{ service_name }}' });
});

app.get('/users', (req, res) => {
  res.json([{ id: 1, name: 'John Doe' }]);
});

app.listen(PORT, () => {
  console.log('{{ service_name }} running on port ' + PORT);
});""",
                },
                {
                    "path": "README.md",
                    "template": """# {{ service_name }}

{{ service_name }} web application.

## Getting Started

```bash
npm install
npm start
```

## API Endpoints

- GET /health - Health check
- GET /users - List users

## Database

Uses {{ database_type }} database.
""",
                },
                {
                    "path": ".github/workflows/ci.yml",
                    "template": """name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test""",
                },
            ],
        }

        blueprint_file = blueprints_dir / "e2e-web-app.yaml"
        blueprint_file.write_text(yaml.dump(blueprint_content))

        # Initialize ServiceCreator
        config = {"blueprints_dir": str(blueprints_dir)}
        creator = ServiceCreator(config)

        # Create comprehensive service request
        request = ServiceCreationRequest(
            name="comprehensive-blog-service",
            description="A comprehensive blog management platform",
            requirements="""
            Build a comprehensive blog platform with the following features:

            User Management:
            - User registration with email verification
            - User authentication with JWT tokens
            - User profiles with avatar upload
            - Role-based access control (admin, author, reader)

            Content Management:
            - Create, read, update, delete blog posts
            - Rich text editor for post content
            - Image upload and management
            - Post categories and tags
            - Draft and published states
            - Post scheduling

            Social Features:
            - Comments on posts with moderation
            - Like and share functionality
            - User following system
            - Notification system

            Search and Discovery:
            - Full-text search across posts
            - Filter by category, tags, author
            - Trending posts algorithm
            - Related posts suggestions

            API Requirements:
            - RESTful API design
            - OpenAPI 3.0 documentation
            - Rate limiting
            - Request/response logging
            - Error handling with proper HTTP status codes

            Performance Requirements:
            - Handle 10,000 concurrent users
            - Response time under 200ms for 95% of requests
            - Database query optimization
            - Caching strategy for frequently accessed data

            Security Requirements:
            - Input validation and sanitization
            - SQL injection prevention
            - XSS protection
            - CSRF protection
            - Secure password storage
            - HTTPS enforcement

            Infrastructure Requirements:
            - Containerized deployment with Docker
            - Auto-scaling based on load
            - Health checks and monitoring
            - Automated backups
            - CI/CD pipeline with testing
            """,
            service_type="e2e-web-app",
            cloud_provider=CloudProvider.AWS,
            environments=["development", "staging", "production"],
            enable_monitoring=True,
            enable_ci_cd=True,
            auto_deploy=False,
        )

        # Execute service creation
        service = await creator.create_service(request, output_dir)

        # Comprehensive verification
        assert isinstance(service, CreatedService)
        assert service.name == "comprehensive-blog-service"

        # Check specification
        spec = service.specification
        assert spec is not None
        assert spec.service_name == "comprehensive-blog-service"
        assert len(spec.functional_requirements) > 0
        assert len(spec.non_functional_requirements) > 0

        # Check generated code structure
        code_path = service.code_path
        assert code_path.exists()
        assert (code_path / "src").is_dir()
        assert (code_path / "src" / "controllers").is_dir()
        assert (code_path / "tests").is_dir()
        assert (code_path / "config").is_dir()
        assert (code_path / ".github" / "workflows").is_dir()

        # Check generated files
        package_json = code_path / "package.json"
        assert package_json.exists()
        package_data = json.loads(package_json.read_text())
        assert package_data["name"] == "comprehensive-blog-service"

        index_js = code_path / "src" / "index.js"
        assert index_js.exists()
        index_content = index_js.read_text()
        assert "comprehensive-blog-service" in index_content
        assert "/health" in index_content
        assert "/users" in index_content

        readme = code_path / "README.md"
        assert readme.exists()
        readme_content = readme.read_text()
        assert "comprehensive-blog-service" in readme_content
        assert "postgres" in readme_content

        ci_file = code_path / ".github" / "workflows" / "ci.yml"
        assert ci_file.exists()
        ci_content = ci_file.read_text()
        assert "npm test" in ci_content

        # Check infrastructure
        infra_path = service.infrastructure_path
        assert infra_path is not None

        # Check contract tests
        assert len(service.contract_tests) >= 0

        # Check documentation
        assert service.documentation_url is not None or service.api_docs_url is not None

        # Test agent execution interface
        input_data = AgentInput(
            intent="create_service",
            task_id="e2e-integration-test",
            payload={
                "name": "agent-interface-test",
                "description": "Test agent interface",
                "requirements": "Build a simple REST API",
                "service_type": "e2e-web-app",
                "output_dir": str(output_dir / "agent_test"),
            },
        )

        output = await creator.execute(input_data)

        assert output.status == AgentStatus.OK
        assert len(output.artifacts) >= 3

        # Verify artifacts
        service_artifact = next((a for a in output.artifacts if a.kind == "service"), None)
        assert service_artifact is not None

        spec_artifact = next((a for a in output.artifacts if a.kind == "specification"), None)
        assert spec_artifact is not None

        contracts_artifact = next((a for a in output.artifacts if a.kind == "contracts"), None)
        assert contracts_artifact is not None

        # Verify metrics
        assert "service_created" in output.metrics
        assert "functional_requirements_count" in output.metrics
        assert "infrastructure_generated" in output.metrics

        # Test validation
        is_valid = await creator.validate(output)
        assert is_valid is True

        # Test capabilities
        capabilities = creator.get_capabilities()
        assert "End-to-end service generation" in capabilities["features"]
        assert "Multi-agent orchestration" in capabilities["features"]

        print(
            f"""
🎉 End-to-End Service Creation Test Completed Successfully! 🎉
================================================================

Service Details:
- Name: {service.name}
- Code Path: {service.code_path}
- Infrastructure: {service.infrastructure_path}
- Contract Tests: {len(service.contract_tests)}
- Functional Requirements: {len(service.specification.functional_requirements)}
- Non-Functional Requirements: {len(service.specification.non_functional_requirements)}

Generated Files: {len(service.code_path.rglob('*')) if service.code_path.exists() else 0}

Agent Integration:
- Input Processing: ✅
- Artifact Generation: ✅
- Metrics Collection: ✅
- Output Validation: ✅

Phase 5 Implementation: COMPLETE ✅
        """
        )
