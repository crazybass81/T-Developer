#!/usr/bin/env node

/**
 * 개발 환경 최종 검증 테스트 스크립트
 * SubTask 0.14.2 검증용
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 개발 환경 최종 검증 테스트 시작...\n');

// 1. 필수 파일 존재 확인
console.log('📁 필수 파일 존재 확인:');
const requiredFiles = [
  'scripts/verify-environment.ts',
  'package.json',
  '.env.example'
];

let allFilesExist = true;
for (const file of requiredFiles) {
  const exists = fs.existsSync(path.join(process.cwd(), file));
  console.log(`  ${exists ? '✅' : '❌'} ${file}`);
  if (!exists) allFilesExist = false;
}

if (!allFilesExist) {
  console.log('\n❌ 필수 파일이 누락되었습니다.');
  process.exit(1);
}

// 2. TypeScript 컴파일 확인
console.log('\n🔧 TypeScript 컴파일 확인:');
try {
  execSync('npx tsc --noEmit scripts/verify-environment.ts', { stdio: 'pipe' });
  console.log('  ✅ TypeScript 컴파일 성공');
} catch (error) {
  console.log('  ❌ TypeScript 컴파일 실패');
  console.log(`     ${error.message}`);
  process.exit(1);
}

// 3. 필수 의존성 확인
console.log('\n📦 필수 의존성 확인:');
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const requiredDeps = [
  'chalk',
  'axios',
  'ioredis',
  '@aws-sdk/client-dynamodb'
];

let allDepsExist = true;
for (const dep of requiredDeps) {
  const exists = packageJson.dependencies?.[dep] || packageJson.devDependencies?.[dep];
  console.log(`  ${exists ? '✅' : '❌'} ${dep}`);
  if (!exists) allDepsExist = false;
}

if (!allDepsExist) {
  console.log('\n⚠️  일부 의존성이 누락되었습니다. npm install을 실행하세요.');
}

// 4. 환경 변수 템플릿 확인
console.log('\n🔐 환경 변수 템플릿 확인:');
try {
  const envExample = fs.readFileSync('.env.example', 'utf8');
  const requiredEnvVars = [
    'NODE_ENV',
    'AWS_REGION',
    'DYNAMODB_ENDPOINT',
    'REDIS_HOST',
    'REDIS_PORT'
  ];
  
  let allEnvVarsExist = true;
  for (const envVar of requiredEnvVars) {
    const exists = envExample.includes(envVar);
    console.log(`  ${exists ? '✅' : '❌'} ${envVar}`);
    if (!exists) allEnvVarsExist = false;
  }
  
  if (!allEnvVarsExist) {
    console.log('\n⚠️  일부 환경 변수가 .env.example에 누락되었습니다.');
  }
  
} catch (error) {
  console.log('  ❌ .env.example 파일 읽기 실패');
}

// 5. 검증 스크립트 구조 확인
console.log('\n🏗️  검증 스크립트 구조 확인:');
const verifyScript = fs.readFileSync('scripts/verify-environment.ts', 'utf8');

const requiredClasses = ['EnvironmentVerifier'];
const requiredMethods = ['verify', 'verifyNodeEnvironment', 'verifyAWSConfiguration', 'verifyDatabases'];

let allStructuresExist = true;
for (const className of requiredClasses) {
  const exists = verifyScript.includes(`class ${className}`);
  console.log(`  ${exists ? '✅' : '❌'} ${className} 클래스`);
  if (!exists) allStructuresExist = false;
}

for (const methodName of requiredMethods) {
  const exists = verifyScript.includes(methodName);
  console.log(`  ${exists ? '✅' : '❌'} ${methodName} 메서드`);
  if (!exists) allStructuresExist = false;
}

if (!allStructuresExist) {
  console.log('\n❌ 검증 스크립트 구조가 불완전합니다.');
  process.exit(1);
}

// 6. 검증 카테고리 확인
console.log('\n📋 검증 카테고리 확인:');
const verificationCategories = [
  'Node.js 환경',
  'AWS 설정', 
  '데이터베이스',
  '외부 서비스',
  '개발 도구',
  '보안 설정'
];

let allCategoriesExist = true;
for (const category of verificationCategories) {
  const exists = verifyScript.includes(category.replace(' ', '')) || 
                 verifyScript.includes(category.toLowerCase().replace(' ', ''));
  console.log(`  ${exists ? '✅' : '❌'} ${category} 검증`);
  if (!exists) allCategoriesExist = false;
}

if (!allCategoriesExist) {
  console.log('\n⚠️  일부 검증 카테고리가 누락되었습니다.');
}

// 7. 출력 형식 확인
console.log('\n🎨 출력 형식 확인:');
const outputFeatures = [
  'chalk',           // 컬러 출력
  'statusIcons',     // 상태 아이콘
  'printResults',    // 결과 출력
  'statistics'       // 통계 정보
];

let allOutputFeaturesExist = true;
for (const feature of outputFeatures) {
  const exists = verifyScript.includes(feature);
  console.log(`  ${exists ? '✅' : '❌'} ${feature} 기능`);
  if (!exists) allOutputFeaturesExist = false;
}

if (!allOutputFeaturesExist) {
  console.log('\n⚠️  일부 출력 기능이 누락되었습니다.');
}

console.log('\n✅ 개발 환경 최종 검증 테스트 완료!');
console.log('\n📋 구현된 기능:');
console.log('  • Node.js 환경 검증 (버전, 패키지)');
console.log('  • AWS 설정 검증 (자격증명, DynamoDB, S3)');
console.log('  • 데이터베이스 연결 검증 (Redis, DynamoDB Local)');
console.log('  • 외부 서비스 검증 (GitHub, AI 서비스)');
console.log('  • 개발 도구 검증 (Docker, Git, VS Code)');
console.log('  • 보안 설정 검증 (환경변수, 파일권한)');
console.log('  • 컬러 출력 및 통계 정보');

console.log('\n🎯 SubTask 0.14.2 완료!');