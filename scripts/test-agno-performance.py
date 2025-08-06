#!/usr/bin/env python3

import sys
import os
import asyncio
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

async def test_performance_optimizer():
    print("🚀 Testing Agno Performance Optimizer...\n")
    
    try:
        from agno.performance_optimizer import AgnoPerformanceOptimizer
        
        # 성능 최적화기 초기화
        optimizer = AgnoPerformanceOptimizer()
        
        # 최적화 실행
        print("⚡ Running optimization...")
        await optimizer.optimize_agent_creation()
        
        # 벤치마크 실행
        print("📊 Running performance benchmark...")
        results = await optimizer.benchmark_performance()
        
        # 결과 출력
        print(f"✅ Instantiation time: {results['instantiation_time_us']:.2f}μs (target: ≤3μs)")
        print(f"✅ Memory per agent: {results['memory_per_agent_kb']:.2f}KB (target: ≤6.5KB)")
        print(f"✅ Target met: {results['target_met']}")
        print(f"📦 Preloaded modules: {results['preloaded_modules']}")
        print(f"🏊 Agent pool size: {results['agent_pool_size']}")
        print(f"💾 Memory pool size: {results['memory_pool_size']}")
        
        if results['target_met']:
            print("\n🎯 Performance targets achieved!")
        else:
            print("\n⚠️ Performance targets not met, optimization needed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_performance_optimizer())
    sys.exit(0 if success else 1)