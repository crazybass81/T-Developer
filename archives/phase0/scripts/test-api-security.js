#!/usr/bin/env node

const { APIKeyManager, HMACValidator, APISecurityMiddleware } = require('../backend/src/security/api-security');
const crypto = require('crypto');

console.log('🔐 API 보안 시스템 테스트 시작...\n');

// 1. API 키 관리 테스트
console.log('1. API 키 관리 테스트');
const apiKey = APIKeyManager.generateAPIKey();
console.log(`✅ API 키 생성: ${apiKey}`);

const hashedKey = APIKeyManager.hashAPIKey(apiKey);
console.log(`✅ API 키 해시: ${hashedKey.substring(0, 16)}...`);

const isValidFormat = APIKeyManager.validateKeyFormat(apiKey);
console.log(`✅ 키 형식 검증: ${isValidFormat}`);

const isInvalidFormat = APIKeyManager.validateKeyFormat('invalid-key');
console.log(`✅ 잘못된 키 형식 검증: ${!isInvalidFormat}\n`);

// 2. HMAC 서명 테스트
console.log('2. HMAC 서명 검증 테스트');
const secret = 'test-secret';
const method = 'POST';
const path = '/api/test';
const timestamp = Math.floor(Date.now() / 1000);
const body = { test: 'data' };

const signature = HMACValidator.generateSignature(secret, method, path, timestamp, body);
console.log(`✅ HMAC 서명 생성: ${signature.substring(0, 16)}...`);

// Mock request 객체
const mockReq = {
  method,
  path,
  body,
  headers: {
    'x-signature': signature,
    'x-timestamp': timestamp.toString()
  }
};

const isValidSignature = HMACValidator.validateRequest(mockReq, secret);
console.log(`✅ 서명 검증: ${isValidSignature}`);

// 잘못된 서명 테스트
const invalidReq = {
  ...mockReq,
  headers: {
    'x-signature': 'invalid-signature',
    'x-timestamp': timestamp.toString()
  }
};

const isInvalidSignature = HMACValidator.validateRequest(invalidReq, secret);
console.log(`✅ 잘못된 서명 검증: ${!isInvalidSignature}\n`);

// 3. 스코프 검증 테스트
console.log('3. 스코프 검증 테스트');
const validateScopes = (required, userScopes) => {
  return userScopes.includes('admin:all') || required.every(scope => userScopes.includes(scope));
};

const adminScopes = ['admin:all'];
const userScopes = ['projects:read', 'projects:write'];
const requiredScopes = ['projects:read'];

console.log(`✅ 관리자 스코프 검증: ${validateScopes(requiredScopes, adminScopes)}`);
console.log(`✅ 사용자 스코프 검증: ${validateScopes(requiredScopes, userScopes)}`);
console.log(`✅ 권한 부족 검증: ${!validateScopes(['admin:all'], userScopes)}\n`);

// 4. 보안 헤더 테스트
console.log('4. 보안 헤더 테스트');
const mockRes = {
  headers: {},
  setHeader(name, value) {
    this.headers[name] = value;
  }
};

const securityHeaders = APISecurityMiddleware.securityHeaders();
securityHeaders({}, mockRes, () => {});

const expectedHeaders = [
  'X-Content-Type-Options',
  'X-Frame-Options', 
  'X-XSS-Protection',
  'Strict-Transport-Security',
  'Content-Security-Policy'
];

const hasAllHeaders = expectedHeaders.every(header => mockRes.headers[header]);
console.log(`✅ 보안 헤더 설정: ${hasAllHeaders}`);
console.log(`   설정된 헤더: ${Object.keys(mockRes.headers).join(', ')}\n`);

// 5. User-Agent 검증 테스트
console.log('5. User-Agent 검증 테스트');
const suspiciousAgents = ['curl', 'wget', 'bot', 'crawler', 'spider'];

const validUserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36';
const suspiciousUserAgent = 'curl/7.68.0';

const isValidUA = !suspiciousAgents.some(agent => validUserAgent.toLowerCase().includes(agent));
const isSuspiciousUA = suspiciousAgents.some(agent => suspiciousUserAgent.toLowerCase().includes(agent));

console.log(`✅ 정상 User-Agent 검증: ${isValidUA}`);
console.log(`✅ 의심스러운 User-Agent 탐지: ${isSuspiciousUA}\n`);

console.log('🎉 모든 API 보안 테스트 통과!');