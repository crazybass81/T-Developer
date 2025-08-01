# backend/src/agents/implementations/assembly/test_assembly_agent.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from assembly_agent import (
    AssemblyAgent, ServiceIntegrator, DependencyResolver,
    ConfigurationManager, DeploymentOrchestrator,
    ComponentSpec, AssemblyResult
)

@pytest.fixture
def sample_components():
    return [
        ComponentSpec(
            id="frontend",
            name="React Frontend",
            type="web_app",
            source_code="import React from 'react';",
            dependencies=["react", "axios"],
            config={"port": 3000}
        ),
        ComponentSpec(
            id="backend",
            name="FastAPI Backend",
            type="api_server",
            source_code="from fastapi import FastAPI",
            dependencies=["fastapi", "uvicorn"],
            config={"port": 8000}
        ),
        ComponentSpec(
            id="database",
            name="PostgreSQL Database",
            type="database",
            source_code="-- Database schema",
            dependencies=["postgresql"],
            config={"port": 5432}
        )
    ]

@pytest.fixture
def mock_agent():
    agent = Mock()
    agent.arun = AsyncMock(return_value="Mock response")
    return agent

class TestServiceIntegrator:
    @pytest.mark.asyncio
    async def test_integrate_components(self, sample_components, mock_agent):
        with patch('assembly_agent.Agent', return_value=mock_agent):
            integrator = ServiceIntegrator()
            result = await integrator.integrate_components(sample_components)
            
            assert "architecture" in result
            assert "dependencies" in result
            assert "configuration" in result
            mock_agent.arun.assert_called_once()

    def test_parse_integration_response(self):
        integrator = ServiceIntegrator()
        response = "Integration architecture: microservices"
        result = integrator._parse_integration_response(response)
        
        assert result["architecture"] == "microservices"
        assert "dependencies" in result
        assert "configuration" in result

class TestDependencyResolver:
    @pytest.mark.asyncio
    async def test_resolve_dependencies(self, sample_components, mock_agent):
        with patch('assembly_agent.Agent', return_value=mock_agent):
            resolver = DependencyResolver()
            result = await resolver.resolve_dependencies(sample_components)
            
            assert "resolved_order" in result
            assert "conflicts" in result
            assert "optimizations" in result
            mock_agent.arun.assert_called_once()

    def test_build_dependency_graph(self, sample_components):
        resolver = DependencyResolver()
        graph = resolver._build_dependency_graph(sample_components)
        
        assert "frontend" in graph
        assert "backend" in graph
        assert "database" in graph
        assert graph["frontend"] == ["react", "axios"]

class TestConfigurationManager:
    @pytest.mark.asyncio
    async def test_generate_configuration(self, sample_components, mock_agent):
        with patch('assembly_agent.Agent', return_value=mock_agent):
            config_manager = ConfigurationManager()
            result = await config_manager.generate_configuration(
                sample_components, "production"
            )
            
            assert result["environment"] == "production"
            assert "database" in result
            assert "api" in result
            mock_agent.arun.assert_called_once()

    def test_parse_configuration(self):
        config_manager = ConfigurationManager()
        response = "Database URL: postgresql://localhost:5432/app"
        result = config_manager._parse_configuration(response, "development")
        
        assert result["environment"] == "development"
        assert "database" in result

class TestDeploymentOrchestrator:
    @pytest.mark.asyncio
    async def test_create_deployment_manifest(self, sample_components, mock_agent):
        with patch('assembly_agent.Agent', return_value=mock_agent):
            orchestrator = DeploymentOrchestrator()
            result = await orchestrator.create_deployment_manifest(
                sample_components, "kubernetes"
            )
            
            assert result["apiVersion"] == "apps/v1"
            assert result["kind"] == "Deployment"
            mock_agent.arun.assert_called_once()

    def test_parse_deployment_manifest_kubernetes(self):
        orchestrator = DeploymentOrchestrator()
        response = "Kubernetes deployment manifest"
        result = orchestrator._parse_deployment_manifest(response, "kubernetes")
        
        assert result["apiVersion"] == "apps/v1"
        assert result["kind"] == "Deployment"

    def test_parse_deployment_manifest_docker(self):
        orchestrator = DeploymentOrchestrator()
        response = "Docker deployment"
        result = orchestrator._parse_deployment_manifest(response, "docker")
        
        assert result["platform"] == "docker"
        assert "config" in result

class TestAssemblyAgent:
    @pytest.mark.asyncio
    async def test_assemble_service_full_flow(self, sample_components):
        with patch('assembly_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(return_value="Mock response")
            mock_agent_class.return_value = mock_agent
            
            agent = AssemblyAgent()
            result = await agent.assemble_service(
                sample_components,
                target_environment="production",
                deployment_platform="kubernetes"
            )
            
            assert isinstance(result, AssemblyResult)
            assert result.assembled_code
            assert result.configuration
            assert result.deployment_manifest
            assert result.integration_tests
            assert result.documentation

    @pytest.mark.asyncio
    async def test_generate_integration_tests(self, sample_components):
        with patch('assembly_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(return_value="Integration test code")
            mock_agent_class.return_value = mock_agent
            
            agent = AssemblyAgent()
            result = await agent._generate_integration_tests(sample_components)
            
            assert result == "Integration test code"
            mock_agent.arun.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_documentation(self, sample_components):
        with patch('assembly_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(return_value="Documentation content")
            mock_agent_class.return_value = mock_agent
            
            agent = AssemblyAgent()
            result = await agent._generate_documentation(
                sample_components,
                {"architecture": "microservices"},
                {"environment": "production"}
            )
            
            assert result == "Documentation content"

    @pytest.mark.asyncio
    async def test_assemble_final_code(self, sample_components):
        with patch('assembly_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(return_value="Assembled application code")
            mock_agent_class.return_value = mock_agent
            
            agent = AssemblyAgent()
            result = await agent._assemble_final_code(
                sample_components,
                {"architecture": "microservices"},
                {"resolved_order": ["database", "backend", "frontend"]}
            )
            
            assert result == "Assembled application code"

    @pytest.mark.asyncio
    async def test_batch_assemble(self, sample_components):
        with patch('assembly_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(return_value="Mock response")
            mock_agent_class.return_value = mock_agent
            
            agent = AssemblyAgent()
            service_specs = [
                {
                    "components": sample_components,
                    "environment": "development",
                    "platform": "docker"
                },
                {
                    "components": sample_components[:2],
                    "environment": "production",
                    "platform": "kubernetes"
                }
            ]
            
            results = await agent.batch_assemble(service_specs)
            
            assert len(results) == 2
            assert all(isinstance(r, AssemblyResult) for r in results)

    @pytest.mark.asyncio
    async def test_error_handling_missing_components(self):
        with patch('assembly_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(side_effect=Exception("Component error"))
            mock_agent_class.return_value = mock_agent
            
            agent = AssemblyAgent()
            
            with pytest.raises(Exception):
                await agent.assemble_service([])

if __name__ == "__main__":
    pytest.main([__file__])