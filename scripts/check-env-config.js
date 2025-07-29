#!/usr/bin/env node
// scripts/check-env-config.js

require('dotenv').config();

console.log('🔍 환경 변수 설정 확인...\n');

const checks = [
  { key: 'NODE_ENV', required: true },
  { key: 'PORT', required: true },
  { key: 'AWS_ACCESS_KEY_ID', required: true, sensitive: true },
  { key: 'AWS_SECRET_ACCESS_KEY', required: true, sensitive: true },
  { key: 'OPENAI_API_KEY', required: false, sensitive: true },
  { key: 'ANTHROPIC_API_KEY', required: false, sensitive: true },
  { key: 'DYNAMODB_ENDPOINT', required: true },
  { key: 'S3_ARTIFACTS_BUCKET', required: true },
  { key: 'JWT_SECRET', required: true, sensitive: true }
];

let passed = 0;
let total = checks.length;

checks.forEach(check => {
  const value = process.env[check.key];
  const exists = !!value;
  const status = exists ? '✅' : (check.required ? '❌' : '⚠️');
  
  let displayValue = '';
  if (exists) {
    if (check.sensitive) {
      displayValue = `${value.substring(0, 8)}...`;
    } else {
      displayValue = value;
    }
  } else {
    displayValue = 'Not set';
  }
  
  console.log(`${status} ${check.key}: ${displayValue}`);
  
  if (exists) passed++;
});

console.log(`\n📊 결과: ${passed}/${total} 설정됨`);

if (passed >= checks.filter(c => c.required).length) {
  console.log('✅ 필수 환경 변수 설정 완료!');
} else {
  console.log('❌ 필수 환경 변수 누락');
}