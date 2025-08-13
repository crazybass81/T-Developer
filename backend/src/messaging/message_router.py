"""Message Router - Day 9: Enhanced API Gateway Integration

Simple message router for API Gateway to agent communication
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from .agent_registry import AgentCapabilityRegistry
from .message_queue import MessageQueue


class MessageRouter:
    """Message Router for API Gateway to Agent communication"""

    def __init__(self, agent_registry: AgentCapabilityRegistry, config: Optional[Dict] = None):
        self.agent_registry = agent_registry
        self.config = config or {}
        self.message_queue = MessageQueue("message_router_queue", config)

    async def route_message(self, message: Dict) -> Dict:
        """Route message to appropriate agent"""
        try:
            # Extract target agent
            to_agent = message.get("to_agent")
            if not to_agent:
                return {
                    "status": "failed",
                    "error": "No target agent specified",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Check if agent is registered
            agent_info = self.agent_registry.get_agent_capabilities(to_agent)
            if not agent_info:
                return {
                    "status": "failed",
                    "error": f"Agent {to_agent} not found",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Enqueue message
            message_id = await self.message_queue.enqueue(message)

            return {
                "status": "routed",
                "message_id": message_id,
                "to_agent": to_agent,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

    async def broadcast_message(self, message: Dict, capabilities: List[str]) -> Dict:
        """Broadcast message to agents with specific capabilities"""
        try:
            target_agents = []
            for capability in capabilities:
                agents = self.agent_registry.find_agents_by_capability(capability)
                target_agents.extend(agents)

            # Remove duplicates
            target_agents = list(set(target_agents))

            if not target_agents:
                return {
                    "status": "failed",
                    "error": f"No agents found with capabilities: {capabilities}",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Send to all target agents
            results = []
            for agent_id in target_agents:
                broadcast_message = {
                    **message,
                    "to_agent": agent_id,
                    "broadcast": True,
                    "original_capabilities": capabilities,
                }

                result = await self.route_message(broadcast_message)
                results.append({"agent_id": agent_id, "result": result})

            return {
                "status": "broadcast",
                "target_agents": target_agents,
                "results": results,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

    def get_routing_stats(self) -> Dict:
        """Get routing statistics"""
        return {
            "registered_agents": len(self.agent_registry._local_registry),
            "router_status": "active",
            "timestamp": datetime.utcnow().isoformat(),
        }
