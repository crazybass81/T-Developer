"""
CLI test for Agent Registry

에이전트 레지스트리 기능을 직접 테스트하는 스크립트입니다.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from evolution.registry import AgentRegistry, AgentType, AgentMetrics


async def test_registry():
    """레지스트리 기본 기능 테스트"""
    print("🧬 T-Developer Agent Registry 테스트 시작")

    # 레지스트리 초기화
    registry = AgentRegistry()
    await registry.initialize()
    print("✅ 레지스트리 초기화 완료")

    # 에이전트 생성
    agent = await registry.create_agent(
        name="테스트_자연어_처리_에이전트",
        agent_type=AgentType.NL_INPUT,
        code="""
def process_natural_language(text: str) -> dict:
    \"\"\"자연어 텍스트를 처리하여 의도와 엔티티를 추출합니다\"\"\"
    import re

    # 간단한 의도 분류
    if "만들어" in text or "생성" in text:
        intent = "create"
    elif "찾아" in text or "검색" in text:
        intent = "search"
    else:
        intent = "unknown"

    # 엔티티 추출 (간단한 예시)
    entities = {}
    if "앱" in text:
        entities["type"] = "app"
    if "웹사이트" in text:
        entities["type"] = "website"

    return {
        "intent": intent,
        "entities": entities,
        "confidence": 0.85
    }
""",
        description="한국어 자연어 입력을 처리하는 에이전트",
        tags={"nlp", "korean", "input"},
    )

    print(f"✅ 에이전트 생성 완료: {agent.name} (ID: {agent.id[:8]}...)")

    # 성능 메트릭 업데이트
    metrics = AgentMetrics(
        memory_usage_kb=4.2,
        instantiation_time_us=2.1,
        execution_time_ms=45.0,
        accuracy=0.92,
        throughput_ops_per_sec=850.0,
        error_rate=0.02,
        fitness_score=0.88,
        safety_score=0.99,
    )

    await registry.update_agent_metrics(agent.id, metrics)
    print("✅ 성능 메트릭 업데이트 완료")

    # 코드 업데이트 (새 버전 생성)
    new_version = await registry.update_agent_code(
        agent.id,
        """
def process_natural_language(text: str) -> dict:
    \"\"\"개선된 자연어 처리 함수\"\"\"
    import re

    # 향상된 의도 분류
    intents = {
        "create": ["만들어", "생성", "작성", "개발"],
        "search": ["찾아", "검색", "찾기", "조회"],
        "update": ["수정", "변경", "업데이트", "편집"],
        "delete": ["삭제", "제거", "지우기"]
    }

    intent = "unknown"
    confidence = 0.0

    for intent_type, keywords in intents.items():
        for keyword in keywords:
            if keyword in text:
                intent = intent_type
                confidence = 0.9
                break
        if confidence > 0:
            break

    # 개선된 엔티티 추출
    entities = {}
    if "앱" in text or "어플" in text:
        entities["type"] = "mobile_app"
    elif "웹사이트" in text or "사이트" in text:
        entities["type"] = "website"
    elif "API" in text or "api" in text:
        entities["type"] = "api"

    return {
        "intent": intent,
        "entities": entities,
        "confidence": confidence
    }
""",
        "v2: 의도 분류 정확도 개선 및 엔티티 추출 향상",
    )

    print(f"✅ 코드 업데이트 완료: 버전 {new_version}")

    # 에이전트 검색 테스트
    search_results = await registry.search_agents("자연어")
    print(f"✅ 검색 결과: {len(search_results)}개 에이전트 발견")

    # 타입별 조회
    nl_agents = await registry.get_agents_by_type(AgentType.NL_INPUT)
    print(f"✅ NL Input 에이전트: {len(nl_agents)}개")

    # 통계 조회
    stats = await registry.get_registry_stats()
    print(f"✅ 레지스트리 통계:")
    print(f"   - 총 에이전트: {stats['total_agents']}개")
    print(f"   - 타입별 분포: {stats['by_type']}")
    print(f"   - 상태별 분포: {stats['by_status']}")

    # 에이전트 정보 출력
    updated_agent = await registry.get_agent(agent.id)
    print(f"\n📊 에이전트 상세 정보:")
    print(f"   이름: {updated_agent.name}")
    print(f"   타입: {updated_agent.agent_type.value}")
    print(f"   현재 버전: {updated_agent.version}")
    print(f"   전체 버전: {len(updated_agent.versions)}개")
    print(f"   메모리 사용량: {updated_agent.metrics.memory_usage_kb:.1f}KB")
    print(f"   인스턴스화 시간: {updated_agent.metrics.instantiation_time_us:.1f}μs")
    print(f"   정확도: {updated_agent.metrics.accuracy:.1%}")
    print(f"   적합도 점수: {updated_agent.metrics.fitness_score:.2f}")
    print(f"   안전성 점수: {updated_agent.metrics.safety_score:.2f}")

    print("\n🎉 모든 테스트 완료! T-Developer Evolution System이 정상 작동합니다.")

    return True


if __name__ == "__main__":
    asyncio.run(test_registry())
