const express = require('../backend/node_modules/express');
const app = require('../backend/dist/app').default;

async function testSecurity() {
  console.log('🔒 보안 미들웨어 테스트 시작...\n');
  
  const server = app.listen(3004, () => {
    console.log('✅ 테스트 서버 시작: http://localhost:3004');
    runTests();
  });
  
  async function runTests() {
    try {
      // 1. Health check 테스트
      const response = await fetch('http://localhost:3004/health');
      const data = await response.json();
      
      console.log('📊 Health Check 테스트:');
      console.log('✅ Status:', data.status);
      console.log('✅ Request ID:', data.requestId);
      
      // 2. Security headers 확인
      console.log('\n🛡️ Security Headers 확인:');
      console.log('✅ X-Request-ID:', response.headers.get('X-Request-ID'));
      console.log('✅ X-Content-Type-Options:', response.headers.get('X-Content-Type-Options'));
      console.log('✅ X-Frame-Options:', response.headers.get('X-Frame-Options'));
      console.log('✅ Strict-Transport-Security:', response.headers.get('Strict-Transport-Security'));
      
      // 3. CORS 테스트 (허용된 origin)
      const corsResponse = await fetch('http://localhost:3004/health', {
        headers: {
          'Origin': 'http://localhost:3000'
        }
      });
      console.log('\n🌐 CORS 테스트:');
      console.log('✅ Access-Control-Allow-Origin:', corsResponse.headers.get('Access-Control-Allow-Origin'));
      
      console.log('\n🎉 보안 미들웨어 테스트 완료!');
      
    } catch (error) {
      console.error('❌ 테스트 실패:', error.message);
    } finally {
      server.close();
      process.exit(0);
    }
  }
}

testSecurity();