#!/usr/bin/env node

const Redis = require('ioredis');

// 에이전트 통신 프로토콜 테스트
async function testAgentCommunication() {
  console.log('🔄 Testing Agent Communication Protocol...\n');
  
  try {
    // Redis 연결 테스트
    const redis = new Redis({
      host: 'localhost',
      port: 6379,
      retryDelayOnFailover: 100,
      maxRetriesPerRequest: 3
    });
    
    await redis.ping();
    console.log('✅ Redis connection successful');
    
    // 메시지 발행/구독 테스트
    const publisher = new Redis({ host: 'localhost', port: 6379 });
    const subscriber = new Redis({ host: 'localhost', port: 6379 });
    
    let messageReceived = false;
    
    subscriber.on('message', (channel, message) => {
      console.log(`📨 Message received on ${channel}:`, JSON.parse(message));
      messageReceived = true;
    });
    
    await subscriber.subscribe('agent:test');
    
    const testMessage = {
      id: 'test-msg-001',
      type: 'request',
      source: 'test-agent-1',
      target: 'test-agent-2',
      payload: { action: 'ping' },
      timestamp: new Date()
    };
    
    await publisher.publish('agent:test', JSON.stringify(testMessage));
    
    // 메시지 수신 대기
    await new Promise(resolve => setTimeout(resolve, 100));
    
    if (messageReceived) {
      console.log('✅ Message pub/sub working');
    } else {
      console.log('❌ Message not received');
    }
    
    // 정리
    await subscriber.unsubscribe('agent:test');
    await publisher.quit();
    await subscriber.quit();
    await redis.quit();
    
    console.log('\n✅ Agent Communication Protocol test completed!');
    
  } catch (error) {
    console.error('❌ Agent Communication test failed:', error.message);
    process.exit(1);
  }
}

// Bedrock AgentCore 설정 테스트
async function testBedrockConfig() {
  console.log('\n🔄 Testing Bedrock AgentCore Configuration...\n');
  
  try {
    // AWS SDK 설치 확인
    const { BedrockAgentRuntimeClient } = require('@aws-sdk/client-bedrock-agent-runtime');
    console.log('✅ AWS Bedrock SDK available');
    
    // 설정 검증
    const config = {
      agentId: 'test-agent-id',
      agentAliasId: 'test-alias-id',
      region: 'us-east-1'
    };
    
    // 클라이언트 생성 테스트 (실제 호출 없이)
    const client = new BedrockAgentRuntimeClient({
      region: config.region
    });
    
    console.log('✅ Bedrock client created successfully');
    console.log('📋 Configuration:', config);
    
    console.log('\n✅ Bedrock AgentCore configuration test completed!');
    
  } catch (error) {
    console.error('❌ Bedrock configuration test failed:', error.message);
    
    if (error.code === 'MODULE_NOT_FOUND') {
      console.log('💡 Install AWS SDK: npm install @aws-sdk/client-bedrock-agent-runtime');
    }
  }
}

// 메인 실행
async function main() {
  console.log('🧪 SubTask 0.13.2: Agent Communication Protocol Test\n');
  
  await testAgentCommunication();
  await testBedrockConfig();
  
  console.log('\n🎉 All tests completed!');
}

if (require.main === module) {
  main().catch(console.error);
}