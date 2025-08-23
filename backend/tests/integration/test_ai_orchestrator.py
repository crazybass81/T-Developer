#!/usr/bin/env python3
"""AI Orchestrator 통합 테스트 - 100% 실제 AI 사용."""

import asyncio
import json
import sys
from pathlib import Path

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from backend.packages.orchestrator.upgrade_orchestrator import UpgradeOrchestrator as AIOrchestrator
from backend.packages.memory.hub import MemoryHub


async def test_ai_orchestrator():
    """AI Orchestrator 완전 통합 테스트."""
    print("="*60)
    print("🚀 T-Developer v2 AI Orchestrator 테스트")
    print("   100% Real AI - No Mocks!")
    print("="*60)
    
    # 메모리 허브 초기화
    print("\n📦 메모리 허브 초기화...")
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    print("✅ 메모리 허브 준비 완료")
    
    # AI Orchestrator 생성
    print("\n🤖 AI Orchestrator 생성...")
    orchestrator = AIOrchestrator(memory_hub)
    print("✅ Orchestrator 준비 완료")
    
    # 테스트 요구사항
    requirement = """
    Create a simple REST API endpoint for user registration:
    - POST /api/register
    - Input: email, password, name
    - Password must be hashed with bcrypt
    - Return JWT token
    - Store user in database
    - Input validation required
    - Error handling for duplicate emails
    """
    
    print("\n📋 요구사항:")
    print(requirement)
    
    print("\n" + "="*60)
    print("🔄 AI Orchestration 시작...")
    print("="*60)
    
    try:
        # 오케스트레이션 실행
        result = await orchestrator.orchestrate(requirement)
        
        print("\n" + "="*60)
        print("✅ Orchestration 완료!")
        print("="*60)
        
        # 결과 출력
        print(f"\n📊 실행 결과:")
        print(f"   - 성공 여부: {'✅ 성공' if result['success'] else '❌ 실패'}")
        print(f"   - 실행 시간: {result.get('execution_time', 0):.2f}초")
        print(f"   - 완료된 에이전트: {len(result.get('completed_agents', []))}개")
        
        if result.get('completed_agents'):
            print(f"\n📍 실행된 에이전트:")
            for agent in result['completed_agents']:
                print(f"   - {agent}")
        
        if result.get('execution_plan'):
            plan = result['execution_plan']
            print(f"\n📝 실행 계획:")
            print(f"   - 신뢰도: {plan.get('confidence', 0)*100:.1f}%")
            print(f"   - 위험도: {plan.get('risk_level', 'unknown')}")
            print(f"   - 추론: {plan.get('reasoning', 'N/A')[:100]}...")
        
        if result.get('quality'):
            quality = result['quality']
            print(f"\n✨ 품질 검증:")
            print(f"   - 통과 여부: {'✅' if quality.get('passed', False) else '❌'}")
            print(f"   - 이유: {quality.get('reason', 'N/A')}")
        
        if result.get('improvements'):
            print(f"\n💡 개선 제안:")
            for improvement in result['improvements'][:3]:
                print(f"   - {improvement}")
        
        if result.get('decisions'):
            print(f"\n🧠 AI 의사결정 기록: {len(result['decisions'])}건")
            for decision in result['decisions'][:3]:
                print(f"   - [{decision['type']}] {decision.get('reason', 'N/A')[:50]}...")
        
        # 생성된 코드 확인
        if result.get('results', {}).get('code_generator'):
            code_data = result['results']['code_generator']
            if isinstance(code_data, dict) and 'code' in code_data:
                print(f"\n📄 생성된 코드 (일부):")
                print("```python")
                print(code_data['code'][:500])
                print("```")
        
        # 보고서 경로
        if result.get('report'):
            print(f"\n📊 보고서 생성됨")
        
        print("\n" + "="*60)
        print("🎉 테스트 완료!")
        print("="*60)
        
        return result
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        # 메모리 허브 종료
        await memory_hub.shutdown()
        print("\n메모리 허브 종료 완료")


if __name__ == "__main__":
    import os
    
    # AWS 환경 변수 설정
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    print("🔧 환경 설정:")
    print(f"   - AWS Region: {os.environ.get('AWS_DEFAULT_REGION')}")
    print(f"   - Python: {sys.version.split()[0]}")
    
    # 테스트 실행
    result = asyncio.run(test_ai_orchestrator())
    
    if result:
        # 결과를 파일로 저장
        output_file = Path("orchestrator_test_result.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str, ensure_ascii=False)
        print(f"\n💾 전체 결과 저장: {output_file.absolute()}")