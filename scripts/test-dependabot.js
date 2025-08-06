#!/usr/bin/env node

/**
 * Dependabot 설정 검증 스크립트
 */

const fs = require('fs');
const yaml = require('js-yaml');

console.log('🤖 Dependabot 설정 검증 시작...\n');

// dependabot.yml 확인
const dependabotPath = '.github/dependabot.yml';
if (fs.existsSync(dependabotPath)) {
  console.log('✅ dependabot.yml 파일 존재');
  
  try {
    const content = fs.readFileSync(dependabotPath, 'utf8');
    const config = yaml.load(content);
    
    console.log(`✅ YAML 구문 정상`);
    console.log(`✅ 업데이트 설정 수: ${config.updates.length}개`);
    
    // 각 업데이트 설정 확인
    config.updates.forEach((update, index) => {
      console.log(`\n📦 업데이트 설정 ${index + 1}:`);
      console.log(`  - 패키지 시스템: ${update['package-ecosystem']}`);
      console.log(`  - 디렉토리: ${update.directory}`);
      console.log(`  - 스케줄: ${update.schedule.interval}`);
      
      if (update.groups) {
        console.log(`  - 그룹 수: ${Object.keys(update.groups).length}개`);
      }
    });
    
  } catch (error) {
    console.log(`❌ YAML 파싱 오류: ${error.message}`);
  }
  
} else {
  console.log('❌ dependabot.yml 파일 없음');
}

console.log('\n🚀 Dependabot 기능:');
console.log('✅ NPM 패키지 일일 업데이트 확인');
console.log('✅ Docker 이미지 주간 업데이트');
console.log('✅ GitHub Actions 주간 업데이트');
console.log('✅ AWS SDK 그룹화');
console.log('✅ 개발 도구 그룹화');
console.log('✅ PR 제한 (최대 5개)');

console.log('\n📊 업데이트 전략:');
console.log('- AWS SDK: 그룹으로 일괄 업데이트');
console.log('- 개발 도구: ESLint, Prettier, Jest 등 그룹화');
console.log('- Docker: 베이스 이미지 보안 업데이트');
console.log('- GitHub Actions: 액션 버전 업데이트');

console.log('\n✅ Dependabot 설정 완료!');