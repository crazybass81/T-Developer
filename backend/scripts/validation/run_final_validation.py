#!/usr/bin/env python3
"""NL Input Agent 최종 검증 스크립트"""

import asyncio
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.implementations.nl_integration import NLInputAgentIntegration


async def main():
    print("🚀 NL Input Agent 최종 검증 시작...")

    integration = NLInputAgentIntegration()

    # 검증 케이스
    test_cases = [
        "간단한 할일 관리 웹 애플리케이션을 만들어주세요",
        "React와 Node.js를 사용한 실시간 채팅 앱",
        "모바일 앱 - iOS/Android 지원, 사진 공유 기능",
    ]

    results = []
    total_time = 0

    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 테스트 {i}/{len(test_cases)}: {case[:50]}...")

        start_time = time.time()
        try:
            result = await integration.process_complete_request([case])
            elapsed = time.time() - start_time
            total_time += elapsed

            success = result["processing_status"] != "error"
            confidence = result.get("confidence_score", 0)

            print(f"   ✅ 성공: {success}")
            print(f"   ⏱️  시간: {elapsed:.2f}s")
            print(f"   🎯 신뢰도: {confidence:.2f}")

            results.append(
                {
                    "case": case,
                    "success": success,
                    "time": elapsed,
                    "confidence": confidence,
                }
            )

        except Exception as e:
            print(f"   ❌ 오류: {e}")
            results.append(
                {
                    "case": case,
                    "success": False,
                    "time": time.time() - start_time,
                    "confidence": 0,
                }
            )

    # 최종 결과
    print(f"\n📊 최종 결과:")
    success_rate = sum(1 for r in results if r["success"]) / len(results)
    avg_time = total_time / len(results)
    avg_confidence = sum(r["confidence"] for r in results) / len(results)

    print(f"   성공률: {success_rate:.1%}")
    print(f"   평균 시간: {avg_time:.2f}s")
    print(f"   평균 신뢰도: {avg_confidence:.2f}")

    # 목표 달성 확인
    print(f"\n🎯 목표 달성:")
    print(f"   응답시간 < 2s: {'✅' if avg_time < 2.0 else '❌'}")
    print(f"   성공률 > 95%: {'✅' if success_rate > 0.95 else '❌'}")
    print(f"   신뢰도 > 0.8: {'✅' if avg_confidence > 0.8 else '❌'}")

    if success_rate > 0.95 and avg_time < 2.0:
        print("\n🎉 Task 4.1 NL Input Agent 완성!")
        return True
    else:
        print("\n⚠️  일부 목표 미달성")
        return False


if __name__ == "__main__":
    asyncio.run(main())
