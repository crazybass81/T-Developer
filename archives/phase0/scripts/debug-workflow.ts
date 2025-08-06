#!/usr/bin/env ts-node
// Debug CI/CD Workflow
import { CICDOrchestrator } from '../backend/src/cicd';

async function debugWorkflow() {
  console.log('🔍 Debugging CI/CD Workflow...\n');

  const orchestrator = new CICDOrchestrator();
  
  // Test simple pipeline first
  console.log('1️⃣ Testing simple pipeline execution:');
  try {
    const result = await orchestrator['pipelineManager'].execute('build');
    console.log(`   Pipeline result: ${result.success ? 'SUCCESS' : 'FAILED'}`);
    console.log(`   Error: ${result.error || 'None'}`);
    console.log(`   Stages: ${result.stages.length}`);
    
    result.stages.forEach((stage, i) => {
      console.log(`   Stage ${i+1}: ${stage.name} - ${stage.success ? 'OK' : 'FAIL'}`);
      if (stage.error) console.log(`     Error: ${stage.error}`);
    });
  } catch (error: any) {
    console.log(`   Exception: ${error.message}`);
  }

  // Test workflow step by step
  console.log('\n2️⃣ Testing workflow step execution:');
  try {
    const step = {
      name: 'test-step',
      type: 'pipeline' as const,
      pipeline: 'build',
      continueOnFailure: false
    };
    
    const trigger = {
      type: 'manual',
      source: 'debug',
      artifact: 'test-v1.0.0'
    };

    const stepResult = await orchestrator['executeWorkflowStep'](step, trigger);
    console.log(`   Step result: ${stepResult.success ? 'SUCCESS' : 'FAILED'}`);
    console.log(`   Duration: ${Math.round(stepResult.duration / 1000)}s`);
    if (stepResult.error) console.log(`   Error: ${stepResult.error}`);
  } catch (error: any) {
    console.log(`   Exception: ${error.message}`);
  }

  // Test with mock commands
  console.log('\n3️⃣ Testing with working commands:');
  orchestrator['pipelineManager'].register({
    name: 'working-build',
    stages: [
      { name: 'test', commands: ['echo "test passed"'], timeout: 5000, retries: 1 }
    ],
    environment: { NODE_ENV: 'test' },
    notifications: []
  });

  try {
    const result = await orchestrator['pipelineManager'].execute('working-build');
    console.log(`   Working pipeline: ${result.success ? 'SUCCESS' : 'FAILED'}`);
    if (result.error) console.log(`   Error: ${result.error}`);
  } catch (error: any) {
    console.log(`   Exception: ${error.message}`);
  }
}

debugWorkflow().catch(console.error);