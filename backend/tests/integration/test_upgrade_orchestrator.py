#!/usr/bin/env python3
"""UpgradeOrchestrator 통합 테스트 - 100% Real AI."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator, 
    UpgradeConfig
)


async def test_upgrade_orchestrator():
    """UpgradeOrchestrator 완전 통합 테스트."""
    print("="*80)
    print("🚀 T-Developer v2 UpgradeOrchestrator 테스트")
    print("   100% Real AI - NO MOCKS!")
    print("="*80)
    
    # 설정
    config = UpgradeConfig(
        project_path=str(Path.cwd()),
        output_dir="reports",
        enable_dynamic_analysis=False,
        include_behavior_analysis=True,
        generate_impact_matrix=True,
        generate_recommendations=True,
        safe_mode=True,
        max_execution_time=600,
        parallel_analysis=True
    )
    
    print("\n📋 설정:")
    print(f"   - 프로젝트 경로: {config.project_path}")
    print(f"   - 출력 디렉토리: {config.output_dir}")
    print(f"   - 병렬 분석: {config.parallel_analysis}")
    print(f"   - 최대 실행 시간: {config.max_execution_time}초")
    
    # 오케스트레이터 생성 및 초기화
    print("\n🔧 오케스트레이터 초기화...")
    orchestrator = UpgradeOrchestrator(config)
    await orchestrator.initialize()
    print("✅ 초기화 완료")
    
    # 테스트 요구사항
    requirements = """
    Analyze and upgrade the T-Developer v2 system:
    
    1. Complete system analysis:
       - Code quality assessment
       - Architecture review
       - Security vulnerability scan
       - Performance analysis
       - Test coverage evaluation
    
    2. Generate upgrade recommendations:
       - Identify improvement areas
       - Suggest refactoring opportunities
       - Propose new features
       - Recommend best practices
    
    3. Create comprehensive documentation:
       - System architecture diagram
       - API documentation
       - Deployment guide
       - User manual
    
    Focus on:
    - AI-driven automation
    - Self-improvement capabilities
    - Safety mechanisms
    - Quality gates
    """
    
    print("\n📝 요구사항:")
    print(requirements[:200] + "...")
    
    print("\n" + "="*80)
    print("🔄 분석 시작...")
    print("="*80)
    
    start_time = datetime.now()
    
    try:
        # 분석 실행
        report = await orchestrator.analyze(requirements, include_research=True)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "="*80)
        print("✅ 분석 완료!")
        print("="*80)
        
        # 결과 요약
        print(f"\n📊 분석 결과:")
        print(f"   - 실행 시간: {execution_time:.2f}초")
        print(f"   - 완료된 단계: {report.phases_completed}개")
        print(f"   - 실패한 단계: {report.phases_failed}개")
        print(f"   - 시스템 건강도: {report.system_health_score:.2f}/100")
        print(f"   - 업그레이드 위험도: {report.upgrade_risk_score:.2f}/100")
        print(f"   - 발견된 이슈: {report.total_issues_found}개")
        
        # 세부 결과
        if report.requirement_analysis:
            print(f"\n   [RequirementAnalyzer]")
            spec = report.requirement_analysis.get('specification', {})
            print(f"   - 기능 요구사항: {len(spec.get('functional_requirements', []))}개")
            print(f"   - 비기능 요구사항: {len(spec.get('non_functional_requirements', []))}개")
        
        if report.static_analysis:
            print(f"\n   [StaticAnalyzer]")
            print(f"   - 분석된 파일: {report.static_analysis.get('total_files', 0)}개")
            print(f"   - 코드 라인: {report.static_analysis.get('total_lines', 0)}")
            print(f"   - 복잡도 핫스팟: {report.static_analysis.get('complexity_hotspots', 0)}개")
        
        if report.code_analysis:
            print(f"\n   [CodeAnalysisAgent]")
            analysis = report.code_analysis.get('analysis', {})
            if analysis:
                print(f"   - AI 분석 완료")
        
        if report.gap_analysis:
            print(f"\n   [GapAnalyzer]")
            gaps = report.gap_analysis.get('gaps', [])
            print(f"   - 식별된 갭: {len(gaps)}개")
        
        if report.quality_metrics:
            print(f"\n   [QualityGate]")
            print(f"   - 품질 통과: {'✅' if report.quality_metrics.get('passed', False) else '❌'}")
        
        # 권장사항
        if report.immediate_actions:
            print(f"\n💡 즉시 조치사항:")
            for action in report.immediate_actions[:3]:
                print(f"   - {action}")
        
        if report.short_term_goals:
            print(f"\n🎯 단기 목표:")
            for goal in report.short_term_goals[:3]:
                print(f"   - {goal}")
        
        if report.long_term_goals:
            print(f"\n🚀 장기 목표:")
            for goal in report.long_term_goals[:3]:
                print(f"   - {goal}")
        
        # 태스크 분석
        if report.tasks_breakdown:
            print(f"\n📋 태스크 분석:")
            print(f"   - 총 태스크: {len(report.tasks_breakdown)}개")
            for task in report.tasks_breakdown[:3]:
                print(f"   - {task.get('name', 'N/A')} ({task.get('duration', 'N/A')}분)")
        
        # 보고서 저장
        report_path = await orchestrator.save_report(report)
        if report_path:
            print(f"\n📁 보고서 저장됨: {report_path}")
        
        # JSON으로도 저장
        json_path = Path("reports") / f"upgrade_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_path.parent.mkdir(exist_ok=True)
        
        # Convert report to dict (handle dataclass)
        report_dict = {
            "timestamp": report.timestamp,
            "project_path": report.project_path,
            "system_health_score": report.system_health_score,
            "upgrade_risk_score": report.upgrade_risk_score,
            "total_issues_found": report.total_issues_found,
            "phases_completed": report.phases_completed,
            "phases_failed": report.phases_failed,
            "execution_time": execution_time,
            "immediate_actions": report.immediate_actions,
            "short_term_goals": report.short_term_goals,
            "long_term_goals": report.long_term_goals
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        print(f"📁 JSON 보고서: {json_path.absolute()}")
        
        print("\n" + "="*80)
        print("🎉 테스트 완료!")
        print("="*80)
        
        return report
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        # 정리
        if orchestrator.memory_hub:
            await orchestrator.memory_hub.shutdown()
        print("\n메모리 허브 종료 완료")


if __name__ == "__main__":
    import os
    
    # AWS 환경 변수 설정
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    print("🔧 환경 설정:")
    print(f"   - AWS Region: {os.environ.get('AWS_DEFAULT_REGION')}")
    print(f"   - Python: {sys.version.split()[0]}")
    
    # 테스트 실행
    asyncio.run(test_upgrade_orchestrator())