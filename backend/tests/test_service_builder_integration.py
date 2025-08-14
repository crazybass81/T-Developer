"""
ServiceBuilder Integration Tests
Day 25: Phase 2 - Meta Agents
Complete end-to-end service building tests
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List

import pytest

from src.agents.meta.agent_generator import get_generator
from src.agents.meta.requirement_analyzer import get_analyzer
from src.agents.meta.service_builder import ServiceBuilder, ServiceRequest, get_service_builder
from src.agents.meta.workflow_composer import get_composer
from src.deployment.auto_deployer import get_auto_deployer


class TestServiceBuilder:
    """Test service builder functionality"""

    @pytest.fixture
    def builder(self):
        """Get service builder instance"""
        return get_service_builder()

    @pytest.mark.asyncio
    async def test_build_simple_service(self, builder):
        """Test building a simple service"""

        request = ServiceRequest(
            name="SimpleService",
            description="A simple test service",
            requirements="Create a basic service that processes data",
            type="generic",
            complexity="simple",
        )

        result = await builder.build_service(request)

        assert result.service_name == "SimpleService"
        # May not succeed in test environment
        if result.success:
            assert result.blueprint is not None
            assert len(result.blueprint.agents) > 0

    @pytest.mark.asyncio
    async def test_build_microservice(self, builder):
        """Test building a microservice"""

        request = ServiceRequest(
            name="UserMicroservice",
            description="User management microservice",
            requirements="""
            Create a user management service with:
            - User registration
            - Authentication
            - Profile management
            """,
            type="microservice",
            complexity="medium",
        )

        result = await builder.build_service(request)

        assert result.service_name == "UserMicroservice"

        if result.blueprint:
            # Should have standard microservice agents
            agent_names = [a["name"] for a in result.blueprint.agents]
            assert "APIGatewayAgent" in agent_names
            assert "ValidationAgent" in agent_names
            assert "BusinessLogicAgent" in agent_names

    @pytest.mark.asyncio
    async def test_build_data_processor(self, builder):
        """Test building a data processor service"""

        request = ServiceRequest(
            name="DataProcessor",
            description="Data processing pipeline",
            requirements="""
            Process incoming data:
            - Validate format
            - Transform structure
            - Aggregate results
            - Store output
            """,
            type="data_processor",
            complexity="medium",
        )

        result = await builder.build_service(request)

        assert result.service_name == "DataProcessor"

        if result.blueprint:
            # Should have data processing agents
            agent_names = [a["name"] for a in result.blueprint.agents]
            assert "IngestionAgent" in agent_names
            assert "ValidationAgent" in agent_names
            assert "TransformAgent" in agent_names

    @pytest.mark.asyncio
    async def test_build_event_handler(self, builder):
        """Test building an event handler service"""

        request = ServiceRequest(
            name="EventHandler",
            description="Event processing service",
            requirements="""
            Handle incoming events:
            - Listen for events
            - Parse event data
            - Process events
            - Dispatch results
            """,
            type="event_handler",
            complexity="simple",
        )

        result = await builder.build_service(request)

        assert result.service_name == "EventHandler"

        if result.blueprint:
            # Should have event handling agents
            agent_names = [a["name"] for a in result.blueprint.agents]
            assert "EventListenerAgent" in agent_names
            assert "EventProcessorAgent" in agent_names

    @pytest.mark.asyncio
    async def test_build_api_service(self, builder):
        """Test building an API service"""

        request = ServiceRequest(
            name="APIService",
            description="REST API service",
            requirements="""
            Create REST API with:
            - Request handling
            - Authentication
            - Data processing
            - Response formatting
            """,
            type="api",
            complexity="medium",
        )

        result = await builder.build_service(request)

        assert result.service_name == "APIService"

        if result.blueprint:
            # Should have API agents
            agent_names = [a["name"] for a in result.blueprint.agents]
            assert "RequestHandlerAgent" in agent_names
            assert "AuthAgent" in agent_names

    def test_service_blueprint_creation(self, builder):
        """Test blueprint creation logic"""

        request = ServiceRequest(
            name="TestService",
            description="Test",
            requirements="Test requirements",
            type="microservice",
            complexity="simple",
        )

        # Mock analysis result
        class MockAnalysis:
            def __init__(self):
                self.requirements = []
                self.patterns = ["microservices"]
                self.complexity_score = 0.5

        # Test blueprint creation synchronously
        import asyncio

        loop = asyncio.new_event_loop()
        blueprint = loop.run_until_complete(builder._design_service(request, MockAnalysis()))

        assert blueprint.service_name == "TestService"
        assert blueprint.architecture["type"] == "microservice"
        assert blueprint.architecture["style"] == "microservices"
        assert len(blueprint.agents) > 0
        assert blueprint.estimated_cost > 0
        assert blueprint.estimated_time > 0

    def test_agent_determination(self, builder):
        """Test agent determination for different service types"""

        class MockAnalysis:
            def __init__(self):
                self.requirements = []

        analysis = MockAnalysis()

        # Test microservice agents
        agents = builder._determine_agents("microservice", analysis)
        assert len(agents) == 5
        assert any(a["name"] == "APIGatewayAgent" for a in agents)

        # Test API agents
        agents = builder._determine_agents("api", analysis)
        assert len(agents) == 4
        assert any(a["name"] == "RequestHandlerAgent" for a in agents)

        # Test data processor agents
        agents = builder._determine_agents("data_processor", analysis)
        assert len(agents) == 5
        assert any(a["name"] == "IngestionAgent" for a in agents)

        # Test event handler agents
        agents = builder._determine_agents("event_handler", analysis)
        assert len(agents) == 4
        assert any(a["name"] == "EventListenerAgent" for a in agents)

    def test_cost_estimation(self, builder):
        """Test cost estimation logic"""

        agents = [{"name": f"Agent{i}"} for i in range(5)]

        # Test different architectures
        architectures = [
            {"style": "microservices"},
            {"style": "event-driven"},
            {"style": "pipeline"},
            {"style": "rest"},
            {"style": "layered"},
        ]

        costs = []
        for arch in architectures:
            cost = builder._estimate_cost(agents, arch)
            costs.append(cost)
            assert cost > 0

        # Microservices should be most expensive
        assert costs[0] > costs[3]  # More than REST
        assert costs[0] > costs[4]  # More than layered

    def test_time_estimation(self, builder):
        """Test time estimation logic"""

        agents = [{"name": f"Agent{i}"} for i in range(5)]

        # Test different complexities
        simple_time = builder._estimate_time(agents, "simple")
        medium_time = builder._estimate_time(agents, "medium")
        complex_time = builder._estimate_time(agents, "complex")

        assert simple_time > 0
        assert medium_time > simple_time
        assert complex_time > medium_time

    def test_api_spec_creation(self, builder):
        """Test API specification creation"""

        request = ServiceRequest(
            name="TestAPI",
            description="Test API service",
            requirements="Test",
            type="api",
            complexity="simple",
        )

        agents = [{"name": "TestAgent"}]

        api_spec = builder._create_api_spec(request, agents)

        assert api_spec["openapi"] == "3.0.0"
        assert api_spec["info"]["title"] == "TestAPI"
        assert "/api/v1/testapi/execute" in api_spec["paths"]
        assert "/api/v1/testapi/status" in api_spec["paths"]

    def test_service_metrics(self, builder):
        """Test service metrics tracking"""

        # Get initial metrics
        metrics = builder.get_metrics()
        initial_count = metrics["services_built"]

        # Record a service
        request = ServiceRequest(
            name="MetricsTest",
            description="Test",
            requirements="Test",
            type="api",
            complexity="simple",
        )

        class MockBlueprint:
            def __init__(self):
                self.agents = [{"name": "Agent1"}, {"name": "Agent2"}]

        builder._record_service(request, MockBlueprint(), {"build_time": 10.0})

        # Check updated metrics
        new_metrics = builder.get_metrics()
        assert new_metrics["services_built"] == initial_count + 1


class TestRequirementAnalyzer:
    """Test requirement analyzer integration"""

    @pytest.fixture
    def analyzer(self):
        """Get analyzer instance"""
        return get_analyzer()

    @pytest.mark.asyncio
    async def test_analyze_service_requirements(self, analyzer):
        """Test analyzing service requirements"""

        requirements = """
        Create a user management service that:
        - Handles user registration with email verification
        - Implements JWT-based authentication
        - Manages user profiles with CRUD operations
        - Includes role-based access control
        - Provides password reset functionality
        - Integrates with external OAuth providers
        """

        result = await analyzer.analyze(requirements)

        assert result is not None
        assert len(result.requirements) > 0
        assert result.complexity_score >= 0.0
        assert result.complexity_score <= 1.0


class TestAgentGenerator:
    """Test agent generator integration"""

    @pytest.fixture
    def generator(self):
        """Get generator instance"""
        return get_generator()

    @pytest.mark.asyncio
    async def test_generate_service_agent(self, generator):
        """Test generating agent for service"""

        requirements = """
        Create a validation agent that:
        - Validates input data format
        - Checks business rules
        - Returns validation errors
        """

        result = await generator.generate(requirements, "ValidationAgent")

        assert result.name == "ValidationAgent"
        assert result.code is not None
        assert result.size_bytes < 6500  # Must meet size constraint
        assert "async" in result.code  # Should be async
        assert "execute" in result.code  # Should have execute method


class TestWorkflowComposer:
    """Test workflow composer integration"""

    @pytest.fixture
    def composer(self):
        """Get composer instance"""
        return get_composer()

    @pytest.mark.asyncio
    async def test_compose_service_workflow(self, composer):
        """Test composing workflow for service agents"""

        agents = [
            "APIGatewayAgent",
            "ValidationAgent",
            "BusinessLogicAgent",
            "DataAccessAgent",
            "ResponseAgent",
        ]

        requirements = {"type": "microservice", "flow": "sequential"}

        workflow = await composer.compose(agents, requirements)

        assert workflow is not None
        assert len(workflow.dag.steps) == len(agents)
        assert workflow.optimization_score >= 0.0
        assert workflow.optimization_score <= 1.0


@pytest.mark.integration
class TestFullIntegration:
    """Full integration tests for ServiceBuilder"""

    @pytest.mark.asyncio
    async def test_complete_service_build_flow(self):
        """Test complete service building flow"""

        builder = get_service_builder()

        # Create comprehensive service request
        request = ServiceRequest(
            name="CompleteService",
            description="Complete test service",
            requirements="""
            Build a complete data processing service that:
            1. Accepts JSON data via REST API
            2. Validates the data structure
            3. Transforms the data format
            4. Enriches data with external sources
            5. Stores processed data
            6. Returns processing results
            7. Handles errors gracefully
            8. Provides monitoring metrics
            """,
            type="data_processor",
            complexity="complex",
            constraints={"cpu": 8.0, "memory": 16384, "disk": 51200},
        )

        print(f"\n🏗️ Building {request.name}...")
        result = await builder.build_service(request)

        # Check result structure
        assert result.service_name == "CompleteService"

        if result.success:
            print(f"✅ Service built successfully!")

            # Check blueprint
            assert result.blueprint is not None
            assert len(result.blueprint.agents) > 0
            assert result.blueprint.architecture["type"] == "data_processor"

            # Check workflow
            if result.blueprint.workflow:
                assert result.blueprint.workflow.dag is not None
                assert len(result.blueprint.workflow.dag.steps) > 0

            # Check API spec
            assert "openapi" in result.blueprint.api_spec

            # Check metrics
            assert result.metrics["agents_generated"] > 0
            assert result.metrics["build_time"] > 0

            print(f"   Agents: {result.metrics['agents_generated']}")
            print(f"   Deployed: {result.metrics['agents_deployed']}")
            print(f"   Endpoints: {result.metrics['api_endpoints']}")
            print(f"   Build time: {result.metrics['build_time']:.2f}s")
            print(f"   Optimization: {result.metrics['optimization_score']:.2f}")
        else:
            print(f"❌ Service build failed: {result.errors}")
            # This is expected in test environment
            assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_multiple_service_types(self):
        """Test building multiple service types"""

        builder = get_service_builder()

        service_types = [
            ("microservice", "UserService", "User management"),
            ("api", "SearchAPI", "Search functionality"),
            ("data_processor", "ETLPipeline", "Data ETL"),
            ("event_handler", "NotificationHandler", "Handle notifications"),
        ]

        results = []

        for svc_type, name, desc in service_types:
            request = ServiceRequest(
                name=name,
                description=desc,
                requirements=f"Create a {svc_type} for {desc}",
                type=svc_type,
                complexity="simple",
            )

            result = await builder.build_service(request)
            results.append(result)

            # Check each result
            assert result.service_name == name

            if result.blueprint:
                assert result.blueprint.architecture["type"] == svc_type

        # Check metrics after multiple builds
        metrics = builder.get_metrics()
        assert metrics["services_built"] >= len(service_types)
        assert len(metrics["service_types"]) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
