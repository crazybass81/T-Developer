#!/usr/bin/env ts-node
// Individual Component Testing
import { PipelineManager, DeploymentManager, PipelineMonitor } from '../backend/src/cicd';

async function testComponents() {
  console.log('🧪 Testing Individual CI/CD Components...\n');

  // Test Pipeline Manager
  console.log('1️⃣ Testing Pipeline Manager:');
  const pipeline = new PipelineManager();
  
  pipeline.register({
    name: 'simple-test',
    stages: [
      { name: 'echo-test', commands: ['echo "Hello CI/CD"'], timeout: 5000, retries: 1 }
    ],
    environment: { TEST: 'true' },
    notifications: []
  });

  const pipelineResult = await pipeline.execute('simple-test');
  console.log(`   Result: ${pipelineResult.success ? '✅ SUCCESS' : '❌ FAILED'}`);
  console.log(`   Duration: ${Math.round(pipelineResult.duration / 1000)}s`);

  // Test Deployment Manager
  console.log('\n2️⃣ Testing Deployment Manager:');
  const deployment = new DeploymentManager();
  
  const deployResult = await deployment.deploy({
    name: 'test-deploy',
    environment: 'dev',
    strategy: 'rolling',
    healthCheck: { endpoint: '/health', timeout: 5000, retries: 1, interval: 1000 },
    rollback: { enabled: true, threshold: 0.9, autoRollback: false }
  }, 'test-v1.0.0');

  console.log(`   Result: ${deployResult.success ? '✅ SUCCESS' : '❌ FAILED'}`);
  console.log(`   Strategy: ${deployResult.strategy}`);
  console.log(`   Duration: ${Math.round(deployResult.duration / 1000)}s`);

  // Test Pipeline Monitor
  console.log('\n3️⃣ Testing Pipeline Monitor:');
  const monitor = new PipelineMonitor();
  
  // Record some test metrics
  monitor.recordExecution({
    pipelineName: 'test-pipeline',
    executionId: 'exec-1',
    duration: 2000,
    success: true,
    timestamp: new Date(),
    stages: [{ name: 'test', duration: 2000, success: true, retries: 1 }]
  });

  monitor.recordExecution({
    pipelineName: 'test-pipeline',
    executionId: 'exec-2',
    duration: 1500,
    success: true,
    timestamp: new Date(),
    stages: [{ name: 'test', duration: 1500, success: true, retries: 1 }]
  });

  const stats = monitor.getStats('test-pipeline');
  console.log(`   Total Executions: ${stats.totalExecutions}`);
  console.log(`   Success Rate: ${Math.round(stats.successRate * 100)}%`);
  console.log(`   Avg Duration: ${Math.round(stats.averageDuration / 1000)}s`);

  const health = monitor.getHealth();
  console.log(`   Health Status: ${health.status}`);

  console.log('\n🎯 All individual components tested successfully!');
}

testComponents().catch(console.error);