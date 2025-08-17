"""Blueprint Agent - Generate service scaffolds from templates.

Phase 5: P5-T2 - Blueprint Agent
Creates complete service structure from blueprint templates.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml
from jinja2 import Environment

from .base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent


@dataclass
class BlueprintVariable:
    """Blueprint template variable."""

    name: str
    type: str
    description: str = ""
    default: Optional[Any] = None
    required: bool = False
    options: list[Any] = field(default_factory=list)


@dataclass
class BlueprintFile:
    """File to be generated from blueprint."""

    path: str
    template: str
    condition: Optional[str] = None
    permissions: str = "644"


@dataclass
class Blueprint:
    """Service blueprint definition."""

    name: str
    description: str
    version: str
    variables: dict[str, BlueprintVariable]
    structure: dict[str, list[str]]
    files: list[BlueprintFile]
    ci_cd: Optional[dict] = None
    deployment: Optional[dict] = None


@dataclass
class GeneratedService:
    """Generated service from blueprint."""

    name: str
    path: Path
    files_created: list[str]
    blueprint_used: str
    variables_used: dict[str, Any]


class BlueprintCatalog:
    """Catalog of available blueprints."""

    def __init__(self, blueprints_dir: Path = Path("blueprints")):
        """Initialize blueprint catalog."""
        self.blueprints_dir = blueprints_dir
        self.blueprints: dict[str, Blueprint] = {}
        self._load_blueprints()

    def _load_blueprints(self):
        """Load all blueprints from directory."""
        if not self.blueprints_dir.exists():
            return

        for blueprint_file in self.blueprints_dir.glob("*.yaml"):
            try:
                with open(blueprint_file) as f:
                    data = yaml.safe_load(f)

                blueprint = self._parse_blueprint(data)
                self.blueprints[blueprint.name] = blueprint
            except Exception as e:
                print(f"Error loading blueprint {blueprint_file}: {e}")

    def _parse_blueprint(self, data: dict) -> Blueprint:
        """Parse blueprint from YAML data."""
        variables = {}
        for var_name, var_data in data.get("variables", {}).items():
            variables[var_name] = BlueprintVariable(
                name=var_name,
                type=var_data.get("type", "string"),
                description=var_data.get("description", ""),
                default=var_data.get("default"),
                required=var_data.get("required", False),
                options=var_data.get("options", []),
            )

        files = []
        for file_data in data.get("files", []):
            files.append(
                BlueprintFile(
                    path=file_data["path"],
                    template=file_data["template"],
                    condition=file_data.get("condition"),
                    permissions=file_data.get("permissions", "644"),
                )
            )

        return Blueprint(
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            variables=variables,
            structure=data.get("structure", {}),
            files=files,
            ci_cd=data.get("ci_cd"),
            deployment=data.get("deployment"),
        )

    def get_blueprint(self, name: str) -> Optional[Blueprint]:
        """Get blueprint by name."""
        return self.blueprints.get(name)

    def list_blueprints(self) -> list[str]:
        """List available blueprint names."""
        return list(self.blueprints.keys())

    def get_blueprint_info(self, name: str) -> Optional[dict]:
        """Get blueprint information."""
        blueprint = self.get_blueprint(name)
        if not blueprint:
            return None

        return {
            "name": blueprint.name,
            "description": blueprint.description,
            "version": blueprint.version,
            "variables": {
                var.name: {
                    "type": var.type,
                    "description": var.description,
                    "required": var.required,
                    "default": var.default,
                }
                for var in blueprint.variables.values()
            },
        }


class TemplateEngine:
    """Template rendering engine."""

    def __init__(self):
        """Initialize template engine."""
        self.env = Environment(trim_blocks=True, lstrip_blocks=True)

    def render(self, template_str: str, variables: dict[str, Any]) -> str:
        """Render template with variables."""
        template = self.env.from_string(template_str)
        return template.render(**variables)

    def evaluate_condition(self, condition: str, variables: dict[str, Any]) -> bool:
        """Evaluate template condition."""
        if not condition:
            return True

        # Simple condition evaluation
        # In production, use a proper expression evaluator
        try:
            # Replace variables in condition
            for var_name, var_value in variables.items():
                condition = condition.replace(var_name, repr(var_value))
            return eval(condition)
        except:
            return True


class CodeGenerator:
    """Generate code from blueprints."""

    def __init__(self, catalog: BlueprintCatalog):
        """Initialize code generator."""
        self.catalog = catalog
        self.template_engine = TemplateEngine()

    async def generate_service(
        self, blueprint_name: str, service_name: str, output_dir: Path, variables: dict[str, Any]
    ) -> GeneratedService:
        """Generate service from blueprint."""
        blueprint = self.catalog.get_blueprint(blueprint_name)
        if not blueprint:
            raise ValueError(f"Blueprint '{blueprint_name}' not found")

        # Add service name to variables
        variables["service_name"] = service_name

        # Validate required variables
        self._validate_variables(blueprint, variables)

        # Set defaults for missing variables
        for var_name, var_def in blueprint.variables.items():
            if var_name not in variables and var_def.default is not None:
                variables[var_name] = var_def.default

        # Create output directory
        service_dir = output_dir / service_name
        service_dir.mkdir(parents=True, exist_ok=True)

        # Create directory structure
        self._create_structure(service_dir, blueprint.structure)

        # Generate files
        files_created = []
        for file_def in blueprint.files:
            if self.template_engine.evaluate_condition(file_def.condition, variables):
                file_path = service_dir / file_def.path
                file_content = self.template_engine.render(file_def.template, variables)

                # Create parent directory if needed
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Write file
                file_path.write_text(file_content)

                # Set permissions (Unix-like systems)
                if hasattr(os, "chmod"):
                    os.chmod(file_path, int(file_def.permissions, 8))

                files_created.append(str(file_path.relative_to(service_dir)))

        # Generate CI/CD files
        if blueprint.ci_cd:
            ci_files = self._generate_ci_cd(service_dir, blueprint.ci_cd, variables)
            files_created.extend(ci_files)

        # Generate deployment files
        if blueprint.deployment:
            deploy_files = self._generate_deployment(service_dir, blueprint.deployment, variables)
            files_created.extend(deploy_files)

        return GeneratedService(
            name=service_name,
            path=service_dir,
            files_created=files_created,
            blueprint_used=blueprint_name,
            variables_used=variables,
        )

    def _validate_variables(self, blueprint: Blueprint, variables: dict[str, Any]):
        """Validate required variables are provided."""
        missing = []
        for var_name, var_def in blueprint.variables.items():
            if var_def.required and var_name not in variables:
                missing.append(var_name)

        if missing:
            raise ValueError(f"Missing required variables: {', '.join(missing)}")

    def _create_structure(self, base_dir: Path, structure: dict[str, list[str]]):
        """Create directory structure."""
        for dir_type, directories in structure.items():
            if dir_type == "directories":
                for directory in directories:
                    (base_dir / directory).mkdir(parents=True, exist_ok=True)

    def _generate_ci_cd(
        self, service_dir: Path, ci_cd_config: dict, variables: dict[str, Any]
    ) -> list[str]:
        """Generate CI/CD configuration files."""
        files_created = []

        if "github_actions" in ci_cd_config:
            for workflow in ci_cd_config["github_actions"]:
                file_path = service_dir / workflow["path"]
                file_path.parent.mkdir(parents=True, exist_ok=True)

                content = self.template_engine.render(workflow["template"], variables)
                file_path.write_text(content)

                files_created.append(str(file_path.relative_to(service_dir)))

        return files_created

    def _generate_deployment(
        self, service_dir: Path, deployment_config: dict, variables: dict[str, Any]
    ) -> list[str]:
        """Generate deployment configuration files."""
        files_created = []

        for platform, configs in deployment_config.items():
            for config in configs:
                file_path = service_dir / config["path"]
                file_path.parent.mkdir(parents=True, exist_ok=True)

                content = self.template_engine.render(config["template"], variables)
                file_path.write_text(content)

                files_created.append(str(file_path.relative_to(service_dir)))

        return files_created


class ProjectScaffolder:
    """Scaffold complete projects from blueprints."""

    def __init__(self, catalog: BlueprintCatalog):
        """Initialize project scaffolder."""
        self.catalog = catalog
        self.generator = CodeGenerator(catalog)

    async def scaffold_project(
        self, blueprint_name: str, project_name: str, output_dir: Path, config: dict[str, Any]
    ) -> GeneratedService:
        """Scaffold a complete project."""
        # Generate main service
        service = await self.generator.generate_service(
            blueprint_name=blueprint_name,
            service_name=project_name,
            output_dir=output_dir,
            variables=config,
        )

        # Add additional project files
        await self._add_project_files(service.path, config)

        # Initialize git repository
        if config.get("init_git", True):
            await self._init_git(service.path)

        # Install dependencies (optional)
        if config.get("install_deps", False):
            await self._install_dependencies(service.path, blueprint_name)

        return service

    async def _add_project_files(self, project_dir: Path, config: dict[str, Any]):
        """Add additional project files."""
        # Add README
        readme_path = project_dir / "README.md"
        readme_content = f"""# {config.get('service_name', 'Service')}

{config.get('description', 'Service description')}

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Running Locally
```bash
docker-compose up
```

### Running Tests
```bash
npm test  # or pytest
```

## API Documentation

See `/docs` endpoint for API documentation.
"""
        readme_path.write_text(readme_content)

        # Add .gitignore
        gitignore_path = project_dir / ".gitignore"
        gitignore_content = """# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Environment
.env
*.env.local

# IDE
.vscode/
.idea/
*.swp

# Build
dist/
build/
*.egg-info/

# Logs
*.log
logs/

# Coverage
coverage/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
"""
        gitignore_path.write_text(gitignore_content)

    async def _init_git(self, project_dir: Path):
        """Initialize git repository."""
        import subprocess

        try:
            subprocess.run(["git", "init"], cwd=project_dir, check=True)
            subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit from blueprint"],
                cwd=project_dir,
                check=True,
            )
        except Exception as e:
            print(f"Git initialization failed: {e}")

    async def _install_dependencies(self, project_dir: Path, blueprint_name: str):
        """Install project dependencies."""
        import subprocess

        # Detect package manager
        if (project_dir / "package.json").exists():
            subprocess.run(["npm", "install"], cwd=project_dir)
        elif (project_dir / "requirements.txt").exists():
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=project_dir)
        elif (project_dir / "go.mod").exists():
            subprocess.run(["go", "mod", "download"], cwd=project_dir)


class BlueprintAgent(BaseAgent):
    """Main blueprint agent for service generation."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize blueprint agent."""
        super().__init__("BlueprintAgent", config)
        blueprints_dir = (
            Path(config.get("blueprints_dir", "blueprints")) if config else Path("blueprints")
        )
        self.catalog = BlueprintCatalog(blueprints_dir)
        self.scaffolder = ProjectScaffolder(self.catalog)

    async def create_service(
        self,
        service_type: str,
        service_name: str,
        output_dir: Path,
        config: Optional[dict[str, Any]] = None,
    ) -> GeneratedService:
        """Create a new service from blueprint."""
        config = config or {}

        # Select blueprint based on service type
        blueprint_name = self._select_blueprint(service_type)

        # Generate service
        service = await self.scaffolder.scaffold_project(
            blueprint_name=blueprint_name,
            project_name=service_name,
            output_dir=output_dir,
            config=config,
        )

        return service

    def _select_blueprint(self, service_type: str) -> str:
        """Select appropriate blueprint for service type."""
        # Map service types to blueprints
        blueprint_map = {
            "api": "rest-api",
            "rest": "rest-api",
            "microservice": "microservice",
            "web": "web-app",
            "cli": "cli-tool",
            "library": "library",
        }

        return blueprint_map.get(service_type.lower(), "rest-api")

    def list_available_blueprints(self) -> list[dict]:
        """List all available blueprints with info."""
        blueprints = []
        for name in self.catalog.list_blueprints():
            info = self.catalog.get_blueprint_info(name)
            if info:
                blueprints.append(info)
        return blueprints

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Execute blueprint agent task.

        Args:
            input: Agent input containing service generation request

        Returns:
            Agent output with generated service artifacts
        """
        try:
            self.logger.info(f"Processing blueprint task: {input.task_id}")

            intent = input.intent
            payload = input.payload

            if intent == "create_service":
                return await self._create_service(input)
            elif intent == "list_blueprints":
                return await self._list_blueprints(input)
            elif intent == "scaffold_project":
                return await self._scaffold_project(input)
            else:
                return AgentOutput(
                    task_id=input.task_id,
                    status=AgentStatus.FAIL,
                    error=f"Unknown intent: {intent}",
                )

        except Exception as e:
            self.logger.error(f"Blueprint agent failed: {e}")
            return AgentOutput(task_id=input.task_id, status=AgentStatus.FAIL, error=str(e))

    async def _create_service(self, input: AgentInput) -> AgentOutput:
        """Create a new service from blueprint."""
        service_type = input.payload.get("service_type", "")
        service_name = input.payload.get("service_name", "")
        output_dir_str = input.payload.get("output_dir", "")
        config = input.payload.get("config", {})

        if not service_type or not service_name or not output_dir_str:
            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.FAIL,
                error="service_type, service_name, and output_dir are required",
            )

        output_dir = Path(output_dir_str)

        generated_service = await self.create_service(
            service_type=service_type,
            service_name=service_name,
            output_dir=output_dir,
            config=config,
        )

        artifacts = [
            Artifact(
                kind="service",
                ref=str(generated_service.path),
                content=generated_service,
                metadata={
                    "service_name": generated_service.name,
                    "blueprint": generated_service.blueprint_used,
                    "files_count": len(generated_service.files_created),
                },
            ),
            Artifact(
                kind="files",
                ref="generated_files",
                content=generated_service.files_created,
                metadata={"count": len(generated_service.files_created)},
            ),
        ]

        metrics = {
            "files_generated": len(generated_service.files_created),
            "blueprint_used": generated_service.blueprint_used,
            "variables_count": len(generated_service.variables_used),
        }

        return AgentOutput(
            task_id=input.task_id, status=AgentStatus.OK, artifacts=artifacts, metrics=metrics
        )

    async def _list_blueprints(self, input: AgentInput) -> AgentOutput:
        """List available blueprints."""
        blueprints = self.list_available_blueprints()

        artifacts = [
            Artifact(
                kind="blueprints",
                ref="available_blueprints",
                content=blueprints,
                metadata={"count": len(blueprints)},
            )
        ]

        metrics = {
            "blueprints_count": len(blueprints),
            "blueprints_available": [bp["name"] for bp in blueprints],
        }

        return AgentOutput(
            task_id=input.task_id, status=AgentStatus.OK, artifacts=artifacts, metrics=metrics
        )

    async def _scaffold_project(self, input: AgentInput) -> AgentOutput:
        """Scaffold a complete project from blueprint."""
        blueprint_name = input.payload.get("blueprint_name", "")
        project_name = input.payload.get("project_name", "")
        output_dir_str = input.payload.get("output_dir", "")
        config = input.payload.get("config", {})

        if not blueprint_name or not project_name or not output_dir_str:
            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.FAIL,
                error="blueprint_name, project_name, and output_dir are required",
            )

        output_dir = Path(output_dir_str)

        generated_service = await self.scaffolder.scaffold_project(
            blueprint_name=blueprint_name,
            project_name=project_name,
            output_dir=output_dir,
            config=config,
        )

        artifacts = [
            Artifact(
                kind="project",
                ref=str(generated_service.path),
                content=generated_service,
                metadata={
                    "project_name": generated_service.name,
                    "blueprint": generated_service.blueprint_used,
                    "files_count": len(generated_service.files_created),
                },
            )
        ]

        metrics = {
            "files_generated": len(generated_service.files_created),
            "blueprint_used": generated_service.blueprint_used,
            "git_initialized": config.get("init_git", True),
            "dependencies_installed": config.get("install_deps", False),
        }

        return AgentOutput(
            task_id=input.task_id, status=AgentStatus.OK, artifacts=artifacts, metrics=metrics
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

        # Check for required artifacts based on intent
        artifact_kinds = {artifact.kind for artifact in output.artifacts}

        # For most intents, we should have some artifacts
        if not output.artifacts:
            return False

        # Check metrics
        if "files_generated" in output.metrics and output.metrics["files_generated"] < 0:
            return False

        return True

    def get_capabilities(self) -> dict[str, Any]:
        """Return agent capabilities for discovery.

        Returns:
            Dictionary of capabilities
        """
        return {
            "name": "BlueprintAgent",
            "version": "1.0.0",
            "description": "Generates service scaffolds from templates and blueprints",
            "intents": ["create_service", "list_blueprints", "scaffold_project"],
            "inputs": {
                "create_service": {
                    "service_type": "string",
                    "service_name": "string",
                    "output_dir": "string",
                    "config": "dict (optional)",
                },
                "list_blueprints": {},
                "scaffold_project": {
                    "blueprint_name": "string",
                    "project_name": "string",
                    "output_dir": "string",
                    "config": "dict (optional)",
                },
            },
            "outputs": {
                "artifacts": ["service", "project", "files", "blueprints"],
                "metrics": ["files_generated", "blueprint_used", "variables_count"],
            },
            "features": [
                "Template-based code generation",
                "Multiple blueprint support",
                "Configurable variables",
                "Directory structure creation",
                "CI/CD pipeline generation",
                "Git repository initialization",
                "Dependency installation",
            ],
            "supported_blueprints": self.catalog.list_blueprints(),
        }
