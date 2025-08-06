#!/usr/bin/env node

const { AgentRegistry } = require('../backend/dist/orchestration/agent-registry');

async function testAgentRegistry() {
  console.log('🧪 Testing Agent Registry System...\n');

  try {
    // Create registry instance
    const registry = new AgentRegistry('t-developer-agents-test');
    
    // Test agent metadata
    const testAgent = {
      name: 'test-agent',
      version: '1.0.0',
      capabilities: ['text-processing', 'analysis'],
      maxConcurrent: 5,
      timeout: 30000
    };

    console.log('✅ 1. Registry instance created');

    // Test registration
    await registry.register(testAgent);
    console.log('✅ 2. Agent registered successfully');

    // Test listing agents
    const agents = await registry.listAgents();
    console.log(`✅ 3. Listed ${agents.length} agents`);

    // Test status check
    const status = registry.getAgentStatus('test-agent');
    console.log(`✅ 4. Agent status: ${status ? 'found' : 'not found'}`);

    // Test status update
    await registry.updateAgentStatus('test-agent', 'active');
    console.log('✅ 5. Agent status updated');

    // Test unregistration
    await registry.unregister('test-agent');
    console.log('✅ 6. Agent unregistered');

    console.log('\n🎉 All Agent Registry tests passed!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  testAgentRegistry();
}

module.exports = { testAgentRegistry };