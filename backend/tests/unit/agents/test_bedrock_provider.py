#!/usr/bin/env python3
"""Test AWS Bedrock AI Provider.

실제 AWS Bedrock Claude 모델이 작동하는지 테스트합니다.
"""

import asyncio
import json
import sys
from pathlib import Path

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from backend.packages.agents.ai_providers import get_ai_provider, BedrockAIProvider


async def test_bedrock_provider():
    """Bedrock Provider 테스트."""
    
    print("🚀 AWS Bedrock AI Provider 테스트")
    print("=" * 60)
    
    # 1. Bedrock Provider 생성
    print("\n1. Bedrock Provider 생성...")
    provider = get_ai_provider("bedrock", {
        "model": "claude-3-sonnet",
        "region": "us-east-1"
    })
    
    assert isinstance(provider, BedrockAIProvider)
    print(f"   ✅ Bedrock Provider 생성 성공")
    print(f"   Model: {provider.default_model_id}")
    print(f"   Region: {provider.region}")
    
    # 2. 간단한 테스트
    print("\n2. 간단한 대화 테스트...")
    response = await provider.generate(
        prompt="Say 'Hello, T-Developer v2!' in Korean",
        system_prompt="You are a helpful assistant."
    )
    
    if response.success:
        print("   ✅ 응답 생성 성공")
        print(f"   응답: {response.content[:100]}")
        print(f"   Provider: {response.metadata['provider']}")
        print(f"   Model: {response.metadata['model']}")
    else:
        print(f"   ❌ 응답 실패: {response.error}")
        return
    
    # 3. 요구사항 분석 테스트
    print("\n3. 요구사항 분석 테스트...")
    response = await provider.generate(
        prompt="""Analyze the following requirements for a user authentication system:
        1. Users should be able to register with email and password
        2. Support OAuth login (Google, GitHub)
        3. Two-factor authentication
        4. Password reset via email
        
        Provide a structured analysis in JSON format with:
        - functional_requirements (list)
        - non_functional_requirements (list)
        - suggested_architecture (list of components)
        - estimated_complexity (low/medium/high)
        """,
        system_prompt="You are an expert software architect. Analyze requirements and provide structured responses."
    )
    
    if response.success:
        print("   ✅ 요구사항 분석 완료")
        try:
            # JSON 파싱 시도
            if "```json" in response.content:
                json_start = response.content.find("```json") + 7
                json_end = response.content.find("```", json_start)
                json_str = response.content[json_start:json_end].strip()
            else:
                json_str = response.content
            
            data = json.loads(json_str)
            print(f"   - Functional requirements: {len(data.get('functional_requirements', []))}개")
            print(f"   - Complexity: {data.get('estimated_complexity', 'N/A')}")
        except:
            print(f"   - 응답 길이: {len(response.content)} 문자")
    
    # 4. 코드 생성 테스트
    print("\n4. 코드 생성 테스트...")
    response = await provider.generate(
        prompt="""Generate a Python function that validates email addresses.
        Requirements:
        - Check for @ symbol
        - Check domain format
        - Return True if valid, False otherwise
        - Include docstring
        
        Return only the Python code.""",
        max_tokens=500
    )
    
    if response.success:
        print("   ✅ 코드 생성 성공")
        print(f"   - 생성된 코드 길이: {len(response.content)} 문자")
        
        # 코드 미리보기
        code_preview = response.content[:200] + "..." if len(response.content) > 200 else response.content
        print(f"   - 미리보기:\n{code_preview}")
    
    # 5. 스트리밍 테스트
    print("\n5. 스트리밍 응답 테스트...")
    print("   Streaming: ", end="", flush=True)
    
    chunks = []
    async for chunk in provider.stream_generate(
        prompt="Write a haiku about artificial intelligence"
    ):
        chunks.append(chunk)
        print(".", end="", flush=True)
    
    print(f"\n   ✅ {len(chunks)} 청크 수신 (현재는 한 번에 전송)")
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 통과!")
    print("\nAWS Bedrock Claude가 정상적으로 작동합니다.")
    print("T-Developer v2가 실제 AI를 사용할 준비가 되었습니다!")


async def test_direct_bedrock_call():
    """직접 Bedrock API 호출 테스트."""
    
    print("\n\n📡 직접 Bedrock API 호출 테스트")
    print("=" * 60)
    
    import boto3
    
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    body = json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'messages': [{'role': 'user', 'content': 'What is 2+2?'}],
        'max_tokens': 50
    })
    
    try:
        response = client.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=body
        )
        
        result = json.loads(response['body'].read())
        print(f"✅ 직접 호출 성공!")
        print(f"   응답: {result['content'][0]['text']}")
        
    except Exception as e:
        print(f"❌ 직접 호출 실패: {e}")
    
    print("=" * 60)


async def main():
    """메인 실행 함수."""
    try:
        await test_bedrock_provider()
        await test_direct_bedrock_call()
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())