#!/usr/bin/env python3
"""ExternalResearcher 단독 테스트 - 외부 리서치 검증."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from backend.packages.agents.external_researcher import ExternalResearcher
from backend.packages.agents.base import AgentTask
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType


async def test_external_researcher():
    """ExternalResearcher 상세 테스트."""
    print("="*80)
    print("🔎 ExternalResearcher 검증 테스트")
    print("="*80)
    
    # 메모리 허브 초기화
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    # ExternalResearcher 생성
    researcher = ExternalResearcher(memory_hub=memory_hub)
    
    # 테스트 1: FastAPI 관련 리서치
    topic1 = "FastAPI best practices for production deployment"
    
    print("\n📋 테스트 1: FastAPI 리서치")
    print("-"*50)
    print(f"주제: {topic1}")
    
    # 리서치 실행
    task1 = AgentTask(
        intent="research",
        inputs={
            "topic": topic1,
            "depth": "detailed",
            "sources": ["documentation", "articles", "best_practices"]
        }
    )
    
    print("\n🔄 리서치 진행 중...")
    result1 = await researcher.execute(task1)
    
    print(f"\n✅ 리서치 결과:")
    print(f"   - 성공 여부: {result1.success}")
    print(f"   - 상태: {result1.status}")
    
    if result1.success and result1.data:
        data = result1.data
        
        # 리서치 상세 출력
        print(f"\n📊 리서치 내용:")
        
        if 'findings' in data:
            findings = data['findings']
            print(f"\n   [주요 발견사항] {len(findings)}개")
            for i, finding in enumerate(findings[:5], 1):
                if isinstance(finding, dict):
                    print(f"   {i}. {finding.get('title', 'N/A')}")
                    print(f"      - {finding.get('summary', '')[:100]}...")
                else:
                    print(f"   {i}. {str(finding)[:100]}...")
        
        if 'recommendations' in data:
            recs = data['recommendations']
            print(f"\n   [권장사항] {len(recs)}개")
            for i, rec in enumerate(recs[:5], 1):
                if isinstance(rec, dict):
                    print(f"   {i}. {rec.get('title', rec.get('recommendation', 'N/A'))}")
                else:
                    print(f"   {i}. {str(rec)[:80]}...")
        
        if 'sources' in data:
            sources = data['sources']
            print(f"\n   [참고 자료] {len(sources)}개")
            for i, source in enumerate(sources[:3], 1):
                if isinstance(source, dict):
                    print(f"   {i}. {source.get('title', source.get('url', 'N/A'))}")
                else:
                    print(f"   {i}. {source}")
        
        if 'summary' in data:
            print(f"\n   [요약]")
            print(f"   {data['summary'][:200]}...")
    
    # 결과를 파일로 저장
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"research_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "topic": topic1,
            "result": {
                "success": result1.success,
                "status": str(result1.status),
                "data": result1.data,
                "metadata": result1.metadata
            }
        }, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n💾 리서치 결과 저장: {output_file.absolute()}")
    
    # 테스트 2: 마이크로서비스 마이그레이션 리서치
    print("\n" + "="*80)
    topic2 = "Migrating monolithic Django application to microservices architecture patterns and strategies"
    
    print("📋 테스트 2: 마이크로서비스 마이그레이션 리서치")
    print("-"*50)
    print(f"주제: {topic2[:80]}...")
    
    task2 = AgentTask(
        intent="research",
        inputs={
            "topic": topic2,
            "depth": "comprehensive",
            "sources": ["case_studies", "patterns", "tools"],
            "focus_areas": ["data migration", "service boundaries", "zero downtime"]
        }
    )
    
    print("\n🔄 리서치 진행 중...")
    result2 = await researcher.execute(task2)
    
    if result2.success and result2.data:
        print(f"\n✅ 마이그레이션 리서치 완료:")
        print(f"   • 발견사항: {len(result2.data.get('findings', []))}개")
        print(f"   • 권장사항: {len(result2.data.get('recommendations', []))}개")
        print(f"   • 참고자료: {len(result2.data.get('sources', []))}개")
    
    # 메모리에서 저장된 리서치 확인
    print("\n" + "="*80)
    print("📦 메모리 허브 확인")
    print("-"*50)
    
    # 저장된 리서치 검색
    stored_research = await memory_hub.search(
        context_type=ContextType.U_CTX,  # Research is usually stored in U_CTX
        limit=5
    )
    
    print(f"저장된 리서치: {len(stored_research)}개")
    for research in stored_research:
        print(f"  - Key: {research.get('key', 'N/A')}")
        print(f"    Created: {research.get('created_at', 'N/A')}")
    
    # 정리
    await memory_hub.shutdown()
    print("\n✅ ExternalResearcher 테스트 완료!")


if __name__ == "__main__":
    import os
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    print("🔧 환경 설정:")
    print(f"   - AWS Region: {os.environ.get('AWS_DEFAULT_REGION')}")
    print(f"   - Python: {sys.version.split()[0]}")
    print()
    
    asyncio.run(test_external_researcher())