#!/usr/bin/env node

const { SecurityScanner } = require('../backend/tests/security/security-scanner');
const path = require('path');
const fs = require('fs');

async function runSecurityScan() {
  console.log('🔒 Starting Security Scan...\n');
  
  const scanner = new SecurityScanner();
  const projectPath = path.join(__dirname, '..');
  
  try {
    const result = await scanner.scanProject(projectPath);
    const report = scanner.generateReport(result);
    
    console.log(report);
    
    // 보고서 파일 저장
    const reportPath = path.join(__dirname, '../security-report.txt');
    fs.writeFileSync(reportPath, report);
    console.log(`📄 Security report saved to: ${reportPath}`);
    
    // 심각한 취약점이 있으면 종료 코드 1
    if (result.vulnerabilities.high > 0) {
      console.log('\n❌ High severity vulnerabilities found!');
      process.exit(1);
    } else {
      console.log('\n✅ No high severity vulnerabilities found');
    }
    
  } catch (error) {
    console.error('❌ Security scan failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  runSecurityScan();
}