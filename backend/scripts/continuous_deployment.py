#!/usr/bin/env python3
"""
Continuous Deployment Script
Day 24: Phase 2 - Meta Agents
Monitors for changes and auto-deploys agents
"""

import asyncio
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.deployment.api_registry_updater import get_registry_updater
from src.deployment.auto_deployer import DeploymentConfig, get_auto_deployer
from src.deployment.validation_engine import get_validator


class ContinuousDeployment:
    """Continuous deployment orchestrator"""

    def __init__(self):
        self.auto_deployer = get_auto_deployer()
        self.validator = get_validator()
        self.registry_updater = get_registry_updater()

        # Configuration
        self.watch_dirs = ["src/agents/unified", "src/agents/meta", "src/agents/ecs-integrated"]
        self.check_interval = 10  # seconds
        self.environment = os.getenv("ENVIRONMENT", "development")

        # State tracking
        self.file_hashes: Dict[str, str] = {}
        self.deployment_queue: List[DeploymentConfig] = []
        self.running = False

    async def start(self):
        """Start continuous deployment monitoring"""

        print(f"🚀 Starting continuous deployment...")
        print(f"Environment: {self.environment}")
        print(f"Watching directories: {self.watch_dirs}")

        self.running = True

        # Initial scan
        await self._scan_agents()

        # Start monitoring loop
        try:
            while self.running:
                await self._check_for_changes()
                await self._process_deployment_queue()
                await asyncio.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n⏹ Stopping continuous deployment...")
            self.running = False

    async def _scan_agents(self):
        """Initial scan of agent files"""

        print("📂 Scanning for agents...")

        for watch_dir in self.watch_dirs:
            dir_path = Path(watch_dir)
            if not dir_path.exists():
                continue

            for agent_file in dir_path.glob("*.py"):
                if agent_file.name.startswith("__"):
                    continue

                # Calculate file hash
                file_hash = self._calculate_file_hash(agent_file)
                self.file_hashes[str(agent_file)] = file_hash

        print(f"Found {len(self.file_hashes)} agent files")

    async def _check_for_changes(self):
        """Check for changed agent files"""

        changed_files = []

        for file_path, old_hash in list(self.file_hashes.items()):
            if not Path(file_path).exists():
                # File deleted
                del self.file_hashes[file_path]
                continue

            new_hash = self._calculate_file_hash(Path(file_path))

            if new_hash != old_hash:
                changed_files.append(file_path)
                self.file_hashes[file_path] = new_hash

        # Check for new files
        for watch_dir in self.watch_dirs:
            dir_path = Path(watch_dir)
            if not dir_path.exists():
                continue

            for agent_file in dir_path.glob("*.py"):
                if agent_file.name.startswith("__"):
                    continue

                file_str = str(agent_file)
                if file_str not in self.file_hashes:
                    # New file found
                    file_hash = self._calculate_file_hash(agent_file)
                    self.file_hashes[file_str] = file_hash
                    changed_files.append(file_str)

        # Queue changed files for deployment
        for file_path in changed_files:
            await self._queue_deployment(file_path)

    async def _queue_deployment(self, file_path: str):
        """Queue agent for deployment"""

        path = Path(file_path)
        agent_name = path.stem.replace("_", "").title() + "Agent"

        # Validate before queuing
        validation = await self.validator.validate_agent(file_path, agent_name)

        if not validation["valid"]:
            print(f"❌ Validation failed for {agent_name}: {validation['errors']}")
            return

        # Create deployment config
        config = DeploymentConfig(
            agent_name=agent_name,
            agent_path=file_path,
            version=self._get_version(file_path),
            environment=self.environment,
            auto_rollback=True,
            validation_required=True,
            registry_update=True,
            backup_enabled=True,
        )

        # Check if already queued
        if not any(c.agent_path == file_path for c in self.deployment_queue):
            self.deployment_queue.append(config)
            print(f"📋 Queued {agent_name} for deployment")

    async def _process_deployment_queue(self):
        """Process pending deployments"""

        if not self.deployment_queue:
            return

        print(f"🔄 Processing {len(self.deployment_queue)} deployments...")

        # Deploy in batch
        configs = self.deployment_queue[:5]  # Process up to 5 at a time
        self.deployment_queue = self.deployment_queue[5:]

        results = await self.auto_deployer.batch_deploy(configs, parallel=True)

        # Report results
        for result in results:
            if result.success:
                print(f"✅ Deployed {result.agent_name} v{result.version}")
                print(f"   Deployment ID: {result.deployment_id}")
                print(f"   Registry updated: {result.registry_updated}")
            else:
                print(f"❌ Failed to deploy {result.agent_name}: {result.errors}")

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""

        if not file_path.exists():
            return ""

        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _get_version(self, file_path: str) -> str:
        """Extract version from file or generate"""

        # Try to extract from file
        try:
            with open(file_path, "r") as f:
                content = f.read()
                if "__version__" in content:
                    # Extract version string
                    for line in content.split("\n"):
                        if "__version__" in line:
                            parts = line.split("=")
                            if len(parts) == 2:
                                version = parts[1].strip().strip("'\"")
                                return version
        except:
            pass

        # Generate version based on timestamp
        return f"1.0.{int(time.time()) % 10000}"

    async def deploy_all(self):
        """Deploy all agents immediately"""

        print("🚀 Deploying all agents...")

        configs = []

        for file_path in self.file_hashes.keys():
            path = Path(file_path)
            agent_name = path.stem.replace("_", "").title() + "Agent"

            config = DeploymentConfig(
                agent_name=agent_name,
                agent_path=file_path,
                version=self._get_version(file_path),
                environment=self.environment,
            )
            configs.append(config)

        results = await self.auto_deployer.batch_deploy(configs, parallel=True)

        success_count = sum(1 for r in results if r.success)
        print(f"✅ Deployed {success_count}/{len(results)} agents successfully")

        return results

    async def status(self):
        """Get deployment status"""

        print("\n📊 Deployment Status")
        print("=" * 50)

        # Active agents
        active_agents = self.registry_updater.list_active_agents()
        print(f"Active agents: {len(active_agents)}")
        for agent in active_agents[:5]:
            print(f"  - {agent}")

        # Deployment metrics
        metrics = self.auto_deployer.get_metrics()
        print(f"\nDeployment metrics:")
        print(f"  Total deployments: {metrics['total_deployments']}")
        print(f"  Success rate: {metrics['success_rate']:.1%}")

        # Registry metrics
        reg_metrics = self.registry_updater.get_metrics()
        print(f"\nRegistry metrics:")
        print(f"  Total endpoints: {reg_metrics['total_endpoints']}")
        print(f"  Active agents: {reg_metrics['active_agents']}")

        # Queue status
        print(f"\nQueue: {len(self.deployment_queue)} pending")

        print("=" * 50)


async def main():
    """Main entry point"""

    cd = ContinuousDeployment()

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "deploy-all":
            await cd.deploy_all()
        elif command == "status":
            await cd.status()
        else:
            print(f"Unknown command: {command}")
            print("Usage: continuous_deployment.py [deploy-all|status]")
    else:
        # Start monitoring
        await cd.start()


if __name__ == "__main__":
    asyncio.run(main())
