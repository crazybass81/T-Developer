// Task 1.18: 성능 벤치마크 도구 - Entry Point
export { AgentBenchmark } from './agent-benchmark';
export { SystemLoadTester, VirtualUser } from './load-testing';
export { MemoryProfiler, ResourceMonitor } from './memory-profiler';
export { BenchmarkRunner, defaultSuites } from './benchmark-runner';

// Quick start function
export async function runDefaultBenchmarks(): Promise<void> {
  const { BenchmarkRunner, defaultSuites } = await import('./benchmark-runner');
  
  const runner = new BenchmarkRunner();
  
  for (const suite of defaultSuites) {
    await runner.runSuite(suite);
  }
}

// CLI interface
if (require.main === module) {
  runDefaultBenchmarks()
    .then(() => console.log('All benchmarks completed'))
    .catch(console.error);
}