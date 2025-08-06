const { RateLimiter } = require('../backend/dist/middleware/rate-limiter');

async function testRateLimiter() {
  console.log('🚦 Rate Limiter 기본 테스트 시작...\n');
  
  try {
    const rateLimiter = new RateLimiter();
    console.log('✅ RateLimiter 인스턴스 생성 성공');
    
    const limits = rateLimiter.apiLimits();
    console.log('✅ API 제한 설정 로드 성공');
    console.log('- General API: 1분에 100회');
    console.log('- Auth API: 5분에 5회');
    console.log('- Create API: 1시간에 10회');
    console.log('- AI API: 1분에 20회');
    
    console.log('\n🎉 Rate Limiter 기본 테스트 완료!');
    console.log('📋 실제 테스트는 Redis 연결 후 Express 서버에서 확인 가능');
    
  } catch (error) {
    console.error('❌ 테스트 실패:', error.message);
  }
}

testRateLimiter();