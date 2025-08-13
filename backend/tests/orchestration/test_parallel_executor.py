"""Tests for Parallel Executor"""
import asyncio
import time

import pytest

from src.orchestration.parallel_executor import ExecutionResult, ExecutionTask, ParallelExecutor


class TestParallelExecutor:
    def test_executor_initialization(self):
        """Test parallel executor initialization"""
        executor = ParallelExecutor(max_workers=5)
        assert executor.max_workers == 5
        assert executor.thread_pool is not None
        assert executor.process_pool is None
        assert executor.execution_stats["total"] == 0

    @pytest.mark.asyncio
    async def test_async_execution_success(self):
        """Test successful async task execution"""
        executor = ParallelExecutor(max_workers=3)

        async def async_func(x):
            await asyncio.sleep(0.01)
            return x * 2

        tasks = [ExecutionTask(f"task_{i}", async_func, (i,), {}) for i in range(5)]

        results = await executor.execute_async(tasks)

        assert len(results) == 5
        assert all(r.success for r in results)
        assert results[0].result == 0
        assert results[1].result == 2
        assert results[4].result == 8

    @pytest.mark.asyncio
    async def test_async_execution_with_error(self):
        """Test async execution with errors"""
        executor = ParallelExecutor()

        async def failing_func():
            raise ValueError("Test error")

        tasks = [
            ExecutionTask("fail", failing_func, (), {}),
            ExecutionTask("success", lambda: 42, (), {}),
        ]

        results = await executor.execute_async(tasks)

        assert results[0].success == False
        assert "Test error" in results[0].error
        # Note: Lambda needs to be async for async execution

    @pytest.mark.asyncio
    async def test_async_execution_timeout(self):
        """Test async execution with timeout"""
        executor = ParallelExecutor()

        async def slow_func():
            await asyncio.sleep(5)
            return "done"

        task = ExecutionTask("slow", slow_func, (), {}, timeout=0.1)
        results = await executor.execute_async([task])

        assert results[0].success == False
        assert results[0].error == "Timeout"

    @pytest.mark.asyncio
    async def test_priority_execution(self):
        """Test priority-based execution"""
        executor = ParallelExecutor(max_workers=1)  # Sequential execution

        execution_order = []

        async def track_func(task_id):
            execution_order.append(task_id)
            return task_id

        tasks = [
            ExecutionTask("low", track_func, ("low",), {}, priority=1),
            ExecutionTask("high", track_func, ("high",), {}, priority=10),
            ExecutionTask("medium", track_func, ("medium",), {}, priority=5),
        ]

        await executor.execute_async(tasks)

        # High priority should execute first
        assert execution_order[0] == "high"
        assert execution_order[1] == "medium"
        assert execution_order[2] == "low"

    def test_sync_execution_thread(self):
        """Test synchronous execution with threads"""
        executor = ParallelExecutor()

        def sync_func(x):
            time.sleep(0.01)
            return x * 2

        tasks = [ExecutionTask(f"task_{i}", sync_func, (i,), {}) for i in range(3)]

        results = executor.execute_batch(tasks, mode="thread")

        assert len(results) == 3
        assert all(r.success for r in results)
        assert results[0].result == 0
        assert results[1].result == 2
        assert results[2].result == 4

    @pytest.mark.asyncio
    async def test_semaphore_concurrency(self):
        """Test semaphore limits concurrent execution"""
        executor = ParallelExecutor(max_workers=2)

        concurrent_count = 0
        max_concurrent = 0

        async def count_concurrent():
            nonlocal concurrent_count, max_concurrent
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)
            await asyncio.sleep(0.05)
            concurrent_count -= 1
            return True

        tasks = [ExecutionTask(f"task_{i}", count_concurrent, (), {}) for i in range(10)]

        await executor.execute_async(tasks)

        # Max concurrent should not exceed max_workers
        assert max_concurrent <= executor.max_workers

    @pytest.mark.asyncio
    async def test_map_reduce(self):
        """Test map-reduce pattern"""
        executor = ParallelExecutor()

        def map_func(chunk):
            return sum(chunk)

        def reduce_func(a, b):
            return a + b

        data = list(range(100))
        result = await executor.map_reduce(data, map_func, reduce_func, chunk_size=20)

        # Sum of 0-99 = 4950
        assert result == 4950

    @pytest.mark.asyncio
    async def test_map_reduce_empty(self):
        """Test map-reduce with empty data"""
        executor = ParallelExecutor()

        result = await executor.map_reduce([], lambda x: x, lambda a, b: a + b)
        assert result is None

    def test_execution_stats(self):
        """Test execution statistics tracking"""
        executor = ParallelExecutor()

        def success_func():
            time.sleep(0.01)
            return "ok"

        def fail_func():
            raise ValueError("fail")

        tasks = [
            ExecutionTask("s1", success_func, (), {}),
            ExecutionTask("s2", success_func, (), {}),
            ExecutionTask("f1", fail_func, (), {}),
        ]

        executor.execute_batch(tasks, mode="thread")

        stats = executor.get_stats()
        assert stats["total"] == 3
        assert stats["success"] == 2
        assert stats["failed"] == 1
        assert stats["avg_time"] > 0

    @pytest.mark.asyncio
    async def test_mixed_sync_async(self):
        """Test mixed sync/async function execution"""
        executor = ParallelExecutor()

        async def async_func(x):
            await asyncio.sleep(0.01)
            return f"async_{x}"

        def sync_func(x):
            time.sleep(0.01)
            return f"sync_{x}"

        tasks = [
            ExecutionTask("async", async_func, (1,), {}),
            ExecutionTask("sync", sync_func, (2,), {}),
        ]

        results = await executor.execute_async(tasks)

        assert results[0].success == True
        assert results[0].result == "async_1"
        assert results[1].success == True
        assert results[1].result == "sync_2"

    def test_shutdown(self):
        """Test executor shutdown"""
        executor = ParallelExecutor()

        # Create process pool
        executor.execute_batch([], mode="process")
        assert executor.process_pool is not None

        executor.shutdown()
        # Should not raise errors
