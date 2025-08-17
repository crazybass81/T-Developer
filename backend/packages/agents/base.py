"""Base agent interface for T-Developer agents."""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from backend.core.shared_context import SharedContextStore, get_context_store

# Constants
DEFAULT_TIMEOUT: int = 300
MAX_RETRIES: int = 3


class AgentStatus(Enum):
    """Agent execution status."""

    OK = "ok"
    RETRY = "retry"
    FAIL = "fail"


@dataclass
class AgentInput:
    """Standard input for all agents."""

    intent: str  # "research", "plan", "code", "evaluate"
    task_id: str  # Unique identifier for idempotency
    payload: dict[str, Any]  # Task-specific data
    context: Optional[dict[str, Any]] = None  # Repo, branch, user, etc.
    constraints: Optional[dict[str, Any]] = None  # Time, cost, quality limits


@dataclass
class AgentOutput:
    """Standard output from all agents."""

    task_id: str
    status: AgentStatus
    artifacts: list[Artifact] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    events: list[Event] = field(default_factory=list)
    next_tasks: list[dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class Artifact:
    """Represents a produced artifact."""

    kind: str  # "diff", "file", "report", "pr", "metric"
    ref: str  # Path or URL
    content: Optional[Any] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Event:
    """Event for async communication."""

    type: str  # e.g., "code.patch.ready"
    key: str  # Deduplication key
    data: Any
    visibility: str = "internal"  # "internal" or "a2a"


class BaseAgent(ABC):
    """Base class for all T-Developer agents."""

    def __init__(self, name: str, config: Optional[dict[str, Any]] = None):
        """Initialize agent.

        Args:
            name: Agent name
            config: Agent configuration
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{name}")
        self.context_store: SharedContextStore = get_context_store()
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate agent configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        timeout = self.config.get("timeout", DEFAULT_TIMEOUT)
        if timeout <= 0:
            raise ValueError("Timeout must be positive")

    @abstractmethod
    async def execute(self, input: AgentInput) -> AgentOutput:
        """Execute the agent's primary task.

        Args:
            input: Task input

        Returns:
            Task output

        Raises:
            TimeoutError: If execution exceeds timeout
            RuntimeError: If execution fails
        """
        pass

    @abstractmethod
    async def validate(self, output: AgentOutput) -> bool:
        """Validate the agent's output.

        Args:
            output: Output to validate

        Returns:
            True if output is valid
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        """Return agent capabilities for discovery.

        Returns:
            Dictionary of capabilities
        """
        pass

    async def store_agent_data(
        self, section: str, data: dict[str, Any], evolution_id: Optional[str] = None
    ) -> bool:
        """Store agent-specific data in context store.

        Args:
            section: Section to update (e.g., 'original_analysis')
            data: Data to store
            evolution_id: Evolution ID (uses current if not provided)

        Returns:
            Success status
        """
        try:
            success = await self.context_store.update_context(section, data, evolution_id)
            if success:
                self.logger.info(
                    f"Stored data in {section} for evolution {evolution_id or 'current'}"
                )
            else:
                self.logger.error(f"Failed to store data in {section}")
            return success
        except Exception as e:
            self.logger.error(f"Error storing agent data: {e}")
            return False

    async def retrieve_context(
        self, evolution_id: Optional[str] = None
    ) -> Optional[dict[str, Any]]:
        """Retrieve evolution context data.

        Args:
            evolution_id: Evolution ID (uses current if not provided)

        Returns:
            Context data dictionary or None
        """
        try:
            context = await self.context_store.get_context(evolution_id)
            if context:
                return context.to_dict()
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving context: {e}")
            return None

    async def get_current_evolution_id(self) -> Optional[str]:
        """Get current evolution ID from context store.

        Returns:
            Current evolution ID or None
        """
        return self.context_store.current_evolution_id

    async def execute_with_retry(
        self, input: AgentInput, max_retries: Optional[int] = None
    ) -> AgentOutput:
        """Execute with automatic retry on failure.

        Args:
            input: Task input
            max_retries: Override default retry count

        Returns:
            Final execution result
        """
        retries = max_retries or self.config.get("retries", MAX_RETRIES)
        last_error: Optional[Exception] = None
        timeout = self.config.get("timeout", DEFAULT_TIMEOUT)

        for attempt in range(retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{retries} for task {input.task_id}")

                result = await asyncio.wait_for(self.execute(input), timeout=timeout)

                if result.status == AgentStatus.OK:
                    return result

                if result.status == AgentStatus.FAIL:
                    last_error = Exception(result.error)

            except asyncio.TimeoutError as e:
                last_error = e
                self.logger.warning(f"Attempt {attempt + 1} timed out")
            except Exception as e:
                last_error = e
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")

            if attempt < retries - 1:
                await asyncio.sleep(2**attempt)  # Exponential backoff

        return AgentOutput(
            task_id=input.task_id,
            status=AgentStatus.FAIL,
            error=str(last_error),
            metrics={"attempts": retries},
        )
