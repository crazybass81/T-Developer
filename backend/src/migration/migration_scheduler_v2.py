"""🧬 Migration Scheduler <6.5KB
Day 16: Migration Framework
Orchestrates agent migration process
"""
import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

from .compatibility_checker_v2 import CompatibilityChecker
from .code_converter_v2 import CodeConverter
from .legacy_analyzer_v2 import LegacyAnalyzer


class MigrationStatus(Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    CONVERTING = "converting"
    VALIDATING = "validating"
    DEPLOYING = "deploying"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationTask:
    """Single migration task"""
    agent_name: str
    source_path: str
    target_path: str
    status: MigrationStatus = MigrationStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None
    rollback_path: Optional[str] = None


@dataclass
class MigrationPlan:
    """Migration execution plan"""
    tasks: List[MigrationTask]
    parallel_groups: List[List[str]]
    estimated_duration: float
    total_agents: int
    complexity_score: int


class MigrationScheduler:
    """Orchestrates the migration process"""
    
    def __init__(self, source_dir: str, target_dir: str):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.analyzer = LegacyAnalyzer()
        self.converter = CodeConverter()
        self.checker = CompatibilityChecker()
        
        self.tasks: Dict[str, MigrationTask] = {}
        self.completed: Set[str] = set()
        self.failed: Set[str] = set()
        
        self.logger = logging.getLogger(__name__)
        self.max_parallel = 5
        self.backup_dir = Path(target_dir) / ".backup"

    def create_plan(self) -> MigrationPlan:
        """Create migration plan"""
        # Analyze all agents
        analysis_results = self.analyzer.analyze_directory(str(self.source_dir))
        
        # Create tasks
        tasks = []
        for result in analysis_results:
            source = self.source_dir / f"{result.agent_name}.py"
            target = self.target_dir / f"{result.agent_name}_v2.py"
            
            task = MigrationTask(
                agent_name=result.agent_name,
                source_path=str(source),
                target_path=str(target),
                dependencies=self._extract_deps(result.dependencies)
            )
            tasks.append(task)
            self.tasks[result.agent_name] = task
        
        # Determine parallel groups based on dependencies
        parallel_groups = self._create_parallel_groups(tasks)
        
        # Estimate duration
        complexity_score = sum(
            1 if r.complexity.value == "low" else
            3 if r.complexity.value == "medium" else 5
            for r in analysis_results
        )
        estimated_duration = complexity_score * 2  # seconds per point
        
        return MigrationPlan(
            tasks=tasks,
            parallel_groups=parallel_groups,
            estimated_duration=estimated_duration,
            total_agents=len(tasks),
            complexity_score=complexity_score
        )
    
    def _extract_deps(self, dependencies: List[str]) -> List[str]:
        """Extract agent dependencies"""
        agent_deps = []
        for dep in dependencies:
            if 'agent' in dep.lower():
                # Extract agent name from import
                parts = dep.split('.')
                for part in parts:
                    if 'agent' in part.lower():
                        agent_deps.append(part.replace('_agent', '').replace('Agent', ''))
        return agent_deps
    
    def _create_parallel_groups(self, tasks: List[MigrationTask]) -> List[List[str]]:
        """Create parallel execution groups"""
        groups = []
        remaining = set(t.agent_name for t in tasks)
        completed = set()
        
        while remaining:
            # Find tasks with satisfied dependencies
            group = []
            for name in remaining:
                task = self.tasks[name]
                if all(dep in completed for dep in task.dependencies):
                    group.append(name)
            
            if not group:
                # Circular dependency or error
                group = list(remaining)  # Force remaining
            
            groups.append(group)
            completed.update(group)
            remaining -= set(group)
        
        return groups
    
    async def execute_plan(self, plan: MigrationPlan) -> Dict:
        """Execute migration plan"""
        start_time = time.time()
        results = {
            "total": plan.total_agents,
            "completed": 0,
            "failed": 0,
            "duration": 0,
            "details": []
        }
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Execute groups in order
        for group in plan.parallel_groups:
            # Execute tasks in parallel within group
            tasks = []
            for agent_name in group[:self.max_parallel]:
                task = self.tasks[agent_name]
                tasks.append(self._migrate_agent(task))
            
            # Wait for group completion
            group_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for agent_name, result in zip(group, group_results):
                if isinstance(result, Exception):
                    self.failed.add(agent_name)
                    results["failed"] += 1
                    results["details"].append({
                        "agent": agent_name,
                        "status": "failed",
                        "error": str(result)
                    })
                else:
                    self.completed.add(agent_name)
                    results["completed"] += 1
                    results["details"].append({
                        "agent": agent_name,
                        "status": "completed"
                    })
        
        results["duration"] = time.time() - start_time
        return results
    
    async def _migrate_agent(self, task: MigrationTask) -> bool:
        """Migrate single agent"""
        task.status = MigrationStatus.ANALYZING
        task.start_time = time.time()
        
        try:
            # Backup original if target exists
            target_path = Path(task.target_path)
            if target_path.exists():
                backup_path = self.backup_dir / target_path.name
                target_path.rename(backup_path)
                task.rollback_path = str(backup_path)
            
            # Analyze
            analysis = self.analyzer.analyze_file(task.source_path)
            if analysis.issues:
                raise Exception(f"Analysis issues: {analysis.issues}")
            
            # Convert
            task.status = MigrationStatus.CONVERTING
            success, result = self.converter.convert_file(
                task.source_path,
                task.target_path
            )
            if not success:
                raise Exception(f"Conversion failed: {result}")
            
            # Validate
            task.status = MigrationStatus.VALIDATING
            compat_result = self.checker.check_agent(task.target_path)
            if not compat_result.is_compatible:
                raise Exception(f"Compatibility issues: {compat_result.issues}")
            
            # Deploy (placeholder)
            task.status = MigrationStatus.DEPLOYING
            await asyncio.sleep(0.1)  # Simulate deployment
            
            # Complete
            task.status = MigrationStatus.COMPLETED
            task.end_time = time.time()
            return True
            
        except Exception as e:
            task.status = MigrationStatus.FAILED
            task.error = str(e)
            task.end_time = time.time()
            
            # Rollback if needed
            if task.rollback_path:
                self._rollback(task)
            
            raise e
    
    def _rollback(self, task: MigrationTask):
        """Rollback failed migration"""
        try:
            if task.rollback_path:
                backup = Path(task.rollback_path)
                target = Path(task.target_path)
                
                if target.exists():
                    target.unlink()
                if backup.exists():
                    backup.rename(target)
                
                task.status = MigrationStatus.ROLLED_BACK
        except Exception as e:
            self.logger.error(f"Rollback failed for {task.agent_name}: {e}")
    
    def get_status(self) -> Dict:
        """Get current migration status"""
        return {
            "total": len(self.tasks),
            "pending": sum(1 for t in self.tasks.values() if t.status == MigrationStatus.PENDING),
            "in_progress": sum(1 for t in self.tasks.values() if t.status in [
                MigrationStatus.ANALYZING,
                MigrationStatus.CONVERTING,
                MigrationStatus.VALIDATING,
                MigrationStatus.DEPLOYING
            ]),
            "completed": len(self.completed),
            "failed": len(self.failed),
            "tasks": {
                name: {
                    "status": task.status.value,
                    "error": task.error
                }
                for name, task in self.tasks.items()
            }
        }
    
    def generate_report(self) -> str:
        """Generate migration report"""
        report = []
        report.append("=" * 50)
        report.append("MIGRATION REPORT")
        report.append("=" * 50)
        
        status = self.get_status()
        report.append(f"Total Agents: {status['total']}")
        report.append(f"Completed: {status['completed']}")
        report.append(f"Failed: {status['failed']}")
        report.append("")
        
        if self.failed:
            report.append("Failed Migrations:")
            for name in self.failed:
                task = self.tasks[name]
                report.append(f"  - {name}: {task.error}")
        
        if self.completed:
            report.append("\nSuccessful Migrations:")
            for name in sorted(self.completed):
                task = self.tasks[name]
                duration = (task.end_time - task.start_time) if task.end_time else 0
                report.append(f"  - {name} ({duration:.1f}s)")
        
        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    scheduler = MigrationScheduler(
        source_dir="backend/src/agents/legacy",
        target_dir="backend/src/agents/migrated"
    )
    
    # Create plan
    plan = scheduler.create_plan()
    print(f"Migration Plan: {plan.total_agents} agents")
    print(f"Estimated Duration: {plan.estimated_duration}s")
    
    # Execute migration
    async def run():
        results = await scheduler.execute_plan(plan)
        print(f"Results: {json.dumps(results, indent=2)}")
        print(scheduler.generate_report())
    
    asyncio.run(run())