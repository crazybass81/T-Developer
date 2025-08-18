"""AI-Powered Blueprint Agent - Intelligent service generation.

Phase 5: P5-T2 - Enhanced Blueprint Agent
Creates complete service structure using AI with template fallback.
"""

from __future__ import annotations

import ast
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import aiohttp
import yaml
from jinja2 import Environment
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.core.shared_context import SharedContextStore
from backend.packages.learning.memory_curator import MemoryCurator

from ..base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent

logger = logging.getLogger("agents.blueprint")


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


class UnifiedAIService:
    """Unified AI service for code generation (shared with RefactorAgent)."""

    def __init__(self, provider: str = "auto", model: Optional[str] = None):
        self.provider = provider
        self.model = model
        self.available_providers = []

        if os.getenv("AWS_ACCESS_KEY_ID"):
            self.available_providers.append("bedrock")
        if os.getenv("OPENAI_API_KEY"):
            self.available_providers.append("openai")
        if os.getenv("ANTHROPIC_API_KEY"):
            self.available_providers.append("anthropic")

    async def generate_code(self, context: dict, instruction: str) -> Optional[str]:
        """Generate code using AI."""
        prompt = self._build_prompt(context, instruction)

        if self.provider == "auto":
            if "anthropic" in self.available_providers:
                return await self._use_anthropic(prompt)
            elif "openai" in self.available_providers:
                return await self._use_openai(prompt)
            elif "bedrock" in self.available_providers:
                return await self._use_bedrock(prompt)

        return None

    def _build_prompt(self, context: dict, instruction: str) -> str:
        """Build generation prompt."""
        prompt = f"{instruction}\n\n"

        if "requirements" in context:
            prompt += f"Requirements:\n{context['requirements']}\n\n"

        if "architecture" in context:
            prompt += f"Architecture:\n{json.dumps(context['architecture'], indent=2)}\n\n"

        if "examples" in context:
            prompt += f"Examples:\n{context['examples']}\n\n"

        prompt += "Generate only the code without explanations."
        return prompt

    async def _use_anthropic(self, prompt: str) -> Optional[str]:
        """Use Anthropic API."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                }

                payload = {
                    "model": self.model or "claude-3-sonnet-20240229",
                    "max_tokens": 4000,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                }

                async with session.post(
                    "https://api.anthropic.com/v1/messages", json=payload, headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["content"][0]["text"]

        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            return None

    async def _use_openai(self, prompt: str) -> Optional[str]:
        """Use OpenAI API."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

                payload = {
                    "model": self.model or "gpt-4",
                    "messages": [
                        {"role": "system", "content": "You are an expert code generator."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                }

                async with session.post(
                    "https://api.openai.com/v1/chat/completions", json=payload, headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return None

    async def _use_bedrock(self, prompt: str) -> Optional[str]:
        """Use AWS Bedrock."""
        try:
            import boto3

            bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

            body = json.dumps(
                {
                    "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                    "max_tokens_to_sample": 4000,
                    "temperature": 0.2,
                }
            )

            response = bedrock.invoke_model(
                body=body,
                modelId=self.model or "anthropic.claude-v2",
                accept="application/json",
                contentType="application/json",
            )

            result = json.loads(response["body"].read())
            return result.get("completion")

        except Exception as e:
            logger.error(f"Bedrock error: {e}")
            return None


class RAGContextRetriever:
    """Retrieval-Augmented Generation context retriever."""

    def __init__(self, context_store: SharedContextStore, memory_curator: MemoryCurator):
        self.context_store = context_store
        self.memory_curator = memory_curator
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.code_embeddings = {}

    async def retrieve_relevant_context(
        self, query: str, context_type: str = "all", top_k: int = 5
    ) -> dict[str, Any]:
        """Retrieve relevant context using RAG."""
        relevant_context = {
            "existing_code": [],
            "patterns": [],
            "plans": [],
            "similar_implementations": [],
            "constraints": [],
        }

        # Get evolution context
        evolution_context = await self.context_store.get_current_context()

        if evolution_context:
            # Retrieve plan details
            if evolution_context.improvement_plan:
                relevant_context["plans"] = evolution_context.improvement_plan
                relevant_context["objectives"] = evolution_context.objectives

            # Retrieve learned patterns
            if evolution_context.patterns_learned:
                relevant_context["patterns"] = evolution_context.patterns_learned

            # Get implementation constraints
            relevant_context["constraints"] = evolution_context.focus_areas

        # Retrieve from memory curator
        memories = await self.memory_curator.recall(
            query=query, relevance_threshold=0.7, max_results=top_k
        )

        for memory in memories:
            if memory.get("type") == "pattern":
                relevant_context["patterns"].append(memory)
            elif memory.get("type") == "implementation":
                relevant_context["similar_implementations"].append(memory)

        return relevant_context

    async def find_similar_code(
        self, description: str, codebase_path: Path, threshold: float = 0.6
    ) -> list[dict[str, Any]]:
        """Find similar existing code to prevent duplication."""
        similar_code = []

        # Scan codebase
        for py_file in codebase_path.rglob("*.py"):
            try:
                with open(py_file) as f:
                    content = f.read()

                # Parse AST to understand code structure
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        # Get docstring
                        docstring = ast.get_docstring(node) or ""

                        # Calculate similarity
                        if (
                            docstring
                            and self._calculate_similarity(description, docstring) > threshold
                        ):
                            similar_code.append(
                                {
                                    "file": str(py_file),
                                    "name": node.name,
                                    "type": type(node).__name__,
                                    "docstring": docstring,
                                    "line": node.lineno,
                                }
                            )
            except Exception as e:
                logger.debug(f"Error parsing {py_file}: {e}")

        return similar_code

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using TF-IDF."""
        try:
            tfidf = TfidfVectorizer().fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0


class ClaudeCodeExecutor:
    """Execute code generation using Claude Code CLI."""

    def __init__(self, claude_path: str = "claude"):
        self.claude_path = claude_path
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Claude Code is available."""
        try:
            import subprocess

            result = subprocess.run([self.claude_path, "--version"], capture_output=True, timeout=2)
            return result.returncode == 0
        except:
            return False

    async def generate_with_context(
        self, task: str, context: dict[str, Any], files: list[str] = None, output_dir: Path = None
    ) -> dict[str, Any]:
        """Generate code using Claude Code with full context."""

        if not self.available:
            return {"success": False, "error": "Claude Code not available"}

        try:
            import subprocess
            import tempfile

            # Prepare context file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(context, f)
                context_file = f.name

            # Build Claude Code command
            cmd = [self.claude_path]

            # Add task
            cmd.extend(["--task", task])

            # Add context
            cmd.extend(["--context-file", context_file])

            # Add files to analyze
            if files:
                for file in files:
                    cmd.extend(["--analyze", file])

            # Add output directory
            if output_dir:
                cmd.extend(["--output", str(output_dir)])

            # Execute Claude Code
            logger.info(f"Executing Claude Code: {' '.join(cmd[:3])}...")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Clean up context file
            Path(context_file).unlink()

            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except:
                    return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            logger.error(f"Claude Code execution failed: {e}")
            return {"success": False, "error": str(e)}


class ContextAwareCodeGenerator:
    """Context-aware AI code generator with Claude Code and RAG."""

    def __init__(
        self,
        ai_service: UnifiedAIService,
        context_retriever: RAGContextRetriever,
        template_catalog: Optional[BlueprintCatalog] = None,
        use_claude_code: bool = True,
    ):
        self.ai_service = ai_service
        self.context_retriever = context_retriever
        self.template_catalog = template_catalog
        self.context_store = SharedContextStore()

        # Initialize Claude Code executor
        self.use_claude_code = use_claude_code
        self.claude_executor = ClaudeCodeExecutor() if use_claude_code else None

    async def generate_from_plan(
        self, plan: dict[str, Any], service_name: str, output_dir: Path
    ) -> GeneratedService:
        """Generate service strictly following the plan using Claude Code."""

        # Retrieve all relevant context
        context = await self.context_retriever.retrieve_relevant_context(
            query=json.dumps(plan), context_type="all"
        )

        # Check for existing similar code
        existing_code = await self.context_retriever.find_similar_code(
            description=plan.get("description", ""), codebase_path=output_dir.parent
        )

        if existing_code:
            logger.warning(f"Found {len(existing_code)} similar existing implementations")
            context["existing_code"] = existing_code

        # Create service directory
        service_dir = output_dir / service_name
        service_dir.mkdir(parents=True, exist_ok=True)

        # Try Claude Code first if available
        if self.claude_executor and self.claude_executor.available:
            logger.info("Using Claude Code for context-aware generation")

            # Prepare comprehensive task for Claude Code
            task = f"""
            Generate a complete service implementation based on this plan:

            Service: {service_name}
            Plan: {json.dumps(plan, indent=2)}

            Context:
            - Existing similar code: {len(existing_code)} items found
            - Patterns to apply: {len(context.get('patterns', []))} patterns
            - Constraints: {context.get('constraints', [])}

            Requirements:
            1. Follow the plan EXACTLY - implement all specified components
            2. DO NOT duplicate existing code - reuse or adapt instead
            3. Apply learned patterns from context
            4. Generate comprehensive tests for each component
            5. Include proper error handling and logging
            6. Add documentation and type hints

            Output a complete, production-ready implementation.
            """

            # Execute Claude Code with full context
            result = await self.claude_executor.generate_with_context(
                task=task,
                context={
                    "plan": plan,
                    "existing_code": existing_code,
                    "patterns": context.get("patterns", []),
                    "objectives": context.get("objectives", []),
                    "constraints": context.get("constraints", []),
                },
                files=[item["file"] for item in existing_code[:5]] if existing_code else None,
                output_dir=service_dir,
            )

            if result.get("success"):
                # Get list of created files
                files_created = []
                for root, dirs, files in os.walk(service_dir):
                    for file in files:
                        file_path = Path(root) / file
                        rel_path = file_path.relative_to(service_dir)
                        files_created.append(str(rel_path))

                logger.info(f"Claude Code generated {len(files_created)} files")

                # Store implementation log
                await self.context_store.store_implementation_log(
                    modified_files=files_created,
                    changes=[{"type": "created", "file": f} for f in files_created],
                    rollback_points=[],
                    evolution_id=context.get("evolution_id"),
                )

                return GeneratedService(
                    name=service_name,
                    path=service_dir,
                    files_created=files_created,
                    blueprint_used="claude-code-context-aware",
                    variables_used={"plan": plan, "context": context},
                )
            else:
                logger.warning(f"Claude Code failed: {result.get('error')}")

        # Fallback to AI-based generation
        logger.info("Using AI service for generation (Claude Code unavailable)")

        # Generate architecture based on plan
        architecture = await self._generate_architecture_from_plan(plan, context)

        # Generate structure following plan specifications
        structure = await self._generate_structure_from_plan(plan, architecture, context)

        # Generate each component according to plan
        files_created = []
        for component in plan.get("components", []):
            files = await self._generate_component(
                component=component,
                architecture=architecture,
                context=context,
                service_dir=service_dir,
            )
            files_created.extend(files)

        # Store implementation log
        await self.context_store.store_implementation_log(
            modified_files=files_created,
            changes=[{"type": "created", "file": f} for f in files_created],
            rollback_points=[],
            evolution_id=context.get("evolution_id"),
        )

        return GeneratedService(
            name=service_name,
            path=service_dir,
            files_created=files_created,
            blueprint_used="context-aware-ai",
            variables_used={"plan": plan, "context": context},
        )

    async def _generate_architecture_from_plan(
        self, plan: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate architecture strictly from plan."""

        prompt = f"""
        Generate architecture based on this plan:
        {json.dumps(plan, indent=2)}

        Context from previous implementations:
        {json.dumps(context.get('patterns', []), indent=2)}

        Existing similar code (DO NOT DUPLICATE):
        {json.dumps(context.get('existing_code', []), indent=2)}

        Requirements:
        1. Follow the plan exactly
        2. Reuse existing code where possible
        3. Apply learned patterns
        4. Ensure no duplication

        Return JSON with architecture details.
        """

        result = await self.ai_service.generate_code(
            context={"task": "architecture_from_plan"}, instruction=prompt
        )

        try:
            return json.loads(result) if result else self._default_architecture_from_plan(plan)
        except:
            return self._default_architecture_from_plan(plan)

    def _default_architecture_from_plan(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Generate default architecture from plan."""
        return {
            "tech_stack": plan.get("tech_stack", ["python", "fastapi"]),
            "patterns": plan.get("patterns", ["repository", "service"]),
            "components": plan.get("components", []),
            "constraints": plan.get("constraints", []),
            "reuse": plan.get("reuse_components", []),
        }

    async def _generate_structure_from_plan(
        self, plan: dict[str, Any], architecture: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate project structure from plan."""

        structure = {"directories": [], "files": []}

        # Extract structure from plan
        if "structure" in plan:
            structure = plan["structure"]
        else:
            # Generate based on components
            for component in plan.get("components", []):
                comp_type = component.get("type", "module")
                comp_name = component.get("name", "unknown")

                if comp_type == "service":
                    structure["directories"].extend(
                        [f"src/services/{comp_name}", f"tests/services/{comp_name}"]
                    )
                elif comp_type == "api":
                    structure["directories"].extend(
                        [f"src/api/{comp_name}", f"tests/api/{comp_name}"]
                    )

        return structure

    async def _generate_component(
        self,
        component: dict[str, Any],
        architecture: dict[str, Any],
        context: dict[str, Any],
        service_dir: Path,
    ) -> list[str]:
        """Generate a single component according to plan."""

        files_created = []
        comp_name = component.get("name", "component")
        comp_type = component.get("type", "module")
        comp_specs = component.get("specifications", {})

        # Check if similar component exists
        existing = context.get("existing_code", [])
        reusable = None

        for existing_item in existing:
            if existing_item.get("name") == comp_name:
                reusable = existing_item
                logger.info(f"Found reusable component: {comp_name} in {existing_item['file']}")
                break

        if reusable:
            # Adapt existing code
            code = await self._adapt_existing_code(reusable, comp_specs)
        else:
            # Generate new code
            code = await self._generate_new_component(component, architecture, context)

        # Determine file path
        file_path = self._get_component_path(comp_type, comp_name, service_dir)

        # Write code
        if code:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(code)
            files_created.append(str(file_path.relative_to(service_dir)))

            # Generate tests
            test_code = await self._generate_component_tests(component, code)
            if test_code:
                test_path = self._get_test_path(comp_type, comp_name, service_dir)
                test_path.parent.mkdir(parents=True, exist_ok=True)
                test_path.write_text(test_code)
                files_created.append(str(test_path.relative_to(service_dir)))

        return files_created

    async def _adapt_existing_code(
        self, existing: dict[str, Any], specifications: dict[str, Any]
    ) -> str:
        """Adapt existing code to new specifications."""

        prompt = f"""
        Adapt this existing code to meet new specifications:

        Existing: {existing['file']}:{existing['line']}
        Type: {existing['type']}
        Current purpose: {existing['docstring']}

        New specifications:
        {json.dumps(specifications, indent=2)}

        Generate adapted code that:
        1. Maintains compatibility
        2. Meets new requirements
        3. Follows existing patterns
        """

        return await self.ai_service.generate_code(
            context={"task": "adapt_code"}, instruction=prompt
        )

    async def _generate_new_component(
        self, component: dict[str, Any], architecture: dict[str, Any], context: dict[str, Any]
    ) -> str:
        """Generate new component code."""

        prompt = f"""
        Generate {component['type']} component:

        Component specification:
        {json.dumps(component, indent=2)}

        Architecture:
        {json.dumps(architecture, indent=2)}

        Apply these patterns:
        {json.dumps(context.get('patterns', []), indent=2)}

        Follow these constraints:
        {json.dumps(context.get('constraints', []), indent=2)}

        Generate production-ready code.
        """

        return await self.ai_service.generate_code(
            context={"component": component}, instruction=prompt
        )

    async def _generate_component_tests(self, component: dict[str, Any], code: str) -> str:
        """Generate tests for component."""

        prompt = f"""
        Generate comprehensive tests for this component:

        Component: {component['name']}
        Type: {component['type']}

        Code to test:
        {code[:1000]}  # First 1000 chars

        Generate pytest tests with:
        1. Unit tests
        2. Integration tests
        3. Edge cases
        4. Error handling
        """

        return await self.ai_service.generate_code(
            context={"task": "test_generation"}, instruction=prompt
        )

    def _get_component_path(self, comp_type: str, comp_name: str, service_dir: Path) -> Path:
        """Get file path for component."""

        path_map = {
            "service": f"src/services/{comp_name}.py",
            "api": f"src/api/{comp_name}.py",
            "model": f"src/models/{comp_name}.py",
            "repository": f"src/repositories/{comp_name}.py",
            "controller": f"src/controllers/{comp_name}.py",
            "util": f"src/utils/{comp_name}.py",
        }

        rel_path = path_map.get(comp_type, f"src/{comp_name}.py")
        return service_dir / rel_path

    def _get_test_path(self, comp_type: str, comp_name: str, service_dir: Path) -> Path:
        """Get test file path for component."""

        path_map = {
            "service": f"tests/services/test_{comp_name}.py",
            "api": f"tests/api/test_{comp_name}.py",
            "model": f"tests/models/test_{comp_name}.py",
            "repository": f"tests/repositories/test_{comp_name}.py",
            "controller": f"tests/controllers/test_{comp_name}.py",
            "util": f"tests/utils/test_{comp_name}.py",
        }

        rel_path = path_map.get(comp_type, f"tests/test_{comp_name}.py")
        return service_dir / rel_path


class AICodeGenerator:
    """AI-powered code generator."""

    def __init__(
        self, ai_service: UnifiedAIService, template_catalog: Optional[BlueprintCatalog] = None
    ):
        self.ai_service = ai_service
        self.template_catalog = template_catalog

    async def generate_from_requirements(
        self, requirements: str, service_name: str, service_type: str, output_dir: Path
    ) -> GeneratedService:
        """Generate complete service from requirements using AI."""

        # Step 1: Analyze requirements and determine architecture
        architecture = await self._analyze_requirements(requirements, service_type)

        # Step 2: Generate project structure
        structure = await self._generate_structure(architecture, service_name)

        # Step 3: Create directories
        service_dir = output_dir / service_name
        await self._create_directories(service_dir, structure)

        # Step 4: Generate each file
        files_created = []
        for file_spec in structure["files"]:
            file_path = service_dir / file_spec["path"]

            # Get examples from templates if available
            examples = (
                self._get_template_examples(file_spec["type"]) if self.template_catalog else None
            )

            # Generate code with AI
            code = await self.ai_service.generate_code(
                context={
                    "requirements": requirements,
                    "architecture": architecture,
                    "file_type": file_spec["type"],
                    "file_purpose": file_spec["purpose"],
                    "examples": examples,
                    "service_name": service_name,
                },
                instruction=f"Generate {file_spec['type']} for {file_spec['purpose']}",
            )

            if code:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(code)
                files_created.append(str(file_path.relative_to(service_dir)))
            else:
                # Fallback to template if AI fails
                if self.template_catalog:
                    code = self._generate_from_template(file_spec, service_name)
                    if code:
                        file_path.write_text(code)
                        files_created.append(str(file_path.relative_to(service_dir)))

        # Step 5: Generate tests
        test_files = await self._generate_tests(service_dir, architecture, files_created)
        files_created.extend(test_files)

        # Step 6: Generate documentation
        doc_files = await self._generate_documentation(service_dir, requirements, architecture)
        files_created.extend(doc_files)

        return GeneratedService(
            name=service_name,
            path=service_dir,
            files_created=files_created,
            blueprint_used="ai-generated",
            variables_used={"requirements": requirements, "architecture": architecture},
        )

    async def _analyze_requirements(self, requirements: str, service_type: str) -> dict:
        """Analyze requirements to determine architecture."""

        analysis_prompt = f"""
        Analyze these requirements and determine the best architecture:

        Requirements: {requirements}
        Service Type: {service_type}

        Return a JSON object with:
        - tech_stack: list of technologies
        - patterns: list of design patterns
        - components: list of main components
        - database: database type if needed
        - external_services: list of external services
        """

        result = await self.ai_service.generate_code(
            context={"task": "architecture_analysis"}, instruction=analysis_prompt
        )

        try:
            return json.loads(result) if result else self._default_architecture(service_type)
        except:
            return self._default_architecture(service_type)

    def _default_architecture(self, service_type: str) -> dict:
        """Default architecture fallback."""
        architectures = {
            "api": {
                "tech_stack": ["fastapi", "postgresql", "redis"],
                "patterns": ["repository", "service", "controller"],
                "components": ["auth", "database", "cache"],
                "database": "postgresql",
                "external_services": [],
            },
            "microservice": {
                "tech_stack": ["fastapi", "rabbitmq", "mongodb"],
                "patterns": ["event-driven", "saga"],
                "components": ["message_broker", "service_registry"],
                "database": "mongodb",
                "external_services": ["service_discovery"],
            },
            "web": {
                "tech_stack": ["react", "typescript", "tailwind"],
                "patterns": ["mvc", "component-based"],
                "components": ["router", "state_management", "api_client"],
                "database": None,
                "external_services": ["api_backend"],
            },
        }
        return architectures.get(service_type, architectures["api"])

    async def _generate_structure(self, architecture: dict, service_name: str) -> dict:
        """Generate project structure based on architecture."""

        structure_prompt = f"""
        Generate project structure for:
        Architecture: {json.dumps(architecture)}
        Service Name: {service_name}

        Return JSON with:
        - directories: list of directory paths
        - files: list of file specs with path, type, and purpose
        """

        result = await self.ai_service.generate_code(
            context={"task": "structure_generation"}, instruction=structure_prompt
        )

        try:
            return json.loads(result) if result else self._default_structure(architecture)
        except:
            return self._default_structure(architecture)

    def _default_structure(self, architecture: dict) -> dict:
        """Default structure fallback."""
        return {
            "directories": [
                "src",
                "src/models",
                "src/services",
                "src/controllers",
                "tests",
                "config",
                "scripts",
            ],
            "files": [
                {"path": "src/main.py", "type": "main", "purpose": "application entry point"},
                {"path": "src/config.py", "type": "config", "purpose": "configuration management"},
                {
                    "path": "requirements.txt",
                    "type": "dependencies",
                    "purpose": "python dependencies",
                },
                {"path": "Dockerfile", "type": "docker", "purpose": "container definition"},
                {
                    "path": "docker-compose.yml",
                    "type": "docker-compose",
                    "purpose": "local development",
                },
                {"path": ".env.example", "type": "env", "purpose": "environment variables example"},
            ],
        }

    async def _create_directories(self, base_dir: Path, structure: dict):
        """Create directory structure."""
        for directory in structure.get("directories", []):
            (base_dir / directory).mkdir(parents=True, exist_ok=True)

    def _get_template_examples(self, file_type: str) -> Optional[str]:
        """Get template examples for file type."""
        if not self.template_catalog:
            return None

        # Get example from existing templates
        for blueprint in self.template_catalog.blueprints.values():
            for file in blueprint.files:
                if file_type in file.path:
                    return file.template
        return None

    def _generate_from_template(self, file_spec: dict, service_name: str) -> Optional[str]:
        """Fallback to template generation."""
        # Simple template fallback
        templates = {
            "main": f"""from fastapi import FastAPI\n\napp = FastAPI(title="{service_name}")\n\n@app.get("/health")\ndef health_check():\n    return {{"status": "healthy"}}""",
            "config": """import os\nfrom pydantic import BaseSettings\n\nclass Settings(BaseSettings):\n    app_name: str = "service"\n    debug: bool = False\n\nsettings = Settings()""",
            "dependencies": """fastapi\nuvicorn\npydantic\npytest""",
            "docker": """FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]""",
        }
        return templates.get(file_spec["type"])

    async def _generate_tests(self, service_dir: Path, architecture: dict, files: list) -> list:
        """Generate test files."""
        test_files = []

        for file in files:
            if file.endswith(".py") and "test" not in file:
                test_file = f"tests/test_{Path(file).stem}.py"
                test_path = service_dir / test_file

                test_code = await self.ai_service.generate_code(
                    context={"file_to_test": file, "architecture": architecture},
                    instruction=f"Generate comprehensive pytest tests for {file}",
                )

                if test_code:
                    test_path.parent.mkdir(parents=True, exist_ok=True)
                    test_path.write_text(test_code)
                    test_files.append(test_file)

        return test_files

    async def _generate_documentation(
        self, service_dir: Path, requirements: str, architecture: dict
    ) -> list:
        """Generate documentation files."""
        doc_files = []

        # Generate README
        readme_content = await self.ai_service.generate_code(
            context={"requirements": requirements, "architecture": architecture},
            instruction="Generate comprehensive README.md with setup instructions",
        )

        if readme_content:
            (service_dir / "README.md").write_text(readme_content)
            doc_files.append("README.md")

        # Generate API documentation
        if "api" in str(architecture):
            api_doc = await self.ai_service.generate_code(
                context={"architecture": architecture},
                instruction="Generate OpenAPI/Swagger documentation",
            )

            if api_doc:
                (service_dir / "openapi.yaml").write_text(api_doc)
                doc_files.append("openapi.yaml")

        return doc_files


class BlueprintAgent(BaseAgent):
    """Main blueprint agent for service generation."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize context-aware AI-powered blueprint agent."""
        super().__init__("BlueprintAgent", config)

        # Initialize AI service
        ai_provider = config.get("ai_provider", "auto") if config else "auto"
        self.ai_service = UnifiedAIService(provider=ai_provider)

        # Initialize context systems
        self.context_store = SharedContextStore()
        self.memory_curator = MemoryCurator()

        # Initialize RAG context retriever
        self.context_retriever = RAGContextRetriever(
            context_store=self.context_store, memory_curator=self.memory_curator
        )

        # Keep template catalog as fallback
        blueprints_dir = (
            Path(config.get("blueprints_dir", "blueprints")) if config else Path("blueprints")
        )
        self.catalog = BlueprintCatalog(blueprints_dir) if blueprints_dir.exists() else None
        self.scaffolder = ProjectScaffolder(self.catalog) if self.catalog else None

        # Initialize context-aware code generator
        self.context_generator = ContextAwareCodeGenerator(
            ai_service=self.ai_service,
            context_retriever=self.context_retriever,
            template_catalog=self.catalog,
        )

        # Keep standard AI generator for backward compatibility
        self.ai_generator = AICodeGenerator(self.ai_service, self.catalog)

        # Configuration flags
        self.use_context_aware = config.get("use_context_aware", True) if config else True
        self.use_ai_generation = config.get("use_ai_generation", True) if config else True
        self.fallback_to_templates = config.get("fallback_to_templates", True) if config else True
        self.strict_plan_mode = config.get("strict_plan_mode", True) if config else True

    async def create_service(
        self,
        service_type: str,
        service_name: str,
        output_dir: Path,
        config: Optional[dict[str, Any]] = None,
    ) -> GeneratedService:
        """Create a new service using context-aware AI, standard AI, or templates."""
        config = config or {}

        # Extract plan and requirements
        plan = config.get("plan")
        requirements = config.get("requirements", "")

        # Priority 1: Context-aware generation with plan
        if self.use_context_aware and plan:
            try:
                logger.info(
                    f"Generating service '{service_name}' using context-aware AI with plan..."
                )

                # Check for duplicate implementations first
                existing = await self.context_retriever.find_similar_code(
                    description=plan.get("description", service_name),
                    codebase_path=output_dir.parent,
                    threshold=0.8,
                )

                if existing and self.strict_plan_mode:
                    logger.warning(f"Found {len(existing)} similar implementations:")
                    for item in existing[:3]:  # Show top 3
                        logger.warning(f"  - {item['file']}:{item['line']} - {item['name']}")

                    # Ask for confirmation or adapt existing
                    if config.get("force_new", False):
                        logger.info("Forcing new implementation despite existing code")
                    else:
                        logger.info("Adapting existing implementation")

                service = await self.context_generator.generate_from_plan(
                    plan=plan, service_name=service_name, output_dir=output_dir
                )

                logger.info(f"Context-aware generation successful for '{service_name}'")

                # Store success pattern
                await self.memory_curator.store(
                    {
                        "type": "generation_success",
                        "service_name": service_name,
                        "plan": plan,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                return service

            except Exception as e:
                logger.warning(f"Context-aware generation failed: {e}")
                if self.strict_plan_mode:
                    raise  # Don't fallback if strict mode

        # Priority 2: Standard AI generation with requirements
        if self.use_ai_generation and requirements:
            try:
                logger.info(f"Generating service '{service_name}' using standard AI...")
                service = await self.ai_generator.generate_from_requirements(
                    requirements=requirements,
                    service_name=service_name,
                    service_type=service_type,
                    output_dir=output_dir,
                )
                logger.info(f"AI generation successful for '{service_name}'")
                return service
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")
                if not self.fallback_to_templates:
                    raise

        # Priority 3: Template-based generation
        if self.scaffolder and self.fallback_to_templates:
            logger.info(f"Falling back to template generation for '{service_name}'")
            blueprint_name = self._select_blueprint(service_type)
            service = await self.scaffolder.scaffold_project(
                blueprint_name=blueprint_name,
                project_name=service_name,
                output_dir=output_dir,
                config=config,
            )
            return service

        # If no generation method available
        raise ValueError(
            "No generation method available (context-aware AI, standard AI, or templates)"
        )

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
            "version": "2.0.0",
            "description": "AI-powered intelligent service generation with template fallback",
            "intents": ["create_service", "list_blueprints", "scaffold_project"],
            "inputs": {
                "create_service": {
                    "service_type": "string",
                    "service_name": "string",
                    "output_dir": "string",
                    "config": "dict (optional)",
                    "requirements": "string (for AI generation)",
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
                "Claude Code CLI integration (PRIMARY)",
                "Context-aware generation with RAG",
                "Plan-driven strict implementation",
                "Duplicate detection and prevention",
                "Pattern learning and application",
                "AI-powered code generation from requirements",
                "Intelligent architecture selection",
                "Automatic test generation",
                "Documentation generation",
                "Template-based fallback",
                "Multiple blueprint support",
                "Configurable variables",
                "Directory structure creation",
                "CI/CD pipeline generation",
                "Git repository initialization",
                "Dependency installation",
            ],
            "claude_code_available": self.context_generator.claude_executor.available
            if hasattr(self, "context_generator")
            else False,
            "ai_providers": self.ai_service.available_providers,
            "ai_enabled": self.use_ai_generation,
            "context_aware_enabled": self.use_context_aware,
            "strict_plan_mode": self.strict_plan_mode,
            "supported_blueprints": self.catalog.list_blueprints() if self.catalog else [],
        }
