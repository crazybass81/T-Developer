#!/usr/bin/env node

const { ExecutionTracker } = require('../backend/dist/workflow/execution-tracker');
const WebSocket = require('ws');

async function testExecutionTracker() {
  console.log('🔍 Testing Execution Tracker...');

  const tracker = new ExecutionTracker();
  
  // Mock workflow
  const workflow = {
    steps: [
      { id: 'step1', name: 'Initialize' },
      { id: 'step2', name: 'Process' },
      { id: 'step3', name: 'Complete' }
    ]
  };

  const workflowId = 'test-workflow-001';

  try {
    // Test 1: Track execution
    await tracker.trackExecution(workflowId, workflow);
    console.log('✅ Execution tracking started');

    // Test 2: Update progress
    await tracker.updateStepProgress(workflowId, 'step1', 33);
    await tracker.updateStepProgress(workflowId, 'step2', 66);
    console.log('✅ Progress updates successful');

    // Test 3: Get state
    const state = tracker.getExecutionState(workflowId);
    console.log('✅ State retrieved:', {
      status: state?.status,
      currentStep: state?.currentStep,
      progress: state?.progress
    });

    // Test 4: Complete execution
    await tracker.completeExecution(workflowId, { success: true });
    const finalState = tracker.getExecutionState(workflowId);
    console.log('✅ Execution completed:', {
      status: finalState?.status,
      duration: finalState?.endTime ? 
        finalState.endTime.getTime() - finalState.startTime.getTime() : 0
    });

    console.log('🎉 All execution tracker tests passed!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  testExecutionTracker();
}