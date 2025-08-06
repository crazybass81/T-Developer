const express = require('../backend/node_modules/express');
const axios = require('../backend/node_modules/axios');
const { RateLimiter } = require('../backend/dist/middleware/rate-limiter');

async function testRateLimiter() {
  console.log('🚦 Rate Limiter 테스트 시작...\n');
  
  const app = express();
  const rateLimiter = new RateLimiter();
  
  // 테스트용 엄격한 제한 설정 (10초에 3회)
  const testLimiter = rateLimiter.middleware({
    windowMs: 10000,
    max: 3,
    message: 'Rate limit exceeded'
  });
  
  app.use(testLimiter);
  
  app.get('/test', (req, res) => {
    res.json({ message: 'Request successful', timestamp: new Date() });
  });
  
  const server = app.listen(3003, () => {
    console.log('✅ 테스트 서버 시작: http://localhost:3003');
    runTests();
  });
  
  async function runTests() {
    // axios already imported above
    
    try {
      console.log('\n📊 Rate Limit 테스트 (10초에 3회 제한):\n');
      
      // 3번의 성공적인 요청
      for (let i = 1; i <= 3; i++) {
        const response = await axios.get('http://localhost:3003/test');
        console.log(`${i}. ✅ 요청 성공 - Remaining: ${response.headers['x-ratelimit-remaining']}`);
      }
      
      // 4번째 요청은 차단되어야 함
      try {
        await axios.get('http://localhost:3003/test');
        console.log('4. ❌ 예상과 다름 - 요청이 통과됨');
      } catch (error) {
        if (error.response?.status === 429) {
          console.log('4. ✅ Rate limit 차단 성공 - 429 응답');
          console.log(`   Retry-After: ${error.response.data.retryAfter}초`);
        }
      }
      
      console.log('\n🎉 Rate Limiter 테스트 완료!');
      
    } catch (error) {
      console.error('❌ 테스트 실패:', error.message);
    } finally {
      server.close();
      process.exit(0);
    }
  }
}

testRateLimiter();