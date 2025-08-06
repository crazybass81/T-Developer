#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('📚 개발자 가이드 문서 구조 검증 중...\n');

// 검증할 문서 구조
const expectedStructure = [
  'docs/developer-guide/index.md',
  'scripts/generate-docs.ts'
];

let allPassed = true;

// 파일 존재 확인
console.log('1️⃣ 파일 존재 확인:');
expectedStructure.forEach(filePath => {
  const exists = fs.existsSync(filePath);
  console.log(`   ${exists ? '✅' : '❌'} ${filePath}`);
  if (!exists) allPassed = false;
});

// 개발자 가이드 인덱스 내용 확인
console.log('\n2️⃣ 개발자 가이드 내용 확인:');
try {
  const indexContent = fs.readFileSync('docs/developer-guide/index.md', 'utf8');
  
  const requiredSections = [
    '시작하기',
    '아키텍처 개요',
    '에이전트 개발',
    'API 레퍼런스',
    '통합 가이드',
    '베스트 프랙티스',
    '문제 해결'
  ];
  
  requiredSections.forEach(section => {
    const hasSection = indexContent.includes(section);
    console.log(`   ${hasSection ? '✅' : '❌'} ${section} 섹션`);
    if (!hasSection) allPassed = false;
  });
  
} catch (error) {
  console.log('   ❌ 개발자 가이드 인덱스 읽기 실패');
  allPassed = false;
}

// 문서 생성 스크립트 확인
console.log('\n3️⃣ 문서 생성 스크립트 확인:');
try {
  const scriptContent = fs.readFileSync('scripts/generate-docs.ts', 'utf8');
  
  const requiredFeatures = [
    'generateDocumentation',
    'generateDocsIndex',
    'TypeDoc',
    'metadata.json'
  ];
  
  requiredFeatures.forEach(feature => {
    const hasFeature = scriptContent.includes(feature);
    console.log(`   ${hasFeature ? '✅' : '❌'} ${feature} 기능`);
    if (!hasFeature) allPassed = false;
  });
  
} catch (error) {
  console.log('   ❌ 문서 생성 스크립트 읽기 실패');
  allPassed = false;
}

// 최종 결과
console.log('\n' + '='.repeat(50));
if (allPassed) {
  console.log('✅ 모든 개발자 가이드 문서 구조 검증 통과!');
  console.log('\n📖 다음 단계:');
  console.log('   1. 각 섹션별 상세 문서 작성');
  console.log('   2. API 문서 자동 생성 설정');
  console.log('   3. 문서 검색 기능 구현');
  process.exit(0);
} else {
  console.log('❌ 일부 검증 실패. 위의 오류를 확인하세요.');
  process.exit(1);
}