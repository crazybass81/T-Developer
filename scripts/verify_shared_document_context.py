#!/usr/bin/env python3
"""SharedDocumentContext 통합 검증 스크립트

이 스크립트는 UpgradeOrchestrator와 NewBuildOrchestrator에
SharedDocumentContext가 올바르게 통합되었는지 확인합니다.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.packages.memory.document_context import SharedDocumentContext
from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator,
    UpgradeConfig
)
from backend.packages.orchestrator.newbuild_orchestrator import (
    NewBuildOrchestrator,
    NewBuildConfig
)


async def test_shared_document_context():
    """SharedDocumentContext 기본 기능 테스트"""
    print("=" * 80)
    print("🧪 Testing SharedDocumentContext Basic Functionality")
    print("=" * 80)
    
    # SharedDocumentContext 생성
    doc_context = SharedDocumentContext()
    
    # 문서 추가 테스트
    print("\n1. Adding documents...")
    doc_context.add_document(
        "RequirementAnalyzer",
        {"requirements": "Build a web app", "priority": "high"},
        document_type="analysis"
    )
    doc_context.add_document(
        "ExternalResearcher",
        {"best_practices": ["Use React", "Apply SOLID"], "references": []},
        document_type="research"
    )
    
    # 문서 조회 테스트
    print("2. Retrieving documents...")
    req_doc = doc_context.get_document("RequirementAnalyzer")
    if req_doc:
        print(f"   ✅ RequirementAnalyzer document found: {req_doc['type']}")
    else:
        print("   ❌ RequirementAnalyzer document not found")
    
    # 모든 문서 조회
    all_docs = doc_context.get_all_documents()
    print(f"3. Total documents in current loop: {len(all_docs)}")
    for agent_name, doc in all_docs.items():
        print(f"   - {agent_name}: {doc['type']} (created at {doc['created_at']})")
    
    # 새 루프 시작
    print("\n4. Starting new loop...")
    doc_context.start_new_loop()
    print(f"   Current loop number: {doc_context.current_loop_number}")
    
    # 새 루프에서 문서 추가
    doc_context.add_document(
        "GapAnalyzer",
        {"gaps": ["Missing authentication", "No tests"], "gap_score": 0.7},
        document_type="analysis"
    )
    
    # AI 컨텍스트 생성
    print("\n5. Generating AI context...")
    ai_context = doc_context.get_context_for_ai(include_history=True)
    print(f"   Context length: {len(ai_context)} characters")
    print(f"   Preview: {ai_context[:200]}...")
    
    # 분석 요약
    print("\n6. Analysis summary:")
    summary = doc_context.get_analysis_summary()
    print(f"   Total loops: {summary['total_loops']}")
    print(f"   Total documents: {summary['total_documents']}")
    print(f"   Current loop progress: {summary['current_loop_progress']}")
    
    print("\n✅ SharedDocumentContext basic tests completed!")
    return True


async def test_upgrade_orchestrator_integration():
    """UpgradeOrchestrator의 SharedDocumentContext 통합 테스트"""
    print("\n" + "=" * 80)
    print("🔧 Testing UpgradeOrchestrator SharedDocumentContext Integration")
    print("=" * 80)
    
    try:
        # 테스트 설정
        config = UpgradeConfig(
            project_path="/tmp/test-project",
            output_dir="/tmp/test-output",
            # AI 드리븐 워크플로우 활성화
            ai_driven_workflow=True,
            allow_parallel_execution=True,
            enable_evolution_loop=True,
            max_evolution_iterations=1  # 테스트를 위해 1회만
        )
        
        print("\n1. Creating UpgradeOrchestrator with AI-driven workflow enabled...")
        orchestrator = UpgradeOrchestrator(config)
        
        print("2. Initializing orchestrator...")
        await orchestrator.initialize()
        
        # SharedDocumentContext 확인
        if orchestrator.document_context:
            print("   ✅ SharedDocumentContext is initialized")
        else:
            print("   ❌ SharedDocumentContext is NOT initialized")
            return False
        
        # 에이전트들이 document_context를 가지고 있는지 확인
        print("\n3. Checking agent integrations...")
        agents_to_check = [
            ("requirement_analyzer", "RequirementAnalyzer"),
            ("external_researcher", "ExternalResearcher"),
            ("gap_analyzer", "GapAnalyzer"),
            ("system_architect", "SystemArchitect"),
            ("orchestrator_designer", "OrchestratorDesigner")
        ]
        
        for attr_name, display_name in agents_to_check:
            agent = getattr(orchestrator, attr_name, None)
            if agent and hasattr(agent, 'document_context'):
                if agent.document_context is orchestrator.document_context:
                    print(f"   ✅ {display_name} shares the same document context")
                else:
                    print(f"   ⚠️ {display_name} has different document context")
            else:
                print(f"   ❌ {display_name} doesn't have document context")
        
        # 동적 워크플로우 메서드 확인
        print("\n4. Checking dynamic workflow methods...")
        if hasattr(orchestrator, '_execute_dynamic_workflow'):
            print("   ✅ _execute_dynamic_workflow method exists")
        else:
            print("   ❌ _execute_dynamic_workflow method NOT found")
        
        if hasattr(orchestrator, '_execute_single_agent'):
            print("   ✅ _execute_single_agent method exists")
        else:
            print("   ❌ _execute_single_agent method NOT found")
        
        print("\n✅ UpgradeOrchestrator integration test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ UpgradeOrchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_newbuild_orchestrator_integration():
    """NewBuildOrchestrator의 SharedDocumentContext 통합 테스트"""
    print("\n" + "=" * 80)
    print("🚀 Testing NewBuildOrchestrator SharedDocumentContext Integration")
    print("=" * 80)
    
    try:
        # 테스트 설정
        config = NewBuildConfig(
            project_name="test-shared-context",
            output_dir="/tmp/test-newbuild",
            project_type="api",
            language="python",
            framework="fastapi",
            enable_evolution_loop=True,
            max_evolution_iterations=1,  # 테스트를 위해 1회만
            ai_driven_design=True
        )
        
        print("\n1. Creating NewBuildOrchestrator...")
        orchestrator = NewBuildOrchestrator(config)
        
        print("2. Initializing orchestrator...")
        await orchestrator.initialize()
        
        # SharedDocumentContext 확인
        if orchestrator.document_context:
            print("   ✅ SharedDocumentContext is initialized")
        else:
            print("   ❌ SharedDocumentContext is NOT initialized")
            return False
        
        # 에이전트들이 document_context를 가지고 있는지 확인
        print("\n3. Checking agent integrations...")
        agents_to_check = [
            ("requirement_analyzer", "RequirementAnalyzer"),
            ("external_researcher", "ExternalResearcher"),
            ("gap_analyzer", "GapAnalyzer"),
            ("system_architect", "SystemArchitect"),
            ("orchestrator_designer", "OrchestratorDesigner"),
            ("planner_agent", "PlannerAgent"),
            ("task_creator_agent", "TaskCreatorAgent"),
            ("code_generator", "CodeGenerator")
        ]
        
        all_integrated = True
        for attr_name, display_name in agents_to_check:
            agent = getattr(orchestrator, attr_name, None)
            if agent and hasattr(agent, 'document_context'):
                if agent.document_context is orchestrator.document_context:
                    print(f"   ✅ {display_name} shares the same document context")
                else:
                    print(f"   ⚠️ {display_name} has different document context")
                    all_integrated = False
            else:
                print(f"   ❌ {display_name} doesn't have document context")
                all_integrated = False
        
        # Evolution Loop 에이전트도 확인
        print("\n4. Checking Evolution Loop agents...")
        evolution_agents = [
            ("static_analyzer", "StaticAnalyzer"),
            ("code_analyzer", "CodeAnalysisAgent"),
            ("behavior_analyzer", "BehaviorAnalyzer"),
            ("impact_analyzer", "ImpactAnalyzer"),
            ("quality_gate", "QualityGate")
        ]
        
        for attr_name, display_name in evolution_agents:
            agent = getattr(orchestrator, attr_name, None)
            if agent and hasattr(agent, 'document_context'):
                if agent.document_context is orchestrator.document_context:
                    print(f"   ✅ {display_name} shares the same document context")
                else:
                    print(f"   ⚠️ {display_name} has different document context")
                    all_integrated = False
            else:
                print(f"   ❌ {display_name} doesn't have document context")
                all_integrated = False
        
        if all_integrated:
            print("\n✅ NewBuildOrchestrator integration test completed successfully!")
        else:
            print("\n⚠️ NewBuildOrchestrator integration has some issues")
        
        return all_integrated
        
    except Exception as e:
        print(f"\n❌ NewBuildOrchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """메인 테스트 실행"""
    print("=" * 80)
    print("🔍 SharedDocumentContext Integration Verification")
    print(f"📅 {datetime.now().isoformat()}")
    print("=" * 80)
    
    results = []
    
    # 1. SharedDocumentContext 기본 기능 테스트
    result1 = await test_shared_document_context()
    results.append(("SharedDocumentContext Basic", result1))
    
    # 2. UpgradeOrchestrator 통합 테스트
    result2 = await test_upgrade_orchestrator_integration()
    results.append(("UpgradeOrchestrator Integration", result2))
    
    # 3. NewBuildOrchestrator 통합 테스트
    result3 = await test_newbuild_orchestrator_integration()
    results.append(("NewBuildOrchestrator Integration", result3))
    
    # 최종 결과 요약
    print("\n" + "=" * 80)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 All verification tests PASSED!")
        print("SharedDocumentContext is successfully integrated!")
    else:
        print("⚠️ Some tests FAILED. Please review the issues above.")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)