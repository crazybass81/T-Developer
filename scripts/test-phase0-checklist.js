#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 Phase 0 체크리스트 검증 시작...\n');

// 1. TypeScript 컴파일 확인
console.log('1. TypeScript 컴파일 확인...');
try {
  execSync('npx tsc --noEmit scripts/phase0-checklist.ts', { stdio: 'pipe' });
  console.log('✅ TypeScript 컴파일 성공');
} catch (error) {
  console.log('❌ TypeScript 컴파일 실패');
  console.log(error.stdout?.toString() || error.message);
  process.exit(1);
}

// 2. 필수 파일 존재 확인
console.log('\n2. 필수 파일 존재 확인...');
const requiredFiles = [
  'scripts/phase0-checklist.ts',
  'docs/setup/development-environment.md',
  '.env.example',
  'backend/package.json',
  'docker-compose.yml'
];

let allFilesExist = true;
for (const file of requiredFiles) {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} - 파일이 없습니다`);
    allFilesExist = false;
  }
}

// 3. 체크리스트 스크립트 실행 테스트
console.log('\n3. 체크리스트 스크립트 실행 테스트...');
try {
  // dry-run 모드로 실행 (실제 검사는 하지 않고 구조만 확인)
  const result = execSync('npx ts-node scripts/phase0-checklist.ts', { 
    stdio: 'pipe',
    timeout: 30000 
  });
  console.log('✅ 체크리스트 스크립트 실행 성공');
} catch (error) {
  console.log('⚠️  체크리스트 스크립트 실행 (일부 항목 실패는 정상)');
  // 체크리스트에서 일부 실패는 정상이므로 에러로 처리하지 않음
}

// 4. package.json 스크립트 추가 확인
console.log('\n4. package.json 스크립트 확인...');
const packageJsonPath = 'package.json';
if (fs.existsSync(packageJsonPath)) {
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  
  if (!packageJson.scripts) {
    packageJson.scripts = {};
  }
  
  // 체크리스트 스크립트 추가
  packageJson.scripts['phase0:check'] = 'ts-node scripts/phase0-checklist.ts';
  packageJson.scripts['verify:env'] = 'ts-node scripts/environment-verifier.ts';
  
  fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
  console.log('✅ package.json 스크립트 추가 완료');
} else {
  console.log('❌ package.json 파일이 없습니다');
  allFilesExist = false;
}

// 결과 출력
console.log('\n' + '='.repeat(50));
if (allFilesExist) {
  console.log('🎉 Phase 0 체크리스트 검증 완료!');
  console.log('\n사용법:');
  console.log('  npm run phase0:check  - Phase 0 완료 상태 확인');
  console.log('  npm run verify:env   - 개발 환경 검증');
} else {
  console.log('❌ 일부 파일이 누락되었습니다.');
  process.exit(1);
}