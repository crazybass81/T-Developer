"""ServiceBuilder - Main orchestrator for automatic service creation."""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .agent_generator import AgentConfig, AgentGenerator
from .requirement_analyzer import AnalysisConfig, RequirementAnalyzer
from .workflow_composer import WorkflowComposer, WorkflowConfig

logger = logging.getLogger("meta_agents.service_builder")


@dataclass
class ServiceBuilderConfig:
    """Configuration for service builder."""

    enable_ai_analysis: bool = True
    auto_generate_agents: bool = True
    create_workflows: bool = True
    validate_requirements: bool = True
    max_agents_per_service: int = 10
    default_timeout_minutes: int = 60
    output_directory: str = "generated_services"


@dataclass
class ServiceDefinition:
    """Definition of a generated service."""

    name: str
    description: str
    requirements: list[str]
    agents: list[str]
    workflow_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0.0"
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate service definition."""
        if not self.name or not self.name.strip():
            return False
        if not self.description:
            return False
        if not self.requirements:
            return False
        if not self.agents:
            return False
        if not self.workflow_id:
            return False
        return True


class ServiceBuilder:
    """Main orchestrator for automatic service creation using meta agents."""

    def __init__(self, config: Optional[ServiceBuilderConfig] = None):
        """Initialize service builder."""
        self.config = config or ServiceBuilderConfig()

        # Initialize meta agents
        self.requirement_analyzer = RequirementAnalyzer(
            AnalysisConfig(use_ai=self.config.enable_ai_analysis)
        )
        self.agent_generator = AgentGenerator(
            AgentConfig(auto_generate=self.config.auto_generate_agents)
        )
        self.workflow_composer = WorkflowComposer(WorkflowConfig(enable_optimization=True))

    async def build_service(self, service_request: dict[str, Any]) -> dict[str, Any]:
        """Build complete service from high-level requirements.

        Args:
            service_request: Service specification with name, description, requirements

        Returns:
            Service creation result with generated service definition
        """
        service_id = f"service-{uuid.uuid4().hex[:8]}"
        service_name = service_request.get("name", f"Service-{service_id}")

        logger.info(f"Building service: {service_name}")

        try:
            # Phase 1: Analyze Requirements
            logger.info("Phase 1: Analyzing requirements...")
            requirements_text = service_request.get("requirements_text", "")

            requirement_analysis = await self.requirement_analyzer.analyze_requirements(
                requirements_text
            )

            if self.config.validate_requirements:
                if not requirement_analysis.get("requirements"):
                    return {
                        "success": False,
                        "error": "Requirement validation failed: No valid requirements found",
                        "service_id": service_id,
                    }

            # Phase 2: Generate Agents
            logger.info("Phase 2: Generating agents...")
            requirements = requirement_analysis["requirements"]

            if len(requirements) > self.config.max_agents_per_service:
                logger.warning(
                    f"Truncating {len(requirements)} requirements to {self.config.max_agents_per_service}"
                )
                requirements = requirements[: self.config.max_agents_per_service]

            generated_agents = await self.agent_generator.generate_agents(requirements)

            # Check for agent generation failures
            failed_agents = [a for a in generated_agents if not a.get("success")]
            if failed_agents:
                return {
                    "success": False,
                    "error": f"Agent generation failed for {len(failed_agents)} agents",
                    "failed_agents": [a.get("agent_name") for a in failed_agents],
                    "service_id": service_id,
                }

            # Phase 3: Compose Workflow
            logger.info("Phase 3: Composing workflow...")
            workflow_requirements = []
            agent_mapping = {}

            for i, req in enumerate(requirements):
                agent_name = generated_agents[i].get("agent_name", f"Agent{i}")
                agent_mapping[req["id"]] = agent_name

                workflow_req = {
                    "id": req["id"],
                    "description": req["description"],
                    "agents": [agent_name],
                    "depends_on": req.get("depends_on", []),
                }
                workflow_requirements.append(workflow_req)

            workflow = await self.workflow_composer.compose(workflow_requirements)

            # Phase 4: Create Service Definition
            logger.info("Phase 4: Creating service definition...")
            agent_names = [a["agent_name"] for a in generated_agents if a.get("success")]
            requirement_descriptions = [r["description"] for r in requirements]

            service_definition = {
                "id": service_id,
                "name": service_name,
                "description": service_request.get(
                    "description", f"Auto-generated service: {service_name}"
                ),
                "requirements": requirement_descriptions,
                "agents": agent_names,
                "workflow_id": workflow["id"],
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "metadata": {
                    "requirement_analysis": requirement_analysis.get("analysis", {}),
                    "agent_count": len(agent_names),
                    "workflow_steps": len(workflow.get("steps", [])),
                    "generation_method": "ai_assisted"
                    if self.config.enable_ai_analysis
                    else "template_based",
                },
                "agent_code": {
                    a["agent_name"]: a.get("code", "") for a in generated_agents if a.get("success")
                },
                "workflow": workflow,
            }

            # Phase 5: Validate Service
            if not await self.validate_service(service_definition):
                return {
                    "success": False,
                    "error": "Service validation failed",
                    "service_id": service_id,
                }

            logger.info(f"Service {service_name} built successfully")

            return {
                "success": True,
                "service": service_definition,
                "service_id": service_id,
                "agents_generated": len(agent_names),
                "workflow_steps": len(workflow.get("steps", [])),
                "requirements_analyzed": len(requirements),
            }

        except Exception as e:
            logger.error(f"Service building failed: {e}")
            return {
                "success": False,
                "error": f"Service building failed: {e!s}",
                "service_id": service_id,
            }

    async def validate_service(self, service: dict[str, Any]) -> bool:
        """Validate complete service definition."""
        # Check required fields
        required_fields = ["name", "description", "requirements", "agents", "workflow_id"]
        for field in required_fields:
            if not service.get(field):
                logger.error(f"Service validation failed: missing {field}")
                return False

        # Check that service has content
        if not service["requirements"]:
            logger.error("Service validation failed: no requirements")
            return False

        if not service["agents"]:
            logger.error("Service validation failed: no agents")
            return False

        # Validate workflow if present
        if service.get("workflow"):
            if not await self.workflow_composer.validate(service["workflow"]):
                logger.error("Service validation failed: invalid workflow")
                return False

        return True

    async def optimize_service(self, service: dict[str, Any]) -> dict[str, Any]:
        """Optimize service for better performance and resource usage."""
        if service.get("workflow"):
            optimized_workflow = await self.workflow_composer.optimize(service["workflow"])

            # Update service with optimization results
            optimized_service = service.copy()
            optimized_service["workflow"] = optimized_workflow
            optimized_service["optimized"] = True
            optimized_service["optimization_applied_at"] = datetime.now().isoformat()

            return optimized_workflow

        return {"optimized": False, "reason": "No workflow to optimize"}

    async def save_service(self, service: dict[str, Any], output_path: Path) -> dict[str, Any]:
        """Save service to files."""
        service_name = service["name"].lower().replace(" ", "_")
        service_dir = output_path / service_name
        service_dir.mkdir(parents=True, exist_ok=True)

        files_created = []

        try:
            # Save service configuration
            service_config = {k: v for k, v in service.items() if k != "agent_code"}
            config_file = service_dir / "service.json"
            with open(config_file, "w") as f:
                json.dump(service_config, f, indent=2, default=str)
            files_created.append(str(config_file))

            # Save agent code files
            agents_dir = service_dir / "agents"
            agents_dir.mkdir(exist_ok=True)

            for agent_name, code in service.get("agent_code", {}).items():
                agent_file = agents_dir / f"{agent_name.lower()}.py"
                agent_file.write_text(code)
                files_created.append(str(agent_file))

            # Save workflow
            if service.get("workflow"):
                workflow_file = service_dir / "workflow.json"
                await self.workflow_composer.save(service["workflow"], workflow_file)
                files_created.append(str(workflow_file))

            # Generate and save documentation
            docs = await self.generate_documentation(service)
            docs_file = service_dir / "README.md"
            docs_file.write_text(docs)
            files_created.append(str(docs_file))

            return {"success": True, "service_directory": str(service_dir), "files": files_created}

        except Exception as e:
            logger.error(f"Failed to save service: {e}")
            return {"success": False, "error": str(e), "files": files_created}

    async def load_service(self, service_path: Path) -> dict[str, Any]:
        """Load service from files."""
        service_config_file = service_path / "service.json"

        if not service_config_file.exists():
            raise FileNotFoundError(f"Service config not found: {service_config_file}")

        # Load service configuration
        with open(service_config_file) as f:
            service = json.load(f)

        # Load agent code
        agents_dir = service_path / "agents"
        if agents_dir.exists():
            agent_code = {}
            for agent_file in agents_dir.glob("*.py"):
                agent_name = agent_file.stem.title()
                agent_code[agent_name] = agent_file.read_text()
            service["agent_code"] = agent_code

        # Load workflow
        workflow_file = service_path / "workflow.json"
        if workflow_file.exists():
            service["workflow"] = await self.workflow_composer.load(workflow_file)

        return service

    async def generate_documentation(self, service: dict[str, Any]) -> str:
        """Generate comprehensive documentation for the service."""
        docs = f"""# {service['name']}

{service['description']}

## Overview

This service was automatically generated using T-Developer's ServiceBuilder.

**Created:** {service.get('created_at', 'Unknown')}
**Version:** {service.get('version', '1.0.0')}

## Requirements

The service fulfills the following requirements:

"""

        for i, req in enumerate(service.get("requirements", []), 1):
            docs += f"{i}. {req}\n"

        docs += f"""

## Architecture

### Agents ({len(service.get('agents', []))})

"""

        for agent in service.get("agents", []):
            docs += f"- **{agent}**: Handles specific service operations\n"

        workflow = service.get("workflow", {})
        if workflow.get("steps"):
            docs += f"""

### Workflow

The service workflow consists of {len(workflow['steps'])} steps:

"""
            for i, step in enumerate(workflow["steps"], 1):
                step_name = step.get("name", step.get("id", f"Step {i}"))
                agent = step.get("agent", "Unknown")
                docs += f"{i}. **{step_name}** (Agent: {agent})\n"

        metadata = service.get("metadata", {})
        if metadata:
            docs += f"""

## Metrics

- **Agents:** {metadata.get('agent_count', 'Unknown')}
- **Workflow Steps:** {metadata.get('workflow_steps', 'Unknown')}
- **Generation Method:** {metadata.get('generation_method', 'Unknown')}
"""

        docs += """

## Usage

This service can be deployed and executed using the T-Developer platform.

### Quick Start

1. Deploy the agents to your runtime environment
2. Configure the workflow orchestrator
3. Start the service workflow

## Generated Files

- `service.json` - Service configuration
- `agents/` - Agent implementations
- `workflow.json` - Workflow definition
- `README.md` - This documentation

---

*Generated by T-Developer ServiceBuilder*
"""

        return docs

    async def get_metrics(self, service: dict[str, Any]) -> dict[str, Any]:
        """Get service metrics and statistics."""
        workflow = service.get("workflow", {})
        steps = workflow.get("steps", [])

        # Calculate estimated duration
        total_duration = sum(step.get("estimated_duration", 30) for step in steps)

        # Calculate complexity score based on multiple factors
        complexity_factors = [
            len(service.get("agents", [])) * 5,  # Agent complexity
            len(service.get("requirements", [])) * 3,  # Requirement complexity
            len(steps) * 2,  # Workflow complexity
        ]
        complexity_score = sum(complexity_factors)

        return {
            "agent_count": len(service.get("agents", [])),
            "requirement_count": len(service.get("requirements", [])),
            "workflow_steps": len(steps),
            "estimated_duration": total_duration,
            "complexity_score": complexity_score,
            "service_size": "small"
            if complexity_score < 50
            else "medium"
            if complexity_score < 100
            else "large",
            "created_at": service.get("created_at"),
            "version": service.get("version", "1.0.0"),
        }

    def get_capabilities(self) -> dict[str, Any]:
        """Get service builder capabilities."""
        return {
            "name": "ServiceBuilder",
            "version": "1.0.0",
            "description": "Automatic service creation using meta agents",
            "features": [
                "requirement_analysis",
                "agent_generation",
                "workflow_composition",
                "service_validation",
                "service_optimization",
                "documentation_generation",
                "service_persistence",
            ],
            "supported_languages": ["python"],
            "max_agents_per_service": self.config.max_agents_per_service,
            "ai_powered": self.config.enable_ai_analysis,
            "meta_agents": {
                "requirement_analyzer": self.requirement_analyzer.__class__.__name__,
                "agent_generator": self.agent_generator.__class__.__name__,
                "workflow_composer": self.workflow_composer.__class__.__name__,
            },
        }
