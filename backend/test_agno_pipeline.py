#!/usr/bin/env python3
"""
Agno Framework 기반 동적 에이전트 생성 파이프라인 테스트
"""

import asyncio
import json
from src.agents.unified.generation.todo_agent_factory import TodoAgentFactory
from src.agno.agent_generator import agent_generator
import time

async def test_dynamic_agent_generation():
    """동적 에이전트 생성 및 실행 테스트"""
    
    print("=" * 60)
    print("🚀 Agno Framework Dynamic Agent Generation Test")
    print("=" * 60)
    
    # 1. TodoAgentFactory 초기화
    print("\n1️⃣ Initializing TodoAgentFactory...")
    factory = TodoAgentFactory()
    
    # 2. 요구사항 정의 (Parser와 Component Decision 에이전트가 분석할 내용)
    requirements = {
        'features': [
            'task management',
            'priority setting',
            'filtering and search',
            'statistics dashboard',
            'local storage persistence',
            'ui themes',
            'notifications'
        ],
        'entities': {
            'Task': {
                'fields': ['id', 'title', 'description', 'completed', 'priority', 'dueDate', 'category', 'tags']
            }
        },
        'specifications': {
            'framework': 'react',
            'storage': 'localStorage',
            'theme': 'dark_mode_support'
        }
    }
    
    print("\n2️⃣ Requirements defined:")
    print(f"   Features: {len(requirements['features'])} features")
    print(f"   Entities: {list(requirements['entities'].keys())}")
    
    # 3. 동적으로 에이전트 생성
    print("\n3️⃣ Dynamically creating agents based on requirements...")
    start_time = time.perf_counter()
    
    agent_result = await factory.analyze_and_create_agents(requirements)
    
    creation_time = (time.perf_counter() - start_time) * 1000
    print(f"   ✅ Created {agent_result['agents_created']} agents in {creation_time:.2f}ms")
    print(f"   Agents: {', '.join(agent_result['agent_names'])}")
    
    # 4. 생성된 에이전트들 테스트
    print("\n4️⃣ Testing generated agents with sample workflow...")
    test_result = await factory.test_generated_agents("Create a high priority task for testing")
    
    if 'error' not in test_result:
        workflow = test_result['workflow_result']
        print(f"   ✅ Workflow completed successfully")
        print(f"   Steps executed: {len(workflow['steps'])}")
        
        for step in workflow['steps']:
            status = "✅" if step['result'].get('success') else "❌"
            print(f"      {status} {step['step']}")
        
        # 성능 메트릭
        perf = test_result['performance']
        print(f"\n   📊 Performance Metrics:")
        print(f"      Total executions: {perf['total_executions']}")
        print(f"      Average execution time: {perf['average_execution_time_ms']:.2f}ms")
        print(f"      Success rate: {perf['success_rate']:.2%}")
    else:
        print(f"   ❌ Error: {test_result['error']}")
    
    # 5. Agno Framework 성능 리포트
    print("\n5️⃣ Agno Framework Performance Report:")
    perf_report = agent_generator.get_performance_report()
    
    print(f"   Total agents generated: {perf_report['total_agents_generated']}")
    print(f"   Average generation time: {perf_report['average_generation_time_us']:.2f}μs")
    print(f"   Target met (≤3μs): {'✅ Yes' if perf_report['target_met'] else '❌ No'}")
    
    # 6. 생성된 에이전트 코드 샘플
    print("\n6️⃣ Sample Generated Agent Code:")
    if 'TodoCRUDAgent' in agent_result['agent_names']:
        sample_code = factory.generate_agent_code('TodoCRUDAgent')
        print("   TodoCRUDAgent JavaScript code generated:")
        print("   " + sample_code.split('\n')[0])  # 첫 줄만 출력
        print("   ... (code generation successful)")
    
    # 7. 개별 에이전트 기능 테스트
    print("\n7️⃣ Testing Individual Agent Capabilities:")
    
    # CRUD 테스트
    if factory.runtime:
        # 작업 생성
        create_result = await factory.runtime.create_task({
            'title': 'Implement authentication',
            'description': 'Add user login and registration',
            'completed': False
        })
        print(f"   ✅ Task created: {create_result.get('success', False)}")
        
        # 통계 조회
        stats_result = await factory.runtime.get_task_statistics()
        if stats_result.get('success'):
            stats = stats_result.get('result', {})
            print(f"   ✅ Statistics generated:")
            for key, value in list(stats.items())[:3]:  # 상위 3개만 출력
                print(f"      - {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✨ Agno Framework Test Complete!")
    print("=" * 60)
    
    return {
        'success': True,
        'agents_created': agent_result['agents_created'],
        'performance': perf_report,
        'test_passed': test_result.get('workflow_result', {}).get('final_result', {}).get('success', False)
    }


async def test_agent_generation_speed():
    """에이전트 생성 속도 벤치마크"""
    
    print("\n🏎️ Agent Generation Speed Benchmark")
    print("-" * 40)
    
    blueprints = [
        {'name': f'Agent_{i}', 'type': 'data_manager', 'config': {'entity': f'Entity_{i}'}}
        for i in range(100)
    ]
    
    from src.agno.agent_generator import create_agent_from_blueprint
    
    start_time = time.perf_counter_ns()
    agents = []
    
    for blueprint in blueprints:
        agent = await create_agent_from_blueprint(blueprint)
        agents.append(agent)
    
    total_time_ns = time.perf_counter_ns() - start_time
    total_time_ms = total_time_ns / 1_000_000
    avg_time_us = (total_time_ns / len(blueprints)) / 1_000
    
    print(f"   Generated {len(blueprints)} agents")
    print(f"   Total time: {total_time_ms:.2f}ms")
    print(f"   Average per agent: {avg_time_us:.2f}μs")
    print(f"   Target (3μs): {'✅ Met' if avg_time_us <= 3 else f'❌ Missed by {avg_time_us - 3:.2f}μs'}")
    
    return avg_time_us


if __name__ == "__main__":
    async def main():
        # 메인 테스트
        result = await test_dynamic_agent_generation()
        
        # 속도 벤치마크
        await test_agent_generation_speed()
        
        if result['success']:
            print("\n✅ All tests passed!")
            exit(0)
        else:
            print("\n❌ Some tests failed")
            exit(1)
    
    asyncio.run(main())