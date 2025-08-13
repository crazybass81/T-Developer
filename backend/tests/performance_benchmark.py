#!/usr/bin/env python3
"""
Performance Benchmark System for T-Developer MVP
성능 벤치마크 및 최적화 시스템
"""

import asyncio
import httpx
import time
import statistics
import json
import logging
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import psutil
import threading
import sys
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 테스트 설정
BASE_URL = "http://localhost:8000"
TIMEOUT = 120  # 2분 타임아웃


@dataclass
class PerformanceMetrics:
    """성능 메트릭"""

    generation_time: float
    response_time: float
    download_time: float
    total_time: float
    memory_usage: Dict[str, float]
    cpu_usage: float
    file_count: int
    zip_size_mb: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class BenchmarkResult:
    """벤치마크 결과"""

    scenario: str
    metrics: List[PerformanceMetrics]
    average_generation_time: float
    median_generation_time: float
    success_rate: float
    performance_target_met: bool
    recommendations: List[str]


class SystemMonitor:
    """시스템 리소스 모니터링"""

    def __init__(self):
        self.monitoring = False
        self.metrics = []
        self.monitor_thread = None

    def start_monitoring(self):
        """모니터링 시작"""
        self.monitoring = True
        self.metrics = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()

    def stop_monitoring(self) -> Dict[str, float]:
        """모니터링 중지 및 결과 반환"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

        if not self.metrics:
            return {"memory_mb": 0, "cpu_percent": 0}

        memory_values = [m["memory_mb"] for m in self.metrics]
        cpu_values = [m["cpu_percent"] for m in self.metrics]

        return {
            "memory_mb": {
                "avg": statistics.mean(memory_values),
                "max": max(memory_values),
                "min": min(memory_values),
            },
            "cpu_percent": {
                "avg": statistics.mean(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values),
            },
        }

    def _monitor_loop(self):
        """모니터링 루프"""
        while self.monitoring:
            try:
                # 현재 프로세스 메모리 사용량
                process = psutil.Process(os.getpid())
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024

                # CPU 사용률
                cpu_percent = process.cpu_percent()

                self.metrics.append(
                    {
                        "timestamp": time.time(),
                        "memory_mb": memory_mb,
                        "cpu_percent": cpu_percent,
                    }
                )

                time.sleep(1)  # 1초마다 측정
            except Exception as e:
                logger.warning(f"모니터링 오류: {e}")
                time.sleep(1)


class PerformanceBenchmark:
    """성능 벤치마크 실행기"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        self.system_monitor = SystemMonitor()

    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """종합 성능 벤치마크 실행"""

        print("🚀 T-Developer Performance Benchmark Starting...")
        print("=" * 60)

        # 벤치마크 시나리오
        scenarios = [
            ("Simple React App", self._benchmark_simple_react, 3),
            ("Todo Application", self._benchmark_todo_app, 3),
            ("Blog Website", self._benchmark_blog_website, 2),
            ("Dashboard App", self._benchmark_dashboard, 2),
            ("Complex E-commerce", self._benchmark_ecommerce, 1),
        ]

        benchmark_results = []
        overall_start_time = time.time()

        for scenario_name, benchmark_func, run_count in scenarios:
            print(f"\n📊 Running: {scenario_name} ({run_count} runs)")

            try:
                result = await self._run_scenario_benchmark(
                    scenario_name, benchmark_func, run_count
                )
                benchmark_results.append(result)

                # 결과 요약 출력
                print(f"✅ {scenario_name}:")
                print(f"   평균 생성시간: {result.average_generation_time:.2f}초")
                print(f"   성공률: {result.success_rate:.1f}%")
                print(f"   목표달성: {'✅' if result.performance_target_met else '❌'}")

            except Exception as e:
                print(f"❌ {scenario_name}: 벤치마크 실패 - {e}")
                logger.error(
                    f"Benchmark failed for {scenario_name}: {e}", exc_info=True
                )

        total_benchmark_time = time.time() - overall_start_time

        # 종합 결과 분석
        overall_results = self._analyze_overall_performance(benchmark_results)
        overall_results["total_benchmark_time"] = total_benchmark_time
        overall_results["benchmark_results"] = [
            {
                "scenario": r.scenario,
                "avg_time": r.average_generation_time,
                "success_rate": r.success_rate,
                "target_met": r.performance_target_met,
                "recommendations": r.recommendations,
            }
            for r in benchmark_results
        ]

        # 결과 출력
        self._print_benchmark_summary(overall_results)

        return overall_results

    async def _run_scenario_benchmark(
        self, scenario_name: str, benchmark_func, run_count: int
    ) -> BenchmarkResult:
        """시나리오별 벤치마크 실행"""

        metrics_list = []

        for run_num in range(run_count):
            print(f"   Run {run_num + 1}/{run_count}...", end=" ")

            try:
                metrics = await benchmark_func()
                metrics_list.append(metrics)

                status = "✅" if metrics.success else "❌"
                print(f"{status} {metrics.total_time:.2f}s")

            except Exception as e:
                error_metrics = PerformanceMetrics(
                    generation_time=0,
                    response_time=0,
                    download_time=0,
                    total_time=0,
                    memory_usage={"memory_mb": {"avg": 0}},
                    cpu_usage=0,
                    file_count=0,
                    zip_size_mb=0,
                    success=False,
                    error_message=str(e),
                )
                metrics_list.append(error_metrics)
                print(f"❌ ERROR: {str(e)[:50]}...")

        return self._calculate_scenario_results(scenario_name, metrics_list)

    async def _benchmark_simple_react(self) -> PerformanceMetrics:
        """간단한 React 앱 벤치마크"""
        return await self._benchmark_project_generation(
            {
                "user_input": "Create a simple React app with modern design",
                "project_type": "react",
                "features": [],
            }
        )

    async def _benchmark_todo_app(self) -> PerformanceMetrics:
        """Todo 앱 벤치마크"""
        return await self._benchmark_project_generation(
            {
                "user_input": "Create a React todo application with add, edit, delete functionality",
                "project_type": "react",
                "features": ["todo"],
            }
        )

    async def _benchmark_blog_website(self) -> PerformanceMetrics:
        """블로그 웹사이트 벤치마크"""
        return await self._benchmark_project_generation(
            {
                "user_input": "Create a blog website with React and routing for multiple pages",
                "project_type": "react",
                "features": ["routing", "blog"],
            }
        )

    async def _benchmark_dashboard(self) -> PerformanceMetrics:
        """대시보드 벤치마크"""
        return await self._benchmark_project_generation(
            {
                "user_input": "Create an admin dashboard with charts and data visualization",
                "project_type": "react",
                "features": ["dashboard", "charts"],
            }
        )

    async def _benchmark_ecommerce(self) -> PerformanceMetrics:
        """이커머스 벤치마크"""
        return await self._benchmark_project_generation(
            {
                "user_input": "Create a complete e-commerce website with React, routing, state management, and shopping cart",
                "project_type": "react",
                "features": ["routing", "state-management", "ecommerce", "cart"],
            }
        )

    async def _benchmark_project_generation(
        self, payload: Dict[str, Any]
    ) -> PerformanceMetrics:
        """프로젝트 생성 벤치마크 실행"""

        # 시스템 모니터링 시작
        self.system_monitor.start_monitoring()

        total_start_time = time.time()

        try:
            # 1. 프로젝트 생성 요청
            generation_start_time = time.time()

            response = await self.client.post(
                f"{self.base_url}/api/v1/generate", json=payload
            )

            generation_time = time.time() - generation_start_time
            response_time = generation_time

            if response.status_code != 200:
                raise Exception(f"Generation failed: {response.status_code}")

            data = response.json()

            if not data.get("success"):
                raise Exception(f"Generation unsuccessful: {data.get('message')}")

            project_id = data.get("project_id")
            download_url = data.get("download_url")

            # 2. 다운로드 테스트
            download_start_time = time.time()

            download_response = await self.client.get(f"{self.base_url}{download_url}")

            download_time = time.time() - download_start_time

            if download_response.status_code != 200:
                raise Exception(f"Download failed: {download_response.status_code}")

            # 3. ZIP 파일 검증
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
                temp_zip.write(download_response.content)
                temp_zip_path = temp_zip.name

            try:
                file_count, zip_size_mb = self._analyze_zip_file(temp_zip_path)
            finally:
                os.unlink(temp_zip_path)

            total_time = time.time() - total_start_time

            # 시스템 모니터링 중지
            system_metrics = self.system_monitor.stop_monitoring()

            return PerformanceMetrics(
                generation_time=generation_time,
                response_time=response_time,
                download_time=download_time,
                total_time=total_time,
                memory_usage=system_metrics,
                cpu_usage=system_metrics.get("cpu_percent", {}).get("avg", 0),
                file_count=file_count,
                zip_size_mb=zip_size_mb,
                success=True,
            )

        except Exception as e:
            total_time = time.time() - total_start_time
            system_metrics = self.system_monitor.stop_monitoring()

            return PerformanceMetrics(
                generation_time=0,
                response_time=0,
                download_time=0,
                total_time=total_time,
                memory_usage=system_metrics,
                cpu_usage=system_metrics.get("cpu_percent", {}).get("avg", 0),
                file_count=0,
                zip_size_mb=0,
                success=False,
                error_message=str(e),
            )

    def _analyze_zip_file(self, zip_path: str) -> Tuple[int, float]:
        """ZIP 파일 분석"""
        try:
            with zipfile.ZipFile(zip_path, "r") as zipf:
                file_count = len([f for f in zipf.filelist if not f.is_dir()])
                zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
                return file_count, zip_size_mb
        except Exception:
            return 0, 0

    def _calculate_scenario_results(
        self, scenario_name: str, metrics_list: List[PerformanceMetrics]
    ) -> BenchmarkResult:
        """시나리오 결과 계산"""

        successful_metrics = [m for m in metrics_list if m.success]
        success_rate = (len(successful_metrics) / len(metrics_list)) * 100

        if not successful_metrics:
            return BenchmarkResult(
                scenario=scenario_name,
                metrics=metrics_list,
                average_generation_time=0,
                median_generation_time=0,
                success_rate=success_rate,
                performance_target_met=False,
                recommendations=["모든 실행이 실패했습니다. 시스템 상태를 확인해주세요."],
            )

        generation_times = [m.generation_time for m in successful_metrics]
        average_generation_time = statistics.mean(generation_times)
        median_generation_time = statistics.median(generation_times)

        # 성능 목표: 30초 이내
        performance_target = 30.0
        performance_target_met = average_generation_time <= performance_target

        # 추천사항 생성
        recommendations = self._generate_recommendations(
            scenario_name,
            successful_metrics,
            average_generation_time,
            performance_target,
        )

        return BenchmarkResult(
            scenario=scenario_name,
            metrics=metrics_list,
            average_generation_time=average_generation_time,
            median_generation_time=median_generation_time,
            success_rate=success_rate,
            performance_target_met=performance_target_met,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        scenario: str,
        metrics: List[PerformanceMetrics],
        avg_time: float,
        target: float,
    ) -> List[str]:
        """성능 개선 추천사항 생성"""

        recommendations = []

        # 성능 목표 미달성 시
        if avg_time > target:
            recommendations.append(f"평균 생성시간이 목표({target}초)를 초과했습니다 ({avg_time:.2f}초)")

            if avg_time > target * 1.5:
                recommendations.append("심각한 성능 저하 - Agent 병렬 처리 최적화 필요")

            # 메모리 사용량 분석
            avg_memory = statistics.mean(
                [m.memory_usage.get("memory_mb", {}).get("avg", 0) for m in metrics]
            )

            if avg_memory > 500:  # 500MB 초과
                recommendations.append(
                    f"메모리 사용량이 높습니다 ({avg_memory:.1f}MB) - 메모리 최적화 필요"
                )

            # CPU 사용률 분석
            avg_cpu = statistics.mean([m.cpu_usage for m in metrics])
            if avg_cpu > 80:
                recommendations.append(f"CPU 사용률이 높습니다 ({avg_cpu:.1f}%) - 처리 로직 최적화 필요")
        else:
            recommendations.append(f"성능 목표 달성! (평균 {avg_time:.2f}초)")

        # 파일 크기 분석
        avg_zip_size = statistics.mean([m.zip_size_mb for m in metrics])
        if avg_zip_size > 10:
            recommendations.append(
                f"ZIP 파일이 큽니다 ({avg_zip_size:.1f}MB) - 불필요한 파일 제거 검토"
            )

        return recommendations

    def _analyze_overall_performance(
        self, results: List[BenchmarkResult]
    ) -> Dict[str, Any]:
        """전체 성능 분석"""

        if not results:
            return {"overall_grade": "F", "performance_met": False}

        successful_results = [r for r in results if r.success_rate > 0]

        if not successful_results:
            return {
                "overall_grade": "F",
                "performance_met": False,
                "summary": "모든 벤치마크 실패",
            }

        # 전체 평균 성능
        avg_times = [r.average_generation_time for r in successful_results]
        overall_avg_time = statistics.mean(avg_times)

        # 성공률
        success_rates = [r.success_rate for r in results]
        overall_success_rate = statistics.mean(success_rates)

        # 성능 목표 달성률
        target_met_count = sum(
            1 for r in successful_results if r.performance_target_met
        )
        target_met_rate = (target_met_count / len(successful_results)) * 100

        # 등급 계산
        grade = self._calculate_performance_grade(
            overall_avg_time, overall_success_rate, target_met_rate
        )

        return {
            "overall_grade": grade,
            "overall_avg_time": overall_avg_time,
            "overall_success_rate": overall_success_rate,
            "target_met_rate": target_met_rate,
            "performance_met": grade in ["A", "B"],
            "summary": f"평균 {overall_avg_time:.1f}초, 성공률 {overall_success_rate:.1f}%, 목표달성률 {target_met_rate:.1f}%",
        }

    def _calculate_performance_grade(
        self, avg_time: float, success_rate: float, target_met_rate: float
    ) -> str:
        """성능 등급 계산"""

        # A등급: 평균 20초 이내, 성공률 95% 이상, 목표달성률 80% 이상
        if avg_time <= 20 and success_rate >= 95 and target_met_rate >= 80:
            return "A"

        # B등급: 평균 30초 이내, 성공률 90% 이상, 목표달성률 60% 이상
        elif avg_time <= 30 and success_rate >= 90 and target_met_rate >= 60:
            return "B"

        # C등급: 평균 45초 이내, 성공률 80% 이상
        elif avg_time <= 45 and success_rate >= 80:
            return "C"

        # D등급: 평균 60초 이내, 성공률 70% 이상
        elif avg_time <= 60 and success_rate >= 70:
            return "D"

        # F등급: 그 외
        else:
            return "F"

    def _print_benchmark_summary(self, results: Dict[str, Any]):
        """벤치마크 결과 요약 출력"""

        print("\n" + "=" * 60)
        print("📊 PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 60)

        print(f"Overall Grade: {results['overall_grade']}")
        print(
            f"Performance Target Met: {'✅ YES' if results['performance_met'] else '❌ NO'}"
        )
        print(f"{results['summary']}")

        print("\n🎯 Scenario Results:")
        for scenario in results["benchmark_results"]:
            status = "✅" if scenario["target_met"] else "❌"
            print(
                f"  {status} {scenario['scenario']}: {scenario['avg_time']:.2f}s ({scenario['success_rate']:.1f}%)"
            )

        print(f"\n⏱️  Total Benchmark Time: {results['total_benchmark_time']:.2f}s")

        # 추천사항 출력
        print("\n💡 Performance Recommendations:")
        all_recommendations = set()
        for scenario in results["benchmark_results"]:
            all_recommendations.update(scenario["recommendations"])

        for i, rec in enumerate(sorted(all_recommendations), 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 60)

    async def save_benchmark_report(
        self, results: Dict[str, Any], output_path: Optional[str] = None
    ) -> str:
        """벤치마크 보고서 저장"""

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"performance_benchmark_report_{timestamp}.json"

        report_data = {
            "benchmark_suite": "T-Developer MVP Performance Benchmark",
            "execution_time": datetime.now().isoformat(),
            "system_info": {"python_version": sys.version, "platform": sys.platform},
            "results": results,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)

        print(f"📋 Benchmark report saved to: {output_path}")
        return output_path

    async def cleanup(self):
        """정리"""
        await self.client.aclose()


async def run_performance_benchmark():
    """성능 벤치마크 실행 메인 함수"""

    benchmark = PerformanceBenchmark()

    try:
        # 서버 상태 확인
        try:
            response = await benchmark.client.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                raise Exception("서버가 응답하지 않습니다")
            print("✅ Server health check passed")
        except Exception as e:
            print(f"❌ Server not available: {e}")
            return 1

        # 벤치마크 실행
        results = await benchmark.run_comprehensive_benchmark()

        # 보고서 저장
        await benchmark.save_benchmark_report(results)

        # 결과에 따른 종료 코드
        if results["performance_met"]:
            print("\n🎉 Performance benchmark passed!")
            return 0
        else:
            print(
                f"\n💥 Performance benchmark failed (Grade: {results['overall_grade']})!"
            )
            return 1

    except Exception as e:
        print(f"\n❌ Benchmark execution failed: {e}")
        logger.error("Benchmark failed", exc_info=True)
        return 1
    finally:
        await benchmark.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(run_performance_benchmark())
    sys.exit(exit_code)
