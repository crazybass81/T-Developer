#!/usr/bin/env python3
"""
Migration Scheduler Script
Day 16: Migration Framework - Scheduling Script
Generated: 2025-08-13

Command-line interface for the T-Developer migration scheduler
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from migration.code_converter import CodeConverter
from migration.compatibility_checker import CompatibilityChecker
from migration.legacy_analyzer import LegacyAnalyzer
from migration.migration_scheduler import MigrationScheduler, MigrationTask, Priority


class MigrationOrchestrator:
    """Orchestrates the complete migration process"""

    def __init__(self):
        self.scheduler = MigrationScheduler()
        self.analyzer = LegacyAnalyzer()
        self.checker = CompatibilityChecker()
        self.converter = CodeConverter()

    async def run_migration(self, source_paths: List[str], dry_run: bool = False):
        """Run complete migration process"""
        print(f"🚀 Starting T-Developer Migration Process...")
        print(f"📁 Processing {len(source_paths)} agent files")

        # Step 1: Analyze legacy agents
        print("\n📊 Phase 1: Analyzing Legacy Agents...")
        analysis_results = []
        for path in source_paths:
            result = self.analyzer.analyze_file(path)
            analysis_results.append((path, result))
            print(f"  ✅ {result.agent_name}: {result.complexity.value} complexity")

        # Step 2: Check compatibility
        print("\n🔍 Phase 2: Checking Compatibility...")
        for path, analysis in analysis_results:
            with open(path, "r") as f:
                code = f.read()
            compat_result = self.checker.check_compatibility(code, analysis.agent_name)
            print(
                f"  ✅ {analysis.agent_name}: {compat_result.compatibility_level.value} compatibility"
            )

        # Step 3: Create migration tasks
        print("\n📋 Phase 3: Creating Migration Tasks...")
        task_id = 1
        for path, analysis in analysis_results:
            priority = Priority.HIGH if analysis.complexity.name == "LOW" else Priority.MEDIUM
            task = MigrationTask(
                id=f"migration_{task_id}",
                agent_name=analysis.agent_name,
                source_path=path,
                priority=priority,
                dependencies=[],
                estimated_memory_kb=analysis.performance_baseline.get("estimated_memory_kb", 1.0),
                estimated_duration_minutes=5,
            )
            self.scheduler.add_task(task)
            print(f"  📝 Created task: {task.id} ({task.priority.name} priority)")
            task_id += 1

        # Step 4: Show execution plan
        print("\n🗓️  Phase 4: Execution Plan...")
        plan = self.scheduler.create_execution_plan()
        for i, batch in enumerate(plan, 1):
            print(f"  Batch {i}: {[task.agent_name for task in batch]}")

        # Step 5: Execute migrations (or dry run)
        if dry_run:
            print("\n🧪 Dry Run Complete - No actual migrations performed")
        else:
            print("\n⚡ Phase 5: Executing Migrations...")
            results = await self.scheduler.execute_batch()

            # Show results
            completed = sum(1 for r in results if r.status.name == "COMPLETED")
            failed = sum(1 for r in results if r.status.name == "FAILED")

            print(f"\n✅ Migration Complete!")
            print(f"  Completed: {completed}")
            print(f"  Failed: {failed}")
            print(f"  Success Rate: {completed/(completed+failed)*100:.1f}%")

        # Show final progress
        progress = self.scheduler.get_migration_progress()
        print(f"\n📈 Final Progress: {progress['progress_percentage']:.1f}%")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="T-Developer Migration Scheduler")
    parser.add_argument("paths", nargs="+", help="Paths to legacy agent files")
    parser.add_argument(
        "--dry-run", action="store_true", help="Perform dry run without actual migration"
    )
    parser.add_argument(
        "--max-concurrent", type=int, default=3, help="Maximum concurrent migrations"
    )

    args = parser.parse_args()

    # Validate paths
    valid_paths = []
    for path in args.paths:
        if Path(path).exists():
            valid_paths.append(path)
        else:
            print(f"⚠️  Warning: {path} does not exist, skipping")

    if not valid_paths:
        print("❌ No valid paths found")
        return 1

    # Run migration
    orchestrator = MigrationOrchestrator()
    try:
        asyncio.run(orchestrator.run_migration(valid_paths, args.dry_run))
        return 0
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
