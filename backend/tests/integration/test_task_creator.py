#!/usr/bin/env python3
"""TaskCreatorAgent 단독 테스트 - 태스크 생성 검증."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from pprint import pprint

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from backend.packages.agents.task_creator_agent import TaskCreatorAgent
from backend.packages.agents.base import AgentTask
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType


async def test_task_creator():
    """TaskCreatorAgent 상세 테스트."""
    print("="*80)
    print("🔨 TaskCreatorAgent 검증 테스트")
    print("="*80)
    
    # 메모리 허브 초기화
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    # TaskCreatorAgent 생성
    task_creator = TaskCreatorAgent(memory_hub=memory_hub)
    
    # 테스트 1: 간단한 실행 계획으로부터 태스크 생성
    plan1 = {
        "goals": [
            "Create REST API endpoints",
            "Implement authentication",
            "Add validation and error handling"
        ],
        "phases": [
            {
                "name": "API Development",
                "description": "Build core API endpoints",
                "objectives": ["Implement CRUD operations"],
                "deliverables": ["Working API"],
                "duration_hours": 8
            },
            {
                "name": "Security Implementation",
                "description": "Add authentication and authorization",
                "objectives": ["Secure the API"],
                "deliverables": ["JWT authentication"],
                "duration_hours": 6
            },
            {
                "name": "Quality Assurance",
                "description": "Testing and validation",
                "objectives": ["Ensure quality"],
                "deliverables": ["Test suite", "Documentation"],
                "duration_hours": 4
            }
        ],
        "tasks": [
            {
                "id": "task_001",
                "name": "Analyze API requirements",
                "description": "Analyze and document API requirements",
                "phase": "API Development",
                "agent": "requirement_analyzer",
                "inputs": ["requirements", "context"],
                "outputs": ["specification", "api_design"],
                "duration_minutes": 60
            },
            {
                "id": "task_002",
                "name": "Setup FastAPI project",
                "description": "Initialize FastAPI project structure",
                "phase": "API Development",
                "agent": "code_generator",
                "inputs": ["specification"],
                "outputs": ["project_structure", "base_code"],
                "duration_minutes": 30
            },
            {
                "id": "task_003",
                "name": "Implement CRUD endpoints",
                "description": "Create user CRUD operations",
                "phase": "API Development",
                "agent": "code_generator",
                "inputs": ["api_design", "base_code"],
                "outputs": ["api_endpoints"],
                "duration_minutes": 120
            },
            {
                "id": "task_004",
                "name": "Implement JWT authentication",
                "description": "Add JWT-based authentication",
                "phase": "Security Implementation",
                "agent": "code_generator",
                "inputs": ["api_endpoints"],
                "outputs": ["auth_system"],
                "duration_minutes": 90
            },
            {
                "id": "task_005",
                "name": "Add input validation",
                "description": "Implement request validation",
                "phase": "Security Implementation",
                "agent": "code_generator",
                "inputs": ["api_endpoints"],
                "outputs": ["validated_endpoints"],
                "duration_minutes": 60
            },
            {
                "id": "task_006",
                "name": "Write unit tests",
                "description": "Create comprehensive test suite",
                "phase": "Quality Assurance",
                "agent": "code_generator",
                "inputs": ["validated_endpoints", "auth_system"],
                "outputs": ["test_suite"],
                "duration_minutes": 120
            },
            {
                "id": "task_007",
                "name": "Generate documentation",
                "description": "Create API documentation",
                "phase": "Quality Assurance",
                "agent": "report_generator",
                "inputs": ["validated_endpoints"],
                "outputs": ["api_documentation"],
                "duration_minutes": 30
            }
        ],
        "dependencies": {
            "task_002": ["task_001"],
            "task_003": ["task_002"],
            "task_004": ["task_003"],
            "task_005": ["task_003"],
            "task_006": ["task_004", "task_005"],
            "task_007": ["task_005"]
        },
        "requirements": "Build a user management API with FastAPI"
    }
    
    print("\n📋 테스트 1: API 개발 태스크 생성")
    print("-"*50)
    print(f"계획: {len(plan1['phases'])}개 단계")
    for phase in plan1['phases']:
        print(f"  - {phase['name']}")
    
    # 태스크 생성 실행
    task1 = AgentTask(
        intent="create_tasks",
        inputs={
            "plan": plan1,
            "requirements": plan1["requirements"]
        }
    )
    
    print("\n🔄 태스크 생성 중...")
    result1 = await task_creator.execute(task1)
    
    print(f"\n✅ 태스크 생성 결과:")
    print(f"   - 성공 여부: {result1.success}")
    print(f"   - 상태: {result1.status}")
    
    if result1.success and result1.data:
        data = result1.data
        
        # 태스크 상세 출력
        print(f"\n📊 생성된 태스크:")
        
        if 'tasks' in data:
            tasks = data['tasks']
            print(f"\n   [태스크 목록] 총 {len(tasks)}개")
            for i, task in enumerate(tasks[:10], 1):
                print(f"\n   {i}. {task.get('name', 'N/A')}")
                print(f"      - ID: {task.get('id', 'N/A')}")
                print(f"      - 타입: {task.get('type', 'N/A')}")
                print(f"      - 에이전트: {task.get('agent', 'N/A')}")
                print(f"      - 우선순위: {task.get('priority', 'N/A')}")
                print(f"      - 예상 시간: {task.get('estimated_duration', 'N/A')}분")
                if 'dependencies' in task:
                    print(f"      - 의존성: {', '.join(task['dependencies']) if task['dependencies'] else 'None'}")
                if 'inputs' in task:
                    print(f"      - 입력: {', '.join(task['inputs'][:3])}")
                if 'outputs' in task:
                    print(f"      - 출력: {', '.join(task['outputs'][:3])}")
        
        # 실행 순서
        if 'execution_order' in data:
            order = data['execution_order']
            print(f"\n   [실행 순서]")
            for i, task_id in enumerate(order[:5], 1):
                print(f"   {i}. {task_id}")
        
        # 태스크 통계
        if 'statistics' in data:
            stats = data['statistics']
            print(f"\n   [태스크 통계]")
            print(f"   • 총 태스크: {stats.get('total_tasks', 0)}개")
            print(f"   • 총 예상 시간: {stats.get('total_duration', 0)}분")
            print(f"   • 병렬 실행 가능: {stats.get('parallelizable', 0)}개")
            print(f"   • Critical path: {stats.get('critical_path_duration', 0)}분")
    
    # 결과를 파일로 저장
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"task_creation_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "plan": plan1,
            "result": {
                "success": result1.success,
                "status": str(result1.status),
                "data": result1.data,
                "metadata": result1.metadata
            }
        }, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n💾 태스크 생성 결과 저장: {output_file.absolute()}")
    
    # 테스트 2: 복잡한 마이그레이션 계획
    print("\n" + "="*80)
    plan2 = {
        "goals": [
            "Extract services from monolith",
            "Setup microservices infrastructure",
            "Migrate data with zero downtime",
            "Implement service mesh"
        ],
        "phases": [
            {
                "name": "Service Extraction",
                "description": "Extract microservices from monolith",
                "objectives": ["Identify service boundaries", "Extract services"],
                "deliverables": ["Service definitions", "Extracted code"],
                "duration_hours": 40
            },
            {
                "name": "Infrastructure Setup",
                "description": "Setup Kubernetes and service mesh",
                "objectives": ["Deploy infrastructure"],
                "deliverables": ["K8s cluster", "Service mesh"],
                "duration_hours": 24
            },
            {
                "name": "Data Migration",
                "description": "Migrate data to microservices databases",
                "objectives": ["Zero downtime migration"],
                "deliverables": ["Migrated data", "Sync mechanisms"],
                "duration_hours": 32
            },
            {
                "name": "Cutover",
                "description": "Switch traffic to microservices",
                "objectives": ["Complete migration"],
                "deliverables": ["Live microservices"],
                "duration_hours": 8
            }
        ],
        "tasks": [
            {
                "id": "migrate_001",
                "name": "Analyze monolith architecture",
                "description": "Analyze current monolith to identify service boundaries",
                "phase": "Service Extraction",
                "agent": "code_analysis",
                "inputs": ["codebase", "requirements"],
                "outputs": ["service_boundaries", "dependency_map"],
                "duration_minutes": 480
            },
            {
                "id": "migrate_002",
                "name": "Extract user service",
                "description": "Extract user management to microservice",
                "phase": "Service Extraction",
                "agent": "code_generator",
                "inputs": ["service_boundaries"],
                "outputs": ["user_service"],
                "duration_minutes": 480
            },
            {
                "id": "migrate_003",
                "name": "Setup Kubernetes cluster",
                "description": "Deploy and configure K8s infrastructure",
                "phase": "Infrastructure Setup",
                "agent": "orchestrator",
                "inputs": ["infrastructure_spec"],
                "outputs": ["k8s_cluster"],
                "duration_minutes": 240
            },
            {
                "id": "migrate_004",
                "name": "Implement data sync",
                "description": "Setup data synchronization between old and new systems",
                "phase": "Data Migration",
                "agent": "code_generator",
                "inputs": ["user_service", "k8s_cluster"],
                "outputs": ["data_sync_system"],
                "duration_minutes": 480
            },
            {
                "id": "migrate_005",
                "name": "Perform cutover",
                "description": "Switch traffic to new microservices",
                "phase": "Cutover",
                "agent": "orchestrator",
                "inputs": ["data_sync_system", "user_service"],
                "outputs": ["live_system"],
                "duration_minutes": 120
            }
        ],
        "dependencies": {
            "migrate_002": ["migrate_001"],
            "migrate_003": [],
            "migrate_004": ["migrate_002", "migrate_003"],
            "migrate_005": ["migrate_004"]
        },
        "requirements": "Migrate monolith to microservices with zero downtime"
    }
    
    print("📋 테스트 2: 마이크로서비스 마이그레이션 태스크")
    print("-"*50)
    print(f"계획: {len(plan2['phases'])}개 단계")
    
    task2 = AgentTask(
        intent="create_tasks",
        inputs={
            "plan": plan2,
            "requirements": plan2["requirements"],
            "complexity": "high"
        }
    )
    
    print("\n🔄 태스크 생성 중...")
    result2 = await task_creator.execute(task2)
    
    if result2.success and result2.data:
        tasks2 = result2.data.get('tasks', [])
        stats2 = result2.data.get('statistics', {})
        print(f"\n✅ 마이그레이션 태스크 생성 완료:")
        print(f"   • 총 태스크: {len(tasks2)}개")
        print(f"   • 총 예상 시간: {stats2.get('total_duration', 0)}분")
        print(f"   • Critical path: {stats2.get('critical_path_duration', 0)}분")
        
        # Agent별 태스크 분포
        agent_distribution = {}
        for task in tasks2:
            agent = task.get('agent', 'unknown')
            agent_distribution[agent] = agent_distribution.get(agent, 0) + 1
        
        print(f"\n   [에이전트별 태스크 분포]")
        for agent, count in agent_distribution.items():
            print(f"   • {agent}: {count}개")
    
    # 메모리에서 저장된 태스크 확인
    print("\n" + "="*80)
    print("📦 메모리 허브 확인")
    print("-"*50)
    
    # 저장된 태스크 검색
    stored_tasks = await memory_hub.search(
        context_type=ContextType.O_CTX,
        limit=5
    )
    
    print(f"저장된 항목: {len(stored_tasks)}개")
    for item in stored_tasks:
        print(f"  - Key: {item.get('key', 'N/A')}")
        print(f"    Created: {item.get('created_at', 'N/A')}")
    
    # 정리
    await memory_hub.shutdown()
    print("\n✅ TaskCreatorAgent 테스트 완료!")


if __name__ == "__main__":
    import os
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    print("🔧 환경 설정:")
    print(f"   - AWS Region: {os.environ.get('AWS_DEFAULT_REGION')}")
    print(f"   - Python: {sys.version.split()[0]}")
    print()
    
    asyncio.run(test_task_creator())