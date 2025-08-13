"""
Day 10: Performance Benchmarking Suite
Comprehensive performance testing for T-Developer Registry System
Validates 6.5KB memory constraint and 3μs instantiation requirements
"""

import asyncio
import gc
import json
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Tuple

import psutil
import pytest

from backend.src.messaging.agent_registry import AgentCapabilityRegistry
from backend.src.api.enhanced_gateway import EnhancedAPIGateway
from backend.src.analysis.ai_analysis_engine import AIAnalysisEngine


class PerformanceBenchmark:
    """Comprehensive performance benchmarking suite"""
    
    def __init__(self):
        self.results = {}
        self.process = psutil.Process(os.getpid())
        self.baseline_memory = self._get_memory_mb()
        
    def _get_memory_mb(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def _get_memory_kb(self) -> float:
        """Get current memory usage in KB"""
        return self.process.memory_info().rss / 1024
    
    def record_benchmark(self, test_name: str, metrics: Dict):
        """Record benchmark results"""
        self.results[test_name] = {
            **metrics,
            "timestamp": datetime.utcnow().isoformat(),
            "memory_at_test_mb": self._get_memory_mb()
        }
    
    def get_summary_report(self) -> Dict:
        """Generate summary performance report"""
        return {
            "baseline_memory_mb": self.baseline_memory,
            "current_memory_mb": self._get_memory_mb(),
            "total_tests": len(self.results),
            "test_results": self.results,
            "generated_at": datetime.utcnow().isoformat()
        }


class TestRegistryPerformance:
    """Performance tests for registry system"""
    
    @pytest.fixture(scope="class")
    def benchmark_suite(self):
        """Setup performance benchmark suite"""
        return PerformanceBenchmark()
    
    def test_memory_constraint_6_5kb(self, benchmark_suite):
        """Test 6.5KB memory constraint compliance"""
        print("\n🧪 Testing 6.5KB Memory Constraint...")
        
        # Test multiple component instantiation
        memory_readings = []
        components = []
        
        for i in range(10):
            gc.collect()  # Force garbage collection
            start_memory = benchmark_suite._get_memory_kb()
            
            # Create registry instance
            registry = AgentCapabilityRegistry()
            
            # Add test data
            for j in range(10):
                agent_data = {
                    "agent_id": f"mem_test_{i}_{j}",
                    "name": f"Memory Test Agent {i}-{j}",
                    "capabilities": ["test_cap"],
                    "input_types": ["text"],
                    "output_types": ["json"]
                }
                registry.register_agent_capabilities(agent_data["agent_id"], agent_data)
            
            end_memory = benchmark_suite._get_memory_kb()
            memory_used = end_memory - start_memory
            memory_readings.append(memory_used)
            components.append(registry)
        
        avg_memory = statistics.mean(memory_readings)
        max_memory = max(memory_readings)
        min_memory = min(memory_readings)
        
        # Record results
        benchmark_suite.record_benchmark("memory_constraint_6_5kb", {
            "average_memory_kb": avg_memory,
            "max_memory_kb": max_memory,
            "min_memory_kb": min_memory,
            "constraint_6_5kb": True,
            "passes_constraint": max_memory < 6.5,
            "memory_efficiency": (6.5 - avg_memory) / 6.5 * 100  # % efficiency
        })
        
        print(f"   Average Memory: {avg_memory:.3f} KB")
        print(f"   Max Memory: {max_memory:.3f} KB") 
        print(f"   Constraint (6.5KB): {'✅ PASS' if max_memory < 6.5 else '❌ FAIL'}")
        
        # Assert constraint compliance
        assert max_memory < 6.5, f"Memory usage {max_memory:.3f}KB exceeds 6.5KB constraint"
        
        # Cleanup
        del components
        gc.collect()
    
    def test_instantiation_3_microseconds(self, benchmark_suite):
        """Test 3μs instantiation requirement"""
        print("\n⚡ Testing 3μs Instantiation Requirement...")
        
        instantiation_times = []
        
        # Test multiple instantiations
        for i in range(100):
            start_time = time.perf_counter()
            registry = AgentCapabilityRegistry()
            end_time = time.perf_counter()
            
            instantiation_time_us = (end_time - start_time) * 1_000_000
            instantiation_times.append(instantiation_time_us)
            del registry
        
        avg_time = statistics.mean(instantiation_times)
        max_time = max(instantiation_times)
        min_time = min(instantiation_times)
        p95_time = statistics.quantiles(instantiation_times, n=20)[18]  # 95th percentile
        
        # Record results
        benchmark_suite.record_benchmark("instantiation_3_microseconds", {
            "average_time_us": avg_time,
            "max_time_us": max_time,
            "min_time_us": min_time,
            "p95_time_us": p95_time,
            "constraint_3us": True,
            "passes_constraint": p95_time < 3.0,
            "performance_efficiency": (3.0 - avg_time) / 3.0 * 100  # % efficiency
        })
        
        print(f"   Average Time: {avg_time:.3f} μs")
        print(f"   95th Percentile: {p95_time:.3f} μs")
        print(f"   Max Time: {max_time:.3f} μs")
        print(f"   Constraint (3μs): {'✅ PASS' if p95_time < 3.0 else '❌ FAIL'}")
        
        # Assert constraint compliance
        assert p95_time < 3.0, f"95th percentile instantiation {p95_time:.3f}μs exceeds 3μs constraint"
    
    @pytest.mark.asyncio
    async def test_concurrent_performance(self, benchmark_suite):
        """Test concurrent processing capabilities"""
        print("\n🔀 Testing Concurrent Processing...")
        
        registry = AgentCapabilityRegistry()
        
        # Test concurrent registrations
        concurrent_levels = [1, 5, 10, 20, 50]
        results = {}
        
        for concurrency in concurrent_levels:
            print(f"   Testing {concurrency} concurrent operations...")
            
            start_time = time.time()
            tasks = []
            
            for i in range(concurrency):
                agent_data = {
                    "agent_id": f"concurrent_{concurrency}_{i}",
                    "name": f"Concurrent Agent {i}",
                    "capabilities": [f"concurrent_cap_{i}"],
                    "input_types": ["text"],
                    "output_types": ["json"]
                }
                task = registry.register_agent_capabilities_async(
                    agent_data["agent_id"], agent_data
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            end_time = time.time()
            
            total_time = (end_time - start_time) * 1000  # ms
            throughput = concurrency / (total_time / 1000)  # ops/sec
            avg_latency = total_time / concurrency  # ms per op
            
            results[f"concurrency_{concurrency}"] = {
                "total_time_ms": total_time,
                "throughput_ops_per_sec": throughput,
                "avg_latency_ms": avg_latency
            }
            
            print(f"     Total Time: {total_time:.2f}ms")
            print(f"     Throughput: {throughput:.2f} ops/sec")
            print(f"     Avg Latency: {avg_latency:.2f}ms")
        
        # Test concurrent searches
        search_start = time.time()
        search_tasks = []
        
        for i in range(50):
            task = registry.find_agents_by_capability_async(f"concurrent_cap_{i % 20}")
            search_tasks.append(task)
        
        search_results = await asyncio.gather(*search_tasks)
        search_end = time.time()
        search_time = (search_end - search_start) * 1000  # ms
        
        results["concurrent_search"] = {
            "search_time_ms": search_time,
            "search_throughput": 50 / (search_time / 1000),
            "results_found": sum(len(r) for r in search_results)
        }
        
        # Record benchmark
        benchmark_suite.record_benchmark("concurrent_performance", results)
        
        # Verify performance thresholds
        assert results["concurrency_10"]["avg_latency_ms"] < 100, "10 concurrent ops latency too high"
        assert results["concurrent_search"]["search_time_ms"] < 200, "Concurrent search too slow"
        
        print(f"   Concurrent Search: {search_time:.2f}ms for 50 searches")
    
    def test_scalability_performance(self, benchmark_suite):
        """Test system scalability with increasing load"""
        print("\n📈 Testing Scalability Performance...")
        
        registry = AgentCapabilityRegistry()
        scalability_results = {}
        
        # Test different data sizes
        data_sizes = [100, 500, 1000, 2000, 5000]
        
        for size in data_sizes:
            print(f"   Testing with {size} agents...")
            
            # Setup phase - register agents
            setup_start = time.time()
            for i in range(size):
                agent_data = {
                    "agent_id": f"scale_test_{size}_{i}",
                    "name": f"Scale Test Agent {i}",
                    "capabilities": [f"scale_cap_{i % 10}"],  # 10 different capabilities
                    "input_types": ["text"],
                    "output_types": ["json"]
                }
                registry.register_agent_capabilities(agent_data["agent_id"], agent_data)
            setup_time = (time.time() - setup_start) * 1000  # ms
            
            # Query phase - test search performance
            query_start = time.time()
            
            # Test multiple query types
            query_results = []
            for cap_id in range(10):
                agents = registry.find_agents_by_capability(f"scale_cap_{cap_id}")
                query_results.append(len(agents))
            
            query_time = (time.time() - query_start) * 1000  # ms
            
            # Statistics phase
            stats_start = time.time()
            stats = registry.get_capability_statistics()
            stats_time = (time.time() - stats_start) * 1000  # ms
            
            scalability_results[f"size_{size}"] = {
                "setup_time_ms": setup_time,
                "query_time_ms": query_time,
                "stats_time_ms": stats_time,
                "agents_registered": stats["total_agents"],
                "query_results_total": sum(query_results),
                "setup_rate_agents_per_ms": size / setup_time,
                "query_rate_queries_per_ms": 10 / query_time
            }
            
            print(f"     Setup: {setup_time:.2f}ms ({size/setup_time:.1f} agents/ms)")
            print(f"     Query: {query_time:.2f}ms (10 searches)")
            print(f"     Stats: {stats_time:.2f}ms")
        
        # Record benchmark
        benchmark_suite.record_benchmark("scalability_performance", scalability_results)
        
        # Verify scalability metrics
        size_1000_query_time = scalability_results["size_1000"]["query_time_ms"]
        size_5000_query_time = scalability_results["size_5000"]["query_time_ms"]
        
        # Query time shouldn't grow linearly with data size (should be sub-linear)
        scaling_factor = size_5000_query_time / size_1000_query_time
        assert scaling_factor < 3.0, f"Query time scaling factor {scaling_factor:.2f} too high"
        
        print(f"   Scaling Factor (5K vs 1K): {scaling_factor:.2f}x")
    
    @pytest.mark.asyncio
    async def test_api_gateway_performance(self, benchmark_suite):
        """Test API Gateway performance benchmarks"""
        print("\n🌐 Testing API Gateway Performance...")
        
        gateway = EnhancedAPIGateway({"host": "localhost", "port": 8889})
        await gateway.initialize()
        
        # Test memory usage
        memory_before = benchmark_suite._get_memory_kb()
        
        # Simulate load
        for i in range(100):
            test_agent = {
                "agent_id": f"gateway_test_{i}",
                "name": f"Gateway Test Agent {i}",
                "capabilities": ["gateway_test"],
                "endpoints": [{"path": f"/test/{i}", "methods": ["GET"]}]
            }
            await gateway.agent_registry.register_agent_capabilities_async(
                test_agent["agent_id"], test_agent
            )
        
        memory_after = benchmark_suite._get_memory_kb()
        memory_used = memory_after - memory_before
        
        # Test performance metrics
        metrics = gateway.performance_tracker.get_metrics()
        
        # Test instantiation
        instantiation_time = gateway.validate_instantiation_time()
        
        gateway_results = {
            "memory_used_kb": memory_used,
            "memory_limit_compliant": memory_used < 6.5,
            "instantiation_time_us": instantiation_time,
            "instantiation_compliant": instantiation_time < 3.0,
            "registered_agents": len(gateway.registered_agents),
            "system_metrics": metrics["system"] if "system" in metrics else {},
            "constraints_validation": metrics.get("constraints", {})
        }
        
        benchmark_suite.record_benchmark("api_gateway_performance", gateway_results)
        
        print(f"   Memory Used: {memory_used:.3f} KB")
        print(f"   Instantiation: {instantiation_time:.3f} μs")
        print(f"   Constraints: {'✅ PASS' if memory_used < 6.5 and instantiation_time < 3.0 else '❌ FAIL'}")
        
        # Assert constraints
        assert memory_used < 6.5, f"Gateway memory {memory_used:.3f}KB exceeds 6.5KB"
        assert instantiation_time < 3.0, f"Gateway instantiation {instantiation_time:.3f}μs exceeds 3μs"
    
    def test_stress_test_suite(self, benchmark_suite):
        """Comprehensive stress testing"""
        print("\n💪 Running Stress Test Suite...")
        
        # Create multiple registries for stress testing
        registries = []
        stress_results = {}
        
        # Phase 1: Memory stress test
        memory_start = benchmark_suite._get_memory_mb()
        
        for i in range(10):  # Create 10 registry instances
            registry = AgentCapabilityRegistry()
            
            # Add substantial data to each
            for j in range(500):  # 500 agents per registry = 5000 total
                agent_data = {
                    "agent_id": f"stress_{i}_{j}",
                    "name": f"Stress Test Agent {i}-{j}",
                    "capabilities": [f"stress_cap_{j % 50}"],  # 50 different capabilities
                    "input_types": ["text", "json"],
                    "output_types": ["json", "analysis"],
                    "metadata": {
                        "stress_test": True,
                        "registry_id": i,
                        "agent_number": j
                    }
                }
                registry.register_agent_capabilities(agent_data["agent_id"], agent_data)
            
            registries.append(registry)
        
        memory_peak = benchmark_suite._get_memory_mb()
        memory_used = memory_peak - memory_start
        
        # Phase 2: Performance stress test
        stress_start_time = time.time()
        
        # Concurrent operations across all registries
        operation_count = 0
        for registry in registries:
            # Multiple search operations
            for cap_id in range(10):
                agents = registry.find_agents_by_capability(f"stress_cap_{cap_id}")
                operation_count += len(agents)
            
            # Get statistics
            stats = registry.get_capability_statistics()
            operation_count += stats["total_agents"]
        
        stress_end_time = time.time()
        stress_duration = (stress_end_time - stress_start_time) * 1000  # ms
        
        stress_results = {
            "registries_created": len(registries),
            "total_agents": sum(reg.get_capability_statistics()["total_agents"] for reg in registries),
            "memory_used_mb": memory_used,
            "stress_duration_ms": stress_duration,
            "operations_performed": operation_count,
            "throughput_ops_per_sec": operation_count / (stress_duration / 1000)
        }
        
        benchmark_suite.record_benchmark("stress_test_suite", stress_results)
        
        print(f"   Registries: {len(registries)}")
        print(f"   Total Agents: {stress_results['total_agents']}")
        print(f"   Memory Used: {memory_used:.2f} MB")
        print(f"   Stress Duration: {stress_duration:.2f}ms")
        print(f"   Throughput: {stress_results['throughput_ops_per_sec']:.2f} ops/sec")
        
        # Cleanup
        del registries
        gc.collect()
        
        # Verify system still responsive
        quick_registry = AgentCapabilityRegistry()
        quick_start = time.time()
        quick_registry.register_agent_capabilities("post_stress_test", {"name": "Post Stress"})
        quick_time = (time.time() - quick_start) * 1000
        
        assert quick_time < 10, f"System slow after stress test: {quick_time:.2f}ms"
        print(f"   Post-stress responsiveness: {quick_time:.2f}ms ✅")


def run_complete_benchmark_suite():
    """Run all performance benchmarks and generate report"""
    print("🚀 Starting T-Developer Performance Benchmark Suite")
    print("=" * 60)
    
    # Initialize benchmark suite
    benchmark = PerformanceBenchmark()
    test_instance = TestRegistryPerformance()
    
    # Run all benchmarks
    try:
        test_instance.test_memory_constraint_6_5kb(benchmark)
        test_instance.test_instantiation_3_microseconds(benchmark)
        asyncio.run(test_instance.test_concurrent_performance(benchmark))
        test_instance.test_scalability_performance(benchmark)
        asyncio.run(test_instance.test_api_gateway_performance(benchmark))
        test_instance.test_stress_test_suite(benchmark)
        
        print("\n" + "=" * 60)
        print("✅ All Performance Benchmarks Completed Successfully!")
        
        # Generate final report
        report = benchmark.get_summary_report()
        
        # Save report to file
        report_path = "/home/ec2-user/T-DeveloperMVP/backend/tests/performance/benchmark_results.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📊 Detailed report saved to: {report_path}")
        
        return report
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        raise


if __name__ == "__main__":
    # Run benchmark suite directly
    report = run_complete_benchmark_suite()
    
    # Print summary
    print(f"\n📈 Final Performance Summary:")
    print(f"   Total Tests: {report['total_tests']}")
    print(f"   Memory Baseline: {report['baseline_memory_mb']:.2f} MB")
    print(f"   Memory Current: {report['current_memory_mb']:.2f} MB")
    
    # Check key constraints
    memory_test = report['test_results'].get('memory_constraint_6_5kb', {})
    instantiation_test = report['test_results'].get('instantiation_3_microseconds', {})
    
    if memory_test.get('passes_constraint') and instantiation_test.get('passes_constraint'):
        print("🎯 All Core Constraints: ✅ PASSED")
    else:
        print("⚠️  Some Core Constraints: ❌ FAILED")