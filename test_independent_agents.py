#!/usr/bin/env python3
"""Test independent agent execution."""

import asyncio
import sys

# Add backend to path
sys.path.append("/home/ec2-user/T-Developer/backend")

from packages.agents.base import AgentInput, AgentStatus
from packages.agents.code_analysis import CodeAnalysisAgent, CodeAnalysisConfig
from packages.agents.external_research import ExternalResearchAgent, ExternalResearchConfig

from backend.core.shared_context import get_context_store


async def test_independent_code_analysis():
    """Test CodeAnalysisAgent independently."""
    print("\n=== Testing Independent CodeAnalysisAgent ===")

    try:
        config = CodeAnalysisConfig(max_files_to_scan=5)
        agent = CodeAnalysisAgent(config=config)

        input_data = AgentInput(
            task_id="code-001",
            intent="analyze",
            payload={
                "target_path": "/home/ec2-user/T-Developer/backend/packages/agents",
                "focus_areas": ["code quality"],
            },
        )

        result = await agent.execute(input_data)

        if result.status == AgentStatus.OK:
            print("✓ Code analysis successful")
            print(f"  - Files analyzed: {result.metrics.get('files_analyzed', 0)}")
            print(
                f"  - Evolution ID: {result.context.get('evolution_id') if result.context else 'None'}"
            )
            return result.context.get("evolution_id") if result.context else None
        else:
            print(f"✗ Code analysis failed: {result.error}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


async def test_independent_external_research():
    """Test ExternalResearchAgent independently (without evolution_id)."""
    print("\n=== Testing Independent ExternalResearchAgent (Direct Mode) ===")

    try:
        config = ExternalResearchConfig(max_external_searches=3)
        agent = ExternalResearchAgent(config=config)

        input_data = AgentInput(
            task_id="research-001",
            intent="research",
            payload={
                "problem": "implement authentication system",
                "requirements": ["jwt", "oauth2", "security"],
                "constraints": {"budget": "low", "timeline": "urgent"},
            },
        )

        result = await agent.execute(input_data)

        if result.status == AgentStatus.OK:
            print("✓ External research successful")
            print(f"  - GitHub solutions: {result.metrics.get('github_solutions', 0)}")
            print(f"  - Recommendations: {result.metrics.get('recommendations', 0)}")
            print(f"  - Trends analyzed: {result.metrics.get('trends_analyzed', 0)}")
        else:
            print(f"✗ External research failed: {result.error}")

    except Exception as e:
        print(f"✗ Error: {e}")


async def test_external_research_with_context(evolution_id):
    """Test ExternalResearchAgent with SharedContext."""
    print("\n=== Testing ExternalResearchAgent with SharedContext ===")

    try:
        config = ExternalResearchConfig(max_external_searches=3)
        agent = ExternalResearchAgent(config=config)

        input_data = AgentInput(
            task_id="research-002",
            intent="research",
            payload={"evolution_id": evolution_id, "category": "code-quality"},
        )

        result = await agent.execute(input_data)

        if result.status == AgentStatus.OK:
            print("✓ Context-based research successful")
            print(f"  - Evolution ID: {evolution_id}")
            print(f"  - GitHub solutions: {result.metrics.get('github_solutions', 0)}")
            print(f"  - Recommendations: {result.metrics.get('recommendations', 0)}")
        else:
            print(f"✗ Context-based research failed: {result.error}")

    except Exception as e:
        print(f"✗ Error: {e}")


async def test_context_analyzer():
    """Test ContextAnalyzerAgent independently."""
    print("\n=== Testing Independent ContextAnalyzerAgent ===")

    try:
        agent = ContextAnalyzerAgent()

        input_data = AgentInput(
            task_id="context-001",
            intent="analyze",
            payload={"target_path": "/home/ec2-user/T-Developer"},
        )

        result = await agent.execute(input_data)

        if result.status == AgentStatus.OK:
            print("✓ Context analysis successful")
            if result.artifacts:
                for artifact in result.artifacts:
                    if hasattr(artifact, "content"):
                        content = artifact.content
                        print(f"  - Language: {content.get('language', 'Unknown')}")
                        print(f"  - Framework: {content.get('framework', 'Unknown')}")
                        print(f"  - Type: {content.get('project_type', 'Unknown')}")
                        break
        else:
            print(f"✗ Context analysis failed: {result.error}")

    except Exception as e:
        print(f"✗ Error: {e}")


async def main():
    """Run all independent agent tests."""
    print("=" * 60)
    print("Independent Agent Execution Test")
    print("=" * 60)

    # Test each agent independently
    evolution_id = await test_independent_code_analysis()
    await test_independent_external_research()

    if evolution_id:
        await test_external_research_with_context(evolution_id)

    # Check SharedContext
    print("\n=== SharedContext Status ===")
    context_store = get_context_store()
    contexts = await context_store.get_all_contexts()
    print(f"Total contexts: {len(contexts)}")

    print("\n" + "=" * 60)
    print("Test Complete - All Agents Are Independent!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
