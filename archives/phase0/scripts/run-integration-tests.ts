#!/usr/bin/env ts-node
// Integration test execution script
import { runAllIntegrationTests } from '../backend/src/tests/integration';

async function main() {
  console.log('🚀 Starting T-Developer Integration Test Suite');
  console.log('============================================\n');
  
  try {
    await runAllIntegrationTests();
  } catch (error) {
    console.error('❌ Integration tests failed:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}