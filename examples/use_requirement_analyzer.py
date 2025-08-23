#!/usr/bin/env python3
"""RequirementAnalyzer 사용 예시.

이 예시는 RequirementAnalyzer를 사용하여 자연어 요구사항을 분석하는 방법을 보여줍니다.
"""

import asyncio
import sys
from pathlib import Path

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from backend.packages.memory.hub import MemoryHub
from backend.packages.agents.requirement_analyzer import RequirementAnalyzer


async def analyze_user_requirements():
    """사용자 요구사항 분석 예시."""
    
    print("📋 RequirementAnalyzer 사용 예시")
    print("=" * 60)
    
    # 시스템 초기화
    print("\n초기화 중...")
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    analyzer = RequirementAnalyzer(memory_hub=memory_hub)
    print("✅ 시스템 준비 완료\n")
    
    # 분석할 요구사항
    requirements = """
    우리는 온라인 쇼핑몰을 위한 재고 관리 시스템이 필요합니다.
    
    주요 기능:
    1. 실시간 재고 추적
    2. 자동 재주문 시스템 (재고가 임계값 이하로 떨어지면)
    3. 다중 창고 지원
    4. 재고 이동 추적
    5. 재고 보고서 생성 (일별, 주별, 월별)
    6. 바코드 스캔 지원
    7. 공급업체 관리
    
    기술 요구사항:
    - REST API로 구현
    - PostgreSQL 데이터베이스 사용
    - Redis 캐싱
    - 실시간 알림을 위한 WebSocket
    - Docker 컨테이너화
    - 99.9% 가용성 목표
    """
    
    print("📝 요구사항:")
    print("-" * 40)
    print(requirements[:200] + "...")
    print("-" * 40)
    
    # 요구사항 분석
    print("\n🔍 분석 중...")
    result = await analyzer.execute({
        "requirements": requirements,
        "project_context": {
            "name": "Inventory Management System",
            "type": "E-commerce Backend",
            "industry": "Retail"
        },
        "focus_area": "backend system"
    })
    
    if result["success"]:
        print("\n✅ 분석 완료!")
        
        spec = result["specification"]
        feasibility = result["feasibility"]
        
        print("\n📊 분석 결과:")
        print(f"  • 기능 요구사항: {len(spec['functional_requirements'])}개")
        print(f"  • 비기능 요구사항: {len(spec['non_functional_requirements'])}개")
        print(f"  • 필요 컴포넌트: {len(spec['components'])}개")
        print(f"  • 복잡도: {spec['complexity']}")
        print(f"  • 우선순위: {spec['priority']}")
        
        print("\n🏗️ 주요 컴포넌트:")
        for comp in spec['components'][:3]:
            if isinstance(comp, dict):
                print(f"  • {comp.get('name', 'Unknown')}: {comp.get('responsibility', '')[:50]}")
        
        print(f"\n📈 구현 가능성:")
        print(f"  • 전체 점수: {feasibility['overall_score']:.1%}")
        print(f"  • 위험 수준: {feasibility['risk_level']}")
        
        if feasibility.get('recommendations'):
            print("\n💡 권장사항:")
            for rec in feasibility['recommendations'][:2]:
                print(f"  • {rec}")
    
    else:
        print(f"\n❌ 분석 실패: {result.get('error')}")
    
    # 정리
    await memory_hub.shutdown()
    print("\n" + "=" * 60)
    print("예시 완료!")


if __name__ == "__main__":
    asyncio.run(analyze_user_requirements())