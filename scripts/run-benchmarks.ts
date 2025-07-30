#!/usr/bin/env ts-node
// Benchmark execution script
import { BenchmarkRunner, defaultSuites } from '../backend/src/benchmarks';

async function main() {
  const runner = new BenchmarkRunner();
  
  console.log('🚀 Starting T-Developer Performance Benchmarks');
  
  try {
    for (const suite of defaultSuites) {
      console.log(`\n📊 Running suite: ${suite.name}`);
      await runner.runSuite(suite);
    }
    
    console.log('\n✅ All benchmarks completed successfully');
  } catch (error) {
    console.error('❌ Benchmark execution failed:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}