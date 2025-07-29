#!/usr/bin/env ts-node

import { 
  createAgnoConfig, 
  AgnoNLInputAgent, 
  initializeGlobalAgnoMonitoring 
} from '../backend/src/integrations/agno';
import { v4 as uuidv4 } from 'uuid';

async function testAgnoMonitoring() {
  console.log('🔍 Testing Agno Monitoring Integration...\n');
  
  try {
    // Create Agno configuration (using mock values for testing)
    const agnoConfig = createAgnoConfig(
      process.env.AGNO_API_KEY || 'mock-api-key',
      process.env.AGNO_PROJECT_ID || 'mock-project-id',
      'development',
      process.env.AGNO_ENDPOINT || 'https://mock-agno-api.com'
    );
    
    console.log('📋 Agno Configuration:', {
      projectId: agnoConfig.projectId,
      environment: agnoConfig.environment,
      endpoint: agnoConfig.endpoint,
      batchSize: agnoConfig.batchSize,
      flushInterval: agnoConfig.flushInterval
    });
    
    // Initialize global monitoring
    const globalClient = initializeGlobalAgnoMonitoring(agnoConfig);
    
    // Create Agno-monitored agent
    const nlAgent = new AgnoNLInputAgent(agnoConfig);
    
    // Start agent
    await nlAgent.start({
      projectId: 'test-project-123',
      userId: 'test-user-456',
      sessionId: 'test-session-789',
      metadata: { test: true }
    });
    
    console.log('✅ Agno-monitored agent started');
    
    // Test monitored message processing
    const message = {
      id: uuidv4(),
      type: 'request' as const,
      source: 'test-client',
      target: nlAgent.id,
      payload: {
        action: 'process_natural_language_with_monitoring',
        text: 'Build a social media platform with real-time messaging and user profiles'
      },
      timestamp: new Date()
    };
    
    console.log('\n📤 Sending monitored message...');
    
    if (process.env.AGNO_API_KEY && process.env.AGNO_PROJECT_ID) {
      // Real Agno test
      const response = await nlAgent.handleMessage(message);
      console.log('📥 Monitored Response:', response.payload);
    } else {
      // Mock test
      console.log('⚠️ Agno credentials not found, running mock test');
      
      // Simulate monitoring calls
      await globalClient.sendMetric({
        name: 'test.agent.duration',
        value: 1250,
        tags: {
          agent: 'nl-input',
          operation: 'process_text',
          status: 'success'
        }
      });
      
      await globalClient.sendEvent({
        type: 'agent_operation',
        data: {
          agent: 'nl-input',
          operation: 'process_text',
          duration: 1250,
          success: true
        }
      });
      
      await globalClient.monitorProjectProgress(
        'test-project-123',
        'natural_language_processing',
        100,
        { confidence: 0.85 }
      );
      
      console.log('📊 Mock monitoring data sent');
    }
    
    // Show agent capabilities
    console.log('\n🔧 Monitored Agent Capabilities:');
    const capabilities = nlAgent.getCapabilities();
    capabilities.forEach(cap => {
      console.log(`  - ${cap.name}: ${cap.description}`);
    });
    
    // Test error tracking
    console.log('\n🚨 Testing error tracking...');
    try {
      await globalClient.trackError(
        new Error('Test error for monitoring'),
        {
          agent: 'nl-input',
          operation: 'test_operation',
          userId: 'test-user-456',
          projectId: 'test-project-123'
        }
      );
      console.log('✅ Error tracking test completed');
    } catch (error) {
      console.log('⚠️ Error tracking test failed (expected in mock mode)');
    }
    
    // Wait for flush
    console.log('\n⏳ Waiting for data flush...');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Cleanup
    await nlAgent.stop();
    
    console.log('\n✅ Agno monitoring integration test completed!');
    
  } catch (error) {
    console.error('❌ Agno monitoring test failed:', error);
    
    console.log('\n💡 To test with real Agno:');
    console.log('1. Sign up at https://agno.com');
    console.log('2. Create a project and get API key');
    console.log('3. Set environment variables:');
    console.log('   - AGNO_API_KEY');
    console.log('   - AGNO_PROJECT_ID');
    console.log('   - AGNO_ENDPOINT (optional)');
  }
}

if (require.main === module) {
  testAgnoMonitoring().catch(console.error);
}