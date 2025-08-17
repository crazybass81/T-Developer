"""Tests for ServiceBuilder - Main orchestrator for automatic service creation."""

from unittest.mock import AsyncMock

import pytest
from packages.meta_agents.service_builder import (
    ServiceBuilder,
    ServiceBuilderConfig,
    ServiceDefinition,
)


class TestServiceBuilderConfig:
    """Test service builder configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ServiceBuilderConfig()

        assert config.enable_ai_analysis is True
        assert config.auto_generate_agents is True
        assert config.create_workflows is True
        assert config.validate_requirements is True
        assert config.max_agents_per_service == 10
        assert config.default_timeout_minutes == 60

    def test_custom_config(self):
        """Test custom configuration."""
        config = ServiceBuilderConfig(
            enable_ai_analysis=False, max_agents_per_service=5, default_timeout_minutes=30
        )

        assert config.enable_ai_analysis is False
        assert config.max_agents_per_service == 5
        assert config.default_timeout_minutes == 30


class TestServiceDefinition:
    """Test service definition."""

    def test_service_creation(self):
        """Test creating service definition."""
        service = ServiceDefinition(
            name="UserService",
            description="Manages user operations",
            requirements=["Create users", "Authenticate users"],
            agents=["UserAgent", "AuthAgent"],
            workflow_id="workflow-123",
        )

        assert service.name == "UserService"
        assert service.description == "Manages user operations"
        assert len(service.requirements) == 2
        assert len(service.agents) == 2
        assert service.workflow_id == "workflow-123"

    def test_service_validation(self):
        """Test service validation."""
        valid_service = ServiceDefinition(
            name="TestService",
            description="Test service",
            requirements=["Requirement 1"],
            agents=["Agent1"],
            workflow_id="workflow-1",
        )

        assert valid_service.validate() is True

        # Invalid service (no name)
        invalid_service = ServiceDefinition(
            name="",
            description="Test",
            requirements=["Req"],
            agents=["Agent"],
            workflow_id="workflow",
        )

        assert invalid_service.validate() is False


class TestServiceBuilder:
    """Test service builder."""

    @pytest.fixture
    def builder(self):
        """Create service builder with mocked dependencies."""
        config = ServiceBuilderConfig()
        builder = ServiceBuilder(config)

        # Mock the meta agents
        builder.requirement_analyzer = AsyncMock()
        builder.agent_generator = AsyncMock()
        builder.workflow_composer = AsyncMock()

        return builder

    @pytest.mark.asyncio
    async def test_build_service_complete_flow(self, builder):
        """Test complete service building flow."""
        # Setup mock responses
        builder.requirement_analyzer.analyze_requirements.return_value = {
            "requirements": [
                {
                    "id": "REQ-1",
                    "description": "Create user API",
                    "priority": "high",
                    "acceptance_criteria": ["REST endpoint", "Validation", "Database storage"],
                },
                {
                    "id": "REQ-2",
                    "description": "User authentication",
                    "priority": "high",
                    "acceptance_criteria": ["JWT tokens", "Password hashing"],
                    "depends_on": ["REQ-1"],
                },
            ],
            "analysis": {"complexity": "medium", "estimated_effort": 40, "technical_debt": "low"},
        }

        builder.agent_generator.generate_agents.return_value = [
            {"agent_name": "UserAgent", "code": "class UserAgent: pass", "success": True},
            {"agent_name": "AuthAgent", "code": "class AuthAgent: pass", "success": True},
        ]

        builder.workflow_composer.compose.return_value = {
            "id": "workflow-123",
            "name": "User Service Workflow",
            "steps": [
                {"id": "step-1", "agent": "UserAgent"},
                {"id": "step-2", "agent": "AuthAgent", "dependencies": ["step-1"]},
            ],
        }

        # Execute service building
        service_request = {
            "name": "UserService",
            "description": "Complete user management service",
            "requirements_text": "Need to create users and authenticate them with JWT tokens",
        }

        result = await builder.build_service(service_request)

        # Verify results
        assert result["success"] is True
        assert result["service"]["name"] == "UserService"
        assert len(result["service"]["agents"]) == 2
        assert result["service"]["workflow_id"] == "workflow-123"

        # Verify agent calls
        builder.requirement_analyzer.analyze_requirements.assert_called_once()
        builder.agent_generator.generate_agents.assert_called_once()
        builder.workflow_composer.compose.assert_called_once()

    @pytest.mark.asyncio
    async def test_build_service_with_validation_failure(self, builder):
        """Test service building with requirement validation failure."""
        # Setup mock to return invalid requirements
        builder.requirement_analyzer.analyze_requirements.return_value = {
            "requirements": [],  # Empty requirements should fail validation
            "analysis": {"complexity": "low"},
        }

        service_request = {
            "name": "EmptyService",
            "description": "Service with no requirements",
            "requirements_text": "",
        }

        result = await builder.build_service(service_request)

        assert result["success"] is False
        assert "validation" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_build_service_with_agent_generation_failure(self, builder):
        """Test service building with agent generation failure."""
        # Setup mocks
        builder.requirement_analyzer.analyze_requirements.return_value = {
            "requirements": [
                {"id": "REQ-1", "description": "Test requirement", "priority": "medium"}
            ],
            "analysis": {"complexity": "low"},
        }

        # Agent generation fails
        builder.agent_generator.generate_agents.return_value = [
            {"agent_name": "FailedAgent", "success": False, "error": "Generation failed"}
        ]

        service_request = {
            "name": "FailingService",
            "description": "Service that fails agent generation",
            "requirements_text": "Simple requirement",
        }

        result = await builder.build_service(service_request)

        assert result["success"] is False
        assert "agent generation" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_validate_service_definition(self, builder):
        """Test service definition validation."""
        # Valid service
        valid_service = {
            "name": "ValidService",
            "description": "A valid service",
            "requirements": ["Req1", "Req2"],
            "agents": ["Agent1", "Agent2"],
            "workflow_id": "workflow-123",
        }

        assert await builder.validate_service(valid_service) is True

        # Invalid service (missing required fields)
        invalid_service = {
            "name": "",  # Empty name
            "description": "Invalid service",
            "requirements": [],  # No requirements
            "agents": ["Agent1"],
        }

        assert await builder.validate_service(invalid_service) is False

    @pytest.mark.asyncio
    async def test_generate_service_documentation(self, builder):
        """Test service documentation generation."""
        service = {
            "name": "TestService",
            "description": "A test service",
            "requirements": ["Requirement 1", "Requirement 2"],
            "agents": ["Agent1", "Agent2"],
            "workflow_id": "workflow-123",
            "created_at": "2025-08-16T10:00:00Z",
        }

        documentation = await builder.generate_documentation(service)

        assert "TestService" in documentation
        assert "A test service" in documentation
        assert "Agent1" in documentation
        assert "Agent2" in documentation
        assert "Requirements" in documentation

    @pytest.mark.asyncio
    async def test_save_service(self, builder, tmp_path):
        """Test saving service to files."""
        service = {
            "name": "SavedService",
            "description": "Service to be saved",
            "requirements": ["Req1"],
            "agents": ["Agent1"],
            "workflow_id": "workflow-123",
            "agent_code": {"Agent1": "class Agent1: pass"},
            "workflow": {"id": "workflow-123", "steps": [{"id": "step-1", "agent": "Agent1"}]},
        }

        result = await builder.save_service(service, tmp_path)

        assert result["success"] is True
        assert len(result["files"]) > 0

        # Check that files were created
        service_dir = tmp_path / "saved_service"
        assert service_dir.exists()

    @pytest.mark.asyncio
    async def test_load_service(self, builder, tmp_path):
        """Test loading service from files."""
        # Create a service directory structure
        service_dir = tmp_path / "test_service"
        service_dir.mkdir()

        # Create service.json
        service_config = {
            "name": "LoadedService",
            "description": "Service loaded from files",
            "agents": ["Agent1"],
        }

        import json

        (service_dir / "service.json").write_text(json.dumps(service_config))

        # Load service
        loaded_service = await builder.load_service(service_dir)

        assert loaded_service["name"] == "LoadedService"
        assert loaded_service["description"] == "Service loaded from files"

    @pytest.mark.asyncio
    async def test_optimize_service(self, builder):
        """Test service optimization."""
        service = {
            "name": "OptimizableService",
            "description": "Service that can be optimized",
            "agents": ["Agent1", "Agent2", "Agent3"],
            "workflow": {
                "steps": [
                    {"id": "step-1", "agent": "Agent1", "estimated_duration": 30},
                    {"id": "step-2", "agent": "Agent2", "estimated_duration": 20},
                    {"id": "step-3", "agent": "Agent3", "estimated_duration": 25},
                ]
            },
        }

        builder.workflow_composer.optimize.return_value = {
            "optimized": True,
            "parallel_groups": [["step-1", "step-2"], ["step-3"]],
            "estimated_duration": 55,  # Reduced from 75 due to parallelization
        }

        optimized = await builder.optimize_service(service)

        assert optimized["optimized"] is True
        assert "parallel_groups" in optimized
        builder.workflow_composer.optimize.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_service_metrics(self, builder):
        """Test getting service metrics."""
        service = {
            "name": "MetricsService",
            "agents": ["Agent1", "Agent2"],
            "workflow": {
                "steps": [
                    {"id": "step-1", "estimated_duration": 15},
                    {"id": "step-2", "estimated_duration": 25},
                ]
            },
            "requirements": ["Req1", "Req2", "Req3"],
        }

        metrics = await builder.get_metrics(service)

        assert metrics["agent_count"] == 2
        assert metrics["workflow_steps"] == 2
        assert metrics["estimated_duration"] == 40
        assert metrics["requirement_count"] == 3
        assert metrics["complexity_score"] > 0

    @pytest.mark.asyncio
    async def test_service_builder_capabilities(self, builder):
        """Test service builder capabilities."""
        capabilities = builder.get_capabilities()

        assert "name" in capabilities
        assert capabilities["name"] == "ServiceBuilder"
        assert "version" in capabilities
        assert "features" in capabilities
        assert "requirement_analysis" in capabilities["features"]
        assert "agent_generation" in capabilities["features"]
        assert "workflow_composition" in capabilities["features"]
