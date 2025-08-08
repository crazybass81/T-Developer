# backend/src/agents/framework/parallel_coordinator.py
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

@dataclass
class ParallelTask:
    id: str
    agent_id: str
    action: str
    inputs: Dict[str, Any]
    priority: int = 0
    timeout: int = 300
    dependencies: Set[str] = None

@dataclass
class TaskResult:
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0

class ParallelCoordinator:
    def __init__(self, max_workers: int = 50):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_handlers: Dict[str, Callable] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.semaphore = asyncio.Semaphore(max_workers)
    
    def register_task_handler(self, agent_id: str, handler: Callable):
        self.task_handlers[agent_id] = handler
    
    async def execute_parallel_tasks(self, tasks: List[ParallelTask]) -> Dict[str, TaskResult]:
        # Sort by priority and resolve dependencies
        sorted_tasks = self._resolve_dependencies(tasks)
        
        # Execute tasks in batches based on dependencies
        results = {}
        for batch in sorted_tasks:
            batch_results = await self._execute_batch(batch)
            results.update(batch_results)
        
        return results
    
    def _resolve_dependencies(self, tasks: List[ParallelTask]) -> List[List[ParallelTask]]:
        task_map = {task.id: task for task in tasks}
        batches = []
        remaining_tasks = set(task.id for task in tasks)
        completed_tasks = set()
        
        while remaining_tasks:
            current_batch = []
            
            for task_id in list(remaining_tasks):
                task = task_map[task_id]
                dependencies = task.dependencies or set()
                
                if dependencies.issubset(completed_tasks):
                    current_batch.append(task)
                    remaining_tasks.remove(task_id)
            
            if not current_batch:
                # Circular dependency or missing dependency
                raise ValueError("Circular dependency or missing dependency detected")
            
            # Sort batch by priority
            current_batch.sort(key=lambda t: t.priority, reverse=True)
            batches.append(current_batch)
            completed_tasks.update(task.id for task in current_batch)
        
        return batches
    
    async def _execute_batch(self, tasks: List[ParallelTask]) -> Dict[str, TaskResult]:
        # Create tasks for parallel execution
        async_tasks = []
        for task in tasks:
            async_task = asyncio.create_task(self._execute_single_task(task))
            async_tasks.append((task.id, async_task))
            self.active_tasks[task.id] = async_task
        
        # Wait for all tasks to complete
        results = {}
        for task_id, async_task in async_tasks:
            try:
                result = await async_task
                results[task_id] = result
                self.completed_tasks[task_id] = result
            except Exception as e:
                error_result = TaskResult(
                    task_id=task_id,
                    success=False,
                    error=str(e)
                )
                results[task_id] = error_result
                self.completed_tasks[task_id] = error_result
            finally:
                self.active_tasks.pop(task_id, None)
        
        return results
    
    async def _execute_single_task(self, task: ParallelTask) -> TaskResult:
        async with self.semaphore:
            handler = self.task_handlers.get(task.agent_id)
            if not handler:
                return TaskResult(
                    task_id=task.id,
                    success=False,
                    error=f"No handler for agent {task.agent_id}"
                )
            
            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await asyncio.wait_for(
                        handler(task.action, task.inputs),
                        timeout=task.timeout
                    )
                else:
                    # Execute sync function in thread pool
                    result = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            self.executor,
                            lambda: handler(task.action, task.inputs)
                        ),
                        timeout=task.timeout
                    )
                
                execution_time = time.time() - start_time
                return TaskResult(
                    task_id=task.id,
                    success=True,
                    result=result,
                    execution_time=execution_time
                )
            
            except asyncio.TimeoutError:
                return TaskResult(
                    task_id=task.id,
                    success=False,
                    error=f"Task timed out after {task.timeout} seconds",
                    execution_time=time.time() - start_time
                )
            except Exception as e:
                return TaskResult(
                    task_id=task.id,
                    success=False,
                    error=str(e),
                    execution_time=time.time() - start_time
                )
    
    async def cancel_task(self, task_id: str) -> bool:
        task = self.active_tasks.get(task_id)
        if task:
            task.cancel()
            return True
        return False
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        if task_id in self.active_tasks:
            return "running"
        elif task_id in self.completed_tasks:
            return "completed"
        return None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        completed = list(self.completed_tasks.values())
        successful = [t for t in completed if t.success]
        failed = [t for t in completed if not t.success]
        
        return {
            "total_tasks": len(completed),
            "successful_tasks": len(successful),
            "failed_tasks": len(failed),
            "success_rate": len(successful) / len(completed) if completed else 0,
            "avg_execution_time": sum(t.execution_time for t in successful) / len(successful) if successful else 0,
            "active_tasks": len(self.active_tasks)
        }