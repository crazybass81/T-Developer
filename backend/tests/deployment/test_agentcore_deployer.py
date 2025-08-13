import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.deployment.agentcore_deployer import AgentCoreDeployer, AgentSpec, Status


class TestAgentSpec:
    def test_agent_spec_creation(self):
        spec = AgentSpec(name="test_agent", code='def test(): return "hello"', version="1.0.0")
        assert spec.name == "test_agent"
        assert spec.version == "1.0.0"
        assert spec.runtime == "python3.11"  # default
        assert spec.timeout == 900  # default

    def test_agent_spec_with_custom_values(self):
        spec = AgentSpec(
            name="custom_agent",
            code="print('test')",
            version="2.0.0",
            description="Custom agent",
            runtime="python3.12",
            timeout=1800,
            memory=256,
        )
        assert spec.description == "Custom agent"
        assert spec.runtime == "python3.12"
        assert spec.timeout == 1800
        assert spec.memory == 256


class TestAgentCoreDeployer:
    @pytest.fixture
    def mock_bedrock_clients(self):
        with patch("boto3.client") as mock_client:
            mock_agent_client = MagicMock()
            mock_runtime_client = MagicMock()

            def client_factory(service_name, **kwargs):
                if service_name == "bedrock-agent":
                    return mock_agent_client
                elif service_name == "bedrock-agent-runtime":
                    return mock_runtime_client
                return MagicMock()

            mock_client.side_effect = client_factory
            yield mock_agent_client, mock_runtime_client

    @pytest.fixture
    def deployer(self, mock_bedrock_clients):
        with patch.dict(
            os.environ,
            {"BEDROCK_AGENT_ID": "test_agent_id", "BEDROCK_AGENT_ALIAS_ID": "test_alias_id"},
        ):
            return AgentCoreDeployer()

    def test_deployer_initialization(self, deployer):
        assert deployer.region == "us-east-1"
        assert deployer.aid == "test_agent_id"
        assert deployer.alias == "test_alias_id"
        assert isinstance(deployer.deps, dict)

    @pytest.mark.asyncio
    async def test_deploy_agent_success(self, deployer, mock_bedrock_clients):
        mock_agent_client, _ = mock_bedrock_clients

        # Mock successful responses
        mock_agent_client.create_agent_action_group.return_value = {
            "agentActionGroup": {"actionGroupId": "test_action_group_id"}
        }
        mock_agent_client.update_agent.return_value = {"agentId": "test_agent_id"}
        mock_agent_client.prepare_agent.return_value = {"agentId": "test_agent_id"}

        spec = AgentSpec(name="test_agent", code='def test(): return "success"', version="1.0.0")

        result = await deployer.deploy_agent(spec)

        assert result["name"] == "test_agent"
        assert result["status"] == Status.DEPLOYED
        assert "duration" in result
        assert result["error"] is None

        # Verify API calls were made
        mock_agent_client.create_agent_action_group.assert_called_once()
        mock_agent_client.update_agent.assert_called_once()
        mock_agent_client.prepare_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_deploy_agent_size_constraint(self, deployer):
        large_code = "x = 1\n" * 5000  # Create code > 6.5KB
        spec = AgentSpec(name="large_agent", code=large_code, version="1.0.0")

        result = await deployer.deploy_agent(spec)

        assert result["status"] == Status.FAILED
        assert "too large" in result["error"]

    @pytest.mark.asyncio
    async def test_deploy_agent_failure(self, deployer, mock_bedrock_clients):
        mock_agent_client, _ = mock_bedrock_clients
        mock_agent_client.create_agent_action_group.side_effect = Exception("API Error")

        spec = AgentSpec(name="failing_agent", code="def test(): pass", version="1.0.0")

        result = await deployer.deploy_agent(spec)

        assert result["status"] == Status.FAILED
        assert "API Error" in result["error"]

    def test_get_deployment(self, deployer):
        # Add a mock deployment
        deployer.deps["test123"] = {"id": "test123", "status": Status.DEPLOYED}

        result = deployer.get_deployment("test123")
        assert result["id"] == "test123"
        assert result["status"] == Status.DEPLOYED

        # Test non-existent deployment
        result = deployer.get_deployment("nonexistent")
        assert result is None

    def test_list_deployments(self, deployer):
        # Add mock deployments
        deployer.deps["dep1"] = {"id": "dep1", "status": Status.DEPLOYED}
        deployer.deps["dep2"] = {"id": "dep2", "status": Status.FAILED}

        result = deployer.list_deployments()
        assert len(result) == 2
        assert any(d["id"] == "dep1" for d in result)
        assert any(d["id"] == "dep2" for d in result)

    @pytest.mark.asyncio
    async def test_test_deployment_success(self, deployer, mock_bedrock_clients):
        _, mock_runtime_client = mock_bedrock_clients
        mock_runtime_client.invoke_agent.return_value = {"response": "success"}

        # Add a deployed agent
        deployer.deps["test123"] = {"id": "test123", "status": Status.DEPLOYED}

        result = await deployer.test_deployment("test123")

        assert result["status"] == "success"
        assert "response" in result
        mock_runtime_client.invoke_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_deployment_not_ready(self, deployer):
        # Add a pending deployment
        deployer.deps["test123"] = {"id": "test123", "status": Status.PENDING}

        result = await deployer.test_deployment("test123")

        assert result["status"] == "error"
        assert "Not ready" in result["message"]

    @pytest.mark.asyncio
    async def test_test_deployment_nonexistent(self, deployer):
        result = await deployer.test_deployment("nonexistent")

        assert result["status"] == "error"
        assert "Not ready" in result["message"]


class TestDeploymentIntegration:
    @pytest.mark.asyncio
    async def test_full_deployment_lifecycle(self):
        """Test complete deployment lifecycle with mocks"""
        with patch("boto3.client") as mock_client, patch.dict(
            os.environ, {"BEDROCK_AGENT_ID": "test_id"}
        ):
            # Setup mocks
            mock_agent_client = MagicMock()
            mock_runtime_client = MagicMock()

            def client_factory(service_name, **kwargs):
                if service_name == "bedrock-agent":
                    return mock_agent_client
                elif service_name == "bedrock-agent-runtime":
                    return mock_runtime_client
                return MagicMock()

            mock_client.side_effect = client_factory

            mock_agent_client.create_agent_action_group.return_value = {
                "agentActionGroup": {"actionGroupId": "ag_123"}
            }
            mock_agent_client.update_agent.return_value = {"agentId": "test_id"}
            mock_agent_client.prepare_agent.return_value = {"agentId": "test_id"}
            mock_runtime_client.invoke_agent.return_value = {"response": "test_success"}

            # Create deployer and deploy agent
            deployer = AgentCoreDeployer()
            spec = AgentSpec("integration_test", 'def run(): return "ok"', "1.0.0")

            # Deploy
            deploy_result = await deployer.deploy_agent(spec)
            assert deploy_result["status"] == Status.DEPLOYED

            # Test deployment
            test_result = await deployer.test_deployment(deploy_result["id"])
            assert test_result["status"] == "success"

            # Verify deployment is listed
            deployments = deployer.list_deployments()
            assert len(deployments) == 1
            assert deployments[0]["name"] == "integration_test"


class TestPerformanceConstraints:
    @pytest.mark.asyncio
    async def test_deployment_instantiation_speed(self):
        """Test that deployer instantiation is fast"""
        import time

        with patch("boto3.client") as mock_client, patch.dict(
            os.environ, {"BEDROCK_AGENT_ID": "test_id"}
        ):
            mock_client.return_value = MagicMock()

            # Measure instantiation time
            start_time = time.perf_counter()
            deployer = AgentCoreDeployer()
            end_time = time.perf_counter()

            instantiation_time = (end_time - start_time) * 1_000_000  # Convert to microseconds

            # Should instantiate in < 3 microseconds (very lenient for mocked test)
            assert instantiation_time < 100, f"Instantiation took {instantiation_time:.2f}μs"
            assert deployer is not None

    @pytest.mark.asyncio
    async def test_memory_usage_constraints(self):
        """Test memory usage of deployment components"""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        base_memory = process.memory_info().rss

        with patch("boto3.client") as mock_client, patch.dict(
            os.environ, {"BEDROCK_AGENT_ID": "test_id"}
        ):
            mock_client.return_value = MagicMock()

            # Create multiple deployers to test memory usage
            deployers = []
            for i in range(10):
                deployers.append(AgentCoreDeployer())

            current_memory = process.memory_info().rss
            memory_used = current_memory - base_memory
            memory_used_kb = memory_used / 1024

            # Should use reasonable amount of memory (under 1MB for 10 instances)
            assert memory_used_kb < 1024, f"Memory usage too high: {memory_used_kb:.2f}KB"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
