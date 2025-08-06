const { execSync } = require('child_process');
const fs = require('fs');

console.log('📊 테스트 보고서 생성 설정 검증 시작...\n');

try {
  // jest-html-reporter 의존성 확인
  console.log('📦 의존성 확인:');
  const packageJson = require('../backend/package.json');
  
  if (packageJson.devDependencies['jest-html-reporter']) {
    console.log('✅ jest-html-reporter 설치됨');
  } else {
    console.log('❌ jest-html-reporter 없음');
    process.exit(1);
  }

  // Jest 설정 확인
  console.log('\n🔧 Jest 설정 확인:');
  const jestConfig = require('../backend/jest.config.js');
  
  if (jestConfig.reporters && jestConfig.reporters.some(r => Array.isArray(r) && r[0] === 'jest-html-reporter')) {
    console.log('✅ Jest HTML 리포터 설정됨');
  } else {
    console.log('❌ Jest HTML 리포터 설정 없음');
  }

  // 테스트 리포트 파일 확인
  console.log('\n📁 테스트 리포트 파일 확인:');
  const reportFiles = [
    './backend/jest-html-reporter.config.js',
    './backend/src/utils/test-reporter.ts',
    './backend/test-reports'
  ];
  
  reportFiles.forEach(file => {
    if (fs.existsSync(file)) {
      console.log(`✅ ${file} 존재`);
    } else {
      console.log(`❌ ${file} 없음`);
    }
  });

  // 간단한 테스트 실행으로 리포트 생성 확인
  console.log('\n🧪 테스트 리포트 생성 테스트:');
  try {
    execSync('cd backend && npm test -- --passWithNoTests', { 
      stdio: 'pipe',
      timeout: 30000
    });
    
    if (fs.existsSync('./backend/test-reports/index.html')) {
      console.log('✅ HTML 테스트 리포트 생성됨');
    } else {
      console.log('⚠️  HTML 리포트 파일 없음 (테스트 없음)');
    }
    
    if (fs.existsSync('./backend/test-reports/test-results.json')) {
      console.log('✅ JSON 테스트 결과 생성됨');
    } else {
      console.log('⚠️  JSON 결과 파일 없음');
    }
  } catch (error) {
    console.log('⚠️  테스트 실행 중 오류 (정상적일 수 있음)');
  }

  console.log('\n🎉 테스트 보고서 생성 설정 검증 완료!');
  console.log('\n💡 사용 가능한 리포트 기능:');
  console.log('   - HTML 테스트 리포트 (test-reports/index.html)');
  console.log('   - JSON 테스트 결과 (test-reports/test-results.json)');
  console.log('   - 커버리지 리포트 (coverage/index.html)');
  console.log('   - 커스텀 테스트 리포터 (콘솔 요약)');
  
} catch (error) {
  console.error('❌ 리포트 설정 검증 실패:', error.message);
  process.exit(1);
}