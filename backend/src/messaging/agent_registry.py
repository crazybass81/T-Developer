"""Agent Capability Registry - Day 8"""

import json
from datetime import datetime
from typing import Dict, List, Optional

import redis.asyncio as redis


class AgentCapabilityRegistry:
    """Registry for agent capabilities"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {"redis_url": "redis://localhost:6379"}
        self._redis_client = None
        self._local_registry = {}  # agent_id -> capabilities

    async def _get_redis_client(self):
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(self.config["redis_url"], decode_responses=True)
            except Exception:
                pass
        return self._redis_client

    def register_agent_capabilities(self, agent_id: str, capabilities_info: Dict):
        self._local_registry[agent_id] = {
            "agent_id": agent_id,
            "registered_at": datetime.utcnow().isoformat(),
            **capabilities_info,
        }

    async def register_agent_capabilities_async(self, agent_id: str, capabilities_info: Dict):
        self.register_agent_capabilities(agent_id, capabilities_info)
        r = await self._get_redis_client()
        if r:
            await r.hset("agent_capabilities", agent_id, json.dumps(self._local_registry[agent_id]))

    def find_agents_by_capability(self, capability: str) -> List[str]:
        return [
            aid
            for aid, info in self._local_registry.items()
            if capability in info.get("capabilities", [])
        ]

    async def find_agents_by_capability_async(self, capability: str) -> List[str]:
        r = await self._get_redis_client()
        if r:
            return list(await r.smembers(f"capability_index:{capability}"))
        return self.find_agents_by_capability(capability)

    def find_agents_by_input_type(self, input_type: str) -> List[str]:
        return [
            aid
            for aid, info in self._local_registry.items()
            if input_type in info.get("input_types", [])
        ]

    async def find_agents_by_input_type_async(self, input_type: str) -> List[str]:
        r = await self._get_redis_client()
        if r:
            return list(await r.smembers(f"input_type_index:{input_type}"))
        return self.find_agents_by_input_type(input_type)

    def find_agents_by_output_type(self, output_type: str) -> List[str]:
        return [
            aid
            for aid, info in self._local_registry.items()
            if output_type in info.get("output_types", [])
        ]

    def get_agent_capabilities(self, agent_id: str) -> Optional[Dict]:
        return self._local_registry.get(agent_id)

    async def get_agent_capabilities_async(self, agent_id: str) -> Optional[Dict]:
        r = await self._get_redis_client()
        if r:
            data = await r.hget("agent_capabilities", agent_id)
            if data:
                return json.loads(data)
        return self._local_registry.get(agent_id)

    def find_compatible_agents(self, required_capabilities: List[str]) -> List[str]:
        if not required_capabilities:
            return list(self._local_registry.keys())
        compatible = None
        for cap in required_capabilities:
            agents = set(self.find_agents_by_capability(cap))
            compatible = agents if compatible is None else compatible.intersection(agents)
        return list(compatible or [])

    def get_capability_statistics(self) -> Dict:
        if not self._local_registry:
            return {"status": "no_agents_registered"}
        return {
            "total_agents": len(self._local_registry),
            "agent_types": list(
                set(info.get("type", "unknown") for info in self._local_registry.values())
            ),
        }

    async def update_agent_status(self, agent_id: str, status: str):
        if agent_id in self._local_registry:
            self._local_registry[agent_id]["status"] = status
            self._local_registry[agent_id]["last_updated"] = datetime.utcnow().isoformat()
            r = await self._get_redis_client()
            if r:
                await r.hset(
                    "agent_capabilities", agent_id, json.dumps(self._local_registry[agent_id])
                )

    async def remove_agent(self, agent_id: str):
        if agent_id in self._local_registry:
            info = self._local_registry[agent_id]
            del self._local_registry[agent_id]
            r = await self._get_redis_client()
            if r:
                await r.hdel("agent_capabilities", agent_id)
                for cap in info.get("capabilities", []):
                    await r.srem(f"capability_index:{cap}", agent_id)
                for inp in info.get("input_types", []):
                    await r.srem(f"input_type_index:{inp}", agent_id)
                for out in info.get("output_types", []):
                    await r.srem(f"output_type_index:{out}", agent_id)

    def list_all_agents(self) -> List[Dict]:
        return list(self._local_registry.values())

    async def get_all_agents(self) -> List[Dict]:
        r = await self._get_redis_client()
        if r:
            try:
                data = await r.hgetall("agent_capabilities")
                if data:
                    return [json.loads(d) for d in data.values()]
            except Exception:
                pass
        return list(self._local_registry.values())
