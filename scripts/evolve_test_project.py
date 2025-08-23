"""T-Developer-TEST 프로젝트 진화 실행 스크립트

T-Developer가 T-Developer-TEST를 타겟으로 품질을 30% 향상시키는 진화를 수행합니다.
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


async def evolve_test_project():
    """T-Developer-TEST 프로젝트 진화 실행"""
    
    print("🚀 T-Developer Evolution Engine Starting...")
    print("📁 Target: T-Developer-TEST")
    print("🎯 Goal: 30% Overall Quality Improvement")
    print("-" * 60)
    
    # 설정
    config = UpgradeConfig(
        project_path="/home/ec2-user/T-Developer-TEST",
        output_dir="/tmp/t-developer/evolution_reports",
        enable_dynamic_analysis=False,
        include_behavior_analysis=True,
        generate_impact_matrix=True,
        generate_recommendations=True,
        safe_mode=True,
        max_execution_time=1800,  # 30분
        parallel_analysis=True,
        
        # Evolution Loop 설정 - 핵심!
        enable_evolution_loop=True,  # Evolution Loop 활성화
        max_evolution_iterations=5,  # 최대 5회 반복
        auto_generate_agents=True,  # Agno를 통한 자동 에이전트 생성
        auto_implement_code=True,  # CodeGenerator를 통한 자동 코드 구현
        evolution_convergence_threshold=0.70  # 70% 개선 시 수렴으로 판단
    )
    
    # 요구사항
    requirements = """
    ## 품질 향상 목표 (30% 전반적 개선)
    
    1. **코드 품질 개선 (목표: 30% 향상)**
       - 복잡도 감소 (Cyclomatic Complexity 개선)
       - 코드 중복 제거
       - SOLID 원칙 적용
       - 더 나은 추상화 및 모듈화
    
    2. **테스트 커버리지 향상 (목표: 85% 이상)**
       - 단위 테스트 커버리지 85% 달성
       - 통합 테스트 강화
       - 엣지 케이스 테스트 추가
       - 실제 AI Provider 테스트 (Mock 없이)
    
    3. **문서화 개선 (목표: Docstring 커버리지 90%)**
       - 모든 public API에 docstring 추가
       - 파라미터, 반환값, 예외 명세
       - 사용 예제 포함
       - 한글 주석으로 복잡한 로직 설명
    
    4. **성능 최적화 (목표: 20% 속도 향상)**
       - 병렬 처리 최적화
       - 불필요한 AI 호출 감소
       - 캐싱 전략 구현
       - 메모리 사용량 최적화
    
    5. **보안 강화**
       - 입력 검증 강화
       - SQL 인젝션 방지
       - 환경 변수 안전 처리
       - 민감 정보 로깅 방지
    
    6. **에러 처리 개선**
       - 모든 예외 상황 처리
       - 명확한 에러 메시지
       - 적절한 롤백 메커니즘
       - Circuit Breaker 패턴 적용
    
    7. **아키텍처 개선**
       - 순환 의존성 제거
       - 레이어 분리 명확화
       - 인터페이스 정의 개선
       - 의존성 주입 패턴 적용
    
    ## 제약사항
    - 기존 API 호환성 유지
    - Mock/Fake 코드 사용 금지
    - 모든 변경사항은 테스트 필수
    - Evolution Loop를 통한 점진적 개선
    
    ## 성공 기준
    - 전체 품질 메트릭 30% 이상 개선
    - 모든 테스트 통과
    - 보안 취약점 0개
    - 성능 저하 없음
    """
    
    try:
        # 오케스트레이터 초기화
        orchestrator = UpgradeOrchestrator(config)
        await orchestrator.initialize()
        
        print("\n📊 Starting Analysis and Evolution...")
        print("This may take several minutes as the system:")
        print("  1. Analyzes current state")
        print("  2. Identifies gaps")
        print("  3. Designs improvements")
        print("  4. Implements changes")
        print("  5. Tests and validates")
        print("  6. Repeats until quality target is met")
        print()
        
        # 진화 실행
        report = await orchestrator.analyze(requirements)
        
        # 결과 저장
        report_path = Path(config.output_dir) / f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report.__dict__, f, default=str, indent=2)
        
        # 결과 출력
        print("\n" + "=" * 60)
        print("✅ EVOLUTION COMPLETE!")
        print("=" * 60)
        
        print(f"\n📈 Quality Metrics:")
        print(f"  - System Health: {report.system_health_score:.1f}/100")
        print(f"  - Upgrade Risk: {report.upgrade_risk_score:.1f}/100")
        print(f"  - Issues Found: {report.total_issues_found}")
        print(f"  - Critical Issues: {len(report.critical_issues)}")
        
        if hasattr(report, 'evolution_summary'):
            print(f"\n🔄 Evolution Summary:")
            print(f"  - Iterations: {report.evolution_summary.get('iterations', 0)}")
            print(f"  - Improvements Made: {report.evolution_summary.get('improvements_count', 0)}")
            print(f"  - Quality Improvement: {report.evolution_summary.get('quality_improvement', 0):.1f}%")
            print(f"  - Agents Created: {report.evolution_summary.get('agents_created', 0)}")
            print(f"  - Code Generated: {report.evolution_summary.get('code_generated_lines', 0)} lines")
        
        print(f"\n📄 Full report saved to: {report_path}")
        
        # 주요 개선사항 출력
        if report.immediate_actions:
            print("\n🎯 Immediate Actions Taken:")
            for action in report.immediate_actions[:5]:
                print(f"  • {action}")
        
        if report.short_term_goals:
            print("\n📋 Remaining Goals:")
            for goal in report.short_term_goals[:5]:
                print(f"  • {goal}")
        
        return report
        
    except Exception as e:
        print(f"\n❌ Evolution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """메인 실행 함수"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  T-Developer Self-Evolution                  ║
║                         Version 2.0.0                        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 확인 프롬프트
    print("⚠️  Warning: This will modify T-Developer-TEST project files!")
    print("The system will:")
    print("  • Analyze code quality")
    print("  • Generate improvement plans")
    print("  • Implement changes automatically")
    print("  • Run tests to validate changes")
    print()
    
    response = input("Do you want to proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Evolution cancelled.")
        return
    
    # 진화 실행
    report = await evolve_test_project()
    
    if report:
        print("\n✨ Evolution completed successfully!")
        print("Check the T-Developer-TEST folder for improvements.")
    else:
        print("\n⚠️  Evolution completed with issues. Please check logs.")


if __name__ == "__main__":
    asyncio.run(main())