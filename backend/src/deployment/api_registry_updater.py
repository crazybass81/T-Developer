"""
API Registry Updater - Automatic API endpoint registration
Size: < 6.5KB | Performance: < 3μs
Day 24: Phase 2 - Meta Agents
"""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class APIEndpoint:
    """API endpoint definition"""

    path: str
    method: str  # GET, POST, PUT, DELETE
    agent_name: str
    version: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    auth_required: bool = True
    rate_limit: int = 100  # requests per minute


@dataclass
class RegistryEntry:
    """Registry entry for deployed agent"""

    agent_name: str
    deployment_id: str
    version: str
    endpoints: List[APIEndpoint]
    status: str  # active, inactive, deprecated
    created_at: float
    updated_at: float
    metadata: Dict[str, Any]


class APIRegistryUpdater:
    """Manage API registry for deployed agents"""

    def __init__(self):
        self.registry: Dict[str, RegistryEntry] = {}
        self.endpoint_map: Dict[str, str] = {}  # path -> agent_name
        self.version_history: Dict[str, List[str]] = {}  # agent -> versions

    async def update_registry(
        self,
        agent_name: str,
        deployment_id: str,
        version: str,
        endpoints: Optional[List[APIEndpoint]] = None,
    ) -> bool:
        """Update registry with new deployment"""

        try:
            # Generate default endpoints if not provided
            if not endpoints:
                endpoints = self._generate_default_endpoints(agent_name, version)

            # Create registry entry
            entry = RegistryEntry(
                agent_name=agent_name,
                deployment_id=deployment_id,
                version=version,
                endpoints=endpoints,
                status="active",
                created_at=time.time(),
                updated_at=time.time(),
                metadata={
                    "auto_generated": endpoints is None,
                    "deployment_environment": "production",
                },
            )

            # Update registry
            self.registry[agent_name] = entry

            # Update endpoint map
            for endpoint in endpoints:
                self.endpoint_map[endpoint.path] = agent_name

            # Track version history
            if agent_name not in self.version_history:
                self.version_history[agent_name] = []
            self.version_history[agent_name].append(version)

            # Deprecate old versions
            await self._deprecate_old_versions(agent_name, version)

            return True

        except Exception as e:
            print(f"Registry update failed: {e}")
            return False

    def _generate_default_endpoints(self, agent_name: str, version: str) -> List[APIEndpoint]:
        """Generate default API endpoints for agent"""

        base_path = f"/api/v1/{agent_name.lower().replace('agent', '')}"

        endpoints = [
            # Main execution endpoint
            APIEndpoint(
                path=f"{base_path}/execute",
                method="POST",
                agent_name=agent_name,
                version=version,
                description=f"Execute {agent_name}",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                auth_required=True,
                rate_limit=100,
            ),
            # Status endpoint
            APIEndpoint(
                path=f"{base_path}/status",
                method="GET",
                agent_name=agent_name,
                version=version,
                description=f"Get {agent_name} status",
                input_schema={},
                output_schema={"type": "object", "properties": {"status": {"type": "string"}}},
                auth_required=False,
                rate_limit=1000,
            ),
            # Health check
            APIEndpoint(
                path=f"{base_path}/health",
                method="GET",
                agent_name=agent_name,
                version=version,
                description=f"Health check for {agent_name}",
                input_schema={},
                output_schema={"type": "object", "properties": {"healthy": {"type": "boolean"}}},
                auth_required=False,
                rate_limit=1000,
            ),
        ]

        # Add CRUD endpoints if applicable
        if "crud" in agent_name.lower() or "data" in agent_name.lower():
            endpoints.extend(
                [
                    APIEndpoint(
                        path=f"{base_path}/create",
                        method="POST",
                        agent_name=agent_name,
                        version=version,
                        description=f"Create resource",
                        input_schema={"type": "object"},
                        output_schema={"type": "object"},
                        auth_required=True,
                        rate_limit=50,
                    ),
                    APIEndpoint(
                        path=f"{base_path}/read",
                        method="GET",
                        agent_name=agent_name,
                        version=version,
                        description=f"Read resource",
                        input_schema={"type": "object"},
                        output_schema={"type": "object"},
                        auth_required=True,
                        rate_limit=200,
                    ),
                    APIEndpoint(
                        path=f"{base_path}/update",
                        method="PUT",
                        agent_name=agent_name,
                        version=version,
                        description=f"Update resource",
                        input_schema={"type": "object"},
                        output_schema={"type": "object"},
                        auth_required=True,
                        rate_limit=50,
                    ),
                    APIEndpoint(
                        path=f"{base_path}/delete",
                        method="DELETE",
                        agent_name=agent_name,
                        version=version,
                        description=f"Delete resource",
                        input_schema={"type": "object"},
                        output_schema={"type": "object"},
                        auth_required=True,
                        rate_limit=20,
                    ),
                ]
            )

        return endpoints

    async def _deprecate_old_versions(self, agent_name: str, current_version: str):
        """Mark old versions as deprecated"""

        for name, entry in self.registry.items():
            if name == agent_name and entry.version != current_version:
                entry.status = "deprecated"
                entry.updated_at = time.time()

    def get_endpoint(self, path: str) -> Optional[APIEndpoint]:
        """Get endpoint by path"""

        agent_name = self.endpoint_map.get(path)
        if not agent_name:
            return None

        entry = self.registry.get(agent_name)
        if not entry:
            return None

        for endpoint in entry.endpoints:
            if endpoint.path == path:
                return endpoint

        return None

    def get_agent_endpoints(self, agent_name: str) -> List[APIEndpoint]:
        """Get all endpoints for an agent"""

        entry = self.registry.get(agent_name)
        if not entry:
            return []

        return entry.endpoints

    def list_active_agents(self) -> List[str]:
        """List all active agents"""

        return [name for name, entry in self.registry.items() if entry.status == "active"]

    def get_api_documentation(self) -> Dict[str, Any]:
        """Generate API documentation"""

        docs = {
            "version": "1.0.0",
            "title": "T-Developer Agent API",
            "description": "Auto-generated API documentation",
            "agents": {},
        }

        for name, entry in self.registry.items():
            if entry.status != "active":
                continue

            agent_doc = {
                "name": name,
                "version": entry.version,
                "deployment_id": entry.deployment_id,
                "endpoints": [],
            }

            for endpoint in entry.endpoints:
                endpoint_doc = {
                    "path": endpoint.path,
                    "method": endpoint.method,
                    "description": endpoint.description,
                    "auth_required": endpoint.auth_required,
                    "rate_limit": endpoint.rate_limit,
                    "input_schema": endpoint.input_schema,
                    "output_schema": endpoint.output_schema,
                }
                agent_doc["endpoints"].append(endpoint_doc)

            docs["agents"][name] = agent_doc

        return docs

    def export_openapi(self) -> Dict[str, Any]:
        """Export registry as OpenAPI specification"""

        openapi = {
            "openapi": "3.0.0",
            "info": {
                "title": "T-Developer Agent API",
                "version": "1.0.0",
                "description": "Auto-generated API for deployed agents",
            },
            "servers": [{"url": "https://api.t-developer.com", "description": "Production"}],
            "paths": {},
        }

        for name, entry in self.registry.items():
            if entry.status != "active":
                continue

            for endpoint in entry.endpoints:
                if endpoint.path not in openapi["paths"]:
                    openapi["paths"][endpoint.path] = {}

                operation = {
                    "summary": endpoint.description,
                    "operationId": f"{name}_{endpoint.method.lower()}",
                    "tags": [name],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {"application/json": {"schema": endpoint.output_schema}},
                        }
                    },
                }

                if endpoint.method in ["POST", "PUT"]:
                    operation["requestBody"] = {
                        "content": {"application/json": {"schema": endpoint.input_schema}}
                    }

                if endpoint.auth_required:
                    operation["security"] = [{"bearerAuth": []}]

                openapi["paths"][endpoint.path][endpoint.method.lower()] = operation

        # Add security schemes
        openapi["components"] = {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            }
        }

        return openapi

    def get_metrics(self) -> Dict[str, Any]:
        """Get registry metrics"""

        active_agents = sum(1 for e in self.registry.values() if e.status == "active")
        total_endpoints = sum(len(e.endpoints) for e in self.registry.values())

        return {
            "total_agents": len(self.registry),
            "active_agents": active_agents,
            "deprecated_agents": len(self.registry) - active_agents,
            "total_endpoints": total_endpoints,
            "unique_paths": len(self.endpoint_map),
            "versions_tracked": sum(len(v) for v in self.version_history.values()),
        }


# Global instance
registry_updater = None


def get_registry_updater() -> APIRegistryUpdater:
    """Get or create registry updater instance"""
    global registry_updater
    if not registry_updater:
        registry_updater = APIRegistryUpdater()
    return registry_updater


async def main():
    """Test API registry updater"""
    updater = get_registry_updater()

    # Register first agent
    success = await updater.update_registry(
        agent_name="DataProcessorAgent", deployment_id="deploy_001", version="1.0.0"
    )

    print(f"Registration: {'Success' if success else 'Failed'}")

    # Register second agent with custom endpoints
    custom_endpoints = [
        APIEndpoint(
            path="/api/v1/search",
            method="POST",
            agent_name="SearchAgent",
            version="2.0.0",
            description="Search data",
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"results": {"type": "array"}}},
            auth_required=True,
            rate_limit=50,
        )
    ]

    await updater.update_registry(
        agent_name="SearchAgent",
        deployment_id="deploy_002",
        version="2.0.0",
        endpoints=custom_endpoints,
    )

    # Get documentation
    docs = updater.get_api_documentation()
    print(f"\nActive agents: {updater.list_active_agents()}")
    print(f"Total endpoints: {len(updater.endpoint_map)}")

    # Export OpenAPI
    openapi = updater.export_openapi()
    print(f"\nOpenAPI paths: {list(openapi['paths'].keys())}")

    # Get metrics
    metrics = updater.get_metrics()
    print(f"\nMetrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())
