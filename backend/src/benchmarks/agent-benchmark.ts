// SubTask 1.18.1: 에이전트 성능 측정
import { performance } from 'perf_hooks';

interface BenchmarkConfig {
  iterations: number;
  warmupIterations: number;
  testData: any[];
  cooldownMs?: number;
}

interface PerformanceMetric {
  duration: number;
  cpu: { user: number; system: number };
  memory: { heapUsed: number; rss: number };
  success: boolean;
  error?: string;
}

interface BenchmarkResult {
  summary: {
    iterations: number;
    successRate: number;
    totalDuration: number;
  };
  latency: {
    min: number;
    max: number;
    mean: number;
    p95: number;
    p99: number;
  };
  throughput: {
    rps: number;
  };
}

export class AgentBenchmark {
  async benchmarkAgent(
    agentType: string,
    config: BenchmarkConfig
  ): Promise<BenchmarkResult> {
    const agent = await this.createAgent(agentType);
    const results: PerformanceMetric[] = [];
    
    // Warmup
    for (let i = 0; i < config.warmupIterations; i++) {
      await agent.execute(config.testData[0]);
    }
    
    // Main benchmark
    for (let i = 0; i < config.iterations; i++) {
      const metric = await this.measureExecution(
        agent,
        config.testData[i % config.testData.length]
      );
      results.push(metric);
      
      if (config.cooldownMs) {
        await this.delay(config.cooldownMs);
      }
    }
    
    return this.analyzeResults(results);
  }
  
  private async measureExecution(agent: any, testData: any): Promise<PerformanceMetric> {
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
    } catch (error: any) {
      return {
        duration: performance.now() - startTime,
        cpu: process.cpuUsage(startCpu),
        memory: process.memoryUsage(),
        success: false,
        error: error.message
      };
    }
  }
  
  private analyzeResults(metrics: PerformanceMetric[]): BenchmarkResult {
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
  
  private percentile(arr: number[], p: number): number {
    const sorted = [...arr].sort((a, b) => a - b);
    const index = Math.ceil(p * sorted.length) - 1;
    return sorted[index];
  }
  
  private async createAgent(type: string): Promise<any> {
    // Mock agent for testing
    return {
      execute: async (data: any) => {
        await this.delay(Math.random() * 100);
        return { result: 'success', data };
      }
    };
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}