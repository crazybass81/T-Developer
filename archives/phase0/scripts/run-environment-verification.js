#!/usr/bin/env node

/**
 * 환경 검증 스크립트 실행기
 * SubTask 0.14.2 - 개발 환경 최종 검증
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 T-Developer 개발 환경 최종 검증 시작...\n');

// TypeScript 파일을 ts-node로 실행
const verifyScript = path.join(__dirname, 'verify-environment.ts');

const child = spawn('npx', ['ts-node', verifyScript], {
  stdio: 'inherit',
  env: {
    ...process.env,
    NODE_ENV: 'development',
    AWS_REGION: 'us-east-1',
    DYNAMODB_ENDPOINT: 'http://localhost:8000',
    REDIS_HOST: 'localhost',
    REDIS_PORT: '6379'
  }
});

child.on('close', (code) => {
  if (code === 0) {
    console.log('\n✅ 환경 검증이 성공적으로 완료되었습니다!');
  } else {
    console.log('\n❌ 환경 검증 중 문제가 발생했습니다.');
    console.log('위의 실패 항목들을 확인하고 수정해주세요.');
  }
  process.exit(code);
});

child.on('error', (error) => {
  console.error('❌ 환경 검증 스크립트 실행 실패:', error.message);
  process.exit(1);
});