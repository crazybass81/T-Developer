import pytest
import asyncio
from unittest.mock import Mock, patch
import time

from src.agents.implementations.nl_advanced_integration import AdvancedNLIntegration
from src.agents.implementations.nl_performance_optimizer import NLPerformanceOptimizer

@pytest.mark.asyncio
class TestAdvancedNLIntegration:
    """고급 NL 통합 테스트"""

    @pytest.fixture
    async def advanced_nl(self):
        integration = AdvancedNLIntegration()
        yield integration

    @pytest.fixture
    def test_descriptions(self):
        return {
            "fintech": "Create a payment processing system with fraud detection and PCI compliance",
            "healthcare": "Build a patient management system with HIPAA compliance and HL7 integration",
            "ecommerce": "Develop an online shopping platform with product catalog and checkout",
            "complex": "Build a scalable microservices platform that can handle 1 million users with real-time analytics"
        }

    async def test_domain_detection_accuracy(self, advanced_nl, test_descriptions):
        """도메인 감지 정확도 테스트"""
        
        for domain, description in test_descriptions.items():
            if domain == "complex":
                continue
                
            result = await advanced_nl.process_advanced_requirements(description)
            
            assert result.domain_analysis.domain == domain
            assert result.confidence_score > 0.7
            assert len(result.domain_analysis.compliance_requirements) > 0

    async def test_intent_analysis(self, advanced_nl, test_descriptions):
        """의도 분석 테스트"""
        
        result = await advanced_nl.process_advanced_requirements(
            test_descriptions["complex"]
        )
        
        assert result.intent_analysis.primary.value == "build_new"
        assert result.intent_analysis.confidence > 0.5
        assert len(result.intent_analysis.technical_goals) > 0
        
        # 성능 목표 확인
        perf_goals = [g for g in result.intent_analysis.technical_goals if g.type == "performance"]
        assert len(perf_goals) > 0
        assert "1000000" in perf_goals[0].target_state

    async def test_requirement_prioritization(self, advanced_nl, test_descriptions):
        """요구사항 우선순위 테스트"""
        
        result = await advanced_nl.process_advanced_requirements(
            test_descriptions["ecommerce"]
        )
        
        assert len(result.prioritized_requirements) > 0
        
        # 우선순위 순서 확인
        priorities = [req.priority_score for req in result.prioritized_requirements]
        assert priorities == sorted(priorities, reverse=True)
        
        # 스프린트 할당 확인
        sprints = [req.recommended_sprint for req in result.prioritized_requirements]
        assert all(sprint >= 1 for sprint in sprints)

    async def test_performance_targets(self, advanced_nl, test_descriptions):
        """성능 목표 테스트"""
        
        start_time = time.time()
        
        result = await advanced_nl.process_advanced_requirements(
            test_descriptions["fintech"]
        )
        
        processing_time = time.time() - start_time
        
        # 성능 목표 확인
        assert processing_time < 3.0  # 3초 이내
        assert result.confidence_score > 0.8  # 80% 이상 신뢰도
        assert len(result.recommendations) > 0

    async def test_parallel_processing(self, advanced_nl, test_descriptions):
        """병렬 처리 테스트"""
        
        tasks = []
        for description in test_descriptions.values():
            task = advanced_nl.process_advanced_requirements(description)
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # 병렬 처리로 시간 단축 확인
        assert total_time < 5.0  # 5초 이내에 모든 처리 완료
        assert len(results) == len(test_descriptions)
        assert all(r.confidence_score > 0.5 for r in results)

@pytest.mark.asyncio
class TestNLPerformanceOptimizer:
    """NL 성능 최적화 테스트"""

    @pytest.fixture
    async def optimizer(self):
        opt = NLPerformanceOptimizer()
        await opt.initialize()
        yield opt
        await opt.cleanup()

    async def test_caching_functionality(self, optimizer):
        """캐싱 기능 테스트"""
        
        async def mock_processor(description):
            await asyncio.sleep(0.1)  # 처리 시간 시뮬레이션
            return f"processed: {description}"
        
        description = "test description"
        
        # 첫 번째 호출 (캐시 미스)
        start_time = time.time()
        result1 = await optimizer.optimize_processing(
            description, mock_processor, use_cache=True
        )
        first_call_time = time.time() - start_time
        
        # 두 번째 호출 (캐시 히트)
        start_time = time.time()
        result2 = await optimizer.optimize_processing(
            description, mock_processor, use_cache=True
        )
        second_call_time = time.time() - start_time
        
        # 결과 검증
        assert result1 == result2
        assert second_call_time < first_call_time * 0.5  # 50% 이상 빠름
        
        stats = optimizer.get_performance_stats()
        assert stats['cache_hit_rate'] > 0

    async def test_batch_processing(self, optimizer):
        """배치 처리 테스트"""
        
        async def mock_processor(description):
            await asyncio.sleep(0.05)
            return f"batch processed: {description}"
        
        # 여러 요청 동시 처리
        tasks = []
        for i in range(5):
            task = optimizer.optimize_processing(
                f"short description {i}",
                mock_processor,
                use_batching=True
            )
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # 배치 처리 효과 확인
        assert len(results) == 5
        assert all("batch processed" in result for result in results)
        assert total_time < 0.3  # 배치 처리로 시간 단축

    async def test_performance_metrics(self, optimizer):
        """성능 메트릭 테스트"""
        
        async def mock_processor(description):
            return f"processed: {description}"
        
        # 여러 요청 처리
        for i in range(10):
            await optimizer.optimize_processing(
                f"description {i}",
                mock_processor
            )
        
        stats = optimizer.get_performance_stats()
        
        # 메트릭 검증
        assert stats['total_requests'] == 10
        assert 'cache_hit_rate' in stats
        assert 'error_rate' in stats
        assert stats['error_rate'] == 0  # 에러 없음

    async def test_error_handling(self, optimizer):
        """에러 처리 테스트"""
        
        async def failing_processor(description):
            raise ValueError("Processing failed")
        
        with pytest.raises(ValueError):
            await optimizer.optimize_processing(
                "test description",
                failing_processor
            )
        
        stats = optimizer.get_performance_stats()
        assert stats['error_rate'] > 0

@pytest.mark.integration
class TestNLAdvancedAPI:
    """고급 NL API 통합 테스트"""

    async def test_api_response_format(self):
        """API 응답 형식 테스트"""
        # FastAPI 테스트 클라이언트를 사용한 실제 API 테스트
        # 실제 구현에서는 TestClient 사용
        pass

    async def test_api_performance(self):
        """API 성능 테스트"""
        # 부하 테스트 및 응답 시간 측정
        pass