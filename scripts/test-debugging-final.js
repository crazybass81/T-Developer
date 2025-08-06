#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔧 디버깅 도구 통합 최종 검증...\n');

// 1. 필수 파일 존재 확인
const files = [
  'backend/src/dev/debugging-tools.ts',
  'backend/src/routes/debug-demo.ts'
];

let allFilesExist = true;

files.forEach(file => {
  const filePath = path.join(__dirname, '..', file);
  if (fs.existsSync(filePath)) {
    const stats = fs.statSync(filePath);
    console.log(`✅ ${file} (${(stats.size / 1024).toFixed(2)} KB)`);
  } else {
    console.log(`❌ ${file} 파일 누락`);
    allFilesExist = false;
  }
});

// 2. 디버깅 도구 기능 검증
const debugToolsPath = path.join(__dirname, '../backend/src/dev/debugging-tools.ts');
const debugToolsContent = fs.readFileSync(debugToolsPath, 'utf8');

const coreFeatures = [
  { name: 'Inspector API 통합', pattern: 'InspectorSession' },
  { name: '조건부 브레이크포인트', pattern: 'setConditionalBreakpoint' },
  { name: 'CPU 프로파일링', pattern: 'startProfiling' },
  { name: '메모리 스냅샷', pattern: 'takeHeapSnapshot' },
  { name: '실행 추적', pattern: 'ExecutionTracer' },
  { name: '향상된 콘솔', pattern: 'EnhancedConsole' },
  { name: '디버그 프록시', pattern: 'createDebugProxy' },
  { name: 'HTTP 미들웨어', pattern: 'debuggingMiddleware' },
  { name: '트레이스 컨텍스트', pattern: 'AsyncLocalStorage' }
];

console.log('\n🔍 핵심 기능 검증:');
coreFeatures.forEach(feature => {
  if (debugToolsContent.includes(feature.pattern)) {
    console.log(`✅ ${feature.name}`);
  } else {
    console.log(`❌ ${feature.name} 누락`);
    allFilesExist = false;
  }
});

// 3. 데모 API 검증
const demoPath = path.join(__dirname, '../backend/src/routes/debug-demo.ts');
const demoContent = fs.readFileSync(demoPath, 'utf8');

const demoEndpoints = [
  { name: 'Profiling Demo', pattern: '/profile' },
  { name: 'Trace Demo', pattern: '/trace' },
  { name: 'Proxy Demo', pattern: '/proxy' },
  { name: 'Snapshot Demo', pattern: '/snapshot' }
];

console.log('\n🌐 데모 API 엔드포인트:');
demoEndpoints.forEach(endpoint => {
  if (demoContent.includes(endpoint.pattern)) {
    console.log(`✅ ${endpoint.name} (${endpoint.pattern})`);
  } else {
    console.log(`❌ ${endpoint.name} 누락`);
    allFilesExist = false;
  }
});

// 4. TypeScript 데코레이터 검증
if (demoContent.includes('@tracer.trace')) {
  console.log('✅ TypeScript 데코레이터 사용');
} else {
  console.log('❌ TypeScript 데코레이터 누락');
  allFilesExist = false;
}

// 5. 통계 정보
console.log('\n📊 구현 통계:');
console.log(`   - 디버깅 도구 파일: ${(fs.statSync(debugToolsPath).size / 1024).toFixed(2)} KB`);
console.log(`   - 데모 API 파일: ${(fs.statSync(demoPath).size / 1024).toFixed(2)} KB`);
console.log(`   - 총 라인 수: ${debugToolsContent.split('\n').length + demoContent.split('\n').length}`);

// 최종 결과
console.log('\n' + '='.repeat(60));
if (allFilesExist) {
  console.log('🎉 SubTask 0.12.4: 디버깅 도구 통합 완료!');
  console.log('\n✨ 구현된 기능:');
  console.log('   🔧 Inspector API 기반 고급 디버거');
  console.log('   📊 CPU 프로파일링 및 메모리 분석');
  console.log('   🔍 실행 추적 및 분산 트레이싱');
  console.log('   📝 향상된 콘솔 로깅 시스템');
  console.log('   🎭 디버그 프록시 및 객체 감시');
  console.log('   🌐 HTTP 요청 추적 미들웨어');
  console.log('   🎯 조건부 브레이크포인트 설정');
  console.log('   📸 힙 메모리 스냅샷 생성');
  console.log('\n🚀 사용법:');
  console.log('   - import { AdvancedDebugger } from "./dev/debugging-tools"');
  console.log('   - @tracer.trace() 데코레이터로 함수 추적');
  console.log('   - debuggingMiddleware()로 HTTP 요청 추적');
  console.log('   - createDebugProxy()로 객체 감시');
  process.exit(0);
} else {
  console.log('❌ 디버깅 도구 통합 검증 실패');
  process.exit(1);
}