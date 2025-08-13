"""
AWS Agent Squad Integration
Orchestration framework for managing agent collaboration
"""
import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.frameworks.agno_framework import (
    AgentContext,
    AgentInput,
    AgentResult,
    AgentStatus,
    AgnoAgent,
)

logger = logging.getLogger(__name__)


class SquadRole(Enum):
    """Agent roles in the squad"""

    LEADER = "leader"
    WORKER = "worker"
    VALIDATOR = "validator"
    AGGREGATOR = "aggregator"
    ROUTER = "router"


class RoutingStrategy(Enum):
    """Routing strategies for agent selection"""

    ROUND_ROBIN = "round_robin"
    LOAD_BALANCED = "load_balanced"
    SKILL_BASED = "skill_based"
    PRIORITY_BASED = "priority_based"
    CONDITIONAL = "conditional"


@dataclass
class SquadConfig:
    """Agent Squad configuration"""

    max_agents: int = 10
    enable_auto_scaling: bool = True
    min_agents: int = 1
    routing_strategy: RoutingStrategy = RoutingStrategy.SKILL_BASED
    session_timeout: int = 3600
    enable_consensus: bool = False
    consensus_threshold: float = 0.7
    enable_fallback: bool = True
    max_retries: int = 3


@dataclass
class AgentProfile:
    """Profile for squad agents"""

    agent_id: str
    name: str
    role: SquadRole
    skills: List[str] = field(default_factory=list)
    capacity: int = 10
    current_load: int = 0
    priority: int = 1
    success_rate: float = 1.0
    average_response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SquadSession:
    """Squad execution session"""

    session_id: str
    created_at: datetime
    context: AgentContext
    participating_agents: List[str] = field(default_factory=list)
    results: List[AgentResult] = field(default_factory=list)
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)


class RoutingRule:
    """Rule for conditional routing"""

    def __init__(
        self,
        condition: Callable[[Any], bool],
        target_agents: List[str],
        priority: int = 1,
    ):
        self.condition = condition
        self.target_agents = target_agents
        self.priority = priority

    def evaluate(self, input_data: Any) -> bool:
        """Evaluate if rule applies"""
        try:
            return self.condition(input_data)
        except Exception as e:
            logger.error(f"Error evaluating routing rule: {e}")
            return False


class AgentSquad:
    """AWS Agent Squad orchestrator"""

    def __init__(self, squad_name: str, config: Optional[SquadConfig] = None):
        self.squad_name = squad_name
        self.config = config or SquadConfig()
        self.agents: Dict[str, Tuple[AgnoAgent, AgentProfile]] = {}
        self.sessions: Dict[str, SquadSession] = {}
        self.routing_rules: List[RoutingRule] = []
        self._round_robin_index = 0
        self._metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "completed_sessions": 0,
            "failed_sessions": 0,
            "total_agent_calls": 0,
            "average_session_time": 0.0,
        }

    def add_agent(self, agent: AgnoAgent, profile: AgentProfile) -> None:
        """Add agent to squad"""
        if len(self.agents) >= self.config.max_agents:
            raise ValueError(f"Squad already has maximum agents ({self.config.max_agents})")

        self.agents[profile.agent_id] = (agent, profile)
        logger.info(f"Added agent {profile.name} to squad {self.squad_name}")

    def remove_agent(self, agent_id: str) -> bool:
        """Remove agent from squad"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Removed agent {agent_id} from squad {self.squad_name}")
            return True
        return False

    def add_routing_rule(self, rule: RoutingRule) -> None:
        """Add routing rule"""
        self.routing_rules.append(rule)
        self.routing_rules.sort(key=lambda r: r.priority, reverse=True)

    def _select_agents(
        self, input_data: Any, required_skills: List[str] = None, num_agents: int = 1
    ) -> List[str]:
        """Select agents based on routing strategy"""
        available_agents = []

        # Filter by skills if required
        for agent_id, (agent, profile) in self.agents.items():
            if profile.current_load >= profile.capacity:
                continue

            if required_skills:
                if not all(skill in profile.skills for skill in required_skills):
                    continue

            available_agents.append(agent_id)

        if not available_agents:
            logger.warning("No available agents matching criteria")
            return []

        # Apply routing strategy
        if self.config.routing_strategy == RoutingStrategy.ROUND_ROBIN:
            selected = []
            for _ in range(min(num_agents, len(available_agents))):
                idx = self._round_robin_index % len(available_agents)
                selected.append(available_agents[idx])
                self._round_robin_index += 1
            return selected

        elif self.config.routing_strategy == RoutingStrategy.LOAD_BALANCED:
            # Sort by load and select least loaded
            available_agents.sort(key=lambda aid: self.agents[aid][1].current_load)
            return available_agents[:num_agents]

        elif self.config.routing_strategy == RoutingStrategy.SKILL_BASED:
            # Sort by skill match and success rate
            if required_skills:
                available_agents.sort(
                    key=lambda aid: (
                        -len(set(self.agents[aid][1].skills) & set(required_skills)),
                        -self.agents[aid][1].success_rate,
                    )
                )
            return available_agents[:num_agents]

        elif self.config.routing_strategy == RoutingStrategy.PRIORITY_BASED:
            # Sort by priority and success rate
            available_agents.sort(
                key=lambda aid: (
                    -self.agents[aid][1].priority,
                    -self.agents[aid][1].success_rate,
                )
            )
            return available_agents[:num_agents]

        elif self.config.routing_strategy == RoutingStrategy.CONDITIONAL:
            # Apply routing rules
            for rule in self.routing_rules:
                if rule.evaluate(input_data):
                    matching = [aid for aid in rule.target_agents if aid in available_agents]
                    if matching:
                        return matching[:num_agents]

            # Fallback to first available
            return available_agents[:num_agents]

        return available_agents[:num_agents]

    async def create_session(self, context: Optional[AgentContext] = None) -> str:
        """Create new squad session"""
        session_id = str(uuid.uuid4())

        if context is None:
            context = AgentContext(request_id=str(uuid.uuid4()))

        session = SquadSession(session_id=session_id, created_at=datetime.utcnow(), context=context)

        self.sessions[session_id] = session
        self._metrics["total_sessions"] += 1
        self._metrics["active_sessions"] += 1

        logger.info(f"Created squad session {session_id}")
        return session_id

    async def execute_single(self, session_id: str, agent_id: str, input_data: Any) -> AgentResult:
        """Execute single agent in session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        session = self.sessions[session_id]
        agent, profile = self.agents[agent_id]

        # Update load
        profile.current_load += 1

        try:
            # Prepare input
            agent_input = AgentInput(
                data=input_data,
                context=session.context,
                previous_results=session.results.copy(),
            )

            # Execute agent
            start_time = datetime.utcnow()
            result = await agent.execute(agent_input)
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            # Update profile metrics
            profile.average_response_time = (
                profile.average_response_time * self._metrics["total_agent_calls"] + execution_time
            ) / (self._metrics["total_agent_calls"] + 1)

            if result.status == AgentStatus.COMPLETED:
                profile.success_rate = (
                    profile.success_rate * self._metrics["total_agent_calls"] + 1
                ) / (self._metrics["total_agent_calls"] + 1)
            else:
                profile.success_rate = (
                    profile.success_rate * self._metrics["total_agent_calls"]
                ) / (self._metrics["total_agent_calls"] + 1)

            # Add to session results
            session.results.append(result)
            session.participating_agents.append(agent_id)

            self._metrics["total_agent_calls"] += 1

            return result

        finally:
            # Update load
            profile.current_load -= 1

    async def execute_parallel(
        self, session_id: str, agent_ids: List[str], input_data: Any
    ) -> List[AgentResult]:
        """Execute multiple agents in parallel"""
        tasks = [self.execute_single(session_id, agent_id, input_data) for agent_id in agent_ids]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    AgentResult(
                        agent_name=agent_ids[i],
                        status=AgentStatus.FAILED,
                        error=str(result),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    async def execute_with_consensus(
        self,
        session_id: str,
        input_data: Any,
        required_skills: List[str] = None,
        min_agents: int = 3,
    ) -> AgentResult:
        """Execute with consensus from multiple agents"""
        # Select agents for consensus
        agent_ids = self._select_agents(input_data, required_skills, num_agents=max(min_agents, 3))

        if len(agent_ids) < min_agents:
            return AgentResult(
                agent_name="squad_consensus",
                status=AgentStatus.FAILED,
                error=f"Not enough agents available (required: {min_agents})",
            )

        # Execute agents in parallel
        results = await self.execute_parallel(session_id, agent_ids, input_data)

        # Aggregate results for consensus
        successful_results = [r for r in results if r.status == AgentStatus.COMPLETED]

        if len(successful_results) / len(results) < self.config.consensus_threshold:
            return AgentResult(
                agent_name="squad_consensus",
                status=AgentStatus.FAILED,
                error="Consensus threshold not met",
                metadata={"results": results},
            )

        # Combine results (simple majority or averaging)
        # This is a simplified consensus - real implementation would be more sophisticated
        combined_data = {}
        for result in successful_results:
            if isinstance(result.data, dict):
                for key, value in result.data.items():
                    if key not in combined_data:
                        combined_data[key] = []
                    combined_data[key].append(value)

        # Take most common value or average
        consensus_data = {}
        for key, values in combined_data.items():
            if all(isinstance(v, (int, float)) for v in values):
                # Numeric - take average
                consensus_data[key] = sum(values) / len(values)
            else:
                # Non-numeric - take most common
                from collections import Counter

                counter = Counter(values)
                consensus_data[key] = counter.most_common(1)[0][0]

        return AgentResult(
            agent_name="squad_consensus",
            status=AgentStatus.COMPLETED,
            data=consensus_data,
            confidence=len(successful_results) / len(results),
            metadata={
                "participating_agents": agent_ids,
                "successful_agents": len(successful_results),
                "total_agents": len(results),
            },
        )

    async def execute_with_fallback(
        self,
        session_id: str,
        input_data: Any,
        primary_skills: List[str],
        fallback_skills: List[str] = None,
    ) -> AgentResult:
        """Execute with fallback strategy"""
        # Try primary agents
        primary_agents = self._select_agents(
            input_data, required_skills=primary_skills, num_agents=1
        )

        if primary_agents:
            result = await self.execute_single(session_id, primary_agents[0], input_data)

            if result.status == AgentStatus.COMPLETED:
                return result

        # Fallback to secondary agents
        if self.config.enable_fallback and fallback_skills:
            fallback_agents = self._select_agents(
                input_data, required_skills=fallback_skills, num_agents=1
            )

            if fallback_agents:
                return await self.execute_single(session_id, fallback_agents[0], input_data)

        return AgentResult(
            agent_name="squad_fallback",
            status=AgentStatus.FAILED,
            error="No agents available for primary or fallback execution",
        )

    async def close_session(self, session_id: str) -> bool:
        """Close squad session"""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        session.status = "closed"

        # Update metrics
        self._metrics["active_sessions"] -= 1
        self._metrics["completed_sessions"] += 1

        # Calculate session time
        session_time = (datetime.utcnow() - session.created_at).total_seconds()
        self._metrics["average_session_time"] = (
            self._metrics["average_session_time"] * (self._metrics["completed_sessions"] - 1)
            + session_time
        ) / self._metrics["completed_sessions"]

        logger.info(f"Closed squad session {session_id}")
        return True

    def get_session(self, session_id: str) -> Optional[SquadSession]:
        """Get session details"""
        return self.sessions.get(session_id)

    def get_agent_profiles(self) -> List[AgentProfile]:
        """Get all agent profiles"""
        return [profile for _, profile in self.agents.values()]

    def get_metrics(self) -> Dict[str, Any]:
        """Get squad metrics"""
        agent_metrics = {}
        for agent_id, (agent, profile) in self.agents.items():
            agent_metrics[agent_id] = {
                "profile": {
                    "name": profile.name,
                    "role": profile.role.value,
                    "skills": profile.skills,
                    "current_load": profile.current_load,
                    "capacity": profile.capacity,
                    "success_rate": profile.success_rate,
                    "average_response_time": profile.average_response_time,
                },
                "metrics": agent.get_metrics(),
            }

        return {
            "squad_name": self.squad_name,
            "squad_metrics": self._metrics,
            "agent_metrics": agent_metrics,
            "total_agents": len(self.agents),
            "routing_strategy": self.config.routing_strategy.value,
        }

    def reset_metrics(self) -> None:
        """Reset all metrics"""
        self._metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "completed_sessions": 0,
            "failed_sessions": 0,
            "total_agent_calls": 0,
            "average_session_time": 0.0,
        }

        for agent, _ in self.agents.values():
            agent.reset_metrics()


# Export classes
__all__ = [
    "SquadRole",
    "RoutingStrategy",
    "SquadConfig",
    "AgentProfile",
    "SquadSession",
    "RoutingRule",
    "AgentSquad",
]
