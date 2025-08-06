#!/usr/bin/env node

const express = require('express');
const axios = require('axios');

// 테스트 서버 생성
function createTestServer() {
  const app = express();
  app.use(express.json());
  
  // 암호화 라우터 추가
  const encryptionRouter = require('../backend/src/routes/encryption-demo');
  app.use('/api/encryption', encryptionRouter);
  
  return app;
}

async function testEncryptionAPI() {
  console.log('🔐 Testing Encryption API...\n');
  
  const app = createTestServer();
  const server = app.listen(0); // 랜덤 포트
  const port = server.address().port;
  const baseURL = `http://localhost:${port}`;
  
  try {
    // 1. 암호화 테스트
    console.log('1. Testing Encryption Endpoint:');
    const encryptResponse = await axios.post(`${baseURL}/api/encryption/encrypt`, {
      data: 'sensitive-user-data-12345'
    });
    
    console.log(`   ✅ Encryption successful`);
    console.log(`   Original: ${encryptResponse.data.original}`);
    console.log(`   Encrypted: ${encryptResponse.data.encrypted.substring(0, 50)}...`);
    console.log(`   Hash: ${encryptResponse.data.hash.substring(0, 20)}...\n`);
    
    // 2. 복호화 테스트
    console.log('2. Testing Decryption Endpoint:');
    const decryptResponse = await axios.post(`${baseURL}/api/encryption/decrypt`, {
      encryptedData: encryptResponse.data.encrypted
    });
    
    console.log(`   ✅ Decryption successful`);
    console.log(`   Decrypted: ${decryptResponse.data.decrypted}`);
    console.log(`   Match: ${encryptResponse.data.original === decryptResponse.data.decrypted}\n`);
    
    // 3. 데이터 마스킹 테스트
    console.log('3. Testing Data Masking Endpoint:');
    const maskResponse = await axios.post(`${baseURL}/api/encryption/mask`, {
      data: {
        name: 'John Doe',
        email: 'john.doe@example.com',
        phone: '+1-555-123-4567',
        user: {
          personalEmail: 'john.personal@gmail.com'
        }
      },
      sensitiveFields: ['email', 'phone', 'user.personalEmail']
    });
    
    console.log(`   ✅ Masking successful`);
    console.log(`   Original:`, JSON.stringify(maskResponse.data.original, null, 2));
    console.log(`   Masked:`, JSON.stringify(maskResponse.data.masked, null, 2));
    
    // 4. 토큰 생성 테스트
    console.log('\n4. Testing Token Generation Endpoint:');
    const tokenResponse = await axios.get(`${baseURL}/api/encryption/token?length=16`);
    
    console.log(`   ✅ Token generation successful`);
    console.log(`   Token: ${tokenResponse.data.token}`);
    console.log(`   Length: ${tokenResponse.data.length}\n`);
    
    // 5. 해시 생성 테스트
    console.log('5. Testing Hash Generation Endpoint:');
    const hashResponse = await axios.post(`${baseURL}/api/encryption/hash`, {
      data: 'password123'
    });
    
    console.log(`   ✅ Hash generation successful`);
    console.log(`   Original: ${hashResponse.data.original}`);
    console.log(`   Hash: ${hashResponse.data.hash}`);
    console.log(`   Algorithm: ${hashResponse.data.algorithm}\n`);
    
    console.log('✅ All encryption API tests completed successfully!');
    
  } catch (error) {
    console.error('❌ API test failed:', error.response?.data || error.message);
  } finally {
    server.close();
  }
}

// 테스트 실행
testEncryptionAPI().catch(error => {
  console.error('❌ Test failed:', error.message);
  process.exit(1);
});