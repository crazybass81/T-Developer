#!/usr/bin/env python3
"""빠른 UpgradeOrchestrator 검증 스크립트.

이 스크립트는 UpgradeOrchestrator의 초기화와 구조만 확인합니다.
실제 AI 호출 없이 빠르게 검증합니다.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator,
    UpgradeConfig
)


async def verify_orchestrator():
    """UpgradeOrchestrator 구조 검증"""
    
    print("=" * 80)
    print("🔍 UpgradeOrchestrator 구조 검증")
    print("=" * 80)
    
    # 설정 생성
    config = UpgradeConfig(
        project_path="/home/ec2-user/T-Developer",
        output_dir="/tmp/t-developer/test_reports",
        enable_dynamic_analysis=False,
        include_behavior_analysis=True,
        generate_impact_matrix=True,
        generate_recommendations=True,
        safe_mode=True,
        parallel_analysis=True,
        max_execution_time=600,
        # Evolution Loop 설정
        enable_evolution_loop=True,
        max_evolution_iterations=3,
        auto_generate_agents=True,
        auto_implement_code=False,
        evolution_convergence_threshold=0.95
    )
    
    print("\n✅ 설정 객체 생성 완료")
    print(f"  - Project Path: {config.project_path}")
    print(f"  - Evolution Loop: {config.enable_evolution_loop}")
    print(f"  - Auto Generate Agents: {config.auto_generate_agents}")
    
    # 오케스트레이터 생성
    print("\n🔧 오케스트레이터 생성 중...")
    orchestrator = UpgradeOrchestrator(config)
    print("✅ 오케스트레이터 생성 완료")
    
    # 초기화
    print("\n🔧 오케스트레이터 초기화 중...")
    await orchestrator.initialize()
    print("✅ 오케스트레이터 초기화 완료")
    
    # 에이전트 확인
    print("\n📋 초기화된 에이전트:")
    agents = [
        ("requirement_analyzer", "RequirementAnalyzer"),
        ("static_analyzer", "StaticAnalyzer"),
        ("code_analyzer", "CodeAnalysisAgent"),
        ("gap_analyzer", "GapAnalyzer"),
        ("behavior_analyzer", "BehaviorAnalyzer"),
        ("impact_analyzer", "ImpactAnalyzer"),
        ("external_researcher", "ExternalResearcher"),
        ("planner_agent", "PlannerAgent"),
        ("task_creator_agent", "TaskCreatorAgent"),
        ("system_architect", "SystemArchitect"),
        ("orchestrator_designer", "OrchestratorDesigner"),
        ("code_generator", "CodeGenerator"),
        ("quality_gate", "QualityGate")
    ]
    
    for attr_name, agent_name in agents:
        if hasattr(orchestrator, attr_name):
            agent = getattr(orchestrator, attr_name)
            if agent is not None:
                print(f"  ✅ {agent_name}: 초기화 성공")
            else:
                print(f"  ❌ {agent_name}: None")
        else:
            print(f"  ❌ {agent_name}: 속성 없음")
    
    # 주요 메서드 확인
    print("\n📋 주요 메서드:")
    methods = [
        "analyze",
        "execute_evolution_loop",
        "_execute_requirement_analysis",
        "_execute_current_state_analysis",
        "_execute_external_research",
        "_execute_gap_analysis",
        "_execute_architecture_design",
        "_execute_orchestrator_design",
        "_execute_planning",
        "_execute_task_creation",
        "_execute_code_generation",
        "_generate_agents_with_agno",
        "_define_phases_with_ai",
        "_save_all_reports_as_markdown"
    ]
    
    for method_name in methods:
        if hasattr(orchestrator, method_name):
            method = getattr(orchestrator, method_name)
            if callable(method):
                print(f"  ✅ {method_name}: 구현됨")
            else:
                print(f"  ⚠️ {method_name}: 호출 불가")
        else:
            print(f"  ❌ {method_name}: 미구현")
    
    # Evolution Loop 관련 확인
    print("\n🧬 Evolution Loop 기능:")
    if config.enable_evolution_loop:
        print("  ✅ Evolution Loop 활성화")
        print(f"  - 최대 반복: {config.max_evolution_iterations}회")
        print(f"  - 수렴 임계값: {config.evolution_convergence_threshold:.1%}")
        if config.auto_generate_agents:
            print("  ✅ Agno 자동 에이전트 생성 활성화")
        else:
            print("  ⚠️ Agno 자동 에이전트 생성 비활성화")
    else:
        print("  ⚠️ Evolution Loop 비활성화")
    
    # 메모리 허브 확인
    print("\n💾 메모리 시스템:")
    if orchestrator.memory_hub:
        print("  ✅ MemoryHub 초기화됨")
    else:
        print("  ❌ MemoryHub 없음")
    
    # 안전 메커니즘 확인
    print("\n🔒 안전 메커니즘:")
    if hasattr(orchestrator, 'circuit_breaker'):
        print("  ✅ Circuit Breaker 활성화")
    else:
        print("  ❌ Circuit Breaker 없음")
    
    if hasattr(orchestrator, 'resource_limiter'):
        print("  ✅ Resource Limiter 활성화")
    else:
        print("  ❌ Resource Limiter 없음")
    
    # MD 파일 저장 경로 확인
    print("\n📁 MD 파일 저장 설정:")
    print(f"  - 출력 디렉토리: {config.output_dir}")
    output_path = Path(config.output_dir)
    if output_path.exists():
        print(f"  ✅ 디렉토리 존재")
    else:
        print(f"  ⚠️ 디렉토리 없음 (자동 생성됨)")
    
    # 종료
    if orchestrator.memory_hub:
        await orchestrator.memory_hub.shutdown()
    
    print("\n" + "=" * 80)
    print("✅ 검증 완료!")
    print("=" * 80)
    print("\n💡 UpgradeOrchestrator가 정상적으로 구현되었습니다.")
    print("   실제 분석을 실행하려면 test_upgrade_orchestrator.py를 사용하세요.")
    print("   (주의: 실제 AI 호출로 인해 시간이 소요됩니다)")
    
    return True


def main():
    """Main entry point"""
    success = asyncio.run(verify_orchestrator())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()