#!/usr/bin/env python3
"""UpgradeOrchestrator 전체 통합 테스트 - 완전한 워크플로우 검증."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator, 
    UpgradeConfig
)


async def test_full_orchestrator():
    """전체 오케스트레이터 통합 테스트."""
    print("="*80)
    print("🚀 UpgradeOrchestrator 전체 통합 테스트")
    print("="*80)
    
    # 테스트 프로젝트 설정
    project_path = Path("/home/ec2-user/T-Developer-v2")
    
    # 업그레이드 설정
    config = UpgradeConfig(
        project_path=str(project_path),
        output_dir="test_outputs/orchestrator_reports",
        enable_dynamic_analysis=False,  # 안전을 위해 비활성화
        include_behavior_analysis=True,
        generate_impact_matrix=True,
        generate_recommendations=True,
        safe_mode=True,
        max_execution_time=300,  # 5분 제한
        parallel_analysis=True
    )
    
    print("\n📋 테스트 설정:")
    print(f"   • 프로젝트: {config.project_name}")
    print(f"   • 경로: {config.project_path}")
    print(f"   • 버전: {config.target_version}")
    print(f"   • 타입: {config.upgrade_type}")
    print(f"   • 안전 검사: {config.safety_checks}")
    print(f"   • 백업: {config.backup_enabled}")
    print(f"   • Dry Run: {config.dry_run}")
    print(f"   • 타임아웃: {config.timeout_seconds}초")
    
    # 오케스트레이터 생성
    print("\n🔧 오케스트레이터 초기화...")
    orchestrator = UpgradeOrchestrator(config)
    
    # 초기화
    print("📦 시스템 초기화...")
    await orchestrator.initialize()
    
    # 전체 업그레이드 실행
    print("\n" + "="*80)
    print("🚀 업그레이드 프로세스 시작")
    print("="*80)
    
    try:
        # 타임스탬프
        start_time = datetime.now()
        print(f"\n⏰ 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 업그레이드 실행
        print("\n단계별 진행 상황:")
        print("-"*50)
        
        result = await orchestrator.execute_upgrade()
        
        # 종료 시간
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*80)
        print("📊 실행 결과")
        print("="*80)
        
        if result:
            print(f"\n✅ 업그레이드 성공!")
            print(f"   • 소요 시간: {duration:.1f}초")
            print(f"   • 상태: {result.status}")
            print(f"   • 단계: {result.phase}")
            
            # 상세 결과
            if result.reports:
                print(f"\n📝 생성된 보고서: {len(result.reports)}개")
                for report_name, report_path in result.reports.items():
                    print(f"   • {report_name}: {report_path}")
            
            if result.artifacts:
                print(f"\n📦 생성된 아티팩트: {len(result.artifacts)}개")
                for artifact_name, artifact_info in result.artifacts.items():
                    print(f"   • {artifact_name}: {artifact_info}")
            
            if result.metrics:
                print(f"\n📈 메트릭:")
                for metric_name, metric_value in result.metrics.items():
                    print(f"   • {metric_name}: {metric_value}")
            
            if result.validation_results:
                print(f"\n✔️ 검증 결과:")
                for check_name, check_result in result.validation_results.items():
                    status = "✅" if check_result else "❌"
                    print(f"   {status} {check_name}: {check_result}")
            
            # 결과 저장
            output_dir = Path("test_outputs")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"full_orchestrator_result_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "config": {
                        "project_name": config.project_name,
                        "project_path": config.project_path,
                        "target_version": config.target_version,
                        "upgrade_type": config.upgrade_type
                    },
                    "result": {
                        "status": result.status,
                        "phase": result.phase,
                        "success": result.success,
                        "reports": result.reports,
                        "artifacts": result.artifacts,
                        "metrics": result.metrics,
                        "validation_results": result.validation_results,
                        "errors": result.errors,
                        "warnings": result.warnings
                    },
                    "execution": {
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "duration_seconds": duration
                    }
                }, f, indent=2, default=str)
            
            print(f"\n💾 전체 결과 저장: {output_file.absolute()}")
            
        else:
            print(f"\n❌ 업그레이드 실패")
            print(f"   • 소요 시간: {duration:.1f}초")
        
    except asyncio.TimeoutError:
        print("\n⏱️ 타임아웃 발생 (10분 초과)")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        print(traceback.format_exc())
    
    finally:
        # 정리
        print("\n🧹 시스템 정리...")
        await orchestrator.shutdown()
        
        print("\n" + "="*80)
        print("✅ 전체 통합 테스트 완료!")
        print("="*80)


async def monitor_progress(orchestrator: UpgradeOrchestrator):
    """진행 상황 모니터링 (별도 태스크)."""
    while True:
        await asyncio.sleep(5)  # 5초마다 체크
        # 여기에 진행 상황 체크 로직 추가 가능
        print(".", end="", flush=True)


if __name__ == "__main__":
    import os
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    print("🔧 환경 설정:")
    print(f"   - AWS Region: {os.environ.get('AWS_DEFAULT_REGION')}")
    print(f"   - Python: {sys.version.split()[0]}")
    print(f"   - Working Dir: {os.getcwd()}")
    print()
    
    # 이벤트 루프 실행
    try:
        asyncio.run(test_full_orchestrator())
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n\n❌ 치명적 오류: {e}")
        import traceback
        traceback.print_exc()