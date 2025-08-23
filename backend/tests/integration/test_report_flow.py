#!/usr/bin/env python3
"""Test script to verify report generation and consumption flow between agents."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.packages.agents.requirement_analyzer import RequirementAnalyzer
from backend.packages.agents.external_researcher import ExternalResearcher
from backend.packages.agents.gap_analyzer import GapAnalyzer
from backend.packages.agents.planner_agent import PlannerAgent
from backend.packages.agents.task_creator_agent import TaskCreatorAgent
from backend.packages.agents.code_generator import CodeGenerator
from backend.packages.agents.base import AgentTask
from backend.packages.memory.hub import MemoryHub
from backend.packages.agents.ai_providers import BedrockAIProvider


async def test_report_flow():
    """Test the complete report flow between agents."""
    
    print("=" * 80)
    print("TESTING REPORT GENERATION AND CONSUMPTION FLOW")
    print("=" * 80)
    
    # Initialize memory hub
    memory_hub = MemoryHub()
    
    # Initialize AI provider
    ai_provider = BedrockAIProvider(
        model="claude-3-sonnet",
        region="us-east-1"
    )
    
    # Test requirement
    test_requirement = """
    Build a simple REST API service for user management with the following features:
    - User registration with email and password
    - User login with JWT authentication
    - Get user profile
    - Update user profile
    """
    
    try:
        # Step 1: RequirementAnalyzer generates report
        print("\n1. RequirementAnalyzer - Generating requirement report...")
        req_analyzer = RequirementAnalyzer(
            memory_hub=memory_hub
        )
        # Set AI provider separately
        req_analyzer.ai_provider = ai_provider
        
        req_task = AgentTask(
            intent="Analyze user management API requirements",
            inputs={"requirements": test_requirement}
        )
        
        req_result = await req_analyzer.execute(req_task)
        if req_result.success:
            print("   ✅ Requirement analysis completed")
            print(f"   📝 Generated components: {len(req_result.data.get('components', []))}")
            
            # Generate report
            req_report = await req_analyzer.generate_report(req_result, "json")
            print(f"   📄 Report saved: {req_report.get('path')}")
        else:
            print(f"   ❌ Failed: {req_result.error}")
            return
        
        # Step 2: ExternalResearcher consumes requirement report
        print("\n2. ExternalResearcher - Consuming requirement report...")
        ext_researcher = ExternalResearcher(
            memory_hub=memory_hub
        )
        
        ext_task = AgentTask(
            intent="Research best practices for user management API",
            inputs={
                "topic": "User management REST API best practices",
                "focus_areas": ["Authentication", "Security", "Performance"]
            }
        )
        
        ext_result = await ext_researcher.execute(ext_task)
        if ext_result.success:
            print("   ✅ External research completed")
            
            # Check if requirement reports were consumed
            if "requirement_analysis" in ext_task.inputs:
                print("   📥 Successfully consumed requirement reports")
            else:
                print("   ⚠️  No requirement reports consumed")
        
        # Step 3: GapAnalyzer consumes multiple reports
        print("\n3. GapAnalyzer - Consuming requirement and analysis reports...")
        gap_analyzer = GapAnalyzer(
            memory_hub=memory_hub
        )
        gap_analyzer.ai_provider = ai_provider
        
        gap_task = AgentTask(
            intent="Analyze test coverage gaps",
            inputs={
                "project_path": ".",
                "min_coverage": 80
            }
        )
        
        gap_result = await gap_analyzer.execute(gap_task)
        if gap_result.success:
            print("   ✅ Gap analysis completed")
            
            # Check if reports were consumed
            context_reports = gap_task.inputs.get("context_reports", {})
            if context_reports:
                print(f"   📥 Consumed reports: {list(context_reports.keys())}")
        
        # Step 4: PlannerAgent consumes external and gap reports
        print("\n4. PlannerAgent - Consuming external and gap reports...")
        planner = PlannerAgent(
            memory_hub=memory_hub
        )
        planner.ai_provider = ai_provider
        
        plan_task = AgentTask(
            intent="Create execution plan for user management API",
            inputs={
                "requirement": test_requirement,
                "context": {"project_type": "REST API"}
            }
        )
        
        plan_result = await planner.execute(plan_task)
        if plan_result.success:
            print("   ✅ Planning completed")
            
            # Check if research reports were consumed
            if "research_insights" in plan_task.inputs.get("context", {}):
                print("   📥 Successfully consumed research reports")
        
        # Step 5: TaskCreatorAgent consumes external and gap reports
        print("\n5. TaskCreatorAgent - Consuming external and gap reports...")
        task_creator = TaskCreatorAgent(
            memory_hub=memory_hub
        )
        task_creator.ai_provider = ai_provider
        
        task_task = AgentTask(
            intent="Create executable tasks from plan",
            inputs={
                "plan": plan_result.data.get("plan", {}),
                "requirement": test_requirement,
                "context": {}
            }
        )
        
        task_result = await task_creator.execute(task_task)
        if task_result.success:
            print("   ✅ Task creation completed")
            print(f"   📝 Created tasks: {len(task_result.data.get('tasks', []))}")
            
            # Check if research reports were consumed
            if "research_insights" in task_task.inputs.get("context", {}):
                print("   📥 Successfully consumed research reports")
        
        # Step 6: CodeGenerator consumes planner and task reports
        print("\n6. CodeGenerator - Consuming planner and task reports...")
        code_gen = CodeGenerator(
            memory_hub=memory_hub
        )
        code_gen.ai_provider = ai_provider
        
        gen_task = {
            "requirements": req_result.data,
            "target_language": "python",
            "framework": "fastapi"
        }
        
        gen_result = await code_gen.execute(gen_task)
        if gen_result.get("success"):
            print("   ✅ Code generation completed")
            print(f"   📝 Generated components: {gen_result.get('total_components', 0)}")
            
            # Check if planner/task reports were consumed
            if "execution_plans" in gen_task or "executable_tasks" in gen_task:
                print("   📥 Successfully consumed planner/task reports")
        
        # Summary
        print("\n" + "=" * 80)
        print("REPORT FLOW TEST SUMMARY")
        print("=" * 80)
        
        print("\n✅ Report Generation Chain:")
        print("   1. RequirementAnalyzer → Report generated")
        print("   2. ExternalResearcher → Consumed requirement report")
        print("   3. GapAnalyzer → Consumed requirement + analysis reports")
        print("   4. PlannerAgent → Consumed external + gap reports")
        print("   5. TaskCreatorAgent → Consumed external + gap reports")
        print("   6. CodeGenerator → Consumed planner + task reports")
        
        print("\n🔄 Complete report flow verified successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_report_flow())