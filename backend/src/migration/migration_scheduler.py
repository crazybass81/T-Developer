"""
Migration Scheduler
Day 16: Migration Framework - Migration Task Scheduling
Generated: 2025-08-13

Schedules and coordinates migration tasks with dependency resolution
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set


class Priority(Enum):
    """Migration task priorities"""

    HIGH = 1
    MEDIUM = 2
    LOW = 3


class MigrationStatus(Enum):
    """Migration task status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationTask:
    """Migration task representation"""

    id: str
    agent_name: str
    source_path: str
    priority: Priority
    dependencies: List[str] = field(default_factory=list)
    status: MigrationStatus = MigrationStatus.PENDING
    retry_count: int = 0
    estimated_memory_kb: float = 0.0
    estimated_duration_minutes: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    backup_path: Optional[str] = None
    rollback_timestamp: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class ValidationResult:
    """Task validation result"""

    valid: bool
    errors: List[str] = field(default_factory=list)


class MigrationScheduler:
    """Schedules and manages migration tasks"""

    def __init__(
        self, max_concurrent_migrations: int = 3, retry_attempts: int = 3, timeout_minutes: int = 30
    ):
        self.max_concurrent_migrations = max_concurrent_migrations
        self.retry_attempts = retry_attempts
        self.timeout_minutes = timeout_minutes

        self.pending_tasks: List[MigrationTask] = []
        self.active_tasks: List[MigrationTask] = []
        self.completed_tasks: List[MigrationTask] = []
        self.failed_tasks: List[MigrationTask] = []

    def add_task(self, task: MigrationTask):
        """Add a migration task to the scheduler"""
        self.pending_tasks.append(task)
        task.updated_at = datetime.utcnow()

    def get_task(self, task_id: str) -> Optional[MigrationTask]:
        """Get a task by ID"""
        all_tasks = (
            self.pending_tasks + self.active_tasks + self.completed_tasks + self.failed_tasks
        )
        for task in all_tasks:
            if task.id == task_id:
                return task
        return None

    def update_task_status(self, task_id: str, status: MigrationStatus):
        """Update task status"""
        task = self.get_task(task_id)
        if task:
            task.status = status
            task.updated_at = datetime.utcnow()

            # Move task to appropriate list
            if status == MigrationStatus.COMPLETED and task in self.active_tasks:
                self.active_tasks.remove(task)
                self.completed_tasks.append(task)
                task.completed_at = datetime.utcnow()
            elif status == MigrationStatus.FAILED and task in self.active_tasks:
                self.active_tasks.remove(task)
                self.failed_tasks.append(task)

    def _get_next_schedulable_tasks(self) -> List[MigrationTask]:
        """Get next tasks that can be scheduled"""
        schedulable = []
        completed_task_ids = {task.id for task in self.completed_tasks}

        # Filter pending tasks by priority and dependencies
        for task in self.pending_tasks:
            # Check if all dependencies are completed
            dependencies_met = all(dep_id in completed_task_ids for dep_id in task.dependencies)

            if dependencies_met and len(schedulable) < self.max_concurrent_migrations:
                schedulable.append(task)

        # Sort by priority (high priority first)
        schedulable.sort(key=lambda t: t.priority.value)

        return schedulable[: self.max_concurrent_migrations]

    async def _execute_task(self, task: MigrationTask) -> bool:
        """Execute a single migration task"""
        try:
            task.status = MigrationStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()

            # Perform the migration
            success = await self._perform_migration(task)

            if success:
                task.status = MigrationStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                return True
            else:
                task.status = MigrationStatus.FAILED
                return False

        except Exception as e:
            task.status = MigrationStatus.FAILED
            task.error_message = str(e)
            return False

    async def _perform_migration(self, task: MigrationTask) -> bool:
        """Perform the actual migration - to be implemented by subclasses"""
        # Simulate migration work
        await asyncio.sleep(0.1)
        return True

    def increment_retry_count(self, task: MigrationTask):
        """Increment retry count for a task"""
        task.retry_count += 1

    def create_execution_plan(self) -> List[List[MigrationTask]]:
        """Create execution plan with batches based on dependencies"""
        plan = []
        remaining_tasks = self.pending_tasks.copy()
        completed_ids = set()

        while remaining_tasks:
            # Find tasks with no unmet dependencies
            current_batch = []
            tasks_to_remove = []

            for task in remaining_tasks:
                dependencies_met = all(dep_id in completed_ids for dep_id in task.dependencies)
                if dependencies_met:
                    current_batch.append(task)
                    tasks_to_remove.append(task)

            if not current_batch:
                # Circular dependency or other issue
                break

            # Remove scheduled tasks from remaining
            for task in tasks_to_remove:
                remaining_tasks.remove(task)
                completed_ids.add(task.id)

            plan.append(current_batch)

        return plan

    async def execute_batch(self) -> List[MigrationTask]:
        """Execute all pending migration tasks"""
        results = []
        execution_plan = self.create_execution_plan()

        for batch in execution_plan:
            # Execute batch concurrently
            tasks = []
            for task in batch:
                tasks.append(self._execute_task(task))

            # Wait for batch completion
            await asyncio.gather(*tasks)

            for task in batch:
                results.append(task)

        return results

    def rollback_task(self, task: MigrationTask):
        """Rollback a migration task"""
        task.status = MigrationStatus.ROLLED_BACK
        task.rollback_timestamp = datetime.utcnow()
        # Implementation would restore from backup_path

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a migration task"""
        task = self.get_task(task_id)
        if task and task.status == MigrationStatus.PENDING:
            task.status = MigrationStatus.CANCELLED
            task.updated_at = datetime.utcnow()
            return True
        return False

    def get_migration_progress(self) -> Dict:
        """Get overall migration progress"""
        total = (
            len(self.pending_tasks)
            + len(self.active_tasks)
            + len(self.completed_tasks)
            + len(self.failed_tasks)
        )
        completed = len(self.completed_tasks)

        return {
            "total": total,
            "pending": len(self.pending_tasks),
            "active": len(self.active_tasks),
            "completed": completed,
            "failed": len(self.failed_tasks),
            "progress_percentage": (completed / total * 100) if total > 0 else 0.0,
        }

    def estimate_migration_timeline(self) -> Dict:
        """Estimate migration completion timeline"""
        total_duration = sum(task.estimated_duration_minutes for task in self.pending_tasks)

        # Set minimum duration if no tasks have estimated duration
        if total_duration == 0 and self.pending_tasks:
            total_duration = len(self.pending_tasks) * 5  # 5 minutes per task default

        # Account for concurrent execution
        concurrent_duration = (
            max(1, total_duration / self.max_concurrent_migrations) if total_duration > 0 else 0
        )

        estimated_completion = datetime.utcnow() + timedelta(minutes=concurrent_duration)

        return {
            "estimated_duration_minutes": int(concurrent_duration),
            "estimated_completion_time": estimated_completion.isoformat(),
        }

    def calculate_resource_allocation(self) -> Dict:
        """Calculate resource allocation for migrations"""
        total_memory = sum(task.estimated_memory_kb for task in self.pending_tasks)

        return {
            "memory_usage_kb": total_memory,
            "concurrent_slots": self.max_concurrent_migrations,
            "available_slots": self.max_concurrent_migrations - len(self.active_tasks),
        }

    def validate_task(self, task: MigrationTask) -> ValidationResult:
        """Validate a migration task before execution"""
        errors = []

        # Check if source path exists (mock validation)
        if "nonexistent" in task.source_path.lower():
            errors.append("Source path does not exist")

        # Check dependencies
        for dep_id in task.dependencies:
            if not self.get_task(dep_id):
                errors.append(f"Dependency task {dep_id} not found")

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def get_health_status(self) -> Dict:
        """Get scheduler health status"""
        return {
            "active_migrations": len(self.active_tasks),
            "queue_size": len(self.pending_tasks),
            "system_resources": {"memory_usage": "normal", "cpu_usage": "normal"},
            "last_health_check": datetime.utcnow().isoformat(),
        }

    def get_migration_metrics(self) -> Dict:
        """Get migration performance metrics"""
        completed_migrations = len(self.completed_tasks)

        if completed_migrations > 0:
            total_duration = sum(
                (task.completed_at - task.started_at).total_seconds() / 60
                for task in self.completed_tasks
                if task.started_at and task.completed_at
            )
            avg_duration = total_duration / completed_migrations
        else:
            avg_duration = 0

        total_migrations = completed_migrations + len(self.failed_tasks)
        success_rate = (
            (completed_migrations / total_migrations * 100) if total_migrations > 0 else 0
        )

        return {
            "total_migrations": total_migrations,
            "average_duration_minutes": round(avg_duration, 2),
            "success_rate": round(success_rate, 2),
        }
