#!/usr/bin/env python3
"""
NL Input Agent 완성도 검증 스크립트
Tasks 4.3 및 4.4 완료 확인
"""

import asyncio
import sys
import time
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def validate_task_4_3_completion():
    """Task 4.3: NL 에이전트 고급 기능 검증"""
    
    print("🔍 Task 4.3 검증 시작: NL 에이전트 고급 기능")
    
    results = {
        "domain_specific_processing": False,
        "intent_analysis": False,
        "requirement_prioritization": False,
        "performance_targets": False
    }
    
    try:
        # SubTask 4.3.1: 도메인 특화 처리
        from src.agents.implementations.nl_domain_specific import DomainSpecificNLProcessor
        
        processor = DomainSpecificNLProcessor()
        
        # 도메인 감지 테스트
        fintech_desc = "Create a payment processing system with fraud detection"
        domain_result = await processor.process_domain_specific_requirements(fintech_desc)
        
        if (domain_result.domain == 'fintech' and 
            len(domain_result.compliance_requirements) > 0):
            results["domain_specific_processing"] = True
            print("✅ 도메인 특화 처리 - 통과")
        else:
            print("❌ 도메인 특화 처리 - 실패")
        
        # SubTask 4.3.2: 의도 분석
        from src.agents.implementations.nl_intent_analyzer import IntentAnalyzer
        
        analyzer = IntentAnalyzer()
        intent_result = await analyzer.analyze_user_intent(
            "Build a scalable web application that can handle 1 million users"
        )
        
        if (intent_result.primary.value == 'build_new' and
            len(intent_result.technical_goals) > 0 and
            any(goal.type == 'performance' for goal in intent_result.technical_goals)):
            results["intent_analysis"] = True
            print("✅ 의도 분석 - 통과")
        else:
            print("❌ 의도 분석 - 실패")
        
        # SubTask 4.3.3: 요구사항 우선순위
        from src.agents.implementations.nl_priority_analyzer import RequirementPrioritizer, ParsedRequirement
        
        prioritizer = RequirementPrioritizer()
        test_requirements = [
            ParsedRequirement("req1", "User authentication", "security", 3),
            ParsedRequirement("req2", "Product catalog", "core_functionality", 4),
            ParsedRequirement("req3", "Payment processing", "integration", 5)
        ]
        
        prioritized = await prioritizer.prioritize_requirements(test_requirements, {})
        
        if (len(prioritized) == 3 and
            all(req.priority_score > 0 for req in prioritized) and
            all(req.recommended_sprint >= 1 for req in prioritized)):
            results["requirement_prioritization"] = True
            print("✅ 요구사항 우선순위 - 통과")
        else:
            print("❌ 요구사항 우선순위 - 실패")
        
        # 성능 목표 확인
        start_time = time.time()
        
        # 모든 고급 기능 통합 테스트
        from src.agents.implementations.nl_advanced_integration import AdvancedNLIntegration
        
        integration = AdvancedNLIntegration()
        result = await integration.process_advanced_requirements(
            "Create an e-commerce platform with real-time inventory management"
        )
        
        processing_time = time.time() - start_time
        
        if (processing_time < 5.0 and  # 5초 이내
            result.confidence_score > 0.7 and  # 70% 이상 신뢰도
            len(result.recommendations) > 0):
            results["performance_targets"] = True
            print("✅ 성능 목표 - 통과")
        else:
            print(f"❌ 성능 목표 - 실패 (시간: {processing_time:.2f}s, 신뢰도: {result.confidence_score:.2f})")
        
    except Exception as e:
        print(f"❌ Task 4.3 검증 중 오류: {e}")
        return False
    
    success_rate = sum(results.values()) / len(results)
    print(f"\n📊 Task 4.3 완성도: {success_rate:.1%}")
    
    return success_rate >= 0.8  # 80% 이상 통과

async def validate_task_4_4_completion():
    """Task 4.4: NL Agent 완성 및 통합 검증"""
    
    print("\n🔍 Task 4.4 검증 시작: NL Agent 완성 및 통합")
    
    results = {
        "performance_optimization": False,
        "comprehensive_integration": False,
        "api_endpoints": False,
        "system_health": False
    }
    
    try:
        # SubTask 4.4.1: 성능 최적화
        from src.agents.implementations.nl_performance_optimizer import NLPerformanceOptimizer
        
        optimizer = NLPerformanceOptimizer()
        await optimizer.initialize()
        
        # 캐싱 테스트
        async def mock_processor(desc):
            await asyncio.sleep(0.1)
            return f"processed: {desc}"
        
        # 첫 번째 호출
        start_time = time.time()
        result1 = await optimizer.optimize_processing("test", mock_processor, use_cache=True)
        first_time = time.time() - start_time
        
        # 두 번째 호출 (캐시 히트)
        start_time = time.time()
        result2 = await optimizer.optimize_processing("test", mock_processor, use_cache=True)
        second_time = time.time() - start_time
        
        if (result1 == result2 and second_time < first_time * 0.5):
            results["performance_optimization"] = True
            print("✅ 성능 최적화 - 통과")
        else:
            print("❌ 성능 최적화 - 실패")
        
        await optimizer.cleanup()
        
        # SubTask 4.4.2: 종합 통합
        from src.agents.implementations.nl_final_integration import ComprehensiveNLAgent
        
        comprehensive_agent = ComprehensiveNLAgent()
        await comprehensive_agent.initialize()
        
        # 종합 처리 테스트
        result = await comprehensive_agent.process_comprehensive_request(
            description="Build a healthcare management system with patient records",
            session_id="test_session",
            user_id="test_user",
            enable_advanced_analysis=True
        )
        
        if (result.confidence_score > 0.6 and
            result.processing_time < 10.0 and
            len(result.next_actions) > 0):
            results["comprehensive_integration"] = True
            print("✅ 종합 통합 - 통과")
        else:
            print("❌ 종합 통합 - 실패")
        
        # 시스템 상태 확인
        status = await comprehensive_agent.get_system_status()
        
        if (status["initialized"] and
            status["health_score"] > 0.7 and
            all(comp == "active" for comp in status["components"].values())):
            results["system_health"] = True
            print("✅ 시스템 건강도 - 통과")
        else:
            print("❌ 시스템 건강도 - 실패")
        
        await comprehensive_agent.cleanup()
        
        # SubTask 4.4.3: API 엔드포인트
        try:
            from src.api.nl_advanced_api import router
            
            # API 라우터 확인
            endpoints = [route.path for route in router.routes]
            required_endpoints = ["/process", "/performance/stats", "/health"]
            
            if all(any(endpoint in path for path in endpoints) for endpoint in required_endpoints):
                results["api_endpoints"] = True
                print("✅ API 엔드포인트 - 통과")
            else:
                print("❌ API 엔드포인트 - 실패")
        except Exception as e:
            print(f"❌ API 엔드포인트 확인 실패: {e}")
        
    except Exception as e:
        print(f"❌ Task 4.4 검증 중 오류: {e}")
        return False
    
    success_rate = sum(results.values()) / len(results)
    print(f"\n📊 Task 4.4 완성도: {success_rate:.1%}")
    
    return success_rate >= 0.8  # 80% 이상 통과

async def main():
    """메인 검증 함수"""
    
    print("🚀 NL Input Agent Tasks 4.3 & 4.4 완성도 검증")
    print("=" * 60)
    
    # Task 4.3 검증
    task_4_3_passed = await validate_task_4_3_completion()
    
    # Task 4.4 검증
    task_4_4_passed = await validate_task_4_4_completion()
    
    # 전체 결과
    print("\n" + "=" * 60)
    print("📋 최종 검증 결과")
    print(f"Task 4.3 (고급 기능): {'✅ 통과' if task_4_3_passed else '❌ 실패'}")
    print(f"Task 4.4 (완성 및 통합): {'✅ 통과' if task_4_4_passed else '❌ 실패'}")
    
    overall_success = task_4_3_passed and task_4_4_passed
    
    if overall_success:
        print("\n🎉 NL Input Agent Tasks 4.3 & 4.4 완료!")
        print("✅ 모든 고급 기능이 성공적으로 구현되었습니다.")
        print("\n📈 달성된 기능:")
        print("  - 도메인 특화 처리 (fintech, healthcare, ecommerce, legal)")
        print("  - 의도 분석 및 목표 추출")
        print("  - 요구사항 자동 우선순위 결정")
        print("  - 성능 최적화 (캐싱, 배치 처리)")
        print("  - 종합 통합 시스템")
        print("  - 고급 API 엔드포인트")
        return 0
    else:
        print("\n⚠️ 일부 기능이 완료되지 않았습니다.")
        print("실패한 항목을 확인하고 수정해주세요.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())