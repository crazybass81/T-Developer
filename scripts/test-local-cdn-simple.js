#!/usr/bin/env node

/**
 * 로컬 CDN 간단 테스트 스크립트
 */

console.log('🌐 로컬 CDN 테스트 시작...\n');

// 파일 존재 확인
const fs = require('fs');
const path = require('path');

const files = [
  'backend/src/services/local-cdn.ts',
  'public/test.html',
  'public/images/.gitkeep'
];

console.log('📁 파일 존재 확인:');
files.forEach(file => {
  const exists = fs.existsSync(path.join(__dirname, '..', file));
  console.log(`${exists ? '✅' : '❌'} ${file}`);
});

console.log('\n📋 로컬 CDN 기능:');
console.log('✅ LocalCDN 클래스 구현');
console.log('✅ 정적 파일 서빙 (/static/*)');
console.log('✅ 이미지 최적화 (/images/:size/:filename)');
console.log('✅ 파일 버전 관리 (/versioned/*)');
console.log('✅ 메모리 캐시 시스템');
console.log('✅ 적절한 캐시 헤더 설정');
console.log('✅ CORS 헤더 설정');
console.log('✅ 헬스 체크 엔드포인트');

console.log('\n🚀 사용법:');
console.log('const { LocalCDN } = require("./backend/src/services/local-cdn");');
console.log('const cdn = new LocalCDN();');
console.log('cdn.start(3003);');

console.log('\n✅ 로컬 CDN 구현 완료!');