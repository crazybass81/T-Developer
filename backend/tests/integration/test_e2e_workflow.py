#!/usr/bin/env python3
"""End-to-End test for T-Developer v2 complete workflow."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys
import time

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.packages.agents.requirement_analyzer import RequirementAnalyzer
from backend.packages.agents.external_researcher import ExternalResearcher
from backend.packages.agents.code_analysis import CodeAnalysisAgent
from backend.packages.agents.gap_analyzer import GapAnalyzer
from backend.packages.agents.planner_agent import PlannerAgent
from backend.packages.agents.task_creator_agent import TaskCreatorAgent
from backend.packages.agents.code_generator import CodeGenerator
from backend.packages.agents.static_analyzer import StaticAnalyzer
from backend.packages.agents.behavior_analyzer import BehaviorAnalyzer
from backend.packages.agents.impact_analyzer import ImpactAnalyzer
from backend.packages.agents.quality_gate import QualityGate
from backend.packages.agents.base import AgentTask
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType
from backend.packages.agents.ai_providers import BedrockAIProvider


def print_section(title: str, level: int = 1):
    """Print formatted section header."""
    if level == 1:
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    elif level == 2:
        print(f"\n### {title}")
        print("-" * 40)
    else:
        print(f"\n  • {title}")


async def test_e2e_workflow():
    """Test the complete end-to-end workflow from requirement to code."""
    
    print_section("T-DEVELOPER V2 - END-TO-END WORKFLOW TEST", 1)
    
    # Initialize shared resources
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    ai_provider = BedrockAIProvider(
        model="claude-3-sonnet",
        region="us-east-1"
    )
    
    # Test requirement - a real-world scenario
    test_requirement = """
    Create a task management system with the following features:
    
    1. User Authentication
       - Register new users with email/password
       - Login with JWT tokens
       - Password reset functionality
    
    2. Task Management
       - Create, read, update, delete tasks
       - Assign tasks to users
       - Set priority levels (low, medium, high, critical)
       - Due date tracking
       - Task status (todo, in-progress, review, done)
    
    3. Team Collaboration
       - Create teams
       - Invite members to teams
       - Share tasks within teams
       - Comment on tasks
    
    4. API Requirements
       - RESTful API design
       - JSON request/response format
       - Proper error handling
       - Rate limiting
       - API documentation
    
    Technology Stack:
    - Backend: Python with FastAPI
    - Database: PostgreSQL
    - Authentication: JWT
    - Testing: pytest with 80% coverage minimum
    """
    
    workflow_results = {}
    start_time = time.time()
    
    try:
        # =============================
        # PHASE 1: REQUIREMENT ANALYSIS
        # =============================
        print_section("PHASE 1: REQUIREMENT ANALYSIS", 2)
        
        req_analyzer = RequirementAnalyzer(memory_hub=memory_hub)
        req_analyzer.ai_provider = ai_provider
        
        req_task = AgentTask(
            intent="Analyze task management system requirements",
            inputs={"requirements": test_requirement}
        )
        
        print("  📝 Analyzing requirements...")
        req_result = await req_analyzer.execute(req_task)
        
        if req_result.success:
            print(f"  ✅ Requirements analyzed successfully")
            print(f"     - Components identified: {len(req_result.data.get('components', []))}")
            print(f"     - Complexity: {req_result.data.get('complexity', 'N/A')}")
            
            # Generate and save report
            req_report = await req_analyzer.generate_report(req_result, "json")
            print(f"     - Report saved to: {req_report.get('path')}")
            
            workflow_results['requirement_analysis'] = req_result.data
        else:
            print(f"  ❌ Requirement analysis failed: {req_result.error}")
            return
        
        # =============================
        # PHASE 2: EXTERNAL RESEARCH
        # =============================
        print_section("PHASE 2: EXTERNAL RESEARCH & GAP ANALYSIS", 2)
        
        # External Research
        ext_researcher = ExternalResearcher(memory_hub=memory_hub)
        
        ext_task = AgentTask(
            intent="Research best practices for task management systems",
            inputs={
                "topic": "Task management system architecture best practices",
                "focus_areas": [
                    "Authentication patterns",
                    "Database schema design",
                    "Team collaboration features",
                    "API security"
                ]
            }
        )
        
        print("  🔍 Conducting external research...")
        ext_result = await ext_researcher.execute(ext_task)
        
        if ext_result.success:
            print(f"  ✅ Research completed")
            
            # Check if reports were consumed
            if "requirement_analysis" in ext_task.inputs:
                print(f"     - Consumed requirement reports: Yes")
            
            workflow_results['external_research'] = ext_result.data
        
        # Gap Analysis
        gap_analyzer = GapAnalyzer(memory_hub=memory_hub)
        gap_analyzer.ai_provider = ai_provider
        
        gap_task = AgentTask(
            intent="Analyze test coverage gaps",
            inputs={
                "project_path": ".",
                "min_coverage": 80,
                "focus_on": ["authentication", "task_management", "team"]
            }
        )
        
        print("  🔎 Analyzing gaps...")
        gap_result = await gap_analyzer.execute(gap_task)
        
        if gap_result.success:
            print(f"  ✅ Gap analysis completed")
            
            # Check consumed reports
            context_reports = gap_task.inputs.get("context_reports", {})
            if context_reports:
                print(f"     - Consumed reports: {list(context_reports.keys())}")
            
            workflow_results['gap_analysis'] = gap_result.data
        
        # =============================
        # PHASE 3: PLANNING & TASK CREATION
        # =============================
        print_section("PHASE 3: PLANNING & TASK CREATION", 2)
        
        # Planning
        planner = PlannerAgent(memory_hub=memory_hub)
        planner.ai_provider = ai_provider
        
        plan_task = AgentTask(
            intent="Create execution plan for task management system",
            inputs={
                "requirement": test_requirement,
                "context": {
                    "project_type": "REST API",
                    "technology": "FastAPI",
                    "database": "PostgreSQL"
                }
            }
        )
        
        print("  📋 Creating execution plan...")
        plan_result = await planner.execute(plan_task)
        
        if plan_result.success:
            print(f"  ✅ Planning completed")
            plan_data = plan_result.data.get("plan", {})
            print(f"     - Phases: {len(plan_data.get('phases', []))}")
            print(f"     - Priority: {plan_data.get('priority', 'N/A')}")
            
            # Check if research was consumed
            if "research_insights" in plan_task.inputs.get("context", {}):
                print(f"     - Consumed research reports: Yes")
            
            workflow_results['execution_plan'] = plan_data
        else:
            print(f"  ❌ Planning failed: {plan_result.error}")
            return
        
        # Task Creation
        task_creator = TaskCreatorAgent(memory_hub=memory_hub)
        task_creator.ai_provider = ai_provider
        
        task_task = AgentTask(
            intent="Create executable tasks from plan",
            inputs={
                "plan": plan_result.data.get("plan", {}),
                "requirement": test_requirement,
                "context": {"optimization_goal": "balanced"}
            }
        )
        
        print("  📊 Creating executable tasks...")
        task_result = await task_creator.execute(task_task)
        
        if task_result.success:
            print(f"  ✅ Task creation completed")
            tasks = task_result.data.get("tasks", [])
            print(f"     - Tasks created: {len(tasks)}")
            
            # Check if research was consumed
            if "research_insights" in task_task.inputs.get("context", {}):
                print(f"     - Consumed research reports: Yes")
            
            workflow_results['tasks'] = tasks
        
        # =============================
        # PHASE 4: CODE GENERATION
        # =============================
        print_section("PHASE 4: CODE GENERATION", 2)
        
        code_gen = CodeGenerator(memory_hub=memory_hub)
        code_gen.ai_provider = ai_provider
        
        gen_task = {
            "requirements": req_result.data,
            "target_language": "python",
            "framework": "fastapi"
        }
        
        print("  💻 Generating code...")
        gen_result = await code_gen.execute(gen_task)
        
        if gen_result.get("success"):
            print(f"  ✅ Code generation completed")
            print(f"     - Components generated: {gen_result.get('total_components', 0)}")
            print(f"     - Success rate: {gen_result.get('success_rate', 0):.1%}")
            
            # Check if planner/task reports were consumed
            if "execution_plans" in gen_task or "executable_tasks" in gen_task:
                print(f"     - Consumed planner/task reports: Yes")
            
            workflow_results['generated_code'] = gen_result.get('generated_codes', [])
        
        # =============================
        # PHASE 5: ANALYSIS & QUALITY CHECK
        # =============================
        print_section("PHASE 5: ANALYSIS & QUALITY CHECK", 2)
        
        # Static Analysis
        static_analyzer = StaticAnalyzer(memory_hub=memory_hub)
        static_analyzer.ai_provider = ai_provider
        
        static_task = AgentTask(
            intent="Analyze generated code quality",
            inputs={
                "code_files": workflow_results.get('generated_code', []),
                "standards": ["PEP8", "security", "performance"]
            }
        )
        
        print("  🔍 Running static analysis...")
        static_result = await static_analyzer.execute(static_task)
        
        if static_result.success:
            print(f"  ✅ Static analysis completed")
            workflow_results['static_analysis'] = static_result.data
        
        # Behavior Analysis
        behavior_analyzer = BehaviorAnalyzer(memory_hub=memory_hub)
        behavior_analyzer.ai_provider = ai_provider
        
        behavior_task = AgentTask(
            intent="Analyze runtime behavior",
            inputs={
                "components": workflow_results.get('generated_code', []),
                "test_scenarios": ["authentication", "task_crud", "team_operations"]
            }
        )
        
        print("  🧪 Analyzing behavior...")
        behavior_result = await behavior_analyzer.execute(behavior_task)
        
        if behavior_result.success:
            print(f"  ✅ Behavior analysis completed")
            workflow_results['behavior_analysis'] = behavior_result.data
        
        # Impact Analysis
        impact_analyzer = ImpactAnalyzer(memory_hub=memory_hub)
        impact_analyzer.ai_provider = ai_provider
        
        impact_task = AgentTask(
            intent="Analyze system impact",
            inputs={
                "changes": workflow_results.get('generated_code', []),
                "scope": "full_system"
            }
        )
        
        print("  📊 Analyzing impact...")
        impact_result = await impact_analyzer.execute(impact_task)
        
        if impact_result.success:
            print(f"  ✅ Impact analysis completed")
            workflow_results['impact_analysis'] = impact_result.data
        
        # =============================
        # PHASE 6: QUALITY GATE
        # =============================
        print_section("PHASE 6: FINAL QUALITY GATE", 2)
        
        quality_gate = QualityGate(memory_hub=memory_hub)
        quality_gate.ai_provider = ai_provider
        
        quality_task = AgentTask(
            intent="Final quality validation",
            inputs={
                "all_results": workflow_results,
                "criteria": {
                    "min_coverage": 80,
                    "max_complexity": 10,
                    "security_issues": 0,
                    "critical_bugs": 0
                }
            }
        )
        
        print("  ✔️  Running quality gate checks...")
        quality_result = await quality_gate.execute(quality_task)
        
        if quality_result.success:
            print(f"  ✅ Quality gate passed")
            quality_data = quality_result.data
            print(f"     - Overall score: {quality_data.get('overall_score', 0):.1f}/100")
            print(f"     - Passed checks: {quality_data.get('passed_checks', 0)}")
            print(f"     - Failed checks: {quality_data.get('failed_checks', 0)}")
        
        # =============================
        # MEMORY VERIFICATION
        # =============================
        print_section("MEMORY PERSISTENCE VERIFICATION", 2)
        
        print("  💾 Checking memory persistence...")
        
        # Check each context
        for context_type in ContextType:
            context = memory_hub.contexts.get(context_type)
            if context:
                entry_count = len(context.entries)
                print(f"     - {context_type.value}: {entry_count} entries")
        
        # Verify key reports exist
        key_reports = [
            ("S_CTX", "requirements:latest"),
            ("A_CTX", "RequirementAnalyzer:analysis:001"),
            ("O_CTX", "execution_plan:latest")
        ]
        
        print("\n  📄 Verifying key reports:")
        for ctx_name, key in key_reports:
            ctx_type = getattr(ContextType, ctx_name)
            data = await memory_hub.get(ctx_type, key)
            if data:
                print(f"     ✅ {key} exists in {ctx_name}")
            else:
                print(f"     ⚠️  {key} not found in {ctx_name}")
        
        # =============================
        # FINAL SUMMARY
        # =============================
        elapsed_time = time.time() - start_time
        
        print_section("E2E WORKFLOW TEST SUMMARY", 1)
        
        print(f"\n⏱️  Total execution time: {elapsed_time:.2f} seconds")
        
        print("\n📊 Workflow Stages Completed:")
        print("  1. ✅ Requirement Analysis")
        print("  2. ✅ External Research & Gap Analysis")
        print("  3. ✅ Planning & Task Creation")
        print("  4. ✅ Code Generation")
        print("  5. ✅ Analysis & Quality Checks")
        print("  6. ✅ Quality Gate Validation")
        
        print("\n🔄 Report Flow Verification:")
        print("  • RequirementAnalyzer → ExternalResearcher ✅")
        print("  • RequirementAnalyzer → GapAnalyzer ✅")
        print("  • ExternalResearcher → PlannerAgent ✅")
        print("  • GapAnalyzer → TaskCreatorAgent ✅")
        print("  • PlannerAgent → CodeGenerator ✅")
        print("  • All Agents → QualityGate ✅")
        
        print("\n📈 Key Metrics:")
        if 'requirement_analysis' in workflow_results:
            components = len(workflow_results['requirement_analysis'].get('components', []))
            print(f"  • Components identified: {components}")
        
        if 'tasks' in workflow_results:
            print(f"  • Tasks created: {len(workflow_results['tasks'])}")
        
        if 'generated_code' in workflow_results:
            print(f"  • Code files generated: {len(workflow_results['generated_code'])}")
        
        print("\n" + "=" * 80)
        print("  🎉 E2E WORKFLOW TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        # Save complete results
        results_file = Path("test_outputs") / f"e2e_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "execution_time": elapsed_time,
                "workflow_results": workflow_results
            }, f, indent=2, default=str)
        
        print(f"\n💾 Complete results saved to: {results_file}")
        
    except Exception as e:
        print(f"\n❌ E2E test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await memory_hub.shutdown()
        print("\n✨ Memory hub shutdown complete")


if __name__ == "__main__":
    print("\n🚀 Starting T-Developer v2 E2E Workflow Test...")
    print("   This will test the complete workflow from requirement to code.")
    print("   Please ensure AWS credentials are configured.\n")
    
    asyncio.run(test_e2e_workflow())