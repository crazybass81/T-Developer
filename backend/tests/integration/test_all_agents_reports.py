#!/usr/bin/env python3
"""모든 에이전트의 보고서 생성 통합 테스트."""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from backend.packages.agents.base import AgentTask
from backend.packages.memory.hub import MemoryHub

# 모든 에이전트 import
from backend.packages.agents.requirement_analyzer import RequirementAnalyzer
from backend.packages.agents.code_analysis import CodeAnalysisAgent  
from backend.packages.agents.external_researcher import ExternalResearcher
from backend.packages.agents.static_analyzer import StaticAnalyzer
from backend.packages.agents.behavior_analyzer import BehaviorAnalyzer
from backend.packages.agents.gap_analyzer import GapAnalyzer
from backend.packages.agents.impact_analyzer import ImpactAnalyzer
from backend.packages.agents.planner_agent import PlannerAgent
from backend.packages.agents.task_creator_agent import TaskCreatorAgent


async def test_agent_report(agent_class, agent_name: str, task: AgentTask, memory_hub: MemoryHub) -> Dict[str, Any]:
    """개별 에이전트의 보고서 생성 테스트."""
    print(f"\n📋 {agent_name} 테스트")
    print("-"*50)
    
    try:
        # 에이전트 생성
        agent = agent_class(memory_hub=memory_hub)
        
        # 분석 실행
        print(f"🔄 분석 실행 중...")
        result = await agent.execute(task)
        print(f"   - 분석 결과: {'✅ 성공' if result.success else '❌ 실패'}")
        
        if result.success:
            # 보고서 생성 (3가지 포맷)
            reports = {}
            
            # Markdown 보고서
            md_report = await agent.generate_report(result, "markdown")
            reports['markdown'] = md_report
            print(f"   - MD 보고서: {md_report['path']}")
            
            # JSON 보고서
            json_report = await agent.generate_report(result, "json")
            reports['json'] = json_report
            print(f"   - JSON 보고서: {json_report['path']}")
            
            # HTML 보고서 (선택적)
            if agent_name in ['RequirementAnalyzer', 'CodeAnalysisAgent', 'ExternalResearcher']:
                html_report = await agent.generate_report(result, "html")
                reports['html'] = html_report
                print(f"   - HTML 보고서: {html_report['path']}")
            
            # 메모리 키 확인
            if md_report.get('memory_key'):
                print(f"   - 메모리 저장: {md_report['memory_key']}")
            
            return {
                "agent": agent_name,
                "success": True,
                "reports": reports,
                "data_summary": {
                    "keys": list(result.data.keys()) if result.data else [],
                    "size": len(str(result.data)) if result.data else 0
                }
            }
        else:
            print(f"   ⚠️ 분석 실패: {result.error}")
            return {
                "agent": agent_name,
                "success": False,
                "error": result.error
            }
            
    except Exception as e:
        print(f"   ❌ 에러: {e}")
        return {
            "agent": agent_name,
            "success": False,
            "error": str(e)
        }


async def test_all_agents():
    """모든 에이전트의 보고서 생성 테스트."""
    print("="*80)
    print("🔍 전체 에이전트 보고서 생성 통합 테스트")
    print("="*80)
    
    # 메모리 허브 초기화
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    # 테스트 결과 저장
    test_results = []
    
    # 1. RequirementAnalyzer
    task = AgentTask(
        intent="analyze_requirement",
        inputs={
            "requirements": "Build a scalable REST API with FastAPI including authentication, caching, and monitoring"
        }
    )
    result = await test_agent_report(RequirementAnalyzer, "RequirementAnalyzer", task, memory_hub)
    test_results.append(result)
    
    # 2. CodeAnalysisAgent
    task = AgentTask(
        intent="analyze_code",
        inputs={
            "project_path": "/home/ec2-user/T-Developer-v2",
            "focus_areas": ["complexity", "patterns", "dependencies"]
        }
    )
    result = await test_agent_report(CodeAnalysisAgent, "CodeAnalysisAgent", task, memory_hub)
    test_results.append(result)
    
    # 3. ExternalResearcher
    task = AgentTask(
        intent="research",
        inputs={
            "topic": "FastAPI best practices and performance optimization",
            "depth": "comprehensive"
        }
    )
    result = await test_agent_report(ExternalResearcher, "ExternalResearcher", task, memory_hub)
    test_results.append(result)
    
    # 4. StaticAnalyzer
    task = AgentTask(
        intent="analyze_static",
        inputs={
            "project_path": "/home/ec2-user/T-Developer-v2",
            "check_security": True,
            "check_complexity": True
        }
    )
    result = await test_agent_report(StaticAnalyzer, "StaticAnalyzer", task, memory_hub)
    test_results.append(result)
    
    # 5. BehaviorAnalyzer
    task = AgentTask(
        intent="analyze_behavior",
        inputs={
            "project_path": "/home/ec2-user/T-Developer-v2",
            "analyze_patterns": True
        }
    )
    result = await test_agent_report(BehaviorAnalyzer, "BehaviorAnalyzer", task, memory_hub)
    test_results.append(result)
    
    # 6. GapAnalyzer
    task = AgentTask(
        intent="analyze_gaps",
        inputs={
            "current_state": {"coverage": 50, "complexity": 15},
            "target_state": {"coverage": 80, "complexity": 10},
            "project_path": "/home/ec2-user/T-Developer-v2"
        }
    )
    result = await test_agent_report(GapAnalyzer, "GapAnalyzer", task, memory_hub)
    test_results.append(result)
    
    # 7. ImpactAnalyzer
    task = AgentTask(
        intent="analyze_impact",
        inputs={
            "project_path": "/home/ec2-user/T-Developer-v2",
            "proposed_changes": [
                {"type": "feature", "description": "Add caching layer"},
                {"type": "refactor", "description": "Optimize database queries"}
            ]
        }
    )
    result = await test_agent_report(ImpactAnalyzer, "ImpactAnalyzer", task, memory_hub)
    test_results.append(result)
    
    # 8. PlannerAgent
    task = AgentTask(
        intent="create_plan",
        inputs={
            "requirement": "Build scalable API with authentication",
            "context": {"project_type": "api", "timeline": "4 weeks"}
        }
    )
    result = await test_agent_report(PlannerAgent, "PlannerAgent", task, memory_hub)
    test_results.append(result)
    
    # 9. TaskCreatorAgent
    plan = {
        "phases": [
            {"name": "Setup", "duration_hours": 8},
            {"name": "Development", "duration_hours": 40}
        ],
        "tasks": [
            {
                "id": "task_001",
                "name": "Setup project",
                "agent": "orchestrator",
                "duration_minutes": 120
            }
        ]
    }
    task = AgentTask(
        intent="create_tasks",
        inputs={
            "plan": plan,
            "requirement": "Build API"
        }
    )
    result = await test_agent_report(TaskCreatorAgent, "TaskCreatorAgent", task, memory_hub)
    test_results.append(result)
    
    # 결과 요약
    print("\n" + "="*80)
    print("📊 테스트 결과 요약")
    print("="*80)
    
    success_count = sum(1 for r in test_results if r['success'])
    total_count = len(test_results)
    
    print(f"\n전체: {success_count}/{total_count} 성공")
    print("\n상세 결과:")
    for result in test_results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['agent']}")
        if result['success'] and 'reports' in result:
            formats = list(result['reports'].keys())
            print(f"      - 생성된 포맷: {', '.join(formats)}")
            if 'data_summary' in result:
                print(f"      - 데이터 키: {', '.join(result['data_summary']['keys'][:3])}")
    
    # 메모리에 저장된 보고서 확인
    print("\n" + "="*80)
    print("📦 메모리 허브 저장 확인")
    print("-"*50)
    
    from backend.packages.memory.contexts import ContextType
    stored_reports = await memory_hub.search(
        context_type=ContextType.A_CTX,
        limit=10
    )
    
    print(f"A_CTX에 저장된 항목: {len(stored_reports)}개")
    for item in stored_reports[:5]:
        print(f"  - {item.get('key', 'N/A')}")
    
    # 파일시스템 보고서 확인
    print("\n" + "="*80)
    print("📁 생성된 보고서 파일")
    print("-"*50)
    
    reports_dir = Path("reports")
    if reports_dir.exists():
        agent_dirs = list(reports_dir.iterdir())
        print(f"에이전트 디렉토리: {len(agent_dirs)}개")
        for agent_dir in sorted(agent_dirs)[:5]:
            if agent_dir.is_dir():
                report_count = sum(1 for _ in agent_dir.rglob("*.md")) + \
                              sum(1 for _ in agent_dir.rglob("*.json")) + \
                              sum(1 for _ in agent_dir.rglob("*.html"))
                print(f"  - {agent_dir.name}: {report_count}개 보고서")
    
    # 정리
    await memory_hub.shutdown()
    print("\n✅ 전체 테스트 완료!")


if __name__ == "__main__":
    import os
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    print("🔧 환경 설정:")
    print(f"   - AWS Region: {os.environ.get('AWS_DEFAULT_REGION')}")
    print(f"   - Python: {sys.version.split()[0]}")
    print()
    
    asyncio.run(test_all_agents())