"""Parallel Executor for Concurrent Agent Operations < 6.5KB"""
import asyncio
import multiprocessing as mp
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class ExecutionTask:
    id: str
    func: Callable
    args: Tuple
    kwargs: Dict
    timeout: Optional[float] = 30
    priority: int = 5


@dataclass
class ExecutionResult:
    task_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0


class ParallelExecutor:
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = None
        self.semaphore = asyncio.Semaphore(max_workers)
        self.execution_stats = {"total": 0, "success": 0, "failed": 0, "timeout": 0, "avg_time": 0}

    async def execute_async(self, tasks: List[ExecutionTask]) -> List[ExecutionResult]:
        """Execute tasks asynchronously"""
        # Sort by priority
        sorted_tasks = sorted(tasks, key=lambda x: x.priority, reverse=True)

        # Execute with semaphore for concurrency control
        async_tasks = [self._execute_single_async(task) for task in sorted_tasks]

        results = await asyncio.gather(*async_tasks, return_exceptions=True)

        # Process results
        final_results = []
        for task, result in zip(sorted_tasks, results):
            if isinstance(result, Exception):
                final_results.append(
                    ExecutionResult(task_id=task.id, success=False, error=str(result))
                )
            else:
                final_results.append(result)

        self._update_stats(final_results)
        return final_results

    async def _execute_single_async(self, task: ExecutionTask) -> ExecutionResult:
        """Execute single task asynchronously"""
        async with self.semaphore:
            start_time = time.time()

            try:
                # Execute with timeout
                if asyncio.iscoroutinefunction(task.func):
                    result = await asyncio.wait_for(
                        task.func(*task.args, **task.kwargs), timeout=task.timeout
                    )
                else:
                    # Run sync function in thread pool
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(self.thread_pool, task.func, *task.args),
                        timeout=task.timeout,
                    )

                return ExecutionResult(
                    task_id=task.id,
                    success=True,
                    result=result,
                    execution_time=time.time() - start_time,
                )

            except asyncio.TimeoutError:
                self.execution_stats["timeout"] += 1
                return ExecutionResult(
                    task_id=task.id,
                    success=False,
                    error="Timeout",
                    execution_time=time.time() - start_time,
                )
            except Exception as e:
                return ExecutionResult(
                    task_id=task.id,
                    success=False,
                    error=str(e),
                    execution_time=time.time() - start_time,
                )

    def execute_batch(
        self, tasks: List[ExecutionTask], mode: str = "thread"
    ) -> List[ExecutionResult]:
        """Execute tasks in batch using threads or processes"""
        if mode == "process":
            return self._execute_batch_process(tasks)
        else:
            return self._execute_batch_thread(tasks)

    def _execute_batch_thread(self, tasks: List[ExecutionTask]) -> List[ExecutionResult]:
        """Execute using thread pool"""
        futures = []
        results = []

        for task in tasks:
            future = self.thread_pool.submit(self._execute_sync_wrapper, task)
            futures.append((task.id, future))

        for task_id, future in futures:
            try:
                result = future.result(timeout=30)
                results.append(result)
            except Exception as e:
                results.append(ExecutionResult(task_id=task_id, success=False, error=str(e)))

        self._update_stats(results)
        return results

    def _execute_batch_process(self, tasks: List[ExecutionTask]) -> List[ExecutionResult]:
        """Execute using process pool"""
        if not self.process_pool:
            self.process_pool = mp.Pool(processes=self.max_workers)

        results = []

        # Note: Functions must be picklable for process pool
        for task in tasks:
            try:
                result = self.process_pool.apply_async(self._execute_sync_wrapper, (task,))
                res = result.get(timeout=task.timeout)
                results.append(res)
            except Exception as e:
                results.append(ExecutionResult(task_id=task.id, success=False, error=str(e)))

        self._update_stats(results)
        return results

    def _execute_sync_wrapper(self, task: ExecutionTask) -> ExecutionResult:
        """Wrapper for sync execution"""
        start_time = time.time()

        try:
            result = task.func(*task.args, **task.kwargs)
            return ExecutionResult(
                task_id=task.id,
                success=True,
                result=result,
                execution_time=time.time() - start_time,
            )
        except Exception as e:
            return ExecutionResult(
                task_id=task.id,
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
            )

    def _update_stats(self, results: List[ExecutionResult]):
        """Update execution statistics"""
        for result in results:
            self.execution_stats["total"] += 1
            if result.success:
                self.execution_stats["success"] += 1
            else:
                self.execution_stats["failed"] += 1

            # Update average time
            if result.execution_time > 0:
                current_avg = self.execution_stats["avg_time"]
                total = self.execution_stats["total"]
                new_avg = (current_avg * (total - 1) + result.execution_time) / total
                self.execution_stats["avg_time"] = new_avg

    async def map_reduce(
        self, data: List[Any], map_func: Callable, reduce_func: Callable, chunk_size: int = 10
    ) -> Any:
        """Map-reduce pattern execution"""
        # Split data into chunks
        chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

        # Map phase
        map_tasks = [
            ExecutionTask(id=f"map_{i}", func=map_func, args=(chunk,), kwargs={})
            for i, chunk in enumerate(chunks)
        ]

        map_results = await self.execute_async(map_tasks)

        # Extract successful results
        mapped_data = [r.result for r in map_results if r.success and r.result is not None]

        # Reduce phase
        if not mapped_data:
            return None

        result = mapped_data[0]
        for data in mapped_data[1:]:
            result = reduce_func(result, data)

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return dict(self.execution_stats)

    def shutdown(self):
        """Shutdown executor pools"""
        self.thread_pool.shutdown(wait=True)
        if self.process_pool:
            self.process_pool.close()
            self.process_pool.join()


# Example usage
if __name__ == "__main__":

    async def async_task(x):
        await asyncio.sleep(0.1)
        return x * 2

    def sync_task(x):
        time.sleep(0.1)
        return x * 2

    async def test_executor():
        executor = ParallelExecutor(max_workers=5)

        # Create async tasks
        tasks = [
            ExecutionTask(id=f"task_{i}", func=async_task, args=(i,), kwargs={}, priority=i)
            for i in range(10)
        ]

        # Execute asynchronously
        results = await executor.execute_async(tasks)
        for r in results:
            print(f"Task {r.task_id}: Success={r.success}, Result={r.result}")

        # Map-reduce example
        data = list(range(100))
        result = await executor.map_reduce(data, lambda chunk: sum(chunk), lambda a, b: a + b)
        print(f"Map-reduce result: {result}")

        # Get stats
        print(f"Stats: {executor.get_stats()}")

        executor.shutdown()

    asyncio.run(test_executor())
