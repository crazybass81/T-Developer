#!/usr/bin/env python3
"""모든 오케스트레이터 통합 테스트 스크립트

UpgradeOrchestrator와 NewBuildOrchestrator를 모두 테스트합니다.
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator,
    UpgradeConfig
)
from backend.packages.orchestrator.newbuild_orchestrator import (
    NewBuildOrchestrator,
    NewBuildConfig
)


async def test_upgrade_orchestrator():
    """UpgradeOrchestrator 테스트"""
    print("\n" + "=" * 80)
    print("📈 Testing UpgradeOrchestrator")
    print("=" * 80)
    
    config = UpgradeConfig(
        project_path="/home/ec2-user/T-Developer",
        output_dir="/tmp/t-developer/upgrade-reports",
        enable_dynamic_analysis=False,
        include_behavior_analysis=True,
        generate_impact_matrix=True,
        generate_recommendations=True,
        safe_mode=True,
        parallel_analysis=True,
        max_execution_time=300,
        enable_evolution_loop=False,
        auto_generate_agents=False,
        auto_implement_code=False
    )
    
    requirements = """
    T-Developer의 UpgradeOrchestrator를 완성하고 최적화합니다.
    - 모든 에이전트가 정해진 순서대로 실행되도록 보장
    - 아키텍트 에이전트와 오케스트레이터 디자이너 통합
    - 문서 생성 및 MD 파일 저장 기능 완성
    - 테스트 커버리지 80% 이상 달성
    """
    
    try:
        orchestrator = UpgradeOrchestrator(config)
        await orchestrator.initialize()
        
        start_time = datetime.now()
        report = await orchestrator.analyze(requirements, include_research=True)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\n✅ UpgradeOrchestrator Test Results:")
        print(f"  - Execution Time: {execution_time:.2f}s")
        print(f"  - System Health Score: {report.system_health_score:.1f}/100")
        print(f"  - Total Issues Found: {report.total_issues_found}")
        print(f"  - Tasks Created: {len(report.tasks_breakdown)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ UpgradeOrchestrator test failed: {e}")
        return False


async def test_newbuild_orchestrator():
    """NewBuildOrchestrator 테스트"""
    print("\n" + "=" * 80)
    print("🏗️ Testing NewBuildOrchestrator")
    print("=" * 80)
    
    config = NewBuildConfig(
        project_name=f"test-api-{datetime.now().strftime('%H%M%S')}",
        output_dir="/tmp/t-developer/new-projects",
        project_type="api",
        language="python",
        framework="fastapi",
        include_tests=True,
        include_docs=True,
        include_docker=True,
        ai_driven_design=True,
        auto_generate_all=True,
        max_execution_time=300,
        max_files=20
    )
    
    requirements = """
    Create a RESTful API for a simple blog system:
    - User authentication with JWT
    - CRUD operations for blog posts
    - Comment system
    - Category management
    - Search functionality
    - API documentation with Swagger
    """
    
    try:
        orchestrator = NewBuildOrchestrator(config)
        await orchestrator.initialize()
        
        start_time = datetime.now()
        report = await orchestrator.build(requirements)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\n✅ NewBuildOrchestrator Test Results:")
        print(f"  - Execution Time: {execution_time:.2f}s")
        print(f"  - Success: {report.success}")
        print(f"  - Files Created: {len(report.files_created)}")
        print(f"  - Output Path: {report.output_path}")
        
        return report.success
        
    except Exception as e:
        print(f"\n❌ NewBuildOrchestrator test failed: {e}")
        return False


async def compare_orchestrators():
    """두 오케스트레이터 비교 분석"""
    print("\n" + "=" * 80)
    print("📊 Orchestrator Comparison")
    print("=" * 80)
    
    comparison = {
        "UpgradeOrchestrator": {
            "Purpose": "Upgrade/refactor existing projects",
            "Key Features": [
                "Analyzes existing codebase",
                "Identifies gaps and issues",
                "Generates upgrade recommendations",
                "Evolution loop for iterative improvements"
            ],
            "Agents Used": [
                "RequirementAnalyzer",
                "StaticAnalyzer",
                "CodeAnalysisAgent",
                "BehaviorAnalyzer",
                "ImpactAnalyzer",
                "QualityGate",
                "ExternalResearcher",
                "GapAnalyzer",
                "SystemArchitect",
                "OrchestratorDesigner",
                "PlannerAgent",
                "TaskCreatorAgent",
                "CodeGenerator"
            ]
        },
        "NewBuildOrchestrator": {
            "Purpose": "Build new projects from scratch",
            "Key Features": [
                "Creates project structure",
                "Generates all code from requirements",
                "Includes tests and documentation",
                "Sets up CI/CD pipeline"
            ],
            "Agents Used": [
                "RequirementAnalyzer",
                "ExternalResearcher",
                "SystemArchitect",
                "OrchestratorDesigner",
                "PlannerAgent",
                "TaskCreatorAgent",
                "CodeGenerator",
                "QualityGate"
            ]
        }
    }
    
    print("\nComparison Summary:")
    print(json.dumps(comparison, indent=2))
    
    print("\n🔄 Workflow Differences:")
    print("  UpgradeOrchestrator: Analyze → Identify Gaps → Design Changes → Implement")
    print("  NewBuildOrchestrator: Requirements → Design → Create Structure → Generate Code")
    
    print("\n📈 Use Cases:")
    print("  • Use UpgradeOrchestrator for:")
    print("    - Refactoring existing code")
    print("    - Adding new features to existing projects")
    print("    - Debugging and optimization")
    print("    - Technical debt reduction")
    print("\n  • Use NewBuildOrchestrator for:")
    print("    - Creating new projects")
    print("    - Prototyping ideas quickly")
    print("    - Generating boilerplate code")
    print("    - Setting up project templates")


async def main():
    """메인 테스트 실행"""
    print("=" * 80)
    print("🚀 T-Developer Orchestrators Integration Test")
    print("=" * 80)
    
    print("\nThis test will validate both orchestrators:")
    print("1. UpgradeOrchestrator - For upgrading existing projects")
    print("2. NewBuildOrchestrator - For creating new projects")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test UpgradeOrchestrator
    print("\n[1/2] Running UpgradeOrchestrator test...")
    upgrade_success = await test_upgrade_orchestrator()
    results["tests"]["UpgradeOrchestrator"] = {
        "success": upgrade_success,
        "status": "PASSED" if upgrade_success else "FAILED"
    }
    
    # Test NewBuildOrchestrator
    print("\n[2/2] Running NewBuildOrchestrator test...")
    newbuild_success = await test_newbuild_orchestrator()
    results["tests"]["NewBuildOrchestrator"] = {
        "success": newbuild_success,
        "status": "PASSED" if newbuild_success else "FAILED"
    }
    
    # Compare orchestrators
    await compare_orchestrators()
    
    # Final summary
    print("\n" + "=" * 80)
    print("📋 Test Summary")
    print("=" * 80)
    
    all_passed = upgrade_success and newbuild_success
    
    print(f"\n{'✅' if upgrade_success else '❌'} UpgradeOrchestrator: {'PASSED' if upgrade_success else 'FAILED'}")
    print(f"{'✅' if newbuild_success else '❌'} NewBuildOrchestrator: {'PASSED' if newbuild_success else 'FAILED'}")
    
    # Save results
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    results_file = output_dir / f"orchestrators_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Test results saved to: {results_file}")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 All Orchestrator Tests Passed Successfully!")
    else:
        print("⚠️ Some Orchestrator Tests Failed - Review logs for details")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)