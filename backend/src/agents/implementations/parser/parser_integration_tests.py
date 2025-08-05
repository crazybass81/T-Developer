# backend/src/agents/implementations/parser_integration_tests.py
import pytest
import asyncio
import time
from typing import Dict, List, Any
from unittest.mock import Mock, patch
from dataclasses import dataclass

from parser_agent import ParserAgent
from parser_requirement_separator import RequirementSeparator
from parser_dependency_analyzer import DependencyAnalyzer
from parser_user_story_generator import UserStoryGenerator

@dataclass
class TestCase:
    name: str
    description: str
    expected_functional: int
    expected_non_functional: int
    expected_dependencies: int
    expected_user_stories: int

class ParserIntegrationTester:
    """Parser Agent 통합 테스트"""

    def __init__(self):
        self.parser_agent = None
        self.test_cases = self._load_test_cases()
        self.performance_metrics = {}

    async def setup(self):
        """테스트 환경 설정"""
        self.parser_agent = ParserAgent()
        await self.parser_agent.initialize()

    async def teardown(self):
        """테스트 환경 정리"""
        if self.parser_agent:
            await self.parser_agent.cleanup()

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """포괄적인 통합 테스트 실행"""
        
        results = {
            'functional_tests': await self._test_functional_parsing(),
            'performance_tests': await self._test_performance(),
            'accuracy_tests': await self._test_accuracy(),
            'edge_case_tests': await self._test_edge_cases(),
            'integration_tests': await self._test_component_integration()
        }

        # 전체 결과 요약
        results['summary'] = self._generate_test_summary(results)
        
        return results

    async def _test_functional_parsing(self) -> Dict[str, Any]:
        """기능적 파싱 테스트"""
        
        test_results = []
        
        for test_case in self.test_cases:
            start_time = time.time()
            
            try:
                # 파싱 실행
                result = await self.parser_agent.parse_requirements(
                    test_case.description,
                    project_context={'name': test_case.name}
                )
                
                # 결과 검증
                validation = self._validate_parsing_result(result, test_case)
                
                test_results.append({
                    'test_case': test_case.name,
                    'status': 'passed' if validation['valid'] else 'failed',
                    'execution_time': time.time() - start_time,
                    'validation': validation,
                    'result_counts': {
                        'functional': len(result.functional_requirements),
                        'non_functional': len(result.non_functional_requirements),
                        'user_stories': len(result.user_stories),
                        'dependencies': sum(len(req.dependencies) for req in result.functional_requirements)
                    }
                })
                
            except Exception as e:
                test_results.append({
                    'test_case': test_case.name,
                    'status': 'error',
                    'error': str(e),
                    'execution_time': time.time() - start_time
                })

        return {
            'total_tests': len(test_results),
            'passed': len([r for r in test_results if r['status'] == 'passed']),
            'failed': len([r for r in test_results if r['status'] == 'failed']),
            'errors': len([r for r in test_results if r['status'] == 'error']),
            'results': test_results
        }

    async def _test_performance(self) -> Dict[str, Any]:
        """성능 테스트"""
        
        performance_results = {}
        
        # 단일 요구사항 처리 시간
        simple_req = "Build a user authentication system"
        times = []
        
        for _ in range(10):
            start = time.time()
            await self.parser_agent.parse_requirements(simple_req)
            times.append(time.time() - start)
        
        performance_results['single_requirement'] = {
            'avg_time': sum(times) / len(times),
            'max_time': max(times),
            'min_time': min(times)
        }
        
        # 복잡한 요구사항 처리
        complex_req = self._get_complex_requirement()
        start = time.time()
        await self.parser_agent.parse_requirements(complex_req)
        performance_results['complex_requirement'] = time.time() - start
        
        # 동시 처리 성능
        concurrent_times = await self._test_concurrent_processing()
        performance_results['concurrent_processing'] = concurrent_times
        
        return performance_results

    async def _test_accuracy(self) -> Dict[str, Any]:
        """정확도 테스트"""
        
        accuracy_results = {}
        
        # 요구사항 분류 정확도
        classification_accuracy = await self._test_classification_accuracy()
        accuracy_results['classification'] = classification_accuracy
        
        # 의존성 탐지 정확도
        dependency_accuracy = await self._test_dependency_accuracy()
        accuracy_results['dependency_detection'] = dependency_accuracy
        
        # 사용자 스토리 생성 품질
        story_quality = await self._test_user_story_quality()
        accuracy_results['user_story_quality'] = story_quality
        
        return accuracy_results

    async def _test_edge_cases(self) -> Dict[str, Any]:
        """엣지 케이스 테스트"""
        
        edge_cases = [
            {
                'name': 'empty_input',
                'input': '',
                'expected_behavior': 'handle_gracefully'
            },
            {
                'name': 'very_long_input',
                'input': 'Build a system ' * 1000,
                'expected_behavior': 'process_without_error'
            },
            {
                'name': 'special_characters',
                'input': 'Build a system with @#$%^&*() characters',
                'expected_behavior': 'parse_correctly'
            },
            {
                'name': 'multilingual_input',
                'input': 'Build a système with 시스템 functionality',
                'expected_behavior': 'handle_mixed_languages'
            }
        ]
        
        results = []
        
        for case in edge_cases:
            try:
                result = await self.parser_agent.parse_requirements(case['input'])
                results.append({
                    'case': case['name'],
                    'status': 'passed',
                    'result_valid': result is not None
                })
            except Exception as e:
                results.append({
                    'case': case['name'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        return {
            'total_cases': len(edge_cases),
            'passed': len([r for r in results if r['status'] == 'passed']),
            'results': results
        }

    async def _test_component_integration(self) -> Dict[str, Any]:
        """컴포넌트 통합 테스트"""
        
        integration_results = {}
        
        # RequirementSeparator 통합
        separator_test = await self._test_separator_integration()
        integration_results['requirement_separator'] = separator_test
        
        # DependencyAnalyzer 통합
        dependency_test = await self._test_dependency_integration()
        integration_results['dependency_analyzer'] = dependency_test
        
        # UserStoryGenerator 통합
        story_test = await self._test_story_generator_integration()
        integration_results['user_story_generator'] = story_test
        
        return integration_results

    def _validate_parsing_result(self, result, test_case: TestCase) -> Dict[str, Any]:
        """파싱 결과 검증"""
        
        validation = {'valid': True, 'issues': []}
        
        # 기능 요구사항 수 검증
        if len(result.functional_requirements) < test_case.expected_functional * 0.8:
            validation['valid'] = False
            validation['issues'].append(f"Too few functional requirements: {len(result.functional_requirements)}")
        
        # 비기능 요구사항 수 검증
        if len(result.non_functional_requirements) < test_case.expected_non_functional * 0.8:
            validation['valid'] = False
            validation['issues'].append(f"Too few non-functional requirements: {len(result.non_functional_requirements)}")
        
        # 사용자 스토리 수 검증
        if len(result.user_stories) < test_case.expected_user_stories * 0.8:
            validation['valid'] = False
            validation['issues'].append(f"Too few user stories: {len(result.user_stories)}")
        
        # 데이터 품질 검증
        for req in result.functional_requirements:
            if not req.id or not req.description:
                validation['valid'] = False
                validation['issues'].append("Missing required fields in functional requirements")
                break
        
        return validation

    async def _test_concurrent_processing(self) -> Dict[str, Any]:
        """동시 처리 테스트"""
        
        num_concurrent = 5
        test_req = "Build a web application with user management"
        
        async def process_requirement():
            return await self.parser_agent.parse_requirements(test_req)
        
        start_time = time.time()
        tasks = [process_requirement() for _ in range(num_concurrent)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful = len([r for r in results if not isinstance(r, Exception)])
        
        return {
            'concurrent_requests': num_concurrent,
            'successful': successful,
            'total_time': total_time,
            'avg_time_per_request': total_time / num_concurrent
        }

    def _load_test_cases(self) -> List[TestCase]:
        """테스트 케이스 로드"""
        
        return [
            TestCase(
                name="Simple Web App",
                description="Build a simple web application with user authentication and basic CRUD operations",
                expected_functional=5,
                expected_non_functional=2,
                expected_dependencies=3,
                expected_user_stories=8
            ),
            TestCase(
                name="E-commerce Platform",
                description="""
                Create an e-commerce platform with the following features:
                - User registration and authentication
                - Product catalog with search and filtering
                - Shopping cart functionality
                - Order processing and payment integration
                - Admin dashboard for inventory management
                
                Non-functional requirements:
                - Support 10,000 concurrent users
                - Response time under 200ms
                - 99.9% uptime
                - PCI DSS compliance for payments
                """,
                expected_functional=12,
                expected_non_functional=6,
                expected_dependencies=8,
                expected_user_stories=20
            ),
            TestCase(
                name="Mobile Banking App",
                description="""
                Develop a mobile banking application with:
                - Secure user authentication (biometric + PIN)
                - Account balance and transaction history
                - Money transfer between accounts
                - Bill payment functionality
                - Investment portfolio management
                
                Security requirements:
                - End-to-end encryption
                - Multi-factor authentication
                - Fraud detection system
                - Compliance with banking regulations
                """,
                expected_functional=10,
                expected_non_functional=8,
                expected_dependencies=6,
                expected_user_stories=15
            )
        ]

    def _get_complex_requirement(self) -> str:
        """복잡한 요구사항 반환"""
        
        return """
        Build a comprehensive enterprise resource planning (ERP) system that includes:
        
        Core Modules:
        1. Human Resources Management
        2. Financial Management and Accounting
        3. Supply Chain Management
        4. Customer Relationship Management
        5. Project Management
        6. Inventory Management
        
        Technical Requirements:
        - Microservices architecture
        - RESTful APIs for all modules
        - Real-time data synchronization
        - Multi-tenant support
        - Role-based access control
        
        Performance Requirements:
        - Support 50,000+ concurrent users
        - 99.99% uptime SLA
        - Response time < 100ms for critical operations
        - Handle 1M+ transactions per day
        
        Security Requirements:
        - SOX compliance
        - GDPR compliance
        - End-to-end encryption
        - Audit trail for all operations
        - Single sign-on (SSO) integration
        
        Integration Requirements:
        - Third-party accounting software
        - Payment gateways
        - Email and SMS services
        - Document management systems
        - Business intelligence tools
        """

    def _generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """테스트 결과 요약 생성"""
        
        total_tests = 0
        total_passed = 0
        
        for test_type, test_result in results.items():
            if test_type == 'summary':
                continue
                
            if isinstance(test_result, dict) and 'total_tests' in test_result:
                total_tests += test_result['total_tests']
                total_passed += test_result.get('passed', 0)
        
        return {
            'total_tests': total_tests,
            'total_passed': total_passed,
            'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0,
            'overall_status': 'PASSED' if total_passed == total_tests else 'FAILED'
        }

# 테스트 실행 스크립트
async def run_integration_tests():
    """통합 테스트 실행"""
    
    tester = ParserIntegrationTester()
    
    try:
        await tester.setup()
        results = await tester.run_comprehensive_tests()
        
        print("=== Parser Agent Integration Test Results ===")
        print(f"Total Tests: {results['summary']['total_tests']}")
        print(f"Passed: {results['summary']['total_passed']}")
        print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
        print(f"Overall Status: {results['summary']['overall_status']}")
        
        return results
        
    finally:
        await tester.teardown()

if __name__ == "__main__":
    asyncio.run(run_integration_tests())