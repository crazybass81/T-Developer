#!/usr/bin/env python3
"""RequirementAnalyzer 단독 테스트 - 요구사항 분석 검증."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from pprint import pprint

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from backend.packages.agents.requirement_analyzer import RequirementAnalyzer
from backend.packages.agents.base import AgentTask
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType


async def test_requirement_analyzer():
    """RequirementAnalyzer 상세 테스트."""
    print("="*80)
    print("🔍 RequirementAnalyzer 검증 테스트")
    print("="*80)
    
    # 메모리 허브 초기화
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    # RequirementAnalyzer 생성
    analyzer = RequirementAnalyzer(memory_hub=memory_hub)
    
    # 테스트 요구사항 1: 간단한 API 엔드포인트
    requirement1 = """
    Create a REST API endpoint for user management:
    - GET /users - List all users with pagination
    - GET /users/{id} - Get user by ID
    - POST /users - Create new user
    - PUT /users/{id} - Update user
    - DELETE /users/{id} - Delete user
    
    Requirements:
    - Use FastAPI framework
    - Include input validation
    - Add authentication using JWT
    - Implement rate limiting
    - Add comprehensive error handling
    - Include OpenAPI documentation
    - Write unit tests with 80% coverage
    """
    
    print("\n📋 테스트 1: API 엔드포인트 요구사항")
    print("-"*50)
    print(requirement1[:200] + "...")
    
    # 분석 실행
    task1 = AgentTask(
        intent="analyze_requirement",
        inputs={"requirements": requirement1}
    )
    
    print("\n🔄 분석 중...")
    result1 = await analyzer.execute(task1)
    
    print(f"\n✅ 분석 결과:")
    print(f"   - 성공 여부: {result1.success}")
    print(f"   - 상태: {result1.status}")
    
    if result1.success and result1.data:
        data = result1.data
        
        # 분석 결과 상세 출력
        print(f"\n📊 상세 분석:")
        
        # 1. 명세서 (specification)
        if 'specification' in data:
            spec = data['specification']
            print(f"\n   [명세서]")
            print(f"   • 기능 요구사항: {len(spec.get('functional_requirements', []))}개")
            for i, req in enumerate(spec.get('functional_requirements', [])[:3], 1):
                print(f"     {i}. {req[:80]}...")
            
            print(f"   • 비기능 요구사항: {len(spec.get('non_functional_requirements', []))}개")
            for i, req in enumerate(spec.get('non_functional_requirements', [])[:3], 1):
                print(f"     {i}. {req[:80]}...")
            
            print(f"   • 컴포넌트: {len(spec.get('components', []))}개")
            for comp in spec.get('components', [])[:3]:
                print(f"     - {comp.get('name')}: {comp.get('responsibility', '')[:60]}...")
            
            print(f"   • 의존성: {len(spec.get('dependencies', []))}개")
            for dep in spec.get('dependencies', [])[:5]:
                print(f"     - {dep}")
            
            print(f"   • 복잡도: {spec.get('complexity', 'N/A')}")
            print(f"   • 우선순위: {spec.get('priority', 'N/A')}")
            print(f"   • 예상 공수: {spec.get('estimated_effort', 'N/A')}")
            
            print(f"   • 위험 요소: {len(spec.get('risks', []))}개")
            for risk in spec.get('risks', [])[:2]:
                print(f"     - {risk[:80]}...")
            
            print(f"   • 성공 기준: {len(spec.get('success_criteria', []))}개")
            for criteria in spec.get('success_criteria', [])[:2]:
                print(f"     - {criteria[:80]}...")
        
        # 2. 타당성 평가 (feasibility)
        if 'feasibility' in data:
            feasibility = data['feasibility']
            print(f"\n   [타당성 평가]")
            print(f"   • 전체 점수: {feasibility.get('overall_score', 0):.2f}")
            print(f"   • 기술적 타당성: {feasibility.get('technical_feasibility', False)}")
            print(f"   • 리소스 가용성: {feasibility.get('resource_availability', False)}")
            print(f"   • 시간 타당성: {feasibility.get('time_feasibility', False)}")
            print(f"   • 위험 수준: {feasibility.get('risk_level', 'N/A')}")
            
            if feasibility.get('warnings'):
                print(f"   • 경고: {len(feasibility['warnings'])}개")
                for warn in feasibility['warnings'][:2]:
                    print(f"     - {warn[:80]}...")
        
        # 3. AI 분석 (analysis)
        if 'analysis' in data:
            analysis = data['analysis']
            print(f"\n   [AI 분석 요약]")
            if isinstance(analysis, dict):
                for key in ['functional_requirements', 'non_functional_requirements'][:1]:
                    if key in analysis and analysis[key]:
                        print(f"   • {key}: {len(analysis[key])}개 항목")
    
    # 결과를 파일로 저장
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"requirement_analysis_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "requirement": requirement1,
            "result": {
                "success": result1.success,
                "status": str(result1.status),
                "data": result1.data,
                "metadata": result1.metadata
            }
        }, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n💾 분석 결과 저장: {output_file.absolute()}")
    
    # 테스트 2: 복잡한 시스템 요구사항
    print("\n" + "="*80)
    requirement2 = """
    Build a comprehensive e-commerce platform with the following features:
    
    1. User Management
       - Multi-factor authentication
       - Role-based access control (Admin, Seller, Customer)
       - Social login integration
    
    2. Product Catalog
       - Advanced search with filters
       - Product recommendations using ML
       - Real-time inventory tracking
    
    3. Order Processing
       - Shopping cart with session management
       - Multiple payment gateway integration
       - Order tracking and notifications
    
    4. Analytics Dashboard
       - Real-time sales metrics
       - Customer behavior analysis
       - Predictive analytics for demand forecasting
    
    Technical Requirements:
    - Microservices architecture
    - Kubernetes deployment
    - GraphQL API
    - Event-driven architecture with Kafka
    - PostgreSQL for transactional data
    - MongoDB for product catalog
    - Redis for caching
    - Elasticsearch for search
    """
    
    print("📋 테스트 2: 복잡한 e-commerce 시스템")
    print("-"*50)
    print(requirement2[:200] + "...")
    
    task2 = AgentTask(
        intent="analyze_requirement",
        inputs={"requirements": requirement2}
    )
    
    print("\n🔄 분석 중...")
    result2 = await analyzer.execute(task2)
    
    if result2.success and result2.data:
        spec2 = result2.data.get('specification', {})
        print(f"\n✅ 분석 완료:")
        print(f"   • 기능 요구사항: {len(spec2.get('functional_requirements', []))}개")
        print(f"   • 컴포넌트: {len(spec2.get('components', []))}개")
        print(f"   • 복잡도: {spec2.get('complexity', 'N/A')}")
        print(f"   • 예상 공수: {spec2.get('estimated_effort', 'N/A')}")
    
    # 메모리에서 저장된 분석 결과 확인
    print("\n" + "="*80)
    print("📦 메모리 허브 확인")
    print("-"*50)
    
    # 저장된 분석 결과 검색
    stored_results = await memory_hub.search(
        query="requirement",
        context_type=ContextType.A_CTX,
        limit=5
    )
    
    print(f"저장된 분석 결과: {len(stored_results)}개")
    for result in stored_results:
        print(f"  - Key: {result.get('key', 'N/A')}")
        print(f"    Created: {result.get('created_at', 'N/A')}")
    
    # 정리
    await memory_hub.shutdown()
    print("\n✅ 테스트 완료!")


if __name__ == "__main__":
    import os
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    print("🔧 환경 설정:")
    print(f"   - AWS Region: {os.environ.get('AWS_DEFAULT_REGION')}")
    print(f"   - Python: {sys.version.split()[0]}")
    print()
    
    asyncio.run(test_requirement_analyzer())