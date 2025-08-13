"""
Agent Capability Registry
Day 8: Message Queue System
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

import redis.asyncio as redis


class AgentCapabilityRegistry:
    """Registry for agent capabilities and routing information"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {"redis_url": "redis://localhost:6379"}
        self._redis_client = None
        self._local_registry = {}  # agent_id -> capabilities

    async def _get_redis_client(self):
        """Get or create Redis client connection"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(self.config["redis_url"], decode_responses=True)
            except Exception:
                pass
        return self._redis_client

    def register_agent_capabilities(self, agent_id: str, capabilities_info: Dict):
        """Register agent capabilities"""
        self._local_registry[agent_id] = {
            "agent_id": agent_id,
            "registered_at": datetime.utcnow().isoformat(),
            **capabilities_info,
        }

    async def register_agent_capabilities_async(self, agent_id: str, capabilities_info: Dict):
        """Async register agent capabilities"""
        self.register_agent_capabilities(agent_id, capabilities_info)
        redis_client = await self._get_redis_client()
        if redis_client:
            await redis_client.hset("agent_capabilities", agent_id, json.dumps(self._local_registry[agent_id]))

    def find_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents that have specific capability"""
        matching_agents = []

        for agent_id, agent_info in self._local_registry.items():
            capabilities = agent_info.get("capabilities", [])
            if capability in capabilities:
                matching_agents.append(agent_id)

        return matching_agents

    async def find_agents_by_capability_async(self, capability: str) -> List[str]:
        """Async find agents by capability"""
        redis_client = await self._get_redis_client()
        if redis_client:
            return list(await redis_client.smembers(f"capability_index:{capability}"))
        return self.find_agents_by_capability(capability)

    def find_agents_by_input_type(self, input_type: str) -> List[str]:
        """Find agents that accept specific input type"""
        matching_agents = []

        for agent_id, agent_info in self._local_registry.items():
            input_types = agent_info.get("input_types", [])
            if input_type in input_types:
                matching_agents.append(agent_id)

        return matching_agents

    async def find_agents_by_input_type_async(self, input_type: str) -> List[str]:
        """Async find agents by input type"""
        redis_client = await self._get_redis_client()
        if redis_client:
            return list(await redis_client.smembers(f"input_type_index:{input_type}"))
        return self.find_agents_by_input_type(input_type)

    def find_agents_by_output_type(self, output_type: str) -> List[str]:
        """Find agents that produce specific output type"""
        matching_agents = []

        for agent_id, agent_info in self._local_registry.items():
            output_types = agent_info.get("output_types", [])
            if output_type in output_types:
                matching_agents.append(agent_id)

        return matching_agents

    def get_agent_capabilities(self, agent_id: str) -> Optional[Dict]:
        """Get capabilities for specific agent"""
        return self._local_registry.get(agent_id)

    async def get_agent_capabilities_async(self, agent_id: str) -> Optional[Dict]:
        """Async get agent capabilities"""
        redis_client = await self._get_redis_client()
        if redis_client:
            agent_data = await redis_client.hget("agent_capabilities", agent_id)
            if agent_data:
                return json.loads(agent_data)
        return self._local_registry.get(agent_id)

    def find_compatible_agents(self, required_capabilities: List[str]) -> List[str]:
        """Find agents with all required capabilities"""
        if not required_capabilities:
            return list(self._local_registry.keys())
        compatible = None
        for capability in required_capabilities:
            agents = set(self.find_agents_by_capability(capability))
            compatible = agents if compatible is None else compatible.intersection(agents)
        return list(compatible or [])

    def get_capability_statistics(self) -> Dict:
        """Get capability statistics"""
        if not self._local_registry:
            return {"status": "no_agents_registered"}
        return {
            "total_agents": len(self._local_registry),
            "agent_types": list(set(info.get("type", "unknown") for info in self._local_registry.values())),
        }

    async def update_agent_status(self, agent_id: str, status: str):
        """Update agent operational status"""
        if agent_id in self._local_registry:
            self._local_registry[agent_id]["status"] = status
            self._local_registry[agent_id]["last_updated"] = datetime.utcnow().isoformat()

            redis_client = await self._get_redis_client()
            if redis_client:
                await redis_client.hset(
                    "agent_capabilities", agent_id, json.dumps(self._local_registry[agent_id])
                )

    async def remove_agent(self, agent_id: str):
        """Remove agent from registry"""
        if agent_id in self._local_registry:
            agent_info = self._local_registry[agent_id]
            del self._local_registry[agent_id]

            redis_client = await self._get_redis_client()
            if redis_client:
                # Remove from main registry
                await redis_client.hdel("agent_capabilities", agent_id)

                # Remove from indexes
                for capability in agent_info.get("capabilities", []):
                    await redis_client.srem(f"capability_index:{capability}", agent_id)
                for input_type in agent_info.get("input_types", []):
                    await redis_client.srem(f"input_type_index:{input_type}", agent_id)
                for output_type in agent_info.get("output_types", []):
                    await redis_client.srem(f"output_type_index:{output_type}", agent_id)

    def list_all_agents(self) -> List[Dict]:
        """List all agents"""
        return list(self._local_registry.values())
