#!/usr/bin/env node
// scripts/check-frontend-ready.js

const fs = require('fs');
const path = require('path');

function checkFrontendReady() {
  console.log('🔍 프론트엔드 준비 상태 확인...');
  
  const checks = [
    {
      name: 'package.json 존재',
      check: () => fs.existsSync('frontend/package.json'),
      required: true
    },
    {
      name: 'vite.config.ts 존재',
      check: () => fs.existsSync('frontend/vite.config.ts'),
      required: true
    },
    {
      name: 'tsconfig.json 존재',
      check: () => fs.existsSync('frontend/tsconfig.json'),
      required: true
    },
    {
      name: 'node_modules 설치됨',
      check: () => fs.existsSync('frontend/node_modules'),
      required: false
    },
    {
      name: 'React 의존성 확인',
      check: () => {
        try {
          const pkg = JSON.parse(fs.readFileSync('frontend/package.json', 'utf8'));
          return pkg.dependencies && pkg.dependencies.react;
        } catch {
          return false;
        }
      },
      required: true
    }
  ];
  
  let passed = 0;
  let required = 0;
  
  checks.forEach(check => {
    const result = check.check();
    const status = result ? '✅' : '❌';
    console.log(`${status} ${check.name}`);
    
    if (result) passed++;
    if (check.required) required++;
  });
  
  console.log(`\n📊 결과: ${passed}/${checks.length} 통과`);
  
  if (passed >= required) {
    console.log('✅ 프론트엔드 준비 완료!');
    console.log('\n📋 다음 단계:');
    console.log('1. cd frontend && npm install (의존성 미설치시)');
    console.log('2. npm run dev (개발 서버 실행)');
    return true;
  } else {
    console.log('❌ 프론트엔드 설정 미완료');
    return false;
  }
}

if (require.main === module) {
  process.exit(checkFrontendReady() ? 0 : 1);
}

module.exports = { checkFrontendReady };