const { AuthManager } = require('../backend/dist/utils/auth');

async function testAuth() {
  const authManager = new AuthManager();
  
  console.log('🔐 JWT 인증 시스템 테스트 시작...\n');
  
  try {
    // 1. 토큰 생성 테스트
    const payload = {
      userId: 'user123',
      email: 'test@example.com',
      role: 'user'
    };
    
    const tokens = await authManager.generateTokens(payload);
    console.log('✅ 토큰 생성 성공');
    console.log('Access Token:', tokens.accessToken.substring(0, 50) + '...');
    console.log('Refresh Token:', tokens.refreshToken.substring(0, 50) + '...\n');
    
    // 2. 토큰 검증 테스트
    const verifiedPayload = await authManager.verifyAccessToken(tokens.accessToken);
    console.log('✅ Access Token 검증 성공');
    console.log('Verified Payload:', verifiedPayload);
    
    const refreshPayload = await authManager.verifyRefreshToken(tokens.refreshToken);
    console.log('✅ Refresh Token 검증 성공');
    console.log('Refresh Payload:', refreshPayload);
    
    // 3. 비밀번호 해싱 테스트
    const password = 'testPassword123';
    const hashedPassword = await authManager.hashPassword(password);
    console.log('\n✅ 비밀번호 해싱 성공');
    console.log('Hashed Password:', hashedPassword.substring(0, 30) + '...');
    
    const isValid = await authManager.verifyPassword(password, hashedPassword);
    console.log('✅ 비밀번호 검증 성공:', isValid);
    
    console.log('\n🎉 모든 JWT 인증 테스트 통과!');
    
  } catch (error) {
    console.error('❌ 테스트 실패:', error);
  }
}

testAuth();