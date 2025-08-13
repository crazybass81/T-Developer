#!/usr/bin/env python3
"""
범용 에이전트 생성 테스트
다양한 앱 요청에 대해 동적으로 에이전트를 생성하는지 확인
"""

import asyncio
from src.agents.unified.generation.universal_agent_factory import UniversalAgentFactory

async def test_various_apps():
    factory = UniversalAgentFactory()
    
    test_cases = [
        {
            "name": "Chat App",
            "requirements": {
                "user_input": "Create a chat application",
                "description": "Real-time chat with messages",
                "features": ["chat", "message", "notification", "user"]
            },
            "expected_agents": ["MessageManager", "SocketService", "NotificationService", "UserManager"]
        },
        {
            "name": "E-commerce",
            "requirements": {
                "user_input": "Build an online shop",
                "description": "Shopping platform with products and cart",
                "features": ["product", "cart", "payment", "order"]
            },
            "expected_agents": ["ProductManager", "CartService", "PaymentService", "OrderManager"]
        },
        {
            "name": "Blog Platform",
            "requirements": {
                "user_input": "Create a blog",
                "description": "Blog with posts and comments",
                "features": ["blog", "article", "comment", "tag"]
            },
            "expected_agents": ["PostManager", "CommentService", "TagManager"]
        },
        {
            "name": "Task Manager",
            "requirements": {
                "user_input": "Task management system",
                "description": "Manage tasks with priorities",
                "features": ["task", "schedule", "calendar"]
            },
            "expected_agents": ["TaskManager", "SchedulerService", "CalendarService"]
        }
    ]
    
    print("=" * 60)
    print("🧪 Universal Agent Factory Test")
    print("=" * 60)
    
    for test in test_cases:
        print(f"\n📱 {test['name']}")
        print("-" * 40)
        
        # 에이전트 생성
        result = await factory.analyze_and_create_agents(test['requirements'])
        
        print(f"✅ Agents Created: {result['agents_created']}")
        print(f"📋 Agent Names:")
        for agent_name in result['agent_names']:
            print(f"   - {agent_name}")
        
        # 생성된 코드 확인
        if 'generated_code' in result:
            print(f"\n📝 Generated Code Files: {len(result['generated_code'])}")
            for agent_name, code in list(result['generated_code'].items())[:2]:
                lines = code.split('\n')[:5]
                print(f"\n   {agent_name}.js (first 5 lines):")
                for i, line in enumerate(lines, 1):
                    if line.strip():
                        print(f"      {i}: {line[:60]}")
        
        # 예상 에이전트와 비교
        created_set = set(result['agent_names'])
        expected_set = set(test['expected_agents'])
        matched = created_set.intersection(expected_set)
        
        print(f"\n🎯 Expected vs Created:")
        print(f"   Matched: {len(matched)}/{len(expected_set)}")
        if matched:
            print(f"   ✅ {', '.join(matched)}")
    
    print("\n" + "=" * 60)
    print("✨ Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_various_apps())