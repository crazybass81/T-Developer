#!/usr/bin/env python3
"""TaskCreatorAgent 간단한 테스트 - 태스크 생성 검증."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from backend.packages.agents.task_creator_agent import TaskCreatorAgent
from backend.packages.agents.base import AgentTask
from backend.packages.memory.hub import MemoryHub


async def test_task_creator_simple():
    """TaskCreatorAgent 간단한 테스트."""
    print("="*80)
    print("🔨 TaskCreatorAgent 간단한 검증 테스트")
    print("="*80)
    
    # 메모리 허브 초기화
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    # TaskCreatorAgent 생성
    task_creator = TaskCreatorAgent(memory_hub=memory_hub)
    
    # 간단한 계획 - 단일 태스크만
    simple_plan = {
        "tasks": [
            {
                "id": "task_001",
                "name": "Test Task",
                "description": "A simple test task",
                "agent": "test_agent",
                "inputs": ["input1"],
                "outputs": ["output1"],
                "duration_minutes": 30
            }
        ],
        "dependencies": {}
    }
    
    print("\n📋 간단한 태스크 테스트")
    print(f"   - 태스크 수: {len(simple_plan['tasks'])}")
    
    # 태스크 생성 실행
    task = AgentTask(
        intent="create_tasks",
        inputs={
            "plan": simple_plan,
            "requirement": "Test requirement"
        }
    )
    
    print("\n🔄 태스크 생성 중...")
    
    try:
        result = await task_creator.execute(task)
        
        print(f"\n✅ 결과:")
        print(f"   - 성공: {result.success}")
        print(f"   - 상태: {result.status}")
        
        if result.data:
            print(f"   - 생성된 태스크 수: {len(result.data.get('tasks', []))}")
            
            # 결과 저장
            output_dir = Path("test_outputs")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"task_simple_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump({
                    "plan": simple_plan,
                    "result": {
                        "success": result.success,
                        "status": str(result.status),
                        "data": result.data
                    }
                }, f, indent=2, default=str)
            
            print(f"\n💾 저장: {output_file}")
            
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
    
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
    
    asyncio.run(test_task_creator_simple())