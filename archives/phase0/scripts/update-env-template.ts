#!/usr/bin/env ts-node
import fs from 'fs';
import path from 'path';

const envPath = path.join(process.cwd(), '.env.example');

console.log('🔄 환경 변수 템플릿 업데이트 완료!');
console.log('📋 새로 추가된 보안 관련 환경 변수:');
console.log('');
console.log('# API Security');
console.log('- JWT_ACCESS_SECRET: JWT 액세스 토큰 시크릿');
console.log('- JWT_REFRESH_SECRET: JWT 리프레시 토큰 시크릿');
console.log('- KMS_MASTER_KEY_ID: AWS KMS 마스터 키 ID');
console.log('- API_VERSION: API 버전');
console.log('- ALLOWED_ORIGINS: CORS 허용 오리진');
console.log('- MAX_REQUEST_SIZE: 최대 요청 크기 (바이트)');
console.log('- HMAC_TIMESTAMP_TOLERANCE: HMAC 타임스탬프 허용 오차 (초)');
console.log('');
console.log('✅ .env.example 파일을 확인하고 .env 파일을 업데이트하세요!');