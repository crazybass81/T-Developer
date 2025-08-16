"""A2A (Agent-to-Agent) Broker for external agent integration.

Phase 4: A2A External Integration
P4-T1: A2A Broker Setup
"""

import asyncio
import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

import aiohttp
import yaml

logger = logging.getLogger(__name__)


class BrokerStatus(Enum):
    """Broker operational status."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class BrokerConfig:
    """Configuration for A2A broker."""

    port: int = 8080
    max_connections: int = 100
    timeout_seconds: int = 30
    enable_mtls: bool = True
    enable_audit: bool = True
    rate_limit_per_minute: int = 60
    retry_attempts: int = 3
    retry_delay_seconds: int = 1


@dataclass
class AgentCapability:
    """Definition of an agent capability."""

    name: str
    version: str = "1.0.0"
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def matches(self, required_tags: list[str]) -> bool:
        """Check if capability matches required tags."""
        return any(tag in self.tags for tag in required_tags)


@dataclass
class AgentRequest:
    """Request to an external agent."""

    agent_id: str
    capability: str
    payload: dict[str, Any]
    timeout: Optional[int] = None
    trace_id: Optional[str] = None


@dataclass
class AgentResponse:
    """Response from an external agent."""

    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: Optional[int] = None


class AgentRegistry:
    """Registry for external agents and their capabilities."""

    def __init__(self):
        """Initialize agent registry."""
        self._agents: dict[str, dict[str, Any]] = {}
        self._capabilities: dict[str, list[str]] = defaultdict(list)

    def register(self, agent_id: str, endpoint: str, capabilities: list[AgentCapability]) -> str:
        """Register an external agent."""
        self._agents[agent_id] = {
            "endpoint": endpoint,
            "capabilities": capabilities,
            "registered_at": datetime.now().isoformat(),
        }

        # Index capabilities
        for cap in capabilities:
            self._capabilities[cap.name].append(agent_id)
            for tag in cap.tags:
                self._capabilities[f"tag:{tag}"].append(agent_id)

        logger.info(f"Registered agent {agent_id} with {len(capabilities)} capabilities")
        return agent_id

    def unregister(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self._agents:
            # Remove from capability index
            agent_data = self._agents[agent_id]
            for cap in agent_data["capabilities"]:
                if cap.name in self._capabilities:
                    self._capabilities[cap.name].remove(agent_id)
                for tag in cap.tags:
                    key = f"tag:{tag}"
                    if key in self._capabilities and agent_id in self._capabilities[key]:
                        self._capabilities[key].remove(agent_id)

            del self._agents[agent_id]
            logger.info(f"Unregistered agent {agent_id}")

    def is_registered(self, agent_id: str) -> bool:
        """Check if agent is registered."""
        return agent_id in self._agents

    def discover(
        self, tags: Optional[list[str]] = None, capability: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Discover agents by tags or capability."""
        matching_agents = set()

        if tags:
            for tag in tags:
                key = f"tag:{tag}"
                if key in self._capabilities:
                    matching_agents.update(self._capabilities[key])

        if capability:
            if capability in self._capabilities:
                matching_agents.update(self._capabilities[capability])

        # Return agent details
        return [
            {"agent_id": aid, **self._agents[aid]} for aid in matching_agents if aid in self._agents
        ]


class PolicyEngine:
    """Policy engine for capability and agent control."""

    def __init__(self):
        """Initialize policy engine."""
        self.whitelist_capabilities: set[str] = set()
        self.whitelist_agents: set[str] = set()
        self.blacklist_capabilities: set[str] = set()
        self.blacklist_agents: set[str] = set()
        self.rate_limits: dict[str, int] = {}

    async def load_policy(self, policy_file: Path) -> None:
        """Load policy configuration from file."""
        with open(policy_file) as f:
            config = yaml.safe_load(f)

        # Load whitelist
        if "whitelist" in config:
            self.whitelist_capabilities = set(config["whitelist"].get("capabilities", []))
            self.whitelist_agents = set(config["whitelist"].get("agents", []))

        # Load blacklist
        if "blacklist" in config:
            self.blacklist_capabilities = set(config["blacklist"].get("capabilities", []))
            self.blacklist_agents = set(config["blacklist"].get("agents", []))

        # Load rate limits
        if "rate_limits" in config:
            self.rate_limits = config["rate_limits"]

        logger.info(f"Loaded policy from {policy_file}")

    def is_capability_allowed(self, capability: str) -> bool:
        """Check if capability is allowed."""
        if capability in self.blacklist_capabilities:
            return False
        if self.whitelist_capabilities:
            return capability in self.whitelist_capabilities
        return True

    def is_agent_allowed(self, agent_id: str) -> bool:
        """Check if agent is allowed."""
        # Check blacklist patterns
        for pattern in self.blacklist_agents:
            if pattern.endswith("*"):
                if agent_id.startswith(pattern[:-1]):
                    return False
            elif agent_id == pattern:
                return False

        # Check whitelist patterns
        if self.whitelist_agents:
            for pattern in self.whitelist_agents:
                if pattern.endswith("*"):
                    if agent_id.startswith(pattern[:-1]):
                        return True
                elif agent_id == pattern:
                    return True
            return False

        return True

    async def validate_request(self, request: AgentRequest) -> bool:
        """Validate request against policy."""
        if not self.is_agent_allowed(request.agent_id):
            logger.warning(f"Agent {request.agent_id} not allowed by policy")
            return False

        if not self.is_capability_allowed(request.capability):
            logger.warning(f"Capability {request.capability} not allowed by policy")
            return False

        return True


class AuthManager:
    """Authentication and authorization manager."""

    def __init__(self):
        """Initialize auth manager."""
        self._agents: dict[str, str] = {}  # agent_id -> api_key
        self._mtls_enabled = False
        self._cert_path: Optional[Path] = None
        self._key_path: Optional[Path] = None
        self._ca_path: Optional[Path] = None

    async def setup_mtls(self, cert_path: Path, key_path: Path, ca_path: Path) -> bool:
        """Setup mTLS configuration."""
        if cert_path.exists() and key_path.exists() and ca_path.exists():
            self._cert_path = cert_path
            self._key_path = key_path
            self._ca_path = ca_path
            self._mtls_enabled = True
            logger.info("mTLS configured successfully")
            return True
        return False

    def is_mtls_enabled(self) -> bool:
        """Check if mTLS is enabled."""
        return self._mtls_enabled

    async def register_agent(self, agent_id: str, api_key: str) -> None:
        """Register agent credentials."""
        self._agents[agent_id] = api_key
        logger.info(f"Registered credentials for agent {agent_id}")

    async def authenticate(self, agent_id: str, api_key: str) -> bool:
        """Authenticate agent."""
        if agent_id not in self._agents:
            return False
        return self._agents[agent_id] == api_key


class RateLimiter:
    """Rate limiting for agent requests."""

    def __init__(self):
        """Initialize rate limiter."""
        self._limits: dict[str, int] = {}  # agent_id -> requests_per_minute
        self._windows: dict[str, float] = {}  # agent_id -> window_start_time
        self._counts: dict[str, int] = defaultdict(int)  # agent_id -> request_count

    def set_limit(self, agent_id: str, requests_per_minute: int) -> None:
        """Set rate limit for agent."""
        self._limits[agent_id] = requests_per_minute
        self._windows[agent_id] = time.time()

    async def check_rate_limit(self, agent_id: str) -> bool:
        """Check if request is within rate limit."""
        if agent_id not in self._limits:
            return True

        current_time = time.time()
        window_start = self._windows.get(agent_id, current_time)

        # Reset window if more than 60 seconds have passed
        if current_time - window_start > 60:
            self._windows[agent_id] = current_time
            self._counts[agent_id] = 0
            return True

        # Check if within limit
        return self._counts[agent_id] < self._limits[agent_id]

    async def record_request(self, agent_id: str) -> None:
        """Record a request for rate limiting."""
        if agent_id in self._limits:
            self._counts[agent_id] += 1


class AuditLogger:
    """Audit logging for all broker operations."""

    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize audit logger."""
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self._logs: list[dict[str, Any]] = []

    async def log_request(self, request: AgentRequest, response: AgentResponse) -> None:
        """Log agent request and response."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": request.agent_id,
            "capability": request.capability,
            "success": response.success,
            "duration_ms": response.duration_ms,
            "error": response.error,
        }

        self._logs.append(log_entry)

        # Write to file
        log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    async def query(
        self, start_time: Optional[datetime] = None, agent_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Query audit logs."""
        results = self._logs

        if start_time:
            results = [
                log for log in results if datetime.fromisoformat(log["timestamp"]) >= start_time
            ]

        if agent_id:
            results = [log for log in results if log["agent_id"] == agent_id]

        return results


class MessageRouter:
    """Message routing for A2A communication."""

    def __init__(self):
        """Initialize message router."""
        self.routes: dict[str, str] = {}  # capability -> agent_id
        self.load_balancer = LoadBalancer()
        self.protocol_translator = ProtocolTranslator()

    def add_route(self, capability: str, agent_id: str) -> None:
        """Add routing rule for capability."""
        if capability not in self.routes:
            self.routes[capability] = []
        if isinstance(self.routes[capability], str):
            self.routes[capability] = [self.routes[capability]]
        self.routes[capability].append(agent_id)

    def route_message(self, capability: str) -> Optional[str]:
        """Route message to appropriate agent."""
        if capability not in self.routes:
            return None

        agents = self.routes[capability]
        if isinstance(agents, str):
            return agents
        if isinstance(agents, list) and agents:
            return self.load_balancer.select_agent(agents)
        return None


class LoadBalancer:
    """Load balancer for distributing requests across agents."""

    def __init__(self):
        """Initialize load balancer."""
        self.agent_metrics: dict[str, dict[str, Any]] = {}
        self.strategy = "round_robin"
        self._counters: dict[str, int] = {}

    def select_agent(self, agent_ids: list[str]) -> str:
        """Select agent based on load balancing strategy."""
        if not agent_ids:
            raise ValueError("No agents available")

        if self.strategy == "round_robin":
            return self._round_robin_select(agent_ids)
        elif self.strategy == "least_connections":
            return self._least_connections_select(agent_ids)
        elif self.strategy == "response_time":
            return self._response_time_select(agent_ids)
        else:
            return agent_ids[0]  # Default to first

    def _round_robin_select(self, agent_ids: list[str]) -> str:
        """Round-robin selection."""
        key = ":".join(sorted(agent_ids))
        if key not in self._counters:
            self._counters[key] = 0

        index = self._counters[key] % len(agent_ids)
        self._counters[key] += 1
        return agent_ids[index]

    def _least_connections_select(self, agent_ids: list[str]) -> str:
        """Select agent with least active connections."""
        min_connections = float("inf")
        selected_agent = agent_ids[0]

        for agent_id in agent_ids:
            connections = self.agent_metrics.get(agent_id, {}).get("connections", 0)
            if connections < min_connections:
                min_connections = connections
                selected_agent = agent_id

        return selected_agent

    def _response_time_select(self, agent_ids: list[str]) -> str:
        """Select agent with best response time."""
        min_response_time = float("inf")
        selected_agent = agent_ids[0]

        for agent_id in agent_ids:
            response_time = self.agent_metrics.get(agent_id, {}).get("avg_response_time", 0)
            if response_time < min_response_time:
                min_response_time = response_time
                selected_agent = agent_id

        return selected_agent

    def update_agent_metrics(self, agent_id: str, metrics: dict[str, Any]) -> None:
        """Update agent performance metrics."""
        self.agent_metrics[agent_id] = metrics


class ProtocolTranslator:
    """Protocol translation for different agent communication formats."""

    def __init__(self):
        """Initialize protocol translator."""
        self.translators: dict[str, Callable] = {
            "json": self._json_translator,
            "grpc": self._grpc_translator,
            "rest": self._rest_translator,
        }

    def translate(
        self, message: dict[str, Any], from_protocol: str, to_protocol: str
    ) -> dict[str, Any]:
        """Translate message between protocols."""
        if from_protocol == to_protocol:
            return message

        # First convert to common format
        common_format = self._to_common_format(message, from_protocol)

        # Then convert to target protocol
        return self._from_common_format(common_format, to_protocol)

    def _to_common_format(self, message: dict[str, Any], protocol: str) -> dict[str, Any]:
        """Convert message to common internal format."""
        if protocol in self.translators:
            return self.translators[protocol](message, "to_common")
        return message

    def _from_common_format(self, message: dict[str, Any], protocol: str) -> dict[str, Any]:
        """Convert from common format to target protocol."""
        if protocol in self.translators:
            return self.translators[protocol](message, "from_common")
        return message

    def _json_translator(self, message: dict[str, Any], direction: str) -> dict[str, Any]:
        """JSON protocol translator."""
        return message  # JSON is our common format

    def _grpc_translator(self, message: dict[str, Any], direction: str) -> dict[str, Any]:
        """gRPC protocol translator."""
        if direction == "to_common":
            # Convert gRPC message to common format
            return {
                "type": message.get("type", "request"),
                "payload": message.get("data", {}),
                "metadata": message.get("metadata", {}),
            }
        else:
            # Convert common format to gRPC
            return {
                "type": message.get("type", "request"),
                "data": message.get("payload", {}),
                "metadata": message.get("metadata", {}),
            }

    def _rest_translator(self, message: dict[str, Any], direction: str) -> dict[str, Any]:
        """REST protocol translator."""
        if direction == "to_common":
            return {
                "type": "request",
                "payload": message.get("body", {}),
                "metadata": {
                    "method": message.get("method", "POST"),
                    "headers": message.get("headers", {}),
                    "query": message.get("query", {}),
                },
            }
        else:
            return {
                "method": message.get("metadata", {}).get("method", "POST"),
                "body": message.get("payload", {}),
                "headers": message.get("metadata", {}).get("headers", {}),
                "query": message.get("metadata", {}).get("query", {}),
            }


class HealthChecker:
    """Health checking for registered agents."""

    def __init__(self, check_interval: int = 60):
        """Initialize health checker."""
        self.check_interval = check_interval
        self.agent_status: dict[str, dict[str, Any]] = {}
        self.unhealthy_agents: set[str] = set()
        self._running = False
        self._check_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start health checking."""
        if self._running:
            return

        self._running = True
        self._check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Health checker started")

    async def stop(self) -> None:
        """Stop health checking."""
        if not self._running:
            return

        self._running = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        logger.info("Health checker stopped")

    async def check_agent_health(self, agent_id: str, endpoint: str) -> bool:
        """Check health of a specific agent."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{endpoint}/health", timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.agent_status[agent_id] = {
                            "healthy": True,
                            "last_check": time.time(),
                            "response_time": time.time() - time.time(),
                            "details": data,
                        }
                        if agent_id in self.unhealthy_agents:
                            self.unhealthy_agents.remove(agent_id)
                        return True
                    else:
                        self._mark_unhealthy(agent_id, f"HTTP {response.status}")
                        return False

        except Exception as e:
            self._mark_unhealthy(agent_id, str(e))
            return False

    def _mark_unhealthy(self, agent_id: str, reason: str) -> None:
        """Mark agent as unhealthy."""
        self.agent_status[agent_id] = {
            "healthy": False,
            "last_check": time.time(),
            "reason": reason,
        }
        self.unhealthy_agents.add(agent_id)
        logger.warning(f"Agent {agent_id} marked unhealthy: {reason}")

    async def _health_check_loop(self) -> None:
        """Background health checking loop."""
        while self._running:
            try:
                # This would check all registered agents
                # Implementation depends on registry integration
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(self.check_interval)


class A2ABroker:
    """Main A2A broker for agent orchestration."""

    def __init__(self, config: BrokerConfig):
        """Initialize A2A broker."""
        self.config = config
        self.status = BrokerStatus.STOPPED
        self.registry = AgentRegistry()
        self.policy = PolicyEngine()
        self.auth = AuthManager()
        self.limiter = RateLimiter()
        self.audit = AuditLogger()
        self._server: Optional[asyncio.Server] = None

        # Enhanced components
        self.router = MessageRouter()
        self.health_checker = HealthChecker()
        self.discovery_service = AgentDiscoveryService()


class AgentDiscoveryService:
    """Service discovery for A2A agents."""

    def __init__(self):
        """Initialize discovery service."""
        self.service_registry: dict[str, dict[str, Any]] = {}
        self.service_tags: dict[str, list[str]] = defaultdict(list)
        self.heartbeat_interval = 30
        self.service_ttl = 90

    def register_service(
        self,
        service_id: str,
        service_name: str,
        endpoint: str,
        port: int,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Register a service for discovery."""
        service_info = {
            "id": service_id,
            "name": service_name,
            "endpoint": endpoint,
            "port": port,
            "tags": tags or [],
            "metadata": metadata or {},
            "registered_at": time.time(),
            "last_heartbeat": time.time(),
            "healthy": True,
        }

        self.service_registry[service_id] = service_info

        # Index by tags
        for tag in tags or []:
            self.service_tags[tag].append(service_id)

        logger.info(f"Registered service: {service_name} ({service_id})")

    def deregister_service(self, service_id: str) -> bool:
        """Deregister a service."""
        if service_id not in self.service_registry:
            return False

        service = self.service_registry[service_id]

        # Remove from tag index
        for tag in service.get("tags", []):
            if tag in self.service_tags and service_id in self.service_tags[tag]:
                self.service_tags[tag].remove(service_id)

        del self.service_registry[service_id]
        logger.info(f"Deregistered service: {service_id}")
        return True

    def discover_services(
        self,
        service_name: Optional[str] = None,
        tags: Optional[list[str]] = None,
        healthy_only: bool = True,
    ) -> list[dict[str, Any]]:
        """Discover services by name or tags."""
        matching_services = []

        for service_id, service in self.service_registry.items():
            # Filter by health
            if healthy_only and not service.get("healthy", False):
                continue

            # Filter by service name
            if service_name and service.get("name") != service_name:
                continue

            # Filter by tags
            if tags:
                service_tags = set(service.get("tags", []))
                required_tags = set(tags)
                if not required_tags.intersection(service_tags):
                    continue

            matching_services.append(service)

        return matching_services

    def heartbeat(self, service_id: str) -> bool:
        """Update service heartbeat."""
        if service_id not in self.service_registry:
            return False

        self.service_registry[service_id]["last_heartbeat"] = time.time()
        self.service_registry[service_id]["healthy"] = True
        return True

    def check_service_health(self) -> None:
        """Check service health based on heartbeats."""
        current_time = time.time()

        for service_id, service in self.service_registry.items():
            last_heartbeat = service.get("last_heartbeat", 0)
            if current_time - last_heartbeat > self.service_ttl:
                service["healthy"] = False
                logger.warning(f"Service {service_id} marked unhealthy due to missing heartbeat")

    async def start(self) -> None:
        """Start the broker."""
        self.status = BrokerStatus.STARTING

        try:
            # Start enhanced components
            await self.health_checker.start()

            # Start server (mocked for testing)
            await self._start_server()
            self.status = BrokerStatus.RUNNING
            logger.info(f"A2A Broker started on port {self.config.port}")
        except Exception as e:
            self.status = BrokerStatus.ERROR
            logger.error(f"Failed to start broker: {e}")
            raise

    async def _start_server(self) -> None:
        """Start the actual server (implementation depends on framework)."""
        # This would start an actual HTTP/gRPC server
        # For testing, we just mark as started
        pass

    async def shutdown(self) -> None:
        """Shutdown the broker gracefully."""
        self.status = BrokerStatus.STOPPING

        try:
            # Stop enhanced components
            await self.health_checker.stop()

            if self._server:
                self._server.close()
                await self._server.wait_closed()
            self.status = BrokerStatus.STOPPED
            logger.info("A2A Broker stopped")
        except Exception as e:
            self.status = BrokerStatus.ERROR
            logger.error(f"Error during shutdown: {e}")

    def health_check(self) -> bool:
        """Check broker health."""
        return self.status == BrokerStatus.RUNNING

    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Handle agent request with enhanced routing."""
        start_time = time.time()

        try:
            # Validate request
            if not await self.policy.validate_request(request):
                return AgentResponse(success=False, error="Request blocked by policy")

            # Check rate limit
            if not await self.limiter.check_rate_limit(request.agent_id):
                return AgentResponse(success=False, error="Rate limit exceeded")

            # Record request for rate limiting
            await self.limiter.record_request(request.agent_id)

            # Route request to appropriate agent
            target_agent_id = self.router.route_message(request.capability)
            if not target_agent_id:
                # Fallback to original agent if no route found
                target_agent_id = request.agent_id

            # Get agent endpoint
            if not self.registry.is_registered(target_agent_id):
                return AgentResponse(success=False, error=f"Agent {target_agent_id} not registered")

            agent_data = self.registry._agents[target_agent_id]
            endpoint = agent_data["endpoint"]

            # Check agent health
            if target_agent_id in self.health_checker.unhealthy_agents:
                return AgentResponse(success=False, error=f"Agent {target_agent_id} is unhealthy")

            # Call external agent
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{endpoint}/{request.capability}",
                    json=request.payload,
                    timeout=aiohttp.ClientTimeout(
                        total=request.timeout or self.config.timeout_seconds
                    ),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response = AgentResponse(
                            success=True,
                            data=data,
                            duration_ms=int((time.time() - start_time) * 1000),
                        )
                    else:
                        response = AgentResponse(
                            success=False,
                            error=f"Agent returned status {resp.status}",
                            duration_ms=int((time.time() - start_time) * 1000),
                        )

            # Update load balancer metrics
            duration_ms = int((time.time() - start_time) * 1000)
            self.router.load_balancer.update_agent_metrics(
                target_agent_id,
                {
                    "avg_response_time": duration_ms,
                    "connections": 1,  # Simplified metric
                    "last_request": time.time(),
                },
            )

        except asyncio.TimeoutError:
            response = AgentResponse(
                success=False,
                error="Request timeout",
                duration_ms=int((time.time() - start_time) * 1000),
            )
        except Exception as e:
            response = AgentResponse(
                success=False, error=str(e), duration_ms=int((time.time() - start_time) * 1000)
            )

        # Audit log
        if self.config.enable_audit:
            await self.audit.log_request(request, response)

        return response

    def add_route(self, capability: str, agent_id: str) -> None:
        """Add routing rule for capability."""
        self.router.add_route(capability, agent_id)

    def discover_agents(self, tags: Optional[list[str]] = None) -> list[dict[str, Any]]:
        """Discover agents by tags."""
        return self.discovery_service.discover_services(tags=tags)

    def register_agent_service(
        self,
        agent_id: str,
        agent_name: str,
        endpoint: str,
        port: int,
        capabilities: list[AgentCapability],
        tags: Optional[list[str]] = None,
    ) -> str:
        """Register agent with both registry and discovery service."""
        # Register with main registry
        registration_id = self.registry.register(agent_id, endpoint, capabilities)

        # Register with discovery service
        self.discovery_service.register_service(
            service_id=agent_id,
            service_name=agent_name,
            endpoint=endpoint,
            port=port,
            tags=tags or [],
            metadata={"capabilities": [cap.name for cap in capabilities], "agent_type": "external"},
        )

        # Add routes for capabilities
        for capability in capabilities:
            self.router.add_route(capability.name, agent_id)

        return registration_id
