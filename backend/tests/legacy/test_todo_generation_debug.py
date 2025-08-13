#!/usr/bin/env python3
"""
Todo 앱 생성 디버깅
"""

import asyncio
import json
from src.agents.unified.generation.agent import GenerationAgent
from src.agents.unified.generation.todo_agent_factory import TodoAgentFactory

async def test_todo_generation():
    print("=" * 60)
    print("TODO APP GENERATION DEBUG TEST")
    print("=" * 60)
    
    # 1. Generation Agent 초기화
    print("\n1. Initializing Generation Agent...")
    agent = GenerationAgent()
    
    # 2. 테스트 요청 데이터
    test_request = {
        "name": "Debug Todo App",
        "description": "Todo app for debugging",
        "framework": "react",
        "features": ["todo", "priority", "filter"],
        "project_id": "debug_todo_001"
    }
    
    print(f"2. Test Request: {test_request['name']}")
    
    # 3. Todo 앱 감지 테스트
    is_todo = agent._is_todo_app_request(test_request)
    print(f"3. Is Todo App: {'✅ YES' if is_todo else '❌ NO'}")
    
    if is_todo:
        # 4. TodoAgentFactory 테스트
        print("\n4. Testing TodoAgentFactory...")
        factory = TodoAgentFactory()
        
        # 5. 에이전트 생성
        print("5. Creating dynamic agents...")
        agent_result = await factory.analyze_and_create_agents(test_request)
        print(f"   Created {agent_result['agents_created']} agents:")
        for agent_name in agent_result['agent_names']:
            print(f"   - {agent_name}")
        
        # 6. 파일 생성 테스트
        print("\n6. Generating Todo app files...")
        generated_files = await agent._generate_todo_app_with_agents(
            test_request,
            factory,
            agent_result
        )
        
        print(f"   Generated {len(generated_files)} files:")
        for file_path in list(generated_files.keys())[:10]:  # 첫 10개만 표시
            print(f"   - {file_path}")
        
        # 7. 파일 내용 검증
        print("\n7. Validating file contents...")
        
        # package.json 확인
        if 'package.json' in generated_files:
            try:
                package_data = json.loads(generated_files['package.json'])
                print(f"   ✅ package.json valid - name: {package_data.get('name')}")
            except:
                print("   ❌ package.json invalid JSON")
        
        # App.js 확인
        if 'src/App.js' in generated_files:
            app_content = generated_files['src/App.js']
            if 'TodoCRUDAgent' in app_content:
                print("   ✅ App.js contains agent imports")
            else:
                print("   ❌ App.js missing agent imports")
        
        # 에이전트 파일 확인
        agent_files = [f for f in generated_files.keys() if 'agents/' in f]
        print(f"   Found {len(agent_files)} agent files")
        
        # 8. 전체 Generation Agent 프로세스 테스트
        print("\n8. Testing full Generation Agent process...")
        result = await agent.process(test_request)
        
        if result.success:
            print("   ✅ Generation successful!")
            print(f"   - Files: {result.total_files}")
            print(f"   - Agents: {result.agents_created}")
            if hasattr(result, 'workspace_path'):
                print(f"   - Workspace: {result.workspace_path}")
        else:
            print(f"   ❌ Generation failed: {result.error}")
        
        return result
    
    else:
        print("❌ Not detected as Todo app!")
        return None

async def main():
    result = await test_todo_generation()
    
    if result and result.success:
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        # 생성된 파일 목록
        if hasattr(result, 'generated_files'):
            print(f"\n📁 Total files generated: {len(result.generated_files)}")
            print("\n📦 Project structure:")
            for file_path in sorted(result.generated_files.keys()):
                size = len(result.generated_files[file_path])
                print(f"   {file_path} ({size} bytes)")
    else:
        print("\n❌ TEST FAILED")

if __name__ == "__main__":
    asyncio.run(main())