#!/usr/bin/env ts-node
// CI/CD System Test Script
import { CICDOrchestrator } from '../backend/src/cicd';

async function testCICD() {
  console.log('🚀 Testing CI/CD Pipeline System...\n');

  const orchestrator = new CICDOrchestrator();

  // Register default workflow
  const workflow = orchestrator.getDefaultWorkflow();
  orchestrator.registerWorkflow(workflow);

  console.log('📋 Registered workflow:', workflow.name);
  console.log('   Steps:', workflow.steps.map(s => s.name).join(' → '));

  // Test pipeline execution
  console.log('\n🔧 Testing build pipeline...');
  try {
    const buildResult = await orchestrator.executeWorkflow('ci-cd', {
      type: 'push',
      source: 'main',
      artifact: 'v1.0.0'
    });

    console.log('✅ Workflow execution:', buildResult.success ? 'SUCCESS' : 'FAILED');
    console.log('   Duration:', Math.round(buildResult.duration / 1000), 'seconds');
    console.log('   Steps completed:', buildResult.steps.filter(s => s.success).length, '/', buildResult.steps.length);

    if (buildResult.error) {
      console.log('   Error:', buildResult.error);
    }

    // Show step details
    console.log('\n📊 Step Details:');
    buildResult.steps.forEach((step, i) => {
      const status = step.success ? '✅' : '❌';
      const duration = Math.round(step.duration / 1000);
      console.log(`   ${i + 1}. ${status} ${step.name} (${duration}s)`);
      if (step.error) {
        console.log(`      Error: ${step.error}`);
      }
    });

  } catch (error: any) {
    console.error('❌ Workflow execution failed:', error.message);
  }

  // Test monitoring
  console.log('\n📈 System Status:');
  const status = orchestrator.getWorkflowStatus();
  console.log('   Health:', status.health);
  console.log('   Success Rate:', Math.round(status.successRate * 100) + '%');
  console.log('   Avg Duration:', Math.round(status.averageDuration / 1000) + 's');

  console.log('\n✅ CI/CD system test completed!');
}

// Run test
testCICD().catch(console.error);