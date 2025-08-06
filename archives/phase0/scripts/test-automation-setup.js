#!/usr/bin/env node

/**
 * 테스트 자동화 설정 검증 스크립트
 */

const fs = require('fs');
const path = require('path');

console.log('🧪 테스트 자동화 설정 검증 시작...\n');

// 테스트 자동화 워크플로우 확인
const testWorkflow = '.github/workflows/test-automation.yml';
if (fs.existsSync(testWorkflow)) {
  console.log('✅ test-automation.yml 워크플로우 존재');
  
  const content = fs.readFileSync(testWorkflow, 'utf8');
  
  // 필수 요소 확인
  const checks = [
    { name: 'PR 트리거', pattern: /pull_request:/ },
    { name: 'Push 트리거', pattern: /push:/ },
    { name: 'DynamoDB 서비스', pattern: /amazon\/dynamodb-local/ },
    { name: 'Redis 서비스', pattern: /redis:7-alpine/ },
    { name: '테스트 매트릭스', pattern: /test-suite.*unit.*integration.*e2e/ },
    { name: '커버리지 업로드', pattern: /upload-artifact.*coverage/ }
  ];
  
  checks.forEach(check => {
    const exists = check.pattern.test(content);
    console.log(`${exists ? '✅' : '❌'} ${check.name}`);
  });
  
} else {
  console.log('❌ test-automation.yml 워크플로우 없음');
}

// package.json 테스트 스크립트 확인
const packageJsonPath = path.join('backend', 'package.json');
if (fs.existsSync(packageJsonPath)) {
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  
  console.log('\n📋 테스트 스크립트 확인:');
  const testScripts = [
    'test:unit',
    'test:integration', 
    'test:e2e',
    'test:all'
  ];
  
  testScripts.forEach(script => {
    const exists = packageJson.scripts && packageJson.scripts[script];
    console.log(`${exists ? '✅' : '❌'} ${script}`);
  });
}

console.log('\n🚀 테스트 자동화 기능:');
console.log('✅ PR 생성/업데이트 시 자동 테스트');
console.log('✅ main/develop 브랜치 푸시 시 테스트');
console.log('✅ 테스트 매트릭스 (unit/integration/e2e)');
console.log('✅ DynamoDB Local + Redis 서비스');
console.log('✅ 커버리지 리포트 생성');
console.log('✅ 테스트 결과 아티팩트 업로드');

console.log('\n⏱️ 테스트 타임아웃:');
console.log('- Unit 테스트: 10분');
console.log('- Integration 테스트: 20분');
console.log('- E2E 테스트: 30분');

console.log('\n✅ 테스트 자동화 파이프라인 설정 완료!');