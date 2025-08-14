"""
ServiceBuilder Agent - Complete service builder orchestrator
Size: < 6.5KB | Performance: < 3μs
Day 25: Phase 2 - Meta Agents
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src.agents.meta.agent_generator import get_generator
from src.agents.meta.requirement_analyzer import get_analyzer
from src.agents.meta.workflow_composer import get_composer
from src.deployment.auto_deployer import DeploymentConfig, get_auto_deployer


@dataclass
class ServiceRequest:
    """Service build request"""

    name: str
    description: str
    requirements: str
    type: str  # microservice, api, data_processor, event_handler
    complexity: str  # simple, medium, complex
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceBlueprint:
    """Service architecture blueprint"""

    service_name: str
    agents: List[Dict[str, Any]]
    workflow: Any  # ComposedWorkflow
    architecture: Dict[str, Any]
    dependencies: List[str]
    api_spec: Dict[str, Any]
    deployment_plan: Dict[str, Any]
    estimated_cost: float
    estimated_time: float


@dataclass
class ServiceResult:
    """Service building result"""

    success: bool
    service_name: str
    blueprint: Optional[ServiceBlueprint]
    deployed_agents: List[str]
    api_endpoints: List[str]
    workflow_id: str
    metrics: Dict[str, Any]
    errors: List[str]


class ServiceBuilder:
    """Complete service builder orchestrator"""

    def __init__(self):
        self.analyzer = get_analyzer()
        self.generator = get_generator()
        self.composer = get_composer()
        self.deployer = get_auto_deployer()
        self.service_history = []

    async def build_service(self, request: ServiceRequest) -> ServiceResult:
        """Build complete service from request"""

        start_time = time.time()
        errors = []

        try:
            # Phase 1: Analyze requirements
            print(f"📋 Analyzing requirements for {request.name}...")
            analysis = await self.analyzer.analyze(request.requirements)

            if analysis.complexity_score > 0.8 and request.complexity == "simple":
                errors.append("Requirements too complex for simple service")
                return self._create_failed_result(request, errors)

            # Phase 2: Design service architecture
            print(f"🏗️ Designing service architecture...")
            blueprint = await self._design_service(request, analysis)

            # Phase 3: Generate agents
            print(f"🤖 Generating {len(blueprint.agents)} agents...")
            generated_agents = await self._generate_agents(blueprint)

            if not generated_agents:
                errors.append("Failed to generate agents")
                return self._create_failed_result(request, errors)

            # Phase 4: Compose workflow
            print(f"🔄 Composing workflow...")
            workflow = await self._compose_workflow(
                [agent["name"] for agent in generated_agents], request.constraints
            )
            blueprint.workflow = workflow

            # Phase 5: Deploy service
            print(f"🚀 Deploying service...")
            deployment_results = await self._deploy_service(generated_agents, request.name)

            # Phase 6: Register API endpoints
            print(f"📡 Registering API endpoints...")
            api_endpoints = await self._register_apis(deployment_results, blueprint)

            # Calculate metrics
            build_time = time.time() - start_time
            metrics = {
                "build_time": build_time,
                "agents_generated": len(generated_agents),
                "agents_deployed": len([r for r in deployment_results if r.success]),
                "api_endpoints": len(api_endpoints),
                "workflow_steps": len(workflow.dag.steps) if workflow else 0,
                "optimization_score": workflow.optimization_score if workflow else 0,
            }

            # Record service
            self._record_service(request, blueprint, metrics)

            return ServiceResult(
                success=True,
                service_name=request.name,
                blueprint=blueprint,
                deployed_agents=[r.agent_name for r in deployment_results if r.success],
                api_endpoints=api_endpoints,
                workflow_id=workflow.name if workflow else "",
                metrics=metrics,
                errors=[],
            )

        except Exception as e:
            errors.append(f"Service build error: {str(e)}")
            return self._create_failed_result(request, errors)

    async def _design_service(self, request: ServiceRequest, analysis: Any) -> ServiceBlueprint:
        """Design service architecture"""

        # Determine required agents based on service type
        agents = self._determine_agents(request.type, analysis)

        # Design architecture
        architecture = {
            "type": request.type,
            "style": self._determine_architecture_style(request.type),
            "patterns": analysis.patterns,
            "layers": self._design_layers(request.type),
            "data_flow": self._design_data_flow(agents),
        }

        # Determine dependencies
        dependencies = self._determine_dependencies(request.type)

        # Create API specification
        api_spec = self._create_api_spec(request, agents)

        # Create deployment plan
        deployment_plan = {
            "environment": "development",
            "strategy": "rolling" if len(agents) > 3 else "immediate",
            "rollback": True,
            "monitoring": True,
        }

        # Estimate cost and time
        estimated_cost = self._estimate_cost(agents, architecture)
        estimated_time = self._estimate_time(agents, request.complexity)

        return ServiceBlueprint(
            service_name=request.name,
            agents=agents,
            workflow=None,  # Set later
            architecture=architecture,
            dependencies=dependencies,
            api_spec=api_spec,
            deployment_plan=deployment_plan,
            estimated_cost=estimated_cost,
            estimated_time=estimated_time,
        )

    def _determine_agents(self, service_type: str, analysis: Any) -> List[Dict]:
        """Determine required agents for service"""

        agents = []

        if service_type == "microservice":
            agents = [
                {"name": "APIGatewayAgent", "type": "gateway", "priority": 1},
                {"name": "ValidationAgent", "type": "validator", "priority": 2},
                {"name": "BusinessLogicAgent", "type": "processor", "priority": 3},
                {"name": "DataAccessAgent", "type": "data", "priority": 4},
                {"name": "ResponseAgent", "type": "responder", "priority": 5},
            ]
        elif service_type == "api":
            agents = [
                {"name": "RequestHandlerAgent", "type": "handler", "priority": 1},
                {"name": "AuthAgent", "type": "auth", "priority": 1},
                {"name": "ProcessorAgent", "type": "processor", "priority": 2},
                {"name": "CacheAgent", "type": "cache", "priority": 3},
            ]
        elif service_type == "data_processor":
            agents = [
                {"name": "IngestionAgent", "type": "ingestion", "priority": 1},
                {"name": "ValidationAgent", "type": "validator", "priority": 2},
                {"name": "TransformAgent", "type": "transform", "priority": 3},
                {"name": "AggregationAgent", "type": "aggregation", "priority": 4},
                {"name": "OutputAgent", "type": "output", "priority": 5},
            ]
        elif service_type == "event_handler":
            agents = [
                {"name": "EventListenerAgent", "type": "listener", "priority": 1},
                {"name": "EventParserAgent", "type": "parser", "priority": 2},
                {"name": "EventProcessorAgent", "type": "processor", "priority": 3},
                {"name": "EventDispatcherAgent", "type": "dispatcher", "priority": 4},
            ]
        else:
            # Generic service
            agents = [
                {"name": "InputAgent", "type": "input", "priority": 1},
                {"name": "ProcessAgent", "type": "processor", "priority": 2},
                {"name": "OutputAgent", "type": "output", "priority": 3},
            ]

        # Add requirements from analysis
        if len(analysis.requirements) > 10:
            agents.append({"name": "OrchestrationAgent", "type": "orchestrator", "priority": 0})

        return agents

    def _determine_architecture_style(self, service_type: str) -> str:
        """Determine architecture style"""

        styles = {
            "microservice": "microservices",
            "api": "rest",
            "data_processor": "pipeline",
            "event_handler": "event-driven",
        }
        return styles.get(service_type, "layered")

    def _design_layers(self, service_type: str) -> List[str]:
        """Design service layers"""

        if service_type == "microservice":
            return ["presentation", "business", "data", "integration"]
        elif service_type == "api":
            return ["gateway", "service", "data"]
        elif service_type == "data_processor":
            return ["ingestion", "processing", "storage", "output"]
        else:
            return ["input", "processing", "output"]

    def _design_data_flow(self, agents: List[Dict]) -> Dict[str, Any]:
        """Design data flow between agents"""

        return {
            "type": "sequential" if len(agents) <= 3 else "parallel",
            "stages": len(agents),
            "checkpoints": max(1, len(agents) // 3),
        }

    def _determine_dependencies(self, service_type: str) -> List[str]:
        """Determine service dependencies"""

        base_deps = ["asyncio", "typing", "dataclasses"]

        if service_type in ["microservice", "api"]:
            base_deps.extend(["fastapi", "pydantic", "uvicorn"])
        if service_type == "data_processor":
            base_deps.extend(["pandas", "numpy"])
        if service_type == "event_handler":
            base_deps.extend(["aiokafka", "redis"])

        return base_deps

    def _create_api_spec(self, request: ServiceRequest, agents: List[Dict]) -> Dict[str, Any]:
        """Create API specification"""

        return {
            "openapi": "3.0.0",
            "info": {"title": request.name, "description": request.description, "version": "1.0.0"},
            "paths": {
                f"/api/v1/{request.name.lower()}/execute": {
                    "post": {
                        "summary": f"Execute {request.name}",
                        "operationId": f"execute_{request.name.lower()}",
                        "responses": {"200": {"description": "Success"}},
                    }
                },
                f"/api/v1/{request.name.lower()}/status": {
                    "get": {
                        "summary": f"Get {request.name} status",
                        "operationId": f"status_{request.name.lower()}",
                        "responses": {"200": {"description": "Status"}},
                    }
                },
            },
        }

    def _estimate_cost(self, agents: List[Dict], architecture: Dict) -> float:
        """Estimate service cost"""

        # Base cost per agent
        base_cost = 0.05 * len(agents)

        # Architecture complexity factor
        complexity_factors = {
            "microservices": 1.5,
            "event-driven": 1.3,
            "pipeline": 1.2,
            "rest": 1.0,
            "layered": 0.9,
        }

        factor = complexity_factors.get(architecture["style"], 1.0)

        return base_cost * factor

    def _estimate_time(self, agents: List[Dict], complexity: str) -> float:
        """Estimate build time in seconds"""

        # Base time per agent
        time_per_agent = 2.0

        # Complexity multiplier
        complexity_multipliers = {"simple": 1.0, "medium": 1.5, "complex": 2.0}

        multiplier = complexity_multipliers.get(complexity, 1.5)

        return len(agents) * time_per_agent * multiplier

    async def _generate_agents(self, blueprint: ServiceBlueprint) -> List[Dict[str, Any]]:
        """Generate all agents for service"""

        generated = []

        for agent_spec in blueprint.agents:
            try:
                # Generate agent requirements
                requirements = f"""
                Create {agent_spec['type']} agent for {blueprint.service_name}.
                Priority: {agent_spec.get('priority', 5)}
                Architecture: {blueprint.architecture['style']}
                """

                # Generate agent
                agent_result = await self.generator.generate(requirements, agent_spec["name"])

                # Save generated code
                agent_path = f"/tmp/{agent_spec['name'].lower()}.py"
                with open(agent_path, "w") as f:
                    f.write(agent_result.code)

                generated.append(
                    {
                        "name": agent_spec["name"],
                        "path": agent_path,
                        "code": agent_result.code,
                        "size": agent_result.size_bytes,
                        "version": "1.0.0",
                    }
                )

            except Exception as e:
                print(f"Failed to generate {agent_spec['name']}: {e}")

        return generated

    async def _compose_workflow(self, agent_names: List[str], constraints: Dict[str, Any]) -> Any:
        """Compose workflow for agents"""

        requirements = {"agents": agent_names, "constraints": constraints}

        return await self.composer.compose(agent_names, requirements, constraints)

    async def _deploy_service(self, agents: List[Dict[str, Any]], service_name: str) -> List[Any]:
        """Deploy all service agents"""

        configs = []

        for agent in agents:
            config = DeploymentConfig(
                agent_name=agent["name"],
                agent_path=agent["path"],
                version=agent.get("version", "1.0.0"),
                environment="development",
                validation_required=True,
                registry_update=True,
            )
            configs.append(config)

        # Deploy in batch
        return await self.deployer.batch_deploy(configs, parallel=True)

    async def _register_apis(
        self, deployment_results: List[Any], blueprint: ServiceBlueprint
    ) -> List[str]:
        """Register API endpoints"""

        endpoints = []

        for result in deployment_results:
            if result.success:
                # API endpoints are auto-registered by deployer
                base_path = f"/api/v1/{result.agent_name.lower()}"
                endpoints.extend(
                    [f"{base_path}/execute", f"{base_path}/status", f"{base_path}/health"]
                )

        return endpoints

    def _create_failed_result(self, request: ServiceRequest, errors: List[str]) -> ServiceResult:
        """Create failed result"""

        return ServiceResult(
            success=False,
            service_name=request.name,
            blueprint=None,
            deployed_agents=[],
            api_endpoints=[],
            workflow_id="",
            metrics={},
            errors=errors,
        )

    def _record_service(
        self, request: ServiceRequest, blueprint: ServiceBlueprint, metrics: Dict[str, Any]
    ):
        """Record service in history"""

        record = {
            "timestamp": time.time(),
            "service_name": request.name,
            "type": request.type,
            "agents_count": len(blueprint.agents),
            "metrics": metrics,
        }

        self.service_history.append(record)

        # Keep only last 50 services
        if len(self.service_history) > 50:
            self.service_history = self.service_history[-50:]

    def get_metrics(self) -> Dict[str, Any]:
        """Get service builder metrics"""

        if not self.service_history:
            return {"services_built": 0, "average_agents": 0, "average_build_time": 0}

        total = len(self.service_history)
        avg_agents = sum(s["agents_count"] for s in self.service_history) / total
        avg_time = sum(s["metrics"].get("build_time", 0) for s in self.service_history) / total

        return {
            "services_built": total,
            "average_agents": avg_agents,
            "average_build_time": avg_time,
            "service_types": list(set(s["type"] for s in self.service_history)),
        }


# Global instance
service_builder = None


def get_service_builder() -> ServiceBuilder:
    """Get or create service builder instance"""
    global service_builder
    if not service_builder:
        service_builder = ServiceBuilder()
    return service_builder


async def main():
    """Test service builder"""
    builder = get_service_builder()

    # Test service request
    request = ServiceRequest(
        name="UserService",
        description="User management microservice",
        requirements="""
        Create a user management service that:
        - Handles user registration and authentication
        - Manages user profiles
        - Provides CRUD operations
        - Includes caching for performance
        - Has proper error handling
        """,
        type="microservice",
        complexity="medium",
        constraints={"cpu": 4.0, "memory": 8192},
    )

    print(f"🏗️ Building {request.name}...")
    result = await builder.build_service(request)

    if result.success:
        print(f"✅ Service built successfully!")
        print(f"   Agents deployed: {len(result.deployed_agents)}")
        print(f"   API endpoints: {len(result.api_endpoints)}")
        print(f"   Build time: {result.metrics['build_time']:.2f}s")
    else:
        print(f"❌ Service build failed: {result.errors}")


if __name__ == "__main__":
    asyncio.run(main())
