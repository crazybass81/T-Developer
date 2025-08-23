#!/usr/bin/env python3
"""PlannerAgent 단독 테스트 - 실행 계획 생성 검증."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from pprint import pprint

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from backend.packages.agents.planner_agent import PlannerAgent
from backend.packages.agents.base import AgentTask
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType


async def test_planner_agent():
    """PlannerAgent 상세 테스트."""
    print("="*80)
    print("📋 PlannerAgent 검증 테스트")
    print("="*80)
    
    # 메모리 허브 초기화
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    # PlannerAgent 생성
    planner = PlannerAgent(memory_hub=memory_hub)
    
    # 테스트 1: API 엔드포인트 개발 계획
    requirement1 = """
    Create a REST API endpoint for user management with the following features:
    - GET /users - List all users with pagination
    - GET /users/{id} - Get user by ID  
    - POST /users - Create new user
    - PUT /users/{id} - Update user
    - DELETE /users/{id} - Delete user
    
    Technical requirements:
    - Use FastAPI framework
    - Include input validation
    - Add JWT authentication
    - Implement rate limiting
    - Add error handling
    - Include OpenAPI documentation
    - Write unit tests with 80% coverage
    """
    
    print("\n📝 테스트 1: API 엔드포인트 개발 계획")
    print("-"*50)
    print(requirement1[:200] + "...")
    
    # 계획 생성 실행
    task1 = AgentTask(
        intent="create_plan",
        inputs={
            "requirement": requirement1,
            "context": {"project_type": "api_development"}
        }
    )
    
    print("\n🔄 계획 생성 중...")
    result1 = await planner.execute(task1)
    
    print(f"\n✅ 계획 생성 결과:")
    print(f"   - 성공 여부: {result1.success}")
    print(f"   - 상태: {result1.status}")
    
    if result1.success and result1.data:
        data = result1.data
        
        # 계획 상세 출력
        print(f"\n📊 생성된 실행 계획:")
        
        if 'plan' in data:
            plan = data['plan']
            
            # 단계별 계획
            if 'phases' in plan:
                print(f"\n   [실행 단계] {len(plan['phases'])}개 단계")
                for i, phase in enumerate(plan['phases'][:5], 1):
                    print(f"   {i}. {phase.get('name', 'N/A')}")
                    if 'tasks' in phase:
                        for j, task in enumerate(phase['tasks'][:3], 1):
                            print(f"      {i}.{j} {task.get('description', '')[:60]}...")
            
            # 우선순위
            if 'priorities' in plan:
                print(f"\n   [우선순위]")
                for priority in plan['priorities'][:3]:
                    print(f"   • {priority}")
            
            # 일정
            if 'timeline' in plan:
                timeline = plan['timeline']
                print(f"\n   [일정 계획]")
                print(f"   • 총 기간: {timeline.get('duration', 'N/A')}")
                print(f"   • 시작일: {timeline.get('start', 'N/A')}")
                print(f"   • 종료일: {timeline.get('end', 'N/A')}")
            
            # 의존성
            if 'dependencies' in plan:
                deps = plan['dependencies']
                print(f"\n   [의존성] {len(deps)}개")
                # dependencies is a dict, not a list
                for task_id, dep_list in list(deps.items())[:3]:
                    print(f"   • {task_id} depends on: {', '.join(dep_list)}")
            
            # 리스크
            if 'risks' in plan:
                print(f"\n   [리스크] {len(plan['risks'])}개")
                for risk in plan['risks'][:2]:
                    print(f"   • {risk.get('description', '')[:70]}...")
            
            # 성공 지표
            if 'success_metrics' in plan:
                print(f"\n   [성공 지표] {len(plan['success_metrics'])}개")
                for metric in plan['success_metrics'][:3]:
                    print(f"   • {metric}")
    
    # 결과를 파일로 저장
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"planner_result_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "requirement": requirement1,
            "result": {
                "success": result1.success,
                "status": str(result1.status),
                "data": result1.data,
                "metadata": result1.metadata
            }
        }, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n💾 계획 결과 저장: {output_file.absolute()}")
    
    # 테스트 2: 마이크로서비스 마이그레이션 계획
    print("\n" + "="*80)
    requirement2 = """
    Migrate a monolithic application to microservices architecture:
    
    Current System:
    - Monolithic Django application
    - PostgreSQL database
    - 100,000 daily active users
    - 5GB database size
    
    Target Architecture:
    - User Service
    - Product Service  
    - Order Service
    - Payment Service
    - Notification Service
    
    Requirements:
    - Zero downtime migration
    - Data consistency
    - Gradual rollout with feature flags
    - Monitoring and observability
    - Rollback capability
    """
    
    print("📝 테스트 2: 마이크로서비스 마이그레이션 계획")
    print("-"*50)
    print(requirement2[:200] + "...")
    
    task2 = AgentTask(
        intent="create_plan",
        inputs={
            "requirement": requirement2,
            "context": {"project_type": "migration"}
        }
    )
    
    print("\n🔄 계획 생성 중...")
    result2 = await planner.execute(task2)
    
    if result2.success and result2.data:
        plan2 = result2.data.get('plan', {})
        print(f"\n✅ 마이그레이션 계획 생성 완료:")
        print(f"   • 단계: {len(plan2.get('phases', []))}개")
        print(f"   • 예상 기간: {plan2.get('timeline', {}).get('duration', 'N/A')}")
        print(f"   • 리스크: {len(plan2.get('risks', []))}개 식별")
    
    # 메모리에서 저장된 계획 확인
    print("\n" + "="*80)
    print("📦 메모리 허브 확인")
    print("-"*50)
    
    # 저장된 계획 검색
    stored_plans = await memory_hub.search(
        context_type=ContextType.O_CTX,  # Plans are stored in O_CTX
        limit=5
    )
    
    print(f"저장된 계획: {len(stored_plans)}개")
    for plan in stored_plans:
        print(f"  - Key: {plan.get('key', 'N/A')}")
        print(f"    Created: {plan.get('created_at', 'N/A')}")
    
    # 정리
    await memory_hub.shutdown()
    print("\n✅ PlannerAgent 테스트 완료!")


if __name__ == "__main__":
    import os
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    print("🔧 환경 설정:")
    print(f"   - AWS Region: {os.environ.get('AWS_DEFAULT_REGION')}")
    print(f"   - Python: {sys.version.split()[0]}")
    print()
    
    asyncio.run(test_planner_agent())