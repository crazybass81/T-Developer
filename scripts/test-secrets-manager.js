const { SecretsManager } = require('../backend/dist/config/secrets-manager');

async function testSecretsManager() {
  console.log('🔐 Secrets Manager 테스트 시작...\n');
  
  const manager = new SecretsManager();
  
  try {
    // 1. 개발 환경 시크릿 테스트
    console.log('📋 개발 환경 시크릿 로드 테스트:');
    
    // 환경 변수 설정
    process.env.NODE_ENV = 'development';
    
    // 시크릿 로드 시도
    await manager.loadEnvironmentSecrets();
    
    // 2. 캐시 테스트
    console.log('\n🗄️ 캐시 테스트:');
    const start1 = Date.now();
    await manager.getSecret('t-developer/development/config');
    const time1 = Date.now() - start1;
    console.log(`✅ 첫 번째 호출: ${time1}ms`);
    
    const start2 = Date.now();
    await manager.getSecret('t-developer/development/config');
    const time2 = Date.now() - start2;
    console.log(`✅ 두 번째 호출 (캐시): ${time2}ms`);
    
    console.log(`📊 캐시 성능 향상: ${Math.round((time1 - time2) / time1 * 100)}%`);
    
    console.log('\n🎉 Secrets Manager 테스트 완료!');
    
  } catch (error) {
    if (error.name === 'ResourceNotFoundException') {
      console.log('⚠️  시크릿이 존재하지 않음 - 로컬 .env 사용');
      console.log('💡 시크릿 생성: node scripts/create-secrets.js');
    } else {
      console.error('❌ 테스트 실패:', error.message);
    }
  }
}

testSecretsManager();