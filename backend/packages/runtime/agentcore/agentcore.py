"""AgentCore - Main runtime for agent lifecycle and task orchestration.

Phase 2: AWS Integration
P2-T2: AgentCore Runtime
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional, Protocol

from .bedrock_integration import BedrockService


class AgentState(Enum):
    """Agent lifecycle states."""

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    EXECUTING = "executing"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ExecutionContext(Protocol):
    """Protocol for execution context."""

    task_id: str
    agent_id: str
    user_id: Optional[str]
    session_id: Optional[str]
    metadata: dict[str, Any]


@dataclass
class Task:
    """Task definition for agent execution.

    Attributes:
        id: Unique task identifier
        type: Task type/category
        payload: Task input data
        agent_id: Target agent identifier
        priority: Task priority (0-10, higher is more urgent)
        timeout_seconds: Maximum execution time
        retry_count: Number of retry attempts
        dependencies: List of task IDs this task depends on
        created_at: Task creation timestamp
        scheduled_at: When task should be executed
        metadata: Additional task metadata
    """

    id: str
    type: str
    payload: dict[str, Any]
    agent_id: str
    priority: int = 5
    timeout_seconds: int = 300
    retry_count: int = 3
    dependencies: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Result of task execution.

    Attributes:
        task_id: Task identifier
        status: Execution status
        result: Task output data
        error: Error message if failed
        duration_ms: Execution time in milliseconds
        agent_id: Executing agent identifier
        completed_at: Completion timestamp
        metadata: Additional result metadata
    """

    task_id: str
    status: TaskStatus
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    agent_id: Optional[str] = None
    completed_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMemory:
    """Agent memory state.

    Attributes:
        short_term: Recent interactions and context
        long_term: Persistent knowledge and patterns
        working: Current task working memory
        episodic: Episode/conversation memory
        max_short_term: Maximum short-term memory entries
        max_working: Maximum working memory entries
    """

    short_term: list[dict[str, Any]] = field(default_factory=list)
    long_term: dict[str, Any] = field(default_factory=dict)
    working: dict[str, Any] = field(default_factory=dict)
    episodic: list[dict[str, Any]] = field(default_factory=list)
    max_short_term: int = 100
    max_working: int = 50

    def add_short_term(self, entry: dict[str, Any]) -> None:
        """Add entry to short-term memory."""
        self.short_term.append({**entry, "timestamp": datetime.now().isoformat()})

        # Trim if over limit
        if len(self.short_term) > self.max_short_term:
            self.short_term.pop(0)

    def add_working(self, key: str, value: Any) -> None:
        """Add entry to working memory."""
        self.working[key] = {"value": value, "timestamp": datetime.now().isoformat()}

        # Trim if over limit
        if len(self.working) > self.max_working:
            # Remove oldest entry
            oldest_key = min(self.working.keys(), key=lambda k: self.working[k]["timestamp"])
            del self.working[oldest_key]

    def get_context(self) -> dict[str, Any]:
        """Get current memory context."""
        return {
            "short_term": self.short_term[-10:],  # Last 10 entries
            "working": self.working,
            "long_term_keys": list(self.long_term.keys()),
        }


class Agent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, agent_id: str, agent_type: str, config: Optional[dict[str, Any]] = None):
        """Initialize agent.

        Args:
            agent_id: Unique agent identifier
            agent_type: Agent type/category
            config: Agent configuration
        """
        self.id = agent_id
        self.type = agent_type
        self.config = config or {}
        self.state = AgentState.CREATED
        self.memory = AgentMemory()
        self.logger = logging.getLogger(f"{self.__class__.__name__}[{agent_id}]")
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent.

        Returns:
            True if initialization was successful
        """
        pass

    @abstractmethod
    async def execute_task(self, task: Task, context: ExecutionContext) -> TaskResult:
        """Execute a task.

        Args:
            task: Task to execute
            context: Execution context

        Returns:
            Task execution result
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up agent resources."""
        pass

    def update_state(self, new_state: AgentState) -> None:
        """Update agent state.

        Args:
            new_state: New agent state
        """
        old_state = self.state
        self.state = new_state
        self.last_activity = datetime.now()
        self.logger.info(f"State transition: {old_state.value} -> {new_state.value}")

    def is_available(self) -> bool:
        """Check if agent is available for tasks."""
        return self.state in [AgentState.READY, AgentState.PAUSED]


class TaskQueue:
    """Priority queue for task management."""

    def __init__(self, max_size: int = 1000):
        """Initialize task queue.

        Args:
            max_size: Maximum queue size
        """
        self.max_size = max_size
        self._queue: list[Task] = []
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition(self._lock)

    async def enqueue(self, task: Task) -> bool:
        """Add task to queue.

        Args:
            task: Task to enqueue

        Returns:
            True if task was enqueued
        """
        async with self._condition:
            if len(self._queue) >= self.max_size:
                return False

            # Insert based on priority and scheduled time
            insert_index = 0
            for i, existing_task in enumerate(self._queue):
                if self._should_insert_before(task, existing_task):
                    insert_index = i
                    break
                insert_index = i + 1

            self._queue.insert(insert_index, task)
            self._condition.notify()
            return True

    async def dequeue(self, agent_id: Optional[str] = None) -> Optional[Task]:
        """Remove and return next task.

        Args:
            agent_id: Filter tasks for specific agent

        Returns:
            Next task or None if queue is empty
        """
        async with self._condition:
            while True:
                # Find next eligible task
                for i, task in enumerate(self._queue):
                    if self._is_task_ready(task, agent_id):
                        return self._queue.pop(i)

                # No eligible tasks, wait for notification
                await self._condition.wait()

    async def peek(self, agent_id: Optional[str] = None) -> Optional[Task]:
        """Look at next task without removing it.

        Args:
            agent_id: Filter tasks for specific agent

        Returns:
            Next task or None
        """
        async with self._lock:
            for task in self._queue:
                if self._is_task_ready(task, agent_id):
                    return task
            return None

    async def remove_task(self, task_id: str) -> bool:
        """Remove task from queue.

        Args:
            task_id: Task identifier

        Returns:
            True if task was removed
        """
        async with self._condition:
            for i, task in enumerate(self._queue):
                if task.id == task_id:
                    self._queue.pop(i)
                    return True
            return False

    def _should_insert_before(self, new_task: Task, existing_task: Task) -> bool:
        """Determine if new task should be inserted before existing task."""
        # Higher priority first
        if new_task.priority > existing_task.priority:
            return True
        if new_task.priority < existing_task.priority:
            return False

        # Same priority, check scheduled time
        new_scheduled = new_task.scheduled_at or new_task.created_at
        existing_scheduled = existing_task.scheduled_at or existing_task.created_at
        return new_scheduled < existing_scheduled

    def _is_task_ready(self, task: Task, agent_id: Optional[str] = None) -> bool:
        """Check if task is ready for execution."""
        # Check agent filter
        if agent_id and task.agent_id != agent_id:
            return False

        # Check scheduled time
        if task.scheduled_at and task.scheduled_at > datetime.now():
            return False

        return True

    async def size(self) -> int:
        """Get queue size."""
        async with self._lock:
            return len(self._queue)


class ResourceMonitor:
    """Monitor system resources and agent performance."""

    def __init__(self):
        """Initialize resource monitor."""
        self.metrics: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def record_metric(
        self, name: str, value: Any, labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record a metric value.

        Args:
            name: Metric name
            value: Metric value
            labels: Optional labels for the metric
        """
        async with self._lock:
            timestamp = datetime.now().isoformat()
            metric_key = f"{name}:{':'.join(f'{k}={v}' for k, v in (labels or {}).items())}"

            if metric_key not in self.metrics:
                self.metrics[metric_key] = []

            self.metrics[metric_key].append({"value": value, "timestamp": timestamp})

            # Keep only last 1000 entries
            if len(self.metrics[metric_key]) > 1000:
                self.metrics[metric_key] = self.metrics[metric_key][-1000:]

    async def get_metrics(self, name: Optional[str] = None) -> dict[str, Any]:
        """Get recorded metrics.

        Args:
            name: Optional metric name filter

        Returns:
            Dictionary of metrics
        """
        async with self._lock:
            if name:
                return {k: v for k, v in self.metrics.items() if k.startswith(name)}
            return dict(self.metrics)


class AgentCore:
    """Main agent runtime for lifecycle and task orchestration."""

    def __init__(self, core_id: Optional[str] = None, config: Optional[dict[str, Any]] = None):
        """Initialize AgentCore.

        Args:
            core_id: Unique core identifier
            config: Core configuration
        """
        self.id = core_id or str(uuid.uuid4())
        self.config = config or {}
        self.logger = logging.getLogger(f"AgentCore[{self.id}]")

        # Core components
        self.agents: dict[str, Agent] = {}
        self.task_queue = TaskQueue(max_size=self.config.get("max_queue_size", 1000))
        self.resource_monitor = ResourceMonitor()
        self.bedrock_service = BedrockService(self.config.get("bedrock"))

        # Execution state
        self.running_tasks: dict[str, asyncio.Task] = {}
        self.task_results: dict[str, TaskResult] = {}
        self.max_concurrent_tasks = self.config.get("max_concurrent_tasks", 10)

        # Lifecycle
        self.is_running = False
        self.shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """Start the AgentCore runtime."""
        if self.is_running:
            self.logger.warning("AgentCore is already running")
            return

        self.logger.info("Starting AgentCore runtime")
        self.is_running = True

        # Start background tasks
        asyncio.create_task(self._task_executor())
        asyncio.create_task(self._health_monitor())
        asyncio.create_task(self._resource_collector())

        self.logger.info("AgentCore runtime started")

    async def shutdown(self) -> None:
        """Shutdown the AgentCore runtime gracefully."""
        if not self.is_running:
            return

        self.logger.info("Shutting down AgentCore runtime")
        self.is_running = False

        # Cancel running tasks
        for task_id, task in self.running_tasks.items():
            self.logger.info(f"Cancelling running task: {task_id}")
            task.cancel()

        # Wait for tasks to complete
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)

        # Cleanup agents
        for agent in self.agents.values():
            try:
                await agent.cleanup()
            except Exception as e:
                self.logger.error(f"Error cleaning up agent {agent.id}: {e}")

        # Shutdown services
        await self.bedrock_service.shutdown()

        self.shutdown_event.set()
        self.logger.info("AgentCore runtime shutdown complete")

    async def register_agent(self, agent: Agent) -> bool:
        """Register an agent with the core.

        Args:
            agent: Agent to register

        Returns:
            True if registration was successful
        """
        if agent.id in self.agents:
            self.logger.warning(f"Agent {agent.id} is already registered")
            return False

        try:
            # Initialize agent
            agent.update_state(AgentState.INITIALIZING)
            success = await agent.initialize()

            if success:
                agent.update_state(AgentState.READY)
                self.agents[agent.id] = agent
                self.logger.info(f"Registered agent: {agent.id}")

                # Record metrics
                await self.resource_monitor.record_metric(
                    "agent_registered", 1, {"agent_id": agent.id, "agent_type": agent.type}
                )

                return True
            else:
                agent.update_state(AgentState.ERROR)
                self.logger.error(f"Failed to initialize agent: {agent.id}")
                return False

        except Exception as e:
            agent.update_state(AgentState.ERROR)
            self.logger.error(f"Error registering agent {agent.id}: {e}")
            return False

    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            True if unregistration was successful
        """
        if agent_id not in self.agents:
            return False

        agent = self.agents[agent_id]
        agent.update_state(AgentState.STOPPING)

        try:
            await agent.cleanup()
            agent.update_state(AgentState.STOPPED)
            del self.agents[agent_id]

            self.logger.info(f"Unregistered agent: {agent_id}")

            # Record metrics
            await self.resource_monitor.record_metric(
                "agent_unregistered", 1, {"agent_id": agent_id}
            )

            return True

        except Exception as e:
            agent.update_state(AgentState.ERROR)
            self.logger.error(f"Error unregistering agent {agent_id}: {e}")
            return False

    async def submit_task(self, task: Task) -> bool:
        """Submit a task for execution.

        Args:
            task: Task to submit

        Returns:
            True if task was submitted successfully
        """
        # Validate task
        if task.agent_id not in self.agents:
            self.logger.error(f"Unknown agent for task {task.id}: {task.agent_id}")
            return False

        # Enqueue task
        success = await self.task_queue.enqueue(task)
        if success:
            self.logger.info(f"Submitted task: {task.id}")
            await self.resource_monitor.record_metric(
                "task_submitted", 1, {"task_type": task.type, "agent_id": task.agent_id}
            )
        else:
            self.logger.error(f"Failed to enqueue task: {task.id}")

        return success

    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get result of a completed task.

        Args:
            task_id: Task identifier

        Returns:
            Task result or None if not found
        """
        return self.task_results.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task.

        Args:
            task_id: Task identifier

        Returns:
            True if task was cancelled
        """
        # Try to remove from queue first
        if await self.task_queue.remove_task(task_id):
            self.logger.info(f"Cancelled pending task: {task_id}")

            # Store cancelled result
            result = TaskResult(task_id=task_id, status=TaskStatus.CANCELLED)
            self.task_results[task_id] = result

            return True

        # Try to cancel running task
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            self.logger.info(f"Cancelled running task: {task_id}")
            return True

        return False

    async def get_agent_status(self, agent_id: Optional[str] = None) -> dict[str, Any]:
        """Get status of agents.

        Args:
            agent_id: Optional specific agent ID

        Returns:
            Agent status information
        """
        if agent_id:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                return {
                    "id": agent.id,
                    "type": agent.type,
                    "state": agent.state.value,
                    "created_at": agent.created_at.isoformat(),
                    "last_activity": agent.last_activity.isoformat(),
                    "memory_context": agent.memory.get_context(),
                }
            return {}

        return {
            agent_id: {
                "id": agent.id,
                "type": agent.type,
                "state": agent.state.value,
                "created_at": agent.created_at.isoformat(),
                "last_activity": agent.last_activity.isoformat(),
            }
            for agent_id, agent in self.agents.items()
        }

    async def get_queue_status(self) -> dict[str, Any]:
        """Get task queue status."""
        queue_size = await self.task_queue.size()
        return {
            "queue_size": queue_size,
            "running_tasks": len(self.running_tasks),
            "max_concurrent": self.max_concurrent_tasks,
            "completed_tasks": len(self.task_results),
        }

    async def _task_executor(self) -> None:
        """Background task executor."""
        self.logger.info("Task executor started")

        while self.is_running:
            try:
                # Check if we can run more tasks
                if len(self.running_tasks) >= self.max_concurrent_tasks:
                    await asyncio.sleep(0.1)
                    continue

                # Get next task
                task = await self.task_queue.dequeue()
                if not task:
                    await asyncio.sleep(0.1)
                    continue

                # Execute task
                execution_task = asyncio.create_task(self._execute_task(task))
                self.running_tasks[task.id] = execution_task

                # Clean up completed tasks
                await self._cleanup_completed_tasks()

            except Exception as e:
                self.logger.error(f"Error in task executor: {e}")
                await asyncio.sleep(1)

        self.logger.info("Task executor stopped")

    async def _execute_task(self, task: Task) -> None:
        """Execute a single task.

        Args:
            task: Task to execute
        """
        start_time = time.time()
        agent = self.agents.get(task.agent_id)

        if not agent:
            result = TaskResult(
                task_id=task.id, status=TaskStatus.FAILED, error=f"Agent {task.agent_id} not found"
            )
            self.task_results[task.id] = result
            return

        # Check agent availability
        if not agent.is_available():
            result = TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=f"Agent {task.agent_id} is not available",
            )
            self.task_results[task.id] = result
            return

        try:
            # Update agent state
            agent.update_state(AgentState.EXECUTING)

            # Create execution context
            context = type(
                "Context",
                (),
                {
                    "task_id": task.id,
                    "agent_id": task.agent_id,
                    "user_id": task.metadata.get("user_id"),
                    "session_id": task.metadata.get("session_id"),
                    "metadata": task.metadata,
                },
            )()

            # Execute with timeout
            result = await asyncio.wait_for(
                agent.execute_task(task, context), timeout=task.timeout_seconds
            )

            # Update result timing
            result.duration_ms = int((time.time() - start_time) * 1000)

        except asyncio.TimeoutError:
            result = TaskResult(
                task_id=task.id,
                status=TaskStatus.TIMEOUT,
                error=f"Task exceeded timeout of {task.timeout_seconds}s",
                duration_ms=int((time.time() - start_time) * 1000),
                agent_id=task.agent_id,
            )

        except asyncio.CancelledError:
            result = TaskResult(
                task_id=task.id,
                status=TaskStatus.CANCELLED,
                duration_ms=int((time.time() - start_time) * 1000),
                agent_id=task.agent_id,
            )

        except Exception as e:
            self.logger.error(f"Task execution error: {e}")
            result = TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=str(e),
                duration_ms=int((time.time() - start_time) * 1000),
                agent_id=task.agent_id,
            )

        finally:
            # Update agent state
            if agent.state == AgentState.EXECUTING:
                agent.update_state(AgentState.READY)

        # Store result
        self.task_results[task.id] = result

        # Record metrics
        await self.resource_monitor.record_metric(
            "task_completed",
            1,
            {"task_type": task.type, "agent_id": task.agent_id, "status": result.status.value},
        )

        await self.resource_monitor.record_metric(
            "task_duration_ms",
            result.duration_ms or 0,
            {"task_type": task.type, "agent_id": task.agent_id},
        )

        self.logger.info(
            f"Task {task.id} completed with status {result.status.value} "
            f"in {result.duration_ms}ms"
        )

    async def _cleanup_completed_tasks(self) -> None:
        """Clean up completed task references."""
        completed_tasks = []
        for task_id, task in self.running_tasks.items():
            if task.done():
                completed_tasks.append(task_id)

        for task_id in completed_tasks:
            del self.running_tasks[task_id]

    async def _health_monitor(self) -> None:
        """Background health monitoring."""
        self.logger.info("Health monitor started")

        while self.is_running:
            try:
                # Check agent health
                for agent_id, agent in self.agents.items():
                    # Check for stuck agents
                    time_since_activity = datetime.now() - agent.last_activity
                    if time_since_activity > timedelta(minutes=30):
                        self.logger.warning(f"Agent {agent_id} inactive for {time_since_activity}")

                # Record health metrics
                await self.resource_monitor.record_metric("agents_count", len(self.agents))

                await self.resource_monitor.record_metric(
                    "queue_size", await self.task_queue.size()
                )

                await self.resource_monitor.record_metric("running_tasks", len(self.running_tasks))

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(60)

        self.logger.info("Health monitor stopped")

    async def _resource_collector(self) -> None:
        """Background resource metrics collection."""
        self.logger.info("Resource collector started")

        while self.is_running:
            try:
                # Collect bedrock usage
                bedrock_usage = self.bedrock_service.client.get_usage_summary()
                for metric_name, value in bedrock_usage.items():
                    await self.resource_monitor.record_metric(f"bedrock_{metric_name}", value)

                await asyncio.sleep(300)  # Collect every 5 minutes

            except Exception as e:
                self.logger.error(f"Error in resource collector: {e}")
                await asyncio.sleep(300)

        self.logger.info("Resource collector stopped")
