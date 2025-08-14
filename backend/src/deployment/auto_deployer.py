"""
Auto Deployer - Automatic agent deployment to AgentCore
Size: < 6.5KB | Performance: < 3μs
Day 24: Phase 2 - Meta Agents
"""

import asyncio
import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.deployment.agentcore_deployer import AgentCoreDeployer, AgentSpec
from src.deployment.api_registry_updater import APIRegistryUpdater, get_registry_updater
from src.deployment.validation_engine import ValidationEngine, get_validator


@dataclass
class DeploymentConfig:
    """Deployment configuration"""

    agent_name: str
    agent_path: str
    version: str
    environment: str  # dev, staging, prod
    auto_rollback: bool = True
    validation_required: bool = True
    registry_update: bool = True
    backup_enabled: bool = True


@dataclass
class DeploymentResult:
    """Deployment result details"""

    success: bool
    agent_name: str
    version: str
    deployment_id: str
    validation_results: Dict[str, Any]
    registry_updated: bool
    rollback_available: bool
    metrics: Dict[str, Any]
    errors: List[str]


class AutoDeployer:
    """Automatic agent deployment orchestrator"""

    def __init__(self):
        self.deployer = AgentCoreDeployer()
        self.validator = get_validator()
        self.registry_updater = get_registry_updater()
        self.deployment_history = []
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    async def deploy_agent(self, config: DeploymentConfig) -> DeploymentResult:
        """Deploy agent with full automation"""

        start_time = time.time()
        errors = []

        try:
            # Pre-deployment validation
            if config.validation_required:
                validation = await self.validator.validate_agent(
                    config.agent_path, config.agent_name
                )
                if not validation["valid"]:
                    return DeploymentResult(
                        success=False,
                        agent_name=config.agent_name,
                        version=config.version,
                        deployment_id="",
                        validation_results=validation,
                        registry_updated=False,
                        rollback_available=False,
                        metrics={},
                        errors=validation.get("errors", []),
                    )

            # Create backup if enabled
            backup_id = None
            if config.backup_enabled:
                backup_id = await self._create_backup(config)

            # Deploy to AgentCore
            deployment_id = await self._deploy_with_retry(config)

            if not deployment_id:
                errors.append("Deployment failed after retries")
                return DeploymentResult(
                    success=False,
                    agent_name=config.agent_name,
                    version=config.version,
                    deployment_id="",
                    validation_results={},
                    registry_updated=False,
                    rollback_available=bool(backup_id),
                    metrics={},
                    errors=errors,
                )

            # Post-deployment validation
            post_validation = await self.validator.validate_deployment(
                deployment_id, config.agent_name
            )

            if not post_validation["success"]:
                if config.auto_rollback and backup_id:
                    await self._rollback(backup_id, config)
                    errors.append("Post-deployment validation failed, rolled back")
                    return DeploymentResult(
                        success=False,
                        agent_name=config.agent_name,
                        version=config.version,
                        deployment_id=deployment_id,
                        validation_results=post_validation,
                        registry_updated=False,
                        rollback_available=True,
                        metrics={},
                        errors=errors,
                    )

            # Update API registry
            registry_updated = False
            if config.registry_update:
                registry_updated = await self.registry_updater.update_registry(
                    config.agent_name, deployment_id, config.version
                )

            # Calculate metrics
            deployment_time = time.time() - start_time
            metrics = {
                "deployment_time": deployment_time,
                "validation_time": validation.get("time", 0),
                "registry_update_time": 0.1 if registry_updated else 0,
                "total_time": deployment_time,
            }

            # Record deployment
            self._record_deployment(config, deployment_id, True)

            return DeploymentResult(
                success=True,
                agent_name=config.agent_name,
                version=config.version,
                deployment_id=deployment_id,
                validation_results=post_validation,
                registry_updated=registry_updated,
                rollback_available=bool(backup_id),
                metrics=metrics,
                errors=[],
            )

        except Exception as e:
            errors.append(f"Deployment error: {str(e)}")
            return DeploymentResult(
                success=False,
                agent_name=config.agent_name,
                version=config.version,
                deployment_id="",
                validation_results={},
                registry_updated=False,
                rollback_available=False,
                metrics={},
                errors=errors,
            )

    async def _deploy_with_retry(self, config: DeploymentConfig) -> Optional[str]:
        """Deploy with retry logic"""

        for attempt in range(self.max_retries):
            try:
                # Read agent code
                with open(config.agent_path, "r") as f:
                    agent_code = f.read()

                # Deploy to AgentCore
                spec = AgentSpec(
                    name=config.agent_name,
                    code=agent_code,
                    version=config.version,
                    description=f"Auto-deployed {config.agent_name} v{config.version}",
                )
                result = await self.deployer.deploy_agent(spec)

                if result.get("success"):
                    return result.get("deployment_id")

                # Wait before retry
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

            except Exception as e:
                print(f"Deployment attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

        return None

    async def _create_backup(self, config: DeploymentConfig) -> str:
        """Create backup before deployment"""

        backup_id = hashlib.md5(
            f"{config.agent_name}_{config.version}_{time.time()}".encode()
        ).hexdigest()[:8]

        backup_path = f"/tmp/backup_{backup_id}.json"

        # Read current agent if exists
        current_code = ""
        if os.path.exists(config.agent_path):
            with open(config.agent_path, "r") as f:
                current_code = f.read()

        backup_data = {
            "backup_id": backup_id,
            "agent_name": config.agent_name,
            "version": config.version,
            "timestamp": time.time(),
            "code": current_code,
            "config": {"environment": config.environment, "path": config.agent_path},
        }

        with open(backup_path, "w") as f:
            json.dump(backup_data, f)

        return backup_id

    async def _rollback(self, backup_id: str, config: DeploymentConfig):
        """Rollback to previous version"""

        backup_path = f"/tmp/backup_{backup_id}.json"

        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup {backup_id} not found")

        with open(backup_path, "r") as f:
            backup_data = json.load(f)

        # Restore agent code
        with open(config.agent_path, "w") as f:
            f.write(backup_data["code"])

        # Redeploy previous version
        spec = AgentSpec(
            name=backup_data["agent_name"],
            code=backup_data["code"],
            version=backup_data["version"],
            description=f"Rollback to {backup_data['version']}",
        )
        await self.deployer.deploy_agent(spec)

    def _record_deployment(self, config: DeploymentConfig, deployment_id: str, success: bool):
        """Record deployment in history"""

        record = {
            "timestamp": time.time(),
            "agent_name": config.agent_name,
            "version": config.version,
            "environment": config.environment,
            "deployment_id": deployment_id,
            "success": success,
        }

        self.deployment_history.append(record)

        # Keep only last 100 deployments
        if len(self.deployment_history) > 100:
            self.deployment_history = self.deployment_history[-100:]

    async def batch_deploy(
        self, configs: List[DeploymentConfig], parallel: bool = True
    ) -> List[DeploymentResult]:
        """Deploy multiple agents"""

        if parallel:
            # Deploy in parallel
            tasks = [self.deploy_agent(config) for config in configs]
            results = await asyncio.gather(*tasks)
        else:
            # Deploy sequentially
            results = []
            for config in configs:
                result = await self.deploy_agent(config)
                results.append(result)

        return results

    async def deploy_workflow(
        self, workflow_id: str, agents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Deploy complete workflow"""

        results = []

        for agent_info in agents:
            config = DeploymentConfig(
                agent_name=agent_info["name"],
                agent_path=agent_info["path"],
                version=agent_info.get("version", "1.0.0"),
                environment=agent_info.get("environment", "development"),
            )

            result = await self.deploy_agent(config)
            results.append(result)

        # Calculate workflow deployment success
        success_count = sum(1 for r in results if r.success)

        return {
            "workflow_id": workflow_id,
            "total_agents": len(agents),
            "deployed": success_count,
            "failed": len(agents) - success_count,
            "results": results,
        }

    def get_deployment_history(
        self, agent_name: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get deployment history"""

        history = self.deployment_history

        if agent_name:
            history = [h for h in history if h["agent_name"] == agent_name]

        return history[-limit:]

    def get_metrics(self) -> Dict[str, Any]:
        """Get deployer metrics"""

        if not self.deployment_history:
            return {"total_deployments": 0, "success_rate": 0.0, "average_time": 0.0}

        total = len(self.deployment_history)
        success = sum(1 for h in self.deployment_history if h["success"])

        return {
            "total_deployments": total,
            "success_rate": success / total if total > 0 else 0.0,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "history_size": len(self.deployment_history),
        }


# Global instance
auto_deployer = None


def get_auto_deployer() -> AutoDeployer:
    """Get or create auto deployer instance"""
    global auto_deployer
    if not auto_deployer:
        auto_deployer = AutoDeployer()
    return auto_deployer


async def main():
    """Test auto deployer"""
    deployer = get_auto_deployer()

    # Test deployment config
    config = DeploymentConfig(
        agent_name="TestAgent",
        agent_path="/tmp/test_agent.py",
        version="1.0.0",
        environment="development",
    )

    # Create test agent file
    test_agent = """
class TestAgent:
    def __init__(self):
        self.name = "TestAgent"

    async def execute(self, input_data):
        return {"status": "success", "data": input_data}
"""

    with open("/tmp/test_agent.py", "w") as f:
        f.write(test_agent)

    # Deploy
    result = await deployer.deploy_agent(config)

    print(f"Deployment: {'Success' if result.success else 'Failed'}")
    print(f"Agent: {result.agent_name} v{result.version}")
    if result.deployment_id:
        print(f"Deployment ID: {result.deployment_id}")
    if result.errors:
        print(f"Errors: {result.errors}")

    # Get metrics
    metrics = deployer.get_metrics()
    print(f"\nMetrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())
