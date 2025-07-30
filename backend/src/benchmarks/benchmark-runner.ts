// SubTask 1.18.4: 벤치마크 실행 및 리포팅
import { AgentBenchmark } from './agent-benchmark';
import { SystemLoadTester } from './load-testing';
import { MemoryProfiler, ResourceMonitor } from './memory-profiler';

interface BenchmarkSuite {
  name: string;
  tests: BenchmarkTest[];
}

interface BenchmarkTest {
  name: string;
  type: 'agent' | 'load' | 'memory';
  config: any;
}

interface BenchmarkReport {
  suite: string;
  timestamp: Date;
  results: TestResult[];
  summary: {
    totalTests: number;
    passed: number;
    failed: number;
    duration: number;
  };
}

interface TestResult {
  name: string;
  type: string;
  success: boolean;
  duration: number;
  metrics: any;
  error?: string;
}

export class BenchmarkRunner {
  private agentBenchmark = new AgentBenchmark();
  private loadTester = new SystemLoadTester();
  private memoryProfiler = new MemoryProfiler();
  private resourceMonitor = new ResourceMonitor();
  
  async runSuite(suite: BenchmarkSuite): Promise<BenchmarkReport> {
    const startTime = Date.now();
    const results: TestResult[] = [];
    
    console.log(`Running benchmark suite: ${suite.name}`);
    
    // Start resource monitoring
    this.resourceMonitor.startMonitoring();
    
    for (const test of suite.tests) {
      console.log(`Running test: ${test.name}`);
      
      try {
        const result = await this.runTest(test);
        results.push(result);
        console.log(`✅ ${test.name} completed`);
      } catch (error: any) {
        results.push({
          name: test.name,
          type: test.type,
          success: false,
          duration: 0,
          metrics: {},
          error: error.message
        });
        console.log(`❌ ${test.name} failed: ${error.message}`);
      }
    }
    
    // Stop resource monitoring
    const resourceReport = this.resourceMonitor.stopMonitoring();
    
    const report: BenchmarkReport = {
      suite: suite.name,
      timestamp: new Date(),
      results,
      summary: {
        totalTests: results.length,
        passed: results.filter(r => r.success).length,
        failed: results.filter(r => !r.success).length,
        duration: Date.now() - startTime
      }
    };
    
    await this.generateReport(report, resourceReport);
    return report;
  }
  
  private async runTest(test: BenchmarkTest): Promise<TestResult> {
    const startTime = Date.now();
    let metrics: any = {};
    
    switch (test.type) {
      case 'agent':
        metrics = await this.agentBenchmark.benchmarkAgent(
          test.config.agentType,
          test.config
        );
        break;
        
      case 'load':
        metrics = await this.loadTester.runLoadTest(test.config);
        break;
        
      case 'memory':
        this.memoryProfiler.start(test.config.intervalMs || 1000);
        await this.delay(test.config.duration || 10000);
        metrics = this.memoryProfiler.stop();
        break;
        
      default:
        throw new Error(`Unknown test type: ${test.type}`);
    }
    
    return {
      name: test.name,
      type: test.type,
      success: true,
      duration: Date.now() - startTime,
      metrics
    };
  }
  
  private async generateReport(
    report: BenchmarkReport,
    resourceReport: any
  ): Promise<void> {
    const reportContent = {
      ...report,
      resourceUsage: resourceReport,
      recommendations: this.generateRecommendations(report)
    };
    
    // Save to file
    const fs = await import('fs/promises');
    const filename = `benchmark-${report.suite}-${Date.now()}.json`;
    await fs.writeFile(filename, JSON.stringify(reportContent, null, 2));
    
    console.log(`\n📊 Benchmark Report Generated: ${filename}`);
    this.printSummary(report);
  }
  
  private generateRecommendations(report: BenchmarkReport): string[] {
    const recommendations: string[] = [];
    
    // Analyze results and generate recommendations
    for (const result of report.results) {
      if (result.type === 'agent' && result.metrics?.latency?.p99 > 1000) {
        recommendations.push(`Agent ${result.name}: High P99 latency (${result.metrics.latency.p99}ms). Consider optimization.`);
      }
      
      if (result.type === 'load' && result.metrics?.throughput < 100) {
        recommendations.push(`Load test ${result.name}: Low throughput (${result.metrics.throughput} RPS). Scale up resources.`);
      }
      
      if (result.type === 'memory' && result.metrics?.leaks?.length > 0) {
        recommendations.push(`Memory test ${result.name}: ${result.metrics.leaks.length} potential memory leaks detected.`);
      }
    }
    
    return recommendations;
  }
  
  private printSummary(report: BenchmarkReport): void {
    console.log('\n📈 Benchmark Summary:');
    console.log(`Suite: ${report.suite}`);
    console.log(`Total Tests: ${report.summary.totalTests}`);
    console.log(`Passed: ${report.summary.passed}`);
    console.log(`Failed: ${report.summary.failed}`);
    console.log(`Duration: ${report.summary.duration}ms`);
    console.log(`Success Rate: ${((report.summary.passed / report.summary.totalTests) * 100).toFixed(2)}%`);
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Default benchmark suites
export const defaultSuites: BenchmarkSuite[] = [
  {
    name: 'agent-performance',
    tests: [
      {
        name: 'nl-input-agent',
        type: 'agent',
        config: {
          agentType: 'nl-input',
          iterations: 100,
          warmupIterations: 10,
          testData: [{ input: 'test data' }]
        }
      },
      {
        name: 'code-generation-agent',
        type: 'agent',
        config: {
          agentType: 'generation',
          iterations: 50,
          warmupIterations: 5,
          testData: [{ prompt: 'generate code' }]
        }
      }
    ]
  },
  {
    name: 'system-load',
    tests: [
      {
        name: 'api-load-test',
        type: 'load',
        config: {
          users: 50,
          duration: 30000,
          rampUp: 5000,
          rampDown: 5000,
          thinkTime: 1000
        }
      }
    ]
  },
  {
    name: 'memory-analysis',
    tests: [
      {
        name: 'memory-profiling',
        type: 'memory',
        config: {
          duration: 60000,
          intervalMs: 1000
        }
      }
    ]
  }
];