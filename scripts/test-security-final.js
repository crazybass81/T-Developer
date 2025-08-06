#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔒 Testing Security Test Automation...\n');

// 1. 파일 존재 확인
const files = [
  'backend/tests/security/security-test-suite.ts',
  'backend/tests/security/security-scanner.ts',
  'scripts/run-security-scan.js'
];

let allFilesExist = true;
for (const file of files) {
  const filePath = path.join(__dirname, '..', file);
  if (fs.existsSync(filePath)) {
    console.log(`✅ ${file} exists`);
  } else {
    console.log(`❌ ${file} missing`);
    allFilesExist = false;
  }
}

if (!allFilesExist) {
  console.log('\n❌ Some security test files are missing');
  process.exit(1);
}

// 2. 보안 테스트 내용 검증
const securityTestFile = path.join(__dirname, '../backend/tests/security/security-test-suite.ts');
const testContent = fs.readFileSync(securityTestFile, 'utf8');

const requiredTests = [
  'testSQLInjection',
  'testXSS', 
  'testAuthBypass',
  'testSecurityHeaders'
];

let allTestsFound = true;
for (const test of requiredTests) {
  if (testContent.includes(test)) {
    console.log(`✅ ${test} test found`);
  } else {
    console.log(`❌ ${test} test missing`);
    allTestsFound = false;
  }
}

// 3. 보안 스캐너 검증
const scannerFile = path.join(__dirname, '../backend/tests/security/security-scanner.ts');
const scannerContent = fs.readFileSync(scannerFile, 'utf8');

const scannerFeatures = [
  'scanForSecrets',
  'scanForVulnerablePatterns',
  'generateReport'
];

let allFeaturesFound = true;
for (const feature of scannerFeatures) {
  if (scannerContent.includes(feature)) {
    console.log(`✅ ${feature} feature found`);
  } else {
    console.log(`❌ ${feature} feature missing`);
    allFeaturesFound = false;
  }
}

// 4. package.json 스크립트 확인
const packageJsonPath = path.join(__dirname, '../backend/package.json');
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

if (packageJson.scripts && packageJson.scripts['test:security']) {
  console.log('✅ test:security script found in package.json');
} else {
  console.log('❌ test:security script missing in package.json');
  allTestsFound = false;
}

// 5. 최종 결과
if (allFilesExist && allTestsFound && allFeaturesFound) {
  console.log('\n🎉 Security Test Automation setup completed successfully!');
  console.log('\nFeatures implemented:');
  console.log('- SQL Injection testing');
  console.log('- XSS prevention testing');
  console.log('- Authentication bypass testing');
  console.log('- Security headers validation');
  console.log('- Automated vulnerability scanning');
  console.log('- Secret detection');
  console.log('- Security report generation');
  console.log('\nNext steps:');
  console.log('- Run: npm run test:security');
  console.log('- Run: node scripts/run-security-scan.js');
  console.log('- Integrate with CI/CD pipeline');
} else {
  console.log('\n❌ Security test automation setup incomplete');
  process.exit(1);
}