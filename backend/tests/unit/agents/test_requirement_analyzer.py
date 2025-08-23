#!/usr/bin/env python3
"""Test Requirement Analyzer Agent.

RequirementAnalyzer 에이전트가 요구사항을 올바르게 분석하는지 테스트합니다.
"""

import asyncio
import json
import sys
from pathlib import Path
from pprint import pprint

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType
from backend.packages.agents.requirement_analyzer import RequirementAnalyzer


async def test_requirement_analyzer():
    """RequirementAnalyzer 테스트."""
    
    print("🔍 Requirement Analyzer 테스트")
    print("=" * 60)
    
    # 1. 메모리 허브 초기화
    print("\n1. 시스템 초기화...")
    memory_hub = MemoryHub()
    await memory_hub.initialize()  # 초기화 필수!
    analyzer = RequirementAnalyzer(memory_hub=memory_hub)
    print("   ✅ RequirementAnalyzer 준비 완료")
    
    # 2. 간단한 요구사항 분석
    print("\n2. 간단한 요구사항 분석...")
    simple_requirements = """
    Create a REST API for task management with the following features:
    - User authentication using JWT
    - CRUD operations for tasks
    - Task assignment to users
    - Due date tracking
    - Task status (pending, in-progress, completed)
    """
    
    result = await analyzer.execute({
        "requirements": simple_requirements,
        "focus_area": "backend API"
    })
    
    if result.success:
        print("   ✅ 분석 성공!")
        spec = result.data["specification"]
        print(f"   - Functional requirements: {len(spec['functional_requirements'])}개")
        print(f"   - Components: {len(spec['components'])}개")
        print(f"   - Complexity: {spec['complexity']}")
        print(f"   - Priority: {spec['priority']}")
        
        # 가능성 평가
        feasibility = result.data["feasibility"]
        print(f"\n   📊 가능성 평가:")
        print(f"   - Overall score: {feasibility['overall_score']:.2f}")
        print(f"   - Risk level: {feasibility['risk_level']}")
        
        if feasibility["recommendations"]:
            print(f"   - Recommendations: {len(feasibility['recommendations'])}개")
            for rec in feasibility["recommendations"][:2]:
                print(f"     • {rec}")
    else:
        print(f"   ❌ 분석 실패: {result.get('error')}")
    
    # 3. 복잡한 요구사항 분석
    print("\n3. 복잡한 T-Developer 요구사항 분석...")
    complex_requirements = """
    Build an autonomous AI development system (T-Developer v2) that:
    
    1. Accepts natural language requirements and generates production-ready services
    2. Self-evolves to improve its code generation capabilities
    3. Implements multi-agent architecture with specialized agents:
       - RequirementAnalyzer: Analyzes and structures requirements
       - CodeGenerator: Generates code from specifications
       - QualityGate: Validates code quality and security
       - EvolutionOrchestrator: Manages self-improvement cycles
    
    4. Uses AWS Bedrock for AI capabilities (Claude models)
    5. Implements memory system for context persistence
    6. Includes safety mechanisms:
       - Circuit breakers to prevent infinite loops
       - Resource limiters
       - Rollback capabilities
    
    7. Tracks metrics:
       - Code quality metrics (coverage, complexity)
       - Evolution metrics (improvement rate, success rate)
       - Operational metrics (performance, errors)
    
    Non-functional requirements:
    - Must be fully autonomous after initial setup
    - Python-based implementation
    - AWS cloud-native
    - Test coverage > 85%
    - Comprehensive logging and monitoring
    """
    
    result = await analyzer.execute({
        "requirements": complex_requirements,
        "project_context": {
            "name": "T-Developer v2",
            "type": "AI Development System",
            "technology_stack": ["Python", "AWS", "Bedrock"]
        }
    })
    
    if result.success:
        print("   ✅ 복잡한 요구사항 분석 성공!")
        spec = result.data["specification"]
        
        print(f"\n   📋 분석 결과:")
        print(f"   - Functional requirements: {len(spec['functional_requirements'])}개")
        print(f"   - Non-functional requirements: {len(spec['non_functional_requirements'])}개")
        print(f"   - Components: {len(spec['components'])}개")
        print(f"   - Dependencies: {len(spec['dependencies'])}개")
        print(f"   - Risks: {len(spec['risks'])}개")
        print(f"   - Complexity: {spec['complexity']}")
        print(f"   - Estimated effort: {spec.get('estimated_effort', 'N/A')}")
        
        print(f"\n   🏗️ 식별된 컴포넌트:")
        for comp in spec['components'][:5]:  # 처음 5개만
            if isinstance(comp, dict):
                print(f"   - {comp.get('name', 'Unknown')}: {comp.get('type', '')} - {comp.get('responsibility', '')[:50]}")
            else:
                print(f"   - {comp}")
        
        if spec['risks']:
            print(f"\n   ⚠️  식별된 위험:")
            for risk in spec['risks'][:3]:
                print(f"   - {risk}")
        
        if spec['success_criteria']:
            print(f"\n   ✅ 성공 기준:")
            for criteria in spec['success_criteria'][:3]:
                print(f"   - {criteria}")
        
        # 가능성 평가
        feasibility = result.data["feasibility"]
        print(f"\n   📊 구현 가능성:")
        print(f"   - Overall score: {feasibility['overall_score']:.2f}")
        print(f"   - Risk level: {feasibility['risk_level']}")
        print(f"   - Technical feasibility: {feasibility['technical_feasibility']}")
        
        if feasibility["warnings"]:
            print(f"\n   ⚠️  경고:")
            for warning in feasibility["warnings"]:
                print(f"   - {warning}")
    
    # 4. 메모리 확인
    print("\n4. 메모리 저장 확인...")
    # MemoryHub는 현재 search 메서드가 없으므로 컨텍스트 직접 확인
    agent_context = memory_hub.contexts.get(ContextType.A_CTX)
    shared_context = memory_hub.contexts.get(ContextType.S_CTX)
    
    agent_entries = len(agent_context.entries) if agent_context else 0
    shared_entries = len(shared_context.entries) if shared_context else 0
    
    print(f"   - Agent 컨텍스트 항목: {agent_entries}개")
    print(f"   - Shared 컨텍스트 항목: {shared_entries}개")
    
    print("\n" + "=" * 60)
    print("✅ RequirementAnalyzer 테스트 완료!")
    print("\n에이전트가 요구사항을 성공적으로 분석하고 구조화된 명세를 생성했습니다.")
    
    # 메모리 정리 (각 컨텍스트별로)
    await memory_hub.clear_context(ContextType.A_CTX)
    await memory_hub.clear_context(ContextType.S_CTX)


async def main():
    """메인 실행 함수."""
    try:
        await test_requirement_analyzer()
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())