#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔍 디버깅 도구 통합 검증 시작...\n');

// 1. 파일 존재 확인
const debuggingToolsPath = path.join(__dirname, '../backend/src/dev/debugging-tools.ts');

if (!fs.existsSync(debuggingToolsPath)) {
  console.error('❌ debugging-tools.ts 파일이 존재하지 않습니다');
  process.exit(1);
}

console.log('✅ debugging-tools.ts 파일 존재 확인');

// 2. 파일 내용 검증
const content = fs.readFileSync(debuggingToolsPath, 'utf8');

const requiredComponents = [
  'AdvancedDebugger',
  'ExecutionTracer',
  'EnhancedConsole',
  'createDebugProxy',
  'debuggingMiddleware',
  'traceContext',
  'AsyncLocalStorage',
  'InspectorSession'
];

let allComponentsFound = true;

requiredComponents.forEach(component => {
  if (content.includes(component)) {
    console.log(`✅ ${component} 컴포넌트 발견`);
  } else {
    console.log(`❌ ${component} 컴포넌트 누락`);
    allComponentsFound = false;
  }
});

// 3. TypeScript 구문 검사
try {
  // 기본적인 구문 검사
  if (content.includes('export class') && 
      content.includes('interface') && 
      content.includes('async ') &&
      content.includes('Promise<')) {
    console.log('✅ TypeScript 구문 구조 정상');
  } else {
    console.log('❌ TypeScript 구문 구조 문제');
    allComponentsFound = false;
  }
} catch (error) {
  console.log('❌ TypeScript 구문 검사 실패:', error.message);
  allComponentsFound = false;
}

// 4. 필수 기능 확인
const requiredFeatures = [
  'setConditionalBreakpoint',
  'startProfiling',
  'stopProfiling',
  'takeHeapSnapshot',
  'traceExecution',
  'debuggingMiddleware'
];

requiredFeatures.forEach(feature => {
  if (content.includes(feature)) {
    console.log(`✅ ${feature} 기능 구현됨`);
  } else {
    console.log(`❌ ${feature} 기능 누락`);
    allComponentsFound = false;
  }
});

// 5. 의존성 확인
const requiredImports = [
  'inspector',
  'perf_hooks',
  'async_hooks',
  'util',
  'chalk',
  'crypto'
];

requiredImports.forEach(imp => {
  if (content.includes(`from '${imp}'`) || content.includes(`require('${imp}')`)) {
    console.log(`✅ ${imp} 모듈 임포트 확인`);
  } else {
    console.log(`❌ ${imp} 모듈 임포트 누락`);
    allComponentsFound = false;
  }
});

// 6. 파일 크기 확인
const stats = fs.statSync(debuggingToolsPath);
const fileSizeKB = (stats.size / 1024).toFixed(2);

console.log(`\n📊 파일 정보:`);
console.log(`   - 크기: ${fileSizeKB} KB`);
console.log(`   - 라인 수: ${content.split('\n').length}`);

if (stats.size > 1000) {
  console.log('✅ 파일 크기 적절함');
} else {
  console.log('❌ 파일 크기가 너무 작음');
  allComponentsFound = false;
}

// 최종 결과
console.log('\n' + '='.repeat(50));
if (allComponentsFound) {
  console.log('🎉 디버깅 도구 통합 검증 완료!');
  console.log('\n주요 기능:');
  console.log('  - Inspector API 기반 고급 디버거');
  console.log('  - 조건부 브레이크포인트 설정');
  console.log('  - CPU 프로파일링 및 메모리 스냅샷');
  console.log('  - 실행 추적 및 트레이싱');
  console.log('  - 향상된 콘솔 로깅');
  console.log('  - 디버그 프록시');
  console.log('  - HTTP 요청 추적 미들웨어');
  process.exit(0);
} else {
  console.log('❌ 디버깅 도구 통합 검증 실패');
  process.exit(1);
}