// Demo script showing Secrets Manager functionality without AWS dependency
const { SecretsManager } = require('../backend/dist/config/secrets-manager');

// Mock Secrets Manager for demo
class MockSecretsManager extends SecretsManager {
  constructor() {
    super();
    // Mock secrets data
    this.mockSecrets = {
      't-developer/development/config': {
        JWT_ACCESS_SECRET: 'dev-jwt-access-secret-key',
        JWT_REFRESH_SECRET: 'dev-jwt-refresh-secret-key',
        ENCRYPTION_KEY: 'dev-encryption-key-32-characters',
        OPENAI_API_KEY: 'sk-dev-openai-key',
        ANTHROPIC_API_KEY: 'sk-ant-dev-anthropic-key'
      }
    };
  }
  
  async getSecret(secretName) {
    console.log(`📥 시크릿 요청: ${secretName}`);
    
    // 캐시 확인
    const cached = this.cache.get(secretName);
    if (cached && cached.expiry > Date.now()) {
      console.log('🗄️ 캐시에서 반환');
      return cached.value;
    }
    
    // Mock 데이터 반환
    if (this.mockSecrets[secretName]) {
      const value = this.mockSecrets[secretName];
      
      // 캐시에 저장
      this.cache.set(secretName, {
        value,
        expiry: Date.now() + this.cacheTTL
      });
      
      console.log('✅ 시크릿 로드 성공');
      return value;
    }
    
    throw new Error('ResourceNotFoundException');
  }
}

async function demoSecretsManager() {
  console.log('🔐 Secrets Manager 데모 시작...\n');
  
  const manager = new MockSecretsManager();
  
  try {
    // 1. 시크릿 로드 테스트
    console.log('📋 시크릿 로드 테스트:');
    const secrets = await manager.getSecret('t-developer/development/config');
    console.log('✅ 로드된 시크릿 키:', Object.keys(secrets));
    
    // 2. 캐시 성능 테스트
    console.log('\n🗄️ 캐시 성능 테스트:');
    const start1 = Date.now();
    await manager.getSecret('t-developer/development/config');
    const time1 = Date.now() - start1;
    console.log(`⏱️ 첫 번째 호출: ${time1}ms`);
    
    const start2 = Date.now();
    await manager.getSecret('t-developer/development/config');
    const time2 = Date.now() - start2;
    console.log(`⏱️ 두 번째 호출 (캐시): ${time2}ms`);
    
    // 3. 환경 변수 로드 시뮬레이션
    console.log('\n🌍 환경 변수 로드 시뮬레이션:');
    const originalEnv = { ...process.env };
    
    // 환경 변수 설정
    Object.entries(secrets).forEach(([key, value]) => {
      if (!process.env[key]) {
        process.env[key] = value;
        console.log(`✅ 환경 변수 설정: ${key}=***`);
      }
    });
    
    console.log('\n🎉 Secrets Manager 데모 완료!');
    console.log('\n💡 실제 사용 시:');
    console.log('   1. AWS Secrets Manager에서 시크릿 생성');
    console.log('   2. IAM 권한 설정 (secretsmanager:GetSecretValue)');
    console.log('   3. 프로덕션에서 자동 로드');
    
  } catch (error) {
    console.error('❌ 데모 실패:', error.message);
  }
}

demoSecretsManager();