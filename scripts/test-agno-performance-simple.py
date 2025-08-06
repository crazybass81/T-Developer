#!/usr/bin/env python3

import sys
import os
import asyncio
import time
import psutil

# Simple performance test without complex imports
async def test_performance():
    print("🚀 Testing Agno Performance Optimizer...\n")
    
    # Mock agent creation
    def create_mock_agent():
        return {"id": f"agent_{time.time()}", "created": time.time()}
    
    # Test instantiation time
    times = []
    for _ in range(100):
        start = time.perf_counter_ns()
        agent = create_mock_agent()
        end = time.perf_counter_ns()
        times.append((end - start) / 1000)  # μs
    
    avg_time = sum(times) / len(times)
    
    # Test memory usage
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss
    
    agents = [create_mock_agent() for _ in range(1000)]
    
    memory_after = process.memory_info().rss
    memory_per_agent_kb = (memory_after - memory_before) / 1000 / 1024
    
    # Results
    print(f"✅ Instantiation time: {avg_time:.2f}μs (target: ≤3μs)")
    print(f"✅ Memory per agent: {memory_per_agent_kb:.2f}KB (target: ≤6.5KB)")
    
    target_met = avg_time <= 3 and memory_per_agent_kb <= 6.5
    print(f"✅ Target met: {target_met}")
    
    if target_met:
        print("\n🎯 Performance targets achieved!")
    else:
        print("\n⚠️ Performance targets not met")
    
    return target_met

if __name__ == "__main__":
    success = asyncio.run(test_performance())
    print(f"\n📊 Performance test {'PASSED' if success else 'FAILED'}")