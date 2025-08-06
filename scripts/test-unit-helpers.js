const { execSync } = require('child_process');

console.log('🧪 단위 테스트 헬퍼 검증 시작...\n');

try {
  // Jest 테스트 실행
  console.log('📋 Jest 테스트 실행:');
  const output = execSync('npm test', { 
    cwd: './backend',
    encoding: 'utf8',
    stdio: 'pipe'
  });
  
  console.log('✅ 모든 테스트 통과!');
  
  // 테스트 커버리지 실행
  console.log('\n📊 테스트 커버리지 확인:');
  const coverageOutput = execSync('npm run test:coverage', { 
    cwd: './backend',
    encoding: 'utf8',
    stdio: 'pipe'
  });
  
  console.log('✅ 커버리지 리포트 생성 완료!');
  console.log('📁 커버리지 리포트: backend/coverage/lcov-report/index.html');
  
  console.log('\n🎉 단위 테스트 헬퍼 검증 완료!');
  console.log('\n💡 사용 가능한 테스트 유틸리티:');
  console.log('   - TestDataGenerator: 테스트 데이터 생성');
  console.log('   - waitFor: 비동기 조건 대기');
  console.log('   - MockTimer: 타이머 모킹');
  console.log('   - mockEnvironment: 환경 변수 모킹');
  console.log('   - dynamoDBMock: DynamoDB 클라이언트 모킹');
  
} catch (error) {
  console.error('❌ 테스트 실패:', error.message);
  process.exit(1);
}