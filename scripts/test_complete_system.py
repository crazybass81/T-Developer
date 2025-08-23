#!/usr/bin/env python3
"""T-Developer v2.0 완전 통합 테스트

이 스크립트는 페르소나가 적용된 전체 시스템을 테스트합니다.
- 오케스트레이터 초기화
- 에이전트 페르소나 확인
- SharedDocumentContext 동작
- Evolution Loop 시뮬레이션
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# T-Developer 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator, UpgradeConfig
)
from backend.packages.orchestrator.newbuild_orchestrator import (
    NewBuildOrchestrator, NewBuildConfig
)
from backend.packages.agents.personas import get_all_personas


def print_section(title):
    """섹션 헤더 출력"""
    print("\n" + "=" * 80)
    print(f"🔍 {title}")
    print("=" * 80)


async def test_personas():
    """페르소나 시스템 테스트"""
    print_section("페르소나 시스템 테스트")
    
    personas = get_all_personas()
    print(f"✅ 총 {len(personas)}개 페르소나 정의됨")
    
    # 각 페르소나 확인
    for name, persona in personas.items():
        print(f"\n📌 {name}")
        print(f"   이름: {persona.name}")
        print(f"   역할: {persona.role}")
        print(f"   캐치프레이즈: '{persona.catchphrase}'")
        print(f"   성격: {', '.join([t.value for t in persona.personality_traits])}")
    
    return len(personas) == 17  # 15 에이전트 + 2 오케스트레이터


async def test_upgrade_orchestrator():
    """UpgradeOrchestrator 테스트"""
    print_section("UpgradeOrchestrator 테스트")
    
    try:
        # 설정
        config = UpgradeConfig(
            project_path="/tmp/test-project",
            output_dir="/tmp/test-output",
            enable_evolution_loop=False,  # 테스트를 위해 비활성화
            ai_driven_workflow=True
        )
        
        # 오케스트레이터 생성
        print("1. 오케스트레이터 생성...")
        orchestrator = UpgradeOrchestrator(config)
        
        # 페르소나 확인
        if orchestrator.persona:
            print(f"✅ 페르소나 활성화: {orchestrator.persona.name}")
            print(f"   '{orchestrator.persona.catchphrase}'")
        else:
            print("❌ 페르소나 없음")
            return False
        
        # 초기화
        print("2. 초기화...")
        await orchestrator.initialize()
        
        # SharedDocumentContext 확인
        if orchestrator.document_context:
            print("✅ SharedDocumentContext 활성화")
        else:
            print("❌ SharedDocumentContext 없음")
            return False
        
        # 에이전트 페르소나 확인
        print("3. 에이전트 페르소나 확인...")
        agents_with_persona = 0
        agents_to_check = [
            ("requirement_analyzer", "RequirementAnalyzer"),
            ("external_researcher", "ExternalResearcher"),
            ("gap_analyzer", "GapAnalyzer"),
            ("system_architect", "SystemArchitect"),
            ("orchestrator_designer", "OrchestratorDesigner"),
            ("planner_agent", "PlannerAgent"),
            ("task_creator_agent", "TaskCreatorAgent"),
            ("code_generator", "CodeGenerator"),
            ("quality_gate", "QualityGate")
        ]
        
        for attr_name, display_name in agents_to_check:
            agent = getattr(orchestrator, attr_name, None)
            if agent and hasattr(agent, 'persona') and agent.persona:
                print(f"   ✅ {display_name}: {agent.persona.name}")
                agents_with_persona += 1
            else:
                print(f"   ⚠️ {display_name}: 페르소나 없음")
        
        print(f"\n페르소나 적용된 에이전트: {agents_with_persona}/{len(agents_to_check)}")
        
        # 동적 워크플로우 메서드 확인
        print("4. 동적 워크플로우 기능 확인...")
        if hasattr(orchestrator, '_execute_dynamic_workflow'):
            print("   ✅ AI-driven dynamic workflow 지원")
        else:
            print("   ❌ Dynamic workflow 미지원")
        
        return agents_with_persona >= 7  # 최소 7개 이상 페르소나 적용
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_newbuild_orchestrator():
    """NewBuildOrchestrator 테스트"""
    print_section("NewBuildOrchestrator 테스트")
    
    try:
        # 설정
        config = NewBuildConfig(
            project_name="test-project",
            output_dir="/tmp/test-output",
            project_type="api",
            language="python",
            framework="fastapi",
            enable_evolution_loop=False  # 테스트를 위해 비활성화
        )
        
        # 오케스트레이터 생성
        print("1. 오케스트레이터 생성...")
        orchestrator = NewBuildOrchestrator(config)
        
        # 페르소나 확인
        if orchestrator.persona:
            print(f"✅ 페르소나 활성화: {orchestrator.persona.name}")
            print(f"   '{orchestrator.persona.catchphrase}'")
        else:
            print("❌ 페르소나 없음")
            return False
        
        # 초기화
        print("2. 초기화...")
        await orchestrator.initialize()
        
        # SharedDocumentContext 확인
        if orchestrator.document_context:
            print("✅ SharedDocumentContext 활성화")
            
            # 문서 추가 테스트
            orchestrator.document_context.add_document(
                "TestAgent",
                {"test": "data", "timestamp": datetime.now().isoformat()},
                document_type="test"
            )
            
            docs = orchestrator.document_context.get_all_documents()
            if "TestAgent" in docs:
                print("✅ 문서 저장 및 조회 성공")
            else:
                print("❌ 문서 저장 실패")
        else:
            print("❌ SharedDocumentContext 없음")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_document_sharing():
    """SharedDocumentContext 문서 공유 테스트"""
    print_section("SharedDocumentContext 문서 공유 테스트")
    
    from backend.packages.memory.document_context import SharedDocumentContext
    
    # 컨텍스트 생성
    context = SharedDocumentContext()
    
    # 시뮬레이션: Evolution Loop 첫 번째 반복
    print("1. Evolution Loop 첫 번째 반복 시뮬레이션...")
    
    # 각 에이전트가 문서 추가
    agents = [
        ("RequirementAnalyzer", {"requirements": "Build API", "priority": "high"}),
        ("ExternalResearcher", {"best_practices": ["REST", "GraphQL"], "trends": []}),
        ("GapAnalyzer", {"gaps": ["authentication", "testing"], "gap_score": 0.7}),
        ("SystemArchitect", {"architecture": "microservices", "components": []}),
        ("PlannerAgent", {"phases": ["design", "implement", "test"], "timeline": "2 weeks"})
    ]
    
    for agent_name, doc_content in agents:
        context.add_document(agent_name, doc_content, document_type="analysis")
        print(f"   ✅ {agent_name} 문서 추가")
    
    # 모든 문서 조회
    all_docs = context.get_all_documents()
    print(f"\n2. 현재 루프 문서 수: {len(all_docs)}")
    
    # AI 컨텍스트 생성
    ai_context = context.get_context_for_ai(include_history=False)
    print(f"3. AI 컨텍스트 크기: {len(ai_context)} 문자")
    
    # 새 루프 시작
    context.start_new_loop()
    print(f"4. 새 루프 시작 (루프 번호: {context.current_loop_number})")
    
    # 히스토리 확인
    history = context.get_history()
    print(f"5. 히스토리 루프 수: {len(history)}")
    
    return len(all_docs) == 5 and len(history) == 1


async def test_mock_fake_removal():
    """Mock/Fake 코드 제거 확인"""
    print_section("Mock/Fake 코드 제거 확인")
    
    import subprocess
    
    # 실제 소스 코드에서 mock/fake 검색 (테스트 제외)
    result = subprocess.run(
        ["grep", "-r", "-i", "mock\\|fake", 
         "/home/ec2-user/T-Developer/backend/packages",
         "--include=*.py"],
        capture_output=True,
        text=True
    )
    
    # 결과 분석
    lines = result.stdout.strip().split('\n') if result.stdout else []
    
    # 주석과 문서 제외
    actual_usage = []
    for line in lines:
        if line and '#' not in line and '"""' not in line and "'''" not in line:
            # 테스트 템플릿 제외
            if 'templates/test_' not in line:
                actual_usage.append(line)
    
    if actual_usage:
        print(f"⚠️ Mock/Fake 사용 발견 ({len(actual_usage)}개):")
        for usage in actual_usage[:5]:  # 처음 5개만 표시
            print(f"   {usage[:100]}...")
    else:
        print("✅ 실제 코드에서 Mock/Fake 사용 없음")
    
    return len(actual_usage) == 0


async def main():
    """메인 테스트 실행"""
    print("=" * 80)
    print("🚀 T-Developer v2.0 완전 통합 테스트")
    print(f"📅 {datetime.now().isoformat()}")
    print("=" * 80)
    
    results = {}
    
    # 1. 페르소나 시스템 테스트
    results['personas'] = await test_personas()
    
    # 2. UpgradeOrchestrator 테스트
    results['upgrade_orchestrator'] = await test_upgrade_orchestrator()
    
    # 3. NewBuildOrchestrator 테스트
    results['newbuild_orchestrator'] = await test_newbuild_orchestrator()
    
    # 4. SharedDocumentContext 테스트
    results['document_sharing'] = await test_document_sharing()
    
    # 5. Mock/Fake 제거 확인
    results['no_mock_fake'] = await test_mock_fake_removal()
    
    # 최종 결과
    print_section("테스트 결과 요약")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 모든 테스트 통과! T-Developer v2.0 준비 완료!")
        print("✨ 특징:")
        print("  - 17개 페르소나 (15 에이전트 + 2 오케스트레이터)")
        print("  - SharedDocumentContext로 완전한 정보 공유")
        print("  - Evolution Loop 자동 개선")
        print("  - 100% Real AI (Mock/Fake 제로)")
        print("  - AI-Driven Dynamic Workflow")
    else:
        print("⚠️ 일부 테스트 실패. 위 결과를 확인하세요.")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)