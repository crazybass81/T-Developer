// Complete benchmark system test
console.log('🎯 T-Developer Benchmark System - Complete Test Suite\n');
console.log('====================================================\n');

async function runAllTests() {
  const tests = [
    {
      name: 'Agent Performance Benchmark',
      file: './test-benchmark.js',
      description: 'Tests agent execution performance with latency and throughput metrics'
    },
    {
      name: 'Memory Profiling',
      file: './test-memory-profiler.js', 
      description: 'Tests memory usage tracking and leak detection'
    },
    {
      name: 'Load Testing',
      file: './test-load-testing.js',
      description: 'Tests system under concurrent user load'
    }
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (const test of tests) {
    console.log(`\n🧪 Running: ${test.name}`);
    console.log(`📝 ${test.description}`);
    console.log('─'.repeat(50));
    
    try {
      const { spawn } = require('child_process');
      
      await new Promise((resolve, reject) => {
        const child = spawn('node', [test.file], { stdio: 'inherit' });
        
        child.on('close', (code) => {
          if (code === 0) {
            resolve();
          } else {
            reject(new Error(`Test failed with code ${code}`));
          }
        });
        
        child.on('error', reject);
      });
      
      console.log(`✅ ${test.name} - PASSED`);
      passed++;
      
    } catch (error) {
      console.log(`❌ ${test.name} - FAILED: ${error.message}`);
      failed++;
    }
  }
  
  console.log('\n' + '='.repeat(50));
  console.log('📊 BENCHMARK SYSTEM TEST SUMMARY');
  console.log('='.repeat(50));
  console.log(`Total Tests: ${tests.length}`);
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);
  console.log(`Success Rate: ${((passed / tests.length) * 100).toFixed(2)}%`);
  
  if (failed === 0) {
    console.log('\n🎉 ALL BENCHMARK TESTS PASSED!');
    console.log('✨ The T-Developer benchmark system is working correctly.');
    console.log('\n📋 Available Features:');
    console.log('  • Agent performance measurement');
    console.log('  • Memory profiling and leak detection');
    console.log('  • Load testing with virtual users');
    console.log('  • Comprehensive reporting');
    console.log('  • P95/P99 latency analysis');
    console.log('  • Throughput measurement');
  } else {
    console.log(`\n⚠️  ${failed} test(s) failed. Please check the output above.`);
    process.exit(1);
  }
}

runAllTests().catch(console.error);