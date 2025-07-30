// Simple test runner for benchmarks
const { performance } = require('perf_hooks');

// Mock Agent class for testing
class MockAgent {
  async execute(data) {
    // Simulate work with random delay
    await new Promise(resolve => setTimeout(resolve, Math.random() * 100 + 50));
    
    if (Math.random() < 0.05) { // 5% failure rate
      throw new Error('Mock execution failed');
    }
    
    return { result: 'success', data };
  }
}

// Simplified AgentBenchmark for testing
class AgentBenchmark {
  async benchmarkAgent(agentType, config) {
    const agent = new MockAgent();
    const results = [];
    
    console.log(`🔥 Warming up ${config.warmupIterations} iterations...`);
    for (let i = 0; i < config.warmupIterations; i++) {
      await agent.execute(config.testData[0]);
    }
    
    console.log(`📊 Running ${config.iterations} benchmark iterations...`);
    for (let i = 0; i < config.iterations; i++) {
      const metric = await this.measureExecution(
        agent,
        config.testData[i % config.testData.length]
      );
      results.push(metric);
      
      if ((i + 1) % 10 === 0) {
        console.log(`  Progress: ${i + 1}/${config.iterations}`);
      }
    }
    
    return this.analyzeResults(results);
  }
  
  async measureExecution(agent, testData) {
    const startMemory = process.memoryUsage();
    const startCpu = process.cpuUsage();
    const startTime = performance.now();
    
    try {
      await agent.execute(testData);
      const endTime = performance.now();
      const endCpu = process.cpuUsage(startCpu);
      const endMemory = process.memoryUsage();
      
      return {
        duration: endTime - startTime,
        cpu: {
          user: endCpu.user / 1000,
          system: endCpu.system / 1000
        },
        memory: {
          heapUsed: endMemory.heapUsed - startMemory.heapUsed,
          rss: endMemory.rss - startMemory.rss
        },
        success: true
      };
    } catch (error) {
      return {
        duration: performance.now() - startTime,
        cpu: process.cpuUsage(startCpu),
        memory: process.memoryUsage(),
        success: false,
        error: error.message
      };
    }
  }
  
  analyzeResults(metrics) {
    const durations = metrics.map(m => m.duration);
    const successCount = metrics.filter(m => m.success).length;
    
    return {
      summary: {
        iterations: metrics.length,
        successRate: successCount / metrics.length,
        totalDuration: durations.reduce((a, b) => a + b, 0)
      },
      latency: {
        min: Math.min(...durations),
        max: Math.max(...durations),
        mean: durations.reduce((a, b) => a + b, 0) / durations.length,
        p95: this.percentile(durations, 0.95),
        p99: this.percentile(durations, 0.99)
      },
      throughput: {
        rps: metrics.length / (durations.reduce((a, b) => a + b, 0) / 1000)
      }
    };
  }
  
  percentile(arr, p) {
    const sorted = [...arr].sort((a, b) => a - b);
    const index = Math.ceil(p * sorted.length) - 1;
    return sorted[index];
  }
}

// Test runner
async function runTest() {
  console.log('🚀 Starting T-Developer Benchmark Test\n');
  
  const benchmark = new AgentBenchmark();
  
  const config = {
    iterations: 50,
    warmupIterations: 5,
    testData: [
      { input: 'test data 1' },
      { input: 'test data 2' },
      { input: 'test data 3' }
    ]
  };
  
  try {
    const startTime = Date.now();
    const result = await benchmark.benchmarkAgent('mock-agent', config);
    const totalTime = Date.now() - startTime;
    
    console.log('\n📈 Benchmark Results:');
    console.log('==================');
    console.log(`Total Iterations: ${result.summary.iterations}`);
    console.log(`Success Rate: ${(result.summary.successRate * 100).toFixed(2)}%`);
    console.log(`Total Duration: ${totalTime}ms`);
    console.log('\nLatency Metrics:');
    console.log(`  Min: ${result.latency.min.toFixed(2)}ms`);
    console.log(`  Max: ${result.latency.max.toFixed(2)}ms`);
    console.log(`  Mean: ${result.latency.mean.toFixed(2)}ms`);
    console.log(`  P95: ${result.latency.p95.toFixed(2)}ms`);
    console.log(`  P99: ${result.latency.p99.toFixed(2)}ms`);
    console.log('\nThroughput:');
    console.log(`  RPS: ${result.throughput.rps.toFixed(2)}`);
    
    console.log('\n✅ Benchmark test completed successfully!');
    
  } catch (error) {
    console.error('❌ Benchmark test failed:', error.message);
    process.exit(1);
  }
}

// Run the test
runTest();