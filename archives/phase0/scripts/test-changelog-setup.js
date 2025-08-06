#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('📝 변경 로그 자동화 설정 검증 중...\n');

// 검증할 파일들
const expectedFiles = [
  '.commitlintrc.json',
  '.changelog.config.js',
  '.cliff.toml',
  '.github/workflows/changelog.yml'
];

let allPassed = true;

// 파일 존재 확인
console.log('1️⃣ 파일 존재 확인:');
expectedFiles.forEach(filePath => {
  const exists = fs.existsSync(filePath);
  console.log(`   ${exists ? '✅' : '❌'} ${filePath}`);
  if (!exists) allPassed = false;
});

// commitlint 설정 확인
console.log('\n2️⃣ Commitlint 설정 확인:');
try {
  const commitlintConfig = JSON.parse(fs.readFileSync('.commitlintrc.json', 'utf8'));
  
  const requiredRules = ['type-enum', 'subject-case', 'header-max-length'];
  requiredRules.forEach(rule => {
    const hasRule = commitlintConfig.rules && commitlintConfig.rules[rule];
    console.log(`   ${hasRule ? '✅' : '❌'} ${rule} 규칙`);
    if (!hasRule) allPassed = false;
  });
  
  const commitTypes = commitlintConfig.rules['type-enum'][2];
  const expectedTypes = ['feat', 'fix', 'docs', 'chore'];
  expectedTypes.forEach(type => {
    const hasType = commitTypes.includes(type);
    console.log(`   ${hasType ? '✅' : '❌'} ${type} 타입`);
    if (!hasType) allPassed = false;
  });
  
} catch (error) {
  console.log('   ❌ commitlint 설정 파일 읽기 실패');
  allPassed = false;
}

// changelog 설정 확인
console.log('\n3️⃣ Changelog 설정 확인:');
try {
  const changelogConfig = require(path.resolve('.changelog.config.js'));
  
  const requiredSections = ['✨ Features', '🐛 Bug Fixes', '📚 Documentation'];
  const configTypes = changelogConfig.types.map(t => t.section);
  
  requiredSections.forEach(section => {
    const hasSection = configTypes.includes(section);
    console.log(`   ${hasSection ? '✅' : '❌'} ${section} 섹션`);
    if (!hasSection) allPassed = false;
  });
  
} catch (error) {
  console.log('   ❌ changelog 설정 파일 읽기 실패');
  allPassed = false;
}

// GitHub Actions 워크플로우 확인
console.log('\n4️⃣ GitHub Actions 워크플로우 확인:');
try {
  const workflowContent = fs.readFileSync('.github/workflows/changelog.yml', 'utf8');
  
  const requiredElements = [
    'git-cliff-action',
    'CHANGELOG.md',
    'github-actions[bot]',
    'tags:'
  ];
  
  requiredElements.forEach(element => {
    const hasElement = workflowContent.includes(element);
    console.log(`   ${hasElement ? '✅' : '❌'} ${element} 포함`);
    if (!hasElement) allPassed = false;
  });
  
} catch (error) {
  console.log('   ❌ GitHub Actions 워크플로우 읽기 실패');
  allPassed = false;
}

// 최종 결과
console.log('\n' + '='.repeat(50));
if (allPassed) {
  console.log('✅ 모든 변경 로그 자동화 설정 검증 통과!');
  console.log('\n📝 다음 단계:');
  console.log('   1. commitlint 패키지 설치: npm install --save-dev @commitlint/cli @commitlint/config-conventional');
  console.log('   2. husky 설정으로 커밋 메시지 검증 활성화');
  console.log('   3. 첫 릴리스 태그 생성 시 CHANGELOG 자동 생성 확인');
  process.exit(0);
} else {
  console.log('❌ 일부 검증 실패. 위의 오류를 확인하세요.');
  process.exit(1);
}