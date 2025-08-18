#!/usr/bin/env python3
"""하이브리드 컨텍스트 분석기 테스트."""

import asyncio
import os
import sys

# Add backend to path
sys.path.append("/home/ec2-user/T-Developer/backend")

from packages.agents.base import AgentInput
from packages.agents.hybrid_context_analyzer import HybridContextAnalyzer


async def test_hybrid_analyzer():
    """하이브리드 분석기 테스트."""
    print("=" * 60)
    print("Hybrid Context Analyzer Test")
    print("=" * 60)

    # 설정
    config = {"ai_enabled": True, "ai_threshold": 0.6}  # AI 활성화  # 신뢰도 60% 미만시 AI 사용

    analyzer = HybridContextAnalyzer(config)

    # 테스트 1: 간단한 코드 (AI 불필요)
    print("\n=== Test 1: Simple Code Analysis ===")
    input1 = AgentInput(
        task_id="test-001",
        intent="analyze",
        payload={
            "target": "/home/ec2-user/T-Developer/backend/packages/agents/base.py",
            "type": "code",
            "force_ai": False,
        },
    )

    result1 = await analyzer.execute(input1)
    print(f"Status: {result1.status}")
    print(f"Confidence: {result1.metrics.get('confidence', 0):.2f}")
    print(f"AI Used: {result1.metrics.get('ai_used', False)}")

    # 테스트 2: 복잡한 코드 (AI 필요할 수 있음)
    print("\n=== Test 2: Complex Code Analysis ===")
    input2 = AgentInput(
        task_id="test-002",
        intent="analyze",
        payload={
            "target": "/home/ec2-user/T-Developer/backend/packages/agents/context_analyzer.py",
            "type": "code",
            "force_ai": False,
        },
    )

    result2 = await analyzer.execute(input2)
    print(f"Status: {result2.status}")
    print(f"Confidence: {result2.metrics.get('confidence', 0):.2f}")
    print(f"AI Used: {result2.metrics.get('ai_used', False)}")

    # 테스트 3: 강제 AI 사용
    print("\n=== Test 3: Forced AI Analysis ===")

    # API 키 확인
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not set - AI analysis will be skipped")
        print("   Set with: export ANTHROPIC_API_KEY='your-key-here'")

    input3 = AgentInput(
        task_id="test-003",
        intent="analyze",
        payload={
            "target": "/home/ec2-user/T-Developer/backend/packages/agents/hybrid_context_analyzer.py",
            "type": "code",
            "force_ai": True,  # AI 강제 사용
        },
    )

    result3 = await analyzer.execute(input3)
    print(f"Status: {result3.status}")
    print(f"Confidence: {result3.metrics.get('confidence', 0):.2f}")
    print(f"AI Used: {result3.metrics.get('ai_used', False)}")

    # 테스트 4: 아키텍처 분석
    print("\n=== Test 4: Architecture Analysis ===")
    input4 = AgentInput(
        task_id="test-004",
        intent="analyze",
        payload={
            "target": "/home/ec2-user/T-Developer/backend/packages/agents",
            "type": "architecture",
            "force_ai": False,
        },
    )

    result4 = await analyzer.execute(input4)
    print(f"Status: {result4.status}")
    print(f"Confidence: {result4.metrics.get('confidence', 0):.2f}")

    # 결과 요약
    print("\n=== Analysis Summary ===")
    capabilities = analyzer.get_capabilities()
    metrics = capabilities["metrics"]

    print(f"Total Static Analyses: {metrics['static_analysis_count']}")
    print(f"Total AI Analyses: {metrics['ai_analysis_count']}")
    print(f"Cache Hits: {metrics['cache_hits']}")
    print(f"AI Usage Rate: {metrics['ai_usage_rate']:.1%}")

    # 권장사항 출력 (있는 경우)
    if result3.artifacts:
        content = result3.artifacts[0].content
        if "recommendations" in content:
            print("\n=== Recommendations ===")
            for rec in content["recommendations"][:5]:
                print(f"• {rec}")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_hybrid_analyzer())
