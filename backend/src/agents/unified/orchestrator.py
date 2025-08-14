"""Unified Orchestrator Module"""

from typing import Any, Dict, List


class UnifiedOrchestrator:
    """Orchestrator for unified agents"""

    def __init__(self):
        self.agents = {}

    def register_agent(self, name: str, agent: Any):
        """Register an agent"""
        self.agents[name] = agent

    async def execute_pipeline(self, input_data: Any) -> Dict[str, Any]:
        """Execute the agent pipeline"""
        results = {}
        for name, agent in self.agents.items():
            result = await agent.execute(input_data)
            results[name] = result
        return results
