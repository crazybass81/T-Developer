#!/usr/bin/env python3
"""
Todo 앱 감지 및 생성 테스트
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

async def test_todo_generation():
    from src.agents.unified.generation.agent import GenerationAgent
    
    agent = GenerationAgent()
    
    # Todo 앱 요청 데이터
    test_data = {
        'data': {
            'user_input': 'Create a todo app with tasks and priorities',
            'description': 'A todo application with task management',
            'features': ['todo', 'priority', 'categories'],
            'name': 'advanced-todo',
            'framework': 'react',
            'project_id': 'test-todo-123'
        },
        'context': {
            'pipeline_id': 'test'
        }
    }
    
    print("Testing Todo App Detection and Generation...")
    print("=" * 50)
    
    # 1. Todo 앱 감지 테스트
    is_todo = agent._is_todo_app_request(test_data['data'])
    print(f"1. Is Todo App Detected: {is_todo}")
    
    if is_todo:
        print("\n2. Generating Todo App with Dynamic Agents...")
        
        # 실제 process 메서드 호출
        result = await agent.process(test_data)
        
        if hasattr(result, 'generated_files'):
            files = result.generated_files
            print(f"\n3. Generated Files: {len(files)}")
            
            # 파일 목록
            for file_path in sorted(files.keys())[:10]:
                print(f"   - {file_path}")
            
            # 에이전트 파일 확인
            agent_files = [f for f in files.keys() if 'agents/' in f]
            if agent_files:
                print(f"\n4. Dynamic Agent Files Created: {len(agent_files)}")
                for af in agent_files:
                    print(f"   - {af}")
            
            # App.js 내용 확인
            if 'src/App.js' in files:
                app_content = files['src/App.js']
                print(f"\n5. App.js Analysis:")
                print(f"   - Size: {len(app_content)} chars")
                print(f"   - Has TodoCRUDAgent: {'TodoCRUDAgent' in app_content}")
                print(f"   - Has useState: {'useState' in app_content}")
                print(f"   - Has TodoList component: {'TodoList' in app_content}")
            
            # TodoCRUDAgent 코드 확인
            if 'src/agents/TodoCRUDAgent.js' in files:
                crud_content = files['src/agents/TodoCRUDAgent.js']
                print(f"\n6. TodoCRUDAgent.js Analysis:")
                print(f"   - Size: {len(crud_content)} chars")
                print(f"   - Has create method: {'create(' in crud_content}")
                print(f"   - Has localStorage: {'localStorage' in crud_content}")
                
                # 처음 5줄 출력
                lines = crud_content.split('\n')[:5]
                print(f"\n   First 5 lines:")
                for i, line in enumerate(lines, 1):
                    print(f"   {i}: {line[:60]}...")
        
        # 메타데이터 확인
        if hasattr(result, 'is_todo_app'):
            print(f"\n7. Metadata:")
            print(f"   - is_todo_app: {result.is_todo_app}")
            print(f"   - agents_created: {result.agents_created}")
            if hasattr(result, 'agent_names'):
                print(f"   - agent_names: {result.agent_names}")
    else:
        print("\n❌ Todo app not detected!")

if __name__ == "__main__":
    asyncio.run(test_todo_generation())