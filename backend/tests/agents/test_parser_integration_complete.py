# backend/tests/agents/test_parser_integration_complete.py
import pytest
import asyncio
import time
from typing import Dict, List, Any
from unittest.mock import Mock, patch, AsyncMock

from parser_agent import ParserAgent
from parser_integration_tests import ParserIntegrationTester
from parser_performance_monitor import ParserPerformanceMonitor
from parser_validation_framework import ParserValidationFramework

@pytest.mark.integration
class TestParserIntegrationComplete:
    """Parser Agent 완전 통합 테스트"""

    @pytest.fixture
    async def parser_system(self):
        """완전한 파서 시스템 설정"""
        parser_agent = ParserAgent()
        integration_tester = ParserIntegrationTester()
        performance_monitor = ParserPerformanceMonitor()
        validation_framework = ParserValidationFramework()
        
        await parser_agent.initialize()
        await integration_tester.setup()
        
        yield {
            'parser': parser_agent,
            'tester': integration_tester,
            'monitor': performance_monitor,
            'validator': validation_framework
        }
        
        await parser_agent.cleanup()
        await integration_tester.teardown()

    @pytest.fixture
    def comprehensive_test_cases(self):
        """포괄적인 테스트 케이스"""
        return [
            {
                'name': 'Simple Web Application',
                'description': 'Build a simple web application with user authentication',
                'expected_functional': 3,
                'expected_non_functional': 2,
                'complexity': 'low'
            },
            {
                'name': 'E-commerce Platform',
                'description': '''
                Create a comprehensive e-commerce platform with:
                - User registration and authentication with OAuth 2.0
                - Product catalog with search and filtering capabilities
                - Shopping cart with session persistence
                - Order processing and payment integration with Stripe
                - Admin dashboard for inventory management
                - Customer reviews and ratings system
                
                Performance requirements:
                - Support 10,000 concurrent users
                - Response time under 200ms for product searches
                - 99.9% uptime SLA
                
                Security requirements:
                - PCI DSS compliance for payment processing
                - Data encryption at rest and in transit
                - Role-based access control
                ''',
                'expected_functional': 15,
                'expected_non_functional': 8,
                'complexity': 'high'
            },
            {
                'name': 'Healthcare Management System',
                'description': '''
                Develop a HIPAA-compliant healthcare management system:
                
                Core Features:
                - Patient registration and medical records management
                - Appointment scheduling with calendar integration
                - Prescription management and drug interaction checking
                - Billing and insurance claim processing
                - Lab results integration
                - Telemedicine video consultation platform
                
                Compliance Requirements:
                - HIPAA compliance for patient data protection
                - Audit logging for all data access
                - Role-based access control for medical staff
                - Data backup and disaster recovery
                
                Integration Requirements:
                - HL7 FHIR standard for medical data exchange
                - Integration with insurance providers
                - Laboratory information systems
                - Electronic health record (EHR) systems
                ''',
                'expected_functional': 20,
                'expected_non_functional': 12,
                'complexity': 'very_high'
            }
        ]

    @pytest.mark.asyncio
    async def test_end_to_end_parsing_workflow(self, parser_system, comprehensive_test_cases):
        """엔드투엔드 파싱 워크플로우 테스트"""
        
        parser = parser_system['parser']
        validator = parser_system['validator']
        
        for test_case in comprehensive_test_cases:
            # 1. 파싱 실행
            parsing_result = await parser.parse_requirements(
                test_case['description'],
                project_context={'name': test_case['name']}
            )
            
            # 2. 기본 구조 검증
            assert parsing_result is not None
            assert hasattr(parsing_result, 'functional_requirements')
            assert hasattr(parsing_result, 'non_functional_requirements')
            assert hasattr(parsing_result, 'user_stories')
            
            # 3. 결과 검증
            validation_result = await validator.validate_parsing_result(
                parsing_result,
                test_case['description']
            )
            
            # 4. 품질 기준 확인
            assert validation_result['quality_score'] >= 0.7
            assert validation_result['summary']['total_errors'] == 0
            
            # 5. 예상 결과와 비교
            functional_count = len(parsing_result.functional_requirements)
            assert functional_count >= test_case['expected_functional'] * 0.8
            
            non_functional_count = len(parsing_result.non_functional_requirements)
            assert non_functional_count >= test_case['expected_non_functional'] * 0.8

    @pytest.mark.asyncio
    async def test_performance_under_load(self, parser_system):
        """부하 상황에서의 성능 테스트"""
        
        parser = parser_system['parser']
        monitor = parser_system['monitor']
        
        # 동시 요청 테스트
        concurrent_requests = 10
        test_requirement = "Build a REST API with authentication and CRUD operations"
        
        async def make_request():
            start_time = time.time()
            result = await parser.parse_requirements(test_requirement)
            return {
                'duration': time.time() - start_time,
                'success': result is not None,
                'functional_count': len(result.functional_requirements) if result else 0
            }
        
        # 동시 실행
        tasks = [make_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        
        # 성능 검증
        successful_requests = [r for r in results if r['success']]
        assert len(successful_requests) == concurrent_requests
        
        avg_duration = sum(r['duration'] for r in successful_requests) / len(successful_requests)
        assert avg_duration < 3.0  # 평균 3초 이내
        
        # 결과 일관성 검증
        functional_counts = [r['functional_count'] for r in successful_requests]
        assert all(count > 0 for count in functional_counts)

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, parser_system):
        """오류 처리 및 복구 테스트"""
        
        parser = parser_system['parser']
        
        error_test_cases = [
            {
                'name': 'empty_input',
                'input': '',
                'expected_behavior': 'graceful_handling'
            },
            {
                'name': 'malformed_input',
                'input': '!@#$%^&*()',
                'expected_behavior': 'error_recovery'
            },
            {
                'name': 'extremely_long_input',
                'input': 'Build a system ' * 10000,
                'expected_behavior': 'handle_large_input'
            }
        ]
        
        for test_case in error_test_cases:
            try:
                result = await parser.parse_requirements(test_case['input'])
                
                # 결과가 있다면 최소한의 구조는 있어야 함
                if result:
                    assert hasattr(result, 'functional_requirements')
                    assert hasattr(result, 'non_functional_requirements')
                
            except Exception as e:
                # 예외가 발생해도 시스템이 복구 가능해야 함
                assert isinstance(e, (ValueError, TypeError))
                
                # 다음 요청이 정상 작동하는지 확인
                recovery_result = await parser.parse_requirements(
                    "Build a simple web application"
                )
                assert recovery_result is not None

    @pytest.mark.asyncio
    async def test_memory_efficiency(self, parser_system):
        """메모리 효율성 테스트"""
        
        parser = parser_system['parser']
        monitor = parser_system['monitor']
        
        # 메모리 누수 테스트
        memory_test_result = await monitor.memory_leak_test(
            parser,
            iterations=50
        )
        
        # 메모리 증가가 50MB 이하여야 함
        assert memory_test_result['memory_growth'] < 50
        assert not memory_test_result['leak_detected']

    @pytest.mark.asyncio
    async def test_parsing_accuracy_validation(self, parser_system, comprehensive_test_cases):
        """파싱 정확도 검증 테스트"""
        
        parser = parser_system['parser']
        validator = parser_system['validator']
        
        accuracy_results = []
        
        for test_case in comprehensive_test_cases:
            # 파싱 실행
            result = await parser.parse_requirements(test_case['description'])
            
            # 정확도 측정
            accuracy_metrics = await self._measure_parsing_accuracy(
                result,
                test_case,
                validator
            )
            
            accuracy_results.append({
                'test_case': test_case['name'],
                'accuracy': accuracy_metrics
            })
        
        # 전체 정확도 검증
        avg_accuracy = sum(r['accuracy']['overall'] for r in accuracy_results) / len(accuracy_results)
        assert avg_accuracy >= 0.85  # 85% 이상 정확도

    @pytest.mark.asyncio
    async def test_component_integration_stability(self, parser_system):
        """컴포넌트 통합 안정성 테스트"""
        
        parser = parser_system['parser']
        tester = parser_system['tester']
        
        # 각 컴포넌트 개별 테스트
        component_tests = await tester._test_component_integration()
        
        # 모든 컴포넌트가 정상 작동해야 함
        for component_name, test_result in component_tests.items():
            assert test_result['status'] == 'passed'
            assert test_result.get('error_count', 0) == 0

    @pytest.mark.asyncio
    async def test_scalability_limits(self, parser_system):
        """확장성 한계 테스트"""
        
        parser = parser_system['parser']
        
        # 점진적으로 부하 증가
        load_levels = [5, 10, 20, 30]
        max_successful_load = 0
        
        for load_level in load_levels:
            try:
                # 동시 요청 실행
                tasks = [
                    parser.parse_requirements("Build a web application")
                    for _ in range(load_level)
                ]
                
                start_time = time.time()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                duration = time.time() - start_time
                
                # 성공률 계산
                successful = len([r for r in results if not isinstance(r, Exception)])
                success_rate = successful / load_level
                
                # 성공률이 90% 이상이고 평균 응답시간이 5초 이하면 통과
                if success_rate >= 0.9 and duration / load_level < 5.0:
                    max_successful_load = load_level
                else:
                    break
                    
            except Exception as e:
                break
        
        # 최소 10개 동시 요청은 처리할 수 있어야 함
        assert max_successful_load >= 10

    async def _measure_parsing_accuracy(
        self,
        parsing_result,
        test_case: Dict[str, Any],
        validator
    ) -> Dict[str, float]:
        """파싱 정확도 측정"""
        
        # 검증 실행
        validation_result = await validator.validate_parsing_result(
            parsing_result,
            test_case['description']
        )
        
        # 정확도 메트릭 계산
        accuracy_metrics = {
            'overall': validation_result['quality_score'],
            'completeness': validation_result['validation_results'].get(
                'completeness', {}
            ).get('completeness_score', 0.0),
            'consistency': validation_result['validation_results'].get(
                'consistency', {}
            ).get('consistency_score', 0.0),
            'quality': validation_result['validation_results'].get(
                'quality', {}
            ).get('quality_score', 0.0)
        }
        
        return accuracy_metrics

    @pytest.mark.performance
    async def test_benchmark_against_targets(self, parser_system):
        """목표 성능 대비 벤치마크 테스트"""
        
        parser = parser_system['parser']
        monitor = parser_system['monitor']
        
        # 성능 목표
        performance_targets = {
            'avg_response_time': 2.0,  # 2초 이내
            'throughput': 0.5,         # 초당 0.5 요청 이상
            'error_rate': 0.05,        # 5% 이하
            'memory_usage': 100        # 100MB 이하
        }
        
        # 벤치마크 실행
        test_cases = [
            "Build a simple web application",
            "Create a complex enterprise system with multiple modules"
        ]
        
        benchmark_results = await monitor.benchmark_parsing_performance(
            parser,
            test_cases,
            iterations=5
        )
        
        # 목표 대비 검증
        summary = benchmark_results['summary']
        
        assert summary['average_duration'] <= performance_targets['avg_response_time']
        assert summary['average_throughput'] >= performance_targets['throughput']
        assert summary['overall_error_rate'] <= performance_targets['error_rate']

# 통합 테스트 실행 스크립트
async def run_complete_integration_tests():
    """완전한 통합 테스트 실행"""
    
    print("=== Parser Agent Complete Integration Tests ===")
    
    # pytest 실행
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-m', 'integration'
    ])
    
    return exit_code == 0

if __name__ == "__main__":
    success = asyncio.run(run_complete_integration_tests())
    print(f"\nIntegration tests {'PASSED' if success else 'FAILED'}")