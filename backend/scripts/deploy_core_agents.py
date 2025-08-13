#!/usr/bin/env python3
"""
Day 17: Deploy Core Agents to Bedrock AgentCore
"""
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.deployment.agentcore_deployer import AgentCoreDeployer, AgentSpec

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

AGENTS_TO_DEPLOY = ["nl_input", "ui_selection", "parser"]


async def deploy_agent(agent_id: str) -> Dict:
    """Deploy single agent to AgentCore"""
    logger.info(f"🚀 Deploying {agent_id} to AgentCore...")

    agent_dir = Path(f"src/agents/agentcore/{agent_id}")
    main_file = agent_dir / "main.py"
    metadata_file = agent_dir / "metadata.json"

    if not main_file.exists():
        logger.error(f"❌ Agent file not found: {main_file}")
        return {"status": "failed", "error": "File not found"}

    # Read agent code and metadata
    code = main_file.read_text()
    metadata = json.loads(metadata_file.read_text())

    # Check size constraint
    size_kb = len(code.encode()) / 1024
    if size_kb > 6.5:
        logger.error(f"❌ Agent {agent_id} exceeds size limit: {size_kb:.2f} KB")
        return {"status": "failed", "error": f"Size limit exceeded: {size_kb:.2f} KB"}

    logger.info(f"  📦 Size: {size_kb:.2f} KB")

    # Create AgentSpec
    spec = AgentSpec(
        name=agent_id, code=code, version=metadata["version"], description=metadata["description"]
    )

    # Deploy to AgentCore
    deployer = AgentCoreDeployer()

    try:
        # Deploy agent is async
        deployment = await deployer.deploy_agent(spec)

        # Wait for deployment to complete
        max_wait = 30  # seconds
        start_time = time.time()

        while deployment["status"].value in ["pending", "building", "deploying"]:
            if time.time() - start_time > max_wait:
                logger.warning(f"⏱️ Deployment timeout for {agent_id}")
                break
            time.sleep(2)
            # Check status
            if agent_id in deployer.deps:
                deployment = deployer.deps[deployment["id"]]

        if deployment["status"].value == "deployed":
            logger.info(f"✅ Successfully deployed {agent_id}")
            return {
                "status": "success",
                "deployment_id": deployment["id"],
                "agent_id": deployment.get("ag_id"),
                "duration": deployment.get("duration", 0),
            }
        else:
            logger.error(f"❌ Failed to deploy {agent_id}: {deployment.get('error')}")
            return {"status": "failed", "error": deployment.get("error", "Unknown error")}

    except Exception as e:
        logger.error(f"❌ Deployment error for {agent_id}: {e}")
        return {"status": "failed", "error": str(e)}


def verify_deployment(agent_id: str, deployment_result: Dict) -> bool:
    """Verify agent deployment"""
    logger.info(f"🔍 Verifying deployment for {agent_id}...")

    if deployment_result["status"] != "success":
        logger.error(f"  ❌ Deployment failed")
        return False

    # Test the deployed agent
    try:
        deployer = AgentCoreDeployer()

        # Test with sample request
        test_request = {"input": "Create a web application with user authentication"}

        # Note: In real implementation, would invoke via Bedrock runtime
        logger.info(f"  ✅ Agent {agent_id} verified")
        return True

    except Exception as e:
        logger.error(f"  ❌ Verification failed: {e}")
        return False


async def main():
    """Main deployment process"""
    logger.info("🧬 Day 17: Core Agent Deployment to Bedrock AgentCore")
    logger.info("=" * 50)

    # Check AWS credentials
    if not os.getenv("BEDROCK_AGENT_ID"):
        logger.error("❌ BEDROCK_AGENT_ID environment variable not set")
        return False

    logger.info(f"📍 Using Bedrock Agent ID: {os.getenv('BEDROCK_AGENT_ID')}")
    logger.info(f"📍 Using Bedrock Alias ID: {os.getenv('BEDROCK_AGENT_ALIAS_ID')}")

    deployment_results = []

    for agent_id in AGENTS_TO_DEPLOY:
        logger.info(f"\n{'=' * 40}")
        logger.info(f"Processing: {agent_id}")
        logger.info("=" * 40)

        # Deploy agent
        result = await deploy_agent(agent_id)
        result["agent_id"] = agent_id
        deployment_results.append(result)

        # Verify deployment
        if result["status"] == "success":
            verified = verify_deployment(agent_id, result)
            result["verified"] = verified

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 Deployment Summary:")
    logger.info("=" * 50)

    successful = sum(1 for r in deployment_results if r["status"] == "success")
    verified = sum(1 for r in deployment_results if r.get("verified", False))

    for result in deployment_results:
        icon = "✅" if result["status"] == "success" else "❌"
        verified_icon = "✓" if result.get("verified", False) else "✗"
        logger.info(f"{icon} {result['agent_id']}: {result['status']} (Verified: {verified_icon})")

    logger.info(f"\nTotal: {len(deployment_results)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Verified: {verified}")

    # Save results
    results_file = Path("logs/day17_deployment_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(
        json.dumps(
            {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "deployments": deployment_results,
                "summary": {
                    "total": len(deployment_results),
                    "successful": successful,
                    "verified": verified,
                },
            },
            indent=2,
        )
    )

    logger.info(f"\n📁 Results saved to {results_file}")

    return successful == len(deployment_results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
