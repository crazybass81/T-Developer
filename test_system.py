#!/usr/bin/env python3
"""Test script for the integrated system."""

import asyncio
import json
import sys

# Add backend to path
sys.path.append("/home/ec2-user/T-Developer/backend")

from packages.agents.base import AgentInput, AgentStatus
from packages.agents.code_analysis import CodeAnalysisAgent, CodeAnalysisConfig
from packages.agents.research import ResearchAgent, ResearchConfig

from backend.core.shared_context import get_context_store


async def test_code_analysis():
    """Test CodeAnalysisAgent."""
    print("\n=== Testing CodeAnalysisAgent ===")

    try:
        # Create agent
        config = CodeAnalysisConfig(max_files_to_scan=10, focus_patterns=["*.py"])
        agent = CodeAnalysisAgent(config=config)

        # Create input
        input_data = AgentInput(
            task_id="test-001",
            intent="analyze",
            payload={
                "target_path": "/home/ec2-user/T-Developer/backend/packages/agents",
                "focus_areas": ["code quality", "patterns"],
            },
        )

        # Execute
        print("Running code analysis...")
        result = await agent.execute(input_data)

        # Check result
        if result.status == AgentStatus.OK:
            print("✓ Code analysis successful")
            print(f"  - Files analyzed: {result.metrics.get('files_analyzed', 0)}")
            print(f"  - Improvements found: {result.metrics.get('improvements_found', 0)}")
            print(f"  - Evolution ID: {result.metrics.get('evolution_id', 'N/A')}")

            # Check if stored in context
            if result.context and result.context.get("evolution_id"):
                context_store = get_context_store()
                context = await context_store.get_context(result.context["evolution_id"])
                if context:
                    print("✓ Analysis stored in SharedContext")
                else:
                    print("✗ Failed to store in SharedContext")

            return result.context.get("evolution_id") if result.context else None
        else:
            print(f"✗ Code analysis failed: {result.error}")
            return None

    except Exception as e:
        print(f"✗ Error in code analysis: {e}")
        import traceback

        traceback.print_exc()
        return None


async def test_research_agent(evolution_id=None):
    """Test ResearchAgent with orchestration."""
    print("\n=== Testing ResearchAgent (Orchestrator) ===")

    try:
        # Create agent
        config = ResearchConfig(
            max_files_to_scan=10,
            enable_reference_search=True,
            enable_ai_analysis=False,  # Disable AI for testing
        )
        agent = ResearchAgent(config=config)

        # Create input
        payload = {
            "target_path": "/home/ec2-user/T-Developer/backend/packages/agents",
            "focus_areas": ["performance", "security"],
            "problem": "code quality improvements",
            "requirements": ["maintainability", "testability"],
        }

        if evolution_id:
            payload["evolution_id"] = evolution_id

        input_data = AgentInput(task_id="test-002", intent="research", payload=payload)

        print("Running research orchestration...")
        result = await agent.execute(input_data)

        if result.status == AgentStatus.OK:
            print("✓ Research orchestration successful")
            print(f"  - Files analyzed: {result.metrics.get('files_analyzed', 0)}")
            print(f"  - Improvements: {result.metrics.get('improvements_found', 0)}")
            print(f"  - External solutions: {result.metrics.get('external_solutions', 0)}")
            print(f"  - Recommendations: {result.metrics.get('recommendations', 0)}")

            # Check artifacts
            if result.artifacts:
                for artifact in result.artifacts:
                    if hasattr(artifact, "kind") and artifact.kind == "report":
                        print("✓ Comprehensive report generated")
                        # Save report for inspection
                        with open("/home/ec2-user/T-Developer/test_report.json", "w") as f:
                            json.dump(artifact.content, f, indent=2)
                        print("  Report saved to test_report.json")
                        break
        else:
            print(f"✗ Research orchestration failed: {result.error}")

    except Exception as e:
        print(f"✗ Error in research: {e}")
        import traceback

        traceback.print_exc()


async def test_shared_context():
    """Test SharedContextStore functionality."""
    print("\n=== Testing SharedContextStore ===")

    try:
        context_store = get_context_store()

        # Get all contexts
        contexts = await context_store.get_all_contexts()
        print(f"Found {len(contexts)} evolution contexts")

        if contexts:
            # Check latest context
            latest = contexts[-1]
            print("Latest context:")
            print(f"  - Evolution ID: {latest['evolution_id']}")
            print(f"  - Status: {latest['status']}")
            print(f"  - Phase: {latest['current_phase']}")
            print(f"  - Target: {latest['target_path']}")
            print(f"  - Has errors: {latest['has_errors']}")

            # Get full context
            full_context = await context_store.get_context(latest["evolution_id"])
            if full_context:
                print("✓ Context retrieved successfully")

                # Check sections
                sections = []
                if full_context.original_analysis:
                    sections.append("original_analysis")
                if full_context.external_research:
                    sections.append("external_research")
                if full_context.current_state:
                    sections.append("current_state")

                print(f"  Populated sections: {', '.join(sections)}")
            else:
                print("✗ Failed to retrieve full context")
        else:
            print("No contexts found in store")

    except Exception as e:
        print(f"✗ Error checking SharedContext: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Run all tests."""
    print("=" * 60)
    print("T-Developer System Integration Test")
    print("=" * 60)

    # Test individual components
    evolution_id = await test_code_analysis()

    # Test orchestration
    await test_research_agent(evolution_id)

    # Check SharedContext
    await test_shared_context()

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
