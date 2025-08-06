const { execSync } = require('child_process');
const fs = require('fs');

console.log('🐳 Docker Compose 설정 검증 시작...\n');

try {
  // docker-compose.yml 파일 확인
  console.log('📁 설정 파일 확인:');
  if (fs.existsSync('./docker-compose.yml')) {
    console.log('✅ docker-compose.yml 존재');
  } else {
    console.log('❌ docker-compose.yml 없음');
    process.exit(1);
  }

  // Docker 실행 확인
  console.log('\n🐳 Docker 상태 확인:');
  try {
    execSync('docker --version', { stdio: 'pipe' });
    console.log('✅ Docker 설치됨');
  } catch (error) {
    console.log('❌ Docker 설치되지 않음');
    process.exit(1);
  }

  try {
    execSync('docker-compose --version', { stdio: 'pipe' });
    console.log('✅ Docker Compose 설치됨');
  } catch (error) {
    console.log('❌ Docker Compose 설치되지 않음');
  }

  // 설정 파일 구문 검사
  console.log('\n🔧 Docker Compose 설정 검증:');
  try {
    execSync('docker-compose config', { stdio: 'pipe' });
    console.log('✅ docker-compose.yml 구문 정상');
  } catch (error) {
    console.log('❌ docker-compose.yml 구문 오류');
    console.log(error.message);
  }

  // 스크립트 파일 확인
  console.log('\n📋 스크립트 파일 확인:');
  const scripts = [
    './scripts/setup-localstack.py',
    './scripts/docker-health-check.sh'
  ];
  
  scripts.forEach(script => {
    if (fs.existsSync(script)) {
      console.log(`✅ ${script} 존재`);
    } else {
      console.log(`❌ ${script} 없음`);
    }
  });

  console.log('\n🎉 Docker Compose 설정 검증 완료!');
  console.log('\n💡 사용 가능한 명령:');
  console.log('   - docker-compose up -d        # 서비스 시작');
  console.log('   - docker-compose down         # 서비스 중지');
  console.log('   - ./scripts/docker-health-check.sh  # 헬스 체크');
  console.log('   - python scripts/setup-localstack.py # LocalStack 초기화');
  
} catch (error) {
  console.error('❌ Docker 설정 검증 실패:', error.message);
  process.exit(1);
}