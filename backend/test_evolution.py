#!/usr/bin/env python3
"""Test T-Developer Self-Evolution with Various Goals"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.agents.evolution.orchestrator import EvolutionOrchestrator


async def test_evolution():
    """Run evolution with different goals"""

    orchestrator = EvolutionOrchestrator()

    print("\n" + "=" * 60)
    print("🧬 T-Developer Evolution Test Suite")
    print("=" * 60)

    # First analyze the system
    analysis = await orchestrator.analyze_self()
    print(f"\n📊 Evolution Readiness: {analysis['evolution_readiness']}%")

    if analysis["evolution_readiness"] < 75:
        print("⚠️ System not ready for evolution")
        return

    # Evolution Goal: Remove unnecessary blank lines and optimize code
    print("\n" + "=" * 60)
    print("🎯 Goal: Code Optimization")
    print("=" * 60)

    optimization_goal = {
        "description": "Optimize code by removing unnecessary blank lines and improving structure",
        "constraints": [
            "Preserve all functionality",
            "Keep code readable",
            "Maintain PEP 8 compliance",
        ],
        "success_criteria": {"blank_lines": 100},  # Reduce blank lines
        "max_cycles": 1,
        "use_ai": False,
    }

    result = await orchestrator.evolve(optimization_goal)

    print("\n📊 Optimization Results:")
    print(f"  Success: {result['success']}")
    print(f"  Files Modified: {result['total_improvements']}")

    # Show comparison
    if result.get("comparison"):
        comp = result["comparison"]
        if comp["improvement_summary"] or comp["regression_summary"]:
            print("\n📈 Changes Made:")
            for change in comp["improvement_summary"]:
                print(f"  ✅ {change}")
            for change in comp["regression_summary"]:
                print(f"  ⚠️ {change}")

    # Check if files were actually modified
    if result["total_improvements"] > 0:
        print(f"\n✨ Evolution successful! {result['total_improvements']} files improved.")
    else:
        print("\n💡 No improvements made. The code may already be optimized.")
        print("   Consider trying different improvement goals:")
        print("   - Add more comprehensive error handling")
        print("   - Improve logging and debugging")
        print("   - Add performance optimizations")
        print("   - Enhance test coverage")


if __name__ == "__main__":
    asyncio.run(test_evolution())
