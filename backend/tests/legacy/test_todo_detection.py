#!/usr/bin/env python3
"""
Todo 앱 감지 테스트
"""

import asyncio
from src.agents.unified.generation.agent import GenerationAgent

async def test_todo_detection():
    agent = GenerationAgent()
    
    test_cases = [
        {"name": "Todo App", "description": "A todo application"},
        {"name": "Task Manager", "description": "Manage tasks"},
        {"name": "To-Do List", "description": "Simple list"},
        {"name": "Advanced Todo App", "description": "Complete todo app"},
        {"name": "Blog App", "description": "A blog application"},
    ]
    
    print("Testing Todo App Detection:")
    print("-" * 40)
    
    for test_case in test_cases:
        is_todo = agent._is_todo_app_request(test_case)
        status = "✅ TODO" if is_todo else "❌ NOT TODO"
        print(f"{status}: {test_case['name']}")
    
    # 실제 API 요청 형식 테스트
    api_request = {
        "name": "Test Todo App with Agno",
        "description": "Complete Todo application with dynamically generated agents",
        "framework": "react",
        "features": ["todo", "priority", "filter", "search", "statistics", "dark-mode"],
        "aiModel": "claude"
    }
    
    print("\nAPI Request Test:")
    is_todo = agent._is_todo_app_request(api_request)
    print(f"{'✅ TODO' if is_todo else '❌ NOT TODO'}: {api_request['name']}")
    
    # Generation Agent 실행 테스트
    print("\nTesting Generation Agent with Todo Request:")
    print("-" * 40)
    
    result = await agent.process(api_request)
    
    if result.success:
        print(f"✅ Generation successful!")
        if hasattr(result, 'agents_created'):
            print(f"   Agents created: {result.agents_created}")
        if hasattr(result, 'generated_files'):
            print(f"   Files generated: {len(result.generated_files)}")
    else:
        print(f"❌ Generation failed: {result.error}")

if __name__ == "__main__":
    asyncio.run(test_todo_detection())