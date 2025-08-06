#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔒 Testing Security Test Suite...\n');

// 1. 파일 존재 확인
const securityTestFile = path.join(__dirname, '../backend/tests/security/security-test-suite.ts');
if (!fs.existsSync(securityTestFile)) {
  console.error('❌ Security test suite file not found');
  process.exit(1);
}

console.log('✅ Security test suite file exists');

// 2. TypeScript 컴파일 확인
try {
  execSync('cd backend && npx tsc --noEmit tests/security/security-test-suite.ts', { stdio: 'pipe' });
  console.log('✅ TypeScript compilation successful');
} catch (error) {
  console.error('❌ TypeScript compilation failed:', error.message);
  process.exit(1);
}

// 3. 보안 테스트 실행 (간단한 구문 검사)
try {
  const testContent = fs.readFileSync(securityTestFile, 'utf8');
  
  // 필수 테스트 케이스 확인
  const requiredTests = [
    'SQL injection',
    'XSS',
    'authentication bypass',
    'security headers'
  ];
  
  for (const test of requiredTests) {
    if (!testContent.toLowerCase().includes(test.toLowerCase())) {
      console.error(`❌ Missing test case: ${test}`);
      process.exit(1);
    }
  }
  
  console.log('✅ All required security test cases found');
  
} catch (error) {
  console.error('❌ Error reading security test file:', error.message);
  process.exit(1);
}

// 4. 보안 테스트 스크립트 추가
const packageJsonPath = path.join(__dirname, '../backend/package.json');
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

if (!packageJson.scripts['test:security']) {
  packageJson.scripts['test:security'] = 'jest tests/security --verbose';
  fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
  console.log('✅ Added test:security script to package.json');
}

console.log('\n🎉 Security Test Suite setup completed!');
console.log('\nNext steps:');
console.log('- Run: npm run test:security');
console.log('- Install security scanning tools (OWASP ZAP, etc.)');
console.log('- Set up automated security scans in CI/CD');