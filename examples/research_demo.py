#!/usr/bin/env python3
"""Demonstration of Enhanced Research Agent with Reference Library."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.agents.base import AgentInput
from packages.agents.research import ResearchAgent, ResearchConfig


async def demo_codebase_analysis():
    """Demo: Analyze current codebase for improvements."""
    print("\n" + "=" * 60)
    print("DEMO 1: Codebase Analysis")
    print("=" * 60)

    config = ResearchConfig(
        max_files_to_scan=20,
        enable_ai_analysis=False,  # No AI for demo
        enable_reference_search=False,  # Focus on code analysis
    )

    agent = ResearchAgent("research-demo", config)

    input_data = AgentInput(
        intent="research",
        task_id="demo-001",
        payload={"target_path": "./packages/agents", "focus": ["improvements", "patterns"]},
    )

    output = await agent.execute(input_data)

    if output.artifacts:
        report = output.artifacts[0].content
        print("\n📊 Analysis Summary:")
        print(f"  Files analyzed: {report['summary']['files_analyzed']}")
        print(f"  Improvements found: {report['summary']['improvements_found']}")
        print(f"  Patterns detected: {report['summary']['patterns_detected']}")
        print(f"  Code smells: {report['summary']['code_smells']}")

        if report["codebase_analysis"]["improvements"]:
            print("\n🔧 Top Improvements:")
            for imp in report["codebase_analysis"]["improvements"][:3]:
                print(f"  - {imp.get('type', 'unknown')}: {imp.get('suggestion', '')}")


async def demo_reference_search():
    """Demo: Search for technology solutions."""
    print("\n" + "=" * 60)
    print("DEMO 2: External Reference Search")
    print("=" * 60)

    config = ResearchConfig(
        enable_ai_analysis=False, enable_reference_search=True, save_to_library=True
    )

    agent = ResearchAgent("research-demo", config)

    # Example: Search for authentication solution
    input_data = AgentInput(
        intent="reference",
        task_id="demo-002",
        payload={
            "problem": "user authentication system with OAuth support",
            "requirements": ["oauth", "jwt", "social_login"],
            "constraints": {"budget": "medium", "timeline": "urgent", "korean_market": True},
            "category": "authentication",
        },
    )

    print("\n🔍 Searching for: Authentication solutions")
    print(f"  Requirements: {input_data.payload['requirements']}")
    print(f"  Constraints: {input_data.payload['constraints']}")

    output = await agent.execute(input_data)

    if output.artifacts:
        report = output.artifacts[0].content

        if report.get("recommendations") and report["recommendations"].get("recommended"):
            rec = report["recommendations"]["recommended"]
            print(f"\n✅ Recommended Solution: {rec['solution']}")
            print(f"  Type: {rec.get('type', 'unknown')}")
            print("  Reasoning:")
            for reason in rec.get("reasoning", []):
                print(f"    - {reason}")

            if rec.get("pros"):
                print("  Pros:")
                for pro in rec["pros"][:3]:
                    print(f"    + {pro}")

            if rec.get("cons"):
                print("  Cons:")
                for con in rec["cons"][:2]:
                    print(f"    - {con}")

        # Show external references if found
        ext_refs = report.get("external_references", {})
        if ext_refs:
            github = ext_refs.get("external_references", {}).get("github", [])
            if github:
                print("\n📚 Related GitHub Projects:")
                for repo in github[:3]:
                    print(f"  - {repo.get('name', 'unknown')} ⭐ {repo.get('stars', 0)}")


async def demo_combined_research():
    """Demo: Combined codebase analysis and reference search."""
    print("\n" + "=" * 60)
    print("DEMO 3: Combined Research (Code + References)")
    print("=" * 60)

    config = ResearchConfig(
        max_files_to_scan=10,
        enable_ai_analysis=False,
        enable_reference_search=True,
        save_to_library=True,
    )

    agent = ResearchAgent("research-demo", config)

    # Analyze current code and find better solutions
    input_data = AgentInput(
        intent="research",
        task_id="demo-003",
        payload={
            "target_path": "./packages",
            "problem": "improve testing framework",
            "requirements": ["async_support", "coverage", "mocking"],
            "constraints": {"budget": "low", "timeline": "moderate"},
            "category": "testing",
        },
    )

    print("\n🔬 Analyzing codebase and searching for testing improvements...")

    output = await agent.execute(input_data)

    if output.artifacts:
        report = output.artifacts[0].content

        # Show code analysis
        print("\n📊 Current Codebase:")
        print(f"  Files analyzed: {report['summary']['files_analyzed']}")
        print(f"  Code smells: {report['summary']['code_smells']}")

        # Show external solutions
        if report.get("external_references"):
            ext_count = report["summary"].get("external_references_found", 0)
            print(f"\n🌐 External Solutions Found: {ext_count}")

            trends = report["external_references"].get("trends", [])
            if trends:
                print("\n📈 Technology Trends:")
                for trend in trends[:2]:
                    print(f"  - {trend['name']}: {trend['status']} ({trend['momentum']} momentum)")


async def main():
    """Run all demos."""
    print("\n🚀 Enhanced Research Agent Demo")
    print("================================")

    # Demo 1: Codebase Analysis
    await demo_codebase_analysis()

    # Demo 2: External Reference Search
    # Note: This will make real API calls to GitHub/npm
    # Comment out if you don't want external calls
    # await demo_reference_search()

    # Demo 3: Combined Research
    await demo_combined_research()

    print("\n✨ Demo completed!")
    print("\n📁 Reference library saved to: ./references/")

    # Show library structure
    lib_path = Path("references")
    if lib_path.exists():
        print("\n📚 Library Structure:")
        for category in ["solutions", "patterns", "trends"]:
            cat_path = lib_path / category
            if cat_path.exists():
                files = list(cat_path.rglob("*.yaml"))
                if files:
                    print(f"  {category}/: {len(files)} files")


if __name__ == "__main__":
    asyncio.run(main())
