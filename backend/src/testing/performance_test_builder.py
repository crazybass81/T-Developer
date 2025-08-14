"""PerformanceTestBuilder - Day 34
Performance test generation - Size: ~6.5KB"""
from typing import Any, Dict, List


class PerformanceTestBuilder:
    """Build performance tests - Size optimized to 6.5KB"""

    def __init__(self):
        self.thresholds = {
            "response_time": 200,  # ms
            "throughput": 1000,  # ops/sec
            "memory": 6.5,  # KB
            "cpu": 80,  # percent
        }

    def build_latency_test(self, operation: str, threshold: float) -> str:
        """Build latency test"""
        return f'''def test_{operation}_latency():
    """Test {operation} latency < {threshold}ms"""
    import time
    times = []

    for _ in range(100):
        start = time.perf_counter()
        # Execute {operation}
        result = {operation}()
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)

    avg = sum(times) / len(times)
    p95 = sorted(times)[94]

    assert avg < {threshold}, f"Avg {{avg:.2f}}ms > {threshold}ms"
    assert p95 < {threshold * 1.5}, f"P95 {{p95:.2f}}ms > {threshold * 1.5}ms"
'''

    def build_throughput_test(self, operation: str, min_ops: int) -> str:
        """Build throughput test"""
        return f'''def test_{operation}_throughput():
    """Test {operation} throughput > {min_ops} ops/sec"""
    import time

    ops = 0
    start = time.time()

    while time.time() - start < 1.0:
        {operation}()
        ops += 1

    assert ops >= {min_ops}, f"Throughput {{ops}} ops/s < {min_ops} ops/s"
'''

    def build_memory_test(self, operation: str, max_kb: float) -> str:
        """Build memory test"""
        return f'''def test_{operation}_memory():
    """Test {operation} memory < {max_kb}KB"""
    import tracemalloc

    tracemalloc.start()

    # Run operation
    for _ in range(100):
        {operation}()

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_kb = peak / 1024
    assert peak_kb < {max_kb}, f"Peak memory {{peak_kb:.2f}}KB > {max_kb}KB"
'''

    def build_concurrent_test(self, operation: str, workers: int) -> str:
        """Build concurrency test"""
        return f'''def test_{operation}_concurrent():
    """Test {operation} with {workers} workers"""
    import concurrent.futures
    import time

    def worker():
        start = time.perf_counter()
        {operation}()
        return time.perf_counter() - start

    with concurrent.futures.ThreadPoolExecutor(max_workers={workers}) as executor:
        futures = [executor.submit(worker) for _ in range({workers * 10})]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    avg = sum(results) / len(results) * 1000
    assert avg < 500, f"Avg concurrent time {{avg:.2f}}ms > 500ms"
'''

    def build_load_test(self, operation: str, max_load: int) -> str:
        """Build load test"""
        return f'''def test_{operation}_load():
    """Test {operation} under load"""
    import time

    loads = [10, 50, 100, 500, {max_load}]

    for load in loads:
        start = time.time()
        errors = 0

        for _ in range(load):
            try:
                {operation}()
            except:
                errors += 1

        elapsed = time.time() - start
        error_rate = errors / load

        assert error_rate < 0.01, f"Error rate {{error_rate:.1%}} at load {{load}}"
        assert elapsed < load * 0.01, f"Time {{elapsed:.2f}}s at load {{load}}"
'''

    def build_stress_test(self, operation: str, duration: int) -> str:
        """Build stress test"""
        return f'''def test_{operation}_stress():
    """Test {operation} under stress for {duration}s"""
    import time

    start = time.time()
    ops = 0
    errors = 0

    while time.time() - start < {duration}:
        try:
            {operation}()
            ops += 1
        except:
            errors += 1

    success_rate = ops / (ops + errors) if (ops + errors) > 0 else 0
    throughput = ops / {duration}

    assert success_rate > 0.99, f"Success rate {{success_rate:.1%}} < 99%"
    assert throughput > 100, f"Throughput {{throughput:.0f}} ops/s < 100 ops/s"
'''

    def build_suite(self, config: Dict[str, Any]) -> str:
        """Build complete performance test suite"""
        suite = '''"""Performance Test Suite"""
import pytest
import time
import tracemalloc
import concurrent.futures

'''

        op = config.get("operation", "process")

        if "latency" in config:
            suite += self.build_latency_test(op, config["latency"])
            suite += "\n"

        if "throughput" in config:
            suite += self.build_throughput_test(op, config["throughput"])
            suite += "\n"

        if "memory" in config:
            suite += self.build_memory_test(op, config["memory"])
            suite += "\n"

        if "concurrent" in config:
            suite += self.build_concurrent_test(op, config["concurrent"])
            suite += "\n"

        if "load" in config:
            suite += self.build_load_test(op, config["load"])
            suite += "\n"

        if "stress" in config:
            suite += self.build_stress_test(op, config["stress"])

        return suite
