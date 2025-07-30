// Task 1.19: 통합 테스트 환경 - Entry Point
export { TestEnvironmentManager } from './test-environment';
export { IntegrationTestRunner } from './test-runner';
export { apiTestSuite } from './api-tests';
export { databaseTestSuite } from './database-tests';
export { agentTestSuite } from './agent-tests';

import { IntegrationTestRunner } from './test-runner';
import { apiTestSuite } from './api-tests';
import { databaseTestSuite } from './database-tests';
import { agentTestSuite } from './agent-tests';

// Main integration test runner
export async function runAllIntegrationTests(): Promise<void> {
  const runner = new IntegrationTestRunner();
  
  const suites = [
    apiTestSuite,
    databaseTestSuite,
    agentTestSuite
  ];
  
  console.log('🧪 Starting T-Developer Integration Tests\n');
  
  let totalTests = 0;
  let totalPassed = 0;
  let totalFailed = 0;
  
  for (const suite of suites) {
    console.log(`\n📋 Running ${suite.name}...`);
    console.log('='.repeat(50));
    
    const results = await runner.runSuite(suite);
    
    const passed = results.filter(r => r.success).length;
    const failed = results.filter(r => !r.success).length;
    
    totalTests += results.length;
    totalPassed += passed;
    totalFailed += failed;
    
    console.log(`\n📊 ${suite.name} Results:`);
    console.log(`  Tests: ${results.length}`);
    console.log(`  Passed: ${passed}`);
    console.log(`  Failed: ${failed}`);
    console.log(`  Success Rate: ${((passed / results.length) * 100).toFixed(2)}%`);
    
    if (failed > 0) {
      console.log('\n❌ Failed Tests:');
      results.filter(r => !r.success).forEach(r => {
        console.log(`  - ${r.name}: ${r.error}`);
      });
    }
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('📈 INTEGRATION TEST SUMMARY');
  console.log('='.repeat(60));
  console.log(`Total Test Suites: ${suites.length}`);
  console.log(`Total Tests: ${totalTests}`);
  console.log(`Passed: ${totalPassed}`);
  console.log(`Failed: ${totalFailed}`);
  console.log(`Overall Success Rate: ${((totalPassed / totalTests) * 100).toFixed(2)}%`);
  
  if (totalFailed === 0) {
    console.log('\n🎉 ALL INTEGRATION TESTS PASSED!');
    console.log('✨ T-Developer integration is working correctly.');
  } else {
    console.log(`\n⚠️  ${totalFailed} integration test(s) failed.`);
    process.exit(1);
  }
}

// CLI interface
if (require.main === module) {
  runAllIntegrationTests()
    .then(() => console.log('\n✅ Integration tests completed'))
    .catch(console.error);
}