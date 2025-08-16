#!/usr/bin/env python3
"""Demonstration of Planner Agent creating execution plans."""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.agents.base import AgentInput
from packages.agents.planner import PlannerAgent, PlannerConfig


async def demo_simple_plan():
    """Demo: Create a simple execution plan."""
    print("\n" + "=" * 60)
    print("DEMO 1: Simple Plan - Add Logging")
    print("=" * 60)

    config = PlannerConfig(max_hours_per_task=4.0, enable_ai_planning=False)  # No AI for demo

    agent = PlannerAgent("planner-demo", config)

    # Simulate research data
    research_data = {
        "improvements": [
            {
                "type": "logging",
                "location": "auth.py",
                "priority": "high",
                "suggestion": "Add structured logging to authentication module",
            },
            {
                "type": "logging",
                "location": "api.py",
                "priority": "medium",
                "suggestion": "Add request/response logging",
            },
            {
                "type": "logging",
                "location": "database.py",
                "priority": "low",
                "suggestion": "Add query logging",
            },
        ],
        "summary": {"files_analyzed": 15, "improvements_found": 3},
    }

    input_data = AgentInput(
        intent="plan",
        task_id="demo-001",
        payload={
            "goal": "Add comprehensive logging to the application",
            "research_data": research_data,
            "constraints": {
                "max_hours": 10,
                "deadline": (datetime.now() + timedelta(days=3)).isoformat(),
            },
        },
    )

    output = await agent.execute(input_data)

    if output.artifacts:
        plan = output.artifacts[0].content

        print(f"\n📋 Plan Created: {plan['goal']}")
        print(f"  Total Tasks: {len(plan['tasks'])}")
        print(f"  Total Hours: {plan['total_estimated_hours']}")
        print(f"  Valid Plan: {plan['is_valid']}")

        print("\n📝 Tasks:")
        for task in plan["tasks"]:
            deps = (
                f" (depends on: {', '.join(task['dependencies'])})" if task["dependencies"] else ""
            )
            print(f"  [{task['priority']}] {task['name']} - {task['estimated_hours']}h{deps}")

        if plan.get("critical_path"):
            print(f"\n⚡ Critical Path: {' → '.join(plan['critical_path'])}")


async def demo_complex_migration():
    """Demo: Create a complex migration plan."""
    print("\n" + "=" * 60)
    print("DEMO 2: Complex Migration Plan")
    print("=" * 60)

    config = PlannerConfig(max_hours_per_task=4.0, buffer_percentage=20)

    agent = PlannerAgent("planner-demo", config)

    # Simulate migration research data
    research_data = {
        "improvements": [],
        "external_references": {
            "recommendations": {
                "migration_steps": [
                    "Setup new framework alongside existing",
                    "Migrate middleware layer",
                    "Convert API routes",
                    "Migrate database connections",
                    "Update tests",
                    "Performance testing",
                    "Gradual traffic migration",
                    "Deprecate old framework",
                ]
            }
        },
        "summary": {"complexity": "high", "risk": "medium"},
    }

    input_data = AgentInput(
        intent="plan",
        task_id="demo-002",
        payload={
            "goal": "Migrate from Express to Fastify framework",
            "research_data": research_data,
            "constraints": {
                "max_hours": 40,
                "milestones": [
                    {
                        "name": "Framework Setup Complete",
                        "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
                    },
                    {
                        "name": "APIs Migrated",
                        "deadline": (datetime.now() + timedelta(days=14)).isoformat(),
                    },
                    {
                        "name": "Full Migration Complete",
                        "deadline": (datetime.now() + timedelta(days=21)).isoformat(),
                    },
                ],
            },
        },
    )

    output = await agent.execute(input_data)

    if output.artifacts:
        plan = output.artifacts[0].content

        print(f"\n📋 Migration Plan: {plan['goal']}")
        print(f"  Total Tasks: {len(plan['tasks'])}")
        print(f"  Total Hours: {plan['total_estimated_hours']}")
        print(f"  Milestones: {len(plan['milestones'])}")

        print("\n🎯 Milestones:")
        for milestone in plan["milestones"]:
            print(f"  {milestone['name']}")
            print(f"    Deadline: {milestone['deadline'][:10]}")
            print(f"    Tasks: {len(milestone['tasks'])}")
            print(f"    Progress: {milestone['progress']:.1f}%")

        print("\n📝 Task Breakdown:")
        for i, task in enumerate(plan["tasks"], 1):
            deps = f" [deps: {len(task['dependencies'])}]" if task["dependencies"] else ""
            print(f"  {i}. {task['name']} ({task['estimated_hours']}h){deps}")

        # Show Gantt chart data if available
        if len(output.artifacts) > 1:
            gantt = output.artifacts[1].content
            print(f"\n📊 Gantt Chart Data Available: {gantt['title']}")
            print(f"  Tasks in timeline: {len(gantt['tasks'])}")


async def demo_hierarchical_planning():
    """Demo: Hierarchical task decomposition."""
    print("\n" + "=" * 60)
    print("DEMO 3: Hierarchical Planning - 4-Hour Rule")
    print("=" * 60)

    config = PlannerConfig(
        max_hours_per_task=4.0,  # Enforce 4-hour rule
        min_hours_per_task=0.5,
        parallel_tasks_limit=3,
    )

    agent = PlannerAgent("planner-demo", config)

    # Large task that needs decomposition
    research_data = {
        "improvements": [
            {
                "type": "refactor",
                "location": "legacy_module",
                "complexity": "high",
                "effort": "12h",  # Will be split
                "priority": "high",
                "suggestion": "Complete refactoring of legacy authentication system",
            },
            {
                "type": "test",
                "location": "legacy_module",
                "effort": "6h",  # Will be split
                "priority": "high",
                "suggestion": "Add comprehensive test coverage",
            },
        ]
    }

    input_data = AgentInput(
        intent="plan",
        task_id="demo-003",
        payload={
            "goal": "Refactor and test legacy module",
            "research_data": research_data,
            "constraints": {"parallel_execution": True},
        },
    )

    output = await agent.execute(input_data)

    if output.artifacts:
        plan = output.artifacts[0].content

        print(f"\n📋 Hierarchical Plan: {plan['goal']}")
        print(f"  Tasks Created: {len(plan['tasks'])}")
        print(f"  Max Hours/Task: {max(t['estimated_hours'] for t in plan['tasks'])}h")
        print(f"  Total Hours: {plan['total_estimated_hours']}")

        print("\n🔄 Task Decomposition:")
        for task in plan["tasks"]:
            indent = "  " if "Part" not in task["name"] else "    →"
            parallel = " [PARALLEL]" if not task["dependencies"] else ""
            print(f"{indent} {task['name']} ({task['estimated_hours']}h){parallel}")

        # Analyze parallelization
        parallel_tasks = [t for t in plan["tasks"] if not t["dependencies"]]
        print("\n⚡ Parallel Execution:")
        print(f"  Tasks that can run in parallel: {len(parallel_tasks)}")
        print(f"  Maximum parallel paths: {config.parallel_tasks_limit}")

        # Show critical path
        if plan.get("critical_path"):
            critical_time = sum(
                t["estimated_hours"] for t in plan["tasks"] if t["id"] in plan["critical_path"]
            )
            print("\n📊 Critical Path Analysis:")
            print(f"  Path: {' → '.join(plan['critical_path'][:3])}...")
            print(f"  Critical Path Time: {critical_time}h")
            print(
                f"  Time Savings from Parallelization: {plan['total_estimated_hours'] - critical_time:.1f}h"
            )


async def main():
    """Run all planning demos."""
    print("\n🚀 Planner Agent Demo")
    print("=" * 60)
    print("Demonstrating hierarchical task planning with 4-hour rule")

    # Demo 1: Simple planning
    await demo_simple_plan()

    # Demo 2: Complex migration
    await demo_complex_migration()

    # Demo 3: Hierarchical decomposition
    await demo_hierarchical_planning()

    print("\n✨ Planning demos completed!")
    print("\n💡 Key Features Demonstrated:")
    print("  ✓ Task decomposition (4-hour rule)")
    print("  ✓ Dependency analysis")
    print("  ✓ Milestone creation")
    print("  ✓ Critical path analysis")
    print("  ✓ Parallel execution planning")
    print("  ✓ Time estimation with buffers")
    print("  ✓ Gantt chart generation")


if __name__ == "__main__":
    asyncio.run(main())
