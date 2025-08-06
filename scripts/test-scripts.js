const { execSync } = require('child_process');
const fs = require('fs');

console.log('🧪 테스트 실행 스크립트 검증 시작...\n');

try {
  // package.json 스크립트 확인
  console.log('📦 package.json 스크립트 확인:');
  const packageJson = require('../backend/package.json');
  
  const expectedScripts = [
    'test:unit',
    'test:integration', 
    'test:e2e',
    'test:seed',
    'test:all'
  ];
  
  expectedScripts.forEach(script => {
    if (packageJson.scripts[script]) {
      console.log(`✅ ${script} 스크립트 존재`);
    } else {
      console.log(`❌ ${script} 스크립트 없음`);
    }
  });

  // 실행 스크립트 파일 확인
  console.log('\n📋 실행 스크립트 파일 확인:');
  if (fs.existsSync('./scripts/run-tests.sh')) {
    console.log('✅ run-tests.sh 존재');
    
    // 실행 권한 확인
    const stats = fs.statSync('./scripts/run-tests.sh');
    const isExecutable = !!(stats.mode & parseInt('111', 8));
    if (isExecutable) {
      console.log('✅ 실행 권한 설정됨');
    } else {
      console.log('⚠️  실행 권한 필요: chmod +x scripts/run-tests.sh');
    }
  } else {
    console.log('❌ run-tests.sh 없음');
  }

  // 테스트 실행 (간단한 구문 검사)
  console.log('\n🔧 스크립트 구문 검사:');
  try {
    execSync('bash -n scripts/run-tests.sh', { stdio: 'pipe' });
    console.log('✅ Bash 스크립트 구문 정상');
  } catch (error) {
    console.log('❌ Bash 스크립트 구문 오류');
  }

  console.log('\n🎉 테스트 실행 스크립트 검증 완료!');
  console.log('\n💡 사용 가능한 테스트 명령:');
  console.log('   - ./scripts/run-tests.sh unit      # 단위 테스트');
  console.log('   - ./scripts/run-tests.sh integration # 통합 테스트');
  console.log('   - ./scripts/run-tests.sh e2e       # E2E 테스트');
  console.log('   - ./scripts/run-tests.sh seed      # 데이터 시딩');
  console.log('   - ./scripts/run-tests.sh all       # 전체 테스트');
  
} catch (error) {
  console.error('❌ 스크립트 검증 실패:', error.message);
  process.exit(1);
}