"""Agent Router - Day 8"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import redis.asyncio as redis


class AgentMessageRouter:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {"redis_url": "redis://localhost:6379"}
        self._redis_client = None
        self.registered_agents = {}
        self.message_delivery_log = []

    async def _get_redis_client(self):
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(
                    self.config["redis_url"], decode_responses=True
                )
            except Exception:
                pass
        return self._redis_client

    async def register_agent(
        self, agent_id: str, agent_type: str, capabilities: Optional[List[str]] = None
    ):
        agent_info = {
            "agent_id": agent_id,
            "capabilities": capabilities or [],
            "status": "active",
        }
        self.registered_agents[agent_id] = agent_info

        redis_client = await self._get_redis_client()
        if redis_client:
            await redis_client.hset("agents", agent_id, json.dumps(agent_info))

    async def route_message(self, message: Dict) -> Dict:
        routing_id = str(uuid.uuid4())
        to_agent = message.get("to_agent")

        envelope = {
            "routing_id": routing_id,
            "to_agent": to_agent,
            "original_message": message,
        }

        if to_agent:
            result = await self._route_direct(envelope)
        else:
            result = await self._route_by_capability(envelope)

        self.message_delivery_log.append({"routing_id": routing_id, "result": result})
        return result

    async def _route_direct(self, envelope: Dict) -> Dict:
        to_agent = envelope["to_agent"]

        if (
            to_agent not in self.registered_agents
            or self.registered_agents[to_agent]["status"] != "active"
        ):
            return {
                "status": "error",
                "error": "Agent not available",
                "routing_id": envelope["routing_id"],
            }

        delivery_result = await self._deliver_message(to_agent, envelope)
        return {
            "status": "delivered",
            "target_agent": to_agent,
            "routing_id": envelope["routing_id"],
            "delivery_result": delivery_result,
        }

    async def _route_by_capability(self, envelope: Dict) -> Dict:
        message = envelope["original_message"]
        required_capability = message.get("required_capability")

        if not required_capability:
            return {
                "status": "error",
                "error": "No capability specified",
                "routing_id": envelope["routing_id"],
            }

        capable_agents = await self._find_agents_by_capability(required_capability)
        if not capable_agents:
            return {
                "status": "error",
                "error": "No capable agents",
                "routing_id": envelope["routing_id"],
            }

        selected_agent = None
        for agent_id in capable_agents:
            if (
                agent_id in self.registered_agents
                and self.registered_agents[agent_id]["status"] == "active"
            ):
                selected_agent = agent_id
                break

        if not selected_agent:
            return {
                "status": "error",
                "error": "No active agents",
                "routing_id": envelope["routing_id"],
            }

        delivery_result = await self._deliver_message(selected_agent, envelope)
        return {
            "status": "delivered",
            "target_agent": selected_agent,
            "routing_method": "capability_based",
            "capability": required_capability,
            "routing_id": envelope["routing_id"],
            "delivery_result": delivery_result,
        }

    async def _find_agents_by_capability(self, capability: str) -> List[str]:
        capable_agents = []
        for agent_id, agent_info in self.registered_agents.items():
            if capability in agent_info.get("capabilities", []):
                capable_agents.append(agent_id)
        return capable_agents

    async def _deliver_message(self, target_agent: str, envelope: Dict) -> Dict:
        return {
            "status": "delivered",
            "message_id": envelope["routing_id"],
            "delivered_at": datetime.utcnow().isoformat(),
            "target_agent": target_agent,
        }

    async def broadcast_message(
        self, message: Dict, target_agents: Optional[List[str]] = None
    ) -> Dict:
        broadcast_id = str(uuid.uuid4())
        if target_agents is None:
            target_agents = [
                agent_id
                for agent_id, info in self.registered_agents.items()
                if info["status"] == "active"
            ]

        delivery_results = []
        for agent_id in target_agents:
            envelope = {
                "routing_id": f"{broadcast_id}_{agent_id}",
                "to_agent": agent_id,
                "original_message": message,
            }
            try:
                await self._deliver_message(agent_id, envelope)
                delivery_results.append({"agent_id": agent_id, "status": "delivered"})
            except Exception:
                delivery_results.append({"agent_id": agent_id, "status": "failed"})

        successful = sum(1 for r in delivery_results if r["status"] == "delivered")
        return {
            "broadcast_id": broadcast_id,
            "total_targets": len(target_agents),
            "successful_deliveries": successful,
        }

    async def update_agent_status(self, agent_id: str, status: str):
        if agent_id in self.registered_agents:
            self.registered_agents[agent_id]["status"] = status

    async def get_routing_statistics(self) -> Dict:
        if not self.message_delivery_log:
            return {"status": "no_data"}

        total = len(self.message_delivery_log)
        successful = sum(
            1 for log in self.message_delivery_log if log["result"]["status"] == "delivered"
        )

        return {
            "total_messages_routed": total,
            "successful_deliveries": successful,
            "delivery_success_rate": successful / total if total > 0 else 0,
        }