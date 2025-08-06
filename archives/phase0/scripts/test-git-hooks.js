#!/usr/bin/env node

/**
 * Git 훅 및 커밋 규칙 설정 검증 스크립트
 * SubTask 0.14.1 검증용
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 Git 훅 및 커밋 규칙 설정 검증 시작...\n');

// 1. 필수 파일 존재 확인
const requiredFiles = [
  'scripts/setup-git-hooks.sh',
  'commitlint.config.js',
  '.gitmessage'
];

console.log('📁 필수 파일 존재 확인:');
let allFilesExist = true;

for (const file of requiredFiles) {
  const filePath = path.join(process.cwd(), file);
  const exists = fs.existsSync(filePath);
  
  console.log(`  ${exists ? '✅' : '❌'} ${file}`);
  
  if (!exists) {
    allFilesExist = false;
  }
}

if (!allFilesExist) {
  console.log('\n❌ 일부 필수 파일이 누락되었습니다.');
  process.exit(1);
}

// 2. Git 저장소 확인
console.log('\n🔧 Git 저장소 확인:');
try {
  const gitStatus = execSync('git status --porcelain', { encoding: 'utf8' });
  console.log('  ✅ Git 저장소 확인됨');
} catch (error) {
  console.log('  ❌ Git 저장소가 아니거나 Git이 설치되지 않음');
  process.exit(1);
}

// 3. commitlint 설정 검증
console.log('\n📝 commitlint 설정 검증:');
try {
  const commitlintConfig = require(path.join(process.cwd(), 'commitlint.config.js'));
  
  const hasExtends = commitlintConfig.extends && commitlintConfig.extends.includes('@commitlint/config-conventional');
  const hasTypeEnum = commitlintConfig.rules && commitlintConfig.rules['type-enum'];
  const hasScopeEnum = commitlintConfig.rules && commitlintConfig.rules['scope-enum'];
  const hasAgentType = hasTypeEnum && commitlintConfig.rules['type-enum'][2].includes('agent');
  
  console.log(`  ${hasExtends ? '✅' : '❌'} Conventional Commits 확장`);
  console.log(`  ${hasTypeEnum ? '✅' : '❌'} 커밋 타입 규칙`);
  console.log(`  ${hasScopeEnum ? '✅' : '❌'} 스코프 규칙`);
  console.log(`  ${hasAgentType ? '✅' : '❌'} T-Developer 전용 'agent' 타입`);
  
  if (!hasExtends || !hasTypeEnum || !hasScopeEnum || !hasAgentType) {
    throw new Error('commitlint 설정이 불완전합니다.');
  }
  
} catch (error) {
  console.log(`  ❌ commitlint 설정 오류: ${error.message}`);
  process.exit(1);
}

// 4. Git 메시지 템플릿 검증
console.log('\n📋 Git 메시지 템플릿 검증:');
try {
  const gitmessagePath = path.join(process.cwd(), '.gitmessage');
  const gitmessageContent = fs.readFileSync(gitmessagePath, 'utf8');
  
  const hasTypeScope = gitmessageContent.includes('<type>(<scope>): <subject>');
  const hasExamples = gitmessageContent.includes('feat(agents):');
  const hasInstructions = gitmessageContent.includes('Type: feat, fix, docs');
  const hasAgentType = gitmessageContent.includes('agent');
  
  console.log(`  ${hasTypeScope ? '✅' : '❌'} 커밋 메시지 형식`);
  console.log(`  ${hasExamples ? '✅' : '❌'} 예시 포함`);
  console.log(`  ${hasInstructions ? '✅' : '❌'} 사용 지침`);
  console.log(`  ${hasAgentType ? '✅' : '❌'} agent 타입 포함`);
  
  if (!hasTypeScope || !hasExamples || !hasInstructions || !hasAgentType) {
    throw new Error('Git 메시지 템플릿이 불완전합니다.');
  }
  
} catch (error) {
  console.log(`  ❌ Git 메시지 템플릿 오류: ${error.message}`);
  process.exit(1);
}

// 5. 스크립트 실행 권한 확인
console.log('\n🔐 스크립트 실행 권한 확인:');
try {
  const setupScriptPath = path.join(process.cwd(), 'scripts/setup-git-hooks.sh');
  const stats = fs.statSync(setupScriptPath);
  const isExecutable = !!(stats.mode & parseInt('111', 8));
  
  if (!isExecutable) {
    console.log('  ⚠️  실행 권한 없음, 권한 부여 중...');
    execSync(`chmod +x ${setupScriptPath}`);
    console.log('  ✅ 실행 권한 부여 완료');
  } else {
    console.log('  ✅ 실행 권한 확인됨');
  }
  
} catch (error) {
  console.log(`  ❌ 실행 권한 확인 실패: ${error.message}`);
  process.exit(1);
}

// 6. Bash 구문 검사
console.log('\n🔧 Bash 스크립트 구문 검사:');
try {
  execSync('bash -n scripts/setup-git-hooks.sh', { stdio: 'pipe' });
  console.log('  ✅ Bash 구문 검사 통과');
} catch (error) {
  console.log('  ❌ Bash 구문 오류 발견');
  console.log(`     ${error.message}`);
  process.exit(1);
}

console.log('\n✅ Git 훅 및 커밋 규칙 설정 검증 완료!');
console.log('\n📋 구현된 기능:');
console.log('  • Husky Git 훅 설정 스크립트');
console.log('  • Conventional Commits 규칙');
console.log('  • T-Developer 전용 커밋 타입 (agent)');
console.log('  • 스코프 기반 커밋 분류');
console.log('  • Git 메시지 템플릿');
console.log('  • pre-commit/pre-push 훅');

console.log('\n🎯 SubTask 0.14.1 완료!');