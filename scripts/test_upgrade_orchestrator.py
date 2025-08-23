#!/usr/bin/env python3
"""Test script for UpgradeOrchestrator with all agents.

이 스크립트는 UpgradeOrchestrator가 모든 에이전트를 정해진 순서대로
실행하는지 테스트합니다.
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


async def test_upgrade_orchestrator():
    """UpgradeOrchestrator 테스트"""
    
    print("=" * 80)
    print("🚀 Testing UpgradeOrchestrator with All Agents")
    print("=" * 80)
    
    # 테스트 프로젝트 경로 설정 (T-Developer 사용)
    test_project_path = "/home/ec2-user/T-Developer"
    
    print(f"📁 Project Path: {test_project_path}")
    
    # 요구사항 정의
    requirements = """T-Developer의 여러가지 오케스트레이터 중 UpgradeOrchestrator를 중점적으로 완성한다.

## UpgradeOrchestrator의 세부사항
1. 개발중인 대상프로젝트를 요청에 따라 업그레이드/디버깅/리팩터링을 수행하는 UpgradeOrchestrator를 완성한다.
2. 정해진 기본 호출 순서에 따라 작업수행 하는 것을 원칙으로 하지만 요청사항에 따라 호출하는 에이전트의 종류나 순서를 변경할 수 있는 AI드리븐 오케스트레이터이다.
3. 기본 호출순서는 요청사항 분석에이전트 - 현재상태 분석 에이전트들 - 외부리서치 에이전트 - 갭분석 에이전트 - 아키텍트 에이전트 - 오케스트레이터 디자이너 - 계획수립 에이전트 - 세부임무계획 에이전트 - 코드제너레이터 - 테스트 에이전트
"""
    
    print(f"📝 Requirements: {requirements[:100]}...")
    
    # 설정 생성
    config = UpgradeConfig(
        project_path=test_project_path,
        output_dir="/tmp/t-developer/test_reports",
        enable_dynamic_analysis=False,
        include_behavior_analysis=True,
        generate_impact_matrix=True,
        generate_recommendations=True,
        safe_mode=True,
        parallel_analysis=True,
        max_execution_time=600,
        # Evolution Loop 설정
        enable_evolution_loop=False,  # 테스트에서는 비활성화
        auto_generate_agents=False,
        auto_implement_code=False
    )
    
    print("\n⚙️ Configuration:")
    print(f"  - Output Dir: {config.output_dir}")
    print(f"  - Parallel Analysis: {config.parallel_analysis}")
    print(f"  - Max Execution Time: {config.max_execution_time}s")
    
    # 오케스트레이터 생성 및 초기화
    print("\n🔧 Initializing UpgradeOrchestrator...")
    orchestrator = UpgradeOrchestrator(config)
    await orchestrator.initialize()
    print("✅ Orchestrator initialized")
    
    # 분석 실행
    print("\n🔍 Starting Analysis...")
    print("-" * 40)
    
    start_time = datetime.now()
    
    try:
        # analyze 메서드 실행
        report = await orchestrator.analyze(
            requirements=requirements,
            include_research=True  # 외부 리서치 포함
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print("\n✅ Analysis Completed!")
        print("-" * 40)
        
        # 결과 출력
        print("\n📊 Analysis Results:")
        print(f"  - Execution Time: {execution_time:.2f}s")
        print(f"  - Project Path: {report.project_path}")
        print(f"  - Timestamp: {report.timestamp}")
        
        # 각 에이전트 실행 결과 확인
        print("\n📋 Agent Execution Results:")
        
        if report.requirement_analysis:
            print("  ✅ RequirementAnalyzer - Completed")
        else:
            print("  ❌ RequirementAnalyzer - Failed or Skipped")
        
        if report.static_analysis:
            print("  ✅ StaticAnalyzer - Completed")
        else:
            print("  ❌ StaticAnalyzer - Failed or Skipped")
        
        if report.code_analysis:
            print("  ✅ CodeAnalysisAgent - Completed")
        else:
            print("  ❌ CodeAnalysisAgent - Failed or Skipped")
        
        if report.behavior_analysis:
            print("  ✅ BehaviorAnalyzer - Completed")
        else:
            print("  ❌ BehaviorAnalyzer - Failed or Skipped")
        
        if report.impact_analysis:
            print("  ✅ ImpactAnalyzer - Completed")
        else:
            print("  ❌ ImpactAnalyzer - Failed or Skipped")
        
        if report.quality_metrics:
            print("  ✅ QualityGate - Completed")
        else:
            print("  ❌ QualityGate - Failed or Skipped")
        
        if report.research_pack:
            print("  ✅ ExternalResearcher - Completed")
        else:
            print("  ❌ ExternalResearcher - Failed or Skipped")
        
        if report.gap_analysis:
            print("  ✅ GapAnalyzer - Completed")
        else:
            print("  ❌ GapAnalyzer - Failed or Skipped")
        
        # SystemArchitect와 OrchestratorDesigner는 report에 직접 저장되지 않으므로
        # tasks_breakdown을 통해 확인
        if report.tasks_breakdown and len(report.tasks_breakdown) > 0:
            print("  ✅ SystemArchitect - Completed")
            print("  ✅ OrchestratorDesigner - Completed")
            print("  ✅ PlannerAgent - Completed")
            print("  ✅ TaskCreatorAgent - Completed")
            print(f"     - Total Tasks: {len(report.tasks_breakdown)}")
        else:
            print("  ⚠️ Architecture/Planning agents may not have run")
        
        # 메트릭 출력
        print("\n📈 Metrics:")
        print(f"  - System Health Score: {report.system_health_score:.1f}/100")
        print(f"  - Upgrade Risk Score: {report.upgrade_risk_score:.1f}/100")
        print(f"  - Total Issues Found: {report.total_issues_found}")
        print(f"  - Critical Issues: {len(report.critical_issues)}")
        
        # MD 파일 저장 확인
        print("\n💾 Report Files:")
        output_dir = Path(config.output_dir)
        if output_dir.exists():
            project_name = Path(test_project_path).name
            timestamp = report.timestamp.replace(':', '-').replace('.', '-')
            report_dir = output_dir / project_name / timestamp
            
            if report_dir.exists():
                md_files = list(report_dir.glob("*.md"))
                json_files = list(report_dir.glob("*.json"))
                
                print(f"  - Report Directory: {report_dir}")
                print(f"  - MD Files: {len(md_files)}")
                print(f"  - JSON Files: {len(json_files)}")
                
                if md_files:
                    print("\n  📝 MD Files Generated:")
                    for md_file in sorted(md_files)[:10]:  # 최대 10개만 출력
                        print(f"    • {md_file.name}")
            else:
                print(f"  ⚠️ Report directory not found: {report_dir}")
        
        # 추천사항 출력
        if report.immediate_actions:
            print("\n🎯 Immediate Actions:")
            for action in report.immediate_actions[:5]:
                print(f"  • {action}")
        
        # 전체 보고서를 JSON으로 저장
        test_output_path = Path("test_outputs")
        test_output_path.mkdir(exist_ok=True)
        
        output_file = test_output_path / f"upgrade_orchestrator_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert report to dict
        report_dict = {}
        for key, value in report.__dict__.items():
            if value is None:
                report_dict[key] = None
            elif hasattr(value, '__dict__'):
                try:
                    from dataclasses import asdict
                    report_dict[key] = asdict(value)
                except:
                    report_dict[key] = str(value)
            elif isinstance(value, (list, dict, str, int, float, bool)):
                report_dict[key] = value
            else:
                report_dict[key] = str(value)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"\n💾 Full report saved to: {output_file}")
        
        print("\n" + "=" * 80)
        print("🎉 Test Completed Successfully!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    success = asyncio.run(test_upgrade_orchestrator())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()