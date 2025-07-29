#!/usr/bin/env ts-node

import { createBedrockConfig, BedrockNLInputAgent } from '../backend/src/integrations/bedrock';
import { v4 as uuidv4 } from 'uuid';

async function testBedrockIntegration() {
  console.log('🤖 Testing Bedrock AgentCore Integration...\n');
  
  try {
    // Create Bedrock configuration (using mock values for testing)
    const bedrockConfig = createBedrockConfig(
      process.env.BEDROCK_AGENT_ID || 'mock-agent-id',
      process.env.BEDROCK_AGENT_ALIAS_ID || 'mock-alias-id',
      'us-east-1',
      process.env.BEDROCK_KNOWLEDGE_BASE_ID
    );
    
    console.log('📋 Bedrock Configuration:', {
      agentId: bedrockConfig.agentId,
      agentAliasId: bedrockConfig.agentAliasId,
      region: bedrockConfig.region,
      hasKnowledgeBase: !!bedrockConfig.knowledgeBaseId
    });
    
    // Create Bedrock-powered agent
    const nlAgent = new BedrockNLInputAgent(bedrockConfig);
    
    // Start agent
    await nlAgent.start({
      projectId: 'test-project',
      userId: 'test-user',
      sessionId: 'test-session',
      metadata: { test: true }
    });
    
    console.log('✅ Bedrock agent started');
    
    // Test message processing
    const message = {
      id: uuidv4(),
      type: 'request' as const,
      source: 'test-client',
      target: nlAgent.id,
      payload: {
        action: 'process_natural_language',
        text: 'I want to build a web application for managing tasks with user authentication and real-time updates'
      },
      timestamp: new Date()
    };
    
    console.log('\n📤 Sending test message...');
    
    if (process.env.BEDROCK_AGENT_ID && process.env.BEDROCK_AGENT_ALIAS_ID) {
      // Real Bedrock test
      const response = await nlAgent.handleMessage(message);
      console.log('📥 Bedrock Response:', response.payload);
    } else {
      // Mock test
      console.log('⚠️ Bedrock credentials not found, running mock test');
      console.log('📥 Mock Response: Natural language processing would happen here');
    }
    
    // Show agent capabilities
    console.log('\n🔧 Agent Capabilities:');
    const capabilities = nlAgent.getCapabilities();
    capabilities.forEach(cap => {
      console.log(`  - ${cap.name}: ${cap.description}`);
    });
    
    // Stop agent
    await nlAgent.stop();
    console.log('\n✅ Bedrock integration test completed!');
    
  } catch (error) {
    console.error('❌ Bedrock integration test failed:', error);
    
    if (error instanceof Error && error.message.includes('credentials')) {
      console.log('\n💡 To test with real Bedrock:');
      console.log('1. Set up AWS credentials');
      console.log('2. Create a Bedrock agent in AWS Console');
      console.log('3. Set environment variables:');
      console.log('   - BEDROCK_AGENT_ID');
      console.log('   - BEDROCK_AGENT_ALIAS_ID');
      console.log('   - BEDROCK_KNOWLEDGE_BASE_ID (optional)');
    }
  }
}

if (require.main === module) {
  testBedrockIntegration().catch(console.error);
}