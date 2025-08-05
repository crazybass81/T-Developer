import asyncio
import time
import statistics
from typing import List, Dict, Any
from .nl_input_agent import NLInputAgent
from .nl_input_multimodal import MultimodalInputProcessor
from .requirement_clarification import RequirementClarificationSystem

class NLAgentBenchmark:
    """NL Agent 성능 벤치마크"""
    
    def __init__(self):
        self.nl_agent = NLInputAgent()
        self.multimodal_processor = MultimodalInputProcessor(self.nl_agent)
        self.clarification_system = RequirementClarificationSystem()
        
    async def run_performance_benchmark(self) -> Dict[str, Any]:
        """성능 벤치마크 실행"""
        
        test_cases = [
            "간단한 할일 관리 웹 애플리케이션을 만들어주세요",
            "React와 Node.js를 사용한 실시간 채팅 앱",
            "Python Django로 REST API 서버 구축",
            "모바일 앱 - iOS/Android 지원, 사진 공유 기능",
            "전자상거래 플랫폼 - 결제, 주문관리, 재고관리"
        ]
        
        results = {
            'total_tests': len(test_cases),
            'individual_times': [],
            'accuracy_scores': [],
            'memory_usage': [],
            'error_count': 0
        }
        
        for i, test_case in enumerate(test_cases):
            print(f"Running test {i+1}/{len(test_cases)}: {test_case[:50]}...")
            
            try:
                # 시간 측정
                start_time = time.perf_counter()
                
                # NL 처리 실행
                requirements = await self.nl_agent.process_description(test_case)
                
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                
                results['individual_times'].append(execution_time)
                
                # 정확도 평가 (간단한 휴리스틱)
                accuracy = self._evaluate_accuracy(test_case, requirements)
                results['accuracy_scores'].append(accuracy)
                
                print(f"  Time: {execution_time:.3f}s, Accuracy: {accuracy:.2f}")
                
            except Exception as e:
                print(f"  Error: {e}")
                results['error_count'] += 1
        
        # 통계 계산
        if results['individual_times']:
            results['avg_time'] = statistics.mean(results['individual_times'])
            results['max_time'] = max(results['individual_times'])
            results['min_time'] = min(results['individual_times'])
            results['std_dev'] = statistics.stdev(results['individual_times']) if len(results['individual_times']) > 1 else 0
        
        if results['accuracy_scores']:
            results['avg_accuracy'] = statistics.mean(results['accuracy_scores'])
            
        results['success_rate'] = (len(test_cases) - results['error_count']) / len(test_cases)
        
        return results
    
    def _evaluate_accuracy(self, input_text: str, requirements) -> float:
        """정확도 평가 (간단한 휴리스틱)"""
        score = 0.0
        
        # 프로젝트 타입 정확도
        if self._check_project_type_accuracy(input_text, requirements.project_type):
            score += 0.3
            
        # 기술 스택 추출 정확도
        if self._check_tech_stack_accuracy(input_text, requirements.technology_preferences):
            score += 0.3
            
        # 요구사항 추출 정확도
        if len(requirements.technical_requirements) > 0:
            score += 0.2
            
        # 구조화 정확도
        if requirements.description and requirements.project_type:
            score += 0.2
            
        return min(score, 1.0)
    
    def _check_project_type_accuracy(self, input_text: str, project_type: str) -> bool:
        """프로젝트 타입 정확도 확인"""
        input_lower = input_text.lower()
        
        type_keywords = {
            'web_application': ['웹', 'web', '웹앱'],
            'mobile_application': ['모바일', 'mobile', '앱', 'ios', 'android'],
            'api_service': ['api', 'rest', '서버'],
            'cli_tool': ['cli', 'command', '명령어']
        }
        
        expected_keywords = type_keywords.get(project_type, [])
        return any(keyword in input_lower for keyword in expected_keywords)
    
    def _check_tech_stack_accuracy(self, input_text: str, tech_prefs: Dict) -> bool:
        """기술 스택 정확도 확인"""
        input_lower = input_text.lower()
        
        # 입력에 명시된 기술이 추출되었는지 확인
        mentioned_techs = []
        if 'react' in input_lower:
            mentioned_techs.append('react')
        if 'node' in input_lower or 'nodejs' in input_lower:
            mentioned_techs.append('node')
        if 'python' in input_lower:
            mentioned_techs.append('python')
        if 'django' in input_lower:
            mentioned_techs.append('django')
            
        if not mentioned_techs:
            return True  # 기술이 명시되지 않았으면 정확도 통과
            
        # 추출된 기술과 비교
        extracted_techs = []
        for category, techs in tech_prefs.items():
            if isinstance(techs, list):
                extracted_techs.extend([t.lower() for t in techs])
            elif isinstance(techs, str):
                extracted_techs.append(techs.lower())
                
        return any(tech in extracted_techs for tech in mentioned_techs)
    
    async def run_load_test(self, concurrent_requests: int = 10) -> Dict[str, Any]:
        """부하 테스트"""
        test_case = "React와 Node.js를 사용한 웹 애플리케이션을 만들어주세요"
        
        async def single_request():
            start_time = time.perf_counter()
            try:
                await self.nl_agent.process_description(test_case)
                return time.perf_counter() - start_time, True
            except Exception:
                return time.perf_counter() - start_time, False
        
        print(f"Running load test with {concurrent_requests} concurrent requests...")
        
        # 동시 요청 실행
        start_time = time.perf_counter()
        tasks = [single_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_time
        
        # 결과 분석
        times = [r[0] for r in results]
        successes = [r[1] for r in results]
        
        return {
            'concurrent_requests': concurrent_requests,
            'total_time': total_time,
            'avg_response_time': statistics.mean(times),
            'max_response_time': max(times),
            'min_response_time': min(times),
            'success_rate': sum(successes) / len(successes),
            'requests_per_second': concurrent_requests / total_time
        }

async def main():
    """벤치마크 실행"""
    benchmark = NLAgentBenchmark()
    
    print("🚀 Starting NL Agent Performance Benchmark...")
    
    # 성능 벤치마크
    perf_results = await benchmark.run_performance_benchmark()
    
    print("\n📊 Performance Results:")
    print(f"  Average Time: {perf_results.get('avg_time', 0):.3f}s")
    print(f"  Max Time: {perf_results.get('max_time', 0):.3f}s")
    print(f"  Average Accuracy: {perf_results.get('avg_accuracy', 0):.2f}")
    print(f"  Success Rate: {perf_results.get('success_rate', 0):.2f}")
    
    # 부하 테스트
    load_results = await benchmark.run_load_test(concurrent_requests=5)
    
    print("\n⚡ Load Test Results:")
    print(f"  Concurrent Requests: {load_results['concurrent_requests']}")
    print(f"  Requests/Second: {load_results['requests_per_second']:.2f}")
    print(f"  Average Response Time: {load_results['avg_response_time']:.3f}s")
    print(f"  Success Rate: {load_results['success_rate']:.2f}")
    
    # 목표 달성 여부 확인
    print("\n✅ Target Achievement:")
    print(f"  Response Time < 2s: {'✅' if perf_results.get('avg_time', 0) < 2.0 else '❌'}")
    print(f"  Accuracy > 95%: {'✅' if perf_results.get('avg_accuracy', 0) > 0.95 else '❌'}")
    print(f"  Success Rate > 99%: {'✅' if perf_results.get('success_rate', 0) > 0.99 else '❌'}")

if __name__ == "__main__":
    asyncio.run(main())