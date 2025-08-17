#!/usr/bin/env python3
"""
Verify that each agent properly integrates with SharedContextStore.
"""

import asyncio
import logging
import os
import sys
from typing import Any

# Add backend directory to path for proper imports
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_path)

from packages.agents.code_analysis import CodeAnalysisAgent
from packages.agents.evaluator import EvaluatorAgent
from packages.agents.planner import PlannerAgent
from packages.agents.refactor import RefactorAgent
from packages.agents.research import ResearchAgent
from packages.shared_context import get_context_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentContextVerifier:
    """Verifies agent SharedContextStore integration."""

    def __init__(self):
        self.context_store = get_context_store()
        self.agents = {
            "ResearchAgent": ResearchAgent("research_agent"),
            "CodeAnalysisAgent": CodeAnalysisAgent("code_analysis_agent"),
            "PlannerAgent": PlannerAgent("planner_agent"),
            "RefactorAgent": RefactorAgent("refactor_agent"),
            "EvaluatorAgent": EvaluatorAgent("evaluator_agent"),
        }
        self.results = {}

    async def verify_agent_has_context_store(self, agent_name: str, agent: Any) -> dict[str, Any]:
        """Verify agent has context_store attribute."""
        result = {
            "has_context_store": hasattr(agent, "context_store"),
            "context_store_type": type(getattr(agent, "context_store", None)).__name__,
            "is_shared_instance": getattr(agent, "context_store", None) is self.context_store,
        }
        return result

    async def verify_agent_stores_data(self, agent_name: str, agent: Any) -> dict[str, Any]:
        """Verify agent can store data in context."""
        result = {"stores_data": False, "store_methods": []}

        # Check for store methods in agent code
        import inspect

        source = inspect.getsource(agent.__class__)

        store_patterns = [
            "store_original_analysis",
            "store_external_research",
            "store_improvement_plan",
            "store_implementation_log",
            "store_evaluation_results",
            "context_store.store",
            "self.context_store.",
        ]

        for pattern in store_patterns:
            if pattern in source:
                result["stores_data"] = True
                result["store_methods"].append(pattern)

        return result

    async def verify_agent_reads_data(self, agent_name: str, agent: Any) -> dict[str, Any]:
        """Verify agent can read data from context."""
        result = {"reads_data": False, "read_methods": []}

        # Check for read methods in agent code
        import inspect

        source = inspect.getsource(agent.__class__)

        read_patterns = [
            "get_context",
            "get_comparison_data",
            "context_store.get",
            "self.context_store.get",
        ]

        for pattern in read_patterns:
            if pattern in source:
                result["reads_data"] = True
                result["read_methods"].append(pattern)

        return result

    async def test_context_flow(self) -> dict[str, Any]:
        """Test data flow through context store."""
        test_results = {"success": False, "phases": {}}

        try:
            # Create test context
            evolution_id = await self.context_store.create_context(
                target_path="/tmp/test", focus_areas=["test"]
            )

            # Test Phase 1: Store original analysis
            await self.context_store.store_original_analysis(
                evolution_id=evolution_id,
                files_analyzed=5,
                metrics={"test_coverage": 50},
                issues=[{"type": "missing_docstring", "count": 10}],
                improvements=[{"type": "add_types", "priority": "high"}],
            )
            test_results["phases"]["original_analysis"] = True

            # Test Phase 2: Store research
            await self.context_store.store_external_research(
                evolution_id=evolution_id,
                best_practices=["Use type hints"],
                references=["PEP 484"],
                patterns=[{"name": "factory", "usage": "common"}],
            )
            test_results["phases"]["external_research"] = True

            # Test Phase 3: Store plan
            await self.context_store.store_improvement_plan(
                evolution_id=evolution_id,
                tasks=[{"name": "Add docstrings", "priority": 1}],
                priorities=["high"],
                dependencies={},
            )
            test_results["phases"]["improvement_plan"] = True

            # Test Phase 4: Store implementation log
            await self.context_store.store_implementation_log(
                evolution_id=evolution_id,
                modified_files=["test.py"],
                changes=[{"file": "test.py", "type": "docstring"}],
                rollback_points=[],
            )
            test_results["phases"]["implementation_log"] = True

            # Test Phase 5: Store evaluation
            await self.context_store.store_evaluation_results(
                evolution_id=evolution_id,
                goals_achieved=["Improve documentation"],
                metrics_comparison={"test_coverage": {"before": 50, "after": 75}},
                success_rate=0.8,
            )
            test_results["phases"]["evaluation_results"] = True

            # Verify all data is retrievable
            context = await self.context_store.get_context(evolution_id)
            comparison = await self.context_store.get_comparison_data(evolution_id)

            test_results["success"] = (
                context is not None
                and comparison is not None
                and all(test_results["phases"].values())
            )

        except Exception as e:
            test_results["error"] = str(e)

        return test_results

    async def run_verification(self):
        """Run complete verification suite."""
        logger.info("=" * 60)
        logger.info("🔍 AGENT CONTEXT INTEGRATION VERIFICATION")
        logger.info("=" * 60)
        logger.info("")

        # Verify each agent
        for agent_name, agent in self.agents.items():
            logger.info(f"\n📋 Verifying {agent_name}:")

            # Check context store
            context_check = await self.verify_agent_has_context_store(agent_name, agent)
            status = "✅" if context_check["has_context_store"] else "❌"
            logger.info(f"  {status} Has context_store: {context_check['has_context_store']}")
            logger.info(f"      Type: {context_check['context_store_type']}")
            logger.info(f"      Shared instance: {context_check['is_shared_instance']}")

            # Check store capability
            store_check = await self.verify_agent_stores_data(agent_name, agent)
            status = "✅" if store_check["stores_data"] else "⚠️"
            logger.info(f"  {status} Stores data: {store_check['stores_data']}")
            if store_check["store_methods"]:
                logger.info(f"      Methods: {', '.join(store_check['store_methods'][:3])}")

            # Check read capability
            read_check = await self.verify_agent_reads_data(agent_name, agent)
            status = "✅" if read_check["reads_data"] else "⚠️"
            logger.info(f"  {status} Reads data: {read_check['reads_data']}")
            if read_check["read_methods"]:
                logger.info(f"      Methods: {', '.join(read_check['read_methods'][:3])}")

            self.results[agent_name] = {
                "context": context_check,
                "stores": store_check,
                "reads": read_check,
            }

        # Test context flow
        logger.info("\n📊 Testing Context Store Flow:")
        flow_test = await self.test_context_flow()

        if flow_test["success"]:
            logger.info("  ✅ Context flow test PASSED")
            for phase, success in flow_test["phases"].items():
                status = "✅" if success else "❌"
                logger.info(f"    {status} {phase}")
        else:
            logger.info("  ❌ Context flow test FAILED")
            if "error" in flow_test:
                logger.info(f"    Error: {flow_test['error']}")

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📈 VERIFICATION SUMMARY")
        logger.info("=" * 60)

        total_agents = len(self.agents)
        agents_with_context = sum(
            1 for r in self.results.values() if r["context"]["has_context_store"]
        )
        agents_storing = sum(1 for r in self.results.values() if r["stores"]["stores_data"])
        agents_reading = sum(1 for r in self.results.values() if r["reads"]["reads_data"])

        logger.info(f"  Agents with context_store: {agents_with_context}/{total_agents}")
        logger.info(f"  Agents storing data: {agents_storing}/{total_agents}")
        logger.info(f"  Agents reading data: {agents_reading}/{total_agents}")
        logger.info(f"  Context flow test: {'PASSED' if flow_test['success'] else 'FAILED'}")

        overall_success = agents_with_context == total_agents and flow_test["success"]

        if overall_success:
            logger.info("\n✅ All agents properly integrated with SharedContextStore!")
        else:
            logger.info("\n⚠️  Some agents need SharedContextStore integration improvements")

        return overall_success


async def main():
    verifier = AgentContextVerifier()
    success = await verifier.run_verification()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
