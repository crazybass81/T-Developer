#!/usr/bin/env python3
"""
Day 17: Core Agent Migration Script
Migrates NL Input, UI Selection, and Parser agents to AgentCore
"""
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.deployment.agentcore_deployer import AgentCoreDeployer
from src.deployment.deployment_tracker import DeploymentTracker
from src.deployment.rollback_manager import RollbackManager
from src.migration.code_converter_v2 import CodeConverter
from src.migration.compatibility_checker_v2 import CompatibilityChecker
from src.migration.legacy_analyzer_v2 import LegacyAnalyzer
from src.migration.migration_scheduler_v2 import MigrationScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Core agents to migrate
CORE_AGENTS = {
    "nl_input": {
        "source": "src/agents/unified/nl_input/agent.py",
        "name": "NL Input Agent",
        "description": "Natural Language Input Processing Agent",
    },
    "ui_selection": {
        "source": "src/agents/unified/ui_selection/agent.py",
        "name": "UI Selection Agent",
        "description": "UI Component Selection Agent",
    },
    "parser": {
        "source": "src/agents/unified/parser/agent.py",
        "name": "Parser Agent",
        "description": "Requirement Parser Agent",
    },
}


def migrate_agent(agent_id: str, agent_config: Dict) -> Dict:
    """Migrate a single agent to AgentCore format"""
    logger.info(f"🚀 Starting migration for {agent_config['name']}")

    source_path = Path(agent_config["source"])
    target_dir = Path("src/agents/agentcore") / agent_id
    target_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "agent_id": agent_id,
        "name": agent_config["name"],
        "status": "pending",
        "details": {},
    }

    try:
        # Step 1: Analyze legacy code
        logger.info(f"📊 Analyzing {agent_config['name']}...")
        analyzer = LegacyAnalyzer()
        analysis = analyzer.analyze_file(str(source_path))
        result["details"]["analysis"] = analysis

        # Step 2: Convert to AgentCore format
        logger.info(f"🔄 Converting {agent_config['name']}...")
        converter = CodeConverter()
        # Read source code first
        source_code = source_path.read_text()
        converted_code = converter.convert_to_agentcore(source_code)

        # Write converted code
        target_file = target_dir / "main.py"
        target_file.write_text(converted_code)
        result["details"]["target_path"] = str(target_file)

        # Step 3: Check compatibility
        logger.info(f"✅ Validating {agent_config['name']}...")
        checker = CompatibilityChecker()
        compatibility_result = checker.check_agent(str(target_file))

        # Convert to dict format
        compatibility = {
            "is_compatible": compatibility_result.is_compatible,
            "size_kb": compatibility_result.memory_usage,
            "instantiation_us": compatibility_result.metrics.get("instantiation_us", 0.5),
            "issues": compatibility_result.issues,
        }
        result["details"]["compatibility"] = compatibility

        if not compatibility["is_compatible"]:
            raise ValueError(f"Compatibility check failed: {compatibility['issues']}")

        # Step 4: Create AgentCore metadata
        metadata = {
            "agent_id": agent_id,
            "name": agent_config["name"],
            "description": agent_config["description"],
            "version": "1.0.0",
            "size_kb": compatibility["size_kb"],
            "instantiation_us": compatibility.get("instantiation_us", 0.5),
            "dependencies": analysis.get("dependencies", []),
            "created_at": "2025-08-15T00:00:00Z",
        }

        metadata_file = target_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))

        result["status"] = "success"
        result["details"]["metadata"] = metadata
        logger.info(f"✅ Successfully migrated {agent_config['name']}")

    except Exception as e:
        logger.error(f"❌ Failed to migrate {agent_config['name']}: {e}")
        result["status"] = "failed"
        result["details"]["error"] = str(e)

    return result


def deploy_to_agentcore(results: List[Dict]) -> Dict:
    """Deploy migrated agents to AgentCore"""
    logger.info("🚀 Deploying agents to AgentCore...")

    deployment_results = {"total": len(results), "successful": 0, "failed": 0, "agents": []}

    deployer = AgentCoreDeployer()
    tracker = DeploymentTracker()

    for result in results:
        if result["status"] != "success":
            logger.warning(f"⏭️ Skipping {result['name']} (migration failed)")
            deployment_results["failed"] += 1
            continue

        try:
            # Deploy to AgentCore
            agent_dir = Path(result["details"]["target_path"]).parent
            # Create AgentSpec for deployment
            from src.deployment.agentcore_deployer import AgentSpec

            spec = AgentSpec(
                name=result["agent_id"],
                code=Path(result["details"]["target_path"]).read_text(),
                version=result["details"]["metadata"]["version"],
                description=result["details"]["metadata"]["description"],
            )
            deployment = deployer.deploy_agent(spec)

            # Track deployment
            tracker.track_deployment(result["agent_id"], deployment)

            deployment_results["successful"] += 1
            deployment_results["agents"].append(
                {
                    "agent_id": result["agent_id"],
                    "name": result["name"],
                    "deployment_id": deployment.get("deployment_id"),
                    "status": "deployed",
                }
            )

            logger.info(f"✅ Deployed {result['name']} to AgentCore")

        except Exception as e:
            logger.error(f"❌ Failed to deploy {result['name']}: {e}")
            deployment_results["failed"] += 1

    return deployment_results


def main():
    """Main migration process"""
    logger.info("🧬 Day 17: Core Agent Migration")
    logger.info("=" * 50)

    # Create migration scheduler
    scheduler = MigrationScheduler(
        source_dir="src/agents/unified", target_dir="src/agents/agentcore"
    )

    # Migrate all core agents
    migration_results = []
    for agent_id, agent_config in CORE_AGENTS.items():
        result = migrate_agent(agent_id, agent_config)
        migration_results.append(result)

    # Summary of migration
    logger.info("\n📊 Migration Summary:")
    for result in migration_results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        logger.info(f"{status_icon} {result['name']}: {result['status']}")

    # Deploy to AgentCore
    deployment_results = deploy_to_agentcore(migration_results)

    # Final summary
    logger.info("\n🎯 Deployment Summary:")
    logger.info(f"Total agents: {deployment_results['total']}")
    logger.info(f"Successfully deployed: {deployment_results['successful']}")
    logger.info(f"Failed: {deployment_results['failed']}")

    # Save results
    results_file = Path("logs/day17_migration_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(
        json.dumps(
            {"migration_results": migration_results, "deployment_results": deployment_results},
            indent=2,
        )
    )

    logger.info(f"\n📁 Results saved to {results_file}")

    return deployment_results["failed"] == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
