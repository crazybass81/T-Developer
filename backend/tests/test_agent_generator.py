"""Tests for Agent Generator - TDD approach."""

from unittest.mock import patch

import pytest
from packages.meta_agents.agent_generator import (
    AgentConfig,
    AgentGenerator,
    AgentTemplate,
    CodeGenerator,
    DependencyManager,
    TemplateLibrary,
)


class TestAgentTemplate:
    """Test agent template data model."""

    def test_template_creation(self):
        """Test creating an agent template."""
        template = AgentTemplate(
            name="APIAgent",
            base_class="BaseAgent",
            imports=["requests", "json"],
            methods=["execute", "validate"],
            dependencies=["base_agent"],
            template_code="class {name}({base_class}): pass",
        )

        assert template.name == "APIAgent"
        assert template.base_class == "BaseAgent"
        assert "requests" in template.imports
        assert "execute" in template.methods
        assert len(template.dependencies) == 1

    def test_template_rendering(self):
        """Test rendering template with variables."""
        template = AgentTemplate(
            name="APIAgent",
            base_class="BaseAgent",
            imports=["requests"],
            methods=["execute"],
            dependencies=[],
            template_code="class {name}({base_class}):\n    def {method}(self): pass",
        )

        rendered = template.render({"method": "execute"})

        assert "class APIAgent(BaseAgent):" in rendered
        assert "def execute(self): pass" in rendered

    def test_template_validation(self):
        """Test template validation."""
        template = AgentTemplate(
            name="APIAgent",
            base_class="BaseAgent",
            imports=[],
            methods=["execute"],
            dependencies=[],
            template_code="class {name}({base_class}): pass",
        )

        assert template.validate() is True

        # Invalid template with no methods
        template.methods = []
        assert template.validate() is False


class TestTemplateLibrary:
    """Test template library management."""

    @pytest.fixture
    def library(self):
        """Create template library."""
        return TemplateLibrary()

    def test_load_builtin_templates(self, library):
        """Test loading built-in templates."""
        templates = library.get_all_templates()

        # Should have common templates
        assert "crud_agent" in templates
        assert "api_agent" in templates
        assert "data_processor" in templates
        assert "validation_agent" in templates

    def test_get_template_by_type(self, library):
        """Test getting template by requirement type."""
        # API requirement should return API agent template
        template = library.get_template_for_requirement("REST API endpoint")
        assert template.name in ["APIAgent", "api_agent", "rest_agent"]

        # Data processing requirement
        template = library.get_template_for_requirement("process CSV files")
        assert template.name in ["DataProcessor", "data_processor", "file_handler"]

        # Database requirement
        template = library.get_template_for_requirement("database CRUD operations")
        assert template.name in ["CRUDAgent", "crud_agent"]

    def test_add_custom_template(self, library):
        """Test adding custom template."""
        custom = AgentTemplate(
            name="CustomAgent",
            base_class="BaseAgent",
            imports=["custom_lib"],
            methods=["custom_method"],
            dependencies=[],
            template_code="class {name}: pass",
        )

        library.add_template(custom)

        assert "CustomAgent" in library.get_all_templates()
        assert library.get_template("CustomAgent") == custom


class TestDependencyManager:
    """Test dependency management."""

    @pytest.fixture
    def manager(self):
        """Create dependency manager."""
        return DependencyManager()

    def test_resolve_dependencies(self, manager):
        """Test resolving agent dependencies."""
        agent_spec = {"name": "DataAgent", "dependencies": ["database", "cache", "validator"]}

        resolved = manager.resolve(agent_spec)

        assert "imports" in resolved
        assert "packages" in resolved
        assert len(resolved["imports"]) >= 3

        # Should include standard dependencies
        assert any("sqlalchemy" in imp for imp in resolved["imports"])
        assert any("redis" in imp for imp in resolved["imports"])

    def test_detect_circular_dependencies(self, manager):
        """Test detecting circular dependencies."""
        agents = {
            "AgentA": {"dependencies": ["AgentB"]},
            "AgentB": {"dependencies": ["AgentC"]},
            "AgentC": {"dependencies": ["AgentA"]},  # Circular!
        }

        with pytest.raises(ValueError, match="Circular dependency"):
            manager.validate_dependencies(agents)

    def test_install_dependencies(self, manager):
        """Test installing required packages."""
        packages = ["requests", "pydantic"]

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            result = manager.install_packages(packages)

            assert result["success"] is True
            assert result["installed"] == packages
            mock_run.assert_called()


class TestCodeGenerator:
    """Test code generation."""

    @pytest.fixture
    def generator(self):
        """Create code generator."""
        return CodeGenerator()

    def test_generate_agent_code(self, generator):
        """Test generating agent code from template."""
        template = AgentTemplate(
            name="TestAgent",
            base_class="BaseAgent",
            imports=["json", "typing"],
            methods=["execute", "validate"],
            dependencies=[],
            template_code="""
class {name}({base_class}):
    def __init__(self):
        super().__init__()

    def execute(self, input):
        return {{"result": "success"}}

    def validate(self, output):
        return True
""",
        )

        code = generator.generate(template, {"name": "TestAgent"})

        assert "class TestAgent(BaseAgent):" in code
        assert "def execute(self, input):" in code
        assert "def validate(self, output):" in code
        assert "import json" in code
        assert "import typing" in code

    def test_generate_with_requirements(self, generator):
        """Test generating code based on requirements."""
        requirements = [
            {
                "type": "FUNCTIONAL",
                "description": "Create user account",
                "acceptance_criteria": ["Validate email", "Hash password"],
            }
        ]

        code = generator.generate_from_requirements(requirements)

        assert "def create_user" in code or "def execute" in code
        assert "validate" in code.lower()
        assert "password" in code.lower()

    def test_add_error_handling(self, generator):
        """Test adding error handling to generated code."""
        code = """
def process_data(data):
    result = data * 2
    return result
"""

        enhanced = generator.add_error_handling(code)

        assert "try:" in enhanced
        assert "except" in enhanced
        assert "logger" in enhanced or "logging" in enhanced


class TestAgentConfig:
    """Test agent configuration."""

    def test_default_config(self):
        """Test default agent configuration."""
        config = AgentConfig()

        assert config.auto_generate is True
        assert config.add_tests is True
        assert config.add_documentation is True
        assert config.validate_code is True
        assert config.max_retries == 3

    def test_custom_config(self):
        """Test custom configuration."""
        config = AgentConfig(auto_generate=False, add_tests=False, max_retries=5)

        assert config.auto_generate is False
        assert config.add_tests is False
        assert config.max_retries == 5


class TestAgentGenerator:
    """Test agent generator."""

    @pytest.fixture
    def generator(self):
        """Create agent generator."""
        config = AgentConfig()
        return AgentGenerator(config)

    @pytest.mark.asyncio
    async def test_generate_agent(self, generator):
        """Test generating a complete agent."""
        requirement = {
            "id": "REQ-001",
            "type": "FUNCTIONAL",
            "description": "User authentication API",
            "acceptance_criteria": ["Validate credentials", "Generate JWT token", "Handle errors"],
        }

        result = await generator.generate_agent(requirement)

        assert "agent_name" in result
        assert "code" in result
        assert "tests" in result
        assert "documentation" in result
        assert result["success"] is True

        # Check generated code
        code = result["code"]
        assert "class" in code
        assert "def execute" in code
        assert "jwt" in code.lower() or "token" in code.lower()

    @pytest.mark.asyncio
    async def test_generate_multiple_agents(self, generator):
        """Test generating multiple agents from requirements."""
        requirements = [
            {"id": "REQ-001", "type": "FUNCTIONAL", "description": "User management"},
            {"id": "REQ-002", "type": "FUNCTIONAL", "description": "Product catalog"},
            {"id": "REQ-003", "type": "NON_FUNCTIONAL", "description": "Caching layer"},
        ]

        results = await generator.generate_agents(requirements)

        assert len(results) == 3
        assert all(r["success"] for r in results)
        assert results[0]["agent_name"] != results[1]["agent_name"]

        # Should generate appropriate agent types
        assert "user" in results[0]["agent_name"].lower()
        assert "product" in results[1]["agent_name"].lower()
        assert "cache" in results[2]["agent_name"].lower()

    @pytest.mark.asyncio
    async def test_validate_generated_code(self, generator):
        """Test validating generated Python code."""
        valid_code = """
class TestAgent:
    def execute(self):
        return {"status": "ok"}
"""

        invalid_code = """
class TestAgent:
    def execute(self)  # Missing colon
        return {"status": "ok"}
"""

        assert await generator.validate_code(valid_code) is True
        assert await generator.validate_code(invalid_code) is False

    @pytest.mark.asyncio
    async def test_generate_tests(self, generator):
        """Test generating tests for agent."""
        agent_code = """
class DataAgent:
    def execute(self, data):
        return {"processed": len(data)}

    def validate(self, output):
        return "processed" in output
"""

        tests = await generator.generate_tests("DataAgent", agent_code)

        assert "import pytest" in tests
        assert "class TestDataAgent" in tests
        assert "def test_execute" in tests
        assert "def test_validate" in tests
        assert "assert" in tests

    @pytest.mark.asyncio
    async def test_generate_documentation(self, generator):
        """Test generating documentation."""
        agent_name = "APIAgent"
        agent_code = """
class APIAgent:
    def execute(self, request):
        '''Process API request.'''
        return {"response": "ok"}
"""

        docs = await generator.generate_documentation(agent_name, agent_code)

        assert f"# {agent_name}" in docs
        assert "## Methods" in docs
        assert "execute" in docs
        assert "Process API request" in docs

    @pytest.mark.asyncio
    async def test_save_agent(self, generator, tmp_path):
        """Test saving generated agent to file."""
        agent_data = {
            "agent_name": "TestAgent",
            "code": "class TestAgent: pass",
            "tests": "def test_agent(): pass",
            "documentation": "# TestAgent",
        }

        output_dir = tmp_path / "agents"
        result = await generator.save_agent(agent_data, output_dir)

        assert result["saved"] is True
        assert (output_dir / "test_agent.py").exists()
        assert (output_dir / "test_test_agent.py").exists()
        assert (output_dir / "test_agent.md").exists()
