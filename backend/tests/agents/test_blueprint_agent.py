"""Tests for Blueprint Agent - Service scaffolding and template generation.

Phase 5: P5-T2 - Blueprint Agent Tests
Tests for template-based service generation and scaffolding.
"""

from __future__ import annotations

import json
from unittest.mock import Mock

import pytest
import yaml
from packages.agents.base import AgentInput, AgentOutput, AgentStatus
from packages.agents.blueprint_agent import (
    Blueprint,
    BlueprintAgent,
    BlueprintCatalog,
    BlueprintVariable,
    GeneratedService,
    ProjectScaffolder,
)


class TestBlueprintVariable:
    """Test BlueprintVariable dataclass."""

    def test_blueprint_variable_creation(self):
        """Test creating blueprint variables."""
        var = BlueprintVariable(
            name="service_name",
            type="string",
            description="Name of the service",
            required=True,
            default="my-service",
        )

        assert var.name == "service_name"
        assert var.type == "string"
        assert var.required is True
        assert var.default == "my-service"

    def test_blueprint_variable_validation(self):
        """Test blueprint variable validation."""
        var = BlueprintVariable(
            name="port", type="integer", description="Service port", required=False, default=3000
        )

        # Valid integer
        assert var.validate_value(8080) is True

        # Invalid type
        assert var.validate_value("invalid") is False

    def test_blueprint_variable_defaults(self):
        """Test blueprint variable with defaults."""
        var = BlueprintVariable(name="debug", type="boolean", description="Enable debug mode")

        assert var.required is False
        assert var.default is None


class TestBlueprintCatalog:
    """Test BlueprintCatalog functionality."""

    @pytest.fixture
    def temp_blueprints_dir(self, tmp_path):
        """Create temporary blueprints directory."""
        blueprints_dir = tmp_path / "blueprints"
        blueprints_dir.mkdir()

        # Create a test blueprint
        blueprint_content = {
            "name": "test-api",
            "description": "Test API blueprint",
            "version": "1.0.0",
            "variables": {
                "service_name": {
                    "type": "string",
                    "description": "Name of the service",
                    "required": True,
                }
            },
            "structure": {"directories": ["src", "tests"]},
            "files": [
                {
                    "path": "src/main.py",
                    "template": "# {{ service_name }} main file\nprint('Hello {{ service_name }}')",
                }
            ],
        }

        blueprint_file = blueprints_dir / "test-api.yaml"
        blueprint_file.write_text(yaml.dump(blueprint_content))

        return blueprints_dir

    @pytest.fixture
    def catalog(self, temp_blueprints_dir):
        """Create BlueprintCatalog instance."""
        return BlueprintCatalog(temp_blueprints_dir)

    def test_list_blueprints(self, catalog):
        """Test listing available blueprints."""
        blueprints = catalog.list_blueprints()
        assert "test-api" in blueprints

    def test_load_blueprint(self, catalog):
        """Test loading a blueprint."""
        blueprint = catalog.load_blueprint("test-api")

        assert blueprint is not None
        assert blueprint.name == "test-api"
        assert blueprint.description == "Test API blueprint"
        assert blueprint.version == "1.0.0"
        assert len(blueprint.variables) == 1
        assert "service_name" in blueprint.variables

    def test_load_nonexistent_blueprint(self, catalog):
        """Test loading non-existent blueprint."""
        blueprint = catalog.load_blueprint("nonexistent")
        assert blueprint is None

    def test_get_blueprint_info(self, catalog):
        """Test getting blueprint information."""
        info = catalog.get_blueprint_info("test-api")

        assert info is not None
        assert info["name"] == "test-api"
        assert info["description"] == "Test API blueprint"
        assert info["version"] == "1.0.0"
        assert "variables" in info

    def test_validate_blueprint(self, catalog):
        """Test blueprint validation."""
        blueprint = catalog.load_blueprint("test-api")

        # Valid configuration
        config = {"service_name": "my-api"}
        errors = catalog.validate_blueprint_config(blueprint, config)
        assert len(errors) == 0

        # Missing required variable
        config = {}
        errors = catalog.validate_blueprint_config(blueprint, config)
        assert len(errors) > 0
        assert any("service_name" in error for error in errors)


class TestProjectScaffolder:
    """Test ProjectScaffolder functionality."""

    @pytest.fixture
    def mock_catalog(self):
        """Create mock BlueprintCatalog."""
        catalog = Mock()

        # Mock blueprint
        blueprint = Blueprint(
            name="test-api",
            description="Test API",
            version="1.0.0",
            variables={
                "service_name": BlueprintVariable(
                    name="service_name", type="string", description="Service name", required=True
                )
            },
            structure={"directories": ["src", "tests"]},
            files=[
                {
                    "path": "src/main.py",
                    "template": "# {{ service_name }} main file\nprint('Hello {{ service_name }}')",
                },
                {
                    "path": "package.json",
                    "template": '{"name": "{{ service_name }}", "version": "1.0.0"}',
                },
            ],
        )

        catalog.load_blueprint.return_value = blueprint
        catalog.validate_blueprint_config.return_value = []

        return catalog

    @pytest.fixture
    def scaffolder(self, mock_catalog):
        """Create ProjectScaffolder instance."""
        return ProjectScaffolder(mock_catalog)

    @pytest.mark.asyncio
    async def test_scaffold_project(self, scaffolder, tmp_path):
        """Test scaffolding a complete project."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        service = await scaffolder.scaffold_project(
            blueprint_name="test-api",
            project_name="my-test-api",
            output_dir=output_dir,
            config={"service_name": "my-test-api"},
        )

        assert service.name == "my-test-api"
        assert service.blueprint_used == "test-api"
        assert service.path == output_dir / "my-test-api"
        assert len(service.files_created) >= 2

        # Check if directories were created
        project_path = output_dir / "my-test-api"
        assert (project_path / "src").exists()
        assert (project_path / "tests").exists()

        # Check if files were created and templated
        main_file = project_path / "src" / "main.py"
        assert main_file.exists()
        content = main_file.read_text()
        assert "my-test-api" in content
        assert "Hello my-test-api" in content

    @pytest.mark.asyncio
    async def test_create_directory_structure(self, scaffolder, tmp_path):
        """Test creating directory structure."""
        project_path = tmp_path / "test-project"
        directories = ["src", "src/controllers", "tests", "docs"]

        await scaffolder._create_directory_structure(project_path, directories)

        assert (project_path / "src").exists()
        assert (project_path / "src" / "controllers").exists()
        assert (project_path / "tests").exists()
        assert (project_path / "docs").exists()

    @pytest.mark.asyncio
    async def test_render_template_files(self, scaffolder, tmp_path):
        """Test rendering template files."""
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        files = [
            {
                "path": "config.json",
                "template": '{"name": "{{ service_name }}", "port": {{ port }}}',
            }
        ]

        config = {"service_name": "test-service", "port": 8080}

        created_files = await scaffolder._render_template_files(project_path, files, config)

        assert len(created_files) == 1
        assert "config.json" in created_files[0]

        config_file = project_path / "config.json"
        assert config_file.exists()

        content = json.loads(config_file.read_text())
        assert content["name"] == "test-service"
        assert content["port"] == 8080


class TestBlueprintAgent:
    """Test main BlueprintAgent functionality."""

    @pytest.fixture
    def agent_config(self, tmp_path):
        """Create agent configuration."""
        blueprints_dir = tmp_path / "blueprints"
        blueprints_dir.mkdir()

        # Create test blueprints
        for blueprint_name in ["rest-api", "microservice", "web-app"]:
            blueprint_content = {
                "name": blueprint_name,
                "description": f"Test {blueprint_name} blueprint",
                "version": "1.0.0",
                "variables": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service",
                        "required": True,
                    }
                },
                "structure": {"directories": ["src", "tests"]},
                "files": [
                    {
                        "path": "README.md",
                        "template": "# {{ service_name }}\n\nA {{ service_name }} service.",
                    }
                ],
            }

            blueprint_file = blueprints_dir / f"{blueprint_name}.yaml"
            blueprint_file.write_text(yaml.dump(blueprint_content))

        return {"blueprints_dir": str(blueprints_dir)}

    @pytest.fixture
    def agent(self, agent_config):
        """Create BlueprintAgent instance."""
        return BlueprintAgent(agent_config)

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "BlueprintAgent"
        assert agent.catalog is not None
        assert agent.scaffolder is not None

    def test_list_available_blueprints(self, agent):
        """Test listing available blueprints."""
        blueprints = agent.list_available_blueprints()

        assert len(blueprints) >= 3
        blueprint_names = [bp["name"] for bp in blueprints]
        assert "rest-api" in blueprint_names
        assert "microservice" in blueprint_names
        assert "web-app" in blueprint_names

    @pytest.mark.asyncio
    async def test_create_service(self, agent, tmp_path):
        """Test creating a service from blueprint."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        service = await agent.create_service(
            service_type="rest-api",
            service_name="test-service",
            output_dir=output_dir,
            config={"service_name": "test-service"},
        )

        assert service.name == "test-service"
        assert service.blueprint_used == "rest-api"
        assert service.path.exists()
        assert len(service.files_created) > 0

    @pytest.mark.asyncio
    async def test_execute_create_service(self, agent, tmp_path):
        """Test execute method with create_service intent."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        input_data = AgentInput(
            intent="create_service",
            task_id="test-task",
            payload={
                "service_type": "rest-api",
                "service_name": "test-service",
                "output_dir": str(output_dir),
                "config": {"service_name": "test-service"},
            },
        )

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.OK
        assert len(output.artifacts) >= 2

        # Check service artifact
        service_artifact = next((a for a in output.artifacts if a.kind == "service"), None)
        assert service_artifact is not None
        assert service_artifact.metadata["service_name"] == "test-service"

        # Check metrics
        assert "files_generated" in output.metrics
        assert "blueprint_used" in output.metrics
        assert output.metrics["blueprint_used"] == "rest-api"

    @pytest.mark.asyncio
    async def test_execute_list_blueprints(self, agent):
        """Test execute method with list_blueprints intent."""
        input_data = AgentInput(intent="list_blueprints", task_id="test-task", payload={})

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.OK
        assert len(output.artifacts) == 1

        blueprints_artifact = output.artifacts[0]
        assert blueprints_artifact.kind == "blueprints"
        assert len(blueprints_artifact.content) >= 3

        assert "blueprints_count" in output.metrics
        assert output.metrics["blueprints_count"] >= 3

    @pytest.mark.asyncio
    async def test_execute_scaffold_project(self, agent, tmp_path):
        """Test execute method with scaffold_project intent."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        input_data = AgentInput(
            intent="scaffold_project",
            task_id="test-task",
            payload={
                "blueprint_name": "microservice",
                "project_name": "my-microservice",
                "output_dir": str(output_dir),
                "config": {"service_name": "my-microservice"},
            },
        )

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.OK
        assert len(output.artifacts) == 1

        project_artifact = output.artifacts[0]
        assert project_artifact.kind == "project"
        assert project_artifact.metadata["project_name"] == "my-microservice"

    @pytest.mark.asyncio
    async def test_execute_invalid_intent(self, agent):
        """Test execute method with invalid intent."""
        input_data = AgentInput(intent="invalid_intent", task_id="test-task", payload={})

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.FAIL
        assert "Unknown intent" in output.error

    @pytest.mark.asyncio
    async def test_execute_missing_parameters(self, agent):
        """Test execute method with missing required parameters."""
        input_data = AgentInput(
            intent="create_service", task_id="test-task", payload={}  # Missing required parameters
        )

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.FAIL
        assert "required" in output.error.lower()

    @pytest.mark.asyncio
    async def test_validate_success(self, agent, tmp_path):
        """Test validate method with successful output."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create a successful output
        input_data = AgentInput(
            intent="create_service",
            task_id="test-task",
            payload={
                "service_type": "rest-api",
                "service_name": "test-service",
                "output_dir": str(output_dir),
                "config": {"service_name": "test-service"},
            },
        )

        output = await agent.execute(input_data)
        is_valid = await agent.validate(output)

        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_failure(self, agent):
        """Test validate method with failed output."""
        failed_output = AgentOutput(
            task_id="test-task",
            status=AgentStatus.FAIL,
            error="Test error",
            artifacts=[],
            metrics={},
        )

        is_valid = await agent.validate(failed_output)
        assert is_valid is False

    def test_get_capabilities(self, agent):
        """Test get_capabilities method."""
        capabilities = agent.get_capabilities()

        assert capabilities["name"] == "BlueprintAgent"
        assert capabilities["version"] == "1.0.0"
        assert "description" in capabilities

        # Check intents
        expected_intents = ["create_service", "list_blueprints", "scaffold_project"]
        assert all(intent in capabilities["intents"] for intent in expected_intents)

        # Check inputs and outputs
        assert "inputs" in capabilities
        assert "outputs" in capabilities
        assert "features" in capabilities

        # Check supported blueprints
        assert "supported_blueprints" in capabilities
        assert len(capabilities["supported_blueprints"]) >= 3


class TestGeneratedService:
    """Test GeneratedService dataclass."""

    def test_generated_service_creation(self, tmp_path):
        """Test creating GeneratedService instance."""
        service_path = tmp_path / "my-service"
        service_path.mkdir()

        service = GeneratedService(
            name="my-service",
            path=service_path,
            blueprint_used="rest-api",
            files_created=["src/main.py", "package.json"],
            variables_used={"service_name": "my-service", "port": 3000},
        )

        assert service.name == "my-service"
        assert service.path == service_path
        assert service.blueprint_used == "rest-api"
        assert len(service.files_created) == 2
        assert service.variables_used["service_name"] == "my-service"


class TestBlueprintIntegration:
    """Integration tests for blueprint system."""

    @pytest.mark.asyncio
    async def test_end_to_end_service_generation(self, tmp_path):
        """Test complete service generation flow."""
        # Setup
        blueprints_dir = tmp_path / "blueprints"
        blueprints_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create a comprehensive blueprint
        blueprint_content = {
            "name": "full-stack-app",
            "description": "Full stack web application",
            "version": "1.0.0",
            "variables": {
                "service_name": {
                    "type": "string",
                    "description": "Name of the service",
                    "required": True,
                },
                "database_type": {
                    "type": "string",
                    "description": "Database type",
                    "default": "postgres",
                    "options": ["postgres", "mysql", "mongodb"],
                },
                "port": {"type": "integer", "description": "Service port", "default": 3000},
            },
            "structure": {
                "directories": [
                    "src",
                    "src/controllers",
                    "src/models",
                    "src/routes",
                    "tests",
                    "tests/unit",
                    "tests/integration",
                    "config",
                    "docs",
                ]
            },
            "files": [
                {
                    "path": "package.json",
                    "template": json.dumps(
                        {
                            "name": "{{ service_name }}",
                            "version": "1.0.0",
                            "description": "{{ service_name }} application",
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
const PORT = process.env.PORT || {{ port }};

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: '{{ service_name }}' });
});

app.listen(PORT, () => {
  console.log('{{ service_name }} running on port ' + PORT);
});""",
                },
                {
                    "path": "config/database.js",
                    "condition": "database_type != 'none'",
                    "template": """module.exports = {
  development: {
    type: '{{ database_type }}',
    host: 'localhost',
    database: '{{ service_name }}_dev'
  }
};""",
                },
                {
                    "path": "README.md",
                    "template": """# {{ service_name }}

A full-stack web application.

## Features
- Express.js server
{% if database_type != 'none' %}- {{ database_type|title }} database{% endif %}
- Health check endpoint

## Getting Started

```bash
npm install
npm start
```

Server will run on port {{ port }}.
""",
                },
            ],
            "ci_cd": {
                "github_actions": [
                    {
                        "name": "CI Pipeline",
                        "path": ".github/workflows/ci.yml",
                        "template": """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test""",
                    }
                ]
            },
        }

        blueprint_file = blueprints_dir / "full-stack-app.yaml"
        blueprint_file.write_text(yaml.dump(blueprint_content))

        # Initialize agent
        config = {"blueprints_dir": str(blueprints_dir)}
        agent = BlueprintAgent(config)

        # Generate service
        service = await agent.create_service(
            service_type="full-stack-app",
            service_name="my-awesome-app",
            output_dir=output_dir,
            config={"service_name": "my-awesome-app", "database_type": "postgres", "port": 8080},
        )

        # Verify results
        assert service.name == "my-awesome-app"
        assert service.blueprint_used == "full-stack-app"
        assert service.path.exists()

        # Check directory structure
        project_path = service.path
        assert (project_path / "src").is_dir()
        assert (project_path / "src" / "controllers").is_dir()
        assert (project_path / "tests" / "unit").is_dir()
        assert (project_path / "config").is_dir()

        # Check generated files
        package_json = project_path / "package.json"
        assert package_json.exists()
        package_data = json.loads(package_json.read_text())
        assert package_data["name"] == "my-awesome-app"

        index_js = project_path / "src" / "index.js"
        assert index_js.exists()
        index_content = index_js.read_text()
        assert "my-awesome-app" in index_content
        assert "8080" in index_content

        database_config = project_path / "config" / "database.js"
        assert database_config.exists()
        db_content = database_config.read_text()
        assert "postgres" in db_content
        assert "my-awesome-app_dev" in db_content

        readme = project_path / "README.md"
        assert readme.exists()
        readme_content = readme.read_text()
        assert "my-awesome-app" in readme_content
        assert "Postgres database" in readme_content
        assert "port 8080" in readme_content

        # Check CI/CD files
        ci_file = project_path / ".github" / "workflows" / "ci.yml"
        assert ci_file.exists()
        ci_content = ci_file.read_text()
        assert "npm test" in ci_content

        # Verify all expected files were created
        expected_files = [
            "package.json",
            "src/index.js",
            "config/database.js",
            "README.md",
            ".github/workflows/ci.yml",
        ]
        for expected_file in expected_files:
            assert any(expected_file in created_file for created_file in service.files_created)
