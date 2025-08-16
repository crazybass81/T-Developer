"""A2A agent discovery service for finding and connecting to agents.

Phase 4: A2A External Integration
P4-T2: A2A Protocol Implementation
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from .message_types import (
    A2AMessage,
    AgentInfo,
    CapabilityInfo,
    MessageType,
    create_capability_discovery_message,
)


class DiscoveryMethod(Enum):
    """Agent discovery methods."""

    BROADCAST = "broadcast"
    MULTICAST = "multicast"
    REGISTRY = "registry"
    DNS = "dns"
    STATIC = "static"


class AgentStatus(Enum):
    """Agent availability status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"
    UNREACHABLE = "unreachable"


@dataclass
class DiscoveryConfig:
    """Discovery service configuration.

    Attributes:
        discovery_methods: Enabled discovery methods
        discovery_interval: Discovery interval in seconds
        agent_ttl: Agent TTL in seconds
        max_agents: Maximum tracked agents
        broadcast_address: Broadcast address for discovery
        registry_endpoints: Registry service endpoints
        static_agents: Statically configured agents
    """

    discovery_methods: list[DiscoveryMethod] = field(
        default_factory=lambda: [DiscoveryMethod.BROADCAST, DiscoveryMethod.REGISTRY]
    )
    discovery_interval: int = 60
    agent_ttl: int = 300
    max_agents: int = 1000
    broadcast_address: str = "255.255.255.255"
    registry_endpoints: list[str] = field(default_factory=list)
    static_agents: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DiscoveredAgent:
    """Information about a discovered agent.

    Attributes:
        agent_info: Agent information
        status: Agent status
        discovered_at: Discovery timestamp
        last_seen: Last seen timestamp
        discovery_method: How agent was discovered
        endpoint: Agent endpoint
        response_time: Last response time
        reliability_score: Reliability score (0.0-1.0)
        metadata: Additional metadata
    """

    agent_info: AgentInfo
    status: AgentStatus = AgentStatus.UNKNOWN
    discovered_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    discovery_method: DiscoveryMethod = DiscoveryMethod.BROADCAST
    endpoint: str = ""
    response_time: Optional[float] = None
    reliability_score: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_stale(self, ttl: int) -> bool:
        """Check if agent information is stale."""
        return time.time() - self.last_seen > ttl

    def update_seen(self) -> None:
        """Update last seen timestamp."""
        self.last_seen = time.time()

    def update_reliability(self, success: bool) -> None:
        """Update reliability score based on interaction result."""
        # Simple exponential moving average
        alpha = 0.1
        if success:
            self.reliability_score = (1 - alpha) * self.reliability_score + alpha * 1.0
        else:
            self.reliability_score = (1 - alpha) * self.reliability_score + alpha * 0.0

        # Clamp to valid range
        self.reliability_score = max(0.0, min(1.0, self.reliability_score))


@dataclass
class CapabilityQuery:
    """Query for discovering agents with specific capabilities.

    Attributes:
        capability_names: Required capability names
        tags: Required tags
        min_version: Minimum capability version
        exclude_agents: Agents to exclude from results
        max_results: Maximum number of results
        min_reliability: Minimum reliability score
        prefer_local: Prefer local agents
    """

    capability_names: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    min_version: Optional[str] = None
    exclude_agents: set[str] = field(default_factory=set)
    max_results: int = 10
    min_reliability: float = 0.5
    prefer_local: bool = True


class DiscoveryRegistry:
    """Registry of discovered agents and their capabilities."""

    def __init__(self, config: DiscoveryConfig):
        """Initialize discovery registry.

        Args:
            config: Discovery configuration
        """
        self.config = config
        self.agents: dict[str, DiscoveredAgent] = {}
        self.capability_index: dict[str, set[str]] = defaultdict(set)
        self.tag_index: dict[str, set[str]] = defaultdict(set)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._lock = asyncio.Lock()

    async def register_agent(
        self,
        agent_info: AgentInfo,
        discovery_method: DiscoveryMethod = DiscoveryMethod.REGISTRY,
        endpoint: str = "",
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Register discovered agent.

        Args:
            agent_info: Agent information
            discovery_method: How agent was discovered
            endpoint: Agent endpoint
            metadata: Additional metadata
        """
        async with self._lock:
            agent_id = agent_info.agent_id

            if agent_id in self.agents:
                # Update existing agent
                discovered_agent = self.agents[agent_id]
                discovered_agent.agent_info = agent_info
                discovered_agent.update_seen()
                discovered_agent.status = AgentStatus.ACTIVE
                discovered_agent.endpoint = endpoint or discovered_agent.endpoint
                discovered_agent.metadata.update(metadata or {})
            else:
                # Check agent limit
                if len(self.agents) >= self.config.max_agents:
                    # Remove oldest stale agent
                    await self._cleanup_stale_agents()

                    if len(self.agents) >= self.config.max_agents:
                        self.logger.warning("Agent registry is full, cannot register new agent")
                        return

                # Add new agent
                discovered_agent = DiscoveredAgent(
                    agent_info=agent_info,
                    status=AgentStatus.ACTIVE,
                    discovery_method=discovery_method,
                    endpoint=endpoint,
                    metadata=metadata or {},
                )
                self.agents[agent_id] = discovered_agent

            # Update capability index
            self._update_capability_index(agent_id, agent_info.capabilities)

            self.logger.info(f"Registered agent: {agent_id} via {discovery_method.value}")

    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister agent.

        Args:
            agent_id: Agent identifier

        Returns:
            True if agent was unregistered
        """
        async with self._lock:
            if agent_id not in self.agents:
                return False

            # Remove from indexes
            self._remove_from_indexes(agent_id)

            # Remove agent
            del self.agents[agent_id]

            self.logger.info(f"Unregistered agent: {agent_id}")
            return True

    async def update_agent_status(
        self, agent_id: str, status: AgentStatus, response_time: Optional[float] = None
    ) -> None:
        """Update agent status.

        Args:
            agent_id: Agent identifier
            status: New status
            response_time: Response time measurement
        """
        async with self._lock:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                agent.status = status
                agent.update_seen()

                if response_time is not None:
                    agent.response_time = response_time

                # Update reliability based on status
                agent.update_reliability(status == AgentStatus.ACTIVE)

    async def find_agents(self, query: CapabilityQuery) -> list[DiscoveredAgent]:
        """Find agents matching capability query.

        Args:
            query: Capability query

        Returns:
            List of matching agents
        """
        async with self._lock:
            matching_agents = []

            for agent_id, agent in self.agents.items():
                # Skip excluded agents
                if agent_id in query.exclude_agents:
                    continue

                # Check reliability
                if agent.reliability_score < query.min_reliability:
                    continue

                # Check status (prefer active agents)
                if agent.status != AgentStatus.ACTIVE:
                    continue

                # Check capabilities
                if query.capability_names:
                    if not self._agent_has_capabilities(agent, query.capability_names):
                        continue

                # Check tags
                if query.tags:
                    if not self._agent_has_tags(agent, query.tags):
                        continue

                # Check version
                if query.min_version:
                    if not self._agent_meets_version(agent, query.min_version):
                        continue

                matching_agents.append(agent)

            # Sort by preference
            matching_agents.sort(key=lambda a: self._calculate_preference_score(a, query))

            # Limit results
            return matching_agents[: query.max_results]

    async def get_agent(self, agent_id: str) -> Optional[DiscoveredAgent]:
        """Get agent by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            Discovered agent or None
        """
        async with self._lock:
            return self.agents.get(agent_id)

    async def get_all_agents(self) -> list[DiscoveredAgent]:
        """Get all registered agents."""
        async with self._lock:
            return list(self.agents.values())

    async def get_capabilities(self) -> dict[str, list[str]]:
        """Get all available capabilities and the agents that provide them."""
        async with self._lock:
            return {
                capability: list(agent_ids)
                for capability, agent_ids in self.capability_index.items()
            }

    async def cleanup_stale_agents(self) -> int:
        """Clean up stale agents.

        Returns:
            Number of agents removed
        """
        async with self._lock:
            return await self._cleanup_stale_agents()

    async def _cleanup_stale_agents(self) -> int:
        """Internal cleanup method."""
        stale_agents = []

        for agent_id, agent in self.agents.items():
            if agent.is_stale(self.config.agent_ttl):
                stale_agents.append(agent_id)

        for agent_id in stale_agents:
            self._remove_from_indexes(agent_id)
            del self.agents[agent_id]

        if stale_agents:
            self.logger.info(f"Cleaned up {len(stale_agents)} stale agents")

        return len(stale_agents)

    def _update_capability_index(self, agent_id: str, capabilities: list[CapabilityInfo]) -> None:
        """Update capability index for agent."""
        # Remove old entries
        self._remove_from_indexes(agent_id)

        # Add new entries
        for capability in capabilities:
            self.capability_index[capability.name].add(agent_id)

            for tag in capability.tags:
                self.tag_index[tag].add(agent_id)

    def _remove_from_indexes(self, agent_id: str) -> None:
        """Remove agent from all indexes."""
        # Remove from capability index
        for agent_ids in self.capability_index.values():
            agent_ids.discard(agent_id)

        # Remove from tag index
        for agent_ids in self.tag_index.values():
            agent_ids.discard(agent_id)

    def _agent_has_capabilities(self, agent: DiscoveredAgent, capability_names: list[str]) -> bool:
        """Check if agent has required capabilities."""
        agent_capabilities = {cap.name for cap in agent.agent_info.capabilities}
        return all(cap in agent_capabilities for cap in capability_names)

    def _agent_has_tags(self, agent: DiscoveredAgent, tags: list[str]) -> bool:
        """Check if agent has required tags."""
        agent_tags = set()
        for cap in agent.agent_info.capabilities:
            agent_tags.update(cap.tags)

        return any(tag in agent_tags for tag in tags)

    def _agent_meets_version(self, agent: DiscoveredAgent, min_version: str) -> bool:
        """Check if agent meets version requirement."""
        # Simplified version comparison
        try:
            agent_version = agent.agent_info.version
            return agent_version >= min_version
        except:
            return False

    def _calculate_preference_score(self, agent: DiscoveredAgent, query: CapabilityQuery) -> float:
        """Calculate preference score for ranking agents."""
        score = 0.0

        # Reliability score (higher is better)
        score += agent.reliability_score * 100

        # Response time (lower is better)
        if agent.response_time is not None:
            score -= agent.response_time * 10

        # Prefer local agents if requested
        if query.prefer_local and agent.discovery_method == DiscoveryMethod.REGISTRY:
            score += 50

        # Status bonus
        if agent.status == AgentStatus.ACTIVE:
            score += 20

        return -score  # Negative for descending sort


class AgentDiscoveryService:
    """Service for discovering and tracking A2A agents."""

    def __init__(self, local_agent: AgentInfo, config: Optional[DiscoveryConfig] = None):
        """Initialize discovery service.

        Args:
            local_agent: Local agent information
            config: Discovery configuration
        """
        self.local_agent = local_agent
        self.config = config or DiscoveryConfig()
        self.registry = DiscoveryRegistry(self.config)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Discovery state
        self.running = False
        self.discovery_task: Optional[asyncio.Task] = None

        # Callbacks
        self.on_agent_discovered: Optional[Callable[[DiscoveredAgent], None]] = None
        self.on_agent_lost: Optional[Callable[[str], None]] = None

        # Transport function for sending discovery messages
        self.transport: Optional[Callable[[A2AMessage], None]] = None

    async def start(self, transport: Callable[[A2AMessage], None]) -> None:
        """Start discovery service.

        Args:
            transport: Transport function for sending messages
        """
        if self.running:
            return

        self.transport = transport
        self.running = True

        # Register static agents
        await self._register_static_agents()

        # Start discovery task
        self.discovery_task = asyncio.create_task(self._discovery_loop())

        self.logger.info("Agent discovery service started")

    async def stop(self) -> None:
        """Stop discovery service."""
        if not self.running:
            return

        self.running = False

        if self.discovery_task:
            self.discovery_task.cancel()
            try:
                await self.discovery_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Agent discovery service stopped")

    async def discover_agents(
        self, query: Optional[CapabilityQuery] = None, force_discovery: bool = False
    ) -> list[DiscoveredAgent]:
        """Discover agents matching query.

        Args:
            query: Capability query
            force_discovery: Force new discovery instead of using cache

        Returns:
            List of discovered agents
        """
        if force_discovery:
            await self._perform_discovery(query)

        if query:
            return await self.registry.find_agents(query)
        else:
            return await self.registry.get_all_agents()

    async def register_discovered_agent(
        self,
        agent_info: AgentInfo,
        discovery_method: DiscoveryMethod = DiscoveryMethod.REGISTRY,
        endpoint: str = "",
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Register a discovered agent.

        Args:
            agent_info: Agent information
            discovery_method: Discovery method used
            endpoint: Agent endpoint
            metadata: Additional metadata
        """
        await self.registry.register_agent(
            agent_info=agent_info,
            discovery_method=discovery_method,
            endpoint=endpoint,
            metadata=metadata,
        )

        # Notify discovery callback
        if self.on_agent_discovered:
            discovered_agent = await self.registry.get_agent(agent_info.agent_id)
            if discovered_agent:
                await self._safe_callback(self.on_agent_discovered, discovered_agent)

    async def handle_discovery_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Handle incoming discovery message.

        Args:
            message: Discovery message

        Returns:
            Response message if applicable
        """
        if message.header.message_type == MessageType.CAPABILITY_DISCOVERY:
            return await self._handle_capability_discovery(message)
        elif message.header.message_type == MessageType.REGISTRATION:
            return await self._handle_agent_registration(message)
        elif message.header.message_type == MessageType.HEARTBEAT:
            await self._handle_heartbeat(message)
            return None

        return None

    async def update_agent_status(
        self, agent_id: str, status: AgentStatus, response_time: Optional[float] = None
    ) -> None:
        """Update agent status.

        Args:
            agent_id: Agent identifier
            status: New status
            response_time: Response time measurement
        """
        await self.registry.update_agent_status(agent_id, status, response_time)

    async def _discovery_loop(self) -> None:
        """Background discovery loop."""
        while self.running:
            try:
                # Perform discovery
                await self._perform_discovery()

                # Clean up stale agents
                removed_count = await self.registry.cleanup_stale_agents()
                if removed_count > 0 and self.on_agent_lost:
                    # Note: This is simplified - in practice you'd track which specific agents were removed
                    pass

                await asyncio.sleep(self.config.discovery_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Discovery loop error: {e}")
                await asyncio.sleep(self.config.discovery_interval)

    async def _perform_discovery(self, query: Optional[CapabilityQuery] = None) -> None:
        """Perform agent discovery."""
        if not self.transport:
            return

        for method in self.config.discovery_methods:
            try:
                if method == DiscoveryMethod.BROADCAST:
                    await self._broadcast_discovery(query)
                elif method == DiscoveryMethod.REGISTRY:
                    await self._registry_discovery(query)
                # Add other discovery methods as needed

            except Exception as e:
                self.logger.error(f"Discovery error for {method.value}: {e}")

    async def _broadcast_discovery(self, query: Optional[CapabilityQuery] = None) -> None:
        """Perform broadcast discovery."""
        if not self.transport:
            return

        # Create discovery message
        query_tags = query.tags if query else []
        query_capabilities = query.capability_names if query else []

        discovery_msg = create_capability_discovery_message(
            sender_id=self.local_agent.agent_id,
            query_tags=query_tags,
            query_capabilities=query_capabilities,
        )

        # Broadcast message
        await self.transport(discovery_msg)

        self.logger.debug("Sent broadcast discovery message")

    async def _registry_discovery(self, query: Optional[CapabilityQuery] = None) -> None:
        """Perform registry-based discovery."""
        # This would query external registry services
        # Implementation depends on specific registry protocol
        pass

    async def _register_static_agents(self) -> None:
        """Register statically configured agents."""
        for agent_config in self.config.static_agents:
            try:
                agent_info = AgentInfo.from_dict(agent_config)
                await self.registry.register_agent(
                    agent_info=agent_info,
                    discovery_method=DiscoveryMethod.STATIC,
                    endpoint=agent_config.get("endpoint", ""),
                )
            except Exception as e:
                self.logger.error(f"Error registering static agent: {e}")

    async def _handle_capability_discovery(self, message: A2AMessage) -> A2AMessage:
        """Handle capability discovery request."""
        query_tags = message.payload.data.get("query_tags", [])
        query_capabilities = message.payload.data.get("query_capabilities", [])

        # Check if we match the query
        matches = True

        if query_capabilities:
            our_capabilities = {cap.name for cap in self.local_agent.capabilities}
            if not any(cap in our_capabilities for cap in query_capabilities):
                matches = False

        if query_tags:
            our_tags = set()
            for cap in self.local_agent.capabilities:
                our_tags.update(cap.tags)
            if not any(tag in our_tags for tag in query_tags):
                matches = False

        if matches:
            # Return our agent info
            return message.create_response(
                status="success",
                data={
                    "agent_info": self.local_agent.to_dict(),
                    "matching_capabilities": [
                        cap.to_dict() for cap in self.local_agent.capabilities
                    ],
                },
            )
        else:
            # Don't respond if we don't match
            return message.create_response(status="no_match", data={})

    async def _handle_agent_registration(self, message: A2AMessage) -> A2AMessage:
        """Handle agent registration message."""
        try:
            agent_info = AgentInfo.from_dict(message.payload.data)

            await self.registry.register_agent(
                agent_info=agent_info,
                discovery_method=DiscoveryMethod.REGISTRY,
                endpoint=message.payload.metadata.get("endpoint", ""),
            )

            return message.create_response(status="success", data={"registered": True})

        except Exception as e:
            return message.create_response(status="error", error=str(e))

    async def _handle_heartbeat(self, message: A2AMessage) -> None:
        """Handle heartbeat message."""
        agent_id = message.header.sender_id
        status_str = message.payload.data.get("status", "unknown")

        try:
            status = (
                AgentStatus(status_str)
                if status_str in [s.value for s in AgentStatus]
                else AgentStatus.UNKNOWN
            )
            await self.registry.update_agent_status(agent_id, status)
        except Exception as e:
            self.logger.error(f"Error handling heartbeat from {agent_id}: {e}")

    async def _safe_callback(self, callback: Callable, *args) -> None:
        """Safely call callback function."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            self.logger.error(f"Discovery callback error: {e}")

    def get_agent_count(self) -> int:
        """Get number of discovered agents."""
        return len(self.registry.agents)

    async def get_capability_summary(self) -> dict[str, int]:
        """Get summary of available capabilities."""
        capabilities = await self.registry.get_capabilities()
        return {capability: len(agent_ids) for capability, agent_ids in capabilities.items()}
