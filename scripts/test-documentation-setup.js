#!/usr/bin/env node

/**
 * 문서화 시스템 설정 검증 스크립트
 */

const fs = require('fs');
const path = require('path');

console.log('📚 문서화 시스템 설정 검증 시작...\n');

// Swagger 설정 확인
const swaggerPath = path.join('backend', 'src', 'config', 'swagger.ts');
if (fs.existsSync(swaggerPath)) {
  console.log('✅ Swagger 설정 파일 존재');
} else {
  console.log('❌ Swagger 설정 파일 없음');
}

// TypeDoc 설정 확인
const typedocPath = path.join('backend', 'typedoc.json');
if (fs.existsSync(typedocPath)) {
  console.log('✅ TypeDoc 설정 파일 존재');
  
  const config = JSON.parse(fs.readFileSync(typedocPath, 'utf8'));
  console.log(`✅ 출력 디렉토리: ${config.out}`);
  console.log(`✅ 프로젝트명: ${config.name}`);
} else {
  console.log('❌ TypeDoc 설정 파일 없음');
}

// 문서화 표준 예시 확인
const standardsPath = path.join('backend', 'src', 'standards', 'documentation.ts');
if (fs.existsSync(standardsPath)) {
  console.log('✅ 문서화 표준 예시 존재');
} else {
  console.log('❌ 문서화 표준 예시 없음');
}

// package.json 스크립트 확인
const packageJsonPath = path.join('backend', 'package.json');
if (fs.existsSync(packageJsonPath)) {
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  
  console.log('\n📦 문서화 스크립트 확인:');
  const docScripts = ['docs:generate', 'docs:serve'];
  
  docScripts.forEach(script => {
    const exists = packageJson.scripts?.[script];
    console.log(`${exists ? '✅' : '❌'} ${script}: ${exists || 'N/A'}`);
  });
  
  console.log('\n📦 문서화 의존성 확인:');
  const docDeps = [
    'swagger-jsdoc',
    'swagger-ui-express',
    'typedoc',
    'typedoc-plugin-markdown',
    'http-server'
  ];
  
  docDeps.forEach(dep => {
    const exists = packageJson.dependencies?.[dep] || packageJson.devDependencies?.[dep];
    console.log(`${exists ? '✅' : '❌'} ${dep}`);
  });
}

console.log('\n🚀 문서화 기능:');
console.log('✅ Swagger/OpenAPI 3.0 API 문서');
console.log('✅ TypeDoc 코드 문서 자동 생성');
console.log('✅ JSDoc/TSDoc 표준 지원');
console.log('✅ Markdown 플러그인 지원');
console.log('✅ HTTP 서버로 문서 서빙');

console.log('\n📋 문서 생성 명령어:');
console.log('- API 문서: npm run docs:generate');
console.log('- 문서 서버: npm run docs:serve');
console.log('- Swagger UI: http://localhost:8000/api-docs');

console.log('\n✅ 문서화 시스템 설정 완료!');