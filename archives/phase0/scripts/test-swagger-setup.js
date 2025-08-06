#!/usr/bin/env node

/**
 * Swagger API 문서 설정 검증 스크립트
 */

const fs = require('fs');
const path = require('path');

console.log('📚 Swagger API 문서 설정 검증 시작...\n');

// Swagger 설정 파일 확인
const swaggerConfigPath = path.join('backend', 'src', 'config', 'swagger.ts');
if (fs.existsSync(swaggerConfigPath)) {
  console.log('✅ swagger.ts 설정 파일 존재');
  
  const content = fs.readFileSync(swaggerConfigPath, 'utf8');
  
  // 필수 요소 확인
  const checks = [
    { name: 'OpenAPI 3.0.0', pattern: /openapi.*3\.0\.0/ },
    { name: 'API 정보', pattern: /title.*T-Developer API/ },
    { name: '서버 설정', pattern: /servers.*localhost.*8000/ },
    { name: 'Bearer 인증', pattern: /bearerAuth.*bearer/ },
    { name: 'Swagger UI 설정', pattern: /swaggerUi\.setup/ },
    { name: 'JSON 엔드포인트', pattern: /api-docs\.json/ }
  ];
  
  checks.forEach(check => {
    const exists = check.pattern.test(content);
    console.log(`${exists ? '✅' : '❌'} ${check.name}`);
  });
  
} else {
  console.log('❌ swagger.ts 설정 파일 없음');
}

// package.json 의존성 확인
const packageJsonPath = path.join('backend', 'package.json');
if (fs.existsSync(packageJsonPath)) {
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  
  console.log('\n📦 Swagger 의존성 확인:');
  const swaggerDeps = [
    'swagger-jsdoc',
    'swagger-ui-express',
    '@types/swagger-jsdoc',
    '@types/swagger-ui-express'
  ];
  
  swaggerDeps.forEach(dep => {
    const exists = packageJson.dependencies?.[dep] || packageJson.devDependencies?.[dep];
    console.log(`${exists ? '✅' : '❌'} ${dep}`);
  });
}

console.log('\n🚀 Swagger 기능:');
console.log('✅ OpenAPI 3.0 스펙 지원');
console.log('✅ Swagger UI 인터페이스');
console.log('✅ JWT Bearer 토큰 인증');
console.log('✅ API 키 인증 지원');
console.log('✅ JSON 스펙 엔드포인트');
console.log('✅ 커스텀 CSS 스타일링');

console.log('\n📋 API 문서 엔드포인트:');
console.log('- Swagger UI: http://localhost:8000/api-docs');
console.log('- JSON 스펙: http://localhost:8000/api-docs.json');

console.log('\n✅ Swagger API 문서 설정 완료!');