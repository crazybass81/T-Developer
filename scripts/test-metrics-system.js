#!/usr/bin/env node

const fs = require('fs');
const http = require('http');

console.log('📊 메트릭 수집 시스템 검증 중...\n');

// 검증할 파일들
const expectedFiles = [
  'backend/src/config/metrics.ts',
  'backend/src/middleware/metrics.ts'
];

let allPassed = true;

// 파일 존재 확인
console.log('1️⃣ 파일 존재 확인:');
expectedFiles.forEach(filePath => {
  const exists = fs.existsSync(filePath);
  console.log(`   ${exists ? '✅' : '❌'} ${filePath}`);
  if (!exists) allPassed = false;
});

// 메트릭 정의 확인
console.log('\n2️⃣ 메트릭 정의 확인:');
try {
  const metricsContent = fs.readFileSync('backend/src/config/metrics.ts', 'utf8');
  
  const requiredMetrics = [
    'httpRequestDuration',
    'httpRequestTotal',
    'agentExecutionDuration',
    'agentExecutionTotal',
    'agentTokenUsage',
    'projectCreationDuration',
    'activeProjects',
    'cacheHitRate',
    'queueSize',
    'componentUsage'
  ];
  
  requiredMetrics.forEach(metric => {
    const hasMetric = metricsContent.includes(metric);
    console.log(`   ${hasMetric ? '✅' : '❌'} ${metric} 메트릭`);
    if (!hasMetric) allPassed = false;
  });
  
  // Prometheus 설정 확인
  const prometheusFeatures = [
    'promClient.Registry',
    'promClient.Histogram',
    'promClient.Counter',
    'promClient.Gauge',
    'collectDefaultMetrics',
    'MetricsHelper'
  ];
  
  prometheusFeatures.forEach(feature => {
    const hasFeature = metricsContent.includes(feature);
    console.log(`   ${hasFeature ? '✅' : '❌'} ${feature} 기능`);
    if (!hasFeature) allPassed = false;
  });
  
} catch (error) {
  console.log('   ❌ 메트릭 파일 읽기 실패');
  allPassed = false;
}

// 미들웨어 확인
console.log('\n3️⃣ 메트릭 미들웨어 확인:');
try {
  const middlewareContent = fs.readFileSync('backend/src/middleware/metrics.ts', 'utf8');
  
  const requiredElements = [
    'collectMetrics',
    'trackAgentExecution',
    'trackProjectCreation',
    'httpRequestDuration.observe',
    'httpRequestTotal.inc',
    'MetricsHelper.recordAgentExecution'
  ];
  
  requiredElements.forEach(element => {
    const hasElement = middlewareContent.includes(element);
    console.log(`   ${hasElement ? '✅' : '❌'} ${element} 포함`);
    if (!hasElement) allPassed = false;
  });
  
} catch (error) {
  console.log('   ❌ 미들웨어 파일 읽기 실패');
  allPassed = false;
}

// package.json 의존성 확인
console.log('\n4️⃣ 의존성 확인:');
try {
  const packageJson = JSON.parse(fs.readFileSync('backend/package.json', 'utf8'));
  const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
  
  const requiredDeps = ['prom-client'];
  
  requiredDeps.forEach(dep => {
    const hasDep = dependencies[dep];
    console.log(`   ${hasDep ? '✅' : '❌'} ${dep} ${hasDep ? `(${dependencies[dep]})` : '누락'}`);
    if (!hasDep) allPassed = false;
  });
  
} catch (error) {
  console.log('   ❌ package.json 읽기 실패');
  allPassed = false;
}

// 최종 결과
console.log('\n' + '='.repeat(50));
if (allPassed) {
  console.log('✅ 모든 메트릭 수집 시스템 검증 통과!');
  console.log('\n📊 다음 단계:');
  console.log('   1. prom-client 패키지 설치: npm install prom-client');
  console.log('   2. Express 앱에 메트릭 미들웨어 통합');
  console.log('   3. /metrics 엔드포인트 추가');
  console.log('   4. Prometheus 서버 설정');
  process.exit(0);
} else {
  console.log('❌ 일부 검증 실패. 위의 오류를 확인하세요.');
  process.exit(1);
}