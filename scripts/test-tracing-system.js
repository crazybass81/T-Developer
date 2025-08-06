#!/usr/bin/env node

const fs = require('fs');

console.log('🔍 분산 추적 시스템 검증 중...\n');

// 검증할 파일들
const expectedFiles = [
  'backend/src/config/tracing.ts',
  'backend/src/monitoring/apm.ts'
];

let allPassed = true;

// 파일 존재 확인
console.log('1️⃣ 파일 존재 확인:');
expectedFiles.forEach(filePath => {
  const exists = fs.existsSync(filePath);
  console.log(`   ${exists ? '✅' : '❌'} ${filePath}`);
  if (!exists) allPassed = false;
});

// 추적 시스템 확인
console.log('\n2️⃣ OpenTelemetry 추적 시스템 확인:');
try {
  const tracingContent = fs.readFileSync('backend/src/config/tracing.ts', 'utf8');
  
  const requiredFeatures = [
    'NodeTracerProvider',
    'JaegerExporter',
    'BatchSpanProcessor',
    'HttpInstrumentation',
    'ExpressInstrumentation',
    'TracingHelper',
    'traceAgentExecution',
    'traceExternalCall',
    'traceDatabaseOperation',
    'tracingMiddleware'
  ];
  
  requiredFeatures.forEach(feature => {
    const hasFeature = tracingContent.includes(feature);
    console.log(`   ${hasFeature ? '✅' : '❌'} ${feature} 기능`);
    if (!hasFeature) allPassed = false;
  });
  
} catch (error) {
  console.log('   ❌ 추적 파일 읽기 실패');
  allPassed = false;
}

// APM 시스템 확인
console.log('\n3️⃣ APM 모니터링 시스템 확인:');
try {
  const apmContent = fs.readFileSync('backend/src/monitoring/apm.ts', 'utf8');
  
  const requiredElements = [
    'APMService',
    'PerformanceMetrics',
    'collectMetrics',
    'checkThresholds',
    'getHealthStatus',
    'cpu.usage',
    'memory.heapUsed',
    'eventLoop.delay'
  ];
  
  requiredElements.forEach(element => {
    const hasElement = apmContent.includes(element);
    console.log(`   ${hasElement ? '✅' : '❌'} ${element} 포함`);
    if (!hasElement) allPassed = false;
  });
  
} catch (error) {
  console.log('   ❌ APM 파일 읽기 실패');
  allPassed = false;
}

// 필요한 의존성 확인
console.log('\n4️⃣ 필요한 의존성 확인:');
const requiredDeps = [
  '@opentelemetry/api',
  '@opentelemetry/sdk-trace-node',
  '@opentelemetry/resources',
  '@opentelemetry/semantic-conventions',
  '@opentelemetry/exporter-jaeger',
  '@opentelemetry/sdk-trace-base',
  '@opentelemetry/instrumentation',
  '@opentelemetry/instrumentation-http',
  '@opentelemetry/instrumentation-express'
];

requiredDeps.forEach(dep => {
  console.log(`   📦 ${dep} (설치 필요)`);
});

// 최종 결과
console.log('\n' + '='.repeat(50));
if (allPassed) {
  console.log('✅ 모든 분산 추적 시스템 검증 통과!');
  console.log('\n🔍 다음 단계:');
  console.log('   1. OpenTelemetry 패키지 설치');
  console.log('   2. Jaeger 서버 설정 (Docker)');
  console.log('   3. Express 앱에 추적 미들웨어 통합');
  console.log('   4. APM 모니터링 시작');
  process.exit(0);
} else {
  console.log('❌ 일부 검증 실패. 위의 오류를 확인하세요.');
  process.exit(1);
}