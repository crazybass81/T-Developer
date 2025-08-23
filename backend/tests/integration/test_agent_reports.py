#!/usr/bin/env python3
"""각 에이전트의 자체 보고서 생성 테스트."""

import asyncio
import sys
from pathlib import Path

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from backend.packages.agents.requirement_analyzer import RequirementAnalyzer
from backend.packages.agents.planner_agent import PlannerAgent
from backend.packages.agents.base import AgentTask
from backend.packages.memory.hub import MemoryHub


async def test_agent_self_reports():
    """각 에이전트가 자체 보고서를 생성하는지 테스트."""
    print("="*80)
    print("🔍 에이전트 자체 보고서 생성 테스트")
    print("="*80)
    
    # 메모리 허브 초기화
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    # 1. RequirementAnalyzer 테스트
    print("\n📋 RequirementAnalyzer 테스트")
    print("-"*50)
    
    req_analyzer = RequirementAnalyzer(memory_hub=memory_hub)
    
    task = AgentTask(
        intent="analyze_requirement",
        inputs={
            "requirements": "Build a REST API with FastAPI including JWT authentication"
        }
    )
    
    # 분석 실행
    result = await req_analyzer.execute(task)
    print(f"분석 결과: {result.success}")
    
    # 자체 보고서 생성
    if result.success:
        report = await req_analyzer.generate_report(result, "markdown")
        print(f"✅ 보고서 생성: {report['path']}")
        
        # JSON 포맷도 테스트
        json_report = await req_analyzer.generate_report(result, "json")
        print(f"✅ JSON 보고서: {json_report['path']}")
    
    # 2. PlannerAgent 테스트
    print("\n📅 PlannerAgent 테스트")
    print("-"*50)
    
    planner = PlannerAgent(memory_hub=memory_hub)
    
    plan_task = AgentTask(
        intent="create_plan",
        inputs={
            "requirement": "Build a REST API with FastAPI",
            "context": {"project_type": "api"}
        }
    )
    
    # 계획 생성
    plan_result = await planner.execute(plan_task)
    print(f"계획 생성: {plan_result.success}")
    
    # 자체 보고서 생성
    if plan_result.success:
        plan_report = await planner.generate_report(plan_result, "markdown")
        print(f"✅ 계획 보고서: {plan_report['path']}")
        
        # HTML 포맷도 테스트
        html_report = await planner.generate_report(plan_result, "html")
        print(f"✅ HTML 보고서: {html_report['path']}")
    
    # 생성된 보고서 목록 확인
    print("\n" + "="*80)
    print("📁 생성된 보고서 목록:")
    print("-"*50)
    
    reports_dir = Path("reports")
    if reports_dir.exists():
        for agent_dir in reports_dir.iterdir():
            if agent_dir.is_dir():
                print(f"\n{agent_dir.name}:")
                for report_dir in sorted(agent_dir.iterdir())[-3:]:  # 최근 3개만
                    if report_dir.is_dir():
                        for report_file in report_dir.iterdir():
                            print(f"  - {report_file.name}")
    
    # 정리
    await memory_hub.shutdown()
    print("\n✅ 테스트 완료!")


if __name__ == "__main__":
    import os
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    print("🔧 환경 설정:")
    print(f"   - AWS Region: {os.environ.get('AWS_DEFAULT_REGION')}")
    print(f"   - Python: {sys.version.split()[0]}")
    print()
    
    asyncio.run(test_agent_self_reports())