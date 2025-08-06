#!/usr/bin/env node

const { MockServiceManager, mockConfig } = require('../backend/src/dev/mock-system.ts');
const axios = require('axios');

async function testMockSystem() {
  console.log('🧪 Testing Mock System...\n');

  // Set environment variables for testing
  process.env.USE_MOCKS = 'true';

  const mockManager = new MockServiceManager();

  try {
    // Start mock services
    console.log('1. Starting mock services...');
    await mockManager.startAll();
    
    // Wait for services to be ready
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Test Bedrock mock
    console.log('\n2. Testing Bedrock mock...');
    try {
      const bedrockResponse = await axios.post('http://localhost:4567/model/anthropic.claude-3-sonnet/invoke', {
        prompt: 'analyze this project'
      });
      console.log('✅ Bedrock mock response:', bedrockResponse.data.completion.substring(0, 100) + '...');
    } catch (error) {
      console.log('❌ Bedrock mock test failed:', error.message);
    }

    // Test NPM mock
    console.log('\n3. Testing NPM mock...');
    try {
      const npmResponse = await axios.get('http://localhost:4569/npm/express');
      console.log('✅ NPM mock response:', {
        name: npmResponse.data.name,
        version: npmResponse.data.version,
        downloads: npmResponse.data.downloads.weekly
      });
    } catch (error) {
      console.log('❌ NPM mock test failed:', error.message);
    }

    // Test GitHub mock
    console.log('\n4. Testing GitHub mock...');
    try {
      const githubResponse = await axios.get('http://localhost:4569/github/repos/facebook/react');
      console.log('✅ GitHub mock response:', {
        name: githubResponse.data.name,
        stars: githubResponse.data.stargazers_count,
        language: githubResponse.data.language
      });
    } catch (error) {
      console.log('❌ GitHub mock test failed:', error.message);
    }

    console.log('\n✅ Mock system test completed successfully!');

  } catch (error) {
    console.error('❌ Mock system test failed:', error);
  } finally {
    // Stop mock services
    console.log('\n5. Stopping mock services...');
    await mockManager.stopAll();
  }
}

if (require.main === module) {
  testMockSystem().catch(console.error);
}

module.exports = { testMockSystem };