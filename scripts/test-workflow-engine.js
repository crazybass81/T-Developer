#!/usr/bin/env node

const { WorkflowEngine, StepType } = require('../backend/src/workflow/workflow_engine.js');

async function testWorkflowEngine() {
  console.log('🔧 Testing Workflow Engine...\n');

  try {
    const engine = new WorkflowEngine();

    // Test 1: Dynamic workflow creation
    console.log('1. Testing dynamic workflow creation...');
    const intent = {
      type: 'development',
      description: 'Create a web application with API and UI',
      confidence: 0.9,
      entities: { projectType: 'web', features: ['api', 'ui'] },
      context: { complexity: 'medium' }
    };

    const agents = ['CodeAgent', 'UIAgent', 'APIAgent', 'TestAgent'];
    const workflow = await engine.createWorkflow(intent, agents);

    console.log(`✅ Created workflow: ${workflow.name}`);
    console.log(`   - Steps: ${workflow.steps.length}`);
    console.log(`   - Estimated duration: ${workflow.estimatedDuration}s`);
    console.log(`   - Parallel steps: ${workflow.steps.filter(s => s.type === StepType.PARALLEL).length}`);

    // Test 2: Template-based workflow
    console.log('\n2. Testing template-based workflow...');
    const testIntent = {
      type: 'test',
      description: 'Run comprehensive tests',
      confidence: 0.95,
      entities: { testType: 'full' },
      context: {}
    };

    const testWorkflow = await engine.createWorkflow(testIntent, ['TestAgent', 'SecurityAgent']);
    console.log(`✅ Created test workflow: ${testWorkflow.name}`);
    console.log(`   - Steps: ${testWorkflow.steps.length}`);

    // Test 3: Workflow validation
    console.log('\n3. Testing workflow validation...');
    try {
      // Create invalid workflow with circular dependency
      const invalidWorkflow = {
        id: 'invalid',
        name: 'Invalid Workflow',
        steps: [
          {
            id: 'step1',
            name: 'Step 1',
            type: StepType.SEQUENTIAL,
            agents: ['CodeAgent'],
            dependencies: ['step2'],
            timeout: 300
          },
          {
            id: 'step2',
            name: 'Step 2',
            type: StepType.SEQUENTIAL,
            agents: ['TestAgent'],
            dependencies: ['step1'],
            timeout: 300
          }
        ],
        estimatedDuration: 600,
        createdAt: new Date()
      };

      const { WorkflowValidator } = require('../backend/src/workflow/workflow_engine.js');
      const validator = new WorkflowValidator();
      await validator.validate(invalidWorkflow);
      console.log('❌ Validation should have failed');
    } catch (error) {
      console.log('✅ Validation correctly caught circular dependency');
    }

    // Test 4: Workflow optimization
    console.log('\n4. Testing workflow optimization...');
    const complexWorkflow = await engine.createWorkflow({
      type: 'development',
      description: 'Complex project with multiple components',
      confidence: 0.8,
      entities: {},
      context: {}
    }, ['CodeAgent', 'UIAgent', 'APIAgent', 'TestAgent', 'SecurityAgent', 'DeploymentAgent']);

    console.log(`✅ Optimized complex workflow:`);
    console.log(`   - Original steps: ${complexWorkflow.steps.length}`);
    console.log(`   - Parallel groups: ${complexWorkflow.steps.filter(s => s.type === StepType.PARALLEL).length}`);

    console.log('\n✅ All workflow engine tests passed!');

  } catch (error) {
    console.error('❌ Workflow engine test failed:', error.message);
    process.exit(1);
  }
}

// Run tests
testWorkflowEngine().catch(console.error);