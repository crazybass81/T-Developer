# backend/src/agents/implementations/parser_performance_monitor.py
import time
import asyncio
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import psutil
import threading

@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceReport:
    test_name: str
    duration: float
    memory_usage: Dict[str, float]
    cpu_usage: float
    throughput: float
    error_rate: float
    metrics: List[PerformanceMetric] = field(default_factory=list)

class ParserPerformanceMonitor:
    """Parser Agent 성능 모니터링"""

    def __init__(self):
        self.metrics_history = []
        self.monitoring_active = False
        self.baseline_metrics = None

    async def benchmark_parsing_performance(
        self,
        parser_agent,
        test_cases: List[str],
        iterations: int = 10
    ) -> Dict[str, Any]:
        """파싱 성능 벤치마크"""
        
        benchmark_results = {}
        
        for i, test_case in enumerate(test_cases):
            case_name = f"test_case_{i+1}"
            
            # 단일 케이스 벤치마크
            case_results = await self._benchmark_single_case(
                parser_agent,
                test_case,
                iterations,
                case_name
            )
            
            benchmark_results[case_name] = case_results
        
        # 전체 성능 요약
        benchmark_results['summary'] = self._generate_performance_summary(
            benchmark_results
        )
        
        return benchmark_results

    async def _benchmark_single_case(
        self,
        parser_agent,
        test_case: str,
        iterations: int,
        case_name: str
    ) -> PerformanceReport:
        """단일 케이스 벤치마크"""
        
        execution_times = []
        memory_usage = []
        cpu_usage = []
        errors = 0
        
        # 베이스라인 메모리 측정
        baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        for i in range(iterations):
            # CPU 사용률 모니터링 시작
            cpu_monitor = CPUMonitor()
            cpu_monitor.start()
            
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            try:
                # 파싱 실행
                result = await parser_agent.parse_requirements(test_case)
                
                # 결과 검증
                if not result or not result.functional_requirements:
                    errors += 1
                
            except Exception as e:
                errors += 1
                print(f"Error in iteration {i+1}: {e}")
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # 메트릭 수집
            execution_times.append(end_time - start_time)
            memory_usage.append(end_memory - start_memory)
            
            cpu_monitor.stop()
            cpu_usage.append(cpu_monitor.get_average_usage())
            
            # 메모리 정리를 위한 짧은 대기
            await asyncio.sleep(0.1)
        
        # 통계 계산
        avg_execution_time = statistics.mean(execution_times)
        avg_memory_usage = statistics.mean(memory_usage)
        avg_cpu_usage = statistics.mean(cpu_usage)
        
        throughput = iterations / sum(execution_times)  # requests per second
        error_rate = errors / iterations
        
        return PerformanceReport(
            test_name=case_name,
            duration=avg_execution_time,
            memory_usage={
                'average': avg_memory_usage,
                'peak': max(memory_usage),
                'baseline': baseline_memory
            },
            cpu_usage=avg_cpu_usage,
            throughput=throughput,
            error_rate=error_rate,
            metrics=[
                PerformanceMetric(
                    name="execution_time",
                    value=avg_execution_time,
                    unit="seconds",
                    timestamp=datetime.now(),
                    context={'iterations': iterations}
                ),
                PerformanceMetric(
                    name="memory_usage",
                    value=avg_memory_usage,
                    unit="MB",
                    timestamp=datetime.now()
                ),
                PerformanceMetric(
                    name="throughput",
                    value=throughput,
                    unit="requests/second",
                    timestamp=datetime.now()
                )
            ]
        )

    async def stress_test(
        self,
        parser_agent,
        concurrent_requests: int = 20,
        duration_seconds: int = 60
    ) -> Dict[str, Any]:
        """스트레스 테스트"""
        
        test_requirement = "Build a web application with user authentication and data management"
        
        # 동시 요청 생성
        async def make_request():
            try:
                start_time = time.time()
                result = await parser_agent.parse_requirements(test_requirement)
                end_time = time.time()
                
                return {
                    'success': True,
                    'duration': end_time - start_time,
                    'result_valid': result is not None
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'duration': 0
                }
        
        # 스트레스 테스트 실행
        start_time = time.time()
        completed_requests = 0
        successful_requests = 0
        total_duration = 0
        errors = []
        
        while time.time() - start_time < duration_seconds:
            # 동시 요청 배치 실행
            tasks = [make_request() for _ in range(concurrent_requests)]
            results = await asyncio.gather(*tasks)
            
            # 결과 집계
            for result in results:
                completed_requests += 1
                if result['success']:
                    successful_requests += 1
                    total_duration += result['duration']
                else:
                    errors.append(result.get('error', 'Unknown error'))
        
        # 스트레스 테스트 결과
        test_duration = time.time() - start_time
        
        return {
            'test_duration': test_duration,
            'completed_requests': completed_requests,
            'successful_requests': successful_requests,
            'error_rate': (completed_requests - successful_requests) / completed_requests,
            'average_response_time': total_duration / successful_requests if successful_requests > 0 else 0,
            'requests_per_second': completed_requests / test_duration,
            'concurrent_users': concurrent_requests,
            'errors': errors[:10]  # 처음 10개 에러만 저장
        }

    async def memory_leak_test(
        self,
        parser_agent,
        iterations: int = 100
    ) -> Dict[str, Any]:
        """메모리 누수 테스트"""
        
        memory_snapshots = []
        test_requirement = "Create a REST API with authentication and CRUD operations"
        
        # 초기 메모리 측정
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_snapshots.append(initial_memory)
        
        for i in range(iterations):
            # 파싱 실행
            await parser_agent.parse_requirements(test_requirement)
            
            # 메모리 측정 (10회마다)
            if i % 10 == 0:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_snapshots.append(current_memory)
        
        # 최종 메모리 측정
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_snapshots.append(final_memory)
        
        # 메모리 증가 분석
        memory_growth = final_memory - initial_memory
        max_memory = max(memory_snapshots)
        
        # 메모리 누수 감지
        leak_detected = memory_growth > 50  # 50MB 이상 증가 시 누수 의심
        
        return {
            'initial_memory': initial_memory,
            'final_memory': final_memory,
            'memory_growth': memory_growth,
            'max_memory': max_memory,
            'leak_detected': leak_detected,
            'memory_snapshots': memory_snapshots,
            'iterations': iterations
        }

    def _generate_performance_summary(
        self,
        benchmark_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """성능 요약 생성"""
        
        all_durations = []
        all_throughputs = []
        all_error_rates = []
        
        for key, result in benchmark_results.items():
            if key == 'summary':
                continue
                
            if isinstance(result, PerformanceReport):
                all_durations.append(result.duration)
                all_throughputs.append(result.throughput)
                all_error_rates.append(result.error_rate)
        
        return {
            'average_duration': statistics.mean(all_durations) if all_durations else 0,
            'max_duration': max(all_durations) if all_durations else 0,
            'min_duration': min(all_durations) if all_durations else 0,
            'average_throughput': statistics.mean(all_throughputs) if all_throughputs else 0,
            'overall_error_rate': statistics.mean(all_error_rates) if all_error_rates else 0,
            'performance_grade': self._calculate_performance_grade(all_durations, all_error_rates)
        }

    def _calculate_performance_grade(
        self,
        durations: List[float],
        error_rates: List[float]
    ) -> str:
        """성능 등급 계산"""
        
        if not durations or not error_rates:
            return 'UNKNOWN'
        
        avg_duration = statistics.mean(durations)
        avg_error_rate = statistics.mean(error_rates)
        
        # 성능 기준
        if avg_duration < 1.0 and avg_error_rate < 0.01:
            return 'EXCELLENT'
        elif avg_duration < 2.0 and avg_error_rate < 0.05:
            return 'GOOD'
        elif avg_duration < 5.0 and avg_error_rate < 0.10:
            return 'ACCEPTABLE'
        else:
            return 'POOR'


class CPUMonitor:
    """CPU 사용률 모니터"""

    def __init__(self):
        self.cpu_samples = []
        self.monitoring = False
        self.monitor_thread = None

    def start(self):
        """모니터링 시작"""
        self.monitoring = True
        self.cpu_samples = []
        self.monitor_thread = threading.Thread(target=self._monitor_cpu)
        self.monitor_thread.start()

    def stop(self):
        """모니터링 중지"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def get_average_usage(self) -> float:
        """평균 CPU 사용률 반환"""
        return statistics.mean(self.cpu_samples) if self.cpu_samples else 0.0

    def _monitor_cpu(self):
        """CPU 모니터링 스레드"""
        while self.monitoring:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_samples.append(cpu_percent)
            time.sleep(0.1)


# 성능 테스트 실행 스크립트
async def run_performance_tests(parser_agent):
    """성능 테스트 실행"""
    
    monitor = ParserPerformanceMonitor()
    
    # 테스트 케이스
    test_cases = [
        "Build a simple web application",
        "Create an e-commerce platform with user management, product catalog, and payment processing",
        "Develop a complex enterprise system with multiple modules and integrations"
    ]
    
    print("=== Parser Agent Performance Tests ===")
    
    # 벤치마크 테스트
    print("Running benchmark tests...")
    benchmark_results = await monitor.benchmark_parsing_performance(
        parser_agent,
        test_cases,
        iterations=5
    )
    
    print(f"Average Duration: {benchmark_results['summary']['average_duration']:.2f}s")
    print(f"Performance Grade: {benchmark_results['summary']['performance_grade']}")
    
    # 스트레스 테스트
    print("\nRunning stress test...")
    stress_results = await monitor.stress_test(
        parser_agent,
        concurrent_requests=10,
        duration_seconds=30
    )
    
    print(f"Requests per second: {stress_results['requests_per_second']:.2f}")
    print(f"Error rate: {stress_results['error_rate']:.2%}")
    
    # 메모리 누수 테스트
    print("\nRunning memory leak test...")
    memory_results = await monitor.memory_leak_test(
        parser_agent,
        iterations=50
    )
    
    print(f"Memory growth: {memory_results['memory_growth']:.2f}MB")
    print(f"Leak detected: {memory_results['leak_detected']}")
    
    return {
        'benchmark': benchmark_results,
        'stress': stress_results,
        'memory': memory_results
    }