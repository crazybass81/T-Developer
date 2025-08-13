"""
AgentCore API Endpoint Registry
Manages all deployed agent endpoints
"""
import asyncio
import json
import time
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import boto3


class EndpointStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPLOYING = "deploying"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class EndpointInfo:
    id: str
    agent_name: str
    version: str
    url: str
    method: str
    status: EndpointStatus
    created_at: float
    updated_at: float
    health_check_url: Optional[str] = None
    metadata: Optional[Dict] = None


class EndpointRegistry:
    def __init__(self, storage_path: str = "/tmp/endpoints.json"):
        self.storage_path = storage_path
        self.endpoints: Dict[str, EndpointInfo] = {}
        self.load_registry()
        self.bedrock_client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

    def load_registry(self):
        """Load endpoints from persistent storage"""
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                for ep_id, ep_data in data.items():
                    self.endpoints[ep_id] = EndpointInfo(
                        **{k: EndpointStatus(v) if k == "status" else v for k, v in ep_data.items()}
                    )
        except FileNotFoundError:
            self.endpoints = {}

    def save_registry(self):
        """Persist endpoints to storage"""
        data = {
            ep_id: {
                k: v.value if isinstance(v, EndpointStatus) else v for k, v in asdict(ep).items()
            }
            for ep_id, ep in self.endpoints.items()
        }
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def register_endpoint(
        self,
        agent_name: str,
        version: str,
        url: str,
        method: str = "POST",
        health_check_url: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """Register a new agent endpoint"""
        ep_id = f"{agent_name}_{version}_{int(time.time())}"

        endpoint = EndpointInfo(
            id=ep_id,
            agent_name=agent_name,
            version=version,
            url=url,
            method=method,
            status=EndpointStatus.DEPLOYING,
            created_at=time.time(),
            updated_at=time.time(),
            health_check_url=health_check_url or f"{url}/health",
            metadata=metadata or {},
        )

        self.endpoints[ep_id] = endpoint
        self.save_registry()
        return ep_id

    def update_status(self, endpoint_id: str, status: EndpointStatus):
        """Update endpoint status"""
        if endpoint_id in self.endpoints:
            self.endpoints[endpoint_id].status = status
            self.endpoints[endpoint_id].updated_at = time.time()
            self.save_registry()

    def get_endpoint(self, endpoint_id: str) -> Optional[EndpointInfo]:
        """Get endpoint by ID"""
        return self.endpoints.get(endpoint_id)

    def get_agent_endpoints(self, agent_name: str) -> List[EndpointInfo]:
        """Get all endpoints for a specific agent"""
        return [ep for ep in self.endpoints.values() if ep.agent_name == agent_name]

    def get_active_endpoints(self) -> List[EndpointInfo]:
        """Get all active endpoints"""
        return [ep for ep in self.endpoints.values() if ep.status == EndpointStatus.ACTIVE]

    def remove_endpoint(self, endpoint_id: str) -> bool:
        """Remove endpoint from registry"""
        if endpoint_id in self.endpoints:
            del self.endpoints[endpoint_id]
            self.save_registry()
            return True
        return False

    async def health_check(self, endpoint_id: str) -> bool:
        """Check endpoint health"""
        endpoint = self.get_endpoint(endpoint_id)
        if not endpoint:
            return False

        try:
            # Simulate health check (in production, make actual HTTP request)
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint.health_check_url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        self.update_status(endpoint_id, EndpointStatus.ACTIVE)
                        return True
                    else:
                        self.update_status(endpoint_id, EndpointStatus.ERROR)
                        return False
        except Exception as e:
            self.update_status(endpoint_id, EndpointStatus.ERROR)
            return False

    async def health_check_all(self):
        """Health check all endpoints"""
        tasks = [self.health_check(ep_id) for ep_id in self.endpoints.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        status_counts = {}
        for endpoint in self.endpoints.values():
            status_counts[endpoint.status.value] = status_counts.get(endpoint.status.value, 0) + 1

        agent_counts = {}
        for endpoint in self.endpoints.values():
            agent_counts[endpoint.agent_name] = agent_counts.get(endpoint.agent_name, 0) + 1

        return {
            "total_endpoints": len(self.endpoints),
            "status_breakdown": status_counts,
            "agents": agent_counts,
            "active_count": len(self.get_active_endpoints()),
        }

    def create_api_gateway_mapping(self) -> Dict[str, Any]:
        """Create API Gateway mapping configuration"""
        mapping = {"version": "1.0", "endpoints": []}

        for endpoint in self.get_active_endpoints():
            mapping["endpoints"].append(
                {
                    "path": f"/agents/{endpoint.agent_name}/{endpoint.version}",
                    "method": endpoint.method,
                    "backend_url": endpoint.url,
                    "timeout": 30000,
                    "cache_enabled": False,
                    "auth_required": True,
                }
            )

        return mapping


# Example usage
if __name__ == "__main__":
    registry = EndpointRegistry()

    # Register some endpoints
    ep_id1 = registry.register_endpoint(
        agent_name="nl_input",
        version="2.0.0",
        url="https://api.agentcore.com/nl_input",
        metadata={"region": "us-east-1"},
    )

    ep_id2 = registry.register_endpoint(
        agent_name="generation", version="2.0.0", url="https://api.agentcore.com/generation"
    )

    # Update status
    registry.update_status(ep_id1, EndpointStatus.ACTIVE)
    registry.update_status(ep_id2, EndpointStatus.ACTIVE)

    # Get statistics
    stats = registry.get_statistics()
    print(f"Registry Statistics: {json.dumps(stats, indent=2)}")

    # Create API Gateway mapping
    mapping = registry.create_api_gateway_mapping()
    print(f"API Gateway Mapping: {json.dumps(mapping, indent=2)}")
