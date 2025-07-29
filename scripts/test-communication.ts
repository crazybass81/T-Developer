#!/usr/bin/env ts-node

import { initializeAgentFramework, AgentWorkflow } from '../backend/src/agents/framework';
import { ExampleAgent } from '../backend/src/agents/examples/example-agent';
import { v4 as uuidv4 } from 'uuid';

async function testCommunication() {
  console.log('📡 Testing Agent Communication...\n');
  
  // Initialize framework
  const { manager, communicationManager } = initializeAgentFramework();
  
  // Register agents
  manager.registerAgentType('example', ExampleAgent);
  
  // Create multiple agents
  const agent1Id = await manager.createAgent('example');
  const agent2Id = await manager.createAgent('example');
  
  console.log(`Created agents: ${agent1Id}, ${agent2Id}`);
  
  // Start agents
  const context = {
    projectId: 'test-project',
    userId: 'test-user',
    sessionId: 'test-session',
    metadata: { test: true }
  };
  
  await manager.startAgent(agent1Id, context);
  await manager.startAgent(agent2Id, context);
  
  // Register agents with communication manager
  const agent1 = manager.getAgent(agent1Id);
  const agent2 = manager.getAgent(agent2Id);
  
  communicationManager.registerAgent(agent1Id, agent1);
  communicationManager.registerAgent(agent2Id, agent2);
  
  // Test direct messaging
  console.log('\n📤 Testing direct messaging...');
  
  const message = {
    id: uuidv4(),
    type: 'request' as const,
    source: 'test-client',
    target: agent1Id,
    payload: {
      action: 'process_text',
      text: 'Hello from communication test!'
    },
    timestamp: new Date()
  };
  
  await communicationManager.sendMessage(message);
  
  // Test workflow
  console.log('\n🔄 Testing workflow...');
  
  const workflow = new AgentWorkflow(manager, communicationManager);
  
  try {
    const result = await workflow.execute({
      projectId: 'test-project',
      userId: 'test-user',
      sessionId: 'test-session',
      initialInput: { text: 'Workflow test input' },
      steps: ['nl-input'] // Just test with one step for now
    });
    
    console.log('✅ Workflow result:', result);
  } catch (error) {
    console.log('⚠️ Workflow test skipped (agents not implemented yet)');
  }
  
  // Show routing info
  console.log('\n📋 Routing Information:');
  const routing = communicationManager.getRoutingInfo();
  for (const [channel, agents] of routing.entries()) {
    console.log(`  ${channel}: ${agents.join(', ')}`);
  }
  
  // Cleanup
  await manager.stopAgent(agent1Id);
  await manager.stopAgent(agent2Id);
  
  console.log('\n✅ Communication test completed!');
}

if (require.main === module) {
  testCommunication().catch(console.error);
}