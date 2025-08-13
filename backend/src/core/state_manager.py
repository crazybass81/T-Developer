"""
Pipeline State Management System
Manages state, history, and checkpoints for pipeline execution
"""
import asyncio
import hashlib
import json
import pickle
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from src.core.interfaces import AgentResult, PipelineContext, ProcessingStatus

try:
    from src.services.aws_clients import get_dynamodb_client, get_s3_client

    # Redis client is optional
    try:
        from src.services.aws_clients import get_redis_client
    except ImportError:

        def get_redis_client():
            return None

except ImportError:
    # Fallback if aws_clients is not available
    def get_dynamodb_client():
        return None

    def get_s3_client():
        return None

    def get_redis_client():
        return None


class StateType(Enum):
    """Types of state storage"""

    MEMORY = "memory"
    REDIS = "redis"
    DYNAMODB = "dynamodb"
    S3 = "s3"


class CheckpointStrategy(Enum):
    """Checkpoint strategies"""

    AFTER_EACH_AGENT = "after_each_agent"
    CRITICAL_POINTS = "critical_points"
    TIME_BASED = "time_based"
    ON_DEMAND = "on_demand"


@dataclass
class StateSnapshot:
    """Snapshot of pipeline state at a point in time"""

    snapshot_id: str
    pipeline_id: str
    timestamp: datetime
    agent_name: str
    agent_status: ProcessingStatus
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "snapshot_id": self.snapshot_id,
            "pipeline_id": self.pipeline_id,
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
            "agent_status": self.agent_status.value,
            "data": self.data,
            "metadata": self.metadata,
        }


@dataclass
class Checkpoint:
    """Pipeline execution checkpoint"""

    checkpoint_id: str
    pipeline_id: str
    created_at: datetime
    agent_name: str
    state_data: bytes  # Pickled state
    can_resume: bool = True
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if checkpoint is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


class PipelineStateManager:
    """Manages pipeline execution state"""

    def __init__(
        self,
        state_type: StateType = StateType.MEMORY,
        checkpoint_strategy: CheckpointStrategy = CheckpointStrategy.CRITICAL_POINTS,
        ttl_seconds: int = 3600,
    ):
        """Initialize state manager"""
        self.state_type = state_type
        self.checkpoint_strategy = checkpoint_strategy
        self.ttl_seconds = ttl_seconds

        # In-memory state storage
        self._states: Dict[str, Dict[str, Any]] = {}
        self._history: Dict[str, List[StateSnapshot]] = {}
        self._checkpoints: Dict[str, List[Checkpoint]] = {}

        # External storage clients
        self._dynamodb = None
        self._s3 = None
        self._redis = None

        # Critical agents for checkpointing
        self.critical_agents = {"parser", "generation", "assembly"}

        # State locks for concurrent access
        self._locks: Dict[str, asyncio.Lock] = {}

    async def initialize(self):
        """Initialize external storage connections"""
        if self.state_type == StateType.DYNAMODB:
            self._dynamodb = get_dynamodb_client()
        elif self.state_type == StateType.S3:
            self._s3 = get_s3_client()
        elif self.state_type == StateType.REDIS:
            # Redis client would be initialized here
            pass

    def _get_lock(self, pipeline_id: str) -> asyncio.Lock:
        """Get or create lock for pipeline"""
        if pipeline_id not in self._locks:
            self._locks[pipeline_id] = asyncio.Lock()
        return self._locks[pipeline_id]

    async def create_pipeline_state(self, context: PipelineContext) -> str:
        """Create new pipeline state"""
        pipeline_id = context.pipeline_id

        async with self._get_lock(pipeline_id):
            initial_state = {
                "pipeline_id": pipeline_id,
                "project_id": context.project_id,
                "status": ProcessingStatus.PENDING.value,
                "context": context.to_dict(),
                "agents_completed": [],
                "current_agent": None,
                "results": {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Store in memory
            self._states[pipeline_id] = initial_state
            self._history[pipeline_id] = []
            self._checkpoints[pipeline_id] = []

            # Store in external storage if configured
            await self._persist_state(pipeline_id, initial_state)

            return pipeline_id

    async def get_state(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get current pipeline state"""
        # Check memory first
        if pipeline_id in self._states:
            return self._states[pipeline_id].copy()

        # Try to load from external storage
        state = await self._load_state(pipeline_id)
        if state:
            self._states[pipeline_id] = state
            return state

        return None

    async def update_state(self, pipeline_id: str, agent_name: str, result: AgentResult) -> None:
        """Update pipeline state with agent result"""
        async with self._get_lock(pipeline_id):
            if pipeline_id not in self._states:
                raise ValueError(f"Pipeline {pipeline_id} not found")

            state = self._states[pipeline_id]

            # Update state
            state["current_agent"] = agent_name
            state["results"][agent_name] = result.to_dict()
            state["updated_at"] = datetime.utcnow().isoformat()

            if result.is_successful():
                if agent_name not in state["agents_completed"]:
                    state["agents_completed"].append(agent_name)

            # Add to history
            snapshot = StateSnapshot(
                snapshot_id=f"{pipeline_id}_{agent_name}_{datetime.utcnow().timestamp()}",
                pipeline_id=pipeline_id,
                timestamp=datetime.utcnow(),
                agent_name=agent_name,
                agent_status=result.status,
                data=result.to_dict(),
            )

            if pipeline_id not in self._history:
                self._history[pipeline_id] = []
            self._history[pipeline_id].append(snapshot)

            # Persist state
            await self._persist_state(pipeline_id, state)

            # Create checkpoint if needed
            await self._maybe_create_checkpoint(pipeline_id, agent_name, state)

    async def _maybe_create_checkpoint(
        self, pipeline_id: str, agent_name: str, state: Dict[str, Any]
    ) -> None:
        """Create checkpoint based on strategy"""
        should_checkpoint = False

        if self.checkpoint_strategy == CheckpointStrategy.AFTER_EACH_AGENT:
            should_checkpoint = True
        elif self.checkpoint_strategy == CheckpointStrategy.CRITICAL_POINTS:
            should_checkpoint = agent_name in self.critical_agents
        elif self.checkpoint_strategy == CheckpointStrategy.TIME_BASED:
            # Check if enough time has passed since last checkpoint
            if self._checkpoints.get(pipeline_id):
                last_checkpoint = self._checkpoints[pipeline_id][-1]
                time_diff = datetime.utcnow() - last_checkpoint.created_at
                should_checkpoint = time_diff.total_seconds() > 60  # Every minute
            else:
                should_checkpoint = True

        if should_checkpoint:
            await self.create_checkpoint(pipeline_id, agent_name)

    async def create_checkpoint(self, pipeline_id: str, agent_name: str) -> str:
        """Create a checkpoint for pipeline state"""
        if pipeline_id not in self._states:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        state = self._states[pipeline_id]
        checkpoint_id = f"ckpt_{pipeline_id}_{agent_name}_{datetime.utcnow().timestamp()}"

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            pipeline_id=pipeline_id,
            created_at=datetime.utcnow(),
            agent_name=agent_name,
            state_data=pickle.dumps(state),
            can_resume=True,
            expires_at=datetime.utcnow() + timedelta(seconds=self.ttl_seconds),
        )

        if pipeline_id not in self._checkpoints:
            self._checkpoints[pipeline_id] = []
        self._checkpoints[pipeline_id].append(checkpoint)

        # Store checkpoint in external storage
        await self._persist_checkpoint(checkpoint)

        return checkpoint_id

    async def restore_from_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Restore pipeline state from checkpoint"""
        # Find checkpoint
        checkpoint = None
        for pipeline_checkpoints in self._checkpoints.values():
            for ckpt in pipeline_checkpoints:
                if ckpt.checkpoint_id == checkpoint_id:
                    checkpoint = ckpt
                    break
            if checkpoint:
                break

        if not checkpoint:
            # Try loading from external storage
            checkpoint = await self._load_checkpoint(checkpoint_id)

        if not checkpoint:
            return None

        if checkpoint.is_expired():
            return None

        # Restore state
        state = pickle.loads(checkpoint.state_data)
        self._states[checkpoint.pipeline_id] = state

        return state

    async def get_pipeline_history(self, pipeline_id: str) -> List[StateSnapshot]:
        """Get execution history for pipeline"""
        if pipeline_id in self._history:
            return self._history[pipeline_id].copy()

        # Try loading from external storage
        history = await self._load_history(pipeline_id)
        if history:
            self._history[pipeline_id] = history
            return history

        return []

    async def get_checkpoints(self, pipeline_id: str) -> List[Dict[str, Any]]:
        """Get available checkpoints for pipeline"""
        if pipeline_id not in self._checkpoints:
            return []

        checkpoints = []
        for checkpoint in self._checkpoints[pipeline_id]:
            if not checkpoint.is_expired():
                checkpoints.append(
                    {
                        "checkpoint_id": checkpoint.checkpoint_id,
                        "created_at": checkpoint.created_at.isoformat(),
                        "agent_name": checkpoint.agent_name,
                        "can_resume": checkpoint.can_resume,
                    }
                )

        return checkpoints

    async def cleanup_pipeline(self, pipeline_id: str) -> None:
        """Clean up pipeline state and resources"""
        async with self._get_lock(pipeline_id):
            # Remove from memory
            if pipeline_id in self._states:
                del self._states[pipeline_id]
            if pipeline_id in self._history:
                del self._history[pipeline_id]
            if pipeline_id in self._checkpoints:
                del self._checkpoints[pipeline_id]
            if pipeline_id in self._locks:
                del self._locks[pipeline_id]

            # Clean up external storage
            await self._cleanup_external(pipeline_id)

    # ============= External Storage Methods =============

    async def _persist_state(self, pipeline_id: str, state: Dict[str, Any]) -> None:
        """Persist state to external storage"""
        if self.state_type == StateType.DYNAMODB:
            await self._persist_to_dynamodb(pipeline_id, state)
        elif self.state_type == StateType.S3:
            await self._persist_to_s3(pipeline_id, state)
        elif self.state_type == StateType.REDIS:
            await self._persist_to_redis(pipeline_id, state)

    async def _load_state(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Load state from external storage"""
        if self.state_type == StateType.DYNAMODB:
            return await self._load_from_dynamodb(pipeline_id)
        elif self.state_type == StateType.S3:
            return await self._load_from_s3(pipeline_id)
        elif self.state_type == StateType.REDIS:
            return await self._load_from_redis(pipeline_id)
        return None

    async def _persist_to_dynamodb(self, pipeline_id: str, state: Dict[str, Any]) -> None:
        """Persist state to DynamoDB"""
        if not self._dynamodb:
            return

        # Add TTL for automatic cleanup
        ttl_timestamp = int((datetime.utcnow() + timedelta(seconds=self.ttl_seconds)).timestamp())

        item = {**state, "ttl": ttl_timestamp}

        self._dynamodb.put_item(table_name="t-developer-pipeline-state", item=item)

    async def _load_from_dynamodb(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Load state from DynamoDB"""
        if not self._dynamodb:
            return None

        result = self._dynamodb.get_item(
            table_name="t-developer-pipeline-state", key={"pipeline_id": pipeline_id}
        )

        return result

    async def _persist_to_s3(self, pipeline_id: str, state: Dict[str, Any]) -> None:
        """Persist state to S3"""
        if not self._s3:
            return

        key = f"pipeline-states/{pipeline_id}/state.json"
        data = json.dumps(state).encode("utf-8")

        self._s3.upload_data(
            data=data,
            bucket_name="t-developer-pipeline-states",
            object_key=key,
            content_type="application/json",
        )

    async def _load_from_s3(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Load state from S3"""
        if not self._s3:
            return None

        key = f"pipeline-states/{pipeline_id}/state.json"

        data = self._s3.get_object(bucket_name="t-developer-pipeline-states", object_key=key)

        if data:
            return json.loads(data.decode("utf-8"))
        return None

    async def _persist_to_redis(self, pipeline_id: str, state: Dict[str, Any]) -> None:
        """Persist state to Redis"""
        # Redis implementation would go here
        pass

    async def _load_from_redis(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Load state from Redis"""
        # Redis implementation would go here
        return None

    async def _persist_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Persist checkpoint to external storage"""
        if self.state_type == StateType.S3:
            key = f"checkpoints/{checkpoint.pipeline_id}/{checkpoint.checkpoint_id}.pkl"
            self._s3.upload_data(
                data=pickle.dumps(checkpoint),
                bucket_name="t-developer-pipeline-states",
                object_key=key,
            )

    async def _load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load checkpoint from external storage"""
        # Implementation would go here
        return None

    async def _load_history(self, pipeline_id: str) -> List[StateSnapshot]:
        """Load history from external storage"""
        # Implementation would go here
        return []

    async def _cleanup_external(self, pipeline_id: str) -> None:
        """Clean up external storage"""
        if self.state_type == StateType.DYNAMODB and self._dynamodb:
            self._dynamodb.delete_item(
                table_name="t-developer-pipeline-state",
                key={"pipeline_id": pipeline_id},
            )
        elif self.state_type == StateType.S3 and self._s3:
            # Delete all objects with pipeline_id prefix
            objects = self._s3.list_objects(
                bucket_name="t-developer-pipeline-states",
                prefix=f"pipeline-states/{pipeline_id}/",
            )
            for obj in objects:
                self._s3.delete_object(
                    bucket_name="t-developer-pipeline-states", object_key=obj["Key"]
                )


# Export classes
__all__ = [
    "StateType",
    "CheckpointStrategy",
    "StateSnapshot",
    "Checkpoint",
    "PipelineStateManager",
]
