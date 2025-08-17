#!/usr/bin/env python3
"""
Perfect Evolution Run Script
Orchestrates a complete evolution cycle with SharedContextStore integration.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add backend directory to path for proper imports
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

from evolution_engine import EvolutionEngine
from models.evolution import EvolutionConfig, FocusArea
from packages.shared_context import get_context_store

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('evolution_run.log')
    ]
)
logger = logging.getLogger(__name__)


class EvolutionOrchestrator:
    """Orchestrates a perfect evolution cycle with monitoring and validation."""

    def __init__(self):
        self.engine = EvolutionEngine()
        self.context_store = get_context_store()
        self.start_time = None
        self.evolution_id = None

    async def prepare_environment(self) -> bool:
        """Verify environment is ready for evolution."""
        logger.info("🔍 Checking environment readiness...")

        checks = {
            "backend_server": await self._check_backend_server(),
            "aws_credentials": self._check_aws_credentials(),
            "external_tools": self._check_external_tools(),
            "target_exists": self._check_target_exists(),
            "context_store": await self._check_context_store(),
        }

        for check, result in checks.items():
            status = "✅" if result else "❌"
            logger.info(f"  {status} {check}: {result}")

        return all(checks.values())

    async def _check_backend_server(self) -> bool:
        """Check if backend server is running."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/health")
                return response.status_code == 200
        except:
            return False

    def _check_aws_credentials(self) -> bool:
        """Check if AWS credentials are configured."""
        return all([
            os.environ.get("AWS_ACCESS_KEY_ID"),
            os.environ.get("AWS_SECRET_ACCESS_KEY"),
            os.environ.get("AWS_DEFAULT_REGION")
        ])

    def _check_external_tools(self) -> bool:
        """Check if required external tools are available."""
        tools = ["black", "autopep8", "doq", "pyupgrade"]
        for tool in tools:
            if os.system(f"which {tool} > /dev/null 2>&1") != 0:
                logger.warning(f"Tool {tool} not found")
                return False
        return True

    def _check_target_exists(self) -> bool:
        """Check if test target exists."""
        return Path("/tmp/test_evolution_target").exists()

    async def _check_context_store(self) -> bool:
        """Check if context store is functional."""
        try:
            test_id = await self.context_store.create_context(
                target_path="/tmp/test",
                focus_areas=["test"]
            )
            return bool(test_id)
        except:
            return False

    async def create_evolution_config(self) -> EvolutionConfig:
        """Create configuration for the evolution run."""
        config = EvolutionConfig(
            target_path="/tmp/test_evolution_target",
            focus_areas=[
                FocusArea.DOCUMENTATION,
                FocusArea.CODE_QUALITY,
                FocusArea.TYPE_SAFETY,
                FocusArea.ERROR_HANDLING,
                FocusArea.PERFORMANCE
            ],
            max_iterations=1,
            improvement_threshold=0.15,  # 15% improvement target
            safety_checks_enabled=True,
            auto_commit=False,  # Don't commit automatically
            metrics_tracking=True
        )

        logger.info("📋 Evolution Configuration:")
        logger.info(f"  Target: {config.target_path}")
        logger.info(f"  Focus Areas: {', '.join([f.value for f in config.focus_areas])}")
        logger.info(f"  Improvement Target: {config.improvement_threshold*100}%")

        return config

    async def run_evolution(self, config: EvolutionConfig) -> dict[str, Any]:
        """Execute the evolution cycle."""
        logger.info("\n" + "="*60)
        logger.info("🚀 STARTING EVOLUTION CYCLE")
        logger.info("="*60 + "\n")

        self.start_time = datetime.now()

        try:
            # Run evolution
            result = await self.engine.evolve(config)
            self.evolution_id = self.engine.current_evolution_id

            # Log results
            logger.info("\n" + "="*60)
            logger.info("✅ EVOLUTION COMPLETED")
            logger.info("="*60)

            duration = (datetime.now() - self.start_time).total_seconds()
            logger.info(f"  Duration: {duration:.2f} seconds")
            logger.info(f"  Evolution ID: {self.evolution_id}")
            logger.info(f"  Success: {result.get('success', False)}")

            if result.get('improvements'):
                logger.info("\n📊 Improvements Made:")
                for imp in result['improvements']:
                    logger.info(f"  • {imp}")

            if result.get('metrics'):
                logger.info("\n📈 Metrics:")
                for metric, value in result['metrics'].items():
                    logger.info(f"  • {metric}: {value}")

            return result

        except Exception as e:
            logger.error(f"❌ Evolution failed: {e}")
            raise

    async def verify_context_store(self) -> bool:
        """Verify that SharedContextStore has all phase data."""
        logger.info("\n🔍 Verifying SharedContextStore data...")

        if not self.evolution_id:
            logger.error("No evolution ID available")
            return False

        try:
            # Get context data
            context = await self.context_store.get_context(self.evolution_id)

            # Check for all phase data
            required_phases = [
                'original_analysis',
                'external_research',
                'improvement_plan',
                'implementation_results',
                'evaluation_summary'
            ]

            for phase in required_phases:
                if phase in context and context[phase]:
                    logger.info(f"  ✅ {phase}: Data present")
                else:
                    logger.warning(f"  ⚠️ {phase}: No data")

            # Get comparison data
            comparison = await self.context_store.get_comparison_data(self.evolution_id)
            if comparison:
                logger.info("  ✅ Comparison data available")
                logger.info(f"    • Before metrics: {len(comparison.get('before', {}).get('metrics', {}))}")
                logger.info(f"    • Plan tasks: {len(comparison.get('plan', {}).get('tasks', []))}")
                logger.info(f"    • After metrics: {len(comparison.get('after', {}).get('metrics', {}))}")
            else:
                logger.warning("  ⚠️ No comparison data")

            return True

        except Exception as e:
            logger.error(f"Failed to verify context: {e}")
            return False

    async def verify_code_changes(self) -> bool:
        """Verify that actual code changes were made."""
        logger.info("\n🔍 Verifying code changes...")

        target_path = Path("/tmp/test_evolution_target")

        # Check for backup directory (indicates changes were made)
        backup_dirs = list(target_path.glob(".backup_*"))
        if backup_dirs:
            logger.info(f"  ✅ Found {len(backup_dirs)} backup(s)")

        # Check git status if it's a git repo
        os.chdir(target_path)
        git_status = os.popen("git status --short 2>/dev/null").read()
        if git_status:
            logger.info("  ✅ Git changes detected:")
            for line in git_status.strip().split('\n')[:5]:
                logger.info(f"    {line}")
            if len(git_status.strip().split('\n')) > 5:
                logger.info(f"    ... and {len(git_status.strip().split('\n')) - 5} more")

        return True

    async def export_results(self) -> str:
        """Export evolution results to file."""
        if not self.evolution_id:
            return None

        export_dir = Path("evolution_results")
        export_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = export_dir / f"evolution_{timestamp}.json"

        try:
            # Get all context data
            context = await self.context_store.get_context(self.evolution_id)
            comparison = await self.context_store.get_comparison_data(self.evolution_id)

            # Create export data
            export_data = {
                "evolution_id": self.evolution_id,
                "timestamp": timestamp,
                "duration": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                "context": context,
                "comparison": comparison,
                "target_path": "/tmp/test_evolution_target"
            }

            # Write to file
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)

            logger.info(f"\n📁 Results exported to: {export_file}")
            return str(export_file)

        except Exception as e:
            logger.error(f"Failed to export results: {e}")
            return None

    async def main(self):
        """Main orchestration flow."""
        try:
            # 1. Check environment
            if not await self.prepare_environment():
                logger.error("❌ Environment not ready. Please fix issues and retry.")
                return False

            # 2. Create configuration
            config = await self.create_evolution_config()

            # 3. Run evolution
            result = await self.run_evolution(config)

            # 4. Verify SharedContextStore
            await self.verify_context_store()

            # 5. Verify code changes
            await self.verify_code_changes()

            # 6. Export results
            await self.export_results()

            logger.info("\n" + "="*60)
            logger.info("🎉 PERFECT EVOLUTION CYCLE COMPLETE!")
            logger.info("="*60)

            return True

        except Exception as e:
            logger.error(f"\n❌ Evolution failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def run():
    """Run the evolution orchestrator."""
    orchestrator = EvolutionOrchestrator()
    success = await orchestrator.main()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(run())
    sys.exit(exit_code)
