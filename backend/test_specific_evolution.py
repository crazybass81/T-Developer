#!/usr/bin/env python3
"""Test Evolution on Specific Target File"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.agents.evolution.evaluator_agent import EvaluatorAgent
from src.agents.evolution.refactor_agent import RefactorAgent


async def test_single_file_evolution():
    """Test evolution on a single file with missing docstrings"""

    print("\n" + "=" * 60)
    print("🧬 Single File Evolution Test")
    print("=" * 60)

    target_file = "/home/ec2-user/T-DeveloperMVP/backend/src/agents/test_evolution_target.py"

    # 1. Evaluate before
    print("\n📊 Evaluating file BEFORE improvements...")
    evaluator = EvaluatorAgent()

    before_eval = await evaluator.execute(
        {
            "before": target_file,
            "after": target_file,
            "criteria": ["documentation", "quality"],
            "target_metrics": {"docstring_coverage": 80},
        }
    )

    print(
        f"  Docstring Coverage: {before_eval['metrics']['after'].get('docstring_coverage', 0):.1f}%"
    )
    print(f"  Functions: {before_eval['metrics']['after'].get('function_count', 0)}")
    print(f"  Classes: {before_eval['metrics']['after'].get('class_count', 0)}")

    # 2. Apply improvements
    print("\n🔧 Applying improvements...")
    refactor = RefactorAgent()

    improve_result = await refactor.execute(
        {
            "target": target_file,
            "improvement_type": ["docstring", "type_hints"],
            "use_ai": False,
            "auto_commit": False,
        }
    )

    if improve_result.get("improvements"):
        print(f"✅ Improvements applied:")
        for imp in improve_result["improvements"]:
            if "error" not in imp:
                print(f"  - {imp.get('description', 'Unknown improvement')}")

    # 3. Evaluate after
    print("\n📊 Evaluating file AFTER improvements...")
    after_eval = await evaluator.execute(
        {
            "before": target_file,
            "after": target_file,
            "criteria": ["documentation", "quality"],
            "target_metrics": {"docstring_coverage": 80},
        }
    )

    print(
        f"  Docstring Coverage: {after_eval['metrics']['after'].get('docstring_coverage', 0):.1f}%"
    )
    print(f"  Quality Score: {after_eval.get('score', 0)}/100")

    # 4. Show improvement
    before_coverage = before_eval["metrics"]["after"].get("docstring_coverage", 0)
    after_coverage = after_eval["metrics"]["after"].get("docstring_coverage", 0)

    if after_coverage > before_coverage:
        print(
            f"\n✨ SUCCESS! Docstring coverage improved from {before_coverage:.1f}% to {after_coverage:.1f}%"
        )
        print(f"   Improvement: +{after_coverage - before_coverage:.1f}%")
    else:
        print(f"\n⚠️ No improvement in docstring coverage")

    # Show the actual file content
    print("\n📄 File content preview (first 30 lines):")
    with open(target_file, "r") as f:
        lines = f.readlines()[:30]
        for i, line in enumerate(lines, 1):
            print(f"{i:3}: {line}", end="")


if __name__ == "__main__":
    asyncio.run(test_single_file_evolution())
