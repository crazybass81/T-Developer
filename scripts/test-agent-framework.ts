#!/usr/bin/env ts-node

import { initializeAgentFramework, AgentType } from '../backend/src/agents/framework';
import { ExampleAgent } from '../backend/src/agents/examples/example-agent';
import { v4 as uuidv4 } from 'uuid';

async function testAgentFramework() {
  console.log('🧪 Testing Agent Framework...\n');
  
  // Initialize framework
  const { manager, communicationManager } = initializeAgentFramework();
  
  // Register example agent
  manager.registerAgentType('example', ExampleAgent);
  
  // Create and start agent
  const agentId = await manager.createAgent('example');
  console.log(`Created agent: ${agentId}`);
  
  await manager.startAgent(agentId, {
    projectId: 'test-project',
    userId: 'test-user',
    sessionId: 'test-session',
    metadata: { test: true }
  });
  
  // Send test message
  const message = {
    id: uuidv4(),
    type: 'request' as const,
    source: 'test-client',
    target: agentId,
    payload: {
      action: 'process_text',
      text: 'Hello world from T-Developer agent framework!'
    },
    timestamp: new Date()
  };
  
  console.log('\n📤 Sending message:', message.payload);
  
  const response = await manager.sendMessage(agentId, message);
  console.log('📥 Received response:', response.payload);
  
  // Check agent metrics
  console.log('\n📊 Agent Metrics:');
  const metrics = manager.getAgentMetrics();
  console.table(metrics);
  
  // List all agents
  console.log('\n📋 Active Agents:');
  const agents = manager.listAgents();
  console.table(agents);
  
  // Stop agent
  await manager.stopAgent(agentId);
  console.log('\n✅ Agent framework test completed!');
}

if (require.main === module) {
  testAgentFramework().catch(console.error);
}