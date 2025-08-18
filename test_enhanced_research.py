#!/usr/bin/env python3
"""Enhanced External Research Agent 테스트."""

import asyncio
import os
import sys

# Add backend to path
sys.path.append("/home/ec2-user/T-Developer/backend")

from packages.agents.base import AgentInput
from packages.agents.enhanced_external_research import (
    EnhancedExternalResearchAgent,
    EnhancedResearchConfig,
)


async def test_enhanced_research():
    """향상된 외부 리서치 테스트."""
    print("=" * 70)
    print("Enhanced External Research Agent Test")
    print("=" * 70)

    # 설정
    config = EnhancedResearchConfig(
        enable_ai_analysis=True,
        ai_model="claude-3-sonnet-20240229",  # 깊이 있는 분석
        use_chain_of_thought=True,
        cot_steps=5,
        ai_temperature=0.3,  # 일관된 분석
        cache_ai_responses=True,
    )

    agent = EnhancedExternalResearchAgent(config=config)

    # 테스트 1: 인증 시스템 리서치
    print("\n=== Test 1: Authentication System Research ===")
    input1 = AgentInput(
        task_id="research-001",
        intent="research",
        payload={
            "problem": "implement secure authentication system with JWT and OAuth2",
            "requirements": ["jwt", "oauth2", "security", "scalability"],
            "constraints": {
                "budget": "medium",
                "timeline": "urgent",
                "team_size": "small",
                "tech_stack": "python/fastapi",
            },
        },
    )

    print("Searching GitHub, NPM, PyPI...")
    result1 = await agent.execute(input1)

    print(f"\nStatus: {result1.status}")
    print(f"API Calls: {result1.metrics.get('api_calls', 0)}")
    print(f"GitHub Solutions: {result1.metrics.get('github_solutions', 0)}")
    print(f"NPM Packages: {result1.metrics.get('npm_packages', 0)}")
    print(f"PyPI Packages: {result1.metrics.get('pypi_packages', 0)}")

    # API 키 확인
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  ANTHROPIC_API_KEY not set - AI analysis skipped")
        print("   Set with: export ANTHROPIC_API_KEY='your-key-here'")
    else:
        print(f"AI Analysis Performed: {result1.metrics.get('ai_calls', 0) > 0}")
        print(f"AI Confidence: {result1.metrics.get('ai_confidence', 0):.1%}")

    # AI 분석 결과 출력 (있는 경우)
    if result1.artifacts and result1.artifacts[0].content.get("ai_analysis"):
        ai_analysis = result1.artifacts[0].content["ai_analysis"]

        print("\n=== AI Analysis Results ===")
        print(f"Best Solution: {ai_analysis.get('best_solution', 'N/A')}")
        print(f"Confidence: {ai_analysis.get('confidence', 0):.1%}")

        # Chain of Thought 단계
        if ai_analysis.get("reasoning_chain"):
            print("\n--- Chain of Thought Steps ---")
            for i, step in enumerate(ai_analysis["reasoning_chain"][:3], 1):
                print(f"Step {i}: {step[:100]}...")

        # 구현 가이드
        if ai_analysis.get("implementation_guide"):
            print("\n--- Implementation Guide ---")
            for phase, details in list(ai_analysis["implementation_guide"].items())[:2]:
                print(f"• {phase}: {details.get('task', 'N/A')} ({details.get('duration', 'N/A')})")

        # 한국 컨텍스트
        if ai_analysis.get("korean_context"):
            korean = ai_analysis["korean_context"]
            print("\n--- Korean Context ---")
            print(f"• Localization Needed: {korean.get('localization_needed', False)}")
            print(f"• Community Support: {korean.get('community_support', 'N/A')}")

        # 리스크 평가
        if ai_analysis.get("risk_assessment"):
            risks = ai_analysis["risk_assessment"]
            if risks.get("technical_risks"):
                print(f"\n⚠️  Technical Risks: {len(risks['technical_risks'])} identified")

    # 권장사항
    if result1.artifacts and result1.artifacts[0].content.get("recommendations"):
        print("\n=== Recommendations ===")
        for rec in result1.artifacts[0].content["recommendations"][:5]:
            print(f"• {rec}")

    # 테스트 2: 머신러닝 파이프라인 리서치
    print("\n" + "=" * 70)
    print("=== Test 2: ML Pipeline Research ===")
    input2 = AgentInput(
        task_id="research-002",
        intent="research",
        payload={
            "problem": "build production ML pipeline with monitoring",
            "requirements": ["python", "mlflow", "kubernetes", "monitoring"],
            "constraints": {"budget": "high", "timeline": "flexible", "team_size": "medium"},
        },
    )

    result2 = await agent.execute(input2)
    print(f"\nStatus: {result2.status}")
    print(
        f"Total Solutions Found: {result2.metrics.get('github_solutions', 0) + result2.metrics.get('pypi_packages', 0)}"
    )

    # 능력 요약
    print("\n" + "=" * 70)
    print("=== Agent Capabilities ===")
    capabilities = agent.get_capabilities()
    print(f"Name: {capabilities['name']}")
    print(f"Version: {capabilities['version']}")
    print(f"AI Model: {capabilities['ai_model']}")
    print(f"Chain of Thought: {capabilities['cot_enabled']}")
    print("\nFeatures:")
    for feature in capabilities["features"][:5]:
        print(f"• {feature}")

    print("\nMetrics:")
    metrics = capabilities["metrics"]
    print(f"• Total API Calls: {metrics['total_api_calls']}")
    print(f"• Total AI Calls: {metrics['total_ai_calls']}")
    print(f"• Cache Size: {metrics['cache_size']}")

    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_enhanced_research())
