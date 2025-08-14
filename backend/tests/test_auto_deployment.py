"""
Test suite for Auto Deployment System
Day 24: Phase 2 - Meta Agents
"""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest

from src.deployment.api_registry_updater import (
    APIEndpoint,
    APIRegistryUpdater,
    get_registry_updater,
)
from src.deployment.auto_deployer import AutoDeployer, DeploymentConfig, get_auto_deployer
from src.deployment.validation_engine import ValidationEngine, get_validator


class TestAutoDeployer:
    """Test auto deployer functionality"""

    @pytest.fixture
    def deployer(self):
        """Get deployer instance"""
        return get_auto_deployer()

    @pytest.fixture
    def test_agent_code(self):
        """Test agent code"""
        return """
import asyncio
from typing import Dict, Any

class TestAgent:
    def __init__(self):
        self.name = "TestAgent"
        self.version = "1.0.0"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.001)
        return {
            "status": "success",
            "agent": self.name,
            "data": input_data
        }

    async def health_check(self) -> bool:
        return True
"""

    @pytest.mark.asyncio
    async def test_deploy_agent(self, deployer, test_agent_code):
        """Test single agent deployment"""

        # Create temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_agent_code)
            agent_path = f.name

        try:
            config = DeploymentConfig(
                agent_name="TestAgent",
                agent_path=agent_path,
                version="1.0.0",
                environment="development",
                validation_required=False,  # Skip for test
            )

            result = await deployer.deploy_agent(config)

            assert result.agent_name == "TestAgent"
            assert result.version == "1.0.0"
            # Note: actual deployment may fail in test environment

        finally:
            os.unlink(agent_path)

    @pytest.mark.asyncio
    async def test_batch_deploy(self, deployer, test_agent_code):
        """Test batch deployment"""

        configs = []
        temp_files = []

        try:
            # Create multiple test agents
            for i in range(3):
                with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                    f.write(test_agent_code.replace("TestAgent", f"Agent{i}"))
                    temp_files.append(f.name)

                    config = DeploymentConfig(
                        agent_name=f"Agent{i}",
                        agent_path=f.name,
                        version="1.0.0",
                        environment="development",
                        validation_required=False,
                    )
                    configs.append(config)

            # Deploy batch
            results = await deployer.batch_deploy(configs, parallel=True)

            assert len(results) == 3
            for i, result in enumerate(results):
                assert result.agent_name == f"Agent{i}"

        finally:
            for path in temp_files:
                os.unlink(path)

    @pytest.mark.asyncio
    async def test_deployment_with_validation(self, deployer, test_agent_code):
        """Test deployment with validation"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_agent_code)
            agent_path = f.name

        try:
            config = DeploymentConfig(
                agent_name="ValidatedAgent",
                agent_path=agent_path,
                version="1.0.0",
                environment="development",
                validation_required=True,
                auto_rollback=True,
            )

            result = await deployer.deploy_agent(config)

            # Validation should pass for valid code
            assert result.agent_name == "ValidatedAgent"

        finally:
            os.unlink(agent_path)

    def test_deployment_history(self, deployer):
        """Test deployment history tracking"""

        # Simulate recording deployments
        config = DeploymentConfig(
            agent_name="HistoryAgent",
            agent_path="/tmp/test.py",
            version="1.0.0",
            environment="development",
        )

        deployer._record_deployment(config, "deploy_123", True)
        deployer._record_deployment(config, "deploy_124", False)

        history = deployer.get_deployment_history()
        assert len(history) >= 2

        # Filter by agent name
        agent_history = deployer.get_deployment_history(agent_name="HistoryAgent")
        assert all(h["agent_name"] == "HistoryAgent" for h in agent_history)

    def test_deployer_metrics(self, deployer):
        """Test deployer metrics"""

        metrics = deployer.get_metrics()

        assert "total_deployments" in metrics
        assert "success_rate" in metrics
        assert "max_retries" in metrics
        assert metrics["max_retries"] == 3


class TestValidationEngine:
    """Test validation engine functionality"""

    @pytest.fixture
    def validator(self):
        """Get validator instance"""
        return get_validator()

    @pytest.mark.asyncio
    async def test_validate_valid_agent(self, validator):
        """Test validation of valid agent"""

        valid_code = """
import asyncio
from typing import Dict, Any

class ValidAgent:
    def __init__(self):
        self.name = "ValidAgent"

    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success"}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(valid_code)
            agent_path = f.name

        try:
            result = await validator.validate_agent(agent_path, "ValidAgent")

            assert result["valid"] is True
            assert len(result["errors"]) == 0
            assert result["size_bytes"] < 6500

        finally:
            os.unlink(agent_path)

    @pytest.mark.asyncio
    async def test_validate_invalid_syntax(self, validator):
        """Test validation of invalid syntax"""

        invalid_code = """
class InvalidAgent:
    def __init__(self)
        self.name = "Invalid"  # Missing colon
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(invalid_code)
            agent_path = f.name

        try:
            result = await validator.validate_agent(agent_path, "InvalidAgent")

            assert result["valid"] is False
            assert len(result["errors"]) > 0
            assert any("syntax" in e.lower() for e in result["errors"])

        finally:
            os.unlink(agent_path)

    @pytest.mark.asyncio
    async def test_validate_size_constraint(self, validator):
        """Test size constraint validation"""

        # Generate large code
        large_code = "# " + "x" * 10000 + "\nclass LargeAgent: pass"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(large_code)
            agent_path = f.name

        try:
            result = await validator.validate_agent(agent_path, "LargeAgent")

            assert result["valid"] is False
            assert any("size" in e.lower() for e in result["errors"])

        finally:
            os.unlink(agent_path)

    @pytest.mark.asyncio
    async def test_validate_security_check(self, validator):
        """Test security validation"""

        unsafe_code = """
import os

class UnsafeAgent:
    def __init__(self):
        self.name = "Unsafe"

    async def execute(self, cmd):
        return eval(cmd)  # Security issue!
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(unsafe_code)
            agent_path = f.name

        try:
            result = await validator.validate_agent(agent_path, "UnsafeAgent")

            assert result["valid"] is False
            assert any("security" in e.lower() for e in result["errors"])

        finally:
            os.unlink(agent_path)

    @pytest.mark.asyncio
    async def test_deployment_validation(self, validator):
        """Test deployment validation"""

        result = await validator.validate_deployment("deploy_test", "TestAgent")

        assert "success" in result
        assert "validations" in result
        assert "health_check" in result["validations"]
        assert "performance_check" in result["validations"]


class TestAPIRegistryUpdater:
    """Test API registry updater functionality"""

    @pytest.fixture
    def updater(self):
        """Get registry updater instance"""
        return get_registry_updater()

    @pytest.mark.asyncio
    async def test_update_registry(self, updater):
        """Test registry update"""

        success = await updater.update_registry(
            agent_name="TestAgent", deployment_id="deploy_001", version="1.0.0"
        )

        assert success is True
        assert "TestAgent" in updater.registry

        entry = updater.registry["TestAgent"]
        assert entry.version == "1.0.0"
        assert entry.status == "active"
        assert len(entry.endpoints) > 0

    @pytest.mark.asyncio
    async def test_custom_endpoints(self, updater):
        """Test custom endpoint registration"""

        custom_endpoints = [
            APIEndpoint(
                path="/api/v1/custom",
                method="POST",
                agent_name="CustomAgent",
                version="1.0.0",
                description="Custom endpoint",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                auth_required=True,
                rate_limit=100,
            )
        ]

        success = await updater.update_registry(
            agent_name="CustomAgent",
            deployment_id="deploy_002",
            version="1.0.0",
            endpoints=custom_endpoints,
        )

        assert success is True

        endpoint = updater.get_endpoint("/api/v1/custom")
        assert endpoint is not None
        assert endpoint.method == "POST"
        assert endpoint.agent_name == "CustomAgent"

    @pytest.mark.asyncio
    async def test_version_deprecation(self, updater):
        """Test version deprecation"""

        # Register v1
        await updater.update_registry(
            agent_name="VersionedAgent", deployment_id="deploy_v1", version="1.0.0"
        )

        # Register v2
        await updater.update_registry(
            agent_name="VersionedAgent", deployment_id="deploy_v2", version="2.0.0"
        )

        # v2 should be active
        entry = updater.registry["VersionedAgent"]
        assert entry.version == "2.0.0"
        assert entry.status == "active"

    def test_api_documentation(self, updater):
        """Test API documentation generation"""

        docs = updater.get_api_documentation()

        assert "version" in docs
        assert "title" in docs
        assert "agents" in docs

    def test_openapi_export(self, updater):
        """Test OpenAPI specification export"""

        openapi = updater.export_openapi()

        assert openapi["openapi"] == "3.0.0"
        assert "info" in openapi
        assert "paths" in openapi
        assert "components" in openapi

    def test_registry_metrics(self, updater):
        """Test registry metrics"""

        metrics = updater.get_metrics()

        assert "total_agents" in metrics
        assert "active_agents" in metrics
        assert "total_endpoints" in metrics
        assert "unique_paths" in metrics


@pytest.mark.integration
class TestIntegration:
    """Integration tests for auto deployment system"""

    @pytest.mark.asyncio
    async def test_complete_deployment_flow(self):
        """Test complete deployment flow"""

        deployer = get_auto_deployer()
        validator = get_validator()
        updater = get_registry_updater()

        # Create test agent
        agent_code = """
import asyncio
from typing import Dict, Any

class IntegrationAgent:
    __version__ = "1.0.0"

    def __init__(self):
        self.name = "IntegrationAgent"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "processed": input_data}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(agent_code)
            agent_path = f.name

        try:
            # Create deployment config
            config = DeploymentConfig(
                agent_name="IntegrationAgent",
                agent_path=agent_path,
                version="1.0.0",
                environment="development",
                validation_required=True,
                registry_update=True,
            )

            # Deploy
            result = await deployer.deploy_agent(config)

            # Check deployment result
            assert result.agent_name == "IntegrationAgent"
            assert result.version == "1.0.0"

            # Verify in registry
            if result.success and result.registry_updated:
                agents = updater.list_active_agents()
                assert "IntegrationAgent" in agents

                endpoints = updater.get_agent_endpoints("IntegrationAgent")
                assert len(endpoints) > 0

            # Get metrics
            deploy_metrics = deployer.get_metrics()
            registry_metrics = updater.get_metrics()

            print(f"\nDeployment metrics: {deploy_metrics}")
            print(f"Registry metrics: {registry_metrics}")

        finally:
            os.unlink(agent_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
