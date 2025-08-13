"""
Broadcast Manager Implementation
Day 8: Message Queue System
Generated: 2024-11-18

Manage agent groups and broadcast messaging
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

import redis.asyncio as redis


class BroadcastManager:
    """Manage agent groups and broadcast messaging"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {"redis_url": "redis://localhost:6379"}
        self._redis_client = None
        self._agent_groups = {}  # group_name -> set of agent_ids
        self._broadcast_history = []

    async def _get_redis_client(self):
        """Get or create Redis client connection"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(self.config["redis_url"], decode_responses=True)
            except Exception:
                pass
        return self._redis_client

    async def create_agent_group(self, group_name: str, agent_ids: List[str]):
        """Create a new agent group"""
        self._agent_groups[group_name] = set(agent_ids)

        redis_client = await self._get_redis_client()
        if redis_client:
            # Store group in Redis
            await redis_client.sadd(f"group:{group_name}", *agent_ids)

    async def add_agent_to_group(self, group_name: str, agent_id: str):
        """Add agent to existing group"""
        if group_name not in self._agent_groups:
            self._agent_groups[group_name] = set()

        self._agent_groups[group_name].add(agent_id)

        redis_client = await self._get_redis_client()
        if redis_client:
            await redis_client.sadd(f"group:{group_name}", agent_id)

    async def remove_agent_from_group(self, group_name: str, agent_id: str):
        """Remove agent from group"""
        if group_name in self._agent_groups:
            self._agent_groups[group_name].discard(agent_id)

        redis_client = await self._get_redis_client()
        if redis_client:
            await redis_client.srem(f"group:{group_name}", agent_id)

    async def get_group_members(self, group_name: str) -> List[str]:
        """Get all members of a group"""
        redis_client = await self._get_redis_client()
        if redis_client:
            members = await redis_client.smembers(f"group:{group_name}")
            return list(members)

        return list(self._agent_groups.get(group_name, set()))

    async def broadcast_to_group(self, group_name: str, message: Dict) -> List[Dict]:
        """Broadcast message to all agents in group"""
        broadcast_id = str(uuid.uuid4())

        # Get group members
        agent_ids = await self.get_group_members(group_name)

        if not agent_ids:
            return [
                {
                    "broadcast_id": broadcast_id,
                    "status": "error",
                    "error": f"Group {group_name} not found or empty",
                }
            ]

        # Prepare broadcast message
        broadcast_message = {
            "broadcast_id": broadcast_id,
            "group_name": group_name,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "target_count": len(agent_ids),
        }

        # Send to each agent
        results = []
        for agent_id in agent_ids:
            try:
                result = await self._send_to_agent(agent_id, broadcast_message)
                results.append({"agent_id": agent_id, "status": "sent", "result": result})
            except Exception as e:
                results.append({"agent_id": agent_id, "status": "failed", "error": str(e)})

        # Record broadcast history
        self._broadcast_history.append(
            {
                "broadcast_id": broadcast_id,
                "group_name": group_name,
                "timestamp": datetime.utcnow().isoformat(),
                "target_count": len(agent_ids),
                "successful_sends": sum(1 for r in results if r["status"] == "sent"),
                "failed_sends": sum(1 for r in results if r["status"] == "failed"),
            }
        )

        return results

    async def _send_to_agent(self, agent_id: str, message: Dict) -> Dict:
        """Send message to individual agent"""
        # Mock implementation - in production would use actual agent communication
        return {
            "status": "sent",
            "agent_id": agent_id,
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def broadcast_to_all_active_agents(self, message: Dict) -> List[Dict]:
        """Broadcast to all currently active agents"""
        # In production, would query agent registry for active agents
        active_agents = ["agent_001", "agent_002", "agent_003"]  # Mock data

        broadcast_id = str(uuid.uuid4())
        results = []

        for agent_id in active_agents:
            try:
                result = await self._send_to_agent(
                    agent_id,
                    {
                        "broadcast_id": broadcast_id,
                        "type": "global_broadcast",
                        "message": message,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                results.append({"agent_id": agent_id, "status": "sent", "result": result})
            except Exception as e:
                results.append({"agent_id": agent_id, "status": "failed", "error": str(e)})

        return results

    async def get_broadcast_statistics(self) -> Dict:
        """Get broadcast usage statistics"""
        if not self._broadcast_history:
            return {"status": "no_data"}

        total_broadcasts = len(self._broadcast_history)
        total_targets = sum(b["target_count"] for b in self._broadcast_history)
        total_successful = sum(b["successful_sends"] for b in self._broadcast_history)
        total_failed = sum(b["failed_sends"] for b in self._broadcast_history)

        # Group statistics
        group_stats = {}
        for broadcast in self._broadcast_history:
            group = broadcast["group_name"]
            if group not in group_stats:
                group_stats[group] = {"broadcasts": 0, "targets": 0, "success": 0}

            group_stats[group]["broadcasts"] += 1
            group_stats[group]["targets"] += broadcast["target_count"]
            group_stats[group]["success"] += broadcast["successful_sends"]

        return {
            "total_broadcasts": total_broadcasts,
            "total_message_targets": total_targets,
            "total_successful_deliveries": total_successful,
            "total_failed_deliveries": total_failed,
            "success_rate": total_successful / max(total_targets, 1),
            "active_groups": len(self._agent_groups),
            "group_statistics": group_stats,
            "most_active_group": max(group_stats.keys(), key=lambda g: group_stats[g]["broadcasts"])
            if group_stats
            else None,
        }

    async def cleanup_empty_groups(self) -> int:
        """Remove groups with no members"""
        removed_count = 0
        groups_to_remove = []

        for group_name in self._agent_groups:
            members = await self.get_group_members(group_name)
            if not members:
                groups_to_remove.append(group_name)

        for group_name in groups_to_remove:
            del self._agent_groups[group_name]
            removed_count += 1

            redis_client = await self._get_redis_client()
            if redis_client:
                await redis_client.delete(f"group:{group_name}")

        return removed_count

    def get_group_list(self) -> List[Dict]:
        """Get list of all groups with member counts"""
        groups = []
        for group_name, members in self._agent_groups.items():
            groups.append(
                {"group_name": group_name, "member_count": len(members), "members": list(members)}
            )
        return groups
