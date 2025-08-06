const { execSync } = require('child_process');

console.log('🔄 E2E 테스트 환경 검증 시작...\n');

try {
  // E2E 테스트 환경 확인
  console.log('📋 E2E 테스트 환경 확인:');
  
  // Docker 확인
  try {
    execSync('docker --version', { stdio: 'pipe' });
    console.log('✅ Docker 사용 가능');
  } catch (error) {
    console.log('⚠️  Docker 없음 - E2E 테스트 스킵');
    process.exit(0);
  }
  
  // 테스트 파일 존재 확인
  const fs = require('fs');
  const testFiles = [
    './backend/tests/e2e/setup.ts',
    './backend/tests/e2e/workflow.test.ts',
    './backend/tests/fixtures/seed-data.ts'
  ];
  
  testFiles.forEach(file => {
    if (fs.existsSync(file)) {
      console.log(`✅ ${file} 존재`);
    } else {
      console.log(`❌ ${file} 없음`);
    }
  });
  
  console.log('\n🎉 E2E 테스트 환경 검증 완료!');
  console.log('\n💡 사용 가능한 E2E 테스트 도구:');
  console.log('   - E2ETestEnvironment: Docker 기반 환경 설정');
  console.log('   - TestDataSeeder: 테스트 데이터 생성');
  console.log('   - 워크플로우 테스트: 전체 프로세스 검증');
  console.log('   - DynamoDB Local + Redis 통합');
  
} catch (error) {
  console.error('❌ E2E 환경 검증 실패:', error.message);
  process.exit(1);
}