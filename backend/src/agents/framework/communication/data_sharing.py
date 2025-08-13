# backend/src/agents/framework/data_sharing.py
from typing import Dict, Any, Optional, List, Set
import asyncio
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum


class ShareScope(Enum):
    PRIVATE = "private"
    AGENT_GROUP = "agent_group"
    PROJECT = "project"
    GLOBAL = "global"


class DataType(Enum):
    STATE = "state"
    RESULT = "result"
    CONTEXT = "context"
    METADATA = "metadata"


@dataclass
class SharedData:
    id: str
    owner_id: str
    data_type: DataType
    scope: ShareScope
    content: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    allowed_agents: Optional[Set[str]] = None


class DataSharingManager:
    def __init__(self):
        self.shared_data: Dict[str, SharedData] = {}
        self.access_log: List[Dict[str, Any]] = []
        self.subscriptions: Dict[str, List[str]] = {}  # data_id -> [agent_ids]
        self._lock = asyncio.Lock()

    async def share_data(
        self,
        owner_id: str,
        data_type: DataType,
        content: Dict[str, Any],
        scope: ShareScope = ShareScope.AGENT_GROUP,
        ttl_seconds: Optional[int] = None,
        allowed_agents: Optional[Set[str]] = None,
    ) -> str:
        """Share data with specified scope and permissions"""
        import uuid

        data_id = str(uuid.uuid4())
        expires_at = None
        if ttl_seconds:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

        shared_data = SharedData(
            id=data_id,
            owner_id=owner_id,
            data_type=data_type,
            scope=scope,
            content=content,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            allowed_agents=allowed_agents,
        )

        async with self._lock:
            self.shared_data[data_id] = shared_data

        # Notify subscribers
        await self._notify_subscribers(data_id, "data_shared")

        return data_id

    async def get_shared_data(
        self, data_id: str, requester_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve shared data with access control"""
        async with self._lock:
            data = self.shared_data.get(data_id)
            if not data:
                return None

            # Check expiration
            if data.expires_at and datetime.utcnow() > data.expires_at:
                del self.shared_data[data_id]
                return None

            # Check access permissions
            if not self._check_access(data, requester_id):
                return None

            # Update access count
            data.access_count += 1

            # Log access
            self.access_log.append(
                {
                    "data_id": data_id,
                    "requester_id": requester_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "read",
                }
            )

            return data.content

    def _check_access(self, data: SharedData, requester_id: str) -> bool:
        """Check if requester has access to the data"""
        if data.owner_id == requester_id:
            return True

        if data.scope == ShareScope.PRIVATE:
            return False

        if data.scope == ShareScope.GLOBAL:
            return True

        if data.allowed_agents and requester_id not in data.allowed_agents:
            return False

        return True

    async def update_shared_data(
        self, data_id: str, requester_id: str, new_content: Dict[str, Any]
    ) -> bool:
        """Update shared data (owner only)"""
        async with self._lock:
            data = self.shared_data.get(data_id)
            if not data or data.owner_id != requester_id:
                return False

            data.content.update(new_content)
            await self._notify_subscribers(data_id, "data_updated")
            return True

    async def subscribe_to_data(self, data_id: str, agent_id: str):
        """Subscribe to data changes"""
        if data_id not in self.subscriptions:
            self.subscriptions[data_id] = []

        if agent_id not in self.subscriptions[data_id]:
            self.subscriptions[data_id].append(agent_id)

    async def _notify_subscribers(self, data_id: str, event_type: str):
        """Notify subscribers of data changes"""
        subscribers = self.subscriptions.get(data_id, [])
        for subscriber_id in subscribers:
            # In a real implementation, this would send actual notifications
            print(f"Notifying {subscriber_id} of {event_type} for {data_id}")

    async def cleanup_expired_data(self):
        """Remove expired data"""
        now = datetime.utcnow()
        expired_ids = []

        async with self._lock:
            for data_id, data in self.shared_data.items():
                if data.expires_at and now > data.expires_at:
                    expired_ids.append(data_id)

            for data_id in expired_ids:
                del self.shared_data[data_id]

        return len(expired_ids)


class AgentDataSharingMixin:
    def __init__(self):
        self.data_manager = DataSharingManager()
        self.agent_id = getattr(self, "agent_id", "unknown")

    async def share_state(
        self,
        state: Dict[str, Any],
        scope: ShareScope = ShareScope.AGENT_GROUP,
        ttl_seconds: Optional[int] = 3600,
    ) -> str:
        """Share agent state"""
        return await self.data_manager.share_data(
            self.agent_id, DataType.STATE, state, scope, ttl_seconds
        )

    async def share_result(
        self, result: Dict[str, Any], scope: ShareScope = ShareScope.PROJECT
    ) -> str:
        """Share execution result"""
        return await self.data_manager.share_data(
            self.agent_id, DataType.RESULT, result, scope
        )

    async def get_shared_state(self, data_id: str) -> Optional[Dict[str, Any]]:
        """Get shared state from another agent"""
        return await self.data_manager.get_shared_data(data_id, self.agent_id)

    async def subscribe_to_agent_data(self, data_id: str):
        """Subscribe to data changes"""
        await self.data_manager.subscribe_to_data(data_id, self.agent_id)
