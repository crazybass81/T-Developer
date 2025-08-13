"""
Test suite for Migration Scheduler
Day 16: Migration Framework - TDD Implementation
Generated: 2025-08-13

Testing requirements:
1. Priority-based migration scheduling
2. Dependency graph resolution
3. Batch migration coordination
4. Rollback and recovery mechanisms
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.migration.migration_scheduler import (
    MigrationScheduler,
    MigrationStatus,
    MigrationTask,
    Priority,
)


class TestMigrationScheduler:
    """Test suite for migration scheduler"""

    @pytest.fixture
    def scheduler(self):
        return MigrationScheduler(max_concurrent_migrations=3, retry_attempts=3, timeout_minutes=30)

    @pytest.fixture
    def sample_migration_tasks(self):
        return [
            MigrationTask(
                id="task1",
                agent_name="nl_input_agent",
                source_path="/path/to/nl_input.py",
                priority=Priority.HIGH,
                dependencies=[],
            ),
            MigrationTask(
                id="task2",
                agent_name="parser_agent",
                source_path="/path/to/parser.py",
                priority=Priority.MEDIUM,
                dependencies=["task1"],
            ),
            MigrationTask(
                id="task3",
                agent_name="generation_agent",
                source_path="/path/to/generation.py",
                priority=Priority.LOW,
                dependencies=["task1", "task2"],
            ),
        ]

    def test_add_migration_task(self, scheduler):
        """Test adding migration tasks to scheduler"""
        task = MigrationTask(
            id="test_task",
            agent_name="test_agent",
            source_path="/path/to/test.py",
            priority=Priority.HIGH,
        )

        scheduler.add_task(task)

        assert len(scheduler.pending_tasks) == 1
        assert scheduler.pending_tasks[0].id == "test_task"
        assert scheduler.pending_tasks[0].status == MigrationStatus.PENDING

    def test_priority_based_scheduling(self, scheduler, sample_migration_tasks):
        """Test priority-based task scheduling"""
        for task in sample_migration_tasks:
            scheduler.add_task(task)

        # Should schedule high priority first
        next_tasks = scheduler._get_next_schedulable_tasks()

        assert len(next_tasks) > 0
        assert next_tasks[0].priority == Priority.HIGH
        assert next_tasks[0].agent_name == "nl_input_agent"

    def test_dependency_resolution(self, scheduler, sample_migration_tasks):
        """Test dependency graph resolution"""
        for task in sample_migration_tasks:
            scheduler.add_task(task)

        # task2 depends on task1, so task1 should be scheduled first
        schedulable = scheduler._get_next_schedulable_tasks()

        # Only task1 should be schedulable initially (no dependencies)
        assert len(schedulable) == 1
        assert schedulable[0].id == "task1"

    def test_concurrent_migration_limit(self, scheduler, sample_migration_tasks):
        """Test concurrent migration limit enforcement"""
        # Set up 5 independent tasks (no dependencies)
        independent_tasks = []
        for i in range(5):
            task = MigrationTask(
                id=f"task_{i}",
                agent_name=f"agent_{i}",
                source_path=f"/path/to/agent_{i}.py",
                priority=Priority.MEDIUM,
                dependencies=[],
            )
            independent_tasks.append(task)
            scheduler.add_task(task)

        # Should only schedule up to max_concurrent_migrations
        schedulable = scheduler._get_next_schedulable_tasks()

        assert len(schedulable) <= scheduler.max_concurrent_migrations

    @pytest.mark.asyncio
    async def test_execute_migration_task(self, scheduler):
        """Test execution of a single migration task"""
        task = MigrationTask(
            id="execute_test",
            agent_name="test_agent",
            source_path="/path/to/test.py",
            priority=Priority.HIGH,
        )

        with patch.object(scheduler, "_perform_migration", return_value=True) as mock_migrate:
            result = await scheduler._execute_task(task)

            assert result
            assert task.status == MigrationStatus.COMPLETED
            mock_migrate.assert_called_once_with(task)

    @pytest.mark.asyncio
    async def test_migration_failure_handling(self, scheduler):
        """Test handling of migration failures"""
        task = MigrationTask(
            id="failure_test",
            agent_name="failing_agent",
            source_path="/path/to/failing.py",
            priority=Priority.HIGH,
        )

        with patch.object(
            scheduler, "_perform_migration", side_effect=Exception("Migration failed")
        ):
            result = await scheduler._execute_task(task)

            assert not result
            assert task.status == MigrationStatus.FAILED
            assert task.retry_count == 0  # First attempt

    @pytest.mark.asyncio
    async def test_retry_mechanism(self, scheduler):
        """Test retry mechanism for failed migrations"""
        task = MigrationTask(
            id="retry_test",
            agent_name="retry_agent",
            source_path="/path/to/retry.py",
            priority=Priority.HIGH,
        )

        # Fail first two attempts, succeed on third
        call_count = 0

        def mock_migration(task):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Migration failed")
            return True

        with patch.object(scheduler, "_perform_migration", side_effect=mock_migration):
            # First failure
            await scheduler._execute_task(task)
            assert task.status == MigrationStatus.FAILED
            assert task.retry_count == 0

            # Manually increment retry count to simulate retry logic
            scheduler.increment_retry_count(task)

            # Retry
            task.status = MigrationStatus.PENDING  # Reset for retry
            await scheduler._execute_task(task)
            assert task.status == MigrationStatus.FAILED
            assert task.retry_count == 1

            # Manually increment retry count again
            scheduler.increment_retry_count(task)

            # Final success
            task.status = MigrationStatus.PENDING
            result = await scheduler._execute_task(task)
            assert result
            assert task.status == MigrationStatus.COMPLETED

    def test_batch_migration_planning(self, scheduler, sample_migration_tasks):
        """Test batch migration planning with dependencies"""
        for task in sample_migration_tasks:
            scheduler.add_task(task)

        execution_plan = scheduler.create_execution_plan()

        assert isinstance(execution_plan, list)
        assert len(execution_plan) >= 1  # At least one batch

        # First batch should only contain tasks with no dependencies
        first_batch = execution_plan[0]
        assert len(first_batch) == 1
        assert first_batch[0].id == "task1"

    @pytest.mark.asyncio
    async def test_full_batch_execution(self, scheduler, sample_migration_tasks):
        """Test full batch migration execution"""
        for task in sample_migration_tasks:
            scheduler.add_task(task)

        with patch.object(scheduler, "_perform_migration", return_value=True):
            results = await scheduler.execute_batch()

            assert len(results) == 3
            assert all(result.status == MigrationStatus.COMPLETED for result in results)

    def test_rollback_capability(self, scheduler):
        """Test rollback capability for failed migrations"""
        task = MigrationTask(
            id="rollback_test",
            agent_name="rollback_agent",
            source_path="/path/to/rollback.py",
            priority=Priority.HIGH,
        )

        # Simulate partial migration
        task.status = MigrationStatus.IN_PROGRESS
        task.backup_path = "/backup/rollback.py"

        scheduler.rollback_task(task)

        assert task.status == MigrationStatus.ROLLED_BACK
        assert task.rollback_timestamp is not None

    def test_migration_progress_tracking(self, scheduler, sample_migration_tasks):
        """Test migration progress tracking"""
        for task in sample_migration_tasks:
            scheduler.add_task(task)

        # Initially all pending
        progress = scheduler.get_migration_progress()

        assert progress["total"] == 3
        assert progress["pending"] == 3
        assert progress["completed"] == 0
        assert progress["failed"] == 0
        assert progress["progress_percentage"] == 0.0

    def test_task_status_updates(self, scheduler):
        """Test task status update notifications"""
        task = MigrationTask(
            id="status_test",
            agent_name="status_agent",
            source_path="/path/to/status.py",
            priority=Priority.HIGH,
        )

        scheduler.add_task(task)

        # Update status
        scheduler.update_task_status(task.id, MigrationStatus.IN_PROGRESS)

        updated_task = scheduler.get_task(task.id)
        assert updated_task.status == MigrationStatus.IN_PROGRESS
        assert updated_task.updated_at is not None

    def test_migration_timeline_estimation(self, scheduler, sample_migration_tasks):
        """Test migration timeline estimation"""
        for task in sample_migration_tasks:
            scheduler.add_task(task)

        timeline = scheduler.estimate_migration_timeline()

        assert isinstance(timeline, dict)
        assert "estimated_duration_minutes" in timeline
        assert "estimated_completion_time" in timeline
        assert timeline["estimated_duration_minutes"] > 0

    def test_resource_allocation(self, scheduler):
        """Test resource allocation for migrations"""
        # Add many tasks to test resource allocation
        tasks = []
        for i in range(10):
            task = MigrationTask(
                id=f"resource_task_{i}",
                agent_name=f"resource_agent_{i}",
                source_path=f"/path/to/resource_{i}.py",
                priority=Priority.MEDIUM if i % 2 == 0 else Priority.LOW,
                estimated_memory_kb=1.5,
                estimated_duration_minutes=5,
            )
            tasks.append(task)
            scheduler.add_task(task)

        allocation = scheduler.calculate_resource_allocation()

        assert "memory_usage_kb" in allocation
        assert "concurrent_slots" in allocation
        assert allocation["concurrent_slots"] <= scheduler.max_concurrent_migrations

    def test_migration_validation_before_execution(self, scheduler):
        """Test validation before migration execution"""
        task = MigrationTask(
            id="validation_test",
            agent_name="validation_agent",
            source_path="/nonexistent/path.py",  # Invalid path
            priority=Priority.HIGH,
        )

        scheduler.add_task(task)

        validation_result = scheduler.validate_task(task)

        assert not validation_result.valid
        assert len(validation_result.errors) > 0
        assert "path" in str(validation_result.errors).lower()

    def test_migration_cancellation(self, scheduler):
        """Test migration task cancellation"""
        task = MigrationTask(
            id="cancel_test",
            agent_name="cancel_agent",
            source_path="/path/to/cancel.py",
            priority=Priority.HIGH,
        )

        scheduler.add_task(task)

        # Cancel the task
        success = scheduler.cancel_task(task.id)

        assert success
        cancelled_task = scheduler.get_task(task.id)
        assert cancelled_task.status == MigrationStatus.CANCELLED

    def test_health_check_during_migration(self, scheduler):
        """Test health check during migration process"""
        health = scheduler.get_health_status()

        assert isinstance(health, dict)
        assert "active_migrations" in health
        assert "queue_size" in health
        assert "system_resources" in health
        assert "last_health_check" in health

    def test_migration_metrics_collection(self, scheduler):
        """Test collection of migration metrics"""
        # Add and complete some tasks
        completed_task = MigrationTask(
            id="metrics_test",
            agent_name="metrics_agent",
            source_path="/path/to/metrics.py",
            priority=Priority.HIGH,
        )

        completed_task.status = MigrationStatus.COMPLETED
        completed_task.started_at = datetime.utcnow() - timedelta(minutes=5)
        completed_task.completed_at = datetime.utcnow()

        scheduler.completed_tasks.append(completed_task)

        metrics = scheduler.get_migration_metrics()

        assert "total_migrations" in metrics
        assert "average_duration_minutes" in metrics
        assert "success_rate" in metrics
        assert metrics["total_migrations"] == 1
