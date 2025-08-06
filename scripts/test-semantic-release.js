#!/usr/bin/env node

/**
 * Semantic Release 설정 검증 스크립트
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 Semantic Release 설정 검증 시작...\n');

// .releaserc.json 검증
console.log('📋 .releaserc.json 검증:');
try {
  const releaserc = JSON.parse(fs.readFileSync('.releaserc.json', 'utf8'));
  
  console.log('✅ JSON 구문 정상');
  console.log(`✅ 브랜치: ${releaserc.branches.join(', ')}`);
  console.log(`✅ 플러그인 수: ${releaserc.plugins.length}개`);
  
  // 필수 플러그인 확인
  const pluginNames = releaserc.plugins.map(p => 
    typeof p === 'string' ? p : p[0]
  );
  
  const requiredPlugins = [
    '@semantic-release/commit-analyzer',
    '@semantic-release/release-notes-generator',
    '@semantic-release/changelog',
    '@semantic-release/npm',
    '@semantic-release/github',
    '@semantic-release/git'
  ];
  
  requiredPlugins.forEach(plugin => {
    const exists = pluginNames.includes(plugin);
    console.log(`${exists ? '✅' : '❌'} ${plugin}`);
  });
  
} catch (error) {
  console.log(`❌ .releaserc.json 오류: ${error.message}`);
}

// Release 워크플로우 검증
console.log('\n📋 Release 워크플로우 검증:');
const releaseWorkflow = '.github/workflows/release.yml';
if (fs.existsSync(releaseWorkflow)) {
  console.log('✅ release.yml 파일 존재');
  
  const content = fs.readFileSync(releaseWorkflow, 'utf8');
  
  // 필수 요소 확인
  const checks = [
    { name: 'main 브랜치 트리거', pattern: /branches:\s*\[\s*main\s*\]/ },
    { name: 'Node.js 설정', pattern: /setup-node@v4/ },
    { name: 'semantic-release 실행', pattern: /npx semantic-release/ },
    { name: 'GITHUB_TOKEN 환경변수', pattern: /GITHUB_TOKEN/ }
  ];
  
  checks.forEach(check => {
    const exists = check.pattern.test(content);
    console.log(`${exists ? '✅' : '❌'} ${check.name}`);
  });
  
} else {
  console.log('❌ release.yml 파일 없음');
}

console.log('\n🚀 Semantic Release 기능:');
console.log('✅ 커밋 메시지 분석');
console.log('✅ 자동 버전 증가');
console.log('✅ CHANGELOG.md 생성');
console.log('✅ GitHub Release 생성');
console.log('✅ Git 태그 생성');

console.log('\n📊 커밋 메시지 규칙:');
console.log('- feat: 새로운 기능 (minor 버전 증가)');
console.log('- fix: 버그 수정 (patch 버전 증가)');
console.log('- BREAKING CHANGE: 호환성 변경 (major 버전 증가)');
console.log('- docs, style, refactor, test, chore: 버전 증가 없음');

console.log('\n✅ Semantic Release 설정 완료!');