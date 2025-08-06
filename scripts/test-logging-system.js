#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('📊 구조화된 로깅 시스템 검증 중...\n');

// 검증할 파일들
const expectedFiles = [
  'backend/src/config/logger.ts',
  'backend/src/middleware/logging.ts'
];

let allPassed = true;

// 파일 존재 확인
console.log('1️⃣ 파일 존재 확인:');
expectedFiles.forEach(filePath => {
  const exists = fs.existsSync(filePath);
  console.log(`   ${exists ? '✅' : '❌'} ${filePath}`);
  if (!exists) allPassed = false;
});

// Logger 클래스 구조 확인
console.log('\n2️⃣ Logger 클래스 구조 확인:');
try {
  const loggerContent = fs.readFileSync('backend/src/config/logger.ts', 'utf8');
  
  const requiredMethods = ['fatal', 'error', 'warn', 'info', 'debug', 'trace'];
  requiredMethods.forEach(method => {
    const hasMethod = loggerContent.includes(`${method}(message: string`);
    console.log(`   ${hasMethod ? '✅' : '❌'} ${method} 메서드`);
    if (!hasMethod) allPassed = false;
  });
  
  const requiredFeatures = [
    'customLevels',
    'winston.format.timestamp',
    'winston.format.json',
    'DailyRotateFile',
    'startTimer',
    'logAgentExecution'
  ];
  
  requiredFeatures.forEach(feature => {
    const hasFeature = loggerContent.includes(feature);
    console.log(`   ${hasFeature ? '✅' : '❌'} ${feature} 기능`);
    if (!hasFeature) allPassed = false;
  });
  
} catch (error) {
  console.log('   ❌ Logger 파일 읽기 실패');
  allPassed = false;
}

// 로깅 미들웨어 확인
console.log('\n3️⃣ 로깅 미들웨어 확인:');
try {
  const middlewareContent = fs.readFileSync('backend/src/middleware/logging.ts', 'utf8');
  
  const requiredElements = [
    'loggingMiddleware',
    'createRequestLogger',
    'Request started',
    'Request completed',
    'req.id',
    'req.logger'
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

// logs 디렉토리 생성
console.log('\n4️⃣ 로그 디렉토리 설정:');
const logsDir = 'backend/logs';
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
  console.log(`   ✅ ${logsDir} 디렉토리 생성`);
} else {
  console.log(`   ✅ ${logsDir} 디렉토리 존재`);
}

// .gitignore 확인
const gitignoreContent = fs.readFileSync('.gitignore', 'utf8');
if (!gitignoreContent.includes('logs/')) {
  fs.appendFileSync('.gitignore', '\n# Logs\nlogs/\n*.log\n');
  console.log('   ✅ .gitignore에 로그 파일 제외 추가');
} else {
  console.log('   ✅ .gitignore에 로그 파일 제외 설정됨');
}

// 최종 결과
console.log('\n' + '='.repeat(50));
if (allPassed) {
  console.log('✅ 모든 구조화된 로깅 시스템 검증 통과!');
  console.log('\n📊 다음 단계:');
  console.log('   1. winston 패키지 설치: npm install winston winston-daily-rotate-file');
  console.log('   2. Express 앱에 로깅 미들웨어 통합');
  console.log('   3. 로그 레벨 환경 변수 설정 (LOG_LEVEL)');
  process.exit(0);
} else {
  console.log('❌ 일부 검증 실패. 위의 오류를 확인하세요.');
  process.exit(1);
}