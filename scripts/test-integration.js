const { execSync } = require('child_process');

console.log('🔗 통합 테스트 환경 검증 시작...\n');

try {
  // 통합 테스트 실행
  console.log('📋 통합 테스트 실행:');
  const output = execSync('npm test tests/integration', { 
    cwd: './backend',
    encoding: 'utf8',
    stdio: 'pipe'
  });
  
  console.log('✅ 모든 통합 테스트 통과!');
  
  // 전체 테스트 실행
  console.log('\n📊 전체 테스트 실행:');
  const allOutput = execSync('npm test', { 
    cwd: './backend',
    encoding: 'utf8',
    stdio: 'pipe'
  });
  
  console.log('✅ 전체 테스트 통과!');
  
  console.log('\n🎉 통합 테스트 환경 검증 완료!');
  console.log('\n💡 사용 가능한 통합 테스트 도구:');
  console.log('   - TestServer: Express 테스트 서버');
  console.log('   - TestClient: HTTP 클라이언트');
  console.log('   - 테스트 픽스처: 미리 정의된 테스트 데이터');
  console.log('   - API 엔드포인트 테스트');
  
} catch (error) {
  console.error('❌ 테스트 실패:', error.message);
  process.exit(1);
}