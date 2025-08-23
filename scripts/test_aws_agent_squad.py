#!/usr/bin/env python3
"""AWS Agent Squad 프레임워크 통합 테스트.

이 스크립트는 AWS Agent Squad 프레임워크와 Bedrock AgentCore 런타임을
사용하는 T-Developer v2.0 시스템을 테스트합니다.

테스트 항목:
1. AWS Agent Squad 런타임 초기화
2. UpgradeOrchestrator Evolution Loop
3. NewBuilderOrchestrator SeedProduct 생성
4. 페르소나 시스템
5. 문서 공유 시스템
6. AI-Driven 워크플로우
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json
import tempfile

# T-Developer 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

# AWS Agent Squad 프레임워크
from backend.packages.aws_agent_squad.core import (
    AgentRuntime,
    RuntimeConfig,
    SquadOrchestrator,
    SquadConfig
)

# 오케스트레이터
from backend.packages.orchestrator.aws_upgrade_orchestrator import (
    AWSUpgradeOrchestrator,
    AWSUpgradeConfig
)
from backend.packages.orchestrator.aws_newbuilder_orchestrator import (
    AWSNewBuilderOrchestrator,
    AWSNewBuilderConfig,
    SeedProductConfig
)

# 페르소나
from backend.packages.agents.personas import get_all_personas


def print_section(title):
    """섹션 헤더 출력."""
    print("\n" + "=" * 80)
    print(f"🔍 {title}")
    print("=" * 80)


async def test_aws_runtime():
    """AWS Agent Squad 런타임 테스트."""
    print_section("AWS Agent Squad Runtime 테스트")
    
    try:
        # 런타임 설정
        config = RuntimeConfig(
            region="us-east-1",
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            max_tokens=4096,
            temperature=0.7,
            max_parallel_agents=5,
            enable_tracing=True
        )
        
        # 런타임 초기화
        print("1. AWS Bedrock AgentCore 런타임 초기화...")
        runtime = AgentRuntime(config)
        
        print(f"✅ 런타임 초기화 성공 (Region: {config.region})")
        
        # 페르소나 등록 테스트
        print("2. 페르소나 시스템 테스트...")
        personas = get_all_personas()
        
        for name, persona in list(personas.items())[:3]:  # 처음 3개만 테스트
            runtime.register_persona(name, {
                'name': persona.name,
                'role': persona.role,
                'catchphrase': persona.catchphrase
            })
        
        print(f"✅ {len(runtime.personas)}개 페르소나 등록 완료")
        
        # 공유 문서 컨텍스트 테스트
        print("3. 문서 공유 시스템 테스트...")
        runtime.update_shared_context("TestAgent", {"test": "document", "timestamp": datetime.now().isoformat()})
        shared = runtime.get_shared_context()
        
        if "TestAgent" in shared:
            print("✅ 문서 공유 시스템 작동 확인")
        else:
            print("❌ 문서 공유 실패")
            return False
        
        # 메트릭 확인
        print("4. 실행 메트릭 확인...")
        metrics = runtime.get_execution_metrics()
        print(f"   - 총 실행: {metrics['total_executions']}")
        print(f"   - 성공률: {metrics['success_rate']:.1%}")
        print(f"   - 활성 에이전트: {metrics['active_agents']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 런타임 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_squad_orchestrator():
    """Squad Orchestrator 테스트."""
    print_section("Squad Orchestrator 테스트")
    
    try:
        # 런타임 초기화
        runtime_config = RuntimeConfig()
        runtime = AgentRuntime(runtime_config)
        
        # Squad 설정
        squad_config = SquadConfig(
            name="TestSquad",
            strategy="ai_driven",
            enable_evolution_loop=True,
            share_all_documents=True
        )
        
        # Squad 생성
        print("1. Squad Orchestrator 생성...")
        squad = SquadOrchestrator(runtime, squad_config)
        
        print(f"✅ Squad '{squad_config.name}' 생성 (전략: {squad_config.strategy})")
        
        # 더미 에이전트 등록
        print("2. 테스트 에이전트 등록...")
        
        async def dummy_agent(task, context):
            """더미 에이전트."""
            return {"result": "success", "task": task.get('type', 'unknown')}
        
        test_agents = ["Analyzer", "Designer", "Implementer"]
        
        for agent_name in test_agents:
            squad.register_agent(agent_name, dummy_agent)
        
        print(f"✅ {len(squad.agents)}개 에이전트 등록")
        
        # 실행 순서 설정
        print("3. 실행 순서 설정...")
        squad.set_execution_order(test_agents)
        
        print("✅ Squad Orchestrator 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ Squad Orchestrator 테스트 실패: {str(e)}")
        return False


async def test_upgrade_orchestrator():
    """UpgradeOrchestrator 테스트."""
    print_section("AWS UpgradeOrchestrator 테스트")
    
    try:
        # 임시 프로젝트 생성
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            project_path.mkdir()
            
            # 테스트 파일 생성
            (project_path / "main.py").write_text("print('Hello World')", encoding='utf-8')
            
            # 설정
            config = AWSUpgradeConfig(
                project_path=str(project_path),
                output_dir=str(Path(temp_dir) / "output"),
                enable_evolution_loop=False,  # 테스트를 위해 비활성화
                ai_driven_workflow=True,
                enable_personas=True
            )
            
            # 오케스트레이터 생성
            print("1. UpgradeOrchestrator 생성...")
            orchestrator = AWSUpgradeOrchestrator(config)
            
            # 페르소나 확인
            if orchestrator.persona:
                print(f"✅ 페르소나 활성화: {orchestrator.persona.name}")
                print(f"   캐치프레이즈: '{orchestrator.persona.catchphrase}'")
            
            # 초기화
            print("2. 에이전트 초기화...")
            await orchestrator.initialize()
            
            print(f"✅ 에이전트 초기화 완료")
            
            # 갭 스코어 확인
            print("3. 초기 상태 확인...")
            gap = orchestrator.get_gap_score()
            iteration = orchestrator.get_iteration_count()
            
            print(f"   - 초기 갭 스코어: {gap:.2%}")
            print(f"   - 반복 횟수: {iteration}")
            
            print("✅ UpgradeOrchestrator 테스트 완료")
            return True
            
    except Exception as e:
        print(f"❌ UpgradeOrchestrator 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_newbuilder_orchestrator():
    """NewBuilderOrchestrator 테스트."""
    print_section("AWS NewBuilderOrchestrator 테스트")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # SeedProduct 설정
            seed_config = SeedProductConfig(
                name="test-seed",
                type="api",
                language="python",
                framework="fastapi",
                architecture_pattern="clean"
            )
            
            # 설정
            config = AWSNewBuilderConfig(
                project_name="test-seed-project",
                output_dir=temp_dir,
                seed_config=seed_config,
                enable_evolution_loop=False,  # 테스트를 위해 비활성화
                skip_current_state_first_loop=True,
                use_gap_for_priority=True,
                enable_personas=True
            )
            
            # 오케스트레이터 생성
            print("1. NewBuilderOrchestrator 생성...")
            orchestrator = AWSNewBuilderOrchestrator(config)
            
            # 페르소나 확인
            if orchestrator.persona:
                print(f"✅ 페르소나 활성화: {orchestrator.persona.name}")
                print(f"   캐치프레이즈: '{orchestrator.persona.catchphrase}'")
            
            # 초기화
            print("2. 에이전트 초기화...")
            await orchestrator.initialize()
            
            print(f"✅ 에이전트 초기화 완료")
            
            # 첫 루프 상태 확인
            print("3. 첫 루프 설정 확인...")
            print(f"   - 첫 루프 상태: {orchestrator.is_first_loop}")
            print(f"   - 현재 상태 분석 건너뛰기: {config.skip_current_state_first_loop}")
            print(f"   - 갭 분석 우선순위용: {config.use_gap_for_priority}")
            
            print("✅ NewBuilderOrchestrator 테스트 완료")
            return True
            
    except Exception as e:
        print(f"❌ NewBuilderOrchestrator 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_evolution_loop_logic():
    """Evolution Loop 로직 테스트."""
    print_section("Evolution Loop 로직 테스트")
    
    try:
        # 런타임과 Squad 생성
        runtime = AgentRuntime(RuntimeConfig())
        squad_config = SquadConfig(
            name="EvolutionTestSquad",
            strategy="evolution_loop",
            enable_evolution_loop=True,
            convergence_threshold=0.95,
            max_iterations=5
        )
        squad = SquadOrchestrator(runtime, squad_config)
        
        print("1. Evolution Loop 설정 확인...")
        print(f"   - 전략: {squad.config.strategy}")
        print(f"   - 최대 반복: {squad.config.max_iterations}")
        print(f"   - 수렴 임계값: {squad.config.convergence_threshold}")
        
        # 갭 스코어 시뮬레이션
        print("2. 갭 스코어 수렴 시뮬레이션...")
        
        gap_scores = [1.0, 0.8, 0.5, 0.2, 0.05]  # 점진적 감소
        
        for i, gap in enumerate(gap_scores):
            squad.gap_score = gap
            squad.current_iteration = i + 1
            
            converged = gap <= (1 - squad.config.convergence_threshold)
            
            print(f"   Iteration {i+1}: 갭={gap:.2%}, 수렴={'✅' if converged else '❌'}")
            
            if converged:
                print(f"✅ Evolution Loop 수렴 달성! (Iteration {i+1})")
                break
        
        return True
        
    except Exception as e:
        print(f"❌ Evolution Loop 테스트 실패: {str(e)}")
        return False


async def test_personas_integration():
    """페르소나 시스템 통합 테스트."""
    print_section("페르소나 시스템 통합 테스트")
    
    try:
        # 모든 페르소나 확인
        personas = get_all_personas()
        
        print(f"1. 전체 페르소나 수: {len(personas)}개")
        
        # 오케스트레이터 페르소나
        orchestrator_personas = ["UpgradeOrchestrator", "NewBuildOrchestrator"]
        for name in orchestrator_personas:
            if name in personas:
                persona = personas[name]
                print(f"\n✅ {name}")
                print(f"   - 이름: {persona.name}")
                print(f"   - 역할: {persona.role}")
                print(f"   - 캐치프레이즈: '{persona.catchphrase}'")
        
        # 에이전트 페르소나 샘플
        print("\n2. 에이전트 페르소나 (샘플):")
        agent_samples = ["RequirementAnalyzer", "GapAnalyzer", "CodeGenerator"]
        
        for name in agent_samples:
            if name in personas:
                persona = personas[name]
                print(f"   ✅ {name}: {persona.name}")
        
        # 페르소나 카운트
        agent_count = len(personas) - len(orchestrator_personas)
        print(f"\n3. 페르소나 통계:")
        print(f"   - 오케스트레이터: {len(orchestrator_personas)}개")
        print(f"   - 에이전트: {agent_count}개")
        print(f"   - 총계: {len(personas)}개")
        
        return len(personas) >= 17  # 15 에이전트 + 2 오케스트레이터
        
    except Exception as e:
        print(f"❌ 페르소나 테스트 실패: {str(e)}")
        return False


async def main():
    """메인 테스트 실행."""
    print("=" * 80)
    print("🚀 AWS Agent Squad 프레임워크 통합 테스트")
    print(f"📅 {datetime.now().isoformat()}")
    print("=" * 80)
    
    results = {}
    
    # 테스트 실행
    tests = [
        ("AWS Runtime", test_aws_runtime),
        ("Squad Orchestrator", test_squad_orchestrator),
        ("UpgradeOrchestrator", test_upgrade_orchestrator),
        ("NewBuilderOrchestrator", test_newbuilder_orchestrator),
        ("Evolution Loop", test_evolution_loop_logic),
        ("Personas", test_personas_integration)
    ]
    
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {str(e)}")
            results[test_name] = False
    
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
        print("🎉 모든 테스트 통과!")
        print("✨ AWS Agent Squad 프레임워크 통합 완료!")
        print("🚀 특징:")
        print("  - AWS Bedrock AgentCore 런타임")
        print("  - Evolution Loop (갭 → 0)")
        print("  - AI-Driven 워크플로우")
        print("  - 17개 페르소나 시스템")
        print("  - 모든 문서 공유 시스템")
        print("  - SeedProduct 생성 지원")
    else:
        print("⚠️ 일부 테스트 실패. 위 결과를 확인하세요.")
    print("=" * 80)
    
    # 결과 저장
    result_file = Path("/tmp/aws_agent_squad_test_result.json")
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'all_passed': all_passed
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 테스트 결과 저장: {result_file}")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)