"""API Performance - Day 9: Enhanced with Memory and Instantiation Tracking

Performance monitoring and tracking for T-Developer API Gateway:
- Memory usage tracking (6.5KB constraint validation)
- Instantiation time monitoring (3μs requirement)
- Request performance tracking
- Load testing capabilities
"""

import asyncio
import concurrent.futures
import gc
import os
import statistics
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

import psutil


class PerformanceTester:
    def __init__(self):
        self.test_results = []

    def start_timing(self) -> float:
        return time.time()

    def end_timing(self, start_time: float) -> float:
        return (time.time() - start_time) * 1000

    def measure_function(self, func: Callable, *args, **kwargs) -> Dict:
        start_time = self.start_timing()
        try:
            result = func(*args, **kwargs)
            execution_time = self.end_timing(start_time)
            return {
                "success": True,
                "result": result,
                "execution_time_ms": execution_time,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            execution_time = self.end_timing(start_time)
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": execution_time,
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def measure_async_function(self, func: Callable, *args, **kwargs) -> Dict:
        start_time = self.start_timing()
        try:
            result = await func(*args, **kwargs)
            execution_time = self.end_timing(start_time)
            return {
                "success": True,
                "result": result,
                "execution_time_ms": execution_time,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            execution_time = self.end_timing(start_time)
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": execution_time,
                "timestamp": datetime.utcnow().isoformat(),
            }

    def load_test(
        self, func: Callable, concurrent_requests: int, total_requests: int, *args, **kwargs
    ) -> Dict:
        start_time = time.time()

        def single_request():
            return self.measure_function(func, *args, **kwargs)

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            results = [
                future.result()
                for future in concurrent.futures.as_completed(
                    [executor.submit(single_request) for _ in range(total_requests)]
                )
            ]
        total_time = time.time() - start_time
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        if successful:
            times = [r["execution_time_ms"] for r in successful]
            return {
                "total_requests": total_requests,
                "successful_requests": len(successful),
                "failed_requests": len(failed),
                "success_rate": len(successful) / total_requests,
                "total_time_seconds": total_time,
                "requests_per_second": total_requests / total_time,
                "response_times": {
                    "average_ms": statistics.mean(times),
                    "median_ms": statistics.median(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                },
                "errors": [r["error"] for r in failed],
                "timestamp": datetime.utcnow().isoformat(),
            }
        return {
            "total_requests": total_requests,
            "successful_requests": 0,
            "failed_requests": len(failed),
            "success_rate": 0,
            "errors": [r["error"] for r in failed],
        }

    def benchmark_comparison(self, test_cases: Dict[str, Callable], iterations: int = 100) -> Dict:
        results = {}
        for name, func in test_cases.items():
            times = []
            success_count = 0
            for _ in range(iterations):
                result = self.measure_function(func)
                if result["success"]:
                    times.append(result["execution_time_ms"])
                    success_count += 1
            if times:
                results[name] = {
                    "iterations": iterations,
                    "successful_runs": success_count,
                    "success_rate": success_count / iterations,
                    "average_ms": statistics.mean(times),
                    "median_ms": statistics.median(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                }
            else:
                results[name] = {
                    "iterations": iterations,
                    "successful_runs": 0,
                    "success_rate": 0,
                    "error": "All failed",
                }
        return {
            "benchmark_results": results,
            "fastest": min(results.keys(), key=lambda k: results[k].get("average_ms", float("inf")))
            if results
            else None,
            "timestamp": datetime.utcnow().isoformat(),
        }


class PerformanceMonitor:
    def __init__(self):
        self.metrics_history = []
        self.max_history_size = 1000

    def record_performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        metric = {
            "name": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.metrics_history.append(metric)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)

    def get_performance_summary(self, metric_name: str, minutes: int = 5) -> Dict:
        from datetime import timedelta

        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_metrics = [
            m
            for m in self.metrics_history
            if m["name"] == metric_name and datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        if not recent_metrics:
            return {"metric_name": metric_name, "count": 0, "time_window_minutes": minutes}
        values = [m["value"] for m in recent_metrics]
        return {
            "metric_name": metric_name,
            "count": len(values),
            "time_window_minutes": minutes,
            "average": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "unit": recent_metrics[0]["unit"],
        }

    def get_all_metrics_summary(self, minutes: int = 5) -> Dict:
        metric_names = set(m["name"] for m in self.metrics_history)
        summaries = {}
        for metric_name in metric_names:
            summaries[metric_name] = self.get_performance_summary(metric_name, minutes)
        return {
            "time_window_minutes": minutes,
            "metrics": summaries,
            "timestamp": datetime.utcnow().isoformat(),
        }


class PerformanceTracker:
    """Enhanced Performance Tracker for API Gateway

    Tracks memory usage, instantiation time, and request performance
    to validate 6.5KB memory constraint and 3μs instantiation requirement
    """

    def __init__(self):
        self.start_time = time.time()
        self.instantiation_start = time.perf_counter()
        self.process = psutil.Process(os.getpid())
        self.request_metrics = []
        self.max_metrics_history = 1000

        # Complete instantiation timing
        self.instantiation_time_us = (time.perf_counter() - self.instantiation_start) * 1_000_000

    def get_memory_usage_kb(self) -> float:
        """Get current memory usage in KB for 6.5KB constraint validation"""
        try:
            # Get memory info for current process
            memory_info = self.process.memory_info()
            # RSS (Resident Set Size) - physical memory currently used
            memory_kb = memory_info.rss / 1024
            return round(memory_kb, 2)
        except Exception:
            return 0.0

    def get_instantiation_time_us(self) -> float:
        """Get instantiation time in microseconds for 3μs requirement validation"""
        return round(self.instantiation_time_us, 2)

    def get_uptime(self) -> str:
        """Get system uptime"""
        uptime_seconds = time.time() - self.start_time
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    @contextmanager
    def track_request(self, path: str):
        """Context manager to track individual request performance"""
        start_time = time.perf_counter()
        start_memory = self.get_memory_usage_kb()

        try:
            yield
        finally:
            end_time = time.perf_counter()
            end_memory = self.get_memory_usage_kb()

            # Record request metrics
            request_metric = {
                "path": path,
                "response_time_ms": (end_time - start_time) * 1000,
                "memory_start_kb": start_memory,
                "memory_end_kb": end_memory,
                "memory_diff_kb": end_memory - start_memory,
                "timestamp": datetime.utcnow().isoformat(),
            }

            self.request_metrics.append(request_metric)

            # Keep metrics history within limit
            if len(self.request_metrics) > self.max_metrics_history:
                self.request_metrics.pop(0)

    def get_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        current_memory = self.get_memory_usage_kb()

        metrics = {
            "system": {
                "uptime": self.get_uptime(),
                "instantiation_time_us": self.instantiation_time_us,
                "instantiation_constraint_met": self.instantiation_time_us < 3.0,
                "current_memory_kb": current_memory,
                "memory_constraint_met": current_memory < 6.5,
                "timestamp": datetime.utcnow().isoformat(),
            },
            "constraints": {
                "memory_limit_kb": 6.5,
                "instantiation_limit_us": 3.0,
                "memory_status": "PASS" if current_memory < 6.5 else "FAIL",
                "instantiation_status": "PASS" if self.instantiation_time_us < 3.0 else "FAIL",
            },
        }

        # Request metrics summary
        if self.request_metrics:
            recent_requests = [
                r
                for r in self.request_metrics
                if datetime.fromisoformat(r["timestamp"]) > datetime.utcnow() - timedelta(minutes=5)
            ]

            if recent_requests:
                response_times = [r["response_time_ms"] for r in recent_requests]
                memory_usage = [r["memory_end_kb"] for r in recent_requests]

                metrics["requests"] = {
                    "recent_count": len(recent_requests),
                    "avg_response_time_ms": statistics.mean(response_times),
                    "max_response_time_ms": max(response_times),
                    "min_response_time_ms": min(response_times),
                    "avg_memory_kb": statistics.mean(memory_usage),
                    "max_memory_kb": max(memory_usage),
                }

        return metrics

    def validate_constraints(self) -> Dict:
        """Validate performance constraints"""
        current_memory = self.get_memory_usage_kb()

        return {
            "memory_constraint": {
                "limit_kb": 6.5,
                "current_kb": current_memory,
                "status": "PASS" if current_memory < 6.5 else "FAIL",
                "margin_kb": 6.5 - current_memory,
            },
            "instantiation_constraint": {
                "limit_us": 3.0,
                "current_us": self.instantiation_time_us,
                "status": "PASS" if self.instantiation_time_us < 3.0 else "FAIL",
                "margin_us": 3.0 - self.instantiation_time_us,
            },
            "overall_status": "PASS"
            if (current_memory < 6.5 and self.instantiation_time_us < 3.0)
            else "FAIL",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def reset_metrics(self):
        """Reset collected metrics"""
        self.request_metrics.clear()
        gc.collect()  # Force garbage collection
