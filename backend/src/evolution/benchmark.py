"""
T-Developer Evolution System - Performance Benchmark
에이전트 성능 벤치마킹 도구

목표:
- 인스턴스화 시간: < 3μs
- 메모리 사용량: < 6.5KB
- 응답 시간: < 100ms
"""

import gc
import importlib.util
import json
import os
import statistics
import sys
import time
import tracemalloc
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil


@dataclass
class BenchmarkResult:
    """벤치마크 결과"""

    agent_name: str
    instantiation_us: float
    memory_kb: float
    response_time_ms: float
    cpu_percent: float
    passes_constraints: bool
    iterations: int
    std_dev_us: float
    min_us: float
    max_us: float
    percentile_95_us: float


class AgentBenchmark:
    """
    에이전트 성능 벤치마킹 시스템
    정밀한 성능 측정 및 제약 조건 검증
    """

    # 성능 목표
    TARGET_INSTANTIATION_US = 3.0
    TARGET_MEMORY_KB = 6.5
    TARGET_RESPONSE_MS = 100.0

    # 벤치마크 설정
    WARMUP_ITERATIONS = 10
    BENCHMARK_ITERATIONS = 100

    def __init__(self, results_path: str = None):
        """벤치마크 시스템 초기화"""
        self.results_path = Path(results_path or "backend/data/benchmarks/results.json")
        self.results_path.parent.mkdir(parents=True, exist_ok=True)

        self.results: List[BenchmarkResult] = []
        self.current_process = psutil.Process()

    def benchmark_agent(self, agent_path: str, iterations: int = None) -> BenchmarkResult:
        """
        단일 에이전트 벤치마킹

        Args:
            agent_path: 에이전트 파일 경로
            iterations: 반복 횟수 (기본: BENCHMARK_ITERATIONS)

        Returns:
            벤치마크 결과
        """
        agent_file = Path(agent_path)
        if not agent_file.exists():
            raise FileNotFoundError(f"Agent file not found: {agent_path}")

        iterations = iterations or self.BENCHMARK_ITERATIONS
        agent_name = agent_file.stem

        print(f"\n⚡ Benchmarking: {agent_name}")
        print(f"   Iterations: {iterations}")

        # 워밍업
        self._warmup(agent_path)

        # 인스턴스화 속도 측정
        instantiation_times = self._measure_instantiation_speed(agent_path, iterations)

        # 메모리 사용량 측정
        memory_kb = self._measure_memory_usage(agent_path)

        # 응답 시간 측정
        response_time_ms = self._measure_response_time(agent_path)

        # CPU 사용률 측정
        cpu_percent = self._measure_cpu_usage(agent_path)

        # 통계 계산
        avg_instantiation = statistics.mean(instantiation_times)
        std_dev = statistics.stdev(instantiation_times) if len(instantiation_times) > 1 else 0
        min_time = min(instantiation_times)
        max_time = max(instantiation_times)
        percentile_95 = self._calculate_percentile(instantiation_times, 95)

        # 제약 조건 확인
        passes = (
            avg_instantiation <= self.TARGET_INSTANTIATION_US
            and memory_kb <= self.TARGET_MEMORY_KB
            and response_time_ms <= self.TARGET_RESPONSE_MS
        )

        result = BenchmarkResult(
            agent_name=agent_name,
            instantiation_us=round(avg_instantiation, 3),
            memory_kb=round(memory_kb, 2),
            response_time_ms=round(response_time_ms, 2),
            cpu_percent=round(cpu_percent, 1),
            passes_constraints=passes,
            iterations=iterations,
            std_dev_us=round(std_dev, 3),
            min_us=round(min_time, 3),
            max_us=round(max_time, 3),
            percentile_95_us=round(percentile_95, 3),
        )

        self.results.append(result)
        self._print_result(result)

        return result

    def _warmup(self, agent_path: str):
        """JIT 컴파일러 워밍업"""
        try:
            for _ in range(self.WARMUP_ITERATIONS):
                spec = importlib.util.spec_from_file_location("warmup_agent", agent_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                del module
                gc.collect()
        except Exception:
            pass  # 워밍업 실패는 무시

    def _measure_instantiation_speed(self, agent_path: str, iterations: int) -> List[float]:
        """
        에이전트 인스턴스화 속도 정밀 측정

        Returns:
            각 반복의 인스턴스화 시간 (마이크로초)
        """
        times = []

        for i in range(iterations):
            try:
                # 가비지 컬렉션 강제 실행
                gc.collect()
                gc.disable()  # 측정 중 GC 비활성화

                # 모듈 로드 및 인스턴스화 시간 측정
                start = time.perf_counter_ns()

                spec = importlib.util.spec_from_file_location(f"test_agent_{i}", agent_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 에이전트 클래스 찾기 및 인스턴스화
                for name in dir(module):
                    obj = getattr(module, name)
                    if isinstance(obj, type) and "Agent" in name:
                        instance = obj()
                        break

                end = time.perf_counter_ns()

                # 나노초를 마이크로초로 변환
                elapsed_us = (end - start) / 1000
                times.append(elapsed_us)

                # 정리
                del module
                if "instance" in locals():
                    del instance

            except Exception as e:
                print(f"⚠️ Iteration {i} failed: {e}")
                times.append(float("inf"))

            finally:
                gc.enable()
                gc.collect()

        # 이상치 제거 (상위/하위 5%)
        times.sort()
        trim_count = max(1, len(times) // 20)
        if len(times) > 20:
            times = times[trim_count:-trim_count]

        return times

    def _measure_memory_usage(self, agent_path: str) -> float:
        """
        에이전트 메모리 사용량 측정

        Returns:
            메모리 사용량 (KB)
        """
        # 파일 크기 (정적 메모리)
        file_size_kb = Path(agent_path).stat().st_size / 1024

        # 런타임 메모리 측정
        tracemalloc.start()
        gc.collect()

        try:
            spec = importlib.util.spec_from_file_location("memory_test", agent_path)
            module = importlib.util.module_from_spec(spec)

            snapshot1 = tracemalloc.take_snapshot()
            spec.loader.exec_module(module)

            # 에이전트 인스턴스 생성
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and "Agent" in name:
                    instance = obj()
                    break

            snapshot2 = tracemalloc.take_snapshot()

            # 메모리 차이 계산
            stats = snapshot2.compare_to(snapshot1, "lineno")
            runtime_memory_kb = sum(stat.size_diff for stat in stats) / 1024

        except Exception as e:
            print(f"⚠️ Memory measurement failed: {e}")
            runtime_memory_kb = 0

        finally:
            tracemalloc.stop()

        # 정적 + 동적 메모리
        total_memory_kb = file_size_kb + max(0, runtime_memory_kb)

        return total_memory_kb

    def _measure_response_time(self, agent_path: str) -> float:
        """
        에이전트 응답 시간 측정

        Returns:
            평균 응답 시간 (밀리초)
        """
        try:
            spec = importlib.util.spec_from_file_location("response_test", agent_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 에이전트 인스턴스 생성
            agent_instance = None
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and "Agent" in name:
                    agent_instance = obj()
                    break

            if not agent_instance:
                return 0.0

            # process 메서드가 있으면 호출
            if hasattr(agent_instance, "process"):
                test_input = {"test": "data"}

                times = []
                for _ in range(10):
                    start = time.perf_counter()
                    agent_instance.process(test_input)
                    end = time.perf_counter()
                    times.append((end - start) * 1000)  # 밀리초

                return statistics.mean(times)

        except Exception:
            pass

        return 0.0

    def _measure_cpu_usage(self, agent_path: str) -> float:
        """
        에이전트 CPU 사용률 측정

        Returns:
            평균 CPU 사용률 (%)
        """
        try:
            # 초기 CPU 상태
            self.current_process.cpu_percent()
            time.sleep(0.1)

            # 에이전트 실행 중 CPU 측정
            spec = importlib.util.spec_from_file_location("cpu_test", agent_path)
            module = importlib.util.module_from_spec(spec)

            cpu_samples = []
            for _ in range(5):
                spec.loader.exec_module(module)
                cpu_samples.append(self.current_process.cpu_percent())
                time.sleep(0.01)

            return statistics.mean(cpu_samples)

        except Exception:
            return 0.0

    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """백분위수 계산"""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def _print_result(self, result: BenchmarkResult):
        """벤치마크 결과 출력"""
        status = "✅ PASS" if result.passes_constraints else "❌ FAIL"

        print(f"\n{status} Benchmark Results for {result.agent_name}")
        print("=" * 50)
        print(f"Instantiation Speed:")
        print(f"  Average: {result.instantiation_us}μs (target: <{self.TARGET_INSTANTIATION_US}μs)")
        print(f"  Std Dev: {result.std_dev_us}μs")
        print(f"  Min/Max: {result.min_us}μs / {result.max_us}μs")
        print(f"  95th percentile: {result.percentile_95_us}μs")
        print(f"\nMemory Usage: {result.memory_kb}KB (target: <{self.TARGET_MEMORY_KB}KB)")
        print(f"Response Time: {result.response_time_ms}ms (target: <{self.TARGET_RESPONSE_MS}ms)")
        print(f"CPU Usage: {result.cpu_percent}%")

    def benchmark_directory(self, directory: str) -> List[BenchmarkResult]:
        """
        디렉토리 내 모든 에이전트 벤치마킹

        Args:
            directory: 에이전트 디렉토리 경로

        Returns:
            모든 벤치마크 결과
        """
        agent_dir = Path(directory)
        if not agent_dir.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        agent_files = list(agent_dir.rglob("*agent*.py"))
        print(f"\n🚀 Found {len(agent_files)} agents to benchmark")

        results = []
        for agent_file in agent_files:
            try:
                result = self.benchmark_agent(str(agent_file))
                results.append(result)
            except Exception as e:
                print(f"❌ Failed to benchmark {agent_file.name}: {e}")

        self._save_results()
        self._print_summary()

        return results

    def _save_results(self):
        """벤치마크 결과 저장"""
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": [asdict(r) for r in self.results],
            "summary": self._calculate_summary(),
        }

        with open(self.results_path, "w") as f:
            json.dump(data, f, indent=2)

    def _calculate_summary(self) -> Dict[str, Any]:
        """전체 벤치마크 요약"""
        if not self.results:
            return {}

        passing = sum(1 for r in self.results if r.passes_constraints)
        total = len(self.results)

        return {
            "total_agents": total,
            "passing_agents": passing,
            "pass_rate": f"{(passing/total)*100:.1f}%",
            "avg_instantiation_us": round(
                statistics.mean(r.instantiation_us for r in self.results), 3
            ),
            "avg_memory_kb": round(statistics.mean(r.memory_kb for r in self.results), 2),
            "avg_response_ms": round(statistics.mean(r.response_time_ms for r in self.results), 2),
            "fastest_agent": min(self.results, key=lambda r: r.instantiation_us).agent_name,
            "smallest_agent": min(self.results, key=lambda r: r.memory_kb).agent_name,
        }

    def _print_summary(self):
        """벤치마크 요약 출력"""
        summary = self._calculate_summary()
        if not summary:
            return

        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 60)

        for key, value in summary.items():
            print(f"{key}: {value}")

        print("\n🏆 Top Performers:")

        # 속도 순위
        speed_sorted = sorted(self.results, key=lambda r: r.instantiation_us)[:3]
        print("\nFastest Agents:")
        for i, r in enumerate(speed_sorted, 1):
            print(f"  {i}. {r.agent_name}: {r.instantiation_us}μs")

        # 메모리 순위
        memory_sorted = sorted(self.results, key=lambda r: r.memory_kb)[:3]
        print("\nSmallest Agents:")
        for i, r in enumerate(memory_sorted, 1):
            print(f"  {i}. {r.agent_name}: {r.memory_kb}KB")


# CLI 인터페이스
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agent Performance Benchmark")
    parser.add_argument("path", help="Agent file or directory path")
    parser.add_argument("--iterations", type=int, default=100, help="Number of iterations")
    parser.add_argument(
        "--quick-test", action="store_true", help="Quick test with fewer iterations"
    )

    args = parser.parse_args()

    benchmark = AgentBenchmark()

    iterations = 10 if args.quick_test else args.iterations

    path = Path(args.path)
    if path.is_file():
        benchmark.benchmark_agent(str(path), iterations)
    elif path.is_dir():
        benchmark.benchmark_directory(str(path))
    else:
        print(f"❌ Path not found: {args.path}")
        sys.exit(1)

    # 빠른 테스트 결과
    if args.quick_test:
        results = benchmark.results
        if results and results[0].passes_constraints:
            print("\n✅ PASS - Agent meets performance constraints")
            sys.exit(0)
        else:
            print("\n❌ FAIL - Agent violates performance constraints")
            sys.exit(1)
